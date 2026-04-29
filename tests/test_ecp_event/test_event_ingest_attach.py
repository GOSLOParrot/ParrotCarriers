"""Tests for `parrot.brain.event_ingest.attach_ecp_event_ingest` (Phase 4 W2 收口).

Focus:
    1. attach_ecp_event_ingest registers a `data_received` listener that
       routes only `parrot.ecp.event` topic packets through handle_raw.
    2. Foreign topic packets (e.g. parrot.telemetry) are not forwarded —
       coexistence with attach_telemetry_receiver is conflict-free.
    3. The singleton getter returns the same instance attach binds.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from parrot.brain.event_ingest import (
    attach_ecp_event_ingest,
    get_ecp_event_ingest,
    reset_ecp_event_ingest_for_tests,
)
from parrot.shared.ecp_event import (
    TOPIC_ECP_EVENT,
    EcpEvent,
    EcpEventSource,
    EcpEventType,
)


@pytest.fixture(autouse=True)
def _reset_singleton():
    reset_ecp_event_ingest_for_tests()
    yield
    reset_ecp_event_ingest_for_tests()


class _FakeRoom:
    """Minimal stand-in for livekit.rtc.Room — captures the registered
    `data_received` callback so tests can invoke it directly."""

    def __init__(self) -> None:
        self.data_callback = None

    def on(self, event_name: str):
        def decorator(fn):
            assert event_name == "data_received"
            self.data_callback = fn
            return fn
        return decorator


class _FakePacket:
    def __init__(self, data: bytes, topic: str) -> None:
        self.data = data
        self.topic = topic


def test_attach_returns_singleton_and_singleton_getter_matches():
    room = _FakeRoom()
    bound = attach_ecp_event_ingest(room)
    assert get_ecp_event_ingest() is bound


def test_attach_registers_data_received_listener():
    room = _FakeRoom()
    attach_ecp_event_ingest(room)
    assert callable(room.data_callback)


def test_inbound_ecp_event_packet_dispatched():
    room = _FakeRoom()
    ingest = attach_ecp_event_ingest(room)
    received = []
    ingest.subscribe(EcpEventType.SNAPSHOT_CAPTURED, received.append)

    src = EcpEvent.build(
        event_type=EcpEventType.SNAPSHOT_CAPTURED,
        source=EcpEventSource.UNITY,
        payload={"snapshot_uuid": "snap_attach_test"},
    )
    packet = _FakePacket(src.to_wire_json().encode("utf-8"), TOPIC_ECP_EVENT)

    room.data_callback(packet)

    assert len(received) == 1
    assert received[0].event_id == src.event_id


def test_inbound_foreign_topic_not_dispatched():
    """Coexistence with telemetry receiver: foreign topics must short-circuit
    before decode."""
    room = _FakeRoom()
    ingest = attach_ecp_event_ingest(room)
    received = []
    ingest.subscribe(None, received.append)  # wildcard

    # parrot.telemetry topic — belongs to attach_telemetry_receiver, not us.
    packet = _FakePacket(b'{"any":"shape"}', "parrot.telemetry")
    room.data_callback(packet)

    assert received == []


def test_inbound_str_data_coerced_to_bytes():
    """LiveKit Python SDK occasionally hands str instead of bytes; the
    attach wrapper must handle both."""
    room = _FakeRoom()
    ingest = attach_ecp_event_ingest(room)
    received = []
    ingest.subscribe(EcpEventType.BBOX_PLACED, received.append)

    src = EcpEvent.build(
        event_type=EcpEventType.BBOX_PLACED,
        source=EcpEventSource.UNITY,
        payload={"bbox_id": "bb_str"},
    )
    # Pass the wire JSON as str (not bytes) — same path Python SDK
    # sometimes takes for short payloads.
    packet = _FakePacket(src.to_wire_json(), TOPIC_ECP_EVENT)  # type: ignore[arg-type]
    room.data_callback(packet)

    assert len(received) == 1
