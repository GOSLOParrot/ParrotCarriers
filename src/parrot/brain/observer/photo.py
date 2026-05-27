"""Sprint4 Phase 4 W8 — photo observer.

Authoritative spec:
    - ``architecture/sprint4_phase4_entry_20260430.md §8.1`` L7 (PhotoNode
      vs ObjectNode) + L8 (dual-channel preview / asset)
    - ``architecture/sprint4_phase4_entry_20260430.md §8.3`` event_type
      registry rows for ``photo.taken_preview`` + ``photo.asset_uploaded``
    - ``audit_identify_object_no_screenshot_20260420.md §5.1 B3`` for
      photo file path convention (deferred to Phase 5+ — Phase 4 cache
      lives at ``data/photos/``)

Pipeline (Phase 4 W8 Brain side; Unity half is a separate chat)::

    Unity: capturePhoto → preview ready
        → publish EcpEvent ``photo.taken_preview`` (≤ 8KB inline JPEG)
        → HTTP POST /upload/photo/{photo_id} (full-resolution asset)
                                                                │
                                                                ▼
    Brain event_ingest dispatches photo.taken_preview            │
        ─► observer.photo._on_photo_taken_preview                │
            • upsert PhotoNode (NodeKind.PHOTO) into L2BGraph    │
              with reference_image_path="" (asset not yet uploaded)
            • write transient/last_photo_event BB key            │
                                                                 │
    Brain photo_upload_server receives full-res asset on HTTP POST
        • saves bytes to data/photos/{yyyy-mm-dd}/{photo_id}.jpg
        • publishes EcpEvent ``photo.asset_uploaded`` (correlation_id =
          original preview event_id when known)
                                                                 │
        ─► observer.photo._on_photo_asset_uploaded               │
            • finds existing PhotoNode by photo_id
            • updates reference_image_path to the saved file path
            • re-writes transient/last_photo_event BB with stage="asset_uploaded"

Boundary contract (entry doc §3.7):
    Observer records evidence only. It writes:
        • PhotoNode to L2BGraph — analogous to identify_object._upsert_to_l2b
          for ObjectNode; PhotoNode is a NEW NodeKind, distinct from OBJECT,
          so the §8.1 L7 rule "PhotoEvent does NOT auto-create unknown
          ObjectNodes" is structurally enforced
        • BB transient/last_photo_event — its declared writer key

    It does NOT:
        • Write ObjectNodes (that's identify_object.save_new on user demand)
        • Auto-promote PhotoNode candidate_subject to a CONFIRMED ObjectNode
          (Phase 5+ resolver flow)
        • Mutate Episode (PART_OF_EPISODE / HAS_PHOTO edges deferred to
          Phase 5+ when Episode lifecycle is fully wired)
"""

from __future__ import annotations

import asyncio
import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from parrot.brain.event_ingest import EcpEventIngest
from parrot.shared.ecp_event import EcpEvent, EcpEventType

if TYPE_CHECKING:
    import py_trees


logger = logging.getLogger(__name__)


_BB_WRITER = "brain.observer.photo"
_BB_KEY_LAST_PHOTO = "transient/last_photo_event"
_PHOTO_EVENT_SCHEMA_VERSION = 1


# Counters for debug HUD / pytest assertions — symmetric with the
# sighting/bbox/focus observer pattern.
_metrics: dict[str, int] = {
    "preview_received": 0,
    "asset_uploaded_received": 0,
    "photo_nodes_upserted": 0,
    "photo_nodes_updated_with_asset": 0,
    "missing_photo_id": 0,
    "asset_for_unknown_photo_id": 0,
    "asset_orphan_nodes_repaired": 0,
    "awareness_decisions": 0,
    "awareness_preview_refs_staged": 0,
    "awareness_react_allowed": 0,
}


def get_metrics_snapshot() -> dict[str, int]:
    return dict(_metrics)


def reset_metrics_for_tests() -> None:
    for k in _metrics:
        _metrics[k] = 0


_bb: "py_trees.blackboard.Client | None" = None


def _ensure_bb() -> "py_trees.blackboard.Client":
    global _bb
    if _bb is None:
        from parrot.scheduler.blackboard import open_bb_client
        _bb = open_bb_client(name="observer_photo", writer=_BB_WRITER)
    return _bb


# ─── photo.taken_preview handler ────────────────────────────────


def _on_photo_taken_preview(event: EcpEvent) -> None:
    _metrics["preview_received"] += 1
    payload = event.payload or {}
    photo_id = str(payload.get("photo_id", "") or "")
    if not photo_id:
        _metrics["missing_photo_id"] += 1
        logger.debug(
            "[observer.photo] taken_preview without photo_id (event_id=%s)",
            event.event_id,
        )
        return

    # 1) Upsert PhotoNode in L2-B with kind=PHOTO. reference_image_path stays
    # empty until the HTTP asset upload lands.
    _upsert_photo_node(
        photo_id=photo_id,
        episode_ref=str(payload.get("episode_ref", "") or ""),
        candidate_subject_uuid=str(payload.get("candidate_subject_uuid", "") or ""),
        focus_refs=tuple(payload.get("focus_refs") or ()),
        bbox_refs=tuple(payload.get("bbox_refs") or ()),
        pose=payload.get("pose") if isinstance(payload.get("pose"), dict) else {},
        source_event_id=event.event_id,
    )

    # 2) Mirror payload + observer-derived fields to the BB key.
    bb_payload = _build_bb_payload(
        stage="preview",
        photo_id=photo_id,
        payload=payload,
    )
    try:
        bb = _ensure_bb()
        bb.set(_BB_KEY_LAST_PHOTO, bb_payload)
    except Exception:
        logger.debug(
            "[observer.photo] BB write failed for photo_id=%s",
            photo_id, exc_info=True,
        )

    # Awareness is a policy decision, not a camera-mode decision. It can stage
    # a short-lived IntentWorkspace preview ref for GOSLO while still blocking
    # speech interruption in App v1.
    _apply_awareness_decision(
        photo_id=photo_id,
        payload=payload,
        source_event_id=event.event_id,
    )


# ─── photo.asset_uploaded handler ───────────────────────────────


def _on_photo_asset_uploaded(event: EcpEvent) -> None:
    _metrics["asset_uploaded_received"] += 1
    payload = event.payload or {}
    photo_id = str(payload.get("photo_id", "") or "")
    if not photo_id:
        _metrics["missing_photo_id"] += 1
        logger.debug(
            "[observer.photo] asset_uploaded without photo_id (event_id=%s)",
            event.event_id,
        )
        return

    asset_ref = str(payload.get("asset_ref", "") or "")
    asset_path = str(payload.get("asset_path", "") or "")
    asset_bytes = int(payload.get("asset_bytes", 0) or 0)
    storage_ref = asset_path or asset_ref
    evidence_sample = _record_photo_asset_evidence(
        event=event,
        photo_id=photo_id,
        asset_ref=asset_ref,
        asset_path=asset_path,
        asset_bytes=asset_bytes,
        payload=payload,
    )
    _record_photo_catalog_entry(
        photo_id=photo_id,
        asset_ref=asset_ref,
        asset_path=asset_path,
        asset_bytes=asset_bytes,
        payload=payload,
        evidence_id=str(getattr(evidence_sample, "evidence_id", "") or ""),
        captured_at_ms=int(getattr(getattr(evidence_sample, "timebase", None), "wall_time_ms", 0) or 0),
    )

    # Find the existing PhotoNode created on preview. If preview was dropped or
    # arrived out-of-order, repair the PHOTO node from the storage-backed asset
    # event so Web/L2-B/IntentWorkspace do not lose the photo.
    updated = _update_photo_node_asset(
        photo_id=photo_id,
        storage_ref=storage_ref,
    )
    if not updated:
        _metrics["asset_for_unknown_photo_id"] += 1
        logger.warning(
            "[observer.photo] asset_uploaded for unknown photo_id=%s — preview event "
            "missed or arrived out of order; repairing PhotoNode from asset",
            photo_id,
        )
        _upsert_photo_node(
            photo_id=photo_id,
            episode_ref=str(payload.get("episode_ref", "") or ""),
            candidate_subject_uuid=str(payload.get("candidate_subject_uuid", "") or ""),
            focus_refs=tuple(payload.get("focus_refs") or ()),
            bbox_refs=tuple(payload.get("bbox_refs") or ()),
            pose=payload.get("pose") if isinstance(payload.get("pose"), dict) else {},
            source_event_id=event.event_id,
        )
        updated = _update_photo_node_asset(
            photo_id=photo_id,
            storage_ref=storage_ref,
        )
        if updated:
            _metrics["asset_orphan_nodes_repaired"] += 1

    # BB write regardless — debug HUD wants to see the upload happened.
    bb_payload = _build_bb_payload(
        stage="asset_uploaded",
        photo_id=photo_id,
        payload=payload,
    )
    bb_payload["asset_ref"] = asset_ref
    bb_payload["asset_path"] = asset_path
    bb_payload["asset_bytes"] = asset_bytes
    try:
        bb = _ensure_bb()
        bb.set(_BB_KEY_LAST_PHOTO, bb_payload)
    except Exception:
        logger.debug(
            "[observer.photo] BB write failed for asset_uploaded photo_id=%s",
            photo_id, exc_info=True,
        )

    if updated and storage_ref:
        _stage_photo_asset_ref(
            photo_id=photo_id,
            storage_ref=storage_ref,
            asset_ref=asset_ref,
            asset_bytes=asset_bytes,
        )
        _record_photo_analysis_report(
            photo_id=photo_id,
            asset_ref=asset_ref,
            asset_path=storage_ref,
            asset_bytes=asset_bytes,
            payload=payload,
            evidence_id=str(getattr(evidence_sample, "evidence_id", "") or ""),
        )


# ─── L2-B PhotoNode helpers ─────────────────────────────────────


def _upsert_photo_node(
    *,
    photo_id: str,
    episode_ref: str,
    candidate_subject_uuid: str,
    focus_refs: tuple,
    bbox_refs: tuple,
    pose: dict,
    source_event_id: str,
) -> None:
    """Create-or-update a PhotoNode in L2-B working memory."""
    try:
        from parrot.dsg.l2b_graph import get_l2b_graph
        from parrot.dsg.l2b_types import (
            ConfirmationStatus,
            NodeKind,
            Salience,
            SemanticNode,
        )
    except Exception:
        logger.debug("[observer.photo] L2-B types unavailable", exc_info=True)
        return

    try:
        graph = get_l2b_graph()
    except Exception:
        logger.debug("[observer.photo] L2-B graph unavailable", exc_info=True)
        return

    if graph is None:
        return

    existing = graph.get_node(photo_id)
    if existing is not None:
        # Idempotent — re-publish or reconnect both arrive here. Refresh
        # last_seen + interaction_count, leave reference_image_path alone
        # (asset upload is the only thing allowed to set it).
        existing.last_seen_this_session = time.time()
        existing.interaction_count += 1
        return

    node = SemanticNode(
        uuid=photo_id,
        kind=NodeKind.PHOTO,
        label=f"photo:{photo_id}",
        confirmation=ConfirmationStatus.CONFIRMED,  # user took it; it exists
        evidence_score=1.0,
        attention=0.6,
        salience=Salience.ACTIVE,
        provenance_stream_id=source_event_id,
        meta={
            "episode_ref": episode_ref,
            "candidate_subject_uuid": candidate_subject_uuid,
            "focus_refs": list(focus_refs),
            "bbox_refs": list(bbox_refs),
            "pose": pose,
        },
    )
    graph.upsert_node(node)
    _metrics["photo_nodes_upserted"] += 1
    logger.info(
        "[observer.photo] PhotoNode upserted photo_id=%s episode=%s candidate=%s",
        photo_id, episode_ref or "—", candidate_subject_uuid or "—",
    )


def _update_photo_node_asset(*, photo_id: str, storage_ref: str) -> bool:
    """Set reference_image_path on an existing PhotoNode.

    ``storage_ref`` should be a real disk path when available. The HTTP
    ``asset_ref`` remains in the ECP payload for clients, but L2-B and RefTable
    need a path that can be checked with Path.exists().
    """
    try:
        from parrot.dsg.l2b_graph import get_l2b_graph
    except Exception:
        return False

    try:
        graph = get_l2b_graph()
    except Exception:
        return False

    if graph is None:
        return False

    existing = graph.get_node(photo_id)
    if existing is None:
        return False
    existing.reference_image_path = storage_ref
    existing.last_seen_this_session = time.time()
    _metrics["photo_nodes_updated_with_asset"] += 1
    logger.info(
        "[observer.photo] PhotoNode photo_id=%s storage_ref=%s",
        photo_id, storage_ref,
    )
    return True


def _stage_photo_asset_ref(
    *,
    photo_id: str,
    storage_ref: str,
    asset_ref: str,
    asset_bytes: int,
) -> None:
    """Stage the photo path in IntentWorkspace and bind it in L1.5 RefTable."""

    async def _stage() -> None:
        try:
            from parrot.brain.intent_workspace import (
                PayloadSource,
                StagedRefKind,
                StagedRefMetadata,
                StagedRefRequest,
                get_intent_workspace,
            )
            from parrot.dsg.l1_5 import get_l1_5_pool
            from parrot.dsg.l1_5.ref_table import RefKind

            path = Path(storage_ref)
            ws = get_intent_workspace()
            handle = await ws.stage(
                StagedRefRequest(
                    kind=StagedRefKind.PHOTO,
                    payload_source=PayloadSource.DISK_PATH,
                    payload_value=path,
                    metadata=StagedRefMetadata(
                        origin="observer.photo",
                        kind=StagedRefKind.PHOTO,
                        payload_source=PayloadSource.DISK_PATH,
                        related_node_uuid=photo_id,
                        size_bytes=asset_bytes,
                        custom_meta={
                            "photo_id": photo_id,
                            "asset_ref": asset_ref,
                            "asset_path": storage_ref,
                            "role": "photo_capture",
                        },
                    ),
                )
            )
            pool = get_l1_5_pool()
            pool.bind_ref(
                photo_id,
                RefKind.PHOTO_PATH,
                storage_ref,
                intent_workspace_ref_id=handle.ref_id,
            )
        except Exception:
            logger.debug("[observer.photo] photo asset staging failed", exc_info=True)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(_stage())
    else:
        loop.create_task(_stage())


def _record_photo_asset_evidence(
    *,
    event: EcpEvent,
    photo_id: str,
    asset_ref: str,
    asset_path: str,
    asset_bytes: int,
    payload: dict[str, Any],
) -> Any | None:
    """Mirror full-resolution photo uploads into the temporal evidence ledger."""
    try:
        from parrot.brain.vision.evidence import (
            EvidenceKind,
            record_ecp_evidence_sample,
        )

        return record_ecp_evidence_sample(
            event,
            kind=EvidenceKind.IMAGE_ASSET,
            asset_path=asset_path,
            asset_uri=asset_ref,
            related_refs=(photo_id,),
            bbox_refs=tuple(str(x) for x in payload.get("bbox_refs") or ()),
            focus_refs=tuple(str(x) for x in payload.get("focus_refs") or ()),
            description=f"photo asset {photo_id}",
            meta={
                "source": "observer.photo",
                "photo_id": photo_id,
                "asset_bytes": asset_bytes,
            },
        )
    except Exception:
        logger.debug("[observer.photo] evidence ledger write failed", exc_info=True)
        return None


def _record_photo_catalog_entry(
    *,
    photo_id: str,
    asset_ref: str,
    asset_path: str,
    asset_bytes: int,
    payload: dict[str, Any],
    evidence_id: str,
    captured_at_ms: int,
) -> None:
    """Mirror PhotoNode asset uploads into the vision catalog manifest."""
    try:
        from parrot.brain.vision.object_discovery import record_photo_asset

        record_photo_asset(
            photo_uuid=photo_id,
            asset_path=asset_path or asset_ref,
            evidence_id=evidence_id,
            asset_ref=asset_ref,
            asset_bytes=asset_bytes,
            payload=payload,
            captured_at_ms=captured_at_ms,
        )
    except Exception:
        logger.debug("[observer.photo] vision photo catalog write failed", exc_info=True)


def _record_photo_analysis_report(
    *,
    photo_id: str,
    asset_ref: str,
    asset_path: str,
    asset_bytes: int,
    payload: dict[str, Any],
    evidence_id: str,
) -> None:
    """Create a photo-level report pointer without object identity binding."""
    try:
        from parrot.brain.vision.photo_analysis import create_photo_analysis_report

        create_photo_analysis_report(
            photo_id=photo_id,
            asset_path=asset_path,
            asset_ref=asset_ref,
            evidence_id=evidence_id,
            asset_bytes=asset_bytes,
            payload=payload,
        )
    except Exception:
        logger.debug("[observer.photo] photo analysis report write failed", exc_info=True)


def _build_bb_payload(
    *,
    stage: str,
    photo_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Construct the BB transient/last_photo_event payload (locked schema
    in bb_schema.py comment)."""
    return {
        "schema_version": _PHOTO_EVENT_SCHEMA_VERSION,
        "photo_id": photo_id,
        "stage": stage,
        "pose": payload.get("pose") if isinstance(payload.get("pose"), dict) else {},
        "episode_ref": str(payload.get("episode_ref", "") or ""),
        "focus_refs": list(payload.get("focus_refs") or ()),
        "bbox_refs": list(payload.get("bbox_refs") or ()),
        "candidate_subject_uuid": str(payload.get("candidate_subject_uuid", "") or ""),
        "preview_jpeg_b64": (
            str(payload.get("preview_jpeg_b64", "") or "")
            if stage == "preview" else ""
        ),
        "asset_ref": str(payload.get("asset_ref", "") or "") if stage == "asset_uploaded" else "",
        "asset_path": str(payload.get("asset_path", "") or "") if stage == "asset_uploaded" else "",
        "asset_bytes": int(payload.get("asset_bytes", 0) or 0) if stage == "asset_uploaded" else 0,
        "ts_ms": int(time.time() * 1000),
    }


def _apply_awareness_decision(
    *,
    photo_id: str,
    payload: dict[str, Any],
    source_event_id: str,
) -> None:
    try:
        from parrot.brain.photo_awareness import handle_photo_preview_awareness

        decision = handle_photo_preview_awareness(
            photo_id=photo_id,
            payload=payload,
            source_event_id=source_event_id,
        )
    except Exception:
        logger.debug("[observer.photo] awareness decision failed", exc_info=True)
        return

    _metrics["awareness_decisions"] += 1
    if decision.preview_ref_id:
        _metrics["awareness_preview_refs_staged"] += 1
    if decision.allow_react:
        _metrics["awareness_react_allowed"] += 1


# ─── registration ───────────────────────────────────────────────


def register(ingest: EcpEventIngest) -> None:
    """Subscribe to PHOTO_TAKEN_PREVIEW + PHOTO_ASSET_UPLOADED on the given
    ingest. Both subscribers are synchronous; PhotoNode upsert + BB write
    complete in microseconds (no I/O), so no asyncio scheduling needed."""
    ingest.subscribe(EcpEventType.PHOTO_TAKEN_PREVIEW, _on_photo_taken_preview)
    ingest.subscribe(EcpEventType.PHOTO_ASSET_UPLOADED, _on_photo_asset_uploaded)
    logger.debug(
        "[observer.photo] Phase 4 W8 handlers subscribed (preview + asset_uploaded)"
    )


__all__ = ["get_metrics_snapshot", "register", "reset_metrics_for_tests"]
