"""Sprint4 Phase 4 — sighting observer (skeleton).

Phase 4 W4-5 wires the real handler. This is the "记录" half: when
visual_match completes (synchronously in identify_object Intent), we publish
``sighting.matched`` or ``sighting.unmatched`` as a brain-source EcpEvent so
downstream consumers (DSG ingest filters, Graphiti archiver, future
attention thresholding) can subscribe through the same EcpEventIngest the
Unity-source events flow through.

The actual EcpEvent **publish** path back onto the wire (brain → Unity room)
is wired from ``brain.agent`` in W3 — this module only has to call
``ingest._dispatch`` (or a future explicit publish helper) once the producer
exists.

For W1-2 (current) we register zero subscribers but keep the module so the
package wiring graph is complete and the entry-doc §8.4 routing is honored.
"""

from __future__ import annotations

import logging

from parrot.brain.event_ingest import EcpEventIngest


logger = logging.getLogger(__name__)


def register(ingest: EcpEventIngest) -> None:
    """Phase 4 W1-2: no-op. W4-5 will hook visual_match callbacks here."""
    logger.debug("[observer.sighting] Phase 4 W1-2 stub registered (no subscribers)")


__all__ = ["register"]
