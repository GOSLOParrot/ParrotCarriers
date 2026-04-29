"""B4: fly_to — command the parrot to fly to a position in AR space.

Brain → LiveKit RPC → Unity Animator.
"""

from __future__ import annotations

from livekit.agents import RunContext, function_tool

from parrot.brain.tools._rpc_bridge import call_unity_rpc
from parrot.shared.ecp import EcpCommandKind, wrap_legacy_rpc_payload


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
    # Phase 2 TODO (Sprint4 ECP-minimal, 2026-04-29):
    # `_command` is intentionally discarded here. The Sprint4 protocol design
    # (`sprint4_protocol_v2_ecp.md` §6) eventually wants every wrap to emit an
    # `ecp.command.issued` L0 EventEnvelope so the audit trail spans
    # turn → command → ack → snapshot → sighting. The cleanest place for that
    # write is inside `_rpc_bridge.call_unity_rpc` (single chokepoint), not
    # individual tools — we'll fold it in alongside the EcpAck full-shape
    # upgrade. Until then, command_id is preserved on the wire via `_ecp` so
    # cross-side correlation still works.
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
    )
    result = await call_unity_rpc(
        method="flyTo",
        payload=payload,
    )
    return result
