"""Scheduler task type catalog.

The Scheduler can route many event shapes, but Plan step dispatch currently
expects Nanobot-backed tasks because Plan completion depends on Nanobot result
or timeout callbacks. Keeping the catalog here lets Brain validate that a Plan
step can actually return before it is dispatched.
"""

from __future__ import annotations

GENERAL_NANOBOT_TASK_TYPES = frozenset({
    "research",
    "summarize",
    "remind",
    "memory_consolidation",
    "vocabulary_learn",
})

GOOGLE_WORKSPACE_TASK_TYPES = frozenset({
    "calendar_fetch",
    "calendar_create",
    "calendar_patch",
    "calendar_delete",
    "message_check",
})

NANOBOT_TASK_TYPES = GENERAL_NANOBOT_TASK_TYPES | GOOGLE_WORKSPACE_TASK_TYPES


def is_nanobot_task_type(task_type: str) -> bool:
    """Return whether Scheduler will route this task to Nanobot result flow."""
    return task_type in NANOBOT_TASK_TYPES
