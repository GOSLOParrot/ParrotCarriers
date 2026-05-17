"""Developer-console adapter for Graphiti memory-core management.

The Web console needs to inspect and test Graphiti without turning page loads
into memory writes. This adapter keeps reads, drafts, and explicit episode
writes separate. It degrades cleanly when the optional ``memory`` extra or the
graph database is not available.
"""

from __future__ import annotations

import datetime as _dt
import inspect
import json
import os
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
) -> GraphitiConsoleResult:
    """Search Graphiti with a scoped partition and graceful failure."""
    installed = _graphiti_core_installed()
    selected_limit = _safe_limit(limit, default=5, maximum=20)
    selected_partition = _normalize_partition(partition)
    selected_focal = str(focal_node_uuid or "").strip()
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
            },
        )
        if remote.get("success"):
            remote_data = dict(remote.get("data") or {})
            remote_data.setdefault("query", query)
            remote_data.setdefault("partition", selected_partition)
            remote_data.setdefault("limit", selected_limit)
            if selected_focal:
                remote_data.setdefault("focal_node_uuid", selected_focal)
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
        results = await _call_graphiti_search(
            g,
            query=query.strip(),
            partition=selected_partition,
            limit=selected_limit,
            focal_node_uuid=selected_focal,
        )
        rows = [_serialize_search_hit(hit) for hit in list(results)[:selected_limit]]
        data: dict[str, Any] = {
            "query": query,
            "partition": selected_partition,
            "limit": selected_limit,
            "results": rows,
        }
        if selected_focal:
            data["focal_node_uuid"] = selected_focal
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
    collected = await _collect_graphiti_subgraph_hits(
        query=query,
        partition=selected_partition,
        limit=selected_limit,
        strategy=selected_strategy,
        depth=selected_depth,
        expansion_limit=selected_expansion_limit,
        focal_node_uuid=selected_focal,
    )
    if not collected["success"]:
        search = collected["base_search"]
        payload = search.as_json() if isinstance(search, GraphitiConsoleResult) else {}
        payload.setdefault("success", False)
        payload.setdefault("available", False)
        payload.setdefault("message", "Graphiti search failed")
        payload["action"] = "graphiti.subgraph.search"
        payload.setdefault("data", {}).update(
            {
                "query": query.strip(),
                "partition": selected_partition,
                "limit": selected_limit,
                "strategy": selected_strategy,
                "depth": selected_depth,
                "expansion_limit": selected_expansion_limit,
                "focal_node_uuid": selected_focal,
                "hits": [],
                "subgraph": _empty_subgraph(
                    query=query,
                    partition=selected_partition,
                ),
                "search_plan": collected["search_plan"],
                "warnings": collected["warnings"],
            }
        )
        return payload

    hits = list(collected["hits"])
    subgraph = _hits_to_subgraph(hits, query=query, partition=selected_partition)
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
            "hits": hits,
            "subgraph": subgraph,
            "search_plan": collected["search_plan"],
            "warnings": collected["warnings"],
        },
        "audit": {
            "web_only": True,
            "read_only": True,
            "direct_falkordb_write": False,
        },
    }


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
        return GraphitiConsoleResult(
            action="add_episode",
            success=False,
            available=False,
            message=_GRAPHITI_MISSING_MESSAGE,
            data={"draft": episode},
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
) -> Any:
    """Call Graphiti search across 0.28-compatible parameter spellings."""

    search = getattr(graphiti, "search")
    focal = str(focal_node_uuid or "").strip()
    kwargs: dict[str, Any] = {"query": query}
    try:
        parameters = inspect.signature(search).parameters
    except (TypeError, ValueError):
        parameters = {}

    if not parameters or "group_ids" in parameters:
        kwargs["group_ids"] = [partition]
    if not parameters or "num_results" in parameters:
        kwargs["num_results"] = limit
    elif "limit" in parameters:
        kwargs["limit"] = limit
    if focal:
        for name in ("focal_node_uuid", "center_node_uuid", "node_uuid"):
            if not parameters or name in parameters:
                kwargs[name] = focal
                break

    try:
        return await search(**kwargs)
    except TypeError:
        if focal:
            return await search(query, focal, group_ids=[partition], num_results=limit)
        return await search(query=query, group_ids=[partition], num_results=limit)


async def _collect_graphiti_subgraph_hits(
    *,
    query: str,
    partition: str,
    limit: int,
    strategy: str,
    depth: int,
    expansion_limit: int,
    focal_node_uuid: str,
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
    return value if value in {"hybrid", "iterative_hybrid", "node_distance"} else "hybrid"


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
    raw = os.getenv("PARROT_WEB_CONSOLE_GRAPHITI_TIMEOUT_S", "3.0")
    try:
        return max(0.5, min(float(raw), 15.0))
    except ValueError:
        return 3.0


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
        getattr(hit, "fact", None)
        or getattr(hit, "text", None)
        or getattr(hit, "summary", None)
        or str(hit)
    )
    raw = _graphiti_raw_payload(hit)
    return {
        "text": str(text)[:800],
        "score": getattr(hit, "score", None),
        "uuid": getattr(hit, "uuid", ""),
        "source_node_uuid": getattr(hit, "source_node_uuid", ""),
        "target_node_uuid": getattr(hit, "target_node_uuid", ""),
        "source_url": getattr(hit, "source_url", ""),
        "source_description": getattr(hit, "source_description", ""),
        "graphiti_raw": raw,
    }


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
        nodes.setdefault(
            node_id,
            {
                "id": node_id,
                "label": _label_from_text(text, fallback=f"Graphiti hit {index + 1}"),
                "kind": "graphiti_fact",
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


def _endpoint_label(hit: dict[str, Any], role: str, *, fallback: str) -> str:
    raw = _graphiti_raw_payload(hit)
    name = _endpoint_name_from_raw(raw, role)
    return name or fallback


def _endpoint_raw(hit: dict[str, Any], role: str) -> dict[str, Any]:
    raw = _graphiti_raw_payload(hit)
    node = raw.get(f"{role}_node")
    if isinstance(node, dict):
        return _jsonable(node)
    uuid = str(hit.get(f"{role}_node_uuid") or "").strip()
    return {"uuid": uuid, "role": role} if uuid else {"role": role}


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
    return {
        "schema_version": 1,
        "kind": str(hit.get("graphiti_kind") or hit.get("kind") or "graphiti_fact"),
        "partition": partition,
        "index": index,
        "uuid": graphiti_uuid,
        "graphiti_edge_uuid": graphiti_uuid,
        "source_node_uuid": source_node_uuid,
        "target_node_uuid": target_node_uuid,
        "episode_uuids": _episode_uuids_from_hit(hit),
        "source_url": str(hit.get("source_url") or ""),
        "source_description": str(hit.get("source_description") or ""),
        "score": hit.get("score"),
        "label": _label_from_text(text, fallback=f"Graphiti hit {index + 1}"),
        "text": text,
        "search_context": _jsonable(hit.get("search_context") or {}),
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


def _extract_export_hits(body: dict[str, Any]) -> list[dict[str, Any]]:
    raw = body.get("hits")
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
    "search_graphiti",
    "search_graphiti_subgraph",
]
