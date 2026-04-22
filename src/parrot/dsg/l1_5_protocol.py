"""L1.5 Perception Protocol — contract for any upstream detection source.

Sprint 0 S0.7: lock the schema of L1.5 detection messages so Sprint 2+
can wire up actual sources (A10 SAM2+DINOv2, Gemini Flash vision loop,
Sentinel lightweight CV) against a single interface. **No producer or
consumer is implemented here**; this module is a pure schema lock.

Why L1.5 exists (from `module_map_p2.md §10.1` and `ar_feature_vision.md §3.6`):

    L1   视网膜         raw frames from LiveKit Video Track
    L1.5 视觉皮层      detection list (pluggable: A10 / Gemini / Sentinel / CPU)   ← THIS MODULE
    L2-A 背侧 Where    spatial topology (P3)
    L2-B 腹侧 What     semantic working memory (implemented)
    L3   前额叶        narrative observer (P3+)

L2-B / L3 are stable; the L1.5 source is **swappable**. Any new detection
source must serialize its output as `L15DetectionFrame` so Ingest filters
(`dsg/ingest/cv_track_filter.py`, Sprint 2) can accept it uniformly.

Pydantic v2 rationale: same as `shared/event_log.py` — cross-process
protocol, field validation, and alignment with Graphiti custom entity
types. See `sprint0_preflight.md §10.1` for why SemanticNode stays
dataclass while persistent/protocol types migrate to Pydantic.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DetectionSource(str, Enum):
    """Which upstream produced this detection frame.

    Used by Ingest filters to decide trust level (CONFIRMED vs TENTATIVE)
    and to pick the right filter chain. Do NOT overload this with arbitrary
    strings; add a new enum member in a commit dedicated to that source.
    """

    A10_SAM2_DINO = "a10_sam2_dino"
    GEMINI_FLASH = "gemini_flash"
    SENTINEL_CPU = "sentinel_cpu"
    MANUAL = "manual"


class L15Detection(BaseModel):
    """A single detected object / region in a frame.

    Sprint 0 locks only the fields every upstream is guaranteed to provide.
    Source-specific extras (e.g. DINO embedding, Gemini caption) go into
    `extra` as an open dict; promote fields to top-level only after two or
    more sources agree on a shared meaning (avoid premature schema lock
    per sprint0_preflight.md §6).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    label: str = Field(..., min_length=1, max_length=128)
    confidence: float = Field(..., ge=0.0, le=1.0)
    # bbox in normalized image coords [x, y, w, h] with origin at top-left.
    # Kept as list (not tuple) for pydantic JSON round-trip friendliness.
    bbox_normalized: list[float] = Field(default_factory=list, min_length=0, max_length=4)
    # Optional pointer to a source-specific embedding store (e.g. FAISS id,
    # Graphiti UUID). Empty string = not available.
    embedding_ref: str = Field(default="", max_length=64)
    # Source-specific extras; any upstream may populate freely. Consumers
    # MUST tolerate absence of any field inside `extra`.
    extra: dict[str, Any] = Field(default_factory=dict)


class L15DetectionFrame(BaseModel):
    """A single detection batch for one source frame.

    Multiple upstreams may produce frames at different rates; consumers
    (Ingest filters) deduplicate by `frame_id` + `source`.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    source: DetectionSource
    frame_id: str = Field(..., min_length=1, max_length=64)
    # Unix epoch seconds at capture time (NOT at detection time — that
    # should go into `extra` if needed, to preserve wall-clock alignment
    # with LiveKit video timestamps).
    capture_ts: float = Field(..., gt=0.0)
    detections: list[L15Detection] = Field(default_factory=list)
    # Optional link to the L0 event that requested this detection (e.g.
    # identify_object dispatched a burst capture). Empty = upstream-driven.
    provenance_parent: str = Field(default="", max_length=64)


__all__ = [
    "DetectionSource",
    "L15Detection",
    "L15DetectionFrame",
]
