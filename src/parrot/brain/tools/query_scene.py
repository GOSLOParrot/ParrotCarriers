"""B9: query_scene — ask about objects in the current scene via DSG interface."""

from __future__ import annotations

import logging

from livekit.agents import RunContext, function_tool

logger = logging.getLogger(__name__)


@function_tool()
async def query_scene(
    context: RunContext,
    query: str,
) -> str:
    """Search for information about objects and the scene around the user.

    Use this when the user asks about their surroundings, objects on their desk,
    or anything related to the physical space.

    Args:
        query: What to look for in the scene (e.g., "what's on the desk", "where is my cup").
    """
    try:
        from parrot.memory.graphiti_client import PARTITIONS, get_graphiti

        g = await get_graphiti()
        results = await g.search(
            query=query,
            group_ids=[PARTITIONS.SCENE],
            num_results=5,
        )

        if not results:
            return "I don't have any scene information right now. My eyes aren't fully set up yet!"

        lines = []
        for r in results:
            fact = getattr(r, "fact", None) or getattr(r, "text", str(r))
            lines.append(f"- {fact}")

        return f"Here's what I know about the scene:\n" + "\n".join(lines)
    except Exception:
        logger.exception("query_scene: failed")
        return "I can't check the scene right now."
