"""Switch BehaviorMode — Gemini can request a mode change."""

from __future__ import annotations

import logging

from livekit.agents import RunContext, function_tool

from parrot.shared.parrot_actions import BehaviorMode

logger = logging.getLogger(__name__)

_MODES = {
    "companion": BehaviorMode.BASE | BehaviorMode.COMPANION,
    "butler": BehaviorMode.BASE | BehaviorMode.COMPANION | BehaviorMode.BUTLER,
    "researcher": BehaviorMode.BASE | BehaviorMode.COMPANION | BehaviorMode.RESEARCHER,
    "playful": BehaviorMode.BASE | BehaviorMode.COMPANION | BehaviorMode.PLAYFUL,
    "on_hand": BehaviorMode.BASE | BehaviorMode.COMPANION | BehaviorMode.ON_HAND,
    "full": (
        BehaviorMode.BASE | BehaviorMode.COMPANION | BehaviorMode.BUTLER
        | BehaviorMode.RESEARCHER | BehaviorMode.PLAYFUL
    ),
}


@function_tool()
async def set_mode(
    context: RunContext,
    mode: str,
) -> str:
    """Switch the parrot's behavior mode.

    Use this when the user asks you to change how you behave, or when
    the situation calls for it (e.g., user is working → butler mode).

    Args:
        mode: Target mode. Options:
            'companion' — default, friendly and playful.
            'butler' — proactive assistant (track time, todos, environment).
            'researcher' — proactively research and provide detailed info.
            'playful' — extra fun and silly.
            'on_hand' — perched on the user's hand; keep talking while the
                phone is just a camera view into AR.
            'full' — all modes active.
    """
    from parrot.brain.mode_watcher import set_behavior_mode

    target = _MODES.get(mode.lower())
    if target is None:
        return f"Unknown mode '{mode}'. Options: {', '.join(_MODES.keys())}."

    try:
        await set_behavior_mode(target)
        logger.info("set_mode: switched to '%s'", mode)
        return f"Mode switched to {mode}!"
    except Exception:
        logger.exception("set_mode: failed")
        return "I couldn't switch modes right now."
