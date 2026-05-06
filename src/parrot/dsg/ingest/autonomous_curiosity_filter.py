"""Autonomous Curiosity Filter — GOSLO self-initiated discovery → Observation.

DSG-POOL-V1 § 3 + master § 3.3 (priority < user-asked, short TTL).

Input shape (from Brain attention path / GosloCuriosityTrigger):
    {
        "label": "...",                # required
        "description": "...",           # optional
        "confidence": 0.5,              # default 0.5
        "obsidian_uuid": "",
        "graphiti_uuid": "",
        "snapshot_uuid": "",
        "reference_image_path": "",
        "provenance_stream_id": "",
        "meta": {...}
    }

Emits an Observation with ``source=GOSLO_AUTONOMOUS``. The L1.5 pool's
DesktopPolicy routes such observations to ``BucketKind.AUTONOMOUS_CURIOSITY``
(short TTL applied via the bucket's default_ttl_seconds).
"""

from __future__ import annotations

import logging
from typing import Any

from parrot.dsg.ingest.base import (
    IngestFilter,
    IngestOutcome,
    Observation,
    ObservationSource,
)
from parrot.dsg.l1_5_protocol import SensorFrame
from parrot.dsg.l2b_types import ConfirmationStatus, NodeKind

logger = logging.getLogger(__name__)


class AutonomousCuriosityFilter(IngestFilter):
    """Converts GOSLO curiosity payloads to GOSLO_AUTONOMOUS Observations."""

    name = "autonomous_curiosity_filter"

    def process_frame(self, frame: SensorFrame) -> IngestOutcome:
        return IngestOutcome(filter_name=self.name)

    def process_text(
        self,
        text: str,
        *,
        source: ObservationSource,
        provenance_stream_id: str = "",
        meta: dict[str, Any] | None = None,
    ) -> IngestOutcome:
        # text-path not used; curiosity goes through process_payload
        return IngestOutcome(filter_name=self.name)

    def process_payload(
        self,
        payload: dict[str, Any],
        *,
        provenance_stream_id: str = "",
    ) -> IngestOutcome:
        if not isinstance(payload, dict):
            return IngestOutcome(
                filter_name=self.name, rejected=1, reason="not_a_dict",
            )
        label = str(payload.get("label", "")).strip()
        if not label:
            return IngestOutcome(
                filter_name=self.name, rejected=1, reason="missing_label",
            )

        try:
            confidence = float(payload.get("confidence", 0.5))
        except (TypeError, ValueError):
            confidence = 0.5
        confidence = max(0.0, min(1.0, confidence))

        obs = Observation(
            source=ObservationSource.GOSLO_AUTONOMOUS,
            provenance_stream_id=provenance_stream_id or str(payload.get("provenance_stream_id", "")),
            obsidian_uuid=str(payload.get("obsidian_uuid", "")),
            graphiti_uuid=str(payload.get("graphiti_uuid", "")),
            snapshot_uuid=str(payload.get("snapshot_uuid", "")),
            reference_image_path=str(payload.get("reference_image_path", "")),
            label=label[:128],
            kind=NodeKind.OBJECT,
            description=str(payload.get("description", ""))[:400],
            confidence=confidence,
            confirmation=ConfirmationStatus.TENTATIVE,
            meta=dict(payload.get("meta", {}) or {}),
        )
        return IngestOutcome(
            filter_name=self.name, accepted=1, observations=(obs,),
        )


__all__ = ["AutonomousCuriosityFilter"]
