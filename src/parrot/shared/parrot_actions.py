"""Parrot action and state enums — shared between backend BT and frontend Animator.

Unity Animator state names must match these string values exactly.
"""

from __future__ import annotations

from enum import Flag, auto
from enum import Enum as _Enum


class ParrotAnimation(str, _Enum):
    """Animations the parrot can play (maps to Unity Animator clips)."""

    IDLE = "idle"
    FLY = "fly"
    DANCE = "dance"
    WING_FLAP = "wing_flap"
    PERCH = "perch"
    SIT = "sit"
    HEAD_BOB = "head_bob"
    SLEEP = "sleep"


class ParrotBodyState(str, _Enum):
    """High-level body states (Unity Animator top layer).

    NEED-P3-A (cross_chat_pending_registry_20260507 §4.A): these 5
    values are wire-locked (Phase 4 §8 + cs_parity guard). They suit
    bird-like avatars; non-bird models registered via ModelManifest
    must squash their own state ("walking" / "waving" / "sitting") to
    the closest of these 5 → wire粒度 loss.

    Two upgrade options (need P3 ADR + cs_parity bump):
        Option A (conservative): keep these 5 + add
            ``EcpFrontendState.controller_body_state: str`` free field
            (model-defined), Brain LLM reads via attach_state_header.
        Option B (aggressive): upgrade body_state to free string;
            old 5 become "standard dialect".

    See goslo_modularization_residual_debt_20260506.md §2.2 #2 for the
    full evaluation.
    """

    IDLE = "idle"
    FLYING = "flying"
    PERCHING = "perching"
    DANCING = "dancing"
    FROZEN = "frozen"


class CognitiveState(str, _Enum):
    """Cognitive state mirror — Brain side, not Unity side.

    Source: parrot_behavior_rules.md §1.3 (LISTENING / THINKING / SPEAKING /
    IDLE_MIND). Mapped 1:1 from livekit-agents `AgentState` literal:

        initializing → IDLE_MIND  (treat startup as no-cognitive-task)
        idle         → IDLE_MIND
        listening    → LISTENING
        thinking     → THINKING
        speaking     → SPEAKING

    Producer (declared in `shared.bb_schema`): brain.agent (via
    `parrot.brain.cognitive_state_tracker.attach_cognitive_state_tracker`).
    Consumer: Sprint4 Phase 4 W3 selection-C tool wrappers (fly_to /
    animate / set_video_tier prepend a state header to the LLM-facing tool
    result).
    """

    LISTENING = "LISTENING"
    THINKING = "THINKING"
    SPEAKING = "SPEAKING"
    IDLE_MIND = "IDLE_MIND"


class BehaviorMode(Flag):
    """Behavior modes — stackable flags (Brooks subsumption-inspired).

    P1.5: only BASE + COMPANION are active.
    P2+: BUTLER, RESEARCHER, PLAYFUL added.
    P2.5+: ROLEPLAY added (NEED-P3-MODE-ROLEPLAY).

    ROLEPLAY semantics (menu_design_complete §3.3 + dsg_decisions_master §3.2):
        When set, persona_loader applies the persona's ``mode.roleplay``
        section, the ``OBSIDIAN_SETTING_ROLEPLAY`` bucket is included in
        active context (already preserved across scene switches), and the
        L2-B graph admits the ``ROLEPLAY_TEMP`` bucket. Frontend may key on
        ROLEPLAY to swap themed sprites, but skin swap is independent of
        this flag — see menu_design_complete §6.

    Adding ROLEPLAY does **not** touch wire / cs_parity: BehaviorMode is
    Python-only (Brain ↔ Redis Pub-Sub serialised by name), never crosses
    the LiveKit DataChannel as a typed value.
    """

    BASE = auto()
    COMPANION = auto()
    BUTLER = auto()
    RESEARCHER = auto()
    PLAYFUL = auto()
    ROLEPLAY = auto()
