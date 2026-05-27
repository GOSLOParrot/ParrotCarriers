"""Photo-level analysis reports for the visual identity chain.

V1 deliberately stays at the photo layer: it writes a storage-backed report,
stages that report for IntentWorkspace, and adds a lightweight pointer to the
PhotoNode. It does not create ObjectNodes, accept samples, or make same-object
identity decisions.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image

from parrot.brain.vision.object_discovery import vision_root

SCHEMA_VERSION = "photo_analysis_v1"


@dataclass(frozen=True)
class PhotoAnalysisReport:
    schema_version: str = SCHEMA_VERSION
    photo_id: str = ""
    photo_node_uuid: str = ""
    asset_path: str = ""
    rendered_preview_path: str = ""
    evidence_id: str = ""
    scene_summary: str = ""
    content_summary: str = ""
    ocr_text: list[str] = field(default_factory=list)
    visible_logo_or_text: list[str] = field(default_factory=list)
    photo_level_brand_candidates: list[str] = field(default_factory=list)
    photo_level_web_research: list[dict[str, Any]] = field(default_factory=list)
    photo_level_graphiti_hits: list[dict[str, Any]] = field(default_factory=list)
    possible_object_mentions: list[dict[str, Any]] = field(default_factory=list)
    object_inventory_ref: str = ""
    nanobot_report_ref_id: str = ""
    nanobot_report_path: str = ""
    quality_flags: list[str] = field(default_factory=list)
    width: int = 0
    height: int = 0
    content_sha256: str = ""
    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    updated_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    audit: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


def create_photo_analysis_report(
    *,
    photo_id: str,
    asset_path: str,
    asset_ref: str = "",
    evidence_id: str = "",
    asset_bytes: int = 0,
    payload: dict[str, Any] | None = None,
    stage_intent_workspace: bool = True,
) -> dict[str, Any]:
    """Create and stage a photo-level report for a stored image asset."""
    photo_id = str(photo_id or "").strip()
    if not photo_id:
        return {"action": "vision.photo_analysis.create", "success": False, "error": "missing_photo_id"}

    asset_text = str(asset_path or asset_ref or "").strip()
    quality_flags: list[str] = []
    width = 0
    height = 0
    digest = ""
    if asset_text:
        path = Path(asset_text)
        if path.is_file():
            width, height = _image_size(path)
            digest = _sha256_file(path)
            if width <= 0 or height <= 0:
                quality_flags.append("image_size_unreadable")
        else:
            quality_flags.append("asset_path_not_local_file")
    else:
        quality_flags.append("missing_asset")

    payload_meta = dict(payload or {})
    report = PhotoAnalysisReport(
        photo_id=photo_id,
        photo_node_uuid=photo_id,
        asset_path=asset_text,
        evidence_id=str(evidence_id or ""),
        scene_summary=_scene_summary(width=width, height=height, asset_bytes=asset_bytes),
        content_summary="Photo asset recorded; semantic enrichment pending.",
        possible_object_mentions=_possible_mentions(payload_meta),
        quality_flags=quality_flags,
        width=width,
        height=height,
        content_sha256=digest,
        audit={
            "schema": "PhotoAnalysisReport.backend_v1",
            "identity_binding": "photo_level_only_no_object_identity",
            "image_transport": "storage_path_only_no_inline_image_bytes",
            "asset_ref": asset_ref,
        },
    )
    report_path = _write_report(report.as_json())
    ref_id = ""
    if stage_intent_workspace:
        ref_id = _stage_report_for_intent_workspace(
            photo_id=photo_id,
            report_path=report_path,
            size_bytes=Path(report_path).stat().st_size if Path(report_path).is_file() else 0,
            scene_summary=report.scene_summary,
            content_summary=report.content_summary,
        )
    if ref_id:
        _patch_report(report_path, nanobot_report_ref_id=ref_id)
    _update_photo_node_analysis(
        photo_id=photo_id,
        report_path=report_path,
        report_ref_id=ref_id,
        scene_summary=report.scene_summary,
        content_summary=report.content_summary,
    )
    return {
        "action": "vision.photo_analysis.create",
        "success": True,
        "report_path": report_path,
        "report_ref_id": ref_id,
        "report": {**report.as_json(), "nanobot_report_ref_id": ref_id, "nanobot_report_path": report_path},
    }


def _write_report(report: dict[str, Any]) -> str:
    photo_id = str(report.get("photo_id") or "unknown_photo")
    yyyy, mm, dd = time.strftime("%Y/%m/%d", time.gmtime()).split("/")
    path = (
        vision_root()
        / "photos"
        / "reports"
        / yyyy
        / mm
        / dd
        / f"{_safe_path_segment(photo_id)}.analysis.json"
    )
    body = {**report, "nanobot_report_path": str(path), "updated_at_ms": int(time.time() * 1000)}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8")
    return str(path)


def _patch_report(report_path: str, **updates: Any) -> None:
    path = Path(report_path)
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return
    body.update(updates)
    body["updated_at_ms"] = int(time.time() * 1000)
    path.write_text(json.dumps(body, ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8")


def _stage_report_for_intent_workspace(
    *,
    photo_id: str,
    report_path: str,
    size_bytes: int,
    scene_summary: str,
    content_summary: str,
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
                payload_value=Path(report_path),
                metadata=StagedRefMetadata(
                    origin="vision.photo_analysis",
                    kind=StagedRefKind.RICH_REPORT,
                    payload_source=PayloadSource.DISK_PATH,
                    related_node_uuid=photo_id,
                    size_bytes=size_bytes,
                    custom_meta={
                        "role": "photo_analysis_report",
                        "photo_id": photo_id,
                        "report_path": report_path,
                        "ui_kind": "paper_note",
                        "workspace_id": "report_desk",
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
            return
        _patch_report(report_path, nanobot_report_ref_id=ref_id)
        _update_photo_node_analysis(
            photo_id=photo_id,
            report_path=report_path,
            report_ref_id=ref_id,
            scene_summary=scene_summary,
            content_summary=content_summary,
        )

    task = loop.create_task(_stage())
    task.add_done_callback(_finish_stage)
    return ""


def _update_photo_node_analysis(
    *,
    photo_id: str,
    report_path: str,
    report_ref_id: str,
    scene_summary: str,
    content_summary: str,
) -> None:
    try:
        from parrot.dsg.l2b_graph import get_l2b_graph

        node = get_l2b_graph().get_node(photo_id)
    except Exception:
        return
    if node is None:
        return
    meta = dict(getattr(node, "meta", {}) or {})
    meta["photo_analysis"] = {
        "analysis_status": "ready",
        "analysis_version": SCHEMA_VERSION,
        "report_ref_id": report_ref_id,
        "report_path": report_path,
        "scene_summary": scene_summary,
        "content_summary": content_summary,
        "web_research_ref": "",
        "graphiti_search_ref": "",
        "object_inventory_ref": "",
        "updated_at_ms": int(time.time() * 1000),
    }
    node.meta = meta


def _scene_summary(*, width: int, height: int, asset_bytes: int) -> str:
    if width > 0 and height > 0:
        return f"Stored photo asset ({width}x{height}, {asset_bytes} bytes)."
    return f"Stored photo asset ({asset_bytes} bytes); dimensions pending."


def _possible_mentions(payload: dict[str, Any]) -> list[dict[str, Any]]:
    mentions: list[dict[str, Any]] = []
    for key, role in (("bbox_refs", "bbox_ref"), ("focus_refs", "focus_ref")):
        for value in payload.get(key) or ():
            ref = str(value or "").strip()
            if ref:
                mentions.append({"source": "photo_payload", "role": role, "ref_id": ref})
    candidate = str(payload.get("candidate_subject_uuid") or "").strip()
    if candidate:
        mentions.append({"source": "photo_payload", "role": "candidate_subject_uuid", "ref_id": candidate})
    return mentions


def _image_size(path: Path) -> tuple[int, int]:
    try:
        with Image.open(path) as image:
            return image.size
    except Exception:
        return (0, 0)


def _sha256_file(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return ""


def _safe_path_segment(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "_" for ch in value)[:160] or "item"


__all__ = ["PhotoAnalysisReport", "create_photo_analysis_report"]
