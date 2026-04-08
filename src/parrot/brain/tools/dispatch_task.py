"""B11: dispatch_task — Brain asks Scheduler to route a background task.

Brain → Pub/Sub(scheduler.commands) → Scheduler → SimpleRouter
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
    summarization, or other background work.

    Args:
        task_type: Type of task (e.g. 'search_web', 'summarize', 'remind').
        params: JSON-encoded parameters for the task.
        priority: Task priority — 'high', 'normal', or 'low'.
    """
    try:
        parsed_params = json.loads(params) if isinstance(params, str) else params
    except json.JSONDecodeError:
        parsed_params = {"raw": params}

    task_id = await do_dispatch_task(task_type, parsed_params, priority)
    return f"Task dispatched (id={task_id}). I'll let you know when it's done."
