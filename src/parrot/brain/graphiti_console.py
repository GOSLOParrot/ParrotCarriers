"""Developer-console adapter for Graphiti memory-core management.

The Web console needs to inspect and test Graphiti without turning page loads
into memory writes. This adapter keeps reads, drafts, and explicit episode
writes separate. It degrades cleanly when the optional ``memory`` extra or the
graph database is not available.
"""

from __future__ import annotations

import datetime as _dt
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
) -> GraphitiConsoleResult:
    """Search Graphiti with a scoped partition and graceful failure."""
    installed = _graphiti_core_installed()
    selected_limit = _safe_limit(limit, default=5, maximum=20)
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
            payload={"query": query, "partition": partition, "limit": selected_limit},
        )
        if remote.get("success"):
            remote_data = dict(remote.get("data") or {})
            remote_data.setdefault("query", query)
            remote_data.setdefault("partition", _normalize_partition(partition))
            remote_data.setdefault("limit", selected_limit)
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
                "partition": partition,
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
        results = await g.search(
            query=query.strip(),
            group_ids=[_normalize_partition(partition)],
        )
        rows = [_serialize_search_hit(hit) for hit in list(results)[:selected_limit]]
        return GraphitiConsoleResult(
            action="search_graphiti",
            success=True,
            available=True,
            message=f"{len(rows)} result(s)",
            data={"query": query, "partition": partition, "limit": selected_limit, "results": rows},
        )
    except Exception as exc:
        return GraphitiConsoleResult(
            action="search_graphiti",
            success=False,
            available=_graphiti_core_installed(),
            message=f"{type(exc).__name__}: {exc}",
            data={"query": query, "partition": partition},
        )


async def search_graphiti_subgraph(
    *,
    query: str,
    partition: str = PARTITIONS.GOSLO,
    limit: Any = 8,
) -> dict[str, Any]:
    """Return a bounded Graphiti search slice shaped for graph renderers."""
    selected_partition = _normalize_partition(partition)
    selected_limit = _safe_limit(limit, default=8, maximum=20)
    search = await search_graphiti(
        query=query,
        partition=selected_partition,
        limit=selected_limit,
    )
    payload = search.as_json()
    if not search.success:
        payload["action"] = "graphiti.subgraph.search"
        payload.setdefault("data", {})["subgraph"] = _empty_subgraph(
            query=query,
            partition=selected_partition,
        )
        return payload

    hits = list(search.data.get("results") or [])
    subgraph = _hits_to_subgraph(hits, query=query, partition=selected_partition)
    return {
        "action": "graphiti.subgraph.search",
        "success": True,
        "available": search.available,
        "message": f"{len(hits)} hit(s), {len(subgraph['nodes'])} node(s)",
        "data": {
            "query": query.strip(),
            "partition": selected_partition,
            "limit": selected_limit,
            "hits": hits,
            "subgraph": subgraph,
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
    edge_drafts = _hits_to_edge_drafts(hits, partition=partition)
    warnings: list[str] = []
    if not observations:
        warnings.append("no Graphiti hits selected for export")
    if edge_drafts:
        warnings.append("edge_drafts are preview-only until exported nodes resolve to L2-B UUIDs")
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
    return {
        "text": str(text)[:800],
        "score": getattr(hit, "score", None),
        "uuid": getattr(hit, "uuid", ""),
        "source_node_uuid": getattr(hit, "source_node_uuid", ""),
        "target_node_uuid": getattr(hit, "target_node_uuid", ""),
        "source_url": getattr(hit, "source_url", ""),
        "source_description": getattr(hit, "source_description", ""),
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
            },
        )
        source_uuid = str(hit.get("source_node_uuid") or "").strip()
        target_uuid = str(hit.get("target_node_uuid") or "").strip()
        if source_uuid:
            nodes.setdefault(
                f"graphiti:{source_uuid}",
                {
                    "id": f"graphiti:{source_uuid}",
                    "label": source_uuid[:12],
                    "kind": "graphiti_source",
                    "partition": partition,
                    "graphiti_uuid": source_uuid,
                },
            )
        if target_uuid:
            nodes.setdefault(
                f"graphiti:{target_uuid}",
                {
                    "id": f"graphiti:{target_uuid}",
                    "label": target_uuid[:12],
                    "kind": "graphiti_target",
                    "partition": partition,
                    "graphiti_uuid": target_uuid,
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
                }
            )
    return {
        "query": query.strip(),
        "partition": partition,
        "nodes": list(nodes.values()),
        "edges": edges,
    }


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
                },
                "write_policy": "requires_resolved_l2b_node_uuid",
            }
        )
    return edge_drafts


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
        return value.value
    return value


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
