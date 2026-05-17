"""Tests for `parrot.brain.tools._state_context` (Phase 4 W3 selection-C 读者).

Coverage focus:
    1. Default-state snapshot → empty header (no leading "[GOSLO state]")
    2. Each non-default field surfaces individually
    3. ecp_state dict surfaces active_locks + active_command_id
    4. attach_state_header concatenation behaviour
    5. Unknown enum values still serialise (defensive — Unity may emit
       a future state before backend updates)
"""

from __future__ import annotations

from parrot.brain.cognitive_state_tracker import write_cognitive_state
from parrot.brain.tools._state_context import (
    attach_state_header,
    format_state_header,
    get_state_snapshot,
)
from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.parrot_actions import CognitiveState, ParrotBodyState


def _bb_writer_for(name: str, writer: str):
    """Open a BB client we can write through to set up test state."""
    return open_bb_client(name=name, writer=writer)


def _reset_state_to_defaults():
    """Best-effort reset of the BB keys this helper reads. We can't truly
    delete keys via py-trees Client, so we set them to declared defaults."""
    body_bb = _bb_writer_for("test_reset_body", "brain.telemetry_receiver")
    body_bb.set("tick/body_state", ParrotBodyState.IDLE)
    cog_bb = _bb_writer_for("test_reset_cog", "brain.agent")
    cog_bb.set("tick/cognitive_state", CognitiveState.IDLE_MIND)
    # head_state has no producer in W1-2; skip resetting to keep the "key
    # may not exist" path covered by test_get_snapshot_handles_missing_keys


# ─── snapshot ────────────────────────────────────────────────────


def test_get_snapshot_returns_four_keys():
    snap = get_state_snapshot()
    assert set(snap.keys()) == {
        "body_state",
        "head_state",
        "cognitive_state",
        "ecp_state",
    }


def test_get_snapshot_handles_missing_keys():
    """head_state returns None when not set; ecp_state is None before the
    first EcpState packet arrives (or after test teardown clears it).

    Note: GAP-1 added ecp_state_ingest as the real producer of
    session/ecp_state.  This test covers the _safe_get None-return path
    for a key that has not yet been written in this test's process context
    (test_ecp_state_ingest fixtures clean up after themselves by setting
    session/ecp_state = None, restoring the "no packet received" observable).
    """
    snap = get_state_snapshot()
    # head_state has no producer in Phase 4 W1-2 stage; should be None
    assert snap["head_state"] is None
    # ecp_state: None when no EcpState packet has been received (or after
    # test teardown reset). GAP-1 ecp_state_ingest fixture clears this.
    assert snap["ecp_state"] is None


# ─── header format — empty case ─────────────────────────────────


def test_default_state_returns_empty_header():
    """When all fields are at default (or missing), header is empty so
    callers can no-op concat without a stray newline."""
    _reset_state_to_defaults()
    assert format_state_header() == ""


def test_attach_state_header_is_noop_when_default():
    _reset_state_to_defaults()
    rpc_response = '{"status":"completed","reason":"applied"}'
    assert attach_state_header(rpc_response) == rpc_response


# ─── header format — interesting fields ────────────────────────


def test_dancing_body_state_appears_in_header():
    body_bb = _bb_writer_for("test_w_body", "brain.telemetry_receiver")
    body_bb.set("tick/body_state", ParrotBodyState.DANCING)

    header = format_state_header()

    assert header.startswith("[GOSLO state] ")
    assert "body=dancing" in header


def test_thinking_cognitive_state_appears_in_header():
    _reset_state_to_defaults()
    write_cognitive_state(CognitiveState.THINKING)

    header = format_state_header()

    assert "cognitive=THINKING" in header


def test_multiple_fields_combine_in_header():
    body_bb = _bb_writer_for("test_w_body2", "brain.telemetry_receiver")
    body_bb.set("tick/body_state", ParrotBodyState.FLYING)
    write_cognitive_state(CognitiveState.SPEAKING)

    header = format_state_header()

    assert "body=flying" in header
    assert "cognitive=SPEAKING" in header


def test_on_hand_body_state_surfaces_situational_mode():
    body_bb = _bb_writer_for("test_w_body_on_hand", "brain.telemetry_receiver")
    body_bb.set("tick/body_state", ParrotBodyState.PERCHED_ON_HAND)

    header = format_state_header()

    assert "body=perched_on_hand" in header
    assert "mode=ON_HAND" in header


def test_ecp_state_body_fallback_surfaces_on_hand_when_tick_default():
    snap = {
        "body_state": ParrotBodyState.IDLE,
        "head_state": None,
        "cognitive_state": CognitiveState.IDLE_MIND,
        "ecp_state": {
            "body_state": "perched_on_hand",
            "head_state": "HEAD_TILT",
            "active_locks": [],
            "active_command_id": "",
        },
    }

    header = format_state_header(snap)

    assert "body=perched_on_hand" in header
    assert "mode=ON_HAND" in header
    assert "head=HEAD_TILT" in header


def test_active_locks_and_active_cmd_from_ecp_state():
    """ecp_state dict surfaces active_locks comma-joined + active_command_id."""
    snap = {
        "body_state": ParrotBodyState.IDLE,
        "head_state": None,
        "cognitive_state": CognitiveState.IDLE_MIND,
        "ecp_state": {
            "active_locks": ["body", "vision"],
            "active_command_id": "cmd_abc12345",
        },
    }
    header = format_state_header(snap)
    assert "locks=body,vision" in header
    assert "active_cmd=cmd_abc12345" in header


def test_ecp_state_with_empty_locks_and_cmd_omits_fields():
    snap = {
        "body_state": ParrotBodyState.IDLE,
        "head_state": None,
        "cognitive_state": CognitiveState.IDLE_MIND,
        "ecp_state": {"active_locks": [], "active_command_id": ""},
    }
    assert format_state_header(snap) == ""


# ─── attach_state_header concat ────────────────────────────────


def test_attach_state_header_prepends_with_newline():
    body_bb = _bb_writer_for("test_w_body3", "brain.telemetry_receiver")
    body_bb.set("tick/body_state", ParrotBodyState.DANCING)
    rpc_response = '{"status":"completed"}'

    out = attach_state_header(rpc_response)

    assert out.startswith("[GOSLO state] body=dancing")
    assert out.endswith(rpc_response)
    assert "\n" in out  # single newline separator


# ─── defensive ───────────────────────────────────────────────────


def test_unknown_body_state_string_still_surfaces():
    """If telemetry receiver writes a future enum value as raw string, we
    still surface it (better than silent drop — the LLM can pick up that
    something unusual is happening)."""
    body_bb = _bb_writer_for("test_w_body4", "brain.telemetry_receiver")
    # Bypass the enum and write a raw string (defensive path)
    body_bb.set("tick/body_state", "future_state_unknown_to_backend")

    header = format_state_header()

    assert "body=future_state_unknown_to_backend" in header
