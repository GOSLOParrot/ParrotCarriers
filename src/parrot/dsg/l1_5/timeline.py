"""L1.5 Timeline — append-only event-boundary marker log.

DSG-POOL-V1 § 2.4.

Timeline records boundary markers (Episode start/close, IntentEvent
open/close, Plan lifecycle, Scene switch, NanobotTask dispatch/result,
etc.). It does NOT store node bytes — observer / archive consume this
to align L2-B nodes with cognitive structure.

Serialization: ``data/conversations/{conv_id}/timeline.jsonl``
(DSG-ARCHIVE-V1 § 4.2).
"""

from __future__ import annotations

import json
import time
import uuid as uuid_lib
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class TimelineMarkerKind(str, Enum):
    EPISODE_START = "episode_start"
    EPISODE_CLOSE = "episode_close"
    INTENT_EVENT_OPEN = "intent_event_open"
    INTENT_EVENT_CLOSE = "intent_event_close"
    PLAN_DRAFTED = "plan_drafted"
    PLAN_CONFIRMED = "plan_confirmed"
    PLAN_COMPLETE = "plan_complete"
    PLAN_FAILED = "plan_failed"
    PLAN_CANCELLED = "plan_cancelled"
    PLAN_REVISED = "plan_revised"
    SCENE_SWITCHED = "scene_switched"
    BUCKET_OP = "bucket_op"
    NANOBOT_DISPATCHED = "nanobot_dispatched"
    NANOBOT_RESULT = "nanobot_result"
    AUTONOMOUS_CURIOSITY = "autonomous_curiosity"
    REF_BIND = "ref_bind"
    REF_BROKEN = "ref_broken"
    SOURCE_PRIORITY_OVERRIDE = "source_priority_override"


@dataclass(frozen=True)
class TimelineMarker:
    marker_id: str
    kind: TimelineMarkerKind
    ts: float
    payload: dict[str, Any] = field(default_factory=dict)
    related_node_uuids: tuple[str, ...] = ()


class Timeline:
    """Append-only marker list. Owned by ``L15Pool``.

    Concurrency note: append is O(1); ``get_timeline`` does linear scan.
    Desktop baseline expects < few thousand markers per session. P3 may
    add bucket-by-time partitioning if needed.
    """

    def __init__(self) -> None:
        self._markers: list[TimelineMarker] = []

    def mark(
        self,
        kind: TimelineMarkerKind,
        ts: float | None = None,
        payload: dict[str, Any] | None = None,
        related_node_uuids: tuple[str, ...] = (),
    ) -> TimelineMarker:
        marker = TimelineMarker(
            marker_id=uuid_lib.uuid4().hex[:12],
            kind=kind,
            ts=time.time() if ts is None else ts,
            payload=dict(payload) if payload else {},
            related_node_uuids=tuple(related_node_uuids),
        )
        self._markers.append(marker)
        return marker

    def get_timeline(
        self,
        window: tuple[float, float] | None = None,
        kinds: frozenset[TimelineMarkerKind] | None = None,
    ) -> list[TimelineMarker]:
        out = self._markers
        if window is not None:
            lo, hi = window
            out = [m for m in out if lo <= m.ts <= hi]
        if kinds is not None:
            out = [m for m in out if m.kind in kinds]
        return list(out)

    def serialize_timeline(self, dst: Path) -> Path:
        """Dump full timeline to JSON-Lines. Caller ensures parent dir exists."""
        dst.parent.mkdir(parents=True, exist_ok=True)
        with dst.open("w", encoding="utf-8") as f:
            for m in self._markers:
                row = {
                    "marker_id": m.marker_id,
                    "kind": m.kind.value,
                    "ts": m.ts,
                    "payload": m.payload,
                    "related_node_uuids": list(m.related_node_uuids),
                }
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        return dst

    def count(self) -> int:
        return len(self._markers)

    def clear(self) -> None:
        self._markers.clear()


__all__ = [
    "Timeline",
    "TimelineMarker",
    "TimelineMarkerKind",
]
