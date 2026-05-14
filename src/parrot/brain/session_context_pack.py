"""Session context pack for RoomProfile startup context.

RoomSetting stores the selected model/persona/line/scene plus a list of
``setting_file_refs``. Those refs are not the persona itself; they are the
world, scene, action-manual, and Obsidian setting sources that should travel
with the room.

This module keeps the split explicit:

* persona markdown remains owned by ``PersonaLoader``;
* roleplay/daily Obsidian setting notes can be bootstrapped into L1.5;
* selected room context can be appended to the LLM system instructions.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from parrot.brain.obsidian_vault import note_to_ingest_payload, normalize_profile
from parrot.brain.preset_loader import DEFAULT_PRESET_ID, RoomProfile, get_preset_loader

logger = logging.getLogger(__name__)

ACTIVE_ROOM_PROFILE_ENV = "PARROT_ACTIVE_ROOM_PROFILE_ID"
ACTIVE_ROOM_PROFILE_ALIAS_ENV = "PARROT_ACTIVE_ROOM_PROFILE"
DISABLE_SESSION_CONTEXT_ENV = "PARROT_DISABLE_SESSION_CONTEXT_PACK"

_BB_KEY_ACTIVE_ROOM_PROFILE = "global/active_room_profile_id"
_BB_KEY_ACTIVE_ROOM_PROFILE_PAYLOAD = "global/active_room_profile"
_BOOTSTRAPPED_L15_KEYS: set[str] = set()
"""Best-effort in-process dedupe for L1.5 bootstrap events.

The key includes the note mtime, so editing a Room setting file during a dev
session can still re-enter L1.5 without restarting Brain.
"""


@dataclass(frozen=True)
class SessionContextSource:
    """One resolved file ref from ``RoomProfile.setting_file_refs``."""

    ref: str
    path: str
    title: str
    profile: str = ""
    kind: str = ""
    prompt_target: str = "llm"
    l15_target: str = ""
    status: str = "loaded"
    reason: str = ""
    text_excerpt: str = ""
    ingest_payload: dict[str, Any] | None = None

    def as_json(self) -> dict[str, Any]:
        return {
            "ref": self.ref,
            "path": self.path,
            "title": self.title,
            "profile": self.profile,
            "kind": self.kind,
            "prompt_target": self.prompt_target,
            "l15_target": self.l15_target,
            "status": self.status,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class SessionContextBundle:
    """Resolved startup context for the currently selected RoomProfile."""

    room_profile_id: str
    display_name: str
    model_id: str
    persona_id: str
    line_id: str
    scene_profile_id: str
    sources: tuple[SessionContextSource, ...] = ()
    llm_prompt_block: str = ""
    l15_payloads: tuple[dict[str, Any], ...] = ()

    @property
    def has_context(self) -> bool:
        return bool(self.llm_prompt_block or self.l15_payloads)

    def as_json(self) -> dict[str, Any]:
        return {
            "room_profile_id": self.room_profile_id,
            "display_name": self.display_name,
            "model_id": self.model_id,
            "persona_id": self.persona_id,
            "line_id": self.line_id,
            "scene_profile_id": self.scene_profile_id,
            "sources": [source.as_json() for source in self.sources],
            "llm_source_count": sum(
                1 for source in self.sources if "llm" in source.prompt_target
            ),
            "l15_payload_count": len(self.l15_payloads),
        }


def load_active_session_context_bundle(
    room_profile_id: str | None = None,
    *,
    max_chars: int = 9000,
    per_source_chars: int = 2200,
) -> SessionContextBundle:
    """Resolve the active RoomProfile into LLM + L1.5 startup context."""

    profile = _load_room_profile(room_profile_id)
    if _disabled():
        return _empty_bundle(profile)

    # Keep this read-only and deterministic: RoomSetting owns persistence,
    # PersonaLoader owns persona markdown, and this layer only resolves the
    # Room's attached context files into prompt/L1.5 projections.
    sources = [
        _load_source(ref, per_source_chars=per_source_chars)
        for ref in profile.setting_file_refs
    ]
    llm_prompt = _build_llm_prompt(profile, sources, max_chars=max_chars)
    l15_payloads = tuple(
        source.ingest_payload
        for source in sources
        if source.ingest_payload is not None and "l1_5" in source.prompt_target
    )
    return SessionContextBundle(
        room_profile_id=profile.room_profile_id,
        display_name=profile.display_name,
        model_id=profile.model_id,
        persona_id=profile.persona_id,
        line_id=profile.line_id,
        scene_profile_id=profile.scene_profile_id,
        sources=tuple(sources),
        llm_prompt_block=llm_prompt,
        l15_payloads=l15_payloads,
    )


async def bootstrap_active_session_context_to_l15(
    room_profile_id: str | None = None,
    *,
    force: bool = False,
) -> int:
    """Publish active RoomProfile setting notes through the DSG trigger path.

    Returns the count of payloads successfully fired. Returns 0 (without
    marking the dedupe set) when the TriggerRunner has no triggers registered
    yet — this avoids the race where a Room change watcher fires before
    ``_boot_l2b_and_triggers`` has wired ``ObsidianIngestTrigger`` into the
    runner. The next caller (typically the boot path) re-fires the same
    payload because the dedupe set hasn't been populated yet.
    """

    bundle = load_active_session_context_bundle(room_profile_id)
    if not bundle.l15_payloads:
        return 0

    try:
        from parrot.dsg.triggers.runner import get_trigger_runner

        runner = get_trigger_runner()
    except Exception:
        logger.exception("session_context_pack: trigger runner unavailable")
        return 0

    # Guard against firing into a runner whose triggers haven't been wired
    # yet. ``get_trigger_runner`` registers defaults eagerly, but a custom
    # ``TriggerRunner`` injected from tests may start empty; in that case the
    # event would be silently dropped and we'd still mark the dedupe key,
    # making the next legitimate call a no-op.
    triggers = getattr(runner, "_triggers", None)
    if triggers is not None and len(triggers) == 0:
        logger.info(
            "session_context_pack: trigger runner has 0 triggers, deferring "
            "L1.5 bootstrap (room=%s, payloads=%d)",
            bundle.room_profile_id, len(bundle.l15_payloads),
        )
        return 0

    count = 0
    for payload in bundle.l15_payloads:
        dedupe_key = _l15_dedupe_key(bundle.room_profile_id, payload)
        if not force and dedupe_key in _BOOTSTRAPPED_L15_KEYS:
            continue
        note_key = str(payload.get("obsidian_note_key") or payload.get("label") or "")
        event = {
            "type": "obsidian_note",
            "source": "session_context_pack",
            "provenance_stream_id": f"room:{bundle.room_profile_id}:{note_key}",
            "payload": payload,
        }
        try:
            await runner.fire_event(event)
            _BOOTSTRAPPED_L15_KEYS.add(dedupe_key)
            count += 1
        except Exception:
            logger.exception(
                "session_context_pack: failed to bootstrap %s", note_key,
            )
    return count


def reset_session_context_bootstrap_for_test() -> None:
    _BOOTSTRAPPED_L15_KEYS.clear()


def _load_room_profile(room_profile_id: str | None) -> RoomProfile:
    """Resolve the active RoomProfile.

    FIX (2026-05-11 audit, Bug A): if Unity applies an *unsaved* RoomProfile
    draft through App HTTP and then syncs Brain in-room, the on-disk
    ``data/presets/<id>.json`` may not exist yet or may be stale.
    ``preset_loader.apply_room_profile`` also writes the resolved payload to
    ``global/active_room_profile``; prefer that payload when its id matches the
    active id, so ``setting_file_refs`` / ``line_profile_id`` / ``skin_id``
    from the draft survive the round trip.
    """
    active_id = room_profile_id or _active_room_profile_id()

    bb_payload = _bb_room_profile_payload()
    if isinstance(bb_payload, dict) and str(
        bb_payload.get("room_profile_id") or ""
    ).strip() == active_id:
        try:
            return RoomProfile.from_json(bb_payload)
        except (ValueError, TypeError):
            logger.exception(
                "session_context_pack: BB room profile payload unparseable; "
                "falling back to disk for %s",
                active_id,
            )

    return get_preset_loader().load_room_profile(active_id)


def _bb_room_profile_payload() -> Any:
    try:
        from parrot.scheduler.blackboard import open_bb_client

        bb = open_bb_client(name="session_context_pack.payload", writer=None)
        return bb.get(_BB_KEY_ACTIVE_ROOM_PROFILE_PAYLOAD)
    except Exception:
        return None


def _active_room_profile_id() -> str:
    """Resolve the active RoomProfile id.

    Resolution order (mirrors ``line_profile.active_profile_id`` so RemoteSSH
    dev can override stale Blackboard state via env):

    1. ``$PARROT_ACTIVE_ROOM_PROFILE_ID`` (or ``$PARROT_ACTIVE_ROOM_PROFILE``)
       — explicit operator override; wins over a stale BB value left over
       from a previous session.
    2. ``global/active_room_profile_id`` Blackboard key — set by the menu /
       App startup RPC; this is the steady-state runtime path.
    3. ``DEFAULT_PRESET_ID`` fallback.
    """
    for env_name in (ACTIVE_ROOM_PROFILE_ENV, ACTIVE_ROOM_PROFILE_ALIAS_ENV):
        value = os.environ.get(env_name, "").strip()
        if value:
            return value

    try:
        from parrot.scheduler.blackboard import open_bb_client

        bb = open_bb_client(name="session_context_pack.room", writer=None)
        value = bb.get(_BB_KEY_ACTIVE_ROOM_PROFILE)
        if isinstance(value, str) and value.strip():
            return value.strip()
    except Exception:
        pass

    return DEFAULT_PRESET_ID


def _disabled() -> bool:
    return os.environ.get(DISABLE_SESSION_CONTEXT_ENV, "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _empty_bundle(profile: RoomProfile) -> SessionContextBundle:
    return SessionContextBundle(
        room_profile_id=profile.room_profile_id,
        display_name=profile.display_name,
        model_id=profile.model_id,
        persona_id=profile.persona_id,
        line_id=profile.line_id,
        scene_profile_id=profile.scene_profile_id,
    )


def _load_source(ref: str, *, per_source_chars: int) -> SessionContextSource:
    path = _resolve_ref(ref)
    if path is None or not path.is_file():
        return SessionContextSource(
            ref=ref,
            path=str(path or ref),
            title=Path(ref).stem,
            prompt_target="none",
            status="missing",
            reason="file_not_found",
        )

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return SessionContextSource(
            ref=ref,
            path=str(path),
            title=path.stem,
            prompt_target="none",
            status="error",
            reason=f"read_failed:{type(exc).__name__}",
        )

    meta, body = _parse_frontmatter(text)
    title = str(meta.get("title") or meta.get("display_name") or path.stem)
    raw_profile = str(meta.get("profile") or "").strip()
    profile = normalize_profile(raw_profile) if raw_profile else ""
    kind = str(meta.get("kind") or "").strip()
    # The target is intentionally inferred from frontmatter/path. This lets a
    # RoomProfile keep one simple file-ref list while the runtime separates
    # persona files, prompt context, L1.5 setting sources, and audit reports.
    prompt_target = _prompt_target(path, meta, profile)
    ingest_payload = _ingest_payload(path, prompt_target)
    l15_target = ""
    if ingest_payload is not None:
        l15_target = (
            "obsidian_setting_roleplay"
            if ingest_payload.get("profile") == "roleplay"
            else "obsidian_setting_daily"
        )

    return SessionContextSource(
        ref=ref,
        path=str(path),
        title=title,
        profile=profile,
        kind=kind,
        prompt_target=prompt_target,
        l15_target=l15_target,
        text_excerpt=_clean_excerpt(body or text, per_source_chars),
        ingest_payload=ingest_payload,
    )


def _resolve_ref(ref: str) -> Path | None:
    raw = str(ref or "").strip()
    if not raw:
        return None
    path = Path(raw)
    if path.is_absolute():
        return path
    return _repo_root() / path


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").is_file():
            return parent
    return Path.cwd()


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    raw = text[3:end].strip()
    body = text[end + 4 :].strip()
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, body


_PROMPT_TARGET_ALIASES: dict[str, str] = {
    "llm": "llm",
    "system": "llm",
    "llm_system": "llm",
    "l15": "l1_5",
    "l1.5": "l1_5",
    "l1_5": "l1_5",
    "l2b": "l1_5",
    "l2-b": "l1_5",
    "both": "llm+l1_5",
    "llm+l15": "llm+l1_5",
    "llm+l1_5": "llm+l1_5",
    "none": "none",
    "persona_loader_only": "persona_loader_only",
    "reference_only": "reference_only",
}
"""Canonical names accepted for explicit ``prompt_target`` in note frontmatter.

Anything not in this map is treated as a typo: the source is downgraded to
``reference_only`` (still listed in the bundle for debug) and a warning is
logged so the operator can see the bad value, instead of silently dropping
the source from both LLM and L1.5 routes.
"""


def _prompt_target(path: Path, meta: dict[str, str], profile: str) -> str:
    explicit = str(
        meta.get("prompt_target")
        or meta.get("session_target")
        or meta.get("injection_target")
        or ""
    ).strip().lower()
    if explicit:
        canonical = _PROMPT_TARGET_ALIASES.get(explicit)
        if canonical is None:
            # Surface the typo loudly. Returning the raw value used to make
            # the source vanish from both `"llm" in prompt_target` and
            # `"l1_5" in prompt_target` checks downstream.
            logger.warning(
                "session_context_pack: unknown prompt_target=%r in %s; "
                "treating as reference_only (accepted: %s)",
                explicit, path, sorted(_PROMPT_TARGET_ALIASES),
            )
            return "reference_only"
        return canonical

    if meta.get("persona_id") or "personas" in path.parts:
        return "persona_loader_only"
    if ".cursor" in path.parts:
        return "reference_only"
    if profile in {"roleplay", "daily"}:
        return "llm+l1_5"
    if path.suffix.lower() == ".md":
        return "llm"
    return "none"


def _ingest_payload(path: Path, prompt_target: str) -> dict[str, Any] | None:
    if "l1_5" not in prompt_target:
        return None
    try:
        return note_to_ingest_payload(path)
    except Exception:
        logger.exception("session_context_pack: failed to build ingest payload for %s", path)
        return None


def _l15_dedupe_key(room_profile_id: str, payload: dict[str, Any]) -> str:
    note_key = str(payload.get("obsidian_note_key") or payload.get("label") or "")
    file_mtime = str(payload.get("file_mtime") or "")
    return f"{room_profile_id}:{note_key}:{file_mtime}"


def _clean_excerpt(text: str, max_chars: int) -> str:
    body = str(text or "").strip()
    if len(body) <= max_chars:
        return body
    return body[: max_chars - 40].rstrip() + "\n[...truncated for session context...]"


def _build_llm_prompt(
    profile: RoomProfile,
    sources: list[SessionContextSource],
    *,
    max_chars: int,
) -> str:
    llm_sources = [
        source
        for source in sources
        if source.status == "loaded" and "llm" in source.prompt_target
    ]
    if not llm_sources:
        return ""

    parts = [
        "[ROOM SESSION CONTEXT]",
        (
            f"RoomProfile={profile.room_profile_id}; Model={profile.model_id}; "
            f"Persona={profile.persona_id}; Line={profile.line_id}; "
            f"Scene={profile.scene_profile_id}; ExperienceMode={profile.experience_mode}."
        ),
        (
            "Use these room setting sources as selected world, scene, and "
            "action-manual context. Persona rules still come from the active "
            "persona file. Do not quote source text verbatim unless the user "
            "asks for a short excerpt."
        ),
    ]

    for source in llm_sources:
        # Each source is framed as contextual material, not a new higher-priority
        # persona. This prevents a scene note from overriding model/tool safety
        # and keeps the active persona file as the primary character contract.
        header_bits = [f"title={source.title}"]
        if source.profile:
            header_bits.append(f"profile={source.profile}")
        if source.kind:
            header_bits.append(f"kind={source.kind}")
        if source.l15_target:
            header_bits.append(f"l1_5_bucket={source.l15_target}")
        parts.append(f"\n[SETTING SOURCE {'; '.join(header_bits)}]")
        parts.append(source.text_excerpt)
        parts.append("[/SETTING SOURCE]")

    parts.append("[/ROOM SESSION CONTEXT]")
    text = "\n".join(parts)
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 36].rstrip() + "\n[...session context truncated...]"


__all__ = [
    "ACTIVE_ROOM_PROFILE_ALIAS_ENV",
    "ACTIVE_ROOM_PROFILE_ENV",
    "DISABLE_SESSION_CONTEXT_ENV",
    "SessionContextBundle",
    "SessionContextSource",
    "bootstrap_active_session_context_to_l15",
    "load_active_session_context_bundle",
    "reset_session_context_bootstrap_for_test",
]
