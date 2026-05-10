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
from dataclasses import dataclass, field, replace
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
ROOM_PROFILE_SCHEMA_VERSION = 3
DEFAULT_LINE_ID = "line_a"
DEFAULT_LINE_PROFILE_ID = "linea_gemini_realtime"
DEFAULT_LINEB_PROFILE_ID = "lineb_google_default"
DEFAULT_ASR_PROFILE_ID = ""
DEFAULT_TTS_PROFILE_ID = ""
DEFAULT_VOICEPRINT_PROFILE_ID = ""
DEFAULT_ECHO_POLICY_ID = ""
DEFAULT_EXPERIENCE_MODE = "ar_companion"
DEFAULT_LIVEKIT_ROOM_ID = "parrot-main"
DEFAULT_SCENE_SKIN_ID = "goslo_default"
DEFAULT_CANVAS_PRESET_ID = "default_canvas"
DEFAULT_MENU_PREFERENCE_ID = "default_menu"


def _clean_text(value: Any, fallback: str) -> str:
    text = str(value or "").strip()
    return text or fallback


def _tuple_from_raw(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return tuple(s.strip() for s in value.split("|") if s.strip())
    if isinstance(value, (list, tuple)):
        return tuple(str(x).strip() for x in value if str(x).strip())
    return ()


def _default_line_profile_id(line_id: str) -> str:
    return (
        DEFAULT_LINEB_PROFILE_ID
        if str(line_id or "").strip().lower() == "line_b"
        else DEFAULT_LINE_PROFILE_ID
    )


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
class RoomProfile:
    """App-level saved Room profile shown by startup RoomSetting.

    ``Room`` is the user-facing name. ``RoomProfile`` is the internal schema.
    It intentionally supersets the older v2 ``Preset`` so existing
    ``data/presets/*.json`` files remain readable while RoomSetting gains Line,
    ExperienceMode, skin, and menu/canvas persistence anchors.
    """

    room_profile_id: str
    display_name: str
    model_id: str = DEFAULT_MODEL_ID
    persona_id: str = DEFAULT_PERSONA_ID
    line_id: str = DEFAULT_LINE_ID
    line_profile_id: str = DEFAULT_LINE_PROFILE_ID
    asr_profile_id: str = DEFAULT_ASR_PROFILE_ID
    tts_profile_id: str = DEFAULT_TTS_PROFILE_ID
    voiceprint_profile_id: str = DEFAULT_VOICEPRINT_PROFILE_ID
    echo_policy_id: str = DEFAULT_ECHO_POLICY_ID
    scene_profile_id: str = DEFAULT_SCENE_ID
    experience_mode: str = DEFAULT_EXPERIENCE_MODE
    workspace_id: str = DEFAULT_WORKSPACE_ID
    map_id: str = DEFAULT_WORKSPACE_ID
    skin_id: str = DEFAULT_SCENE_SKIN_ID
    setting_file_refs: tuple[str, ...] = ()
    livekit_room_id: str = DEFAULT_LIVEKIT_ROOM_ID
    canvas_preset_id: str = DEFAULT_CANVAS_PRESET_ID
    menu_preference_id: str = DEFAULT_MENU_PREFERENCE_ID
    behavior_mode_defaults: tuple[str, ...] = ("BASE", "COMPANION")
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def builtin_default(cls) -> "RoomProfile":
        return cls(
            room_profile_id=DEFAULT_PRESET_ID,
            display_name="Default GOSLO Room",
        )

    @classmethod
    def from_preset(cls, preset: Preset) -> "RoomProfile":
        metadata = dict(preset.metadata)
        display_name = _clean_text(
            metadata.get("display_name") or metadata.get("user_label"),
            preset.preset_id,
        )
        line_id = _clean_text(
            metadata.get("line_id") or metadata.get("pipeline_id"),
            DEFAULT_LINE_ID,
        )
        line_profile_id = _clean_text(
            metadata.get("line_profile_id"),
            _default_line_profile_id(line_id),
        )
        experience_mode = _clean_text(
            metadata.get("experience_mode"),
            DEFAULT_EXPERIENCE_MODE,
        )
        skin_id = _clean_text(
            metadata.get("skin_id") or metadata.get("theme_skin"),
            DEFAULT_SCENE_SKIN_ID,
        )
        return cls(
            room_profile_id=preset.preset_id,
            display_name=display_name,
            model_id=preset.active_model_id,
            persona_id=preset.active_persona_id,
            line_id=line_id,
            line_profile_id=line_profile_id,
            asr_profile_id=_clean_text(
                metadata.get("asr_profile_id"),
                DEFAULT_ASR_PROFILE_ID,
            ),
            tts_profile_id=_clean_text(
                metadata.get("tts_profile_id"),
                DEFAULT_TTS_PROFILE_ID,
            ),
            voiceprint_profile_id=_clean_text(
                metadata.get("voiceprint_profile_id"),
                DEFAULT_VOICEPRINT_PROFILE_ID,
            ),
            echo_policy_id=_clean_text(
                metadata.get("echo_policy_id"),
                DEFAULT_ECHO_POLICY_ID,
            ),
            scene_profile_id=preset.active_scene_id,
            experience_mode=experience_mode,
            workspace_id=preset.active_workspace_id,
            map_id=_clean_text(metadata.get("map_id"), preset.active_workspace_id),
            skin_id=skin_id,
            setting_file_refs=_tuple_from_raw(metadata.get("setting_file_refs")),
            livekit_room_id=_clean_text(
                metadata.get("livekit_room_id"),
                DEFAULT_LIVEKIT_ROOM_ID,
            ),
            canvas_preset_id=_clean_text(
                metadata.get("canvas_preset_id"),
                DEFAULT_CANVAS_PRESET_ID,
            ),
            menu_preference_id=_clean_text(
                metadata.get("menu_preference_id"),
                DEFAULT_MENU_PREFERENCE_ID,
            ),
            behavior_mode_defaults=preset.active_mode or ("BASE", "COMPANION"),
            metadata=metadata,
        )

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> "RoomProfile":
        if not isinstance(raw, dict):
            raise ValueError("room profile payload must be a JSON object")
        is_room_profile = (
            raw.get("kind") == "room_profile"
            or int(raw.get("schema_version") or 0) >= ROOM_PROFILE_SCHEMA_VERSION
            or "room_profile_id" in raw
        )
        if not is_room_profile:
            return cls.from_preset(Preset.from_json(raw))

        metadata = dict(raw.get("metadata") or {})
        room_profile_id = _clean_text(
            raw.get("room_profile_id") or raw.get("preset_id"),
            DEFAULT_PRESET_ID,
        )
        workspace_id = _clean_text(
            raw.get("workspace_id") or raw.get("active_workspace_id"),
            DEFAULT_WORKSPACE_ID,
        )
        behavior_defaults = (
            _tuple_from_raw(raw.get("behavior_mode_defaults"))
            or _tuple_from_raw(raw.get("active_mode"))
            or _tuple_from_raw(metadata.get("behavior_mode_defaults"))
            or ("BASE", "COMPANION")
        )
        line_id = _clean_text(
            raw.get("line_id")
            or raw.get("pipeline_id")
            or raw.get("brain_pipeline")
            or metadata.get("line_id"),
            DEFAULT_LINE_ID,
        )
        return cls(
            room_profile_id=room_profile_id,
            display_name=_clean_text(raw.get("display_name"), room_profile_id),
            model_id=_clean_text(
                raw.get("model_id") or raw.get("active_model_id"),
                DEFAULT_MODEL_ID,
            ),
            persona_id=_clean_text(
                raw.get("persona_id") or raw.get("active_persona_id"),
                DEFAULT_PERSONA_ID,
            ),
            line_id=line_id,
            line_profile_id=_clean_text(
                raw.get("line_profile_id") or metadata.get("line_profile_id"),
                _default_line_profile_id(line_id),
            ),
            asr_profile_id=_clean_text(
                raw.get("asr_profile_id") or metadata.get("asr_profile_id"),
                DEFAULT_ASR_PROFILE_ID,
            ),
            tts_profile_id=_clean_text(
                raw.get("tts_profile_id") or metadata.get("tts_profile_id"),
                DEFAULT_TTS_PROFILE_ID,
            ),
            voiceprint_profile_id=_clean_text(
                raw.get("voiceprint_profile_id") or metadata.get("voiceprint_profile_id"),
                DEFAULT_VOICEPRINT_PROFILE_ID,
            ),
            echo_policy_id=_clean_text(
                raw.get("echo_policy_id") or metadata.get("echo_policy_id"),
                DEFAULT_ECHO_POLICY_ID,
            ),
            scene_profile_id=_clean_text(
                raw.get("scene_profile_id") or raw.get("active_scene_id"),
                DEFAULT_SCENE_ID,
            ),
            experience_mode=_clean_text(
                raw.get("experience_mode") or metadata.get("experience_mode"),
                DEFAULT_EXPERIENCE_MODE,
            ),
            workspace_id=workspace_id,
            map_id=_clean_text(raw.get("map_id"), workspace_id),
            skin_id=_clean_text(
                raw.get("skin_id") or metadata.get("skin_id") or metadata.get("theme_skin"),
                DEFAULT_SCENE_SKIN_ID,
            ),
            setting_file_refs=_tuple_from_raw(raw.get("setting_file_refs")),
            livekit_room_id=_clean_text(
                raw.get("livekit_room_id") or metadata.get("livekit_room_id"),
                DEFAULT_LIVEKIT_ROOM_ID,
            ),
            canvas_preset_id=_clean_text(
                raw.get("canvas_preset_id") or metadata.get("canvas_preset_id"),
                DEFAULT_CANVAS_PRESET_ID,
            ),
            menu_preference_id=_clean_text(
                raw.get("menu_preference_id") or metadata.get("menu_preference_id"),
                DEFAULT_MENU_PREFERENCE_ID,
            ),
            behavior_mode_defaults=tuple(s.upper() for s in behavior_defaults),
            metadata=metadata,
        )

    def as_json(self) -> dict[str, Any]:
        return {
            "schema_version": ROOM_PROFILE_SCHEMA_VERSION,
            "kind": "room_profile",
            "room_profile_id": self.room_profile_id,
            "display_name": self.display_name,
            "model_id": self.model_id,
            "persona_id": self.persona_id,
            "line_id": self.line_id,
            "line_profile_id": self.line_profile_id,
            "asr_profile_id": self.asr_profile_id,
            "tts_profile_id": self.tts_profile_id,
            "voiceprint_profile_id": self.voiceprint_profile_id,
            "echo_policy_id": self.echo_policy_id,
            "scene_profile_id": self.scene_profile_id,
            "experience_mode": self.experience_mode,
            "workspace_id": self.workspace_id,
            "map_id": self.map_id,
            "skin_id": self.skin_id,
            "setting_file_refs": list(self.setting_file_refs),
            "livekit_room_id": self.livekit_room_id,
            "canvas_preset_id": self.canvas_preset_id,
            "menu_preference_id": self.menu_preference_id,
            "behavior_mode_defaults": list(self.behavior_mode_defaults),
            "metadata": dict(self.metadata),
        }

    def to_preset(self) -> Preset:
        metadata = dict(self.metadata)
        metadata.update(
            {
                "room_profile_id": self.room_profile_id,
                "display_name": self.display_name,
                "line_id": self.line_id,
                "line_profile_id": self.line_profile_id,
                "asr_profile_id": self.asr_profile_id,
                "tts_profile_id": self.tts_profile_id,
                "voiceprint_profile_id": self.voiceprint_profile_id,
                "echo_policy_id": self.echo_policy_id,
                "experience_mode": self.experience_mode,
                "map_id": self.map_id,
                "skin_id": self.skin_id,
                "livekit_room_id": self.livekit_room_id,
                "canvas_preset_id": self.canvas_preset_id,
                "menu_preference_id": self.menu_preference_id,
                "setting_file_refs": list(self.setting_file_refs),
            }
        )
        return Preset(
            preset_id=self.room_profile_id,
            active_model_id=self.model_id,
            active_persona_id=self.persona_id,
            active_mode=tuple(s.upper() for s in self.behavior_mode_defaults),
            active_scene_id=self.scene_profile_id,
            active_workspace_id=self.workspace_id,
            metadata=metadata,
        )

    def behavior_mode(self) -> BehaviorMode:
        return self.to_preset().behavior_mode()

    def with_experience_mode(self, experience_mode: str | None) -> "RoomProfile":
        if not experience_mode:
            return self
        return replace(
            self,
            experience_mode=str(experience_mode).strip() or self.experience_mode,
        )


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

    def list_room_profiles(self) -> tuple[RoomProfile, ...]:
        """List every saved RoomProfile, migrating v1/v2 presets on read."""
        seen: dict[str, RoomProfile] = {}
        for d in self._search_paths:
            try:
                if not d.is_dir():
                    continue
                for f in sorted(d.glob("*.json")):
                    try:
                        profile = RoomProfile.from_json(
                            json.loads(f.read_text(encoding="utf-8"))
                        )
                    except (OSError, ValueError, json.JSONDecodeError):
                        logger.exception("preset_loader: failed to parse room profile %s", f)
                        continue
                    seen[profile.room_profile_id] = profile
            except OSError:
                continue
        if not seen:
            default = self.load_room_profile(DEFAULT_PRESET_ID)
            seen[default.room_profile_id] = default
        return tuple(
            sorted(
                seen.values(),
                key=lambda p: (p.display_name.lower(), p.room_profile_id),
            )
        )

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

    def load_room_profile(self, room_profile_id: str) -> RoomProfile:
        """Return a RoomProfile; v1/v2 preset files migrate on read."""
        path = self._find(room_profile_id)
        if path is None:
            if room_profile_id == DEFAULT_PRESET_ID:
                logger.info(
                    "preset_loader: %s not found on disk - using builtin room profile",
                    room_profile_id,
                )
                return RoomProfile.builtin_default()
            logger.warning(
                "preset_loader: room profile %s not found - falling back to default",
                room_profile_id,
            )
            return self.load_room_profile(DEFAULT_PRESET_ID)
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            return RoomProfile.from_json(raw)
        except (OSError, ValueError, json.JSONDecodeError):
            logger.exception(
                "preset_loader: failed to parse room profile %s - using builtin default",
                path,
            )
            return RoomProfile.builtin_default()

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

    def save_room_profile(self, profile: RoomProfile) -> Path:
        """Persist ``profile`` as the user-facing Room save file."""
        target_dir = self._writable_dir()
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / f"{profile.room_profile_id}.json"
        path.write_text(
            json.dumps(profile.as_json(), ensure_ascii=False, indent=2),
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

    def apply_room_profile(
        self,
        profile: RoomProfile,
        *,
        experience_mode: str | None = None,
    ) -> PresetApplyResult:
        """Apply one RoomProfile through the same single-writer path."""
        selected = profile.with_experience_mode(experience_mode)
        return self._apply_values(
            preset_id=selected.room_profile_id,
            behavior_mode=selected.behavior_mode(),
            values={
                "global/active_room_profile_id": selected.room_profile_id,
                "global/active_persona_id": selected.persona_id,
                "global/active_model_id": selected.model_id,
                "global/active_scene_id": selected.scene_profile_id,
                "global/active_mode": list(selected.behavior_mode_defaults),
                "global/active_workspace_id": selected.workspace_id,
                "global/active_line_id": selected.line_id,
                "global/active_line_profile_id": selected.line_profile_id,
                "global/active_asr_profile_id": selected.asr_profile_id,
                "global/active_tts_profile_id": selected.tts_profile_id,
                "global/active_voiceprint_profile_id": selected.voiceprint_profile_id,
                "global/active_echo_policy_id": selected.echo_policy_id,
                "global/active_experience_mode": selected.experience_mode,
                "global/active_scene_skin_id": selected.skin_id,
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
    "DEFAULT_EXPERIENCE_MODE",
    "DEFAULT_ASR_PROFILE_ID",
    "DEFAULT_ECHO_POLICY_ID",
    "DEFAULT_LINE_ID",
    "DEFAULT_LINE_PROFILE_ID",
    "DEFAULT_LINEB_PROFILE_ID",
    "DEFAULT_LIVEKIT_ROOM_ID",
    "DEFAULT_MENU_PREFERENCE_ID",
    "DEFAULT_PRESET_ID",
    "DEFAULT_SCENE_ID",
    "DEFAULT_SCENE_SKIN_ID",
    "DEFAULT_TTS_PROFILE_ID",
    "DEFAULT_VOICEPRINT_PROFILE_ID",
    "DEFAULT_WORKSPACE_ID",
    "PRESETS_DIR_ENV",
    "Preset",
    "PresetApplyResult",
    "PresetLoader",
    "ROOM_PROFILE_SCHEMA_VERSION",
    "RoomProfile",
    "get_preset_loader",
    "set_preset_loader_for_test",
]
