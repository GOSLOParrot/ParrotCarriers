"""Snapshot (single-frame capture) envelope schema V1.

This is a legacy-compatible metadata envelope for saved/observed still frames.
Formal Unity must not transport full images or inline base64 through LiveKit
RPC. The accepted App path is:

1. Unity ``PhotoController`` emits compact ECP metadata
   (``photo.taken_preview`` / capture time / pose / refs).
2. Full photo bytes are uploaded via HTTP/storage and referenced by path/URI.
3. Brain/DSG consumers attach the reference to sightings or memory nodes.

Design notes:
- ``payload_kind`` remains payload-agnostic for older tests and storage-backed
  consumers. Prefer FILE_PATH / URI / NONE for formal App code.
- ``request_id`` can correlate a user camera action, ECP event, HTTP upload,
  and downstream sighting result.
- ``camera_pose`` is optional because DESKTOP_WEBCAM has no pose; only AR path
  fills it.
- File-layout convention:
      data/snapshots/objects/{uuid}/reference.jpg
      data/snapshots/sightings/{yyyy-mm-dd}/{ts}.jpg
      data/photos/{yyyy-mm-dd}/{ts}.jpg
  These paths are produced by consumers, not required inside the envelope.

Extension points:
- ``exif``: loose dict for camera exposure / focus / lens etc.
- ``meta``: free-form app-level tags (scene, mode, user flags).
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
    """How image bytes are referenced by this envelope."""

    INLINE_JPEG_B64 = "inline_jpeg_b64"
    FILE_PATH = "file_path"
    URI = "uri"
    NONE = "none"


class BBox(BaseModel):
    """Normalized axis-aligned bounding box (x1, y1, x2, y2), all in [0, 1]."""

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
    """World-space camera pose at the instant of capture."""

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
        Unity PhotoController / storage-backed capture
            -> Brain/DSG consumer (identify_object evidence, PhotoEvent
              storage, DSG Ingest cv_track_filter)
        -> SemanticNode.reference_image_path / last_sighting_path (L2-B)
        -> L0 EventEnvelope.payload (audit trail) via provenance_stream_id

    Size budget:
        - Formal App code should use FILE_PATH / URI for image bytes.
        - INLINE_JPEG_B64 exists only for legacy tests/tools and must not be
          sent through LiveKit RPC.
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
