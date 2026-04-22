"""tool_result_filter — identify_object hits → Observations.

Sprint 2 T6. Consumes the structured dict emitted by
`brain.tools.identify_object` when it finds a match (L1/L2 paths in the
audit doc) and turns it into a high-authority Observation.

Confidence policy (sprint2_plan §5.1):
    - IDENTIFY_OBJECT source → CONFIRMED with confidence=1.0
    - Overrides same-label GEMINI_ORAL nodes (runner-side priority)

Input contract (see `audit_identify_object_no_screenshot_20260420.md §5.2`):
    {
        "label": "user's backpack",
        "graphiti_uuid": "abc-123",           # may be empty for novel objects
        "obsidian_uuid": "...",                # may be empty
        "confidence": 0.92,                    # identify_object's own score
        "description": "black nylon backpack",
        "reference_image_path": "data/snapshots/...",
        "bbox": {"x":..., "y":..., "w":..., "h":...},
        "snapshot_uuid": "...",
    }

Anything outside this shape is rejected rather than coerced. Sprint 4 may
add an L2 "save_new" branch; this filter stays schema-loyal.
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
from parrot.shared.snapshot import BBox

logger = logging.getLogger(__name__)

_REQUIRED_KEYS = ("label",)
_MAX_LABEL_LEN = 128


class ToolResultFilter(IngestFilter):
    """Promotes `identify_object` matches into CONFIRMED Observations."""

    name = "tool_result_filter"

    def process_frame(self, frame: SensorFrame) -> IngestOutcome:
        # Not a frame filter.
        return IngestOutcome(filter_name=self.name)

    def process_text(
        self,
        text: str,
        *,
        source: ObservationSource,
        provenance_stream_id: str = "",
        meta: dict[str, Any] | None = None,
    ) -> IngestOutcome:
        # Not a text filter either — tool results come via `process_result`.
        return IngestOutcome(filter_name=self.name)

    def process_result(
        self,
        result: dict[str, Any],
        *,
        provenance_stream_id: str = "",
    ) -> IngestOutcome:
        if not isinstance(result, dict):
            return IngestOutcome(
                filter_name=self.name, rejected=1, reason="not_a_dict"
            )
        missing = [k for k in _REQUIRED_KEYS if not result.get(k)]
        if missing:
            return IngestOutcome(
                filter_name=self.name,
                rejected=1,
                reason=f"missing_keys={','.join(missing)}",
            )

        label = str(result["label"]).strip()[:_MAX_LABEL_LEN]
        if not label:
            return IngestOutcome(
                filter_name=self.name, rejected=1, reason="empty_label"
            )

        bbox = self._parse_bbox(result.get("bbox"))
        confidence = float(result.get("confidence", 1.0))
        confidence = max(0.0, min(1.0, confidence))

        obs = Observation(
            source=ObservationSource.IDENTIFY_OBJECT,
            provenance_stream_id=provenance_stream_id,
            obsidian_uuid=str(result.get("obsidian_uuid", "")),
            graphiti_uuid=str(result.get("graphiti_uuid", "")),
            label=label,
            kind=NodeKind.OBJECT,
            description=str(result.get("description", ""))[:400],
            confidence=confidence,
            confirmation=ConfirmationStatus.CONFIRMED,
            snapshot_uuid=str(result.get("snapshot_uuid", "")),
            bbox=bbox,
            reference_image_path=str(result.get("reference_image_path", "")),
            last_sighting_path=str(result.get("last_sighting_path", "")),
            meta={"tool": "identify_object"},
        )
        return IngestOutcome(
            filter_name=self.name,
            accepted=1,
            observations=(obs,),
        )

    @staticmethod
    def _parse_bbox(raw: Any) -> BBox | None:
        if isinstance(raw, BBox):
            return raw
        if not isinstance(raw, dict):
            return None
        try:
            if "x1" in raw:
                return BBox(
                    x1=float(raw["x1"]),
                    y1=float(raw["y1"]),
                    x2=float(raw["x2"]),
                    y2=float(raw["y2"]),
                )
            if "x" in raw and "w" in raw:
                x = float(raw["x"])
                y = float(raw["y"])
                w = float(raw["w"])
                h = float(raw["h"])
                return BBox(
                    x1=max(0.0, x),
                    y1=max(0.0, y),
                    x2=min(1.0, x + w),
                    y2=min(1.0, y + h),
                )
        except (TypeError, ValueError):
            return None
        return None


__all__ = ["ToolResultFilter"]
