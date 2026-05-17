from __future__ import annotations

import io
import json

from parrot.web_console.flow_cli import main
from parrot.web_console.workflow_drafts import save_workflow_draft


def test_flow_cli_catalog_list_outputs_filtered_json() -> None:
    out = io.StringIO()

    code = main(
        ["catalog", "list", "--kind", "workflow_template", "--q", "workflow_schema", "--limit", "3"],
        stdout=out,
    )
    body = json.loads(out.getvalue())

    assert code == 0
    assert body["action"] == "runtime.capabilities.catalog"
    assert body["success"] is True
    assert body["capabilities"]
    assert len(body["capabilities"]) <= 3
    assert all(row["kind"] == "workflow_template" for row in body["capabilities"])
    assert {row["capability_id"] for row in body["capabilities"]} >= {
        "runtime.workflow.validate",
        "runtime.workflow.export",
        "runtime.workflow.import_preview",
    }


def test_flow_cli_workflow_validate_reuses_schema_validator_and_redacts(tmp_path) -> None:
    workflow_path = tmp_path / "workflow.json"
    workflow_path.write_text(
        json.dumps(
            {
                "workflow_id": "cli-demo",
                "title": "CLI demo",
                "nodes": [
                    {
                        "workflow_node_id": "wf-ref-scan",
                        "capability": {
                            "capability_id": "nanobot.ref_scan",
                            "kind": "nanobot_task",
                            "sample_payload": {"api_token": "do-not-print"},
                        },
                    }
                ],
                "future_canvas_layout": {"x": 10, "y": 20},
            }
        ),
        encoding="utf-8",
    )
    out = io.StringIO()

    code = main(["workflow", "validate", str(workflow_path)], stdout=out)
    body = json.loads(out.getvalue())

    assert code == 0
    assert body["success"] is True
    assert body["data"]["schema"] == "workflow_schema_v1"
    assert body["data"]["summary"]["workflow_id"] == "cli-demo"
    assert body["data"]["workflow"]["extensions"]["unknown_fields"]["future_canvas_layout"] == {"x": 10, "y": 20}
    assert body["data"]["workflow"]["nodes"][0]["capability"]["sample_payload"]["api_token"] == "[REDACTED]"
    assert "do-not-print" not in out.getvalue()


def test_flow_cli_workflow_validate_returns_nonzero_for_bad_workflow(tmp_path) -> None:
    workflow_path = tmp_path / "bad-workflow.json"
    workflow_path.write_text(
        json.dumps({"title": "Bad workflow", "nodes": [{"workflow_node_id": "bad", "capability": {}}]}),
        encoding="utf-8",
    )
    out = io.StringIO()

    code = main(["workflow", "validate", str(workflow_path)], stdout=out)
    body = json.loads(out.getvalue())

    assert code == 2
    assert body["success"] is False
    assert body["data"]["errors"][0]["code"] == "capability_missing_identity"


def test_flow_cli_workflow_validate_reports_invalid_json(tmp_path) -> None:
    workflow_path = tmp_path / "not-json.txt"
    workflow_path.write_text("{not json", encoding="utf-8")
    out = io.StringIO()

    code = main(["workflow", "validate", str(workflow_path)], stdout=out)
    body = json.loads(out.getvalue())

    assert code == 2
    assert body["success"] is False
    assert body["data"]["errors"][0]["code"] == "invalid_json"


def test_flow_cli_workflow_validate_accepts_utf8_bom_json(tmp_path) -> None:
    workflow_path = tmp_path / "workflow-bom.json"
    workflow_path.write_text(
        json.dumps(
            {
                "workflow_id": "cli-bom",
                "nodes": [{"workflow_node_id": "wf-ref-scan", "capability": {"capability_id": "nanobot.ref_scan"}}],
            }
        ),
        encoding="utf-8-sig",
    )
    out = io.StringIO()

    code = main(["workflow", "validate", str(workflow_path)], stdout=out)
    body = json.loads(out.getvalue())

    assert code == 0
    assert body["success"] is True
    assert body["data"]["summary"]["workflow_id"] == "cli-bom"


def test_flow_cli_workflow_export_reads_saved_draft_and_redacts(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("PARROT_WEB_CONSOLE_WORKFLOW_DRAFTS_PATH", str(tmp_path / "workflow_drafts.json"))
    save_workflow_draft(
        {
            "workflow_id": "cli-export",
            "title": "CLI export",
            "workflow_nodes": [
                {
                    "workflow_node_id": "wf-ref-scan",
                    "capability": {
                        "capability_id": "nanobot.ref_scan",
                        "kind": "nanobot_task",
                        "sample_payload": {"api_token": "export-secret"},
                    },
                }
            ],
        }
    )
    out = io.StringIO()

    code = main(["workflow", "export", "cli-export"], stdout=out)
    body = json.loads(out.getvalue())

    assert code == 0
    assert body["action"] == "runtime.workflow.export"
    assert body["data"]["workflow"]["schema"] == "workflow_schema_v1"
    assert body["data"]["summary"]["workflow_id"] == "cli-export"
    assert body["data"]["workflow"]["nodes"][0]["capability"]["sample_payload"]["api_token"] == "[REDACTED]"
    assert "export-secret" not in out.getvalue()


def test_flow_cli_workflow_import_dry_run_reports_diff(tmp_path) -> None:
    imported = tmp_path / "imported.json"
    target = tmp_path / "target.json"
    imported.write_text(
        json.dumps(
            {
                "workflow_id": "cli-import",
                "title": "CLI import",
                "nodes": [
                    {"workflow_node_id": "wf-ref-scan", "capability": {"capability_id": "nanobot.ref_scan"}},
                    {"workflow_node_id": "wf-trigger", "capability": {"capability_id": "trigger.intent", "kind": "trigger"}},
                ],
            }
        ),
        encoding="utf-8",
    )
    target.write_text(
        json.dumps(
            {
                "workflow_id": "cli-target",
                "title": "CLI target",
                "nodes": [{"workflow_node_id": "wf-ref-scan", "capability": {"capability_id": "nanobot.ref_scan"}}],
            }
        ),
        encoding="utf-8",
    )
    out = io.StringIO()

    code = main(["workflow", "import", str(imported), "--target-workflow", str(target)], stdout=out)
    body = json.loads(out.getvalue())

    assert code == 0
    assert body["action"] == "runtime.workflow.import_preview"
    assert body["data"]["would_save"] is False
    assert body["data"]["diff"]["added_nodes"] == ["wf-trigger"]
    assert body["data"]["diff"]["kept_nodes"] == ["wf-ref-scan"]


def test_flow_cli_workflow_import_dry_run_returns_nonzero_for_bad_workflow(tmp_path) -> None:
    imported = tmp_path / "bad-import.json"
    imported.write_text(
        json.dumps({"workflow_id": "bad-import", "nodes": [{"workflow_node_id": "bad", "capability": {}}]}),
        encoding="utf-8",
    )
    out = io.StringIO()

    code = main(["workflow", "import", str(imported)], stdout=out)
    body = json.loads(out.getvalue())

    assert code == 2
    assert body["success"] is False
    assert body["data"]["errors"][0]["code"] == "capability_missing_identity"


def test_flow_cli_workflow_plan_draft_previews_nanobot_steps_and_redacts(tmp_path) -> None:
    workflow_path = tmp_path / "plan-workflow.json"
    workflow_path.write_text(
        json.dumps(
            {
                "workflow_id": "cli-plan",
                "title": "CLI Plan",
                "nodes": [
                    {
                        "workflow_node_id": "wf-ref-scan",
                        "capability": {
                            "capability_id": "nanobot.ref_scan",
                            "title": "Ref scan",
                            "kind": "nanobot_task",
                            "nanobot_task_type": "ref_scan",
                            "plan_step_compatible": True,
                            "result_destinations": ["stage_to_intent_workspace"],
                            "sample_payload": {"api_token": "plan-secret"},
                        },
                    },
                    {
                        "workflow_node_id": "wf-trigger",
                        "capability": {
                            "capability_id": "trigger.intent_event_boundary",
                            "kind": "trigger",
                            "title": "Intent boundary",
                        },
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    out = io.StringIO()

    code = main(["workflow", "plan-draft", str(workflow_path)], stdout=out)
    body = json.loads(out.getvalue())

    assert code == 0
    assert body["action"] == "runtime.workflow.plan_draft"
    assert body["dry_run"] is True
    assert body["operator_mode"] is False
    assert body["data"]["compatible_step_count"] == 1
    assert body["data"]["steps"][0]["expected_tool"] == "ref_scan"
    assert body["data"]["steps"][0]["inputs"]["sample_payload"]["api_token"] == "[REDACTED]"
    assert body["data"]["result_contract"]["schema"] == "workflow_result_contract_v1"
    assert body["data"]["skipped_nodes"][0]["reason"] == "not_nanobot_plan_compatible"
    assert "plan-secret" not in out.getvalue()


def test_flow_cli_workflow_run_dry_run_routes_trigger_and_plan_preview(tmp_path) -> None:
    workflow_path = tmp_path / "run-workflow.json"
    workflow_path.write_text(
        json.dumps(
            {
                "workflow_id": "cli-run",
                "title": "CLI Run",
                "nodes": [
                    {
                        "workflow_node_id": "wf-trigger",
                        "capability": {
                            "capability_id": "trigger.intent_event_boundary",
                            "kind": "trigger",
                            "trigger_name": "intent_event_boundary",
                            "sample_payload": {
                                "trigger_name": "intent_event_boundary",
                                "event": {"type": "intent_boundary", "kind": "cli_run_smoke"},
                                "api_token": "run-secret",
                            },
                        },
                    },
                    {
                        "workflow_node_id": "wf-ref-scan",
                        "capability": {
                            "capability_id": "nanobot.ref_scan",
                            "kind": "nanobot_task",
                            "nanobot_task_type": "ref_scan",
                            "plan_step_compatible": True,
                            "result_destinations": ["stage_to_intent_workspace"],
                        },
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    out = io.StringIO()

    code = main(["workflow", "run", str(workflow_path)], stdout=out)
    body = json.loads(out.getvalue())

    assert code == 0
    assert body["action"] == "runtime.workflow.run"
    assert body["dry_run"] is True
    assert body["operator_mode"] is False
    assert body["data"]["trigger_node_count"] == 1
    assert body["data"]["plan_compatible_count"] == 1
    assert body["data"]["trigger_receipts"][0]["action"] == "dsg.trigger.draft_event"
    assert body["data"]["plan_receipt"]["action"] == "runtime.workflow.plan_draft"
    assert body["data"]["plan_receipt"]["data"]["steps"][0]["expected_tool"] == "ref_scan"
    assert body["data"]["result_contract"]["schema"] == "workflow_result_contract_v1"
    assert "run-secret" not in out.getvalue()


def test_flow_cli_workflow_run_requires_json_or_saved_workflow_id() -> None:
    out = io.StringIO()

    code = main(["workflow", "run"], stdout=out)
    body = json.loads(out.getvalue())

    assert code == 2
    assert body["success"] is False
    assert body["data"]["errors"][0]["code"] == "workflow_input_required"
