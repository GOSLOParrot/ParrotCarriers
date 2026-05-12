# Skill Route: Web Console

Use this route for developer Web console and visualization.

## Read First

1. `codex_workspace/interface_plan.md`
2. `.cursor/memory/architecture/chat_launches/web_console_launch_20260509.md`
3. `.cursor/memory/architecture/Interface/INDEX.md`
4. `.cursor/memory/architecture/user_ideas_and_backend_capability_brief_20260509.md`
5. `.cursor/memory/architecture/Interface/app_web_parallel_routes_agent_team_20260513.md`

## Scope

Read-only first:

- DSG visualization;
- Ref repository;
- module state;
- menu/canvas state;
- ECS/orchestrator status;
- Blackboard, IntentWorkspace, Plan, Scheduler, Nanobot, and Maid/GOSLO chat observability.

Write/admin flows stay Web-only and need explicit core-interface approval before
implementation: AgentTeam apply, MCP edit/apply, process restart controls, and
message/control sends.

## Suggested Structure

- `src/parrot/web_console/` for BFF/read adapters.
- `web/console/` for front-end.

## UI Bias

This is an operational tool. Use dense, scannable panels, clear empty states, and restrained styling. Avoid landing-page composition.

## Completion Signal

The console starts locally and shows either live backend state or clearly labeled fixture state for all four read views.
