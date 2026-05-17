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


def test_flow_cli_result_intake_preview_uses_workflow_contract_and_redacts(tmp_path) -> None:
    workflow_path = tmp_path / "intake-workflow.json"
    result_path = tmp_path / "result.json"
    workflow_path.write_text(
        json.dumps(
            {
                "workflow_id": "cli-intake",
                "title": "CLI Intake",
                "nodes": [
                    {
                        "workflow_node_id": "wf-ref-scan",
                        "capability": {
                            "capability_id": "nanobot.ref_scan",
                            "kind": "nanobot_task",
                            "nanobot_task_type": "ref_scan",
                            "plan_step_compatible": True,
                            "result_destinations": ["stage_to_intent_workspace", "return_to_goslo"],
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    result_path.write_text(
        json.dumps({"summary": "Ref scan finished", "api_token": "intake-secret"}),
        encoding="utf-8",
    )
    out = io.StringIO()

    code = main(
        [
            "result-intake",
            "preview",
            str(result_path),
            "--workflow",
            str(workflow_path),
            "--workflow-id",
            "cli-intake",
            "--workflow-node-id",
            "wf-ref-scan",
        ],
        stdout=out,
    )
    body = json.loads(out.getvalue())

    assert code == 0
    assert body["action"] == "runtime.workflow.result_intake"
    assert body["dry_run"] is True
    assert body["operator_mode"] is False
    assert body["data"]["recorded"] is False
    assert body["data"]["route_count"] == 2
    assert body["data"]["preview_route_count"] == 2
    assert {row["destination"] for row in body["data"]["route_results"]} == {
        "stage_to_intent_workspace",
        "return_to_goslo",
    }
    assert any(row.get("would_stage") for row in body["data"]["route_results"])
    assert "intake-secret" not in out.getvalue()


def test_flow_cli_result_intake_preview_requires_contract_source(tmp_path) -> None:
    result_path = tmp_path / "result.json"
    result_path.write_text(json.dumps({"summary": "No contract"}), encoding="utf-8")
    out = io.StringIO()

    code = main(["result-intake", "preview", str(result_path)], stdout=out)
    body = json.loads(out.getvalue())

    assert code == 2
    assert body["success"] is False
    assert body["data"]["errors"][0]["code"] == "result_contract_required"


def test_flow_cli_result_intake_preview_treats_payload_workflow_id_as_result_data(tmp_path) -> None:
    workflow_path = tmp_path / "intake-workflow.json"
    result_path = tmp_path / "result-with-workflow-id.json"
    workflow_path.write_text(
        json.dumps(
            {
                "workflow_id": "cli-intake-context",
                "nodes": [
                    {
                        "workflow_node_id": "wf-ref-scan",
                        "capability": {
                            "capability_id": "nanobot.ref_scan",
                            "kind": "nanobot_task",
                            "nanobot_task_type": "ref_scan",
                            "plan_step_compatible": True,
                            "result_destinations": ["stage_to_intent_workspace"],
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    result_path.write_text(
        json.dumps(
            {
                "workflow_id": "external-source-workflow",
                "summary": "Ref scan finished",
                "api_token": "payload-workflow-secret",
            }
        ),
        encoding="utf-8",
    )
    out = io.StringIO()

    code = main(
        [
            "result-intake",
            "preview",
            str(result_path),
            "--workflow",
            str(workflow_path),
            "--workflow-node-id",
            "wf-ref-scan",
        ],
        stdout=out,
    )
    body = json.loads(out.getvalue())

    assert code == 0
    assert body["success"] is True
    assert body["data"]["workflow_id"] == "cli-intake-context"
    assert body["data"]["route_count"] == 1
    assert body["data"]["recorded"] is False
    assert "payload-workflow-secret" not in out.getvalue()


def test_flow_cli_table_output_includes_runtime_workflow_ids_and_errors(tmp_path) -> None:
    workflow_path = tmp_path / "table-workflow.json"
    result_path = tmp_path / "table-result.json"
    bad_workflow_path = tmp_path / "bad-table-workflow.json"
    workflow_path.write_text(
        json.dumps(
            {
                "workflow_id": "cli-table",
                "nodes": [
                    {
                        "workflow_node_id": "wf-ref-scan",
                        "capability": {
                            "capability_id": "nanobot.ref_scan",
                            "kind": "nanobot_task",
                            "nanobot_task_type": "ref_scan",
                            "plan_step_compatible": True,
                            "result_destinations": ["stage_to_intent_workspace"],
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    bad_workflow_path.write_text(
        json.dumps(
            {
                "workflow_id": "cli-table-bad",
                "nodes": [{"workflow_node_id": "wf-view", "capability": {"capability_id": "view.only"}}],
            }
        ),
        encoding="utf-8",
    )
    result_path.write_text(json.dumps({"summary": "done"}), encoding="utf-8")

    plan_out = io.StringIO()
    run_out = io.StringIO()
    intake_out = io.StringIO()
    bad_out = io.StringIO()

    plan_code = main(["workflow", "plan-draft", str(workflow_path), "--output", "table"], stdout=plan_out)
    run_code = main(["workflow", "run", str(workflow_path), "--output", "table"], stdout=run_out)
    intake_code = main(
        [
            "result-intake",
            "preview",
            str(result_path),
            "--workflow",
            str(workflow_path),
            "--workflow-node-id",
            "wf-ref-scan",
            "--output",
            "table",
        ],
        stdout=intake_out,
    )
    bad_code = main(["workflow", "plan-draft", str(bad_workflow_path), "--output", "table"], stdout=bad_out)

    assert plan_code == 0
    assert run_code == 0
    assert intake_code == 0
    assert bad_code == 2
    assert "workflow_id\tcli-table" in plan_out.getvalue()
    assert "workflow_id\tcli-table" in run_out.getvalue()
    assert "workflow_id\tcli-table" in intake_out.getvalue()
    assert "error\tno_plan_compatible_workflow_nodes\tno_plan_compatible_workflow_nodes" in bad_out.getvalue()
