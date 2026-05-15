"""Observer for App visual-tool lifecycle events.

Legacy ``bbox.placed`` / ``focus.anchored`` events only bind and unbind refs.
The richer ``visual_tool.lifecycle`` event is the App-facing contract for BBox
and MAG controllers: it records time-aligned evidence, computes a conservative
tool salience score, stages IntentWorkspace context, and optionally emits a C3
context notice through the existing awareness path.
"""

from __future__ import annotations

import logging

from parrot.brain.event_ingest import EcpEventIngest
from parrot.brain.vision.tool_lifecycle import bridge_visual_tool_lifecycle_event
from parrot.shared.ecp_event import EcpEvent, EcpEventType

logger = logging.getLogger(__name__)

_metrics = {
    "lifecycle_received": 0,
    "lifecycle_bridged": 0,
    "bridge_errors": 0,
}


def register(ingest: EcpEventIngest) -> None:
    ingest.subscribe(EcpEventType.VISUAL_TOOL_LIFECYCLE, _on_visual_tool_lifecycle)


def get_metrics_snapshot() -> dict[str, int]:
    return dict(_metrics)


def reset_metrics_for_tests() -> None:
    for key in _metrics:
        _metrics[key] = 0


def _on_visual_tool_lifecycle(event: EcpEvent) -> None:
    _metrics["lifecycle_received"] += 1
    try:
        bridge_visual_tool_lifecycle_event(event)
    except Exception:
        _metrics["bridge_errors"] += 1
        logger.exception(
            "visual_tool.lifecycle observer failed event_id=%s", event.event_id
        )
        return
    _metrics["lifecycle_bridged"] += 1


__all__ = ["get_metrics_snapshot", "register", "reset_metrics_for_tests"]
