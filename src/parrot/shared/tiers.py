"""Two-axis work-mode enums — VideoTier × DsgMode.

Sprint 0 Schema V1. Architecture source: `ar_feature_vision.md §3.6` (ratified
by user 2026-04-21 decision M1).

Core idea:
    The video pipeline (Unity push + Python subscribe) and the DSG workflow
    (which Ingest filters are armed, which node states are allowed) are TWO
    orthogonal axes. A10 downtime must be able to degrade video quality
    independently from DSG mode, and vice versa.

Legal combinations (`ALLOWED_COMBOS`) codify vision §3.6 table C1-C5. Any
(video_tier, dsg_mode) outside this set is rejected — those are nonsense
configurations like "CV pipeline armed but video off".

Runtime code (Sprint 2+) will:
    - Write current tier/mode to Blackboard keys `session/video_tier` and
      `session/dsg_mode` (see `shared/bb_schema.py`).
    - Flip modes via `PerceptionSupervisor` (A10 health) or user-initiated
      RPC (`set_video_tier` tool).
    - Route frames through the Ingest filter set associated with the active
      DsgMode.

Schema layer only — no controller logic here.
"""

from __future__ import annotations

from enum import Enum


class VideoTier(str, Enum):
    """How much video Unity is pushing and who subscribes.

    Values map to concrete (bitrate, resolution, fps) targets documented in
    `ar_feature_vision.md §3.6` but those are runtime knobs, not schema.
    """

    VIDEO_OFF = "video_off"
    VIDEO_GEMINI_ONLY = "video_gemini_only"
    VIDEO_FULL = "video_full"
    VIDEO_BURST = "video_burst"


class DsgMode(str, Enum):
    """Which upstream L1.5 sources are allowed into the L2-B graph.

    Mode names reflect the dominant ingestion source:
        DSG_TEXT_ONLY     — only text facts (identify_object / user tag /
                            Obsidian sync); A10 and video both off
        DSG_GEMINI_VISION — Gemini oral transcription also feeds L2-B,
                            strictly TENTATIVE until a non-oral source
                            confirms; A10 off, video limited to Gemini
        DSG_FULL          — A10 CV pipeline (SAM2 + DINOv2 + YOLO) active
        DSG_SENTINEL_AUX  — P4 fallback with laptop-side YOLO; UNCERTAIN only
    """

    DSG_TEXT_ONLY = "dsg_text_only"
    DSG_GEMINI_VISION = "dsg_gemini_vision"
    DSG_FULL = "dsg_full"
    DSG_SENTINEL_AUX = "dsg_sentinel_aux"


class AppCapabilityMode(str, Enum):
    """User-visible capability bundle for the app session.

    reason: ``VideoTier`` and ``DsgMode`` are lower-level perception axes.
    Startup/menu UX needs a single business mode that also says whether the
    mic should publish, whether GOSLO may greet, and whether action monitoring
    is armed.
    """

    SESSION_ONLY_SILENT = "SessionOnlySilent"
    VOICE_ONLY_NO_VIDEO = "VoiceOnlyNoVideo"
    VOICE_VIDEO_NO_ACTION_MONITOR = "VoiceVideoNoActionMonitor"
    FULL_AR_COMPANION = "FullARCompanion"


CAPABILITY_MODE_DEFAULTS: dict[AppCapabilityMode, tuple[VideoTier, DsgMode]] = {
    AppCapabilityMode.SESSION_ONLY_SILENT: (
        VideoTier.VIDEO_OFF,
        DsgMode.DSG_TEXT_ONLY,
    ),
    AppCapabilityMode.VOICE_ONLY_NO_VIDEO: (
        VideoTier.VIDEO_OFF,
        DsgMode.DSG_TEXT_ONLY,
    ),
    AppCapabilityMode.VOICE_VIDEO_NO_ACTION_MONITOR: (
        VideoTier.VIDEO_GEMINI_ONLY,
        DsgMode.DSG_GEMINI_VISION,
    ),
    AppCapabilityMode.FULL_AR_COMPANION: (
        VideoTier.VIDEO_FULL,
        DsgMode.DSG_FULL,
    ),
}


ALLOWED_COMBOS: frozenset[tuple[VideoTier, DsgMode]] = frozenset(
    {
        (VideoTier.VIDEO_OFF, DsgMode.DSG_TEXT_ONLY),
        (VideoTier.VIDEO_GEMINI_ONLY, DsgMode.DSG_GEMINI_VISION),
        (VideoTier.VIDEO_FULL, DsgMode.DSG_FULL),
        (VideoTier.VIDEO_FULL, DsgMode.DSG_GEMINI_VISION),
        (VideoTier.VIDEO_BURST, DsgMode.DSG_FULL),
    }
)

DEFAULT_COMBO: tuple[VideoTier, DsgMode] = (
    VideoTier.VIDEO_GEMINI_ONLY,
    DsgMode.DSG_GEMINI_VISION,
)


def is_allowed_combo(video_tier: VideoTier, dsg_mode: DsgMode) -> bool:
    """True iff (video_tier, dsg_mode) appears in the whitelist."""
    return (video_tier, dsg_mode) in ALLOWED_COMBOS


class IllegalCombinationError(ValueError):
    """Raised when a (VideoTier, DsgMode) pair is not in ALLOWED_COMBOS."""


def validate_combo(video_tier: VideoTier, dsg_mode: DsgMode) -> None:
    """Raise IllegalCombinationError on illegal pair; otherwise return None."""
    if not is_allowed_combo(video_tier, dsg_mode):
        raise IllegalCombinationError(
            f"({video_tier.value}, {dsg_mode.value}) is not in ALLOWED_COMBOS. "
            f"See ar_feature_vision.md section 3.6 for the legal matrix."
        )


__all__ = [
    "ALLOWED_COMBOS",
    "AppCapabilityMode",
    "CAPABILITY_MODE_DEFAULTS",
    "DEFAULT_COMBO",
    "DsgMode",
    "IllegalCombinationError",
    "VideoTier",
    "is_allowed_combo",
    "validate_combo",
]
