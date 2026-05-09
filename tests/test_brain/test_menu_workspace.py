from __future__ import annotations

from pathlib import Path

import py_trees
import pytest

from parrot.brain.menu_registry import MenuRegistry, MenuSelection
from parrot.brain.preset_loader import (
    DEFAULT_WORKSPACE_ID,
    SCHEMA_VERSION,
    Preset,
    PresetLoader,
    set_preset_loader_for_test,
)
from parrot.brain.workspace_registry import (
    WorkspaceRegistry,
    WorkspaceSummary,
    set_workspace_registry_for_test,
)
from parrot.brain.session_policy import (
    apply_capability_mode,
    is_silent_session,
    should_generate_reply,
)
from parrot.brain.perception_supervisor import PerceptionSupervisor
from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.tiers import AppCapabilityMode, DsgMode, VideoTier


@pytest.fixture(autouse=True)
def _reset_state():
    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    set_preset_loader_for_test(None)
    set_workspace_registry_for_test(None)
    yield
    set_preset_loader_for_test(None)
    set_workspace_registry_for_test(None)


def test_preset_v1_defaults_workspace() -> None:
    old_payload = {
        "schema_version": 1,
        "preset_id": "old_default",
        "active_model_id": "GOSLO_default",
        "active_persona_id": "goslo_parrot_default",
        "active_mode": ["BASE", "COMPANION"],
        "active_scene_id": "ar_handheld",
    }

    preset = Preset.from_json(old_payload)

    assert preset.active_workspace_id == DEFAULT_WORKSPACE_ID
    assert preset.as_json()["schema_version"] == SCHEMA_VERSION
    assert preset.as_json()["active_workspace_id"] == DEFAULT_WORKSPACE_ID


def test_menu_selection_applies_workspace_key(tmp_path: Path) -> None:
    set_preset_loader_for_test(PresetLoader(search_paths=[tmp_path / "presets"]))
    set_workspace_registry_for_test(WorkspaceRegistry(search_paths=[tmp_path / "workspaces"]))

    result = MenuRegistry().apply_selection(
        MenuSelection(
            persona_id="goslo_parrot_default",
            mode_flags=("BASE", "COMPANION"),
            scene_id="ar_handheld",
            model_id="GOSLO_default",
            workspace_id="workdesk",
        )
    )

    bb = open_bb_client(name="test.read", writer=None)
    assert result.success
    assert "global/active_workspace_id" in result.applied_keys
    assert bb.get("global/active_workspace_id") == "workdesk"


def test_workspace_registry_unknown_falls_back_without_tearing_session(tmp_path: Path) -> None:
    set_preset_loader_for_test(PresetLoader(search_paths=[tmp_path / "presets"]))
    registry = WorkspaceRegistry(search_paths=[tmp_path / "workspaces"])
    registry.save_workspace(
        WorkspaceSummary(
            workspace_id="custom_lab",
            display_name="Custom Lab",
            description="Saved user workspace",
        )
    )

    listed = registry.list_workspaces()
    assert any(w.workspace_id == "custom_lab" for w in listed)

    result = registry.apply_workspace("missing_workspace")

    bb = open_bb_client(name="test.workspace.read", writer=None)
    assert result.fallback_used
    assert result.active_workspace_id == DEFAULT_WORKSPACE_ID
    assert "unknown workspace_id" in result.errors[0]
    assert bb.get("global/active_workspace_id") == DEFAULT_WORKSPACE_ID


def test_session_only_silent_blocks_proactive_speech() -> None:
    profile = apply_capability_mode(AppCapabilityMode.SESSION_ONLY_SILENT)

    bb = open_bb_client(name="test.session_policy.read", writer=None)
    assert profile.microphone_enabled is False
    assert profile.greet_after_ar_placement is False
    assert bb.get("session/app_capability_mode") == AppCapabilityMode.SESSION_ONLY_SILENT
    assert is_silent_session() is True
    assert should_generate_reply("unit_test") is False


@pytest.mark.asyncio
async def test_perception_supervisor_applies_capability_profile_without_extra_writer() -> None:
    profile = apply_capability_mode(AppCapabilityMode.VOICE_ONLY_NO_VIDEO)
    supervisor = PerceptionSupervisor()

    applied = await supervisor.apply_capability_profile(profile, push_unity=False)

    bb = open_bb_client(name="test.supervisor_policy.read", writer=None)
    assert applied is True
    assert bb.get("session/video_tier") == VideoTier.VIDEO_OFF
    assert bb.get("session/dsg_mode") == DsgMode.DSG_TEXT_ONLY
