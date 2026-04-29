"""Tests for `parrot.dsg.attention.hint_writer` (Phase 4 W6-7).

Coverage focus:
    1. UNRESOLVED Ref → no L2-B touch, counter increments
    2. L2B_NODE Ref but missing target node → no crash, counter increments
    3. L2B_NODE Ref with present node → attention bumped + clamped to 1.0
    4. Non-L2B target_kind (e.g. EPISODE) → skip path
    5. Multiple bumps accumulate correctly
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from parrot.dsg.attention import hint_writer
from parrot.shared.ref_binding import RefBinding, RefKind, RefTargetKind


@pytest.fixture(autouse=True)
def _reset():
    hint_writer.reset_metrics_for_tests()
    yield
    hint_writer.reset_metrics_for_tests()


def _ref(*, target_kind=RefTargetKind.UNRESOLVED, target_id="") -> RefBinding:
    return RefBinding(
        kind=RefKind.BBOX,
        source_event_id="evt_test",
        target_kind=target_kind,
        target_id=target_id,
    )


# ─── unresolved skip ────────────────────────────────────────────────


def test_unresolved_ref_does_not_call_l2b():
    out = hint_writer.bump_l2b_for_resolved_ref(_ref(), delta=0.5)
    assert out is False
    assert hint_writer.metrics_snapshot()["bumps_skipped_unresolved"] == 1
    assert hint_writer.metrics_snapshot()["bumps_applied"] == 0


# ─── L2B node missing ───────────────────────────────────────────────


def test_l2b_node_missing_returns_false():
    class FakeGraph:
        def get_node(self, _u):
            return None

    with patch("parrot.dsg.l2b_graph.get_l2b_graph", lambda: FakeGraph()):
        out = hint_writer.bump_l2b_for_resolved_ref(
            _ref(target_kind=RefTargetKind.L2B_NODE, target_id="not_in_graph"),
            delta=0.3,
        )
    assert out is False
    assert hint_writer.metrics_snapshot()["bumps_skipped_node_missing"] == 1


# ─── L2B node present → bump + clamp ───────────────────────────────


def test_l2b_node_attention_bumped():
    class FakeNode:
        attention = 0.5
        last_attended = 0.0

    fake_node = FakeNode()

    class FakeGraph:
        def get_node(self, _u):
            return fake_node

    with patch("parrot.dsg.l2b_graph.get_l2b_graph", lambda: FakeGraph()):
        out = hint_writer.bump_l2b_for_resolved_ref(
            _ref(target_kind=RefTargetKind.L2B_NODE, target_id="node_42"),
            delta=0.3,
        )

    assert out is True
    assert fake_node.attention == pytest.approx(0.8)
    assert fake_node.last_attended > 0
    assert hint_writer.metrics_snapshot()["bumps_applied"] == 1


def test_attention_clamped_at_one():
    class FakeNode:
        attention = 0.95
        last_attended = 0.0

    fake_node = FakeNode()

    class FakeGraph:
        def get_node(self, _u):
            return fake_node

    with patch("parrot.dsg.l2b_graph.get_l2b_graph", lambda: FakeGraph()):
        hint_writer.bump_l2b_for_resolved_ref(
            _ref(target_kind=RefTargetKind.L2B_NODE, target_id="n"),
            delta=0.5,
        )
    assert fake_node.attention == 1.0


# ─── unsupported target ────────────────────────────────────────────


def test_episode_target_kind_skipped():
    out = hint_writer.bump_l2b_for_resolved_ref(
        _ref(target_kind=RefTargetKind.EPISODE, target_id="ep_001"),
        delta=0.4,
    )
    assert out is False
    assert hint_writer.metrics_snapshot()["bumps_skipped_unsupported_target"] == 1


def test_l2b_node_target_id_empty_skipped():
    out = hint_writer.bump_l2b_for_resolved_ref(
        _ref(target_kind=RefTargetKind.L2B_NODE, target_id=""),
        delta=0.4,
    )
    assert out is False


# ─── accumulation across calls ─────────────────────────────────────


def test_multiple_bumps_accumulate():
    class FakeNode:
        attention = 0.0
        last_attended = 0.0

    fake_node = FakeNode()

    class FakeGraph:
        def get_node(self, _u):
            return fake_node

    with patch("parrot.dsg.l2b_graph.get_l2b_graph", lambda: FakeGraph()):
        for _ in range(3):
            hint_writer.bump_l2b_for_resolved_ref(
                _ref(target_kind=RefTargetKind.L2B_NODE, target_id="n"),
                delta=0.2,
            )
    assert fake_node.attention == pytest.approx(0.6)
    assert hint_writer.metrics_snapshot()["bumps_applied"] == 3
