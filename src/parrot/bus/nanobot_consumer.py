"""Nanobot task consumer — Path B (L2-only) stub for testing.

This runs inside ParrotCarriers (not inside the nanobot fork).
It mounts as a L2-only worker, reads tasks from Redis Stream, and publishes
Nanobot-shaped task results. Most task types remain lightweight local
fallbacks, while Google Calendar create/patch/delete uses the real Calendar API
when the task carries Plan/HITL or operator approval metadata.

Roles:
  - Integration tests: proves the dispatch→consume→result chain works
  - Fallback: runs when the real nanobot gateway isn't available

For real task processing, use the nanobot gateway with the parrot_bus channel:
  GOSLOParrot/nanobot → nanobot/channels/parrot_bus.py
  Start with: python src/scripts/start_nanobot_worker.py
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from parrot.bus.manifest import ModuleManifest
from parrot.bus.mounting import ModuleMount
from parrot.shared.constants import CH_NANOBOT_RESULTS, STREAM_NANOBOT_DISPATCH
from parrot.shared.redis_client import get_redis
from parrot.shared.types import Layer, ModuleType

logger = logging.getLogger(__name__)

CONSUMER_GROUP = "nanobot-workers"
CONSUMER_NAME = "worker-0"
HEARTBEAT_KEY = "parrot:nanobot_heartbeat"
HEARTBEAT_FIELD = "main_worker"
HEARTBEAT_BUSY_FIELD = "main_worker_busy"


class NanobotConsumer:
    """L2-only worker that consumes tasks from the dispatch stream."""

    def __init__(self):
        self._manifest = ModuleManifest(
            module_id="nanobot-worker",
            module_type=ModuleType.WORKER,
            layers=[Layer.L2],
        )
        self._mount = ModuleMount(self._manifest)
        self._consumer_task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        logger.info("Nanobot consumer starting...")
        await self._mount.mount()
        await self._ensure_consumer_group()
        self._running = True
        self._consumer_task = asyncio.create_task(self._consume_loop())
        logger.info("Nanobot consumer running.")

    async def stop(self) -> None:
        self._running = False
        if self._consumer_task:
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass
        await self._mount.unmount()

    async def _ensure_consumer_group(self) -> None:
        """Create consumer group if it doesn't exist."""
        r = await get_redis()
        group = _consumer_group()
        try:
            await r.xgroup_create(STREAM_NANOBOT_DISPATCH, group, id="0", mkstream=True)
            logger.info("Consumer group '%s' created", group)
        except Exception:
            logger.debug("Consumer group '%s' already exists", group)

    async def _consume_loop(self) -> None:
        """Main loop: read from stream, process, ack, publish result."""
        r = await get_redis()
        while self._running:
            try:
                entries = await r.xreadgroup(
                    _consumer_group(),
                    CONSUMER_NAME,
                    {STREAM_NANOBOT_DISPATCH: ">"},
                    count=1,
                    block=5000,
                )
                if not entries:
                    continue

                for stream_name, messages in entries:
                    for msg_id, fields in messages:
                        await self._handle_task(r, msg_id, fields)

            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Error in consume loop")
                await asyncio.sleep(1)

    async def _handle_task(self, r, msg_id: str, fields: dict) -> None:
        """Process a single task and report the result."""
        raw = fields.get("payload", "{}")
        task = json.loads(raw)
        task_id = task.get("task_id", "unknown")
        task_type = task.get("type", "unknown")
        params = task.get("params", {})

        logger.info("Nanobot processing task: %s (id=%s)", task_type, task_id)
        await r.hset(HEARTBEAT_KEY, mapping={
            HEARTBEAT_FIELD: str(time.time()),
            HEARTBEAT_BUSY_FIELD: "1",
        })

        result = _task_result(task_id=task_id, task_type=task_type, params=params)

        result_channel = params.get("result_channel")
        if result_channel:
            # Keep the normal task type on the Nanobot result. Scheduler owns
            # trigger fan-out and rewrites ``type`` only on CH_TRIGGER_RESULTS.
            result["result_channel"] = result_channel

        await r.xack(STREAM_NANOBOT_DISPATCH, _consumer_group(), msg_id)
        await r.publish(CH_NANOBOT_RESULTS, json.dumps(result))
        await r.hset(HEARTBEAT_KEY, mapping={
            HEARTBEAT_FIELD: str(time.time()),
            HEARTBEAT_BUSY_FIELD: "0",
        })

        logger.info("Nanobot task completed: %s (id=%s) result_channel=%s",
                     task_type, task_id, result_channel or "(default)")


def _task_result(*, task_id: str, task_type: str, params: dict[str, Any]) -> dict[str, Any]:
    if task_type in {"nanobot_mission", "calendar_mission"}:
        return _mission_result(task_id=task_id, task_type=task_type, params=params)
    if task_type == "calendar_fetch":
        return _calendar_fetch_result(task_id=task_id, task_type=task_type, params=params)
    if task_type in {"calendar_create", "calendar_patch", "calendar_delete"}:
        return _calendar_write_result(task_id=task_id, task_type=task_type, params=params)
    if task_type == "message_check":
        return _message_check_result(task_id=task_id, task_type=task_type, params=params)
    if task_type == "remind":
        return _remind_result(task_id=task_id, task_type=task_type, params=params)
    if task_type == "diary_query":
        return _diary_query_result(task_id=task_id, task_type=task_type, params=params)
    if task_type == "ref_scan":
        return _ref_scan_result(task_id=task_id, task_type=task_type, params=params)
    return {
        "task_id": task_id,
        "type": task_type,
        "status": "completed",
        "result": f"[stub] Task '{task_type}' acknowledged (no real processing)",
        "completed_at": time.time(),
    }


def _consumer_group() -> str:
    configured = str(os.getenv("PARROT_NANOBOT_CONSUMER_GROUP") or "").strip()
    return configured or CONSUMER_GROUP


def _calendar_fetch_result(*, task_id: str, task_type: str, params: dict[str, Any]) -> dict[str, Any]:
    events, source_path, warning = _calendar_events_for_params(params)
    limit = _bounded_int(params.get("limit"), default=20, minimum=1, maximum=50)
    filtered = _filter_calendar_events(events, params=params)[:limit]
    body = {
        "status": "completed",
        "event_count": len(filtered),
        "events": filtered,
        "source": "fallback_demo_fixture" if source_path else "fallback_stub",
        "source_path": str(source_path) if source_path else "",
        "calendar_id": str(params.get("calendar_id") or params.get("calendarId") or "primary"),
        "time_min": str(params.get("time_min") or params.get("timeMin") or ""),
        "time_max": str(params.get("time_max") or params.get("timeMax") or ""),
        "timezone": str(params.get("timezone") or "Asia/Shanghai"),
        "warning": warning,
        "worker": "parrot_fallback_nanobot_consumer",
    }
    body["summary"] = _calendar_fetch_summary(body)
    return {
        "task_id": task_id,
        "type": task_type,
        "status": "completed",
        "result": json.dumps(body, ensure_ascii=False),
        "result_summary": body["summary"],
        "completed_at": time.time(),
    }


def _calendar_events_for_params(params: dict[str, Any]) -> tuple[list[dict[str, Any]], Path | None, str]:
    raw_events = params.get("events")
    if isinstance(raw_events, list):
        return (
            [_normalize_calendar_event(item, fallback_index=index) for index, item in enumerate(raw_events) if isinstance(item, dict)],
            None,
            "",
        )

    source_path = _calendar_fixture_path(params)
    if not source_path:
        return [], None, "no_demo_events_path_or_inline_events"
    try:
        raw = json.loads(source_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [], source_path, f"calendar_fixture_read_failed:{type(exc).__name__}"
    if isinstance(raw, dict):
        raw_events = raw.get("events")
    else:
        raw_events = raw
    if not isinstance(raw_events, list):
        return [], source_path, "calendar_fixture_has_no_events_list"
    return (
        [_normalize_calendar_event(item, fallback_index=index) for index, item in enumerate(raw_events) if isinstance(item, dict)],
        source_path,
        "",
    )


def _calendar_fixture_path(params: dict[str, Any]) -> Path | None:
    raw = (
        params.get("demo_events_path")
        or params.get("fixture_path")
        or params.get("events_path")
        or os.getenv("PARROT_CALENDAR_DEMO_EVENTS_PATH")
        or ""
    )
    text = str(raw or "").strip()
    if not text:
        return None
    try:
        return Path(text).expanduser().resolve()
    except OSError:
        return Path(text).expanduser()


def _normalize_calendar_event(event: dict[str, Any], *, fallback_index: int) -> dict[str, Any]:
    start = event.get("start")
    end = event.get("end")
    start_time = str(
        event.get("start_time")
        or (start.get("dateTime") if isinstance(start, dict) else "")
        or (start.get("date") if isinstance(start, dict) else "")
        or start
        or ""
    )
    end_time = str(
        event.get("end_time")
        or (end.get("dateTime") if isinstance(end, dict) else "")
        or (end.get("date") if isinstance(end, dict) else "")
        or end
        or ""
    )
    title = str(event.get("title") or event.get("summary") or event.get("label") or f"calendar event {fallback_index + 1}")
    normalized = dict(event)
    normalized["id"] = str(event.get("id") or event.get("calendar_event_id") or f"demo_event_{fallback_index + 1}")
    normalized["calendar_id"] = str(event.get("calendar_id") or event.get("calendarId") or "primary")
    normalized["title"] = title
    normalized["summary"] = str(event.get("summary") or title)
    normalized["start_time"] = start_time
    normalized["end_time"] = end_time
    normalized.setdefault("status", "confirmed")
    normalized.setdefault("html_link", str(event.get("htmlLink") or event.get("html_link") or "https://calendar.google.com/"))
    return normalized


def _filter_calendar_events(events: list[dict[str, Any]], *, params: dict[str, Any]) -> list[dict[str, Any]]:
    time_min = _parse_isoish_datetime(params.get("time_min") or params.get("timeMin"))
    time_max = _parse_isoish_datetime(params.get("time_max") or params.get("timeMax"))
    rows: list[dict[str, Any]] = []
    for event in events:
        start = _parse_isoish_datetime(event.get("start_time") or _calendar_start_from_event(event))
        if time_min and start and _datetime_before(start, time_min):
            continue
        if time_max and start and not _datetime_before(start, time_max):
            continue
        rows.append(event)
    rows.sort(key=lambda item: str(item.get("start_time") or _calendar_start_from_event(item) or ""))
    return rows


def _calendar_start_from_event(event: dict[str, Any]) -> str:
    start = event.get("start")
    if isinstance(start, dict):
        return str(start.get("dateTime") or start.get("date") or "")
    return str(start or "")


def _calendar_end_from_event(event: dict[str, Any]) -> str:
    end = event.get("end")
    if isinstance(end, dict):
        return str(end.get("dateTime") or end.get("date") or "")
    return str(end or "")


def _calendar_time_text(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("dateTime") or value.get("date") or "")
    return str(value or "")


def _datetime_before(left: datetime, right: datetime) -> bool:
    try:
        return left < right
    except TypeError:
        return left.replace(tzinfo=None) < right.replace(tzinfo=None)


def _datetime_ranges_overlap(
    left_start: datetime,
    left_end: datetime,
    right_start: datetime,
    right_end: datetime,
) -> bool:
    try:
        return left_start < right_end and right_start < left_end
    except TypeError:
        ls = left_start.replace(tzinfo=None)
        le = left_end.replace(tzinfo=None)
        rs = right_start.replace(tzinfo=None)
        re = right_end.replace(tzinfo=None)
        return ls < re and rs < le


def _parse_isoish_datetime(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        try:
            return datetime.fromisoformat(text[:10])
        except ValueError:
            return None


def _calendar_fetch_summary(body: dict[str, Any]) -> str:
    events = [item for item in body.get("events", []) if isinstance(item, dict)]
    if not events:
        warning = str(body.get("warning") or "").strip()
        return "Calendar query returned no events" + (f" ({warning})" if warning else ".")
    parts = []
    for event in events[:4]:
        title = str(event.get("title") or event.get("summary") or event.get("id") or "event")
        start = str(event.get("start_time") or _calendar_start_from_event(event) or "")
        parts.append(f"{start[:16]} {title}".strip())
    return f"Calendar query found {len(events)} event(s): " + "; ".join(parts)


def _mission_result(*, task_id: str, task_type: str, params: dict[str, Any]) -> dict[str, Any]:
    domain = str(params.get("domain") or ("calendar" if task_type == "calendar_mission" else "general")).strip().lower()
    if domain == "calendar" or task_type == "calendar_mission":
        return _calendar_mission_result(task_id=task_id, task_type=task_type, params=params)
    return _generic_mission_result(task_id=task_id, task_type=task_type, params=params)


def _calendar_mission_result(*, task_id: str, task_type: str, params: dict[str, Any]) -> dict[str, Any]:
    authority = _mission_authority(params)
    mode = _mission_mode(params)
    events, source_path, warning = _calendar_events_for_params(params)
    limit = _bounded_int(params.get("limit"), default=12, minimum=1, maximum=50)
    filtered = _filter_calendar_events(events, params=params)[:limit]
    proposed_write = _mission_proposed_write(params)
    conflicts = _calendar_mission_conflicts(proposed_write=proposed_write, events=filtered)
    options = _calendar_mission_options(
        params=params,
        proposed_write=proposed_write,
        conflicts=conflicts,
    )
    requires_approval = _calendar_mission_requires_approval(
        authority=authority,
        proposed_write=proposed_write,
        params=params,
    )
    conflict_override_approved = _calendar_mission_conflict_override_approved(params)
    conflicts_blocked = bool(conflicts) and not conflict_override_approved
    status = "needs_user_decision" if requires_approval or conflicts_blocked else "draft_ready"
    write_result: dict[str, Any] | None = None
    write_body: dict[str, Any] = {}
    write_task_type = ""
    if _calendar_mission_can_execute_write(
        authority=authority,
        proposed_write=proposed_write,
        conflicts_blocked=conflicts_blocked,
        params=params,
    ):
        write_task_type, write_result = _calendar_mission_execute_write(
            task_id=task_id,
            params=params,
            proposed_write=proposed_write,
        )
        write_body = _json_result_body(write_result)
        status = str(write_result.get("status") or write_body.get("status") or "failed")
    body = {
        "schema": "nanobot_mission_result_v1",
        "status": status,
        "domain": "calendar",
        "goal": str(params.get("goal") or params.get("query") or params.get("instructions") or ""),
        "mode": mode,
        "collaboration_mode": mode,
        "authority": authority,
        "workflow_hint": str(params.get("workflow_hint") or ""),
        "workflow": _mission_workflow(params),
        "hitl_policy": str(params.get("hitl_policy") or "ask_before_calendar_write"),
        "nanobot_capabilities": _mission_capability_profile(
            domain="calendar",
            mode=mode,
            authority=authority,
        ),
        "investigation_trace": _calendar_mission_investigation_trace(
            params=params,
            events=filtered,
            conflicts=conflicts,
            proposed_write=proposed_write,
            requires_approval=requires_approval,
            status=status,
        ),
        "workflow_phase_results": _calendar_mission_phase_results(
            params=params,
            events=filtered,
            conflicts=conflicts,
            proposed_write=proposed_write,
            requires_approval=requires_approval,
            status=status,
        ),
        "decision_strategy": _calendar_mission_decision_strategy(
            mode=mode,
            authority=authority,
            proposed_write=proposed_write,
            conflicts=conflicts,
            conflicts_blocked=conflicts_blocked,
            requires_approval=requires_approval,
            status=status,
        ),
        "findings": _calendar_mission_findings(
            events=filtered,
            warning=warning,
            source_path=source_path,
        ),
        "conflicts": conflicts,
        "conflict_override_approved": conflict_override_approved,
        "options": options,
        "recommended_option": options[0]["id"] if options else "",
        "proposed_write": proposed_write,
        "requires_approval": requires_approval,
        "execution_policy": (
            "approved_calendar_write_performed"
            if status == "completed" and write_result
            else "approved_calendar_write_failed"
            if status == "failed" and write_result
            else "mission_paused_for_conflict_decision"
            if conflicts_blocked
            else "mission_reports_only_until_approved"
            if requires_approval
            else "draft_only_no_external_write"
        ),
        "events": filtered,
        "calendar_id": str(params.get("calendar_id") or params.get("calendarId") or "primary"),
        "worker": "parrot_fallback_nanobot_consumer",
        "source": "fallback_agentic_calendar_mission",
    }
    if write_result is not None:
        body["write_task_type"] = write_task_type
        body["write_result"] = write_body
        body["events"] = write_body.get("events") if isinstance(write_body.get("events"), list) else filtered
        body["event"] = write_body.get("event") if isinstance(write_body.get("event"), dict) else {}
        body["event_id"] = str(write_body.get("event_id") or "")
    if status == "needs_user_decision":
        body["reason"] = _calendar_mission_decision_reason(conflicts=conflicts, requires_approval=requires_approval)
        summary = _calendar_mission_needs_decision_summary(body)
    elif status == "completed" and write_result is not None:
        body["reason"] = ""
        summary = _calendar_mission_completed_summary(body)
    elif status == "failed" and write_result is not None:
        body["reason"] = str(write_body.get("error") or write_result.get("error") or "calendar_write_failed")
        summary = _calendar_mission_failed_summary(body)
    else:
        body["reason"] = ""
        summary = _calendar_mission_draft_summary(body)
    body["summary"] = summary
    return {
        "task_id": task_id,
        "type": task_type,
        "status": status,
        "result": json.dumps(body, ensure_ascii=False),
        "result_summary": summary,
        "completed_at": time.time(),
    }


def _generic_mission_result(*, task_id: str, task_type: str, params: dict[str, Any]) -> dict[str, Any]:
    mode = _mission_mode(params)
    authority = _mission_authority(params)
    workflow = _mission_workflow(params)
    goal = str(params.get("goal") or params.get("query") or params.get("instructions") or "")
    body = {
        "schema": "nanobot_mission_result_v1",
        "status": "draft_ready",
        "domain": str(params.get("domain") or "general"),
        "goal": goal,
        "mode": mode,
        "collaboration_mode": mode,
        "authority": authority,
        "workflow_hint": str(params.get("workflow_hint") or ""),
        "workflow": workflow,
        "nanobot_capabilities": _mission_capability_profile(
            domain=str(params.get("domain") or "general"),
            mode=mode,
            authority=authority,
        ),
        "investigation_trace": _generic_mission_investigation_trace(params),
        "workflow_phase_results": _generic_mission_phase_results(params),
        "decision_strategy": {
            "mode": mode,
            "summary": (
                "Fallback worker accepted the natural-language mission and "
                "returned a structured draft. Real upstream Nanobot owns "
                "LLM/tool-loop investigation for non-calendar domains."
            ),
        },
        "findings": [
            {
                "kind": "fallback_notice",
                "summary": (
                    "Local fallback accepted this mission as a structured Nanobot "
                    "mission. Full self-directed tool use belongs to the upstream "
                    "Nanobot worker."
                ),
            }
        ],
        "conflicts": [],
        "options": [],
        "recommended_option": "",
        "requires_approval": False,
        "execution_policy": "fallback_reports_only_no_external_write",
        "worker": "parrot_fallback_nanobot_consumer",
        "source": "fallback_agentic_mission",
    }
    summary = "Nanobot mission draft ready: " + (goal[:120] or "general mission")
    body["summary"] = summary
    return {
        "task_id": task_id,
        "type": task_type,
        "status": "draft_ready",
        "result": json.dumps(body, ensure_ascii=False),
        "result_summary": summary,
        "completed_at": time.time(),
    }


def _mission_authority(params: dict[str, Any]) -> str:
    raw = str(params.get("authority") or params.get("permission") or "draft_only").strip().lower()
    if raw in {"read_only", "draft_only", "approved_write", "operator_write"}:
        return raw
    return "draft_only"


def _mission_mode(params: dict[str, Any]) -> str:
    raw = str(params.get("mode") or params.get("collaboration_mode") or "flexible").strip().lower().replace("-", "_")
    aliases = {
        "guided": "guided_workflow",
        "workflow": "guided_workflow",
        "strict": "guided_workflow",
        "agentic": "flexible",
    }
    value = aliases.get(raw, raw)
    return value if value in {"flexible", "guided_workflow"} else "flexible"


def _mission_workflow(params: dict[str, Any]) -> dict[str, Any] | list[Any]:
    workflow = params.get("workflow")
    if isinstance(workflow, (dict, list)):
        return workflow
    text = str(workflow or "").strip()
    if not text:
        return {}
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text}
    return decoded if isinstance(decoded, (dict, list)) else {"value": decoded}


def _mission_capability_profile(*, domain: str, mode: str, authority: str) -> dict[str, Any]:
    can_write = authority in {"approved_write", "operator_write"}
    calendar_domain = str(domain or "").strip().lower() in {"calendar", "google_calendar", "schedule", "scheduling"}
    return {
        "natural_language_mission": True,
        "self_investigation": True,
        "tool_use_within_allowlist": True,
        "mcp_tool_use_when_available": True,
        "api_tool_use_when_available": True,
        "subtask_or_subagent_delegation": True,
        "workflow_guided": mode == "guided_workflow",
        "workflow_is_guidance_not_fixed_pipeline": True,
        "can_pause_for_human_decision": True,
        "can_resume_after_human_decision": True,
        "can_report_progress_or_partial_findings": True,
        "external_write_allowed_after_approval": can_write,
        "calendar_conflict_analysis": calendar_domain,
        "calendar_write_actuator_available": calendar_domain and can_write,
    }


def _calendar_mission_investigation_trace(
    *,
    params: dict[str, Any],
    events: list[dict[str, Any]],
    conflicts: list[dict[str, Any]],
    proposed_write: dict[str, Any],
    requires_approval: bool,
    status: str,
) -> list[dict[str, Any]]:
    trace: list[dict[str, Any]] = [
        {
            "phase": "understand_goal",
            "status": "completed",
            "summary": str(params.get("goal") or params.get("query") or "Calendar mission accepted")[:240],
        },
        {
            "phase": "inspect_calendar_context",
            "status": "completed",
            "summary": f"Reviewed {len(events)} event(s) in the available Calendar context.",
        },
        {
            "phase": "detect_conflicts",
            "status": "completed",
            "summary": f"Detected {len(conflicts)} blocking time conflict(s).",
        },
    ]
    if proposed_write:
        trace.append({
            "phase": "shape_proposed_write",
            "status": "completed",
            "summary": "Prepared a Calendar write payload candidate inside the mission result.",
        })
    if requires_approval:
        trace.append({
            "phase": "approval_boundary",
            "status": "needs_user_decision",
            "summary": "External Calendar write requires explicit user/HITL/operator approval.",
        })
    elif status == "completed":
        trace.append({
            "phase": "approved_execution",
            "status": "completed",
            "summary": "Approval metadata was present, so Nanobot called the Calendar write actuator.",
        })
    else:
        trace.append({
            "phase": "report",
            "status": status,
            "summary": "Mission returned structured findings without performing an external write.",
        })
    return trace


def _calendar_mission_phase_results(
    *,
    params: dict[str, Any],
    events: list[dict[str, Any]],
    conflicts: list[dict[str, Any]],
    proposed_write: dict[str, Any],
    requires_approval: bool,
    status: str,
) -> list[dict[str, Any]]:
    workflow = _mission_workflow(params)
    steps = _mission_workflow_steps(workflow)
    if not steps:
        steps = [
            "understand_goal",
            "inspect_calendar_context",
            "detect_conflicts",
            "propose_options",
            "pause_or_execute",
        ]
    phase_results: list[dict[str, Any]] = []
    for index, step in enumerate(steps):
        step_id = _workflow_step_id(step, index)
        phase_status = "completed"
        summary = "Completed under fallback deterministic mission handling."
        if step_id in {"inspect_calendar", "inspect_calendar_context", "calendar_context", "list_events"}:
            summary = f"Reviewed {len(events)} event(s)."
        elif step_id in {"detect_conflicts", "conflict_check", "check_conflicts"}:
            summary = f"Found {len(conflicts)} conflict(s)."
        elif step_id in {"propose_options", "rank_options", "shape_proposed_write"}:
            summary = "Prepared options" + (" with a proposed Calendar write." if proposed_write else ".")
        elif step_id in {"wait_for_approval", "pause_for_hitl", "pause_or_execute"}:
            phase_status = "needs_user_decision" if requires_approval or status == "needs_user_decision" else status
            summary = (
                "Paused for user/HITL decision."
                if phase_status == "needs_user_decision"
                else "No approval pause was needed."
            )
        elif step_id in {"execute", "approved_execution", "calendar_write"}:
            phase_status = "completed" if status == "completed" else "blocked"
            summary = (
                "Executed approved Calendar write."
                if status == "completed"
                else "Calendar write was not executed before approval/conflict resolution."
            )
        phase_results.append({
            "id": step_id,
            "label": _workflow_step_label(step, step_id),
            "status": phase_status,
            "summary": summary,
        })
    return phase_results


def _calendar_mission_decision_strategy(
    *,
    mode: str,
    authority: str,
    proposed_write: dict[str, Any],
    conflicts: list[dict[str, Any]],
    conflicts_blocked: bool,
    requires_approval: bool,
    status: str,
) -> dict[str, Any]:
    if status == "completed":
        next_action = "report_write_receipt"
    elif conflicts_blocked:
        next_action = "ask_user_to_resolve_conflict"
    elif requires_approval:
        next_action = "ask_user_to_approve_write"
    elif proposed_write:
        next_action = "return_draft_for_review"
    else:
        next_action = "continue_investigation_or_request_more_context"
    return {
        "mode": mode,
        "authority": authority,
        "conflict_count": len(conflicts),
        "has_proposed_write": bool(proposed_write),
        "requires_approval": requires_approval,
        "next_action": next_action,
        "summary": (
            "Flexible mission" if mode == "flexible" else "Workflow-guided mission"
        ) + f" selected next_action={next_action}.",
    }


def _generic_mission_investigation_trace(params: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "phase": "understand_goal",
            "status": "completed",
            "summary": str(params.get("goal") or params.get("query") or "Mission accepted")[:240],
        },
        {
            "phase": "fallback_boundary",
            "status": "draft_ready",
            "summary": (
                "Local fallback does not run the upstream LLM/tool loop for this "
                "domain; it preserves the agentic mission contract for the real worker."
            ),
        },
    ]


def _generic_mission_phase_results(params: dict[str, Any]) -> list[dict[str, Any]]:
    steps = _mission_workflow_steps(_mission_workflow(params))
    if not steps:
        return []
    return [
        {
            "id": _workflow_step_id(step, index),
            "label": _workflow_step_label(step, _workflow_step_id(step, index)),
            "status": "draft_ready",
            "summary": "Accepted as workflow guidance for upstream Nanobot execution.",
        }
        for index, step in enumerate(steps)
    ]


def _mission_workflow_steps(workflow: dict[str, Any] | list[Any]) -> list[Any]:
    if isinstance(workflow, list):
        return list(workflow)
    if not isinstance(workflow, dict):
        return []
    for key in ("steps", "phases", "nodes", "workflow"):
        value = workflow.get(key)
        if isinstance(value, list):
            return list(value)
    return []


def _workflow_step_id(step: Any, index: int) -> str:
    if isinstance(step, dict):
        raw = step.get("id") or step.get("step_id") or step.get("name") or step.get("title")
    else:
        raw = step
    text = str(raw or f"phase_{index + 1}").strip().lower()
    text = re.sub(r"[^a-z0-9_]+", "_", text)
    return text.strip("_") or f"phase_{index + 1}"


def _workflow_step_label(step: Any, fallback: str) -> str:
    if isinstance(step, dict):
        raw = step.get("label") or step.get("title") or step.get("name") or step.get("id")
    else:
        raw = step
    return str(raw or fallback).strip() or fallback


def _mission_proposed_write(params: dict[str, Any]) -> dict[str, Any]:
    for key in ("proposed_write", "calendar_write", "write", "event_patch", "event_body"):
        value = params.get(key)
        if isinstance(value, dict):
            return dict(value)
    details = _calendar_details(params)
    title = str(params.get("title") or params.get("summary") or details.get("title") or details.get("summary") or "").strip()
    start, end = _calendar_start_end_from_params(params, details=details)
    if not title and not start and not end:
        return {}
    return {
        "action": str(params.get("action") or "create"),
        "calendar_id": str(params.get("calendar_id") or params.get("calendarId") or "primary"),
        "event_id": str(params.get("event_id") or params.get("eventId") or ""),
        "event_body": {
            **({"summary": title} if title else {}),
            **({"start": start} if start else {}),
            **({"end": end} if end else {}),
            **({"location": details.get("location")} if details.get("location") else {}),
            **({"description": details.get("description")} if details.get("description") else {}),
        },
    }


def _calendar_mission_conflicts(
    *,
    proposed_write: dict[str, Any],
    events: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not proposed_write:
        return []
    body = proposed_write.get("event_body") if isinstance(proposed_write.get("event_body"), dict) else proposed_write
    start = _parse_isoish_datetime(_calendar_time_text(body.get("start") if isinstance(body, dict) else ""))
    end = _parse_isoish_datetime(_calendar_time_text(body.get("end") if isinstance(body, dict) else ""))
    if not start or not end:
        return []
    conflicts: list[dict[str, Any]] = []
    for event in events:
        event_start = _parse_isoish_datetime(event.get("start_time") or _calendar_start_from_event(event))
        event_end = _parse_isoish_datetime(event.get("end_time") or _calendar_end_from_event(event))
        if not event_start or not event_end:
            continue
        if _datetime_ranges_overlap(start, end, event_start, event_end):
            conflicts.append({
                "kind": "time_overlap",
                "event_id": str(event.get("id") or ""),
                "title": str(event.get("title") or event.get("summary") or ""),
                "start_time": str(event.get("start_time") or _calendar_start_from_event(event) or ""),
                "end_time": str(event.get("end_time") or _calendar_end_from_event(event) or ""),
                "severity": "hard",
            })
    return conflicts


def _calendar_mission_options(
    *,
    params: dict[str, Any],
    proposed_write: dict[str, Any],
    conflicts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    raw_options = params.get("options")
    if isinstance(raw_options, list) and raw_options:
        return [dict(item) for item in raw_options if isinstance(item, dict)]
    if not proposed_write:
        return [{
            "id": "investigate_more",
            "label": "Investigate more Calendar context before proposing a write",
            "requires_approval": False,
        }]
    return [{
        "id": "proceed_with_proposed_write",
        "label": "Use the proposed Calendar write payload",
        "requires_approval": True,
        "conflict_count": len(conflicts),
        "proposed_write": proposed_write,
    }]


def _calendar_mission_findings(
    *,
    events: list[dict[str, Any]],
    warning: str,
    source_path: Path | None,
) -> list[dict[str, Any]]:
    findings = [{
        "kind": "calendar_context",
        "event_count": len(events),
        "source": "fallback_demo_fixture" if source_path else "fallback_inline_or_stub",
        "summary": _calendar_fetch_summary({"events": events, "warning": warning}),
    }]
    if warning:
        findings.append({"kind": "warning", "summary": warning})
    return findings


def _calendar_mission_requires_approval(
    *,
    authority: str,
    proposed_write: dict[str, Any],
    params: dict[str, Any],
) -> bool:
    if not proposed_write:
        return False
    try:
        action = _calendar_mission_write_action(proposed_write.get("action") or "create")
    except ValueError:
        action = ""
    if action in {"create", "patch", "delete"}:
        return authority not in {"approved_write", "operator_write"} or not _calendar_write_is_approved(params)
    return False


def _calendar_mission_conflict_override_approved(params: dict[str, Any]) -> bool:
    for key in ("conflict_override_approved", "allow_conflicts", "override_conflicts"):
        if _boolish(params.get(key), False):
            return True
    selected = params.get("selected_option")
    if isinstance(selected, dict):
        for key in ("conflict_override_approved", "allow_conflicts", "override_conflicts"):
            if _boolish(selected.get(key), False):
                return True
        selected_id = str(selected.get("id") or selected.get("option_id") or "").strip().lower()
        try:
            conflict_count = int(selected.get("conflict_count") or 0)
        except (TypeError, ValueError):
            conflict_count = 1 if selected.get("conflict_count") else 0
        if conflict_count > 0 and selected_id in {
            "proceed_with_proposed_write",
            "proceed_despite_conflict",
            "override_conflict",
        }:
            return True
    return False


def _calendar_mission_can_execute_write(
    *,
    authority: str,
    proposed_write: dict[str, Any],
    conflicts_blocked: bool,
    params: dict[str, Any],
) -> bool:
    if not proposed_write or conflicts_blocked:
        return False
    if authority not in {"approved_write", "operator_write"}:
        return False
    return _calendar_write_is_approved(params)


def _calendar_mission_execute_write(
    *,
    task_id: str,
    params: dict[str, Any],
    proposed_write: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    try:
        task_type, write_params = _calendar_mission_write_task(
            params=params,
            proposed_write=proposed_write,
        )
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        action = str(proposed_write.get("action") or "write")
        return f"calendar_{action}", {
            "task_id": task_id,
            "type": f"calendar_{action}",
            "status": "failed",
            "result": json.dumps({
                "status": "failed",
                "action": action,
                "error": error,
                "source": "fallback_agentic_calendar_mission",
            }, ensure_ascii=False),
            "result_summary": f"Calendar mission write failed: {error}",
            "error": error,
            "completed_at": time.time(),
        }
    return task_type, _calendar_write_result(
        task_id=task_id,
        task_type=task_type,
        params=write_params,
    )


def _calendar_mission_write_task(
    *,
    params: dict[str, Any],
    proposed_write: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    action = _calendar_mission_write_action(proposed_write.get("action") or params.get("action") or "create")
    event_body = proposed_write.get("event_body")
    if not isinstance(event_body, dict):
        event_body = proposed_write.get("event")
    if not isinstance(event_body, dict):
        event_body = proposed_write.get("patch")
    write_params = dict(params)
    write_params["calendar_id"] = str(
        proposed_write.get("calendar_id")
        or proposed_write.get("calendarId")
        or params.get("calendar_id")
        or params.get("calendarId")
        or "primary"
    )
    event_id = str(
        proposed_write.get("event_id")
        or proposed_write.get("eventId")
        or params.get("event_id")
        or params.get("eventId")
        or ""
    ).strip()
    if event_id:
        write_params["event_id"] = event_id
    if isinstance(event_body, dict):
        write_params["event_body"] = dict(event_body)
        write_params.setdefault("title", str(event_body.get("summary") or event_body.get("title") or ""))
    if isinstance(proposed_write.get("details"), dict):
        write_params["details"] = dict(proposed_write["details"])
    write_params.setdefault("calendar_write_approved", True)
    write_params.setdefault("hitl_approved", True)
    write_params.setdefault("approval_source", "calendar_mission")
    return f"calendar_{action}", write_params


def _calendar_mission_write_action(value: Any) -> str:
    raw = str(value or "create").strip().lower()
    aliases = {
        "add": "create",
        "insert": "create",
        "new": "create",
        "edit": "patch",
        "update": "patch",
        "modify": "patch",
        "remove": "delete",
        "cancel": "delete",
    }
    action = aliases.get(raw, raw)
    if action not in {"create", "patch", "delete"}:
        raise ValueError(f"unsupported_calendar_write_action:{raw}")
    return action


def _json_result_body(result: dict[str, Any]) -> dict[str, Any]:
    raw = result.get("result")
    if isinstance(raw, dict):
        return dict(raw)
    if isinstance(raw, str) and raw.strip():
        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError:
            return {"raw": raw}
        return dict(decoded) if isinstance(decoded, dict) else {"result": decoded}
    return {}


def _calendar_mission_decision_reason(
    *,
    conflicts: list[dict[str, Any]],
    requires_approval: bool,
) -> str:
    if conflicts and requires_approval:
        return "calendar_conflict_and_write_approval_required"
    if conflicts:
        return "calendar_conflict_requires_user_decision"
    if requires_approval:
        return "calendar_write_requires_user_approval"
    return "user_decision_required"


def _calendar_mission_needs_decision_summary(body: dict[str, Any]) -> str:
    conflicts = [item for item in body.get("conflicts", []) if isinstance(item, dict)]
    options = [item for item in body.get("options", []) if isinstance(item, dict)]
    return (
        "Calendar mission needs user decision: "
        f"{len(conflicts)} conflict(s), {len(options)} option(s), "
        f"reason={body.get('reason') or 'approval_required'}"
    )


def _calendar_mission_completed_summary(body: dict[str, Any]) -> str:
    write_result = body.get("write_result") if isinstance(body.get("write_result"), dict) else {}
    write_summary = str(write_result.get("summary") or "").strip()
    event_id = str(write_result.get("event_id") or body.get("event_id") or "").strip()
    if write_summary:
        return f"Calendar mission completed write: {write_summary}"
    return "Calendar mission completed write" + (f": {event_id}" if event_id else ".")


def _calendar_mission_failed_summary(body: dict[str, Any]) -> str:
    reason = str(body.get("reason") or "calendar_write_failed")
    return f"Calendar mission failed during approved write: {reason}"


def _calendar_mission_draft_summary(body: dict[str, Any]) -> str:
    findings = [item for item in body.get("findings", []) if isinstance(item, dict)]
    return f"Calendar mission draft ready: {len(findings)} finding(s), no Calendar write performed"


def _calendar_write_result(*, task_id: str, task_type: str, params: dict[str, Any]) -> dict[str, Any]:
    action = task_type.removeprefix("calendar_")
    calendar_id = str(params.get("calendar_id") or params.get("calendarId") or "primary").strip() or "primary"
    try:
        if not _calendar_write_is_approved(params):
            raise ValueError(
                "calendar_write_not_approved: Calendar create/patch/delete requires "
                "Plan/HITL approval, operator_mode, or an explicit confirmation flag"
            )

        send_updates = _calendar_send_updates(params)
        if action == "create":
            request_body = _calendar_create_event_body(params)
            event_id = ""
            method = "POST"
        elif action == "patch":
            event_id = _calendar_event_id(params)
            request_body = _calendar_patch_event_body(params)
            method = "PATCH"
        elif action == "delete":
            event_id = _calendar_event_id(params)
            request_body = None
            method = "DELETE"
        else:
            raise ValueError(f"unsupported_calendar_write_action:{action}")

        query = _calendar_write_query_params(params, body=request_body)
        if send_updates:
            query["sendUpdates"] = send_updates

        dry_run = _boolish(params.get("dry_run"), False)
        if dry_run:
            api_event: dict[str, Any] = {}
            status_code = 0
            credential_source = "dry_run"
        else:
            api_event, status_code, credential_source = _calendar_google_api_request(
                method=method,
                calendar_id=calendar_id,
                event_id=event_id,
                body=request_body,
                query=query,
            )

        if action == "delete":
            normalized_event = _normalize_calendar_event(
                {
                    "id": event_id,
                    "calendar_id": calendar_id,
                    "summary": str(params.get("title") or params.get("summary") or "Deleted calendar event"),
                    "status": "cancelled",
                    "htmlLink": "",
                },
                fallback_index=0,
            )
            result_event_id = event_id
        else:
            normalized_event = _normalize_calendar_event(
                {**api_event, "calendar_id": str(api_event.get("calendar_id") or calendar_id)},
                fallback_index=0,
            )
            result_event_id = str(normalized_event.get("id") or api_event.get("id") or "")

        body = {
            "status": "completed",
            "action": action,
            "calendar_id": calendar_id,
            "event_id": result_event_id,
            "events": [normalized_event],
            "event": normalized_event,
            "api_status_code": status_code,
            "credential_source": credential_source,
            "dry_run": dry_run,
            "send_updates": send_updates or "",
            "write_model": f"Google Calendar API events.{action} via OAuth2",
            "source": "google_calendar_api",
            "worker": "parrot_fallback_nanobot_consumer",
            "sync_after_execution": [
                "calendar_result trigger ledger",
                "L1.5 GOOGLE_CALENDAR observation import",
                "L2-B event pointer projection",
            ],
        }
        if action != "delete":
            body["html_link"] = str(api_event.get("htmlLink") or api_event.get("html_link") or "")
            body["raw_event"] = api_event
        body["summary"] = _calendar_write_summary(body)
        return {
            "task_id": task_id,
            "type": task_type,
            "status": "completed",
            "result": json.dumps(body, ensure_ascii=False),
            "result_summary": body["summary"],
            "completed_at": time.time(),
        }
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        body = {
            "status": "failed",
            "action": action,
            "calendar_id": calendar_id,
            "event_id": str(params.get("event_id") or params.get("eventId") or ""),
            "events": [],
            "error": error,
            "source": "google_calendar_api",
            "worker": "parrot_fallback_nanobot_consumer",
            "write_model": f"Google Calendar API events.{action} via OAuth2",
        }
        return {
            "task_id": task_id,
            "type": task_type,
            "status": "failed",
            "result": json.dumps(body, ensure_ascii=False),
            "result_summary": f"Calendar {action} failed: {error}",
            "error": error,
            "completed_at": time.time(),
        }


def _calendar_write_is_approved(params: dict[str, Any]) -> bool:
    if _boolish(params.get("dry_run"), False):
        return True
    for key in (
        "calendar_write_approved",
        "hitl_approved",
        "plan_approved",
        "operator_mode",
        "user_confirmed",
        "confirmed_by_user",
        "confirmed",
    ):
        if _boolish(params.get(key), False):
            return True
    approval = params.get("approval")
    if isinstance(approval, dict):
        return any(
            _boolish(approval.get(key), False)
            for key in ("approved", "hitl_approved", "user_confirmed")
        )
    return False


def _calendar_event_id(params: dict[str, Any]) -> str:
    event_id = str(
        params.get("event_id")
        or params.get("eventId")
        or params.get("calendar_event_id")
        or ""
    ).strip()
    if not event_id:
        raise ValueError("missing_event_id")
    return event_id


def _calendar_create_event_body(params: dict[str, Any]) -> dict[str, Any]:
    details = _calendar_details(params)
    body = _calendar_base_event_body(params, details=details)
    summary = str(
        params.get("title")
        or params.get("summary")
        or details.get("title")
        or details.get("summary")
        or body.get("summary")
        or ""
    ).strip()
    if summary:
        body["summary"] = summary
    start, end = _calendar_start_end_from_params(params, details=details)
    body.setdefault("start", start)
    body.setdefault("end", end)
    missing = [key for key in ("summary", "start", "end") if not body.get(key)]
    if missing:
        raise ValueError(f"missing_create_event_fields:{','.join(missing)}")
    return body


def _calendar_patch_event_body(params: dict[str, Any]) -> dict[str, Any]:
    details = _calendar_details(params)
    body = _calendar_base_event_body(params, details=details)
    title = str(params.get("title") or params.get("summary") or "").strip()
    if title:
        body["summary"] = title
    start, end = _calendar_start_end_from_params(params, details=details)
    if start:
        body["start"] = start
    if end:
        body["end"] = end
    for key in ("id", "event_id", "eventId", "calendar_id", "calendarId"):
        body.pop(key, None)
    if not body:
        raise ValueError("missing_patch_event_fields")
    return body


def _calendar_base_event_body(
    params: dict[str, Any],
    *,
    details: dict[str, Any],
) -> dict[str, Any]:
    raw_body = (
        params.get("event_body")
        or params.get("event")
        or params.get("body")
        or params.get("patch")
        or params.get("event_patch")
    )
    source = dict(raw_body) if isinstance(raw_body, dict) else dict(details)
    allowed = {
        "anyoneCanAddSelf",
        "attachments",
        "attendees",
        "birthdayProperties",
        "colorId",
        "conferenceData",
        "description",
        "end",
        "eventType",
        "extendedProperties",
        "focusTimeProperties",
        "gadget",
        "guestsCanInviteOthers",
        "guestsCanModify",
        "guestsCanSeeOtherGuests",
        "id",
        "location",
        "outOfOfficeProperties",
        "recurrence",
        "reminders",
        "source",
        "start",
        "summary",
        "transparency",
        "visibility",
        "workingLocationProperties",
    }
    aliases = {
        "title": "summary",
        "start_time": "start",
        "startTime": "start",
        "end_time": "end",
        "endTime": "end",
    }
    body: dict[str, Any] = {}
    timezone_name = _calendar_timezone_name(params, details=details)
    for key, value in source.items():
        target = aliases.get(str(key), str(key))
        if target not in allowed:
            continue
        if target in {"start", "end"}:
            normalized_time = _calendar_time_object(value, timezone_name=timezone_name)
            if normalized_time:
                body[target] = normalized_time
            continue
        body[target] = value
    return body


def _calendar_details(params: dict[str, Any]) -> dict[str, Any]:
    details = params.get("details")
    if isinstance(details, dict):
        return dict(details)
    raw = params.get("details_json")
    if isinstance(raw, dict):
        return dict(raw)
    text = str(raw or "").strip()
    if not text:
        return {}
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return dict(decoded) if isinstance(decoded, dict) else {}


def _calendar_start_end_from_params(
    params: dict[str, Any],
    *,
    details: dict[str, Any],
) -> tuple[dict[str, str], dict[str, str]]:
    timezone_name = _calendar_timezone_name(params, details=details)
    start_raw = _first_calendar_value(
        params,
        details,
        ("start", "start_time", "startTime", "start_datetime", "startDateTime"),
    )
    end_raw = _first_calendar_value(
        params,
        details,
        ("end", "end_time", "endTime", "end_datetime", "endDateTime"),
    )
    if start_raw and end_raw:
        return (
            _calendar_time_object(start_raw, timezone_name=timezone_name),
            _calendar_time_object(end_raw, timezone_name=timezone_name),
        )
    parsed_start, parsed_end = _parse_calendar_time_range(
        str(params.get("time_range") or params.get("timeRange") or details.get("time_range") or ""),
        timezone_name=timezone_name,
    )
    if parsed_start and parsed_end:
        return (
            _calendar_time_object(parsed_start, timezone_name=timezone_name),
            _calendar_time_object(parsed_end, timezone_name=timezone_name),
        )
    return {}, {}


def _first_calendar_value(
    params: dict[str, Any],
    details: dict[str, Any],
    keys: tuple[str, ...],
) -> Any:
    for key in keys:
        if params.get(key):
            return params.get(key)
        if details.get(key):
            return details.get(key)
    return None


def _calendar_time_object(value: Any, *, timezone_name: str) -> dict[str, str]:
    if isinstance(value, dict):
        if value.get("date"):
            return {"date": str(value.get("date"))}
        text = str(value.get("dateTime") or value.get("datetime") or "").strip()
        if text:
            result = {"dateTime": _calendar_datetime_text(text, timezone_name=timezone_name)}
            tz = str(value.get("timeZone") or value.get("timezone") or "").strip()
            if tz:
                result["timeZone"] = tz
            elif not _datetime_text_has_offset(text):
                result["timeZone"] = timezone_name
            return result
        return {}
    if isinstance(value, date) and not isinstance(value, datetime):
        return {"date": value.isoformat()}
    text = str(value or "").strip()
    if not text:
        return {}
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return {"date": text}
    result = {"dateTime": _calendar_datetime_text(text, timezone_name=timezone_name)}
    if not _datetime_text_has_offset(text):
        result["timeZone"] = timezone_name
    return result


def _calendar_datetime_text(text: str, *, timezone_name: str) -> str:
    cleaned = str(text or "").strip()
    if not cleaned:
        return ""
    try:
        dt = datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
    except ValueError:
        return cleaned
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_zoneinfo(timezone_name))
    return dt.isoformat(timespec="seconds")


def _parse_calendar_time_range(text: str, *, timezone_name: str) -> tuple[str, str]:
    raw = " ".join(str(text or "").strip().split())
    if not raw:
        return "", ""
    if "/" in raw:
        left, right = [part.strip() for part in raw.split("/", 1)]
        if _parse_isoish_datetime(left) and _parse_isoish_datetime(right):
            return (
                _calendar_datetime_text(left, timezone_name=timezone_name),
                _calendar_datetime_text(right, timezone_name=timezone_name),
            )
    iso_matches = re.findall(
        r"\d{4}-\d{2}-\d{2}[ T]\d{1,2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:?\d{2})?",
        raw,
    )
    if len(iso_matches) >= 2:
        return (
            _calendar_datetime_text(iso_matches[0], timezone_name=timezone_name),
            _calendar_datetime_text(iso_matches[1], timezone_name=timezone_name),
        )
    compact = re.search(
        r"(?P<date>\d{4}-\d{2}-\d{2})[ T]+(?P<start>\d{1,2}:\d{2}(?::\d{2})?)"
        r"\s*(?:-|to|~|\u2013|\u2014)\s*"
        r"(?:(?P<end_date>\d{4}-\d{2}-\d{2})[ T]+)?(?P<end>\d{1,2}:\d{2}(?::\d{2})?)",
        raw,
        flags=re.IGNORECASE,
    )
    if compact:
        start = f"{compact.group('date')}T{compact.group('start')}"
        end_date = compact.group("end_date") or compact.group("date")
        end = f"{end_date}T{compact.group('end')}"
        return (
            _calendar_datetime_text(start, timezone_name=timezone_name),
            _calendar_datetime_text(end, timezone_name=timezone_name),
        )
    return "", ""


def _datetime_text_has_offset(text: str) -> bool:
    cleaned = str(text or "").strip()
    if cleaned.endswith("Z"):
        return True
    return bool(re.search(r"[+-]\d{2}:?\d{2}$", cleaned))


def _calendar_timezone_name(params: dict[str, Any], *, details: dict[str, Any]) -> str:
    return str(
        params.get("timezone")
        or params.get("timeZone")
        or details.get("timezone")
        or details.get("timeZone")
        or "Asia/Shanghai"
    ).strip() or "Asia/Shanghai"


def _zoneinfo(timezone_name: str) -> ZoneInfo:
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        return ZoneInfo("UTC")


def _calendar_send_updates(params: dict[str, Any]) -> str:
    raw = str(params.get("send_updates") or params.get("sendUpdates") or "").strip()
    if raw in {"all", "externalOnly", "none"}:
        return raw
    return "none"


def _calendar_write_query_params(params: dict[str, Any], *, body: dict[str, Any] | None) -> dict[str, str]:
    query: dict[str, str] = {}
    if params.get("conferenceDataVersion") is not None:
        query["conferenceDataVersion"] = str(params.get("conferenceDataVersion"))
    elif isinstance(body, dict) and body.get("conferenceData"):
        query["conferenceDataVersion"] = "1"
    if params.get("maxAttendees") is not None:
        query["maxAttendees"] = str(params.get("maxAttendees"))
    if _boolish(params.get("supportsAttachments"), bool(isinstance(body, dict) and body.get("attachments"))):
        query["supportsAttachments"] = "true"
    return query


def _calendar_google_api_request(
    *,
    method: str,
    calendar_id: str,
    event_id: str = "",
    body: dict[str, Any] | None = None,
    query: dict[str, str] | None = None,
) -> tuple[dict[str, Any], int, str]:
    token, credential_source = _google_oauth_access_token()
    encoded_calendar_id = urllib.parse.quote(calendar_id, safe="")
    path = f"https://www.googleapis.com/calendar/v3/calendars/{encoded_calendar_id}/events"
    if event_id:
        path += f"/{urllib.parse.quote(event_id, safe='')}"
    clean_query = {key: value for key, value in (query or {}).items() if str(value)}
    if clean_query:
        path += "?" + urllib.parse.urlencode(clean_query)
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    if data is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
    request = urllib.request.Request(path, data=data, headers=headers, method=method.upper())
    timeout_s = _bounded_float(
        os.getenv("PARROT_CALENDAR_API_TIMEOUT_S"),
        default=20.0,
        minimum=1.0,
        maximum=120.0,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_s) as response:
            status_code = int(getattr(response, "status", 0) or response.getcode())
            raw = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"Google Calendar API HTTP {exc.code}: {detail[:500]}") from exc
    if not raw:
        return {}, status_code, credential_source
    text = raw.decode("utf-8", "replace")
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError:
        decoded = {"raw": text}
    if not isinstance(decoded, dict):
        decoded = {"response": decoded}
    return decoded, status_code, credential_source


def _google_oauth_access_token() -> tuple[str, str]:
    creds, credential_source = _load_google_workspace_credentials()
    from google.auth.transport.requests import Request as GoogleAuthRequest

    if not creds.valid or creds.expired:
        creds.refresh(GoogleAuthRequest())
    token = str(getattr(creds, "token", "") or "")
    if not token:
        raise RuntimeError("Google OAuth credentials did not yield an access token")
    return token, credential_source


def _load_google_workspace_credentials():
    from google.oauth2.credentials import Credentials

    path = _google_workspace_credentials_path()
    if not path.exists():
        raise FileNotFoundError(
            "Google Workspace OAuth credentials not found. "
            "Run scripts/google_oauth.py or mount ECS google-workspace credentials."
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    scopes = data.get("scopes") or str(data.get("scope") or "").split()
    client_id = str(data.get("client_id") or os.getenv("GOOGLE_CLIENT_ID") or "")
    client_secret = str(data.get("client_secret") or os.getenv("GOOGLE_CLIENT_SECRET") or "")
    token_uri = str(data.get("token_uri") or "https://oauth2.googleapis.com/token")
    token = str(data.get("token") or data.get("access_token") or "")
    refresh_token = str(data.get("refresh_token") or "")
    if not token or not refresh_token or not client_id or not client_secret:
        raise RuntimeError("Google OAuth credentials are incomplete")
    creds = Credentials(
        token=token,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes or None,
    )
    expiry = data.get("expiry")
    if expiry:
        try:
            creds.expiry = datetime.fromisoformat(str(expiry).replace("Z", "+00:00"))
        except ValueError:
            pass
    elif data.get("expiry_date"):
        try:
            creds.expiry = datetime.fromtimestamp(float(data["expiry_date"]) / 1000.0)
        except (TypeError, ValueError):
            pass
    return creds, _google_workspace_credential_source(path)


def _google_workspace_credentials_path() -> Path:
    configured = str(
        os.getenv("PARROT_WEB_CONSOLE_GOOGLE_CREDENTIALS_PATH")
        or os.getenv("GOOGLE_WORKSPACE_CREDENTIALS_PATH")
        or ""
    ).strip()
    if configured:
        return Path(configured).expanduser()
    appdata = os.getenv("APPDATA")
    candidates: list[Path] = []
    if appdata:
        base = Path(appdata) / "google-workspace-mcp" / "credentials"
        candidates.extend([base / "credentials_python.json", base / "credentials.json"])
    base = Path.home() / ".nanobot" / "google-workspace-credentials"
    candidates.extend([base / "credentials_python.json", base / "credentials.json"])
    base = Path.home() / ".local" / "share" / "google-workspace-mcp" / "credentials"
    candidates.extend([base / "credentials_python.json", base / "credentials.json"])
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0] if candidates else Path("credentials_python.json")


def _google_workspace_credential_source(path: Path) -> str:
    if os.getenv("PARROT_WEB_CONSOLE_GOOGLE_CREDENTIALS_PATH") or os.getenv(
        "GOOGLE_WORKSPACE_CREDENTIALS_PATH"
    ):
        return "configured_oauth_file"
    path_parts = {part.lower() for part in path.parts}
    if ".nanobot" in path_parts and "google-workspace-credentials" in path_parts:
        return "ecs_nanobot_google_workspace_mcp"
    if "google-workspace-mcp" in path_parts:
        return "local_google_workspace_mcp"
    return "local_oauth_file"


def _calendar_write_summary(body: dict[str, Any]) -> str:
    action = str(body.get("action") or "write")
    event = body.get("event") if isinstance(body.get("event"), dict) else {}
    title = str(event.get("title") or event.get("summary") or body.get("event_id") or "event")
    event_id = str(body.get("event_id") or event.get("id") or "")
    dry_run = " dry-run" if body.get("dry_run") else ""
    if action == "delete":
        return f"Calendar delete{dry_run} completed: {event_id or title}"
    return f"Calendar {action}{dry_run} completed: {title}" + (f" ({event_id})" if event_id else "")


def _message_check_result(*, task_id: str, task_type: str, params: dict[str, Any]) -> dict[str, Any]:
    messages, source_path, warning = _messages_for_params(params)
    limit = _bounded_int(params.get("limit") or params.get("max_messages"), default=5, minimum=1, maximum=20)
    messages = messages[:limit]
    body = {
        "status": "completed",
        "message_count": len(messages),
        "messages": messages,
        "source": "fallback_demo_fixture" if source_path else "fallback_demo_message",
        "source_path": str(source_path) if source_path else "",
        "query": str(params.get("query") or "important unread mail"),
        "warning": warning,
        "worker": "parrot_fallback_nanobot_consumer",
    }
    body["summary"] = _message_check_summary(body)
    return {
        "task_id": task_id,
        "type": task_type,
        "status": "completed",
        "result": json.dumps(body, ensure_ascii=False),
        "result_summary": body["summary"],
        "completed_at": time.time(),
    }


def _messages_for_params(params: dict[str, Any]) -> tuple[list[dict[str, Any]], Path | None, str]:
    raw_messages = params.get("messages")
    if isinstance(raw_messages, list):
        return (
            [_normalize_message(item, fallback_index=index) for index, item in enumerate(raw_messages) if isinstance(item, dict)],
            None,
            "",
        )

    source_path = _message_fixture_path(params)
    if source_path:
        try:
            raw = json.loads(source_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return [], source_path, f"message_fixture_read_failed:{type(exc).__name__}"
        if isinstance(raw, dict):
            raw_messages = raw.get("messages")
        else:
            raw_messages = raw
        if not isinstance(raw_messages, list):
            return [], source_path, "message_fixture_has_no_messages_list"
        return (
            [_normalize_message(item, fallback_index=index) for index, item in enumerate(raw_messages) if isinstance(item, dict)],
            source_path,
            "",
        )

    if str(os.getenv("PARROT_NANOBOT_DEMO_MESSAGE_FALLBACK", "1")).strip().lower() in {"0", "false", "no", "off"}:
        return [], None, "demo_message_fallback_disabled"
    return [_normalize_message(_default_demo_message(), fallback_index=0)], None, ""


def _message_fixture_path(params: dict[str, Any]) -> Path | None:
    raw = (
        params.get("demo_messages_path")
        or params.get("fixture_path")
        or params.get("messages_path")
        or os.getenv("PARROT_MESSAGE_DEMO_MESSAGES_PATH")
        or ""
    )
    text = str(raw or "").strip()
    if not text:
        return None
    try:
        return Path(text).expanduser().resolve()
    except OSError:
        return Path(text).expanduser()


def _default_demo_message() -> dict[str, Any]:
    return {
        "id": "demo_important_message",
        "sender": "项目演示组 <demo@example.com>",
        "subject": "GOSLO 演示准备确认",
        "snippet": "请确认启动后的重要邮件提醒、临近日程提醒和语音播报都已经准备好。",
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "is_reply": False,
        "importance": "high",
        "source": "gmail_demo_fallback",
    }


def _normalize_message(message: dict[str, Any], *, fallback_index: int) -> dict[str, Any]:
    subject = str(message.get("subject") or message.get("title") or f"important message {fallback_index + 1}")
    normalized = dict(message)
    normalized["id"] = str(message.get("id") or message.get("message_id") or f"demo_message_{fallback_index + 1}")
    normalized["sender"] = str(message.get("sender") or message.get("from") or "Unknown sender")
    normalized["subject"] = subject
    normalized["snippet"] = str(message.get("snippet") or message.get("summary") or message.get("body") or "")
    normalized["timestamp"] = str(message.get("timestamp") or datetime.now().astimezone().isoformat(timespec="seconds"))
    normalized["is_reply"] = bool(message.get("is_reply", False))
    normalized["importance"] = str(message.get("importance") or "high").lower()
    normalized["source"] = str(message.get("source") or "gmail")
    return normalized


def _message_check_summary(body: dict[str, Any]) -> str:
    messages = [item for item in body.get("messages", []) if isinstance(item, dict)]
    if not messages:
        warning = str(body.get("warning") or "").strip()
        return "Google important mail check found no urgent messages" + (f" ({warning})" if warning else ".")
    parts = []
    for message in messages[:3]:
        sender = str(message.get("sender") or "Unknown sender")
        subject = str(message.get("subject") or "(no subject)")
        snippet = str(message.get("snippet") or "")[:120]
        parts.append(f"来自 {sender}，主题“{subject}”，内容：{snippet}".strip())
    return f"Google 刚收到 {len(messages)} 封重要邮件：" + "；".join(parts)


def _remind_result(*, task_id: str, task_type: str, params: dict[str, Any]) -> dict[str, Any]:
    reminder_text = " ".join(str(params.get("reminder_text") or params.get("text") or "提醒时间到了").split())
    when = str(params.get("when") or params.get("due_at") or "").strip()
    body = {
        "status": "completed",
        "reminder_text": reminder_text,
        "when": when,
        "reason": str(params.get("reason") or "GOSLO reminder request"),
        "source": "fallback_demo_reminder",
        "worker": "parrot_fallback_nanobot_consumer",
    }
    body["summary"] = (
        f"提醒时间到了：{reminder_text}" + (f"（{when}）" if when else "")
    )
    return {
        "task_id": task_id,
        "type": task_type,
        "status": "completed",
        "result": json.dumps(body, ensure_ascii=False),
        "result_summary": body["summary"],
        "completed_at": time.time(),
    }


def _diary_query_result(*, task_id: str, task_type: str, params: dict[str, Any]) -> dict[str, Any]:
    diary_root = _diary_root(params)
    if not diary_root.exists():
        body = {
            "status": "failed",
            "error": "diary_root_missing",
            "diary_root": str(diary_root),
            "where_to_read": str(diary_root),
            "entries": [],
            "summary": f"Diary root is missing: {diary_root}",
            "worker": "parrot_fallback_nanobot_consumer",
        }
        return {
            "task_id": task_id,
            "type": task_type,
            "status": "failed",
            "result": json.dumps(body, ensure_ascii=False),
            "result_summary": body["summary"],
            "completed_at": time.time(),
        }

    limit = _bounded_int(params.get("limit"), default=7, minimum=1, maximum=30)
    date_from, date_to = _diary_date_window(params)
    entries = _read_diary_entries(diary_root)
    entries = [
        entry
        for entry in entries
        if _diary_entry_in_window(entry, date_from=date_from, date_to=date_to)
    ]
    ranked = _rank_diary_entries(entries, query=str(params.get("query") or params.get("instructions") or ""))
    selected = ranked[:limit]
    body = {
        "status": "completed",
        "query": str(params.get("query") or ""),
        "diary_root": str(diary_root),
        "vault_path": str(params.get("vault_path") or ""),
        "where_to_read": str(diary_root),
        "date_from": date_from.isoformat() if date_from else "",
        "date_to": date_to.isoformat() if date_to else "",
        "entry_count": len(selected),
        "entries": selected,
        "summary": _diary_query_summary(selected, diary_root=diary_root),
        "worker": "parrot_fallback_nanobot_consumer",
        "profile_policy": "Read profile=daily diary files from Diary only; UUID-bound profile=ref docs stay in Refs.",
    }
    return {
        "task_id": task_id,
        "type": task_type,
        "status": "completed",
        "result": json.dumps(body, ensure_ascii=False),
        "result_summary": body["summary"],
        "completed_at": time.time(),
    }


def _diary_root(params: dict[str, Any]) -> Path:
    raw = (
        params.get("diary_root")
        or params.get("diary_path")
        or os.getenv("GOSLO_OBSIDIAN_DIARY_ROOT")
        or ""
    )
    if raw:
        return Path(str(raw)).expanduser().resolve()
    vault = str(params.get("vault_path") or os.getenv("GOSLO_OBSIDIAN_VAULT") or "D:/GOSLOParrot/GOSLObsidian")
    return (Path(vault).expanduser() / "Diary").resolve()


def _read_diary_entries(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        paths = sorted(root.rglob("*.md"))
    except OSError:
        return rows
    for path in paths:
        if ".obsidian" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        frontmatter, body = _split_markdown_frontmatter(text)
        profile = str(frontmatter.get("profile") or "").strip().lower()
        if profile and profile != "daily":
            continue
        entry_date = _entry_date(frontmatter, path)
        rows.append(
            {
                "date": entry_date.isoformat() if entry_date else "",
                "title": str(frontmatter.get("title") or path.stem),
                "path": str(path),
                "summary": _markdown_summary(body),
                "highlights": _diary_highlights(body),
                "tags": _frontmatter_tags(frontmatter.get("tags")),
            }
        )
    rows.sort(key=lambda item: str(item.get("date") or ""), reverse=True)
    return rows


def _split_markdown_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break
    if end_index is None:
        return {}, text
    frontmatter: dict[str, Any] = {}
    for line in lines[1:end_index]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        cleaned = value.strip().strip('"').strip("'")
        frontmatter[key.strip()] = cleaned
    return frontmatter, "\n".join(lines[end_index + 1 :])


def _entry_date(frontmatter: dict[str, Any], path: Path) -> date | None:
    for raw in (frontmatter.get("date"), frontmatter.get("day"), path.stem):
        text = str(raw or "").strip()
        match = re.search(r"\d{4}-\d{2}-\d{2}", text)
        if not match:
            continue
        try:
            return date.fromisoformat(match.group(0))
        except ValueError:
            continue
    return None


def _diary_date_window(params: dict[str, Any]) -> tuple[date | None, date | None]:
    explicit_from = _parse_date_only(params.get("date_from") or params.get("from"))
    explicit_to = _parse_date_only(params.get("date_to") or params.get("to"))
    if explicit_from or explicit_to:
        return explicit_from, explicit_to
    days = _bounded_int(params.get("days"), default=7, minimum=1, maximum=31)
    end = date.today() - timedelta(days=1)
    return end - timedelta(days=days - 1), end


def _parse_date_only(value: Any) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _diary_entry_in_window(entry: dict[str, Any], *, date_from: date | None, date_to: date | None) -> bool:
    entry_date = _parse_date_only(entry.get("date"))
    if entry_date is None:
        return True
    if date_from and entry_date < date_from:
        return False
    if date_to and entry_date > date_to:
        return False
    return True


def _rank_diary_entries(entries: list[dict[str, Any]], *, query: str) -> list[dict[str, Any]]:
    terms = _query_terms(query)
    if not terms:
        return list(entries)

    def score(entry: dict[str, Any]) -> tuple[int, str]:
        haystack = " ".join(
            [
                str(entry.get("title") or ""),
                str(entry.get("summary") or ""),
                " ".join(str(item) for item in entry.get("highlights", []) if str(item)),
                " ".join(str(item) for item in entry.get("tags", []) if str(item)),
            ]
        ).lower()
        hits = sum(1 for term in terms if term in haystack)
        return hits, str(entry.get("date") or "")

    ranked = sorted(entries, key=score, reverse=True)
    return ranked


def _query_terms(query: str) -> list[str]:
    raw = re.findall(r"[A-Za-z0-9_\-]+|[\u4e00-\u9fff]{2,}", str(query or "").lower())
    seen: set[str] = set()
    terms: list[str] = []
    for term in raw:
        if term in seen:
            continue
        seen.add(term)
        terms.append(term)
    return terms[:20]


def _markdown_summary(body: str) -> str:
    cleaned_lines = []
    for line in body.splitlines():
        text = re.sub(r"^[#*\-\s]+", "", line).strip()
        if text:
            cleaned_lines.append(text)
    return " ".join(cleaned_lines)[:700]


def _diary_highlights(body: str) -> list[str]:
    highlights: list[str] = []
    for marker in ("吉他", "追番", "看剧", "锻炼", "喝水", "吃药", "奶茶", "guitar", "anime"):
        for line in body.splitlines():
            text = line.strip(" -#*\t")
            if marker.lower() in text.lower() and text not in highlights:
                highlights.append(text[:180])
                break
    return highlights[:8]


def _frontmatter_tags(raw: Any) -> list[str]:
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]
    text = str(raw or "").strip()
    if not text:
        return []
    return [item.strip() for item in re.split(r"[, ]+", text) if item.strip()]


def _diary_query_summary(entries: list[dict[str, Any]], *, diary_root: Path) -> str:
    if not entries:
        return f"Diary query found no matching Markdown entries under {diary_root}."
    dates = ", ".join(str(entry.get("date") or "?") for entry in entries[:7])
    first = entries[0]
    first_title = str(first.get("title") or first.get("path") or "diary")
    return (
        f"Diary query found {len(entries)} entry(s) under {diary_root}: {dates}. "
        f"Most recent match: {first_title}. Open the returned Markdown paths to read the full diary."
    )


def _ref_scan_result(*, task_id: str, task_type: str, params: dict[str, Any]) -> dict[str, Any]:
    if params.get("allow_mutation") is True:
        body = {
            "scan_id": str(params.get("scan_id") or ""),
            "status": "failed",
            "error": "ref_scan_worker_refuses_mutation",
            "summary": "Ref scan refused because allow_mutation=true.",
            "ref_results": [],
            "manifest_delta": [],
            "warnings": ["mutation_request_rejected"],
        }
        return {
            "task_id": task_id,
            "type": task_type,
            "status": "failed",
            "result": json.dumps(body, ensure_ascii=False),
            "completed_at": time.time(),
        }

    refs = params.get("refs") if isinstance(params.get("refs"), list) else []
    scan_options = _ref_scan_options(params)
    ref_results = [_scan_ref(ref, options=scan_options) for ref in refs if isinstance(ref, dict)]
    manifest_delta = [
        delta
        for result in ref_results
        for delta in _manifest_delta_for_ref(result)
    ]
    warnings = [
        warning
        for result in ref_results
        for warning in result.get("warnings", [])
        if str(warning)
    ]
    body = {
        "scan_id": str(params.get("scan_id") or ""),
        "status": "completed",
        "scan_mode": "read_only",
        "allow_mutation": False,
        "ref_results": ref_results,
        "manifest_delta": manifest_delta,
        "warnings": warnings[:20],
        "summary": f"Scanned {len(ref_results)} ref(s); {len(manifest_delta)} manifest delta(s) proposed.",
        "worker": "parrot_fallback_nanobot_consumer",
        "checker_policy": scan_options["policy"],
    }
    return {
        "task_id": task_id,
        "type": task_type,
        "status": "completed",
        "result": json.dumps(body, ensure_ascii=False),
        "completed_at": time.time(),
    }


def _scan_ref(ref: dict[str, Any], *, options: dict[str, Any]) -> dict[str, Any]:
    locators = _string_list(ref.get("locators"))
    locator_results = [_scan_locator(locator, options=options) for locator in locators]
    health = _overall_ref_health(locator_results)
    result: dict[str, Any] = {
        "ref_id": str(ref.get("ref_id") or ""),
        "canonical_uuid": str(ref.get("canonical_uuid") or ""),
        "kind": str(ref.get("kind") or "external"),
        "health": health,
        "risk_level": str(ref.get("risk_level") or ""),
        "manifest_action": str(ref.get("manifest_action") or "propose_manifest_fingerprint"),
        "locator_results": locator_results,
        "warnings": [
            warning
            for locator_result in locator_results
            for warning in locator_result.get("warnings", [])
            if str(warning)
        ],
    }
    first_ok_file = next(
        (
            row
            for row in locator_results
            if row.get("target_type") in {"local_path", "ecs_path"}
            and row.get("health") == "ok"
            and row.get("content_hash")
        ),
        None,
    )
    if first_ok_file:
        result["resolved_locator"] = first_ok_file.get("locator", "")
        result["content_hash"] = first_ok_file.get("content_hash", "")
        result["size"] = first_ok_file.get("size", 0)
        result["mtime"] = first_ok_file.get("mtime", 0.0)
    return result


def _scan_locator(locator: str, *, options: dict[str, Any]) -> dict[str, Any]:
    text = str(locator or "").strip()
    target_type = _locator_target_type(text)
    if not text:
        return {
            "locator": "",
            "target_type": "blank",
            "health": "missing",
            "reason": "blank_locator",
            "warnings": ["blank_locator"],
        }
    if target_type == "local_path":
        return _scan_local_path(text)
    if target_type == "url":
        if options.get("enable_url_check"):
            return _scan_url(text, options=options)
        return {
            "locator": text,
            "target_type": target_type,
            "health": "unknown",
            "reason": "url_not_checked_by_fallback",
            "warnings": ["url_requires_mcp_or_enabled_network_checker"],
        }
    if target_type == "ecs_path":
        if options.get("enable_ecs_local_check"):
            return _scan_ecs_path(text, options=options)
        return {
            "locator": text,
            "target_type": target_type,
            "health": "unknown",
            "reason": "ecs_path_not_checked_by_fallback",
            "warnings": ["ecs_path_requires_mcp_checker"],
        }
    if target_type == "graphiti_pointer":
        if options.get("enable_graphiti_probe"):
            return _scan_graphiti_pointer(text, options=options)
        return {
            "locator": text,
            "target_type": target_type,
            "health": "unknown",
            "reason": "graphiti_pointer_not_checked_by_fallback",
            "warnings": ["graphiti_pointer_requires_graphiti_checker"],
        }
    return {
        "locator": text,
        "target_type": target_type,
        "health": "unknown",
        "reason": "opaque_locator_not_checked_by_fallback",
        "warnings": ["opaque_locator_requires_mcp_checker"],
    }


def _ref_scan_options(params: dict[str, Any]) -> dict[str, Any]:
    remote_checks = {
        str(item).strip().lower()
        for item in params.get("remote_checks", [])
        if str(item).strip()
    } if isinstance(params.get("remote_checks"), list) else set()
    enable_url_check = (
        _boolish(params.get("enable_url_check"), False)
        or "url" in remote_checks
        or "http_head" in remote_checks
        or _env_bool("PARROT_REF_SCAN_ENABLE_URL_CHECK", False)
    )
    requested_ecs_local_check = (
        _boolish(params.get("enable_ecs_local_check"), False)
        or "ecs" in remote_checks
        or "ecs_path_stat" in remote_checks
        or _env_bool("PARROT_REF_SCAN_ENABLE_ECS_LOCAL_CHECK", False)
    )
    enable_ecs_local_check = requested_ecs_local_check and (
        _boolish(params.get("ecs_local_check_confirmed"), False)
        or _env_bool("PARROT_REF_SCAN_ENABLE_ECS_LOCAL_CHECK", False)
    )
    enable_graphiti_probe = (
        _boolish(params.get("enable_graphiti_probe"), False)
        or "graphiti" in remote_checks
        or "graphiti_uuid_probe" in remote_checks
        or _env_bool("PARROT_REF_SCAN_ENABLE_GRAPHITI_PROBE", False)
    )
    timeout_s = _bounded_float(
        params.get("network_timeout_s"),
        default=_bounded_float(os.getenv("PARROT_REF_SCAN_NETWORK_TIMEOUT_S"), default=3.0),
    )
    ecs_host = str(params.get("ecs_local_host") or os.getenv("PARROT_REF_SCAN_ECS_LOCAL_HOST") or "castle").strip()
    graphiti_base_url = str(
        params.get("graphiti_base_url")
        or os.getenv("PARROT_WEB_CONSOLE_GRAPHITI_URL")
        or os.getenv("PARROT_GRAPHITI_REMOTE_URL")
        or ""
    ).strip().rstrip("/")
    enabled = []
    if enable_url_check:
        enabled.append("url_head")
    if enable_ecs_local_check:
        enabled.append("ecs_local_stat")
    if enable_graphiti_probe:
        enabled.append("graphiti_search_probe")
    return {
        "enable_url_check": enable_url_check,
        "enable_ecs_local_check": enable_ecs_local_check,
        "enable_graphiti_probe": enable_graphiti_probe,
        "network_timeout_s": timeout_s,
        "ecs_local_host": ecs_host,
        "ecs_local_roots": _ecs_local_roots(params.get("ecs_local_roots")),
        "graphiti_base_url": graphiti_base_url,
        "policy": {
            "remote_checks_enabled": enabled,
            "remote_checks_requested": sorted(remote_checks),
            "read_only": True,
            "mutation_allowed": False,
            "url_body_read": False,
            "ecs_write": False,
            "graphiti_write": False,
        },
    }


def _scan_url(locator: str, *, options: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        locator,
        method="HEAD",
        headers={"User-Agent": "ParrotCarriers-ref-scan/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=float(options.get("network_timeout_s") or 3.0)) as response:
            status_code = int(getattr(response, "status", 0) or response.getcode())
            return {
                "locator": locator,
                "target_type": "url",
                "health": "ok" if 200 <= status_code < 400 else "unknown",
                "reason": "url_head_ok" if 200 <= status_code < 400 else "url_head_unexpected_status",
                "status_code": status_code,
                "content_type": response.headers.get("Content-Type", ""),
                "content_length": response.headers.get("Content-Length", ""),
                "warnings": [] if 200 <= status_code < 400 else ["url_head_unexpected_status"],
            }
    except urllib.error.HTTPError as exc:
        status_code = int(exc.code or 0)
        if status_code in {404, 410}:
            health = "missing"
            reason = "url_missing"
            warnings = ["url_missing"]
        elif status_code in {401, 403}:
            health = "unknown"
            reason = "url_auth_required"
            warnings = ["url_auth_required"]
        else:
            health = "unknown"
            reason = "url_head_http_error"
            warnings = ["url_head_http_error"]
        return {
            "locator": locator,
            "target_type": "url",
            "health": health,
            "reason": reason,
            "status_code": status_code,
            "content_type": exc.headers.get("Content-Type", "") if exc.headers else "",
            "content_length": exc.headers.get("Content-Length", "") if exc.headers else "",
            "warnings": warnings,
        }
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {
            "locator": locator,
            "target_type": "url",
            "health": "unknown",
            "reason": f"url_head_failed:{type(exc).__name__}",
            "warnings": ["url_head_failed"],
        }


def _scan_ecs_path(locator: str, *, options: dict[str, Any]) -> dict[str, Any]:
    mapped_path, warning = _ecs_locator_to_local_path(locator, options=options)
    if not mapped_path:
        return {
            "locator": locator,
            "target_type": "ecs_path",
            "health": "unknown",
            "reason": warning or "ecs_path_not_mapped_to_local_host",
            "warnings": [warning or "ecs_path_not_mapped_to_local_host"],
        }
    local_result = _scan_local_path(str(mapped_path))
    result = {
        **local_result,
        "locator": locator,
        "target_type": "ecs_path",
        "local_probe_path": str(mapped_path),
    }
    if result.get("reason") == "local_path_exists":
        result["reason"] = "ecs_local_path_exists"
    elif result.get("reason") == "local_path_missing":
        result["reason"] = "ecs_local_path_missing"
    warnings = [
        "ecs_local_read_only_probe",
        *[str(item) for item in result.get("warnings", []) if str(item)],
    ]
    result["warnings"] = warnings
    return result


def _scan_graphiti_pointer(locator: str, *, options: dict[str, Any]) -> dict[str, Any]:
    parsed = _parse_graphiti_locator(locator)
    graphiti_uuid = parsed.get("uuid", "")
    partition = parsed.get("partition", "")
    base_url = str(options.get("graphiti_base_url") or "").rstrip("/")
    if not graphiti_uuid:
        return {
            "locator": locator,
            "target_type": "graphiti_pointer",
            "health": "unknown",
            "reason": "graphiti_pointer_missing_uuid",
            "warnings": ["graphiti_pointer_missing_uuid"],
        }
    if not base_url:
        return {
            "locator": locator,
            "target_type": "graphiti_pointer",
            "health": "unknown",
            "reason": "graphiti_probe_url_not_configured",
            "graphiti_uuid": graphiti_uuid,
            "partition": partition,
            "warnings": ["graphiti_probe_url_not_configured"],
        }
    payload = json.dumps(
        {"query": graphiti_uuid, "partition": partition, "limit": 10},
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}/api/graphiti/search",
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "ParrotCarriers-ref-scan/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=float(options.get("network_timeout_s") or 3.0)) as response:
            raw = response.read(1024 * 1024)
            data = json.loads(raw.decode("utf-8")) if raw else {}
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {
            "locator": locator,
            "target_type": "graphiti_pointer",
            "health": "unknown",
            "reason": f"graphiti_probe_failed:{type(exc).__name__}",
            "graphiti_uuid": graphiti_uuid,
            "partition": partition,
            "warnings": ["graphiti_probe_failed"],
        }
    if not isinstance(data, dict) or data.get("success") is False:
        error = str(data.get("error") or data.get("message") or "graphiti_probe_unsuccessful") if isinstance(data, dict) else "graphiti_probe_non_object_response"
        return {
            "locator": locator,
            "target_type": "graphiti_pointer",
            "health": "unknown",
            "reason": error,
            "graphiti_uuid": graphiti_uuid,
            "partition": partition,
            "warnings": ["graphiti_probe_unsuccessful"],
        }
    results = data.get("data", {}).get("results", []) if isinstance(data.get("data"), dict) else []
    exact_match = _json_contains_text(results, graphiti_uuid)
    return {
        "locator": locator,
        "target_type": "graphiti_pointer",
        "health": "ok" if exact_match else "unknown",
        "reason": "graphiti_uuid_found_by_search_probe" if exact_match else "graphiti_uuid_not_found_by_search_probe",
        "graphiti_uuid": graphiti_uuid,
        "partition": partition,
        "result_count": len(results) if isinstance(results, list) else 0,
        "warnings": [] if exact_match else ["graphiti_search_probe_is_not_uuid_crud_lookup"],
    }


def _scan_local_path(locator: str) -> dict[str, Any]:
    path = Path(locator).expanduser()
    try:
        exists = path.exists()
    except OSError as exc:
        return {
            "locator": locator,
            "target_type": "local_path",
            "health": "unknown",
            "reason": f"{type(exc).__name__}: {exc}",
            "warnings": ["local_path_stat_failed"],
        }
    if not exists:
        return {
            "locator": locator,
            "target_type": "local_path",
            "health": "missing",
            "reason": "local_path_missing",
            "warnings": ["local_path_missing"],
        }
    try:
        stat = path.stat()
    except OSError as exc:
        return {
            "locator": locator,
            "target_type": "local_path",
            "health": "unknown",
            "reason": f"{type(exc).__name__}: {exc}",
            "warnings": ["local_path_stat_failed"],
        }
    result: dict[str, Any] = {
        "locator": locator,
        "target_type": "local_path",
        "health": "ok",
        "reason": "local_path_exists",
        "size": int(stat.st_size),
        "mtime": float(stat.st_mtime),
        "is_dir": path.is_dir(),
        "warnings": [],
    }
    if path.is_file():
        content_hash, hash_warning = _hash_file(path, size=int(stat.st_size))
        if content_hash:
            result["content_hash"] = content_hash
        if hash_warning:
            result["warnings"].append(hash_warning)
    return result


def _hash_file(path: Path, *, size: int) -> tuple[str, str]:
    max_bytes = _hash_max_bytes()
    if size > max_bytes:
        return "", "local_file_too_large_for_fallback_hash"
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return f"sha256:{digest.hexdigest()}", ""
    except OSError as exc:
        return "", f"local_file_hash_failed:{type(exc).__name__}"


def _hash_max_bytes() -> int:
    try:
        return max(0, int(os.getenv("PARROT_REF_SCAN_HASH_MAX_BYTES", "5242880")))
    except ValueError:
        return 5242880


def _boolish(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value is None or value == "":
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _env_bool(name: str, default: bool) -> bool:
    return _boolish(os.getenv(name), default)


def _bounded_int(value: Any, *, default: int, minimum: int = 1, maximum: int = 100) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(parsed, maximum))


def _bounded_float(value: Any, *, default: float, minimum: float = 0.25, maximum: float = 10.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(parsed, maximum))


def _ecs_local_roots(raw: Any) -> list[Path]:
    if isinstance(raw, (list, tuple, set)):
        values = [str(item) for item in raw]
    else:
        values = str(raw or os.getenv("PARROT_REF_SCAN_ECS_LOCAL_ROOTS") or "/root").split(";")
    roots: list[Path] = []
    for value in values:
        text = str(value or "").strip()
        if not text:
            continue
        try:
            roots.append(Path(text).expanduser().resolve())
        except OSError:
            continue
    return roots or [Path("/root").resolve()]


def _ecs_locator_to_local_path(locator: str, *, options: dict[str, Any]) -> tuple[Path | None, str]:
    text = str(locator or "").strip()
    expected_host = str(options.get("ecs_local_host") or "castle").strip().lower()
    if text.startswith("/root/"):
        candidate = Path(text)
    elif text.lower().startswith("ecs://"):
        parsed = urllib.parse.urlparse(text)
        host = (parsed.netloc or "").lower()
        if expected_host and host and host != expected_host:
            return None, "ecs_locator_host_not_local"
        candidate = Path(urllib.parse.unquote(parsed.path or ""))
    else:
        return None, "ecs_locator_scheme_not_supported_by_local_probe"
    try:
        resolved = candidate.expanduser().resolve()
    except OSError as exc:
        return None, f"ecs_local_path_resolve_failed:{type(exc).__name__}"
    roots = options.get("ecs_local_roots") if isinstance(options.get("ecs_local_roots"), list) else []
    if roots and not any(_path_is_relative_to(resolved, root) for root in roots if isinstance(root, Path)):
        return None, "ecs_local_path_outside_allowed_roots"
    return resolved, ""


def _path_is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _parse_graphiti_locator(locator: str) -> dict[str, str]:
    parsed = urllib.parse.urlparse(str(locator or "").strip())
    parts = [urllib.parse.unquote(part) for part in parsed.path.split("/") if part]
    return {
        "partition": parsed.netloc,
        "kind": parts[0] if parts else "",
        "uuid": parts[-1] if parts else "",
    }


def _json_contains_text(value: Any, needle: str) -> bool:
    if not needle:
        return False
    if isinstance(value, str):
        return value == needle
    if isinstance(value, dict):
        return any(_json_contains_text(item, needle) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_json_contains_text(item, needle) for item in value)
    return False


def _overall_ref_health(locator_results: list[dict[str, Any]]) -> str:
    if not locator_results:
        return "unknown"
    statuses = {str(row.get("health") or "unknown") for row in locator_results}
    if "ok" in statuses:
        return "ok"
    if statuses == {"missing"}:
        return "missing"
    return "unknown"


def _manifest_delta_for_ref(result: dict[str, Any]) -> list[dict[str, Any]]:
    ref_id = str(result.get("ref_id") or "")
    if not ref_id:
        return []
    deltas: list[dict[str, Any]] = []
    health = str(result.get("health") or "unknown")
    if health in {"ok", "missing"}:
        deltas.append({
            "ref_id": ref_id,
            "action": "propose_health_update",
            "health": health,
        })
    if result.get("content_hash"):
        deltas.append({
            "ref_id": ref_id,
            "action": "propose_content_hash_update",
            "content_hash": result.get("content_hash"),
        })
    return deltas


def _locator_target_type(locator: str) -> str:
    lowered = locator.lower()
    if lowered.startswith(("http://", "https://")):
        return "url"
    if lowered.startswith(("ecs://", "ssh://", "sftp://")) or lowered.startswith("/root/") or lowered.startswith("root@"):
        return "ecs_path"
    if lowered.startswith("graphiti://"):
        return "graphiti_pointer"
    if _looks_like_path(locator):
        return "local_path"
    return "opaque_locator"


def _looks_like_path(value: str) -> bool:
    text = str(value or "").strip()
    if not text:
        return False
    if text.startswith(("~", "/", "\\")):
        return True
    if len(text) >= 3 and text[1:3] in {":\\", ":/"}:
        return True
    return "\\" in text or "/" in text


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        values: Any = [value]
    else:
        values = value
    if not isinstance(values, (list, tuple, set)):
        return []
    result: list[str] = []
    seen: set[str] = set()
    for item in values:
        text = str(item or "").strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


async def run_nanobot_consumer() -> None:
    """Entry point for running the Nanobot consumer standalone."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    consumer = NanobotConsumer()
    try:
        await consumer.start()
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(run_nanobot_consumer())
