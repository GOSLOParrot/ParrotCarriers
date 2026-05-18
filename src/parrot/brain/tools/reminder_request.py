"""Nanobot reminder/proactive follow-up request tool for GOSLO."""

from __future__ import annotations

import logging
from typing import Any

from livekit.agents import RunContext, function_tool

logger = logging.getLogger(__name__)


@function_tool()
async def reminder_request(
    context: RunContext,
    reminder_text: str,
    when: str,
    priority: str = "normal",
    reason: str = "",
    require_user_confirmation: bool = True,
) -> str:
    """Dispatch a reminder or proactive follow-up request to Nanobot.

    Category: Task-layer reminder tool. Use this when the user asks GOSLO to
    remind them later, or when a Plan/HITL-approved workflow needs a future
    nudge. The live conversation should not wait for the reminder to mature.

    Nanobot/Scheduler owns scheduling and eventual proactive delivery. This
    tool does not write Google Calendar, does not create Graphiti Episodes, and
    does not mutate L2-B. If the reminder should also become a Calendar event,
    use the Calendar draft/approval flow instead.

    Args:
        reminder_text: What to remind the user about.
        when: Natural-language or ISO-ish target time.
        priority: Scheduler priority: reflex, high, normal, or low.
        reason: Why this reminder exists.
        require_user_confirmation: Keep true unless the user already explicitly
            asked for this reminder in the same turn.
    """

    return await do_reminder_request(
        reminder_text=reminder_text,
        when=when,
        priority=priority,
        reason=reason,
        require_user_confirmation=require_user_confirmation,
    )


async def do_reminder_request(
    *,
    reminder_text: str,
    when: str,
    priority: str = "normal",
    reason: str = "",
    require_user_confirmation: bool = True,
    task_dispatcher: Any = None,
) -> str:
    text = " ".join(str(reminder_text or "").split())[:500]
    target_time = " ".join(str(when or "").split())[:160]
    if not text or not target_time:
        return (
            "Reminder request rejected: reminder_text and when are required. "
            "No task dispatch or memory mutation occurred."
        )

    dispatcher = task_dispatcher
    if dispatcher is None:
        from parrot.brain.tools.dispatch_task import do_dispatch_task

        dispatcher = do_dispatch_task

    params = {
        "reminder_text": text,
        "when": target_time,
        "reason": str(reason or "GOSLO reminder request")[:500],
        "result_channel": "reminder_result",
        "source": "goslo_reminder_request",
        "require_user_confirmation": bool(require_user_confirmation),
        "instructions": (
            "Schedule or track this reminder for the user. Report back through "
            "the configured result channel when it is due or if scheduling fails. "
            "Do not create Google Calendar events unless a separate approved "
            "Calendar workflow explicitly requests that route."
        ),
    }
    try:
        task_id = await dispatcher("remind", params, _priority(priority))
    except Exception as exc:
        logger.exception("reminder_request dispatch failed")
        return (
            "Reminder dispatch failed "
            f"({type(exc).__name__}: {exc}). No Calendar write or memory mutation occurred."
        )
    return (
        f"Reminder request dispatched to Nanobot (task={task_id}, when={target_time}). "
        "GOSLO can continue the conversation; the future reminder belongs to "
        "Scheduler/Nanobot, not L2-B or Graphiti."
    )


def _priority(value: str) -> str:
    selected = str(value or "normal").strip().lower()
    return selected if selected in {"reflex", "high", "normal", "low"} else "normal"


__all__ = ["reminder_request", "do_reminder_request"]
