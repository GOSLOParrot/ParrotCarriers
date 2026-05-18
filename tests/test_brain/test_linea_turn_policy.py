from __future__ import annotations

from parrot.brain.linea_turn_policy import (
    build_linea_realtime_input_config,
    linea_barge_in_enabled,
    linea_turn_policy_status,
)


def test_linea_barge_in_is_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("PARROT_LINEA_BARGE_IN_ENABLED", raising=False)

    status = linea_turn_policy_status()

    assert linea_barge_in_enabled() is False
    assert status["policy"] == "one_question_one_answer"
    assert status["activity_handling"] == "NO_INTERRUPTION"

    config = build_linea_realtime_input_config()
    assert config is not None
    assert str(config.activity_handling) == "ActivityHandling.NO_INTERRUPTION"


def test_linea_barge_in_can_be_explicitly_enabled(monkeypatch) -> None:
    monkeypatch.setenv("PARROT_LINEA_BARGE_IN_ENABLED", "1")

    status = linea_turn_policy_status()

    assert linea_barge_in_enabled() is True
    assert status["policy"] == "low_latency_overlap"
    assert status["activity_handling"] == "START_OF_ACTIVITY_INTERRUPTS"
    assert build_linea_realtime_input_config() is None
