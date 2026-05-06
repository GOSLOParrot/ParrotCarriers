"""DSG Ingest filter subpackage.

Sprint 0 Schema V1 ships only the base protocol (`base.py`). Concrete
filters land in Sprint 2:

    text_source_filter.py        — Gemini oral + user messages (ratified)
    tool_result_filter.py        — identify_object hits (ratified)
    user_tag_filter.py           — Obsidian double-link sync (ratified)
    cv_track_filter.py           — A10 detections (tentative, P3+)
    transcript_extractor         — pipeline-agnostic LLM transcript bridge,
                                   feeds text_source_filter (Sprint 4 Phase 5+
                                   Line B rename of gemini_transcript_extractor;
                                   old module kept as alias shim)

See `ar_feature_vision.md §3.6` for why this layer exists and how
`DsgMode` activates different subsets.
"""

from parrot.dsg.ingest.base import (
    IngestFilter,
    IngestOutcome,
    Observation,
    ObservationSource,
)
from parrot.dsg.ingest.cv_track_filter import CvTrackFilter
from parrot.dsg.ingest.text_source_filter import TextSourceFilter
from parrot.dsg.ingest.tool_result_filter import ToolResultFilter
from parrot.dsg.ingest.user_tag_filter import UserTagFilter

__all__ = [
    "CvTrackFilter",
    "IngestFilter",
    "IngestOutcome",
    "Observation",
    "ObservationSource",
    "TextSourceFilter",
    "ToolResultFilter",
    "UserTagFilter",
]
