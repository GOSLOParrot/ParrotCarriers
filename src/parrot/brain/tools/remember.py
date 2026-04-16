"""B8: remember — store information in long-term memory via Graphiti.

Brain → Graphiti add_episode → FalkorDB graph.
"""

from __future__ import annotations

import logging

from livekit.agents import RunContext, function_tool

logger = logging.getLogger(__name__)


@function_tool()
async def remember(
    context: RunContext,
    information: str,
    importance: str = "normal",
) -> str:
    """Save a piece of information to long-term memory.

    Use this when the user explicitly asks you to remember something,
    or when you observe an important fact worth preserving (preferences,
    names, habits, locations of objects, etc.).

    Args:
        information: The fact or observation to remember.
        importance: How important this is — 'low', 'normal', or 'high'.
    """
    try:
        from graphiti_core.graphiti_types import EpisodeType

        from parrot.memory.graphiti_client import PARTITIONS, get_graphiti

        g = await get_graphiti()
        await g.add_episode(
            text=information,
            episode_type=EpisodeType.text,
            group_id=PARTITIONS.GOSLO,
            source="brain_remember",
        )
        logger.info("remember: stored '%s' (importance=%s)", information[:80], importance)
        return f"Got it! I'll remember that."
    except Exception:
        logger.exception("remember: failed to store")
        return "I tried to remember that but my memory is having trouble right now."
