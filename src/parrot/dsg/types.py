"""DSG data types — L1 events, triggers, and object representations.

These are practical types for P2 simulation + real DSG later.
Not strictly following Opus 17 naming — adapted to what's actually needed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TriggerType(str, Enum):
    """Types of scene change triggers DSG can emit."""
    NEW = "new"
    MISSING = "missing"
    DISPLACED = "displaced"


@dataclass
class ObjectInfo:
    """A detected or expected object in the scene."""
    object_id: str
    label: str
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    confidence: float = 1.0
    surface: str = ""
    zone: str = ""
    graphiti_uuid: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class L1DetectionResult:
    """Output of L1 vision pipeline (or simulation script).

    This represents what L1 *found*, not how it found it.
    """
    objects: list[ObjectInfo] = field(default_factory=list)
    surfaces: list[str] = field(default_factory=list)
    zone: str = ""
    timestamp: float = 0.0


@dataclass
class SceneTrigger:
    """A scene change event to be pushed to Context Injector / Brain."""
    trigger_type: TriggerType
    object_info: ObjectInfo
    description: str = ""
    timestamp: float = 0.0
