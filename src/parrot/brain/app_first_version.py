"""Backend facade for the first App shell and menu-canvas white model.

This module intentionally exposes a small business surface over existing core
modules. Unity and the temporary Web smoke monitor can ask one place for App
module status instead of poking Blackboard, IntentWorkspace, or DSG directly.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from parrot.brain.photo_awareness import (
    PhotoAwarenessPolicy,
    apply_photo_awareness_settings,
    latest_photo_awareness_notice,
)
from parrot.brain.intent_workspace import (
    PayloadSource,
    StagedRefKind,
    StagedRefMetadata,
    StagedRefRequest,
    get_intent_workspace,
)
from parrot.brain.obsidian_vault import check_obsidian_vault
from parrot.brain.preset_loader import DEFAULT_WORKSPACE_ID
from parrot.brain.workspace_registry import WorkspaceApplyResult, get_workspace_registry
from parrot.scheduler.blackboard import open_bb_client


class ExternalModuleId(str, Enum):
    GOOGLE_CALENDAR = "google_calendar"
    OBSIDIAN = "obsidian"
    GOSLO_MODULE = "goslo_module"
    NANOBOT = "nanobot"
    PHOTO_CAMERA = "photo_camera"
    XR_HAND = "xr_hand"
    CANVAS_CONNECTION = "canvas_connection"


class CameraMode(str, Enum):
    OFF = "off"
    PREVIEW = "preview"
    PHOTO_READY = "photo_ready"
    CAPTURE_LOCKED = "capture_locked"


class XrHandMode(str, Enum):
    OFF = "off"
    TRACKING = "tracking"
    GESTURE_SELECT = "gesture_select"


class AppToolId(str, Enum):
    SETTINGS = "settings"
    CAMERA = "camera"
    WORKSPACE = "workspace"
    MAGNIFIER_FOCUS = "magnifier_focus"
    BOUNDARY_BOX = "boundary_box"
    NOTE_INBOX = "note_inbox"


@dataclass(frozen=True)
class AppModuleStatus:
    """Read-only status card for a first-version App module."""

    module_id: ExternalModuleId
    state: str
    health: str = "ok"
    summary: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)
    refs: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id.value,
            "state": self.state,
            "health": self.health,
            "summary": self.summary,
            "metrics": dict(self.metrics),
            "refs": dict(self.refs),
        }


@dataclass(frozen=True)
class AppActionResult:
    """Outcome for a backend-owned App action."""

    action: str
    success: bool
    message: str = ""
    intent_workspace_ref_id: str = ""
    applied_keys: tuple[str, ...] = ()

    def as_json(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "success": self.success,
            "message": self.message,
            "intent_workspace_ref_id": self.intent_workspace_ref_id,
            "applied_keys": list(self.applied_keys),
        }


@dataclass(frozen=True)
class AppToolCard:
    """Read model for one tool-cabinet item in the App shell."""

    tool_id: AppToolId
    label: str
    state: str
    enabled: bool
    summary: str
    flow: tuple[str, ...] = ()
    action_endpoints: tuple[str, ...] = ()
    asset_slot: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)
    refs: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return {
            "tool_id": self.tool_id.value,
            "label": self.label,
            "state": self.state,
            "enabled": self.enabled,
            "summary": self.summary,
            "flow": list(self.flow),
            "action_endpoints": list(self.action_endpoints),
            "asset_slot": self.asset_slot,
            "metrics": dict(self.metrics),
            "refs": dict(self.refs),
        }


@dataclass(frozen=True)
class AppCanvasSnapshot:
    """Read-only payload for Unity menu canvas and the Web smoke monitor."""

    generated_at: float
    active_workspace_id: str
    module_statuses: tuple[AppModuleStatus, ...]
    workspaces: tuple[dict[str, Any], ...]
    paper_notes: tuple[dict[str, Any], ...]
    photo_refs: tuple[dict[str, Any], ...]
    tool_cabinet: tuple[dict[str, Any], ...] = ()
    asset_manifest: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "active_workspace_id": self.active_workspace_id,
            "module_statuses": [status.as_json() for status in self.module_statuses],
            "workspaces": list(self.workspaces),
            "paper_notes": list(self.paper_notes),
            "photo_refs": list(self.photo_refs),
            "tool_cabinet": list(self.tool_cabinet),
            "asset_manifest": dict(self.asset_manifest),
        }


class AppFirstVersionFacade:
    """Business facade for menu canvas, App shell, and smoke monitoring."""

    def __init__(self, obsidian_vault_path: Path | str | None = None) -> None:
        self._obsidian_vault_path = (
            Path(obsidian_vault_path)
            if obsidian_vault_path is not None
            else _default_obsidian_vault_path()
        )

    @property
    def intent_workspace(self):
        """Expose the current workspace for tests and smoke views."""
        return get_intent_workspace()

    def list_module_statuses(self) -> tuple[AppModuleStatus, ...]:
        """Return every App v1 external module status card."""
        return tuple(self.module_status(module_id) for module_id in ExternalModuleId)

    def canvas_snapshot(self) -> AppCanvasSnapshot:
        """Return one complete read model for App v1 shell verification."""
        active_workspace_id = _bb_str("global/active_workspace_id", DEFAULT_WORKSPACE_ID)
        workspaces = tuple(w.as_json() for w in get_workspace_registry().list_workspaces())
        return AppCanvasSnapshot(
            generated_at=time.time(),
            active_workspace_id=active_workspace_id,
            module_statuses=self.list_module_statuses(),
            workspaces=workspaces,
            paper_notes=tuple(self.list_paper_notes()),
            photo_refs=tuple(self.list_photo_refs()),
            tool_cabinet=tuple(tool.as_json() for tool in self.list_tool_cabinet()),
            asset_manifest=self.asset_manifest(),
        )

    def apply_workspace(self, workspace_id: str) -> AppActionResult:
        """Switch the visible 2DWorkspace without touching LiveKit lifecycle."""
        result: WorkspaceApplyResult = get_workspace_registry().apply_workspace(workspace_id)
        return AppActionResult(
            action="apply_workspace",
            success=result.success,
            message=result.active_workspace_id,
            applied_keys=result.applied_keys,
        )

    def module_status(self, module_id: ExternalModuleId | str) -> AppModuleStatus:
        """Read one module status without mutating runtime state."""
        mid = ExternalModuleId(module_id)
        if mid == ExternalModuleId.GOOGLE_CALENDAR:
            return self._google_status()
        if mid == ExternalModuleId.OBSIDIAN:
            return self._obsidian_status()
        if mid == ExternalModuleId.GOSLO_MODULE:
            return self._goslo_status()
        if mid == ExternalModuleId.NANOBOT:
            return self._nanobot_status()
        if mid == ExternalModuleId.PHOTO_CAMERA:
            return self._photo_camera_status()
        if mid == ExternalModuleId.XR_HAND:
            return self._xrhand_status()
        return self._canvas_status()

    def set_camera_mode(self, mode: CameraMode | str) -> AppActionResult:
        """Apply camera-mode state through a backend-owned BB key."""
        selected = CameraMode(mode)
        bb = open_bb_client(name="app_facade.camera", writer="brain.app_first_version")
        bb.set("session/camera_mode", selected.value)
        return AppActionResult(
            action="set_camera_mode",
            success=True,
            message=f"camera_mode={selected.value}",
            applied_keys=("session/camera_mode",),
        )

    def request_camera_capture(
        self,
        *,
        candidate_subject_uuid: str = "",
        awareness_policy: PhotoAwarenessPolicy | str | None = None,
    ) -> AppActionResult:
        """Record an explicit App camera capture request for Unity/Web smoke flows.

        Unity still owns pixels through ``PhotoController``. This request only
        exposes the UI intent to the backend and smoke console, so tests can
        verify camera mode, Awareness policy, and request metadata without
        pretending Python can capture a device frame.
        """
        if awareness_policy is not None:
            self.set_photo_awareness(awareness_policy, enabled=True)
        request_id = f"cap_{uuid.uuid4().hex[:8]}"
        payload = {
            "request_id": request_id,
            "candidate_subject_uuid": candidate_subject_uuid or "",
            "created_at": time.time(),
            "status": "requested",
            "unity_owner": "ParrotApp.Photo.PhotoController",
        }
        bb = open_bb_client(name="app_facade.camera_capture", writer="brain.app_first_version")
        bb.set("session/camera_mode", CameraMode.CAPTURE_LOCKED.value)
        bb.set("session/photo_capture_request", payload)
        return AppActionResult(
            action="request_camera_capture",
            success=True,
            message=request_id,
            applied_keys=("session/camera_mode", "session/photo_capture_request"),
        )

    def set_photo_awareness(
        self,
        policy: PhotoAwarenessPolicy | str,
        *,
        enabled: bool = True,
        preview_ttl_seconds: int = 15 * 60,
    ) -> AppActionResult:
        """Apply Photo Awareness v1 without allowing interrupt by default."""
        selected = PhotoAwarenessPolicy(policy)
        applied = apply_photo_awareness_settings(
            selected,
            enabled=enabled,
            preview_ttl_seconds=preview_ttl_seconds,
        )
        return AppActionResult(
            action="set_photo_awareness",
            success=True,
            message=f"photo_awareness={selected.value}",
            applied_keys=applied,
        )

    def set_xrhand_mode(self, mode: XrHandMode | str) -> AppActionResult:
        """Apply XRHand UI mode without changing Scene or LiveKit lifecycle."""
        selected = XrHandMode(mode)
        bb = open_bb_client(name="app_facade.xrhand", writer="brain.app_first_version")
        bb.set("session/xrhand_mode", selected.value)
        return AppActionResult(
            action="set_xrhand_mode",
            success=True,
            message=f"xrhand_mode={selected.value}",
            applied_keys=("session/xrhand_mode",),
        )

    def list_tool_cabinet(self) -> tuple[AppToolCard, ...]:
        """Return the App v1 tool-cabinet white model.

        The cabinet is a Unity/Web read model. Action endpoints name the only
        backend routes that may mutate state; page refreshes and normal canvas
        reads stay side-effect free.
        """
        from parrot.brain import refs as refs_registry

        refs_metrics = refs_registry.metrics_snapshot()
        camera_mode = _bb_str("session/camera_mode", CameraMode.OFF.value)
        capture_request = _bb_value("session/photo_capture_request", {})
        notes = self.list_paper_notes()
        photo_refs = self.list_photo_refs()
        return (
            AppToolCard(
                tool_id=AppToolId.SETTINGS,
                label="Settings",
                state="ready",
                enabled=True,
                summary="Local App shell settings and mode switches.",
                flow=("open_settings", "adjust_local_ui", "close_settings"),
                action_endpoints=("/api/app/awareness", "/api/app/camera/mode"),
                asset_slot="settings_icon_placeholder",
            ),
            AppToolCard(
                tool_id=AppToolId.CAMERA,
                label="Camera",
                state=camera_mode,
                enabled=True,
                summary="Toolbar camera flow: off -> preview -> photo_ready -> capture request.",
                flow=(
                    "tap_camera_tool",
                    "set preview/photo_ready",
                    "PhotoController captures preview EcpEvent",
                    "HTTP asset upload stays Unity-owned",
                    "Awareness stages short-lived photo ref",
                ),
                action_endpoints=(
                    "/api/app/camera/mode",
                    "/api/app/camera/capture-request",
                    "/api/app/test/photo-preview",
                ),
                asset_slot="camera_modern_or_placeholder",
                metrics={"photo_ref_count": len(photo_refs)},
                refs={"last_capture_request": capture_request if isinstance(capture_request, dict) else {}},
            ),
            AppToolCard(
                tool_id=AppToolId.WORKSPACE,
                label="2D Workdesk",
                state=_bb_str("global/active_workspace_id", DEFAULT_WORKSPACE_ID),
                enabled=True,
                summary="Paper desk overlay for reports, calendar drafts, photo refs, and local decisions.",
                flow=("open_workdesk", "inspect_document", "accept_dismiss_or_archive", "close_workdesk"),
                action_endpoints=("/api/app/workspace/apply",),
                asset_slot="workspace_modern_interiors_room",
                metrics={"paper_note_count": len(notes)},
            ),
            AppToolCard(
                tool_id=AppToolId.MAGNIFIER_FOCUS,
                label="Magnifier",
                state="active" if refs_metrics.get("focus_refs", 0) else "ready",
                enabled=True,
                summary="Visual focus helper; Unity emits focus.anchored/focus.released EcpEvents.",
                flow=("drag_magnifier", "focus.anchored", "RefBinding focus", "threshold may react"),
                action_endpoints=("/api/app/test/focus",),
                asset_slot="magnifier_or_telescope_placeholder",
                metrics={"focus_refs": refs_metrics.get("focus_refs", 0)},
            ),
            AppToolCard(
                tool_id=AppToolId.BOUNDARY_BOX,
                label="Boundary Box",
                state="active" if refs_metrics.get("bbox_refs", 0) else "ready",
                enabled=True,
                summary="Explicit attention box; Unity emits bbox.placed/bbox.removed EcpEvents.",
                flow=("drag_box", "bbox.placed", "RefBinding bbox", "threshold may react"),
                action_endpoints=("/api/app/test/bbox",),
                asset_slot="pixel_boundary_box_placeholder",
                metrics={"bbox_refs": refs_metrics.get("bbox_refs", 0)},
            ),
            AppToolCard(
                tool_id=AppToolId.NOTE_INBOX,
                label="Nanobot Notes",
                state="result_ready" if notes else "idle",
                enabled=True,
                summary="Nanobot and calendar results arrive as selectable, draggable paper notes for the 2D workdesk.",
                flow=("nanobot_result", "paper_note_spawn", "select_drag_scale", "trash_or_workdesk", "local_archive"),
                action_endpoints=("/api/app/nanobot/report", "/api/app/calendar/draft"),
                asset_slot="paper_note_newspaper",
                metrics={"paper_note_count": len(notes)},
                refs={"note_ref_ids": [n["ref_id"] for n in notes]},
            ),
        )

    def asset_manifest(self) -> dict[str, Any]:
        """Return App v1 asset slots and current source paths.

        The manifest deliberately tracks both the curated source and the Unity
        slot. Missing Unity imports are allowed in v1 as long as a placeholder
        is explicit and testable.
        """
        root = (
            "codex_workspace/design_workspace/asset_pipeline/"
            "pixel_asset_workspace/curated"
        )
        return {
            "schema_version": 1,
            "source_root": root,
            "unity_root": "unity/ArSpike/Assets/UI/ParrotApp",
            "slots": [
                {
                    "slot": "ToolDrawerWood",
                    "status": "selected",
                    "source": f"{root}/02_ui_supplements_book_paper_wood/wood_ui/Wood UI/WOOD/Menu1.png",
                    "unity": "Assets/UI/ParrotApp/ToolCabinet/ToolDrawer_Wood_Menu1.png",
                    "fallback": "solid wood-toned Image generated by AppV1MetaUiController",
                },
                {
                    "slot": "ToolButtonWood",
                    "status": "selected",
                    "source": f"{root}/02_ui_supplements_book_paper_wood/wood_ui/Wood UI/Buttons & Bars/Button/Front.png",
                    "unity": "Assets/UI/ParrotApp/ToolCabinet/ToolButton_Wood_Front.png",
                    "fallback": "Unity UI Button color block",
                },
                {
                    "slot": "PaperNoteSmall",
                    "status": "selected",
                    "source": f"{root}/02_ui_supplements_book_paper_wood/paper_ui/BlankNewspaper_New.png",
                    "unity": "Assets/UI/ParrotApp/Notifications/PaperNote_Blank_New.png",
                    "fallback": "paper-colored rounded rect",
                },
                {
                    "slot": "PaperNoteFilled",
                    "status": "selected",
                    "source": f"{root}/02_ui_supplements_book_paper_wood/paper_ui/FilledNewspaper_Old.png",
                    "unity": "Assets/UI/ParrotApp/Notifications/PaperNote_Filled_Old.png",
                    "fallback": "paper-colored rounded rect with status text",
                },
                {
                    "slot": "NanobotReportPaper",
                    "status": "runtime_placeholder",
                    "source": f"{root}/02_ui_supplements_book_paper_wood/paper_ui/BlankNewspaper_New.png",
                    "unity": "",
                    "fallback": "PaperNoteSmall warm tint selected by AppV1MetaUiController",
                },
                {
                    "slot": "CalendarReminderPaper",
                    "status": "runtime_placeholder",
                    "source": f"{root}/02_ui_supplements_book_paper_wood/paper_ui/FilledNewspaper_Old.png",
                    "unity": "",
                    "fallback": "PaperNoteFilled pale-blue tint selected by AppV1MetaUiController",
                },
                {
                    "slot": "TrashCrumpledPaper",
                    "status": "runtime_placeholder",
                    "source": "",
                    "unity": "",
                    "fallback": "three layered UGUI paper chips named TrashCrumpledPaperPlaceholder_*",
                },
                {
                    "slot": "OrangeCatPaw",
                    "status": "selected",
                    "source": "D:/GOSLOParrot/Pixel Asset/NekoClaw.png",
                    "unity": "Assets/UI/ParrotApp/Notifications/NekoClaw_Cutout.png",
                    "fallback": "paper slide-in is the App V1 fallback if the sprite is missing",
                },
                {
                    "slot": "ParrotJoystick",
                    "status": "runtime_placeholder",
                    "source": "",
                    "unity": "",
                    "fallback": "UGUI ParrotJoystick_PlaneWalkPad and knob",
                },
                {
                    "slot": "CameraIcon",
                    "status": "placeholder",
                    "source": f"{root}/06_icons_and_misc/pixelwood_valley_icon_pack/Pixelwood Valley Icon Pack 1.0/1.0/Items 16x16.png",
                    "unity": "Assets/UI/ParrotApp/Icons/Items_16x16.png",
                    "fallback": "text label CAM until modern camera sprite is cropped",
                },
                {
                    "slot": "FocusMagnifierIcon",
                    "status": "placeholder",
                    "source": f"{root}/03_secondary_ui_adventure/AdventureUI/Icons/Icons.png",
                    "unity": "Assets/UI/ParrotApp/Icons/Adventure_Icons.png",
                    "fallback": "text label FOCUS until magnifier sprite is cropped",
                },
                {
                    "slot": "BoundaryBoxIcon",
                    "status": "placeholder",
                    "source": f"{root}/02_ui_supplements_book_paper_wood/book_ui_v1/Sprites/Content/Boxes/Light/1.png",
                    "unity": "Assets/UI/ParrotApp/Icons/BoundaryBox_Frame.png",
                    "fallback": "white outline RectTransform",
                },
                {
                    "slot": "WorkspaceDesk",
                    "status": "selected",
                    "source": f"{root}/04_2d_workspace_modern_interiors",
                    "unity": "Assets/UI/ParrotApp/Workspace",
                    "fallback": "dimmed AR backdrop plus paper desk panel",
                },
                {
                    "slot": "TransitionAnimation",
                    "status": "slot_only",
                    "source": "",
                    "unity": "Assets/UI/ParrotApp/Transitions",
                    "fallback": "no-op fade slot in AppV1MetaUiController",
                },
            ],
        }

    async def create_calendar_draft(
        self,
        *,
        action: str,
        title: str,
        time_range: str = "",
        payload: dict[str, Any] | None = None,
    ) -> AppActionResult:
        """Stage a Google Calendar write action as an IntentWorkspace draft."""
        draft = {
            "action": action,
            "title": title,
            "time_range": time_range,
            "payload": dict(payload or {}),
        }
        handle = await self.intent_workspace.stage(StagedRefRequest(
            kind=StagedRefKind.DOC,
            payload_source=PayloadSource.INLINE_TEXT,
            payload_value=json.dumps(draft, ensure_ascii=False),
            metadata=StagedRefMetadata(
                origin="app:first_version:google_calendar",
                kind=StagedRefKind.DOC,
                payload_source=PayloadSource.INLINE_TEXT,
                custom_meta={
                    "role": "calendar_draft",
                    "action": action,
                    "title": title,
                    "ui_kind": "paper_note",
                    "workspace_id": "workdesk",
                },
            ),
        ))
        return AppActionResult(
            action="create_calendar_draft",
            success=True,
            intent_workspace_ref_id=handle.ref_id,
        )

    async def stage_nanobot_report(
        self,
        *,
        task_id: str,
        title: str,
        body: str,
    ) -> AppActionResult:
        """Stage a Nanobot result as a report note for the 2D report desk."""
        report = {"task_id": task_id, "title": title, "body": body}
        handle = await self.intent_workspace.stage(StagedRefRequest(
            kind=StagedRefKind.RICH_REPORT,
            payload_source=PayloadSource.INLINE_TEXT,
            payload_value=json.dumps(report, ensure_ascii=False),
            metadata=StagedRefMetadata(
                origin=f"app:first_version:nanobot:{task_id}",
                kind=StagedRefKind.RICH_REPORT,
                payload_source=PayloadSource.INLINE_TEXT,
                custom_meta={
                    "role": "nanobot_report",
                    "task_id": task_id,
                    "title": title,
                    "ui_kind": "paper_note",
                    "workspace_id": "report_desk",
                },
            ),
        ))
        return AppActionResult(
            action="stage_nanobot_report",
            success=True,
            intent_workspace_ref_id=handle.ref_id,
        )

    def _google_status(self) -> AppModuleStatus:
        drafts = self.intent_workspace.list_active(role="calendar_draft")
        return AppModuleStatus(
            module_id=ExternalModuleId.GOOGLE_CALENDAR,
            state="ready_for_draft" if drafts else "ready_readonly",
            summary="Google Calendar read path plus draft-gated write actions.",
            metrics={"pending_draft_count": len(drafts)},
            refs={"draft_ref_ids": [d.ref_id for d in drafts]},
        )

    def _obsidian_status(self) -> AppModuleStatus:
        result = check_obsidian_vault(self._obsidian_vault_path)
        health = "ok" if result.status == "ingest_ready" else "warn"
        return AppModuleStatus(
            module_id=ExternalModuleId.OBSIDIAN,
            state=result.status,
            health=health,
            summary=result.recommendation,
            metrics={
                "markdown_count": result.markdown_count,
                "ingest_ready_count": result.ingest_ready_count,
                "invalid_count": result.invalid_count,
                "profile_counts": result.profile_counts,
            },
            refs={
                "vault_path": result.vault_path,
                "ready_notes": result.sample_ready_notes,
                "invalid_notes": result.sample_invalid_notes,
            },
        )

    def _goslo_status(self) -> AppModuleStatus:
        return AppModuleStatus(
            module_id=ExternalModuleId.GOSLO_MODULE,
            state=_bb_str("session/app_capability_mode", "FullARCompanion"),
            summary="GOSLO session policy and awareness controls.",
            metrics={
                "photo_awareness_enabled": _bb_value("session/photo_awareness_enabled", False),
                "photo_awareness_policy": _bb_str(
                    "session/photo_awareness_policy",
                    PhotoAwarenessPolicy.UNAWARE_RECORDED.value,
                ),
                "photo_awareness_preview_ttl_seconds": _bb_value(
                    "session/photo_awareness_preview_ttl_seconds",
                    15 * 60,
                ),
                "allows_interrupt": _bb_value(
                    "session/photo_awareness_allows_interrupt",
                    False,
                ),
            },
        )

    def _nanobot_status(self) -> AppModuleStatus:
        reports = self.intent_workspace.list_active(role="nanobot_report")
        busy = bool(_bb_value("nanobot/busy", False))
        return AppModuleStatus(
            module_id=ExternalModuleId.NANOBOT,
            state="busy" if busy else ("result_ready" if reports else "idle"),
            summary="Background task and report note bridge.",
            metrics={
                "busy": busy,
                "report_count": len(reports),
                "last_active_at": _bb_value("nanobot/last_active_at", 0.0),
            },
            refs={"report_ref_ids": [r.ref_id for r in reports]},
        )

    def _photo_camera_status(self) -> AppModuleStatus:
        photo_refs = self.intent_workspace.list_active(kinds=frozenset({StagedRefKind.PHOTO}))
        return AppModuleStatus(
            module_id=ExternalModuleId.PHOTO_CAMERA,
            state=_bb_str("session/camera_mode", CameraMode.OFF.value),
            summary="Camera mode, photo upload, and awareness status.",
            metrics={
                "photo_ref_count": len(photo_refs),
                "photo_awareness_preview_count": len(
                    self.intent_workspace.list_active(role="photo_preview_awareness")
                ),
                "awareness_enabled": _bb_value("session/photo_awareness_enabled", False),
                "awareness_policy": _bb_str(
                    "session/photo_awareness_policy",
                    PhotoAwarenessPolicy.UNAWARE_RECORDED.value,
                ),
            },
            refs={
                "photo_ref_ids": [r.ref_id for r in photo_refs],
                "awareness_notice": latest_photo_awareness_notice(),
            },
        )

    def _xrhand_status(self) -> AppModuleStatus:
        state = _bb_str("session/xrhand_mode", XrHandMode.OFF.value)
        return AppModuleStatus(
            module_id=ExternalModuleId.XR_HAND,
            state=state,
            summary="XRHand gesture/select mode; does not switch Scene.",
            metrics={"active_scene_id": _bb_str("global/active_scene_id", "")},
        )

    def _canvas_status(self) -> AppModuleStatus:
        return AppModuleStatus(
            module_id=ExternalModuleId.CANVAS_CONNECTION,
            state="ready",
            summary="Menu canvas connects core blocks to external module dock.",
            metrics={
                "active_model_id": _bb_str("global/active_model_id", "GOSLO_default"),
                "active_persona_id": _bb_str("global/active_persona_id", "goslo_parrot_default"),
                "active_scene_id": _bb_str("global/active_scene_id", "ar_handheld"),
                "active_workspace_id": _bb_str(
                    "global/active_workspace_id",
                    DEFAULT_WORKSPACE_ID,
                ),
            },
        )

    def list_paper_notes(self) -> list[dict[str, Any]]:
        """Return paper-note refs for the workdesk/report desk read model."""
        out: list[dict[str, Any]] = []
        for role in ("nanobot_report", "calendar_draft"):
            for handle in self.intent_workspace.list_active(role=role):
                meta = handle.metadata.custom_meta or {}
                out.append({
                    "ref_id": handle.ref_id,
                    "role": role,
                    "source": handle.metadata.origin,
                    "title": str(meta.get("title") or meta.get("action") or role),
                    "workspace_id": str(meta.get("workspace_id") or "workdesk"),
                    "kind": handle.kind.value if handle.kind else "",
                })
        return out

    def list_photo_refs(self) -> list[dict[str, Any]]:
        """Return lightweight photo refs; callers fetch payloads by ref id."""
        refs = self.intent_workspace.list_active(kinds=frozenset({StagedRefKind.PHOTO}))
        out: list[dict[str, Any]] = []
        for handle in refs:
            meta = handle.metadata.custom_meta or {}
            out.append({
                "ref_id": handle.ref_id,
                "role": str(meta.get("role") or "photo"),
                "photo_id": str(meta.get("photo_id") or handle.metadata.related_node_uuid),
                "source": handle.metadata.origin,
                "expires_at": handle.metadata.expires_at,
            })
        return out


def _default_obsidian_vault_path() -> Path:
    env = os.environ.get("GOSLO_OBSIDIAN_VAULT", "").strip()
    if env:
        return Path(env)
    return Path("D:/GOSLOParrot/GOSLObsidian/GOSLOParrot")


def _bb_value(key: str, default: Any = None) -> Any:
    try:
        bb = open_bb_client(name="app_facade.read", writer=None)
        value = bb.get(key)
        return default if value is None else value
    except Exception:
        return default


def _bb_str(key: str, default: str = "") -> str:
    value = _bb_value(key, default)
    if isinstance(value, Enum):
        return value.value
    return str(value or default)


__all__ = [
    "AppActionResult",
    "AppFirstVersionFacade",
    "AppModuleStatus",
    "AppToolCard",
    "AppToolId",
    "CameraMode",
    "ExternalModuleId",
    "PhotoAwarenessPolicy",
    "XrHandMode",
]
