"""BRAIN-PLAN-V1 — Plan-and-Execute state machine + dispatch."""

from __future__ import annotations

import pytest

from parrot.brain.intent_workspace import (
    IntentWorkspace,
    set_intent_workspace_for_test,
)
from parrot.brain.plan import (
    IllegalPlanTransition,
    PlanLifecycle,
    PlanProposal,
    PlanRegistry,
    PlanState,
    PlanStepProposal,
    PlanStepState,
)


def _proposal(
    title: str = "p1",
    *,
    blocks: bool = True,
    steps=None,
) -> PlanProposal:
    if steps is None:
        steps = (
            PlanStepProposal(step_id="s1", title="step1", expected_tool="research"),
            PlanStepProposal(step_id="s2", title="step2", expected_tool="summarize", depends_on=("s1",)),
        )
    return PlanProposal(
        proposed_by="t",
        title=title,
        suggested_steps=steps,
        blocks_conversation=blocks,
    )


@pytest.fixture
def env():
    ws = IntentWorkspace()
    set_intent_workspace_for_test(ws)
    dispatched: list[dict] = []

    async def fake_dispatch(task_type: str, params: dict, priority: str) -> str:
        task_id = f"task_{len(dispatched) + 1}"
        dispatched.append({
            "task_id": task_id,
            "task_type": task_type,
            "params": params,
            "priority": priority,
        })
        return task_id

    registry = PlanRegistry(dispatch_task=fake_dispatch)
    yield {"ws": ws, "registry": registry, "dispatched": dispatched}
    set_intent_workspace_for_test(None)


# ─── Lifecycle transitions ────────────────────────────────────


async def test_draft_creates_plan_with_id(env) -> None:
    plan = await env["registry"].draft(_proposal())
    assert plan.plan_id
    assert plan.state == PlanState.DRAFT
    assert plan.title == "p1"
    assert len(plan.steps) == 2


async def test_draft_stages_to_intent_workspace(env) -> None:
    plan = await env["registry"].draft(_proposal())
    assert plan.staged_ref_id
    ref = env["ws"].fetch(plan.staged_ref_id)
    assert ref is not None


async def test_draft_creates_blackboard_namespace(env) -> None:
    plan = await env["registry"].draft(_proposal())
    assert plan.blackboard_namespace == f"plan/{plan.plan_id}"
    bb = env["registry"].get_blackboard(plan.plan_id)
    assert bb is not None
    bb.set("foo", "bar")
    assert bb.get("foo") == "bar"


async def test_legal_transition_chain_to_complete(env) -> None:
    plan = await env["registry"].draft(_proposal())
    await env["registry"].submit_for_confirmation(plan.plan_id)
    assert plan.state == PlanState.AWAITING_USER_CONFIRMATION
    await env["registry"].approve(plan.plan_id)
    assert plan.state == PlanState.APPROVED
    assert plan.blocks_conversation is False
    await env["registry"].start_executing(plan.plan_id)
    assert plan.state == PlanState.EXECUTING
    assert plan.steps[0].state == PlanStepState.DISPATCHED
    assert plan.steps[1].state == PlanStepState.PENDING
    assert plan.steps[0].nanobot_task_id == "task_1"
    assert env["dispatched"][0]["params"]["plan_id"] == plan.plan_id
    assert env["dispatched"][0]["params"]["step_id"] == "s1"

    await env["registry"].report_step_result(
        plan.plan_id, "s1", success=True, result_summary="ok",
    )
    assert plan.steps[0].state == PlanStepState.DONE
    assert plan.steps[1].state == PlanStepState.DISPATCHED  # cascaded
    assert plan.steps[1].nanobot_task_id == "task_2"
    assert plan.state == PlanState.PARTIAL_COMPLETE

    await env["registry"].report_step_result(
        plan.plan_id, "s2", success=True, result_summary="ok",
    )
    assert plan.state == PlanState.COMPLETE


async def test_calendar_write_plan_step_dispatches_approval_metadata(env) -> None:
    plan = await env["registry"].draft(_proposal(steps=(
        PlanStepProposal(
            step_id="calendar-step",
            title="move tea",
            expected_tool="calendar_patch",
            inputs={"calendar_id": "primary", "event_id": "evt_1"},
        ),
    )))
    await env["registry"].submit_for_confirmation(plan.plan_id)
    await env["registry"].approve(plan.plan_id)
    await env["registry"].start_executing(plan.plan_id)

    params = env["dispatched"][0]["params"]
    assert env["dispatched"][0]["task_type"] == "calendar_patch"
    assert params["result_channel"] == "calendar_result"
    assert params["calendar_write_approved"] is True
    assert params["hitl_approved"] is True
    assert params["approval_source"] == "PlanRegistry.approve"
    assert params["approval_plan_state"] == PlanState.APPROVED.value


async def test_plan_step_waits_for_nanobot_user_decision_then_resumes(env) -> None:
    plan = await env["registry"].draft(_proposal(steps=(
        PlanStepProposal(
            step_id="calendar-mission",
            title="calendar mission",
            expected_tool="calendar_mission",
            inputs={"goal": "find a safe slot", "authority": "draft_only"},
        ),
    )))
    await env["registry"].submit_for_confirmation(plan.plan_id)
    await env["registry"].approve(plan.plan_id)
    await env["registry"].start_executing(plan.plan_id)

    await env["registry"].report_step_result(
        plan.plan_id,
        "calendar-mission",
        success=False,
        status="needs_user_decision",
        result_summary="choose a slot",
        decision_payload={
            "options": [
                {
                    "id": "slot_a",
                    "label": "14:30",
                    "proposed_write": {"action": "create", "event_body": {"summary": "Tea"}},
                }
            ]
        },
    )

    step = plan.step_by_id("calendar-mission")
    assert step is not None
    assert plan.state == PlanState.WAITING_USER_DECISION
    assert step.state == PlanStepState.WAITING_USER_DECISION
    assert step.decision_payload["options"][0]["id"] == "slot_a"

    await env["registry"].resolve_step_user_decision(
        plan.plan_id,
        "calendar-mission",
        decision="resume",
        payload={"selected_option_id": "slot_a"},
    )

    assert plan.state == PlanState.EXECUTING
    assert step.state == PlanStepState.DISPATCHED
    assert step.inputs["selected_option"]["id"] == "slot_a"
    assert step.inputs["proposed_write"]["event_body"]["summary"] == "Tea"
    assert env["dispatched"][1]["task_type"] == "calendar_mission"
    resumed_params = env["dispatched"][1]["params"]
    assert resumed_params["result_channel"] == "calendar_result"
    assert resumed_params["authority"] == "approved_write"
    assert resumed_params["calendar_write_approved"] is True
    assert resumed_params["hitl_approved"] is True
    assert resumed_params["approval_source"] == "PlanRegistry.resolve_step_user_decision"


async def test_plan_step_with_goal_and_no_tool_routes_as_nanobot_mission(env) -> None:
    plan = await env["registry"].draft(_proposal(steps=(
        PlanStepProposal(
            step_id="mission-step",
            title="open ended background work",
            expected_tool="",
            inputs={
                "goal": "Investigate the situation and report options",
                "mode": "flexible",
            },
        ),
    )))
    await env["registry"].submit_for_confirmation(plan.plan_id)
    await env["registry"].approve(plan.plan_id)
    await env["registry"].start_executing(plan.plan_id)

    assert plan.state == PlanState.EXECUTING
    assert env["dispatched"][0]["task_type"] == "nanobot_mission"
    assert env["dispatched"][0]["params"]["goal"] == "Investigate the situation and report options"
    assert env["dispatched"][0]["params"]["requested_expected_tool"] == ""


async def test_plan_step_mission_alias_routes_calendar_domain(env) -> None:
    plan = await env["registry"].draft(_proposal(steps=(
        PlanStepProposal(
            step_id="calendar-alias",
            title="calendar mission alias",
            expected_tool="mission",
            inputs={
                "goal": "Find a safe Calendar slot",
                "domain": "calendar",
            },
        ),
    )))
    await env["registry"].submit_for_confirmation(plan.plan_id)
    await env["registry"].approve(plan.plan_id)
    await env["registry"].start_executing(plan.plan_id)

    assert env["dispatched"][0]["task_type"] == "calendar_mission"
    assert env["dispatched"][0]["params"]["result_channel"] == "calendar_result"
    assert env["dispatched"][0]["params"]["requested_expected_tool"] == "mission"


def test_illegal_transition_raises() -> None:
    plan_state = PlanState.COMPLETE
    legal = PlanLifecycle.LEGAL_TRANSITIONS[plan_state]
    assert PlanState.DRAFT not in legal


async def test_illegal_transition_via_enforce(env) -> None:
    plan = await env["registry"].draft(_proposal())
    plan.state = PlanState.COMPLETE  # mock
    with pytest.raises(IllegalPlanTransition):
        PlanLifecycle.enforce_transition(plan, PlanState.DRAFT)


async def test_step_failure_transitions_plan_failed(env) -> None:
    plan = await env["registry"].draft(_proposal())
    await env["registry"].submit_for_confirmation(plan.plan_id)
    await env["registry"].approve(plan.plan_id)
    await env["registry"].start_executing(plan.plan_id)
    await env["registry"].report_step_result(
        plan.plan_id, "s1", success=False, error="boom",
    )
    assert plan.state == PlanState.FAILED


async def test_dispatch_failure_transitions_plan_failed() -> None:
    ws = IntentWorkspace()
    set_intent_workspace_for_test(ws)

    async def failing_dispatch(task_type: str, params: dict, priority: str) -> str:
        raise RuntimeError("dispatch offline")

    try:
        registry = PlanRegistry(dispatch_task=failing_dispatch)
        plan = await registry.draft(_proposal(steps=(
            PlanStepProposal(step_id="s1", title="step1", expected_tool="research"),
        )))
        await registry.submit_for_confirmation(plan.plan_id)
        await registry.approve(plan.plan_id)
        await registry.start_executing(plan.plan_id)

        assert plan.state == PlanState.FAILED
        assert plan.steps[0].state == PlanStepState.FAILED
        assert plan.steps[0].error == "dispatch_failed:RuntimeError"
    finally:
        set_intent_workspace_for_test(None)


async def test_unsupported_plan_tool_transitions_plan_failed(env) -> None:
    plan = await env["registry"].draft(_proposal(steps=(
        PlanStepProposal(step_id="s1", title="step1", expected_tool="unknown_tool"),
    )))
    await env["registry"].submit_for_confirmation(plan.plan_id)
    await env["registry"].approve(plan.plan_id)
    await env["registry"].start_executing(plan.plan_id)

    assert plan.state == PlanState.FAILED
    assert plan.steps[0].state == PlanStepState.FAILED
    assert plan.steps[0].error == "unsupported_expected_tool:unknown_tool"
    assert env["dispatched"] == []


async def test_empty_plan_completes_on_start(env) -> None:
    plan = await env["registry"].draft(_proposal(steps=()))
    await env["registry"].submit_for_confirmation(plan.plan_id)
    await env["registry"].approve(plan.plan_id)
    await env["registry"].start_executing(plan.plan_id)

    assert plan.state == PlanState.COMPLETE
    assert env["registry"].get(plan.plan_id) is plan
    assert plan not in env["registry"].list_active()


async def test_cancel_transitions_to_cancelled(env) -> None:
    plan = await env["registry"].draft(_proposal())
    await env["registry"].cancel(plan.plan_id, reason="user changed mind")
    assert plan.state == PlanState.CANCELLED


async def test_revise_creates_new_plan_supersedes_old(env) -> None:
    p1 = await env["registry"].draft(_proposal(title="v1"))
    await env["registry"].submit_for_confirmation(p1.plan_id)
    await env["registry"].approve(p1.plan_id)
    await env["registry"].start_executing(p1.plan_id)
    await env["registry"].report_step_result(p1.plan_id, "s1", success=False, error="x")
    assert p1.state == PlanState.FAILED

    p2 = await env["registry"].revise(p1.plan_id, _proposal(title="v2"))
    assert p2.title == "v2"
    assert p2.supersedes == p1.plan_id
    assert p1.superseded_by == p2.plan_id


# ─── Lookups ──────────────────────────────────────────────────


async def test_lookups(env) -> None:
    p1 = await env["registry"].draft(_proposal(title="a"))
    p2 = await env["registry"].draft(_proposal(title="b"))
    p1.intent_event_id = "ev_x"
    p1.episode_id = "ep_x"
    p2.intent_event_id = "ev_y"

    assert env["registry"].get(p1.plan_id) is p1
    actives = env["registry"].list_active()
    assert {p.plan_id for p in actives} == {p1.plan_id, p2.plan_id}
    by_event = env["registry"].list_by_intent_event("ev_x")
    assert by_event == [p1]
    by_ep = env["registry"].list_by_episode("ep_x")
    assert by_ep == [p1]


async def test_get_current_plan_picks_most_recent(env) -> None:
    import time
    p1 = await env["registry"].draft(_proposal(title="early"))
    time.sleep(0.001)
    p2 = await env["registry"].draft(_proposal(title="late"))
    cur = env["registry"].get_current_plan()
    assert cur is p2
