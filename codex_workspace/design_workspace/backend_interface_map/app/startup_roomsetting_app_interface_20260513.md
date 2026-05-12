# Startup RoomSetting App Interface (2026-05-13)

Owner: Unity App chat
Status: active
Category: App business interface
Scope: APP-001, APP-002, APP-003, APP-005
Sources:
- `codex_workspace/design_workspace/tasks/ACTIVE_CONTEXT.md`
- `codex_workspace/design_workspace/unity_ar_app/startup_menu_design_v0_20260509.md`
- `.cursor/memory/architecture/Interface/app_v1_room_setting_room_profile_interface_20260510.md`
- `.cursor/memory/architecture/Interface/app_v1_lineb_menu_readiness_interface_20260511.md`
- `.cursor/memory/architecture/Interface/app_v1_brain_cold_start_line_lifecycle_audit_20260511.md`

This is the durable App business-interface document for startup, RoomSetting,
LineB visibility, LiveKit transition, and the first main-screen readiness
contract. Keep incremental notes here unless a new module owner or lifecycle is
needed.

This file is not the shared core SSOT. Shared fields and endpoints that need
backend/Unity/Web agreement stay in
`../core_interface_candidate_queue_20260513.md` until the user confirms the
exact contract.

## Slice: Startup RoomSetting Six-Axis

Owner chat: Unity App
Status: active
Related TODO: APP-001

### A. Source Readback

- Startup design says `SCENE` opens RoomSetting; first screen keeps `GOSLO Parrot`, model slot, `SCENE`, `START`, and a visual Mode lever.
- RoomSetting interface says user-facing `Room` maps to internal `RoomProfile`, with selectors for `Model`, `Room`, `Persona`, `Line`, `Scene`, and `Maid Team`.
- App/Web route decision says `Maid Team` is a logical AgentTeam layer; V1 may render fixed `CatMaid Team` until core AgentTeam fields are confirmed.

### B. Existing Core Interfaces

Partial yes.

Existing pieces that can compose the App V1 draft:

- `RoomSettingService.snapshot()` exposes rooms, selectors, line profiles, and compatibility.
- `RoomSettingService.preview/save/apply()` supports draft preview, persistence, and active apply.
- `RoomProfile` already stores model, persona, line, line profile, scene, experience mode, workspace, skin, and setting refs.
- Unity `AppStartupConfigDto` mirrors startup fields for START payloads.
- Unity `AppV1MetaUiController` already has a runtime-built startup shell and local selector state.

Existing pieces are enough for a first App UI pass except dynamic Maid Team
selection.

### C. Missing Core Surface

| Candidate | Landing module | SSOT needed | Unity DTO mirror | Notes |
|:--|:--|:--|:--|:--|
| CORE-001 `agent_team_id` or `maid_team_id` on effective RoomSetting selection | Brain / Scheduler / Orchestrator | yes | yes, once confirmed | Needed to move `Maid Team` beyond fixed `CatMaid Team`. |
| CORE-002 AgentTeam registry | Scheduler / Nanobot / Orchestrator | yes | read-only summary only | App needs safe labels/capabilities/restart tier, not Web admin internals. |

Until CORE-001/002 are confirmed, App renders a fixed `CatMaid Team` selector
with a clear V1 placeholder state and does not persist a new field into
RoomProfile.

### D. Observable Completion Signal

- Startup `SCENE` opens RoomSetting, not a LiveKit room picker.
- RoomSetting shows the six selectors in one page.
- Selecting `GOSLO default` or `Ner LineB` updates the model/persona/line/scene/skin preview.
- `Maid Team` is visible as fixed `CatMaid Team` and marked as V1 fixed until shared core is ratified.
- No Web-only Nanobot/MCP admin fields appear in Unity DTOs.

## Slice: START Transition And LiveKit / LineB Status

Owner chat: Unity App
Status: active
Related TODO: APP-002, APP-003

### A. Source Readback

- Startup design keeps progress/loading as a separate transition after START.
- LiveKit lifecycle guidance says connection success is transport only; App lifecycle state and connection health are reported through `EcpState`.
- Cold-start Line audit says selected Line and running Line are separate: `active_line_id()` is the selected value; `running_line_id()` is the live process truth.

### B. Existing Core Interfaces

Partial yes.

Existing pieces:

- Unity `AppStartupFlowController` runs permission check -> token mint -> LiveKit connect -> `applyRoomProfile` -> `setAppCapabilityMode`.
- `LiveKitTokenMintClient` keeps API secret out of Unity.
- `RoomManager` uses the current LiveKit Unity SDK 3-argument `Room.Connect(url, token, RoomOptions)` pattern and keeps strong references to remote audio streams.
- `AppFirstVersionFacade._voice_pipeline_status()` exposes `running_line_id`, `selected_line_id`, and `selection_drift`.
- LineB readiness exposes Google API key, ADC, ASR/TTS, VAD, voiceprint/speaker, echo risk, recent TTS, and last mic-input decision.

### C. Missing Core Surface

No new Unity-specific core contract is required for first rendering of LineB
readiness. App consumes existing RoomSetting and module-status payloads.

Possible later shared gap:

| Candidate | Landing module | SSOT needed | Unity DTO mirror | Notes |
|:--|:--|:--|:--|:--|
| CORE-003 `/status` extension for active AgentTeam and nanobot instance health | Orchestrator / ECS status | yes | small HUD summary only | Needed after `Maid Team` becomes dynamic; not required for first fixed selector. |

### D. Observable Completion Signal

- START enters a transition surface before connection work begins.
- Permission, token mint, LiveKit connect, Brain RPC sync, and failure states are visible.
- Successful LiveKit connect stays silent.
- Greeting waits until scene ready plus explicit placement.
- LineB selection clearly shows if Brain cold restart is required.
- `selection_drift=true` is visible as "selected X, running Y" instead of pretending the hot switch happened.
- Pause/resume/reconnect status is shown through health/lifecycle status, not by exposing backend behavior-tree state.

## Slice: Main Ready Contract

Owner chat: Unity App
Status: active
Related TODO: APP-005

### A. Source Readback

- Main HUD design says center AR view should stay clear; HUD and tool drawer live in corners and expand by user action.
- App route says startup is not complete just because smoke scene or browser monitor works.
- Existing App shell has HUD, tool drawer, 2D workspace, notes, photo, focus, BBox, hand reflex, and model-driver surfaces.

### B. Existing Core Interfaces

Partial yes.

Existing pieces:

- `AppFirstVersionFacade.canvas_snapshot()` returns module statuses, workspaces, notes, photo refs, tool cabinet, and asset manifest.
- `WorkspaceRegistry.apply_workspace()` switches the 2D workspace without tearing down LiveKit.
- Unity has `AppV1MetaUiController` for HUD/tool drawer/workspace and controller bridges for photo/focus/BBox.
- Unity model capability routing exists through `ModelDriver`, `ParrotRegistry`, and `play_capability` backend gating.

### C. Missing Core Surface

No new core field is required to define the App main-ready checklist.
Implementation may still reveal missing read adapters; add those to the core
candidate queue instead of expanding this business doc with protocol details.

### D. Observable Completion Signal

When startup completes:

- Main HUD exists and shows connection, dialogue gate, camera, focus/BBox, and notes state.
- Tool drawer exists and exposes camera/photo/BBox/menu/2D/settings entries without blocking the center view while collapsed.
- 2D workspace can open without disconnecting LiveKit.
- Photo, focus, and BBox controls either work or show a local missing-controller state.
- Selected model id is consistent across RoomProfile, Unity startup config, and model driver.
- No greeting or first proactive speech happens before explicit placement.
