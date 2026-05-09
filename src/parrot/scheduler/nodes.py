"""py-trees Behaviour leaf nodes for the Scheduler BT.

P1.5: shallow Selector with three leaves — equivalent to SimpleRouter if-else
but with the correct py-trees interface for P2 expansion.

Design: BT nodes are pure decision-makers. They read /scheduler/current_event
from Blackboard and write /scheduler/route_result. The async SchedulerService
reads route_result after tick() and executes actual I/O (Redis xadd, publish).
"""

from __future__ import annotations

import logging

import py_trees

logger = logging.getLogger(__name__)

GENERAL_NANOBOT_TASK_TYPES = frozenset({
    "research",
    "summarize",
    "remind",
    "memory_consolidation",
    "vocabulary_learn",
})

GOOGLE_WORKSPACE_TASK_TYPES = frozenset({
    "calendar_fetch",
    "calendar_create",
    "calendar_patch",
    "calendar_delete",
    "message_check",
})

NANOBOT_TASK_TYPES = GENERAL_NANOBOT_TASK_TYPES | GOOGLE_WORKSPACE_TASK_TYPES

BB_NS = "scheduler"


class DispatchToNanobot(py_trees.behaviour.Behaviour):
    """Route background and external-connector tasks to Nanobot."""

    def __init__(self, name: str = "DispatchToNanobot"):
        super().__init__(name)
        self.blackboard = self.attach_blackboard_client(
            name="DispatchToNanobot", namespace=BB_NS
        )
        self.blackboard.register_key(
            key="current_event", access=py_trees.common.Access.READ
        )
        self.blackboard.register_key(
            key="route_result", access=py_trees.common.Access.WRITE
        )
        self.blackboard.register_key(
            key="active_tasks", access=py_trees.common.Access.WRITE
        )

    def update(self) -> py_trees.common.Status:
        event = self.blackboard.current_event
        if not event:
            return py_trees.common.Status.FAILURE

        task_type = event.get("type", "unknown")
        if task_type not in NANOBOT_TASK_TYPES:
            return py_trees.common.Status.FAILURE

        task_id = event.get("task_id", "unknown")

        # TODO(Chat4-plan-nanobot-correlation): when PlanRegistry calls
        #   do_dispatch_task with params={..., "plan_id", "step_id"}, the
        #   incoming ``event["params"]`` will carry both. Stash them into
        #   active_tasks so ``service._listen_nanobot_results`` can route
        #   the result back to PlanRegistry.report_step_result(...). See
        #   cross_chat_pending_registry_20260507 §3.B step 3.
        params = event.get("params", {}) or {}
        active = self.blackboard.active_tasks
        active[task_id] = {
            "type": task_type,
            "status": "dispatched",
            "destination": "nanobot",
            # Trigger-driven tasks use this to fan the Nanobot result back to
            # CH_TRIGGER_RESULTS. The Scheduler is the single fan-out owner;
            # Nanobot only needs to publish one normal task result.
            "result_channel": params.get("result_channel", ""),
            # NEED-P2.5-PLAN-INTEGRATION: extract Plan correlation fields
            # so result回流 / timeout 路径都能找到 Plan owner.
            "plan_id": params.get("plan_id", ""),
            "step_id": params.get("step_id", ""),
        }
        self.blackboard.active_tasks = active
        self.blackboard.route_result = {"destination": "nanobot", "task_id": task_id}

        self.feedback_message = f"dispatched {task_type} (id={task_id})"
        logger.info("BT DispatchToNanobot: %s → nanobot", task_type)
        return py_trees.common.Status.SUCCESS


class HandleBrainDirect(py_trees.behaviour.Behaviour):
    """Fallback: route unmatched tasks back to Brain for direct handling."""

    def __init__(self, name: str = "HandleBrainDirect"):
        super().__init__(name)
        self.blackboard = self.attach_blackboard_client(
            name="HandleBrainDirect", namespace=BB_NS
        )
        self.blackboard.register_key(
            key="current_event", access=py_trees.common.Access.READ
        )
        self.blackboard.register_key(
            key="route_result", access=py_trees.common.Access.WRITE
        )

    def update(self) -> py_trees.common.Status:
        event = self.blackboard.current_event
        if not event:
            return py_trees.common.Status.FAILURE

        task_id = event.get("task_id", "unknown")
        self.blackboard.route_result = {"destination": "brain_direct", "task_id": task_id}
        self.feedback_message = f"brain_direct (id={task_id})"
        logger.info("BT HandleBrainDirect: task %s → brain_direct", task_id)
        return py_trees.common.Status.SUCCESS


class HandleIntent(py_trees.behaviour.Behaviour):
    """Route EventLayer.INTENT events to the `intent_committed` destination.

    Sprint 2 policy (`sprint2_plan_20260423.md §3.5`):
        Intent events are **self-committing** — their producer (typically
        `brain.perception_supervisor`) has already written BB by the time the
        event arrives at the Scheduler. This node exists to complete the 4-leaf
        Selector symmetry (Reflex / Intent / Nanobot / BrainDirect) and to give
        future cross-process Intent producers a routable landing pad. It does
        NOT perform any BB writes; that would double-commit.
    """

    def __init__(self, name: str = "HandleIntent"):
        super().__init__(name)
        self.blackboard = self.attach_blackboard_client(
            name="HandleIntent", namespace=BB_NS
        )
        self.blackboard.register_key(
            key="current_event", access=py_trees.common.Access.READ
        )
        self.blackboard.register_key(
            key="route_result", access=py_trees.common.Access.WRITE
        )

    def update(self) -> py_trees.common.Status:
        event = self.blackboard.current_event
        if not event:
            return py_trees.common.Status.FAILURE

        if event.get("layer") != "intent":
            return py_trees.common.Status.FAILURE

        task_id = event.get("task_id", "unknown")
        kind = event.get("kind", "intent")
        self.blackboard.route_result = {
            "destination": "intent_committed",
            "task_id": task_id,
        }
        self.feedback_message = f"intent {kind} (id={task_id})"
        logger.info("BT HandleIntent: kind=%s → intent_committed", kind)
        return py_trees.common.Status.SUCCESS


class HandleReflex(py_trees.behaviour.Behaviour):
    """Reflex tasks bypass LLM — highest priority.

    P1.5: skeleton only (logs + SUCCESS). P2: integrates with DataChannel RPC.
    """

    def __init__(self, name: str = "HandleReflex"):
        super().__init__(name)
        self.blackboard = self.attach_blackboard_client(
            name="HandleReflex", namespace=BB_NS
        )
        self.blackboard.register_key(
            key="current_event", access=py_trees.common.Access.READ
        )
        self.blackboard.register_key(
            key="route_result", access=py_trees.common.Access.WRITE
        )

    def update(self) -> py_trees.common.Status:
        event = self.blackboard.current_event
        if not event:
            return py_trees.common.Status.FAILURE

        if event.get("priority") != "reflex":
            return py_trees.common.Status.FAILURE

        task_id = event.get("task_id", "unknown")
        self.blackboard.route_result = {"destination": "reflex_direct", "task_id": task_id}
        self.feedback_message = f"reflex (id={task_id})"
        logger.info("BT HandleReflex: %s → reflex_direct", event.get("action"))
        return py_trees.common.Status.SUCCESS
