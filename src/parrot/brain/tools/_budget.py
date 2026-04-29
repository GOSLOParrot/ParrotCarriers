"""Per-segment async timeout helper for staged tool flows.

Authoritative spec: ``architecture/sprint4_phase4_entry_20260430.md §8.1`` (L11)
+ ``audit_identify_object_no_screenshot_20260420.md §9.6`` (Phase 4 W4-5
budget revision).

Why this helper instead of inlining ``asyncio.wait_for`` everywhere:
    Multi-stage tools (identify_object L0 / L1 / L2) need each stage to
    either return a result OR cleanly degrade with stage info that the
    LLM-facing return text can show. Bare ``asyncio.wait_for`` raises
    ``TimeoutError`` which forces try/except clutter at every call site.
    :class:`SegmentResult` makes the success / timeout / error distinction
    a normal data type that flows naturally through the orchestrator.

Not a hard scheduling system — there is no global wall-clock budget
enforcement here. Each segment owns its own timeout; the caller decides
how to react. This matches the felt-experience contract from
``parrot_behavior_rules.md §0.3``: a segment timeout is information for
the LLM (so it can voice "I tried but couldn't see clearly"), not a
hidden cancellation that produces a contradictory tool result.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Generic, TypeVar


logger = logging.getLogger(__name__)


T = TypeVar("T")


@dataclass(frozen=True)
class SegmentResult(Generic[T]):
    """Outcome of one segment in a staged tool flow.

    Fields:
        ok          — True iff the coroutine returned without timing out
                      and without raising
        value       — coroutine return value when ok=True; None otherwise
        error       — short tag for failure mode: "timeout" / "error" /
                      "" (success). Used to compose the LLM-facing stage
                      info string.
        elapsed_ms  — actual wall-clock spent (helpful for logs and the
                      stage info; never decoupled from the segment_name)
        segment     — segment name for traceability
    """

    ok: bool
    value: T | None
    error: str
    elapsed_ms: int
    segment: str


async def with_budget(
    coro: Awaitable[T],
    *,
    timeout_s: float,
    segment: str,
) -> SegmentResult[T]:
    """Run ``coro`` with a hard timeout. Always returns a SegmentResult.

    On timeout the awaited coroutine is cancelled (``asyncio.wait_for``
    semantics). If the coroutine raises any other exception, the exception
    is logged and packaged into ``SegmentResult(ok=False, error="error")``
    rather than re-raised — staged orchestrators want to continue to the
    next segment, not unwind the whole tool call on a single segment glitch.
    """
    start = time.monotonic()
    try:
        value = await asyncio.wait_for(coro, timeout=timeout_s)
    except asyncio.TimeoutError:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        logger.info(
            "with_budget: segment=%s timed out after %dms (limit=%.0fms)",
            segment, elapsed_ms, timeout_s * 1000,
        )
        return SegmentResult(
            ok=False,
            value=None,
            error="timeout",
            elapsed_ms=elapsed_ms,
            segment=segment,
        )
    except Exception as exc:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        logger.exception(
            "with_budget: segment=%s raised %s: %s",
            segment, type(exc).__name__, exc,
        )
        return SegmentResult(
            ok=False,
            value=None,
            error=f"error:{type(exc).__name__}",
            elapsed_ms=elapsed_ms,
            segment=segment,
        )

    elapsed_ms = int((time.monotonic() - start) * 1000)
    return SegmentResult(
        ok=True,
        value=value,
        error="",
        elapsed_ms=elapsed_ms,
        segment=segment,
    )


__all__ = ["SegmentResult", "with_budget"]
