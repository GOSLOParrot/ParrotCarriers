"""L0 Raw Event Stream schema — the single source of truth for state changes.

Sprint 0 S0.A locks the envelope shape. There is **no write-side integration**
in this module; Sprint 1's dispatcher will produce these envelopes and push
them to Redis Stream `STREAM_EVENT_LOG`.

Architecture (from `sprint0_preflight.md §1.3`):

    L0 Raw Event Stream  (Redis Stream `parrot.events.log`)   ← single writer
        │
        ├── projection ──> L1 Blackboard        (current state snapshot)
        ├── projection ──> L2 Graphiti Episode  (Turn Calendar, Gist-level)
        └── projection ──> L3 DSG L2-B Event    (Event Calendar, Fact-level)

Envelope fields:
    ts                 Unix epoch seconds (float, defaults to time.time())
    kind               free-form event-type string; vocabulary is deliberately
                       left open in Sprint 0 and will be frozen by the Sprint 1
                       dispatcher once real write sites exist
    layer              scheduling-layer tag (reflex / intent / task); this is
                       orthogonal to the architectural tier in `shared.types.Layer`
                       (L1 / L2 / L3) — do not confuse the two
    actor              producing component, e.g. "brain.agent", "scheduler.router"
    payload            arbitrary JSON-serializable dict
    provenance_parent  optional Redis Stream id of the causal parent event;
                       enables Reverse Provenance Expansion (SEEM-style)

Why Pydantic v2 (and not dataclass like `telemetry.py` / `l2b_types.py`):
    - L0 is a cross-process protocol; runtime field validation is cheap insurance
    - pydantic v2 is already installed transitively via graphiti-core>=0.28
      (S0.A commit additionally makes the dependency explicit in pyproject.toml)
    - Aligns with Graphiti custom entity types used for Sprint 4 PhotoEvent

Related tasks (see sprint0_preflight.md):
    S0.B  — add `provenance_stream_id` field to dsg/l2b_types.py SemanticNode
    S0.C  — document the timeline API contract
    S0.P  — L2-B SemanticNode Pydantic migration (deferred, see §10.1)
"""

from __future__ import annotations

import json
import time
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EventLayer(str, Enum):
    """Scheduling-layer tag for a raw event.

    Distinct from `shared.types.Layer` (L1/L2/L3 architectural tier).
    Aligned with the three-tier scheduler and the CTHA / GR00T N1.6
    System-1/2 split referenced in `ar_feature_vision.md §3.5`:

        REFLEX  — ms-scale body reactions (finger perch, fly-to cursor)
        INTENT  — s-to-min scale mode/behavior adjustments (switch video_tier,
                  update soul_constraints) — only flips Blackboard state,
                  never dispatches Nanobot, never notifies Gemini
        TASK    — min+ scale externally dispatched work (Nanobot tasks,
                  tool calls, user-facing results)

    **Sprint 1 scope note**: Only REFLEX and TASK are routed end-to-end.
    INTENT is declared here so producers can tag events correctly, but the
    routing side (`scheduler.router.BTRouter.route`) explicitly raises
    `NotImplementedError` on INTENT events. Full Intent-layer dispatch
    (S2-Intent: autonomous visual-tier downgrades, constraint flips, etc.)
    is the main Sprint 2 deliverable; see `sprint1_plan_20260422.md` §5.2.
    """

    REFLEX = "reflex"
    INTENT = "intent"
    TASK = "task"


class EventEnvelope(BaseModel):
    """Immutable wrapper for a single L0 event.

    Producers MUST write every state-changing event into L0 via `to_xadd_fields()`
    before any derived tier (Blackboard / Graphiti Episode / L2-B Event Node)
    observes the change. The derived tiers are **read-only projections** and
    must never be written to directly.

    Pydantic config:
        frozen=True         enforces event-sourcing immutability (SEEM / eventure)
        extra="forbid"      reject unknown fields to catch schema drift early
        use_enum_values     kept False so `envelope.layer` is an EventLayer member
                            (easier to pattern-match in dispatcher code)
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        use_enum_values=False,
    )

    ts: float = Field(default_factory=time.time, gt=0.0)
    kind: str = Field(..., min_length=1, max_length=128)
    layer: EventLayer = EventLayer.TASK
    actor: str = Field(..., min_length=1, max_length=128)
    payload: dict[str, Any] = Field(default_factory=dict)
    provenance_parent: str | None = Field(default=None, max_length=64)

    def to_xadd_fields(self) -> dict[str, str]:
        """Encode as Redis XADD field dict (all values must be str or bytes).

        Payload is serialized as a single JSON string field; top-level metadata
        (ts, kind, layer, actor) stays in separate XADD fields so consumers can
        XRANGE-filter without JSON-decoding every entry.
        """
        return {
            "ts": f"{self.ts:.6f}",
            "kind": self.kind,
            "layer": self.layer.value,
            "actor": self.actor,
            "payload": json.dumps(self.payload, ensure_ascii=False, default=str),
            "provenance_parent": self.provenance_parent or "",
        }

    # Sprint 1 TODO — read-direction decoding (`from_xadd_fields`).
    # Intentionally left unimplemented per sprint0_preflight §6:
    # locking a consumer contract before any real consumer exists is the exact
    # "提前锁定" anti-pattern the tentative/ratified two-state machine fights.
    # When Sprint 1 adds a dispatcher consumer, add it here and bump this
    # module's status note accordingly.


__all__ = ["EventEnvelope", "EventLayer"]
