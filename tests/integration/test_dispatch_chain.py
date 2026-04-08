"""Integration test: Brain → Scheduler → Nanobot dispatch chain.

Requires Redis running (docker compose -f infra/docker-compose.dev.yml up -d).
Tests the full V3 chain: dispatch_task → SimpleRouter → Stream → NanobotConsumer → result.
"""

import asyncio
import json

import pytest

from parrot.brain.tools.dispatch_task import do_dispatch_task
from parrot.bus.nanobot_consumer import NanobotConsumer
from parrot.scheduler.service import SchedulerService
from parrot.shared.constants import CH_NANOBOT_RESULTS
from parrot.shared.redis_client import close_redis, get_redis


@pytest.fixture
async def redis():
    r = await get_redis()
    yield r
    await close_redis()


@pytest.fixture
async def scheduler():
    svc = SchedulerService()
    await svc.start()
    yield svc
    await svc.stop()


@pytest.fixture
async def nanobot():
    consumer = NanobotConsumer()
    await consumer.start()
    yield consumer
    await consumer.stop()


@pytest.mark.asyncio
async def test_dispatch_to_nanobot(redis, scheduler, nanobot):
    """Full chain: dispatch a research task → Scheduler routes to Nanobot → result published."""
    result_received = asyncio.Event()
    result_data = {}

    async def listen_results():
        pubsub = redis.pubsub()
        await pubsub.subscribe(CH_NANOBOT_RESULTS)
        async for message in pubsub.listen():
            if message["type"] == "message":
                result_data.update(json.loads(message["data"]))
                result_received.set()
                break

    listener = asyncio.create_task(listen_results())
    await asyncio.sleep(0.2)  # let subscriptions settle

    task_id = await do_dispatch_task("research", {"query": "what is IPoAC"})

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
