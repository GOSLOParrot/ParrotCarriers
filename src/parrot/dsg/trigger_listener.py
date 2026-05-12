"""DSG Trigger Listener — subscribes to Redis DSG channels and routes to Brain.

Runs as a background task in the Brain process. When DSG events arrive
(from real DSG or simulation script), it:
  1. Updates Context Injector's scene context (silent)
  2. For important triggers (MISSING, NEW), notifies Brain via generate_reply
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging

from parrot.shared.constants import CH_DSG_EVENTS, CH_DSG_SCENE_UPDATE
from parrot.shared.redis_client import get_redis

logger = logging.getLogger(__name__)


async def start_trigger_listener() -> asyncio.Task:
    """Start background listener for DSG events. Returns the task handle.

    FIX (2026-05-12 Phase 5.1, plan §5.1): same Bug N pattern that was
    fixed in :mod:`parrot.brain.agent`'s scheduler-result listener now
    applied here. A malformed Redis payload, JSONDecodeError, or
    transient Brain-side handler crash MUST NOT terminate the
    listener — DSG sources fan out at 0.2-2 Hz and the next event
    must still be picked up.

    Each per-message handler call gets its own try/except so the
    outer ``async for`` loop survives. Connection errors still break
    out so the supervisor / Brain restart path can react.
    """

    async def _listen():
        pubsub = None
        try:
            r = await get_redis()
            pubsub = r.pubsub()
            await pubsub.subscribe(CH_DSG_EVENTS, CH_DSG_SCENE_UPDATE)
            logger.info("dsg_trigger_listener: subscribed to %s, %s", CH_DSG_EVENTS, CH_DSG_SCENE_UPDATE)

            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue

                try:
                    channel = message["channel"]
                    data = message["data"]

                    if channel == CH_DSG_SCENE_UPDATE:
                        await _handle_scene_update(data)
                    elif channel == CH_DSG_EVENTS:
                        await _handle_trigger(data)
                except asyncio.CancelledError:
                    raise
                except Exception:
                    logger.exception(
                        "dsg_trigger_listener: per-message handler failed; "
                        "staying subscribed for the next event"
                    )

        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception("dsg_trigger_listener: error")
        finally:
            if pubsub is not None:
                with contextlib.suppress(Exception):
                    await pubsub.unsubscribe(CH_DSG_EVENTS, CH_DSG_SCENE_UPDATE)
                with contextlib.suppress(Exception):
                    await pubsub.close()

    return asyncio.create_task(_listen())


async def _handle_scene_update(data: str) -> None:
    """Route scene summary to Context Injector."""
    from parrot.brain.context_injector import get_context_injector

    injector = get_context_injector()
    if injector:
        await injector.inject_scene(data)


async def _handle_trigger(data: str) -> None:
    """Route individual triggers — MISSING/NEW → active notification, others → context."""
    from parrot.brain.context_injector import get_context_injector

    try:
        trigger = json.loads(data)
    except json.JSONDecodeError:
        return

    injector = get_context_injector()
    if not injector:
        return

    trigger_type = trigger.get("type", "")
    label = trigger.get("label", "unknown")
    description = trigger.get("description", "")

    if trigger_type in ("missing", "new"):
        msg = f"[Scene change] {description or f'{label} — {trigger_type}'}"
        await injector.inject_notification(msg)
        logger.info("dsg_trigger: active notification → %s", msg)
    else:
        await injector.inject_scene(f"Object update: {description}")
