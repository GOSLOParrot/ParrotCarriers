"""Trigger Runner — orchestrates all DSG triggers as a background task.

Lifecycle:
  1. Brain Agent starts → runner.start() → runs all STARTUP triggers
  2. Background loop: every N seconds, ticks PERIODIC triggers
  3. Redis event subscription: routes events to EVENT_DRIVEN triggers
  4. Brain Agent stops → runner.stop()

The runner is the bridge between triggers and the rest of the system.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time

from parrot.dsg.l2b_graph import L2BGraph, get_l2b_graph
from parrot.dsg.triggers.base import BaseTrigger, TriggerKind, TriggerResult

logger = logging.getLogger(__name__)

TICK_INTERVAL_SECONDS = 60.0


class TriggerRunner:
    """Manages trigger lifecycle and event routing."""

    def __init__(self, graph: L2BGraph | None = None) -> None:
        self._graph = graph or get_l2b_graph()
        self._triggers: list[BaseTrigger] = []
        self._task: asyncio.Task | None = None
        self._event_task: asyncio.Task | None = None
        self._running = False
        self._session = None  # AgentSession, set by agent.py for generate_reply

    def register(self, trigger_cls: type[BaseTrigger]) -> None:
        instance = trigger_cls(self._graph)
        self._triggers.append(instance)
        logger.info("TriggerRunner: registered %s", instance.name)

    def register_all_defaults(self) -> None:
        from parrot.dsg.triggers import ALL_TRIGGERS
        for cls in ALL_TRIGGERS:
            self.register(cls)

    async def start(self) -> None:
        """Run startup triggers and begin background loop."""
        self._running = True

        for t in self._triggers:
            if TriggerKind.STARTUP in t.kinds:
                try:
                    result = await t.on_startup()
                    if result:
                        await self._process_result(result)
                except Exception:
                    logger.exception("TriggerRunner: startup failed for %s", t.name)

        self._task = asyncio.create_task(self._tick_loop())
        self._event_task = asyncio.create_task(self._event_loop())
        logger.info("TriggerRunner: started with %d triggers", len(self._triggers))

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
        if self._event_task:
            self._event_task.cancel()

    async def fire_event(self, event: dict) -> list[TriggerResult]:
        """Manually fire an event to all EVENT_DRIVEN triggers."""
        results = []
        for t in self._triggers:
            if TriggerKind.EVENT_DRIVEN in t.kinds:
                try:
                    result = await t.on_event(event)
                    if result:
                        await self._process_result(result)
                        results.append(result)
                except Exception:
                    logger.exception("TriggerRunner: event error in %s", t.name)
        return results

    async def _tick_loop(self) -> None:
        """Periodic tick for PERIODIC triggers."""
        try:
            while self._running:
                await asyncio.sleep(TICK_INTERVAL_SECONDS)
                now = time.time()

                for t in self._triggers:
                    if TriggerKind.PERIODIC not in t.kinds:
                        continue
                    if t.interval_seconds <= 0:
                        continue
                    if now - t._last_run < t.interval_seconds:
                        continue

                    try:
                        result = await t.on_tick()
                        t._last_run = now
                        t._run_count += 1
                        if result:
                            await self._process_result(result)
                    except Exception:
                        logger.exception("TriggerRunner: tick error in %s", t.name)

        except asyncio.CancelledError:
            pass

    async def _event_loop(self) -> None:
        """Subscribe to Redis channels for trigger events."""
        try:
            from parrot.shared.constants import CH_DSG_EVENTS, CH_NANOBOT_RESULTS, CH_TRIGGER_RESULTS
            from parrot.shared.redis_client import get_redis

            r = await get_redis()
            pubsub = r.pubsub()
            await pubsub.subscribe(CH_DSG_EVENTS, CH_NANOBOT_RESULTS, CH_TRIGGER_RESULTS)

            async for message in pubsub.listen():
                if not self._running:
                    break
                if message["type"] != "message":
                    continue

                try:
                    data = json.loads(message["data"])
                    await self.fire_event(data)
                except (json.JSONDecodeError, TypeError):
                    pass

        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception("TriggerRunner: event loop error")

    async def _process_result(self, result: TriggerResult) -> None:
        """Process a trigger result: log, update context, optionally tell Gemini."""
        logger.info(
            "Trigger [%s]: %s (nodes=%d, nanobot=%s, notify=%s)",
            result.trigger_name,
            result.summary,
            len(result.nodes_affected),
            result.dispatch_to_nanobot,
            result.notify_gemini,
        )

        if result.notify_gemini and result.notification_text and self._session:
            try:
                await self._session.generate_reply(
                    instructions=result.notification_text
                )
            except Exception:
                logger.debug("TriggerRunner: failed to notify Gemini for %s", result.trigger_name)


_runner: TriggerRunner | None = None


def get_trigger_runner() -> TriggerRunner:
    global _runner
    if _runner is None:
        _runner = TriggerRunner()
        _runner.register_all_defaults()
    return _runner
