"""Thin CLI for Collaboration Flow operator artifacts.

This module is intentionally read-only for the first CLI slice. It reuses the
Web Console catalog and workflow_schema_v1 validator instead of creating a
parallel workflow language.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from pathlib import Path
from typing import Any, TextIO

from parrot.web_console.capability_catalog import build_runtime_capability_catalog
from parrot.web_console.runtime_flow import draft_workflow_plan, run_workflow_draft
from parrot.web_console.workflow_result_intake import intake_workflow_result
from parrot.web_console.workflow_drafts import (
    export_workflow_artifact,
    preview_workflow_import,
    validate_workflow_artifact,
)

_SECRET_KEY_RE = re.compile(r"(secret|token|password|api[_-]?key|authorization|credential)", re.I)


def main(argv: list[str] | None = None, *, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    """Run the flow CLI and return a process exit code."""
    out = stdout or sys.stdout
    err = stderr or sys.stderr
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "catalog" and args.catalog_command == "list":
        receipt = _catalog_list(args)
        _emit(receipt, out, table=args.output == "table")
        return 0
    if args.command == "workflow" and args.workflow_command == "validate":
        receipt = _workflow_validate(args)
        _emit(receipt, out, table=args.output == "table")
        return 0 if receipt.get("success") else 2
    if args.command == "workflow" and args.workflow_command == "export":
        receipt = export_workflow_artifact(args.workflow_id)
        _emit(receipt, out, table=args.output == "table")
        return 0 if receipt.get("success") else 2
    if args.command == "workflow" and args.workflow_command == "import":
        receipt = _workflow_import_preview(args)
        _emit(receipt, out, table=args.output == "table")
        return 0 if receipt.get("success") else 2
    if args.command == "workflow" and args.workflow_command == "plan-draft":
        receipt = _workflow_plan_draft(args)
        _emit(receipt, out, table=args.output == "table")
        return 0 if receipt.get("success") else 2
    if args.command == "workflow" and args.workflow_command == "run":
        receipt = _workflow_run_preview(args)
        _emit(receipt, out, table=args.output == "table")
        return 0 if receipt.get("success") else 2
    if args.command == "result-intake" and args.result_intake_command == "preview":
        receipt = _result_intake_preview(args)
        _emit(receipt, out, table=args.output == "table")
        return 0 if receipt.get("success") else 2
    parser.print_help(err)
    return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="parrot-flow",
        description="Validate Collaboration Flow workflow artifacts and inspect real capability rows.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    catalog = sub.add_parser("catalog", help="Inspect the runtime capability catalog.")
    catalog_sub = catalog.add_subparsers(dest="catalog_command", required=True)
    catalog_list = catalog_sub.add_parser("list", help="List searchable capability rows.")
    catalog_list.add_argument("--q", default="", help="Search query.")
    catalog_list.add_argument("--kind", default="", help="Capability kind filter.")
    catalog_list.add_argument("--execution-policy", default="", help="Execution policy filter.")
    catalog_list.add_argument("--interaction-mode", default="", help="Interaction mode filter, such as L0, L1, C3.")
    catalog_list.add_argument("--limit", type=int, default=0, help="Maximum capability rows to emit.")
    _add_output_flags(catalog_list)

    workflow = sub.add_parser("workflow", help="Validate workflow_schema_v1 artifacts.")
    workflow_sub = workflow.add_subparsers(dest="workflow_command", required=True)
    validate = workflow_sub.add_parser("validate", help="Validate a workflow JSON file or stdin.")
    validate.add_argument("path", help="Workflow JSON path, or '-' for stdin.")
    _add_output_flags(validate)
    export = workflow_sub.add_parser("export", help="Export a saved workflow draft as redacted workflow_schema_v1 JSON.")
    export.add_argument("workflow_id", help="Saved workflow draft id.")
    _add_output_flags(export)
    import_preview = workflow_sub.add_parser("import", help="Dry-run import a workflow JSON file and preview the diff.")
    import_preview.add_argument("path", help="Workflow JSON path, or '-' for stdin.")
    import_preview.add_argument("--target-workflow", default="", help="Optional existing workflow JSON path for diff preview.")
    import_preview.add_argument("--target-workflow-id", default="", help="Optional saved workflow draft id for diff preview.")
    import_preview.add_argument("--dry-run", action="store_true", default=True, help="Import preview only. No draft is saved.")
    _add_output_flags(import_preview)
    plan_draft = workflow_sub.add_parser("plan-draft", help="Preview Plan steps for a workflow JSON file or saved draft.")
    plan_draft.add_argument("path", nargs="?", default="", help="Workflow JSON path, or '-' for stdin.")
    plan_draft.add_argument("--workflow-id", default="", help="Optional saved workflow draft id.")
    plan_draft.add_argument("--title", default="", help="Optional title override for the Plan draft preview.")
    plan_draft.add_argument("--rationale", default="", help="Optional rationale carried in the preview receipt.")
    plan_draft.add_argument("--dry-run", action="store_true", default=True, help="Preview only. No Plan is created.")
    _add_output_flags(plan_draft)
    run = workflow_sub.add_parser("run", help="Preview a workflow run without firing triggers or creating Plans.")
    run.add_argument("path", nargs="?", default="", help="Workflow JSON path, or '-' for stdin.")
    run.add_argument("--workflow-id", default="", help="Optional saved workflow draft id.")
    run.add_argument("--title", default="", help="Optional title override for the run preview.")
    run.add_argument("--rationale", default="", help="Optional rationale carried in the preview receipt.")
    run.add_argument("--dry-run", action="store_true", default=True, help="Preview only. No trigger publish or Plan creation.")
    _add_output_flags(run)

    result_intake = sub.add_parser("result-intake", help="Preview workflow result intake routes.")
    result_intake_sub = result_intake.add_subparsers(dest="result_intake_command", required=True)
    result_preview = result_intake_sub.add_parser("preview", help="Preview result-route intake without recording or staging.")
    result_preview.add_argument("path", help="Result payload JSON path, full intake body JSON path, or '-' for stdin.")
    result_preview.add_argument("--workflow", default="", help="Optional workflow JSON path used to derive a result contract.")
    result_preview.add_argument("--workflow-id", default="", help="Optional saved workflow draft id used to derive a result contract.")
    result_preview.add_argument("--workflow-node-id", default="", help="Optional workflow node id to select routes.")
    result_preview.add_argument("--capability-id", default="", help="Optional capability id to select routes.")
    result_preview.add_argument("--contract", default="", help="Optional workflow_result_contract_v1 JSON path.")
    result_preview.add_argument("--routes", default="", help="Optional result_routes JSON path, either a list or an object with result_routes.")
    result_preview.add_argument("--task-id", default="", help="Optional task id metadata.")
    result_preview.add_argument("--result-channel", default="", help="Optional result channel metadata.")
    result_preview.add_argument("--dry-run", action="store_true", default=True, help="Preview only. No result intake row is recorded.")
    _add_output_flags(result_preview)
    return parser


def _add_output_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--output",
        choices=("json", "table"),
        default="json",
        help="Output format. JSON is the default for automation.",
    )
    parser.add_argument(
        "--json",
        dest="output",
        action="store_const",
        const="json",
        help="Emit JSON. This is the default.",
    )


def _catalog_list(args: argparse.Namespace) -> dict[str, Any]:
    receipt = build_runtime_capability_catalog(
        q=args.q,
        kind=args.kind,
        execution_policy=args.execution_policy,
        interaction_mode=args.interaction_mode,
    )
    limit = max(0, int(args.limit or 0))
    if limit:
        receipt = {**receipt, "capabilities": list(receipt.get("capabilities", []))[:limit]}
    return receipt


def _workflow_validate(args: argparse.Namespace) -> dict[str, Any]:
    try:
        payload = _read_json(args.path)
    except Exception as exc:
        return _error_receipt("runtime.workflow.validate", "invalid_json", str(exc))
    if not isinstance(payload, dict):
        return _error_receipt("runtime.workflow.validate", "workflow_json_not_object", "Workflow JSON must be an object.")
    return validate_workflow_artifact({"workflow": payload})


def _workflow_import_preview(args: argparse.Namespace) -> dict[str, Any]:
    try:
        payload = _read_json(args.path)
    except Exception as exc:
        return _error_receipt("runtime.workflow.import_preview", "invalid_json", str(exc))
    if not isinstance(payload, dict):
        return _error_receipt("runtime.workflow.import_preview", "workflow_json_not_object", "Workflow JSON must be an object.")
    body: dict[str, Any] = {
        "workflow": payload,
        "dry_run": True,
        "operator_mode": False,
    }
    if args.target_workflow:
        try:
            target = _read_json(args.target_workflow)
        except Exception as exc:
            return _error_receipt("runtime.workflow.import_preview", "invalid_target_json", str(exc))
        if not isinstance(target, dict):
            return _error_receipt(
                "runtime.workflow.import_preview",
                "target_workflow_json_not_object",
                "Target workflow JSON must be an object.",
            )
        body["target_workflow"] = target
    if args.target_workflow_id:
        body["target_workflow_id"] = args.target_workflow_id
    return preview_workflow_import(body)


def _workflow_plan_draft(args: argparse.Namespace) -> dict[str, Any]:
    body_or_error = _workflow_preview_body(args, action="runtime.workflow.plan_draft")
    if _is_error_receipt(body_or_error):
        return body_or_error
    return asyncio.run(draft_workflow_plan(body_or_error))


def _workflow_run_preview(args: argparse.Namespace) -> dict[str, Any]:
    body_or_error = _workflow_preview_body(args, action="runtime.workflow.run")
    if _is_error_receipt(body_or_error):
        return body_or_error
    return asyncio.run(run_workflow_draft(body_or_error))


def _result_intake_preview(args: argparse.Namespace) -> dict[str, Any]:
    try:
        payload = _read_json(args.path)
    except Exception as exc:
        return _error_receipt("runtime.workflow.result_intake", "invalid_json", str(exc))
    body = _result_intake_body_from_payload(payload)
    body.update({
        "dry_run": True,
        "operator_mode": False,
    })
    if args.workflow:
        try:
            workflow = _read_json(args.workflow)
        except Exception as exc:
            return _error_receipt("runtime.workflow.result_intake", "invalid_workflow_json", str(exc))
        if not isinstance(workflow, dict):
            return _error_receipt("runtime.workflow.result_intake", "workflow_json_not_object", "Workflow JSON must be an object.")
        body["workflow"] = workflow
    if args.contract:
        try:
            contract = _read_json(args.contract)
        except Exception as exc:
            return _error_receipt("runtime.workflow.result_intake", "invalid_contract_json", str(exc))
        if not isinstance(contract, dict):
            return _error_receipt("runtime.workflow.result_intake", "contract_json_not_object", "Result contract JSON must be an object.")
        body["result_contract"] = contract
    if args.routes:
        try:
            routes_payload = _read_json(args.routes)
        except Exception as exc:
            return _error_receipt("runtime.workflow.result_intake", "invalid_routes_json", str(exc))
        routes = routes_payload.get("result_routes") if isinstance(routes_payload, dict) else routes_payload
        if not isinstance(routes, list):
            return _error_receipt("runtime.workflow.result_intake", "routes_json_not_list", "Result routes JSON must be a list.")
        body["result_routes"] = routes
    for arg_name, body_key in (
        ("workflow_id", "workflow_id"),
        ("workflow_node_id", "workflow_node_id"),
        ("capability_id", "capability_id"),
        ("task_id", "task_id"),
        ("result_channel", "result_channel"),
    ):
        value = getattr(args, arg_name, "")
        if value:
            body[body_key] = value
    if not any(body.get(key) for key in ("result_contract", "workflow", "workflow_id", "result_routes")):
        return _error_receipt(
            "runtime.workflow.result_intake",
            "result_contract_required",
            "Provide --workflow, --workflow-id, --contract, or --routes for intake preview.",
        )
    return asyncio.run(intake_workflow_result(body))


def _result_intake_body_from_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict) and any(
        key in payload
        for key in (
            "result_payload",
            "result",
            "payload",
            "workflow_id",
            "workflow_node_id",
            "capability_id",
            "result_contract",
            "result_routes",
        )
    ):
        return dict(payload)
    return {"result_payload": payload}


def _workflow_preview_body(args: argparse.Namespace, *, action: str) -> dict[str, Any]:
    body: dict[str, Any] = {
        "dry_run": True,
        "operator_mode": False,
    }
    if getattr(args, "workflow_id", ""):
        body["workflow_id"] = args.workflow_id
    if getattr(args, "title", ""):
        body["title"] = args.title
    if getattr(args, "rationale", ""):
        body["rationale"] = args.rationale
    if getattr(args, "path", ""):
        try:
            payload = _read_json(args.path)
        except Exception as exc:
            return _error_receipt(action, "invalid_json", str(exc))
        if not isinstance(payload, dict):
            return _error_receipt(action, "workflow_json_not_object", "Workflow JSON must be an object.")
        body["workflow"] = payload
    if not body.get("workflow") and not body.get("workflow_id"):
        return _error_receipt(action, "workflow_input_required", "Provide a workflow JSON path or --workflow-id.")
    return body


def _is_error_receipt(value: dict[str, Any]) -> bool:
    return value.get("success") is False and isinstance(value.get("data"), dict) and bool(value["data"].get("errors"))


def _read_json(path: str) -> Any:
    if path == "-":
        return json.loads(sys.stdin.read())
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _error_receipt(action: str, code: str, message: str) -> dict[str, Any]:
    return {
        "success": False,
        "action": action,
        "data": {
            "valid": False,
            "errors": [{"code": code, "message": message}],
            "warnings": [],
        },
        "audit": {
            "cli": "parrot-flow",
            "read_only": True,
            "web_only": True,
        },
    }


def _emit(receipt: dict[str, Any], out: TextIO, *, table: bool = False) -> None:
    receipt = _redact_secrets(receipt)
    if table:
        rendered = _table(receipt)
        out.write(rendered)
        if not rendered.endswith("\n"):
            out.write("\n")
        return
    out.write(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    out.write("\n")


def _redact_secrets(value: Any, *, key: str = "") -> Any:
    if _SECRET_KEY_RE.search(key):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {str(k): _redact_secrets(v, key=str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact_secrets(item) for item in value]
    return value


def _table(receipt: dict[str, Any]) -> str:
    if receipt.get("action") == "runtime.capabilities.catalog":
        rows = receipt.get("capabilities") if isinstance(receipt.get("capabilities"), list) else []
        lines = ["capability_id\tkind\texecution_policy\troute"]
        for row in rows:
            if not isinstance(row, dict):
                continue
            lines.append(
                "\t".join(
                    [
                        str(row.get("capability_id") or ""),
                        str(row.get("kind") or ""),
                        str(row.get("execution_policy") or ""),
                        str(row.get("route") or ""),
                    ]
                )
            )
        return "\n".join(lines)
    data = receipt.get("data") if isinstance(receipt.get("data"), dict) else {}
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    diff = data.get("diff") if isinstance(data.get("diff"), dict) else {}
    errors = data.get("errors") if isinstance(data.get("errors"), list) else []
    warnings = data.get("warnings") if isinstance(data.get("warnings"), list) else []
    valid = data.get("valid") if "valid" in data else receipt.get("success")
    lines = [
        f"valid\t{bool(valid)}",
        f"workflow_id\t{receipt.get('workflow_id') or summary.get('workflow_id') or ''}",
        f"nodes\t{summary.get('node_count') or 0}",
        f"workflow_node_count\t{data.get('workflow_node_count') or 0}",
        f"plan_compatible_count\t{data.get('plan_compatible_count') or data.get('compatible_step_count') or 0}",
        f"trigger_node_count\t{data.get('trigger_node_count') or 0}",
        f"route_count\t{data.get('route_count') or 0}",
        f"preview_route_count\t{data.get('preview_route_count') or 0}",
        f"recorded\t{bool(data.get('recorded'))}",
        f"errors\t{len(errors)}",
        f"warnings\t{len(warnings)}",
    ]
    if diff:
        lines.extend(
            [
                f"added_nodes\t{len(diff.get('added_nodes') if isinstance(diff.get('added_nodes'), list) else [])}",
                f"removed_nodes\t{len(diff.get('removed_nodes') if isinstance(diff.get('removed_nodes'), list) else [])}",
                f"kept_nodes\t{len(diff.get('kept_nodes') if isinstance(diff.get('kept_nodes'), list) else [])}",
            ]
        )
    for row in errors:
        if isinstance(row, dict):
            lines.append(f"error\t{row.get('code') or ''}\t{row.get('message') or ''}")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
