"""Tests for `parrot.brain.observer.sighting` Phase 4 W4-5 实质化.

Coverage focus:
    1. register() subscribes to BOTH SIGHTING_MATCHED and SIGHTING_UNMATCHED
    2. matched event triggers async fan-out (archiver + L2-B bump)
    3. unmatched event only logs/counts — no archiver, no L2-B writes
    4. matched event missing candidate_uuid is gracefully ignored (no crash)
    5. matched without running event loop falls back gracefully (no crash)
    6. metrics_snapshot reflects counts correctly
"""

from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest

from parrot.brain.event_ingest import (
    EcpEventIngest,
    reset_ecp_event_ingest_for_tests,
)
from parrot.brain.observer import sighting as sighting_observer
from parrot.shared.ecp_event import (
    EcpEvent,
    EcpEventSource,
    EcpEventType,
)


@pytest.fixture(autouse=True)
def _reset():
    reset_ecp_event_ingest_for_tests()
    sighting_observer.reset_metrics_for_tests()
    yield
    reset_ecp_event_ingest_for_tests()
    sighting_observer.reset_metrics_for_tests()


def _matched_event(**overrides) -> EcpEvent:
    payload = {
        "candidate_uuid": "uuid_test_42",
        "label": "blue ceramic mug",
        "description": "blue ceramic mug",
        "category": "container",
        "confidence": 0.83,
        "match_source": "l0_text",
        "snapshot_uuid": "snap_test",
        **overrides,
    }
    return EcpEvent.build(
        event_type=EcpEventType.SIGHTING_MATCHED,
        source=EcpEventSource.BRAIN,
        payload=payload,
        correlation_id=payload.get("snapshot_uuid", ""),
    )


def _unmatched_event(**overrides) -> EcpEvent:
    payload = {
        "description": "white mug",
        "category": "",
        "snapshot_uuid": "snap_unknown",
        "top_l2b_candidates": [{"uuid": "u1", "label": "blue cup", "score": 0.4}],
        "top_graphiti_candidates": [],
        **overrides,
    }
    return EcpEvent.build(
        event_type=EcpEventType.SIGHTING_UNMATCHED,
        source=EcpEventSource.BRAIN,
        payload=payload,
    )


# ─── registration ────────────────────────────────────────────────────


def test_register_subscribes_to_both_event_types():
    ingest = EcpEventIngest()
    sighting_observer.register(ingest)
    assert len(ingest._subs.get("sighting.matched", [])) == 1
    assert len(ingest._subs.get("sighting.unmatched", [])) == 1


# ─── matched: fan-out ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_matched_event_triggers_archiver_and_l2b_bump():
    ingest = EcpEventIngest()
    sighting_observer.register(ingest)

    archiver_called = False
    l2b_node_attention_before = 0.5

    class FakeNode:
        attention = 0.5

    fake_node = FakeNode()

    class FakeOutcome:
        observations = ["fake_obs"]

    class FakeFlt:
        def process_result(self, _data):
            return FakeOutcome()

    class FakeRunner:
        async def commit_outcome(self, _outcome):
            nonlocal archiver_called
            archiver_called = True

    class FakeGraph:
        def get_node(self, _u):
            return fake_node

    with (
        patch("parrot.dsg.ingest.tool_result_filter.ToolResultFilter", FakeFlt),
        patch("parrot.dsg.ingest.runner.get_ingest_runner", lambda: FakeRunner()),
        patch("parrot.dsg.l2b_graph.get_l2b_graph", lambda: FakeGraph()),
    ):
        ingest.handle_raw(
            "parrot.ecp.event",
            _matched_event().to_wire_json().encode("utf-8"),
        )
        # Yield control so the scheduled task can run.
        await asyncio.sleep(0.05)

    metrics = sighting_observer.get_metrics_snapshot()
    assert metrics["matched_received"] == 1
    assert metrics["archiver_attempts"] == 1
    assert archiver_called is True
    assert metrics["archiver_successes"] == 1
    assert metrics["l2b_attention_bumps"] == 1
    # Attention bumped from 0.5 to 0.55 (+0.05)
    assert fake_node.attention == pytest.approx(0.55)


@pytest.mark.asyncio
async def test_matched_event_missing_candidate_uuid_is_skipped():
    ingest = EcpEventIngest()
    sighting_observer.register(ingest)

    bad_event = _matched_event(candidate_uuid="")
    ingest.handle_raw("parrot.ecp.event", bad_event.to_wire_json().encode("utf-8"))
    await asyncio.sleep(0.01)

    metrics = sighting_observer.get_metrics_snapshot()
    assert metrics["matched_received"] == 1  # received, but not fanned out
    assert metrics["archiver_attempts"] == 0
    assert metrics["l2b_attention_bumps"] == 0


def test_matched_event_without_loop_falls_back_silently():
    """No running event loop = can't schedule async fan-out. Don't crash."""
    ingest = EcpEventIngest()
    sighting_observer.register(ingest)

    # Drive directly outside an asyncio loop (sync test function).
    ingest.handle_raw(
        "parrot.ecp.event",
        _matched_event().to_wire_json().encode("utf-8"),
    )

    metrics = sighting_observer.get_metrics_snapshot()
    assert metrics["matched_received"] == 1
    # No async work happened → archiver / L2-B counters stay at 0
    assert metrics["archiver_attempts"] == 0


# ─── unmatched: log + count only ────────────────────────────────────


def test_unmatched_event_only_increments_counter():
    ingest = EcpEventIngest()
    sighting_observer.register(ingest)

    ingest.handle_raw(
        "parrot.ecp.event",
        _unmatched_event().to_wire_json().encode("utf-8"),
    )

    metrics = sighting_observer.get_metrics_snapshot()
    assert metrics["unmatched_received"] == 1
    # NO archiver / L2-B activity — that's the point of "unknown is GOSLO's call"
    assert metrics["archiver_attempts"] == 0
    assert metrics["l2b_attention_bumps"] == 0


# ─── metrics shape ─────────────────────────────────────────────────


def test_metrics_snapshot_has_expected_keys():
    snap = sighting_observer.get_metrics_snapshot()
    assert set(snap.keys()) == {
        "matched_received",
        "unmatched_received",
        "archiver_attempts",
        "archiver_successes",
        "l2b_attention_bumps",
    }
