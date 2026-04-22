"""Observation Log helper — Sprint 1 T9.

Writes a lightweight audit record into the Redis Stream `STREAM_OBS_LOG`
(`parrot.obs_log`) every time Context Injector makes a consciousness-layer
dispatch decision. Unlike `STREAM_EVENT_LOG` (L0 — gated by "something
real happened"), the observation log records every decision path including
Layer-1 "subconscious, no Gemini touch" — so offline reflection tooling can
reconstruct GOSLO's internal dialogue without rerunning the session.

Schema (Redis XADD field dict):
    ts       Unix epoch seconds (float, formatted "%.6f")
    kind     short event-type tag (e.g. "bb_change", "dispatch_skip")
    layer    consciousness layer as string: "1" | "2" | "3"
             (distinct from shared.event_log.EventLayer reflex/intent/task)
    actor    producing module, default "brain.context_injector"
    payload  JSON-encoded arbitrary dict (Enum values stringified)

All writes are fire-and-forget (`asyncio.create_task`) to keep them off the
latency budget of the caller. Redis outages degrade to a logged warning,
never a raised exception — losing an audit line must not brick GOSLO.

Stream is bounded with XADD MAXLEN ≈ 10 000 entries (approximate trim) —
enough for several hours of noisy interaction at <1 event/s.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from enum import Enum
from typing import Any

from parrot.shared.constants import STREAM_OBS_LOG

logger = logging.getLogger(__name__)

_MAXLEN = 10_000
_DEFAULT_ACTOR = "brain.context_injector"


def _encode(value: Any) -> Any:
    """JSON-friendly conversion; Enum → .value, fallback to str via default."""
    if isinstance(value, Enum):
        return value.value
    return value


def _build_fields(
    kind: str,
    layer: int,
    payload: dict[str, Any] | None,
    actor: str,
) -> dict[str, str]:
    safe_payload = {k: _encode(v) for k, v in (payload or {}).items()}
    return {
        "ts": f"{time.time():.6f}",
        "kind": kind,
        "layer": str(layer),
        "actor": actor,
        "payload": json.dumps(safe_payload, ensure_ascii=False, default=str),
    }


async def _write(fields: dict[str, str]) -> None:
    try:
        from parrot.shared.redis_client import get_redis

        r = await get_redis()
        await r.xadd(STREAM_OBS_LOG, fields, maxlen=_MAXLEN, approximate=True)
    except Exception:
        logger.debug("obs_log: xadd failed (redis offline?)", exc_info=True)


def log_obs_event(
    kind: str,
    layer: int,
    payload: dict[str, Any] | None = None,
    *,
    actor: str = _DEFAULT_ACTOR,
) -> None:
    """Fire-and-forget: record one consciousness-layer observation.

    `layer` is the **consciousness** tier (1/2/3), not EventLayer. Use:
        1 — subconscious only (BB written, Gemini untouched)
        2 — autonomous action (BB state changed by GOSLO itself, e.g. soul
            constraints tightened, tier downgraded)
        3 — reported to Gemini (C3 chat_ctx append or C4 generate_reply)

    Safe to call from sync or async context; always returns synchronously.
    """
    fields = _build_fields(kind, layer, payload, actor)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # Sync caller with no loop — just drop the record (obs_log is an
        # audit aid, not a correctness requirement).
        logger.debug("obs_log: no running loop, dropping %s", kind)
        return

    loop.create_task(_write(fields))


__all__ = ["log_obs_event"]
