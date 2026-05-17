"""B8: query_memory — retrieve relevant memories from Graphiti.

Brain → Graphiti search → context for Gemini.
"""

from __future__ import annotations

import logging

from livekit.agents import RunContext, function_tool

logger = logging.getLogger(__name__)


@function_tool()
async def query_memory(
    context: RunContext,
    query: str,
    partition: str = "goslo",
    depth: int = 2,
) -> str:
    """Search long-term memory with Graphiti natural-language subgraph retrieval.

    Use this when:
    - The user asks "do you remember...?" or references past conversations.
    - You need context about the user's preferences or habits.
    - You want to recall facts about objects, people, or places.

    Args:
        query: Natural language query describing what you're looking for.
        partition: Memory partition to search. Options:
            'goslo' — GOSLO's own memories (conversations, observations).
            'maid' — Maid's memories (research, tasks).
            'scene' — Scene/object information.
            'user' — User profile and preferences.
    """
    try:
        from parrot.brain.graphiti_console import search_graphiti_subgraph
        from parrot.memory.graphiti_client import PARTITIONS

        valid_partitions = {
            "goslo": PARTITIONS.GOSLO,
            "maid": PARTITIONS.MAID,
            "scene": PARTITIONS.SCENE,
            "user": PARTITIONS.USER,
            "arknights_test": PARTITIONS.ARKNIGHTS_TEST,
        }
        group_id = valid_partitions.get(partition, PARTITIONS.GOSLO)
        receipt = await search_graphiti_subgraph(
            query=query,
            partition=group_id,
            limit=6,
            strategy="iterative_hybrid",
            depth=max(1, min(int(depth or 2), 3)),
            expansion_limit=3,
        )
        data = receipt.get("data") if isinstance(receipt, dict) else {}
        if not isinstance(data, dict):
            data = {}
        results = data.get("hits")
        if not isinstance(results, list):
            results = []

        if not results:
            logger.info("query_memory: no results for '%s' in %s", query, partition)
            return "I don't have any memories about that yet."

        subgraph = data.get("subgraph") if isinstance(data.get("subgraph"), dict) else {}
        node_count = len(subgraph.get("nodes", [])) if isinstance(subgraph, dict) else 0
        edge_count = len(subgraph.get("edges", [])) if isinstance(subgraph, dict) else 0
        strategy = str(data.get("strategy") or "iterative_hybrid")
        lines: list[str] = []
        for index, row in enumerate(results[:6]):
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

        summary = "\n".join(lines)
        logger.info(
            "query_memory: %d results for '%s' in %s", len(results), query, partition
        )
        return (
            f"Graphiti memory results ({strategy}, {node_count} nodes/{edge_count} edges):\n"
            f"{summary}"
        )
    except Exception:
        logger.exception("query_memory: search failed")
        return "My memory is having trouble right now. Try again later."
