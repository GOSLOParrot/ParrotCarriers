"""B5: animate — play an animation on the parrot.

Brain → LiveKit RPC → Unity Animator HSM.
"""

from __future__ import annotations

from livekit.agents import RunContext, function_tool

from parrot.brain.tools._rpc_bridge import call_unity_rpc

KNOWN_ANIMATIONS = {"dance", "head_bob", "wing_flap", "idle", "sleep", "perch"}


@function_tool()
async def animate(
    context: RunContext,
    animation_name: str,
) -> str:
    """Play an animation on the parrot.

    Args:
        animation_name: Name of the animation to play.
            Supported: dance, head_bob, wing_flap, idle, sleep, perch.
    """
    result = await call_unity_rpc(
        method="animate",
        payload={"animation": animation_name},
    )
    return result
