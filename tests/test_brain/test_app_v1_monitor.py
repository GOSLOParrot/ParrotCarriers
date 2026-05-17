from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import py_trees
import pytest

from parrot.brain import refs as refs_registry
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


def test_monitor_exposes_runtime_workflow_draft_routes(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    from fastapi.testclient import TestClient

    monkeypatch.setenv("PARROT_WEB_CONSOLE_WORKFLOW_DRAFTS_PATH", str(tmp_path / "workflow_drafts.json"))
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
                "sample_payload": {"api_token": "redact-me"},
            },
        }
    ]

    catalog = client.get("/api/runtime/capabilities/catalog?q=workflow&kind=workflow_template").json()
    saved = client.post(
        "/api/runtime/workflows/drafts",
        json={"workflow_id": "monitor-workflow", "title": "Monitor workflow", "workflow_nodes": nodes},
    ).json()
    loaded = client.get("/api/runtime/workflows/drafts/monitor-workflow").json()
    contract = client.post("/api/runtime/workflow/result-contract", json={"workflow_id": "monitor-workflow"}).json()
    plan = client.post("/api/runtime/workflow/plan-draft", json={"workflow_id": "monitor-workflow"}).json()
    run = client.post("/api/runtime/workflow/run", json={"workflow_id": "monitor-workflow"}).json()
    deleted = client.delete("/api/runtime/workflows/drafts/monitor-workflow").json()

    assert any(row["capability_id"] == "runtime.workflow_drafts.registry" for row in catalog["capabilities"])
    assert any(row["capability_id"] == "runtime.workflow.result_contract" for row in catalog["capabilities"])
    assert saved["success"] is True
    assert loaded["draft"]["nodes"][0]["capability"]["sample_payload"]["api_token"] == "[REDACTED]"
    assert contract["success"] is True
    assert contract["data"]["result_contract"]["schema"] == "workflow_result_contract_v1"
    assert plan["success"] is True
    assert plan["data"]["steps"][0]["expected_tool"] == "ref_scan"
    assert plan["data"]["steps"][0]["inputs"]["result_routes"][0]["destination"] == "view_only"
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
