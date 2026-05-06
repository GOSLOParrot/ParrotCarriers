"""ConversationBoundaryDetector — multi-signal OR boundary detection.

DSG-ARCHIVE-V1 § 2.

Signals (all OR-combined; first to fire triggers the archive):
    AGENT_DISCONNECT  Brain agent shutdown hook
    EPISODE_CLOSE     manage_episode tool close call
    LONG_IDLE         no L1.5 commit / tool call ≥ idle_threshold
    EXPLICIT_END      Brain function tool / Unity explicit signal

When any signal fires the Detector calls
``ConversationArchive.serialize(conv_id)`` and starts a fresh conv_id.
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid as uuid_lib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)


class ConversationBoundary(str, Enum):
    AGENT_DISCONNECT = "agent_disconnect"
    EPISODE_CLOSE = "episode_close"
    LONG_IDLE = "long_idle"
    EXPLICIT_END = "explicit_end"


@dataclass(frozen=True)
class ConversationBoundaryEvent:
    boundary: ConversationBoundary
    conv_id: str
    triggered_at: float
    triggering_actor: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


_DEFAULT_IDLE_THRESHOLD_SECONDS = 1800.0  # 30 min desktop baseline


class ConversationBoundaryDetector:
    """Single-process boundary multiplexer."""

    def __init__(
        self, idle_threshold_seconds: float = _DEFAULT_IDLE_THRESHOLD_SECONDS,
    ) -> None:
        self._idle_threshold = idle_threshold_seconds
        self._listeners: dict[
            ConversationBoundary,
            list[Callable[[ConversationBoundaryEvent], Awaitable[None]]],
        ] = {b: [] for b in ConversationBoundary}
        self._conv_id: str = ""
        self._last_activity_ts: float = 0.0
        self._idle_task: asyncio.Task | None = None
        self._running: bool = False
        self._reset_conv_id()

    # ─── Lifecycle ─────────────────────────────────────────────

    async def start(self) -> None:
        self._running = True
        self._touch_activity()
        if self._idle_task is None or self._idle_task.done():
            try:
                loop = asyncio.get_running_loop()
                self._idle_task = loop.create_task(self._idle_watch_loop())
            except RuntimeError:
                # no running loop → idle detection disabled in this context
                self._idle_task = None

    async def stop(self) -> None:
        self._running = False
        if self._idle_task and not self._idle_task.done():
            self._idle_task.cancel()
            try:
                await self._idle_task
            except (asyncio.CancelledError, Exception):
                pass

    # ─── Listeners ─────────────────────────────────────────────

    def register_listener(
        self,
        boundary: ConversationBoundary,
        listener: Callable[[ConversationBoundaryEvent], Awaitable[None]],
    ) -> None:
        self._listeners[boundary].append(listener)

    async def signal_boundary(self, event: ConversationBoundaryEvent) -> None:
        """Public entry: explicitly signal a boundary."""
        for fn in self._listeners.get(event.boundary, []):
            try:
                await fn(event)
            except Exception:
                logger.exception("boundary listener %s failed", fn)
        # Default behavior: serialize via ConversationArchive
        await self._default_serialize(event)
        # New conv_id after the boundary
        self._reset_conv_id()

    async def _default_serialize(
        self, event: ConversationBoundaryEvent
    ) -> None:
        try:
            from parrot.dsg.archive.conversation import get_conversation_archive
            arch = get_conversation_archive()
            await arch.serialize(event.conv_id)
        except Exception:
            logger.exception("default serialize failed for %s", event.conv_id)

    # ─── State ─────────────────────────────────────────────────

    def current_conv_id(self) -> str:
        return self._conv_id

    def configure_idle_threshold(self, seconds: float) -> None:
        self._idle_threshold = max(1.0, seconds)

    def touch_activity(self) -> None:
        """Public entry — call on every L1.5 commit / tool call to
        reset idle timer. Used by IngestRunner / Brain tools."""
        self._touch_activity()

    def _touch_activity(self) -> None:
        self._last_activity_ts = time.time()

    def _reset_conv_id(self) -> None:
        self._conv_id = f"conv_{int(time.time())}_{uuid_lib.uuid4().hex[:4]}"
        self._last_activity_ts = time.time()

    async def _idle_watch_loop(self) -> None:
        try:
            while self._running:
                await asyncio.sleep(self._idle_threshold / 4 if self._idle_threshold > 0 else 1.0)
                if not self._running:
                    break
                if time.time() - self._last_activity_ts >= self._idle_threshold:
                    await self.signal_boundary(ConversationBoundaryEvent(
                        boundary=ConversationBoundary.LONG_IDLE,
                        conv_id=self._conv_id,
                        triggered_at=time.time(),
                        triggering_actor="idle_watch_loop",
                    ))
        except asyncio.CancelledError:
            pass


# ─── Singleton + test injection ──────────────────────────────────

_detector: ConversationBoundaryDetector | None = None


def get_boundary_detector() -> ConversationBoundaryDetector:
    global _detector
    if _detector is None:
        _detector = ConversationBoundaryDetector()
    return _detector


def set_boundary_detector_for_test(
    detector: ConversationBoundaryDetector | None,
) -> None:
    global _detector
    _detector = detector


__all__ = [
    "ConversationBoundary",
    "ConversationBoundaryDetector",
    "ConversationBoundaryEvent",
    "get_boundary_detector",
    "set_boundary_detector_for_test",
]
