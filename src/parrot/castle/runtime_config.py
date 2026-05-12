"""ECS-side runtime config layering.

This module is the single read source for "what should the next
``brain_entrypoint`` use" decisions:

* ``line_id`` (line_a / line_b)
* ``line_profile_id``
* ``room_profile_id``

And the single write source for the future Castle Orchestrator
(see ``app_v1_brain_cold_start_line_lifecycle_audit_20260511.md``
§Phase 2). It deliberately avoids touching ``os.environ`` of the
running Brain process so Tier 1 changes (per the setting-change tier
matrix) can take effect at the next LiveKit room job without a
process restart.

Resolution order (highest priority first):

1. ``data/runtime_config.json`` — orchestrator-controlled file. Wins
   over both BB and env so a deliberate Castle-side write can flip a
   Line on the next reconnect even if env was set differently at
   process boot.
2. Blackboard (``global/active_line_id`` etc.) — runtime apply path
   used by ``apply_room_profile``.
3. Process env (``PARROT_LLM_PIPELINE`` etc.) — boot-time selection.
4. Hard-coded default (``line_a``, default RoomProfile / LineProfile).

Why not just write env? Because ``os.environ`` mutation in a
long-running process has subtle visibility issues across asyncio task
boundaries, child subprocesses, and re-imported modules. A file
+ structured loader is explicit, atomic on POSIX (write-rename), and
also lets the orchestrator audit "what did the next session see" by
just reading the file.

Format (``data/runtime_config.json``)::

    {
      "schema_version": 1,
      "updated_at": 1715000000.0,
      "updated_by": "castle.orchestrator",
      "line_id": "line_b",
      "line_profile_id": "lineb_google_default",
      "room_profile_id": "ner_lineb_room",
      "notes": "Auto-set by orchestrator /set_active_line"
    }

All keys are optional; missing keys fall through to BB / env / default.

The file is read on every ``brain_entrypoint`` invocation (cheap —
small JSON, sub-millisecond) so a write made while a room is live
takes effect on the next room join.
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


_ENV_LINE_ID = "PARROT_LLM_PIPELINE"
_ENV_LINE_PROFILE_ID = "PARROT_ACTIVE_LINE_PROFILE_ID"
_ENV_ROOM_PROFILE_ID = "PARROT_ACTIVE_ROOM_PROFILE_ID"

_KNOWN_LINE_IDS = ("line_a", "line_b")
_DEFAULT_LINE_ID = "line_a"

_SCHEMA_VERSION = 1


def _project_root() -> Path:
    """Return the ParrotCarriers repository root.

    The runtime config file lives at ``<root>/data/runtime_config.json``.
    The lookup walks up from this module file because installed wheels
    or development checkouts both put ``parrot/castle/runtime_config.py``
    a fixed depth below the repo root via ``src/parrot/...``.
    """
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "data").is_dir() and (parent / "src").is_dir():
            return parent
    # Fallback: assume parents[3] (src/parrot/castle/runtime_config.py → repo).
    return here.parents[3]


def runtime_config_path() -> Path:
    """Override path with ``PARROT_RUNTIME_CONFIG_PATH`` for tests."""
    override = os.getenv("PARROT_RUNTIME_CONFIG_PATH", "").strip()
    if override:
        return Path(override).expanduser()
    return _project_root() / "data" / "runtime_config.json"


@dataclass(frozen=True)
class RuntimeConfig:
    """Resolved runtime config snapshot.

    ``source`` is a per-field map: ``{"line_id": "file"}`` etc. This is
    what lets the orchestrator status endpoint and the
    ``global/brain_runtime_snapshot`` BB write surface "this came from
    the file" vs "this came from env" without callers having to
    re-parse the file.
    """

    line_id: str
    line_profile_id: str
    room_profile_id: str
    source: dict[str, str]
    raw_file: dict[str, Any]
    file_path: str
    file_present: bool

    def as_json(self) -> dict[str, Any]:
        return {
            "line_id": self.line_id,
            "line_profile_id": self.line_profile_id,
            "room_profile_id": self.room_profile_id,
            "source": dict(self.source),
            "raw_file": dict(self.raw_file),
            "file_path": self.file_path,
            "file_present": self.file_present,
        }


def _read_file_payload(path: Path) -> tuple[dict[str, Any], bool]:
    """Best-effort read; returns ``({}, False)`` when missing / unreadable."""
    if not path.is_file():
        return {}, False
    try:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
    except (OSError, ValueError):
        logger.warning(
            "[runtime_config] failed to parse %s; falling back to BB+env",
            path,
        )
        return {}, True
    return (data if isinstance(data, dict) else {}), True


def _bb_get(key: str) -> Any:
    """Read BB without holding a long-lived client. Best-effort."""
    try:
        from parrot.scheduler.blackboard import open_bb_client

        bb = open_bb_client(name="castle.runtime_config", writer=None)
        return bb.get(key)
    except Exception:
        return None


def _normalize_line_id(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    raw = value.strip().lower()
    if raw in _KNOWN_LINE_IDS:
        return raw
    return None


def _normalize_id(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    raw = value.strip()
    return raw or None


def resolve_runtime_config() -> RuntimeConfig:
    """Resolve the active line/profile triple per the layering rule.

    Reads the file once, BB on misses, env on misses, defaults last.
    Each key reports its own source.
    """
    path = runtime_config_path()
    payload, file_present = _read_file_payload(path)

    line_id, line_id_src = _resolve_one(
        file_value=payload.get("line_id"),
        bb_key="global/active_line_id",
        env_key=_ENV_LINE_ID,
        default=_DEFAULT_LINE_ID,
        normalizer=_normalize_line_id,
    )
    line_profile_id, lp_src = _resolve_one(
        file_value=payload.get("line_profile_id"),
        bb_key="global/active_line_profile_id",
        env_key=_ENV_LINE_PROFILE_ID,
        default="",
        normalizer=_normalize_id,
    )
    room_profile_id, rp_src = _resolve_one(
        file_value=payload.get("room_profile_id"),
        bb_key="global/active_room_profile_id",
        env_key=_ENV_ROOM_PROFILE_ID,
        default="",
        normalizer=_normalize_id,
    )

    return RuntimeConfig(
        line_id=line_id,
        line_profile_id=line_profile_id,
        room_profile_id=room_profile_id,
        source={
            "line_id": line_id_src,
            "line_profile_id": lp_src,
            "room_profile_id": rp_src,
        },
        raw_file=payload,
        file_path=str(path),
        file_present=file_present,
    )


def _resolve_one(
    *,
    file_value: Any,
    bb_key: str,
    env_key: str,
    default: str,
    normalizer,
) -> tuple[str, str]:
    """Resolve one field, returning ``(value, source_label)``.

    ``source_label`` is one of ``file``, ``bb``, ``env``, ``default``.
    Used by the status snapshot to make the layering visible.
    """
    normalized = normalizer(file_value)
    if normalized:
        return normalized, "file"
    bb_value = _bb_get(bb_key)
    normalized = normalizer(bb_value)
    if normalized:
        return normalized, "bb"
    env_value = os.getenv(env_key, "")
    normalized = normalizer(env_value)
    if normalized:
        return normalized, "env"
    return default, "default"


def write_runtime_config(
    *,
    line_id: str | None = None,
    line_profile_id: str | None = None,
    room_profile_id: str | None = None,
    updated_by: str = "castle.orchestrator",
    notes: str = "",
) -> RuntimeConfig:
    """Atomically write a partial runtime config update.

    Only the keys that are explicitly passed get touched; the others
    are preserved from the existing file. This is what lets the
    orchestrator do ``set_active_line({"line_id": "line_b"})``
    without clobbering ``room_profile_id``.

    Validation:
      * ``line_id`` must be ``line_a`` / ``line_b``; ``ValueError``
        otherwise (the orchestrator surfaces this as 400).
      * ``line_profile_id`` / ``room_profile_id`` must be non-empty
        strings if provided.

    Returns the resolved config *after* the write so the caller can
    mirror it back to BB / response immediately.
    """
    path = runtime_config_path()
    existing, _present = _read_file_payload(path)

    new_payload: dict[str, Any] = dict(existing)
    new_payload["schema_version"] = _SCHEMA_VERSION
    new_payload["updated_at"] = time.time()
    new_payload["updated_by"] = updated_by
    if notes:
        new_payload["notes"] = notes

    if line_id is not None:
        normalized = _normalize_line_id(line_id)
        if normalized is None:
            raise ValueError(
                f"line_id must be one of {_KNOWN_LINE_IDS}; got {line_id!r}"
            )
        new_payload["line_id"] = normalized
    if line_profile_id is not None:
        normalized = _normalize_id(line_profile_id)
        if normalized is None:
            raise ValueError("line_profile_id must be a non-empty string")
        new_payload["line_profile_id"] = normalized
    if room_profile_id is not None:
        normalized = _normalize_id(room_profile_id)
        if normalized is None:
            raise ValueError("room_profile_id must be a non-empty string")
        new_payload["room_profile_id"] = normalized

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(new_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)
    logger.info(
        "[runtime_config] wrote %s (line=%s line_profile=%s room=%s by=%s)",
        path,
        new_payload.get("line_id"),
        new_payload.get("line_profile_id"),
        new_payload.get("room_profile_id"),
        updated_by,
    )
    return resolve_runtime_config()


def clear_runtime_config(*, missing_ok: bool = True) -> bool:
    """Delete the runtime config file (test helper / orchestrator reset).

    Returns ``True`` when a file was removed, ``False`` otherwise.
    """
    path = runtime_config_path()
    try:
        path.unlink()
        return True
    except FileNotFoundError:
        if missing_ok:
            return False
        raise


def write_brain_runtime_snapshot(
    *,
    pid: int,
    room_name: str,
    started_at: float,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Publish what this ``brain_entrypoint`` resolved to BB.

    The orchestrator / Web monitor / canvas voice tile all read
    ``global/brain_runtime_snapshot`` to know:

    * Which Line is actually being served right now.
    * Which layer (file / bb / env / default) provided each setting.
    * Whether a file write happened after this Brain was started — if
      ``raw_file.updated_at > started_at`` the orchestrator can infer
      "drift exists; a Tier 1 reconnect would change the live line".

    Best-effort: if BB is not reachable we still return the dict so
    the caller can log it. Never raises into the caller's loop.
    """
    resolved = resolve_runtime_config()
    snapshot: dict[str, Any] = {
        "pid": pid,
        "room_name": room_name,
        "started_at": started_at,
        "snapshot_at": time.time(),
        "line_id": resolved.line_id,
        "line_profile_id": resolved.line_profile_id,
        "room_profile_id": resolved.room_profile_id,
        "source": dict(resolved.source),
        "raw_file": dict(resolved.raw_file),
        "file_path": resolved.file_path,
        "file_present": resolved.file_present,
    }
    if extra:
        snapshot.update(extra)
    try:
        from parrot.scheduler.blackboard import open_bb_client

        bb = open_bb_client(
            name="castle.runtime_config.snapshot",
            writer="brain.agent",
        )
        bb.set("global/brain_runtime_snapshot", snapshot)
    except Exception:
        logger.warning(
            "[runtime_config] BB snapshot write failed; continuing",
            exc_info=True,
        )
    return snapshot


def clear_brain_runtime_snapshot() -> None:
    """Drop ``global/brain_runtime_snapshot`` on disconnect.

    Without this, an orchestrator status read between Brain disconnects
    and reconnects would still show the last room's snapshot and
    falsely suggest a Brain is live.
    """
    try:
        from parrot.scheduler.blackboard import open_bb_client

        bb = open_bb_client(
            name="castle.runtime_config.snapshot",
            writer="brain.agent",
        )
        bb.set("global/brain_runtime_snapshot", None)
    except Exception:
        logger.warning(
            "[runtime_config] BB snapshot clear failed; continuing",
            exc_info=True,
        )


__all__ = [
    "RuntimeConfig",
    "clear_brain_runtime_snapshot",
    "clear_runtime_config",
    "resolve_runtime_config",
    "runtime_config_path",
    "write_brain_runtime_snapshot",
    "write_runtime_config",
]
