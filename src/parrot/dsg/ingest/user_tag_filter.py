"""user_tag_filter — Obsidian double-link tag sync → Observations.

Sprint 2 T6. Consumes the structured payload emitted by
`parrot.dsg.triggers.ssot_enrichment_trigger` when the user adds / edits
a `[[name]]` double-link in an Obsidian note that carries a `uuid::...`
identifier.

Authority model:
    Obsidian tags come from a human, with a known UUID — highest trust.
    Emit CONFIRMED with confidence=1.0 and stamp `obsidian_uuid` so the
    runner can match existing L2-B nodes by that handle instead of label.

Input shape (from ssot_enrichment_trigger):
    {
        "label": "user's backpack",
        "obsidian_uuid": "...",        # required, this is what makes the tag trusted
        "description": "...",          # optional, from note body
        "tags": ["..."],               # optional
    }

Missing uuid → rejection (freeform tags without uuid belong to
text_source_filter's USER_EXPLICIT lane, not here).
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

_MAX_LABEL_LEN = 128


class UserTagFilter(IngestFilter):
    """Converts Obsidian tag-sync payloads to CONFIRMED Observations."""

    name = "user_tag_filter"

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
        # text-path not used
        return IngestOutcome(filter_name=self.name)

    def process_tag(
        self,
        payload: dict[str, Any],
        *,
        provenance_stream_id: str = "",
    ) -> IngestOutcome:
        if not isinstance(payload, dict):
            return IngestOutcome(
                filter_name=self.name, rejected=1, reason="not_a_dict"
            )
        label = str(payload.get("label", "")).strip()[:_MAX_LABEL_LEN]
        uuid = str(payload.get("obsidian_uuid", "")).strip()
        if not label or not uuid:
            return IngestOutcome(
                filter_name=self.name,
                rejected=1,
                reason="missing_label_or_uuid",
            )

        obs = Observation(
            source=ObservationSource.USER_TAG_OBSIDIAN,
            provenance_stream_id=provenance_stream_id,
            obsidian_uuid=uuid,
            label=label,
            kind=NodeKind.OBJECT,
            description=str(payload.get("description", ""))[:400],
            confidence=1.0,
            confirmation=ConfirmationStatus.CONFIRMED,
            meta={"tags": list(payload.get("tags", []))[:10]},
        )
        return IngestOutcome(
            filter_name=self.name,
            accepted=1,
            observations=(obs,),
        )


__all__ = ["UserTagFilter"]
