"""Web-only L2-B graph policy drafts for CORE-013.

This module is intentionally a policy/read-model layer. It does not mutate the
RustWorkX graph, does not add Unity/App DTO fields, and does not promote
CORE-013 into SSOT. The first job is to make import/subgraph/transform choices
auditable so the UI can show where a source item would land before any real
L1.5 or L2-B write path runs.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
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
    GRAPHITI_BUNDLE_PROJECTION = "graphiti_bundle_projection"
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


def live_subgraph_context(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Read a bounded live L2-B subgraph context for operator inspection.

    This is the first true-connection companion to the preview overlay route:
    it reads the session L2-B RustWorkX graph through ``get_l2b_graph()``,
    expands by stable UUIDs only, and returns a draft overlay plus compact
    node/edge rows. It never exposes RustWorkX integer indices and never writes
    topology.
    """

    body = payload or {}
    if _remote_l2b_base_url() and not _body_bool(body.get("_remote_proxy_disable"), False):
        remote_payload = dict(body)
        remote_payload["_remote_proxy_disable"] = True
        remote = _remote_l2b_request("/api/l2b/subgraphs/context", payload=remote_payload)
        if isinstance(remote, dict) and remote.get("action"):
            remote_data = dict(remote.get("data") or {})
            remote_data["remote_proxy"] = {
                "enabled": bool(remote.get("success")),
                "base_url": _remote_l2b_base_url(),
                "reason": "web_console_l2b_remote_url_configured",
                "error": remote.get("error") or "",
            }
            remote["data"] = remote_data
            return remote

    requested_dry_run = _body_bool(body.get("dry_run"), True)
    requested_operator_mode = _body_bool(body.get("operator_mode"), False)
    node_uuids = _string_tuple(body.get("node_uuids") or body.get("nodes"))
    depth = _body_int(body.get("depth") or body.get("hops"), default=1, minimum=0, maximum=4)
    include_clusters = _body_bool(body.get("include_clusters"), True)
    label = str(body.get("label") or "Live L2-B context").strip()[:80]
    if not node_uuids:
        return _receipt(
            action="l2b.subgraph.context",
            success=False,
            dry_run=True,
            operator_mode=False,
            data={
                "error": "missing_node_selection",
                "core_candidate": "CORE-013",
                "requested_execution": {
                    "dry_run": requested_dry_run,
                    "operator_mode": requested_operator_mode,
                    "ignored_for_context": True,
                },
                "read_only": True,
                "audit": _core013_audit(),
            },
        )

    try:
        from parrot.dsg.l2b.clustering import get_cluster_strategy
        from parrot.dsg.l2b_graph import get_l2b_graph

        graph = get_l2b_graph()
        all_nodes = graph.all_nodes()
        all_edges = graph.all_edges()
    except Exception as exc:
        return _receipt(
            action="l2b.subgraph.context",
            success=False,
            dry_run=True,
            operator_mode=False,
            data={
                "error": "l2b_graph_unavailable",
                "message": str(exc)[:240],
                "core_candidate": "CORE-013",
                "requested_execution": {
                    "dry_run": requested_dry_run,
                    "operator_mode": requested_operator_mode,
                    "ignored_for_context": True,
                },
                "read_only": True,
                "audit": _core013_audit(),
            },
        )

    nodes_by_uuid = {str(node.uuid): node for node in all_nodes if str(getattr(node, "uuid", "") or "")}
    selected = tuple(uuid for uuid in node_uuids if uuid in nodes_by_uuid)
    missing = tuple(uuid for uuid in node_uuids if uuid not in nodes_by_uuid)
    missing_graphiti_preview_uuids = tuple(
        uuid for uuid in missing if uuid.startswith("graphiti:")
    )
    context_lookup_hint = (
        "graphiti_preview_uuid_requires_l2b_materialization"
        if missing_graphiti_preview_uuids
        else ""
    )
    adjacency: dict[str, set[str]] = {}
    for src, dst, _edge in all_edges:
        src_uuid = str(getattr(src, "uuid", "") or "")
        dst_uuid = str(getattr(dst, "uuid", "") or "")
        if not src_uuid or not dst_uuid:
            continue
        adjacency.setdefault(src_uuid, set()).add(dst_uuid)
        adjacency.setdefault(dst_uuid, set()).add(src_uuid)

    included: set[str] = set(selected)
    frontier: set[str] = set(selected)
    for _hop in range(depth):
        next_frontier = {
            neighbor
            for uuid_value in frontier
            for neighbor in adjacency.get(uuid_value, set())
            if neighbor not in included
        }
        if not next_frontier:
            break
        included.update(next_frontier)
        frontier = next_frontier

    ordered_node_uuids = [
        *selected,
        *sorted(uuid_value for uuid_value in included if uuid_value not in set(selected)),
    ]
    edge_rows = [
        _semantic_edge_row(src, dst, edge)
        for src, dst, edge in all_edges
        if str(getattr(src, "uuid", "") or "") in included
        and str(getattr(dst, "uuid", "") or "") in included
    ]
    node_rows = [_semantic_node_row(nodes_by_uuid[uuid_value]) for uuid_value in ordered_node_uuids]
    cluster_rows: list[dict[str, Any]] = []
    if include_clusters and selected:
        selected_set = set(selected)
        try:
            cluster_result = get_cluster_strategy().detect(graph)
            for cluster in cluster_result.clusters:
                member_uuids = tuple(str(uuid_value) for uuid_value in cluster.member_uuids)
                selected_members = tuple(uuid_value for uuid_value in member_uuids if uuid_value in selected_set)
                if not selected_members:
                    continue
                cluster_rows.append({
                    "cluster_id": cluster.cluster_id,
                    "axis": cluster.axis,
                    "size": len(member_uuids),
                    "member_uuids": member_uuids,
                    "selected_member_uuids": selected_members,
                })
        except Exception as exc:
            cluster_rows.append({
                "cluster_id": "cluster_error",
                "axis": "wcc",
                "error": str(exc)[:240],
                "member_uuids": (),
                "selected_member_uuids": selected,
            })

    member_ref_ids = tuple(sorted({
        ref_id
        for edge in edge_rows
        for ref_id in _string_tuple(edge.get("ref_ids"))
    }))
    overlay = GraphOverlay(
        overlay_id=_clean_token(body.get("subgraph_id") or body.get("overlay_id") or _make_id("live_subgraph")),
        label=label or "Live L2-B context",
        overlay_kind="live_l2b_ego_subgraph",
        member_node_uuids=tuple(ordered_node_uuids),
        member_ref_ids=member_ref_ids,
        source_kind="l2b_live_state",
        source_ref=",".join(selected[:4]),
        membership_policy=f"selected_plus_ego_depth_{depth}",
        collapsed=False,
        meta={
            "depth": depth,
            "selected_count": len(selected),
            "missing_count": len(missing),
            "cluster_count": len(cluster_rows),
        },
    )
    return _receipt(
        action="l2b.subgraph.context",
        success=bool(selected),
        dry_run=True,
        operator_mode=False,
        data={
            "core_candidate": "CORE-013",
            "selected_node_uuids": selected,
            "missing_node_uuids": missing,
            "missing_graphiti_preview_node_uuids": missing_graphiti_preview_uuids,
            "context_lookup_hint": context_lookup_hint,
            "depth": depth,
            "depth_cap": 4,
            "nodes": node_rows,
            "edges": edge_rows,
            "clusters": cluster_rows,
            "overlay": _jsonable(overlay),
            "read_only": True,
            "operator_required_for_apply": True,
            "apply_route": "",
            "requested_execution": {
                "dry_run": requested_dry_run,
                "operator_mode": requested_operator_mode,
                "ignored_for_context": True,
            },
            "true_connection": {
                "used_live_l2b_graph": True,
                "source": "parrot.dsg.l2b_graph.get_l2b_graph",
                "read_only": True,
                "direct_l2b_write": False,
                "direct_graphiti_query": False,
                "rwx_idx_exposed": False,
                "node_count_before": len(all_nodes),
                "edge_count_before": len(all_edges),
            },
            "policies": {
                "uuid_identity_only": True,
                "rwx_index_policy": "RustWorkX indices stay private and ephemeral.",
                "graphiti_raw_policy": "Graphiti UUIDs/raw metadata already present on L2-B payloads are returned; this route does not re-query Graphiti.",
                "search_policy": "Use Graphiti /api/graphiti/subgraph/search before import, then use this live L2-B context route after materialization.",
                "write_policy": "No topology writes; persistent overlay/apply is a future operator-reviewed route.",
                "materialized_l2b_uuid_required": True,
                "graphiti_preview_uuid_policy": "UUIDs with graphiti: prefix are import-plan projection pointers, not live L2-B node UUIDs until an operator-reviewed materialization path writes them.",
            },
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
    if transform_kind is GraphTransformKind.GRAPHITI_BUNDLE_PROJECTION:
        return draft_graphiti_bundle_projection({**body, "transform_kind": transform_kind.value})

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


def draft_graphiti_bundle_projection(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Draft a Graphiti bundle -> L2-B/RustWorkX projection.

    This is the bridge preview for the user's "do not break Graphiti data"
    requirement: Graphiti remains the provenance graph, while L2-B receives a
    pointer/topology proposal with raw Graphiti records still attached.
    """

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    bundle = _dict_or_empty(body.get("graphiti_bundle") or body.get("bundle"))
    if not bundle:
        return _receipt(
            action="l2b.transform.draft",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "error": "missing_graphiti_bundle",
                "transform_kind": GraphTransformKind.GRAPHITI_BUNDLE_PROJECTION.value,
                "core_candidate": "CORE-013",
                "shared_status": "candidate_only",
            },
        )

    partition = str(body.get("partition") or bundle.get("partition") or "goslo").strip() or "goslo"
    query = str(body.get("query") or bundle.get("query") or "").strip()
    sections = _dict_or_empty(bundle.get("sections"))
    facts = _record_rows(sections.get("facts"))
    entities = _record_rows(sections.get("entities"))
    episodes = _record_rows(sections.get("episodes"))
    communities = _record_rows(sections.get("communities"))
    l2b_nodes = _graphiti_bundle_l2b_nodes(
        partition=partition,
        entities=entities,
        episodes=episodes,
        communities=communities,
    )
    fact_pointers, l2b_edges, episode_links, issues = _graphiti_bundle_l2b_edges(
        partition=partition,
        facts=facts,
        l2b_nodes=l2b_nodes,
    )
    overlay = GraphOverlay(
        overlay_id=_clean_token(body.get("subgraph_id") or body.get("overlay_id") or _make_id("graphiti_bundle")),
        label=str(body.get("label") or query or "Graphiti bundle projection").strip()[:80],
        overlay_kind="graphiti_bundle_projection",
        member_node_uuids=tuple(str(row.get("uuid") or "") for row in l2b_nodes if row.get("uuid")),
        member_ref_ids=tuple(str(row.get("ref_id") or "") for row in fact_pointers if row.get("ref_id")),
        source_kind="graphiti_bundle",
        source_ref=str(bundle.get("query") or query or partition),
        membership_policy="graphiti_bundle_sections",
        collapsed=False,
        meta={
            "partition": partition,
            "bundle_kind": str(bundle.get("bundle_kind") or ""),
            "transform_kind": GraphTransformKind.GRAPHITI_BUNDLE_PROJECTION.value,
        },
    )
    topology = _rustworkx_projection_preview(l2b_nodes, [*l2b_edges, *episode_links])
    success = bool(facts or entities or episodes or communities)
    return _receipt(
        action="l2b.transform.draft",
        success=success,
        dry_run=True,
        operator_mode=False,
        data={
            "core_candidate": "CORE-013",
            "core_candidates": ["CORE-013", "CORE-015"],
            "shared_status": "candidate_only",
            "projection_kind": "graphiti_bundle_to_l2b_rustworkx_preview",
            "transform_kind": GraphTransformKind.GRAPHITI_BUNDLE_PROJECTION.value,
            "partition": partition,
            "query": query,
            "source_bundle_kind": str(bundle.get("bundle_kind") or ""),
            "section_counts": {
                "facts": len(facts),
                "entities": len(entities),
                "episodes": len(episodes),
                "communities": len(communities),
            },
            "l2b_nodes": l2b_nodes,
            "l2b_edges": l2b_edges,
            "episode_links": episode_links,
            "fact_pointers": fact_pointers,
            "overlay": _jsonable(overlay),
            "rustworkx_preview": topology,
            "issues": issues,
            "policies": {
                "preview_only": True,
                "preserve_raw_graphiti": True,
                "direct_graphiti_write": False,
                "direct_falkordb_write": False,
                "direct_l2b_write": False,
                "app_dto": False,
                "node_identity_policy": "Graphiti UUID is carried as source identity; durable L2-B UUID binding still belongs to IdentityRefIndex/CORE-015.",
                "rwx_index_policy": "RustWorkX indices in this receipt are ephemeral preview handles and must not be persisted.",
                "edge_materialization_policy": "Graphiti facts stay raw in metadata; real L2-B edges require reviewed endpoint UUID resolution.",
            },
            "operator_required_for_apply": True,
            "apply_route": "",
            "audit": _core013_audit(),
        },
    )


def graph_health_snapshot() -> dict[str, Any]:
    """Return read-only graph health metrics for operator planning."""

    if _remote_l2b_base_url() and os.getenv("PARROT_WEB_CONSOLE_L2B_HEALTH_PROXY", "0").strip().lower() in {"1", "true", "yes", "on"}:
        remote = _remote_l2b_request("/api/l2b/analysis/health")
        if isinstance(remote, dict) and remote.get("action"):
            remote["remote_proxy"] = {
                "enabled": bool(remote.get("success")),
                "base_url": _remote_l2b_base_url(),
                "reason": "web_console_l2b_health_proxy_enabled",
                "error": remote.get("error") or "",
            }
            return remote

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


def _record_rows(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [row for row in value if isinstance(row, dict)]


def _remote_l2b_base_url() -> str:
    raw = (
        os.getenv("PARROT_WEB_CONSOLE_L2B_URL")
        or os.getenv("PARROT_WEB_CONSOLE_GRAPHITI_URL")
        or os.getenv("PARROT_GRAPHITI_REMOTE_URL")
        or ""
    )
    return str(raw).strip().rstrip("/")


def _remote_l2b_timeout_s() -> float:
    raw = (
        os.getenv("PARROT_WEB_CONSOLE_L2B_TIMEOUT_S")
        or os.getenv("PARROT_WEB_CONSOLE_GRAPHITI_TIMEOUT_S")
        or os.getenv("PARROT_GRAPHITI_REMOTE_TIMEOUT_S")
        or "30"
    )
    try:
        parsed = float(raw)
    except (TypeError, ValueError):
        parsed = 30.0
    return max(0.5, min(parsed, 300.0))


def _remote_l2b_request(
    path: str,
    *,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    base_url = _remote_l2b_base_url()
    if not base_url:
        return {"success": False, "action": "remote.l2b.proxy", "error": "missing_remote_url"}
    url = f"{base_url}/{path.lstrip('/')}"
    data: bytes | None = None
    headers = {"Accept": "application/json"}
    headers.update(_remote_l2b_auth_headers())
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method="POST" if payload is not None else "GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=_remote_l2b_timeout_s()) as response:
            raw = response.read().decode("utf-8", errors="replace")
        parsed = json.loads(raw) if raw else {}
        if isinstance(parsed, dict):
            return parsed
        return {"success": False, "action": "remote.l2b.proxy", "error": "non_object_json", "raw": parsed}
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        return {
            "success": False,
            "action": "remote.l2b.proxy",
            "error": f"{type(exc).__name__}: {exc}",
            "url": url,
        }


def _remote_l2b_auth_headers() -> dict[str, str]:
    """Return server-side auth headers for app-monitor L2-B proxy calls."""

    secret = (
        os.getenv("PARROT_WEB_CONSOLE_L2B_SECRET")
        or os.getenv("PARROT_WEB_CONSOLE_GRAPHITI_SECRET")
        or os.getenv("PARROT_GRAPHITI_REMOTE_SECRET")
        or os.getenv("PARROT_APP_MONITOR_SECRET")
        or ""
    ).strip()
    if not secret:
        return {}
    return {"Authorization": f"Bearer {secret}"}


def _graphiti_bundle_l2b_nodes(
    *,
    partition: str,
    entities: list[dict[str, Any]],
    episodes: list[dict[str, Any]],
    communities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in entities:
        _append_graphiti_l2b_node(
            nodes,
            seen,
            partition=partition,
            graphiti_kind="entity",
            node_kind=_graphiti_entity_node_kind(row),
            row=row,
        )
    for row in episodes:
        _append_graphiti_l2b_node(
            nodes,
            seen,
            partition=partition,
            graphiti_kind="episode",
            node_kind="event",
            row=row,
        )
    for row in communities:
        _append_graphiti_l2b_node(
            nodes,
            seen,
            partition=partition,
            graphiti_kind="community",
            node_kind="zone",
            row=row,
        )
    return nodes


def _append_graphiti_l2b_node(
    nodes: list[dict[str, Any]],
    seen: set[str],
    *,
    partition: str,
    graphiti_kind: str,
    node_kind: str,
    row: dict[str, Any],
) -> str:
    graphiti_uuid = _graphiti_section_uuid(row)
    if not graphiti_uuid:
        graphiti_uuid = f"anonymous:{len(nodes)}"
    preview_uuid = _graphiti_l2b_uuid(partition, graphiti_kind, graphiti_uuid)
    if preview_uuid in seen:
        return preview_uuid
    raw = _dict_or_empty(row.get("raw"))
    source_ref = f"graphiti://{partition}/{graphiti_kind}/{graphiti_uuid}"
    nodes.append(
        {
            "schema_version": 1,
            "uuid": preview_uuid,
            "node_kind": node_kind,
            "label": _graphiti_row_label(row, fallback=f"Graphiti {graphiti_kind}"),
            "graphiti_uuid": graphiti_uuid,
            "graphiti_kind": f"graphiti_{graphiti_kind}",
            "partition": partition,
            "source": "graphiti",
            "is_pointer": True,
            "source_ref": source_ref,
            "ref_id": f"graphiti:{partition}:{graphiti_kind}:{graphiti_uuid}",
            "bucket_id": "graphiti_import_preview",
            "confirmation": "expected",
            "attention": 0.35,
            "source_meta": {
                "source_tool": "web_console.graphiti_bundle_projection",
                "graphiti_partition": partition,
                "graphiti_kind": graphiti_kind,
                "graphiti_uuid": graphiti_uuid,
                "source_ref": source_ref,
                "pointer_only": True,
            },
            "meta": {
                "preserve_raw_graphiti": True,
                "graphiti_raw": raw,
                "source_envelope": _dict_or_empty(row.get("source_envelope")),
            },
        }
    )
    seen.add(preview_uuid)
    return preview_uuid


def _graphiti_bundle_l2b_edges(
    *,
    partition: str,
    facts: list[dict[str, Any]],
    l2b_nodes: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    fact_pointers: list[dict[str, Any]] = []
    fact_edges: list[dict[str, Any]] = []
    episode_links: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    seen_node_uuids = {str(row.get("uuid") or "") for row in l2b_nodes}
    seen_support_edges: set[tuple[str, str, str, str]] = set()

    for index, row in enumerate(facts[:40]):
        raw = _dict_or_empty(row.get("raw"))
        source_envelope = _dict_or_empty(row.get("source_envelope"))
        fact_uuid = _graphiti_section_uuid(row) or f"fact:{index}"
        source_graphiti_uuid = _graphiti_fact_endpoint_uuid(row, "source")
        target_graphiti_uuid = _graphiti_fact_endpoint_uuid(row, "target")
        label = _graphiti_row_label(row, fallback=f"Graphiti fact {index + 1}")
        episode_uuids = _graphiti_fact_episode_uuids(row)
        fact_pointer = {
            "schema_version": 1,
            "uuid": fact_uuid,
            "graphiti_uuid": fact_uuid,
            "ref_id": f"graphiti:{partition}:fact:{fact_uuid}",
            "label": label,
            "source_ref": f"graphiti://{partition}/fact/{fact_uuid}",
            "source_graphiti_uuid": source_graphiti_uuid,
            "target_graphiti_uuid": target_graphiti_uuid,
            "episode_uuids": episode_uuids,
            "raw": raw,
            "source_envelope": source_envelope,
        }
        fact_pointers.append(fact_pointer)
        if not source_graphiti_uuid or not target_graphiti_uuid:
            issues.append(
                {
                    "severity": "warning",
                    "code": "fact_missing_endpoint_uuid",
                    "fact_uuid": fact_uuid,
                    "label": label,
                }
            )
            continue
        source_uuid = _graphiti_l2b_uuid(partition, "entity", source_graphiti_uuid)
        target_uuid = _graphiti_l2b_uuid(partition, "entity", target_graphiti_uuid)
        if source_uuid not in seen_node_uuids:
            l2b_nodes.append(
                _graphiti_pointer_node(
                    partition=partition,
                    graphiti_kind="entity",
                    graphiti_uuid=source_graphiti_uuid,
                    role="source",
                    parent_fact_uuid=fact_uuid,
                )
            )
            seen_node_uuids.add(source_uuid)
        if target_uuid not in seen_node_uuids:
            l2b_nodes.append(
                _graphiti_pointer_node(
                    partition=partition,
                    graphiti_kind="entity",
                    graphiti_uuid=target_graphiti_uuid,
                    role="target",
                    parent_fact_uuid=fact_uuid,
                )
            )
            seen_node_uuids.add(target_uuid)
        fact_edges.append(
            {
                "source": source_uuid,
                "target": target_uuid,
                "kind": "graphiti_fact",
                "edge_source": "graphiti",
                "strength": max(0.0, min(_body_float(row.get("score") or source_envelope.get("score"), 0.65), 1.0)),
                "label": label,
                "graphiti_uuid": fact_uuid,
                "source_graphiti_uuid": source_graphiti_uuid,
                "target_graphiti_uuid": target_graphiti_uuid,
                "ref_ids": [fact_pointer["ref_id"]],
                "status": "projection_preview_not_materialized",
                "write_policy": "requires_resolved_l2b_node_uuid",
                "meta": {
                    "source_tool": "web_console.graphiti_bundle_projection",
                    "graphiti_partition": partition,
                    "graphiti_raw_kind": "fact",
                    "fact_text": label,
                    "episode_uuids": episode_uuids,
                    "graphiti_raw": raw,
                    "source_envelope": source_envelope,
                    "preserve_raw_graphiti": True,
                },
            }
        )
        for episode_uuid in episode_uuids[:12]:
            episode_node_uuid = _graphiti_l2b_uuid(partition, "episode", episode_uuid)
            if episode_node_uuid not in seen_node_uuids:
                l2b_nodes.append(
                    _graphiti_pointer_node(
                        partition=partition,
                        graphiti_kind="episode",
                        graphiti_uuid=episode_uuid,
                        role="episode",
                        parent_fact_uuid=fact_uuid,
                    )
                )
                seen_node_uuids.add(episode_node_uuid)
            for target in (source_uuid, target_uuid):
                support_key = (episode_node_uuid, target, fact_uuid, "mentions")
                if support_key in seen_support_edges:
                    continue
                seen_support_edges.add(support_key)
                episode_links.append(
                    {
                        "source": episode_node_uuid,
                        "target": target,
                        "kind": "mentions",
                        "edge_source": "graphiti_episode",
                        "strength": 0.4,
                        "label": "episode mentions entity",
                        "graphiti_uuid": fact_uuid,
                        "status": "projection_preview_not_materialized",
                        "meta": {
                            "parent_fact_uuid": fact_uuid,
                            "episode_graphiti_uuid": episode_uuid,
                            "preserve_raw_graphiti": True,
                        },
                    }
                )
    return fact_pointers, fact_edges, episode_links, issues


def _graphiti_pointer_node(
    *,
    partition: str,
    graphiti_kind: str,
    graphiti_uuid: str,
    role: str,
    parent_fact_uuid: str,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "uuid": _graphiti_l2b_uuid(partition, graphiti_kind, graphiti_uuid),
        "node_kind": "event" if graphiti_kind == "episode" else "object",
        "label": f"{graphiti_kind}:{graphiti_uuid[:12]}",
        "graphiti_uuid": graphiti_uuid,
        "graphiti_kind": f"graphiti_{graphiti_kind}",
        "partition": partition,
        "source": "graphiti",
        "is_pointer": True,
        "source_ref": f"graphiti://{partition}/{graphiti_kind}/{graphiti_uuid}",
        "ref_id": f"graphiti:{partition}:{graphiti_kind}:{graphiti_uuid}",
        "bucket_id": "graphiti_import_preview",
        "confirmation": "expected",
        "attention": 0.25,
        "source_meta": {
            "source_tool": "web_console.graphiti_bundle_projection",
            "graphiti_partition": partition,
            "graphiti_kind": graphiti_kind,
            "graphiti_uuid": graphiti_uuid,
            "endpoint_role": role,
            "parent_fact_uuid": parent_fact_uuid,
            "pointer_only": True,
        },
        "meta": {
            "preserve_raw_graphiti": True,
            "pointer_only": True,
            "parent_fact_uuid": parent_fact_uuid,
        },
    }


def _rustworkx_projection_preview(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> dict[str, Any]:
    try:
        import rustworkx as rx
    except Exception as exc:
        return {
            "available": False,
            "error": f"{type(exc).__name__}: {exc}",
            "node_count": len(nodes),
            "edge_count": len(edges),
            "rwx_idx_policy": "unavailable_ephemeral_preview_only",
        }

    graph = rx.PyDiGraph()
    uuid_to_idx: dict[str, int] = {}
    idx_to_uuid: dict[int, str] = {}
    for node in nodes:
        node_uuid = str(node.get("uuid") or "").strip()
        if not node_uuid or node_uuid in uuid_to_idx:
            continue
        idx = int(graph.add_node({"uuid": node_uuid, "node_kind": node.get("node_kind")}))
        uuid_to_idx[node_uuid] = idx
        idx_to_uuid[idx] = node_uuid
    added_edges = 0
    for edge in edges:
        source = uuid_to_idx.get(str(edge.get("source") or ""))
        target = uuid_to_idx.get(str(edge.get("target") or ""))
        if source is None or target is None:
            continue
        graph.add_edge(source, target, {"kind": edge.get("kind"), "graphiti_uuid": edge.get("graphiti_uuid")})
        added_edges += 1
    try:
        components = [set(component) for component in rx.weakly_connected_components(graph)]
    except Exception:
        components = []
    component_sizes = sorted((len(component) for component in components), reverse=True)
    component_samples = [
        [idx_to_uuid.get(int(idx), str(idx)) for idx in sorted(component)[:8]]
        for component in sorted(components, key=lambda item: len(item), reverse=True)[:5]
    ]
    return {
        "available": True,
        "backend": "rustworkx.PyDiGraph",
        "node_count": int(graph.num_nodes()),
        "edge_count": added_edges,
        "weak_component_count": len(components),
        "largest_component_size": component_sizes[0] if component_sizes else int(graph.num_nodes()),
        "component_sizes": component_sizes[:12],
        "component_samples": component_samples,
        "uuid_to_rwx_idx_preview": uuid_to_idx,
        "rwx_idx_policy": "ephemeral_do_not_persist",
    }


def _graphiti_entity_node_kind(row: dict[str, Any]) -> str:
    raw = _dict_or_empty(row.get("raw"))
    labels = raw.get("labels") if isinstance(raw.get("labels"), list) else []
    label_text = " ".join(str(item).lower() for item in labels)
    if "person" in label_text or "operator" in label_text:
        return "person"
    if "event" in label_text or "episode" in label_text:
        return "event"
    return "object"


def _graphiti_row_label(row: dict[str, Any], *, fallback: str) -> str:
    raw = _dict_or_empty(row.get("raw"))
    source_envelope = _dict_or_empty(row.get("source_envelope"))
    for value in (
        raw.get("name"),
        raw.get("label"),
        raw.get("title"),
        raw.get("fact"),
        raw.get("summary"),
        source_envelope.get("text"),
        source_envelope.get("label"),
        row.get("label"),
        row.get("uuid"),
    ):
        text = " ".join(str(value or "").split())
        if text:
            return text[:160]
    return fallback


def _graphiti_section_uuid(row: dict[str, Any]) -> str:
    raw = _dict_or_empty(row.get("raw"))
    source_envelope = _dict_or_empty(row.get("source_envelope"))
    return str(
        row.get("uuid")
        or raw.get("uuid")
        or source_envelope.get("uuid")
        or source_envelope.get("graphiti_edge_uuid")
        or ""
    ).strip()


def _graphiti_fact_endpoint_uuid(row: dict[str, Any], role: str) -> str:
    raw = _dict_or_empty(row.get("raw"))
    source_envelope = _dict_or_empty(row.get("source_envelope"))
    raw_node = _dict_or_empty(raw.get(f"{role}_node"))
    envelope_node = _dict_or_empty(source_envelope.get(f"{role}_node"))
    return str(
        row.get(f"{role}_node_uuid")
        or raw.get(f"{role}_node_uuid")
        or source_envelope.get(f"{role}_node_uuid")
        or raw_node.get("uuid")
        or envelope_node.get("uuid")
        or ""
    ).strip()


def _graphiti_fact_episode_uuids(row: dict[str, Any]) -> list[str]:
    raw = _dict_or_empty(row.get("raw"))
    source_envelope = _dict_or_empty(row.get("source_envelope"))
    values: list[Any] = []
    for candidate in (
        row.get("episode_uuids"),
        raw.get("episode_uuids"),
        source_envelope.get("episode_uuids"),
    ):
        if isinstance(candidate, list):
            values.extend(candidate)
    lookup = _dict_or_empty(row.get("lookup"))
    episodes = lookup.get("episodes")
    if isinstance(episodes, list):
        for episode in episodes:
            if isinstance(episode, dict):
                values.append(episode.get("uuid"))
    return list(_string_tuple(values))


def _graphiti_l2b_uuid(partition: str, graphiti_kind: str, graphiti_uuid: str) -> str:
    return f"graphiti:{partition}:{graphiti_kind}:{graphiti_uuid}"


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
        GraphTransformKind.GRAPHITI_BUNDLE_PROJECTION: "Project a preserved Graphiti bundle into an L2-B/RustWorkX preview without materializing topology.",
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


def _body_int(value: Any, *, default: int, minimum: int, maximum: int) -> int:
    if value is None or value == "":
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, parsed))


def _enum_value(value: Any) -> Any:
    return value.value if isinstance(value, Enum) else value


def _semantic_node_row(node: Any) -> dict[str, Any]:
    return {
        "uuid": str(getattr(node, "uuid", "") or ""),
        "label": str(getattr(node, "label", "") or ""),
        "kind": str(_enum_value(getattr(node, "kind", "")) or ""),
        "graphiti_uuid": str(getattr(node, "graphiti_uuid", "") or ""),
        "obsidian_uuid": str(getattr(node, "obsidian_uuid", "") or ""),
        "category": str(getattr(node, "category", "") or ""),
        "description": str(getattr(node, "description", "") or ""),
        "known_facts": _jsonable(list(getattr(node, "known_facts", []) or [])),
        "tags": _jsonable(list(getattr(node, "tags", []) or [])),
        "typical_location": str(getattr(node, "typical_location", "") or ""),
        "attention": _body_float(getattr(node, "attention", 0.0), 0.0),
        "novelty": _body_float(getattr(node, "novelty", 0.0), 0.0),
        "salience": str(_enum_value(getattr(node, "salience", "")) or ""),
        "confirmation": str(_enum_value(getattr(node, "confirmation", "")) or ""),
        "evidence_score": _body_float(getattr(node, "evidence_score", 0.0), 0.0),
        "episode_id": str(getattr(node, "episode_id", "") or ""),
        "bucket_id": str(getattr(node, "bucket_id", "") or ""),
        "event_id": str(getattr(node, "event_id", "") or ""),
        "scene_type": str(getattr(node, "scene_type", "") or ""),
        "location_tag": str(getattr(node, "location_tag", "") or ""),
        "source": str(getattr(node, "source", "") or ""),
        "source_meta": _jsonable(getattr(node, "source_meta", {}) or {}),
        "meta": _jsonable(getattr(node, "meta", {}) or {}),
        "provenance_stream_id": str(getattr(node, "provenance_stream_id", "") or ""),
        "reference_image_path": str(getattr(node, "reference_image_path", "") or ""),
        "last_sighting_path": str(getattr(node, "last_sighting_path", "") or ""),
        "refs": {
            "graphiti_uuid": str(getattr(node, "graphiti_uuid", "") or ""),
            "obsidian_uuid": str(getattr(node, "obsidian_uuid", "") or ""),
            "reference_image_path": str(getattr(node, "reference_image_path", "") or ""),
            "last_sighting_path": str(getattr(node, "last_sighting_path", "") or ""),
            "provenance_stream_id": str(getattr(node, "provenance_stream_id", "") or ""),
        },
    }


def _semantic_edge_row(src: Any, dst: Any, edge: Any) -> dict[str, Any]:
    return {
        "source": str(getattr(src, "uuid", "") or ""),
        "target": str(getattr(dst, "uuid", "") or ""),
        "source_label": str(getattr(src, "label", "") or ""),
        "target_label": str(getattr(dst, "label", "") or ""),
        "kind": str(_enum_value(getattr(edge, "kind", "")) or ""),
        "strength": _body_float(getattr(edge, "strength", 0.0), 0.0),
        "edge_source": str(getattr(edge, "source", "") or ""),
        "created_at": _body_float(getattr(edge, "created_at", 0.0), 0.0),
        "graphiti_uuid": str(getattr(edge, "graphiti_uuid", "") or ""),
        "source_graphiti_uuid": str(getattr(edge, "source_graphiti_uuid", "") or ""),
        "target_graphiti_uuid": str(getattr(edge, "target_graphiti_uuid", "") or ""),
        "ref_ids": _jsonable(tuple(getattr(edge, "ref_ids", ()) or ())),
        "view_classes": _jsonable(tuple(getattr(edge, "view_classes", ()) or ())),
        "meta": _jsonable(getattr(edge, "meta", {}) or {}),
    }


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
    "draft_graphiti_bundle_projection",
    "draft_import_destination",
    "draft_subgraph_overlay",
    "graph_health_snapshot",
    "live_subgraph_context",
]
