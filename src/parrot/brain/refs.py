"""Sprint4 Phase 4 W6-7 — session-scoped RefBinding registry.

Authoritative spec: ``architecture/sprint4_phase4_entry_20260430.md §8.7``
(W6-7 RefBinding 落地) + §8.1 L9 (BBox/Focus 锚定 → AttentionHint 路径).

What lives here
---------------
A process-wide in-memory dict keyed by ``ref_id`` that holds the
:class:`parrot.shared.ref_binding.RefBinding` objects created during a
LiveKit session. Two index dicts (by bbox_id and by focus_id) make it
cheap for downstream observers / threshold to look up a Ref by the
Unity-side artifact id without iterating the registry.

Why this is "Brain side" not "DSG side"
---------------------------------------
RefBindings are session-scoped runtime state created in response to
EcpEvents arriving on the LiveKit Room. They do **not** belong inside
``parrot.dsg.l2b_graph`` (which is the durable semantic-graph layer)
because:

    1. RefBindings can stay UNRESOLVED for a whole session — there's
       nothing to put in a graph node yet.
    2. Their lifecycle is tied to user UI gestures (bbox placed/removed,
       focus anchored/released), not to L2-B's own attention/episode
       housekeeping.
    3. When a RefBinding does eventually resolve to an L2-B node, the
       resolution is recorded **on the RefBinding** (target_kind /
       target_id), and the L2-B node is bumped via
       ``dsg.attention.hint_writer`` — there is no need for L2-B to know
       the Ref exists.

Lifecycle
---------
Each LiveKit session ideally calls :func:`reset_refs_for_session` on
disconnect. For Phase 4 W6-7 the agent boot does NOT install this hook
(boot already does enough); the registry simply grows during the
process lifetime and is bounded by the bbox/focus removal observers
that ``unbind`` on ``bbox.removed`` / ``focus.released``. Multi-session
agent processes (which Phase 4 doesn't have yet) should add the hook in
brain.agent's room disconnect handler.

Test API
--------
:func:`reset_refs_for_tests` drops everything. Production code MUST NOT
call this — it would orphan UI state mid-session.
"""

from __future__ import annotations

import logging
import threading
from typing import Iterable

from parrot.shared.ref_binding import RefBinding, RefKind, RefTargetKind


logger = logging.getLogger(__name__)


# Single source of truth — keyed by RefBinding.ref_id (time-sortable string).
_refs: dict[str, RefBinding] = {}

# Secondary indexes: kind-specific Unity-side artifact id → ref_id. Lets
# bbox.placed/removed and focus.anchored/released observers find / drop
# their Ref in O(1) without scanning _refs.
_bbox_index: dict[str, str] = {}  # bbox_id → ref_id
_focus_index: dict[str, str] = {}  # focus_id → ref_id

# Single mutex protects all three dicts. Phase 4 W6-7 events arrive on
# the EcpEventIngest dispatcher which is single-threaded, but we cheap-
# protect against future async fan-out paths writing concurrently.
_lock = threading.RLock()


# ─── creation / lookup / removal ────────────────────────────────────


def bind_bbox(
    *,
    bbox_id: str,
    source_event_id: str,
    label: str = "",
) -> RefBinding:
    """Create a new UNRESOLVED RefBinding for a placed BBox.

    If a Ref already exists for this ``bbox_id`` (e.g., user placed twice
    without an intervening removal), the existing Ref is returned —
    we don't fan-out duplicate Refs for the same Unity-side artifact.
    """
    with _lock:
        existing_ref_id = _bbox_index.get(bbox_id)
        if existing_ref_id:
            existing = _refs.get(existing_ref_id)
            if existing is not None:
                logger.debug(
                    "[refs] bind_bbox(%s) hit existing ref_id=%s",
                    bbox_id, existing_ref_id,
                )
                return existing

        ref = RefBinding(
            kind=RefKind.BBOX,
            source_event_id=source_event_id,
            label=label or f"bbox:{bbox_id}",
        )
        _refs[ref.ref_id] = ref
        _bbox_index[bbox_id] = ref.ref_id
        logger.debug(
            "[refs] bind_bbox bbox_id=%s → ref_id=%s",
            bbox_id, ref.ref_id,
        )
        return ref


def bind_focus(
    *,
    focus_id: str,
    source_event_id: str,
    label: str = "",
) -> RefBinding:
    """Create a new UNRESOLVED RefBinding for an anchored Focus.

    Same idempotency contract as :func:`bind_bbox`.
    """
    with _lock:
        existing_ref_id = _focus_index.get(focus_id)
        if existing_ref_id:
            existing = _refs.get(existing_ref_id)
            if existing is not None:
                return existing

        ref = RefBinding(
            kind=RefKind.FOCUS,
            source_event_id=source_event_id,
            label=label or f"focus:{focus_id}",
        )
        _refs[ref.ref_id] = ref
        _focus_index[focus_id] = ref.ref_id
        return ref


def get_ref(ref_id: str) -> RefBinding | None:
    """Look up by ref_id."""
    with _lock:
        return _refs.get(ref_id)


def get_ref_by_bbox(bbox_id: str) -> RefBinding | None:
    with _lock:
        rid = _bbox_index.get(bbox_id)
        return _refs.get(rid) if rid else None


def get_ref_by_focus(focus_id: str) -> RefBinding | None:
    with _lock:
        rid = _focus_index.get(focus_id)
        return _refs.get(rid) if rid else None


def unbind_bbox(bbox_id: str) -> RefBinding | None:
    """Remove a bbox-anchored Ref. Returns the removed Ref or None."""
    with _lock:
        rid = _bbox_index.pop(bbox_id, None)
        if not rid:
            return None
        return _refs.pop(rid, None)


def unbind_focus(focus_id: str) -> RefBinding | None:
    with _lock:
        rid = _focus_index.pop(focus_id, None)
        if not rid:
            return None
        return _refs.pop(rid, None)


def resolve_ref(
    ref_id: str,
    *,
    target_kind: RefTargetKind,
    target_id: str,
    new_event_id: str | None = None,
) -> RefBinding | None:
    """Update a Ref's target via the immutable :meth:`RefBinding.with_resolved_target`
    pattern. Replaces the entry in place under the SAME ref_id (the
    secondary indexes don't need updating since they key on ref_id).

    Returns the new RefBinding (with revision bumped), or None if the
    ref_id was unknown.
    """
    with _lock:
        existing = _refs.get(ref_id)
        if existing is None:
            return None
        updated = existing.with_resolved_target(
            target_kind=target_kind,
            target_id=target_id,
            new_event_id=new_event_id,
        )
        _refs[ref_id] = updated
        logger.debug(
            "[refs] resolve_ref ref_id=%s → %s/%s rev=%d",
            ref_id, target_kind, target_id, updated.revision,
        )
        return updated


# ─── introspection / lifecycle ──────────────────────────────────────


def all_refs() -> tuple[RefBinding, ...]:
    """Snapshot of every Ref currently in the registry."""
    with _lock:
        return tuple(_refs.values())


def metrics_snapshot() -> dict[str, int]:
    """Cheap counters for debug HUD / pytest assertions."""
    with _lock:
        return {
            "total_refs": len(_refs),
            "bbox_refs": len(_bbox_index),
            "focus_refs": len(_focus_index),
        }


def reset_refs_for_session(active_ids: Iterable[str] | None = None) -> int:
    """Drop every Ref whose ``ref_id`` is NOT in ``active_ids``.

    Production sessions can call this on Room.Disconnected to keep the
    registry from holding orphan Refs across sessions. For Phase 4 W6-7
    the agent boot does not install this hook; the bbox/focus removal
    observers handle cleanup of the common case (user removes BBox /
    releases Focus). Returns the number of refs dropped.
    """
    keep = set(active_ids or ())
    with _lock:
        before = len(_refs)
        to_drop = [rid for rid in _refs if rid not in keep]
        for rid in to_drop:
            _refs.pop(rid, None)
        # Sweep secondary indexes for any orphaned entries.
        orphan_bbox = [bid for bid, rid in _bbox_index.items() if rid not in _refs]
        for bid in orphan_bbox:
            _bbox_index.pop(bid, None)
        orphan_focus = [fid for fid, rid in _focus_index.items() if rid not in _refs]
        for fid in orphan_focus:
            _focus_index.pop(fid, None)
        return before - len(_refs)


def reset_refs_for_tests() -> None:
    """Wipe the registry. Tests only."""
    with _lock:
        _refs.clear()
        _bbox_index.clear()
        _focus_index.clear()


__all__ = [
    "all_refs",
    "bind_bbox",
    "bind_focus",
    "get_ref",
    "get_ref_by_bbox",
    "get_ref_by_focus",
    "metrics_snapshot",
    "resolve_ref",
    "reset_refs_for_session",
    "reset_refs_for_tests",
    "unbind_bbox",
    "unbind_focus",
]
