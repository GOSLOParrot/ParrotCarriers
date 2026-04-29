"""Tests for F-05 step ③ — FocusBboxThreshold reads BB
``global/attention_thresholds`` on construct.

Authoritative spec:
    - ``architecture/sprint4_phase4_brain_self_audit_20260430.md §3.2 F-05``
    - ``architecture/sprint4_phase4_w6_w7_unity_completion_20260430.md §3.1`` +
      §8.1 (the prerequisite chain ① + ② + ③)
    - ``architecture/sprint4_phase4_entry_20260430.md §8.1 L9`` (Δ + threshold
      starter values, locked)

Coverage focus:
    1. Bare construct + valid BB → BB values override DEFAULTS
    2. Explicit kwargs always win over BB (test ergonomics path)
    3. Missing BB key → falls through to DEFAULTS
    4. Schema_version mismatch → falls through to DEFAULTS
    5. Non-dict BB value → falls through to DEFAULTS (defensive)
    6. Boolean values rejected (silent bool→float coercion guard)
    7. Partial BB (some fields missing) → only present fields override;
       missing fields keep DEFAULTS
"""

from __future__ import annotations

import pytest

from parrot.dsg.attention.threshold import (
    DEFAULT_DELTA_BBOX,
    DEFAULT_DELTA_FOCUS,
    DEFAULT_THRESHOLD,
    TARGET_TTL_SECONDS,
    FocusBboxThreshold,
    reset_attention_thresholds_for_tests,
)
from parrot.scheduler.blackboard import open_bb_client


_BB_WRITER = "test_bb_inject"
_KEY = "global/attention_thresholds"


@pytest.fixture(autouse=True)
def _isolate():
    """Hard-clear the BB key before AND after every test so each test sees
    a clean slate. The default fixture in test_attention_threshold.py
    handles the same cleanup; we duplicate here so this file is self-contained
    when run in isolation."""
    reset_attention_thresholds_for_tests()
    yield
    reset_attention_thresholds_for_tests()


def _write_bb_attention_config(payload: object) -> None:
    """Write payload to the BB key. Accepts arbitrary types so tests can
    write malformed values to verify defensive paths."""
    bb = open_bb_client(name=f"{_BB_WRITER}_writer", writer="brain._rpc_bridge")
    bb.set(_KEY, payload)


# ─── happy path: BB overrides DEFAULTS ──────────────────────────────


def test_bb_values_override_defaults_when_present_and_valid():
    _write_bb_attention_config({
        "schema_version": 1,
        "delta_focus": 0.33,
        "delta_bbox": 0.77,
        "threshold": 0.95,
        "target_ttl_s": 60.0,
    })
    th = FocusBboxThreshold()
    assert th.delta_focus == pytest.approx(0.33)
    assert th.delta_bbox == pytest.approx(0.77)
    assert th.threshold == pytest.approx(0.95)
    assert th.target_ttl_s == pytest.approx(60.0)


# ─── precedence: explicit kwargs > BB > DEFAULT ──────────────────────


def test_explicit_kwarg_overrides_bb_value():
    _write_bb_attention_config({
        "schema_version": 1,
        "delta_focus": 0.33,
        "delta_bbox": 0.77,
        "threshold": 0.95,
        "target_ttl_s": 60.0,
    })
    th = FocusBboxThreshold(delta_focus=0.5)  # only this one explicit
    assert th.delta_focus == pytest.approx(0.5)  # explicit wins
    assert th.delta_bbox == pytest.approx(0.77)  # BB
    assert th.threshold == pytest.approx(0.95)   # BB
    assert th.target_ttl_s == pytest.approx(60.0)  # BB


def test_all_explicit_kwargs_bypass_bb_completely():
    _write_bb_attention_config({
        "schema_version": 1,
        "delta_focus": 0.33,
        "delta_bbox": 0.77,
        "threshold": 0.95,
        "target_ttl_s": 60.0,
    })
    th = FocusBboxThreshold(
        delta_focus=0.1,
        delta_bbox=0.2,
        threshold=0.3,
        target_ttl_s=10.0,
    )
    assert th.delta_focus == pytest.approx(0.1)
    assert th.delta_bbox == pytest.approx(0.2)
    assert th.threshold == pytest.approx(0.3)
    assert th.target_ttl_s == pytest.approx(10.0)


# ─── fall-through paths ─────────────────────────────────────────────


def test_missing_bb_key_falls_through_to_defaults():
    # autouse fixture already cleared; explicitly verify nothing's there
    th = FocusBboxThreshold()
    assert th.delta_focus == pytest.approx(DEFAULT_DELTA_FOCUS)
    assert th.delta_bbox == pytest.approx(DEFAULT_DELTA_BBOX)
    assert th.threshold == pytest.approx(DEFAULT_THRESHOLD)
    assert th.target_ttl_s == pytest.approx(TARGET_TTL_SECONDS)


def test_wrong_schema_version_falls_through_to_defaults():
    _write_bb_attention_config({
        "schema_version": 2,  # locked at 1
        "delta_focus": 0.99,
        "delta_bbox": 0.99,
        "threshold": 0.99,
        "target_ttl_s": 99.0,
    })
    th = FocusBboxThreshold()
    assert th.delta_focus == pytest.approx(DEFAULT_DELTA_FOCUS)
    assert th.delta_bbox == pytest.approx(DEFAULT_DELTA_BBOX)


def test_missing_schema_version_falls_through():
    _write_bb_attention_config({
        # NO schema_version
        "delta_focus": 0.99,
        "delta_bbox": 0.99,
    })
    th = FocusBboxThreshold()
    assert th.delta_focus == pytest.approx(DEFAULT_DELTA_FOCUS)


def test_non_dict_bb_value_falls_through():
    _write_bb_attention_config("not_a_dict")  # type: ignore[arg-type]
    th = FocusBboxThreshold()
    assert th.delta_focus == pytest.approx(DEFAULT_DELTA_FOCUS)
    assert th.delta_bbox == pytest.approx(DEFAULT_DELTA_BBOX)


# ─── defensive: bool rejection ──────────────────────────────────────


def test_boolean_values_rejected_silently():
    """``isinstance(True, int)`` is True in Python; without the bool guard,
    ``delta_focus = True`` would coerce to 1.0 silently. Guard rejects."""
    _write_bb_attention_config({
        "schema_version": 1,
        "delta_focus": True,    # rejected
        "delta_bbox": False,    # rejected
        "threshold": 1.0,       # accepted
        "target_ttl_s": 30.0,   # accepted
    })
    th = FocusBboxThreshold()
    assert th.delta_focus == pytest.approx(DEFAULT_DELTA_FOCUS)  # fell through
    assert th.delta_bbox == pytest.approx(DEFAULT_DELTA_BBOX)    # fell through
    assert th.threshold == pytest.approx(1.0)
    assert th.target_ttl_s == pytest.approx(30.0)


# ─── partial BB ─────────────────────────────────────────────────────


def test_partial_bb_only_overrides_present_fields():
    _write_bb_attention_config({
        "schema_version": 1,
        "delta_focus": 0.5,
        # delta_bbox / threshold / target_ttl_s missing
    })
    th = FocusBboxThreshold()
    assert th.delta_focus == pytest.approx(0.5)
    assert th.delta_bbox == pytest.approx(DEFAULT_DELTA_BBOX)
    assert th.threshold == pytest.approx(DEFAULT_THRESHOLD)
    assert th.target_ttl_s == pytest.approx(TARGET_TTL_SECONDS)


# ─── int values accepted ────────────────────────────────────────────


def test_int_values_accepted_as_floats():
    """JSON over the wire may carry ``1`` instead of ``1.0`` for whole
    numbers; resolver must accept int and coerce to float."""
    _write_bb_attention_config({
        "schema_version": 1,
        "delta_focus": 1,    # int
        "delta_bbox": 2,
        "threshold": 3,
        "target_ttl_s": 45,
    })
    th = FocusBboxThreshold()
    assert th.delta_focus == pytest.approx(1.0)
    assert isinstance(th.delta_focus, float)
    assert th.delta_bbox == pytest.approx(2.0)
    assert th.target_ttl_s == pytest.approx(45.0)


# ─── reset helper smoke ─────────────────────────────────────────────


def test_reset_helper_clears_bb_back_to_defaults():
    _write_bb_attention_config({
        "schema_version": 1,
        "delta_focus": 0.99,
    })
    th_with_bb = FocusBboxThreshold()
    assert th_with_bb.delta_focus == pytest.approx(0.99)

    reset_attention_thresholds_for_tests()
    th_without_bb = FocusBboxThreshold()
    assert th_without_bb.delta_focus == pytest.approx(DEFAULT_DELTA_FOCUS)
