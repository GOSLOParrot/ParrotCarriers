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
    """
    # Lazy import to avoid circular: each observer module may import event_bus
    # symbols (e.g. logger) once Phase 4 W4+ wires real handlers.
    from parrot.brain.observer import photo, sighting, snapshot

    snapshot.register(ingest)
    sighting.register(ingest)
    photo.register(ingest)

    logger.info(
        "Phase 4 observers registered: snapshot / sighting / photo (skeletons)"
    )


__all__ = ["register_phase4_observers"]
