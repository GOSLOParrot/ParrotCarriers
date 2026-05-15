"""Tests for py-trees BT Scheduler router."""

import json

import py_trees
import pytest

from parrot.scheduler.router import BTRouter
from parrot.scheduler.service import SchedulerService
from parrot.shared.constants import CH_TRIGGER_RESULTS, STREAM_TRIGGER_RESULTS
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


def test_route_google_calendar_fetch_to_nanobot(router):
    result = router.route({
        "task_id": "gcal",
        "type": "calendar_fetch",
        "params": {"result_channel": "calendar_result"},
    })
    assert result["destination"] == "nanobot"
    assert router.active_tasks["gcal"]["result_channel"] == "calendar_result"


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


@pytest.mark.asyncio
async def test_scheduler_trigger_result_fanout_writes_bounded_ledger():
    class FakeRedis:
        def __init__(self):
            self.xadded: list[dict] = []
            self.published: list[tuple[str, str]] = []

        async def xadd(self, stream, fields, *, maxlen=None, approximate=False):
            self.xadded.append({
                "stream": stream,
                "fields": fields,
                "maxlen": maxlen,
                "approximate": approximate,
            })

        async def publish(self, channel, payload):
            self.published.append((channel, payload))

    redis = FakeRedis()
    service = SchedulerService()

    channel = await service._publish_trigger_result(
        redis,
        result={
            "task_id": "task_calendar",
            "type": "calendar_fetch",
            "status": "completed",
            "result": "[]",
        },
        result_channel="calendar_result",
        task_id="task_calendar",
        task_type="calendar_fetch",
    )

    assert channel == "calendar_result"
    assert redis.xadded[0]["stream"] == STREAM_TRIGGER_RESULTS
    assert redis.xadded[0]["maxlen"] == 200
    assert redis.xadded[0]["approximate"] is True
    ledger_payload = json.loads(redis.xadded[0]["fields"]["payload"])
    assert ledger_payload["type"] == "calendar_result"
    assert ledger_payload["original_type"] == "calendar_fetch"
    assert ledger_payload["task_id"] == "task_calendar"
    assert redis.published[0][0] == CH_TRIGGER_RESULTS
    published_payload = json.loads(redis.published[0][1])
    assert published_payload["type"] == "calendar_result"
