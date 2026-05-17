"""Nanobot task consumer — Path B (L2-only) stub for testing.

This runs inside ParrotCarriers (not inside the nanobot fork).
It mounts as a L2-only worker, reads tasks from Redis Stream,
and echoes back success without actually processing the task.

Roles:
  - Integration tests: proves the dispatch→consume→result chain works
  - Fallback: runs when the real nanobot gateway isn't available

For real task processing, use the nanobot gateway with the parrot_bus channel:
  GOSLOParrot/nanobot → nanobot/channels/parrot_bus.py
  Start with: python src/scripts/start_nanobot_worker.py
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from parrot.bus.manifest import ModuleManifest
from parrot.bus.mounting import ModuleMount
from parrot.shared.constants import CH_NANOBOT_RESULTS, STREAM_NANOBOT_DISPATCH
from parrot.shared.redis_client import get_redis
from parrot.shared.types import Layer, ModuleType

logger = logging.getLogger(__name__)

CONSUMER_GROUP = "nanobot-workers"
CONSUMER_NAME = "worker-0"
HEARTBEAT_KEY = "parrot:nanobot_heartbeat"
HEARTBEAT_FIELD = "main_worker"
HEARTBEAT_BUSY_FIELD = "main_worker_busy"


class NanobotConsumer:
    """L2-only worker that consumes tasks from the dispatch stream."""

    def __init__(self):
        self._manifest = ModuleManifest(
            module_id="nanobot-worker",
            module_type=ModuleType.WORKER,
            layers=[Layer.L2],
        )
        self._mount = ModuleMount(self._manifest)
        self._consumer_task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        logger.info("Nanobot consumer starting...")
        await self._mount.mount()
        await self._ensure_consumer_group()
        self._running = True
        self._consumer_task = asyncio.create_task(self._consume_loop())
        logger.info("Nanobot consumer running.")

    async def stop(self) -> None:
        self._running = False
        if self._consumer_task:
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass
        await self._mount.unmount()

    async def _ensure_consumer_group(self) -> None:
        """Create consumer group if it doesn't exist."""
        r = await get_redis()
        try:
            await r.xgroup_create(STREAM_NANOBOT_DISPATCH, CONSUMER_GROUP, id="0", mkstream=True)
            logger.info("Consumer group '%s' created", CONSUMER_GROUP)
        except Exception:
            logger.debug("Consumer group '%s' already exists", CONSUMER_GROUP)

    async def _consume_loop(self) -> None:
        """Main loop: read from stream, process, ack, publish result."""
        r = await get_redis()
        while self._running:
            try:
                entries = await r.xreadgroup(
                    CONSUMER_GROUP,
                    CONSUMER_NAME,
                    {STREAM_NANOBOT_DISPATCH: ">"},
                    count=1,
                    block=5000,
                )
                if not entries:
                    continue

                for stream_name, messages in entries:
                    for msg_id, fields in messages:
                        await self._handle_task(r, msg_id, fields)

            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Error in consume loop")
                await asyncio.sleep(1)

    async def _handle_task(self, r, msg_id: str, fields: dict) -> None:
        """Process a single task and report the result."""
        raw = fields.get("payload", "{}")
        task = json.loads(raw)
        task_id = task.get("task_id", "unknown")
        task_type = task.get("type", "unknown")
        params = task.get("params", {})

        logger.info("Nanobot processing task: %s (id=%s)", task_type, task_id)
        await r.hset(HEARTBEAT_KEY, mapping={
            HEARTBEAT_FIELD: str(time.time()),
            HEARTBEAT_BUSY_FIELD: "1",
        })

        result = _task_result(task_id=task_id, task_type=task_type, params=params)

        result_channel = params.get("result_channel")
        if result_channel:
            # Keep the normal task type on the Nanobot result. Scheduler owns
            # trigger fan-out and rewrites ``type`` only on CH_TRIGGER_RESULTS.
            result["result_channel"] = result_channel

        await r.xack(STREAM_NANOBOT_DISPATCH, CONSUMER_GROUP, msg_id)
        await r.publish(CH_NANOBOT_RESULTS, json.dumps(result))
        await r.hset(HEARTBEAT_KEY, mapping={
            HEARTBEAT_FIELD: str(time.time()),
            HEARTBEAT_BUSY_FIELD: "0",
        })

        logger.info("Nanobot task completed: %s (id=%s) result_channel=%s",
                     task_type, task_id, result_channel or "(default)")


def _task_result(*, task_id: str, task_type: str, params: dict[str, Any]) -> dict[str, Any]:
    if task_type == "ref_scan":
        return _ref_scan_result(task_id=task_id, task_type=task_type, params=params)
    return {
        "task_id": task_id,
        "type": task_type,
        "status": "completed",
        "result": f"[stub] Task '{task_type}' acknowledged (no real processing)",
        "completed_at": time.time(),
    }


def _ref_scan_result(*, task_id: str, task_type: str, params: dict[str, Any]) -> dict[str, Any]:
    if params.get("allow_mutation") is True:
        body = {
            "scan_id": str(params.get("scan_id") or ""),
            "status": "failed",
            "error": "ref_scan_worker_refuses_mutation",
            "summary": "Ref scan refused because allow_mutation=true.",
            "ref_results": [],
            "manifest_delta": [],
            "warnings": ["mutation_request_rejected"],
        }
        return {
            "task_id": task_id,
            "type": task_type,
            "status": "failed",
            "result": json.dumps(body, ensure_ascii=False),
            "completed_at": time.time(),
        }

    refs = params.get("refs") if isinstance(params.get("refs"), list) else []
    scan_options = _ref_scan_options(params)
    ref_results = [_scan_ref(ref, options=scan_options) for ref in refs if isinstance(ref, dict)]
    manifest_delta = [
        delta
        for result in ref_results
        for delta in _manifest_delta_for_ref(result)
    ]
    warnings = [
        warning
        for result in ref_results
        for warning in result.get("warnings", [])
        if str(warning)
    ]
    body = {
        "scan_id": str(params.get("scan_id") or ""),
        "status": "completed",
        "scan_mode": "read_only",
        "allow_mutation": False,
        "ref_results": ref_results,
        "manifest_delta": manifest_delta,
        "warnings": warnings[:20],
        "summary": f"Scanned {len(ref_results)} ref(s); {len(manifest_delta)} manifest delta(s) proposed.",
        "worker": "parrot_fallback_nanobot_consumer",
        "checker_policy": scan_options["policy"],
    }
    return {
        "task_id": task_id,
        "type": task_type,
        "status": "completed",
        "result": json.dumps(body, ensure_ascii=False),
        "completed_at": time.time(),
    }


def _scan_ref(ref: dict[str, Any], *, options: dict[str, Any]) -> dict[str, Any]:
    locators = _string_list(ref.get("locators"))
    locator_results = [_scan_locator(locator, options=options) for locator in locators]
    health = _overall_ref_health(locator_results)
    result: dict[str, Any] = {
        "ref_id": str(ref.get("ref_id") or ""),
        "canonical_uuid": str(ref.get("canonical_uuid") or ""),
        "kind": str(ref.get("kind") or "external"),
        "health": health,
        "risk_level": str(ref.get("risk_level") or ""),
        "manifest_action": str(ref.get("manifest_action") or "propose_manifest_fingerprint"),
        "locator_results": locator_results,
        "warnings": [
            warning
            for locator_result in locator_results
            for warning in locator_result.get("warnings", [])
            if str(warning)
        ],
    }
    first_ok_file = next(
        (
            row
            for row in locator_results
            if row.get("target_type") in {"local_path", "ecs_path"}
            and row.get("health") == "ok"
            and row.get("content_hash")
        ),
        None,
    )
    if first_ok_file:
        result["resolved_locator"] = first_ok_file.get("locator", "")
        result["content_hash"] = first_ok_file.get("content_hash", "")
        result["size"] = first_ok_file.get("size", 0)
        result["mtime"] = first_ok_file.get("mtime", 0.0)
    return result


def _scan_locator(locator: str, *, options: dict[str, Any]) -> dict[str, Any]:
    text = str(locator or "").strip()
    target_type = _locator_target_type(text)
    if not text:
        return {
            "locator": "",
            "target_type": "blank",
            "health": "missing",
            "reason": "blank_locator",
            "warnings": ["blank_locator"],
        }
    if target_type == "local_path":
        return _scan_local_path(text)
    if target_type == "url":
        if options.get("enable_url_check"):
            return _scan_url(text, options=options)
        return {
            "locator": text,
            "target_type": target_type,
            "health": "unknown",
            "reason": "url_not_checked_by_fallback",
            "warnings": ["url_requires_mcp_or_enabled_network_checker"],
        }
    if target_type == "ecs_path":
        if options.get("enable_ecs_local_check"):
            return _scan_ecs_path(text, options=options)
        return {
            "locator": text,
            "target_type": target_type,
            "health": "unknown",
            "reason": "ecs_path_not_checked_by_fallback",
            "warnings": ["ecs_path_requires_mcp_checker"],
        }
    if target_type == "graphiti_pointer":
        if options.get("enable_graphiti_probe"):
            return _scan_graphiti_pointer(text, options=options)
        return {
            "locator": text,
            "target_type": target_type,
            "health": "unknown",
            "reason": "graphiti_pointer_not_checked_by_fallback",
            "warnings": ["graphiti_pointer_requires_graphiti_checker"],
        }
    return {
        "locator": text,
        "target_type": target_type,
        "health": "unknown",
        "reason": "opaque_locator_not_checked_by_fallback",
        "warnings": ["opaque_locator_requires_mcp_checker"],
    }


def _ref_scan_options(params: dict[str, Any]) -> dict[str, Any]:
    remote_checks = {
        str(item).strip().lower()
        for item in params.get("remote_checks", [])
        if str(item).strip()
    } if isinstance(params.get("remote_checks"), list) else set()
    enable_url_check = (
        _boolish(params.get("enable_url_check"), False)
        or "url" in remote_checks
        or "http_head" in remote_checks
        or _env_bool("PARROT_REF_SCAN_ENABLE_URL_CHECK", False)
    )
    requested_ecs_local_check = (
        _boolish(params.get("enable_ecs_local_check"), False)
        or "ecs" in remote_checks
        or "ecs_path_stat" in remote_checks
        or _env_bool("PARROT_REF_SCAN_ENABLE_ECS_LOCAL_CHECK", False)
    )
    enable_ecs_local_check = requested_ecs_local_check and (
        _boolish(params.get("ecs_local_check_confirmed"), False)
        or _env_bool("PARROT_REF_SCAN_ENABLE_ECS_LOCAL_CHECK", False)
    )
    enable_graphiti_probe = (
        _boolish(params.get("enable_graphiti_probe"), False)
        or "graphiti" in remote_checks
        or "graphiti_uuid_probe" in remote_checks
        or _env_bool("PARROT_REF_SCAN_ENABLE_GRAPHITI_PROBE", False)
    )
    timeout_s = _bounded_float(
        params.get("network_timeout_s"),
        default=_bounded_float(os.getenv("PARROT_REF_SCAN_NETWORK_TIMEOUT_S"), default=3.0),
    )
    ecs_host = str(params.get("ecs_local_host") or os.getenv("PARROT_REF_SCAN_ECS_LOCAL_HOST") or "castle").strip()
    graphiti_base_url = str(
        params.get("graphiti_base_url")
        or os.getenv("PARROT_WEB_CONSOLE_GRAPHITI_URL")
        or os.getenv("PARROT_GRAPHITI_REMOTE_URL")
        or ""
    ).strip().rstrip("/")
    enabled = []
    if enable_url_check:
        enabled.append("url_head")
    if enable_ecs_local_check:
        enabled.append("ecs_local_stat")
    if enable_graphiti_probe:
        enabled.append("graphiti_search_probe")
    return {
        "enable_url_check": enable_url_check,
        "enable_ecs_local_check": enable_ecs_local_check,
        "enable_graphiti_probe": enable_graphiti_probe,
        "network_timeout_s": timeout_s,
        "ecs_local_host": ecs_host,
        "ecs_local_roots": _ecs_local_roots(params.get("ecs_local_roots")),
        "graphiti_base_url": graphiti_base_url,
        "policy": {
            "remote_checks_enabled": enabled,
            "remote_checks_requested": sorted(remote_checks),
            "read_only": True,
            "mutation_allowed": False,
            "url_body_read": False,
            "ecs_write": False,
            "graphiti_write": False,
        },
    }


def _scan_url(locator: str, *, options: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        locator,
        method="HEAD",
        headers={"User-Agent": "ParrotCarriers-ref-scan/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=float(options.get("network_timeout_s") or 3.0)) as response:
            status_code = int(getattr(response, "status", 0) or response.getcode())
            return {
                "locator": locator,
                "target_type": "url",
                "health": "ok" if 200 <= status_code < 400 else "unknown",
                "reason": "url_head_ok" if 200 <= status_code < 400 else "url_head_unexpected_status",
                "status_code": status_code,
                "content_type": response.headers.get("Content-Type", ""),
                "content_length": response.headers.get("Content-Length", ""),
                "warnings": [] if 200 <= status_code < 400 else ["url_head_unexpected_status"],
            }
    except urllib.error.HTTPError as exc:
        status_code = int(exc.code or 0)
        if status_code in {404, 410}:
            health = "missing"
            reason = "url_missing"
            warnings = ["url_missing"]
        elif status_code in {401, 403}:
            health = "unknown"
            reason = "url_auth_required"
            warnings = ["url_auth_required"]
        else:
            health = "unknown"
            reason = "url_head_http_error"
            warnings = ["url_head_http_error"]
        return {
            "locator": locator,
            "target_type": "url",
            "health": health,
            "reason": reason,
            "status_code": status_code,
            "content_type": exc.headers.get("Content-Type", "") if exc.headers else "",
            "content_length": exc.headers.get("Content-Length", "") if exc.headers else "",
            "warnings": warnings,
        }
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {
            "locator": locator,
            "target_type": "url",
            "health": "unknown",
            "reason": f"url_head_failed:{type(exc).__name__}",
            "warnings": ["url_head_failed"],
        }


def _scan_ecs_path(locator: str, *, options: dict[str, Any]) -> dict[str, Any]:
    mapped_path, warning = _ecs_locator_to_local_path(locator, options=options)
    if not mapped_path:
        return {
            "locator": locator,
            "target_type": "ecs_path",
            "health": "unknown",
            "reason": warning or "ecs_path_not_mapped_to_local_host",
            "warnings": [warning or "ecs_path_not_mapped_to_local_host"],
        }
    local_result = _scan_local_path(str(mapped_path))
    result = {
        **local_result,
        "locator": locator,
        "target_type": "ecs_path",
        "local_probe_path": str(mapped_path),
    }
    if result.get("reason") == "local_path_exists":
        result["reason"] = "ecs_local_path_exists"
    elif result.get("reason") == "local_path_missing":
        result["reason"] = "ecs_local_path_missing"
    warnings = [
        "ecs_local_read_only_probe",
        *[str(item) for item in result.get("warnings", []) if str(item)],
    ]
    result["warnings"] = warnings
    return result


def _scan_graphiti_pointer(locator: str, *, options: dict[str, Any]) -> dict[str, Any]:
    parsed = _parse_graphiti_locator(locator)
    graphiti_uuid = parsed.get("uuid", "")
    partition = parsed.get("partition", "")
    base_url = str(options.get("graphiti_base_url") or "").rstrip("/")
    if not graphiti_uuid:
        return {
            "locator": locator,
            "target_type": "graphiti_pointer",
            "health": "unknown",
            "reason": "graphiti_pointer_missing_uuid",
            "warnings": ["graphiti_pointer_missing_uuid"],
        }
    if not base_url:
        return {
            "locator": locator,
            "target_type": "graphiti_pointer",
            "health": "unknown",
            "reason": "graphiti_probe_url_not_configured",
            "graphiti_uuid": graphiti_uuid,
            "partition": partition,
            "warnings": ["graphiti_probe_url_not_configured"],
        }
    payload = json.dumps(
        {"query": graphiti_uuid, "partition": partition, "limit": 10},
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}/api/graphiti/search",
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "ParrotCarriers-ref-scan/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=float(options.get("network_timeout_s") or 3.0)) as response:
            raw = response.read(1024 * 1024)
            data = json.loads(raw.decode("utf-8")) if raw else {}
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {
            "locator": locator,
            "target_type": "graphiti_pointer",
            "health": "unknown",
            "reason": f"graphiti_probe_failed:{type(exc).__name__}",
            "graphiti_uuid": graphiti_uuid,
            "partition": partition,
            "warnings": ["graphiti_probe_failed"],
        }
    if not isinstance(data, dict) or data.get("success") is False:
        error = str(data.get("error") or data.get("message") or "graphiti_probe_unsuccessful") if isinstance(data, dict) else "graphiti_probe_non_object_response"
        return {
            "locator": locator,
            "target_type": "graphiti_pointer",
            "health": "unknown",
            "reason": error,
            "graphiti_uuid": graphiti_uuid,
            "partition": partition,
            "warnings": ["graphiti_probe_unsuccessful"],
        }
    results = data.get("data", {}).get("results", []) if isinstance(data.get("data"), dict) else []
    exact_match = _json_contains_text(results, graphiti_uuid)
    return {
        "locator": locator,
        "target_type": "graphiti_pointer",
        "health": "ok" if exact_match else "unknown",
        "reason": "graphiti_uuid_found_by_search_probe" if exact_match else "graphiti_uuid_not_found_by_search_probe",
        "graphiti_uuid": graphiti_uuid,
        "partition": partition,
        "result_count": len(results) if isinstance(results, list) else 0,
        "warnings": [] if exact_match else ["graphiti_search_probe_is_not_uuid_crud_lookup"],
    }


def _scan_local_path(locator: str) -> dict[str, Any]:
    path = Path(locator).expanduser()
    try:
        exists = path.exists()
    except OSError as exc:
        return {
            "locator": locator,
            "target_type": "local_path",
            "health": "unknown",
            "reason": f"{type(exc).__name__}: {exc}",
            "warnings": ["local_path_stat_failed"],
        }
    if not exists:
        return {
            "locator": locator,
            "target_type": "local_path",
            "health": "missing",
            "reason": "local_path_missing",
            "warnings": ["local_path_missing"],
        }
    try:
        stat = path.stat()
    except OSError as exc:
        return {
            "locator": locator,
            "target_type": "local_path",
            "health": "unknown",
            "reason": f"{type(exc).__name__}: {exc}",
            "warnings": ["local_path_stat_failed"],
        }
    result: dict[str, Any] = {
        "locator": locator,
        "target_type": "local_path",
        "health": "ok",
        "reason": "local_path_exists",
        "size": int(stat.st_size),
        "mtime": float(stat.st_mtime),
        "is_dir": path.is_dir(),
        "warnings": [],
    }
    if path.is_file():
        content_hash, hash_warning = _hash_file(path, size=int(stat.st_size))
        if content_hash:
            result["content_hash"] = content_hash
        if hash_warning:
            result["warnings"].append(hash_warning)
    return result


def _hash_file(path: Path, *, size: int) -> tuple[str, str]:
    max_bytes = _hash_max_bytes()
    if size > max_bytes:
        return "", "local_file_too_large_for_fallback_hash"
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return f"sha256:{digest.hexdigest()}", ""
    except OSError as exc:
        return "", f"local_file_hash_failed:{type(exc).__name__}"


def _hash_max_bytes() -> int:
    try:
        return max(0, int(os.getenv("PARROT_REF_SCAN_HASH_MAX_BYTES", "5242880")))
    except ValueError:
        return 5242880


def _boolish(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value is None or value == "":
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _env_bool(name: str, default: bool) -> bool:
    return _boolish(os.getenv(name), default)


def _bounded_float(value: Any, *, default: float, minimum: float = 0.25, maximum: float = 10.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(parsed, maximum))


def _ecs_local_roots(raw: Any) -> list[Path]:
    if isinstance(raw, (list, tuple, set)):
        values = [str(item) for item in raw]
    else:
        values = str(raw or os.getenv("PARROT_REF_SCAN_ECS_LOCAL_ROOTS") or "/root").split(";")
    roots: list[Path] = []
    for value in values:
        text = str(value or "").strip()
        if not text:
            continue
        try:
            roots.append(Path(text).expanduser().resolve())
        except OSError:
            continue
    return roots or [Path("/root").resolve()]


def _ecs_locator_to_local_path(locator: str, *, options: dict[str, Any]) -> tuple[Path | None, str]:
    text = str(locator or "").strip()
    expected_host = str(options.get("ecs_local_host") or "castle").strip().lower()
    if text.startswith("/root/"):
        candidate = Path(text)
    elif text.lower().startswith("ecs://"):
        parsed = urllib.parse.urlparse(text)
        host = (parsed.netloc or "").lower()
        if expected_host and host and host != expected_host:
            return None, "ecs_locator_host_not_local"
        candidate = Path(urllib.parse.unquote(parsed.path or ""))
    else:
        return None, "ecs_locator_scheme_not_supported_by_local_probe"
    try:
        resolved = candidate.expanduser().resolve()
    except OSError as exc:
        return None, f"ecs_local_path_resolve_failed:{type(exc).__name__}"
    roots = options.get("ecs_local_roots") if isinstance(options.get("ecs_local_roots"), list) else []
    if roots and not any(_path_is_relative_to(resolved, root) for root in roots if isinstance(root, Path)):
        return None, "ecs_local_path_outside_allowed_roots"
    return resolved, ""


def _path_is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _parse_graphiti_locator(locator: str) -> dict[str, str]:
    parsed = urllib.parse.urlparse(str(locator or "").strip())
    parts = [urllib.parse.unquote(part) for part in parsed.path.split("/") if part]
    return {
        "partition": parsed.netloc,
        "kind": parts[0] if parts else "",
        "uuid": parts[-1] if parts else "",
    }


def _json_contains_text(value: Any, needle: str) -> bool:
    if not needle:
        return False
    if isinstance(value, str):
        return value == needle
    if isinstance(value, dict):
        return any(_json_contains_text(item, needle) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_json_contains_text(item, needle) for item in value)
    return False


def _overall_ref_health(locator_results: list[dict[str, Any]]) -> str:
    if not locator_results:
        return "unknown"
    statuses = {str(row.get("health") or "unknown") for row in locator_results}
    if "ok" in statuses:
        return "ok"
    if statuses == {"missing"}:
        return "missing"
    return "unknown"


def _manifest_delta_for_ref(result: dict[str, Any]) -> list[dict[str, Any]]:
    ref_id = str(result.get("ref_id") or "")
    if not ref_id:
        return []
    deltas: list[dict[str, Any]] = []
    health = str(result.get("health") or "unknown")
    if health in {"ok", "missing"}:
        deltas.append({
            "ref_id": ref_id,
            "action": "propose_health_update",
            "health": health,
        })
    if result.get("content_hash"):
        deltas.append({
            "ref_id": ref_id,
            "action": "propose_content_hash_update",
            "content_hash": result.get("content_hash"),
        })
    return deltas


def _locator_target_type(locator: str) -> str:
    lowered = locator.lower()
    if lowered.startswith(("http://", "https://")):
        return "url"
    if lowered.startswith(("ecs://", "ssh://", "sftp://")) or lowered.startswith("/root/") or lowered.startswith("root@"):
        return "ecs_path"
    if lowered.startswith("graphiti://"):
        return "graphiti_pointer"
    if _looks_like_path(locator):
        return "local_path"
    return "opaque_locator"


def _looks_like_path(value: str) -> bool:
    text = str(value or "").strip()
    if not text:
        return False
    if text.startswith(("~", "/", "\\")):
        return True
    if len(text) >= 3 and text[1:3] in {":\\", ":/"}:
        return True
    return "\\" in text or "/" in text


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        values: Any = [value]
    else:
        values = value
    if not isinstance(values, (list, tuple, set)):
        return []
    result: list[str] = []
    seen: set[str] = set()
    for item in values:
        text = str(item or "").strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


async def run_nanobot_consumer() -> None:
    """Entry point for running the Nanobot consumer standalone."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    consumer = NanobotConsumer()
    try:
        await consumer.start()
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(run_nanobot_consumer())
