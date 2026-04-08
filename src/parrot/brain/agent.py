"""Brain Agent — the real-time voice AI entry point.

Architecture:
  LiveKit AgentServer (manages room lifecycle)
    → rtc_session handler
      → Bus mount pipeline (preflight → L2 Redis → L1 AgentSession → heartbeat)
      → Gemini RealtimeModel (voice in/out via LiveKit Room)
      → ParrotAssistant (personality + tools: fly_to, animate, dispatch_task)

Usage:
  # Console mode (no LiveKit Server needed — great for local testing):
  python -m parrot.brain.agent console

  # Dev mode (connects to LiveKit Server, auto-creates room):
  python -m parrot.brain.agent dev
"""

from __future__ import annotations

import logging

from livekit import agents
from livekit.agents import Agent, AgentServer, AgentSession, room_io
from livekit.plugins import google

from parrot.brain.soul import PARROT_INSTRUCTIONS
from parrot.brain.tools import ALL_TOOLS
from parrot.bus.manifest import ModuleManifest
from parrot.bus.mounting import ModuleMount
from parrot.shared.config import ParrotConfig
from parrot.shared.types import Layer, ModuleType

logger = logging.getLogger(__name__)


class ParrotAssistant(Agent):
    """Parrot personality with function tools for AR interaction."""

    def __init__(self) -> None:
        super().__init__(
            instructions=PARROT_INSTRUCTIONS,
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

    manifest = _create_manifest()
    mount = ModuleMount(manifest)

    async def attach_l1() -> None:
        logger.info("Brain L1: starting AgentSession in room '%s'", ctx.room.name)
        await session.start(
            room=ctx.room,
            agent=assistant,
            room_options=room_io.RoomOptions(),
        )

    mount.set_l1_hooks(attach=attach_l1)

    await mount.mount()

    await session.generate_reply(
        instructions="Greet the user briefly as Parrot. Be cheerful and short."
    )

    logger.info("Brain Agent session active in room '%s'", ctx.room.name)


if __name__ == "__main__":
    agents.cli.run_app(server)
