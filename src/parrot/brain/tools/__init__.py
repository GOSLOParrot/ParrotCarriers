"""Brain function tools available to the LLM during AgentSession."""

from __future__ import annotations

import os

from parrot.brain.model_manifest_registry import get_model_manifest_registry
from parrot.brain.tools._capability_gate import active_model_id
from parrot.brain.tools.animate import (
    PARROT_ANIMATION_TOOLS,
    animate,
    play_dance,
    play_fly_pose,
    play_head_bob,
    play_idle,
    play_perch_pose,
    play_sit,
    play_sleep,
    play_wing_flap,
)
from parrot.brain.tools.calendar_change_request import calendar_change_request
from parrot.brain.tools.calendar_context import calendar_context
from parrot.brain.tools.calendar_task_status import calendar_task_status
from parrot.brain.tools.dispatch_task import dispatch_task
from parrot.brain.tools.fly_to import fly_to
from parrot.brain.tools.manage_episode import manage_episode
from parrot.brain.tools.perch_to_finger import perch_to_finger
from parrot.brain.tools.play_capability import play_capability
from parrot.brain.tools.query_etiquette_memory import query_etiquette_memory
from parrot.brain.tools.query_memory import query_memory
from parrot.brain.tools.query_scene import query_scene
from parrot.brain.tools.remember import remember
from parrot.brain.tools.return_to_view import return_to_view
from parrot.brain.tools.set_mode import set_mode
from parrot.brain.tools.set_video_tier import set_video_tier
from parrot.brain.tools.web_lookup_intent import web_lookup_intent
from parrot.shared.model_manifest import RESERVED_PARROT_CAPABILITY_IDS

_BASE_TOOLS = [
    fly_to,
    perch_to_finger,
    return_to_view,
    animate,
    *PARROT_ANIMATION_TOOLS,
    play_capability,
    dispatch_task,
    calendar_context,
    calendar_change_request,
    calendar_task_status,
    remember,
    query_memory,
    query_etiquette_memory,
    web_lookup_intent,
    query_scene,
    set_mode,
    manage_episode,
    set_video_tier,
]

ALL_TOOLS = list(_BASE_TOOLS)


def _env_enabled(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _active_pipeline_hint() -> str:
    try:
        from parrot.castle.runtime_config import resolve_runtime_config

        return str(resolve_runtime_config().line_id or "").strip().lower()
    except Exception:
        return os.getenv("PARROT_LLM_PIPELINE", "line_a").strip().lower() or "line_a"


def _gemini_provider_tools():
    """Provider-side tools for Gemini Live."""
    if not _env_enabled("PARROT_ENABLE_GEMINI_SEARCH_TOOL", True):
        return []
    if _active_pipeline_hint() != "line_a":
        return []
    try:
        from livekit.plugins import google

        return [google.tools.GoogleSearch()]
    except Exception:
        return []


def tools_for_active_model():
    """Return Brain tools with model-specific unsafe verbs hidden."""
    model_id = active_model_id()
    registry = get_model_manifest_registry()
    tools = _gemini_provider_tools() + [
        calendar_context,
        calendar_change_request,
        calendar_task_status,
        dispatch_task,
        remember,
        query_memory,
        query_etiquette_memory,
        web_lookup_intent,
        query_scene,
        set_mode,
        manage_episode,
        set_video_tier,
    ]
    declared_capabilities = registry.capability_ids(model_id)
    has_custom_capabilities = bool(declared_capabilities - RESERVED_PARROT_CAPABILITY_IDS)
    if has_custom_capabilities:
        tools.append(play_capability)
    if registry.supports(model_id, "fly"):
        tools.insert(0, fly_to)
    if registry.supports(model_id, "fly") and registry.supports(model_id, "perch"):
        insert_at = 1 if fly_to in tools else 0
        tools.insert(insert_at, perch_to_finger)
    if registry.supports(model_id, "fly"):
        insert_at = 1 if fly_to in tools else 0
        if perch_to_finger in tools:
            insert_at = max(insert_at, tools.index(perch_to_finger) + 1)
        tools.insert(insert_at, return_to_view)
    if registry.parrot_reflex_enabled(model_id):
        insert_at = 1 if fly_to in tools else 0
        for tool in (perch_to_finger, return_to_view):
            if tool in tools:
                insert_at = max(insert_at, tools.index(tool) + 1)
        for tool in reversed(PARROT_ANIMATION_TOOLS):
            tools.insert(insert_at, tool)
    if "identify_object" in globals():
        tools.append(identify_object)
    return tools


if _env_enabled("PARROT_ENABLE_IDENTIFY_OBJECT_TOOL", True):
    # Default-on T1 visual recognition bridge. Gemini Live receives native
    # video_input=True, but those frames are not auditable evidence. This tool
    # uses Parrot's visual evidence path plus L0/L1/Graphiti matching so GOSLO
    # can reason from concrete observations. Set the env var to 0 to disable.
    from parrot.brain.tools.identify_object import identify_object

    ALL_TOOLS.append(identify_object)
else:
    # importlib.reload() reuses the existing module dict. Remove the old symbol
    # so runtime tests or hot reloads cannot keep exposing a disabled tool.
    globals().pop("identify_object", None)


__all__ = [
    "fly_to",
    "perch_to_finger",
    "return_to_view",
    "animate",
    "play_idle",
    "play_fly_pose",
    "play_dance",
    "play_wing_flap",
    "play_perch_pose",
    "play_sit",
    "play_head_bob",
    "play_sleep",
    "PARROT_ANIMATION_TOOLS",
    "play_capability",
    "dispatch_task",
    "calendar_context",
    "calendar_change_request",
    "calendar_task_status",
    "remember",
    "query_memory",
    "query_etiquette_memory",
    "web_lookup_intent",
    "query_scene",
    "set_mode",
    "manage_episode",
    "set_video_tier",
    "ALL_TOOLS",
    "tools_for_active_model",
]

if "identify_object" in globals():
    __all__.append("identify_object")
