"""A10 Redis heartbeat writer — Sprint 3 T-P2.

Purpose: let the Castle-side PerceptionSupervisor know whether the A10 GPU
machine is alive. The A10 is a preemptible instance that can be reclaimed at
any time; Supervisor watches the Redis key TTL to detect this.

Protocol:
    Key   : PARROT_A10_HEARTBEAT_KEY (default "parrot:a10_heartbeat")
    Value : "alive"
    TTL   : 60s — if A10 crashes / is reclaimed, key expires in ≤60s
    Rate  : SETEX every 30s (half TTL = two misses before expiry)

Integration (three options — use whichever fits the A10 startup):

    1. Import and await start_a10_heartbeat() in your main A10 async entry:
       ```python
       from parrot.a10.heartbeat import start_a10_heartbeat
       task = asyncio.create_task(start_a10_heartbeat())
       ```

    2. Run standalone:
       ```bash
       python -m parrot.a10.heartbeat
       ```

    3. Bus on_mount() integration (if A10 runs a Bus worker):
       ```python
       mount.set_on_mount(lambda: asyncio.create_task(start_a10_heartbeat()))
       ```
"""

from __future__ import annotations

import asyncio
import logging
import os

logger = logging.getLogger(__name__)

_HEARTBEAT_KEY = os.getenv("PARROT_A10_HEARTBEAT_KEY", "parrot:a10_heartbeat")
_HEARTBEAT_TTL_S = int(os.getenv("PARROT_A10_HEARTBEAT_TTL", "60"))
_HEARTBEAT_INTERVAL_S = int(os.getenv("PARROT_A10_HEARTBEAT_INTERVAL", "30"))


async def start_a10_heartbeat() -> None:
    """Async task: write SETEX heartbeat every 30s until cancelled.

    Writes on mount immediately, then every _HEARTBEAT_INTERVAL_S seconds.
    Idempotent: safe to run multiple times (last writer wins).
    """
    from parrot.shared.redis_client import get_redis

    r = await get_redis()
    logger.info(
        "A10 heartbeat: starting (key=%s ttl=%ds interval=%ds)",
        _HEARTBEAT_KEY, _HEARTBEAT_TTL_S, _HEARTBEAT_INTERVAL_S,
    )

    # Write immediately on mount so Castle Supervisor sees us within 1 probe cycle
    await r.setex(_HEARTBEAT_KEY, _HEARTBEAT_TTL_S, "alive")
    logger.info("A10 heartbeat: initial write done (key=%s)", _HEARTBEAT_KEY)

    try:
        while True:
            await asyncio.sleep(_HEARTBEAT_INTERVAL_S)
            await r.setex(_HEARTBEAT_KEY, _HEARTBEAT_TTL_S, "alive")
            logger.debug("A10 heartbeat: refreshed (key=%s)", _HEARTBEAT_KEY)
    except asyncio.CancelledError:
        logger.info("A10 heartbeat: stopped (task cancelled)")
        raise


if __name__ == "__main__":
    import asyncio
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    async def _main() -> None:
        print(f"A10 heartbeat writer — key={_HEARTBEAT_KEY}, ttl={_HEARTBEAT_TTL_S}s")
        print("Press Ctrl+C to stop")
        await start_a10_heartbeat()

    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        print("\nA10 heartbeat writer stopped")
