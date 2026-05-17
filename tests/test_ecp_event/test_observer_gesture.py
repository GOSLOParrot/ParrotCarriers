from __future__ import annotations

import py_trees

from parrot.brain.event_ingest import EcpEventIngest
from parrot.brain.observer import gesture as gesture_observer
from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.ecp_event import EcpEvent, EcpEventSource, EcpEventType, TOPIC_ECP_EVENT


def setup_function() -> None:
    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    gesture_observer.reset_metrics_for_tests()


def test_gesture_recognized_updates_transient_hand_gesture() -> None:
    ingest = EcpEventIngest()
    gesture_observer.register(ingest)

    event = EcpEvent.build(
        event_type=EcpEventType.GESTURE_RECOGNIZED,
        source=EcpEventSource.UNITY,
        payload={
            "gesture": "index_finger_branch",
            "hand_detected": True,
            "source": "xr_hands",
            "confidence": 0.82,
            "index_perch": {"x": 1, "y": 2, "z": 3},
            "index_direction": {"x": 0, "y": 0, "z": 1},
        },
        correlation_id="cmd_perch",
    )

    assert ingest.handle_raw(TOPIC_ECP_EVENT, event.to_wire_json().encode("utf-8")) is not None

    bb = open_bb_client(name="test.gesture.read", writer=None)
    value = bb.get("transient/hand_gesture")
    assert value["kind"] == "index_finger_branch"
    assert value["detected"] is True
    assert value["confidence"] == 0.82
    assert value["hand_pose"]["index_perch"] == {"x": 1.0, "y": 2.0, "z": 3.0}
    assert gesture_observer.get_metrics_snapshot()["bb_writes"] == 1
