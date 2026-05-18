"""GOSLO Graphiti natural-language memory lookup for the laptop test lane."""

from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable

from livekit.agents import RunContext, function_tool

logger = logging.getLogger(__name__)

LAPTOP_PROFILE_TEST_PARTITION = "laptop_profile_test"

SearchGraphitiSubgraph = Callable[..., Awaitable[dict[str, Any]]]


@function_tool()
async def query_memory(
    context: RunContext,
    query: str,
    depth: int = 2,
) -> str:
    """Search the laptop-profile Graphiti test partition with natural language.

    Use this only when GOSLO explicitly needs to check the current laptop test
    knowledge base. This is a T1/Intent tool and may block the live
    conversation while Graphiti searches, so do not call it casually or every
    turn.

    Args:
        query: Natural-language question or search phrase.
        depth: Graph traversal depth, clamped to 1-3.
    """
    return await do_query_memory(query=query, depth=depth)


async def do_query_memory(
    *,
    query: str,
    depth: int = 2,
    searcher: SearchGraphitiSubgraph | None = None,
) -> str:
    """Core implementation for tests and tool calls.

    The current laptop smoke-test scope is intentionally fixed to
    ``laptop_profile_test``. Keep routing simple until the real GOSLO memory
    partition policy is decided.
    """
    try:
        from parrot.memory.graphiti_client import PARTITIONS

        if searcher is None:
            from parrot.brain.graphiti_console import search_graphiti_subgraph

            searcher = search_graphiti_subgraph

        clean_query = " ".join(str(query or "").split())
        if not clean_query:
            return "Graphiti query is empty."

        receipt = await searcher(
            query=clean_query,
            partition=PARTITIONS.LAPTOP_PROFILE_TEST,
            limit=8,
            strategy="iterative_hybrid",
            depth=max(1, min(int(depth or 2), 3)),
            expansion_limit=4,
        )
        data = receipt.get("data") if isinstance(receipt, dict) else {}
        if not isinstance(data, dict):
            data = {}
        results = data.get("hits")
        if not isinstance(results, list):
            results = []

        if not results:
            logger.info(
                "query_memory: no results for '%s' in %s",
                clean_query,
                LAPTOP_PROFILE_TEST_PARTITION,
            )
            return (
                "No Graphiti memory hits in laptop_profile_test for that query. "
                "Try a more direct natural-language query."
            )

        subgraph = data.get("subgraph") if isinstance(data.get("subgraph"), dict) else {}
        node_count = len(subgraph.get("nodes", [])) if isinstance(subgraph, dict) else 0
        edge_count = len(subgraph.get("edges", [])) if isinstance(subgraph, dict) else 0
        strategy = str(data.get("strategy") or "iterative_hybrid")
        lines: list[str] = []
        for index, row in enumerate(results[:8]):
            if not isinstance(row, dict):
                continue
            fact = str(row.get("text") or row.get("summary") or row.get("label") or "").strip()
            source_uuid = str(row.get("source_node_uuid") or "").strip()
            target_uuid = str(row.get("target_node_uuid") or "").strip()
            uuid = str(row.get("uuid") or row.get("graphiti_uuid") or "").strip()
            suffix = ""
            if source_uuid or target_uuid:
                suffix = f" [{source_uuid[:8]} -> {target_uuid[:8]}]"
            if uuid:
                suffix += f" ({uuid[:8]})"
            lines.append(f"- {fact[:420] or f'Graphiti result {index + 1}'}{suffix}")

        logger.info(
            "query_memory: %d results for '%s' in %s",
            len(results),
            clean_query,
            LAPTOP_PROFILE_TEST_PARTITION,
        )
        return (
            "Graphiti memory results "
            f"({LAPTOP_PROFILE_TEST_PARTITION}, {strategy}, "
            f"{node_count} nodes/{edge_count} edges):\n"
            f"{chr(10).join(lines)}"
        )
    except Exception:
        logger.exception("query_memory: search failed")
        return "My memory is having trouble right now. Try again later."


__all__ = [
    "LAPTOP_PROFILE_TEST_PARTITION",
    "query_memory",
    "do_query_memory",
]
