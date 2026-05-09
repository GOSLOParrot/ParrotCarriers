"""Session policy interface for app capability modes.

The app has four user-visible capability modes that sit above the lower-level
``VideoTier`` x ``DsgMode`` matrix. This module writes the session policy BB
key and returns the derived tier/mode profile for Unity or Brain callers.

reason: Existing tier enums cannot express "keep room connected but do not
publish microphone or greet yet". A session policy keeps that UX decision out
of LiveKit teardown code and avoids overloading ``VideoTier`` with voice
semantics.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.tiers import (
    AppCapabilityMode,
    CAPABILITY_MODE_DEFAULTS,
    DsgMode,
    VideoTier,
)

logger = logging.getLogger(__name__)

_WRITER = "brain.session_policy"


@dataclass(frozen=True)
class SessionCapabilityProfile:
    """Derived behavior for one app capability mode."""

    mode: AppCapabilityMode
    video_tier: VideoTier
    dsg_mode: DsgMode
    microphone_enabled: bool
    video_enabled: bool
    action_monitor_enabled: bool
    greet_after_ar_placement: bool
    keep_livekit_connected: bool = True

    def as_json(self) -> dict[str, Any]:
        return {
            "mode": self.mode.value,
            "video_tier": self.video_tier.name,
            "dsg_mode": self.dsg_mode.name,
            "microphone_enabled": self.microphone_enabled,
            "video_enabled": self.video_enabled,
            "action_monitor_enabled": self.action_monitor_enabled,
            "greet_after_ar_placement": self.greet_after_ar_placement,
            "keep_livekit_connected": self.keep_livekit_connected,
        }


def parse_capability_mode(raw: str | AppCapabilityMode | None) -> AppCapabilityMode:
    """Parse wire/UI value into :class:`AppCapabilityMode` with safe fallback."""
    if isinstance(raw, AppCapabilityMode):
        return raw
    text = str(raw or "").strip()
    for mode in AppCapabilityMode:
        if text == mode.value or text.upper() == mode.name:
            return mode
    return AppCapabilityMode.FULL_AR_COMPANION


def profile_for_mode(raw: str | AppCapabilityMode | None) -> SessionCapabilityProfile:
    """Return the derived profile for a user-visible capability mode."""
    mode = parse_capability_mode(raw)
    video_tier, dsg_mode = CAPABILITY_MODE_DEFAULTS[mode]
    return SessionCapabilityProfile(
        mode=mode,
        video_tier=video_tier,
        dsg_mode=dsg_mode,
        microphone_enabled=mode
        in {
            AppCapabilityMode.VOICE_ONLY_NO_VIDEO,
            AppCapabilityMode.VOICE_VIDEO_NO_ACTION_MONITOR,
            AppCapabilityMode.FULL_AR_COMPANION,
        },
        video_enabled=video_tier != VideoTier.VIDEO_OFF,
        action_monitor_enabled=mode == AppCapabilityMode.FULL_AR_COMPANION,
        greet_after_ar_placement=mode != AppCapabilityMode.SESSION_ONLY_SILENT,
    )


def apply_capability_mode(raw: str | AppCapabilityMode | None) -> SessionCapabilityProfile:
    """Write ``session/app_capability_mode`` and return the derived profile.

    This intentionally does not push a Unity ``setVideoTier`` RPC. Visible
    media changes still flow through the existing Supervisor/RPC path; this
    key records the session UX policy so startup and menu code can coordinate
    mic/video/greeting gates without destroying the room.
    """
    profile = profile_for_mode(raw)
    try:
        bb = open_bb_client(name="session_policy.apply", writer=_WRITER)
        bb.set("session/app_capability_mode", profile.mode)
        try:
            from parrot.brain.bb_watchers import fire_watcher

            fire_watcher("session/app_capability_mode", profile.mode)
        except Exception:
            logger.debug("session_policy: watcher fan-out skipped", exc_info=True)
    except Exception:
        logger.exception("session_policy: failed to write session/app_capability_mode")
    return profile


def current_capability_mode(
    default: AppCapabilityMode | None = AppCapabilityMode.FULL_AR_COMPANION,
) -> AppCapabilityMode | None:
    """Read the current app capability mode from the Blackboard.

    The helper is intentionally read-only. It lets speech gates, trigger
    runners, and the PerceptionSupervisor make the same policy decision
    without sharing LiveKit transport details.
    """
    try:
        bb = open_bb_client(name="session_policy.read", writer=None)
        return parse_capability_mode(bb.get("session/app_capability_mode"))
    except Exception:
        return default


def is_silent_session() -> bool:
    """True when the room should stay connected but GOSLO must not speak."""
    return current_capability_mode() == AppCapabilityMode.SESSION_ONLY_SILENT


def should_generate_reply(reason: str = "") -> bool:
    """Central gate for server-initiated speech.

    reason: SessionOnlySilent keeps the LiveKit room alive for 2DWorkspace,
    heartbeats, and menu traffic, but it must suppress greetings, scheduler
    reports, trigger notifications, and other proactive ``generate_reply``
    calls. User audio is blocked on Unity as a separate media gate.
    """
    if is_silent_session():
        logger.info("session_policy: suppress generate_reply (%s)", reason or "silent")
        return False
    return True


__all__ = [
    "SessionCapabilityProfile",
    "apply_capability_mode",
    "current_capability_mode",
    "is_silent_session",
    "parse_capability_mode",
    "profile_for_mode",
    "should_generate_reply",
]
