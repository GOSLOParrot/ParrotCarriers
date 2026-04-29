"""Sprint4 Phase 4 W6-7 — bbox observer: RefBinding lifecycle.

Authoritative spec: ``architecture/sprint4_phase4_entry_20260430.md §8.4``
+ §3.7 Observer/Attention 边界.

Subscribes to ``bbox.placed`` / ``bbox.removed`` EcpEvents and maintains
the corresponding :class:`parrot.shared.ref_binding.RefBinding` entries
in :mod:`parrot.brain.refs`.

Boundary contract (entry doc §3.7):
    Observer = "记录" (recording). This module only **registers and
    unregisters** RefBindings — it does NOT compute attention weight (that
    is :class:`parrot.dsg.attention.threshold.FocusBboxThreshold`), it
    does NOT decide thresholds, it does NOT write L2-B nodes
    (:mod:`parrot.dsg.attention.hint_writer`).

Phase 4 W6-7 contract notes
---------------------------
* ``bbox.placed`` payload MUST carry ``bbox_id`` (Unity-side stable id).
  Without it we cannot index the Ref for the matching ``bbox.removed``;
  in that case we still create a Ref but do not index it (same Ref will
  expire at session end via :func:`parrot.brain.refs.reset_refs_for_session`).
* ``bbox.removed`` is best-effort — Unity can drop a removed event on
  reconnect, and we don't want to leak Refs. The session reset is the
  hard floor.
"""

from __future__ import annotations

import logging

from parrot.brain import refs as refs_registry
from parrot.brain.event_ingest import EcpEventIngest
from parrot.shared.ecp_event import EcpEvent, EcpEventType


logger = logging.getLogger(__name__)


_metrics: dict[str, int] = {
    "placed_received": 0,
    "removed_received": 0,
    "refs_created": 0,
    "refs_removed": 0,
    "missing_bbox_id": 0,
}


def get_metrics_snapshot() -> dict[str, int]:
    return dict(_metrics)


def reset_metrics_for_tests() -> None:
    for k in _metrics:
        _metrics[k] = 0


def _on_bbox_placed(event: EcpEvent) -> None:
    _metrics["placed_received"] += 1
    payload = event.payload or {}
    bbox_id = str(payload.get("bbox_id", "") or "")
    if not bbox_id:
        _metrics["missing_bbox_id"] += 1
        logger.debug(
            "[observer.bbox] placed without bbox_id (event_id=%s)", event.event_id,
        )
        return
    label = str(payload.get("label", "") or "")
    refs_registry.bind_bbox(
        bbox_id=bbox_id,
        source_event_id=event.event_id,
        label=label,
    )
    _metrics["refs_created"] += 1


def _on_bbox_removed(event: EcpEvent) -> None:
    _metrics["removed_received"] += 1
    payload = event.payload or {}
    bbox_id = str(payload.get("bbox_id", "") or "")
    if not bbox_id:
        _metrics["missing_bbox_id"] += 1
        return
    removed = refs_registry.unbind_bbox(bbox_id)
    if removed is not None:
        _metrics["refs_removed"] += 1


def register(ingest: EcpEventIngest) -> None:
    ingest.subscribe(EcpEventType.BBOX_PLACED, _on_bbox_placed)
    ingest.subscribe(EcpEventType.BBOX_REMOVED, _on_bbox_removed)


__all__ = ["get_metrics_snapshot", "register", "reset_metrics_for_tests"]
