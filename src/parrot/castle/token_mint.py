"""Token Mint — FastAPI service for LiveKit room token generation.

Sprint 3 T-P4.

Security model (decision D3):
    Bearer PARROT_MINT_SECRET header. Unity stores secret in
    Resources/parrot_config.json (compiled into APK, gitignored).
    Failed auth returns 401. Missing secret env logs a dev-mode warning and opens mint.

Deployment:
    Castle docker-compose token-mint service on port 7888. The service is
    bound for phone access; Castle security group controls public reachability.

Usage:
    POST /mint
    Authorization: Bearer <PARROT_MINT_SECRET>
    Content-Type: application/json
    {"room": "parrot-main", "identity": "unity-<device-id>"}

    200 {"token": "<livekit-jwt>", "url": "<LIVEKIT_URL>"}
    401 {"error": "unauthorized"}
    422 validation error

Unity identities request the unnamed LiveKit Agents Brain dispatch by default
(`PARROT_MINT_AGENT_DISPATCH=unity`). Listener/diagnostic identities can join
without spawning Brain; set `PARROT_MINT_AGENT_DISPATCH=off` for manual dispatch
tests or `all` for broad dev-room dispatch.

Castle can keep a room alive with scheduler/diagnostic participants. In that
case the JWT room-config dispatch may not fire because Unity is not creating a
fresh room. For Unity identities, token-mint also performs a best-effort
server-side dispatch using the LiveKit API secret, while still returning only a
normal participant token to Unity.
"""

from __future__ import annotations

import asyncio
import hmac
import logging
import os
import sys
import time
from datetime import timedelta
from typing import Any

_LOGGER_NAME = "parrot.castle.token_mint"


def _configure_logging() -> None:
    """Keep application logs visible and stable when launched via `python -m`."""
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
    from fastapi import FastAPI, HTTPException, Request
    from pydantic import BaseModel, Field
except ImportError as e:
    raise ImportError(
        "token_mint requires FastAPI and pydantic: pip install fastapi uvicorn"
    ) from e

app = FastAPI(title="Parrot Token Mint", version="1.0.0")

_MINT_SECRET = os.getenv("PARROT_MINT_SECRET", "")
_LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
# ``LIVEKIT_URL`` is the URL returned to Unity, so laptop/phone tests often
# need it to be a LAN address such as ``ws://192.168.x.y:17880``. Containers
# cannot reliably call that host-facing address for LiveKit server APIs, so the
# mint service accepts a separate internal URL for active Brain dispatch.
_LIVEKIT_INTERNAL_URL = os.getenv(
    "PARROT_MINT_LIVEKIT_INTERNAL_URL",
    os.getenv("LIVEKIT_INTERNAL_URL", _LIVEKIT_URL),
)
_LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
_LIVEKIT_API_SECRET = os.getenv(
    "LIVEKIT_API_SECRET",
    "parrot_carriers_local_dev_livekit_secret_key_v1",
)
_DEFAULT_ROOM = os.getenv("LIVEKIT_ROOM", "parrot-main")

# Keep join tokens short-lived. LiveKit token expiry gates the initial
# connection, while connected clients receive refresh tokens for reconnects.
# For self-hosting this also reduces stale-token replay risk because Cloud-only
# token revocation is not available.
_TOKEN_TTL_S = int(os.getenv("PARROT_MINT_TTL_SECONDS", "600"))
# Phone START needs more than a LiveKit room join: Brain must also be present in
# that room before Unity can call business RPCs such as applyRoomProfile. Unity
# must never hold the LiveKit API secret, so the mint service is the narrow
# security boundary that can request the server-side agent dispatch inside the
# short-lived join token. Default "unity" keeps this phone-facing only; observer
# and diagnostics clients can join without spawning Brain.
_AGENT_DISPATCH_MODE = os.getenv("PARROT_MINT_AGENT_DISPATCH", "unity").strip().lower()
_ACTIVE_AGENT_DISPATCH_MODE = os.getenv(
    "PARROT_MINT_ACTIVE_AGENT_DISPATCH",
    "1",
).strip().lower()
_ACTIVE_AGENT_DISPATCH_TIMEOUT_S = float(
    os.getenv("PARROT_MINT_ACTIVE_AGENT_DISPATCH_TIMEOUT_SECONDS", "4.0")
)

# Empty means the Brain worker registered via the default unnamed
# @server.rtc_session() entrypoint. Set only if the deployment later registers a
# named worker and the LiveKit Agents server is configured to accept that name.
_AGENT_NAME = os.getenv("PARROT_MINT_AGENT_NAME", "").strip()


@app.on_event("startup")
async def _log_startup_config() -> None:
    logger.info(
        "Token mint starting: port=%s livekit_url_scheme=%s livekit_url_length=%d "
        "internal_livekit_url_scheme=%s internal_livekit_url_length=%d "
        "api_key_present=%s api_secret_length=%d mint_secret_present=%s default_room=%s "
        "agent_dispatch_mode=%s active_agent_dispatch=%s active_agent_dispatch_timeout_s=%.1f "
        "agent_name_configured=%s",
        os.getenv("PARROT_MINT_PORT", "7888"),
        _LIVEKIT_URL.split(":", 1)[0] if ":" in _LIVEKIT_URL else "",
        len(_LIVEKIT_URL),
        _LIVEKIT_INTERNAL_URL.split(":", 1)[0] if ":" in _LIVEKIT_INTERNAL_URL else "",
        len(_LIVEKIT_INTERNAL_URL),
        bool(_LIVEKIT_API_KEY),
        len(_LIVEKIT_API_SECRET),
        bool(_MINT_SECRET),
        _DEFAULT_ROOM,
        _AGENT_DISPATCH_MODE or "unity",
        _ACTIVE_AGENT_DISPATCH_MODE or "1",
        _ACTIVE_AGENT_DISPATCH_TIMEOUT_S,
        bool(_AGENT_NAME),
    )


class MintRequest(BaseModel):
    room: str = Field(default=_DEFAULT_ROOM, min_length=1, max_length=80)
    identity: str = Field(..., min_length=1, max_length=80)


class MintResponse(BaseModel):
    token: str
    url: str
    expires_at: int
    # Exposed for diagnostics/HUDs. This is not a secret and does not prove the
    # Brain job stayed alive; Unity must still wait for participant presence and
    # successful RPC payloads before marking START complete.
    agent_dispatch_requested: bool = False
    # Token roomConfig dispatch is enough when Unity creates the room. Castle also
    # keeps a scheduler participant in the room, so token-mint performs a
    # best-effort server-side dispatch for Unity identities to avoid a phone START
    # that joins LiveKit successfully but never gets a Brain participant.
    agent_dispatch_active_attempted: bool = False
    agent_dispatch_active_created: bool = False
    agent_dispatch_active_already_present: bool = False
    agent_dispatch_active_error: str = ""


def _check_auth(request: Request) -> None:
    if not _MINT_SECRET:
        logger.warning("PARROT_MINT_SECRET not set — token mint is open (dev mode)")
        return
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        logger.warning(
            "Mint auth failed: missing Bearer prefix (header_present=%s header_length=%d)",
            bool(auth),
            len(auth),
        )
        raise HTTPException(status_code=401, detail="unauthorized")
    token = auth[len("Bearer "):]
    if not hmac.compare_digest(token, _MINT_SECRET):
        logger.warning(
            "Mint auth failed: bearer mismatch (bearer_length=%d expected_length=%d)",
            len(token),
            len(_MINT_SECRET),
        )
        raise HTTPException(status_code=401, detail="unauthorized")


def _should_request_agent_dispatch(identity: str) -> bool:
    """Return whether this token should start the unnamed Brain room job.

    Unity does not hold the LiveKit API secret, so the token mint is the only
    safe place in the phone-facing path to request the server-side Brain agent.
    The default is intentionally narrow: only Unity identities dispatch Brain.
    Diagnostic/listener clients can still join without spawning a new job.
    """
    mode = (_AGENT_DISPATCH_MODE or "unity").strip().lower()
    if mode in {"0", "false", "no", "off", "disabled", "none"}:
        return False
    if mode in {"1", "true", "yes", "on", "all", "always"}:
        return True
    return identity.strip().lower().startswith("unity")


def _active_agent_dispatch_enabled() -> bool:
    mode = (_ACTIVE_AGENT_DISPATCH_MODE or "1").strip().lower()
    return mode not in {"0", "false", "no", "off", "disabled", "none"}


def _is_brain_identity(identity: str) -> bool:
    identity = (identity or "").strip().lower()
    return identity == "brain" or identity.startswith("agent-")


def _livekit_http_url() -> str:
    return _LIVEKIT_INTERNAL_URL.replace("ws://", "http://").replace(
        "wss://", "https://"
    )


async def _ensure_agent_dispatch(room: str) -> dict[str, Any]:
    """Best-effort server-side Brain dispatch for Unity phone START.

    The JWT RoomConfiguration agent dispatch only fires reliably when the
    connecting Unity participant creates the room. Castle can keep the LiveKit
    room alive with scheduler/diagnostic participants, so the mint service also
    uses the server API secret to dispatch Brain when no Brain participant is
    already present. Unity still receives only a normal participant token.
    """
    from livekit.api import (  # type: ignore
        CreateAgentDispatchRequest,
        ListParticipantsRequest,
        LiveKitAPI,
    )
    from livekit.protocol import agent_dispatch as agent_dispatch_pb  # type: ignore

    result: dict[str, Any] = {
        "attempted": True,
        "created": False,
        "already_present": False,
        "error": "",
    }
    lk = LiveKitAPI(_livekit_http_url(), _LIVEKIT_API_KEY, _LIVEKIT_API_SECRET)
    try:
        try:
            participants_response = await lk.room.list_participants(
                ListParticipantsRequest(room=room)
            )
            participants = getattr(participants_response, "participants", []) or []
            for participant in participants:
                identity = getattr(participant, "identity", "")
                if _is_brain_identity(identity):
                    result["already_present"] = True
                    logger.info(
                        "Brain already present during mint dispatch check: room=%s identity=%s",
                        room,
                        identity,
                    )
                    return result
        except Exception as exc:
            # If the room does not exist yet, token RoomConfiguration remains the
            # normal room-create path. Continue with create_dispatch as a
            # best-effort nudge for existing-room cases and keep mint non-fatal.
            logger.info(
                "Could not list LiveKit room participants before active dispatch: "
                "room=%s exception_type=%s",
                room,
                type(exc).__name__,
            )

        try:
            dispatches = await lk.agent_dispatch.list_dispatch(room)
            for dispatch in dispatches:
                agent_name = getattr(dispatch, "agent_name", "")
                if agent_name == _AGENT_NAME:
                    result["already_present"] = True
                    logger.info(
                        "Brain dispatch already present during mint dispatch check: "
                        "room=%s dispatch_id=%s agent_name=%s",
                        room,
                        getattr(dispatch, "id", ""),
                        agent_name,
                    )
                    return result
        except Exception as exc:
            logger.info(
                "Could not list LiveKit agent dispatches before active dispatch: "
                "room=%s exception_type=%s",
                room,
                type(exc).__name__,
            )

        dispatch_request = CreateAgentDispatchRequest(room=room)
        if _AGENT_NAME:
            dispatch_request.agent_name = _AGENT_NAME
        # Phone START calls mint repeatedly across retries/reconnects. Do not let
        # LiveKit restart a failed stale room job into a second Brain while Unity
        # is already creating the next clean dispatch.
        dispatch_request.restart_policy = agent_dispatch_pb.JobRestartPolicy.JRP_NEVER
        dispatch = await lk.agent_dispatch.create_dispatch(dispatch_request)
        result["created"] = True
        logger.info(
            "Active Brain dispatch requested by token mint: room=%s dispatch_id=%s",
            room,
            getattr(dispatch, "id", ""),
        )
        return result
    finally:
        await lk.aclose()


def _generate_token(
    room: str,
    identity: str,
    *,
    include_agent_dispatch: bool | None = None,
) -> str:
    """Generate a LiveKit JWT using livekit-server-sdk-python."""
    try:
        from livekit.api import AccessToken, RoomAgentDispatch, VideoGrants
        from livekit.protocol.room import RoomConfiguration
    except ImportError:
        try:
            from livekit.api import RoomAgentDispatch  # type: ignore
            from livekit.api.access_token import AccessToken, VideoGrants  # type: ignore
            from livekit.protocol.room import RoomConfiguration  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "livekit-server-sdk-python required: pip install livekit-api"
            ) from exc

    # NOTE: with_ttl() requires a timedelta, not a plain int.
    # Historical note: this was verified in the generate_token.py fix on 2026-04-11.
    # Grant only the normal participant powers Unity needs. Do not mint room
    # admin/list/create/record grants from the mobile app token endpoint.
    builder = (
        AccessToken(api_key=_LIVEKIT_API_KEY, api_secret=_LIVEKIT_API_SECRET)
        .with_identity(identity)
        .with_name(identity)
        .with_grants(
            VideoGrants(
                room_join=True,
                room=room,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
            )
        )
        .with_ttl(timedelta(seconds=_TOKEN_TTL_S))
    )
    if include_agent_dispatch is None:
        include_agent_dispatch = _should_request_agent_dispatch(identity)
    if include_agent_dispatch:
        # RoomConfiguration.agents asks LiveKit to dispatch the server-side
        # Brain room job as part of the room join. This does not grant Unity any
        # admin privilege and does not change media grants. If ECS Brain is
        # misconfigured, the phone can still join the room, but START must fail
        # later at the Brain-present/RPC gate instead of reporting fake success.
        dispatch = (
            RoomAgentDispatch(agent_name=_AGENT_NAME)
            if _AGENT_NAME
            else RoomAgentDispatch()
        )
        builder = builder.with_room_config(RoomConfiguration(agents=[dispatch]))
    return builder.to_jwt()


@app.post("/mint", response_model=MintResponse)
async def mint_token(req: MintRequest, request: Request) -> MintResponse:
    """Generate a LiveKit room token.

    Requires Authorization: Bearer <PARROT_MINT_SECRET>.
    """
    logger.info(
        "Mint request received: room=%s identity_length=%d authorization_header_present=%s",
        req.room,
        len(req.identity),
        bool(request.headers.get("Authorization", "")),
    )
    _check_auth(request)
    agent_dispatch_requested = _should_request_agent_dispatch(req.identity)
    active_dispatch_enabled = _active_agent_dispatch_enabled()
    # Use exactly one Brain-dispatch path. The phone-facing default is active
    # server-side dispatch, because it also works when a room already exists.
    # Only fall back to token RoomConfiguration dispatch when active dispatch is
    # explicitly disabled for a diagnostic or older direct-token flow.
    include_token_agent_dispatch = agent_dispatch_requested and not active_dispatch_enabled
    try:
        jwt = _generate_token(
            req.room,
            req.identity,
            include_agent_dispatch=include_token_agent_dispatch,
        )
    except Exception as exc:
        logger.exception("Token generation failed: exception_type=%s", type(exc).__name__)
        raise HTTPException(status_code=500, detail="token generation failed") from exc

    active_dispatch_result: dict[str, Any] = {
        "attempted": False,
        "created": False,
        "already_present": False,
        "error": "",
    }
    if agent_dispatch_requested and active_dispatch_enabled:
        active_dispatch_result["attempted"] = True
        try:
            active_dispatch_result = await asyncio.wait_for(
                _ensure_agent_dispatch(req.room),
                timeout=max(0.1, _ACTIVE_AGENT_DISPATCH_TIMEOUT_S),
            )
        except TimeoutError:
            active_dispatch_result["error"] = "timeout"
            logger.warning(
                "Active Brain dispatch timed out: room=%s timeout_s=%.1f",
                req.room,
                _ACTIVE_AGENT_DISPATCH_TIMEOUT_S,
            )
        except Exception as exc:
            active_dispatch_result["error"] = type(exc).__name__
            logger.exception(
                "Active Brain dispatch failed: room=%s exception_type=%s",
                req.room,
                type(exc).__name__,
            )

    expires_at = int(time.time()) + _TOKEN_TTL_S
    logger.info(
        "Minted token: room=%s identity_length=%d ttl_s=%d expires_at=%d "
        "agent_dispatch_requested=%s active_dispatch_attempted=%s "
        "active_dispatch_created=%s active_dispatch_already_present=%s "
        "active_dispatch_error=%s",
        req.room,
        len(req.identity),
        _TOKEN_TTL_S,
        expires_at,
        agent_dispatch_requested,
        bool(active_dispatch_result.get("attempted")),
        bool(active_dispatch_result.get("created")),
        bool(active_dispatch_result.get("already_present")),
        active_dispatch_result.get("error", ""),
    )
    return MintResponse(
        token=jwt,
        url=_LIVEKIT_URL,
        expires_at=expires_at,
        agent_dispatch_requested=agent_dispatch_requested,
        agent_dispatch_active_attempted=bool(active_dispatch_result.get("attempted")),
        agent_dispatch_active_created=bool(active_dispatch_result.get("created")),
        agent_dispatch_active_already_present=bool(
            active_dispatch_result.get("already_present")
        ),
        agent_dispatch_active_error=str(active_dispatch_result.get("error", "")),
    )


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "token-mint"}


if __name__ == "__main__":
    import uvicorn  # type: ignore

    port = int(os.getenv("PARROT_MINT_PORT", "7888"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
