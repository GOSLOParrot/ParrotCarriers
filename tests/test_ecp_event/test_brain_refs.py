"""Tests for `parrot.brain.refs` (Phase 4 W6-7 RefBinding registry).

Coverage focus:
    1. bind_bbox / bind_focus create UNRESOLVED Refs + index by Unity id
    2. Idempotent: repeat bind for same id returns same Ref
    3. unbind drops the entry; subsequent get_ref returns None
    4. resolve_ref bumps revision + updates target_kind/target_id
    5. resolve preserves ref_id (so callers holding ref_id still work)
    6. reset_refs_for_session keeps a whitelist + drops orphan indexes
    7. metrics_snapshot reflects counts
    8. Cross-kind isolation: bbox + focus with same numeric id stay separate
"""

from __future__ import annotations

import pytest

from parrot.brain import refs as refs_registry
from parrot.shared.ref_binding import RefKind, RefTargetKind


@pytest.fixture(autouse=True)
def _reset():
    refs_registry.reset_refs_for_tests()
    yield
    refs_registry.reset_refs_for_tests()


# ─── bind / get / unbind ────────────────────────────────────────────


def test_bind_bbox_creates_unresolved_ref():
    ref = refs_registry.bind_bbox(bbox_id="bb_001", source_event_id="evt_test_aaaa")
    assert ref.kind == RefKind.BBOX.value
    assert ref.target_kind == RefTargetKind.UNRESOLVED.value
    assert ref.source_event_id == "evt_test_aaaa"
    assert "bbox:bb_001" in ref.label


def test_bind_bbox_idempotent_returns_same_ref():
    a = refs_registry.bind_bbox(bbox_id="bb_dup", source_event_id="evt_a")
    b = refs_registry.bind_bbox(bbox_id="bb_dup", source_event_id="evt_b")
    assert a.ref_id == b.ref_id


def test_get_ref_by_bbox_after_bind():
    ref = refs_registry.bind_bbox(bbox_id="bb_lookup", source_event_id="evt_x")
    found = refs_registry.get_ref_by_bbox("bb_lookup")
    assert found is not None
    assert found.ref_id == ref.ref_id


def test_get_ref_by_bbox_returns_none_for_unknown():
    assert refs_registry.get_ref_by_bbox("never_bound") is None


def test_unbind_bbox_drops_entry():
    ref = refs_registry.bind_bbox(bbox_id="bb_to_remove", source_event_id="evt_y")
    removed = refs_registry.unbind_bbox("bb_to_remove")
    assert removed is not None
    assert removed.ref_id == ref.ref_id
    assert refs_registry.get_ref_by_bbox("bb_to_remove") is None
    assert refs_registry.get_ref(ref.ref_id) is None


def test_unbind_bbox_unknown_returns_none():
    assert refs_registry.unbind_bbox("never_bound") is None


# ─── focus mirror ───────────────────────────────────────────────────


def test_focus_bind_and_unbind():
    ref = refs_registry.bind_focus(focus_id="f_001", source_event_id="evt_f")
    assert ref.kind == RefKind.FOCUS.value
    assert refs_registry.get_ref_by_focus("f_001") is not None
    refs_registry.unbind_focus("f_001")
    assert refs_registry.get_ref_by_focus("f_001") is None


def test_bbox_and_focus_with_same_id_stay_isolated():
    """bbox_id "001" + focus_id "001" must produce distinct Refs."""
    bbox_ref = refs_registry.bind_bbox(bbox_id="001", source_event_id="evt_b")
    focus_ref = refs_registry.bind_focus(focus_id="001", source_event_id="evt_f")
    assert bbox_ref.ref_id != focus_ref.ref_id
    assert bbox_ref.kind == RefKind.BBOX.value
    assert focus_ref.kind == RefKind.FOCUS.value


# ─── resolve ───────────────────────────────────────────────────────


def test_resolve_ref_bumps_revision_and_keeps_ref_id():
    ref = refs_registry.bind_bbox(bbox_id="bb_resolve", source_event_id="evt_a")
    original_id = ref.ref_id

    updated = refs_registry.resolve_ref(
        ref.ref_id,
        target_kind=RefTargetKind.L2B_NODE,
        target_id="node_42",
        new_event_id="evt_match",
    )
    assert updated is not None
    assert updated.ref_id == original_id
    assert updated.revision == 2
    assert updated.target_kind == RefTargetKind.L2B_NODE.value
    assert updated.target_id == "node_42"
    assert updated.source_event_id == "evt_match"

    # Subsequent get_ref returns the resolved version.
    fetched = refs_registry.get_ref(original_id)
    assert fetched is updated


def test_resolve_ref_unknown_returns_none():
    assert refs_registry.resolve_ref(
        "not_a_real_ref_id",
        target_kind=RefTargetKind.L2B_NODE,
        target_id="node_x",
    ) is None


# ─── session reset ─────────────────────────────────────────────────


def test_reset_for_session_keeps_whitelist_drops_others():
    a = refs_registry.bind_bbox(bbox_id="keep", source_event_id="evt_a")
    b = refs_registry.bind_bbox(bbox_id="drop_1", source_event_id="evt_b")
    c = refs_registry.bind_focus(focus_id="drop_2", source_event_id="evt_c")

    dropped = refs_registry.reset_refs_for_session(active_ids={a.ref_id})

    assert dropped == 2
    assert refs_registry.get_ref(a.ref_id) is not None
    assert refs_registry.get_ref(b.ref_id) is None
    assert refs_registry.get_ref(c.ref_id) is None
    # Secondary indexes also cleaned
    assert refs_registry.get_ref_by_bbox("drop_1") is None
    assert refs_registry.get_ref_by_focus("drop_2") is None


# ─── metrics ───────────────────────────────────────────────────────


def test_metrics_snapshot_keys():
    snap = refs_registry.metrics_snapshot()
    assert set(snap.keys()) == {"total_refs", "bbox_refs", "focus_refs"}


def test_metrics_track_counts():
    refs_registry.bind_bbox(bbox_id="bb_m1", source_event_id="evt_1")
    refs_registry.bind_bbox(bbox_id="bb_m2", source_event_id="evt_2")
    refs_registry.bind_focus(focus_id="f_m1", source_event_id="evt_3")

    snap = refs_registry.metrics_snapshot()
    assert snap == {"total_refs": 3, "bbox_refs": 2, "focus_refs": 1}


# ─── F-06: agent.py disconnect handler wires reset_refs_for_session ─


def test_agent_disconnect_handler_invokes_reset_refs_for_session():
    """Brain self-audit F-06 (2026-04-30): refs.py docstring claims
    'Each LiveKit session ideally calls reset_refs_for_session on
    disconnect'. The wire-up lives in brain/agent.py's
    _on_room_disconnected. We assert the source contains the call so a
    refactor that drops the cleanup will fail this freeze test.

    Source-grep instead of behavioural test because driving an actual
    LiveKit Room.Disconnected event requires the full agent boot and
    a Gemini RealtimeModel — out of scope for a unit test.
    """
    from pathlib import Path

    src = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "parrot"
        / "brain"
        / "agent.py"
    ).read_text(encoding="utf-8")

    # Both must appear inside the disconnect handler block.
    assert "from parrot.brain.refs import reset_refs_for_session" in src
    assert "reset_refs_for_session()" in src
    # And must reference the audit finding so the why-comment survives
    # ruthless cleanup passes.
    assert "F-06" in src
