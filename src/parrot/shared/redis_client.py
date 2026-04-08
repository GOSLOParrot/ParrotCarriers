"""Redis connection factory."""

from __future__ import annotations

import redis.asyncio as aioredis

from parrot.shared.config import RedisConfig

_pool: aioredis.ConnectionPool | None = None


async def get_redis(config: RedisConfig | None = None) -> aioredis.Redis:
    """Return a shared async Redis client."""
    global _pool
    if _pool is None:
        cfg = config or RedisConfig()
        _pool = aioredis.ConnectionPool.from_url(cfg.url, decode_responses=True)
    return aioredis.Redis(connection_pool=_pool)


async def close_redis() -> None:
    global _pool
    if _pool is not None:
        await _pool.disconnect()
        _pool = None
