"""Web-only intake for Collaboration Flow result routes."""

from __future__ import annotations

import json
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any

_SCHEMA_VERSION = 1
_MAX_ENTRIES = 160
_MAX_STRING = 6000
_SECRET_KEY_RE = re.compile(r"(secret|token|password|api[_-]?key|authorization|credential)", re.I)
_SUPPORTED_APPLY_DESTINATIONS = frozenset({"stage_to_intent_workspace"})


def list_workflow_result_intakes(*, q: str = "", limit: int = 50) -> dict[str, Any]:
    """Return bounded Web-only workflow result intake ledger entries."""
    query = str(q or "").strip().lower()
    limit = max(1, min(int(limit or 50), _MAX_ENTRIES))
    entries = sorted(_load_store()["entries"], key=lambda row: str(row.get("updated_at") or ""), reverse=True)
    rows = [
        _summary(row)
        for row in entries
        if _matches(row, query)
    ][:limit]
    return {
        "success": True,
        "action": "runtime.workflow.result_intake.list",
        "entries": rows,
        "count": len(rows),
        "audit": _audit(),
    }


async def intake_workflow_result(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Preview or apply result routes for a workflow result payload.

    This is deliberately a Web operator intake layer. It consumes the existing
    ``workflow_result_contract_v1`` shape but does not promote Scheduler result
    routing to a shared protocol yet.
    """
    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    result_payload = _result_payload(body)
    if result_payload is None:
        return _receipt(
            action="runtime.workflow.result_intake",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={"error": "result_payload_required"},
        )

    contract = await _contract_from_payload(body)
    if not contract:
        return _receipt(
            action="runtime.workflow.result_intake",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "error": "workflow_result_contract_not_found",
                "workflow_id": str(body.get("workflow_id") or ""),
                "workflow_node_id": str(body.get("workflow_node_id") or body.get("step_id") or ""),
            },
        )

    routes = _selected_routes(contract, body)
    if not routes:
        return _receipt(
            action="runtime.workflow.result_intake",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "error": "workflow_result_routes_not_found",
                "workflow_id": str(contract.get("workflow_id") or body.get("workflow_id") or ""),
                "workflow_node_id": str(body.get("workflow_node_id") or body.get("step_id") or ""),
                "contract_schema": str(contract.get("schema") or ""),
            },
        )

    now = _iso_now()
    route_results: list[dict[str, Any]] = []
    staged_refs: list[dict[str, Any]] = []
    for route in routes[:24]:
        route_result = await _apply_route(
            route,
            body=body,
            contract=contract,
            result_payload=result_payload,
            dry_run=dry_run,
            operator_mode=operator_mode,
        )
        route_results.append(route_result)
        if route_result.get("staged_ref"):
            staged_refs.append(route_result["staged_ref"])

    applied_count = sum(1 for row in route_results if row.get("intake_state") == "applied")
    blocked_count = sum(1 for row in route_results if row.get("intake_state") == "blocked")
    preview_count = sum(1 for row in route_results if row.get("intake_state") == "preview")
    entry_state = _entry_state(
        applied_count=applied_count,
        blocked_count=blocked_count,
        preview_count=preview_count,
        dry_run=dry_run,
        operator_mode=operator_mode,
    )

    entry: dict[str, Any] | None = None
    if operator_mode and not dry_run:
        entry = {
            "schema_version": _SCHEMA_VERSION,
            "entry_id": _safe_id(body.get("entry_id")) or f"wri_{uuid.uuid4().hex[:12]}",
            "state": entry_state,
            "workflow_id": str(contract.get("workflow_id") or body.get("workflow_id") or ""),
            "workflow_node_id": str(body.get("workflow_node_id") or body.get("step_id") or ""),
            "plan_id": str(body.get("plan_id") or ""),
            "step_id": str(body.get("step_id") or ""),
            "task_id": str(body.get("task_id") or ""),
            "result_channel": str(body.get("result_channel") or ""),
            "route_count": len(routes),
            "applied_route_count": applied_count,
            "blocked_route_count": blocked_count,
            "staged_ref_count": len(staged_refs),
            "routes": _safe_json(routes),
            "route_results": _safe_json(route_results),
            "result_payload": _safe_json(result_payload),
            "created_at": now,
            "updated_at": now,
            "audit": _audit(),
        }
        _save_entry(entry)

    return _receipt(
        action="runtime.workflow.result_intake",
        success=True,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data={
            "workflow_id": str(contract.get("workflow_id") or body.get("workflow_id") or ""),
            "contract_schema": str(contract.get("schema") or ""),
            "route_count": len(routes),
            "applied_route_count": applied_count,
            "blocked_route_count": blocked_count,
            "preview_route_count": preview_count,
            "route_results": route_results,
            "staged_refs": staged_refs,
            "entry": _summary(entry) if entry else {},
            "recorded": bool(entry),
            "scheduler_enforced": False,
            "autonomous_chaining": False,
        },
    )


async def _contract_from_payload(body: dict[str, Any]) -> dict[str, Any]:
    raw = body.get("result_contract")
    if isinstance(raw, dict):
        return raw

    from parrot.web_console.runtime_flow import draft_workflow_result_contract

    receipt = await draft_workflow_result_contract(body)
    data = receipt.get("data") if isinstance(receipt.get("data"), dict) else {}
    contract = data.get("result_contract") if isinstance(data.get("result_contract"), dict) else {}
    return contract


def _selected_routes(contract: dict[str, Any], body: dict[str, Any]) -> list[dict[str, Any]]:
    raw_routes = body.get("result_routes")
    if isinstance(raw_routes, list):
        return [route for route in raw_routes if isinstance(route, dict)]

    workflow_node_id = str(body.get("workflow_node_id") or body.get("step_id") or "").strip()
    capability_id = str(body.get("capability_id") or "").strip()
    node_routes = contract.get("node_routes") if isinstance(contract.get("node_routes"), list) else []
    routes: list[dict[str, Any]] = []
    for node in node_routes:
        if not isinstance(node, dict):
            continue
        if workflow_node_id and str(node.get("workflow_node_id") or "") != workflow_node_id:
            continue
        if capability_id and str(node.get("capability_id") or "") != capability_id:
            continue
        for route in node.get("result_routes") if isinstance(node.get("result_routes"), list) else []:
            if not isinstance(route, dict):
                continue
            routes.append({
                "workflow_node_id": str(route.get("workflow_node_id") or node.get("workflow_node_id") or ""),
                "capability_id": str(route.get("capability_id") or node.get("capability_id") or ""),
                **route,
            })
    return routes


async def _apply_route(
    route: dict[str, Any],
    *,
    body: dict[str, Any],
    contract: dict[str, Any],
    result_payload: Any,
    dry_run: bool,
    operator_mode: bool,
) -> dict[str, Any]:
    destination = str(route.get("destination") or "")
    base = {
        "destination": destination,
        "workflow_node_id": str(route.get("workflow_node_id") or body.get("workflow_node_id") or ""),
        "capability_id": str(route.get("capability_id") or body.get("capability_id") or ""),
        "sink": str(route.get("sink") or ""),
        "route": str(route.get("route") or ""),
        "route_state": str(route.get("route_state") or ""),
        "mutates_memory": bool(route.get("mutates_memory")),
    }
    if destination == "view_only":
        state = "applied" if operator_mode and not dry_run else "preview"
        return {
            **base,
            "intake_state": state,
            "applied": state == "applied",
            "mutated": False,
            "receipt_visible": True,
            "would_record_receipt": True,
            "policy": "view_only results remain in Web receipt/log surfaces.",
        }
    if destination == "return_to_goslo":
        state = "applied" if operator_mode and not dry_run else "preview"
        return {
            **base,
            "intake_state": state,
            "applied": state == "applied",
            "mutated": False,
            "context_return_draft": True,
            "would_return_context": True,
            "policy": "return_to_goslo is exposed as an operator-readable context draft; C3/C4 injection is not automatic.",
        }
    if destination == "stage_to_intent_workspace":
        if dry_run or not operator_mode:
            return {
                **base,
                "intake_state": "preview",
                "applied": False,
                "would_stage": True,
                "mutated": False,
                "apply_skipped_reason": "dry_run_or_operator_mode_missing",
            }
        staged = await _stage_intent_workspace(
            route,
            body=body,
            contract=contract,
            result_payload=result_payload,
        )
        return {
            **base,
            "intake_state": "applied",
            "applied": True,
            "would_stage": True,
            "mutated": True,
            "staged_ref": staged,
            "mutation_scope": "intent_workspace_only",
        }
    return {
        **base,
        "intake_state": "blocked",
        "applied": False,
        "mutated": False,
        "blocked_reason": (
            "explicit_operator_route_required"
            if destination in {"write_to_memory_draft", "write_graphiti_episode", "materialize_l2b"}
            else "destination_not_implemented"
        ),
        "supported_apply_destinations": sorted(_SUPPORTED_APPLY_DESTINATIONS),
    }


async def _stage_intent_workspace(
    route: dict[str, Any],
    *,
    body: dict[str, Any],
    contract: dict[str, Any],
    result_payload: Any,
) -> dict[str, Any]:
    from parrot.brain.intent_workspace import (
        PayloadSource,
        StagedRefKind,
        StagedRefMetadata,
        StagedRefRequest,
        get_intent_workspace,
    )

    workflow_id = str(contract.get("workflow_id") or body.get("workflow_id") or "")
    workflow_node_id = str(route.get("workflow_node_id") or body.get("workflow_node_id") or body.get("step_id") or "")
    capability_id = str(route.get("capability_id") or body.get("capability_id") or "")
    payload_text = json.dumps(
        {
            "schema": "workflow_result_intake_payload_v1",
            "workflow_id": workflow_id,
            "workflow_node_id": workflow_node_id,
            "capability_id": capability_id,
            "plan_id": str(body.get("plan_id") or ""),
            "step_id": str(body.get("step_id") or ""),
            "task_id": str(body.get("task_id") or ""),
            "result_channel": str(body.get("result_channel") or ""),
            "result_payload": _safe_json(result_payload),
            "route": _safe_json(route),
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
    handle = await get_intent_workspace().stage(
        StagedRefRequest(
            kind=StagedRefKind.RICH_REPORT,
            payload_source=PayloadSource.INLINE_TEXT,
            payload_value=payload_text,
            metadata=StagedRefMetadata(
                origin="workflow_result_intake",
                kind=StagedRefKind.RICH_REPORT,
                payload_source=PayloadSource.INLINE_TEXT,
                related_plan_id=str(body.get("plan_id") or ""),
                custom_meta={
                    "role": "workflow_result",
                    "workflow_id": workflow_id,
                    "workflow_node_id": workflow_node_id,
                    "capability_id": capability_id,
                    "step_id": str(body.get("step_id") or ""),
                    "task_id": str(body.get("task_id") or ""),
                    "result_channel": str(body.get("result_channel") or ""),
                    "destination": "stage_to_intent_workspace",
                },
            ),
        )
    )
    return {
        "ref_id": handle.ref_id,
        "kind": handle.kind.value if handle.kind else "",
        "role": "workflow_result",
        "origin": "workflow_result_intake",
        "workflow_id": workflow_id,
        "workflow_node_id": workflow_node_id,
        "capability_id": capability_id,
    }


def _result_payload(body: dict[str, Any]) -> Any:
    if "result_payload" in body:
        return body.get("result_payload")
    if "result" in body:
        return body.get("result")
    if "payload" in body:
        return body.get("payload")
    return None


def _entry_state(
    *,
    applied_count: int,
    blocked_count: int,
    preview_count: int,
    dry_run: bool,
    operator_mode: bool,
) -> str:
    if dry_run or not operator_mode:
        return "preview"
    if applied_count and blocked_count:
        return "partial"
    if applied_count:
        return "applied"
    if blocked_count:
        return "blocked"
    if preview_count:
        return "preview"
    return "empty"


def _save_entry(entry: dict[str, Any]) -> None:
    store = _load_store()
    store["entries"] = [row for row in store["entries"] if row.get("entry_id") != entry.get("entry_id")]
    store["entries"].insert(0, entry)
    store["entries"] = store["entries"][:_MAX_ENTRIES]
    _write_store(store)


def _summary(row: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(row, dict):
        return {}
    return {
        "entry_id": row.get("entry_id"),
        "state": row.get("state"),
        "workflow_id": row.get("workflow_id", ""),
        "workflow_node_id": row.get("workflow_node_id", ""),
        "plan_id": row.get("plan_id", ""),
        "step_id": row.get("step_id", ""),
        "task_id": row.get("task_id", ""),
        "result_channel": row.get("result_channel", ""),
        "route_count": row.get("route_count", 0),
        "applied_route_count": row.get("applied_route_count", 0),
        "blocked_route_count": row.get("blocked_route_count", 0),
        "staged_ref_count": row.get("staged_ref_count", 0),
        "created_at": row.get("created_at", ""),
        "updated_at": row.get("updated_at", ""),
        "audit": _audit(),
    }


def _matches(row: dict[str, Any], query: str) -> bool:
    if not query:
        return True
    return query in json.dumps(_summary(row), ensure_ascii=False, sort_keys=True).lower()


def _load_store() -> dict[str, Any]:
    path = _store_path()
    if not path.exists():
        return {"schema_version": _SCHEMA_VERSION, "entries": []}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        entries = raw.get("entries") if isinstance(raw, dict) else []
        if not isinstance(entries, list):
            entries = []
        return {
            "schema_version": _SCHEMA_VERSION,
            "entries": [row for row in entries if isinstance(row, dict)][:_MAX_ENTRIES],
        }
    except Exception:
        return {"schema_version": _SCHEMA_VERSION, "entries": []}


def _write_store(store: dict[str, Any]) -> None:
    path = _store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".{uuid.uuid4().hex[:8]}.tmp")
    tmp.write_text(json.dumps(store, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def _store_path() -> Path:
    raw = os.getenv("PARROT_WEB_CONSOLE_RESULT_INTAKE_PATH", "").strip()
    return Path(raw).expanduser() if raw else Path.cwd() / "data" / "web_console" / "workflow_result_intake.json"


def _receipt(
    *,
    action: str,
    success: bool,
    dry_run: bool,
    operator_mode: bool,
    data: dict[str, Any],
) -> dict[str, Any]:
    return {
        "success": success,
        "action": action,
        "dry_run": dry_run,
        "operator_mode": operator_mode,
        "receipt_id": f"web-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}",
        "data": _safe_json(data),
        "audit": _audit(),
    }


def _audit() -> dict[str, Any]:
    return {
        "web_only": True,
        "storage": "web_console_workflow_result_intake_json",
        "operator_required_for_mutation": True,
        "scheduler_enforced": False,
        "durable_core_contract": False,
        "core_candidate": "CORE-015",
    }


def _safe_id(value: Any) -> str:
    raw = str(value or "").strip()
    clean = re.sub(r"[^A-Za-z0-9_.:-]+", "_", raw)
    return clean[:96].strip("._:-")


def _safe_json(value: Any, *, key: str = "", depth: int = 0) -> Any:
    if _SECRET_KEY_RE.search(key):
        return "[REDACTED]"
    if depth > 8:
        return str(value)[:_MAX_STRING]
    if isinstance(value, dict):
        return {
            str(k)[:160]: _safe_json(v, key=str(k), depth=depth + 1)
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [_safe_json(item, depth=depth + 1) for item in value[:128]]
    if isinstance(value, tuple):
        return [_safe_json(item, depth=depth + 1) for item in value[:128]]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return str(value)[:_MAX_STRING] if isinstance(value, str) else value
    return str(value)[:_MAX_STRING]


def _body_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


__all__ = [
    "intake_workflow_result",
    "list_workflow_result_intakes",
]
