"""DSG-ARCHIVE-V1 — three-phase delayed archive pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import parrot.dsg.l2b_graph as l2b_graph_module
from parrot.dsg.archive import (
    ArchiveRequest,
    ArchiveRequestKind,
    ArchiveTarget,
    ConversationArchive,
    ConversationBoundary,
    ConversationBoundaryDetector,
    ConversationBoundaryEvent,
    dispatch_archive_request,
    enqueue_episode_for_idle_archive,
    set_archive_for_test,
)
from parrot.dsg.l2b_graph import L2BGraph
from parrot.dsg.l2b_types import NodeKind, SemanticNode


@pytest.fixture
def archive(tmp_path: Path):
    arch = ConversationArchive(base_path=tmp_path / "conversations")
    set_archive_for_test(arch)
    yield arch
    set_archive_for_test(None)


@pytest.fixture
def graph():
    g = L2BGraph()
    l2b_graph_module._instance = g
    yield g
    l2b_graph_module._instance = None


async def test_phase2_serialize_writes_jsonl_files(archive: ConversationArchive) -> None:
    out = await archive.serialize("conv_smoke_001")
    assert out.base_dir.exists()
    expected = {
        "snapshot",
        "refs",
        "timeline",
        "episodes",
        "intent_events",
        "plans",
        "intent_workspace_refs",
        "metadata",
    }
    assert set(out.files.keys()) == expected
    for fname, fpath in out.files.items():
        assert fpath.exists(), fname


async def test_phase2_metadata_marks_not_archived(archive: ConversationArchive) -> None:
    out = await archive.serialize("conv_meta")
    meta_path = out.files["metadata"]
    payload = json.loads(meta_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["archived_to_graphiti"] is False


async def test_phase2_snapshot_includes_node_count(
    archive: ConversationArchive, graph: L2BGraph,
) -> None:
    graph.upsert_node(SemanticNode(label="a", kind=NodeKind.OBJECT))
    graph.upsert_node(SemanticNode(label="b", kind=NodeKind.OBJECT))
    out = await archive.serialize("conv_with_nodes")
    payload = json.loads(out.files["snapshot"].read_text(encoding="utf-8"))
    assert payload["node_count"] == 2


async def test_phase2_serialize_idempotent_on_repeat(archive: ConversationArchive) -> None:
    out1 = await archive.serialize("conv_idem")
    out2 = await archive.serialize("conv_idem")
    assert out1.base_dir == out2.base_dir


async def test_phase3_archive_to_graphiti_skeleton(archive: ConversationArchive) -> None:
    out = await archive.serialize("conv_phase3")
    outcome = await archive.archive_to_graphiti(out)
    assert outcome.success


async def test_dispatch_serialize_now(archive: ConversationArchive) -> None:
    req = ArchiveRequest(
        kind=ArchiveRequestKind.SERIALIZE_NOW,
        target=ArchiveTarget.CONVERSATION,
        target_id="conv_dispatch",
    )
    outcome = await dispatch_archive_request(req)
    assert outcome.success


async def test_dispatch_enqueue_for_idle(archive: ConversationArchive) -> None:
    req = ArchiveRequest(
        kind=ArchiveRequestKind.ENQUEUE_FOR_IDLE,
        target=ArchiveTarget.EPISODE,
        target_id="ep_42",
    )
    outcome = await dispatch_archive_request(req)
    assert outcome.success
    pending = archive.list_pending()
    assert any(p.target_id == "ep_42" for p in pending)


def test_enqueue_helper_writes_queue(archive: ConversationArchive) -> None:
    enqueue_episode_for_idle_archive("ep_helper")
    pending = archive.list_pending()
    assert any(p.target_id == "ep_helper" for p in pending)


async def test_dispatch_scan_and_archive(archive: ConversationArchive) -> None:
    await archive.serialize("conv_scan")
    await archive.enqueue_for_idle_archive(ArchiveTarget.CONVERSATION, "conv_scan")
    req = ArchiveRequest(
        kind=ArchiveRequestKind.SCAN_AND_ARCHIVE,
        target=ArchiveTarget.CONVERSATION,
        target_id="*",
    )
    outcome = await dispatch_archive_request(req)
    assert outcome.success


async def test_boundary_signal_resets_conv_id(archive: ConversationArchive) -> None:
    det = ConversationBoundaryDetector(idle_threshold_seconds=999)
    await det.start()
    cid_before = det.current_conv_id()
    await det.signal_boundary(ConversationBoundaryEvent(
        boundary=ConversationBoundary.EPISODE_CLOSE,
        conv_id=cid_before,
        triggered_at=0.0,
    ))
    assert det.current_conv_id() != cid_before
    await det.stop()


async def test_boundary_signal_serializes_via_archive(
    archive: ConversationArchive,
) -> None:
    det = ConversationBoundaryDetector(idle_threshold_seconds=999)
    await det.start()
    cid = det.current_conv_id()
    await det.signal_boundary(ConversationBoundaryEvent(
        boundary=ConversationBoundary.AGENT_DISCONNECT,
        conv_id=cid,
        triggered_at=0.0,
    ))
    # The archive base dir should have a folder for cid
    assert (archive._base / cid).exists()
    await det.stop()
