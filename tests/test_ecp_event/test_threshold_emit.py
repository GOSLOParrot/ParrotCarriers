"""Tests for `parrot.dsg.attention.threshold._emit_threshold_crossed`
(Phase 4 W6-7 实质化 emit).

Coverage focus:
    1. Crossing publishes attention.threshold.crossed EcpEvent via
       EcpEventPublisher.publish_nowait
    2. Crossing writes transient/current_attention_hint BB key with
       the locked payload shape (schema_version + ref_id + weight +
       subject_kind + subject_id + label + delta_applied + source_event_id
       + ts_ms)
    3. Crossing delegates to hint_writer.bump_l2b_for_resolved_ref
       (which is no-op for UNRESOLVED Refs by design)
    4. Two distinct bbox_ids track separately
    5. correlation_id chain: outgoing attention.threshold.crossed
       carries source_event_id of the trigger as correlation_id
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import py_trees
import pytest

from parrot.brain import refs as refs_registry
from parrot.brain.event_ingest import (
    EcpEventIngest,
    reset_ecp_event_ingest_for_tests,
)
from parrot.brain.event_publisher import (
    attach_ecp_event_publisher,
    reset_ecp_event_publisher_for_tests,
)
from parrot.brain.intent_workspace import (
    IntentWorkspace,
    get_intent_workspace,
    set_intent_workspace_for_test,
)
from parrot.brain.observer import bbox as bbox_observer
from parrot.brain.observer import focus as focus_observer
from parrot.brain.vision.evidence import (
    ClockDomain,
    EvidenceKind,
    EvidenceStatus,
    TimebaseStamp,
    get_evidence_ledger,
)
from parrot.brain.vision.evidence_awareness import latest_evidence_awareness_notice
from parrot.dsg.attention import hint_writer
from parrot.dsg.attention.threshold import (
    FocusBboxThreshold,
    reset_attention_thresholds_for_tests,
)
from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.ecp_event import (
    EcpEvent,
    EcpEventSource,
    EcpEventType,
)


def _fake_room(name: str = "test-room") -> MagicMock:
    room = MagicMock()
    room.name = name
    room.local_participant = MagicMock()
    room.local_participant.publish_data = AsyncMock(return_value=None)
    return room


@pytest.fixture(autouse=True)
def _reset():
    reset_ecp_event_ingest_for_tests()
    reset_ecp_event_publisher_for_tests()
    refs_registry.reset_refs_for_tests()
    bbox_observer.reset_metrics_for_tests()
    focus_observer.reset_metrics_for_tests()
    hint_writer.reset_metrics_for_tests()
    get_evidence_ledger().reset_for_tests()
    # F-05 step ③ side effect: FocusBboxThreshold() now reads BB on construct.
    # Clear the attention-config BB key so DEFAULT_* assertions aren't
    # contaminated by BB writes from test_attention_config_echo or any other
    # test that populates global/attention_thresholds.
    reset_attention_thresholds_for_tests()
    yield
    reset_ecp_event_ingest_for_tests()
    reset_ecp_event_publisher_for_tests()
    refs_registry.reset_refs_for_tests()
    bbox_observer.reset_metrics_for_tests()
    focus_observer.reset_metrics_for_tests()
    hint_writer.reset_metrics_for_tests()
    get_evidence_ledger().reset_for_tests()
    set_intent_workspace_for_test(None)
    reset_attention_thresholds_for_tests()


def _bbox_placed(bbox_id: str = "bb_emit") -> EcpEvent:
    return EcpEvent.build(
        event_type=EcpEventType.BBOX_PLACED,
        source=EcpEventSource.UNITY,
        payload={"bbox_id": bbox_id, "corners": [[0, 0], [1, 1]]},
    )


def _bbox_placed_at(bbox_id: str, wall_time_ms: int) -> EcpEvent:
    return EcpEvent.build(
        event_type=EcpEventType.BBOX_PLACED,
        source=EcpEventSource.UNITY,
        payload={
            "bbox_id": bbox_id,
            "corners": [[0, 0], [1, 1]],
            "timebase": {
                "clock_domain": "unity",
                "wall_time_ms": wall_time_ms,
                "source_id": "pytest-unity",
            },
        },
    )


def _focus_anchored(focus_id: str) -> EcpEvent:
    return EcpEvent.build(
        event_type=EcpEventType.FOCUS_ANCHORED,
        source=EcpEventSource.UNITY,
        payload={"focus_id": focus_id, "center": [0.5, 0.5]},
    )


# ─── EcpEvent publish path ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_bbox_crossing_publishes_attention_threshold_crossed():
    room = _fake_room()
    pub = attach_ecp_event_publisher(room)

    ingest = EcpEventIngest()
    bbox_observer.register(ingest)
    th = FocusBboxThreshold()
    th.register(ingest)

    # 1 BBox crosses threshold (Δ_bbox=1.0 = threshold=1.0)
    bbox_event = _bbox_placed("bb_emit_1")
    ingest.handle_raw(
        "parrot.ecp.event",
        bbox_event.to_wire_json().encode("utf-8"),
    )

    await asyncio.sleep(0.02)  # let publish_nowait run

    # publish_data was called once
    room.local_participant.publish_data.assert_awaited_once()
    call = room.local_participant.publish_data.await_args
    payload_str = call.kwargs["payload"]
    assert '"event_type":"attention.threshold.crossed"' in payload_str
    assert '"source":"brain"' in payload_str
    # correlation_id chains back to the BBox event
    assert f'"correlation_id":"{bbox_event.event_id}"' in payload_str
    # AttentionHint payload fields all present
    for needle in (
        '"schema_version":1',
        '"weight":1.0',
        '"subject_kind":"bbox"',
        '"subject_id":"bb_emit_1"',
        '"delta_applied":1.0',
        f'"source_event_id":"{bbox_event.event_id}"',
    ):
        assert needle in payload_str, f"missing in payload: {needle}"

    assert pub.published_count == 1


# ─── BB write ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_bbox_crossing_writes_bb_attention_hint():
    room = _fake_room()
    attach_ecp_event_publisher(room)

    ingest = EcpEventIngest()
    bbox_observer.register(ingest)
    FocusBboxThreshold().register(ingest)

    ingest.handle_raw(
        "parrot.ecp.event",
        _bbox_placed("bb_bb_write").to_wire_json().encode("utf-8"),
    )
    await asyncio.sleep(0.02)

    bb = open_bb_client(name="test_reader_attn", writer="test")
    hint = bb.get("transient/current_attention_hint")
    assert hint is not None
    assert hint["schema_version"] == 1
    assert hint["subject_kind"] == "bbox"
    assert hint["subject_id"] == "bb_bb_write"
    assert hint["weight"] == pytest.approx(1.0)
    assert hint["delta_applied"] == pytest.approx(1.0)
    assert hint["ts_ms"] > 0


# ─── ref_id propagation ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_attention_hint_includes_ref_id_when_observer_ran_first():
    """bbox observer registers BEFORE threshold (per
    register_phase4_observers ordering), so when threshold fires the
    RefBinding already exists in the registry and ref_id is non-empty."""
    room = _fake_room()
    attach_ecp_event_publisher(room)

    ingest = EcpEventIngest()
    bbox_observer.register(ingest)  # first
    FocusBboxThreshold().register(ingest)  # second

    ingest.handle_raw(
        "parrot.ecp.event",
        _bbox_placed("bb_with_ref").to_wire_json().encode("utf-8"),
    )
    await asyncio.sleep(0.02)

    bb = open_bb_client(name="test_reader_ref", writer="test")
    hint = bb.get("transient/current_attention_hint")
    assert hint["ref_id"]  # non-empty
    # Ref exists in registry under that ref_id
    assert refs_registry.get_ref(hint["ref_id"]) is not None


@pytest.mark.asyncio
async def test_attention_hint_empty_ref_id_when_observer_missing():
    """If bbox observer was NOT registered, threshold still fires but
    ref_id is empty string — defensive path."""
    room = _fake_room()
    attach_ecp_event_publisher(room)

    ingest = EcpEventIngest()
    # NOTE: bbox observer NOT registered
    FocusBboxThreshold().register(ingest)

    ingest.handle_raw(
        "parrot.ecp.event",
        _bbox_placed("bb_no_ref").to_wire_json().encode("utf-8"),
    )
    await asyncio.sleep(0.02)

    bb = open_bb_client(name="test_reader_noref", writer="test")
    hint = bb.get("transient/current_attention_hint")
    assert hint["ref_id"] == ""
    assert hint["subject_id"] == "bb_no_ref"  # subject_id still populated


# ─── multiple targets independent ─────────────────────────────────


@pytest.mark.asyncio
async def test_two_bboxes_track_independently():
    room = _fake_room()
    attach_ecp_event_publisher(room)

    ingest = EcpEventIngest()
    bbox_observer.register(ingest)
    th = FocusBboxThreshold()
    th.register(ingest)

    ingest.handle_raw(
        "parrot.ecp.event",
        _bbox_placed("bb_a").to_wire_json().encode("utf-8"),
    )
    ingest.handle_raw(
        "parrot.ecp.event",
        _bbox_placed("bb_b").to_wire_json().encode("utf-8"),
    )
    await asyncio.sleep(0.05)

    # Two independent crossings = two publish_data calls
    assert room.local_participant.publish_data.await_count == 2
    assert th.thresholds_crossed == 2


# ─── focus needs 5 events to cross ────────────────────────────────


@pytest.mark.asyncio
async def test_focus_crosses_after_five_events_emits_once():
    room = _fake_room()
    attach_ecp_event_publisher(room)

    ingest = EcpEventIngest()
    focus_observer.register(ingest)
    th = FocusBboxThreshold()
    th.register(ingest)

    for _ in range(5):
        ingest.handle_raw(
            "parrot.ecp.event",
            _focus_anchored("f_cross").to_wire_json().encode("utf-8"),
        )
    await asyncio.sleep(0.05)

    # 5 focus events on same focus_id → one threshold crossing
    assert th.thresholds_crossed == 1
    assert room.local_participant.publish_data.await_count == 1

    bb = open_bb_client(name="test_reader_focus", writer="test")
    hint = bb.get("transient/current_attention_hint")
    assert hint["subject_kind"] == "focus"
    assert hint["subject_id"] == "f_cross"
    assert hint["delta_applied"] == pytest.approx(0.2)


# ─── hint_writer delegation (UNRESOLVED is the common case) ───────


@pytest.mark.asyncio
async def test_hint_writer_called_but_no_op_when_ref_unresolved():
    """At threshold-cross time, the Ref is UNRESOLVED (just placed by user;
    no L2B node target yet). hint_writer correctly logs the no-op."""
    room = _fake_room()
    attach_ecp_event_publisher(room)

    ingest = EcpEventIngest()
    bbox_observer.register(ingest)
    FocusBboxThreshold().register(ingest)

    ingest.handle_raw(
        "parrot.ecp.event",
        _bbox_placed("bb_unresolved").to_wire_json().encode("utf-8"),
    )
    await asyncio.sleep(0.02)

    metrics = hint_writer.metrics_snapshot()
    assert metrics["bumps_skipped_unresolved"] == 1
    assert metrics["bumps_applied"] == 0


# ─── F-08: race — bbox.removed AFTER threshold crossed ──────────────


@pytest.mark.asyncio
async def test_threshold_crossing_stages_nearby_frame_without_speech(tmp_path):
    """WEB-015.12: threshold crossing can stage existing evidence for GOSLO.

    The automatic bridge must stay conservative: it uses the stored frame
    cache/ledger path, writes an IntentWorkspace hint, and never asks the
    threshold module to capture images, mutate L2-B, or trigger C4 speech.
    """
    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    set_intent_workspace_for_test(IntentWorkspace())
    ledger = get_evidence_ledger()
    ledger.reset_for_tests()
    wall_time_ms = 1_700_000_040_000
    frame_path = tmp_path / "threshold-auto-frame.jpg"
    frame_path.write_bytes(b"fake-jpeg")
    frame = ledger.record_sample(
        kind=EvidenceKind.VIDEO_FRAME,
        status=EvidenceStatus.READY,
        timebase=TimebaseStamp(
            clock_domain=ClockDomain.LIVEKIT_TRACK,
            wall_time_ms=wall_time_ms + 4,
            source_id="pytest-screen-share",
        ),
        asset_path=str(frame_path),
        mime_type="image/jpeg",
        description="nearby frame for threshold bridge",
    )

    room = _fake_room()
    attach_ecp_event_publisher(room)
    ingest = EcpEventIngest()
    bbox_observer.register(ingest)
    FocusBboxThreshold().register(ingest)

    ingest.handle_raw(
        "parrot.ecp.event",
        _bbox_placed_at("bb_auto_bridge", wall_time_ms).to_wire_json().encode("utf-8"),
    )
    await asyncio.sleep(0.05)

    staged = get_intent_workspace().list_active(role="visual_evidence_hint")
    notice = latest_evidence_awareness_notice()
    assert staged
    assert notice["evidence_id"] == frame.evidence_id
    assert notice["staged_ref_id"] == staged[0].ref_id
    assert notice["allow_interrupt"] is False
    assert "attention threshold crossed" in notice["message"]


@pytest.mark.asyncio
async def test_bbox_removed_after_cross_drops_ref_no_crash():
    """Brain self-audit F-08 (2026-04-30): user places a BBox (cross fires),
    then removes it. The post-cross unbind must not crash; subsequent
    threshold-cross-side dispatches see ref=None and silently no-op."""
    room = _fake_room()
    attach_ecp_event_publisher(room)

    ingest = EcpEventIngest()
    bbox_observer.register(ingest)
    th = FocusBboxThreshold()
    th.register(ingest)

    # Place — crosses threshold
    ingest.handle_raw(
        "parrot.ecp.event",
        _bbox_placed("bb_race").to_wire_json().encode("utf-8"),
    )
    await asyncio.sleep(0.02)
    assert th.thresholds_crossed == 1
    # Ref exists post-cross
    assert refs_registry.get_ref_by_bbox("bb_race") is not None

    # Remove — registry pops the Ref; weight is also pulled below threshold
    e_remove = EcpEvent.build(
        event_type=EcpEventType.BBOX_REMOVED,
        source=EcpEventSource.UNITY,
        payload={"bbox_id": "bb_race"},
    )
    ingest.handle_raw(
        "parrot.ecp.event",
        e_remove.to_wire_json().encode("utf-8"),
    )
    await asyncio.sleep(0.02)
    assert refs_registry.get_ref_by_bbox("bb_race") is None

    # Re-place — must rebind a NEW Ref under the same bbox_id and re-cross
    # without raising (state.crossed reset to False on the negative-delta
    # passage; new Ref created on next bind_bbox).
    ingest.handle_raw(
        "parrot.ecp.event",
        _bbox_placed("bb_race").to_wire_json().encode("utf-8"),
    )
    await asyncio.sleep(0.02)
    assert th.thresholds_crossed == 2
    assert refs_registry.get_ref_by_bbox("bb_race") is not None


# ─── F-09-B: cross-kind isolation — bbox_id "001" vs focus_id "001" ─


@pytest.mark.asyncio
async def test_bbox_and_focus_with_same_id_track_separately_in_threshold():
    """Brain self-audit F-09-B (2026-04-30): _targets is keyed by
    f"{subject_kind}:{subject_id}" so a BBox with id "001" and a Focus
    with id "001" do not share an accumulator. Mirrors the cross-kind
    isolation that test_brain_refs.py already verifies for the
    RefBinding registry.

    Emit 1 bbox.placed (Δ_bbox=1.0 → cross) and 4 focus.anchored events
    (4 × Δ_focus=0.2 = 0.8 < 1.0 → no cross). If keys collided into
    "001", the focus events would inherit the bbox's already-crossed
    state and the focus side would never get to fire its own cross.
    """
    room = _fake_room()
    attach_ecp_event_publisher(room)

    ingest = EcpEventIngest()
    bbox_observer.register(ingest)
    focus_observer.register(ingest)
    th = FocusBboxThreshold()
    th.register(ingest)

    # 1 BBox with id "001" → crosses
    ingest.handle_raw(
        "parrot.ecp.event",
        _bbox_placed("001").to_wire_json().encode("utf-8"),
    )
    # 4 Focus events with id "001" → 0.8, no cross
    for _ in range(4):
        ingest.handle_raw(
            "parrot.ecp.event",
            _focus_anchored("001").to_wire_json().encode("utf-8"),
        )
    await asyncio.sleep(0.05)

    # Exactly 1 cross — only the bbox. The focus accumulator stays at 0.8
    # because it has its own _targets entry under "focus:001".
    assert th.thresholds_crossed == 1
    # 5th focus pushes focus side above threshold → second cross
    ingest.handle_raw(
        "parrot.ecp.event",
        _focus_anchored("001").to_wire_json().encode("utf-8"),
    )
    await asyncio.sleep(0.02)
    assert th.thresholds_crossed == 2
