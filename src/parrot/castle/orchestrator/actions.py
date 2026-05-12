"""Orchestrator action handlers — Tier-routed setting changes.

Plan reference: §Phase 2 of
``app_v1_brain_cold_start_line_lifecycle_audit_20260511.md`` and
the Tier matrix in §3 of the same plan.

Action surface:

* :func:`set_active_line` — Tier 1: writes ``data/runtime_config.json``
  with ``line_id`` (+ optional ``line_profile_id``). Does not touch
  the running Brain process. Caller can opt to ``force_reconnect=True``
  which fires the :func:`force_unity_reconnect` helper.
* :func:`apply_room_profile_id` — Tier 1: writes ``room_profile_id``
  to runtime_config.
* :func:`force_unity_reconnect` — Tier 1: triggers Brain to drop the
  current LiveKit room job. Real implementation in this MVP **does
  not** call into Brain over RPC (no LiveKit room is open from this
  side); instead it writes a "reconnect requested" marker to BB
  ``orchestrator/reconnect_request`` so any future Brain-side polling
  loop or forwarding bridge can pick it up. Phase 3 promotes this to
  a proper inter-service RPC.
* :func:`restart_component` — Tier 2: invokes ``systemctl restart
  parrot-<component>.service`` and waits for the heartbeat to come
  back online.
* :func:`clear_runtime_config` — operator escape hatch.

Every function returns a dict with ``status`` ("ok" / "error") and a
``detail`` payload safe to serialize back to the HTTP layer.
"""

from __future__ import annotations

import asyncio
import logging
import shutil
import subprocess
import threading
import time
from collections import deque
from typing import Any

logger = logging.getLogger(__name__)


KNOWN_COMPONENTS = ("brain", "scheduler", "maid", "goslo-chat", "orchestrator")


# Phase 5.3 — restart rate limiter to avoid thrash.
#
# Rule: at most :data:`_RESTART_BURST` restarts per component within a
# rolling :data:`_RESTART_WINDOW_S` window. Beyond that the
# orchestrator returns a structured "circuit_open" error. The
# operator can clear it explicitly via /clear_runtime_config or by
# waiting out the window.
_RESTART_BURST = 5
_RESTART_WINDOW_S = 300.0
_restart_history: dict[str, deque[float]] = {}
_restart_lock = threading.Lock()


def _record_restart(component: str) -> None:
    now = time.monotonic()
    with _restart_lock:
        history = _restart_history.setdefault(component, deque(maxlen=_RESTART_BURST * 2))
        history.append(now)


def _restart_rate_limited(component: str) -> tuple[bool, dict[str, Any]]:
    """Return ``(blocked, stats)`` for the given component."""
    now = time.monotonic()
    with _restart_lock:
        history = _restart_history.get(component)
        if history is None:
            return False, {"recent_count": 0, "burst": _RESTART_BURST}
        # Drop entries older than the window so the deque represents
        # only the live history.
        while history and (now - history[0]) > _RESTART_WINDOW_S:
            history.popleft()
        recent = len(history)
    blocked = recent >= _RESTART_BURST
    return blocked, {
        "recent_count": recent,
        "burst": _RESTART_BURST,
        "window_s": _RESTART_WINDOW_S,
    }


def restart_stats() -> dict[str, Any]:
    """Snapshot of restart counts per component (for /status)."""
    now = time.monotonic()
    with _restart_lock:
        out: dict[str, Any] = {}
        for component, history in _restart_history.items():
            recent = sum(1 for t in history if (now - t) < _RESTART_WINDOW_S)
            out[component] = {
                "recent_count": recent,
                "burst": _RESTART_BURST,
                "window_s": _RESTART_WINDOW_S,
                "circuit_open": recent >= _RESTART_BURST,
            }
    return out


def reset_restart_history() -> None:
    """Test helper / operator clear."""
    with _restart_lock:
        _restart_history.clear()


def set_active_line(
    *,
    line_id: str,
    line_profile_id: str | None = None,
    updated_by: str = "orchestrator.set_active_line",
    notes: str = "",
) -> dict[str, Any]:
    """Tier 1: persist a line switch for the next room job."""
    from parrot.castle.runtime_config import write_runtime_config

    try:
        resolved = write_runtime_config(
            line_id=line_id,
            line_profile_id=line_profile_id,
            updated_by=updated_by,
            notes=notes or f"set_active_line line_id={line_id}",
        )
    except ValueError as exc:
        return {"status": "error", "reason": "invalid_argument", "detail": str(exc)}
    except Exception as exc:  # noqa: BLE001
        logger.exception("set_active_line write failed")
        return {"status": "error", "reason": "write_failed", "detail": repr(exc)}
    return {
        "status": "ok",
        "tier": 1,
        "runtime_config": resolved.as_json(),
        "next_action": (
            "Call POST /force_unity_reconnect (or restart_component "
            "brain) to make the change live; Tier 1 takes effect on "
            "the next brain_entrypoint."
        ),
    }


def apply_room_profile_id(
    *,
    room_profile_id: str,
    line_id: str | None = None,
    line_profile_id: str | None = None,
    updated_by: str = "orchestrator.apply_room_profile",
) -> dict[str, Any]:
    """Tier 1: persist a RoomProfile selection.

    Optionally also flips ``line_id`` / ``line_profile_id`` in the same
    write so a single transaction can swap the whole triple.
    """
    from parrot.castle.runtime_config import write_runtime_config

    try:
        resolved = write_runtime_config(
            line_id=line_id,
            line_profile_id=line_profile_id,
            room_profile_id=room_profile_id,
            updated_by=updated_by,
            notes=f"apply_room_profile {room_profile_id}",
        )
    except ValueError as exc:
        return {"status": "error", "reason": "invalid_argument", "detail": str(exc)}
    except Exception as exc:  # noqa: BLE001
        logger.exception("apply_room_profile write failed")
        return {"status": "error", "reason": "write_failed", "detail": repr(exc)}
    return {
        "status": "ok",
        "tier": 1,
        "runtime_config": resolved.as_json(),
    }


async def force_unity_reconnect(
    *,
    reason: str = "orchestrator_tier1",
    request_id: str | None = None,
) -> dict[str, Any]:
    """Mark "Brain should drop the room" via BB.

    Phase 2 deliberately uses BB instead of opening a LiveKit RPC
    channel from the orchestrator side: the orchestrator does not
    have a participant identity on the room, and we want to keep its
    own attack surface small. A future Brain-side poller (Phase 3)
    consumes this marker and self-disconnects.

    For Phase 1 deployments the same effect is achieved by Unity
    invoking the ``forceUnityReconnect`` Brain RPC directly. Both
    paths are kept so an operator with only orchestrator access can
    still trigger a reconnect.
    """
    try:
        from parrot.scheduler.blackboard import open_bb_client

        bb = open_bb_client(
            name="castle.orchestrator.action",
            writer="castle.orchestrator",
        )
        marker = {
            "reason": reason,
            "request_id": request_id or "",
            "requested_at": time.time(),
        }
        bb.set("orchestrator/reconnect_request", marker)
    except Exception as exc:  # noqa: BLE001
        logger.exception("force_unity_reconnect BB write failed")
        return {"status": "error", "reason": "bb_write_failed", "detail": repr(exc)}
    return {"status": "ok", "tier": 1, "marker": marker}


def restart_component(
    *,
    component: str,
    reason: str = "orchestrator_restart",
) -> dict[str, Any]:
    """Tier 2: ``systemctl restart parrot-<component>.service``.

    The systemd unit names follow Phase 3.1 of the plan; until those
    units actually land we fall back to a structured error so callers
    don't silently believe a restart happened.

    Returns immediately after issuing the restart; the
    ``GET /status`` endpoint should be polled until the heartbeat
    reappears (callers do this; we don't block here because the
    restart can take 5-15 s for a Brain process).
    """
    if component not in KNOWN_COMPONENTS:
        return {
            "status": "error",
            "reason": "unknown_component",
            "detail": f"{component!r} not in {KNOWN_COMPONENTS}",
        }
    blocked, stats = _restart_rate_limited(component)
    if blocked:
        return {
            "status": "error",
            "reason": "circuit_open",
            "detail": (
                f"{component} has been restarted {stats['recent_count']} times in "
                f"the last {int(stats['window_s'])}s (cap={stats['burst']}); "
                "refusing further restarts to avoid thrash."
            ),
            "restart_stats": stats,
        }
    if shutil.which("systemctl") is None:
        return {
            "status": "error",
            "reason": "systemctl_unavailable",
            "detail": (
                "systemctl is not on PATH. Phase 3.1 systemd units are "
                "not deployed yet, or this orchestrator is running on "
                "a non-Linux host."
            ),
        }

    unit = f"parrot-{component}.service"
    try:
        result = subprocess.run(
            ["systemctl", "restart", unit],
            capture_output=True,
            text=True,
            timeout=20,
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "reason": "systemctl_timeout",
            "detail": f"systemctl restart {unit} timed out (20s)",
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("systemctl restart raised")
        return {"status": "error", "reason": "systemctl_error", "detail": repr(exc)}

    if result.returncode != 0:
        return {
            "status": "error",
            "reason": "systemctl_rc_nonzero",
            "detail": (result.stderr or "").strip(),
            "rc": result.returncode,
        }
    _record_restart(component)
    logger.info(
        "[orchestrator] systemctl restart %s OK (reason=%s)", unit, reason
    )
    return {
        "status": "ok",
        "tier": 2,
        "unit": unit,
        "reason": reason,
        "restart_stats": restart_stats().get(component, {}),
        "next_action": (
            "Poll GET /status until processes[module_id=...].online "
            "becomes true again (typical 5-15s)."
        ),
    }


async def wait_for_heartbeat(
    module_id: str,
    *,
    timeout_s: float = 30.0,
    poll_interval_s: float = 1.0,
) -> dict[str, Any]:
    """Poll heartbeat until it appears or timeout. Helper for callers."""
    deadline = time.monotonic() + timeout_s
    last_seen: float | None = None
    while time.monotonic() < deadline:
        try:
            from parrot.shared.constants import HASH_HEARTBEAT
            from parrot.shared.redis_client import get_redis

            redis = await get_redis()
            raw = await redis.hget(HASH_HEARTBEAT, module_id)
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "error",
                "reason": "heartbeat_read_failed",
                "detail": repr(exc),
            }
        if raw is not None:
            try:
                last_seen = float(raw.decode() if isinstance(raw, bytes) else raw)
            except Exception:
                last_seen = None
            if last_seen is not None and (time.time() - last_seen) < 60.0:
                return {
                    "status": "ok",
                    "module_id": module_id,
                    "last_heartbeat_at": last_seen,
                }
        await asyncio.sleep(poll_interval_s)
    return {
        "status": "error",
        "reason": "heartbeat_timeout",
        "module_id": module_id,
        "timeout_s": timeout_s,
        "last_heartbeat_at": last_seen,
    }


def clear_runtime_config_action() -> dict[str, Any]:
    from parrot.castle.runtime_config import clear_runtime_config

    removed = clear_runtime_config()
    return {"status": "ok", "removed": removed}


async def rolling_restart_brain(
    *,
    reason: str = "rolling_tier1",
    drain_timeout_s: float = 45.0,
) -> dict[str, Any]:
    """Phase 3.4 — minimise voice gap on a Brain restart.

    Strategy (when the Castle has both ``parrot-brain@1`` and
    ``parrot-brain@2`` instantiated):

    1. ``systemctl start parrot-brain@2.service`` (second replica
       comes up; LiveKit dispatch already round-robins agents).
    2. Wait for replica 2 heartbeat to come online.
    3. ``force_unity_reconnect`` — Unity drops, comes back; new
       connection lands on replica 2 (the new env / runtime_config
       takes effect there).
    4. ``systemctl stop parrot-brain@1.service`` — drain old replica.
    5. ``systemctl start parrot-brain@1.service`` (so the pool is
       full again for the next cycle).

    If only the singleton ``parrot-brain.service`` is installed
    (Phase 3.1 baseline), this falls back to a plain restart and
    returns a warning so the operator knows to provision the second
    replica when voice continuity matters.
    """
    if shutil.which("systemctl") is None:
        return {
            "status": "error",
            "reason": "systemctl_unavailable",
            "detail": "rolling_restart_brain requires systemctl",
        }
    has_pool = _systemd_unit_exists("parrot-brain@1.service") and _systemd_unit_exists(
        "parrot-brain@2.service"
    )
    if not has_pool:
        result = restart_component(component="brain", reason=reason)
        result["warning"] = (
            "Rolling restart needs parrot-brain@1.service and parrot-brain@2.service "
            "to be installed; falling back to a simple restart."
        )
        return result

    # Bring up replica 2.
    start_result = _systemctl("start", "parrot-brain@2.service")
    if start_result["status"] == "error":
        return start_result
    online = await wait_for_heartbeat(
        "brain.replica.2", timeout_s=drain_timeout_s
    )
    if online["status"] == "error":
        return {
            "status": "error",
            "reason": "replica2_did_not_come_online",
            "detail": online,
        }

    reconnect = await force_unity_reconnect(reason=reason)
    # Brief drain pause so Unity actually reconnects to replica 2.
    await asyncio.sleep(2.0)

    stop_result = _systemctl("stop", "parrot-brain@1.service")
    restart_pool = _systemctl("start", "parrot-brain@1.service")

    return {
        "status": "ok",
        "tier": 1,
        "reason": reason,
        "steps": {
            "start_replica2": start_result,
            "replica2_online": online,
            "force_reconnect": reconnect,
            "stop_replica1": stop_result,
            "restart_replica1": restart_pool,
        },
    }


def _systemd_unit_exists(unit: str) -> bool:
    try:
        result = subprocess.run(
            ["systemctl", "list-unit-files", unit],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return False
    return result.returncode == 0 and unit in (result.stdout or "")


def _systemctl(verb: str, unit: str) -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["systemctl", verb, unit],
            capture_output=True,
            text=True,
            timeout=20,
        )
    except subprocess.TimeoutExpired:
        return {"status": "error", "reason": "systemctl_timeout", "verb": verb, "unit": unit}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "reason": "systemctl_error", "detail": repr(exc)}
    if result.returncode != 0:
        return {
            "status": "error",
            "reason": "systemctl_rc_nonzero",
            "verb": verb,
            "unit": unit,
            "rc": result.returncode,
            "detail": (result.stderr or "").strip(),
        }
    return {"status": "ok", "verb": verb, "unit": unit}


__all__ = [
    "KNOWN_COMPONENTS",
    "apply_room_profile_id",
    "clear_runtime_config_action",
    "force_unity_reconnect",
    "reset_restart_history",
    "restart_component",
    "restart_stats",
    "rolling_restart_brain",
    "set_active_line",
    "wait_for_heartbeat",
]
