"""Sprint4 Phase 4 — `snapshot.captured` observer (skeleton).

Authoritative spec: ``architecture/sprint4_phase4_entry_20260430.md §8.3``
(event_type registry) + §8.4 (Observer code routing).

Phase 4 W4-5 wires the real handler that mirrors ``snapshot.captured``
payloads to the Blackboard ``transient/just_captured_photo`` key (writer
stays ``brain.vision.snapshot`` per ``bb_schema.py`` — this observer is a
**read-side** projection, not the BB key's producer). Phase 4 W1-2 (current)
just provides the registration hookpoint so the package's wiring graph is
complete.
"""

from __future__ import annotations

import logging

from parrot.brain.event_ingest import EcpEventIngest
from parrot.shared.ecp_event import EcpEvent, EcpEventType


logger = logging.getLogger(__name__)


def _on_snapshot_captured(event: EcpEvent) -> None:
    """Phase 4 W1-2 skeleton: log + drop. W4-5 wires BB transient mirror.

    Not implementing the BB write yet because Phase 4 W3 introduces the
    captureSnapshot RPC end-to-end (tool ② chain) and the BB write should
    be tested against a real producer, not synthesized payload shapes.
    """
    logger.debug(
        "[observer.snapshot] event_id=%s payload_keys=%s",
        event.event_id, sorted(event.payload.keys()),
    )


def register(ingest: EcpEventIngest) -> None:
    ingest.subscribe(EcpEventType.SNAPSHOT_CAPTURED, _on_snapshot_captured)


__all__ = ["register"]
