"""L2-B graph views — lazy filters over the single PyDiGraph.

Views are **NOT** subgraphs in the RustworkX sense; they're filtered
node lists. The single graph remains canonical. P3+ may upgrade to
``rustworkx.subgraph()`` lazy views if performance demands it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from parrot.dsg.l2b_graph import L2BGraph
    from parrot.dsg.l2b_types import NodeKind, SemanticNode


def _iter_nodes(graph: "L2BGraph") -> Iterable["SemanticNode"]:
    return graph.all_nodes()


def view_by_bucket(graph: "L2BGraph", bucket_id: str) -> list:
    """Return nodes whose ``bucket_id`` matches."""
    return [n for n in _iter_nodes(graph) if n.bucket_id == bucket_id]


def view_by_event(graph: "L2BGraph", event_id: str) -> list:
    """Return nodes whose IntentEvent ``event_id`` matches."""
    return [n for n in _iter_nodes(graph) if n.event_id == event_id]


def view_by_scene(graph: "L2BGraph", scene_type: str) -> list:
    """Return nodes whose ``scene_type`` matches."""
    return [n for n in _iter_nodes(graph) if n.scene_type == scene_type]


def view_by_location(graph: "L2BGraph", location_tag: str) -> list:
    """Return nodes whose ``location_tag`` matches."""
    return [n for n in _iter_nodes(graph) if n.location_tag == location_tag]


def view_by_kind(graph: "L2BGraph", kind: "NodeKind") -> list:
    """Return nodes whose ``kind`` matches. Convenience wrapper —
    L2BGraph already exposes ``query_by_kind`` but going through the
    views API keeps the call-sites uniform."""
    return graph.query_by_kind(kind)


__all__ = [
    "view_by_bucket",
    "view_by_event",
    "view_by_kind",
    "view_by_location",
    "view_by_scene",
]
