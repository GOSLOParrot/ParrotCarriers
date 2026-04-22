"""Snapshot (single-frame capture) envelope schema — V1.

Sprint 0 Schema V1. Used by three flows:
  1. `captureSnapshot` RPC (Unity → Brain), see audit §5.1 B1-B2
  2. Brain `capture_current_frame()` helper (`brain/vision/snapshot.py`, Sprint 4)
  3. `PhotoEvent` / identify_object pipeline (Sprint 4 S4.A + audit §5)

Design notes:
  - Envelope is payload-agnostic: `payload_kind` discriminates between inline
    base64, file-path reference, and URI. This lets us start inline (≤120 KB
    LiveKit RPC limit) and migrate to disk / OSS without protocol change.
  - `request_id` is used so concurrent callers (identify_object, camera mode)
    can correlate RPC request ↔ response.
  - `camera_pose` is optional because DESKTOP_WEBCAM has no pose; only AR
    path fills it.
  - File-layout convention per audit §5.1 B3:
        data/snapshots/objects/{uuid}/reference.jpg
        data/snapshots/sightings/{yyyy-mm-dd}/{ts}.jpg
        data/photos/{yyyy-mm-dd}/{ts}.jpg
    These paths are produced by consumers, not required inside the envelope.

Extension points (intentionally left open in V1):
  - `exif`: loose dict for camera exposure / focus / lens etc.
  - `meta`: free-form app-level tags (scene, mode, user flags).
"""

from __future__ import annotations

import time
import uuid as uuid_lib
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SnapshotSource(str, Enum):
    """Where the snapshot came from."""

    UNITY_AR = "unity_ar"
    UNITY_WEBCAM = "unity_webcam"
    GEMINI_VISION_PROXY = "gemini_vision_proxy"
    MOCK = "mock"


class SnapshotPayloadKind(str, Enum):
    """How the image bytes are delivered with this envelope."""

    INLINE_JPEG_B64 = "inline_jpeg_b64"
    FILE_PATH = "file_path"
    URI = "uri"
    NONE = "none"


class BBox(BaseModel):
    """Normalized axis-aligned bounding box (x1, y1, x2, y2), all in [0, 1].

    Coordinate convention: origin at top-left, x right, y down — matches
    image pixel coords after normalization. Flip upstream if your source
    uses bottom-left origin.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    x1: float = Field(..., ge=0.0, le=1.0)
    y1: float = Field(..., ge=0.0, le=1.0)
    x2: float = Field(..., ge=0.0, le=1.0)
    y2: float = Field(..., ge=0.0, le=1.0)

    def width(self) -> float:
        return max(0.0, self.x2 - self.x1)

    def height(self) -> float:
        return max(0.0, self.y2 - self.y1)

    def area(self) -> float:
        return self.width() * self.height()


class CameraPose(BaseModel):
    """World-space camera pose at the instant of capture.

    Optional for DESKTOP_WEBCAM. Required for AR path to anchor PhotoEvent.
    Right-handed, Unity-style (y-up) coordinates.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    px: float = 0.0
    py: float = 0.0
    pz: float = 0.0
    qx: float = 0.0
    qy: float = 0.0
    qz: float = 0.0
    qw: float = 1.0


class SnapshotEnvelope(BaseModel):
    """One captured frame plus metadata.

    Lifecycle:
        Unity SnapshotService.cs → LiveKit RPC response
            → Brain capture_current_frame()
            → consumer (identify_object L0/L1 compare, PhotoEvent storage,
              DSG Ingest cv_track_filter)
        → SemanticNode.reference_image_path / last_sighting_path (L2-B)
        → L0 EventEnvelope.payload (audit trail) via provenance_stream_id

    Size budget:
        - INLINE_JPEG_B64 payload ≤ ~120 KB (LiveKit PerformRpc safe limit)
        - Falls back to FILE_PATH / URI when exceeded; producer decides.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    snapshot_uuid: str = Field(default_factory=lambda: uuid_lib.uuid4().hex[:16])
    request_id: str = Field(default_factory=lambda: uuid_lib.uuid4().hex[:8])
    ts: float = Field(default_factory=time.time, gt=0.0)

    source: SnapshotSource = SnapshotSource.UNITY_WEBCAM
    width: int = Field(..., gt=0, le=8192)
    height: int = Field(..., gt=0, le=8192)
    format: str = Field(default="jpeg", pattern=r"^(jpeg|png|raw)$")

    payload_kind: SnapshotPayloadKind = SnapshotPayloadKind.NONE
    payload_inline_b64: str = ""
    payload_path: str = ""
    payload_uri: str = ""

    camera_pose: CameraPose | None = None
    exif: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)

    def has_payload(self) -> bool:
        return self.payload_kind != SnapshotPayloadKind.NONE

    def size_hint_bytes(self) -> int:
        """Best-effort size estimate for the carried payload (0 if unknown)."""
        if self.payload_kind == SnapshotPayloadKind.INLINE_JPEG_B64:
            return int(len(self.payload_inline_b64) * 0.75)
        return 0


__all__ = [
    "BBox",
    "CameraPose",
    "SnapshotEnvelope",
    "SnapshotPayloadKind",
    "SnapshotSource",
]
