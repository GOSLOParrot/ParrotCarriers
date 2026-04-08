"""E1: SimpleRouter — Phase 1 scheduler implementation.

Simple priority-based if-else routing. Routes incoming events/tasks
to the appropriate handler (Brain direct execution, or Nanobot dispatch).
"""

from __future__ import annotations

import json
import logging
from typing import Any

from parrot.shared.constants import STREAM_NANOBOT_DISPATCH
from parrot.shared.redis_client import get_redis

logger = logging.getLogger(__name__)


class SimpleRouter:
    """Phase 1 scheduler: routes tasks by priority."""

    async def route(self, task: dict[str, Any]) -> str:
        """Route a task to the appropriate destination.

        Returns the destination identifier.
        """
        task_type = task.get("type", "unknown")
        priority = task.get("priority", "normal")

        if priority == "reflex":
            return await self._handle_reflex(task)
        elif task_type in ("research", "memory_consolidation", "vocabulary_learn"):
            return await self._dispatch_to_nanobot(task)
        else:
            return "brain_direct"

    async def _handle_reflex(self, task: dict) -> str:
        """Reflex tasks bypass LLM — direct to Unity via RPC."""
        logger.info("Reflex task: %s", task.get("action"))
        return "reflex_direct"

    async def _dispatch_to_nanobot(self, task: dict) -> str:
        """Dispatch async task to Nanobot via Redis Stream."""
        r = await get_redis()
        await r.xadd(STREAM_NANOBOT_DISPATCH, {"payload": json.dumps(task)})
        logger.info("Task dispatched to Nanobot: %s", task.get("type"))
        return "nanobot"
