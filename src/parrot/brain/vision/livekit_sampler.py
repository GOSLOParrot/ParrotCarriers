"""LiveKit video-track sampler for time-aligned evidence.

This module is the automatic producer that sits above ``frame_cache``.  It
subscribes to remote LiveKit video tracks, samples frames at a bounded rate, and
stores encoded JPEG evidence through ``record_livekit_frame_bytes``.  It does
not depend on Gemini's ``video_input=True`` path because Gemini's internal video
frames are not observable or auditable.
"""

from __future__ import annotations

import asyncio
import contextlib
import io
import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncIterable, Callable

from parrot.brain.vision.evidence import TimeAlignedSampleRef
from parrot.brain.vision.frame_cache import record_livekit_frame_bytes

logger = logging.getLogger(__name__)


FrameStreamFactory = Callable[[Any, int], AsyncIterable[Any]]


@dataclass(slots=True)
class LiveKitFrameSamplerConfig:
    """Runtime policy for room-scoped frame sampling.

    The defaults are intentionally conservative.  A single low-FPS sampler is
    enough to give ``identify_object`` a recent auditable frame without turning
    the Brain process into a high-throughput CV worker.
    """

    enabled: bool = True
    fps: float = 0.5
    jpeg_quality: int = 78
    max_dimension: int = 720
    stream_capacity: int = 1
    fresh_window_ms: int = 15_000
    include_screenshare: bool = True
    track_name_hints: tuple[str, ...] = ("ar-camera", "camera", "screen")

    @classmethod
    def from_env(cls) -> "LiveKitFrameSamplerConfig":
        return cls(
            enabled=_env_bool("PARROT_LIVEKIT_FRAME_SAMPLER_ENABLED", True),
            fps=max(0.0, _env_float("PARROT_LIVEKIT_FRAME_SAMPLER_FPS", 0.5)),
            jpeg_quality=max(25, min(95, _env_int("PARROT_LIVEKIT_FRAME_JPEG_QUALITY", 78))),
            max_dimension=max(64, _env_int("PARROT_LIVEKIT_FRAME_MAX_DIMENSION", 720)),
            stream_capacity=max(1, _env_int("PARROT_LIVEKIT_FRAME_STREAM_CAPACITY", 1)),
            fresh_window_ms=max(1000, _env_int("PARROT_LIVEKIT_FRAME_FRESH_WINDOW_MS", 15_000)),
            include_screenshare=_env_bool("PARROT_LIVEKIT_FRAME_INCLUDE_SCREENSHARE", True),
            track_name_hints=_env_csv(
                "PARROT_LIVEKIT_FRAME_TRACK_HINTS",
                ("ar-camera", "camera", "screen"),
            ),
        )

    @property
    def min_interval_s(self) -> float:
        if self.fps <= 0:
            return float("inf")
        return 1.0 / self.fps


class LiveKitFrameSampler:
    """Room-scoped sampler that records selected remote video frames."""

    def __init__(
        self,
        room: Any,
        *,
        config: LiveKitFrameSamplerConfig | None = None,
        stream_factory: FrameStreamFactory | None = None,
    ) -> None:
        self.room = room
        self.config = config or LiveKitFrameSamplerConfig.from_env()
        self.stream_factory = stream_factory or _default_frame_stream_factory
        self._tasks: dict[str, asyncio.Task[Any]] = {}
        self._last_record_monotonic: dict[str, float] = {}
        self._sequences: dict[str, int] = {}
        self._handlers: list[tuple[str, Callable[..., None]]] = []
        self._started = False
        self._stopped = False
        self._recorded_frames = 0
        self._error_count = 0
        self._last_error = ""
        self._last_frame: dict[str, Any] | None = None
        self._last_frame_by_track: dict[str, dict[str, Any]] = {}

    def start(self) -> None:
        if self._started or not self.config.enabled or self.config.fps <= 0:
            return
        self._started = True
        self._register_room_handlers()
        self._scan_existing_tracks()
        self._write_status("started")

    async def stop(self) -> None:
        self._stopped = True
        for event, handler in self._handlers:
            with contextlib.suppress(Exception):
                self.room.off(event, handler)
        self._handlers.clear()

        tasks = list(self._tasks.values())
        self._tasks.clear()
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self._write_status("stopped")

    def status(self, *, event: str = "status") -> dict[str, Any]:
        now_ms = int(time.time() * 1000)
        latest = _refresh_frame_summary(
            self._last_frame,
            now_ms=now_ms,
            fresh_window_ms=self.config.fresh_window_ms,
        )
        tracks = {
            track_sid: _refresh_frame_summary(
                summary,
                now_ms=now_ms,
                fresh_window_ms=self.config.fresh_window_ms,
            )
            for track_sid, summary in sorted(self._last_frame_by_track.items())
        }
        return {
            "enabled": self.config.enabled,
            "fps": self.config.fps,
            "active_tracks": sorted(self._tasks.keys()),
            "recorded_frames": self._recorded_frames,
            "fresh_window_ms": self.config.fresh_window_ms,
            "latest_frame": latest,
            "latest_frame_age_ms": latest.get("age_ms") if latest else None,
            "latest_frame_fresh": bool(latest and latest.get("fresh")),
            "tracks": tracks,
            "error_count": self._error_count,
            "last_error": self._last_error,
            "event": event,
            "room_id": str(getattr(self.room, "name", "") or ""),
            "updated_at_ms": int(time.time() * 1000),
            "schema": "LiveKitFrameSampler.web_backend_v1",
        }

    def _write_status(self, event: str) -> None:
        _write_sampler_status(self.status(event=event))

    def _register_room_handlers(self) -> None:
        def on_connected() -> None:
            self._scan_existing_tracks()

        def on_reconnected() -> None:
            self._scan_existing_tracks()

        def on_participant_connected(participant: Any) -> None:
            self._scan_participant(participant)

        def on_track_published(publication: Any, participant: Any) -> None:
            if self._publication_looks_video(publication):
                with contextlib.suppress(Exception):
                    publication.set_subscribed(True)
            track = getattr(publication, "track", None)
            if track is not None:
                self._maybe_start_track(track, publication, participant)

        def on_track_subscribed(track: Any, publication: Any, participant: Any) -> None:
            self._maybe_start_track(track, publication, participant)

        def on_track_unsubscribed(track: Any, publication: Any, participant: Any) -> None:
            self._stop_track(_track_sid(track, publication))

        def on_track_unpublished(publication: Any, participant: Any) -> None:
            self._stop_track(_track_sid(getattr(publication, "track", None), publication))

        for event, handler in (
            ("connected", on_connected),
            ("reconnected", on_reconnected),
            ("participant_connected", on_participant_connected),
            ("track_published", on_track_published),
            ("track_subscribed", on_track_subscribed),
            ("track_unsubscribed", on_track_unsubscribed),
            ("track_unpublished", on_track_unpublished),
        ):
            self.room.on(event, handler)
            self._handlers.append((event, handler))

    def _scan_existing_tracks(self) -> None:
        participants = getattr(self.room, "remote_participants", {}) or {}
        for participant in participants.values():
            self._scan_participant(participant)

    def _scan_participant(self, participant: Any) -> None:
        publications = getattr(participant, "track_publications", {}) or {}
        for publication in publications.values():
            if self._publication_looks_video(publication):
                with contextlib.suppress(Exception):
                    publication.set_subscribed(True)
            track = getattr(publication, "track", None)
            if track is not None:
                self._maybe_start_track(track, publication, participant)

    def _maybe_start_track(self, track: Any, publication: Any, participant: Any) -> None:
        if self._stopped or not self._should_sample(track, publication):
            return
        track_sid = _track_sid(track, publication)
        if not track_sid or track_sid in self._tasks:
            return
        task = asyncio.create_task(
            self._consume_track(track, publication, participant),
            name=f"parrot_livekit_frame_sampler:{track_sid}",
        )
        self._tasks[track_sid] = task

        def _done(done: asyncio.Task[Any]) -> None:
            self._tasks.pop(track_sid, None)
            if done.cancelled():
                return
            exc = done.exception()
            if exc is not None:
                self._error_count += 1
                self._last_error = f"{type(exc).__name__}: {str(exc)[:160]}"
                logger.warning("LiveKit frame sampler task failed for %s: %s", track_sid, exc)
                self._write_status("track_error")

        task.add_done_callback(_done)
        self._write_status("track_started")

    def _stop_track(self, track_sid: str) -> None:
        task = self._tasks.pop(track_sid, None)
        if task is not None:
            task.cancel()
            self._write_status("track_stopped")

    def _should_sample(self, track: Any, publication: Any) -> bool:
        if not _is_video_kind(getattr(track, "kind", None)) and not _is_video_kind(getattr(publication, "kind", None)):
            return False
        if bool(getattr(track, "muted", False)) or bool(getattr(publication, "muted", False)):
            return False

        source_name = _track_source_name(getattr(publication, "source", None)).lower()
        if "camera" in source_name:
            return True
        if self.config.include_screenshare and (
            "screenshare" in source_name
            or "screen_share" in source_name
            or ("screen" in source_name and "share" in source_name)
        ):
            return True

        name_blob = " ".join(
            str(value or "").lower()
            for value in (
                getattr(track, "name", ""),
                getattr(publication, "name", ""),
                getattr(publication, "sid", ""),
            )
        )
        return any(hint and hint.lower() in name_blob for hint in self.config.track_name_hints)

    def _publication_looks_video(self, publication: Any) -> bool:
        return _is_video_kind(getattr(publication, "kind", None)) or self._should_sample(
            getattr(publication, "track", None),
            publication,
        )

    async def _consume_track(self, track: Any, publication: Any, participant: Any) -> None:
        track_sid = _track_sid(track, publication)
        stream = self.stream_factory(track, self.config.stream_capacity)
        try:
            async for event in stream:
                if self._stopped:
                    break
                now = time.monotonic()
                if now - self._last_record_monotonic.get(track_sid, 0.0) < self.config.min_interval_s:
                    continue
                self._last_record_monotonic[track_sid] = now
                self._record_event_frame(
                    event,
                    track=track,
                    publication=publication,
                    participant=participant,
                    track_sid=track_sid,
                )
        finally:
            aclose = getattr(stream, "aclose", None)
            if callable(aclose):
                with contextlib.suppress(Exception):
                    await aclose()

    def _record_event_frame(
        self,
        event: Any,
        *,
        track: Any,
        publication: Any,
        participant: Any,
        track_sid: str,
    ) -> None:
        frame = getattr(event, "frame", None)
        if frame is None:
            return
        sequence = self._sequences.get(track_sid, 0) + 1
        self._sequences[track_sid] = sequence
        media_time_us = _safe_int(getattr(event, "timestamp_us", 0))
        encoded = encode_livekit_video_frame_to_jpeg(
            frame,
            quality=self.config.jpeg_quality,
            max_dimension=self.config.max_dimension,
        )
        sample = record_livekit_frame_bytes(
            encoded,
            mime_type="image/jpeg",
            room_id=str(getattr(self.room, "name", "") or ""),
            track_sid=track_sid,
            participant_id=str(getattr(participant, "identity", "") or ""),
            source_id=str(getattr(track, "name", "") or getattr(publication, "name", "") or track_sid),
            wall_time_ms=int(time.time() * 1000),
            monotonic_ms=int(time.monotonic() * 1000),
            media_time_us=media_time_us,
            sequence=sequence,
            description="LiveKit automatic sampler frame",
            meta={
                "source": "livekit_frame_sampler",
                "participant_sid": str(getattr(participant, "sid", "") or ""),
                "publication_sid": str(getattr(publication, "sid", "") or ""),
                "publication_source": _track_source_name(getattr(publication, "source", None)),
                "track_name": str(getattr(track, "name", "") or ""),
                "rotation": str(getattr(event, "rotation", "") or ""),
            },
        )
        summary = _sample_summary(
            sample,
            track_name=str(getattr(track, "name", "") or ""),
            participant_id=str(getattr(participant, "identity", "") or ""),
            publication_source=_track_source_name(getattr(publication, "source", None)),
        )
        self._last_frame = summary
        self._last_frame_by_track[track_sid] = summary
        self._recorded_frames += 1
        self._write_status("frame_recorded")


def attach_livekit_frame_sampler(
    room: Any,
    *,
    config: LiveKitFrameSamplerConfig | None = None,
) -> LiveKitFrameSampler | None:
    cfg = config or LiveKitFrameSamplerConfig.from_env()
    if not cfg.enabled or cfg.fps <= 0:
        return None
    sampler = LiveKitFrameSampler(room, config=cfg)
    sampler.start()
    return sampler


def read_livekit_frame_sampler_status() -> dict[str, Any]:
    """Read the latest Brain sampler status from disk for Web observability."""
    path = _sampler_status_path()
    if not path.is_file():
        return {
            "available": False,
            "message": "status_file_missing",
            "path": str(path),
            "schema": "LiveKitFrameSampler.web_backend_v1",
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "available": False,
            "message": f"status_file_invalid:{type(exc).__name__}",
            "path": str(path),
            "schema": "LiveKitFrameSampler.web_backend_v1",
        }
    if not isinstance(data, dict):
        return {
            "available": False,
            "message": "status_file_not_object",
            "path": str(path),
            "schema": "LiveKitFrameSampler.web_backend_v1",
        }
    data = dict(data)
    data.setdefault("available", True)
    data.setdefault("path", str(path))
    data["status_file_age_ms"] = _status_file_age_ms(data)
    data = _refresh_sampler_status_freshness(data)
    return data


def encode_livekit_video_frame_to_jpeg(
    frame: Any,
    *,
    quality: int = 78,
    max_dimension: int = 720,
) -> bytes:
    """Encode a LiveKit RGB frame to JPEG bytes for durable evidence storage."""
    from PIL import Image
    from livekit.rtc.video_frame import proto_video

    rgb_type = proto_video.VideoBufferType.RGB24
    if getattr(frame, "type", None) != rgb_type:
        frame = frame.convert(rgb_type)

    width = int(getattr(frame, "width"))
    height = int(getattr(frame, "height"))
    image = Image.frombytes("RGB", (width, height), bytes(frame.data))
    if max_dimension and max(width, height) > max_dimension:
        scale = max_dimension / float(max(width, height))
        resized = (max(1, int(width * scale)), max(1, int(height * scale)))
        resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.BICUBIC)
        image = image.resize(resized, resample)

    output = io.BytesIO()
    image.save(output, format="JPEG", quality=max(25, min(95, int(quality))))
    return output.getvalue()


def _default_frame_stream_factory(track: Any, capacity: int) -> AsyncIterable[Any]:
    from livekit import rtc
    from livekit.rtc.video_frame import proto_video

    return rtc.VideoStream.from_track(
        track=track,
        capacity=capacity,
        format=proto_video.VideoBufferType.RGB24,
    )


def _write_sampler_status(status: dict[str, Any]) -> None:
    path = _sampler_status_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(f"{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
        payload = dict(status)
        payload["available"] = True
        tmp.write_text(json.dumps(payload, ensure_ascii=True, sort_keys=True), encoding="utf-8")
        tmp.replace(path)
    except Exception:
        logger.debug("LiveKit frame sampler status write failed", exc_info=True)


def _sample_summary(
    sample: TimeAlignedSampleRef,
    *,
    track_name: str,
    participant_id: str,
    publication_source: str = "",
) -> dict[str, Any]:
    asset_exists = bool(sample.as_json().get("asset_exists"))
    return {
        "evidence_id": sample.evidence_id,
        "kind": str(sample.kind),
        "status": str(sample.status),
        "room_id": sample.room_id,
        "track_sid": sample.track_sid,
        "track_name": track_name,
        "publication_source": publication_source,
        "participant_id": participant_id,
        "source_id": sample.timebase.source_id,
        "wall_time_ms": sample.timebase.wall_time_ms,
        "monotonic_ms": sample.timebase.monotonic_ms,
        "media_time_us": sample.timebase.media_time_us,
        "sequence": sample.timebase.sequence,
        "asset_exists": asset_exists,
    }


def _refresh_frame_summary(
    summary: dict[str, Any] | None,
    *,
    now_ms: int,
    fresh_window_ms: int,
) -> dict[str, Any]:
    if not isinstance(summary, dict):
        return {}
    item = dict(summary)
    try:
        wall_time_ms = int(item.get("wall_time_ms") or 0)
    except (TypeError, ValueError):
        wall_time_ms = 0
    age_ms = max(0, now_ms - wall_time_ms) if wall_time_ms > 0 else None
    item["age_ms"] = age_ms
    item["fresh"] = (
        age_ms is not None
        and age_ms <= fresh_window_ms
        and bool(item.get("asset_exists"))
    )
    return item


def _refresh_sampler_status_freshness(data: dict[str, Any]) -> dict[str, Any]:
    now_ms = int(time.time() * 1000)
    fresh_window_ms = max(1000, _safe_int(data.get("fresh_window_ms")) or 15_000)
    latest = _refresh_frame_summary(
        data.get("latest_frame") if isinstance(data.get("latest_frame"), dict) else None,
        now_ms=now_ms,
        fresh_window_ms=fresh_window_ms,
    )
    raw_tracks = data.get("tracks") if isinstance(data.get("tracks"), dict) else {}
    data["latest_frame"] = latest or None
    data["latest_frame_age_ms"] = latest.get("age_ms") if latest else None
    data["latest_frame_fresh"] = bool(latest and latest.get("fresh"))
    data["tracks"] = {
        str(track_sid): _refresh_frame_summary(
            summary if isinstance(summary, dict) else {},
            now_ms=now_ms,
            fresh_window_ms=fresh_window_ms,
        )
        for track_sid, summary in raw_tracks.items()
    }
    return data


def _status_file_age_ms(data: dict[str, Any]) -> int | None:
    try:
        updated_at_ms = int(data.get("updated_at_ms") or 0)
    except (TypeError, ValueError):
        updated_at_ms = 0
    if updated_at_ms <= 0:
        return None
    return max(0, int(time.time() * 1000) - updated_at_ms)


def _sampler_status_path() -> Path:
    return Path(
        os.getenv(
            "PARROT_LIVEKIT_FRAME_SAMPLER_STATUS_PATH",
            "data/vision/livekit_sampler_status.json",
        )
    )


def _is_video_kind(kind: Any) -> bool:
    try:
        from livekit.rtc._proto import track_pb2

        return int(kind) == int(track_pb2.TrackKind.KIND_VIDEO)
    except Exception:
        return str(kind).lower().endswith("video") or "video" in str(kind).lower()


def _track_source_name(source: Any) -> str:
    try:
        from livekit.rtc._proto import track_pb2

        return track_pb2.TrackSource.Name(int(source))
    except Exception:
        return str(source or "")


def _track_sid(track: Any, publication: Any) -> str:
    return str(
        getattr(track, "sid", "")
        or getattr(publication, "sid", "")
        or getattr(track, "name", "")
        or "unknown_track"
    )


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def _env_csv(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    raw = os.getenv(name)
    if raw is None:
        return default
    items = tuple(item.strip().lower() for item in raw.split(",") if item.strip())
    return items or default


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


__all__ = [
    "LiveKitFrameSampler",
    "LiveKitFrameSamplerConfig",
    "attach_livekit_frame_sampler",
    "encode_livekit_video_frame_to_jpeg",
    "read_livekit_frame_sampler_status",
]
