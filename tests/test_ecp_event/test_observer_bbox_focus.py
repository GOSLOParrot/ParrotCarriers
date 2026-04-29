"""Tests for `parrot.brain.observer.bbox` + `focus` (Phase 4 W6-7).

Coverage focus:
    1. register subscribes to the right 4 event types
    2. bbox.placed → bind_bbox + counter increments
    3. bbox.removed → unbind_bbox + counter increments
    4. Missing bbox_id / focus_id is gracefully counted, no crash
    5. focus.anchored / released mirror behaviour
"""

from __future__ import annotations

import pytest

from parrot.brain import refs as refs_registry
from parrot.brain.event_ingest import (
    EcpEventIngest,
    reset_ecp_event_ingest_for_tests,
)
from parrot.brain.observer import bbox as bbox_observer
from parrot.brain.observer import focus as focus_observer
from parrot.shared.ecp_event import (
    EcpEvent,
    EcpEventSource,
    EcpEventType,
)


@pytest.fixture(autouse=True)
def _reset():
    reset_ecp_event_ingest_for_tests()
    refs_registry.reset_refs_for_tests()
    bbox_observer.reset_metrics_for_tests()
    focus_observer.reset_metrics_for_tests()
    yield
    reset_ecp_event_ingest_for_tests()
    refs_registry.reset_refs_for_tests()
    bbox_observer.reset_metrics_for_tests()
    focus_observer.reset_metrics_for_tests()


def _bbox_placed(bbox_id: str = "bb_test") -> bytes:
    e = EcpEvent.build(
        event_type=EcpEventType.BBOX_PLACED,
        source=EcpEventSource.UNITY,
        payload={"bbox_id": bbox_id, "corners": [[0, 0], [1, 1]]},
    )
    return e.to_wire_json().encode("utf-8")


def _bbox_removed(bbox_id: str = "bb_test") -> bytes:
    e = EcpEvent.build(
        event_type=EcpEventType.BBOX_REMOVED,
        source=EcpEventSource.UNITY,
        payload={"bbox_id": bbox_id},
    )
    return e.to_wire_json().encode("utf-8")


def _focus_anchored(focus_id: str = "f_test") -> bytes:
    e = EcpEvent.build(
        event_type=EcpEventType.FOCUS_ANCHORED,
        source=EcpEventSource.UNITY,
        payload={"focus_id": focus_id, "center": [0.5, 0.5]},
    )
    return e.to_wire_json().encode("utf-8")


def _focus_released(focus_id: str = "f_test") -> bytes:
    e = EcpEvent.build(
        event_type=EcpEventType.FOCUS_RELEASED,
        source=EcpEventSource.UNITY,
        payload={"focus_id": focus_id},
    )
    return e.to_wire_json().encode("utf-8")


# ─── registration ────────────────────────────────────────────────────


def test_bbox_register_subscribes_to_placed_and_removed():
    ingest = EcpEventIngest()
    bbox_observer.register(ingest)
    assert len(ingest._subs.get("bbox.placed", [])) == 1
    assert len(ingest._subs.get("bbox.removed", [])) == 1


def test_focus_register_subscribes_to_anchored_and_released():
    ingest = EcpEventIngest()
    focus_observer.register(ingest)
    assert len(ingest._subs.get("focus.anchored", [])) == 1
    assert len(ingest._subs.get("focus.released", [])) == 1


# ─── bbox lifecycle ─────────────────────────────────────────────────


def test_bbox_placed_creates_ref_and_indexes_it():
    ingest = EcpEventIngest()
    bbox_observer.register(ingest)
    ingest.handle_raw("parrot.ecp.event", _bbox_placed("bb_alpha"))

    ref = refs_registry.get_ref_by_bbox("bb_alpha")
    assert ref is not None
    assert ref.kind == "bbox"
    metrics = bbox_observer.get_metrics_snapshot()
    assert metrics["placed_received"] == 1
    assert metrics["refs_created"] == 1


def test_bbox_removed_drops_ref():
    ingest = EcpEventIngest()
    bbox_observer.register(ingest)
    ingest.handle_raw("parrot.ecp.event", _bbox_placed("bb_drop"))
    assert refs_registry.get_ref_by_bbox("bb_drop") is not None

    ingest.handle_raw("parrot.ecp.event", _bbox_removed("bb_drop"))
    assert refs_registry.get_ref_by_bbox("bb_drop") is None
    assert bbox_observer.get_metrics_snapshot()["refs_removed"] == 1


def test_bbox_placed_without_bbox_id_counted_as_missing():
    ingest = EcpEventIngest()
    bbox_observer.register(ingest)
    bad = EcpEvent.build(
        event_type=EcpEventType.BBOX_PLACED,
        source=EcpEventSource.UNITY,
        payload={},  # NO bbox_id
    )
    ingest.handle_raw("parrot.ecp.event", bad.to_wire_json().encode("utf-8"))

    metrics = bbox_observer.get_metrics_snapshot()
    assert metrics["placed_received"] == 1
    assert metrics["missing_bbox_id"] == 1
    assert metrics["refs_created"] == 0
    assert refs_registry.metrics_snapshot()["bbox_refs"] == 0


# ─── focus lifecycle ────────────────────────────────────────────────


def test_focus_anchored_creates_ref():
    ingest = EcpEventIngest()
    focus_observer.register(ingest)
    ingest.handle_raw("parrot.ecp.event", _focus_anchored("f_alpha"))

    assert refs_registry.get_ref_by_focus("f_alpha") is not None
    assert focus_observer.get_metrics_snapshot()["refs_created"] == 1


def test_focus_released_drops_ref():
    ingest = EcpEventIngest()
    focus_observer.register(ingest)
    ingest.handle_raw("parrot.ecp.event", _focus_anchored("f_drop"))
    ingest.handle_raw("parrot.ecp.event", _focus_released("f_drop"))

    assert refs_registry.get_ref_by_focus("f_drop") is None
    assert focus_observer.get_metrics_snapshot()["refs_removed"] == 1


# ─── coexistence with phase4 register ──────────────────────────────


def test_register_phase4_observers_includes_bbox_focus():
    """Smoke test that the W6-7 observers are wired into the boot helper."""
    from parrot.brain.observer import register_phase4_observers

    ingest = EcpEventIngest()
    register_phase4_observers(ingest)

    # All Phase 4 event types we care about have at least one subscriber.
    for event_type_value in (
        "snapshot.captured",
        "sighting.matched",
        "sighting.unmatched",
        "photo.taken_preview",
        "bbox.placed",
        "bbox.removed",
        "focus.anchored",
        "focus.released",
    ):
        # snapshot/photo W1-2 stubs don't actually subscribe; only check
        # the W4-5 + W6-7 observers that DO subscribe.
        subs = ingest._subs.get(event_type_value, [])
        if event_type_value in {
            "snapshot.captured", "photo.taken_preview",
        }:
            # Phase 4 W4-5 / W8 still stubs — no subscribers asserted
            continue
        assert len(subs) >= 1, f"no subscriber for {event_type_value}"
