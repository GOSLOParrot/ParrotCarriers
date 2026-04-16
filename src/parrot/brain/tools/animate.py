"""B5: animate — play an animation on the parrot.

Brain → LiveKit RPC → Unity Animator HSM.
"""

from __future__ import annotations

from livekit.agents import RunContext, function_tool

from parrot.brain.tools._rpc_bridge import call_unity_rpc
from parrot.shared.parrot_actions import ParrotAnimation

VALID_ANIMATIONS = {a.value for a in ParrotAnimation}


@function_tool()
async def animate(
    context: RunContext,
    animation_name: str,
) -> str:
    """Play an animation on the parrot.

    Args:
        animation_name: Name of the animation to play.
            Supported: idle, fly, dance, wing_flap, perch, sit, head_bob, sleep.
    """
    if animation_name not in VALID_ANIMATIONS:
        return (
            f"Unknown animation '{animation_name}'. "
            f"Available: {', '.join(sorted(VALID_ANIMATIONS))}."
        )
    result = await call_unity_rpc(
        method="animate",
        payload={"animation": animation_name},
    )
    return result
