"""DataChannel telemetry receiver — Unity→Python pose/state/hand data.

Sprint 1 S1.A3: receiver now owns three BB_KEYS (writer="brain.telemetry_receiver"):

    tick/body_state         ← TelemetryFrame.behavior_state
    tick/ar_tracking_state  ← TelemetryEvent type="ar_tracking_state"
    transient/hand_gesture  ← TelemetryEvent type="hand_gesture"

`tick/head_state` is also declared with this module as writer but no Unity
emitter exists yet (head-pose tracking lands in Sprint 2); the key stays
"declared but unwritten" until then. Readers must guard with try/except
KeyError on `.get()`.

Attach to a LiveKit Room via `attach_telemetry_receiver(room)`.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.parrot_actions import ParrotBodyState
from parrot.shared.telemetry import (
    DATACHANNEL_TOPIC_EVENT,
    DATACHANNEL_TOPIC_TELEMETRY,
    TelemetryEvent,
    TelemetryFrame,
    Vec3,
)

if TYPE_CHECKING:
    import py_trees
    from livekit.rtc import DataPacket, Room

logger = logging.getLogger(__name__)

_WRITER = "brain.telemetry_receiver"

_latest_frame: TelemetryFrame | None = None
_bb: "py_trees.blackboard.Client | None" = None


@dataclass
class HandState:
    """Latest known hand tracking state from XRHandTracker."""
    detected: bool = False
    gesture: str = "none"
    palm_position: Vec3 = field(default_factory=Vec3)
    index_tip_position: Vec3 = field(default_factory=Vec3)
    timestamp: float = 0.0


_hand_state = HandState()


def get_latest_telemetry() -> TelemetryFrame | None:
    """Return the most recently received telemetry frame (or None)."""
    return _latest_frame


def get_hand_state() -> HandState:
    """Return the latest hand tracking state."""
    return _hand_state


def _ensure_bb() -> "py_trees.blackboard.Client":
    """Lazy-open the module's BB client on first use."""
    global _bb
    if _bb is None:
        _bb = open_bb_client(name="telemetry_receiver", writer=_WRITER)
    return _bb


def _write_body_state(raw: str) -> None:
    """Mirror Unity behavior_state → tick/body_state as a ParrotBodyState enum."""
    try:
        body = ParrotBodyState(raw)
    except ValueError:
        logger.debug("Unknown behavior_state '%s', coercing to IDLE", raw)
        body = ParrotBodyState.IDLE

    bb = _ensure_bb()
    try:
        current = bb.get("tick/body_state")
    except KeyError:
        current = None
    if current != body:
        bb.set("tick/body_state", body)
        logger.debug("BB tick/body_state: %s → %s", current, body)


def _write_hand_gesture() -> None:
    """Mirror HandState → transient/hand_gesture as {kind, hand_pose, since}."""
    bb = _ensure_bb()
    payload: dict[str, Any] = {
        "kind": _hand_state.gesture,
        "hand_pose": {
            "palm": {
                "x": _hand_state.palm_position.x,
                "y": _hand_state.palm_position.y,
                "z": _hand_state.palm_position.z,
            },
            "index_tip": {
                "x": _hand_state.index_tip_position.x,
                "y": _hand_state.index_tip_position.y,
                "z": _hand_state.index_tip_position.z,
            },
        },
        "detected": _hand_state.detected,
        "since": _hand_state.timestamp or time.time(),
    }
    bb.set("transient/hand_gesture", payload)


def _write_ar_tracking_state(state: str) -> None:
    """Mirror Unity AR session state → tick/ar_tracking_state."""
    bb = _ensure_bb()
    try:
        current = bb.get("tick/ar_tracking_state")
    except KeyError:
        current = None
    if current != state:
        bb.set("tick/ar_tracking_state", state)
        logger.info("BB tick/ar_tracking_state: %s → %s", current, state)


def _parse_hand_event(payload: dict[str, Any]) -> None:
    """Update hand state from a hand_gesture telemetry event."""
    _hand_state.detected = payload.get("hand_detected", False)
    _hand_state.gesture = payload.get("gesture", "none")

    palm = payload.get("palm_position", {})
    _hand_state.palm_position = Vec3(
        x=palm.get("x", 0.0), y=palm.get("y", 0.0), z=palm.get("z", 0.0),
    )
    idx = payload.get("index_tip_position", {})
    _hand_state.index_tip_position = Vec3(
        x=idx.get("x", 0.0), y=idx.get("y", 0.0), z=idx.get("z", 0.0),
    )
    _hand_state.timestamp = payload.get("timestamp", 0.0)


def attach_telemetry_receiver(room: Room) -> None:
    """Register DataChannel receive callbacks on the given LiveKit Room.

    Call this after room.connect() or inside the rtc_session handler.
    """
    _ensure_bb()

    @room.on("data_received")
    def _on_data(packet: DataPacket) -> None:
        global _latest_frame
        topic = getattr(packet, "topic", "") or ""
        raw = packet.data if isinstance(packet.data, (str, bytes)) else ""
        if not raw:
            return

        try:
            if topic == DATACHANNEL_TOPIC_TELEMETRY:
                frame = TelemetryFrame.from_json(raw)
                _latest_frame = frame
                _write_body_state(frame.behavior_state)
                logger.debug(
                    "Telemetry: pos=(%.2f,%.2f,%.2f) state=%s",
                    frame.pose.position.x,
                    frame.pose.position.y,
                    frame.pose.position.z,
                    frame.behavior_state,
                )
            elif topic == DATACHANNEL_TOPIC_EVENT:
                event = TelemetryEvent.from_json(raw)

                if event.type == "hand_gesture":
                    _parse_hand_event(event.payload)
                    _write_hand_gesture()
                    if _hand_state.gesture != "none":
                        logger.info(
                            "Hand: gesture=%s palm=(%.2f,%.2f,%.2f)",
                            _hand_state.gesture,
                            _hand_state.palm_position.x,
                            _hand_state.palm_position.y,
                            _hand_state.palm_position.z,
                        )
                elif event.type == "perch_state":
                    state = event.payload.get("state", "UNKNOWN")
                    logger.info("Perch state: %s", state)
                elif event.type == "ar_tracking_state":
                    state = event.payload.get("state", "UNKNOWN")
                    _write_ar_tracking_state(state)
                else:
                    logger.info(
                        "TelemetryEvent: type=%s payload=%s",
                        event.type, event.payload,
                    )
            else:
                logger.debug("DataChannel data on unknown topic '%s'", topic)
        except Exception:
            logger.exception("Error parsing DataChannel data (topic=%s)", topic)

    logger.info(
        "Telemetry receiver attached — listening on topics: %s, %s",
        DATACHANNEL_TOPIC_TELEMETRY, DATACHANNEL_TOPIC_EVENT,
    )
