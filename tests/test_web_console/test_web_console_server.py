from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from parrot.web_console.server import OrchestratorProxyConfig, _status_summary, build_app


def test_console_config_uses_env_without_leaking_secret(monkeypatch) -> None:
    monkeypatch.setenv("PARROT_WEB_CONSOLE_ORCH_URL", "http://127.0.0.1:9876/")
    monkeypatch.setenv("PARROT_ORCH_SECRET", "secret-value")
    monkeypatch.setenv("PARROT_WEB_CONSOLE_REFRESH_S", "9")

    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    body = client.get("/api/console/config").json()

    assert body["orchestrator_base_url"] == "http://127.0.0.1:9876"
    assert body["orchestrator_auth_mode"] == "bearer"
    assert body["refresh_interval_s"] == 9.0
    assert "secret-value" not in str(body)


def test_orchestrator_status_proxy_calls_fetcher(monkeypatch) -> None:
    monkeypatch.setenv("PARROT_ORCH_PORT", "8123")
    monkeypatch.delenv("PARROT_WEB_CONSOLE_ORCH_URL", raising=False)
    monkeypatch.delenv("PARROT_ORCH_SECRET", raising=False)

    async def fetcher(config: OrchestratorProxyConfig) -> dict[str, Any]:
        assert config.base_url == "http://127.0.0.1:8123"
        assert config.auth_mode == "dev-open"
        return {
            "ok": True,
            "state": "connected",
            "upstream": {
                "url": config.status_url,
                "status_code": 200,
                "auth_mode": config.auth_mode,
                "fetched_at": 1.0,
            },
            "summary": {"online_processes": 1, "offline_processes": 0},
            "status": {"schema_version": 1, "processes": []},
            "detail": {},
        }

    client = TestClient(build_app(status_fetcher=fetcher))
    body = client.get("/api/orchestrator/status").json()

    assert body["ok"] is True
    assert body["upstream"]["url"] == "http://127.0.0.1:8123/status"


def test_index_serves_static_console() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    response = client.get("/")

    assert response.status_code == 200
    assert "Parrot Web Console" in response.text
    assert "/assets/app.js" in response.text


def test_status_summary_marks_degraded_for_offline_process() -> None:
    summary = _status_summary(
        {
            "schema_version": 1,
            "host": "host-a",
            "processes": [
                {"module_id": "brain", "online": True},
                {"module_id": "nanobot-worker", "online": False},
            ],
            "warnings": [],
            "selection_drift": {"is_drift": False},
            "containers": [],
        }
    )

    assert summary["state"] == "degraded"
    assert summary["online_processes"] == 1
    assert summary["offline_processes"] == 1


async def _fake_fetcher(config: OrchestratorProxyConfig) -> dict[str, Any]:
    return {
        "ok": False,
        "state": "offline",
        "upstream": {
            "url": config.status_url,
            "status_code": None,
            "auth_mode": config.auth_mode,
            "fetched_at": 1.0,
        },
        "summary": {},
        "status": None,
        "detail": {"message": "fake"},
    }
