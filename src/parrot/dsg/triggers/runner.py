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
from parrot.dsg.triggers.base import BaseTrigger, TriggerKind, TriggerOutcome

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

    async def fire_event(self, event: dict) -> list[TriggerOutcome]:
        """Route one incoming event to event-driven and on-demand triggers.

        ``ON_DEMAND`` triggers still self-filter inside ``on_event``. Including
        them here makes Web/operator-triggered scene and roleplay events use the
        same TriggerOutcome pipeline instead of requiring a private singleton
        call from the Web process.
        """
        results = []
        for t in self._triggers:
            if not (
                TriggerKind.EVENT_DRIVEN in t.kinds
                or TriggerKind.ON_DEMAND in t.kinds
            ):
                continue
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
            from parrot.shared.constants import CH_DSG_EVENTS, CH_TRIGGER_RESULTS
            from parrot.shared.redis_client import get_redis

            r = await get_redis()
            pubsub = r.pubsub()
            # The Scheduler is the single fan-out owner for Nanobot task
            # results. TriggerRunner only consumes the explicit trigger
            # channel, which prevents duplicate calendar/message processing
            # when a worker and Scheduler both see the same Nanobot result.
            await pubsub.subscribe(CH_DSG_EVENTS, CH_TRIGGER_RESULTS)

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

    async def _process_result(self, result: TriggerOutcome) -> None:
        """Process a TriggerOutcome (DSG-TRIGGER-V2 § 4).

        Order is fixed (avoid inter-channel dependency races):
            1. bucket_ops              影响 admit 路由
            2. commit_observations     入 L1.5 池
            3. staged_refs             stage 大文件
            4. archive_request         入归档队列
            5. plan_request            draft Plan
            6. dispatch_to_nanobot     既有 — 后台任务
            7. notify_gemini           legacy — C3 status notice by default
        Each channel is wrapped in its own try/except so a failure in
        one channel does not block the others.
        """
        logger.info(
            "Trigger [%s]: %s (nodes=%d, nanobot=%s, notify=%s, "
            "obs=%d, bucket_ops=%d, refs=%d, archive=%s, plan=%s)",
            result.trigger_name,
            result.summary,
            len(result.nodes_affected),
            result.dispatch_to_nanobot,
            result.notify_gemini,
            len(result.commit_observations),
            len(result.bucket_ops),
            len(result.staged_refs),
            "yes" if result.archive_request else "no",
            "yes" if result.plan_request else "no",
        )

        # ── 1. bucket_ops ──
        if result.bucket_ops:
            try:
                from parrot.dsg.l1_5 import get_l1_5_pool
                pool = get_l1_5_pool()
                for op in result.bucket_ops:
                    op_result = await pool.apply_bucket_op(op)
                    if not op_result.success:
                        logger.warning(
                            "bucket_op failed: %s — %s", op, op_result.error,
                        )
            except Exception:
                logger.exception("bucket_ops dispatch failed")

        # ── 2. commit_observations ──
        # Route through L15Pool.admit so triggers get full pool
        # bookkeeping (bucket assignment + RefTable bind + Timeline
        # marker). Pool internally calls IngestRunner._merge / _commit
        # so the Phase 4 invariants (Ingest = sole L2-B write gate)
        # remain intact.
        if result.commit_observations:
            try:
                from parrot.dsg.l1_5 import get_l1_5_pool
                pool = get_l1_5_pool()
                await pool.admit(tuple(result.commit_observations))
            except Exception:
                logger.exception("commit_observations dispatch failed")

        # ── 3. staged_refs ──
        if result.staged_refs:
            try:
                from parrot.brain.intent_workspace import get_intent_workspace
                ws = get_intent_workspace()
                for req in result.staged_refs:
                    await ws.stage(req)
            except Exception:
                logger.exception("staged_refs dispatch failed")

        # ── 4. archive_request ──
        if result.archive_request is not None:
            try:
                from parrot.dsg.archive import dispatch_archive_request
                await dispatch_archive_request(result.archive_request)
            except Exception:
                logger.exception("archive_request dispatch failed")

        # ── 5. plan_request ──
        if result.plan_request is not None:
            try:
                from parrot.brain.plan import get_plan_registry
                registry = get_plan_registry()
                await registry.draft(result.plan_request)
            except Exception:
                logger.exception("plan_request dispatch failed")

        # ── 6. dispatch_to_nanobot (legacy) ──
        if result.dispatch_to_nanobot and result.nanobot_task:
            try:
                from parrot.brain.tools.dispatch_task import do_dispatch_task
                task_type = result.nanobot_task.get("task_type", "")
                params = result.nanobot_task.get("params", {})
                priority = result.nanobot_task.get("priority", "normal")
                if task_type:
                    await do_dispatch_task(task_type, params, priority=priority)
            except Exception:
                logger.exception("nanobot dispatch failed for %s", result.trigger_name)

        # ── 7. notify_gemini (legacy) ──
        if result.notify_gemini and result.notification_text and self._session:
            try:
                # ``notify_gemini`` predates the trigger body-feel taxonomy and
                # used to mean C4 speech. That is too strong for ordinary
                # calendar/message/scene context. Default to C3 so GOSLO sees
                # the hint on the next natural turn; future priority fields can
                # opt into C4 explicitly after review.
                from parrot.brain.context_injector import get_context_injector

                injector = get_context_injector()
                if injector:
                    await injector.inject_status_notice(result.notification_text)
            except Exception:
                logger.debug(
                    "TriggerRunner: failed to deliver C3 trigger notice for %s",
                    result.trigger_name,
                )


_runner: TriggerRunner | None = None


def get_trigger_runner() -> TriggerRunner:
    global _runner
    if _runner is None:
        _runner = TriggerRunner()
        _runner.register_all_defaults()
    return _runner
