# Skill Route: Unity AR App

Use this route for Unity app startup, HUD, tool cabinet, AR scene wiring, runtime UI, and app-local interactions.

## Read First

1. `codex_workspace/product_brief.md`
2. `codex_workspace/implementation_map.md`
3. `codex_workspace/design_workspace/backend_interface_map/app/unity_project_inventory_app_ssot_20260513.md`
4. `.cursor/memory/architecture/ar_app_flow_ui_design.md`
5. `.cursor/memory/architecture/Interface/app_web_parallel_routes_agent_team_20260513.md`
6. `codex_workspace/app_web_parallel_workflow_20260513.md`

## Code Areas

- Main implementation: `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/`
- New UI scripts: `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/UI/`
- Startup scripts: `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/Startup/`
- Runtime resources: `unity/ArSpike/Assets/ParrotApp/Resources/`
- Curated App art: `unity/ArSpike/Assets/ParrotApp/Art/AppV1/`
- Models: `unity/ArSpike/Assets/ParrotApp/Models/`
- Test evidence only: `unity/ArSpike/Assets/Tests/Smoke/` and `unity/ArSpike/Assets/Tests/NerTuning/`
- Legacy Smoke/reference UI: `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/UI/AppV1MetaUiController.cs`

## Design Rules

- UI is 2D overlay Meta UI.
- Keep AR center clean.
- HUD and tool cabinet live on opposite corners.
- Always support placeholder/local test mode.
- Do not use `unity/ParrotDev` for new app code.
- Do not recreate `unity/ArSpike/Assets/Scripts/ParrotApp/`, top-level
  App-owned `Assets/Resources`, top-level `Assets/UI`, top-level
  `Assets/Models`, or `Assets/Scenes/SampleScene.unity`. The only allowed
  top-level `Assets/Resources` content is the LiveKit SDK-generated
  `LiveKitSdkVersionInfo.txt`.
- After changing Unity directories, scenes, resources, models, art, or Build
  Settings, update the project inventory SSOT and the App TODO board in the
  same turn.
- `AppV1MetaUiController` is reference/test evidence, not formal homepage
  completion. It can inform HUD/tool drawer/camera/workdesk/note/Focus/BBox
  design, but do not mount it wholesale into the formal startup scene or copy
  its legacy `Scene` / local-preview assumptions into the mobile startup flow.

## First Implementation Targets

1. Boot/loading controller.
2. Startup RoomSetting with Model, Room, Persona, Line, Theme, and Maid Team.
   `Theme` is the user-facing `skin_id` / UI suite selector; do not expose
   internal `scene_profile_id` as a desktop/indoor/outdoor RoomSetting row.
3. HUD panel bound to lifecycle/connection state.
4. Tool cabinet with placeholder buttons.
5. Notification note spawner.
6. Workspace open/close overlay.

Keep Web console admin concerns out of Unity. App may render a fixed
`CatMaid Team` option before the shared `agent_team_id` core field exists.
Write App business-interface notes under
`codex_workspace/design_workspace/backend_interface_map/app/`.

## Verification

- If Unity Editor tooling is available, open the scene and verify no compile errors.
- If no Unity Editor access is available, inspect C# compile dependencies and keep changes isolated.
