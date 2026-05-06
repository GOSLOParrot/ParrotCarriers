"""L1.5 SceneRegistry — SceneType + SceneProfile management.

DSG-SCENE-V1.

SceneType (preset env type) is **orthogonal** to:
    - LocationTag  (physical place; just a label, Node field)
    - Episode      (Gemini conversation segment, existing)
    - IntentEvent  (cognitive boundary, see DSG-INTENT-EVENT-V1)
    - NanobotTask  (async dispatch unit, existing)

A SceneSwitch primarily affects the L1.5 management plane (freeze
authority buckets / clear fresh buckets / switch CV Flow params /
switch DsgMode). It does NOT drive L2-B topology — IntentEvent does
that.

Desktop baseline ships a single SceneType=DESKTOP profile. Other
SceneTypes (HOME_INDOOR / OUTDOOR / LIBRARY / KITCHEN) are P3
extensions; the registration interface is in place now.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from parrot.dsg.l1_5.buckets import BucketKind
from parrot.shared.tiers import DsgMode, VideoTier


class SceneType(str, Enum):
    """Preset scene categories. Desktop baseline only ships DESKTOP."""

    DESKTOP = "desktop"
    HOME_INDOOR = "home_indoor"
    OUTDOOR = "outdoor"
    LIBRARY = "library"
    KITCHEN = "kitchen"
    OTHER = "other"


@dataclass(frozen=True)
class SceneProfile:
    """Per-SceneType configuration. Frozen so each profile is immutable."""

    scene_type: SceneType

    dsg_mode: DsgMode
    video_tier_hint: VideoTier
    cv_flow_params: dict[str, Any] = field(default_factory=dict)

    preserved_bucket_kinds: frozenset = field(default_factory=frozenset)
    fresh_bucket_kinds: frozenset = field(default_factory=frozenset)

    priority_overrides: dict[str, int] = field(default_factory=dict)
    """Source-priority overrides keyed by ``ObservationSource.value``."""

    location_default: str = ""


DESKTOP_PROFILE: SceneProfile = SceneProfile(
    scene_type=SceneType.DESKTOP,
    dsg_mode=DsgMode.DSG_GEMINI_VISION,
    video_tier_hint=VideoTier.VIDEO_GEMINI_ONLY,
    cv_flow_params={"enabled": False},
    preserved_bucket_kinds=frozenset({
        BucketKind.OBSIDIAN_SETTING_DAILY,
        BucketKind.OBSIDIAN_SETTING_ROLEPLAY,
        BucketKind.MAIN,
    }),
    fresh_bucket_kinds=frozenset({
        BucketKind.GOOGLE_CALENDAR,
        BucketKind.AUTONOMOUS_CURIOSITY,
    }),
    location_default="desk",
)


@dataclass(frozen=True)
class SceneSwitchOutcome:
    old_scene_type: SceneType
    new_scene_type: SceneType
    switched_at: float

    preserved_buckets: tuple = ()
    cleared_buckets: tuple = ()
    affected_node_count: int = 0

    dsg_mode_change: tuple[DsgMode, DsgMode] | None = None
    video_tier_change: tuple[VideoTier, VideoTier] | None = None

    old_snapshot_path: Path | None = None

    success: bool = True
    errors: tuple[str, ...] = ()


class SceneRegistry:
    """SceneType ↔ SceneProfile registry + current-Scene tracking."""

    def __init__(self) -> None:
        # TODO(P3-multi-scene): SKELETON. Only DESKTOP profile is
        #   pre-registered. P3 (multi-Scene + sensors + VPS chat) must
        #   add HOME_INDOOR / OUTDOOR / LIBRARY / KITCHEN profiles via
        #   ``self.register(SceneProfile(...))``. Each profile defines:
        #     - dsg_mode (DsgMode enum)
        #     - video_tier_hint (VideoTier enum)
        #     - cv_flow_params (A10 model + threshold dict)
        #     - preserved/fresh_bucket_kinds (which buckets cross / clear)
        #     - priority_overrides (per-scene source priority tweaks)
        #     - location_default (default LocationTag for new nodes)
        #   See DSG-SCENE-V1 § 1.1 + § 8 for the full P3 list.
        self._profiles: dict[SceneType, SceneProfile] = {
            SceneType.DESKTOP: DESKTOP_PROFILE,
        }
        self._current: SceneType = SceneType.DESKTOP
        self._switched_at: float = time.time()

    def register(self, profile: SceneProfile) -> None:
        """Idempotent — re-register with same scene_type overwrites profile."""
        self._profiles[profile.scene_type] = profile

    def get(self, scene_type: SceneType) -> SceneProfile | None:
        return self._profiles.get(scene_type)

    def current_profile(self) -> SceneProfile:
        return self._profiles[self._current]

    def current_scene_type(self) -> SceneType:
        return self._current

    def set_current(self, scene_type: SceneType) -> None:
        if scene_type not in self._profiles:
            raise KeyError(f"SceneType {scene_type!r} not registered")
        self._current = scene_type
        self._switched_at = time.time()

    def time_in_current_scene(self) -> float:
        return time.time() - self._switched_at


__all__ = [
    "DESKTOP_PROFILE",
    "SceneProfile",
    "SceneRegistry",
    "SceneSwitchOutcome",
    "SceneType",
]
