"""Base trigger class for DSG background enrichment.

All triggers follow the same lifecycle:
  1. init(l2b_graph) — store reference to the working memory graph
  2. on_startup() — optional one-time initialization
  3. on_tick() — periodic execution (called by trigger runner)
  4. on_event(event) — react to a specific event
  5. results → either mutate L2-B graph directly, or dispatch to Nanobot
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from parrot.dsg.l2b_graph import L2BGraph

logger = logging.getLogger(__name__)


class TriggerKind(str, Enum):
    STARTUP = "startup"
    PERIODIC = "periodic"
    EVENT_DRIVEN = "event_driven"
    ON_DEMAND = "on_demand"


@dataclass
class TriggerResult:
    """What a trigger produced — for reporting to Gemini via Context Injector."""
    trigger_name: str = ""
    summary: str = ""
    nodes_affected: list[str] = field(default_factory=list)
    dispatch_to_nanobot: bool = False
    nanobot_task: dict[str, Any] | None = None
    notify_gemini: bool = False
    notification_text: str = ""


class BaseTrigger(ABC):
    """Abstract base for all DSG triggers."""

    name: str = "base_trigger"
    kinds: list[TriggerKind] = []
    interval_seconds: float = 0

    def __init__(self, graph: L2BGraph) -> None:
        self._graph = graph
        self._last_run: float = 0.0
        self._run_count: int = 0

    @abstractmethod
    async def on_startup(self) -> TriggerResult | None:
        """Called once when the Brain Agent starts. Return None to skip."""
        ...

    @abstractmethod
    async def on_tick(self) -> TriggerResult | None:
        """Called periodically (interval_seconds). Return None if nothing to do."""
        ...

    @abstractmethod
    async def on_event(self, event: dict[str, Any]) -> TriggerResult | None:
        """Called when a relevant event occurs. Return None if not interested."""
        ...

    async def _dispatch_nanobot(self, task_type: str, params: dict) -> str | None:
        """Helper: dispatch a task to Nanobot via Scheduler."""
        try:
            from parrot.brain.tools.dispatch_task import do_dispatch_task
            task_id = await do_dispatch_task(task_type, params, priority="normal")
            logger.info("%s: dispatched nanobot task %s", self.name, task_id)
            return task_id
        except Exception:
            logger.exception("%s: nanobot dispatch failed", self.name)
            return None

    async def _notify_brain(self, message: str) -> None:
        """Helper: push a notification to Context Injector → Gemini."""
        try:
            from parrot.brain.context_injector import get_context_injector
            injector = get_context_injector()
            if injector:
                await injector.inject_notification(message)
        except Exception:
            logger.debug("%s: notification failed", self.name)
