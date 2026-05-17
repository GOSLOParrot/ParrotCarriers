"""Developer-console adapter for Graphiti memory-core management.

The Web console needs to inspect and test Graphiti without turning page loads
into memory writes. This adapter keeps reads, drafts, and explicit episode
writes separate. It degrades cleanly when the optional ``memory`` extra or the
graph database is not available.
"""

from __future__ import annotations

import datetime as _dt
import copy
import inspect
import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from parrot.memory.graphiti_client import PARTITIONS, graphiti_provider_status

_GRAPHITI_MISSING_MESSAGE = "graphiti-core optional extra not installed"


@dataclass(frozen=True)
class GraphitiConsoleResult:
    """Serializable Graphiti operation result."""

    action: str
    success: bool
    available: bool
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "success": self.success,
            "available": self.available,
            "message": self.message,
            "data": dict(self.data),
        }


def graphiti_status() -> GraphitiConsoleResult:
    """Return dependency/config status without opening a DB connection."""
    installed = _graphiti_core_installed()
    config_data: dict[str, Any] = {
        "installed": installed,
        "partitions": _partition_values(),
    }
    try:
        from parrot.shared.config import ParrotConfig

        cfg = ParrotConfig()
        config_data.update(
            {
                "falkordb": {
                    "host": cfg.falkordb.host,
                    "port": cfg.falkordb.port,
                    "database": cfg.falkordb.database,
                },
                "google_api_key_configured": bool(cfg.google_api_key),
                "graphiti_llm": graphiti_provider_status(cfg),
                "gemini": {
                    "embedding_model": cfg.gemini.embedding_model,
                    "reranker_model": cfg.gemini.reranker_model,
                },
            }
        )
    except Exception as exc:
        config_data["config_error"] = f"{type(exc).__name__}: {exc}"

    message = "graphiti-core importable" if installed else _GRAPHITI_MISSING_MESSAGE
    if not installed:
        remote = _remote_graphiti_request("/api/graphiti/status")
        if remote.get("success"):
            remote_data = dict(remote.get("data") or {})
            remote_data["remote_proxy"] = {
                "enabled": True,
                "base_url": _remote_graphiti_base_url(),
                "local_graphiti_core": False,
                "reason": "local_graphiti_core_missing",
            }
            return GraphitiConsoleResult(
                action="graphiti_status",
                success=bool(remote.get("success")),
                available=bool(remote.get("available")),
                message=f"remote: {remote.get('message') or 'Graphiti status proxied'}",
                data=remote_data,
            )
        config_data["remote_proxy"] = {
            "enabled": False,
            "base_url": _remote_graphiti_base_url(),
            "error": remote.get("error") or "remote_graphiti_status_unavailable",
        }
    return GraphitiConsoleResult(
        action="graphiti_status",
        success=True,
        available=installed,
        message=message,
        data=config_data,
    )


def draft_episode(
    *,
    name: str,
    body: str,
    partition: str = PARTITIONS.GOSLO,
    source_description: str = "app-web-console",
) -> GraphitiConsoleResult:
    """Build the exact episode draft the console would write."""
    selected_partition = _normalize_partition(partition)
    draft = {
        "name": name.strip() or "app_console_episode",
        "episode_body": body.strip(),
        "source": "text",
        "source_description": source_description.strip() or "app-web-console",
        "reference_time": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "group_id": selected_partition,
    }
    warnings: list[str] = []
    if not draft["episode_body"]:
        warnings.append("episode_body is empty; write endpoint will reject it")
    return GraphitiConsoleResult(
        action="draft_episode",
        success=True,
        available=_graphiti_core_installed(),
        message="draft only; no Graphiti write performed",
        data={"draft": draft, "warnings": warnings},
    )


async def search_graphiti(
    *,
    query: str,
    partition: str = PARTITIONS.GOSLO,
    limit: Any = 5,
    focal_node_uuid: str = "",
    search_recipe: str = "",
    node_labels: Any = None,
    edge_types: Any = None,
) -> GraphitiConsoleResult:
    """Search Graphiti with a scoped partition and graceful failure."""
    installed = _graphiti_core_installed()
    selected_limit = _safe_limit(limit, default=5, maximum=20)
    selected_partition = _normalize_partition(partition)
    selected_focal = str(focal_node_uuid or "").strip()
    selected_recipe = _normalize_search_recipe(search_recipe)
    selected_node_labels = _string_list(node_labels)
    selected_edge_types = _string_list(edge_types)
    if not query.strip():
        return GraphitiConsoleResult(
            action="search_graphiti",
            success=False,
            available=installed,
            message="query is required",
        )
    if not installed:
        remote = _remote_graphiti_request(
            "/api/graphiti/search",
            payload={
                "query": query,
                "partition": selected_partition,
                "limit": selected_limit,
                "focal_node_uuid": selected_focal,
                "search_recipe": selected_recipe,
                "node_labels": selected_node_labels,
                "edge_types": selected_edge_types,
            },
        )
        if remote.get("success"):
            remote_data = dict(remote.get("data") or {})
            remote_data.setdefault("query", query)
            remote_data.setdefault("partition", selected_partition)
            remote_data.setdefault("limit", selected_limit)
            if selected_recipe:
                remote_data.setdefault("search_recipe", selected_recipe)
            if selected_focal:
                remote_data.setdefault("focal_node_uuid", selected_focal)
            if selected_node_labels:
                remote_data.setdefault("node_labels", selected_node_labels)
            if selected_edge_types:
                remote_data.setdefault("edge_types", selected_edge_types)
            remote_data["remote_proxy"] = {
                "enabled": True,
                "base_url": _remote_graphiti_base_url(),
                "local_graphiti_core": False,
                "reason": "local_graphiti_core_missing",
            }
            return GraphitiConsoleResult(
                action="search_graphiti",
                success=True,
                available=bool(remote.get("available", True)),
                message=f"remote: {remote.get('message') or 'search proxied'}",
                data=remote_data,
            )
        return GraphitiConsoleResult(
            action="search_graphiti",
            success=False,
            available=False,
            message=_GRAPHITI_MISSING_MESSAGE,
            data={
                "query": query,
                "partition": selected_partition,
                "results": [],
                "remote_proxy": {
                    "enabled": False,
                    "base_url": _remote_graphiti_base_url(),
                    "error": remote.get("error") or "remote_graphiti_search_unavailable",
                },
            },
        )
    try:
        from parrot.memory.graphiti_client import get_graphiti

        g = await get_graphiti()
        results, search_config = await _call_graphiti_search(
            g,
            query=query.strip(),
            partition=selected_partition,
            limit=selected_limit,
            focal_node_uuid=selected_focal,
            search_recipe=selected_recipe,
            node_labels=selected_node_labels,
            edge_types=selected_edge_types,
        )
        rows = [
            _serialize_search_hit(hit)
            for hit in _search_result_items(results)[:selected_limit]
        ]
        fallback_search: dict[str, Any] | None = None
        if not rows:
            rows = await _fallback_graphiti_partition_search(
                g,
                query=query.strip(),
                partition=selected_partition,
                limit=selected_limit,
            )
            if rows:
                strategy = _fallback_strategy_from_rows(rows)
                fallback_search = {
                    "enabled": True,
                    "strategy": strategy,
                    "reason": "graphiti_search_returned_no_results",
                    "partition_graph": selected_partition,
                }
        data: dict[str, Any] = {
            "query": query,
            "partition": selected_partition,
            "limit": selected_limit,
            "results": rows,
            "search_config": search_config,
        }
        if selected_recipe:
            data["search_recipe"] = selected_recipe
        if selected_node_labels:
            data["node_labels"] = selected_node_labels
        if selected_edge_types:
            data["edge_types"] = selected_edge_types
        if selected_focal:
            data["focal_node_uuid"] = selected_focal
        if fallback_search:
            data["fallback_search"] = fallback_search
        return GraphitiConsoleResult(
            action="search_graphiti",
            success=True,
            available=True,
            message=f"{len(rows)} result(s)",
            data=data,
        )
    except Exception as exc:
        return GraphitiConsoleResult(
            action="search_graphiti",
            success=False,
            available=_graphiti_core_installed(),
            message=f"{type(exc).__name__}: {exc}",
            data={"query": query, "partition": selected_partition},
        )


async def search_graphiti_subgraph(
    *,
    query: str,
    partition: str = PARTITIONS.GOSLO,
    limit: Any = 8,
    strategy: str = "hybrid",
    depth: Any = 1,
    expansion_limit: Any = 3,
    focal_node_uuid: str = "",
    search_recipe: str = "",
    node_labels: Any = None,
    edge_types: Any = None,
    enrich: Any = True,
) -> dict[str, Any]:
    """Return a bounded Graphiti search slice shaped for graph renderers.

    ``strategy=iterative_hybrid`` performs real follow-up Graphiti searches from
    endpoint names/facts found in the previous hop. L2-B still receives
    preserved Graphiti envelopes; it does not reinterpret Graphiti as its own
    ontology.
    """
    selected_partition = _normalize_partition(partition)
    selected_limit = _safe_limit(limit, default=8, maximum=20)
    selected_strategy = _normalize_search_strategy(strategy)
    selected_depth = _safe_depth(depth, strategy=selected_strategy)
    selected_expansion_limit = _safe_limit(expansion_limit, default=3, maximum=8)
    selected_focal = str(focal_node_uuid or "").strip()
    selected_recipe = _normalize_search_recipe(search_recipe or selected_strategy)
    selected_node_labels = _string_list(node_labels)
    selected_edge_types = _string_list(edge_types)
    should_enrich = _body_bool(enrich, True)
    collected = await _collect_graphiti_subgraph_hits(
        query=query,
        partition=selected_partition,
        limit=selected_limit,
        strategy=selected_strategy,
        depth=selected_depth,
        expansion_limit=selected_expansion_limit,
        focal_node_uuid=selected_focal,
        search_recipe=selected_recipe,
        node_labels=selected_node_labels,
        edge_types=selected_edge_types,
    )
    if not collected["success"]:
        search = collected["base_search"]
        payload = search.as_json() if isinstance(search, GraphitiConsoleResult) else {}
        payload.setdefault("success", False)
        payload.setdefault("available", False)
        payload.setdefault("message", "Graphiti search failed")
        payload["action"] = "graphiti.subgraph.search"
        empty_subgraph = _empty_subgraph(query=query, partition=selected_partition)
        payload.setdefault("data", {}).update(
            {
                "query": query.strip(),
                "partition": selected_partition,
                "limit": selected_limit,
                "strategy": selected_strategy,
                "depth": selected_depth,
                "expansion_limit": selected_expansion_limit,
                "focal_node_uuid": selected_focal,
                "search_recipe": selected_recipe,
                "node_labels": selected_node_labels,
                "edge_types": selected_edge_types,
                "hits": [],
                "subgraph": empty_subgraph,
                "search_plan": collected["search_plan"],
                "graphiti_bundle": _graphiti_subgraph_bundle(
                    hits=[],
                    partition=selected_partition,
                    query=query,
                    subgraph=empty_subgraph,
                    search_plan=collected["search_plan"],
                    strategy=selected_strategy,
                    depth=selected_depth,
                    expansion_limit=selected_expansion_limit,
                    search_recipe=selected_recipe,
                    node_labels=selected_node_labels,
                    edge_types=selected_edge_types,
                ),
                "warnings": collected["warnings"],
            }
        )
        return payload

    hits = list(collected["hits"])
    enrichment = {"enabled": should_enrich, "success": False, "results": [], "warnings": []}
    if should_enrich and hits:
        enrichment = await _enrich_graphiti_hits(hits, partition=selected_partition)
    subgraph = _hits_to_subgraph(hits, query=query, partition=selected_partition)
    raw_envelopes = _hits_to_raw_envelopes(hits, partition=selected_partition)
    edge_drafts = _hits_to_edge_drafts(hits, partition=selected_partition)
    identity_ref_drafts = _hits_to_identity_ref_drafts(raw_envelopes, partition=selected_partition)
    graphiti_bundle = _graphiti_subgraph_bundle(
        hits=hits,
        partition=selected_partition,
        query=query,
        subgraph=subgraph,
        raw_envelopes=raw_envelopes,
        edge_drafts=edge_drafts,
        identity_ref_drafts=identity_ref_drafts,
        search_plan=collected["search_plan"],
        graphiti_lookup=enrichment,
        strategy=selected_strategy,
        depth=selected_depth,
        expansion_limit=selected_expansion_limit,
        search_recipe=selected_recipe,
        node_labels=selected_node_labels,
        edge_types=selected_edge_types,
    )
    return {
        "action": "graphiti.subgraph.search",
        "success": True,
        "available": bool(collected["available"]),
        "message": f"{len(hits)} hit(s), {len(subgraph['nodes'])} node(s)",
        "data": {
            "query": query.strip(),
            "partition": selected_partition,
            "limit": selected_limit,
            "strategy": selected_strategy,
            "depth": selected_depth,
            "expansion_limit": selected_expansion_limit,
            "focal_node_uuid": selected_focal,
            "search_recipe": selected_recipe,
            "node_labels": selected_node_labels,
            "edge_types": selected_edge_types,
            "enrich": should_enrich,
            "hits": hits,
            "subgraph": subgraph,
            "search_plan": collected["search_plan"],
            "graphiti_lookup": enrichment,
            "graphiti_bundle": graphiti_bundle,
            "warnings": collected["warnings"] + list(enrichment.get("warnings") or []),
        },
        "audit": {
            "web_only": True,
            "read_only": True,
            "direct_falkordb_write": False,
        },
    }


async def lookup_graphiti_uuids(
    *,
    uuids: list[str] | tuple[str, ...] | set[str] | None = None,
    uuid: str = "",
    partition: str = PARTITIONS.GOSLO,
    kind: str = "",
) -> GraphitiConsoleResult:
    """Read Graphiti objects by UUID through official CRUD helpers when present."""

    selected_partition = _normalize_partition(partition)
    requested = _normalize_uuid_list([*(uuids or []), uuid])
    kind_hint = str(kind or "").strip().lower()
    installed = _graphiti_core_installed()
    if not requested:
        return GraphitiConsoleResult(
            action="graphiti.lookup",
            success=False,
            available=installed,
            message="uuid is required",
            data={"partition": selected_partition, "results": []},
        )
    if not installed:
        remote = _remote_graphiti_request(
            "/api/graphiti/lookup",
            payload={
                "uuids": requested,
                "partition": selected_partition,
                "kind": kind_hint,
            },
        )
        if remote.get("success"):
            remote_data = dict(remote.get("data") or {})
            remote_data.setdefault("partition", selected_partition)
            remote_data.setdefault("results", [])
            remote_data["remote_proxy"] = {
                "enabled": True,
                "base_url": _remote_graphiti_base_url(),
                "local_graphiti_core": False,
                "reason": "local_graphiti_core_missing",
            }
            return GraphitiConsoleResult(
                action="graphiti.lookup",
                success=True,
                available=bool(remote.get("available", True)),
                message=f"remote: {remote.get('message') or 'lookup proxied'}",
                data=remote_data,
            )
        return GraphitiConsoleResult(
            action="graphiti.lookup",
            success=False,
            available=False,
            message=_GRAPHITI_MISSING_MESSAGE,
            data={
                "partition": selected_partition,
                "results": [],
                "remote_proxy": {
                    "enabled": False,
                    "base_url": _remote_graphiti_base_url(),
                    "error": remote.get("error") or "remote_graphiti_lookup_unavailable",
                },
            },
        )

    try:
        from parrot.memory.graphiti_client import get_graphiti

        graphiti = await get_graphiti()
        driver = getattr(graphiti, "driver", None) or getattr(graphiti, "graph_driver", None)
        if driver is None:
            raise RuntimeError("Graphiti driver unavailable")
        results = [
            await _lookup_graphiti_uuid_local(driver, item, partition=selected_partition, kind=kind_hint)
            for item in requested[:40]
        ]
        found_count = sum(1 for item in results if item.get("found"))
        return GraphitiConsoleResult(
            action="graphiti.lookup",
            success=found_count > 0,
            available=True,
            message=f"{found_count}/{len(results)} found",
            data={
                "partition": selected_partition,
                "kind": kind_hint,
                "results": results,
            },
        )
    except Exception as exc:
        return GraphitiConsoleResult(
            action="graphiti.lookup",
            success=False,
            available=_graphiti_core_installed(),
            message=f"{type(exc).__name__}: {exc}",
            data={"partition": selected_partition, "results": []},
        )


def draft_graphiti_subgraph_export(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Draft Graphiti search hits as L1.5 observations.

    The draft intentionally uses ``ObservationSource.USER_EXPLICIT`` for this
    first Web operator path: the operator is choosing to materialize search
    results into L2-B. Graphiti provenance stays in meta/graphiti_uuid instead
    of becoming a new shared source enum before CORE-008 review.
    """
    body = payload or {}
    partition = _normalize_partition(str(body.get("partition") or PARTITIONS.GOSLO))
    hits = _extract_export_hits(body)
    observations = [
        _hit_to_l15_observation_draft(hit, partition=partition, index=index)
        for index, hit in enumerate(hits)
    ]
    subgraph = _hits_to_subgraph(hits, query=str(body.get("query") or ""), partition=partition)
    raw_envelopes = _hits_to_raw_envelopes(hits, partition=partition)
    edge_drafts = _hits_to_edge_drafts(hits, partition=partition)
    identity_ref_drafts = _hits_to_identity_ref_drafts(raw_envelopes, partition=partition)
    graphiti_bundle = _graphiti_subgraph_bundle(
        hits=hits,
        partition=partition,
        query=str(body.get("query") or ""),
        subgraph=subgraph,
        raw_envelopes=raw_envelopes,
        edge_drafts=edge_drafts,
        identity_ref_drafts=identity_ref_drafts,
    )
    warnings: list[str] = []
    if not observations:
        warnings.append("no Graphiti hits selected for export")
    if edge_drafts:
        warnings.append("edge_drafts are preview-only until exported nodes resolve to L2-B UUIDs")
    if identity_ref_drafts:
        warnings.append("identity_ref_drafts are CORE-015 previews; they do not persist here")
    return _graphiti_receipt(
        action="graphiti.subgraph.export_draft",
        success=bool(observations),
        dry_run=True,
        operator_mode=False,
        data={
            "partition": partition,
            "query": str(body.get("query") or "").strip(),
            "selected_count": len(observations),
            "observations": observations,
            "subgraph": subgraph,
            "graphiti_raw_envelopes": raw_envelopes,
            "graphiti_bundle": graphiti_bundle,
            "identity_ref_drafts": identity_ref_drafts,
            "identity_ref_write_policy": (
                "Preview only. Apply through /api/memory/identity-ref-index/apply "
                "after operator review; this route does not persist IdentityRefIndex."
            ),
            "edge_drafts": edge_drafts,
            "write_path": "L15Pool.admit(Observation(source=USER_EXPLICIT))",
            "edge_write_policy": (
                "Graphiti fact nodes enter L1.5 first; fact edges require resolved "
                "L2-B node UUIDs before any later operator-gated edge write."
            ),
            "warnings": warnings,
            "operator_required_for_execute": True,
        },
    )


async def export_graphiti_subgraph(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Export selected Graphiti hits into L2-B through L1.5.

    Default browser calls only get a receipt. Real apply requires both
    ``dry_run=false`` and ``operator_mode=true`` so a Graphiti search cannot
    silently mutate L2-B.
    """
    from parrot.dsg.ingest.base import Observation, ObservationSource
    from parrot.dsg.l1_5.pool import get_l1_5_pool
    from parrot.dsg.l2b_types import ConfirmationStatus, NodeKind

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    if _remote_graphiti_base_url() and not _body_bool(body.get("_remote_proxy_disable"), False):
        remote_payload = dict(body)
        remote_payload["_remote_proxy_disable"] = True
        remote = _remote_graphiti_request(
            "/api/graphiti/subgraph/export",
            payload=remote_payload,
        )
        if isinstance(remote, dict) and remote.get("action"):
            remote_data = dict(remote.get("data") or {})
            remote_data["remote_proxy"] = {
                "enabled": bool(remote.get("success")),
                "base_url": _remote_graphiti_base_url(),
                "reason": "web_console_graphiti_remote_url_configured",
                "error": remote.get("error") or "",
            }
            remote["data"] = remote_data
            return remote
    draft = draft_graphiti_subgraph_export(body)
    draft["action"] = "graphiti.subgraph.export"
    draft["dry_run"] = dry_run
    draft["operator_mode"] = operator_mode
    if not draft.get("success"):
        return draft
    if dry_run or not operator_mode:
        draft["data"]["would_apply"] = True
        draft["data"]["apply_skipped_reason"] = "dry_run_or_operator_mode_missing"
        return draft

    observations: list[Observation] = []
    for row in draft["data"]["observations"]:
        observations.append(
            Observation(
                source=ObservationSource.USER_EXPLICIT,
                provenance_stream_id=str(row.get("provenance_stream_id") or ""),
                graphiti_uuid=str(row.get("graphiti_uuid") or ""),
                label=str(row["label"]),
                kind=NodeKind(row.get("kind") or "object"),
                description=str(row.get("description") or ""),
                confidence=float(row.get("confidence") or 0.78),
                confirmation=ConfirmationStatus(row.get("confirmation") or "confirmed"),
                meta=dict(row.get("meta") or {}),
            )
        )
    outcome = await get_l1_5_pool().admit(tuple(observations))
    return _graphiti_receipt(
        action="graphiti.subgraph.export",
        success=not outcome.rejected,
        dry_run=False,
        operator_mode=True,
        data={
            "partition": draft["data"]["partition"],
            "selected_count": len(observations),
            "admit_outcome": _jsonable(outcome),
            "write_path": "L15Pool.admit(Observation(source=USER_EXPLICIT))",
            "graphiti_raw_envelopes": draft["data"].get("graphiti_raw_envelopes", []),
            "graphiti_bundle": draft["data"].get("graphiti_bundle", {}),
            "identity_ref_drafts": draft["data"].get("identity_ref_drafts", []),
            "identity_ref_write_policy": draft["data"].get("identity_ref_write_policy", ""),
            "edge_drafts": draft["data"].get("edge_drafts", []),
            "edge_write_policy": draft["data"].get("edge_write_policy", ""),
        },
    )


async def add_episode(
    *,
    name: str,
    body: str,
    partition: str = PARTITIONS.GOSLO,
    source_description: str = "app-web-console",
    dry_run: bool = True,
) -> GraphitiConsoleResult:
    """Add a text episode only when dry_run is false and body is present."""
    installed = _graphiti_core_installed()
    draft = draft_episode(
        name=name,
        body=body,
        partition=partition,
        source_description=source_description,
    )
    episode = draft.data["draft"]
    if not episode["episode_body"]:
        return GraphitiConsoleResult(
            action="add_episode",
            success=False,
            available=installed,
            message="episode_body is required",
            data={"draft": episode},
        )
    if dry_run:
        return GraphitiConsoleResult(
            action="add_episode",
            success=True,
            available=installed,
            message="dry_run=true; no Graphiti write performed",
            data={"draft": episode},
        )
    if not installed:
        remote = _remote_graphiti_request(
            "/api/graphiti/episode",
            payload={
                "name": episode["name"],
                "body": episode["episode_body"],
                "partition": episode["group_id"],
                "source_description": episode["source_description"],
                "dry_run": False,
            },
        )
        if remote.get("success"):
            remote_data = dict(remote.get("data") or {})
            remote_data.setdefault("episode", episode)
            remote_data["remote_proxy"] = {
                "enabled": True,
                "base_url": _remote_graphiti_base_url(),
                "local_graphiti_core": False,
                "reason": "local_graphiti_core_missing",
            }
            return GraphitiConsoleResult(
                action="add_episode",
                success=True,
                available=bool(remote.get("available", True)),
                message=f"remote: {remote.get('message') or 'episode written'}",
                data=remote_data,
            )
        return GraphitiConsoleResult(
            action="add_episode",
            success=False,
            available=False,
            message=_GRAPHITI_MISSING_MESSAGE,
            data={
                "draft": episode,
                "remote_proxy": {
                    "enabled": False,
                    "base_url": _remote_graphiti_base_url(),
                    "error": remote.get("error") or "remote_graphiti_episode_unavailable",
                },
            },
        )

    try:
        from graphiti_core.nodes import EpisodeType

        from parrot.memory.graphiti_client import get_graphiti

        g = await get_graphiti()
        await g.add_episode(
            name=episode["name"],
            episode_body=episode["episode_body"],
            source=EpisodeType.text,
            source_description=episode["source_description"],
            reference_time=_dt.datetime.now(_dt.timezone.utc),
            group_id=episode["group_id"],
        )
        return GraphitiConsoleResult(
            action="add_episode",
            success=True,
            available=True,
            message="episode written",
            data={"episode": episode},
        )
    except Exception as exc:
        return GraphitiConsoleResult(
            action="add_episode",
            success=False,
            available=_graphiti_core_installed(),
            message=f"{type(exc).__name__}: {exc}",
            data={"draft": episode},
        )


async def _call_graphiti_search(
    graphiti: Any,
    *,
    query: str,
    partition: str,
    limit: int,
    focal_node_uuid: str = "",
    search_recipe: str = "",
    node_labels: list[str] | tuple[str, ...] = (),
    edge_types: list[str] | tuple[str, ...] = (),
) -> tuple[Any, dict[str, Any]]:
    """Call Graphiti search, optionally through a low-level SearchConfig recipe."""

    recipe_name = _graphiti_search_recipe_constant(search_recipe)
    low_level_name, low_level = _graphiti_low_level_search(graphiti)
    details: dict[str, Any] = {
        "mode": "search",
        "requested_recipe": str(search_recipe or ""),
        "recipe": recipe_name,
        "low_level_available": bool(low_level),
        "low_level_method": low_level_name,
        "fallback": False,
    }
    if recipe_name and low_level is not None:
        try:
            results = await _call_graphiti_search_config(
                graphiti,
                low_level=low_level,
                query=query,
                partition=partition,
                limit=limit,
                focal_node_uuid=focal_node_uuid,
                recipe_name=recipe_name,
                node_labels=tuple(node_labels),
                edge_types=tuple(edge_types),
            )
            details["mode"] = "_search"
            details["fallback"] = False
            return results, details
        except Exception as exc:
            details["fallback"] = True
            details["fallback_reason"] = f"{type(exc).__name__}: {exc}"

    return await _call_graphiti_search_default(
        graphiti,
        query=query,
        partition=partition,
        limit=limit,
        focal_node_uuid=focal_node_uuid,
    ), details


async def _call_graphiti_search_default(
    graphiti: Any,
    *,
    query: str,
    partition: str,
    limit: int,
    focal_node_uuid: str = "",
) -> Any:
    """Call Graphiti's public search method across parameter spellings."""

    search = getattr(graphiti, "search")
    focal = str(focal_node_uuid or "").strip()
    kwargs: dict[str, Any] = {"query": query}
    try:
        parameters = inspect.signature(search).parameters
    except (TypeError, ValueError):
        parameters = {}
    accepts_kwargs = _accepts_var_kwargs(parameters)

    if not parameters or accepts_kwargs or "group_ids" in parameters:
        kwargs["group_ids"] = [partition]
    if not parameters or accepts_kwargs or "num_results" in parameters:
        kwargs["num_results"] = limit
    elif "limit" in parameters:
        kwargs["limit"] = limit
    if focal:
        for name in ("focal_node_uuid", "center_node_uuid", "node_uuid"):
            if not parameters or accepts_kwargs or name in parameters:
                kwargs[name] = focal
                break

    try:
        return await search(**kwargs)
    except TypeError:
        if focal:
            return await search(query, focal, group_ids=[partition], num_results=limit)
        return await search(query=query, group_ids=[partition], num_results=limit)


async def _call_graphiti_search_config(
    graphiti: Any,
    *,
    low_level: Any | None = None,
    query: str,
    partition: str,
    limit: int,
    focal_node_uuid: str,
    recipe_name: str,
    node_labels: tuple[str, ...],
    edge_types: tuple[str, ...],
) -> Any:
    """Call Graphiti's lower-level _search(SearchConfig) recipe path."""

    if low_level is None:
        _, low_level = _graphiti_low_level_search(graphiti)
    if low_level is None:
        raise AttributeError("Graphiti low-level search is unavailable")
    config = _copy_graphiti_search_config(_load_search_config_recipe(recipe_name))
    _set_search_config_limit(config, limit)
    search_filter = _build_graphiti_search_filter(
        node_labels=node_labels,
        edge_types=edge_types,
    )
    focal = str(focal_node_uuid or "").strip()
    kwargs: dict[str, Any] = {"query": query}
    try:
        parameters = inspect.signature(low_level).parameters
    except (TypeError, ValueError):
        parameters = {}
    accepts_kwargs = _accepts_var_kwargs(parameters)

    if not parameters or accepts_kwargs or "group_id" in parameters:
        kwargs["group_id"] = partition
    elif "group_ids" in parameters:
        kwargs["group_ids"] = [partition]
    if not parameters or accepts_kwargs or "config" in parameters:
        kwargs["config"] = config
    if search_filter is not None:
        for name in ("search_filter", "filters", "filter"):
            if not parameters or accepts_kwargs or name in parameters:
                kwargs[name] = search_filter
                break
    if focal:
        for name in ("focal_node_uuid", "center_node_uuid", "node_uuid"):
            if not parameters or accepts_kwargs or name in parameters:
                kwargs[name] = focal
                break

    try:
        return await low_level(**kwargs)
    except TypeError:
        return await low_level(query=query, group_id=partition, config=config)


def _load_search_config_recipe(recipe_name: str) -> Any:
    from graphiti_core.search import search_config_recipes

    return getattr(search_config_recipes, recipe_name)


def _accepts_var_kwargs(parameters: dict[str, inspect.Parameter]) -> bool:
    return any(parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in parameters.values())


def _graphiti_low_level_search(graphiti: Any) -> tuple[str, Any | None]:
    for name in ("_search", "search_"):
        method = getattr(graphiti, name, None)
        if method is not None:
            return name, method
    return "", None


def _copy_graphiti_search_config(config: Any) -> Any:
    if hasattr(config, "model_copy"):
        return config.model_copy(deep=True)
    return copy.deepcopy(config)


def _set_search_config_limit(config: Any, limit: int) -> None:
    seen: set[int] = set()
    stack: list[Any] = [config]
    for attr in (
        "edges",
        "edge",
        "edge_config",
        "nodes",
        "node",
        "node_config",
        "communities",
        "community",
        "community_config",
    ):
        child = getattr(config, attr, None)
        if child is not None:
            stack.append(child)
    while stack:
        item = stack.pop()
        identity = id(item)
        if identity in seen:
            continue
        seen.add(identity)
        if hasattr(item, "limit"):
            try:
                setattr(item, "limit", limit)
            except Exception:
                pass


def _build_graphiti_search_filter(
    *,
    node_labels: tuple[str, ...],
    edge_types: tuple[str, ...],
) -> Any | None:
    if not node_labels and not edge_types:
        return None
    try:
        from graphiti_core.search.search_filters import SearchFilters
    except Exception:
        return None
    payload: dict[str, Any] = {}
    if node_labels:
        payload["node_labels"] = list(node_labels)
    if edge_types:
        payload["edge_types"] = list(edge_types)
    try:
        return SearchFilters(**payload)
    except TypeError:
        return None


async def _fallback_graphiti_partition_search(
    graphiti: Any,
    *,
    query: str,
    partition: str,
    limit: int,
) -> list[dict[str, Any]]:
    """Fallback over Graphiti's FalkorDB group graph when search indexes are cold."""

    terms = _fallback_search_terms(query)
    if not terms:
        return []
    driver = getattr(graphiti, "driver", None) or getattr(graphiti, "graph_driver", None)
    if driver is None or not hasattr(driver, "execute_query"):
        return []
    scoped_driver = driver.with_database(partition) if hasattr(driver, "with_database") else driver
    predicates: list[str] = []
    params: dict[str, Any] = {"partition": partition, "limit": max(limit * 4, limit)}
    for index, term in enumerate(terms[:8]):
        key = f"term{index}"
        params[key] = term
        predicates.append(
            " OR ".join(
                [
                    f"toLower(edge.fact) CONTAINS ${key}",
                    f"toLower(edge.name) CONTAINS ${key}",
                    f"toLower(source.name) CONTAINS ${key}",
                    f"toLower(target.name) CONTAINS ${key}",
                ]
            )
        )
    cypher = f"""
    MATCH (source)-[edge]->(target)
    WHERE edge.group_id = $partition
      AND edge.fact IS NOT NULL
      AND ({' OR '.join(f'({item})' for item in predicates)})
    RETURN
      edge.uuid AS uuid,
      edge.group_id AS group_id,
      edge.name AS name,
      edge.fact AS fact,
      edge.episodes AS episode_uuids,
      edge.created_at AS created_at,
      edge.valid_at AS valid_at,
      edge.invalid_at AS invalid_at,
      edge.expired_at AS expired_at,
      source.uuid AS source_node_uuid,
      target.uuid AS target_node_uuid,
      source.name AS source_node_name,
      target.name AS target_node_name,
      labels(source) AS source_labels,
      labels(target) AS target_labels
    LIMIT $limit
    """
    try:
        records, _, _ = await scoped_driver.execute_query(cypher, **params)
    except Exception:
        logger.debug("Graphiti FalkorDB fallback search failed", exc_info=True)
        return []

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in records or []:
        row = _jsonable(record)
        if not isinstance(row, dict):
            continue
        fact = str(row.get("fact") or "").strip()
        uuid = str(row.get("uuid") or "").strip()
        if not fact or not uuid or uuid in seen:
            continue
        seen.add(uuid)
        source_uuid = str(row.get("source_node_uuid") or "").strip()
        target_uuid = str(row.get("target_node_uuid") or "").strip()
        raw = {
            **row,
            "source_node": {
                "uuid": source_uuid,
                "name": str(row.get("source_node_name") or "").strip(),
                "labels": row.get("source_labels") or [],
                "group_id": partition,
            },
            "target_node": {
                "uuid": target_uuid,
                "name": str(row.get("target_node_name") or "").strip(),
                "labels": row.get("target_labels") or [],
                "group_id": partition,
            },
            "fallback_search": {
                "strategy": "falkordb_partition_fact_scan",
                "partition_graph": partition,
            },
        }
        score = _fallback_search_score(
            terms,
            " ".join(
                [
                    fact,
                    str(row.get("name") or ""),
                    str(row.get("source_node_name") or ""),
                    str(row.get("target_node_name") or ""),
                ]
            ),
        )
        rows.append(
            {
                "uuid": uuid,
                "graphiti_uuid": uuid,
                "graphiti_kind": "graphiti_fact",
                "text": fact,
                "fact": fact,
                "name": str(row.get("name") or "").strip(),
                "group_id": str(row.get("group_id") or partition),
                "source_node_uuid": source_uuid,
                "target_node_uuid": target_uuid,
                "episode_uuids": row.get("episode_uuids") or [],
                "created_at": row.get("created_at"),
                "valid_at": row.get("valid_at"),
                "invalid_at": row.get("invalid_at"),
                "expired_at": row.get("expired_at"),
                "score": score,
                "search_context": {
                    "fallback_search": {
                        "strategy": "falkordb_partition_fact_scan",
                        "partition_graph": partition,
                    },
                },
                "graphiti_raw": raw,
            }
        )
    if not rows:
        rows = await _fallback_graphiti_partition_node_search(
            graphiti,
            query=query,
            partition=partition,
            limit=limit,
            terms=terms,
        )
    rows.sort(key=lambda item: float(item.get("score") or 0.0), reverse=True)
    return rows[:limit]


async def _fallback_graphiti_partition_node_search(
    graphiti: Any,
    *,
    query: str,
    partition: str,
    limit: int,
    terms: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Fallback over Graphiti nodes/Episodes when fact search is too narrow."""

    search_terms = terms or _fallback_search_terms(query)
    if not search_terms:
        return []
    driver = getattr(graphiti, "driver", None) or getattr(graphiti, "graph_driver", None)
    if driver is None or not hasattr(driver, "execute_query"):
        return []
    scoped_driver = driver.with_database(partition) if hasattr(driver, "with_database") else driver
    predicates: list[str] = []
    params: dict[str, Any] = {"partition": partition, "limit": max(limit * 4, limit)}
    for index, term in enumerate(search_terms[:8]):
        key = f"term{index}"
        params[key] = term
        predicates.append(
            " OR ".join(
                [
                    f"(node.name IS NOT NULL AND toLower(node.name) CONTAINS ${key})",
                    f"(node.summary IS NOT NULL AND toLower(node.summary) CONTAINS ${key})",
                    f"(node.content IS NOT NULL AND toLower(node.content) CONTAINS ${key})",
                ]
            )
        )
    cypher = f"""
    MATCH (node)
    WHERE node.group_id = $partition
      AND ({' OR '.join(f'({item})' for item in predicates)})
    RETURN
      node.uuid AS uuid,
      node.group_id AS group_id,
      node.name AS name,
      node.summary AS summary,
      node.content AS content,
      node.created_at AS created_at,
      node.valid_at AS valid_at,
      node.invalid_at AS invalid_at,
      labels(node) AS labels
    LIMIT $limit
    """
    try:
        records, _, _ = await scoped_driver.execute_query(cypher, **params)
    except Exception:
        logger.debug("Graphiti FalkorDB fallback node search failed", exc_info=True)
        return []

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in records or []:
        row = _jsonable(record)
        if not isinstance(row, dict):
            continue
        uuid = str(row.get("uuid") or "").strip()
        if not uuid or uuid in seen:
            continue
        seen.add(uuid)
        labels = [str(label) for label in row.get("labels") or []]
        text = str(row.get("summary") or row.get("content") or row.get("name") or "").strip()
        if not text:
            continue
        graphiti_kind = "graphiti_episode" if any("Episodic" in label for label in labels) else "graphiti_entity"
        raw = {
            **row,
            "labels": labels,
            "group_id": str(row.get("group_id") or partition),
            "fallback_search": {
                "strategy": "falkordb_partition_node_scan",
                "partition_graph": partition,
            },
        }
        score = _fallback_search_score(
            search_terms,
            " ".join([text, str(row.get("name") or ""), " ".join(labels)]),
        )
        rows.append(
            {
                "uuid": uuid,
                "graphiti_uuid": uuid,
                "graphiti_kind": graphiti_kind,
                "text": text,
                "name": str(row.get("name") or "").strip(),
                "summary": str(row.get("summary") or "").strip(),
                "content": str(row.get("content") or "").strip(),
                "group_id": str(row.get("group_id") or partition),
                "created_at": row.get("created_at"),
                "valid_at": row.get("valid_at"),
                "invalid_at": row.get("invalid_at"),
                "score": score,
                "labels": labels,
                "search_context": {
                    "fallback_search": {
                        "strategy": "falkordb_partition_node_scan",
                        "partition_graph": partition,
                    },
                },
                "graphiti_raw": raw,
            }
        )
    rows.sort(key=lambda item: float(item.get("score") or 0.0), reverse=True)
    return rows[:limit]


def _fallback_search_terms(query: str) -> list[str]:
    raw_terms = re.findall(r"[A-Za-z0-9_:-]{2,}|[\u4e00-\u9fff]{2,}", query.lower())
    stopwords = {
        "the",
        "and",
        "for",
        "with",
        "near",
        "from",
        "into",
        "this",
        "that",
        "what",
        "why",
        "how",
    }
    result: list[str] = []
    seen: set[str] = set()
    for term in raw_terms:
        normalized = term.strip().lower()
        if not normalized or normalized in stopwords or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
        if len(result) >= 8:
            break
    compact = query.strip().lower()
    if 2 <= len(compact) <= 80 and compact not in seen:
        result.append(compact)
    return result


def _fallback_search_score(terms: list[str], text: str) -> float:
    haystack = text.lower()
    score = 0.0
    for index, term in enumerate(terms):
        if term and term in haystack:
            score += max(0.25, 2.0 - index * 0.15)
    return score


def _fallback_strategy_from_rows(rows: list[dict[str, Any]]) -> str:
    for row in rows:
        context = row.get("search_context")
        if not isinstance(context, dict):
            continue
        fallback = context.get("fallback_search")
        if not isinstance(fallback, dict):
            continue
        strategy = str(fallback.get("strategy") or "").strip()
        if strategy:
            return strategy
    for row in rows:
        kind = str(row.get("graphiti_kind") or "").strip().lower()
        if kind in {"graphiti_episode", "graphiti_entity", "episode", "entity"}:
            return "falkordb_partition_node_scan"
    return "falkordb_partition_fact_scan"


async def _collect_graphiti_subgraph_hits(
    *,
    query: str,
    partition: str,
    limit: int,
    strategy: str,
    depth: int,
    expansion_limit: int,
    focal_node_uuid: str,
    search_recipe: str,
    node_labels: list[str],
    edge_types: list[str],
) -> dict[str, Any]:
    base_query = query.strip()
    search_plan: list[dict[str, Any]] = []
    warnings: list[str] = []
    hits: list[dict[str, Any]] = []
    seen_hits: set[tuple[str, ...]] = set()
    visited_queries: set[str] = {base_query.lower()}
    frontier = [base_query] if base_query else []
    base_search: GraphitiConsoleResult | None = None
    available = True
    max_depth = depth if strategy in {"iterative_hybrid", "node_distance"} else 1

    for hop in range(max_depth):
        if not frontier:
            break
        next_terms: list[str] = []
        for origin_query in frontier[: max(1, expansion_limit)]:
            search_limit = limit if hop == 0 else max(1, min(limit, 6))
            search = await search_graphiti(
                query=origin_query,
                partition=partition,
                limit=search_limit,
                focal_node_uuid=focal_node_uuid if hop == 0 else "",
                search_recipe=search_recipe,
                node_labels=node_labels,
                edge_types=edge_types,
            )
            if base_search is None:
                base_search = search
            available = available and search.available
            rows = [row for row in search.data.get("results", []) if isinstance(row, dict)]
            search_plan.append(
                {
                    "depth": hop + 1,
                    "query": origin_query,
                    "strategy": strategy,
                    "search_recipe": search.data.get("search_recipe", search_recipe),
                    "search_config": search.data.get("search_config", {}),
                    "limit": search_limit,
                    "success": search.success,
                    "available": search.available,
                    "result_count": len(rows),
                    "message": search.message,
                }
            )
            if not search.success:
                if hop == 0 and not hits:
                    return {
                        "success": False,
                        "available": search.available,
                        "base_search": search,
                        "hits": [],
                        "search_plan": search_plan,
                        "warnings": warnings,
                    }
                warnings.append(f"{origin_query}: {search.message}")
                continue
            for index, row in enumerate(rows):
                hit = _with_search_context(
                    row,
                    base_query=base_query,
                    origin_query=origin_query,
                    strategy=strategy,
                    depth=hop + 1,
                    result_index=index,
                )
                identity = _graphiti_hit_identity(hit, len(hits))
                if identity in seen_hits:
                    continue
                seen_hits.add(identity)
                hits.append(hit)
            if hop + 1 < max_depth:
                next_terms.extend(_expansion_terms_from_hits(rows))

        frontier = []
        for term in next_terms:
            normalized = term.lower()
            if normalized in visited_queries:
                continue
            visited_queries.add(normalized)
            frontier.append(term)
            if len(frontier) >= expansion_limit:
                break

    return {
        "success": bool(base_search and base_search.success),
        "available": available,
        "base_search": base_search,
        "hits": hits[:20],
        "search_plan": search_plan,
        "warnings": warnings,
    }


async def _enrich_graphiti_hits(
    hits: list[dict[str, Any]],
    *,
    partition: str,
) -> dict[str, Any]:
    lookup_ids = _graphiti_lookup_ids_from_hits(hits)
    if not lookup_ids:
        return {"enabled": True, "success": True, "results": [], "warnings": []}
    lookup = await lookup_graphiti_uuids(uuids=lookup_ids, partition=partition)
    lookup_json = lookup.as_json()
    data = lookup_json.get("data") if isinstance(lookup_json.get("data"), dict) else {}
    results = data.get("results") if isinstance(data, dict) else []
    if not isinstance(results, list):
        results = []
    lookup_map = {
        str(item.get("uuid") or "").strip(): item
        for item in results
        if isinstance(item, dict) and str(item.get("uuid") or "").strip()
    }
    for hit in hits:
        _attach_graphiti_lookup(hit, lookup_map)
    warnings: list[str] = []
    if not lookup.success:
        warnings.append(f"graphiti_lookup_failed: {lookup.message}")
    return {
        "enabled": True,
        "success": lookup.success,
        "message": lookup.message,
        "results": results,
        "found_count": sum(1 for item in results if isinstance(item, dict) and item.get("found")),
        "requested_count": len(lookup_ids),
        "warnings": warnings,
    }


def _graphiti_lookup_ids_from_hits(hits: list[dict[str, Any]]) -> list[str]:
    values: list[str] = []
    for hit in hits:
        values.extend(
            [
                str(hit.get("uuid") or hit.get("graphiti_uuid") or ""),
                str(hit.get("source_node_uuid") or ""),
                str(hit.get("target_node_uuid") or ""),
            ]
        )
        values.extend(_episode_uuids_from_hit(hit))
    return _normalize_uuid_list(values)


def _attach_graphiti_lookup(
    hit: dict[str, Any],
    lookup_map: dict[str, dict[str, Any]],
) -> None:
    fact_uuid = str(hit.get("uuid") or hit.get("graphiti_uuid") or "").strip()
    source_uuid = str(hit.get("source_node_uuid") or "").strip()
    target_uuid = str(hit.get("target_node_uuid") or "").strip()
    episodes = [
        lookup_map[item]
        for item in _episode_uuids_from_hit(hit)
        if item in lookup_map
    ]
    lookup_payload = {
        "fact": lookup_map.get(fact_uuid, {}),
        "source_node": lookup_map.get(source_uuid, {}),
        "target_node": lookup_map.get(target_uuid, {}),
        "episodes": episodes,
    }
    hit["graphiti_lookup"] = lookup_payload
    raw = _graphiti_raw_payload(hit)
    if isinstance(raw, dict):
        raw = dict(raw)
        raw["lookup"] = lookup_payload
        hit["graphiti_raw"] = raw


async def _lookup_graphiti_uuid_local(
    driver: Any,
    uuid: str,
    *,
    partition: str,
    kind: str = "",
) -> dict[str, Any]:
    normalized = str(uuid or "").strip()
    if not normalized:
        return {"uuid": "", "found": False, "error": "empty_uuid"}
    scoped_driver = driver.with_database(partition) if hasattr(driver, "with_database") else driver

    for graphiti_kind, cls in _graphiti_lookup_classes(kind):
        try:
            obj = await cls.get_by_uuid(scoped_driver, normalized)
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            continue
        raw = _jsonable(obj)
        if not isinstance(raw, dict):
            raw = {"value": raw}
        group_id = str(raw.get("group_id") or "").strip()
        return {
            "uuid": normalized,
            "found": True,
            "graphiti_kind": graphiti_kind,
            "partition": group_id or partition,
            "matches_partition": not group_id or group_id == partition,
            "raw": raw,
        }
    return {
        "uuid": normalized,
        "found": False,
        "graphiti_kind": kind,
        "partition": partition,
        "error": locals().get("last_error", "not_found"),
    }


def _graphiti_lookup_classes(kind: str) -> list[tuple[str, Any]]:
    from graphiti_core.edges import EntityEdge, EpisodicEdge
    from graphiti_core.nodes import EntityNode, EpisodicNode

    all_classes = [
        ("entity_edge", EntityEdge),
        ("entity_node", EntityNode),
        ("episodic_node", EpisodicNode),
        ("episodic_edge", EpisodicEdge),
    ]
    normalized = str(kind or "").strip().lower()
    if not normalized:
        return all_classes
    aliases = {
        "fact": "entity_edge",
        "edge": "entity_edge",
        "entity": "entity_node",
        "node": "entity_node",
        "episode": "episodic_node",
    }
    wanted = aliases.get(normalized, normalized)
    first = [item for item in all_classes if item[0] == wanted]
    rest = [item for item in all_classes if item[0] != wanted]
    return first + rest


def _search_result_items(results: Any) -> list[Any]:
    """Flatten Graphiti search() and _search(SearchResults) shapes."""

    if results is None:
        return []
    if isinstance(results, dict):
        for key in ("edges", "nodes", "communities", "results"):
            raw = results.get(key)
            if isinstance(raw, list) and raw:
                break
        else:
            return [results]
        items: list[Any] = []
        for key in ("edges", "nodes", "communities", "results"):
            raw = results.get(key)
            if isinstance(raw, list):
                items.extend(raw)
        return items
    if any(hasattr(results, name) for name in ("edges", "nodes", "communities")):
        items = []
        for name in ("edges", "nodes", "communities"):
            raw = getattr(results, name, None)
            if isinstance(raw, (list, tuple)):
                items.extend(raw)
        return items
    try:
        return list(results)
    except TypeError:
        return [results]


def _normalize_uuid_list(values: list[str] | tuple[str, ...] | set[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        item = str(value or "").strip()
        if not item or item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def _with_search_context(
    hit: dict[str, Any],
    *,
    base_query: str,
    origin_query: str,
    strategy: str,
    depth: int,
    result_index: int,
) -> dict[str, Any]:
    row = dict(hit)
    context = row.get("search_context")
    if not isinstance(context, dict):
        context = {}
    row["search_context"] = {
        **context,
        "base_query": base_query,
        "origin_query": origin_query,
        "strategy": strategy,
        "depth": depth,
        "result_index": result_index,
    }
    row.setdefault("graphiti_origin_query", origin_query)
    row.setdefault("graphiti_search_strategy", strategy)
    row.setdefault("graphiti_search_depth", depth)
    return row


def _graphiti_hit_identity(hit: dict[str, Any], fallback_index: int) -> tuple[str, ...]:
    graphiti_uuid = str(hit.get("uuid") or hit.get("graphiti_uuid") or "").strip()
    if graphiti_uuid:
        return ("uuid", graphiti_uuid)
    source_uuid = str(hit.get("source_node_uuid") or "").strip()
    target_uuid = str(hit.get("target_node_uuid") or "").strip()
    text = " ".join(str(hit.get("text") or hit.get("summary") or hit.get("label") or "").split())
    if source_uuid or target_uuid:
        return ("edge", source_uuid, target_uuid, text[:200])
    if text:
        return ("text", text[:240])
    return ("index", str(fallback_index))


def _normalize_search_strategy(raw: str) -> str:
    value = str(raw or "").strip().lower().replace("-", "_")
    valid = {
        "hybrid",
        "iterative_hybrid",
        "node_distance",
        "combined_rrf",
        "combined_mmr",
        "combined_cross_encoder",
        "edge_rrf",
        "edge_mmr",
        "edge_node_distance",
        "edge_episode_mentions",
        "edge_cross_encoder",
        "node_rrf",
        "node_mmr",
        "node_node_distance",
        "node_episode_mentions",
        "node_cross_encoder",
        "community_rrf",
    }
    aliases = {
        "rrf": "combined_rrf",
        "mmr": "combined_mmr",
        "cross_encoder": "combined_cross_encoder",
        "episode_mentions": "edge_episode_mentions",
    }
    value = aliases.get(value, value)
    return value if value in valid else "hybrid"


def _normalize_search_recipe(raw: str) -> str:
    value = str(raw or "").strip().lower().replace("-", "_")
    if value in {"", "hybrid", "iterative_hybrid"}:
        return ""
    return _normalize_search_strategy(value)


def _graphiti_search_recipe_constant(recipe: str) -> str:
    normalized = _normalize_search_recipe(recipe)
    return {
        "combined_rrf": "COMBINED_HYBRID_SEARCH_RRF",
        "combined_mmr": "COMBINED_HYBRID_SEARCH_MMR",
        "combined_cross_encoder": "COMBINED_HYBRID_SEARCH_CROSS_ENCODER",
        "node_distance": "EDGE_HYBRID_SEARCH_NODE_DISTANCE",
        "edge_rrf": "EDGE_HYBRID_SEARCH_RRF",
        "edge_mmr": "EDGE_HYBRID_SEARCH_MMR",
        "edge_node_distance": "EDGE_HYBRID_SEARCH_NODE_DISTANCE",
        "edge_episode_mentions": "EDGE_HYBRID_SEARCH_EPISODE_MENTIONS",
        "edge_cross_encoder": "EDGE_HYBRID_SEARCH_CROSS_ENCODER",
        "node_rrf": "NODE_HYBRID_SEARCH_RRF",
        "node_mmr": "NODE_HYBRID_SEARCH_MMR",
        "node_node_distance": "NODE_HYBRID_SEARCH_NODE_DISTANCE",
        "node_episode_mentions": "NODE_HYBRID_SEARCH_EPISODE_MENTIONS",
        "node_cross_encoder": "NODE_HYBRID_SEARCH_CROSS_ENCODER",
        "community_rrf": "COMMUNITY_HYBRID_SEARCH_RRF",
    }.get(normalized, "")


def _string_list(value: Any) -> list[str]:
    raw = value
    if isinstance(raw, str):
        raw = raw.split(",")
    if not isinstance(raw, (list, tuple, set)):
        return []
    result: list[str] = []
    seen: set[str] = set()
    for item in raw:
        text = str(item or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result[:20]


def _safe_depth(value: Any, *, strategy: str) -> int:
    default = 2 if strategy == "iterative_hybrid" else 1
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, min(parsed, 3))


def _expansion_terms_from_hits(hits: list[dict[str, Any]]) -> list[str]:
    terms: list[str] = []
    seen: set[str] = set()
    for hit in hits:
        for term in _expansion_terms_from_hit(hit):
            normalized = term.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            terms.append(term)
    return terms


def _expansion_terms_from_hit(hit: dict[str, Any]) -> list[str]:
    raw = _graphiti_raw_payload(hit)
    source_name = _endpoint_name_from_raw(raw, "source") or str(
        hit.get("source_node_name") or ""
    ).strip()
    target_name = _endpoint_name_from_raw(raw, "target") or str(
        hit.get("target_node_name") or ""
    ).strip()
    candidates: list[str] = []
    if source_name and target_name:
        candidates.append(f"{source_name} {target_name}")
    candidates.extend([source_name, target_name])
    text = str(hit.get("text") or hit.get("summary") or hit.get("label") or "").strip()
    if text:
        candidates.append(_label_from_text(text, fallback=text[:120]))
    clean_terms: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        term = " ".join(str(candidate or "").split())[:160]
        if len(term) < 3:
            continue
        normalized = term.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        clean_terms.append(term)
    return clean_terms


def _endpoint_name_from_raw(raw: dict[str, Any], role: str) -> str:
    node = raw.get(f"{role}_node")
    if isinstance(node, dict):
        for key in ("name", "label", "title", "uuid"):
            value = str(node.get(key) or "").strip()
            if value:
                return value
    for key in (f"{role}_node_name", f"{role}_name"):
        value = str(raw.get(key) or "").strip()
        if value:
            return value
    return ""


def _partition_values() -> list[str]:
    return PARTITIONS.values()


def _normalize_partition(raw: str) -> str:
    value = (raw or "").strip().lower()
    return value if value in _partition_values() else PARTITIONS.GOSLO


def _graphiti_core_installed() -> bool:
    try:
        import graphiti_core  # noqa: F401
    except ImportError:
        return False
    return True


def _remote_graphiti_base_url() -> str:
    """Return the read-through Graphiti monitor URL for local Web Console.

    The React console often runs in a lightweight Web BFF process that does not
    install the optional Graphiti/FalkorDB dependencies. In that case reads can
    safely proxy to the app-monitor developer console, which owns the real
    Graphiti dependency and partition status. Writes still stay explicit and
    operator-gated in their own routes.
    """

    return str(
        os.getenv("PARROT_WEB_CONSOLE_GRAPHITI_URL")
        or os.getenv("PARROT_GRAPHITI_REMOTE_URL")
        or ""
    ).rstrip("/")


def _remote_graphiti_timeout_s() -> float:
    raw = os.getenv("PARROT_WEB_CONSOLE_GRAPHITI_TIMEOUT_S", "60.0")
    try:
        return max(0.5, min(float(raw), 300.0))
    except ValueError:
        return 60.0


def _remote_graphiti_request(
    path: str,
    *,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Call the app-monitor Graphiti API without leaking secrets to the browser."""

    base_url = _remote_graphiti_base_url()
    if not base_url:
        return {
            "success": False,
            "available": False,
            "error": "remote_graphiti_url_not_configured",
        }
    url = f"{base_url}/{path.lstrip('/')}"
    data = None
    headers = {"Accept": "application/json"}
    method = "GET"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
        method = "POST"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=_remote_graphiti_timeout_s()) as response:
            raw = response.read().decode("utf-8")
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
        return {"success": False, "available": False, "error": "remote_graphiti_non_object_response"}
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        return {
            "success": False,
            "available": False,
            "error": f"{type(exc).__name__}: {exc}",
        }


def _serialize_search_hit(hit: Any) -> dict[str, Any]:
    text = (
        _hit_value(hit, "fact")
        or _hit_value(hit, "text")
        or _hit_value(hit, "name")
        or _hit_value(hit, "summary")
        or str(hit)
    )
    raw = _graphiti_raw_payload(hit)
    graphiti_kind = _graphiti_kind_from_search_hit(hit, raw)
    return {
        "text": str(text)[:800],
        "score": _hit_value(hit, "score"),
        "uuid": _hit_value(hit, "uuid") or "",
        "graphiti_kind": graphiti_kind,
        "source_node_uuid": _hit_value(hit, "source_node_uuid") or "",
        "target_node_uuid": _hit_value(hit, "target_node_uuid") or "",
        "source_url": _hit_value(hit, "source_url") or "",
        "source_description": _hit_value(hit, "source_description") or "",
        "graphiti_raw": raw,
    }


def _hit_value(hit: Any, key: str) -> Any:
    if isinstance(hit, dict):
        return hit.get(key)
    return getattr(hit, key, None)


def _graphiti_kind_from_search_hit(hit: Any, raw: dict[str, Any]) -> str:
    value = ""
    if isinstance(hit, dict):
        value = str(hit.get("graphiti_kind") or hit.get("kind") or "")
    if not value:
        labels = raw.get("labels")
        if isinstance(labels, list) and any("Community" in str(item) for item in labels):
            value = "community"
        elif isinstance(labels, list) and any("Episodic" in str(item) for item in labels):
            value = "episode"
    if not value and (
        _hit_value(hit, "fact")
        or _hit_value(hit, "source_node_uuid")
        or _hit_value(hit, "target_node_uuid")
        or raw.get("fact")
    ):
        value = "edge"
    if not value and (_hit_value(hit, "name") or raw.get("name")):
        value = "entity"
    return value or "result"


def _empty_subgraph(*, query: str, partition: str) -> dict[str, Any]:
    return {"query": query.strip(), "partition": partition, "nodes": [], "edges": []}


def _hits_to_subgraph(
    hits: list[dict[str, Any]],
    *,
    query: str,
    partition: str,
) -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []
    for index, hit in enumerate(hits):
        node_id = _graphiti_node_id(hit, index)
        text = str(hit.get("text") or "").strip()
        _put_subgraph_hit_node(
            nodes,
            node_id,
            {
                "id": node_id,
                "label": _label_from_text(text, fallback=f"Graphiti hit {index + 1}"),
                "kind": _subgraph_hit_kind(hit),
                "partition": partition,
                "graphiti_uuid": str(hit.get("uuid") or ""),
                "score": hit.get("score"),
                "summary": text[:280],
                "source_url": str(hit.get("source_url") or ""),
                "source_description": str(hit.get("source_description") or ""),
                "search_context": _jsonable(hit.get("search_context") or {}),
                "graphiti_raw": _graphiti_raw_payload(hit),
            },
        )
        source_uuid = str(hit.get("source_node_uuid") or "").strip()
        target_uuid = str(hit.get("target_node_uuid") or "").strip()
        if source_uuid:
            nodes.setdefault(
                f"graphiti:{source_uuid}",
                {
                    "id": f"graphiti:{source_uuid}",
                    "label": _endpoint_label(hit, "source", fallback=source_uuid[:12]),
                    "kind": "graphiti_source",
                    "partition": partition,
                    "graphiti_uuid": source_uuid,
                    "graphiti_raw": _endpoint_raw(hit, "source"),
                },
            )
        if target_uuid:
            nodes.setdefault(
                f"graphiti:{target_uuid}",
                {
                    "id": f"graphiti:{target_uuid}",
                    "label": _endpoint_label(hit, "target", fallback=target_uuid[:12]),
                    "kind": "graphiti_target",
                    "partition": partition,
                    "graphiti_uuid": target_uuid,
                    "graphiti_raw": _endpoint_raw(hit, "target"),
                },
            )
        if source_uuid and target_uuid:
            edges.append(
                {
                    "id": f"graphiti:{source_uuid}->{target_uuid}:{index}",
                    "source": f"graphiti:{source_uuid}",
                    "target": f"graphiti:{target_uuid}",
                    "kind": "graphiti_fact",
                    "label": _label_from_text(text, fallback="fact"),
                    "hit_id": node_id,
                    "graphiti_uuid": str(hit.get("uuid") or hit.get("graphiti_uuid") or ""),
                    "search_context": _jsonable(hit.get("search_context") or {}),
                }
            )
    return {
        "query": query.strip(),
        "partition": partition,
        "nodes": list(nodes.values()),
        "edges": edges,
    }


def _subgraph_hit_kind(hit: dict[str, Any]) -> str:
    kind = str(hit.get("graphiti_kind") or hit.get("kind") or "").strip().lower()
    if kind in {"edge", "fact", "entity_edge", "graphiti_fact"}:
        return "graphiti_fact"
    if kind in {"entity", "node", "entity_node", "graphiti_entity"}:
        return "graphiti_entity"
    if kind in {"community", "community_node", "graphiti_community"}:
        return "graphiti_community"
    if kind in {"episode", "episodic_node", "graphiti_episode"}:
        return "graphiti_episode"
    return "graphiti_result"


def _put_subgraph_hit_node(
    nodes: dict[str, dict[str, Any]],
    node_id: str,
    payload: dict[str, Any],
) -> None:
    existing = nodes.get(node_id)
    if existing is None:
        nodes[node_id] = payload
        return
    if str(payload.get("kind") or "") == "graphiti_fact":
        return
    for key in (
        "label",
        "kind",
        "score",
        "summary",
        "source_url",
        "source_description",
        "search_context",
        "graphiti_raw",
    ):
        value = payload.get(key)
        if value not in ("", None, {}, []):
            existing[key] = value


def _endpoint_label(hit: dict[str, Any], role: str, *, fallback: str) -> str:
    lookup_raw = _lookup_raw_for_endpoint(hit, role)
    for key in ("name", "label", "title", "uuid"):
        value = str(lookup_raw.get(key) or "").strip()
        if value:
            return value
    raw = _graphiti_raw_payload(hit)
    name = _endpoint_name_from_raw(raw, role)
    return name or fallback


def _endpoint_raw(hit: dict[str, Any], role: str) -> dict[str, Any]:
    lookup_raw = _lookup_raw_for_endpoint(hit, role)
    if lookup_raw:
        return lookup_raw
    raw = _graphiti_raw_payload(hit)
    node = raw.get(f"{role}_node")
    if isinstance(node, dict):
        return _jsonable(node)
    uuid = str(hit.get(f"{role}_node_uuid") or "").strip()
    return {"uuid": uuid, "role": role} if uuid else {"role": role}


def _lookup_raw_for_endpoint(hit: dict[str, Any], role: str) -> dict[str, Any]:
    lookup = hit.get("graphiti_lookup")
    if not isinstance(lookup, dict):
        return {}
    row = lookup.get(f"{role}_node")
    if not isinstance(row, dict):
        return {}
    raw = row.get("raw")
    return _jsonable(raw) if isinstance(raw, dict) else {}


def _hits_to_edge_drafts(
    hits: list[dict[str, Any]],
    *,
    partition: str,
) -> list[dict[str, Any]]:
    """Describe Graphiti fact edges without pretending they are L2-B edges yet."""

    edge_drafts: list[dict[str, Any]] = []
    for index, hit in enumerate(hits[:20]):
        source_uuid = str(hit.get("source_node_uuid") or "").strip()
        target_uuid = str(hit.get("target_node_uuid") or "").strip()
        if not source_uuid or not target_uuid:
            continue
        text = str(hit.get("text") or hit.get("summary") or hit.get("label") or "").strip()
        graphiti_uuid = str(hit.get("uuid") or hit.get("graphiti_uuid") or "").strip()
        raw_envelope = _hit_raw_envelope(hit, partition=partition, index=index)
        edge_drafts.append(
            {
                "kind": "graphiti_fact",
                "label": _label_from_text(text, fallback=f"Graphiti fact {index + 1}"),
                "source_graphiti_uuid": source_uuid,
                "target_graphiti_uuid": target_uuid,
                "hit_graphiti_uuid": graphiti_uuid,
                "strength": _safe_float(hit.get("score"), 0.5),
                "meta": {
                    "source_tool": "web_console.graphiti_subgraph_export",
                    "graphiti_partition": partition,
                    "graphiti_hit_uuid": graphiti_uuid,
                    "fact_text": text[:800],
                    "graphiti_raw": raw_envelope,
                },
                "write_policy": "requires_resolved_l2b_node_uuid",
            }
        )
    return edge_drafts


def _hits_to_raw_envelopes(
    hits: list[dict[str, Any]],
    *,
    partition: str,
) -> list[dict[str, Any]]:
    return [
        _hit_raw_envelope(hit, partition=partition, index=index)
        for index, hit in enumerate(hits[:20])
    ]


def _hit_raw_envelope(
    hit: dict[str, Any],
    *,
    partition: str,
    index: int,
) -> dict[str, Any]:
    text = str(hit.get("text") or hit.get("summary") or hit.get("label") or "").strip()
    graphiti_uuid = str(hit.get("uuid") or hit.get("graphiti_uuid") or "").strip()
    source_node_uuid = str(hit.get("source_node_uuid") or "").strip()
    target_node_uuid = str(hit.get("target_node_uuid") or "").strip()
    raw = _graphiti_raw_payload(hit)
    kind = str(hit.get("graphiti_kind") or hit.get("kind") or "graphiti_fact")
    graphiti_edge_uuid = (
        graphiti_uuid
        if _graphiti_bundle_is_fact(
            kind.strip().lower(),
            {"source_node_uuid": source_node_uuid, "target_node_uuid": target_node_uuid},
            raw,
        )
        else ""
    )
    return {
        "schema_version": 1,
        "kind": kind,
        "partition": partition,
        "index": index,
        "uuid": graphiti_uuid,
        "graphiti_edge_uuid": graphiti_edge_uuid,
        "graphiti_node_uuid": "" if graphiti_edge_uuid else graphiti_uuid,
        "source_node_uuid": source_node_uuid,
        "target_node_uuid": target_node_uuid,
        "episode_uuids": _episode_uuids_from_hit(hit),
        "source_url": str(hit.get("source_url") or ""),
        "source_description": str(hit.get("source_description") or ""),
        "score": hit.get("score"),
        "label": _label_from_text(text, fallback=f"Graphiti hit {index + 1}"),
        "text": text,
        "search_context": _jsonable(hit.get("search_context") or {}),
        "graphiti_lookup": _jsonable(hit.get("graphiti_lookup") or {}),
        "hit": _graphiti_hit_fields(hit),
        "raw": raw,
    }


def _graphiti_hit_fields(hit: dict[str, Any]) -> dict[str, Any]:
    """Keep Web/search wrapper fields beside Graphiti's raw object."""

    omitted = {"graphiti_raw", "raw"}
    return {
        str(key): _jsonable(value)
        for key, value in hit.items()
        if key not in omitted
    }


def _hits_to_identity_ref_drafts(
    raw_envelopes: list[dict[str, Any]],
    *,
    partition: str,
) -> list[dict[str, Any]]:
    drafts: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for envelope in raw_envelopes:
        graphiti_edge_uuid = str(envelope.get("graphiti_edge_uuid") or "").strip()
        graphiti_record_uuid = str(
            envelope.get("graphiti_node_uuid") or envelope.get("uuid") or ""
        ).strip()
        source_node_uuid = str(envelope.get("source_node_uuid") or "").strip()
        target_node_uuid = str(envelope.get("target_node_uuid") or "").strip()
        source_url = str(envelope.get("source_url") or "").strip()
        label = str(envelope.get("label") or "").strip()
        if graphiti_edge_uuid:
            drafts.append(
                _identity_ref_draft(
                    key=("graphiti_edge_uuid", graphiti_edge_uuid),
                    seen=seen,
                    payload={
                        "graphiti_edge_uuid": graphiti_edge_uuid,
                        "alias": label,
                        "confidence": _safe_float(envelope.get("score"), 0.5),
                        "resolution_state": "weak",
                        "ref_id": f"graphiti:{partition}:fact:{graphiti_edge_uuid}",
                        "ref_kind": "graphiti_fact",
                        "url": source_url,
                        "graphiti_raw": envelope,
                        "meta": {
                            "source_tool": "web_console.graphiti_subgraph_export",
                            "graphiti_partition": partition,
                            "graphiti_raw_kind": "fact",
                        },
                    },
                )
            )
        elif graphiti_record_uuid:
            raw = _jsonable(envelope.get("raw") or {})
            labels = raw.get("labels") if isinstance(raw.get("labels"), list) else []
            kind = str(envelope.get("kind") or "").strip().lower()
            if _graphiti_bundle_is_episode(kind, labels):
                ref_kind = "graphiti_episode"
                suffix = "episode"
            elif _graphiti_bundle_is_community(kind, labels):
                ref_kind = "graphiti_community"
                suffix = "community"
            else:
                ref_kind = "graphiti_entity"
                suffix = "entity"
            drafts.append(
                _identity_ref_draft(
                    key=(f"{ref_kind}_uuid", graphiti_record_uuid),
                    seen=seen,
                    payload={
                        "graphiti_record_uuid": graphiti_record_uuid,
                        "alias": label or graphiti_record_uuid[:12],
                        "confidence": _safe_float(envelope.get("score"), 0.5),
                        "resolution_state": "weak",
                        "ref_id": f"graphiti:{partition}:{suffix}:{graphiti_record_uuid}",
                        "ref_kind": ref_kind,
                        "url": source_url,
                        "graphiti_raw": envelope,
                        "meta": {
                            "source_tool": "web_console.graphiti_subgraph_export",
                            "graphiti_partition": partition,
                            "graphiti_raw_kind": suffix,
                        },
                    },
                )
            )
        for role, entity_uuid in (
            ("source", source_node_uuid),
            ("target", target_node_uuid),
        ):
            if not entity_uuid:
                continue
            drafts.append(
                _identity_ref_draft(
                    key=("graphiti_entity_uuid", entity_uuid),
                    seen=seen,
                    payload={
                        "graphiti_entity_uuid": entity_uuid,
                        "alias": entity_uuid[:12],
                        "confidence": _safe_float(envelope.get("score"), 0.5),
                        "resolution_state": "weak",
                        "ref_id": f"graphiti:{partition}:entity:{entity_uuid}",
                        "ref_kind": "graphiti_entity",
                        "url": source_url,
                        "graphiti_raw": {
                            "schema_version": 1,
                            "kind": "graphiti_entity_pointer",
                            "partition": partition,
                            "uuid": entity_uuid,
                            "endpoint_role": role,
                            "parent_edge_uuid": graphiti_edge_uuid,
                            "parent_fact": envelope,
                        },
                        "meta": {
                            "source_tool": "web_console.graphiti_subgraph_export",
                            "graphiti_partition": partition,
                            "graphiti_raw_kind": "entity_pointer",
                        },
                    },
                )
            )
        for episode_uuid in envelope.get("episode_uuids") or []:
            drafts.append(
                _identity_ref_draft(
                    key=("graphiti_episode_uuid", str(episode_uuid)),
                    seen=seen,
                    payload={
                        "graphiti_episode_uuid": str(episode_uuid),
                        "alias": str(episode_uuid)[:12],
                        "confidence": _safe_float(envelope.get("score"), 0.5),
                        "resolution_state": "weak",
                        "ref_id": f"graphiti:{partition}:episode:{episode_uuid}",
                        "ref_kind": "graphiti_episode",
                        "url": source_url,
                        "graphiti_raw": {
                            "schema_version": 1,
                            "kind": "graphiti_episode_pointer",
                            "partition": partition,
                            "uuid": str(episode_uuid),
                            "parent_edge_uuid": graphiti_edge_uuid,
                            "parent_fact": envelope,
                        },
                        "meta": {
                            "source_tool": "web_console.graphiti_subgraph_export",
                            "graphiti_partition": partition,
                            "graphiti_raw_kind": "episode_pointer",
                        },
                    },
                )
            )
    return [draft for draft in drafts if draft]


def _identity_ref_draft(
    *,
    key: tuple[str, str],
    seen: set[tuple[str, str]],
    payload: dict[str, Any],
) -> dict[str, Any]:
    if not key[1] or key in seen:
        return {}
    seen.add(key)
    return {
        **payload,
        "dry_run": True,
        "operator_mode": False,
        "apply_route": "/api/memory/identity-ref-index/apply",
        "write_policy": "draft_only_from_graphiti_export",
    }


def _graphiti_subgraph_bundle(
    *,
    hits: list[dict[str, Any]],
    partition: str,
    query: str,
    subgraph: dict[str, Any] | None = None,
    raw_envelopes: list[dict[str, Any]] | None = None,
    edge_drafts: list[dict[str, Any]] | None = None,
    identity_ref_drafts: list[dict[str, Any]] | None = None,
    search_plan: list[dict[str, Any]] | None = None,
    graphiti_lookup: dict[str, Any] | None = None,
    strategy: str = "",
    depth: int = 1,
    expansion_limit: int = 0,
    search_recipe: str = "",
    node_labels: list[str] | None = None,
    edge_types: list[str] | None = None,
) -> dict[str, Any]:
    """Preserve the Graphiti search slice before any L2-B projection.

    The bundle is intentionally not an L2-B graph. It keeps Graphiti's facts,
    endpoint nodes, episode lookup rows, search plan, and raw payloads as one
    reviewable package so later L1.5/L2-B layers can add overlays without
    losing Graphiti's own relation extraction.
    """

    bounded_hits = [dict(hit) for hit in hits[:20] if isinstance(hit, dict)]
    envelopes = (
        [row for row in raw_envelopes if isinstance(row, dict)]
        if raw_envelopes is not None
        else _hits_to_raw_envelopes(bounded_hits, partition=partition)
    )
    graph = (
        dict(subgraph)
        if isinstance(subgraph, dict)
        else _hits_to_subgraph(bounded_hits, query=query, partition=partition)
    )
    edges = (
        [row for row in edge_drafts if isinstance(row, dict)]
        if edge_drafts is not None
        else _hits_to_edge_drafts(bounded_hits, partition=partition)
    )
    identity_refs = (
        [row for row in identity_ref_drafts if isinstance(row, dict)]
        if identity_ref_drafts is not None
        else _hits_to_identity_ref_drafts(envelopes, partition=partition)
    )
    sections = _graphiti_bundle_sections(envelopes, partition=partition)
    return _jsonable(
        {
            "schema_version": 1,
            "bundle_kind": "graphiti_search_subgraph_bundle",
            "source_tool": "web_console.graphiti_subgraph",
            "partition": partition,
            "query": str(query or "").strip(),
            "selection": _graphiti_bundle_selection(envelopes, sections),
            "search": {
                "strategy": str(strategy or ""),
                "depth": int(depth or 1),
                "expansion_limit": int(expansion_limit or 0),
                "search_recipe": str(search_recipe or ""),
                "node_labels": list(node_labels or []),
                "edge_types": list(edge_types or []),
                "search_plan": list(search_plan or []),
                "lookup": dict(graphiti_lookup or {}),
            },
            "sections": sections,
            "subgraph": graph,
            "raw_envelopes": envelopes,
            "edge_drafts": edges,
            "identity_ref_drafts": identity_refs,
            "l2b_projection_policy": _graphiti_bundle_projection_policy(),
        }
    )


def _graphiti_bundle_sections(
    raw_envelopes: list[dict[str, Any]],
    *,
    partition: str,
) -> dict[str, list[dict[str, Any]]]:
    facts: list[dict[str, Any]] = []
    entities: list[dict[str, Any]] = []
    episodes: list[dict[str, Any]] = []
    communities: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()

    for envelope in raw_envelopes:
        raw = _jsonable(envelope.get("raw") or {})
        if not isinstance(raw, dict):
            raw = {"value": raw}
        kind = str(envelope.get("kind") or "").strip().lower()
        labels = raw.get("labels") if isinstance(raw.get("labels"), list) else []
        if _graphiti_bundle_is_community(kind, labels):
            _append_graphiti_bundle_item(
                communities,
                seen,
                kind="graphiti_community",
                partition=partition,
                uuid=str(envelope.get("uuid") or raw.get("uuid") or ""),
                raw=raw,
                extra={"source_envelope": envelope},
            )
        elif _graphiti_bundle_is_fact(kind, envelope, raw):
            _append_graphiti_bundle_item(
                facts,
                seen,
                kind="graphiti_fact",
                partition=partition,
                uuid=str(envelope.get("uuid") or raw.get("uuid") or ""),
                raw=raw,
                extra={"source_envelope": envelope},
            )
        elif _graphiti_bundle_is_episode(kind, labels):
            _append_graphiti_bundle_item(
                episodes,
                seen,
                kind="graphiti_episode",
                partition=partition,
                uuid=str(envelope.get("uuid") or raw.get("uuid") or ""),
                raw=raw,
                extra={"source_envelope": envelope},
            )
        else:
            _append_graphiti_bundle_item(
                entities,
                seen,
                kind="graphiti_entity",
                partition=partition,
                uuid=str(envelope.get("uuid") or raw.get("uuid") or ""),
                raw=raw,
                extra={"source_envelope": envelope},
            )

        for role in ("source", "target"):
            entity_raw = _graphiti_bundle_endpoint_raw(envelope, role)
            entity_uuid = str(
                entity_raw.get("uuid") or envelope.get(f"{role}_node_uuid") or ""
            ).strip()
            if not entity_uuid and not entity_raw:
                continue
            _append_graphiti_bundle_item(
                entities,
                seen,
                kind="graphiti_entity",
                partition=partition,
                uuid=entity_uuid,
                raw=entity_raw or {"uuid": entity_uuid},
                extra={
                    "endpoint_role": role,
                    "parent_fact_uuid": str(
                        envelope.get("graphiti_edge_uuid") or envelope.get("uuid") or ""
                    ),
                    "parent_fact": envelope,
                },
            )

        for episode_row in _graphiti_bundle_episode_rows(envelope):
            episode_raw = episode_row.get("raw") if isinstance(episode_row.get("raw"), dict) else episode_row
            episode_uuid = str(episode_row.get("uuid") or episode_raw.get("uuid") or "").strip()
            _append_graphiti_bundle_item(
                episodes,
                seen,
                kind="graphiti_episode",
                partition=partition,
                uuid=episode_uuid,
                raw=episode_raw,
                extra={
                    "lookup": episode_row,
                    "parent_fact_uuid": str(
                        envelope.get("graphiti_edge_uuid") or envelope.get("uuid") or ""
                    ),
                    "parent_fact": envelope,
                },
            )
        for episode_uuid in envelope.get("episode_uuids") or []:
            _append_graphiti_bundle_item(
                episodes,
                seen,
                kind="graphiti_episode",
                partition=partition,
                uuid=str(episode_uuid),
                raw={"uuid": str(episode_uuid), "pointer_only": True},
                extra={
                    "parent_fact_uuid": str(
                        envelope.get("graphiti_edge_uuid") or envelope.get("uuid") or ""
                    ),
                    "parent_fact": envelope,
                },
            )

    return {
        "facts": facts,
        "entities": entities,
        "episodes": episodes,
        "communities": communities,
    }


def _graphiti_bundle_is_fact(
    kind: str,
    envelope: dict[str, Any],
    raw: dict[str, Any],
) -> bool:
    return (
        kind in {"edge", "fact", "entity_edge", "graphiti_fact", "episodic_edge"}
        or bool(envelope.get("source_node_uuid"))
        or bool(envelope.get("target_node_uuid"))
        or bool(raw.get("fact"))
    )


def _graphiti_bundle_is_community(kind: str, labels: list[Any]) -> bool:
    return kind in {"community", "community_node", "graphiti_community"} or any(
        "community" in str(label).lower() for label in labels
    )


def _graphiti_bundle_is_episode(kind: str, labels: list[Any]) -> bool:
    return kind in {"episode", "episodic_node", "graphiti_episode"} or any(
        "episode" in str(label).lower() for label in labels
    )


def _graphiti_bundle_endpoint_raw(
    envelope: dict[str, Any],
    role: str,
) -> dict[str, Any]:
    lookup = envelope.get("graphiti_lookup")
    if isinstance(lookup, dict):
        row = lookup.get(f"{role}_node")
        if isinstance(row, dict):
            raw = row.get("raw")
            if isinstance(raw, dict):
                return _jsonable(raw)
            if row:
                return _jsonable(row)
    raw = envelope.get("raw")
    if isinstance(raw, dict):
        node = raw.get(f"{role}_node")
        if isinstance(node, dict):
            return _jsonable(node)
    uuid = str(envelope.get(f"{role}_node_uuid") or "").strip()
    return {"uuid": uuid, "pointer_only": True} if uuid else {}


def _graphiti_bundle_episode_rows(envelope: dict[str, Any]) -> list[dict[str, Any]]:
    lookup = envelope.get("graphiti_lookup")
    if not isinstance(lookup, dict):
        return []
    rows = lookup.get("episodes")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _append_graphiti_bundle_item(
    items: list[dict[str, Any]],
    seen: set[tuple[str, str, str]],
    *,
    kind: str,
    partition: str,
    uuid: str,
    raw: dict[str, Any],
    extra: dict[str, Any] | None = None,
) -> None:
    identity_uuid = str(uuid or raw.get("uuid") or "").strip()
    if not identity_uuid:
        identity_uuid = str(len(items))
    key = (kind, partition, identity_uuid)
    if key in seen:
        return
    seen.add(key)
    items.append(
        {
            "schema_version": 1,
            "kind": kind,
            "partition": partition,
            "uuid": identity_uuid if uuid or raw.get("uuid") else "",
            "raw": _jsonable(raw),
            **(extra or {}),
        }
    )


def _graphiti_bundle_selection(
    raw_envelopes: list[dict[str, Any]],
    sections: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    hit_uuids = _normalize_uuid_list(
        [
            str(row.get("uuid") or row.get("graphiti_edge_uuid") or "")
            for row in raw_envelopes
        ]
    )
    fact_uuids = _normalize_uuid_list(
        [str(row.get("uuid") or "") for row in sections.get("facts", [])]
    )
    node_uuids = _normalize_uuid_list(
        [
            *[
                str(row.get("source_node_uuid") or "")
                for row in raw_envelopes
            ],
            *[
                str(row.get("target_node_uuid") or "")
                for row in raw_envelopes
            ],
            *[
                str(row.get("uuid") or "")
                for row in sections.get("entities", [])
            ],
        ]
    )
    episode_uuids = _normalize_uuid_list(
        [
            *[
                str(item)
                for row in raw_envelopes
                for item in (row.get("episode_uuids") or [])
            ],
            *[
                str(row.get("uuid") or "")
                for row in sections.get("episodes", [])
            ],
        ]
    )
    community_uuids = _normalize_uuid_list(
        [str(row.get("uuid") or "") for row in sections.get("communities", [])]
    )
    return {
        "selected_count": len(raw_envelopes),
        "hit_uuids": hit_uuids,
        "fact_uuids": fact_uuids,
        "node_uuids": node_uuids,
        "episode_uuids": episode_uuids,
        "community_uuids": community_uuids,
        "section_counts": {
            name: len(rows)
            for name, rows in sections.items()
        },
    }


def _graphiti_bundle_projection_policy() -> dict[str, Any]:
    return {
        "preserve_raw_graphiti": True,
        "direct_graphiti_write": False,
        "direct_falkordb_write": False,
        "l1_5_write_path": "L15Pool.admit(Observation(source=USER_EXPLICIT))",
        "l2b_role": (
            "Store Graphiti UUID/raw envelopes and add lightweight placement, "
            "identity, and ref-binding overlays without replacing Graphiti facts."
        ),
        "edge_materialization_policy": "requires_resolved_l2b_node_uuid",
        "ref_policy": (
            "Refs are IdentityRefIndex/RefBinding previews here; apply through "
            "operator-gated routes after UUID resolution."
        ),
    }


def _extract_export_hits(body: dict[str, Any]) -> list[dict[str, Any]]:
    raw = body.get("hits")
    if raw is None:
        raw = body.get("selected_hits")
    if raw is None:
        raw = body.get("results")
    if raw is None:
        raw = (body.get("subgraph") or {}).get("nodes") if isinstance(body.get("subgraph"), dict) else []
    if not isinstance(raw, list):
        return []
    hits: list[dict[str, Any]] = []
    for item in raw[:20]:
        if isinstance(item, dict):
            hits.append(dict(item))
        elif isinstance(item, str) and item.strip():
            hits.append({"text": item.strip()})
    return hits


def _hit_to_l15_observation_draft(
    hit: dict[str, Any],
    *,
    partition: str,
    index: int,
) -> dict[str, Any]:
    text = str(hit.get("text") or hit.get("summary") or hit.get("label") or "").strip()
    label = _label_from_text(text, fallback=f"Graphiti export {index + 1}")[:128]
    graphiti_uuid = str(hit.get("uuid") or hit.get("graphiti_uuid") or "").strip()
    source_node_uuid = str(hit.get("source_node_uuid") or "").strip()
    target_node_uuid = str(hit.get("target_node_uuid") or "").strip()
    source_url = str(hit.get("source_url") or "").strip()
    source_description = str(hit.get("source_description") or "").strip()
    raw_envelope = _hit_raw_envelope(hit, partition=partition, index=index)
    return {
        "source": "user_explicit",
        "provenance_stream_id": f"web:graphiti:{partition}:{graphiti_uuid or index}",
        "graphiti_uuid": graphiti_uuid,
        "label": label,
        "kind": _normalize_node_kind(str(hit.get("kind") or "object")),
        "description": text[:400],
        "confidence": _safe_float(hit.get("confidence"), 0.78),
        "confirmation": str(hit.get("confirmation") or "confirmed"),
        "meta": {
            "source_tool": "web_console.graphiti_subgraph_export",
            "graphiti_partition": partition,
            "graphiti_hit_uuid": graphiti_uuid,
            "graphiti_source_node_uuid": source_node_uuid,
            "graphiti_target_node_uuid": target_node_uuid,
            "graphiti_score": hit.get("score"),
            "source_url": source_url,
            "source_description": source_description,
            "fact_text": text[:800],
            "graphiti_raw": raw_envelope,
        },
    }


def _graphiti_node_id(hit: dict[str, Any], index: int) -> str:
    uuid = str(hit.get("uuid") or hit.get("graphiti_uuid") or "").strip()
    return f"graphiti:{uuid}" if uuid else f"graphiti:hit:{index}"


def _label_from_text(text: str, *, fallback: str) -> str:
    cleaned = " ".join((text or "").split())
    if not cleaned:
        return fallback
    for separator in (".", "。", ":", "：", "\n"):
        if separator in cleaned:
            cleaned = cleaned.split(separator, 1)[0]
            break
    return cleaned[:80] or fallback


def _normalize_node_kind(raw: str) -> str:
    value = raw.strip().lower()
    return value if value in {"object", "surface", "zone", "person", "event", "photo"} else "object"


def _safe_float(value: Any, fallback: float) -> float:
    try:
        return max(0.0, min(float(value), 1.0))
    except (TypeError, ValueError):
        return fallback


def _safe_limit(value: Any, *, default: int, maximum: int) -> int:
    try:
        return max(1, min(int(value), maximum))
    except (TypeError, ValueError):
        return default


def _body_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "model_dump"):
        try:
            return _jsonable(value.model_dump(mode="json"))
        except TypeError:
            return _jsonable(value.model_dump())
    if hasattr(value, "dict") and not isinstance(value, dict):
        try:
            return _jsonable(value.dict())
        except TypeError:
            pass
    if hasattr(value, "as_json"):
        return value.as_json()
    if hasattr(value, "__dataclass_fields__"):
        return {
            key: _jsonable(getattr(value, key))
            for key in value.__dataclass_fields__  # type: ignore[attr-defined]
        }
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if hasattr(value, "value"):
        return _jsonable(value.value)
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except TypeError:
            pass
    return str(value)


def _graphiti_raw_payload(hit: Any) -> dict[str, Any]:
    raw_candidate: Any = hit
    if isinstance(hit, dict):
        raw_candidate = hit.get("graphiti_raw") or hit.get("raw") or hit
    raw = _jsonable(raw_candidate)
    if isinstance(raw, dict):
        return raw
    return {"value": raw}


def _episode_uuids_from_hit(hit: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for key in (
        "episode_uuid",
        "episode_uuids",
        "episodes",
        "source_episode_uuid",
        "source_episode_uuids",
    ):
        raw = hit.get(key)
        if isinstance(raw, (list, tuple, set)):
            values.extend(str(item).strip() for item in raw if str(item).strip())
        elif raw is not None and str(raw).strip():
            values.append(str(raw).strip())
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _graphiti_receipt(
    *,
    action: str,
    success: bool,
    dry_run: bool,
    operator_mode: bool,
    data: dict[str, Any],
) -> dict[str, Any]:
    return {
        "action": action,
        "success": success,
        "dry_run": dry_run,
        "operator_mode": operator_mode,
        "receipt_id": (
            f"web_{action.replace('.', '_')}_"
            f"{_dt.datetime.now(_dt.timezone.utc).timestamp():.0f}"
        ),
        "data": data,
        "audit": {
            "web_only": True,
            "default_mode": "dry_run",
            "write_boundary": "L1.5",
            "direct_falkordb_write": False,
            "app_dto": False,
        },
    }


__all__ = [
    "GraphitiConsoleResult",
    "add_episode",
    "draft_episode",
    "draft_graphiti_subgraph_export",
    "export_graphiti_subgraph",
    "graphiti_status",
    "lookup_graphiti_uuids",
    "search_graphiti",
    "search_graphiti_subgraph",
]
