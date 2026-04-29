"""Sprint4 Phase 4 W3 — `tick/cognitive_state` BB writer.

Authoritative spec: ``architecture/sprint4_phase4_entry_20260430.md §8.1`` (L10
selection C: tools read this on execute).

Hooks the livekit-agents AgentSession ``agent_state_changed`` event and writes
the mapped :class:`parrot.shared.parrot_actions.CognitiveState` to the
Blackboard at ``tick/cognitive_state``. ``bb_schema.py`` declares this key's
writer as ``brain.agent``; this module is the operational wiring of that
declaration.

Why a separate module instead of inlining into ``brain.agent``:
    * ``brain.agent`` is a 500-line bootstrap; one more attach_X helper keeps
      reviewability symmetric with ``attach_telemetry_receiver`` /
      ``attach_video_state_rpc`` / ``attach_context_injector`` / ...
    * Tests can drive cognitive_state without spinning a full AgentSession
      (use the helper's pure-function path).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.parrot_actions import CognitiveState

if TYPE_CHECKING:
    import py_trees
    from livekit.agents.voice.events import AgentStateChangedEvent
    from livekit.agents import AgentSession


logger = logging.getLogger(__name__)


_WRITER = "brain.agent"  # Must match the declaration in bb_schema.py.


# Single mapping table — change here, change tests, change docstring.
# IDLE_MIND covers both `initializing` and `idle` because Sprint4 selection-C
# tools care about "is GOSLO busy" not "is GOSLO mid-bootstrap".
AGENT_STATE_TO_COGNITIVE: dict[str, CognitiveState] = {
    "initializing": CognitiveState.IDLE_MIND,
    "idle": CognitiveState.IDLE_MIND,
    "listening": CognitiveState.LISTENING,
    "thinking": CognitiveState.THINKING,
    "speaking": CognitiveState.SPEAKING,
}


_bb: "py_trees.blackboard.Client | None" = None


def _ensure_bb() -> "py_trees.blackboard.Client":
    global _bb
    if _bb is None:
        _bb = open_bb_client(name="cognitive_state_tracker", writer=_WRITER)
    return _bb


def map_agent_state(agent_state: str) -> CognitiveState:
    """Pure-function mapping for tests + reuse outside the session hook.

    Unknown / future agent states fall back to IDLE_MIND (conservative — we
    do not want to surface a misleading state that could make the LLM
    reason about a "thinking" GOSLO that is actually broken).
    """
    return AGENT_STATE_TO_COGNITIVE.get(agent_state, CognitiveState.IDLE_MIND)


def write_cognitive_state(new_state: CognitiveState) -> None:
    """Write a CognitiveState to BB. Skip identical-write to keep BB
    event-driven semantics clean (no spurious change events on no-op).
    """
    bb = _ensure_bb()
    try:
        current = bb.get("tick/cognitive_state")
    except KeyError:
        current = None
    if current != new_state:
        bb.set("tick/cognitive_state", new_state)
        logger.debug("BB tick/cognitive_state: %s → %s", current, new_state)


def attach_cognitive_state_tracker(session: AgentSession) -> None:
    """Subscribe to AgentSession's ``agent_state_changed`` event and mirror to BB.

    Call this once during agent boot, after the session is constructed.
    Idempotent: re-attaching adds another listener, but the duplicate writes
    are no-ops thanks to :func:`write_cognitive_state`'s identity check.
    """
    _ensure_bb()

    @session.on("agent_state_changed")
    def _on_state_changed(ev: AgentStateChangedEvent) -> None:
        new_cog = map_agent_state(str(ev.new_state))
        write_cognitive_state(new_cog)

    logger.info(
        "Cognitive state tracker attached — agent_state_changed → tick/cognitive_state"
    )


__all__ = [
    "AGENT_STATE_TO_COGNITIVE",
    "attach_cognitive_state_tracker",
    "map_agent_state",
    "write_cognitive_state",
]
