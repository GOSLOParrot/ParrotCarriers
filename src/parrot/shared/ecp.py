"""Embodied Control Protocol (ECP) V2 alpha schemas.

Sprint4 introduces ECP as the command/ack envelope between backend decision
logic and the Unity frontend state machine. This module is intentionally small:
it gives existing RPC paths a shared shape without forcing a full action
framework before `flyTo`, `animate`, and `setVideoTier` prove the contract.
"""

from __future__ import annotations

import time
import uuid as uuid_lib
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from parrot.shared.event_log import EventLayer


SCHEMA_VERSION = "ecp.v2.alpha"


def _short_id(prefix: str) -> str:
    return f"{prefix}_{uuid_lib.uuid4().hex[:12]}"


class EcpCommandKind(str, Enum):
    """Initial Sprint4 command kinds."""

    MOVE_TO = "move_to"
    ANIMATE = "animate"
    SET_VIDEO_TIER = "set_video_tier"
    PERCH_TO_FINGER = "perch_to_finger"
    RETURN_TO_VIEW = "return_to_view"
    FOCUS_REGION = "focus_region"
    CAMERA_CAPTURE = "camera_capture"
    CAPTURE_SNAPSHOT = "capture_snapshot"


class EcpInterruptibility(str, Enum):
    """How a frontend command may interact with existing work."""

    NON_INTERRUPTIBLE = "non_interruptible"
    INTERRUPTIBLE = "interruptible"
    PREEMPTIVE = "preemptive"
    QUEUEABLE = "queueable"


class EcpAckStatus(str, Enum):
    """Unity frontend state-machine acknowledgement states."""

    RECEIVED = "received"
    ACCEPTED = "accepted"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PREEMPTED = "preempted"
    FAILED = "failed"
    UNCHANGED = "unchanged"


# ECP status sets are split into THREE bands deliberately. The Sprint4 background
# anchor (`sprint4_protocol_ecp_background_20260429.md` §3.1) makes the felt-
# experience red line explicit: "tool 的同步/异步行为必须和 GOSLO 说出口的话一致".
# If we collapsed `received`/`queued`/`running` into the success set, an
# intermediate ack would silently flip `tick/last_rpc_ack.ok` to True and
# context_injector would stop surfacing pending work to Gemini — the exact
# fire-and-forget regression `parrot_behavior_rules.md` §0.3 forbids.
#
# Use ECP_TERMINAL_SUCCESS for boolean success decisions (tool result, BB ok
# flag). Use ECP_NON_FAILURE only when you specifically need to distinguish
# "still pending, not a hard failure" from a real reject — never as a stand-in
# for completion.

ECP_TERMINAL_SUCCESS: frozenset[str] = frozenset(
    {
        "ok",  # legacy Unity RPC, treated as completion equivalent
        "applied",
        "unchanged",
        EcpAckStatus.COMPLETED.value,
    }
)

ECP_INTERMEDIATE_STATUSES: frozenset[str] = frozenset(
    {
        EcpAckStatus.RECEIVED.value,
        EcpAckStatus.ACCEPTED.value,
        EcpAckStatus.QUEUED.value,
        EcpAckStatus.RUNNING.value,
    }
)

ECP_FAILURE_STATUSES: frozenset[str] = frozenset(
    {
        "error",  # legacy Unity RPC
        EcpAckStatus.REJECTED.value,
        EcpAckStatus.EXPIRED.value,
        EcpAckStatus.CANCELLED.value,
        EcpAckStatus.PREEMPTED.value,
        EcpAckStatus.FAILED.value,
    }
)

# Anything Unity could legally return that does NOT mean "this command failed".
# Used by callers that want to keep an intermediate ack out of the failure
# escalation path without falsely claiming success.
ECP_NON_FAILURE: frozenset[str] = ECP_TERMINAL_SUCCESS | ECP_INTERMEDIATE_STATUSES

# Backwards-compatible alias for code paths that genuinely want "anything that
# is not a failure". New code should reach for ECP_TERMINAL_SUCCESS instead.
ECP_SUCCESS_STATUSES: frozenset[str] = ECP_NON_FAILURE


class EcpSource(BaseModel):
    """Causal source of an ECP command."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    actor: str = Field(default="", max_length=128)
    turn_id: str = ""
    sighting_id: str = ""
    snapshot_uuid: str = ""
    parent_event_id: str = ""


class EcpCommand(BaseModel):
    """Backend → Unity goal command envelope."""

    model_config = ConfigDict(frozen=True, extra="forbid", use_enum_values=True)

    schema_version: str = SCHEMA_VERSION
    command_id: str = Field(default_factory=lambda: _short_id("cmd"))
    kind: EcpCommandKind
    issued_at: float = Field(default_factory=time.time, gt=0.0)
    valid_after: float = 0.0
    expires_at: float = 0.0
    # `EventLayer` (reflex/intent/task) is the same enum the L0 EventEnvelope
    # already uses; sharing it keeps `ecp.command.issued` events comparable to
    # the rest of the scheduling-layer telemetry. Serialised to a plain string
    # via `use_enum_values=True` so Unity's JsonUtility deserialisation is
    # unaffected.
    layer: EventLayer = EventLayer.INTENT
    priority: int = 50
    interruptibility: EcpInterruptibility = EcpInterruptibility.INTERRUPTIBLE
    source: EcpSource = Field(default_factory=EcpSource)
    target: dict[str, Any] = Field(default_factory=dict)
    expected_duration_ms: int = 0
    fallback_behavior: str = "idle"
    meta: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def for_legacy_rpc(
        cls,
        *,
        kind: EcpCommandKind,
        target: dict[str, Any],
        actor: str,
        layer: EventLayer = EventLayer.INTENT,
        priority: int = 50,
        expires_in_s: float = 10.0,
        interruptibility: EcpInterruptibility = EcpInterruptibility.INTERRUPTIBLE,
        expected_duration_ms: int = 0,
        meta: dict[str, Any] | None = None,
    ) -> "EcpCommand":
        """Build an ECP command for an existing Unity RPC handler.

        ``meta`` carries optional routing / addressing hints that ride alongside
        the command without changing the wire envelope (Phase 4 §8 lock holds:
        ``EcpCommand.meta`` is an existing ``dict[str, Any]`` field). The first
        consumer is the GOSLO-model-modularization work — Brain stamps
        ``meta={"model_id": "..."}`` so Unity-side ParrotRegistry can route
        future multi-actor commands without breaking single-active deployments
        (handlers that don't care about ``meta`` simply ignore it).
        """
        now = time.time()
        return cls(
            kind=kind,
            issued_at=now,
            valid_after=now,
            expires_at=now + expires_in_s if expires_in_s > 0 else 0.0,
            layer=layer,
            priority=priority,
            interruptibility=interruptibility,
            source=EcpSource(actor=actor),
            target=target,
            expected_duration_ms=expected_duration_ms,
            meta=dict(meta) if meta else {},
        )


class ConnectionOverall(str, Enum):
    """Sprint4 Phase 3 connection-health 4-state aggregate.

    Source: ``.cursor/skills/livekit-unity-lifecycle/IMPL_REF.md §4.1``.
    Brain / Gemini consume this single field rather than the 11-state
    Unity FSM; lifecycle FSM stays Unity-side.
    """

    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class EcpFrontendState(BaseModel):
    """Minimal Unity frontend state snapshot included in acks/state sync.

    Sprint4 Phase 3: ``connection_overall`` carries the 4-state aggregate so a
    per-command ack can announce overall health without dragging the full
    ConnectionHealthState through every reply. Full health goes via periodic
    ``EcpState`` (see :class:`EcpState`).
    """

    model_config = ConfigDict(frozen=True, extra="forbid", use_enum_values=True)

    body_state: str = ""
    head_state: str = ""
    cognitive_state: str = ""
    active_locks: tuple[str, ...] = ()
    active_command_id: str = ""
    video_tier: str = ""
    app_lifecycle_state: str = ""
    ar_tracking_state: str = ""
    connection_overall: ConnectionOverall = ConnectionOverall.UNKNOWN


class EcpConnectionHealth(BaseModel):
    """Sprint4 Phase 3 ConnectionHealthState wire form.

    Mirrors the Unity ``ConnectionHealthState`` struct field-for-field
    (see ``unity/ArSpike/Assets/Scripts/ParrotApp/Health/ConnectionHealthState.cs``).
    Embedded inside :class:`EcpState` for periodic uplink; the per-command
    :class:`EcpAck` only carries the 4-state ``connection_overall`` summary.

    Producer routing: ``.cursor/skills/livekit-unity-lifecycle/IMPL_REF.md §4.2``.
    Single-producer-per-field is enforced by Unity ``ConnectionHealthAggregator``;
    this Pydantic model is a passive consumer/audit shape on the Brain side.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", use_enum_values=True)

    room_connected: bool = False
    brain_present: bool = False
    rpc_ready: bool = False
    datachannel_ready: bool = False

    audio_publish_attempted: bool = False
    audio_published: bool = False
    audio_last_error: str = ""

    video_publish_attempted: bool = False
    video_published: bool = False
    video_first_frame: bool = False
    video_fresh_frame: bool = False
    video_tier: str = ""
    video_lifecycle_reason: str = ""

    ar_tracking_state: str = ""

    reconnect_attempt_count: int = 0
    last_disconnected_at: float = 0.0

    overall: ConnectionOverall = ConnectionOverall.UNKNOWN
    last_state_change_at: float = 0.0


class EcpState(BaseModel):
    """Periodic Unity → Brain frontend-state heartbeat.

    Spec: ``.cursor/memory/architecture/sprint4_protocol_v2_ecp.md §5.3`` +
    Phase 3 extension carrying the full :class:`EcpConnectionHealth` payload
    (decision: ``docs/sprint4_research/result/INDEX_for_phase3.md §1 #13``).

    Transport: Reliable DataChannel by default. ``ParticipantAttributes`` is
    not approved for Sprint4 (spike S7 pending — see lifecycle skill §8).

    DRIFT NOTE (Phase 3 entry, 2026-04-29):
        ``connection_health`` is optional because the Unity heartbeat publisher
        may be online before the aggregator has any signal (cold-start window).
        Brain consumers must treat ``connection_health is None`` the same as
        ``overall=unknown``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", use_enum_values=True)

    schema_version: str = SCHEMA_VERSION
    ts: float = Field(default_factory=time.time, gt=0.0)
    unity_identity: str = ""
    room_id: str = ""

    body_state: str = ""
    head_state: str = ""
    cognitive_state: str = ""

    active_command_id: str = ""
    queued_command_ids: tuple[str, ...] = ()
    active_locks: tuple[str, ...] = ()
    last_ack_id: str = ""

    video_tier: str = ""

    app_lifecycle_state: str = ""
    ar_tracking_state: str = ""

    connection_health: EcpConnectionHealth | None = None
    meta: dict[str, Any] = Field(default_factory=dict)


class EcpAck(BaseModel):
    """Unity → backend acknowledgement for one ECP command."""

    model_config = ConfigDict(frozen=True, extra="forbid", use_enum_values=True)

    schema_version: str = SCHEMA_VERSION
    command_id: str = ""
    ack_id: str = Field(default_factory=lambda: _short_id("ack"))
    status: EcpAckStatus
    reason: str = ""
    frontend_state: EcpFrontendState = Field(default_factory=EcpFrontendState)
    received_at: float = Field(default_factory=time.time, gt=0.0)
    started_at: float = 0.0
    completed_at: float = 0.0
    detail: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)

    @property
    def ok(self) -> bool:
        # Use the strict terminal-success band: an `accepted`/`running` ack is
        # not a completion. Callers that want "anything that is not a failure"
        # should branch on `ECP_NON_FAILURE` explicitly.
        return str(self.status) in ECP_TERMINAL_SUCCESS


def wrap_legacy_rpc_payload(
    payload: dict[str, Any],
    *,
    kind: EcpCommandKind,
    target: dict[str, Any],
    actor: str,
    layer: EventLayer = EventLayer.INTENT,
    priority: int = 50,
    expires_in_s: float = 10.0,
    expected_duration_ms: int = 0,
    meta: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], EcpCommand]:
    """Attach `_ecp` to a legacy Unity RPC payload.

    Unity's current JsonUtility-based handlers ignore unknown fields, so this is
    safe while old handlers are still deployed. New handlers can read `_ecp` and
    return an ECP-shaped ack.

    ``meta`` is the routing-hint pass-through introduced for the GOSLO model
    modularization work (Step 1, 2026-05-06). ``EcpCommand.meta`` is the
    existing ``dict[str, Any]`` slot on the wire; populating it does not bump
    ``schema_version`` and does not require a cs_parity-side change. Tools
    that don't need routing hints simply omit the kwarg.
    """
    command = EcpCommand.for_legacy_rpc(
        kind=kind,
        target=target,
        actor=actor,
        layer=layer,
        priority=priority,
        expires_in_s=expires_in_s,
        expected_duration_ms=expected_duration_ms,
        meta=meta,
    )
    wrapped = dict(payload)
    wrapped["_ecp"] = command.model_dump(mode="json")
    return wrapped, command


__all__ = [
    "ConnectionOverall",
    "ECP_FAILURE_STATUSES",
    "ECP_INTERMEDIATE_STATUSES",
    "ECP_NON_FAILURE",
    "ECP_SUCCESS_STATUSES",
    "ECP_TERMINAL_SUCCESS",
    "EcpAck",
    "EcpAckStatus",
    "EcpCommand",
    "EcpCommandKind",
    "EcpConnectionHealth",
    "EcpFrontendState",
    "EcpInterruptibility",
    "EcpSource",
    "EcpState",
    "SCHEMA_VERSION",
    "wrap_legacy_rpc_payload",
]
