"""Tests for `parrot.shared.ref_binding.RefBinding` (Phase 4 ⓒ).

Coverage focus:
    1. Default factory generates time-sortable ref_id with ref_ prefix
    2. Schema enforcement (extra fields rejected)
    3. Mutability via :meth:`with_resolved_target` bumps revision (the only
       sanctioned mutation path)
    4. UNRESOLVED is the default target_kind
    5. source_event_id is required (non-optional) — every Ref is event-driven
"""

from __future__ import annotations

import time

import pytest
from pydantic import ValidationError

from parrot.shared.ref_binding import (
    RefBinding,
    RefKind,
    RefTargetKind,
    generate_ref_id,
)


def test_generate_ref_id_format_and_sortability():
    a = generate_ref_id()
    time.sleep(0.002)
    b = generate_ref_id()

    assert a.startswith("ref_")
    assert b.startswith("ref_")
    assert a != b
    assert a < b


def test_default_target_is_unresolved():
    r = RefBinding(kind=RefKind.FOCUS, source_event_id="evt_test_0001")
    assert r.target_kind == RefTargetKind.UNRESOLVED
    assert r.target_id == ""
    assert r.revision == 1


def test_source_event_id_is_required():
    with pytest.raises(ValidationError):
        RefBinding(kind=RefKind.FOCUS)  # type: ignore[call-arg]


def test_extra_fields_rejected():
    with pytest.raises(ValidationError):
        RefBinding(
            kind=RefKind.FOCUS,
            source_event_id="evt_test_0001",
            future_field="should be rejected",  # type: ignore[call-arg]
        )


def test_with_resolved_target_bumps_revision_and_keeps_ref_id():
    base = RefBinding(
        kind=RefKind.BBOX,
        source_event_id="evt_initial",
        label="user-placed bbox",
    )
    resolved = base.with_resolved_target(
        target_kind=RefTargetKind.L2B_NODE,
        target_id="node_42",
        new_event_id="evt_visual_match_completed",
    )

    assert resolved.ref_id == base.ref_id
    assert resolved.revision == 2
    assert resolved.target_kind == RefTargetKind.L2B_NODE.value
    assert resolved.target_id == "node_42"
    assert resolved.source_event_id == "evt_visual_match_completed"
    assert resolved.label == base.label
    assert resolved.created_at == base.created_at
    assert resolved.updated_at >= base.updated_at


def test_with_resolved_target_can_keep_source_event_id():
    """Optional new_event_id — pass None to keep the original provenance."""
    base = RefBinding(
        kind=RefKind.PHOTO,
        source_event_id="evt_photo_taken",
    )
    resolved = base.with_resolved_target(
        target_kind=RefTargetKind.EPISODE,
        target_id="episode_99",
    )
    assert resolved.source_event_id == "evt_photo_taken"


def test_revision_must_be_positive():
    with pytest.raises(ValidationError):
        RefBinding(
            kind=RefKind.FOCUS,
            source_event_id="evt_test",
            revision=0,
        )
