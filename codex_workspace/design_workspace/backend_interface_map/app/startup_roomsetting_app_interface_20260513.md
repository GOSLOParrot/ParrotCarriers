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
- Unity `AppV1SmokeReferenceUiController` preserves the old runtime-built shell
  as Smoke/reference-only evidence.

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
  backend it creates only a clearly marked local draft. `Save` calls the App
  HTTP RoomSetting save endpoint and must not pretend to persist when the
  backend is down.
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
- `START` first applies the current RoomProfile through App HTTP, then sends
  the same current RoomSetting draft as `room_profile` to Brain
  `applyRoomProfile` after LiveKit connects. Model / Persona / Line /
  `scene_profile_id` / `skin_id` / setting refs selected in Unity must reach
  both the App backend active RoomProfile and Brain before capability policy
  sync.

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
- START must not skip App HTTP RoomSetting apply. For Tier 1 settings such as
  LineB, Unity writes the orchestrator runtime config first, then calls App
  HTTP `/api/app/room-setting/apply`, then requests Mint/LiveKit.
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
- Unity has `AppV1SmokeReferenceUiController` for HUD/tool drawer/workspace reference patterns and controller bridges for photo/focus/BBox.
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
- Selector metadata that is useful outside the full RoomSetting snapshot is
  also App HTTP: `GET /api/app/line-profiles` and `GET /api/app/personas`.
  Persona listing exposes selector-safe metadata only; it does not expose
  prompt body text or server file paths.
- App HTTP write/control POSTs can be protected by setting
  `PARROT_APP_MONITOR_SECRET` on the app-monitor service and `appApiSecret` in
  the gitignored Unity `parrot_config.json`. Do not commit this secret.
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
- `AppV1SmokeReferenceUiController` is an older runtime-built App shell used by the Smoke
  builder and as a design reference. It is not mounted in
  `ParrotApp_Startup.unity`, still contains legacy terms such as `Scene` in
  RoomSetting and `LOCAL PREVIEW`, and should not be treated as formal homepage
  completion evidence.
- The useful reference pieces inside `AppV1SmokeReferenceUiController` are the HUD shape,
  low-occlusion tool drawer, settings panel, camera WYSIWYG overlay, photo
  entry, Focus/BBox draggable overlays, 2D workdesk, Nanobot paper note stack,
  placement gate buttons, and local capability-mode controls. They need to be
  re-bound to the formal startup/lifecycle contracts before production use.

### A2. ECS Retry Finding: Mint OK, Brain Job Crashes

2026-05-13 CST live retry against Castle `8.216.45.45`:

- `parrot_config.json` currently points Unity at ECS `mintUrl`,
  `liveKitUrl`, and `room`, but does not include `appApiUrl` or
  `orchestratorUrl`. Historical finding: before the 2026-05-15 client fix,
  Unity could silently use local fallback App API `127.0.0.1:8790` and skip
  the orchestrator unless those fields were injected for the phone/ECS run.
  Current clients intentionally fail fast when `appApiUrl` is absent.
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
   Brain participant appears -> `applyRoomProfile` and
   `setAppCapabilityMode` payloads succeed -> DataChannel heartbeat ->
   main-ready gate. RoomSetting cold-load/save is verified through App HTTP,
   not Brain RPC.

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
   `applyRoomProfile` and `setAppCapabilityMode` -> check payload business
   status, not just transport success. RoomSetting snapshot load/save remains
   an App HTTP proof, not a Brain RPC proof.
6. Only after step 5 passes, run the phone/device pass for microphone
   permission, Bluetooth input/output route switching, app background/resume,
   AR camera/video publish, and long reconnect behavior.

Current verification target before homepage work can claim "real LiveKit START":

- Brain participant visible in `parrot-main`.
- `applyRoomProfile` and `setAppCapabilityMode` return business-ok payloads.
- Unity DataChannel heartbeat remains bound.
- Main-ready owner waits for HUD, menu snapshot, model/AR, LiveKit, Brain, RPC,
  and DataChannel gates.

### A4. 2026-05-14 Castle Repair Status

Owner report: Castle repair completed and pushed as commit `26a142f`.

Completed server-side repairs:

- `GOOGLE_APPLICATION_CREDENTIALS` was kept as a service-account JSON, not a
  user OAuth credential. The failure was file permissions / directory access,
  not a Google account password change.
- ADC file moved from `/secure/ecs/parrot/google-stt-service-account.json` to
  `data/secrets/google-stt-service-account.json`, owned by `parrot:parrot` and
  mode `400`.
- `.env` / `.env.castle` now points `GOOGLE_APPLICATION_CREDENTIALS` at the
  new readable path.
- `data/secrets/` is gitignored to prevent the service-account key from being
  committed.
- `PARROT_MINT_AGENT_DISPATCH=unity` is present in the Castle environment.
- token-mint was rebuilt/restarted with the dispatch-token change.
- Mint verification returned `agent_dispatch_requested: True` for Unity
  identity, Brain has no new crash after restart, and the five Castle services
  are `active`.

Current status:

- The old blocker "Brain job crashes because LineB Google STT cannot read ADC"
  is resolved.
- This still does not by itself complete Unity START. The next verification is
  a true START chain: Unity/diagnostic client joins with a Unity identity,
  Brain participant appears in `parrot-main`, `applyRoomProfile` and
  `setAppCapabilityMode` return business-ok payloads, DataChannel heartbeat
  stays bound, and main-ready gates are clean. RoomSetting HTTP load/save and
  orchestrator prewrite are separate HTTP proofs.

### A5. 2026-05-14 Formal START Retry After LiveKit Restart

Verification after Castle LiveKit key alignment:

- Mint-issued Unity tokens now validate against Castle LiveKit, and a
  diagnostic Unity client can join `parrot-main`.
- The formal START script passed App HTTP RoomSetting load/preview/save/apply
  for `ner_lineb_room`, orchestrator LineB Tier 1 prewrite, token mint, and
  LiveKit connect.
- It then correctly failed at the Brain-present gate: no `agent-*` / `brain`
  participant became visible within 75 seconds. The script restored active
  RoomSetting to `default` and cleared the temporary runtime config file.
- A follow-up run using the existing `sim_unity_client.py
  --startup-rpc-check --startup-room-profile-id ner_lineb_room` path manually
  dispatched the unnamed Brain job server-side; Brain joined and the post-join
  START RPCs `applyRoomProfile` and `setAppCapabilityMode` returned business-ok.

Interpretation:

- LiveKit key alignment is fixed.
- Brain / LineB / RPC business sync works when the Brain job is actively
  dispatched.
- The remaining phone-path gap is dispatch ownership. Unity cannot hold the
  LiveKit API secret, and JWT `roomConfig.agents=[{}]` does not reliably fire
  when the room already exists because a scheduler/diagnostic participant keeps
  it alive.
- Local follow-up in `src/parrot/castle/token_mint.py` now keeps the existing
  JWT `RoomConfiguration` fallback and additionally performs a best-effort
  server-side active dispatch for Unity identities when no Brain/agent
  participant is present. The `/mint` response exposes non-secret diagnostics:
  `agent_dispatch_active_attempted`, `agent_dispatch_active_created`,
  `agent_dispatch_active_already_present`, and `agent_dispatch_active_error`.
- Historical status: this APP-013 blocker is superseded by the 2026-05-15
  post-ECS-restart probe below. The newer probe closes the non-phone START
  chain through heartbeat, while formal main-ready HUD/menu ownership remains
  APP-015 work.

### A6. 2026-05-15 Formal START Probe After ECS Restart

Verification after the user restarted ECS:

- The non-phone formal START probe used the gitignored Unity runtime config and
  did not add Editor scenes or modify formal App state permanently.
- Passed: App HTTP `GET /api/app/room-setting`, RoomSetting `save` and `apply`
  for `ner_lineb_room`, orchestrator `/apply_room_profile` LineB prewrite,
  token-mint `/mint`, LiveKit connect, Brain `agent-*` participant presence
  without manual dispatch, Brain RPC `applyRoomProfile` business-ok, Brain RPC
  `setAppCapabilityMode` business-ok, and `parrot.ecp.state` heartbeat publish.
- A fresh temporary LiveKit room also spawned Brain from the Mint/LiveKit
  dispatch path without manual server dispatch. This proves the phone-equivalent
  no-manual-dispatch gate is no longer blocked at the connectivity layer.
- Cleanup: active RoomSetting was restored to `default`, and temporary
  orchestrator `runtime_config.json` was cleared back to env-backed runtime
  selection.

Important caveats:

- Mint currently returns `agent_dispatch_requested` but not the newer
  `agent_dispatch_active_*` diagnostics from the local follow-up patch. Treat
  this as a deployment-diagnostics gap, not a START blocker, because the fresh
  room probe proved Brain appears without manual dispatch.
- This is still a non-phone script proof. It does not validate iQOO Neo9
  microphone permission, Bluetooth/SCO/A2DP routing, app switch/resume,
  AR/video publish, or the final formal HUD/menu main-ready owner.

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

- Brain RPC START proof covers Brain participant presence plus post-join
  `applyRoomProfile` / `setAppCapabilityMode` business-ok when dispatch is
  performed server-side. The phone-facing blocker is deploying token-mint's
  active dispatch fallback so Unity does not depend on token-only dispatch in
  an already-live room.
- After token-mint active dispatch is deployed, the remaining App-side blocker
  is the formal main-ready HUD/menu gate and device media/lifecycle pass.
- Unity has local audio route detection and mic republish logic, and
  `AudioRoutePolicyBrainReporter` now pushes the compact route policy to Brain
  `setLineBAudioRoutePolicy`. This is code-complete for the static path, but
  still needs iQOO Neo9 Bluetooth/SCO/A2DP proof before it can be called stable.
- `RoomManager.ReconnectUsingCachedCredentials()` remains editor/debug level.
  Production passive disconnects now have `LiveKitReconnectSupervisor`, which
  remints a fresh token, applies bounded backoff, reconnects LiveKit, reruns
  `applyRoomProfile` / `setAppCapabilityMode`, and rebinds heartbeat. Network
  flap/background behavior still needs phone proof and degraded HUD surfacing.
- `RoomManagerLifecycleBridge` reports room/Brain presence and passive
  disconnects. `FormalMainReadyGate` now owns `ReportRunning()` and waits for
  transport, Brain, heartbeat DataChannel, mic/video when required, HUD, menu,
  model, and AR/session gates.
- Formal homepage/menu is not designed yet. `ParrotAppStartupUiController`
  may only show a main-ready hold screen after START; it must not grow a
  predesigned HUD/menu before APP-018/APP-015 audit and responsibility split.
  The old controller has been demoted/renamed to
  `AppV1SmokeReferenceUiController`; its reusable pieces still need to be
  copied into the formal homepage plan instead of mounting the controller.

2026-05-15 START button repair:

- `AppStartupFlowController` now owns App HTTP RoomSetting apply, so every
  `StartFromConfig` caller follows the same formal path instead of only the UI
  button being correct.
- Fresh START order is now permission gate -> transition -> Tier 1 orchestrator
  prewrite when required -> App HTTP `/api/app/room-setting/apply` -> token
  mint -> LiveKit connect -> Brain `applyRoomProfile` -> Brain
  `setAppCapabilityMode` -> main-ready hold screen.
- If `AppRoomSettingClient` is missing or has no endpoint, START fails with
  `room_setting_http_apply_required`. If the backend rejects the active
  RoomProfile, START fails with `room_setting_http_apply_failed:<reason>`.
  This prevents a phone build from silently treating a local draft as persisted
  ECS state.

2026-05-15 RoomSetting persistence proof:

- Formal App HTTP persistence was verified against ECS using the same
  RoomSetting endpoints as `AppRoomSettingClient`: `/new` returned an unsaved
  `room_*` draft, `/save` persisted fixed probe
  `room_codex_persistence_probe`, and a fresh snapshot listed that Room from
  ECS. A snapshot without `room_profile_id` still reported active Room
  `default`, proving save did not silently apply.
- `BuildWritableRoomProfileForSave()` now treats built-in baseline ids
  `default`, `ner_lineb_room`, `ephemeral`, and `workspace_only` as save-as-new
  ids. This prevents the phone UI from overwriting the shipped default or Ner
  LineB test profile when the user edits a preset and taps Save.
- `AppRoomSettingClient` now rejects malformed save/apply responses that lack a
  returned `room_profile.room_profile_id`, so HTTP 200 with an unusable body is
  not considered a successful save/apply.

### D. Observable Completion Signal

Current completed facts:

- Formal scene starts from `ParrotApp_Startup.unity` and mounts the runtime
  services needed for RoomSetting, token mint, LiveKit, heartbeat, mic/video,
  lifecycle, and orchestrator.
- Startup RoomSetting can load, preview, new, save, and build a full
  RoomProfile draft. Theme writes `skin_id`; `scene_profile_id` remains an
  internal baseline.
- ECS persistence is proven for formal App HTTP `New` + `Save` path; saved Room
  `room_codex_persistence_probe` appears after reload and active Room remains
  unchanged unless apply is called.
- Local smoke proves App API, token mint, LiveKit room join, and DataChannel
  heartbeat binding. The later Castle diagnostic proves Brain participant plus
  post-join `applyRoomProfile` / `setAppCapabilityMode`; production phone
  media and public HTTP endpoints remain separate.
- Passive reconnect now has a formal Runtime service: `LiveKitReconnectSupervisor`
  drives fresh-token reconnect/backoff after a post-main-ready passive drop and
  uses the startup flow to re-sync Brain business RPCs. It is not phone-stable
  until APP-024 evidence exists.
- START while already connected to a Tier1/LineB-changing Room now uses the same
  formal surfaces instead of a hard failure: orchestrator prewrite, App HTTP
  RoomProfile apply, graceful chokepoint shutdown, fresh Mint token, LiveKit
  reconnect, Brain `applyRoomProfile`, Brain `setAppCapabilityMode`, and
  heartbeat rebinding. It waits for shutdown cool-down and `ReportDisconnected()`
  to finish, then explicitly re-enters token/AR-starting gates before mint/connect
  so the old shutdown cannot mark the fresh session disconnected and
  `ReportRoomConnected()` / `ReportRunning()` can advance again. Startup and
  reconnect failures can now call `ReportDegraded()` from token, AR-starting,
  connecting, or reconnecting states instead of leaving the FSM optimistic.
- Formal main-ready now has gate reporters:
  `FormalMainReadyGate` blocks `ReportRunning()` until required gates are
  satisfied and self-reevaluates while waiting, so one-shot loader failures
  degrade instead of silently hanging. `FormalHomeHudController` reports
  `hud_loaded`; `FormalHomeMenuLoader` reports `menu_snapshot_loaded` from App
  HTTP `/api/app/canvas` only after a real workspace/menu shell payload is
  parsed, using a JsonUtility-safe `float generated_at`; `FormalModelReadyReporter`
  reports `model_resolved`; and
  `FormalArRuntimeBootstrap` stays mounted but does not auto-start on the
  startup page. `FormalArSessionBaselineReporter` calls it on demand for
  video/AR modes to mount ARSession/ARCameraManager/ARCameraBackground before
  owning `ar_session_baseline_clean`.
  On mobile AR/video modes the baseline waits for `ARSessionState.SessionTracking`
  instead of accepting `Ready` / `SessionInitializing`, and clears terminal
  coroutine refs after clean or unsupported states.
  `XRGeneralSettings` now auto-loads/runs the ARCore/ARKit/XR Simulation
  loaders instead of leaving ARSession mounted but loaderless.
- Shutdown quit drain was fixed so exiting Play Mode after a connected room no
  longer hangs on SDK unpublish waits.

Do not mark complete at phone/App level yet:

- True LiveKit connection stability under network flap, app switching, token
  expiry, reconnect, and long background.
- Bluetooth/microphone route switching on iQOO Neo9 or other real Android
  hardware.
- Formal touch menu/tool drawer, production model prefab placement, and phone
  evidence. AR runtime mounting now has a formal bootstrap, but it still needs
  iQOO Neo9 AR/video logs before it can be marked stable. `ReportRunning()`
  ownership and first-pass gate reporters exist, but they do not complete the
  final homepage.

Next TODO draft for the homepage/LiveKit continuation:

1. Extract useful patterns from `AppV1SmokeReferenceUiController` into the
   formal homepage plan without mounting the Smoke/reference controller.
2. Define formal homepage gates: RoomSetting applied, LiveKit connected, Brain
   present, RPC policy synced, heartbeat DataChannel ready, HUD loaded, menu
   snapshot loaded, model driver resolved, AR/session baseline clean.
3. Build the formal HUD/menu loader from existing facade data instead of
   mounting the old smoke UI wholesale.
4. Start local App API + token mint + LiveKit + Brain participant and run a
   true START pass. This can be done without phone/voice.
5. Add phone/device pass for microphone permission, Bluetooth route changes,
   AR camera/video publish, app switch, and reconnect behavior.

### E. 2026-05-14 Fast RPC Check And Homepage Readiness Audit

Fast check scope:

- Reused `src/scripts/sim_unity_client.py` instead of adding Unity Editor
  scripts or new scenes. The new `--startup-rpc-check` path only joins the
  room, waits for Brain, verifies startup business RPC payloads, and exits.
- The script now defaults to unnamed LiveKit Agents dispatch, matching
  `PARROT_MINT_AGENT_DISPATCH=unity`, but still accepts `--agent-name` for old
  named local experiments.
- It grants `can_publish_data=True`, because LiveKit RPC/DataChannel readiness
  is part of START and cannot be verified with a media-only token.
- Formal START does not call Brain RoomSetting read/write RPCs: RoomSetting
  cold-load/edit/save uses App HTTP before LiveKit connects, then the selected
  RoomProfile is sent through `applyRoomProfile` after joining.

RoomSetting RPC provenance and cleanup:

- `getRoomSettingSnapshot`, `previewRoomProfile`, `newRoomProfile`, and
  `saveRoomProfile` were older AppV1/RoomSetting Brain RPC methods from the
  2026-05-10/11 design/audit pass.
- The fast test reused that surface and exposed the payload/boundary problem.
  The formal architecture is now HTTP-first for startup and persistent
  RoomSetting edits.
- Cleanup completed in this chat: those RoomSetting read/write RPC handlers
  and their compact snapshot helper were removed from `src/parrot/brain/agent.py`.
  `applyRoomProfile` remains because it is the post-join START sync RPC, not a
  storage/edit API.
- `src/scripts/sim_unity_client.py --startup-rpc-check` loads the selected
  RoomProfile locally/HTTP-side and checks only the post-join Brain sync RPCs.

First result against Castle on 2026-05-14:

- `unity-rpc-check-*` joined `parrot-main`.
- No Brain was present initially; manual unnamed dispatch created a room job.
- Brain participant `agent-*` joined and published `roomio_audio`. This means
  the previous ADC/dispatch blocker is no longer the active START blocker.
- The earlier deployed Brain failed the old RoomSetting snapshot RPC with LiveKit
  `Response payload too large`. Local measurement showed the full snapshot was
  about 27 KB; this is why the RoomSetting read path was moved back to HTTP and
  the Brain RoomSetting RPC surface was removed from active backend code.

Code/deploy result:

- Castle was fast-forwarded to `c0f1705`, which included the compact RPC
  snapshot fix used for the temporary diagnostic.
- Local cleanup after the architecture decision removed the Brain RoomSetting
  read/write RPC surface from active backend code. Castle needs this follow-up
  code before the deployed Brain registration log matches the HTTP-first rule.
- The earlier diagnostic against the default snapshot proved a useful negative
  case: `applyRoomProfile` correctly returned
  `status:error/result.success:false` because Castle Brain is running LineB
  while the default active room is LineA. Unity must keep treating this as a
  real START failure, not a LiveKit transport success.
- Re-running with `--startup-room-profile-id ner_lineb_room` passed the
  post-join business sync RPCs: `applyRoomProfile` and
  `setAppCapabilityMode`. The diagnostic script now loads the selected
  RoomProfile locally, mirroring the Unity HTTP preload.

Config/public endpoint status:

- Local Unity `parrot_config.json` now includes Castle `appApiUrl` and
  `orchestratorUrl` so phone builds no longer silently fall back to
  `127.0.0.1` for RoomSetting save/apply or Tier 1 LineB prewrite.
- 2026-05-14 update: user repaired ECS public routing. From this workstation,
  `http://8.216.45.45:8790/api/app/room-setting` is reachable and returns
  2 rooms, and `http://8.216.45.45:7890/health` returns orchestrator `ok`.
- Local gitignored Unity config now carries Castle App API, Orchestrator,
  mint, LiveKit, and required bearer secrets. Do not commit this file or echo
  the secrets into docs.
- APP-015.3 public endpoint blocker is resolved for HTTP reachability. Unity's
  token mint client also normalizes a root mint service URL to `/mint`, so
  phone config does not fail if `mintUrl` is stored as the service root.

2026-05-14 formal START script result:

- Passed: `GET /api/app/room-setting`, RoomSetting preview/save/apply for
  `ner_lineb_room`, orchestrator `/apply_room_profile` LineB prewrite, and
  token-mint `/mint` with Unity dispatch requested.
- Restored: active RoomSetting was restored to `default`, and the temporary
  orchestrator runtime config file was cleared back to the env-backed LineB
  state.
- Follow-up after LiveKit config restart: token validation is fixed and LiveKit
  join succeeds. The formal script now blocks later because token-only
  `roomConfig.agents=[{}]` did not make a Brain participant appear within
  75 seconds when the room was already alive. Manual server-side dispatch via
  the existing diagnostic script works and proves Brain/RPC business-ok.
- Local follow-up: token-mint now actively dispatches Brain server-side for
  Unity identities when no Brain participant is present, while still returning
  only a normal participant token to Unity. Deploy/restart token-mint on Castle
  before rerunning the full START chain.

2026-05-15 post-ECS-restart formal START script result:

- Passed: RoomSetting snapshot/save/apply for `ner_lineb_room`, orchestrator
  LineB prewrite, Mint, LiveKit connect, Brain `agent-*` presence without
  manual dispatch, `applyRoomProfile` business-ok, `setAppCapabilityMode`
  business-ok, and `parrot.ecp.state` heartbeat publish.
- Fresh-room dispatch probe: a unique temporary room spawned Brain from the
  Mint/LiveKit dispatch path without manual server dispatch.
- Cleanup: active RoomSetting was restored to `default`, and temporary
  orchestrator runtime config was cleared.
- Caveat: Mint response exposes `agent_dispatch_requested` but not the newer
  `agent_dispatch_active_*` diagnostic fields. This is a diagnostics/deploy
  visibility gap, not a current START blocker.

RPC payload budget:

- Treat LiveKit RPC as a small control-plane surface, not a snapshot transport.
  The old compact-menu budget is superseded by the HTTP-first cleanup.
- Measured payloads from the cleanup audit: full RoomSetting snapshot ~27.5 KB
  and full `canvas_snapshot` ~39.3 KB, both too large for routine LiveKit RPC.
- RoomSetting snapshots, full homepage/canvas data, selector lists, and
  menu/preset persistence stay on App HTTP facade. LiveKit RPC is only for
  compact post-join sync and real-time controls.
- Old Brain menu RPC wrappers (`listMenuBlocks`, `applyMenuSelection`,
  `applyPreset`, `saveAsPreset`) are no longer registered by the active room
  job.

Homepage readiness audit:

- Formal scene `ParrotApp_Startup.unity` mounts the correct runtime services
  for RoomSetting, token mint, LiveKit, heartbeat, mic/video, lifecycle, and
  orchestrator.
- `ParrotAppStartupUiController` is still a startup/RoomSetting/transition
  controller with a main-ready hold screen. It is not the final HUD/menu home,
  and homepage/menu loading must be redesigned through APP-018/APP-015 before
  implementation.
- RoomSetting can load snapshot, preview, create a backend draft, save, and
  build the START RoomProfile. `AppRoomSettingClient` and `AppHomeMenuClient`
  intentionally have an empty App API endpoint by default; if `appApiUrl` is
  absent, START/menu loading fails fast instead of silently trying
  `127.0.0.1:8790` on the phone. Editor/dev can still set a local endpoint via
  gitignored `parrot_config.json` or the Inspector.
- Phone config now has reachable App API and Orchestrator endpoints. A phone
  ECS build can proceed after token-mint active dispatch is deployed and the
  formal non-phone START chain passes Brain, RPC, heartbeat, and main-ready
  gates. Until then it can prove RoomSetting/App HTTP, orchestrator prewrite,
  Mint, and LiveKit join, but may still fail before Brain RPC and heartbeat.
- `Scene` as a user-facing RoomSetting concept should stay out of the startup
  page. The visible row is `Theme` and writes `skin_id`; spatial/environment
  baseline remains `scene_profile_id` and should be automatic.
- `AudioRouteDetector` + `MicrophonePublisher` implement route detection,
  sample-rate selection, and mic unpublish/republish on route changes. They are
  not yet verified on iQOO Neo9 Bluetooth/SCO/A2DP and they do not yet publish
  `session/audio_route_policy` to Brain.
- `RoomManager.ReconnectUsingCachedCredentials()` is still an editor/debug
  helper. Production mobile reconnect needs fresh token re-mint, bounded
  backoff, and app-switch/network-flap ownership.
- `AppV1SmokeReferenceUiController` remains a Smoke/reference controller. Reuse only its
  HUD/tool drawer/camera/workdesk/note/Focus/BBox interaction ideas; do not
  mount it wholesale or let its local preview/mobile-incompatible assumptions
  define the formal App.
- The next formal homepage implementation should build the accepted touch
  menu/tool drawer, persona/line-profile selector loaders, model placement, and
  phone AR/video validation on top of the existing main-ready gate reporters.
