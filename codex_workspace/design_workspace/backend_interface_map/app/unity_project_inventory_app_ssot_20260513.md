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
| `unity/ArSpike/Assets/ParrotApp/Resources/` | Runtime-loadable App config/model manifests. | `Resources.Load("parrot_config")` and `Resources.Load("parrot_models/<id>")` resolve here. Real `parrot_config.json` is gitignored. |
| `unity/ArSpike/Assets/ParrotApp/Models/` | Formal App model source/imported assets. | Includes `GOSLO.glb` and Ner Spine/model assets. |
| `unity/ArSpike/Assets/ParrotApp/Art/AppV1/` | Curated App V1 placeholder UI art. | Replaces old `Assets/UI/ParrotApp`. Use only curated assets, not full packs. |
| `unity/ArSpike/Assets/ParrotApp/Art/Startup/Resources/StartupPaperCraft/` | Startup whitebox runtime art. | Contains only sprites actually loaded by `ParrotAppStartupUiController` through `Resources.Load("StartupPaperCraft/<name>")`. |
| `unity/ArSpike/Assets/ParrotApp/Art/Startup/Candidates/StartupPaperCraft/` | Startup candidate art. | Not loaded at runtime. Move a file into `Resources/StartupPaperCraft/` only when code loads it and tests are updated. |
| `unity/ArSpike/Assets/ParrotApp/Prefabs/` | Formal App prefab root. | Empty roots may exist for future formal prefabs; old `Prefabs/UI` shell is removed. |

## Formal Startup Scene Mounts

`Assets/ParrotApp/Scenes/ParrotApp_Startup.unity` currently owns these root
objects:

| Object | Formal role |
|:--|:--|
| `Main Camera` | Startup UI camera and AR/video fallback camera reference. |
| `Directional Light` | Main light required for scene validity. |
| `ParrotAppRoot/StartupDesignStage` | `ParrotAppStartupUiController`; references startup flow, lifecycle, RoomManager, and AppRoomSettingClient. |
| `ParrotAppRoot/RuntimeServices` | AppLifecycleManager, RoomManager, LifecycleShutdownService, RoomManagerLifecycleBridge, LiveKitTokenMintClient, AppStartupFlowController, AppRoomSettingClient, OrchestratorClient, LifecycleHeartbeatPublisher, AudioRouteDetector, MicrophonePublisher, ARVideoPublisher, VideoStateReporter, and VideoTierReceiver. |
| `ParrotAppRoot/AssetPreviewStage` | Empty formal preview mount for future model/art wiring. |

Runtime media services are mounted in the formal scene. 2026-05-13 smoke
verified local token mint + LiveKit room join + Unity DataChannel heartbeat
binding; full START still requires a Brain participant and a real-device
mic/video pass.

## Runtime Script Classification

Formal runtime code lives under `Assets/ParrotApp/Runtime/Scripts/**`, but not
every script in that tree is formal-scene completion evidence.

| Script or group | Classification | Rule |
|:--|:--|:--|
| `Startup/ParrotAppStartupUiController.cs` | Formal startup shell. | Mounted by `ParrotApp_Startup.unity`; owns startup, RoomSetting whitebox, transition, and current main-ready placeholder. |
| `Lifecycle/**`, `LiveKit/**`, `Ecp/**`, `Backend/**`, `Config/**`, `Health/**` | Formal runtime services. | May be mounted by `RuntimeServices` or resolved at runtime. These are the source for lifecycle, LiveKit, DataChannel, RoomSetting, token, orchestrator, mic/video, and health behavior. |
| `Parrot/**`, `Attention/**`, `Photo/**`, `Hands/**`, `RPC/**` | Formal-capable runtime modules. | Useful for homepage/model/menu implementation only after the formal scene or a formal controller wires them and tests name that usage. |
| `UI/AppV1MetaUiController.cs` | Legacy Smoke/reference UI controller. | It is currently mounted by `Assets/Tests/Smoke/Editor/ParrotSmokeSceneBuilder.cs`, not by the formal startup scene. It contains useful HUD/tool drawer/camera/workdesk/note/Focus/BBox ideas, but also legacy startup assumptions such as `Scene` RoomSetting labels and local preview flow. Do not cite it as formal homepage completion. |

Planned cleanup: demote or rename `AppV1MetaUiController` to an explicit
smoke/reference controller in a separate slice, preserving its `.meta`, updating
the Smoke builder/tests, and copying only approved homepage patterns into the
formal App controller. Until then, static tests guard that
`ParrotApp_Startup.unity` does not mount this script.

## Resource Classes

| Class | Path | Runtime status | Rule |
|:--|:--|:--|:--|
| App config and model manifests | `Assets/ParrotApp/Resources/**` | Runtime loaded by App C# and Brain mirror. | Only config examples, gitignored local config, and `parrot_models/*.json` belong here. |
| Startup loaded art | `Assets/ParrotApp/Art/Startup/Resources/StartupPaperCraft/**` | Runtime loaded by the formal startup page. | Must exactly match `LoadSprite("<name>")` calls in `ParrotAppStartupUiController`. |
| Startup candidate art | `Assets/ParrotApp/Art/Startup/Candidates/**` | Not runtime loaded. | Reference/parking only; do not cite as implemented UI. |
| Curated App V1 art | `Assets/ParrotApp/Art/AppV1/**` | Selected assets; currently used by smoke/test builders and future App UI work. | Formal App completion requires wiring into the formal scene or runtime controller, not merely existing here. |
| Model source/imports | `Assets/ParrotApp/Models/**` | Available to formal App/model work. | Raw model assets are not production-ready until prefab/controller wiring is verified. |
| Test evidence assets | `Assets/Tests/**` | Test/tuning only. | Never use as App completion evidence. |

## Project Settings

| File | Required state |
|:--|:--|
| `unity/ArSpike/ProjectSettings/EditorBuildSettings.asset` | Only `Assets/ParrotApp/Scenes/ParrotApp_Startup.unity` is enabled. `Assets/Scenes/SampleScene.unity` must not appear. |
| `unity/ArSpike/ProjectSettings/ProjectSettings.asset` | `templateDefaultScene` points to `Assets/ParrotApp/Scenes/ParrotApp_Startup.unity`. |
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
