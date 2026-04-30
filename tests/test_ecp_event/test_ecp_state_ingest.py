"""Tests for `parrot.brain.ecp_state_ingest` — GAP-1 fix (Sprint4 Phase 4).

Coverage:
    1. attach_ecp_state_ingest subscribes to room data_received
    2. Valid parrot.ecp.state packet writes BB session/ecp_state
    3. Foreign topic (parrot.telemetry) is silently ignored; BB not touched
    4. Malformed JSON is skipped without crash; parse_failures counter bumps
    5. metrics_snapshot returns all expected keys
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any
from unittest.mock import MagicMock

import pytest

from parrot.brain import ecp_state_ingest
from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.ecp_event import TOPIC_ECP_STATE

_BB_WRITER = "brain._rpc_bridge"
_BB_KEY = "session/ecp_state"


# ── helpers ──────────────────────────────────────────────────────────────────

@dataclass
class FakeDataPacket:
    """Minimal stand-in for livekit.rtc.DataPacket used in callbacks."""
    data: bytes | str
    topic: str = TOPIC_ECP_STATE


class FakeRoom:
    """Minimal mock of livekit.rtc.Room that records @room.on handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, list] = {}

    def on(self, event_name: str):
        """Decorator that captures the handler function."""
        def decorator(fn):
            self._handlers.setdefault(event_name, []).append(fn)
            return fn
        return decorator

    def emit(self, event_name: str, packet: FakeDataPacket) -> None:
        """Invoke all registered handlers for the given event."""
        for fn in self._handlers.get(event_name, []):
            fn(packet)


def _make_ecp_state_bytes(**kwargs: Any) -> bytes:
    """Build a minimal EcpStateDto JSON payload, optionally overriding fields."""
    payload = {
        "schema_version": "ecp.v2.alpha",
        "ts": 1234567890.0,
        "sequence_id": 1,
        "unity_identity": "unity_test",
        "room_id": "room_test",
        "body_state": "idle",
        "head_state": "HEAD_FORWARD",
        "cognitive_state": "",
        "active_command_id": "",
        "queued_command_ids": [],
        "active_locks": [],
        "last_ack_id": "",
        "video_tier": "",
        "app_lifecycle_state": "Connected",
        "ar_tracking_state": "",
    }
    payload.update(kwargs)
    return json.dumps(payload).encode("utf-8")


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _reset():
    ecp_state_ingest.reset_metrics_for_tests()
    yield
    ecp_state_ingest.reset_metrics_for_tests()
    # Clear BB session/ecp_state so other tests that expect None are not
    # contaminated (py-trees BB is a global in-process singleton; there is
    # no delete API — setting to None restores the "no producer" observable).
    try:
        _cleanup_bb = open_bb_client(name="test_cleanup_ecp_state", writer=_BB_WRITER)
        _cleanup_bb.set(_BB_KEY, None)
    except Exception:
        pass


# ── tests ─────────────────────────────────────────────────────────────────────

class TestAttachSubscribesToDataReceived:
    """attach_ecp_state_ingest registers a data_received handler on the room."""

    def test_registers_data_received_handler(self):
        room = FakeRoom()
        ecp_state_ingest.attach_ecp_state_ingest(room)
        assert "data_received" in room._handlers
        assert len(room._handlers["data_received"]) >= 1


class TestValidPacketWritesBB:
    """A valid parrot.ecp.state packet writes session/ecp_state to BB."""

    def test_writes_session_ecp_state(self):
        room = FakeRoom()
        ecp_state_ingest.attach_ecp_state_ingest(room)

        packet = FakeDataPacket(
            data=_make_ecp_state_bytes(
                body_state="perched_on_hand",
                head_state="HEAD_TILT",
                active_command_id="cmd_abc",
                active_locks=["fly_to"],
            )
        )
        room.emit("data_received", packet)

        # Read back from BB — use reader client (no writer restriction)
        bb = open_bb_client(name="test_reader_ecp_state")
        state: dict = bb.get("session/ecp_state")
        assert isinstance(state, dict)
        assert state["body_state"] == "perched_on_hand"
        assert state["head_state"] == "HEAD_TILT"
        assert state["active_command_id"] == "cmd_abc"
        assert state["active_locks"] == ["fly_to"]

    def test_dispatched_count_increments(self):
        room = FakeRoom()
        ecp_state_ingest.attach_ecp_state_ingest(room)

        packet = FakeDataPacket(data=_make_ecp_state_bytes())
        room.emit("data_received", packet)

        snap = ecp_state_ingest.get_metrics_snapshot()
        assert snap["received_count"] == 1
        assert snap["dispatched_count"] == 1
        assert snap["parse_failures"] == 0

    def test_sequence_overwrite(self):
        """Second packet overwrites the first — last-write-wins semantics."""
        room = FakeRoom()
        ecp_state_ingest.attach_ecp_state_ingest(room)

        room.emit("data_received", FakeDataPacket(
            data=_make_ecp_state_bytes(sequence_id=1, body_state="idle")))
        room.emit("data_received", FakeDataPacket(
            data=_make_ecp_state_bytes(sequence_id=2, body_state="flying")))

        bb = open_bb_client(name="test_reader_overwrite")
        state = bb.get("session/ecp_state")
        assert state["body_state"] == "flying"
        assert state["sequence_id"] == 2

        snap = ecp_state_ingest.get_metrics_snapshot()
        assert snap["dispatched_count"] == 2


class TestForeignTopicSilentlyIgnored:
    """Packets on other topics (parrot.telemetry etc.) are ignored."""

    def test_foreign_topic_does_not_write_bb(self):
        room = FakeRoom()
        ecp_state_ingest.attach_ecp_state_ingest(room)

        # Send valid JSON on a foreign topic
        foreign_packet = FakeDataPacket(
            data=json.dumps({"body_state": "dancing"}).encode(),
            topic="parrot.telemetry",
        )
        room.emit("data_received", foreign_packet)

        snap = ecp_state_ingest.get_metrics_snapshot()
        # foreign_topic_ignored counter should bump, dispatched should stay 0
        assert snap["foreign_topic_ignored"] >= 1
        assert snap["dispatched_count"] == 0


class TestMalformedJsonSkippedNoCrash:
    """Malformed JSON is silently dropped; parse_failures counter bumps."""

    def test_invalid_json(self):
        room = FakeRoom()
        ecp_state_ingest.attach_ecp_state_ingest(room)

        bad_packet = FakeDataPacket(data=b"not valid json {{{{")
        room.emit("data_received", bad_packet)  # must not raise

        snap = ecp_state_ingest.get_metrics_snapshot()
        assert snap["parse_failures"] >= 1
        assert snap["dispatched_count"] == 0

    def test_non_dict_json_skipped(self):
        room = FakeRoom()
        ecp_state_ingest.attach_ecp_state_ingest(room)

        bad_packet = FakeDataPacket(data=b'"just_a_string"')
        room.emit("data_received", bad_packet)

        snap = ecp_state_ingest.get_metrics_snapshot()
        assert snap["parse_failures"] >= 1

    def test_schema_version_mismatch_is_skipped(self):
        """schema_version mismatch → packet is dropped, BB not written.
        Prevents silently storing an incompatible schema into session/ecp_state.
        When Unity bumps the version, _EXPECTED_SCHEMA_VERSION must be updated here."""
        room = FakeRoom()
        ecp_state_ingest.attach_ecp_state_ingest(room)

        packet = FakeDataPacket(
            data=_make_ecp_state_bytes(schema_version="ecp.v99.future"))
        room.emit("data_received", packet)

        snap = ecp_state_ingest.get_metrics_snapshot()
        assert snap["schema_version_mismatch"] == 1
        # Must NOT dispatch — incompatible schema should not reach BB
        assert snap["dispatched_count"] == 0


class TestMetricsSnapshotKeys:
    """get_metrics_snapshot returns all expected keys."""

    def test_all_expected_keys_present(self):
        snap = ecp_state_ingest.get_metrics_snapshot()
        expected = {
            "received_count",
            "dispatched_count",
            "parse_failures",
            "schema_version_mismatch",
            "bb_write_failures",
            "foreign_topic_ignored",
        }
        assert expected.issubset(snap.keys()), (
            f"Missing keys: {expected - snap.keys()}"
        )

    def test_initial_all_zeros(self):
        snap = ecp_state_ingest.get_metrics_snapshot()
        for v in snap.values():
            assert v == 0
