"""Context Injector (B12) — enriches Gemini's system prompt with relevant memories.

Uses session.update_instructions() to silently inject context from:
  - Graphiti memory (user preferences, past conversations)
  - Scene context (from DSG or Blackboard, when available)

Two modes of operation:
  1. Periodic: polls Graphiti every N seconds for relevant context
  2. On-demand: called by DSG triggers or other modules via inject_context()

The injector appends a [CONTEXT] block to the base instructions without
triggering Gemini to speak (unlike generate_reply).
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from livekit.agents import AgentSession

from parrot.brain.soul import get_instructions
from parrot.shared.parrot_actions import BehaviorMode
from parrot.shared.redis_client import get_redis

logger = logging.getLogger(__name__)

_POLL_INTERVAL_S = 60.0


class ContextInjector:
    """Manages context injection into the Brain's system prompt."""

    def __init__(self, session: AgentSession):
        self._session = session
        self._scene_context: str = ""
        self._memory_context: str = ""
        self._mode = BehaviorMode.BASE | BehaviorMode.COMPANION
        self._task: asyncio.Task | None = None

    def set_mode(self, mode: BehaviorMode) -> None:
        """Update the active BehaviorMode. Called by mode_watcher on switch."""
        self._mode = mode

    def _rebuild_instructions(self) -> str:
        base = get_instructions(self._mode)
        parts = [base]

        if self._memory_context:
            parts.append(
                f"\n[MEMORY CONTEXT]\n{self._memory_context}\n[/MEMORY CONTEXT]"
            )

        if self._scene_context:
            parts.append(
                f"\n[SCENE CONTEXT]\n{self._scene_context}\n[/SCENE CONTEXT]"
            )

        return "\n".join(parts)

    async def inject_memory(self, query: str = "recent important facts") -> None:
        """Pull relevant memories from Graphiti and inject into instructions."""
        try:
            from parrot.memory.graphiti_client import PARTITIONS, get_graphiti

            g = await get_graphiti()
            results = await g.search(
                query=query,
                group_ids=[PARTITIONS.GOSLO, PARTITIONS.USER],
                num_results=5,
            )

            if results:
                lines = []
                for r in results:
                    fact = getattr(r, "fact", None) or getattr(r, "text", str(r))
                    lines.append(f"- {fact}")
                self._memory_context = "\n".join(lines)
            else:
                self._memory_context = ""

            self._session.update_instructions(self._rebuild_instructions())
            logger.debug("context_injector: memory context updated (%d items)", len(results))
        except Exception:
            logger.debug("context_injector: memory injection skipped")

    async def inject_scene(self, scene_summary: str) -> None:
        """Inject scene context (from DSG triggers or simulation)."""
        self._scene_context = scene_summary
        self._session.update_instructions(self._rebuild_instructions())
        logger.debug("context_injector: scene context updated")

    async def inject_notification(self, message: str) -> None:
        """Push an active notification — makes Gemini speak about it."""
        await self._session.generate_reply(instructions=message)

    async def _periodic_poll(self) -> None:
        """Background task: periodically refresh memory context."""
        await asyncio.sleep(5.0)
        while True:
            try:
                await self.inject_memory()
            except Exception:
                logger.debug("context_injector: periodic poll error")
            await asyncio.sleep(_POLL_INTERVAL_S)

    def start_background(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._periodic_poll())

    async def stop(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass


_injector: ContextInjector | None = None


def attach_context_injector(session: AgentSession) -> ContextInjector:
    """Create and attach a ContextInjector to the Brain session."""
    global _injector
    _injector = ContextInjector(session)
    _injector.start_background()
    logger.info("context_injector: attached to Brain session")
    return _injector


def get_context_injector() -> ContextInjector | None:
    """Get the active ContextInjector (if Brain is running)."""
    return _injector
