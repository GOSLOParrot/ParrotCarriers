"""Module registry — tracks registered modules via Redis Hash.

Handles registration, discovery, and online/offline status.
"""

from __future__ import annotations

import json
import logging
import time

from parrot.bus.manifest import ModuleManifest
from parrot.shared.constants import HASH_HEARTBEAT, HASH_MODULES
from parrot.shared.redis_client import get_redis

logger = logging.getLogger(__name__)


async def register_module(manifest: ModuleManifest) -> None:
    """Register a module on the bus."""
    r = await get_redis()
    payload = {
        "module_type": manifest.module_type.value,
        "layers": [layer.value for layer in manifest.layers],
        "registered_at": time.time(),
    }
    await r.hset(HASH_MODULES, manifest.module_id, json.dumps(payload))
    await r.hset(HASH_HEARTBEAT, manifest.module_id, str(time.time()))
    logger.info("Module registered: %s (%s)", manifest.module_id, manifest.module_type.value)


async def deregister_module(module_id: str) -> None:
    """Remove a module from the bus."""
    r = await get_redis()
    await r.hdel(HASH_MODULES, module_id)
    await r.hdel(HASH_HEARTBEAT, module_id)
    logger.info("Module deregistered: %s", module_id)


async def list_modules() -> dict[str, dict]:
    """Return all registered modules."""
    r = await get_redis()
    raw = await r.hgetall(HASH_MODULES)
    return {k: json.loads(v) for k, v in raw.items()}


async def is_module_online(module_id: str, timeout_s: float = 60.0) -> bool:
    """Check if a module's heartbeat is within the timeout window."""
    r = await get_redis()
    last_beat = await r.hget(HASH_HEARTBEAT, module_id)
    if last_beat is None:
        return False
    return (time.time() - float(last_beat)) < timeout_s
