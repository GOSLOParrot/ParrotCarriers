"""Tests for `parrot.brain.event_ingest.EcpEventIngest` (Phase 4 L12 upstream).

Coverage focus:
    1. Schema validation: malformed JSON / wrong topic / unknown event_type
       counts increment the right counters and don't dispatch
    2. Dedup: replaying the same event_id within window dropped + counted
    3. Dedup window expiry: same event_id after window passes is accepted
    4. Subscriber dispatch (typed + wildcard) + subscriber error isolation
    5. 8KB payload cap enforcement on receive (defensive vs misbehaving Unity)
    6. event.rejected.oversize synthetic event is dispatched on cap violation
"""

from __future__ import annotations

import json

from parrot.brain.event_ingest import EcpEventIngest
from parrot.shared.ecp_event import (
    ECP_EVENT_PAYLOAD_LIMIT_BYTES,
    TOPIC_ECP_EVENT,
    EcpEvent,
    EcpEventSource,
    EcpEventType,
)


def _wire_bytes(event: EcpEvent) -> bytes:
    return event.to_wire_json().encode("utf-8")


# ─── happy path ────────────────────────────────────────────────────


def test_handle_raw_dispatches_to_typed_subscriber():
    ingest = EcpEventIngest()
    received: list[EcpEvent] = []
    ingest.subscribe(EcpEventType.SNAPSHOT_CAPTURED, received.append)

    src = EcpEvent.build(
        event_type=EcpEventType.SNAPSHOT_CAPTURED,
        source=EcpEventSource.UNITY,
        payload={"snapshot_uuid": "snap_1"},
    )
    out = ingest.handle_raw(TOPIC_ECP_EVENT, _wire_bytes(src))

    assert out is not None
    assert len(received) == 1
    assert received[0].event_id == src.event_id
    assert ingest.received_count == 1
    assert ingest.dispatched_count == 1
    assert ingest.dedup_dropped_count == 0


def test_wildcard_subscriber_sees_all_event_types():
    ingest = EcpEventIngest()
    seen_types: list[str] = []
    ingest.subscribe(None, lambda e: seen_types.append(str(e.event_type)))

    for et in (EcpEventType.SNAPSHOT_CAPTURED, EcpEventType.BBOX_PLACED, EcpEventType.FOCUS_ANCHORED):
        e = EcpEvent.build(event_type=et, source=EcpEventSource.UNITY, payload={})
        ingest.handle_raw(TOPIC_ECP_EVENT, _wire_bytes(e))

    assert seen_types == ["snapshot.captured", "bbox.placed", "focus.anchored"]


# ─── dedup ─────────────────────────────────────────────────────────


def test_duplicate_event_id_within_window_dropped():
    ingest = EcpEventIngest()
    received: list[EcpEvent] = []
    ingest.subscribe(EcpEventType.BBOX_PLACED, received.append)

    src = EcpEvent.build(
        event_type=EcpEventType.BBOX_PLACED,
        source=EcpEventSource.UNITY,
        payload={"bbox_id": "bb1"},
    )
    raw = _wire_bytes(src)

    first = ingest.handle_raw(TOPIC_ECP_EVENT, raw)
    second = ingest.handle_raw(TOPIC_ECP_EVENT, raw)
    third = ingest.handle_raw(TOPIC_ECP_EVENT, raw)

    assert first is not None
    assert second is None
    assert third is None
    assert len(received) == 1
    assert ingest.received_count == 3
    assert ingest.dedup_dropped_count == 2


def test_dedup_window_evicts_after_expiry():
    """Use a tiny window so the test runs in real time without sleeping seconds."""
    ingest = EcpEventIngest(dedup_window_s=0.05)

    src = EcpEvent.build(
        event_type=EcpEventType.FOCUS_ANCHORED,
        source=EcpEventSource.UNITY,
        payload={"focus_id": "f1"},
    )
    raw = _wire_bytes(src)

    assert ingest.handle_raw(TOPIC_ECP_EVENT, raw) is not None
    assert ingest.handle_raw(TOPIC_ECP_EVENT, raw) is None

    import time
    time.sleep(0.07)

    assert ingest.handle_raw(TOPIC_ECP_EVENT, raw) is not None
    assert ingest.received_count == 3
    assert ingest.dedup_dropped_count == 1


def test_dedup_capacity_evicts_oldest():
    """When window is generous but capacity is hit, oldest entries fall out."""
    ingest = EcpEventIngest(dedup_window_s=600, dedup_max_entries=3)

    events = [
        EcpEvent.build(
            event_type=EcpEventType.GESTURE_RECOGNIZED,
            source=EcpEventSource.UNITY,
            payload={"i": i},
        )
        for i in range(5)
    ]
    for e in events:
        ingest.handle_raw(TOPIC_ECP_EVENT, _wire_bytes(e))

    # Capacity is 3 — first two should have been evicted, replaying them is
    # not detected as duplicate.
    replay_first = ingest.handle_raw(TOPIC_ECP_EVENT, _wire_bytes(events[0]))
    replay_last = ingest.handle_raw(TOPIC_ECP_EVENT, _wire_bytes(events[4]))

    assert replay_first is not None  # evicted from window — accepted again
    assert replay_last is None  # still in window — dropped


# ─── transport-level rejection ────────────────────────────────────


def test_foreign_topic_silently_ignored():
    ingest = EcpEventIngest()
    received: list[EcpEvent] = []
    ingest.subscribe(None, received.append)

    src = EcpEvent.build(
        event_type=EcpEventType.SNAPSHOT_CAPTURED,
        source=EcpEventSource.UNITY,
        payload={},
    )
    out = ingest.handle_raw("parrot.ecp.state", _wire_bytes(src))

    assert out is None
    assert received == []
    assert ingest.dispatched_count == 0
    # received_count is still incremented because the transport delivered
    # something — only dispatch is gated by topic
    assert ingest.received_count == 1


def test_malformed_json_dropped():
    ingest = EcpEventIngest()
    out = ingest.handle_raw(TOPIC_ECP_EVENT, b"{not valid json")
    assert out is None
    assert ingest.malformed_dropped_count == 1


def test_invalid_schema_dropped():
    ingest = EcpEventIngest()
    out = ingest.handle_raw(
        TOPIC_ECP_EVENT,
        b'{"schema_version": 1, "event_type": "not.in.enum"}',
    )
    assert out is None
    assert ingest.malformed_dropped_count == 1


# ─── 8KB payload cap on receive ──────────────────────────────────


def test_oversize_payload_rejected_on_receive():
    """Defensive: even if a misbehaving Unity client sends > 8KB, Brain must
    reject and emit `event.rejected.oversize`."""
    ingest = EcpEventIngest()
    rejected_seen: list[EcpEvent] = []
    ingest.subscribe(EcpEventType.EVENT_REJECTED_OVERSIZE, rejected_seen.append)

    # Construct a wire JSON manually with a payload > 8KB. We bypass the
    # build factory's pre-check (which would refuse on Unity side).
    big_payload = {"blob": "x" * (ECP_EVENT_PAYLOAD_LIMIT_BYTES + 200)}
    encoded = json.dumps(big_payload, separators=(",", ":")).encode("utf-8")
    fake_event = {
        "schema_version": 1,
        "event_id": "evt_oversize_attempt_aaaa",
        "event_type": "photo.taken_preview",
        "created_at": 1700000000000,
        "source": "unity",
        "unity_identity": "unity-bad",
        "room_id": "test",
        "correlation_id": "",
        "payload_bytes": len(encoded),
        "payload": big_payload,
    }
    raw = json.dumps(fake_event, separators=(",", ":")).encode("utf-8")

    out = ingest.handle_raw(TOPIC_ECP_EVENT, raw)

    assert out is None
    assert ingest.oversize_dropped_count == 1
    assert len(rejected_seen) == 1
    rej = rejected_seen[0]
    assert rej.payload["rejected_event_id"] == "evt_oversize_attempt_aaaa"
    assert rej.payload["rejected_event_type"] == "photo.taken_preview"
    assert rej.payload["limit_bytes"] == ECP_EVENT_PAYLOAD_LIMIT_BYTES
    assert rej.correlation_id == "evt_oversize_attempt_aaaa"


# ─── subscriber error isolation ──────────────────────────────────


def test_subscriber_exception_does_not_poison_other_subscribers():
    ingest = EcpEventIngest()
    good_received: list[EcpEvent] = []

    def buggy(_e: EcpEvent) -> None:
        raise RuntimeError("intentional test failure")

    ingest.subscribe(EcpEventType.SNAPSHOT_CAPTURED, buggy)
    ingest.subscribe(EcpEventType.SNAPSHOT_CAPTURED, good_received.append)

    src = EcpEvent.build(
        event_type=EcpEventType.SNAPSHOT_CAPTURED,
        source=EcpEventSource.UNITY,
        payload={},
    )
    out = ingest.handle_raw(TOPIC_ECP_EVENT, _wire_bytes(src))

    assert out is not None
    assert len(good_received) == 1


# ─── metrics snapshot ────────────────────────────────────────────


def test_metrics_snapshot_keys_present():
    ingest = EcpEventIngest()
    snap = ingest.metrics_snapshot()
    assert set(snap.keys()) == {
        "received",
        "dispatched",
        "dedup_dropped",
        "oversize_dropped",
        "malformed_dropped",
        "dedup_window_size",
    }
