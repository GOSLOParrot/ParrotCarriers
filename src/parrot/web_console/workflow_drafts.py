"""Web-only durable workflow drafts for the Collaboration Flow workbench."""

from __future__ import annotations

import json
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any

_SCHEMA = "workflow_schema_v1"
_SCHEMA_VERSION = 1
_MAX_DRAFTS = 80
_MAX_NODES = 48
_MAX_EDGES = 96
_MAX_STRING = 4000
_SECRET_KEY_RE = re.compile(r"(secret|token|password|api[_-]?key|authorization|credential)", re.I)
_KNOWN_WORKFLOW_KEYS = {
    "schema",
    "schema_version",
    "workflow_id",
    "id",
    "title",
    "description",
    "nodes",
    "workflow_nodes",
    "edges",
    "result_destinations",
    "tags",
    "created_at",
    "updated_at",
    "source",
    "audit",
    "extensions",
    "raw",
}


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
    workflow = _workflow_payload(body)
    workflow_id = _safe_id(body.get("workflow_id") or workflow.get("workflow_id") or workflow.get("id"))
    if not workflow_id:
        workflow_id = f"wfd_{uuid.uuid4().hex[:12]}"
    existing = next((row for row in store["drafts"] if row.get("workflow_id") == workflow_id), {})
    draft = _normalize_workflow_artifact(body, existing=existing, workflow_id=workflow_id, updated_at=now)
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


def validate_workflow_artifact(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate and normalize a portable Collaboration Flow workflow artifact."""
    body = payload or {}
    workflow = _normalize_workflow_artifact(body)
    errors, warnings = _validate_normalized_workflow(workflow, body)
    valid = not errors
    return {
        "success": valid,
        "action": "runtime.workflow.validate",
        "data": {
            "schema": _SCHEMA,
            "valid": valid,
            "workflow": workflow,
            "summary": _summary(workflow),
            "errors": errors,
            "warnings": warnings,
            "redaction_applied": _contains_secret_key(body),
            "limits": {
                "max_nodes": _MAX_NODES,
                "max_edges": _MAX_EDGES,
                "max_string": _MAX_STRING,
            },
        },
        "audit": _audit(),
    }


def export_workflow_artifact(workflow_id: str) -> dict[str, Any]:
    """Return a redacted portable workflow artifact for a saved draft."""
    record = get_workflow_draft_record(workflow_id)
    safe_workflow_id = _safe_id(workflow_id)
    if not record:
        return {
            "success": False,
            "action": "runtime.workflow.export",
            "error": "workflow_draft_not_found",
            "workflow_id": safe_workflow_id,
            "audit": _audit(),
        }
    workflow = _normalize_workflow_artifact(record, existing=record, workflow_id=safe_workflow_id)
    validation = validate_workflow_artifact({"workflow": workflow})
    return {
        "success": bool(validation.get("success")),
        "action": "runtime.workflow.export",
        "workflow_id": safe_workflow_id,
        "data": {
            "schema": _SCHEMA,
            "workflow": workflow,
            "summary": _summary(workflow),
            "validation": validation.get("data", {}),
            "redaction_applied": _contains_secret_key(record),
        },
        "audit": _audit(),
    }


def preview_workflow_import(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate an imported workflow and report a non-mutating diff preview."""
    body = payload or {}
    workflow_body = _workflow_payload(body)
    imported = _normalize_workflow_artifact(workflow_body)
    errors, warnings = _validate_normalized_workflow(imported, workflow_body)
    target = _target_workflow_for_diff(body)
    diff = _workflow_diff(imported, target)
    valid = not errors
    return {
        "success": valid,
        "action": "runtime.workflow.import_preview",
        "data": {
            "schema": _SCHEMA,
            "valid": valid,
            "workflow": imported,
            "summary": _summary(imported),
            "diff": diff,
            "errors": errors,
            "warnings": warnings,
            "would_save": False,
            "save_route": "/api/runtime/workflows/drafts",
            "redaction_applied": _contains_secret_key(body),
        },
        "audit": _audit(),
    }


def _normalize_workflow_artifact(
    payload: dict[str, Any],
    *,
    existing: dict[str, Any] | None = None,
    workflow_id: str = "",
    updated_at: str = "",
) -> dict[str, Any]:
    existing = existing or {}
    body = payload if isinstance(payload, dict) else {}
    workflow = _workflow_payload(body)
    nodes = _extract_nodes(body)
    if not nodes and workflow is not body:
        nodes = _extract_nodes(workflow)
    edges = _extract_edges(body)
    if not edges and workflow is not body:
        edges = _extract_edges(workflow)
    now = updated_at or _iso_now()
    safe_workflow_id = _safe_id(
        workflow_id
        or body.get("workflow_id")
        or workflow.get("workflow_id")
        or workflow.get("id")
        or existing.get("workflow_id")
    )
    title = str(
        body.get("title")
        or workflow.get("title")
        or existing.get("title")
        or "Runtime Flow custom workflow"
    ).strip()[:160]
    destinations = _unique_strings(
        body.get("result_destinations")
        or workflow.get("result_destinations")
        or existing.get("result_destinations")
        or _destinations_from_nodes(nodes)
    )
    artifact = {
        "schema": _SCHEMA,
        "schema_version": _SCHEMA_VERSION,
        "workflow_id": safe_workflow_id,
        "title": title or "Runtime Flow custom workflow",
        "description": _safe_string(
            body.get("description")
            or workflow.get("description")
            or existing.get("description")
            or ""
        ),
        "nodes": _normalize_nodes(nodes),
        "edges": [_safe_json(edge) for edge in edges[:_MAX_EDGES]],
        "result_destinations": destinations,
        "tags": _unique_strings(body.get("tags") or workflow.get("tags") or existing.get("tags") or []),
        "created_at": str(existing.get("created_at") or workflow.get("created_at") or now),
        "updated_at": now,
        "source": str(workflow.get("source") or existing.get("source") or "web_console.collaboration_flow")[:160],
        "extensions": _safe_json(_workflow_extensions(workflow)),
        "audit": {
            "web_only": True,
            "durable_core_contract": False,
            "plan_import_route": "/api/runtime/workflow/plan-draft",
            "operator_required_for_execute": True,
            "storage": "web_console_workflow_drafts_json",
            "schema": _SCHEMA,
        },
    }
    if isinstance(workflow.get("raw"), dict):
        artifact["raw"] = _safe_json(workflow.get("raw"))
    return artifact


def _workflow_payload(body: dict[str, Any]) -> dict[str, Any]:
    if isinstance(body.get("workflow"), dict):
        return body["workflow"]
    if isinstance(body.get("draft"), dict):
        return body["draft"]
    data = body.get("data")
    if isinstance(data, dict) and isinstance(data.get("workflow"), dict):
        return data["workflow"]
    return body


def _normalize_nodes(nodes: list[Any]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, node in enumerate(nodes[:_MAX_NODES]):
        if not isinstance(node, dict):
            continue
        safe = _safe_json(node)
        if isinstance(safe, dict):
            safe.setdefault("workflow_node_id", f"wf-import-{index + 1}")
            normalized.append(safe)
    return normalized


def _workflow_extensions(workflow: dict[str, Any]) -> dict[str, Any]:
    explicit = workflow.get("extensions") if isinstance(workflow.get("extensions"), dict) else {}
    unknown = {
        str(key): value
        for key, value in workflow.items()
        if key not in _KNOWN_WORKFLOW_KEYS
    }
    return {
        **explicit,
        **({"unknown_fields": unknown} if unknown else {}),
    }


def _validate_normalized_workflow(
    workflow: dict[str, Any],
    original: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    raw_nodes = _extract_nodes(original)
    if not raw_nodes and _workflow_payload(original) is not original:
        raw_nodes = _extract_nodes(_workflow_payload(original))
    raw_edges = _extract_edges(original)
    if not raw_edges and _workflow_payload(original) is not original:
        raw_edges = _extract_edges(_workflow_payload(original))
    nodes = workflow.get("nodes") if isinstance(workflow.get("nodes"), list) else []
    edges = workflow.get("edges") if isinstance(workflow.get("edges"), list) else []
    if not nodes:
        errors.append({"code": "workflow_has_no_nodes", "message": "Workflow must contain at least one node."})
    if len(raw_nodes) > _MAX_NODES:
        warnings.append({"code": "nodes_truncated", "message": f"Workflow nodes were truncated to {_MAX_NODES}."})
    if len(raw_edges) > _MAX_EDGES:
        warnings.append({"code": "edges_truncated", "message": f"Workflow edges were truncated to {_MAX_EDGES}."})
    node_ids: set[str] = set()
    for index, raw_node in enumerate(raw_nodes[:_MAX_NODES]):
        if not isinstance(raw_node, dict):
            errors.append({"code": "node_not_object", "index": index})
            continue
        if not raw_node.get("workflow_node_id"):
            warnings.append({"code": "node_id_assigned", "index": index})
    for index, node in enumerate(nodes):
        node_id = str(node.get("workflow_node_id") or "")
        if node_id:
            node_ids.add(node_id)
        capability = node.get("capability") if isinstance(node.get("capability"), dict) else node
        if not isinstance(capability, dict):
            errors.append({"code": "node_missing_capability", "index": index, "workflow_node_id": node_id})
            continue
        if not any(capability.get(key) for key in ("capability_id", "route", "kind", "nanobot_task_type", "trigger_name")):
            errors.append({"code": "capability_missing_identity", "index": index, "workflow_node_id": node_id})
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            errors.append({"code": "edge_not_object", "index": index})
            continue
        source = str(edge.get("source") or edge.get("from") or "")
        target = str(edge.get("target") or edge.get("to") or "")
        if not source or not target:
            warnings.append({"code": "edge_missing_endpoint", "index": index})
            continue
        if node_ids and (source not in node_ids or target not in node_ids):
            warnings.append({"code": "edge_dangling_endpoint", "index": index, "source": source, "target": target})
    return errors, warnings


def _target_workflow_for_diff(body: dict[str, Any]) -> dict[str, Any]:
    target_workflow_id = _safe_id(body.get("target_workflow_id") or body.get("current_workflow_id"))
    if target_workflow_id:
        record = get_workflow_draft_record(target_workflow_id)
        if record:
            return _normalize_workflow_artifact(record, existing=record, workflow_id=target_workflow_id)
    for key in ("target_workflow", "current_workflow", "existing_workflow"):
        if isinstance(body.get(key), dict):
            return _normalize_workflow_artifact(body[key])
    return _normalize_workflow_artifact({"workflow_id": target_workflow_id, "title": "empty target", "nodes": []})


def _workflow_diff(imported: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    imported_nodes = _nodes_by_id(imported)
    target_nodes = _nodes_by_id(target)
    imported_ids = set(imported_nodes)
    target_ids = set(target_nodes)
    imported_caps = _capability_ids(imported_nodes.values())
    target_caps = _capability_ids(target_nodes.values())
    return {
        "target_workflow_id": target.get("workflow_id"),
        "added_nodes": sorted(imported_ids - target_ids),
        "removed_nodes": sorted(target_ids - imported_ids),
        "kept_nodes": sorted(imported_ids & target_ids),
        "added_capabilities": sorted(imported_caps - target_caps),
        "removed_capabilities": sorted(target_caps - imported_caps),
        "title_changed": str(imported.get("title") or "") != str(target.get("title") or ""),
        "result_destinations_changed": imported.get("result_destinations") != target.get("result_destinations"),
        "tag_changed": imported.get("tags") != target.get("tags"),
        "imported_summary": _summary(imported),
        "target_summary": _summary(target),
    }


def _nodes_by_id(workflow: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for index, node in enumerate(workflow.get("nodes", []) if isinstance(workflow.get("nodes"), list) else []):
        if not isinstance(node, dict):
            continue
        node_id = str(node.get("workflow_node_id") or f"node-{index + 1}")
        rows[node_id] = node
    return rows


def _capability_ids(nodes: Any) -> set[str]:
    ids: set[str] = set()
    for node in nodes:
        if not isinstance(node, dict):
            continue
        capability = node.get("capability") if isinstance(node.get("capability"), dict) else node
        if not isinstance(capability, dict):
            continue
        value = str(
            capability.get("capability_id")
            or capability.get("route")
            or capability.get("kind")
            or capability.get("nanobot_task_type")
            or ""
        ).strip()
        if value:
            ids.add(value)
    return ids


def _contains_secret_key(value: Any, *, key: str = "") -> bool:
    if _SECRET_KEY_RE.search(key):
        return True
    if isinstance(value, dict):
        return any(_contains_secret_key(v, key=str(k)) for k, v in value.items())
    if isinstance(value, list):
        return any(_contains_secret_key(item) for item in value)
    return False


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
        return {"schema": _SCHEMA, "schema_version": _SCHEMA_VERSION, "drafts": []}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        drafts = raw.get("drafts") if isinstance(raw, dict) else []
        if not isinstance(drafts, list):
            drafts = []
        return {
            "schema": _SCHEMA,
            "schema_version": _SCHEMA_VERSION,
            "drafts": [row for row in drafts if isinstance(row, dict)][:_MAX_DRAFTS],
        }
    except Exception:
        return {"schema": _SCHEMA, "schema_version": _SCHEMA_VERSION, "drafts": []}


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
    "export_workflow_artifact",
    "get_workflow_draft",
    "get_workflow_draft_record",
    "list_workflow_drafts",
    "preview_workflow_import",
    "save_workflow_draft",
    "validate_workflow_artifact",
]
