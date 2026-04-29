"""Tests for `parrot.brain.event_publisher.EcpEventPublisher` (Phase 4 W2 收口).

Coverage focus:
    1. publish() returns True on success and False when no room / no
       local_participant.
    2. publish() invokes room.local_participant.publish_data with the
       reliable + topic + wire-shape contract.
    3. publish_nowait() schedules on the running loop; fails gracefully
       outside a loop.
    4. make_brain_event() pins source=brain and pulls room_id from the
       held room.
    5. Counters update on success / failure / no-room paths.
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from parrot.brain.event_publisher import (
    EcpEventPublisher,
    attach_ecp_event_publisher,
    get_ecp_event_publisher,
    reset_ecp_event_publisher_for_tests,
)
from parrot.shared.ecp_event import (
    TOPIC_ECP_EVENT,
    EcpEvent,
    EcpEventSource,
    EcpEventType,
)


def _fake_room(name: str = "test-room") -> MagicMock:
    """Mock LiveKit Room with an async publish_data method."""
    room = MagicMock()
    room.name = name
    room.local_participant = MagicMock()
    room.local_participant.publish_data = AsyncMock(return_value=None)
    return room


@pytest.fixture(autouse=True)
def _reset_singleton():
    reset_ecp_event_publisher_for_tests()
    yield
    reset_ecp_event_publisher_for_tests()


# ─── publish() happy path ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_publish_success_calls_publish_data_with_correct_args():
    room = _fake_room("parrot-dev")
    pub = EcpEventPublisher(room)
    event = pub.make_brain_event(
        event_type=EcpEventType.SIGHTING_MATCHED,
        payload={"candidate_uuid": "obj_42", "score": 0.83},
    )

    ok = await pub.publish(event)

    assert ok is True
    assert pub.published_count == 1
    assert pub.failed_count == 0
    room.local_participant.publish_data.assert_awaited_once()
    call_kwargs = room.local_participant.publish_data.await_args.kwargs
    assert call_kwargs["topic"] == TOPIC_ECP_EVENT
    assert call_kwargs["reliable"] is True
    # Payload is a string (UTF-8 wire JSON); verify shape, not exact bytes.
    payload_str = call_kwargs["payload"]
    assert isinstance(payload_str, str)
    assert '"event_type":"sighting.matched"' in payload_str
    assert '"source":"brain"' in payload_str


# ─── publish() failure paths ───────────────────────────────────────


@pytest.mark.asyncio
async def test_publish_no_room_returns_false_and_increments_counter():
    pub = EcpEventPublisher(None)  # type: ignore[arg-type]
    event = EcpEvent.build(
        event_type=EcpEventType.SIGHTING_UNMATCHED,
        source=EcpEventSource.BRAIN,
        payload={},
    )
    ok = await pub.publish(event)
    assert ok is False
    assert pub.dropped_no_room_count == 1


@pytest.mark.asyncio
async def test_publish_transport_failure_returns_false():
    room = _fake_room()
    room.local_participant.publish_data = AsyncMock(side_effect=RuntimeError("boom"))
    pub = EcpEventPublisher(room)
    event = pub.make_brain_event(
        event_type=EcpEventType.ATTENTION_THRESHOLD_CROSSED,
        payload={"weight": 1.0},
    )

    ok = await pub.publish(event)

    assert ok is False
    assert pub.failed_count == 1
    assert pub.published_count == 0


# ─── publish_nowait ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_publish_nowait_schedules_and_completes():
    room = _fake_room()
    pub = EcpEventPublisher(room)
    event = pub.make_brain_event(
        event_type=EcpEventType.SIGHTING_MATCHED,
        payload={},
    )

    pub.publish_nowait(event)
    # Yield to let the scheduled coroutine run.
    await asyncio.sleep(0.01)
    assert pub.published_count == 1


def test_publish_nowait_outside_loop_drops_and_logs():
    """No running loop = no schedulable target. Counter increments on
    failed_count so this path is observable."""
    pub = EcpEventPublisher(_fake_room())
    event = EcpEvent.build(
        event_type=EcpEventType.SIGHTING_UNMATCHED,
        source=EcpEventSource.BRAIN,
        payload={},
    )
    pub.publish_nowait(event)
    assert pub.failed_count == 1
    assert pub.published_count == 0


# ─── make_brain_event ──────────────────────────────────────────────


def test_make_brain_event_pins_source_and_pulls_room_id():
    pub = EcpEventPublisher(_fake_room("parrot-dev"))
    event = pub.make_brain_event(
        event_type=EcpEventType.PHOTO_ASSET_UPLOADED,
        payload={"photo_id": "p1"},
    )
    assert event.source == "brain"
    assert event.room_id == "parrot-dev"


def test_make_brain_event_room_id_override_takes_precedence():
    pub = EcpEventPublisher(_fake_room("default-room"))
    event = pub.make_brain_event(
        event_type=EcpEventType.SIGHTING_MATCHED,
        payload={},
        room_id="explicit-room",
    )
    assert event.room_id == "explicit-room"


# ─── singleton attach ──────────────────────────────────────────────


def test_attach_replaces_singleton():
    room1 = _fake_room("a")
    room2 = _fake_room("b")
    pub1 = attach_ecp_event_publisher(room1)
    assert get_ecp_event_publisher() is pub1
    pub2 = attach_ecp_event_publisher(room2)
    assert get_ecp_event_publisher() is pub2
    assert pub1 is not pub2


def test_get_publisher_before_attach_returns_none():
    assert get_ecp_event_publisher() is None


# ─── metrics snapshot ──────────────────────────────────────────────


def test_metrics_snapshot_keys():
    pub = EcpEventPublisher(_fake_room())
    snap = pub.metrics_snapshot()
    assert set(snap.keys()) == {"published", "failed", "dropped_no_room"}
