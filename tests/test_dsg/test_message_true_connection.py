"""Google/Gmail message trigger true-connection tests."""

from __future__ import annotations

import pytest

import parrot.dsg.ingest.runner as ingest_runner_module
import parrot.dsg.l2b_graph as l2b_graph_module
from parrot.dsg.ingest.base import ObservationSource
from parrot.dsg.l1_5 import BucketKind, L15Pool, set_pool_for_test
from parrot.dsg.l2b_graph import L2BGraph
from parrot.dsg.l2b_types import NodeKind
from parrot.dsg.triggers.base import TriggerKind
from parrot.dsg.triggers.message_trigger import MessageNotificationTrigger
from parrot.dsg.triggers.runner import TriggerRunner


@pytest.fixture
def env():
    """Fresh L2-B graph, L1.5 pool, and ingest runner singleton per test."""
    graph = L2BGraph()
    pool = L15Pool()
    l2b_graph_module._instance = graph
    ingest_runner_module._runner = None
    set_pool_for_test(pool)
    yield graph, pool
    set_pool_for_test(None)
    ingest_runner_module._runner = None
    l2b_graph_module._instance = None


@pytest.mark.asyncio
async def test_message_trigger_dispatches_important_mail_check_on_startup(
    env, monkeypatch
):
    graph, _pool = env
    trigger = MessageNotificationTrigger(graph)
    dispatched: list[tuple[str, dict]] = []

    async def fake_dispatch(task_type: str, params: dict):
        dispatched.append((task_type, params))
        return "task_startup_message"

    monkeypatch.setattr(trigger, "_dispatch_nanobot", fake_dispatch)

    outcome = await trigger.on_startup()

    assert TriggerKind.STARTUP in MessageNotificationTrigger.kinds
    assert outcome is not None
    assert outcome.trigger_name == "message_notification"
    assert outcome.summary == "Message check dispatched (task=task_startup_message)"
    assert outcome.dispatch_to_nanobot is False
    assert outcome.nanobot_task is not None
    assert outcome.nanobot_task["task_id"] == "task_startup_message"
    assert len(dispatched) == 1
    task_type, params = dispatched[0]
    assert task_type == "message_check"
    assert outcome.nanobot_task["task_type"] == task_type
    assert outcome.nanobot_task["params"] == params
    assert params["result_channel"] == "message_result"
    assert "unread important messages" in params["query"]
    assert "Skip marketing emails" in params["instructions"]


@pytest.mark.asyncio
async def test_message_push_enters_l1_5_google_message_bucket(env, monkeypatch):
    graph, pool = env
    monkeypatch.setattr(
        MessageNotificationTrigger,
        "_is_quiet_hour",
        staticmethod(lambda: False),
    )
    trigger = MessageNotificationTrigger(graph)

    outcome = await trigger._process_messages([
        {
            "id": "msg_1",
            "sender": "test@example.com",
            "subject": "Need your approval",
            "snippet": "Please review the plan.",
            "importance": "high",
        }
    ])

    assert outcome is not None
    assert graph.node_count() == 0  # trigger itself must not bypass L1.5/Ingest
    assert len(outcome.commit_observations) == 1
    assert outcome.commit_observations[0].source == ObservationSource.GOOGLE_MESSAGE
    assert outcome.proactive_speech is True

    runner = TriggerRunner(graph=graph)
    await runner._process_result(outcome)

    handle = pool.get_bucket(BucketKind.GOOGLE_MESSAGE)
    assert handle is not None
    assert len(handle.node_uuids) == 1
    node = graph.all_nodes()[0]
    assert node.kind == NodeKind.EVENT
    assert node.source == ObservationSource.GOOGLE_MESSAGE.value
    assert node.source_meta["message_id"] == "msg_1"
    assert node.source_meta["sender"] == "test@example.com"


@pytest.mark.asyncio
async def test_message_result_accepts_nanobot_fenced_json(env, monkeypatch):
    graph, _pool = env
    monkeypatch.setattr(
        MessageNotificationTrigger,
        "_is_quiet_hour",
        staticmethod(lambda: False),
    )
    trigger = MessageNotificationTrigger(graph)

    outcome = await trigger._parse_and_process(
        """```json
[
  {
    "id": "msg_fenced",
    "sender": "demo@example.com",
    "subject": "[重要]项目演示邮件",
    "snippet": "请参加毕业典礼的同学抓紧时间完成填写群内表格",
    "timestamp": "2026-05-19T08:18:32+08:00",
    "is_reply": false,
    "importance": true
  }
]
```"""
    )

    assert outcome is not None
    assert outcome.trigger_name == "message_notification"
    assert outcome.proactive_speech is True
    assert "[重要]项目演示邮件" in outcome.notification_text
    assert len(outcome.commit_observations) == 1
    assert outcome.commit_observations[0].source == ObservationSource.GOOGLE_MESSAGE
    assert outcome.commit_observations[0].meta["message_id"] == "msg_fenced"
    assert outcome.commit_observations[0].meta["importance"] == "high"


@pytest.mark.asyncio
async def test_message_refresh_merges_by_message_id(env, monkeypatch):
    graph, pool = env
    monkeypatch.setattr(
        MessageNotificationTrigger,
        "_is_quiet_hour",
        staticmethod(lambda: False),
    )
    trigger = MessageNotificationTrigger(graph)
    runner = TriggerRunner(graph=graph)

    first = await trigger._process_messages([
        {
            "id": "msg_2",
            "sender": "test@example.com",
            "subject": "Old subject",
            "snippet": "First",
            "importance": "high",
        }
    ])
    assert first is not None
    await runner._process_result(first)

    trigger._notified_ids.clear()
    second = await trigger._process_messages([
        {
            "id": "msg_2",
            "sender": "test@example.com",
            "subject": "Updated subject",
            "snippet": "Second",
            "importance": "high",
        }
    ])
    assert second is not None
    await runner._process_result(second)

    assert graph.node_count() == 1
    node = graph.all_nodes()[0]
    assert node.label == "Message: Updated subject"
    assert node.source_meta["snippet"] == "Second"
    handle = pool.get_bucket(BucketKind.GOOGLE_MESSAGE)
    assert handle is not None
    assert len(handle.node_uuids) == 1
