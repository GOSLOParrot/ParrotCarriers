"""B4: fly_to — command the parrot to fly to a position in AR space.

Brain → LiveKit RPC → Unity Animator.

NEED-P3-CAPABILITY-GATING (cross_chat_pending_registry_20260507 §4.F):
    The verb ``fly_to`` semantically assumes the model can fly. Non-flying
    models (humanoid, Q-chibi etc.) registered via ModelManifest will still
    have this tool exposed to the LLM, leading to visually nonsensical
    "fly" commands.

    Fix (Chat 4 increment OR P3): Brain agent reads active model's
    ``ModelManifest.declared_capability_ids`` at startup and dynamically
    registers tools — fly_to only registered when active model declares
    "fly" capability. Requires a ``ModelManifestRegistry`` Brain-side
    mirror (GOSLO Step 3 added ``model_id`` parameter but did not add the
    registry — see ``goslo_modularization_residual_debt_20260506.md §2.2 #3``).
"""

from __future__ import annotations

from livekit.agents import RunContext, function_tool

from parrot.brain.tools._rpc_bridge import call_unity_rpc
from parrot.brain.tools._state_context import attach_state_header
from parrot.shared.ecp import EcpCommandKind, wrap_legacy_rpc_payload


@function_tool()
async def fly_to(
    context: RunContext,
    x: float,
    y: float,
    z: float,
    model_id: str = "",
) -> str:
    """Command the parrot to fly to a specific position in AR space.

    Args:
        x: Target X coordinate in world space.
        y: Target Y coordinate in world space.
        z: Target Z coordinate in world space.
        model_id: Optional. Reserved for multi-companion scenarios — names a
            specific model controller registered on Unity side. Leave empty
            (default) unless the user has explicitly addressed a specific
            named companion. Empty string routes to the currently active
            controller via the Unity-side ParrotRegistry.
    """
    # Phase 2 TODO (Sprint4 ECP-minimal, 2026-04-29):
    # `_command` is intentionally discarded here. The Sprint4 protocol design
    # (`sprint4_protocol_v2_ecp.md` §6) eventually wants every wrap to emit an
    # `ecp.command.issued` L0 EventEnvelope so the audit trail spans
    # turn → command → ack → snapshot → sighting. The cleanest place for that
    # write is inside `_rpc_bridge.call_unity_rpc` (single chokepoint), not
    # individual tools — we'll fold it in alongside the EcpAck full-shape
    # upgrade. Until then, command_id is preserved on the wire via `_ecp` so
    # cross-side correlation still works.
    #
    # GOSLO model modularization (Step 3, 2026-05-06): see `animate.py` for
    # the model_id meta routing rationale. Same wire slot, same default.
    meta_kwarg: dict[str, str] | None = {"model_id": model_id} if model_id else None
    payload, _command = wrap_legacy_rpc_payload(
        {"x": x, "y": y, "z": z},
        kind=EcpCommandKind.MOVE_TO,
        target={
            "body_channel": "body",
            "state": "flying",
            "position": {"x": x, "y": y, "z": z},
        },
        actor="brain.tools.fly_to",
        expires_in_s=5.0,
        expected_duration_ms=1500,
        meta=meta_kwarg,
    )
    result = await call_unity_rpc(
        method="flyTo",
        payload=payload,
    )
    # Sprint4 Phase 4 W3 selection-C (entry doc §8.1 L10): prepend current
    # GOSLO body / head / cognitive snapshot so Gemini's next turn does not
    # propose contradictory actions (e.g. "let's go for a walk" while body
    # is DANCING). No-op when state is at defaults.
    return attach_state_header(result)
