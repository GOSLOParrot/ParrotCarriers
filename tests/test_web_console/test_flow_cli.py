from __future__ import annotations

import io
import json

from parrot.web_console.flow_cli import main


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
