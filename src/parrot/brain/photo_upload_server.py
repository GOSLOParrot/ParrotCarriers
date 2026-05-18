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
    EcpEvent on the same LiveKit Room the agent is connected to, and must
    also dispatch that same event into the local observer pipeline. LiveKit
    data publish is not a reliable self-loop, so relying on the room to echo
    Brain-origin upload events back into Brain leaves PhotoNodes without their
    asset path. Putting the upload server in a separate process would force a
    Redis Pub/Sub bridge to get bytes from the upload process to the agent
    process for the publish + local observer update — extra moving parts for
    what is, at Phase 4 scope, a single-process spike. Future Phase 5+ scaling
    can split if needed.

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
import contextlib
import datetime
import json
import logging
import os
import socket
from pathlib import Path
from typing import TYPE_CHECKING, Any

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
    from fastapi import Body, FastAPI, Header, HTTPException, Request
except ImportError:  # pragma: no cover — only matters on real boot
    Body = None  # type: ignore[assignment]
    FastAPI = None  # type: ignore[assignment]
    Header = None  # type: ignore[assignment]
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
    write_secret = os.environ.get("PARROT_APP_MONITOR_SECRET", "").strip()

    def require_operator_auth(authorization: str = "") -> None:
        if not write_secret:
            return
        if authorization.strip() != f"Bearer {write_secret}":
            raise HTTPException(status_code=401, detail="brain_operator_auth_required")

    @app.get("/health")
    async def health() -> dict:  # noqa: D401  - one-liner FastAPI handler
        return {"status": "ok", "service": "photo-upload"}

    @app.get("/api/app/live-state")
    async def app_live_state(limit: int = 80) -> dict:
        """Read the Brain room job's in-process App live-state.

        Laptop app-monitor/Web Console runs in a different process from the
        LiveKit Brain job.  This read-only debug route lets that monitor refresh
        against the actual process that receives ``photo.taken_preview`` and
        creates PhotoNodes, without moving image bytes or memory writes through
        Web/App code.
        """
        from parrot.brain.app_live_state import build_app_live_state

        body = build_app_live_state(l2b_limit=max(1, min(int(limit or 80), 200))).as_json()
        audit = body.setdefault("audit", {})
        if isinstance(audit, dict):
            audit["source_process"] = "brain.photo_upload_server"
            audit["read_only_proxy_surface"] = True
        return body

    @app.get("/api/l2b/snapshot")
    async def l2b_snapshot(limit: int = 80) -> dict:
        """Read the Brain room job's in-process L2-B snapshot."""
        from parrot.brain.l2b_monitor import build_l2b_snapshot

        body = build_l2b_snapshot(limit=max(1, min(int(limit or 80), 200))).as_json()
        body["remote_source"] = "brain.photo_upload_server"
        body["read_only_proxy_surface"] = True
        return body

    @app.post("/api/l2b/node")
    async def l2b_node(
        payload: dict[str, Any] | None = Body(default=None),
        authorization: str = Header(default=""),
    ) -> dict:
        """Apply a Web Console L2-B node write inside the Brain process."""
        require_operator_auth(authorization)
        from parrot.web_console.memory_ops import apply_l2b_node

        return await apply_l2b_node(_brain_write_payload(payload))

    @app.post("/api/l2b/node/delete")
    async def l2b_node_delete(
        payload: dict[str, Any] | None = Body(default=None),
        authorization: str = Header(default=""),
    ) -> dict:
        require_operator_auth(authorization)
        from parrot.web_console.memory_ops import delete_l2b_node

        return await delete_l2b_node(_brain_write_payload(payload))

    @app.post("/api/l2b/edge")
    async def l2b_edge(
        payload: dict[str, Any] | None = Body(default=None),
        authorization: str = Header(default=""),
    ) -> dict:
        require_operator_auth(authorization)
        from parrot.web_console.memory_ops import apply_l2b_edge

        return await apply_l2b_edge(_brain_write_payload(payload))

    @app.post("/api/l2b/edge/update")
    async def l2b_edge_update(
        payload: dict[str, Any] | None = Body(default=None),
        authorization: str = Header(default=""),
    ) -> dict:
        require_operator_auth(authorization)
        from parrot.web_console.memory_ops import apply_l2b_edge_update

        return await apply_l2b_edge_update(_brain_write_payload(payload))

    @app.post("/api/l2b/edge/delete")
    async def l2b_edge_delete(
        payload: dict[str, Any] | None = Body(default=None),
        authorization: str = Header(default=""),
    ) -> dict:
        require_operator_auth(authorization)
        from parrot.web_console.memory_ops import delete_l2b_edge

        return await delete_l2b_edge(_brain_write_payload(payload))

    @app.post("/api/l2b/subgraphs/apply")
    async def l2b_subgraphs_apply(
        payload: dict[str, Any] | None = Body(default=None),
        authorization: str = Header(default=""),
    ) -> dict:
        require_operator_auth(authorization)
        from parrot.web_console.memory_ops import apply_l2b_work_subgraph

        return apply_l2b_work_subgraph(_brain_write_payload(payload))

    @app.post("/api/graphiti/subgraph/materialize-l2b")
    async def graphiti_subgraph_materialize_l2b(
        payload: dict[str, Any] | None = Body(default=None),
        authorization: str = Header(default=""),
    ) -> dict:
        require_operator_auth(authorization)
        from parrot.web_console.memory_ops import materialize_graphiti_l2b_subgraph

        return materialize_graphiti_l2b_subgraph(_brain_write_payload(payload))

    @app.post("/api/google/calendar/import")
    async def google_calendar_import(
        payload: dict[str, Any] | None = Body(default=None),
        authorization: str = Header(default=""),
    ) -> dict:
        require_operator_auth(authorization)
        from parrot.web_console.memory_ops import apply_google_calendar_import

        return await apply_google_calendar_import(_brain_write_payload(payload))

    @app.post("/api/l15/obsidian-vault/import")
    async def l15_obsidian_vault_import(
        payload: dict[str, Any] | None = Body(default=None),
        authorization: str = Header(default=""),
    ) -> dict:
        require_operator_auth(authorization)
        from parrot.web_console.memory_ops import apply_obsidian_vault_import

        return await apply_obsidian_vault_import(_brain_write_payload(payload))

    @app.post("/upload/photo/{photo_id}")
    async def upload_photo(photo_id: str, request: Request) -> dict:
        """Accept full-resolution photo bytes for a previously-previewed photo.

        Body: raw image bytes (Content-Type ignored; client-decided format).
        Side effect: bytes saved to cache + ``photo.asset_uploaded`` EcpEvent
        dispatched locally and published (best-effort) so observer.photo can
        update the PhotoNode and peers can observe the upload.
        """
        if not is_safe_photo_id(photo_id):
            raise HTTPException(status_code=400, detail="invalid photo_id")

        # TODO (audit Round 3 §D, 2026-05-11): enforce a hard size cap (e.g.
        # 10 MB) before reading the full body into memory. Phase 4 spike
        # explicitly trusts the Unity client; Phase 5+ should add the cap +
        # 413 PAYLOAD_TOO_LARGE response so a buggy / malicious client can't
        # OOM the agent process.
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
        asset_path = str(path)
        bytes_written = len(body)
        correlation_id = request.headers.get("X-Photo-Preview-Event-Id", "")
        timebase = _extract_upload_timebase(request)

        publish_ok = await _publish_asset_uploaded_event(
            photo_id=photo_id,
            asset_ref=asset_ref,
            asset_path=asset_path,
            asset_bytes=bytes_written,
            correlation_id=correlation_id,
            timebase=timebase,
        )

        logger.info(
            "[photo_upload] saved photo_id=%s bytes=%d asset_ref=%s publish_ok=%s",
            photo_id, bytes_written, asset_ref, publish_ok,
        )
        return {
            "ok": True,
            "photo_id": photo_id,
            "asset_ref": asset_ref,
            "asset_path": asset_path,
            "bytes": bytes_written,
            "publish_ok": publish_ok,
        }

    return app


def _brain_write_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    body = dict(payload or {})
    body["_remote_proxy_disable"] = True
    body["_brain_proxy_disable"] = True
    return body


# ─── EcpEvent publish bridge ───────────────────────────────────────


async def _publish_asset_uploaded_event(
    *,
    photo_id: str,
    asset_ref: str,
    asset_path: str,
    asset_bytes: int,
    correlation_id: str = "",
    timebase: dict[str, Any] | None = None,
) -> bool:
    """Record and publish ``photo.asset_uploaded`` from the Brain process.

    Returns True on success, False when no publisher is attached (server
    spun up before agent connect) or transport fails. Best-effort — the
    asset is already saved so a publish miss is recoverable by the next
    photo (observer.photo will see the next preview's BB transient and the
    asset_ref already on the disk).
    """
    try:
        from parrot.brain.event_publisher import get_ecp_event_publisher
        from parrot.shared.ecp_event import EcpEvent, EcpEventSource, EcpEventType
    except Exception:
        return False

    publisher = get_ecp_event_publisher()
    try:
        payload = {
            "photo_id": photo_id,
            "asset_ref": asset_ref,
            # ``asset_ref`` is the HTTP-style pointer. ``asset_path`` is the
            # real disk path used by L2-B RefTable / IntentWorkspace.
            "asset_path": asset_path,
            "asset_bytes": asset_bytes,
            **({"timebase": timebase} if timebase else {}),
        }
        if publisher is not None:
            event = publisher.make_brain_event(
                event_type=EcpEventType.PHOTO_ASSET_UPLOADED,
                payload=payload,
                correlation_id=correlation_id or photo_id,
            )
        else:
            event = EcpEvent.build(
                event_type=EcpEventType.PHOTO_ASSET_UPLOADED,
                source=EcpEventSource.BRAIN,
                payload=payload,
                correlation_id=correlation_id or photo_id,
            )

        _dispatch_asset_uploaded_locally(event)
        if publisher is None:
            return False
        return await publisher.publish(event)
    except Exception:
        logger.exception("[photo_upload] publish_asset_uploaded failed")
        return False


def _dispatch_asset_uploaded_locally(event: "EcpEvent") -> bool:
    """Mirror a Brain-origin upload event into local EcpEvent observers.

    The upload server runs in the Brain job process, but ``publish_data`` sends
    to remote participants and should not be treated as a self-delivery
    guarantee. Local dispatch keeps L2-B PhotoNode, BB, evidence ledger and
    IntentWorkspace updates on the same observer path as room-delivered ECP.
    If a future SDK/runtime echoes the event back, ingest dedup drops it by
    ``event_id``.
    """
    try:
        from parrot.brain.event_ingest import get_existing_ecp_event_ingest
        from parrot.shared.ecp_event import TOPIC_ECP_EVENT

        ingest = get_existing_ecp_event_ingest()
        if ingest is None:
            return False
        handled = ingest.handle_raw(
            TOPIC_ECP_EVENT,
            event.to_wire_json().encode("utf-8"),
        )
        return handled is not None
    except Exception:
        logger.exception("[photo_upload] local asset_uploaded dispatch failed")
        return False


def _extract_upload_timebase(request: "Request") -> dict[str, Any]:
    """Parse optional producer sample-time metadata from photo upload headers.

    This keeps the top-level ECP DTO unchanged while letting Unity/Web upload
    producers attach the same V1 ``payload["timebase"]`` shape used by the
    temporal evidence ledger.  Missing or malformed headers simply return an
    empty dict so old upload clients keep working.
    """
    headers = request.headers
    parsed = _json_header_object(headers.get("X-Parrot-Timebase", ""))
    if parsed:
        return _clean_timebase(parsed)

    raw: dict[str, Any] = {
        "clock_domain": headers.get("X-Parrot-Clock-Domain", ""),
        "wall_time_ms": headers.get("X-Parrot-Wall-Time-Ms", "")
        or headers.get("X-Photo-Ts-Ms", ""),
        "monotonic_ms": headers.get("X-Parrot-Monotonic-Ms", ""),
        "media_time_us": headers.get("X-Parrot-Media-Time-Us", ""),
        "sequence": headers.get("X-Parrot-Sequence", ""),
        "source_id": headers.get("X-Parrot-Source-Id", ""),
    }
    return _clean_timebase(raw)


def _json_header_object(text: str) -> dict[str, Any]:
    if not text:
        return {}
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _clean_timebase(raw: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    clock_domain = str(raw.get("clock_domain") or "").strip()
    source_id = str(raw.get("source_id") or "").strip()
    if clock_domain:
        out["clock_domain"] = clock_domain
    if source_id:
        out["source_id"] = source_id
    for key in ("wall_time_ms", "monotonic_ms", "media_time_us", "sequence"):
        value = _int_or_none(raw.get(key))
        if value is not None:
            out[key] = value
    if "estimated" in raw:
        out["estimated"] = bool(raw.get("estimated"))
    return out


def _int_or_none(value: Any) -> int | None:
    if isinstance(value, bool) or value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# ─── uvicorn lifecycle helper (for brain.agent boot) ───────────────


def _is_port_bindable(host: str, port: int) -> tuple[bool, str]:
    """Probe ``host:port`` with a short-lived socket.

    FIX (2026-05-11 audit Round 5, Bug M): uvicorn's ``Server.startup``
    calls ``sys.exit(1)`` on bind failure. When wrapped in
    ``asyncio.create_task``, that ``SystemExit`` propagates up and can
    tear down the **brain agent's own event loop**, killing the whole
    process. Pre-checking the port lets us refuse to start the server
    cleanly and log a structured error instead of letting uvicorn crash
    the agent.

    Returns ``(True, "")`` if the port can be bound right now,
    ``(False, reason)`` otherwise. The probe-then-bind window is racy
    by definition, but the typical failure mode this guards against is
    "previous Brain process didn't release the port" — a steady-state,
    not a TOCTOU race — so this remains useful even though it's not
    atomic.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Deliberately NOT setting SO_REUSEADDR on the probe: on Windows,
    # SO_REUSEADDR has "share the port" semantics, so a probe with that
    # flag would succeed even when another listener already holds the
    # port. Leaving it off makes the probe accurately answer "can a
    # fresh listener take this port right now?".
    try:
        sock.bind((host, port))
    except OSError as exc:
        return False, f"{type(exc).__name__}: {exc}"
    finally:
        with contextlib.suppress(OSError):
            sock.close()
    return True, ""


async def start_photo_upload_server(
    *,
    host: str | None = None,
    port: int | None = None,
) -> "uvicorn.Server | None":
    """Start the upload server as an asyncio task in the current event loop.

    Returns the ``uvicorn.Server`` instance so the caller can request a
    graceful shutdown later (``server.should_exit = True``). Returns
    ``None`` and logs a warning if uvicorn is missing **or** the port
    is already bound (Round 5 Bug M).

    Brain agent boot calls this and lets the returned task run as long
    as the room is connected.
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

    bindable, reason = _is_port_bindable(host, port)
    if not bindable:
        logger.error(
            "[photo_upload] cannot start: %s:%d already in use (%s); "
            "photo asset upload disabled this session. Stop any stale "
            "Brain / uvicorn process holding the port and reconnect.",
            host, port, reason,
        )
        return None

    app = build_app()
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level=os.getenv("PARROT_LOG_LEVEL", "info").lower(),
        access_log=False,  # spike — keep agent stdout readable
    )
    server = uvicorn.Server(config)

    async def _serve_guarded() -> None:
        """Run uvicorn without letting a bind-race SystemExit kill the job.

        The pre-bind socket check catches the normal stale-port case, but two
        LiveKit room jobs can still race between the check and uvicorn's bind.
        Uvicorn raises ``SystemExit`` for that late bind failure; catching it
        here keeps the Brain room job alive and simply disables photo upload for
        this session.
        """
        try:
            await server.serve()
        except SystemExit as exc:
            logger.error(
                "[photo_upload] uvicorn raised SystemExit(%s) during serve; "
                "photo upload disabled for this room job",
                getattr(exc, "code", "?"),
            )

    # Run in the same loop as the agent; the Server object exposes
    # `should_exit` for cooperative shutdown.
    task = asyncio.create_task(_serve_guarded(), name="photo_upload_server")
    setattr(server, "_parrot_task", task)

    # FIX (2026-05-11 audit Round 5, Bug M): the photo upload task is
    # NOT in `brain.agent.background_tasks`, so it has no
    # `_log_task_done` callback. Without this hook, an unexpected
    # `serve()` failure (e.g. a delayed uvicorn shutdown crash, or a
    # ``SystemExit`` from a future code path) becomes "Task exception
    # was never retrieved" — silently disabled photo upload.
    def _log_done(done: "asyncio.Task[Any]") -> None:
        with contextlib.suppress(asyncio.CancelledError):
            exc = done.exception()
            if exc is None:
                logger.info("[photo_upload] server task exited cleanly")
                return
            if isinstance(exc, SystemExit):
                logger.error(
                    "[photo_upload] uvicorn raised SystemExit(%s) — "
                    "agent process bind likely failed; photo upload "
                    "is now disabled for this session.",
                    getattr(exc, "code", "?"),
                )
                return
            logger.error(
                "[photo_upload] server task crashed: %s",
                exc,
                exc_info=(type(exc), exc, exc.__traceback__),
            )

    task.add_done_callback(_log_done)

    logger.info(
        "[photo_upload] server started host=%s port=%d cache_root=%s",
        host, port, get_cache_root(),
    )
    return server


async def stop_photo_upload_server(
    server: "uvicorn.Server | None",
    *,
    timeout_s: float = 3.0,
) -> None:
    """Request cooperative shutdown for the in-process upload server.

    FIX (2026-05-11 audit Round 5, Bug L): the previous version wrapped
    the task with ``asyncio.shield`` so timeouts could not cancel a
    stuck uvicorn shutdown. The hung task survived the timeout window
    and kept port 7889 bound — which then collided with the next
    session's :func:`start_photo_upload_server` (Bug M) on cold restart.
    Now we ask uvicorn to exit cooperatively first, and if that doesn't
    win within ``timeout_s`` we explicitly cancel the task and wait a
    final short grace period for the cancel to drain.
    """
    if server is None:
        return
    server.should_exit = True
    task = getattr(server, "_parrot_task", None)
    if task is None:
        return

    try:
        await asyncio.wait_for(asyncio.shield(task), timeout=timeout_s)
        return
    except asyncio.TimeoutError:
        logger.warning(
            "[photo_upload] cooperative shutdown did not finish within "
            "%.2fs — cancelling task to release the port.",
            timeout_s,
        )

    task.cancel()
    with contextlib.suppress(asyncio.CancelledError, asyncio.TimeoutError, Exception):
        await asyncio.wait_for(task, timeout=max(0.5, timeout_s / 2))


__all__ = [
    "asset_path_for",
    "asset_ref_for",
    "build_app",
    "get_cache_root",
    "is_safe_photo_id",
    "start_photo_upload_server",
    "stop_photo_upload_server",
    "_is_port_bindable",
]
