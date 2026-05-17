# Unity Project Inventory App SSOT (2026-05-13)

Owner: Unity App chat
Status: active SSOT
Category: Unity App project inventory and directory rules
Scope: `unity/ArSpike` formal App directories, resources, tests, and cleanup rules
Sources:
- User-approved Unity project cleanup plan, 2026-05-13
- `codex_workspace/design_workspace/tasks/ACTIVE_CONTEXT.md`
- `codex_workspace/app_web_parallel_workflow_20260513.md`
- `unity/ArSpike/ProjectSettings/EditorBuildSettings.asset`
- `tests/test_unity/test_app_v1_meta_ui_static.py`

## Current Rule

`unity/ArSpike/Assets/ParrotApp/**` is the single formal Unity App center.

The old duplicate root `unity/ArSpike/Assets/Scripts/ParrotApp/**` is removed
and forbidden for new code. It was a Sprint4 migration-era script root; it is no
longer an active App directory.

Unity moves must preserve `.meta` files. If a scene, script, model, sprite, or
config asset moves, move its `.meta` alongside it so GUID references survive.

## Formal App Directories

| Directory | Role | Notes |
|:--|:--|:--|
| `unity/ArSpike/Assets/ParrotApp/Scenes/` | Formal App scenes. | Build Settings must enable `ParrotApp_Startup.unity` as the entry scene. |
| `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/` | Formal App C# runtime scripts. | Includes Backend, Config, Core, ECP, Hands, Health, Lifecycle, LiveKit, Parrot, Photo, RPC, Startup, and UI scripts. |
| `unity/ArSpike/Assets/ParrotApp/Runtime/Startup/` | Runtime startup assets. | Holds `ParrotLifecycleConfig.asset`; startup UI code lives under `Runtime/Scripts/Startup/`. |
| `unity/ArSpike/Assets/ParrotApp/Editor/` | Formal App editor tools. | Includes audit/build helper scripts and editor-only settings such as `SpineSettings.asset`. |
| `unity/ArSpike/Assets/ParrotApp/Resources/` | Runtime-loadable App config, manifests, current runtime model visuals, and curated runtime AR template assets. | `Resources.Load("parrot_config")`, `Resources.Load("parrot_models/<id>")`, model manifest `asset_path` values such as `Models/GOSLO` / `Models/Ner/NerSkin2_SkeletonData`, and `Resources.Load("ARMobileTemplate/Prefabs/ARFeatheredPlane")` resolve here. Real `parrot_config.json` is gitignored. |
| `unity/ArSpike/Assets/ParrotApp/Models/` | Formal App model source/import staging. | Keep for future imported/source assets only. Current runtime-used GOSLO/Ner visual assets live under `Resources/Models/**` so formal placement does not silently fall back to whitebox. `README.md` keeps the staging directory tracked and explains the boundary. |
| `unity/ArSpike/Assets/ParrotApp/Art/AppV1/` | Curated App V1 placeholder UI art. | Replaces old `Assets/UI/ParrotApp`. Use only curated assets, not full packs. |
| `unity/ArSpike/Assets/ParrotApp/Art/Startup/Resources/StartupPaperCraft/` | Startup whitebox runtime art. | Contains only sprites actually loaded by `ParrotAppStartupUiController` through `Resources.Load("StartupPaperCraft/<name>")`. |
| `unity/ArSpike/Assets/ParrotApp/Art/Startup/Candidates/StartupPaperCraft/` | Startup candidate art. | Not loaded at runtime. Move a file into `Resources/StartupPaperCraft/` only when code loads it and tests are updated. |
| `unity/ArSpike/Assets/ParrotApp/Prefabs/` | Formal App prefab root. | Empty roots may exist for future formal prefabs; old `Prefabs/UI` shell is removed. |
| `unity/ArSpike/Assets/Plugins/Android/` | App-owned Android native bridge root. | Contains only the formal `ParrotAudioRoute.androidlib` route plugin and its manifest/Java bridge for APP-015.23. Do not import a full Android template, old smoke project, or unrelated native sample here. |

## Formal Startup Scene Mounts

`Assets/ParrotApp/Scenes/ParrotApp_Startup.unity` currently owns these root
objects:

| Object | Formal role |
|:--|:--|
| `Main Camera` | Startup UI camera and AR/video camera reference. `FormalArRuntimeBootstrap` attaches ARCameraManager/ARCameraBackground on demand from the AR baseline gate when AR Foundation is compiled. |
| `Directional Light` | Main light required for scene validity. |
| `ParrotAppRoot/StartupDesignStage` | `ParrotAppStartupUiController`; references startup flow, lifecycle, RoomManager, and AppRoomSettingClient. |
| `ParrotAppRoot/RuntimeServices` | AppLifecycleManager, RoomManager, LifecycleShutdownService, RoomManagerLifecycleBridge, LiveKitTokenMintClient, AppStartupFlowController, AppRoomSettingClient, AppHomeMenuClient, OrchestratorClient, LifecycleHeartbeatPublisher, EcpEventPublisher, AudioRouteDetector, MicrophonePublisher, ARVideoPublisher, VideoStateReporter, VideoTierReceiver, AudioRoutePolicyBrainReporter, LiveKitReconnectSupervisor, FormalMainReadyGate, FormalHomeHudController, FormalHomeMenuLoader, FormalHomeMenuController, FormalHomeToolController, FormalModelReadyReporter, FormalModelPlacementController, FormalModelRemoteController, FormalXrHandPerchController, FormalArRuntimeBootstrap, and FormalArSessionBaselineReporter. `AudioRouteManager` is now a formal runtime service resolved/added at startup by `AppStartupFlowController`, `MicrophonePublisher`, or `AudioRoutePolicyBrainReporter` until the serialized scene is next saved with the component mounted. |
| `ParrotAppRoot/AssetPreviewStage` | Formal model placement mount. Current first slice places a manifest-driven `Resources/Models/**` visual only after a valid placement, with whitebox fallback only when a runtime asset cannot load. |

Runtime media services are mounted in the formal scene. 2026-05-15 non-phone
Castle probes verified App HTTP RoomSetting save/apply, orchestrator prewrite,
Mint, LiveKit room join, Brain participant, business RPC, and DataChannel
heartbeat. Full completion still requires iQOO Neo9 mic/Bluetooth/app-switch,
AR/video, reconnect, and ARSession evidence.

## Runtime Script Classification

Formal runtime code lives under `Assets/ParrotApp/Runtime/Scripts/**`, but not
every script in that tree is formal-scene completion evidence.

| Script or group | Classification | Rule |
|:--|:--|:--|
| `Startup/ParrotAppStartupUiController.cs` | Formal startup shell. | Mounted by `ParrotApp_Startup.unity`; owns startup, RoomSetting whitebox, transition, and current main-ready placeholder. |
| `Lifecycle/**`, `LiveKit/**`, `Ecp/**`, `Backend/**`, `Config/**`, `Health/**` | Formal runtime services. | May be mounted by `RuntimeServices` or resolved at runtime. These are the source for lifecycle, main-ready gate ownership, LiveKit, DataChannel, RoomSetting, token, orchestrator, mic/video, and health behavior. |
| `Parrot/**`, `Attention/**`, `Photo/**`, `Hands/**`, `RPC/**` | Formal-capable runtime modules. | Useful for homepage/model/menu implementation only after the formal scene or a formal controller wires them and tests name that usage. `Photo/**` is now first wired through `UI/FormalHomeToolController.cs`; `Attention/**` remains reference-ready but is not active from formal homepage V1 until after phone stability and the backend SVA/ECP evidence contract. `RPC/**` remains compact Brain-to-Unity action handling, not menu persistence. |
| `UI/FormalHomeHudController.cs` | Formal home HUD shell. | Runtime status HUD only. It reports `hud_loaded` to `FormalMainReadyGate`; menu/toolbar/workspace/model/AR loaders remain separate. |
| `Backend/AppHomeMenuClient.cs`, `UI/FormalHomeMenuLoader.cs` | Formal home menu snapshot loader. | Loads `/api/app/canvas` through App HTTP, requires a real workspace/menu shell payload, retries bounded failures, and reports `menu_snapshot_loaded`; it does not use LiveKit RPC for full canvas snapshots and does not own final tool actions. |
| `UI/FormalHomeMenuController.cs` | Formal home HUD/menu V1 renderer. | Renders the always-on compact `FormalHomeToolbar` plus separate App HTTP canvas menu and settings panels. It subscribes to `FormalHomeMenuLoader` snapshot/catalog events, keeps durable saves on HTTP, and applies workspace, camera mode, photo awareness, and XR-hand UI mode through `AppHomeMenuClient` App HTTP routes. Audio-route report remains a session diagnostic owner. MAG/BBox toolbar slots are visible but deferred/disabled. Generic tool cards remain read-only until their owner action is explicitly implemented. Decorative panel/text/icon graphics must not block AR plane taps; only real buttons stay raycastable. It must not mount or copy `AppV1SmokeReferenceUiController`. |
| `UI/FormalHomeToolController.cs` | Formal homepage CAM owner. | CAM delegates to `PhotoController.CapturePhoto()` only when main-ready/Brain/LiveKit gates pass and a phone-safe `photoUploadUrl` or host/port is configured. MAG/BBox methods return deferred status and do not mount `EcpEventPublisher`, `FocusController`, or `BBoxController`. It does not call Brain RPC, `captureSnapshot`, `identify_object`, menu persistence, or Smoke UI. |
| `LiveKit/AudioRouteManager.cs`, `LiveKit/AndroidAudioRouteManager.cs`, `LiveKit/AudioRouteSnapshot.cs`, and `Assets/Plugins/Android/ParrotAudioRoute.androidlib/**` | Formal Android route owner V1. | Implements the approved `unity_audio_route_research_20260516.md` split: native Android owns communication-device routing, Bluetooth permission snapshots, and audio focus; Unity wrapper owns accepted snapshots/policy/debounce; `MicrophonePublisher` consumes those snapshots and serially rebuilds the local LiveKit mic track. Bluetooth is a connected-route preference, not a hard app gate: a real SCO input route may be selected as Bluetooth mic, but Bluetooth being enabled without a connected SCO route falls through to the phone communication route instead of blocking selection. This is code-complete for the first formal slice but not production-stable until iQOO Neo9 Bluetooth/SCO/A2DP, pause/resume, LineA/LineB, and other-media coexistence logs pass. |
| `LiveKit/MicrophonePublisher.cs`, `LiveKit/AndroidPcmMicrophoneSource.cs` | Formal microphone track executor. | Publishes the LiveKit mic track, owns the audio health producer, requests microphone and Android 12+ Bluetooth-connect permission when voice capture starts, and rebuilds the source on accepted `AudioRouteManager` changes. It does not reconnect the LiveKit room for route changes. `AudioRouteDetector` remains fallback/diagnostic only. Current Settings-page `MIC NEXT` / `MIC AUTO` local device-name controls are diagnostic/debug only. A2DP remains output-only and keeps the normal 48 kHz microphone policy; only SCO is treated as a Bluetooth microphone route and first tries the 16 kHz capture policy. If native Android routing is available, microphone permission is granted, and Unity `Microphone.devices` is empty, the executor prefers the formal `AndroidPcmMicrophoneSource` / `AudioRecord` fallback instead of trusting `MicrophoneSource(null)`; stale/unknown native route snapshots after granted mic permission are allowed to reach that fallback instead of blocking with `no_microphone_devices`. If Unity lists a device but the formal guard still sees `AudioRead frames=0`, the fallback attempts use `AudioRoutePreference.SystemDefault` so Bluetooth/A2DP downlink can remain active while Java captures the plain phone MIC source. AudioRecord retry rates are separate `MicrophonePublisher` attempts at 48 kHz, 44.1 kHz, and 16 kHz so each attempt constructs a matching LiveKit `RtcAudioSource`; native Java capture stays strict to the requested rate and now prefers `MediaRecorder.AudioSource.MIC` before `VOICE_COMMUNICATION` because the communication source can initialize while gating near-end capture on some phones. This avoids the LiveKit FFI `sample_rate and num_channels don't match` failure class and the automatic phone-speaker pinning caused by a forced PhoneMic override. `AndroidPcmMicrophoneSource.Start()` accepts PCM callbacks immediately during native startup and rolls back `base.Start()` if native startup fails so a half-subscribed LiveKit source cannot stick across retries. The fallback captures local Android PCM and feeds frames into LiveKit `RtcAudioSource`; it is not a Smoke-script path and must not reconnect the room, mint a token, or dispatch a Brain job. Publish success is not trusted from LiveKit transport alone: Unity-source attempts wait for both `Microphone.GetPosition(...)` and `AudioRead` frames, while native AudioRecord attempts wait for `AudioRead` frames before reporting `audio_published=true`; `audio_read_timeout` means the local source still produced no LiveKit PCM frames. Native Android snapshots must not infer active SCO capture from `AudioManager.getDevices()` availability alone: only `getCommunicationDevice()` can mark `input_route=bluetooth_sco`; otherwise connected A2DP output plus phone mic is the safer voice path. After publish succeeds, `UplinkRuntimeWatchdogLoop` checks Unity recording state when available, native AudioRecord state when that source is active, plus stale `AudioRead` frame age; stale frames or stopped recording mark audio degraded and queue a serialized local mic-track republish only. HUD/debug status exposes selected/default mic, route version, active source kind (`unity_microphone` or `android_audio_record`), native AudioRecord state/error/source, audio frame count, captured channel count, captured sample rate, peak level, last frame age, watchdog state, capture fallback status, recording state, recovery count, and last recovery reason. Manual preference is local Unity runtime state, not RoomSetting or Brain policy truth. Phone proof on iQOO Neo9 is still required before calling this production-stable. |

2026-05-17 audio SSOT addendum: output-only Bluetooth is now treated as a
valid downlink route, not a reason to force speaker/earpiece. If Android exposes
A2DP/BLE speaker/hearing-aid output but no selectable SCO/BLE headset
communication target, native route ownership clears any already-pinned
speaker/earpiece communication device and then leaves routing to Android so the
system output can remain on Bluetooth. Capture recovery tries `system_default`
first and keeps automatic AudioRecord recovery on `system_default` so Bluetooth
downlink can remain with Android while the Java bridge captures plain phone MIC.
Explicit `phone_mic` forcing is now reserved for future manual recovery.
Temporary capture fallback is sticky until user preference changes or a new
session starts; device add/remove callbacks must not undo it. This is still
pending iQOO proof.

2026-05-17 callback-thread addendum: Android AudioRecord fallback frames arrive
through a Java callback thread. Product diagnostics in
`AndroidPcmMicrophoneSource` and `MicrophonePublisher` must stay pure C# on
that path; avoid adding UnityEngine API calls to `OnNativePcmFrame()` or
`OnMicrophoneAudioRead()`.

2026-05-17 SCO/bridge diagnostics addendum: confirmed SCO routes may need a
brief Android settle window, but SCO probes must fail fast and fall through to
system/default or phone-mic recovery if no `AudioRead` frames arrive. Native
PCM bridge failures must surface as specific HUD/debug markers such as
`android_pcm_bridge_unavailable:*` or `pcm_callback_failed:*`; do not collapse
them into a generic `InvalidOperationException`, and do not reconnect the
LiveKit room to repair a local capture source failure.

2026-05-17 fake-silence addendum: fresh `AudioRead` callbacks are not enough to
call Unity microphone capture healthy if the sample peak stays at digital zero.
`MicrophonePublisher` owns this guard. When a `unity_microphone` source has
fresh frames but sustained zero peak, it degrades the local uplink and performs
a one-shot rebuild directly into Android `AudioRecord` retry attempts. HUD
`nz=` is the age since source start or latest non-zero peak; use it with
`frames/ch/readSr/peak/src/nsrc/native/nerr` during phone triage. This guard
does not change RoomSetting, App HTTP, LiveKit room identity, token mint, or
Brain job ownership.

2026-05-17 Brain RoomIO binding addendum: audible `onGosloPlaced` greeting does
not prove AgentSession audio input is listening to the current phone. LiveKit
Agents `RoomIO` can auto-select the first accepted remote participant in a
long-lived room. Brain now treats formal `onSceneReady` / `onGosloPlaced`
caller identity as the current Unity phone and calls
`session.room_io.set_participant(...)` for that identity. This belongs to the
Brain input binding layer, not Unity local audio routing: it must not trigger
LiveKit reconnect, token mint, Brain dispatch, RoomSetting changes, or Android
route preference changes.

| `Lifecycle/FormalModelReadyReporter.cs` | Formal model manifest gate. | Resolves the selected `Resources/parrot_models/<id>` manifest and reports `model_resolved`; it must not call `onGosloPlaced`. |
| `Lifecycle/FormalModelPlacementController.cs` | Formal model placement gate owner. | Places a manifest-driven runtime visual from `Resources/Models/**` when possible, or a whitebox placeholder only as a visible missing-asset fallback, under `AssetPreviewStage` after `MainUiReadyOnce` and `FormalMainReadyGate.IsReady`. It accepts the AR Mobile template `ObjectSpawner` pose from `FormalArRuntimeBootstrap`, keeps the selected RoomSetting manifest/model driver, attaches `XRGrabInteractable` + `ARTransformer` with demo bounds (`0.25` to `2.0`) and demo-like grab defaults (`ColliderPosition`, single focus, default grab transformers), normalizes model height to the manifest target over several post-spawn passes, snaps the visual bottom back to the last AR hit plane after GLB import scale / delayed bounds / pinch scaling, and refuses to fake-place when AR misses a plane. Placement still uses the AR plane for hit position, but the Parrot companion stays world-upright on horizontal placement planes instead of tilting its body to noisy blanket/desk normals; this avoids the body block looking hunched forward while preserving demo2-like tap/drag/pinch behavior. It calls `ReportGosloPlaced()` exactly once from the placement owner. Clearing an already placed model calls `ReportGosloRemovedFromView()`, reusing the in-session `2d_workspace` / `VoiceOnlyNoVideo` policy so LiveKit and the Brain job stay alive while GOSLO is no longer in view; re-placing the same model calls `ReportGosloReturnedToView()` to restore `ar_workspace` / `FullARCompanion` without a new greeting. It publishes `OnPlacementStateChanged` after place/clear/select/scale/XRI-status changes so HUD/menu/joystick state updates immediately instead of relying on delayed polling. Selected-model feedback uses a transparent white `LineRenderer` ring so it does not render as an orange slab or block the camera feed. The old custom EnhancedTouch path remains only as a guarded fallback when the XRI bridge is inactive. |
| `Parrot/AnimationDriver.cs` | Formal GOSLO procedural animation owner. | Keeps the existing Minecraft-inspired head/wing/tail/leg motion path, but the phone AR standing and on-hand poses must not blindly apply the full Minecraft Java body pitch. `GOSLO.glb` imports with a neutral body node, so the formal standing-pose `minecraftStandingBodyPitchWeight` defaults to `0f`; flying keeps `minecraftFlyingBodyPitchWeight=1f` where forward lean is intentional. This prevents the placed Parrot body cube from appearing to jut forward while preserving the rest of the Minecraft motion vocabulary. |
| `UI/FormalModelRemoteController.cs` | Formal local model joystick owner. | Shows a small bottom-left joystick only after main-ready and model placement. It is local Unity input: Ner routes to `spine_walk`, GOSLO routes to `ParrotController`/`AnimationDriver.WalkOnPlane`, and missing owners degrade to visible fallback translation. It must not call Brain RPC, mutate RoomSetting, or pretend to be XRHand fly/perch. |
| `Lifecycle/FormalXrHandPerchController.cs` | Formal XRHand/perch reflex owner. | Mounts `HandGestureSource` and attaches `PerchOnHand` only after main-ready and placed-model gates. It only enables the reflex when the selected model declares/supports `perch` and has an `AnimationDriver`; otherwise it reports `model_perch_unsupported` or `model_no_animation_driver`. `com.unity.xr.hands` and `UNITY_XR_HANDS` are now present, but this is still formal owner wiring until iQOO phone proof confirms hand tracking/perch behavior. It must not call Brain RPC or menu persistence. |
| `Lifecycle/FormalArRuntimeBootstrap.cs` | Formal AR runtime bootstrap. | Mounted in the formal scene but does not auto-start during the startup page; creates/mounts ARSession, XROrigin, ARRaycastManager, ARPlaneManager, ARInputManager, ARCameraManager/ARCameraBackground, and Input System TrackedPoseDriver only when the AR baseline gate calls `EnsureArRuntime()`. It sets XROrigin to demo2-style Device tracking with camera Y offset `0`, loads the curated AR Mobile template `ARFeatheredPlane` prefab from `Resources/ARMobileTemplate/**`, assigns it to `ARPlaneManager.planePrefab`, uses demo2 serialized detection mode `-1` via `(PlaneDetectionMode)(-1)`, keeps plane surfaces visible by default to match demo2's debug-plane slider, mounts the copied `XRI Default Input Actions` through `InputActionManager`, switches the active EventSystem to demo2-style `XRUIInputModule` with the copied `XRI UI` action map, instantiates the copied `Screen Space Ray Interactor`, and connects `ObjectSpawner` + `ARInteractorSpawnTrigger` to the formal placement owner with demo2 `spawnAsChildren=true`. The previous hand-written formal plane/point-dot visuals are not active; demo2 `SampleScene.unity` does not mount `ARPointCloudManager`, so the visible white-dot affordance is treated as the ARFeatheredPlane plane visual chain rather than a separate formal point-cloud renderer. Phone screenshots proved `Shader Graphs/ShadowReceiver` and even the App-owned shader placeholder can still end up as magenta in the current ArSpike Android build path; for phone usability, `ARFeatheredPlaneMeshVisualizerCompanion` now treats both as replaceable on Android and runtime-prefers Unity built-in transparent shaders for the actual fallback plane/occlusion materials. Demo2 ShaderGraph parity remains a follow-up after the formal phone loop is usable. |
| `Lifecycle/FormalArSessionBaselineReporter.cs` | Formal AR/session gate. | Reports `ar_session_baseline_clean` only after mobile `ARSessionState.SessionTracking`; it does not replace `onSceneReady`/`onGosloPlaced`. Mobile FullAR mode still requires iQOO Neo9 AR/video proof. |
| `Assets/Tests/Smoke/Scripts/AppV1SmokeReferenceUiController.cs` | Legacy Smoke/reference UI controller. | It is mounted only by `Assets/Tests/Smoke/Editor/ParrotSmokeSceneBuilder.cs`, not by the formal startup scene. It preserves the old script GUID after the rename and move so test-scene references survive. The file is wrapped in `#if UNITY_EDITOR`, so it remains Editor/Smoke evidence and is not compiled into the Android player. It contains useful HUD/tool drawer/camera/workdesk/note/Focus/BBox ideas, but also legacy startup assumptions such as local preview flow. Do not cite it as formal homepage completion, and do not move it back into `Assets/ParrotApp/Runtime/Scripts/**`. |
| `Assets/Tests/Smoke/Scripts/LifecycleSmokeForcer.cs` | Legacy Smoke lifecycle helper. | Editor/Smoke-only helper wrapped in `#if UNITY_EDITOR`; it must not participate in formal App lifecycle or player builds. Formal lifecycle transitions come from `RoomManager`, `FormalMainReadyGate`, and the runtime lifecycle services under `Assets/ParrotApp/Runtime/Scripts/**`. |

Cleanup status: `AppV1MetaUiController` has been renamed to
`AppV1SmokeReferenceUiController` as an explicit smoke/reference controller,
with `.meta` preserved. Static tests guard that `ParrotApp_Startup.unity` does
not mount this script. Future formal homepage work may extract approved ideas,
but must not mount or copy this controller wholesale.

## Resource Classes

| Class | Path | Runtime status | Rule |
|:--|:--|:--|:--|
| App config and model manifests | `Assets/ParrotApp/Resources/parrot_config*`, `Assets/ParrotApp/Resources/parrot_models/**` | Runtime loaded by App C# and Brain mirror. | Only config examples, gitignored local config, and `parrot_models/*.json` belong here. Phone builds must use public/ECS URLs, not `127.0.0.1`; camera capture additionally needs `photoUploadUrl` or `photoUploadHost`/`photoUploadPort` if the Brain photo upload server is exposed. |
| Runtime model visuals | `Assets/ParrotApp/Resources/Models/**` | Runtime loaded by `FormalModelPlacementController` through manifest `asset_path`. | Current active visuals are `Models/GOSLO` and `Models/Ner/NerSkin2_SkeletonData`; move `.meta` with every asset. Do not duplicate the same runtime asset under `Models/**`. |
| AR Mobile template runtime assets | `Assets/ParrotApp/Resources/ARMobileTemplate/**` | Runtime loaded by `FormalArRuntimeBootstrap` and `FormalHomeMenuController`. | Curated copy from `unity/AR Mobile demo2`: `ARFeatheredPlane` prefab, its material/shader/texture chain including `ShadowReceiver.shadergraph`, `MainLightShadowsSubgraph.shadersubgraph`, `ShadowReceiverShaderFunctions.hlsl`, `URPShadowReceiver.shader`, `InteractablePrimitive.shadergraph`, `PlaneOcclusionShader.shader`, `PlanePatternDot.png`, and the App-owned safety shader `ParrotARPlaneFallback.shader`; center cube button sprites; `XRI Default Input Actions`; and `Screen Space Ray Interactor`. The copied input actions are also bound to `XRUIInputModule` at formal AR runtime mount to match the demo2 EventSystem path. This is allowed formal runtime content because it is copied under `ParrotApp/Resources/**` and loaded by formal controllers; do not recreate top-level `Assets/MobileARTemplateAssets/**` or import the full sample scene into the active App. Current phone-usability state lets the copied demo2 ShaderGraph run only when healthy; if Android reports the graph, occlusion slot, or App-owned placeholder shader as unsafe, runtime falls back to Unity built-in transparent material with `PlanePatternDot` and a transparent no-op occlusion slot. The intended final visual path remains demo2-like transparent feathered dots; remaining visual mismatch must be fixed in the ShaderGraph/material chain after phone usability is restored. |
| AR Mobile template copied scripts | `Assets/ParrotApp/Runtime/Scripts/ARMobileTemplate/XRIStarterAssets/**` | Runtime compiled by the formal App. | Minimal copied demo2 scripts only: `ObjectSpawner.cs` and `ARInteractorSpawnTrigger.cs` with `.meta` preserved. They are allowed because `FormalArRuntimeBootstrap` uses them to reproduce the demo's screen-ray placement trigger while still routing the spawned pose into the formal RoomSetting/ModelDriver/onGosloPlaced owner. The formal runtime must keep parity-critical serialized values such as `SpawnTriggerType.SelectAttempt`, `blockSpawnWhenInteractorHasSelection=true`, `viewportPeriphery=0`, `spawnAngleRange=45`, and `spawnAsChildren=true`, but App placement currently sets `requireHorizontalUpSurface=true` so the selected Parrot cannot spawn on vertical planes near the user's head. The bootstrap must reattach both copied components and the transient spawn proxy idempotently on AR runtime mount, and must keep decorative formal UI out of raycasts so `ARInteractorSpawnTrigger` does not reject plane taps as UI touches. Do not copy the whole sample menu/controller stack or treat `SampleScene.unity` as formal evidence. |
| Startup loaded art | `Assets/ParrotApp/Art/Startup/Resources/StartupPaperCraft/**` | Runtime loaded by the formal startup page. | Must exactly match `LoadSprite("<name>")` calls in `ParrotAppStartupUiController`. |
| Startup candidate art | `Assets/ParrotApp/Art/Startup/Candidates/**` | Not runtime loaded. | Reference/parking only; do not cite as implemented UI. |
| Curated App V1 art | `Assets/ParrotApp/Art/AppV1/**` | Selected assets; currently used by smoke/test builders and future App UI work. | Formal App completion requires wiring into the formal scene or runtime controller, not merely existing here. |
| Model source/import staging | `Assets/ParrotApp/Models/**` | Not runtime loaded by the current formal scene. | Use only as a future source/import parking area. A model becomes active only after its runtime-loadable asset lives under `Resources/Models/**` or a formal prefab address is explicitly wired and tested. `README.md` is a tracked placeholder, not a runtime model. |
| Test evidence assets | `Assets/Tests/**` | Test/tuning only. | Never use as App completion evidence. |

## Project Settings

| File | Required state |
|:--|:--|
| `unity/ArSpike/ProjectSettings/EditorBuildSettings.asset` | Only `Assets/ParrotApp/Scenes/ParrotApp_Startup.unity` is enabled. `Assets/Scenes/SampleScene.unity` must not appear. |
| `unity/ArSpike/ProjectSettings/ProjectSettings.asset` | `templateDefaultScene` points to `Assets/ParrotApp/Scenes/ParrotApp_Startup.unity`; Android identity is `com.parrotcarriers.app`, product is `ParrotApp`, company is `ParrotCarriers`; Android default orientation is LandscapeLeft with portrait autorotation disabled. `insecureHttpOption: 2` is a dev-local Castle bridge so the current `http://8.216.45.45` App API/Mint/Orchestrator URLs work in phone Release builds; production must move those endpoints to HTTPS/WSS and tighten this setting. |
| `unity/ArSpike/Assets/XR/XRGeneralSettings.asset` | Android ARCore, iPhone ARKit, and Standalone providers keep `m_InitManagerOnStart: 0`, `m_AutomaticLoading: 0`, and `m_AutomaticRunning: 0`; ParrotApp START manually initializes XR/AR on mobile video modes before LiveKit video publish to avoid Editor shutdown `StopSubsystems` warnings. |
| `unity/ArSpike/Assets/csc.rsp` | Must define both `UNITY_AR_FOUNDATION` and `UNITY_XR_HANDS`; adding XR Hands must not remove the AR Foundation compile path. |
| `unity/ArSpike/Packages/manifest.json` | Unity `2022.3.62f3`, AR Foundation/ARCore/ARKit `5.2.2`, LiveKit Unity SDK pinned to `7d868ef5cc5615c30a3ef4b73ae0dbb5cc4d6796`. |

## Test And Reference Directories

| Directory | Role | App-completion rule |
|:--|:--|:--|
| `unity/ArSpike/Assets/Tests/Smoke/**` | Smoke-scene evidence and editor builder scripts. | Useful regression evidence only; never cite as formal App completion. |
| `unity/ArSpike/Assets/Tests/NerTuning/**` | Ner mouse/device tuning scene, harness, and acceptance probes. | Test/tuning only; not a formal App scene or production prefab. |
| `unity/ParrotDev/**` | Historical Sprint 1-3 test bed. | Reference only; do not copy its runtime HUD/self-test assumptions into the formal App route. |
| `unity/AR Mobile demo2/**` | Fresh Unity AR Mobile template reference project supplied by the user on 2026-05-16. | Reference source for AR Foundation plane visualization, XRI screen-ray placement, and mobile model manipulation affordances only. Curated assets/scripts may be copied into `Assets/ParrotApp/Resources/ARMobileTemplate/**` or `Assets/ParrotApp/Runtime/Scripts/ARMobileTemplate/**` with `.meta` preserved; the whole sample scene/project is not formal App completion evidence. |

## Sprint4 Migration Archive

The old `Assets/Scripts/ParrotApp/MIGRATION.md` has been moved out of Unity
import as:

`codex_workspace/design_workspace/archive/unity_parrotapp_scripts_migration_20260429.md`

Reference value:

- explains why the duplicate `Assets/Scripts/ParrotApp/**` root existed;
- records Sprint4 migration order and ParrotDev freeze rules;
- lists test-bed scripts that must not be promoted into the formal App.

It is not an active route or implementation source. When it conflicts with this
SSOT, this SSOT wins. New Unity App implementation starts from
`Assets/ParrotApp/**`, not from the archive or from `unity/ParrotDev/**`.

## 2026-05-14 Live START Script Boundary

`src/scripts/sim_unity_client.py` is an external diagnostic client, not a Unity
runtime script and not formal App scene evidence. It may be used to verify
Castle/LiveKit/Brain RPC business payloads quickly before phone testing.

Current useful scope:

- joins `parrot-main` as a `unity-*` identity;
- requests unnamed Brain dispatch through the LiveKit join token / manual
  dispatch fallback;
- verifies post-join `applyRoomProfile` and `setAppCapabilityMode` business
  payloads through `--startup-rpc-check`;
- accepts `--startup-room-profile-id` so the check can target the RoomProfile
  that matches the running Brain line.

2026-05-14 formal START note: Unity `LiveKitTokenMintClient` now normalizes a
root mint service URL to `/mint`. The latest script pass proved App HTTP
RoomSetting save/apply, orchestrator LineB prewrite, and token mint, but Castle
LiveKit rejected the token with 401 invalid token. That is a server key/secret
alignment blocker, not a Unity directory/resource completion signal. Local root
cause is `infra/livekit/livekit.yaml` using the old placeholder secret while
token-mint/Brain use the newer dev secret; local config/test guard is fixed,
but ECS still needs LiveKit config deployment and restart.

Boundary: formal startup cold-load/edit/save uses the App HTTP facade before
LiveKit connects. Brain RoomSetting read/write RPCs have been removed from
active backend code and must not be recreated as formal App scene evidence.

Pollution rule: do not copy this Python client's media, transcript, Redis, or
test-harness assumptions into the mobile Unity App. Phone behavior for iQOO
Neo9 microphone permission, Bluetooth/SCO/A2DP route changes, app switching,
AR/video publish, reconnect, and background recovery must be verified through
the formal `Assets/ParrotApp/**` runtime.

## Pollution Guards

- Formal App proof must come from `Assets/ParrotApp/Scenes/ParrotApp_Startup.unity`,
  Build Settings, runtime scripts under `Assets/ParrotApp/Runtime/Scripts/**`,
  and focused tests.
- `Assets/Tests/Smoke/**`, `Assets/Tests/NerTuning/**`, archived migration
  notes, and `unity/ParrotDev/**` are reference/test evidence only.
- A reference asset becomes a formal App asset only after the formal scene or a
  formal runtime controller loads it and the inventory tests name that usage.

## Removed Or Forbidden Paths

These paths must not be recreated in active App work:

- `unity/ArSpike/Assets/Scripts/ParrotApp/**`
- `unity/ArSpike/Assets/Scripts/**`
- `unity/ArSpike/Assets/UI/ParrotApp/**`
- `unity/ArSpike/Assets/UI/**`
- `unity/ArSpike/Assets/Models/**`
- `unity/ArSpike/Assets/NerTuningTest/**`
- `unity/ArSpike/Assets/Samples/**`
- `unity/ArSpike/Assets/MobileARTemplateAssets/**`
- `unity/ArSpike/Assets/Scenes/SampleScene.unity`
- `unity/ArSpike/Assets/TextMesh Pro/**`
- `unity/ArSpike/Assets/ParrotApp/UI/**`
- `unity/ArSpike/Assets/ParrotApp/Prefabs/UI/**`

Exception: the LiveKit Unity SDK hardcodes an editor embedder that regenerates
`unity/ArSpike/Assets/Resources/LiveKitSdkVersionInfo.txt` on refresh. That
top-level `Assets/Resources` directory is SDK-owned and must contain only
`LiveKitSdkVersionInfo.txt` plus its `.meta`. App-owned runtime resources stay
under `Assets/ParrotApp/Resources/**`; do not put `parrot_config`,
`parrot_models`, or App art/model data in top-level `Assets/Resources`.

## Update Contract

Every Unity App plan must read this SSOT before proposing or implementing work
that touches Unity scenes, scripts, resources, models, art, Build Settings, or
test scenes.

After any Unity directory, scene, resource, model, Build Settings, or formal
entrypoint change, the same chat must update:

1. this SSOT when directory ownership or real resource usage changes;
2. `codex_workspace/design_workspace/tasks/APP_WEB_PARALLEL_TODOLIST_20260513.md`
   when the task status changes;
3. `codex_workspace/design_workspace/tasks/ACTIVE_CONTEXT.md` when a route
   pointer or current-truth summary changes.

If a future task needs shared App/Web or core-interface changes, write only to
`codex_workspace/design_workspace/backend_interface_map/core_interface_candidate_queue_20260513.md`
until the shared core SSOT is explicitly confirmed.

## Verification

Static guard:

```powershell
uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q
```

Focused C# parity guard:

```powershell
uv run pytest tests/test_ecp_event/test_cs_parity.py -q
```

Unity Editor/MCP guard when available:

- refresh `unity/ArSpike`;
- check Console has zero errors;
- validate startup UI, startup flow, RoomSetting client, orchestrator client,
  RoomManager/LiveKit integration, ModelDriver, and Ner controller scripts.
