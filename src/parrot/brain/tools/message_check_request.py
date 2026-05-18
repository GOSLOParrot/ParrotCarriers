"""T3 Gmail/message check request tool for GOSLO.

GOSLO can ask Nanobot to inspect Gmail/Workspace messages without blocking the
live conversation or exposing OAuth credentials to the model runtime.
"""

from __future__ import annotations

import logging
from typing import Any

from livekit.agents import RunContext, function_tool

logger = logging.getLogger(__name__)


@function_tool()
async def message_check_request(
    context: RunContext,
    query: str = "Check Gmail for unread important messages",
    account: str = "",
    max_messages: int = 8,
    priority: str = "normal",
    reason: str = "",
) -> str:
    """Dispatch a non-blocking Gmail/Workspace message check to Nanobot.

    Category: Task-layer Google Workspace read tool. Use this when GOSLO needs
    Gmail/message context but does not need to hold the current voice turn open,
    or when the user asks to check mail in the background. Nanobot owns the
    Google Workspace MCP/OAuth call; GOSLO only dispatches and later summarizes
    returned results from Scheduler/Trigger ledgers.

    This tool is read-oriented. It does not send email, modify labels, delete
    messages, write Graphiti, or mutate L2-B. Important message results should
    return through result_channel=message_result so MessageNotificationTrigger
    can decide whether to stage L1.5 observations and gentle proactive notices.

    Args:
        query: Mail search/check instruction for Nanobot.
        account: Optional Google account hint. Leave empty for the configured
            default account.
        max_messages: Maximum messages Nanobot should summarize, capped at 20.
        priority: Scheduler priority: reflex, high, normal, or low.
        reason: Why GOSLO is checking messages in this conversation.
    """

    return await do_message_check_request(
        query=query,
        account=account,
        max_messages=max_messages,
        priority=priority,
        reason=reason,
    )


async def do_message_check_request(
    *,
    query: str = "Check Gmail for unread important messages",
    account: str = "",
    max_messages: int = 8,
    priority: str = "normal",
    reason: str = "",
    task_dispatcher: Any = None,
) -> str:
    bounded_limit = max(1, min(_safe_int(max_messages, 8), 20))
    selected_priority = _priority(priority)
    selected_query = " ".join(str(query or "").split())[:500]
    if not selected_query:
        selected_query = "Check Gmail for unread important messages"
    dispatcher = task_dispatcher
    if dispatcher is None:
        from parrot.brain.tools.dispatch_task import do_dispatch_task

        dispatcher = do_dispatch_task

    params = {
        "query": selected_query,
        "account": str(account or "").strip(),
        "max_messages": bounded_limit,
        "reason": str(reason or "GOSLO requested message context")[:500],
        "result_channel": "message_result",
        "source": "goslo_message_check_request",
        "instructions": (
            "Use Gmail/Google Workspace MCP or official API credentials available "
            "to Nanobot. Fetch unread or important messages relevant to the query. "
            "Return JSON only as an array of objects with id, thread_id, sender, "
            "subject, snippet, timestamp, is_reply, importance, and source. "
            "Do not send mail, modify labels, delete mail, write Graphiti, or "
            "mutate L2-B."
        ),
    }
    try:
        task_id = await dispatcher("message_check", params, selected_priority)
    except Exception as exc:
        logger.exception("message_check_request dispatch failed")
        return (
            "Message check dispatch failed "
            f"({type(exc).__name__}: {exc}). No Gmail write or memory mutation occurred."
        )
    return (
        "Message check dispatched to Nanobot "
        f"(task={task_id}, result_channel=message_result, max_messages={bounded_limit}). "
        "GOSLO can continue the conversation and use calendar_task_status or "
        "runtime ledgers later if the user asks for progress. No Gmail write, "
        "Graphiti write, or L2-B mutation occurred in this tool."
    )


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _priority(value: str) -> str:
    selected = str(value or "normal").strip().lower()
    return selected if selected in {"reflex", "high", "normal", "low"} else "normal"


__all__ = ["message_check_request", "do_message_check_request"]
