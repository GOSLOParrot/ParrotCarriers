"""PerceptionSupervisor — Sprint 2 autonomous Intent-layer controller.

Purpose (from `ar_feature_vision.md §3.5` / `sprint2_plan_20260423.md §3`):
    Close the loop from perception → autonomous action. Supervisor watches
    `session/visual_state` and external A10 health, and decides when to
    downgrade/upgrade the (video_tier × dsg_mode) combo. All decisions go
    straight to Blackboard; Context Injector picks up the change via its
    BB poll loop and notifies Gemini through C3 (or C2 when crossing tier
    boundaries that require an instructions rebuild).

Split of concerns with sibling modules:

    brain.vision.state       — stateless *fusion* (visual_reason + AR → VisualState)
    brain.perception_supervisor — stateful *hysteresis* + A10 health + decision
    brain.context_injector   — push-to-Gemini surface (reads BB, does NOT decide)

Sprint 2 scope (T1 skeleton): class shell, DEFAULT_COMBO startup write,
attach helper. Decision loop (T2) and L0/obs audit (T4) land in follow-up
commits — see `sprint2_plan_20260423.md §6`.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from parrot.brain.obs_log import log_obs_event
from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.constants import STREAM_EVENT_LOG
from parrot.shared.event_log import EventEnvelope, EventLayer
from parrot.shared.tiers import DEFAULT_COMBO, DsgMode, VideoTier, is_allowed_combo
from parrot.shared.vision_state import VisualState

if TYPE_CHECKING:
    import py_trees
    from livekit.agents import AgentSession
    from livekit.rtc import Room

logger = logging.getLogger(__name__)

_WRITER = "brain.perception_supervisor"

# Hysteresis windows (seconds). Kept as module-level so tests / ops can tune
# without touching the decision function signature.
VISUAL_DEGRADE_GRACE_S = 15.0
A10_DOWN_GRACE_S = 30.0
A10_UP_STABLE_S = 60.0
MANUAL_OVERRIDE_HOLD_S = 300.0

# A10 health probe cadence (seconds). Fast enough to notice a down within
# one hysteresis window, slow enough to not flood the network.
A10_PROBE_INTERVAL_S = 10.0

# Decision loop cadence (seconds). Matches Injector's 1 Hz poll so changes
# propagate within 1-2 ticks.
LOOP_INTERVAL_S = 1.0


@dataclass
class HysteresisState:
    """Time-window state held in Python, NOT on Blackboard.

    Lives inside Supervisor to keep the fusion layer (`brain.vision.state`)
    a pure function. Every tick of the decision loop updates this dataclass
    in place; the decision function reads it to judge whether enough time
    has passed in a given condition to warrant a tier flip.
    """

    degraded_since: float = 0.0
    a10_down_since: float = 0.0
    a10_up_since: float = 0.0
    last_transition_at: float = 0.0
    manual_override_until: float = 0.0

    def reset_degrade(self) -> None:
        self.degraded_since = 0.0

    def reset_a10_down(self) -> None:
        self.a10_down_since = 0.0

    def reset_a10_up(self) -> None:
        self.a10_up_since = 0.0


class PerceptionSupervisor:
    """Autonomous controller for (video_tier, dsg_mode) BB writes.

    Attach once per session via `attach_perception_supervisor(session, room)`.
    Supervisor owns writes to:
        session/video_tier        — VideoTier enum
        session/dsg_mode          — DsgMode enum

    Reads (every loop tick):
        session/visual_state      — from brain.vision.state
        external A10 health probe — Sprint 2 uses a stub (env-configurable URL);
                                    real endpoint lands in Sprint 3 A10 rollout.

    State kept in Python (NOT on BB):
        _hysteresis               — HysteresisState timers
        _current                  — local mirror of last written combo
    """

    def __init__(self) -> None:
        self._bb: "py_trees.blackboard.Client" = open_bb_client(
            name="perception_supervisor", writer=_WRITER
        )
        self._hysteresis = HysteresisState()
        self._current: tuple[VideoTier, DsgMode] = DEFAULT_COMBO
        self._loop_task: asyncio.Task | None = None
        self._a10_stub_force_healthy: bool | None = None
        self._session: "AgentSession | None" = None

    def _write_combo(
        self,
        combo: tuple[VideoTier, DsgMode],
        *,
        cause: str = "init",
    ) -> bool:
        """Commit a new combo to BB. Returns True iff anything changed.

        Sprint 2 T1 covers the startup write only; decision-driven calls
        land in T2 once `_control_loop` is implemented.
        """
        if not is_allowed_combo(*combo):
            logger.warning(
                "Supervisor refused illegal combo %s (cause=%s)", combo, cause
            )
            return False

        video_tier, dsg_mode = combo
        changed = False
        try:
            current_tier = self._bb.get("session/video_tier")
        except KeyError:
            current_tier = None
        try:
            current_mode = self._bb.get("session/dsg_mode")
        except KeyError:
            current_mode = None

        if current_tier != video_tier:
            self._bb.set("session/video_tier", video_tier)
            changed = True
        if current_mode != dsg_mode:
            self._bb.set("session/dsg_mode", dsg_mode)
            changed = True

        if changed:
            self._current = combo
            self._hysteresis.last_transition_at = time.time()
            logger.info(
                "Supervisor BB write: video_tier=%s dsg_mode=%s (cause=%s)",
                video_tier.value, dsg_mode.value, cause,
            )
        return changed

    def initialize(self) -> None:
        """Write the DEFAULT_COMBO to BB so downstream readers see a valid
        baseline even before the first decision tick. Idempotent."""
        self._write_combo(DEFAULT_COMBO, cause="startup")

    def set_manual_override(self, combo: tuple[VideoTier, DsgMode], hold_s: float = 300.0) -> bool:
        """Record a user-initiated tier switch. Returns True if accepted.

        Blocks Supervisor auto-decisions for `hold_s` seconds so the user's
        intent doesn't get overridden by a 30-second hysteresis window.
        """
        if not self._write_combo(combo, cause="manual_override"):
            return False
        self._hysteresis.manual_override_until = time.time() + hold_s
        logger.info(
            "Supervisor manual override: combo=%s hold=%.0fs",
            combo, hold_s,
        )
        return True

    def start_background(self) -> None:
        """Kick off the async decision loop. Safe to call multiple times
        (re-invocations are no-ops while the previous task is alive)."""
        if self._loop_task is not None and not self._loop_task.done():
            return
        self._loop_task = asyncio.create_task(self._control_loop())

    # ─────────────────────── A10 health probe ────────────────────────

    async def _check_a10_health(self) -> bool:
        """Sprint 2 stub: env `PARROT_A10_HEALTH_URL` decides behaviour.

        - If unset → returns True (treat as healthy so Supervisor stays on
          VIDEO_FULL+DSG_FULL when operators have not opted in to hysteresis).
          This is the "dev convenience" default; prod should always set the
          env.
        - If set to `stub:healthy` / `stub:unhealthy` → return that literal
          for offline tests.
        - Otherwise → HTTP GET the URL with a 2s timeout, return True on any
          2xx. We use `aiohttp` if available, else urlopen in a thread to
          avoid another import dep during Sprint 2.
        """
        # Test/force hook takes precedence (used by unit tests and the manual
        # `set_manual_override` path doesn't reach here at all).
        if self._a10_stub_force_healthy is not None:
            return self._a10_stub_force_healthy

        url = os.getenv("PARROT_A10_HEALTH_URL", "").strip()
        if not url:
            return True
        if url.startswith("stub:"):
            return url == "stub:healthy"

        try:
            import aiohttp  # type: ignore
        except ImportError:
            aiohttp = None

        try:
            if aiohttp is not None:
                timeout = aiohttp.ClientTimeout(total=2.0)
                async with aiohttp.ClientSession(timeout=timeout) as s:
                    async with s.get(url) as resp:
                        return 200 <= resp.status < 300
            else:
                import urllib.request

                def _probe() -> bool:
                    try:
                        with urllib.request.urlopen(url, timeout=2.0) as r:
                            return 200 <= r.status < 300
                    except Exception:
                        return False

                return await asyncio.to_thread(_probe)
        except Exception:
            logger.debug("A10 health probe failed at %s", url, exc_info=True)
            return False

    # ─────────────────────── Pure decision function ──────────────────────

    @staticmethod
    def decide(
        *,
        visual_state: VisualState | None,
        a10_healthy: bool,
        now: float,
        hysteresis: HysteresisState,
        current: tuple[VideoTier, DsgMode],
    ) -> tuple[tuple[VideoTier, DsgMode] | None, str]:
        """Pure decision: given observations + timers, return (new_combo | None, cause).

        Returns `(None, "...")` when no change is warranted; otherwise returns
        the new combo plus a short cause string (used for audit + Injector
        message hints).

        Policy (sprint2_plan §4):
            - Manual override (hold_until in future) → keep current, cause="manual_hold"
            - A10 down ≥ GRACE + currently on FULL → step down to
              (VIDEO_GEMINI_ONLY, DSG_GEMINI_VISION)
            - A10 up ≥ STABLE + currently on degraded combo → step up to
              (VIDEO_FULL, DSG_FULL)
            - Visual DEGRADED long-term + currently on FULL → step down to
              (VIDEO_GEMINI_ONLY, DSG_GEMINI_VISION); treat as "video tier
              downgrade" only (dsg_mode follows the tier floor).
        """
        video_tier, dsg_mode = current

        if now < hysteresis.manual_override_until:
            return None, "manual_hold"

        # A10 downgrade wins before upgrade (safety first).
        a10_down_long_enough = (
            not a10_healthy
            and hysteresis.a10_down_since > 0.0
            and (now - hysteresis.a10_down_since) >= A10_DOWN_GRACE_S
        )
        if a10_down_long_enough and video_tier == VideoTier.VIDEO_FULL:
            return (
                (VideoTier.VIDEO_GEMINI_ONLY, DsgMode.DSG_GEMINI_VISION),
                "a10_down_30s",
            )

        # Visual-only downgrade (A10 healthy but camera degraded for long).
        visual_degraded_long = (
            visual_state == VisualState.DEGRADED
            and hysteresis.degraded_since > 0.0
            and (now - hysteresis.degraded_since) >= VISUAL_DEGRADE_GRACE_S
        )
        if visual_degraded_long and video_tier == VideoTier.VIDEO_FULL:
            return (
                (VideoTier.VIDEO_GEMINI_ONLY, DsgMode.DSG_GEMINI_VISION),
                "visual_degraded_15s",
            )

        # Upgrade path: A10 up AND visual acceptable.
        a10_up_long_enough = (
            a10_healthy
            and hysteresis.a10_up_since > 0.0
            and (now - hysteresis.a10_up_since) >= A10_UP_STABLE_S
        )
        visual_acceptable = visual_state in (None, VisualState.ACTIVE)
        if (
            a10_up_long_enough
            and visual_acceptable
            and current != (VideoTier.VIDEO_FULL, DsgMode.DSG_FULL)
            and current != (VideoTier.VIDEO_OFF, DsgMode.DSG_TEXT_ONLY)
        ):
            return (
                (VideoTier.VIDEO_FULL, DsgMode.DSG_FULL),
                "a10_up_60s",
            )

        return None, "steady"

    # ─────────────────────── Hysteresis timer bookkeeping ─────────────

    def _update_timers(
        self,
        visual_state: VisualState | None,
        a10_healthy: bool,
        now: float,
    ) -> None:
        """Advance hysteresis timers based on the latest observation."""
        h = self._hysteresis

        if visual_state == VisualState.DEGRADED:
            if h.degraded_since == 0.0:
                h.degraded_since = now
        else:
            h.reset_degrade()

        if a10_healthy:
            h.reset_a10_down()
            if h.a10_up_since == 0.0:
                h.a10_up_since = now
        else:
            h.reset_a10_up()
            if h.a10_down_since == 0.0:
                h.a10_down_since = now

    # ─────────────────────── Control loop ────────────────────────────

    async def _control_loop(self) -> None:
        """1 Hz: observe → update timers → decide → commit.

        Let the session breathe for a couple of seconds before the first tick
        so `attach_telemetry_receiver` / `attach_video_state_rpc` have time
        to register their BB writes.
        """
        await asyncio.sleep(2.0)

        last_probe_at = 0.0
        a10_healthy = True

        while True:
            try:
                now = time.time()

                if now - last_probe_at >= A10_PROBE_INTERVAL_S:
                    a10_healthy = await self._check_a10_health()
                    last_probe_at = now

                try:
                    visual_state = self._bb.get("session/visual_state")
                except KeyError:
                    visual_state = None

                self._update_timers(visual_state, a10_healthy, now)
                new_combo, cause = self.decide(
                    visual_state=visual_state,
                    a10_healthy=a10_healthy,
                    now=now,
                    hysteresis=self._hysteresis,
                    current=self._current,
                )

                if new_combo is not None and new_combo != self._current:
                    # Capture the OLD state BEFORE _write_combo mutates
                    # self._current. This is the critical ordering fix:
                    # _write_combo sets self._current = combo on success,
                    # so if we pass self._current after the call we get
                    # previous == new, breaking the audit log and the
                    # push_video_tier guard (`if new_tier != prev_tier`).
                    previous_combo = self._current
                    if self._write_combo(new_combo, cause=cause):
                        # self._current is now updated by _write_combo; don't
                        # set it again below.
                        await self._on_decision_committed(
                            previous=previous_combo,
                            new=new_combo,
                            cause=cause,
                        )

            except Exception:
                logger.exception("Supervisor loop hiccup — continuing")
            await asyncio.sleep(LOOP_INTERVAL_S)

    async def _on_decision_committed(
        self,
        *,
        previous: tuple[VideoTier, DsgMode],
        new: tuple[VideoTier, DsgMode],
        cause: str,
    ) -> None:
        """Side-effect hook fired after a successful BB commit.

        Writes the decision to TWO audit surfaces (sprint2_plan §3.3):

          STREAM_EVENT_LOG (L0)  — EventEnvelope layer=INTENT for cross-process
                                   audit + future Reverse Provenance Expansion.
                                   Fire-and-forget; Redis outage does NOT
                                   block the decision loop.
          parrot.obs_log         — `log_obs_event("intent_decision", 2, ...)` for
                                   offline reflection tooling. Layer 2 =
                                   "autonomous action" per ar_feature_vision §3.5.

        Sprint 2 T10 extends this hook to forward a `setVideoTier` RPC to
        Unity; Sprint 3 wires re-publishing track options for real bitrate
        changes.
        """
        prev_tier, prev_mode = previous
        new_tier, new_mode = new

        payload: dict[str, Any] = {
            "from": {"video_tier": prev_tier.value, "dsg_mode": prev_mode.value},
            "to": {"video_tier": new_tier.value, "dsg_mode": new_mode.value},
            "cause": cause,
            "hysteresis": {
                "degraded_since": self._hysteresis.degraded_since,
                "a10_down_since": self._hysteresis.a10_down_since,
                "a10_up_since": self._hysteresis.a10_up_since,
                "manual_override_until": self._hysteresis.manual_override_until,
            },
        }

        try:
            envelope = EventEnvelope(
                kind="intent.tier_change",
                layer=EventLayer.INTENT,
                actor=_WRITER,
                payload=payload,
            )
            await self._xadd_event(envelope)
        except Exception:
            logger.exception("Supervisor: failed to emit L0 EventEnvelope")

        log_obs_event(
            "intent_decision",
            layer=2,
            payload=payload,
            actor=_WRITER,
        )

        if new_tier != prev_tier:
            try:
                from parrot.brain.tools._rpc_bridge import push_video_tier

                # Use .name (uppercase "VIDEO_OFF" / "VIDEO_FULL" etc.) not
                # .value (lowercase). Unity ParseTier() does a switch on the
                # uppercase form — using .value causes every tier push to be
                # silently rejected as "Unknown" on the Unity side.
                ok = await push_video_tier(new_tier.name, reason=cause)
                if not ok:
                    logger.info(
                        "Supervisor: setVideoTier push declined (tier=%s cause=%s) "
                        "— BB already updated, will retry on next transition",
                        new_tier.value, cause,
                    )
            except Exception:
                logger.exception("Supervisor: push_video_tier crashed")

    async def _xadd_event(self, envelope: EventEnvelope) -> None:
        """Push one EventEnvelope to `parrot.events.log`.

        Kept as a thin method so tests can monkeypatch it, and so Sprint 3
        can swap in a batched producer without touching the decision path.
        """
        try:
            from parrot.shared.redis_client import get_redis

            r = await get_redis()
            await r.xadd(
                STREAM_EVENT_LOG,
                envelope.to_xadd_fields(),
                maxlen=10_000,
                approximate=True,
            )
        except Exception:
            logger.debug("Supervisor: xadd to STREAM_EVENT_LOG failed", exc_info=True)

    async def stop(self) -> None:
        if self._loop_task and not self._loop_task.done():
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass


_instance: PerceptionSupervisor | None = None


def attach_perception_supervisor(
    session: "AgentSession",
    room: "Room | None" = None,
) -> PerceptionSupervisor:
    """Create, initialise, and start the PerceptionSupervisor singleton.

    Call this after `attach_context_injector(session)` in `agent.py` so the
    Injector is armed before Supervisor writes its first BB value — that way
    the baseline combo doesn't race the Injector's startup baseline snapshot.
    """
    global _instance
    if _instance is not None:
        return _instance
    _instance = PerceptionSupervisor()
    _instance._session = session
    _instance.initialize()
    _instance.start_background()
    logger.info("perception_supervisor: attached (DEFAULT_COMBO written)")
    del room
    return _instance


def get_perception_supervisor() -> PerceptionSupervisor | None:
    return _instance


__all__ = [
    "HysteresisState",
    "PerceptionSupervisor",
    "attach_perception_supervisor",
    "get_perception_supervisor",
]
