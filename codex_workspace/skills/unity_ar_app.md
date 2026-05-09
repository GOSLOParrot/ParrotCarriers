# Skill Route: Unity AR App

Use this route for Unity app startup, HUD, tool cabinet, AR scene wiring, runtime UI, and app-local interactions.

## Read First

1. `codex_workspace/product_brief.md`
2. `codex_workspace/implementation_map.md`
3. `unity/ArSpike/Assets/Scripts/ParrotApp/MIGRATION.md`
4. `.cursor/memory/architecture/ar_app_flow_ui_design.md`

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
2. HUD panel bound to lifecycle/connection state.
3. Tool cabinet with placeholder buttons.
4. Notification note spawner.
5. Workspace open/close overlay.

## Verification

- If Unity Editor tooling is available, open the scene and verify no compile errors.
- If no Unity Editor access is available, inspect C# compile dependencies and keep changes isolated.
