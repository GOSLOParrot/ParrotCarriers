"""B5: animate — play an animation on the parrot.

Brain → LiveKit RPC → Unity Animator HSM.
"""

from __future__ import annotations

from livekit.agents import RunContext, function_tool

from parrot.brain.tools._rpc_bridge import call_unity_rpc
from parrot.shared.ecp import EcpCommandKind, wrap_legacy_rpc_payload
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
    # Phase 2 TODO: see fly_to.py — `_command` is currently discarded; the
    # `ecp.command.issued` L0 event will be emitted inside `call_unity_rpc`
    # once the bridge becomes the single chokepoint for ECP audit logging.
    payload, _command = wrap_legacy_rpc_payload(
        {"animation": animation_name},
        kind=EcpCommandKind.ANIMATE,
        target={
            "body_channel": "body",
            "animation": animation_name,
        },
        actor="brain.tools.animate",
        expires_in_s=5.0,
        expected_duration_ms=1000,
    )
    result = await call_unity_rpc(
        method="animate",
        payload=payload,
    )
    return result
