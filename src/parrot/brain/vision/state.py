"""GOSLO's visual self-perception — Blackboard writer for VisualState family.

Sprint 1 T5 (inbound wire):
    session/visual_reason     ← Unity RPC `onVideoDegraded(reason, ts)`

Sprint 1 T6 (this module, fusion):
    session/visual_state      ← fused from {session/visual_reason,
                                            tick/ar_tracking_state}
    (tick/last_rpc_ack is available but Sprint 1 does NOT wire it into
    visual_state because Sprint 1 can't tell camera-related RPC failures
    from unrelated ones. Picked up in Sprint 2 when identify_object upgrades.)

Both session/visual_state and session/visual_reason declare this module
(`brain.vision.state`) as sole writer in `shared/bb_schema.BB_KEYS`.
Consumers (context_injector, soul, identify_object upgrades) are READ-only
on them.

## Fusion triggering

`recompute_visual_state()` is pure (reads BB, writes BB only on change). It
is called from:

1. `handle_video_degraded` — self-trigger after visual_reason change
2. `telemetry_receiver._write_ar_tracking_state` — after ar_tracking changes
3. `context_injector` (pull model) — before composing a turn-opening
   context block, Injector calls it once to guarantee freshness

This hybrid push/pull keeps Sprint 1 free of background loops or py-trees
listener plumbing while still feeling event-driven from the Injector's
point of view.

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
from parrot.shared.vision_state import VisualState, VisualStateReason

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
    here to keep a single writer for the key. Always triggers a VisualState
    re-fuse so downstream consumers see both keys update atomically.
    """
    bb = _ensure_bb()
    coerced = _coerce_reason(reason)
    try:
        current = bb.get("session/visual_reason")
    except KeyError:
        current = None
    if current != coerced:
        bb.set("session/visual_reason", coerced)
        logger.info(
            "BB session/visual_reason: %s → %s (ts=%s)",
            current, coerced, ts or time.time(),
        )
    recompute_visual_state()


# ───────────────────────────── T6: VisualState fusion ─────────────────────

# VisualStateReason → target VisualState. Reasons that map to None fall
# through to AR-tracking fallbacks below.
_REASON_TO_STATE: dict[VisualStateReason, VisualState | None] = {
    VisualStateReason.OK: None,
    VisualStateReason.APP_BACKGROUNDED: VisualState.PAUSED,
    VisualStateReason.USER_MUTED: VisualState.PAUSED,
    VisualStateReason.TIER_OFF: VisualState.PAUSED,
    VisualStateReason.TRACK_MUTED: VisualState.PAUSED,
    VisualStateReason.AR_LOST: VisualState.PAUSED,
    VisualStateReason.OBSTRUCTED: VisualState.BLOCKED,
    VisualStateReason.DARK_FRAME: VisualState.DEGRADED,
    VisualStateReason.STATIC_FRAME: VisualState.DEGRADED,
    VisualStateReason.BLUR_FRAME: VisualState.DEGRADED,
    VisualStateReason.LOW_BITRATE: VisualState.DEGRADED,
    VisualStateReason.AR_LIMITED: VisualState.DEGRADED,
    # UNKNOWN is intentionally absent → falls through to safe-default DEGRADED
}


def _compute_visual_state() -> VisualState:
    """Pure: read current BB inputs and return the fused VisualState.

    Precedence (§3.3 + audit §1.2 'felt experience' principle):
      1. explicit reason maps to PAUSED / BLOCKED / DEGRADED
      2. reason=OK or absent → fall through to AR tracking signal
      3. AR NOT_TRACKING → PAUSED; AR LIMITED → DEGRADED
      4. otherwise ACTIVE
      5. reason=UNKNOWN (unrecognized vocab) → DEGRADED (be cautious)
    """
    bb = _ensure_bb()
    try:
        reason = bb.get("session/visual_reason")
    except KeyError:
        reason = None
    try:
        ar = bb.get("tick/ar_tracking_state")
    except KeyError:
        ar = None

    if isinstance(reason, VisualStateReason):
        mapped = _REASON_TO_STATE.get(reason, None)
        if mapped is not None:
            return mapped
        if reason == VisualStateReason.UNKNOWN:
            return VisualState.DEGRADED
        # reason == OK → fall through

    if ar == "NOT_TRACKING":
        return VisualState.PAUSED
    if ar == "LIMITED":
        return VisualState.DEGRADED

    return VisualState.ACTIVE


def recompute_visual_state() -> VisualState:
    """Recompute `session/visual_state` from current inputs; write if changed.

    Idempotent. Called push-style after any input write, and pull-style from
    context_injector at turn boundaries. Returns the (new) VisualState.
    """
    bb = _ensure_bb()
    new_state = _compute_visual_state()
    try:
        current = bb.get("session/visual_state")
    except KeyError:
        current = None
    if current != new_state:
        bb.set("session/visual_state", new_state)
        logger.info("BB session/visual_state: %s → %s", current, new_state)
    return new_state


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


__all__ = [
    "attach_video_state_rpc",
    "handle_video_degraded",
    "recompute_visual_state",
]
