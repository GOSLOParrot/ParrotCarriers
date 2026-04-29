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
    """High-level body states (Unity Animator top layer)."""

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
    """

    BASE = auto()
    COMPANION = auto()
    BUTLER = auto()
    RESEARCHER = auto()
    PLAYFUL = auto()
