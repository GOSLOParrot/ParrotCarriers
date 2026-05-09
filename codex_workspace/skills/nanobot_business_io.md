# Skill Route: Nanobot Business IO

Use this route for Nanobot dispatch/result flow, Google Calendar business mapping, and long-running report delivery.

## Read First

1. `codex_workspace/interface_plan.md`
2. `src/scripts/start_nanobot_worker.py`
3. `../nanobot/config/goslo_config.json`
4. `.cursor/memory/architecture/user_ideas_and_backend_capability_brief_20260509.md` section 4.3

## Current Facts

- Nanobot is a sibling source tree at `../nanobot`.
- `start_nanobot_worker.py` writes runtime config into `~/.nanobot-parrot/config.json`.
- Google Workspace MCP config exists in Nanobot config.
- Scheduler already forwards Nanobot results toward Brain.

## Business Gaps

- Google event raw payload to normalized node/item mapping.
- Calendar create/update/delete writeback command payloads.
- Nanobot result to Unity paper-note/report payload.
- Heartbeat writer for Nanobot liveness.

## Implementation Bias

- Start with pure mapping functions and fixtures.
- Keep token budget explicit: store raw/detail outside LLM context, pass summaries by default.
- Make result payloads UI-friendly before making them graph-perfect.

## Completion Signal

A sample Google event and a sample Nanobot result can both become normalized payloads rendered by Web console or Unity 2D workspace.
