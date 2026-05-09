"""Integration test: Brain → Scheduler → Nanobot dispatch chain.

Requires Redis running (docker compose -f infra/docker-compose.dev.yml up -d).
Tests the full chain: dispatch_task → BT Router → Stream → NanobotConsumer → result
  → Scheduler aggregation → CH_SCHEDULER_TO_BRAIN.
"""

import asyncio
import json

import pytest
from redis.exceptions import RedisError

from parrot.brain.tools.dispatch_task import do_dispatch_task
from parrot.bus.nanobot_consumer import NanobotConsumer
from parrot.scheduler.service import SchedulerService
from parrot.shared.constants import (
    CH_NANOBOT_RESULTS,
    CH_SCHEDULER_TO_BRAIN,
)
from parrot.shared.redis_client import close_redis, get_redis


@pytest.fixture
async def redis():
    r = await get_redis()
    try:
        await r.ping()
    except RedisError as exc:
        await close_redis()
        pytest.skip(f"Redis integration dependency unavailable: {exc}")
    try:
        yield r
    finally:
        await close_redis()


@pytest.fixture
async def scheduler(redis):
    svc = SchedulerService()
    await svc.start()
    yield svc
    await svc.stop()


@pytest.fixture
async def nanobot(redis):
    consumer = NanobotConsumer()
    await consumer.start()
    yield consumer
    await consumer.stop()


@pytest.mark.asyncio
async def test_dispatch_to_nanobot(redis, scheduler, nanobot):
    """Full chain: dispatch a research task → Scheduler routes to Nanobot → result published."""
    task_id = await do_dispatch_task("research", {"query": "what is IPoAC"})

    result_received = asyncio.Event()
    result_data = {}

    async def listen_results():
        pubsub = redis.pubsub()
        await pubsub.subscribe(CH_NANOBOT_RESULTS)
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            data = json.loads(message["data"])
            if data.get("task_id") == task_id:
                result_data.update(data)
                result_received.set()
                break

    listener = asyncio.create_task(listen_results())

    try:
        await asyncio.wait_for(result_received.wait(), timeout=10.0)
    except asyncio.TimeoutError:
        pytest.fail("Timed out waiting for Nanobot result")
    finally:
        listener.cancel()
        try:
            await listener
        except asyncio.CancelledError:
            pass

    assert result_data["task_id"] == task_id
    assert result_data["type"] == "research"
    assert result_data["status"] == "completed"


@pytest.mark.asyncio
async def test_full_chain_scheduler_to_brain(redis, scheduler, nanobot):
    """Formal path: dispatch → Nanobot → CH_NANOBOT_RESULTS → Scheduler aggregation → CH_SCHEDULER_TO_BRAIN.

    This is the official result delivery path (D13). Brain listens to
    CH_SCHEDULER_TO_BRAIN, NOT directly to CH_NANOBOT_RESULTS.
    """
    task_id = await do_dispatch_task("research", {"query": "what is RFC 1149"})

    brain_received = asyncio.Event()
    brain_data = {}

    async def listen_brain_channel():
        pubsub = redis.pubsub()
        await pubsub.subscribe(CH_SCHEDULER_TO_BRAIN)
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            data = json.loads(message["data"])
            if data.get("task_id") == task_id:
                brain_data.update(data)
                brain_received.set()
                break

    listener = asyncio.create_task(listen_brain_channel())

    try:
        await asyncio.wait_for(brain_received.wait(), timeout=10.0)
    except asyncio.TimeoutError:
        pytest.fail("Timed out waiting for Scheduler→Brain forwarded result")
    finally:
        listener.cancel()
        try:
            await listener
        except asyncio.CancelledError:
            pass

    assert brain_data["task_id"] == task_id
    assert brain_data["type"] == "research"
    assert brain_data["status"] == "completed"
    assert brain_data["source_worker"] == "nanobot"
    assert "result_summary" in brain_data


@pytest.mark.asyncio
async def test_brain_direct_route(redis, scheduler):
    """Tasks that don't match nanobot types should route to brain_direct."""
    routed = asyncio.Event()
    route_result = {}

    async def listen_scheduler_results():
        from parrot.shared.constants import CH_SCHEDULER_RESULTS

        pubsub = redis.pubsub()
        await pubsub.subscribe(CH_SCHEDULER_RESULTS)
        async for message in pubsub.listen():
            if message["type"] == "message":
                route_result.update(json.loads(message["data"]))
                routed.set()
                break

    listener = asyncio.create_task(listen_scheduler_results())
    await asyncio.sleep(0.2)

    await do_dispatch_task("conversation", {"utterance": "hello"})

    try:
        await asyncio.wait_for(routed.wait(), timeout=5.0)
    except asyncio.TimeoutError:
        pytest.fail("Timed out waiting for scheduler routing result")
    finally:
        listener.cancel()
        try:
            await listener
        except asyncio.CancelledError:
            pass

    assert route_result["destination"] == "brain_direct"
