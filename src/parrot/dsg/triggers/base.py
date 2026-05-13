"""Base trigger class for DSG background enrichment.

All triggers follow the same lifecycle:
  1. init(l2b_graph): keep a read/query handle to the working memory graph.
  2. on_startup(): optional one-time initialization.
  3. on_tick(): periodic execution called by TriggerRunner.
  4. on_event(event): react to a specific Redis/operator event.
  5. return TriggerOutcome: route side effects through TriggerRunner.

DSG-TRIGGER-V2 (2026-05-06):
  TriggerOutcome supersedes TriggerResult (alias kept for back-compat).
  New upload-channel fields (commit_observations / bucket_ops /
  archive_request / staged_refs / plan_request) let triggers participate in
  the GOSLO runtime without bypassing L1.5 Pool or IngestRunner.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from parrot.brain.intent_workspace import StagedRefRequest
    from parrot.brain.plan import PlanProposal
    from parrot.dsg.archive.conversation import ArchiveRequest
    from parrot.dsg.ingest.base import Observation
    from parrot.dsg.l1_5.buckets import BucketOp
    from parrot.dsg.l2b_graph import L2BGraph

logger = logging.getLogger(__name__)


class TriggerKind(str, Enum):
    STARTUP = "startup"
    PERIODIC = "periodic"
    EVENT_DRIVEN = "event_driven"
    ON_DEMAND = "on_demand"


@dataclass
class TriggerOutcome:
    """What a trigger produced.

    Legacy 7 fields (Phase 4) reach the Brain Context Injector +
    Scheduler / Nanobot path unchanged. New 5 fields (DSG-TRIGGER-V2)
    flow into L1.5 Pool / IntentWorkspace / Plan / Archive subsystems.

    See dsg_protocol_trigger_v2_20260506.md section 2 for the contract.
    """

    # Legacy 7 (Phase 4).
    trigger_name: str = ""
    summary: str = ""
    nodes_affected: list[str] = field(default_factory=list)
    dispatch_to_nanobot: bool = False
    nanobot_task: dict[str, Any] | None = None
    notify_gemini: bool = False
    notification_text: str = ""

    # DSG-TRIGGER-V2 upload channels.
    commit_observations: tuple["Observation", ...] = ()
    bucket_ops: tuple["BucketOp", ...] = ()
    archive_request: "ArchiveRequest | None" = None
    staged_refs: tuple["StagedRefRequest", ...] = ()
    plan_request: "PlanProposal | None" = None


# Back-compat alias. New trigger code should use TriggerOutcome directly.
TriggerResult = TriggerOutcome


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
    async def on_startup(self) -> TriggerOutcome | None:
        """Called once when the Brain Agent starts. Return None to skip."""
        ...

    @abstractmethod
    async def on_tick(self) -> TriggerOutcome | None:
        """Called periodically (interval_seconds). Return None if nothing to do."""
        ...

    @abstractmethod
    async def on_event(self, event: dict[str, Any]) -> TriggerOutcome | None:
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
