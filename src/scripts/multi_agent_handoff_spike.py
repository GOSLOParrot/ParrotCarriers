"""Multi-Agent Handoff minimal spike (Sprint 4 Phase 5+ Line B bonus axis).

Reference: ``.cursor/skills/livekit-agents/SKILL.md §4`` (IntroAgent →
StoryAgent handoff pattern).

Goal:
    Validate that livekit-agents Multi-Agent Handoff works end-to-end with
    the same Line B (STT-LLM-TTS Gemini) plumbing the Brain uses, **without
    coupling to ParrotCarriers selection-C wrappers / DSG triggers / observers**.

What it does:
    1. ``IntroAgent`` (no tools beyond ``information_gathered``) greets the
       user, asks for name + location.
    2. On ``information_gathered(name, location)`` it returns a fresh
       ``StoryAgent`` with the gathered info baked into ``instructions``.
    3. ``StoryAgent`` opens with a one-paragraph story personalized to the
       user; new tools / new instructions are live.

Run:
    PARROT_LLM_PIPELINE=line_b   # not strictly required (this script
                                 # builds its own session), but the env
                                 # gate is honoured for parity reporting.
    GOOGLE_API_KEY=...           # for google.LLM
    GOOGLE_APPLICATION_CREDENTIALS=...  # for google.STT / TTS
    LIVEKIT_URL / LIVEKIT_API_KEY / LIVEKIT_API_SECRET set.

    .venv/Scripts/python.exe -m parrot.scripts.multi_agent_handoff_spike dev

Outcome flag (per Phase 5+ chat acceptance §3):
    PASS — handoff fires + StoryAgent speaks personalized opener.
    FAIL — record reason in ``architecture/lineb_implementation_completion_*.md``
    §Multi-Agent Handoff axis. **Failure is acceptable** and does NOT block
    the first 5 axes per chat task §1.6 + §3.

This is NOT real ParrotCarriers role switching (PerchedParrot → MaidGoslo
etc.) — that lives in the interface-extraction chat. This is purely a
plumbing-soundness check on livekit-agents handoff under Line B.
"""

from __future__ import annotations

import dataclasses
import logging
import os

from livekit import agents
from livekit.agents import Agent, AgentServer, AgentSession, JobContext, RunContext, function_tool
from livekit.plugins import google, silero

logger = logging.getLogger("parrot.scripts.multi_agent_handoff_spike")


@dataclasses.dataclass
class StoryData:
    name: str = ""
    location: str = ""


def _build_session_line_b() -> AgentSession[StoryData]:
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY required for Line B handoff spike")
    text_model = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash")
    stt_model = os.getenv("GOOGLE_STT_MODEL", "latest_long")
    tts_voice = os.getenv("GOOGLE_TTS_VOICE", "cmn-CN-Wavenet-D")
    tts_lang = os.getenv("GOOGLE_TTS_LANGUAGE", "cmn-CN")
    languages = [
        s.strip() for s in os.getenv("GOOGLE_STT_LANGUAGES", "cmn-CN,en-US").split(",")
        if s.strip()
    ] or ["cmn-CN"]
    return AgentSession[StoryData](
        vad=silero.VAD.load(),
        stt=google.STT(model=stt_model, languages=languages),
        llm=google.LLM(model=text_model, api_key=api_key),
        tts=google.TTS(language=tts_lang, voice_name=tts_voice),
        userdata=StoryData(),
    )


class IntroAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a friendly storyteller intro agent. Greet the user "
                "in Chinese (短句 + 友好), ask for their name AND a city / "
                "location they like. As soon as you have BOTH, call the "
                "information_gathered tool with them."
            ),
            tools=[self.information_gathered],
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions="用一句话热情打招呼，问对方的名字和喜欢的城市。"
        )

    @function_tool
    async def information_gathered(
        self,
        context: RunContext[StoryData],
        name: str,
        location: str,
    ) -> tuple["StoryAgent", str]:
        """Receive the user's name + location, then hand off to StoryAgent."""
        context.userdata.name = name
        context.userdata.location = location
        story_agent = StoryAgent(name=name, location=location)
        return story_agent, "现在交给故事讲述者，开始故事吧！"


class StoryAgent(Agent):
    def __init__(self, name: str, location: str) -> None:
        super().__init__(
            instructions=(
                f"You are a storyteller. The user's name is {name} and they "
                f"like {location}. Tell them a SHORT (≤ 4 sentences) "
                f"personalized story in Chinese that mentions both."
            ),
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply()


server = AgentServer()


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    pipeline = os.getenv("PARROT_LLM_PIPELINE", "line_b")
    logger.info("multi_agent_handoff_spike: pipeline=%s room=%s", pipeline, ctx.room.name)
    session = _build_session_line_b()
    await session.start(agent=IntroAgent(), room=ctx.room)


if __name__ == "__main__":
    agents.cli.run_app(server)
