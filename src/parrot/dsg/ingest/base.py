"""DSG Ingest filter base protocol — V1.

Sprint 0 Schema V1. The Ingest layer is the **only** gate through which
external observations can become L2-B SemanticNodes. Every upstream source
(Gemini oral, identify_object, user tag, A10 CV, Sentinel) goes through a
filter here; L2-B never accepts writes directly.

Architecture source: `ar_feature_vision.md §3.6` (Ingest filter layer) +
`audit_identify_object_no_screenshot_20260420.md §5.1 B4` (reference image
storage convention).

Key invariants codified in this file:
  1. An Observation carries its own provenance_stream_id (link back to L0).
  2. An Observation declares `confirmation` defaulting to TENTATIVE; only
     USER-sourced or high-authority tool-result filters may emit CONFIRMED.
  3. Filters are pure functions: consume a SensorFrame / free-form input,
     emit zero-or-more Observations. No Blackboard writes, no Graphiti
     writes. The L2-B graph update path (Sprint 2 S2.B) owns the commit.

Concrete filter implementations land in Sprint 2:
    text_source_filter       Gemini oral + user messages
    tool_result_filter       identify_object hits
    user_tag_filter          Obsidian double-link sync
    cv_track_filter          A10 SAM2 / DINOv2 tracks
"""

from __future__ import annotations

import time
import uuid as uuid_lib
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from parrot.dsg.l1_5_protocol import SensorFrame
from parrot.dsg.l2b_types import ConfirmationStatus, NodeKind
from parrot.shared.snapshot import BBox


class ObservationSource(str, Enum):
    """Ultimate origin of the observation.

    Ordered roughly by default authority (USER > IDENTIFY_OBJECT > GEMINI_ORAL
    > CV_*). Actual TENTATIVE / CONFIRMED mapping is filter-specific; see
    `Observation.confirmation`.
    """

    USER_TAG_OBSIDIAN = "user_tag_obsidian"
    USER_EXPLICIT = "user_explicit"
    IDENTIFY_OBJECT = "identify_object"
    GEMINI_ORAL = "gemini_oral"
    CV_A10 = "cv_a10"
    CV_SENTINEL = "cv_sentinel"
    MOCK = "mock"


class Observation(BaseModel):
    """Unified filter output, ready for the L2-B graph writer.

    Maps roughly 1:1 to a future SemanticNode create-or-update op. The Ingest
    → L2-B writer decides whether this Observation creates a new node or
    touches an existing one (by label / bbox / obsidian_uuid / graphiti_uuid).

    Fields in five groups:

      Identity / linkage
        obs_id, source, provenance_stream_id, obsidian_uuid, graphiti_uuid

      Semantic payload
        label, kind, description, confidence, confirmation

      Evidence (optional)
        snapshot_uuid, bbox, reference_image_path, last_sighting_path

      Time
        observed_at, time_span

      Extensible
        meta
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    obs_id: str = Field(default_factory=lambda: uuid_lib.uuid4().hex[:12])
    source: ObservationSource
    provenance_stream_id: str = ""
    obsidian_uuid: str = ""
    graphiti_uuid: str = ""

    label: str = Field(..., min_length=1, max_length=128)
    kind: NodeKind = NodeKind.OBJECT
    description: str = ""
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    confirmation: ConfirmationStatus = ConfirmationStatus.TENTATIVE

    snapshot_uuid: str = ""
    bbox: BBox | None = None
    reference_image_path: str = ""
    last_sighting_path: str = ""

    observed_at: float = Field(default_factory=time.time, gt=0.0)
    time_span: tuple[float, float | None] = (0.0, None)

    meta: dict[str, Any] = Field(default_factory=dict)


class IngestOutcome(BaseModel):
    """Diagnostic result of processing one input through a filter.

    Sprint 2 runners use this for logging and Observation-log emission;
    schema-layer just fixes the contract.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    filter_name: str
    accepted: int = 0
    rejected: int = 0
    reason: str = ""
    observations: tuple[Observation, ...] = ()


class IngestFilter(ABC):
    """Abstract base for all DSG Ingest filters.

    Concrete filters override `process_frame` (SensorFrame-based) and/or
    `process_text` (free-form text, for Gemini-oral / user-message paths).
    A filter that only handles one input type can leave the other as the
    default no-op.

    Contract:
      - Implementations MUST be pure wrt Blackboard / Graphiti / L2-B graph.
      - Implementations MUST populate `provenance_stream_id` on every
        Observation whose upstream carries one (SensorFrame.frame_uuid is
        not the stream id; the runner passes the stream id separately).
      - Implementations MAY emit zero Observations for a given input.
    """

    name: str = "abstract"

    @abstractmethod
    def process_frame(self, frame: SensorFrame) -> IngestOutcome:
        """Produce Observations from a SensorFrame."""

    def process_text(
        self,
        text: str,
        *,
        source: ObservationSource,
        provenance_stream_id: str = "",
        meta: dict[str, Any] | None = None,
    ) -> IngestOutcome:
        """Produce Observations from free-form text.

        Default no-op for filters that only consume SensorFrames. Override
        in filters that take speech / chat as upstream (e.g. Gemini oral
        transcript extractor).
        """
        del text, source, provenance_stream_id, meta
        return IngestOutcome(filter_name=self.name, accepted=0, rejected=0)


__all__ = [
    "IngestFilter",
    "IngestOutcome",
    "Observation",
    "ObservationSource",
]
