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
    CH_TRIGGER_RESULTS,
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
        """Aggregate Nanobot results, update Plan metadata, then notify Brain.

        Plan-aware tasks carry ``plan_id`` and ``step_id`` in the dispatch-time
        Blackboard metadata. When those fields are present, Scheduler reports
        the result back to PlanRegistry before preserving the existing
        forward-to-Brain summary path for every task.
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
                task_meta = active.get(task_id, {})
                if task_id in active:
                    active[task_id]["status"] = status
                    self._router.active_tasks = active

                await self._report_plan_step_result(
                    task_meta=task_meta,
                    status=status,
                    result=result,
                )

                # Trigger tasks use Nanobot for external I/O but need the
                # structured result to re-enter the DSG trigger runner. The
                # Scheduler owns this fan-out because it has the dispatch-time
                # Blackboard metadata even when Nanobot is a separate process.
                result_channel = (
                    result.get("result_channel")
                    or task_meta.get("result_channel", "")
                )
                if result_channel:
                    trigger_payload = dict(result)
                    trigger_payload["type"] = result_channel
                    trigger_payload.setdefault("original_type", task_type)
                    await r.publish(CH_TRIGGER_RESULTS, json.dumps(trigger_payload))
                    logger.info(
                        "Scheduler fanned Nanobot result to TriggerRunner: "
                        "task=%s channel=%s",
                        task_id,
                        result_channel,
                    )

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
        """Periodically fail timed-out Nanobot tasks and report them upstream.

        If the pending task belongs to a Plan step, the timeout is reported to
        PlanRegistry so the Plan can fail or become revisable instead of
        hanging forever. Brain still receives the legacy timeout summary.
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

                    await self._report_plan_step_timeout(
                        task_meta=active.get(task_id, {}),
                        task_id=task_id,
                    )

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

    async def _report_plan_step_result(
        self,
        *,
        task_meta: dict,
        status: str,
        result: dict,
    ) -> None:
        plan_id = str(task_meta.get("plan_id") or "")
        step_id = str(task_meta.get("step_id") or "")
        if not plan_id or not step_id:
            return
        try:
            from parrot.brain.plan import get_plan_registry

            await get_plan_registry().report_step_result(
                plan_id,
                step_id,
                success=str(status).lower() in {"ok", "success", "completed", "done"},
                result_summary=str(result.get("result") or result.get("summary") or ""),
                result_ref_id=str(result.get("result_ref_id") or ""),
                error=str(result.get("error") or ""),
            )
        except Exception:
            logger.exception(
                "Scheduler failed to report Plan step result: plan=%s step=%s",
                plan_id,
                step_id,
            )

    async def _report_plan_step_timeout(self, *, task_meta: dict, task_id: str) -> None:
        plan_id = str(task_meta.get("plan_id") or "")
        step_id = str(task_meta.get("step_id") or "")
        if not plan_id or not step_id:
            return
        try:
            from parrot.brain.plan import get_plan_registry

            await get_plan_registry().report_step_result(
                plan_id,
                step_id,
                success=False,
                error=f"task {task_id} timed out after {NANOBOT_TASK_TIMEOUT:.0f}s",
            )
        except Exception:
            logger.exception(
                "Scheduler failed to report Plan step timeout: plan=%s step=%s",
                plan_id,
                step_id,
            )


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
