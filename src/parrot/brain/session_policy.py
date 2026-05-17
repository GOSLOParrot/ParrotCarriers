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
_GOSLO_PLACED_KEY = "session/goslo_placed"
_FIRST_GREETING_SENT_KEY = "session/first_greeting_sent"
_PRE_PLACEMENT_REPLY_REASONS = {
    "onGosloPlaced",
}


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
    """Parse wire/UI value into :class:`AppCapabilityMode` with safe fallback.

    FIX (2026-05-11 audit Round 4, Bug J): when ``raw`` is a *non-empty*
    string that doesn't match any enum value, log a warning instead of
    silently falling back to FULL_AR_COMPANION. Verified empirically
    (audit Round 4 §J): ``apply_capability_mode("totally_bogus_mode")``
    used to silently set FullARCompanion. Empty / None input still falls
    through quietly because that's the legitimate "no preference" case.
    """
    if isinstance(raw, AppCapabilityMode):
        return raw
    text = str(raw or "").strip()
    for mode in AppCapabilityMode:
        if text == mode.value or text.upper() == mode.name:
            return mode
    if text:
        logger.warning(
            "session_policy: unknown capability mode %r; falling back to %s "
            "(accepted: %s)",
            text,
            AppCapabilityMode.FULL_AR_COMPANION.value,
            sorted(m.value for m in AppCapabilityMode),
        )
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


def _write_session_policy_key(key: str, value: Any, source: str) -> None:
    try:
        bb = open_bb_client(name=f"session_policy.{source or 'write'}", writer=_WRITER)
        bb.set(key, value)
        try:
            from parrot.brain.bb_watchers import fire_watcher

            fire_watcher(key, value)
        except Exception:
            logger.debug(
                "session_policy: watcher fan-out skipped for %s",
                key,
                exc_info=True,
            )
    except Exception:
        logger.exception("session_policy: failed to write %s", key)


def set_goslo_placed(placed: bool, source: str = "") -> None:
    """Record whether AR placement is complete for proactive speech gates."""
    _write_session_policy_key(_GOSLO_PLACED_KEY, bool(placed), source or "placement")


def is_goslo_placed(default: bool = False) -> bool:
    """Read the AR placement gate for this LiveKit session."""
    try:
        bb = open_bb_client(name="session_policy.placement.read", writer=None)
        return bool(bb.get(_GOSLO_PLACED_KEY))
    except Exception:
        return default


def set_first_greeting_sent(sent: bool, source: str = "") -> None:
    """Record whether the placement-gated first greeting has already fired."""
    _write_session_policy_key(
        _FIRST_GREETING_SENT_KEY,
        bool(sent),
        source or "first_greeting",
    )


def first_greeting_sent(default: bool = False) -> bool:
    """Read the first-greeting dedupe flag for this LiveKit session."""
    try:
        bb = open_bb_client(name="session_policy.first_greeting.read", writer=None)
        return bool(bb.get(_FIRST_GREETING_SENT_KEY))
    except Exception:
        return default


def _allows_pre_placement_reply(reason: str) -> bool:
    text = str(reason or "").strip()
    if text in _PRE_PLACEMENT_REPLY_REASONS:
        return True
    return text.startswith("safety.")


def should_generate_reply(reason: str = "") -> bool:
    """Central gate for server-initiated speech.

    reason: SessionOnlySilent keeps the LiveKit room alive for 2DWorkspace,
    heartbeats, and menu traffic, but it must suppress greetings, scheduler
    reports, trigger notifications, and other proactive ``generate_reply``
    calls. Before Unity confirms AR placement, the same central gate keeps C4
    injections and background task notices quiet so the LiveKit connection
    itself cannot steal the first turn. User audio is blocked on Unity as a
    separate media gate.
    """
    if is_silent_session():
        logger.info("session_policy: suppress generate_reply (%s)", reason or "silent")
        return False
    if not _allows_pre_placement_reply(reason) and not is_goslo_placed():
        logger.info(
            "session_policy: suppress generate_reply before placement (%s)",
            reason or "pre_placement",
        )
        return False
    return True


def should_stage_context_notice(reason: str = "") -> bool:
    """Gate non-speaking C3 / IntentWorkspace notices.

    Placement is a speech boundary, not a memory boundary: pre-placement visual
    evidence and state hints may still be staged quietly so GOSLO can use them
    on a later user turn. SessionOnlySilent remains stricter and suppresses
    model-facing notices as well as speech.
    """
    if is_silent_session():
        logger.info(
            "session_policy: suppress context notice (%s)",
            reason or "silent",
        )
        return False
    return True


__all__ = [
    "SessionCapabilityProfile",
    "apply_capability_mode",
    "current_capability_mode",
    "first_greeting_sent",
    "is_goslo_placed",
    "is_silent_session",
    "parse_capability_mode",
    "profile_for_mode",
    "set_first_greeting_sent",
    "set_goslo_placed",
    "should_generate_reply",
    "should_stage_context_notice",
]
