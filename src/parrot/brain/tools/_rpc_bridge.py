"""Shared RPC forwarding logic — Tool → LiveKit RPC → Unity client.

Unity-bound realtime commands such as fly_to and animate go through this
bridge. Durable App data and image bytes do not belong here; photos use ECP
metadata plus HTTP/storage assets. Sprint 1 S1.A4 adds two BB writer responsibilities on this
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
from parrot.shared.ecp import (
    ECP_FAILURE_STATUSES,
    ECP_INTERMEDIATE_STATUSES,
    ECP_TERMINAL_SUCCESS,
)
from parrot.shared.vision_state import Scene

if TYPE_CHECKING:
    import py_trees

logger = logging.getLogger(__name__)

UNITY_IDENTITY_PREFIX = "unity"
UNITY_PROBE_IDENTITY_MARKERS = ("photo-node-probe",)
_WRITER = "brain._rpc_bridge"

# LiveKit RPC itself is still bounded by response_timeout; this ECP TTL only
# protects Unity's wall-clock expiry check from common phone/host clock skew.
UNITY_RPC_ECP_TTL_S = 90.0


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
    command_id: str = "",
    ecp_status: str = "",
) -> None:
    """Mirror RPC outcome to ``tick/last_rpc_ack`` (event-driven).

    DRIFT NOTE (Sprint4 ECP-minimal, 2026-04-29):
        ``tick/last_ecp_ack`` is currently mirrored as the same legacy
        ``{ok, rpc, reason, detail, command_id, ecp_status, ts}`` dict that
        ``tick/last_rpc_ack`` uses, NOT a real ``EcpAck`` Pydantic dump. The
        Sprint4 protocol design (`sprint4_protocol_v2_ecp.md` §5.2) eventually
        wants a full ``EcpAck`` here (frontend_state, ack_id, started_at,
        completed_at, ...), but Unity's handlers only return a subset and we do
        not yet propagate that subset through the bridge. ``bb_schema``'s
        ``tick/last_ecp_ack`` type_hint is therefore intentionally
        ``dict[str, Any]`` until Phase 2 produces the full envelope upstream.
    """
    bb = _ensure_bb()
    ts = time.time()
    ack = {
        "ok": ok,
        "rpc": rpc,
        "reason": reason,
        "detail": detail,
        "command_id": command_id,
        "ecp_status": ecp_status,
        "ts": ts,
    }
    bb.set("tick/last_rpc_ack", ack)
    if command_id or ecp_status:
        bb.set("tick/last_ecp_ack", ack)


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


def _iter_remote_identities(room) -> tuple[str, ...]:
    remote = getattr(room, "remote_participants", {}) or {}
    if isinstance(remote, dict):
        values = list(remote.keys()) + [
            str(getattr(participant, "identity", "") or "")
            for participant in remote.values()
        ]
    else:
        values = [
            str(getattr(participant, "identity", participant) or "")
            for participant in remote
        ]
    return tuple(dict.fromkeys(identity for identity in values if identity))


def _is_unity_identity(identity: str) -> bool:
    return identity.lower().startswith(UNITY_IDENTITY_PREFIX)


def _is_probe_identity(identity: str) -> bool:
    lowered = identity.lower()
    return any(marker in lowered for marker in UNITY_PROBE_IDENTITY_MARKERS)


def _paired_unity_identity(remote_identities: tuple[str, ...]) -> str:
    """Return the current formal App pairing if BB still matches the room."""
    if not remote_identities:
        return ""
    remote = set(remote_identities)
    bb = _ensure_bb()
    candidates: list[str] = []
    try:
        candidates.append(str(bb.get("session/unity_identity") or ""))
    except KeyError:
        pass
    try:
        ecp_state = bb.get("session/ecp_state")
        if isinstance(ecp_state, dict):
            candidates.append(str(ecp_state.get("unity_identity", "") or ""))
    except KeyError:
        pass

    for candidate in candidates:
        if candidate in remote and _is_unity_identity(candidate):
            return candidate
    return ""


def _find_unity_participant(room) -> str | None:
    """Find the paired formal Unity App participant in the room.

    ARCHITECTURAL RISK (P2+):
    The current app room can contain diagnostic Unity-like participants such as
    photo node probes. Prefer the explicit app pairing captured from
    onSceneReady/onGosloPlaced or ECP state, then fall back to a non-probe
    Unity participant. Multi-user/Multi-device still needs a real target model.
    In P2+ (Multi-user/Multi-device), this needs to be refactored to either
    broadcast to all, or target a specific user's AR view via Context.
    """
    remote_identities = _iter_remote_identities(room)
    paired = _paired_unity_identity(remote_identities)
    if paired:
        return paired

    first_unity = None
    for identity in remote_identities:
        if not _is_unity_identity(identity):
            continue
        if first_unity is None:
            first_unity = identity
        if not _is_probe_identity(identity):
            return identity
    return first_unity


def _classify_response(response: str) -> tuple[bool, str, str]:
    """Parse Unity's JSON response into ``(ok, reason, detail)``.

    Unity may return either legacy status values (``ok`` / ``error``) or
    Sprint4 ECP ack status values (``completed`` / ``rejected`` / ``expired``
    / ...). Any non-JSON or missing-status response is treated as malformed.

    NOTE on intermediate ECP statuses (``received``/``accepted``/``queued``/
    ``running``): we deliberately do NOT treat them as ``ok=True`` so that
    ``tick/last_rpc_ack.ok`` keeps the felt-experience contract from
    `parrot_behavior_rules.md` §0.3 — pending work must remain visible to
    Gemini until the terminal completion ack arrives. Unity's current handlers
    only emit terminal statuses, so this branch is mostly defensive for
    Sprint4 alpha; it becomes load-bearing when Phase 2 begins streaming
    in-progress acks.
    """
    try:
        data = json.loads(response) if response else {}
    except (ValueError, TypeError):
        return (False, "malformed", response[:200] if response else "")

    status = str(data.get("status", "") or "")
    if status in ECP_TERMINAL_SUCCESS:
        # Legacy "ok" replies historically had no `reason`; preserve that to
        # avoid log churn. ECP terminal acks may or may not carry a reason.
        return (True, str(data.get("reason", status if status != "ok" else "") or ""), "")
    if status in ECP_INTERMEDIATE_STATUSES:
        return (
            False,
            str(data.get("reason", status) or status),
            str(data.get("message") or data.get("detail") or ""),
        )
    if status in ECP_FAILURE_STATUSES:
        return (
            False,
            str(data.get("reason", status or "rejected") or "rejected"),
            str(data.get("message") or data.get("detail") or ""),
        )
    return (False, "malformed", str(data)[:200])


def _ack_metadata(response: str) -> tuple[str, str]:
    """Best-effort extraction of ECP command/status metadata from a response."""
    try:
        data = json.loads(response) if response else {}
    except (ValueError, TypeError):
        return "", ""
    return (
        str(data.get("command_id", "") or ""),
        str(data.get("status", "") or ""),
    )


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
    command_id, ecp_status = _ack_metadata(response)
    _write_ack(
        ok=ok,
        rpc=method,
        reason=reason,
        detail=detail,
        command_id=command_id,
        ecp_status=ecp_status,
    )
    if ok:
        logger.info(
            "RPC Unity ack method=%s status=%s reason=%s command_id=%s",
            method,
            ecp_status or "ok",
            reason or "-",
            command_id or "-",
        )
    else:
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

    from parrot.shared.ecp import EcpCommandKind, wrap_legacy_rpc_payload

    payload, command = wrap_legacy_rpc_payload(
        {"video_tier": video_tier, "reason": reason},
        kind=EcpCommandKind.SET_VIDEO_TIER,
        target={"vision_channel": "video", "video_tier": video_tier},
        actor="brain.perception_supervisor",
        expires_in_s=UNITY_RPC_ECP_TTL_S,
        expected_duration_ms=1500,
    )
    logger.info(
        "RPC → Unity [%s] setVideoTier=%s reason=%s command_id=%s",
        unity_id, video_tier, reason or "-", command.command_id,
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
    command_id, ecp_status = _ack_metadata(response)
    _write_ack(
        ok=result.ok,
        rpc="setVideoTier",
        reason="" if result.ok else result.reason,
        detail=result.detail,
        command_id=command_id,
        ecp_status=ecp_status,
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
