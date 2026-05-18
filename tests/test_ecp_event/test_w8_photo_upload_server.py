"""Tests for Phase 4 W8 — `parrot.brain.photo_upload_server`.

Coverage focus:
    1. Pure helpers: is_safe_photo_id (rejects path traversal / whitespace),
       asset_path_for / asset_ref_for (path layout matches spec)
    2. POST /upload/photo/{photo_id} with bytes → 200 + bytes saved + ref
    3. POST with empty body → 400
    4. POST with unsafe photo_id (path traversal) → 400
    5. POST publishes photo.asset_uploaded EcpEvent via EcpEventPublisher
       (mocked Room) — verifies publish_ok in response + publish counter
    6. /health responds 200
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from parrot.brain.event_publisher import (
    attach_ecp_event_publisher,
    reset_ecp_event_publisher_for_tests,
)
from parrot.brain.event_ingest import reset_ecp_event_ingest_for_tests
from parrot.brain.observer import photo as photo_observer
from parrot.brain.photo_upload_server import (
    asset_path_for,
    asset_ref_for,
    build_app,
    is_safe_photo_id,
)


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    """Cache root → tmp_path so tests don't pollute the workspace."""
    from parrot.brain.intent_workspace import set_intent_workspace_for_test
    from parrot.dsg.l1_5 import set_pool_for_test

    monkeypatch.setenv("PARROT_PHOTO_CACHE_ROOT", str(tmp_path))
    reset_ecp_event_ingest_for_tests()
    photo_observer.reset_metrics_for_tests()
    set_intent_workspace_for_test(None)
    set_pool_for_test(None)
    reset_ecp_event_publisher_for_tests()
    yield tmp_path
    reset_ecp_event_ingest_for_tests()
    photo_observer.reset_metrics_for_tests()
    set_intent_workspace_for_test(None)
    set_pool_for_test(None)
    reset_ecp_event_publisher_for_tests()


def _fake_room(name: str = "test-room") -> MagicMock:
    room = MagicMock()
    room.name = name
    room.local_participant = MagicMock()
    room.local_participant.publish_data = AsyncMock(return_value=None)
    return room


# ─── pure helpers ────────────────────────────────────────────────


def test_is_safe_photo_id_accepts_normal():
    assert is_safe_photo_id("ph_abc12345") is True
    assert is_safe_photo_id("photo-001") is True


def test_is_safe_photo_id_rejects_path_traversal():
    assert is_safe_photo_id("../etc/passwd") is False
    assert is_safe_photo_id("foo/bar") is False
    assert is_safe_photo_id("foo\\bar") is False


def test_is_safe_photo_id_rejects_whitespace_and_null():
    assert is_safe_photo_id("") is False
    assert is_safe_photo_id("   ") is False
    assert is_safe_photo_id("foo bar") is False
    assert is_safe_photo_id("foo\tbar") is False
    assert is_safe_photo_id("foo\0bar") is False


def test_is_safe_photo_id_rejects_oversize():
    assert is_safe_photo_id("x" * 129) is False
    assert is_safe_photo_id("x" * 128) is True


def test_asset_path_layout(tmp_path):
    p = asset_path_for("ph_001", root=tmp_path, today="2026-04-30")
    assert p == tmp_path / "2026-04-30" / "ph_001.jpg"


def test_asset_ref_layout():
    ref = asset_ref_for("ph_001", today="2026-04-30")
    assert ref == "/upload/photo/2026-04-30/ph_001.jpg"


# ─── HTTP route — happy path ─────────────────────────────────────


def test_upload_photo_saves_bytes_and_returns_ref(_isolated):
    from fastapi.testclient import TestClient

    app = build_app()
    client = TestClient(app)

    payload = b"\xff\xd8\xff\xe0fake JPEG bytes"
    resp = client.post(
        "/upload/photo/ph_save01",
        content=payload,
        headers={"Content-Type": "image/jpeg"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["ok"] is True
    assert body["photo_id"] == "ph_save01"
    assert body["bytes"] == len(payload)
    assert body["asset_ref"].startswith("/upload/photo/")
    assert body["asset_ref"].endswith("/ph_save01.jpg")
    assert body["asset_path"].endswith("ph_save01.jpg")

    # Verify the file actually landed on disk under the cache root
    saved_files = list(Path(_isolated).rglob("ph_save01.jpg"))
    assert len(saved_files) == 1
    assert saved_files[0].read_bytes() == payload


# ─── HTTP route — failures ───────────────────────────────────────


def test_upload_photo_rejects_empty_body(_isolated):
    from fastapi.testclient import TestClient

    client = TestClient(build_app())
    resp = client.post(
        "/upload/photo/ph_empty",
        content=b"",
    )
    assert resp.status_code == 400
    assert "empty" in resp.json()["detail"].lower()


def test_upload_photo_rejects_unsafe_id(_isolated):
    from fastapi.testclient import TestClient

    client = TestClient(build_app())
    # FastAPI route still matches but is_safe_photo_id rejects.
    resp = client.post(
        "/upload/photo/foo bar",  # space — invalid
        content=b"some bytes",
    )
    assert resp.status_code == 400
    assert "invalid" in resp.json()["detail"].lower()


# ─── /health smoke ──────────────────────────────────────────────


def test_health_endpoint(_isolated):
    from fastapi.testclient import TestClient

    client = TestClient(build_app())
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["service"] == "photo-upload"


def test_brain_read_only_live_state_routes(_isolated):
    """The job-local upload server also exposes read-only debug snapshots.

    Laptop app-monitor/Web Console can use these routes to read the same Brain
    process that receives photo.taken_preview and upserts PhotoNodes.
    """
    from fastapi.testclient import TestClient

    client = TestClient(build_app())

    live = client.get("/api/app/live-state?limit=5")
    l2b = client.get("/api/l2b/snapshot?limit=5")

    assert live.status_code == 200
    assert live.json()["audit"]["source_process"] == "brain.photo_upload_server"
    assert live.json()["audit"]["read_only_proxy_surface"] is True
    assert l2b.status_code == 200
    assert l2b.json()["remote_source"] == "brain.photo_upload_server"
    assert l2b.json()["read_only_proxy_surface"] is True


# ─── publish bridge ─────────────────────────────────────────────


def test_upload_publishes_photo_asset_uploaded_event(_isolated):
    """Wire EcpEventPublisher to a fake Room → POST → publish_data must
    have been awaited with a JSON containing event_type=photo.asset_uploaded
    and source=brain."""
    from fastapi.testclient import TestClient

    room = _fake_room()
    publisher = attach_ecp_event_publisher(room)

    client = TestClient(build_app())
    payload = b"asset-bytes-here"
    resp = client.post(
        "/upload/photo/ph_publish",
        content=payload,
        headers={"X-Photo-Preview-Event-Id": "evt_preview_corr"},
    )
    assert resp.status_code == 200
    assert resp.json()["publish_ok"] is True
    assert publisher.published_count == 1

    # Check the wire JSON FastAPI produced
    room.local_participant.publish_data.assert_awaited_once()
    call = room.local_participant.publish_data.await_args
    wire = call.kwargs["payload"]
    assert '"event_type":"photo.asset_uploaded"' in wire
    assert '"source":"brain"' in wire
    assert '"photo_id":"ph_publish"' in wire
    assert '"asset_path"' in wire
    # correlation_id chains back to preview event_id when header provided
    assert '"correlation_id":"evt_preview_corr"' in wire
    # asset_bytes matches uploaded bytes
    assert f'"asset_bytes":{len(payload)}' in wire


def test_upload_locally_dispatches_asset_uploaded_to_existing_photo_node(_isolated, monkeypatch):
    """HTTP upload must update the Brain-local PhotoNode, not only publish to peers."""
    import py_trees
    from fastapi.testclient import TestClient

    from parrot.brain.event_ingest import get_ecp_event_ingest
    from parrot.brain.intent_workspace import IntentWorkspace, set_intent_workspace_for_test
    from parrot.dsg.l1_5 import L15Pool, set_pool_for_test
    from parrot.dsg.l2b_graph import L2BGraph
    from parrot.shared.ecp_event import (
        TOPIC_ECP_EVENT,
        EcpEvent,
        EcpEventSource,
        EcpEventType,
    )

    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    set_intent_workspace_for_test(IntentWorkspace())
    set_pool_for_test(L15Pool())
    graph = L2BGraph()
    monkeypatch.setattr("parrot.dsg.l2b_graph.get_l2b_graph", lambda: graph)

    ingest = get_ecp_event_ingest()
    photo_observer.register(ingest)
    preview = EcpEvent.build(
        event_type=EcpEventType.PHOTO_TAKEN_PREVIEW,
        source=EcpEventSource.UNITY,
        payload={
            "photo_id": "ph_http_local",
            "episode_ref": "ep_http",
            "candidate_subject_uuid": "",
            "focus_refs": [],
            "bbox_refs": [],
            "pose": {},
            "preview_jpeg_b64": "",
        },
    )
    ingest.handle_raw(TOPIC_ECP_EVENT, preview.to_wire_json().encode("utf-8"))
    assert graph.get_node("ph_http_local").reference_image_path == ""

    room = _fake_room()
    attach_ecp_event_publisher(room)
    resp = TestClient(build_app()).post(
        "/upload/photo/ph_http_local",
        content=b"asset-bytes-here",
        headers={"X-Photo-Preview-Event-Id": preview.event_id},
    )

    assert resp.status_code == 200, resp.text
    assert resp.json()["publish_ok"] is True
    node = graph.get_node("ph_http_local")
    assert node is not None
    assert node.reference_image_path.endswith("ph_http_local.jpg")
    metrics = photo_observer.get_metrics_snapshot()
    assert metrics["asset_uploaded_received"] == 1
    assert metrics["photo_nodes_updated_with_asset"] == 1

    set_intent_workspace_for_test(None)
    set_pool_for_test(None)


def test_upload_publishes_photo_timebase_metadata(_isolated):
    """HTTP uploads can carry producer sample time without ECP top-level churn."""
    from fastapi.testclient import TestClient

    room = _fake_room()
    attach_ecp_event_publisher(room)

    client = TestClient(build_app())
    resp = client.post(
        "/upload/photo/ph_timebase",
        content=b"timebase-bytes",
        headers={
            "X-Parrot-Clock-Domain": "unity",
            "X-Parrot-Wall-Time-Ms": "1700000020123",
            "X-Parrot-Media-Time-Us": "123456",
            "X-Parrot-Sequence": "8",
            "X-Parrot-Source-Id": "unity-photo-controller",
        },
    )
    assert resp.status_code == 200

    wire = room.local_participant.publish_data.await_args.kwargs["payload"]
    assert '"timebase"' in wire
    assert '"clock_domain":"unity"' in wire
    assert '"wall_time_ms":1700000020123' in wire
    assert '"media_time_us":123456' in wire
    assert '"sequence":8' in wire
    assert '"source_id":"unity-photo-controller"' in wire


def test_upload_publishes_when_no_preview_header_uses_photo_id_as_correlation(_isolated):
    from fastapi.testclient import TestClient

    room = _fake_room()
    attach_ecp_event_publisher(room)

    client = TestClient(build_app())
    resp = client.post(
        "/upload/photo/ph_no_corr",
        content=b"some bytes",
    )
    assert resp.status_code == 200

    call = room.local_participant.publish_data.await_args
    wire = call.kwargs["payload"]
    # When no X-Photo-Preview-Event-Id header, correlation_id falls back to photo_id
    assert '"correlation_id":"ph_no_corr"' in wire


def test_upload_returns_publish_ok_false_when_no_publisher(_isolated):
    """No EcpEventPublisher attached → upload still saves bytes + returns
    publish_ok=False, no crash."""
    from fastapi.testclient import TestClient

    # No attach_ecp_event_publisher call — get_ecp_event_publisher returns None
    client = TestClient(build_app())
    resp = client.post(
        "/upload/photo/ph_no_pub",
        content=b"saved-anyway",
    )
    assert resp.status_code == 200
    assert resp.json()["publish_ok"] is False
    assert resp.json()["bytes"] == len(b"saved-anyway")
