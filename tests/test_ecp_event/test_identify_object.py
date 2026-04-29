"""Tests for `parrot.brain.tools.identify_object` Phase 4 W4-5 rewrite.

Coverage focus:
    1. action='deep_search' is REMOVED — returns banner explaining
       dispatch_task is the right path (audit §3.4 / §9.4 freeze test)
    2. L0 hit short-circuits before L1 (no Graphiti call)
    3. L0 miss → L1 hit returns "L1 matched" stage info
    4. L0 + L1 both miss → option α unknown reply with snapshot_id +
       top candidates surfaced
    5. capture failure does not block L0 / L1 — text path still runs
    6. Each segment timeout independently graceful-degrades
    7. attach_state_header wrapping (selection-C) still applied
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, patch

import pytest

# Mock LiveKit RunContext — identify_object decorator wraps with
# function_tool, so we test the underlying coroutine via _func.
from parrot.brain.tools import identify_object as id_module
from parrot.brain.tools._budget import SegmentResult


def _ctx():
    """Stub RunContext — identify_object body never reads it."""
    return None


# Helper: directly invoke the staged orchestrator (skips the
# function_tool wrapping that we test elsewhere).
_match_staged = id_module._match_staged


# ─── action='deep_search' removed ─────────────────────────────────


@pytest.mark.asyncio
async def test_deep_search_action_returns_removal_banner():
    # We bypass the function_tool wrapper by calling the inner orchestrator
    # for 'match', and exercise the deep_search branch through the public
    # tool by accessing _func.
    async def _drive_action(action: str) -> str:
        # The function_tool decorator wraps the original coroutine; access
        # via _func is internal but stable for unit tests.
        return await id_module.identify_object._func(
            _ctx(), description="anything", category="", action=action
        )

    out = await _drive_action("deep_search")
    assert "deep_search" in out
    assert "dispatch_task" in out
    assert "no longer supported" in out


# ─── L0 hit short-circuits ────────────────────────────────────────


@pytest.mark.asyncio
async def test_l0_hit_does_not_call_graphiti():
    async def fake_capture(timeout: float = 0.8):
        env = type("FakeEnv", (), {"request_id": "snap_l0hit"})()
        return env

    async def fake_l0(description: str, category: str):
        return [("uuid_blue_mug", "blue ceramic mug", 0.85)]

    async def fake_l1(description: str, category: str):
        # Should NOT be called when L0 already hit
        raise AssertionError("L1 must not run when L0 hit")

    async def fake_on_match(**kwargs):
        return None

    with (
        patch.object(id_module, "capture_current_frame", new=fake_capture),
        patch.object(id_module, "_l0_text_fast_match", new=fake_l0),
        patch.object(id_module, "_l1_graphiti_search", new=fake_l1),
        patch.object(id_module, "_on_match", new=fake_on_match),
    ):
        out = await _match_staged("blue ceramic mug", "container")

    assert "[L0] matched 'blue ceramic mug'" in out
    assert "uuid=uuid_blue_mug" in out
    assert "identified: blue ceramic mug" in out
    assert "source=L0" in out
    # L1 stage info should be absent
    assert "[L1]" not in out


# ─── L0 miss → L1 hit ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_l0_miss_then_l1_hit():
    async def fake_capture(timeout: float = 0.8):
        env = type("FakeEnv", (), {"request_id": "snap_l1hit"})()
        return env

    async def fake_l0(description: str, category: str):
        return []  # miss

    async def fake_l1(description: str, category: str):
        return [{"uuid": "uuid_g1", "fact": "object: silver laptop", "label": "silver laptop"}]

    async def fake_on_match(**kwargs):
        return None

    with (
        patch.object(id_module, "capture_current_frame", new=fake_capture),
        patch.object(id_module, "_l0_text_fast_match", new=fake_l0),
        patch.object(id_module, "_l1_graphiti_search", new=fake_l1),
        patch.object(id_module, "_on_match", new=fake_on_match),
    ):
        out = await _match_staged("silver laptop", "")

    assert "[L0] no L2-B match" in out
    assert "[L1] Graphiti found 1 candidates" in out
    assert "source=L1" in out
    assert "uuid=uuid_g1" in out


# ─── L0 + L1 both miss → option α ─────────────────────────────────


@pytest.mark.asyncio
async def test_both_miss_returns_option_alpha_unknown():
    async def fake_capture(timeout: float = 0.8):
        env = type("FakeEnv", (), {"request_id": "snap_unknown"})()
        return env

    async def fake_l0(description: str, category: str):
        return [("uuid_near", "blue cup", 0.40)]  # below threshold (0.5)

    async def fake_l1(description: str, category: str):
        return []

    async def fake_on_unmatched(**kwargs):
        return None

    with (
        patch.object(id_module, "capture_current_frame", new=fake_capture),
        patch.object(id_module, "_l0_text_fast_match", new=fake_l0),
        patch.object(id_module, "_l1_graphiti_search", new=fake_l1),
        patch.object(id_module, "_on_unmatched", new=fake_on_unmatched),
    ):
        out = await _match_staged("white mug", "")

    assert "unknown" in out
    assert "snapshot_id: snap_unknown" in out
    # Below-threshold L0 candidate surfaced as near-miss
    assert "L0 near-misses: blue cup(0.40)" in out
    # Option α decision menu is in the LLM-facing reply
    assert "dispatch_task" in out
    assert "save_new" in out


# ─── capture failure does not block ───────────────────────────────


@pytest.mark.asyncio
async def test_capture_failure_does_not_block_l0_l1():
    async def fake_capture(timeout: float = 0.8):
        return None  # capture_current_frame returns None on failure

    l0_called = False
    l1_called = False

    async def fake_l0(description: str, category: str):
        nonlocal l0_called
        l0_called = True
        return []

    async def fake_l1(description: str, category: str):
        nonlocal l1_called
        l1_called = True
        return []

    async def fake_on_unmatched(**kwargs):
        return None

    with (
        patch.object(id_module, "capture_current_frame", new=fake_capture),
        patch.object(id_module, "_l0_text_fast_match", new=fake_l0),
        patch.object(id_module, "_l1_graphiti_search", new=fake_l1),
        patch.object(id_module, "_on_unmatched", new=fake_on_unmatched),
    ):
        out = await _match_staged("anything", "")

    # capture failure tagged in stage info (None return → with_budget
    # treats as success ok=True with value=None, then orchestrator's
    # explicit None check tags it as failed).
    assert "[capture]" in out
    assert l0_called is True
    assert l1_called is True
    # Final reply still reaches option α path
    assert "unknown" in out


# ─── budget timeout is segment-local ──────────────────────────────


@pytest.mark.asyncio
async def test_l0_timeout_does_not_kill_l1():
    async def fake_capture(timeout: float = 0.8):
        return type("FakeEnv", (), {"request_id": "snap_timeout"})()

    async def slow_l0(description: str, category: str):
        await asyncio.sleep(2.0)  # well over the 0.2s budget
        return []

    async def fake_l1(description: str, category: str):
        return [{"uuid": "uuid_g_after_timeout", "fact": "object: thing", "label": "thing"}]

    async def fake_on_match(**kwargs):
        return None

    with (
        patch.object(id_module, "capture_current_frame", new=fake_capture),
        patch.object(id_module, "_l0_text_fast_match", new=slow_l0),
        patch.object(id_module, "_l1_graphiti_search", new=fake_l1),
        patch.object(id_module, "_on_match", new=fake_on_match),
    ):
        t0 = time.monotonic()
        out = await _match_staged("anything", "")
        elapsed = time.monotonic() - t0

    # L0 timed out, L1 picked up
    assert "[L0] no L2-B match" in out and "timeout" in out
    assert "[L1] Graphiti found 1 candidates" in out
    assert "source=L1" in out
    # Total time well under the 2-second slow_l0 because budget cut it
    assert elapsed < 1.5


# ─── selection-C wrapping ────────────────────────────────────────


@pytest.mark.asyncio
async def test_attach_state_header_wraps_match_action():
    """Public tool path goes through attach_state_header for selection-C
    (tool wrappers consistency, audit §B + entry doc §8.1 L10)."""
    # We don't drive Gemini; just confirm the wrapper is invoked by
    # inspecting the source — same protection style as
    # test_tools_state_header.py.
    from pathlib import Path

    src = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "parrot"
        / "brain"
        / "tools"
        / "identify_object.py"
    ).read_text(encoding="utf-8")
    assert "from parrot.brain.tools._state_context import attach_state_header" in src
    assert src.count("attach_state_header(") >= 2  # match + save_new + deep_search banner
