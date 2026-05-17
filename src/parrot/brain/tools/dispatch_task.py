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

    PlanRegistry calls this with ``plan_id`` and ``step_id`` in params when a
    Plan step is dispatched. Scheduler stores those fields in active-task
    metadata so Nanobot results and timeouts can return to the originating Plan
    step.
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
    """Dispatch non-blocking background work to Nanobot via Scheduler.

    This is the Task-layer tool, not an Intent-thinking tool. Use it when GOSLO
    has decided that work can happen outside the current conversational turn:
    research, slow summaries, long MCP/API calls, Calendar operations that need
    worker execution, or Plan steps that nanobot should complete. After calling
    this tool, GOSLO should be able to continue the conversation naturally while
    the task reports back through Scheduler/nanobot result channels, Plan step
    receipts, IntentWorkspace paper notes, or Runtime Flow ledgers.

    Do not use this when GOSLO needs the answer before replying. For quick
    context reads that belong inside a felt "thinking" moment, use a dedicated
    Intent/Thinking tool instead, such as a future calendar-context tool.

    Destructive external actions, including Calendar create/patch/delete, must
    only be dispatched after explicit user confirmation or a Plan/HITL gate has
    approved the action. Put the confirmation context, plan_id/step_id, and
    result_channel in params when available.

    Args:
        task_type: Type of task. Nanobot-routed types:
            'research' — web search, fact lookup, information gathering.
            'summarize' — summarize text or conversation.
            'remind' — create a reminder or timed notification.
            'memory_consolidation' — summarize and archive conversation history.
            'vocabulary_learn' — learn new words or concepts.
            'calendar_fetch' / 'calendar_create' / 'calendar_patch' /
            'calendar_delete' use Google Calendar via Nanobot Google Workspace MCP.
            'message_check' uses Gmail via Nanobot Google Workspace MCP.
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
