"""Web Console BFF helpers for time-aligned evidence debugging."""

from __future__ import annotations

import time
from typing import Any

from parrot.brain.vision.evidence import (
    ClockDomain,
    EvidenceKind,
    EvidenceStatus,
    SampleRegion,
    TimebaseStamp,
    get_evidence_ledger,
)
from parrot.brain.vision.frame_cache import get_frame_cache


def evidence_status() -> dict[str, Any]:
    """Return a secret-free temporal evidence ledger summary."""
    status = get_evidence_ledger().status()
    status["frame_cache"] = get_frame_cache().status()
    return status


def evidence_timeline(*, limit: int = 50, kind: str = "") -> dict[str, Any]:
    normalized_kind = _kind_or_none(kind)
    samples = get_evidence_ledger().timeline(
        limit=max(1, min(int(limit or 50), 200)),
        kind=normalized_kind,
    )
    return {
        "action": "vision.evidence.timeline",
        "success": True,
        "items": [sample.as_json() for sample in samples],
        "limit": max(1, min(int(limit or 50), 200)),
        "kind": str(normalized_kind or ""),
        "now_ms": int(time.time() * 1000),
    }


def evidence_detail(evidence_id: str) -> dict[str, Any]:
    sample = get_evidence_ledger().get(evidence_id)
    if sample is None:
        return {
            "action": "vision.evidence.detail",
            "success": False,
            "message": "evidence_not_found",
            "evidence_id": evidence_id,
        }
    return {
        "action": "vision.evidence.detail",
        "success": True,
        "evidence": sample.as_json(),
    }


def request_evidence(payload: dict[str, Any] | None) -> dict[str, Any]:
    """Request or locate a visual evidence sample near a target time."""
    body = payload or {}
    ledger = get_evidence_ledger()
    evidence_id = str(body.get("evidence_id", "") or "")
    if evidence_id:
        sample = ledger.get(evidence_id)
        if sample is not None:
            return {
                "action": "vision.evidence.request",
                "success": True,
                "message": "evidence_found",
                "evidence": sample.as_json(),
                "request": _request_view(body),
            }

    target_time_ms = _body_int(body.get("target_time_ms"), 0)
    require_asset = _body_bool(body.get("require_asset"), True)
    sample = ledger.nearest(
        target_time_ms=target_time_ms,
        require_asset=require_asset,
        window_ms=_body_int(body.get("window_ms"), 15_000),
    )
    if sample is not None:
        return {
            "action": "vision.evidence.request",
            "success": True,
            "message": "nearest_evidence_found",
            "evidence": sample.as_json(),
            "request": _request_view(body),
        }

    request = ledger.record_sample(
        kind=EvidenceKind.EVIDENCE_REQUEST,
        status=EvidenceStatus.PENDING,
        timebase=TimebaseStamp.from_payload(
            {"wall_time_ms": target_time_ms} if target_time_ms else {},
            default_domain=ClockDomain.WEB,
            default_source_id="web_console",
        ),
        related_refs=tuple(
            ref
            for ref in (
                str(body.get("bbox_ref_id", "") or ""),
                str(body.get("focus_ref_id", "") or ""),
            )
            if ref
        ),
        bbox_refs=(str(body.get("bbox_ref_id", "") or ""),)
        if body.get("bbox_ref_id")
        else (),
        focus_refs=(str(body.get("focus_ref_id", "") or ""),)
        if body.get("focus_ref_id")
        else (),
        description=str(body.get("description", "") or "web evidence request"),
        meta={"source": "web_console", "request": _request_view(body)},
    )
    return {
        "action": "vision.evidence.request",
        "success": False,
        "message": "evidence_request_recorded",
        "evidence": None,
        "request_evidence": request.as_json(),
        "request": _request_view(body),
    }


def simulate_visual_attention(payload: dict[str, Any] | None) -> dict[str, Any]:
    """Record and optionally dispatch a BBox/Focus attention test event."""
    body = payload or {}
    kind = str(body.get("kind") or body.get("subject_kind") or "bbox").lower()
    action = str(body.get("action") or ("placed" if kind == "bbox" else "anchored"))
    subject_id = str(
        body.get("subject_id")
        or body.get("bbox_id")
        or body.get("focus_id")
        or f"web_{kind}_{int(time.time() * 1000)}"
    )
    label = str(body.get("label") or f"web {kind} attention")
    dispatch = _body_bool(body.get("dispatch_harness"), True)

    harness_receipt: dict[str, Any] | None = None
    if dispatch:
        harness_receipt = _dispatch_harness(kind=kind, action=action, subject_id=subject_id, label=label)

    region = _region_from_body(body)
    refs = (subject_id,)
    sample = get_evidence_ledger().record_sample(
        kind=EvidenceKind.BBOX_FOCUS,
        status=EvidenceStatus.READY,
        timebase=TimebaseStamp.from_payload(
            body,
            default_domain=ClockDomain.WEB,
            default_source_id="web_console",
        ),
        region=region,
        related_refs=refs,
        bbox_refs=refs if kind == "bbox" else (),
        focus_refs=refs if kind == "focus" else (),
        description=label,
        meta={
            "source": "web_console.visual_attention",
            "subject_kind": kind,
            "subject_id": subject_id,
            "action": action,
            "harness_dispatched": bool(harness_receipt),
        },
    )
    return {
        "action": "app.test.visual_attention",
        "success": True,
        "message": "visual_attention_recorded",
        "evidence": sample.as_json(),
        "harness": harness_receipt,
    }


def upload_frame_cache(payload: dict[str, Any] | None) -> dict[str, Any]:
    """Operator-gated debug ingress for encoded LiveKit/SVA frame bytes."""
    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    image_base64 = str(body.get("image_base64", "") or "")
    mime_type = str(body.get("mime_type", "") or "image/jpeg")
    common = {
        "action": "vision.evidence.frame_cache.upload",
        "dry_run": dry_run,
        "operator_mode": operator_mode,
    }
    if not image_base64:
        return {
            **common,
            "success": False,
            "message": "missing_image_base64",
        }
    if dry_run or not operator_mode:
        return {
            **common,
            "success": True,
            "message": "frame_cache_upload_validated",
            "data": {
                "would_write": True,
                "apply_skipped_reason": "dry_run_or_operator_mode_missing",
                "mime_type": mime_type,
                "track_sid": str(body.get("track_sid", "") or ""),
                "source_id": str(body.get("source_id", "") or ""),
            },
        }

    try:
        sample = get_frame_cache().record_base64_frame(
            image_base64,
            mime_type=mime_type,
            room_id=str(body.get("room_id", "") or ""),
            track_sid=str(body.get("track_sid", "") or ""),
            participant_id=str(body.get("participant_id", "") or ""),
            source_id=str(body.get("source_id", "") or ""),
            wall_time_ms=_body_int(body.get("wall_time_ms"), 0),
            monotonic_ms=_body_int(body.get("monotonic_ms"), 0),
            media_time_us=_body_int(body.get("media_time_us"), 0),
            sequence=_body_int(body.get("sequence"), 0),
            description=str(body.get("description", "") or "Web uploaded cached frame"),
            meta={"source": "web_console.frame_cache_upload"},
        )
    except Exception as exc:
        return {
            **common,
            "success": False,
            "message": str(exc),
        }

    return {
        **common,
        "success": True,
        "message": "frame_cached",
        "evidence": sample.as_json(),
        "frame_cache": get_frame_cache().status(),
    }


def _dispatch_harness(
    *,
    kind: str,
    action: str,
    subject_id: str,
    label: str,
) -> dict[str, Any]:
    try:
        from parrot.brain.app_test_harness import (
            simulate_bbox_event,
            simulate_focus_event,
        )

        if kind == "focus":
            return simulate_focus_event(
                focus_id=subject_id,
                action=action if action in {"anchored", "released"} else "anchored",
                label=label,
            ).as_json()
        return simulate_bbox_event(
            bbox_id=subject_id,
            action=action if action in {"placed", "removed"} else "placed",
            label=label,
        ).as_json()
    except Exception as exc:
        return {
            "action": "app.test.visual_attention.harness",
            "success": False,
            "message": type(exc).__name__,
        }


def _region_from_body(body: dict[str, Any]) -> SampleRegion | None:
    region = body.get("region")
    if isinstance(region, dict):
        return SampleRegion(
            x=_body_float(region.get("x"), 0.0),
            y=_body_float(region.get("y"), 0.0),
            width=_body_float(region.get("width"), 0.0),
            height=_body_float(region.get("height"), 0.0),
            coordinate_space=str(region.get("coordinate_space") or "normalized"),
        )
    bbox = body.get("bbox")
    if isinstance(bbox, (list, tuple)) and len(bbox) >= 4:
        return SampleRegion(
            x=_body_float(bbox[0], 0.0),
            y=_body_float(bbox[1], 0.0),
            width=_body_float(bbox[2], 0.0),
            height=_body_float(bbox[3], 0.0),
        )
    return None


def _request_view(body: dict[str, Any]) -> dict[str, Any]:
    return {
        "evidence_id": str(body.get("evidence_id", "") or ""),
        "target_time_ms": _body_int(body.get("target_time_ms"), 0),
        "window_ms": _body_int(body.get("window_ms"), 15_000),
        "require_asset": _body_bool(body.get("require_asset"), True),
        "bbox_ref_id": str(body.get("bbox_ref_id", "") or ""),
        "focus_ref_id": str(body.get("focus_ref_id", "") or ""),
    }


def _kind_or_none(kind: str) -> EvidenceKind | None:
    if not kind:
        return None
    try:
        return EvidenceKind(kind)
    except Exception:
        return None


def _body_bool(raw: Any, default: bool = False) -> bool:
    if raw is None:
        return default
    if isinstance(raw, bool):
        return raw
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def _body_int(raw: Any, default: int) -> int:
    if isinstance(raw, bool):
        return default
    try:
        return int(raw)
    except Exception:
        return default


def _body_float(raw: Any, default: float) -> float:
    if isinstance(raw, bool):
        return default
    try:
        return float(raw)
    except Exception:
        return default


__all__ = [
    "evidence_detail",
    "evidence_status",
    "evidence_timeline",
    "request_evidence",
    "simulate_visual_attention",
    "upload_frame_cache",
]
