"""DataChannel telemetry receiver — Unity→Python pose/state/hand data.

P1.5: registers the callback and logs received frames.
P2.5: parses hand gesture events, tracks hand state for Scheduler/PerchOnHand.

Attach to a LiveKit Room via `attach_telemetry_receiver(room)`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from parrot.shared.telemetry import (
    DATACHANNEL_TOPIC_EVENT,
    DATACHANNEL_TOPIC_TELEMETRY,
    TelemetryEvent,
    TelemetryFrame,
    Vec3,
)

if TYPE_CHECKING:
    from livekit.rtc import DataPacket, Room

logger = logging.getLogger(__name__)

_latest_frame: TelemetryFrame | None = None


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
