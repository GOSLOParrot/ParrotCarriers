from __future__ import annotations

from pathlib import Path
import os

import py_trees
import pytest

from parrot.brain.persona_loader import set_persona_loader_for_test
from parrot.brain.preset_loader import (
    PresetLoader,
    RoomProfile,
    set_preset_loader_for_test,
)
from parrot.brain.session_context_pack import (
    bootstrap_active_session_context_to_l15,
    load_active_session_context_bundle,
    reset_session_context_bootstrap_for_test,
)
from parrot.brain.soul import get_instructions
from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.parrot_actions import BehaviorMode


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _reset_state(monkeypatch: pytest.MonkeyPatch):
    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    set_persona_loader_for_test(None)
    set_preset_loader_for_test(
        PresetLoader(search_paths=[_repo_root() / "data" / "presets"])
    )
    reset_session_context_bootstrap_for_test()
    monkeypatch.delenv("PARROT_ACTIVE_ROOM_PROFILE_ID", raising=False)
    monkeypatch.delenv("PARROT_ACTIVE_ROOM_PROFILE", raising=False)
    monkeypatch.delenv("PARROT_DISABLE_SESSION_CONTEXT_PACK", raising=False)
    yield
    set_persona_loader_for_test(None)
    set_preset_loader_for_test(None)
    reset_session_context_bootstrap_for_test()


def test_ner_room_context_classifies_llm_and_l15_sources() -> None:
    bb = open_bb_client(name="test.session_context", writer="brain.preset_loader")
    bb.set("global/active_room_profile_id", "ner_lineb_room")

    bundle = load_active_session_context_bundle()
    by_ref = {source.ref: source for source in bundle.sources}

    roleplay_ref = (
        "codex_workspace/design_workspace/unity_ar_app/"
        "ner_roleplay_setting_obsidian_v0_20260511.md"
    )
    scene_ref = (
        "codex_workspace/design_workspace/unity_ar_app/"
        "ner_mochi_scene_v0_20260511.md"
    )
    persona_ref = "src/parrot/brain/personas/ner_companion.md"
    report_ref = (
        ".cursor/memory/architecture/Interface/"
        "app_v1_lineb_ner_realdevice_config_report_20260511.md"
    )

    assert bundle.room_profile_id == "ner_lineb_room"
    assert by_ref[roleplay_ref].prompt_target == "llm+l1_5"
    assert by_ref[roleplay_ref].l15_target == "obsidian_setting_roleplay"
    assert by_ref[roleplay_ref].ingest_payload is not None
    assert by_ref[roleplay_ref].ingest_payload["profile"] == "roleplay"
    assert by_ref[roleplay_ref].ingest_payload["obsidian_uuid"] == ""
    assert by_ref[scene_ref].prompt_target == "llm"
    assert by_ref[persona_ref].prompt_target == "persona_loader_only"
    assert by_ref[report_ref].prompt_target == "reference_only"
    assert "Ner LineB Roleplay Setting V0" in bundle.llm_prompt_block
    assert "Ner Mochi Scene V0" in bundle.llm_prompt_block
    assert "LineB + Ner Real-Device Config Report" not in bundle.llm_prompt_block
    assert len(bundle.l15_payloads) == 1


def test_soul_instructions_include_selected_room_context() -> None:
    bb = open_bb_client(name="test.session_context", writer="brain.preset_loader")
    bb.set("global/active_room_profile_id", "ner_lineb_room")
    bb.set("global/active_persona_id", "ner_companion")

    instructions = get_instructions(BehaviorMode.BASE | BehaviorMode.COMPANION)

    assert "play_capability" in instructions
    assert "[ROOM SESSION CONTEXT]" in instructions
    assert "RoomProfile=ner_lineb_room" in instructions
    assert "Ner LineB Roleplay Setting V0" in instructions
    assert "Ner Mochi Scene V0" in instructions
    assert "Persona rules still come from the active persona file" in instructions


def test_unsaved_room_profile_draft_apply_preserves_setting_refs(
    tmp_path: Path,
) -> None:
    """Bug A regression (audit 2026-05-11).

    Applying a RoomProfile *draft* (one not yet saved to
    ``data/presets/<id>.json``) used to lose its ``setting_file_refs``:
    ``apply_room_profile`` only wrote the id, then
    ``session_context_pack._load_room_profile`` did
    ``preset_loader.load_room_profile(id)`` which read disk and either
    silently fell back to ``default`` or returned a stale on-disk version.

    With the fix, ``apply_room_profile`` also writes the full payload to
    ``global/active_room_profile`` and ``_load_room_profile`` honours that
    payload when its id matches the active id.
    """
    note = tmp_path / "Draft Setting.md"
    note.write_text(
        """---
profile: roleplay
title: Draft Setting Source
obsidian_note_key: test/draft/setting
---

Draft body for the unsaved RoomProfile.
""",
        encoding="utf-8",
    )
    # Empty preset dir on purpose: the draft id has no on-disk file.
    preset_dir = tmp_path / "presets"
    preset_dir.mkdir()
    loader = PresetLoader(search_paths=[preset_dir])
    set_preset_loader_for_test(loader)

    draft = RoomProfile(
        room_profile_id="unsaved_draft_room",
        display_name="Unsaved Draft Room",
        persona_id="ner_companion",
        model_id="ner_skin2",
        line_id="line_b",
        line_profile_id="lineb_ner_ja_test",
        setting_file_refs=(str(note),),
    )
    apply_result = loader.apply_room_profile(draft)
    assert apply_result.success
    assert "global/active_room_profile" in apply_result.applied_keys

    bundle = load_active_session_context_bundle()
    assert bundle.room_profile_id == "unsaved_draft_room"
    assert any(source.ref == str(note) for source in bundle.sources)
    roleplay_source = next(
        source for source in bundle.sources if source.ref == str(note)
    )
    assert roleplay_source.prompt_target == "llm+l1_5"
    assert "Draft Setting Source" in bundle.llm_prompt_block


@pytest.mark.asyncio
async def test_l15_bootstrap_dedupe_allows_edited_setting_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    note = tmp_path / "Ner Setting.md"
    note.write_text(
        """---
profile: roleplay
title: Ner Runtime Setting
obsidian_note_key: test/ner/runtime
---

First version.
""",
        encoding="utf-8",
    )
    preset_dir = tmp_path / "presets"
    loader = PresetLoader(search_paths=[preset_dir])
    loader.save_room_profile(
        RoomProfile(
            room_profile_id="runtime_ner",
            display_name="Runtime Ner",
            persona_id="ner_companion",
            model_id="ner_skin2",
            line_id="line_b",
            line_profile_id="lineb_ner_ja_test",
            setting_file_refs=(str(note),),
        )
    )
    set_preset_loader_for_test(loader)

    bb = open_bb_client(name="test.session_context", writer="brain.preset_loader")
    bb.set("global/active_room_profile_id", "runtime_ner")

    class FakeRunner:
        def __init__(self) -> None:
            self.events: list[dict] = []

        async def fire_event(self, event: dict) -> list:
            self.events.append(event)
            return []

    fake = FakeRunner()
    import parrot.dsg.triggers.runner as runner_module

    monkeypatch.setattr(runner_module, "get_trigger_runner", lambda: fake)

    assert await bootstrap_active_session_context_to_l15() == 1
    assert await bootstrap_active_session_context_to_l15() == 0
    assert len(fake.events) == 1

    note.write_text(
        """---
profile: roleplay
title: Ner Runtime Setting
obsidian_note_key: test/ner/runtime
---

Second version.
""",
        encoding="utf-8",
    )
    current_mtime = note.stat().st_mtime
    os.utime(note, (current_mtime + 10.0, current_mtime + 10.0))

    assert await bootstrap_active_session_context_to_l15() == 1
    assert len(fake.events) == 2
