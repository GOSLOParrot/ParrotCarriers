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

    Ordered roughly by default authority (USER > IDENTIFY_OBJECT >
    GOSLO_AUTONOMOUS > CV_* > GEMINI_ORAL). Actual TENTATIVE / CONFIRMED
    mapping is filter-specific; see `Observation.confirmation`.

    Additive history (do not change existing values — Phase 4 § 8 + LineB
    § 1.3 lock both rely on the seven baseline strings):
        Phase 4 W3 (2026-04): seven baseline entries below.
        DSG-POOL-V1 (2026-05-06): + ``GOSLO_AUTONOMOUS`` for self-initiated
        curiosity (master § 3.3, brain_protocol_plan_v1 § 3 PlanProposal
        path). Pure addition; no value rename, no value re-order.
        Web Runtime upgrade (2026-05-13): + ``GOOGLE_MESSAGE`` for Gmail /
        Google Workspace message notifications, keeping message triggers on
        the same Observation -> L1.5 -> Ingest path as Calendar/Obsidian.
    """

    USER_TAG_OBSIDIAN = "user_tag_obsidian"
    USER_EXPLICIT = "user_explicit"
    IDENTIFY_OBJECT = "identify_object"
    GEMINI_ORAL = "gemini_oral"
    CV_A10 = "cv_a10"
    CV_SENTINEL = "cv_sentinel"
    MOCK = "mock"
    GOSLO_AUTONOMOUS = "goslo_autonomous"
    GOOGLE_CALENDAR = "google_calendar"
    GOOGLE_MESSAGE = "google_message"


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


def _copy_obsidian_source_meta(obs: Observation) -> dict[str, Any]:
    """Keep Obsidian-specific note metadata on the L2-B node.

    Ref-profile notes use Obsidian UUID as a binding lookup key. Daily and
    roleplay setting notes may not have a UUID, so their path/note key remains
    operational provenance for status views, ref-health checks, and future
    vault reconciliation. These fields are deliberately copied into
    ``source_meta`` rather than becoming new top-level node fields.
    """
    keys = (
        "profile",
        "obsidian_path",
        "obsidian_note_key",
        "file_mtime",
        "double_link_count",
        "tags",
    )
    return {key: obs.meta[key] for key in keys if key in obs.meta}


def _copy_google_calendar_source_meta(obs: Observation) -> dict[str, Any]:
    """Keep Google Calendar identity/version data on the L2-B event node.

    Calendar events are lightweight facts in L2-B. The heavy or editable
    draft state belongs in IntentWorkspace later; here we only store the
    stable API identity, time range, and version tokens needed for refresh
    and write-back.
    """
    keys = (
        "calendar_id",
        "calendar_event_id",
        "ical_uid",
        "etag",
        "html_link",
        "status",
        "start_time",
        "end_time",
        "timezone",
        "location",
        "updated",
        "objects",
        "is_urgent",
        # WEB-014.15: Google incremental sync can report cancelled/deleted
        # events. Preserve the lifecycle marker in source_meta so Web and
        # future reconciliation jobs can distinguish a live event from a
        # historical tombstone without adding a new shared DTO field.
        "calendar_lifecycle",
        "is_tombstone",
        "tombstone_policy",
    )
    return {key: obs.meta[key] for key in keys if key in obs.meta}


def _copy_google_message_source_meta(obs: Observation) -> dict[str, Any]:
    """Keep Gmail/Workspace message identity on the L2-B event node.

    This stores only redacted operational metadata. Full mailbox payloads,
    OAuth tokens, and message bodies stay with the Nanobot/Google connector
    side and must not leak into Web Console snapshots.
    """
    keys = (
        "message_id",
        "thread_id",
        "sender",
        "subject",
        "snippet",
        "timestamp",
        "is_reply",
        "importance",
        "source",
    )
    return {key: obs.meta[key] for key in keys if key in obs.meta}


def _copy_user_explicit_source_meta(obs: Observation) -> dict[str, Any]:
    """Keep selected Web/operator provenance on manually admitted Nodes.

    ``USER_EXPLICIT`` is broad, so this does not copy arbitrary operator JSON
    wholesale. The first Graphiti-to-L2-B export path uses this to preserve
    partition, fact text, source URL/description, and Graphiti endpoint UUIDs
    while still avoiding a new shared ObservationSource before CORE-008 review.
    """
    keys = (
        "source_tool",
        "target_node_uuid",
        "audit_note",
        "graphiti_partition",
        "graphiti_hit_uuid",
        "graphiti_source_node_uuid",
        "graphiti_target_node_uuid",
        "graphiti_score",
        "source_url",
        "source_description",
        "fact_text",
    )
    return {key: obs.meta[key] for key in keys if key in obs.meta}


try:
    from parrot.dsg.l2b_types import register_source_meta_factory

    register_source_meta_factory(
        ObservationSource.USER_EXPLICIT.value,
        _copy_user_explicit_source_meta,
    )
    register_source_meta_factory(
        ObservationSource.USER_TAG_OBSIDIAN.value,
        _copy_obsidian_source_meta,
    )
    register_source_meta_factory(
        ObservationSource.GOOGLE_CALENDAR.value,
        _copy_google_calendar_source_meta,
    )
    register_source_meta_factory(
        ObservationSource.GOOGLE_MESSAGE.value,
        _copy_google_message_source_meta,
    )
except Exception:
    # Import-time factory registration is best-effort. If a test imports this
    # module while l2b_types is being monkey-patched, SemanticNode will still
    # fall back to an empty source_meta dict instead of failing ingestion.
    pass


__all__ = [
    "IngestFilter",
    "IngestOutcome",
    "Observation",
    "ObservationSource",
]
