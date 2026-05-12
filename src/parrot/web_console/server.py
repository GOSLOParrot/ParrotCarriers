"""FastAPI BFF for the Parrot Web Console.

The Web Console keeps operator-only concerns server-side. The browser talks to
this BFF, and the BFF talks to the Castle orchestrator with the optional
``PARROT_ORCH_SECRET`` bearer token.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Awaitable, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    from fastapi import FastAPI
    from fastapi.responses import FileResponse, HTMLResponse
    from fastapi.staticfiles import StaticFiles
except ImportError:  # pragma: no cover - install gate
    FastAPI = None  # type: ignore[assignment]
    FileResponse = None  # type: ignore[assignment]
    HTMLResponse = None  # type: ignore[assignment]
    StaticFiles = None  # type: ignore[assignment]


StatusFetcher = Callable[["OrchestratorProxyConfig"], Awaitable[dict[str, Any]]]
HealthFetcher = Callable[["OrchestratorProxyConfig"], Awaitable[dict[str, Any]]]


@dataclass(frozen=True)
class OrchestratorProxyConfig:
    """Runtime config for the orchestrator status proxy."""

    base_url: str
    secret: str
    timeout_s: float

    @property
    def auth_mode(self) -> str:
        return "bearer" if self.secret else "dev-open"

    @property
    def status_url(self) -> str:
        return f"{self.base_url}/status"


def build_app(
    status_fetcher: StatusFetcher | None = None,
    health_fetcher: HealthFetcher | None = None,
):  # type: ignore[no-untyped-def]
    """Build the Web Console app."""
    if FastAPI is None:
        raise RuntimeError("fastapi not installed; install parrotcarriers[http]")

    app = FastAPI(title="Parrot Web Console", version="0.1.0")
    fetcher = status_fetcher or fetch_orchestrator_status
    health_probe = health_fetcher or fetch_orchestrator_health

    static_root = _static_root()
    assets_root = static_root / "assets"
    if assets_root.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_root)), name="web-console-assets")

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {"status": "ok", "service": "parrot.web_console", "now": time.time()}

    @app.get("/api/console/config")
    async def console_config() -> dict[str, Any]:
        config = _orchestrator_config_from_env()
        return {
            "orchestrator_base_url": config.base_url,
            "orchestrator_auth_mode": config.auth_mode,
            "refresh_interval_s": _env_float("PARROT_WEB_CONSOLE_REFRESH_S", 15.0),
            "now": time.time(),
        }

    @app.get("/api/orchestrator/status")
    async def orchestrator_status() -> dict[str, Any]:
        return await fetcher(_orchestrator_config_from_env())

    @app.get("/api/orchestrator/health")
    async def orchestrator_health() -> dict[str, Any]:
        return await health_probe(_orchestrator_config_from_env())

    @app.get("/", response_class=HTMLResponse)
    async def index():  # type: ignore[no-untyped-def]
        index_path = static_root / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return HTMLResponse(_missing_static_html(), status_code=500)

    @app.get("/{path:path}", response_class=HTMLResponse)
    async def spa_fallback(path: str):  # type: ignore[no-untyped-def]
        if path.startswith("api/") or path.startswith("assets/"):
            return HTMLResponse("Not found", status_code=404)
        index_path = static_root / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return HTMLResponse(_missing_static_html(), status_code=500)

    return app


async def fetch_orchestrator_status(config: OrchestratorProxyConfig) -> dict[str, Any]:
    """Fetch and normalize Castle ``GET /status`` for browser consumption."""
    return await asyncio.to_thread(_fetch_orchestrator_status_sync, config)


async def fetch_orchestrator_health(config: OrchestratorProxyConfig) -> dict[str, Any]:
    """Fetch Castle ``GET /health``. This route is intentionally unauthenticated."""
    return await asyncio.to_thread(_fetch_orchestrator_health_sync, config)


def _fetch_orchestrator_status_sync(config: OrchestratorProxyConfig) -> dict[str, Any]:
    headers = {"Accept": "application/json"}
    if config.secret:
        headers["Authorization"] = f"Bearer {config.secret}"
    status_code, body, detail = _fetch_json(config.status_url, headers, config.timeout_s)

    if status_code != 200:
        state = _upstream_error_state(status_code)
        detail = body if isinstance(body, dict) else detail
        if status_code == 401 and not config.secret:
            detail["message"] = (
                "Orchestrator requires Bearer auth; set PARROT_ORCH_SECRET "
                "for the Web Console process."
            )
        return _proxy_envelope(
            ok=False,
            state=state,
            config=config,
            fetched_at=time.time(),
            status_code=status_code,
            detail=detail,
        )
    if not isinstance(body, dict):
        return _proxy_envelope(
            ok=False,
            state="error",
            config=config,
            fetched_at=time.time(),
            status_code=status_code,
            detail={"detail": "Orchestrator returned non-object JSON."},
        )

    summary = _status_summary(body)
    return _proxy_envelope(
        ok=True,
        state=summary["state"],
        config=config,
        fetched_at=time.time(),
        status_code=status_code,
        status=body,
        summary=summary,
    )


def _upstream_error_state(status_code: int | None) -> str:
    if status_code == 401:
        return "unauthorized"
    if status_code is None:
        return "offline"
    return "error"


def _fetch_orchestrator_health_sync(config: OrchestratorProxyConfig) -> dict[str, Any]:
    health_url = f"{config.base_url}/health"
    status_code, body, detail = _fetch_json(
        health_url,
        {"Accept": "application/json"},
        config.timeout_s,
    )
    ok = status_code == 200 and isinstance(body, dict)
    return {
        "ok": ok,
        "state": "connected" if ok else "offline",
        "upstream": {
            "url": health_url,
            "status_code": status_code,
            "auth_mode": "open",
            "fetched_at": time.time(),
        },
        "health": body if isinstance(body, dict) else None,
        "detail": {} if ok else detail,
    }


def _fetch_json(
    url: str,
    headers: dict[str, str],
    timeout_s: float,
) -> tuple[int | None, Any, dict[str, Any]]:
    request = Request(url, headers=headers, method="GET")
    try:
        with urlopen(request, timeout=timeout_s) as response:  # noqa: S310
            return int(response.status), _decode_json_bytes(response.read()), {}
    except HTTPError as exc:
        return exc.code, _decode_json_bytes(exc.read()), {"detail": str(exc)}
    except (TimeoutError, URLError, OSError) as exc:
        return None, None, {"error": exc.__class__.__name__, "message": str(exc)}


def _proxy_envelope(
    *,
    ok: bool,
    state: str,
    config: OrchestratorProxyConfig,
    fetched_at: float,
    status_code: int | None,
    status: dict[str, Any] | None = None,
    summary: dict[str, Any] | None = None,
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "ok": ok,
        "state": state,
        "upstream": {
            "url": config.status_url,
            "status_code": status_code,
            "auth_mode": config.auth_mode,
            "fetched_at": fetched_at,
        },
        "summary": summary or {},
        "status": status,
        "detail": detail or {},
    }


def _status_summary(status: dict[str, Any]) -> dict[str, Any]:
    processes = status.get("processes")
    process_list = processes if isinstance(processes, list) else []
    online_count = sum(1 for item in process_list if isinstance(item, dict) and item.get("online"))
    offline_count = sum(1 for item in process_list if isinstance(item, dict) and not item.get("online"))
    warnings = status.get("warnings") if isinstance(status.get("warnings"), list) else []
    containers = status.get("containers")
    containers_unavailable = isinstance(containers, dict) and bool(containers.get("unavailable"))
    selection_drift = status.get("selection_drift")
    is_drift = isinstance(selection_drift, dict) and bool(selection_drift.get("is_drift"))
    crash = status.get("brain_last_crash")
    has_crash = isinstance(crash, dict) and bool(crash)
    state = "degraded" if warnings or offline_count or containers_unavailable or is_drift or has_crash else "connected"
    return {
        "state": state,
        "online_processes": online_count,
        "offline_processes": offline_count,
        "warning_count": len(warnings),
        "containers_unavailable": containers_unavailable,
        "selection_drift": is_drift,
        "has_brain_crash": has_crash,
        "host": status.get("host", ""),
        "schema_version": status.get("schema_version"),
    }


def _decode_json_bytes(raw_body: bytes) -> Any:
    try:
        return json.loads(raw_body.decode("utf-8"))
    except Exception:
        return None


def _orchestrator_config_from_env() -> OrchestratorProxyConfig:
    port = os.getenv("PARROT_ORCH_PORT", "7890").strip() or "7890"
    default_url = f"http://127.0.0.1:{port}"
    return OrchestratorProxyConfig(
        base_url=_clean_base_url(os.getenv("PARROT_WEB_CONSOLE_ORCH_URL", default_url)),
        secret=os.getenv("PARROT_ORCH_SECRET", "").strip(),
        timeout_s=_env_float("PARROT_WEB_CONSOLE_ORCH_TIMEOUT_S", 12.0),
    )


def _clean_base_url(value: str) -> str:
    cleaned = value.strip() or "http://127.0.0.1:7890"
    return cleaned[:-1] if cleaned.endswith("/") else cleaned


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def _static_root() -> Path:
    return Path(__file__).resolve().parents[3] / "web" / "console"


def _missing_static_html() -> str:
    return (
        "<!doctype html><title>Parrot Web Console</title>"
        "<body><h1>Parrot Web Console static files missing</h1>"
        "<p>Expected web/console/index.html.</p></body>"
    )
