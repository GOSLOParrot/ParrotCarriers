"""E1: BT Router — py-trees Selector replaces SimpleRouter if-else.

Tree structure (P1.5 — shallow, one-level Selector):

    Selector("Router", memory=False)
    ├── HandleReflex        — priority=="reflex"  → reflex_direct
    ├── DispatchToNanobot   — research/memory/vocab → nanobot
    └── HandleBrainDirect   — everything else       → brain_direct

Event-driven: caller writes Blackboard → tree.tick() → reads route_result.
"""

from __future__ import annotations

import logging
from typing import Any

import py_trees

from parrot.scheduler.nodes import (
    BB_NS,
    DispatchToNanobot,
    HandleBrainDirect,
    HandleReflex,
)
from parrot.shared.parrot_actions import BehaviorMode

logger = logging.getLogger(__name__)


def build_scheduler_tree() -> py_trees.trees.BehaviourTree:
    """Construct the P1.5 shallow behaviour tree."""
    root = py_trees.composites.Selector(
        name="Router",
        memory=False,
        children=[
            HandleReflex(),
            DispatchToNanobot(),
            HandleBrainDirect(),
        ],
    )
    tree = py_trees.trees.BehaviourTree(root=root)
    return tree


class BTRouter:
    """py-trees based router with Blackboard V2 integration.

    Usage (from async context):
        router = BTRouter()
        result = router.route(event_dict)
        # result = {"destination": "nanobot"|"brain_direct"|"reflex_direct", "task_id": ...}
    """

    def __init__(self) -> None:
        py_trees.blackboard.Blackboard.enable_activity_stream()
        self._tree = build_scheduler_tree()
        self._bb = py_trees.blackboard.Client(name="BTRouter", namespace=BB_NS)
        self._bb.register_key(
            key="current_event", access=py_trees.common.Access.WRITE
        )
        self._bb.register_key(
            key="route_result", access=py_trees.common.Access.WRITE
        )
        self._bb.register_key(
            key="active_tasks", access=py_trees.common.Access.WRITE
        )
        self._bb.register_key(
            key="behavior_mode", access=py_trees.common.Access.WRITE
        )

        self._bb.active_tasks = {}
        self._bb.route_result = {}
        self._bb.current_event = {}
        self._bb.behavior_mode = BehaviorMode.BASE | BehaviorMode.COMPANION

        self._tree.setup()

    def route(self, event: dict[str, Any]) -> dict[str, Any]:
        """Write event to Blackboard → tick → return route decision.

        This is a synchronous call. The async SchedulerService calls it
        from the event loop after receiving a Redis message.

        Sprint 1 only routes REFLEX and TASK layers. INTENT (autonomous BB
        state changes without Gemini touch) is reserved for Sprint 2's
        S2-Intent task; early callers get a crisp failure here rather than
        silent misroutes. See `sprint1_plan_20260422.md` §5.2 and
        `shared/event_log.EventLayer` docstring.
        """
        if event.get("layer") == "intent":
            raise NotImplementedError(
                "EventLayer.INTENT not implemented in Sprint 1. "
                "Autonomous-action routing lands in Sprint 2 S2-Intent."
            )

        self._bb.current_event = event
        self._bb.route_result = {}

        self._tree.tick()

        result = self._bb.route_result
        destination = result.get("destination", "brain_direct")
        logger.info(
            "BTRouter: event type=%s → %s", event.get("type", "?"), destination
        )
        return result

    @property
    def active_tasks(self) -> dict:
        return self._bb.active_tasks

    @active_tasks.setter
    def active_tasks(self, value: dict) -> None:
        self._bb.active_tasks = value

    @property
    def blackboard_client(self) -> py_trees.blackboard.Client:
        return self._bb

    def tree_ascii(self) -> str:
        """Return ASCII representation of the tree for debugging."""
        return py_trees.display.unicode_tree(self._tree.root, show_status=True)
