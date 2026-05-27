"""T3 Obsidian diary query request tool for GOSLO."""

from __future__ import annotations

import logging
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from livekit.agents import RunContext, function_tool

logger = logging.getLogger(__name__)


@function_tool()
async def diary_query_request(
    context: RunContext,
    query: str = "Summarize my recent diary entries",
    date_from: str = "",
    date_to: str = "",
    diary_root: str = "",
    limit: int = 7,
    priority: str = "high",
    reason: str = "",
) -> str:
    """Dispatch a non-blocking local Obsidian diary read to Nanobot.

    Category: Task-layer local Obsidian read tool. Use this when GOSLO needs
    to ask Nanobot to read the user's diary Markdown files without blocking the
    live conversation. Diary files are UUID-free profile=daily notes under the
    Diary folder. UUID-bound profile=ref notes belong under Refs and should not
    be treated as diaries.

    Args:
        query: What Nanobot should answer from diary entries.
        date_from: Optional YYYY-MM-DD inclusive start date.
        date_to: Optional YYYY-MM-DD inclusive end date.
        diary_root: Optional absolute diary folder path.
        limit: Maximum diary entries to summarize, capped at 30.
        priority: Scheduler priority: reflex, high, normal, or low.
        reason: Why GOSLO is asking for diary context in this conversation.
    """

    return await do_diary_query_request(
        query=query,
        date_from=date_from,
        date_to=date_to,
        diary_root=diary_root,
        limit=limit,
        priority=priority,
        reason=reason,
    )


async def do_diary_query_request(
    *,
    query: str = "Summarize my recent diary entries",
    date_from: str = "",
    date_to: str = "",
    diary_root: str = "",
    limit: int = 7,
    priority: str = "high",
    reason: str = "",
    task_dispatcher: Any = None,
) -> str:
    bounded_limit = max(1, min(_safe_int(limit, 7), 30))
    selected_query = " ".join(str(query or "").split())[:500] or "Summarize my recent diary entries"
    start, end = _date_window(date_from=date_from, date_to=date_to)
    root = _diary_root(diary_root)
    dispatcher = task_dispatcher
    if dispatcher is None:
        from parrot.brain.tools.dispatch_task import do_dispatch_task

        dispatcher = do_dispatch_task

    params = {
        "query": selected_query,
        "diary_root": str(root),
        "vault_path": str(root.parent),
        "date_from": start,
        "date_to": end,
        "limit": bounded_limit,
        "profile": "daily",
        "reason": str(reason or "GOSLO requested diary context")[:500],
        "result_channel": "diary_result",
        "source": "goslo_diary_query_request",
        "instructions": (
            "Read Markdown files under diary_root only. Treat profile=daily "
            "notes as diary entries. Do not read UUID-bound profile=ref files "
            "as diary entries; those are reference documents for L2-B binding. "
            "Return JSON with diary_root, entries, paths, highlights, and a "
            "short result_summary."
        ),
    }
    try:
        task_id = await dispatcher("diary_query", params, _priority(priority))
    except Exception as exc:
        logger.exception("diary_query_request dispatch failed")
        return (
            "Diary query dispatch failed "
            f"({type(exc).__name__}: {exc}). No Obsidian, Graphiti, or L2-B write occurred."
        )
    return (
        "Diary query dispatched to Nanobot "
        f"(task={task_id}, result_channel=diary_result, diary_root={root}, "
        f"date_from={start}, date_to={end}, limit={bounded_limit}). "
        "GOSLO can speak the returned result when Scheduler forwards the "
        "Nanobot feedback. No Obsidian, Graphiti, or L2-B write occurred."
    )


def _date_window(*, date_from: str, date_to: str) -> tuple[str, str]:
    if date_from.strip() or date_to.strip():
        return date_from.strip(), date_to.strip()
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=6)
    return start.isoformat(), end.isoformat()


def _diary_root(raw: str) -> Path:
    text = str(raw or "").strip()
    if text:
        return Path(text).expanduser().resolve()
    env = os.getenv("GOSLO_OBSIDIAN_DIARY_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    vault = os.getenv("GOSLO_OBSIDIAN_VAULT") or "D:/GOSLOParrot/GOSLObsidian"
    return (Path(vault).expanduser() / "Diary").resolve()


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _priority(value: str) -> str:
    selected = str(value or "high").strip().lower()
    return selected if selected in {"reflex", "high", "normal", "low"} else "high"


__all__ = ["diary_query_request", "do_diary_query_request"]
