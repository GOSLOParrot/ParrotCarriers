"""Castle ECS Orchestrator FastAPI server.

Default port: 7890 (override via ``PARROT_ORCH_PORT``).
Auth: optional Bearer token via ``PARROT_ORCH_SECRET`` env. When unset
the server logs a dev-mode warning and accepts requests; this matches
the ``token_mint`` policy used elsewhere in this repo (see
``parrot.castle.token_mint``).

Routes:

* ``GET  /health``                 — liveness probe (no auth)
* ``GET  /status``                 — full ECS snapshot
* ``POST /set_active_line``        — Tier 1 line switch
* ``POST /apply_room_profile``     — Tier 1 RoomProfile flip
* ``POST /force_unity_reconnect``  — Tier 1 reconnect marker
* ``POST /restart_component``      — Tier 2 systemctl restart
* ``POST /clear_runtime_config``   — drop runtime_config.json

Use :func:`build_app` for tests; ``python -m parrot.castle.orchestrator``
runs the uvicorn server.
"""

from __future__ import annotations

import hmac
import logging
import os
import sys
import time
from typing import Any

from parrot.castle.orchestrator import actions, status

_LOGGER_NAME = "parrot.castle.orchestrator"


def _configure_logging() -> None:
    level_name = os.getenv("PARROT_LOG_LEVEL", os.getenv("LOG_LEVEL", "INFO")).upper()
    level = getattr(logging, level_name, logging.INFO)
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
            stream=sys.stdout,
        )
    logging.getLogger(_LOGGER_NAME).setLevel(level)


_configure_logging()
logger = logging.getLogger(_LOGGER_NAME)

try:
    from fastapi import Body, FastAPI, HTTPException, Request
    from pydantic import BaseModel, Field
except ImportError as e:  # pragma: no cover - install gate
    raise ImportError(
        "orchestrator requires FastAPI and pydantic: pip install fastapi uvicorn"
    ) from e


def _require_auth(request: Request) -> None:
    secret = os.getenv("PARROT_ORCH_SECRET", "").strip()
    if not secret:
        logger.warning(
            "PARROT_ORCH_SECRET not set — orchestrator is open (dev mode)"
        )
        return
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        logger.warning("orchestrator auth failed: missing Bearer prefix")
        raise HTTPException(status_code=401, detail="unauthorized")
    token = auth[len("Bearer "):]
    if not hmac.compare_digest(token, secret):
        logger.warning("orchestrator auth failed: bearer mismatch")
        raise HTTPException(status_code=401, detail="unauthorized")


class SetActiveLineRequest(BaseModel):
    line_id: str = Field(..., min_length=1, max_length=32)
    line_profile_id: str | None = Field(default=None, max_length=128)
    notes: str = Field(default="", max_length=256)
    force_reconnect: bool = Field(default=False)


class ApplyRoomProfileRequest(BaseModel):
    room_profile_id: str = Field(..., min_length=1, max_length=128)
    line_id: str | None = Field(default=None, max_length=32)
    line_profile_id: str | None = Field(default=None, max_length=128)
    force_reconnect: bool = Field(default=False)


class RestartComponentRequest(BaseModel):
    component: str = Field(..., min_length=1, max_length=32)
    reason: str = Field(default="orchestrator_restart", max_length=128)
    wait_for_online: bool = Field(default=True)
    timeout_s: float = Field(default=30.0, ge=1.0, le=300.0)


class ForceReconnectRequest(BaseModel):
    reason: str = Field(default="orchestrator_tier1", max_length=128)
    request_id: str | None = Field(default=None, max_length=64)


class RollingRestartRequest(BaseModel):
    reason: str = Field(default="rolling_tier1", max_length=128)
    drain_timeout_s: float = Field(default=45.0, ge=5.0, le=300.0)


def build_app() -> FastAPI:
    """Construct the FastAPI instance.

    Kept separate from a module-level ``app`` so tests can build a
    fresh instance per test (and so this import doesn't run uvicorn
    when imported elsewhere).
    """
    app = FastAPI(
        title="Parrot Castle Orchestrator",
        version="1.0.0",
        description=(
            "Phase 2 ECS Orchestrator — Tier-routed setting changes, "
            "process restart, and ECS status aggregation. See plan: "
            "app_v1_brain_cold_start_line_lifecycle_audit_20260511.md."
        ),
    )

    @app.get("/health")
    async def _health() -> dict[str, Any]:
        return {"status": "ok", "service": "parrot.castle.orchestrator", "now": time.time()}

    @app.get("/status")
    async def _status(request: Request) -> dict[str, Any]:
        _require_auth(request)
        return await status.gather_status()

    @app.post("/set_active_line")
    async def _set_active_line(
        request: Request,
        body: SetActiveLineRequest,
    ) -> dict[str, Any]:
        _require_auth(request)
        result = actions.set_active_line(
            line_id=body.line_id,
            line_profile_id=body.line_profile_id,
            notes=body.notes,
            updated_by="orchestrator.http.set_active_line",
        )
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result)
        if body.force_reconnect:
            reconnect = await actions.force_unity_reconnect(
                reason="set_active_line"
            )
            result["reconnect"] = reconnect
        return result

    @app.post("/apply_room_profile")
    async def _apply_room_profile(
        request: Request,
        body: ApplyRoomProfileRequest,
    ) -> dict[str, Any]:
        _require_auth(request)
        result = actions.apply_room_profile_id(
            room_profile_id=body.room_profile_id,
            line_id=body.line_id,
            line_profile_id=body.line_profile_id,
            updated_by="orchestrator.http.apply_room_profile",
        )
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result)
        if body.force_reconnect:
            reconnect = await actions.force_unity_reconnect(
                reason="apply_room_profile"
            )
            result["reconnect"] = reconnect
        return result

    @app.post("/force_unity_reconnect")
    async def _force_unity_reconnect(
        request: Request,
        body: ForceReconnectRequest = Body(default_factory=ForceReconnectRequest),
    ) -> dict[str, Any]:
        _require_auth(request)
        return await actions.force_unity_reconnect(
            reason=body.reason,
            request_id=body.request_id,
        )

    @app.post("/restart_component")
    async def _restart_component(
        request: Request,
        body: RestartComponentRequest,
    ) -> dict[str, Any]:
        _require_auth(request)
        restart = actions.restart_component(
            component=body.component,
            reason=body.reason,
        )
        if restart["status"] == "error":
            # systemctl misconfig is operator-visible, not an HTTP-level
            # error. Return 200 with structured detail so the client
            # can render it next to the status snapshot.
            return restart
        if body.wait_for_online:
            heartbeat = await actions.wait_for_heartbeat(
                body.component, timeout_s=body.timeout_s
            )
            restart["heartbeat"] = heartbeat
        return restart

    @app.post("/clear_runtime_config")
    async def _clear_runtime_config(request: Request) -> dict[str, Any]:
        _require_auth(request)
        return actions.clear_runtime_config_action()

    @app.post("/rolling_restart_brain")
    async def _rolling_restart_brain(
        request: Request,
        body: RollingRestartRequest = Body(default_factory=RollingRestartRequest),
    ) -> dict[str, Any]:
        _require_auth(request)
        return await actions.rolling_restart_brain(
            reason=body.reason,
            drain_timeout_s=body.drain_timeout_s,
        )

    return app


def main() -> None:
    """Entry point for ``python -m parrot.castle.orchestrator``."""
    import uvicorn

    host = os.getenv("PARROT_ORCH_HOST", "127.0.0.1")
    port = int(os.getenv("PARROT_ORCH_PORT", "7890"))
    uvicorn.run(build_app(), host=host, port=port, log_level="info")


__all__ = [
    "ApplyRoomProfileRequest",
    "ForceReconnectRequest",
    "RestartComponentRequest",
    "RollingRestartRequest",
    "SetActiveLineRequest",
    "build_app",
    "main",
]
