"""Shared RPC forwarding logic — Tool → LiveKit RPC → Unity client.

All Unity-bound tools (fly_to, animate, captureSnapshot, etc.) go through
this bridge. Sprint 1 S1.A4 adds two BB writer responsibilities on this
module (writer="brain._rpc_bridge"):

    tick/last_rpc_ack   — {ok, rpc, reason, detail, ts}
        Every call_unity_rpc outcome (success / timeout / transport error /
        application-level reject) mirrors here so context_injector can
        surface failures to Gemini via layer ③ Conscious Report. This is
        the backbone the audit_identify_object §7 "felt experience"
        redesign leans on: the LLM sees failure reasons inline with the
        tool return value, never from a stale async side-channel.

    session/scene        — Scene enum, set on session start by whoever
        owns the pairing decision (typically brain.agent). We expose
        `set_scene()` here because the _rpc_bridge already sits on the
        Unity-paired path; keeping the scene writer here avoids another
        ownership dance in Sprint 1.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from livekit.agents import get_job_context
from livekit.agents.llm import ToolError

from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.vision_state import Scene

if TYPE_CHECKING:
    import py_trees

logger = logging.getLogger(__name__)

UNITY_IDENTITY_PREFIX = "unity"
_WRITER = "brain._rpc_bridge"


@dataclass(frozen=True)
class RpcPushResult:
    """Structured outcome for intent RPCs that must feed a same-turn tool result."""

    ok: bool
    reason: str
    detail: str = ""
    response: str = ""

_bb: "py_trees.blackboard.Client | None" = None


def _ensure_bb() -> "py_trees.blackboard.Client":
    global _bb
    if _bb is None:
        _bb = open_bb_client(name="_rpc_bridge", writer=_WRITER)
    return _bb


def _write_ack(
    *,
    ok: bool,
    rpc: str,
    reason: str = "",
    detail: str = "",
) -> None:
    """Mirror RPC outcome to tick/last_rpc_ack (event-driven)."""
    bb = _ensure_bb()
    bb.set(
        "tick/last_rpc_ack",
        {
            "ok": ok,
            "rpc": rpc,
            "reason": reason,
            "detail": detail,
            "ts": time.time(),
        },
    )


def set_scene(scene: Scene) -> None:
    """Set session/scene. Called once on session-start by brain.agent."""
    bb = _ensure_bb()
    try:
        current = bb.get("session/scene")
    except KeyError:
        current = None
    if current != scene:
        bb.set("session/scene", scene)
        logger.info("BB session/scene: %s → %s", current, scene)


def _find_unity_participant(room) -> str | None:
    """Find the first Unity client participant in the room.

    ARCHITECTURAL RISK (P2+):
    Currently returns the FIRST participant with the 'unity' prefix.
    If multiple Unity clients (e.g., sim_client + Unity Editor) are in the room,
    RPC commands (flyTo, animate) will only be sent to one arbitrary client.
    In P2+ (Multi-user/Multi-device), this needs to be refactored to either
    broadcast to all, or target a specific user's AR view via Context.
    """
    for identity in room.remote_participants:
        if identity.startswith(UNITY_IDENTITY_PREFIX):
            return identity
    return None


def _classify_response(response: str) -> tuple[bool, str, str]:
    """Parse Unity's JSON response into (ok, reason, detail).

    Unity ParrotRpcHandler returns either:
        {"status": "ok", ...}                         → (True, "", "")
        {"status": "error", "message": "..."}         → (False, "rejected", message)
    Any non-JSON or missing-status response is treated as malformed.
    """
    try:
        data = json.loads(response) if response else {}
    except (ValueError, TypeError):
        return (False, "malformed", response[:200] if response else "")

    status = data.get("status")
    if status == "ok":
        return (True, "", "")
    if status == "error":
        return (
            False,
            str(data.get("reason", "rejected") or "rejected"),
            str(data.get("message", "")),
        )
    return (False, "malformed", str(data)[:200])


def _result_from_response(response: str) -> RpcPushResult:
    ok, reason, detail = _classify_response(response)
    return RpcPushResult(
        ok=ok,
        reason=reason or ("applied" if ok else "unknown"),
        detail=detail,
        response=response,
    )


async def call_unity_rpc(
    method: str,
    payload: dict,
    timeout: float = 10.0,
) -> str:
    """Forward an RPC call to the Unity client via LiveKit.

    Outcome mirrors to `tick/last_rpc_ack` regardless of success/failure so
    downstream (context_injector / soul constraints) can react. Raises
    `ToolError` on transport failure so the LLM surface gets a synchronous,
    user-facing error message (audit_identify_object §7 "felt experience").
    """
    room = get_job_context().room
    unity_id = _find_unity_participant(room)

    if not unity_id:
        _write_ack(
            ok=False,
            rpc=method,
            reason="no_unity",
            detail="No participant with 'unity' prefix in room",
        )
        logger.warning("RPC %s failed: no Unity client in room", method)
        raise ToolError(
            "The AR display isn't connected right now. "
            "I can't move or animate until it joins the room."
        )

    logger.info("RPC → Unity [%s] method=%s", unity_id, method)
    try:
        response = await room.local_participant.perform_rpc(
            destination_identity=unity_id,
            method=method,
            payload=json.dumps(payload),
            response_timeout=timeout,
        )
    except Exception as e:
        _write_ack(
            ok=False,
            rpc=method,
            reason="transport",
            detail=f"{type(e).__name__}: {e}",
        )
        logger.warning("RPC %s transport error: %s", method, e)
        raise

    ok, reason, detail = _classify_response(response)
    _write_ack(ok=ok, rpc=method, reason=reason, detail=detail)
    if not ok:
        logger.info("RPC %s rejected: reason=%s detail=%s", method, reason, detail)
    return response


async def push_video_tier(video_tier: str, *, reason: str = "") -> bool:
    """Intent-layer RPC: PerceptionSupervisor → Unity `setVideoTier`.

    Sprint 2 T10. Called from `brain.perception_supervisor` when the Two-
    axis decision loop commits a new VideoTier. Unity's
    `VideoTierReceiver.cs` receives the method and (in Sprint 2) logs +
    acknowledges; actual bitrate/fps re-encoding lands in Sprint 3 when the
    AR rebuild is in flight.

    Returns True on ok, False on any failure (including no-Unity). Non-
    raising by design: a tier push failing must not crash the supervisor
    loop; the failure is already mirrored to tick/last_rpc_ack and the
    next decision tick will retry if BB state still demands the move.

    Args:
        video_tier: One of VideoTier enum string values
            (VIDEO_OFF / VIDEO_GEMINI_ONLY / VIDEO_FULL / VIDEO_BURST).
        reason: Optional human-readable cause string, forwarded to Unity
            for log context only.
    """
    result = await push_video_tier_result(video_tier, reason=reason)
    return result.ok


async def push_video_tier_result(video_tier: str, *, reason: str = "") -> RpcPushResult:
    """Push `setVideoTier` to Unity and return a structured same-turn result.

    User-facing tools use this instead of the boolean wrapper so GOSLO can
    wait for Unity's applied/rejected response before speaking. Background
    Supervisor ticks can keep using `push_video_tier()` when failure-only
    escalation through `tick/last_rpc_ack` is enough.
    """
    room = get_job_context().room
    unity_id = _find_unity_participant(room)

    if not unity_id:
        _write_ack(
            ok=False,
            rpc="setVideoTier",
            reason="no_unity",
            detail=f"tier={video_tier}",
        )
        logger.info(
            "push_video_tier: no Unity client — tier=%s dropped", video_tier
        )
        return RpcPushResult(
            ok=False,
            reason="no_unity",
            detail=f"tier={video_tier}",
        )

    payload = {"video_tier": video_tier, "reason": reason}
    logger.info(
        "RPC → Unity [%s] setVideoTier=%s reason=%s",
        unity_id, video_tier, reason or "-",
    )
    try:
        response = await room.local_participant.perform_rpc(
            destination_identity=unity_id,
            method="setVideoTier",
            payload=json.dumps(payload),
            response_timeout=12.0,
        )
    except Exception as e:
        _write_ack(
            ok=False,
            rpc="setVideoTier",
            reason="transport",
            detail=f"{type(e).__name__}: {e}",
        )
        logger.warning("setVideoTier transport error: %s", e)
        return RpcPushResult(
            ok=False,
            reason="transport",
            detail=f"{type(e).__name__}: {e}",
        )

    result = _result_from_response(response)
    _write_ack(
        ok=result.ok,
        rpc="setVideoTier",
        reason="" if result.ok else result.reason,
        detail=result.detail,
    )
    return result


__all__: list[str] = [
    "UNITY_IDENTITY_PREFIX",
    "call_unity_rpc",
    "push_video_tier",
    "push_video_tier_result",
    "RpcPushResult",
    "set_scene",
]
