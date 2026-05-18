"""Phase 4 § 8 + ADR-L1.5-001 + LineB compatibility守护.

Each assertion guards a specific lock that DSG Chat 2 (this commit)
must not have touched. Any failure here means the implementation
silently regressed a Phase 4 contract — rollback or new ADR required.
"""

from __future__ import annotations

import inspect

import pytest

from parrot.dsg.ingest import base as ingest_base
from parrot.dsg.l2b_types import EDGE_KIND_VIEW_CLASSES, EdgeKind, NodeKind, edge_view_classes


# ─── Phase 4 § 8 L1: NodeKind / EdgeKind enum cardinality ────────


def test_node_kind_enum_six_values() -> None:
    """L1 lock — NodeKind 6 entries (object/surface/zone/person/event/photo)."""
    expected = {"object", "surface", "zone", "person", "event", "photo"}
    actual = {m.value for m in NodeKind}
    assert actual == expected, f"NodeKind drifted: {actual}"


def test_edge_kind_enum_eight_values() -> None:
    """L1 lock — EdgeKind 8 entries.
    Phase 4 W8 added has_photo / captured_via / candidate_subject.
    """
    expected = {
        "associated_with",
        "reminds_of",
        "co_occurred",
        "spatial_context",
        "part_of_episode",
        "has_photo",
        "captured_via",
        "candidate_subject",
    }
    actual = {m.value for m in EdgeKind}
    assert expected.issubset(actual), f"Legacy EdgeKind entries dropped: {expected - actual}"


def test_every_edge_kind_has_view_classification() -> None:
    """Every EdgeKind must be filterable by at least one view class."""
    assert set(EDGE_KIND_VIEW_CLASSES) == set(EdgeKind)
    for kind in EdgeKind:
        assert edge_view_classes(kind), f"EdgeKind {kind.value} has no view class"


# ─── ADR-L1.5-001 + LineB compatibility ──────────────────────────


def test_observation_source_legacy_seven_preserved() -> None:
    """LineB § 1.3 / ADR-L1.5-001 § 1.1: the seven baseline source
    string values must remain verbatim. New entries are additive."""
    legacy = {
        "user_tag_obsidian",
        "user_explicit",
        "identify_object",
        "gemini_oral",
        "cv_a10",
        "cv_sentinel",
        "mock",
    }
    actual = {m.value for m in ingest_base.ObservationSource}
    assert legacy.issubset(actual), (
        f"Legacy ObservationSource entries dropped: missing={legacy - actual}"
    )


def test_observation_source_gemini_oral_value_unchanged() -> None:
    """LineB compatibility — ``GEMINI_ORAL`` value must stay
    ``gemini_oral`` even though it now represents any LLM oral mention."""
    assert ingest_base.ObservationSource.GEMINI_ORAL.value == "gemini_oral"


def test_observation_source_goslo_autonomous_added() -> None:
    """DSG-POOL-V1: GOSLO_AUTONOMOUS stays present after later additions."""
    members = {m.name for m in ingest_base.ObservationSource}
    assert "GOSLO_AUTONOMOUS" in members


def test_observation_source_google_calendar_added() -> None:
    """Chat B: Google Calendar is a Python-only source addition."""
    assert ingest_base.ObservationSource.GOOGLE_CALENDAR.value == "google_calendar"


def test_observation_source_google_message_added() -> None:
    """Web Runtime: Gmail/Workspace message notifications use L1.5 ingest."""
    assert ingest_base.ObservationSource.GOOGLE_MESSAGE.value == "google_message"


# ─── ADR-L1.5-001 § 4.1 三触发器 — must NOT be triggered by Chat 2 ──


def test_semantic_node_still_uses_meta_dict_factory() -> None:
    """ADR-L1.5-001 § 2.2 + § 4.1: continue using meta dict + factory
    until we deliberately upgrade. SemanticNode must not have grown a
    typed source-payload field; source_meta stays ``dict[str, Any]``."""
    from parrot.dsg.l2b_types import SemanticNode
    sig = inspect.signature(SemanticNode)
    params = sig.parameters
    assert "source_meta" in params
    assert "source" in params


def test_no_semantic_node_subclass_introduced() -> None:
    """ADR-L1.5-001 § 4.1 condition 3 — no isinstance dispatch."""
    from parrot.dsg.l2b_types import SemanticNode

    # Walk the parrot.* import space and ensure no subclass exists
    import importlib
    for mod_name in (
        "parrot.dsg.l2b_types",
        "parrot.dsg.l2b_graph",
        "parrot.dsg.ingest.runner",
        "parrot.dsg.ingest.base",
        "parrot.dsg.l1_5.pool",
    ):
        mod = importlib.import_module(mod_name)
        for _name, obj in vars(mod).items():
            if isinstance(obj, type) and issubclass(obj, SemanticNode) and obj is not SemanticNode:
                pytest.fail(f"Unexpected SemanticNode subclass {obj} in {mod_name}")


# ─── Phase 4 § 8 L9 + L13: dsg/attention boundary ────────────────


def test_dsg_attention_does_not_export_attention_class() -> None:
    """L13 lock — ``parrot.dsg.attention`` must not export an
    ``Attention`` class symbol at the top level."""
    import parrot.dsg.attention as legacy_attention
    public = {n for n in dir(legacy_attention) if not n.startswith("_")}
    assert "Attention" not in public, (
        f"L13 violated: dsg.attention now exports 'Attention': {public}"
    )


def test_dsg_l2b_attention_does_not_export_attention_class() -> None:
    """The new L2-B attention extensions (decay / mechanism) also must
    not export a generic ``Attention`` class."""
    import parrot.dsg.l2b.attention as new_attention
    public = {n for n in dir(new_attention) if not n.startswith("_")}
    assert "Attention" not in public, (
        f"L13 violated: l2b.attention now exports 'Attention': {public}"
    )


# ─── Source priority ordering — GOSLO between user-asked and CV_A10 ──


def test_source_priority_order_master_3_3() -> None:
    """master § 3.3: GOSLO_AUTONOMOUS priority < IDENTIFY_OBJECT (user-asked)
    and > CV_A10 (passive CV)."""
    from parrot.dsg.ingest.runner import _SOURCE_PRIORITY

    p_user_asked = _SOURCE_PRIORITY[ingest_base.ObservationSource.IDENTIFY_OBJECT]
    p_goslo = _SOURCE_PRIORITY[ingest_base.ObservationSource.GOSLO_AUTONOMOUS]
    p_cv_a10 = _SOURCE_PRIORITY[ingest_base.ObservationSource.CV_A10]
    assert p_cv_a10 < p_goslo < p_user_asked, (
        f"priority ordering broken: cv_a10={p_cv_a10}, "
        f"goslo={p_goslo}, identify_object={p_user_asked}"
    )


def test_source_priority_full_table_unchanged() -> None:
    """Legacy 7 priority numbers MUST stay; GOSLO_AUTONOMOUS=70 is new
    (master § 3.3 — between IDENTIFY_OBJECT=80 and CV_A10=60)."""
    from parrot.dsg.ingest.runner import _SOURCE_PRIORITY
    assert _SOURCE_PRIORITY[ingest_base.ObservationSource.USER_TAG_OBSIDIAN] == 100
    assert _SOURCE_PRIORITY[ingest_base.ObservationSource.USER_EXPLICIT] == 95
    assert _SOURCE_PRIORITY[ingest_base.ObservationSource.IDENTIFY_OBJECT] == 80
    assert _SOURCE_PRIORITY[ingest_base.ObservationSource.GOSLO_AUTONOMOUS] == 70
    assert _SOURCE_PRIORITY[ingest_base.ObservationSource.GOOGLE_CALENDAR] == 65
    assert _SOURCE_PRIORITY[ingest_base.ObservationSource.GOOGLE_MESSAGE] == 64
    assert _SOURCE_PRIORITY[ingest_base.ObservationSource.CV_A10] == 60
    assert _SOURCE_PRIORITY[ingest_base.ObservationSource.CV_SENTINEL] == 40
    assert _SOURCE_PRIORITY[ingest_base.ObservationSource.GEMINI_ORAL] == 30
    assert _SOURCE_PRIORITY[ingest_base.ObservationSource.MOCK] == 10
