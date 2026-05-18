from __future__ import annotations

import json
from pathlib import Path

import py_trees
import pytest

from parrot.brain.menu_registry import MenuRegistry, MenuSelection
from parrot.brain.line_profile import (
    DEFAULT_LINEB_PROFILE_ID,
    LineProfileLoader,
    active_lineb_runtime_settings,
    set_line_profile_loader_for_test,
)
from parrot.brain.model_manifest_registry import (
    ModelManifestRegistry,
    set_model_manifest_registry_for_test,
)
from parrot.brain.persona_loader import PersonaLoader
from parrot.brain.preset_loader import (
    DEFAULT_WORKSPACE_ID,
    ROOM_PROFILE_SCHEMA_VERSION,
    SCHEMA_VERSION,
    Preset,
    PresetLoader,
    RoomProfile,
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
from parrot.brain.tools import (
    PARROT_ANIMATION_TOOLS,
    animate,
    fly_to,
    play_capability,
    play_dance,
    return_to_view,
    tools_for_active_model,
)
from parrot.brain.perception_supervisor import PerceptionSupervisor
from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.parrot_actions import BehaviorMode
from parrot.shared.tiers import AppCapabilityMode, DsgMode, VideoTier


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _reset_state(monkeypatch: pytest.MonkeyPatch):
    for key in (
        "PARROT_LLM_PIPELINE",
        "PARROT_LINE_PROFILE",
        "PARROT_ACTIVE_LINE_PROFILE_ID",
        "PARROT_LINEB_TTS_PROVIDER",
        "PARROT_LINEB_CARTESIA_VOICE_ID",
        "PARROT_LINEB_VOICEPRINT_ENABLED",
        "PARROT_LINEB_VOICEPRINT_PROFILE_ID",
        "PARROT_LINEB_VOICEPRINT_PROVIDER",
        "PARROT_LINEB_VOICEPRINT_MANIFEST",
        "PARROT_VOICEPRINT_AUDIO_ROOT",
        "PARROT_AUDIO_OUTPUT_ROUTE",
        "PARROT_LINEB_ECHO_HANDLING_MODE",
        "GOOGLE_TTS_VOICE",
        "GOOGLE_TTS_LANGUAGE",
    ):
        monkeypatch.delenv(key, raising=False)
    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    set_preset_loader_for_test(None)
    set_line_profile_loader_for_test(None)
    set_model_manifest_registry_for_test(None)
    set_workspace_registry_for_test(None)
    yield
    set_preset_loader_for_test(None)
    set_line_profile_loader_for_test(None)
    set_model_manifest_registry_for_test(None)
    set_workspace_registry_for_test(None)


class TestAuditRound4MenuCanvasGuards:
    """Audit Round 4 (2026-05-11) regressions: Bugs G + I + J.

    Bug G: RoomSetting save could overwrite the builtin ``default`` preset
    (and other reserved sentinel ids) without any guard, silently rebranding
    the system default.

    Bug I: ``MenuRegistry.apply_selection`` silently substituted the
    fallback workspace when an unknown ``workspace_id`` was passed,
    returning ``success=True`` with no signal that a substitution
    happened. Menu canvas could believe its requested workspace was
    active when actually mansion_hub was applied.

    Bug J: ``parse_capability_mode`` silently returned ``FULL_AR_COMPANION``
    on unknown non-empty inputs. Now logs a warning so misconfigured
    Unity payloads / typos in env vars are visible in operator logs.
    """

    def test_save_reserved_room_profile_id_raises(self, tmp_path: Path) -> None:
        from parrot.brain.preset_loader import (
            RESERVED_ROOM_PROFILE_IDS,
            ReservedRoomProfileIdError,
        )

        loader = PresetLoader(search_paths=[tmp_path / "presets"])
        for reserved_id in RESERVED_ROOM_PROFILE_IDS:
            with pytest.raises(ReservedRoomProfileIdError):
                loader.save_room_profile(
                    RoomProfile(
                        room_profile_id=reserved_id,
                        display_name=f"Hijack {reserved_id}",
                        model_id="evil_model",
                    )
                )
        # Sanity: a fresh non-reserved id still saves successfully
        non_reserved_path = loader.save_room_profile(
            RoomProfile(
                room_profile_id="audit_round4_test",
                display_name="Audit Round 4 Test",
            )
        )
        assert non_reserved_path.exists()

    def test_save_reserved_id_via_facade_returns_structured_error(
        self,
        tmp_path: Path,
    ) -> None:
        from parrot.brain.app_first_version import AppFirstVersionFacade
        from parrot.brain.preset_loader import RESERVED_ROOM_PROFILE_IDS

        set_preset_loader_for_test(PresetLoader(search_paths=[tmp_path / "presets"]))
        facade = AppFirstVersionFacade()
        result = facade.save_room_profile(
            {
                "schema_version": ROOM_PROFILE_SCHEMA_VERSION,
                "kind": "room_profile",
                "room_profile_id": "default",
                "display_name": "Hijacked Default",
            }
        )
        assert result["status"] == "error"
        assert result["reason"] == "reserved_room_profile_id"
        assert result["room_profile_id"] == "default"
        assert set(result["reserved_ids"]) == RESERVED_ROOM_PROFILE_IDS

    def test_apply_menu_selection_surfaces_workspace_fallback_warning(
        self,
        tmp_path: Path,
    ) -> None:
        set_preset_loader_for_test(PresetLoader(search_paths=[tmp_path / "presets"]))
        registry = MenuRegistry()
        result = registry.apply_selection(
            MenuSelection(
                persona_id="goslo_parrot_default",
                mode_flags=("BASE", "COMPANION"),
                scene_id="ar_handheld",
                model_id="GOSLO_default",
                workspace_id="nonexistent_xyz",
            )
        )
        assert result.success
        assert any(
            "nonexistent_xyz" in w and "substituted" in w for w in result.warnings
        ), f"expected substitution warning, got warnings={result.warnings}"

    def test_apply_menu_selection_known_workspace_no_warning(
        self,
        tmp_path: Path,
    ) -> None:
        set_preset_loader_for_test(PresetLoader(search_paths=[tmp_path / "presets"]))
        registry = MenuRegistry()
        result = registry.apply_selection(
            MenuSelection(
                persona_id="goslo_parrot_default",
                mode_flags=("BASE", "COMPANION"),
                scene_id="ar_handheld",
                model_id="GOSLO_default",
                workspace_id=DEFAULT_WORKSPACE_ID,
            )
        )
        assert result.success
        assert result.warnings == ()

    def test_capability_mode_unknown_input_logs_warning(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        with caplog.at_level("WARNING", logger="parrot.brain.session_policy"):
            profile = apply_capability_mode("totally_bogus_mode")
        assert profile.mode == AppCapabilityMode.FULL_AR_COMPANION
        assert any(
            "totally_bogus_mode" in record.message for record in caplog.records
        ), f"expected warning about bogus mode, got records={caplog.records}"

    def test_capability_mode_empty_input_no_warning(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        # Empty / None is the legitimate "no preference" case; no spam.
        with caplog.at_level("WARNING", logger="parrot.brain.session_policy"):
            apply_capability_mode("")
            apply_capability_mode(None)
        assert not any(
            "unknown capability mode" in record.message for record in caplog.records
        )


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


def test_room_profile_migrates_v2_preset_and_round_trips(tmp_path: Path) -> None:
    loader = PresetLoader(search_paths=[tmp_path / "presets"])
    loader.save(
        Preset(
            preset_id="study",
            active_model_id="GOSLO_default",
            active_persona_id="goslo_parrot_default",
            active_scene_id="ar_handheld",
            active_workspace_id="workdesk",
            metadata={
                "user_label": "Study Room",
                "line_id": "line_b",
                "theme_skin": "manor",
            },
        )
    )

    profile = loader.load_room_profile("study")
    path = loader.save_room_profile(profile)
    raw = json.loads(path.read_text(encoding="utf-8"))

    assert profile.room_profile_id == "study"
    assert profile.display_name == "Study Room"
    assert profile.line_id == "line_b"
    assert profile.line_profile_id == DEFAULT_LINEB_PROFILE_ID
    assert profile.workspace_id == "workdesk"
    assert raw["schema_version"] == ROOM_PROFILE_SCHEMA_VERSION
    assert raw["kind"] == "room_profile"
    assert raw["model_id"] == "GOSLO_default"
    assert raw["line_profile_id"] == DEFAULT_LINEB_PROFILE_ID


def test_room_profile_apply_writes_startup_active_keys(tmp_path: Path) -> None:
    loader = PresetLoader(search_paths=[tmp_path / "presets"])
    profile = RoomProfile(
        room_profile_id="ar_default",
        display_name="AR Default",
        line_id="line_a",
        line_profile_id="linea_gemini_realtime",
        experience_mode="ar_companion",
        skin_id="goslo_blue",
    )

    result = loader.apply_room_profile(profile)

    bb = open_bb_client(name="test.room_profile.read", writer=None)
    assert result.success
    assert "global/active_room_profile_id" in result.applied_keys
    assert bb.get("global/active_room_profile_id") == "ar_default"
    assert bb.get("global/active_line_id") == "line_a"
    assert bb.get("global/active_line_profile_id") == "linea_gemini_realtime"
    assert bb.get("global/active_experience_mode") == "ar_companion"
    assert bb.get("global/active_scene_skin_id") == "goslo_blue"


def test_line_profile_loader_reads_default_config_and_env_override(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "line_profiles"
    config_dir.mkdir()
    (config_dir / "lineb_test.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "kind": "line_profile",
                "line_profile_id": "lineb_test",
                "display_name": "LineB Test",
                "line_id": "line_b",
                "asr": {"languages": ["ja-JP"]},
                "tts": {"language": "ja-JP", "voice_name": "ja-JP-Neural2-B"},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("GOOGLE_TTS_VOICE", "ja-JP-Neural2-C")
    monkeypatch.delenv("GOOGLE_STT_LANGUAGES", raising=False)
    loader = LineProfileLoader(search_paths=[config_dir])

    profile = loader.load("lineb_test", apply_env=True)

    assert profile.line_profile_id == "lineb_test"
    assert profile.asr.languages == ("ja-JP",)
    assert profile.tts.voice_name == "ja-JP-Neural2-C"


def test_line_profile_empty_env_does_not_clear_saved_voice(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "line_profiles"
    config_dir.mkdir()
    (config_dir / "lineb_voice.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "kind": "line_profile",
                "line_profile_id": "lineb_voice",
                "display_name": "LineB Voice",
                "line_id": "line_b",
                "tts": {"language": "ja-JP", "voice_name": "ja-JP-Neural2-B"},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("GOOGLE_TTS_VOICE", "")
    loader = LineProfileLoader(search_paths=[config_dir])

    profile = loader.load("lineb_voice", apply_env=True)

    assert profile.tts.voice_name == "ja-JP-Neural2-B"


def test_line_profile_cartesia_env_uses_profile_as_source_of_truth(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "line_profiles"
    config_dir.mkdir()
    (config_dir / "lineb_cartesia.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "kind": "line_profile",
                "line_profile_id": "lineb_cartesia",
                "display_name": "LineB Cartesia",
                "line_id": "line_b",
                "tts": {
                    "provider": "cartesia.TTS",
                    "language": "ja-JP",
                    "voice_name": "profile-voice-id",
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("PARROT_LINEB_TTS_PROVIDER", raising=False)
    monkeypatch.delenv("PARROT_LINEB_CARTESIA_VOICE_ID", raising=False)
    loader = LineProfileLoader(search_paths=[config_dir])

    profile = loader.load("lineb_cartesia", apply_env=True)

    assert profile.tts.provider == "cartesia.TTS"
    assert profile.tts.voice_name == "profile-voice-id"
    set_line_profile_loader_for_test(loader)
    monkeypatch.setenv("PARROT_ACTIVE_LINE_PROFILE_ID", "lineb_cartesia")
    runtime = active_lineb_runtime_settings()
    assert runtime.tts_provider == "cartesia.TTS"
    assert runtime.tts_voice == "profile-voice-id"

    monkeypatch.setenv("PARROT_LINEB_CARTESIA_VOICE_ID", "env-voice-id")
    profile = loader.load("lineb_cartesia", apply_env=True)

    assert profile.tts.voice_name == "env-voice-id"


def test_repo_ner_line_profile_and_room_setting_are_selectable() -> None:
    root = _repo_root()
    line_loader = LineProfileLoader(search_paths=[root / "data" / "line_profiles"])
    preset_loader = PresetLoader(search_paths=[root / "data" / "presets"])

    line_profile = line_loader.load("lineb_ner_ja_test")
    room_profile = preset_loader.load_room_profile("ner_lineb_room")

    assert line_profile.line_id == "line_b"
    assert line_profile.asr.languages == ("ja-JP", "cmn-CN", "en-US")
    assert line_profile.tts.language == "ja-JP"
    assert line_profile.tts.provider == "cartesia.TTS"
    assert line_profile.tts.voice_name == "bfd1cc5a-5c3b-4e88-b7be-df9f3ec7e9a5"
    assert line_profile.voiceprint.enabled is True
    assert "not an official character voice" in line_profile.tts.style_note
    assert room_profile.model_id == "ner_skin2"
    assert room_profile.persona_id == "ner_companion"
    assert room_profile.line_profile_id == "lineb_ner_ja_test"
    assert (
        "codex_workspace/design_workspace/unity_ar_app/"
        "ner_roleplay_setting_obsidian_v0_20260511.md"
    ) in room_profile.setting_file_refs


def test_ner_roleplay_setting_is_uuid_free_obsidian_source() -> None:
    setting = (
        _repo_root()
        / "codex_workspace"
        / "design_workspace"
        / "unity_ar_app"
        / "ner_roleplay_setting_obsidian_v0_20260511.md"
    ).read_text(encoding="utf-8")
    frontmatter = setting.split("---", 2)[1]

    assert "profile: roleplay" in frontmatter
    assert "obsidian_note_key: goslo/app/ner/roleplay_setting_v0" in frontmatter
    assert "obsidian_uuid" not in frontmatter
    assert "Voice actor / CV metadata is reference-only" in setting
    assert "cheek_pinch_warning" in setting


def test_ner_persona_loads_custom_capability_and_voice_trigger_rules() -> None:
    persona = PersonaLoader().load(
        "ner_companion",
        mode=BehaviorMode.BASE | BehaviorMode.COMPANION,
    )

    assert persona is not None
    assert "play_capability" in persona.text
    assert "animate: Reserved" in persona.text
    assert "cheek_pinch_warning" in persona.text
    assert "Do not imitate a real voice actor" in persona.text
    assert "Default to Chinese" in persona.text


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


def test_menu_registry_lists_ner_manifest_model() -> None:
    snapshot = MenuRegistry().list_blocks()
    models = {m.model_id: m for m in snapshot.models}

    assert "GOSLO_default" in models
    assert "ner_skin2" in models
    assert "face_happy" in models["ner_skin2"].declared_capability_ids
    assert models["GOSLO_default"].parrot_reflex_enabled is True
    assert models["ner_skin2"].parrot_reflex_enabled is False
    assert "fly" not in models["ner_skin2"].declared_capability_ids
    assert "perch" not in models["ner_skin2"].declared_capability_ids


def test_model_manifest_registry_reads_capability_ids() -> None:
    registry = ModelManifestRegistry()

    ner = registry.get("ner_skin2")

    assert ner is not None
    assert registry.supports("GOSLO_default", "fly")
    assert not registry.supports("ner_skin2", "fly")
    assert registry.supports("ner_skin2", "face_happy")
    assert registry.supports("ner_skin2", "face_serious")
    assert registry.capability("ner_skin2", "face_angry").parameters["variants"][-1] == "Angry_8"
    assert registry.supports("ner_skin2", "cheek_pinch_hold")
    assert registry.capability("ner_skin2", "cheek_pinch_hold").kind.value == "procedural"
    assert "touch_idle" in registry.capability_ids("ner_skin2")


def test_tools_for_active_model_hides_parrot_verbs_for_ner() -> None:
    bb = open_bb_client(name="test.model_tools.write", writer="brain.preset_loader")
    bb.set("global/active_model_id", "ner_skin2")

    tools = tools_for_active_model()

    assert play_capability in tools
    assert fly_to not in tools
    assert return_to_view not in tools
    assert animate not in tools
    assert not any(tool in tools for tool in PARROT_ANIMATION_TOOLS)

    bb.set("global/active_model_id", "GOSLO_default")
    goslo_tools = tools_for_active_model()

    assert fly_to in goslo_tools
    assert return_to_view in goslo_tools
    assert animate not in goslo_tools
    assert play_dance in goslo_tools
    assert all(tool in goslo_tools for tool in PARROT_ANIMATION_TOOLS)
    assert play_capability not in goslo_tools


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
