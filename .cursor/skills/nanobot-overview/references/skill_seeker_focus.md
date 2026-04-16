# Skill Seeker distillation focus (injected for Gemini enhance)

> **Repo:** HKUDS/nanobot | **Pin:** v0.1.4.post6

Prioritize accurate coverage of these English symbols and API names when rewriting SKILL.md:

## Core Agent Loop
- `agent/loop.py` — main LLM ↔ tool execution loop
- `agent/context.py` — prompt builder
- `agent/memory.py` — persistent memory
- `agent/tools/` — built-in tools (including `spawn`)

## Configuration
- `config/schema.py` — `ProvidersConfig`, `AgentsConfig`
- `~/.nanobot/config.json` — runtime config
- `providers/registry.py` — `ProviderSpec`, provider registration

## Subagent / Background Execution
- `spawn` tool — create subagent from main agent
- Multiple instances (`--name` flag)
- Workspace sandboxing per instance

## Task Scheduling
- `cron` module — scheduled tasks
- `nanobot cron add` / `list` / `remove`
- Natural language task scheduling

## Memory
- `memory/MEMORY.md` — persistent memory file
- `memory/HISTORY.md` — conversation history
- Memory consolidation patterns

## Channel Adapters (Chat Apps)
- `channels/` — Telegram, Discord, WhatsApp, Feishu, Slack, DingTalk, QQ, Email, Matrix
- `ChannelAdapter` base pattern
- `Gateway` — HTTP gateway for channels

## Python SDK
- `from nanobot import ...` — use as library
- No CLI, no gateway, pure Python

## Tool System
- Built-in tools: github, weather, web search, tmux
- Compatible with OpenClaw skills
- MCP integration

## What to focus on for ParrotCarriers:
1. **agent/loop.py** — the LLM ↔ tool execution cycle is our reference for nanobot-worker design
2. **spawn subagent** — pattern for creating background workers from main agent
3. **cron module** — reference for scheduled tasks (heartbeat, memory consolidation)
4. **memory.py** — how persistent memory is managed (we use Graphiti instead, but the lifecycle pattern matters)
5. **Python SDK** — we embed nanobot as a library, not as a CLI gateway
6. We do NOT use nanobot's channel adapters (Telegram etc.) — our channel is LiveKit Room
