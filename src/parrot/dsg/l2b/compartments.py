"""L2-B Compartment — topological grouping concept (lazy view).

Compartment is the **L2-B-domain** name for grouping nodes by event /
bucket / scene / kind axis. It is NOT stored as a separate graph; it
is a lazy view materialized through ``parrot.dsg.l2b.views``.

Cross-compartment edges:
    A SemanticEdge is "cross-compartment" if its endpoints lie in
    different compartments along the chosen axis. We tag such edges in
    ``edge.meta["cross_compartment"] = axis_name`` so attention /
    spreading-activation strategies (P3) can up- or down-weight them.

Naming hard rule (主设计稿 § 0.2):
    "Compartment" is L2-B-only. Don't mix with "Bucket" (L1.5 term).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from parrot.dsg.l2b_types import SemanticNode


class CompartmentKind(str, Enum):
    """Axis along which the Compartment is sliced."""

    EVENT = "event"          # by node.event_id
    BUCKET = "bucket"        # by node.bucket_id
    SCENE = "scene"          # by node.scene_type
    LOCATION = "location"    # by node.location_tag
    KIND = "kind"            # by node.kind


@dataclass(frozen=True)
class Compartment:
    """Identity tuple — (kind, value).

    Example: Compartment(kind=CompartmentKind.EVENT, value="ev_abc123")
    """

    kind: CompartmentKind
    value: str

    def matches(self, node: "SemanticNode") -> bool:
        if self.kind == CompartmentKind.EVENT:
            return node.event_id == self.value
        if self.kind == CompartmentKind.BUCKET:
            return node.bucket_id == self.value
        if self.kind == CompartmentKind.SCENE:
            return node.scene_type == self.value
        if self.kind == CompartmentKind.LOCATION:
            return node.location_tag == self.value
        if self.kind == CompartmentKind.KIND:
            return node.kind.value == self.value
        return False


def is_cross_compartment_edge(
    src: "SemanticNode",
    dst: "SemanticNode",
    axis: CompartmentKind,
) -> bool:
    """Check if an edge spans two compartments along ``axis``."""
    if axis == CompartmentKind.EVENT:
        return src.event_id != dst.event_id
    if axis == CompartmentKind.BUCKET:
        return src.bucket_id != dst.bucket_id
    if axis == CompartmentKind.SCENE:
        return src.scene_type != dst.scene_type
    if axis == CompartmentKind.LOCATION:
        return src.location_tag != dst.location_tag
    if axis == CompartmentKind.KIND:
        return src.kind != dst.kind
    return False


__all__ = [
    "Compartment",
    "CompartmentKind",
    "is_cross_compartment_edge",
]
