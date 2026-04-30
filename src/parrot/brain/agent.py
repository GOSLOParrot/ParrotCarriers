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
from parrot.brain.tools import ALL_TOOLS
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
            tools=ALL_TOOLS,
        )


def _create_manifest() -> ModuleManifest:
    return ModuleManifest(
        module_id="brain-agent",
        module_type=ModuleType.CORE,
        layers=[Layer.L1, Layer.L2],
        livekit_identity="brain",
    )


server = AgentServer()


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


def _attach_gemini_transcript_to_terminal(session: AgentSession) -> None:
    """Gemini 侧用户转写与助手文本: 打终端 + 喂 DSG Ingest (Sprint 2 T7).

    Two sinks per event (order matters — terminal log runs even if the
    Ingest path is missing a Graphiti/L2-B dep, because the logs are what
    ops actually watches):

        1. terminal print + logger.info            (Sprint 1 behaviour)
        2. GeminiTranscriptExtractor.feed_transcript (Sprint 2 T7)

    The extractor drops status/context echoes itself (see sprint2_plan
    §9.N3), so we just forward everything we see here.
    """
    try:
        from parrot.dsg.ingest.gemini_transcript_extractor import (
            get_gemini_transcript_extractor,
        )
        extractor = get_gemini_transcript_extractor()
    except Exception:
        extractor = None
        logger.warning("Gemini transcript extractor unavailable — DSG ingest disabled")

    @session.on("user_input_transcribed")
    def _on_user_transcribed(ev: UserInputTranscribedEvent) -> None:
        if not ev.is_final:
            return
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
        line = f"[Gemini·鹦鹉] {text}"
        logger.info("%s", line)
        print(f"\n{line}\n", flush=True)
        if extractor is not None:
            try:
                extractor.feed_transcript(text, "assistant")
            except Exception:
                logger.exception("extractor.feed_transcript(assistant) failed")


async def _generate_reply_after_current_speech(
    session: AgentSession,
    instructions: str,
    reason: str,
) -> None:
    """Call Gemini programmatic speech without overlapping the active turn.

    Gemini Live + LiveKit Agents can time out or cancel tool calls if multiple
    server-initiated generate_reply calls race with current speech/user audio.
    Keep explicit Brain prompts serialized so startup greetings and status
    notices do not steal the user's first turn.
    """
    current_speech = getattr(session, "current_speech", None)
    if current_speech is not None:
        logger.debug("%s: waiting for current_speech before generate_reply", reason)
        await current_speech
    await session.generate_reply(instructions=instructions)


def _attach_scene_ready_rpc(
    room: "Any",
    session: AgentSession,
    greeting_state: dict[str, bool],
) -> None:
    """Sprint 3 S3.D4: handle Unity 'onSceneReady' RPC → time-of-day greeting.

    Unity sends this 500ms after LiveKit connect. Brain generates a brief
    greeting appropriate to the time of day.  The existing `generate_reply`
    at session start fires immediately (before Unity connects); this handler
    fires again when the AR scene is ready — typically they don't overlap
    because the AR scene takes a moment to load after LiveKit connects.
    """
    import json as _json

    @room.local_participant.register_rpc_method("onSceneReady")
    async def _on_scene_ready(data: "Any") -> str:
        try:
            payload = _json.loads(data.payload) if data.payload else {}
        except Exception:
            payload = {}
        time_of_day = payload.get("time_of_day", "morning")
        greeting_map = {
            "morning":   "早上好！我现在在你桌面上了，有什么可以帮你的吗？",
            "afternoon": "下午好！我在这里陪你，有什么想聊的吗？",
            "evening":   "晚上好！今天过得怎么样？",
        }
        instructions = (
            f"AR 场景已就绪，用户的 AR 鹦鹉刚刚出现在桌面上。"
            f"时段: {time_of_day}。请用以下语气打招呼（参考但不照搬）: "
            f"'{greeting_map.get(time_of_day, greeting_map['morning'])}' "
            f"保持角色，简短活泼，体现你是 GOSLO 鹦鹉这个身份。"
        )
        try:
            if greeting_state.get("sent"):
                logger.info("onSceneReady: greeting already sent; skipping duplicate")
                return _json.dumps({"status": "ok", "skipped": "duplicate_greeting"})
            greeting_state["sent"] = True
            await _generate_reply_after_current_speech(
                session,
                instructions,
                "onSceneReady",
            )
            logger.info("onSceneReady: greeting generated (time_of_day=%s)", time_of_day)
        except Exception:
            logger.exception("onSceneReady: generate_reply failed")
        return _json.dumps({"status": "ok"})

    @room.local_participant.register_rpc_method("onGosloPlaced")
    async def _on_goslo_placed(data: "Any") -> str:
        """Unity sends this when user taps to place GOSLO on the desk."""
        logger.info("onGosloPlaced: GOSLO placed on desk — no action needed in Brain")
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
    logger.info(
        "Brain Gemini Live: model=%s voice=%s",
        config.gemini.live_model, config.gemini.live_voice,
    )
    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            voice=config.gemini.live_voice,
            model=config.gemini.live_model,
            api_key=config.google_api_key or None,
        ),
    )
    _attach_gemini_transcript_to_terminal(session)

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
        logger.info(
            "Sprint4 Phase 4 wired: EcpEventIngest + Observers + AttentionConfigHandler "
            "+ FocusBboxThreshold + Publisher"
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

    async def _fallback_startup_greeting() -> None:
        # Unity usually sends onSceneReady after connection. Use this fallback
        # only when that RPC never arrives, so Gemini does not speak two opening
        # greetings and confuse turn detection/transcription.
        await asyncio.sleep(3.0)
        if greeting_state.get("sent"):
            return
        greeting_state["sent"] = True
        try:
            await _generate_reply_after_current_speech(
                session,
                "Greet the user briefly as Parrot. Be cheerful and short.",
                "startup_fallback",
            )
            logger.info("startup fallback greeting generated")
        except Exception:
            logger.exception("startup fallback greeting failed")

    asyncio.create_task(_fallback_startup_greeting())

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
