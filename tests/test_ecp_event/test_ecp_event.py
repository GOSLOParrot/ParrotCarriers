"""Tests for `parrot.shared.ecp_event.EcpEvent` (Phase 4 wire envelope).

Coverage focus (entry doc §8.5 防漂移 #1-#5):
    1. event_id format / time-sortability
    2. Schema enforcement (forbid extras, reject free-string event_type / source)
    3. 8KB payload cap (build factory + raw construction)
    4. Topic constants are the locked values (not the §C-d typo `ecp.event.v1`)
    5. Wire JSON round-trip is stable byte-for-byte for fixed input
    6. Naming sanity — EcpEvent must not collide with event_log.EventEnvelope
"""

from __future__ import annotations

import json
import time

import pytest
from pydantic import ValidationError

from parrot.shared.ecp_event import (
    ECP_EVENT_PAYLOAD_LIMIT_BYTES,
    SCHEMA_VERSION,
    TOPIC_ECP_EVENT,
    TOPIC_ECP_STATE,
    TOPIC_ECP_TICK,
    EcpEvent,
    EcpEventSource,
    EcpEventType,
    generate_event_id,
)


# ─── identity / naming sanity ────────────────────────────────────────


def test_ecp_event_class_name_does_not_collide_with_event_log_envelope():
    """`event_log.EventEnvelope` is the L0 Sprint 0 internal envelope; this
    one is the Phase 4 wire envelope. Both are Pydantic; both are immutable.
    They MUST stay distinct (entry doc §8.0)."""
    from parrot.shared.event_log import EventEnvelope

    assert EcpEvent is not EventEnvelope
    assert EcpEvent.__name__ != EventEnvelope.__name__
    assert EcpEvent.__module__ != EventEnvelope.__module__


def test_topic_constants_match_locked_values():
    """§8.2 final table. If these change, entry doc §8.2 must change first."""
    assert TOPIC_ECP_EVENT == "parrot.ecp.event"
    assert TOPIC_ECP_STATE == "parrot.ecp.state"
    assert TOPIC_ECP_TICK == "parrot.ecp.tick"


def test_schema_version_starts_at_one():
    """§8.1 L2 lock. Bumping is a deliberate field-set change."""
    assert SCHEMA_VERSION == 1


def test_payload_limit_is_8kb():
    """§8.1 L3 lock."""
    assert ECP_EVENT_PAYLOAD_LIMIT_BYTES == 8 * 1024


# ─── event_id format ──────────────────────────────────────────────────


def test_generate_event_id_has_evt_prefix_and_time_sortable():
    a = generate_event_id()
    time.sleep(0.002)
    b = generate_event_id()

    assert a.startswith("evt_")
    assert b.startswith("evt_")
    assert a != b
    # Lexicographic order should match temporal order (12-char hex prefix
    # = ms epoch, monotonic increasing).
    assert a < b


def test_generate_event_id_format_is_evt_underscore_hex():
    eid = generate_event_id()
    parts = eid.split("_")
    assert parts[0] == "evt"
    assert len(parts) == 3
    assert len(parts[1]) == 12  # 12-char ms hex
    assert len(parts[2]) == 8  # 8-char rand hex
    int(parts[1], 16)  # raises if not hex
    int(parts[2], 16)


def test_event_id_validator_rejects_whitespace_and_commas():
    """Wire safety: event_id ends up in JSON + Redis Stream IDs."""
    for bad in ("evt_with space", "evt,comma", "evt\nnewline", "evt\0null"):
        with pytest.raises(ValidationError):
            EcpEvent(
                event_type=EcpEventType.SNAPSHOT_CAPTURED,
                source=EcpEventSource.UNITY,
                created_at=1,
                payload_bytes=2,
                event_id=bad,
            )


# ─── enum enforcement ─────────────────────────────────────────────────


def test_free_string_event_type_rejected():
    with pytest.raises(ValidationError):
        EcpEvent(
            event_type="snapshot.captured.NOT.IN.ENUM",  # type: ignore[arg-type]
            source=EcpEventSource.UNITY,
            created_at=1,
            payload_bytes=2,
        )


def test_free_string_source_rejected():
    with pytest.raises(ValidationError):
        EcpEvent(
            event_type=EcpEventType.SNAPSHOT_CAPTURED,
            source="malicious_actor",  # type: ignore[arg-type]
            created_at=1,
            payload_bytes=2,
        )


def test_extra_fields_rejected():
    with pytest.raises(ValidationError):
        EcpEvent(
            event_type=EcpEventType.SNAPSHOT_CAPTURED,
            source=EcpEventSource.UNITY,
            created_at=1,
            payload_bytes=2,
            new_field_someone_added="oops",  # type: ignore[call-arg]
        )


def test_event_is_frozen():
    e = EcpEvent.build(
        event_type=EcpEventType.SNAPSHOT_CAPTURED,
        source=EcpEventSource.UNITY,
        payload={"x": 1},
    )
    with pytest.raises(ValidationError):
        e.event_id = "evt_changed_in_place"  # type: ignore[misc]


# ─── 8KB payload cap ──────────────────────────────────────────────────


def test_build_rejects_payload_over_8kb():
    big = {"blob": "x" * (ECP_EVENT_PAYLOAD_LIMIT_BYTES + 100)}
    with pytest.raises(ValueError) as exc:
        EcpEvent.build(
            event_type=EcpEventType.PHOTO_TAKEN_PREVIEW,
            source=EcpEventSource.UNITY,
            payload=big,
        )
    assert "8KB" in str(exc.value)


def test_build_accepts_payload_at_cap():
    # Build a payload that JSON-encodes to exactly close to (but under) 8KB.
    # Reserve ~50 bytes for the JSON object framing + key.
    blob = "x" * (ECP_EVENT_PAYLOAD_LIMIT_BYTES - 50)
    e = EcpEvent.build(
        event_type=EcpEventType.PHOTO_TAKEN_PREVIEW,
        source=EcpEventSource.UNITY,
        payload={"blob": blob},
    )
    assert e.payload_bytes <= ECP_EVENT_PAYLOAD_LIMIT_BYTES


def test_build_computes_payload_bytes_from_compact_json():
    """payload_bytes must match the on-wire encoded size, with compact
    separators (no spaces). Otherwise consumers re-encoding for size checks
    will see drift."""
    e = EcpEvent.build(
        event_type=EcpEventType.SNAPSHOT_CAPTURED,
        source=EcpEventSource.UNITY,
        payload={"a": 1, "b": "two"},
    )
    expected = json.dumps({"a": 1, "b": "two"}, separators=(",", ":")).encode("utf-8")
    assert e.payload_bytes == len(expected)


# ─── wire JSON round-trip ──────────────────────────────────────────────


def test_wire_json_round_trip_via_pydantic():
    """The wire JSON must deserialize back to an equal EcpEvent via Pydantic
    (this is what Brain's event_ingest does on receive)."""
    src = EcpEvent.build(
        event_type=EcpEventType.BBOX_PLACED,
        source=EcpEventSource.UNITY,
        payload={"bbox_id": "bb1", "corners": [[0.0, 0.0], [1.0, 1.0]]},
        unity_identity="unity-arspike-test",
        room_id="parrot-dev",
        correlation_id="corr_xyz",
    )
    wire = src.to_wire_json()
    parsed = EcpEvent.model_validate_json(wire)

    assert parsed.event_id == src.event_id
    assert parsed.event_type == src.event_type
    assert parsed.source == src.source
    assert parsed.created_at == src.created_at
    assert parsed.unity_identity == src.unity_identity
    assert parsed.room_id == src.room_id
    assert parsed.correlation_id == src.correlation_id
    assert parsed.payload == src.payload
    assert parsed.payload_bytes == src.payload_bytes


def test_wire_json_uses_enum_values_not_repr():
    """Cross-language requires plain strings on the wire (Unity's JsonUtility
    can't grok Python enum reprs)."""
    e = EcpEvent.build(
        event_type=EcpEventType.SIGHTING_MATCHED,
        source=EcpEventSource.BRAIN,
        payload={},
    )
    wire = json.loads(e.to_wire_json())
    assert wire["event_type"] == "sighting.matched"
    assert wire["source"] == "brain"


def test_wire_json_preserves_all_required_fields():
    """All 9 required wire fields must be present (entry doc §8.1 L2)."""
    e = EcpEvent.build(
        event_type=EcpEventType.ATTENTION_THRESHOLD_CROSSED,
        source=EcpEventSource.BRAIN,
        payload={"weight": 1.2},
    )
    wire = json.loads(e.to_wire_json())
    expected_fields = {
        "schema_version",
        "event_id",
        "event_type",
        "created_at",
        "source",
        "unity_identity",
        "room_id",
        "correlation_id",
        "payload_bytes",
        "payload",
    }
    assert set(wire.keys()) == expected_fields


# ─── event_type registry coverage ─────────────────────────────────────


def test_event_type_registry_matches_entry_doc_8_3():
    """Entry doc §8.3 starter set must equal EcpEventType members.

    Update both atomically: changing one without the other = silent drift
    across the protocol/code boundary."""
    expected = {
        "snapshot.captured",
        "sighting.matched",
        "sighting.unmatched",
        "bbox.placed",
        "bbox.removed",
        "focus.anchored",
        "focus.released",
        "attention.threshold.crossed",
        "attention.config.echo",  # Phase 4 W6-7 F-05 fix (Unity B chat)
        "photo.taken_preview",
        "photo.asset_uploaded",
        "gesture.recognized",
        "event.rejected.oversize",
    }
    actual = {member.value for member in EcpEventType}
    assert actual == expected, (
        f"EcpEventType drift from entry doc §8.3:\n"
        f"  added in code:    {actual - expected}\n"
        f"  removed in code:  {expected - actual}"
    )
