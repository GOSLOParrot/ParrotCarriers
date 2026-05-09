"""Google Calendar true-connection tests."""

from __future__ import annotations

import json

import pytest

import parrot.dsg.ingest.runner as ingest_runner_module
import parrot.dsg.l2b_graph as l2b_graph_module
from parrot.dsg.ingest.base import ObservationSource
from parrot.dsg.l1_5 import BucketKind, L15Pool, set_pool_for_test
from parrot.dsg.l2b_graph import L2BGraph
from parrot.dsg.l2b_types import NodeKind
from parrot.dsg.triggers.calendar_trigger import CalendarTrigger
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
async def test_calendar_result_enters_l1_5_google_bucket(env):
    graph, pool = env
    trigger = CalendarTrigger(graph)
    raw = json.dumps([
        {
            "id": "evt_1",
            "title": "Dentist",
            "start_time": "2026-05-09T10:00:00+08:00",
            "end_time": "2026-05-09T10:30:00+08:00",
            "location": "Clinic",
            "objects": ["insurance card"],
            "etag": "abc",
        }
    ])

    outcome = await trigger._parse_and_process(raw)
    assert outcome is not None
    assert len(outcome.commit_observations) == 1
    assert outcome.commit_observations[0].source == ObservationSource.GOOGLE_CALENDAR

    runner = TriggerRunner(graph=graph)
    await runner._process_result(outcome)

    handle = pool.get_bucket(BucketKind.GOOGLE_CALENDAR)
    assert handle is not None
    assert len(handle.node_uuids) == 1
    node = graph.all_nodes()[0]
    assert node.kind == NodeKind.EVENT
    assert node.source == ObservationSource.GOOGLE_CALENDAR.value
    assert node.source_meta["calendar_event_id"] == "evt_1"
    assert node.source_meta["etag"] == "abc"


@pytest.mark.asyncio
async def test_calendar_refresh_merges_by_google_event_id(env):
    graph, pool = env
    trigger = CalendarTrigger(graph)
    runner = TriggerRunner(graph=graph)

    first = await trigger._parse_and_process(json.dumps([
        {"id": "evt_2", "title": "Old title", "start_time": "2026-05-09T11:00:00+08:00"}
    ]))
    assert first is not None
    await runner._process_result(first)

    second = await trigger._parse_and_process(json.dumps([
        {
            "id": "evt_2",
            "title": "New title",
            "start_time": "2026-05-09T12:00:00+08:00",
            "etag": "new_etag",
        }
    ]))
    assert second is not None
    await runner._process_result(second)

    assert graph.node_count() == 1
    node = graph.all_nodes()[0]
    assert node.label == "New title"
    assert node.source_meta["etag"] == "new_etag"
    handle = pool.get_bucket(BucketKind.GOOGLE_CALENDAR)
    assert handle is not None
    assert len(handle.node_uuids) == 1
