"""Tests for `parrot.shared.model_manifest` (GOSLO model modularization Step 1).

Coverage map:
* ``RESERVED_PARROT_CAPABILITY_IDS`` is exactly the ``ParrotAnimation`` enum's
  string values (no drift from the wire-locked vocabulary).
* ``Capability`` validation: free-form ``capability_id`` accepted; whitespace /
  control chars rejected; ``is_reserved_parrot_id`` flips on for reserved ids.
* ``ModelManifest`` validation: required fields, axis enum lock, unique
  ``capability_id`` constraint, JSON round-trip stability.
* ``parrot_reflex_enabled`` derived property: True when any capability_id
  intersects the reserved set; False otherwise.
* ``declared_capability_ids`` / ``supports`` helpers.
* GOSLO_default-shaped manifest matches the legacy AnimationDriver contract
  (8 reserved capabilities → reflex on).
"""

from __future__ import annotations

import json

import pytest

from parrot.shared.model_manifest import (
    DEFAULT_MODEL_ID,
    RESERVED_PARROT_CAPABILITY_IDS,
    Capability,
    CapabilityKind,
    ModelManifest,
)
from parrot.shared.parrot_actions import ParrotAnimation


# ─── Reserved set parity with ParrotAnimation enum ─────────────────────────


def test_reserved_set_equals_parrot_animation_enum_values():
    """The reserved set MUST equal the ParrotAnimation enum string values.

    If this drifts, the launch-prompt §3 lock ("ParrotAnimation enum 8 entries
    are the Brain LLM vocabulary AND Reflex trigger") silently breaks. This is
    the cheap structural guard.
    """
    assert RESERVED_PARROT_CAPABILITY_IDS == frozenset(a.value for a in ParrotAnimation)
    assert len(RESERVED_PARROT_CAPABILITY_IDS) == 8  # locked count


def test_default_model_id_constant():
    """Backward-compat default — single-GOSLO deployments don't need a model_id."""
    assert DEFAULT_MODEL_ID == "GOSLO_default"


# ─── Capability schema ─────────────────────────────────────────────────────


def test_capability_with_reserved_id_flags_reserved():
    cap = Capability(capability_id="fly", kind=CapabilityKind.POSE, handler="Fly")
    assert cap.is_reserved_parrot_id is True


def test_capability_with_custom_id_does_not_flag_reserved():
    cap = Capability(capability_id="dance_q_pose", kind=CapabilityKind.PROCEDURAL)
    assert cap.is_reserved_parrot_id is False


def test_capability_id_rejects_whitespace():
    with pytest.raises(ValueError):
        Capability(capability_id="head bob", kind=CapabilityKind.POSE)


def test_capability_id_rejects_newline():
    with pytest.raises(ValueError):
        Capability(capability_id="fly\n", kind=CapabilityKind.POSE)


def test_capability_id_rejects_empty():
    with pytest.raises(ValueError):
        Capability(capability_id="", kind=CapabilityKind.POSE)


def test_capability_kind_serialises_as_string():
    cap = Capability(capability_id="fly", kind=CapabilityKind.POSE)
    dumped = cap.model_dump(mode="json")
    assert dumped["kind"] == "pose"


def test_capability_extra_fields_rejected():
    """Frozen + extra='forbid' guards against typo'd manifest fields slipping
    through — the AI CLI / human author should get a hard error rather than
    a silently-ignored unknown key."""
    with pytest.raises(ValueError):
        Capability(  # type: ignore[call-arg]
            capability_id="fly",
            kind=CapabilityKind.POSE,
            unknown_field="oops",
        )


# ─── ModelManifest schema ──────────────────────────────────────────────────


def _minimal_manifest(**overrides) -> ModelManifest:
    base = dict(
        model_id="test_model",
        asset_path="parrot_models/test",
        controller_type="ParrotApp.Parrot.TestController",
    )
    base.update(overrides)
    return ModelManifest(**base)


def test_minimal_manifest_constructs_with_defaults():
    m = _minimal_manifest()
    assert m.schema_version == 1
    assert m.manifest_version == 1
    assert m.forward_axis == "+Z"
    assert m.up_axis == "+Y"
    assert m.unit_meters == 1.0
    assert m.default_pet_height_m == 0.20
    assert m.auto_scale_to_pet_height is True
    assert m.capabilities == ()
    assert m.parrot_reflex_enabled is False
    assert m.declared_capability_ids == frozenset()


def test_manifest_axis_lock_rejects_freeform():
    with pytest.raises(ValueError):
        _minimal_manifest(forward_axis="forward")
    with pytest.raises(ValueError):
        _minimal_manifest(up_axis="z")


def test_manifest_axis_lock_accepts_negative_axes():
    """Authors with right-handed source assets (e.g. some FBX exporters) need
    -Z / -Y forward — protocol allows declaring it instead of forcing a coord
    transform on the model."""
    m = _minimal_manifest(forward_axis="-Z", up_axis="-Y")
    assert m.forward_axis == "-Z"
    assert m.up_axis == "-Y"


def test_manifest_unit_meters_must_be_positive():
    with pytest.raises(ValueError):
        _minimal_manifest(unit_meters=0.0)
    with pytest.raises(ValueError):
        _minimal_manifest(unit_meters=-1.0)


def test_manifest_pet_height_must_be_positive():
    with pytest.raises(ValueError):
        _minimal_manifest(default_pet_height_m=0.0)


def test_manifest_model_id_rejects_path_separator():
    """A model_id is also used as a Resources path fragment in the AI CLI
    output convention. Slashes / backslashes / whitespace would silently
    create nested folders or break Resources lookup, so reject early."""
    with pytest.raises(ValueError):
        _minimal_manifest(model_id="folder/model")
    with pytest.raises(ValueError):
        _minimal_manifest(model_id="folder\\model")
    with pytest.raises(ValueError):
        _minimal_manifest(model_id="my model")


def test_manifest_duplicate_capability_id_rejected():
    with pytest.raises(ValueError):
        _minimal_manifest(
            capabilities=(
                Capability(capability_id="fly", kind=CapabilityKind.POSE),
                Capability(capability_id="fly", kind=CapabilityKind.ANIMATION),
            )
        )


def test_manifest_supports_helper():
    m = _minimal_manifest(
        capabilities=(
            Capability(capability_id="fly", kind=CapabilityKind.POSE),
            Capability(capability_id="dance_q_pose", kind=CapabilityKind.PROCEDURAL),
        )
    )
    assert m.supports("fly") is True
    assert m.supports("dance_q_pose") is True
    assert m.supports("idle") is False
    assert m.declared_capability_ids == frozenset({"fly", "dance_q_pose"})


# ─── Reflex layer activation ───────────────────────────────────────────────


def test_reflex_enabled_when_any_reserved_capability_declared():
    m = _minimal_manifest(
        capabilities=(
            Capability(capability_id="idle", kind=CapabilityKind.POSE),
            Capability(capability_id="dance_q_pose", kind=CapabilityKind.PROCEDURAL),
        )
    )
    assert m.parrot_reflex_enabled is True


def test_reflex_disabled_when_no_reserved_capability_declared():
    """Custom-only capabilities — the model is not parrot-shaped, so suppress
    the reflex layer (idle breath / head bob / tail sway would look wrong on
    e.g. a humanoid Q-version chibi)."""
    m = _minimal_manifest(
        capabilities=(
            Capability(capability_id="dance_q_pose", kind=CapabilityKind.PROCEDURAL),
            Capability(capability_id="wave_hand", kind=CapabilityKind.ANIMATION),
        )
    )
    assert m.parrot_reflex_enabled is False


def test_reflex_disabled_when_capabilities_empty():
    m = _minimal_manifest()
    assert m.parrot_reflex_enabled is False


# ─── GOSLO_default contract — sentinel ────────────────────────────────────


def test_goslo_default_manifest_shape_matches_legacy_contract():
    """A GOSLO-shaped manifest must declare all 8 ParrotAnimation enum entries
    as capabilities → Reflex on. This is the test that guards the Step 2
    AnimationDriver shim from accidentally losing one of the original 8 wire
    string targets (idle / fly / dance / wing_flap / perch / sit / head_bob /
    sleep)."""
    capabilities = tuple(
        Capability(capability_id=a.value, kind=CapabilityKind.POSE)
        for a in ParrotAnimation
    )
    m = ModelManifest(
        model_id=DEFAULT_MODEL_ID,
        display_name="GOSLO (default parrot)",
        asset_path="parrot_models/goslo_default",
        controller_type="ParrotApp.Parrot.GosloLegacyController",
        capabilities=capabilities,
        auto_scale_to_pet_height=False,
    )
    assert m.declared_capability_ids == RESERVED_PARROT_CAPABILITY_IDS
    assert m.parrot_reflex_enabled is True
    assert m.supports("fly") is True
    assert m.supports("sleep") is True


# ─── JSON round-trip (Unity JsonUtility surrogate) ─────────────────────────


def test_manifest_json_round_trip_preserves_capability_set():
    """JsonUtility on Unity side reads on-disk manifests as JSON. We round-trip
    through json.loads to mimic that path and check no field gets lost."""
    capabilities = (
        Capability(capability_id="fly", kind=CapabilityKind.POSE, handler="Fly"),
        Capability(
            capability_id="dance_q_pose",
            kind=CapabilityKind.PROCEDURAL,
            handler="DanceQPose",
            description="Q-version chibi celebration pose",
        ),
    )
    m = ModelManifest(
        model_id="qfufu_v1",
        display_name="Q-Fufu",
        asset_path="parrot_models/qfufu_v1",
        controller_type="ParrotApp.Parrot.QFufuController",
        capabilities=capabilities,
    )

    raw = m.model_dump_json()
    parsed = json.loads(raw)
    rebuilt = ModelManifest.model_validate(parsed)

    assert rebuilt == m
    assert rebuilt.declared_capability_ids == frozenset({"fly", "dance_q_pose"})
    # JsonUtility-friendly: capabilities serialised as a JSON array.
    assert isinstance(parsed["capabilities"], list)
    assert parsed["capabilities"][0]["kind"] == "pose"


def test_manifest_extra_fields_rejected():
    """Mirrors Capability — manifest typos must hard-fail."""
    with pytest.raises(ValueError):
        ModelManifest(  # type: ignore[call-arg]
            model_id="bad",
            asset_path="x",
            controller_type="y",
            unknown_top_level="oops",
        )
