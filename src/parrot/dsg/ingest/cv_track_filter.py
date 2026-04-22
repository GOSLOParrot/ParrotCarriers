"""cv_track_filter — A10 CV track → Observations (SKELETON, Sprint 2 T6).

Sprint 2 scope: **skeleton only**. The A10 pipeline (SAM2 + DINOv2 + YOLO)
is not deployed yet, so this filter exists to lock the L1.5 → Ingest shape
and to give `mode_controller` something non-null to enable when `dsg_mode
== DSG_FULL`. The real detection → Observation translation lives here, but
actual calls happen in Sprint 3+ once A10 comes online.

Authority model (aligned with L1.5 DetectionAuthority ordering):
    USER  > GEMINI_DESCRIBED > REID_CONFIRMED > YOLO_VOTED > YOLO_SINGLE
    → Observation.confirmation derives from the top detection's authority:
        REID_CONFIRMED or higher → CONFIRMED
        YOLO_VOTED              → TENTATIVE
        YOLO_SINGLE / UNKNOWN   → UNCERTAIN

Rejection rules (in process_frame):
    - No detections → reject (keeps L2-B sparse until something real shows)
    - Detection label in global blocklist → reject
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
from parrot.dsg.l1_5_protocol import Detection, DetectionAuthority, SensorFrame
from parrot.dsg.l2b_types import ConfirmationStatus, NodeKind

logger = logging.getLogger(__name__)

_LABEL_BLOCKLIST = frozenset({"unknown", "object", "thing"})


class CvTrackFilter(IngestFilter):
    """Turns L1.5 SensorFrame detections into L2-B-bound Observations."""

    name = "cv_track_filter"

    def process_frame(self, frame: SensorFrame) -> IngestOutcome:
        if not frame.has_detections():
            return IngestOutcome(
                filter_name=self.name, rejected=1, reason="no_detections"
            )

        observations: list[Observation] = []
        rejected = 0
        for det in frame.detections:
            obs = self._detection_to_observation(det, frame)
            if obs is None:
                rejected += 1
                continue
            observations.append(obs)

        return IngestOutcome(
            filter_name=self.name,
            accepted=len(observations),
            rejected=rejected,
            observations=tuple(observations),
        )

    def process_text(
        self,
        text: str,
        *,
        source: ObservationSource,
        provenance_stream_id: str = "",
        meta: dict[str, Any] | None = None,
    ) -> IngestOutcome:
        return IngestOutcome(filter_name=self.name)

    # ─── Helpers ────────────────────────────────────────────────────

    def _detection_to_observation(
        self, det: Detection, frame: SensorFrame
    ) -> Observation | None:
        if det.label.lower() in _LABEL_BLOCKLIST:
            return None

        confirmation = self._authority_to_confirmation(det.authority)
        source = (
            ObservationSource.CV_SENTINEL
            if frame.source.value.startswith("sentinel")
            else ObservationSource.CV_A10
        )

        return Observation(
            source=source,
            provenance_stream_id=frame.provenance_parent or "",
            label=det.label,
            kind=NodeKind.OBJECT,
            description=det.meta.get("description", ""),
            confidence=det.confidence,
            confirmation=confirmation,
            snapshot_uuid=frame.frame_ref,
            bbox=det.bbox,
            meta={
                "track_id": det.track_id,
                "reid_hash": det.reid_hash,
                "authority": det.authority.value,
            },
        )

    @staticmethod
    def _authority_to_confirmation(authority: DetectionAuthority) -> ConfirmationStatus:
        if authority.priority() >= DetectionAuthority.REID_CONFIRMED.priority():
            return ConfirmationStatus.CONFIRMED
        if authority.priority() >= DetectionAuthority.YOLO_VOTED.priority():
            return ConfirmationStatus.TENTATIVE
        return ConfirmationStatus.UNCERTAIN


__all__ = ["CvTrackFilter"]
