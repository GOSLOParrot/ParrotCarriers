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

Multi-agent collaboration (Phase 3, NEED-P2.5 / Plan):
    A single Brain process can run several actors concurrently —
    ParrotAssistant (main LLM session), nanobot subtasks, Plan steps.
    Each actor wants its own scoped view of staged refs:

    * Parent / global workspace owns shared refs (PHOTO captured by user,
      DOC pinned via remember-tool, etc.).
    * A child actor opens a ``ScopedIntentWorkspace`` keyed by
      ``actor_id`` (e.g. plan_id / nanobot_task_id). The child can READ
      everything the parent sees, but its own ``stage()`` calls record
      refs that only the child + parent can see, never sibling actors.

    This mirrors the LimboAI / Unreal Blackboard "scope chain" pattern
    and the Cursor Agent.create / resume sub-context model. We do **not**
    physically copy refs — child views are filters over the parent index.

Pressure callbacks (Phase 3):
    Long-running Brain sessions can accumulate refs faster than the user
    closes IntentEvents. ``register_pressure_callback`` lets a subscriber
    react when ``memory_pressure().pressure_level`` first reaches WARN /
    CRITICAL — typical actions: prompt the LLM to summarise + evict, or
    page out PHOTO refs to disk via Backend.swap.
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


PressureCallback = "Callable[[PressureReport], None]"
"""Sync callable invoked by :meth:`memory_pressure` on level transitions."""


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
        # Actor metadata: ref_id → owning_actor_id ("" = parent / global).
        self._owners: dict[str, str] = {}
        # Last-fired pressure level (so callbacks only fire on transitions).
        self._last_pressure_level: PressureLevel | None = None
        self._pressure_callbacks: list[Any] = []  # PressureCallback list

    # ─── Stage / Fetch ─────────────────────────────────────────

    async def stage(
        self,
        request: StagedRefRequest,
        *,
        owner_id: str = "",
    ) -> RefHandle:
        """Stage a Ref.

        ``owner_id`` records which actor owns the ref:
            ""           — parent / global (visible to every scoped view)
            "<actor_id>" — child scope (visible only to parent + that scope)

        Idempotency checks consider ``owner_id`` so two scoped actors
        staging the same payload independently get distinct ref_ids — they
        often have orthogonal lifecycles (one closes, the other lingers).
        """
        idempotency_key = self._idempotency_key(
            request.kind, request.payload_source, request.payload_value,
            owner_id=owner_id,
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
        self._owners[ref_id] = owner_id

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
        *,
        plan_id: str | None = None,
        role: str | None = None,
        origin_prefix: str | None = None,
        owner_id: str | None = None,
        include_parent: bool = True,
    ) -> list[RefHandle]:
        """List active refs with rich filters.

        ``intent_event_id`` / ``kinds`` — original 2 filters (back-compat).
        ``plan_id`` — only refs with ``metadata.related_plan_id == plan_id``.
        ``role`` — match ``metadata.custom_meta["role"]``. The Plan / Photo
            / Report flow sets ``role = "plan_draft"`` / ``"plan_step"`` /
            ``"identify_object_pending"`` etc. instead of expanding the
            ``StagedRefKind`` enum (interface_design_supplement_20260507 §1.1
            decision: keep enum content-typed, encode roles in metadata).
        ``origin_prefix`` — substring/prefix match on ``metadata.origin``
            (useful for ``"trigger:"`` / ``"tool:"`` / ``"user:"`` filters).
        ``owner_id`` / ``include_parent`` — multi-agent scope filter
            (default behaviour: include both parent + named owner refs).
        """
        out: list[RefHandle] = []
        for ref in self._index.values():
            if intent_event_id is not None and ref.metadata.related_intent_event_id != intent_event_id:
                continue
            if kinds is not None and ref.kind not in kinds:
                continue
            if plan_id is not None and ref.metadata.related_plan_id != plan_id:
                continue
            if role is not None:
                actual_role = (ref.metadata.custom_meta or {}).get("role", "")
                if actual_role != role:
                    continue
            if origin_prefix is not None and not ref.metadata.origin.startswith(origin_prefix):
                continue
            if owner_id is not None:
                this_owner = self._owners.get(ref.ref_id, "")
                if this_owner != owner_id:
                    if not (include_parent and this_owner == ""):
                        continue
            out.append(RefHandle(
                ref_id=ref.ref_id,
                kind=ref.kind,
                metadata=ref.metadata,
            ))
        return out

    def get_owner(self, ref_id: str) -> str:
        """Return owner_id for ``ref_id`` (``""`` = parent / global)."""
        return self._owners.get(ref_id, "")

    def list_by_role(self, role: str) -> list[RefHandle]:
        """Sugar for ``list_active(role=role)`` — common Plan / Report query."""
        return self.list_active(role=role)

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
        self._owners.pop(ref_id, None)
        return True

    async def evict_owner(self, owner_id: str) -> int:
        """Evict every ref owned by ``owner_id`` (multi-agent shutdown).

        Parent refs (``owner_id=""``) are never touched even if the caller
        passes ``""`` — that would wipe shared state. Use :meth:`close`
        for full teardown instead.
        """
        if not owner_id:
            return 0
        targets = [
            ref_id for ref_id, owner in list(self._owners.items())
            if owner == owner_id
        ]
        evicted = 0
        for ref_id in targets:
            if await self.evict(ref_id):
                evicted += 1
        return evicted

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

        # Candidate evictions: LRU by last_accessed_at, but exclude high-
        # value kinds (PLAN / RICH_REPORT) so a careless callback doesn't
        # silently delete in-flight Plan drafts.
        protected = {StagedRefKind.PLAN, StagedRefKind.RICH_REPORT}
        sorted_refs = sorted(
            (r for r in self._index.values() if r.kind not in protected),
            key=lambda r: r.metadata.last_accessed_at,
        )
        candidates = tuple(r.ref_id for r in sorted_refs[:8])

        report = PressureReport(
            backend_usage_bytes=usage,
            backend_total_capacity=self._max_bytes,
            pressure_level=level,
            candidate_evictions=candidates,
        )

        if level != self._last_pressure_level:
            self._last_pressure_level = level
            for cb in list(self._pressure_callbacks):
                try:
                    cb(report)
                except Exception:
                    logger.exception("pressure callback failed")

        return report

    def register_pressure_callback(self, cb: Any) -> None:
        """Subscribe ``cb(report)`` to fire when pressure level transitions.

        Callback fires synchronously from :meth:`memory_pressure`. Heavy
        work should hop into ``asyncio.create_task`` inside the callback.
        Adds idempotently — duplicate registrations are accepted (caller
        can deregister via :meth:`unregister_pressure_callback`).
        """
        self._pressure_callbacks.append(cb)

    def unregister_pressure_callback(self, cb: Any) -> bool:
        try:
            self._pressure_callbacks.remove(cb)
            return True
        except ValueError:
            return False

    # ─── Multi-agent scoped views ─────────────────────────────

    def scope(self, owner_id: str) -> "ScopedIntentWorkspace":
        """Return a child view bound to ``owner_id``.

        Reads through to the parent. Writes (``stage`` / ``evict``) only
        affect refs owned by ``owner_id``. Parent refs are never mutated
        through a child scope.
        """
        if not owner_id:
            raise ValueError("owner_id must be non-empty for child scope")
        return ScopedIntentWorkspace(self, owner_id)

    # ─── Recovery (Disk backend only) ─────────────────────────

    async def recover_from_disk(self) -> int:
        """If the active backend is a DiskBackend, rebuild the upper-layer
        ``_index`` + ``_idempotency`` from on-disk metadata files.

        Returns the number of refs recovered. Safe no-op when the backend
        is in-memory (returns 0).
        """
        recover_fn = getattr(self._backend, "recover", None)
        if not callable(recover_fn):
            return 0
        recovered = await recover_fn()
        n = 0
        for ref_id, ref in recovered:
            self._index[ref_id] = ref
            idem = self._idempotency_key(
                ref.kind or StagedRefKind.OTHER,
                ref.payload_source or PayloadSource.INLINE_TEXT,
                ref.payload,
                owner_id="",
            )
            self._idempotency.setdefault(idem, ref_id)
            self._owners.setdefault(ref_id, "")
            n += 1
        return n

    async def close(self) -> None:
        await self._backend.close()
        self._index.clear()
        self._idempotency.clear()
        self._owners.clear()
        self._pressure_callbacks.clear()
        self._last_pressure_level = None

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
        kind: StagedRefKind,
        ps: PayloadSource,
        value: Any,
        *,
        owner_id: str = "",
    ) -> str:
        h = hashlib.sha1()
        h.update(kind.value.encode("utf-8"))
        h.update(b":")
        h.update(ps.value.encode("utf-8"))
        h.update(b":")
        h.update(owner_id.encode("utf-8", "replace"))
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


# ─── Multi-agent scoped view ─────────────────────────────────────


class ScopedIntentWorkspace:
    """Read-through child view of :class:`IntentWorkspace`.

    Mature multi-agent coordination patterns (LimboAI / Unreal Blackboard
    scope chain; Cursor Agent.create + resume; LangChain ChatHistory +
    per-agent state) all share the same shape:

        Parent global state visible everywhere; child has its own write
        scope; sibling actors never see each other's writes by default.

    Usage::

        plan_ws = ws.scope(owner_id=plan_id)
        await plan_ws.stage(req)                # owned by plan_id
        plan_ws.list_active(role="plan_step")   # parent + plan_id refs
        await plan_ws.shutdown()                # evicts plan_id refs only

    Reads default to ``include_parent=True``; pass
    ``include_parent=False`` for a strict child-only view (rare; mostly
    used by tests / per-agent debug snapshots).
    """

    def __init__(self, parent: IntentWorkspace, owner_id: str) -> None:
        self._parent = parent
        self._owner_id = owner_id

    @property
    def owner_id(self) -> str:
        return self._owner_id

    async def stage(self, request: StagedRefRequest) -> RefHandle:
        return await self._parent.stage(request, owner_id=self._owner_id)

    async def stage_from_path(
        self,
        path: Path,
        kind: StagedRefKind,
        metadata: StagedRefMetadata,
    ) -> RefHandle:
        request = StagedRefRequest(
            kind=kind,
            payload_source=PayloadSource.DISK_PATH,
            payload_value=path,
            metadata=metadata,
        )
        return await self._parent.stage(request, owner_id=self._owner_id)

    def fetch(self, ref_id: str) -> StagedRef | None:
        # Children may fetch any ref the parent index knows about (parent
        # + sibling-public refs are visible read-only). Use list_active
        # if you only want refs *owned* by this scope.
        return self._parent.fetch(ref_id)

    def fetch_payload(self, ref_id: str) -> Any:
        return self._parent.fetch_payload(ref_id)

    def list_active(
        self,
        intent_event_id: str | None = None,
        kinds: frozenset[StagedRefKind] | None = None,
        *,
        plan_id: str | None = None,
        role: str | None = None,
        origin_prefix: str | None = None,
        include_parent: bool = True,
    ) -> list[RefHandle]:
        return self._parent.list_active(
            intent_event_id=intent_event_id,
            kinds=kinds,
            plan_id=plan_id,
            role=role,
            origin_prefix=origin_prefix,
            owner_id=self._owner_id,
            include_parent=include_parent,
        )

    async def evict(self, ref_id: str) -> bool:
        """Only allow eviction of refs owned by this scope."""
        if self._parent.get_owner(ref_id) != self._owner_id:
            return False
        return await self._parent.evict(ref_id)

    async def shutdown(self) -> int:
        """Evict all refs owned by this scope. Parent state untouched."""
        return await self._parent.evict_owner(self._owner_id)


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
    "PressureCallback",
    "PressureLevel",
    "PressureReport",
    "RefHandle",
    "ScopedIntentWorkspace",
    "StagedRef",
    "StagedRefKind",
    "StagedRefMetadata",
    "StagedRefRequest",
    "get_intent_workspace",
    "register_intent_workspace_backend",
    "set_intent_workspace_for_test",
]
