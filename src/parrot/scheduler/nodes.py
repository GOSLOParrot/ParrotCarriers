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

NANOBOT_TASK_TYPES = frozenset({
    "research", "summarize", "remind",
    "memory_consolidation", "vocabulary_learn",
})

BB_NS = "scheduler"


class DispatchToNanobot(py_trees.behaviour.Behaviour):
    """Route research / memory / vocabulary tasks to Nanobot."""

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

        active = self.blackboard.active_tasks
        active[task_id] = {
            "type": task_type,
            "status": "dispatched",
            "destination": "nanobot",
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
