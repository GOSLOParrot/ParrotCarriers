"""FastAPI BFF for the Parrot Web Console.

The Web Console keeps operator-only concerns server-side. The browser talks to
this BFF, and the BFF talks to the Castle orchestrator with the optional
``PARROT_ORCH_SECRET`` bearer token.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import time
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any, Awaitable, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    from fastapi import Body, FastAPI, HTTPException
    from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
    from fastapi.staticfiles import StaticFiles
except ImportError:  # pragma: no cover - install gate
    Body = None  # type: ignore[assignment]
    FastAPI = None  # type: ignore[assignment]
    HTTPException = None  # type: ignore[assignment]
    FileResponse = None  # type: ignore[assignment]
    HTMLResponse = None  # type: ignore[assignment]
    StreamingResponse = None  # type: ignore[assignment]
    StaticFiles = None  # type: ignore[assignment]


StatusFetcher = Callable[["OrchestratorProxyConfig"], Awaitable[dict[str, Any]]]
HealthFetcher = Callable[["OrchestratorProxyConfig"], Awaitable[dict[str, Any]]]
AppFacadeFactory = Callable[[], Any]


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
    app_facade_factory: AppFacadeFactory | None = None,
):  # type: ignore[no-untyped-def]
    """Build the Web Console app."""
    if FastAPI is None:
        raise RuntimeError("fastapi not installed; install parrotcarriers[http]")

    app = FastAPI(title="Parrot Web Console", version="0.1.0")
    fetcher = status_fetcher or fetch_orchestrator_status
    health_probe = health_fetcher or fetch_orchestrator_health
    app_facade = app_facade_factory or _default_app_facade_factory

    @app.middleware("http")
    async def no_cache_console_static(request, call_next):  # type: ignore[no-untyped-def]
        response = await call_next(request)
        path = request.url.path
        if path == "/" or path.startswith("/assets/") or not path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

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

    @app.get("/api/app/canvas")
    async def app_canvas() -> dict[str, Any]:
        return app_facade().canvas_snapshot().as_json()

    @app.get("/api/app/modules")
    async def app_modules() -> list[dict[str, Any]]:
        return [status.as_json() for status in app_facade().list_module_statuses()]

    @app.get("/api/app/line-profiles")
    async def line_profiles() -> list[dict[str, Any]]:
        return list(app_facade().list_line_profiles())

    @app.post("/api/app/line-profiles/apply")
    async def line_profile_apply(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        body = payload or {}
        draft_or_id = body.get("line_profile") or body.get("line_profile_id") or body
        return app_facade().apply_line_profile(draft_or_id)

    @app.post("/api/app/workspace/apply")
    async def workspace_apply(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        body = payload or {}
        workspace_id = str(body.get("workspace_id") or "workdesk")
        return app_facade().apply_workspace(workspace_id).as_json()

    @app.post("/api/app/lineb/audio-route")
    async def lineb_audio_route(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        body = payload or {}
        return app_facade().set_lineb_audio_route_policy(
            input_route=str(body.get("input_route") or "web_voice_lab"),
            output_route=str(body.get("output_route") or "web_audio"),
            microphone_enabled=_body_bool(body.get("microphone_enabled"), True),
            speaker_output_enabled=_body_bool_or_none(body.get("speaker_output_enabled")),
            echo_handling_mode=str(body.get("echo_handling_mode") or "web_no_video"),
            voiceprint_enabled=_body_bool(body.get("voiceprint_enabled"), False),
            speaker_state=str(body.get("speaker_state") or "web_no_video"),
            source=str(body.get("source") or "web_console.lineb_voice"),
        )

    @app.post("/api/app/lineb/tts-segment")
    async def lineb_tts_segment(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        body = payload or {}
        acoustic_refs = body.get("acoustic_refs")
        return app_facade().register_lineb_tts_segment(
            text_summary=str(body.get("text_summary") or body.get("text") or ""),
            duration_s=_body_float(body.get("duration_s"), 0.5),
            started_at=_body_float_or_none(body.get("started_at")),
            tts_voice=str(body.get("tts_voice") or body.get("voice") or ""),
            voiceprint_hash=str(body.get("voiceprint_hash") or ""),
            conversation_turn_id=str(body.get("conversation_turn_id") or ""),
            acoustic_refs=acoustic_refs if isinstance(acoustic_refs, dict) else None,
        )

    @app.post("/api/app/lineb/mic-input")
    async def lineb_mic_input(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        body = payload or {}
        return app_facade().classify_lineb_mic_input(
            observed_at=_body_float_or_none(body.get("observed_at")),
            duration_s=_body_float(body.get("duration_s"), 0.0),
            asr_text=str(body.get("asr_text") or body.get("text") or ""),
            voiceprint_hash=str(body.get("voiceprint_hash") or ""),
            echo_score=_body_float_or_none(body.get("echo_score")),
            speaker_similarity=_body_float_or_none(body.get("speaker_similarity")),
            voiceprint_decision=str(body.get("voiceprint_decision") or ""),
            speaker_label=str(body.get("speaker_label") or ""),
            voiceprint_profile_id=str(body.get("voiceprint_profile_id") or ""),
            voiceprint_enabled=_body_bool_or_none(body.get("voiceprint_enabled")),
            voiceprint_provider=str(body.get("voiceprint_provider") or ""),
            voiceprint_manifest_path=str(body.get("voiceprint_manifest_path") or ""),
            voiceprint_threshold_accept=_body_float_or_none(
                body.get("voiceprint_threshold_accept")
            ),
            voiceprint_threshold_reject=_body_float_or_none(
                body.get("voiceprint_threshold_reject")
            ),
        )

    @app.get("/api/app/live-state")
    async def app_live_state(limit: int = 80) -> dict[str, Any]:
        from parrot.brain.app_live_state import build_app_live_state

        return build_app_live_state(l2b_limit=max(1, min(limit, 200))).as_json()

    @app.get("/api/memory/live-state/changes")
    async def memory_live_state_changes(
        since: int = 0,
        limit: int = 120,
    ) -> dict[str, Any]:
        from parrot.web_console.memory_live_state import build_memory_live_state_changes

        return build_memory_live_state_changes(
            since=since,
            limit=max(1, min(limit, 200)),
        )

    @app.get("/api/memory/live-state/stream")
    async def memory_live_state_stream(
        since: int = 0,
        limit: int = 120,
        interval_s: float = 1.0,
        heartbeat_s: float = 15.0,
        max_events: int = 0,
    ):  # type: ignore[no-untyped-def]
        """Read-only SSE stream over the Memory changed-since envelope.

        This is intentionally a thin transport wrapper around
        ``/api/memory/live-state/changes``. SSE does not create a second event
        schema; it streams the same ``memory_runtime_delta_v1`` rows and keeps
        operator receipts on a separate future stream.
        """

        from parrot.web_console.memory_live_state import build_memory_live_state_changes

        safe_limit = max(1, min(int(limit or 120), 200))
        safe_interval = max(0.25, min(float(interval_s or 1.0), 30.0))
        safe_heartbeat = max(5.0, min(float(heartbeat_s or 15.0), 60.0))
        event_cap = max(0, min(int(max_events or 0), 50))

        async def event_stream():  # type: ignore[no-untyped-def]
            current_since = max(0, int(since or 0))
            sent_events = 0
            last_heartbeat = time.time()
            yield _sse_event(
                "stream_open",
                {
                    "action": "memory.live_state.stream",
                    "event_schema": "memory_runtime_delta_v1",
                    "since": current_since,
                    "receipt_stream": "separate",
                    "web_only": True,
                },
                event_id=f"memory-stream-{int(time.time() * 1000)}",
            )
            while True:
                changes = build_memory_live_state_changes(
                    since=current_since,
                    limit=safe_limit,
                )
                if changes.get("changed"):
                    current_since = int(changes.get("sequence") or current_since)
                    sent_events += 1
                    yield _sse_event(
                        "memory_delta",
                        changes,
                        event_id=str(current_since),
                    )
                    if event_cap and sent_events >= event_cap:
                        break
                    last_heartbeat = time.time()
                elif time.time() - last_heartbeat >= safe_heartbeat:
                    yield f": keep-alive {time.time():.3f}\n\n"
                    last_heartbeat = time.time()
                await asyncio.sleep(safe_interval)
            yield _sse_event(
                "stream_close",
                {
                    "action": "memory.live_state.stream.close",
                    "event_schema": "memory_runtime_delta_v1",
                    "sequence": current_since,
                    "sent_events": sent_events,
                },
                event_id=f"memory-stream-close-{current_since}",
            )

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    @app.get("/api/memory/blackboard/activity")
    async def memory_blackboard_activity(limit: int = 40) -> dict[str, Any]:
        from parrot.web_console.blackboard_activity import build_blackboard_activity_snapshot

        return build_blackboard_activity_snapshot(limit=max(1, min(limit, 120)))

    @app.get("/api/vision/evidence/status")
    async def vision_evidence_status() -> dict[str, Any]:
        from parrot.web_console.vision_evidence import evidence_status

        return evidence_status()

    @app.get("/api/vision/evidence/timeline")
    async def vision_evidence_timeline(
        limit: int = 50,
        kind: str = "",
    ) -> dict[str, Any]:
        from parrot.web_console.vision_evidence import evidence_timeline

        return evidence_timeline(limit=max(1, min(limit, 200)), kind=kind)

    @app.post("/api/vision/evidence/request")
    async def vision_evidence_request(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.vision_evidence import request_evidence

        return request_evidence(payload or {})

    @app.post("/api/vision/evidence/stage-hint")
    async def vision_evidence_stage_hint(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.vision_evidence import stage_evidence_hint

        return await stage_evidence_hint(payload or {})

    @app.post("/api/vision/evidence/memory-draft")
    async def vision_evidence_memory_draft(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.vision_evidence import evidence_memory_draft

        return evidence_memory_draft(payload or {})

    @app.post("/api/vision/evidence/frame-cache/upload")
    async def vision_evidence_frame_cache_upload(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.vision_evidence import upload_frame_cache

        return upload_frame_cache(payload or {})

    @app.get("/api/vision/evidence/screen-share-smoke")
    async def vision_evidence_screen_share_smoke(window_ms: int = 15_000) -> dict[str, Any]:
        from parrot.web_console.vision_evidence import screen_share_smoke_check

        return screen_share_smoke_check(window_ms=window_ms)

    @app.get("/api/vision/evidence/{evidence_id}")
    async def vision_evidence_detail(evidence_id: str) -> dict[str, Any]:
        from parrot.web_console.vision_evidence import evidence_detail

        return evidence_detail(evidence_id)

    @app.post("/api/app/test/visual-attention")
    async def app_test_visual_attention(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.vision_evidence import simulate_visual_attention

        return simulate_visual_attention(payload or {})

    @app.post("/api/vision/evidence/tool-lifecycle")
    async def vision_evidence_tool_lifecycle(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.brain.vision.tool_lifecycle import handle_visual_tool_lifecycle

        return await handle_visual_tool_lifecycle(payload or {}, source="web_console")

    @app.get("/api/runtime/monitor")
    async def runtime_monitor() -> dict[str, Any]:
        from parrot.web_console.runtime_monitor import build_runtime_monitor_snapshot

        return build_runtime_monitor_snapshot()

    @app.get("/api/runtime/flow")
    async def runtime_flow() -> dict[str, Any]:
        from parrot.web_console.runtime_flow import build_runtime_flow_snapshot

        return build_runtime_flow_snapshot()

    @app.get("/api/runtime/flow/changes")
    async def runtime_flow_changes(since: int = 0) -> dict[str, Any]:
        from parrot.web_console.runtime_flow import build_runtime_flow_changes

        return build_runtime_flow_changes(since=since)

    @app.get("/api/runtime/flow/stream")
    async def runtime_flow_stream(
        since: int = 0,
        interval_s: float = 1.0,
        heartbeat_s: float = 15.0,
        max_events: int = 0,
    ):  # type: ignore[no-untyped-def]
        """Read-only SSE stream over the Runtime Flow changed-since model.

        This exposes observability deltas only. It does not dispatch Scheduler
        tasks, mutate py-trees Blackboard state, or send Nanobot messages.
        Operator action receipts remain separate from this runtime read stream.
        """

        from parrot.web_console.runtime_flow import build_runtime_flow_changes

        safe_interval = max(0.25, min(float(interval_s or 1.0), 30.0))
        safe_heartbeat = max(5.0, min(float(heartbeat_s or 15.0), 60.0))
        event_cap = max(0, min(int(max_events or 0), 50))

        async def event_stream():  # type: ignore[no-untyped-def]
            current_since = max(0, int(since or 0))
            sent_events = 0
            last_heartbeat = time.time()
            yield _sse_event(
                "stream_open",
                {
                    "action": "runtime.flow.stream",
                    "event_schema": "runtime_flow_delta_v1",
                    "since": current_since,
                    "receipt_stream": "separate",
                    "web_only": True,
                },
                event_id=f"runtime-stream-{int(time.time() * 1000)}",
            )
            while True:
                changes = build_runtime_flow_changes(since=current_since)
                if changes.get("changed"):
                    current_since = int(changes.get("sequence") or current_since)
                    sent_events += 1
                    yield _sse_event(
                        "runtime_delta",
                        changes,
                        event_id=str(current_since),
                    )
                    if event_cap and sent_events >= event_cap:
                        break
                    last_heartbeat = time.time()
                elif time.time() - last_heartbeat >= safe_heartbeat:
                    yield f": keep-alive {time.time():.3f}\n\n"
                    last_heartbeat = time.time()
                await asyncio.sleep(safe_interval)
            yield _sse_event(
                "stream_close",
                {
                    "action": "runtime.flow.stream.close",
                    "event_schema": "runtime_flow_delta_v1",
                    "sequence": current_since,
                    "sent_events": sent_events,
                },
                event_id=f"runtime-stream-close-{current_since}",
            )

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    @app.get("/api/runtime/hitl/pending")
    async def runtime_hitl_pending() -> dict[str, Any]:
        from parrot.web_console.runtime_flow import pending_human_gates

        return pending_human_gates()

    @app.post("/api/runtime/hitl/draft-decision")
    async def runtime_hitl_draft_decision(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.runtime_flow import draft_human_gate_decision

        return draft_human_gate_decision(payload or {})

    @app.post("/api/runtime/hitl/apply-decision")
    async def runtime_hitl_apply_decision(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.runtime_flow import apply_human_gate_decision

        return await apply_human_gate_decision(payload or {})

    @app.get("/api/dsg/triggers/catalog")
    async def dsg_triggers_catalog() -> dict[str, Any]:
        from parrot.web_console.memory_ops import trigger_catalog

        return trigger_catalog()

    @app.post("/api/dsg/triggers/draft-event")
    async def dsg_triggers_draft_event(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import draft_trigger_event

        return draft_trigger_event(payload or {})

    @app.post("/api/dsg/triggers/fire-event")
    async def dsg_triggers_fire_event(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import fire_trigger_event

        return await fire_trigger_event(payload or {})

    @app.get("/api/l15/pool")
    async def l15_pool() -> dict[str, Any]:
        from parrot.web_console.memory_ops import build_l15_pool_snapshot

        return await build_l15_pool_snapshot()

    @app.get("/api/l15/obsidian-vault/scan")
    async def l15_obsidian_vault_scan(  # type: ignore[misc]
        vault_path: str = "",
        limit: str = "24",
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import scan_obsidian_vault

        return scan_obsidian_vault({"vault_path": vault_path, "limit": limit})

    @app.post("/api/l15/obsidian-vault/import-draft")
    async def l15_obsidian_vault_import_draft(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import draft_obsidian_vault_import

        return draft_obsidian_vault_import(payload or {})

    @app.post("/api/l15/obsidian-vault/import-plan")
    async def l15_obsidian_vault_import_plan(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import draft_obsidian_l2b_import_plan

        return draft_obsidian_l2b_import_plan(payload or {})

    @app.post("/api/l15/obsidian-vault/import")
    async def l15_obsidian_vault_import(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import apply_obsidian_vault_import

        return await apply_obsidian_vault_import(payload or {})

    @app.post("/api/l15/bucket-op/draft")
    async def l15_bucket_op_draft(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import draft_l15_bucket_op

        return draft_l15_bucket_op(payload or {})

    @app.post("/api/l15/bucket-op")
    async def l15_bucket_op(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import apply_l15_bucket_op

        return await apply_l15_bucket_op(payload or {})

    @app.post("/api/refs/binding/draft")
    async def refs_binding_draft(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import draft_ref_binding

        return draft_ref_binding(payload or {})

    @app.post("/api/refs/binding/apply")
    async def refs_binding_apply(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import apply_ref_binding

        return apply_ref_binding(payload or {})

    @app.get("/api/memory/identity-ref-index")
    async def memory_identity_ref_index(limit: int = 80) -> dict[str, Any]:
        from parrot.web_console.memory_ops import memory_identity_ref_index_snapshot

        return memory_identity_ref_index_snapshot(limit=limit)

    @app.post("/api/memory/identity-ref-index/draft")
    async def memory_identity_ref_index_draft(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import draft_memory_identity_ref_index

        return draft_memory_identity_ref_index(payload or {})

    @app.post("/api/memory/identity-ref-index/apply")
    async def memory_identity_ref_index_apply(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import apply_memory_identity_ref_index

        return apply_memory_identity_ref_index(payload or {})

    @app.post("/api/memory/identity-ref-index/graphiti-ref/draft")
    async def memory_identity_ref_index_graphiti_ref_draft(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import draft_graphiti_ref_writeback

        return draft_graphiti_ref_writeback(payload or {})

    @app.post("/api/memory/identity-ref-index/graphiti-ref/apply")
    async def memory_identity_ref_index_graphiti_ref_apply(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import apply_graphiti_ref_writeback

        return await apply_graphiti_ref_writeback(payload or {})

    @app.post("/api/memory/identity-ref-index/verify")
    async def memory_identity_ref_index_verify(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import verify_memory_identity_ref_index

        return verify_memory_identity_ref_index(payload or {})

    @app.post("/api/memory/identity-ref-index/resolve-graphiti")
    async def memory_identity_ref_index_resolve_graphiti(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import resolve_graphiti_identity_ref_index

        return resolve_graphiti_identity_ref_index(payload or {})

    @app.post("/api/memory/identity-ref-index/apply-graphiti-edge")
    async def memory_identity_ref_index_apply_graphiti_edge(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import apply_graphiti_identity_ref_edge

        return await apply_graphiti_identity_ref_edge(payload or {})

    @app.post("/api/memory/identity-ref-index/ref-scan-plan")
    async def memory_identity_ref_index_ref_scan_plan(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import draft_memory_ref_scan_plan

        return draft_memory_ref_scan_plan(payload or {})

    @app.post("/api/memory/identity-ref-index/ref-scan-dispatch")
    async def memory_identity_ref_index_ref_scan_dispatch(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import dispatch_memory_ref_scan_plan

        return await dispatch_memory_ref_scan_plan(payload or {})

    @app.get("/api/memory/identity-ref-index/ref-scan-results")
    async def memory_identity_ref_index_ref_scan_results(limit: int = 20) -> dict[str, Any]:
        from parrot.web_console.memory_ops import memory_ref_scan_result_history

        return await memory_ref_scan_result_history(limit=limit)

    @app.post("/api/l15/obsidian-node/draft")
    async def l15_obsidian_node_draft(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import draft_obsidian_setting_node

        return draft_obsidian_setting_node(payload or {})

    @app.post("/api/l15/obsidian-node")
    async def l15_obsidian_node(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import apply_obsidian_setting_node

        return await apply_obsidian_setting_node(payload or {})

    @app.post("/api/l2b/node/draft")
    async def l2b_node_draft(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import draft_l2b_node

        return draft_l2b_node(payload or {})

    @app.post("/api/l2b/node")
    async def l2b_node(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import apply_l2b_node

        return await apply_l2b_node(payload or {})

    @app.post("/api/l2b/node/delete")
    async def l2b_node_delete(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import delete_l2b_node

        return await delete_l2b_node(payload or {})

    @app.post("/api/l2b/edge/draft")
    async def l2b_edge_draft(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import draft_l2b_edge

        return draft_l2b_edge(payload or {})

    @app.post("/api/l2b/edge")
    async def l2b_edge(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import apply_l2b_edge

        return await apply_l2b_edge(payload or {})

    @app.post("/api/l2b/edge/update")
    async def l2b_edge_update(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import apply_l2b_edge_update

        return await apply_l2b_edge_update(payload or {})

    @app.post("/api/l2b/edge/delete")
    async def l2b_edge_delete(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import delete_l2b_edge

        return await delete_l2b_edge(payload or {})

    @app.post("/api/l2b/graph-policy/import-draft")
    async def l2b_graph_policy_import_draft(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.graph_policy import draft_import_destination

        return draft_import_destination(payload or {})

    @app.post("/api/l2b/subgraphs/draft")
    async def l2b_subgraphs_draft(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.graph_policy import draft_subgraph_overlay

        return draft_subgraph_overlay(payload or {})

    @app.post("/api/l2b/subgraphs/context")
    async def l2b_subgraphs_context(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.graph_policy import live_subgraph_context

        return live_subgraph_context(payload or {})

    @app.post("/api/l2b/transforms/draft")
    async def l2b_transforms_draft(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.graph_policy import draft_graph_transform

        return draft_graph_transform(payload or {})

    @app.get("/api/l2b/analysis/health")
    async def l2b_analysis_health() -> dict[str, Any]:
        from parrot.web_console.graph_policy import graph_health_snapshot

        return graph_health_snapshot()

    @app.post("/api/google/messages/check")
    async def google_messages_check(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import dispatch_message_check

        return await dispatch_message_check(payload or {})

    @app.post("/api/google/messages/push-test")
    async def google_messages_push_test(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import push_test_message

        return await push_test_message(payload or {})

    @app.post("/api/google/calendar/preview")
    async def google_calendar_preview(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import preview_google_calendar_events

        return preview_google_calendar_events(payload or {})

    @app.post("/api/google/calendar/fetch")
    async def google_calendar_fetch(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import dispatch_google_calendar_fetch

        return await dispatch_google_calendar_fetch(payload or {})

    @app.get("/api/google/calendar/results")
    async def google_calendar_results(limit: int = 20) -> dict[str, Any]:
        from parrot.web_console.memory_ops import google_calendar_result_history

        return await google_calendar_result_history(limit=limit)

    @app.post("/api/google/calendar/api-fetch")
    async def google_calendar_api_fetch(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import fetch_google_calendar_api

        return await fetch_google_calendar_api(payload or {})

    @app.post("/api/google/calendar/nanobot-fetch")
    async def google_calendar_nanobot_fetch(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import fetch_google_calendar_nanobot

        return await fetch_google_calendar_nanobot(payload or {})

    @app.post("/api/google/calendar/import-draft")
    async def google_calendar_import_draft(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import draft_google_calendar_import

        return draft_google_calendar_import(payload or {})

    @app.post("/api/google/calendar/import-plan")
    async def google_calendar_import_plan(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import draft_google_calendar_l2b_import_plan

        return draft_google_calendar_l2b_import_plan(payload or {})

    @app.post("/api/google/calendar/import")
    async def google_calendar_import(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import apply_google_calendar_import

        return await apply_google_calendar_import(payload or {})

    @app.get("/api/graphiti/status")
    async def graphiti_status_endpoint() -> dict[str, Any]:
        from parrot.brain.graphiti_console import graphiti_status

        return graphiti_status().as_json()

    @app.post("/api/graphiti/search")
    async def graphiti_search_endpoint(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.brain.graphiti_console import search_graphiti

        body = payload or {}
        return (
            await search_graphiti(
                query=str(body.get("query") or ""),
                partition=str(body.get("partition") or "goslo"),
                limit=body.get("limit") or 5,
                focal_node_uuid=str(body.get("focal_node_uuid") or ""),
                search_recipe=str(body.get("search_recipe") or body.get("strategy") or ""),
                node_labels=body.get("node_labels"),
                edge_types=body.get("edge_types"),
            )
        ).as_json()

    @app.post("/api/graphiti/subgraph/search")
    async def graphiti_subgraph_search_endpoint(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.brain.graphiti_console import search_graphiti_subgraph

        body = payload or {}
        return await search_graphiti_subgraph(
            query=str(body.get("query") or ""),
            partition=str(body.get("partition") or "goslo"),
            limit=body.get("limit") or 8,
            strategy=str(body.get("strategy") or "hybrid"),
            depth=body.get("depth") or 1,
            expansion_limit=body.get("expansion_limit") or 3,
            focal_node_uuid=str(body.get("focal_node_uuid") or ""),
            search_recipe=str(body.get("search_recipe") or ""),
            node_labels=body.get("node_labels"),
            edge_types=body.get("edge_types"),
            enrich=body.get("enrich", True),
        )

    @app.post("/api/graphiti/lookup")
    async def graphiti_lookup_endpoint(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.brain.graphiti_console import lookup_graphiti_uuids

        body = payload or {}
        raw_uuids = body.get("uuids")
        uuids = raw_uuids if isinstance(raw_uuids, list) else []
        return (
            await lookup_graphiti_uuids(
                uuids=[str(item) for item in uuids],
                uuid=str(body.get("uuid") or ""),
                partition=str(body.get("partition") or "goslo"),
                kind=str(body.get("kind") or ""),
            )
        ).as_json()

    @app.post("/api/graphiti/subgraph/export-draft")
    async def graphiti_subgraph_export_draft(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.brain.graphiti_console import draft_graphiti_subgraph_export

        return draft_graphiti_subgraph_export(payload or {})

    @app.post("/api/graphiti/subgraph/import-plan")
    async def graphiti_subgraph_import_plan(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.web_console.memory_ops import draft_graphiti_l2b_import_plan

        return draft_graphiti_l2b_import_plan(payload or {})

    @app.post("/api/graphiti/subgraph/export")
    async def graphiti_subgraph_export(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.brain.graphiti_console import export_graphiti_subgraph

        return await export_graphiti_subgraph(payload or {})

    @app.post("/api/graphiti/episode/draft")
    async def graphiti_episode_draft(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.brain.graphiti_console import draft_episode

        body = payload or {}
        return draft_episode(
            name=str(body.get("name") or "app_console_episode"),
            body=str(body.get("body") or ""),
            partition=str(body.get("partition") or "goslo"),
            source_description=str(body.get("source_description") or "app-web-console"),
        ).as_json()

    @app.post("/api/graphiti/episode")
    async def graphiti_episode(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        from parrot.brain.graphiti_console import add_episode

        body = payload or {}
        return (
            await add_episode(
                name=str(body.get("name") or "app_console_episode"),
                body=str(body.get("body") or ""),
                partition=str(body.get("partition") or "goslo"),
                source_description=str(body.get("source_description") or "app-web-console"),
                dry_run=_body_bool(body.get("dry_run"), True),
            )
        ).as_json()

    @app.get("/api/photos/asset/{day}/{photo_id}")
    async def photo_asset(day: str, photo_id: str):  # type: ignore[no-untyped-def]
        path = _safe_photo_asset_path(day=day, photo_id=photo_id)
        response = FileResponse(str(path), media_type="image/jpeg", filename=path.name)
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/api/livekit/config")
    async def livekit_config() -> dict[str, Any]:
        room = _clean_livekit_value(os.getenv("LIVEKIT_ROOM", "parrot-main"), "parrot-main")
        return {
            "url": os.getenv("LIVEKIT_URL", "ws://localhost:7880"),
            "room": room,
            "token_ttl_s": _env_int("PARROT_WEB_CONSOLE_LIVEKIT_TOKEN_TTL_S", 600),
            "web_identity_prefix": "web-console",
            "token_available": True,
        }

    @app.post("/api/livekit/web-token")
    async def livekit_web_token(  # type: ignore[misc]
        payload: dict[str, Any] | None = Body(default=None),
    ) -> dict[str, Any]:
        body = payload or {}
        room = _clean_livekit_value(
            str(body.get("room") or os.getenv("LIVEKIT_ROOM", "parrot-main")),
            "parrot-main",
        )
        identity = _clean_livekit_value(
            str(body.get("identity") or f"web-console-{int(time.time())}"),
            f"web-console-{int(time.time())}",
        )
        ttl_s = _env_int("PARROT_WEB_CONSOLE_LIVEKIT_TOKEN_TTL_S", 600)
        try:
            token = _mint_livekit_join_token(room=room, identity=identity, ttl_s=ttl_s)
        except Exception as exc:
            if HTTPException is None:
                raise
            raise HTTPException(
                status_code=500,
                detail=f"LiveKit token mint failed: {type(exc).__name__}",
            ) from exc
        return {
            "url": os.getenv("LIVEKIT_URL", "ws://localhost:7880"),
            "room": room,
            "identity": identity,
            "token": token,
            "expires_at": int(time.time()) + ttl_s,
        }

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


def _default_app_facade_factory() -> Any:
    from parrot.brain.app_first_version import AppFirstVersionFacade

    return AppFirstVersionFacade()


def _body_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _body_bool_or_none(value: Any) -> bool | None:
    if value is None or value == "":
        return None
    return _body_bool(value, False)


def _body_float(value: Any, default: float) -> float:
    parsed = _body_float_or_none(value)
    return default if parsed is None else parsed


def _body_float_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _mint_livekit_join_token(*, room: str, identity: str, ttl_s: int) -> str:
    try:
        from livekit.api import AccessToken, VideoGrants
    except ImportError:
        from livekit.api.access_token import AccessToken, VideoGrants  # type: ignore

    return (
        AccessToken(
            api_key=os.getenv("LIVEKIT_API_KEY", "devkey"),
            api_secret=os.getenv(
                "LIVEKIT_API_SECRET",
                "parrot_carriers_local_dev_livekit_secret_key_v1",
            ),
        )
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
        .with_ttl(timedelta(seconds=max(30, min(ttl_s, 3600))))
        .to_jwt()
    )


def _clean_livekit_value(value: str, default: str) -> str:
    cleaned = "".join(ch for ch in str(value or "").strip() if ch.isalnum() or ch in "-_.")
    return (cleaned or default)[:80]


def _safe_photo_asset_path(*, day: str, photo_id: str) -> Path:
    """Resolve a Web Console photo preview without exposing arbitrary files.

    Unity/App uploads store photo bytes in ``PARROT_PHOTO_CACHE_ROOT/day/id.jpg``.
    The Web route is intentionally read-only: it only serves files that resolve
    under that cache root and it reuses the upload server's photo id guard.
    """
    from parrot.brain.photo_upload_server import get_cache_root, is_safe_photo_id

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(day or "")):
        raise HTTPException(status_code=400, detail="invalid photo day")
    clean_id = str(photo_id or "").strip()
    if clean_id.lower().endswith(".jpg"):
        clean_id = clean_id[:-4]
    if not is_safe_photo_id(clean_id):
        raise HTTPException(status_code=400, detail="invalid photo id")

    root = get_cache_root().resolve()
    path = (root / day / f"{clean_id}.jpg").resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="photo path escapes cache root") from exc
    if not path.is_file():
        raise HTTPException(status_code=404, detail="photo asset not found")
    return path


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
    offline_count = sum(
        1 for item in process_list if isinstance(item, dict) and not item.get("online")
    )
    warnings = status.get("warnings") if isinstance(status.get("warnings"), list) else []
    containers = status.get("containers")
    containers_unavailable = isinstance(containers, dict) and bool(containers.get("unavailable"))
    selection_drift = status.get("selection_drift")
    is_drift = isinstance(selection_drift, dict) and bool(selection_drift.get("is_drift"))
    crash = status.get("brain_last_crash")
    has_crash = isinstance(crash, dict) and bool(crash)
    state = (
        "degraded"
        if warnings or offline_count or containers_unavailable or is_drift or has_crash
        else "connected"
    )
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


def _sse_event(event: str, data: dict[str, Any], *, event_id: str = "") -> str:
    """Serialize one Server-Sent Event frame with JSON data.

    Keep this tiny and dependency-free so the first realtime path can run in
    the existing FastAPI stack. Large binary/photo payloads must still travel
    through HTTP/storage routes, never through SSE data frames.
    """

    lines: list[str] = []
    if event_id:
        lines.append(f"id: {event_id}")
    lines.append(f"event: {event}")
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"), default=str)
    for line in payload.splitlines() or ["{}"]:
        lines.append(f"data: {line}")
    return "\n".join(lines) + "\n\n"


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


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _static_root() -> Path:
    web_root = Path(__file__).resolve().parents[3] / "web"
    react_dist = web_root / "console_dist"
    if (react_dist / "index.html").exists():
        return react_dist
    return web_root / "console"


def _missing_static_html() -> str:
    return (
        "<!doctype html><title>Parrot Web Console</title>"
        "<body><h1>Parrot Web Console static files missing</h1>"
        "<p>Expected web/console/index.html.</p></body>"
    )
