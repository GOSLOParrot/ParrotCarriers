"""IdleArchiveTrigger (PERIODIC).

DSG-TRIGGER-V2 § 5.5 + DSG-ARCHIVE-V1 § 8.2.

Periodic check: when nanobot heartbeat indicates idle and Brain agent
is not in an active IntentEvent, fire ``SCAN_AND_ARCHIVE`` request to
push pending conversation snapshots through unified_filter + LLM →
Graphiti.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from parrot.dsg.archive import (
    ArchiveRequest,
    ArchiveRequestKind,
    ArchiveTarget,
)
from parrot.dsg.triggers.base import BaseTrigger, TriggerKind, TriggerOutcome

logger = logging.getLogger(__name__)


_DEFAULT_NANOBOT_IDLE_SECONDS = 600.0  # 10 min desktop baseline


class IdleArchiveTrigger(BaseTrigger):
    name = "idle_archive_trigger"
    kinds = [TriggerKind.PERIODIC]
    interval_seconds = 600.0

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._idle_threshold = _DEFAULT_NANOBOT_IDLE_SECONDS

    async def on_startup(self) -> TriggerOutcome | None:
        return None

    async def on_tick(self) -> TriggerOutcome | None:
        idle = await _is_nanobot_idle(self._idle_threshold)
        if not idle:
            return None
        if _intent_event_active():
            return None

        return TriggerOutcome(
            trigger_name=self.name,
            summary="nanobot idle — sweep archive queue",
            archive_request=ArchiveRequest(
                kind=ArchiveRequestKind.SCAN_AND_ARCHIVE,
                target=ArchiveTarget.CONVERSATION,
                target_id="*",
            ),
        )

    async def on_event(self, event: dict[str, Any]) -> TriggerOutcome | None:
        return None


async def _is_nanobot_idle(min_idle_seconds: float) -> bool:
    """Read Redis HASH ``parrot:nanobot_heartbeat`` and check last beat.

    DSG-ARCHIVE-V1 § 8.2. If Redis is unavailable, we conservatively
    return False (don't fire archive — wait for heartbeat).

    # TODO(Chat4-nanobot-heartbeat): SKELETON ONLY. The Redis HASH
    #   ``parrot:nanobot_heartbeat`` reader is wired; the **writer**
    #   (nanobot worker periodic update) is NOT implemented yet.
    #   Chat 4 must:
    #     1. Add nanobot.consumer or parrot_bus channel writer that
    #        emits ``HSET parrot:nanobot_heartbeat <worker_id> <ts>``
    #        every N seconds (suggest 60s).
    #     2. Wire writer to nanobot ``ParrotBusChannel`` lifecycle so
    #        idle = no recent task processing.
    #     3. Optionally add a "currently busy" flag for finer-grained
    #        idle detection (avoid kicking archive while task is mid-run).
    #   See: nanobot skill (.cursor/skills/nanobot/SKILL.md) for heartbeat
    #   pattern reference.
    """
    try:
        from parrot.shared.redis_client import get_redis
        r = await get_redis()
        busy_raw = await r.hget("parrot:nanobot_heartbeat", "main_worker_busy")
        if str(busy_raw or "").lower() in {"1", "true", "yes"}:
            return False
        last_ts_raw = await r.hget("parrot:nanobot_heartbeat", "main_worker")
        if last_ts_raw is None:
            return False
        try:
            last_ts = float(last_ts_raw)
        except (TypeError, ValueError):
            return False
        return (time.time() - last_ts) >= min_idle_seconds
    except Exception:
        return False


def _intent_event_active() -> bool:
    try:
        from parrot.dsg.l2b.intent_event_boundary import get_intent_event_handler
        return bool(get_intent_event_handler().current_event_id())
    except Exception:
        return False


__all__ = ["IdleArchiveTrigger"]
