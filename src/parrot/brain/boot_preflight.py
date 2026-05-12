"""Brain boot pre-flight audit (Phase 5.1).

Plan reference: §Phase 5.1 of
``app_v1_brain_cold_start_line_lifecycle_audit_20260511.md``.

Runs synchronous and async checks before the heavy Brain listeners
mount so an obvious deploy-time failure (Redis unreachable, photo
upload port already bound, runtime config corrupt) is logged loudly
instead of silently degrading the room session.

The checks here are deliberately read-only and never raise. The
return value is a structured audit list that the orchestrator
``GET /status`` endpoint and the canvas voice tile both consume.
"""

from __future__ import annotations

import asyncio
import logging
import os
import socket
import time
from dataclasses import asdict, dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PreflightCheck:
    name: str
    status: str  # "ok" | "warning" | "error"
    summary: str
    detail: dict[str, Any]


@dataclass
class PreflightReport:
    started_at: float
    duration_ms: float
    checks: list[PreflightCheck]
    overall: str

    def as_json(self) -> dict[str, Any]:
        return {
            "started_at": self.started_at,
            "duration_ms": self.duration_ms,
            "overall": self.overall,
            "checks": [asdict(c) for c in self.checks],
        }


async def run_preflight() -> PreflightReport:
    """Run all checks and return a single report.

    Always returns; never raises into the caller.
    """
    started = time.time()
    checks: list[PreflightCheck] = []

    checks.append(_check_runtime_config())
    checks.append(await _check_redis())
    checks.append(_check_photo_upload_port())

    overall = "ok"
    if any(c.status == "error" for c in checks):
        overall = "error"
    elif any(c.status == "warning" for c in checks):
        overall = "warning"

    duration_ms = (time.time() - started) * 1000.0
    report = PreflightReport(
        started_at=started,
        duration_ms=duration_ms,
        checks=checks,
        overall=overall,
    )
    _publish_to_bb(report)
    return report


def _check_runtime_config() -> PreflightCheck:
    try:
        from parrot.castle.runtime_config import resolve_runtime_config

        resolved = resolve_runtime_config()
    except Exception as exc:  # noqa: BLE001
        return PreflightCheck(
            name="runtime_config",
            status="error",
            summary=f"runtime_config resolve failed: {exc!r}",
            detail={"error": repr(exc)},
        )
    return PreflightCheck(
        name="runtime_config",
        status="ok",
        summary=(
            f"line_id={resolved.line_id} ({resolved.source['line_id']}); "
            f"file_present={resolved.file_present}"
        ),
        detail=resolved.as_json(),
    )


async def _check_redis() -> PreflightCheck:
    try:
        from parrot.shared.redis_client import get_redis

        redis = await get_redis()
        await asyncio.wait_for(redis.ping(), timeout=2.0)
    except asyncio.TimeoutError:
        return PreflightCheck(
            name="redis",
            status="error",
            summary="Redis ping timed out (>2s)",
            detail={"timeout_s": 2.0},
        )
    except Exception as exc:  # noqa: BLE001
        return PreflightCheck(
            name="redis",
            status="error",
            summary=f"Redis unreachable: {exc!r}",
            detail={"error": repr(exc)},
        )
    return PreflightCheck(
        name="redis",
        status="ok",
        summary="Redis ping OK",
        detail={},
    )


def _check_photo_upload_port() -> PreflightCheck:
    """Mirror Bug M's pre-check at boot so an early bind conflict surfaces.

    Skipped entirely when ``PARROT_DISABLE_PHOTO_UPLOAD=1`` (matching
    ``brain.agent`` gating).
    """
    if os.getenv("PARROT_DISABLE_PHOTO_UPLOAD", "0").lower() in {"1", "true", "yes"}:
        return PreflightCheck(
            name="photo_upload_port",
            status="ok",
            summary="photo upload server is disabled by env",
            detail={"env": "PARROT_DISABLE_PHOTO_UPLOAD"},
        )
    host = os.getenv("PARROT_PHOTO_UPLOAD_HOST", "127.0.0.1")
    try:
        port = int(os.getenv("PARROT_PHOTO_UPLOAD_PORT", "7889"))
    except ValueError:
        port = 7889
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((host, port))
    except OSError as exc:
        return PreflightCheck(
            name="photo_upload_port",
            status="warning",
            summary=(
                f"port {host}:{port} is already in use (errno={exc.errno}); "
                "photo upload server start will be skipped"
            ),
            detail={"host": host, "port": port, "errno": exc.errno},
        )
    finally:
        sock.close()
    return PreflightCheck(
        name="photo_upload_port",
        status="ok",
        summary=f"port {host}:{port} is bindable",
        detail={"host": host, "port": port},
    )


def _publish_to_bb(report: PreflightReport) -> None:
    """Surface the preflight to BB so orchestrator /status can include it."""
    try:
        from parrot.scheduler.blackboard import open_bb_client

        bb = open_bb_client(name="brain.boot_preflight", writer="brain.agent")
        bb.set("global/brain_boot_preflight", report.as_json())
    except Exception:
        logger.warning("[boot_preflight] BB write failed", exc_info=True)


__all__ = [
    "PreflightCheck",
    "PreflightReport",
    "run_preflight",
]
