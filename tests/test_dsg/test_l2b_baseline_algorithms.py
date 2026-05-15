"""Phase 4 L2-B baseline algorithms — connected-components clustering +
iterative spreading activation + cross-compartment edge tagging.
"""

from __future__ import annotations

import pytest

from parrot.dsg.l2b import (
    Cluster,
    ClusterResult,
    ConnectedComponentsClusterStrategy,
    NoOpClusterStrategy,
)
from parrot.dsg.l2b.attention.mechanism import (
    BoundedBfsActivation,
    IterativeSpreadingActivation,
    SpreadingActivationPlaceholder,
)
from parrot.dsg.l2b_graph import L2BGraph
from parrot.dsg.l2b_types import EdgeKind, NodeKind, SemanticEdge, SemanticNode


# ─── Helpers ────────────────────────────────────────────────────────


def _node(label: str, **kwargs) -> SemanticNode:
    return SemanticNode(label=label, kind=NodeKind.OBJECT, **kwargs)


# ─── ConnectedComponents baseline ────────────────────────────────────


def test_connected_components_two_disjoint_clusters() -> None:
    g = L2BGraph()
    a, b, c, d = _node("a"), _node("b"), _node("c"), _node("d")
    for n in (a, b, c, d):
        g.upsert_node(n)
    g.connect(a.uuid, b.uuid)
    g.connect(c.uuid, d.uuid)

    result = ConnectedComponentsClusterStrategy().detect(g)
    assert isinstance(result, ClusterResult)
    assert len(result.clusters) == 2
    sizes = sorted(c.size() for c in result.clusters)
    assert sizes == [2, 2]


def test_connected_components_singletons() -> None:
    g = L2BGraph()
    a = _node("a")
    g.upsert_node(a)
    result = ConnectedComponentsClusterStrategy().detect(g)
    assert len(result.clusters) == 1
    assert result.clusters[0].size() == 1


def test_connected_components_deterministic_id() -> None:
    g = L2BGraph()
    a, b = _node("a"), _node("b")
    g.upsert_node(a)
    g.upsert_node(b)
    g.connect(a.uuid, b.uuid)

    r1 = ConnectedComponentsClusterStrategy().detect(g)
    r2 = ConnectedComponentsClusterStrategy().detect(g)
    assert r1.clusters[0].cluster_id == r2.clusters[0].cluster_id


def test_connected_components_node_filter() -> None:
    g = L2BGraph()
    a = _node("a", attention=0.9)
    b = _node("b", attention=0.1)
    g.upsert_node(a)
    g.upsert_node(b)
    g.connect(a.uuid, b.uuid)

    result = ConnectedComponentsClusterStrategy().detect(
        g,
        node_filter=lambda n: n.attention >= 0.5,
    )
    assert len(result.clusters) == 1
    assert result.clusters[0].size() == 1
    assert result.clusters[0].member_uuids[0] == a.uuid


def test_no_op_cluster_strategy() -> None:
    g = L2BGraph()
    g.upsert_node(_node("a"))
    g.upsert_node(_node("b"))
    result = NoOpClusterStrategy().detect(g)
    assert len(result.clusters) == 2
    assert all(c.size() == 1 for c in result.clusters)


# ─── Iterative Spreading Activation ─────────────────────────────────


def test_iterative_spreading_basic_decay() -> None:
    g = L2BGraph()
    a = _node("a", evidence_score=1.0)
    b = _node("b", evidence_score=1.0)
    c = _node("c", evidence_score=1.0)
    for n in (a, b, c):
        g.upsert_node(n)
    g.connect(a.uuid, b.uuid, SemanticEdge(strength=1.0))
    g.connect(b.uuid, c.uuid, SemanticEdge(strength=1.0))

    spread = IterativeSpreadingActivation(decay=0.7, epsilon=0.0001, max_iter=5)
    ranked = spread.activate(g, seed_uuids=(a.uuid,), max_depth=4, top_k=10)
    by_uuid = dict(ranked)
    # Seed has the highest score, then b, then c (decay each hop)
    assert by_uuid[a.uuid] >= by_uuid.get(b.uuid, 0.0)
    assert by_uuid.get(b.uuid, 0.0) >= by_uuid.get(c.uuid, 0.0)


def test_iterative_spreading_hop_cap_at_4() -> None:
    g = L2BGraph()
    chain = [_node(f"n{i}", evidence_score=1.0) for i in range(8)]
    for n in chain:
        g.upsert_node(n)
    for i in range(7):
        g.connect(chain[i].uuid, chain[i + 1].uuid, SemanticEdge(strength=1.0))

    spread = IterativeSpreadingActivation(decay=0.9, epsilon=1e-9, max_iter=20)
    ranked = spread.activate(g, seed_uuids=(chain[0].uuid,), max_depth=99)
    by_uuid = dict(ranked)
    # AGCN hard cap: nodes at hop > 4 should be unreachable.
    assert chain[5].uuid not in by_uuid or by_uuid[chain[5].uuid] == 0.0
    assert chain[7].uuid not in by_uuid


def test_iterative_spreading_cross_compartment_downweighted() -> None:
    g = L2BGraph()
    a = _node("a", event_id="ev_a", evidence_score=1.0)
    b_same = _node("b_same", event_id="ev_a", evidence_score=1.0)
    b_xc = _node("b_xc", event_id="ev_b", evidence_score=1.0)
    for n in (a, b_same, b_xc):
        g.upsert_node(n)
    # connect() auto-tags cross_compartment for ev_a -> ev_b
    g.connect(a.uuid, b_same.uuid, SemanticEdge(strength=1.0))
    g.connect(a.uuid, b_xc.uuid, SemanticEdge(strength=1.0))

    spread = IterativeSpreadingActivation(
        decay=0.7,
        epsilon=1e-9,
        max_iter=2,
        cross_compartment_weight=0.3,
    )
    ranked = spread.activate(g, seed_uuids=(a.uuid,), max_depth=2, top_k=10)
    by_uuid = dict(ranked)
    assert by_uuid[b_same.uuid] > by_uuid[b_xc.uuid]


def test_iterative_spreading_validation() -> None:
    with pytest.raises(ValueError):
        IterativeSpreadingActivation(decay=0)
    with pytest.raises(ValueError):
        IterativeSpreadingActivation(epsilon=0)
    with pytest.raises(ValueError):
        IterativeSpreadingActivation(max_iter=0)


def test_spreading_placeholder_alias() -> None:
    """Backward-compat alias still works."""
    g = L2BGraph()
    a = _node("a", evidence_score=1.0)
    b = _node("b", evidence_score=1.0)
    g.upsert_node(a)
    g.upsert_node(b)
    g.connect(a.uuid, b.uuid)

    placeholder = SpreadingActivationPlaceholder(decay=0.5)
    ranked = placeholder.activate(g, seed_uuids=(a.uuid,))
    assert ranked


def test_bounded_bfs_still_default_baseline() -> None:
    """``BoundedBfsActivation`` remains the registry default."""
    from parrot.dsg.l2b.attention.mechanism import (
        get_attention_mechanism,
        register_attention_mechanism,
    )

    register_attention_mechanism(BoundedBfsActivation())
    assert isinstance(get_attention_mechanism(), BoundedBfsActivation)


# ─── Cross-compartment edge tagging ─────────────────────────────────


def test_connect_tags_cross_event_edges() -> None:
    g = L2BGraph()
    a = _node("a", event_id="ev_a")
    b = _node("b", event_id="ev_b")
    g.upsert_node(a)
    g.upsert_node(b)
    edge = SemanticEdge()
    g.connect(a.uuid, b.uuid, edge)
    assert edge.meta.get("cross_compartment") == "event"
    axes = edge.meta.get("cross_compartment_axes")
    assert axes is not None and "event" in axes


def test_connect_no_cross_tag_for_same_compartment() -> None:
    g = L2BGraph()
    a = _node("a", event_id="ev", bucket_id="main", scene_type="desktop")
    b = _node("b", event_id="ev", bucket_id="main", scene_type="desktop")
    g.upsert_node(a)
    g.upsert_node(b)
    edge = SemanticEdge()
    g.connect(a.uuid, b.uuid, edge)
    assert "cross_compartment" not in edge.meta


def test_connect_tags_cross_bucket_edges() -> None:
    g = L2BGraph()
    a = _node("a", bucket_id="main")
    b = _node("b", bucket_id="roleplay_temp")
    g.upsert_node(a)
    g.upsert_node(b)
    edge = SemanticEdge()
    g.connect(a.uuid, b.uuid, edge)
    assert edge.meta.get("cross_compartment") == "bucket"


# ─── Phase 4 § 8 L13 guard — clustering must not export Attention ───


def test_clustering_module_does_not_export_attention_symbol() -> None:
    from parrot.dsg.l2b import clustering as mod

    public = {n for n in dir(mod) if not n.startswith("_")}
    assert "Attention" not in public, public


def test_edge_update_and_remove_use_endpoint_filters_not_rustworkx_indexes() -> None:
    g = L2BGraph()
    a = _node("a")
    b = _node("b")
    g.upsert_node(a)
    g.upsert_node(b)
    assert g.connect(
        a.uuid,
        b.uuid,
        SemanticEdge(kind=EdgeKind.ASSOCIATED_WITH, strength=0.4, source="web_console"),
    )

    updated = g.update_edge_between(
        a.uuid,
        b.uuid,
        SemanticEdge(
            kind=EdgeKind.REMINDS_OF,
            strength=0.9,
            source="web_console",
            meta={"operator_note": "preview_update"},
        ),
        match_kind="associated_with",
        match_source="web_console",
    )
    assert updated is True
    edges = g.all_edges()
    assert len(edges) == 1
    _, _, edge = edges[0]
    assert edge.kind == EdgeKind.REMINDS_OF
    assert edge.strength == 0.9
    assert edge.meta["operator_note"] == "preview_update"

    # The previous filter no longer matches after update; callers must match
    # on the current payload, not stale UI text or a RustWorkX edge index.
    assert g.remove_edge_between(a.uuid, b.uuid, match_kind="associated_with") is False
    assert g.remove_edge_between(a.uuid, b.uuid, match_kind="reminds_of") is True
    assert g.all_edges() == []
