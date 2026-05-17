from __future__ import annotations

from parrot.shared.config import GEMINI_LIVE_VOICE_DEFAULT, GeminiConfig


def test_linea_live_voice_defaults_to_locked_goslo_voice(monkeypatch):
    monkeypatch.delenv("GEMINI_LIVE_VOICE", raising=False)

    assert GEMINI_LIVE_VOICE_DEFAULT == "Aoede"
    assert GeminiConfig().live_voice == "Aoede"


def test_linea_live_voice_normalizes_supported_env_value(monkeypatch):
    monkeypatch.setenv("GEMINI_LIVE_VOICE", "leda")

    assert GeminiConfig().live_voice == "Leda"


def test_linea_live_voice_unknown_env_falls_back_to_locked_default(monkeypatch):
    monkeypatch.setenv("GEMINI_LIVE_VOICE", "not-a-live-voice")

    assert GeminiConfig().live_voice == "Aoede"
