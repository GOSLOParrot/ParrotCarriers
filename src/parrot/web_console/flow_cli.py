"""Thin CLI for Collaboration Flow operator artifacts.

This module is intentionally read-only for the first CLI slice. It reuses the
Web Console catalog and workflow_schema_v1 validator instead of creating a
parallel workflow language.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, TextIO

from parrot.web_console.capability_catalog import build_runtime_capability_catalog
from parrot.web_console.workflow_drafts import validate_workflow_artifact


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
    if table:
        rendered = _table(receipt)
        out.write(rendered)
        if not rendered.endswith("\n"):
            out.write("\n")
        return
    out.write(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    out.write("\n")


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
    errors = data.get("errors") if isinstance(data.get("errors"), list) else []
    warnings = data.get("warnings") if isinstance(data.get("warnings"), list) else []
    lines = [
        f"valid\t{bool(data.get('valid'))}",
        f"workflow_id\t{summary.get('workflow_id') or ''}",
        f"nodes\t{summary.get('node_count') or 0}",
        f"errors\t{len(errors)}",
        f"warnings\t{len(warnings)}",
    ]
    for row in errors:
        if isinstance(row, dict):
            lines.append(f"error\t{row.get('code') or ''}\t{row.get('message') or ''}")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
