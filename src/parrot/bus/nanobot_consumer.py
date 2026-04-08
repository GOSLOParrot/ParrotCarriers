"""Nanobot task consumer — Path B (L2-only) stub for testing.

This runs inside ParrotCarriers (not inside the nanobot fork).
It mounts as a L2-only worker, reads tasks from Redis Stream,
and echoes back success without actually processing the task.

Roles:
  - Integration tests: proves the dispatch→consume→result chain works
  - Fallback: runs when the real nanobot gateway isn't available

For real task processing, use the nanobot gateway with the parrot_bus channel:
  GOSLOParrot/nanobot → nanobot/channels/parrot_bus.py
  Start with: python src/scripts/start_nanobot_worker.py
"""

from __future__ import annotations

import asyncio
import json
import logging
import time

from parrot.bus.manifest import ModuleManifest
from parrot.bus.mounting import ModuleMount
from parrot.shared.constants import CH_NANOBOT_RESULTS, STREAM_NANOBOT_DISPATCH
from parrot.shared.redis_client import get_redis
from parrot.shared.types import Layer, ModuleType

logger = logging.getLogger(__name__)

CONSUMER_GROUP = "nanobot-workers"
CONSUMER_NAME = "worker-0"


class NanobotConsumer:
    """L2-only worker that consumes tasks from the dispatch stream."""

    def __init__(self):
        self._manifest = ModuleManifest(
            module_id="nanobot-worker",
            module_type=ModuleType.WORKER,
            layers=[Layer.L2],
        )
        self._mount = ModuleMount(self._manifest)
        self._consumer_task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        logger.info("Nanobot consumer starting...")
        await self._mount.mount()
        await self._ensure_consumer_group()
        self._running = True
        self._consumer_task = asyncio.create_task(self._consume_loop())
        logger.info("Nanobot consumer running.")

    async def stop(self) -> None:
        self._running = False
        if self._consumer_task:
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass
        await self._mount.unmount()

    async def _ensure_consumer_group(self) -> None:
        """Create consumer group if it doesn't exist."""
        r = await get_redis()
        try:
            await r.xgroup_create(STREAM_NANOBOT_DISPATCH, CONSUMER_GROUP, id="0", mkstream=True)
            logger.info("Consumer group '%s' created", CONSUMER_GROUP)
        except Exception:
            logger.debug("Consumer group '%s' already exists", CONSUMER_GROUP)

    async def _consume_loop(self) -> None:
        """Main loop: read from stream, process, ack, publish result."""
        r = await get_redis()
        while self._running:
            try:
                entries = await r.xreadgroup(
                    CONSUMER_GROUP,
                    CONSUMER_NAME,
                    {STREAM_NANOBOT_DISPATCH: ">"},
                    count=1,
                    block=5000,
                )
                if not entries:
                    continue

                for stream_name, messages in entries:
                    for msg_id, fields in messages:
                        await self._handle_task(r, msg_id, fields)

            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Error in consume loop")
                await asyncio.sleep(1)

    async def _handle_task(self, r, msg_id: str, fields: dict) -> None:
        """Process a single task and report the result."""
        raw = fields.get("payload", "{}")
        task = json.loads(raw)
        task_id = task.get("task_id", "unknown")
        task_type = task.get("type", "unknown")

        logger.info("Nanobot processing task: %s (id=%s)", task_type, task_id)

        # Phase 1: stub execution — just echo back success
        # Phase 2: forward to actual nanobot agent loop
        result = {
            "task_id": task_id,
            "type": task_type,
            "status": "completed",
            "completed_at": time.time(),
        }

        await r.xack(STREAM_NANOBOT_DISPATCH, CONSUMER_GROUP, msg_id)
        await r.publish(CH_NANOBOT_RESULTS, json.dumps(result))
        logger.info("Nanobot task completed: %s (id=%s)", task_type, task_id)


async def run_nanobot_consumer() -> None:
    """Entry point for running the Nanobot consumer standalone."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    consumer = NanobotConsumer()
    try:
        await consumer.start()
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(run_nanobot_consumer())
