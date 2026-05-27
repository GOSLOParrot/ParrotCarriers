"""Command the parrot to leave the user's hand and fly back into view."""

from __future__ import annotations

from livekit.agents import RunContext, function_tool

from parrot.brain.tools._capability_gate import supports_capability, unsupported_message
from parrot.brain.tools._rpc_bridge import UNITY_RPC_ECP_TTL_S, call_unity_rpc
from parrot.brain.tools._state_context import attach_state_header
from parrot.shared.ecp import EcpCommandKind, wrap_legacy_rpc_payload


@function_tool()
async def return_to_view(
    context: RunContext,
    model_id: str = "",
) -> str:
    """Ask Unity to fly the parrot back into the camera view.

    Use this when the parrot is on the user's hand or has followed the hand
    out of the phone's current camera frame, and the user asks it to come back
    into view.

    Args:
        model_id: Optional. Reserved for multi-companion scenarios. Leave empty
            unless the user explicitly addresses a specific model.
    """
    if not supports_capability("fly", model_id):
        return unsupported_message("fly", model_id)

    meta_kwarg: dict[str, str] | None = {"model_id": model_id} if model_id else None
    payload, _command = wrap_legacy_rpc_payload(
        {
            "timeout_seconds": 5.0,
        },
        kind=EcpCommandKind.RETURN_TO_VIEW,
        target={
            "body_channel": "body",
            "state": "idle",
            "anchor": "camera_view_center",
        },
        actor="brain.tools.return_to_view",
        expires_in_s=UNITY_RPC_ECP_TTL_S,
        expected_duration_ms=1800,
        meta=meta_kwarg,
    )
    result = await call_unity_rpc(
        method="returnToView",
        payload=payload,
        timeout=7.0,
    )
    return attach_state_header(result)
