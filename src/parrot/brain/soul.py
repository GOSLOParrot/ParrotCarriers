"""ParrotSoul — personality and system instructions for the Brain Agent.

Backward-compat shim for ``brain/personas/<persona_id>.md`` files.

Sprint 1 + 2 shipped CORE / per-mode / SOUL_CONSTRAINTS as module-level
Python constants. NEED-P2.5-A externalised them to markdown persona files
(``architecture/Interface/menu_design_complete §3.2``). This module keeps
``get_instructions()`` / ``render_visual_constraints()`` / ``SOUL_CONSTRAINTS``
exports stable so existing call sites (Brain agent, Context Injector,
mode_watcher, ParrotAssistant) need no edits.

Resolution order on import / call:
1. ``global/active_persona_id`` Blackboard key (set by PresetLoader / menu)
2. ``$PARROT_ACTIVE_PERSONA`` env override (smoke / pytest)
3. ``DEFAULT_PERSONA_ID`` = ``goslo_parrot_default``

The default persona file mirrors the original prompt text 1:1 — running
``soul.get_instructions()`` before / after this refactor produces the same
string modulo whitespace normalisation.
"""

from __future__ import annotations

import logging
import os

from parrot.brain.persona_loader import (
    DEFAULT_PERSONA_ID,
    PersonaInstructions,
    VisualConstraints,
    get_persona_loader,
)
from parrot.shared.parrot_actions import BehaviorMode
from parrot.shared.vision_state import VisualState

logger = logging.getLogger(__name__)


_ACTIVE_PERSONA_ENV = "PARROT_ACTIVE_PERSONA"
_BB_KEY_ACTIVE_PERSONA = "global/active_persona_id"


def _resolve_active_persona_id() -> str:
    """Pick the persona id to use right now.

    Tries the Blackboard first (so menu / preset switches take effect
    immediately), then env, then default. Any error path falls back to
    the default persona — never raises.
    """
    # Blackboard read is best-effort; tests + smoke that don't run BB still work.
    try:
        from parrot.scheduler.blackboard import open_bb_client

        bb = open_bb_client(name="soul.persona_resolver", writer=None)
        try:
            value = bb.get(_BB_KEY_ACTIVE_PERSONA)
        except Exception:
            value = None
        if isinstance(value, str) and value:
            return value
    except Exception:
        pass

    env_val = os.environ.get(_ACTIVE_PERSONA_ENV, "").strip()
    if env_val:
        return env_val
    return DEFAULT_PERSONA_ID


def get_instructions(mode: BehaviorMode | None = None) -> str:
    """Return the assembled LLM system prompt for the active persona + mode.

    Behaviour-equivalent to the legacy module-level constants:
        BASE | COMPANION default; later modes append their section verbatim.

    If the active persona is missing on disk (e.g. someone deleted the file
    behind us), we fall back to ``DEFAULT_PERSONA_ID``. If that's also gone,
    we return an empty string and log loudly — the LLM will boot with no
    instructions which is at least loud, not silent.
    """
    if mode is None:
        mode = BehaviorMode.BASE | BehaviorMode.COMPANION

    loader = get_persona_loader()
    persona_id = _resolve_active_persona_id()
    instructions = loader.load(persona_id, mode=mode)
    if instructions is None and persona_id != DEFAULT_PERSONA_ID:
        logger.warning(
            "soul: persona %r not found; falling back to %r",
            persona_id, DEFAULT_PERSONA_ID,
        )
        instructions = loader.load(DEFAULT_PERSONA_ID, mode=mode)
    if instructions is None:
        logger.error(
            "soul: default persona %r also missing — returning empty instructions",
            DEFAULT_PERSONA_ID,
        )
        return ""
    return instructions.text


def get_persona_instructions(
    persona_id: str | None = None,
    mode: BehaviorMode | None = None,
) -> PersonaInstructions | None:
    """Explicit-id variant for tools that need both text + metadata + visual
    constraints in one call (Context Injector, persona watcher).
    """
    if mode is None:
        mode = BehaviorMode.BASE | BehaviorMode.COMPANION
    if persona_id is None:
        persona_id = _resolve_active_persona_id()
    return get_persona_loader().load(persona_id, mode=mode)


# Backward-compat: old call sites import PARROT_INSTRUCTIONS as a constant.
PARROT_INSTRUCTIONS = get_instructions()


# ───────────────────────── SOUL_CONSTRAINTS shim ──────────────────────
#
# The legacy table was a module-level dict[VisualState, dict[str, list[str]]].
# We rebuild the same shape on demand from the active persona's
# ``visual_state.*`` sections so existing Injector code can keep doing
# ``SOUL_CONSTRAINTS[state]["allow"]``.
#
# This is a *read-only proxy*; mutating it in-place won't propagate back to
# the persona file (legacy code never wrote to it either, so this is safe).


class _SoulConstraintsView:
    """Dict-like view over the active persona's visual_state sections."""

    def __getitem__(self, state: VisualState) -> dict[str, list[str]]:
        snap = self._snapshot()
        if state not in snap:
            raise KeyError(state)
        row = snap[state]
        return {"allow": list(row.allow), "deny": list(row.deny)}

    def get(
        self,
        state: VisualState,
        default: dict[str, list[str]] | None = None,
    ) -> dict[str, list[str]] | None:
        snap = self._snapshot()
        row = snap.get(state)
        if row is None:
            return default
        return {"allow": list(row.allow), "deny": list(row.deny)}

    def __contains__(self, state: object) -> bool:
        return state in self._snapshot()

    def __iter__(self):
        return iter(self._snapshot())

    def items(self):
        return [(s, {"allow": list(c.allow), "deny": list(c.deny)}) for s, c in self._snapshot().items()]

    @staticmethod
    def _snapshot() -> dict[VisualState, VisualConstraints]:
        instr = get_persona_instructions()
        return dict(instr.visual_constraints) if instr else {}


SOUL_CONSTRAINTS = _SoulConstraintsView()


def render_visual_constraints(state: VisualState | None) -> str | None:
    """Render the SOUL_CONSTRAINTS row for ``state`` as a compact chat-ctx hint.

    Backward-compat with Sprint 1 T8 + Sprint 2 T12. Returns ``None`` when
    there's nothing to nag about (ACTIVE / missing state / empty rows).
    """
    if state is None or not isinstance(state, VisualState):
        return None
    persona_id = _resolve_active_persona_id()
    rendered = get_persona_loader().render_visual_constraint(persona_id, state)
    if rendered is None and persona_id != DEFAULT_PERSONA_ID:
        rendered = get_persona_loader().render_visual_constraint(DEFAULT_PERSONA_ID, state)
    return rendered


__all__ = [
    "PARROT_INSTRUCTIONS",
    "SOUL_CONSTRAINTS",
    "get_instructions",
    "get_persona_instructions",
    "render_visual_constraints",
]
