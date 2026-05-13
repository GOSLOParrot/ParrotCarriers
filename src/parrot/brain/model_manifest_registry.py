"""Brain-side mirror of Unity model manifests.

Unity owns the actual prefab/controller lifecycle. Brain still needs a small
read-only mirror so RoomSetting, tool gating, and test reports can answer one
question consistently: which capabilities does the selected model declare?
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from parrot.shared.model_manifest import (
    DEFAULT_MODEL_ID,
    RESERVED_PARROT_CAPABILITY_IDS,
    Capability,
    CapabilityKind,
    ModelManifest,
)

logger = logging.getLogger(__name__)

MODEL_MANIFEST_DIR_ENV = "PARROT_MODEL_MANIFEST_DIR"

_REPO_ROOT = Path(__file__).resolve().parents[3]
_UNITY_MODEL_MANIFEST_DIR = (
    _REPO_ROOT
    / "unity"
    / "ArSpike"
    / "Assets"
    / "ParrotApp"
    / "Resources"
    / "parrot_models"
)


class ModelManifestRegistry:
    """Disk-backed model manifest registry used by Brain/UI read models."""

    def __init__(self, search_paths: list[Path] | None = None) -> None:
        if search_paths is None:
            search_paths = self._default_search_paths()
        self._search_paths = [Path(p) for p in search_paths]

    @staticmethod
    def _default_search_paths() -> list[Path]:
        out: list[Path] = []
        env = os.environ.get(MODEL_MANIFEST_DIR_ENV, "").strip()
        if env:
            out.extend(Path(p) for p in env.split(os.pathsep) if p)
        out.append(_UNITY_MODEL_MANIFEST_DIR)
        return out

    def list_manifests(self) -> tuple[ModelManifest, ...]:
        by_id: dict[str, ModelManifest] = {DEFAULT_MODEL_ID: _builtin_goslo_manifest()}
        for directory in self._search_paths:
            try:
                if not directory.is_dir():
                    continue
                for path in sorted(directory.glob("*.json")):
                    try:
                        manifest = ModelManifest.model_validate_json(
                            path.read_text(encoding="utf-8")
                        )
                    except Exception:
                        logger.exception("ModelManifestRegistry: failed to parse %s", path)
                        continue
                    by_id[manifest.model_id] = manifest
            except OSError:
                continue
        ordered_ids = [DEFAULT_MODEL_ID] + sorted(
            model_id for model_id in by_id if model_id != DEFAULT_MODEL_ID
        )
        return tuple(by_id[model_id] for model_id in ordered_ids)

    def get(self, model_id: str) -> ModelManifest | None:
        safe = str(model_id or "").strip()
        if not safe:
            return None
        for manifest in self.list_manifests():
            if manifest.model_id == safe:
                return manifest
        return None

    def capability(self, model_id: str, capability_id: str) -> Capability | None:
        manifest = self.get(model_id)
        if manifest is None:
            return None
        for capability in manifest.capabilities:
            if capability.capability_id == capability_id:
                return capability
        return None

    def supports(self, model_id: str, capability_id: str) -> bool:
        manifest = self.get(model_id)
        return bool(manifest and manifest.supports(capability_id))

    def capability_ids(self, model_id: str) -> frozenset[str]:
        manifest = self.get(model_id)
        return manifest.declared_capability_ids if manifest else frozenset()

    def parrot_reflex_enabled(self, model_id: str) -> bool:
        manifest = self.get(model_id)
        return bool(manifest and manifest.parrot_reflex_enabled)


def _builtin_goslo_manifest() -> ModelManifest:
    return ModelManifest(
        model_id=DEFAULT_MODEL_ID,
        display_name="GOSLO (default parrot)",
        asset_path="parrot_models/goslo_default",
        controller_type="ParrotApp.Parrot.GosloLegacyController",
        auto_scale_to_pet_height=False,
        capabilities=tuple(
            Capability(
                capability_id=capability_id,
                kind=(
                    CapabilityKind.ANIMATION
                    if capability_id in {"wing_flap", "head_bob"}
                    else CapabilityKind.POSE
                ),
                handler=capability_id,
            )
            for capability_id in sorted(RESERVED_PARROT_CAPABILITY_IDS)
        ),
    )


_registry: ModelManifestRegistry | None = None


def get_model_manifest_registry() -> ModelManifestRegistry:
    global _registry
    if _registry is None:
        _registry = ModelManifestRegistry()
    return _registry


def set_model_manifest_registry_for_test(registry: ModelManifestRegistry | None) -> None:
    global _registry
    _registry = registry


__all__ = [
    "MODEL_MANIFEST_DIR_ENV",
    "ModelManifestRegistry",
    "get_model_manifest_registry",
    "set_model_manifest_registry_for_test",
]
