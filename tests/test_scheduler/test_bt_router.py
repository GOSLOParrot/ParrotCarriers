"""Tests for py-trees BT Scheduler router."""

import py_trees
import pytest

from parrot.scheduler.router import BTRouter
from parrot.shared.parrot_actions import BehaviorMode


@pytest.fixture(autouse=True)
def _reset_blackboard():
    """Reset py-trees global Blackboard between tests."""
    py_trees.blackboard.Blackboard.enable_activity_stream()
    yield
    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    py_trees.blackboard.Blackboard.activity_stream = None


@pytest.fixture
def router(_reset_blackboard):
    return BTRouter()


def test_route_research_to_nanobot(router):
    result = router.route({"task_id": "t1", "type": "research", "params": {}})
    assert result["destination"] == "nanobot"
    assert result["task_id"] == "t1"


def test_route_memory_consolidation_to_nanobot(router):
    result = router.route({"task_id": "t2", "type": "memory_consolidation", "params": {}})
    assert result["destination"] == "nanobot"


def test_route_vocabulary_learn_to_nanobot(router):
    result = router.route({"task_id": "t3", "type": "vocabulary_learn", "params": {}})
    assert result["destination"] == "nanobot"


def test_route_unknown_to_brain_direct(router):
    result = router.route({"task_id": "t4", "type": "conversation", "params": {}})
    assert result["destination"] == "brain_direct"


def test_route_reflex_priority(router):
    result = router.route({"task_id": "t5", "priority": "reflex", "action": "fly_to_hand"})
    assert result["destination"] == "reflex_direct"


def test_active_tasks_tracking(router):
    router.route({"task_id": "abc", "type": "research", "params": {}})
    active = router.active_tasks
    assert "abc" in active
    assert active["abc"]["status"] == "dispatched"
    assert active["abc"]["destination"] == "nanobot"


def test_active_tasks_dedup(router):
    """Routing the same task twice updates rather than duplicates."""
    router.route({"task_id": "dup", "type": "research", "params": {}})
    router.route({"task_id": "dup", "type": "research", "params": {}})
    active = router.active_tasks
    assert len([k for k in active if k == "dup"]) == 1


def test_tree_ascii_output(router):
    """tree_ascii() should return a non-empty string."""
    output = router.tree_ascii()
    assert "Router" in output
    assert "HandleReflex" in output
    assert "DispatchToNanobot" in output
    assert "HandleBrainDirect" in output


def test_default_behavior_mode(router):
    bb = router.blackboard_client
    mode = bb.behavior_mode
    assert BehaviorMode.BASE in mode
    assert BehaviorMode.COMPANION in mode
