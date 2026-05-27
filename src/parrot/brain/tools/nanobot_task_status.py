"""Read-only Nanobot task/mission status tool for GOSLO."""

from __future__ import annotations

import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from livekit.agents import RunContext, function_tool

from parrot.scheduler.task_catalog import normalize_nanobot_task_type
from parrot.shared.constants import (
    CH_NANOBOT_RESULTS,
    STREAM_NANOBOT_DISPATCH,
    STREAM_NANOBOT_RESULTS,
    STREAM_TRIGGER_RESULTS,
)

logger = logging.getLogger(__name__)

StreamReader = Callable[[str, int], Awaitable[list[tuple[Any, dict[str, Any]]]]]


@function_tool()
async def nanobot_task_status(
    context: RunContext,
    task_id: str = "",
    task_type: str = "",
    limit: int = 8,
    include_payload: bool = False,
) -> str:
    """Check Nanobot background task or mission progress.

    Category: read-only Task-layer monitor. Use this when GOSLO has delegated a
    background Nanobot mission/task and wants to see whether it is pending,
    draft_ready, needs_user_decision, completed, or failed.

    This tool only reads bounded Scheduler/Nanobot ledgers. It never dispatches
    work, writes Google Calendar, calls MCP tools, imports L1.5, mutates L2-B,
    or writes Graphiti.
    """

    return await do_nanobot_task_status(
        task_id=task_id,
        task_type=task_type,
        limit=limit,
        include_payload=include_payload,
    )


async def do_nanobot_task_status(
    *,
    task_id: str = "",
    task_type: str = "",
    limit: int = 8,
    include_payload: bool = False,
    stream_reader: StreamReader | None = None,
) -> str:
    bounded_limit = max(1, min(_safe_int(limit, 8), 20))
    target_task_id = str(task_id or "").strip()
    target_task_type = _normalized_filter_task_type(task_type)

    try:
        reader = stream_reader or _default_stream_reader
        result_rows = await _read_result_rows(
            reader,
            limit=bounded_limit,
            task_id=target_task_id,
            task_type=target_task_type,
            include_payload=include_payload,
        )
        dispatch_rows = await _read_dispatch_rows(
            reader,
            limit=bounded_limit,
            task_id=target_task_id,
            task_type=target_task_type,
            include_payload=include_payload,
        )
    except Exception as exc:
        logger.info(
            "nanobot_task_status: status read unavailable: %s: %s",
            type(exc).__name__,
            exc,
        )
        return (
            "Nanobot task status unavailable "
            f"(read-only monitor): {type(exc).__name__}: {exc}. "
            "No task dispatch, external write, L1.5 import, L2-B mutation, "
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
            f"Nanobot task status: no recent row found for task={target_task_id}. "
            "It may be older than the bounded ledger, not yet routed, or not a "
            "Nanobot-routed task. GOSLO can continue naturally; no write or "
            "memory mutation occurred."
        )

    merged = _merge_recent_rows(result_rows, dispatch_rows, bounded_limit)
    if not merged:
        return (
            "Nanobot task status: no recent Nanobot task/result rows in the "
            "bounded ledgers. No dispatch, write, or memory mutation occurred."
        )

    lines = [f"Nanobot task status ({len(merged)} recent row(s), read-only monitor):"]
    for index, row in enumerate(merged, start=1):
        lines.append(f"{index}. {_compact_status_row(row)}")
    lines.append(
        "No task dispatch, external write, L1.5 import, L2-B mutation, or "
        "Graphiti write occurred in this status check."
    )
    return "\n".join(lines)


async def _default_stream_reader(stream: str, count: int) -> list[tuple[Any, dict[str, Any]]]:
    from parrot.shared.redis_client import get_redis

    redis = await get_redis()
    return list(await redis.xrevrange(stream, count=count))


async def _read_result_rows(
    reader: StreamReader,
    *,
    limit: int,
    task_id: str,
    task_type: str,
    include_payload: bool,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for stream in (STREAM_NANOBOT_RESULTS, STREAM_TRIGGER_RESULTS):
        raw_rows = await reader(stream, limit * 6)
        for stream_id, fields in raw_rows:
            row = _result_row_from_payload(
                stream=stream,
                stream_id=stream_id,
                fields=fields,
                task_id=task_id,
                task_type=task_type,
                include_payload=include_payload,
            )
            if not row:
                continue
            dedupe_key = (str(row.get("task_id") or ""), str(row.get("task_type") or ""))
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            rows.append(row)
            if len(rows) >= limit:
                return rows
    return rows


def _result_row_from_payload(
    *,
    stream: str,
    stream_id: Any,
    fields: dict[str, Any],
    task_id: str,
    task_type: str,
    include_payload: bool,
) -> dict[str, Any]:
    payload = _load_payload(_field(fields, "payload"))
    original_type = str(
        payload.get("original_type")
        or payload.get("task_type")
        or _field(fields, "task_type")
        or payload.get("type")
        or ""
    )
    params = payload.get("params") if isinstance(payload.get("params"), dict) else {}
    normalized_type = normalize_nanobot_task_type(original_type, params=params)
    result_channel = str(payload.get("result_channel") or _field(fields, "result_channel") or "")
    if stream == STREAM_TRIGGER_RESULTS and not result_channel:
        result_channel = str(payload.get("type") or "")
    if not normalized_type and result_channel != CH_NANOBOT_RESULTS:
        return {}
    row_task_id = str(payload.get("task_id") or _field(fields, "task_id") or "")
    if task_id and row_task_id != task_id:
        return {}
    if task_type and normalized_type != task_type:
        return {}
    decoded_result = _decoded_result(payload)
    status = str(payload.get("status") or decoded_result.get("status") or "completed")
    row: dict[str, Any] = {
        "kind": "result",
        "stream": stream,
        "stream_id": _decode(stream_id),
        "created_at": _field(fields, "created_at"),
        "task_id": row_task_id,
        "task_type": normalized_type or original_type,
        "result_channel": result_channel,
        "status": status,
        "decision_state": _decision_state(status, decoded_result),
        "summary": _result_summary(payload, decoded_result),
    }
    if include_payload:
        row["payload"] = _redact_payload(payload)
    return row


async def _read_dispatch_rows(
    reader: StreamReader,
    *,
    limit: int,
    task_id: str,
    task_type: str,
    include_payload: bool,
) -> list[dict[str, Any]]:
    raw_rows = await reader(STREAM_NANOBOT_DISPATCH, limit * 6)
    rows: list[dict[str, Any]] = []
    for stream_id, fields in raw_rows:
        payload = _load_payload(_field(fields, "payload"))
        raw_type = str(payload.get("type") or "")
        params = payload.get("params") if isinstance(payload.get("params"), dict) else {}
        normalized_type = normalize_nanobot_task_type(raw_type, params=params)
        if not normalized_type:
            continue
        row_task_id = str(payload.get("task_id") or "")
        if task_id and row_task_id != task_id:
            continue
        if task_type and normalized_type != task_type:
            continue
        row = {
            "kind": "dispatch",
            "stream": STREAM_NANOBOT_DISPATCH,
            "stream_id": _decode(stream_id),
            "task_id": row_task_id,
            "task_type": normalized_type,
            "requested_type": str(payload.get("requested_type") or params.get("requested_task_type") or raw_type),
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
        "Nanobot task status: result available.\n"
        f"Task: {row.get('task_id')} / {row.get('task_type') or 'nanobot task'} / {row.get('status')}.\n"
        f"Decision state: {row.get('decision_state') or 'none'}.\n"
        f"Result channel: {row.get('result_channel') or 'not declared'}.\n"
        f"Summary: {row.get('summary') or 'no summary'}.\n"
        "This status tool did not dispatch work, write external systems, import L1.5, mutate L2-B, or write Graphiti."
    )


def _format_single_dispatch(row: dict[str, Any]) -> str:
    return (
        "Nanobot task status: dispatched or pending.\n"
        f"Task: {row.get('task_id')} / {row.get('task_type')} / priority={row.get('priority') or 'normal'}.\n"
        f"Requested type: {row.get('requested_type') or row.get('task_type')}.\n"
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
            f"status={row.get('status') or '?'} decision={row.get('decision_state') or 'none'} "
            f"summary={row.get('summary') or ''}"
        ).strip()
    return (
        f"dispatch task={row.get('task_id') or '?'} type={row.get('task_type') or '?'} "
        f"status={row.get('status') or '?'} priority={row.get('priority') or 'normal'} "
        f"summary={row.get('summary') or ''}"
    ).strip()


def _decoded_result(payload: dict[str, Any]) -> dict[str, Any]:
    result = payload.get("result")
    if isinstance(result, dict):
        return dict(result)
    if isinstance(result, str) and result.strip():
        return _load_payload(result)
    return {}


def _result_summary(payload: dict[str, Any], decoded_result: dict[str, Any]) -> str:
    for source in (payload, decoded_result):
        summary = str(source.get("result_summary") or source.get("summary") or "").strip()
        if summary:
            return summary.replace("\n", " ")[:260]
    strategy = decoded_result.get("decision_strategy")
    if isinstance(strategy, dict) and strategy.get("summary"):
        return str(strategy["summary"]).replace("\n", " ")[:260]
    goal = str(decoded_result.get("goal") or "").strip()
    reason = str(decoded_result.get("reason") or "").strip()
    if goal or reason:
        return (goal + ("; " + reason if reason else "")).strip()[:260]
    result = payload.get("result")
    if isinstance(result, str) and result.strip():
        return result.replace("\n", " ")[:260]
    return str(payload.get("status") or "").strip()[:260]


def _decision_state(status: str, decoded_result: dict[str, Any]) -> str:
    normalized = str(status or decoded_result.get("status") or "").strip().lower()
    if normalized == "needs_user_decision":
        return str(decoded_result.get("reason") or "needs_user_decision")
    if decoded_result.get("requires_approval") is True:
        return "requires_approval"
    return ""


def _dispatch_summary(payload: dict[str, Any], params: dict[str, Any]) -> str:
    for key in ("goal", "mission", "query", "intent", "instructions"):
        text = str(params.get(key) or payload.get(key) or "").strip()
        if text:
            return text.replace("\n", " ")[:260]
    return str(payload.get("type") or "").strip()


def _normalized_filter_task_type(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    return normalize_nanobot_task_type(raw) or raw


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


def _redact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in payload.items():
        lowered = str(key).lower()
        if any(token in lowered for token in ("token", "secret", "credential", "authorization")):
            redacted[key] = "[redacted]"
        else:
            redacted[key] = value
    return redacted


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default


__all__ = ["nanobot_task_status", "do_nanobot_task_status"]
