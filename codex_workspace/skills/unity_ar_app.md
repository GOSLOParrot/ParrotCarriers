# Skill Route: Unity AR App

Use this route for Unity app startup, HUD, tool cabinet, AR scene wiring, runtime UI, and app-local interactions.

## Read First

1. `codex_workspace/product_brief.md`
2. `codex_workspace/implementation_map.md`
3. `unity/ArSpike/Assets/Scripts/ParrotApp/MIGRATION.md`
4. `.cursor/memory/architecture/ar_app_flow_ui_design.md`
5. `.cursor/memory/architecture/Interface/app_web_parallel_routes_agent_team_20260513.md`

## Code Areas

- Main implementation: `unity/ArSpike/Assets/Scripts/ParrotApp/`
- New UI scripts: `unity/ArSpike/Assets/Scripts/ParrotApp/UI/`
- Assets: `unity/ArSpike/Assets/UI/`

## Design Rules

- UI is 2D overlay Meta UI.
- Keep AR center clean.
- HUD and tool cabinet live on opposite corners.
- Always support placeholder/local test mode.
- Do not use `unity/ParrotDev` for new app code.

## First Implementation Targets

1. Boot/loading controller.
2. Startup RoomSetting with Model, Room, Persona, Line, Scene, and Maid Team.
3. HUD panel bound to lifecycle/connection state.
4. Tool cabinet with placeholder buttons.
5. Notification note spawner.
6. Workspace open/close overlay.

Keep Web console admin concerns out of Unity. App may render a fixed
`CatMaid Team` option before the shared `agent_team_id` core field exists.

## Verification

- If Unity Editor tooling is available, open the scene and verify no compile errors.
- If no Unity Editor access is available, inspect C# compile dependencies and keep changes isolated.
