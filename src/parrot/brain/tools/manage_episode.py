"""P2.5+: manage_episode — Gemini-driven episode segmentation for L2-B.

Episodes are conversational/situational segments in GOSLO's working memory.
Gemini decides when to start/end episodes based on topic changes, user
activity shifts, or significant events.

This is the "conscious" episode management — Gemini decides.
Triggers can also create episodes automatically (the "subconscious" path).
"""

from __future__ import annotations

import logging

from livekit.agents import RunContext, function_tool

logger = logging.getLogger(__name__)


@function_tool()
async def manage_episode(
    context: RunContext,
    action: str,
    title: str = "",
    summary: str = "",
) -> str:
    """Manage conversational episodes in your working memory.

    Use this to segment your experience into meaningful chunks:
    - Start a new episode when the topic/activity changes significantly
    - End an episode when a conversation topic concludes
    - The system archives completed episodes to long-term memory

    Args:
        action: 'start' to begin a new episode, 'end' to close current one, 'status' to check.
        title: Short title for the episode (when starting). E.g., "帮主人找蓝色包裹".
        summary: Brief summary of what happened (when ending). E.g., "找到了包裹在桌子底下".
    """
    try:
        from parrot.dsg.l2b_graph import get_l2b_graph

        graph = get_l2b_graph()

        if action == "start":
            ep = graph.start_episode(title=title, trigger_source="gemini_tool")
            return (
                f"Started new episode: '{title or ep.episode_id}'. "
                f"I'll track what happens in this episode. "
                f"Currently tracking {graph.node_count()} objects in the scene."
            )

        elif action == "end":
            ep = graph.close_current_episode(summary=summary)
            if ep:
                await graph.archive_episode_to_graphiti(ep.episode_id)
                node_count = len(ep.participating_node_uuids)
                return (
                    f"Closed episode '{ep.title or ep.episode_id}' "
                    f"({node_count} objects involved). "
                    f"Archived to long-term memory."
                )
            return "No active episode to close."

        elif action == "status":
            ep = graph.get_current_episode()
            if ep:
                duration = __import__("time").time() - ep.started_at
                return (
                    f"Current episode: '{ep.title or ep.episode_id}' "
                    f"(running {duration:.0f}s, "
                    f"trigger: {ep.trigger_source})"
                )
            return "No active episode right now."

        else:
            return f"Unknown action '{action}'. Use 'start', 'end', or 'status'."

    except Exception:
        logger.exception("manage_episode failed")
        return "Episode management is not available right now."
