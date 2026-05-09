from __future__ import annotations

import py_trees
import pytest

from parrot.brain.app_monitor_server import build_app
from parrot.brain.app_v1_self_check import run_app_v1_self_check
from parrot.brain.intent_workspace import IntentWorkspace, set_intent_workspace_for_test
from parrot.brain.l2b_monitor import build_l2b_snapshot
from parrot.brain.preset_loader import PresetLoader, set_preset_loader_for_test
from parrot.brain.workspace_registry import WorkspaceRegistry, set_workspace_registry_for_test
from parrot.dsg.l2b_graph import L2BGraph
from parrot.dsg.l2b_types import SemanticEdge, SemanticNode


@pytest.fixture(autouse=True)
def _reset_state(tmp_path):
    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    set_intent_workspace_for_test(IntentWorkspace())
    set_preset_loader_for_test(PresetLoader(search_paths=[tmp_path / "presets"]))
    set_workspace_registry_for_test(WorkspaceRegistry(search_paths=[tmp_path / "workspaces"]))
    yield
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
    assert "L2-B Topology" in page.text
    assert "/pixel-assets/curated/00_previews/Paper_UI_preview.png" in page.text
    assert health.status_code == 200
    assert health.json()["service"] == "app-v1-monitor"
    assert canvas.status_code == 200
    body = canvas.json()
    assert len(body["module_statuses"]) == 7
    assert any(w["workspace_id"] == "workdesk" for w in body["workspaces"])


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
