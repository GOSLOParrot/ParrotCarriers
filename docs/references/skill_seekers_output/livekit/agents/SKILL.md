# agents

The `livekit/agents` skill provides a robust framework for building realtime, programmable voice AI agents. These agents can act as participants in LiveKit rooms, equipped with capabilities to see, hear, and understand, enabling advanced conversational and multi-modal interactions. This skill is ideal for developing server-side applications that interact with users via voice, video, and data channels.

## Description

A framework for building realtime voice AI agents 🤖🎙️📹

**Repository:** [livekit/agents](https://github.com/livekit/agents)
**Homepage:** https://docs.livekit.io/agents
**Language:** Python
**Stars:** 10,010
**License:** Apache License 2.0

## When to Use This Skill

Use this skill when you need to:
- Understand how to use agents
- Look up API documentation and implementation details
- Find real-world usage examples from the codebase
- Review design patterns and architecture
- Check for known issues or recent changes
- Explore release history and changelogs
- Integrate various STT, LLM, and TTS providers.
- Build agents with adaptive interruption handling and dynamic endpointing.
- Implement multi-agent workflows or agent handoffs.
- Develop agents for telephony integration.
- Track agent session usage and performance metrics.

## Table of Contents

- [agents](#agents)
  - [Description](#description)
  - [When to Use This Skill](#when-to-use-this-skill)
  - [Table of Contents](#table-of-contents)
  - [Key Concepts](#key-concepts)
  - [⚡ Quick Reference](#-quick-reference)
    - [1. Basic Agent Session Setup](#1-basic-agent-session-setup)
    - [2. Defining a Function Tool](#2-defining-a-function-tool)
    - [3. Configuring Turn Handling (Endpointing & Interruption)](#3-configuring-turn-handling-endpointing--interruption)
    - [4. Multi-Agent Handoff](#4-multi-agent-handoff)
    - [5. Testing Agents with Judges](#5-testing-agents-with-judges)
    - [6. Tracking Session Usage](#6-tracking-session-usage)
    - [7. Running an Agent in Console Mode](#7-running-an-agent-in-console-mode)
  - [Repository Information](#repository-information)
  - [Languages Used](#languages-used)
  - [⚠️ Known Issues](#️-known-issues)
  - [Recent Releases](#recent-releases)
  - [📖 Available References](#-available-references)
  - [Repository File Structure Overview](#repository-file-structure-overview)
  - [💻 Usage and Further Reading](#-usage-and-further-reading)

## Key Concepts

-   **Agent**: An LLM-based application with defined instructions and tools.
-   **AgentSession**: A container for agents that manages interactions with end users, handling STT, LLM, TTS, and overall conversational flow. It supports advanced features like `turn_handling` for `turn_detection`, `adaptive interruption`, and `dynamic endpointing`.
-   **entrypoint**: The starting point for an interactive session on an `AgentServer`, similar to a request handler in a web server, often defined with `@server.rtc_session()`.
-   **AgentServer**: The main process that coordinates job scheduling and launches `AgentSession`s for user interactions.
-   **`function_tool`**: A decorator used to expose Python functions as tools that an LLM-based `Agent` can call.
-   **`generate_reply`**: A method on `AgentSession` to prompt the agent to generate a conversational reply based on current context or specific instructions.
-   **`update_chat_ctx`**: Method used to modify the agent's chat context, for example, to inject system messages or override previous turns.
-   **`session.start()`**: Initiates an `AgentSession` with a specified agent and LiveKit room.
-   **`session.close()`**: Terminates an `AgentSession`, cleaning up resources.
-   **`DataPacket` / `DataReceived` / `publish_data`**: Mechanisms for exchanging arbitrary data between the agent and LiveKit clients using RPCs and other Data APIs.
-   **`TurnHandlingOptions`**: A unified API for configuring `turn_detection`, `endpointing` delays, and `allow_interruptions` in an `AgentSession`. This replaces deprecated individual arguments for more granular control over conversational flow.

## ⚡ Quick Reference

Here are some practical code examples demonstrating key functionalities:

### 1. Basic Agent Session Setup

Initialize an `AgentSession` with STT, LLM, and TTS providers, and start it with a simple agent in a LiveKit room.

```python
from livekit.agents import Agent, AgentSession, JobContext, inference
from livekit.plugins import silero

server = AgentServer()

@server.rtc_session()
async def entrypoint(ctx: JobContext):
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=inference.STT("deepgram/nova-3", language="multi"),
        llm=inference.LLM("openai/gpt-4.1-mini"),
        tts=inference.TTS("cartesia/sonic-3", voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"),
    )

    agent = Agent(
        instructions="You are a friendly voice assistant built by LiveKit.",
    )

    await session.start(agent=agent, room=ctx.room)
    await session.generate_reply(instructions="greet the user and ask about their day")
```

### 2. Defining a Function Tool

Create a Python function and expose it as a tool that your agent's LLM can invoke.

```python
from livekit.agents import function_tool, RunContext

@function_tool
async def lookup_weather(
    context: RunContext,
    location: str,
):
    """Used to look up weather information."""
    return {"weather": "sunny", "temperature": 70}

# ... (then add lookup_weather to agent's tools)
# agent = Agent(instructions="...", tools=[lookup_weather])
```

### 3. Configuring Turn Handling (Endpointing & Interruption)

Use `TurnHandlingOptions` to control how the agent detects user turns and handles interruptions, including adaptive interruption.

```python
from livekit.agents import AgentSession, TurnHandlingOptions

session = AgentSession(
    # ... other session params
    turn_handling=TurnHandlingOptions(
        turn_detection="vad", # Or "stt"
        endpointing={
            "mode": "dynamic", # Or "static"
            "min_delay": 0.3,
            "max_delay": 3.0,
        },
        interruption={
            "enabled": True,
            "mode": "adaptive", # Or "vad"
            # min_interruption_duration, min_interruption_words can also be configured
        },
    ),
)
```

### 4. Multi-Agent Handoff

Demonstrates how one agent (`IntroAgent`) can gather information and then seamlessly handoff to another agent (`StoryAgent`) with updated context.

```python
from livekit.agents import Agent, AgentSession, RunContext, JobContext, function_tool
from livekit.plugins import silero, openai

class StoryData:
    name: str
    location: str

class IntroAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="You are a story teller. Gather the user's name and location.",
            tools=[self.information_gathered]
        )
    async def on_enter(self):
        self.session.generate_reply(instructions="greet the user and gather information")

    @function_tool
    async def information_gathered(
        self,
        context: RunContext,
        name: str,
        location: str,
    ):
        context.userdata.name = name
        context.userdata.location = location
        story_agent = StoryAgent(name, location)
        return story_agent, "Let's start the story!"

class StoryAgent(Agent):
    def __init__(self, name: str, location: str) -> None:
        super().__init__(
            instructions=f"You are a storyteller. User's name is {name}, from {location}",
            llm=openai.realtime.RealtimeModel(voice="echo"),
        )
    async def on_enter(self):
        self.session.generate_reply()

@server.rtc_session()
async def entrypoint(ctx: JobContext):
    userdata = StoryData()
    session = AgentSession[StoryData](
        vad=silero.VAD.load(),
        stt="deepgram/nova-3",
        llm="openai/gpt-4.1-mini",
        tts="cartesia/sonic-3:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
        userdata=userdata,
    )
    await session.start(agent=IntroAgent(), room=ctx.room)
```

### 5. Testing Agents with Judges

Use the built-in test framework with `pytest` and `judge` assertions to validate agent behavior against non-deterministic LLM outputs.

```python
import pytest
from livekit.agents import AgentSession, Agent, google

class MyAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="...")

@pytest.mark.asyncio
async def test_no_availability() -> None:
    llm = google.LLM()
    async AgentSession(llm=llm) as sess:
        await sess.start(MyAgent())
        result = await sess.run(user_input="Hello, I need to place an order.")
        result.expect.skip_next_event_if(type="message", role="assistant")
        result.expect.next_event().is_function_call(name="start_order")
        result.expect.next_event().is_function_call_output()
        await (
            result.expect.next_event()
            .is_message(role="assistant")
            .judge(llm, intent="assistant should be asking the user what they would like")
        )
```

### 6. Tracking Session Usage

Monitor token counts, character counts, and audio durations per model and provider using the `session_usage_updated` event.

```python
from livekit.agents import AgentSession, SessionUsageUpdatedEvent

session = AgentSession(...)

@session.on("session_usage_updated")
def on_usage(ev: SessionUsageUpdatedEvent):
    for usage in ev.usage.model_usage:
        print(f"Provider: {usage.provider}, Model: {usage.model}, Usage: {usage}")

# You can also access aggregated usage at any time:
# usage = session.usage
# for model_usage in usage.model_usage:
#     print(model_usage)
```

### 7. Running an Agent in Console Mode

Quickly test your agent locally without external servers or dependencies.

```bash
python myagent.py console
```

## Repository Information

- **Description:** A framework for building realtime voice AI agents
- **Topics:** ai, real-time, voice, video, agents, openai
- **Open Issues:** 540
- **Last Updated:** 2026-04-11

## Languages Used

- **Python:** 98.8%
- **C:** 0.7%
- **Makefile:** 0.3%
- **C++:** 0.1%
- **CMake:** 0.1%

## ⚠️ Known Issues

*Recent issues from GitHub (selected)*

-   **#5410**: Feature Request: document a small testing-result surface around `voice.testing.RunResult.events` (Created: 2026-04-10)
-   **#3795**: Turn Detection for Polish language (`enhancement`, `turn-detector`) (Created: 2025-11-04)
-   **#5408**: [google] RealtimeModel + external VAD: generate_reply() conflicts with activity-based audio flow, STT transcript discarded (`bug`) (Created: 2026-04-10)
-   **#5296**: LiveKit not compatible with GA of Azure GPT Realtime 1.5 (`enhancement`) (Created: 2026-04-01)
-   **#5378**: Support for MCP tool list changed notification (`enhancement`) (Created: 2026-04-08)

## Recent Releases

-   **livekit-agents@1.5.2** (2026-04-08):
    -   Key features include: Update Phonic `generate_reply` timeout, fix Prometheus multiproc dir initialization, upgrade MistralAI SDK v2, add WebSocket streaming to Baseten TTS, support multiple provider keys in extra_content serialization, and add D-ID avatar plugin.
-   **livekit-agents@1.5.1** (2026-03-23):
    -   Addressed various fixes and enhancements: Azure OpenAI realtime support, relax transformers upper bound, add translation support for Gladia & Soniox, support custom observability endpoints, add Hamming monitoring plugin, and expose Chirp 3 Google STT endpoint sensitivity.
-   **livekit-agents@1.5.0** (2026-03-19):
    -   Introduced major features: Adaptive Interruption Handling, Dynamic Endpointing, new `TurnHandlingOptions` API, Session Usage Tracking, Per-Turn Latency on `ChatMessage.metrics`, Action-Aware Chat Context Summarization, and Configurable Log Level. Also included several deprecations.

## 📖 Available References

-   `references/README.md` - Complete README documentation
-   `references/CHANGELOG.md` - Version history and changes
-   `references/issues.md` - Recent GitHub issues
-   `references/releases.md` - Release notes
-   `references/file_structure.md` - Repository structure

## Repository File Structure Overview

The `livekit/agents` repository is structured to organize the core framework, examples, and various plugins:

-   **`.github/`**: Contains GitHub Actions workflows for CI/CD, issue templates, and repository banners.
-   **`examples/`**: A crucial directory showcasing various agent implementations, including `voice_agents` (e.g., `basic_agent.py`, `multi_agent.py`), `avatar_agents`, `telephony`, and `primitives`.
-   **`livekit-agents/`**: The core Python package for the LiveKit Agents framework, including modules for `AgentSession`, `Agent`, `inference`, `voice` handling, `llm` integrations, `stt`, `tts`, `utils`, `evals`, and `ipc`.
-   **`livekit-plugins/`**: A comprehensive collection of plugins for integrating with various third-party services like `openai`, `google`, `deepgram`, `elevenlabs`, `cartesia`, `anthropic`, `aws`, `azure`, and many more for STT, LLM, TTS, and avatar services.
-   **`scripts/`**: Utility scripts for development and maintenance.
-   **`tests/`**: Contains unit and integration tests for the core framework and plugins, covering functionalities like `agent_session`, `llm`, `stt`, `tts`, `interruption`, and `realtime` interactions.

This structure allows for modular development and easy extension with new providers and agent types.

## 💻 Usage and Further Reading

For complete usage instructions, detailed API documentation, and more advanced examples, please refer to the main [README.md](references/README.md) file and the official LiveKit Agents documentation: [https://docs.livekit.io/agents/](https://docs.livekit.io/agents/).

To develop with AI coding agents, it's recommended to install the [LiveKit Docs MCP server](https://docs.livekit.io/mcp) for up-to-date documentation and the [LiveKit Agent Skill](https://github.com/livekit/agent-skills) for architectural guidance and best practices.

```shell
# Install the core Agents library with popular plugins
pip install "livekit-agents[openai,silero,deepgram,cartesia,turn-detector]~=1.4"
```