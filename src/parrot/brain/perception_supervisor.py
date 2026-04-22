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
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.tiers import DEFAULT_COMBO, DsgMode, VideoTier, is_allowed_combo

if TYPE_CHECKING:
    import py_trees
    from livekit.agents import AgentSession
    from livekit.rtc import Room

logger = logging.getLogger(__name__)

_WRITER = "brain.perception_supervisor"


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

    async def _control_loop(self) -> None:
        """Decision loop — implemented in T2 (see sprint2_plan §6)."""
        logger.debug("Supervisor loop placeholder (T2 implements the decision tick)")
        while True:
            await asyncio.sleep(1.0)

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
