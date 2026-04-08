"""B4: fly_to — command the parrot to fly to a position in AR space.

Brain → LiveKit RPC → Unity Animator.
"""

from __future__ import annotations

from livekit.agents import RunContext, function_tool

from parrot.brain.tools._rpc_bridge import call_unity_rpc


@function_tool()
async def fly_to(
    context: RunContext,
    x: float,
    y: float,
    z: float,
) -> str:
    """Command the parrot to fly to a specific position in AR space.

    Args:
        x: Target X coordinate in world space.
        y: Target Y coordinate in world space.
        z: Target Z coordinate in world space.
    """
    result = await call_unity_rpc(
        method="flyTo",
        payload={"x": x, "y": y, "z": z},
    )
    return result
