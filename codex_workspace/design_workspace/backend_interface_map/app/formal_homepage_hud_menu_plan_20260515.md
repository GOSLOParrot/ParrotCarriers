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
| `Runtime/Scripts/Lifecycle/FormalModelPlacementController.cs` | First formal placement owner: after `MainUiReadyOnce` and `FormalMainReadyGate.IsReady`, tries AR Foundation plane raycast placement, loads the selected manifest visual from `Resources/Models/**` when available, immediately bootstraps its manifest controller, uses EnhancedTouch for demo2-like tap placement/selection, one-finger drag on AR planes, pinch scale as a multiplier over manifest-normalized pet height, refuses to fake-place when AR misses a plane, uses a whitebox only after a valid placement when the runtime asset cannot load, and then triggers `onGosloPlaced` through `AppStartupFlowController.ReportGosloPlaced()`. Selection affordance is a non-blocking transparent white `LineRenderer` ring, not an orange cylinder/slab mesh. | Formal source; phone proof still pending. |
| `Runtime/Scripts/UI/FormalModelRemoteController.cs` | First local model remote owner: a small bottom-left joystick appears after main-ready and placement. It routes Ner to `spine_walk`, GOSLO to `ParrotController`/`AnimationDriver.WalkOnPlane`, and degrades visibly to local translation when no owner exists. | Formal source; local-only, no Brain RPC or menu persistence. |
| `Runtime/Scripts/Lifecycle/FormalXrHandPerchController.cs` | First formal hand-perch owner: mounts `HandGestureSource`, gates `PerchOnHand` behind main-ready + placed model + manifest/controller `perch` support + `AnimationDriver`, and reports debug-only/package-missing degraded status when `UNITY_XR_HANDS` is unavailable. | Formal source; no Brain RPC/menu persistence, and not phone proof until XR Hands package/define and iQOO Neo9 logs exist. |
| `Runtime/Scripts/Lifecycle/FormalArRuntimeBootstrap.cs` and `FormalArSessionBaselineReporter.cs` | Keep AR runtime bootstrap behind the AR/session gate, not during the startup page. The bootstrap mounts XROrigin, ARRaycastManager, ARPlaneManager, camera managers, ARInputManager, Input System TrackedPoseDriver, demo2 `XRUIInputModule`, and the imported Unity AR Mobile template `ARFeatheredPlane` visual chain plus XRI screen-ray/object-spawner bridge for formal AR placement/video. The previous hand-written plane mesh and point-dot visuals are removed. Android builds keep the copied ShaderGraph by default; the runtime-safe white-dot plane material is only an emergency/null/error fallback. | Formal source. |
| `Runtime/Scripts/LiveKit/**` | Reuse RoomManager, fresh-token reconnect supervisor, mic/video publishers, audio route policy reporter, video tier receiver. | Formal source; phone proof still pending. |
| `Runtime/Scripts/Ecp/**` | Reuse heartbeat, state/event publisher, event dispatcher, object-payload parser. | Formal ECP source; no full menu dumps. |
| `Runtime/Scripts/Attention/**`, `Photo/**`, `Hands/**` | Photo is first wired by `FormalHomeToolController`; Hands is first wired by `FormalXrHandPerchController`. Attention/BBox modules remain reference-ready but are not active from formal homepage V1 until after phone stability and the backend SVA/ECP evidence upgrade. | Formal-capable modules. Phone proof and richer interaction design are still pending. |
| `Runtime/Scripts/Parrot/**` | Reuse model controller and Ner/GOSLO capability scripts for model placement and interactions. | Needs formal prefab/controller wiring. |
| `Runtime/Scripts/RPC/ParrotRpcHandler.cs` | Keep Brain-to-Unity compact action handlers such as `flyTo`, `animate`, `setVideoTier`. | Do not add storage/menu persistence here. |

### Reference-only scripts

| File / group | Reference value | Production rule |
|:--|:--|:--|
| `Assets/Tests/Smoke/Scripts/AppV1SmokeReferenceUiController.cs` | HUD zones, tool drawer open/close, paper note stack, camera overlay, Focus/BBox overlay ideas, workspace panel, joystick interaction sketch. | Reference only. Do not mount it, subclass it, or use it as formal completion evidence. Extract only small, reviewed patterns into new formal controllers. |
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
- Audio route is visible in the formal HUD/menu and Settings panel, and can be manually rescanned/reported to Brain. The first formal native route layer now exists: Android `ParrotAudioRoute.androidlib` owns communication-device routing, Bluetooth permission snapshots, and audio focus; Unity `AudioRouteManager` exposes accepted snapshots; `MicrophonePublisher` consumes those snapshots and serially rebuilds the LiveKit mic track without reconnecting the room. A2DP remains output-only in Unity mic selection and keeps the normal 48 kHz mic policy; only SCO uses the 16 kHz Bluetooth capture policy. The Settings page still has local `MIC NEXT` / `MIC AUTO` diagnostic controls that cycle `MicrophonePublisher`'s Unity device-name preference; they are not the final production audio-route UX. Route-policy RPC reporting rejects `status:error` and `result.success:false` business failures. Formal route-manager settings UI and iQOO Neo9 Bluetooth/SCO/A2DP proof are still pending.
- 2026-05-17 uplink audit fix: `MicrophonePublisher` no longer treats `PublishTrack` transport success as proven microphone capture. After publishing the local track it waits for Unity `Microphone.GetPosition(...)` to produce samples; timeout/exception unpublishes the track, reports degraded health, and shows `microphone_start_timeout` or `microphone_start_exception` in the HUD instead of fake `audio_published=true`. The formal HUD now has separate `UsingMic` and `Uplink` lines with selected/default mic device, available device count/list, publish stage, sample rate, route version, and error.
- First formal model placement owner exists with AR raycast, no fake placement
  on AR miss, and attempts runtime GOSLO/Ner visuals from `Resources/Models/**`.
  Whitebox is now only a visible fallback after a valid placement when the
  runtime visual cannot load. First
  local joystick owner exists, and a first formal XRHand/perch owner now mounts
  the local hand source/perch reflex only when model capability and animation
  gates pass. Model animation expansion and greeting proof on phone still need
  real mobile implementation and proof.
- 2026-05-17 placement size audit fix: the height-normalization pass now updates
  `_placedBaseScale` and resets `ScaleMultiplier` whenever renderer bounds are
  normalized to the manifest `default_pet_height_m`. This prevents the later
  scale application/XRI bridge from restoring the raw GLB's oversized scale.
  Delayed normalization now runs for more passes to catch late renderer/model
  driver bounds, but stops once the user intentionally pinches/scales the model.
- 2026-05-17 scale ownership fix: XRI `ARTransformer.minScale/maxScale` are
  absolute root `localScale` values, while the formal App exposes 0.25-2.0 as a
  user multiplier. `FormalModelPlacementController` now maps the transformer
  range to `_placedBaseScale * multiplier` and calls
  `AnimationDriver.RebaseBaseTransformFromCurrent()` after placement, drag,
  scale, and XRI release so GOSLO's idle/breath animation cannot restore the
  GLB import-time scale or local origin.
- 2026-05-17 standing-pose fix: `GOSLO.glb` imports with a neutral body node.
  The full Minecraft Java body pitch (`McBodyXRot`) looked like the body cube
  was jutting forward in phone AR, especially during the placement greeting.
  `AnimationDriver` now keeps standing/on-hand body pitch neutral by default
  with `minecraftStandingBodyPitchWeight=0f`, while flying keeps the forward
  lean with `minecraftFlyingBodyPitchWeight=1f`.
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
  assigns it to `ARPlaneManager.planePrefab`, matches demo2 serialized
  detection mode `-1`, and sets `XROrigin` to Device tracking with
  camera Y offset `0`. The previous custom `FormalARPlaneVisual_` and
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
- Strict-copy bridge update: the formal App now imports the demo2
  `XRI Default Input Actions`, `Screen Space Ray Interactor`, `ObjectSpawner`,
  and `ARInteractorSpawnTrigger` into `Assets/ParrotApp/**` with `.meta`
  preserved. `FormalArRuntimeBootstrap` mounts that XRI screen-ray chain at
  AR-runtime startup, enables the copied input actions through
  `InputActionManager`, switches the active EventSystem to the demo2-style
  `XRUIInputModule` with the copied `XRI UI` action map, and routes
  `ObjectSpawner` placements into
  `FormalModelPlacementController.PlaceAt(...)` so the spawned object remains
  the RoomSetting-selected Parrot/Ner manifest and still owns
  `onGosloPlaced`. Placed models now receive `XRGrabInteractable` +
  `ARTransformer` with demo-like multiplier bounds mapped onto the
  manifest-normalized root scale and demo-like grab defaults (`ColliderPosition`,
  single focus, default grab transformers) so
  selection, drag, and
  pinch-scale use the Unity AR Mobile template interaction stack instead of
  more hand-written gesture expansion. The bridge status is now surfaced in the
  HUD via `LastTemplateInteractionStatus`, and placed models keep the
  transformer in the grab starting list to avoid dynamic registration drift.
  Follow-up parity audit matched `SampleScene.unity`'s
  `ObjectSpawner.spawnAsChildren = true`; the spawned demo proxy remains
  transient and is immediately routed into the formal Parrot/Ner placement
  owner.
  Follow-up input parity audit matched demo2's `XRUIInputModule` path rather
  than the plain startup `InputSystemUIInputModule`: the formal bootstrap now
  disables the non-XRI input module after AR runtime mount, enables
  `XRUIInputModule`, and binds `Point`, `Click`, `MiddleClick`, `RightClick`,
  `ScrollWheel`, `Navigate`, `Submit`, and `Cancel` from the copied `XRI UI`
  action map so screen-ray select attempts follow the template chain.
  Follow-up origin parity audit matched demo2's `XROrigin` settings:
  `TrackingOriginMode.Device`, camera Y offset `0`, and
  `ARPlaneManager` detection mode `-1` (AR Foundation 5.2.2 exposes only
  `Horizontal`/`Vertical` enum names, so code uses `(PlaneDetectionMode)(-1)`).
  This is still not a full SampleScene UI import; phone proof is required
  before calling it stable.
- Static guard:
  `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28 passed.
- Unity batchmode compile audit:
  `D:\Unity\Editor\2022.3.62f3\Editor\Unity.exe -batchmode -quit -projectPath unity/ArSpike`
  reaches `Tundra build success`; the latest pass also validates the copied
  XRI Starter Assets and the formal XRI bridge compile inside ArSpike.
- Device status: local ADB currently reports no attached/authorized iQOO
  device, so the next acceptance step is still a phone Build & Run pass.
- Phone diagnostics: `FormalHomeHudController` now shows AR baseline,
  AR Mobile template spatial-visual binding, and placement diagnostics from
  `FormalModelPlacementController.LastDiagnosticSummary` so iQOO testing can
  distinguish no-plane raycast, missing manager, drag state, selected state,
  and runtime visual source without adding test scenes or RPC probes.
- UI raycast hygiene fix: the formal HUD/menu/tool canvases now keep
  decorative panels, status text, dots, and icons out of UI raycasts while
  leaving real buttons raycastable. This reduces false `IsPointerOverUI`
  blocks against the copied `ARInteractorSpawnTrigger` without changing the
  demo2 trigger script or adding a new gesture path.
- XRI spawner idempotency fix: `FormalArRuntimeBootstrap` now re-checks and
  reattaches both `ObjectSpawner` and `ARInteractorSpawnTrigger` on every AR
  runtime mount, even if only one cached component survived a Unity refresh or
  scene re-entry. This prevents a half-mounted `FormalARMobileTemplateObjectSpawner`
  from becoming a null-reference or silent no-place state on phone. The
  transient spawn proxy is also reparented to the current XROrigin on every
  mount so a resumed/recreated AR rig cannot keep spawning through an old
  transform root.
- Clear/re-place diagnostics: clearing the placed model now resets the formal
  placement status to `cleared` instead of leaving the previous `placed:*`
  status in the HUD. This avoids false phone evidence when testing the demo2
  clear/place loop.
- Placement state propagation: `FormalModelPlacementController` now emits
  `OnPlacementStateChanged` after place, clear, select, scale, and XRI-status
  changes. The formal HUD, menu, and joystick subscribe to that event so the
  cube button label, settings action, diagnostics, and joystick visibility
  update immediately instead of waiting for their next polling tick.
- 2026-05-17 phone-blocker fix: the on-device magenta plane pointed to an
  incomplete demo2 shader copy. `ShadowReceiverShaderFunctions.hlsl` is now
  copied into the formal `ARMobileTemplate` shader chain with its `.meta` GUID
  preserved. `goslo_default` now auto-scales to 0.16 m. Clearing the placed
  model reports the existing `2d_workspace` session policy through
  `ReportGosloRemovedFromView()` so the room/Brain job remain connected while
  GOSLO is simply out of view. Re-placing the same model restores
  `ar_workspace` / `FullARCompanion` through `ReportGosloReturnedToView()`
  without replaying the first greeting. The local joystick is now selected-model
  scoped instead of showing immediately after placement. The next rebuilt iQOO
  pass still needs to prove audible `onGosloPlaced` greeting and material parity
  on device.
- Second iQOO blocker follow-up: the copied demo ShaderGraph still failed on
  the phone until the missing shader chain was repaired. The normal target is
  still the demo2 `ARFeatheredPlane` ShaderGraph so the transparent plane,
  feathered edge, and shrinking dot pattern remain intact. If the graph still
  resolves to magenta on phone, the fallback is intentionally just a simple
  translucent white safety surface while the ShaderGraph chain is diagnosed.
  Placement is also constrained to horizontal-up planes and then
  height-normalized after the visual is active. `LastBrainRpcStatus` is
  surfaced in the HUD placement line to expose the real `onGosloPlaced` result.
- Shader migration correction: the AR Mobile template plane material was still
  missing part of the demo2 shader chain. `URPShadowReceiver.shader` and
  `InteractablePrimitive.shadergraph` are now copied under
  `Assets/ParrotApp/Resources/ARMobileTemplate/Shaders/**` with `.meta`
  preserved, and the formal `ShadowReceiver.mat` `_Texture2D` slot now points
  at the copied `PlanePatternDot` texture instead of a missing GUID. Editor
  build logs show `Shader Graphs/ShadowReceiver` compiling for `gles3`; any
  remaining phone magenta is a ShaderGraph/build/runtime parity bug. The
  runtime safe material fallback remains only as a simple translucent-white
  guard, not as the demo-effect implementation.
- Phone audio HUD correction: the temporary HUD can carry extra diagnostic
  fields until the production HUD design replaces it. It now shows
  native/fallback route source, route version, Bluetooth permission, audio
  focus/mode, selected mic device, configured sample rate, device count, local
  policy, manual pick status, and Brain audio-route report success/attempts.
  This is diagnostic display only; it does not change RoomSetting persistence
  or reconnect the LiveKit room during device switches.
- Plane visual parity fix: the formal bootstrap now mirrors the template menu's
  default debug-slider behavior by tracking `ARFeatheredPlaneMeshVisualizerCompanion`
  instances and keeping plane surface fill hidden by default while retaining the
  template dot/pattern affordance. This removes the oversized blue overlay seen
  in the first iQOO formal screenshot without importing the whole demo menu.
  The white dots visible in the user's demo screenshots come from this
  `ARFeatheredPlane` visual chain; demo2 does not mount an `ARPointCloudManager`
  in `SampleScene.unity`, so the formal App should not add a separate custom
  point-cloud renderer for this parity task.

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

2026-05-17 iQOO AR/audio triage follow-up:

- The latest phone screenshots show why the fallback must stay modest: it can
  prevent a magenta plane, but it cannot be the demo2 visual implementation.
  `showArMobileTemplatePlaneSurfaces=true` remains the intended demo2 path, and
  the fallback is a simple translucent-white surface only when the material
  resolves to a true error/fallback shader. Healthy
  `Shader Graphs/ShadowReceiver` must be allowed to run while the copied
  ShaderGraph/material chain is fixed. HUD diagnostics now include
  `LastPlaneMaterialStatus` so the next device pass reports the actual plane
  shader/fallback state.
- Follow-up fix: the demo2 prefab itself was copied correctly, but the plane has
  two material slots. The first slot is the visible dot/surface ShaderGraph; the
  second slot is an invisible `AR/Occlusion` helper. On the formal Android build
  that helper can render as a large magenta error plane while still not being
  caught by the broad ShaderGraph fallback. The formal companion now preserves
  the demo2 dot/surface slot and replaces only the mobile `AR/Occlusion` slot
  with a transparent no-op material. This is intentionally narrower than
  replacing the whole plane material and should keep the shrinking white-dot
  affordance visible.
- The HUD showed native Android `phone_mic`, microphone permission, Bluetooth
  permission, and audio focus as healthy while Unity `Microphone.devices`
  returned zero. `MicrophonePublisher` now treats the Android-only
  native-route-plus-permission state as a valid default communication input,
  labels it `android_default_microphone`, and lets
  `MicrophoneSource(null, ...)` use the current OS route instead of failing
  with `no_microphone_devices`.
- Compile fix: `FormalModelPlacementController` now imports
  `System.Collections` for its non-generic placement coroutine enumerator.
  Android route selection also treats Bluetooth as an advisory connected-device
  preference: only a real SCO input route is selected as Bluetooth mic, while
  Bluetooth being enabled without a connected route falls through to the phone
  communication device instead of blocking selection. `MIC NEXT` mirrors the
  same fallback by showing `auto:android_default_microphone` when Unity has no
  listed microphone devices but native Android routing can supply the default
  input.
- Parrot placement height is now normalized over several delayed post-spawn
  passes, not only once in the same frame, so late renderer/model-driver bounds
  can shrink the GLB/Spine visual to the manifest target before the user starts
  drag/pinch tuning.
- Follow-up fix: XRI `selectEntered` can fire as part of the same tap that
  places the model. That is focus, not proof that the user manually scaled the
  model. The placement owner now waits until at least one manifest-height pass
  succeeds before treating XRI selection as a user scale override; otherwise
  the delayed normalization loop could be skipped and the model could remain at
  importer size on phone.

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
