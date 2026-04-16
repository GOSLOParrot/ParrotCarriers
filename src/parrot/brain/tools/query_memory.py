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
) -> str:
    """Search long-term memory for relevant information.

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
        from parrot.memory.graphiti_client import PARTITIONS, get_graphiti

        valid_partitions = {
            "goslo": PARTITIONS.GOSLO,
            "maid": PARTITIONS.MAID,
            "scene": PARTITIONS.SCENE,
            "user": PARTITIONS.USER,
        }
        group_id = valid_partitions.get(partition, PARTITIONS.GOSLO)

        g = await get_graphiti()
        results = await g.search(
            query=query,
            group_ids=[group_id],
            num_results=5,
        )

        if not results:
            logger.info("query_memory: no results for '%s' in %s", query, partition)
            return "I don't have any memories about that yet."

        lines = []
        for r in results:
            fact = getattr(r, "fact", None) or getattr(r, "text", str(r))
            lines.append(f"- {fact}")

        summary = "\n".join(lines)
        logger.info(
            "query_memory: %d results for '%s' in %s", len(results), query, partition
        )
        return f"Here's what I remember:\n{summary}"
    except Exception:
        logger.exception("query_memory: search failed")
        return "My memory is having trouble right now. Try again later."
