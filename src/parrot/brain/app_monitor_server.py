"""App v1 Web smoke monitor and developer test console.

This FastAPI app is intentionally small and local-first. It exposes the same
facade read models that Unity should consume, plus a bounded L2-B snapshot for
debug visualization. Mutating test actions route through the App facade or the
same EcpEvent observer path Unity uses; live-state views are read-only.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from parrot.brain.app_first_version import (
    AppFirstVersionFacade,
    CameraMode,
    PhotoAwarenessPolicy,
)
from parrot.brain.app_test_harness import (
    simulate_bbox_event,
    simulate_focus_event,
    simulate_photo_preview,
)
from parrot.brain.app_v1_self_check import run_app_v1_self_check
from parrot.brain.graphiti_console import (
    add_episode,
    draft_episode,
    draft_graphiti_subgraph_export,
    export_graphiti_subgraph,
    graphiti_status,
    lookup_graphiti_uuids,
    search_graphiti,
    search_graphiti_subgraph,
)
from parrot.brain.app_live_state import build_app_live_state
from parrot.brain.l2b_monitor import build_l2b_snapshot

try:
    from fastapi import Body, FastAPI, Header, HTTPException, Request
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
except ImportError:  # pragma: no cover - only matters on deployments without [http]
    Body = None  # type: ignore[assignment]
    FastAPI = None  # type: ignore[assignment]
    Header = None  # type: ignore[assignment]
    HTTPException = None  # type: ignore[assignment]
    Request = None  # type: ignore[assignment]
    HTMLResponse = None  # type: ignore[assignment]
    JSONResponse = None  # type: ignore[assignment]
    StaticFiles = None  # type: ignore[assignment]


def build_app():  # type: ignore[no-untyped-def]
    """Build the read-only smoke monitor app."""
    if FastAPI is None:
        raise RuntimeError("fastapi not installed; install parrotcarriers[http]")

    app = FastAPI(title="GOSLO App V1 Smoke Monitor")
    write_secret = os.environ.get("PARROT_APP_MONITOR_SECRET", "").strip()

    @app.middleware("http")
    async def app_monitor_write_auth(request: Request, call_next):  # type: ignore[no-untyped-def]
        if write_secret and request.method.upper() in {"POST", "PUT", "PATCH", "DELETE"}:
            auth = request.headers.get("Authorization", "").strip()
            if auth != f"Bearer {write_secret}":
                return JSONResponse(
                    status_code=401,
                    content={"detail": "app_monitor_auth_required"},
                )
        return await call_next(request)

    def require_write_auth(authorization: str = "") -> None:
        if not write_secret:
            return
        if authorization.strip() != f"Bearer {write_secret}":
            raise HTTPException(status_code=401, detail="app_monitor_auth_required")

    asset_root = _pixel_asset_root()
    if asset_root.exists():
        app.mount("/pixel-assets", StaticFiles(directory=str(asset_root)), name="pixel-assets")

    @app.get("/", response_class=HTMLResponse)
    async def index():  # type: ignore[no-untyped-def]
        return _index_html()

    @app.get("/api/app/canvas")
    async def app_canvas():  # type: ignore[no-untyped-def]
        return AppFirstVersionFacade().canvas_snapshot().as_json()

    @app.get("/api/app/modules")
    async def app_modules():  # type: ignore[no-untyped-def]
        return [status.as_json() for status in AppFirstVersionFacade().list_module_statuses()]

    @app.get("/api/app/tool-cabinet")
    async def tool_cabinet():  # type: ignore[no-untyped-def]
        return [tool.as_json() for tool in AppFirstVersionFacade().list_tool_cabinet()]

    @app.get("/api/app/assets")
    async def app_assets():  # type: ignore[no-untyped-def]
        return AppFirstVersionFacade().asset_manifest()

    @app.get("/api/app/personas")
    async def app_personas():  # type: ignore[no-untyped-def]
        return list(AppFirstVersionFacade().list_personas())

    @app.get("/api/app/room-setting")
    async def room_setting(room_profile_id: str = ""):  # type: ignore[no-untyped-def]
        return AppFirstVersionFacade().room_setting_snapshot(
            room_profile_id or None
        ).as_json()

    @app.post("/api/app/room-setting/preview")
    async def room_setting_preview(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        body = payload or {}
        draft = body.get("room_profile") if isinstance(body.get("room_profile"), dict) else body
        return AppFirstVersionFacade().preview_room_profile(draft)

    @app.post("/api/app/room-setting/new")
    async def room_setting_new(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        body = payload or {}
        return AppFirstVersionFacade().new_room_profile(
            base_id=str(body.get("base_id") or "") or None,
            display_name=str(body.get("display_name") or "") or None,
        )

    @app.post("/api/app/room-setting/save")
    async def room_setting_save(
        payload: dict[str, Any] | None = Body(default=None),
        authorization: str = Header(default=""),
    ):  # type: ignore[misc]
        require_write_auth(authorization)
        body = payload or {}
        draft = body.get("room_profile") if isinstance(body.get("room_profile"), dict) else body
        return AppFirstVersionFacade().save_room_profile(draft)

    @app.post("/api/app/room-setting/apply")
    async def room_setting_apply(
        payload: dict[str, Any] | None = Body(default=None),
        authorization: str = Header(default=""),
    ):  # type: ignore[misc]
        require_write_auth(authorization)
        body = payload or {}
        draft_or_id = body.get("room_profile") or body.get("room_profile_id") or body
        return AppFirstVersionFacade().apply_room_profile(
            draft_or_id,
            experience_mode=body.get("experience_mode"),
        )

    @app.get("/api/app/line-profiles")
    async def line_profiles():  # type: ignore[no-untyped-def]
        return list(AppFirstVersionFacade().list_line_profiles())

    @app.post("/api/app/line-profiles/preview")
    async def line_profile_preview(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        body = payload or {}
        draft = body.get("line_profile") if isinstance(body.get("line_profile"), dict) else body
        return AppFirstVersionFacade().preview_line_profile(draft)

    @app.post("/api/app/line-profiles/save")
    async def line_profile_save(
        payload: dict[str, Any] | None = Body(default=None),
        authorization: str = Header(default=""),
    ):  # type: ignore[misc]
        require_write_auth(authorization)
        body = payload or {}
        draft = body.get("line_profile") if isinstance(body.get("line_profile"), dict) else body
        return AppFirstVersionFacade().save_line_profile(draft)

    @app.post("/api/app/line-profiles/apply")
    async def line_profile_apply(
        payload: dict[str, Any] | None = Body(default=None),
        authorization: str = Header(default=""),
    ):  # type: ignore[misc]
        require_write_auth(authorization)
        body = payload or {}
        draft_or_id = body.get("line_profile") or body.get("line_profile_id") or body
        return AppFirstVersionFacade().apply_line_profile(draft_or_id)

    @app.post("/api/app/lineb/audio-route")
    async def lineb_audio_route(
        payload: dict[str, Any] | None = Body(default=None),
        authorization: str = Header(default=""),
    ):  # type: ignore[misc]
        require_write_auth(authorization)
        body = payload or {}
        return AppFirstVersionFacade().set_lineb_audio_route_policy(
            input_route=str(body.get("input_route") or "unknown"),
            output_route=str(body.get("output_route") or "unknown"),
            microphone_enabled=_body_bool(body.get("microphone_enabled"), True),
            speaker_output_enabled=_body_bool_or_none(body.get("speaker_output_enabled")),
            echo_handling_mode=str(body.get("echo_handling_mode") or "") or None,
            voiceprint_enabled=_body_bool(body.get("voiceprint_enabled"), False),
            speaker_state=str(body.get("speaker_state") or "unknown"),
            source=str(body.get("source") or "web_monitor"),
        )

    @app.post("/api/app/lineb/tts-segment")
    async def lineb_tts_segment(
        payload: dict[str, Any] | None = Body(default=None),
        authorization: str = Header(default=""),
    ):  # type: ignore[misc]
        require_write_auth(authorization)
        body = payload or {}
        acoustic_refs = body.get("acoustic_refs")
        return AppFirstVersionFacade().register_lineb_tts_segment(
            text_summary=str(body.get("text_summary") or body.get("text") or ""),
            duration_s=_body_float(body.get("duration_s"), 0.5),
            started_at=_body_float_or_none(body.get("started_at")),
            tts_voice=str(body.get("tts_voice") or body.get("voice") or ""),
            voiceprint_hash=str(body.get("voiceprint_hash") or ""),
            conversation_turn_id=str(body.get("conversation_turn_id") or ""),
            acoustic_refs=acoustic_refs if isinstance(acoustic_refs, dict) else None,
        )

    @app.post("/api/app/lineb/mic-input")
    async def lineb_mic_input(
        payload: dict[str, Any] | None = Body(default=None),
        authorization: str = Header(default=""),
    ):  # type: ignore[misc]
        require_write_auth(authorization)
        body = payload or {}
        return AppFirstVersionFacade().classify_lineb_mic_input(
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

    @app.post("/api/app/lineb/voiceprint/verify-embedding")
    async def lineb_voiceprint_verify_embedding(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        body = payload or {}
        embedding = body.get("embedding")
        if not isinstance(embedding, list):
            embedding = []
        embedding_values: list[float] = []
        for item in embedding:
            parsed = _body_float_or_none(item)
            if parsed is not None:
                embedding_values.append(parsed)
        return AppFirstVersionFacade().verify_lineb_voiceprint_embedding(
            embedding_values,
            observed_at=_body_float_or_none(body.get("observed_at")),
        )

    @app.get("/api/app/live-state")
    async def app_live_state(limit: int = 80):  # type: ignore[no-untyped-def]
        return build_app_live_state(l2b_limit=max(1, min(limit, 200))).as_json()

    @app.post("/api/app/workspace/apply")
    async def apply_workspace(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        body = payload or {}
        workspace_id = str(body.get("workspace_id") or "workdesk")
        return AppFirstVersionFacade().apply_workspace(workspace_id).as_json()

    @app.post("/api/app/camera/mode")
    async def set_camera_mode(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        body = payload or {}
        mode = str(body.get("mode") or CameraMode.PREVIEW.value)
        return AppFirstVersionFacade().set_camera_mode(mode).as_json()

    @app.post("/api/app/camera/capture-request")
    async def camera_capture_request(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        body = payload or {}
        return AppFirstVersionFacade().request_camera_capture(
            candidate_subject_uuid=str(body.get("candidate_subject_uuid") or ""),
            awareness_policy=str(body.get("awareness_policy") or PhotoAwarenessPolicy.AWARE_SILENT.value),
        ).as_json()

    @app.post("/api/app/awareness")
    async def set_awareness(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        body = payload or {}
        return AppFirstVersionFacade().set_photo_awareness(
            str(body.get("policy") or PhotoAwarenessPolicy.AWARE_SILENT.value),
            enabled=bool(body.get("enabled", True)),
            preview_ttl_seconds=int(body.get("preview_ttl_seconds") or 15 * 60),
        ).as_json()

    @app.post("/api/app/xrhand/mode")
    async def set_xrhand_mode(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        body = payload or {}
        return AppFirstVersionFacade().set_xrhand_mode(str(body.get("mode") or "tracking")).as_json()

    @app.post("/api/app/visual-tool/event")
    async def visual_tool_event(
        payload: dict[str, Any] | None = Body(default=None),
        authorization: str = Header(default=""),
    ):  # type: ignore[misc]
        """App BBox/MAG lifecycle route.

        Unity should call this for stable interaction milestones such as
        ``lock``, ``confirm`` or ``explicit_send``.  High-frequency drag frames
        stay local or use the lossy ECP tick topic; this route records durable
        evidence anchors and decides whether the event is only staged in
        IntentWorkspace or also pushed as a C3 context notice.
        """
        require_write_auth(authorization)
        from parrot.brain.vision.tool_lifecycle import handle_visual_tool_lifecycle

        return await handle_visual_tool_lifecycle(payload or {}, source="app_http")

    @app.post("/api/app/visual-tool/asset/{asset_id}")
    async def visual_tool_asset_upload(
        asset_id: str,
        request: Request,
        authorization: str = Header(default=""),
    ):  # type: ignore[misc]
        """Upload a BBox/MAG rendered crop or preview image.

        The response returns ``asset_path`` and a `TimeAlignedSampleRef`.
        Unity can pass that ``asset_path`` into `/api/app/visual-tool/event`
        so the lifecycle receipt stages a concrete stored image instead of
        only a region/time anchor.  This keeps image bytes out of ECP/RPC.
        """
        require_write_auth(authorization)
        from parrot.brain.vision.tool_lifecycle import store_visual_tool_asset

        body = await request.body()
        return store_visual_tool_asset(
            asset_id=asset_id,
            body=body,
            content_type=str(request.headers.get("content-type") or ""),
            metadata=_visual_tool_asset_metadata_from_headers(request),
        )

    @app.post("/api/app/nanobot/report")
    async def nanobot_report(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        body = payload or {}
        return (await AppFirstVersionFacade().stage_nanobot_report(
            task_id=str(body.get("task_id") or "web_console_task"),
            title=str(body.get("title") or "Web console Nanobot note"),
            body=str(body.get("body") or "Fixture Nanobot report from App V1 Web console."),
        )).as_json()

    @app.post("/api/app/calendar/draft")
    async def calendar_draft(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        body = payload or {}
        return (await AppFirstVersionFacade().create_calendar_draft(
            action=str(body.get("action") or "create"),
            title=str(body.get("title") or "Web console calendar draft"),
            time_range=str(body.get("time_range") or ""),
            payload=body.get("payload") if isinstance(body.get("payload"), dict) else None,
        )).as_json()

    @app.post("/api/app/test/focus")
    async def test_focus(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        body = payload or {}
        return simulate_focus_event(
            focus_id=str(body.get("focus_id") or "fc_web_console"),
            action=str(body.get("action") or "anchored"),
            label=str(body.get("label") or "web console focus"),
        ).as_json()

    @app.post("/api/app/test/bbox")
    async def test_bbox(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        body = payload or {}
        return simulate_bbox_event(
            bbox_id=str(body.get("bbox_id") or "bb_web_console"),
            action=str(body.get("action") or "placed"),
            label=str(body.get("label") or "web console bbox"),
        ).as_json()

    @app.post("/api/app/test/photo-preview")
    async def test_photo_preview(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        body = payload or {}
        return simulate_photo_preview(
            photo_id=str(body.get("photo_id") or "ph_web_console"),
            candidate_subject_uuid=str(body.get("candidate_subject_uuid") or ""),
        ).as_json()

    @app.post("/api/app/self-check")
    async def app_self_check():  # type: ignore[no-untyped-def]
        return (await run_app_v1_self_check()).as_json()

    @app.get("/api/l2b/snapshot")
    async def l2b_snapshot(limit: int = 80):  # type: ignore[no-untyped-def]
        return build_l2b_snapshot(limit=max(1, min(limit, 200))).as_json()

    @app.post("/api/l2b/subgraphs/context")
    async def l2b_subgraphs_context(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        from parrot.web_console.graph_policy import live_subgraph_context

        return live_subgraph_context({**(payload or {}), "_remote_proxy_disable": True})

    @app.get("/api/l2b/analysis/health")
    async def l2b_analysis_health():  # type: ignore[no-untyped-def]
        from parrot.web_console.graph_policy import graph_health_snapshot

        return graph_health_snapshot()

    @app.get("/api/runtime/capabilities/catalog")
    async def runtime_capabilities_catalog(
        q: str = "",
        kind: str = "",
        execution_policy: str = "",
        interaction_mode: str = "",
    ):  # type: ignore[no-untyped-def]
        from parrot.web_console.capability_catalog import build_runtime_capability_catalog

        return build_runtime_capability_catalog(
            q=q,
            kind=kind,
            execution_policy=execution_policy,
            interaction_mode=interaction_mode,
        )

    @app.post("/api/runtime/workflow/plan-draft")
    async def runtime_workflow_plan_draft(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        from parrot.web_console.runtime_flow import draft_workflow_plan

        return await draft_workflow_plan(payload or {})

    @app.post("/api/runtime/workflow/result-contract")
    async def runtime_workflow_result_contract(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        from parrot.web_console.runtime_flow import draft_workflow_result_contract

        return await draft_workflow_result_contract(payload or {})

    @app.post("/api/runtime/workflow/validate")
    async def runtime_workflow_validate(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        from parrot.web_console.workflow_drafts import validate_workflow_artifact

        return validate_workflow_artifact(payload or {})

    @app.get("/api/runtime/workflow/export")
    async def runtime_workflow_export(workflow_id: str):  # type: ignore[no-untyped-def]
        from parrot.web_console.workflow_drafts import export_workflow_artifact

        return export_workflow_artifact(workflow_id)

    @app.post("/api/runtime/workflow/import-preview")
    async def runtime_workflow_import_preview(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        from parrot.web_console.workflow_drafts import preview_workflow_import

        return preview_workflow_import(payload or {})

    @app.get("/api/runtime/workflow/result-intake")
    async def runtime_workflow_result_intake_list(q: str = "", limit: int = 50):  # type: ignore[no-untyped-def]
        from parrot.web_console.workflow_result_intake import list_workflow_result_intakes

        return list_workflow_result_intakes(q=q, limit=limit)

    @app.post("/api/runtime/workflow/result-intake")
    async def runtime_workflow_result_intake(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        from parrot.web_console.workflow_result_intake import intake_workflow_result

        return await intake_workflow_result(payload or {})

    @app.delete("/api/runtime/workflow/result-intake/{entry_id}")
    async def runtime_workflow_result_intake_delete(entry_id: str):  # type: ignore[no-untyped-def]
        from parrot.web_console.workflow_result_intake import delete_workflow_result_intake

        return delete_workflow_result_intake(entry_id)

    @app.post("/api/runtime/workflow/run")
    async def runtime_workflow_run(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        from parrot.web_console.runtime_flow import run_workflow_draft

        return await run_workflow_draft(payload or {})

    @app.get("/api/runtime/workflow/action-gates")
    async def runtime_workflow_action_gates(state: str = "pending", q: str = "", limit: int = 50):  # type: ignore[no-untyped-def]
        from parrot.web_console.workflow_action_gates import list_workflow_action_gates

        return list_workflow_action_gates(state=state, q=q, limit=limit)

    @app.post("/api/runtime/workflow/action-gates")
    async def runtime_workflow_action_gate_draft(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        from parrot.web_console.workflow_action_gates import draft_workflow_action_gate

        return draft_workflow_action_gate(payload or {})

    @app.post("/api/runtime/workflow/action-gates/decision")
    async def runtime_workflow_action_gate_decision(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        from parrot.web_console.workflow_action_gates import apply_workflow_action_gate

        return await apply_workflow_action_gate(payload or {})

    @app.delete("/api/runtime/workflow/action-gates/{gate_id}")
    async def runtime_workflow_action_gate_delete(gate_id: str):  # type: ignore[no-untyped-def]
        from parrot.web_console.workflow_action_gates import delete_workflow_action_gate

        return delete_workflow_action_gate(gate_id)

    @app.get("/api/runtime/workflows/drafts")
    async def runtime_workflow_drafts(q: str = "", limit: int = 50):  # type: ignore[no-untyped-def]
        from parrot.web_console.workflow_drafts import list_workflow_drafts

        return list_workflow_drafts(q=q, limit=limit)

    @app.get("/api/runtime/workflows/drafts/{workflow_id}")
    async def runtime_workflow_draft_get(workflow_id: str):  # type: ignore[no-untyped-def]
        from parrot.web_console.workflow_drafts import get_workflow_draft

        return get_workflow_draft(workflow_id)

    @app.post("/api/runtime/workflows/drafts")
    async def runtime_workflow_draft_save(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        from parrot.web_console.workflow_drafts import save_workflow_draft

        return save_workflow_draft(payload or {})

    @app.delete("/api/runtime/workflows/drafts/{workflow_id}")
    async def runtime_workflow_draft_delete(workflow_id: str):  # type: ignore[no-untyped-def]
        from parrot.web_console.workflow_drafts import delete_workflow_draft

        return delete_workflow_draft(workflow_id)

    @app.post("/api/google/calendar/preview")
    async def google_calendar_preview(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        from parrot.web_console.memory_ops import preview_google_calendar_events

        return preview_google_calendar_events(payload or {})

    @app.post("/api/google/calendar/api-fetch")
    async def google_calendar_api_fetch(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        from parrot.web_console.memory_ops import fetch_google_calendar_api

        return await fetch_google_calendar_api(payload or {})

    @app.post("/api/google/calendar/nanobot-fetch")
    async def google_calendar_nanobot_fetch(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        from parrot.web_console.memory_ops import fetch_google_calendar_nanobot

        return await fetch_google_calendar_nanobot(payload or {})

    @app.post("/api/google/messages/check")
    async def google_messages_check(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        from parrot.web_console.memory_ops import dispatch_message_check

        return await dispatch_message_check(payload or {})

    @app.post("/api/google/messages/push-test")
    async def google_messages_push_test(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        from parrot.web_console.memory_ops import push_test_message

        return await push_test_message(payload or {})

    @app.get("/api/graphiti/status")
    async def graphiti_status_endpoint():  # type: ignore[no-untyped-def]
        return graphiti_status().as_json()

    @app.post("/api/graphiti/search")
    async def graphiti_search_endpoint(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        body = payload or {}
        return (await search_graphiti(
            query=str(body.get("query") or ""),
            partition=str(body.get("partition") or "goslo"),
            limit=body.get("limit") or 5,
            focal_node_uuid=str(body.get("focal_node_uuid") or ""),
            search_recipe=str(body.get("search_recipe") or body.get("strategy") or ""),
            node_labels=body.get("node_labels"),
            edge_types=body.get("edge_types"),
        )).as_json()

    @app.post("/api/graphiti/subgraph/search")
    async def graphiti_subgraph_search_endpoint(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
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
    async def graphiti_lookup_endpoint(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        body = payload or {}
        raw_uuids = body.get("uuids")
        uuids = raw_uuids if isinstance(raw_uuids, list) else []
        return (await lookup_graphiti_uuids(
            uuids=[str(item) for item in uuids],
            uuid=str(body.get("uuid") or ""),
            partition=str(body.get("partition") or "goslo"),
            kind=str(body.get("kind") or ""),
        )).as_json()

    @app.post("/api/graphiti/subgraph/export-draft")
    async def graphiti_subgraph_export_draft(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        return draft_graphiti_subgraph_export(payload or {})

    @app.post("/api/graphiti/subgraph/import-plan")
    async def graphiti_subgraph_import_plan(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        from parrot.web_console.memory_ops import draft_graphiti_l2b_import_plan

        return draft_graphiti_l2b_import_plan(payload or {})

    @app.post("/api/graphiti/subgraph/materialize-l2b")
    async def graphiti_subgraph_materialize_l2b(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        from parrot.web_console.memory_ops import materialize_graphiti_l2b_subgraph

        return materialize_graphiti_l2b_subgraph({**(payload or {}), "_remote_proxy_disable": True})

    @app.post("/api/graphiti/subgraph/export")
    async def graphiti_subgraph_export_endpoint(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        return await export_graphiti_subgraph(payload or {})

    @app.post("/api/graphiti/episode/draft")
    async def graphiti_episode_draft(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        body = payload or {}
        return draft_episode(
            name=str(body.get("name") or "app_console_episode"),
            body=str(body.get("body") or ""),
            partition=str(body.get("partition") or "goslo"),
            source_description=str(body.get("source_description") or "app-web-console"),
        ).as_json()

    @app.post("/api/graphiti/episode")
    async def graphiti_episode(payload: dict[str, Any] | None = Body(default=None)):  # type: ignore[misc]
        body = payload or {}
        return (await add_episode(
            name=str(body.get("name") or "app_console_episode"),
            body=str(body.get("body") or ""),
            partition=str(body.get("partition") or "goslo"),
            source_description=str(body.get("source_description") or "app-web-console"),
            dry_run=bool(body.get("dry_run", True)),
        )).as_json()

    @app.get("/health")
    async def health():  # type: ignore[no-untyped-def]
        return {"ok": True, "service": "app-v1-monitor", "mode": "developer-console"}

    return app


def _pixel_asset_root() -> Path:
    return Path("codex_workspace/design_workspace/asset_pipeline/pixel_asset_workspace").resolve()


def _index_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>GOSLO App V1 Console</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #202024;
      --bg-2: #17171b;
      --panel: #27262d;
      --panel-2: #302e38;
      --panel-3: #1f1e25;
      --ink: #dcddde;
      --muted: #a6a3ad;
      --accent: #8b6cef;
      --accent-2: #b9a7ff;
      --ok: #83e6b2;
      --warn: #ffd37a;
      --bad: #ff8f9c;
      --line: #3b3945;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background:
        linear-gradient(180deg, rgba(32,32,36,.96), rgba(23,23,27,.99)),
        url('/pixel-assets/curated/00_previews/Paper_UI_preview.png');
      color: var(--ink);
      font: 13px/1.45 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      image-rendering: pixelated;
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 18px 22px;
      border-bottom: 1px solid var(--line);
      background: rgba(23, 23, 27, .94);
    }
    h1 { margin: 0; font-size: 18px; letter-spacing: 0; }
    .statusline { color: var(--muted); font-size: 12px; margin-top: 3px; }
    button {
      border: 1px solid #5b4f80;
      background: #2b253b;
      color: var(--ink);
      padding: 8px 11px;
      border-radius: 6px;
      cursor: pointer;
      min-height: 34px;
    }
    button:hover { border-color: var(--accent-2); color: #fff; }
    input, select, textarea {
      width: 100%;
      border: 1px solid var(--line);
      background: #1b1a20;
      color: var(--ink);
      border-radius: 5px;
      padding: 8px;
      font: inherit;
    }
    textarea { min-height: 72px; resize: vertical; }
    label { display: block; color: var(--muted); font-size: 11px; margin: 8px 0 4px; }
    nav {
      display: flex;
      gap: 6px;
      padding: 9px 14px;
      background: rgba(31, 30, 37, .94);
      border-bottom: 1px solid var(--line);
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
    }
    nav button { background: transparent; border-color: transparent; color: var(--muted); }
    nav button.active { background: #302a45; border-color: #5b4f80; color: #fff; }
    .actions { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
    .pill {
      border: 1px solid var(--line);
      background: #1d1c23;
      color: var(--muted);
      border-radius: 999px;
      padding: 5px 8px;
      font-size: 12px;
    }
    .toggle {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      color: var(--muted);
      user-select: none;
    }
    .toggle input { width: auto; }
    main {
      display: grid;
      grid-template-columns: 1.05fr .95fr;
      gap: 14px;
      padding: 14px;
    }
    section {
      border: 1px solid var(--line);
      background: rgba(39, 38, 45, .95);
      border-radius: 6px;
      min-height: 140px;
      overflow: hidden;
    }
    .tab { display: none; }
    .tab.active { display: grid; }
    h2 {
      margin: 0;
      padding: 10px 12px;
      font-size: 13px;
      color: #dcd4ff;
      background: #25232d;
      border-bottom: 1px solid var(--line);
    }
    .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; padding: 10px; }
    .card { background: var(--panel-2); border: 1px solid #403d4d; border-radius: 5px; padding: 10px; min-height: 86px; }
    .mini-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; padding: 10px; }
    .metric { background: #1f1d27; border: 1px solid #403d4d; border-radius: 5px; padding: 9px; min-height: 58px; }
    .metric strong { display: block; color: #fff; font-size: 17px; }
    .name { color: var(--accent); font-weight: 700; }
    .state { margin-top: 6px; color: var(--ok); }
    .warn { color: var(--warn); }
    .bad { color: var(--bad); }
    .muted { color: var(--muted); }
    .changed { border-color: var(--warn) !important; box-shadow: inset 3px 0 0 var(--warn); }
    .presence { display: inline-flex; gap: 4px; flex-wrap: wrap; }
    .dot {
      display: inline-block;
      min-width: 26px;
      text-align: center;
      border-radius: 999px;
      border: 1px solid #4a4656;
      color: var(--muted);
      padding: 2px 6px;
      font-size: 11px;
    }
    .dot.on { color: #101015; background: var(--ok); border-color: var(--ok); }
    .dot.warn { color: #17130a; background: var(--warn); border-color: var(--warn); }
    table { width: 100%; border-collapse: collapse; font-size: 12px; }
    th, td { border-bottom: 1px solid var(--line); padding: 7px 8px; vertical-align: top; text-align: left; }
    th { color: #dcd4ff; background: #25232d; font-weight: 700; position: sticky; top: 0; }
    td code { color: #d6d0e8; }
    .tablewrap { max-height: 420px; overflow: auto; }
    .graph { min-height: 280px; padding: 10px; background: #1b1a20; }
    .graph svg { width: 100%; height: 280px; display: block; }
    pre {
      margin: 0;
      padding: 12px;
      white-space: pre-wrap;
      color: #d6d0e8;
      font: 12px/1.45 ui-monospace, SFMono-Regular, Consolas, monospace;
      max-height: 520px;
      overflow: auto;
    }
    .form { padding: 10px; display: grid; gap: 8px; }
    .wide { grid-column: 1 / -1; }
    .running { color: var(--warn); }
    .okline { color: var(--ok); }
    .errorline { color: var(--bad); }
    @media (max-width: 900px) {
      header {
        flex-direction: column;
        align-items: stretch;
        gap: 10px;
      }
      .actions {
        justify-content: space-between;
      }
      main { grid-template-columns: 1fr; }
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>GOSLO App V1 Console</h1>
      <div class="statusline">Developer console for App shell, tool flow, L2-B, Graphiti, and assets</div>
    </div>
    <div class="actions">
      <span class="pill" id="health">health: loading</span>
      <button onclick="refresh()">Refresh</button>
    </div>
  </header>
  <nav>
    <button class="active" onclick="showTab('overview', this)">Overview</button>
    <button onclick="showTab('live', this)">Live State</button>
    <button onclick="showTab('tools', this)">Tool Flow</button>
    <button onclick="showTab('memory', this)">L2-B / Graphiti</button>
    <button onclick="showTab('assets', this)">Assets</button>
    <button onclick="showTab('selfcheck', this)">Self-check</button>
  </nav>
  <main id="overview" class="tab active">
    <section>
      <h2>Module Rail</h2>
      <div id="modules" class="grid"></div>
    </section>
    <section>
      <h2>Canvas Workspace</h2>
      <pre id="workspace">loading...</pre>
    </section>
    <section>
      <h2>Paper Notes</h2>
      <pre id="paper">loading...</pre>
    </section>
    <section>
      <h2>Photo / Awareness</h2>
      <pre id="photo">loading...</pre>
    </section>
    <section class="wide">
      <h2>L2-B Topology</h2>
      <pre id="l2b">loading...</pre>
    </section>
  </main>
  <main id="live" class="tab">
    <section class="wide">
      <h2>Live Poll</h2>
      <div class="form">
        <div class="actions">
          <label class="toggle"><input id="liveAuto" type="checkbox" checked onchange="setLivePoll(this.checked)" /> Auto poll</label>
          <span class="pill" id="liveMeta">live: loading</span>
          <button onclick="refreshLive()">Poll Now</button>
        </div>
      </div>
      <div id="liveMetrics" class="mini-grid"></div>
    </section>
    <section class="wide">
      <h2>Tool Artifacts</h2>
      <div id="toolArtifacts" class="tablewrap"></div>
    </section>
    <section>
      <h2>Blackboard Live</h2>
      <div id="blackboardLive" class="tablewrap"></div>
    </section>
    <section>
      <h2>IntentWorkspace Live</h2>
      <div id="intentLive" class="tablewrap"></div>
    </section>
    <section class="wide">
      <h2>L2-B Live Graph</h2>
      <div id="l2bGraph" class="graph">loading...</div>
    </section>
    <section>
      <h2>RefBinding Registry</h2>
      <div id="refLive" class="tablewrap"></div>
    </section>
    <section>
      <h2>Live JSON</h2>
      <pre id="liveJson">loading...</pre>
    </section>
  </main>
  <main id="tools" class="tab">
    <section class="wide">
      <h2>Tool Cabinet</h2>
      <div id="toolcabinet" class="grid"></div>
    </section>
    <section>
      <h2>Camera Flow</h2>
      <div class="form">
        <label>camera mode</label>
        <select id="cameraMode">
          <option value="preview">preview</option>
          <option value="photo_ready">photo_ready</option>
          <option value="capture_locked">capture_locked</option>
          <option value="off">off</option>
        </select>
        <label>candidate subject uuid</label>
        <input id="cameraCandidate" value="obj_web_console" />
        <div class="actions">
          <button onclick="postJson('/api/app/camera/mode', {mode: fieldValue('cameraMode')})">Set Mode</button>
          <button onclick="postJson('/api/app/camera/capture-request', {candidate_subject_uuid: fieldValue('cameraCandidate')})">Request Capture</button>
          <button onclick="postJson('/api/app/test/photo-preview', {photo_id: 'ph_web_console'})">Sim Preview</button>
        </div>
      </div>
    </section>
    <section>
      <h2>Focus / BoundaryBox</h2>
      <div class="form">
        <label>focus id</label>
        <input id="focusId" value="fc_web_console" />
        <label>bbox id</label>
        <input id="bboxId" value="bb_web_console" />
        <div class="actions">
          <button onclick="postJson('/api/app/test/focus', {focus_id: fieldValue('focusId'), action:'anchored'})">Anchor Focus</button>
          <button onclick="postJson('/api/app/test/focus', {focus_id: fieldValue('focusId'), action:'released'})">Release Focus</button>
          <button onclick="postJson('/api/app/test/bbox', {bbox_id: fieldValue('bboxId'), action:'placed'})">Place BBox</button>
          <button onclick="postJson('/api/app/test/bbox', {bbox_id: fieldValue('bboxId'), action:'removed'})">Remove BBox</button>
        </div>
      </div>
    </section>
    <section>
      <h2>Paper Note Inputs</h2>
      <div class="form">
        <label>note title</label>
        <input id="noteTitle" value="Web console paper note" />
        <label>note body</label>
        <textarea id="noteBody">Nanobot fixture report for App V1 testing.</textarea>
        <div class="actions">
          <button onclick="postJson('/api/app/nanobot/report', {title:fieldValue('noteTitle'), body:fieldValue('noteBody'), task_id:'web_console'})">Nanobot Note</button>
          <button onclick="postJson('/api/app/calendar/draft', {title:fieldValue('noteTitle'), action:'create'})">Calendar Draft</button>
        </div>
      </div>
    </section>
    <section>
      <h2>Last Action</h2>
      <pre id="lastAction">no action yet</pre>
    </section>
  </main>
  <main id="memory" class="tab">
    <section>
      <h2>Graphiti Core</h2>
      <div class="form">
        <label>partition</label>
        <select id="graphitiPartition">
          <option value="goslo">goslo</option>
          <option value="maid">maid</option>
          <option value="scene">scene</option>
          <option value="user">user</option>
        </select>
        <label>query</label>
        <input id="graphitiQuery" value="GOSLO app v1" />
        <label>episode body</label>
        <textarea id="episodeBody">App console dry-run episode.</textarea>
        <div class="actions">
          <button onclick="loadGraphitiStatus()">Status</button>
          <button onclick="postJson('/api/graphiti/search', {query:fieldValue('graphitiQuery'), partition:fieldValue('graphitiPartition')})">Search</button>
          <button onclick="postJson('/api/graphiti/episode/draft', {name:'app_console_episode', body:fieldValue('episodeBody'), partition:fieldValue('graphitiPartition')})">Draft Episode</button>
          <button onclick="postJson('/api/graphiti/episode', {name:'app_console_episode', body:fieldValue('episodeBody'), partition:fieldValue('graphitiPartition'), dry_run:true})">Dry Run Write</button>
        </div>
      </div>
    </section>
    <section>
      <h2>Graphiti Result</h2>
      <pre id="graphiti">loading...</pre>
    </section>
    <section class="wide">
      <h2>L2-B Topology</h2>
      <pre id="l2b2">loading...</pre>
    </section>
  </main>
  <main id="assets" class="tab">
    <section class="wide">
      <h2>Asset Map</h2>
      <pre id="assetMap">loading...</pre>
    </section>
  </main>
  <main id="selfcheck" class="tab">
    <section>
      <h2>App V1 Self-check</h2>
      <div class="form">
        <div id="selfcheckStatus" class="muted">Ready to run.</div>
        <button onclick="runSelfCheck()">Run Self-check</button>
      </div>
    </section>
    <section>
      <h2>Self-check Result</h2>
      <pre id="selfcheckResult">not run</pre>
    </section>
  </main>
  <script>
    let liveTimer = null;
    let liveSignatures = {};

    async function getJson(url) {
      const res = await fetch(url, {cache: 'no-store'});
      if (!res.ok) throw new Error(`${url}: ${res.status}`);
      return res.json();
    }
    async function postJson(url, body) {
      const res = await fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body || {})
      });
      const data = await res.json();
      document.getElementById('lastAction').textContent = JSON.stringify(data, null, 2);
      await refresh();
      await refreshLive();
      return data;
    }
    function fieldValue(id) { return document.getElementById(id).value; }
    function esc(value) {
      return String(value ?? '').replace(/[&<>"']/g, ch => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
      }[ch]));
    }
    function clip(value, maxLen = 180) {
      const text = typeof value === 'string' ? value : JSON.stringify(value);
      return text.length > maxLen ? `${text.slice(0, maxLen)}...` : text;
    }
    function signature(value) { return JSON.stringify(value); }
    function changed(key, value) {
      const next = signature(value);
      const prior = liveSignatures[key];
      return prior !== undefined && prior !== next;
    }
    function collectLiveSignatures(state) {
      const out = {};
      (state.blackboard?.keys || []).forEach(row => out[`bb:${row.key}`] = signature(row.value));
      (state.intent_workspace?.refs || []).forEach(row => out[`iw:${row.ref_id}`] = signature(row));
      (state.refs?.refs || []).forEach(row => out[`ref:${row.ref_id}`] = signature(row));
      (state.l2b?.nodes || []).forEach(row => out[`l2b:${row.uuid}`] = signature(row));
      (state.tool_artifacts || []).forEach(row => out[`tool:${row.tool_id}`] = signature(row.locations));
      return out;
    }
    function presenceDots(locations) {
      const map = [
        ['BB', locations.blackboard?.present],
        ['IW', locations.intent_workspace?.present],
        ['REF', locations.ref_registry?.present],
        ['L2B', locations.l2b?.present],
      ];
      return `<span class="presence">${map.map(([label, on]) =>
        `<span class="dot ${on ? 'on' : ''}">${label}</span>`).join('')}</span>`;
    }
    function renderMetrics(state) {
      const metrics = [
        ['BB keys', `${state.blackboard.present_count}/${state.blackboard.declared_count}`],
        ['Intent refs', state.intent_workspace.ref_count],
        ['RefBindings', state.refs.metrics.total_refs],
        ['L2-B nodes', state.l2b.node_count],
      ];
      document.getElementById('liveMetrics').innerHTML = metrics.map(([label, value]) =>
        `<div class="metric"><strong>${esc(value)}</strong><span class="muted">${esc(label)}</span></div>`
      ).join('');
    }
    function renderToolArtifacts(rows) {
      document.getElementById('toolArtifacts').innerHTML =
        `<table><thead><tr><th>Tool</th><th>State</th><th>Surfaces</th><th>Expected Flow</th><th>Scenario Checks</th></tr></thead><tbody>` +
        rows.map(row => {
          const cls = changed(`tool:${row.tool_id}`, row.locations) ? 'changed' : '';
          return `<tr class="${cls}"><td><code>${esc(row.tool_id)}</code><br>${esc(row.label)}</td>` +
            `<td>${esc(row.status)}</td><td>${presenceDots(row.locations)}</td>` +
            `<td>${esc(row.expectation)}</td>` +
            `<td>${(row.scenario_checks || []).map(esc).join('<br>')}</td></tr>`;
        }).join('') + `</tbody></table>`;
    }
    function renderBlackboard(bb) {
      const rows = [...(bb.keys || [])].sort((a, b) => {
        if (a.exists !== b.exists) return a.exists ? -1 : 1;
        return a.key.localeCompare(b.key);
      });
      document.getElementById('blackboardLive').innerHTML =
        `<table><thead><tr><th>Key</th><th>Writer</th><th>Present</th><th>Summary</th><th>Value</th></tr></thead><tbody>` +
        rows.map(row => {
          const cls = changed(`bb:${row.key}`, row.value) ? 'changed' : '';
          return `<tr class="${cls}"><td><code>${esc(row.key)}</code><br><span class="muted">${esc(row.scope)} / ${esc(row.type_hint)}</span></td>` +
            `<td>${esc(row.writer)}</td><td>${row.exists ? '<span class="dot on">yes</span>' : '<span class="dot">no</span>'}</td>` +
            `<td>${esc(row.summary)}</td><td><code>${esc(clip(row.value, 220))}</code></td></tr>`;
        }).join('') + `</tbody></table>`;
    }
    function renderIntentWorkspace(iw) {
      const rows = iw.refs || [];
      document.getElementById('intentLive').innerHTML =
        `<table><thead><tr><th>Ref</th><th>Role</th><th>Origin</th><th>Workspace</th><th>Node/Photo</th><th>Expires</th></tr></thead><tbody>` +
        rows.map(row => {
          const cls = changed(`iw:${row.ref_id}`, row) ? 'changed' : '';
          const expires = row.expires_in_seconds === null ? 'manual' : `${row.expires_in_seconds}s`;
          return `<tr class="${cls}"><td><code>${esc(row.ref_id)}</code><br><span class="muted">${esc(row.kind)} / ${esc(row.payload_source)}</span></td>` +
            `<td>${esc(row.role || row.ui_kind || '')}</td><td>${esc(row.origin)}</td>` +
            `<td>${esc(row.workspace_id || row.owner_id || 'parent')}</td>` +
            `<td>${esc(row.photo_id || row.related_node_uuid || '')}</td><td>${esc(expires)}</td></tr>`;
        }).join('') + `</tbody></table>`;
    }
    function renderRefs(refs) {
      const rows = refs.refs || [];
      document.getElementById('refLive').innerHTML =
        `<table><thead><tr><th>Ref</th><th>Kind</th><th>Target</th><th>Label</th><th>Source Event</th></tr></thead><tbody>` +
        rows.map(row => {
          const cls = changed(`ref:${row.ref_id}`, row) ? 'changed' : '';
          return `<tr class="${cls}"><td><code>${esc(row.ref_id)}</code><br><span class="muted">rev ${esc(row.revision)}</span></td>` +
            `<td>${esc(row.kind)}</td><td>${esc(row.target_kind)} ${esc(row.target_id || '')}</td>` +
            `<td>${esc(row.label)}</td><td><code>${esc(row.source_event_id)}</code></td></tr>`;
        }).join('') + `</tbody></table>`;
    }
    function renderL2bGraph(l2b) {
      const nodes = l2b.nodes || [];
      const edges = l2b.edges || [];
      if (!nodes.length) {
        document.getElementById('l2bGraph').innerHTML = '<div class="muted">No L2-B nodes yet. Sim Photo Preview will create a PHOTO node.</div>';
        return;
      }
      const w = 900, h = 280, cx = w / 2, cy = h / 2, r = Math.min(310, 58 + nodes.length * 18);
      const pos = {};
      nodes.forEach((node, i) => {
        const angle = (Math.PI * 2 * i) / Math.max(nodes.length, 1) - Math.PI / 2;
        pos[node.uuid] = {
          x: nodes.length === 1 ? cx : cx + Math.cos(angle) * r,
          y: nodes.length === 1 ? cy : cy + Math.sin(angle) * Math.min(r, 105),
        };
      });
      const color = kind => kind === 'photo' ? '#b9a7ff' : (kind === 'object' ? '#83e6b2' : '#ffd37a');
      const edgeSvg = edges.map(edge => {
        const a = pos[edge.source], b = pos[edge.target];
        if (!a || !b) return '';
        return `<line x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" stroke="#5b4f80" stroke-width="1.5" opacity=".75" />`;
      }).join('');
      const nodeSvg = nodes.map(node => {
        const p = pos[node.uuid];
        const cls = changed(`l2b:${node.uuid}`, node) ? ' changed-node' : '';
        const label = esc(node.label || node.uuid);
        return `<g class="${cls}"><circle cx="${p.x}" cy="${p.y}" r="24" fill="${color(node.kind)}" opacity=".92" />` +
          `<text x="${p.x}" y="${p.y + 4}" text-anchor="middle" font-size="10" fill="#101015">${esc(node.kind || 'node')}</text>` +
          `<text x="${p.x}" y="${p.y + 40}" text-anchor="middle" font-size="11" fill="#dcddde">${label.slice(0, 34)}</text></g>`;
      }).join('');
      document.getElementById('l2bGraph').innerHTML =
        `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="L2-B graph">${edgeSvg}${nodeSvg}</svg>`;
    }
    async function refreshLive() {
      const state = await getJson('/api/app/live-state?limit=80');
      document.getElementById('liveMeta').textContent =
        `live: seq ${state.sequence} / ${new Date(state.generated_at * 1000).toLocaleTimeString()}`;
      renderMetrics(state);
      renderToolArtifacts(state.tool_artifacts || []);
      renderBlackboard(state.blackboard || {});
      renderIntentWorkspace(state.intent_workspace || {});
      renderRefs(state.refs || {});
      renderL2bGraph(state.l2b || {});
      document.getElementById('liveJson').textContent = JSON.stringify(state, null, 2);
      liveSignatures = collectLiveSignatures(state);
      return state;
    }
    function setLivePoll(enabled) {
      if (liveTimer) clearInterval(liveTimer);
      liveTimer = null;
      if (enabled) liveTimer = setInterval(() => refreshLive().catch(console.error), 1200);
    }
    function showTab(id, btn) {
      document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
      document.getElementById(id).classList.add('active');
      document.querySelectorAll('nav button').forEach(el => el.classList.remove('active'));
      btn.classList.add('active');
    }
    function card(status) {
      const health = status.health === 'ok' ? 'state' : 'state warn';
      return `<div class="card"><div class="name">${status.module_id}</div>` +
        `<div class="${health}">${status.state}</div>` +
        `<div class="muted">${status.summary || ''}</div></div>`;
    }
    function toolCard(tool) {
      const stateClass = tool.enabled ? 'state' : 'state bad';
      return `<div class="card"><div class="name">${tool.label}</div>` +
        `<div class="${stateClass}">${tool.state}</div>` +
        `<div class="muted">${tool.summary}</div>` +
        `<div class="muted">asset: ${tool.asset_slot}</div></div>`;
    }
    async function refresh() {
      const [health, canvas, l2b, graphitiStatus] = await Promise.all([
        getJson('/health'),
        getJson('/api/app/canvas'),
        getJson('/api/l2b/snapshot?limit=60'),
        getJson('/api/graphiti/status')
      ]);
      document.getElementById('health').textContent = `health: ${health.service} / ${health.mode}`;
      document.getElementById('modules').innerHTML = canvas.module_statuses.map(card).join('');
      document.getElementById('toolcabinet').innerHTML = canvas.tool_cabinet.map(toolCard).join('');
      document.getElementById('workspace').textContent = JSON.stringify({
        active_workspace_id: canvas.active_workspace_id,
        workspaces: canvas.workspaces
      }, null, 2);
      document.getElementById('paper').textContent = JSON.stringify(canvas.paper_notes, null, 2);
      document.getElementById('photo').textContent = JSON.stringify(canvas.photo_refs, null, 2);
      document.getElementById('l2b').textContent = JSON.stringify(l2b, null, 2);
      document.getElementById('l2b2').textContent = JSON.stringify(l2b, null, 2);
      document.getElementById('graphiti').textContent = JSON.stringify(graphitiStatus, null, 2);
      document.getElementById('assetMap').textContent = JSON.stringify(canvas.asset_manifest, null, 2);
    }
    async function loadGraphitiStatus() {
      document.getElementById('graphiti').textContent =
        JSON.stringify(await getJson('/api/graphiti/status'), null, 2);
    }
    async function runSelfCheck() {
      const status = document.getElementById('selfcheckStatus');
      const output = document.getElementById('selfcheckResult');
      status.className = 'running';
      status.textContent = 'Running self-check...';
      output.textContent = 'running...';
      try {
        const res = await fetch('/api/app/self-check', {method:'POST'});
        if (!res.ok) throw new Error(`self-check failed: ${res.status}`);
        const data = await res.json();
        output.textContent = JSON.stringify(data, null, 2);
        status.className = data.passed ? 'okline' : 'errorline';
        status.textContent = data.passed ? 'Self-check passed.' : 'Self-check completed with failures.';
        await refresh();
        await refreshLive();
      } catch (err) {
        status.className = 'errorline';
        status.textContent = 'Self-check failed to run.';
        output.textContent = err.message;
      }
    }
    refresh()
      .then(() => refreshLive())
      .then(() => setLivePoll(document.getElementById('liveAuto').checked))
      .catch(err => {
        document.getElementById('modules').innerHTML =
          `<div class="card"><div class="name">error</div><div class="state warn">${err.message}</div></div>`;
      });
  </script>
</body>
</html>"""


def _visual_tool_asset_metadata_from_headers(request: Request) -> dict[str, Any]:  # type: ignore[valid-type]
    """Parse optional visual-tool upload metadata from App HTTP headers."""
    meta: dict[str, Any] = {
        "tool_id": request.headers.get("X-Parrot-Tool-Id", ""),
        "tool_kind": request.headers.get("X-Parrot-Tool-Kind", ""),
        "interaction_phase": request.headers.get("X-Parrot-Tool-Phase", ""),
        "source_surface": request.headers.get("X-Parrot-Source-Surface", "app_ar_overlay"),
        "source_id": request.headers.get("X-Parrot-Source-Id", ""),
        "description": request.headers.get("X-Parrot-Description", ""),
    }
    timebase = _json_header(request, "X-Parrot-Timebase")
    if isinstance(timebase, dict):
        meta["timebase"] = timebase
    region = _json_header(request, "X-Parrot-Region")
    if isinstance(region, dict):
        meta["region"] = region
    return meta


def _json_header(request: Request, name: str) -> Any:  # type: ignore[valid-type]
    raw = request.headers.get(name, "")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _body_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on", "enabled"}


def _body_bool_or_none(value: Any) -> bool | None:
    if value is None:
        return None
    return _body_bool(value, False)


def _body_float(value: Any, default: float) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _body_float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


create_app = build_app

__all__ = ["build_app", "create_app"]
