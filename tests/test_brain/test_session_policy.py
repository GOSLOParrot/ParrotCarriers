from __future__ import annotations

import py_trees

from parrot.brain.session_policy import (
    apply_capability_mode,
    first_greeting_sent,
    is_goslo_placed,
    set_first_greeting_sent,
    set_goslo_placed,
    should_generate_reply,
    should_stage_context_notice,
)
from parrot.shared.tiers import AppCapabilityMode


def setup_function() -> None:
    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}


def test_generate_reply_is_blocked_before_goslo_placement() -> None:
    apply_capability_mode(AppCapabilityMode.FULL_AR_COMPANION)
    set_goslo_placed(False, source="unit_test")

    assert should_generate_reply("scheduler_result") is False
    assert should_generate_reply("context_injector.C4") is False
    assert should_stage_context_notice("vision.evidence_awareness") is True
    assert should_generate_reply("onGosloPlaced") is True

    set_goslo_placed(True, source="unit_test")

    assert is_goslo_placed() is True
    assert should_generate_reply("scheduler_result") is True


def test_silent_mode_still_blocks_placement_greeting() -> None:
    apply_capability_mode(AppCapabilityMode.SESSION_ONLY_SILENT)
    set_goslo_placed(True, source="unit_test")

    assert should_generate_reply("onGosloPlaced") is False
    assert should_stage_context_notice("vision.evidence_awareness") is False


def test_first_greeting_flag_round_trips_through_blackboard() -> None:
    assert first_greeting_sent() is False

    set_first_greeting_sent(True, source="unit_test")

    assert first_greeting_sent() is True
