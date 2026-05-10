"""Play a model-declared capability by capability_id.

This is the custom-model companion to ``animate``. ``animate`` remains locked
to the eight reserved parrot animation names; ``play_capability`` validates
against the selected model manifest and then routes the capability id through
the existing Unity animate RPC path.
"""

from __future__ import annotations

from livekit.agents import RunContext, function_tool

from parrot.brain.tools._capability_gate import (
    resolve_model_id,
    supports_capability,
    unsupported_message,
)
from parrot.brain.tools._rpc_bridge import call_unity_rpc
from parrot.brain.tools._state_context import attach_state_header
from parrot.shared.ecp import EcpCommandKind, wrap_legacy_rpc_payload


@function_tool()
async def play_capability(
    context: RunContext,
    capability_id: str,
    model_id: str = "",
    parameters_json: str = "",
) -> str:
    """Play a capability declared by the selected model manifest.

    Args:
        capability_id: Manifest capability id, such as face_happy, touch_idle,
            pat_idle, tickle_idle, eat, spine_idle, or spine_walk for Ner.
        model_id: Optional model id. Leave empty to target the active model.
        parameters_json: Optional JSON string for parameterized capabilities.
            Unity forwards it to the selected model controller and returns a
            capability_unsupported ack when strict capability routing fails.
    """
    selected_model_id = resolve_model_id(model_id)
    safe_capability_id = str(capability_id or "").strip()
    if not safe_capability_id:
        return "Missing capability_id."
    if not supports_capability(safe_capability_id, selected_model_id):
        return unsupported_message(safe_capability_id, selected_model_id)

    meta_kwarg: dict[str, str] = {"model_id": selected_model_id}
    payload, _command = wrap_legacy_rpc_payload(
        {
            "animation": safe_capability_id,
            "parameters_json": parameters_json or "",
            "strict_capability": True,
        },
        kind=EcpCommandKind.ANIMATE,
        target={
            "body_channel": "body",
            "capability_id": safe_capability_id,
            "parameters_json": parameters_json or "",
        },
        actor="brain.tools.play_capability",
        expires_in_s=5.0,
        expected_duration_ms=1000,
        meta=meta_kwarg,
    )
    result = await call_unity_rpc(method="animate", payload=payload)
    return attach_state_header(result)


__all__ = ["play_capability"]
