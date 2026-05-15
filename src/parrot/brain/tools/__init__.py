"""Brain function tools — available to the LLM during AgentSession."""

from __future__ import annotations

import os

from parrot.brain.tools.animate import animate
from parrot.brain.tools.dispatch_task import dispatch_task
from parrot.brain.tools.fly_to import fly_to
from parrot.brain.tools.manage_episode import manage_episode
from parrot.brain.tools.play_capability import play_capability
from parrot.brain.tools.query_memory import query_memory
from parrot.brain.tools.query_scene import query_scene
from parrot.brain.tools.remember import remember
from parrot.brain.tools.set_mode import set_mode
from parrot.brain.tools.set_video_tier import set_video_tier
from parrot.brain.tools._capability_gate import active_model_id
from parrot.brain.model_manifest_registry import get_model_manifest_registry

ALL_TOOLS = [
    fly_to, animate, play_capability, dispatch_task,
    remember, query_memory, query_scene, set_mode,
    manage_episode, set_video_tier,
]


def tools_for_active_model():
    """Return Brain tools with model-specific unsafe verbs hidden."""
    model_id = active_model_id()
    registry = get_model_manifest_registry()
    tools = [
        dispatch_task,
        remember,
        query_memory,
        query_scene,
        set_mode,
        manage_episode,
        set_video_tier,
        play_capability,
    ]
    if registry.supports(model_id, "fly"):
        tools.insert(0, fly_to)
    if registry.parrot_reflex_enabled(model_id):
        insert_at = 1 if fly_to in tools else 0
        tools.insert(insert_at, animate)
    if "identify_object" in globals():
        tools.append(identify_object)
    return tools

if os.getenv("PARROT_ENABLE_IDENTIFY_OBJECT_TOOL", "0").lower() in {"1", "true", "yes"}:
    # Sprint4 Phase 4 W4-5 (2026-04-30) rewrote identify_object as a staged
    # L0-text → L1-Graphiti → L2-unknown pipeline with sync budget +
    # sighting EcpEvent emission (entry doc §8.1 L11; audit_identify_object
    # _no_screenshot_20260420.md §9). Felt-experience闭环 restored —
    # `_deep_search` removed (audit §3.4); option α return 让 GOSLO 自决
    # 下一步 (dispatch_task / save_new / 描述 / 反问 用户).
    #
    # Env gate KEPT for one more shake-down cycle: real-device validation +
    # observer.sighting wiring confirmation in identify_object/Phase 4 W5.
    # Un-gate (move to ALL_TOOLS unconditionally) when:
    #   1. P2.5 真机 spike confirms 1.9s budget holds end-to-end (entry doc §8.1 L11)
    #   2. Formal photo evidence path lands (ECP metadata + HTTP/storage asset)
    #   3. observer.sighting archiver path verified against Graphiti live
    from parrot.brain.tools.identify_object import identify_object
    ALL_TOOLS.append(identify_object)

__all__ = [
    "fly_to", "animate", "play_capability", "dispatch_task",
    "remember", "query_memory", "query_scene", "set_mode",
    "manage_episode", "set_video_tier",
    "ALL_TOOLS", "tools_for_active_model",
]

if "identify_object" in globals():
    __all__.append("identify_object")
