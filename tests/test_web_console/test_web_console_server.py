from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from importlib import import_module
from types import SimpleNamespace
from typing import Any

from fastapi.testclient import TestClient

from parrot.web_console.server import OrchestratorProxyConfig, _status_summary, build_app


def test_console_config_uses_env_without_leaking_secret(monkeypatch) -> None:
    monkeypatch.setenv("PARROT_WEB_CONSOLE_ORCH_URL", "http://127.0.0.1:9876/")
    monkeypatch.setenv("PARROT_ORCH_SECRET", "secret-value")
    monkeypatch.setenv("PARROT_WEB_CONSOLE_REFRESH_S", "9")

    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    body = client.get("/api/console/config").json()

    assert body["orchestrator_base_url"] == "http://127.0.0.1:9876"
    assert body["orchestrator_auth_mode"] == "bearer"
    assert body["refresh_interval_s"] == 9.0
    assert "secret-value" not in str(body)


def test_orchestrator_status_proxy_calls_fetcher(monkeypatch) -> None:
    monkeypatch.setenv("PARROT_ORCH_PORT", "8123")
    monkeypatch.delenv("PARROT_WEB_CONSOLE_ORCH_URL", raising=False)
    monkeypatch.delenv("PARROT_ORCH_SECRET", raising=False)

    async def fetcher(config: OrchestratorProxyConfig) -> dict[str, Any]:
        assert config.base_url == "http://127.0.0.1:8123"
        assert config.auth_mode == "dev-open"
        return {
            "ok": True,
            "state": "connected",
            "upstream": {
                "url": config.status_url,
                "status_code": 200,
                "auth_mode": config.auth_mode,
                "fetched_at": 1.0,
            },
            "summary": {"online_processes": 1, "offline_processes": 0},
            "status": {"schema_version": 1, "processes": []},
            "detail": {},
        }

    client = TestClient(build_app(status_fetcher=fetcher))
    body = client.get("/api/orchestrator/status").json()

    assert body["ok"] is True
    assert body["upstream"]["url"] == "http://127.0.0.1:8123/status"


def test_index_serves_static_console() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    response = client.get("/")

    assert response.status_code == 200
    assert "Parrot Web Console" in response.text
    app_asset_match = re.search(r'src="(?P<asset>/assets/app\.js)"', response.text)
    style_asset_match = re.search(r'href="(?P<asset>/assets/styles\.css)"', response.text)
    assert app_asset_match is not None
    assert style_asset_match is not None
    assert response.headers["Cache-Control"] == "no-store"

    asset = client.get(app_asset_match.group("asset"))
    assert asset.status_code == 200
    assert asset.headers["Cache-Control"] == "no-store"
    style_asset = client.get(style_asset_match.group("asset"))
    assert style_asset.status_code == 200
    assert style_asset.headers["Cache-Control"] == "no-store"

    fallback = client.get("/memory")
    assert fallback.status_code == 200
    assert "Parrot Web Console" in fallback.text
    assert fallback.headers["Cache-Control"] == "no-store"


def test_app_canvas_and_lineb_facade_routes_are_exposed() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher, app_facade_factory=_FakeAppFacade))

    canvas = client.get("/api/app/canvas").json()
    modules = client.get("/api/app/modules").json()
    profiles = client.get("/api/app/line-profiles").json()
    route = client.post("/api/app/lineb/audio-route", json={}).json()
    mic = client.post(
        "/api/app/lineb/mic-input",
        json={"asr_text": "hello LineB", "echo_score": "0.1"},
    ).json()

    assert canvas["active_workspace_id"] == "workdesk"
    assert modules[0]["module_id"] == "voice_pipeline"
    assert profiles[0]["line_profile_id"] == "lineb_google_default"
    assert route["source"] == "web_console.lineb_voice"
    assert mic["turn_decision"] == "user_turn"


def test_livekit_web_token_mints_without_exposing_api_secret(monkeypatch) -> None:
    monkeypatch.setenv("LIVEKIT_URL", "ws://127.0.0.1:7880")
    monkeypatch.setenv("LIVEKIT_API_KEY", "devkey")
    monkeypatch.setenv("LIVEKIT_API_SECRET", "very-secret-livekit-api-secret-with-length")
    monkeypatch.setenv("PARROT_WEB_CONSOLE_LIVEKIT_TOKEN_TTL_S", "60")

    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    config = client.get("/api/livekit/config").json()
    token = client.post(
        "/api/livekit/web-token",
        json={"room": "parrot-test", "identity": "web-console-test"},
    ).json()

    assert config["url"] == "ws://127.0.0.1:7880"
    assert config["room"] == "parrot-main"
    assert "very-secret-livekit-api-secret" not in str(config)
    assert token["url"] == "ws://127.0.0.1:7880"
    assert token["room"] == "parrot-test"
    assert token["identity"] == "web-console-test"
    assert token["token"]
    assert "very-secret-livekit-api-secret" not in str(token)


def test_runtime_capability_catalog_indexes_real_workbench_routes() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    body = client.get("/api/runtime/capabilities/catalog").json()
    by_id = {row["capability_id"]: row for row in body["capabilities"]}

    assert body["action"] == "runtime.capabilities.catalog"
    assert body["success"] is True
    assert body["audit"]["web_only"] is True
    assert {row["id"] for row in body["interaction_modes"]} == {"L0", "L1", "L2", "C3", "C4", "I0"}
    assert body["groups"]["interaction_mode"]
    assert by_id["runtime.flow.snapshot"]["route"] == "/api/runtime/flow"
    assert "L0" in by_id["runtime.flow.snapshot"]["interaction_modes"]
    assert by_id["runtime.workflow.result_contract"]["route"] == "/api/runtime/workflow/result-contract"
    assert by_id["runtime.workflow.result_contract"]["execution_policy"] == "draft_only"
    assert "L2" in by_id["runtime.workflow.result_contract"]["interaction_modes"]
    assert by_id["runtime.workflow.validate"]["route"] == "/api/runtime/workflow/validate"
    assert by_id["runtime.workflow.export"]["route"] == "/api/runtime/workflow/export"
    assert by_id["runtime.workflow.import_preview"]["route"] == "/api/runtime/workflow/import-preview"
    assert by_id["runtime.workflow.action_gates"]["route"] == "/api/runtime/workflow/action-gates"
    assert by_id["runtime.workflow.action_gates"]["kind"] == "hitl_gate"
    assert by_id["graphiti.subgraph.search"]["true_connection"]["state"] == "ecs_proxy"
    assert "C3" in by_id["graphiti.subgraph.search"]["interaction_modes"]
    assert by_id["graphiti.materialize_l2b"]["execution_policy"] == "operator_gated"
    assert "L1" in by_id["graphiti.materialize_l2b"]["interaction_modes"]
    assert by_id["l2b.subgraph.context"]["execution_policy"] == "read_only"
    assert by_id["refs.ref_scan.dispatch"]["nanobot_task_type"] == "ref_scan"
    assert by_id["nanobot.calendar_fetch"]["plan_step_compatible"] is True

    trigger_rows = [row for row in body["capabilities"] if row["kind"] == "trigger"]
    assert trigger_rows
    assert any(row["route"] == "/api/dsg/triggers/fire-event" for row in trigger_rows)
    assert any(row["sample_payload"].get("trigger_name") for row in trigger_rows)

    filtered = client.get("/api/runtime/capabilities/catalog?q=graphiti&kind=graphiti_search").json()
    assert filtered["capabilities"]
    assert all(row["kind"] == "graphiti_search" for row in filtered["capabilities"])
    assert all("graphiti" in str(row).lower() for row in filtered["capabilities"])

    c3 = client.get("/api/runtime/capabilities/catalog?interaction_mode=C3").json()
    assert c3["capabilities"]
    assert all("C3" in row["interaction_modes"] for row in c3["capabilities"])


def test_runtime_workflow_plan_draft_imports_nanobot_capabilities_to_hitl() -> None:
    from parrot.brain.intent_workspace import IntentWorkspace, set_intent_workspace_for_test
    from parrot.brain.plan import PlanRegistry, PlanState, set_plan_registry_for_test

    set_intent_workspace_for_test(IntentWorkspace())
    registry = PlanRegistry(dispatch_task=_fake_plan_dispatch)
    set_plan_registry_for_test(registry)
    try:
        client = TestClient(build_app(status_fetcher=_fake_fetcher))
        workflow_nodes = [
            {
                "workflow_node_id": "wf-ref-scan",
                "capability": {
                    "capability_id": "nanobot.ref_scan",
                    "title": "Ref scan",
                    "route": "/api/memory/identity-ref-index/ref-scan-dispatch",
                    "execution_policy": "nanobot_dispatch",
                    "plan_step_compatible": True,
                    "nanobot_task_type": "ref_scan",
                    "result_destinations": ["stage_to_intent_workspace"],
                },
            },
            {
                "workflow_node_id": "wf-trigger",
                "capability": {
                    "capability_id": "trigger.intent_event_boundary",
                    "title": "Trigger boundary",
                    "plan_step_compatible": False,
                },
            },
        ]

        preview = client.post(
            "/api/runtime/workflow/plan-draft",
            json={"title": "Workbench plan", "workflow_nodes": workflow_nodes, "dry_run": True},
        ).json()
        result_contract = client.post(
            "/api/runtime/workflow/result-contract",
            json={"title": "Workbench plan", "workflow_nodes": workflow_nodes},
        ).json()
        nested_preview = client.post(
            "/api/runtime/workflow/plan-draft",
            json={
                "workflow": {
                    "workflow_id": "nested-workbench-plan",
                    "title": "Nested workbench plan",
                    "nodes": workflow_nodes,
                },
                "dry_run": True,
            },
        ).json()
        applied = client.post(
            "/api/runtime/workflow/plan-draft",
            json={
                "title": "Workbench plan",
                "workflow_nodes": workflow_nodes,
                "dry_run": False,
                "operator_mode": True,
            },
        ).json()
        pending = client.get("/api/runtime/hitl/pending").json()

        assert preview["action"] == "runtime.workflow.plan_draft"
        assert preview["success"] is True
        assert preview["data"]["compatible_step_count"] == 1
        assert preview["data"]["steps"][0]["expected_tool"] == "ref_scan"
        assert preview["data"]["steps"][0]["inputs"]["result_contract_version"] == "workflow_result_contract_v1"
        assert preview["data"]["steps"][0]["inputs"]["result_routes"][0]["destination"] == "stage_to_intent_workspace"
        assert preview["data"]["result_contract"]["schema"] == "workflow_result_contract_v1"
        assert preview["data"]["skipped_nodes"][0]["reason"] == "not_nanobot_plan_compatible"
        assert result_contract["action"] == "runtime.workflow.result_contract"
        assert result_contract["success"] is True
        assert result_contract["data"]["result_contract"]["destination_counts"]["stage_to_intent_workspace"] == 1
        assert result_contract["data"]["result_contract"]["execution_model"]["scheduler_enforced"] is False
        assert nested_preview["success"] is True
        assert nested_preview["data"]["title"] == "Nested workbench plan"
        assert nested_preview["data"]["source_workflow_id"] == "nested-workbench-plan"
        assert nested_preview["data"]["result_contract"]["workflow_id"] == "nested-workbench-plan"
        assert nested_preview["data"]["workflow_node_count"] == 2
        assert applied["success"] is True
        assert applied["dry_run"] is False
        plan_id = applied["data"]["created_plan_id"]
        assert registry.get(plan_id).state == PlanState.AWAITING_USER_CONFIRMATION
        assert applied["data"]["pending_gate_id"] == f"plan:{plan_id}"
        assert any(gate["gate_id"] == f"plan:{plan_id}" for gate in pending["gates"])
    finally:
        set_plan_registry_for_test(None)
        set_intent_workspace_for_test(None)


def test_runtime_workflow_draft_registry_persists_and_imports_saved_plan(monkeypatch, tmp_path) -> None:
    from parrot.brain.intent_workspace import IntentWorkspace, get_intent_workspace, set_intent_workspace_for_test
    from parrot.brain.plan import PlanRegistry, set_plan_registry_for_test

    monkeypatch.setenv("PARROT_WEB_CONSOLE_WORKFLOW_DRAFTS_PATH", str(tmp_path / "workflow_drafts.json"))
    monkeypatch.setenv("PARROT_WEB_CONSOLE_ACTION_GATES_PATH", str(tmp_path / "workflow_action_gates.json"))
    monkeypatch.setenv("PARROT_WEB_CONSOLE_RESULT_INTAKE_PATH", str(tmp_path / "workflow_result_intake.json"))
    set_intent_workspace_for_test(IntentWorkspace())
    registry = PlanRegistry(dispatch_task=_fake_plan_dispatch)
    set_plan_registry_for_test(registry)
    try:
        client = TestClient(build_app(status_fetcher=_fake_fetcher))
        nodes = [
            {
                "workflow_node_id": "wf-ref-scan",
                "capability": {
                    "capability_id": "nanobot.ref_scan",
                    "title": "Ref scan",
                    "kind": "nanobot_task",
                    "nanobot_task_type": "ref_scan",
                    "plan_step_compatible": True,
                    "result_destinations": ["stage_to_intent_workspace"],
                    "sample_payload": {"api_token": "should-not-persist"},
                },
            },
            {
                "workflow_node_id": "wf-trigger",
                "capability": {
                    "capability_id": "trigger.intent_event_boundary",
                    "title": "Intent boundary",
                    "kind": "trigger",
                    "result_destinations": ["return_to_goslo"],
                },
            },
        ]

        saved = client.post(
            "/api/runtime/workflows/drafts",
            json={
                "workflow_id": "wf-demo",
                "title": "Demo durable workflow",
                "workflow_nodes": nodes,
                "tags": ["demo"],
            },
        ).json()
        listed = client.get("/api/runtime/workflows/drafts?q=demo").json()
        loaded = client.get("/api/runtime/workflows/drafts/wf-demo").json()
        validated = client.post(
            "/api/runtime/workflow/validate",
            json={"workflow": loaded["draft"]},
        ).json()
        exported = client.get("/api/runtime/workflow/export?workflow_id=wf-demo").json()
        import_preview = client.post(
            "/api/runtime/workflow/import-preview",
            json={
                "workflow": exported["data"]["workflow"],
                "target_workflow": {
                    "workflow_id": "wf-target",
                    "title": "Target durable workflow",
                    "nodes": [nodes[0]],
                },
            },
        ).json()
        invalid_validation = client.post(
            "/api/runtime/workflow/validate",
            json={"workflow": {"title": "Bad workflow", "nodes": [{"workflow_node_id": "bad", "capability": {}}]}},
        ).json()
        action_gate = client.post(
            "/api/runtime/workflow/action-gates",
            json={"workflow_id": "wf-demo", "workflow_node_id": "wf-trigger"},
        ).json()
        action_gates = client.get("/api/runtime/workflow/action-gates").json()
        action_gate_preview = client.post(
            "/api/runtime/workflow/action-gates/decision",
            json={"gate_id": action_gate["data"]["gate"]["gate_id"], "decision": "apply", "dry_run": True},
        ).json()
        action_gate_cancel = client.post(
            "/api/runtime/workflow/action-gates/decision",
            json={
                "gate_id": action_gate["data"]["gate"]["gate_id"],
                "decision": "cancel",
                "dry_run": False,
                "operator_mode": True,
            },
        ).json()
        route_contract = client.post(
            "/api/runtime/workflow/result-contract",
            json={"workflow_id": "wf-demo"},
        ).json()
        result_intake = client.post(
            "/api/runtime/workflow/result-intake",
            json={
                "workflow_id": "wf-demo",
                "workflow_node_id": "wf-ref-scan",
                "task_id": "task-demo",
                "result_channel": "memory_ref_scan_result",
                "result_payload": {"summary": "Ref scan complete", "api_token": "hide-me"},
                "dry_run": False,
                "operator_mode": True,
            },
        ).json()
        result_intakes = client.get("/api/runtime/workflow/result-intake").json()
        result_intake_delete = client.delete(
            f"/api/runtime/workflow/result-intake/{result_intake['data']['entry']['entry_id']}",
        ).json()
        result_intakes_after_delete = client.get("/api/runtime/workflow/result-intake").json()
        view_preview = client.post(
            "/api/runtime/workflow/result-intake",
            json={
                "result_contract": {"schema": "workflow_result_contract_v1", "workflow_id": "direct-preview"},
                "result_routes": [{"destination": "view_only", "sink": "web_console.receipt_rail"}],
                "result_payload": {"summary": "Preview-only receipt"},
                "dry_run": True,
            },
        ).json()
        blocked_apply = client.post(
            "/api/runtime/workflow/result-intake",
            json={
                "entry_id": "blocked-graphiti-route",
                "result_contract": {"schema": "workflow_result_contract_v1", "workflow_id": "blocked-demo"},
                "result_routes": [{"destination": "write_graphiti_episode", "sink": "graphiti.episode"}],
                "result_payload": {"summary": "Blocked Graphiti write"},
                "dry_run": False,
                "operator_mode": True,
            },
        ).json()
        preview_plan = client.post(
            "/api/runtime/workflow/plan-draft",
            json={"workflow_id": "wf-demo", "dry_run": True},
        ).json()
        applied_plan = client.post(
            "/api/runtime/workflow/plan-draft",
            json={"workflow_id": "wf-demo", "dry_run": False, "operator_mode": True},
        ).json()
        run_preview = client.post(
            "/api/runtime/workflow/run",
            json={"workflow_id": "wf-demo", "dry_run": True},
        ).json()
        deleted = client.delete("/api/runtime/workflows/drafts/wf-demo").json()
        missing = client.get("/api/runtime/workflows/drafts/wf-demo").json()

        assert saved["action"] == "runtime.workflow_drafts.save"
        assert saved["success"] is True
        assert saved["summary"]["node_count"] == 2
        assert saved["summary"]["trigger_count"] == 1
        assert saved["summary"]["plan_compatible_count"] == 1
        assert listed["count"] == 1
        assert validated["action"] == "runtime.workflow.validate"
        assert validated["success"] is True
        assert validated["data"]["schema"] == "workflow_schema_v1"
        assert exported["action"] == "runtime.workflow.export"
        assert exported["success"] is True
        assert exported["data"]["workflow"]["schema"] == "workflow_schema_v1"
        assert "should-not-persist" not in str(exported)
        assert import_preview["action"] == "runtime.workflow.import_preview"
        assert import_preview["success"] is True
        assert import_preview["data"]["would_save"] is False
        assert import_preview["data"]["diff"]["added_nodes"] == ["wf-trigger"]
        assert import_preview["data"]["diff"]["kept_nodes"] == ["wf-ref-scan"]
        assert invalid_validation["success"] is False
        assert invalid_validation["data"]["errors"][0]["code"] == "capability_missing_identity"
        assert loaded["draft"]["nodes"][0]["capability"]["sample_payload"]["api_token"] == "[REDACTED]"
        assert action_gate["action"] == "runtime.workflow.action_gate.draft"
        assert action_gate["success"] is True
        assert action_gate["data"]["gate"]["action_kind"] == "trigger_event"
        assert action_gates["count"] == 1
        assert action_gate_preview["success"] is True
        assert action_gate_preview["data"]["preview_receipt"]["action"] == "dsg.trigger.draft_event"
        assert action_gate_cancel["success"] is True
        assert action_gate_cancel["data"]["gate"]["state"] == "cancelled"
        assert route_contract["success"] is True
        assert route_contract["data"]["result_contract"]["workflow_id"] == "wf-demo"
        assert route_contract["data"]["result_contract"]["destination_counts"]["return_to_goslo"] == 1
        assert result_intake["success"] is True
        assert result_intake["data"]["recorded"] is True
        assert result_intake["data"]["staged_refs"][0]["role"] == "workflow_result"
        assert result_intake["data"]["route_results"][0]["staged_ref"]["ref_id"]
        assert "hide-me" not in str(result_intake)
        assert result_intakes["count"] == 1
        assert result_intake_delete["success"] is True
        assert result_intake_delete["deleted"] is True
        assert result_intakes_after_delete["count"] == 0
        assert get_intent_workspace().list_by_role("workflow_result")
        assert view_preview["success"] is True
        assert view_preview["data"]["route_results"][0]["intake_state"] == "preview"
        assert view_preview["data"]["route_results"][0]["applied"] is False
        assert view_preview["data"]["recorded"] is False
        assert blocked_apply["success"] is True
        assert blocked_apply["data"]["entry"]["state"] == "blocked"
        assert blocked_apply["data"]["blocked_route_count"] == 1
        assert blocked_apply["data"]["route_results"][0]["intake_state"] == "blocked"
        assert preview_plan["success"] is True
        assert preview_plan["data"]["source_workflow_id"] == "wf-demo"
        assert preview_plan["data"]["steps"][0]["expected_tool"] == "ref_scan"
        assert applied_plan["success"] is True
        assert registry.get(applied_plan["data"]["created_plan_id"]) is not None
        assert run_preview["action"] == "runtime.workflow.run"
        assert run_preview["success"] is True
        assert run_preview["data"]["trigger_node_count"] == 1
        assert run_preview["data"]["plan_compatible_count"] == 1
        assert run_preview["data"]["result_contract"]["schema"] == "workflow_result_contract_v1"
        assert run_preview["data"]["trigger_receipts"][0]["action"] == "dsg.trigger.draft_event"
        assert run_preview["data"]["plan_receipt"]["data"]["steps"][0]["expected_tool"] == "ref_scan"
        assert deleted["deleted"] is True
        assert missing["success"] is False
    finally:
        set_plan_registry_for_test(None)
        set_intent_workspace_for_test(None)


def test_graphiti_status_search_and_dry_run_routes_are_exposed(monkeypatch) -> None:
    from parrot.brain import graphiti_console

    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-status-secret")
    monkeypatch.setenv("GRAPHITI_LLM_PROVIDER", "deepseek")
    monkeypatch.delenv("GRAPHITI_DEEPSEEK_JSON_SCHEMA_ENABLED", raising=False)
    monkeypatch.setenv("GOOGLE_API_KEY", "google-status-secret")
    monkeypatch.setattr(graphiti_console, "_graphiti_core_installed", lambda: False)
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    status = client.get("/api/graphiti/status").json()
    blank_search = client.post("/api/graphiti/search", json={"query": ""}).json()
    missing_search = client.post(
        "/api/graphiti/search",
        json={"query": "blue mug", "partition": "scene"},
    ).json()
    draft = client.post(
        "/api/graphiti/episode/draft",
        json={"name": "web_test", "body": "hello memory", "partition": "maid"},
    ).json()
    dry_run = client.post(
        "/api/graphiti/episode",
        json={"name": "web_test", "body": "hello memory", "partition": "maid", "dry_run": True},
    ).json()

    assert status["action"] == "graphiti_status"
    assert status["success"] is True
    assert status["data"]["partitions"] == [
        "goslo",
        "maid",
        "scene",
        "user",
        "arknights_test",
        "noble_etiquette",
    ]
    assert status["data"]["graphiti_llm"]["requested_provider"] == "deepseek"
    assert status["data"]["graphiti_llm"]["provider"] == "gemini"
    assert status["data"]["graphiti_llm"]["model"] == "gemini-2.5-flash"
    assert (
        status["data"]["graphiti_llm"]["fallback_reason"]
        == "deepseek_json_schema_response_format_disabled"
    )
    assert status["data"]["graphiti_llm"]["secret_configured"] is True
    assert "deepseek-status-secret" not in str(status)
    assert "google-status-secret" not in str(status)
    assert blank_search["success"] is False
    assert blank_search["message"] == "query is required"
    assert missing_search["success"] is False
    assert missing_search["available"] is False
    assert missing_search["message"] == "graphiti-core optional extra not installed"
    assert "pip install" not in str(missing_search)
    assert draft["action"] == "draft_episode"
    assert draft["data"]["draft"]["group_id"] == "maid"
    assert dry_run["action"] == "add_episode"
    assert dry_run["success"] is True
    assert "dry_run=true" in dry_run["message"]


def test_graphiti_deepseek_provider_requires_json_schema_opt_in(monkeypatch) -> None:
    from parrot.memory.graphiti_client import __all__, get_llm_clients, graphiti_provider_status
    from parrot.shared.config import ParrotConfig

    assert "get_llm_clients" in __all__

    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-status-secret")
    monkeypatch.setenv("GOOGLE_API_KEY", "google-status-secret")
    monkeypatch.setenv("GRAPHITI_LLM_PROVIDER", "deepseek")
    monkeypatch.delenv("GRAPHITI_DEEPSEEK_JSON_SCHEMA_ENABLED", raising=False)

    safe_default = graphiti_provider_status(ParrotConfig())

    assert safe_default["requested_provider"] == "deepseek"
    assert safe_default["provider"] == "gemini"
    assert safe_default["fallback_reason"] == "deepseek_json_schema_response_format_disabled"
    assert "deepseek-status-secret" not in str(safe_default)
    assert "google-status-secret" not in str(safe_default)

    monkeypatch.setenv("GRAPHITI_DEEPSEEK_JSON_SCHEMA_ENABLED", "1")

    opt_in = graphiti_provider_status(ParrotConfig())

    assert opt_in["requested_provider"] == "deepseek"
    assert opt_in["provider"] == "deepseek"
    assert opt_in["model"] == "deepseek-v4-pro"
    assert "fallback_reason" not in opt_in
    assert "deepseek-status-secret" not in str(opt_in)
    assert callable(get_llm_clients)


def test_graphiti_subgraph_export_routes_are_l15_dry_run_and_secret_safe(monkeypatch) -> None:
    from parrot.brain import graphiti_console

    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-export-secret")
    monkeypatch.setattr(graphiti_console, "_graphiti_core_installed", lambda: False)
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    missing_search = client.post(
        "/api/graphiti/subgraph/search",
        json={"query": "Amiya Chernobog", "partition": "arknights_test", "limit": 3},
    ).json()
    bad_limit_search = client.post(
        "/api/graphiti/subgraph/search",
        json={"query": "Amiya Chernobog", "partition": "arknights_test", "limit": "bad"},
    ).json()
    bad_limit_plain_search = client.post(
        "/api/graphiti/search",
        json={"query": "Amiya Chernobog", "partition": "arknights_test", "limit": "bad"},
    ).json()
    hit = {
        "text": "Amiya's field role changes during the Chernobog crisis.",
        "uuid": "graphiti-hit-1",
        "source_node_uuid": "source-amiya",
        "target_node_uuid": "target-chernobog",
        "episode_uuids": ["episode-main-00"],
        "labels": ["Entity", "CrisisFact"],
        "valid_at": "1096-12-23T00:00:00Z",
        "custom_payload": {"node_kind": "operator", "rarity": 5},
        "score": 0.91,
        "source_url": "https://prts.wiki/w/%E5%89%A7%E6%83%85%E4%B8%80%E8%A7%88",
        "source_description": "arknights_test:main_00_01",
    }
    draft = client.post(
        "/api/graphiti/subgraph/export-draft",
        json={"partition": "arknights_test", "query": "Amiya", "hits": [hit]},
    ).json()
    export = client.post(
        "/api/graphiti/subgraph/export",
        json={
            "partition": "arknights_test",
            "query": "Amiya",
            "hits": [hit],
            "dry_run": True,
            "operator_mode": False,
        },
    ).json()

    assert missing_search["action"] == "graphiti.subgraph.search"
    assert missing_search["success"] is False
    assert missing_search["data"]["subgraph"]["partition"] == "arknights_test"
    assert bad_limit_search["action"] == "graphiti.subgraph.search"
    assert bad_limit_search["data"]["subgraph"]["partition"] == "arknights_test"
    assert bad_limit_plain_search["action"] == "search_graphiti"
    assert bad_limit_plain_search["message"] == "graphiti-core optional extra not installed"
    assert draft["action"] == "graphiti.subgraph.export_draft"
    assert draft["success"] is True
    assert draft["data"]["write_path"] == "L15Pool.admit(Observation(source=USER_EXPLICIT))"
    observation = draft["data"]["observations"][0]
    assert observation["graphiti_uuid"] == "graphiti-hit-1"
    assert observation["meta"]["graphiti_partition"] == "arknights_test"
    assert observation["meta"]["graphiti_source_node_uuid"] == "source-amiya"
    assert observation["meta"]["source_description"] == "arknights_test:main_00_01"
    assert observation["meta"]["graphiti_raw"]["raw"]["labels"] == ["Entity", "CrisisFact"]
    assert observation["meta"]["graphiti_raw"]["raw"]["custom_payload"]["rarity"] == 5
    assert draft["data"]["subgraph"]["partition"] == "arknights_test"
    assert draft["data"]["graphiti_raw_envelopes"][0]["episode_uuids"] == ["episode-main-00"]
    assert draft["data"]["graphiti_raw_envelopes"][0]["raw"]["valid_at"] == "1096-12-23T00:00:00Z"
    bundle = draft["data"]["graphiti_bundle"]
    assert bundle["schema_version"] == 1
    assert bundle["bundle_kind"] == "graphiti_search_subgraph_bundle"
    assert bundle["selection"]["fact_uuids"] == ["graphiti-hit-1"]
    assert bundle["selection"]["node_uuids"] == ["source-amiya", "target-chernobog"]
    assert bundle["selection"]["episode_uuids"] == ["episode-main-00"]
    assert bundle["sections"]["facts"][0]["raw"]["custom_payload"]["rarity"] == 5
    assert bundle["sections"]["entities"][0]["uuid"] == "source-amiya"
    assert bundle["sections"]["episodes"][0]["raw"]["pointer_only"] is True
    assert bundle["l2b_projection_policy"]["preserve_raw_graphiti"] is True
    assert bundle["l2b_projection_policy"]["direct_falkordb_write"] is False
    identity_ref_drafts = draft["data"]["identity_ref_drafts"]
    assert {
        row.get("ref_kind")
        for row in identity_ref_drafts
    } == {"graphiti_fact", "graphiti_entity", "graphiti_episode"}
    assert identity_ref_drafts[0]["graphiti_edge_uuid"] == "graphiti-hit-1"
    assert identity_ref_drafts[0]["graphiti_raw"]["raw"]["labels"] == ["Entity", "CrisisFact"]
    assert identity_ref_drafts[1]["graphiti_entity_uuid"] == "source-amiya"
    assert identity_ref_drafts[1]["graphiti_raw"]["parent_fact"]["uuid"] == "graphiti-hit-1"
    assert draft["data"]["edge_drafts"][0]["source_graphiti_uuid"] == "source-amiya"
    assert draft["data"]["edge_drafts"][0]["target_graphiti_uuid"] == "target-chernobog"
    assert draft["data"]["edge_drafts"][0]["meta"]["graphiti_raw"]["raw"]["custom_payload"]["node_kind"] == "operator"
    assert draft["data"]["edge_drafts"][0]["write_policy"] == "requires_resolved_l2b_node_uuid"
    assert draft["data"]["identity_ref_write_policy"].startswith("Preview only")
    assert "resolved L2-B node UUIDs" in draft["data"]["edge_write_policy"]
    assert export["action"] == "graphiti.subgraph.export"
    assert export["data"]["would_apply"] is True
    assert export["data"]["apply_skipped_reason"] == "dry_run_or_operator_mode_missing"
    assert export["audit"]["direct_falkordb_write"] is False
    assert "deepseek-export-secret" not in str(missing_search) + str(draft) + str(export)


def test_graphiti_subgraph_search_expands_real_search_hops(monkeypatch) -> None:
    from parrot.brain import graphiti_console
    from parrot.brain.graphiti_console import GraphitiConsoleResult

    calls: list[dict[str, Any]] = []

    async def fake_search_graphiti(**kwargs: Any) -> GraphitiConsoleResult:
        calls.append(dict(kwargs))
        query = str(kwargs.get("query") or "")
        if query == "Amiya Chernobog":
            rows = [
                {
                    "text": "Amiya leads Rhodes Island out of Chernobog.",
                    "uuid": "fact-base-1",
                    "source_node_uuid": "node-amiya",
                    "target_node_uuid": "node-rhodes",
                    "graphiti_raw": {
                        "uuid": "fact-base-1",
                        "fact": "Amiya leads Rhodes Island out of Chernobog.",
                        "source_node": {"uuid": "node-amiya", "name": "Amiya"},
                        "target_node": {"uuid": "node-rhodes", "name": "Rhodes Island"},
                    },
                }
            ]
        elif query == "Amiya Rhodes Island":
            rows = [
                {
                    "text": "Rhodes Island evacuates Chernobog under Amiya's command.",
                    "uuid": "fact-hop-2",
                    "source_node_uuid": "node-rhodes",
                    "target_node_uuid": "node-chernobog",
                    "graphiti_raw": {
                        "uuid": "fact-hop-2",
                        "fact": "Rhodes Island evacuates Chernobog under Amiya's command.",
                        "source_node": {"uuid": "node-rhodes", "name": "Rhodes Island"},
                        "target_node": {"uuid": "node-chernobog", "name": "Chernobog"},
                    },
                }
            ]
        else:
            rows = []
        return GraphitiConsoleResult(
            action="search_graphiti",
            success=True,
            available=True,
            message=f"{len(rows)} result(s)",
            data={
                "query": query,
                "partition": str(kwargs.get("partition") or "arknights_test"),
                "limit": int(kwargs.get("limit") or 6),
                "results": rows,
            },
        )

    monkeypatch.setattr(graphiti_console, "search_graphiti", fake_search_graphiti)
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    body = client.post(
        "/api/graphiti/subgraph/search",
        json={
            "query": "Amiya Chernobog",
            "partition": "arknights_test",
            "limit": 6,
            "strategy": "iterative_hybrid",
            "depth": 2,
        },
    ).json()

    assert body["success"] is True
    assert [call["query"] for call in calls][:2] == ["Amiya Chernobog", "Amiya Rhodes Island"]
    assert body["data"]["strategy"] == "iterative_hybrid"
    assert body["data"]["depth"] == 2
    assert [row["uuid"] for row in body["data"]["hits"]] == ["fact-base-1", "fact-hop-2"]
    assert body["data"]["hits"][1]["search_context"]["depth"] == 2
    assert body["data"]["subgraph"]["nodes"][0]["graphiti_raw"]["uuid"] == "fact-base-1"
    assert body["data"]["search_plan"][1]["query"] == "Amiya Rhodes Island"


def test_graphiti_subgraph_search_uses_search_config_recipe_and_filters(monkeypatch) -> None:
    from parrot.brain import graphiti_console
    from parrot.memory import graphiti_client

    calls: list[dict[str, Any]] = []

    class FakeConfig:
        def __init__(self) -> None:
            self.limit = 0

        def model_copy(self, deep: bool = True) -> "FakeConfig":
            assert deep is True
            return FakeConfig()

    class FakeGraphiti:
        async def _search(self, **kwargs: Any) -> SimpleNamespace:
            calls.append(dict(kwargs))
            return SimpleNamespace(
                edges=[
                    SimpleNamespace(
                        uuid="fact-rrf-1",
                        fact="Amiya protects Chernobog civilians.",
                        source_node_uuid="node-amiya-rrf",
                        target_node_uuid="node-chernobog-rrf",
                        score=0.92,
                    )
                ],
                nodes=[
                    SimpleNamespace(
                        uuid="node-amiya-rrf",
                        name="Amiya",
                        summary="Rhodes Island operator.",
                        score=0.71,
                    )
                ],
                communities=[],
            )

    async def fake_get_graphiti() -> FakeGraphiti:
        return FakeGraphiti()

    monkeypatch.setattr(graphiti_console, "_graphiti_core_installed", lambda: True)
    monkeypatch.setattr(graphiti_console, "_load_search_config_recipe", lambda recipe: FakeConfig())
    monkeypatch.setattr(
        graphiti_console,
        "_build_graphiti_search_filter",
        lambda **kwargs: {
            "node_labels": list(kwargs["node_labels"]),
            "edge_types": list(kwargs["edge_types"]),
        },
    )
    monkeypatch.setattr(graphiti_client, "get_graphiti", fake_get_graphiti)
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    body = client.post(
        "/api/graphiti/subgraph/search",
        json={
            "query": "Amiya Chernobog",
            "partition": "arknights_test",
            "limit": 4,
            "strategy": "combined_rrf",
            "search_recipe": "combined_rrf",
            "node_labels": ["Entity", "Operator"],
            "edge_types": ["CrisisFact"],
            "enrich": False,
        },
    ).json()

    assert body["success"] is True
    assert calls
    assert calls[0]["query"] == "Amiya Chernobog"
    assert calls[0]["group_id"] == "arknights_test"
    assert calls[0]["config"].limit == 4
    assert calls[0]["search_filter"] == {
        "node_labels": ["Entity", "Operator"],
        "edge_types": ["CrisisFact"],
    }
    assert body["data"]["strategy"] == "combined_rrf"
    assert body["data"]["search_recipe"] == "combined_rrf"
    assert body["data"]["node_labels"] == ["Entity", "Operator"]
    assert body["data"]["edge_types"] == ["CrisisFact"]
    assert body["data"]["search_plan"][0]["search_config"]["mode"] == "_search"
    assert body["data"]["search_plan"][0]["search_config"]["recipe"] == "COMBINED_HYBRID_SEARCH_RRF"
    assert body["data"]["search_plan"][0]["search_config"]["low_level_method"] == "_search"
    assert body["data"]["hits"][0]["graphiti_kind"] == "edge"
    assert body["data"]["graphiti_bundle"]["search"]["search_recipe"] == "combined_rrf"
    assert body["data"]["graphiti_bundle"]["search"]["node_labels"] == ["Entity", "Operator"]
    assert body["data"]["graphiti_bundle"]["selection"]["fact_uuids"] == ["fact-rrf-1"]
    nodes = {row["graphiti_uuid"]: row for row in body["data"]["subgraph"]["nodes"]}
    assert nodes["fact-rrf-1"]["kind"] == "graphiti_fact"
    assert nodes["node-amiya-rrf"]["kind"] == "graphiti_entity"


def test_graphiti_subgraph_search_enriches_hits_with_uuid_lookup(monkeypatch) -> None:
    from parrot.brain import graphiti_console
    from parrot.brain.graphiti_console import GraphitiConsoleResult

    async def fake_search_graphiti(**kwargs: Any) -> GraphitiConsoleResult:
        rows = [
            {
                "text": "Amiya works with Rhodes Island.",
                "uuid": "fact-rich-1",
                "source_node_uuid": "node-amiya-rich",
                "target_node_uuid": "node-rhodes-rich",
            }
        ]
        return GraphitiConsoleResult(
            action="search_graphiti",
            success=True,
            available=True,
            message="1 result(s)",
            data={
                "query": str(kwargs.get("query") or ""),
                "partition": "arknights_test",
                "limit": 1,
                "results": rows,
            },
        )

    async def fake_lookup_graphiti_uuids(**kwargs: Any) -> GraphitiConsoleResult:
        requested = list(kwargs.get("uuids") or [])
        raw_by_uuid = {
            "fact-rich-1": {
                "uuid": "fact-rich-1",
                "fact": "Amiya works with Rhodes Island.",
                "group_id": "arknights_test",
            },
            "node-amiya-rich": {
                "uuid": "node-amiya-rich",
                "name": "Amiya",
                "summary": "Rhodes Island operator.",
                "group_id": "arknights_test",
            },
            "node-rhodes-rich": {
                "uuid": "node-rhodes-rich",
                "name": "Rhodes Island",
                "summary": "Pharmaceutical organization.",
                "group_id": "arknights_test",
            },
        }
        return GraphitiConsoleResult(
            action="graphiti.lookup",
            success=True,
            available=True,
            message="3/3 found",
            data={
                "partition": "arknights_test",
                "results": [
                    {
                        "uuid": item,
                        "found": item in raw_by_uuid,
                        "graphiti_kind": "entity_edge" if item.startswith("fact") else "entity_node",
                        "partition": "arknights_test",
                        "matches_partition": True,
                        "raw": raw_by_uuid.get(item, {}),
                    }
                    for item in requested
                ],
            },
        )

    monkeypatch.setattr(graphiti_console, "search_graphiti", fake_search_graphiti)
    monkeypatch.setattr(graphiti_console, "lookup_graphiti_uuids", fake_lookup_graphiti_uuids)
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    body = client.post(
        "/api/graphiti/subgraph/search",
        json={
            "query": "Amiya Rhodes",
            "partition": "arknights_test",
            "limit": 1,
            "enrich": True,
        },
    ).json()
    hit = body["data"]["hits"][0]
    nodes = {row["graphiti_uuid"]: row for row in body["data"]["subgraph"]["nodes"]}

    assert body["success"] is True
    assert body["data"]["graphiti_lookup"]["found_count"] == 3
    assert hit["graphiti_lookup"]["fact"]["raw"]["fact"] == "Amiya works with Rhodes Island."
    assert hit["graphiti_raw"]["lookup"]["source_node"]["raw"]["name"] == "Amiya"
    bundle = body["data"]["graphiti_bundle"]
    assert bundle["sections"]["facts"][0]["raw"]["lookup"]["fact"]["raw"]["uuid"] == "fact-rich-1"
    entities = {row["uuid"]: row for row in bundle["sections"]["entities"]}
    assert entities["node-amiya-rich"]["raw"]["name"] == "Amiya"
    assert entities["node-rhodes-rich"]["raw"]["name"] == "Rhodes Island"
    assert bundle["search"]["lookup"]["found_count"] == 3
    assert bundle["l2b_projection_policy"]["edge_materialization_policy"] == "requires_resolved_l2b_node_uuid"
    assert nodes["node-amiya-rich"]["label"] == "Amiya"
    assert nodes["node-rhodes-rich"]["graphiti_raw"]["summary"] == "Pharmaceutical organization."


def test_graphiti_lookup_route_returns_lookup_receipt(monkeypatch) -> None:
    from parrot.brain import graphiti_console
    from parrot.brain.graphiti_console import GraphitiConsoleResult

    async def fake_lookup_graphiti_uuids(**kwargs: Any) -> GraphitiConsoleResult:
        return GraphitiConsoleResult(
            action="graphiti.lookup",
            success=True,
            available=True,
            message="1/1 found",
            data={
                "partition": str(kwargs.get("partition") or ""),
                "results": [
                    {
                        "uuid": str(kwargs.get("uuid") or ""),
                        "found": True,
                        "graphiti_kind": "entity_node",
                        "raw": {"uuid": str(kwargs.get("uuid") or ""), "name": "Amiya"},
                    }
                ],
            },
        )

    monkeypatch.setattr(graphiti_console, "lookup_graphiti_uuids", fake_lookup_graphiti_uuids)
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    body = client.post(
        "/api/graphiti/lookup",
        json={"uuid": "node-amiya-rich", "partition": "arknights_test"},
    ).json()

    assert body["action"] == "graphiti.lookup"
    assert body["success"] is True
    assert body["data"]["results"][0]["raw"]["name"] == "Amiya"


def test_graphiti_add_episode_proxies_to_remote_when_extra_missing(monkeypatch) -> None:
    import asyncio

    from parrot.brain import graphiti_console

    calls: list[tuple[str, dict[str, Any] | None]] = []

    def fake_remote(path: str, *, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        calls.append((path, payload))
        return {
            "success": True,
            "available": True,
            "message": "episode written",
            "data": {"episode": {"name": payload["name"] if payload else ""}},
        }

    monkeypatch.setenv("PARROT_WEB_CONSOLE_GRAPHITI_URL", "http://ecs-graphiti")
    monkeypatch.setattr(graphiti_console, "_graphiti_core_installed", lambda: False)
    monkeypatch.setattr(graphiti_console, "_remote_graphiti_request", fake_remote)

    result = asyncio.run(graphiti_console.add_episode(
        name="remote_episode",
        body="Amiya works with Rhodes Island.",
        partition="arknights_test",
        source_description="web-console-test",
        dry_run=False,
    ))

    assert result.success is True
    assert result.message.startswith("remote:")
    assert calls[0][0] == "/api/graphiti/episode"
    assert calls[0][1]["dry_run"] is False
    assert result.data["remote_proxy"]["base_url"] == "http://ecs-graphiti"


def test_graphiti_execute_export_proxies_when_remote_url_configured(monkeypatch) -> None:
    import asyncio

    from parrot.brain import graphiti_console

    calls: list[tuple[str, dict[str, Any] | None]] = []

    def fake_remote(path: str, *, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        calls.append((path, payload))
        return {
            "action": "graphiti.subgraph.export",
            "success": True,
            "dry_run": False,
            "operator_mode": True,
            "data": {"selected_count": 1, "admit_outcome": {"rejected": []}},
        }

    monkeypatch.setenv("PARROT_WEB_CONSOLE_GRAPHITI_URL", "http://ecs-graphiti")
    monkeypatch.setattr(graphiti_console, "_remote_graphiti_request", fake_remote)

    receipt = asyncio.run(graphiti_console.export_graphiti_subgraph({
        "partition": "arknights_test",
        "query": "Amiya",
        "hits": [{"uuid": "fact-1", "text": "Amiya works with Rhodes Island."}],
        "dry_run": False,
        "operator_mode": True,
    }))

    assert receipt["success"] is True
    assert calls[0][0] == "/api/graphiti/subgraph/export"
    assert calls[0][1]["_remote_proxy_disable"] is True
    assert receipt["data"]["remote_proxy"]["enabled"] is True


def test_graphiti_search_falls_back_to_partition_fact_scan(monkeypatch) -> None:
    import asyncio

    from parrot.brain import graphiti_console
    from parrot.memory import graphiti_client

    class FakeDriver:
        def with_database(self, database: str) -> "FakeDriver":
            assert database == "arknights_test"
            return self

        async def execute_query(self, cypher: str, **params: Any) -> tuple[list[dict[str, Any]], list[str], None]:
            assert "MATCH (source)-[edge]->(target)" in cypher
            assert params["partition"] == "arknights_test"
            return (
                [
                    {
                        "uuid": "fact-fallback-1",
                        "group_id": "arknights_test",
                        "name": "PROTECTS",
                        "fact": "Rhodes Island protects Amiya near Chernobog.",
                        "episode_uuids": ["episode-1"],
                        "source_node_uuid": "node-rhodes",
                        "target_node_uuid": "node-amiya",
                        "source_node_name": "Rhodes Island",
                        "target_node_name": "Amiya",
                        "source_labels": ["Entity"],
                        "target_labels": ["Entity"],
                    }
                ],
                [],
                None,
            )

    class FakeGraphiti:
        driver = FakeDriver()

        async def search(self, **kwargs: Any) -> list[Any]:
            return []

    async def fake_get_graphiti() -> FakeGraphiti:
        return FakeGraphiti()

    monkeypatch.setattr(graphiti_console, "_graphiti_core_installed", lambda: True)
    monkeypatch.setattr(graphiti_client, "get_graphiti", fake_get_graphiti)

    result = asyncio.run(graphiti_console.search_graphiti(
        query="Amiya Chernobog",
        partition="arknights_test",
        limit=2,
    ))

    assert result.success is True
    assert result.data["fallback_search"]["strategy"] == "falkordb_partition_fact_scan"
    assert result.data["results"][0]["uuid"] == "fact-fallback-1"
    assert result.data["results"][0]["graphiti_raw"]["source_node"]["name"] == "Rhodes Island"


def test_graphiti_search_falls_back_to_episode_node_scan(monkeypatch) -> None:
    import asyncio

    from parrot.brain import graphiti_console
    from parrot.memory import graphiti_client

    class FakeDriver:
        def with_database(self, database: str) -> "FakeDriver":
            assert database == "noble_etiquette"
            return self

        async def execute_query(self, cypher: str, **params: Any) -> tuple[list[dict[str, Any]], list[str], None]:
            assert params["partition"] == "noble_etiquette"
            if "MATCH (source)-[edge]->(target)" in cypher:
                return ([], [], None)
            assert "MATCH (node)" in cypher
            assert "node.summary IS NOT NULL" in cypher
            return (
                [
                    {
                        "uuid": "episode-noble-1",
                        "group_id": "noble_etiquette",
                        "name": "noble_etiquette_01_greeting_rank",
                        "summary": None,
                        "content": "Original etiquette note. Formal greetings acknowledge relative rank.",
                        "created_at": "2026-05-17T00:00:00Z",
                        "valid_at": None,
                        "invalid_at": None,
                        "labels": ["Episodic"],
                    }
                ],
                [],
                None,
            )

    class FakeGraphiti:
        driver = FakeDriver()

        async def search(self, **kwargs: Any) -> list[Any]:
            return []

    async def fake_get_graphiti() -> FakeGraphiti:
        return FakeGraphiti()

    monkeypatch.setattr(graphiti_console, "_graphiti_core_installed", lambda: True)
    monkeypatch.setattr(graphiti_client, "get_graphiti", fake_get_graphiti)

    result = asyncio.run(graphiti_console.search_graphiti(
        query="etiquette",
        partition="noble_etiquette",
        limit=2,
    ))

    assert result.success is True
    assert result.data["fallback_search"]["strategy"] == "falkordb_partition_node_scan"
    assert result.data["results"][0]["uuid"] == "episode-noble-1"
    assert result.data["results"][0]["graphiti_kind"] == "graphiti_episode"
    assert result.data["results"][0]["graphiti_raw"]["content"].startswith("Original etiquette note")


def test_graphiti_subgraph_import_plan_combines_l15_and_graph_policy(monkeypatch) -> None:
    from parrot.brain import graphiti_console

    monkeypatch.setattr(graphiti_console, "_graphiti_core_installed", lambda: False)
    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    hit = {
        "text": "Amiya's role changes as Rhodes Island leaves Chernobog.",
        "uuid": "graphiti-hit-plan-1",
        "source_node_uuid": "source-amiya",
        "target_node_uuid": "target-rhodes",
        "episode_uuids": ["episode-plan-1"],
        "graphiti_raw": {
            "uuid": "graphiti-hit-plan-1",
            "fact": "Amiya's role changes as Rhodes Island leaves Chernobog.",
            "source_node": {"uuid": "source-amiya", "name": "Amiya"},
            "target_node": {"uuid": "target-rhodes", "name": "Rhodes Island"},
        },
        "score": 0.83,
        "source_url": "https://prts.wiki/w/%E5%89%A7%E6%83%85%E4%B8%80%E8%A7%88",
        "source_description": "arknights_test:main_00",
    }

    plan = client.post(
        "/api/graphiti/subgraph/import-plan",
        json={
            "partition": "arknights_test",
            "query": "Amiya Chernobog",
            "hits": [hit],
            "destination": "isolated_compartment",
            "dry_run": False,
            "operator_mode": True,
        },
    ).json()
    selected_hits_alias = client.post(
        "/api/graphiti/subgraph/import-plan",
        json={
            "partition": "arknights_test",
            "query": "Amiya Chernobog",
            "selected_hits": [hit],
            "destination": "isolated_compartment",
            "dry_run": True,
            "operator_mode": False,
        },
    ).json()

    assert plan["action"] == "graphiti.subgraph.import_plan"
    assert plan["success"] is True
    assert plan["dry_run"] is True
    assert plan["operator_mode"] is False
    assert plan["data"]["requested_execution"] == {
        "dry_run": False,
        "operator_mode": True,
        "ignored_for_plan": True,
    }
    assert plan["data"]["selected_count"] == 1
    assert selected_hits_alias["success"] is True
    assert selected_hits_alias["data"]["selected_count"] == 1
    assert plan["data"]["observations"][0]["graphiti_uuid"] == "graphiti-hit-plan-1"
    assert plan["data"]["graphiti_raw_envelopes"][0]["raw"]["source_node"]["name"] == "Amiya"
    assert plan["data"]["graphiti_bundle"]["sections"]["facts"][0]["raw"]["target_node"]["name"] == "Rhodes Island"
    assert plan["data"]["graphiti_bundle"]["import_overlay"]["destination"] == "isolated_compartment"
    assert plan["data"]["graphiti_bundle"]["import_overlay"]["l15_export_route"] == "/api/graphiti/subgraph/export"
    assert plan["data"]["graphiti_bundle"]["import_overlay"]["apply_route"] == "/api/graphiti/subgraph/materialize-l2b"
    assert plan["data"]["direct_graphiti_write"] is False
    assert plan["data"]["direct_l2b_write"] is False
    assert plan["data"]["materialization_state"] == "preview_only_not_materialized"
    assert plan["data"]["context_route_policy"]["requires_materialized_l2b_uuid"] is True
    assert (
        plan["data"]["graphiti_bundle"]["import_overlay"]["context_route_policy"]["preview_uuid_status"]
        == "not_queryable_until_l2b_materialization"
    )
    transform_preview = plan["data"]["l2b_transform_preview"]
    assert transform_preview["projection_kind"] == "graphiti_bundle_to_l2b_rustworkx_preview"
    assert transform_preview["section_counts"] == {
        "facts": 1,
        "entities": 2,
        "episodes": 1,
        "communities": 0,
    }
    assert transform_preview["l2b_edges"][0]["kind"] == "graphiti_fact"
    assert transform_preview["l2b_edges"][0]["source"] == "graphiti:arknights_test:entity:source-amiya"
    assert transform_preview["l2b_edges"][0]["target"] == "graphiti:arknights_test:entity:target-rhodes"
    assert transform_preview["l2b_edges"][0]["meta"]["graphiti_raw"]["target_node"]["name"] == "Rhodes Island"
    assert transform_preview["rustworkx_preview"]["rwx_idx_policy"] == "ephemeral_do_not_persist"
    assert transform_preview["policies"]["preserve_raw_graphiti"] is True
    assert plan["data"]["graphiti_bundle"]["import_overlay"]["transform_preview"]["projection_kind"] == "graphiti_bundle_to_l2b_rustworkx_preview"
    assert plan["data"]["identity_ref_drafts"][0]["graphiti_raw"]["raw"]["target_node"]["name"] == "Rhodes Island"
    assert plan["data"]["identity_ref_drafts"][0]["apply_route"] == "/api/memory/identity-ref-index/apply"
    assert plan["data"]["edge_drafts"][0]["source_graphiti_uuid"] == "source-amiya"
    assert plan["data"]["import_policy"]["destination"] == "isolated_compartment"
    assert plan["data"]["import_policy"]["source_kind"] == "graphiti"
    assert plan["data"]["import_draft"]["proposed_edges"][0]["source"] == "source-amiya"
    assert plan["data"]["l15_export_route"] == "/api/graphiti/subgraph/export"
    assert plan["data"]["apply_route"] == "/api/graphiti/subgraph/materialize-l2b"
    assert plan["data"]["apply_preconditions"]["materialize_l2b"].startswith("reviewed Graphiti bundle")
    assert plan["data"]["apply_preconditions"]["preserve_raw_graphiti"] is True
    assert plan["data"]["core_candidates"] == ["CORE-008", "CORE-013", "CORE-015"]
    assert plan["data"]["export_receipt_id"].startswith("web_")
    assert "sk-" not in str(plan).lower()


def test_graphiti_subgraph_materialize_l2b_is_operator_gated_and_context_queryable(
    monkeypatch,
    tmp_path,
) -> None:
    import parrot.dsg.l2b_graph as l2b_graph_module
    from parrot.brain import graphiti_console
    from parrot.dsg.l2b_graph import L2BGraph

    monkeypatch.delenv("PARROT_WEB_CONSOLE_L2B_URL", raising=False)
    monkeypatch.delenv("PARROT_WEB_CONSOLE_GRAPHITI_URL", raising=False)
    monkeypatch.delenv("PARROT_GRAPHITI_REMOTE_URL", raising=False)
    monkeypatch.setenv(
        "PARROT_MEMORY_IDENTITY_REF_INDEX_PATH",
        str(tmp_path / "identity_ref_index.json"),
    )
    monkeypatch.setattr(graphiti_console, "_graphiti_core_installed", lambda: False)
    graph = L2BGraph()
    monkeypatch.setattr(l2b_graph_module, "_instance", graph)
    hit = {
        "text": "Amiya's role changes as Rhodes Island leaves Chernobog.",
        "uuid": "graphiti-hit-materialize-1",
        "source_node_uuid": "source-amiya",
        "target_node_uuid": "target-rhodes",
        "episode_uuids": ["episode-plan-1"],
        "graphiti_raw": {
            "uuid": "graphiti-hit-materialize-1",
            "fact": "Amiya's role changes as Rhodes Island leaves Chernobog.",
            "source_node": {"uuid": "source-amiya", "name": "Amiya"},
            "target_node": {"uuid": "target-rhodes", "name": "Rhodes Island"},
        },
        "score": 0.83,
        "source_description": "arknights_test:main_00",
    }
    payload = {
        "partition": "arknights_test",
        "query": "Amiya Chernobog",
        "hits": [hit],
        "destination": "isolated_compartment",
    }

    try:
        client = TestClient(build_app(status_fetcher=_fake_fetcher))
        preview = client.post(
            "/api/graphiti/subgraph/materialize-l2b",
            json={**payload, "dry_run": True, "operator_mode": False},
        ).json()
        assert preview["action"] == "graphiti.subgraph.materialize_l2b"
        assert preview["success"] is True
        assert preview["dry_run"] is True
        assert preview["data"]["would_materialize"] is True
        assert preview["data"]["direct_l2b_write"] is False
        assert preview["data"]["identity_ref_index_write"] is False
        assert graph.node_count() == 0

        applied = client.post(
            "/api/graphiti/subgraph/materialize-l2b",
            json={**payload, "dry_run": False, "operator_mode": True},
        ).json()
        assert applied["success"] is True
        assert applied["dry_run"] is False
        assert applied["operator_mode"] is True
        assert applied["data"]["direct_l2b_write"] is True
        assert applied["data"]["direct_graphiti_write"] is False
        assert applied["data"]["direct_falkordb_write"] is False
        assert applied["data"]["materialization_state"] == "materialized_l2b_pointer_graph"
        assert applied["data"]["nodes_upserted"] >= 3
        assert applied["data"]["edges_added"] >= 1
        assert applied["data"]["identity_ref_index_write"] is True
        assert applied["data"]["context_node_uuids"][0] == "graphiti:arknights_test:entity:source-amiya"

        node = graph.get_node("graphiti:arknights_test:entity:source-amiya")
        assert node is not None
        assert node.source == "graphiti"
        assert node.bucket_id == "graphiti_import_materialized"
        assert "None" not in node.known_facts
        assert node.known_facts == ["Amiya"]
        assert node.meta["preserve_raw_graphiti"] is True
        assert node.meta["materialization_state"] == "materialized_l2b_pointer"
        assert node.source_meta["source_ref"] == "graphiti://arknights_test/entity/source-amiya"
        edge = next(
            edge
            for src, dst, edge in graph.all_edges()
            if src.uuid == "graphiti:arknights_test:entity:source-amiya"
            and dst.uuid == "graphiti:arknights_test:entity:target-rhodes"
        )
        assert edge.kind.value == "graphiti_fact"
        assert edge.source == "graphiti"
        assert edge.graphiti_uuid == "graphiti-hit-materialize-1"
        assert edge.meta["graphiti_raw"]["target_node"]["name"] == "Rhodes Island"

        context = client.post(
            "/api/l2b/subgraphs/context",
            json={
                "node_uuids": ["graphiti:arknights_test:entity:source-amiya"],
                "depth": 1,
                "dry_run": False,
                "operator_mode": True,
            },
        ).json()
        assert context["success"] is True
        assert context["data"]["selected_node_uuids"] == ["graphiti:arknights_test:entity:source-amiya"]
        assert context["data"]["missing_graphiti_preview_node_uuids"] == []
        assert {row["uuid"] for row in context["data"]["nodes"]} >= {
            "graphiti:arknights_test:entity:source-amiya",
            "graphiti:arknights_test:entity:target-rhodes",
        }
        assert context["data"]["edges"][0]["meta"]["preserve_raw_graphiti"] is True

        reapplied = client.post(
            "/api/graphiti/subgraph/materialize-l2b",
            json={**payload, "dry_run": False, "operator_mode": True},
        ).json()
        assert reapplied["success"] is True
        assert reapplied["data"]["edges_added"] == 0
        assert reapplied["data"]["edges_skipped_duplicate"] >= applied["data"]["edges_added"]
    finally:
        l2b_graph_module._instance = None


def test_graphiti_subgraph_import_plan_preserves_episode_hit_without_fact_edge(monkeypatch) -> None:
    from parrot.brain import graphiti_console

    monkeypatch.setattr(graphiti_console, "_graphiti_core_installed", lambda: False)
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    plan = client.post(
        "/api/graphiti/subgraph/import-plan",
        json={
            "partition": "noble_etiquette",
            "query": "etiquette",
            "hits": [
                {
                    "uuid": "episode-noble-1",
                    "graphiti_uuid": "episode-noble-1",
                    "graphiti_kind": "graphiti_episode",
                    "text": "Original etiquette note. Formal greetings acknowledge relative rank.",
                    "graphiti_raw": {
                        "uuid": "episode-noble-1",
                        "group_id": "noble_etiquette",
                        "labels": ["Episodic"],
                        "content": "Original etiquette note. Formal greetings acknowledge relative rank.",
                    },
                }
            ],
        },
    ).json()

    assert plan["success"] is True
    bundle = plan["data"]["graphiti_bundle"]
    assert len(bundle["sections"]["facts"]) == 0
    assert bundle["sections"]["episodes"][0]["uuid"] == "episode-noble-1"
    assert plan["data"]["edge_drafts"] == []
    assert plan["data"]["identity_ref_drafts"][0]["ref_kind"] == "graphiti_episode"
    assert "graphiti_edge_uuid" not in plan["data"]["identity_ref_drafts"][0]
    transform_preview = plan["data"]["l2b_transform_preview"]
    assert transform_preview["section_counts"]["facts"] == 0
    assert transform_preview["section_counts"]["episodes"] == 1

    materialize = client.post(
        "/api/graphiti/subgraph/materialize-l2b",
        json={
            "partition": "noble_etiquette",
            "query": "etiquette",
            "graphiti_bundle": bundle,
            "dry_run": True,
            "operator_mode": False,
        },
    ).json()
    assert materialize["success"] is True
    assert materialize["data"]["projection_source"] == "graphiti_bundle_payload"
    assert materialize["data"]["selected_count"] == 1
    assert materialize["data"]["node_count"] == 1
    assert materialize["data"]["edge_count"] == 0


def test_graphiti_subgraph_import_plan_uses_normalized_partition(monkeypatch) -> None:
    from parrot.brain import graphiti_console

    monkeypatch.setattr(graphiti_console, "_graphiti_core_installed", lambda: False)
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    plan = client.post(
        "/api/graphiti/subgraph/import-plan",
        json={
            "partition": "unknown_partition",
            "query": "Amiya",
            "hits": [{"text": "Amiya leads Rhodes Island.", "uuid": "graphiti-hit-raw"}],
        },
    ).json()

    assert plan["success"] is True
    assert plan["data"]["partition"] == "goslo"
    assert plan["data"]["subgraph"]["partition"] == "goslo"
    assert plan["data"]["observations"][0]["meta"]["graphiti_partition"] == "goslo"
    assert plan["data"]["import_policy"]["source_id"] == "goslo:Amiya"


def test_graphiti_subgraph_import_plan_skips_policy_when_no_hits(monkeypatch) -> None:
    from parrot.brain import graphiti_console

    monkeypatch.setattr(graphiti_console, "_graphiti_core_installed", lambda: False)
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    plan = client.post(
        "/api/graphiti/subgraph/import-plan",
        json={
            "partition": "arknights_test",
            "query": "nothing selected",
            "hits": [],
            "destination": "isolated_compartment",
        },
    ).json()

    assert plan["action"] == "graphiti.subgraph.import_plan"
    assert plan["success"] is False
    assert plan["data"]["selected_count"] == 0
    assert plan["data"]["import_policy"] == {}
    assert plan["data"]["import_draft"] == {}
    assert plan["data"]["policy_skipped_reason"] == "no_graphiti_observations"
    assert plan["data"]["policy_receipt_id"] == ""


def test_graphiti_subgraph_operator_export_admits_through_l15(monkeypatch) -> None:
    captured: list[Any] = []

    class FakePool:
        async def admit(self, observations):
            captured.extend(observations)
            return _FakeAdmitOutcome()

    monkeypatch.setattr("parrot.dsg.l1_5.pool.get_l1_5_pool", lambda: FakePool())
    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    hit = {
        "text": "Amiya chooses to protect Rhodes Island during Chernobog.",
        "uuid": "graphiti-operator-hit-1",
        "source_node_uuid": "source-amiya",
        "target_node_uuid": "target-rhodes",
        "source_description": "arknights_test:main_00",
    }

    body = client.post(
        "/api/graphiti/subgraph/export",
        json={
            "partition": "arknights_test",
            "query": "Amiya",
            "hits": [hit],
            "dry_run": False,
            "operator_mode": True,
        },
    ).json()

    assert body["action"] == "graphiti.subgraph.export"
    assert body["success"] is True
    assert body["dry_run"] is False
    assert body["operator_mode"] is True
    assert body["data"]["selected_count"] == 1
    assert len(captured) == 1
    assert captured[0].graphiti_uuid == "graphiti-operator-hit-1"
    assert captured[0].meta["graphiti_partition"] == "arknights_test"
    assert captured[0].meta["graphiti_raw"]["uuid"] == "graphiti-operator-hit-1"
    assert body["data"]["write_path"] == "L15Pool.admit(Observation(source=USER_EXPLICIT))"
    assert body["data"]["identity_ref_drafts"][0]["graphiti_edge_uuid"] == "graphiti-operator-hit-1"


def test_arknights_graphiti_fixture_script_dry_run() -> None:
    import subprocess
    import sys

    result = subprocess.run(
        [
            sys.executable,
            "src/scripts/import_arknights_to_graphiti.py",
            "--dry-run",
            "--limit",
            "2",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["dry_run"] is True
    assert payload["partition"] == "arknights_test"
    assert len(payload["episodes"]) == 2
    assert payload["episodes"][0]["story_order"] == "main_00_01"
    assert "copied" not in payload["episodes"][0]["episode_body"].lower()
    assert "source_url" in payload["episodes"][0]["episode_body"]


def test_obsidian_vault_scan_previews_three_profiles(tmp_path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "daily.md").write_text(
        "---\nprofile: daily\nlabel: Daily desk rule\nkind: object\ntags: daily,desk\n---\nKeep the desk clear.",
        encoding="utf-8-sig",
    )
    (vault / "roleplay.md").write_text(
        "---\nprofile: roleplay\nlabel: Harbor scene pack\nkind: object\n---\nScene mood and props.",
        encoding="utf-8",
    )
    (vault / "ref.md").write_text(
        "---\nprofile: ref\nlabel: Blue mug ref\nobsidian_uuid: mug-ref-1\ntarget_node_uuid: node-1\n---\nReference binding.",
        encoding="utf-8",
    )
    (vault / "bad_ref.md").write_text(
        "---\nprofile: ref\nlabel: Missing target\n---\nThis ref is intentionally invalid.",
        encoding="utf-8",
    )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    body = client.get(
        "/api/l15/obsidian-vault/scan",
        params={"vault_path": str(vault), "limit": 8},
    ).json()

    assert body["action"] == "l15.obsidian_vault.scan"
    assert body["success"] is True
    assert body["data"]["vault"]["status"] == "ingest_ready"
    profiles = {row["profile"] for row in body["data"]["notes"]}
    assert {"daily", "roleplay", "ref"} <= profiles
    roleplay = next(row for row in body["data"]["notes"] if row["profile"] == "roleplay")
    assert roleplay["uuid_free_allowed"] is True
    assert roleplay["target_bucket"] == "obsidian_setting_roleplay"
    ref = next(row for row in body["data"]["notes"] if row["profile"] == "ref")
    assert ref["payload"]["target_node_uuid"] == "node-1"
    assert body["data"]["invalid_notes"][0]["reason"] == "missing_frontmatter_or_ref_target"


def test_obsidian_vault_import_draft_uses_l15_observation_path(tmp_path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "daily.md").write_text(
        "---\nprofile: daily\nlabel: Daily desk rule\nkind: object\n---\nKeep the desk clear.",
        encoding="utf-8",
    )
    (vault / "roleplay.md").write_text(
        "---\nprofile: roleplay\nlabel: Harbor pack\nkind: object\n---\nRoleplay scene notes.",
        encoding="utf-8",
    )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    draft = client.post(
        "/api/l15/obsidian-vault/import-draft",
        json={"vault_path": str(vault), "paths": ["roleplay.md"], "limit": 8},
    ).json()
    dry_apply = client.post(
        "/api/l15/obsidian-vault/import",
        json={
            "vault_path": str(vault),
            "paths": ["roleplay.md"],
            "dry_run": True,
            "operator_mode": False,
        },
    ).json()

    assert draft["action"] == "l15.obsidian_vault.import_draft"
    assert draft["success"] is True
    assert draft["data"]["selected_count"] == 1
    item = draft["data"]["items"][0]
    assert item["profile"] == "roleplay"
    assert item["target_bucket"] == "obsidian_setting_roleplay"
    assert item["observation"]["source"] == "user_tag_obsidian"
    assert item["observation"]["meta"]["profile"] == "roleplay"
    assert draft["data"]["write_path"] == "UserTagFilter -> L15Pool.admit(USER_TAG_OBSIDIAN)"
    assert dry_apply["action"] == "l15.obsidian_vault.import"
    assert dry_apply["data"]["would_apply"] is True
    assert dry_apply["data"]["apply_skipped_reason"] == "dry_run_or_operator_mode_missing"


def test_obsidian_vault_operator_import_admits_through_l15(tmp_path, monkeypatch) -> None:
    captured: list[Any] = []

    class FakePool:
        async def admit(self, observations):
            captured.extend(observations)
            return _FakeAdmitOutcome()

    monkeypatch.setattr("parrot.dsg.l1_5.pool.get_l1_5_pool", lambda: FakePool())
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "daily.md").write_text(
        "---\nprofile: daily\nlabel: Daily desk rule\nkind: object\n---\nKeep the desk clear.",
        encoding="utf-8",
    )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    body = client.post(
        "/api/l15/obsidian-vault/import",
        json={
            "vault_path": str(vault),
            "paths": ["daily.md"],
            "dry_run": False,
            "operator_mode": True,
        },
    ).json()

    assert body["action"] == "l15.obsidian_vault.import"
    assert body["success"] is True
    assert body["dry_run"] is False
    assert body["operator_mode"] is True
    assert body["data"]["imported_count"] == 1
    assert len(captured) == 1
    assert captured[0].label == "Daily desk rule"
    assert captured[0].meta["profile"] == "daily"
    assert body["data"]["write_path"] == "UserTagFilter -> L15Pool.admit(USER_TAG_OBSIDIAN)"


def test_obsidian_vault_import_plan_combines_l15_and_graph_policy(tmp_path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "daily.md").write_text(
        "---\nprofile: daily\nlabel: Daily desk rule\nkind: object\n---\nKeep the desk clear.",
        encoding="utf-8",
    )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    plan = client.post(
        "/api/l15/obsidian-vault/import-plan",
        json={
            "vault_path": str(vault),
            "paths": ["daily.md"],
            "destination": "isolated_compartment",
            "workspace_id": "memory_graph",
            "subgraph_label": "Daily settings",
            "dry_run": False,
            "operator_mode": True,
        },
    ).json()

    assert plan["action"] == "l15.obsidian_vault.import_plan"
    assert plan["success"] is True
    assert plan["dry_run"] is True
    assert plan["operator_mode"] is False
    assert plan["data"]["requested_execution"] == {
        "dry_run": False,
        "operator_mode": True,
        "ignored_for_plan": True,
    }
    assert plan["data"]["selected_count"] == 1
    assert plan["data"]["items"][0]["target_bucket"] == "obsidian_setting_daily"
    assert plan["data"]["import_policy"]["destination"] == "isolated_compartment"
    assert plan["data"]["import_policy"]["source_kind"] == "obsidian"
    assert plan["data"]["apply_route"] == "/api/l15/obsidian-vault/import"
    assert "UserTagFilter" in plan["data"]["write_path"]
    assert "CORE-013" in plan["data"]["core_candidates"]
    assert "PARROT_ORCH_SECRET" not in str(plan)


def test_obsidian_vault_import_plan_skips_policy_when_no_items(tmp_path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    plan = client.post(
        "/api/l15/obsidian-vault/import-plan",
        json={
            "vault_path": str(vault),
            "paths": ["missing.md"],
            "destination": "isolated_compartment",
        },
    ).json()

    assert plan["action"] == "l15.obsidian_vault.import_plan"
    assert plan["success"] is False
    assert plan["data"]["selected_count"] == 0
    assert plan["data"]["import_policy"] == {}
    assert plan["data"]["import_draft"] == {}
    assert plan["data"]["policy_skipped_reason"] == "no_importable_obsidian_items"
    assert plan["data"]["policy_receipt_id"] == ""
    assert plan["data"]["errors"][0]["error"] == "selected_path_not_found"


def test_obsidian_vault_import_draft_reports_selected_missing_or_invalid_paths(tmp_path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "daily.md").write_text(
        "---\nprofile: daily\nlabel: Daily desk rule\nkind: object\n---\nKeep the desk clear.",
        encoding="utf-8",
    )
    (vault / "bad_ref.md").write_text(
        "---\nprofile: ref\nlabel: Missing target\n---\nThis ref is intentionally invalid.",
        encoding="utf-8",
    )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    draft = client.post(
        "/api/l15/obsidian-vault/import-draft",
        json={
            "vault_path": str(vault),
            "paths": ["daily.md", "bad_ref.md", "missing.md"],
            "limit": 8,
        },
    ).json()

    assert draft["action"] == "l15.obsidian_vault.import_draft"
    assert draft["success"] is False
    assert draft["data"]["selected_count"] == 1
    errors = {row["path"]: row["error"] for row in draft["data"]["errors"]}
    assert errors["bad_ref.md"] == "note_not_import_ready"
    assert errors["missing.md"] == "selected_path_not_found"


def test_obsidian_vault_import_draft_reports_profile_mismatch_for_selected_path(tmp_path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "daily.md").write_text(
        "---\nprofile: daily\nlabel: Daily desk rule\nkind: object\n---\nKeep the desk clear.",
        encoding="utf-8",
    )
    (vault / "roleplay.md").write_text(
        "---\nprofile: roleplay\nlabel: Harbor pack\nkind: object\n---\nRoleplay scene notes.",
        encoding="utf-8",
    )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    draft = client.post(
        "/api/l15/obsidian-vault/import-draft",
        json={
            "vault_path": str(vault),
            "paths": ["daily.md", "roleplay.md"],
            "profiles": ["roleplay"],
            "limit": 8,
        },
    ).json()

    assert draft["success"] is False
    assert draft["data"]["selected_count"] == 1
    assert draft["data"]["items"][0]["path"] == "roleplay.md"
    assert draft["data"]["errors"] == [
        {
            "path": "daily.md",
            "profile": "daily",
            "error": "selected_profile_mismatch",
            "expected_profiles": ["roleplay"],
        }
    ]


def test_obsidian_vault_import_draft_reports_selected_paths_over_limit(tmp_path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    for name in ("a.md", "b.md", "c.md"):
        (vault / name).write_text(
            f"---\nprofile: daily\nlabel: {name}\nkind: object\n---\n{name}",
            encoding="utf-8",
        )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    draft = client.post(
        "/api/l15/obsidian-vault/import-draft",
        json={
            "vault_path": str(vault),
            "paths": ["a.md", "b.md", "c.md"],
            "limit": 2,
        },
    ).json()

    assert draft["success"] is False
    assert draft["data"]["selected_count"] == 2
    assert [item["path"] for item in draft["data"]["items"]] == ["a.md", "b.md"]
    assert draft["data"]["errors"] == [
        {
            "path": "c.md",
            "profile": "daily",
            "error": "selected_path_over_limit",
            "limit": 2,
        }
    ]


def test_obsidian_vault_scan_and_import_draft_reject_invalid_limit(tmp_path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "daily.md").write_text(
        "---\nprofile: daily\nlabel: Daily desk rule\nkind: object\n---\nKeep the desk clear.",
        encoding="utf-8",
    )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    scan = client.get(
        "/api/l15/obsidian-vault/scan",
        params={"vault_path": str(vault), "limit": "abc"},
    ).json()
    draft = client.post(
        "/api/l15/obsidian-vault/import-draft",
        json={"vault_path": str(vault), "paths": ["daily.md"], "limit": "abc"},
    ).json()

    assert scan["success"] is False
    assert scan["data"]["error"]["error"] == "invalid_limit"
    assert draft["success"] is False
    assert draft["data"]["errors"][0]["error"] == "invalid_limit"


def test_google_calendar_preview_preserves_mapping_fields() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    body = client.post(
        "/api/google/calendar/preview",
        json={
            "events": [
                {
                    "id": "evt_preview",
                    "calendar_id": "primary",
                    "summary": "Calendar preview",
                    "start": {"dateTime": "2026-05-15T10:00:00+08:00", "timeZone": "Asia/Shanghai"},
                    "end": {"dateTime": "2026-05-15T10:30:00+08:00", "timeZone": "Asia/Shanghai"},
                    "location": "Desk",
                    "htmlLink": "https://calendar.google.com/event?eid=test",
                    "etag": "etag-preview",
                    "status": "confirmed",
                    "iCalUID": "ical-preview",
                    "objects": ["blue mug"],
                }
            ]
        },
    ).json()

    assert body["action"] == "google.calendar.preview"
    assert body["success"] is True
    normalized = body["data"]["normalized_events"][0]
    assert normalized["id"] == "evt_preview"
    assert normalized["start_time"] == "2026-05-15T10:00:00+08:00"
    assert normalized["timezone"] == "Asia/Shanghai"
    assert normalized["html_link"].startswith("https://calendar.google.com/")
    observation = body["data"]["observations"][0]
    assert observation["source"] == "google_calendar"
    assert observation["kind"] == "event"
    assert observation["meta"]["calendar_event_id"] == "evt_preview"
    assert observation["meta"]["etag"] == "etag-preview"
    mapping = body["data"]["mapping_rows"][0]
    assert mapping["calendar_event_id"] == "evt_preview"
    assert mapping["l15_bucket"] == "google_calendar"
    assert mapping["l2b_kind"] == "event"
    assert mapping["l2b_action"] == "upsert_event"
    assert mapping["intent_workspace_policy"] == "not_used_for_read_sync"
    assert "operator_required_for_import" in body["data"]


def test_google_calendar_preview_accepts_raw_google_items_payload() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    raw = json.dumps(
        {
            "items": [
                {
                    "id": "evt_raw",
                    "calendar_id": "primary",
                    "summary": "Raw Google item",
                    "start": {
                        "dateTime": "2026-05-15T12:00:00+08:00",
                        "timeZone": "Asia/Shanghai",
                    },
                    "end": {
                        "dateTime": "2026-05-15T12:30:00+08:00",
                        "timeZone": "Asia/Shanghai",
                    },
                    "htmlLink": "https://calendar.google.com/event?eid=raw",
                }
            ]
        }
    )

    body = client.post("/api/google/calendar/preview", json={"raw": raw}).json()

    assert body["success"] is True
    normalized = body["data"]["normalized_events"][0]
    assert normalized["id"] == "evt_raw"
    assert normalized["title"] == "Raw Google item"
    assert normalized["start_time"] == "2026-05-15T12:00:00+08:00"
    assert body["data"]["observations"][0]["meta"]["calendar_event_id"] == "evt_raw"
    assert body["data"]["mapping_rows"][0]["provider_ref"] == "google_calendar:primary:evt_raw"


def test_google_calendar_preview_marks_cancelled_as_historical_tombstone() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    body = client.post(
        "/api/google/calendar/preview",
        json={
            "events": [
                {
                    "id": "evt_cancelled",
                    "calendar_id": "primary",
                    "summary": "Cancelled sync item",
                    "status": "cancelled",
                    "start": {"dateTime": "2026-05-15T13:00:00+08:00"},
                }
            ]
        },
    ).json()

    assert body["success"] is True
    mapping = body["data"]["mapping_rows"][0]
    observation = body["data"]["observations"][0]
    assert mapping["status"] == "cancelled"
    assert mapping["l2b_action"] == "mark_historical_tombstone"
    assert mapping["policy_note"] == "keep_google_identity_and_set_ghost_state"
    assert observation["confirmation"] == "ghost"
    assert observation["meta"]["is_tombstone"] is True
    assert observation["meta"]["tombstone_policy"] == "historical_event"


def test_google_calendar_fetch_dispatch_is_operator_gated() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    body = client.post("/api/google/calendar/fetch", json={}).json()

    assert body["action"] == "google.calendar.fetch.dispatch"
    assert body["success"] is True
    assert body["dry_run"] is True
    assert body["operator_mode"] is False
    assert body["data"]["task_type"] == "calendar_fetch"
    assert body["data"]["params"]["result_channel"] == "calendar_result"
    assert body["data"]["would_dispatch"] is True
    assert body["data"]["dispatch_skipped_reason"] == "dry_run_or_operator_mode_missing"
    assert "Google Workspace MCP" in body["data"]["result_flow"]
    assert "sk-" not in str(body).lower()


def test_google_calendar_fetch_can_dispatch_in_operator_mode(monkeypatch) -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    calls: list[dict[str, Any]] = []

    async def fake_do_dispatch_task(
        task_type: str,
        *,
        params: dict[str, Any] | None = None,
        priority: str = "normal",
    ) -> str:
        calls.append({"task_type": task_type, "params": params or {}, "priority": priority})
        return "task_calendar_real"

    dispatch_module = import_module("parrot.brain.tools.dispatch_task")
    monkeypatch.setattr(dispatch_module, "do_dispatch_task", fake_do_dispatch_task)

    body = client.post(
        "/api/google/calendar/fetch",
        json={"dry_run": False, "operator_mode": True, "priority": "normal"},
    ).json()

    assert body["action"] == "google.calendar.fetch.dispatch"
    assert body["success"] is True
    assert body["dry_run"] is False
    assert body["operator_mode"] is True
    assert body["data"]["dispatched"] is True
    assert body["data"]["task_id"] == "task_calendar_real"
    assert calls == [
        {
            "task_type": "calendar_fetch",
            "params": body["data"]["params"],
            "priority": "normal",
        }
    ]


def test_google_calendar_results_reads_scheduler_ledger(monkeypatch) -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    class FakeRedis:
        async def xrevrange(self, stream: str, count: int = 20):
            assert stream == "parrot.trigger.results.stream"
            assert count >= 6
            return [
                (
                    "1710000000000-0",
                    {
                        "payload": json.dumps(
                            {
                                "task_id": "task_calendar",
                                "type": "calendar_result",
                                "original_type": "calendar_fetch",
                                "status": "completed",
                                "api_key": "sk-should-redact",
                                "result": json.dumps(
                                    [
                                        {
                                            "id": "evt_history",
                                            "summary": "Ledger event",
                                            "start": {"dateTime": "2026-05-15T10:00:00+08:00"},
                                        }
                                    ]
                                ),
                            }
                        ),
                        "result_channel": "calendar_result",
                        "task_id": "task_calendar",
                        "created_at": "1710000000.0",
                    },
                )
            ]

    async def fake_get_redis():
        return FakeRedis()

    monkeypatch.setattr("parrot.shared.redis_client.get_redis", fake_get_redis)

    body = client.get("/api/google/calendar/results", params={"limit": 2}).json()

    assert body["action"] == "google.calendar.results"
    assert body["success"] is True
    assert body["data"]["available"] is True
    row = body["data"]["rows"][0]
    assert row["task_id"] == "task_calendar"
    assert row["result_channel"] == "calendar_result"
    assert row["original_type"] == "calendar_fetch"
    assert row["event_count"] == 1
    assert row["event_sample"][0]["id"] == "evt_history"
    assert row["payload"]["api_key"] == "<redacted>"
    assert "sk-should-redact" not in str(body)


def test_google_calendar_results_tolerates_missing_redis(monkeypatch) -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    async def fake_get_redis():
        raise RuntimeError("redis offline")

    monkeypatch.setattr("parrot.shared.redis_client.get_redis", fake_get_redis)

    body = client.get("/api/google/calendar/results").json()

    assert body["action"] == "google.calendar.results"
    assert body["success"] is True
    assert body["data"]["available"] is False
    assert body["data"]["rows"] == []


def test_google_calendar_api_fetch_uses_official_api_preview(monkeypatch) -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    calls: list[dict[str, Any]] = []

    async def fake_api_fetch(**kwargs):
        calls.append(kwargs)
        return {
            "credential_source": "local_google_workspace_mcp",
            "nextSyncToken": "sync-token-redacted",
            "items": [
                {
                    "id": "evt_api",
                    "summary": "API event",
                    "start": {
                        "dateTime": "2026-05-17T09:00:00+08:00",
                        "timeZone": "Asia/Shanghai",
                    },
                    "end": {"dateTime": "2026-05-17T09:30:00+08:00"},
                    "htmlLink": "https://calendar.google.com/event?eid=api",
                    "etag": "etag-api",
                    "status": "confirmed",
                    "iCalUID": "ical-api",
                }
            ],
        }

    memory_ops = import_module("parrot.web_console.memory_ops")
    monkeypatch.setattr(memory_ops, "_fetch_google_calendar_events_from_api", fake_api_fetch)

    body = client.post(
        "/api/google/calendar/api-fetch",
        json={
            "calendar_id": "primary",
            "timeMin": "2026-05-17T00:00:00+08:00",
            "timeMax": "2026-05-18T00:00:00+08:00",
            "limit": 5,
        },
    ).json()

    assert body["action"] == "google.calendar.api_fetch"
    assert body["success"] is True
    assert body["dry_run"] is False
    assert body["data"]["available"] is True
    assert body["data"]["read_model"] == "Google Calendar API events.list via OAuth2"
    assert body["data"]["count"] == 1
    assert body["data"]["events"][0]["calendar_id"] == "primary"
    assert body["data"]["normalized_events"][0]["id"] == "evt_api"
    assert body["data"]["observations"][0]["source"] == "google_calendar"
    assert body["data"]["mapping_rows"][0]["provider_ref"] == "google_calendar:primary:evt_api"
    assert body["data"]["next_sync_token_present"] is True
    assert body["data"]["credential_source"] == "local_google_workspace_mcp"
    assert calls == [
        {
            "calendar_id": "primary",
            "time_min": "2026-05-17T00:00:00+08:00",
            "time_max": "2026-05-18T00:00:00+08:00",
            "limit": 5,
            "show_deleted": False,
        }
    ]
    assert "sync-token-redacted" not in str(body)
    assert "access_token" not in str(body).lower()


def test_google_calendar_credentials_path_accepts_ecs_nanobot_mount(
    monkeypatch, tmp_path
) -> None:
    memory_ops = import_module("parrot.web_console.memory_ops")
    monkeypatch.delenv("PARROT_WEB_CONSOLE_GOOGLE_CREDENTIALS_PATH", raising=False)
    monkeypatch.delenv("GOOGLE_WORKSPACE_CREDENTIALS_PATH", raising=False)
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.setattr(memory_ops.Path, "home", lambda: tmp_path)

    credentials_dir = tmp_path / ".nanobot" / "google-workspace-credentials"
    credentials_dir.mkdir(parents=True)
    credentials_path = credentials_dir / "credentials_python.json"
    credentials_path.write_text("{}", encoding="utf-8")

    assert memory_ops._google_calendar_credentials_path() == credentials_path
    assert (
        memory_ops._google_calendar_credential_source(credentials_path)
        == "ecs_nanobot_google_workspace_mcp"
    )


def test_google_calendar_nanobot_fetch_uses_ecs_mcp_preview(monkeypatch) -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    calls: list[dict[str, Any]] = []

    async def fake_nanobot_fetch(**kwargs):
        calls.append(kwargs)
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "status": "success",
                                "event_count": 1,
                                "events": [
                                    {
                                        "id": "evt_nanobot",
                                        "summary": "Nanobot event",
                                        "start_time": "2026-05-17T10:00:00+08:00",
                                        "end_time": "2026-05-17T10:30:00+08:00",
                                        "html_link": "https://calendar.google.com/event?eid=nanobot",
                                        "status": "confirmed",
                                        "iCalUID": "ical-nanobot",
                                    }
                                ],
                            }
                        )
                    }
                }
            ]
        }

    memory_ops = import_module("parrot.web_console.memory_ops")
    monkeypatch.setattr(
        memory_ops,
        "_fetch_google_calendar_events_from_nanobot",
        fake_nanobot_fetch,
    )

    body = client.post(
        "/api/google/calendar/nanobot-fetch",
        json={
            "account": "gosloparrot@gmail.com",
            "calendar_id": "primary",
            "timeMin": "2026-05-17T00:00:00+08:00",
            "timeMax": "2026-05-18T00:00:00+08:00",
            "limit": 4,
        },
    ).json()

    assert body["action"] == "google.calendar.nanobot_fetch"
    assert body["success"] is True
    assert body["dry_run"] is False
    assert body["data"]["available"] is True
    assert body["data"]["read_model"] == "ECS Nanobot -> Google Workspace MCP manage_calendar"
    assert body["data"]["source_kind"] == "google_calendar_nanobot"
    assert body["data"]["count"] == 1
    assert body["data"]["nanobot_event_count"] == 1
    assert body["data"]["events"][0]["calendar_id"] == "primary"
    assert body["data"]["normalized_events"][0]["id"] == "evt_nanobot"
    assert body["data"]["observations"][0]["source"] == "google_calendar"
    assert body["data"]["mapping_rows"][0]["provider_ref"] == "google_calendar:primary:evt_nanobot"
    assert calls == [
        {
            "account": "gosloparrot@gmail.com",
            "calendar_id": "primary",
            "time_min": "2026-05-17T00:00:00+08:00",
            "time_max": "2026-05-18T00:00:00+08:00",
            "timezone_name": "Asia/Shanghai",
            "limit": 4,
            "show_deleted": False,
        }
    ]
    assert "access_token" not in str(body).lower()
    assert "refresh_token" not in str(body).lower()


def test_google_calendar_import_routes_are_l15_operator_gated() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    payload = {
        "events": [
            {
                "id": "evt_import",
                "calendar_id": "primary",
                "summary": "Calendar import",
                "start": {"dateTime": "2026-05-15T11:00:00+08:00", "timeZone": "Asia/Shanghai"},
                "end": {"dateTime": "2026-05-15T11:30:00+08:00", "timeZone": "Asia/Shanghai"},
                "htmlLink": "https://calendar.google.com/event?eid=import",
                "etag": "etag-import",
                "status": "confirmed",
                "objects": ["blue mug"],
            }
        ]
    }

    draft = client.post("/api/google/calendar/import-draft", json=payload).json()
    apply_preview = client.post("/api/google/calendar/import", json=payload).json()

    assert draft["action"] == "google.calendar.import_draft"
    assert draft["success"] is True
    assert draft["dry_run"] is True
    assert draft["operator_mode"] is False
    assert draft["data"]["observation_count"] == 1
    assert draft["data"]["observations"][0]["source"] == "google_calendar"
    assert draft["data"]["observations"][0]["meta"]["calendar_event_id"] == "evt_import"
    assert draft["data"]["mapping_rows"][0]["merge_key"] == "primary:evt_import"
    assert "L15Pool.admit" in draft["data"]["write_path"]
    assert apply_preview["action"] == "google.calendar.import"
    assert apply_preview["success"] is True
    assert apply_preview["dry_run"] is True
    assert apply_preview["operator_mode"] is False
    assert apply_preview["data"]["would_apply"] is True
    assert apply_preview["data"]["apply_skipped_reason"] == "dry_run_or_operator_mode_missing"
    assert "sk-" not in str(draft).lower()
    assert "PARROT_ORCH_SECRET" not in str(draft)


def test_google_calendar_import_plan_combines_l15_and_graph_policy() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    plan = client.post(
        "/api/google/calendar/import-plan",
        json={
            "destination": "isolated_compartment",
            "events": [
                {
                    "id": "evt_plan",
                    "calendar_id": "primary",
                    "summary": "Calendar import plan",
                    "start": {
                        "dateTime": "2026-05-15T11:00:00+08:00",
                        "timeZone": "Asia/Shanghai",
                    },
                    "end": {"dateTime": "2026-05-15T11:30:00+08:00"},
                    "status": "confirmed",
                }
            ],
            "dry_run": False,
            "operator_mode": True,
        },
    ).json()

    assert plan["action"] == "google.calendar.import_plan"
    assert plan["success"] is True
    assert plan["dry_run"] is True
    assert plan["operator_mode"] is False
    assert plan["data"]["requested_execution"] == {
        "dry_run": False,
        "operator_mode": True,
        "ignored_for_plan": True,
    }
    assert plan["data"]["observation_count"] == 1
    assert plan["data"]["mapping_rows"][0]["merge_key"] == "primary:evt_plan"
    assert plan["data"]["import_policy"]["destination"] == "isolated_compartment"
    assert plan["data"]["import_policy"]["source_kind"] == "google_calendar"
    assert plan["data"]["sync_policy"].startswith("manual_fetch_import_v1")
    assert plan["data"]["apply_route"] == "/api/google/calendar/import"
    assert "CORE-013" in plan["data"]["core_candidates"]
    assert "sk-" not in str(plan).lower()


def test_source_import_plan_matrix_is_draft_only_and_operator_safe(tmp_path, monkeypatch) -> None:
    from parrot.brain import graphiti_console

    monkeypatch.setattr(graphiti_console, "_graphiti_core_installed", lambda: False)
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "daily.md").write_text(
        "---\nprofile: daily\nlabel: Daily desk rule\nkind: object\n---\nKeep the desk clear.",
        encoding="utf-8",
    )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    graphiti_hit = {
        "text": "Amiya's role changes as Rhodes Island leaves Chernobog.",
        "uuid": "graphiti-hit-matrix-1",
        "source_node_uuid": "source-amiya",
        "target_node_uuid": "target-rhodes",
        "score": 0.83,
        "source_url": "https://prts.wiki/w/%E5%89%A7%E6%83%85%E4%B8%80%E8%A7%88",
        "source_description": "arknights_test:main_00",
    }
    calendar_event = {
        "id": "evt_matrix",
        "calendar_id": "primary",
        "summary": "Calendar import plan",
        "start": {
            "dateTime": "2026-05-15T11:00:00+08:00",
            "timeZone": "Asia/Shanghai",
        },
        "end": {"dateTime": "2026-05-15T11:30:00+08:00"},
        "status": "confirmed",
    }
    requests = [
        (
            "graphiti",
            "/api/graphiti/subgraph/import-plan",
            {
                "partition": "arknights_test",
                "query": "Amiya Chernobog",
                "hits": [graphiti_hit],
                "destination": "isolated_compartment",
                "dry_run": False,
                "operator_mode": True,
            },
            "/api/graphiti/subgraph/materialize-l2b",
        ),
        (
            "obsidian",
            "/api/l15/obsidian-vault/import-plan",
            {
                "vault_path": str(vault),
                "paths": ["daily.md"],
                "destination": "isolated_compartment",
                "dry_run": False,
                "operator_mode": True,
            },
            "/api/l15/obsidian-vault/import",
        ),
        (
            "google_calendar",
            "/api/google/calendar/import-plan",
            {
                "events": [calendar_event],
                "destination": "isolated_compartment",
                "dry_run": False,
                "operator_mode": True,
            },
            "/api/google/calendar/import",
        ),
    ]

    for source_kind, route, payload, apply_route in requests:
        plan = client.post(route, json=payload).json()
        data = plan["data"]
        serialized = str(plan).lower()

        assert plan["success"] is True
        assert plan["dry_run"] is True
        assert plan["operator_mode"] is False
        assert data["requested_execution"] == {
            "dry_run": False,
            "operator_mode": True,
            "ignored_for_plan": True,
        }
        assert data["operator_required_for_execute"] is True
        assert data["apply_route"] == apply_route
        assert data["apply_preconditions"]["dry_run"] is False
        assert data["apply_preconditions"]["operator_mode"] is True
        assert data["import_policy"]["destination"] == "isolated_compartment"
        assert data["import_policy"]["source_kind"] == source_kind
        assert "CORE-008" in data["core_candidates"]
        assert "CORE-013" in data["core_candidates"]
        assert "sk-" not in serialized
        assert "parrot_orch_secret" not in serialized
        assert "direct_falkordb_write': true" not in serialized


def test_google_calendar_import_plan_skips_policy_when_no_observations() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    plan = client.post(
        "/api/google/calendar/import-plan",
        json={"destination": "isolated_compartment", "events": []},
    ).json()

    assert plan["action"] == "google.calendar.import_plan"
    assert plan["success"] is False
    assert plan["data"]["observation_count"] == 0
    assert plan["data"]["import_policy"] == {}
    assert plan["data"]["import_draft"] == {}
    assert plan["data"]["policy_skipped_reason"] == "no_calendar_observations"
    assert plan["data"]["policy_receipt_id"] == ""


def test_google_calendar_operator_import_preserves_event_time(monkeypatch) -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    captured: list[Any] = []

    @dataclass(frozen=True)
    class FakeOutcome:
        rejected: tuple[Any, ...] = ()

    class FakePool:
        async def admit(self, observations):
            captured.extend(observations)
            return FakeOutcome()

    monkeypatch.setattr(
        "parrot.dsg.l1_5.pool.get_l1_5_pool",
        lambda: FakePool(),
    )

    body = client.post(
        "/api/google/calendar/import",
        json={
            "dry_run": False,
            "operator_mode": True,
            "events": [
                {
                    "id": "evt_import_time",
                    "calendar_id": "primary",
                    "summary": "Calendar import keeps time",
                    "start": {
                        "dateTime": "2026-05-15T11:00:00+08:00",
                        "timeZone": "Asia/Shanghai",
                    },
                    "end": {
                        "dateTime": "2026-05-15T11:30:00+08:00",
                        "timeZone": "Asia/Shanghai",
                    },
                }
            ],
        },
    ).json()

    assert body["action"] == "google.calendar.import"
    assert body["success"] is True
    assert body["dry_run"] is False
    assert body["operator_mode"] is True
    assert captured
    observation = captured[0]
    assert observation.meta["calendar_event_id"] == "evt_import_time"
    assert observation.time_span[0] == observation.observed_at
    assert observation.time_span[1] is not None
    assert observation.time_span[1] > observation.time_span[0]


def test_runtime_monitor_route_is_web_only_read_surface() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    body = client.get("/api/runtime/monitor").json()

    assert body["audit"]["read_only"] is True
    assert body["audit"]["web_only"] is True
    assert body["agent_team"]["agent_team_id"] == "catmaid-team-v1"
    assert body["scheduler"]["channels"]["commands"] == "parrot.scheduler.commands"
    assert "research" in body["scheduler"]["nanobot_task_types"]["all"]
    assert body["nanobot"]["dispatch_stream"] == "parrot.nanobot.dispatch"
    assert [stage["stage"] for stage in body["collaboration"]["channel_flow"]] == [
        "scheduler_commands",
        "nanobot_dispatch",
        "nanobot_worker",
        "nanobot_results",
        "brain_return",
    ]
    assert body["collaboration"]["channel_flow"][0]["channel"] == "parrot.scheduler.commands"
    assert "secret" not in str(body).lower()


def test_runtime_flow_typed_models_preserve_route_wire_shape() -> None:
    from parrot.web_console.runtime_flow_models import (
        RuntimeFlowChanges,
        RuntimeFlowEdge,
        RuntimeFlowEvent,
        RuntimeFlowNode,
        RuntimeFlowSnapshot,
        RuntimeHumanGate,
        RuntimeReceipt,
    )

    node = RuntimeFlowNode(
        id="plan:p1",
        lane="plan",
        entity_kind="plan",
        entity_id="p1",
        trace_id="plan:p1",
        label="Plan",
        status="awaiting_user_confirmation",
        summary="1 step",
        payload_ref="ref:p1",
    ).as_json()
    edge = RuntimeFlowEdge(
        id="plan:p1->gate:plan:p1:awaits_human",
        source="plan:p1",
        target="gate:plan:p1",
        kind="awaits_human",
        trace_id="plan:p1",
    ).as_json()
    event = RuntimeFlowEvent(
        sequence=7,
        trace_id="plan:p1",
        span_id="7:plan:p1:awaiting_user_confirmation",
        parent_span_id="",
        entity_kind="plan",
        entity_id="p1",
        op="awaiting_user_confirmation",
        status="awaiting_user_confirmation",
        event_source="web_console.runtime_flow",
        writer="read_model",
        summary="Plan",
        created_at=1.0,
        payload_ref="ref:p1",
    ).as_json()
    gate = RuntimeHumanGate(
        gate_id="plan:p1",
        target_kind="plan",
        target_id="p1",
        trace_id="plan:p1",
        state="pending",
        plan_state="awaiting_user_confirmation",
        prompt="Approve?",
        summary="Plan",
        options=["approve", "approve_and_start"],
        valid_actions_for_state=["approve", "approve_and_start"],
        payload_ref="ref:p1",
    ).as_json()
    audit = {
        "web_only": True,
        "read_model": True,
        "typed_schema": "parrot.web_console.runtime_flow_models",
    }
    snapshot = RuntimeFlowSnapshot(
        sequence=7,
        generated_at=1.0,
        lanes=[{"id": "plan", "label": "Plan"}],
        nodes=[node],
        edges=[edge],
        events=[event],
        pending_human_gates=[gate],
        source_sequences={"live_state": 1},
        audit=audit,
    ).as_json()
    changes = RuntimeFlowChanges(
        since=6,
        sequence=7,
        changed=True,
        events=[event],
        snapshot=snapshot,
        audit=audit,
    ).as_json()
    receipt = RuntimeReceipt(
        action="runtime.hitl.draft_decision",
        success=True,
        dry_run=True,
        operator_mode=False,
        receipt_id="web-test",
        data={"gate_id": "plan:p1"},
        audit={"web_only": True, "core_candidate": "CORE-011"},
    ).as_json()

    assert node["id"] == "plan:p1"
    assert edge["source"] == "plan:p1"
    assert edge["target"] == "gate:plan:p1"
    assert event["source"] == "web_console.runtime_flow"
    assert "event_source" not in event
    assert gate["options"] == gate["valid_actions_for_state"]
    assert snapshot["action"] == "runtime.flow.snapshot"
    assert snapshot["pending_human_gates"][0]["target_kind"] == "plan"
    assert changes["event_schema"] == "runtime_flow_delta_v1"
    assert changes["snapshot"]["sequence"] == 7
    assert receipt["core_candidate"] == "CORE-011"


def test_runtime_flow_and_hitl_routes_are_web_only_receipt_surfaces(monkeypatch) -> None:
    import asyncio

    from parrot.brain.intent_workspace import IntentWorkspace, set_intent_workspace_for_test
    from parrot.brain.plan import (
        PlanProposal,
        PlanRegistry,
        PlanStepProposal,
        set_plan_registry_for_test,
    )

    monkeypatch.setenv("PARROT_ORCH_SECRET", "runtime-flow-secret")
    set_intent_workspace_for_test(IntentWorkspace())
    registry = PlanRegistry(dispatch_task=_fake_plan_dispatch)
    set_plan_registry_for_test(registry)
    try:
        plan = asyncio.run(registry.draft(PlanProposal(
            proposed_by="test",
            title="Runtime HITL test plan",
            suggested_steps=(
                PlanStepProposal(
                    step_id="s1",
                    title="Check messages",
                    expected_tool="message_check",
                ),
                PlanStepProposal(
                    step_id="s2",
                    title="Summarize messages",
                    expected_tool="summarize",
                    depends_on=("s1", "s1"),
                ),
            ),
        )))
        asyncio.run(registry.submit_for_confirmation(plan.plan_id))

        client = TestClient(build_app(status_fetcher=_fake_fetcher))
        flow = client.get("/api/runtime/flow").json()
        changes = client.get("/api/runtime/flow/changes?since=0").json()
        no_change = client.get(f"/api/runtime/flow/changes?since={flow['sequence']}").json()
        pending = client.get("/api/runtime/hitl/pending").json()
        draft = client.post(
            "/api/runtime/hitl/draft-decision",
            json={"gate_id": f"plan:{plan.plan_id}", "decision": "approve"},
        ).json()
        missing_plan_draft = client.post(
            "/api/runtime/hitl/draft-decision",
            json={"gate_id": "plan:missing", "decision": "approve"},
        ).json()
        unsupported_target_draft = client.post(
            "/api/runtime/hitl/draft-decision",
            json={"gate_id": "trigger:manual_llm_push", "decision": "approve"},
        ).json()
        dry_apply = client.post(
            "/api/runtime/hitl/apply-decision",
            json={
                "gate_id": f"plan:{plan.plan_id}",
                "decision": "approve_and_start",
                "dry_run": True,
                "operator_mode": False,
            },
        ).json()

        assert flow["success"] is True
        assert flow["audit"]["web_only"] is True
        assert "CORE-010" in flow["audit"]["shared_core_candidates"]
        assert any(lane["id"] == "human_gate" for lane in flow["lanes"])
        assert any(gate["target_id"] == plan.plan_id for gate in flow["pending_human_gates"])
        node_ids = {node["id"] for node in flow["nodes"]}
        edge_ids = [edge["id"] for edge in flow["edges"]]
        assert len(edge_ids) == len(set(edge_ids))
        assert all(edge["source"] in node_ids and edge["target"] in node_ids for edge in flow["edges"])
        assert any(node.get("trace_id") == f"plan:{plan.plan_id}" for node in flow["nodes"])
        assert flow["audit"]["typed_schema"] == "parrot.web_console.runtime_flow_models"
        assert flow["audit"]["event_schema"] == "runtime_flow_delta_v1"
        assert changes["event_schema"] == "runtime_flow_delta_v1"
        assert changes["changed"] is True
        assert no_change["changed"] is False
        assert no_change["snapshot"] is None
        assert pending["gates"][0]["gate_id"] == f"plan:{plan.plan_id}"
        assert pending["gates"][0]["plan_state"] == "awaiting_user_confirmation"
        assert pending["gates"][0]["options"] == pending["gates"][0]["valid_actions_for_state"]
        assert pending["gates"][0]["operator_required_for_execute"] is True
        assert draft["success"] is True
        assert draft["core_candidate"] == "CORE-011"
        assert draft["data"]["operator_required_for_execute"] is True
        assert missing_plan_draft["success"] is False
        assert missing_plan_draft["data"]["error"] == "plan_not_found"
        assert unsupported_target_draft["success"] is False
        assert unsupported_target_draft["data"]["error"] == "unsupported_hitl_target"
        assert unsupported_target_draft["data"]["target_kind"] == "trigger"
        assert unsupported_target_draft["data"]["valid_actions"] == []
        assert unsupported_target_draft["data"]["valid_actions_for_state"] == []
        assert unsupported_target_draft["data"]["valid_target_kinds"] == ["plan"]
        assert dry_apply["data"]["would_apply"] is True
        assert dry_apply["data"]["apply_skipped_reason"] == "dry_run_or_operator_mode_missing"
        assert "runtime-flow-secret" not in str(flow) + str(changes) + str(pending)
    finally:
        set_plan_registry_for_test(None)
        set_intent_workspace_for_test(None)


def test_runtime_flow_sse_stream_uses_delta_schema() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    with client.stream(
        "GET",
        "/api/runtime/flow/stream",
        params={"since": 0, "max_events": 1, "interval_s": 0.25},
    ) as response:
        body = "".join(response.iter_text())

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: stream_open" in body
    assert "event: runtime_delta" in body
    assert "runtime_flow_delta_v1" in body
    assert "receipt_stream" in body


def test_memory_live_state_changes_uses_stable_web_sequence(monkeypatch) -> None:
    import parrot.brain.app_live_state as app_live_state_module
    import parrot.dsg.l2b_graph as l2b_graph_module
    import parrot.web_console.memory_live_state as memory_live_state_module
    from parrot.dsg.l2b_graph import L2BGraph
    from parrot.dsg.l2b_types import NodeKind, SemanticNode

    graph = L2BGraph()
    l2b_graph_module._instance = graph
    app_live_state_module._sequence = 0
    monkeypatch.setattr(memory_live_state_module, "_memory_sequence", 0)
    monkeypatch.setattr(memory_live_state_module, "_memory_signature", "")

    try:
        client = TestClient(build_app(status_fetcher=_fake_fetcher))
        first = client.get("/api/memory/live-state/changes", params={"since": 0}).json()
        second = client.get(
            "/api/memory/live-state/changes",
            params={"since": first["sequence"]},
        ).json()

        graph.upsert_node(SemanticNode(
            uuid="memory_change_node",
            kind=NodeKind.OBJECT,
            label="Memory changed",
        ))
        third = client.get(
            "/api/memory/live-state/changes",
            params={"since": first["sequence"]},
        ).json()

        assert first["action"] == "memory.live_state.changes"
        assert first["event_schema"] == "memory_runtime_delta_v1"
        assert first["changed"] is True
        assert first["snapshot"]["l2b"]["node_count"] == 0
        assert first["audit"]["web_only"] is True
        assert first["audit"]["app_dto_pollution"] is False
        assert second["sequence"] == first["sequence"]
        assert second["changed"] is False
        assert second["snapshot"] is None
        assert third["sequence"] > first["sequence"]
        assert third["changed"] is True
        assert third["snapshot"]["l2b"]["node_count"] == 1
        assert third["events"][0]["event_schema"] == "memory_runtime_delta_v1"
        assert third["events"][0]["event_id"]
        assert third["events"][0]["redacted"] is True
        assert any(event["entity_kind"] == "l2b_node" for event in third["events"])
    finally:
        l2b_graph_module._instance = None
        app_live_state_module._sequence = 0
        memory_live_state_module._memory_sequence = 0
        memory_live_state_module._memory_signature = ""


def test_memory_live_state_sse_stream_uses_delta_schema(monkeypatch) -> None:
    import parrot.brain.app_live_state as app_live_state_module
    import parrot.web_console.memory_live_state as memory_live_state_module

    app_live_state_module._sequence = 0
    monkeypatch.setattr(memory_live_state_module, "_memory_sequence", 0)
    monkeypatch.setattr(memory_live_state_module, "_memory_signature", "")

    try:
        client = TestClient(build_app(status_fetcher=_fake_fetcher))
        with client.stream(
            "GET",
            "/api/memory/live-state/stream",
            params={"since": 0, "max_events": 1, "interval_s": 0.25},
        ) as response:
            body = "".join(response.iter_text())

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        assert "event: stream_open" in body
        assert "event: memory_delta" in body
        assert "memory_runtime_delta_v1" in body
        assert "receipt_stream" in body
    finally:
        app_live_state_module._sequence = 0
        memory_live_state_module._memory_sequence = 0
        memory_live_state_module._memory_signature = ""


def test_runtime_hitl_draft_validates_plan_state() -> None:
    import asyncio

    from parrot.brain.intent_workspace import IntentWorkspace, set_intent_workspace_for_test
    from parrot.brain.plan import (
        PlanProposal,
        PlanRegistry,
        PlanStepProposal,
        set_plan_registry_for_test,
    )

    set_intent_workspace_for_test(IntentWorkspace())
    registry = PlanRegistry(dispatch_task=_fake_plan_dispatch)
    set_plan_registry_for_test(registry)
    try:
        plan = asyncio.run(registry.draft(PlanProposal(
            proposed_by="test",
            title="Approved plan",
            suggested_steps=(PlanStepProposal(
                step_id="s1",
                title="Check messages",
                expected_tool="message_check",
            ),),
        )))
        asyncio.run(registry.submit_for_confirmation(plan.plan_id))
        asyncio.run(registry.approve(plan.plan_id))

        empty_plan = asyncio.run(registry.draft(PlanProposal(
            proposed_by="test",
            title="Empty complete plan",
            suggested_steps=(),
        )))
        asyncio.run(registry.submit_for_confirmation(empty_plan.plan_id))
        asyncio.run(registry.approve(empty_plan.plan_id))
        asyncio.run(registry.start_executing(empty_plan.plan_id))

        client = TestClient(build_app(status_fetcher=_fake_fetcher))
        stale_approve = client.post(
            "/api/runtime/hitl/draft-decision",
            json={"gate_id": f"plan:{plan.plan_id}", "decision": "approve"},
        ).json()
        start_draft = client.post(
            "/api/runtime/hitl/draft-decision",
            json={"gate_id": f"plan:{plan.plan_id}", "decision": "approve_and_start"},
        ).json()
        completed_cancel = client.post(
            "/api/runtime/hitl/draft-decision",
            json={"gate_id": f"plan:{empty_plan.plan_id}", "decision": "cancel"},
        ).json()

        assert stale_approve["success"] is False
        assert stale_approve["data"]["error"] == "invalid_plan_state"
        assert stale_approve["data"]["plan_state"] == "approved"
        assert "approve_and_start" in stale_approve["data"]["valid_actions_for_state"]
        assert start_draft["success"] is True
        assert completed_cancel["success"] is False
        assert completed_cancel["data"]["error"] == "invalid_plan_state"
        assert completed_cancel["data"]["plan_state"] == "complete"
    finally:
        set_plan_registry_for_test(None)
        set_intent_workspace_for_test(None)


def test_blackboard_activity_route_returns_bounded_summaries() -> None:
    import py_trees

    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    py_trees.blackboard.Blackboard.activity_stream = None
    try:
        py_trees.blackboard.Blackboard.enable_activity_stream()
        bb = py_trees.blackboard.Client(name="web_activity_test")
        bb.register_key(key="global/web_activity_test", access=py_trees.common.Access.WRITE)
        bb.set("global/web_activity_test", {"status": "ok", "secret": "summary-only"})

        client = TestClient(build_app(status_fetcher=_fake_fetcher))
        body = client.get("/api/memory/blackboard/activity?limit=5").json()

        assert body["success"] is True
        assert body["action"] == "blackboard.activity"
        assert body["audit"]["web_only"] is True
        assert body["audit"]["values"] == "summaries_only"
        assert body["data"]["limit"] == 5
        assert body["data"]["activities"]
        row = body["data"]["activities"][-1]
        assert row["key"] == "global/web_activity_test"
        assert row["scope"] == "global"
        assert row["client_name"] == "web_activity_test"
        assert row["current_summary"].startswith("dict(")
        assert "summary-only" not in str(body)
        assert "secret" not in str(body).lower()
    finally:
        py_trees.blackboard.Blackboard.storage = {}
        py_trees.blackboard.Blackboard.metadata = {}
        py_trees.blackboard.Blackboard.activity_stream = None


def test_runtime_monitor_plan_rows_include_dag_edges() -> None:
    from parrot.web_console.runtime_monitor import _plan_row

    plan = SimpleNamespace(
        plan_id="plan_a",
        title="Test Plan",
        state="executing",
        intent_event_id="intent_a",
        episode_id="episode_a",
        related_node_uuids=("node_a",),
        related_staged_ref_ids=("ref_a",),
        staged_ref_id="plan_ref",
        blackboard_namespace="plan/plan_a",
        blocks_conversation=False,
        drafted_at=10.0,
        approved_at=11.0,
        started_executing_at=12.0,
        completed_at=0.0,
        supersedes="",
        superseded_by="",
        steps=[
            SimpleNamespace(
                step_id="step_a",
                title="Fetch mail",
                description="",
                expected_tool="message_check",
                state="done",
                depends_on=(),
                nanobot_task_id="task_a",
                started_at=12.0,
                completed_at=13.0,
                result_summary="ok",
                result_ref_id="result_a",
                error="",
            ),
            SimpleNamespace(
                step_id="step_b",
                title="Summarize",
                description="",
                expected_tool="summarize",
                state="pending",
                depends_on=("step_a",),
                nanobot_task_id="",
                started_at=0.0,
                completed_at=0.0,
                result_summary="",
                result_ref_id="",
                error="",
            ),
        ],
    )

    row = _plan_row(plan)

    assert row["related_node_uuids"] == ["node_a"]
    assert row["steps"][1]["depends_on"] == ["step_a"]
    assert row["steps"][0]["result_ref_id"] == "result_a"
    assert row["dag"]["edges"] == [
        {"source": "step_a", "target": "step_b", "kind": "depends_on"}
    ]
    assert row["dag"]["ready_step_ids"] == ["step_b"]
    assert row["dag"]["blocked_step_ids"] == []
    assert row["dag"]["critical_step_ids"] == ["step_a", "step_b"]


def test_dsg_trigger_management_routes_are_dry_run_and_secret_safe(monkeypatch) -> None:
    monkeypatch.setenv("PARROT_ORCH_SECRET", "route-secret")
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    catalog = client.get("/api/dsg/triggers/catalog").json()
    draft = client.post(
        "/api/dsg/triggers/draft-event",
        json={
            "trigger_name": "message_notification",
            "event": {"type": "message_push", "subject": "hello"},
        },
    ).json()
    dry_fire = client.post(
        "/api/dsg/triggers/fire-event",
        json={
            "trigger_name": "message_notification",
            "event": {"type": "message_push", "subject": "hello"},
            "dry_run": True,
            "operator_mode": False,
        },
    ).json()
    on_demand_draft = client.post(
        "/api/dsg/triggers/draft-event",
        json={"event": {"kind": "scene_switch", "new_scene_type": "desktop_webcam"}},
    ).json()

    assert catalog["success"] is True
    assert "message_notification" in {item["name"] for item in catalog["triggers"]}
    assert len(catalog["taxonomy"]["dimensions"]["ascending_channel"]) >= 4
    assert {
        "external_inbox",
        "scheduled_poll",
        "perception_scene",
        "operator_mode",
    } <= {row["id"] for row in catalog["taxonomy"]["dimensions"]["ascending_channel"]}
    message_meta = next(
        item for item in catalog["triggers"] if item["name"] == "message_notification"
    )
    assert "external_inbox" in message_meta["ascending_channels"]
    assert "google_message" in message_meta["interaction_modules"]
    assert "google_message" in message_meta["information_tags"]
    assert any(
        row["id"] == "external_inbox" and "message_notification" in row["trigger_names"]
        for row in catalog["groups"]["ascending_channel"]
    )
    assert draft["dry_run"] is True
    assert draft["data"]["matched_triggers"] == ["message_notification"]
    assert dry_fire["data"]["would_publish"] is True
    assert dry_fire["data"]["publish_skipped_reason"] == "dry_run_or_operator_mode_missing"
    assert on_demand_draft["data"]["matched_triggers"] == ["scene_switch"]
    assert "route-secret" not in str(catalog) + str(draft) + str(dry_fire)


def test_l15_pool_route_and_operator_drafts_are_exposed() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    pool = client.get("/api/l15/pool").json()
    bucket_draft = client.post(
        "/api/l15/bucket-op/draft",
        json={"op": "freeze", "kind": "main"},
    ).json()
    bucket_apply_dry_run = client.post(
        "/api/l15/bucket-op",
        json={"op": "clear", "kind": "main", "dry_run": True, "operator_mode": False},
    ).json()
    daily_obsidian = client.post(
        "/api/l15/obsidian-node/draft",
        json={
            "profile": "daily",
            "label": "UUID free setting",
            "description": "No Obsidian UUID is required for daily settings.",
        },
    ).json()
    ref_obsidian = client.post(
        "/api/l15/obsidian-node/draft",
        json={"profile": "ref", "label": "Missing UUID ref"},
    ).json()
    blank_label_obsidian = client.post(
        "/api/l15/obsidian-node/draft",
        json={"profile": "daily", "label": "   "},
    ).json()

    assert pool["success"] is True
    assert "main" in {item["kind"] for item in pool["buckets"]}
    assert pool["audit"]["web_only"] is True
    assert bucket_draft["data"]["bucket_op"]["op"] == "freeze"
    assert bucket_apply_dry_run["action"] == "l15.bucket_op.apply"
    assert bucket_apply_dry_run["data"]["would_apply"] is True
    assert bucket_apply_dry_run["data"]["apply_skipped_reason"] == "dry_run_or_operator_mode_missing"
    assert daily_obsidian["success"] is True
    assert daily_obsidian["data"]["uuid_free_allowed"] is True
    blank_payload = blank_label_obsidian["data"]["event"]["payload"]
    assert blank_payload["label"] == "Web Console setting"
    assert blank_payload["obsidian_note_key"] == "web-console/daily/Web Console setting"
    assert ref_obsidian["success"] is False
    assert ref_obsidian["data"]["error"] == "ref_profile_requires_obsidian_uuid"


def test_l2b_node_and_edge_routes_stay_dry_run_by_default() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    node = client.post(
        "/api/l2b/node",
        json={"label": "Web Test Node", "kind": "object", "description": "draft only"},
    ).json()
    update = client.post(
        "/api/l2b/node",
        json={
            "node_uuid": "node_a",
            "label": "Updated Web Test Node",
            "kind": "object",
            "description": "update draft only",
        },
    ).json()
    delete = client.post("/api/l2b/node/delete", json={"node_uuid": "node_a"}).json()
    edge = client.post(
        "/api/l2b/edge",
        json={
            "from_uuid": "node_a",
            "to_uuid": "node_b",
            "kind": "associated_with",
            "strength": 0.7,
            "meta": {"tag": "web_test"},
        },
    ).json()
    edge_update = client.post(
        "/api/l2b/edge/update",
        json={
            "from_uuid": "node_a",
            "to_uuid": "node_b",
            "kind": "reminds_of",
            "match_kind": "associated_with",
            "strength": 0.9,
            "meta": {"reason": "operator_preview"},
        },
    ).json()
    edge_delete = client.post(
        "/api/l2b/edge/delete",
        json={"from_uuid": "node_a", "to_uuid": "node_b", "match_kind": "associated_with"},
    ).json()
    self_edge = client.post(
        "/api/l2b/edge/draft",
        json={"from_uuid": "node_a", "to_uuid": "node_a", "kind": "associated_with"},
    ).json()

    assert node["success"] is True
    assert node["dry_run"] is True
    assert node["data"]["would_apply"] is True
    assert node["data"]["write_path"] == "L15Pool.admit(Observation(source=USER_EXPLICIT))"
    assert update["data"]["would_apply"] is True
    assert update["data"]["observation"]["meta"]["target_node_uuid"] == "node_a"
    assert delete["data"]["would_evict"] is True
    assert edge["data"]["would_apply"] is True
    assert edge["data"]["apply_skipped_reason"] == "dry_run_or_operator_mode_missing"
    assert edge["data"]["operator_required_for_execute"] is True
    assert edge["data"]["edge"]["kind"] == "associated_with"
    assert edge["data"]["edge"]["strength"] == 0.7
    assert edge["data"]["edge"]["meta"]["tag"] == "web_test"
    assert edge_update["data"]["would_apply"] is True
    assert edge_update["data"]["edge"]["kind"] == "reminds_of"
    assert edge_update["data"]["match_kind"] == "associated_with"
    assert edge_delete["data"]["would_delete"] is True
    assert edge_delete["data"]["match_kind"] == "associated_with"
    assert self_edge["success"] is False
    assert self_edge["data"]["error"] == "self_edge_not_allowed"


def test_l2b_graph_policy_draft_routes_are_core013_and_dry_run() -> None:
    from parrot.web_console.graph_policy import (
        GraphDeltaEntityKind,
        GraphDeltaEvent,
        GraphDeltaOp,
    )

    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    import_draft = client.post(
        "/api/l2b/graph-policy/import-draft",
        json={
            "source_kind": "graphiti",
            "source_id": "arknights_test",
            "destination": "isolated_compartment",
            "node_uuids": ["node_a", "node_b"],
            "ref_ids": ["ref_a"],
            "subgraph_label": "Arknights test slice",
            "proposed_edges": [
                {
                    "source": "node_a",
                    "target": "node_b",
                    "kind": "graphiti_fact",
                    "source_graphiti_uuid": "source-amiya",
                    "target_graphiti_uuid": "target-chernobog",
                    "label": "Amiya reaches Chernobog",
                    "edge_source": "graphiti",
                }
            ],
        },
    ).json()
    invalid_import = client.post(
        "/api/l2b/graph-policy/import-draft",
        json={"destination": "whole_graph_magic"},
    ).json()
    subgraph = client.post(
        "/api/l2b/subgraphs/draft",
        json={"label": "Work selection", "node_uuids": ["node_a", "node_b"]},
    ).json()
    transform = client.post(
        "/api/l2b/transforms/draft",
        json={
            "transform_kind": "wrap_selection",
            "node_uuids": ["node_a", "node_b"],
            "label": "Wrapped work selection",
        },
    ).json()
    graphiti_projection = client.post(
        "/api/l2b/transforms/draft",
        json={
            "transform_kind": "graphiti_bundle_projection",
            "graphiti_bundle": {
                "bundle_kind": "graphiti_search_subgraph_bundle",
                "partition": "arknights_test",
                "query": "Amiya Chernobog",
                "sections": {
                    "facts": [
                        {
                            "kind": "graphiti_fact",
                            "uuid": "fact-a",
                            "raw": {
                                "uuid": "fact-a",
                                "fact": "Amiya protects Rhodes Island.",
                                "source_node": {"uuid": "node-amiya", "name": "Amiya"},
                                "target_node": {"uuid": "node-rhodes", "name": "Rhodes Island"},
                            },
                            "source_envelope": {
                                "uuid": "fact-a",
                                "source_node_uuid": "node-amiya",
                                "target_node_uuid": "node-rhodes",
                                "episode_uuids": ["episode-a"],
                            },
                        }
                    ],
                    "entities": [],
                    "episodes": [],
                    "communities": [],
                },
            },
        },
    ).json()
    llm_context = client.post(
        "/api/l2b/transforms/draft",
        json={"transform_kind": "send_context_to_llm", "node_uuids": ["node_a"]},
    ).json()

    assert import_draft["action"] == "l2b.graph_policy.import_draft"
    assert import_draft["dry_run"] is True
    assert import_draft["data"]["core_candidate"] == "CORE-013"
    assert import_draft["data"]["audit"]["app_dto_pollution"] is False
    assert import_draft["data"]["policy"]["destination"] == "isolated_compartment"
    assert import_draft["data"]["policy"]["would_mutate_l2b_topology"] is True
    assert import_draft["data"]["draft"]["proposed_overlay"]["overlay_kind"] == "isolated_compartment"
    assert import_draft["data"]["draft"]["proposed_edges"][0]["edge_source"] == "graphiti"
    assert (
        import_draft["data"]["draft"]["proposed_edges"][0]["meta"]["source_graphiti_uuid"]
        == "source-amiya"
    )
    assert (
        import_draft["data"]["draft"]["proposed_edges"][0]["meta"]["target_graphiti_uuid"]
        == "target-chernobog"
    )
    assert import_draft["data"]["apply_route"] == ""
    assert invalid_import["success"] is False
    assert invalid_import["data"]["error"] == "invalid_import_destination"
    assert "connect_by_rule" in invalid_import["data"]["valid_destinations"]
    assert subgraph["action"] == "l2b.subgraph.draft"
    assert subgraph["data"]["overlay"]["label"] == "Work selection"
    assert subgraph["data"]["overlay"]["member_node_uuids"] == ["node_a", "node_b"]
    assert transform["action"] == "l2b.transform.draft"
    assert transform["data"]["draft"]["transform_kind"] == "wrap_selection"
    assert transform["data"]["draft"]["proposed_overlay"]["label"] == "Wrapped work selection"
    assert graphiti_projection["success"] is True
    assert graphiti_projection["data"]["transform_kind"] == "graphiti_bundle_projection"
    assert graphiti_projection["data"]["l2b_edges"][0]["kind"] == "graphiti_fact"
    assert graphiti_projection["data"]["l2b_nodes"][0]["is_pointer"] is True
    assert graphiti_projection["data"]["rustworkx_preview"]["rwx_idx_policy"] == "ephemeral_do_not_persist"
    assert graphiti_projection["data"]["policies"]["direct_l2b_write"] is False
    assert llm_context["data"]["draft"]["requires_operator"] is False
    assert llm_context["data"]["operator_required_for_apply"] is False
    delta = GraphDeltaEvent(
        sequence=1,
        entity_kind=GraphDeltaEntityKind.GRAPH_OVERLAY.value,
        entity_id="overlay_a",
        op=GraphDeltaOp.OVERLAY_CREATE.value,
        overlay_id="overlay_a",
        patch={"label": "Work selection"},
    )
    assert delta.graph_scope == "memory_graph"
    assert delta.redacted is True


def test_l2b_graph_health_route_is_read_only(monkeypatch) -> None:
    import parrot.dsg.l2b_graph as l2b_graph_module
    from parrot.dsg.l2b_graph import L2BGraph
    from parrot.dsg.l2b_types import EdgeKind, NodeKind, SemanticEdge, SemanticNode

    graph = L2BGraph()
    graph.upsert_node(
        SemanticNode(
            uuid="health_a",
            kind=NodeKind.OBJECT,
            label="A",
            graphiti_uuid="node-graphiti-1",
            obsidian_uuid="node-obsidian-1",
            category="operator_fixture",
            known_facts=["A came from a Graphiti canary."],
            typical_location="desk",
            provenance_stream_id="web:graphiti:arknights_test:node-graphiti-1",
            reference_image_path="data/snapshots/objects/health_a/reference.jpg",
            last_sighting_path="data/snapshots/sightings/2026-05-17/health_a.jpg",
        )
    )
    graph.upsert_node(SemanticNode(uuid="health_b", kind=NodeKind.EVENT, label="B"))
    graph.upsert_node(SemanticNode(uuid="health_c", kind=NodeKind.PHOTO, label="C"))
    graph.connect(
        "health_a",
        "health_b",
        SemanticEdge(
            kind=EdgeKind.GRAPHITI_FACT,
            source="graphiti",
            graphiti_uuid="fact-graphiti-1",
            source_graphiti_uuid="source-graphiti-1",
            target_graphiti_uuid="target-graphiti-1",
            ref_ids=("ref-graphiti-1",),
        ),
    )
    monkeypatch.setattr(l2b_graph_module, "_instance", graph)

    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    health = client.get("/api/l2b/analysis/health").json()
    live_state = client.get("/api/app/live-state").json()

    assert health["action"] == "l2b.analysis.health"
    assert health["success"] is True
    assert health["read_only"] is True
    assert health["core_candidate"] == "CORE-013"
    assert health["node_count"] == 3
    assert health["edge_count"] == 1
    assert health["orphan_count"] == 1
    assert health["wcc_count"] == 2
    assert health["largest_wcc_size"] == 2
    assert health["kind_counts"]["object"] == 1
    assert health["audit"]["unity_dto_pollution"] is False
    node = next(item for item in live_state["l2b"]["nodes"] if item["uuid"] == "health_a")
    assert node["graphiti_uuid"] == "node-graphiti-1"
    assert node["obsidian_uuid"] == "node-obsidian-1"
    assert node["known_facts"] == ["A came from a Graphiti canary."]
    assert node["typical_location"] == "desk"
    assert node["provenance_stream_id"] == "web:graphiti:arknights_test:node-graphiti-1"
    assert node["reference_image_path"] == "data/snapshots/objects/health_a/reference.jpg"
    assert node["last_sighting_path"] == "data/snapshots/sightings/2026-05-17/health_a.jpg"
    edge = live_state["l2b"]["edges"][0]
    assert edge["kind"] == "graphiti_fact"
    assert edge["edge_source"] == "graphiti"
    assert edge["view_classes"] == ["graphiti", "semantic"]
    assert edge["graphiti_uuid"] == "fact-graphiti-1"
    assert edge["source_graphiti_uuid"] == "source-graphiti-1"
    assert edge["target_graphiti_uuid"] == "target-graphiti-1"
    assert edge["ref_ids"] == ["ref-graphiti-1"]
    assert edge["meta"]["view_classes"] == ["graphiti", "semantic"]


def test_l2b_subgraph_context_reads_live_l2b_without_rwx_index(monkeypatch) -> None:
    import parrot.dsg.l2b_graph as l2b_graph_module
    from parrot.dsg.l2b_graph import L2BGraph
    from parrot.dsg.l2b_types import EdgeKind, NodeKind, SemanticEdge, SemanticNode

    graph = L2BGraph()
    graph.upsert_node(
        SemanticNode(
            uuid="ctx_a",
            kind=NodeKind.OBJECT,
            label="Etiquette bell",
            graphiti_uuid="graphiti-node-a",
            obsidian_uuid="obsidian-node-a",
            known_facts=["Bell placement marks a formal greeting ritual."],
            reference_image_path="data/snapshots/objects/ctx_a/reference.jpg",
            provenance_stream_id="web:graphiti:etiquette:graphiti-node-a",
        )
    )
    graph.upsert_node(SemanticNode(uuid="ctx_b", kind=NodeKind.EVENT, label="Greeting lesson"))
    graph.upsert_node(SemanticNode(uuid="ctx_c", kind=NodeKind.PHOTO, label="Unselected photo"))
    graph.connect(
        "ctx_a",
        "ctx_b",
        SemanticEdge(
            kind=EdgeKind.GRAPHITI_FACT,
            source="graphiti",
            graphiti_uuid="graphiti-fact-a",
            source_graphiti_uuid="graphiti-node-a",
            target_graphiti_uuid="graphiti-node-b",
            ref_ids=("ref-etiquette-page-1",),
            meta={"graphiti_raw": {"fact": "The bell is used before the formal greeting."}},
        ),
    )
    monkeypatch.setattr(l2b_graph_module, "_instance", graph)

    try:
        client = TestClient(build_app(status_fetcher=_fake_fetcher))
        body = client.post(
            "/api/l2b/subgraphs/context",
            json={
                "label": "Etiquette context",
                "node_uuids": [
                    "ctx_a",
                    "missing_ctx",
                    "graphiti:noble_etiquette:entity:preview",
                ],
                "depth": 1,
                "dry_run": False,
                "operator_mode": True,
            },
        ).json()

        assert body["action"] == "l2b.subgraph.context"
        assert body["success"] is True
        assert body["dry_run"] is True
        assert body["operator_mode"] is False
        assert body["data"]["requested_execution"] == {
            "dry_run": False,
            "operator_mode": True,
            "ignored_for_context": True,
        }
        assert body["data"]["true_connection"]["used_live_l2b_graph"] is True
        assert body["data"]["true_connection"]["source"] == "parrot.dsg.l2b_graph.get_l2b_graph"
        assert body["data"]["true_connection"]["rwx_idx_exposed"] is False
        assert body["data"]["missing_node_uuids"] == [
            "missing_ctx",
            "graphiti:noble_etiquette:entity:preview",
        ]
        assert body["data"]["missing_graphiti_preview_node_uuids"] == [
            "graphiti:noble_etiquette:entity:preview"
        ]
        assert body["data"]["context_lookup_hint"] == "graphiti_preview_uuid_requires_l2b_materialization"
        assert body["data"]["policies"]["materialized_l2b_uuid_required"] is True
        assert body["data"]["selected_node_uuids"] == ["ctx_a"]
        assert {row["uuid"] for row in body["data"]["nodes"]} == {"ctx_a", "ctx_b"}
        assert body["data"]["nodes"][0]["graphiti_uuid"] == "graphiti-node-a"
        assert body["data"]["nodes"][0]["refs"]["reference_image_path"].endswith("reference.jpg")
        assert body["data"]["edges"][0]["graphiti_uuid"] == "graphiti-fact-a"
        assert body["data"]["edges"][0]["ref_ids"] == ["ref-etiquette-page-1"]
        assert body["data"]["edges"][0]["meta"]["graphiti_raw"]["fact"].startswith("The bell")
        assert body["data"]["clusters"][0]["selected_member_uuids"] == ["ctx_a"]
        assert body["data"]["overlay"]["overlay_kind"] == "live_l2b_ego_subgraph"
        assert body["data"]["overlay"]["member_ref_ids"] == ["ref-etiquette-page-1"]
        assert "_rx_index" not in str(body)
    finally:
        l2b_graph_module._instance = None


def test_google_message_routes_use_nanobot_and_trigger_drafts() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    check = client.post("/api/google/messages/check", json={}).json()
    push = client.post(
        "/api/google/messages/push-test",
        json={"subject": "mail test", "dry_run": True},
    ).json()

    assert check["action"] == "google.message_check.dispatch"
    assert check["data"]["task_type"] == "message_check"
    assert check["data"]["would_dispatch"] is True
    assert push["action"] == "dsg.trigger.fire_event"
    assert push["data"]["event"]["type"] == "message_push"
    assert push["data"]["would_publish"] is True


def test_ref_binding_draft_is_core_candidate_and_draft_only() -> None:
    from parrot.brain import refs as refs_registry

    refs_registry.reset_refs_for_tests()
    try:
        ref = refs_registry.bind_focus(
            focus_id="focus-web-ref",
            source_event_id="evt-web-ref",
            label="Focus web ref",
        )
        client = TestClient(build_app(status_fetcher=_fake_fetcher))

        draft = client.post(
            "/api/refs/binding/draft",
            json={
                "ref_id": ref.ref_id,
                "target_kind": "l2b_node",
                "target_id": "node-web-ref",
                "dry_run": True,
                "operator_mode": False,
            },
        ).json()
        missing = client.post(
            "/api/refs/binding/draft",
            json={"ref_id": ref.ref_id, "target_kind": "l2b_node"},
        ).json()
        unresolved = client.post(
            "/api/refs/binding/draft",
            json={"ref_id": ref.ref_id, "target_kind": "unresolved"},
        ).json()

        assert draft["action"] == "refs.binding.draft"
        assert draft["success"] is True
        assert draft["data"]["core_candidate"] == "CORE-006"
        assert draft["data"]["apply_route"] == "/api/refs/binding/apply"
        assert draft["data"]["current_ref"]["ref_id"] == ref.ref_id
        assert draft["data"]["draft_target"] == {
            "target_kind": "l2b_node",
            "target_id": "node-web-ref",
        }
        assert "does not mutate L2-B" in draft["data"]["policy"]
        assert missing["success"] is False
        assert missing["data"]["error"] == "missing_target_id"
        assert unresolved["success"] is True
        assert unresolved["data"]["operation"] == "unresolve_ref"
        assert unresolved["data"]["would_resolve"] is False
        assert unresolved["data"]["would_unresolve"] is True
        assert unresolved["data"]["draft_target"] == {
            "target_kind": "unresolved",
            "target_id": "",
        }

        preview = client.post(
            "/api/refs/binding/apply",
            json={
                "ref_id": ref.ref_id,
                "target_kind": "l2b_node",
                "target_id": "node-web-ref",
                "dry_run": True,
                "operator_mode": False,
            },
        ).json()
        applied = client.post(
            "/api/refs/binding/apply",
            json={
                "ref_id": ref.ref_id,
                "target_kind": "l2b_node",
                "target_id": "node-web-ref",
                "event_id": "evt-web-ref-apply",
                "dry_run": False,
                "operator_mode": True,
            },
        ).json()
        unresolve_apply = client.post(
            "/api/refs/binding/apply",
            json={
                "ref_id": ref.ref_id,
                "target_kind": "unresolved",
                "event_id": "evt-web-ref-unresolve",
                "dry_run": False,
                "operator_mode": True,
            },
        ).json()

        assert preview["action"] == "refs.binding.apply"
        assert preview["success"] is True
        assert preview["data"]["would_apply"] is True
        assert preview["data"]["apply_skipped_reason"] == "dry_run_or_operator_mode_missing"
        assert applied["action"] == "refs.binding.apply"
        assert applied["success"] is True
        assert applied["dry_run"] is False
        assert applied["operator_mode"] is True
        assert applied["data"]["mutated"] is True
        assert applied["data"]["updated_ref"]["revision"] == ref.revision + 1
        assert applied["data"]["updated_ref"]["target_kind"] == "l2b_node"
        assert applied["data"]["updated_ref"]["target_id"] == "node-web-ref"
        assert applied["data"]["direct_l2b_write"] is False
        assert applied["data"]["direct_graphiti_write"] is False
        assert unresolve_apply["success"] is True
        assert unresolve_apply["data"]["updated_ref"]["target_kind"] == "unresolved"
        assert unresolve_apply["data"]["updated_ref"]["target_id"] == ""
        assert refs_registry.get_ref(ref.ref_id).target_kind == "unresolved"
    finally:
        refs_registry.reset_refs_for_tests()


def test_memory_identity_ref_index_routes_are_core_candidate_and_persist_json(
    monkeypatch,
    tmp_path,
) -> None:
    index_path = tmp_path / "memory_identity_ref_index.json"
    monkeypatch.setenv("PARROT_MEMORY_IDENTITY_REF_INDEX_PATH", str(index_path))
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    empty = client.get("/api/memory/identity-ref-index").json()
    missing = client.post("/api/memory/identity-ref-index/draft", json={}).json()
    draft = client.post(
        "/api/memory/identity-ref-index/draft",
        json={
            "canonical_uuid": "canon-amiya",
            "l2b_uuid": "l2b-amiya",
            "graphiti_entity_uuid": "graphiti-amiya",
            "graphiti_edge_uuid": "graphiti-fact-1",
            "graphiti_episode_uuid": "graphiti-episode-1",
            "obsidian_uuid": "obsidian-amiya",
            "provider_key": "google_calendar:primary:event-1",
            "alias": "Amiya",
            "confidence": 0.91,
            "resolution_state": "weak",
            "ref_id": "ref-amiya-doc",
            "ref_kind": "obsidian_doc",
            "locator": "D:/GOSLOParrot/GOSLObsidian/Worlds/Amiya.md",
            "content_hash": "sha256:test",
            "health": "unknown",
            "managed_by": "git",
            "graphiti_raw": {"fact": "Amiya is associated with Chernobog."},
            "ref_meta": {"source": "web_test"},
        },
    ).json()
    assert draft["action"] == "memory.identity_ref_index.draft"
    assert draft["success"] is True
    assert draft["data"]["core_candidate"] == "CORE-015"
    assert draft["data"]["identity_draft"]["canonical_uuid"] == "canon-amiya"
    assert draft["data"]["identity_draft"]["graphiti_entity_uuids"] == ["graphiti-amiya"]
    assert draft["data"]["identity_draft"]["graphiti_raw"]["fact"].startswith("Amiya")
    assert draft["data"]["ref_draft"]["canonical_uri"] == "parrot://refs/ref-amiya-doc"
    assert draft["data"]["would_persist"] is False
    assert index_path.exists() is False

    preview = client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-amiya",
            "graphiti_entity_uuid": "graphiti-amiya",
            "ref_id": "ref-amiya-doc",
            "locator": "D:/GOSLOParrot/GOSLObsidian/Worlds/Amiya.md",
            "dry_run": True,
            "operator_mode": False,
        },
    ).json()
    assert preview["action"] == "memory.identity_ref_index.apply"
    assert preview["data"]["would_persist"] is True
    assert preview["data"]["apply_skipped_reason"] == "dry_run_or_operator_mode_missing"
    assert index_path.exists() is False

    applied = client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-amiya",
            "l2b_uuid": "l2b-amiya",
            "graphiti_entity_uuid": "graphiti-amiya",
            "obsidian_uuid": "obsidian-amiya",
            "ref_id": "ref-amiya-doc",
            "ref_kind": "obsidian_doc",
            "locator": "D:/GOSLOParrot/GOSLObsidian/Worlds/Amiya.md",
            "dry_run": False,
            "operator_mode": True,
        },
    ).json()
    snapshot = client.get("/api/memory/identity-ref-index").json()

    assert empty["action"] == "memory.identity_ref_index.snapshot"
    assert empty["data"]["identity_count"] == 0
    assert empty["data"]["core_candidate"] == "CORE-015"
    assert missing["success"] is False
    assert missing["data"]["error"] == "missing_identity_or_ref_signal"
    assert applied["success"] is True
    assert applied["dry_run"] is False
    assert applied["operator_mode"] is True
    assert applied["data"]["mutated"] is True
    assert applied["data"]["direct_l2b_write"] is False
    assert applied["data"]["direct_graphiti_write"] is False
    assert applied["data"]["conflict_count"] == 0
    assert applied["data"]["merge_report"]["target_reason"] == "explicit_canonical_uuid"
    assert index_path.exists() is True
    assert snapshot["data"]["identity_count"] == 1
    assert snapshot["data"]["ref_count"] == 1
    assert snapshot["data"]["identities"][0]["l2b_uuid"] == "l2b-amiya"
    assert snapshot["data"]["refs"][0]["locators"] == [
        "D:/GOSLOParrot/GOSLObsidian/Worlds/Amiya.md"
    ]


def test_memory_identity_ref_index_merge_policy_preserves_conflicts(
    monkeypatch,
    tmp_path,
) -> None:
    index_path = tmp_path / "memory_identity_ref_index.json"
    monkeypatch.setenv("PARROT_MEMORY_IDENTITY_REF_INDEX_PATH", str(index_path))
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    first = client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-a",
            "l2b_uuid": "l2b-a",
            "graphiti_entity_uuid": "graphiti-shared",
            "alias": "Amiya",
            "ref_id": "ref-a",
            "locator": str(tmp_path / "amiya.md"),
            "dry_run": False,
            "operator_mode": True,
        },
    ).json()
    merged = client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "graphiti_entity_uuid": "graphiti-shared",
            "alias": "Doctor",
            "ref_id": "ref-a-note",
            "locator": str(tmp_path / "doctor.md"),
            "dry_run": False,
            "operator_mode": True,
        },
    ).json()
    graphiti_conflict = client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-b",
            "l2b_uuid": "l2b-b",
            "graphiti_entity_uuid": "graphiti-shared",
            "alias": "Conflicting Amiya",
            "dry_run": False,
            "operator_mode": True,
        },
    ).json()
    l2b_conflict = client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-c",
            "l2b_uuid": "l2b-b",
            "graphiti_entity_uuid": "graphiti-c",
            "dry_run": False,
            "operator_mode": True,
        },
    ).json()
    snapshot = client.get("/api/memory/identity-ref-index").json()
    identities = {
        item["canonical_uuid"]: item
        for item in snapshot["data"]["identities"]
    }

    assert first["success"] is True
    assert merged["data"]["identity"]["canonical_uuid"] == "canon-a"
    assert merged["data"]["merge_report"]["target_reason"] == "single_existing_signal"
    assert merged["data"]["conflict_count"] == 0
    assert set(merged["data"]["identity"]["aliases"]) == {"Amiya", "Doctor"}
    assert graphiti_conflict["data"]["identity"]["canonical_uuid"] == "canon-b"
    assert graphiti_conflict["data"]["conflict_count"] == 1
    assert graphiti_conflict["data"]["conflicts"][0]["kind"] == "graphiti_entity_uuid"
    assert graphiti_conflict["data"]["conflicts"][0]["existing_canonical_uuid"] == "canon-a"
    assert l2b_conflict["data"]["identity"]["canonical_uuid"] == "canon-c"
    assert l2b_conflict["data"]["conflict_count"] == 1
    assert l2b_conflict["data"]["conflicts"][0]["kind"] == "l2b_uuid"
    assert l2b_conflict["data"]["conflicts"][0]["existing_canonical_uuid"] == "canon-b"
    assert snapshot["data"]["identity_count"] == 3
    assert identities["canon-a"]["resolution_state"] == "conflicted"
    assert identities["canon-b"]["resolution_state"] == "conflicted"
    assert identities["canon-c"]["resolution_state"] == "conflicted"
    assert "graphiti-shared" in identities["canon-a"]["graphiti_entity_uuids"]
    assert "graphiti-shared" in identities["canon-b"]["graphiti_entity_uuids"]
    assert identities["canon-b"]["l2b_uuid"] == "l2b-b"
    assert identities["canon-c"]["l2b_uuid"] == "l2b-b"
    assert identities["canon-a"]["conflicts"][0]["policy"] == "preserve_without_auto_merge"


def test_memory_identity_ref_index_graphiti_ref_writeback_drafts_and_applies(
    monkeypatch,
    tmp_path,
) -> None:
    index_path = tmp_path / "memory_identity_ref_index.json"
    old_ref = tmp_path / "old_amiya.md"
    new_ref = tmp_path / "new_amiya.md"
    old_ref.write_text("old", encoding="utf-8")
    new_ref.write_text("new", encoding="utf-8")
    monkeypatch.setenv("PARROT_MEMORY_IDENTITY_REF_INDEX_PATH", str(index_path))
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-m14-amiya",
            "l2b_uuid": "l2b-m14-amiya",
            "graphiti_entity_uuid": "graphiti-m14-amiya",
            "ref_id": "ref-m14-amiya-doc",
            "ref_kind": "obsidian_doc",
            "locator": str(old_ref),
            "dry_run": False,
            "operator_mode": True,
        },
    )
    missing = client.post(
        "/api/memory/identity-ref-index/graphiti-ref/draft",
        json={
            "ref_id": "ref-without-graphiti",
            "locator": str(new_ref),
        },
    ).json()
    draft = client.post(
        "/api/memory/identity-ref-index/graphiti-ref/draft",
        json={
            "partition": "arknights_test",
            "graphiti_kind": "entity",
            "graphiti_uuid": "graphiti-m14-amiya",
            "graphiti_raw": {
                "uuid": "graphiti-m14-amiya",
                "name": "Amiya",
                "labels": ["Entity", "Operator"],
            },
            "external_refs": [
                {
                    "ref_id": "ref-m14-amiya-doc",
                    "ref_kind": "obsidian_doc",
                    "locator": str(new_ref),
                    "content_hash": "sha256:new",
                    "managed_by": "git",
                    "git_commit": "m14",
                }
            ],
            "requested_by": "pytest",
        },
    ).json()
    snapshot_after_draft = client.get("/api/memory/identity-ref-index").json()
    preview = client.post(
        "/api/memory/identity-ref-index/graphiti-ref/apply",
        json={
            "partition": "arknights_test",
            "graphiti_kind": "entity",
            "graphiti_uuid": "graphiti-m14-amiya",
            "external_refs": [
                {
                    "ref_id": "ref-m14-amiya-doc",
                    "ref_kind": "obsidian_doc",
                    "locator": str(new_ref),
                }
            ],
            "dry_run": True,
            "operator_mode": False,
        },
    ).json()
    applied = client.post(
        "/api/memory/identity-ref-index/graphiti-ref/apply",
        json={
            "partition": "arknights_test",
            "graphiti_kind": "entity",
            "graphiti_uuid": "graphiti-m14-amiya",
            "graphiti_raw": {"uuid": "graphiti-m14-amiya", "name": "Amiya"},
            "external_refs": [
                {
                    "ref_id": "ref-m14-amiya-doc",
                    "ref_kind": "obsidian_doc",
                    "locator": str(new_ref),
                    "content_hash": "sha256:new",
                    "managed_by": "git",
                    "git_commit": "m14",
                }
            ],
            "dry_run": False,
            "operator_mode": True,
        },
    ).json()
    snapshot_after_apply = client.get("/api/memory/identity-ref-index").json()

    assert missing["action"] == "memory.identity_ref_index.graphiti_ref_writeback_draft"
    assert missing["success"] is False
    assert missing["data"]["error"] == "missing_graphiti_uuid"
    assert draft["action"] == "memory.identity_ref_index.graphiti_ref_writeback_draft"
    assert draft["success"] is True
    assert draft["data"]["would_persist"] is False
    assert draft["data"]["graphiti_record_ref"]["partition"] == "arknights_test"
    assert draft["data"]["graphiti_record_ref"]["graphiti_kind"] == "entity"
    assert draft["data"]["identity_binding"]["canonical_uuid"] == "canon-m14-amiya"
    assert draft["data"]["external_ref_records"][0]["ref_id"] == "ref-m14-amiya-doc"
    assert draft["data"]["ref_move_events"][0]["event_type"] == "locator_added"
    assert draft["data"]["ref_move_events"][0]["old_locators"] == [str(old_ref)]
    assert draft["data"]["ref_move_events"][0]["new_locators"] == [
        str(old_ref),
        str(new_ref),
    ]
    assert draft["data"]["audit_episode_draft"]["write_status"] == "draft_only"
    assert "ref-m14-amiya-doc" in draft["data"]["audit_episode_draft"]["body"]
    assert snapshot_after_draft["data"]["refs"][0]["locators"] == [str(old_ref)]
    assert preview["action"] == "memory.identity_ref_index.graphiti_ref_writeback_apply"
    assert preview["data"]["would_persist"] is True
    assert preview["data"]["apply_skipped_reason"] == "dry_run_or_operator_mode_missing"
    assert applied["success"] is True
    assert applied["dry_run"] is False
    assert applied["operator_mode"] is True
    assert applied["data"]["mutated"] is True
    assert applied["data"]["mutation_scope"] == "memory_identity_ref_index_json_only"
    assert applied["data"]["direct_l2b_write"] is False
    assert applied["data"]["direct_graphiti_write"] is False
    assert applied["data"]["direct_file_move"] is False
    assert applied["data"]["graphiti_audit_episode"]["written"] is False
    persisted_ref = {
        item["ref_id"]: item for item in snapshot_after_apply["data"]["refs"]
    }["ref-m14-amiya-doc"]
    assert persisted_ref["locators"] == [str(old_ref), str(new_ref)]
    assert persisted_ref["content_hash"] == "sha256:new"
    assert persisted_ref["meta"]["graphiti_record_ref"]["graphiti_uuid"] == "graphiti-m14-amiya"


def test_memory_identity_ref_index_graphiti_ref_writeback_skips_empty_external_ref(
    monkeypatch,
    tmp_path,
) -> None:
    index_path = tmp_path / "memory_identity_ref_index.json"
    monkeypatch.setenv("PARROT_MEMORY_IDENTITY_REF_INDEX_PATH", str(index_path))
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    payload = {
        "partition": "arknights_test",
        "graphiti_kind": "edge",
        "graphiti_uuid": "graphiti-m14-empty-ref",
        "external_refs": [
            {
                "ref_id": "ref-m14-empty",
                "ref_kind": "graphiti_fact",
            }
        ],
        "dry_run": False,
        "operator_mode": True,
    }
    draft = client.post(
        "/api/memory/identity-ref-index/graphiti-ref/draft",
        json=payload,
    ).json()
    applied = client.post(
        "/api/memory/identity-ref-index/graphiti-ref/apply",
        json=payload,
    ).json()
    snapshot = client.get("/api/memory/identity-ref-index").json()

    assert draft["success"] is True
    assert draft["data"]["external_ref_payloads"] == []
    assert draft["data"]["external_ref_records"] == []
    assert draft["data"]["ref_move_events"] == []
    assert applied["success"] is True
    assert applied["data"]["identity_binding"]["graphiti_edge_uuids"] == [
        "graphiti-m14-empty-ref"
    ]
    assert applied["data"]["external_ref_records"] == []
    assert snapshot["data"]["identity_count"] == 1
    assert snapshot["data"]["ref_count"] == 0


def test_memory_identity_ref_index_graphiti_ref_writeback_can_write_audit_episode(
    monkeypatch,
    tmp_path,
) -> None:
    index_path = tmp_path / "memory_identity_ref_index.json"
    monkeypatch.setenv("PARROT_MEMORY_IDENTITY_REF_INDEX_PATH", str(index_path))
    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    calls: list[dict[str, Any]] = []

    class FakeGraphitiResult:
        def as_json(self) -> dict[str, Any]:
            return {
                "action": "add_episode",
                "success": True,
                "available": True,
                "message": "episode written",
                "data": {"episode_uuid": "episode-m14-audit"},
            }

    async def fake_add_episode(**kwargs: Any) -> FakeGraphitiResult:
        calls.append(kwargs)
        return FakeGraphitiResult()

    graphiti_console = import_module("parrot.brain.graphiti_console")
    monkeypatch.setattr(graphiti_console, "add_episode", fake_add_episode)

    applied = client.post(
        "/api/memory/identity-ref-index/graphiti-ref/apply",
        json={
            "partition": "arknights_test",
            "graphiti_kind": "edge",
            "graphiti_uuid": "graphiti-m14-fact",
            "graphiti_raw": {
                "uuid": "graphiti-m14-fact",
                "fact": "Amiya has an audit ref.",
            },
            "external_refs": [
                {
                    "ref_id": "ref-m14-audit",
                    "ref_kind": "url",
                    "url": "https://example.com/m14-audit",
                    "managed_by": "git",
                }
            ],
            "write_graphiti_audit_episode": True,
            "dry_run": False,
            "operator_mode": True,
        },
    ).json()

    assert applied["action"] == "memory.identity_ref_index.graphiti_ref_writeback_apply"
    assert applied["success"] is True
    assert applied["data"]["direct_graphiti_write"] is True
    assert applied["data"]["graphiti_audit_episode_written"] is True
    assert applied["data"]["mutation_scope"] == (
        "memory_identity_ref_index_json_and_graphiti_audit_episode"
    )
    assert applied["data"]["graphiti_audit_episode"]["written"] is True
    assert applied["data"]["graphiti_audit_episode"]["result"]["data"]["episode_uuid"] == (
        "episode-m14-audit"
    )
    assert calls
    assert calls[0]["partition"] == "arknights_test"
    assert calls[0]["dry_run"] is False
    assert calls[0]["source_description"] == "parrot-web-console-ref-writeback-audit"
    assert "ref-m14-audit" in calls[0]["body"]
    assert index_path.exists() is True


def test_memory_identity_ref_index_resolves_graphiti_edges_without_l2b_write(
    monkeypatch,
    tmp_path,
) -> None:
    index_path = tmp_path / "memory_identity_ref_index.json"
    monkeypatch.setenv("PARROT_MEMORY_IDENTITY_REF_INDEX_PATH", str(index_path))
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-source",
            "l2b_uuid": "l2b-source",
            "graphiti_entity_uuid": "graphiti-source",
            "alias": "Amiya",
            "dry_run": False,
            "operator_mode": True,
        },
    )
    client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-target",
            "l2b_uuid": "l2b-target",
            "graphiti_entity_uuid": "graphiti-target",
            "alias": "Chernobog",
            "dry_run": False,
            "operator_mode": True,
        },
    )
    client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-fact",
            "graphiti_edge_uuid": "graphiti-fact",
            "alias": "Amiya associated with Chernobog",
            "dry_run": False,
            "operator_mode": True,
        },
    )

    resolved = client.post(
        "/api/memory/identity-ref-index/resolve-graphiti",
        json={
            "partition": "arknights_test",
            "edge_drafts": [
                {
                    "source_graphiti_uuid": "graphiti-source",
                    "target_graphiti_uuid": "graphiti-target",
                    "hit_graphiti_uuid": "graphiti-fact",
                    "label": "Amiya Chernobog fact",
                    "strength": 0.87,
                    "meta": {"fact_text": "Amiya reaches Chernobog."},
                }
            ],
        },
    ).json()

    edge = resolved["data"]["edges"][0]
    assert resolved["action"] == "memory.identity_ref_index.resolve_graphiti"
    assert resolved["success"] is True
    assert resolved["data"]["ready_count"] == 1
    assert resolved["data"]["mutated"] is False
    assert resolved["data"]["direct_l2b_write"] is False
    assert resolved["data"]["direct_graphiti_write"] is False
    assert edge["can_materialize_l2b_edge"] is True
    assert edge["blocked_reasons"] == []
    assert edge["source"]["status"] == "resolved_l2b"
    assert edge["source"]["canonical_uuid"] == "canon-source"
    assert edge["source"]["l2b_uuid"] == "l2b-source"
    assert edge["target"]["status"] == "resolved_l2b"
    assert edge["fact"]["status"] == "canonical_only"
    assert edge["l2b_edge_draft"]["source_uuid"] == "l2b-source"
    assert edge["l2b_edge_draft"]["target_uuid"] == "l2b-target"
    assert edge["l2b_edge_draft"]["meta"]["fact_canonical_uuid"] == "canon-fact"
    assert resolved["data"]["apply_preconditions"]["source"] == "resolved_l2b"


def test_memory_identity_ref_index_graphiti_resolver_blocks_missing_and_conflicted(
    monkeypatch,
    tmp_path,
) -> None:
    index_path = tmp_path / "memory_identity_ref_index.json"
    monkeypatch.setenv("PARROT_MEMORY_IDENTITY_REF_INDEX_PATH", str(index_path))
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-source-only",
            "l2b_uuid": "l2b-source-only",
            "graphiti_entity_uuid": "graphiti-source-only",
            "dry_run": False,
            "operator_mode": True,
        },
    )
    one_missing = client.post(
        "/api/memory/identity-ref-index/resolve-graphiti",
        json={
            "partition": "arknights_test",
            "source_graphiti_uuid": "graphiti-source-only",
            "target_graphiti_uuid": "graphiti-missing-target",
            "hit_graphiti_uuid": "graphiti-missing-fact",
        },
    ).json()
    both_missing = client.post(
        "/api/memory/identity-ref-index/resolve-graphiti",
        json={
            "partition": "arknights_test",
            "edge_drafts": [
                {
                    "source_graphiti_uuid": "graphiti-missing-source",
                    "target_graphiti_uuid": "graphiti-missing-target",
                    "hit_graphiti_uuid": "graphiti-missing-fact",
                }
            ],
        },
    ).json()

    client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-conflict-a",
            "l2b_uuid": "l2b-conflict-a",
            "graphiti_entity_uuid": "graphiti-conflict",
            "dry_run": False,
            "operator_mode": True,
        },
    )
    client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-conflict-b",
            "l2b_uuid": "l2b-conflict-b",
            "graphiti_entity_uuid": "graphiti-conflict",
            "dry_run": False,
            "operator_mode": True,
        },
    )
    conflicted = client.post(
        "/api/memory/identity-ref-index/resolve-graphiti",
        json={
            "partition": "arknights_test",
            "edge_drafts": [
                {
                    "source_graphiti_uuid": "graphiti-conflict",
                    "target_graphiti_uuid": "graphiti-source-only",
                    "hit_graphiti_uuid": "graphiti-conflict-fact",
                }
            ],
        },
    ).json()

    one_missing_edge = one_missing["data"]["edges"][0]
    both_missing_edge = both_missing["data"]["edges"][0]
    conflicted_edge = conflicted["data"]["edges"][0]
    assert one_missing["data"]["ready_count"] == 0
    assert one_missing_edge["can_materialize_l2b_edge"] is False
    assert one_missing_edge["source"]["status"] == "resolved_l2b"
    assert one_missing_edge["target"]["status"] == "missing"
    assert one_missing_edge["target"]["pointer_candidate"]["graphiti_entity_uuid"] == (
        "graphiti-missing-target"
    )
    assert one_missing_edge["blocked_reasons"] == ["target_missing"]
    assert both_missing["data"]["missing_endpoint_count"] == 2
    assert both_missing_edge["blocked_reasons"] == ["source_missing", "target_missing"]
    assert both_missing_edge["l2b_edge_draft"] == {}
    assert conflicted_edge["source"]["status"] == "conflicted"
    assert conflicted_edge["source"]["match_count"] == 2
    assert conflicted_edge["blocked_reasons"] == ["source_conflicted"]
    assert conflicted["data"]["direct_l2b_write"] is False


def test_memory_identity_ref_index_materializes_resolved_graphiti_edge_under_operator(
    monkeypatch,
    tmp_path,
) -> None:
    import parrot.dsg.l2b_graph as l2b_graph_module
    from parrot.dsg.l2b_graph import L2BGraph
    from parrot.dsg.l2b_types import EdgeKind, NodeKind, SemanticNode

    index_path = tmp_path / "memory_identity_ref_index.json"
    monkeypatch.setenv("PARROT_MEMORY_IDENTITY_REF_INDEX_PATH", str(index_path))
    graph = L2BGraph()
    graph.upsert_node(SemanticNode(uuid="l2b-m5-source", kind=NodeKind.OBJECT, label="Amiya"))
    graph.upsert_node(SemanticNode(uuid="l2b-m5-target", kind=NodeKind.ZONE, label="Chernobog"))
    monkeypatch.setattr(l2b_graph_module, "_instance", graph)
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-m5-source",
            "l2b_uuid": "l2b-m5-source",
            "graphiti_entity_uuid": "graphiti-m5-source",
            "dry_run": False,
            "operator_mode": True,
        },
    )
    client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-m5-target",
            "l2b_uuid": "l2b-m5-target",
            "graphiti_entity_uuid": "graphiti-m5-target",
            "dry_run": False,
            "operator_mode": True,
        },
    )
    client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-m5-fact",
            "graphiti_edge_uuid": "graphiti-m5-fact",
            "dry_run": False,
            "operator_mode": True,
        },
    )
    payload = {
        "partition": "arknights_test",
        "edge_drafts": [
            {
                "source_graphiti_uuid": "graphiti-m5-source",
                "target_graphiti_uuid": "graphiti-m5-target",
                "hit_graphiti_uuid": "graphiti-m5-fact",
                "label": "Amiya reaches Chernobog",
                "strength": 0.72,
                "meta": {
                    "fact_text": "Amiya reaches Chernobog.",
                    "ref_ids": ["ref-m5-fact"],
                    "graphiti_raw": {
                        "uuid": "graphiti-m5-fact",
                        "name": "Amiya reaches Chernobog",
                    },
                },
            }
        ],
    }

    preview = client.post(
        "/api/memory/identity-ref-index/apply-graphiti-edge",
        json={**payload, "dry_run": True, "operator_mode": False},
    ).json()
    edges_after_preview = [
        edge
        for _, _, edge in graph.all_edges()
        if edge.graphiti_uuid == "graphiti-m5-fact"
    ]
    applied = client.post(
        "/api/memory/identity-ref-index/apply-graphiti-edge",
        json={**payload, "dry_run": False, "operator_mode": True},
    ).json()
    materialized_edges = [
        (source, target, edge)
        for source, target, edge in graph.all_edges()
        if edge.graphiti_uuid == "graphiti-m5-fact"
    ]

    assert preview["action"] == "memory.identity_ref_index.apply_graphiti_edge"
    assert preview["success"] is True
    assert preview["data"]["would_apply"] is True
    assert preview["data"]["mutated"] is False
    assert preview["data"]["direct_l2b_write"] is False
    assert preview["data"]["l2b_apply_receipt"]["action"] == "l2b.edge.apply"
    assert edges_after_preview == []
    assert applied["success"] is True
    assert applied["data"]["connected"] is True
    assert applied["data"]["mutated"] is True
    assert applied["data"]["direct_l2b_write"] is True
    assert applied["data"]["direct_graphiti_write"] is False
    assert len(materialized_edges) == 1
    source, target, edge = materialized_edges[0]
    assert source.uuid == "l2b-m5-source"
    assert target.uuid == "l2b-m5-target"
    assert edge.kind == EdgeKind.GRAPHITI_FACT
    assert edge.source == "graphiti"
    assert edge.source_graphiti_uuid == "graphiti-m5-source"
    assert edge.target_graphiti_uuid == "graphiti-m5-target"
    assert edge.ref_ids == ("ref-m5-fact",)
    assert edge.meta["graphiti_partition"] == "arknights_test"
    assert edge.meta["source_canonical_uuid"] == "canon-m5-source"
    assert edge.meta["target_canonical_uuid"] == "canon-m5-target"
    assert edge.meta["fact_canonical_uuid"] == "canon-m5-fact"
    assert edge.meta["graphiti_raw"]["uuid"] == "graphiti-m5-fact"
    assert edge.meta["graphiti_raw_edge"]["label"] == "Amiya reaches Chernobog"


def test_memory_identity_ref_index_graphiti_edge_apply_blocks_unresolved_endpoint(
    monkeypatch,
    tmp_path,
) -> None:
    import parrot.dsg.l2b_graph as l2b_graph_module
    from parrot.dsg.l2b_graph import L2BGraph
    from parrot.dsg.l2b_types import NodeKind, SemanticNode

    index_path = tmp_path / "memory_identity_ref_index.json"
    monkeypatch.setenv("PARROT_MEMORY_IDENTITY_REF_INDEX_PATH", str(index_path))
    graph = L2BGraph()
    graph.upsert_node(SemanticNode(uuid="l2b-m5-block-source", kind=NodeKind.OBJECT, label="Amiya"))
    monkeypatch.setattr(l2b_graph_module, "_instance", graph)
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-m5-block-source",
            "l2b_uuid": "l2b-m5-block-source",
            "graphiti_entity_uuid": "graphiti-m5-block-source",
            "dry_run": False,
            "operator_mode": True,
        },
    )
    blocked = client.post(
        "/api/memory/identity-ref-index/apply-graphiti-edge",
        json={
            "partition": "arknights_test",
            "source_graphiti_uuid": "graphiti-m5-block-source",
            "target_graphiti_uuid": "graphiti-m5-missing-target",
            "hit_graphiti_uuid": "graphiti-m5-blocked-fact",
            "dry_run": False,
            "operator_mode": True,
        },
    ).json()
    materialized_edges = [
        edge
        for _, _, edge in graph.all_edges()
        if edge.graphiti_uuid == "graphiti-m5-blocked-fact"
    ]

    assert blocked["action"] == "memory.identity_ref_index.apply_graphiti_edge"
    assert blocked["success"] is False
    assert blocked["data"]["error"] == "unresolved_graphiti_edge_endpoints"
    assert blocked["data"]["blocked_reasons"] == ["target_missing"]
    assert blocked["data"]["mutated"] is False
    assert blocked["data"]["direct_l2b_write"] is False
    assert "l2b_apply_receipt" not in blocked["data"]
    assert materialized_edges == []


def test_memory_identity_ref_index_ref_scan_plan_drafts_nanobot_mcp_contract(
    monkeypatch,
    tmp_path,
) -> None:
    index_path = tmp_path / "memory_identity_ref_index.json"
    manifest_path = tmp_path / "runtime_manifests" / "memory_refs_manifest.json"
    obsidian_note = tmp_path / "Amiya.md"
    obsidian_note.write_text("---\nuuid: obsidian-ref\n---\nAmiya\n", encoding="utf-8")
    monkeypatch.setenv("PARROT_MEMORY_IDENTITY_REF_INDEX_PATH", str(index_path))
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-scan-obsidian",
            "l2b_uuid": "l2b-scan-obsidian",
            "graphiti_entity_uuid": "graphiti-scan-obsidian",
            "obsidian_uuid": "obsidian-ref",
            "ref_id": "ref-scan-obsidian",
            "ref_kind": "obsidian_doc",
            "locator": str(obsidian_note),
            "content_hash": "sha256:old",
            "managed_by": "git",
            "git_commit": "abc123",
            "dry_run": False,
            "operator_mode": True,
        },
    )
    client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-scan-url",
            "ref_id": "ref-scan-url",
            "ref_kind": "url",
            "url": "https://example.com/amiya",
            "dry_run": False,
            "operator_mode": True,
        },
    )
    client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-scan-ecs",
            "ref_id": "ref-scan-ecs",
            "ref_kind": "ecs_path",
            "locator": "ecs://castle/root/photos/amiya.jpg",
            "managed_by": "nanobot",
            "dry_run": False,
            "operator_mode": True,
        },
    )
    client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-scan-graphiti",
            "graphiti_entity_uuid": "graphiti-scan-node",
            "ref_id": "ref-scan-graphiti",
            "ref_kind": "graphiti_entity",
            "locator": "graphiti://arknights/entity/graphiti-scan-node",
            "dry_run": False,
            "operator_mode": True,
        },
    )

    plan = client.post(
        "/api/memory/identity-ref-index/ref-scan-plan",
        json={
            "manifest_path": str(manifest_path),
            "git_root": str(tmp_path),
            "limit": 20,
            "priority": "low",
        },
    ).json()

    rows = {item["ref_id"]: item for item in plan["data"]["ref_scan_plan"]}
    assert plan["action"] == "memory.identity_ref_index.ref_scan_plan"
    assert plan["success"] is True
    assert plan["dry_run"] is True
    assert plan["operator_mode"] is False
    assert plan["data"]["task_type"] == "ref_scan"
    assert plan["data"]["priority"] == "low"
    assert plan["data"]["params"]["result_channel"] == "memory_ref_scan_result"
    assert plan["data"]["params"]["remote_checks"] == []
    assert plan["data"]["params"]["enable_url_check"] is False
    assert plan["data"]["params"]["enable_ecs_local_check"] is False
    assert plan["data"]["params"]["enable_graphiti_probe"] is False
    assert plan["data"]["remote_check_policy"]["mutation_allowed"] is False
    assert plan["data"]["params"]["refs"][0]["ref_id"]
    assert plan["data"]["operator_required_for_dispatch"] is True
    assert plan["data"]["mutated"] is False
    assert plan["data"]["direct_l2b_write"] is False
    assert plan["data"]["direct_graphiti_write"] is False
    assert plan["data"]["direct_ecs_write"] is False
    assert plan["data"]["git_manifest"]["write_policy"] == "propose_manifest_delta_only"
    assert plan["data"]["git_manifest"]["nanobot_may_write"] is False
    assert manifest_path.exists() is False
    assert rows["ref-scan-obsidian"]["scan_targets"][0]["target_type"] == "local_path"
    assert "obsidian_frontmatter_uuid_probe" in rows["ref-scan-obsidian"]["nanobot_checks"]
    assert "git_manifest_diff" in rows["ref-scan-obsidian"]["nanobot_checks"]
    assert "graphiti_uuid_probe" in rows["ref-scan-obsidian"]["nanobot_checks"]
    assert rows["ref-scan-url"]["scan_targets"][0]["target_type"] == "url"
    assert "url_head" in rows["ref-scan-url"]["nanobot_checks"]
    assert rows["ref-scan-ecs"]["scan_targets"][0]["target_type"] == "ecs_path"
    assert "ecs_path_stat" in rows["ref-scan-ecs"]["nanobot_checks"]
    assert rows["ref-scan-graphiti"]["scan_targets"][0]["target_type"] == "graphiti_pointer"
    assert "graphiti_uuid_probe" in rows["ref-scan-graphiti"]["nanobot_checks"]
    assert plan["data"]["counts"]["by_target_type"]["ecs_path"] == 1
    assert plan["data"]["counts"]["by_target_type"]["graphiti_pointer"] == 1
    assert plan["data"]["counts"]["by_target_type"]["local_path"] == 1
    assert plan["data"]["counts"]["by_target_type"]["url"] == 1


def test_memory_identity_ref_index_ref_scan_dispatch_is_operator_gated(
    monkeypatch,
    tmp_path,
) -> None:
    index_path = tmp_path / "memory_identity_ref_index.json"
    monkeypatch.setenv("PARROT_MEMORY_IDENTITY_REF_INDEX_PATH", str(index_path))
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-dispatch-ref",
            "ref_id": "ref-dispatch",
            "ref_kind": "local_path",
            "locator": str(tmp_path / "dispatch.md"),
            "dry_run": False,
            "operator_mode": True,
        },
    )

    preview = client.post(
        "/api/memory/identity-ref-index/ref-scan-dispatch",
        json={"dry_run": True, "operator_mode": False, "priority": "low"},
    ).json()

    assert preview["action"] == "memory.identity_ref_index.ref_scan_dispatch"
    assert preview["success"] is True
    assert preview["dry_run"] is True
    assert preview["operator_mode"] is False
    assert preview["data"]["task_type"] == "ref_scan"
    assert preview["data"]["would_dispatch"] is True
    assert preview["data"]["dispatch_skipped_reason"] == "dry_run_or_operator_mode_missing"
    assert preview["data"]["params"]["result_channel"] == "memory_ref_scan_result"
    assert preview["data"]["params"]["allow_mutation"] is False


def test_memory_identity_ref_index_ref_scan_dispatch_can_enqueue_read_only_task(
    monkeypatch,
    tmp_path,
) -> None:
    index_path = tmp_path / "memory_identity_ref_index.json"
    monkeypatch.setenv("PARROT_MEMORY_IDENTITY_REF_INDEX_PATH", str(index_path))
    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    calls: list[dict[str, Any]] = []

    async def fake_do_dispatch_task(
        task_type: str,
        *,
        params: dict[str, Any] | None = None,
        priority: str = "normal",
    ) -> str:
        calls.append({"task_type": task_type, "params": params or {}, "priority": priority})
        return "task_ref_scan_real"

    dispatch_module = import_module("parrot.brain.tools.dispatch_task")
    monkeypatch.setattr(dispatch_module, "do_dispatch_task", fake_do_dispatch_task)

    client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-dispatch-real",
            "graphiti_entity_uuid": "graphiti-dispatch-real",
            "ref_id": "ref-dispatch-real",
            "ref_kind": "graphiti_entity",
            "locator": "graphiti://arknights/entity/graphiti-dispatch-real",
            "dry_run": False,
            "operator_mode": True,
        },
    )
    body = client.post(
        "/api/memory/identity-ref-index/ref-scan-dispatch",
        json={
            "dry_run": False,
            "operator_mode": True,
            "priority": "low",
            "remote_checks": ["url", "ecs", "graphiti"],
        },
    ).json()

    assert body["action"] == "memory.identity_ref_index.ref_scan_dispatch"
    assert body["success"] is True
    assert body["dry_run"] is False
    assert body["operator_mode"] is True
    assert body["data"]["dispatched"] is True
    assert body["data"]["task_id"] == "task_ref_scan_real"
    assert body["data"]["mutation_scope"] == "scheduler_nanobot_queue_only"
    assert body["data"]["mutated"] is False
    assert body["data"]["direct_l2b_write"] is False
    assert body["data"]["direct_graphiti_write"] is False
    assert body["data"]["direct_ecs_write"] is False
    assert calls == [
        {
            "task_type": "ref_scan",
            "params": body["data"]["params"],
            "priority": "low",
        }
    ]
    assert calls[0]["params"]["allow_mutation"] is False
    assert calls[0]["params"]["scan_mode"] == "read_only"
    assert calls[0]["params"]["remote_checks"] == ["url", "ecs", "graphiti"]
    assert calls[0]["params"]["enable_url_check"] is True
    assert calls[0]["params"]["enable_ecs_local_check"] is False
    assert calls[0]["params"]["ecs_local_check_confirmed"] is False
    assert calls[0]["params"]["enable_graphiti_probe"] is True
    assert calls[0]["params"]["refs"][0]["ref_id"] == "ref-dispatch-real"


def test_memory_identity_ref_index_ref_scan_results_read_scheduler_ledger(
    monkeypatch,
) -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    class FakeRedis:
        async def xrevrange(self, stream: str, count: int = 20):
            assert stream == "parrot.trigger.results.stream"
            assert count >= 6
            return [
                (
                    "1710000001000-0",
                    {
                        "payload": json.dumps(
                            {
                                "task_id": "task_ref_scan",
                                "type": "memory_ref_scan_result",
                                "original_type": "ref_scan",
                                "status": "completed",
                                "api_key": "sk-should-redact",
                                "result": json.dumps(
                                    {
                                        "scan_id": "refscan_test",
                                        "summary": "Scanned 1 ref",
                                        "ref_results": [
                                            {
                                                "ref_id": "ref-health-ok",
                                                "canonical_uuid": "canon-health-ok",
                                                "health": "ok",
                                                "resolved_locator": "D:/Refs/Amiya.md",
                                                "manifest_action": "compare_git_manifest_and_ref_record",
                                            }
                                        ],
                                        "manifest_delta": [
                                            {"ref_id": "ref-health-ok", "action": "update_hash"}
                                        ],
                                        "warnings": ["hash_changed"],
                                    }
                                ),
                            }
                        ),
                        "result_channel": "memory_ref_scan_result",
                        "task_id": "task_ref_scan",
                        "created_at": "1710000001.0",
                    },
                )
            ]

    async def fake_get_redis():
        return FakeRedis()

    monkeypatch.setattr("parrot.shared.redis_client.get_redis", fake_get_redis)

    body = client.get(
        "/api/memory/identity-ref-index/ref-scan-results",
        params={"limit": 2},
    ).json()

    assert body["action"] == "memory.identity_ref_index.ref_scan_results"
    assert body["success"] is True
    assert body["data"]["available"] is True
    assert body["data"]["result_channel"] == "memory_ref_scan_result"
    row = body["data"]["rows"][0]
    assert row["task_id"] == "task_ref_scan"
    assert row["result_channel"] == "memory_ref_scan_result"
    assert row["original_type"] == "ref_scan"
    assert row["scan_id"] == "refscan_test"
    assert row["ref_result_count"] == 1
    assert row["ref_result_sample"][0]["ref_id"] == "ref-health-ok"
    assert row["manifest_delta_count"] == 1
    assert row["warnings"] == ["hash_changed"]
    assert row["payload"]["api_key"] == "<redacted>"
    assert "sk-should-redact" not in str(body)


def test_memory_identity_ref_index_ref_scan_results_tolerates_missing_redis(
    monkeypatch,
) -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    async def fake_get_redis():
        raise RuntimeError("redis offline")

    monkeypatch.setattr("parrot.shared.redis_client.get_redis", fake_get_redis)

    body = client.get("/api/memory/identity-ref-index/ref-scan-results").json()

    assert body["action"] == "memory.identity_ref_index.ref_scan_results"
    assert body["success"] is True
    assert body["data"]["available"] is False
    assert body["data"]["rows"] == []


def test_memory_identity_ref_index_verify_reports_local_and_uuid_health(
    monkeypatch,
    tmp_path,
) -> None:
    index_path = tmp_path / "memory_identity_ref_index.json"
    existing_ref = tmp_path / "amiya.md"
    existing_ref.write_text("Amiya", encoding="utf-8")
    monkeypatch.setenv("PARROT_MEMORY_IDENTITY_REF_INDEX_PATH", str(index_path))
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-health-ok",
            "l2b_uuid": "l2b-health-ok",
            "graphiti_entity_uuid": "graphiti-health-ok",
            "obsidian_uuid": "obsidian-health-ok",
            "ref_id": "ref-health-ok",
            "ref_kind": "obsidian_doc",
            "locator": str(existing_ref),
            "dry_run": False,
            "operator_mode": True,
        },
    )
    client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-health-missing",
            "graphiti_entity_uuid": "graphiti-health-missing",
            "obsidian_uuid": "obsidian-health-missing",
            "ref_id": "ref-health-missing",
            "ref_kind": "local_path",
            "locator": str(tmp_path / "missing.md"),
            "dry_run": False,
            "operator_mode": True,
        },
    )
    client.post(
        "/api/memory/identity-ref-index/apply",
        json={
            "canonical_uuid": "canon-health-url",
            "ref_id": "ref-health-url",
            "ref_kind": "url",
            "url": "https://example.com/ref",
            "dry_run": False,
            "operator_mode": True,
        },
    )

    preview = client.post(
        "/api/memory/identity-ref-index/verify",
        json={
            "graphiti_uuid_statuses": {
                "graphiti-health-ok": True,
                "graphiti-health-missing": False,
            },
            "obsidian_uuid_statuses": {
                "obsidian-health-ok": True,
                "obsidian-health-missing": False,
            },
            "update_index": True,
            "dry_run": True,
            "operator_mode": False,
        },
    ).json()
    snapshot_after_preview = client.get("/api/memory/identity-ref-index").json()
    applied = client.post(
        "/api/memory/identity-ref-index/verify",
        json={
            "graphiti_uuid_statuses": {
                "graphiti-health-ok": True,
                "graphiti-health-missing": False,
            },
            "obsidian_uuid_statuses": {
                "obsidian-health-ok": True,
                "obsidian-health-missing": False,
            },
            "update_index": True,
            "dry_run": False,
            "operator_mode": True,
        },
    ).json()
    snapshot_after_apply = client.get("/api/memory/identity-ref-index").json()

    ref_checks = {item["ref_id"]: item for item in preview["data"]["ref_checks"]}
    identity_checks = {
        item["canonical_uuid"]: item for item in preview["data"]["identity_checks"]
    }
    assert preview["action"] == "memory.identity_ref_index.verify"
    assert preview["data"]["core_candidate"] == "CORE-015"
    assert preview["data"]["updated_index"] is False
    assert preview["data"]["apply_skipped_reason"] == "dry_run_or_operator_mode_missing"
    assert ref_checks["ref-health-ok"]["health"] == "ok"
    assert ref_checks["ref-health-ok"]["locator_checks"][0]["reason"] == "local_path_exists"
    assert ref_checks["ref-health-missing"]["health"] == "missing"
    assert ref_checks["ref-health-url"]["health"] == "unknown"
    assert ref_checks["ref-health-url"]["locator_checks"][0]["reason"] == "url_not_checked"
    assert identity_checks["canon-health-ok"]["health"] == "ok"
    assert identity_checks["canon-health-missing"]["health"] == "missing"
    assert snapshot_after_preview["data"]["refs"][0]["health"] == "unknown"
    assert applied["data"]["updated_index"] is True
    persisted_health = {
        item["ref_id"]: item["health"] for item in snapshot_after_apply["data"]["refs"]
    }
    assert persisted_health["ref-health-ok"] == "ok"
    assert persisted_health["ref-health-missing"] == "missing"
    assert persisted_health["ref-health-url"] == "unknown"


def test_photo_asset_route_serves_only_cache_root(monkeypatch, tmp_path) -> None:
    day = "2026-05-15"
    photo_id = "web_photo_asset"
    photo_dir = tmp_path / day
    photo_dir.mkdir()
    photo_bytes = b"\xff\xd8web-console-photo\xff\xd9"
    (photo_dir / f"{photo_id}.jpg").write_bytes(photo_bytes)
    monkeypatch.setenv("PARROT_PHOTO_CACHE_ROOT", str(tmp_path))

    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    direct = client.get(f"/api/photos/asset/{day}/{photo_id}")
    with_extension = client.get(f"/api/photos/asset/{day}/{photo_id}.jpg")
    missing = client.get(f"/api/photos/asset/{day}/missing_photo")
    bad_day = client.get(f"/api/photos/asset/not-a-day/{photo_id}")
    bad_id = client.get(f"/api/photos/asset/{day}/bad..photo")

    assert direct.status_code == 200
    assert direct.content == photo_bytes
    assert direct.headers["content-type"].startswith("image/jpeg")
    assert direct.headers["Cache-Control"] == "no-store"
    assert with_extension.status_code == 200
    assert with_extension.content == photo_bytes
    assert missing.status_code == 404
    assert bad_day.status_code == 400
    assert bad_id.status_code == 400


def test_status_summary_marks_degraded_for_offline_process() -> None:
    summary = _status_summary(
        {
            "schema_version": 1,
            "host": "host-a",
            "processes": [
                {"module_id": "brain", "online": True},
                {"module_id": "nanobot-worker", "online": False},
            ],
            "warnings": [],
            "selection_drift": {"is_drift": False},
            "containers": [],
        }
    )

    assert summary["state"] == "degraded"
    assert summary["online_processes"] == 1
    assert summary["offline_processes"] == 1


def test_vision_evidence_routes_are_secret_safe_and_record_timeline(tmp_path, monkeypatch) -> None:
    from parrot.brain.vision.evidence import get_evidence_ledger
    from parrot.brain.vision.frame_cache import reset_frame_cache_for_tests
    from parrot.brain.vision.tool_lifecycle import reset_visual_tool_lifecycle_for_tests

    ledger = get_evidence_ledger()
    ledger.reset_for_tests()
    reset_frame_cache_for_tests()
    reset_visual_tool_lifecycle_for_tests()
    monkeypatch.setenv(
        "PARROT_LIVEKIT_FRAME_SAMPLER_STATUS_PATH",
        str(tmp_path / "missing-sampler-status.json"),
    )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    status = client.get("/api/vision/evidence/status").json()
    request = client.post(
        "/api/vision/evidence/request",
        json={"description": "what is in the highlighted region", "target_time_ms": 1},
    ).json()
    attention = client.post(
        "/api/app/test/visual-attention",
        json={
            "kind": "bbox",
            "subject_id": "bb_test_web",
            "label": "test bbox",
            "dispatch_harness": False,
            "timebase": {
                "clock_domain": "web",
                "wall_time_ms": 1_700_000_000_000,
                "source_id": "pytest",
            },
        },
    ).json()
    lifecycle = client.post(
        "/api/vision/evidence/tool-lifecycle",
        json={
            "tool_id": "bb_web_lifecycle",
            "tool_kind": "bbox",
            "interaction_phase": "confirm",
            "region": {"x": 0.2, "y": 0.2, "width": 0.3, "height": 0.3},
            "delivery_preference": "intent_only",
        },
    ).json()
    timeline = client.get("/api/vision/evidence/timeline?kind=bbox_focus").json()
    detail = client.get(
        f"/api/vision/evidence/{attention['evidence']['evidence_id']}"
    ).json()

    assert status["action"] == "vision.evidence.status"
    assert status["livekit_sampler"]["message"] == "status_file_missing"
    assert request["action"] == "vision.evidence.request"
    assert request["message"] == "evidence_request_recorded"
    assert attention["action"] == "app.test.visual_attention"
    assert attention["evidence"]["kind"] == "bbox_focus"
    assert lifecycle["success"] is True
    assert lifecycle["delivery"]["resolved_channel"] == "intent_workspace"
    evidence_ids = {row["evidence_id"] for row in timeline["items"]}
    assert attention["evidence"]["evidence_id"] in evidence_ids
    assert lifecycle["evidence"]["evidence_id"] in evidence_ids
    assert detail["success"] is True


def test_vision_frame_cache_upload_records_video_frame(tmp_path) -> None:
    from parrot.brain.vision.evidence import get_evidence_ledger
    from parrot.brain.vision.frame_cache import reset_frame_cache_for_tests

    ledger = get_evidence_ledger()
    ledger.reset_for_tests()
    reset_frame_cache_for_tests(root=tmp_path)
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    dry = client.post(
        "/api/vision/evidence/frame-cache/upload",
        json={
            "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII=",
            "mime_type": "image/png",
            "track_sid": "track-web-test",
        },
    ).json()
    applied = client.post(
        "/api/vision/evidence/frame-cache/upload",
        json={
            "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII=",
            "mime_type": "image/png",
            "room_id": "parrot-test",
            "track_sid": "track-web-test",
            "source_id": "track-web-test",
            "wall_time_ms": 1_700_000_020_000,
            "media_time_us": 55_000,
            "sequence": 3,
            "dry_run": False,
            "operator_mode": True,
        },
    ).json()
    request = client.post(
        "/api/vision/evidence/request",
        json={"target_time_ms": 1_700_000_020_001, "require_asset": True},
    ).json()
    timeline = client.get("/api/vision/evidence/timeline?kind=video_frame").json()

    assert dry["success"] is True
    assert dry["data"]["apply_skipped_reason"] == "dry_run_or_operator_mode_missing"
    assert applied["action"] == "vision.evidence.frame_cache.upload"
    assert applied["success"] is True
    assert applied["evidence"]["kind"] == "video_frame"
    assert applied["evidence"]["asset_exists"] is True
    assert applied["frame_cache"]["frame_count"] == 1
    assert request["message"] == "nearest_evidence_found"
    assert request["evidence"]["evidence_id"] == applied["evidence"]["evidence_id"]
    assert timeline["items"][0]["evidence_id"] == applied["evidence"]["evidence_id"]
    assert "sk-" not in str(applied).lower()


def test_vision_screen_share_smoke_is_read_only_and_checks_source(tmp_path, monkeypatch) -> None:
    from parrot.brain.vision.evidence import get_evidence_ledger
    from parrot.brain.vision.frame_cache import (
        record_livekit_frame_bytes,
        reset_frame_cache_for_tests,
    )

    ledger = get_evidence_ledger()
    ledger.reset_for_tests()
    reset_frame_cache_for_tests(root=tmp_path)
    monkeypatch.setenv(
        "PARROT_LIVEKIT_FRAME_SAMPLER_STATUS_PATH",
        str(tmp_path / "missing-sampler-status.json"),
    )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    empty = client.get("/api/vision/evidence/screen-share-smoke").json()
    assert empty["action"] == "livekit.screen_share.evidence_check"
    assert empty["success"] is False
    assert empty["audit"]["no_pending_request_written"] is True
    assert ledger.status()["sample_count"] == 0

    sample = record_livekit_frame_bytes(
        b"fake-screen-frame",
        mime_type="image/png",
        room_id="parrot-test",
        track_sid="track-screen",
        participant_id="web-console",
        source_id="web-console-screen",
        wall_time_ms=int(time.time() * 1000),
        sequence=1,
        description="Web Console screen-share frame",
        meta={"publication_source": "SOURCE_SCREEN_SHARE"},
    )
    confirmed = client.get("/api/vision/evidence/screen-share-smoke?window_ms=15000").json()

    assert confirmed["success"] is True
    assert confirmed["message"] == "screen_share_evidence_confirmed"
    assert confirmed["data"]["screen_share_confirmed"] is True
    assert confirmed["data"]["likely_screen_share"] is True
    assert confirmed["data"]["nearest_evidence_id"] == sample.evidence_id
    assert confirmed["data"]["frame_cache_count"] == 1
    assert "sk-" not in str(confirmed).lower()


def test_vision_screen_share_smoke_accepts_livekit_js_source_name(tmp_path, monkeypatch) -> None:
    from parrot.brain.vision.evidence import get_evidence_ledger
    from parrot.brain.vision.frame_cache import (
        record_livekit_frame_bytes,
        reset_frame_cache_for_tests,
    )

    get_evidence_ledger().reset_for_tests()
    reset_frame_cache_for_tests(root=tmp_path)
    monkeypatch.setenv(
        "PARROT_LIVEKIT_FRAME_SAMPLER_STATUS_PATH",
        str(tmp_path / "missing-sampler-status.json"),
    )
    record_livekit_frame_bytes(
        b"fake-js-screen-frame",
        mime_type="image/png",
        room_id="parrot-test",
        track_sid="track-screen-js",
        participant_id="web-console",
        source_id="screen_share",
        wall_time_ms=int(time.time() * 1000),
        sequence=1,
        description="LiveKit JS screen-share frame",
        meta={"publication_source": "screen_share"},
    )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    check = client.get("/api/vision/evidence/screen-share-smoke?window_ms=15000").json()

    assert check["success"] is True
    assert check["message"] == "screen_share_evidence_confirmed"
    assert check["data"]["screen_share_confirmed"] is True
    assert check["data"]["likely_screen_share"] is True


def test_vision_screen_share_smoke_does_not_mix_stale_screen_with_fresh_camera(
    tmp_path,
    monkeypatch,
) -> None:
    from parrot.brain.vision.evidence import get_evidence_ledger
    from parrot.brain.vision.frame_cache import (
        record_livekit_frame_bytes,
        reset_frame_cache_for_tests,
    )

    ledger = get_evidence_ledger()
    ledger.reset_for_tests()
    reset_frame_cache_for_tests(root=tmp_path)
    sampler_status_path = tmp_path / "sampler-status.json"
    now_ms = int(time.time() * 1000)
    sampler_status_path.write_text(
        json.dumps(
            {
                "available": True,
                "enabled": True,
                "fresh_window_ms": 15_000,
                "recorded_frames": 7,
                "active_tracks": ["stale-screen"],
                "latest_frame": {
                    "evidence_id": "ev_stale_screen",
                    "track_sid": "stale-screen",
                    "track_name": "web-console-screen",
                    "source_id": "web-console-screen",
                    "publication_source": "SOURCE_SCREEN_SHARE",
                    "wall_time_ms": now_ms - 120_000,
                    "asset_exists": True,
                },
                "tracks": {
                    "stale-screen": {
                        "evidence_id": "ev_stale_screen",
                        "track_sid": "stale-screen",
                        "track_name": "web-console-screen",
                        "publication_source": "SOURCE_SCREEN_SHARE",
                        "wall_time_ms": now_ms - 120_000,
                        "asset_exists": True,
                    }
                },
                "updated_at_ms": now_ms,
                "schema": "LiveKitFrameSampler.web_backend_v1",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("PARROT_LIVEKIT_FRAME_SAMPLER_STATUS_PATH", str(sampler_status_path))
    record_livekit_frame_bytes(
        b"fresh-camera-frame",
        mime_type="image/png",
        room_id="parrot-test",
        track_sid="track-camera",
        participant_id="unity-phone",
        source_id="ar-camera",
        wall_time_ms=now_ms,
        sequence=1,
        description="fresh camera frame",
        meta={"publication_source": "SOURCE_CAMERA"},
    )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    check = client.get("/api/vision/evidence/screen-share-smoke?window_ms=15000").json()

    assert check["success"] is False
    assert check["message"] == "screen_share_track_seen_but_stale"
    assert check["data"]["fresh_any_evidence"] is True
    assert check["data"]["likely_screen_share"] is True
    assert check["data"]["fresh_screen_share"] is False
    assert check["data"]["frame_cache_count"] == 1
    assert any("stale" in step.lower() for step in check["data"]["next_steps"])
    assert not any("Memory Draft" in step for step in check["data"]["next_steps"])


def test_vision_evidence_stage_hint_writes_intent_workspace_notice(tmp_path, monkeypatch) -> None:
    import py_trees

    from parrot.brain.intent_workspace import IntentWorkspace, set_intent_workspace_for_test
    from parrot.brain.vision.evidence import (
        ClockDomain,
        EvidenceKind,
        EvidenceStatus,
        TimebaseStamp,
        get_evidence_ledger,
    )

    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    set_intent_workspace_for_test(IntentWorkspace())
    monkeypatch.setenv(
        "PARROT_LIVEKIT_FRAME_SAMPLER_STATUS_PATH",
        str(tmp_path / "missing-sampler-status.json"),
    )
    ledger = get_evidence_ledger()
    ledger.reset_for_tests()
    sample = ledger.record_sample(
        kind=EvidenceKind.IMAGE_ASSET,
        status=EvidenceStatus.READY,
        timebase=TimebaseStamp(clock_domain=ClockDomain.WEB, wall_time_ms=1_700_000_020_000),
        description="staged red mug",
    )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    try:
        staged = client.post(
            "/api/vision/evidence/stage-hint",
            json={"evidence_id": sample.evidence_id, "description": "staged red mug"},
        ).json()
        status = client.get("/api/vision/evidence/status").json()

        assert staged["action"] == "vision.evidence.stage_hint"
        assert staged["success"] is True
        assert staged["decision"]["staged_ref_id"]
        assert status["evidence_awareness"]["staged_ref_id"] == staged["decision"]["staged_ref_id"]
        assert "sk-" not in str(staged).lower()
    finally:
        set_intent_workspace_for_test(None)


def test_vision_evidence_memory_draft_returns_l15_and_ref_plan(tmp_path, monkeypatch) -> None:
    from parrot.brain.vision.evidence import (
        ClockDomain,
        EvidenceKind,
        EvidenceStatus,
        TimebaseStamp,
        get_evidence_ledger,
    )

    monkeypatch.setenv(
        "PARROT_LIVEKIT_FRAME_SAMPLER_STATUS_PATH",
        str(tmp_path / "missing-sampler-status.json"),
    )
    ledger = get_evidence_ledger()
    ledger.reset_for_tests()
    image_path = tmp_path / "memory-draft.jpg"
    image_path.write_bytes(b"fake-jpeg")
    sample = ledger.record_sample(
        kind=EvidenceKind.IMAGE_ASSET,
        status=EvidenceStatus.READY,
        timebase=TimebaseStamp(
            clock_domain=ClockDomain.WEB,
            wall_time_ms=1_700_000_050_000,
            source_id="pytest",
        ),
        asset_path=str(image_path),
        mime_type="image/jpeg",
        related_refs=("ref-photo-test",),
        description="photo evidence for memory draft",
    )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    draft = client.post(
        "/api/vision/evidence/memory-draft",
        json={
            "evidence_id": sample.evidence_id,
            "target_node_uuid": "node_existing",
            "label": "Desk photo evidence",
            "dry_run": True,
        },
    ).json()

    assert draft["action"] == "vision.evidence.memory_draft"
    assert draft["success"] is True
    assert draft["dry_run"] is True
    assert draft["data"]["observation"]["kind"] == "photo"
    assert draft["data"]["observation"]["meta"]["evidence_id"] == sample.evidence_id
    assert draft["data"]["observation"]["meta"]["target_node_uuid"] == "node_existing"
    assert draft["data"]["ref_binding_draft"]["ref_id"] == "ref-photo-test"
    assert draft["data"]["ref_binding_draft"]["target_kind"] == "l2b_node"
    assert draft["data"]["write_paths"]["node"].startswith("L15Pool.admit")
    assert draft["data"]["apply_status"] == "not_implemented_until_CORE_012_review"
    assert draft["audit"]["read_only"] is True
    assert draft["audit"]["no_l2b_mutation"] is True
    assert draft["audit"]["no_ref_binding_mutation"] is True
    assert draft["core_candidate"] == "CORE-012"
    assert "sk-" not in str(draft).lower()


def test_vision_evidence_memory_draft_missing_sample_is_safe(tmp_path, monkeypatch) -> None:
    from parrot.brain.vision.evidence import get_evidence_ledger

    monkeypatch.setenv(
        "PARROT_LIVEKIT_FRAME_SAMPLER_STATUS_PATH",
        str(tmp_path / "missing-sampler-status.json"),
    )
    get_evidence_ledger().reset_for_tests()
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    draft = client.post(
        "/api/vision/evidence/memory-draft",
        json={"evidence_id": "missing-evidence", "dry_run": True},
    ).json()

    assert draft["action"] == "vision.evidence.memory_draft"
    assert draft["success"] is False
    assert draft["audit"]["read_only"] is True
    assert draft["audit"]["no_l15_mutation"] is True
    assert draft["data"]["error"] == "evidence_not_found"
    assert draft["data"]["core_candidates"] == ["CORE-012", "CORE-006", "CORE-008"]


async def _fake_fetcher(config: OrchestratorProxyConfig) -> dict[str, Any]:
    return {
        "ok": False,
        "state": "offline",
        "upstream": {
            "url": config.status_url,
            "status_code": None,
            "auth_mode": config.auth_mode,
            "fetched_at": 1.0,
        },
        "summary": {},
        "status": None,
        "detail": {"message": "fake"},
    }


async def _fake_plan_dispatch(task_type: str, params: dict, priority: str) -> str:
    return f"task-{task_type}-{params.get('step_id', 'step')}-{priority}"


class _FakeSnapshot:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def as_json(self) -> dict[str, Any]:
        return self._payload


class _FakeStatus:
    def as_json(self) -> dict[str, Any]:
        return {
            "module_id": "voice_pipeline",
            "state": "ready",
            "summary": "fake",
            "metrics": {},
            "refs": {},
        }


class _FakeActionResult:
    def as_json(self) -> dict[str, Any]:
        return {"status": "ok", "workspace_id": "workdesk"}


@dataclass
class _FakeAdmitOutcome:
    rejected: tuple[Any, ...] = ()


class _FakeAppFacade:
    def canvas_snapshot(self) -> _FakeSnapshot:
        return _FakeSnapshot(
            {
                "active_workspace_id": "workdesk",
                "module_statuses": [_FakeStatus().as_json()],
                "workspaces": [{"workspace_id": "workdesk", "display_name": "Workdesk"}],
                "paper_notes": [],
                "photo_refs": [],
                "tool_cabinet": [],
            }
        )

    def list_module_statuses(self) -> list[_FakeStatus]:
        return [_FakeStatus()]

    def list_line_profiles(self) -> list[dict[str, Any]]:
        return [{"line_profile_id": "lineb_google_default"}]

    def apply_line_profile(self, draft_or_id: dict[str, Any] | str) -> dict[str, Any]:
        return {"line_profile": draft_or_id}

    def apply_workspace(self, workspace_id: str) -> _FakeActionResult:
        return _FakeActionResult()

    def set_lineb_audio_route_policy(self, **kwargs: Any) -> dict[str, Any]:
        return kwargs

    def register_lineb_tts_segment(self, **kwargs: Any) -> dict[str, Any]:
        return {"segment_id": "seg_fake", **kwargs}

    def classify_lineb_mic_input(self, **kwargs: Any) -> dict[str, Any]:
        return {"turn_decision": "user_turn", **kwargs}
