"""Aggregate ECS status for the orchestrator ``GET /status`` endpoint.

This module deliberately avoids depending on ``systemctl`` / ``docker
compose`` so it stays unit-testable on a developer laptop. The
``processes`` block reads Redis ``parrot.heartbeat`` (every Bus-mounted
module writes a heartbeat every 30 s; see
``parrot.bus.heartbeat.HeartbeatSender``) and joins it with ``parrot.modules``.
The ``containers`` block calls ``docker compose ps`` only when invoked
through ``shell_status``; the unit test path patches that helper.

Output schema (stable; clients should treat new fields as additive)::

    {
      "schema_version": 1,
      "now": <unix_seconds>,
      "host": "<ECS hostname>",
      "runtime_config": <runtime_config.RuntimeConfig.as_json>,
      "brain_runtime_snapshot": <BB global/brain_runtime_snapshot or {}>,
      "selection_drift": {
        "is_drift": bool,
        "selected_line_id": str,
        "running_line_id": str,
        "summary": str
      },
      "processes": [
        { "module_id", "online", "last_heartbeat_at", "stale_seconds",
          "module_type", "layers", "registered_at" },
        ...
      ],
      "containers": <list[dict] or {"unavailable": "<reason>"}>,
      "warnings": [str, ...]
    }
"""

from __future__ import annotations

import asyncio
import json
import logging
import socket
import subprocess
import time
from typing import Any

logger = logging.getLogger(__name__)


HEARTBEAT_STALE_S = 90.0


async def gather_status() -> dict[str, Any]:
    """Build a full status snapshot. Always returns; never raises."""
    warnings: list[str] = []
    runtime_config = _runtime_config_payload(warnings)
    brain_snap = _brain_runtime_snapshot(warnings)
    drift = _selection_drift(runtime_config, brain_snap)
    processes = await _processes(warnings)
    containers = await asyncio.to_thread(_containers, warnings)
    crash = _bb_dict("global/brain_last_crash", warnings)
    preflight = _bb_dict("global/brain_boot_preflight", warnings)
    restart_history = _restart_stats_safe(warnings)
    return {
        "schema_version": 1,
        "now": time.time(),
        "host": socket.gethostname(),
        "runtime_config": runtime_config,
        "brain_runtime_snapshot": brain_snap,
        "brain_boot_preflight": preflight,
        "brain_last_crash": crash,
        "selection_drift": drift,
        "processes": processes,
        "containers": containers,
        "restart_stats": restart_history,
        "warnings": warnings,
    }


def _bb_dict(key: str, warnings: list[str]) -> dict[str, Any]:
    try:
        from parrot.scheduler.blackboard import open_bb_client

        bb = open_bb_client(name="castle.orchestrator.status", writer=None)
        value = bb.get(key)
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"BB read {key} failed: {exc!r}")
        return {}
    return value if isinstance(value, dict) else {}


def _restart_stats_safe(warnings: list[str]) -> dict[str, Any]:
    try:
        from parrot.castle.orchestrator.actions import restart_stats

        return restart_stats()
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"restart_stats read failed: {exc!r}")
        return {}


def _runtime_config_payload(warnings: list[str]) -> dict[str, Any]:
    try:
        from parrot.castle.runtime_config import resolve_runtime_config

        return resolve_runtime_config().as_json()
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"runtime_config.resolve failed: {exc!r}")
        return {}


def _brain_runtime_snapshot(warnings: list[str]) -> dict[str, Any]:
    """Read ``global/brain_runtime_snapshot`` BB. Empty dict on miss."""
    try:
        from parrot.scheduler.blackboard import open_bb_client

        bb = open_bb_client(name="castle.orchestrator.status", writer=None)
        value = bb.get("global/brain_runtime_snapshot")
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"brain_runtime_snapshot read failed: {exc!r}")
        return {}
    if isinstance(value, dict):
        return value
    return {}


def _selection_drift(
    runtime_config: dict[str, Any],
    brain_snap: dict[str, Any],
) -> dict[str, Any]:
    """Compare what the file/env *would* serve vs what Brain actually serves.

    ``runtime_config.line_id`` is "what the next ``brain_entrypoint``
    will see" (file > BB > env > default). ``brain_snap.line_id`` is
    "what the currently running ``brain_entrypoint`` resolved at room
    join". When they differ, an operator wrote the file (or BB)
    *after* Brain joined the room — a Tier 1 reconnect would flip the
    live line.
    """
    selected_line = str(runtime_config.get("line_id") or "")
    running_line = str(brain_snap.get("line_id") or "")
    if not selected_line or not running_line:
        return {
            "is_drift": False,
            "selected_line_id": selected_line,
            "running_line_id": running_line,
            "summary": "No live Brain snapshot; drift check skipped.",
        }
    if selected_line == running_line:
        return {
            "is_drift": False,
            "selected_line_id": selected_line,
            "running_line_id": running_line,
            "summary": "Selected and running lines agree.",
        }
    return {
        "is_drift": True,
        "selected_line_id": selected_line,
        "running_line_id": running_line,
        "summary": (
            f"Selected line ({selected_line}) differs from running "
            f"Brain ({running_line}). A Tier 1 reconnect "
            f"(forceUnityReconnect or restart_component brain) would "
            f"apply the new selection."
        ),
    }


async def _processes(warnings: list[str]) -> list[dict[str, Any]]:
    """Combine ``parrot.modules`` + ``parrot.heartbeat`` Redis hashes."""
    try:
        from parrot.shared.constants import HASH_HEARTBEAT, HASH_MODULES
        from parrot.shared.redis_client import get_redis
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"redis_client unavailable: {exc!r}")
        return []
    try:
        redis = await get_redis()
        modules_raw = await redis.hgetall(HASH_MODULES) or {}
        heartbeat_raw = await redis.hgetall(HASH_HEARTBEAT) or {}
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"Redis read failed: {exc!r}")
        return []

    now = time.time()
    seen_ids: set[str] = set()
    out: list[dict[str, Any]] = []

    def _decode_key(key: Any) -> str:
        return key.decode() if isinstance(key, bytes) else str(key)

    def _decode_val(val: Any) -> str:
        return val.decode() if isinstance(val, bytes) else str(val)

    for raw_id, payload in modules_raw.items():
        module_id = _decode_key(raw_id)
        seen_ids.add(module_id)
        try:
            data = json.loads(_decode_val(payload))
        except Exception:
            data = {}
        last_beat = heartbeat_raw.get(raw_id)
        last_beat_f: float | None = None
        if last_beat is not None:
            try:
                last_beat_f = float(_decode_val(last_beat))
            except Exception:
                last_beat_f = None
        stale = (now - last_beat_f) if last_beat_f is not None else None
        out.append(
            {
                "module_id": module_id,
                "online": stale is not None and stale < HEARTBEAT_STALE_S,
                "last_heartbeat_at": last_beat_f,
                "stale_seconds": stale,
                "module_type": data.get("module_type", ""),
                "layers": data.get("layers", []),
                "registered_at": data.get("registered_at"),
            }
        )

    # Modules with a heartbeat but no manifest — surface them so
    # operators can spot a stale supervisor that forgot to deregister.
    for raw_id, last_beat in heartbeat_raw.items():
        module_id = _decode_key(raw_id)
        if module_id in seen_ids:
            continue
        try:
            last_beat_f = float(_decode_val(last_beat))
        except Exception:
            last_beat_f = None
        stale = (now - last_beat_f) if last_beat_f is not None else None
        out.append(
            {
                "module_id": module_id,
                "online": stale is not None and stale < HEARTBEAT_STALE_S,
                "last_heartbeat_at": last_beat_f,
                "stale_seconds": stale,
                "module_type": "",
                "layers": [],
                "registered_at": None,
                "warning": "heartbeat without manifest",
            }
        )

    out.sort(key=lambda item: item["module_id"])
    return out


def _containers(warnings: list[str]) -> Any:
    """Run ``docker compose ps --format json`` if available.

    Returns ``{"unavailable": "<reason>"}`` when docker isn't on PATH
    or the command fails. Status callers should treat that as a soft
    miss and continue rather than 500 the whole status read.
    """
    try:
        result = subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                "infra/docker-compose.yml",
                "ps",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except FileNotFoundError:
        warnings.append("docker not on PATH; container status unavailable")
        return {"unavailable": "docker_not_found"}
    except subprocess.TimeoutExpired:
        warnings.append("docker compose ps timeout (5s)")
        return {"unavailable": "docker_timeout"}
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"docker compose ps failed: {exc!r}")
        return {"unavailable": f"docker_error:{type(exc).__name__}"}

    if result.returncode != 0:
        warnings.append(f"docker compose ps rc={result.returncode}")
        return {"unavailable": f"docker_rc_{result.returncode}"}

    raw = (result.stdout or "").strip()
    if not raw:
        return []
    # Docker emits one JSON object per line in newer versions.
    out: list[dict[str, Any]] = []
    if raw.lstrip().startswith("["):
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return data
        except Exception:
            pass
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


__all__ = [
    "HEARTBEAT_STALE_S",
    "gather_status",
]
