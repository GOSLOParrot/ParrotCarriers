"""Sprint4 Phase 4 W6-7 — focus observer: RefBinding lifecycle.

Mirrors ``brain/observer/bbox.py`` but for ``focus.anchored`` /
``focus.released`` events. Same boundary contract — observe + manage
RefBinding lifecycle, do NOT compute attention math.
"""

from __future__ import annotations

import logging

from parrot.brain import refs as refs_registry
from parrot.brain.event_ingest import EcpEventIngest
from parrot.shared.ecp_event import EcpEvent, EcpEventType


logger = logging.getLogger(__name__)


_metrics: dict[str, int] = {
    "anchored_received": 0,
    "released_received": 0,
    "refs_created": 0,
    "refs_removed": 0,
    "missing_focus_id": 0,
}


def get_metrics_snapshot() -> dict[str, int]:
    return dict(_metrics)


def reset_metrics_for_tests() -> None:
    for k in _metrics:
        _metrics[k] = 0


def _on_focus_anchored(event: EcpEvent) -> None:
    _metrics["anchored_received"] += 1
    payload = event.payload or {}
    focus_id = str(payload.get("focus_id", "") or "")
    if not focus_id:
        _metrics["missing_focus_id"] += 1
        logger.debug(
            "[observer.focus] anchored without focus_id (event_id=%s)",
            event.event_id,
        )
        return
    label = str(payload.get("label", "") or "")
    refs_registry.bind_focus(
        focus_id=focus_id,
        source_event_id=event.event_id,
        label=label,
    )
    _metrics["refs_created"] += 1


def _on_focus_released(event: EcpEvent) -> None:
    _metrics["released_received"] += 1
    payload = event.payload or {}
    focus_id = str(payload.get("focus_id", "") or "")
    if not focus_id:
        _metrics["missing_focus_id"] += 1
        return
    removed = refs_registry.unbind_focus(focus_id)
    if removed is not None:
        _metrics["refs_removed"] += 1


def register(ingest: EcpEventIngest) -> None:
    ingest.subscribe(EcpEventType.FOCUS_ANCHORED, _on_focus_anchored)
    ingest.subscribe(EcpEventType.FOCUS_RELEASED, _on_focus_released)


__all__ = ["get_metrics_snapshot", "register", "reset_metrics_for_tests"]
