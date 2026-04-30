"""Sprint4 Phase 4 W8 — high-quality photo asset upload server.

Authoritative spec:
    - ``architecture/sprint4_phase4_entry_20260430.md §8.1`` L8 (照片
      payload 双通道：preview 走 reliable DataChannel + EcpEvent；
      high-quality asset 走 HTTP POST → Brain 暴露 /upload/photo endpoint，
      Castle 本地 cache，无 S3 / MinIO 依赖)
    - ``audit_identify_object_no_screenshot_20260420.md §5.1 B3`` for
      file path convention (Phase 5+ will add reference image discipline;
      Phase 4 just stores at ``data/photos/{yyyy-mm-dd}/{photo_id}.jpg``)

Why a separate FastAPI app inside the brain process (vs. a token-mint-style
standalone service):
    The asset upload completion MUST publish a ``photo.asset_uploaded``
    EcpEvent on the same LiveKit Room the agent is connected to. Putting
    the upload server in a separate process would force a Redis Pub/Sub
    bridge to get bytes from the upload process to the agent process for
    the publish — extra moving parts for what is, at Phase 4 scope, a
    single-process spike. Future Phase 5+ scaling can split if needed.

Lifecycle:
    :func:`start_photo_upload_server` is called by ``brain.agent`` at boot
    as an asyncio Task. It runs uvicorn programmatically inside the agent's
    event loop (``Server.serve()`` co-exists with LiveKit Agents' own loop).
    Shutdown is best-effort on agent disconnect; no graceful drain because
    the upload set is small + reconnect retries are Unity's responsibility.

What this server does NOT do (Phase 4 scope):
    * No authentication — Phase 5+ adds Bearer token mirroring token_mint
      pattern; for Phase 4 spike this server binds to localhost or the
      Castle internal network only
    * No deduplication on photo_id collision — Unity is expected to mint
      unique ids; conflict path overwrites the older file
    * No size cap enforcement at HTTP layer — Phase 5+ may add a 10 MB
      hard cap; for now we trust the Unity client
    * No object-storage backend — see entry §8.6 / §8.1 L8 deferral note
"""

from __future__ import annotations

import asyncio
import datetime
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import uvicorn  # type: ignore[import-not-found]

logger = logging.getLogger(__name__)


# Default cache root — overridable via env. Path layout per audit §5.1 B3:
#   data/photos/{yyyy-mm-dd}/{photo_id}.jpg
_PHOTO_CACHE_ROOT_ENV = "PARROT_PHOTO_CACHE_ROOT"
_DEFAULT_PHOTO_CACHE_ROOT = "data/photos"

# Server bind config — defaults to localhost:7889 for spike safety.
_PHOTO_UPLOAD_HOST_ENV = "PARROT_PHOTO_UPLOAD_HOST"
_PHOTO_UPLOAD_PORT_ENV = "PARROT_PHOTO_UPLOAD_PORT"
_DEFAULT_HOST = "127.0.0.1"
_DEFAULT_PORT = 7889

# photo_id grammar — Unity emits "ph_<hex8>". We accept anything matching
# a conservative ID grammar so future format tweaks don't require a server
# update. Reject path traversal characters at the storage step.
_FORBIDDEN_PATH_CHARS = ("/", "\\", "..", "\0", " ", "\t", "\n", "\r")


# ─── pure helpers (testable without HTTP) ─────────────────────────


def get_cache_root() -> Path:
    return Path(os.getenv(_PHOTO_CACHE_ROOT_ENV, _DEFAULT_PHOTO_CACHE_ROOT))


def is_safe_photo_id(photo_id: str) -> bool:
    """photo_id must not contain path traversal / whitespace."""
    if not photo_id or not photo_id.strip():
        return False
    if any(ch in photo_id for ch in _FORBIDDEN_PATH_CHARS):
        return False
    if len(photo_id) > 128:
        return False
    return True


def asset_path_for(photo_id: str, *, root: Path | None = None, today: str | None = None) -> Path:
    """Compute the on-disk path for a photo_id. Pure function — no I/O."""
    base = root or get_cache_root()
    day = today or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    return base / day / f"{photo_id}.jpg"


def asset_ref_for(photo_id: str, *, today: str | None = None) -> str:
    """Compute the HTTP-style asset_ref string the EcpEvent payload carries.

    The ref is intentionally not a full URL — clients dereference relative
    to the upload server origin (or read directly from disk in colocated
    Brain deployments). Format mirrors the file path layout for trivial
    server-side resolution.
    """
    day = today or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    return f"/upload/photo/{day}/{photo_id}.jpg"


# ─── FastAPI app construction (lazy — keeps module import cheap) ────


try:
    from fastapi import FastAPI, HTTPException, Request
except ImportError:  # pragma: no cover — only matters on real boot
    FastAPI = None  # type: ignore[assignment]
    HTTPException = None  # type: ignore[assignment]
    Request = None  # type: ignore[assignment]


def build_app():  # type: ignore[no-untyped-def]
    """Build a fresh FastAPI app instance.

    Constructed via factory so tests can spin up isolated app+TestClient
    pairs without sharing global state. FastAPI is imported at module
    level (above) so the type annotations on the handler signatures are
    real types — string-quoted ``"Request"`` annotations confuse FastAPI's
    dependency-resolver into treating ``request`` as a Pydantic body field
    (tests caught this with 422 responses).
    """
    if FastAPI is None:  # pragma: no cover — token_mint already requires fastapi in deploy
        raise ImportError(
            "photo_upload_server requires FastAPI: pip install fastapi uvicorn"
        )

    app = FastAPI(title="Parrot Photo Upload", version="1.0.0")

    @app.get("/health")
    async def health() -> dict:  # noqa: D401  - one-liner FastAPI handler
        return {"status": "ok", "service": "photo-upload"}

    @app.post("/upload/photo/{photo_id}")
    async def upload_photo(photo_id: str, request: Request) -> dict:
        """Accept full-resolution photo bytes for a previously-previewed photo.

        Body: raw image bytes (Content-Type ignored; client-decided format).
        Side effect: bytes saved to cache + ``photo.asset_uploaded`` EcpEvent
        published (best-effort) so observer.photo can update the PhotoNode.
        """
        if not is_safe_photo_id(photo_id):
            raise HTTPException(status_code=400, detail="invalid photo_id")

        body = await request.body()
        if not body:
            raise HTTPException(status_code=400, detail="empty body")

        path = asset_path_for(photo_id)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
        except OSError as exc:
            logger.exception("photo upload save failed photo_id=%s", photo_id)
            raise HTTPException(status_code=500, detail=f"save failed: {exc}") from exc

        asset_ref = asset_ref_for(photo_id)
        bytes_written = len(body)
        correlation_id = request.headers.get("X-Photo-Preview-Event-Id", "")

        publish_ok = await _publish_asset_uploaded_event(
            photo_id=photo_id,
            asset_ref=asset_ref,
            asset_bytes=bytes_written,
            correlation_id=correlation_id,
        )

        logger.info(
            "[photo_upload] saved photo_id=%s bytes=%d asset_ref=%s publish_ok=%s",
            photo_id, bytes_written, asset_ref, publish_ok,
        )
        return {
            "ok": True,
            "photo_id": photo_id,
            "asset_ref": asset_ref,
            "bytes": bytes_written,
            "publish_ok": publish_ok,
        }

    return app


# ─── EcpEvent publish bridge ───────────────────────────────────────


async def _publish_asset_uploaded_event(
    *,
    photo_id: str,
    asset_ref: str,
    asset_bytes: int,
    correlation_id: str = "",
) -> bool:
    """Publish ``photo.asset_uploaded`` via the brain's EcpEventPublisher.

    Returns True on success, False when no publisher is attached (server
    spun up before agent connect) or transport fails. Best-effort — the
    asset is already saved so a publish miss is recoverable by the next
    photo (observer.photo will see the next preview's BB transient and the
    asset_ref already on the disk).
    """
    try:
        from parrot.brain.event_publisher import get_ecp_event_publisher
        from parrot.shared.ecp_event import EcpEventType
    except Exception:
        return False

    publisher = get_ecp_event_publisher()
    if publisher is None:
        return False
    try:
        event = publisher.make_brain_event(
            event_type=EcpEventType.PHOTO_ASSET_UPLOADED,
            payload={
                "photo_id": photo_id,
                "asset_ref": asset_ref,
                "asset_bytes": asset_bytes,
            },
            correlation_id=correlation_id or photo_id,
        )
        return await publisher.publish(event)
    except Exception:
        logger.exception("[photo_upload] publish_asset_uploaded failed")
        return False


# ─── uvicorn lifecycle helper (for brain.agent boot) ───────────────


async def start_photo_upload_server(
    *,
    host: str | None = None,
    port: int | None = None,
) -> "uvicorn.Server | None":
    """Start the upload server as an asyncio task in the current event loop.

    Returns the ``uvicorn.Server`` instance so the caller can request a
    graceful shutdown later (``server.should_exit = True``). Returns
    ``None`` and logs a warning if uvicorn is missing.

    Brain agent boot calls this and lets the returned task run as long
    as the room is connected; no explicit drain on disconnect (Phase 4
    spike scope — Phase 5+ will add lifecycle coupling).
    """
    try:
        import uvicorn  # type: ignore[import-not-found]
    except ImportError:
        logger.warning(
            "photo_upload_server: uvicorn not available; skipping HTTP boot"
        )
        return None

    host = host or os.getenv(_PHOTO_UPLOAD_HOST_ENV, _DEFAULT_HOST)
    port = port or int(os.getenv(_PHOTO_UPLOAD_PORT_ENV, str(_DEFAULT_PORT)))
    app = build_app()

    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level=os.getenv("PARROT_LOG_LEVEL", "info").lower(),
        access_log=False,  # spike — keep agent stdout readable
    )
    server = uvicorn.Server(config)

    # Run in the same loop as the agent; the Server object exposes
    # `should_exit` for cooperative shutdown.
    asyncio.create_task(server.serve(), name="photo_upload_server")
    logger.info(
        "[photo_upload] server started host=%s port=%d cache_root=%s",
        host, port, get_cache_root(),
    )
    return server


__all__ = [
    "asset_path_for",
    "asset_ref_for",
    "build_app",
    "get_cache_root",
    "is_safe_photo_id",
    "start_photo_upload_server",
]
