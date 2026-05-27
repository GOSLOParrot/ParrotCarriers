"""GOSLO Calendar task/result status tool."""

from __future__ import annotations

import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from livekit.agents import RunContext, function_tool

from parrot.shared.constants import STREAM_NANOBOT_DISPATCH, STREAM_TRIGGER_RESULTS

logger = logging.getLogger(__name__)

StreamReader = Callable[[str, int], Awaitable[list[tuple[Any, dict[str, Any]]]]]

_CALENDAR_TASK_TYPES = {
    "calendar_fetch",
    "calendar_create",
    "calendar_patch",
    "calendar_delete",
    "calendar_mission",
}


@function_tool()
async def calendar_task_status(
    context: RunContext,
    task_id: str = "",
    limit: int = 8,
    include_payload: bool = False,
) -> str:
    """Check Calendar background task progress and recent results.

    Category: T1/T3 monitor tool. Use this when GOSLO has already dispatched a
    Calendar-related background task, or when a user asks whether the background
    Calendar check/write proposal has returned.

    Conversation blocking: brief. This tool only reads bounded Redis ledgers:
    the Nanobot dispatch stream and the Scheduler trigger-result stream. It
    does not wait for a task to finish.

    Write authority: none. It never writes Google Calendar, never dispatches a
    task, never imports L1.5, never mutates L2-B, and never writes Graphiti. If
    a completed write result should be synced into memory, that must happen via
    the CalendarTrigger/import policy or a later operator/HITL path.

    Args:
        task_id: Optional task id to find. Empty means show recent Calendar
            task/result rows.
        limit: Maximum rows to inspect and return, capped to 20.
        include_payload: Include compact redacted payload fields for debugging.
    """

    return await do_calendar_task_status(
        task_id=task_id,
        limit=limit,
        include_payload=include_payload,
    )


async def do_calendar_task_status(
    *,
    task_id: str = "",
    limit: int = 8,
    include_payload: bool = False,
    stream_reader: StreamReader | None = None,
) -> str:
    bounded_limit = max(1, min(int(limit or 8), 20))
    target_task_id = str(task_id or "").strip()

    try:
        reader = stream_reader or _default_stream_reader
        result_rows = await _read_calendar_result_rows(
            reader,
            limit=bounded_limit,
            task_id=target_task_id,
            include_payload=include_payload,
        )
        dispatch_rows = await _read_calendar_dispatch_rows(
            reader,
            limit=bounded_limit,
            task_id=target_task_id,
            include_payload=include_payload,
        )
    except Exception as exc:
        logger.info(
            "calendar_task_status: status read unavailable: %s: %s",
            type(exc).__name__,
            exc,
        )
        return (
            "Calendar task status unavailable "
            f"(T1/T3 monitor): {type(exc).__name__}: {exc}. "
            "No Google Calendar write, Nanobot dispatch, L1.5 import, L2-B mutation, "
            "or Graphiti write occurred."
        )

    if target_task_id:
        result = next((row for row in result_rows if row.get("task_id") == target_task_id), None)
        if result:
            return _format_single_result(result)
        dispatch = next((row for row in dispatch_rows if row.get("task_id") == target_task_id), None)
        if dispatch:
            return _format_single_dispatch(dispatch)
        return (
            f"Calendar task status: no recent row found for task={target_task_id}. "
            "It may be older than the bounded ledger, not yet routed, or not a Calendar task. "
            "GOSLO should not block the conversation while waiting. No write or memory mutation occurred."
        )

    merged = _merge_recent_rows(result_rows, dispatch_rows, bounded_limit)
    if not merged:
        return (
            "Calendar task status: no recent Calendar task/result rows in the bounded ledgers. "
            "No write or memory mutation occurred."
        )

    lines = [
        f"Calendar task status ({len(merged)} recent row(s), read-only T1/T3 monitor):"
    ]
    for index, row in enumerate(merged, start=1):
        lines.append(f"{index}. {_compact_status_row(row)}")
    lines.append(
        "No Google Calendar write, Nanobot dispatch, L1.5 import, L2-B mutation, "
        "or Graphiti write occurred in this status check."
    )
    return "\n".join(lines)


async def _default_stream_reader(stream: str, count: int) -> list[tuple[Any, dict[str, Any]]]:
    from parrot.shared.redis_client import get_redis

    redis = await get_redis()
    return list(await redis.xrevrange(stream, count=count))


async def _read_calendar_result_rows(
    reader: StreamReader,
    *,
    limit: int,
    task_id: str,
    include_payload: bool,
) -> list[dict[str, Any]]:
    raw_rows = await reader(STREAM_TRIGGER_RESULTS, limit * 4)
    rows: list[dict[str, Any]] = []
    for stream_id, fields in raw_rows:
        payload = _load_payload(_field(fields, "payload"))
        if str(payload.get("type") or "") != "calendar_result":
            continue
        row_task_id = str(payload.get("task_id") or _field(fields, "task_id") or "")
        if task_id and row_task_id != task_id:
            continue
        events = _events_from_payload(payload)
        row: dict[str, Any] = {
            "kind": "result",
            "stream": STREAM_TRIGGER_RESULTS,
            "stream_id": _decode(stream_id),
            "created_at": _field(fields, "created_at"),
            "task_id": row_task_id,
            "task_type": str(payload.get("original_type") or ""),
            "status": str(payload.get("status") or "completed"),
            "event_count": len(events),
            "summary": _result_summary(payload, events),
        }
        if include_payload:
            row["payload"] = _redact_payload(payload)
        rows.append(row)
        if len(rows) >= limit:
            break
    return rows


async def _read_calendar_dispatch_rows(
    reader: StreamReader,
    *,
    limit: int,
    task_id: str,
    include_payload: bool,
) -> list[dict[str, Any]]:
    raw_rows = await reader(STREAM_NANOBOT_DISPATCH, limit * 4)
    rows: list[dict[str, Any]] = []
    for stream_id, fields in raw_rows:
        payload = _load_payload(_field(fields, "payload"))
        task_type = str(payload.get("type") or "")
        if task_type not in _CALENDAR_TASK_TYPES:
            continue
        row_task_id = str(payload.get("task_id") or "")
        if task_id and row_task_id != task_id:
            continue
        params = payload.get("params") if isinstance(payload.get("params"), dict) else {}
        row = {
            "kind": "dispatch",
            "stream": STREAM_NANOBOT_DISPATCH,
            "stream_id": _decode(stream_id),
            "task_id": row_task_id,
            "task_type": task_type,
            "priority": str(payload.get("priority") or ""),
            "status": "dispatched_or_pending",
            "result_channel": str(params.get("result_channel") or ""),
            "summary": _dispatch_summary(payload, params),
        }
        if include_payload:
            row["payload"] = _redact_payload(payload)
        rows.append(row)
        if len(rows) >= limit:
            break
    return rows


def _format_single_result(row: dict[str, Any]) -> str:
    return (
        "Calendar task status: result available.\n"
        f"Task: {row.get('task_id')} / {row.get('task_type') or 'calendar task'} / {row.get('status')}.\n"
        f"Events: {row.get('event_count', 0)}.\n"
        f"Summary: {row.get('summary') or 'no summary'}.\n"
        "This status tool did not write Calendar, dispatch work, import L1.5, mutate L2-B, or write Graphiti."
    )


def _format_single_dispatch(row: dict[str, Any]) -> str:
    return (
        "Calendar task status: dispatched or pending.\n"
        f"Task: {row.get('task_id')} / {row.get('task_type')} / priority={row.get('priority') or 'normal'}.\n"
        f"Result channel: {row.get('result_channel') or 'not declared'}.\n"
        f"Summary: {row.get('summary') or 'waiting for result'}.\n"
        "GOSLO can continue the conversation and check again later."
    )


def _merge_recent_rows(
    results: list[dict[str, Any]],
    dispatches: list[dict[str, Any]],
    limit: int,
) -> list[dict[str, Any]]:
    seen_result_tasks = {str(row.get("task_id") or "") for row in results}
    merged = list(results)
    for row in dispatches:
        task_id = str(row.get("task_id") or "")
        if task_id and task_id in seen_result_tasks:
            continue
        merged.append(row)
    return merged[:limit]


def _compact_status_row(row: dict[str, Any]) -> str:
    if row.get("kind") == "result":
        return (
            f"result task={row.get('task_id') or '?'} type={row.get('task_type') or '?'} "
            f"status={row.get('status') or '?'} events={row.get('event_count', 0)} "
            f"summary={row.get('summary') or ''}"
        ).strip()
    return (
        f"dispatch task={row.get('task_id') or '?'} type={row.get('task_type') or '?'} "
        f"status={row.get('status') or '?'} priority={row.get('priority') or 'normal'} "
        f"summary={row.get('summary') or ''}"
    ).strip()


def _field(fields: dict[str, Any], key: str) -> Any:
    value = fields.get(key)
    if value is None:
        value = fields.get(key.encode("utf-8"))
    return _decode(value)


def _decode(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _load_payload(raw: Any) -> dict[str, Any]:
    raw = _decode(raw)
    if isinstance(raw, dict):
        return dict(raw)
    if not isinstance(raw, str) or not raw.strip():
        return {}
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError:
        return {"result": raw}
    return dict(decoded) if isinstance(decoded, dict) else {"result": decoded}


def _events_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[Any] = [
        payload.get("events"),
        payload.get("normalized_events"),
    ]
    result = payload.get("result")
    if isinstance(result, str):
        result = _load_payload(result)
    if isinstance(result, dict):
        candidates.extend([
            result.get("events"),
            result.get("normalized_events"),
            result.get("items"),
        ])
    for candidate in candidates:
        if isinstance(candidate, list):
            return [dict(item) for item in candidate if isinstance(item, dict)]
    return []


def _result_summary(payload: dict[str, Any], events: list[dict[str, Any]]) -> str:
    summary = str(payload.get("summary") or "").strip()
    if summary:
        return summary[:220]
    if events:
        titles = [
            str(event.get("title") or event.get("summary") or event.get("id") or "")
            for event in events[:3]
        ]
        return ", ".join(item for item in titles if item)[:220]
    result = payload.get("result")
    if isinstance(result, str) and result.strip():
        return result.replace("\n", " ")[:220]
    return str(payload.get("status") or "").strip()[:220]


def _dispatch_summary(payload: dict[str, Any], params: dict[str, Any]) -> str:
    intent = str(params.get("intent") or "").strip()
    if intent:
        return intent[:220]
    instructions = str(params.get("instructions") or "").strip()
    if instructions:
        return instructions.replace("\n", " ")[:220]
    return str(payload.get("type") or "").strip()


def _redact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in payload.items():
        lowered = str(key).lower()
        if any(token in lowered for token in ("token", "secret", "credential", "authorization")):
            redacted[key] = "[redacted]"
        else:
            redacted[key] = value
    return redacted


__all__ = ["calendar_task_status", "do_calendar_task_status"]
