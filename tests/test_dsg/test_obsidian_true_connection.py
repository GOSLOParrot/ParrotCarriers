"""Obsidian three-profile true-connection tests."""

from __future__ import annotations

import pytest

import parrot.dsg.ingest.runner as ingest_runner_module
import parrot.dsg.l2b_graph as l2b_graph_module
from parrot.dsg.ingest.user_tag_filter import UserTagFilter
from parrot.dsg.l1_5 import BucketKind, L15Pool, RefKind, set_pool_for_test
from parrot.dsg.l2b_graph import L2BGraph
from parrot.dsg.l2b_types import NodeKind, SemanticNode


@pytest.fixture
def env():
    """Fresh graph and pool so ref-only notes cannot leak between tests."""
    graph = L2BGraph()
    pool = L15Pool()
    l2b_graph_module._instance = graph
    ingest_runner_module._runner = None
    set_pool_for_test(pool)
    yield graph, pool
    set_pool_for_test(None)
    ingest_runner_module._runner = None
    l2b_graph_module._instance = None


def test_user_tag_filter_preserves_obsidian_profile_and_metadata():
    outcome = UserTagFilter().process_tag({
        "label": "blue mug",
        "obsidian_uuid": "obs_1",
        "profile": "roleplay_setting",
        "kind": "object",
        "tags": ["cup"],
        "obsidian_path": "Vault/blue mug.md",
        "file_mtime": 123.0,
        "double_link_count": 2,
    })

    assert outcome.accepted == 1
    obs = outcome.observations[0]
    assert obs.meta["profile"] == "roleplay"
    assert obs.meta["obsidian_path"] == "Vault/blue mug.md"
    assert obs.meta["double_link_count"] == 2
    assert obs.kind == NodeKind.OBJECT


def test_user_tag_filter_allows_setting_note_without_uuid():
    outcome = UserTagFilter().process_tag({
        "label": "大小姐宅邸设定",
        "profile": "roleplay",
        "kind": "zone",
        "obsidian_path": "Vault/GOSLO_Setting_Mansion_Ojou_Household.md",
        "obsidian_note_key": "Vault/GOSLO_Setting_Mansion_Ojou_Household.md",
    })

    assert outcome.accepted == 1
    obs = outcome.observations[0]
    assert obs.obsidian_uuid == ""
    assert obs.meta["profile"] == "roleplay"
    assert obs.meta["obsidian_note_key"].endswith("Ojou_Household.md")


def test_user_tag_filter_requires_uuid_for_ref_profile():
    outcome = UserTagFilter().process_tag({
        "label": "blue mug",
        "profile": "ref",
        "kind": "object",
    })

    assert outcome.accepted == 0
    assert outcome.rejected == 1
    assert outcome.reason == "missing_ref_uuid"


@pytest.mark.asyncio
async def test_obsidian_daily_setting_without_uuid_enters_daily_bucket(env):
    graph, pool = env
    outcome = UserTagFilter().process_tag({
        "label": "blue mug daily setting",
        "profile": "daily",
        "kind": "object",
        "obsidian_note_key": "Vault/GOSLO_Test_Daily_Blue_Mug.md",
        "obsidian_path": "Vault/GOSLO_Test_Daily_Blue_Mug.md",
    })

    admit = await pool.admit(outcome.observations)

    assert len(admit.admitted_node_uuids) == 1
    handle = pool.get_bucket(BucketKind.OBSIDIAN_SETTING_DAILY)
    assert handle is not None
    assert admit.admitted_node_uuids[0] in handle.node_uuids
    node = graph.all_nodes()[0]
    assert node.obsidian_uuid == ""
    assert node.source_meta["profile"] == "daily"
    assert node.source_meta["obsidian_note_key"].endswith("Daily_Blue_Mug.md")


@pytest.mark.asyncio
async def test_obsidian_ref_profile_binds_existing_node_without_creating_node(env):
    graph, pool = env
    graph.upsert_node(SemanticNode(uuid="node_1", label="blue mug"))

    outcome = UserTagFilter().process_tag({
        "label": "blue mug",
        "obsidian_uuid": "obs_ref_1",
        "profile": "ref",
        "obsidian_path": "Vault/blue mug.md",
    })
    admit = await pool.admit(outcome.observations)

    assert graph.node_count() == 1
    assert admit.promoted == ("node_1",)
    assert pool.refs.lookup_by_ref(RefKind.OBSIDIAN_UUID, "obs_ref_1") == "node_1"
    daily = pool.get_bucket(BucketKind.OBSIDIAN_SETTING_DAILY)
    roleplay = pool.get_bucket(BucketKind.OBSIDIAN_SETTING_ROLEPLAY)
    assert daily is not None and "node_1" not in daily.node_uuids
    assert roleplay is not None and "node_1" not in roleplay.node_uuids


@pytest.mark.asyncio
async def test_obsidian_roleplay_profile_enters_roleplay_bucket(env):
    graph, pool = env
    outcome = UserTagFilter().process_tag({
        "label": "stage prop",
        "obsidian_uuid": "obs_role_1",
        "profile": "roleplay",
    })
    admit = await pool.admit(outcome.observations)

    assert len(admit.admitted_node_uuids) == 1
    handle = pool.get_bucket(BucketKind.OBSIDIAN_SETTING_ROLEPLAY)
    assert handle is not None
    assert admit.admitted_node_uuids[0] in handle.node_uuids
    node = graph.all_nodes()[0]
    assert node.source_meta["profile"] == "roleplay"
