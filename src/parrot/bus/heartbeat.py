"""Bus heartbeat — periodic liveness proof for all registered modules.

This is the BUS heartbeat (passive liveness), NOT nanobot's internal heartbeat
(active task trigger). See bus_v4.md v4.2 § 心跳机制边界.
"""

from __future__ import annotations

import asyncio
import logging
import time

from parrot.shared.constants import HASH_HEARTBEAT
from parrot.shared.redis_client import get_redis

logger = logging.getLogger(__name__)


class HeartbeatSender:
    """Sends periodic heartbeat for a module."""

    def __init__(self, module_id: str, interval_s: float = 30.0):
        self._module_id = module_id
        self._interval = interval_s
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._task = asyncio.create_task(self._loop())
        logger.info("Heartbeat started for %s (every %.0fs)", self._module_id, self._interval)

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Heartbeat stopped for %s", self._module_id)

    async def _loop(self) -> None:
        r = await get_redis()
        while True:
            await r.hset(HASH_HEARTBEAT, self._module_id, str(time.time()))
            await asyncio.sleep(self._interval)
