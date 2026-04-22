"""L2-B DSG Node & Edge types — semantic working memory adapted for Graphiti.

Design decisions:
  - Nodes are working-memory enrichments of Graphiti EntityNodes
  - Each node stores its Graphiti UUID for bidirectional sync
  - Attention / novelty / habituation are runtime-only (not persisted)
  - Episode membership tracks which conversational segment a node belongs to
  - Edge types are minimal for now; add more as association patterns emerge
  - Sprint 0 S0.B: every node carries `provenance_stream_id` pointing back to
    the L0 Redis Stream event that created it (SEEM-style reverse provenance
    expansion). See `shared/event_log.py` and `sprint0_preflight.md §1.3`.

References:
  - Opus 17 §2: L2-B node hierarchy (adapted, not copied)
  - Opus 17 §3: Graphiti custom entity types
  - Graphiti SKILL: Entity/Fact/Episode model
  - sprint0_preflight.md §1 — 四层时间轴, §10.1 — L2-B Pydantic 迁移 deferred
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

    # ── Provenance (S0.B, points back to L0 Redis Stream) ──
    # Empty string = node predates the L0 stream or was created out-of-band
    # (e.g. legacy preload). Sprint 1 writers must populate this.
    provenance_stream_id: str = ""
    # Effective time span of the node as a semantic entity (NOT wall-clock
    # attention). first = earliest known sighting, second = latest known
    # sighting or None if still "currently in play". Unit: Unix epoch seconds.
    time_span: tuple[float, float | None] = (0.0, None)

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
    # S0.B: provenance back to the L0 event that created the edge.
    provenance_stream_id: str = ""
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
    # S0.B: L0 event id of the `episode_start` event.
    provenance_stream_id: str = ""

    @property
    def is_open(self) -> bool:
        return self.ended_at == 0.0

    def close(self, summary: str = "") -> None:
        self.ended_at = time.time()
        if summary:
            self.summary = summary
