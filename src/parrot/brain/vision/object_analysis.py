"""Object-level report/index generation for findObject.

Object reports summarize accepted samples and photo-object evidence edges for
an existing ObjectNode. They are pointers and indexes, not identity truth:
identity remains in ObjectNode + accepted ObjectSample + edge manifests.
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid as uuid_lib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from parrot.brain.vision.object_discovery import (
    list_object_samples,
    list_photo_object_edges,
    vision_root,
)

SCHEMA_VERSION = "object_analysis_v1"


@dataclass(frozen=True)
class ObjectAnalysisReport:
    schema_version: str = SCHEMA_VERSION
    report_uuid: str = field(default_factory=lambda: _new_prefixed_id("rep"))
    object_uuid: str = ""
    label: str = ""
    category: str = ""
    description_index: str = ""
    find_tags: list[str] = field(default_factory=list)
    reference_image_path: str = ""
    last_sighting_path: str = ""
    sample_index_ref: str = ""
    accepted_samples: list[dict[str, Any]] = field(default_factory=list)
    photo_edges: list[dict[str, Any]] = field(default_factory=list)
    graphiti_search_ref: str = ""
    web_research_ref: str = ""
    quality_flags: list[str] = field(default_factory=list)
    report_ref_id: str = ""
    report_path: str = ""
    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    updated_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    audit: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


def create_object_analysis_report(
    *,
    object_uuid: str,
    stage_intent_workspace: bool = True,
) -> dict[str, Any]:
    """Create an object-level report from accepted samples and evidence edges."""
    object_uuid = str(object_uuid or "").strip()
    if not object_uuid:
        return {"action": "vision.object_analysis.create", "success": False, "error": "missing_object_uuid"}

    node = _object_node(object_uuid)
    profile = dict(getattr(node, "meta", {}).get("object_profile") or {}) if node is not None else {}
    samples = list_object_samples(object_uuid=object_uuid, accepted_only=True)
    edges = list_photo_object_edges(object_uuid=object_uuid)
    sample_index_ref = str(
        vision_root()
        / "object_samples"
        / "by_object"
        / _safe_path_segment(object_uuid[:2] or "un")
        / _safe_path_segment(object_uuid)
        / "manifest.json"
    )
    report = ObjectAnalysisReport(
        object_uuid=object_uuid,
        label=str(getattr(node, "label", "") or _first_nonempty(samples, "label") or object_uuid),
        category=str(getattr(node, "category", "") or _first_nonempty(samples, "category") or ""),
        description_index=str(profile.get("description_index") or ""),
        find_tags=list(profile.get("find_tags") or []),
        reference_image_path=str(getattr(node, "reference_image_path", "") or ""),
        last_sighting_path=str(getattr(node, "last_sighting_path", "") or ""),
        sample_index_ref=sample_index_ref,
        accepted_samples=[_sample_summary(sample) for sample in samples],
        photo_edges=[_edge_summary(edge) for edge in edges],
        quality_flags=_quality_flags(samples=samples, edges=edges),
        audit={
            "schema": "ObjectAnalysisReport.backend_v1",
            "identity_binding": "report_index_only_no_identity_mutation",
            "accepted_samples_only": True,
        },
    )
    report_path = _write_report(report.as_json())
    report_ref_id = ""
    if stage_intent_workspace:
        report_ref_id = _stage_report_for_intent_workspace(
            object_uuid=object_uuid,
            report_path=report_path,
            size_bytes=Path(report_path).stat().st_size if Path(report_path).is_file() else 0,
        )
    if report_ref_id:
        _patch_report(report_path, report_ref_id=report_ref_id)
    _update_object_profile_report_ref(
        object_uuid=object_uuid,
        report_path=report_path,
        report_ref_id=report_ref_id,
        sample_index_ref=sample_index_ref,
    )
    return {
        "action": "vision.object_analysis.create",
        "success": True,
        "object_uuid": object_uuid,
        "report_uuid": report.report_uuid,
        "report_path": report_path,
        "report_ref_id": report_ref_id,
        "sample_count": len(samples),
        "edge_count": len(edges),
        "report": {**report.as_json(), "report_path": report_path, "report_ref_id": report_ref_id},
    }


def _write_report(report: dict[str, Any]) -> str:
    object_uuid = str(report.get("object_uuid") or "unknown_object")
    report_uuid = str(report.get("report_uuid") or _new_prefixed_id("rep"))
    path = (
        vision_root()
        / "reports"
        / "object"
        / _safe_path_segment(object_uuid[:2] or "un")
        / _safe_path_segment(object_uuid)
        / f"{_safe_path_segment(report_uuid)}.json"
    )
    body = {
        **report,
        "report_uuid": report_uuid,
        "report_path": str(path),
        "updated_at_ms": int(time.time() * 1000),
    }
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


def _stage_report_for_intent_workspace(*, object_uuid: str, report_path: str, size_bytes: int) -> str:
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
                    origin="vision.object_analysis",
                    kind=StagedRefKind.RICH_REPORT,
                    payload_source=PayloadSource.DISK_PATH,
                    related_node_uuid=object_uuid,
                    size_bytes=size_bytes,
                    custom_meta={
                        "role": "object_analysis_report",
                        "object_uuid": object_uuid,
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
        _patch_report(report_path, report_ref_id=ref_id)
        _update_object_profile_report_ref(
            object_uuid=object_uuid,
            report_path=report_path,
            report_ref_id=ref_id,
        )

    task = loop.create_task(_stage())
    task.add_done_callback(_finish_stage)
    return ""


def _update_object_profile_report_ref(
    *,
    object_uuid: str,
    report_path: str,
    report_ref_id: str,
    sample_index_ref: str = "",
) -> None:
    node = _object_node(object_uuid)
    if node is None:
        return
    meta = dict(getattr(node, "meta", {}) or {})
    profile = dict(meta.get("object_profile") or {})
    paths = list(profile.get("object_report_paths") or [])
    refs = list(profile.get("object_report_ref_ids") or [])
    if report_path and report_path not in paths:
        paths.append(report_path)
    if report_ref_id and report_ref_id not in refs:
        refs.append(report_ref_id)
    profile["object_report_paths"] = paths[-10:]
    profile["object_report_ref_ids"] = refs[-10:]
    if sample_index_ref:
        profile["sample_index_ref"] = sample_index_ref
    profile["updated_at_ms"] = int(time.time() * 1000)
    meta["object_profile"] = profile
    node.meta = meta


def _object_node(object_uuid: str) -> Any | None:
    try:
        from parrot.dsg.l2b_graph import get_l2b_graph

        return get_l2b_graph().get_node(object_uuid)
    except Exception:
        return None


def _sample_summary(sample: dict[str, Any]) -> dict[str, Any]:
    return {
        "sample_uuid": str(sample.get("sample_uuid") or ""),
        "photo_uuid": str(sample.get("photo_uuid") or ""),
        "object_ref_id": str(sample.get("object_ref_id") or ""),
        "crop_path": str(sample.get("crop_path") or ""),
        "source_asset_path": str(sample.get("source_asset_path") or ""),
        "bbox": dict(sample.get("bbox") or {}),
        "content_sha256": str(sample.get("content_sha256") or ""),
        "label": str(sample.get("label") or ""),
        "category": str(sample.get("category") or ""),
        "quality_flags": list(sample.get("quality_flags") or []),
        "review_status": str(sample.get("review_status") or ""),
    }


def _edge_summary(edge: dict[str, Any]) -> dict[str, Any]:
    return {
        "edge_uuid": str(edge.get("edge_uuid") or ""),
        "photo_uuid": str(edge.get("photo_uuid") or ""),
        "object_uuid": str(edge.get("object_uuid") or ""),
        "sample_uuid": str(edge.get("sample_uuid") or ""),
        "evidence_id": str(edge.get("evidence_id") or ""),
        "bbox": dict(edge.get("bbox") or {}),
        "crop_path": str(edge.get("crop_path") or ""),
        "object_ref_id": str(edge.get("object_ref_id") or ""),
        "match_confidence": float(edge.get("match_confidence") or 0.0),
        "match_source": str(edge.get("match_source") or ""),
        "edge_status": str(edge.get("edge_status") or ""),
        "review_status": str(edge.get("review_status") or ""),
    }


def _quality_flags(*, samples: list[dict[str, Any]], edges: list[dict[str, Any]]) -> list[str]:
    flags: list[str] = []
    if not samples:
        flags.append("no_accepted_samples")
    if not edges:
        flags.append("no_photo_edges")
    return flags


def _first_nonempty(rows: list[dict[str, Any]], key: str) -> str:
    for row in rows:
        value = str(row.get(key) or "").strip()
        if value:
            return value
    return ""


def _safe_path_segment(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "_" for ch in str(value or ""))[:160] or "item"


def _new_prefixed_id(prefix: str) -> str:
    factory = getattr(uuid_lib, "uuid7", None)
    value = factory() if callable(factory) else uuid_lib.uuid4()
    return f"{prefix}_{value.hex}"


__all__ = ["ObjectAnalysisReport", "create_object_analysis_report"]
