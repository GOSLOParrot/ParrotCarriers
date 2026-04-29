"""Tests for `parrot.dsg.attention.threshold.FocusBboxThreshold` (Phase 4 W6-7 临时阈值器).

Coverage focus:
    1. Default Δ + threshold values match entry doc §8.1 L9 lock
    2. Single BBox crosses threshold immediately
    3. Five Focus events needed to cross (5 × 0.2 ≥ 1.0)
    4. Released / removed events decrement (and cap at 0)
    5. Threshold-cross is fired exactly once per "rising edge"
    6. Wiring through EcpEventIngest works end-to-end (subscriber count)
    7. Package __init__ enforces "no Attention class" (entry doc §8.1 L13)
"""

from __future__ import annotations

import pytest

from parrot.brain.event_ingest import EcpEventIngest
from parrot.dsg.attention.threshold import (
    DEFAULT_DELTA_BBOX,
    DEFAULT_DELTA_FOCUS,
    DEFAULT_THRESHOLD,
    FocusBboxThreshold,
)
from parrot.shared.ecp_event import EcpEvent, EcpEventSource, EcpEventType


def _make(et: EcpEventType, *, correlation_id: str = "tgt1") -> EcpEvent:
    return EcpEvent.build(
        event_type=et,
        source=EcpEventSource.UNITY,
        payload={},
        correlation_id=correlation_id,
    )


# ─── locked starter values ──────────────────────────────────────


def test_default_values_match_entry_doc_8_1_l9():
    """Entry doc §8.1 L9: Δ_focus=0.2, Δ_bbox=1.0, threshold=1.0.

    1 BBox直接到阈值 (1.0 ≥ 1.0); 5 Focuses to cross (5 × 0.2 = 1.0 ≥ 1.0).
    """
    assert DEFAULT_DELTA_FOCUS == 0.2
    assert DEFAULT_DELTA_BBOX == 1.0
    assert DEFAULT_THRESHOLD == 1.0


# ─── threshold crossing math ────────────────────────────────────


def test_single_bbox_crosses_threshold():
    th = FocusBboxThreshold()
    th._on_bbox_placed(_make(EcpEventType.BBOX_PLACED))
    assert th.thresholds_crossed == 1


def test_five_focus_events_needed_to_cross():
    th = FocusBboxThreshold()
    for _ in range(4):
        th._on_focus_anchored(_make(EcpEventType.FOCUS_ANCHORED))
    assert th.thresholds_crossed == 0
    th._on_focus_anchored(_make(EcpEventType.FOCUS_ANCHORED))
    assert th.thresholds_crossed == 1


def test_threshold_fires_only_once_per_rising_edge():
    """Hammering bbox.placed for the same target must not spam crossings —
    only one crossing per rising-edge event."""
    th = FocusBboxThreshold()
    for _ in range(5):
        th._on_bbox_placed(_make(EcpEventType.BBOX_PLACED, correlation_id="bbox_A"))
    assert th.thresholds_crossed == 1


def test_remove_drops_below_then_re_cross():
    """Place → cross. Remove → uncross. Place again → cross again."""
    th = FocusBboxThreshold()
    cid = "bbox_round_trip"
    th._on_bbox_placed(_make(EcpEventType.BBOX_PLACED, correlation_id=cid))
    assert th.thresholds_crossed == 1

    th._on_bbox_removed(_make(EcpEventType.BBOX_REMOVED, correlation_id=cid))
    th._on_bbox_placed(_make(EcpEventType.BBOX_PLACED, correlation_id=cid))
    assert th.thresholds_crossed == 2


def test_weight_caps_at_zero_on_negative_delta():
    """Weight floor — never goes negative even with surplus removes."""
    th = FocusBboxThreshold()
    cid = "neg_test"
    # Place + remove 3 times — each remove shouldn't drive weight below 0
    for _ in range(3):
        th._on_focus_released(_make(EcpEventType.FOCUS_RELEASED, correlation_id=cid))
    # Now place once — should still need 5 focuses to cross from 0
    for _ in range(4):
        th._on_focus_anchored(_make(EcpEventType.FOCUS_ANCHORED, correlation_id=cid))
    assert th.thresholds_crossed == 0


def test_separate_correlation_ids_track_separately():
    th = FocusBboxThreshold()
    th._on_bbox_placed(_make(EcpEventType.BBOX_PLACED, correlation_id="a"))
    th._on_bbox_placed(_make(EcpEventType.BBOX_PLACED, correlation_id="b"))
    assert th.thresholds_crossed == 2


# ─── EcpEventIngest wiring ─────────────────────────────────────


def test_register_subscribes_to_all_four_event_types():
    ingest = EcpEventIngest()
    th = FocusBboxThreshold()
    th.register(ingest)

    for et in (
        EcpEventType.FOCUS_ANCHORED,
        EcpEventType.FOCUS_RELEASED,
        EcpEventType.BBOX_PLACED,
        EcpEventType.BBOX_REMOVED,
    ):
        # Confirm at least one subscriber registered for each event type.
        # Reach into private dict to avoid adding test-only public API.
        assert len(ingest._subs.get(et.value, [])) >= 1, et


def test_full_ingest_to_threshold_chain():
    """End-to-end: build event, push through ingest, threshold accumulator
    fires."""
    ingest = EcpEventIngest()
    th = FocusBboxThreshold()
    th.register(ingest)

    bbox = EcpEvent.build(
        event_type=EcpEventType.BBOX_PLACED,
        source=EcpEventSource.UNITY,
        payload={"bbox_id": "wiring_test"},
        correlation_id="wiring_test",
    )
    ingest.handle_raw("parrot.ecp.event", bbox.to_wire_json().encode("utf-8"))

    assert th.thresholds_crossed == 1


# ─── Package boundary hard constraint ──────────────────────────


def test_attention_init_does_not_export_Attention_class():
    """Entry doc §8.1 L13: top-level `Attention` symbol forbidden so future
    readers cannot mistake the Phase 4 临时阈值器 for the unbuilt L3 module."""
    import parrot.dsg.attention as attention_pkg

    assert not hasattr(attention_pkg, "Attention"), (
        "parrot.dsg.attention package must NOT export `Attention` "
        "(entry doc §8.1 L13). Use FocusBboxThreshold instead."
    )
    assert "Attention" not in attention_pkg.__all__


def test_attention_init_only_exports_focus_bbox_threshold():
    import parrot.dsg.attention as attention_pkg

    assert attention_pkg.__all__ == ["FocusBboxThreshold"]


def test_threshold_module_header_calls_out_non_l3():
    """Audit the file header — entry doc §8.5 #3 hard requirement."""
    from pathlib import Path

    p = Path(__file__).resolve().parents[2] / "src" / "parrot" / "dsg" / "attention" / "threshold.py"
    text = p.read_text(encoding="utf-8")
    head = text.split('"""', 2)[1]  # docstring body
    assert "Phase 4" in head and "L3" in head, (
        "threshold.py header must explicitly mark Phase 4 + non-L3 status "
        "(entry doc §8.5 #3)."
    )
