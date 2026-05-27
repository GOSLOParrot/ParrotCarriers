"""A10/CV detection import helpers for object discovery.

This module turns storage-backed ``SensorFrame`` detections into reviewable
PhotoObject/ObjectSample drafts. It does not write L2-B Object identity and it
does not accept samples automatically.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from parrot.brain.vision.evidence import EvidenceKind, SampleRegion, get_evidence_ledger
from parrot.brain.vision.object_discovery import record_visual_tool_object_draft
from parrot.dsg.l1_5_protocol import Detection, SensorFrame


def record_a10_detections_as_sample_drafts(
    frame: SensorFrame,
    *,
    photo_id: str = "",
    mime_type: str = "image/jpeg",
) -> dict[str, Any]:
    """Create reviewable sample drafts from A10 detections on a frame asset."""
    asset_path = str(frame.frame_ref or "").strip()
    resolved_photo_id = str(photo_id or frame.meta.get("photo_id") or frame.frame_uuid)
    if not asset_path:
        return {
            "action": "vision.a10_import.detections_to_drafts",
            "success": False,
            "error": "missing_frame_ref",
            "draft_count": 0,
        }

    drafts: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for det in frame.detections:
        region = _region_from_detection(det)
        if region is None:
            skipped.append({"det_id": det.det_id, "reason": "missing_bbox"})
            continue
        sample = get_evidence_ledger().record_sample(
            kind=EvidenceKind.IMAGE_ASSET,
            asset_path=asset_path,
            mime_type=mime_type,
            region=region,
            related_refs=(resolved_photo_id,),
            description=f"A10 detection {det.label}",
            meta={
                "source": "a10_detection",
                "photo_id": resolved_photo_id,
                "frame_uuid": frame.frame_uuid,
                "frame_ref": asset_path,
                "det_id": det.det_id,
                "track_id": det.track_id,
                "reid_hash": det.reid_hash,
                "authority": det.authority.value,
                "confidence": det.confidence,
                "detection_meta": dict(det.meta),
            },
        )
        packet = SimpleNamespace(
            tool_kind="bbox",
            interaction_phase="confirm",
            tool_event_id=f"a10:{frame.frame_uuid}:{det.det_id}",
            tool_id=f"a10_{det.det_id}",
            attention_hint=det.confidence,
            source_surface="a10_cv",
            subject_hint=det.label,
            label=det.label,
            asset_path=asset_path,
            region=region,
            meta={
                "photo_id": resolved_photo_id,
                "sample_label": det.label,
                "sample_category": str(det.meta.get("category") or det.label),
                "sample_source": "a10_detection",
                "frame_uuid": frame.frame_uuid,
                "det_id": det.det_id,
                "track_id": det.track_id,
                "reid_hash": det.reid_hash,
                "authority": det.authority.value,
                "confidence": det.confidence,
                "detection_meta": dict(det.meta),
            },
        )
        result = record_visual_tool_object_draft(packet=packet, sample=sample, ref_id=f"a10:{det.det_id}")
        if result:
            drafts.append(result)

    return {
        "action": "vision.a10_import.detections_to_drafts",
        "success": True,
        "photo_id": resolved_photo_id,
        "frame_uuid": frame.frame_uuid,
        "draft_count": len(drafts),
        "skipped_count": len(skipped),
        "drafts": drafts,
        "skipped": skipped,
        "audit": {
            "identity_binding": "draft_only_no_object_identity",
            "source": "a10_detection",
            "image_transport": "storage_path_only_no_inline_image_bytes",
        },
    }


def _region_from_detection(det: Detection) -> SampleRegion | None:
    bbox = det.bbox
    if bbox is None:
        return None
    return SampleRegion(
        x=float(bbox.x1),
        y=float(bbox.y1),
        width=float(bbox.width()),
        height=float(bbox.height()),
        coordinate_space="normalized",
    )


__all__ = ["record_a10_detections_as_sample_drafts"]
