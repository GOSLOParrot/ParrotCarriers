"""T1 Graphiti query tool for the noble_etiquette partition."""

from __future__ import annotations

import asyncio
import inspect
import logging
from typing import Any, Awaitable, Callable

from livekit.agents import RunContext, function_tool

logger = logging.getLogger(__name__)

GraphitiSearcher = Callable[..., Awaitable[dict[str, Any]] | dict[str, Any]]


@function_tool()
async def query_etiquette_memory(
    context: RunContext,
    query: str,
    depth: int = 2,
    limit: int = 6,
) -> str:
    """Search the noble_etiquette Graphiti partition with natural language.

    Use this when the user asks about the imported "ladies etiquette" / noble
    etiquette test corpus, or when GOSLO needs etiquette context before drafting
    a Plan, giving advice, or deciding whether to pull a larger subgraph into
    L2-B.  This is an Intent/Thinking read tool: it searches Graphiti with a
    bounded multi-hop strategy and reports raw Graphiti UUID/provenance cues, but
    it does not write Episodes, materialize L2-B, edit Refs, or mutate files.

    Args:
        query: Natural language etiquette question or search phrase.
        depth: Multi-hop search depth, clamped to 1..3.
        limit: Number of primary hits, clamped to 1..10.
    """

    return await do_query_etiquette_memory(query=query, depth=depth, limit=limit)


async def do_query_etiquette_memory(
    *,
    query: str,
    depth: int = 2,
    limit: int = 6,
    searcher: GraphitiSearcher | None = None,
) -> str:
    selected_query = _compact(query, 500)
    if not selected_query:
        return (
            "query_etiquette_memory needs a natural-language query. No Graphiti "
            "search, L2-B mutation, Episode write, or Ref mutation occurred."
        )

    selected_depth = max(1, min(_safe_int(depth, 2), 3))
    selected_limit = max(1, min(_safe_int(limit, 6), 10))
    try:
        from parrot.memory.graphiti_client import PARTITIONS

        graphiti_search = searcher
        if graphiti_search is None:
            from parrot.brain.graphiti_console import search_graphiti_subgraph

            graphiti_search = search_graphiti_subgraph
        receipt = await _maybe_await(
            graphiti_search(
                query=selected_query,
                partition=PARTITIONS.NOBLE_ETIQUETTE,
                limit=selected_limit,
                strategy="iterative_hybrid",
                depth=selected_depth,
                expansion_limit=3,
                enrich=True,
            )
        )
        return _format_etiquette_receipt(
            receipt,
            query=selected_query,
            depth=selected_depth,
            limit=selected_limit,
        )
    except Exception as exc:
        logger.exception("query_etiquette_memory: Graphiti search failed")
        return (
            "noble_etiquette Graphiti search failed "
            f"({type(exc).__name__}: {_compact(str(exc), 180)}). "
            "No Graphiti write, L2-B mutation, Episode write, or Ref mutation occurred."
        )


def _format_etiquette_receipt(
    receipt: dict[str, Any],
    *,
    query: str,
    depth: int,
    limit: int,
) -> str:
    success = bool(receipt.get("success")) if isinstance(receipt, dict) else False
    message = _compact(str(receipt.get("message") or ""), 180) if isinstance(receipt, dict) else ""
    data = receipt.get("data") if isinstance(receipt, dict) else {}
    if not isinstance(data, dict):
        data = {}
    hits = data.get("hits") if isinstance(data.get("hits"), list) else []
    subgraph = data.get("subgraph") if isinstance(data.get("subgraph"), dict) else {}
    bundle = data.get("graphiti_bundle") if isinstance(data.get("graphiti_bundle"), dict) else {}
    search_plan = data.get("search_plan") if isinstance(data.get("search_plan"), list) else []

    node_count = len(subgraph.get("nodes", [])) if isinstance(subgraph, dict) else 0
    edge_count = len(subgraph.get("edges", [])) if isinstance(subgraph, dict) else 0
    raw_count = len(bundle.get("raw_envelopes", [])) if isinstance(bundle, dict) else 0

    if not success:
        return (
            "noble_etiquette Graphiti search did not succeed"
            f"{f': {message}' if message else ''}. Query: {query}. "
            "No Graphiti write, L2-B mutation, Episode write, or Ref mutation occurred."
        )
    if not hits:
        return (
            "noble_etiquette Graphiti search returned no hits. "
            f"Query: {query}; depth={depth}; limit={limit}; message={message or 'empty'}. "
            "No Graphiti write, L2-B mutation, Episode write, or Ref mutation occurred."
        )

    lines: list[str] = []
    for index, row in enumerate(hits[:limit], start=1):
        if not isinstance(row, dict):
            continue
        text = _compact(
            str(row.get("text") or row.get("fact") or row.get("summary") or row.get("label") or ""),
            360,
        )
        uuid = _compact(str(row.get("uuid") or row.get("graphiti_uuid") or ""), 36)
        source_uuid = _compact(str(row.get("source_node_uuid") or ""), 36)
        target_uuid = _compact(str(row.get("target_node_uuid") or ""), 36)
        relation = _compact(str(row.get("name") or row.get("relation_type") or ""), 80)
        suffix_parts = []
        if relation:
            suffix_parts.append(f"rel={relation}")
        if source_uuid or target_uuid:
            suffix_parts.append(f"{source_uuid[:8]}->{target_uuid[:8]}")
        if uuid:
            suffix_parts.append(f"uuid={uuid[:8]}")
        suffix = f" ({'; '.join(suffix_parts)})" if suffix_parts else ""
        lines.append(f"{index}. {text or 'Graphiti etiquette hit'}{suffix}")

    plan_terms = []
    for step in search_plan[:4]:
        if isinstance(step, dict):
            term = _compact(str(step.get("query") or step.get("term") or ""), 80)
            if term:
                plan_terms.append(term)
    plan_block = f"\nSearch plan: {' | '.join(plan_terms)}" if plan_terms else ""
    return (
        "noble_etiquette Graphiti result "
        f"(T1 Intent/Thinking, iterative_hybrid, depth={depth}, "
        f"{node_count} nodes/{edge_count} edges, raw_envelopes={raw_count}).\n"
        f"Query: {query}{plan_block}\n"
        + "\n".join(lines)
        + "\nThis read preserved Graphiti semantics for later Web/L2-B import-plan use. "
        "No Graphiti write, L2-B materialization, Episode write, or Ref mutation occurred."
    )


async def _maybe_await(value: Awaitable[dict[str, Any]] | dict[str, Any]) -> dict[str, Any]:
    if inspect.isawaitable(value):
        return await value
    return value


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _compact(value: str, limit: int) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


__all__ = ["query_etiquette_memory", "do_query_etiquette_memory"]
