"""PresetLoader — menu preset application (NEED-P3-C + 2DWorkspace MVP).

A *Preset* is a named tuple of the user-facing menu blocks:

    {
        "active_model_id":   "GOSLO_default",
        "active_persona_id": "goslo_parrot_default",
        "active_mode":       ["BASE", "COMPANION"],
        "active_scene_id":   "ar_handheld",
        "active_workspace_id": "mansion_hub",
    }

``PresetLoader.load`` reads ``data/presets/<id>.json`` and returns a
:class:`Preset` value object. ``PresetLoader.apply`` writes the five
``global/active_*`` Blackboard keys atomically (single writer per
``shared/bb_schema``) and returns a :class:`PresetApplyResult`.

This is the **only** path that should write the menu active BB keys.
``MenuRegistry.apply_selection`` constructs an ad-hoc Preset from a
selection and routes it through here so the contract stays single-writer.

Watcher integration:
- :func:`apply` flips the BB keys; downstream watchers (mode_watcher,
  persona_watcher, scene_watcher) react to the BB events.
- For non-LiveKit / unit-test paths, callers can pass ``trigger_watchers
  =True`` to publish the legacy mode Pub/Sub channel as a fallback signal.

How TODO decisions:
- Preset JSON schema is intentionally tiny: 4 strings + a metadata dict.
  Adding ``active_workspace_id`` bumps to schema v2 while keeping v1 files
  readable through a default value.
- Validation: model_id is checked when the Brain mirror of
  ``ModelManifestRegistry`` lands; for now we accept any non-empty string.
- Default fallback: ``data/presets/default.json`` ships with the project
  baseline; if absent or unparseable, ``Preset.builtin_default()`` is used.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from parrot.brain.persona_loader import DEFAULT_PERSONA_ID
from parrot.shared.parrot_actions import BehaviorMode

logger = logging.getLogger(__name__)


PRESETS_DIR_ENV = "PARROT_PRESETS_DIR"
DEFAULT_MODEL_ID = "GOSLO_default"
DEFAULT_SCENE_ID = "ar_handheld"
DEFAULT_WORKSPACE_ID = "mansion_hub"
DEFAULT_PRESET_ID = "default"
SCHEMA_VERSION = 2


# ─── Preset value object ─────────────────────────────────────────────


@dataclass(frozen=True)
class Preset:
    """Value object for one preset entry."""

    preset_id: str
    active_model_id: str = DEFAULT_MODEL_ID
    active_persona_id: str = DEFAULT_PERSONA_ID
    active_mode: tuple[str, ...] = ("BASE", "COMPANION")
    active_scene_id: str = DEFAULT_SCENE_ID
    # reason: Scene is the perception/environment baseline; 2DWorkspace is
    # the in-app desktop surface. Keeping a separate id lets the user switch
    # workspaces without making the LiveKit room look like a new AR scene.
    active_workspace_id: str = DEFAULT_WORKSPACE_ID
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def builtin_default(cls) -> "Preset":
        """Hard-coded fallback used when ``data/presets/default.json`` is
        missing / unparseable.
        """
        return cls(preset_id=DEFAULT_PRESET_ID)

    def as_json(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "preset_id": self.preset_id,
            "active_model_id": self.active_model_id,
            "active_persona_id": self.active_persona_id,
            "active_mode": list(self.active_mode),
            "active_scene_id": self.active_scene_id,
            "active_workspace_id": self.active_workspace_id,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> "Preset":
        if not isinstance(raw, dict):
            raise ValueError("preset payload must be a JSON object")
        preset_id = str(raw.get("preset_id", DEFAULT_PRESET_ID))
        mode_raw = raw.get("active_mode") or []
        if isinstance(mode_raw, str):
            mode_raw = [s.strip() for s in mode_raw.split("|") if s.strip()]
        if not isinstance(mode_raw, (list, tuple)):
            raise ValueError("active_mode must be a list of flag names")
        return cls(
            preset_id=preset_id,
            active_model_id=str(raw.get("active_model_id", DEFAULT_MODEL_ID)),
            active_persona_id=str(raw.get("active_persona_id", DEFAULT_PERSONA_ID)),
            active_mode=tuple(str(x).upper() for x in mode_raw),
            active_scene_id=str(raw.get("active_scene_id", DEFAULT_SCENE_ID)),
            active_workspace_id=str(raw.get("active_workspace_id", DEFAULT_WORKSPACE_ID)),
            metadata=dict(raw.get("metadata") or {}),
        )

    def behavior_mode(self) -> BehaviorMode:
        """Decode ``active_mode`` flag names into a BehaviorMode value.

        Unknown flag names log a warning and are dropped — we never want a
        typo in a preset file to crash boot.
        """
        out = BehaviorMode(0)
        for name in self.active_mode:
            try:
                out |= BehaviorMode[name]
            except KeyError:
                logger.warning("preset %s: unknown BehaviorMode flag %r", self.preset_id, name)
        if out == BehaviorMode(0):
            out = BehaviorMode.BASE | BehaviorMode.COMPANION
        return out


@dataclass(frozen=True)
class PresetApplyResult:
    """Outcome of :meth:`PresetLoader.apply`."""

    preset_id: str
    applied_keys: tuple[str, ...]
    behavior_mode: BehaviorMode
    success: bool = True
    errors: tuple[str, ...] = ()


# ─── Loader ──────────────────────────────────────────────────────────


class PresetLoader:
    """Disk-backed loader + single-writer apply path for menu active keys."""

    def __init__(self, search_paths: list[Path] | None = None) -> None:
        if search_paths is None:
            search_paths = self._default_search_paths()
        self._search_paths: list[Path] = [Path(p) for p in search_paths]

    @staticmethod
    def _default_search_paths() -> list[Path]:
        out: list[Path] = []
        env = os.environ.get(PRESETS_DIR_ENV, "").strip()
        if env:
            out.extend(Path(p) for p in env.split(os.pathsep) if p)
        # Repo-root data/presets — Brain runs from repo root in dev / CI.
        out.append(Path("data") / "presets")
        return out

    # ─── Public API ──────────────────────────────────────────────

    def list_presets(self) -> list[str]:
        seen: set[str] = set()
        for d in self._search_paths:
            try:
                if not d.is_dir():
                    continue
                for f in sorted(d.glob("*.json")):
                    seen.add(f.stem)
            except OSError:
                continue
        return sorted(seen)

    def load(self, preset_id: str) -> Preset:
        """Return ``Preset`` for ``preset_id``; falls back to builtin default."""
        path = self._find(preset_id)
        if path is None:
            if preset_id == DEFAULT_PRESET_ID:
                logger.info(
                    "preset_loader: %s not found on disk — using builtin default",
                    preset_id,
                )
                return Preset.builtin_default()
            logger.warning("preset_loader: %s not found — falling back to default", preset_id)
            return self.load(DEFAULT_PRESET_ID)
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            return Preset.from_json(raw)
        except (OSError, ValueError, json.JSONDecodeError):
            logger.exception("preset_loader: failed to parse %s — using builtin default", path)
            return Preset.builtin_default()

    def save(self, preset: Preset) -> Path:
        """Write ``preset`` to the first writable directory in search paths.

        Returns the full file path. Creates parents as needed.
        """
        target_dir = self._writable_dir()
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / f"{preset.preset_id}.json"
        path.write_text(
            json.dumps(preset.as_json(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    def apply(self, preset: Preset) -> PresetApplyResult:
        """Write the menu ``global/active_*`` BB keys for ``preset``.

        Returns a :class:`PresetApplyResult` regardless of whether the BB
        client is available — the menu UI must surface success/failure to
        the user.
        """
        return self._apply_values(
            preset_id=preset.preset_id,
            behavior_mode=preset.behavior_mode(),
            values={
                "global/active_persona_id": preset.active_persona_id,
                "global/active_model_id": preset.active_model_id,
                "global/active_scene_id": preset.active_scene_id,
                "global/active_mode": list(preset.active_mode),
                "global/active_workspace_id": preset.active_workspace_id,
            },
        )

    def apply_workspace_id(
        self,
        workspace_id: str,
        *,
        preset_id: str = "workspace_only",
    ) -> PresetApplyResult:
        """Apply only ``global/active_workspace_id`` through the same writer.

        reason: Workspace switching is a frequent in-session operation. It
        needs the PresetLoader writer so the BB single-writer contract remains
        true, but it must not rewrite model/persona/mode/scene or tear down the
        LiveKit room.
        """
        safe = str(workspace_id or DEFAULT_WORKSPACE_ID).strip() or DEFAULT_WORKSPACE_ID
        return self._apply_values(
            preset_id=preset_id,
            behavior_mode=BehaviorMode.BASE | BehaviorMode.COMPANION,
            values={"global/active_workspace_id": safe},
        )

    def _apply_values(
        self,
        *,
        preset_id: str,
        behavior_mode: BehaviorMode,
        values: dict[str, Any],
    ) -> PresetApplyResult:
        try:
            from parrot.scheduler.blackboard import open_bb_client
        except Exception:
            return PresetApplyResult(
                preset_id=preset_id,
                applied_keys=(),
                behavior_mode=behavior_mode,
                success=False,
                errors=("blackboard module unavailable",),
            )

        try:
            bb = open_bb_client(name="preset_loader.apply", writer="brain.preset_loader")
        except Exception as exc:  # noqa: BLE001
            return PresetApplyResult(
                preset_id=preset_id,
                applied_keys=(),
                behavior_mode=behavior_mode,
                success=False,
                errors=(f"open_bb_client failed: {exc!r}",),
            )

        applied: list[str] = []
        errors: list[str] = []
        new_values: dict[str, Any] = {}

        def _try_set(key: str, value: Any) -> None:
            try:
                bb.set(key, value)
                applied.append(key)
                new_values[key] = value
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{key}: {exc!r}")

        for key, value in values.items():
            _try_set(key, value)

        # Fan out to any in-process watcher subscribers (persona reload /
        # mode_watcher / scene_watcher). Cross-process watchers (Redis
        # Pub/Sub) are still wired by their own modules — this only
        # services local subscribers in the same Python process.
        try:
            from parrot.brain.bb_watchers import fire_watcher

            for key, value in new_values.items():
                fire_watcher(key, value)
        except Exception:
            logger.exception("preset_loader: watcher fan-out failed")

        return PresetApplyResult(
            preset_id=preset_id,
            applied_keys=tuple(applied),
            behavior_mode=behavior_mode,
            success=not errors,
            errors=tuple(errors),
        )

    # ─── Internals ───────────────────────────────────────────────

    def _find(self, preset_id: str) -> Path | None:
        safe = preset_id.strip()
        if not safe or "/" in safe or "\\" in safe or ".." in safe:
            return None
        for d in self._search_paths:
            candidate = d / f"{safe}.json"
            if candidate.is_file():
                return candidate
        return None

    def _writable_dir(self) -> Path:
        for d in self._search_paths:
            try:
                d.mkdir(parents=True, exist_ok=True)
                return d
            except OSError:
                continue
        return Path("data") / "presets"


# ─── Singleton + test injection ──────────────────────────────────────


_loader: PresetLoader | None = None


def get_preset_loader() -> PresetLoader:
    global _loader
    if _loader is None:
        _loader = PresetLoader()
    return _loader


def set_preset_loader_for_test(loader: PresetLoader | None) -> None:
    global _loader
    _loader = loader


__all__ = [
    "DEFAULT_MODEL_ID",
    "DEFAULT_PRESET_ID",
    "DEFAULT_SCENE_ID",
    "DEFAULT_WORKSPACE_ID",
    "PRESETS_DIR_ENV",
    "Preset",
    "PresetApplyResult",
    "PresetLoader",
    "get_preset_loader",
    "set_preset_loader_for_test",
]
