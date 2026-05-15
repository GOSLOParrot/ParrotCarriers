"""Web-only changed-since wrapper for the Memory Graph live-state.

``parrot.brain.app_live_state`` is a full snapshot builder shared by the older
App monitor and the React Web Console. Its ``sequence`` increments on every
read, which is useful for debugging but too noisy for a realtime canvas. This
module keeps a Web Console read model sequence based on stable memory content
instead. It does not introduce a new App DTO.
"""

from __future__ import annotations

import json
import time
from typing import Any

from parrot.brain.app_live_state import build_app_live_state

_memory_sequence = 0
_memory_signature = ""

_ALWAYS_VOLATILE_KEYS = frozenset({
    "generated_at",
    "expires_in_seconds",
})
_ROOT_VOLATILE_KEYS = frozenset({"sequence"})


def build_memory_live_state_changes(*, since: int = 0, limit: int = 120) -> dict[str, Any]:
    """Return a polling diff envelope for Memory Graph state.

    V1 deliberately stays polling-based. The stable signature ignores snapshot
    bookkeeping fields that change on every read, so the React canvas can skip
    applying a no-op Memory Graph update while still seeing real L2-B,
    Blackboard, IntentWorkspace, and Ref changes.
    """

    global _memory_sequence, _memory_signature

    snapshot = build_app_live_state(l2b_limit=max(1, min(int(limit or 120), 200))).as_json()
    signature = _stable_memory_signature(snapshot)
    if signature != _memory_signature:
        _memory_sequence += 1
        _memory_signature = signature

    sequence = _memory_sequence
    changed = sequence > max(0, int(since or 0))
    events = _memory_events_from_snapshot(snapshot, sequence) if changed else []
    return {
        "success": True,
        "action": "memory.live_state.changes",
        "since": max(0, int(since or 0)),
        "sequence": sequence,
        "changed": changed,
        "generated_at": time.time(),
        "events": events,
        "snapshot": snapshot if changed else None,
        "audit": {
            "web_only": True,
            "read_model": True,
            "diff_strategy": "stable_signature_polling",
            "source": "parrot.brain.app_live_state.build_app_live_state",
            "shared_core_candidates": ["CORE-009", "CORE-010"],
            "app_dto_pollution": False,
        },
    }


def _stable_memory_signature(snapshot: dict[str, Any]) -> str:
    """Create a stable content signature for changed-since polling."""

    normalized = _strip_volatile(snapshot, depth=0)
    return json.dumps(normalized, sort_keys=True, ensure_ascii=False, default=str)


def _strip_volatile(value: Any, *, depth: int) -> Any:
    """Remove transport noise without hiding nested business sequence fields."""

    if isinstance(value, dict):
        return {
            str(key): _strip_volatile(item, depth=depth + 1)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
            if str(key) not in _ALWAYS_VOLATILE_KEYS
            and not (depth == 0 and str(key) in _ROOT_VOLATILE_KEYS)
        }
    if isinstance(value, list):
        return [_strip_volatile(item, depth=depth + 1) for item in value]
    if isinstance(value, tuple):
        return [_strip_volatile(item, depth=depth + 1) for item in value]
    return value


def _memory_events_from_snapshot(snapshot: dict[str, Any], sequence: int) -> list[dict[str, Any]]:
    """Build a small operator-readable event list from the current snapshot."""

    events: list[dict[str, Any]] = []
    l2b = snapshot.get("l2b", {}) if isinstance(snapshot.get("l2b"), dict) else {}
    blackboard = (
        snapshot.get("blackboard", {})
        if isinstance(snapshot.get("blackboard"), dict)
        else {}
    )
    intent_workspace = (
        snapshot.get("intent_workspace", {})
        if isinstance(snapshot.get("intent_workspace"), dict)
        else {}
    )
    refs = snapshot.get("refs", {}) if isinstance(snapshot.get("refs"), dict) else {}

    events.append(_event(
        sequence,
        entity_kind="memory_graph",
        entity_id="l2b",
        op="snapshot",
        status="observed",
        summary=(
            f"L2-B nodes {int(l2b.get('node_count') or 0)} / "
            f"edges {int(l2b.get('edge_count') or 0)}"
        ),
    ))
    events.append(_event(
        sequence,
        entity_kind="blackboard",
        entity_id="summary",
        op="present_keys",
        status="observed",
        summary=f"{int(blackboard.get('present_count') or 0)} / {int(blackboard.get('declared_count') or 0)} keys present",
    ))
    events.append(_event(
        sequence,
        entity_kind="intent_workspace",
        entity_id="refs",
        op="active_refs",
        status="observed",
        summary=f"{int(intent_workspace.get('ref_count') or 0)} active refs",
    ))
    events.append(_event(
        sequence,
        entity_kind="refs",
        entity_id="registry",
        op="resolved_targets",
        status="observed",
        summary=f"{len(refs.get('resolved_l2b_targets') or [])} resolved L2-B targets",
    ))

    for node in list(l2b.get("top_attention") or [])[:6]:
        if not isinstance(node, dict):
            continue
        events.append(_event(
            sequence,
            entity_kind="l2b_node",
            entity_id=str(node.get("uuid") or ""),
            op="top_attention",
            status=str(node.get("kind") or "node"),
            summary=f"{node.get('label') or node.get('uuid') or 'Node'} attention={node.get('attention', 0)}",
        ))

    return events[:24]


def _event(
    sequence: int,
    *,
    entity_kind: str,
    entity_id: str,
    op: str,
    status: str,
    summary: str,
) -> dict[str, Any]:
    return {
        "sequence": sequence,
        "entity_kind": entity_kind,
        "entity_id": entity_id,
        "op": op,
        "status": status,
        "summary": summary,
        "source": "web_console.memory_live_state",
        "created_at": time.time(),
    }


__all__ = ["build_memory_live_state_changes"]
