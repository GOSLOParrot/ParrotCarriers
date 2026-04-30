"""Tests for Phase 4 W8 — `parrot.brain.observer.photo` real handlers.

Coverage focus:
    1. register subscribes to BOTH photo.taken_preview and photo.asset_uploaded
    2. taken_preview → PhotoNode upserted with kind=NodeKind.PHOTO + meta
       (episode_ref / candidate_subject_uuid / focus_refs / bbox_refs / pose)
    3. taken_preview → BB transient/last_photo_event written with stage="preview"
    4. asset_uploaded → finds existing PhotoNode and sets reference_image_path
    5. asset_uploaded for unknown photo_id (preview missed) → counted, no crash
    6. taken_preview without photo_id → counted as missing, no node created
    7. Re-publish (Unity reconnect) is idempotent — same photo_id touches
       interaction_count instead of creating duplicate node
    8. PhotoNode is NodeKind.PHOTO — distinct from NodeKind.OBJECT (the
       structural enforcement of entry doc §8.1 L7 "no auto ObjectNode")
"""

from __future__ import annotations

import pytest

from parrot.brain.event_ingest import EcpEventIngest, reset_ecp_event_ingest_for_tests
from parrot.brain.observer import photo as photo_observer
from parrot.dsg.l2b_graph import L2BGraph
from parrot.dsg.l2b_types import NodeKind
from parrot.shared.ecp_event import EcpEvent, EcpEventSource, EcpEventType


@pytest.fixture(autouse=True)
def _isolated(monkeypatch):
    """Each test gets a fresh L2BGraph so PhotoNode upserts don't leak.

    L2BGraph is exposed as a singleton via get_l2b_graph(); we monkey-patch
    the module-level holder for test isolation.
    """
    reset_ecp_event_ingest_for_tests()
    photo_observer.reset_metrics_for_tests()

    fresh_graph = L2BGraph()
    monkeypatch.setattr(
        "parrot.dsg.l2b_graph.get_l2b_graph",
        lambda: fresh_graph,
    )
    yield fresh_graph

    reset_ecp_event_ingest_for_tests()
    photo_observer.reset_metrics_for_tests()


def _preview_event(
    photo_id: str = "ph_test01",
    *,
    episode_ref: str = "",
    candidate_subject_uuid: str = "",
    focus_refs: tuple = (),
    bbox_refs: tuple = (),
    preview_jpeg_b64: str = "",
) -> EcpEvent:
    return EcpEvent.build(
        event_type=EcpEventType.PHOTO_TAKEN_PREVIEW,
        source=EcpEventSource.UNITY,
        payload={
            "photo_id": photo_id,
            "episode_ref": episode_ref,
            "candidate_subject_uuid": candidate_subject_uuid,
            "focus_refs": list(focus_refs),
            "bbox_refs": list(bbox_refs),
            "pose": {"px": 1.0, "py": 2.0, "pz": 3.0},
            "preview_jpeg_b64": preview_jpeg_b64,
        },
    )


def _asset_uploaded_event(
    photo_id: str = "ph_test01",
    asset_ref: str = "/upload/photo/2026-04-30/ph_test01.jpg",
    asset_bytes: int = 12345,
    correlation_id: str = "",
) -> EcpEvent:
    return EcpEvent.build(
        event_type=EcpEventType.PHOTO_ASSET_UPLOADED,
        source=EcpEventSource.BRAIN,
        payload={
            "photo_id": photo_id,
            "asset_ref": asset_ref,
            "asset_bytes": asset_bytes,
        },
        correlation_id=correlation_id,
    )


# ─── registration ────────────────────────────────────────────────


def test_register_subscribes_to_both_photo_event_types():
    ingest = EcpEventIngest()
    photo_observer.register(ingest)
    assert len(ingest._subs.get("photo.taken_preview", [])) == 1
    assert len(ingest._subs.get("photo.asset_uploaded", [])) == 1


# ─── taken_preview → PhotoNode upsert ────────────────────────────


def test_preview_creates_photo_node_with_kind_photo(_isolated):
    ingest = EcpEventIngest()
    photo_observer.register(ingest)
    ev = _preview_event(
        photo_id="ph_kind",
        episode_ref="ep_001",
        candidate_subject_uuid="obj_42",
        focus_refs=("ref_focus_a",),
        bbox_refs=("ref_bbox_b",),
    )
    ingest.handle_raw("parrot.ecp.event", ev.to_wire_json().encode("utf-8"))

    node = _isolated.get_node("ph_kind")
    assert node is not None
    # NodeKind.PHOTO is the structural guard from entry §8.1 L7 — must be
    # PHOTO, NEVER OBJECT (PhotoEvent doesn't auto-create ObjectNodes).
    assert node.kind == NodeKind.PHOTO
    assert node.kind != NodeKind.OBJECT
    assert node.label == "photo:ph_kind"
    assert node.meta["episode_ref"] == "ep_001"
    assert node.meta["candidate_subject_uuid"] == "obj_42"
    assert node.meta["focus_refs"] == ["ref_focus_a"]
    assert node.meta["bbox_refs"] == ["ref_bbox_b"]
    assert node.meta["pose"] == {"px": 1.0, "py": 2.0, "pz": 3.0}
    assert photo_observer.get_metrics_snapshot()["preview_received"] == 1
    assert photo_observer.get_metrics_snapshot()["photo_nodes_upserted"] == 1


def test_preview_writes_bb_last_photo_event(_isolated):
    from parrot.scheduler.blackboard import open_bb_client

    ingest = EcpEventIngest()
    photo_observer.register(ingest)
    ingest.handle_raw(
        "parrot.ecp.event",
        _preview_event(photo_id="ph_bb", preview_jpeg_b64="QUJDRA==").to_wire_json().encode("utf-8"),
    )

    bb = open_bb_client(name="test_bb_photo_reader", writer="test")
    bb_payload = bb.get("transient/last_photo_event")
    assert bb_payload["schema_version"] == 1
    assert bb_payload["photo_id"] == "ph_bb"
    assert bb_payload["stage"] == "preview"
    assert bb_payload["preview_jpeg_b64"] == "QUJDRA=="
    assert bb_payload["asset_ref"] == ""  # not yet uploaded


# ─── asset_uploaded → PhotoNode update ──────────────────────────


def test_asset_uploaded_updates_existing_photo_node(_isolated):
    ingest = EcpEventIngest()
    photo_observer.register(ingest)

    # First: preview creates the node.
    ingest.handle_raw(
        "parrot.ecp.event",
        _preview_event(photo_id="ph_chain").to_wire_json().encode("utf-8"),
    )
    node = _isolated.get_node("ph_chain")
    assert node is not None
    assert node.reference_image_path == ""

    # Then: asset_uploaded sets the path.
    ingest.handle_raw(
        "parrot.ecp.event",
        _asset_uploaded_event(
            photo_id="ph_chain",
            asset_ref="/upload/photo/2026-04-30/ph_chain.jpg",
        ).to_wire_json().encode("utf-8"),
    )

    node_after = _isolated.get_node("ph_chain")
    assert node_after.reference_image_path == "/upload/photo/2026-04-30/ph_chain.jpg"
    assert photo_observer.get_metrics_snapshot()["photo_nodes_updated_with_asset"] == 1


def test_asset_uploaded_for_unknown_photo_id_counted_no_crash(_isolated):
    ingest = EcpEventIngest()
    photo_observer.register(ingest)
    ingest.handle_raw(
        "parrot.ecp.event",
        _asset_uploaded_event(photo_id="ph_orphan").to_wire_json().encode("utf-8"),
    )
    metrics = photo_observer.get_metrics_snapshot()
    assert metrics["asset_uploaded_received"] == 1
    assert metrics["asset_for_unknown_photo_id"] == 1
    assert metrics["photo_nodes_updated_with_asset"] == 0
    assert _isolated.get_node("ph_orphan") is None


# ─── defensive paths ────────────────────────────────────────────


def test_preview_without_photo_id_counted_no_node():
    ingest = EcpEventIngest()
    photo_observer.register(ingest)
    bad = EcpEvent.build(
        event_type=EcpEventType.PHOTO_TAKEN_PREVIEW,
        source=EcpEventSource.UNITY,
        payload={},  # NO photo_id
    )
    ingest.handle_raw("parrot.ecp.event", bad.to_wire_json().encode("utf-8"))
    metrics = photo_observer.get_metrics_snapshot()
    assert metrics["preview_received"] == 1
    assert metrics["missing_photo_id"] == 1
    assert metrics["photo_nodes_upserted"] == 0


# ─── idempotency ─────────────────────────────────────────────────


def test_preview_replay_is_idempotent(_isolated):
    """Unity reconnect republishes preview — must not create a duplicate
    PhotoNode under the same photo_id; must instead bump interaction_count."""
    ingest = EcpEventIngest()
    photo_observer.register(ingest)

    raw = _preview_event(photo_id="ph_replay").to_wire_json().encode("utf-8")
    ingest.handle_raw("parrot.ecp.event", raw)
    # Use a fresh event_id to bypass dedup window
    raw2 = _preview_event(photo_id="ph_replay").to_wire_json().encode("utf-8")
    ingest.handle_raw("parrot.ecp.event", raw2)

    nodes = [n for n in _isolated.all_nodes() if n.uuid == "ph_replay"]
    assert len(nodes) == 1
    assert nodes[0].interaction_count >= 1


# ─── metrics snapshot shape ─────────────────────────────────────


def test_metrics_snapshot_keys():
    snap = photo_observer.get_metrics_snapshot()
    assert set(snap.keys()) == {
        "preview_received",
        "asset_uploaded_received",
        "photo_nodes_upserted",
        "photo_nodes_updated_with_asset",
        "missing_photo_id",
        "asset_for_unknown_photo_id",
    }
