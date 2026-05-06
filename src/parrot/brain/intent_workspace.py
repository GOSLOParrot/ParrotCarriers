"""IntentWorkspace — Brain Intent-layer Ref staging space.

BRAIN-INTENT-WS-V1.

Purpose: holds large files / rich-doc payloads that GOSLO Intent layer
is **currently** reading or analyzing (photos, mermaid diagrams,
nanobot rich-text reports, short videos, Plan payloads, etc.).

Lifecycle: stage → fetch → list_active → evict (manual / auto on
IntentEvent close / auto on capacity pressure).

Module layout (see BRAIN-INTENT-WS-V1 § 2.2):
    src/parrot/brain/
    ├── intent_workspace.py            ← this file
    └── intent_workspace_backend.py    ← Backend Protocol + InMemory + Disk

Pipeline-agnostic by design: the Intent layer doesn't know if Line A
(Gemini Live) or Line B (STT-LLM-TTS) initiated the Intent — both feed
ObservationSource.GEMINI_ORAL via the same transcript_extractor (per
LineB completion report § 1.3 ObservationSource enum 0 漂移). So this
module simply records ``StagedRef.metadata.origin`` for traceability,
without branching by upstream LLM.
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid as uuid_lib
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from parrot.brain.intent_workspace_backend import (
    InMemoryBackend,
    IntentWorkspaceBackend,
)

logger = logging.getLogger(__name__)


# ─── Enums ────────────────────────────────────────────────────────


class StagedRefKind(str, Enum):
    PHOTO = "photo"
    DOC = "doc"
    URL = "url"
    MERMAID = "mermaid"
    RICH_REPORT = "rich_report"
    VIDEO_SHORT = "video_short"
    AUDIO_CLIP = "audio_clip"
    PLAN = "plan"
    OTHER = "other"


class PayloadSource(str, Enum):
    DISK_PATH = "disk_path"
    INLINE_BYTES = "inline_bytes"
    INLINE_TEXT = "inline_text"
    URL = "url"


class PressureLevel(str, Enum):
    OK = "ok"
    WATCH = "watch"
    WARN = "warn"
    CRITICAL = "critical"


# ─── Schema ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class StagedRefMetadata:
    origin: str = ""
    kind: StagedRefKind = StagedRefKind.OTHER
    payload_source: PayloadSource = PayloadSource.INLINE_BYTES
    related_node_uuid: str = ""
    related_intent_event_id: str = ""
    related_plan_id: str = ""
    size_bytes: int = 0
    loaded_at: float = 0.0
    last_accessed_at: float = 0.0
    auto_evict_on_intent_close: bool = True
    expires_at: float = 0.0
    custom_meta: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StagedRef:
    ref_id: str
    kind: StagedRefKind | None
    payload_source: PayloadSource | None
    payload: Path | bytes | str | None
    metadata: StagedRefMetadata


@dataclass(frozen=True)
class StagedRefRequest:
    """TriggerOutcome upload-channel payload (DSG-TRIGGER-V2 § 3.3)."""

    kind: StagedRefKind
    payload_source: PayloadSource
    payload_value: Any
    metadata: StagedRefMetadata


@dataclass(frozen=True)
class RefHandle:
    ref_id: str
    kind: StagedRefKind | None
    metadata: StagedRefMetadata

    def __repr__(self) -> str:
        kind = self.kind.value if self.kind else "unknown"
        return f"RefHandle({kind}/{self.ref_id})"


@dataclass(frozen=True)
class PressureReport:
    backend_usage_bytes: int
    backend_total_capacity: int
    pressure_level: PressureLevel
    candidate_evictions: tuple[str, ...] = ()


# ─── IntentWorkspace ────────────────────────────────────────────


class IntentWorkspace:
    """In-memory key-value cache for GOSLO Intent layer payloads."""

    def __init__(
        self,
        backend: IntentWorkspaceBackend | None = None,
        max_memory_bytes: int = 256 * 1024 * 1024,
    ) -> None:
        self._backend: IntentWorkspaceBackend = backend or InMemoryBackend()
        self._max_bytes = max_memory_bytes
        self._index: dict[str, StagedRef] = {}
        # idempotency key (kind, payload-hash) → ref_id
        self._idempotency: dict[str, str] = {}

    # ─── Stage / Fetch ─────────────────────────────────────────

    async def stage(self, request: StagedRefRequest) -> RefHandle:
        idempotency_key = self._idempotency_key(
            request.kind, request.payload_source, request.payload_value,
        )
        existing_id = self._idempotency.get(idempotency_key)
        if existing_id is not None:
            existing_ref = self._index.get(existing_id)
            if existing_ref is not None:
                return RefHandle(
                    ref_id=existing_id,
                    kind=existing_ref.kind,
                    metadata=existing_ref.metadata,
                )

        ref_id = uuid_lib.uuid4().hex[:16]
        now = time.time()
        size = self._estimate_size(request.payload_source, request.payload_value)

        meta = StagedRefMetadata(
            origin=request.metadata.origin,
            kind=request.kind,
            payload_source=request.payload_source,
            related_node_uuid=request.metadata.related_node_uuid,
            related_intent_event_id=request.metadata.related_intent_event_id,
            related_plan_id=request.metadata.related_plan_id,
            size_bytes=size,
            loaded_at=now,
            last_accessed_at=now,
            auto_evict_on_intent_close=request.metadata.auto_evict_on_intent_close,
            expires_at=request.metadata.expires_at,
            custom_meta=dict(request.metadata.custom_meta),
        )

        await self._backend.put(ref_id, request.payload_value, meta)

        ref = StagedRef(
            ref_id=ref_id,
            kind=request.kind,
            payload_source=request.payload_source,
            payload=request.payload_value,
            metadata=meta,
        )
        self._index[ref_id] = ref
        self._idempotency[idempotency_key] = ref_id

        return RefHandle(ref_id=ref_id, kind=request.kind, metadata=meta)

    async def stage_from_path(
        self,
        path: Path,
        kind: StagedRefKind,
        metadata: StagedRefMetadata,
    ) -> RefHandle:
        return await self.stage(StagedRefRequest(
            kind=kind,
            payload_source=PayloadSource.DISK_PATH,
            payload_value=path,
            metadata=metadata,
        ))

    def fetch(self, ref_id: str) -> StagedRef | None:
        ref = self._index.get(ref_id)
        if ref is None:
            return None
        # update last_accessed_at
        new_meta = StagedRefMetadata(
            origin=ref.metadata.origin,
            kind=ref.metadata.kind,
            payload_source=ref.metadata.payload_source,
            related_node_uuid=ref.metadata.related_node_uuid,
            related_intent_event_id=ref.metadata.related_intent_event_id,
            related_plan_id=ref.metadata.related_plan_id,
            size_bytes=ref.metadata.size_bytes,
            loaded_at=ref.metadata.loaded_at,
            last_accessed_at=time.time(),
            auto_evict_on_intent_close=ref.metadata.auto_evict_on_intent_close,
            expires_at=ref.metadata.expires_at,
            custom_meta=dict(ref.metadata.custom_meta),
        )
        new_ref = StagedRef(
            ref_id=ref.ref_id,
            kind=ref.kind,
            payload_source=ref.payload_source,
            payload=ref.payload,
            metadata=new_meta,
        )
        self._index[ref_id] = new_ref
        return new_ref

    def fetch_payload(self, ref_id: str) -> Any:
        ref = self.fetch(ref_id)
        return ref.payload if ref else None

    # ─── Listing ───────────────────────────────────────────────

    def list_active(
        self,
        intent_event_id: str | None = None,
        kinds: frozenset[StagedRefKind] | None = None,
    ) -> list[RefHandle]:
        out: list[RefHandle] = []
        for ref in self._index.values():
            if intent_event_id is not None and ref.metadata.related_intent_event_id != intent_event_id:
                continue
            if kinds is not None and ref.kind not in kinds:
                continue
            out.append(RefHandle(
                ref_id=ref.ref_id,
                kind=ref.kind,
                metadata=ref.metadata,
            ))
        return out

    # ─── Eviction ──────────────────────────────────────────────

    async def evict(self, ref_id: str) -> bool:
        ref = self._index.pop(ref_id, None)
        if ref is None:
            return False
        await self._backend.delete(ref_id)
        # remove idempotency entries pointing here
        keys_to_remove = [k for k, v in self._idempotency.items() if v == ref_id]
        for k in keys_to_remove:
            self._idempotency.pop(k, None)
        return True

    async def evict_intent(self, intent_event_id: str) -> int:
        targets = [
            ref_id for ref_id, ref in list(self._index.items())
            if ref.metadata.related_intent_event_id == intent_event_id
            and ref.metadata.auto_evict_on_intent_close
        ]
        evicted = 0
        for ref_id in targets:
            if await self.evict(ref_id):
                evicted += 1
        return evicted

    async def evict_expired(self) -> int:
        now = time.time()
        targets = [
            ref_id for ref_id, ref in list(self._index.items())
            if ref.metadata.expires_at and ref.metadata.expires_at <= now
        ]
        evicted = 0
        for ref_id in targets:
            if await self.evict(ref_id):
                evicted += 1
        return evicted

    # ─── Pressure / Health ─────────────────────────────────────

    def memory_pressure(self) -> PressureReport:
        usage = self._backend.usage()
        ratio = usage / self._max_bytes if self._max_bytes else 0.0

        if ratio > 0.95:
            level = PressureLevel.CRITICAL
        elif ratio > 0.80:
            level = PressureLevel.WARN
        elif ratio > 0.60:
            level = PressureLevel.WATCH
        else:
            level = PressureLevel.OK

        # Candidate evictions: LRU by last_accessed_at
        sorted_refs = sorted(
            self._index.values(),
            key=lambda r: r.metadata.last_accessed_at,
        )
        candidates = tuple(r.ref_id for r in sorted_refs[:8])

        return PressureReport(
            backend_usage_bytes=usage,
            backend_total_capacity=self._max_bytes,
            pressure_level=level,
            candidate_evictions=candidates,
        )

    async def close(self) -> None:
        await self._backend.close()
        self._index.clear()
        self._idempotency.clear()

    # ─── Internals ─────────────────────────────────────────────

    @staticmethod
    def _estimate_size(payload_source: PayloadSource, value: Any) -> int:
        if payload_source == PayloadSource.INLINE_BYTES and isinstance(value, (bytes, bytearray)):
            return len(value)
        if payload_source == PayloadSource.INLINE_TEXT and isinstance(value, str):
            return len(value.encode("utf-8", "replace"))
        if payload_source == PayloadSource.DISK_PATH:
            try:
                return Path(value).stat().st_size
            except OSError:
                return 0
        return 0

    @staticmethod
    def _idempotency_key(
        kind: StagedRefKind, ps: PayloadSource, value: Any,
    ) -> str:
        h = hashlib.sha1()
        h.update(kind.value.encode("utf-8"))
        h.update(b":")
        h.update(ps.value.encode("utf-8"))
        h.update(b":")
        if isinstance(value, (bytes, bytearray)):
            h.update(bytes(value)[:1024])  # short prefix
            h.update(str(len(value)).encode("ascii"))
        elif isinstance(value, Path):
            h.update(str(value).encode("utf-8", "replace"))
        elif isinstance(value, str):
            h.update(value.encode("utf-8", "replace"))
        else:
            h.update(repr(value).encode("utf-8", "replace"))
        return h.hexdigest()[:24]


# ─── Singleton + test injection ──────────────────────────────────

_workspace: IntentWorkspace | None = None


def get_intent_workspace() -> IntentWorkspace:
    global _workspace
    if _workspace is None:
        _workspace = IntentWorkspace()
    return _workspace


def set_intent_workspace_for_test(ws: IntentWorkspace | None) -> None:
    global _workspace
    _workspace = ws


def register_intent_workspace_backend(backend: IntentWorkspaceBackend) -> None:
    """Replace the global workspace's backend (P3 / test only)."""
    global _workspace
    if _workspace is None:
        _workspace = IntentWorkspace(backend=backend)
    else:
        _workspace._backend = backend  # type: ignore[attr-defined]


__all__ = [
    "IntentWorkspace",
    "PayloadSource",
    "PressureLevel",
    "PressureReport",
    "RefHandle",
    "StagedRef",
    "StagedRefKind",
    "StagedRefMetadata",
    "StagedRefRequest",
    "get_intent_workspace",
    "register_intent_workspace_backend",
    "set_intent_workspace_for_test",
]
