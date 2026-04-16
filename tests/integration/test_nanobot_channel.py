"""Integration test: ParrotBusChannel (real nanobot adapter) connectivity.

Requires Redis running (docker compose -f infra/docker-compose.dev.yml up -d).
Tests the nanobot-side ParrotBusChannel can consume tasks from the dispatch
stream and publish results back — the same path that the real nanobot gateway
uses, but without the full AgentLoop (we mock the agent reply).

Chain: ParrotCarriers Scheduler → Redis Stream → ParrotBusChannel → agent bus
      → mock reply → Redis Pub/Sub → ParrotCarriers Scheduler
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

NANOBOT_ROOT = Path(__file__).resolve().parents[3] / "nanobot"
if str(NANOBOT_ROOT) not in sys.path:
    sys.path.insert(0, str(NANOBOT_ROOT))

from parrot.brain.tools.dispatch_task import do_dispatch_task
from parrot.scheduler.service import SchedulerService
from parrot.shared.constants import CH_NANOBOT_RESULTS, CH_SCHEDULER_TO_BRAIN
from parrot.shared.redis_client import close_redis, get_redis


def _make_parrot_bus_channel():
    """Create a ParrotBusChannel with a mock MessageBus."""
    from nanobot.bus.queue import MessageBus
    from nanobot.channels.parrot_bus import ParrotBusChannel

    bus = MessageBus()
    config = {
        "enabled": True,
        "redisUrl": "redis://localhost:6379/0",
        "stream": "parrot.nanobot.dispatch",
        "resultsChannel": "parrot.nanobot.results",
        "consumerGroup": "nanobot-test-workers",
        "consumerName": "test-worker-0",
        "allowFrom": ["*"],
    }
    return ParrotBusChannel(config, bus), bus


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
async def parrot_bus():
    """Start the ParrotBusChannel and auto-reply from the bus."""
    channel, bus = _make_parrot_bus_channel()

    async def _auto_reply():
        """Simulate the nanobot agent: consume inbound, publish outbound via channel.send()."""
        from nanobot.bus.events import OutboundMessage

        while True:
            try:
                msg = await asyncio.wait_for(bus.consume_inbound(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break

            reply = OutboundMessage(
                channel="parrot_bus",
                chat_id=msg.chat_id,
                content=f"Nanobot completed: {msg.content[:60]}",
            )
            await channel.send(reply)

    channel_task = asyncio.create_task(channel.start())
    reply_task = asyncio.create_task(_auto_reply())
    await asyncio.sleep(0.5)

    yield channel

    await channel.stop()
    reply_task.cancel()
    channel_task.cancel()
    try:
        await asyncio.gather(channel_task, reply_task, return_exceptions=True)
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_parrot_bus_channel_consumes_and_replies(redis, scheduler, parrot_bus):
    """ParrotBusChannel reads from dispatch stream and publishes result to Pub/Sub."""
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
    await asyncio.sleep(0.2)

    task_id = await do_dispatch_task("research", {"query": "test parrot bus channel"})

    try:
        await asyncio.wait_for(result_received.wait(), timeout=15.0)
    except asyncio.TimeoutError:
        pytest.fail("Timed out waiting for ParrotBusChannel result")
    finally:
        listener.cancel()
        try:
            await listener
        except asyncio.CancelledError:
            pass

    assert result_data["task_id"] == task_id
    assert result_data["status"] == "completed"
    assert "Nanobot completed" in result_data.get("result", "")


@pytest.mark.asyncio
async def test_parrot_bus_full_chain_to_brain(redis, scheduler, parrot_bus):
    """Full chain: dispatch → ParrotBusChannel → result → Scheduler → CH_SCHEDULER_TO_BRAIN."""
    brain_received = asyncio.Event()
    brain_data = {}

    async def listen_brain():
        pubsub = redis.pubsub()
        await pubsub.subscribe(CH_SCHEDULER_TO_BRAIN)
        async for message in pubsub.listen():
            if message["type"] == "message":
                brain_data.update(json.loads(message["data"]))
                brain_received.set()
                break

    listener = asyncio.create_task(listen_brain())
    await asyncio.sleep(0.5)

    task_id = await do_dispatch_task("summarize", {"text": "ParrotCarriers is an AR parrot companion."})

    try:
        await asyncio.wait_for(brain_received.wait(), timeout=15.0)
    except asyncio.TimeoutError:
        pytest.fail("Timed out waiting for Scheduler→Brain forwarded result from ParrotBusChannel")
    finally:
        listener.cancel()
        try:
            await listener
        except asyncio.CancelledError:
            pass

    assert brain_data["task_id"] == task_id
    assert brain_data["status"] == "completed"
    assert brain_data["source_worker"] == "nanobot"
    assert "result_summary" in brain_data
