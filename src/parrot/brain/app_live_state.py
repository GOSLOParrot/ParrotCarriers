"""Read-only live-state aggregation for the App V1 developer console.

The Web console needs to answer one practical debugging question: after a
tool action, which runtime surfaces changed?  This module keeps that view
read-only and bounded while preserving existing ownership boundaries:

* Blackboard remains the lightweight state surface.
* IntentWorkspace remains the staged rich-payload/ref surface.
* RefBinding remains the transient Focus/BBox anchor registry.
* L2-B remains the semantic graph surface.
"""

from __future__ import annotations

import dataclasses
import time
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from parrot.brain import refs as refs_registry
from parrot.brain.intent_workspace import get_intent_workspace
from parrot.brain.l2b_monitor import build_l2b_snapshot
from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.bb_schema import BB_KEYS


@dataclass(frozen=True)
class AppLiveStateSnapshot:
    """Single bounded read model for live App V1 tool-flow debugging."""

    generated_at: float
    sequence: int
    blackboard: dict[str, Any]
    intent_workspace: dict[str, Any]
    refs: dict[str, Any]
    l2b: dict[str, Any]
    tool_artifacts: tuple[dict[str, Any], ...]
    audit: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "sequence": self.sequence,
            "blackboard": self.blackboard,
            "intent_workspace": self.intent_workspace,
            "refs": self.refs,
            "l2b": self.l2b,
            "tool_artifacts": list(self.tool_artifacts),
            "audit": self.audit,
        }


_sequence = 0


def build_app_live_state(*, l2b_limit: int = 80) -> AppLiveStateSnapshot:
    """Build a live, read-only snapshot for the App V1 Web console."""
    global _sequence
    _sequence += 1
    generated_at = time.time()
    blackboard = _blackboard_snapshot()
    intent_workspace = _intent_workspace_snapshot(generated_at=generated_at)
    refs = _refs_snapshot()
    l2b = _l2b_snapshot(limit=l2b_limit)
    tool_artifacts = tuple(_tool_artifacts(
        blackboard=blackboard,
        intent_workspace=intent_workspace,
        refs=refs,
        l2b=l2b,
    ))
    return AppLiveStateSnapshot(
        generated_at=generated_at,
        sequence=_sequence,
        blackboard=blackboard,
        intent_workspace=intent_workspace,
        refs=refs,
        l2b=l2b,
        tool_artifacts=tool_artifacts,
        audit={
            "read_only": True,
            "l2b_write_boundary": "observer/photo, identify_object, ingest runner; console only reads snapshots",
            "blackboard_write_boundary": "tool actions route through AppFirstVersionFacade or EcpEvent observers",
            "intent_workspace_write_boundary": "facade/observer stage refs; console only lists handles",
            "graphiti_write_boundary": "Graphiti console defaults to dry-run outside this live-state snapshot",
        },
    )


def _blackboard_snapshot() -> dict[str, Any]:
    bb = open_bb_client(name="app_live_state.bb", writer=None)
    rows: list[dict[str, Any]] = []
    by_scope: dict[str, list[dict[str, Any]]] = {}
    for key in BB_KEYS:
        exists = True
        try:
            value = bb.get(key.name)
            if value is None:
                exists = False
        except Exception:
            exists = False
            value = None
        row = {
            "key": key.name,
            "scope": key.scope.value,
            "writer": key.writer,
            "type_hint": key.type_hint,
            "event_driven": key.event_driven,
            "exists": exists,
            "value": _jsonable(value) if exists else None,
            "summary": _summary(value) if exists else "not_set",
        }
        rows.append(row)
        by_scope.setdefault(key.scope.value, []).append(row)
    present = [row for row in rows if row["exists"]]
    return {
        "declared_count": len(rows),
        "present_count": len(present),
        "keys": rows,
        "scopes": by_scope,
        "present_keys": present,
    }


def _intent_workspace_snapshot(*, generated_at: float) -> dict[str, Any]:
    ws = get_intent_workspace()
    handles = ws.list_active()
    rows: list[dict[str, Any]] = []
    roles: Counter[str] = Counter()
    kinds: Counter[str] = Counter()
    owners: Counter[str] = Counter()
    for handle in handles:
        meta = handle.metadata
        custom_meta = dict(meta.custom_meta or {})
        role = str(custom_meta.get("role") or "")
        kind = handle.kind.value if handle.kind else ""
        owner = ws.get_owner(handle.ref_id)
        if role:
            roles[role] += 1
        if kind:
            kinds[kind] += 1
        owners[owner or "parent"] += 1
        rows.append({
            "ref_id": handle.ref_id,
            "kind": kind,
            "owner_id": owner,
            "origin": meta.origin,
            "role": role,
            "ui_kind": str(custom_meta.get("ui_kind") or ""),
            "workspace_id": str(custom_meta.get("workspace_id") or ""),
            "title": str(custom_meta.get("title") or custom_meta.get("action") or ""),
            "photo_id": str(custom_meta.get("photo_id") or meta.related_node_uuid or ""),
            "related_node_uuid": meta.related_node_uuid,
            "related_intent_event_id": meta.related_intent_event_id,
            "payload_source": meta.payload_source.value,
            "size_bytes": int(meta.size_bytes or 0),
            "loaded_at": meta.loaded_at,
            "last_accessed_at": meta.last_accessed_at,
            "expires_at": meta.expires_at,
            "expires_in_seconds": (
                round(meta.expires_at - generated_at, 3)
                if meta.expires_at else None
            ),
            "custom_meta": _jsonable(custom_meta),
        })

    pressure = ws.memory_pressure()
    return {
        "ref_count": len(rows),
        "refs": rows,
        "counts_by_role": dict(sorted(roles.items())),
        "counts_by_kind": dict(sorted(kinds.items())),
        "counts_by_owner": dict(sorted(owners.items())),
        "pressure": {
            "backend_usage_bytes": pressure.backend_usage_bytes,
            "backend_total_capacity": pressure.backend_total_capacity,
            "pressure_level": pressure.pressure_level.value,
            "candidate_evictions": list(pressure.candidate_evictions),
        },
    }


def _refs_snapshot() -> dict[str, Any]:
    ref_rows = [_jsonable(ref) for ref in refs_registry.all_refs()]
    by_kind: Counter[str] = Counter()
    resolved_targets: list[dict[str, Any]] = []
    for row in ref_rows:
        if not isinstance(row, dict):
            continue
        kind = str(row.get("kind") or "")
        if kind:
            by_kind[kind] += 1
        if str(row.get("target_kind") or "") == "l2b_node" and row.get("target_id"):
            resolved_targets.append({
                "ref_id": row.get("ref_id"),
                "kind": kind,
                "target_id": row.get("target_id"),
            })
    return {
        "metrics": refs_registry.metrics_snapshot(),
        "refs": ref_rows,
        "counts_by_kind": dict(sorted(by_kind.items())),
        "resolved_l2b_targets": resolved_targets,
    }


def _l2b_snapshot(*, limit: int) -> dict[str, Any]:
    snapshot = build_l2b_snapshot(limit=max(1, min(limit, 200))).as_json()
    by_kind: Counter[str] = Counter()
    top_attention: list[dict[str, Any]] = []
    for node in snapshot.get("nodes", []):
        kind = str(node.get("kind") or "")
        if kind:
            by_kind[kind] += 1
        top_attention.append({
            "uuid": node.get("uuid", ""),
            "label": node.get("label", ""),
            "kind": kind,
            "attention": node.get("attention", 0),
        })
    top_attention.sort(key=lambda item: float(item.get("attention") or 0), reverse=True)
    snapshot["counts_by_kind"] = dict(sorted(by_kind.items()))
    snapshot["top_attention"] = top_attention[:8]
    return snapshot


def _tool_artifacts(
    *,
    blackboard: dict[str, Any],
    intent_workspace: dict[str, Any],
    refs: dict[str, Any],
    l2b: dict[str, Any],
) -> list[dict[str, Any]]:
    bb_by_key = {row["key"]: row for row in blackboard.get("keys", [])}
    iw_refs = list(intent_workspace.get("refs", []))
    ref_rows = list(refs.get("refs", []))
    l2b_nodes = list(l2b.get("nodes", []))

    photo_iw = [
        row for row in iw_refs
        if row.get("kind") == "photo" or str(row.get("role") or "").startswith("photo")
    ]
    photo_nodes = [node for node in l2b_nodes if node.get("kind") == "photo"]
    focus_refs = [row for row in ref_rows if row.get("kind") == "focus"]
    bbox_refs = [row for row in ref_rows if row.get("kind") == "bbox"]
    focus_nodes = _target_nodes(focus_refs, l2b_nodes)
    bbox_nodes = _target_nodes(bbox_refs, l2b_nodes)
    note_refs = [
        row for row in iw_refs
        if row.get("role") in {"nanobot_report", "calendar_draft"}
    ]
    active_workspace = _bb_value(bb_by_key, "global/active_workspace_id")
    hand_hint = _present_keys(bb_by_key, ("session/xrhand_mode", "transient/hand_gesture"))

    return [
        _tool_row(
            tool_id="camera",
            label="Camera / Photo Awareness",
            status="active" if _present_keys(bb_by_key, (
                "session/photo_capture_request",
                "transient/last_photo_event",
                "transient/photo_awareness_notice",
            )) or photo_nodes or photo_iw else "ready",
            blackboard=_present_keys(bb_by_key, (
                "session/camera_mode",
                "session/photo_capture_request",
                "session/photo_awareness_policy",
                "session/photo_awareness_enabled",
                "session/photo_awareness_allows_interrupt",
                "transient/last_photo_event",
                "transient/photo_awareness_notice",
            )),
            intent_refs=photo_iw,
            ref_registry=[],
            l2b_nodes=photo_nodes,
            expectation="capture request lives in Blackboard; preview creates L2-B PhotoNode; Awareness may stage short-lived PHOTO ref",
            scenarios=(
                "preview/off/photo_ready changes session/camera_mode",
                "capture request records session/photo_capture_request without pretending Python owns pixels",
                "photo preview writes transient/last_photo_event and L2-B PHOTO node",
                "Awareness enabled stages IntentWorkspace photo_preview_awareness ref and still blocks interrupt",
            ),
        ),
        _tool_row(
            tool_id="magnifier_focus",
            label="Magnifier Focus",
            status="active" if focus_refs else "ready",
            blackboard=_present_keys(bb_by_key, ("transient/current_attention_hint",)),
            intent_refs=[],
            ref_registry=focus_refs,
            l2b_nodes=focus_nodes,
            expectation="Focus creates session RefBinding; it only affects L2-B after the ref resolves to an L2-B node",
            scenarios=(
                "drag emits local UI movement only",
                "release-on-surface emits focus.anchored and creates a focus RefBinding",
                "close emits focus.released and removes the focus RefBinding",
                "threshold may update transient/current_attention_hint; unresolved refs do not mutate L2-B",
            ),
        ),
        _tool_row(
            tool_id="boundary_box",
            label="BoundaryBox",
            status="active" if bbox_refs else "ready",
            blackboard=_present_keys(bb_by_key, ("transient/current_attention_hint",)),
            intent_refs=[],
            ref_registry=bbox_refs,
            l2b_nodes=bbox_nodes,
            expectation="BBox creates session RefBinding; Unity owns rectangle geometry and Brain owns threshold/ref resolution",
            scenarios=(
                "drag/resize updates local overlay geometry",
                "confirm emits bbox.placed and creates a bbox RefBinding",
                "resize can re-place/update the current box without creating duplicate refs",
                "close emits bbox.removed and removes the bbox RefBinding",
            ),
        ),
        _tool_row(
            tool_id="workdesk_notes",
            label="2D Workdesk / Paper Notes",
            status="active" if active_workspace or note_refs else "idle",
            blackboard=_present_keys(bb_by_key, ("global/active_workspace_id",)),
            intent_refs=note_refs,
            ref_registry=[],
            l2b_nodes=[],
            expectation="Nanobot/calendar outputs become paper-note refs; the 2D workdesk displays refs without owning payload lifecycle",
            scenarios=(
                "Nanobot report stages IntentWorkspace rich_report with role nanobot_report",
                "Calendar action stages IntentWorkspace doc with role calendar_draft",
                "Workdesk switch writes global/active_workspace_id through facade/preset registry",
                "accept/dismiss/archive remains a UI workflow, not direct Graphiti/L2-B write",
            ),
        ),
        _tool_row(
            tool_id="xrhand",
            label="XRHand / Perch Command",
            status="active" if hand_hint else "ready",
            blackboard=hand_hint,
            intent_refs=[],
            ref_registry=[],
            l2b_nodes=[],
            expectation="XRHand is local reflex + app mode state; hand gestures must not switch Scene or write L2-B directly",
            scenarios=(
                "index-middle perch is handled by Unity PerchOnHand local reflex",
                "gesture-select mode can be mirrored through session/xrhand_mode",
                "gesture telemetry may appear as transient/hand_gesture",
                "Brain commands stay EcpCommand/RPC semantic, not a new data-channel topic",
            ),
        ),
        _tool_row(
            tool_id="settings",
            label="Settings / GOSLO Awareness",
            status="active" if _present_keys(bb_by_key, (
                "session/photo_awareness_policy",
                "session/photo_awareness_enabled",
            )) else "ready",
            blackboard=_present_keys(bb_by_key, (
                "session/app_capability_mode",
                "session/photo_awareness_policy",
                "session/photo_awareness_enabled",
                "session/photo_awareness_allows_interrupt",
                "session/photo_awareness_preview_ttl_seconds",
            )),
            intent_refs=[],
            ref_registry=[],
            l2b_nodes=[],
            expectation="Settings writes backend-owned policy keys; no direct memory or graph mutation",
            scenarios=(
                "Awareness off records photos without notifying GOSLO",
                "AWARE_SILENT stages preview context for GOSLO without speech interrupt",
                "AWARE_REACT may allow later-turn reaction but still does not interrupt in App V1",
            ),
        ),
    ]


def _tool_row(
    *,
    tool_id: str,
    label: str,
    status: str,
    blackboard: list[dict[str, Any]],
    intent_refs: list[dict[str, Any]],
    ref_registry: list[dict[str, Any]],
    l2b_nodes: list[dict[str, Any]],
    expectation: str,
    scenarios: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "tool_id": tool_id,
        "label": label,
        "status": status,
        "expectation": expectation,
        "locations": {
            "blackboard": {
                "present": bool(blackboard),
                "keys": blackboard,
            },
            "intent_workspace": {
                "present": bool(intent_refs),
                "refs": intent_refs,
            },
            "ref_registry": {
                "present": bool(ref_registry),
                "refs": ref_registry,
            },
            "l2b": {
                "present": bool(l2b_nodes),
                "nodes": l2b_nodes,
            },
        },
        "scenario_checks": list(scenarios),
    }


def _present_keys(
    bb_by_key: dict[str, dict[str, Any]],
    keys: tuple[str, ...],
) -> list[dict[str, Any]]:
    return [
        bb_by_key[key]
        for key in keys
        if key in bb_by_key and bb_by_key[key].get("exists")
    ]


def _bb_value(bb_by_key: dict[str, dict[str, Any]], key: str) -> Any:
    row = bb_by_key.get(key) or {}
    return row.get("value") if row.get("exists") else None


def _target_nodes(ref_rows: list[dict[str, Any]], l2b_nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    target_ids = {
        str(row.get("target_id") or "")
        for row in ref_rows
        if row.get("target_kind") == "l2b_node" and row.get("target_id")
    }
    return [node for node in l2b_nodes if node.get("uuid") in target_ids]


def _summary(value: Any) -> str:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        if "request_id" in value:
            return f"request:{value.get('request_id')} status={value.get('status', '')}"
        if "photo_id" in value:
            stage = value.get("stage") or value.get("reason") or ""
            return f"photo:{value.get('photo_id')} {stage}"
        if "subject_kind" in value:
            return f"{value.get('subject_kind')}:{value.get('subject_id', '')}"
        keys = ", ".join(list(value.keys())[:4])
        return f"dict[{keys}]"
    if isinstance(value, (list, tuple, set)):
        return f"{type(value).__name__}[{len(value)}]"
    return str(value)


def _jsonable(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Enum):
        return value.value
    if dataclasses.is_dataclass(value):
        return _jsonable(dataclasses.asdict(value))
    if hasattr(value, "model_dump") and callable(value.model_dump):
        return _jsonable(value.model_dump())
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, bytes | bytearray):
        return {"bytes": len(value)}
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_jsonable(v) for v in value]
    if isinstance(value, (str, int, float, bool)):
        if isinstance(value, str) and len(value) > 1000:
            return f"{value[:1000]}...<truncated {len(value) - 1000} chars>"
        return value
    return str(value)


__all__ = ["AppLiveStateSnapshot", "build_app_live_state"]
