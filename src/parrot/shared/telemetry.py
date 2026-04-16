"""DataChannel telemetry message definitions.

Unity→Python (Lossy, 10Hz):
    TelemetryFrame — pose + timestamp + behavior_state

Python→Unity (Reliable, event-driven):
    Reserved for P2 body_cmd / head_cmd / state_sync.

Wire format: JSON over LiveKit DataChannel.
Size budget: ≤1300 bytes per Lossy frame (LiveKit MTU).
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Vec3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass
class Quat:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 1.0


@dataclass
class Pose:
    position: Vec3 = field(default_factory=Vec3)
    rotation: Quat = field(default_factory=Quat)


@dataclass
class TelemetryFrame:
    """Unity→Python telemetry (Lossy DataChannel, 10Hz).

    Fields:
        pose: parrot world-space pose (position + rotation)
        timestamp: Unix epoch seconds (float)
        behavior_state: current Unity Animator body state (e.g. "idle", "flying")
        anim_clip: currently playing animation clip name
    """

    pose: Pose = field(default_factory=Pose)
    timestamp: float = field(default_factory=time.time)
    behavior_state: str = "idle"
    anim_clip: str = "idle"

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, raw: str | bytes) -> TelemetryFrame:
        data = json.loads(raw)
        pose_data = data.get("pose", {})
        pos = Vec3(**pose_data.get("position", {}))
        rot = Quat(**pose_data.get("rotation", {}))
        return cls(
            pose=Pose(position=pos, rotation=rot),
            timestamp=data.get("timestamp", 0.0),
            behavior_state=data.get("behavior_state", "idle"),
            anim_clip=data.get("anim_clip", "idle"),
        )


@dataclass
class TelemetryEvent:
    """Unity→Python event (Reliable DataChannel, event-driven).

    Used for discrete events like arrival, gesture detection, animation completion.
    """

    type: str = "unknown"
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, raw: str | bytes) -> TelemetryEvent:
        data = json.loads(raw)
        return cls(
            type=data.get("type", "unknown"),
            payload=data.get("payload", {}),
            timestamp=data.get("timestamp", 0.0),
        )


DATACHANNEL_TOPIC_TELEMETRY = "parrot.telemetry"
DATACHANNEL_TOPIC_EVENT = "parrot.event"
DATACHANNEL_TOPIC_COMMAND = "parrot.command"
