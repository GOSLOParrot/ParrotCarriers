"""Command the parrot to fly to the user's index finger perch anchor."""

from __future__ import annotations

from livekit.agents import RunContext, function_tool

from parrot.brain.tools._capability_gate import supports_capability, unsupported_message
from parrot.brain.tools._rpc_bridge import UNITY_RPC_ECP_TTL_S, call_unity_rpc
from parrot.brain.tools._state_context import attach_state_header
from parrot.shared.ecp import EcpCommandKind, wrap_legacy_rpc_payload


@function_tool()
async def perch_to_finger(
    context: RunContext,
    model_id: str = "",
    require_branch_gesture: bool = False,
) -> str:
    """Ask Unity to fly the parrot to the user's index finger middle segment.

    Args:
        model_id: Optional. Reserved for multi-companion scenarios. Leave empty
            unless the user explicitly addresses a specific model.
        require_branch_gesture: If true, Unity only accepts the command while
            the user is making the horizontal one-index-finger perch gesture.
            Leave false for a direct GOSLO instruction such as "fly to my hand".
    """
    if not supports_capability("fly", model_id):
        return unsupported_message("fly", model_id)
    if not supports_capability("perch", model_id):
        return unsupported_message("perch", model_id)

    meta_kwarg: dict[str, str] | None = {"model_id": model_id} if model_id else None
    payload, _command = wrap_legacy_rpc_payload(
        {
            "require_branch_gesture": require_branch_gesture,
            "timeout_seconds": 6.0,
        },
        kind=EcpCommandKind.PERCH_TO_FINGER,
        target={
            "body_channel": "body",
            "state": "perched_on_hand",
            "anchor": "index_finger_middle_segment",
        },
        actor="brain.tools.perch_to_finger",
        expires_in_s=UNITY_RPC_ECP_TTL_S,
        expected_duration_ms=2500,
        meta=meta_kwarg,
    )
    result = await call_unity_rpc(
        method="perchToFinger",
        payload=payload,
        timeout=8.0,
    )
    return attach_state_header(result)
