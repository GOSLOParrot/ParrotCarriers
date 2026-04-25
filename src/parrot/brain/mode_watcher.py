"""BehaviorMode dynamic switching — listens for mode changes via Redis.

Flow:
  External trigger (tool, Scheduler, or direct Redis write)
    → Redis Pub/Sub CH_BEHAVIOR_MODE
    → Brain picks up new mode
    → ParrotSoul regenerates instructions
    → session.update_instructions()

Also provides set_behavior_mode() for programmatic mode changes.
"""

from __future__ import annotations

import asyncio
import json
import logging

from livekit.agents import AgentSession

from parrot.brain.soul import get_instructions
from parrot.shared.constants import CH_BEHAVIOR_MODE
from parrot.shared.parrot_actions import BehaviorMode
from parrot.shared.redis_client import get_redis

logger = logging.getLogger(__name__)

_HASH_BEHAVIOR_MODE = "parrot.bb.scheduler"
_HASH_FIELD = "behavior_mode"


def _sync_injector_mode(mode: BehaviorMode) -> None:
    """Forward the new mode to the active ContextInjector (if running)."""
    try:
        from parrot.brain.context_injector import get_context_injector
        injector = get_context_injector()
        if injector is not None:
            injector.set_mode(mode)
    except Exception:
        pass


def _parse_mode(raw: str | int) -> BehaviorMode:
    """Parse a BehaviorMode from a JSON/Redis value."""
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            pass
    if isinstance(raw, int):
        return BehaviorMode(raw)
    if isinstance(raw, str):
        parts = [s.strip().upper() for s in raw.split("|") if s.strip()]
        mode = BehaviorMode(0)
        for p in parts:
            try:
                mode |= BehaviorMode[p]
            except KeyError:
                logger.warning("Unknown BehaviorMode flag: %s", p)
        return mode or (BehaviorMode.BASE | BehaviorMode.COMPANION)
    return BehaviorMode.BASE | BehaviorMode.COMPANION


async def set_behavior_mode(mode: BehaviorMode) -> None:
    """Write new BehaviorMode to Redis (triggers watchers in all Brain instances)."""
    r = await get_redis()
    value = mode.value
    await r.hset(_HASH_BEHAVIOR_MODE, _HASH_FIELD, json.dumps(value))
    await r.publish(CH_BEHAVIOR_MODE, json.dumps(value))
    logger.info("set_behavior_mode: %s (value=%d)", mode, value)


def attach_mode_watcher(session: AgentSession) -> asyncio.Task:
    """Start a background task that watches for BehaviorMode changes.

    When a change arrives, regenerates ParrotSoul instructions and
    calls session.update_instructions() to hot-swap the system prompt.
    """
    current_mode = BehaviorMode.BASE | BehaviorMode.COMPANION

    def _try_update_instructions(new_instructions: str, reason: str) -> None:
        updater = getattr(session, "update_instructions", None)
        if callable(updater):
            updater(new_instructions)
            return
        logger.warning(
            "mode_watcher: AgentSession.update_instructions unavailable; "
            "mode context updated locally only (%s)",
            reason,
        )

    async def _watch() -> None:
        nonlocal current_mode
        try:
            r = await get_redis()

            stored = await r.hget(_HASH_BEHAVIOR_MODE, _HASH_FIELD)
            if stored:
                current_mode = _parse_mode(stored)
                _sync_injector_mode(current_mode)
                new_instructions = get_instructions(current_mode)
                _try_update_instructions(new_instructions, "init")
                logger.info("mode_watcher: initialized with %s", current_mode)

            pubsub = r.pubsub()
            await pubsub.subscribe(CH_BEHAVIOR_MODE)
            logger.info("mode_watcher: listening on %s", CH_BEHAVIOR_MODE)

            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue
                new_mode = _parse_mode(message["data"])
                if new_mode == current_mode:
                    continue

                current_mode = new_mode
                _sync_injector_mode(current_mode)
                new_instructions = get_instructions(current_mode)
                _try_update_instructions(new_instructions, "switch")
                logger.info("mode_watcher: switched to %s", current_mode)

        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception("mode_watcher: error in watch loop")

    task = asyncio.create_task(_watch())
    return task
