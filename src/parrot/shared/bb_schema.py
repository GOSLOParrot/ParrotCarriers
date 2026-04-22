"""Blackboard key registry — V1 manifest.

Sprint 0 Schema V1. Source: `ar_feature_vision.md §3.5` four-scope Blackboard
design (Global / Session / Tick / Transient). Ratified implicitly by the
existing `src/parrot/scheduler/blackboard.py` (py-trees Client with namespace
`scheduler`) — this file extends that one namespace into a documented
multi-scope contract.

This file is **pure manifest** (no py-trees import, no runtime side effects).
Sprint 1 S1.A wires the keys into the actual py-trees Blackboard and Redis
mirror. Consumers should:

    from parrot.shared.bb_schema import BB_KEYS, BlackboardKey, BbScope
    for k in BB_KEYS:
        if k.scope == BbScope.SESSION:
            ...

Each key carries a single **writer** string naming the module that owns
writes. py-trees Blackboard in Sprint 1 should reject other writers via
`Client.register_key(..., access=WRITE if owner else READ)`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BbScope(str, Enum):
    """Four Blackboard scopes (vision §3.5)."""

    GLOBAL = "global"
    SESSION = "session"
    TICK = "tick"
    TRANSIENT = "transient"


@dataclass(frozen=True)
class BlackboardKey:
    """Declaration of one Blackboard key.

    Fields:
        scope        — storage scope (affects persistence + reset lifecycle)
        name         — `<scope>/<path>` identifier used by py-trees
        type_hint    — Python type name as string (avoid real imports here
                       to keep this module dependency-free)
        writer       — dotted module path that owns WRITE access; all other
                       consumers get READ only
        description  — one-line doc string
        event_driven — if True, writing this key fires a listener that may
                       trigger scheduler tick / Injector notify
    """

    scope: BbScope
    name: str
    type_hint: str
    writer: str
    description: str
    event_driven: bool = False


BB_KEYS: tuple[BlackboardKey, ...] = (
    # ───── Global scope (cross-session, loaded from Graphiti / config) ─────
    BlackboardKey(
        BbScope.GLOBAL,
        "global/user_profile",
        "dict[str, Any]",
        "brain.state.loader",
        "Name, preferences, key-memory indices.",
    ),
    BlackboardKey(
        BbScope.GLOBAL,
        "global/behavior_mode",
        "BehaviorMode",
        "brain.tools.set_mode",
        "BASE / COMPANION (see shared.parrot_actions).",
        event_driven=True,
    ),
    BlackboardKey(
        BbScope.GLOBAL,
        "global/soul_constraints",
        "dict[str, Any]",
        "brain.soul.constraints_loader",
        "Per-VisualState action/assertion allow-lists consumed by Soul.",
    ),

    # ───── Session scope (alive while LiveKit room is connected) ─────
    BlackboardKey(
        BbScope.SESSION,
        "session/room_id",
        "str",
        "brain.agent",
        "Current LiveKit room identifier.",
    ),
    BlackboardKey(
        BbScope.SESSION,
        "session/unity_identity",
        "str",
        "brain.agent",
        "Unity participant identity that Brain is paired with.",
    ),
    BlackboardKey(
        BbScope.SESSION,
        "session/connected_since",
        "float",
        "brain.agent",
        "Unix epoch of LiveKit connect.",
    ),
    BlackboardKey(
        BbScope.SESSION,
        "session/scene",
        "Scene",
        "brain._rpc_bridge",
        "Scene enum (DESKTOP_WEBCAM / AR_HANDHELD).",
        event_driven=True,
    ),
    BlackboardKey(
        BbScope.SESSION,
        "session/visual_state",
        "VisualState",
        "brain.vision.state",
        "Four-level vision self-awareness.",
        event_driven=True,
    ),
    BlackboardKey(
        BbScope.SESSION,
        "session/visual_reason",
        "VisualStateReason",
        "brain.vision.state",
        "Explanation for the current visual_state.",
    ),
    BlackboardKey(
        BbScope.SESSION,
        "session/video_tier",
        "VideoTier",
        "brain.perception_supervisor",
        "Current Unity push tier (OFF / GEMINI_ONLY / FULL / BURST).",
        event_driven=True,
    ),
    BlackboardKey(
        BbScope.SESSION,
        "session/dsg_mode",
        "DsgMode",
        "brain.perception_supervisor",
        "Active DSG ingestion mode.",
        event_driven=True,
    ),

    # ───── Tick scope (refreshed on each Unity telemetry / RPC ack) ─────
    BlackboardKey(
        BbScope.TICK,
        "tick/body_state",
        "BodyState",
        "brain.telemetry_receiver",
        "IDLE / FLYING / PERCHING / ... (parrot_behavior_rules §1.1).",
        event_driven=True,
    ),
    BlackboardKey(
        BbScope.TICK,
        "tick/head_state",
        "HeadState",
        "brain.telemetry_receiver",
        "HEAD_FORWARD / HEAD_LOOK_AT / ... .",
    ),
    BlackboardKey(
        BbScope.TICK,
        "tick/cognitive_state",
        "CognitiveState",
        "brain.agent",
        "LISTENING / THINKING / SPEAKING (set by Gemini session hooks).",
    ),
    BlackboardKey(
        BbScope.TICK,
        "tick/ar_tracking_state",
        "str",
        "brain.telemetry_receiver",
        "TRACKING / LIMITED / NOT_TRACKING (ARCore/ARKit session state).",
    ),
    BlackboardKey(
        BbScope.TICK,
        "tick/last_rpc_ack",
        "dict[str, Any]",
        "brain._rpc_bridge",
        "{ok, rpc_name, reason} — failure-feedback surface.",
        event_driven=True,
    ),

    # ───── Transient scope (seconds, consume-then-expire) ─────
    BlackboardKey(
        BbScope.TRANSIENT,
        "transient/just_captured_photo",
        "SnapshotEnvelope",
        "brain.vision.snapshot",
        "Most recent SnapshotEnvelope (identify_object / camera mode).",
        event_driven=True,
    ),
    BlackboardKey(
        BbScope.TRANSIENT,
        "transient/hand_gesture",
        "dict[str, Any]",
        "brain.gesture_source",
        "{kind, hand_pose, since} — expires 2s after last sighting.",
        event_driven=True,
    ),
    BlackboardKey(
        BbScope.TRANSIENT,
        "transient/user_interruption",
        "dict[str, Any]",
        "brain.agent",
        "User mid-turn interruption event.",
        event_driven=True,
    ),
)


_BY_NAME: dict[str, BlackboardKey] = {k.name: k for k in BB_KEYS}


def get_key(name: str) -> BlackboardKey:
    """Look up a BlackboardKey by its `scope/name` identifier."""
    if name not in _BY_NAME:
        raise KeyError(
            f"Unknown Blackboard key: {name!r}. "
            f"Add it to BB_KEYS in shared/bb_schema.py first."
        )
    return _BY_NAME[name]


def keys_in_scope(scope: BbScope) -> tuple[BlackboardKey, ...]:
    """All declared keys within the given scope."""
    return tuple(k for k in BB_KEYS if k.scope == scope)


__all__ = [
    "BB_KEYS",
    "BbScope",
    "BlackboardKey",
    "get_key",
    "keys_in_scope",
]
