"""L1.5 Bucket — multi-source partition tags for the L2-B graph.

DSG-POOL-V1 § 2.2.

Buckets are the L1.5 management-plane grouping unit. They DO NOT own
node bytes; the node bodies live in ``parrot.dsg.l2b_graph``. A bucket
owns a set of UUIDs plus per-bucket policy (TTL, freeze, scene
preservation, etc.).

Naming (主设计稿 § 0.2): the term "Bucket" is L1.5-only.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class BucketKind(str, Enum):
    """Baseline desktop bucket set (DSG-POOL-V1 § 2.2).

    More buckets can be registered at runtime via
    ``L15Pool.register_bucket(BucketSpec(kind=...))`` — adding a
    BucketKind member is one option but not required (BucketSpec also
    accepts a free-form ``custom_kind: str`` for ad-hoc buckets).
    """

    MAIN = "main"
    OBSIDIAN_SETTING_DAILY = "obsidian_setting_daily"
    OBSIDIAN_SETTING_ROLEPLAY = "obsidian_setting_roleplay"
    GOOGLE_CALENDAR = "google_calendar"
    AUTONOMOUS_CURIOSITY = "autonomous_curiosity"
    ROLEPLAY_TEMP = "roleplay_temp"


@dataclass(frozen=True)
class BucketSpec:
    """Bucket definition. Frozen so spec is immutable after register."""

    kind: BucketKind
    is_authority: bool = False
    """Authority buckets are never overwritten by lower-priority sources;
    never auto-decay; never transition to GHOST. Default False."""

    default_ttl_seconds: float | None = None
    """``None`` = no expiry. Used by AUTONOMOUS_CURIOSITY (short TTL)."""

    preserved_across_scene_switch: bool = False
    """If True, a SceneSwitchTrigger does NOT clear this bucket."""

    cleared_on_scene_switch: bool = False
    """If True, a SceneSwitchTrigger CLEARs this bucket. Mutually
    exclusive with ``preserved_across_scene_switch``."""

    max_nodes: int | None = None
    """``None`` = no hard cap (desktop baseline)."""

    admission_policy_overrides: dict[str, Any] = field(default_factory=dict)


@dataclass
class BucketHandle:
    """Mutable runtime state of a registered bucket."""

    spec: BucketSpec
    node_uuids: set[str] = field(default_factory=set)
    frozen: bool = False
    created_at: float = field(default_factory=time.time)
    last_modified_at: float = field(default_factory=time.time)


class BucketOpKind(str, Enum):
    REGISTER = "register"
    IMPORT = "import"
    FREEZE = "freeze"
    UNFREEZE = "unfreeze"
    CLEAR = "clear"
    UNREGISTER = "unregister"


@dataclass(frozen=True)
class BucketOp:
    """Trigger → L1.5 Pool upload-channel payload (DSG-TRIGGER-V2 § 3.1)."""

    op: BucketOpKind
    kind: BucketKind
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BucketOpResult:
    op: BucketOp
    success: bool
    bucket_handle: BucketHandle | None = None
    affected_nodes: int = 0
    error: str = ""


class BucketRegistry:
    """In-memory registry of buckets. Owned by ``L15Pool``."""

    def __init__(self) -> None:
        self._buckets: dict[BucketKind, BucketHandle] = {}
        self._install_defaults()

    def _install_defaults(self) -> None:
        """Install desktop-baseline buckets at construction time."""
        defaults = [
            BucketSpec(
                kind=BucketKind.MAIN,
                is_authority=False,
                preserved_across_scene_switch=True,
            ),
            BucketSpec(
                kind=BucketKind.OBSIDIAN_SETTING_DAILY,
                is_authority=True,
                preserved_across_scene_switch=True,
            ),
            BucketSpec(
                kind=BucketKind.OBSIDIAN_SETTING_ROLEPLAY,
                is_authority=True,
                preserved_across_scene_switch=True,
            ),
            BucketSpec(
                kind=BucketKind.GOOGLE_CALENDAR,
                is_authority=False,
                cleared_on_scene_switch=True,
            ),
            BucketSpec(
                kind=BucketKind.AUTONOMOUS_CURIOSITY,
                is_authority=False,
                default_ttl_seconds=300.0,
                cleared_on_scene_switch=True,
            ),
        ]
        for spec in defaults:
            self.register(spec)

    def register(self, spec: BucketSpec) -> BucketHandle:
        """Idempotent: re-register with same kind returns existing handle."""
        existing = self._buckets.get(spec.kind)
        if existing is not None:
            return existing
        handle = BucketHandle(spec=spec)
        self._buckets[spec.kind] = handle
        return handle

    def get(self, kind: BucketKind) -> BucketHandle | None:
        return self._buckets.get(kind)

    def list(self, only_unfrozen: bool = False) -> list[BucketHandle]:
        if only_unfrozen:
            return [h for h in self._buckets.values() if not h.frozen]
        return list(self._buckets.values())

    def add_node(self, kind: BucketKind, node_uuid: str) -> bool:
        h = self._buckets.get(kind)
        if h is None or h.frozen:
            return False
        h.node_uuids.add(node_uuid)
        h.last_modified_at = time.time()
        return True

    def remove_node(self, kind: BucketKind, node_uuid: str) -> bool:
        h = self._buckets.get(kind)
        if h is None or h.frozen:
            return False
        if node_uuid in h.node_uuids:
            h.node_uuids.discard(node_uuid)
            h.last_modified_at = time.time()
            return True
        return False

    def freeze(self, kind: BucketKind) -> bool:
        h = self._buckets.get(kind)
        if h is None:
            return False
        h.frozen = True
        h.last_modified_at = time.time()
        return True

    def unfreeze(self, kind: BucketKind) -> bool:
        h = self._buckets.get(kind)
        if h is None:
            return False
        h.frozen = False
        h.last_modified_at = time.time()
        return True

    def clear(self, kind: BucketKind) -> set[str]:
        """Returns evicted node_uuids (caller must remove from L2BGraph)."""
        h = self._buckets.get(kind)
        if h is None:
            return set()
        evicted = set(h.node_uuids)
        h.node_uuids.clear()
        h.last_modified_at = time.time()
        return evicted

    def unregister(self, kind: BucketKind) -> bool:
        return self._buckets.pop(kind, None) is not None

    def find_bucket_of_node(self, node_uuid: str) -> BucketKind | None:
        for kind, h in self._buckets.items():
            if node_uuid in h.node_uuids:
                return kind
        return None


__all__ = [
    "BucketHandle",
    "BucketKind",
    "BucketOp",
    "BucketOpKind",
    "BucketOpResult",
    "BucketRegistry",
    "BucketSpec",
]
