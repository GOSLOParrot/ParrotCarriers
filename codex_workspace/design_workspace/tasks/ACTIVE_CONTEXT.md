# Design Workspace Active Context

> Updated: 2026-05-15
> Code repo / Codex project route: `D:\GOSLOParrot\ParrotCarriers`
> App design workspace: `D:\GOSLOParrot\ParrotCarriers\codex_workspace\design_workspace`
> Clean status report: `.cursor/memory/architecture/Interface/app_v1_current_status_and_test_report_20260510.md`

## Current Truth

The formal App frontend is **not complete**.

2026-05-13 parallel work route:

- App and Web can now proceed in separate chats using the workflow in
  `codex_workspace/app_web_parallel_workflow_20260513.md`.
- Shared coordination board:
  `codex_workspace/design_workspace/tasks/APP_WEB_PARALLEL_TODOLIST_20260513.md`.
- Copyable App/Web startup prompts:
  `codex_workspace/design_workspace/tasks/APP_WEB_CHAT_START_PROMPTS_20260513.md`.
- Unity App business interfaces:
  `codex_workspace/design_workspace/backend_interface_map/app/`.
- Unity App transport/interface taxonomy:
  `codex_workspace/design_workspace/backend_interface_map/app/unity_app_transport_interface_taxonomy_20260515.md`.
- Unity App LiveKit/ECP/SVA data-flow map:
  `codex_workspace/design_workspace/backend_interface_map/app/unity_livekit_ecp_sva_data_flow_map_20260515.md`.
- Unity App formal homepage HUD/menu V1 implementation prep:
  `codex_workspace/design_workspace/backend_interface_map/app/formal_homepage_hud_menu_plan_20260515.md`.
- 2026-05-15 formal homepage status: HUD/menu shell and App HTTP canvas load
  exist; workspace apply, camera mode, photo awareness, and XR-hand UI mode now
  apply through App HTTP. CAM is the only active toolbar tool owner. MAG/BBox
  are disabled/deferred until after iQOO phone stability and backend SVA/ECP
  visual-evidence design. The new XR-hand HTTP route and deferred MAG/BBox
  canvas state are local until the next ECS deploy.
- 2026-05-15 iQOO Neo9 phone START pass has started. Formal package identity is
  now `com.parrotcarriers.app` / `ParrotApp` / `ParrotCarriers`; Android
  orientation is locked to landscape for the phone UI. Release builds originally
  blocked current `http://8.216.45.45` dev Castle endpoints until
  `ProjectSettings.asset` was changed to `insecureHttpOption: 2`. After rebuild,
  a LineA phone pass showed `parrot_config` load, App HTTP RoomSetting/menu save
  exercise, Mint/LiveKit connect, Brain `agent-*` participant audio, Brain
  `setVideoTier` RPC traffic, Android phone mic publish, AR video first frame /
  1280x720 publish, and short background pause/resume video-state reporting.
  Follow-up bugfixes hide the startup main-ready surface once the formal home
  gates are satisfied and ignore stale RoomSetting preview responses so delayed
  HTTP replies cannot overwrite newer preset selections. This is useful phone
  evidence, not final phone stability: Bluetooth/SCO/A2DP switching, network
  reconnect, long background/session hold, LineB voice, and a visual re-run after
  the UI fix remain pending.
- Unity App RoomSetting ECS persistence is verified as of 2026-05-15:
  `New` returns an unsaved draft, `Save` persists a user Room through App HTTP,
  reload lists it from ECS, and save does not apply or change active Room.
- Unity App project inventory / directory SSOT:
  `codex_workspace/design_workspace/backend_interface_map/app/unity_project_inventory_app_ssot_20260513.md`.
- Web Console business interfaces:
  `codex_workspace/design_workspace/backend_interface_map/web_console/`.
- Shared core-interface candidates:
  `codex_workspace/design_workspace/backend_interface_map/core_interface_candidate_queue_20260513.md`.
- Ratified shared core interfaces still live only under
  `.cursor/memory/architecture/Interface/**` after the required App/Web lane
  confirmation.

`ACTIVE_CONTEXT.md` is not the TODO board. Keep detailed lane tasks in the
shared TODO board and lane-specific business-interface directories.

`D:\GOSLOParrot` is not the code repository. The root-level `D:\GOSLOParrot\codex_workspace` was a duplicate route and has been removed. New Codex work for this app should start from `D:\GOSLOParrot\ParrotCarriers`.

The only App design workspace is:

- `codex_workspace/design_workspace`

The only formal Unity App center is:

- `unity/ArSpike/Assets/ParrotApp/**`

`unity/ArSpike/Assets/Scripts/ParrotApp/**` was a migration-era duplicate
script root and is now removed/forbidden. Unity App chats must read the project
inventory SSOT before touching scenes, scripts, resources, models, art, or Build
Settings.

The only current App V1 status/test report is:

- `.cursor/memory/architecture/Interface/app_v1_current_status_and_test_report_20260510.md`

## Completed Inventory

Completed backend/interface surfaces:

- `AppFirstVersionFacade`
- `list_module_statuses()`
- `canvas_snapshot()`
- `apply_workspace()`
- Google draft, Nanobot report, Photo Awareness, XRHand, Camera mode facade

Completed menu/preset foundations:

- `PresetLoader`
- `MenuRegistry`
- `WorkspaceRegistry`
- `SessionPolicy`
- `AppStartupConfigDto`
- `data/presets/default.json`
- `RoomProfile`
- `RoomSettingService`
- `line_status.py`
- `lineb_audio_guard.py`
- `VOICE_PIPELINE` App module status
- `ner_lineb_room` RoomProfile draft
- `ner_companion` Persona draft
- `ner_skin2` model manifest and `NerSpineController` probe

Completed or selected assets:

- Formal startup page runtime sprites are under
  `unity/ArSpike/Assets/ParrotApp/Art/Startup/Resources/StartupPaperCraft`
  and must exactly match sprites loaded by `ParrotAppStartupUiController`.
- Unused startup placeholder candidates are separated under
  `unity/ArSpike/Assets/ParrotApp/Art/Startup/Candidates/StartupPaperCraft`
  and are not completion evidence.
- Unity imported Wood drawer/button, Paper notes, NekoClaw, BBox frame, and icon sheets under `unity/ArSpike/Assets/ParrotApp/Art/AppV1`.
  These are curated/selected App V1 assets, but most are not yet wired into
  the formal startup scene; current direct usage is mostly smoke/test builder
  evidence until formal controllers load them.
- Ner/GOSLO runtime-loaded visuals now live under
  `unity/ArSpike/Assets/ParrotApp/Resources/Models/**`; `Assets/ParrotApp/Models/**`
  is source/import staging only and is not completion evidence by itself.
- Ner is now a selectable backend/model-menu candidate through
  `unity/ArSpike/Assets/ParrotApp/Resources/parrot_models/ner_skin2.json`.
- Ner has first-pass Unity controller probes for Spine capabilities, cheek
  pinch, and body pickup/place. It is **not** yet a verified production Unity
  prefab or real-device model.
- Pixel asset selection/mapping docs exist; only `pixel_asset_workspace/curated` should guide App import.

Verified narrow tests from the cleaned report path:

- Facade tests
- Monitor tests
- Photo observer tests
- Unity meta UI static tests
- 2026-05-11 LineB/RoomSetting related regression: `42 passed`
- 2026-05-11 LineB/model capability resolver regression: `88 passed`; strict capability bugfix focused regression: `29 passed`; Ner Spine/cheek manifest focused regression: `31 passed`

## Non-Completion Evidence

These are useful test evidence only. They must not be used as App completion evidence:

- `ParrotSmokeScene`
- Web monitor / browser smoke
- Longline self-check or smoke-derived completion docs
- Unity runtime UI prototype mounted into a smoke scene

## Blocking Original Requirements

1. Room Setting: the startup `ROOM` entry opens an App preset/config page for saved Room preset, LineA/LineB, Model, setting file, Theme/skin, Persona, Maid Team, and startup `experience_mode`. Here `Room` means App menu preset, not LiveKit Room. User-visible `Theme` writes `skin_id`; internal `scene_profile_id` is a launch baseline selected by app/device/experience policy, not a desktop/indoor/outdoor RoomSetting row.
2. LineB menu upgrade: the menu must show ASR/TTS readiness, Google ADC status, voiceprint/speaker state, echo risk, and echo handling mode.
3. Ner second model: Ner must move from raw asset to selectable production model path. Startup must be able to choose Brain pipeline, model, setting, scene, and skin.

2026-05-10 RoomSetting clarification:

- User-facing saved preset name: `Room`.
- Internal/professional term: `RoomProfile`.
- Startup RoomSetting exposes Room select/new/save plus six selectors: `Model`, `Room`, `Persona`, `Line`, `Theme`, `Maid Team`.
- Do not use a bare startup field named `Mode`. The startup-page right-side lever is `experience_mode`; GOSLO behavior flags are `behavior_mode` and belong to runtime Brain/persona menus.
- New interface contract: `.cursor/memory/architecture/Interface/app_v1_room_setting_room_profile_interface_20260510.md`.

2026-05-11 LineB clarification:

- LineB menu readiness backend is partial: `src/parrot/brain/line_status.py` exposes LineA/LineB, Google API key, Google ADC, ASR, TTS, VAD, voiceprint/speaker, and echo state.
- `src/parrot/brain/lineb_audio_guard.py` now owns `session/audio_route_policy`, recent TTS segment registry, and last mic-input decision evidence.
- RoomSetting `selectors.lines` and App module `VOICE_PIPELINE` now carry the structured LineB status plus recent TTS / last input decision fields.
- Facade/Web/RPC surfaces exist for audio route policy, TTS segment registration, and mic input classification.
- This is not final voiceprint echo suppression. Real acoustic/DSP echo score, true voiceprint comparison, Unity warning UI, and real-device LineB smoke remain pending.
- Interface contract: `.cursor/memory/architecture/Interface/app_v1_lineb_menu_readiness_interface_20260511.md`.

2026-05-11 LineB + Ner validation route:

- Config/report: `.cursor/memory/architecture/Interface/app_v1_lineb_ner_realdevice_config_report_20260511.md`.
- RoomProfile: `data/presets/ner_lineb_room.json`.
- Persona: `src/parrot/brain/personas/ner_companion.md`.
- Ner LineProfile: `data/line_profiles/lineb_ner_ja_test.json`.
- Ner roleplay setting source:
  `codex_workspace/design_workspace/unity_ar_app/ner_roleplay_setting_obsidian_v0_20260511.md`
  (`profile: roleplay`, no `obsidian_uuid` in frontmatter).
- Scene draft: `codex_workspace/design_workspace/unity_ar_app/ner_mochi_scene_v0_20260511.md`.
- Model manifest: `unity/ArSpike/Assets/ParrotApp/Resources/parrot_models/ner_skin2.json`.
- Unity controller probe: `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/Parrot/NerSpineController.cs`.
- Unity animation audit: `unity/ArSpike/Assets/ParrotApp/Editor/NerSpineAnimationAudit.cs`.
- Current boundary: RoomSetting can recognize/select Ner; Unity Editor has verified 60 imported Spine animations and primary manifest handlers. First-pass cheek pinch code exists (`NerCheekPinchInteractor` + Spine cheek-bone offset/reset), and first-pass body pickup/place code exists (`NerPickupPlaceInteractor` + body capabilities). Unity prefab wiring, startup UI binding, joystick routing to `spine_walk`, expression-button UI, hit-region tuning, and real-device ASR/TTS pass remain pending.

2026-05-11 LineB configurable + Ner gameplay longline:

- Longline TODO: `codex_workspace/design_workspace/tasks/lineb_ner_gameplay_longline_todo_20260511.md`.
- Architecture verdict: the current ECP `meta.model_id` route is sufficient for this round. Do not rewrite the ECP wire protocol before the profile, manifest, and capability layers are implemented.
- Phase 1 complete: LineB now has `LineProfile`, `LineProfileLoader`, `data/line_profiles/lineb_google_default.json`, RoomProfile line-profile ids, facade methods, Web monitor endpoints, and status/device-check tests.
- Phase 2 complete enough for the next Unity/Ner pass: `ModelManifestRegistry` mirrors Unity manifests, RoomSetting exposes per-model capability decisions, `play_capability` validates custom capability ids, and active Ner hides/rejects `fly_to`/reserved `animate` while keeping custom face/touch capabilities available. Strict custom capability calls now preserve Unity `parameters_json` and return `capability_unsupported:<id>` when rejected.
- Phase 4 partial: Ner `SkeletonDataAsset` exact animation names are enumerated in Unity; `ner_skin2.json` now uses verified primary handlers with variant metadata; `NerSpineController` supports `parameters_json` variant/exact-animation dispatch and idle visual fallback on missing animation.
- 2026-05-11 gameplay audit: Trickcal references point to cheek-touch/poke/pat/tickle and room/invite/furniture interactions as the core feel. Ner first playable must prioritize universal joystick movement, cheek pinch, long-press pickup/drag/place, and touch/pat/tickle/eat before deeper combat-like systems. Cheek pinch first pass is implemented in code; production prefab/device tuning remains.
- 2026-05-11 bug audit: cheek pinch now recovers on disabled/lost touch, scans all raycast hits so body colliders do not hide cheek triggers, and normalizes invalid side payloads. This Ner work is non-blocking for continuing LineB configurable-profile and RoomSetting integration.
- 2026-05-11 persona/config update: `ner_companion` now uses `play_capability`
  for Ner custom actions, carries LineB-aware voice/animation trigger rules,
  and `ner_lineb_room` now defaults to `lineb_ner_ja_test`. The roleplay
  Obsidian setting source uses `obsidian_note_key` instead of UUID binding.
- 2026-05-11 Session Context Pack: selected Room setting files now feed runtime
  instructions and UUID-free Obsidian roleplay L1.5 payloads. Persona remains
  loaded by `PersonaLoader`; roleplay/world/scene/action-manual files are Room
  session context. Contract:
  `.cursor/memory/architecture/Interface/app_v1_session_context_pack_upgrade_20260511.md`.
- 2026-05-11 Brain cold-start Line contract: startup RoomSetting can select
  `Line` via `RoomProfile.line_id` / `line_profile_id` and
  `selectors.lines` / `selectors.line_profiles`, but LineA/LineB is
  **cold-start only** because `brain.agent` builds one `AgentSession` from
  `PARROT_LLM_PIPELINE`. Runtime `applyRoomProfile` now blocks a mismatched
  Line with `line.cold_start = requires_brain_cold_restart`. Brain room-scoped
  DSG/Scheduler/listener/upload tasks now clean up on disconnect. Contract:
  `.cursor/memory/architecture/Interface/app_v1_brain_cold_start_line_lifecycle_audit_20260511.md`.
- 2026-05-11 LineB bugfix/bridge: missing `tts.voice_name` now blocks even
  when ADC is also missing. `lineb_audio_guard` now writes
  `session/lineb_voice_activity` for `speaking`, `listening`,
  `agent_echo_suppressed`, and related states; App status exposes
  `voice_activity_state`. `lineb_model_reaction.py` now dispatches those states
  as strict model capabilities, and Ner handles them by switching expression or
  suppressing cheek/touch reactions while speaking / echo-suppressed.
- 2026-05-11 LineB defensive echo guard: high `echo_score` without a recent
  matching TTS segment now becomes `uncertain` / `listening_uncertain`, not a
  user turn. Malformed or non-finite numeric DSP/status values no longer break
  mic classification or the Unity-facing reaction payload.
- 2026-05-11 Ner pickup/place first pass: `ner_skin2.json` declares
  body pickup/held/drag/place capabilities, `NerSpineController` handles them,
  and `NerPickupPlaceInteractor` maps long-press body interaction to
  AR-compatible placement. LineB speaking/echo suppression now blocks new
  strong body/touch starts while allowing release/cancel recovery. Manifest
  capability `kind` stays within the current protocol enum
  (`pose` / `animation` / `procedural`).
- 2026-05-11 final audit fix: pickup cancel/lost-touch/LineB-suppressed drag
  now drops Ner back to the last ground point instead of leaving the model
  suspended. Body/placement raycasts now respect both the interactor transform
  and an explicitly assigned `targetRoot`.
- Micro-tuning handoff prompt:
  `codex_workspace/design_workspace/tasks/ner_unity_tuning_chat_prompt_20260511.md`.
- Latest focused App/LineB/Ner regression: `101 passed` plus py_compile passed
  for touched Python LineB/reaction files. Unity MCP `validate_script` reports
  0 errors for `NerPickupPlaceInteractor.cs` and `NerSpineController.cs`, and
  Console after refresh has 0 errors / 0 warnings. Real-device timing/feel are
  still pending.
- Next blockers:
  1. Phase 4 remaining: create/verify the production Ner prefab with Spine component, `ModelDriver(modelId=ner_skin2)`, `NerSpineController`, cheek/touch hit regions, and camera-safe scale.
  2. Phase 5+: Unity/device tuning for LineB voice-trigger reactions, Ner gameplay, GOSLO joystick/gameplay upgrade, unified prop/object interaction.
  3. External Brain cold-start supervisor for RoomSetting Line selection
     (`PARROT_LLM_PIPELINE` + `PARROT_ACTIVE_LINE_PROFILE_ID`) before Unity
     START can switch LineB without manual restart.
  4. Startup/RoomSetting Unity binding for saved RoomProfile, Line, Model, Persona, Theme/skin, and Maid Team selectors.

2026-05-13 Unity project inventory audit:

- Physical cleanup is complete enough for current App work: formal scene,
  runtime scripts, resources, art, and models live under `Assets/ParrotApp/**`.
- `Assets/Scripts/ParrotApp/**` is removed and forbidden. Sprint4 migration
  notes are archived at
  `codex_workspace/design_workspace/archive/unity_parrotapp_scripts_migration_20260429.md`
  for historical/reference value only.
- Top-level `Assets/Resources` is SDK-owned and may contain only LiveKit's
  generated `LiveKitSdkVersionInfo.txt`; App config/manifests live under
  `Assets/ParrotApp/Resources/**`.
- Current formal scene status: `ParrotApp_Startup` has Camera, Directional
  Light, `ParrotAppRoot`, `StartupDesignStage`, `RuntimeServices`, and
  `AssetPreviewStage`. Startup UI, lifecycle, token mint, RoomManager, shutdown
  bridge, startup flow, AppRoomSettingClient, OrchestratorClient,
  LifecycleHeartbeatPublisher, AudioRouteDetector, MicrophonePublisher,
  ARVideoPublisher, VideoStateReporter, VideoTierReceiver, and formal home
  services are mounted or runtime-resolved under formal scene services.
- 2026-05-13 runtime audit update: local App API `127.0.0.1:8790`, token
  mint `127.0.0.1:7888`, and LiveKit dev server `127.0.0.1:7880` were brought
  up for smoke verification. RoomSetting snapshot/new/save/reload works through
  the App HTTP facade; Python and Unity both joined LiveKit `parrot-main`;
  Unity heartbeat rebound to the LiveKit DataChannel. No Brain participant was
  running, so Unity correctly failed START at `brain_rpc_room_profile_sync_timeout`
  and must not be marked full START complete yet.
- 2026-05-13 ECS retry update: Castle Mint/LiveKit (`8.216.45.45`) are
  reachable and authorized Mint returns a token. A diagnostic client joined
  `parrot-main`; without dispatch the room only showed `scheduler`. Manual
  unnamed dispatch reached systemd Brain, but the job crashed before participant
  presence because LineB `google.STT` could not find Google Application Default
  Credentials. This proves the current blocker is ECS LineB ADC/runtime config
  (plus token-mint deployment), not phone/voice/mic. The Unity config file also
  lacks `appApiUrl`/`orchestratorUrl`; after the 2026-05-15 client fix, ECS
  phone runs fail fast when App HTTP is missing instead of falling back to
  local App API. Orchestrator remains explicit for Tier 1 LineB prewrite.
- Follow-up ECS probe as `User=parrot`: `GOOGLE_APPLICATION_CREDENTIALS` is set,
  but the service account file is not visible/readable to `parrot` even though
  root can see it. Treat this as an ECS file permission/path/env issue, not as
  evidence that the user changed their Google password. Fix ADC readability for
  the systemd runtime before repeating LineB START.
- Repair route recorded in
  `backend_interface_map/app/startup_roomsetting_app_interface_20260513.md`
  A3 and TODO `APP-017`: deploy token-mint dispatch, fix systemd Brain LineB
  ADC or run a deliberate LineA START smoke, retire duplicate tmux Brain
  evidence, then rerun non-phone Brain RPC proof before device audio/AR tests.
- 2026-05-14 Castle repair status: ADC stayed as a service-account JSON
  unrelated to Google account password. The file was moved to
  `data/secrets/google-stt-service-account.json` with `parrot:parrot 400`,
  env was updated, `data/secrets/` was gitignored, `PARROT_MINT_AGENT_DISPATCH=unity`
  was added, token-mint was rebuilt/restarted, commit `26a142f` was pushed, Mint
  now reports `agent_dispatch_requested: True` for Unity identity, Brain has no
  new crash, and the five Castle services are active. The remaining gate is a
  true START proof with Brain participant + business-ok RPC payloads, not just
  service health.
- 2026-05-14 fast START RPC retry: reused `src/scripts/sim_unity_client.py`
  instead of adding Editor scenes. The diagnostic Unity identity joined Castle
  `parrot-main`; Brain was absent at first, unnamed dispatch succeeded,
  `agent-*` joined, and the previous ADC blocker did not recur. After Castle
  was fast-forwarded to `c0f1705`, the earlier RoomSetting RPC diagnostic
  exposed a boundary problem. Formal START proof no longer depends on Brain
  RoomSetting RPC: RoomSetting cold-load/edit/save is App HTTP before LiveKit,
  and the diagnostic script now mirrors the post-join sync by loading the
  selected RoomProfile locally/HTTP-side. The obsolete Brain RoomSetting
  read/write RPC handlers were removed from active backend code; only
  `applyRoomProfile` remains as the post-join sync RPC. The default active RoomProfile
  (`default`, LineA) correctly failed `applyRoomProfile` against the running
  LineB Brain with
  `status:error/result.success:false`; this remains a real START failure, not
  a transport success. Re-running with `--startup-room-profile-id ner_lineb_room`
  passed `applyRoomProfile` and `setAppCapabilityMode` business-ok.
- Current phone/ECS config status: local Unity `parrot_config.json` now
  contains Castle `appApiUrl`, `orchestratorUrl`, mint/LiveKit/room values, and
  the required bearer secrets in the gitignored local config. Do not commit or
  echo those secrets. User repaired ECS public routing; from this workstation
  App HTTP, line profiles, and orchestrator health are reachable. APP-015.3
  HTTP reachability is resolved.
- 2026-05-14 formal START retry after Castle LiveKit config restart: Minted
  Unity tokens now validate and a diagnostic Unity client can join
  `parrot-main`. The full formal START script reached RoomSetting save/apply,
  LineB Tier 1 prewrite, Mint, and LiveKit connect, then correctly failed
  because no Brain participant became visible within 75s. A follow-up run with
  existing `sim_unity_client.py --startup-rpc-check --startup-room-profile-id
  ner_lineb_room` manually dispatched the unnamed Brain job server-side; Brain
  joined and `applyRoomProfile` / `setAppCapabilityMode` returned business-ok.
  Interpretation: token secret alignment is fixed, Brain itself works, but the
  phone path cannot rely only on JWT `roomConfig.agents=[{}]` when the LiveKit
  room already exists with the scheduler participant. Local token-mint follow-up
  now performs a best-effort server-side active dispatch for Unity identities
  when no Brain/agent participant is present, without exposing the LiveKit API
  secret to Unity. This still needs Castle deployment/restart before APP-013 can
  be marked complete. The failed formal script restored active RoomSetting to
  `default` and cleared the temporary runtime config file.
- 2026-05-14 App HTTP selector/security update: `GET /api/app/line-profiles`
  is already present on app-monitor and reachable from Castle; `GET
  /api/app/personas` was added for selector-safe persona metadata
  (`persona_id`, display name, description, schema version, tags only).
  App-monitor POST write/control routes can now be guarded with
  `PARROT_APP_MONITOR_SECRET`; Unity can send that value through the new
  gitignored `appApiSecret` runtime config field.
- 2026-05-15 RPC/HTTP cleanup rule: LiveKit RPC is compact real-time control
  plane only. Old menu wrappers (`listMenuBlocks`, `applyMenuSelection`,
  `applyPreset`, `saveAsPreset`) are no longer registered by the Brain room
  job. Full RoomSetting (~27.5 KB) and full `canvas_snapshot` (~39.3 KB)
  remain HTTP-owned; RoomSetting snapshots, selector lists, full
  homepage/canvas snapshots, and menu/preset persistence must use App HTTP
  facade or a future compact paged HTTP model.
- Lifecycle cleanup note: `LifecycleShutdownService` synchronous quit drain no
  longer blocks on SDK `UnpublishTrack`; latest Unity Play Mode exit after a
  connected room showed 0 Console errors/warnings.
- Current not-complete boundary: this is still a whitebox startup/main-ready
  shell. Full formal AR homepage, production model prefab wiring, real-device
  LiveKit/LineB pass, and final canvas menu implementation remain pending.
- 2026-05-15 START / interface taxonomy update: RoomSetting page has backend
  `New` and `Save`; when Unity `appApiUrl` points to ECS, saved Rooms persist
  through App HTTP RoomProfile storage. `AppStartupFlowController` now applies
  the selected RoomProfile through App HTTP before Mint/LiveKit, after any
  required Tier 1 orchestrator prewrite. Missing App HTTP endpoint or backend
  rejection fails START instead of treating a local draft as ECS state. The
  current main-ready surface is only a hold screen, not homepage/menu design.
  Formal homepage/menu work must restart from
  `unity_app_transport_interface_taxonomy_20260515.md`: App HTTP owns durable
  load/save and large snapshots, Orchestrator HTTP owns Tier 1 runtime control,
  token-mint owns short-lived tokens and server-side Brain dispatch, LiveKit
  media owns audio/video, ECP is the broad embodied-control protocol plane
  (`EcpCommand`/`EcpAck`, `EcpState`, `EcpEvent`, lossy tick, command
  causality, snapshot/sighting/ref links), and Brain RPC remains one compact
  in-room transport/control bridge under that larger model. Smoke scripts
  remain fast evidence, not phone production completion.
- 2026-05-15 post-ECS-restart formal START probe: using the gitignored Unity
  runtime config, the non-phone script passed App HTTP RoomSetting
  snapshot/save/apply for `ner_lineb_room`, orchestrator LineB prewrite,
  token mint, LiveKit connect, Brain `agent-*` presence without manual
  dispatch, `applyRoomProfile` business-ok, `setAppCapabilityMode`
  business-ok, and `parrot.ecp.state` heartbeat publish. A fresh temporary
  LiveKit room also spawned Brain from Mint/LiveKit dispatch without manual
  server dispatch. Mint currently returns `agent_dispatch_requested` but not
  the newer active-dispatch diagnostic fields, so that is a deployment
  diagnostics gap, not a START blocker. The probe restored active RoomSetting
  to `default` and cleared temporary runtime config. This closes APP-013 for
  non-phone START verification only; formal HUD/menu main-ready ownership and
  iQOO Neo9 mic/Bluetooth/app-switch/AR/video tests remain pending.
- 2026-05-15 homepage/menu/LiveKit audit: read
  `backend_interface_map/app/unity_homepage_menu_livekit_audit_20260515.md`
  before designing the formal homepage. Current main-ready is a hold screen
  only. Menu persistence and large canvas/homepage reads stay on App HTTP;
  Brain RPC is compact in-room control; ECP is the broad embodied-control
  protocol plane, not a single DataChannel. Existing LiveKit stability coverage
  is partial: silent keepalive, chokepoint shutdown, route-aware mic republish,
  background FSM, AR/video tiers, audio-route Brain RPC publication, ECP event
  payload parsing, and fresh-token reconnect/backoff now exist, but production
  gaps remain in 2D pause policy, degraded HUD, and phone evidence.
  The App TODO board now has a binding execution order. Current checkpoint:
  FormalMainReadyGate owns `ReportRunning()` and self-reevaluates while waiting
  so missing one-shot loader events degrade instead of silently hanging.
  FormalHomeHudController reports `hud_loaded`, FormalHomeMenuLoader reports
  `menu_snapshot_loaded` from App HTTP `/api/app/canvas` only after a real
  workspace/menu shell payload is parsed, FormalModelReadyReporter reports
  `model_resolved` from Resources manifests, FormalModelPlacementController
  owns first placement plus `onGosloPlaced`, waits for
  `FormalMainReadyGate.IsReady`, tries AR plane raycast placement first, and
  loads the selected runtime visual from `Resources/Models/**` when available
  before falling back to whitebox/manual preview placement under
  `AssetPreviewStage`,
  FormalArRuntimeBootstrap mounts ARSession, XROrigin, ARRaycastManager,
  ARPlaneManager, TrackedPoseDriver, and ARCameraManager/ARCameraBackground for the formal scene,
  XRGeneralSettings automatic init/loading/running stays disabled for Android,
  iPhone, and Standalone while the formal bootstrap owns mobile AR startup, and
  FormalArSessionBaselineReporter owns
  `ar_session_baseline_clean` by waiting for mobile `ARSessionState.SessionTracking`. The home menu/model/AR
  reporters catch up if mounted after `OnMainUiReady`, so dynamic service
  resolution does not leave the App stuck on missing gates. START while already
  connected to a Tier1/LineB-changing Room now uses graceful shutdown plus fresh
  Mint reconnect instead of hard-failing. Next App
  work should verify and extend the first formal touch menu/tool drawer, then
  add production model placement from the App HTTP/RPC/ECP boundaries, not from
  Smoke UI. Runtime-used model visuals are separated from source/import
  staging: manifests resolve `Resources/Models/**`, while
  `Assets/ParrotApp/Models/**` is not a completion signal by itself. The first
  formal HUD/menu implementation Ref is
  `backend_interface_map/app/formal_homepage_hud_menu_plan_20260515.md`.
  Current first slices: `FormalHomeMenuController` renders App HTTP canvas
  modules/workspaces/tools/notes into a formal landscape drawer; workspace tabs
  and quick camera/photo-awareness/XR-hand controls delegate through
  `AppStartupFlowController` compact RPC wrappers only after Brain is present.
  `FormalHomeHudController` now shows startup failure, menu loader failure, and
  reconnect-pending state in the home status line. The menu loader now also
  reads `/api/app/personas` and `/api/app/line-profiles` for read-only selector
  status rows; selector edit/apply still needs an owner flow. Workspace tabs
  pass App HTTP `layout_kind` into `AppStartupFlowController`, and
  `2d_workspace` now applies `VoiceOnlyNoVideo` before `applyWorkspace`, pausing
  AR/video without disconnecting the LiveKit room. `FormalHomeToolController`
  now owns the first CAM/MAG/BOX toolbar slice: CAM delegates to
  `PhotoController` only when `photoUploadUrl` (or host/port) is phone-safe,
  MAG emits Focus ECP events, and BOX emits BBox ECP events. It does not call
  Brain RPC, `captureSnapshot`, `identify_object`, menu persistence, or Smoke
  UI. Generic tool cards and durable save/edit affordances remain read-only
  until their owner action is explicitly wired. The Settings quick actions now include a model placement
  button that delegates to `FormalModelPlacementController`; runtime GOSLO/Ner
  visuals are attempted before whitebox fallback. `FormalModelRemoteController`
  now provides a local-only bottom-left joystick after placement, routing Ner to
  `spine_walk` and GOSLO to local walk handlers without Brain RPC.
  `FormalXrHandPerchController` now mounts the formal local hand-perch owner
  after main-ready and placement, but it degrades to package-missing/debug-only
  until `com.unity.xr.hands` / `UNITY_XR_HANDS` and phone proof exist. Model
  animation expansion remains pending.
- 2026-05-15 input-device continuation: formal Settings now exposes local
  `MIC NEXT` / `MIC AUTO` controls that update `MicrophonePublisher`'s Unity
  `Microphone.devices` preference and republish the LiveKit mic track when
  connected. This remains a Unity device-name preference, not native Android
  route forcing; iQOO Neo9 SCO/A2DP/wired/speaker logs are still required before
  calling audio switching stable.
- 2026-05-13 homepage/LiveKit continuation audit: Brain RPC testing does not
  require phone or voice, but it does require a Brain / LiveKit Agents
  participant in the same room. Phone/device testing is still required for AR
  camera, microphone permission, Bluetooth route switching, app switching, and
  full voice media. `UI/AppV1SmokeReferenceUiController.cs` is now classified as a
  legacy Smoke/reference controller, not formal homepage evidence; useful HUD,
  tool drawer, camera, workdesk, note, Focus, and BBox ideas must be re-bound to
  the formal startup/lifecycle contracts before use.

## App Frontend Longline

1. **调研**：read the source design docs, HTML sketches, interface docs, Unity Build Settings, existing scenes, assets, and App scripts before implementation.
2. **启动页**：implement the landscape startup page with `GOSLO Parrot`, `SCENE`, `START`, Mode lever, and model portrait slot.
3. **Room Setting**：complete the preset/config page with saved Room/RoomProfile, Model, Room, Persona, Line, Theme/skin, and Maid Team selectors. The startup lever is `experience_mode`; GOSLO behavior flags stay runtime-owned.
4. **启动转场**：create an independent IPoAC progress page; permission checks, Mint, and LiveKit connect run during this transition. Successful connect must stay silent.
5. **AR 主界面**：add a formal App scene to Build Settings and stop treating the smoke scene as the App entry.
6. **放置与问候**：after AR plane ready, wait for user placement. Only after placement should GOSLO wake/question and greet.
7. **HUD 与工具抽屉**：left-top HUD and right-bottom tool drawer should be low-occlusion while collapsed and useful when expanded.
8. **菜单画布**：complete Model / Persona / Mode / Scene / 2DWorkspace, then add LineB, Ner, and external module status.
9. **2D 工作区**：implement mansion hub, work desk, paper/report/calendar/photo entries; switching must not destroy LiveKit session.
10. **素材落位**：import only curated assets, record Unity import settings, and do not import the full asset package.
11. **收口报告**：keep one App V1 completion/test report with completed, partial, not complete, and next-round risk sections.

## Entry Order For New App Frontend Work

1. `codex_workspace/design_workspace/tasks/ACTIVE_CONTEXT.md`
2. `codex_workspace/app_web_parallel_workflow_20260513.md`
3. `.cursor/memory/architecture/Interface/app_web_parallel_routes_agent_team_20260513.md`
4. `codex_workspace/design_workspace/backend_interface_map/app/unity_project_inventory_app_ssot_20260513.md`
5. `codex_workspace/design_workspace/tasks/APP_WEB_PARALLEL_TODOLIST_20260513.md`
6. `codex_workspace/design_workspace/unity_ar_app/startup_menu_design_v0_20260509.md`
7. `codex_workspace/design_workspace/sketches/startup_menu_landscape_v0.html`
8. `codex_workspace/design_workspace/unity_ar_app/main_hud_landscape_v0_20260509.md`
9. `codex_workspace/design_workspace/sketches/main_hud_landscape_v0.html`
10. `.cursor/memory/architecture/Interface/app_v1_room_setting_room_profile_interface_20260510.md`
11. `codex_workspace/design_workspace/tasks/lineb_ner_gameplay_longline_todo_20260511.md` for LineB/Ner implementation planning.
12. `codex_workspace/design_workspace/tasks/ner_unity_tuning_chat_prompt_20260511.md` when opening a dedicated Ner prefab/device-feel tuning chat.
13. Backend interface documents only after the page flow is understood.

## Route Rules

- Page design and App flow decisions come first from this Design workspace.
- Cursor memory is backend/protocol/interface context; it must not override the page flow already designed here.
- If the task is App page design or Unity frontend implementation, do not start from `ParrotSmokeScene`, Web monitor reports, or old longline/self-check docs.
- If the task changes backend protocol, DTOs, BB keys, RPC methods, or public Python surfaces, use `.cursor/memory/architecture/Interface/INDEX.md`.
