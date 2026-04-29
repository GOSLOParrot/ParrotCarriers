"""Tests for `parrot.brain.tools._budget` (Phase 4 W4-5 staged budget).

Coverage focus:
    1. Success path returns ok=True + value + elapsed_ms tracked
    2. Timeout returns ok=False, error="timeout", value=None — no exception
    3. Inner exception caught and packaged as error="error:..."
    4. SegmentResult always includes the segment name passed in
"""

from __future__ import annotations

import asyncio

import pytest

from parrot.brain.tools._budget import SegmentResult, with_budget


# ─── success ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_success_returns_value_and_elapsed():
    async def fast_coro():
        return 42

    seg = await with_budget(fast_coro(), timeout_s=0.1, segment="test_fast")
    assert seg.ok is True
    assert seg.value == 42
    assert seg.error == ""
    assert seg.segment == "test_fast"
    assert seg.elapsed_ms >= 0
    assert seg.elapsed_ms < 100  # well under budget


# ─── timeout ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_timeout_returns_ok_false_with_timeout_tag():
    async def slow_coro():
        await asyncio.sleep(0.5)
        return "never_seen"

    seg = await with_budget(slow_coro(), timeout_s=0.05, segment="test_slow")
    assert seg.ok is False
    assert seg.value is None
    assert seg.error == "timeout"
    assert seg.segment == "test_slow"
    # Elapsed should be roughly the budget, not the full coroutine duration
    assert seg.elapsed_ms < 200


# ─── inner exception ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_inner_exception_caught_and_packaged():
    async def raising_coro():
        raise ValueError("boom")

    seg = await with_budget(raising_coro(), timeout_s=0.1, segment="test_raise")
    assert seg.ok is False
    assert seg.value is None
    assert seg.error.startswith("error:")
    assert "ValueError" in seg.error
    assert seg.segment == "test_raise"


# ─── SegmentResult shape ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_segment_result_immutable_dataclass():
    seg = await with_budget(_quick(), timeout_s=0.1, segment="frozen_check")
    assert isinstance(seg, SegmentResult)
    # frozen=True dataclass — assigning a field should raise FrozenInstanceError.
    with pytest.raises(Exception):
        seg.ok = False  # type: ignore[misc]


async def _quick() -> int:
    return 1
