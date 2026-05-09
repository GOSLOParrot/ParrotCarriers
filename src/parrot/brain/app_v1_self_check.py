"""Autonomous App v1 business self-check.

This is a deterministic smoke routine for the first app shell. It exercises
the same facade calls that Unity and the temporary Web monitor will use:
workspace switch, camera mode, Photo Awareness, Google draft, Nanobot paper
note, and canvas snapshot assembly.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from parrot.brain.app_first_version import (
    AppFirstVersionFacade,
    CameraMode,
    ExternalModuleId,
    PhotoAwarenessPolicy,
)
from parrot.brain.app_test_harness import simulate_bbox_event, simulate_focus_event
from parrot.brain.graphiti_console import graphiti_status
from parrot.brain.photo_awareness import handle_photo_preview_awareness


@dataclass(frozen=True)
class AppV1SelfCheckResult:
    """Serializable result for CLI, Web monitor, or docs capture."""

    passed: bool
    checks: tuple[dict[str, Any], ...]
    snapshot: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "checks": list(self.checks),
            "snapshot": dict(self.snapshot),
        }


async def run_app_v1_self_check(
    *,
    obsidian_vault_path: Path | str | None = None,
) -> AppV1SelfCheckResult:
    """Run the App v1 business checks against the current in-process runtime."""
    facade = AppFirstVersionFacade(obsidian_vault_path=obsidian_vault_path)
    checks: list[dict[str, Any]] = []

    def record(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    statuses = facade.list_module_statuses()
    record(
        "module_status_count",
        len(statuses) == len(ExternalModuleId),
        f"{len(statuses)}/{len(ExternalModuleId)}",
    )

    workspace = facade.apply_workspace("workdesk")
    record("workspace_switch_workdesk", workspace.success, workspace.message)

    camera = facade.set_camera_mode(CameraMode.PHOTO_READY)
    record("camera_mode_photo_ready", camera.success, camera.message)

    capture_request = facade.request_camera_capture(
        candidate_subject_uuid="selfcheck_candidate",
        awareness_policy=PhotoAwarenessPolicy.AWARE_SILENT,
    )
    record("camera_capture_request", capture_request.success, capture_request.message)

    awareness = facade.set_photo_awareness(
        PhotoAwarenessPolicy.AWARE_SILENT,
        enabled=True,
        preview_ttl_seconds=60,
    )
    record("photo_awareness_silent", awareness.success, awareness.message)

    decision = handle_photo_preview_awareness(
        photo_id="selfcheck_photo",
        source_event_id="selfcheck_preview_event",
        payload={
            "preview_jpeg_b64": "U0VMRkNIRUNL",
            "pose": {"px": 0, "py": 0, "pz": 0},
        },
    )
    if not decision.preview_ref_id:
        # If the self-check runs inside an already-active event loop, the
        # synchronous observer schedules preview staging as a task. Yield once
        # so the smoke result observes the same completed state Unity will see.
        await asyncio.sleep(0)
    preview_refs = facade.intent_workspace.list_active(role="photo_preview_awareness")
    record(
        "photo_awareness_preview_ref",
        bool(preview_refs) and decision.notify_goslo and not decision.allow_interrupt,
        preview_refs[0].ref_id if preview_refs else decision.reason,
    )

    google = await facade.create_calendar_draft(
        action="create",
        title="App v1 self-check calendar draft",
        time_range="2026-05-10 03:00-03:15",
    )
    record("google_calendar_draft", google.success and bool(google.intent_workspace_ref_id))

    report = await facade.stage_nanobot_report(
        task_id="selfcheck_nanobot",
        title="Self-check report",
        body="Nanobot paper note smoke payload.",
    )
    record("nanobot_report_note", report.success and bool(report.intent_workspace_ref_id))

    focus = simulate_focus_event(focus_id="fc_selfcheck")
    bbox = simulate_bbox_event(bbox_id="bb_selfcheck")
    record("focus_tool_ecp_flow", focus.success, focus.event_id)
    record("bbox_tool_ecp_flow", bbox.success, bbox.event_id)

    snapshot = facade.canvas_snapshot().as_json()
    record(
        "tool_cabinet_complete",
        len(snapshot.get("tool_cabinet", [])) >= 6,
        str(len(snapshot.get("tool_cabinet", []))),
    )
    record(
        "canvas_snapshot_paper_notes",
        len(snapshot.get("paper_notes", [])) >= 2,
        str(len(snapshot.get("paper_notes", []))),
    )
    record(
        "canvas_snapshot_photo_refs",
        any(ref.get("role") == "photo_preview_awareness" for ref in snapshot.get("photo_refs", [])),
        str(len(snapshot.get("photo_refs", []))),
    )
    g_status = graphiti_status().as_json()
    record(
        "graphiti_console_graceful_status",
        bool(g_status.get("success")),
        str(g_status.get("message", "")),
    )

    passed = all(check["ok"] for check in checks)
    return AppV1SelfCheckResult(
        passed=passed,
        checks=tuple(checks),
        snapshot=snapshot,
    )


__all__ = ["AppV1SelfCheckResult", "run_app_v1_self_check"]
