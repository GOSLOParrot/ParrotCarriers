"""L2-B views + Compartment dataclass coverage."""

from __future__ import annotations

import pytest

from parrot.dsg.l2b import (
    Compartment,
    CompartmentKind,
    is_cross_compartment_edge,
    view_by_bucket,
    view_by_event,
    view_by_kind,
    view_by_location,
    view_by_scene,
)
from parrot.dsg.l2b_graph import L2BGraph
from parrot.dsg.l2b_types import NodeKind, SemanticNode


@pytest.fixture
def graph_with_tagged_nodes():
    g = L2BGraph()
    g.upsert_node(SemanticNode(
        label="cup", kind=NodeKind.OBJECT,
        bucket_id="main", event_id="ev_a",
        scene_type="desktop", location_tag="desk",
    ))
    g.upsert_node(SemanticNode(
        label="couch", kind=NodeKind.OBJECT,
        bucket_id="obsidian_setting_daily", event_id="ev_a",
        scene_type="home_indoor", location_tag="living_room",
    ))
    g.upsert_node(SemanticNode(
        label="ph", kind=NodeKind.PHOTO,
        bucket_id="main", event_id="ev_b",
        scene_type="desktop", location_tag="desk",
    ))
    return g


def test_view_by_bucket(graph_with_tagged_nodes: L2BGraph) -> None:
    main = view_by_bucket(graph_with_tagged_nodes, "main")
    labels = sorted(n.label for n in main)
    assert labels == ["cup", "ph"]


def test_view_by_event(graph_with_tagged_nodes: L2BGraph) -> None:
    ev_a = view_by_event(graph_with_tagged_nodes, "ev_a")
    assert sorted(n.label for n in ev_a) == ["couch", "cup"]


def test_view_by_scene(graph_with_tagged_nodes: L2BGraph) -> None:
    desktop = view_by_scene(graph_with_tagged_nodes, "desktop")
    assert sorted(n.label for n in desktop) == ["cup", "ph"]


def test_view_by_location(graph_with_tagged_nodes: L2BGraph) -> None:
    desk = view_by_location(graph_with_tagged_nodes, "desk")
    assert sorted(n.label for n in desk) == ["cup", "ph"]


def test_view_by_kind(graph_with_tagged_nodes: L2BGraph) -> None:
    photos = view_by_kind(graph_with_tagged_nodes, NodeKind.PHOTO)
    assert len(photos) == 1 and photos[0].label == "ph"


def test_compartment_matches() -> None:
    n = SemanticNode(label="x", event_id="ev_a", bucket_id="main", scene_type="desktop")
    assert Compartment(kind=CompartmentKind.EVENT, value="ev_a").matches(n)
    assert Compartment(kind=CompartmentKind.BUCKET, value="main").matches(n)
    assert Compartment(kind=CompartmentKind.SCENE, value="desktop").matches(n)
    assert not Compartment(kind=CompartmentKind.EVENT, value="ev_b").matches(n)


def test_is_cross_compartment_edge_event_axis() -> None:
    a = SemanticNode(label="a", event_id="ev_a")
    b = SemanticNode(label="b", event_id="ev_b")
    c = SemanticNode(label="c", event_id="ev_a")
    assert is_cross_compartment_edge(a, b, CompartmentKind.EVENT)
    assert not is_cross_compartment_edge(a, c, CompartmentKind.EVENT)


def test_is_cross_compartment_edge_bucket_axis() -> None:
    a = SemanticNode(label="a", bucket_id="main")
    b = SemanticNode(label="b", bucket_id="roleplay_temp")
    assert is_cross_compartment_edge(a, b, CompartmentKind.BUCKET)
