from __future__ import annotations

import json

from parrot.brain.lineb_voiceprint import (
    decision_payload_for_similarity,
    runtime_status,
    verify_embedding,
)
from parrot.brain.line_profile import (
    LineProfile,
    LineProfileLoader,
    TtsProfile,
    VoiceprintProfile,
    evaluate_line_profile,
)


def test_voiceprint_embedding_verifies_owner_rejects_other_and_marks_uncertain(tmp_path) -> None:
    manifest = tmp_path / "voiceprint.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_id": "owner_test",
                "model": {"provider": "external"},
                "enrollment": {"centroid": [1.0, 0.0]},
                "thresholds": {
                    "accept_similarity": 0.8,
                    "reject_similarity": 0.4,
                },
            }
        ),
        encoding="utf-8",
    )
    env = {
        "PARROT_LINEB_VOICEPRINT_ENABLED": "1",
        "PARROT_LINEB_VOICEPRINT_MANIFEST": str(manifest),
    }

    status = runtime_status(env=env)
    owner = verify_embedding([1.0, 0.0], env=env)
    other = verify_embedding([0.0, 1.0], env=env)
    uncertain = verify_embedding([0.7, 0.7], env=env)

    assert status.state == "ready"
    assert owner.decision == "owner_user"
    assert owner.speaker_role == "user"
    assert owner.similarity == 1.0
    assert other.decision == "other_speaker"
    assert other.speaker_role == "other"
    assert uncertain.decision == "uncertain"
    assert uncertain.speaker_role == "uncertain"


def test_voiceprint_status_reports_pending_configuration() -> None:
    status = runtime_status(env={"PARROT_LINEB_VOICEPRINT_ENABLED": "1"})

    assert status.state == "not_configured"
    assert status.health == "warning"
    assert "MANIFEST" in status.summary


def test_voiceprint_similarity_without_manifest_is_not_trusted() -> None:
    decision = decision_payload_for_similarity(
        0.99,
        env={"PARROT_LINEB_VOICEPRINT_ENABLED": "1"},
    )

    assert decision["decision"] == "not_configured"
    assert decision["speaker_role"] == "unknown"


def test_line_profile_voiceprint_runtime_uses_profile_provider_and_thresholds(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "test")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS_JSON", "{}")
    monkeypatch.delenv("PARROT_LINEB_VOICEPRINT_ENABLED", raising=False)
    monkeypatch.delenv("PARROT_LINEB_VOICEPRINT_PROVIDER", raising=False)
    monkeypatch.delenv("PARROT_LINEB_VOICEPRINT_MANIFEST", raising=False)
    manifest = tmp_path / "voiceprint.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_id": "owner_profile_from_line",
                "enrollment": {"centroid": [1.0, 0.0, 0.0]},
            }
        ),
        encoding="utf-8",
    )
    profile = LineProfile(
        line_profile_id="lineb_profile_provider",
        display_name="LineB Profile Provider",
        line_id="line_b",
        tts=TtsProfile(language="ja-JP", voice_name="ja-JP-Neural2-B"),
        voiceprint=VoiceprintProfile(
            voiceprint_profile_id="owner_profile_from_line",
            enabled=True,
            provider="external",
            manifest_path=str(manifest),
            threshold_accept=0.73,
            threshold_reject=0.41,
        ),
    )

    check = evaluate_line_profile(profile).as_json()
    voiceprint = next(
        row for row in check["findings"] if row["component_id"] == "voiceprint"
    )

    assert voiceprint["state"] == "ready"
    assert voiceprint["refs"]["runtime"]["provider"] == "external"
    assert voiceprint["refs"]["runtime"]["threshold_accept"] == 0.73
    assert voiceprint["refs"]["runtime"]["threshold_reject"] == 0.41


def test_voiceprint_similarity_can_use_profile_config_without_env_enable(tmp_path) -> None:
    manifest = tmp_path / "voiceprint.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_id": "owner_profile_menu_only",
                "model": {"provider": "external"},
                "enrollment": {"centroid": [1.0, 0.0]},
                "thresholds": {"accept_similarity": 0.75, "reject_similarity": 0.4},
            }
        ),
        encoding="utf-8",
    )

    decision = decision_payload_for_similarity(
        0.9,
        env={},
        enabled=True,
        manifest_path=manifest,
        provider="external",
        profile_id="owner_profile_menu_only",
    )

    assert decision["decision"] == "owner_user"
    assert decision["speaker_role"] == "user"


def test_active_line_profile_accepts_room_setting_env_name(
    monkeypatch,
    tmp_path,
) -> None:
    profile_dir = tmp_path / "lines"
    profile_dir.mkdir()
    (profile_dir / "lineb_ner_ja_test.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "kind": "line_profile",
                "line_profile_id": "lineb_ner_ja_test",
                "display_name": "LineB Ner Japanese Test",
                "line_id": "line_b",
                "tts": {"language": "ja-JP", "voice_name": "ja-JP-Neural2-B"},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("PARROT_LINE_PROFILE", raising=False)
    monkeypatch.setenv("PARROT_ACTIVE_LINE_PROFILE_ID", "lineb_ner_ja_test")

    loader = LineProfileLoader(search_paths=[profile_dir])

    assert loader.active_profile_id() == "lineb_ner_ja_test"
    assert loader.active_profile().line_id == "line_b"
