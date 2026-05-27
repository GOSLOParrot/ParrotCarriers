"""Agentic Nanobot mission request tool for GOSLO.

This is the foreground-friendly wrapper around Scheduler/Nanobot dispatch. It
lets Brain hand off a natural-language goal plus authority/workflow guidance
without reducing Nanobot to a fixed function endpoint.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from livekit.agents import RunContext, function_tool

logger = logging.getLogger(__name__)

_AUTHORITY_VALUES = {"read_only", "draft_only", "approved_write", "operator_write"}
_MISSION_MODES = {"flexible", "guided_workflow"}
_CALENDAR_DOMAINS = {"calendar", "google_calendar", "schedule", "scheduling"}


@function_tool()
async def nanobot_mission_request(
    context: RunContext,
    goal: str,
    domain: str = "general",
    mode: str = "flexible",
    authority: str = "draft_only",
    workflow_hint: str = "",
    workflow_json: str = "{}",
    allowed_tools_json: str = "[]",
    context_refs_json: str = "[]",
    expected_report: str = "",
    hitl_policy: str = "ask_before_external_write",
    priority: str = "normal",
    result_channel: str = "",
    user_confirmation: bool = False,
    approval_json: str = "{}",
) -> str:
    """Dispatch a self-directed Nanobot mission through Scheduler.

    Category: Task-layer agentic delegation. Use this when GOSLO has a goal
    that may need background investigation, multiple tool calls, conflict
    analysis, or a strict-but-not-dead workflow. Brain owns the foreground
    conversation; Nanobot owns the background investigation and reports back
    through Scheduler.

    Two modes are supported:
      - flexible: Nanobot may decide how to investigate and solve the mission.
      - guided_workflow: workflow_hint/workflow_json are a playbook. Nanobot
        should follow them unless context, conflicts, safety, or missing data
        require a pause or a better route.

    Write authority is a hard boundary. Default draft_only means Nanobot may
    investigate, propose options, and return draft_ready/needs_user_decision,
    but must not write external systems. approved_write/operator_write require
    explicit user/HITL/operator confirmation in this call or in a later Plan
    gate; otherwise this tool downgrades the mission to draft_only.
    """

    return await do_nanobot_mission_request(
        goal=goal,
        domain=domain,
        mode=mode,
        authority=authority,
        workflow_hint=workflow_hint,
        workflow_json=workflow_json,
        allowed_tools_json=allowed_tools_json,
        context_refs_json=context_refs_json,
        expected_report=expected_report,
        hitl_policy=hitl_policy,
        priority=priority,
        result_channel=result_channel,
        user_confirmation=user_confirmation,
        approval_json=approval_json,
    )


async def do_nanobot_mission_request(
    *,
    goal: str,
    domain: str = "general",
    mode: str = "flexible",
    authority: str = "draft_only",
    workflow_hint: str = "",
    workflow_json: str | dict[str, Any] | list[Any] = "{}",
    allowed_tools_json: str | list[Any] = "[]",
    context_refs_json: str | list[Any] = "[]",
    expected_report: str = "",
    hitl_policy: str = "ask_before_external_write",
    priority: str = "normal",
    result_channel: str = "",
    user_confirmation: bool = False,
    approval_json: str | dict[str, Any] = "{}",
    task_dispatcher: Any = None,
) -> str:
    """Core Nanobot mission dispatch logic for tests and tool wrapper."""

    selected_goal = " ".join(str(goal or "").split())[:2000]
    if not selected_goal:
        return (
            "Nanobot mission rejected: missing goal. No Scheduler dispatch, "
            "external write, Graphiti write, or L2-B mutation occurred."
        )

    selected_domain = _domain(domain)
    selected_mode = _mode(mode)
    requested_authority = _authority(authority)
    approval, approval_error = _json_object(approval_json, default={})
    if approval_error:
        return (
            "Nanobot mission rejected: approval_json is not a JSON object "
            f"({approval_error}). No Scheduler dispatch or external write occurred."
        )
    workflow, workflow_error = _json_any(workflow_json, default={})
    if workflow_error:
        return (
            "Nanobot mission rejected: workflow_json is invalid JSON "
            f"({workflow_error}). No Scheduler dispatch or external write occurred."
        )
    allowed_tools, tools_error = _json_list(allowed_tools_json)
    if tools_error:
        return (
            "Nanobot mission rejected: allowed_tools_json must be a JSON array "
            f"({tools_error}). No Scheduler dispatch or external write occurred."
        )
    context_refs, refs_error = _json_list(context_refs_json)
    if refs_error:
        return (
            "Nanobot mission rejected: context_refs_json must be a JSON array "
            f"({refs_error}). No Scheduler dispatch or external write occurred."
        )

    effective_authority, authority_note = _effective_authority(
        requested_authority=requested_authority,
        user_confirmation=user_confirmation,
        approval=approval,
    )
    task_type = "calendar_mission" if selected_domain in _CALENDAR_DOMAINS else "nanobot_mission"
    selected_result_channel = (
        str(result_channel or "").strip()
        or ("calendar_result" if task_type == "calendar_mission" else "nanobot_mission_result")
    )
    params = {
        "schema": "goslo_nanobot_mission_request_v1",
        "source": "goslo_nanobot_mission_request",
        "goal": selected_goal,
        "domain": selected_domain,
        "mode": selected_mode,
        "collaboration_mode": selected_mode,
        "authority": effective_authority,
        "requested_authority": requested_authority,
        "authority_note": authority_note,
        "workflow_hint": " ".join(str(workflow_hint or "").split())[:2000],
        "workflow": workflow,
        "allowed_tools": allowed_tools[:50],
        "context_refs": context_refs[:50],
        "expected_report": " ".join(str(expected_report or "").split())[:1000],
        "hitl_policy": str(hitl_policy or "ask_before_external_write").strip()
        or "ask_before_external_write",
        "result_channel": selected_result_channel,
        "nanobot_capabilities": _mission_capability_profile(
            task_type=task_type,
            mode=selected_mode,
            authority=effective_authority,
        ),
        "mission_protocol": _mission_protocol(selected_mode),
        "report_contract": _mission_report_contract(task_type),
        "task_policy": {
            "agentic_worker": True,
            "brain_role": "foreground_interaction_and_user_alignment",
            "nanobot_role": "background_investigation_planning_and_execution_with_authority_limits",
            "workflow_guided": selected_mode == "guided_workflow",
            "workflow_is_playbook_not_dead_pipeline": True,
            "self_investigation_required_before_calendar_write": task_type == "calendar_mission",
            "pause_status_for_human_decision": "needs_user_decision",
        },
        "instructions": _mission_instructions(
            task_type=task_type,
            mode=selected_mode,
            authority=effective_authority,
        ),
    }
    if _approved(approval) or user_confirmation:
        params["approval"] = approval or {"approved": True}
        params["user_confirmed"] = True
        params["calendar_write_approved"] = task_type == "calendar_mission"
        params["approval_source"] = str(approval.get("source") or "nanobot_mission_request")
    if effective_authority == "operator_write":
        params["operator_mode"] = True

    dispatcher = task_dispatcher
    if dispatcher is None:
        from parrot.brain.tools.dispatch_task import do_dispatch_task

        dispatcher = do_dispatch_task

    selected_priority = _priority(priority)
    try:
        task_id = await dispatcher(task_type, params, selected_priority)
    except Exception as exc:
        logger.exception("nanobot_mission_request dispatch failed")
        return (
            "Nanobot mission dispatch failed "
            f"({type(exc).__name__}: {exc}). No external write, Graphiti write, "
            "or L2-B mutation occurred in this tool."
        )

    downgrade = f" Authority note: {authority_note}" if authority_note else ""
    return (
        "Nanobot mission dispatched "
        f"(task={task_id}, task_type={task_type}, mode={selected_mode}, "
        f"authority={effective_authority}, result_channel={selected_result_channel}). "
        "Nanobot may investigate, use allowed tools, report draft_ready, or pause "
        "with needs_user_decision when conflicts, ambiguity, or approval are needed."
        f"{downgrade}"
    )


def _domain(value: str) -> str:
    raw = str(value or "general").strip().lower().replace("-", "_")
    aliases = {
        "google calendar": "google_calendar",
        "calendar_event": "calendar",
        "meeting": "calendar",
        "meetings": "calendar",
    }
    return aliases.get(raw, raw or "general")


def _mode(value: str) -> str:
    raw = str(value or "flexible").strip().lower().replace("-", "_")
    aliases = {
        "guided": "guided_workflow",
        "workflow": "guided_workflow",
        "strict": "guided_workflow",
        "agentic": "flexible",
    }
    raw = aliases.get(raw, raw)
    return raw if raw in _MISSION_MODES else "flexible"


def _authority(value: str) -> str:
    raw = str(value or "draft_only").strip().lower().replace("-", "_")
    aliases = {
        "readonly": "read_only",
        "draft": "draft_only",
        "approved": "approved_write",
        "write": "approved_write",
        "operator": "operator_write",
    }
    raw = aliases.get(raw, raw)
    return raw if raw in _AUTHORITY_VALUES else "draft_only"


def _effective_authority(
    *,
    requested_authority: str,
    user_confirmation: bool,
    approval: dict[str, Any],
) -> tuple[str, str]:
    if requested_authority in {"read_only", "draft_only"}:
        return requested_authority, ""
    if requested_authority == "operator_write":
        if _boolish(approval.get("operator_mode"), False):
            return "operator_write", ""
        if user_confirmation or _approved(approval):
            return (
                "approved_write",
                "requested operator_write but no operator_mode approval was present; downgraded to approved_write",
            )
        return (
            "draft_only",
            "requested operator_write without explicit approval; downgraded to draft_only",
        )
    if user_confirmation or _approved(approval):
        return "approved_write", ""
    return (
        "draft_only",
        "requested approved_write without explicit user/HITL approval; downgraded to draft_only",
    )


def _approved(approval: dict[str, Any]) -> bool:
    return any(
        _boolish(approval.get(key), False)
        for key in ("approved", "hitl_approved", "user_confirmed", "calendar_write_approved")
    )


def _mission_instructions(*, task_type: str, mode: str, authority: str) -> str:
    common = (
        "Treat this as an agentic mission, not a fixed endpoint call. Start by "
        "collecting relevant context, then decide whether to complete, draft, "
        "or pause. If the task needs user judgment, missing data, conflict "
        "resolution, or write approval, return status=needs_user_decision with "
        "findings, conflicts, options, recommended_option, and proposed_write "
        "when applicable. "
    )
    if mode == "guided_workflow":
        common += (
            "Follow workflow_hint/workflow as a playbook, but each phase may "
            "self-investigate and may pause when context changes the plan. "
        )
    else:
        common += (
            "Use flexible planning: choose the needed tools and investigation "
            "steps within the authority boundary. "
        )
    if task_type == "calendar_mission":
        common += (
            "For Calendar work, inspect relevant events before any write, check "
            "time overlaps and ambiguity, and never call Calendar create/patch/"
            "delete unless authority is approved_write/operator_write and "
            "approval metadata is present. "
        )
    if authority in {"read_only", "draft_only"}:
        common += "External writes are forbidden for this mission."
    return common


def _mission_capability_profile(*, task_type: str, mode: str, authority: str) -> dict[str, Any]:
    can_write = authority in {"approved_write", "operator_write"}
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
        "calendar_conflict_analysis": task_type == "calendar_mission",
        "calendar_write_actuator_available": task_type == "calendar_mission" and can_write,
    }


def _mission_protocol(mode: str) -> dict[str, Any]:
    return {
        "input_style": "natural_language_goal_plus_constraints",
        "mode": mode,
        "flexible_mode": mode == "flexible",
        "guided_workflow_mode": mode == "guided_workflow",
        "workflow_semantics": "playbook_with_agentic_investigation_per_phase",
        "pause_status": "needs_user_decision",
        "terminal_success_statuses": ["draft_ready", "completed"],
        "terminal_failure_status": "failed",
        "approval_boundary": "external_write_requires_explicit_hitl_or_operator_approval",
    }


def _mission_report_contract(task_type: str) -> list[str]:
    fields = [
        "schema",
        "status",
        "domain",
        "goal",
        "mode",
        "authority",
        "findings",
        "investigation_trace",
        "options",
        "recommended_option",
        "requires_approval",
        "reason",
        "summary",
    ]
    if task_type == "calendar_mission":
        fields.extend([
            "conflicts",
            "proposed_write",
            "execution_policy",
            "workflow_phase_results",
            "write_result",
        ])
    return fields


def _json_object(value: str | dict[str, Any], *, default: dict[str, Any]) -> tuple[dict[str, Any], str]:
    if isinstance(value, dict):
        return dict(value), ""
    decoded, error = _json_any(value, default=default)
    if error:
        return {}, error
    if isinstance(decoded, dict):
        return dict(decoded), ""
    return {}, "top-level JSON value must be an object"


def _json_list(value: str | list[Any]) -> tuple[list[Any], str]:
    if isinstance(value, list):
        return list(value), ""
    decoded, error = _json_any(value, default=[])
    if error:
        return [], error
    if isinstance(decoded, list):
        return list(decoded), ""
    return [], "top-level JSON value must be an array"


def _json_any(value: str | dict[str, Any] | list[Any], *, default: Any) -> tuple[Any, str]:
    if isinstance(value, (dict, list)):
        return value, ""
    raw = str(value or "").strip()
    if not raw:
        return default, ""
    try:
        return json.loads(raw), ""
    except json.JSONDecodeError as exc:
        return default, str(exc)


def _priority(value: str) -> str:
    selected = str(value or "normal").strip().lower()
    return selected if selected in {"reflex", "high", "normal", "low"} else "normal"


def _boolish(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on", "approved"}


__all__ = ["nanobot_mission_request", "do_nanobot_mission_request"]
