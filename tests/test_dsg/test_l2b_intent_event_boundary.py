"""DSG-INTENT-EVENT-V1 — IntentEventBoundary minimum behaviour."""

from __future__ import annotations

import pytest

import parrot.dsg.l2b_graph as l2b_graph_module
from parrot.dsg.l2b.intent_event_boundary import (
    IntentEventBoundaryHandler,
    IntentEventReason,
    NoOpDecayStrategy,
    NoOpFoldStrategy,
    SimpleDecayStrategy,
    set_intent_event_handler_for_test,
)
from parrot.dsg.l2b_graph import L2BGraph
from parrot.dsg.l2b_types import NodeKind, SemanticNode


@pytest.fixture
def graph():
    g = L2BGraph()
    # inject our test graph as the singleton
    l2b_graph_module._instance = g
    yield g
    l2b_graph_module._instance = None


@pytest.fixture
def handler():
    h = IntentEventBoundaryHandler(
        decay_strategy=NoOpDecayStrategy(),
        fold_strategy=NoOpFoldStrategy(),
    )
    set_intent_event_handler_for_test(h)
    yield h
    set_intent_event_handler_for_test(None)


def test_open_assigns_event_id_to_active_nodes(graph: L2BGraph, handler: IntentEventBoundaryHandler) -> None:
    n = SemanticNode(label="active_high_attention", attention=0.9, event_id="")
    graph.upsert_node(n)
    state = handler.open(IntentEventReason.TOOL_CALL_BOUNDARY)
    assert n.event_id == state.event_id


def test_open_does_not_overwrite_existing_event_id(graph: L2BGraph, handler: IntentEventBoundaryHandler) -> None:
    n = SemanticNode(label="already_tagged", attention=0.9, event_id="ev_old")
    graph.upsert_node(n)
    handler.open(IntentEventReason.TOOL_CALL_BOUNDARY)
    assert n.event_id == "ev_old"


def test_close_invokes_decay_strategy(graph: L2BGraph) -> None:
    decay = SimpleDecayStrategy(decay_factor=0.5)
    h = IntentEventBoundaryHandler(decay_strategy=decay)
    set_intent_event_handler_for_test(h)
    try:
        n = SemanticNode(label="x", attention=0.8, event_id="", evidence_score=0.5)
        graph.upsert_node(n)
        state = h.open(IntentEventReason.TOOL_CALL_BOUNDARY)
        assert n.event_id == state.event_id
        h.close(state.event_id)
        # SimpleDecayStrategy halves attention
        assert n.attention == pytest.approx(0.4)
    finally:
        set_intent_event_handler_for_test(None)


def test_open_replaces_previous_active_event(graph: L2BGraph, handler: IntentEventBoundaryHandler) -> None:
    s1 = handler.open(IntentEventReason.TOOL_CALL_BOUNDARY)
    s2 = handler.open(IntentEventReason.PLAN_PHASE_CHANGE)
    assert s1.event_id != s2.event_id
    assert handler.current_event_id() == s2.event_id

    closed_state = handler.get_event_state(s1.event_id)
    assert closed_state is not None and closed_state.closed_at > 0


def test_baseline_noop_fold_returns_member_list(graph: L2BGraph, handler: IntentEventBoundaryHandler) -> None:
    n1 = SemanticNode(label="a", attention=0.9, event_id="")
    n2 = SemanticNode(label="b", attention=0.9, event_id="")
    graph.upsert_node(n1)
    graph.upsert_node(n2)
    s = handler.open(IntentEventReason.EXPLICIT)

    fold = NoOpFoldStrategy()
    result = fold.fold(s.event_id, graph)
    assert set(result.folded_node_uuids) == {n1.uuid, n2.uuid}
    assert result.folded_edges_count == 0


def test_simple_decay_strategy_factor_validation() -> None:
    with pytest.raises(ValueError):
        SimpleDecayStrategy(decay_factor=1.5)


def test_cross_event_channel_returns_edges(graph: L2BGraph, handler: IntentEventBoundaryHandler) -> None:
    a = SemanticNode(label="a", event_id="ev_a")
    b = SemanticNode(label="b", event_id="ev_b")
    graph.upsert_node(a)
    graph.upsert_node(b)
    graph.connect(a.uuid, b.uuid)

    edges = handler.cross_event_channel("ev_a", "ev_b")
    assert len(edges) == 1
