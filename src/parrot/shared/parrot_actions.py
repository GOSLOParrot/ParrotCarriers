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
