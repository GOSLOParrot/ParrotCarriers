from __future__ import annotations

from pathlib import Path

import py_trees
import pytest

from parrot.brain.intent_workspace import IntentWorkspace, StagedRefKind, set_intent_workspace_for_test
from parrot.brain.line_profile import LineProfileLoader, set_line_profile_loader_for_test
from parrot.brain.lineb_audio_guard import reset_lineb_audio_guard_for_test
from parrot.brain.app_first_version import (
    AppFirstVersionFacade,
    AppToolId,
    CameraMode,
    ExternalModuleId,
    PhotoAwarenessPolicy,
    XrHandMode,
)
from parrot.brain.preset_loader import PresetLoader, RoomProfile, set_preset_loader_for_test
from parrot.brain.workspace_registry import WorkspaceRegistry, set_workspace_registry_for_test
from parrot.scheduler.blackboard import open_bb_client


@pytest.fixture(autouse=True)
def _reset_state():
    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    reset_lineb_audio_guard_for_test()
    set_intent_workspace_for_test(IntentWorkspace())
    set_line_profile_loader_for_test(None)
    set_preset_loader_for_test(None)
    set_workspace_registry_for_test(None)
    yield
    reset_lineb_audio_guard_for_test()
    set_intent_workspace_for_test(None)
    set_line_profile_loader_for_test(None)
    set_preset_loader_for_test(None)
    set_workspace_registry_for_test(None)


def _write_note(path: Path, frontmatter: str, body: str = "Body") -> None:
    path.write_text(f"---\n{frontmatter.strip()}\n---\n\n{body}\n", encoding="utf-8")


def test_v1_module_statuses_cover_app_shell(tmp_path: Path) -> None:
    facade = AppFirstVersionFacade(obsidian_vault_path=tmp_path / "missing")

    statuses = {s.module_id: s for s in facade.list_module_statuses()}

    assert set(statuses) == {
        ExternalModuleId.VOICE_PIPELINE,
        ExternalModuleId.GOOGLE_CALENDAR,
        ExternalModuleId.OBSIDIAN,
        ExternalModuleId.GOSLO_MODULE,
        ExternalModuleId.NANOBOT,
        ExternalModuleId.PHOTO_CAMERA,
        ExternalModuleId.XR_HAND,
        ExternalModuleId.CANVAS_CONNECTION,
    }
    assert statuses[ExternalModuleId.CANVAS_CONNECTION].metrics["active_workspace_id"]
    assert statuses[ExternalModuleId.VOICE_PIPELINE].metrics["active_line_id"] == "line_a"
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
    capture_result = facade.request_camera_capture(candidate_subject_uuid="obj_1")
    awareness_result = facade.set_photo_awareness(
        PhotoAwarenessPolicy.AWARE_SILENT,
        enabled=True,
    )

    bb = open_bb_client(name="test.app_facade.read", writer=None)
    assert camera_result.success
    assert capture_result.success
    assert awareness_result.success
    assert bb.get("session/camera_mode") == CameraMode.CAPTURE_LOCKED.value
    assert bb.get("session/photo_capture_request")["candidate_subject_uuid"] == "obj_1"
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
    assert len(snapshot["module_statuses"]) == 8
    assert any(w["workspace_id"] == "workdesk" for w in snapshot["workspaces"])
    assert {note["role"] for note in snapshot["paper_notes"]} == {
        "calendar_draft",
        "nanobot_report",
    }
    assert {tool["tool_id"] for tool in snapshot["tool_cabinet"]} >= {
        AppToolId.CAMERA.value,
        AppToolId.MAGNIFIER_FOCUS.value,
        AppToolId.BOUNDARY_BOX.value,
        AppToolId.NOTE_INBOX.value,
    }
    assert snapshot["asset_manifest"]["schema_version"] == 1


def test_tool_cabinet_documents_camera_and_attention_tools() -> None:
    facade = AppFirstVersionFacade()

    tools = {tool.tool_id: tool for tool in facade.list_tool_cabinet()}

    assert set(tools) == set(AppToolId)
    assert "PhotoController" in " ".join(tools[AppToolId.CAMERA].flow)
    assert "/api/app/test/focus" in tools[AppToolId.MAGNIFIER_FOCUS].action_endpoints
    assert "/api/app/test/bbox" in tools[AppToolId.BOUNDARY_BOX].action_endpoints
    assert tools[AppToolId.NOTE_INBOX].asset_slot == "paper_note_newspaper"


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


def test_voice_pipeline_status_reports_lineb_readiness(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS_JSON", raising=False)

    status = AppFirstVersionFacade().module_status(ExternalModuleId.VOICE_PIPELINE)

    lines = {line["line_id"]: line for line in status.refs["lines"]}
    assert status.metrics["active_line_id"] == "line_a"
    assert lines["line_b"]["state"] == "blocked"
    assert lines["line_b"]["readiness"]["google_api_key"] == "blocked"
    assert lines["line_b"]["readiness"]["google_adc"] == "blocked"
    assert lines["line_b"]["voiceprint"]["state"] == "not_configured"
    assert lines["line_b"]["readiness"]["line_profile_id"] == "lineb_google_default"
    assert status.refs["line_profiles"]
    assert lines["line_a"]["echo"]["handling_mode"] == "headphones_recommended"


def test_line_profile_preview_explains_tts_voice_voiceprint_and_echo(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS_JSON", "{}")
    monkeypatch.delenv("GOOGLE_TTS_VOICE", raising=False)
    set_line_profile_loader_for_test(LineProfileLoader(search_paths=[tmp_path / "lines"]))

    preview = AppFirstVersionFacade().preview_line_profile(
        {
            "schema_version": 1,
            "kind": "line_profile",
            "line_profile_id": "lineb_missing_voice",
            "display_name": "LineB Missing Voice",
            "line_id": "line_b",
            "asr": {
                "asr_profile_id": "asr_ja",
                "provider": "google.STT",
                "model": "latest_long",
                "languages": ["ja-JP"],
            },
            "tts": {
                "tts_profile_id": "tts_blank",
                "provider": "google.TTS",
                "language": "ja-JP",
                "voice_name": "",
            },
            "voiceprint": {
                "voiceprint_profile_id": "vp_off",
                "enabled": False,
                "speaker_policy": "monitor_only",
            },
            "echo": {
                "echo_policy_id": "echo_speaker",
                "output_route": "speaker",
                "handling_mode": "monitor_only",
            },
        }
    )

    findings = {
        row["component_id"]: row for row in preview["device_check"]["findings"]
    }
    assert preview["device_check"]["state"] == "blocked"
    assert findings["tts"]["state"] == "blocked"
    assert findings["voiceprint"]["state"] == "not_configured"
    assert findings["echo"]["state"] == "high"


def test_lineb_missing_tts_voice_blocks_even_when_adc_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS_JSON", raising=False)
    monkeypatch.delenv("GOOGLE_TTS_VOICE", raising=False)
    payload = {
        "schema_version": 1,
        "kind": "line_profile",
        "line_profile_id": "lineb_missing_voice_no_adc",
        "display_name": "LineB Missing Voice No ADC",
        "line_id": "line_b",
        "asr": {"asr_profile_id": "asr_ja", "model": "latest_long", "languages": ["ja-JP"]},
        "tts": {"tts_profile_id": "tts_blank", "language": "ja-JP", "voice_name": ""},
        "voiceprint": {"voiceprint_profile_id": "vp_off", "enabled": False},
        "echo": {"echo_policy_id": "echo_headphones", "output_route": "headphones"},
    }
    bb = open_bb_client(name="test.lineb.missing_voice.seed", writer="brain.preset_loader")
    bb.set("global/active_line_id", "line_b")
    bb.set("global/active_line_profile_id", "lineb_missing_voice_no_adc")
    bb.set("global/active_line_profile", payload)

    preview = AppFirstVersionFacade().preview_line_profile(payload)
    status = AppFirstVersionFacade().module_status(ExternalModuleId.VOICE_PIPELINE)
    line_b = next(line for line in status.refs["lines"] if line["line_id"] == "line_b")
    findings = {
        row["component_id"]: row for row in preview["device_check"]["findings"]
    }

    assert preview["device_check"]["state"] == "blocked"
    assert findings["google_adc"]["state"] == "blocked"
    assert findings["tts"]["state"] == "blocked"
    assert status.state == "blocked"
    assert status.summary == "LineB selected TTS profile is missing a usable voice."
    assert line_b["readiness"]["tts"] == "blocked"


def test_apply_line_profile_updates_active_profile_and_audio_policy(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS_JSON", "{}")
    set_line_profile_loader_for_test(LineProfileLoader(search_paths=[tmp_path / "lines"]))
    facade = AppFirstVersionFacade()

    result = facade.apply_line_profile(
        {
            "schema_version": 1,
            "kind": "line_profile",
            "line_profile_id": "lineb_ner_voice",
            "display_name": "LineB Ner Voice",
            "line_id": "line_b",
            "asr": {"asr_profile_id": "asr_ner", "languages": ["ja-JP", "cmn-CN"]},
            "tts": {
                "tts_profile_id": "tts_ner",
                "language": "ja-JP",
                "voice_name": "ja-JP-Neural2-B",
            },
            "voiceprint": {
                "voiceprint_profile_id": "vp_monitor",
                "enabled": True,
                "speaker_policy": "monitor_then_gate",
                "speaker_state": "monitoring",
            },
            "echo": {
                "echo_policy_id": "echo_phone_speaker",
                "output_route": "phone_speaker",
                "handling_mode": "voiceprint_gate",
            },
        }
    )
    status = facade.module_status(ExternalModuleId.VOICE_PIPELINE)

    bb = open_bb_client(name="test.line_profile.read", writer=None)
    line_b = next(line for line in status.refs["lines"] if line["line_id"] == "line_b")
    assert result["success"] is True
    assert bb.get("global/active_line_profile_id") == "lineb_ner_voice"
    assert bb.get("global/active_tts_profile_id") == "tts_ner"
    assert status.metrics["active_line_id"] == "line_b"
    assert status.metrics["active_line_profile_id"] == "lineb_ner_voice"
    assert status.metrics["echo_handling_mode"] == "voiceprint_gate"
    assert status.metrics["voiceprint_state"] == "monitoring"
    assert line_b["readiness"]["tts_profile_id"] == "tts_ner"
    assert line_b["readiness"]["echo_risk"] == "medium"


def test_lineb_audio_route_policy_updates_voice_pipeline_status() -> None:
    bb = open_bb_client(name="test.lineb.seed", writer="brain.preset_loader")
    bb.set("global/active_line_id", "line_b")
    facade = AppFirstVersionFacade()

    policy = facade.set_lineb_audio_route_policy(
        input_route="phone_mic",
        output_route="phone_speaker",
        voiceprint_enabled=True,
        speaker_state="monitoring",
    )
    status = facade.module_status(ExternalModuleId.VOICE_PIPELINE)

    line_b = next(line for line in status.refs["lines"] if line["line_id"] == "line_b")
    assert policy["source"] == "app_facade"
    assert policy["voiceprint"]["state"] == "monitoring"
    assert policy["echo"]["risk_level"] == "medium"
    assert status.metrics["active_line_id"] == "line_b"
    assert status.metrics["echo_handling_mode"] == "voiceprint_gate"
    assert status.metrics["voiceprint_state"] == "monitoring"
    assert line_b["readiness"]["echo_risk"] == "medium"
    assert line_b["refs"]["audio_route_policy"]["output_route"] == "phone_speaker"


def test_lineb_tts_and_mic_decision_are_exposed() -> None:
    bb = open_bb_client(name="test.lineb.seed", writer="brain.preset_loader")
    bb.set("global/active_line_id", "line_b")
    facade = AppFirstVersionFacade()

    segment = facade.register_lineb_tts_segment(
        text_summary="GOSLO speaking",
        duration_s=2.0,
        started_at=100.0,
        tts_voice="ner_voice",
        voiceprint_hash="vp_agent",
    )
    decision = facade.classify_lineb_mic_input(
        observed_at=100.5,
        duration_s=0.3,
        asr_text="GOSLO speaking",
        voiceprint_hash="vp_agent",
    )
    status = facade.module_status(ExternalModuleId.VOICE_PIPELINE)
    line_b = next(line for line in status.refs["lines"] if line["line_id"] == "line_b")

    assert segment["segment_id"].startswith("tts_")
    assert decision["turn_decision"] == "agent_echo"
    assert decision["matched_segment_id"] == segment["segment_id"]
    assert status.metrics["recent_tts_segment_count"] == 1
    assert status.metrics["last_input_decision"] == "agent_echo"
    assert status.metrics["voice_activity_state"] == "agent_echo_suppressed"
    assert line_b["refs"]["last_input_decision"]["speaker_role"] == "agent"
    assert line_b["refs"]["voice_activity"]["recommended_model_trigger"] == (
        "lineb_echo_suppressed"
    )
    assert bb.get("session/lineb_voice_activity")["state"] == "agent_echo_suppressed"
    assert bb.get("session/lineb_recent_tts_segments")[0]["segment_id"] == segment["segment_id"]
    assert bb.get("transient/lineb_last_input_decision")["turn_decision"] == "agent_echo"


def test_lineb_user_turn_updates_voice_activity_for_unity_bridge() -> None:
    bb = open_bb_client(name="test.lineb.user_turn.seed", writer="brain.preset_loader")
    bb.set("global/active_line_id", "line_b")
    facade = AppFirstVersionFacade()

    decision = facade.classify_lineb_mic_input(
        observed_at=300.0,
        duration_s=0.5,
        asr_text="Ner mic test",
    )
    status = facade.module_status(ExternalModuleId.VOICE_PIPELINE)
    line_b = next(line for line in status.refs["lines"] if line["line_id"] == "line_b")

    assert decision["turn_decision"] == "user_turn"
    assert status.metrics["voice_activity_state"] == "listening"
    assert line_b["readiness"]["voice_activity_state"] == "listening"
    assert line_b["refs"]["voice_activity"]["model_reaction_policy"] == "listen_user_turn"
    assert bb.get("session/lineb_voice_activity")["recommended_model_trigger"] == (
        "lineb_listening"
    )


def test_lineb_high_echo_score_without_recent_tts_is_uncertain() -> None:
    bb = open_bb_client(name="test.lineb.high_echo.seed", writer="brain.preset_loader")
    bb.set("global/active_line_id", "line_b")
    facade = AppFirstVersionFacade()

    decision = facade.classify_lineb_mic_input(
        observed_at=500.0,
        duration_s=0.4,
        asr_text="possible speaker echo",
        echo_score=0.93,
    )
    status = facade.module_status(ExternalModuleId.VOICE_PIPELINE)
    line_b = next(line for line in status.refs["lines"] if line["line_id"] == "line_b")

    assert decision["turn_decision"] == "uncertain"
    assert decision["speaker_role"] == "uncertain"
    assert decision["reason"] == "high_echo_score_without_recent_tts"
    assert status.metrics["voice_activity_state"] == "listening_uncertain"
    assert line_b["refs"]["voice_activity"]["recommended_model_trigger"] == (
        "lineb_uncertain_input"
    )


def test_lineb_malformed_echo_score_does_not_break_mic_classification() -> None:
    bb = open_bb_client(name="test.lineb.bad_echo_score.seed", writer="brain.preset_loader")
    bb.set("global/active_line_id", "line_b")
    facade = AppFirstVersionFacade()

    decision = facade.classify_lineb_mic_input(
        observed_at=510.0,
        duration_s=0.4,
        asr_text="Ner mic test",
        echo_score="not-a-number",
    )
    status = facade.module_status(ExternalModuleId.VOICE_PIPELINE)

    assert decision["turn_decision"] == "user_turn"
    assert decision["echo_score"] == 0.0
    assert decision["reason"] == "no_recent_tts_overlap"
    assert status.metrics["voice_activity_state"] == "listening"

    nan_decision = facade.classify_lineb_mic_input(
        observed_at=511.0,
        duration_s=0.4,
        asr_text="Ner mic test again",
        echo_score="nan",
    )

    assert nan_decision["turn_decision"] == "user_turn"
    assert nan_decision["echo_score"] == 0.0


def test_room_setting_snapshot_exposes_five_axes(tmp_path: Path) -> None:
    set_preset_loader_for_test(PresetLoader(search_paths=[tmp_path / "presets"]))
    set_workspace_registry_for_test(WorkspaceRegistry(search_paths=[tmp_path / "workspaces"]))
    facade = AppFirstVersionFacade()

    snapshot = facade.room_setting_snapshot().as_json()

    assert snapshot["active_room"]["room_profile_id"] == "default"
    assert {line["line_id"] for line in snapshot["selectors"]["lines"]} == {
        "line_a",
        "line_b",
    }
    line_b = next(line for line in snapshot["selectors"]["lines"] if line["line_id"] == "line_b")
    assert "voiceprint" in line_b
    assert "echo" in line_b
    assert {mode["experience_mode"] for mode in snapshot["selectors"]["experience_modes"]} >= {
        "ar_companion",
        "2d_hall",
    }
    assert snapshot["selectors"]["models"][0]["model_id"] == "GOSLO_default"
    assert {model["model_id"] for model in snapshot["selectors"]["models"]} >= {
        "GOSLO_default",
        "ner_skin2",
    }
    assert snapshot["compatibility"]["state"] == "ready"


def test_room_profile_preview_enables_ner_and_disables_fly_to_hand(tmp_path: Path) -> None:
    set_preset_loader_for_test(PresetLoader(search_paths=[tmp_path / "presets"]))
    facade = AppFirstVersionFacade()

    preview = facade.preview_room_profile(
        {
            "schema_version": 3,
            "kind": "room_profile",
            "room_profile_id": "ner_unwired",
            "display_name": "Ner Unwired",
            "model_id": "ner_skin2",
            "persona_id": "goslo_parrot_default",
            "line_id": "line_a",
            "scene_profile_id": "ar_handheld",
            "experience_mode": "ar_companion",
            "workspace_id": "mansion_hub",
        }
    )

    decisions = preview["compatibility"]["decisions"]
    assert preview["compatibility"]["state"] == "degraded"
    assert any(
        d["capability_id"] == "model.available"
        and d["state"] == "enabled"
        and d["reason"] == "model_registered"
        for d in decisions
    )
    assert any(
        d["capability_id"] == "parrot.fly_to_hand"
        and d["state"] == "disabled"
        and d["reason"] == "selected_model_missing_fly_or_perch"
        for d in decisions
    )
    assert any(
        d["capability_id"] == "model.reflex.parrot_reserved"
        and d["state"] == "disabled"
        for d in decisions
    )
    assert any(
        d["capability_id"] == "model.capability.face_happy"
        and d["state"] == "enabled"
        for d in decisions
    )
    assert any(
        d["capability_id"] == "model.capability.touch_idle"
        and d["state"] == "enabled"
        for d in decisions
    )


def test_room_profile_preview_blocks_unknown_model(tmp_path: Path) -> None:
    set_preset_loader_for_test(PresetLoader(search_paths=[tmp_path / "presets"]))
    facade = AppFirstVersionFacade()

    preview = facade.preview_room_profile(
        {
            "schema_version": 3,
            "kind": "room_profile",
            "room_profile_id": "missing_model_room",
            "display_name": "Missing Model Room",
            "model_id": "missing_model",
            "persona_id": "goslo_parrot_default",
            "line_id": "line_a",
            "scene_profile_id": "ar_handheld",
            "experience_mode": "ar_companion",
            "workspace_id": "mansion_hub",
        }
    )

    decisions = preview["compatibility"]["decisions"]
    assert preview["compatibility"]["state"] == "blocked"
    assert any(
        d["capability_id"] == "model.available"
        and d["state"] == "blocked"
        and d["reason"] == "selected_model_not_registered"
        for d in decisions
    )


def test_new_room_profile_creates_unsaved_draft(tmp_path: Path) -> None:
    set_preset_loader_for_test(PresetLoader(search_paths=[tmp_path / "presets"]))
    facade = AppFirstVersionFacade()

    draft = facade.new_room_profile(display_name="Fresh Room")

    assert draft["room_profile"]["room_profile_id"].startswith("room_")
    assert draft["room_profile"]["display_name"] == "Fresh Room"
    assert draft["room_profile"]["model_id"] == "GOSLO_default"
    assert draft["compatibility"]["state"] == "ready"


def test_apply_room_profile_enforces_valid_profile_and_writes_keys(tmp_path: Path) -> None:
    set_preset_loader_for_test(PresetLoader(search_paths=[tmp_path / "presets"]))
    facade = AppFirstVersionFacade()
    profile = RoomProfile(
        room_profile_id="launch_room",
        display_name="Launch Room",
        line_id="line_a",
        scene_profile_id="ar_handheld",
        experience_mode="2d_hall",
        workspace_id="mansion_hub",
    )

    result = facade.apply_room_profile(profile.as_json())

    bb = open_bb_client(name="test.room_setting.read", writer=None)
    assert result["success"] is True
    assert "global/active_room_profile_id" in result["applied_keys"]
    assert bb.get("global/active_room_profile_id") == "launch_room"
    assert bb.get("global/active_experience_mode") == "2d_hall"
