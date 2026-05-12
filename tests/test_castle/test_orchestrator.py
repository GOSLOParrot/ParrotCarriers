"""Phase 2 ECS Orchestrator FastAPI tests.

Plan reference: §Phase 2 of
``app_v1_brain_cold_start_line_lifecycle_audit_20260511.md``.

Coverage:

* ``GET /health`` is open and ``GET /status`` is gated by
  ``PARROT_ORCH_SECRET``.
* ``POST /set_active_line`` writes the file via
  ``actions.set_active_line`` and reflects the result back.
* ``POST /restart_component`` rejects unknown components and surfaces
  ``systemctl_unavailable`` cleanly when systemctl is absent.
* :class:`OrchestratorClient` round-trips through the FastAPI test
  client (using its httpx-based transport) and surfaces errors.
* Tier matrix: writing line_id is Tier 1; restart is Tier 2.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def isolated_runtime(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    target = tmp_path / "runtime_config.json"
    monkeypatch.setenv("PARROT_RUNTIME_CONFIG_PATH", str(target))
    monkeypatch.delenv("PARROT_LLM_PIPELINE", raising=False)
    monkeypatch.delenv("PARROT_ACTIVE_LINE_PROFILE_ID", raising=False)
    monkeypatch.delenv("PARROT_ACTIVE_ROOM_PROFILE_ID", raising=False)
    monkeypatch.delenv("PARROT_ORCH_SECRET", raising=False)
    import parrot.castle.runtime_config as rc

    monkeypatch.setattr(rc, "_bb_get", lambda key: None)
    return target


@pytest.fixture()
def app_client(isolated_runtime: Path):
    from parrot.castle.orchestrator import build_app

    return TestClient(build_app())


def test_health_open(app_client: TestClient) -> None:
    r = app_client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["service"] == "parrot.castle.orchestrator"


def _stub_status_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _stub_processes(warnings):
        return []

    monkeypatch.setattr(
        "parrot.castle.orchestrator.status._processes", _stub_processes
    )
    monkeypatch.setattr(
        "parrot.castle.orchestrator.status._containers",
        lambda warnings: {"unavailable": "stubbed"},
    )


def test_status_open_in_dev_mode(
    monkeypatch: pytest.MonkeyPatch,
    isolated_runtime: Path,
) -> None:
    """Without PARROT_ORCH_SECRET, /status is reachable (dev mode)."""
    _stub_status_helpers(monkeypatch)

    from parrot.castle.orchestrator import build_app

    client = TestClient(build_app())
    r = client.get("/status")
    assert r.status_code == 200
    body = r.json()
    assert body["schema_version"] == 1
    assert "runtime_config" in body
    assert body["selection_drift"]["is_drift"] is False


def test_status_requires_bearer_when_secret_set(
    monkeypatch: pytest.MonkeyPatch,
    isolated_runtime: Path,
) -> None:
    monkeypatch.setenv("PARROT_ORCH_SECRET", "s3cret")
    _stub_status_helpers(monkeypatch)

    from parrot.castle.orchestrator import build_app

    client = TestClient(build_app())
    assert client.get("/status").status_code == 401
    assert (
        client.get(
            "/status", headers={"Authorization": "Bearer wrong"}
        ).status_code
        == 401
    )
    ok = client.get("/status", headers={"Authorization": "Bearer s3cret"})
    assert ok.status_code == 200


def test_set_active_line_writes_file(
    isolated_runtime: Path, app_client: TestClient
) -> None:
    r = app_client.post(
        "/set_active_line",
        json={"line_id": "line_b", "line_profile_id": "lineb_google_default"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "ok"
    assert body["tier"] == 1
    assert body["runtime_config"]["line_id"] == "line_b"
    assert body["runtime_config"]["source"]["line_id"] == "file"
    assert isolated_runtime.is_file()
    written = json.loads(isolated_runtime.read_text(encoding="utf-8"))
    assert written["line_id"] == "line_b"


def test_set_active_line_rejects_invalid(
    isolated_runtime: Path, app_client: TestClient
) -> None:
    r = app_client.post("/set_active_line", json={"line_id": "line_z"})
    assert r.status_code == 400
    detail = r.json()["detail"]
    assert detail["status"] == "error"
    assert detail["reason"] == "invalid_argument"


def test_apply_room_profile_writes_triple(
    isolated_runtime: Path, app_client: TestClient
) -> None:
    r = app_client.post(
        "/apply_room_profile",
        json={
            "room_profile_id": "ner_lineb_room",
            "line_id": "line_b",
            "line_profile_id": "lineb_ner_ja_test",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["runtime_config"]["room_profile_id"] == "ner_lineb_room"
    assert body["runtime_config"]["line_id"] == "line_b"


def test_clear_runtime_config(
    isolated_runtime: Path, app_client: TestClient
) -> None:
    app_client.post("/set_active_line", json={"line_id": "line_b"})
    assert isolated_runtime.is_file()
    r = app_client.post("/clear_runtime_config")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["removed"] is True
    assert not isolated_runtime.is_file()


def test_restart_component_rejects_unknown(
    isolated_runtime: Path, app_client: TestClient
) -> None:
    r = app_client.post(
        "/restart_component",
        json={"component": "definitely_not_a_module", "wait_for_online": False},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "error"
    assert body["reason"] == "unknown_component"


def test_restart_component_handles_missing_systemctl(
    monkeypatch: pytest.MonkeyPatch,
    isolated_runtime: Path,
    app_client: TestClient,
) -> None:
    """On Windows / non-systemd hosts, systemctl is unavailable."""
    monkeypatch.setattr(
        "parrot.castle.orchestrator.actions.shutil.which",
        lambda cmd: None,
    )
    r = app_client.post(
        "/restart_component",
        json={"component": "brain", "wait_for_online": False},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "error"
    assert body["reason"] == "systemctl_unavailable"


def test_force_unity_reconnect_writes_marker(
    monkeypatch: pytest.MonkeyPatch,
    isolated_runtime: Path,
    app_client: TestClient,
) -> None:
    captured: dict[str, Any] = {}

    class _FakeBB:
        def set(self, key: str, value: Any) -> None:
            captured[key] = value

    monkeypatch.setattr(
        "parrot.scheduler.blackboard.open_bb_client",
        lambda **kw: _FakeBB(),
    )
    r = app_client.post(
        "/force_unity_reconnect",
        json={"reason": "tier1_test", "request_id": "req-1"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert captured["orchestrator/reconnect_request"]["reason"] == "tier1_test"
    assert captured["orchestrator/reconnect_request"]["request_id"] == "req-1"


def test_set_active_line_force_reconnect_combines(
    monkeypatch: pytest.MonkeyPatch,
    isolated_runtime: Path,
    app_client: TestClient,
) -> None:
    captured: dict[str, Any] = {}

    class _FakeBB:
        def set(self, key: str, value: Any) -> None:
            captured[key] = value

    monkeypatch.setattr(
        "parrot.scheduler.blackboard.open_bb_client",
        lambda **kw: _FakeBB(),
    )
    r = app_client.post(
        "/set_active_line",
        json={"line_id": "line_b", "force_reconnect": True},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "ok"
    assert "reconnect" in body
    assert body["reconnect"]["status"] == "ok"


def test_client_sdk_round_trip(
    monkeypatch: pytest.MonkeyPatch,
    isolated_runtime: Path,
) -> None:
    """OrchestratorClient should work against the in-process app via httpx.

    We patch ``httpx.Client`` so requests are routed to FastAPI's
    TestClient ASGI layer instead of a real socket.
    """
    from parrot.castle.orchestrator import build_app
    from parrot.castle.orchestrator.client import OrchestratorClient

    test_client = TestClient(build_app())

    class _PatchedHttpxClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def request(self, method, url, *, headers=None, json=None):
            path = url.split("://", 1)[-1].split("/", 1)[-1]
            if not path.startswith("/"):
                path = "/" + path
            response = test_client.request(method, path, headers=headers, json=json)

            class _Resp:
                status_code = response.status_code
                text = response.text

            return _Resp()

    import httpx  # type: ignore

    monkeypatch.setattr(httpx, "Client", _PatchedHttpxClient)

    sdk = OrchestratorClient(base_url="http://localhost:7890")
    health = sdk.health()
    assert health["status"] == "ok"

    written = sdk.set_active_line("line_b")
    assert written["runtime_config"]["line_id"] == "line_b"
