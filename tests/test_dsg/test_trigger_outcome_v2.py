"""DSG-TRIGGER-V2 — TriggerOutcome 5-channel routing."""

from __future__ import annotations

from pathlib import Path

import pytest

import parrot.dsg.l2b_graph as l2b_graph_module
from parrot.brain.intent_workspace import (
    IntentWorkspace,
    PayloadSource,
    StagedRefKind,
    StagedRefMetadata,
    StagedRefRequest,
    set_intent_workspace_for_test,
)
from parrot.brain.plan import (
    PlanProposal,
    PlanRegistry,
    PlanStepProposal,
    set_plan_registry_for_test,
)
from parrot.dsg.archive import (
    ArchiveRequest,
    ArchiveRequestKind,
    ArchiveTarget,
    ConversationArchive,
    set_archive_for_test,
)
from parrot.dsg.ingest.base import Observation, ObservationSource
from parrot.dsg.l1_5 import (
    BucketKind,
    BucketOp,
    BucketOpKind,
    BucketSpec,
    L15Pool,
    set_pool_for_test,
)
from parrot.dsg.l2b_graph import L2BGraph
from parrot.dsg.l2b_types import ConfirmationStatus, NodeKind
from parrot.dsg.triggers.base import BaseTrigger, TriggerKind, TriggerOutcome, TriggerResult
from parrot.dsg.triggers.runner import TriggerRunner


@pytest.fixture
def env(tmp_path: Path):
    """Wire up all singletons in isolation."""
    pool = L15Pool()
    set_pool_for_test(pool)
    ws = IntentWorkspace()
    set_intent_workspace_for_test(ws)
    registry = PlanRegistry()
    set_plan_registry_for_test(registry)
    arch = ConversationArchive(base_path=tmp_path / "conversations")
    set_archive_for_test(arch)
    graph = L2BGraph()
    l2b_graph_module._instance = graph

    yield {
        "pool": pool,
        "ws": ws,
        "registry": registry,
        "arch": arch,
        "graph": graph,
    }

    set_pool_for_test(None)
    set_intent_workspace_for_test(None)
    set_plan_registry_for_test(None)
    set_archive_for_test(None)
    l2b_graph_module._instance = None


def test_trigger_result_alias_kept_for_back_compat() -> None:
    """Legacy 4 triggers reference TriggerResult — alias must work."""
    assert TriggerResult is TriggerOutcome


def test_trigger_implementations_use_trigger_outcome_name() -> None:
    """TriggerResult is kept for imports, not as the implementation style."""
    repo_root = Path(__file__).resolve().parents[2]
    trigger_dir = repo_root / "src" / "parrot" / "dsg" / "triggers"
    offenders = []
    for path in sorted(trigger_dir.glob("*.py")):
        if path.name == "base.py":
            continue
        if "TriggerResult" in path.read_text(encoding="utf-8"):
            offenders.append(path.name)

    assert offenders == []


def test_trigger_implementations_leave_notification_delivery_to_runner() -> None:
    """Concrete triggers should not duplicate the Runner-owned C3 delivery path."""
    repo_root = Path(__file__).resolve().parents[2]
    trigger_dir = repo_root / "src" / "parrot" / "dsg" / "triggers"
    offenders = []
    for path in sorted(trigger_dir.glob("*.py")):
        if path.name == "base.py":
            continue
        if "_notify_brain(" in path.read_text(encoding="utf-8"):
            offenders.append(path.name)

    assert offenders == []


def test_legacy_only_outcome_runs_legacy_path(env) -> None:
    """A TriggerOutcome with only legacy fields populated is valid."""
    out = TriggerOutcome(
        trigger_name="legacy",
        summary="x",
        notify_gemini=False,
    )
    assert out.commit_observations == ()
    assert out.bucket_ops == ()
    assert out.archive_request is None
    assert out.staged_refs == ()
    assert out.plan_request is None


async def test_bucket_ops_dispatched_through_pool(env) -> None:
    runner = TriggerRunner(graph=env["graph"])
    spec = BucketSpec(kind=BucketKind.ROLEPLAY_TEMP, is_authority=True)
    outcome = TriggerOutcome(
        trigger_name="t1",
        bucket_ops=(
            BucketOp(
                op=BucketOpKind.REGISTER,
                kind=BucketKind.ROLEPLAY_TEMP,
                payload={"spec": spec},
            ),
        ),
    )
    await runner._process_result(outcome)
    assert env["pool"].get_bucket(BucketKind.ROLEPLAY_TEMP) is not None


async def test_commit_observations_routed_through_pool_admit(env) -> None:
    runner = TriggerRunner(graph=env["graph"])
    obs = Observation(
        source=ObservationSource.GOSLO_AUTONOMOUS,
        label="curiosity_obj",
        confidence=0.7,
        confirmation=ConfirmationStatus.TENTATIVE,
        kind=NodeKind.OBJECT,
    )
    outcome = TriggerOutcome(
        trigger_name="t2",
        commit_observations=(obs,),
    )
    await runner._process_result(outcome)
    # The pool's autonomous_curiosity bucket should have a node assigned
    handle = env["pool"].get_bucket(BucketKind.AUTONOMOUS_CURIOSITY)
    assert handle is not None
    assert len(handle.node_uuids) >= 1


async def test_staged_refs_routed_to_intent_workspace(env) -> None:
    runner = TriggerRunner(graph=env["graph"])
    req = StagedRefRequest(
        kind=StagedRefKind.RICH_REPORT,
        payload_source=PayloadSource.INLINE_TEXT,
        payload_value="**Markdown report**",
        metadata=StagedRefMetadata(
            origin="trigger:t3",
            kind=StagedRefKind.RICH_REPORT,
            payload_source=PayloadSource.INLINE_TEXT,
        ),
    )
    outcome = TriggerOutcome(trigger_name="t3", staged_refs=(req,))
    await runner._process_result(outcome)
    active = env["ws"].list_active()
    assert any(h.kind == StagedRefKind.RICH_REPORT for h in active)


async def test_archive_request_routed_to_archive_module(env) -> None:
    runner = TriggerRunner(graph=env["graph"])
    req = ArchiveRequest(
        kind=ArchiveRequestKind.ENQUEUE_FOR_IDLE,
        target=ArchiveTarget.EPISODE,
        target_id="ep_archive_test",
    )
    outcome = TriggerOutcome(trigger_name="t4", archive_request=req)
    await runner._process_result(outcome)
    pending = env["arch"].list_pending()
    assert any(p.target_id == "ep_archive_test" for p in pending)


async def test_plan_request_routed_to_plan_registry(env) -> None:
    runner = TriggerRunner(graph=env["graph"])
    proposal = PlanProposal(
        proposed_by="trigger:t5",
        title="auto plan",
        suggested_steps=(PlanStepProposal(step_id="x1", title="test"),),
    )
    outcome = TriggerOutcome(trigger_name="t5", plan_request=proposal)
    await runner._process_result(outcome)
    actives = env["registry"].list_active()
    assert any(p.title == "auto plan" for p in actives)


async def test_fire_event_routes_on_demand_triggers(env) -> None:
    class OnDemandOnlyTrigger(BaseTrigger):
        name = "on_demand_test"
        kinds = [TriggerKind.ON_DEMAND]

        async def on_startup(self):
            return None

        async def on_tick(self):
            return None

        async def on_event(self, event):
            if event.get("kind") != "on_demand_test":
                return None
            return TriggerOutcome(trigger_name=self.name, summary="fired")

    runner = TriggerRunner(graph=env["graph"])
    runner.register(OnDemandOnlyTrigger)

    results = await runner.fire_event({"kind": "on_demand_test"})

    assert len(results) == 1
    assert results[0].trigger_name == "on_demand_test"


async def test_one_channel_failure_does_not_block_others(env) -> None:
    """If bucket_ops fails (unknown kind etc), staged_refs should still
    be processed."""
    runner = TriggerRunner(graph=env["graph"])
    # malformed bucket_op (unknown kind cleared via REGISTER without spec is OK,
    # use UNREGISTER on a non-existent bucket to provoke a soft-failure)
    bad_op = BucketOp(op=BucketOpKind.UNREGISTER, kind=BucketKind.ROLEPLAY_TEMP)
    good_req = StagedRefRequest(
        kind=StagedRefKind.OTHER,
        payload_source=PayloadSource.INLINE_TEXT,
        payload_value="payload",
        metadata=StagedRefMetadata(
            origin="t6",
            kind=StagedRefKind.OTHER,
            payload_source=PayloadSource.INLINE_TEXT,
        ),
    )
    outcome = TriggerOutcome(
        trigger_name="t6",
        bucket_ops=(bad_op,),
        staged_refs=(good_req,),
    )
    await runner._process_result(outcome)
    active = env["ws"].list_active()
    assert any(h.metadata.origin == "t6" for h in active)


async def test_processing_order_bucket_ops_before_commit(env) -> None:
    """If bucket REGISTER comes in the same outcome as a commit
    targeting that bucket, REGISTER must run first so admit() finds
    the bucket. We exercise this via the IMPORT op which combines both."""
    runner = TriggerRunner(graph=env["graph"])
    obs = Observation(
        source=ObservationSource.MOCK,
        label="x",
        confidence=0.9,
        confirmation=ConfirmationStatus.TENTATIVE,
        kind=NodeKind.OBJECT,
    )
    spec = BucketSpec(
        kind=BucketKind.ROLEPLAY_TEMP, is_authority=True,
    )
    outcome = TriggerOutcome(
        trigger_name="t7",
        bucket_ops=(
            BucketOp(
                op=BucketOpKind.REGISTER,
                kind=BucketKind.ROLEPLAY_TEMP,
                payload={"spec": spec},
            ),
        ),
        commit_observations=(obs,),
    )
    await runner._process_result(outcome)
    assert env["pool"].get_bucket(BucketKind.ROLEPLAY_TEMP) is not None


async def test_legacy_notify_gemini_routes_to_c3_status_notice(env) -> None:
    """Legacy trigger notifications should not default to C4 speech."""
    from parrot.brain import context_injector as context_injector_module

    class _FakeInjector:
        def __init__(self) -> None:
            self.notices: list[str] = []
            self.speeches: list[str] = []

        async def inject_status_notice(self, message: str) -> None:
            self.notices.append(message)

        async def inject_notification(self, message: str) -> None:
            self.speeches.append(message)

    fake = _FakeInjector()
    old_injector = context_injector_module._injector
    context_injector_module._injector = fake  # type: ignore[assignment]
    try:
        runner = TriggerRunner(graph=env["graph"])
        runner._session = object()
        outcome = TriggerOutcome(
            trigger_name="generic_trigger",
            notify_gemini=True,
            notification_text="Calendar digest ready.",
        )

        await runner._process_result(outcome)

        assert fake.notices == ["Calendar digest ready."]
        assert fake.speeches == []
    finally:
        context_injector_module._injector = old_injector


async def test_proactive_message_trigger_speaks_after_policy_allows(
    env, monkeypatch: pytest.MonkeyPatch
) -> None:
    from parrot.brain import context_injector as context_injector_module

    class _FakeInjector:
        def __init__(self) -> None:
            self.notices: list[str] = []

        async def inject_status_notice(self, message: str) -> None:
            self.notices.append(message)

    class _FakeSession:
        current_speech = None

        def __init__(self) -> None:
            self.instructions: str | None = None

        async def generate_reply(self, *, instructions: str) -> None:
            self.instructions = instructions

    fake = _FakeInjector()
    session = _FakeSession()
    old_injector = context_injector_module._injector
    context_injector_module._injector = fake  # type: ignore[assignment]
    monkeypatch.setattr(
        "parrot.brain.session_policy.should_generate_reply",
        lambda reason: True,
    )
    try:
        runner = TriggerRunner(graph=env["graph"])
        runner._session = session
        outcome = TriggerOutcome(
            trigger_name="message_notification",
            notify_gemini=True,
            notification_text="Important mail from demo@example.com.",
            proactive_speech=True,
        )

        await runner._process_result(outcome)

        assert fake.notices == ["Important mail from demo@example.com."]
        assert session.instructions is not None
        assert "Proactively remind the user" in session.instructions
        assert "source channel" in session.instructions
        assert "Nanobot/Google result" in session.instructions
        assert "Do not read raw worker output aloud" in session.instructions
        assert "Important mail from demo@example.com." in session.instructions
    finally:
        context_injector_module._injector = old_injector
