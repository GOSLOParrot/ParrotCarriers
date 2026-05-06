"""Scheduler service — mounts on Bus and routes tasks via py-trees BT.

Architecture (P1.5):
  Redis Pub/Sub event → write Blackboard → tree.tick() → read decision
  → async I/O (xadd to Nanobot Stream, publish result)

Also hosts the NanobotResultListener (Task 3):
  CH_NANOBOT_RESULTS → correlate with Blackboard active_tasks
  → publish CH_SCHEDULER_TO_BRAIN
"""

from __future__ import annotations

import asyncio
import json
import logging
import time

from parrot.bus.manifest import ModuleManifest
from parrot.bus.mounting import ModuleMount
from parrot.scheduler.router import BTRouter
from parrot.shared.config import ParrotConfig
from parrot.shared.constants import (
    CH_NANOBOT_RESULTS,
    CH_SCHEDULER_COMMANDS,
    CH_SCHEDULER_RESULTS,
    CH_SCHEDULER_TO_BRAIN,
    STREAM_NANOBOT_DISPATCH,
)
from parrot.shared.redis_client import get_redis
from parrot.shared.types import Layer, ModuleType

logger = logging.getLogger(__name__)

NANOBOT_TASK_TIMEOUT = 120.0
TIMEOUT_CHECK_INTERVAL = 15.0


class SchedulerService:
    """Scheduler: receives tasks, routes via BT, reports results, aggregates Nanobot output."""

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
        self._router = BTRouter()
        self._listener_task: asyncio.Task | None = None
        self._result_listener_task: asyncio.Task | None = None
        self._timeout_task: asyncio.Task | None = None
        self._pending_tasks: dict[str, float] = {}

    async def start(self) -> None:
        logger.info("Scheduler starting (py-trees BT)...")
        await self._mount.mount()
        self._listener_task = asyncio.create_task(self._listen_commands())
        self._result_listener_task = asyncio.create_task(self._listen_nanobot_results())
        self._timeout_task = asyncio.create_task(self._check_timeouts())
        logger.info("Scheduler running.\n%s", self._router.tree_ascii())

    async def stop(self) -> None:
        for task in (self._listener_task, self._result_listener_task, self._timeout_task):
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        await self._mount.unmount()

    async def _connect_livekit(self) -> None:
        logger.info(
            "Scheduler: connecting to LiveKit Room '%s'",
            self._config.livekit.room_name,
        )
        try:
            from livekit import rtc
            from livekit.api import AccessToken, VideoGrants
            import asyncio
            
            token = (
                AccessToken(self._config.livekit.api_key, self._config.livekit.api_secret)
                .with_identity(self._manifest.livekit_identity)
                .with_name("Parrot Scheduler")
                .with_grants(VideoGrants(room_join=True, room=self._config.livekit.room_name))
                .to_jwt()
            )
            
            self._room = rtc.Room()
            await self._room.connect(self._config.livekit.url, token)
            logger.info("Scheduler connected to LiveKit room %s as %s", self._room.name, self._manifest.livekit_identity)
        except ImportError:
            logger.warning("livekit client SDK not installed, skipping LiveKit connection")
        except Exception as e:
            logger.error("Scheduler failed to connect to LiveKit: %s", e)

    async def _listen_commands(self) -> None:
        """Subscribe to scheduler command channel → BT route → execute I/O."""
        r = await get_redis()
        pubsub = r.pubsub()
        await pubsub.subscribe(CH_SCHEDULER_COMMANDS)
        logger.info("Scheduler listening on %s", CH_SCHEDULER_COMMANDS)

        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            try:
                task = json.loads(message["data"])
                result = self._router.route(task)
                destination = result.get("destination", "brain_direct")

                if destination == "nanobot":
                    await r.xadd(
                        STREAM_NANOBOT_DISPATCH, {"payload": json.dumps(task)}
                    )
                    self._pending_tasks[task.get("task_id", "")] = time.monotonic()

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

    async def _listen_nanobot_results(self) -> None:
        """Aggregate Nanobot results → correlate with active_tasks → forward to Brain.

        # TODO(Chat4-plan-step-result-route): when ``active_tasks[task_id]``
        #   carries non-empty ``plan_id`` + ``step_id`` (set by
        #   ``DispatchToNanobot`` per cross_chat_pending_registry_20260507
        #   §3.B step 3), this listener must additionally route the result
        #   to ``parrot.brain.plan.PlanRegistry.report_step_result(plan_id,
        #   step_id, success=(status=="completed"), result_summary=...)``
        #   so Plan-and-Execute state machine can advance / cascade /
        #   fail-transition. The forward-to-Brain path (CH_SCHEDULER_TO_BRAIN)
        #   stays unchanged for non-Plan tasks.
        """
        r = await get_redis()
        pubsub = r.pubsub()
        await pubsub.subscribe(CH_NANOBOT_RESULTS)
        logger.info("Scheduler listening for Nanobot results on %s", CH_NANOBOT_RESULTS)

        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            try:
                result = json.loads(message["data"])
                task_id = result.get("task_id", "?")
                task_type = result.get("type", "unknown")
                status = result.get("status", "unknown")

                self._pending_tasks.pop(task_id, None)

                active = self._router.active_tasks
                if task_id in active:
                    active[task_id]["status"] = status
                    self._router.active_tasks = active

                # TODO(Chat4-plan-step-result-route): if active[task_id]
                #   has plan_id + step_id, additionally call
                #   ``PlanRegistry.report_step_result(...)`` here.

                summary = {
                    "task_id": task_id,
                    "type": task_type,
                    "status": status,
                    "result_summary": result.get("result", ""),
                    "source_worker": "nanobot",
                }
                await r.publish(CH_SCHEDULER_TO_BRAIN, json.dumps(summary))
                logger.info(
                    "Scheduler forwarded result to Brain: task=%s type=%s status=%s",
                    task_id, task_type, status,
                )
            except Exception:
                logger.exception("Error processing Nanobot result")


    async def _check_timeouts(self) -> None:
        """Periodically check for timed-out Nanobot tasks and notify Brain.

        # TODO(Chat4-plan-step-timeout): when active_tasks[task_id] has
        #   plan_id + step_id, the timeout path must also call
        #   ``PlanRegistry.report_step_result(plan_id, step_id,
        #   success=False, error="timeout after Ns")`` so Plan transitions
        #   to FAILED (or revisable) state. Otherwise a stuck Plan never
        #   completes / never fails. See cross_chat_pending_registry_20260507
        #   §3.B step 5.
        """
        while True:
            try:
                await asyncio.sleep(TIMEOUT_CHECK_INTERVAL)
                now = time.monotonic()
                timed_out = [
                    tid for tid, ts in self._pending_tasks.items()
                    if now - ts > NANOBOT_TASK_TIMEOUT
                ]
                if not timed_out:
                    continue

                r = await get_redis()
                for task_id in timed_out:
                    self._pending_tasks.pop(task_id, None)
                    active = self._router.active_tasks
                    if task_id in active:
                        active[task_id]["status"] = "timeout"
                        self._router.active_tasks = active

                    summary = {
                        "task_id": task_id,
                        "type": active.get(task_id, {}).get("type", "unknown"),
                        "status": "timeout",
                        "result_summary": f"Task timed out after {NANOBOT_TASK_TIMEOUT:.0f}s",
                        "source_worker": "nanobot",
                    }
                    await r.publish(CH_SCHEDULER_TO_BRAIN, json.dumps(summary))
                    logger.warning("Task %s timed out, notified Brain", task_id)

            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Error in timeout check")


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
