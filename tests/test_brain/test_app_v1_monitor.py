from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import py_trees
import pytest

from parrot.brain import refs as refs_registry
from parrot.brain import app_monitor_server
from parrot.brain.app_monitor_server import build_app
from parrot.brain.app_v1_self_check import run_app_v1_self_check
from parrot.brain.intent_workspace import IntentWorkspace, set_intent_workspace_for_test
from parrot.brain.lineb_audio_guard import reset_lineb_audio_guard_for_test
from parrot.brain.l2b_monitor import build_l2b_snapshot
from parrot.brain.persona_loader import set_persona_loader_for_test
from parrot.brain.preset_loader import PresetLoader, set_preset_loader_for_test
from parrot.brain.vision.evidence import get_evidence_ledger
from parrot.brain.vision.tool_lifecycle import reset_visual_tool_lifecycle_for_tests
from parrot.brain.workspace_registry import WorkspaceRegistry, set_workspace_registry_for_test
import parrot.dsg.l2b_graph as l2b_graph_module
from parrot.dsg.l2b_graph import L2BGraph
from parrot.dsg.l2b_types import SemanticEdge, SemanticNode


@pytest.fixture(autouse=True)
def _reset_state(tmp_path, monkeypatch: pytest.MonkeyPatch):
    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    reset_lineb_audio_guard_for_test()
    refs_registry.reset_refs_for_tests()
    get_evidence_ledger().reset_for_tests()
    reset_visual_tool_lifecycle_for_tests()
    monkeypatch.setenv("PARROT_VISUAL_TOOL_ASSET_ROOT", str(tmp_path / "visual_tools"))
    set_intent_workspace_for_test(IntentWorkspace())
    l2b_graph_module._instance = L2BGraph()
    set_persona_loader_for_test(None)
    set_preset_loader_for_test(PresetLoader(search_paths=[tmp_path / "presets"]))
    set_workspace_registry_for_test(WorkspaceRegistry(search_paths=[tmp_path / "workspaces"]))
    yield
    reset_lineb_audio_guard_for_test()
    refs_registry.reset_refs_for_tests()
    get_evidence_ledger().reset_for_tests()
    reset_visual_tool_lifecycle_for_tests()
    l2b_graph_module._instance = None
    set_intent_workspace_for_test(None)
    set_persona_loader_for_test(None)
    set_preset_loader_for_test(None)
    set_workspace_registry_for_test(None)


def test_l2b_snapshot_exports_nodes_and_edges_read_only() -> None:
    graph = L2BGraph()
    graph.upsert_node(SemanticNode(uuid="a", label="calendar event"))
    graph.upsert_node(SemanticNode(uuid="b", label="paper note"))
    graph.connect("a", "b", SemanticEdge(strength=0.8, source="unit_test"))

    snapshot = build_l2b_snapshot(graph).as_json()

    assert snapshot["node_count"] == 2
    assert snapshot["edge_count"] == 1
    assert snapshot["nodes"][0]["uuid"] == "a"
    assert snapshot["edges"][0]["source"] == "a"
    assert snapshot["edges"][0]["target"] == "b"


def test_app_monitor_proxies_live_state_to_brain_room_job(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from fastapi.testclient import TestClient

    monkeypatch.setenv(
        "PARROT_APP_MONITOR_BRAIN_LIVE_STATE_URL",
        "http://brain:7889",
    )
    calls: list[tuple[str, str]] = []

    def fake_fetch(base_url: str, path: str) -> dict[str, Any]:
        calls.append((base_url, path))
        if path.startswith("/api/app/live-state"):
            return {
                "generated_at": 1.0,
                "sequence": 7,
                "blackboard": {},
                "intent_workspace": {},
                "refs": {},
                "l2b": {
                    "node_count": 1,
                    "edge_count": 0,
                    "nodes": [{"uuid": "ph_real_phone", "kind": "photo"}],
                    "edges": [],
                },
                "tool_artifacts": [],
                "audit": {"source_process": "brain.photo_upload_server"},
            }
        return {
            "node_count": 1,
            "edge_count": 0,
            "nodes": [{"uuid": "ph_real_phone", "kind": "photo"}],
            "edges": [],
        }

    monkeypatch.setattr(
        app_monitor_server,
        "_fetch_brain_live_state_json_sync",
        fake_fetch,
    )

    client = TestClient(app_monitor_server.build_app())
    live = client.get("/api/app/live-state?limit=12").json()
    l2b = client.get("/api/l2b/snapshot?limit=12").json()

    assert live["l2b"]["nodes"][0]["uuid"] == "ph_real_phone"
    assert live["audit"]["app_monitor_proxy"]["source"] == "brain_room_job"
    assert live["audit"]["app_monitor_proxy"]["read_only"] is True
    assert l2b["nodes"][0]["uuid"] == "ph_real_phone"
    assert l2b["app_monitor_proxy"]["route"] == "/api/l2b/snapshot"
    assert calls == [
        ("http://brain:7889", "/api/app/live-state?limit=12"),
        ("http://brain:7889", "/api/l2b/snapshot?limit=12"),
    ]


def test_app_monitor_proxies_operator_l2b_write_to_brain_room_job(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from fastapi.testclient import TestClient

    monkeypatch.setenv(
        "PARROT_APP_MONITOR_BRAIN_LIVE_STATE_URL",
        "http://brain:7889",
    )
    calls: list[tuple[str, str, dict[str, Any]]] = []

    def fake_post(base_url: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        calls.append((base_url, path, payload))
        return {
            "success": True,
            "action": "l2b.subgraph.apply",
            "dry_run": False,
            "operator_mode": True,
            "data": {
                "direct_l2b_write": True,
                "member_node_uuids": ["node-from-brain"],
            },
        }

    monkeypatch.setattr(
        app_monitor_server,
        "_post_brain_live_state_json_sync",
        fake_post,
    )

    client = TestClient(app_monitor_server.build_app())
    body = client.post(
        "/api/l2b/subgraphs/apply",
        json={
            "label": "Brain write proxy smoke",
            "node_uuids": ["node-from-brain"],
            "dry_run": False,
            "operator_mode": True,
        },
    ).json()

    assert body["success"] is True
    assert body["action"] == "l2b.subgraph.apply"
    assert body["data"]["direct_l2b_write"] is True
    assert body["data"]["brain_write_proxy"]["source"] == "brain_room_job"
    assert body["data"]["brain_write_proxy"]["read_write"] is True
    assert calls == [
        (
            "http://brain:7889",
            "/api/l2b/subgraphs/apply",
            {
                "label": "Brain write proxy smoke",
                "node_uuids": ["node-from-brain"],
                "dry_run": False,
                "operator_mode": True,
                "_remote_proxy_disable": True,
                "_brain_proxy_disable": True,
            },
        )
    ]


def test_monitor_health_and_canvas_endpoints() -> None:
    from fastapi.testclient import TestClient

    client = TestClient(build_app())

    page = client.get("/")
    health = client.get("/health")
    console_config = client.get("/api/console/config")
    canvas = client.get("/api/app/canvas")
    memory_changes = client.get("/api/memory/live-state/changes?since=0&limit=4")
    l15_pool = client.get("/api/l15/pool")
    runtime_changes = client.get("/api/runtime/flow/changes?since=0")
    trigger_catalog = client.get("/api/dsg/triggers/catalog")

    assert page.status_code == 200
    assert "Module Rail" in page.text
    assert "Canvas Workspace" in page.text
    assert "Live State" in page.text
    assert "Blackboard Live" in page.text
    assert "IntentWorkspace Live" in page.text
    assert "Tool Artifacts" in page.text
    assert "Tool Flow" in page.text
    assert "Graphiti Core" in page.text
    assert "L2-B Topology" in page.text
    assert "L2-B Live Graph" in page.text
    assert "function fieldValue" in page.text
    assert "value('cameraMode')" not in page.text
    assert "/pixel-assets/curated/00_previews/Paper_UI_preview.png" in page.text
    assert health.status_code == 200
    assert health.json()["service"] == "app-v1-monitor"
    assert console_config.status_code == 200
    assert console_config.json()["environment"]["service"] == "app-monitor"
    assert "local_laptop_app_api_secret_change_me" not in json.dumps(console_config.json())
    assert memory_changes.status_code == 200
    assert memory_changes.json()["event_schema"] == "memory_runtime_delta_v1"
    assert l15_pool.status_code == 200
    assert l15_pool.json()["success"] is True
    assert runtime_changes.status_code == 200
    assert runtime_changes.json()["event_schema"] == "runtime_flow_delta_v1"
    assert trigger_catalog.status_code == 200
    assert trigger_catalog.json()["action"] == "trigger_catalog"
    assert canvas.status_code == 200
    body = canvas.json()
    assert len(body["module_statuses"]) == 8
    assert any(w["workspace_id"] == "workdesk" for w in body["workspaces"])
    assert len(body["tool_cabinet"]) >= 6
    assert body["asset_manifest"]["schema_version"] == 1


def test_monitor_exposes_graphiti_materialize_and_l2b_context_routes() -> None:
    from fastapi.testclient import TestClient

    client = TestClient(build_app())

    materialize = client.post(
        "/api/graphiti/subgraph/materialize-l2b",
        json={
            "partition": "noble_etiquette",
            "query": "formal greeting",
            "graphiti_bundle": {
                "partition": "noble_etiquette",
                "query": "formal greeting",
                "sections": {
                    "episodes": [
                        {
                            "uuid": "episode-noble-route-1",
                            "raw": {
                                "uuid": "episode-noble-route-1",
                                "content": "A formal greeting acknowledges relative rank.",
                            },
                        }
                    ]
                },
            },
            "dry_run": True,
        },
    ).json()
    context = client.post("/api/l2b/subgraphs/context", json={}).json()

    assert materialize["action"] == "graphiti.subgraph.materialize_l2b"
    assert materialize["success"] is True
    assert materialize["data"]["direct_l2b_write"] is False
    assert materialize["data"]["context_route"] == "/api/l2b/subgraphs/context"
    assert context["action"] == "l2b.subgraph.context"
    assert context["success"] is False
    assert context["data"]["error"] == "missing_node_selection"


def test_monitor_exposes_l2b_node_operator_route_for_web_console() -> None:
    from fastapi.testclient import TestClient

    client = TestClient(build_app())

    node = client.post(
        "/api/l2b/node",
        json={
            "label": "Monitor Web Node",
            "kind": "object",
            "dry_run": False,
            "operator_mode": True,
        },
    ).json()
    live = client.get("/api/app/live-state?limit=20").json()

    assert node["success"] is True
    assert node["action"] == "l2b.node.apply"
    assert node["data"]["admit_outcome"]["rejected"] == []
    monitor_node = next(row for row in live["l2b"]["nodes"] if row["label"] == "Monitor Web Node")

    work_subgraph = client.post(
        "/api/l2b/subgraphs/apply",
        json={
            "label": "Monitor work subgraph",
            "node_uuids": [monitor_node["uuid"]],
            "dry_run": False,
            "operator_mode": True,
        },
    ).json()
    live_after = client.get("/api/app/live-state?limit=40").json()

    assert work_subgraph["action"] == "l2b.subgraph.apply"
    assert work_subgraph["success"] is True
    assert work_subgraph["data"]["direct_l2b_write"] is True
    assert work_subgraph["data"]["member_node_uuids"] == [monitor_node["uuid"]]
    assert any(row["label"] == "Monitor work subgraph" for row in live_after["l2b"]["nodes"])


def test_monitor_exposes_identity_ref_routes_for_ref_scan(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from fastapi.testclient import TestClient

    index_path = tmp_path / "memory_identity_ref_index.json"
    ref_file = tmp_path / "ref.md"
    ref_file.write_text("laptop ref scan route smoke\n", encoding="utf-8")
    monkeypatch.setenv("PARROT_MEMORY_IDENTITY_REF_INDEX_PATH", str(index_path))
    client = TestClient(build_app())
    payload = {
        "canonical_uuid": "canon-monitor-ref-route",
        "l2b_uuid": "l2b-monitor-ref-route",
        "ref_id": "monitor-ref-route",
        "ref_kind": "obsidian_doc",
        "locator": str(ref_file),
        "managed_by": "nanobot",
    }

    draft = client.post("/api/memory/identity-ref-index/draft", json=payload).json()
    applied = client.post(
        "/api/memory/identity-ref-index/apply",
        json={**payload, "dry_run": False, "operator_mode": True},
    ).json()
    snapshot = client.get("/api/memory/identity-ref-index").json()
    plan = client.post(
        "/api/memory/identity-ref-index/ref-scan-plan",
        json={"limit": 10},
    ).json()

    assert draft["action"] == "memory.identity_ref_index.draft"
    assert draft["data"]["would_persist"] is False
    assert applied["action"] == "memory.identity_ref_index.apply"
    assert applied["data"]["mutated"] is True
    assert snapshot["data"]["ref_count"] == 1
    assert plan["action"] == "memory.identity_ref_index.ref_scan_plan"
    assert plan["data"]["counts"]["ref_count"] == 1
    assert plan["data"]["ref_scan_plan"][0]["ref_id"] == "monitor-ref-route"


def test_monitor_exposes_obsidian_source_board_and_photo_routes(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from fastapi.testclient import TestClient

    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "daily.md").write_text(
        "---\n"
        "profile: daily\n"
        "label: Laptop Obsidian Smoke\n"
        "kind: object\n"
        "tags: laptop,smoke\n"
        "---\n"
        "A laptop source-board smoke note can rise into L1.5 as an Obsidian observation.",
        encoding="utf-8",
    )
    photo_day = "2026-05-18"
    photo_id = "monitor_photo_route"
    photo_root = tmp_path / "photos"
    (photo_root / photo_day).mkdir(parents=True)
    photo_bytes = b"\xff\xd8monitor-photo-route\xff\xd9"
    (photo_root / photo_day / f"{photo_id}.jpg").write_bytes(photo_bytes)
    monkeypatch.setenv("PARROT_PHOTO_CACHE_ROOT", str(photo_root))

    client = TestClient(build_app())
    scan = client.get(
        "/api/l15/obsidian-vault/scan",
        params={"vault_path": str(vault), "limit": "8"},
    ).json()
    draft = client.post(
        "/api/l15/obsidian-vault/import-draft",
        json={"vault_path": str(vault), "paths": ["daily.md"], "limit": 8},
    ).json()
    plan = client.post(
        "/api/l15/obsidian-vault/import-plan",
        json={
            "vault_path": str(vault),
            "paths": ["daily.md"],
            "destination": "isolated_compartment",
        },
    ).json()
    dry_apply = client.post(
        "/api/l15/obsidian-vault/import",
        json={
            "vault_path": str(vault),
            "paths": ["daily.md"],
            "dry_run": True,
            "operator_mode": False,
        },
    ).json()
    node_draft = client.post(
        "/api/l15/obsidian-node/draft",
        json={"profile": "daily", "label": "Manual source note", "body": "Draft only."},
    ).json()
    photo = client.get(f"/api/photos/asset/{photo_day}/{photo_id}")
    bad_photo = client.get(f"/api/photos/asset/not-a-day/{photo_id}")

    assert scan["action"] == "l15.obsidian_vault.scan"
    assert scan["success"] is True
    assert scan["data"]["vault"]["status"] == "ingest_ready"
    assert scan["data"]["notes"][0]["path"] == "daily.md"
    assert draft["action"] == "l15.obsidian_vault.import_draft"
    assert draft["success"] is True
    assert draft["data"]["selected_count"] == 1
    assert plan["action"] == "l15.obsidian_vault.import_plan"
    assert plan["success"] is True
    assert plan["data"]["apply_route"] == "/api/l15/obsidian-vault/import"
    assert dry_apply["action"] == "l15.obsidian_vault.import"
    assert dry_apply["data"]["would_apply"] is True
    assert dry_apply["data"]["apply_skipped_reason"] == "dry_run_or_operator_mode_missing"
    assert node_draft["action"] == "l15.obsidian_node.draft"
    assert node_draft["success"] is True
    assert photo.status_code == 200
    assert photo.content == photo_bytes
    assert photo.headers["Cache-Control"] == "no-store"
    assert bad_photo.status_code == 400


def test_monitor_exposes_google_calendar_true_fetch_routes(monkeypatch: pytest.MonkeyPatch) -> None:
    from fastapi.testclient import TestClient
    from parrot.web_console import memory_ops

    api_calls: list[dict[str, Any]] = []
    nanobot_calls: list[dict[str, Any]] = []

    async def fake_api_fetch(**kwargs: Any) -> dict[str, Any]:
        api_calls.append(kwargs)
        return {
            "credential_source": "configured_oauth_file",
            "items": [
                {
                    "id": "evt_monitor_api",
                    "summary": "Monitor API event",
                    "start": {"dateTime": "2026-05-18T09:00:00+08:00"},
                    "end": {"dateTime": "2026-05-18T09:30:00+08:00"},
                }
            ],
        }

    async def fake_nanobot_fetch(**kwargs: Any) -> dict[str, Any]:
        nanobot_calls.append(kwargs)
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
                                        "id": "evt_monitor_nanobot",
                                        "summary": "Monitor Nanobot event",
                                        "start_time": "2026-05-18T10:00:00+08:00",
                                        "end_time": "2026-05-18T10:30:00+08:00",
                                    }
                                ],
                            }
                        )
                    }
                }
            ]
        }

    monkeypatch.setattr(memory_ops, "_fetch_google_calendar_events_from_api", fake_api_fetch)
    monkeypatch.setattr(
        memory_ops,
        "_fetch_google_calendar_events_from_nanobot",
        fake_nanobot_fetch,
    )
    client = TestClient(build_app())

    api = client.post(
        "/api/google/calendar/api-fetch",
        json={
            "calendar_id": "primary",
            "timeMin": "2026-05-18T00:00:00+08:00",
            "timeMax": "2026-05-19T00:00:00+08:00",
            "limit": 2,
        },
    ).json()
    nanobot = client.post(
        "/api/google/calendar/nanobot-fetch",
        json={
            "account": "gosloparrot@gmail.com",
            "calendar_id": "primary",
            "timeMin": "2026-05-18T00:00:00+08:00",
            "timeMax": "2026-05-19T00:00:00+08:00",
            "limit": 2,
        },
    ).json()
    preview = client.post(
        "/api/google/calendar/preview",
        json={"events": [{"id": "evt_monitor_preview", "summary": "Preview"}]},
    ).json()
    message_check = client.post(
        "/api/google/messages/check",
        json={"query": "newer_than:7d"},
    ).json()

    assert api["action"] == "google.calendar.api_fetch"
    assert api["success"] is True
    assert api["data"]["read_model"] == "Google Calendar API events.list via OAuth2"
    assert api["data"]["count"] == 1
    assert api["data"]["credential_source"] == "configured_oauth_file"
    assert nanobot["action"] == "google.calendar.nanobot_fetch"
    assert nanobot["success"] is True
    assert nanobot["data"]["read_model"] == "ECS Nanobot -> Google Workspace MCP manage_calendar"
    assert nanobot["data"]["nanobot_success"] is True
    assert nanobot["data"]["count"] == 1
    assert preview["action"] == "google.calendar.preview"
    assert preview["success"] is True
    assert message_check["action"] == "google.message_check.dispatch"
    assert message_check["success"] is True
    assert message_check["data"]["task_type"] == "message_check"
    assert message_check["data"]["would_dispatch"] is True
    assert api_calls == [
        {
            "calendar_id": "primary",
            "time_min": "2026-05-18T00:00:00+08:00",
            "time_max": "2026-05-19T00:00:00+08:00",
            "limit": 2,
            "show_deleted": False,
        }
    ]
    assert nanobot_calls[0]["account"] == "gosloparrot@gmail.com"
    assert nanobot_calls[0]["limit"] == 2


def test_monitor_exposes_runtime_workflow_draft_routes(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    from fastapi.testclient import TestClient

    monkeypatch.setenv("PARROT_WEB_CONSOLE_WORKFLOW_DRAFTS_PATH", str(tmp_path / "workflow_drafts.json"))
    monkeypatch.setenv("PARROT_WEB_CONSOLE_ACTION_GATES_PATH", str(tmp_path / "workflow_action_gates.json"))
    monkeypatch.setenv("PARROT_WEB_CONSOLE_RESULT_INTAKE_PATH", str(tmp_path / "workflow_result_intake.json"))
    client = TestClient(build_app())
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
                "sample_payload": {"api_token": "redact-me"},
            },
        },
        {
            "workflow_node_id": "wf-message-check",
            "capability": {
                "capability_id": "nanobot.message_check",
                "title": "Message check",
                "kind": "nanobot_task",
                "nanobot_task_type": "message_check",
                "plan_step_compatible": True,
            },
        }
    ]

    catalog = client.get("/api/runtime/capabilities/catalog?q=workflow&kind=workflow_template").json()
    gates_catalog = client.get("/api/runtime/capabilities/catalog?q=action_gates").json()
    intake_catalog = client.get("/api/runtime/capabilities/catalog?q=result_intake").json()
    c3_catalog = client.get("/api/runtime/capabilities/catalog?interaction_mode=C3").json()
    saved = client.post(
        "/api/runtime/workflows/drafts",
        json={"workflow_id": "monitor-workflow", "title": "Monitor workflow", "workflow_nodes": nodes},
    ).json()
    loaded = client.get("/api/runtime/workflows/drafts/monitor-workflow").json()
    validated = client.post("/api/runtime/workflow/validate", json={"workflow": loaded["draft"]}).json()
    exported = client.get("/api/runtime/workflow/export?workflow_id=monitor-workflow").json()
    import_preview = client.post(
        "/api/runtime/workflow/import-preview",
        json={"workflow": exported["data"]["workflow"], "target_workflow": {"nodes": [nodes[0]]}},
    ).json()
    gate = client.post(
        "/api/runtime/workflow/action-gates",
        json={"workflow_id": "monitor-workflow", "workflow_node_id": "wf-message-check"},
    ).json()
    gate_list = client.get("/api/runtime/workflow/action-gates").json()
    gate_preview = client.post(
        "/api/runtime/workflow/action-gates/decision",
        json={"gate_id": gate["data"]["gate"]["gate_id"], "decision": "apply", "dry_run": True},
    ).json()
    intake = client.post(
        "/api/runtime/workflow/result-intake",
        json={
            "workflow_id": "monitor-workflow",
            "workflow_node_id": "wf-ref-scan",
            "result_payload": {"summary": "monitor result"},
            "dry_run": True,
        },
    ).json()
    intake_list = client.get("/api/runtime/workflow/result-intake").json()
    intake_missing_delete = client.delete("/api/runtime/workflow/result-intake/missing-entry").json()
    contract = client.post("/api/runtime/workflow/result-contract", json={"workflow_id": "monitor-workflow"}).json()
    plan = client.post("/api/runtime/workflow/plan-draft", json={"workflow_id": "monitor-workflow"}).json()
    run = client.post("/api/runtime/workflow/run", json={"workflow_id": "monitor-workflow"}).json()
    deleted = client.delete("/api/runtime/workflows/drafts/monitor-workflow").json()

    assert any(row["capability_id"] == "runtime.workflow_drafts.registry" for row in catalog["capabilities"])
    assert any(row["capability_id"] == "runtime.workflow.action_gates" for row in gates_catalog["capabilities"])
    assert any(row["capability_id"] == "runtime.workflow.result_intake" for row in intake_catalog["capabilities"])
    assert any(row["capability_id"] == "runtime.workflow.result_contract" for row in catalog["capabilities"])
    assert any(row["capability_id"] == "runtime.workflow.validate" for row in catalog["capabilities"])
    assert c3_catalog["capabilities"]
    assert all("C3" in row["interaction_modes"] for row in c3_catalog["capabilities"])
    assert saved["success"] is True
    assert loaded["draft"]["nodes"][0]["capability"]["sample_payload"]["api_token"] == "[REDACTED]"
    assert validated["success"] is True
    assert exported["data"]["workflow"]["schema"] == "workflow_schema_v1"
    assert "redact-me" not in str(exported)
    assert import_preview["success"] is True
    assert import_preview["data"]["diff"]["added_nodes"] == ["wf-message-check"]
    assert gate["success"] is True
    assert gate["data"]["gate"]["action_kind"] == "message_check"
    assert gate_list["count"] == 1
    assert gate_preview["data"]["preview_receipt"]["action"] == "google.message_check.draft"
    assert intake["success"] is True
    assert intake["data"]["route_results"][0]["intake_state"] == "preview"
    assert intake["data"]["route_results"][0]["would_stage"] is True
    assert intake["data"]["recorded"] is False
    assert intake_list["count"] == 0
    assert intake_missing_delete["success"] is False
    assert intake_missing_delete["deleted"] is False
    assert contract["success"] is True
    assert contract["data"]["result_contract"]["schema"] == "workflow_result_contract_v1"
    assert plan["success"] is True
    assert plan["data"]["steps"][0]["expected_tool"] == "ref_scan"
    assert plan["data"]["steps"][0]["inputs"]["result_routes"][0]["destination"] == "stage_to_intent_workspace"
    assert run["success"] is True
    assert run["data"]["plan_receipt"]["data"]["steps"][0]["expected_tool"] == "ref_scan"
    assert deleted["deleted"] is True


def test_monitor_personas_endpoint_lists_selector_metadata() -> None:
    from fastapi.testclient import TestClient

    client = TestClient(build_app())

    response = client.get("/api/app/personas")

    assert response.status_code == 200
    personas = response.json()
    assert {row["persona_id"] for row in personas} >= {
        "goslo_parrot_default",
        "ner_companion",
    }
    assert all("text" not in row for row in personas)
    assert all("file_path" not in row for row in personas)


def test_monitor_write_auth_is_optional_but_enforced_when_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from fastapi.testclient import TestClient

    monkeypatch.setenv("PARROT_APP_MONITOR_SECRET", "unit-secret")
    client = TestClient(build_app())

    open_read = client.get("/api/app/personas")
    blocked = client.post("/api/app/room-setting/preview", json={})
    allowed = client.post(
        "/api/app/room-setting/preview",
        json={},
        headers={"Authorization": "Bearer unit-secret"},
    )

    assert open_read.status_code == 200
    assert blocked.status_code == 401
    assert blocked.json()["detail"] == "app_monitor_auth_required"
    assert allowed.status_code == 200
    assert "compatibility" in allowed.json()


def test_console_action_endpoints_drive_app_tool_flows() -> None:
    from fastapi.testclient import TestClient

    client = TestClient(build_app())

    before = client.get("/api/app/live-state")
    camera = client.post(
        "/api/app/camera/capture-request",
        json={"candidate_subject_uuid": "obj_console"},
    )
    xrhand = client.post("/api/app/xrhand/mode", json={"mode": "gesture_select"})
    focus = client.post("/api/app/test/focus", json={"focus_id": "fc_console"})
    bbox = client.post("/api/app/test/bbox", json={"bbox_id": "bb_console"})
    visual_asset = client.post(
        "/api/app/visual-tool/asset/bb_console_crop",
        content=b"fake-image-bytes",
        headers={
            "content-type": "image/png",
            "X-Parrot-Tool-Id": "bb_console_tool",
            "X-Parrot-Tool-Kind": "bbox",
            "X-Parrot-Tool-Phase": "confirm",
            "X-Parrot-Timebase": '{"clock_domain":"unity","wall_time_ms":1777000000000}',
            "X-Parrot-Region": '{"x":0.1,"y":0.1,"width":0.2,"height":0.2}',
        },
    )
    visual_tool = client.post(
        "/api/app/visual-tool/event",
        json={
            "tool_id": "bb_console_tool",
            "tool_kind": "bbox",
            "interaction_phase": "confirm",
            "region": {"x": 0.1, "y": 0.1, "width": 0.2, "height": 0.2},
            "asset_path": visual_asset.json().get("asset_path", ""),
            "mime_type": "image/png",
        },
    )
    photo = client.post(
        "/api/app/test/photo-preview",
        json={"photo_id": "ph_console", "candidate_subject_uuid": "obj_console"},
    )
    report = client.post("/api/app/nanobot/report", json={"title": "Console report"})
    graphiti = client.get("/api/graphiti/status")
    draft = client.post(
        "/api/graphiti/episode/draft",
        json={"name": "console", "body": "draft body", "partition": "goslo"},
    )
    live = client.get("/api/app/live-state")

    assert before.status_code == 200
    assert camera.status_code == 200 and camera.json()["success"] is True
    assert xrhand.status_code == 200 and xrhand.json()["success"] is True
    assert focus.status_code == 200 and focus.json()["success"] is True
    assert bbox.status_code == 200 and bbox.json()["success"] is True
    assert visual_asset.status_code == 200 and visual_asset.json()["success"] is True
    assert visual_asset.json()["evidence"]["kind"] == "image_asset"
    assert visual_tool.status_code == 200 and visual_tool.json()["success"] is True
    assert visual_tool.json()["delivery"]["resolved_channel"] == "c3_context_notice"
    assert visual_tool.json()["evidence"]["kind"] == "image_asset"
    assert photo.status_code == 200 and photo.json()["success"] is True
    assert report.status_code == 200 and report.json()["success"] is True
    assert graphiti.status_code == 200 and graphiti.json()["success"] is True
    assert draft.status_code == 200
    assert draft.json()["data"]["draft"]["group_id"] == "goslo"
    assert refs_registry.metrics_snapshot()["focus_refs"] == 1
    assert refs_registry.metrics_snapshot()["bbox_refs"] == 2
    assert live.status_code == 200
    live_body = live.json()
    bb_keys = {row["key"]: row for row in live_body["blackboard"]["keys"]}
    assert bb_keys["session/photo_capture_request"]["exists"] is True
    assert bb_keys["transient/last_photo_event"]["value"]["photo_id"] == "ph_console"
    assert any(
        row["role"] == "nanobot_report"
        for row in live_body["intent_workspace"]["refs"]
    )
    assert any(
        node["uuid"] == "ph_console" and node["kind"] == "photo"
        for node in live_body["l2b"]["nodes"]
    )
    artifacts = {row["tool_id"]: row for row in live_body["tool_artifacts"]}
    assert artifacts["camera"]["locations"]["blackboard"]["present"] is True
    assert artifacts["camera"]["locations"]["intent_workspace"]["present"] is True
    assert artifacts["camera"]["locations"]["l2b"]["present"] is True
    assert artifacts["magnifier_focus"]["locations"]["ref_registry"]["present"] is True
    assert artifacts["boundary_box"]["locations"]["ref_registry"]["present"] is True
    assert artifacts["workdesk_notes"]["locations"]["intent_workspace"]["present"] is True


def test_monitor_graphiti_routes_forward_search_config_recipe_and_filters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from fastapi.testclient import TestClient
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
                        uuid="fact-monitor-rrf-1",
                        fact="Amiya protects Chernobog civilians.",
                        source_node_uuid="node-monitor-amiya",
                        target_node_uuid="node-monitor-chernobog",
                        score=0.92,
                    )
                ],
                nodes=[],
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
    client = TestClient(build_app())

    search = client.post(
        "/api/graphiti/search",
        json={
            "query": "Amiya Chernobog",
            "partition": "arknights_test",
            "limit": 4,
            "search_recipe": "combined_rrf",
            "node_labels": ["Entity"],
            "edge_types": ["CrisisFact"],
        },
    ).json()
    subgraph = client.post(
        "/api/graphiti/subgraph/search",
        json={
            "query": "Amiya Chernobog",
            "partition": "arknights_test",
            "limit": 4,
            "strategy": "hybrid",
            "search_recipe": "combined_rrf",
            "node_labels": ["Entity"],
            "edge_types": ["CrisisFact"],
            "enrich": False,
        },
    ).json()

    assert search["success"] is True
    assert search["data"]["search_config"]["mode"] == "_search"
    assert subgraph["success"] is True
    assert subgraph["data"]["search_plan"][0]["search_config"]["mode"] == "_search"
    assert len(calls) == 2
    assert calls[0]["group_id"] == "arknights_test"
    assert calls[0]["config"].limit == 4
    assert calls[0]["search_filter"] == {
        "node_labels": ["Entity"],
        "edge_types": ["CrisisFact"],
    }
    assert calls[1]["search_filter"] == calls[0]["search_filter"]


def test_lineb_monitor_endpoints_update_voice_pipeline_refs() -> None:
    from fastapi.testclient import TestClient

    client = TestClient(build_app())

    policy = client.post(
        "/api/app/lineb/audio-route",
        json={
            "input_route": "phone_mic",
            "output_route": "speaker",
            "voiceprint_enabled": True,
        },
    )
    segment = client.post(
        "/api/app/lineb/tts-segment",
        json={
            "text_summary": "hello from LineB",
            "duration_s": 2.0,
            "started_at": 10.0,
            "voiceprint_hash": "vp_agent",
        },
    )
    decision = client.post(
        "/api/app/lineb/mic-input",
        json={
            "observed_at": 10.5,
            "duration_s": 0.2,
            "asr_text": "hello from LineB",
            "voiceprint_hash": "vp_agent",
        },
    )
    modules = client.get("/api/app/modules")

    assert policy.status_code == 200
    assert policy.json()["echo"]["handling_mode"] == "voiceprint_gate"
    assert segment.status_code == 200
    assert decision.status_code == 200
    assert decision.json()["turn_decision"] == "agent_echo"
    voice = next(row for row in modules.json() if row["module_id"] == "voice_pipeline")
    line_b = next(line for line in voice["refs"]["lines"] if line["line_id"] == "line_b")
    assert line_b["readiness"]["recent_tts_segment_count"] == 1
    assert line_b["readiness"]["last_input_decision"] == "agent_echo"


def test_line_profile_monitor_endpoints_preview_and_apply() -> None:
    from fastapi.testclient import TestClient

    client = TestClient(build_app())

    listed = client.get("/api/app/line-profiles")
    preview = client.post(
        "/api/app/line-profiles/preview",
        json={
            "line_profile_id": "lineb_web_preview",
            "display_name": "LineB Web Preview",
            "line_id": "line_b",
            "tts": {
                "tts_profile_id": "tts_preview",
                "language": "ja-JP",
                "voice_name": "",
            },
            "echo": {
                "echo_policy_id": "echo_speaker",
                "output_route": "speaker",
                "handling_mode": "monitor_only",
            },
        },
    )
    applied = client.post(
        "/api/app/line-profiles/apply",
        json={"line_profile_id": "lineb_google_default"},
    )

    assert listed.status_code == 200
    assert any(row["line_profile_id"] == "lineb_google_default" for row in listed.json())
    assert preview.status_code == 200
    assert preview.json()["device_check"]["line_profile_id"] == "lineb_web_preview"
    assert applied.status_code == 200
    assert applied.json()["line_profile"]["line_profile_id"] == "lineb_google_default"


@pytest.mark.asyncio
async def test_app_v1_self_check_reaches_business_targets(tmp_path) -> None:
    result = await run_app_v1_self_check(obsidian_vault_path=tmp_path / "missing")
    body = result.as_json()

    assert body["passed"] is True
    assert {check["name"] for check in body["checks"]} >= {
        "module_status_count",
        "workspace_switch_workdesk",
        "photo_awareness_preview_ref",
        "google_calendar_draft",
        "nanobot_report_note",
        "canvas_snapshot_paper_notes",
    }
