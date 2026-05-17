"""T1 Calendar context tool for GOSLO Intent thinking.

GOSLO uses this tool when it needs schedule context before answering the user.
It is intentionally read-only: Google Calendar writes and L1.5/L2-B imports
must go through Plan/HITL or operator-gated routes.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from livekit.agents import RunContext, function_tool

logger = logging.getLogger(__name__)

CalendarFetcher = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


@function_tool()
async def calendar_context(
    context: RunContext,
    intent: str = "",
    date: str = "today",
    calendar_id: str = "primary",
    timezone: str = "Asia/Shanghai",
    limit: int = 8,
    fetch_source: str = "api",
    sync_policy: str = "preview",
) -> str:
    """Read Google Calendar context for GOSLO's current Intent turn.

    Category: T1 Intent / Thinking tool. Use this when GOSLO needs schedule
    context before replying, such as "what do I have today?", "can we fit this
    plan before dinner?", or "check my calendar before recommending a time."
    The tool may briefly block the turn in a natural thinking state.

    This tool is read-only. It never creates, patches, or deletes Google
    Calendar events; it never performs a direct L1.5 import; and it never writes
    L2-B or Graphiti. It returns a compact answer plus a source-to-DSG sync
    preview so GOSLO can reason about what would become L1.5 observations and
    L2-B event pointers later. For slow background fetches, use dispatch_task
    with task_type='calendar_fetch'. For Calendar write actions, create a
    Calendar change draft and require Plan/HITL approval before nanobot runs.

    Args:
        intent: Why GOSLO is checking the calendar in this conversational turn.
        date: Date to inspect. Supports 'today', 'tomorrow', 'yesterday', or
            an ISO date like '2026-05-18'.
        calendar_id: Google Calendar id, usually 'primary'.
        timezone: IANA timezone for date window calculation.
        limit: Maximum events to return, capped at 12 for a thinking turn.
        fetch_source: 'api' for official OAuth API, 'nanobot' for ECS Nanobot
            MCP read, or 'auto' to try API first then Nanobot.
        sync_policy: Currently only 'preview' is allowed. Other values are
            acknowledged but downgraded to preview.
    """

    return await do_calendar_context(
        intent=intent,
        date=date,
        calendar_id=calendar_id,
        timezone=timezone,
        limit=limit,
        fetch_source=fetch_source,
        sync_policy=sync_policy,
    )


async def do_calendar_context(
    *,
    intent: str = "",
    date: str = "today",
    calendar_id: str = "primary",
    timezone: str = "Asia/Shanghai",
    limit: int = 8,
    fetch_source: str = "api",
    sync_policy: str = "preview",
    api_fetcher: CalendarFetcher | None = None,
    nanobot_fetcher: CalendarFetcher | None = None,
) -> str:
    """Implementation helper kept separate for tests and future adapters."""

    bounded_limit = max(1, min(int(limit or 8), 12))
    source = str(fetch_source or "api").strip().lower()
    if source not in {"api", "nanobot", "auto"}:
        source = "api"
    payload = {
        "date": _resolve_date(date, timezone_name=timezone),
        "calendar_id": str(calendar_id or "primary"),
        "timezone": str(timezone or "Asia/Shanghai"),
        "limit": bounded_limit,
    }

    tried: list[str] = []
    receipt: dict[str, Any] | None = None
    source_used = source
    if source in {"api", "auto"}:
        tried.append("api")
        receipt = await _call_api_fetcher(payload, api_fetcher=api_fetcher)
        source_used = "api"
    if (source == "nanobot") or (
        source == "auto" and not _receipt_success(receipt)
    ):
        tried.append("nanobot")
        receipt = await _call_nanobot_fetcher(payload, nanobot_fetcher=nanobot_fetcher)
        source_used = "nanobot"

    if receipt is None:
        receipt = {
            "success": False,
            "data": {"error": "calendar_context_fetch_not_attempted", "events": []},
        }
    return format_calendar_context(
        receipt,
        intent=intent,
        requested_date=str(date or "today"),
        resolved_date=payload["date"],
        fetch_source=source_used,
        tried_sources=tried,
        sync_policy=sync_policy,
    )


def format_calendar_context(
    receipt: dict[str, Any],
    *,
    intent: str = "",
    requested_date: str = "today",
    resolved_date: str = "",
    fetch_source: str = "api",
    tried_sources: list[str] | None = None,
    sync_policy: str = "preview",
) -> str:
    """Render a compact, GOSLO-readable Calendar context string."""

    data = receipt.get("data") if isinstance(receipt, dict) else {}
    if not isinstance(data, dict):
        data = {}
    success = _receipt_success(receipt)
    error = str(data.get("error") or "").strip()
    read_model = str(data.get("read_model") or "Google Calendar read model").strip()
    count = int(data.get("count") or 0)
    events = _event_rows(data)
    mapping_rows = [row for row in data.get("mapping_rows", []) if isinstance(row, dict)]
    sync_policy_raw = str(sync_policy or "preview").strip().lower()
    sync_note = "preview_only"
    if sync_policy_raw not in {"", "preview", "draft"}:
        sync_note = f"requested_{sync_policy_raw}_downgraded_to_preview"

    if not success:
        return (
            "Calendar context unavailable "
            f"(T1 Intent/Thinking, source={fetch_source}, tried={','.join(tried_sources or [])}).\n"
            f"Reason: {error or 'unknown_error'}.\n"
            "No Google Calendar write, no L1.5 import, and no L2-B mutation occurred. "
            "If this context is not needed before replying, dispatch a background "
            "calendar_fetch task instead."
        )

    lines = [
        "Calendar context "
        f"(T1 Intent/Thinking, source={fetch_source}, {count or len(events)} event(s)).",
        f"Intent: {str(intent or 'schedule context check')[:180]}",
        f"Window: {requested_date or 'today'} -> {resolved_date or str(data.get('time_min') or '')}",
        f"Read model: {read_model}",
    ]
    if not events:
        lines.append("No events found in this window.")
    else:
        lines.append("Events:")
        for index, event in enumerate(events[:12], start=1):
            lines.append(f"{index}. {_event_summary(event)}")

    lines.append(
        "Memory buffer preview: "
        f"{len(mapping_rows)} L1.5 observation candidate(s), "
        "L2-B event pointer/tombstone policy available from mapping rows, "
        f"sync_policy={sync_note}."
    )
    lines.append(
        "No Google Calendar write, no L1.5 import, no L2-B mutation, and no "
        "Graphiti write occurred. Use Plan/HITL plus nanobot for create, patch, "
        "or delete."
    )
    return "\n".join(lines)


async def _call_api_fetcher(
    payload: dict[str, Any],
    *,
    api_fetcher: CalendarFetcher | None,
) -> dict[str, Any]:
    try:
        fetcher = api_fetcher
        if fetcher is None:
            from parrot.web_console.memory_ops import fetch_google_calendar_api

            fetcher = fetch_google_calendar_api
        return await fetcher(payload)
    except Exception as exc:
        logger.exception("calendar_context: API fetch failed")
        return {"success": False, "data": {"error": f"{type(exc).__name__}: {exc}", "events": []}}


async def _call_nanobot_fetcher(
    payload: dict[str, Any],
    *,
    nanobot_fetcher: CalendarFetcher | None,
) -> dict[str, Any]:
    try:
        fetcher = nanobot_fetcher
        if fetcher is None:
            from parrot.web_console.memory_ops import fetch_google_calendar_nanobot

            fetcher = fetch_google_calendar_nanobot
        return await fetcher(payload)
    except Exception as exc:
        logger.exception("calendar_context: Nanobot fetch failed")
        return {"success": False, "data": {"error": f"{type(exc).__name__}: {exc}", "events": []}}


def _resolve_date(date_text: str, *, timezone_name: str) -> str:
    raw = str(date_text or "today").strip()
    lowered = raw.lower()
    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        tz = ZoneInfo("UTC")
    today = datetime.now(tz).date()
    aliases = {
        "today": today,
        "tonight": today,
        "今天": today,
        "tomorrow": today + timedelta(days=1),
        "明天": today + timedelta(days=1),
        "yesterday": today - timedelta(days=1),
        "昨天": today - timedelta(days=1),
    }
    if lowered in aliases:
        return aliases[lowered].isoformat()
    try:
        return datetime.fromisoformat(raw).date().isoformat()
    except ValueError:
        logger.info("calendar_context: unparseable date %r, falling back to today", raw)
        return today.isoformat()


def _receipt_success(receipt: dict[str, Any] | None) -> bool:
    return bool(isinstance(receipt, dict) and receipt.get("success"))


def _event_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    normalized = data.get("normalized_events")
    if isinstance(normalized, list) and normalized:
        return [dict(item) for item in normalized if isinstance(item, dict)]
    events = data.get("events")
    if isinstance(events, list):
        return [dict(item) for item in events if isinstance(item, dict)]
    return []


def _event_summary(event: dict[str, Any]) -> str:
    title = str(event.get("title") or event.get("summary") or "Untitled event").strip()
    start = _time_label(event.get("start_time") or event.get("start"))
    end = _time_label(event.get("end_time") or event.get("end"))
    location = str(event.get("location") or "").strip()
    status = str(event.get("status") or "").strip()
    event_id = str(event.get("id") or event.get("calendar_event_id") or "").strip()
    pieces = [f"{start}-{end}" if end else start, title[:160]]
    if location:
        pieces.append(f"@ {location[:120]}")
    if status:
        pieces.append(f"status={status[:40]}")
    if event_id:
        pieces.append(f"id={event_id[:32]}")
    return " ".join(piece for piece in pieces if piece)


def _time_label(value: Any) -> str:
    if isinstance(value, dict):
        value = value.get("dateTime") or value.get("date") or ""
    text = str(value or "").strip()
    if not text:
        return "TBD"
    if len(text) == 10:
        return text
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return text[:32]
    return dt.strftime("%m-%d %H:%M")


__all__ = [
    "calendar_context",
    "do_calendar_context",
    "format_calendar_context",
]
