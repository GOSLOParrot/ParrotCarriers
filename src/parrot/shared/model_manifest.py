"""GOSLO model manifest — protocol layer for swappable Unity model controllers.

Authoritative spec: ``architecture/goslo_model_manifest_protocol_v1.md``.
Launch prompt: ``architecture/goslo_model_modularization_launch_prompt_20260506.md``.

WHY THIS FILE EXISTS
--------------------
Sprint 0–4 hardcoded a single GOSLO.glb model: `unity/.../Parrot/AnimationDriver.cs`
binds bone names like ``"Head"`` / ``"left_wing"`` / ``"tail"`` and pinpoint-tunes
30+ procedural-animation parameters via ``[SerializeField]``. Brain-side
``parrot.shared.parrot_actions.ParrotAnimation`` enum (8 entries — wire-locked
under Phase 4 §8) is the LLM's animation vocabulary.

Once the user wants to drop in a non-GOSLO model (a different bird, a Q-version
chibi character, a non-bird companion entirely), the AnimationDriver hardcoding
breaks. Recreating an AnimationDriver per model is the wrong abstraction — the
right one is **declarative manifest + capability registration**.

PHILOSOPHY (locked 2026-05-06 design Q-A)
-----------------------------------------
* **Capabilities are open registration.** A model's controller declares what it
  supports (``capability_id`` is free-form). Unity-side ``ModelDriver`` routes
  ``ApplyCapability(capability_id, parameters)`` calls to that controller.
* **ParrotAnimation enum 8 entries are NOT a "must-implement" set** — they are
  the **Brain LLM's vocabulary** AND the **Parrot Reflex layer's activation
  trigger**. A model that opts into any of those eight ``capability_id`` values
  automatically enables the secondary procedural reflex behaviour (idle breath,
  head-bob, tail sway) that defines the "feels alive" parrot baseline.
* **Custom capabilities work.** A model can declare ``capability_id="dance_q_pose"``
  which is unknown to Brain LLM. It will not be invoked autonomously, but it
  CAN be invoked via dispatch_task / future tool extensions / explicit user
  request routed through the LLM.
* **Wire is unchanged.** ``model_id`` rides on the existing
  :attr:`parrot.shared.ecp.EcpCommand.meta` ``dict[str, Any]`` slot. Phase 4
  §8 wire lock holds; cs_parity guard remains green.

OUT OF SCOPE (for this Step 1)
------------------------------
* Multi-actor true routing on Unity side — ``ParrotRegistry`` ships as a
  single-active stub here; deferred to a P3 chat.
* Auto-generated MonoBehaviour ``.cs`` files from manifests — the AI CLI in
  this stack only emits ``manifest.json`` + a validation report. The model
  author writes their own controller.
* Physics / IK / collision — orthogonal to the manifest contract.
* Editing the ``ParrotAnimation`` / ``ParrotBodyState`` / ``BehaviorMode`` enums.
  These are wire-locked. Custom actions go through new ``capability_id`` values
  that Brain LLM does not know about by default.

CROSS-LANGUAGE CONTRACT
-----------------------
This Pydantic schema is the Python source-of-truth. The Unity side reads the
on-disk manifest JSON via ``UnityEngine.JsonUtility`` (forgiving of unknown
fields). The fields here are kept JsonUtility-friendly:

* No ``dict[str, list[...]]`` nesting — JsonUtility cannot deserialise that.
* ``tuple[...]`` is materialised as a JSON array on dump — JsonUtility reads it
  as ``[]`` of the element type.
* ``str``-valued enums dump to plain strings.
* ``author_meta: dict[str, str]`` is allowed because Unity side will declare a
  matching ``[Serializable] class StringStringEntry`` adapter (see Step 2).

There is intentionally NO cs_parity guard for ``Capability`` /
``ModelManifest`` field sets — the manifest is read by Unity, never sent on
the wire to Python, and never participates in the LiveKit DataChannel flow.
The only wire involvement is ``EcpCommand.meta["model_id"]``, which is one
free-form string and needs no cross-language enum.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from parrot.shared.parrot_actions import ParrotAnimation


SCHEMA_VERSION: int = 1


# Brain LLM's animation vocabulary AND Parrot Reflex layer activation trigger.
# Wire-locked under Phase 4 §8 (do NOT extend / shrink here — extend the model's
# declared capabilities or add a new tool instead). Defining this set here as a
# module-level frozenset keeps it cheap to test against and impossible to drift
# from `ParrotAnimation`.
RESERVED_PARROT_CAPABILITY_IDS: frozenset[str] = frozenset(a.value for a in ParrotAnimation)


# Conventional default model id used when callers (Brain tools / Unity registry)
# do not specify one. Deployments that want to make the active model explicit
# may pin a different value via manifest, but the default is preserved for
# backward-compat with the existing single-GOSLO setup.
DEFAULT_MODEL_ID: str = "GOSLO_default"


class CapabilityKind(str, Enum):
    """How the controller dispatches a given capability internally.

    The kind is informational metadata for the manifest reader (Brain-side
    tooling, AI CLI, debugging UIs). Unity ``ModelDriver`` routes the same way
    regardless of kind: it calls ``IParrotController.ApplyCapability(id, json)``
    and lets the controller pick the dispatch strategy.

    POSE
        Persistent state (e.g. ``"flying"``, ``"perching"``, ``"dancing"``).
        Lives until the next state change. Wire-equivalent of the Unity Animator
        top-layer state names that the existing AnimationDriver swaps via
        ``ApplyBodyStateString``.
    ANIMATION
        One-shot clip / trigger (e.g. ``"wing_flap"``, ``"head_bob"``). Returns
        to the prior pose when complete.
    PROCEDURAL
        Custom code path on the controller — typically used for capabilities
        that don't fit the pose/animation dichotomy (e.g. a controller-specific
        ``"q_pose_celebration"`` that combines pose + per-bone tweaking).
    """

    POSE = "pose"
    ANIMATION = "animation"
    PROCEDURAL = "procedural"


class Capability(BaseModel):
    """One capability the model controller declares supporting.

    ``capability_id`` is free-form. If it falls inside
    :data:`RESERVED_PARROT_CAPABILITY_IDS`, the Parrot Reflex layer activates
    on Unity side (idle breath / head bob / tail sway secondary behaviour).
    Otherwise the capability is callable but does NOT receive auto-reflex
    treatment — appropriate for non-bird companions where idle breath etc.
    would look wrong.

    ``handler`` is the controller's internal pointer (a method name, an
    Animator state name, an AnimationClip name) — Unity-side concern. Brain
    NEVER reads ``handler``: Brain only sees ``capability_id``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    capability_id: str = Field(..., min_length=1, max_length=64)
    kind: CapabilityKind
    handler: str = Field(default="", max_length=128)
    parameters: dict[str, Any] = Field(default_factory=dict)
    description: str = Field(default="", max_length=512)

    @field_validator("capability_id")
    @classmethod
    def _capability_id_format(cls, v: str) -> str:
        # Tolerant — must not contain whitespace / illegal JSON chars / newline,
        # but otherwise free-form. Lowercase snake_case is recommended (see
        # protocol doc §3.4) but not enforced; localised IDs / kebab-case for
        # legacy assets are allowed.
        for bad in (" ", "\t", "\n", ",", "\0"):
            if bad in v:
                raise ValueError(f"capability_id contains illegal char {bad!r}: {v!r}")
        return v

    @property
    def is_reserved_parrot_id(self) -> bool:
        """True if this capability_id triggers Parrot Reflex layer activation."""
        return self.capability_id in RESERVED_PARROT_CAPABILITY_IDS


class ModelManifest(BaseModel):
    """Top-level descriptor for one importable Unity model controller.

    A manifest is the contract a model author (or AI CLI) hands to the
    Unity-side ``ModelDriver``. It declares:

    1. Identity (``model_id``, ``display_name``).
    2. Where to find the asset and how to instantiate the controller
       (``asset_path``, ``controller_type``).
    3. Coordinate-system / unit / scale conventions
       (``forward_axis``, ``up_axis``, ``unit_meters``, ``default_pet_height_m``).
    4. The set of capabilities the controller responds to.

    See ``architecture/goslo_model_manifest_protocol_v1.md`` for the
    end-to-end author guide and the MMD → FBX → manifest walkthrough.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: int = Field(default=SCHEMA_VERSION, ge=1, le=255)
    manifest_version: int = Field(default=1, ge=1, le=255)
    model_id: str = Field(..., min_length=1, max_length=64)
    display_name: str = Field(default="", max_length=128)
    asset_path: str = Field(..., min_length=1, max_length=256)
    controller_type: str = Field(..., min_length=1, max_length=256)

    # ─── Coordinate / unit / scale (minimal_lock — see design Q-D) ──────
    # Defaults align with glTF / Unity conventions: +Z forward, +Y up,
    # 1 unit = 1 metre, default desktop-pet height ≈ 0.20 m. AI CLI
    # validation report flags any deviation so the user reviews intentionally.
    forward_axis: str = Field(default="+Z")
    up_axis: str = Field(default="+Y")
    unit_meters: float = Field(default=1.0, gt=0.0)
    default_pet_height_m: float = Field(default=0.20, gt=0.0)
    auto_scale_to_pet_height: bool = Field(default=True)

    # ─── Capability set (free-form; reserved IDs activate Reflex) ───────
    capabilities: tuple[Capability, ...] = Field(default_factory=tuple)

    # ─── Metadata ───────────────────────────────────────────────────────
    preview_image: str = Field(default="", max_length=256)
    author_meta: dict[str, str] = Field(default_factory=dict)

    @field_validator("model_id")
    @classmethod
    def _model_id_format(cls, v: str) -> str:
        for bad in (" ", "\t", "\n", ",", "/", "\\", "\0"):
            if bad in v:
                raise ValueError(f"model_id contains illegal char {bad!r}: {v!r}")
        return v

    @field_validator("forward_axis", "up_axis")
    @classmethod
    def _axis_format(cls, v: str) -> str:
        if v not in {"+X", "-X", "+Y", "-Y", "+Z", "-Z"}:
            raise ValueError(
                f"axis must be one of '+X' / '-X' / '+Y' / '-Y' / '+Z' / '-Z', got {v!r}"
            )
        return v

    @field_validator("capabilities")
    @classmethod
    def _capability_ids_unique(cls, v: tuple[Capability, ...]) -> tuple[Capability, ...]:
        ids = [c.capability_id for c in v]
        if len(ids) != len(set(ids)):
            seen: set[str] = set()
            dupes = [i for i in ids if i in seen or seen.add(i)]  # type: ignore[func-returns-value]
            raise ValueError(f"duplicate capability_id: {sorted(set(dupes))}")
        return v

    @property
    def parrot_reflex_enabled(self) -> bool:
        """Reflex is on if any declared capability_id is in the reserved set.

        This drives Unity-side ``ModelDriver`` to attach the secondary
        procedural reflex behaviour (idle breath / head bob / tail sway)
        — appropriate for parrot-shaped models, suppressed for non-bird
        companions whose ``capabilities`` never overlap the reserved set.
        """
        return any(c.is_reserved_parrot_id for c in self.capabilities)

    @property
    def declared_capability_ids(self) -> frozenset[str]:
        """The set of ``capability_id`` strings this model supports.

        Used by Brain-side tooling (e.g. ``query_scene``) to surface
        controllable verbs to the LLM, and by Unity ``ModelDriver`` to
        graceful-ignore unsupported capability calls (return False from
        ``ApplyCapability`` so RPC handlers can emit ``capability.unsupported``
        in a future telemetry stream).
        """
        return frozenset(c.capability_id for c in self.capabilities)

    def supports(self, capability_id: str) -> bool:
        """Convenience: True if ``capability_id`` is declared by this manifest."""
        return capability_id in self.declared_capability_ids


__all__ = [
    "DEFAULT_MODEL_ID",
    "RESERVED_PARROT_CAPABILITY_IDS",
    "SCHEMA_VERSION",
    "Capability",
    "CapabilityKind",
    "ModelManifest",
]
