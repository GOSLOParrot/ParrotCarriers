"""Brain function tools — available to the LLM during AgentSession."""

from __future__ import annotations

import os

from parrot.brain.tools.animate import animate
from parrot.brain.tools.dispatch_task import dispatch_task
from parrot.brain.tools.fly_to import fly_to
from parrot.brain.tools.manage_episode import manage_episode
from parrot.brain.tools.query_memory import query_memory
from parrot.brain.tools.query_scene import query_scene
from parrot.brain.tools.remember import remember
from parrot.brain.tools.set_mode import set_mode
from parrot.brain.tools.set_video_tier import set_video_tier

ALL_TOOLS = [
    fly_to, animate, dispatch_task,
    remember, query_memory, query_scene, set_mode,
    manage_episode, set_video_tier,
]

if os.getenv("PARROT_ENABLE_IDENTIFY_OBJECT_TOOL", "0").lower() in {"1", "true", "yes"}:
    # identify_object is an on-demand conscious vision tool, but the current
    # implementation still lacks captureSnapshot and same-turn visual evidence.
    # Keep it opt-in so unfinished discovery behavior cannot steal Gemini turns
    # during connection/audio stability tests.
    from parrot.brain.tools.identify_object import identify_object
    ALL_TOOLS.append(identify_object)

__all__ = [
    "fly_to", "animate", "dispatch_task",
    "remember", "query_memory", "query_scene", "set_mode",
    "manage_episode", "set_video_tier",
    "ALL_TOOLS",
]

if "identify_object" in globals():
    __all__.append("identify_object")
