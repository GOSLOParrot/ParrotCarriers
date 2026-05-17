# Design Workspace Active Context

> Updated: 2026-05-17
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
- 2026-05-16 AR Mobile demo2 parity pass: formal App imported the demo2 XRI
  interaction bridge (`XRI Default Input Actions`, `Screen Space Ray
  Interactor`, `ObjectSpawner`, `ARInteractorSpawnTrigger`) under
  `Assets/ParrotApp/**`, mounts demo2-style `XRUIInputModule`, Device tracking
  origin, plane detection `-1`, and routes `ObjectSpawner` poses into the
  RoomSetting-selected Parrot/Ner placement owner. Follow-up fixes keep
  decorative formal HUD/menu/tool UI out of raycasts and align grab defaults
  closer to the demo. Placement owner now emits `OnPlacementStateChanged` so
  HUD/menu/joystick labels and visibility update immediately after place,
  clear, select, scale, or XRI-status changes. Static tests and Unity batch compilation pass, but ADB
  currently shows no attached phone; iQOO proof of plane detection, placement,
  select, drag, pinch, Bluetooth/SCO/A2DP, app switch, reconnect, and LineB
  voice remains pending.
- 2026-05-17 formal App phone-blocker follow-up: Parrot placement size was
  tightened by making manifest-height normalization refresh the placed model's
  base scale and by extending delayed normalization passes for late renderer
  bounds; this targets the repeated head-sized GLB symptom. Microphone uplink
  now has an anti-fake-success guard: after LiveKit `PublishTrack`, Unity waits
  for both `Microphone.GetPosition(...)` and LiveKit Unity
  `MicrophoneSource.AudioRead` frames before reporting audio published. Failure
  is surfaced as `microphone_start_timeout`, `microphone_start_exception`, or
  `audio_read_timeout`. The HUD now shows separate `UsingMic` and `Uplink`
  diagnostics plus audio frame count / channels / sample rate / peak so iQOO
  tests can distinguish route/device selection, SDK capture, and Brain/STT
  hearing.
- 2026-05-17 audio / LiveKit deep audit is recorded at
  `codex_workspace/design_workspace/backend_interface_map/app/unity_audio_livekit_deep_audit_20260517.md`.
  Reread conclusion: the formal route architecture is sound and must not be
  replaced by old ParrotDev/Smoke LineA connectivity scripts. The P1 remaining
  gap was steady-state uplink health after initial publish success; the formal
  `MicrophonePublisher` now has a watchdog for `Microphone.IsRecording`, stale
  `AudioReadFrameCount`, last frame age, degraded HUD state, and serial local
  mic republish without LiveKit room reconnect. Treat iQOO phone proof as the
  stability gate for Bluetooth/SCO/A2DP, pause/resume, LineA, and LineB.
- Latest iQOO blocker fix: screenshot evidence now covers both Bluetooth-on and
  Bluetooth-off routes. In both cases local capture still produced no frames
  (`Mic wait`, `frames=0`, `readSr=0`) even though the route/permission/focus
  looked valid. `MicrophonePublisher` still retries SCO at 48 kHz and can
  temporarily ask the Android route bridge for `AudioRoutePreference.SystemDefault`.
  If Unity exposes no microphone devices, or if Unity exposes a device but
  `MicrophoneSource` still times out with `AudioRead frames=0`, the final
  attempt now uses the formal `AndroidPcmMicrophoneSource` backed by Android
  `AudioRecord`. This fallback feeds PCM into the existing LiveKit local audio
  track and must remain local-only: no room reconnect, no Mint token refresh,
  and no Brain dispatch. If the native route snapshot is stale/unknown after
  permission is granted, the final AudioRecord attempt is still allowed because
  the previous phone evidence showed route labels can look valid while Unity
  capture remains silent. The AR plane now treats both the imported
  `ShadowReceiver` graph and the App-owned placeholder shader as replaceable on
  Android; runtime fallback prefers Unity built-in transparent shaders with the
  copied dot texture plus a transparent occlusion slot. Demo2 ShaderGraph parity
  remains a follow-up, but phone usability must not stay pink.
- Latest audio-route audit follow-up: Android `getDevices()` is now treated as
  an availability list, not proof of the active capture route. Native snapshots
  may report `bluetooth_sco` only when `getCommunicationDevice()` confirms SCO
  is actually selected; otherwise connected A2DP output plus phone mic is the
  safer formal voice path. The PhoneMic capture fallback is now a temporary
  native route override and does not change the user's durable App preference.
  It is intentionally sticky until the user changes route preference or the
  session restarts, because restoring Auto/Bluetooth on `device_added` /
  `device_removed` can immediately undo the fallback that made uplink work.
  This targets
  the iQOO symptom where HUD showed a Bluetooth/SCO or phone route but local
  audio frames stayed at zero. Phone proof still has to show `AudioRead`
  frames increasing before LineA/LineB voice is considered usable.
- Latest audio uplink blocker fix: iQOO showed `Mic wait` /
  `Uplink not_published` with `microphone_start_exception` during the final
  `android_audio_record` fallback, while Android route/permission/focus looked
  valid. The formal route bridge now prefers phone speaker over earpiece for
  AR companion voice fallback when no real Bluetooth SCO or wired route is
  selected. Follow-up wider audit found a LiveKit FFI sample-rate trap:
  `RtcAudioSource` rejects PCM frames whose sample rate differs from the source
  created at construction time. Therefore `MicrophonePublisher` now creates
  separate Android AudioRecord attempts for 48 kHz, 44.1 kHz, and 16 kHz, while
  native `AndroidPcmMicCapture` stays strict to the requested rate and only
  switches between `VOICE_COMMUNICATION` and raw `MIC` sources inside that
  rate. `AndroidPcmMicrophoneSource.Start()` also rolls back `base.Start()` if
  native start fails, preventing a half-subscribed LiveKit audio source from
  sticking across retries. Unity preserves the last native AudioRecord
  state/error after failed startup so the HUD can show the real Android failure
  instead of only `InvalidOperationException`. Rebuilt iQOO proof remains
  required; success means HUD `frames/ch/readSr/peak` become non-zero, not
  merely `LK on` or audible Parrot output.
- Latest greeting-only uplink fix: iQOO now proves downlink/Brain enough to play
  placement greeting, but user speech still did not drive follow-up dialogue.
  Treat this as local uplink capture / LiveKit frame delivery, not Mint or Brain
  presence. `AndroidPcmMicCapture` now prefers Android `MIC` before
  `VOICE_COMMUNICATION`, because the communication source can initialize while
  still gating or silencing near-end capture on some phones. Native state now
  includes `source_name`; `AndroidPcmMicrophoneSource.Start()` accepts Java PCM
  callbacks immediately during native startup and rolls back on exception; and
  automatic AudioRecord retries stay on `system_default` so Bluetooth/A2DP
  downlink is not pinned back to phone speaker by a forced PhoneMic override.
  Explicit PhoneMic forcing is deferred to a future manual recovery control.
  Next iQOO proof must show increasing `frames`, non-zero `ch/readSr`, and
  non-flat `peak`; if those are healthy but Brain still ignores speech, shift
  the investigation to remote track subscription / STT ingestion.
- Follow-up audio sweep: Android route ownership now recognizes BLE headset
  voice routes (`TYPE_BLE_HEADSET`) in addition to classic SCO, and fallback
  diagnostics recognize BLE speaker/hearing-aid output classes. Java
  `AndroidPcmMicCapture` now reports `pcm_callback_failed:*` instead of
  swallowing `AndroidJavaProxy` PCM callback failures. `MicrophonePublisher`
  also owns local source detach/stop/dispose after every retry because the
  pinned LiveKit Unity SDK does not stop the C# source for us on unpublish.
- Output-only Bluetooth correction: `auto` routing no longer forces
  speaker/earpiece when Android exposes Bluetooth A2DP/BLE output but no
  selectable SCO/BLE headset communication device. If an older speaker/earpiece
  communication device is already pinned, the Android bridge now clears that
  explicit selection so the system can keep Bluetooth media/downlink output
  while Unity captures from phone/default mic. The capture fallback tries
  `system_default` first so headset downlink can stay active, then only forces
  `phone_mic` on the final low-rate AudioRecord recovery attempt. iQOO proof is
  still required for both uplink frames and headset output retention.
- Audio callback-thread hygiene: native AudioRecord PCM enters via an Android
  Java callback thread. App-owned peak/channel diagnostics now use pure C# math
  instead of `Mathf.*` on that path, keeping `pcm_callback_failed:*` focused on
  actual JNI/LiveKit issues.
- Latest SCO/AudioRecord diagnostics: a confirmed Android SCO communication
  device now gets only a short settle/probe window before the formal executor
  falls through to system/default or phone-mic recovery, so a dead Bluetooth
  voice path should not stall the App through repeated full mic timeouts. If the
  native `AudioRecord` bridge is missing or not packaged into the APK, HUD/debug
  now surfaces `android_pcm_bridge_unavailable:*` rather than a generic startup
  exception. iQOO proof still requires non-zero `frames/ch/readSr/peak`, or a
  specific `native=` / `nerr=` blocker.
- Latest native PCM guard: `AndroidPcmMicCapture` now reports and exits on
  persistent zero-byte `AudioRecord.read(...)` loops as `read_zero_persistent`,
  matching the existing `read_error_persistent:*` path for negative reads. The
  Android microphone foreground service is stopped via `stopService(...)`, not a
  `startService(STOP)` command that Android may reject during pause/teardown.
  `MicrophonePublisher` now consumes those persistent native errors during the
  startup wait and preserves them as `native_audio_record_failed:*` instead of
  flattening them into generic `audio_read_timeout`, so the retry ladder and HUD
  expose the real Android capture blocker.
  Native Android device add/remove callbacks now re-apply the current
  communication-device preference while voice mode is active, and
  `system_default` remains a clear-device operation so Bluetooth/A2DP output is
  not stolen by a stale speaker pin.
  Formal Android capture now prefers the App-owned `AndroidPcmMicrophoneSource`
  before Unity `MicrophoneSource` when no manual mic device is selected, because
  LiveKit Unity / device evidence shows Unity can report local `AudioRead`
  frames while remote uplink still receives no usable mic media.
  Focus-resume is now treated as another local capture-refresh trigger: after
  app switch, permission dialog, or Bluetooth settings focus hops, Unity pulls a
  fresh route snapshot and queues/restarts only the mic source/track if needed.
  AudioRecord itself now has a zero-peak recovery branch: if the plain Android
  `MIC` source emits fresh but digitally silent frames, the next local rebuild
  retries the same AudioRecord ladder with `VOICE_COMMUNICATION` first; if that
  also stays silent, HUD/health expose `uplink_watchdog_zero_peak_android_audio_record`
  instead of calling the uplink healthy.
  Latest A2DP correction: when Android exposes Bluetooth media output but no
  selectable SCO/BLE headset communication target, the native route owner now
  keeps `MODE_NORMAL` / media routing instead of entering
  `MODE_IN_COMMUNICATION`. This is meant to preserve headset downlink and avoid
  OEM communication-stack near-end mic gating while Unity captures through the
  App-owned AudioRecord/phone MIC path. The same rule applies to
  connect-after-START device callbacks: if the route becomes A2DP-only, Android
  exits communication mode instead of merely clearing a speaker pin. Stopping
  mic publish or room disconnect also exits communication mode so stale routing
  cannot poison the next START.
- Latest phone/default route correction: the formal App no longer enters
  `MODE_IN_COMMUNICATION` just to use the phone speaker + phone mic path. If
  Android has no selectable headset communication target, the native route
  owner keeps `MODE_NORMAL` as `normal_phone_output` and lets the App-owned
  `AudioRecord` capture phone MIC frames. If a Bluetooth communication-device
  selection is rejected but Bluetooth media output exists, it also falls back to
  `normal_bt_output` instead of leaving the App in a half-communication state.
  This is still a local mic-track rebuild path only; iQOO proof must show
  non-zero `frames/ch/readSr/peak` before calling voice stable.
  Temporary native route overrides are session-local and are restored to the
  durable user preference when communication mode is disabled, so one failed
  mic recovery cannot poison the next START.
  These are local capture-lifecycle guards only and must not reconnect LiveKit,
  mint a token, or dispatch a new Brain job.
- Latest Parrot pose fix: `GOSLO.glb` was confirmed to import with a neutral
  `body` node; the body block appeared to jut forward because the formal
  `AnimationDriver` was applying the full Minecraft Java body pitch to standing
  and placement-greeting poses. Standing/on-hand body pitch now defaults to
  neutral through `minecraftStandingBodyPitchWeight=0f`, while flying still keeps
  its intentional forward lean. Follow-up placement fix keeps the companion
  world-upright on accepted horizontal AR planes instead of tilting the whole
  model to noisy blanket/desk normals. Phone proof is still required, but this
  should stop the placed model from looking hunched forward.
- Latest Brain RoomIO binding fix: iQOO now proves placement RPC/downlink well
  enough for an audible greeting, but the long-lived Castle room can still make
  LiveKit Agents auto-bind audio/video input to the first old/diagnostic remote
  participant instead of the current phone. Brain now rebinds
  `session.room_io` to the Unity `caller_identity` on `onSceneReady` and
  `onGosloPlaced`. This is not a phone-route change: no Mint, room reconnect,
  Brain dispatch, RoomSetting, or Android audio route is touched. Next proof is
  HUD non-zero uplink plus Castle logs showing `RoomIO input participant
  rebound` and transcript events from the current Unity identity.
- Latest imported frames=0 TODO implementation: the desktop audit has been
  moved to
  `backend_interface_map/app/imported_frames0_root_cause_audit_todo_20260517.md`.
  The first formal-App P0 slice is implemented without touching Smoke/ParrotDev:
  Android microphone foreground service + Android 14 microphone FGS permission,
  `AudioRecord.read<0` persistent-error exit, route-manager singleton callback
  cleanup, `setCommunicationDevice` short retry, AR video no-webcam-default and
  post-publish frame truth gate, HUD `Video src/frames/age/error`, volatile audio
  peak diagnostics, 35s shutdown cool-down, and 8s AR first-frame timeout.
  Validation passed: Java androidlib `javac`, Unity static guard 28/28, Unity MCP
  refresh with Console 0 errors. This is still not phone-stable until a rebuilt
  iQOO run proves non-zero `frames/ch/readSr/peak` and then LineA/LineB speech.
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
  so missing one-shot loader events degrade instead of silently hanging. It no
  longer treats mic/video publish health as a startup hold blocker; those remain
  HUD/health degraded states so the AR home can open for placement and route
  diagnosis.
  FormalHomeHudController reports `hud_loaded`, FormalHomeMenuLoader reports
  `menu_snapshot_loaded` from App HTTP `/api/app/canvas` only after a real
  workspace/menu shell payload is parsed, FormalModelReadyReporter reports
  `model_resolved` from Resources manifests, FormalModelPlacementController
  owns first placement plus `onGosloPlaced`, waits for
  `FormalMainReadyGate.IsReady`, tries AR plane raycast placement first,
  uses Input System EnhancedTouch, supports demo2-like tap placement/selection,
  one-finger drag over AR planes, pinch scale with 0.25-2.0 bounds, demo-style
  camera-facing spawn rotation with +/-45 degree yaw, immediately bootstraps the selected
  Parrot model controller, and loads the selected runtime visual from
  `Resources/Models/**` when available. It now refuses fake placement when AR
  plane raycast misses; whitebox is only a missing-runtime-asset fallback after
  a valid placement under `AssetPreviewStage`.
  FormalArRuntimeBootstrap mounts ARSession, XROrigin, ARRaycastManager,
  ARPlaneManager, the imported AR Mobile template `ARFeatheredPlane` plane
  visual, TrackedPoseDriver, and ARCameraManager/ARCameraBackground for the formal scene,
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
  Smoke UI. 2026-05-16 correction: the previous hand-written plane/point-dot
  visuals were removed; curated AR Mobile demo2 plane/button assets now live
  under `Assets/ParrotApp/Resources/ARMobileTemplate/**` and are loaded by
  formal controllers. The formal controller recreates the demo2 placement
  interaction semantics for the selected Parrot model without importing the
  full sample scene/object catalog, which remains reference-only.
  Runtime-used model visuals are separated from source/import
  staging: manifests resolve `Resources/Models/**`, while
  `Assets/ParrotApp/Models/**` is not a completion signal by itself. The first
  2026-05-16 batchmode compile audit found and fixed a `TouchPhase` ambiguity
  in the legacy Input fallback and trimmed `EditorBuildSettings.asset`; Unity
  script compilation now reaches `Tundra build success`. The formal HUD now
  exposes AR baseline/spatial visual status and placement diagnostics from
  `FormalModelPlacementController`, so the next iQOO run can tell no-plane,
  missing-manager, drag, selection, and visual-source states apart. Phone proof
  is still required for the AR placement behavior. The first
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
  after main-ready and placement. `com.unity.xr.hands` / `UNITY_XR_HANDS` is
  present, but phone proof for hand tracking/perch behavior is still pending.
  `Assets/csc.rsp` must keep both `UNITY_AR_FOUNDATION` and `UNITY_XR_HANDS` so
  enabling hands never disables the AR Foundation runtime path. Model animation
  expansion remains pending.
- 2026-05-15 input-device continuation: formal Settings now exposes local
  `MIC NEXT` / `MIC AUTO` controls that update `MicrophonePublisher`'s Unity
  `Microphone.devices` preference and republish the LiveKit mic track when
  connected. This remains a Unity device-name preference, not native Android
  route forcing; iQOO Neo9 SCO/A2DP/wired/speaker logs are still required before
  calling audio switching stable.
- 2026-05-16 audio-route correction: read
  `backend_interface_map/app/unity_audio_route_research_20260516.md` before
  implementing audio-device work. Old LineA/Smoke connectivity scripts proved
  mic publish and Brain room presence only; they must not define formal
  Bluetooth strategy. Formal direction is an Android-native route owner
  (`AudioManager` communication devices, audio focus, Android 12+
  `BLUETOOTH_CONNECT` as needed) plus serialized LiveKit mic-track rebuild.
  `MicrophonePublisher` remains the executor; `AudioRoutePolicyBrainReporter`
  remains Brain observation, not Brain-driven device switching.
- 2026-05-16 audio-route research round 2: public Android/LiveKit/Unity docs and
  issues now reinforce the same split. The preferred V1 is a native Android
  route bridge plus Unity policy wrapper plus serialized mic republish; route
  change is not a room reconnect reason. `MIC NEXT` / `MIC AUTO` are diagnostic
  controls until the formal route manager and settings UX are designed.
- 2026-05-16 audio-route implementation slice: created the formal App-owned
  `Assets/Plugins/Android/ParrotAudioRoute.androidlib/**` route plugin plus
  manifest permissions (`RECORD_AUDIO`, `MODIFY_AUDIO_SETTINGS`, Android 12+
  `BLUETOOTH_CONNECT`) and Java `AndroidAudioRouteManager`. Unity now has
  `AudioRouteSnapshot`, `AndroidAudioRouteManager`, and `AudioRouteManager`
  under `Assets/ParrotApp/Runtime/Scripts/LiveKit/**`; `MicrophonePublisher`
  consumes accepted route snapshots and only serially rebuilds the local mic
  track, while `AudioRoutePolicyBrainReporter` observes/reports compact Brain
  route policy. `AudioRouteDetector` remains fallback/diagnostic. Static Unity
  guard passes; phone proof is still required before calling Bluetooth/SCO/A2DP
  stable.
- 2026-05-17 audio-route review fix: native route preference changes are cached
  until voice communication mode is active, so startup/Settings observation does
  not seize communication routing before the App intends to publish microphone
  audio. The Android API-31 communication-device listener is isolated behind an
  API-31 holder while the Unity project still declares minSdk 30.
  `MicrophonePublisher` also refreshes route state on formal lifecycle resume,
  so pause/resume recovery is not dependent only on plug/unplug callbacks. The
  Android route plugin no longer imports `UnityPlayer`; C# passes Activity and
  a `AudioRouteSnapshotCallback` proxy, then marshals callbacks to Unity main
  thread. The route androidlib manifest/source Gradle file owns
  `com.parrotcarriers.audio` and disables route-library `BuildConfig`
  generation, avoiding duplicate launcher `BuildConfig` during dex merge.
  Unity MCP Android APK build now succeeds with `errors=0`, `warnings=3`.
- 2026-05-17 AR placement phone-blocker fix: the iQOO screenshot showed a
  head-sized GOSLO and magenta AR plane fill. `goslo_default.json` now enables
  manifest auto-scaling to a 0.16 m target height, and the missing demo2
  `ShadowReceiverShaderFunctions.hlsl` include is copied into
  `Assets/ParrotApp/Resources/ARMobileTemplate/Shaders/ShadowReceiver/` with
  its `.meta` GUID preserved. Clearing the first placed GOSLO now calls
  `ReportGosloRemovedFromView()`, which reuses the existing in-room
  `2d_workspace` policy (`VoiceOnlyNoVideo` + `applyWorkspace`) instead of
  disconnecting LiveKit or starting a new Brain job. Re-placing the same model
  calls `ReportGosloReturnedToView()` to restore the `ar_workspace` /
  `FullARCompanion` policy without replaying the first greeting. The local
  joystick is now selected-model scoped, so it hides after placement until the
  model is selected. Rebuilt phone proof is still required for audible
  `onGosloPlaced` greeting and final plane material parity.
- 2026-05-17 second iQOO AR blocker follow-up: the demo2 ShaderGraph material
  still rendered magenta after rebuild, so the copied
  `ARFeatheredPlaneMeshVisualizerCompanion` gained a transparent
  `PlanePatternDot` fallback for unsupported materials. Follow-up phone
  screenshot showed the ShaderGraph chain is now present, so the formal App no
  longer treats fallback as the visual goal. The root fix is the demo2
  ShaderGraph/material chain itself; Android fallback remains enabled only as a
  simple translucent white safety surface if the copied ShaderGraph still
  resolves to magenta. The XRI spawn trigger now
  requires `HorizontalUp` planes so taps do not spawn on vertical wall/curtain
  planes above the user. `FormalModelPlacementController` also performs a
  second post-placement renderer-bounds height normalization after the visual
  is active, guarding against GLB/import/XRI scale layers ignoring the manifest
  height. `AppStartupFlowController.LastBrainRpcStatus` is now shown in the HUD
  placement line, so the next phone run can distinguish "Brain connected" from
  "onGosloPlaced actually returned ok".
- 2026-05-17 shader/audio diagnostics correction: the plane ShaderGraph issue
  is not recorded as permanently unfixable. The formal AR Mobile template copy
  now includes demo2's `URPShadowReceiver.shader` and
  `InteractablePrimitive.shadergraph` with `.meta`, and `ShadowReceiver.mat`
  no longer references a missing `_Texture2D` GUID. Static/editor logs now show
  `Shader Graphs/ShadowReceiver` compiling for `gles3` without a shader error,
  so remaining phone magenta must be treated as a shader-chain/build/runtime
  parity bug to diagnose, not solved by a fancy fallback. The fallback is kept
  intentionally simple: translucent white only. `FormalHomeHudController`
  now exposes the phone audio path in more detail: native/fallback source,
  route version, Bluetooth permission, audio focus/mode, selected mic device,
  configured sample rate, device count, local route policy, manual selection,
  and Brain audio-route report success/attempts. Use these fields in the next
  iQOO LineA/LineB route test before claiming Bluetooth/SCO/A2DP stability.
- 2026-05-17 iQOO screenshot triage: HUD showed native Android route
  `phone_mic`, permission and audio focus granted, but Unity
  `Microphone.devices` returned zero and blocked publish with
  `no_microphone_devices`. `MicrophonePublisher` now allows an Android-only
  default communication input fallback when the native route manager is present
  and microphone permission is granted, passing `null` to LiveKit/Unity's
  microphone source so Android supplies the current phone/SCO/wired input. The
  HUD should show
  `android_default_microphone` instead of failing with zero devices on the next
  rebuild. Placement height normalization now runs several delayed passes after
  the spawned model is active, so late renderer/model-driver bounds can shrink
  the Parrot back to the manifest target instead of leaving a head-sized GLB.
- 2026-05-17 compile/audio fallback fix: `FormalModelPlacementController`
  explicitly imports `System.Collections` so delayed placement coroutines use
  non-generic `IEnumerator` and compile in Unity. The Android audio-route
  bridge no longer treats missing/unused `BLUETOOTH_CONNECT` or an explicit
  Bluetooth preference as a blocker for built-in phone routing: Bluetooth SCO
  is preferred only when actually available, otherwise the route falls through
  to wired/earpiece/speaker plus phone mic. The manual `MIC NEXT` diagnostic
  also resolves empty Unity device lists to `auto:android_default_microphone`
  when the native Android route can supply the default input.
- 2026-05-17 selected-plane visual correction: the latest phone screenshots
  clarified that the pink/magenta surface is the AR plane material and the
  orange surface is the selected GOSLO affordance. Formal selection feedback no
  longer uses a cylinder/slab mesh; `FormalModelPlacementController` now draws
  a transparent white `LineRenderer` ring around the selected model so it does
  not occlude the camera view. A later phone run proved the copied
  `Shader Graphs/ShadowReceiver` material can still render as Unity magenta in
  the current ArSpike Android build. `ARFeatheredPlaneMeshVisualizerCompanion`
  now uses the bundled `ParrotARPlaneFallback.shader` translucent-white shader
  for that Android graph/error path so phone AR remains usable. Demo2 visual
  parity is still the target, but it must be fixed by cleaning the copied
  ShaderGraph/material chain rather than by reintroducing custom AR visuals.
  `FormalArRuntimeBootstrap.LastPlaneMaterialStatus` is now surfaced in the
  HUD so the next phone screenshot shows whether the plane is using
  `Shader Graphs/ShadowReceiver`, `AR/Occlusion`, an error shader, or fallback.
- 2026-05-17 follow-up after iQOO no-uplink screenshots: the failure is still
  local Unity/Android capture startup, not Brain/STT. Web research confirms
  two relevant mobile risks: Unity Android Bluetooth microphone capture can
  fail even when permission and route look correct, and
  `AudioSettings.OnAudioConfigurationChanged` is not a reliable headset-change
  signal. `MicrophonePublisher` now keeps automatic recovery on
  `system_default` so Android can preserve Bluetooth/A2DP downlink while the
  fallback creates `AndroidPcmMicrophoneSource` backed by Android
  `AudioRecord`. It handles both "Unity lists no mic" and "Unity emits no or
  fake-silent frames" cases; explicit PhoneMic forcing is deferred to a manual
  recovery control. This fallback must remain local-only: no LiveKit reconnect,
  no Mint token refresh, and no Brain dispatch. The next phone run must prove
  HUD audio `frames/ch/readSr/peak/nz` and native `nsrc` diagnostics before
  voice can be treated as connected.
- 2026-05-13 homepage/LiveKit continuation audit: Brain RPC testing does not
  require phone or voice, but it does require a Brain / LiveKit Agents
  participant in the same room. Phone/device testing is still required for AR
  camera, microphone permission, Bluetooth route switching, app switching, and
  full voice media. `Assets/Tests/Smoke/Scripts/AppV1SmokeReferenceUiController.cs` is now classified as a
  legacy Smoke/reference controller, not formal homepage evidence. It and
  `LifecycleSmokeForcer.cs` are wrapped in `#if UNITY_EDITOR`, so they remain
  Editor/Smoke evidence and do not compile into Android player builds. Useful
  HUD, tool drawer, camera, workdesk, note, Focus, and BBox ideas must be
  re-bound to the formal startup/lifecycle contracts before use.
- 2026-05-17 mic diagnostic follow-up: `MicrophonePublisher` now preserves
  native fallback evidence after success and exposes `ActiveAudioSourceKind`,
  `NativeAudioRecordState`, and `NativeAudioRecordError` to the formal HUD. The
  next iQOO run should use these fields plus `frames/ch/readSr/peak` to tell
  whether the App is on Unity mic, Android AudioRecord fallback, or a started
  capture path that still emits no frames.
- 2026-05-17 fake-silence guard: fresh frames with all-zero PCM are no longer
  accepted as healthy Unity microphone capture. The watchdog degrades
  `uplink_watchdog_zero_peak_unity_microphone` and forces the next local-track
  rebuild into Android AudioRecord attempts. HUD `nz=` is the age since source
  start or latest non-zero peak.

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
