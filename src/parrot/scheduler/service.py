"""Scheduler service — mounts on Bus and routes tasks.

Mounts via Path A (L1+L2). Listens for dispatch requests from Brain,
routes them via SimpleRouter, and forwards results.
"""

from __future__ import annotations

import asyncio
import json
import logging

from parrot.bus.manifest import ModuleManifest
from parrot.bus.mounting import ModuleMount
from parrot.scheduler.router import SimpleRouter
from parrot.shared.config import ParrotConfig
from parrot.shared.constants import CH_SCHEDULER_COMMANDS, CH_SCHEDULER_RESULTS
from parrot.shared.redis_client import get_redis
from parrot.shared.types import Layer, ModuleType

logger = logging.getLogger(__name__)


class SchedulerService:
    """Scheduler: receives tasks, routes them, reports results."""

    def __init__(self, config: ParrotConfig | None = None):
        self._config = config or ParrotConfig()
        self._manifest = ModuleManifest(
            module_id="scheduler",
            module_type=ModuleType.CORE,
            layers=[Layer.L1, Layer.L2],
            livekit_identity="scheduler",
        )
        self._mount = ModuleMount(self._manifest)
        self._mount.set_l1_hooks(attach=self._connect_livekit)
        self._router = SimpleRouter()
        self._listener_task: asyncio.Task | None = None

    async def start(self) -> None:
        logger.info("Scheduler starting...")
        await self._mount.mount()
        self._listener_task = asyncio.create_task(self._listen_commands())
        logger.info("Scheduler running.")

    async def stop(self) -> None:
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
        await self._mount.unmount()

    async def _connect_livekit(self) -> None:
        logger.info(
            "Scheduler: connecting to LiveKit Room '%s'",
            self._config.livekit.room_name,
        )

    async def _listen_commands(self) -> None:
        """Subscribe to scheduler command channel and route tasks."""
        r = await get_redis()
        pubsub = r.pubsub()
        await pubsub.subscribe(CH_SCHEDULER_COMMANDS)
        logger.info("Scheduler listening on %s", CH_SCHEDULER_COMMANDS)

        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            try:
                task = json.loads(message["data"])
                destination = await self._router.route(task)
                logger.info("Task routed to: %s", destination)

                await r.publish(
                    CH_SCHEDULER_RESULTS,
                    json.dumps({
                        "task_id": task.get("task_id"),
                        "destination": destination,
                        "status": "routed",
                    }),
                )
            except Exception:
                logger.exception("Error routing task")


async def run_scheduler() -> None:
    """Entry point for running the Scheduler standalone."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    svc = SchedulerService()
    try:
        await svc.start()
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        await svc.stop()


if __name__ == "__main__":
    asyncio.run(run_scheduler())
