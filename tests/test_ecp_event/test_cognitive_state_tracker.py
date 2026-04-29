"""Tests for `parrot.brain.cognitive_state_tracker` (Phase 4 W3 selection-C 写者).

Coverage focus:
    1. map_agent_state covers all 5 livekit-agents AgentState literals
    2. Unknown agent_state falls back to IDLE_MIND (conservative)
    3. write_cognitive_state writes to BB and skips identical-write
    4. attach_cognitive_state_tracker hooks the session event correctly
"""

from __future__ import annotations

from unittest.mock import MagicMock

from parrot.brain.cognitive_state_tracker import (
    AGENT_STATE_TO_COGNITIVE,
    attach_cognitive_state_tracker,
    map_agent_state,
    write_cognitive_state,
)
from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.parrot_actions import CognitiveState


# ─── pure mapping ────────────────────────────────────────────────


def test_all_five_agent_states_mapped():
    """livekit-agents AgentState literal: initializing / idle / listening /
    thinking / speaking. All 5 must map deterministically."""
    expected = {
        "initializing": CognitiveState.IDLE_MIND,
        "idle": CognitiveState.IDLE_MIND,
        "listening": CognitiveState.LISTENING,
        "thinking": CognitiveState.THINKING,
        "speaking": CognitiveState.SPEAKING,
    }
    assert AGENT_STATE_TO_COGNITIVE == expected


def test_unknown_agent_state_falls_back_to_idle_mind():
    """Conservative fallback — never surface a misleading 'thinking' state
    for a future SDK enum we don't recognize yet."""
    assert map_agent_state("future_unknown_state") == CognitiveState.IDLE_MIND
    assert map_agent_state("") == CognitiveState.IDLE_MIND


def test_each_agent_state_value_round_trips():
    for agent_state, expected in AGENT_STATE_TO_COGNITIVE.items():
        assert map_agent_state(agent_state) == expected


# ─── write_cognitive_state BB integration ──────────────────────


def test_write_cognitive_state_actually_writes_to_bb():
    write_cognitive_state(CognitiveState.SPEAKING)
    bb = open_bb_client(name="test_reader_cog", writer="test")
    assert bb.get("tick/cognitive_state") == CognitiveState.SPEAKING


def test_write_cognitive_state_transitions_visible():
    write_cognitive_state(CognitiveState.LISTENING)
    write_cognitive_state(CognitiveState.THINKING)
    bb = open_bb_client(name="test_reader_cog2", writer="test")
    assert bb.get("tick/cognitive_state") == CognitiveState.THINKING


# ─── attach hook ────────────────────────────────────────────────


def test_attach_subscribes_to_agent_state_changed():
    """Verify the session.on('agent_state_changed', ...) listener is
    registered. We can't drive the actual event easily without a real
    AgentSession, so we assert the hook registration."""
    session = MagicMock()

    # session.on is a decorator factory — capture what we register
    registrations: dict[str, list] = {}

    def fake_on(event_name: str):
        def decorator(fn):
            registrations.setdefault(event_name, []).append(fn)
            return fn
        return decorator

    session.on = fake_on

    attach_cognitive_state_tracker(session)

    assert "agent_state_changed" in registrations
    assert len(registrations["agent_state_changed"]) == 1


def test_attach_listener_writes_cognitive_state_on_event():
    """Drive the registered listener with a fake event and verify BB write."""
    session = MagicMock()
    captured: dict = {}

    def fake_on(event_name: str):
        def decorator(fn):
            captured[event_name] = fn
            return fn
        return decorator

    session.on = fake_on
    attach_cognitive_state_tracker(session)

    fake_event = MagicMock()
    fake_event.new_state = "thinking"

    captured["agent_state_changed"](fake_event)

    bb = open_bb_client(name="test_reader_cog3", writer="test")
    assert bb.get("tick/cognitive_state") == CognitiveState.THINKING
