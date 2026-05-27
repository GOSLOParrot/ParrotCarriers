"""Scheduler task type catalog and Nanobot mission normalization.

The Scheduler can route many event shapes, but Plan step dispatch expects a
Nanobot-backed task because Plan completion depends on Nanobot result or
timeout callbacks. Keeping the catalog here lets Brain validate that a Plan
step can actually return before it is dispatched while still accepting
natural-language mission aliases that normalize to a routable Nanobot mission.
"""

from __future__ import annotations

from typing import Any

GENERAL_NANOBOT_TASK_TYPES = frozenset({
    "research",
    "summarize",
    "remind",
    "memory_consolidation",
    "diary_query",
    "ref_scan",
    "vocabulary_learn",
    "nanobot_mission",
})

GOOGLE_WORKSPACE_TASK_TYPES = frozenset({
    "calendar_fetch",
    "calendar_create",
    "calendar_patch",
    "calendar_delete",
    "calendar_mission",
    "message_check",
})

NANOBOT_TASK_TYPES = GENERAL_NANOBOT_TASK_TYPES | GOOGLE_WORKSPACE_TASK_TYPES

MISSION_TASK_ALIASES = frozenset({
    "",
    "mission",
    "agentic_mission",
    "background_mission",
    "natural_language_task",
    "nanobot",
    "nanobot_task",
    "nanobot_work",
})

CALENDAR_MISSION_ALIASES = frozenset({
    "calendar",
    "calendar_task",
    "schedule",
    "scheduling",
    "google_calendar",
    "google_calendar_mission",
    "calendar_agentic_mission",
})

CALENDAR_DOMAINS = frozenset({
    "calendar",
    "google_calendar",
    "schedule",
    "scheduling",
    "meeting",
    "meetings",
})


def is_nanobot_task_type(task_type: str) -> bool:
    """Return whether Scheduler will route this task to Nanobot result flow."""
    return bool(normalize_nanobot_task_type(task_type))


def normalize_nanobot_task_type(
    task_type: str,
    params: dict[str, Any] | None = None,
) -> str:
    """Return the routable Nanobot task type for a raw event shape.

    Fixed task types remain fixed. Natural-language mission aliases normalize
    to ``nanobot_mission`` or ``calendar_mission`` based on domain hints. Empty
    task types are accepted only when the params look like a mission request,
    so arbitrary malformed events still fall through to BrainDirect.
    """

    raw = str(task_type or "").strip().lower().replace("-", "_")
    payload = params if isinstance(params, dict) else {}
    if raw in NANOBOT_TASK_TYPES:
        return raw
    if raw in CALENDAR_MISSION_ALIASES:
        return "calendar_mission"
    if raw in MISSION_TASK_ALIASES:
        if raw == "" and not _looks_like_mission(payload):
            return ""
        return "calendar_mission" if _calendar_domain(payload) else "nanobot_mission"
    return ""


def _looks_like_mission(params: dict[str, Any]) -> bool:
    for key in ("goal", "mission", "query", "instructions", "workflow", "workflow_hint"):
        if str(params.get(key) or "").strip():
            return True
    return False


def _calendar_domain(params: dict[str, Any]) -> bool:
    raw = str(params.get("domain") or params.get("kind") or "").strip().lower().replace("-", "_")
    if raw in CALENDAR_DOMAINS:
        return True
    if str(params.get("calendar_id") or params.get("calendarId") or "").strip():
        return True
    goal = str(params.get("goal") or params.get("mission") or params.get("query") or "").lower()
    return any(word in goal for word in ("calendar", "schedule", "meeting"))
