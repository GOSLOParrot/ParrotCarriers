"""DSG Ingest filter subpackage.

Sprint 0 Schema V1 ships only the base protocol (`base.py`). Concrete
filters land in Sprint 2:

    text_source_filter.py        — Gemini oral + user messages (ratified)
    tool_result_filter.py        — identify_object hits (ratified)
    user_tag_filter.py           — Obsidian double-link sync (ratified)
    cv_track_filter.py           — A10 detections (tentative, P3+)
    gemini_transcript_extractor  — NP + locative preposition extractor,
                                   feeds text_source_filter

See `ar_feature_vision.md §3.6` for why this layer exists and how
`DsgMode` activates different subsets.
"""

from parrot.dsg.ingest.base import (
    IngestFilter,
    IngestOutcome,
    Observation,
    ObservationSource,
)

__all__ = [
    "IngestFilter",
    "IngestOutcome",
    "Observation",
    "ObservationSource",
]
