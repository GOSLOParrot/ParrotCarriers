"""MenuRegistry — frontend-facing aggregator for the 4 menu blocks.

This module is the single Python entry the Unity menu canvas / HUD calls
into. It surfaces:

    * Persona block         — list_personas() / current persona
    * Mode block            — BehaviorMode flags (BASE..ROLEPLAY)
    * Scene block           — registered SceneType profiles
    * Model block           — ModelManifest list (delegates to the
                              ModelManifestRegistry mirror once a Brain-
                              side mirror lands; baseline returns a single
                              GOSLO_default entry)

How TODO decisions:
- 4 *separate* registries with a thin aggregator (Option A in the plan)
  rather than one unified ABC. Persona / Mode / Scene / Model already
  exist as independent modules; rewriting them as a class hierarchy would
  churn imports without changing behaviour.
- ``apply_selection`` synthesises a ``Preset`` and routes to
  ``PresetLoader.apply`` so the BB single-writer contract is preserved.
- The menu API is *blocking-friendly*: ``list_blocks()`` is sync-safe
  (no Redis / file IO beyond the persona dir glob). Frontend can call it
  on RPC threads without awaiting.
- ``apply_preset_id`` is the simple "load + apply" combo for the default
  fallback menu (NEED-P3-E). The node-canvas variant (NEED-P3-D) calls
  ``apply_selection`` directly with a freshly-built ``MenuSelection``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Sequence

from parrot.brain.persona_loader import (
    DEFAULT_PERSONA_ID,
    PersonaSummary,
    get_persona_loader,
)
from parrot.brain.preset_loader import (
    DEFAULT_MODEL_ID,
    DEFAULT_SCENE_ID,
    Preset,
    PresetApplyResult,
    get_preset_loader,
)
from parrot.dsg.l1_5.scene_snapshot import SceneType
from parrot.shared.parrot_actions import BehaviorMode

logger = logging.getLogger(__name__)


# ─── Block summaries ────────────────────────────────────────────────


@dataclass(frozen=True)
class ModelBlockSummary:
    """ModelManifest summary view for the menu canvas.

    Brain-side ModelManifestRegistry mirror is still pending
    (cross_chat_pending_registry §4.F). For now we surface the GOSLO_default
    entry hard-coded and let Unity-side ParrotRegistry remain the
    authoritative source on model presence.
    """

    model_id: str
    display_name: str
    declared_capability_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ModeBlockSummary:
    """BehaviorMode flag summary."""

    flag_name: str
    display_name: str
    description: str = ""
    default: bool = False


@dataclass(frozen=True)
class SceneBlockSummary:
    """SceneProfile summary."""

    scene_id: str
    display_name: str
    is_baseline: bool


@dataclass(frozen=True)
class MenuRegistrySnapshot:
    """Full menu state surfaced to the Unity canvas."""

    personas: tuple[PersonaSummary, ...]
    modes: tuple[ModeBlockSummary, ...]
    scenes: tuple[SceneBlockSummary, ...]
    models: tuple[ModelBlockSummary, ...]
    active_persona_id: str
    active_mode_flags: tuple[str, ...]
    active_scene_id: str
    active_model_id: str
    available_preset_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class MenuSelection:
    """Frontend-supplied selection to apply atomically."""

    persona_id: str
    mode_flags: tuple[str, ...]
    scene_id: str
    model_id: str
    metadata: dict = field(default_factory=dict)


# ─── Static descriptors ─────────────────────────────────────────────


_MODE_BLOCK_DESCRIPTORS: tuple[ModeBlockSummary, ...] = (
    ModeBlockSummary(
        flag_name="BASE",
        display_name="基础",
        description="始终激活；安全 + 工具调用规则。",
        default=True,
    ),
    ModeBlockSummary(
        flag_name="COMPANION",
        display_name="陪伴",
        description="敏感于情绪 / 闲聊 / 共处。",
        default=True,
    ),
    ModeBlockSummary(
        flag_name="BUTLER",
        display_name="管家",
        description="时间 / 待办 / 主动汇报 nanobot 结果。",
    ),
    ModeBlockSummary(
        flag_name="RESEARCHER",
        display_name="研究员",
        description="主动 dispatch_task 调研 / 总结。",
    ),
    ModeBlockSummary(
        flag_name="PLAYFUL",
        display_name="顽皮",
        description="多动画 / 多笑话；通过 animate 频繁律动。",
    ),
    ModeBlockSummary(
        flag_name="ROLEPLAY",
        display_name="角色扮演",
        description="临时人格语气；激活 Obsidian roleplay 设定桶。",
    ),
)


_SCENE_BASELINES = frozenset({SceneType.DESKTOP_WEBCAM, SceneType.AR_HANDHELD, SceneType.DESKTOP})


def _scene_display_name(scene_type: SceneType) -> str:
    return {
        SceneType.DESKTOP: "桌面 (legacy)",
        SceneType.DESKTOP_WEBCAM: "桌面 / Webcam",
        SceneType.AR_HANDHELD: "AR 手持",
        SceneType.HOME_INDOOR: "室内家居",
        SceneType.OUTDOOR: "户外",
        SceneType.LIBRARY: "图书馆",
        SceneType.KITCHEN: "厨房",
        SceneType.OTHER: "其他",
    }.get(scene_type, scene_type.value)


# ─── Active state probes ────────────────────────────────────────────


def _read_active(key: str, default: str = "") -> str:
    """Best-effort BB read; returns ``default`` on any failure."""
    try:
        from parrot.scheduler.blackboard import open_bb_client

        bb = open_bb_client(name="menu_registry.read", writer=None)
        try:
            value = bb.get(key)
        except Exception:
            return default
        if isinstance(value, str):
            return value
        return default
    except Exception:
        return default


def _read_active_mode_flags() -> tuple[str, ...]:
    """Best-effort BB read for active_mode (list[str])."""
    try:
        from parrot.scheduler.blackboard import open_bb_client

        bb = open_bb_client(name="menu_registry.read_mode", writer=None)
        try:
            value = bb.get("global/active_mode")
        except Exception:
            value = None
        if isinstance(value, list):
            return tuple(str(v).upper() for v in value)
        if isinstance(value, str):
            return tuple(s.strip().upper() for s in value.split("|") if s.strip())
        return ("BASE", "COMPANION")
    except Exception:
        return ("BASE", "COMPANION")


# ─── MenuRegistry ───────────────────────────────────────────────────


class MenuRegistry:
    """Aggregator over the 4 block sub-registries."""

    def __init__(self) -> None:
        self._mode_descriptors = _MODE_BLOCK_DESCRIPTORS

    # ─── List ────────────────────────────────────────────────────

    def list_blocks(self) -> MenuRegistrySnapshot:
        loader = get_persona_loader()
        personas = tuple(loader.list_personas())

        scenes: list[SceneBlockSummary] = []
        for st in SceneType:
            scenes.append(SceneBlockSummary(
                scene_id=st.value,
                display_name=_scene_display_name(st),
                is_baseline=st in _SCENE_BASELINES,
            ))

        models = (ModelBlockSummary(
            model_id=DEFAULT_MODEL_ID,
            display_name="GOSLO Parrot (default)",
            declared_capability_ids=(
                "fly", "dance", "wing_flap", "head_bob", "perch", "sit", "sleep", "idle",
            ),
        ),)

        active_persona_id = _read_active("global/active_persona_id") or DEFAULT_PERSONA_ID
        active_scene_id = _read_active("global/active_scene_id") or DEFAULT_SCENE_ID
        active_model_id = _read_active("global/active_model_id") or DEFAULT_MODEL_ID
        active_mode_flags = _read_active_mode_flags()

        try:
            preset_ids = tuple(get_preset_loader().list_presets())
        except Exception:
            preset_ids = ()

        return MenuRegistrySnapshot(
            personas=personas,
            modes=self._mode_descriptors,
            scenes=tuple(scenes),
            models=models,
            active_persona_id=active_persona_id,
            active_mode_flags=active_mode_flags,
            active_scene_id=active_scene_id,
            active_model_id=active_model_id,
            available_preset_ids=preset_ids,
        )

    # ─── Apply ───────────────────────────────────────────────────

    def apply_selection(self, selection: MenuSelection) -> PresetApplyResult:
        """Atomic apply of a 4-block selection.

        Synthesises an ad-hoc Preset (preset_id="ephemeral") and routes
        through PresetLoader.apply so the BB single-writer contract holds.
        """
        preset = Preset(
            preset_id="ephemeral",
            active_persona_id=selection.persona_id or DEFAULT_PERSONA_ID,
            active_model_id=selection.model_id or DEFAULT_MODEL_ID,
            active_scene_id=selection.scene_id or DEFAULT_SCENE_ID,
            active_mode=tuple(s.upper() for s in selection.mode_flags) or ("BASE", "COMPANION"),
            metadata=dict(selection.metadata),
        )
        return get_preset_loader().apply(preset)

    def apply_preset_id(self, preset_id: str) -> PresetApplyResult:
        """Convenience: load by id then apply."""
        preset = get_preset_loader().load(preset_id)
        return get_preset_loader().apply(preset)

    # ─── Validation helpers ──────────────────────────────────────

    def validate_mode_flags(self, flags: Sequence[str]) -> tuple[BehaviorMode, tuple[str, ...]]:
        """Return (decoded_flag, unknown_names). Caller decides whether to error."""
        out = BehaviorMode(0)
        unknown: list[str] = []
        for name in flags:
            try:
                out |= BehaviorMode[name.upper()]
            except KeyError:
                unknown.append(name)
        if out == BehaviorMode(0):
            out = BehaviorMode.BASE | BehaviorMode.COMPANION
        return out, tuple(unknown)


# ─── Singleton + test injection ──────────────────────────────────────


_registry: MenuRegistry | None = None


def get_menu_registry() -> MenuRegistry:
    global _registry
    if _registry is None:
        _registry = MenuRegistry()
    return _registry


def set_menu_registry_for_test(registry: MenuRegistry | None) -> None:
    global _registry
    _registry = registry


__all__ = [
    "MenuRegistry",
    "MenuRegistrySnapshot",
    "MenuSelection",
    "ModeBlockSummary",
    "ModelBlockSummary",
    "SceneBlockSummary",
    "get_menu_registry",
    "set_menu_registry_for_test",
]
