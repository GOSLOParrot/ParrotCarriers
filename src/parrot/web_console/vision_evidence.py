"""Web Console BFF helpers for time-aligned evidence debugging."""

from __future__ import annotations

import time
from typing import Any

from parrot.brain.vision.evidence import (
    ClockDomain,
    EvidenceKind,
    EvidenceStatus,
    SampleRegion,
    TimeAlignedSampleRef,
    TimebaseStamp,
    get_evidence_ledger,
)
from parrot.brain.vision.frame_cache import get_frame_cache
from parrot.brain.vision.evidence_awareness import (
    latest_evidence_awareness_notice,
    stage_evidence_for_goslo,
)
from parrot.brain.vision.livekit_sampler import read_livekit_frame_sampler_status


def evidence_status() -> dict[str, Any]:
    """Return a secret-free temporal evidence ledger summary."""
    status = get_evidence_ledger().status()
    status["frame_cache"] = get_frame_cache().status()
    status["livekit_sampler"] = read_livekit_frame_sampler_status()
    status["evidence_awareness"] = latest_evidence_awareness_notice()
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


def evidence_memory_draft(payload: dict[str, Any] | None) -> dict[str, Any]:
    """Draft a safe Evidence -> Memory promotion without mutating L1.5/L2-B.

    Runtime owns sampling and attention; Memory owns durable graph/ref
    management.  This route is the handoff receipt between them.  It converts a
    stored ``TimeAlignedSampleRef`` into an operator-readable promotion plan:

    - create/update an L2-B node through ``L15Pool.admit(Observation(...))``;
    - optionally attach an existing BBox/Focus/Photo ref through the CORE-006
      RefBinding draft path; or
    - keep the sample staged only when the operator has not chosen a target.

    V1 intentionally has no apply branch.  The user-visible button can preview
    exactly what would happen while App/Web review CORE-012 and CORE-006.
    """
    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    sample = _resolve_sample_for_memory_draft(body)
    if sample is None:
        return _receipt(
            action="vision.evidence.memory_draft",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "error": "evidence_not_found",
                "evidence_id": str(body.get("evidence_id") or ""),
                "target_time_ms": _body_int(body.get("target_time_ms"), 0),
                "core_candidates": ["CORE-012", "CORE-006", "CORE-008"],
            },
        )

    mode = str(body.get("mode") or "create_node").strip().lower()
    if mode not in {"create_node", "attach_ref", "stage_only"}:
        mode = "create_node"
    observation = _sample_to_observation_draft(sample, body)
    ref_binding = _ref_binding_draft_for_sample(sample, body)
    if mode == "attach_ref" and not ref_binding.get("ref_id"):
        return _receipt(
            action="vision.evidence.memory_draft",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "error": "missing_ref_for_attach_ref",
                "evidence": sample.as_json(),
                "available_refs": _sample_refs(sample),
                "core_candidates": ["CORE-012", "CORE-006"],
            },
        )

    plan = {
        "mode": mode,
        "evidence": sample.as_json(),
        "observation": observation if mode != "stage_only" else None,
        "ref_binding_draft": ref_binding if ref_binding.get("ref_id") else None,
        "operator_required_for_execute": True,
        "apply_route": "",
        "apply_status": "not_implemented_until_CORE_012_review",
        "write_paths": {
            "node": "L15Pool.admit(Observation(source=USER_EXPLICIT))",
            "ref_binding": "RefBinding draft only; CORE-006 apply route not ratified",
            "stage_only": "IntentWorkspace visual_evidence_hint / no L2-B mutation",
        },
        "mapping": {
            "runtime_source": "TemporalEvidenceLedger",
            "working_context": "IntentWorkspace visual_evidence_hint",
            "memory_gate": "L1.5 admit before L2-B",
            "durable_graph": "L2-B SemanticNode/RefBinding after operator review",
        },
        "core_candidates": ["CORE-012", "CORE-006", "CORE-008"],
    }
    return _receipt(
        action="vision.evidence.memory_draft",
        success=True,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data=plan,
    )


def screen_share_smoke_check(*, window_ms: int = 15_000) -> dict[str, Any]:
    """Return a read-only verdict for the Web no-camera screen-share smoke.

    The browser can publish a screen-share track, but the important backend
    proof is whether Brain's sampler/frame cache produced a fresh, auditable
    ``VIDEO_FRAME`` row that still carries a screen-share source hint.  Keep
    this check server-side so Web receipts, docs, and tests all use the same
    rule and no failed check writes noisy pending evidence rows.
    """
    bounded_window_ms = max(1_000, min(int(window_ms or 15_000), 120_000))
    now_ms = int(time.time() * 1000)
    status = evidence_status()
    sampler = _dict_or_empty(status.get("livekit_sampler"))
    frame_cache = _dict_or_empty(status.get("frame_cache"))
    nearest = get_evidence_ledger().nearest(
        target_time_ms=now_ms,
        require_asset=True,
        window_ms=bounded_window_ms,
    )
    nearest_json = nearest.as_json() if nearest is not None else None

    candidate_rows = _screen_share_candidate_rows(
        nearest_json=nearest_json,
        sampler=sampler,
        frame_cache=frame_cache,
    )

    likely_screen_share = any(_looks_like_screen_share(row["item"]) for row in candidate_rows)
    fresh_screen_share = any(
        bool(row.get("fresh")) and _looks_like_screen_share(row["item"])
        for row in candidate_rows
    )
    fresh_any_evidence = bool(
        sampler.get("latest_frame_fresh")
        or frame_cache.get("latest_frame_fresh")
        or nearest_json
    )
    screen_share_confirmed = fresh_screen_share
    data = {
        "window_ms": bounded_window_ms,
        "fresh_any_evidence": fresh_any_evidence,
        "screen_share_confirmed": screen_share_confirmed,
        "likely_screen_share": likely_screen_share,
        "fresh_screen_share": fresh_screen_share,
        "nearest_evidence_found": nearest_json is not None,
        "nearest_evidence_id": str((nearest_json or {}).get("evidence_id") or ""),
        "latest_frame_fresh": bool(
            sampler.get("latest_frame_fresh") or frame_cache.get("latest_frame_fresh")
        ),
        "sampler_available": bool(sampler.get("available")),
        "sampler_active_tracks": _list_len(sampler.get("active_tracks")),
        "sampler_recorded_frames": _body_int(sampler.get("recorded_frames"), 0),
        "sampler_latest_age_ms": sampler.get("latest_frame_age_ms"),
        "sampler_latest_source": _screen_share_source_hint(sampler.get("latest_frame")),
        "frame_cache_count": _body_int(frame_cache.get("frame_count"), 0),
        "frame_cache_latest_age_ms": frame_cache.get("latest_frame_age_ms"),
        "frame_cache_latest_fresh": bool(frame_cache.get("latest_frame_fresh")),
        "frame_cache_latest_source": _screen_share_source_hint(frame_cache.get("latest_frame")),
        "next_steps": _screen_share_next_steps(
            sampler_available=bool(sampler.get("available")),
            fresh_any_evidence=fresh_any_evidence,
            likely_screen_share=likely_screen_share,
            fresh_screen_share=fresh_screen_share,
        ),
    }
    if nearest_json is not None:
        data["nearest_evidence"] = _compact_evidence_view(nearest_json)

    message = "screen_share_evidence_confirmed"
    if not screen_share_confirmed:
        if fresh_any_evidence and not likely_screen_share:
            message = "fresh_evidence_not_screen_share"
        elif likely_screen_share:
            message = "screen_share_track_seen_but_stale"
        else:
            message = "no_fresh_screen_share_evidence"
    return {
        "action": "livekit.screen_share.evidence_check",
        "success": screen_share_confirmed,
        "dry_run": True,
        "operator_mode": False,
        "message": message,
        "data": data,
        "audit": {
            "read_only": True,
            "no_pending_request_written": True,
            "secret_safe": True,
            "schema": "ScreenShareEvidenceSmoke.web_backend_v1",
        },
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


async def stage_evidence_hint(payload: dict[str, Any] | None) -> dict[str, Any]:
    """Stage a ready evidence sample into IntentWorkspace for GOSLO."""
    body = payload or {}
    decision = await stage_evidence_for_goslo(
        evidence_id=str(body.get("evidence_id", "") or ""),
        target_time_ms=_body_int(body.get("target_time_ms"), 0),
        description=str(body.get("description", "") or "web evidence hint"),
        notify_requested=_body_bool(body.get("notify_requested"), True),
        source=str(body.get("source", "") or "web_console"),
        ttl_seconds=_body_int(body.get("ttl_seconds"), 15 * 60),
    )
    return {
        "action": "vision.evidence.stage_hint",
        "success": bool(decision.staged_ref_id),
        "decision": decision.as_json(),
        "notice": latest_evidence_awareness_notice(),
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


def _dict_or_empty(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _dict_values(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, dict):
        return []
    return [dict(item) for item in value.values() if isinstance(item, dict)]


def _list_len(value: Any) -> int:
    return len(value) if isinstance(value, list) else 0


def _screen_share_candidate_rows(
    *,
    nearest_json: dict[str, Any] | None,
    sampler: dict[str, Any],
    frame_cache: dict[str, Any],
) -> list[dict[str, Any]]:
    """Pair each screen-share smoke candidate with its own freshness bit.

    Freshness and source classification must belong to the same row. Otherwise
    a stale screen-share track plus a fresh camera frame could accidentally
    pass the no-camera screen-share smoke.
    """
    rows: list[dict[str, Any]] = []
    if isinstance(nearest_json, dict):
        rows.append({"item": nearest_json, "fresh": True})
    sampler_latest = sampler.get("latest_frame")
    if isinstance(sampler_latest, dict):
        rows.append({
            "item": sampler_latest,
            "fresh": bool(sampler_latest.get("fresh") or sampler.get("latest_frame_fresh")),
        })
    frame_latest = frame_cache.get("latest_frame")
    if isinstance(frame_latest, dict):
        rows.append({
            "item": frame_latest,
            "fresh": bool(frame_latest.get("fresh") or frame_cache.get("latest_frame_fresh")),
        })
    rows.extend(
        {"item": row, "fresh": bool(row.get("fresh"))}
        for row in _dict_values(sampler.get("tracks"))
    )
    rows.extend(
        {"item": row, "fresh": bool(row.get("fresh"))}
        for row in _dict_values(frame_cache.get("tracks"))
    )
    return rows


def _looks_like_screen_share(row: dict[str, Any]) -> bool:
    text = " ".join(_screen_share_text_parts(row)).lower()
    return (
        "web-console-screen" in text
        or "source_screen_share" in text
        or "screen_share" in text
        or "screenshare" in text
        or ("screen" in text and "share" in text)
    )


def _screen_share_text_parts(row: dict[str, Any]) -> list[str]:
    parts: list[str] = []
    for key in (
        "track_name",
        "source_id",
        "track_sid",
        "participant_id",
        "publication_source",
        "description",
        "room_id",
    ):
        parts.append(str(row.get(key) or ""))
    for nested_key in ("meta", "timebase"):
        nested = row.get(nested_key)
        if isinstance(nested, dict):
            for key in (
                "source",
                "source_id",
                "track_name",
                "publication_source",
                "participant_id",
            ):
                parts.append(str(nested.get(key) or ""))
    return parts


def _screen_share_source_hint(row: Any) -> str:
    if not isinstance(row, dict):
        return ""
    for key in ("track_name", "source_id", "track_sid", "publication_source"):
        value = str(row.get(key) or "")
        if value:
            return value
    timebase = row.get("timebase")
    if isinstance(timebase, dict):
        return str(timebase.get("source_id") or "")
    return ""


def _compact_evidence_view(sample: dict[str, Any]) -> dict[str, Any]:
    timebase = sample.get("timebase") if isinstance(sample.get("timebase"), dict) else {}
    meta = sample.get("meta") if isinstance(sample.get("meta"), dict) else {}
    return {
        "evidence_id": str(sample.get("evidence_id") or ""),
        "kind": str(sample.get("kind") or ""),
        "status": str(sample.get("status") or ""),
        "description": str(sample.get("description") or ""),
        "asset_exists": bool(sample.get("asset_exists")),
        "track_sid": str(sample.get("track_sid") or ""),
        "source_id": str(timebase.get("source_id") or ""),
        "wall_time_ms": _body_int(timebase.get("wall_time_ms"), 0),
        "publication_source": str(meta.get("publication_source") or ""),
    }


def _screen_share_next_steps(
    *,
    sampler_available: bool,
    fresh_any_evidence: bool,
    likely_screen_share: bool,
    fresh_screen_share: bool,
) -> list[str]:
    if fresh_screen_share:
        return [
            "Screen-share evidence is fresh; try Memory Draft or identify_object with this evidence id.",
        ]
    steps = []
    if not sampler_available:
        steps.append("Start Brain/LiveKit Agent so the room-scoped frame sampler writes status.")
    steps.append("Connect Web to the same LiveKit room as Brain.")
    steps.append("Click screen share and choose a window or tab.")
    if fresh_any_evidence and not likely_screen_share:
        steps.append("A fresh frame exists, but its source does not look like screen-share; check track source/name.")
    elif likely_screen_share and not fresh_screen_share:
        steps.append("Screen-share metadata exists, but its latest evidence is stale; share again or wait for a fresh sampler frame.")
    else:
        steps.append("Wait for one sampler interval, then run the check again.")
    return steps


def _resolve_sample_for_memory_draft(body: dict[str, Any]) -> TimeAlignedSampleRef | None:
    evidence_id = str(body.get("evidence_id") or "").strip()
    ledger = get_evidence_ledger()
    if evidence_id:
        return ledger.get(evidence_id)
    return ledger.nearest(
        target_time_ms=_body_int(body.get("target_time_ms"), 0),
        require_asset=_body_bool(body.get("require_asset"), True),
        window_ms=_body_int(body.get("window_ms"), 15_000),
    )


def _sample_to_observation_draft(
    sample: TimeAlignedSampleRef,
    body: dict[str, Any],
) -> dict[str, Any]:
    kind = str(body.get("node_kind") or body.get("kind") or "").strip().lower()
    if kind not in {"object", "surface", "zone", "person", "event", "photo"}:
        sample_kind = _enum_value(sample.kind)
        kind = "photo" if sample_kind in {"image_asset", "video_frame"} else "object"
    label = str(body.get("label") or sample.description or "").strip()
    if not label:
        label = f"{_enum_value(sample.kind)} evidence {sample.evidence_id[:8]}"
    description = str(body.get("description") or sample.description or "").strip()
    if not description:
        description = (
            f"Time-aligned {_enum_value(sample.kind)} evidence "
            f"from {_enum_value(sample.timebase.clock_domain)}."
        )
    return {
        "source": "user_explicit",
        "provenance_stream_id": f"web:evidence:{sample.evidence_id}",
        "obsidian_uuid": "",
        "graphiti_uuid": "",
        "label": label[:128],
        "kind": kind,
        "description": description[:400],
        "confidence": max(0.0, min(_body_float(body.get("confidence"), 0.75), 1.0)),
        "confirmation": str(body.get("confirmation") or "tentative"),
        "reference_image_path": sample.asset_path if _enum_value(sample.kind) == "image_asset" else "",
        "last_sighting_path": sample.asset_path,
        "observed_at": sample.timebase.wall_time_ms / 1000.0 if sample.timebase.wall_time_ms else time.time(),
        "time_span": (
            sample.timebase.wall_time_ms / 1000.0 if sample.timebase.wall_time_ms else 0.0,
            None,
        ),
        "meta": {
            "source_tool": "web_console.evidence_memory_draft",
            "target_node_uuid": str(body.get("target_node_uuid") or body.get("node_uuid") or ""),
            "audit_note": "Draft only. Evidence-to-Memory apply waits for CORE-012/CORE-006 review.",
            "evidence_id": sample.evidence_id,
            "evidence_kind": _enum_value(sample.kind),
            "evidence_status": _enum_value(sample.status),
            "evidence_asset_uri": sample.asset_uri,
            "evidence_asset_path": sample.asset_path,
            "evidence_mime_type": sample.mime_type,
            "evidence_timebase": sample.timebase.model_dump(mode="json"),
            "related_refs": list(sample.related_refs),
            "bbox_refs": list(sample.bbox_refs),
            "focus_refs": list(sample.focus_refs),
            "room_id": sample.room_id,
            "track_sid": sample.track_sid,
            "participant_id": str(getattr(sample, "participant_id", "") or ""),
        },
    }


def _ref_binding_draft_for_sample(
    sample: TimeAlignedSampleRef,
    body: dict[str, Any],
) -> dict[str, Any]:
    ref_id = str(body.get("ref_id") or "").strip()
    if not ref_id:
        refs = _sample_refs(sample)
        ref_id = refs[0] if refs else ""
    target_node_uuid = str(body.get("target_node_uuid") or body.get("node_uuid") or "").strip()
    if not ref_id:
        return {}
    return {
        "ref_id": ref_id,
        "target_kind": "l2b_node" if target_node_uuid else "unresolved",
        "target_id": target_node_uuid,
        "would_unresolve": not bool(target_node_uuid),
        "core_candidate": "CORE-006",
        "write_path": "POST /api/refs/binding/draft",
    }


def _sample_refs(sample: TimeAlignedSampleRef) -> list[str]:
    seen: set[str] = set()
    refs: list[str] = []
    for ref in [*sample.bbox_refs, *sample.focus_refs, *sample.related_refs]:
        text = str(ref or "").strip()
        if text and text not in seen:
            seen.add(text)
            refs.append(text)
    return refs


def _enum_value(value: Any) -> str:
    return str(getattr(value, "value", value) or "")


def _receipt(
    *,
    action: str,
    success: bool,
    dry_run: bool,
    operator_mode: bool,
    data: dict[str, Any],
) -> dict[str, Any]:
    return {
        "action": action,
        "success": success,
        "dry_run": dry_run,
        "operator_mode": operator_mode,
        "receipt": {
            "receipt_id": f"web_evidence_{int(time.time() * 1000):x}",
            "created_at": time.time(),
            "audit_level": "operator" if operator_mode else "draft",
            "secret_redacted": True,
        },
        "audit": {
            "schema": "EvidenceMemoryDraft.web_backend_v1",
            "read_only": True,
            "secret_safe": True,
            "no_l15_mutation": True,
            "no_l2b_mutation": True,
            "no_ref_binding_mutation": True,
            "operator_required_for_execute": True,
        },
        "core_candidate": "CORE-012",
        "core_candidates": ["CORE-012", "CORE-006", "CORE-008"],
        "data": data,
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
    "evidence_memory_draft",
    "evidence_status",
    "evidence_timeline",
    "request_evidence",
    "simulate_visual_attention",
    "stage_evidence_hint",
    "upload_frame_cache",
]
