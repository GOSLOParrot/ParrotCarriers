"""Web-only action gates for Collaboration Flow trigger/message nodes."""

from __future__ import annotations

import json
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any

_SCHEMA_VERSION = 1
_MAX_GATES = 160
_MAX_STRING = 4000
_SECRET_KEY_RE = re.compile(r"(secret|token|password|api[_-]?key|authorization|credential)", re.I)
_TERMINAL_STATES = frozenset({"applied", "rejected", "cancelled", "failed"})
_VALID_DECISIONS = frozenset({"apply", "approve", "reject", "cancel"})


def list_workflow_action_gates(*, state: str = "pending", q: str = "", limit: int = 50) -> dict[str, Any]:
    """Return bounded Web-only workflow action gates."""
    query = str(q or "").strip().lower()
    state_filter = str(state or "").strip().lower()
    limit = max(1, min(int(limit or 50), _MAX_GATES))
    gates = sorted(_load_store()["gates"], key=lambda row: str(row.get("updated_at") or ""), reverse=True)
    rows = [
        _summary(row)
        for row in gates
        if (not state_filter or str(row.get("state") or "") == state_filter)
        and _matches(row, query)
    ][:limit]
    return {
        "success": True,
        "action": "runtime.workflow.action_gates.list",
        "gates": rows,
        "count": len(rows),
        "audit": _audit(),
    }


def draft_workflow_action_gate(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create a pending gate for a trigger/message workflow node."""
    body = payload or {}
    node = _workflow_node_from_payload(body)
    if node is None:
        return _receipt(
            action="runtime.workflow.action_gate.draft",
            success=False,
            dry_run=True,
            operator_mode=False,
            data={
                "error": "workflow_node_not_found",
                "workflow_id": str(body.get("workflow_id") or ""),
                "workflow_node_id": str(body.get("workflow_node_id") or ""),
            },
        )
    action_spec = _action_spec_for_node(node, body)
    if action_spec.get("error"):
        return _receipt(
            action="runtime.workflow.action_gate.draft",
            success=False,
            dry_run=True,
            operator_mode=False,
            data=action_spec,
        )

    store = _load_store()
    gate_id = _safe_id(body.get("gate_id")) or f"wag_{uuid.uuid4().hex[:12]}"
    now = _iso_now()
    gate = {
        "schema_version": _SCHEMA_VERSION,
        "gate_id": gate_id,
        "state": "pending",
        "target_kind": "workflow_action",
        "action_kind": action_spec["action_kind"],
        "workflow_id": str(body.get("workflow_id") or action_spec.get("workflow_id") or ""),
        "workflow_node_id": action_spec["workflow_node_id"],
        "capability_id": action_spec["capability_id"],
        "title": str(body.get("title") or action_spec["title"] or "Workflow action gate")[:160],
        "summary": action_spec["summary"],
        "payload": _safe_json(action_spec["payload"]),
        "draft_route": action_spec["draft_route"],
        "apply_route": action_spec["apply_route"],
        "preview_receipt": _safe_json(action_spec["preview_receipt"]),
        "created_at": now,
        "updated_at": now,
        "decision_history": [],
        "audit": _audit(),
    }
    store["gates"] = [row for row in store["gates"] if row.get("gate_id") != gate_id]
    store["gates"].insert(0, gate)
    store["gates"] = store["gates"][:_MAX_GATES]
    _write_store(store)
    return _receipt(
        action="runtime.workflow.action_gate.draft",
        success=True,
        dry_run=True,
        operator_mode=False,
        data={
            "gate": _summary(gate),
            "preview_receipt": gate["preview_receipt"],
            "operator_required_for_execute": True,
        },
    )


async def apply_workflow_action_gate(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Apply or close a workflow action gate under explicit operator policy."""
    body = payload or {}
    gate_id = _safe_id(body.get("gate_id"))
    decision = str(body.get("decision") or body.get("action") or "apply").strip().lower()
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    store = _load_store()
    gate = next((row for row in store["gates"] if row.get("gate_id") == gate_id), None)
    if gate is None:
        return _receipt(
            action="runtime.workflow.action_gate.apply",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={"gate_id": gate_id, "decision": decision, "error": "action_gate_not_found"},
        )
    validation_error = _decision_error(gate, decision)
    if validation_error:
        return _receipt(
            action="runtime.workflow.action_gate.apply",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "gate": _summary(gate),
                "decision": decision,
                "error": validation_error,
                "valid_decisions": sorted(_VALID_DECISIONS),
            },
        )

    preview_receipt = await _preview_gate_receipt(gate)
    if dry_run or not operator_mode:
        return _receipt(
            action="runtime.workflow.action_gate.apply",
            success=True,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "gate": _summary(gate),
                "decision": decision,
                "would_apply": decision in {"apply", "approve"},
                "apply_skipped_reason": "dry_run_or_operator_mode_missing",
                "preview_receipt": preview_receipt,
            },
        )

    now = _iso_now()
    execution_receipt: dict[str, Any] | None = None
    next_state = str(gate.get("state") or "pending")
    if decision in {"reject", "cancel"}:
        next_state = "rejected" if decision == "reject" else "cancelled"
    else:
        execution_receipt = await _execute_gate(gate)
        next_state = "applied" if execution_receipt.get("success") else "failed"

    history = gate.get("decision_history") if isinstance(gate.get("decision_history"), list) else []
    history.append({
        "decision": decision,
        "at": now,
        "operator_mode": True,
        "dry_run": False,
        "result_state": next_state,
        "execution_action": execution_receipt.get("action") if isinstance(execution_receipt, dict) else "",
    })
    gate.update({
        "state": next_state,
        "updated_at": now,
        "decision_history": history[-24:],
        "last_execution_receipt": _safe_json(execution_receipt) if execution_receipt else {},
    })
    _write_store(store)
    return _receipt(
        action="runtime.workflow.action_gate.apply",
        success=next_state in {"applied", "rejected", "cancelled"},
        dry_run=False,
        operator_mode=True,
        data={
            "gate": _summary(gate),
            "decision": decision,
            "applied": next_state == "applied",
            "execution_receipt": execution_receipt,
        },
    )


def delete_workflow_action_gate(gate_id: str) -> dict[str, Any]:
    """Hard-delete one Web-only action gate for smoke/test cleanup."""
    gate_id = _safe_id(gate_id)
    store = _load_store()
    before = len(store["gates"])
    store["gates"] = [row for row in store["gates"] if row.get("gate_id") != gate_id]
    deleted = len(store["gates"]) != before
    if deleted:
        _write_store(store)
    return {
        "success": deleted,
        "action": "runtime.workflow.action_gate.delete",
        "gate_id": gate_id,
        "deleted": deleted,
        "audit": _audit(),
    }


async def _preview_gate_receipt(gate: dict[str, Any]) -> dict[str, Any]:
    action_kind = str(gate.get("action_kind") or "")
    payload = gate.get("payload") if isinstance(gate.get("payload"), dict) else {}
    if action_kind == "trigger_event":
        from parrot.web_console.memory_ops import draft_trigger_event

        return draft_trigger_event({**payload, "dry_run": True, "operator_mode": False})
    if action_kind == "message_check":
        from parrot.web_console.memory_ops import draft_message_check

        return draft_message_check({**payload, "dry_run": True, "operator_mode": False})
    if action_kind == "message_push":
        from parrot.web_console.memory_ops import push_test_message

        return await push_test_message({**payload, "dry_run": True, "operator_mode": False})
    return {"success": False, "action": "runtime.workflow.action_gate.preview", "data": {"error": "unsupported_action_kind"}}


async def _execute_gate(gate: dict[str, Any]) -> dict[str, Any]:
    action_kind = str(gate.get("action_kind") or "")
    payload = gate.get("payload") if isinstance(gate.get("payload"), dict) else {}
    if action_kind == "trigger_event":
        from parrot.web_console.memory_ops import fire_trigger_event

        return await fire_trigger_event({**payload, "dry_run": False, "operator_mode": True})
    if action_kind == "message_check":
        from parrot.web_console.memory_ops import dispatch_message_check

        return await dispatch_message_check({**payload, "dry_run": False, "operator_mode": True})
    if action_kind == "message_push":
        from parrot.web_console.memory_ops import push_test_message

        return await push_test_message({**payload, "dry_run": False, "operator_mode": True})
    return {"success": False, "action": "runtime.workflow.action_gate.execute", "data": {"error": "unsupported_action_kind"}}


def _workflow_node_from_payload(body: dict[str, Any]) -> dict[str, Any] | None:
    node = body.get("workflow_node")
    if isinstance(node, dict):
        return node
    if isinstance(body.get("node"), dict):
        return body["node"]
    workflow_id = str(body.get("workflow_id") or "").strip()
    workflow_node_id = str(body.get("workflow_node_id") or "").strip()
    if workflow_id and workflow_node_id:
        from parrot.web_console.workflow_drafts import get_workflow_draft_record

        draft = get_workflow_draft_record(workflow_id) or {}
        for row in draft.get("nodes", []) if isinstance(draft.get("nodes"), list) else []:
            if isinstance(row, dict) and str(row.get("workflow_node_id") or "") == workflow_node_id:
                return row
    if isinstance(body.get("capability"), dict):
        return {
            "workflow_node_id": str(body.get("workflow_node_id") or ""),
            "capability": body["capability"],
        }
    return None


def _action_spec_for_node(node: dict[str, Any], body: dict[str, Any]) -> dict[str, Any]:
    capability = node.get("capability") if isinstance(node.get("capability"), dict) else node
    workflow_node_id = str(node.get("workflow_node_id") or body.get("workflow_node_id") or "")
    capability_id = str(capability.get("capability_id") or "")
    kind = str(capability.get("kind") or "")
    task_type = str(capability.get("nanobot_task_type") or "")
    title = str(capability.get("title") or capability_id or "Workflow action")
    if kind == "trigger":
        payload = _trigger_payload(capability, workflow_node_id)
        from parrot.web_console.memory_ops import draft_trigger_event

        return {
            "workflow_id": str(body.get("workflow_id") or ""),
            "workflow_node_id": workflow_node_id,
            "capability_id": capability_id,
            "title": title,
            "summary": f"Trigger {payload.get('trigger_name') or capability_id}",
            "action_kind": "trigger_event",
            "draft_route": "/api/dsg/triggers/draft-event",
            "apply_route": "/api/dsg/triggers/fire-event",
            "payload": payload,
            "preview_receipt": draft_trigger_event({**payload, "dry_run": True, "operator_mode": False}),
        }
    if task_type == "message_check":
        payload = _message_check_payload(capability)
        from parrot.web_console.memory_ops import draft_message_check

        return {
            "workflow_id": str(body.get("workflow_id") or ""),
            "workflow_node_id": workflow_node_id,
            "capability_id": capability_id,
            "title": title,
            "summary": "Dispatch message_check through Scheduler/Nanobot",
            "action_kind": "message_check",
            "draft_route": "/api/google/messages/check",
            "apply_route": "/api/google/messages/check",
            "payload": payload,
            "preview_receipt": draft_message_check({**payload, "dry_run": True, "operator_mode": False}),
        }
    return {
        "workflow_node_id": workflow_node_id,
        "capability_id": capability_id,
        "kind": kind,
        "nanobot_task_type": task_type,
        "error": "unsupported_action_gate_target",
        "supported_targets": ["trigger", "nanobot.message_check"],
    }


def _trigger_payload(capability: dict[str, Any], workflow_node_id: str) -> dict[str, Any]:
    sample = capability.get("sample_payload") if isinstance(capability.get("sample_payload"), dict) else {}
    event = sample.get("event") if isinstance(sample.get("event"), dict) else {}
    if not event:
        event = {
            "type": "workflow_capability_fire",
            "kind": str(capability.get("trigger_name") or capability.get("capability_id") or "trigger"),
            "source": "runtime_flow_workbench",
        }
    return {
        **sample,
        "trigger_name": str(sample.get("trigger_name") or capability.get("trigger_name") or ""),
        "event": {
            **event,
            "workflow_node_id": workflow_node_id,
            "workflow_capability_id": str(capability.get("capability_id") or ""),
        },
    }


def _message_check_payload(capability: dict[str, Any]) -> dict[str, Any]:
    sample = capability.get("sample_payload") if isinstance(capability.get("sample_payload"), dict) else {}
    return {
        "query": str(sample.get("query") or "Check Gmail for unread important messages"),
        "instructions": str(sample.get("instructions") or ""),
        "priority": str(sample.get("priority") or "normal"),
        "result_channel": str(sample.get("result_channel") or "message_result"),
    }


def _decision_error(gate: dict[str, Any], decision: str) -> str:
    if decision not in _VALID_DECISIONS:
        return "invalid_action_gate_decision"
    if str(gate.get("state") or "") in _TERMINAL_STATES:
        return "action_gate_already_terminal"
    return ""


def _summary(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "gate_id": row.get("gate_id"),
        "state": row.get("state"),
        "target_kind": row.get("target_kind"),
        "action_kind": row.get("action_kind"),
        "workflow_id": row.get("workflow_id", ""),
        "workflow_node_id": row.get("workflow_node_id", ""),
        "capability_id": row.get("capability_id", ""),
        "title": row.get("title", ""),
        "summary": row.get("summary", ""),
        "draft_route": row.get("draft_route", ""),
        "apply_route": row.get("apply_route", ""),
        "created_at": row.get("created_at", ""),
        "updated_at": row.get("updated_at", ""),
        "decision_count": len(row.get("decision_history") if isinstance(row.get("decision_history"), list) else []),
        "last_execution_receipt": row.get("last_execution_receipt") if isinstance(row.get("last_execution_receipt"), dict) else {},
        "audit": _audit(),
    }


def _matches(row: dict[str, Any], query: str) -> bool:
    if not query:
        return True
    return query in json.dumps(_summary(row), ensure_ascii=False, sort_keys=True).lower()


def _load_store() -> dict[str, Any]:
    path = _store_path()
    if not path.exists():
        return {"schema_version": _SCHEMA_VERSION, "gates": []}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        gates = raw.get("gates") if isinstance(raw, dict) else []
        if not isinstance(gates, list):
            gates = []
        return {
            "schema_version": _SCHEMA_VERSION,
            "gates": [row for row in gates if isinstance(row, dict)][:_MAX_GATES],
        }
    except Exception:
        return {"schema_version": _SCHEMA_VERSION, "gates": []}


def _write_store(store: dict[str, Any]) -> None:
    path = _store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".{uuid.uuid4().hex[:8]}.tmp")
    tmp.write_text(json.dumps(store, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def _store_path() -> Path:
    raw = os.getenv("PARROT_WEB_CONSOLE_ACTION_GATES_PATH", "").strip()
    return Path(raw).expanduser() if raw else Path.cwd() / "data" / "web_console" / "workflow_action_gates.json"


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
        "storage": "web_console_workflow_action_gates_json",
        "operator_required_for_execute": True,
        "durable_core_contract": False,
        "core_candidate": "CORE-011",
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
    "apply_workflow_action_gate",
    "delete_workflow_action_gate",
    "draft_workflow_action_gate",
    "list_workflow_action_gates",
]
