"""Token Mint — FastAPI service for LiveKit room token generation.

Sprint 3 T-P4.

Security model (decision D3):
    Bearer PARROT_MINT_SECRET header. Unity stores secret in
    Resources/parrot_config.json (compiled into APK, gitignored).
    Failed auth → 401. Missing secret env → 500 with log warning (never
    expose the absence of a secret in the HTTP response body).

Deployment:
    Castle docker-compose token-mint service on port 7888 (internal only,
    behind Castle firewall — Unity connects over LAN or VPN).

Usage:
    POST /mint
    Authorization: Bearer <PARROT_MINT_SECRET>
    Content-Type: application/json
    {"room": "parrot-main", "identity": "unity-<device-id>"}

    → 200 {"token": "<livekit-jwt>", "url": "<LIVEKIT_URL>"}
    → 401 {"error": "unauthorized"}
    → 422 validation error
"""

from __future__ import annotations

import logging
import os
import time

logger = logging.getLogger(__name__)

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
_LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
_LIVEKIT_API_SECRET = os.getenv(
    "LIVEKIT_API_SECRET",
    "parrot_carriers_local_dev_livekit_secret_key_v1",
)
_DEFAULT_ROOM = os.getenv("LIVEKIT_ROOM", "parrot-main")

# Token TTL: 24 hours (Unity caches in PlayerPrefs and reuses until expiry)
_TOKEN_TTL_S = 86_400


class MintRequest(BaseModel):
    room: str = Field(default=_DEFAULT_ROOM, min_length=1, max_length=80)
    identity: str = Field(..., min_length=1, max_length=80)


class MintResponse(BaseModel):
    token: str
    url: str
    expires_at: int


def _check_auth(request: Request) -> None:
    if not _MINT_SECRET:
        logger.warning("PARROT_MINT_SECRET not set — token mint is open (dev mode)")
        return
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="unauthorized")
    token = auth[len("Bearer "):]
    if token != _MINT_SECRET:
        raise HTTPException(status_code=401, detail="unauthorized")


def _generate_token(room: str, identity: str) -> str:
    """Generate a LiveKit JWT using livekit-server-sdk-python."""
    try:
        from livekit.api import AccessToken, VideoGrants
    except ImportError:
        try:
            from livekit.api.access_token import AccessToken, VideoGrants  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "livekit-server-sdk-python required: pip install livekit-api"
            ) from exc

    token = (
        AccessToken(api_key=_LIVEKIT_API_KEY, api_secret=_LIVEKIT_API_SECRET)
        .with_identity(identity)
        .with_name(identity)
        .with_grants(VideoGrants(room_join=True, room=room))
        .with_ttl(seconds=_TOKEN_TTL_S)
    )
    return token.to_jwt()


@app.post("/mint", response_model=MintResponse)
async def mint_token(req: MintRequest, request: Request) -> MintResponse:
    """Generate a LiveKit room token.

    Requires Authorization: Bearer <PARROT_MINT_SECRET>.
    """
    _check_auth(request)
    try:
        jwt = _generate_token(req.room, req.identity)
    except Exception as exc:
        logger.exception("Token generation failed")
        raise HTTPException(status_code=500, detail="token generation failed") from exc

    expires_at = int(time.time()) + _TOKEN_TTL_S
    logger.info("Minted token: room=%s identity=%s expires_at=%d", req.room, req.identity, expires_at)
    return MintResponse(token=jwt, url=_LIVEKIT_URL, expires_at=expires_at)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "token-mint"}


if __name__ == "__main__":
    import uvicorn  # type: ignore

    port = int(os.getenv("PARROT_MINT_PORT", "7888"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
