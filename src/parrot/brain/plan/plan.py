"""Plan / PlanStep / PlanProposal dataclasses.

BRAIN-PLAN-V1 § 2.

A Plan is GOSLO's structured action plan for a single complex Intent.
It lives primarily in IntentWorkspace (StagedRefKind.PLAN) and is
mirrored to L2-B by reusing ``NodeKind.EVENT`` + ``source_meta.plan_role``
(Phase 4 § 8 L1 NodeKind enum is locked — never extend it for Plan).
"""

from __future__ import annotations

import time
import uuid as uuid_lib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PlanState(str, Enum):
    DRAFT = "draft"
    AWAITING_USER_CONFIRMATION = "awaiting_user_confirmation"
    APPROVED = "approved"
    EXECUTING = "executing"
    PARTIAL_COMPLETE = "partial_complete"
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVISED = "revised"


class PlanStepState(str, Enum):
    PENDING = "pending"
    DISPATCHED = "dispatched"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class PlanStepProposal:
    step_id: str
    title: str
    expected_tool: str = ""
    inputs: dict[str, Any] = field(default_factory=dict)
    depends_on: tuple[str, ...] = ()


@dataclass(frozen=True)
class PlanProposal:
    """TriggerOutcome upload-channel payload (DSG-TRIGGER-V2 § 3.4)."""

    proposed_by: str
    title: str
    rationale: str = ""
    suggested_steps: tuple[PlanStepProposal, ...] = ()
    suggested_intent_event_kind: str = ""
    related_node_uuids: tuple[str, ...] = ()
    related_staged_ref_ids: tuple[str, ...] = ()
    estimated_duration_s: float = 0.0
    blocks_conversation: bool = False


@dataclass
class PlanStep:
    step_id: str = field(default_factory=lambda: uuid_lib.uuid4().hex[:8])
    title: str = ""
    description: str = ""
    expected_tool: str = ""
    inputs: dict[str, Any] = field(default_factory=dict)
    depends_on: tuple[str, ...] = ()
    state: PlanStepState = PlanStepState.PENDING
    nanobot_task_id: str = ""
    started_at: float = 0.0
    completed_at: float = 0.0
    result_summary: str = ""
    result_ref_id: str = ""
    error: str = ""

    def is_terminal(self) -> bool:
        return self.state in (
            PlanStepState.DONE,
            PlanStepState.FAILED,
            PlanStepState.SKIPPED,
        )


@dataclass
class Plan:
    plan_id: str = field(default_factory=lambda: uuid_lib.uuid4().hex[:12])
    title: str = ""
    rationale: str = ""

    drafted_at: float = field(default_factory=time.time)
    approved_at: float = 0.0
    started_executing_at: float = 0.0
    completed_at: float = 0.0

    state: PlanState = PlanState.DRAFT

    intent_event_id: str = ""
    episode_id: str = ""
    related_node_uuids: tuple[str, ...] = ()
    related_staged_ref_ids: tuple[str, ...] = ()

    blocks_conversation: bool = True
    estimated_duration_s: float = 0.0

    steps: list[PlanStep] = field(default_factory=list)

    superseded_by: str = ""
    supersedes: str = ""

    staged_ref_id: str = ""
    blackboard_namespace: str = ""

    def step_by_id(self, step_id: str) -> PlanStep | None:
        for s in self.steps:
            if s.step_id == step_id:
                return s
        return None

    def all_steps_terminal(self) -> bool:
        return bool(self.steps) and all(s.is_terminal() for s in self.steps)

    def any_step_failed(self) -> bool:
        return any(s.state == PlanStepState.FAILED for s in self.steps)

    def all_steps_done(self) -> bool:
        return bool(self.steps) and all(s.state == PlanStepState.DONE for s in self.steps)

    def ready_steps(self) -> list[PlanStep]:
        """Return steps with state=PENDING whose dependencies are all DONE."""
        out: list[PlanStep] = []
        for s in self.steps:
            if s.state != PlanStepState.PENDING:
                continue
            if all(
                (dep := self.step_by_id(d)) is not None
                and dep.state == PlanStepState.DONE
                for d in s.depends_on
            ) or not s.depends_on:
                out.append(s)
        return out


__all__ = [
    "Plan",
    "PlanProposal",
    "PlanState",
    "PlanStep",
    "PlanStepProposal",
    "PlanStepState",
]
