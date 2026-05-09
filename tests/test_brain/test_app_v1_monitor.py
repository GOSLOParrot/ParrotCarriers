from __future__ import annotations

import py_trees
import pytest

from parrot.brain import refs as refs_registry
from parrot.brain.app_monitor_server import build_app
from parrot.brain.app_v1_self_check import run_app_v1_self_check
from parrot.brain.intent_workspace import IntentWorkspace, set_intent_workspace_for_test
from parrot.brain.l2b_monitor import build_l2b_snapshot
from parrot.brain.preset_loader import PresetLoader, set_preset_loader_for_test
from parrot.brain.workspace_registry import WorkspaceRegistry, set_workspace_registry_for_test
import parrot.dsg.l2b_graph as l2b_graph_module
from parrot.dsg.l2b_graph import L2BGraph
from parrot.dsg.l2b_types import SemanticEdge, SemanticNode


@pytest.fixture(autouse=True)
def _reset_state(tmp_path):
    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    refs_registry.reset_refs_for_tests()
    set_intent_workspace_for_test(IntentWorkspace())
    l2b_graph_module._instance = L2BGraph()
    set_preset_loader_for_test(PresetLoader(search_paths=[tmp_path / "presets"]))
    set_workspace_registry_for_test(WorkspaceRegistry(search_paths=[tmp_path / "workspaces"]))
    yield
    refs_registry.reset_refs_for_tests()
    l2b_graph_module._instance = None
    set_intent_workspace_for_test(None)
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


def test_monitor_health_and_canvas_endpoints() -> None:
    from fastapi.testclient import TestClient

    client = TestClient(build_app())

    page = client.get("/")
    health = client.get("/health")
    canvas = client.get("/api/app/canvas")

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
    assert canvas.status_code == 200
    body = canvas.json()
    assert len(body["module_statuses"]) == 7
    assert any(w["workspace_id"] == "workdesk" for w in body["workspaces"])
    assert len(body["tool_cabinet"]) >= 6
    assert body["asset_manifest"]["schema_version"] == 1


def test_console_action_endpoints_drive_app_tool_flows() -> None:
    from fastapi.testclient import TestClient

    client = TestClient(build_app())

    before = client.get("/api/app/live-state")
    camera = client.post(
        "/api/app/camera/capture-request",
        json={"candidate_subject_uuid": "obj_console"},
    )
    focus = client.post("/api/app/test/focus", json={"focus_id": "fc_console"})
    bbox = client.post("/api/app/test/bbox", json={"bbox_id": "bb_console"})
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
    assert focus.status_code == 200 and focus.json()["success"] is True
    assert bbox.status_code == 200 and bbox.json()["success"] is True
    assert photo.status_code == 200 and photo.json()["success"] is True
    assert report.status_code == 200 and report.json()["success"] is True
    assert graphiti.status_code == 200 and graphiti.json()["success"] is True
    assert draft.status_code == 200
    assert draft.json()["data"]["draft"]["group_id"] == "goslo"
    assert refs_registry.metrics_snapshot()["focus_refs"] == 1
    assert refs_registry.metrics_snapshot()["bbox_refs"] == 1
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
