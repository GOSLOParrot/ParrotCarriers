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

from livekit import agents
from livekit.agents import Agent, AgentServer, AgentSession, room_io
from livekit.agents.llm import ChatMessage
from livekit.agents.voice.events import ConversationItemAddedEvent, UserInputTranscribedEvent
from livekit.plugins import google

from parrot.brain.soul import get_instructions
from parrot.brain.telemetry_receiver import attach_telemetry_receiver
from parrot.brain.tools import ALL_TOOLS
from parrot.bus.manifest import ModuleManifest
from parrot.bus.mounting import ModuleMount
from parrot.shared.config import ParrotConfig
from parrot.shared.constants import CH_SCHEDULER_TO_BRAIN, HASH_GOSLO_MODE
from parrot.shared.redis_client import get_redis
from parrot.shared.types import Layer, ModuleType

logger = logging.getLogger(__name__)


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
    """把 Gemini 侧用户转写与助手文本打到 Brain 进程终端（与房间 lk.transcription 互补）。"""

    @session.on("user_input_transcribed")
    def _on_user_transcribed(ev: UserInputTranscribedEvent) -> None:
        if not ev.is_final:
            return
        line = f"[Gemini·用户] {ev.transcript}"
        logger.info("%s", line)
        print(f"\n{line}\n", flush=True)

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


@server.rtc_session(agent_name="parrot-brain")
async def brain_entrypoint(ctx: agents.JobContext):
    """Called by LiveKit when a participant joins. Boots Bus + Gemini session."""
    config = ParrotConfig()

    assistant = ParrotAssistant()
    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            voice="Puck",
            model="gemini-2.5-flash-native-audio-preview-12-2025",
            api_key=config.google_api_key or None,
        ),
    )
    _attach_gemini_transcript_to_terminal(session)

    manifest = _create_manifest()
    mount = ModuleMount(manifest)

    async def attach_l1() -> None:
        logger.info("Brain L1: starting AgentSession in room '%s'", ctx.room.name)
        await session.start(
            room=ctx.room,
            agent=assistant,
            room_options=room_io.RoomOptions(video_input=True),
        )

    mount.set_l1_hooks(attach=attach_l1)

    await mount.mount()
    await _set_goslo_mode("live", session_id=ctx.room.name)
    logger.info("GOSLO mode → live (room=%s)", ctx.room.name)

    attach_telemetry_receiver(ctx.room)

    try:
        from parrot.memory.conversation_writer import attach_conversation_writer
        attach_conversation_writer(session)
    except Exception:
        logger.warning("Memory subsystem not available — conversation archiving disabled")

    from parrot.brain.mode_watcher import attach_mode_watcher
    attach_mode_watcher(session)

    from parrot.brain.context_injector import attach_context_injector
    attach_context_injector(session)

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
                await session.generate_reply(instructions=instructions)
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception("Error in scheduler result listener")

    asyncio.create_task(_listen_scheduler_results())

    await session.generate_reply(
        instructions="Greet the user briefly as Parrot. Be cheerful and short."
    )

    @ctx.room.on("disconnected")
    def _on_room_disconnected(*_args) -> None:
        asyncio.ensure_future(_set_goslo_mode("chat"))
        try:
            from parrot.dsg.triggers.runner import get_trigger_runner
            runner = get_trigger_runner()
            asyncio.ensure_future(runner.stop())
        except Exception:
            pass
        logger.info("GOSLO mode → chat (room disconnected)")

    logger.info("Brain Agent session active in room '%s'", ctx.room.name)


if __name__ == "__main__":
    agents.cli.run_app(server)
