from __future__ import annotations

from pathlib import Path

import py_trees
import pytest

from parrot.brain.intent_workspace import IntentWorkspace, StagedRefKind, set_intent_workspace_for_test
from parrot.brain.app_first_version import (
    AppFirstVersionFacade,
    CameraMode,
    ExternalModuleId,
    PhotoAwarenessPolicy,
    XrHandMode,
)
from parrot.brain.preset_loader import PresetLoader, set_preset_loader_for_test
from parrot.brain.workspace_registry import WorkspaceRegistry, set_workspace_registry_for_test
from parrot.scheduler.blackboard import open_bb_client


@pytest.fixture(autouse=True)
def _reset_state():
    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    set_intent_workspace_for_test(IntentWorkspace())
    set_preset_loader_for_test(None)
    set_workspace_registry_for_test(None)
    yield
    set_intent_workspace_for_test(None)
    set_preset_loader_for_test(None)
    set_workspace_registry_for_test(None)


def _write_note(path: Path, frontmatter: str, body: str = "Body") -> None:
    path.write_text(f"---\n{frontmatter.strip()}\n---\n\n{body}\n", encoding="utf-8")


def test_v1_module_statuses_cover_app_shell(tmp_path: Path) -> None:
    facade = AppFirstVersionFacade(obsidian_vault_path=tmp_path / "missing")

    statuses = {s.module_id: s for s in facade.list_module_statuses()}

    assert set(statuses) == {
        ExternalModuleId.GOOGLE_CALENDAR,
        ExternalModuleId.OBSIDIAN,
        ExternalModuleId.GOSLO_MODULE,
        ExternalModuleId.NANOBOT,
        ExternalModuleId.PHOTO_CAMERA,
        ExternalModuleId.XR_HAND,
        ExternalModuleId.CANVAS_CONNECTION,
    }
    assert statuses[ExternalModuleId.CANVAS_CONNECTION].metrics["active_workspace_id"]
    assert statuses[ExternalModuleId.GOOGLE_CALENDAR].metrics["pending_draft_count"] == 0


def test_obsidian_status_accepts_setting_notes_without_uuid(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    _write_note(
        vault / "Ojou Mansion.md",
        """
profile: "roleplay"
kind: "zone"
title: "大小姐宅邸设定"
tags: "goslo,test,roleplay"
""",
    )
    _write_note(
        vault / "Ref Missing UUID.md",
        """
profile: "ref"
title: "Ref without UUID"
""",
    )

    status = AppFirstVersionFacade(obsidian_vault_path=vault).module_status(
        ExternalModuleId.OBSIDIAN
    )

    assert status.state == "ingest_ready"
    assert status.metrics["markdown_count"] == 2
    assert status.metrics["ingest_ready_count"] == 1
    assert status.metrics["profile_counts"] == {"roleplay": 1}
    assert "Ref Missing UUID.md" in status.refs["invalid_notes"]


def test_camera_and_awareness_write_backend_owned_state() -> None:
    facade = AppFirstVersionFacade()

    camera_result = facade.set_camera_mode(CameraMode.PHOTO_READY)
    awareness_result = facade.set_photo_awareness(
        PhotoAwarenessPolicy.AWARE_SILENT,
        enabled=True,
    )

    bb = open_bb_client(name="test.app_facade.read", writer=None)
    assert camera_result.success
    assert awareness_result.success
    assert bb.get("session/camera_mode") == CameraMode.PHOTO_READY.value
    assert bb.get("session/photo_awareness_policy") == PhotoAwarenessPolicy.AWARE_SILENT.value
    assert bb.get("session/photo_awareness_enabled") is True
    assert bb.get("session/photo_awareness_allows_interrupt") is False
    assert bb.get("session/photo_awareness_preview_ttl_seconds") == 15 * 60


@pytest.mark.asyncio
async def test_google_calendar_write_action_creates_intent_workspace_draft() -> None:
    facade = AppFirstVersionFacade()

    result = await facade.create_calendar_draft(
        action="create",
        title="Review GOSLO app shell",
        time_range="2026-05-10 15:00-16:00",
    )

    assert result.success
    assert result.intent_workspace_ref_id
    drafts = facade.intent_workspace.list_active(role="calendar_draft")
    assert len(drafts) == 1
    assert drafts[0].kind == StagedRefKind.DOC
    google = facade.module_status(ExternalModuleId.GOOGLE_CALENDAR)
    assert google.metrics["pending_draft_count"] == 1


@pytest.mark.asyncio
async def test_nanobot_report_becomes_report_note() -> None:
    facade = AppFirstVersionFacade()

    result = await facade.stage_nanobot_report(
        task_id="task_123",
        title="Calendar audit",
        body="Nanobot result body",
    )

    assert result.success
    reports = facade.intent_workspace.list_active(role="nanobot_report")
    assert len(reports) == 1
    assert reports[0].kind == StagedRefKind.RICH_REPORT
    nanobot = facade.module_status(ExternalModuleId.NANOBOT)
    assert nanobot.metrics["report_count"] == 1
    paper = facade.list_paper_notes()
    assert paper[0]["title"] == "Calendar audit"
    assert paper[0]["workspace_id"] == "report_desk"


@pytest.mark.asyncio
async def test_canvas_snapshot_collects_workspace_notes_and_photo_refs(tmp_path: Path) -> None:
    set_preset_loader_for_test(PresetLoader(search_paths=[tmp_path / "presets"]))
    set_workspace_registry_for_test(WorkspaceRegistry(search_paths=[tmp_path / "workspaces"]))
    facade = AppFirstVersionFacade(obsidian_vault_path=tmp_path / "missing")

    workspace_result = facade.apply_workspace("workdesk")
    await facade.create_calendar_draft(action="create", title="Draft event")
    await facade.stage_nanobot_report(task_id="task_1", title="Report note", body="Ready")

    snapshot = facade.canvas_snapshot().as_json()

    assert workspace_result.success
    assert snapshot["active_workspace_id"] == "workdesk"
    assert len(snapshot["module_statuses"]) == 7
    assert any(w["workspace_id"] == "workdesk" for w in snapshot["workspaces"])
    assert {note["role"] for note in snapshot["paper_notes"]} == {
        "calendar_draft",
        "nanobot_report",
    }


def test_xrhand_mode_updates_without_scene_switch() -> None:
    bb = open_bb_client(name="test.seed", writer="brain.preset_loader")
    bb.set("global/active_scene_id", "ar_handheld")
    facade = AppFirstVersionFacade()

    result = facade.set_xrhand_mode(XrHandMode.GESTURE_SELECT)

    assert result.success
    assert bb.get("session/xrhand_mode") == XrHandMode.GESTURE_SELECT.value
    assert bb.get("global/active_scene_id") == "ar_handheld"
    status = facade.module_status(ExternalModuleId.XR_HAND)
    assert status.state == "gesture_select"
