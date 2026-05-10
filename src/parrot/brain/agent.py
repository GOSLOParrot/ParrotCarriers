"""Brain Agent — the real-time voice AI entry point.

Architecture:
  LiveKit AgentServer (manages room lifecycle)
    → rtc_session handler
      → Bus mount pipeline (preflight → L2 Redis → L1 AgentSession → heartbeat)
      → Gemini RealtimeModel (voice in/out via LiveKit Room)
      → ParrotAssistant (personality + tools: fly_to, animate, dispatch_task)
      → DataChannel telemetry receiver (parrot.telemetry / parrot.event)
      → Scheduler result listener (CH_SCHEDULER_TO_BRAIN → generate_reply)

Usage:
  # Console mode (no LiveKit Server needed — great for local testing):
  python -m parrot.brain.agent console

  # Dev mode (connects to LiveKit Server, auto-creates room):
  python -m parrot.brain.agent dev
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from livekit import agents
from livekit.agents import Agent, AgentServer, AgentSession, room_io
from livekit.agents.llm import ChatMessage
from livekit.agents.voice.events import ConversationItemAddedEvent, UserInputTranscribedEvent
from livekit.plugins import google

from parrot.brain.soul import get_instructions
from parrot.brain.telemetry_receiver import attach_telemetry_receiver
from parrot.brain.vision.state import attach_video_state_rpc
from parrot.brain.tools import tools_for_active_model
from parrot.bus.manifest import ModuleManifest
from parrot.bus.mounting import ModuleMount
from parrot.shared.config import ParrotConfig
from parrot.shared.constants import CH_SCHEDULER_TO_BRAIN, HASH_GOSLO_MODE
from parrot.shared.redis_client import get_redis
from parrot.shared.types import Layer, ModuleType

logger = logging.getLogger("parrot.brain.agent")


# region agent log
_AGENT_DEBUG_LOG = Path(os.getenv("PARROT_AGENT_DEBUG_LOG", "debug-5bc081.log"))


def _agent_log(run_id: str, hypothesis_id: str, location: str, message: str, data: dict) -> None:
    """Temporary NDJSON evidence for the current Cursor debug session."""
    payload = {
        "sessionId": "5bc081",
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    try:
        with _AGENT_DEBUG_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass


# endregion


class ParrotAssistant(Agent):
    """Parrot personality with function tools for AR interaction."""

    def __init__(self) -> None:
        super().__init__(
            instructions=get_instructions(),
            tools=tools_for_active_model(),
        )


def _create_manifest() -> ModuleManifest:
    return ModuleManifest(
        module_id="brain-agent",
        module_type=ModuleType.CORE,
        layers=[Layer.L1, Layer.L2],
        livekit_identity="brain",
    )


server = AgentServer()


# region pipeline selection (Sprint 4 Phase 5+ Line B, 2026-05-04)
#
# `PARROT_LLM_PIPELINE=line_a / line_b` env-gates the AgentSession
# construction. Default = line_a (Gemini Live RealtimeModel — Phase 4 baseline,
# fully validated). line_b uses livekit-agents STT-LLM-TTS pipeline with
# Gemini text API + google.STT + google.TTS + silero.VAD (per
# sprint4_pre_entry §双管线适配边界 + GAP-2 §options E trade-off).
#
# Failure mode: any unknown PARROT_LLM_PIPELINE value or any missing Line B
# dependency raises explicitly at session build time. NO silent fallback to
# line_a (per Phase 5+ chat task §2 spec); a misconfigured Line B run must
# surface, not silently masquerade as Line A.
#
# This is the ONLY differential between Line A and Line B. All other wiring
# (transcript listener, cognitive_state_tracker, DSG triggers, observers,
# selection-C tool wrappers, etc.) is pipeline-agnostic.

_PIPELINE_LINE_A = "line_a"
_PIPELINE_LINE_B = "line_b"
_DEFAULT_PIPELINE = _PIPELINE_LINE_A


def _resolve_pipeline() -> str:
    raw = os.getenv("PARROT_LLM_PIPELINE", _DEFAULT_PIPELINE).strip().lower()
    if raw not in (_PIPELINE_LINE_A, _PIPELINE_LINE_B):
        raise RuntimeError(
            f"PARROT_LLM_PIPELINE={raw!r} invalid; expected {_PIPELINE_LINE_A!r} "
            f"or {_PIPELINE_LINE_B!r} (default {_DEFAULT_PIPELINE!r})."
        )
    return raw


def _build_session(pipeline: str, config: ParrotConfig) -> AgentSession:
    """Construct AgentSession for the requested pipeline.

    line_a: google.realtime.RealtimeModel (Gemini Live, multimodal native).
    line_b: google.STT + google.LLM (Gemini text API) + google.TTS + silero.VAD.

    Both yield an AgentSession that emits the same agent_state_changed /
    user_input_transcribed / conversation_item_added events the rest of the
    Brain wire-up (cognitive_state_tracker, transcript extractor,
    context_injector C2/C3/C4) consumes.
    """
    if pipeline == _PIPELINE_LINE_A:
        logger.info(
            "Brain pipeline=line_a (Gemini Live): model=%s voice=%s",
            config.gemini.live_model, config.gemini.live_voice,
        )
        return AgentSession(
            llm=google.realtime.RealtimeModel(
                voice=config.gemini.live_voice,
                model=config.gemini.live_model,
                api_key=config.google_api_key or None,
            ),
        )

    # line_b — STT-LLM-TTS pipeline (no fallback if any plugin import fails).
    #
    # Auth note (FINDING-LB-AUTH, Sprint 4 Phase 5+ Line B 2026-05-04):
    #   * google.LLM (Gemini text API)   → uses ``api_key`` (GOOGLE_API_KEY env)
    #   * google.STT / google.TTS        → use Google Cloud ADC; require
    #     ``GOOGLE_APPLICATION_CREDENTIALS`` to point at a service account
    #     JSON with Speech-to-Text + Text-to-Speech roles.
    # If ADC is unset, livekit-plugins-google will surface the credentials
    # error at first STT/TTS invocation (after Room connect), not at Session
    # construction. Surface this fast at boot so misconfigured deployments
    # do not appear "connected but mute".
    from livekit.plugins import silero

    from parrot.brain.line_profile import active_lineb_runtime_settings

    lineb_settings = active_lineb_runtime_settings()
    text_model = lineb_settings.llm_model
    stt_model = lineb_settings.stt_model
    languages = list(lineb_settings.stt_languages) or ["cmn-CN"]
    tts_voice = lineb_settings.tts_voice
    tts_lang = lineb_settings.tts_language

    api_key = config.google_api_key or None
    if not api_key:
        raise RuntimeError(
            "PARROT_LLM_PIPELINE=line_b requires GOOGLE_API_KEY for google.LLM "
            "(Gemini text API)."
        )
    if not (
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        or os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    ):
        logger.warning(
            "PARROT_LLM_PIPELINE=line_b: GOOGLE_APPLICATION_CREDENTIALS not set — "
            "google.STT / google.TTS will fail at first invocation. Set ADC to "
            "a service account JSON with Speech-to-Text + Text-to-Speech roles."
        )

    logger.info(
        "Brain pipeline=line_b (STT-LLM-TTS): profile=%s llm=%s stt=%s lang=%s tts_voice=%s",
        lineb_settings.line_profile_id, text_model, stt_model, languages, tts_voice,
    )
    return AgentSession(
        vad=silero.VAD.load(),
        stt=google.STT(model=stt_model, languages=languages),
        llm=google.LLM(model=text_model, api_key=api_key),
        tts=google.TTS(language=tts_lang, voice_name=tts_voice),
    )


# endregion


async def _set_goslo_mode(mode: str, session_id: str = "") -> None:
    """Write GOSLO body-mode signal to Redis Hash."""
    from datetime import datetime, timezone

    r = await get_redis()
    await r.hset(
        HASH_GOSLO_MODE,
        mapping={
            "active_body": mode,
            "live_session_id": session_id,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )


def _attach_transcript_listener_to_session(
    session: AgentSession,
    pipeline: str = _PIPELINE_LINE_A,
) -> None:
    """LLM 侧用户转写与助手文本: 打终端 + 喂 DSG Ingest.

    Sprint 2 T7 wiring. **Pipeline-agnostic** (Sprint 4 Phase 5+ Line B,
    2026-05-04): both Gemini Live (Line A) and STT-LLM-TTS (Line B) emit
    the same ``user_input_transcribed`` / ``conversation_item_added``
    events on AgentSession, so this hook works for both.

    Two sinks per event (order matters — terminal log runs even if the
    Ingest path is missing a Graphiti/L2-B dep, because the logs are what
    ops actually watches):

        1. terminal print + logger.info            (Sprint 1 behaviour)
        2. TranscriptExtractor.feed_transcript     (Sprint 2 T7)

    The extractor drops status/context echoes itself (see sprint2_plan
    §9.N3), so we just forward everything we see here.

    The terminal label still says ``[Gemini·…]`` because the LLM provider
    in both Line A and Line B is Gemini (Realtime vs text API). When
    DeepSeek V4 / other LLMs land as a third Line, revisit the label.
    """
    try:
        from parrot.dsg.ingest.transcript_extractor import (
            get_transcript_extractor,
        )
        extractor = get_transcript_extractor()
    except Exception:
        extractor = None
        logger.warning("transcript extractor unavailable — DSG ingest disabled")

    @session.on("user_input_transcribed")
    def _on_user_transcribed(ev: UserInputTranscribedEvent) -> None:
        if not ev.is_final:
            return
        if pipeline == _PIPELINE_LINE_B:
            try:
                from parrot.brain.lineb_audio_guard import classify_mic_input

                decision = classify_mic_input(asr_text=ev.transcript)
                _schedule_lineb_voice_activity_reaction("user_input_transcribed")
                if decision.turn_decision == "agent_echo":
                    logger.info(
                        "LineB suppressed mic fragment as agent echo: %s",
                        decision.as_json(),
                    )
                    return
            except Exception:
                logger.exception("LineB mic input classification failed")
        line = f"[Gemini·用户] {ev.transcript}"
        logger.info("%s", line)
        print(f"\n{line}\n", flush=True)
        if extractor is not None:
            try:
                extractor.feed_transcript(ev.transcript, "user")
            except Exception:
                logger.exception("extractor.feed_transcript(user) failed")

    @session.on("conversation_item_added")
    def _on_conversation_item(ev: ConversationItemAddedEvent) -> None:
        item = ev.item
        if not isinstance(item, ChatMessage):
            return
        if item.role != "assistant":
            return
        text = item.text_content
        if not text:
            return
        if pipeline == _PIPELINE_LINE_B:
            try:
                from parrot.brain.line_profile import active_lineb_runtime_settings
                from parrot.brain.lineb_audio_guard import register_tts_segment

                register_tts_segment(
                    text_summary=text,
                    duration_s=_estimate_tts_duration_s(text),
                    tts_voice=active_lineb_runtime_settings().tts_voice,
                    conversation_turn_id=str(getattr(item, "id", "") or ""),
                    acoustic_refs={"source": "conversation_item_added"},
                )
                _schedule_lineb_voice_activity_reaction("conversation_item_added")
            except Exception:
                logger.exception("LineB TTS segment registration failed")
        line = f"[Gemini·鹦鹉] {text}"
        logger.info("%s", line)
        print(f"\n{line}\n", flush=True)
        if extractor is not None:
            try:
                extractor.feed_transcript(text, "assistant")
            except Exception:
                logger.exception("extractor.feed_transcript(assistant) failed")


def _estimate_tts_duration_s(text: str) -> float:
    stripped = str(text or "").strip()
    if not stripped:
        return 0.35
    return max(0.35, min(24.0, len(stripped) / 7.5))


def _schedule_lineb_voice_activity_reaction(reason: str) -> None:
    try:
        from parrot.brain.lineb_model_reaction import (
            dispatch_latest_lineb_voice_activity_to_model,
        )

        asyncio.create_task(
            dispatch_latest_lineb_voice_activity_to_model(reason=reason)
        )
    except RuntimeError:
        logger.debug("LineB voice activity reaction skipped: no running event loop")
    except Exception:
        logger.exception("LineB voice activity reaction scheduling failed")


async def _generate_reply_after_current_speech(
    session: AgentSession,
    instructions: str,
    reason: str,
) -> bool:
    """Call Gemini programmatic speech without overlapping the active turn.

    Gemini Live + LiveKit Agents can time out or cancel tool calls if multiple
    server-initiated generate_reply calls race with current speech/user audio.
    Keep explicit Brain prompts serialized so startup greetings and status
    notices do not steal the user's first turn.
    """
    from parrot.brain.session_policy import should_generate_reply

    if not should_generate_reply(reason):
        return False

    current_speech = getattr(session, "current_speech", None)
    if current_speech is not None:
        logger.debug("%s: waiting for current_speech before generate_reply", reason)
        await current_speech
    await session.generate_reply(instructions=instructions)
    return True


def _attach_menu_rpc(room: "Any") -> None:
    """Expose menu/workspace business RPCs to Unity.

    reason: The existing Brain core interfaces are Python objects
    (MenuRegistry/PresetLoader/WorkspaceRegistry). Unity needs a minimal
    LiveKit RPC boundary to list/apply/save menu selections without learning
    Blackboard internals or reconnecting the room on 2DWorkspace switches.
    """
    import json as _json
    from dataclasses import asdict, is_dataclass

    def _to_wire(obj: "Any") -> "Any":
        if is_dataclass(obj):
            return _to_wire(asdict(obj))
        if isinstance(obj, dict):
            return {str(k): _to_wire(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [_to_wire(v) for v in obj]
        if hasattr(obj, "name") and hasattr(obj, "value"):
            return getattr(obj, "name")
        return obj

    def _dump(obj: "Any") -> str:
        return _json.dumps(_to_wire(obj), ensure_ascii=False)

    def _payload(data: "Any") -> dict:
        try:
            raw = _json.loads(data.payload) if data.payload else {}
        except Exception:
            raw = {}
        return raw if isinstance(raw, dict) else {}

    def _payload_bool(payload: dict, key: str, default: bool) -> bool:
        value = payload.get(key)
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "on", "enabled"}

    def _payload_bool_or_none(payload: dict, key: str) -> bool | None:
        if payload.get(key) is None:
            return None
        return _payload_bool(payload, key, False)

    def _payload_float(payload: dict, key: str, default: float) -> float:
        try:
            return float(payload.get(key, default))
        except (TypeError, ValueError):
            return default

    def _payload_float_or_none(payload: dict, key: str) -> float | None:
        if payload.get(key) is None:
            return None
        try:
            return float(payload.get(key))
        except (TypeError, ValueError):
            return None

    @room.local_participant.register_rpc_method("listMenuBlocks")
    async def _list_menu_blocks(data: "Any") -> str:
        from parrot.brain.menu_registry import get_menu_registry

        return _dump({"status": "ok", "snapshot": get_menu_registry().list_blocks()})

    @room.local_participant.register_rpc_method("getRoomSettingSnapshot")
    async def _get_room_setting_snapshot(data: "Any") -> str:
        from parrot.brain.app_first_version import AppFirstVersionFacade

        payload = _payload(data)
        snapshot = AppFirstVersionFacade().room_setting_snapshot(
            str(payload.get("room_profile_id") or "") or None
        )
        return _dump({"status": "ok", "snapshot": snapshot.as_json()})

    @room.local_participant.register_rpc_method("previewRoomProfile")
    async def _preview_room_profile(data: "Any") -> str:
        from parrot.brain.app_first_version import AppFirstVersionFacade

        payload = _payload(data)
        draft = payload.get("room_profile") if isinstance(payload.get("room_profile"), dict) else payload
        return _dump({"status": "ok", "preview": AppFirstVersionFacade().preview_room_profile(draft)})

    @room.local_participant.register_rpc_method("newRoomProfile")
    async def _new_room_profile(data: "Any") -> str:
        from parrot.brain.app_first_version import AppFirstVersionFacade

        payload = _payload(data)
        draft = AppFirstVersionFacade().new_room_profile(
            base_id=str(payload.get("base_id") or "") or None,
            display_name=str(payload.get("display_name") or "") or None,
        )
        return _dump({"status": "ok", "draft": draft})

    @room.local_participant.register_rpc_method("saveRoomProfile")
    async def _save_room_profile(data: "Any") -> str:
        from parrot.brain.app_first_version import AppFirstVersionFacade

        payload = _payload(data)
        draft = payload.get("room_profile") if isinstance(payload.get("room_profile"), dict) else payload
        saved = AppFirstVersionFacade().save_room_profile(draft)
        return _dump({"status": "ok", "saved": saved})

    @room.local_participant.register_rpc_method("applyRoomProfile")
    async def _apply_room_profile(data: "Any") -> str:
        from parrot.brain.app_first_version import AppFirstVersionFacade

        payload = _payload(data)
        draft_or_id = payload.get("room_profile") or payload.get("room_profile_id") or payload
        applied = AppFirstVersionFacade().apply_room_profile(
            draft_or_id,
            experience_mode=payload.get("experience_mode"),
        )
        return _dump({"status": "ok" if applied.get("success") else "error", "result": applied})

    @room.local_participant.register_rpc_method("setLineBAudioRoutePolicy")
    async def _set_lineb_audio_route_policy(data: "Any") -> str:
        from parrot.brain.app_first_version import AppFirstVersionFacade

        payload = _payload(data)
        policy = AppFirstVersionFacade().set_lineb_audio_route_policy(
            input_route=str(payload.get("input_route") or "unknown"),
            output_route=str(payload.get("output_route") or "unknown"),
            microphone_enabled=_payload_bool(payload, "microphone_enabled", True),
            speaker_output_enabled=_payload_bool_or_none(payload, "speaker_output_enabled"),
            echo_handling_mode=str(payload.get("echo_handling_mode") or "") or None,
            voiceprint_enabled=_payload_bool(payload, "voiceprint_enabled", False),
            speaker_state=str(payload.get("speaker_state") or "unknown"),
            source=str(payload.get("source") or "livekit_rpc"),
        )
        return _dump({"status": "ok", "policy": policy})

    @room.local_participant.register_rpc_method("registerLineBTtsSegment")
    async def _register_lineb_tts_segment(data: "Any") -> str:
        from parrot.brain.app_first_version import AppFirstVersionFacade

        payload = _payload(data)
        acoustic_refs = payload.get("acoustic_refs")
        segment = AppFirstVersionFacade().register_lineb_tts_segment(
            text_summary=str(payload.get("text_summary") or payload.get("text") or ""),
            duration_s=_payload_float(payload, "duration_s", 0.5),
            started_at=_payload_float_or_none(payload, "started_at"),
            tts_voice=str(payload.get("tts_voice") or payload.get("voice") or ""),
            voiceprint_hash=str(payload.get("voiceprint_hash") or ""),
            conversation_turn_id=str(payload.get("conversation_turn_id") or ""),
            acoustic_refs=acoustic_refs if isinstance(acoustic_refs, dict) else None,
        )
        return _dump({"status": "ok", "segment": segment})

    @room.local_participant.register_rpc_method("classifyLineBMicInput")
    async def _classify_lineb_mic_input(data: "Any") -> str:
        from parrot.brain.app_first_version import AppFirstVersionFacade

        payload = _payload(data)
        decision = AppFirstVersionFacade().classify_lineb_mic_input(
            observed_at=_payload_float_or_none(payload, "observed_at"),
            duration_s=_payload_float(payload, "duration_s", 0.0),
            asr_text=str(payload.get("asr_text") or payload.get("text") or ""),
            voiceprint_hash=str(payload.get("voiceprint_hash") or ""),
            echo_score=_payload_float_or_none(payload, "echo_score"),
        )
        return _dump({"status": "ok", "decision": decision})

    @room.local_participant.register_rpc_method("applyMenuSelection")
    async def _apply_menu_selection(data: "Any") -> str:
        from parrot.brain.menu_registry import MenuSelection, get_menu_registry

        payload = _payload(data)
        mode_flags = payload.get("mode_flags") or payload.get("active_mode") or ()
        if isinstance(mode_flags, str):
            mode_flags = [s.strip() for s in mode_flags.split("|") if s.strip()]
        selection = MenuSelection(
            persona_id=str(payload.get("persona_id") or payload.get("active_persona_id") or ""),
            mode_flags=tuple(str(x) for x in mode_flags),
            scene_id=str(payload.get("scene_id") or payload.get("active_scene_id") or ""),
            model_id=str(payload.get("model_id") or payload.get("active_model_id") or ""),
            workspace_id=str(
                payload.get("workspace_id") or payload.get("active_workspace_id") or ""
            ),
            metadata=dict(payload.get("metadata") or {}),
        )
        result = get_menu_registry().apply_selection(selection)
        return _dump({"status": "ok" if result.success else "error", "result": result})

    @room.local_participant.register_rpc_method("applyPreset")
    async def _apply_preset(data: "Any") -> str:
        from parrot.brain.menu_registry import get_menu_registry

        payload = _payload(data)
        preset_id = str(payload.get("preset_id") or "default")
        result = get_menu_registry().apply_preset_id(preset_id)
        return _dump({"status": "ok" if result.success else "error", "result": result})

    @room.local_participant.register_rpc_method("saveAsPreset")
    async def _save_as_preset(data: "Any") -> str:
        from parrot.brain.preset_loader import Preset, get_preset_loader

        payload = _payload(data)
        preset = Preset.from_json(payload)
        path = get_preset_loader().save(preset)
        return _dump({"status": "ok", "preset_id": preset.preset_id, "path": str(path)})

    @room.local_participant.register_rpc_method("applyWorkspace")
    async def _apply_workspace(data: "Any") -> str:
        from parrot.brain.workspace_registry import get_workspace_registry

        payload = _payload(data)
        workspace_id = str(payload.get("workspace_id") or payload.get("active_workspace_id") or "")
        result = get_workspace_registry().apply_workspace(workspace_id)
        return _dump({"status": "ok" if result.success else "error", "result": result})

    @room.local_participant.register_rpc_method("setAppCapabilityMode")
    async def _set_app_capability_mode(data: "Any") -> str:
        from parrot.brain.session_policy import apply_capability_mode

        payload = _payload(data)
        profile = apply_capability_mode(payload.get("mode") or payload.get("capability_mode"))
        supervisor_applied = False
        try:
            from parrot.brain.perception_supervisor import get_perception_supervisor

            supervisor = get_perception_supervisor()
            if supervisor is not None:
                supervisor_applied = await supervisor.apply_capability_profile(profile)
        except Exception:
            logger.exception("setAppCapabilityMode: supervisor policy apply failed")
        return _dump(
            {
                "status": "ok",
                "profile": profile,
                "supervisor_applied": supervisor_applied,
            }
        )

    logger.info(
        "Menu RPC handlers registered: listMenuBlocks, applyMenuSelection, "
        "applyPreset, saveAsPreset, applyWorkspace, setAppCapabilityMode, "
        "getRoomSettingSnapshot, previewRoomProfile, newRoomProfile, "
        "saveRoomProfile, applyRoomProfile, setLineBAudioRoutePolicy, "
        "registerLineBTtsSegment, classifyLineBMicInput"
    )


def _attach_scene_ready_rpc(
    room: "Any",
    session: AgentSession,
    greeting_state: dict[str, bool],
) -> None:
    """Handle Unity startup/placement RPCs.

    reason: LiveKit connection success only means transport is alive. The user
    asked that GOSLO stay silent until AR plane detection and explicit placement
    finish, so ``onSceneReady`` is now a readiness marker and the greeting moves
    to ``onGosloPlaced``.
    """
    import json as _json

    @room.local_participant.register_rpc_method("onSceneReady")
    async def _on_scene_ready(data: "Any") -> str:
        try:
            payload = _json.loads(data.payload) if data.payload else {}
        except Exception:
            payload = {}
        logger.info("onSceneReady: readiness marker only payload=%s", payload)
        return _json.dumps({"status": "ok", "greeting": "deferred_until_goslo_placed"})

    @room.local_participant.register_rpc_method("onGosloPlaced")
    async def _on_goslo_placed(data: "Any") -> str:
        """Unity sends this after AR plane detection + explicit user placement."""
        try:
            payload = _json.loads(data.payload) if data.payload else {}
        except Exception:
            payload = {}
        time_of_day = payload.get("time_of_day", "morning")
        mode = str(payload.get("capability_mode", "") or "")
        if mode == "SessionOnlySilent":
            logger.info("onGosloPlaced: silent mode; greeting suppressed")
            return _json.dumps({"status": "ok", "skipped": "silent_mode"})

        greeting_map = {
            "morning": "早上好！我现在在你桌面上了，有什么可以帮你的吗？",
            "afternoon": "下午好！我在这里陪你，有什么想聊的吗？",
            "evening": "晚上好！今天过得怎么样？",
        }
        instructions = (
            "AR 平面识别已经完成，用户也手动放置好了 GOSLO。"
            f"时段: {time_of_day}。请用以下语气打招呼（参考但不照搬）: "
            f"'{greeting_map.get(time_of_day, greeting_map['morning'])}' "
            "保持角色，简短活泼，体现你是 GOSLO 鹦鹉这个身份。"
        )
        try:
            if greeting_state.get("sent"):
                logger.info("onGosloPlaced: greeting already sent; skipping duplicate")
                return _json.dumps({"status": "ok", "skipped": "duplicate_greeting"})
            generated = await _generate_reply_after_current_speech(
                session,
                instructions,
                "onGosloPlaced",
            )
            if not generated:
                return _json.dumps({"status": "ok", "skipped": "session_policy"})
            greeting_state["sent"] = True
            logger.info("onGosloPlaced: greeting generated (time_of_day=%s)", time_of_day)
        except Exception:
            logger.exception("onGosloPlaced: generate_reply failed")
        return _json.dumps({"status": "ok"})

    @room.local_participant.register_rpc_method("setScene")
    async def _on_set_scene(data: "Any") -> str:
        """Unity SceneProfileManager tells Brain which scene is active.

        Writes session/scene to BB so context_injector + soul know whether
        we are in AR_HANDHELD or DESKTOP_WEBCAM mode. This mirrors the
        startup write in brain.agent (which uses DESKTOP_WEBCAM by default)
        but lets Unity override it at runtime when running on a real device.
        """
        try:
            payload = _json.loads(data.payload) if data.payload else {}
        except Exception:
            payload = {}
        scene_str = str(payload.get("scene", "")).lower()

        from parrot.shared.vision_state import Scene
        from parrot.brain.tools._rpc_bridge import set_scene

        try:
            scene = Scene(scene_str)
        except ValueError:
            logger.warning("setScene: unknown scene '%s', ignoring", scene_str)
            return _json.dumps({"status": "error", "message": f"unknown scene: {scene_str}"})

        set_scene(scene)
        logger.info("setScene RPC: session/scene → %s", scene.value)
        return _json.dumps({"status": "ok", "scene": scene.value})

    logger.info("onSceneReady + onGosloPlaced + setScene RPC handlers registered")


@server.rtc_session()
async def brain_entrypoint(ctx: agents.JobContext):
    """Handle LiveKit's default room jobs and boot the Bus + Gemini session.

    Unity currently creates normal room-join tokens and does not request a
    named agent. Keep this handler unnamed so LiveKit's JT_ROOM dispatch with
    agentName="" can reach Brain. If future clients request named agents,
    route that explicitly at the token/room-config layer instead of changing
    this default handler.
    """
    config = ParrotConfig()
    # region agent log
    _agent_log(
        "post-fix",
        "H1,H2",
        "src/parrot/brain/agent.py:brain_entrypoint",
        "brain default rtc_session entrypoint invoked",
        {
            "room": getattr(ctx.room, "name", ""),
            "job_id_present": bool(getattr(ctx, "job", None)),
            "logger_name": logger.name,
        },
    )
    # endregion

    assistant = ParrotAssistant()
    pipeline = _resolve_pipeline()
    session = _build_session(pipeline, config)
    _attach_transcript_listener_to_session(session, pipeline=pipeline)

    # Sprint4 Phase 4 W3 (entry doc §8.1 L10 selection-C):
    # Mirror Gemini agent_state_changed → BB tick/cognitive_state so
    # selection-C tool wrappers (fly_to / animate / set_video_tier) can
    # surface cognitive state to the LLM in their return values.
    try:
        from parrot.brain.cognitive_state_tracker import attach_cognitive_state_tracker
        attach_cognitive_state_tracker(session)
    except Exception:
        logger.exception("Sprint4 Phase 4: cognitive_state_tracker attach failed")

    manifest = _create_manifest()
    mount = ModuleMount(manifest)

    async def attach_l1() -> None:
        logger.info("Brain L1: starting AgentSession in room '%s'", ctx.room.name)
        # region agent log
        _agent_log(
            "post-fix",
            "H3",
            "src/parrot/brain/agent.py:attach_l1",
            "brain about to start AgentSession",
            {"room": ctx.room.name, "video_input": True},
        )
        # endregion
        try:
            await session.start(
                room=ctx.room,
                agent=assistant,
                room_options=room_io.RoomOptions(video_input=True),
            )
        except Exception as exc:
            # region agent log
            _agent_log(
                "post-fix",
                "H3",
                "src/parrot/brain/agent.py:attach_l1",
                "brain AgentSession start failed",
                {"exception_type": type(exc).__name__, "exception_message": str(exc)[:200]},
            )
            # endregion
            raise
        # region agent log
        _agent_log(
            "post-fix",
            "H3",
            "src/parrot/brain/agent.py:attach_l1",
            "brain AgentSession start completed",
            {"room": ctx.room.name},
        )
        # endregion

    mount.set_l1_hooks(attach=attach_l1)

    await mount.mount()
    await _set_goslo_mode("live", session_id=ctx.room.name)
    logger.info("GOSLO mode → live (room=%s)", ctx.room.name)

    attach_telemetry_receiver(ctx.room)
    attach_video_state_rpc(ctx.room)
    _attach_menu_rpc(ctx.room)
    greeting_state = {"sent": False}
    _attach_scene_ready_rpc(ctx.room, session, greeting_state)

    # Sprint4 Phase 4 W2 收口 (entry doc §8.1 L12 + §8.4):
    # 上行 EcpEvent ingest + 下行 publisher + Phase 4 observers + 临时阈值器。
    # Wire-up 顺序：先 ingest（subscriber 注册前必须有 ingest 实例），再注册
    # observers/threshold（必须在 publisher 之前，避免 brain-source 事件在
    # publisher 未绑定时被 publish_nowait 丢弃），最后 publisher。
    try:
        from parrot.brain.event_ingest import attach_ecp_event_ingest
        from parrot.brain.event_publisher import attach_ecp_event_publisher
        from parrot.brain.observer import register_phase4_observers
        from parrot.brain import attention_config_handler
        from parrot.dsg.attention.threshold import FocusBboxThreshold

        ingest = attach_ecp_event_ingest(ctx.room)
        register_phase4_observers(ingest)
        attention_config_handler.register(ingest)
        FocusBboxThreshold().register(ingest)
        attach_ecp_event_publisher(ctx.room)

        # GAP-1 (audit §5.5 Finding B): wire EcpState ingest so Unity W3.A.3
        # LifecycleHeartbeatPublisher packets on parrot.ecp.state reach Brain
        # and populate BB session/ecp_state (writer=brain._rpc_bridge).
        # Without this handler, session/ecp_state is always None and
        # selection-C tool wrappers see active_locks=[] / active_command_id=""
        # from the ECP side regardless of what Unity reports.
        from parrot.brain.ecp_state_ingest import attach_ecp_state_ingest
        attach_ecp_state_ingest(ctx.room)

        logger.info(
            "Sprint4 Phase 4 wired: EcpEventIngest + Observers + AttentionConfigHandler "
            "+ FocusBboxThreshold + Publisher + EcpStateIngest(GAP-1)"
        )
    except Exception:
        logger.exception("Sprint4 Phase 4: EcpEvent wire-up failed")

    # Sprint4 Phase 4 W8 (entry doc §8.1 L8 + audit §5.1 B3):
    # photo asset upload server (FastAPI on 127.0.0.1:7889 by default) —
    # accepts full-resolution photos via HTTP POST and publishes
    # photo.asset_uploaded EcpEvent for observer.photo to update PhotoNode.
    # Disabled when PARROT_DISABLE_PHOTO_UPLOAD=1 (e.g. multi-process or
    # test environments that bring their own server).
    if os.getenv("PARROT_DISABLE_PHOTO_UPLOAD", "0").lower() not in {"1", "true", "yes"}:
        try:
            from parrot.brain.photo_upload_server import start_photo_upload_server
            await start_photo_upload_server()
        except Exception:
            logger.exception("Sprint4 Phase 4 W8: photo_upload_server start failed")

    try:
        from parrot.memory.conversation_writer import attach_conversation_writer
        attach_conversation_writer(session)
    except Exception:
        logger.warning("Memory subsystem not available — conversation archiving disabled")

    from parrot.brain.mode_watcher import attach_mode_watcher
    attach_mode_watcher(session)

    from parrot.brain.context_injector import attach_context_injector
    attach_context_injector(session)

    # Sprint 2 T1+T10: PerceptionSupervisor (Intent-layer autonomous controller)
    # and ModeController (DsgMode → filter enablement cache). Supervisor must
    # attach AFTER Injector so the default combo write triggers Injector's
    # baseline C3 announcement on the first poll cycle. ModeController reads
    # the same BB key Supervisor just wrote, so order matters.
    try:
        from parrot.brain.perception_supervisor import (
            attach_perception_supervisor,
        )
        attach_perception_supervisor(session)
    except Exception:
        logger.exception("Sprint 2: PerceptionSupervisor attach failed")

    try:
        from parrot.dsg.mode_controller import attach_mode_controller

        attach_mode_controller()
    except Exception:
        logger.exception("Sprint 2: ModeController attach failed")

    from parrot.dsg.trigger_listener import start_trigger_listener
    asyncio.create_task(start_trigger_listener())

    async def _boot_l2b_and_triggers() -> None:
        """Preload L2-B from Graphiti and start all DSG triggers."""
        try:
            from parrot.dsg.l2b_graph import get_l2b_graph
            graph = get_l2b_graph()
            loaded = await graph.preload_from_graphiti()
            logger.info("L2-B preload: %d nodes from Graphiti", loaded)

            from parrot.dsg.triggers.runner import get_trigger_runner
            runner = get_trigger_runner()
            runner._session = session
            await runner.start()
            logger.info("TriggerRunner started with %d triggers", len(runner._triggers))
        except Exception:
            logger.warning("L2-B / TriggerRunner boot failed — continuing without triggers")

    asyncio.create_task(_boot_l2b_and_triggers())

    async def _listen_scheduler_results() -> None:
        """Background task: listen for aggregated results from Scheduler and notify user."""
        try:
            r = await get_redis()
            pubsub = r.pubsub()
            await pubsub.subscribe(CH_SCHEDULER_TO_BRAIN)
            logger.info("Brain: listening for Scheduler results on %s", CH_SCHEDULER_TO_BRAIN)
            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue
                result = json.loads(message["data"])
                task_id = result.get("task_id", "?")
                task_type = result.get("type", "unknown")
                status = result.get("status", "unknown")
                source = result.get("source_worker", "unknown")
                summary = result.get("result_summary", "")
                logger.info(
                    "Brain got result via Scheduler: task=%s type=%s status=%s source=%s",
                    task_id, task_type, status, source,
                )
                if status == "timeout":
                    instructions = (
                        f"A background task timed out. "
                        f"Task type: {task_type}, id: {task_id}. "
                        f"Apologize briefly and suggest trying again later."
                    )
                elif status == "completed" and summary:
                    instructions = (
                        f"A background task just completed! "
                        f"Task type: {task_type}, result: {summary}. "
                        f"Briefly tell the user the result in a cheerful parrot way."
                    )
                else:
                    instructions = (
                        f"A background task finished with status: {status}. "
                        f"Task type: {task_type}, id: {task_id}. "
                        f"Summary: {summary}. "
                        f"Briefly tell the user about it."
                    )
                await _generate_reply_after_current_speech(
                    session,
                    instructions,
                    "scheduler_result",
                )
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception("Error in scheduler result listener")

    asyncio.create_task(_listen_scheduler_results())

    # ChatA startup policy (2026-05-09): do not auto-greet on LiveKit connect.
    # Greeting is explicitly gated by Unity RPC ``onGosloPlaced`` after AR plane
    # detection and user placement. Keeping this silent avoids stealing the
    # first turn while the user is still in the transition/loading flow.

    @ctx.room.on("disconnected")
    def _on_room_disconnected(*_args) -> None:
        asyncio.ensure_future(_set_goslo_mode("chat"))
        try:
            from parrot.dsg.triggers.runner import get_trigger_runner
            asyncio.ensure_future(get_trigger_runner().stop())
        except Exception:
            pass
        # Cancel the Supervisor control loop so that ghost 1Hz tasks do not
        # outlive the room and compete with a future session's Supervisor over
        # BB writes to session/video_tier and session/dsg_mode.
        try:
            from parrot.brain.perception_supervisor import get_perception_supervisor
            sv = get_perception_supervisor()
            if sv is not None:
                asyncio.ensure_future(sv.stop())
        except Exception:
            pass
        # Phase 4 W6-7 self-audit F-06 (2026-04-30): clear the RefBinding
        # registry on disconnect so reload / reconnect cannot inherit stale
        # Refs from the prior session. refs.py docstring already declared
        # this contract; this is the wire-up.
        try:
            from parrot.brain.refs import reset_refs_for_session
            dropped = reset_refs_for_session()  # active_ids=None → drop all
            if dropped:
                logger.info(
                    "RefBinding registry cleared on disconnect (%d refs dropped)",
                    dropped,
                )
        except Exception:
            logger.exception("RefBinding registry cleanup failed on disconnect")
        logger.info("GOSLO mode → chat (room disconnected)")

    logger.info("Brain Agent session active in room '%s'", ctx.room.name)
    # region agent log
    _agent_log(
        "post-fix",
        "H1,H2,H3",
        "src/parrot/brain/agent.py:brain_entrypoint",
        "brain session active",
        {"room": ctx.room.name},
    )
    # endregion


if __name__ == "__main__":
    agents.cli.run_app(server)
