"""L1.5 sensor output protocol — V1.

Sprint 0 Schema V1. Defines the cross-process contract between **any upstream
CV/sensor source** and the DSG Ingest filter layer.

Layer map (see `.cursor/memory/architecture/sprint0_preflight.md §1.3` and
`module_map_p2.md §10.1`):

    L0 Raw Event Stream   ─────────┐
    L1 Blackboard                   ├── shared/event_log.py (DONE, S0.A)
    L1.5 Sensor Output   ←── THIS FILE
       │  Producers (pluggable, any subset):
       │    - Unity ARCameraSubsystem (camera pose, ARTracking state)
       │    - A10 CV pipeline (SAM2 + DINOv2 + YOLO, P3+)
       │    - Laptop-side Sentinel (YOLO-World, P4)
       │    - Gemini vision-proxy (oral → text extraction, always available)
       │  Consumers:
       │    - DSG Ingest filters (dsg/ingest/*.py)
       │    - Brain vision helpers (identify_object L0-L2)
    L2-B / L3 (unchanged by source — only Ingest filter set varies)

Design constraints:
  - V1 locks the **shape**; no concrete producer is required in Sprint 0.
  - Keeps image bytes out of this envelope — pass a `frame_ref` instead
    (SnapshotEnvelope uuid or file path). Image-handling stays in
    `shared/snapshot.py`.
  - `DsgMode` (shared/tiers.py) decides which producers are allowed to emit
    SensorFrames and which filters consume them; this file does not enforce.
"""

from __future__ import annotations

import time
import uuid as uuid_lib
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from parrot.shared.snapshot import BBox


class FrameSource(str, Enum):
    """Who produced this sensor frame.

    `UNITY_AR_TELEMETRY` is pose-only (no detections); the rest carry
    `detections` plus optional `frame_ref` to a SnapshotEnvelope.
    """

    UNITY_AR_TELEMETRY = "unity_ar_telemetry"
    UNITY_WEBCAM_TELEMETRY = "unity_webcam_telemetry"
    A10_SAM2_DINOV2 = "a10_sam2_dinov2"
    A10_YOLO_WORLD = "a10_yolo_world"
    SENTINEL_YOLO = "sentinel_yolo"
    GEMINI_VISION_PROXY = "gemini_vision_proxy"
    MOCK = "mock"


class DetectionAuthority(str, Enum):
    """Authority tier for a single detection (ADR-026 chain).

    Higher wins when the same object gets multiple detections in one frame.
    Values are ordinal (`priority()` returns the numeric rank).
    """

    USER = "user"
    GEMINI_DESCRIBED = "gemini_described"
    REID_CONFIRMED = "reid_confirmed"
    YOLO_VOTED = "yolo_voted"
    YOLO_SINGLE = "yolo_single"
    UNKNOWN = "unknown"

    def priority(self) -> int:
        return {
            DetectionAuthority.USER: 100,
            DetectionAuthority.GEMINI_DESCRIBED: 80,
            DetectionAuthority.REID_CONFIRMED: 60,
            DetectionAuthority.YOLO_VOTED: 40,
            DetectionAuthority.YOLO_SINGLE: 20,
            DetectionAuthority.UNKNOWN: 0,
        }[self]


class Detection(BaseModel):
    """One object detection inside a SensorFrame.

    `track_id` is the upstream tracker's internal id (persistent across
    frames in the same session); `reid_hash` is optional DINOv2 / similar
    embedding digest for cross-session ReID. Leave both empty if the
    producer has no tracker (e.g. zero-shot YOLO-World single-frame).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    det_id: str = Field(default_factory=lambda: uuid_lib.uuid4().hex[:12])
    label: str = Field(..., min_length=1, max_length=128)
    confidence: float = Field(..., ge=0.0, le=1.0)
    authority: DetectionAuthority = DetectionAuthority.UNKNOWN

    bbox: BBox | None = None
    track_id: str = ""
    reid_hash: str = ""

    meta: dict[str, Any] = Field(default_factory=dict)


class SensorFrame(BaseModel):
    """One L1.5 emission from a single source at a single instant.

    Multi-source fusion (if needed) happens **downstream** in the Ingest
    filter layer; this envelope is source-atomic.

    `frame_ref` holds either a SnapshotEnvelope uuid (in-memory handoff)
    or a file path on disk. Empty string = telemetry-only frame with no
    pixels attached (e.g. ARTracking state change).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    frame_uuid: str = Field(default_factory=lambda: uuid_lib.uuid4().hex[:16])
    ts: float = Field(default_factory=time.time, gt=0.0)
    source: FrameSource
    frame_ref: str = ""

    detections: tuple[Detection, ...] = ()

    ar_tracking_state: str = ""
    camera_pose_ref: str = ""

    provenance_parent: str | None = Field(default=None, max_length=64)
    meta: dict[str, Any] = Field(default_factory=dict)

    def has_detections(self) -> bool:
        return len(self.detections) > 0

    def top_detection(self) -> Detection | None:
        """Highest (authority, confidence) detection, or None if empty."""
        if not self.detections:
            return None
        return max(
            self.detections,
            key=lambda d: (d.authority.priority(), d.confidence),
        )


__all__ = [
    "Detection",
    "DetectionAuthority",
    "FrameSource",
    "SensorFrame",
]
