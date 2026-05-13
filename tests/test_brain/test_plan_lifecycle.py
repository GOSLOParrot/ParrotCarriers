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
