"""Observer for storage-backed snapshot/photo metadata events."""

from __future__ import annotations

import logging

from parrot.brain.event_ingest import EcpEventIngest
from parrot.shared.ecp_event import EcpEvent, EcpEventType


logger = logging.getLogger(__name__)


def _on_snapshot_captured(event: EcpEvent) -> None:
    """Log snapshot metadata without assuming inline image transport."""
    logger.debug(
        "[observer.snapshot] event_id=%s payload_keys=%s",
        event.event_id,
        sorted(event.payload.keys()),
    )
    try:
        from parrot.brain.vision.evidence import (
            EvidenceKind,
            record_ecp_evidence_sample,
        )

        payload = event.payload or {}
        record_ecp_evidence_sample(
            event,
            kind=EvidenceKind.IMAGE_ASSET,
            asset_path=str(payload.get("asset_path", "") or ""),
            asset_uri=str(payload.get("asset_ref", "") or payload.get("asset_uri", "") or ""),
            description=str(payload.get("description", "") or "snapshot.captured"),
            meta={"source": "observer.snapshot"},
        )
    except Exception:
        logger.debug("[observer.snapshot] evidence ledger write failed", exc_info=True)


def register(ingest: EcpEventIngest) -> None:
    ingest.subscribe(EcpEventType.SNAPSHOT_CAPTURED, _on_snapshot_captured)


__all__ = ["register"]
