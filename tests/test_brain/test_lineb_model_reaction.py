from __future__ import annotations

import json

import py_trees
import pytest

from parrot.brain.lineb_model_reaction import (
    capability_for_voice_activity,
    dispatch_lineb_voice_activity_to_model,
    voice_activity_parameters_json,
)
from parrot.brain.model_manifest_registry import set_model_manifest_registry_for_test
from parrot.scheduler.blackboard import open_bb_client


@pytest.fixture(autouse=True)
def _reset_state():
    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    set_model_manifest_registry_for_test(None)
    yield
    set_model_manifest_registry_for_test(None)


def test_lineb_voice_activity_maps_to_model_capabilities() -> None:
    assert capability_for_voice_activity({"state": "speaking"}) == "lineb_speaking"
    assert capability_for_voice_activity({"state": "listening"}) == "lineb_listening"
    assert (
        capability_for_voice_activity({"state": "agent_echo_suppressed"})
        == "lineb_echo_suppressed"
    )
    assert (
        capability_for_voice_activity({"state": "listening_uncertain"})
        == "lineb_listening_uncertain"
    )
    assert capability_for_voice_activity({"state": "listening_noise"}) == "lineb_listening_noise"
    assert capability_for_voice_activity({"state": "idle"}) == ""


def test_lineb_voice_activity_parameters_are_unity_json_friendly() -> None:
    raw = {
        "state": "speaking",
        "source": "tts_segment",
        "segment_id": "tts_1",
        "model_reaction_policy": "suppress_touch_and_cheek_reactions",
        "recommended_model_trigger": "lineb_speaking",
        "suppression_duration_s": 2.5,
    }

    payload = json.loads(voice_activity_parameters_json(raw))

    assert payload["state"] == "speaking"
    assert payload["segment_id"] == "tts_1"
    assert payload["suppression_duration_s"] == 2.5
    assert payload["recommended_model_trigger"] == "lineb_speaking"


def test_lineb_voice_activity_parameters_tolerate_malformed_numbers() -> None:
    raw = {
        "state": "speaking",
        "echo_score": "nan",
        "suppression_duration_s": "inf",
    }

    payload = json.loads(voice_activity_parameters_json(raw))

    assert payload["echo_score"] == 0.0
    assert payload["suppression_duration_s"] == 1.2


@pytest.mark.asyncio
async def test_lineb_voice_activity_dispatch_skips_when_model_lacks_capability() -> None:
    bb = open_bb_client(name="test.lineb.reaction.seed", writer="brain.preset_loader")
    bb.set("global/active_model_id", "GOSLO_default")

    result = await dispatch_lineb_voice_activity_to_model({"state": "speaking"})

    assert result.ok is False
    assert result.reason == "capability_not_declared_by_model"
    assert result.capability_id == "lineb_speaking"
    assert result.model_id == "GOSLO_default"
