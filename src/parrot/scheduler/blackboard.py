"""E3: Redis Blackboard — shared state read/write.

Wraps Redis Hash operations for the Scheduler's state management.
"""

from __future__ import annotations

import json
from typing import Any

from parrot.shared.constants import BB_PARROT_STATE
from parrot.shared.redis_client import get_redis


class Blackboard:
    """Redis-backed shared state store."""

    def __init__(self, namespace: str = BB_PARROT_STATE):
        self._ns = namespace

    async def get(self, key: str) -> Any | None:
        r = await get_redis()
        val = await r.hget(self._ns, key)
        if val is None:
            return None
        try:
            return json.loads(val)
        except (json.JSONDecodeError, TypeError):
            return val

    async def set(self, key: str, value: Any) -> None:
        r = await get_redis()
        await r.hset(self._ns, key, json.dumps(value))

    async def delete(self, key: str) -> None:
        r = await get_redis()
        await r.hdel(self._ns, key)

    async def get_all(self) -> dict[str, Any]:
        r = await get_redis()
        raw = await r.hgetall(self._ns)
        result = {}
        for k, v in raw.items():
            try:
                result[k] = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                result[k] = v
        return result
