"""Web-only durable workflow drafts for the Collaboration Flow workbench."""

from __future__ import annotations

import json
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any

_SCHEMA_VERSION = 1
_MAX_DRAFTS = 80
_MAX_NODES = 48
_MAX_EDGES = 96
_MAX_STRING = 4000
_SECRET_KEY_RE = re.compile(r"(secret|token|password|api[_-]?key|authorization|credential)", re.I)


def list_workflow_drafts(*, q: str = "", limit: int = 50) -> dict[str, Any]:
    """Return bounded workflow draft summaries."""
    query = str(q or "").strip().lower()
    limit = max(1, min(int(limit or 50), _MAX_DRAFTS))
    drafts = sorted(_load_store()["drafts"], key=lambda row: str(row.get("updated_at") or ""), reverse=True)
    rows = [_summary(row) for row in drafts if _matches(row, query)][:limit]
    return {
        "success": True,
        "action": "runtime.workflow_drafts.list",
        "drafts": rows,
        "count": len(rows),
        "audit": _audit(),
    }


def get_workflow_draft(workflow_id: str) -> dict[str, Any]:
    """Return one workflow draft by id."""
    workflow_id = _safe_id(workflow_id)
    for row in _load_store()["drafts"]:
        if row.get("workflow_id") == workflow_id:
            return {
                "success": True,
                "action": "runtime.workflow_drafts.get",
                "draft": row,
                "audit": _audit(),
            }
    return {
        "success": False,
        "action": "runtime.workflow_drafts.get",
        "error": "workflow_draft_not_found",
        "workflow_id": workflow_id,
        "audit": _audit(),
    }


def save_workflow_draft(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create or update a Web-only workflow draft."""
    body = payload or {}
    store = _load_store()
    now = _iso_now()
    workflow = body.get("workflow") if isinstance(body.get("workflow"), dict) else {}
    workflow_id = _safe_id(body.get("workflow_id") or workflow.get("workflow_id") or workflow.get("id"))
    if not workflow_id:
        workflow_id = f"wfd_{uuid.uuid4().hex[:12]}"
    existing = next((row for row in store["drafts"] if row.get("workflow_id") == workflow_id), {})
    nodes = _extract_nodes(body)
    edges = _extract_edges(body)
    title = str(
        body.get("title")
        or workflow.get("title")
        or existing.get("title")
        or "Runtime Flow custom workflow"
    ).strip()[:160]
    draft = {
        "schema_version": _SCHEMA_VERSION,
        "workflow_id": workflow_id,
        "title": title or "Runtime Flow custom workflow",
        "description": _safe_string(body.get("description") or workflow.get("description") or existing.get("description") or ""),
        "nodes": [_safe_json(node) for node in nodes[:_MAX_NODES]],
        "edges": [_safe_json(edge) for edge in edges[:_MAX_EDGES]],
        "result_destinations": _unique_strings(
            body.get("result_destinations")
            or workflow.get("result_destinations")
            or _destinations_from_nodes(nodes)
        ),
        "tags": _unique_strings(body.get("tags") or workflow.get("tags") or []),
        "created_at": str(existing.get("created_at") or now),
        "updated_at": now,
        "source": "web_console.collaboration_flow",
        "audit": {
            "web_only": True,
            "durable_core_contract": False,
            "plan_import_route": "/api/runtime/workflow/plan-draft",
            "operator_required_for_execute": True,
            "storage": "web_console_workflow_drafts_json",
        },
    }
    drafts = [row for row in store["drafts"] if row.get("workflow_id") != workflow_id]
    drafts.insert(0, draft)
    store["drafts"] = drafts[:_MAX_DRAFTS]
    _write_store(store)
    return {
        "success": True,
        "action": "runtime.workflow_drafts.save",
        "workflow_id": workflow_id,
        "draft": draft,
        "summary": _summary(draft),
        "audit": _audit(),
    }


def delete_workflow_draft(workflow_id: str) -> dict[str, Any]:
    """Delete one Web-only workflow draft."""
    workflow_id = _safe_id(workflow_id)
    store = _load_store()
    before = len(store["drafts"])
    store["drafts"] = [row for row in store["drafts"] if row.get("workflow_id") != workflow_id]
    deleted = len(store["drafts"]) != before
    if deleted:
        _write_store(store)
    return {
        "success": deleted,
        "action": "runtime.workflow_drafts.delete",
        "workflow_id": workflow_id,
        "deleted": deleted,
        "audit": _audit(),
    }


def get_workflow_draft_record(workflow_id: str) -> dict[str, Any] | None:
    """Return the raw draft record for internal callers."""
    workflow_id = _safe_id(workflow_id)
    for row in _load_store()["drafts"]:
        if row.get("workflow_id") == workflow_id:
            return row
    return None


def _extract_nodes(body: dict[str, Any]) -> list[Any]:
    if isinstance(body.get("workflow_nodes"), list):
        return list(body["workflow_nodes"])
    workflow = body.get("workflow")
    if isinstance(workflow, dict) and isinstance(workflow.get("nodes"), list):
        return list(workflow["nodes"])
    if isinstance(body.get("nodes"), list):
        return list(body["nodes"])
    return []


def _extract_edges(body: dict[str, Any]) -> list[Any]:
    workflow = body.get("workflow")
    if isinstance(workflow, dict) and isinstance(workflow.get("edges"), list):
        return list(workflow["edges"])
    if isinstance(body.get("edges"), list):
        return list(body["edges"])
    return []


def _destinations_from_nodes(nodes: list[Any]) -> list[str]:
    values: list[str] = []
    for row in nodes:
        if not isinstance(row, dict):
            continue
        capability = row.get("capability") if isinstance(row.get("capability"), dict) else row
        raw = capability.get("result_destinations")
        if isinstance(raw, list):
            values.extend(str(item) for item in raw)
    return _unique_strings(values)


def _summary(row: dict[str, Any]) -> dict[str, Any]:
    nodes = row.get("nodes") if isinstance(row.get("nodes"), list) else []
    trigger_count = 0
    plan_count = 0
    kinds: list[str] = []
    for node in nodes:
        if not isinstance(node, dict):
            continue
        capability = node.get("capability") if isinstance(node.get("capability"), dict) else node
        kind = str(capability.get("kind") or "")
        if kind:
            kinds.append(kind)
        if kind == "trigger":
            trigger_count += 1
        if capability.get("plan_step_compatible") or capability.get("nanobot_task_type"):
            plan_count += 1
    return {
        "workflow_id": row.get("workflow_id"),
        "title": row.get("title"),
        "description": row.get("description", ""),
        "node_count": len(nodes),
        "edge_count": len(row.get("edges") if isinstance(row.get("edges"), list) else []),
        "trigger_count": trigger_count,
        "plan_compatible_count": plan_count,
        "capability_kinds": sorted(set(kinds)),
        "result_destinations": row.get("result_destinations") if isinstance(row.get("result_destinations"), list) else [],
        "tags": row.get("tags") if isinstance(row.get("tags"), list) else [],
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }


def _matches(row: dict[str, Any], query: str) -> bool:
    if not query:
        return True
    haystack = json.dumps(_summary(row), ensure_ascii=False, sort_keys=True).lower()
    for node in row.get("nodes", []) if isinstance(row.get("nodes"), list) else []:
        haystack += " " + json.dumps(node, ensure_ascii=False, sort_keys=True, default=str).lower()
    return query in haystack


def _load_store() -> dict[str, Any]:
    path = _store_path()
    if not path.exists():
        return {"schema_version": _SCHEMA_VERSION, "drafts": []}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        drafts = raw.get("drafts") if isinstance(raw, dict) else []
        if not isinstance(drafts, list):
            drafts = []
        return {
            "schema_version": _SCHEMA_VERSION,
            "drafts": [row for row in drafts if isinstance(row, dict)][:_MAX_DRAFTS],
        }
    except Exception:
        return {"schema_version": _SCHEMA_VERSION, "drafts": []}


def _write_store(store: dict[str, Any]) -> None:
    path = _store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".{uuid.uuid4().hex[:8]}.tmp")
    tmp.write_text(json.dumps(store, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def _store_path() -> Path:
    raw = os.getenv("PARROT_WEB_CONSOLE_WORKFLOW_DRAFTS_PATH", "").strip()
    return Path(raw).expanduser() if raw else Path.cwd() / "data" / "web_console" / "workflow_drafts.json"


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
            _safe_string(k)[:160]: _safe_json(v, key=str(k), depth=depth + 1)
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [_safe_json(item, depth=depth + 1) for item in value[:128]]
    if isinstance(value, tuple):
        return [_safe_json(item, depth=depth + 1) for item in value[:128]]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return _safe_string(value) if isinstance(value, str) else value
    return _safe_string(value)


def _safe_string(value: Any) -> str:
    return str(value or "")[:_MAX_STRING]


def _unique_strings(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    out: list[str] = []
    seen: set[str] = set()
    for item in values:
        value = str(item or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value[:120])
    return out[:24]


def _iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _audit() -> dict[str, Any]:
    return {
        "web_only": True,
        "durable_core_contract": False,
        "storage": "web_console_workflow_drafts_json",
        "operator_required_for_execute": True,
    }


__all__ = [
    "delete_workflow_draft",
    "get_workflow_draft",
    "get_workflow_draft_record",
    "list_workflow_drafts",
    "save_workflow_draft",
]
