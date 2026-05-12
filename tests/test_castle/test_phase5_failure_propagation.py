"""Phase 5 — failure propagation hardening tests."""

from __future__ import annotations

import asyncio
import socket
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture()
def isolated_runtime(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    target = tmp_path / "runtime_config.json"
    monkeypatch.setenv("PARROT_RUNTIME_CONFIG_PATH", str(target))
    monkeypatch.delenv("PARROT_LLM_PIPELINE", raising=False)
    monkeypatch.delenv("PARROT_ACTIVE_LINE_PROFILE_ID", raising=False)
    monkeypatch.delenv("PARROT_ACTIVE_ROOM_PROFILE_ID", raising=False)
    import parrot.castle.runtime_config as rc

    monkeypatch.setattr(rc, "_bb_get", lambda key: None)
    return target


# ── 5.1 DSG trigger listener — per-message error isolation ───────────


def test_dsg_listener_survives_bad_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    """A JSONDecodeError on one message must not terminate the listener."""
    from parrot.dsg import trigger_listener as tl

    handled: list[str] = []

    async def _bad_handler(_data: str) -> None:
        handled.append("call")
        raise ValueError("simulated handler crash")

    async def _good_handler(_data: str) -> None:
        handled.append("good")

    # Replace handlers so we can count loop iterations.
    monkeypatch.setattr(tl, "_handle_trigger", _bad_handler)
    monkeypatch.setattr(tl, "_handle_scene_update", _good_handler)

    class _FakePubSub:
        def __init__(self) -> None:
            self.subscribed: tuple[str, ...] = ()

        async def subscribe(self, *channels: str) -> None:
            self.subscribed = channels

        async def unsubscribe(self, *_args: Any) -> None:
            return None

        async def close(self) -> None:
            return None

        async def listen(self):
            yield {"type": "message", "channel": "dsg.events", "data": "{}"}
            yield {"type": "message", "channel": "dsg.scene_update", "data": "ok"}
            yield {"type": "message", "channel": "dsg.events", "data": "{}"}

    class _FakeRedis:
        def pubsub(self):
            return _FakePubSub()

    async def _fake_get_redis():
        return _FakeRedis()

    monkeypatch.setattr(tl, "get_redis", _fake_get_redis)
    # Channel constants.
    monkeypatch.setattr(tl, "CH_DSG_EVENTS", "dsg.events")
    monkeypatch.setattr(tl, "CH_DSG_SCENE_UPDATE", "dsg.scene_update")

    async def _run() -> None:
        task = await tl.start_trigger_listener()
        # Let the listener consume all 3 fake messages.
        for _ in range(20):
            await asyncio.sleep(0)
            if len(handled) >= 3:
                break
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    asyncio.run(_run())

    # All 3 messages must have been handled despite handler #1 raising.
    assert handled == ["call", "good", "call"]


# ── 5.1 boot preflight ────────────────────────────────────────────────


def test_boot_preflight_runs_and_publishes(
    monkeypatch: pytest.MonkeyPatch, isolated_runtime: Path
) -> None:
    captured: dict[str, Any] = {}

    class _FakeBB:
        def set(self, key: str, value: Any) -> None:
            captured[key] = value

    monkeypatch.setattr(
        "parrot.scheduler.blackboard.open_bb_client",
        lambda **kw: _FakeBB(),
    )

    class _FakeRedis:
        async def ping(self) -> bool:
            return True

    async def _fake_get_redis():
        return _FakeRedis()

    monkeypatch.setattr(
        "parrot.shared.redis_client.get_redis",
        _fake_get_redis,
    )

    monkeypatch.setenv("PARROT_DISABLE_PHOTO_UPLOAD", "1")

    from parrot.brain.boot_preflight import run_preflight

    report = asyncio.run(run_preflight())
    assert report.overall == "ok"
    by_name = {c.name: c for c in report.checks}
    assert by_name["runtime_config"].status == "ok"
    assert by_name["redis"].status == "ok"
    assert by_name["photo_upload_port"].status == "ok"
    # BB write happened.
    assert "global/brain_boot_preflight" in captured


def test_boot_preflight_reports_redis_unreachable(
    monkeypatch: pytest.MonkeyPatch, isolated_runtime: Path
) -> None:
    monkeypatch.setattr(
        "parrot.scheduler.blackboard.open_bb_client",
        lambda **kw: type("BB", (), {"set": lambda self, k, v: None})(),
    )

    async def _bad_get_redis():
        raise OSError("connection refused")

    monkeypatch.setattr(
        "parrot.shared.redis_client.get_redis",
        _bad_get_redis,
    )

    monkeypatch.setenv("PARROT_DISABLE_PHOTO_UPLOAD", "1")

    from parrot.brain.boot_preflight import run_preflight

    report = asyncio.run(run_preflight())
    assert report.overall == "error"
    redis_check = next(c for c in report.checks if c.name == "redis")
    assert redis_check.status == "error"


def test_boot_preflight_warns_on_bound_port(
    monkeypatch: pytest.MonkeyPatch, isolated_runtime: Path
) -> None:
    monkeypatch.setattr(
        "parrot.scheduler.blackboard.open_bb_client",
        lambda **kw: type("BB", (), {"set": lambda self, k, v: None})(),
    )

    class _FakeRedis:
        async def ping(self) -> bool:
            return True

    async def _fake_get_redis():
        return _FakeRedis()

    monkeypatch.setattr(
        "parrot.shared.redis_client.get_redis",
        _fake_get_redis,
    )
    # Ensure the photo upload check actually runs.
    monkeypatch.setenv("PARROT_DISABLE_PHOTO_UPLOAD", "0")

    blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    blocker.bind(("127.0.0.1", 0))
    blocker.listen(1)
    bound_port = blocker.getsockname()[1]
    monkeypatch.setenv("PARROT_PHOTO_UPLOAD_PORT", str(bound_port))

    try:
        from parrot.brain.boot_preflight import run_preflight

        report = asyncio.run(run_preflight())
    finally:
        blocker.close()

    photo_check = next(c for c in report.checks if c.name == "photo_upload_port")
    assert photo_check.status == "warning"
    assert report.overall == "warning"


# ── 5.2 crash hook ────────────────────────────────────────────────────


def test_crash_hook_writes_bb_on_sync_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    class _FakeBB:
        def set(self, key: str, value: Any) -> None:
            captured[key] = value

    monkeypatch.setattr(
        "parrot.scheduler.blackboard.open_bb_client",
        lambda **kw: _FakeBB(),
    )

    from parrot.brain import crash_hook

    # Force re-install on the test event loop.
    crash_hook._INSTALLED = False
    crash_hook.install_crash_hook()

    try:
        raise RuntimeError("simulated unhandled crash")
    except RuntimeError:
        import sys

        exc_type, exc, tb = sys.exc_info()
        crash_hook._sync_excepthook(exc_type, exc, tb)

    payload = captured.get("global/brain_last_crash")
    assert payload is not None
    assert payload["exc_type"] == "RuntimeError"
    assert "simulated unhandled crash" in payload["message"]
    assert payload["source"] == "sync"


def test_crash_hook_writes_bb_on_async_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    class _FakeBB:
        def set(self, key: str, value: Any) -> None:
            captured[key] = value

    monkeypatch.setattr(
        "parrot.scheduler.blackboard.open_bb_client",
        lambda **kw: _FakeBB(),
    )

    from parrot.brain import crash_hook

    async def _runner() -> None:
        loop = asyncio.get_running_loop()
        crash_hook.install_for_running_loop(loop)
        exc = ValueError("async boom")
        try:
            raise exc
        except ValueError:
            import sys as _sys

            ctx = {"message": "task failed", "exception": exc}
            crash_hook._async_exception_handler(loop, ctx)
            del _sys

    asyncio.run(_runner())
    payload = captured.get("global/brain_last_crash")
    assert payload is not None
    assert payload["exc_type"] == "ValueError"
    assert payload["source"] == "async"


# ── 5.3 restart rate limiter ──────────────────────────────────────────


def test_restart_rate_limiter_blocks_after_burst(
    monkeypatch: pytest.MonkeyPatch, isolated_runtime: Path
) -> None:
    """After 5 restarts in 5min, further requests must short-circuit."""
    # Stub out systemctl so the actual restart succeeds quickly.
    import parrot.castle.orchestrator.actions as actions

    actions.reset_restart_history()
    monkeypatch.setattr(actions.shutil, "which", lambda cmd: "/usr/bin/systemctl")
    monkeypatch.setattr(
        actions.subprocess,
        "run",
        lambda *args, **kw: type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})(),
    )

    for _ in range(5):
        result = actions.restart_component(component="brain")
        assert result["status"] == "ok", result

    blocked = actions.restart_component(component="brain")
    assert blocked["status"] == "error"
    assert blocked["reason"] == "circuit_open"
    assert blocked["restart_stats"]["recent_count"] == 5


def test_restart_stats_exposed_via_status_endpoint(
    monkeypatch: pytest.MonkeyPatch, isolated_runtime: Path
) -> None:
    """``GET /status`` must include ``restart_stats`` and BB extras."""
    import parrot.castle.orchestrator.actions as actions

    actions.reset_restart_history()
    actions._record_restart("brain")

    captured_keys: set[str] = set()

    class _FakeBB:
        def get(self, key: str) -> Any:
            captured_keys.add(key)
            if key == "global/brain_last_crash":
                return {"exc_type": "RuntimeError", "message": "old crash"}
            if key == "global/brain_boot_preflight":
                return {"overall": "ok", "checks": []}
            return None

    monkeypatch.setattr(
        "parrot.scheduler.blackboard.open_bb_client",
        lambda **kw: _FakeBB(),
    )

    async def _stub_processes(_warnings):
        return []

    monkeypatch.setattr(
        "parrot.castle.orchestrator.status._processes", _stub_processes
    )
    monkeypatch.setattr(
        "parrot.castle.orchestrator.status._containers",
        lambda warnings: {"unavailable": "stubbed"},
    )

    from fastapi.testclient import TestClient

    from parrot.castle.orchestrator import build_app

    client = TestClient(build_app())
    body = client.get("/status").json()
    assert body["restart_stats"]["brain"]["recent_count"] == 1
    assert body["brain_last_crash"]["exc_type"] == "RuntimeError"
    assert body["brain_boot_preflight"]["overall"] == "ok"
    assert "global/brain_last_crash" in captured_keys
    assert "global/brain_boot_preflight" in captured_keys
