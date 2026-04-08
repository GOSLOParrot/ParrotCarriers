---
name: nanobot
description: Use when researching nanobot architecture, subagents, memory consolidation, gateway, cron, MCP, or multi-instance runtime
---

# nanobot: Ultra-Lightweight Personal AI Assistant

## Description

`nanobot` is an ultra-lightweight, extensible personal AI assistant platform. For `ParrotCarriers`, its main value is not the chat-channel product surface, but the runtime patterns behind:

- subagents / background execution
- multiple instances
- queue and result routing
- memory consolidation
- heartbeat / cron
- tool and MCP integration

## When to Use This Reference

Use this reference when you need to:
- understand `nanobot` runtime architecture
- inspect how subagents and background work are organized
- inspect how multi-instance configs and workspaces are separated
- inspect heartbeat / cron / memory behavior
- check recent release changes affecting runtime decomposition
- review known issues before borrowing patterns

## Quick Reference

- Repository: `HKUDS/nanobot`
- Language: Python
- Architecture emphasis: lightweight runtime, channels, tools, memory, subagent execution
- Recent turning point: `v0.1.4.post6` runtime decomposition and native provider refactor

## Available References

- `INDEX.md`
- `references/README.md`
- `references/file_structure.md`
- `references/releases.md`
- `references/issues.md`

## Notes For ParrotCarriers

For this project, treat `nanobot` as:

1. a pattern source for backend worker design
2. a pattern source for async task execution
3. a pattern source for queue / callback / result return flow

Do not treat it as:

1. the default architecture for the whole Bus
2. the source of truth for LiveKit / Unity / DSG design
3. a direct deployment template for the current project
