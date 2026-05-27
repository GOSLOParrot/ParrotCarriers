from pathlib import Path

import pytest

from parrot.brain.intent_workspace import IntentWorkspace
from parrot.brain.intent_workspace_backend import DiskBackend
from parrot.dsg.identity_ref_index import MemoryIdentityRefIndex
from parrot.dsg.l2b_graph import L2BGraph
from parrot.dsg.l2b_types import EdgeKind, SemanticNode
from parrot.dsg.workspace_ref_sync import (
    apply_workspace_ref_sync,
    draft_workspace_ref_sync,
)


def test_workspace_ref_sync_drafts_large_file_as_pointer(tmp_path: Path) -> None:
    large_file = tmp_path / "source-pack.bin"
    large_file.write_bytes(b"x" * 64)

    draft = draft_workspace_ref_sync(
        {
            "locator": str(large_file),
            "label": "Large source pack",
            "ref_kind": "local_doc",
            "owner_id": "nanobot:task-1",
            "workspace_id": "nanobot_workspace",
            "hash_max_bytes": 16,
        }
    )

    data = draft["data"]
    assert draft["action"] == "memory.workspace_ref_sync.draft"
    assert draft["success"] is True
    assert data["hash"]["status"] == "deferred_large_file"
    assert data["storage_policy"]["l2b"] == "pointer_node_no_payload"
    assert data["identity_ref_payload"]["locators"] == [str(large_file)]
    assert data["identity_ref_payload"]["ref_meta"]["workspace_sync"]["owner_id"] == "nanobot:task-1"
    assert data["l2b_node_draft"]["meta"]["payload_policy"] == "pointer_only_no_inline_large_payload"
    assert data["intent_workspace_request"]["owner_id"] == "nanobot:task-1"
    assert data["mutated"] is False


@pytest.mark.asyncio
async def test_workspace_ref_sync_apply_stages_ref_binds_index_and_materializes_l2b(
    tmp_path: Path,
) -> None:
    source_doc = tmp_path / "obsidian-note.md"
    source_doc.write_text("# Note\nstable content", encoding="utf-8")
    workspace = IntentWorkspace(backend=DiskBackend(base_path=tmp_path / "intent_ws"))
    index = MemoryIdentityRefIndex(path=tmp_path / "identity_ref_index.json")
    graph = L2BGraph()
    graph.upsert_node(SemanticNode(uuid="existing-node", label="Existing node"))

    applied = await apply_workspace_ref_sync(
        {
            "locator": str(source_doc),
            "label": "Obsidian note",
            "ref_id": "obsidian:note:demo",
            "ref_kind": "obsidian_doc",
            "canonical_uuid": "canon-note",
            "l2b_uuid": "l2b-note-pointer",
            "owner_id": "nanobot:scan-42",
            "workspace_id": "workdesk",
            "related_node_uuid": "existing-node",
            "dry_run": False,
            "operator_mode": True,
        },
        intent_workspace=workspace,
        identity_index=index,
        l2b_graph=graph,
    )

    data = applied["data"]
    staged = workspace.fetch(data["intent_workspace"]["ref_id"])
    ref_record = index.refs["obsidian:note:demo"]
    pointer_node = graph.get_node("l2b-note-pointer")
    edges = graph.all_edges()

    assert applied["action"] == "memory.workspace_ref_sync.apply"
    assert applied["success"] is True
    assert data["intent_workspace_write"] is True
    assert data["identity_ref_index_write"] is True
    assert data["direct_l2b_write"] is True
    assert staged is not None
    assert staged.payload == source_doc
    assert workspace.get_owner(staged.ref_id) == "nanobot:scan-42"
    assert ref_record.locators == [str(source_doc)]
    assert ref_record.meta["workspace_sync"]["intent_workspace_ref_id"] == staged.ref_id
    assert pointer_node is not None
    assert pointer_node.meta["payload_policy"] == "pointer_only_no_inline_large_payload"
    assert pointer_node.source_meta["ref_id"] == "obsidian:note:demo"
    assert any(
        src.uuid == "existing-node"
        and dst.uuid == "l2b-note-pointer"
        and edge.kind == EdgeKind.HAS_REF
        for src, dst, edge in edges
    )


@pytest.mark.asyncio
async def test_workspace_ref_sync_apply_refuses_missing_local_path_for_staging(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing.pdf"

    applied = await apply_workspace_ref_sync(
        {
            "locator": str(missing),
            "dry_run": False,
            "operator_mode": True,
        },
        intent_workspace=IntentWorkspace(),
        identity_index=MemoryIdentityRefIndex(path=tmp_path / "index.json"),
        l2b_graph=L2BGraph(),
    )

    assert applied["success"] is False
    assert applied["data"]["error"] == "cannot_stage_missing_local_path"
    assert applied["data"]["mutated"] is False
