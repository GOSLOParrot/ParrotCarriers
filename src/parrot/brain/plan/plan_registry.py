"""PlanRegistry — central Plan management.

BRAIN-PLAN-V1 § 5.

Responsibilities:
    - draft / submit / approve / start_executing / report_step / cancel / revise
    - stage Plan in IntentWorkspace (kind=PLAN)
    - allocate PlanBlackboardClient per Plan
    - emit Timeline markers via L15Pool

This implementation focuses on **interface contract + happy path**;
NanobotTask dispatch / wire signaling for user confirmation are P3
follow-ups. The skeleton lets verification tests pass and contract
shapes are stable for downstream chats.
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from parrot.brain.intent_workspace import (
    PayloadSource,
    StagedRefKind,
    StagedRefMetadata,
    StagedRefRequest,
    get_intent_workspace,
)
from parrot.brain.plan.plan import (
    Plan,
    PlanProposal,
    PlanState,
    PlanStep,
    PlanStepState,
)
from parrot.brain.plan.plan_blackboard import PlanBlackboardClient
from parrot.brain.plan.plan_lifecycle import PlanLifecycle

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class PlanRegistry:
    """Singleton registry holding active + historical Plans."""

    def __init__(self) -> None:
        self._active: dict[str, Plan] = {}
        self._archive: dict[str, Plan] = {}
        self._blackboards: dict[str, PlanBlackboardClient] = {}

    # ─── Lifecycle methods ─────────────────────────────────────

    async def draft(self, proposal: PlanProposal) -> Plan:
        plan = self._build_plan_from_proposal(proposal)

        # Stage Plan body to IntentWorkspace
        try:
            ws = get_intent_workspace()
            handle = await ws.stage(StagedRefRequest(
                kind=StagedRefKind.PLAN,
                payload_source=PayloadSource.INLINE_TEXT,
                payload_value=self._serialize_plan(plan),
                metadata=StagedRefMetadata(
                    origin=f"plan_registry:{plan.plan_id}",
                    kind=StagedRefKind.PLAN,
                    payload_source=PayloadSource.INLINE_TEXT,
                    related_plan_id=plan.plan_id,
                    related_intent_event_id=plan.intent_event_id,
                    auto_evict_on_intent_close=False,
                ),
            ))
            plan.staged_ref_id = handle.ref_id
        except Exception:
            logger.exception("PlanRegistry.draft: IntentWorkspace stage failed")

        plan.blackboard_namespace = f"plan/{plan.plan_id}"
        self._blackboards[plan.plan_id] = PlanBlackboardClient(plan.plan_id)
        self._active[plan.plan_id] = plan

        # Timeline marker
        self._mark_timeline("plan_drafted", plan)

        return plan

    async def submit_for_confirmation(self, plan_id: str) -> None:
        """Move Plan from DRAFT to AWAITING_USER_CONFIRMATION.

        # TODO(P3-Wire-PlanUI): Wire signaling to Unity is **NOT** wired.
        #   Currently we just write a Timeline marker. Real impl needs:
        #     1. New EcpEventType.PLAN_PROPOSED (touches wire — needs ADR
        #        upgrade, blocked by Phase 4 § 8 lock).
        #     2. Unity DTO + handler to render Plan card UI (mermaid /
        #        Gantt / step list / approve button).
        #     3. EcpCommand.APPROVE_PLAN / REJECT_PLAN / CANCEL_PLAN /
        #        REVISE_PLAN flow back from Unity.
        #     4. Brain RPC bridge to receive user decision and call
        #        approve() / cancel() accordingly.
        #   Until P3 wire ADR: callers must invoke approve() directly
        #   (test mode / GOSLO self-approve). See BRAIN-PLAN-V1 § 8.
        """
        plan = self._require_active(plan_id)
        PlanLifecycle.enforce_transition(plan, PlanState.AWAITING_USER_CONFIRMATION)
        self._mark_timeline("plan_submitted_for_confirmation", plan)

    async def approve(self, plan_id: str) -> None:
        plan = self._require_active(plan_id)
        PlanLifecycle.enforce_transition(plan, PlanState.APPROVED)
        plan.approved_at = time.time()
        plan.blocks_conversation = False
        self._mark_timeline("plan_confirmed", plan)

    async def start_executing(self, plan_id: str) -> None:
        """Approve → Executing transition. Dispatch ready PlanSteps.

        # TODO(Chat4-plan-dispatch): SKELETON. We mark step.state =
        #   DISPATCHED but **do NOT** call ``do_dispatch_task`` to push
        #   the NanobotTask onto Redis Stream. Chat 4 must wire:
        #     1. For each ready step: call
        #        ``parrot.brain.tools.dispatch_task.do_dispatch_task(
        #            task_type=step.expected_tool,
        #            params={**step.inputs, plan_id, step_id, result_channel},
        #            priority="normal"
        #        )``
        #     2. Stash returned task_id into step.nanobot_task_id
        #     3. Set up listener on CH_NANOBOT_RESULTS so result回流
        #        triggers report_step_result(plan_id, step_id, ...).
        #     4. Handle dispatch failures (don't transition to FAILED;
        #        retry / fallback).
        #   See BRAIN-PLAN-V1 § 7.4 + dsg_protocol_trigger_v2 § 5.5
        #   (IdleArchiveTrigger uses heartbeat pattern that this can mirror).
        """
        plan = self._require_active(plan_id)
        PlanLifecycle.enforce_transition(plan, PlanState.EXECUTING)
        plan.started_executing_at = time.time()
        for step in plan.ready_steps():
            step.state = PlanStepState.DISPATCHED
            step.started_at = time.time()
            # TODO(Chat4-plan-dispatch): real dispatch_task call here
        self._mark_timeline("plan_executing", plan)

    async def report_step_result(
        self,
        plan_id: str,
        step_id: str,
        *,
        success: bool,
        result_summary: str = "",
        result_ref_id: str = "",
        error: str = "",
    ) -> None:
        plan = self._require_active(plan_id)
        step = plan.step_by_id(step_id)
        if step is None:
            return
        step.completed_at = time.time()
        step.result_summary = result_summary
        step.result_ref_id = result_ref_id
        step.error = error
        step.state = PlanStepState.DONE if success else PlanStepState.FAILED

        # Cascade: dispatch ready steps now that this dep is done
        if success:
            for next_step in plan.ready_steps():
                next_step.state = PlanStepState.DISPATCHED
                next_step.started_at = time.time()

        # Plan-level transition
        if plan.any_step_failed():
            try:
                PlanLifecycle.enforce_transition(plan, PlanState.FAILED)
                plan.completed_at = time.time()
                self._mark_timeline("plan_failed", plan)
                self._archive_plan(plan)
            except Exception:
                logger.exception("Plan failed transition error")
        elif plan.all_steps_done():
            try:
                PlanLifecycle.enforce_transition(plan, PlanState.COMPLETE)
                plan.completed_at = time.time()
                self._mark_timeline("plan_complete", plan)
                self._archive_plan(plan)
            except Exception:
                logger.exception("Plan complete transition error")
        else:
            # Mark partial complete (intermediate)
            if plan.state == PlanState.EXECUTING and any(
                s.state == PlanStepState.DONE for s in plan.steps
            ):
                if PlanLifecycle.can_transition(plan.state, PlanState.PARTIAL_COMPLETE):
                    plan.state = PlanState.PARTIAL_COMPLETE

    async def cancel(self, plan_id: str, reason: str = "") -> None:
        plan = self._require_active(plan_id)
        PlanLifecycle.enforce_transition(plan, PlanState.CANCELLED)
        plan.completed_at = time.time()
        self._mark_timeline("plan_cancelled", plan, payload={"reason": reason})
        self._archive_plan(plan)

    async def revise(
        self, old_plan_id: str, new_proposal: PlanProposal
    ) -> Plan:
        old_plan = self._require_active_or_archived(old_plan_id)
        new_plan = await self.draft(new_proposal)
        new_plan.supersedes = old_plan.plan_id
        old_plan.superseded_by = new_plan.plan_id
        # Old plan transitions to REVISED
        try:
            PlanLifecycle.enforce_transition(old_plan, PlanState.REVISED)
        except Exception:
            pass
        self._mark_timeline("plan_revised", new_plan, payload={
            "supersedes": old_plan.plan_id,
        })
        if old_plan.plan_id in self._active:
            self._archive_plan(old_plan)
        return new_plan

    # ─── Lookups ───────────────────────────────────────────────

    def get(self, plan_id: str) -> Plan | None:
        return self._active.get(plan_id) or self._archive.get(plan_id)

    def get_current_plan(self) -> Plan | None:
        # Most recently drafted active plan
        actives = sorted(
            self._active.values(),
            key=lambda p: p.drafted_at,
            reverse=True,
        )
        return actives[0] if actives else None

    def list_active(self) -> list[Plan]:
        return list(self._active.values())

    def list_by_intent_event(self, intent_event_id: str) -> list[Plan]:
        return [
            p for p in (*self._active.values(), *self._archive.values())
            if p.intent_event_id == intent_event_id
        ]

    def list_by_episode(self, episode_id: str) -> list[Plan]:
        return [
            p for p in (*self._active.values(), *self._archive.values())
            if p.episode_id == episode_id
        ]

    def get_blackboard(self, plan_id: str) -> PlanBlackboardClient | None:
        return self._blackboards.get(plan_id)

    # ─── Internals ─────────────────────────────────────────────

    def _build_plan_from_proposal(self, proposal: PlanProposal) -> Plan:
        steps: list[PlanStep] = []
        for sp in proposal.suggested_steps:
            steps.append(PlanStep(
                step_id=sp.step_id or PlanStep().step_id,
                title=sp.title,
                expected_tool=sp.expected_tool,
                inputs=dict(sp.inputs),
                depends_on=tuple(sp.depends_on),
            ))
        return Plan(
            title=proposal.title,
            rationale=proposal.rationale,
            blocks_conversation=proposal.blocks_conversation,
            estimated_duration_s=proposal.estimated_duration_s,
            related_node_uuids=tuple(proposal.related_node_uuids),
            related_staged_ref_ids=tuple(proposal.related_staged_ref_ids),
            steps=steps,
        )

    def _archive_plan(self, plan: Plan) -> None:
        self._archive[plan.plan_id] = plan
        self._active.pop(plan.plan_id, None)

    def _require_active(self, plan_id: str) -> Plan:
        plan = self._active.get(plan_id)
        if plan is None:
            raise KeyError(f"Plan {plan_id} not active")
        return plan

    def _require_active_or_archived(self, plan_id: str) -> Plan:
        plan = self._active.get(plan_id) or self._archive.get(plan_id)
        if plan is None:
            raise KeyError(f"Plan {plan_id} not found")
        return plan

    def _mark_timeline(
        self, kind_str: str, plan: Plan, payload: dict | None = None,
    ) -> None:
        try:
            from parrot.dsg.l1_5 import (
                TimelineMarkerKind,
                get_l1_5_pool,
            )
            mapping = {
                "plan_drafted": TimelineMarkerKind.PLAN_DRAFTED,
                "plan_submitted_for_confirmation": TimelineMarkerKind.PLAN_DRAFTED,
                "plan_confirmed": TimelineMarkerKind.PLAN_CONFIRMED,
                "plan_executing": TimelineMarkerKind.PLAN_CONFIRMED,
                "plan_complete": TimelineMarkerKind.PLAN_COMPLETE,
                "plan_failed": TimelineMarkerKind.PLAN_FAILED,
                "plan_cancelled": TimelineMarkerKind.PLAN_CANCELLED,
                "plan_revised": TimelineMarkerKind.PLAN_REVISED,
            }
            marker_kind = mapping.get(kind_str, TimelineMarkerKind.PLAN_DRAFTED)
            base_payload = {
                "plan_id": plan.plan_id,
                "title": plan.title,
                "state": plan.state.value,
            }
            if payload:
                base_payload.update(payload)
            get_l1_5_pool().mark(marker_kind, payload=base_payload)
        except Exception:
            logger.debug("PlanRegistry timeline mark skipped (L1.5 unavailable)")

    @staticmethod
    def _serialize_plan(plan: Plan) -> str:
        """Lightweight JSON for IntentWorkspace stage. Full schema in
        DSG-ARCHIVE-V1 § 4.2 plans.jsonl."""
        import json
        return json.dumps({
            "plan_id": plan.plan_id,
            "title": plan.title,
            "rationale": plan.rationale,
            "state": plan.state.value,
            "intent_event_id": plan.intent_event_id,
            "episode_id": plan.episode_id,
            "drafted_at": plan.drafted_at,
            "blocks_conversation": plan.blocks_conversation,
            "steps": [
                {
                    "step_id": s.step_id,
                    "title": s.title,
                    "expected_tool": s.expected_tool,
                    "inputs": s.inputs,
                    "depends_on": list(s.depends_on),
                    "state": s.state.value,
                }
                for s in plan.steps
            ],
        }, ensure_ascii=False)


# ─── Singleton + test injection ──────────────────────────────────

_registry: PlanRegistry | None = None


def get_plan_registry() -> PlanRegistry:
    global _registry
    if _registry is None:
        _registry = PlanRegistry()
    return _registry


def set_plan_registry_for_test(registry: PlanRegistry | None) -> None:
    global _registry
    _registry = registry


__all__ = [
    "PlanRegistry",
    "get_plan_registry",
    "set_plan_registry_for_test",
]
