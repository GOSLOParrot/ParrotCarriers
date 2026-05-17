"""ECP gesture observer for XRHand state mirrored into Brain context.

Unity owns the real-time hand tracking and perch reflex. Brain only needs a
small, transient awareness hint so the next turn can avoid saying something
that contradicts the user's gesture or the bird's body state.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from parrot.brain.event_ingest import EcpEventIngest
from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.ecp_event import EcpEvent, EcpEventType


logger = logging.getLogger(__name__)

_WRITER = "brain.observer.gesture"
_BB_KEY = "transient/hand_gesture"

_metrics: dict[str, int] = {
    "recognized_received": 0,
    "bb_writes": 0,
    "missing_gesture": 0,
    "bb_write_failures": 0,
}


def get_metrics_snapshot() -> dict[str, int]:
    return dict(_metrics)


def reset_metrics_for_tests() -> None:
    for key in _metrics:
        _metrics[key] = 0


def _vec(value: Any) -> dict[str, float]:
    if not isinstance(value, dict):
        return {"x": 0.0, "y": 0.0, "z": 0.0}
    return {
        "x": float(value.get("x", 0.0) or 0.0),
        "y": float(value.get("y", 0.0) or 0.0),
        "z": float(value.get("z", 0.0) or 0.0),
    }


def _on_gesture_recognized(event: EcpEvent) -> None:
    _metrics["recognized_received"] += 1
    payload = event.payload or {}
    gesture = str(payload.get("gesture", "") or "")
    if not gesture:
        _metrics["missing_gesture"] += 1
        return

    bb_payload = {
        "kind": gesture,
        "detected": bool(payload.get("hand_detected", False)),
        "confidence": float(payload.get("confidence", 0.0) or 0.0),
        "source": str(payload.get("source", "") or ""),
        "event_id": event.event_id,
        "correlation_id": event.correlation_id,
        "since": (event.created_at / 1000.0) if event.created_at else time.time(),
        "hand_pose": {
            "index_perch": _vec(payload.get("index_perch")),
            "index_direction": _vec(payload.get("index_direction")),
        },
    }

    try:
        bb = open_bb_client(name="observer_gesture", writer=_WRITER)
        bb.set(_BB_KEY, bb_payload)
        _metrics["bb_writes"] += 1
    except Exception:
        _metrics["bb_write_failures"] += 1
        logger.debug("[observer.gesture] BB write failed", exc_info=True)


def register(ingest: EcpEventIngest) -> None:
    ingest.subscribe(EcpEventType.GESTURE_RECOGNIZED, _on_gesture_recognized)


__all__ = ["get_metrics_snapshot", "register", "reset_metrics_for_tests"]
