"""Photo/object/sample catalog for the findObject evidence chain.

This module is the narrow persistence layer between App visual tools,
PhotoNode evidence, and ``identify_object``. It keeps the layers separated:
photos remain photo records, bbox crops become sample drafts, and ObjectNode
binding happens only on explicit accepted paths such as ``save_new``.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import shutil
import time
import uuid as uuid_lib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from parrot.brain.vision.evidence import SampleRegion, TimeAlignedSampleRef
from parrot.brain.vision.evidence_image import persist_evidence_crop

logger = logging.getLogger(__name__)

VISION_ROOT_ENV = "PARROT_VISION_ROOT"
DEFAULT_VISION_ROOT = "data/vision"
SCHEMA_VERSION = 1


@dataclass(frozen=True)
class PhotoRecord:
    photo_uuid: str
    photo_node_uuid: str
    asset_path: str = ""
    rendered_path: str = ""
    thumb_path: str = ""
    content_sha256: str = ""
    evidence_id: str = ""
    intent_workspace_ref_id: str = ""
    captured_at_ms: int = 0
    width: int = 0
    height: int = 0
    photo_report_path: str = ""
    status: str = "ready"
    asset_ref: str = ""
    asset_bytes: int = 0
    created_at_ms: int = 0
    updated_at_ms: int = 0
    meta: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return {"schema_version": SCHEMA_VERSION, **asdict(self)}


@dataclass(frozen=True)
class PhotoObjectRecord:
    object_ref_id: str
    photo_uuid: str
    bbox: dict[str, Any]
    crop_path: str
    sample_draft_id: str
    candidate_object_uuid: str = ""
    edge_uuid: str = ""
    review_status: str = "draft"
    evidence_id: str = ""
    source_asset_path: str = ""
    tool_id: str = ""
    tool_kind: str = ""
    tool_event_id: str = ""
    label_guess: str = ""
    category_guess: str = ""
    confidence: float = 0.0
    source: str = "user_bbox"
    created_at_ms: int = 0
    updated_at_ms: int = 0
    meta: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return {"schema_version": SCHEMA_VERSION, **asdict(self)}


@dataclass(frozen=True)
class ObjectSampleRecord:
    sample_uuid: str
    object_uuid: str
    photo_uuid: str
    object_ref_id: str
    crop_path: str
    source_asset_path: str = ""
    bbox: dict[str, Any] = field(default_factory=dict)
    content_sha256: str = ""
    evidence_id: str = ""
    label: str = ""
    category: str = ""
    visual_description: str = ""
    quality_flags: list[str] = field(default_factory=list)
    review_status: str = "draft"
    created_by: str = "user"
    created_at_ms: int = 0
    updated_at_ms: int = 0
    meta: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return {"schema_version": SCHEMA_VERSION, **asdict(self)}


@dataclass(frozen=True)
class PhotoObjectEdgeRecord:
    edge_uuid: str
    photo_uuid: str
    object_uuid: str
    sample_uuid: str
    evidence_id: str = ""
    bbox: dict[str, Any] = field(default_factory=dict)
    crop_path: str = ""
    object_ref_id: str = ""
    match_confidence: float = 0.0
    match_source: str = "user_confirmed"
    edge_status: str = "candidate"
    review_status: str = "draft"
    created_at_ms: int = 0
    updated_at_ms: int = 0
    meta: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return {"schema_version": SCHEMA_VERSION, **asdict(self)}


def vision_root() -> Path:
    configured = os.getenv(VISION_ROOT_ENV, "").strip()
    return Path(configured).expanduser() if configured else Path(DEFAULT_VISION_ROOT)


def record_photo_asset(
    *,
    photo_uuid: str,
    asset_path: str,
    evidence_id: str = "",
    asset_ref: str = "",
    asset_bytes: int = 0,
    payload: dict[str, Any] | None = None,
    captured_at_ms: int = 0,
    intent_workspace_ref_id: str = "",
) -> dict[str, Any]:
    """Record a storage-backed PhotoNode asset in the vision catalog."""
    photo_uuid = str(photo_uuid or "").strip()
    if not photo_uuid:
        return {"action": "vision.object_discovery.photo_asset", "success": False, "error": "missing_photo_uuid"}

    existing = _find_jsonl_record(
        _catalog_file("photos.jsonl"),
        lambda row: str(row.get("photo_uuid") or "") == photo_uuid
        and str(row.get("asset_path") or "") == str(asset_path or ""),
    )
    if existing is not None:
        return {
            "action": "vision.object_discovery.photo_asset",
            "success": True,
            "idempotent": True,
            "photo": existing,
        }

    now_ms = _now_ms()
    width, height = _image_size(asset_path)
    record = PhotoRecord(
        photo_uuid=photo_uuid,
        photo_node_uuid=photo_uuid,
        asset_path=str(asset_path or ""),
        content_sha256=_sha256_file(asset_path),
        evidence_id=str(evidence_id or ""),
        intent_workspace_ref_id=str(intent_workspace_ref_id or ""),
        captured_at_ms=int(captured_at_ms or now_ms),
        width=width,
        height=height,
        asset_ref=str(asset_ref or ""),
        asset_bytes=int(asset_bytes or 0),
        created_at_ms=now_ms,
        updated_at_ms=now_ms,
        meta={
            "schema": "vision_photo_record_v1",
            "source": "observer.photo",
            "payload": _small_dict(payload),
        },
    )
    _append_jsonl(_catalog_file("photos.jsonl"), record.as_json())
    return {
        "action": "vision.object_discovery.photo_asset",
        "success": True,
        "photo": record.as_json(),
    }


def record_visual_tool_object_draft(
    *,
    packet: Any,
    sample: TimeAlignedSampleRef,
    ref_id: str = "",
) -> dict[str, Any]:
    """Create a PhotoObject/ObjectSample draft from a BBox confirm packet."""
    tool_kind = _enum_value(getattr(packet, "tool_kind", ""))
    phase = _enum_value(getattr(packet, "interaction_phase", ""))
    if tool_kind != "bbox" or phase not in {"confirm", "explicit_send"}:
        return {}

    existing = _find_existing_draft(
        evidence_id=sample.evidence_id,
        tool_event_id=str(getattr(packet, "tool_event_id", "") or ""),
    )
    if existing is not None:
        return {
            "action": "vision.object_discovery.object_draft",
            "success": True,
            "idempotent": True,
            "photo_object": existing,
            "sample": _find_sample_by_uuid(str(existing.get("sample_draft_id") or "")) or {},
            "audit": _audit_base(),
        }

    now_ms = _now_ms()
    photo_uuid = _extract_photo_uuid(packet, sample)
    object_ref_id = _new_prefixed_id("pobj")
    sample_uuid = _new_prefixed_id("os")
    bbox = _region_dict(getattr(sample, "region", None) or getattr(packet, "region", None))
    source_asset_path = str(sample.asset_path or getattr(packet, "asset_path", "") or "")
    label = _label_from_packet(packet)
    category = _category_from_packet(packet)
    sample_source = str((getattr(packet, "meta", {}) or {}).get("sample_source") or "user_bbox")
    quality_flags: list[str] = []
    crop_path = ""
    content_sha256 = ""
    review_status = "draft"

    if source_asset_path:
        output_path = _staging_sample_path(
            photo_uuid=photo_uuid,
            object_ref_id=object_ref_id,
            sample_uuid=sample_uuid,
        )
        persisted = persist_evidence_crop(
            sample,
            output_path,
            assume_source_is_crop=_asset_is_already_region_capture(source_asset_path, packet),
        )
        if persisted is None:
            review_status = "needs_crop"
            quality_flags.append("crop_persist_failed")
        else:
            crop_path = persisted.crop_path
            content_sha256 = persisted.content_sha256
            if persisted.width < 16 or persisted.height < 16:
                quality_flags.append("crop_too_small")
    else:
        review_status = "needs_crop"
        quality_flags.append("missing_asset")

    photo_object = PhotoObjectRecord(
        object_ref_id=object_ref_id,
        photo_uuid=photo_uuid,
        bbox=bbox,
        crop_path=crop_path,
        sample_draft_id=sample_uuid,
        review_status=review_status,
        evidence_id=sample.evidence_id,
        source_asset_path=source_asset_path,
        tool_id=str(getattr(packet, "tool_id", "") or ""),
        tool_kind=tool_kind,
        tool_event_id=str(getattr(packet, "tool_event_id", "") or ""),
        label_guess=label,
        category_guess=category,
        confidence=float(getattr(packet, "attention_hint", 0.0) or 0.0),
        source=sample_source,
        created_at_ms=now_ms,
        updated_at_ms=now_ms,
        meta={
            "schema": "vision_photo_object_draft_v1",
            "source_ref_id": ref_id,
            "source_surface": str(getattr(packet, "source_surface", "") or ""),
            "packet_meta": _small_dict(getattr(packet, "meta", {}) or {}),
        },
    )
    object_sample = ObjectSampleRecord(
        sample_uuid=sample_uuid,
        object_uuid="",
        photo_uuid=photo_uuid,
        object_ref_id=object_ref_id,
        crop_path=crop_path,
        source_asset_path=source_asset_path,
        bbox=bbox,
        content_sha256=content_sha256,
        evidence_id=sample.evidence_id,
        label=label,
        category=category,
        quality_flags=quality_flags,
        review_status=review_status,
        created_by=sample_source,
        created_at_ms=now_ms,
        updated_at_ms=now_ms,
        meta={
            "schema": "vision_object_sample_draft_v1",
            "source_ref_id": ref_id,
            "source_tool_id": str(getattr(packet, "tool_id", "") or ""),
            "source_tool_event_id": str(getattr(packet, "tool_event_id", "") or ""),
        },
    )
    _append_jsonl(_catalog_file("photo_objects.jsonl"), photo_object.as_json())
    _append_jsonl(_catalog_file("object_samples.jsonl"), object_sample.as_json())
    manifest_path = _write_staging_manifest(photo_object, object_sample)
    intent_workspace_ref_id = _stage_object_sample_draft(
        photo_object=photo_object,
        sample=object_sample,
        manifest_path=manifest_path,
    )
    if intent_workspace_ref_id:
        _patch_staging_manifest(manifest_path, intent_workspace_ref_id=intent_workspace_ref_id)
    return {
        "action": "vision.object_discovery.object_draft",
        "success": True,
        "photo_object": photo_object.as_json(),
        "sample": object_sample.as_json(),
        "manifest_path": str(manifest_path),
        "intent_workspace_ref_id": intent_workspace_ref_id,
        "audit": {
            **_audit_base(),
            "identity_binding": "draft_only_no_object_uuid",
            "photo_uuid_missing": not bool(photo_uuid),
        },
    }


def accept_new_object_from_evidence(
    *,
    object_uuid: str,
    description: str,
    category: str = "",
    evidence_sample: TimeAlignedSampleRef | None = None,
    photo_uuid: str = "",
    object_ref_id: str = "",
    match_source: str = "user_confirmed",
    match_confidence: float = 0.9,
) -> dict[str, Any]:
    """Promote evidence or a draft sample into an accepted ObjectSample."""
    object_uuid = str(object_uuid or "").strip()
    if not object_uuid:
        return {"action": "vision.object_discovery.accept_sample", "success": False, "error": "missing_object_uuid"}

    draft_object = _find_photo_object_by_ref(object_ref_id) if object_ref_id else None
    draft_sample = _find_sample_by_uuid(str(draft_object.get("sample_draft_id") or "")) if draft_object else None
    if draft_object is None and evidence_sample is not None:
        draft_object = _find_draft_by_evidence(evidence_sample.evidence_id)
        draft_sample = _find_sample_by_uuid(str(draft_object.get("sample_draft_id") or "")) if draft_object else None

    now_ms = _now_ms()
    sample_uuid = str((draft_sample or {}).get("sample_uuid") or _new_prefixed_id("os"))
    resolved_photo_uuid = str(photo_uuid or (draft_sample or {}).get("photo_uuid") or (draft_object or {}).get("photo_uuid") or "")
    resolved_object_ref_id = str(object_ref_id or (draft_sample or {}).get("object_ref_id") or (draft_object or {}).get("object_ref_id") or "")
    bbox = _dict_or_empty((draft_sample or {}).get("bbox") or (draft_object or {}).get("bbox"))
    source_asset_path = str((draft_sample or {}).get("source_asset_path") or getattr(evidence_sample, "asset_path", "") or "")
    source_crop_path = str((draft_sample or {}).get("crop_path") or "")
    content_sha256 = str((draft_sample or {}).get("content_sha256") or "")
    quality_flags = list((draft_sample or {}).get("quality_flags") or [])

    if not source_crop_path and evidence_sample is not None:
        temp_ref = resolved_object_ref_id or _new_prefixed_id("pobj")
        resolved_object_ref_id = temp_ref
        persisted = persist_evidence_crop(
            evidence_sample,
            _staging_sample_path(
                photo_uuid=resolved_photo_uuid,
                object_ref_id=temp_ref,
                sample_uuid=sample_uuid,
            ),
            assume_source_is_crop=_asset_is_already_region_capture(str(evidence_sample.asset_path), None),
        )
        if persisted is not None:
            source_crop_path = persisted.crop_path
            source_asset_path = persisted.source_asset_path
            content_sha256 = persisted.content_sha256
        else:
            quality_flags.append("crop_persist_failed")

    accepted_path = ""
    if source_crop_path:
        target_path = str(_accepted_sample_path(object_uuid=object_uuid, sample_uuid=sample_uuid))
        if _copy_sample_file(source_crop_path, target_path):
            accepted_path = target_path
            content_sha256 = _sha256_file(accepted_path) or content_sha256
        else:
            quality_flags.append("accepted_copy_failed")
    elif source_asset_path:
        target_path = str(_accepted_sample_path(object_uuid=object_uuid, sample_uuid=sample_uuid))
        if _copy_sample_file(source_asset_path, target_path):
            accepted_path = target_path
            content_sha256 = _sha256_file(accepted_path) or content_sha256
        else:
            quality_flags.append("accepted_copy_failed")
    else:
        quality_flags.append("missing_asset")

    accepted = ObjectSampleRecord(
        sample_uuid=sample_uuid,
        object_uuid=object_uuid,
        photo_uuid=resolved_photo_uuid,
        object_ref_id=resolved_object_ref_id,
        crop_path=accepted_path,
        source_asset_path=source_asset_path,
        bbox=bbox,
        content_sha256=content_sha256,
        evidence_id=str(getattr(evidence_sample, "evidence_id", "") or (draft_sample or {}).get("evidence_id") or ""),
        label=description[:120],
        category=category,
        quality_flags=quality_flags,
        review_status="accepted" if accepted_path else "needs_crop",
        created_by="identify_object_save_new",
        created_at_ms=now_ms,
        updated_at_ms=now_ms,
        meta={
            "schema": "vision_object_sample_accepted_v1",
            "source_draft_sample_id": str((draft_sample or {}).get("sample_uuid") or ""),
        },
    )
    _append_jsonl(_catalog_file("object_samples.jsonl"), accepted.as_json())
    _write_object_sample_manifest(object_uuid, accepted)

    edge_result = _record_photo_object_edge(
        photo_uuid=resolved_photo_uuid,
        object_uuid=object_uuid,
        sample=accepted,
        object_ref_id=resolved_object_ref_id,
        match_source=match_source,
        match_confidence=match_confidence,
        edge_status="confirmed",
        review_status=accepted.review_status,
    )
    _update_l2b_object_profile(
        object_uuid=object_uuid,
        description=description,
        category=category,
        sample=accepted,
        edge=edge_result.get("edge", {}),
    )
    identity = _bind_identity_ref_index(
        object_uuid=object_uuid,
        description=description,
        category=category,
        sample=accepted,
        confidence=match_confidence,
    )
    refs = _bind_l1_5_refs(object_uuid=object_uuid, sample=accepted)
    report = _create_object_analysis_report(object_uuid)
    return {
        "action": "vision.object_discovery.accept_sample",
        "success": True,
        "sample": accepted.as_json(),
        "edge": edge_result.get("edge", {}),
        "l2b_edge_written": bool(edge_result.get("l2b_edge_written")),
        "identity": identity,
        "l1_5_refs": refs,
        "object_report": report,
        "audit": _audit_base(),
    }


def record_candidate_match_from_evidence(
    *,
    object_uuid: str,
    evidence_sample: TimeAlignedSampleRef | None,
    description: str,
    category: str = "",
    match_source: str = "l0_text",
    match_confidence: float = 0.0,
) -> dict[str, Any]:
    """Write a candidate sample/edge for an automatic match without accepting it."""
    if evidence_sample is None or not object_uuid:
        return {}
    existing = _find_draft_by_evidence(evidence_sample.evidence_id)
    sample_uuid = str((existing or {}).get("sample_draft_id") or _new_prefixed_id("os"))
    object_ref_id = str((existing or {}).get("object_ref_id") or _new_prefixed_id("pobj"))
    photo_uuid = str((existing or {}).get("photo_uuid") or _photo_uuid_from_sample(evidence_sample))
    bbox = _region_dict(getattr(evidence_sample, "region", None))
    crop_path = str((existing or {}).get("crop_path") or "")
    content_sha256 = ""
    quality_flags: list[str] = []
    if not crop_path and evidence_sample.asset_path:
        persisted = persist_evidence_crop(
            evidence_sample,
            _staging_sample_path(
                photo_uuid=photo_uuid,
                object_ref_id=object_ref_id,
                sample_uuid=sample_uuid,
            ),
            assume_source_is_crop=_asset_is_already_region_capture(evidence_sample.asset_path, None),
        )
        if persisted is not None:
            crop_path = persisted.crop_path
            content_sha256 = persisted.content_sha256
        else:
            quality_flags.append("crop_persist_failed")

    now_ms = _now_ms()
    sample = ObjectSampleRecord(
        sample_uuid=sample_uuid,
        object_uuid=object_uuid,
        photo_uuid=photo_uuid,
        object_ref_id=object_ref_id,
        crop_path=crop_path,
        source_asset_path=str(evidence_sample.asset_path or ""),
        bbox=bbox,
        content_sha256=content_sha256,
        evidence_id=evidence_sample.evidence_id,
        label=description[:120],
        category=category,
        quality_flags=quality_flags,
        review_status="needs_review",
        created_by=f"identify_object_{match_source}",
        created_at_ms=now_ms,
        updated_at_ms=now_ms,
        meta={"schema": "vision_object_sample_candidate_v1"},
    )
    _append_jsonl(_catalog_file("object_samples.jsonl"), sample.as_json())
    edge_result = _record_photo_object_edge(
        photo_uuid=photo_uuid,
        object_uuid=object_uuid,
        sample=sample,
        object_ref_id=object_ref_id,
        match_source=match_source,
        match_confidence=match_confidence,
        edge_status="candidate",
        review_status="needs_review",
    )
    return {
        "action": "vision.object_discovery.candidate_match",
        "success": True,
        "sample": sample.as_json(),
        "edge": edge_result.get("edge", {}),
        "l2b_edge_written": bool(edge_result.get("l2b_edge_written")),
        "audit": _audit_base(),
    }


def list_object_samples(
    *,
    object_uuid: str = "",
    review_status: str = "",
    accepted_only: bool = False,
) -> list[dict[str, Any]]:
    """Read object sample catalog rows for resolver/export code."""
    rows = _read_jsonl(_catalog_file("object_samples.jsonl"))
    if object_uuid:
        rows = [row for row in rows if str(row.get("object_uuid") or "") == object_uuid]
    if accepted_only:
        rows = [row for row in rows if str(row.get("review_status") or "") == "accepted"]
    elif review_status:
        rows = [row for row in rows if str(row.get("review_status") or "") == review_status]
    return rows


def list_photo_object_edges(
    *,
    photo_uuid: str = "",
    object_uuid: str = "",
) -> list[dict[str, Any]]:
    """Read PhotoNode/ObjectNode evidence edge catalog rows."""
    rows = _read_jsonl(_catalog_file("photo_object_edges.jsonl"))
    if photo_uuid:
        rows = [row for row in rows if str(row.get("photo_uuid") or "") == photo_uuid]
    if object_uuid:
        rows = [row for row in rows if str(row.get("object_uuid") or "") == object_uuid]
    return rows


def reject_object_sample_draft(
    *,
    object_ref_id: str = "",
    sample_uuid: str = "",
    reason: str = "",
    reviewer: str = "user",
) -> dict[str, Any]:
    """Mark a draft sample as rejected without touching object identity.

    JSONL rows are append-only, so this writes a newer row for the same
    PhotoObject/ObjectSample ids instead of mutating the original draft. That
    keeps the review trail intact while making latest-record lookups resolve to
    ``rejected``.
    """
    draft_object = _find_photo_object_by_ref(object_ref_id) if object_ref_id else None
    draft_sample = _find_sample_by_uuid(sample_uuid) if sample_uuid else None
    if draft_sample is None and draft_object is not None:
        draft_sample = _find_sample_by_uuid(str(draft_object.get("sample_draft_id") or ""))
    if draft_object is None and draft_sample is not None:
        draft_object = _find_photo_object_by_sample_uuid(str(draft_sample.get("sample_uuid") or ""))
    if draft_object is None or draft_sample is None:
        return {
            "action": "vision.object_discovery.reject_draft",
            "success": False,
            "error": "draft_not_found",
        }

    current_status = str(draft_sample.get("review_status") or "")
    if current_status == "accepted":
        return {
            "action": "vision.object_discovery.reject_draft",
            "success": False,
            "error": "sample_already_accepted",
            "sample": draft_sample,
        }
    if current_status == "rejected":
        return {
            "action": "vision.object_discovery.reject_draft",
            "success": True,
            "idempotent": True,
            "photo_object": draft_object,
            "sample": draft_sample,
            "audit": _audit_base(),
        }

    now_ms = _now_ms()
    updated_object = {
        **draft_object,
        "review_status": "rejected",
        "updated_at_ms": now_ms,
        "meta": {
            **_dict_or_empty(draft_object.get("meta")),
            "review": _review_meta(reason=reason, reviewer=reviewer, status="rejected"),
        },
    }
    updated_sample = {
        **draft_sample,
        "review_status": "rejected",
        "updated_at_ms": now_ms,
        "meta": {
            **_dict_or_empty(draft_sample.get("meta")),
            "review": _review_meta(reason=reason, reviewer=reviewer, status="rejected"),
        },
    }
    # Rejection is review state only. Do not write ObjectNode, L2-B edge, or
    # IdentityRefIndex entries here.
    _append_jsonl(_catalog_file("photo_objects.jsonl"), updated_object)
    _append_jsonl(_catalog_file("object_samples.jsonl"), updated_sample)
    manifest_path = _staging_manifest_path(
        photo_uuid=str(updated_object.get("photo_uuid") or ""),
        object_ref_id=str(updated_object.get("object_ref_id") or ""),
    )
    _patch_staging_manifest(
        manifest_path,
        photo_object=updated_object,
        sample=updated_sample,
        review_status="rejected",
    )
    return {
        "action": "vision.object_discovery.reject_draft",
        "success": True,
        "photo_object": updated_object,
        "sample": updated_sample,
        "manifest_path": str(manifest_path),
        "audit": {
            **_audit_base(),
            "identity_binding": "rejected_draft_no_object_identity",
        },
    }


def write_same_object_report(report: dict[str, Any]) -> str:
    """Persist a SameObjectResolutionReport and return its disk path."""
    job_uuid = str(report.get("job_uuid") or _new_prefixed_id("job"))
    yyyy, mm, dd = _day_parts()
    path = (
        vision_root()
        / "reports"
        / "same_object"
        / yyyy
        / mm
        / dd
        / f"{_safe_path_segment(job_uuid)}.json"
    )
    body = {
        "schema_version": SCHEMA_VERSION,
        **report,
        "job_uuid": job_uuid,
        "report_path": str(path),
        "updated_at_ms": _now_ms(),
    }
    _write_json(path, body)
    return str(path)


def _record_photo_object_edge(
    *,
    photo_uuid: str,
    object_uuid: str,
    sample: ObjectSampleRecord,
    object_ref_id: str,
    match_source: str,
    match_confidence: float,
    edge_status: str,
    review_status: str,
) -> dict[str, Any]:
    now_ms = _now_ms()
    edge = PhotoObjectEdgeRecord(
        edge_uuid=_new_prefixed_id("pe"),
        photo_uuid=photo_uuid,
        object_uuid=object_uuid,
        sample_uuid=sample.sample_uuid,
        evidence_id=sample.evidence_id,
        bbox=sample.bbox,
        crop_path=sample.crop_path,
        object_ref_id=object_ref_id,
        match_confidence=float(match_confidence or 0.0),
        match_source=match_source,
        edge_status=edge_status,
        review_status=review_status,
        created_at_ms=now_ms,
        updated_at_ms=now_ms,
        meta={"schema": "vision_photo_object_edge_v1"},
    )
    _append_jsonl(_catalog_file("photo_object_edges.jsonl"), edge.as_json())
    return {
        "edge": edge.as_json(),
        "l2b_edge_written": _write_l2b_photo_object_edge(edge),
    }


def _write_l2b_photo_object_edge(edge: PhotoObjectEdgeRecord) -> bool:
    if not edge.photo_uuid or not edge.object_uuid:
        return False
    try:
        from parrot.dsg.l2b_graph import get_l2b_graph
        from parrot.dsg.l2b_types import EdgeKind, SemanticEdge

        graph = get_l2b_graph()
        if graph.get_node(edge.photo_uuid) is None or graph.get_node(edge.object_uuid) is None:
            return False
        return graph.connect(
            edge.photo_uuid,
            edge.object_uuid,
            SemanticEdge(
                kind=EdgeKind.CANDIDATE_SUBJECT,
                strength=min(1.0, max(0.1, edge.match_confidence or 0.5)),
                source="vision.object_discovery",
                ref_ids=tuple(
                    item
                    for item in (edge.sample_uuid, edge.evidence_id, edge.object_ref_id)
                    if item
                ),
                meta=edge.as_json(),
            ),
        )
    except Exception:
        logger.debug("object_discovery: L2-B edge write skipped", exc_info=True)
        return False


def _update_l2b_object_profile(
    *,
    object_uuid: str,
    description: str,
    category: str,
    sample: ObjectSampleRecord,
    edge: dict[str, Any],
) -> None:
    try:
        from parrot.dsg.l2b_graph import get_l2b_graph

        node = get_l2b_graph().get_node(object_uuid)
        if node is None:
            return
        if sample.crop_path and not node.reference_image_path:
            node.reference_image_path = sample.crop_path
        if sample.source_asset_path:
            node.last_sighting_path = sample.source_asset_path
        profile = dict(node.meta.get("object_profile") or {})
        find_tags = list(profile.get("find_tags") or [])
        for tag in (category, description):
            tag = str(tag or "").strip()
            if tag and tag not in find_tags:
                find_tags.append(tag)
        report_refs = list(profile.get("object_report_ref_ids") or [])
        sample_index_ref = str(_object_sample_manifest_path(object_uuid))
        photo_edge_refs = list(profile.get("photo_edge_refs") or [])
        edge_uuid = str(edge.get("edge_uuid") or "")
        if edge_uuid and edge_uuid not in photo_edge_refs:
            photo_edge_refs.append(edge_uuid)
        profile.update(
            {
                "description_index": description,
                "find_tags": find_tags[:12],
                "object_report_ref_ids": report_refs,
                "object_report_paths": list(profile.get("object_report_paths") or []),
                "sample_index_ref": sample_index_ref,
                "primary_sample_id": profile.get("primary_sample_id") or sample.sample_uuid,
                "photo_edge_refs": photo_edge_refs,
                "updated_at_ms": _now_ms(),
            }
        )
        node.meta["object_profile"] = profile
    except Exception:
        logger.debug("object_discovery: object profile update skipped", exc_info=True)


def _bind_identity_ref_index(
    *,
    object_uuid: str,
    description: str,
    category: str,
    sample: ObjectSampleRecord,
    confidence: float,
) -> dict[str, Any]:
    try:
        from parrot.dsg.identity_ref_index import MemoryIdentityRefIndex

        index = MemoryIdentityRefIndex()
        payload = {
            "canonical_uuid": object_uuid if object_uuid.startswith("obj_") else "",
            "l2b_uuid": object_uuid,
            "aliases": [item for item in (description, category) if item],
            "confidence": float(confidence or 0.9),
            "resolution_state": "confirmed",
            "ref_id": sample.sample_uuid,
            "kind": "object_sample",
            "locators": [item for item in (sample.crop_path, sample.source_asset_path) if item],
            "content_hash": sample.content_sha256,
            "mime_type": "image/jpeg",
            "managed_by": "vision.object_discovery",
            "meta": {
                "sample_uuid": sample.sample_uuid,
                "photo_uuid": sample.photo_uuid,
                "object_ref_id": sample.object_ref_id,
            },
        }
        identity, ref = index.upsert(payload)
        index.save()
        return {
            "identity": identity.to_dict(),
            "ref": ref.to_dict() if ref is not None else {},
            "report": dict(index.last_upsert_report),
        }
    except Exception:
        logger.debug("object_discovery: IdentityRefIndex bind skipped", exc_info=True)
        return {}


def _bind_l1_5_refs(*, object_uuid: str, sample: ObjectSampleRecord) -> list[dict[str, Any]]:
    bindings: list[dict[str, Any]] = []
    try:
        from parrot.dsg.l1_5 import get_l1_5_pool
        from parrot.dsg.l1_5.ref_table import RefKind

        pool = get_l1_5_pool()
        if sample.crop_path:
            binding = pool.bind_ref(object_uuid, RefKind.PHOTO_PATH, sample.crop_path)
            bindings.append(
                {
                    "node_uuid": binding.node_uuid,
                    "kind": binding.kind.value,
                    "ref_value": binding.ref_value,
                }
            )
        binding = pool.bind_ref(object_uuid, RefKind.OTHER, sample.sample_uuid)
        bindings.append(
            {
                "node_uuid": binding.node_uuid,
                "kind": binding.kind.value,
                "ref_value": binding.ref_value,
            }
        )
    except Exception:
        logger.debug("object_discovery: L1.5 ref bind skipped", exc_info=True)
    return bindings


def _create_object_analysis_report(object_uuid: str) -> dict[str, Any]:
    try:
        from parrot.brain.vision.object_analysis import create_object_analysis_report

        return create_object_analysis_report(object_uuid=object_uuid)
    except Exception:
        logger.debug("object_discovery: object analysis report skipped", exc_info=True)
        return {}


def _write_staging_manifest(photo_object: PhotoObjectRecord, sample: ObjectSampleRecord) -> Path:
    manifest_path = _staging_manifest_path(
        photo_uuid=photo_object.photo_uuid,
        object_ref_id=photo_object.object_ref_id,
    )
    _write_json(
        manifest_path,
        {
            "schema_version": SCHEMA_VERSION,
            "photo_object": photo_object.as_json(),
            "sample": sample.as_json(),
            "updated_at_ms": _now_ms(),
        },
    )
    return manifest_path


def _patch_staging_manifest(path: Path, **updates: Any) -> None:
    body = _read_json(path)
    if not body:
        return
    body.update(updates)
    body["updated_at_ms"] = _now_ms()
    _write_json(path, body)


def _stage_object_sample_draft(
    *,
    photo_object: PhotoObjectRecord,
    sample: ObjectSampleRecord,
    manifest_path: Path,
) -> str:
    async def _stage() -> str:
        from parrot.brain.intent_workspace import (
            PayloadSource,
            StagedRefKind,
            StagedRefMetadata,
            StagedRefRequest,
            get_intent_workspace,
        )

        handle = await get_intent_workspace().stage(
            StagedRefRequest(
                kind=StagedRefKind.RICH_REPORT,
                payload_source=PayloadSource.DISK_PATH,
                payload_value=manifest_path,
                metadata=StagedRefMetadata(
                    origin="vision.object_discovery",
                    kind=StagedRefKind.RICH_REPORT,
                    payload_source=PayloadSource.DISK_PATH,
                    related_node_uuid=photo_object.photo_uuid,
                    size_bytes=manifest_path.stat().st_size if manifest_path.is_file() else 0,
                    custom_meta={
                        "role": "object_sample_draft",
                        "photo_id": photo_object.photo_uuid,
                        "object_ref_id": photo_object.object_ref_id,
                        "sample_uuid": sample.sample_uuid,
                        "source": photo_object.source,
                        "manifest_path": str(manifest_path),
                        "crop_path": sample.crop_path,
                        "review_status": sample.review_status,
                        "ui_kind": "paper_note",
                        "workspace_id": "workdesk",
                    },
                ),
            )
        )
        return handle.ref_id

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_stage())

    def _finish_stage(done: asyncio.Task[str]) -> None:
        if done.cancelled():
            return
        try:
            ref_id = done.result()
        except Exception:
            logger.debug("object_discovery: object sample draft stage failed", exc_info=True)
            return
        _patch_staging_manifest(manifest_path, intent_workspace_ref_id=ref_id)

    task = loop.create_task(_stage())
    task.add_done_callback(_finish_stage)
    return ""


def _write_object_sample_manifest(object_uuid: str, sample: ObjectSampleRecord) -> None:
    path = _object_sample_manifest_path(object_uuid)
    current = _read_json(path)
    samples = list(current.get("samples") or [])
    samples = [item for item in samples if str(item.get("sample_uuid") or "") != sample.sample_uuid]
    samples.append(sample.as_json())
    _write_json(
        path,
        {
            "schema_version": SCHEMA_VERSION,
            "object_uuid": object_uuid,
            "samples": samples,
            "updated_at_ms": _now_ms(),
        },
    )


def _catalog_file(name: str) -> Path:
    return vision_root() / "catalog" / name


def _staging_sample_path(*, photo_uuid: str, object_ref_id: str, sample_uuid: str) -> Path:
    yyyy, mm, dd = _day_parts()
    photo_part = _safe_path_segment(photo_uuid or "unbound_photo")
    return (
        vision_root()
        / "object_sample_staging"
        / yyyy
        / mm
        / dd
        / photo_part
        / _safe_path_segment(object_ref_id)
        / f"{_safe_path_segment(sample_uuid)}.jpg"
    )


def _staging_manifest_path(*, photo_uuid: str, object_ref_id: str) -> Path:
    path = _staging_sample_path(
        photo_uuid=photo_uuid,
        object_ref_id=object_ref_id,
        sample_uuid="manifest",
    )
    return path.with_name("manifest.json")


def _accepted_sample_path(*, object_uuid: str, sample_uuid: str) -> Path:
    return (
        vision_root()
        / "object_samples"
        / "by_object"
        / _safe_path_segment(object_uuid[:2] or "un")
        / _safe_path_segment(object_uuid)
        / "accepted"
        / f"{_safe_path_segment(sample_uuid)}.jpg"
    )


def _object_sample_manifest_path(object_uuid: str) -> Path:
    return (
        vision_root()
        / "object_samples"
        / "by_object"
        / _safe_path_segment(object_uuid[:2] or "un")
        / _safe_path_segment(object_uuid)
        / "manifest.json"
    )


def _find_existing_draft(*, evidence_id: str, tool_event_id: str) -> dict[str, Any] | None:
    return _find_jsonl_record(
        _catalog_file("photo_objects.jsonl"),
        lambda row: bool(
            (tool_event_id and str(row.get("tool_event_id") or "") == tool_event_id)
            or (evidence_id and str(row.get("evidence_id") or "") == evidence_id)
        ),
    )


def _find_draft_by_evidence(evidence_id: str) -> dict[str, Any] | None:
    if not evidence_id:
        return None
    return _find_jsonl_record(
        _catalog_file("photo_objects.jsonl"),
        lambda row: str(row.get("evidence_id") or "") == evidence_id,
    )


def _find_photo_object_by_ref(object_ref_id: str) -> dict[str, Any] | None:
    if not object_ref_id:
        return None
    return _find_jsonl_record(
        _catalog_file("photo_objects.jsonl"),
        lambda row: str(row.get("object_ref_id") or "") == object_ref_id,
    )


def _find_photo_object_by_sample_uuid(sample_uuid: str) -> dict[str, Any] | None:
    if not sample_uuid:
        return None
    return _find_jsonl_record(
        _catalog_file("photo_objects.jsonl"),
        lambda row: str(row.get("sample_draft_id") or "") == sample_uuid,
    )


def _find_sample_by_uuid(sample_uuid: str) -> dict[str, Any] | None:
    if not sample_uuid:
        return None
    return _find_jsonl_record(
        _catalog_file("object_samples.jsonl"),
        lambda row: str(row.get("sample_uuid") or "") == sample_uuid,
    )


def _find_jsonl_record(path: Path, predicate: Any) -> dict[str, Any] | None:
    for row in reversed(_read_jsonl(path)):
        try:
            if predicate(row):
                return row
        except Exception:
            continue
    return None


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            value = json.loads(line)
            if isinstance(value, dict):
                rows.append(value)
    except (OSError, json.JSONDecodeError):
        return rows
    return rows


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
        fh.write("\n")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _review_meta(*, reason: str, reviewer: str, status: str) -> dict[str, Any]:
    return {
        "status": status,
        "reason": str(reason or "")[:500],
        "reviewer": str(reviewer or "user")[:120],
        "reviewed_at_ms": _now_ms(),
    }


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(f"{path.suffix}.tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def _copy_sample_file(source: str, target: str) -> bool:
    src = Path(source)
    dst = Path(target)
    if not src.is_file():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.resolve() == dst.resolve():
        return True
    shutil.copyfile(src, dst)
    return True


def _new_prefixed_id(prefix: str) -> str:
    factory = getattr(uuid_lib, "uuid7", None)
    value = factory() if callable(factory) else uuid_lib.uuid4()
    return f"{prefix}_{value.hex}"


def _now_ms() -> int:
    return int(time.time() * 1000)


def _day_parts() -> tuple[str, str, str]:
    text = time.strftime("%Y/%m/%d", time.gmtime())
    yyyy, mm, dd = text.split("/")
    return yyyy, mm, dd


def _sha256_file(path_text: str) -> str:
    if not path_text:
        return ""
    path = Path(path_text)
    if not path.is_file():
        return ""
    digest = hashlib.sha256()
    try:
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError:
        return ""
    return digest.hexdigest()


def _image_size(path_text: str) -> tuple[int, int]:
    if not path_text:
        return (0, 0)
    try:
        from PIL import Image

        with Image.open(path_text) as image:
            return int(image.width), int(image.height)
    except Exception:
        return (0, 0)


def _extract_photo_uuid(packet: Any, sample: TimeAlignedSampleRef) -> str:
    meta = _packet_meta(packet)
    for key in ("photo_uuid", "photo_id", "photo_node_uuid", "source_photo_id"):
        value = str(meta.get(key) or "").strip()
        if value:
            return value
    return _photo_uuid_from_sample(sample)


def _photo_uuid_from_sample(sample: TimeAlignedSampleRef) -> str:
    meta = dict(getattr(sample, "meta", {}) or {})
    for key in ("photo_uuid", "photo_id", "photo_node_uuid", "source_photo_id"):
        value = str(meta.get(key) or "").strip()
        if value:
            return value
    nested = meta.get("meta")
    if isinstance(nested, dict):
        for key in ("photo_uuid", "photo_id", "photo_node_uuid", "source_photo_id"):
            value = str(nested.get(key) or "").strip()
            if value:
                return value
    return ""


def _packet_meta(packet: Any) -> dict[str, Any]:
    meta = getattr(packet, "meta", {}) or {}
    return meta if isinstance(meta, dict) else {}


def _label_from_packet(packet: Any) -> str:
    meta = _packet_meta(packet)
    for key in ("sample_label", "label", "object_label"):
        value = str(meta.get(key) or "").strip()
        if value:
            return value
    return str(getattr(packet, "subject_hint", "") or getattr(packet, "label", "") or "").strip()


def _category_from_packet(packet: Any) -> str:
    meta = _packet_meta(packet)
    return str(meta.get("category") or meta.get("sample_category") or meta.get("sample_label") or "").strip()


def _asset_is_already_region_capture(asset_path: str, packet: Any | None) -> bool:
    if not asset_path:
        return False
    parts = {part.lower() for part in Path(asset_path).parts}
    if "visual_tools" in parts:
        return True
    meta = _packet_meta(packet) if packet is not None else {}
    capture = str(meta.get("asset_capture") or meta.get("asset_status") or "").lower()
    return "screen_region" in capture or "region_capture" in capture


def _region_dict(region: Any) -> dict[str, Any]:
    if region is None:
        return {}
    if isinstance(region, SampleRegion):
        return region.model_dump(mode="json")
    if hasattr(region, "model_dump"):
        try:
            return region.model_dump(mode="json")
        except Exception:
            pass
    out = {
        "x": float(getattr(region, "x", 0.0) or 0.0),
        "y": float(getattr(region, "y", 0.0) or 0.0),
        "width": float(getattr(region, "width", 0.0) or 0.0),
        "height": float(getattr(region, "height", 0.0) or 0.0),
        "coordinate_space": str(getattr(region, "coordinate_space", "") or "normalized"),
    }
    return out if out["width"] > 0 and out["height"] > 0 else {}


def _enum_value(value: Any) -> str:
    return str(getattr(value, "value", value) or "").strip()


def _safe_path_segment(value: str) -> str:
    text = "".join(ch if ch.isalnum() or ch in {"_", "-", "."} else "_" for ch in str(value or ""))
    return text.strip("._")[:160] or "unknown"


def _small_dict(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {
        str(key): item
        for key, item in value.items()
        if isinstance(item, (str, int, float, bool, type(None), list, dict))
    }


def _dict_or_empty(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _audit_base() -> dict[str, Any]:
    return {
        "schema": "VisionObjectDiscovery.backend_v1",
        "image_transport": "storage_path_only_no_inline_image_bytes",
        "photo_object_boundary": "draft_sample_not_confirmed_object_identity",
    }


__all__ = [
    "PhotoObjectEdgeRecord",
    "PhotoObjectRecord",
    "PhotoRecord",
    "ObjectSampleRecord",
    "accept_new_object_from_evidence",
    "list_object_samples",
    "list_photo_object_edges",
    "record_candidate_match_from_evidence",
    "record_photo_asset",
    "record_visual_tool_object_draft",
    "reject_object_sample_draft",
    "vision_root",
    "write_same_object_report",
]
