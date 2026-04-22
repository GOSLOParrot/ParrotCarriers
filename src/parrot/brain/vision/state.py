"""GOSLO's visual self-perception — Blackboard writer for VisualState family.

Sprint 1 T5 (this file, minimal wire):
    session/visual_reason     ← Unity RPC `onVideoDegraded(reason, ts)`

Sprint 1 T6 (follow-up, fusion):
    session/visual_state      ← derived from {visual_reason,
                                               tick/ar_tracking_state,
                                               tick/last_rpc_ack}

Both keys declare this module (`brain.vision.state`) as sole writer in
`shared/bb_schema.BB_KEYS`. Consumers (context_injector, soul, identify_object
upgrades) are READ-only on them.

## Inbound RPC contract (T5)

Unity publishes `onVideoDegraded` whenever the visual stream changes from
GOSLO's point of view at the **producer** end:

    RPC method : onVideoDegraded
    payload    : { "reason": "<VisualStateReason.value>", "ts": <unix_seconds> }
    response   : { "status": "ok" }      (always — this is fire-and-forget
                                          telemetry, never a rejectable request)

Minimum viable Unity reporter (Sprint 1): OnApplicationPause only. AR
tracking state changes already flow through the DataChannel
`ar_tracking_state` event path (telemetry_receiver → tick/ar_tracking_state),
so T5 does not add a second route for it. Brightness variance / blur
detection land in P3.

Unknown reason strings coerce to `VisualStateReason.UNKNOWN`; we never
drop the event because an unknown reason still means "something changed".
"""

from __future__ import annotations

import json
import logging
import time
from typing import TYPE_CHECKING

from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.vision_state import VisualStateReason

if TYPE_CHECKING:
    import py_trees
    from livekit.rtc import Room, RpcInvocationData

logger = logging.getLogger(__name__)

_WRITER = "brain.vision.state"
_RPC_METHOD = "onVideoDegraded"

_bb: "py_trees.blackboard.Client | None" = None


def _ensure_bb() -> "py_trees.blackboard.Client":
    global _bb
    if _bb is None:
        _bb = open_bb_client(name="vision_state", writer=_WRITER)
    return _bb


def _coerce_reason(raw: str) -> VisualStateReason:
    """String → VisualStateReason, falling back to UNKNOWN without dropping."""
    try:
        return VisualStateReason(raw)
    except ValueError:
        logger.warning("Unknown visual_reason %r, coerced to UNKNOWN", raw)
        return VisualStateReason.UNKNOWN


def handle_video_degraded(reason: str, ts: float | None = None) -> None:
    """Write `session/visual_reason` from a Unity-reported signal.

    Safe to call from any context (not tied to the RPC handler); other
    producers (e.g. Sprint 2 Python-side blur detector) can route through
    here to keep a single writer for the key.
    """
    bb = _ensure_bb()
    coerced = _coerce_reason(reason)
    try:
        current = bb.get("session/visual_reason")
    except KeyError:
        current = None
    if current == coerced:
        return
    bb.set("session/visual_reason", coerced)
    logger.info(
        "BB session/visual_reason: %s → %s (ts=%s)",
        current, coerced, ts or time.time(),
    )


def attach_video_state_rpc(room: "Room") -> None:
    """Register the `onVideoDegraded` inbound RPC on the given LiveKit Room.

    Call this after `room.connect()` (or right after `session.start()`), in
    the same place `attach_telemetry_receiver(room)` is called.
    """
    _ensure_bb()

    @room.local_participant.register_rpc_method(_RPC_METHOD)
    async def _on_video_degraded(data: "RpcInvocationData") -> str:
        try:
            payload = json.loads(data.payload) if data.payload else {}
        except (ValueError, TypeError):
            logger.warning(
                "%s: malformed payload from %s: %r",
                _RPC_METHOD, data.caller_identity, data.payload,
            )
            return json.dumps({"status": "ok"})

        reason = str(payload.get("reason", "unknown"))
        ts = payload.get("ts")
        try:
            ts_f = float(ts) if ts is not None else None
        except (TypeError, ValueError):
            ts_f = None

        logger.debug(
            "%s <- %s: reason=%s ts=%s",
            _RPC_METHOD, data.caller_identity, reason, ts_f,
        )
        handle_video_degraded(reason, ts_f)
        return json.dumps({"status": "ok"})

    logger.info("Video-state RPC attached: %s", _RPC_METHOD)


__all__ = ["attach_video_state_rpc", "handle_video_degraded"]
