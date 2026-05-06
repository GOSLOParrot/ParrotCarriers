"""DSG-POOL-V1 § 2.3 — RefTable lightweight UUID/path binding."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from parrot.dsg.l1_5.ref_table import (
    RefHealthStatus,
    RefKind,
    RefTable,
)


def test_bind_ref_idempotent() -> None:
    rt = RefTable()
    b1 = rt.bind_ref("node_a", RefKind.PHOTO_PATH, "data/x.jpg")
    b2 = rt.bind_ref("node_a", RefKind.PHOTO_PATH, "data/x.jpg")
    # Re-bind updates row but doesn't double-register
    assert rt.total_bindings() == 1
    assert b1.node_uuid == b2.node_uuid == "node_a"


def test_lookup_by_ref_returns_node_uuid() -> None:
    rt = RefTable()
    rt.bind_ref("node_a", RefKind.OBSIDIAN_UUID, "obs_123")
    assert rt.lookup_by_ref(RefKind.OBSIDIAN_UUID, "obs_123") == "node_a"


def test_lookup_returns_none_when_unbound() -> None:
    rt = RefTable()
    assert rt.lookup_by_ref(RefKind.URL, "http://x") is None


def test_list_refs_of_node_aggregates() -> None:
    rt = RefTable()
    rt.bind_ref("n1", RefKind.OBSIDIAN_UUID, "obs1")
    rt.bind_ref("n1", RefKind.PHOTO_PATH, "data/p.jpg")
    rt.bind_ref("n1", RefKind.URL, "http://example.com")
    refs = rt.list_refs_of_node("n1")
    kinds = {r.kind for r in refs}
    assert kinds == {RefKind.OBSIDIAN_UUID, RefKind.PHOTO_PATH, RefKind.URL}


def test_unbind_ref_removes_row() -> None:
    rt = RefTable()
    rt.bind_ref("n1", RefKind.URL, "http://x")
    assert rt.unbind_ref(RefKind.URL, "http://x") is True
    assert rt.lookup_by_ref(RefKind.URL, "http://x") is None
    assert rt.unbind_ref(RefKind.URL, "http://x") is False


def test_unbind_all_for_node_clears_all_kinds() -> None:
    rt = RefTable()
    rt.bind_ref("n1", RefKind.OBSIDIAN_UUID, "obs1")
    rt.bind_ref("n1", RefKind.URL, "http://x")
    n = rt.unbind_all_for_node("n1")
    assert n == 2
    assert rt.list_refs_of_node("n1") == []


def test_clear_intent_workspace_ref_keeps_binding() -> None:
    """Clearing the IntentWorkspace pointer must not unbind the ref."""
    rt = RefTable()
    rt.bind_ref(
        "n1", RefKind.PHOTO_PATH, "data/x.jpg",
        intent_workspace_ref_id="ws_42",
    )
    cleared = rt.clear_intent_workspace_ref("ws_42")
    assert cleared == 1
    binding = rt.list_refs_of_node("n1")[0]
    assert binding.intent_workspace_ref_id == ""
    # underlying binding still exists
    assert rt.lookup_by_ref(RefKind.PHOTO_PATH, "data/x.jpg") == "n1"


async def test_verify_ref_healthy_for_existing_file() -> None:
    rt = RefTable()
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(b"x")
        path = Path(f.name)
    try:
        binding = rt.bind_ref("n1", RefKind.PHOTO_PATH, str(path))
        health = await rt.verify_ref(binding)
        assert health.status == RefHealthStatus.HEALTHY
    finally:
        path.unlink(missing_ok=True)


async def test_verify_ref_broken_for_missing_file() -> None:
    rt = RefTable()
    binding = rt.bind_ref("n1", RefKind.PHOTO_PATH, "/nonexistent/file.jpg")
    health = await rt.verify_ref(binding)
    assert health.status == RefHealthStatus.BROKEN


async def test_verify_ref_skips_url() -> None:
    rt = RefTable()
    binding = rt.bind_ref("n1", RefKind.URL, "http://example.com")
    health = await rt.verify_ref(binding)
    assert health.status in (RefHealthStatus.UNVERIFIED, RefHealthStatus.STALE)
