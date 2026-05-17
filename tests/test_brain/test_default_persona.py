from __future__ import annotations

import py_trees

from parrot.brain.persona_loader import set_persona_loader_for_test
from parrot.brain.soul import get_instructions


def test_default_goslo_persona_estate_contract(monkeypatch):
    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    set_persona_loader_for_test(None)
    monkeypatch.delenv("PARROT_ACTIVE_PERSONA", raising=False)

    instructions = get_instructions()

    assert "parrot young lady of the shared mansion" in instructions
    assert "mansion owners" in instructions
    assert "trusted friend" in instructions
    assert "Nanobot is the mansion maid" in instructions
    assert "never imitate" in instructions
    assert "maid tone" in instructions
    assert "Do not greet just because LiveKit connected" in instructions
    assert "Reflex layer" in instructions
    assert "Intent layer" in instructions
    assert "Work layer" in instructions
    assert "Minecraft-style" not in instructions
