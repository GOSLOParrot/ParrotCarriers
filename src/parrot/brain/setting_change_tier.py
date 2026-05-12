"""Setting-change tier registry loader (Phase 4.1).

Reads ``data/registries/setting_change_tier.json`` and exposes a
read-only API for ``RoomSettingService``, the orchestrator, and the
Unity startup page. The single source of truth lives in the JSON;
this module only parses, validates, and caches it.

Public surface:

* :func:`load_tier_registry` — full registry dict (cached).
* :func:`tier_for` — return the tier (0/1/2/3) for a given setting
  key. Falls back to a documented "unknown" tier when the key is not
  in the registry.
* :func:`tier_label` / :func:`tier_summary` — human-readable.
"""

from __future__ import annotations

import json
import logging
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TierEntry:
    """One row in the registry."""

    key: str
    tier: int
    doc: str = ""
    ui_action: str = ""
    elevates_to_tier_1_when: str = ""
    phase1_promise: bool = False

    def as_json(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "tier": self.tier,
            "doc": self.doc,
            "ui_action": self.ui_action,
            "elevates_to_tier_1_when": self.elevates_to_tier_1_when,
            "phase1_promise": self.phase1_promise,
        }


_DEFAULT_TIER = 2  # if a setting isn't catalogued, assume "needs Brain restart" (safe default)
_REGISTRY_RELATIVE = Path("data") / "registries" / "setting_change_tier.json"

_lock = threading.Lock()
_cached: dict[str, Any] | None = None
_cached_path: Path | None = None


def _registry_path() -> Path:
    """Walk up from this module to find the repo root."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / _REGISTRY_RELATIVE
        if candidate.is_file():
            return candidate
    return here.parents[3] / _REGISTRY_RELATIVE


def load_tier_registry(*, force_reload: bool = False) -> dict[str, Any]:
    """Return the parsed registry dict. Cached; reload via ``force_reload``."""
    global _cached, _cached_path
    if _cached is not None and not force_reload:
        return _cached
    with _lock:
        if _cached is not None and not force_reload:
            return _cached
        path = _registry_path()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            logger.warning("[setting_change_tier] registry not found at %s", path)
            data = {"schema_version": 1, "tiers": {}, "settings": []}
        except json.JSONDecodeError:
            logger.exception("[setting_change_tier] registry parse failed; using empty fallback")
            data = {"schema_version": 1, "tiers": {}, "settings": []}
        _cached = data
        _cached_path = path
    return _cached


def reset_cache() -> None:
    """Drop cached registry — used by tests after touching the file."""
    global _cached, _cached_path
    with _lock:
        _cached = None
        _cached_path = None


def list_tier_entries() -> tuple[TierEntry, ...]:
    registry = load_tier_registry()
    out: list[TierEntry] = []
    for raw in registry.get("settings", []):
        if not isinstance(raw, dict):
            continue
        try:
            tier = int(raw.get("tier", _DEFAULT_TIER))
        except Exception:
            tier = _DEFAULT_TIER
        out.append(
            TierEntry(
                key=str(raw.get("key", "")).strip(),
                tier=tier,
                doc=str(raw.get("doc", "")),
                ui_action=str(raw.get("ui_action", "")),
                elevates_to_tier_1_when=str(raw.get("elevates_to_tier_1_when", "")),
                phase1_promise=str(raw.get("phase1_promise", "")).lower()
                in {"1", "true", "yes"},
            )
        )
    return tuple(out)


def tier_for(setting_key: str) -> int:
    """Return the tier for ``setting_key`` (0–3)."""
    if not setting_key:
        return _DEFAULT_TIER
    for entry in list_tier_entries():
        if entry.key == setting_key:
            return entry.tier
    return _DEFAULT_TIER


def tier_label(tier: int) -> str:
    registry = load_tier_registry()
    return str(registry.get("tiers", {}).get(str(tier), {}).get("label", ""))


def tier_summary(tier: int, *, lang: str = "en") -> str:
    registry = load_tier_registry()
    tier_data = registry.get("tiers", {}).get(str(tier), {}) or {}
    if lang == "zh":
        return str(tier_data.get("summary_zh") or tier_data.get("summary_en", ""))
    return str(tier_data.get("summary_en", ""))


def tier_ui_action(tier: int) -> str:
    registry = load_tier_registry()
    return str(registry.get("tiers", {}).get(str(tier), {}).get("ui_action", ""))


def line_switch_tier_for_profile(profile_line_id: str, running_line_id: str) -> int:
    """Specialised resolver for the line_id selector.

    The static tier for ``line_id`` is ``1`` (Phase 1 promise). When
    the profile and running line agree, the change is a no-op and we
    report ``0`` so the UI doesn't show a needless reconnect prompt.
    """
    if profile_line_id and running_line_id and profile_line_id == running_line_id:
        return 0
    return tier_for("line_id")


__all__ = [
    "TierEntry",
    "line_switch_tier_for_profile",
    "list_tier_entries",
    "load_tier_registry",
    "reset_cache",
    "tier_for",
    "tier_label",
    "tier_summary",
    "tier_ui_action",
]
