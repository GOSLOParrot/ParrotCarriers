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
| `unity/ArSpike/Assets/ParrotApp/Resources/` | Runtime-loadable App config, manifests, and current runtime model visuals. | `Resources.Load("parrot_config")`, `Resources.Load("parrot_models/<id>")`, and model manifest `asset_path` values such as `Models/GOSLO` / `Models/Ner/NerSkin2_SkeletonData` resolve here. Real `parrot_config.json` is gitignored. |
| `unity/ArSpike/Assets/ParrotApp/Models/` | Formal App model source/import staging. | Keep for future imported/source assets only. Current runtime-used GOSLO/Ner visual assets live under `Resources/Models/**` so formal placement does not silently fall back to whitebox. `README.md` keeps the staging directory tracked and explains the boundary. |
| `unity/ArSpike/Assets/ParrotApp/Art/AppV1/` | Curated App V1 placeholder UI art. | Replaces old `Assets/UI/ParrotApp`. Use only curated assets, not full packs. |
| `unity/ArSpike/Assets/ParrotApp/Art/Startup/Resources/StartupPaperCraft/` | Startup whitebox runtime art. | Contains only sprites actually loaded by `ParrotAppStartupUiController` through `Resources.Load("StartupPaperCraft/<name>")`. |
| `unity/ArSpike/Assets/ParrotApp/Art/Startup/Candidates/StartupPaperCraft/` | Startup candidate art. | Not loaded at runtime. Move a file into `Resources/StartupPaperCraft/` only when code loads it and tests are updated. |
| `unity/ArSpike/Assets/ParrotApp/Prefabs/` | Formal App prefab root. | Empty roots may exist for future formal prefabs; old `Prefabs/UI` shell is removed. |

## Formal Startup Scene Mounts

`Assets/ParrotApp/Scenes/ParrotApp_Startup.unity` currently owns these root
objects:

| Object | Formal role |
|:--|:--|
| `Main Camera` | Startup UI camera and AR/video camera reference. `FormalArRuntimeBootstrap` attaches ARCameraManager/ARCameraBackground on demand from the AR baseline gate when AR Foundation is compiled. |
| `Directional Light` | Main light required for scene validity. |
| `ParrotAppRoot/StartupDesignStage` | `ParrotAppStartupUiController`; references startup flow, lifecycle, RoomManager, and AppRoomSettingClient. |
| `ParrotAppRoot/RuntimeServices` | AppLifecycleManager, RoomManager, LifecycleShutdownService, RoomManagerLifecycleBridge, LiveKitTokenMintClient, AppStartupFlowController, AppRoomSettingClient, AppHomeMenuClient, OrchestratorClient, LifecycleHeartbeatPublisher, EcpEventPublisher, AudioRouteDetector, MicrophonePublisher, ARVideoPublisher, VideoStateReporter, VideoTierReceiver, AudioRoutePolicyBrainReporter, LiveKitReconnectSupervisor, FormalMainReadyGate, FormalHomeHudController, FormalHomeMenuLoader, FormalHomeMenuController, FormalHomeToolController, FormalModelReadyReporter, FormalModelPlacementController, FormalModelRemoteController, FormalXrHandPerchController, FormalArRuntimeBootstrap, and FormalArSessionBaselineReporter. |
| `ParrotAppRoot/AssetPreviewStage` | Formal preview/model placement mount. Current first slice places a manifest-driven `Resources/Models/**` visual when available, with whitebox fallback only when a runtime asset cannot load. |

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
| `UI/FormalHomeMenuController.cs` | Formal home HUD/menu V1 renderer. | Renders the always-on compact `FormalHomeToolbar` plus separate App HTTP canvas menu and settings panels. It subscribes to `FormalHomeMenuLoader` snapshot/catalog events, keeps durable saves on HTTP, and applies workspace, camera mode, photo awareness, and XR-hand UI mode through `AppHomeMenuClient` App HTTP routes. Audio-route report remains a session diagnostic owner. MAG/BBox toolbar slots are visible but deferred/disabled. Generic tool cards remain read-only until their owner action is explicitly implemented. It must not mount or copy `AppV1SmokeReferenceUiController`. |
| `UI/FormalHomeToolController.cs` | Formal homepage CAM owner. | CAM delegates to `PhotoController.CapturePhoto()` only when main-ready/Brain/LiveKit gates pass and a phone-safe `photoUploadUrl` or host/port is configured. MAG/BBox methods return deferred status and do not mount `EcpEventPublisher`, `FocusController`, or `BBoxController`. It does not call Brain RPC, `captureSnapshot`, `identify_object`, menu persistence, or Smoke UI. |
| `LiveKit/MicrophonePublisher.cs` | Formal microphone publisher and local input-device preference owner. | Publishes the LiveKit mic track, owns the audio health producer, rebuilds the source on route changes, and accepts Settings-page `MIC NEXT` / `MIC AUTO` local device-name preference changes. A2DP remains output-only; only SCO is treated as a Bluetooth microphone route. Manual preference is local Unity runtime state, not RoomSetting or Brain policy truth. |
| `Lifecycle/FormalModelReadyReporter.cs` | Formal model manifest gate. | Resolves the selected `Resources/parrot_models/<id>` manifest and reports `model_resolved`; it must not call `onGosloPlaced`. |
| `Lifecycle/FormalModelPlacementController.cs` | Formal model placement gate owner. | Places a manifest-driven runtime visual from `Resources/Models/**` when possible, or a whitebox placeholder only as a visible fallback, under `AssetPreviewStage` after `MainUiReadyOnce` and `FormalMainReadyGate.IsReady`. It first tries AR Foundation `ARRaycastManager` against `PlaneWithinPolygon` and falls back to camera-forward preview if AR raycast is unavailable. It calls `ReportGosloPlaced()` exactly once from the placement owner. |
| `UI/FormalModelRemoteController.cs` | Formal local model joystick owner. | Shows a small bottom-left joystick only after main-ready and model placement. It is local Unity input: Ner routes to `spine_walk`, GOSLO routes to `ParrotController`/`AnimationDriver.WalkOnPlane`, and missing owners degrade to visible fallback translation. It must not call Brain RPC, mutate RoomSetting, or pretend to be XRHand fly/perch. |
| `Lifecycle/FormalXrHandPerchController.cs` | Formal XRHand/perch reflex owner. | Mounts `HandGestureSource` and attaches `PerchOnHand` only after main-ready and placed-model gates. It only enables the reflex when the selected model declares/supports `perch` and has an `AnimationDriver`; otherwise it reports `model_perch_unsupported`, `model_no_animation_driver`, or package/debug-only degraded status. `com.unity.xr.hands` / `UNITY_XR_HANDS` is still not enabled, so this is formal owner wiring, not phone proof. It must not call Brain RPC or menu persistence. |
| `Lifecycle/FormalArRuntimeBootstrap.cs` | Formal AR runtime bootstrap. | Mounted in the formal scene but does not auto-start during the startup page; creates/mounts ARSession, XROrigin, ARRaycastManager, ARPlaneManager, ARInputManager, ARCameraManager/ARCameraBackground, and Input System TrackedPoseDriver only when the AR baseline gate calls `EnsureArRuntime()`. |
| `Lifecycle/FormalArSessionBaselineReporter.cs` | Formal AR/session gate. | Reports `ar_session_baseline_clean` only after mobile `ARSessionState.SessionTracking`; it does not replace `onSceneReady`/`onGosloPlaced`. Mobile FullAR mode still requires iQOO Neo9 AR/video proof. |
| `UI/AppV1SmokeReferenceUiController.cs` | Legacy Smoke/reference UI controller. | It is mounted only by `Assets/Tests/Smoke/Editor/ParrotSmokeSceneBuilder.cs`, not by the formal startup scene. It preserves the old script GUID after the rename so test-scene references survive. It contains useful HUD/tool drawer/camera/workdesk/note/Focus/BBox ideas, but also legacy startup assumptions such as local preview flow. Do not cite it as formal homepage completion. |

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
| `unity/ArSpike/Assets/csc.rsp` | Must define `UNITY_AR_FOUNDATION` so ARVideoPublisher and formal AR bootstrap compile the AR Foundation path. |
| `unity/ArSpike/Packages/manifest.json` | Unity `2022.3.62f3`, AR Foundation/ARCore/ARKit `5.2.2`, LiveKit Unity SDK pinned to `7d868ef5cc5615c30a3ef4b73ae0dbb5cc4d6796`. |

## Test And Reference Directories

| Directory | Role | App-completion rule |
|:--|:--|:--|
| `unity/ArSpike/Assets/Tests/Smoke/**` | Smoke-scene evidence and editor builder scripts. | Useful regression evidence only; never cite as formal App completion. |
| `unity/ArSpike/Assets/Tests/NerTuning/**` | Ner mouse/device tuning scene, harness, and acceptance probes. | Test/tuning only; not a formal App scene or production prefab. |
| `unity/ParrotDev/**` | Historical Sprint 1-3 test bed. | Reference only; do not copy its runtime HUD/self-test assumptions into the formal App route. |

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
