"""L1.5 RefTable — lightweight UUID / pointer binding registry.

DSG-POOL-V1 § 2.3.

RefTable is the **lightweight** layer of the dual-layer Ref design:
    - This module: O(1) UUID/pointer → node_uuid index. No payload.
    - parrot.brain.intent_workspace: heavy payload cache (BRAIN-INTENT-WS-V1).

When a Ref is staged in IntentWorkspace, its ref_id is recorded here as
``intent_workspace_ref_id`` so node-level lookup can route to the heavy
payload when needed.

Health monitoring (verify_ref / ref_health_report) is baseline-binary:
    HEALTHY     last access succeeded
    UNVERIFIED  no check yet
    STALE       past TTL since last verify
    BROKEN      access failed (file missing / Graphiti deleted / 4xx URL)

Bionic upgrades (Ebbinghaus decay / access-frequency weighting) are P3.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class RefKind(str, Enum):
    """Ref source types. Lightweight binding only — payload elsewhere."""

    GRAPHITI_UUID = "graphiti_uuid"
    OBSIDIAN_UUID = "obsidian_uuid"
    PHOTO_PATH = "photo_path"
    URL = "url"
    RICH_DOC = "rich_doc"
    VIDEO_SHORT = "video_short"
    AUDIO_CLIP = "audio_clip"
    OTHER = "other"


class RefHealthStatus(str, Enum):
    HEALTHY = "healthy"
    UNVERIFIED = "unverified"
    STALE = "stale"
    BROKEN = "broken"


@dataclass(frozen=True)
class RefBinding:
    node_uuid: str
    kind: RefKind
    ref_value: str
    bound_at: float
    last_verified_at: float
    intent_workspace_ref_id: str = ""


@dataclass(frozen=True)
class RefHealth:
    binding: RefBinding
    status: RefHealthStatus
    last_check_error: str = ""


class RefTable:
    """In-memory ref registry. Owned by ``L15Pool``."""

    def __init__(self, stale_after_seconds: float = 3600.0) -> None:
        # primary index: (kind, ref_value) → RefBinding
        self._by_ref: dict[tuple[RefKind, str], RefBinding] = {}
        # secondary index: node_uuid → list of (kind, ref_value)
        self._by_node: dict[str, list[tuple[RefKind, str]]] = {}
        self._stale_after = stale_after_seconds

    def bind_ref(
        self,
        node_uuid: str,
        kind: RefKind,
        ref_value: str,
        intent_workspace_ref_id: str = "",
    ) -> RefBinding:
        """Idempotent — same (kind, ref_value) re-bind updates existing row."""
        now = time.time()
        binding = RefBinding(
            node_uuid=node_uuid,
            kind=kind,
            ref_value=ref_value,
            bound_at=now,
            last_verified_at=now,
            intent_workspace_ref_id=intent_workspace_ref_id,
        )
        self._by_ref[(kind, ref_value)] = binding
        node_refs = self._by_node.setdefault(node_uuid, [])
        key = (kind, ref_value)
        if key not in node_refs:
            node_refs.append(key)
        return binding

    def lookup_by_ref(self, kind: RefKind, ref_value: str) -> str | None:
        b = self._by_ref.get((kind, ref_value))
        return b.node_uuid if b else None

    def list_refs_of_node(self, node_uuid: str) -> list[RefBinding]:
        keys = self._by_node.get(node_uuid, [])
        return [self._by_ref[k] for k in keys if k in self._by_ref]

    def unbind_ref(self, kind: RefKind, ref_value: str) -> bool:
        binding = self._by_ref.pop((kind, ref_value), None)
        if binding is None:
            return False
        node_keys = self._by_node.get(binding.node_uuid, [])
        try:
            node_keys.remove((kind, ref_value))
        except ValueError:
            pass
        if not node_keys:
            self._by_node.pop(binding.node_uuid, None)
        return True

    def unbind_all_for_node(self, node_uuid: str) -> int:
        """Remove every binding referencing node_uuid (for evict path)."""
        keys = self._by_node.pop(node_uuid, [])
        for k in keys:
            self._by_ref.pop(k, None)
        return len(keys)

    def clear_intent_workspace_ref(self, ws_ref_id: str) -> int:
        """Clear the IntentWorkspace ref_id field on every binding that
        currently points to ``ws_ref_id``. Bindings themselves are kept
        — the lightweight UUID binding is still valid even when the
        heavy payload is evicted."""
        cleared = 0
        for key, b in list(self._by_ref.items()):
            if b.intent_workspace_ref_id == ws_ref_id:
                self._by_ref[key] = RefBinding(
                    node_uuid=b.node_uuid,
                    kind=b.kind,
                    ref_value=b.ref_value,
                    bound_at=b.bound_at,
                    last_verified_at=b.last_verified_at,
                    intent_workspace_ref_id="",
                )
                cleared += 1
        return cleared

    async def verify_ref(self, binding: RefBinding) -> RefHealth:
        """Check Ref still resolves. Baseline:
            - PHOTO_PATH / VIDEO_SHORT / AUDIO_CLIP → file exists
            - URL                                  → no auto-fetch (skip; UNVERIFIED)
            - GRAPHITI_UUID / OBSIDIAN_UUID        → no auto-fetch (skip; UNVERIFIED)
            - other                                → UNVERIFIED

        # TODO(P3-RefHealth): SKELETON. URL / Graphiti / Obsidian
        #   verification is **NOT** implemented. P3 should add:
        #     1. URL: HTTP HEAD request (with timeout / retry budget)
        #     2. GRAPHITI_UUID: query Graphiti for node existence
        #     3. OBSIDIAN_UUID: scan vault for matching uuid:: tag
        #     4. Replace binary HEALTHY/BROKEN with Ebbinghaus decay
        #        (RefHealthMonitor strategy — DSG-POOL-V1 § 7).
        #   Until then, only file-path refs report HEALTHY/BROKEN; other
        #   kinds report UNVERIFIED/STALE based on staleness window.
        """
        try:
            now = time.time()
            if binding.kind in (
                RefKind.PHOTO_PATH,
                RefKind.VIDEO_SHORT,
                RefKind.AUDIO_CLIP,
                RefKind.RICH_DOC,
            ):
                exists = Path(binding.ref_value).exists()
                if exists:
                    self._touch(binding, now)
                    return RefHealth(
                        binding=self._by_ref[(binding.kind, binding.ref_value)],
                        status=RefHealthStatus.HEALTHY,
                    )
                return RefHealth(
                    binding=binding,
                    status=RefHealthStatus.BROKEN,
                    last_check_error="file_not_found",
                )
            # URL / Graphiti / Obsidian — skip baseline verification
            stale_age = now - binding.last_verified_at
            if stale_age > self._stale_after:
                return RefHealth(binding=binding, status=RefHealthStatus.STALE)
            return RefHealth(binding=binding, status=RefHealthStatus.UNVERIFIED)
        except Exception as e:
            return RefHealth(
                binding=binding,
                status=RefHealthStatus.BROKEN,
                last_check_error=str(e),
            )

    def _touch(self, binding: RefBinding, now: float) -> None:
        key = (binding.kind, binding.ref_value)
        old = self._by_ref.get(key)
        if old is None:
            return
        self._by_ref[key] = RefBinding(
            node_uuid=old.node_uuid,
            kind=old.kind,
            ref_value=old.ref_value,
            bound_at=old.bound_at,
            last_verified_at=now,
            intent_workspace_ref_id=old.intent_workspace_ref_id,
        )

    async def ref_health_report(
        self, kinds: frozenset[RefKind] | None = None
    ) -> list[RefHealth]:
        out: list[RefHealth] = []
        for binding in self._by_ref.values():
            if kinds is not None and binding.kind not in kinds:
                continue
            out.append(await self.verify_ref(binding))
        return out

    def total_bindings(self) -> int:
        return len(self._by_ref)


__all__ = [
    "RefBinding",
    "RefHealth",
    "RefHealthStatus",
    "RefKind",
    "RefTable",
]
