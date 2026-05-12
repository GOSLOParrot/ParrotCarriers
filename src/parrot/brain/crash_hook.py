"""Brain unhandled-exception hook (Phase 5.2).

Plan reference: §Phase 5.2 of
``app_v1_brain_cold_start_line_lifecycle_audit_20260511.md``.

When a Bug-M-style propagation kills the Brain process, the
orchestrator currently learns about it only via the heartbeat going
stale. This module installs:

* :func:`sys.excepthook` (synchronous unhandled exceptions)
* :func:`asyncio.AbstractEventLoop.set_exception_handler` (async loop
  exceptions)

Both hooks write a structured payload to BB
``global/brain_last_crash`` so the orchestrator ``GET /status``
endpoint can show the last failure cause + timestamp without an
operator having to ssh in and tail logs.

The BB write is best-effort and uses a short-lived sync Redis
connection (BB client) — calling ``open_bb_client`` from inside an
exception handler is safe because every prior fault has already
been logged.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import time
import traceback
from typing import Any

logger = logging.getLogger(__name__)


_PREVIOUS_EXCEPTHOOK: Any = None
_INSTALLED = False


def install_crash_hook() -> None:
    """Idempotently install the sync + async exception handlers."""
    global _PREVIOUS_EXCEPTHOOK, _INSTALLED
    if _INSTALLED:
        return
    _PREVIOUS_EXCEPTHOOK = sys.excepthook
    sys.excepthook = _sync_excepthook
    try:
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(_async_exception_handler)
    except RuntimeError:
        # No running loop yet — that's fine, brain_entrypoint will
        # also call this and the loop hook will attach later.
        pass
    _INSTALLED = True
    logger.info("[crash_hook] sync + async exception hooks installed")


def install_for_running_loop(loop: asyncio.AbstractEventLoop) -> None:
    """Attach the async hook to a specific loop (called from brain_entrypoint)."""
    if loop is None:
        return
    loop.set_exception_handler(_async_exception_handler)


def _sync_excepthook(exc_type, exc_value, exc_tb) -> None:
    payload = _build_payload(
        source="sync",
        exc_type=getattr(exc_type, "__name__", str(exc_type)),
        message=str(exc_value),
        traceback_text="".join(traceback.format_exception(exc_type, exc_value, exc_tb)),
    )
    _write_bb(payload)
    if _PREVIOUS_EXCEPTHOOK is not None:
        try:
            _PREVIOUS_EXCEPTHOOK(exc_type, exc_value, exc_tb)
            return
        except Exception:
            pass
    sys.__excepthook__(exc_type, exc_value, exc_tb)


def _async_exception_handler(loop: asyncio.AbstractEventLoop, context: dict[str, Any]) -> None:
    exc = context.get("exception")
    message = context.get("message", "")
    if exc is not None:
        exc_type = type(exc).__name__
        traceback_text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    else:
        exc_type = "AsyncContextWarning"
        traceback_text = ""
    payload = _build_payload(
        source="async",
        exc_type=exc_type,
        message=str(exc) if exc is not None else message,
        traceback_text=traceback_text,
    )
    _write_bb(payload)
    # Fall through to the default handler so the message still hits stderr.
    loop.default_exception_handler(context)


def _build_payload(
    *,
    source: str,
    exc_type: str,
    message: str,
    traceback_text: str,
) -> dict[str, Any]:
    return {
        "source": source,
        "exc_type": exc_type,
        "message": message[:1024],
        "traceback": traceback_text[-4096:],
        "timestamp": time.time(),
        "pid": os.getpid(),
    }


def _write_bb(payload: dict[str, Any]) -> None:
    try:
        from parrot.scheduler.blackboard import open_bb_client

        bb = open_bb_client(name="brain.crash_hook", writer="brain.agent")
        bb.set("global/brain_last_crash", payload)
    except Exception:
        # Don't compound the crash; just log and let the original
        # excepthook print the traceback.
        logger.warning("[crash_hook] BB write failed", exc_info=True)


__all__ = [
    "install_crash_hook",
    "install_for_running_loop",
]
