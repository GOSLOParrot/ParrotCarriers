from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Callable

import py_trees
import pytest

from parrot.brain import telemetry_receiver
from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.telemetry import DATACHANNEL_TOPIC_EVENT, TelemetryEvent


class FakeRoom:
    def __init__(self) -> None:
        self.handlers: dict[str, Callable[[object], None]] = {}

    def on(
        self,
        event_name: str,
    ) -> Callable[[Callable[[object], None]], Callable[[object], None]]:
        def _decorator(callback: Callable[[object], None]) -> Callable[[object], None]:
            self.handlers[event_name] = callback
            return callback

        return _decorator


def setup_function() -> None:
    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    telemetry_receiver._bb = None
    telemetry_receiver._latest_frame = None
    telemetry_receiver._hand_state = telemetry_receiver.HandState()


def test_legacy_hand_gesture_does_not_write_observer_owned_blackboard(
    caplog: pytest.LogCaptureFixture,
) -> None:
    room = FakeRoom()
    telemetry_receiver.attach_telemetry_receiver(room)  # type: ignore[arg-type]

    event = TelemetryEvent(
        type="hand_gesture",
        payload={
            "hand_detected": True,
            "gesture": "index_finger_branch",
            "palm_position": {"x": 1.0, "y": 2.0, "z": 3.0},
            "index_tip_position": {"x": 4.0, "y": 5.0, "z": 6.0},
            "timestamp": 123.0,
        },
    )
    packet = SimpleNamespace(topic=DATACHANNEL_TOPIC_EVENT, data=event.to_json())

    with caplog.at_level(logging.ERROR, logger="parrot.brain.telemetry_receiver"):
        room.handlers["data_received"](packet)

    assert "Error parsing DataChannel data" not in caplog.text
    assert telemetry_receiver.get_hand_state().gesture == "index_finger_branch"

    bb = open_bb_client(name="test.legacy_hand.read", writer=None)
    with pytest.raises(KeyError):
        bb.get("transient/hand_gesture")
