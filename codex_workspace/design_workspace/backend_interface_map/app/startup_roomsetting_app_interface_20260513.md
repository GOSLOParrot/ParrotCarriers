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

- Startup whitebox now uses a settings entry to open RoomSetting; the first screen keeps a large product title, `设置/ROOM`, `开始/START`, and a PlayMode / `experience_mode` lever.
- RoomSetting interface says user-facing `Room` maps to internal `RoomProfile`.
  The Unity startup page now renders selectors for `Room`, `Model`,
  `Persona`, `Line`, `Theme`, and `Agent Team`. `Theme` is the user-visible
  label for `skin_id` / UI suite. The older backend `scene_profile_id` remains
  an internal launch baseline selected by app/device/experience policy.
- App/Web route decision says `Agent Team` is a logical AgentTeam layer; V1 may render fixed `CatMaid Agent Team` until core AgentTeam fields are confirmed.

### B. Existing Core Interfaces

Partial yes.

Existing pieces that can compose the App V1 draft:

- `RoomSettingService.snapshot()` exposes rooms, selectors, line profiles, and compatibility.
- `RoomSettingService.preview/save/apply()` supports draft preview, persistence, and active apply.
- `RoomProfile` already stores model, persona, line, line profile,
  `scene_profile_id`, experience mode, workspace, `skin_id`, and setting refs.
- Unity `AppStartupConfigDto` mirrors startup fields for START payloads.
- Unity `AppV1MetaUiController` already has a runtime-built startup shell and local selector state.

Existing pieces are enough for a first App UI pass except dynamic Agent Team
selection.

### C. Missing Core Surface

| Candidate | Landing module | SSOT needed | Unity DTO mirror | Notes |
|:--|:--|:--|:--|:--|
| CORE-001 `agent_team_id` on effective RoomSetting selection | Brain / Scheduler / Orchestrator | yes | yes, once confirmed | Needed to move `Agent Team` beyond fixed `CatMaid Agent Team`. |
| CORE-002 AgentTeam registry | Scheduler / Nanobot / Orchestrator | yes | read-only summary only | App needs safe labels/capabilities/restart tier, not Web admin internals. |

Until CORE-001/002 are confirmed, App renders a fixed `CatMaid Agent Team` selector
with a clear V1 placeholder state and does not persist a new field into
RoomProfile.

### D. Observable Completion Signal

- Startup `设置/ROOM` opens RoomSetting, not a LiveKit room picker.
- RoomSetting shows the six selectors as rows in one page.
- Selecting `GOSLO default` or `Ner LineB` updates the model/persona/line/theme preview.
- `New` creates a backend draft when the App API is available; without the
  backend it creates only a clearly marked local draft. `Save` calls
  `saveRoomProfile` and must not pretend to persist when the backend is down.
- `Agent Team` is visible as fixed `CatMaid Agent Team` and marked as V1 fixed until shared core is ratified.
- No Web-only Nanobot/MCP admin fields appear in Unity DTOs.

2026-05-13 Unity whitebox update:

- Formal startup now uses a minimal paper/wood placeholder slot set under
  `Assets/ParrotApp/Art/Startup/Resources/StartupPaperCraft/**`.
- First screen is intentionally sparse: large Chinese-first title
  `AR 提醒助手`, `设置/ROOM`, `开始/START`, a PlayMode / `experience_mode`
  lever, and a Chinese/English switch. Default language is Chinese.
- RoomSetting is a separate full page, not a popup overlay on the first screen.
- RoomSetting uses six selector rows: `Room`, `Model`, `Persona`, `Line`,
  `Theme`, and `Agent Team`; it does not expose a separate `Mode` selector in
  this whitebox.
- `Theme` writes `skin_id`. It is where mansion paper / GOSLO classic /
  Ner mochi room / pirate prototype UI suites belong.
- `scene_profile_id` is not a user-facing desktop/indoor/outdoor picker in
  startup RoomSetting. Environment/baseline selection should be automatic
  through the AR/device/experience component.
- The first-screen lever is the startup PlayMode / `experience_mode` selector,
  not a RoomSetting row and not a UI-only local preview switch. Current whitebox
  cycles the backend-registered values `ar_companion`, `2d_hall`, and
  `room_only`.
- `ar_companion` still requires an AR-capable internal baseline. Unity
  auto-restores `scene_id=ar_handheld` when the PlayMode lever returns to AR,
  and backend compatibility blocks `desktop_webcam + ar_companion` drafts from
  non-startup clients. This is runtime baseline policy, not a user Theme row.
- `START` sends the current RoomSetting draft as `room_profile` to
  `applyRoomProfile`, not just `room_profile_id`, so Model / Persona / Line /
  `scene_profile_id` / `skin_id` / setting refs selected in Unity reach Brain before capability
  policy sync.

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
| CORE-003 `/status` extension for active AgentTeam and nanobot instance health | Orchestrator / ECS status | yes | small HUD summary only | Needed after `Agent Team` becomes dynamic; not required for first fixed selector. |

### D. Observable Completion Signal

- START enters a transition surface before connection work begins.
- Permission, token mint, LiveKit connect, Brain RPC sync, and failure states are visible.
- Successful LiveKit connect stays silent.
- Greeting waits until scene ready plus explicit placement.
- LineB selection clearly shows if Brain cold restart is required.
- `selection_drift=true` is visible as "selected X, running Y" instead of pretending the hot switch happened.
- Pause/resume/reconnect status is shown through health/lifecycle status, not by exposing backend behavior-tree state.

2026-05-13 Unity whitebox update:

- `START` calls `AppStartupFlowController.StartFromConfig` with the selected
  `experience_mode` from the startup PlayMode lever.
- The first screen exposes no token, permission, or backend debugging prose; those
  states remain in transition/HUD surfaces.
- The old `StartupModern` temporary resources are no longer referenced by the
  formal startup scene.

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

## Slice: 2026-05-13 Unity Directory Re-Audit And Cold-Load Implementation

Owner chat: Unity App
Status: done_static_verified
Related TODO: APP-001, APP-002, APP-003, APP-005

### A. Source Readback

- Unity project root is `unity/ArSpike`. The formal App scene is
  `Assets/ParrotApp/Scenes/ParrotApp_Startup.unity`.
- Version locks are valid: Unity `2022.3.62f3`, AR Foundation/ARCore/ARKit
  `5.2.2`, LiveKit Unity SDK git pin
  `7d868ef5cc5615c30a3ef4b73ae0dbb5cc4d6796`.
- Formal App inventory is now centralized in
  `unity_project_inventory_app_ssot_20260513.md`: `Assets/ParrotApp/**` is the
  only formal App center, while `Assets/Tests/Smoke/**` and
  `Assets/Tests/NerTuning/**` are test evidence only.
- Removed/forbidden legacy roots include `Assets/Scripts/ParrotApp/**`,
  top-level App-owned `Assets/Resources/**`, top-level `Assets/UI/**`,
  top-level `Assets/Models/**`, `Assets/Samples/**`,
  `Assets/MobileARTemplateAssets/**`, `Assets/Scenes/SampleScene.unity`, and
  `Assets/TextMesh Pro/**`. The only allowed top-level `Assets/Resources`
  content is the LiveKit SDK-generated `LiveKitSdkVersionInfo.txt`.

### B. Existing Core Interfaces

- True cold RoomSetting load uses the local App HTTP monitor facade before
  LiveKit: `GET /api/app/room-setting`, `POST /api/app/room-setting/preview`,
  `new`, `save`, and `apply`.
- In-room Brain RPC remains the START sync surface after LiveKit connects:
  `applyRoomProfile`, `setAppCapabilityMode`, `onSceneReady`, and
  `onGosloPlaced`.
- Tier 1 LineB cold-start now goes through Castle orchestrator HTTP before
  token mint / LiveKit connect: `POST /apply_room_profile` or
  `POST /set_active_line` writes `data/runtime_config.json`. It does not
  restart Brain in this flow.

### C. Missing Core Surface

No new shared core gap was found for startup cold-load. The App can consume the
existing App HTTP facade plus the existing orchestrator Tier 1 endpoints. Agent
Team and canvas/menu unification remain covered by CORE-001, CORE-002, and
CORE-007 in the candidate queue.

### D. Observable Completion Signal

- Build Settings starts from `Assets/ParrotApp/Scenes/ParrotApp_Startup.unity`;
  `SampleScene` is removed from Build Settings and from the active Assets tree.
- RoomSetting selector data comes from the App backend snapshot when available,
  with a local fallback only when the backend is unavailable.
- User-visible `Theme` means `skin_id` / UI suite. Internal
  `scene_profile_id` remains the runtime launch baseline. Startup mode is
  `experience_mode`, not a bare `Mode`.
- START fails if a Tier 1 LineB switch requires orchestrator but no
  orchestrator endpoint is configured.
- Unity inspects LiveKit RPC response payloads, so `status:error` and
  `result.success:false` are not treated as successful START.
- `LifecycleHeartbeatPublisher` is rebound to a LiveKit DataChannel transport
  after the room connects.
- Main Ready only means transport and UI are ready. `onSceneReady` and
  `onGosloPlaced` stay separate gates; greeting/dialogue remains blocked until
  placement.
- Verification: `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py
  tests/test_brain/test_app_first_version_facade.py tests/test_brain/test_menu_workspace.py
  tests/test_brain/test_app_v1_monitor.py -q` passed with 82 tests. Unity MCP
  script validation found 0 compile errors on the changed startup/backend/
  lifecycle scripts.
- Live runtime verification: local App API `127.0.0.1:8790`, token mint
  `127.0.0.1:7888`, and LiveKit dev server `127.0.0.1:7880` were brought up
  for a smoke pass. App HTTP RoomSetting snapshot/new/save/reload works, with
  saved smoke files isolated under `codex_workspace/design_workspace/artifacts/`.
  A Python LiveKit client joined `parrot-main`, and Unity START joined the same
  room as `unity-codex-smoke-*`.
- Current LiveKit boundary: this proves token mint + LiveKit room join + Unity
  DataChannel heartbeat binding, not full App START. No Brain participant was
  running, so Unity correctly failed at `brain_rpc_room_profile_sync_timeout`
  instead of showing fake success.
- Shutdown fix: the formal scene now exits Play Mode after a connected room
  with 0 Console errors/warnings. `LifecycleShutdownService` uses a synthetic
  delta for synchronous quit drain and publishers skip blocking on SDK
  `UnpublishTrack` during `OnApplicationQuit`.
- Formal scene wiring update: `RuntimeServices` now explicitly mounts
  AppRoomSettingClient, OrchestratorClient, LifecycleHeartbeatPublisher,
  AudioRouteDetector, MicrophonePublisher, ARVideoPublisher,
  VideoStateReporter, and VideoTierReceiver. Startup flow references for
  RoomSetting, heartbeat, mic, video, and orchestrator are non-null.
  A true media-ready START still requires a live server/device pass.

## Slice: 2026-05-13 Homepage And LiveKit Runtime Continuation Audit

Owner chat: Unity App
Status: in_progress
Related TODO: APP-013, APP-015, APP-016

### A. Source Readback

- Brain RPC does not require a real phone or user voice by itself. It requires a
  Brain / LiveKit Agents participant in the same LiveKit room. The latest local
  smoke did not run that participant, so Unity correctly stopped at
  `brain_rpc_room_profile_sync_timeout`.
- Real phone tests are still required for AR camera, microphone permission
  prompts, Android audio route changes, Bluetooth SCO/A2DP behavior, OS
  background/resume, and the full voice/ASR/TTS loop.
- `AppV1MetaUiController` is an older runtime-built App shell used by the Smoke
  builder and as a design reference. It is not mounted in
  `ParrotApp_Startup.unity`, still contains legacy terms such as `Scene` in
  RoomSetting and `LOCAL PREVIEW`, and should not be treated as formal homepage
  completion evidence.
- The useful reference pieces inside `AppV1MetaUiController` are the HUD shape,
  low-occlusion tool drawer, settings panel, camera WYSIWYG overlay, photo
  entry, Focus/BBox draggable overlays, 2D workdesk, Nanobot paper note stack,
  placement gate buttons, and local capability-mode controls. They need to be
  re-bound to the formal startup/lifecycle contracts before production use.

### A2. ECS Retry Finding: Mint OK, Brain Job Crashes

2026-05-13 CST live retry against Castle `8.216.45.45`:

- `parrot_config.json` currently points Unity at ECS `mintUrl`,
  `liveKitUrl`, and `room`, but does not include `appApiUrl` or
  `orchestratorUrl`. Unity would therefore use local fallback App API
  `127.0.0.1:8790` and skip the orchestrator unless those fields are injected
  for the phone/ECS run.
- ECS token mint `/health` is reachable and authorized `/mint` returns a
  LiveKit token. A diagnostic LiveKit client joined `parrot-main`.
- Without dispatch, the room showed only `scheduler`; there was no `agent-*`
  or `brain` participant, so Unity Brain RPC would correctly time out.
- Manual unnamed LiveKit agent dispatch reached `parrot-brain.service`, but the
  job crashed before a Brain participant became visible:
  `google.STT` raised `Application default credentials must be available`.
  This is an ECS LineB ADC/runtime config blocker, not a phone or microphone
  test requirement.
- Follow-up ECS probe as the systemd runtime user found the sharper cause:
  `GOOGLE_APPLICATION_CREDENTIALS` is set and root can see the service account
  file, but user `parrot` reports the file as not existing / not readable. Since
  `parrot-brain.service` runs as `User=parrot`, Google STT cannot load ADC.
  This is a file ownership / directory traversal / env-file runtime issue, not
  a normal Google account password change symptom.
- ECS currently has both a systemd `parrot-brain.service` and an old root tmux
  `python -m parrot.brain.agent dev` process. Future validation should treat
  the systemd service as canonical and retire/ignore tmux evidence unless the
  operator explicitly chooses the tmux path.
- Public `:7890/status` returned `502` during this retry, while the host
  service listens on `127.0.0.1:7890`. Unity ECS config must not assume
  orchestrator is phone-reachable until that control path is explicitly fixed
  or tunneled.

Local code follow-up completed in this chat: `parrot.castle.token_mint` now
requests unnamed LiveKit Agents dispatch for Unity identities by default
(`PARROT_MINT_AGENT_DISPATCH=unity`). This removes the need for Unity to hold a
LiveKit API secret or call a separate dispatch API, but ECS still needs the
updated token-mint deployment plus valid LineB Google ADC, or a deliberate
LineA runtime config for a START smoke.

Resolution path:

1. Put the Google service account JSON in a path readable by `parrot` but not
   public, preferably under a gitignored runtime/secrets directory outside Unity
   and outside committed source.
2. Set `GOOGLE_APPLICATION_CREDENTIALS` in the env file actually loaded by
   `parrot-brain.service` to that path, then restart Brain.
3. Deploy/restart token-mint so the Unity identity dispatch fix is active.
4. Retire or ignore old tmux Brain processes; use systemd Brain as the formal
   ECS validation source.
5. Re-run START with a diagnostic participant check: Mint OK -> Unity joins ->
   Brain participant appears -> `getRoomSettingSnapshot` / `applyRoomProfile`
   RPC payload succeeds -> DataChannel heartbeat -> main-ready gate.

### A3. Repair Plan For START / Brain RPC

Do not treat this as an Android/voice problem first. Repair in this order:

1. Deploy the token-mint dispatch change to Castle and restart token-mint.
   Verification: an authorized `/mint` call for identity `unity-*` returns a
   token whose decoded claims include `roomConfig.agents=[{}]`; listener
   identities such as `observer` should not dispatch by default.
2. Fix the Brain runtime line for the smoke target:
   - Production LineB route: install a Google Cloud service account JSON on
     Castle, set `GOOGLE_APPLICATION_CREDENTIALS` for the same systemd
     environment that runs `parrot-brain.service`, ensure the `parrot` user can
     read it, then restart `parrot-brain`.
   - Temporary START smoke route: clear/override `data/runtime_config.json` to
     `line_a` and verify Brain no longer builds the LineB STT pipeline. This
     proves START/RPC before the LineB ADC secret is ready, but must not be
     labeled as a LineB pass.
3. Remove or park the old root tmux Brain process. Use systemd Brain as the
   canonical evidence source so dispatch, crash, restart, and logs are not
   split between two runtimes.
4. Configure Unity phone/ECS runtime endpoints. `parrot_config.json` needs
   ECS/LAN `mintUrl` and `liveKitUrl`, and either a valid/tunneled
   `orchestratorUrl` / `appApiUrl` or an explicit decision to run those
   endpoints locally for the current smoke. Do not let an ECS phone build
   silently fall back to `127.0.0.1:8790`.
5. Run the non-phone START proof:
   mint token -> LiveKit join -> Brain participant appears -> call
   `getRoomSettingSnapshot`, `applyRoomProfile`, and `setAppCapabilityMode` ->
   check payload business status, not just transport success.
6. Only after step 5 passes, run the phone/device pass for microphone
   permission, Bluetooth input/output route switching, app background/resume,
   AR camera/video publish, and long reconnect behavior.

Current verification target before homepage work can claim "real LiveKit START":

- Brain participant visible in `parrot-main`.
- `applyRoomProfile` and `setAppCapabilityMode` return business-ok payloads.
- Unity DataChannel heartbeat remains bound.
- Main-ready owner waits for HUD, menu snapshot, model/AR, LiveKit, Brain, RPC,
  and DataChannel gates.

### B. Existing Core Interfaces

- App HTTP facade:
  `GET /api/app/room-setting`, `POST /api/app/room-setting/preview`,
  `POST /api/app/room-setting/new`, `POST /api/app/room-setting/save`,
  `POST /api/app/room-setting/apply`.
- Token and runtime control:
  token mint `POST /mint`, orchestrator `POST /apply_room_profile`,
  `POST /set_active_line`, and dev-only `POST /force_unity_reconnect`.
- LiveKit RPC after join:
  `applyRoomProfile`, `setAppCapabilityMode`, `applyWorkspace`,
  `onSceneReady`, `onGosloPlaced`, and the legacy video degraded path
  `onVideoDegraded`.
- LiveKit DataChannel topics currently emitted by Unity:
  `parrot.ecp.state`, `parrot.ecp.health`,
  `parrot.ecp.intent_disconnect`, and `parrot.ecp.event`.
- LineB audio backend state exists through
  `session/audio_route_policy`, `session/lineb_recent_tts_segments`,
  `session/lineb_voice_activity`, and
  `transient/lineb_last_input_decision`.

### C. Missing Core Surface

No new shared core field is required before formal homepage loading can start.
The next work should use the existing App HTTP facade, LiveKit RPC/DataChannel,
RoomSetting, menu registry, canvas snapshot, and LineB status surfaces.

Open implementation gaps:

- Brain RPC full START test is pending until a Brain participant joins the same
  LiveKit room and stays alive. The latest ECS retry proved the dispatch reaches
  Brain but LineB crashes on missing Google STT Application Default Credentials.
- Unity has local audio route detection and mic republish logic, but it does
  not yet push route policy to Brain `session/audio_route_policy`. The backend
  route policy endpoint/RPC exists; the Unity producer hook is intentionally
  reserved.
- `RoomManager.ReconnectUsingCachedCredentials()` is editor/debug level. A
  production reconnect loop with fresh token re-mint, network flap handling,
  and bounded retry/backoff is not complete.
- `RoomManagerLifecycleBridge` reports room/Brain presence and passive
  disconnects, but `ReportRunning()` still needs a formal main-ready owner that
  waits for HUD/menu/model/media gates.
- Formal homepage/menu is still a placeholder in
  `ParrotAppStartupUiController`; the old `AppV1MetaUiController` should be
  demoted/renamed in a separate cleanup slice after its reusable pieces are
  copied into the formal homepage plan.

### D. Observable Completion Signal

Current completed facts:

- Formal scene starts from `ParrotApp_Startup.unity` and mounts the runtime
  services needed for RoomSetting, token mint, LiveKit, heartbeat, mic/video,
  lifecycle, and orchestrator.
- Startup RoomSetting can load, preview, new, save, and build a full
  RoomProfile draft. Theme writes `skin_id`; `scene_profile_id` remains an
  internal baseline.
- Local smoke proves App API, token mint, LiveKit room join, and DataChannel
  heartbeat binding. It does not prove Brain RPC success or production media.
- Shutdown quit drain was fixed so exiting Play Mode after a connected room no
  longer hangs on SDK unpublish waits.

Do not mark complete yet:

- Brain RPC START sync (`applyRoomProfile` and `setAppCapabilityMode`) with a
  live Brain participant.
- True LiveKit connection stability under network flap, app switching, token
  expiry, reconnect, and long background.
- Bluetooth/microphone route switching on iQOO Neo9 or other real Android
  hardware.
- Formal homepage HUD/menu loading, canvas snapshot binding, model prefab
  readiness, and `ReportRunning()` ownership.

Next TODO draft for the homepage/LiveKit continuation:

1. Demote or rename the old `AppV1MetaUiController` to an explicit
   smoke/reference controller, preserving `.meta` and updating Smoke tests.
2. Define formal homepage gates: RoomSetting applied, LiveKit connected, Brain
   present, RPC policy synced, heartbeat DataChannel ready, HUD loaded, menu
   snapshot loaded, model driver resolved, AR/session baseline clean.
3. Build the formal HUD/menu loader from existing facade data instead of
   mounting the old smoke UI wholesale.
4. Start local App API + token mint + LiveKit + Brain participant and run a
   true START pass. This can be done without phone/voice.
5. Add phone/device pass for microphone permission, Bluetooth route changes,
   AR camera/video publish, app switch, and reconnect behavior.
