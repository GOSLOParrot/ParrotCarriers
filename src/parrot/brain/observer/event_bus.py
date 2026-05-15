"""Sprint4 Phase 4 — Observer registration entry point.

Single function :func:`register_phase4_observers` subscribes all Phase 4
Observer modules to a shared :class:`parrot.brain.event_ingest.EcpEventIngest`
instance. ``brain.agent`` calls this once during boot.

Why a single registration call vs each module self-registering at import:
    * Import-time side effects make ordering fragile (Observer would need
      EcpEventIngest before its module body runs).
    * Single call lets unit tests construct an ingest, call this, and assert
      the subscriber set.
    * Phase 4 W3+ may want to gate observer registration on feature flags
      (e.g. tool ④ photo observer off until UI lands); a single hookpoint
      makes flag wiring easy.
"""

from __future__ import annotations

import logging

from parrot.brain.event_ingest import EcpEventIngest


logger = logging.getLogger(__name__)


def register_phase4_observers(ingest: EcpEventIngest) -> None:
    """Wire all Phase 4 observers onto the shared ingest.

    Idempotent: re-registration appends fresh subscribers (EcpEventIngest's
    subscriber list is a list, not a set). Brain agent boot must call this
    exactly once; tests should construct a fresh EcpEventIngest per test
    rather than relying on idempotency.

    **Order matters** for W6-7 attention pipeline: bbox/focus observers MUST
    register before the threshold accumulator subscribes to the same events
    (caller wires threshold separately via FocusBboxThreshold().register()).
    Subscribers fire in registration order; threshold reads from the
    RefBinding registry that bbox/focus populate on the same event.
    """
    # Lazy import to avoid circular: each observer module may import event_bus
    # symbols (e.g. logger) once Phase 4 W4+ wires real handlers.
    from parrot.brain.observer import bbox, focus, photo, sighting, snapshot, visual_tool

    snapshot.register(ingest)
    sighting.register(ingest)
    photo.register(ingest)
    visual_tool.register(ingest)
    # W6-7: bbox + focus observers manage RefBinding lifecycle. They must
    # subscribe BEFORE FocusBboxThreshold (which the agent boot registers
    # right after this call) so that by the time threshold's _add_weight
    # runs and looks up a Ref, the bind_bbox / bind_focus has already
    # populated parrot.brain.refs.
    bbox.register(ingest)
    focus.register(ingest)

    logger.info(
        "Phase 4 observers registered: snapshot / sighting / photo / visual_tool / bbox / focus"
    )


__all__ = ["register_phase4_observers"]
