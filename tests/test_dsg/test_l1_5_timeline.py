"""DSG-POOL-V1 § 2.4 — Timeline append-only marker log."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from parrot.dsg.l1_5.timeline import (
    Timeline,
    TimelineMarker,
    TimelineMarkerKind,
)


def test_mark_appends() -> None:
    t = Timeline()
    m1 = t.mark(TimelineMarkerKind.EPISODE_START, payload={"episode_id": "ep1"})
    m2 = t.mark(TimelineMarkerKind.INTENT_EVENT_OPEN, payload={"event_id": "ev1"})
    assert t.count() == 2
    assert m1.kind == TimelineMarkerKind.EPISODE_START
    assert m2.kind == TimelineMarkerKind.INTENT_EVENT_OPEN


def test_mark_default_ts_is_now() -> None:
    import time
    t = Timeline()
    before = time.time()
    m = t.mark(TimelineMarkerKind.PLAN_DRAFTED)
    after = time.time()
    assert before <= m.ts <= after


def test_get_timeline_filters_by_window() -> None:
    t = Timeline()
    t.mark(TimelineMarkerKind.EPISODE_START, ts=100.0)
    t.mark(TimelineMarkerKind.INTENT_EVENT_OPEN, ts=200.0)
    t.mark(TimelineMarkerKind.PLAN_DRAFTED, ts=300.0)
    out = t.get_timeline(window=(150.0, 250.0))
    assert len(out) == 1
    assert out[0].kind == TimelineMarkerKind.INTENT_EVENT_OPEN


def test_get_timeline_filters_by_kinds() -> None:
    t = Timeline()
    t.mark(TimelineMarkerKind.EPISODE_START)
    t.mark(TimelineMarkerKind.INTENT_EVENT_OPEN)
    t.mark(TimelineMarkerKind.PLAN_DRAFTED)
    out = t.get_timeline(
        kinds=frozenset({TimelineMarkerKind.PLAN_DRAFTED}),
    )
    assert len(out) == 1
    assert out[0].kind == TimelineMarkerKind.PLAN_DRAFTED


def test_serialize_timeline_to_jsonl(tmp_path: Path) -> None:
    t = Timeline()
    t.mark(TimelineMarkerKind.EPISODE_START, payload={"episode_id": "ep1"})
    t.mark(TimelineMarkerKind.INTENT_EVENT_CLOSE, payload={"event_id": "ev1"})

    dst = tmp_path / "timeline.jsonl"
    t.serialize_timeline(dst)

    assert dst.exists()
    rows = [json.loads(line) for line in dst.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 2
    kinds = {row["kind"] for row in rows}
    assert kinds == {"episode_start", "intent_event_close"}


def test_clear_resets_count() -> None:
    t = Timeline()
    t.mark(TimelineMarkerKind.EPISODE_START)
    t.mark(TimelineMarkerKind.INTENT_EVENT_OPEN)
    assert t.count() == 2
    t.clear()
    assert t.count() == 0


def test_marker_payload_is_copied_not_aliased() -> None:
    """Mutating the original dict after mark() must not affect the marker."""
    t = Timeline()
    payload = {"key": "value"}
    m = t.mark(TimelineMarkerKind.EPISODE_START, payload=payload)
    payload["key"] = "MUTATED"
    assert m.payload["key"] == "value"
