"""Tests for `parrot.brain.attention_config_handler` (Phase 4 W6-7 F-05 Echo).

Coverage focus:
    1. register() subscribes to ATTENTION_CONFIG_ECHO
    2. Valid Echo payload writes BB global/attention_thresholds with all
       5 locked fields
    3. Missing required fields are rejected + counter increments
    4. Non-numeric values are rejected
    5. threshold ≤ 0 is rejected (defensive even though Unity SO clamps)
    6. Wrong schema_version is rejected (forward-compat: future Unity
       payload v2 must NOT be silently truncated)
    7. Reconnect re-publish (§B.6) — multiple Echos overwrite BB,
       writer attribution stays "brain._rpc_bridge" per bb_schema lock
"""

from __future__ import annotations

import pytest

from parrot.brain import attention_config_handler
from parrot.brain.event_ingest import (
    EcpEventIngest,
    reset_ecp_event_ingest_for_tests,
)
from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.ecp_event import (
    EcpEvent,
    EcpEventSource,
    EcpEventType,
)


@pytest.fixture(autouse=True)
def _reset():
    reset_ecp_event_ingest_for_tests()
    attention_config_handler.reset_metrics_for_tests()
    # Best-effort BB key cleanup: open_bb_client.unset is not part of the
    # public API in test fixtures, so we just overwrite with a sentinel
    # here and assert the handler-written value below. Tests that care
    # about the absent state assert via metrics.
    yield
    reset_ecp_event_ingest_for_tests()
    attention_config_handler.reset_metrics_for_tests()


def _echo_event(payload: dict) -> bytes:
    """Build an Echo EcpEvent and return wire bytes for handle_raw."""
    e = EcpEvent.build(
        event_type=EcpEventType.ATTENTION_CONFIG_ECHO,
        source=EcpEventSource.UNITY,
        payload=payload,
    )
    return e.to_wire_json().encode("utf-8")


def _default_payload() -> dict:
    """Locked starter values from entry doc §8.1 L9."""
    return {
        "delta_focus": 0.2,
        "delta_bbox": 1.0,
        "threshold": 1.0,
        "target_ttl_s": 30.0,
        "schema_version": 1,
    }


# ─── registration ────────────────────────────────────────────────────


def test_register_subscribes_to_attention_config_echo():
    ingest = EcpEventIngest()
    attention_config_handler.register(ingest)
    subs = ingest._subs.get("attention.config.echo", [])
    assert len(subs) == 1


# ─── happy path ──────────────────────────────────────────────────────


def test_valid_echo_writes_bb_with_all_5_fields():
    ingest = EcpEventIngest()
    attention_config_handler.register(ingest)

    ingest.handle_raw("parrot.ecp.event", _echo_event(_default_payload()))

    bb = open_bb_client(name="test_reader_attn_cfg", writer="test")
    written = bb.get("global/attention_thresholds")
    assert written is not None
    assert written == {
        "delta_focus": 0.2,
        "delta_bbox": 1.0,
        "threshold": 1.0,
        "target_ttl_s": 30.0,
        "schema_version": 1,
    }

    metrics = attention_config_handler.get_metrics_snapshot()
    assert metrics["received"] == 1
    assert metrics["bb_writes"] == 1


def test_non_default_values_persist_to_bb():
    """Verify Unity SO override (e.g. user tunes thresholds in Inspector)
    propagates verbatim to BB."""
    ingest = EcpEventIngest()
    attention_config_handler.register(ingest)

    payload = {
        "delta_focus": 0.35,
        "delta_bbox": 0.8,
        "threshold": 1.5,
        "target_ttl_s": 60.0,
        "schema_version": 1,
    }
    ingest.handle_raw("parrot.ecp.event", _echo_event(payload))

    bb = open_bb_client(name="test_reader_tuned", writer="test")
    written = bb.get("global/attention_thresholds")
    assert written["delta_focus"] == pytest.approx(0.35)
    assert written["delta_bbox"] == pytest.approx(0.8)
    assert written["threshold"] == pytest.approx(1.5)
    assert written["target_ttl_s"] == pytest.approx(60.0)


# ─── reject paths ────────────────────────────────────────────────────


def test_missing_required_field_rejected():
    ingest = EcpEventIngest()
    attention_config_handler.register(ingest)

    bad = _default_payload()
    del bad["delta_bbox"]
    ingest.handle_raw("parrot.ecp.event", _echo_event(bad))

    metrics = attention_config_handler.get_metrics_snapshot()
    assert metrics["received"] == 1
    assert metrics["rejected_invalid"] == 1
    assert metrics["bb_writes"] == 0


def test_non_numeric_value_rejected():
    ingest = EcpEventIngest()
    attention_config_handler.register(ingest)

    bad = _default_payload()
    bad["delta_focus"] = "not_a_number"
    ingest.handle_raw("parrot.ecp.event", _echo_event(bad))

    metrics = attention_config_handler.get_metrics_snapshot()
    assert metrics["received"] == 1
    assert metrics["rejected_invalid"] == 1
    assert metrics["bb_writes"] == 0


def test_zero_threshold_rejected():
    """Defensive: Unity SO clamps but Brain MUST also reject."""
    ingest = EcpEventIngest()
    attention_config_handler.register(ingest)

    bad = _default_payload()
    bad["threshold"] = 0.0
    ingest.handle_raw("parrot.ecp.event", _echo_event(bad))

    metrics = attention_config_handler.get_metrics_snapshot()
    assert metrics["rejected_invalid"] == 1
    assert metrics["bb_writes"] == 0


def test_wrong_schema_version_rejected():
    """Forward-compat: a future Unity build sending v2 must NOT have its
    payload silently accepted as v1 (would truncate fields)."""
    ingest = EcpEventIngest()
    attention_config_handler.register(ingest)

    bad = _default_payload()
    bad["schema_version"] = 2
    ingest.handle_raw("parrot.ecp.event", _echo_event(bad))

    metrics = attention_config_handler.get_metrics_snapshot()
    assert metrics["rejected_schema_version"] == 1
    assert metrics["bb_writes"] == 0


# ─── §B.6 reconnect re-publish ──────────────────────────────────────


def test_reconnect_repeated_echo_overwrites_bb():
    """Reconnect / Brain pipeline switch (§B.6) re-publishes the SO. BB
    should reflect the latest values, not accumulate or stale-out.
    """
    ingest = EcpEventIngest()
    attention_config_handler.register(ingest)

    # First Echo on initial connect
    ingest.handle_raw("parrot.ecp.event", _echo_event(_default_payload()))

    # User tunes Inspector during reconnect window, then reconnects
    tuned = {
        "delta_focus": 0.5,
        "delta_bbox": 1.2,
        "threshold": 2.0,
        "target_ttl_s": 45.0,
        "schema_version": 1,
    }
    ingest.handle_raw("parrot.ecp.event", _echo_event(tuned))

    bb = open_bb_client(name="test_reader_reconnect", writer="test")
    written = bb.get("global/attention_thresholds")
    assert written["delta_focus"] == pytest.approx(0.5)
    assert written["threshold"] == pytest.approx(2.0)

    metrics = attention_config_handler.get_metrics_snapshot()
    assert metrics["received"] == 2
    assert metrics["bb_writes"] == 2


# ─── writer attribution (bb_schema.py lock) ─────────────────────────


def test_writer_string_matches_bb_schema_declared_producer():
    """``bb_schema.py:global/attention_thresholds`` declares producer =
    ``brain._rpc_bridge``. The handler MUST use that string so the
    declared contract is honoured even though the physical write happens
    in ``attention_config_handler.py``.
    """
    # Sanity: the constant in the handler is what we expect
    assert attention_config_handler._BB_WRITER == "brain._rpc_bridge"

    # And the BB key string is the one bb_schema declares
    assert attention_config_handler._BB_KEY == "global/attention_thresholds"
