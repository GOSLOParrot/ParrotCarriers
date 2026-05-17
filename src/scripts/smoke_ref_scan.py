"""Smoke test CORE-015 ref_scan through Scheduler -> Nanobot -> Web ledger.

This script is read-only for real refs. It creates a temporary IdentityRefIndex
with one local file and remote placeholder refs, dispatches a read-only
``ref_scan`` task through the normal Scheduler/Nanobot Redis path, then reads
the Web Console result ledger to prove ``memory_ref_scan_result`` returned.

Usage:
  python src/scripts/smoke_ref_scan.py
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any

from redis.exceptions import RedisError

from parrot.bus.nanobot_consumer import NanobotConsumer
from parrot.dsg.identity_ref_index import MemoryIdentityRefIndex
from parrot.scheduler.service import SchedulerService
from parrot.shared.redis_client import close_redis, get_redis
from parrot.web_console.memory_ops import (
    dispatch_memory_ref_scan_plan,
    memory_ref_scan_result_history,
)


async def run_smoke(
    *,
    timeout_s: float,
    include_remote_placeholders: bool,
    remote_checks: bool,
) -> dict[str, Any]:
    try:
        redis = await get_redis()
        await redis.ping()
    except RedisError as exc:
        await close_redis()
        return {
            "success": False,
            "status": "skipped",
            "error": f"Redis unavailable: {exc}",
        }

    scheduler = SchedulerService()
    nanobot = NanobotConsumer()
    temp_dir = tempfile.TemporaryDirectory(prefix="parrot_ref_scan_smoke_")
    old_index_path = os.environ.get("PARROT_MEMORY_IDENTITY_REF_INDEX_PATH")
    try:
        temp_path = Path(temp_dir.name)
        smoke_file = temp_path / "Amiya.md"
        smoke_file.write_text("Amiya ref scan smoke\n", encoding="utf-8")
        os.environ["PARROT_MEMORY_IDENTITY_REF_INDEX_PATH"] = str(
            temp_path / "memory_identity_ref_index.json"
        )
        _seed_identity_ref_index(
            smoke_file=smoke_file,
            include_remote_placeholders=include_remote_placeholders,
        )

        await scheduler.start()
        await nanobot.start()
        # Scheduler command intake uses Redis Pub/Sub, so give the listener
        # tasks a moment to complete subscription before publishing once.
        await asyncio.sleep(0.75)
        dispatch = await dispatch_memory_ref_scan_plan(
            {
                "dry_run": False,
                "operator_mode": True,
                "priority": "low",
                "limit": 20,
                "remote_checks": ["url", "ecs", "graphiti"] if remote_checks else [],
            }
        )
        task_id = str((dispatch.get("data") or {}).get("task_id") or "")
        if not dispatch.get("success") or not task_id:
            return {"success": False, "status": "dispatch_failed", "dispatch": dispatch}

        deadline = time.monotonic() + timeout_s
        last_history: dict[str, Any] = {}
        while time.monotonic() < deadline:
            history = await memory_ref_scan_result_history(limit=20)
            last_history = history
            rows = (history.get("data") or {}).get("rows") or []
            match = next(
                (row for row in rows if isinstance(row, dict) and row.get("task_id") == task_id),
                None,
            )
            if match:
                return {
                    "success": True,
                    "status": "completed",
                    "task_id": task_id,
                    "dispatch": dispatch,
                    "result_row": match,
                }
            await asyncio.sleep(0.25)

        return {
            "success": False,
            "status": "timeout",
            "task_id": task_id,
            "dispatch": dispatch,
            "last_history": last_history,
        }
    finally:
        await nanobot.stop()
        await scheduler.stop()
        if old_index_path is None:
            os.environ.pop("PARROT_MEMORY_IDENTITY_REF_INDEX_PATH", None)
        else:
            os.environ["PARROT_MEMORY_IDENTITY_REF_INDEX_PATH"] = old_index_path
        temp_dir.cleanup()
        await close_redis()


def _seed_identity_ref_index(
    *,
    smoke_file: Path,
    include_remote_placeholders: bool,
) -> None:
    index = MemoryIdentityRefIndex()
    index.upsert(
        {
            "canonical_uuid": "canon-ref-scan-smoke-local",
            "l2b_uuid": "l2b-ref-scan-smoke-local",
            "obsidian_uuid": "obsidian-ref-scan-smoke-local",
            "ref_id": "ref-scan-smoke-local",
            "ref_kind": "obsidian_doc",
            "locator": str(smoke_file),
            "managed_by": "git",
        }
    )
    if include_remote_placeholders:
        index.upsert(
            {
                "canonical_uuid": "canon-ref-scan-smoke-url",
                "ref_id": "ref-scan-smoke-url",
                "ref_kind": "url",
                "url": "https://example.com/ref-scan-smoke",
                "managed_by": "external",
            }
        )
        index.upsert(
            {
                "canonical_uuid": "canon-ref-scan-smoke-ecs",
                "ref_id": "ref-scan-smoke-ecs",
                "ref_kind": "ecs_path",
                "locator": "ecs://castle/root/ref-scan-smoke.txt",
                "managed_by": "nanobot",
            }
        )
        index.upsert(
            {
                "canonical_uuid": "canon-ref-scan-smoke-graphiti",
                "graphiti_entity_uuid": "graphiti-ref-scan-smoke",
                "ref_id": "ref-scan-smoke-graphiti",
                "ref_kind": "graphiti_entity",
                "locator": "graphiti://smoke/entity/graphiti-ref-scan-smoke",
                "managed_by": "graphiti",
            }
        )
    index.save()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=12.0)
    parser.add_argument(
        "--no-remote-placeholders",
        action="store_true",
        help="Only include the temporary local file ref.",
    )
    parser.add_argument(
        "--remote-checks",
        action="store_true",
        help="Request optional URL/Graphiti probes; ECS local stat still requires worker-side confirmation.",
    )
    args = parser.parse_args()
    result = asyncio.run(
        run_smoke(
            timeout_s=args.timeout,
            include_remote_placeholders=not args.no_remote_placeholders,
            remote_checks=args.remote_checks,
        )
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if result.get("success"):
        return 0
    if result.get("status") == "skipped":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
