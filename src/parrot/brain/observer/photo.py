"""Sprint4 Phase 4 — photo observer (skeleton).

Phase 4 W8 (visual range — tool ④) wires the real handler:

    Unity ──► EcpEvent ``photo.taken_preview`` (preview JPEG ≤ 8KB inline)
                 │
                 ▼
    this module ─► BB transient (preview metadata)
                 ─► register pending asset upload
                 ─► await Brain HTTP /upload/photo handler emitting
                    ``photo.asset_uploaded`` (correlation_id == preview event_id)
                 ─► write PhotoNode to L2-B (via dsg.attention or its W8
                    successor)

For Phase 4 W1-2 (current) the module is the registration hookpoint only;
the inline preview ↔ HTTP asset reconciliation is W8 work and depends on
the Brain HTTP endpoint landing.
"""

from __future__ import annotations

import logging

from parrot.brain.event_ingest import EcpEventIngest


logger = logging.getLogger(__name__)


def register(ingest: EcpEventIngest) -> None:
    """Phase 4 W1-2: no-op. W8 will hook preview / asset reconciliation here."""
    logger.debug("[observer.photo] Phase 4 W1-2 stub registered (no subscribers)")


__all__ = ["register"]
