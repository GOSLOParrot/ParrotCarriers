"""Tests for L2-B SemanticNode source dispatch (Phase 4 → 5 transition).

Authoritative spec:
    - `architecture/adr_l1_5_source_dispatch_extension_space_20260504.md`
    - `src/parrot/dsg/l2b_types.py` "Source dispatch" module-level comment
      (Q1 / Q2 decisions + future upgrade path)

Coverage focus:
    1. SemanticNode default `source=""` + `source_meta={}` (backward compat
       with pre-Phase-4 construction)
    2. `from_observation()` factory propagates `obs.source.value` to
       `node.source`
    3. `from_observation()` invokes `_SOURCE_META_FACTORIES` lookup; default
       (no factory) yields empty dict
    4. `register_source_meta_factory()` lets a new source plug in custom
       per-source meta payload without touching SemanticNode (extension
       space proof)
    5. `IngestRunner._observation_to_node` round-trips source value
    6. `_source_for_node()` prefers `node.source` when set; falls back to
       identifier heuristic when empty (backward compat)
    7. Unknown source string in node.source falls through to heuristic
       (forward compat with newer pipelines)
"""

from __future__ import annotations

import pytest

from parrot.dsg.ingest.base import (
    Observation,
    ObservationSource,
)
from parrot.dsg.ingest.runner import IngestRunner, _source_for_node
from parrot.dsg.l2b_types import (
    ConfirmationStatus,
    NodeKind,
    Salience,
    SemanticNode,
    _SOURCE_META_FACTORIES,
    register_source_meta_factory,
)


@pytest.fixture(autouse=True)
def _isolate_factories():
    """Snapshot + restore the source-factory registry around each test
    so register_source_meta_factory tests don't leak across cases."""
    snapshot = dict(_SOURCE_META_FACTORIES)
    yield
    _SOURCE_META_FACTORIES.clear()
    _SOURCE_META_FACTORIES.update(snapshot)


def _obs(
    *,
    source: ObservationSource = ObservationSource.GEMINI_ORAL,
    label: str = "test_node",
    confidence: float = 0.5,
    confirmation: ConfirmationStatus = ConfirmationStatus.TENTATIVE,
    graphiti_uuid: str = "",
    obsidian_uuid: str = "",
    description: str = "",
) -> Observation:
    return Observation(
        source=source,
        label=label,
        confidence=confidence,
        confirmation=confirmation,
        graphiti_uuid=graphiti_uuid,
        obsidian_uuid=obsidian_uuid,
        description=description,
        kind=NodeKind.OBJECT,
    )


# ─── 1. backward-compat default ─────────────────────────────────────


def test_default_construction_has_empty_source_and_meta():
    """Pre-Phase-4 callers (preload_from_graphiti / test fixtures) construct
    SemanticNode bare. Defaults must keep working unchanged."""
    n = SemanticNode(label="legacy_node")
    assert n.source == ""
    assert n.source_meta == {}


# ─── 2. from_observation propagates source ────────────────────────


def test_from_observation_propagates_source_value():
    obs = _obs(source=ObservationSource.CV_A10, label="a10_chair")
    n = SemanticNode.from_observation(obs)
    assert n.source == "cv_a10"  # the .value of the enum


def test_from_observation_carries_through_observation_fields():
    """Observation → Node copies the existing fields too (no regression
    on identifier / description / confidence propagation)."""
    obs = _obs(
        source=ObservationSource.IDENTIFY_OBJECT,
        label="blue_mug",
        graphiti_uuid="g_abc",
        confidence=0.9,
        confirmation=ConfirmationStatus.CONFIRMED,
        description="a blue ceramic mug",
    )
    n = SemanticNode.from_observation(obs)
    assert n.label == "blue_mug"
    assert n.graphiti_uuid == "g_abc"
    assert n.evidence_score == 0.9
    assert n.confirmation == ConfirmationStatus.CONFIRMED
    assert n.description == "a blue ceramic mug"
    assert n.source == "identify_object"


# ─── 3. default factory returns empty meta ────────────────────────


def test_from_observation_default_factory_yields_empty_source_meta():
    obs = _obs(source=ObservationSource.GEMINI_ORAL)
    n = SemanticNode.from_observation(obs)
    assert n.source_meta == {}  # default factory


# ─── 4. extension space — register a factory ──────────────────────


def test_register_source_meta_factory_attaches_payload():
    """Future A10 / Sentinel pipelines call register_source_meta_factory
    on import to plug in their own per-source meta builder. SemanticNode
    code does not need to change."""
    seen_observations = []

    def fake_a10_factory(obs):
        seen_observations.append(obs)
        return {
            "reid_hash": "deadbeef",
            "track_id": "trk_42",
            "yolo_class_votes": ["chair", "table"],
        }

    register_source_meta_factory(ObservationSource.CV_A10.value, fake_a10_factory)

    obs = _obs(source=ObservationSource.CV_A10, label="a10_node")
    n = SemanticNode.from_observation(obs)

    assert n.source == "cv_a10"
    assert n.source_meta == {
        "reid_hash": "deadbeef",
        "track_id": "trk_42",
        "yolo_class_votes": ["chair", "table"],
    }
    # Factory received the original Observation
    assert len(seen_observations) == 1
    assert seen_observations[0].label == "a10_node"


def test_unrelated_source_unaffected_by_other_factory():
    """Registering an A10 factory must not change USER / GEMINI behaviour."""
    register_source_meta_factory(
        ObservationSource.CV_A10.value,
        lambda _o: {"a10_only": True},
    )

    obs = _obs(source=ObservationSource.GEMINI_ORAL)
    n = SemanticNode.from_observation(obs)

    assert n.source == "gemini_oral"
    assert n.source_meta == {}


# ─── 5. IngestRunner round-trip ────────────────────────────────────


def test_runner_observation_to_node_carries_source():
    """The runner must use the from_observation factory under the hood and
    therefore the resulting node carries the source tag."""
    obs = _obs(source=ObservationSource.IDENTIFY_OBJECT, label="runner_node")
    runner = IngestRunner.__new__(IngestRunner)  # avoid graph-init in unit test
    runner._graph = None  # type: ignore[attr-defined]
    runner._label_cache = {}  # type: ignore[attr-defined]
    runner._repeat_window_s = 30.0  # type: ignore[attr-defined]

    node = runner._observation_to_node(obs)
    assert node.source == "identify_object"


def test_runner_user_explicit_promotes_salience_to_foreground():
    """Phase 4 W4-5 behaviour: user-explicit observations get FOREGROUND
    salience; the source-dispatch refactor must NOT regress this rule."""
    runner = IngestRunner.__new__(IngestRunner)
    runner._graph = None
    runner._label_cache = {}
    runner._repeat_window_s = 30.0

    obs = _obs(source=ObservationSource.USER_EXPLICIT, label="user_node")
    node = runner._observation_to_node(obs)
    assert node.salience == Salience.FOREGROUND


# ─── 6. _source_for_node prefers node.source ──────────────────────


def test_source_for_node_prefers_explicit_node_source_over_heuristic():
    """When a node carries an explicit source (Phase 4+ ingest path),
    the runner must trust it instead of inferring from identifiers."""
    n = SemanticNode(
        label="ambiguous",
        graphiti_uuid="g_abc",  # heuristic would say IDENTIFY_OBJECT
        source="cv_a10",  # explicit — must win
    )
    assert _source_for_node(n) == ObservationSource.CV_A10


def test_source_for_node_falls_back_to_heuristic_on_empty_source():
    """Pre-Phase-4 nodes (preloaded from Graphiti) have empty source —
    runner falls back to identifier heuristic for backward compat."""
    n = SemanticNode(label="pre_phase4", obsidian_uuid="ob_xyz", source="")
    assert _source_for_node(n) == ObservationSource.USER_TAG_OBSIDIAN

    n2 = SemanticNode(label="pre_phase4_g", graphiti_uuid="g_xyz", source="")
    assert _source_for_node(n2) == ObservationSource.IDENTIFY_OBJECT

    n3 = SemanticNode(label="pre_phase4_orphan", source="")
    assert _source_for_node(n3) == ObservationSource.GEMINI_ORAL


# ─── 7. forward-compat — unknown source string ─────────────────────


def test_source_for_node_unknown_source_string_falls_through():
    """Forward compat: a newer pipeline writes a source string this
    Brain doesn't recognise yet. We must NOT crash; fall back to the
    identifier heuristic so authority comparison still works."""
    n = SemanticNode(
        label="future_source",
        graphiti_uuid="g_abc",
        source="some_future_pipeline_v2",
    )
    # Falls through to heuristic — graphiti_uuid → IDENTIFY_OBJECT
    assert _source_for_node(n) == ObservationSource.IDENTIFY_OBJECT
