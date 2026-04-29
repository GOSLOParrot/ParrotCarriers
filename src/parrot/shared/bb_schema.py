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
    # NOTE (Sprint 2 T12, closes Sprint 1 §6.1):
    # `global/soul_constraints` was declared here in Sprint 1 planning but the
    # SOUL_CONSTRAINTS table ended up as a module-level dict inside
    # `brain.soul` and is never written to the Blackboard. To avoid a
    # dual-identity trap (BB declared but absent → KeyError surprises) we
    # remove the key from the manifest entirely and keep `brain.soul.
    # SOUL_CONSTRAINTS` as the single source of truth. Injector / vision
    # layers import it directly. Re-introduce a BB key ONLY when we actually
    # need per-scene or runtime hot-swappable constraints (Sprint 4+).

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
    # ───── Sprint4 ECP candidate keys (DRIFT NOTE) ─────
    # Declared by `sprint4_protocol_v2_ecp.md` §3.2 as the unified state surface
    # the protocol upgrade promises. Producers do NOT exist yet — Phase 3
    # (lifecycle / audio / connection health) and Phase 4 (snapshot / sighting
    # / attention) own the writers. We list them here so any code that tries to
    # read them fails loudly via `get_key()` instead of silently typo-ing a new
    # name. DO NOT register WRITE access in py-trees clients until the writer
    # module actually lands; the same anti-pattern killed
    # `global/soul_constraints` in Sprint 1 (see comment above). When you add
    # the producer, remove this `# CANDIDATE` marker line.
    BlackboardKey(
        BbScope.SESSION,
        "session/connection_health",  # CANDIDATE — no writer yet (Phase 3)
        "dict[str, Any]",
        "brain.telemetry_receiver",
        "Unified room / Brain / audio / video / RPC readiness snapshot.",
        event_driven=True,
    ),
    BlackboardKey(
        BbScope.SESSION,
        "session/audio_route_policy",  # CANDIDATE — no writer yet (Phase 3)
        "dict[str, Any]",
        "brain.telemetry_receiver",
        "Current input/output route policy and echo-risk summary.",
        event_driven=True,
    ),
    BlackboardKey(
        BbScope.SESSION,
        "session/ecp_state",  # CANDIDATE — no writer yet (Phase 2 EcpState upload)
        "dict[str, Any]",
        "brain._rpc_bridge",
        "Latest Unity frontend state-machine snapshot.",
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
    BlackboardKey(
        BbScope.TICK,
        "tick/last_ecp_ack",
        # DRIFT NOTE (Sprint4 ECP-minimal, 2026-04-29):
        # Originally declared as "EcpAck" but the bridge currently mirrors the
        # same legacy ack dict we write to `tick/last_rpc_ack` plus
        # `command_id` / `ecp_status` fields. Promoting to a full EcpAck
        # Pydantic shape is Phase 2 work (needs Unity-side full state upload).
        # Keeping the type_hint as the actual stored shape so consumers don't
        # rely on fields that aren't there yet.
        "dict[str, Any]",
        "brain._rpc_bridge",
        "Mirrored RPC ack augmented with ECP command_id/status (Phase 2 will replace with full EcpAck).",
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
        # Writer reassigned in Sprint 1 S1.A2 (see sprint0_completion §10.4):
        # `brain.gesture_source` was a speculative standalone module; the actual
        # data source is XRHandTracker → DataChannel → telemetry_receiver.
        "brain.telemetry_receiver",
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
    # CANDIDATE — Phase 4 (focus-tools / snapshot-identify) owns the producer.
    # See sprint4_protocol_v2_ecp.md §7.2 / §7.3.
    #
    # Phase 4 update (2026-04-29, entry doc §8.4): producer reassigned from
    # `brain.telemetry_receiver` to `dsg.attention.threshold` — Focus/BBox
    # attention is computed by the threshold accumulator, not by the raw
    # telemetry receiver. The receiver only mirrors transport-level state;
    # the Phase 4 临时阈值器 is the BB writer for this key. Mirror is removed
    # when the Phase 4 W6-7 producer lands.
    BlackboardKey(
        BbScope.TRANSIENT,
        "transient/current_attention_hint",  # Phase 4 W6-7 producer = dsg.attention.threshold (active)
        # Payload shape (locked Phase 4 W6-7, schema_version=1):
        #   schema_version: int
        #   ref_id: str (RefBinding.ref_id, may be "" if registry race)
        #   weight: float
        #   subject_kind: "bbox" | "focus"
        #   subject_id: Unity-side bbox_id or focus_id
        #   label: str (human-readable)
        #   delta_applied: float
        #   source_event_id: str (EcpEvent.event_id of the trigger)
        #   ts_ms: int (epoch ms)
        "dict[str, Any]",
        "dsg.attention.threshold",
        "Current Focus / Bounding Box attention hint; expires quickly.",
        event_driven=True,
    ),
    BlackboardKey(
        BbScope.TRANSIENT,
        "transient/last_sighting_event",  # CANDIDATE — Phase 4 W4-5 producer = brain.observer.sighting
        "dict[str, Any]",
        "brain.observer.sighting",
        "Most recent object / region sighting evidence.",
        event_driven=True,
    ),

    # ───── Sprint4 Phase 4 attention config (W6-7) ─────
    # CANDIDATE — Unity ScriptableObject `ParrotAttentionConfig` writes the
    # active Δ_focus / Δ_bbox / threshold + TTL into BB so backend tooling
    # (FocusBboxThreshold, debug HUD) reads the same values the user sees in
    # the Inspector. Locked in entry doc §8.1 L9.
    #
    # Wire format: {"delta_focus": float, "delta_bbox": float, "threshold":
    # float, "target_ttl_s": float, "schema_version": int=1}. Producer = the
    # `EcpEventDispatcher` (Unity downstream router) which echoes the SO on
    # Brain handshake; documented here as `brain._rpc_bridge` because that is
    # the Brain-side surface that receives the Echo and writes BB.
    #
    # ⚠ Brain 自审 F-05 (2026-04-30): Echo 路径 Phase 4 W6-7 仅声明、未接通。
    # Brain 端读取者 (FocusBboxThreshold.__init__) 当前不读这个 key，永远走
    # 硬编码 DEFAULTS。完整接通顺序见 entry doc §8.1 L9 ⚠ 注。在 Unity B chat
    # 落地 ParrotAttentionConfig SO + EcpEvent attention.config.echo 之前，
    # 这个 key 保留 # CANDIDATE 标记。
    BlackboardKey(
        BbScope.GLOBAL,
        "global/attention_thresholds",  # CANDIDATE — Echo 路径未接通 (F-05)
        "dict[str, Any]",
        "brain._rpc_bridge",
        "Δ_focus / Δ_bbox / threshold / target_ttl_s (Unity ScriptableObject Echo).",
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
