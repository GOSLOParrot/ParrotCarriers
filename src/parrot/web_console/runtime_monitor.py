"""Read-only Web Console runtime monitor aggregation.

This module is deliberately Web-only. It composes existing runtime surfaces
without promoting Scheduler internals, py-trees blackboard keys, or Nanobot
worker details into App DTOs or shared core contracts.
"""

from __future__ import annotations

import dataclasses
import time
from collections import Counter
from enum import Enum
from pathlib import Path
from typing import Any

import py_trees

from parrot.brain.app_first_version import AppFirstVersionFacade
from parrot.brain.plan import get_plan_registry
from parrot.scheduler.blackboard import open_bb_client
from parrot.scheduler.nodes import (
    BB_NS as SCHEDULER_BB_NS,
    GENERAL_NANOBOT_TASK_TYPES,
    GOOGLE_WORKSPACE_TASK_TYPES,
    NANOBOT_TASK_TYPES,
)
from parrot.shared.bb_schema import BB_KEYS
from parrot.shared.constants import (
    CH_NANOBOT_RESULTS,
    CH_SCHEDULER_COMMANDS,
    CH_SCHEDULER_RESULTS,
    CH_SCHEDULER_TO_BRAIN,
    CH_TRIGGER_RESULTS,
    STREAM_NANOBOT_DISPATCH,
)


def build_runtime_monitor_snapshot() -> dict[str, Any]:
    """Return a bounded read-only snapshot for Web runtime monitoring."""
    generated_at = time.time()
    modules = _app_module_statuses()
    scheduler = _scheduler_snapshot()
    plans = _plans_snapshot()
    nanobot = _nanobot_snapshot(modules)
    blackboard = _blackboard_summary()
    agent_team = _agent_team_snapshot(nanobot)
    collaboration = _collaboration_snapshot(
        scheduler=scheduler,
        nanobot=nanobot,
        plans=plans,
    )
    return {
        "generated_at": generated_at,
        "scheduler": scheduler,
        "nanobot": nanobot,
        "plans": plans,
        "blackboard": blackboard,
        "agent_team": agent_team,
        "collaboration": collaboration,
        "audit": {
            "read_only": True,
            "web_only": True,
            "scheduler_boundary": (
                "py-trees routing internals are observed here, not promoted "
                "to App DTOs or shared core contracts"
            ),
            "nanobot_boundary": (
                "Nanobot is observed as a background worker/task bridge; "
                "operator send/admin actions need separate draft receipts"
            ),
        },
    }


def _app_module_statuses() -> list[dict[str, Any]]:
    try:
        return [status.as_json() for status in AppFirstVersionFacade().list_module_statuses()]
    except Exception as exc:
        return [
            {
                "module_id": "app_facade",
                "state": "error",
                "health": "warn",
                "summary": f"{type(exc).__name__}: {exc}",
                "metrics": {},
                "refs": {},
            }
        ]


def _scheduler_snapshot() -> dict[str, Any]:
    active_tasks = _read_scheduler_active_tasks()
    return {
        "router": {
            "name": "py-trees Scheduler Router",
            "route_order": [
                "HandleReflex",
                "HandleIntent",
                "DispatchToNanobot",
                "HandleBrainDirect",
            ],
            "destinations": [
                "reflex_direct",
                "intent_committed",
                "nanobot",
                "brain_direct",
            ],
        },
        "channels": {
            "commands": CH_SCHEDULER_COMMANDS,
            "results": CH_SCHEDULER_RESULTS,
            "nanobot_results": CH_NANOBOT_RESULTS,
            "scheduler_to_brain": CH_SCHEDULER_TO_BRAIN,
            "trigger_results": CH_TRIGGER_RESULTS,
            "nanobot_dispatch_stream": STREAM_NANOBOT_DISPATCH,
        },
        "nanobot_task_types": {
            "general": sorted(GENERAL_NANOBOT_TASK_TYPES),
            "google_workspace": sorted(GOOGLE_WORKSPACE_TASK_TYPES),
            "all": sorted(NANOBOT_TASK_TYPES),
        },
        "active_task_count": len(active_tasks),
        "active_tasks": active_tasks,
        "visibility": (
            "active_tasks are visible only for the current py-trees process "
            "unless RedisBlackboardSync starts mirroring scheduler state"
        ),
    }


def _read_scheduler_active_tasks() -> list[dict[str, Any]]:
    client = py_trees.blackboard.Client(
        name="WebConsoleRuntimeMonitor",
        namespace=SCHEDULER_BB_NS,
    )
    client.register_key(key="active_tasks", access=py_trees.common.Access.READ)
    try:
        active = client.active_tasks
    except Exception:
        return []
    if not isinstance(active, dict):
        return []
    rows: list[dict[str, Any]] = []
    for task_id, payload in active.items():
        row = dict(payload) if isinstance(payload, dict) else {"value": payload}
        row["task_id"] = str(task_id)
        rows.append(_jsonable(row))
    return rows


def _nanobot_snapshot(modules: list[dict[str, Any]]) -> dict[str, Any]:
    status = next((row for row in modules if row.get("module_id") == "nanobot"), None)
    status = status or {
        "module_id": "nanobot",
        "state": "unknown",
        "health": "warn",
        "summary": "Nanobot module status not available",
        "metrics": {},
        "refs": {},
    }
    metrics = status.get("metrics") if isinstance(status.get("metrics"), dict) else {}
    refs = status.get("refs") if isinstance(status.get("refs"), dict) else {}
    return {
        "status": status,
        "busy": bool(metrics.get("busy", False)),
        "report_count": int(metrics.get("report_count") or 0),
        "last_active_at": metrics.get("last_active_at") or 0.0,
        "report_ref_ids": list(refs.get("report_ref_ids") or []),
        "dispatch_stream": STREAM_NANOBOT_DISPATCH,
        "result_channel": CH_NANOBOT_RESULTS,
        "worker_role": "background_task_agent",
    }


def _plans_snapshot() -> dict[str, Any]:
    try:
        registry = get_plan_registry()
        active = [_plan_row(plan) for plan in registry.list_active()]
        archived_values = getattr(registry, "_archive", {})  # Web-only best-effort read.
        archived = [
            _plan_row(plan) for plan in archived_values.values() if hasattr(plan, "plan_id")
        ]
        current = registry.get_current_plan()
    except Exception as exc:
        return {
            "active_count": 0,
            "archived_count": 0,
            "current_plan": None,
            "plans": [],
            "state_counts": {},
            "error": f"{type(exc).__name__}: {exc}",
        }
    rows = [*active, *archived]
    state_counts = Counter(row["state"] for row in rows if row.get("state"))
    return {
        "active_count": len(active),
        "archived_count": len(archived),
        "current_plan": _plan_row(current) if current is not None else None,
        "plans": rows[:24],
        "state_counts": dict(sorted(state_counts.items())),
    }


def _plan_row(plan: Any) -> dict[str, Any]:
    steps = list(getattr(plan, "steps", []) or [])
    step_states = Counter(_enum_value(getattr(step, "state", "")) for step in steps)
    step_rows = [_plan_step_row(step) for step in steps[:8]]
    return {
        "plan_id": str(getattr(plan, "plan_id", "")),
        "title": str(getattr(plan, "title", "")),
        "state": _enum_value(getattr(plan, "state", "")),
        "intent_event_id": str(getattr(plan, "intent_event_id", "")),
        "episode_id": str(getattr(plan, "episode_id", "")),
        "related_node_uuids": list(getattr(plan, "related_node_uuids", ()) or ()),
        "related_staged_ref_ids": list(getattr(plan, "related_staged_ref_ids", ()) or ()),
        "staged_ref_id": str(getattr(plan, "staged_ref_id", "")),
        "blackboard_namespace": str(getattr(plan, "blackboard_namespace", "")),
        "blocks_conversation": bool(getattr(plan, "blocks_conversation", False)),
        "drafted_at": float(getattr(plan, "drafted_at", 0.0) or 0.0),
        "approved_at": float(getattr(plan, "approved_at", 0.0) or 0.0),
        "started_executing_at": float(getattr(plan, "started_executing_at", 0.0) or 0.0),
        "completed_at": float(getattr(plan, "completed_at", 0.0) or 0.0),
        "supersedes": str(getattr(plan, "supersedes", "")),
        "superseded_by": str(getattr(plan, "superseded_by", "")),
        "step_count": len(steps),
        "step_state_counts": dict(sorted(step_states.items())),
        "steps": step_rows,
        "dag": _plan_dag(step_rows),
    }


def _plan_step_row(step: Any) -> dict[str, Any]:
    return {
        "step_id": str(getattr(step, "step_id", "")),
        "title": str(getattr(step, "title", "")),
        "description": str(getattr(step, "description", "")),
        "expected_tool": str(getattr(step, "expected_tool", "")),
        "state": _enum_value(getattr(step, "state", "")),
        "depends_on": [str(dep) for dep in (getattr(step, "depends_on", ()) or ())],
        "nanobot_task_id": str(getattr(step, "nanobot_task_id", "")),
        "started_at": float(getattr(step, "started_at", 0.0) or 0.0),
        "completed_at": float(getattr(step, "completed_at", 0.0) or 0.0),
        "result_summary": str(getattr(step, "result_summary", "")),
        "result_ref_id": str(getattr(step, "result_ref_id", "")),
        "error": str(getattr(step, "error", "")),
    }


def _plan_dag(step_rows: list[dict[str, Any]]) -> dict[str, Any]:
    step_ids = {row["step_id"] for row in step_rows if row.get("step_id")}
    rows_by_id = {row["step_id"]: row for row in step_rows if row.get("step_id")}
    edges: list[dict[str, str]] = []
    for row in step_rows:
        target = str(row.get("step_id") or "")
        if not target:
            continue
        for dep in row.get("depends_on", []) or []:
            dep_id = str(dep)
            if dep_id and dep_id in step_ids:
                edges.append({
                    "source": dep_id,
                    "target": target,
                    "kind": "depends_on",
                })
    ready_ids, blocked_ids, critical_ids = _plan_step_hints(step_rows, rows_by_id)
    return {
        "nodes": [
            {
                "step_id": row.get("step_id", ""),
                "title": row.get("title", ""),
                "state": row.get("state", ""),
                "expected_tool": row.get("expected_tool", ""),
            }
            for row in step_rows
        ],
        "edges": edges,
        "ready_step_ids": ready_ids,
        "blocked_step_ids": blocked_ids,
        "critical_step_ids": critical_ids,
    }


def _plan_step_hints(
    step_rows: list[dict[str, Any]],
    rows_by_id: dict[str, dict[str, Any]],
) -> tuple[list[str], list[str], list[str]]:
    done_states = {"done", "complete", "completed", "success", "succeeded"}
    bad_states = {"failed", "error", "cancelled", "blocked"}
    running_states = {"running", "executing", "dispatched"}
    ready: list[str] = []
    blocked: list[str] = []
    running: list[str] = []
    failed: list[str] = []

    for row in step_rows:
        step_id = str(row.get("step_id") or "")
        if not step_id:
            continue
        state = str(row.get("state") or "")
        if state in done_states:
            continue
        if state in bad_states:
            failed.append(step_id)
            continue
        if state in running_states:
            running.append(step_id)
        deps = [str(dep) for dep in row.get("depends_on", []) or []]
        missing = [
            dep for dep in deps
            if dep in rows_by_id and str(rows_by_id[dep].get("state") or "") not in done_states
        ]
        if missing:
            blocked.append(step_id)
        else:
            ready.append(step_id)

    seed = failed[:1] or running[:1] or ready[:1] or blocked[:1]
    critical = _plan_ancestor_ids(seed, rows_by_id)
    return sorted(set(ready)), sorted(set(blocked)), critical


def _plan_ancestor_ids(
    seed_ids: list[str],
    rows_by_id: dict[str, dict[str, Any]],
) -> list[str]:
    visited: set[str] = set()
    ordered: list[str] = []

    def visit(step_id: str) -> None:
        if not step_id or step_id in visited:
            return
        visited.add(step_id)
        row = rows_by_id.get(step_id)
        if row:
            for dep in row.get("depends_on", []) or []:
                visit(str(dep))
        ordered.append(step_id)

    for seed_id in seed_ids:
        visit(seed_id)
    return ordered


def _blackboard_summary() -> dict[str, Any]:
    client = open_bb_client(name="web_console.runtime_monitor", writer=None)
    scope_counts: Counter[str] = Counter()
    present_by_scope: Counter[str] = Counter()
    present_keys: list[dict[str, Any]] = []
    for key in BB_KEYS:
        scope = key.scope.value
        scope_counts[scope] += 1
        try:
            value = client.get(key.name)
        except Exception:
            value = None
        if value is None:
            continue
        present_by_scope[scope] += 1
        present_keys.append(
            {
                "key": key.name,
                "scope": scope,
                "writer": key.writer,
                "summary": _summary(value),
            }
        )
    return {
        "declared_count": len(BB_KEYS),
        "present_count": len(present_keys),
        "declared_by_scope": dict(sorted(scope_counts.items())),
        "present_by_scope": dict(sorted(present_by_scope.items())),
        "present_keys": present_keys[:32],
    }


def _agent_team_snapshot(nanobot: dict[str, Any]) -> dict[str, Any]:
    nanobot_state = nanobot.get("status", {}).get("state", "unknown")
    return {
        "agent_team_id": "catmaid-team-v1",
        "display_name": "CatMaid Team",
        "status": "active" if nanobot_state not in {"error", "unknown"} else "placeholder",
        "members": [
            {
                "role": "maid",
                "worker": "nanobot",
                "state": nanobot_state,
            }
        ],
        "core_candidates": ["CORE-001", "CORE-002", "CORE-003", "CORE-004"],
    }


def _collaboration_snapshot(
    *,
    scheduler: dict[str, Any],
    nanobot: dict[str, Any],
    plans: dict[str, Any],
) -> dict[str, Any]:
    active_tasks = int(scheduler.get("active_task_count") or 0)
    reports = int(nanobot.get("report_count") or 0)
    active_plans = int(plans.get("active_count") or 0)
    nanobot_state = str(nanobot.get("status", {}).get("state") or "unknown")
    return {
        "goslo_to_nanobot": {
            "dispatch_entry": CH_SCHEDULER_COMMANDS,
            "dispatch_stream": STREAM_NANOBOT_DISPATCH,
            "result_channel": CH_NANOBOT_RESULTS,
            "brain_return_channel": CH_SCHEDULER_TO_BRAIN,
        },
        "channel_flow": [
            {
                "stage": "scheduler_commands",
                "label": "Scheduler Commands",
                "channel": CH_SCHEDULER_COMMANDS,
                "status": "busy" if active_tasks else "idle",
                "detail": f"{active_tasks} active task(s)",
            },
            {
                "stage": "nanobot_dispatch",
                "label": "Nanobot Dispatch",
                "channel": STREAM_NANOBOT_DISPATCH,
                "status": "busy" if active_tasks or active_plans else "idle",
                "detail": f"{active_plans} active plan(s)",
            },
            {
                "stage": "nanobot_worker",
                "label": "Nanobot Worker",
                "channel": "nanobot-worker",
                "status": nanobot_state,
                "detail": str(nanobot.get("status", {}).get("summary") or nanobot_state),
            },
            {
                "stage": "nanobot_results",
                "label": "Nanobot Results",
                "channel": CH_NANOBOT_RESULTS,
                "status": "ready" if reports else "idle",
                "detail": f"{reports} report(s)",
            },
            {
                "stage": "brain_return",
                "label": "Brain Return",
                "channel": CH_SCHEDULER_TO_BRAIN,
                "status": "ready" if reports or active_tasks else "idle",
                "detail": "summary/result refs only",
            },
        ],
        "task_summary": {
            "active_scheduler_tasks": active_tasks,
            "nanobot_reports": reports,
            "active_plans": active_plans,
        },
        "chatroom": {
            "status": "planned",
            "safe_surface": "summaries/status/receipts first; raw channel admin later",
        },
    }


def _enum_value(value: Any) -> str:
    return value.value if isinstance(value, Enum) else str(value)


def _summary(value: Any) -> str:
    value = _jsonable(value)
    if isinstance(value, dict):
        keys = ", ".join(list(value.keys())[:4])
        return f"dict[{keys}]"
    if isinstance(value, list):
        return f"list[{len(value)}]"
    return str(value)


def _jsonable(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Enum):
        return value.value
    if dataclasses.is_dataclass(value):
        return _jsonable(dataclasses.asdict(value))
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_jsonable(v) for v in value]
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


__all__ = ["build_runtime_monitor_snapshot"]
