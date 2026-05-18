"""GOSLO Calendar Intent decision-draft tool.

This tool stages a Calendar change decision for Plan/HITL review. It is not an
execution tool and never writes Google Calendar directly.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from livekit.agents import RunContext, function_tool

logger = logging.getLogger(__name__)

_ACTION_TO_TASK_TYPE = {
    "create": "calendar_create",
    "patch": "calendar_patch",
    "delete": "calendar_delete",
}


@function_tool()
async def calendar_change_request(
    context: RunContext,
    action: str,
    title: str = "",
    time_range: str = "",
    calendar_id: str = "primary",
    event_id: str = "",
    reason: str = "",
    details_json: str = "{}",
    require_user_confirmation: bool = True,
    plan_id: str = "",
    step_id: str = "",
) -> str:
    """Stage a Google Calendar change decision for Plan/HITL approval.

    Category: Intent-layer Calendar decision/draft tool. Use this while GOSLO
    is deciding with the user whether a Calendar change should happen, checking
    whether the proposed change conflicts with context, and gradually shaping a
    Plan or HITL-ready draft. This tool is for decision handoff, not execution.

    Conversation blocking: brief. It only stages a paper-note draft in
    IntentWorkspace, so GOSLO can keep speaking naturally after it returns.

    Write authority: none. This tool never calls Google Calendar, never
    dispatches Nanobot, never imports L1.5, never mutates L2-B, and never writes
    Graphiti. The staged draft is the input to a later Plan/HITL gate. After
    approval, GOSLO/Plan may choose the execution route: a fast T1 direct
    Calendar API action if the operation is safe and quick enough, or a T3
    Nanobot/Scheduler task (`calendar_create`, `calendar_patch`, or
    `calendar_delete`) when the work should run in the background. This tool
    deliberately does not choose or execute that route.

    Args:
        action: Requested mutation: 'create', 'patch', 'update', or 'delete'.
            'update' is normalized to 'patch'.
        title: Human-readable event title or draft summary.
        time_range: Proposed time window in user-facing text or ISO-ish form.
        calendar_id: Google Calendar id, usually 'primary'.
        event_id: Existing Google Calendar event id for patch/delete.
        reason: Why GOSLO is proposing the change.
        details_json: Optional JSON object with fields such as description,
            location, attendees, recurrence, reminders, or source refs.
        require_user_confirmation: Keep true for normal write proposals.
        plan_id: Optional Plan id if this draft belongs to an existing Plan.
        step_id: Optional Plan step id if known.
    """

    return await do_calendar_change_request(
        action=action,
        title=title,
        time_range=time_range,
        calendar_id=calendar_id,
        event_id=event_id,
        reason=reason,
        details_json=details_json,
        require_user_confirmation=require_user_confirmation,
        plan_id=plan_id,
        step_id=step_id,
    )


async def do_calendar_change_request(
    *,
    action: str,
    title: str = "",
    time_range: str = "",
    calendar_id: str = "primary",
    event_id: str = "",
    reason: str = "",
    details_json: str | dict[str, Any] = "{}",
    require_user_confirmation: bool = True,
    plan_id: str = "",
    step_id: str = "",
) -> str:
    normalized_action = _normalize_action(action)
    if normalized_action not in _ACTION_TO_TASK_TYPE:
        return (
            "Calendar change draft rejected: unsupported action "
            f"'{str(action or '').strip()}'. Use create, patch/update, or delete. "
            "No Google Calendar write, no Nanobot dispatch, and no memory mutation occurred."
        )

    missing = _missing_required_fields(
        action=normalized_action,
        title=title,
        time_range=time_range,
        event_id=event_id,
    )
    if missing:
        return (
            "Calendar change draft rejected: missing "
            f"{', '.join(missing)} for action={normalized_action}. "
            "GOSLO should ask the user for the missing detail or use "
            "calendar_context/calendar_task_status before drafting. No write occurred."
        )

    details, details_error = _parse_details(details_json)
    if details_error:
        return (
            f"Calendar change draft rejected: details_json is not a JSON object ({details_error}). "
            "No Google Calendar write, no Nanobot dispatch, and no memory mutation occurred."
        )

    task_type = _ACTION_TO_TASK_TYPE[normalized_action]
    draft_payload = {
        "schema": "goslo_calendar_change_request_v1",
        "tool_category": "T2_INTENT_PLAN_HITL_DRAFT",
        "decision_layer": "Intent",
        "draft_is_execution_request": False,
        "action": normalized_action,
        "suggested_nanobot_task_type": task_type,
        "execution_route_owner": "GOSLO/Plan after Plan/HITL approval",
        "execution_route_policy": (
            "not hardcoded; GOSLO/Plan chooses T1 direct or T3 Nanobot after approval"
        ),
        "allowed_execution_routes_after_approval": [
            "T1_DIRECT_GOOGLE_CALENDAR_API",
            "T3_NANOBOT_SCHEDULER_TASK",
        ],
        "blocked_side_effects": [
            "google_calendar_write",
            "nanobot_dispatch",
            "l1_5_import",
            "l2b_mutation",
            "graphiti_write",
        ],
        "calendar_id": str(calendar_id or "primary"),
        "event_id": str(event_id or ""),
        "title": str(title or ""),
        "time_range": str(time_range or ""),
        "reason": str(reason or ""),
        "details": details,
        "requires_hitl": True,
        "require_user_confirmation": bool(require_user_confirmation),
        "plan_id": str(plan_id or ""),
        "step_id": str(step_id or ""),
        "result_channel": "calendar_result",
        "write_authority": (
            "Plan/HITL approval first; execution route selected by GOSLO/Plan "
            "based on latency, risk, and conversation feel"
        ),
        "sync_after_execution": [
            "IntentWorkspace result paper note",
            "calendar_result trigger ledger",
            "L1.5 GOOGLE_CALENDAR observation import",
            "L2-B event pointer projection",
        ],
        "memory_sync_policy": (
            "L1.5/L2-B/Graphiti are post-result working-memory or audit projections, "
            "not the Calendar task SSOT"
        ),
    }

    try:
        from parrot.brain.app_first_version import AppFirstVersionFacade

        facade = AppFirstVersionFacade()
        result = await facade.create_calendar_draft(
            action=normalized_action,
            title=str(title or f"{normalized_action} calendar event"),
            time_range=str(time_range or ""),
            payload=draft_payload,
        )
    except Exception as exc:
        logger.exception("calendar_change_request: failed to stage IntentWorkspace draft")
        return (
            "Calendar change draft failed while staging IntentWorkspace: "
            f"{type(exc).__name__}: {exc}. No Google Calendar write or Nanobot dispatch occurred."
        )

    ref_id = result.intent_workspace_ref_id or ""
    confirmation_line = (
        "User confirmation is required before dispatch."
        if require_user_confirmation
        else "Draft says confirmation may already be present, but Plan/HITL should still verify it."
    )
    return (
        "Calendar change draft staged (Intent-layer Plan/HITL draft).\n"
        f"Draft ref: {ref_id or 'unknown'}.\n"
        f"Action: {normalized_action}; suggested background task={task_type} only if T3 execution is chosen.\n"
        f"Calendar/event: {draft_payload['calendar_id']} / {draft_payload['event_id'] or 'new event'}.\n"
        f"{confirmation_line}\n"
        "Next step: present the draft to the user or a Plan/HITL gate; after approval, "
        "GOSLO/Plan chooses either T1 direct Google Calendar API execution or T3 Nanobot dispatch "
        f"({task_type}, result_channel=calendar_result).\n"
        "No Google Calendar write, no Nanobot dispatch, no L1.5 import, no L2-B mutation, "
        "and no Graphiti write occurred."
    )


def _normalize_action(action: str) -> str:
    raw = str(action or "").strip().lower()
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
    return aliases.get(raw, raw)


def _missing_required_fields(
    *,
    action: str,
    title: str,
    time_range: str,
    event_id: str,
) -> list[str]:
    missing: list[str] = []
    if action == "create":
        if not str(title or "").strip():
            missing.append("title")
        if not str(time_range or "").strip():
            missing.append("time_range")
    if action in {"patch", "delete"} and not str(event_id or "").strip():
        missing.append("event_id")
    return missing


def _parse_details(details_json: str | dict[str, Any]) -> tuple[dict[str, Any], str]:
    if isinstance(details_json, dict):
        return dict(details_json), ""
    raw = str(details_json or "{}").strip()
    if not raw:
        return {}, ""
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError as exc:
        return {}, str(exc)
    if not isinstance(decoded, dict):
        return {}, "top-level JSON value must be an object"
    return dict(decoded), ""


__all__ = ["calendar_change_request", "do_calendar_change_request"]
