"""PersonaLoader — externalised LLM persona files (NEED-P2.5-A).

Loads ``brain/personas/<persona_id>.md`` files into ``PersonaInstructions``
records that compose into a single LLM system prompt at runtime.

File format (markdown with YAML frontmatter):

    ---
    persona_id: goslo_parrot_default
    display_name: GOSLO Parrot (default)
    schema_version: 1
    description: ...
    ---

    ## core
    <core instructions>

    ## mode.companion
    <Companion Mode (active) ...>

    ## mode.butler
    ...

    ## visual_state.degraded
    allow:
    - ...
    deny:
    - ...

The loader preserves the public ``get_instructions()`` and
``render_visual_constraints()`` contracts while allowing the runtime persona
text to evolve outside Python source.

Why markdown not toml:
- ``soul.py`` ships large free-form prompt text. Markdown sections are the
  smallest format that keeps the body verbatim while still being parseable.
- Adding a TOML / Pydantic schema is a P3 item — once the menu canvas chat
  defines the canonical persona schema we can attach a validator without
  re-writing files.

Single-source-of-truth for default persona:
- ``src/parrot/brain/personas/goslo_parrot_default.md`` owns the current
  runtime GOSLO persona. ``soul.py`` keeps a thin shim that delegates to the
  loader so consumers can keep importing ``get_instructions()`` /
  ``render_visual_constraints()``.

Concurrency:
- ``PersonaLoader`` is a passive cache. ``get_persona_loader()`` is a
  process-singleton. The watcher (``persona_watcher.attach_persona_watcher``)
  rebuilds the cache when ``global/active_persona_id`` changes.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping

from parrot.shared.parrot_actions import BehaviorMode
from parrot.shared.vision_state import VisualState

logger = logging.getLogger(__name__)


DEFAULT_PERSONA_ID = "goslo_parrot_default"
"""Default persona id used when ``global/active_persona_id`` is unset."""

PERSONA_DIRS_ENV = "PARROT_PERSONA_DIRS"
"""Optional ``os.pathsep``-separated list of extra persona search paths."""


# ─── Public dataclasses ──────────────────────────────────────────────


@dataclass(frozen=True)
class PersonaSummary:
    """Lightweight metadata view used by the menu API listing."""

    persona_id: str
    display_name: str
    description: str
    file_path: str
    schema_version: int = 1
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class VisualConstraints:
    """Per-VisualState allow / deny phrases for SOUL_CONSTRAINTS rendering."""

    allow: tuple[str, ...] = ()
    deny: tuple[str, ...] = ()

    def is_empty(self) -> bool:
        return not self.allow and not self.deny


@dataclass(frozen=True)
class PersonaInstructions:
    """Full assembled LLM system prompt for a (persona, mode, visual_state)
    selection.

    ``text`` is the multi-section string suitable for
    ``AgentSession.update_instructions`` / ``Agent.__init__``.
    ``visual_constraints`` is the original SOUL_CONSTRAINTS table (used by
    ``render_visual_constraints`` for chat-context hints, not the system
    prompt).
    """

    persona_id: str
    text: str
    summary: PersonaSummary
    active_mode: BehaviorMode
    visual_constraints: dict[VisualState, VisualConstraints] = field(default_factory=dict)


# ─── Internal cached schema ──────────────────────────────────────────


@dataclass
class _CachedPersona:
    summary: PersonaSummary
    core: str
    mode_sections: dict[BehaviorMode, str]
    visual_state_sections: dict[VisualState, VisualConstraints]


_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
# Only match ``## <known-section>`` headers — body text is allowed to use
# ``## ...`` freely (e.g. ``## Companion Mode (active)``) without confusing
# the splitter.
_SECTION_RE = re.compile(
    r"^##\s+(core|intro|mode\.[a-z_]+|visual_state\.[a-z_]+)\s*$",
    re.MULTILINE,
)

_MODE_NAME_TO_FLAG: Mapping[str, BehaviorMode] = {
    "companion": BehaviorMode.COMPANION,
    "butler": BehaviorMode.BUTLER,
    "researcher": BehaviorMode.RESEARCHER,
    "playful": BehaviorMode.PLAYFUL,
    "roleplay": BehaviorMode.ROLEPLAY,
    "on_hand": BehaviorMode.ON_HAND,
}
"""Section names ``mode.<name>`` → BehaviorMode flag mapping."""

_VISUAL_NAME_TO_STATE: Mapping[str, VisualState] = {
    "active": VisualState.ACTIVE,
    "degraded": VisualState.DEGRADED,
    "paused": VisualState.PAUSED,
    "blocked": VisualState.BLOCKED,
}


# ─── PersonaLoader ───────────────────────────────────────────────────


class PersonaLoader:
    """File-system backed persona registry.

    Search order for ``persona_id``:
    1. Each path in ``$PARROT_PERSONA_DIRS`` (newer paths win for overrides).
    2. ``src/parrot/brain/personas/`` (built-in defaults).

    Returns ``None`` from :meth:`load` when the persona is missing — callers
    must fall back to ``DEFAULT_PERSONA_ID`` explicitly so we never silently
    swap personas under the LLM.
    """

    def __init__(self, search_paths: Iterable[Path] | None = None) -> None:
        if search_paths is None:
            search_paths = self._default_search_paths()
        self._search_paths: list[Path] = [Path(p) for p in search_paths]
        self._cache: dict[str, _CachedPersona] = {}

    @staticmethod
    def _default_search_paths() -> list[Path]:
        # Internal personas dir always present; env override stacks on top.
        import os as _os

        builtin = Path(__file__).parent / "personas"
        out: list[Path] = []
        env_paths = _os.environ.get(PERSONA_DIRS_ENV, "").strip()
        if env_paths:
            out.extend(Path(p) for p in env_paths.split(_os.pathsep) if p)
        out.append(builtin)
        return out

    # ─── Public listing API ──────────────────────────────────────

    def list_personas(self) -> list[PersonaSummary]:
        """List every ``*.md`` persona discoverable in search paths.

        Later paths override earlier ones on duplicate ``persona_id``.
        """
        seen: dict[str, PersonaSummary] = {}
        for d in self._search_paths:
            try:
                if not d.is_dir():
                    continue
                for f in sorted(d.glob("*.md")):
                    try:
                        cached = self._load_file(f)
                        seen[cached.summary.persona_id] = cached.summary
                    except Exception:
                        logger.exception("PersonaLoader: failed to parse %s", f)
            except OSError:
                continue
        return list(seen.values())

    def load(
        self,
        persona_id: str,
        mode: BehaviorMode | None = None,
        visual_state: VisualState | None = None,
    ) -> PersonaInstructions | None:
        """Return assembled instructions for ``persona_id``.

        ``mode`` defaults to ``BASE | COMPANION`` to match legacy
        ``soul.get_instructions()`` behaviour. ``visual_state`` is currently
        not folded into the prompt body — it is exposed via
        :meth:`PersonaInstructions.visual_constraints` for chat-context hints
        (per Sprint 1 T8 + Sprint 2 T12 contract).
        """
        if mode is None:
            mode = BehaviorMode.BASE | BehaviorMode.COMPANION

        cached = self._resolve(persona_id)
        if cached is None:
            return None

        parts: list[str] = [cached.core]
        for flag, text in cached.mode_sections.items():
            if flag in mode:
                parts.append(text)

        return PersonaInstructions(
            persona_id=persona_id,
            text="\n".join(p for p in parts if p),
            summary=cached.summary,
            active_mode=mode,
            visual_constraints=dict(cached.visual_state_sections),
        )

    def render_visual_constraint(
        self,
        persona_id: str,
        state: VisualState | None,
    ) -> str | None:
        """Compact ``"视觉状态=X | 可以: ... | 不要: ..."`` string for the
        Context Injector. Returns ``None`` when there's nothing to nag about.

        Behaviourally identical to the legacy ``soul.render_visual_constraints``
        helper; just sourced from the persona file rather than the Python
        constant table.
        """
        if state is None or not isinstance(state, VisualState):
            return None
        cached = self._resolve(persona_id)
        if cached is None:
            return None
        row = cached.visual_state_sections.get(state)
        if row is None or row.is_empty():
            return None
        bits: list[str] = [f"视觉状态={state.value}"]
        if row.allow:
            bits.append("可以: " + "; ".join(row.allow))
        if row.deny:
            bits.append("不要: " + "; ".join(row.deny))
        return " | ".join(bits)

    # ─── Cache plumbing ──────────────────────────────────────────

    def invalidate(self, persona_id: str | None = None) -> None:
        """Drop cached parse results so the next ``load()`` re-reads disk."""
        if persona_id is None:
            self._cache.clear()
        else:
            self._cache.pop(persona_id, None)

    def _resolve(self, persona_id: str) -> _CachedPersona | None:
        if persona_id in self._cache:
            return self._cache[persona_id]
        path = self._find(persona_id)
        if path is None:
            return None
        try:
            cached = self._load_file(path)
        except Exception:
            logger.exception("PersonaLoader: failed to parse %s", path)
            return None
        self._cache[persona_id] = cached
        return cached

    def _find(self, persona_id: str) -> Path | None:
        # Sanitize persona_id to avoid filesystem traversal.
        safe = persona_id.strip()
        if not safe or "/" in safe or "\\" in safe or ".." in safe:
            return None
        for d in self._search_paths:
            candidate = d / f"{safe}.md"
            if candidate.is_file():
                return candidate
        return None

    @staticmethod
    def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
        m = _FRONTMATTER_RE.match(text)
        if not m:
            return {}, text
        body = text[m.end():]
        meta_block = m.group(1)
        meta: dict[str, str] = {}
        # Minimal "key: value" scanner. We deliberately avoid PyYAML to keep
        # the loader dependency-free; the persona schema is shallow enough.
        cur_key: str | None = None
        cur_lines: list[str] = []
        for raw_line in meta_block.splitlines():
            if not raw_line:
                continue
            if raw_line.startswith(" ") and cur_key is not None:
                cur_lines.append(raw_line.strip())
                continue
            if cur_key is not None:
                meta[cur_key] = "\n".join([meta[cur_key], *cur_lines]) if cur_lines else meta.get(cur_key, "")
                cur_lines = []
                cur_key = None
            if ":" in raw_line:
                k, _, v = raw_line.partition(":")
                key = k.strip()
                val = v.strip()
                if val == "|":
                    cur_key = key
                    meta[key] = ""
                else:
                    meta[key] = val
        if cur_key is not None and cur_lines:
            meta[cur_key] = "\n".join(cur_lines)
        return meta, body

    def _load_file(self, path: Path) -> _CachedPersona:
        text = path.read_text(encoding="utf-8")
        meta, body = self._parse_frontmatter(text)

        persona_id = meta.get("persona_id", path.stem)
        summary = PersonaSummary(
            persona_id=persona_id,
            display_name=meta.get("display_name", persona_id),
            description=meta.get("description", "").strip(),
            file_path=str(path),
            schema_version=int(meta.get("schema_version", 1) or 1),
        )

        # Section split on "## <name>" markers
        sections = self._split_sections(body)

        core_text = sections.pop("core", "").strip("\n")
        if not core_text:
            # Allow personas that omit ## core when ## intro / fallback exist
            core_text = sections.pop("intro", "").strip("\n")

        mode_sections: dict[BehaviorMode, str] = {}
        for name, flag in _MODE_NAME_TO_FLAG.items():
            text = sections.pop(f"mode.{name}", "").strip("\n")
            if text:
                mode_sections[flag] = text

        visual_sections: dict[VisualState, VisualConstraints] = {}
        for name, state in _VISUAL_NAME_TO_STATE.items():
            text = sections.pop(f"visual_state.{name}", "")
            visual_sections[state] = self._parse_visual_constraints(text)

        return _CachedPersona(
            summary=summary,
            core=core_text,
            mode_sections=mode_sections,
            visual_state_sections=visual_sections,
        )

    @staticmethod
    def _split_sections(body: str) -> dict[str, str]:
        sections: dict[str, str] = {}
        if not body:
            return sections
        positions = [(m.start(), m.end(), m.group(1).strip()) for m in _SECTION_RE.finditer(body)]
        if not positions:
            return sections
        for i, (_start, end, name) in enumerate(positions):
            next_start = positions[i + 1][0] if i + 1 < len(positions) else len(body)
            sections[name] = body[end:next_start].lstrip("\n")
        return sections

    @staticmethod
    def _parse_visual_constraints(raw: str) -> VisualConstraints:
        if not raw or not raw.strip():
            return VisualConstraints()
        # Body can be either a plain narrative (treated as a single allow phrase
        # — matches the legacy "ACTIVE: no constraints" empty-row contract) or
        # an "allow:" / "deny:" YAML-ish block.
        allow: list[str] = []
        deny: list[str] = []
        cur: list[str] | None = None
        for raw_line in raw.splitlines():
            line = raw_line.rstrip()
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.lower().startswith("allow:"):
                cur = allow
                rest = stripped.partition(":")[2].strip()
                if rest:
                    allow.append(rest.lstrip("- ").strip())
                continue
            if stripped.lower().startswith("deny:"):
                cur = deny
                rest = stripped.partition(":")[2].strip()
                if rest:
                    deny.append(rest.lstrip("- ").strip())
                continue
            if cur is None:
                # Narrative fallback — treat as a description, no constraints.
                continue
            if stripped.startswith("- "):
                cur.append(stripped[2:].strip())
            elif stripped.startswith("-"):
                cur.append(stripped[1:].strip())
            else:
                cur.append(stripped)
        return VisualConstraints(
            allow=tuple(s for s in allow if s),
            deny=tuple(s for s in deny if s),
        )


# ─── Singleton + test injection ──────────────────────────────────────


_loader: PersonaLoader | None = None


def get_persona_loader() -> PersonaLoader:
    """Process-wide PersonaLoader singleton."""
    global _loader
    if _loader is None:
        _loader = PersonaLoader()
    return _loader


def set_persona_loader_for_test(loader: PersonaLoader | None) -> None:
    """Replace the singleton (test fixtures + watcher reload)."""
    global _loader
    _loader = loader


__all__ = [
    "DEFAULT_PERSONA_ID",
    "PERSONA_DIRS_ENV",
    "PersonaInstructions",
    "PersonaLoader",
    "PersonaSummary",
    "VisualConstraints",
    "get_persona_loader",
    "set_persona_loader_for_test",
]
