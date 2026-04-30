"""L2-B DSG Node & Edge types — semantic working memory adapted for Graphiti.

Design decisions:
  - Nodes are working-memory enrichments of Graphiti EntityNodes
  - Each node stores its Graphiti UUID for bidirectional sync
  - Attention / novelty / habituation are runtime-only (not persisted)
  - Episode membership tracks which conversational segment a node belongs to
  - Edge types are minimal for now; add more as association patterns emerge

Sprint 0 Schema V1 (2026-04-22, see `.cursor/memory/architecture/sprint0_preflight.md`):
  - `provenance_stream_id`  — links node to its creating L0 EventEnvelope
  - `time_span`             — event time-range for EVENT-kind nodes
  - `reference_image_path`  — canonical image for identify_object / PhotoEvent
  - `last_sighting_path`    — rolling most-recent sighting
  All four are additive (defaults preserve existing call sites). The decision
  to keep SemanticNode as @dataclass (not Pydantic) is deferred — see
  sprint0_preflight.md §10.1 S0.P.

References:
  - Opus 17 §2: L2-B node hierarchy (adapted, not copied)
  - Opus 17 §3: Graphiti custom entity types
  - Graphiti SKILL: Entity/Fact/Episode model
  - audit_identify_object_no_screenshot_20260420.md §5.1 (B4) — image fields
  - ar_feature_vision.md §3.5 — provenance for three-layer consciousness
"""

from __future__ import annotations

import time
import uuid as uuid_lib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Enumerations
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class NodeKind(str, Enum):
    """The kind of real-world entity a semantic node represents."""
    OBJECT = "object"
    SURFACE = "surface"
    ZONE = "zone"
    PERSON = "person"
    EVENT = "event"
    # Sprint4 Phase 4 W8 (2026-04-30, entry doc §8.1 L7) — PhotoNode is the
    # L2-B representation of a user-captured photo. Distinct from OBJECT so
    # the rule "PhotoEvent does NOT auto-create unknown ObjectNodes"
    # (entry §8.1 L7) is enforceable at NodeKind level.
    PHOTO = "photo"


class Salience(str, Enum):
    """How prominent this node is in GOSLO's current attention."""
    ALERT = "alert"
    FOREGROUND = "foreground"
    ACTIVE = "active"
    BACKGROUND = "background"
    PERIPHERAL = "peripheral"


class ConfirmationStatus(str, Enum):
    """How well-confirmed this node is against reality."""
    EXPECTED = "expected"
    TENTATIVE = "tentative"
    UNCERTAIN = "uncertain"
    CONFIRMED = "confirmed"
    GHOST = "ghost"


class EdgeKind(str, Enum):
    """Semantic relationship types between L2-B nodes."""
    ASSOCIATED_WITH = "associated_with"
    REMINDS_OF = "reminds_of"
    CO_OCCURRED = "co_occurred"
    SPATIAL_CONTEXT = "spatial_context"
    PART_OF_EPISODE = "part_of_episode"
    # Sprint4 Phase 4 W8 (2026-04-30, entry doc §8.1 L7) — Photo-specific
    # edges. Wiring connect() calls is mostly Phase 5+ (need full Episode
    # graph + ObjectNode candidate already in L2-B); the enum values land
    # in W8 so future wiring doesn't churn the schema.
    HAS_PHOTO = "has_photo"             # Episode  → PhotoNode
    CAPTURED_VIA = "captured_via"        # PhotoNode → Focus/BBox subject (Phase 5+)
    CANDIDATE_SUBJECT = "candidate_subject"  # PhotoNode → ObjectNode (only when known)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Node
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class SemanticNode:
    """L2-B working-memory node — one per recognized entity.

    Lifecycle:
        Graphiti preload → create node (EXPECTED) →
        L1/tool confirms → CONFIRMED →
        archive back to Graphiti on episode end
    """

    # ── Identity (persisted via Graphiti) ──
    uuid: str = field(default_factory=lambda: str(uuid_lib.uuid4())[:12])
    kind: NodeKind = NodeKind.OBJECT
    label: str = ""
    graphiti_uuid: str = ""
    obsidian_uuid: str = ""

    # ── Graphiti-sourced semantic data ──
    category: str = ""
    description: str = ""
    known_facts: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    typical_location: str = ""

    # ── Runtime: attention system (not persisted) ──
    attention: float = 0.5
    novelty: float = 1.0
    habituation_count: int = 0
    salience: Salience = Salience.BACKGROUND
    last_attended: float = field(default_factory=time.time)

    # ── Runtime: confirmation state ──
    confirmation: ConfirmationStatus = ConfirmationStatus.EXPECTED
    evidence_score: float = 0.0

    # ── Runtime: episode tracking ──
    episode_id: str = ""
    first_seen_this_session: float = field(default_factory=time.time)
    last_seen_this_session: float = field(default_factory=time.time)
    interaction_count: int = 0

    # ── Sprint 0 Schema V1 additions (S0.B + audit B4) ──
    # Links this node back to its creating L0 event (Redis Stream id of the
    # EventEnvelope in `parrot.events.log`). Empty string = pre-S0 node or
    # node created before L0 stream was live. Used by Reverse Provenance
    # Expansion and archive filters (Sprint 4+).
    provenance_stream_id: str = ""

    # Event time-range for EVENT-kind nodes (start_ts, end_ts). `end_ts = None`
    # means open-ended (still ongoing). OBJECT/PERSON/SURFACE nodes may leave
    # this at the default; they carry their own first_seen/last_seen fields.
    time_span: tuple[float, float | None] = (0.0, None)

    # Canonical reference image for this entity — produced on first
    # identify_object confirmation or user upload. Path convention:
    #     data/snapshots/objects/{uuid}/reference.jpg
    reference_image_path: str = ""

    # Most recent sighting frame path, rotated weekly. Empty string until
    # first sighting is stored. Path convention:
    #     data/snapshots/sightings/{yyyy-mm-dd}/{ts}.jpg
    last_sighting_path: str = ""

    # ── Extensible metadata ──
    meta: dict[str, Any] = field(default_factory=dict)

    # ── RustworkX graph index (set by L2BGraph) ──
    _rx_index: int = -1

    def is_notable(self) -> bool:
        """Worth mentioning to Gemini?"""
        return self.attention > 0.4 or self.salience in (Salience.FOREGROUND, Salience.ALERT)

    def touch(self) -> None:
        """Mark as recently attended."""
        self.last_attended = time.time()
        self.last_seen_this_session = time.time()
        self.interaction_count += 1


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Edge
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class SemanticEdge:
    """L2-B relationship between two semantic nodes."""

    kind: EdgeKind = EdgeKind.ASSOCIATED_WITH
    strength: float = 0.5
    source: str = "observation"
    created_at: float = field(default_factory=time.time)
    meta: dict[str, Any] = field(default_factory=dict)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Episode marker
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class EpisodeMarker:
    """Marks a conversational/situational episode in the L2-B graph.

    Gemini creates these via tool; triggers can also create them.
    An episode groups nodes that were active during a time window.
    """

    episode_id: str = field(
        default_factory=lambda: f"ep_{int(time.time())}_{uuid_lib.uuid4().hex[:4]}"
    )
    title: str = ""
    started_at: float = field(default_factory=time.time)
    ended_at: float = 0.0
    summary: str = ""
    trigger_source: str = ""
    participating_node_uuids: list[str] = field(default_factory=list)
    archived_to_graphiti: bool = False

    @property
    def is_open(self) -> bool:
        return self.ended_at == 0.0

    def close(self, summary: str = "") -> None:
        self.ended_at = time.time()
        if summary:
            self.summary = summary
