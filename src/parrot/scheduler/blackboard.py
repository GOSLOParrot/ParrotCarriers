"""py-trees Blackboard V2 integration + optional Redis persistence adapter.

Namespace layout:
    /scheduler/active_tasks     — dict[task_id, TaskInfo]     WRITE: Scheduler nodes
    /scheduler/behavior_mode    — BehaviorMode Flag           WRITE: Brain (via Redis)
    /scheduler/current_event    — dict                        WRITE: event listener
    /scheduler/route_result     — dict                        WRITE: BT nodes
    /scheduler/resource_locks   — dict                        WRITE: lock nodes (P2)

py-trees Blackboard is in-process memory. The RedisBlackboardSync adapter
optionally mirrors selected keys to/from Redis Hash for cross-process sharing.
P1.5: in-process only; Redis sync added as needed.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import py_trees

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
