from __future__ import annotations

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
    assert "/assets/app.js" in response.text
    assert response.headers["Cache-Control"] == "no-store"

    asset = client.get("/assets/app.js")
    assert asset.status_code == 200
    assert asset.headers["Cache-Control"] == "no-store"

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


def test_graphiti_status_search_and_dry_run_routes_are_exposed(monkeypatch) -> None:
    from parrot.brain import graphiti_console

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
    assert status["data"]["partitions"] == ["goslo", "maid", "scene", "user"]
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

    assert pool["success"] is True
    assert "main" in {item["kind"] for item in pool["buckets"]}
    assert pool["audit"]["web_only"] is True
    assert bucket_draft["data"]["bucket_op"]["op"] == "freeze"
    assert bucket_apply_dry_run["action"] == "l15.bucket_op.apply"
    assert bucket_apply_dry_run["data"]["would_apply"] is True
    assert bucket_apply_dry_run["data"]["apply_skipped_reason"] == "dry_run_or_operator_mode_missing"
    assert daily_obsidian["success"] is True
    assert daily_obsidian["data"]["uuid_free_allowed"] is True
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
        json={"from_uuid": "node_a", "to_uuid": "node_b", "kind": "associated_with"},
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
    assert self_edge["success"] is False
    assert self_edge["data"]["error"] == "self_edge_not_allowed"


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
