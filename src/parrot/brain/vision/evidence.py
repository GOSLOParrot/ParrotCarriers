"""Time-aligned visual evidence ledger for Brain/Web tooling.

This module is intentionally backend-first.  It gives ``identify_object``,
Focus/BBox attention, photo uploads, and future SVA/SAM2/DINOv2 workers one
place to register samples without changing Unity's top-level ECP DTOs.  V1
only reads optional ``payload["timebase"]`` / ``command.meta["timebase"]`` and
legacy timestamp keys such as ``ts_ms``.
"""

from __future__ import annotations

import time
import uuid as uuid_lib
from collections import deque
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from threading import RLock
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ClockDomain(str, Enum):
    """Producer clock namespace for a media or attention sample."""

    BRAIN = "brain"
    UNITY = "unity"
    WEB = "web"
    LIVEKIT_TRACK = "livekit_track"
    ASR = "asr"
    CV_WORKER = "cv_worker"


class EvidenceKind(str, Enum):
    """Kinds the temporal ledger can index."""

    VIDEO_FRAME = "video_frame"
    IMAGE_ASSET = "image_asset"
    BBOX_FOCUS = "bbox_focus"
    ASR_SEGMENT = "asr_segment"
    CV_DETECTION = "cv_detection"
    EVIDENCE_REQUEST = "evidence_request"


class EvidenceStatus(str, Enum):
    """Lifecycle of a sample or evidence request."""

    PENDING = "pending"
    READY = "ready"
    MISSING = "missing"
    ERROR = "error"


class TimebaseStamp(BaseModel):
    """Sample-time stamp, separate from ECP envelope creation time."""

    model_config = ConfigDict(frozen=True, extra="forbid", use_enum_values=True)

    clock_domain: ClockDomain = ClockDomain.BRAIN
    wall_time_ms: int = Field(default_factory=lambda: int(time.time() * 1000), ge=0)
    monotonic_ms: int = 0
    media_time_us: int = 0
    sequence: int = 0
    estimated: bool = False
    source_id: str = ""

    @classmethod
    def now(
        cls,
        *,
        clock_domain: ClockDomain = ClockDomain.BRAIN,
        source_id: str = "",
        estimated: bool = False,
    ) -> "TimebaseStamp":
        return cls(
            clock_domain=clock_domain,
            wall_time_ms=int(time.time() * 1000),
            monotonic_ms=int(time.monotonic() * 1000),
            estimated=estimated,
            source_id=source_id,
        )

    @classmethod
    def from_payload(
        cls,
        payload: dict[str, Any] | None,
        *,
        default_domain: ClockDomain = ClockDomain.BRAIN,
        default_source_id: str = "",
        envelope_created_at_ms: int = 0,
    ) -> "TimebaseStamp":
        """Build from explicit ``timebase`` or legacy timestamp fields.

        ``EcpEvent.created_at`` is envelope time.  When we fall back to it, the
        returned stamp is marked ``estimated=True`` so downstream code can tell
        it was not the real producer sample time.
        """
        body = payload or {}
        raw = body.get("timebase") if isinstance(body.get("timebase"), dict) else body
        raw_dict = raw if isinstance(raw, dict) else {}

        domain = _clock_domain(raw_dict.get("clock_domain"), default_domain)
        source_id = str(raw_dict.get("source_id") or default_source_id or "")

        wall_time_ms = _coerce_epoch_ms(raw_dict.get("wall_time_ms"))
        estimated = bool(raw_dict.get("estimated", False))
        if wall_time_ms <= 0:
            wall_time_ms = _legacy_wall_time_ms(raw_dict)
            estimated = True
        if wall_time_ms <= 0 and envelope_created_at_ms > 0:
            wall_time_ms = int(envelope_created_at_ms)
            estimated = True
        if wall_time_ms <= 0:
            wall_time_ms = int(time.time() * 1000)
            estimated = True

        return cls(
            clock_domain=domain,
            wall_time_ms=wall_time_ms,
            monotonic_ms=_coerce_int(raw_dict.get("monotonic_ms")),
            media_time_us=_coerce_int(raw_dict.get("media_time_us")),
            sequence=_coerce_int(raw_dict.get("sequence")),
            estimated=estimated,
            source_id=source_id,
        )

    @classmethod
    def from_command_meta(
        cls,
        meta: dict[str, Any] | None,
        *,
        default_domain: ClockDomain = ClockDomain.BRAIN,
        default_source_id: str = "",
        command_issued_at_s: float = 0.0,
    ) -> "TimebaseStamp":
        """Build from ``EcpCommand.meta`` without changing the command DTO.

        ``EcpCommand.issued_at`` is the command envelope time.  If a producer
        does not provide ``meta["timebase"]``, using ``issued_at`` is only an
        estimate of the media/sample time, so ``from_payload`` marks it
        ``estimated=True``.
        """
        return cls.from_payload(
            meta or {},
            default_domain=default_domain,
            default_source_id=default_source_id,
            envelope_created_at_ms=_coerce_epoch_ms(command_issued_at_s),
        )


class SampleRegion(BaseModel):
    """Optional image/video region attached to a sample."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0
    coordinate_space: str = "normalized"


class TimeAlignedSampleRef(BaseModel):
    """Storage-backed, time-aligned evidence pointer.

    Image bytes are not embedded here.  ``asset_path`` / ``asset_uri`` point to
    the HTTP/storage asset that the VLM or Web console may later dereference.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", use_enum_values=True)

    evidence_id: str = Field(default_factory=lambda: f"ev_{uuid_lib.uuid4().hex[:16]}")
    kind: EvidenceKind
    status: EvidenceStatus = EvidenceStatus.READY
    timebase: TimebaseStamp
    asset_path: str = ""
    asset_uri: str = ""
    mime_type: str = ""
    region: SampleRegion | None = None
    related_refs: tuple[str, ...] = ()
    bbox_refs: tuple[str, ...] = ()
    focus_refs: tuple[str, ...] = ()
    request_id: str = ""
    room_id: str = ""
    track_sid: str = ""
    description: str = ""
    quality_flags: tuple[str, ...] = ()
    meta: dict[str, Any] = Field(default_factory=dict)
    created_at_ms: int = Field(default_factory=lambda: int(time.time() * 1000))
    updated_at_ms: int = Field(default_factory=lambda: int(time.time() * 1000))

    @property
    def has_asset(self) -> bool:
        return bool(self.asset_path or self.asset_uri)

    def as_json(self) -> dict[str, Any]:
        data = self.model_dump(mode="json")
        data["asset_exists"] = _asset_exists(self.asset_path)
        return data


class TemporalEvidenceLedger:
    """Bounded in-process sample ledger used by Brain and the Web BFF."""

    def __init__(self, *, max_samples: int = 512) -> None:
        self._samples: deque[TimeAlignedSampleRef] = deque(maxlen=max_samples)
        self._by_id: dict[str, TimeAlignedSampleRef] = {}
        self._lock = RLock()

    def reset_for_tests(self) -> None:
        with self._lock:
            self._samples.clear()
            self._by_id.clear()

    def record(self, sample: TimeAlignedSampleRef) -> TimeAlignedSampleRef:
        with self._lock:
            self._samples.append(sample)
            self._by_id[sample.evidence_id] = sample
        return sample

    def record_sample(
        self,
        *,
        kind: EvidenceKind,
        timebase: TimebaseStamp | None = None,
        status: EvidenceStatus = EvidenceStatus.READY,
        asset_path: str = "",
        asset_uri: str = "",
        mime_type: str = "",
        region: SampleRegion | None = None,
        related_refs: tuple[str, ...] = (),
        bbox_refs: tuple[str, ...] = (),
        focus_refs: tuple[str, ...] = (),
        request_id: str = "",
        room_id: str = "",
        track_sid: str = "",
        description: str = "",
        quality_flags: tuple[str, ...] = (),
        meta: dict[str, Any] | None = None,
    ) -> TimeAlignedSampleRef:
        return self.record(
            TimeAlignedSampleRef(
                kind=kind,
                status=status,
                timebase=timebase or TimebaseStamp.now(),
                asset_path=asset_path,
                asset_uri=asset_uri,
                mime_type=mime_type,
                region=region,
                related_refs=tuple(related_refs),
                bbox_refs=tuple(bbox_refs),
                focus_refs=tuple(focus_refs),
                request_id=request_id,
                room_id=room_id,
                track_sid=track_sid,
                description=description,
                quality_flags=tuple(quality_flags),
                meta=dict(meta or {}),
            )
        )

    def get(self, evidence_id: str) -> TimeAlignedSampleRef | None:
        if not evidence_id:
            return None
        with self._lock:
            return self._by_id.get(evidence_id)

    def timeline(
        self,
        *,
        limit: int = 50,
        kind: EvidenceKind | str | None = None,
        newest_first: bool = True,
    ) -> list[TimeAlignedSampleRef]:
        normalized_kind = _evidence_kind(kind) if kind else None
        with self._lock:
            items = list(self._samples)
        if normalized_kind is not None:
            items = [sample for sample in items if sample.kind == normalized_kind]
        items.sort(key=lambda sample: sample.timebase.wall_time_ms, reverse=newest_first)
        return items[: max(1, min(limit, 200))]

    def status(self) -> dict[str, Any]:
        with self._lock:
            items = list(self._samples)
        by_kind: dict[str, int] = {}
        latest_by_kind: dict[str, dict[str, Any]] = {}
        for sample in items:
            kind = str(sample.kind)
            by_kind[kind] = by_kind.get(kind, 0) + 1
            current = latest_by_kind.get(kind)
            if current is None or sample.timebase.wall_time_ms >= int(
                current.get("timebase", {}).get("wall_time_ms", 0)
            ):
                latest_by_kind[kind] = sample.as_json()
        return {
            "action": "vision.evidence.status",
            "sample_count": len(items),
            "by_kind": by_kind,
            "latest_by_kind": latest_by_kind,
            "visual_asset_count": sum(1 for s in items if s.has_asset),
            "now_ms": int(time.time() * 1000),
            "schema": "TimeAlignedEvidenceRef.web_backend_v1",
        }

    def nearest(
        self,
        *,
        target_time_ms: int = 0,
        kinds: tuple[EvidenceKind, ...] = (
            EvidenceKind.VIDEO_FRAME,
            EvidenceKind.IMAGE_ASSET,
        ),
        require_asset: bool = False,
        window_ms: int = 10_000,
    ) -> TimeAlignedSampleRef | None:
        with self._lock:
            items = list(self._samples)
        candidates = [
            sample
            for sample in items
            if sample.status == EvidenceStatus.READY
            and sample.kind in kinds
            and (not require_asset or sample.has_asset)
        ]
        if not candidates:
            return None

        target = int(target_time_ms or time.time() * 1000)
        candidates.sort(key=lambda sample: abs(sample.timebase.wall_time_ms - target))
        best = candidates[0]
        if window_ms > 0 and abs(best.timebase.wall_time_ms - target) > window_ms:
            return None
        return best


_LEDGER = TemporalEvidenceLedger()


def get_evidence_ledger() -> TemporalEvidenceLedger:
    return _LEDGER


def record_ecp_evidence_sample(
    event: Any,
    *,
    kind: EvidenceKind,
    status: EvidenceStatus = EvidenceStatus.READY,
    asset_path: str = "",
    asset_uri: str = "",
    related_refs: tuple[str, ...] = (),
    bbox_refs: tuple[str, ...] = (),
    focus_refs: tuple[str, ...] = (),
    description: str = "",
    meta: dict[str, Any] | None = None,
) -> TimeAlignedSampleRef:
    payload = getattr(event, "payload", {}) or {}
    timebase = TimebaseStamp.from_payload(
        payload,
        default_domain=ClockDomain.UNITY,
        default_source_id=str(getattr(event, "unity_identity", "") or ""),
        envelope_created_at_ms=int(getattr(event, "created_at", 0) or 0),
    )
    event_meta = {
        "event_id": str(getattr(event, "event_id", "") or ""),
        "event_type": str(getattr(event, "event_type", "") or ""),
        "envelope_created_at_ms": int(getattr(event, "created_at", 0) or 0),
    }
    event_meta.update(dict(meta or {}))
    return get_evidence_ledger().record_sample(
        kind=kind,
        status=status,
        timebase=timebase,
        asset_path=asset_path,
        asset_uri=asset_uri,
        related_refs=related_refs,
        bbox_refs=bbox_refs,
        focus_refs=focus_refs,
        description=description,
        room_id=str(getattr(event, "room_id", "") or ""),
        meta=event_meta,
    )


async def resolve_identify_evidence(
    *,
    evidence_id: str = "",
    bbox_ref_id: str = "",
    focus_ref_id: str = "",
    target_time_ms: int = 0,
    description: str = "",
    request_source: str = "identify_object",
) -> TimeAlignedSampleRef | None:
    """Find a stored visual sample for ``identify_object``.

    The function never calls Unity snapshot RPC.  If no image/frame is ready it
    records a pending request so the Web console and future frame workers can
    see what GOSLO asked for.
    """
    ledger = get_evidence_ledger()
    if evidence_id:
        sample = ledger.get(evidence_id)
        if sample is not None:
            return sample

    sample = ledger.nearest(
        target_time_ms=target_time_ms,
        kinds=(EvidenceKind.VIDEO_FRAME,),
        require_asset=True,
        window_ms=15_000,
    )
    if sample is None:
        sample = ledger.nearest(
            target_time_ms=target_time_ms,
            kinds=(EvidenceKind.IMAGE_ASSET,),
            require_asset=True,
            window_ms=15_000,
        )
    if sample is not None:
        return sample

    refs = tuple(ref for ref in (bbox_ref_id, focus_ref_id) if ref)
    ledger.record_sample(
        kind=EvidenceKind.EVIDENCE_REQUEST,
        status=EvidenceStatus.PENDING,
        timebase=TimebaseStamp.from_payload(
            {"wall_time_ms": target_time_ms} if target_time_ms else {},
            default_domain=ClockDomain.BRAIN,
            default_source_id=request_source,
        ),
        related_refs=refs,
        bbox_refs=(bbox_ref_id,) if bbox_ref_id else (),
        focus_refs=(focus_ref_id,) if focus_ref_id else (),
        description=description,
        meta={
            "request_source": request_source,
            "requested_evidence_id": evidence_id,
            "needs": "stored image/video frame near target_time_ms",
        },
    )
    return None


def _clock_domain(raw: Any, default: ClockDomain) -> ClockDomain:
    try:
        return ClockDomain(str(raw))
    except Exception:
        return default


def _evidence_kind(raw: EvidenceKind | str | None) -> EvidenceKind | None:
    if raw is None:
        return None
    try:
        return raw if isinstance(raw, EvidenceKind) else EvidenceKind(str(raw))
    except Exception:
        return None


def _coerce_int(raw: Any) -> int:
    if isinstance(raw, bool):
        return 0
    try:
        return int(raw)
    except Exception:
        return 0


def _coerce_epoch_ms(raw: Any) -> int:
    if isinstance(raw, bool):
        return 0
    try:
        value = float(raw)
    except Exception:
        return 0
    if value <= 0:
        return 0
    # Seconds since epoch are usually 10 digits; milliseconds are 13.
    return int(value * 1000) if value < 10_000_000_000 else int(value)


def _legacy_wall_time_ms(raw: dict[str, Any]) -> int:
    for key in ("ts_ms", "target_time_ms", "timestamp_ms", "observed_at_ms"):
        value = _coerce_epoch_ms(raw.get(key))
        if value > 0:
            return value
    for key in ("timestamp", "observed_at", "started_at", "captured_at"):
        parsed = _coerce_epoch_ms(raw.get(key))
        if parsed > 0:
            return parsed
        iso = _parse_iso_ms(raw.get(key))
        if iso > 0:
            return iso
    return 0


def _parse_iso_ms(raw: Any) -> int:
    if not isinstance(raw, str) or not raw.strip():
        return 0
    text = raw.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return 0
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp() * 1000)


def _asset_exists(asset_path: str) -> bool:
    if not asset_path:
        return False
    try:
        return Path(asset_path).exists()
    except OSError:
        return False


__all__ = [
    "ClockDomain",
    "EvidenceKind",
    "EvidenceStatus",
    "SampleRegion",
    "TemporalEvidenceLedger",
    "TimeAlignedSampleRef",
    "TimebaseStamp",
    "get_evidence_ledger",
    "record_ecp_evidence_sample",
    "resolve_identify_evidence",
]
