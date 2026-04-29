"""Sprint4 Phase 4 ⓒ — `RefBinding` schema.

Authoritative spec: ``architecture/sprint4_phase4_entry_20260430.md §8.7``
(Phase 4 weeks 6-7) + §3.2 (Ref outputs per tool).

A RefBinding is the **stable handle** that anchors a transient interaction
artifact (Focus / BBox / Photo / Sighting) to a durable graph entity (L2-B
Node, Graphiti UUID, Episode). Producers create RefBindings; consumers walk
them as opaque handles.

Why a dedicated module instead of folding into ``ecp_event``:
    EcpEvent is the **wire**; RefBinding is the **graph anchor**. They share
    serialization conventions (Pydantic + JSON-friendly) but diverge in
    lifecycle:

    * EcpEvent is append-only, dedup'd by event_id, expires from the dedup
      window after 60s.
    * RefBinding is mutable inside its host node's lifetime (anchor target may
      be re-resolved as L2-B candidates promote). Consumers must not assume
      RefBinding is frozen — only that the binding's ``ref_id`` is stable.

Phase 4 scope (locked in §8.7 W6-7): RefBinding is the load-bearing schema
for tool ③ (Focus / BBox → L2-B candidate weight) and tool ④ (Photo →
Episode + Focus/BBox provenance). Tool ② only emits SightingEvent (transient
EcpEvent); a SightingEvent that promotes to a stable subject becomes a
RefBinding by Sphase 5 (deferred).
"""

from __future__ import annotations

import os
import time
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def generate_ref_id() -> str:
    """Time-sortable ref_id with the same format as :func:`ecp_event.generate_event_id`.

    Format: ``ref_<ts_ms_hex>_<rand_hex>``. Kept symmetric with event_id for
    debugging — when a ref is created in response to an event, the two ids
    will sort within milliseconds of each other in audit logs.
    """
    ts_ms = int(time.time() * 1000)
    ts_hex = format(ts_ms, "012x")
    rand_hex = os.urandom(4).hex()
    return f"ref_{ts_hex}_{rand_hex}"


class RefKind(str, Enum):
    """What category of artifact this Ref anchors.

    Locked in §8.7. Adding a kind is backward compatible; renaming or removing
    is a schema_version bump on the producer's EcpEvent payload.
    """

    FOCUS = "focus"  # Focus magnifier anchor (tool ③)
    BBOX = "bbox"  # Bounding box anchor (tool ③)
    PHOTO = "photo"  # Photo node (tool ④)
    SIGHTING = "sighting"  # Sighting evidence (tool ②, Phase 5+ promotion)


class RefTargetKind(str, Enum):
    """What kind of durable entity the Ref points at.

    Phase 4 starter set; tool ② SightingEvent → ObjectNode promotion logic
    requires this enum to be stable, so adding values is preferred over
    renaming.
    """

    L2B_NODE = "l2b_node"  # rustworkx node id in DSG L2-B graph
    L2B_EDGE = "l2b_edge"  # rustworkx edge id in DSG L2-B graph
    GRAPHITI_UUID = "graphiti_uuid"  # Graphiti entity UUID
    EPISODE = "episode"  # Episode id (manage_episode-managed)
    UNRESOLVED = "unresolved"  # Ref created before target resolved (e.g. unknown object pending visual_match)


class RefBinding(BaseModel):
    """Anchor between a transient interaction artifact and a durable entity.

    Mutability note: ``target_kind`` and ``target_id`` MAY be updated when an
    UNRESOLVED ref later resolves (e.g. a Focus that anchors to "this thing"
    starts UNRESOLVED, then resolves to an L2B_NODE once visual_match returns).
    To keep audit clean, do NOT rewrite an existing RefBinding in place;
    create a new one with the same ``ref_id`` and bump ``revision``. Consumers
    that cache must check revision before assuming a cached copy is current.

    NOT FROZEN — see mutability note above. Other Phase 4 schemas (EcpEvent,
    EcpCommand, EcpAck) are frozen because they are wire envelopes; RefBinding
    is an in-graph attachment whose target field intentionally evolves.
    """

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    ref_id: str = Field(default_factory=generate_ref_id, min_length=1, max_length=64)
    revision: int = Field(default=1, ge=1)
    kind: RefKind
    target_kind: RefTargetKind = RefTargetKind.UNRESOLVED
    target_id: str = Field(default="", max_length=128)

    # Provenance — which event_id created this Ref. Lets consumers trace
    # forward (event → ref) and backward (ref → event) without a separate
    # join table. Required because Ref creation is always event-driven in
    # Phase 4.
    source_event_id: str = Field(..., min_length=1, max_length=64)

    # Optional human-readable label — useful for debug HUD and Inspector
    # readouts. Producers may leave empty.
    label: str = Field(default="", max_length=256)

    created_at: int = Field(default_factory=lambda: int(time.time() * 1000), ge=0)
    updated_at: int = Field(default_factory=lambda: int(time.time() * 1000), ge=0)
    meta: dict[str, Any] = Field(default_factory=dict)

    def with_resolved_target(
        self,
        *,
        target_kind: RefTargetKind,
        target_id: str,
        new_event_id: str | None = None,
    ) -> "RefBinding":
        """Return a new RefBinding with revision bumped + target resolved.

        Use this instead of mutating in place — keeps audit linear and lets
        consumers detect changes by comparing ``revision``. The ``ref_id``
        is preserved so external references (e.g. AttentionHint pointing at
        a Ref) keep working across resolution.
        """
        return self.model_copy(
            update={
                "revision": self.revision + 1,
                "target_kind": target_kind,
                "target_id": target_id,
                "source_event_id": new_event_id or self.source_event_id,
                "updated_at": int(time.time() * 1000),
            }
        )


__all__ = [
    "RefBinding",
    "RefKind",
    "RefTargetKind",
    "generate_ref_id",
]
