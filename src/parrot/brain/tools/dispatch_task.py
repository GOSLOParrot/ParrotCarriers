"""B11: dispatch_task — Brain asks Scheduler to route a background task.

Brain → Pub/Sub(scheduler.commands) → Scheduler → BT Router
  → Redis Stream(nanobot.dispatch) → Nanobot consumes

Two entry points:
  - do_dispatch_task(): raw async function (tests, direct calls)
  - dispatch_task: @function_tool wrapper (LLM tool calling)
"""

from __future__ import annotations

import json
import logging
import uuid

from livekit.agents import RunContext, function_tool

from parrot.shared.constants import CH_SCHEDULER_COMMANDS
from parrot.shared.redis_client import get_redis

logger = logging.getLogger(__name__)


async def do_dispatch_task(
    task_type: str,
    params: dict | None = None,
    priority: str = "normal",
) -> str:
    """Core dispatch logic — callable from tests and from the function tool.

    Returns the task_id for tracking.

    # TODO(Chat4-plan-dispatch): When ``parrot.brain.plan.PlanRegistry``
    #   wires real Nanobot dispatch (DSG Chat 2 §9.1 F-3 +
    #   cross_chat_pending_registry_20260507 §3.B NEED-P2.5-PLAN-INTEGRATION),
    #   PlanRegistry.start_executing must call this function with:
    #       params={**step.inputs, "plan_id": plan.plan_id,
    #                "step_id": step.step_id,
    #                "result_channel": CH_NANOBOT_RESULTS}
    #   so that Scheduler / nanobot can correlate the task back to its
    #   originating Plan + step. The Scheduler side is also stubbed; see
    #   ``scheduler/nodes.py:DispatchToNanobot`` and
    #   ``scheduler/service.py:_listen_nanobot_results`` for the matching
    #   ``TODO(Chat4-plan-nanobot-correlation)`` markers.
    """
    task_id = str(uuid.uuid4())[:8]
    task = {
        "task_id": task_id,
        "type": task_type,
        "params": params or {},
        "priority": priority,
    }
    r = await get_redis()
    await r.publish(CH_SCHEDULER_COMMANDS, json.dumps(task))
    logger.info("dispatch_task: %s (id=%s) → Scheduler", task_type, task_id)
    return task_id


@function_tool()
async def dispatch_task(
    context: RunContext,
    task_type: str,
    params: str = "{}",
    priority: str = "normal",
) -> str:
    """Dispatch a background task to Nanobot via the Scheduler.

    Use this for anything that takes time: web searches, reminders,
    summarization, vocabulary learning, or other background work.

    Args:
        task_type: Type of task. Nanobot-routed types:
            'research' — web search, fact lookup, information gathering.
            'summarize' — summarize text or conversation.
            'remind' — create a reminder or timed notification.
            'memory_consolidation' — summarize and archive conversation history.
            'vocabulary_learn' — learn new words or concepts.
            Other types are handled directly by Brain (not dispatched to Nanobot).
        params: JSON-encoded parameters for the task.
        priority: Task priority — 'reflex', 'high', 'normal', or 'low'.
    """
    try:
        parsed_params = json.loads(params) if isinstance(params, str) else params
    except json.JSONDecodeError:
        parsed_params = {"raw": params}

    task_id = await do_dispatch_task(task_type, parsed_params, priority)
    return f"Task dispatched (id={task_id}). I'll let you know when it's done."
