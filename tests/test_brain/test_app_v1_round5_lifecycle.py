"""Round 5 regression tests — Brain cold-start + lifecycle audit.

See ``.cursor/memory/architecture/Interface/app_v1_brain_cold_start_line_lifecycle_audit_20260511.md``
§Round 5 for the bug list.

Each ``test_bug_*`` test re-creates the conditions of one Bug L/M/N/O
repro and asserts the post-fix behaviour. They are kept small,
self-contained, and free of external services so they run on CI.
"""

from __future__ import annotations

import asyncio
import socket
from typing import Any

import pytest


# ── Bug L: stop_photo_upload_server cancels a stuck task on timeout ──


def test_bug_l_stop_cancels_hung_task_after_timeout() -> None:
    """A stuck uvicorn shutdown must not survive the timeout window.

    Pre-fix: ``asyncio.shield(task)`` made ``wait_for`` impotent on
    timeout, leaving the task running and port 7889 bound on the next
    cold-start cycle.
    """
    from parrot.brain.photo_upload_server import stop_photo_upload_server

    async def _run() -> tuple[bool, bool]:
        cancel_seen = {"value": False}

        async def _hung_serve() -> None:
            try:
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                cancel_seen["value"] = True
                raise

        class _FakeServer:
            should_exit = False

        fake = _FakeServer()
        task = asyncio.create_task(_hung_serve(), name="hung_serve_test")
        setattr(fake, "_parrot_task", task)

        await stop_photo_upload_server(fake, timeout_s=0.2)
        return task.done(), cancel_seen["value"]

    done, cancelled = asyncio.run(_run())
    assert done, "task must be terminated after stop returns"
    assert cancelled, "task must observe CancelledError, not be silently abandoned"


# ── Bug M: start_photo_upload_server refuses to start on bound port ──


def test_bug_m_refuses_to_start_when_port_bound() -> None:
    """Pre-fix: uvicorn ``Server.startup`` calls ``sys.exit(1)`` on bind
    failure; the unawaited task propagated ``SystemExit`` back to the
    agent loop, killing the Brain process. Post-fix: pre-check the port
    and return None with a structured log line.

    Note the blocker socket is created **without** ``SO_REUSEADDR`` — on
    Windows that flag has "share the port" semantics that would let
    another listener bind the same port; the probe-vs-blocker test
    needs them both to model the real production case where uvicorn
    can't take the port from a stale process.
    """
    from parrot.brain.photo_upload_server import start_photo_upload_server

    blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    blocker.bind(("127.0.0.1", 0))
    bound_port = blocker.getsockname()[1]
    blocker.listen(1)
    try:
        async def _run() -> Any:
            return await start_photo_upload_server(host="127.0.0.1", port=bound_port)

        result = asyncio.run(_run())
        assert result is None, (
            "start_photo_upload_server must return None when the port "
            "is already bound; returning a Server triggers Bug M's "
            "SystemExit-from-task crash."
        )
    finally:
        blocker.close()


def test_bug_m_port_check_helper_reports_in_use() -> None:
    """Direct check of the helper used by start: returns False + reason."""
    from parrot.brain.photo_upload_server import _is_port_bindable

    blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    blocker.bind(("127.0.0.1", 0))
    bound_port = blocker.getsockname()[1]
    blocker.listen(1)
    try:
        ok, reason = _is_port_bindable("127.0.0.1", bound_port)
        assert ok is False
        assert reason  # non-empty diagnostic
    finally:
        blocker.close()


def test_bug_m_port_check_helper_succeeds_on_free_port() -> None:
    from parrot.brain.photo_upload_server import _is_port_bindable

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    free_port = sock.getsockname()[1]
    sock.close()

    ok, reason = _is_port_bindable("127.0.0.1", free_port)
    assert ok is True, reason


# ── Bug N: per-message scheduler-listener handler stays alive on err ─


def test_bug_n_per_message_handler_logs_and_continues(caplog) -> None:
    """Static contract: handler is its own coroutine and the listener
    wraps each call in try/except. We don't run a Redis loop here —
    just call the extracted handler directly to confirm an exception
    in ``json.loads`` propagates up to the caller (so the listener can
    catch + continue) instead of being silently swallowed.
    """
    from parrot.brain import agent

    async def _run() -> None:
        bad_message = {"data": b"this is not json", "type": "message"}
        with pytest.raises(Exception):
            await agent._handle_scheduler_message(session=None, message=bad_message)

    asyncio.run(_run())


def test_bug_n_listener_source_has_per_message_guard() -> None:
    """Source-level guard: assert the per-message try/except wrapper
    pattern is in place so a future refactor that flattens the loop
    can't reintroduce Bug N silently.
    """
    from pathlib import Path

    src = Path("src/parrot/brain/agent.py").read_text(encoding="utf-8")
    listener = src.split("async def _listen_scheduler_results", 1)[1].split(
        "async def ", 1
    )[0]
    assert "_handle_scheduler_message" in listener
    assert "per-message handler" in listener.lower() or "per-message" in listener.lower()
    # The outer except must NOT be the only guard — there must be an
    # inner try/except around the handler call.
    inner_try = listener.find("try:", listener.find("async for"))
    assert inner_try > 0, "missing per-message try/except in scheduler listener"


# ── Bug O: running_line_id env-first; active_line_id BB-first ────────


def test_bug_o_running_line_id_is_env_first(monkeypatch) -> None:
    import py_trees

    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    bb = py_trees.blackboard.Client(name="round5", namespace="/")
    bb.register_key("global/active_line_id", access=py_trees.common.Access.WRITE)
    bb.set("global/active_line_id", "line_b")  # selected
    monkeypatch.setenv("PARROT_LLM_PIPELINE", "line_a")  # running

    from parrot.brain.line_status import active_line_id, running_line_id

    assert running_line_id() == "line_a", (
        "running_line_id must report the env-pinned process pipeline"
    )
    assert active_line_id() == "line_b", (
        "active_line_id keeps its preferred-selection semantics"
    )


def test_bug_o_running_line_id_defaults_to_line_a(monkeypatch) -> None:
    monkeypatch.delenv("PARROT_LLM_PIPELINE", raising=False)
    from parrot.brain.line_status import running_line_id

    assert running_line_id() == "line_a"


def test_bug_o_running_line_id_rejects_unknown_env(monkeypatch) -> None:
    monkeypatch.setenv("PARROT_LLM_PIPELINE", "line_c")
    from parrot.brain.line_status import running_line_id

    assert running_line_id() == "line_a"


def test_bug_o_voice_pipeline_status_surfaces_drift(monkeypatch) -> None:
    """The GOSLO Module canvas voice tile must call out the
    selected-vs-running drift even though the tile's headline state
    keeps its selection-driven semantics for backwards compatibility.
    """
    import py_trees

    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    bb = py_trees.blackboard.Client(name="round5_voice", namespace="/")
    bb.register_key("global/active_line_id", access=py_trees.common.Access.WRITE)
    bb.set("global/active_line_id", "line_b")
    monkeypatch.setenv("PARROT_LLM_PIPELINE", "line_a")

    from parrot.brain.app_first_version import (
        AppFirstVersionFacade,
        ExternalModuleId,
    )

    facade = AppFirstVersionFacade()
    statuses = {s.module_id: s for s in facade.list_module_statuses()}
    voice = statuses.get(ExternalModuleId.VOICE_PIPELINE)
    assert voice is not None

    metrics = voice.metrics
    # The new contract: explicit running/selected fields surface the
    # cold-start truth without breaking the legacy "selected drives
    # the headline" tile semantics.
    assert metrics["running_line_id"] == "line_a"
    assert metrics["selected_line_id"] == "line_b"
    assert metrics["selection_drift"] is True
    # Drift must be visible in the user-facing summary.
    assert "drift" in voice.summary.lower()
    # And in health — a clean selection on the wrong process should at
    # least show a warning so the operator notices the cold-restart gap.
    assert voice.health in {"warning", "error"}


def test_bug_o_voice_pipeline_status_no_drift_when_aligned(monkeypatch) -> None:
    import py_trees

    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    monkeypatch.setenv("PARROT_LLM_PIPELINE", "line_a")

    from parrot.brain.app_first_version import (
        AppFirstVersionFacade,
        ExternalModuleId,
    )

    facade = AppFirstVersionFacade()
    statuses = {s.module_id: s for s in facade.list_module_statuses()}
    voice = statuses[ExternalModuleId.VOICE_PIPELINE]
    assert voice.metrics["selection_drift"] is False
    assert voice.metrics["running_line_id"] == voice.metrics["selected_line_id"]


# ── Static guards for the audit doc claims ───────────────────────────


def test_round5_photo_upload_uses_pre_bind_check_in_source() -> None:
    """Static lock: any future refactor that drops the pre-bind probe
    must trip this assertion before it lands.
    """
    from pathlib import Path

    src = Path("src/parrot/brain/photo_upload_server.py").read_text(encoding="utf-8")
    assert "_is_port_bindable" in src
    assert "_is_port_bindable(host, port)" in src
    assert "task.add_done_callback(_log_done)" in src
    # Cooperative shutdown must cancel on timeout (Bug L lock).
    assert "task.cancel()" in src
    # Round 4 already had the cooperative-stop scaffolding; ensure it's
    # still present.
    assert "should_exit = True" in src
