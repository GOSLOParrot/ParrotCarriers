# Formal Homepage HUD / Menu V1 Plan (2026-05-15)

Owner: Unity App chat
Status: active implementation prep
Category: App business interface
Related TODO: APP-015.6, APP-015.16, APP-015.20, APP-015.21, APP-021, APP-022, APP-023, APP-024

This file is the handoff from START verification into the first formal
homepage HUD/menu implementation. It exists so the next slice can build the
real mobile App surface without copying the Smoke scene, resurrecting legacy
menu RPCs, or treating a connectivity script as phone production proof.

Read before implementing this plan:

- `unity_project_inventory_app_ssot_20260513.md`
- `unity_app_transport_interface_taxonomy_20260515.md`
- `unity_livekit_ecp_sva_data_flow_map_20260515.md`
- `unity_homepage_menu_livekit_audit_20260515.md`
- `canvas_menu_ref_workspace_app_interface_20260513.md`
- `.cursor/skills/client-sdk-unity/SKILL.md`
- `.cursor/skills/livekit-unity-lifecycle/SKILL.md`
- `.cursor/skills/livekit-unity-video-publish/IMPL_REF.md`
- `.cursor/skills/ar-foundation-api/SKILL.md`

## A. Current Completion

Startup / RoomSetting / START:

- Formal Unity entry is `unity/ArSpike/Assets/ParrotApp/Scenes/ParrotApp_Startup.unity`.
- RoomSetting uses App HTTP for snapshot, preview, new, save, and apply.
- User-facing `Theme` maps to `skin_id`; `scene_profile_id` stays an internal
  launch baseline and must not return as a desktop/indoor/outdoor manual row.
- START order is permission gate -> orchestrator Tier 1 prewrite when needed
  -> App HTTP RoomProfile apply -> Mint -> LiveKit join -> Brain participant ->
  `applyRoomProfile` -> `setAppCapabilityMode` -> DataChannel heartbeat ->
  main-ready hold/gates.
- 2026-05-15 non-phone formal probe passed App HTTP save/apply, orchestrator
  prewrite, Mint, LiveKit join, Brain presence, business-ok RPCs, and
  DataChannel heartbeat publish/delivery to a second participant.

Not complete:

- Formal homepage is only in its first shell slice. Current UI after START has
  a compact HUD, a bottom-right toolbar, and separate menu/settings panels, but
  the final model placement, full tool owner flows, and phone visual proof are
  not complete.
- Brain-side ECP ingest is not externally visible through App monitor
  `live-state` yet, even though LiveKit DataChannel delivery is proved.
- iQOO Neo9 mic permission, Bluetooth/SCO/A2DP route changes,
  background/resume, network flap, AR/video publish, and reconnect still need
  phone evidence.
- 2026-05-15 first iQOO formal package pass found phone-build blockers before a
  complete START verdict: the formal package now runs as
  `com.parrotcarriers.app`, but Release builds blocked current Castle
  `http://` App HTTP/Mint/Orchestrator endpoints until
  `ProjectSettings.asset` was changed to `insecureHttpOption: 2`. This is a
  dev-local bridge only; production endpoints should become HTTPS/WSS.
- 2026-05-15 follow-up iQOO LineA pass after rebuild produced useful formal
  phone evidence: Unity loaded `parrot_config`, RoomSetting/menu save was
  exercised through the App HTTP path, Mint/LiveKit connected, a Brain
  `agent-*` participant published audio and sent `setVideoTier`, Android phone
  mic published to LiveKit, AR video produced its first frame and published
  1280x720, and short app-switch/background transitions paused/resumed video
  state without an obvious C# or Java fatal crash in the captured log. The pass
  also exposed two formal UI issues now fixed in code: startup main-ready
  background staying visible over the formal home, and delayed RoomSetting
  preview responses making preset taps feel sticky.

## B. Reuse Inventory

### Formal App scripts to reuse or extend

| File / group | Use in homepage V1 | Rule |
|:--|:--|:--|
| `Runtime/Scripts/UI/FormalHomeHudController.cs` | Keep as the first top-left status HUD owner. Extend it to show degraded state and menu/model/AR gates, but do not make it own tool drawer logic. | Formal source. |
| `Runtime/Scripts/UI/FormalHomeMenuLoader.cs` | Keep as HTTP canvas snapshot loader and `menu_snapshot_loaded` gate reporter. It now emits snapshot success/failure events and optional persona/line-profile catalog events to the formal menu renderer. | Formal source. |
| `Runtime/Scripts/UI/FormalHomeMenuController.cs` | First formal homepage renderer: compact bottom-right toolbar plus separate App HTTP canvas menu and settings panels. Workspace switch, camera mode, photo awareness, and XR-hand UI mode now apply through `AppHomeMenuClient` App HTTP routes. Audio-route rescan/report remains a LiveKit/Brain session diagnostic until the phone stability slice decides its final owner. MAG/BBox are visible placeholders only and are deferred. | Formal source. |
| `Runtime/Scripts/UI/FormalHomeToolController.cs` | First formal CAM owner. It delegates camera/photo capture to `PhotoController`, gates capture behind main-ready + LiveKit/Brain presence, and prevents phone camera capture when the upload endpoint is still loopback. MAG/BBox methods return deferred status and do not mount Focus/BBox/ECP owners. | Formal source; no Brain RPC, no `captureSnapshot`, no `identify_object`, no Smoke UI. |
| `Runtime/Scripts/Backend/AppHomeMenuClient.cs` | App HTTP client for `/api/app/canvas`, `/api/app/personas`, `/api/app/line-profiles`, `/api/app/workspace/apply`, `/api/app/camera/mode`, `/api/app/awareness`, and `/api/app/xrhand/mode`. Do not add full-snapshot RPC paths. | Formal source. |
| `Runtime/Scripts/Lifecycle/FormalMainReadyGate.cs` | Keep as the only `ReportRunning()` owner. Homepage components satisfy START, LiveKit/Brain/DataChannel, HUD, menu, model, and AR/session gates; they do not bypass this gate. Mic/video publish readiness is health/HUD-degraded state, not a blocker that keeps the startup hold surface over the AR home. | Formal source. |
| `Runtime/Scripts/Lifecycle/FormalModelReadyReporter.cs` | Reuse for manifest resolution before placing model UI. It reports only `model_resolved`. | Formal source. |
| `Runtime/Scripts/Lifecycle/FormalModelPlacementController.cs` | First formal placement owner: after `MainUiReadyOnce` and `FormalMainReadyGate.IsReady`, tries AR Foundation plane raycast placement, loads the selected manifest visual from `Resources/Models/**` when available, immediately bootstraps its manifest controller, uses EnhancedTouch for demo2-like tap placement/selection, one-finger drag on AR planes, pinch scale with 0.25-2.0 bounds, refuses to fake-place when AR misses a plane, uses a whitebox only after a valid placement when the runtime asset cannot load, and then triggers `onGosloPlaced` through `AppStartupFlowController.ReportGosloPlaced()`. | Formal source; phone proof still pending. |
| `Runtime/Scripts/UI/FormalModelRemoteController.cs` | First local model remote owner: a small bottom-left joystick appears after main-ready and placement. It routes Ner to `spine_walk`, GOSLO to `ParrotController`/`AnimationDriver.WalkOnPlane`, and degrades visibly to local translation when no owner exists. | Formal source; local-only, no Brain RPC or menu persistence. |
| `Runtime/Scripts/Lifecycle/FormalXrHandPerchController.cs` | First formal hand-perch owner: mounts `HandGestureSource`, gates `PerchOnHand` behind main-ready + placed model + manifest/controller `perch` support + `AnimationDriver`, and reports debug-only/package-missing degraded status when `UNITY_XR_HANDS` is unavailable. | Formal source; no Brain RPC/menu persistence, and not phone proof until XR Hands package/define and iQOO Neo9 logs exist. |
| `Runtime/Scripts/Lifecycle/FormalArRuntimeBootstrap.cs` and `FormalArSessionBaselineReporter.cs` | Keep AR runtime bootstrap behind the AR/session gate, not during the startup page. The bootstrap mounts XROrigin, ARRaycastManager, ARPlaneManager, camera managers, ARInputManager, Input System TrackedPoseDriver, and the imported Unity AR Mobile template `ARFeatheredPlane` visual chain for formal AR placement/video. The previous hand-written plane mesh and point-dot visuals are removed. | Formal source. |
| `Runtime/Scripts/LiveKit/**` | Reuse RoomManager, fresh-token reconnect supervisor, mic/video publishers, audio route policy reporter, video tier receiver. | Formal source; phone proof still pending. |
| `Runtime/Scripts/Ecp/**` | Reuse heartbeat, state/event publisher, event dispatcher, object-payload parser. | Formal ECP source; no full menu dumps. |
| `Runtime/Scripts/Attention/**`, `Photo/**`, `Hands/**` | Photo is first wired by `FormalHomeToolController`; Hands is first wired by `FormalXrHandPerchController`. Attention/BBox modules remain reference-ready but are not active from formal homepage V1 until after phone stability and the backend SVA/ECP evidence upgrade. | Formal-capable modules. Phone proof and richer interaction design are still pending. |
| `Runtime/Scripts/Parrot/**` | Reuse model controller and Ner/GOSLO capability scripts for model placement and interactions. | Needs formal prefab/controller wiring. |
| `Runtime/Scripts/RPC/ParrotRpcHandler.cs` | Keep Brain-to-Unity compact action handlers such as `flyTo`, `animate`, `setVideoTier`. | Do not add storage/menu persistence here. |

### Reference-only scripts

| File / group | Reference value | Production rule |
|:--|:--|:--|
| `Runtime/Scripts/UI/AppV1SmokeReferenceUiController.cs` | HUD zones, tool drawer open/close, paper note stack, camera overlay, Focus/BBox overlay ideas, workspace panel, joystick interaction sketch. | Reference only. Do not mount it, subclass it, or use it as formal completion evidence. Extract only small, reviewed patterns into new formal controllers. |
| `Assets/Tests/Smoke/**` | Smoke builder shows how old AppV1 sprites were assigned and how Focus/BBox/Photo were demoed. | Test evidence only. |
| `Assets/Tests/NerTuning/**` | Ner cheek/pickup/walk tuning and acceptance probes. | Test/tuning only; do not copy mouse harness or scene builder into mobile homepage. |
| `unity/ParrotDev/**` and Sprint4 migration archive | Script lineage and freeze rules. | Historical reference only. |

### Assets

| Path | Homepage V1 use | Rule |
|:--|:--|:--|
| `Assets/ParrotApp/Art/AppV1/ToolCabinet/**` | First toolbar/menu button whitebox art. | Curated App V1 asset. Formal use starts only when loaded by the new formal renderer. |
| `Assets/ParrotApp/Art/AppV1/Notifications/**` | Paper note/ref cards and degraded/error notes. | Curated App V1 asset. |
| `Assets/ParrotApp/Art/AppV1/Icons/**` | Placeholder icons for camera, Focus, BBox, tool state. | Use as icon sheets/placeholders; do not over-promise final art. |
| `Assets/ParrotApp/Art/AppV1/Workspace/**` and `Transitions/**` | Slot roots only. | Empty/slot roots are not completion evidence. |
| `Assets/ParrotApp/Art/Startup/Resources/StartupPaperCraft/**` | Startup style reference and possible shared paper/wood sprites if the visual language stays consistent. | Already runtime-loaded by startup; avoid coupling homepage to startup-only sprite names unless deliberate. |
| `Assets/ParrotApp/Art/Startup/Candidates/**` | Parking/reference. | Not runtime loaded. |
| `Assets/ParrotApp/Resources/parrot_models/**` | Model manifest selection for `FormalModelReadyReporter`. | Runtime source. |
| `Assets/ParrotApp/Resources/Models/GOSLO.glb`, `Assets/ParrotApp/Resources/Models/Ner/**` | Runtime-loadable GOSLO/Ner visual assets used by formal placement. | Manifest `asset_path` values resolve here; whitebox is now only a fallback/error state. |
| `Assets/ParrotApp/Resources/ARMobileTemplate/**` | Curated AR Mobile template runtime assets copied from `unity/AR Mobile demo2`: `ARFeatheredPlane`, plane materials/shaders/textures, and center cube button sprites. | Formal runtime source for plane visualization and the demo-like place affordance. Do not import the whole template scene or top-level `MobileARTemplateAssets` root into the active App. |
| `Assets/ParrotApp/Models/**` | Source/import staging only. | Do not cite this as runtime completion until a future formal prefab/addressing path is explicitly wired. |

Search result note: no explicit formal "Minecraft" namespace or asset was found
under `Assets/ParrotApp/**`. The useful game-like references are the AppV1
pixel/wood/paper slots, `ParrotController` joystick walk, and Ner
cheek/pickup/walk capability code.

## C. Transport / Interface Rules For Homepage

Use App HTTP for:

- `GET /api/app/canvas`
- `GET /api/app/modules`
- `GET /api/app/tool-cabinet`
- `GET /api/app/assets`
- `GET /api/app/personas`
- `GET /api/app/line-profiles`
- `GET /api/app/live-state`
- future menu/profile save/load and persistent edits.

Use LiveKit RPC only after Brain is present for compact in-room controls:

- `applyWorkspace`
- `setAppCapabilityMode`
- `setPhotoAwareness`
- `setCameraMode`
- `setXrHandMode`
- `setLineBAudioRoutePolicy`
- placement/session gates such as `onSceneReady` and `onGosloPlaced`
- Brain-to-Unity action handlers such as `flyTo`, `animate`, `setVideoTier`.

Use ECP/DataChannel for:

- periodic `EcpState` and connection health;
- `EcpEvent` facts such as Focus/BBox/photo/sighting artifacts;
- lossy interaction ticks where only current tendency matters;
- command causality and ack/state linkage when the formal ECP command bridge is
  implemented.

Do not use RPC/ECP for:

- full RoomSetting snapshot;
- full `canvas_snapshot`;
- persistent RoomSetting/menu/preset save;
- large selector lists;
- binary assets or model/art payloads.

## D. Homepage V1 Implementation TODO

| Order | TODO | Owner surface | Done when |
|:--|:--|:--|:--|
| 1 | Keep status documents honest. Non-phone START is a transport/business proof, not phone stability or final homepage proof. | TODO board + startup doc | APP-013/APP-014 wording no longer claims main-ready/homepage or phone proof. |
| 2 | Add a formal menu renderer/controller next to `FormalHomeMenuLoader`. | `FormalHomeMenuController.cs` | It consumes `AppCanvasSnapshotDto` from the HTTP loader and renders first toolbar plus separate menu/settings panels without Smoke UI. |
| 3 | Extend the HUD to show gate/degraded state clearly. | `FormalHomeHudController` | Missing App API, no Brain, heartbeat gap, menu load failure, model missing, AR unsupported, and reconnecting states are visible without claiming success. |
| 4 | Render first App HTTP canvas data. | `AppHomeMenuClient` + formal menu renderer | Workspaces, module statuses, tool cabinet, paper notes/photo refs render from `/api/app/canvas`; empty/malformed payload degrades. |
| 5 | Add first touch toolbar/settings controls. | Formal menu renderer + App HTTP menu client | Buttons exist for camera, magnifier, BBox, canvas menu, 2D workspace, settings, photo awareness, XR hand mode, and audio route status/manual rescan. Workspace/camera/photo-awareness/XR-hand menu apply uses App HTTP. CAM delegates to the photo owner; MAG/BBox are disabled/deferred placeholders until phone stability and backend SVA/ECP evidence design. |
| 6 | Keep persistence on HTTP. | App HTTP client | Any save/load/edit affordance calls App HTTP or stays disabled with a clear "not implemented" state; no old menu RPC wrappers return. |
| 7 | Wire model placement placeholder. | Formal model/menu controller + model manifests | Model manifest is shown; placement stays gated by AR/model readiness and does not call `onGosloPlaced` until the user actually places/accepts. |
| 8 | Add 2D workspace pause policy hook. | Lifecycle + menu controller + LiveKit publishers | 2D workspace can request silent/session-hold policy without disconnecting; mic/video pause/resume states are visible. |
| 9 | Add static guards. | `tests/test_unity/test_app_v1_meta_ui_static.py` or focused tests | Formal scene still does not mount Smoke UI; homepage uses App HTTP canvas; no old menu RPC wrapper strings are reintroduced. |
| 10 | Run phone pass. | APP-015.8 / APP-024 | iQOO Neo9 logs prove mic, Bluetooth/SCO/A2DP, app switch/resume, network flap, AR/video, reconnect, and no fake success. |

## E. First Slice Acceptance

The first formal homepage HUD/menu slice can be considered implemented when:

- START reaches the main-ready hold only after HTTP apply, LiveKit, Brain,
  business-ok RPCs, and heartbeat are satisfied.
- A formal HUD is visible in iQOO Neo9 landscape proportions and reports real
  gates/degraded states.
- A formal toolbar is always visible, while menu/settings surfaces open
  separately and render `/api/app/canvas` workspaces, module statuses, and tool
  cards from App HTTP.
- No full menu/canvas snapshot is fetched through LiveKit RPC.
- `AppV1SmokeReferenceUiController` is not mounted in
  `ParrotApp_Startup.unity`.
- Missing backend/Brain/menu/model/AR surfaces fail visibly instead of becoming
  local fake success.
- Phone-only claims remain unclaimed until APP-024 evidence exists.

## F. Known Gaps

- Brain-side ECP ingest visibility needs a readable App monitor/live-state
  signal or a separate diagnostic. Current non-phone proof covers LiveKit
  delivery, not Brain persistence/BB surfacing.
- Photo/camera capture now has a first formal toolbar owner, but phone capture
  still needs the Brain photo upload server exposed through `photoUploadUrl`
  (or host/port) in the gitignored Unity config. Without that, CAM degrades
  instead of POSTing to the device's own `127.0.0.1`. `PhotoController` still
  owns `photo.taken_preview` ECP metadata and HTTP image upload; formal Unity
  must not send photo bytes through RPC.
- `identify_object` is a backend/Web/SVA upgrade, not a homepage shortcut. It
  should sample time-aligned LiveKit background video or an SVA frame cache and
  feed GOSLO Intent/L2-B with evidence refs. Do not wire the homepage camera
  button to a fake identify-object snapshot RPC.
- BBox and magnifier are deliberately deferred from formal homepage V1. The
  App HTTP canvas marks both tools `deferred_phone_stability`, toolbar taps only
  surface that state, and `FormalHomeToolController` no longer mounts
  `FocusController`/`BBoxController` or emits attention ECP. The refreshed
  SVA/ECP visual-evidence contract is a later backend/Web + phone-stability
  slice.
- Persona/LineProfile selection APIs exist or are planned through App HTTP, but
  the formal homepage selector UI is not built.
- Audio route is now visible in formal HUD/menu and the Settings panel, and can be manually rescanned/reported to Brain. Android route detection tries `AudioManager.getDevices(...)` before legacy flags and displays the source. A2DP remains output-only in Unity mic selection; only SCO prefers a Bluetooth microphone device. The Settings page now has local `MIC NEXT` / `MIC AUTO` controls that cycle `MicrophonePublisher`'s Unity device-name preference and republish the LiveKit mic track when connected. Native OS route forcing and iQOO Neo9 Bluetooth/SCO/A2DP proof are still pending.
- First formal model placement owner exists with AR raycast, no fake placement
  on AR miss, and attempts runtime GOSLO/Ner visuals from `Resources/Models/**`.
  Whitebox is now only a visible fallback after a valid placement when the
  runtime visual cannot load. First
  local joystick owner exists, and a first formal XRHand/perch owner now mounts
  the local hand source/perch reflex only when model capability and animation
  gates pass. Model animation expansion and greeting proof on phone still need
  real mobile implementation and proof.
- XRHand fly/perch is not production-ready yet: `com.unity.xr.hands` /
  `UNITY_XR_HANDS` is not enabled in the current project, so
  `FormalXrHandPerchController` can only expose a debug-only/package-missing
  degraded owner until the package/define and iQOO Neo9 proof exist. Do not
  claim hand-perch stability from Editor debug events.
- HTTPS/WSS and production auth are not solved; current public ECS config is
  personal/dev-only and stays in gitignored Unity config.

## G. No New Core Candidate

No new shared core interface is required for this first HUD/menu slice. If the
formal menu needs a new shared CanvasMenu DTO or ECP topic beyond existing
CORE-006/CORE-007 candidates, add it to
`core_interface_candidate_queue_20260513.md` first and do not edit core SSOT
directly.

## H. Implementation Checkpoint

2026-05-15 first code slice:

- Added `Runtime/Scripts/UI/FormalHomeMenuController.cs`.
- `AppStartupFlowController.ResolveServices()` now ensures the formal menu
  controller is mounted with the other RuntimeServices.
- `FormalHomeMenuLoader` now emits `OnSnapshotLoaded` and
  `OnSnapshotLoadFailed`, so rendering is driven by the real App HTTP canvas
  result.
- `AppHomeMenuClient.AppToolCardDto` now mirrors `action_endpoints`, but the
  first renderer keeps tool cards read-only. This prevents fake save/apply
  buttons before the owning App HTTP or compact RPC action is wired.
- Added first quick controls in the formal settings/menu surfaces:
  `QuickCameraMode`, `QuickPhotoAwareness`, and `QuickXrHandMode`. They call
  `AppHomeMenuClient` App HTTP routes (`/api/app/camera/mode`,
  `/api/app/awareness`, `/api/app/xrhand/mode`) and parse business failure
  responses instead of assuming request success.
- Added HTTP read-only selector catalogs for `/api/app/personas` and
  `/api/app/line-profiles`. The formal menu shows the active persona and
  line profile plus catalog availability/degraded state, but it does not save
  or apply selector changes from the homepage. Workstation HTTP check against
  Castle returned canvas `200`, two personas, and three line profiles.
- Workspace tabs now call App HTTP `/api/app/workspace/apply` through
  `AppHomeMenuClient`. The local UI waits for the HTTP business result before
  changing active workspace state. The 2D workspace video-pause/session-hold
  policy remains an explicit phone-stability follow-up rather than an implicit
  old menu RPC side effect.
- `FormalHomeHudController` now prioritizes startup failure, menu loader
  failure, and reconnect-pending state in the home status line, so degraded
  startup/home loading states are visible instead of becoming optimistic
  "ready" copy.
- Static Unity guard updated and passing:
  `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q`.

2026-05-15 toolbar shell slice:

- `FormalHomeMenuController` now defaults `openDrawerOnLoad=false`.
- The always-on homepage surface is `FormalHomeToolbar`, with placeholder
  32x32 pixel slots for camera, magnifier, BBox, canvas menu, 2D workspace, and
  settings.
- Canvas menu and settings are separate panels opened from the toolbar. The
  old large drawer no longer stays open on the main AR/camera view.
- Magnifier and BBox buttons deliberately do not call identify-object,
  captureSnapshot, any fake image RPC, or attention ECP. They open the menu
  panel and report that MAG/BOX are delayed until after phone stability.
- The 2D workspace toolbar button selects the first enabled
  `layout_kind=2d_workspace` from the App HTTP canvas snapshot, then applies it
  through `/api/app/workspace/apply`.
- Static Unity guard updated to prevent losing the toolbar shell:
  `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q`.

2026-05-15 model placement owner slice:

- Added `FormalModelPlacementController` under `Runtime/Scripts/Lifecycle/`.
  It owns the first real `onGosloPlaced` trigger, waits for
  `FormalMainReadyGate.IsReady`, and is mounted by
  `AppStartupFlowController.ResolveServices()` with the other RuntimeServices.
- The current implementation first tries `ARRaycastManager.Raycast` at screen
  center against `TrackableType.PlaneWithinPolygon`; if no AR plane is
  available it now refuses placement instead of creating a fake preview. After
  a valid placement it loads the selected manifest visual from
  `Resources/Models/**` when loadable and uses a whitebox capsule only as a
  visible missing-asset fallback under `AssetPreviewStage`.
- `FormalArRuntimeBootstrap` now also mounts an `XROrigin`, `ARRaycastManager`,
  `ARPlaneManager`, and Input System `TrackedPoseDriver`, so formal placement
  and AR camera pose have the minimum AR Foundation owner path.
- `FormalHomeMenuController` exposes a `ModelPlacementPlaceButton` in the
  Settings quick actions. The UI calls only `PlaceAtDefaultPreview()` on the
  placement owner; it does not issue raw RPC.
- `ModelDriver.ConfigureModelId()` lets runtime-created placeholders load the
  selected RoomSetting model manifest before their controller registers.
- `FormalModelRemoteController` is mounted by runtime service resolution. Its
  small bottom-left joystick appears only after main-ready and model placement,
  routes Ner to `spine_walk`, GOSLO to local walk handlers, and never calls
  Brain RPC or menu persistence.
- Static Unity guard now asserts that model ready, AR baseline, and menu code
  do not own `ReportGosloPlaced`; only placement owner triggers it:
  `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q`.

2026-05-16 AR Mobile template correction:

- User supplied `unity/AR Mobile demo2` as the fresh reference. The formal App
  now copies the demo's `ARFeatheredPlane` prefab, plane material/shader/texture
  chain, and cube button sprites into `Assets/ParrotApp/Resources/ARMobileTemplate/**`
  with `.meta` files preserved.
- `FormalArRuntimeBootstrap` loads `Resources.Load("ARMobileTemplate/Prefabs/ARFeatheredPlane")`,
  assigns it to `ARPlaneManager.planePrefab`, and requests horizontal plus
  vertical plane detection. The previous custom `FormalARPlaneVisual_` and
  `FormalARPointDot` path is removed.
- `FormalHomeMenuController` adds a bottom-center demo-like cube placement
  button using the imported template sprites. The old Settings placement
  button remains a secondary route, but the primary phone affordance now matches
  the template flow more closely.
- This is not a wholesale import of `SampleScene.unity` or the demo's object
  catalog UI. The formal App keeps its own `ModelDriver`, selected Parrot/Ner
  manifest, `onGosloPlaced`, LiveKit, and main-ready gates, so copied sample
  code cannot bypass the App lifecycle.
- Interaction parity first fix: `FormalModelPlacementController` now uses
  Input System EnhancedTouch, demo2 scale bounds (`0.25` to `2.0`), demo2
  camera-facing spawn rotation with +/-45 degree yaw, tap-to-place,
  tap-to-select, one-finger drag over AR planes, pinch-scale, and clear through
  the cube/settings placement action. This is a formal behavior-equivalent
  integration rather than a wholesale `SampleScene.unity` import, so it keeps
  the selected RoomSetting manifest, `ModelDriver`, and `onGosloPlaced` gate.
  Phone proof is still required before calling placement stable.
- Strict-copy gap recorded: demo2's full interaction chain is
  `XR Origin (AR Rig)` -> `Screen Space Ray Interactor` ->
  `ObjectSpawner` + `ARInteractorSpawnTrigger` -> `XRGrabInteractable` +
  `ARTransformer`. The formal App has copied the plane prefab/assets and now
  mirrors the behavior in `FormalModelPlacementController`, but has not yet
  imported the full XRI object-spawner/interactable prefab chain because the
  spawned object must remain the RoomSetting-selected Parrot/Ner manifest and
  must preserve LiveKit/main-ready/`onGosloPlaced` ownership. If the next phone
  pass still feels different from demo2, the next implementation slice is to
  adapt that exact XRI chain around a single manifest-backed Parrot prefab,
  not to add more hand-written gesture code.
- Static guard:
  `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28 passed.
- Unity batchmode compile audit:
  `D:\Unity\Editor\2022.3.62f3\Editor\Unity.exe -batchmode -quit -projectPath unity/ArSpike`
  now reaches `Tundra build success`; the pass fixed a `TouchPhase` ambiguity
  in the legacy Input fallback and removed trailing whitespace from
  `ProjectSettings/EditorBuildSettings.asset`.
- Phone diagnostics: `FormalHomeHudController` now shows AR baseline,
  AR Mobile template spatial-visual binding, and placement diagnostics from
  `FormalModelPlacementController.LastDiagnosticSummary` so iQOO testing can
  distinguish no-plane raycast, missing manager, drag state, selected state,
  and runtime visual source without adding test scenes or RPC probes.
- Clear/re-place diagnostics: clearing the placed model now resets the formal
  placement status to `cleared` instead of leaving the previous `placed:*`
  status in the HUD. This avoids false phone evidence when testing the demo2
  clear/place loop.
- Plane visual parity fix: the formal bootstrap now mirrors the template menu's
  default debug-slider behavior by tracking `ARFeatheredPlaneMeshVisualizerCompanion`
  instances and keeping plane surface fill hidden by default while retaining the
  template dot/pattern affordance. This removes the oversized blue overlay seen
  in the first iQOO formal screenshot without importing the whole demo menu.

2026-05-15 formal toolbar tool-owner slice:

- Added `FormalHomeToolController` under `Runtime/Scripts/UI/`.
- `AppStartupFlowController.ResolveServices()` now ensures
  `FormalHomeToolController` is mounted with the other formal RuntimeServices.
- `FormalHomeMenuController` keeps CAM active but defers MAG/BOX. CAM delegates
  to `PhotoController.CapturePhoto()`. MAG/BOX toolbar taps report
  `after phone stability` and do not call Focus/BBox owners.
- The tool owner is explicitly transport-clean: no Brain RPC, no
  `captureSnapshot`, no `identify_object`, no menu persistence, and no Smoke UI.
- `ParrotRuntimeConfig` and `parrot_config.json.example` now include optional
  `photoUploadUrl` plus host/port fields. On phone, CAM refuses loopback upload
  endpoints instead of pretending capture succeeded.
- Bugfix pass: `PhotoController` now preserves the `http`/`https` scheme from
  `photoUploadUrl` instead of always POSTing over `http`.
- 2026-05-15 correction: MAG/BBox were moved out of active homepage V1 and into
  the post-phone-stability backlog. `AppFirstVersionFacade.list_tool_cabinet()`
  marks both as disabled/deferred, `FormalHomeToolController` no longer mounts
  `FocusController`, `BBoxController`, or `EcpEventPublisher`, and static tests
  guard that no attention ECP is emitted from the formal homepage yet.
- 2026-05-15 App HTTP menu apply slice: `AppHomeMenuClient` now owns
  `/api/app/workspace/apply`, `/api/app/camera/mode`, `/api/app/awareness`, and
  `/api/app/xrhand/mode` calls for the formal menu. `FormalHomeMenuController`
  uses those methods for workspace, camera, photo awareness, and hand mode and
  only updates local labels after the HTTP business result succeeds. Selector
  rows remain read-only until a Room/Profile save/apply owner is designed.
- Castle deploy note: the local code has the new XR-hand route and deferred
  MAG/BBox tool-card state. Until deployed, ECS may still return 404 for
  `/api/app/xrhand/mode` and old enabled MAG/BBox cards in `/api/app/canvas`.
- Static Unity guard updated and passing:
  `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q`.

2026-05-15 BBox/Mag evidence-tool design intake:

- BBox and magnifier are post-phone-stability active tools, not homepage V1
  shortcuts. They must not call `captureSnapshot`, send inline image bytes over
  RPC, or invoke `identify_object` directly from Unity UI.
- The intended active flow mirrors the photo/evidence family: Unity creates a
  compact ECP/ref packet with tool kind (`bbox`, `mag`, or `focus`), region,
  pose/screen coordinates, optional `payload.timebase`, and any known
  `bbox_ref_id` / `focus_ref_id`; rendered/cropped image bytes move through
  HTTP/storage with matching metadata.
- Backend evidence alignment owns the hard part: it resolves a BBox/Focus ref
  to the matching stored asset or to the nearest time-aligned frame, then
  stages compact evidence refs for GOSLO/IntentWorkspace according to
  awareness policy. Unity should treat this as a backend receipt, not as a
  local success guess.
- Attention semantics stay separate from rendering. The tools may produce L3
  attention hints and threshold-trigger candidates, but speaking/interrupting
  GOSLO remains policy-owned by the awareness/trigger taxonomy.
- Do not model MAG/BBox as new `NodeKind` values. The App-facing concept is a
  UI/evidence tool that may create or link refs; later L2-B representation is
  controlled by graph-link policy, not by the toolbar.
- App animation note for the animation backlog: while listening, the parrot can
  use a subtle head-tilt/listening posture. This is a model/body-language
  behavior, not part of the evidence DTO.

Remaining before marking phone-ready:

- Unity Editor/phone visual pass for the new formal toolbar and panels.
- Full owner wiring for joystick/remote control, XRHand fly/perch-to-hand,
  animation/Minecraft-style
  actions, note inbox, native audio route picker/proof,
  persona/line selector
  edit/apply flows, save/load/edit affordances, and the camera-mode photo
  notification UI.
- BBox/magnifier active attention wiring is intentionally after phone stability
  and after the backend SVA/ECP visual-evidence contract report.
- Degraded HUD polish for model/AR-specific failure state and final copy.
- iQOO Neo9 mic/Bluetooth/app-switch/AR/video/workspace-pause/reconnect proof.
- Rebuild/re-run after the startup-surface and RoomSetting preview fixes to
  confirm the camera/AR background is no longer covered and preset switching
  feels responsive on device.
- Unity Editor currently warns that LiveKit's Android ARM64 FFI plugin is not
  16KB-aligned. Track this during Android 15/iQOO stability work; it is not a
  C# compile error, but it may become a native-package compatibility issue.
