"""py-trees Blackboard V2 integration + optional Redis persistence adapter.

Two layers coexist here (Sprint 1 S1.A):

1. **Scheduler-internal namespace** (`scheduler/*`) — kept for BT Router
   backward-compat: `active_tasks`, `behavior_mode`, `current_event`,
   `route_result`. These are scheduler implementation details and are NOT
   declared in `shared/bb_schema.py`.

2. **Cross-module BB (bb_schema.BB_KEYS)** — 19 keys across 4 scopes
   (global / session / tick / transient), each with a declared single
   writer. Modules open a Client via `open_bb_client(name, writer=...)`
   which registers WRITE on the keys they own and READ on everything
   else. This enforces the "single-writer per key" contract from
   `ar_feature_vision.md §3.5` without a custom runtime checker.

Usage (cross-module):

    from parrot.scheduler.blackboard import open_bb_client

    bb = open_bb_client(name="telemetry_receiver",
                        writer="brain.telemetry_receiver")
    bb.set("tick/body_state", "flying")      # WRITE allowed
    bb.get("session/visual_state")           # READ allowed
    # bb.set("session/visual_state", ...)    # raises AttributeError

py-trees Blackboard is in-process memory. The RedisBlackboardSync adapter
optionally mirrors selected keys to/from Redis Hash for cross-process sharing.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import py_trees

from parrot.shared.bb_schema import BB_KEYS, BbScope, BlackboardKey
from parrot.shared.parrot_actions import BehaviorMode

logger = logging.getLogger(__name__)

BB_NS = "scheduler"


def init_scheduler_blackboard() -> py_trees.blackboard.Client:
    """Create and initialize the scheduler's Blackboard client with defaults."""
    bb = py_trees.blackboard.Client(name="SchedulerInit", namespace=BB_NS)
    bb.register_key(key="active_tasks", access=py_trees.common.Access.WRITE)
    bb.register_key(key="behavior_mode", access=py_trees.common.Access.WRITE)
    bb.register_key(key="current_event", access=py_trees.common.Access.WRITE)
    bb.register_key(key="route_result", access=py_trees.common.Access.WRITE)

    bb.active_tasks = {}
    bb.behavior_mode = BehaviorMode.BASE | BehaviorMode.COMPANION
    bb.current_event = {}
    bb.route_result = {}

    return bb


# ──────────────────────────────────────────────────────────────
# Cross-module BB (bb_schema.BB_KEYS) — writer-based access
# ──────────────────────────────────────────────────────────────

def open_bb_client(
    name: str,
    writer: str | None = None,
) -> py_trees.blackboard.Client:
    """Open a py-trees Blackboard Client with writer-based access on BB_KEYS.

    Every declared key in `BB_KEYS` is registered on the returned Client:
        - WRITE access if `key.writer == writer`
        - READ  access otherwise

    This means any attempt by a module to write to a key it does not own
    raises py-trees' `AttributeError` at runtime, turning the single-writer
    contract into a hard assertion.

    Use `client.set("<scope>/<name>", value)` / `client.get("<scope>/<name>")`
    to read/write — attribute access (`client.global.user_profile`) breaks
    because '/' is not a valid attribute character; the explicit `set/get`
    methods use py-trees' full-key addressing.

    Pass `writer=None` to get a read-only observer client (useful for
    dispatchers / injectors that aggregate across scopes).
    """
    client = py_trees.blackboard.Client(name=name)
    for k in BB_KEYS:
        access = (
            py_trees.common.Access.WRITE
            if writer is not None and k.writer == writer
            else py_trees.common.Access.READ
        )
        client.register_key(key=k.name, access=access)
    return client


def iter_keys_for_writer(writer: str) -> tuple[BlackboardKey, ...]:
    """All BB_KEYS whose writer equals `writer`."""
    return tuple(k for k in BB_KEYS if k.writer == writer)


def iter_keys_by_scope(scope: BbScope) -> tuple[BlackboardKey, ...]:
    """All BB_KEYS within a scope (thin re-export of bb_schema helper)."""
    return tuple(k for k in BB_KEYS if k.scope == scope)


class RedisBlackboardSync:
    """Optional adapter: sync py-trees Blackboard keys ↔ Redis Hash.

    Usage (P2+):
        sync = RedisBlackboardSync(redis, namespace="scheduler")
        await sync.push("active_tasks")   # BB → Redis
        await sync.pull("behavior_mode")  # Redis → BB
    """

    def __init__(self, redis_client: Any, namespace: str = BB_NS):
        self._redis = redis_client
        self._hash_key = f"parrot.bb.{namespace}"
        self._bb = py_trees.blackboard.Client(
            name="RedisSync", namespace=namespace
        )

    async def push(self, key: str) -> None:
        """Push a Blackboard key to Redis Hash."""
        self._bb.register_key(key=key, access=py_trees.common.Access.READ)
        try:
            value = getattr(self._bb, key)
            await self._redis.hset(self._hash_key, key, json.dumps(value, default=str))
            logger.debug("BB→Redis: %s/%s", self._hash_key, key)
        except KeyError:
            logger.warning("BB push: key '%s' not found in Blackboard", key)

    async def pull(self, key: str) -> Any | None:
        """Pull a value from Redis Hash into Blackboard."""
        self._bb.register_key(key=key, access=py_trees.common.Access.WRITE)
        raw = await self._redis.hget(self._hash_key, key)
        if raw is None:
            return None
        try:
            value = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            value = raw
        setattr(self._bb, key, value)
        logger.debug("Redis→BB: %s/%s = %s", self._hash_key, key, value)
        return value


__all__ = [
    "BB_NS",
    "RedisBlackboardSync",
    "init_scheduler_blackboard",
    "iter_keys_by_scope",
    "iter_keys_for_writer",
    "open_bb_client",
]
