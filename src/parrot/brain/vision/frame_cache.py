"""Storage-backed frame cache for time-aligned visual evidence.

The cache is the first real producer for ``EvidenceKind.VIDEO_FRAME``.  LiveKit
or SVA frame workers should call ``record_livekit_frame_bytes`` after they have
an encoded JPEG/PNG/WebP frame.  This module deliberately does not subscribe to
LiveKit by itself; it keeps the storage and ledger contract small and reusable.
"""

from __future__ import annotations

import base64
import binascii
import os
import time
import uuid as uuid_lib
from collections import deque
from pathlib import Path
from threading import RLock
from typing import Any

from parrot.brain.vision.evidence import (
    ClockDomain,
    EvidenceKind,
    EvidenceStatus,
    TimeAlignedSampleRef,
    TimebaseStamp,
    get_evidence_ledger,
)


_MIME_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


class LiveKitFrameCache:
    """Bounded metadata index plus storage writer for encoded video frames."""

    def __init__(
        self,
        *,
        root: Path | str | None = None,
        max_frames: int | None = None,
        max_bytes: int | None = None,
    ) -> None:
        self.root = Path(root) if root is not None else _default_root()
        self.max_frames = max(1, int(max_frames or _env_int("PARROT_FRAME_CACHE_MAX_FRAMES", 120)))
        self.max_bytes = max(1024, int(max_bytes or _env_int("PARROT_FRAME_CACHE_MAX_BYTES", 2_500_000)))
        self._frames: deque[TimeAlignedSampleRef] = deque()
        self._lock = RLock()

    def reset_for_tests(self, *, root: Path | str | None = None) -> None:
        with self._lock:
            if root is not None:
                self.root = Path(root)
            self._frames.clear()

    def status(self) -> dict[str, Any]:
        with self._lock:
            frames = list(self._frames)
        latest = frames[-1].as_json() if frames else None
        return {
            "root": str(self.root),
            "max_frames": self.max_frames,
            "max_bytes": self.max_bytes,
            "frame_count": len(frames),
            "latest_frame": latest,
            "schema": "LiveKitFrameCache.web_backend_v1",
        }

    def record_base64_frame(
        self,
        image_base64: str,
        *,
        mime_type: str = "image/jpeg",
        **kwargs: Any,
    ) -> TimeAlignedSampleRef:
        return self.record_encoded_frame(
            _decode_base64_image(image_base64),
            mime_type=mime_type,
            **kwargs,
        )

    def record_encoded_frame(
        self,
        frame_bytes: bytes,
        *,
        mime_type: str = "image/jpeg",
        room_id: str = "",
        track_sid: str = "",
        participant_id: str = "",
        source_id: str = "",
        wall_time_ms: int = 0,
        monotonic_ms: int = 0,
        media_time_us: int = 0,
        sequence: int = 0,
        description: str = "",
        meta: dict[str, Any] | None = None,
    ) -> TimeAlignedSampleRef:
        """Persist an encoded frame and mirror it to the evidence ledger.

        Callers pass already encoded image bytes because this layer should not
        depend on OpenCV/Pillow or a particular LiveKit frame representation.
        Future SVA processors can do the raw-frame conversion at their boundary.
        """
        mime = _clean_mime(mime_type)
        _validate_frame_bytes(frame_bytes, max_bytes=self.max_bytes)
        now_ms = int(time.time() * 1000)
        stamp = TimebaseStamp(
            clock_domain=ClockDomain.LIVEKIT_TRACK,
            wall_time_ms=int(wall_time_ms or now_ms),
            monotonic_ms=int(monotonic_ms or time.monotonic() * 1000),
            media_time_us=int(media_time_us or 0),
            sequence=int(sequence or 0),
            estimated=wall_time_ms <= 0,
            source_id=str(source_id or track_sid or participant_id or "livekit_track"),
        )
        asset_path = self._write_frame(
            frame_bytes,
            mime_type=mime,
            timebase=stamp,
            source_id=stamp.source_id,
        )
        sample = get_evidence_ledger().record_sample(
            kind=EvidenceKind.VIDEO_FRAME,
            status=EvidenceStatus.READY,
            timebase=stamp,
            asset_path=str(asset_path),
            mime_type=mime,
            room_id=str(room_id or ""),
            track_sid=str(track_sid or ""),
            description=description or "LiveKit/SVA cached video frame",
            meta={
                "source": "livekit_frame_cache",
                "participant_id": str(participant_id or ""),
                "byte_size": len(frame_bytes),
                **dict(meta or {}),
            },
        )
        with self._lock:
            self._frames.append(sample)
            self._prune_unlocked()
        return sample

    def _write_frame(
        self,
        frame_bytes: bytes,
        *,
        mime_type: str,
        timebase: TimebaseStamp,
        source_id: str,
    ) -> Path:
        safe_source = _safe_segment(source_id or "track")
        day = time.strftime("%Y-%m-%d", time.gmtime(timebase.wall_time_ms / 1000))
        directory = self.root / day / safe_source
        directory.mkdir(parents=True, exist_ok=True)
        suffix = _MIME_EXTENSIONS[mime_type]
        name = (
            f"frame_{timebase.wall_time_ms}_{timebase.sequence:06d}_"
            f"{uuid_lib.uuid4().hex[:8]}{suffix}"
        )
        path = directory / name
        path.write_bytes(frame_bytes)
        return path

    def _prune_unlocked(self) -> None:
        while len(self._frames) > self.max_frames:
            old = self._frames.popleft()
            if not old.asset_path:
                continue
            try:
                Path(old.asset_path).unlink()
            except OSError:
                # If another process is reading the frame, leave it for a
                # later cache pass rather than blocking visual evidence.
                pass


def record_livekit_frame_bytes(
    frame_bytes: bytes,
    *,
    mime_type: str = "image/jpeg",
    room_id: str = "",
    track_sid: str = "",
    participant_id: str = "",
    source_id: str = "",
    wall_time_ms: int = 0,
    monotonic_ms: int = 0,
    media_time_us: int = 0,
    sequence: int = 0,
    description: str = "",
    meta: dict[str, Any] | None = None,
) -> TimeAlignedSampleRef:
    """Producer entry point for LiveKit/SVA encoded frame bytes."""
    return get_frame_cache().record_encoded_frame(
        frame_bytes,
        mime_type=mime_type,
        room_id=room_id,
        track_sid=track_sid,
        participant_id=participant_id,
        source_id=source_id,
        wall_time_ms=wall_time_ms,
        monotonic_ms=monotonic_ms,
        media_time_us=media_time_us,
        sequence=sequence,
        description=description,
        meta=meta,
    )


def _default_root() -> Path:
    return Path(os.getenv("PARROT_FRAME_CACHE_ROOT", "data/vision/frame_cache"))


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _clean_mime(mime_type: str) -> str:
    mime = str(mime_type or "image/jpeg").split(";", 1)[0].strip().lower()
    if mime not in _MIME_EXTENSIONS:
        raise ValueError(f"unsupported_frame_mime:{mime}")
    return mime


def _validate_frame_bytes(frame_bytes: bytes, *, max_bytes: int) -> None:
    if not isinstance(frame_bytes, (bytes, bytearray)):
        raise TypeError("frame_bytes_must_be_bytes")
    if not frame_bytes:
        raise ValueError("empty_frame_bytes")
    if len(frame_bytes) > max_bytes:
        raise ValueError("frame_bytes_too_large")


def _decode_base64_image(image_base64: str) -> bytes:
    text = str(image_base64 or "").strip()
    if "," in text and text.lower().startswith("data:image/"):
        text = text.split(",", 1)[1]
    try:
        return base64.b64decode(text, validate=True)
    except binascii.Error as exc:
        raise ValueError("invalid_image_base64") from exc


def _safe_segment(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value)
    return cleaned[:80] or "track"


_FRAME_CACHE = LiveKitFrameCache()


def get_frame_cache() -> LiveKitFrameCache:
    return _FRAME_CACHE


def reset_frame_cache_for_tests(*, root: Path | str | None = None) -> None:
    _FRAME_CACHE.reset_for_tests(root=root)


__all__ = [
    "LiveKitFrameCache",
    "get_frame_cache",
    "record_livekit_frame_bytes",
    "reset_frame_cache_for_tests",
]
