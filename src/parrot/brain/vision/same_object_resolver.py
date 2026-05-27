"""Same-object resolver for the findObject evidence chain.

This is the synchronous, worker-compatible core that GOSLO can await from
``identify_object``. A future nanobot worker can call the same function from a
background queue; V1 keeps it in-process so the evidence/report contract lands
without depending on the full nanobot runtime.
"""

from __future__ import annotations

import base64
import io
import time
import uuid as uuid_lib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image

from parrot.brain.vision.evidence import TimeAlignedSampleRef
from parrot.brain.vision.evidence_image import prepare_evidence_image
from parrot.brain.vision.object_discovery import (
    list_object_samples,
    list_photo_object_edges,
    write_same_object_report,
)

SCHEMA_VERSION = 1
STRONG_MATCH_CONFIDENCE = 0.75
AMBIGUOUS_MATCH_CONFIDENCE = 0.55
TEXT_CANDIDATE_FLOOR = 0.08


@dataclass(frozen=True)
class ResolverCandidate:
    object_uuid: str
    label: str
    category: str = ""
    text_score: float = 0.0
    reference_image_path: str = ""
    sample_ids: list[str] = field(default_factory=list)
    sample_paths: list[str] = field(default_factory=list)
    edge_refs: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ComparedSample:
    object_uuid: str
    sample_uuid: str
    reference_image_path: str
    label: str = ""
    compare_source: str = "vlm_same_object"
    compared: bool = False
    confidence: float = 0.0
    error: str = ""

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SameObjectResolutionReport:
    status: str
    target_evidence_id: str = ""
    target_photo_id: str = ""
    target_crop_path: str = ""
    photo_report_path: str = ""
    best_object_uuid: str = ""
    best_confidence: float = 0.0
    candidate_objects: list[dict[str, Any]] = field(default_factory=list)
    compared_samples: list[dict[str, Any]] = field(default_factory=list)
    reasoning_summary: str = ""
    recommended_action: str = "ask_user"
    job_uuid: str = field(default_factory=lambda: _new_prefixed_id("job"))
    report_path: str = ""
    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    audit: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return {"schema_version": SCHEMA_VERSION, **asdict(self)}


async def resolve_same_object(
    *,
    evidence_sample: TimeAlignedSampleRef | None,
    description: str,
    category: str = "",
    photo_id: str = "",
    object_ref_id: str = "",
    max_candidates: int = 5,
    enable_visual_compare: bool = True,
) -> dict[str, Any]:
    """Resolve whether the current evidence is an existing ObjectNode.

    The resolver scans ObjectNodes plus accepted object samples. Draft samples
    are deliberately ignored for strong matching.
    """
    if evidence_sample is None or not getattr(evidence_sample, "asset_path", ""):
        return _persist_report(
            SameObjectResolutionReport(
                status="no_evidence",
                target_evidence_id=str(getattr(evidence_sample, "evidence_id", "") or ""),
                target_photo_id=photo_id,
                reasoning_summary="No storage-backed target image was available.",
                recommended_action="need_better_crop",
                audit=_audit(),
            )
        )

    prepared = prepare_evidence_image(evidence_sample, max_dimension=720)
    if prepared is None:
        return _persist_report(
            SameObjectResolutionReport(
                status="no_evidence",
                target_evidence_id=evidence_sample.evidence_id,
                target_photo_id=photo_id or _photo_uuid_from_sample(evidence_sample),
                reasoning_summary="Target evidence asset could not be loaded.",
                recommended_action="need_better_crop",
                audit=_audit(),
            )
        )

    resolved_photo_id = photo_id or _photo_uuid_from_sample(evidence_sample)
    candidates = _rank_candidates(
        description=description,
        category=category,
        max_candidates=max_candidates,
    )
    if not candidates:
        return _persist_report(
            SameObjectResolutionReport(
                status="new_object",
                target_evidence_id=evidence_sample.evidence_id,
                target_photo_id=resolved_photo_id,
                target_crop_path=prepared.asset_path,
                reasoning_summary="No accepted object samples or ObjectNode candidates matched the current evidence.",
                recommended_action="save_new",
                audit=_audit(object_ref_id=object_ref_id),
            )
        )

    compared: list[ComparedSample] = []
    visual_candidates: list[dict[str, Any]] = []
    if enable_visual_compare:
        for candidate in candidates:
            reference_path = candidate.reference_image_path or (candidate.sample_paths[0] if candidate.sample_paths else "")
            b64 = _image_file_to_b64_jpeg(reference_path)
            compared.append(
                ComparedSample(
                    object_uuid=candidate.object_uuid,
                    sample_uuid=candidate.sample_ids[0] if candidate.sample_ids else "",
                    reference_image_path=reference_path,
                    label=candidate.label,
                    compared=bool(b64),
                    error="" if b64 else "missing_reference_image",
                )
            )
            if b64:
                visual_candidates.append(
                    {
                        "uuid": candidate.object_uuid,
                        "label": candidate.label,
                        "reference_image_b64": b64,
                    }
                )

    match_uuid = ""
    match_confidence = 0.0
    if visual_candidates:
        from parrot.brain.vision.visual_match import compare_current_frame

        visual_match = await compare_current_frame(prepared.b64_jpeg, visual_candidates)
        if visual_match is not None:
            match_uuid, match_confidence = visual_match

    compared = _stamp_visual_confidence(compared, match_uuid=match_uuid, confidence=match_confidence)
    top_candidate = candidates[0]
    best_uuid = match_uuid or top_candidate.object_uuid
    best_confidence = match_confidence if match_uuid else min(0.54, top_candidate.text_score)

    if match_uuid and match_confidence >= STRONG_MATCH_CONFIDENCE:
        status = "matched"
        recommended_action = "bind_existing"
        summary = f"VLM same-object comparison matched {match_uuid} at {match_confidence:.2f}."
    elif match_uuid and match_confidence >= AMBIGUOUS_MATCH_CONFIDENCE:
        status = "ambiguous"
        recommended_action = "ask_user"
        summary = f"VLM comparison found a possible match {match_uuid} at {match_confidence:.2f}."
    else:
        status = "ambiguous" if top_candidate.text_score >= 0.35 else "new_object"
        recommended_action = "ask_user" if status == "ambiguous" else "save_new"
        summary = (
            "Candidate scan produced text/sample candidates but no strong same-object visual match."
            if status == "ambiguous"
            else "No strong candidate survived same-object comparison."
        )

    return _persist_report(
        SameObjectResolutionReport(
            status=status,
            target_evidence_id=evidence_sample.evidence_id,
            target_photo_id=resolved_photo_id,
            target_crop_path=prepared.asset_path,
            best_object_uuid=best_uuid,
            best_confidence=round(best_confidence, 3),
            candidate_objects=[candidate.as_json() for candidate in candidates],
            compared_samples=[item.as_json() for item in compared],
            reasoning_summary=summary,
            recommended_action=recommended_action,
            audit=_audit(
                object_ref_id=object_ref_id,
                candidate_count=len(candidates),
                visual_candidate_count=len(visual_candidates),
            ),
        )
    )


def _rank_candidates(
    *,
    description: str,
    category: str,
    max_candidates: int,
) -> list[ResolverCandidate]:
    nodes = _object_nodes()
    accepted_samples = list_object_samples(accepted_only=True)
    samples_by_object: dict[str, list[dict[str, Any]]] = {}
    for sample in accepted_samples:
        object_uuid = str(sample.get("object_uuid") or "")
        if object_uuid:
            samples_by_object.setdefault(object_uuid, []).append(sample)

    object_ids = sorted({*nodes.keys(), *samples_by_object.keys()})
    candidates: list[ResolverCandidate] = []
    for object_uuid in object_ids:
        node = nodes.get(object_uuid)
        samples = samples_by_object.get(object_uuid, [])
        label = str(getattr(node, "label", "") or _first_nonempty(samples, "label") or object_uuid)
        node_category = str(getattr(node, "category", "") or _first_nonempty(samples, "category") or "")
        haystack_parts = [
            label,
            node_category,
            str(getattr(node, "description", "") or ""),
            " ".join(str(item) for item in getattr(node, "tags", []) or []),
            _object_profile_text(node),
            " ".join(str(sample.get("label") or "") for sample in samples),
            " ".join(str(sample.get("category") or "") for sample in samples),
        ]
        text_score, reasons = _score_text(
            query=" ".join(part for part in (description, category) if part),
            category=category,
            haystack=" ".join(haystack_parts),
        )
        if samples:
            text_score += 0.05
            reasons.append("has_accepted_sample")
        reference_image_path = str(getattr(node, "reference_image_path", "") or "")
        sample_paths = [
            str(sample.get("crop_path") or "")
            for sample in samples
            if str(sample.get("crop_path") or "")
        ]
        if not reference_image_path and sample_paths:
            reference_image_path = sample_paths[0]
        if reference_image_path:
            text_score += 0.03
            reasons.append("has_reference_image")
        if text_score < TEXT_CANDIDATE_FLOOR and not sample_paths and not reference_image_path:
            continue
        edges = list_photo_object_edges(object_uuid=object_uuid)
        candidates.append(
            ResolverCandidate(
                object_uuid=object_uuid,
                label=label,
                category=node_category,
                text_score=round(min(1.0, text_score), 3),
                reference_image_path=reference_image_path,
                sample_ids=[str(sample.get("sample_uuid") or "") for sample in samples],
                sample_paths=sample_paths,
                edge_refs=[str(edge.get("edge_uuid") or "") for edge in edges],
                reasons=reasons,
            )
        )

    candidates.sort(key=lambda item: (item.text_score, bool(item.reference_image_path)), reverse=True)
    return candidates[: max(1, min(max_candidates, 20))]


def _score_text(*, query: str, category: str, haystack: str) -> tuple[float, list[str]]:
    query_tokens = _tokens(query)
    haystack_tokens = _tokens(haystack)
    if not query_tokens or not haystack_tokens:
        return (0.0, [])
    overlap = query_tokens & haystack_tokens
    score = len(overlap) / max(1, len(query_tokens))
    reasons: list[str] = []
    if overlap:
        reasons.append("text_overlap:" + ",".join(sorted(overlap)[:6]))
    category_token = str(category or "").strip().lower()
    if category_token and category_token in haystack_tokens:
        score += 0.15
        reasons.append("category_match")
    if query.strip().lower() and query.strip().lower() in haystack.lower():
        score = max(score, 0.8)
        reasons.append("phrase_match")
    return min(1.0, score), reasons


def _tokens(text: str) -> set[str]:
    normalized = []
    for ch in str(text or "").lower():
        normalized.append(ch if ch.isalnum() else " ")
    return {token for token in "".join(normalized).split() if len(token) >= 2}


def _object_nodes() -> dict[str, Any]:
    try:
        from parrot.dsg.l2b_graph import get_l2b_graph
        from parrot.dsg.l2b_types import ConfirmationStatus, NodeKind

        graph = get_l2b_graph()
        nodes = {}
        for node in graph.all_nodes():
            if node.kind != NodeKind.OBJECT:
                continue
            if node.confirmation == ConfirmationStatus.GHOST:
                continue
            nodes[node.uuid] = node
        return nodes
    except Exception:
        return {}


def _object_profile_text(node: Any) -> str:
    profile = dict(getattr(node, "meta", {}).get("object_profile") or {}) if node is not None else {}
    parts = [
        str(profile.get("description_index") or ""),
        " ".join(str(item) for item in profile.get("find_tags") or []),
    ]
    return " ".join(parts)


def _first_nonempty(rows: list[dict[str, Any]], key: str) -> str:
    for row in rows:
        value = str(row.get(key) or "").strip()
        if value:
            return value
    return ""


def _stamp_visual_confidence(
    compared: list[ComparedSample],
    *,
    match_uuid: str,
    confidence: float,
) -> list[ComparedSample]:
    if not match_uuid:
        return compared
    out: list[ComparedSample] = []
    for item in compared:
        if item.object_uuid != match_uuid:
            out.append(item)
            continue
        out.append(
            ComparedSample(
                object_uuid=item.object_uuid,
                sample_uuid=item.sample_uuid,
                reference_image_path=item.reference_image_path,
                label=item.label,
                compare_source=item.compare_source,
                compared=item.compared,
                confidence=float(confidence or 0.0),
                error=item.error,
            )
        )
    return out


def _image_file_to_b64_jpeg(path_text: str, *, max_dimension: int = 720) -> str:
    if not path_text:
        return ""
    path = Path(path_text)
    if not path.is_file():
        return ""
    try:
        with Image.open(path) as opened:
            image = opened.convert("RGB")
        if max_dimension and max(image.size) > max_dimension:
            scale = max_dimension / float(max(image.size))
            size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
            resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.BICUBIC)
            image = image.resize(size, resample)
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=84)
        return base64.b64encode(output.getvalue()).decode("ascii")
    except Exception:
        return ""


def _persist_report(report: SameObjectResolutionReport) -> dict[str, Any]:
    body = report.as_json()
    path = write_same_object_report(body)
    body["report_path"] = path
    return body


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


def _new_prefixed_id(prefix: str) -> str:
    factory = getattr(uuid_lib, "uuid7", None)
    value = factory() if callable(factory) else uuid_lib.uuid4()
    return f"{prefix}_{value.hex}"


def _audit(
    *,
    object_ref_id: str = "",
    candidate_count: int = 0,
    visual_candidate_count: int = 0,
) -> dict[str, Any]:
    return {
        "schema": "SameObjectResolver.backend_v1",
        "execution_model": "sync_wait_core_worker_compatible",
        "object_ref_id": object_ref_id,
        "candidate_count": candidate_count,
        "visual_candidate_count": visual_candidate_count,
        "strong_match_confidence": STRONG_MATCH_CONFIDENCE,
        "ambiguous_match_confidence": AMBIGUOUS_MATCH_CONFIDENCE,
        "no_inline_image_bytes": True,
    }


__all__ = [
    "AMBIGUOUS_MATCH_CONFIDENCE",
    "STRONG_MATCH_CONFIDENCE",
    "SameObjectResolutionReport",
    "resolve_same_object",
]
