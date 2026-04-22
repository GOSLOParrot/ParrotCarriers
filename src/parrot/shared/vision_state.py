"""Session-scoped observable state enums — VisualState + Scene.

Sprint 0 Schema V1. Source of truth: `ar_feature_vision.md §3.3` (VisualState
four levels, ratified by user decision V1) and §3.4 (Scene list, ratified by
decision S1).

These enums live in `shared/` because they are consumed by Brain, DSG,
Scheduler, and Unity-telemetry-ingress alike. Keep them value-only: decision
logic (when to flip, how to notify Gemini) belongs in Sprint 1 S1.C injector.
"""

from __future__ import annotations

from enum import Enum


class VisualState(str, Enum):
    """Four-level self-awareness of current vision quality.

    Semantics (from ar_feature_vision §3.3):
        ACTIVE    — seeing clearly; normal picture description allowed
        DEGRADED  — seeing but blurry / dim / shaky; no assertions, use
                    hedging language ("looks like", "seems")
        PAUSED    — explicitly off (app-backgrounded / user-muted / tier=OFF);
                    no picture mentions, fall back to audio + memory
        BLOCKED   — camera obstructed (hand / object in front); actively
                    call it out ("I am being blocked! move your hand")
    """

    ACTIVE = "active"
    DEGRADED = "degraded"
    PAUSED = "paused"
    BLOCKED = "blocked"


class Scene(str, Enum):
    """Current physical environment GOSLO believes she is in.

    P2 ships only the first two. P3+ scenes stay as future extension points;
    do NOT add them here until real code branches exist.
    """

    DESKTOP_WEBCAM = "desktop_webcam"
    AR_HANDHELD = "ar_handheld"

    # Placeholders (not yet scheduled):
    # AR_WORLD_LOCKED = "ar_world_locked"        # P3 — ARWorldMap anchors
    # OUTDOOR_LIGHT_SHOW = "outdoor_light_show"  # P3+
    # MULTIPLAYER_PRESENCE = "multiplayer_presence"  # P3+ (Sky-style)


class VisualStateReason(str, Enum):
    """Why the VisualState changed. Carried alongside state in Injector msgs.

    One reason may trigger multiple states (e.g. `app_backgrounded` →
    PAUSED, `ar_lost` → DEGRADED or PAUSED depending on duration). The
    mapping is Sprint 1 S1.C's job; this enum just fixes the vocabulary.
    """

    OK = "ok"
    DARK_FRAME = "dark_frame"
    STATIC_FRAME = "static_frame"
    BLUR_FRAME = "blur_frame"
    OBSTRUCTED = "obstructed"
    AR_LIMITED = "ar_limited"
    AR_LOST = "ar_lost"
    TRACK_MUTED = "track_muted"
    TRACK_REBUILDING = "track_rebuilding"
    LOW_BITRATE = "low_bitrate"
    APP_BACKGROUNDED = "app_backgrounded"
    USER_MUTED = "user_muted"
    TIER_OFF = "tier_off"
    UNKNOWN = "unknown"


__all__ = ["Scene", "VisualState", "VisualStateReason"]
