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
    MENTIONS = "mentions"
    SAME_AS = "same_as"
    HAS_REF = "has_ref"
    HAS_EVIDENCE = "has_evidence"
    DERIVED_FROM = "derived_from"
    TEMPORAL_NEXT = "temporal_next"
    CONTAINS = "contains"
    LOCATED_ON = "located_on"
    LOCATED_NEAR = "located_near"
    GRAPHITI_FACT = "graphiti_fact"
    # Sprint4 Phase 4 W8 (2026-04-30, entry doc §8.1 L7) — Photo-specific
    # edges. Wiring connect() calls is mostly Phase 5+ (need full Episode
    # graph + ObjectNode candidate already in L2-B); the enum values land
    # in W8 so future wiring doesn't churn the schema.
    HAS_PHOTO = "has_photo"             # Episode  → PhotoNode
    CAPTURED_VIA = "captured_via"        # PhotoNode → Focus/BBox subject (Phase 5+)
    CANDIDATE_SUBJECT = "candidate_subject"  # PhotoNode → ObjectNode (only when known)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class EdgeViewClass(str, Enum):
    """Filter and algorithm classes for L2-B edge views."""

    SEMANTIC = "semantic"
    SPATIAL = "spatial"
    TEMPORAL = "temporal"
    EPISODIC = "episodic"
    IDENTITY = "identity"
    REF = "ref"
    EVIDENCE = "evidence"
    GRAPHITI = "graphiti"
    HIERARCHY = "hierarchy"


EDGE_KIND_VIEW_CLASSES: dict[EdgeKind, tuple[EdgeViewClass, ...]] = {
    EdgeKind.ASSOCIATED_WITH: (EdgeViewClass.SEMANTIC,),
    EdgeKind.REMINDS_OF: (EdgeViewClass.SEMANTIC,),
    EdgeKind.CO_OCCURRED: (EdgeViewClass.SEMANTIC, EdgeViewClass.TEMPORAL),
    EdgeKind.SPATIAL_CONTEXT: (EdgeViewClass.SPATIAL,),
    EdgeKind.PART_OF_EPISODE: (EdgeViewClass.EPISODIC, EdgeViewClass.HIERARCHY),
    EdgeKind.MENTIONS: (EdgeViewClass.SEMANTIC, EdgeViewClass.REF),
    EdgeKind.SAME_AS: (EdgeViewClass.IDENTITY,),
    EdgeKind.HAS_REF: (EdgeViewClass.REF,),
    EdgeKind.HAS_EVIDENCE: (EdgeViewClass.EVIDENCE, EdgeViewClass.REF),
    EdgeKind.DERIVED_FROM: (EdgeViewClass.REF, EdgeViewClass.EPISODIC),
    EdgeKind.TEMPORAL_NEXT: (EdgeViewClass.TEMPORAL, EdgeViewClass.EPISODIC),
    EdgeKind.CONTAINS: (EdgeViewClass.SPATIAL, EdgeViewClass.HIERARCHY),
    EdgeKind.LOCATED_ON: (EdgeViewClass.SPATIAL,),
    EdgeKind.LOCATED_NEAR: (EdgeViewClass.SPATIAL,),
    EdgeKind.GRAPHITI_FACT: (EdgeViewClass.GRAPHITI, EdgeViewClass.SEMANTIC),
    EdgeKind.HAS_PHOTO: (EdgeViewClass.EVIDENCE, EdgeViewClass.REF),
    EdgeKind.CAPTURED_VIA: (EdgeViewClass.EVIDENCE,),
    EdgeKind.CANDIDATE_SUBJECT: (EdgeViewClass.EVIDENCE, EdgeViewClass.IDENTITY),
}


def edge_view_classes(kind: EdgeKind | str) -> tuple[str, ...]:
    """Return stable classes used by filters, views, and graph algorithms."""

    try:
        normalized = kind if isinstance(kind, EdgeKind) else EdgeKind(str(kind))
    except ValueError:
        return (EdgeViewClass.SEMANTIC.value,)
    return tuple(
        item.value
        for item in EDGE_KIND_VIEW_CLASSES.get(normalized, (EdgeViewClass.SEMANTIC,))
    )


#  Node
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Source dispatch (Phase 4 → 5 transition, 2026-05-04)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# Phase 4 closed protocol upgrade with 0 drift; the next architectural seam
# (Phase 5+) is "different ingest sources should be able to drive different
# Node states / lifecycles / subclasses" (e.g. A10 CV pipeline produces
# nodes that need their own confidence-decay curves, while user-tagged
# Obsidian nodes never decay). The exact subclass split is **效果未知** —
# we don't know which dimensions will be load-bearing until DSG L1.5
# preloaded-pool design (separate chat) and the ConceptGraph distillation
# task (separate workspace, see `dsg_skill_seeker_l1_5_a10_l2a_*`) both
# land. Locking subclasses now would freeze the wrong axis.
#
# Decision (2026-05-04, recorded in ADR
# `adr_l1_5_source_dispatch_extension_space_20260504.md` + active_context):
#
#   Q1 — Where does source live? **Python only** (Brain L1.5 / L2-B /
#        Observation). Unity wire stays clean (EcpEventSource enum already
#        covers Unity-vs-Brain provenance). A10 is a Brain-side CV
#        pipeline that never touches Unity DataChannel, so adding a
#        source field on the Unity wire would be premature surface area.
#
#   Q2 — How to keep extension space? **Meta dict + factory hook hybrid.**
#        - SemanticNode.source: ObservationSource (the bare dispatch tag)
#        - SemanticNode.source_meta: dict[str, Any] (per-source extension
#          payload — e.g. A10 may stash `{"reid_hash": ..., "track_id":
#          ..., "yolo_class_votes": [...]}`; user-tagged may stash
#          `{"obsidian_path": ..., "tags": [...]}`. The dict is unstructured
#          BY DESIGN until we observe what fields actually matter.)
#        - SemanticNode.from_observation(obs) classmethod with a
#          _SOURCE_FACTORIES dict that lets new sources register custom
#          per-source builders WITHOUT subclassing SemanticNode (yet).
#
#        We did NOT pick mixin/subclass dispatch (option 3) because:
#        (a) effects unknown — locking inheritance now means refactoring
#        every isinstance check later when we discover the right axis;
#        (b) the IngestFilter layer already has the subclass dispatch
#        pattern available — pushing it down to Node level is structural
#        change, not protocol change.
#
# Future upgrade path (when to revisit):
#   - When L1.5 preloaded Node pool design (separate chat) lands and
#     reveals per-source state machines that diverge by ≥3 fields →
#     graduate from meta dict to typed dataclasses (still under one
#     SemanticNode parent, with `source_payload: A10NodeMeta | UserMeta
#     | ...` discriminated union).
#   - When ≥2 sources need behavior polymorphism (not just data shape) —
#     e.g. A10 nodes auto-decay confidence on `touch()` while user nodes
#     don't — graduate to subclass dispatch at the SemanticNode level.
#     This is the option-3 endgame.
#
# Until then: meta dict + factory hook stays as the extension surface.


# Built-in source factories registry (Phase 4 → 5 hybrid hook).
# Each entry maps an ObservationSource to a builder taking the Observation
# and returning the per-source `source_meta` payload. The default factory
# (None entry) returns an empty dict — most sources don't need custom
# state today. Adding a new factory is the correct place to grow per-
# source state without touching SemanticNode itself.
#
# Type kept loose (Callable, dict-typed) on purpose — when a factory's
# output schema stabilizes, promote it to a Pydantic model under
# `parrot.dsg.l2b_source_meta` (Phase 5+) without changing this signature.
#
# Lazy import at use-site (factory references Observation, which lives in
# dsg/ingest/base.py — circular if imported here at module load).


def _default_source_meta_factory(_obs: "Any") -> dict[str, Any]:
    """No per-source state — every existing source uses this in Phase 4."""
    return {}


_SOURCE_META_FACTORIES: dict[str, Any] = {}  # ObservationSource.value -> Callable


def register_source_meta_factory(source_value: str, factory: "Any") -> None:
    """Register a per-source meta builder. New CV/auth pipelines call this
    on import to add their own factory without touching SemanticNode.

    `source_value` is the ObservationSource enum's string value (e.g.
    `"cv_a10"`); we key on the value not the enum to keep this module
    free of `dsg.ingest.base` imports (avoids circular).
    """
    _SOURCE_META_FACTORIES[source_value] = factory


def _resolve_source_meta_factory(source_value: str):
    """Look up factory; fall back to default no-op."""
    return _SOURCE_META_FACTORIES.get(source_value, _default_source_meta_factory)


@dataclass
class SemanticNode:
    """L2-B working-memory node — one per recognized entity.

    Lifecycle:
        Graphiti preload → create node (EXPECTED) →
        L1/tool confirms → CONFIRMED →
        archive back to Graphiti on episode end

    Source dispatch (Phase 4 → 5 transition, 2026-05-04):
        See module docstring above. Short version:
          - `source` carries the ingest origin tag (was previously inferred
            via runner heuristic; now propagated explicitly).
          - `source_meta` is a free-form dict for per-source state that
            doesn't yet warrant a typed schema.
          - Use :meth:`from_observation` (classmethod) to construct from
            an Observation — it dispatches via `_SOURCE_META_FACTORIES`.
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

    # ── Informational tag fields (DSG-POOL-V1 / DSG-INTENT-EVENT-V1 /
    #    DSG-SCENE-V1, 2026-05-06) ──
    # All four are *labels*; they do not change behaviour by themselves.
    # The L1.5 Pool / IntentEventBoundary / SceneRegistry modules drive
    # behaviour through their own state. Adding these fields is additive
    # (Phase 4 § 8 L1 NodeKind / EdgeKind enum stay untouched).
    #
    # bucket_id   — L1.5 Bucket the node lives in (parrot.dsg.l1_5.buckets).
    #               Values: "main" / "obsidian_setting_daily" / etc.
    #               Default "main" so existing code paths land in the
    #               default bucket without any change.
    #
    # event_id    — Current IntentEvent the node belongs to (cognitive
    #               focus window). Empty = not yet associated with any
    #               IntentEvent. Strict naming: never "Event" alone (see
    #               dsg_protocol_intent_event_boundary_v1 § 0).
    #
    # scene_type  — SceneType label ("desktop" / "home_indoor" / ...).
    #               Empty = legacy / preloaded node without scene info.
    #
    # location_tag — Physical LocationTag ("desk" / "kitchen" / ...).
    #               Empty = no location attached yet.
    bucket_id: str = "main"
    event_id: str = ""
    scene_type: str = ""
    location_tag: str = ""

    # ── Source dispatch fields (Phase 4 → 5 transition, 2026-05-04) ──
    # See module-level "Source dispatch" comment above for the full
    # rationale (Q1: Python only / Q2: meta+factory hybrid / future
    # upgrade path).
    #
    # `source` is the string value of an ObservationSource enum (we keep
    # it as `str` not the enum class to avoid a circular import with
    # `dsg.ingest.base.ObservationSource` — runner sets it via
    # `obs.source.value`). Empty string = pre-Phase-4 node OR node
    # created without a source declaration; in that case
    # `runner._source_for_node()` falls back to identifier heuristics.
    source: str = ""

    # `source_meta` is the free-form per-source extension surface. Use
    # `register_source_meta_factory(source_value, factory)` to declare
    # what a new ingest source wants to stash here.
    source_meta: dict[str, Any] = field(default_factory=dict)

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

    @classmethod
    def from_observation(cls, obs: "Any") -> "SemanticNode":
        """Construct a SemanticNode from an Observation.

        Phase 4 → 5 transition factory: dispatches via
        `_SOURCE_META_FACTORIES` so new ingest sources can grow their own
        per-source `source_meta` payloads without touching this method.

        `obs: Any` keeps the type hint loose to avoid a circular import
        with `dsg.ingest.base.Observation`. Callers (currently
        `IngestRunner._observation_to_node`) pass a real Observation.

        See module-level "Source dispatch" comment for the full rationale
        and the future upgrade path (graduate to typed source_meta /
        subclass dispatch when L1.5 preloaded-pool design reveals which
        axis matters).
        """
        source_value = obs.source.value if hasattr(obs.source, "value") else str(obs.source)
        factory = _resolve_source_meta_factory(source_value)
        source_meta = factory(obs)

        return cls(
            kind=obs.kind,
            label=obs.label,
            graphiti_uuid=obs.graphiti_uuid,
            obsidian_uuid=obs.obsidian_uuid,
            description=obs.description,
            known_facts=[obs.description] if obs.description else [],
            confirmation=obs.confirmation,
            evidence_score=obs.confidence,
            attention=0.6 if obs.confirmation == ConfirmationStatus.CONFIRMED else 0.35,
            salience=Salience.ACTIVE,  # caller may override after construction
            reference_image_path=obs.reference_image_path,
            last_sighting_path=obs.last_sighting_path,
            time_span=obs.time_span,
            provenance_stream_id=obs.provenance_stream_id,
            source=source_value,
            source_meta=source_meta,
        )


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
    graphiti_uuid: str = ""
    source_graphiti_uuid: str = ""
    target_graphiti_uuid: str = ""
    ref_ids: tuple[str, ...] = ()
    view_classes: tuple[str, ...] = ()
    meta: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.view_classes:
            self.view_classes = edge_view_classes(self.kind)
        self.meta.setdefault("view_classes", tuple(self.view_classes))
        if self.graphiti_uuid:
            self.meta.setdefault("graphiti_uuid", self.graphiti_uuid)
        if self.source_graphiti_uuid:
            self.meta.setdefault("source_graphiti_uuid", self.source_graphiti_uuid)
        if self.target_graphiti_uuid:
            self.meta.setdefault("target_graphiti_uuid", self.target_graphiti_uuid)
        if self.ref_ids:
            self.meta.setdefault("ref_ids", tuple(self.ref_ids))


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
