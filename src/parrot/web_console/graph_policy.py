"""Web-only L2-B graph policy drafts for CORE-013.

This module is intentionally a policy/read-model layer. It does not mutate the
RustWorkX graph, does not add Unity/App DTO fields, and does not promote
CORE-013 into SSOT. The first job is to make import/subgraph/transform choices
auditable so the UI can show where a source item would land before any real
L1.5 or L2-B write path runs.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
from typing import Any


class ImportDestination(str, Enum):
    """Where a source item should land before/when it reaches L2-B."""

    WORKSPACE_ONLY = "workspace_only"
    INDEX_POINTER = "index_pointer"
    ISOLATED_COMPARTMENT = "isolated_compartment"
    PROMOTE_TO_MAIN_GRAPH = "promote_to_main_graph"
    CONNECT_BY_RULE = "connect_by_rule"


class GraphTransformKind(str, Enum):
    """Operator-visible graph actions that start as dry-run drafts."""

    WRAP_SELECTION = "wrap_selection"
    AGGREGATE_SUBGRAPHS = "aggregate_subgraphs"
    COMPARE_SUBGRAPHS = "compare_subgraphs"
    DRAFT_CROSS_LINKS = "draft_cross_links"
    PROMOTE_TO_MAIN_GRAPH = "promote_to_main_graph"
    SPLIT_SUBGRAPH = "split_subgraph"
    TOMBSTONE_STALE_CLUSTER = "tombstone_stale_cluster"
    SEND_CONTEXT_TO_LLM = "send_context_to_llm"


class GraphDeltaOp(str, Enum):
    """Small operation vocabulary for future changed-since/SSE graph streams."""

    SNAPSHOT = "snapshot"
    UPSERT = "upsert"
    UPDATE = "update"
    DELETE = "delete"
    TOMBSTONE = "tombstone"
    LINK = "link"
    UNLINK = "unlink"
    OVERLAY_CREATE = "overlay_create"
    OVERLAY_UPDATE = "overlay_update"
    TRANSFORM_DRAFT = "transform_draft"
    RECEIPT = "receipt"


class GraphDeltaEntityKind(str, Enum):
    """Entity vocabulary shared by Memory graph deltas and graph-policy drafts."""

    L2B_NODE = "l2b_node"
    L2B_EDGE = "l2b_edge"
    GRAPH_OVERLAY = "graph_overlay"
    L15_BUCKET = "l15_bucket"
    REF_BINDING = "ref_binding"
    GRAPHITI_HIT = "graphiti_hit"
    INTENT_WORKSPACE_REF = "intent_workspace_ref"
    RECEIPT = "receipt"


@dataclass(frozen=True)
class GraphOverlay:
    """Named wrapper over existing graph things.

    The overlay is not a semantic Node and is not a separate RustWorkX graph.
    It is the future place for collapsible subgraphs, isolated compartments,
    and source-pack views.
    """

    overlay_id: str
    label: str
    overlay_kind: str
    member_node_uuids: tuple[str, ...] = ()
    member_ref_ids: tuple[str, ...] = ()
    source_kind: str = ""
    source_ref: str = ""
    membership_policy: str = "explicit_selection"
    collapsed: bool = False
    meta: dict[str, Any] | None = None


@dataclass(frozen=True)
class ImportDestinationPolicy:
    """Dry-run policy decision for one source/import operation."""

    destination: ImportDestination
    source_kind: str
    source_id: str
    workspace_id: str
    subgraph_id: str
    linkage_policy: str
    promotion_policy: str
    write_path: str
    would_mutate_l2b_topology: bool
    would_create_overlay: bool
    would_connect_edges: bool
    reason: str


@dataclass(frozen=True)
class GraphRewriteDraft:
    """Preview of a bounded graph rewrite before any operator apply route."""

    draft_id: str
    transform_kind: str
    affected_node_uuids: tuple[str, ...]
    source_overlay_ids: tuple[str, ...]
    proposed_overlay: GraphOverlay | None = None
    proposed_edges: tuple[dict[str, Any], ...] = ()
    confidence: float = 0.5
    reason: str = ""
    requires_operator: bool = True


@dataclass(frozen=True)
class GraphTransformReceipt:
    """Receipt payload for graph policy drafts."""

    receipt_kind: str
    core_candidate: str
    draft: GraphRewriteDraft | None
    policy: ImportDestinationPolicy | None
    audit: dict[str, Any]


@dataclass(frozen=True)
class GraphDeltaEvent:
    """Candidate delta row for future changed-since/SSE work.

    This is deliberately renderer-agnostic: React Flow, React-Force-Graph, and
    a future dense graph engine can all consume stable business ids plus a
    small patch. It is not a Unity/App DTO and must not contain source secrets
    or raw image/file payloads.
    """

    sequence: int
    entity_kind: str
    entity_id: str
    op: str
    graph_scope: str = "memory_graph"
    event_id: str = ""
    overlay_id: str = ""
    source_id: str = ""
    target_id: str = ""
    edge_kind: str = ""
    trace_id: str = ""
    receipt_id: str = ""
    source: str = "web_console.graph_policy"
    summary: str = ""
    patch: dict[str, Any] | None = None
    before_ref: str = ""
    after_ref: str = ""
    created_at: float = 0.0
    redacted: bool = True


def draft_import_destination(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Draft where a source item would land.

    This route answers the operator question "does this import stay in the
    workspace, become a pointer, become an isolated subgraph, or connect into
    the main graph?" It returns the policy and any proposed Edge/overlay data,
    but never calls L1.5 or L2-B.
    """

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    destination = _parse_enum(
        ImportDestination,
        body.get("destination") or body.get("graph_view_mode") or ImportDestination.WORKSPACE_ONLY.value,
    )
    if destination is None:
        return _receipt(
            action="l2b.graph_policy.import_draft",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "error": "invalid_import_destination",
                "valid_destinations": [item.value for item in ImportDestination],
                "core_candidate": "CORE-013",
            },
        )

    node_uuids = _string_tuple(body.get("node_uuids") or body.get("nodes"))
    ref_ids = _string_tuple(body.get("ref_ids") or body.get("refs"))
    item_ids = _string_tuple(body.get("item_ids") or body.get("items"))
    source_kind = _clean_token(body.get("source_kind") or body.get("source") or "manual")
    source_id = str(body.get("source_id") or body.get("source_ref") or "").strip()
    workspace_id = _clean_token(body.get("workspace_id") or "default")
    subgraph_id = _clean_token(body.get("subgraph_id") or "")
    subgraph_label = str(body.get("subgraph_label") or body.get("label") or "").strip()
    linkage_policy = _clean_token(body.get("linkage_policy") or _default_linkage_policy(destination))
    promotion_policy = _clean_token(body.get("promotion_policy") or _default_promotion_policy(destination))
    edges = _draft_edges(body, node_uuids=node_uuids, destination=destination)
    overlay = _overlay_for_import(
        destination=destination,
        subgraph_id=subgraph_id,
        subgraph_label=subgraph_label,
        source_kind=source_kind,
        source_id=source_id,
        node_uuids=node_uuids,
        ref_ids=ref_ids,
        item_ids=item_ids,
    )
    policy = ImportDestinationPolicy(
        destination=destination,
        source_kind=source_kind,
        source_id=source_id,
        workspace_id=workspace_id,
        subgraph_id=overlay.overlay_id if overlay else subgraph_id,
        linkage_policy=linkage_policy,
        promotion_policy=promotion_policy,
        write_path=_write_path_for_destination(destination),
        would_mutate_l2b_topology=destination
        in {
            ImportDestination.INDEX_POINTER,
            ImportDestination.ISOLATED_COMPARTMENT,
            ImportDestination.PROMOTE_TO_MAIN_GRAPH,
            ImportDestination.CONNECT_BY_RULE,
        },
        would_create_overlay=overlay is not None,
        would_connect_edges=bool(edges),
        reason=_reason_for_destination(destination),
    )
    draft = GraphRewriteDraft(
        draft_id=_make_id("graph_import"),
        transform_kind="import_destination",
        affected_node_uuids=node_uuids,
        source_overlay_ids=(overlay.overlay_id,) if overlay else (),
        proposed_overlay=overlay,
        proposed_edges=edges,
        confidence=_body_float(body.get("confidence"), 0.65),
        reason=policy.reason,
    )
    receipt = GraphTransformReceipt(
        receipt_kind="import_destination",
        core_candidate="CORE-013",
        draft=draft,
        policy=policy,
        audit=_core013_audit(),
    )
    return _receipt(
        action="l2b.graph_policy.import_draft",
        success=True,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data={
            **_jsonable(receipt),
            "operator_required_for_apply": True,
            "apply_route": "",
            "shared_status": "candidate_only",
        },
    )


def draft_subgraph_overlay(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Draft a foldable subgraph/cluster overlay without changing L2-B."""

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    node_uuids = _string_tuple(body.get("node_uuids") or body.get("nodes"))
    ref_ids = _string_tuple(body.get("ref_ids") or body.get("refs"))
    overlay = GraphOverlay(
        overlay_id=_clean_token(body.get("subgraph_id") or body.get("overlay_id") or _make_id("subgraph")),
        label=str(body.get("label") or "L2-B subgraph").strip()[:80],
        overlay_kind=_clean_token(body.get("overlay_kind") or "foldable_subgraph"),
        member_node_uuids=node_uuids,
        member_ref_ids=ref_ids,
        source_kind=_clean_token(body.get("source_kind") or "manual"),
        source_ref=str(body.get("source_ref") or body.get("source_id") or "").strip(),
        membership_policy=_clean_token(body.get("membership_policy") or "explicit_selection"),
        collapsed=_body_bool(body.get("collapsed"), False),
        meta=_dict_or_empty(body.get("meta")),
    )
    draft = GraphRewriteDraft(
        draft_id=_make_id("overlay"),
        transform_kind="subgraph_overlay",
        affected_node_uuids=node_uuids,
        source_overlay_ids=(overlay.overlay_id,),
        proposed_overlay=overlay,
        confidence=_body_float(body.get("confidence"), 0.7),
        reason="Overlay wraps selection for visualization and review; it is not a semantic Node.",
    )
    return _receipt(
        action="l2b.subgraph.draft",
        success=True,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data={
            "core_candidate": "CORE-013",
            "draft": _jsonable(draft),
            "overlay": _jsonable(overlay),
            "operator_required_for_apply": True,
            "apply_route": "",
            "audit": _core013_audit(),
        },
    )


def draft_graph_transform(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Draft a bounded graph transform or LLM-context alternative."""

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    transform_kind = _parse_enum(
        GraphTransformKind,
        body.get("transform_kind") or body.get("op") or GraphTransformKind.WRAP_SELECTION.value,
    )
    if transform_kind is None:
        return _receipt(
            action="l2b.transform.draft",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "error": "invalid_transform_kind",
                "valid_transform_kinds": [item.value for item in GraphTransformKind],
                "core_candidate": "CORE-013",
            },
        )

    node_uuids = _string_tuple(body.get("node_uuids") or body.get("nodes"))
    overlay_ids = _string_tuple(body.get("subgraph_ids") or body.get("overlay_ids"))
    if transform_kind in {GraphTransformKind.WRAP_SELECTION, GraphTransformKind.DRAFT_CROSS_LINKS} and not node_uuids:
        return _receipt(
            action="l2b.transform.draft",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "error": "missing_node_selection",
                "transform_kind": transform_kind.value,
                "core_candidate": "CORE-013",
            },
        )

    proposed_overlay = None
    if transform_kind is GraphTransformKind.WRAP_SELECTION:
        proposed_overlay = GraphOverlay(
            overlay_id=_make_id("wrapped"),
            label=str(body.get("label") or "Wrapped selection").strip()[:80],
            overlay_kind="foldable_subgraph",
            member_node_uuids=node_uuids,
            source_kind="manual_transform",
            membership_policy="explicit_selection",
            collapsed=False,
            meta={"transform_kind": transform_kind.value},
        )
    edges = _draft_edges(body, node_uuids=node_uuids, destination=ImportDestination.CONNECT_BY_RULE)
    if transform_kind is GraphTransformKind.SEND_CONTEXT_TO_LLM:
        edges = ()
    draft = GraphRewriteDraft(
        draft_id=_make_id("transform"),
        transform_kind=transform_kind.value,
        affected_node_uuids=node_uuids,
        source_overlay_ids=overlay_ids,
        proposed_overlay=proposed_overlay,
        proposed_edges=edges,
        confidence=_body_float(body.get("confidence"), 0.55),
        reason=_reason_for_transform(transform_kind),
        requires_operator=transform_kind is not GraphTransformKind.SEND_CONTEXT_TO_LLM,
    )
    return _receipt(
        action="l2b.transform.draft",
        success=True,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data={
            "core_candidate": "CORE-013",
            "draft": _jsonable(draft),
            "operator_required_for_apply": draft.requires_operator,
            "apply_route": "",
            "llm_context_alternative": transform_kind is not GraphTransformKind.SEND_CONTEXT_TO_LLM,
            "audit": _core013_audit(),
        },
    )


def graph_health_snapshot() -> dict[str, Any]:
    """Return read-only graph health metrics for operator planning."""

    try:
        from parrot.dsg.l2b.clustering import get_cluster_strategy
        from parrot.dsg.l2b_graph import get_l2b_graph

        graph = get_l2b_graph()
        nodes = graph.all_nodes()
        edges = graph.all_edges()
        connected = {
            node.uuid
            for src, dst, _edge in edges
            for node in (src, dst)
        }
        cluster_result = get_cluster_strategy().detect(graph)
        kind_counts: dict[str, int] = {}
        bucket_counts: dict[str, int] = {}
        source_counts: dict[str, int] = {}
        for node in nodes:
            kind = getattr(getattr(node, "kind", ""), "value", str(getattr(node, "kind", "")))
            bucket = str(getattr(node, "bucket_id", "") or "main")
            source = str(getattr(node, "source", "") or "unspecified")
            kind_counts[kind] = kind_counts.get(kind, 0) + 1
            bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
            source_counts[source] = source_counts.get(source, 0) + 1
        orphan_uuids = sorted(
            str(node.uuid)
            for node in nodes
            if str(getattr(node, "uuid", "")) not in connected
        )
        return {
            "success": True,
            "action": "l2b.analysis.health",
            "read_only": True,
            "core_candidate": "CORE-013",
            "node_count": len(nodes),
            "edge_count": len(edges),
            "orphan_count": len(orphan_uuids),
            "orphan_uuids": orphan_uuids[:80],
            "wcc_count": len(cluster_result.clusters),
            "largest_wcc_size": cluster_result.largest().size() if cluster_result.largest() else 0,
            "kind_counts": kind_counts,
            "bucket_counts": bucket_counts,
            "source_counts": source_counts,
            "analysis_tier": "online_interaction_safe",
            "audit": _core013_audit(),
        }
    except Exception as exc:
        return {
            "success": False,
            "action": "l2b.analysis.health",
            "read_only": True,
            "core_candidate": "CORE-013",
            "error": f"{type(exc).__name__}: {exc}",
            "audit": _core013_audit(),
        }


def _overlay_for_import(
    *,
    destination: ImportDestination,
    subgraph_id: str,
    subgraph_label: str,
    source_kind: str,
    source_id: str,
    node_uuids: tuple[str, ...],
    ref_ids: tuple[str, ...],
    item_ids: tuple[str, ...],
) -> GraphOverlay | None:
    if destination not in {ImportDestination.ISOLATED_COMPARTMENT, ImportDestination.CONNECT_BY_RULE} and not subgraph_id:
        return None
    overlay_kind = (
        "isolated_compartment"
        if destination is ImportDestination.ISOLATED_COMPARTMENT
        else "foldable_subgraph"
    )
    return GraphOverlay(
        overlay_id=subgraph_id or _make_id("subgraph"),
        label=(subgraph_label or f"{source_kind} import").strip()[:80],
        overlay_kind=overlay_kind,
        member_node_uuids=node_uuids,
        member_ref_ids=ref_ids or item_ids,
        source_kind=source_kind,
        source_ref=source_id,
        membership_policy="import_source_selection",
        collapsed=False,
        meta={"destination": destination.value},
    )


def _draft_edges(
    body: dict[str, Any],
    *,
    node_uuids: tuple[str, ...],
    destination: ImportDestination,
) -> tuple[dict[str, Any], ...]:
    raw_edges = body.get("proposed_edges") or body.get("edge_drafts") or []
    edges: list[dict[str, Any]] = []
    if isinstance(raw_edges, list):
        for raw in raw_edges[:24]:
            if not isinstance(raw, dict):
                continue
            source = str(raw.get("source") or raw.get("from_uuid") or "").strip()
            target = str(raw.get("target") or raw.get("to_uuid") or "").strip()
            if not source or not target or source == target:
                continue
            edges.append(_edge_row(raw, source=source, target=target))
    if not edges and destination is ImportDestination.CONNECT_BY_RULE and len(node_uuids) >= 2:
        edge_kind = str(body.get("edge_kind") or "associated_with")
        for source, target in zip(node_uuids, node_uuids[1:]):
            if source != target:
                edges.append(_edge_row(body, source=source, target=target, kind=edge_kind))
    return tuple(edges)


def _edge_row(
    raw: dict[str, Any],
    *,
    source: str,
    target: str,
    kind: str | None = None,
) -> dict[str, Any]:
    meta = _dict_or_empty(raw.get("meta"))
    for key in (
        "source_graphiti_uuid",
        "target_graphiti_uuid",
        "hit_graphiti_uuid",
        "label",
        "fact",
        "write_policy",
    ):
        value = raw.get(key)
        if value not in (None, ""):
            meta[key] = value
    return {
        "source": source,
        "target": target,
        "kind": _clean_token(kind or raw.get("kind") or raw.get("edge_kind") or "associated_with"),
        "strength": max(0.0, min(_body_float(raw.get("strength"), 0.5), 1.0)),
        "edge_source": _clean_token(raw.get("edge_source") or raw.get("source_kind") or "web_console.graph_policy"),
        "meta": meta,
        "status": "draft",
    }


def _write_path_for_destination(destination: ImportDestination) -> str:
    if destination is ImportDestination.WORKSPACE_ONLY:
        return "IntentWorkspace/Ref staging only; no L2-B topology mutation"
    if destination is ImportDestination.INDEX_POINTER:
        return "L15Pool.admit(pointer Observation) + RefBinding"
    if destination is ImportDestination.ISOLATED_COMPARTMENT:
        return "L15Pool.admit(...) + GraphOverlay(isolated_compartment)"
    if destination is ImportDestination.PROMOTE_TO_MAIN_GRAPH:
        return "L15Pool.admit(...) into main graph + reviewed Edge drafts"
    return "L15Pool.admit(...) + bounded connect-by-rule Edge drafts"


def _reason_for_destination(destination: ImportDestination) -> str:
    reasons = {
        ImportDestination.WORKSPACE_ONLY: "Keep rich payload in IntentWorkspace until it proves useful for L2-B.",
        ImportDestination.INDEX_POINTER: "Create a lightweight index pointer while preserving heavy payload elsewhere.",
        ImportDestination.ISOLATED_COMPARTMENT: "Keep source-pack topology reviewable before main-graph promotion.",
        ImportDestination.PROMOTE_TO_MAIN_GRAPH: "Operator chose direct promotion into the canonical L2-B graph.",
        ImportDestination.CONNECT_BY_RULE: "Draft only bounded local links; do not run whole-graph rewrites.",
    }
    return reasons[destination]


def _reason_for_transform(kind: GraphTransformKind) -> str:
    reasons = {
        GraphTransformKind.WRAP_SELECTION: "Wrap selected Nodes as a collapsible overlay without changing NodeKind.",
        GraphTransformKind.AGGREGATE_SUBGRAPHS: "Compare/aggregate two overlays before deciding whether any topology changes are useful.",
        GraphTransformKind.COMPARE_SUBGRAPHS: "Read-only structural comparison; prefer LLM synthesis for broad semantics.",
        GraphTransformKind.DRAFT_CROSS_LINKS: "Draft cross-subgraph Edges for operator review.",
        GraphTransformKind.PROMOTE_TO_MAIN_GRAPH: "Preview promotion from an isolated view into the canonical graph.",
        GraphTransformKind.SPLIT_SUBGRAPH: "Preview splitting stale or mixed clusters into smaller overlays.",
        GraphTransformKind.TOMBSTONE_STALE_CLUSTER: "Preview tombstone/ghost lifecycle changes; no silent delete.",
        GraphTransformKind.SEND_CONTEXT_TO_LLM: "Use selected graph context for synthesis without mutating topology.",
    }
    return reasons[kind]


def _default_linkage_policy(destination: ImportDestination) -> str:
    if destination is ImportDestination.CONNECT_BY_RULE:
        return "bounded_local_rules"
    if destination is ImportDestination.PROMOTE_TO_MAIN_GRAPH:
        return "operator_reviewed_edges"
    return "no_automatic_edges"


def _default_promotion_policy(destination: ImportDestination) -> str:
    if destination is ImportDestination.WORKSPACE_ONLY:
        return "defer_until_review"
    if destination is ImportDestination.ISOLATED_COMPARTMENT:
        return "operator_promote_later"
    return "operator_draft_first"


def _core013_audit() -> dict[str, Any]:
    return {
        "web_only": True,
        "core_candidate": "CORE-013",
        "app_dto_pollution": False,
        "unity_dto_pollution": False,
        "default_mode": "dry_run",
        "ssot_status": "candidate_only",
    }


def _receipt(
    *,
    action: str,
    success: bool,
    dry_run: bool,
    operator_mode: bool,
    data: dict[str, Any],
) -> dict[str, Any]:
    return {
        "success": success,
        "action": action,
        "dry_run": dry_run,
        "operator_mode": operator_mode,
        "receipt": {
            "receipt_id": f"web_{uuid.uuid4().hex[:12]}",
            "created_at": time.time(),
            "audit_level": "operator" if operator_mode else "draft",
            "secret_redacted": True,
        },
        "data": _jsonable(data),
    }


def _make_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def _parse_enum(enum_cls: Any, raw: Any) -> Any | None:
    value = str(raw or "").strip().lower()
    try:
        return enum_cls(value)
    except Exception:
        return None


def _body_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _body_float(value: Any, default: float) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _string_tuple(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        values: Any = [value]
    else:
        values = value
    if not isinstance(values, (list, tuple, set)):
        return ()
    seen: set[str] = set()
    out: list[str] = []
    for item in values:
        text = str(item or "").strip()
        if text and text not in seen:
            seen.add(text)
            out.append(text[:160])
    return tuple(out)


def _clean_token(value: Any) -> str:
    text = str(value or "").strip().lower().replace(" ", "_")
    return "".join(ch for ch in text if ch.isalnum() or ch in "._:-")[:96]


def _dict_or_empty(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _jsonable(getattr(value, field.name))
            for field in fields(value)
            if not field.name.startswith("_")
        }
    if isinstance(value, dict):
        return {str(_jsonable(key)): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, set):
        return sorted(_jsonable(item) for item in value)
    return value


__all__ = [
    "GraphDeltaEvent",
    "GraphDeltaEntityKind",
    "GraphDeltaOp",
    "GraphOverlay",
    "GraphRewriteDraft",
    "GraphTransformKind",
    "GraphTransformReceipt",
    "ImportDestination",
    "ImportDestinationPolicy",
    "draft_graph_transform",
    "draft_import_destination",
    "draft_subgraph_overlay",
    "graph_health_snapshot",
]
