"""Read-only L2-B snapshot DTOs for smoke monitors.

The Web console should inspect the current working-memory graph without
learning RustworkX internals or mutating L2-B. This module exports a compact
node/edge JSON shape suitable for a temporary dashboard or Unity smoke read.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from parrot.dsg.l2b_graph import L2BGraph


@dataclass(frozen=True)
class L2BGraphSnapshot:
    """Serializable read model for L2-B visualization."""

    node_count: int
    edge_count: int
    nodes: tuple[dict[str, Any], ...]
    edges: tuple[dict[str, Any], ...]

    def as_json(self) -> dict[str, Any]:
        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "nodes": list(self.nodes),
            "edges": list(self.edges),
        }


def build_l2b_snapshot(graph: L2BGraph | None = None, *, limit: int = 80) -> L2BGraphSnapshot:
    """Build a bounded read-only snapshot from the current L2-B graph."""
    if graph is None:
        from parrot.dsg.l2b_graph import get_l2b_graph

        graph = get_l2b_graph()

    nodes = graph.all_nodes()[: max(0, limit)]
    node_ids = {node.uuid for node in nodes}
    all_edges = graph.all_edges()
    node_payloads = tuple(_node_payload(node) for node in nodes)
    edge_payloads = tuple(
        _edge_payload(src, dst, edge)
        for src, dst, edge in all_edges
        if src.uuid in node_ids and dst.uuid in node_ids
    )
    return L2BGraphSnapshot(
        node_count=graph.node_count(),
        edge_count=len(all_edges),
        nodes=node_payloads,
        edges=edge_payloads,
    )


def _node_payload(node: Any) -> dict[str, Any]:
    return {
        "uuid": node.uuid,
        "label": node.label,
        "kind": getattr(node.kind, "value", str(node.kind)),
        "description": node.description,
        "tags": list(node.tags or []),
        "attention": float(node.attention),
        "novelty": float(node.novelty),
        "evidence_score": float(node.evidence_score),
        "salience": getattr(node.salience, "value", str(node.salience)),
        "confirmation": getattr(node.confirmation, "value", str(node.confirmation)),
        "bucket_id": node.bucket_id,
        "event_id": node.event_id,
        "scene_type": node.scene_type,
        "location_tag": node.location_tag,
        "source": node.source,
        "source_meta": dict(node.source_meta or {}),
        "meta": dict(node.meta or {}),
    }


def _edge_payload(src: Any, dst: Any, edge: Any) -> dict[str, Any]:
    meta = dict(edge.meta or {})
    return {
        "source": src.uuid,
        "target": dst.uuid,
        "kind": getattr(edge.kind, "value", str(edge.kind)),
        "strength": float(edge.strength),
        "edge_source": edge.source,
        "created_at": float(edge.created_at),
        "cross_compartment": meta.get("cross_compartment", ""),
        "meta": meta,
    }


__all__ = ["L2BGraphSnapshot", "build_l2b_snapshot"]
