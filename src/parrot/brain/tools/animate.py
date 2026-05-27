"""B5: animate — play an animation on the parrot.

Brain → LiveKit RPC → Unity Animator HSM.
"""

from __future__ import annotations

from typing import Literal

from livekit.agents import RunContext, function_tool

from parrot.brain.tools._capability_gate import supports_capability, unsupported_message
from parrot.brain.tools._rpc_bridge import UNITY_RPC_ECP_TTL_S, call_unity_rpc
from parrot.brain.tools._state_context import attach_state_header
from parrot.shared.ecp import EcpCommandKind, wrap_legacy_rpc_payload
from parrot.shared.parrot_actions import ParrotAnimation

VALID_ANIMATIONS = {a.value for a in ParrotAnimation}
ParrotAnimationName = Literal[
    "idle",
    "fly",
    "dance",
    "wing_flap",
    "perch",
    "sit",
    "head_bob",
    "sleep",
]


@function_tool()
async def animate(
    context: RunContext,
    animation_name: ParrotAnimationName,
    model_id: str = "",
) -> str:
    """Play an animation on the parrot.

    Args:
        animation_name: Name of the animation to play.
            Supported: idle, fly, dance, wing_flap, perch, sit, head_bob, sleep.
        model_id: Optional. Reserved for multi-companion scenarios — names a
            specific model controller registered on Unity side. Leave empty
            (default) unless the user has explicitly addressed a specific
            named companion. Empty string routes to the currently active
            controller via the Unity-side ParrotRegistry.
    """
    animation_name = str(animation_name)
    if animation_name not in VALID_ANIMATIONS:
        return (
            f"Unknown animation '{animation_name}'. "
            f"Available: {', '.join(sorted(VALID_ANIMATIONS))}."
        )
    # Phase 2 TODO: see fly_to.py — `_command` is currently discarded; the
    # `ecp.command.issued` L0 event will be emitted inside `call_unity_rpc`
    # once the bridge becomes the single chokepoint for ECP audit logging.
    #
    # GOSLO model modularization (Step 3, 2026-05-06): a non-empty model_id
    # rides on `EcpCommand.meta["model_id"]` (existing Phase 4 §8 wire slot,
    # 0 schema bump). Empty model_id stays out of meta so unrelated tooling
    # observing the wire sees the same shape it always did.
    if not supports_capability(animation_name, model_id):
        return unsupported_message(animation_name, model_id)

    meta_kwarg: dict[str, str] | None = {"model_id": model_id} if model_id else None
    payload, _command = wrap_legacy_rpc_payload(
        {"animation": animation_name},
        kind=EcpCommandKind.ANIMATE,
        target={
            "body_channel": "body",
            "animation": animation_name,
        },
        actor="brain.tools.animate",
        expires_in_s=UNITY_RPC_ECP_TTL_S,
        expected_duration_ms=1000,
        meta=meta_kwarg,
    )
    result = await call_unity_rpc(
        method="animate",
        payload=payload,
    )
    # Sprint4 Phase 4 W3 selection-C (entry doc §8.1 L10): see fly_to.py.
    return attach_state_header(result)


async def _play_registered_animation(animation_name: ParrotAnimationName) -> str:
    """Execute one registered Parrot animation without exposing action fields.

    These fixed tools are the GOSLO_default "skill selection" surface: GOSLO
    chooses a tool such as play_dance, and backend code owns the canonical
    animation id plus Unity RPC payload.
    """
    animation_name = str(animation_name)
    if animation_name not in VALID_ANIMATIONS:
        return (
            f"Unknown animation '{animation_name}'. "
            f"Available: {', '.join(sorted(VALID_ANIMATIONS))}."
        )
    if not supports_capability(animation_name):
        return unsupported_message(animation_name)

    payload, _command = wrap_legacy_rpc_payload(
        {"animation": animation_name},
        kind=EcpCommandKind.ANIMATE,
        target={
            "body_channel": "body",
            "animation": animation_name,
        },
        actor=f"brain.tools.{animation_name}",
        expires_in_s=UNITY_RPC_ECP_TTL_S,
        expected_duration_ms=1000,
    )
    result = await call_unity_rpc(
        method="animate",
        payload=payload,
    )
    return attach_state_header(result)


@function_tool()
async def play_idle(context: RunContext) -> str:
    """Return the parrot to its registered idle animation."""
    return await _play_registered_animation("idle")


@function_tool()
async def play_fly_pose(context: RunContext) -> str:
    """Play the registered flying pose without choosing a destination."""
    return await _play_registered_animation("fly")


@function_tool()
async def play_dance(context: RunContext) -> str:
    """Play the registered dance animation."""
    return await _play_registered_animation("dance")


@function_tool()
async def play_wing_flap(context: RunContext) -> str:
    """Play the registered wing-flap animation."""
    return await _play_registered_animation("wing_flap")


@function_tool()
async def play_perch_pose(context: RunContext) -> str:
    """Play the registered perch pose without flying to a hand."""
    return await _play_registered_animation("perch")


@function_tool()
async def play_sit(context: RunContext) -> str:
    """Play the registered sitting pose."""
    return await _play_registered_animation("sit")


@function_tool()
async def play_head_bob(context: RunContext) -> str:
    """Play the registered head-bob animation."""
    return await _play_registered_animation("head_bob")


@function_tool()
async def play_sleep(context: RunContext) -> str:
    """Play the registered sleep animation."""
    return await _play_registered_animation("sleep")


PARROT_ANIMATION_TOOLS = (
    play_idle,
    play_fly_pose,
    play_dance,
    play_wing_flap,
    play_perch_pose,
    play_sit,
    play_head_bob,
    play_sleep,
)
