"""Backend facade for the first App shell and menu-canvas white model.

This module intentionally exposes a small business surface over existing core
modules. Unity and the temporary Web smoke monitor can ask one place for App
module status instead of poking Blackboard, IntentWorkspace, or DSG directly.
"""

from __future__ import annotations

import json
import os
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


@dataclass(frozen=True)
class AppCanvasSnapshot:
    """Read-only payload for Unity menu canvas and the Web smoke monitor."""

    generated_at: float
    active_workspace_id: str
    module_statuses: tuple[AppModuleStatus, ...]
    workspaces: tuple[dict[str, Any], ...]
    paper_notes: tuple[dict[str, Any], ...]
    photo_refs: tuple[dict[str, Any], ...]

    def as_json(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "active_workspace_id": self.active_workspace_id,
            "module_statuses": [status.as_json() for status in self.module_statuses],
            "workspaces": list(self.workspaces),
            "paper_notes": list(self.paper_notes),
            "photo_refs": list(self.photo_refs),
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
        import time

        active_workspace_id = _bb_str("global/active_workspace_id", DEFAULT_WORKSPACE_ID)
        workspaces = tuple(w.as_json() for w in get_workspace_registry().list_workspaces())
        return AppCanvasSnapshot(
            generated_at=time.time(),
            active_workspace_id=active_workspace_id,
            module_statuses=self.list_module_statuses(),
            workspaces=workspaces,
            paper_notes=tuple(self.list_paper_notes()),
            photo_refs=tuple(self.list_photo_refs()),
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
    "CameraMode",
    "ExternalModuleId",
    "PhotoAwarenessPolicy",
    "XrHandMode",
]
