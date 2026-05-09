---
status: active
category: frontend-audit
date: 2026-05-10
owner: Codex / App V1
scope: ArSpike real-device smoke prep, Nanobot paper reports, XRHand perch, parrot plane walk
code:
  - unity/ArSpike/Assets/Scripts/ParrotApp/UI/AppV1MetaUiController.cs
  - unity/ArSpike/Assets/Scripts/ParrotApp/Parrot/ParrotController.cs
  - unity/ArSpike/Assets/Scripts/ParrotApp/Parrot/AnimationDriver.cs
  - unity/ArSpike/Assets/Scripts/ParrotApp/Hands/HandGestureSource.cs
  - unity/ArSpike/Assets/Scripts/ParrotApp/Hands/PerchOnHand.cs
tests:
  - tests/test_unity/test_app_v1_meta_ui_static.py
---

# App V1 ArSpike Real-Device / Nanobot / XRHand Audit

## 1. Cursor docs and local code audited

- `.cursor/memory/lore/ideas.md`: Nanobot should deliver lightweight 2D pixel-style paper reports; heavy Graphiti/memory management belongs in the Web console.
- `.cursor/memory/requirements.md`: C8/C9 cover XRHand input/reflex; C11 calls out plane walking.
- `.cursor/memory/parrot_behavior_rules.md`: index-middle perch, hand-lost/fist return, local reflex boundary, and front-end predictable animation are already architectural rules.
- `HandGestureSource.cs`: real hand detection is guarded by `UNITY_XR_HANDS`; editor fallback is `DebugFireBranchGesture()`.
- `PerchOnHand.cs`: implemented state machine is `IDLE -> FLYING_TO_HAND -> PERCHED -> RETURNING -> IDLE`, target is `IndexIntermediate`.
- `ProjectSettings.asset`: Android package id still `com.unity.template.ar_mobile`; camera usage text exists, microphone usage text is empty.
- `Packages/manifest.json`: AR Foundation/ARCore/ARKit/XR Interaction Toolkit exist, but `com.unity.xr.hands` is not installed.
- `Assets/csc.rsp`: defines `UNITY_AR_FOUNDATION` only; real XRHand path needs `UNITY_XR_HANDS`.

## 2. Implemented in this pass

Nanobot paper report UI:

- `PaperNote_DraggableSelectable`: tap/drag selects the paper and shows a white outline.
- Scroll or `+/-` buttons scale paper between `0.78x` and `1.65x`.
- `PaperNoteDropTargets_RightRail`: right-side landscape drop rail with wiggling `TRASH` and `DESK` targets when a note is selected.
- `PaperDropTarget_Trash`: moves the current note to local `_trashDocuments` and updates the HUD trash count.
- `PaperDropTarget_Workdesk`: opens the `AppV1_2DWorkdesk` and leaves the paper in reviewable local documents.
- Paper kinds use runtime tinting: `nanobot_report`, `calendar_draft`, `workdesk_alert`, `system_popup`.

Parrot movement:

- `ParrotJoystick_PlaneWalkPad`: bottom-left App joystick.
- `ParrotController.WalkOnPlane(input, dt)`: local Unity-side walk input, with no Brain command and no Scene switch.
- `AnimationDriver.BodyState.Walk`: simple v1 walk animation using bob, leg alternation, folded wings, and tail sway.
- `ParrotController.ReturnToPlaneWalkHome()`: joystick `home` flies the parrot back to the remembered desktop/plane home.

Asset slots:

- Added explicit runtime slots for `NanobotReportPaper`, `CalendarReminderPaper`, `TrashCrumpledPaper`, `OrangeCatPaw`, and `ParrotJoystick`.
- `OrangeCatPaw` now uses the AI-generated source `D:/GOSLOParrot/Pixel Asset/NekoClaw.png`, imported as transparent Unity sprite `Assets/UI/ParrotApp/Notifications/NekoClaw_Cutout.png`.
- Trash uses layered UGUI paper chips as the temporary crumpled-paper ball.

Smoke-scene prep:

- Added `Tools/Parrot/Upgrade Current A2 Smoke Scene` to non-interactively add `AppV1MetaUI` to an already-saved smoke scene and wire Photo/Focus/BBox/XRHand/Parrot references.
- Ran the upgrader against `Assets/Scenes/ParrotSmokeScene.unity`; the scene now has an `AppV1MetaUI` root.
- Fixed Unity 2022 runtime font creation by switching App UI text from invalid `Arial.ttf` to `LegacyRuntime.ttf`.

## 3. Real-device smoke checklist still needed

Before a phone/Quest run:

1. Build the ArSpike smoke scene from `Tools/Parrot/Build A2 Smoke Scene`.
2. Confirm `Assets/Models/GOSLO.glb` imports with glTFast; the file and meta currently exist.
3. Replace Android package id `com.unity.template.ar_mobile` with a project id before distributable builds.
4. Fill microphone usage description if LiveKit mic publish is enabled.
5. Generate LAN smoke config with `uv run python src/scripts/prepare_app_v1_device_smoke.py --print`.
6. Make sure phone and workstation can reach LiveKit, token mint, photo upload, and Web console by LAN IP, not `localhost`.
7. Run App flow: Startup -> Local Preview/Start AR -> SceneReady -> GOSLO Placed -> tools.
8. Run paper flow: Notes -> select paper -> scale -> drag to trash -> Notes again -> drag to workdesk -> accept/dismiss/archive.
9. Run parrot flow: joystick walk -> release -> home return -> XRHand debug branch.
10. If real XRHand is required, install `com.unity.xr.hands`, add `UNITY_XR_HANDS`, and verify the OpenXR/AR provider actually exposes hand joints on the target device.

Mint startup fix:

- 2026-05-10 audit found the smoke scene could still auto-connect through `RoomManager`'s editor token-file path while `AppV1MetaUI.startupFlow` was empty.
- `ParrotSmokeSceneBuilder.UpgradeCurrentSmokeScene()` now ensures `AppStartupFlowController` + `LiveKitTokenMintClient` exist on `Lifecycle`, wires `AppV1MetaUI.startupFlow`, and sets `RoomManager.autoConnectOnStart=false` / `allowEditorTokenFile=false`.
- Current `ParrotSmokeScene.unity` has `LiveKitTokenMintClient.mintEndpoint=http://127.0.0.1:7888/mint`; for real device testing this must be changed to the phone-reachable LAN/Castle endpoint.

## 4. Current XRHand answer

The code path for "gesture/command flies to the index-finger middle segment, plays perch animation, and flies back" is implemented for editor smoke and ready for real package activation:

- Fly target: `HandGestureSnapshot.IndexIntermediate`.
- Flying animation: `AnimationDriver.BodyState.Fly`.
- Perch animation: `AnimationDriver.BodyState.PerchedOnHand` plus `HeadState.Tilt`.
- Return trigger: hand lost or `closed_fist`.
- Return target: parrot position cached when branch gesture starts, unless `explicitReturnPosition` is set.

What is not yet real-device complete:

- Real hand tracking package/define is missing.
- We still need a device pass to validate hand-joint coordinate transform, arrival distance, and finger-jitter smoothing.
- No backend command is needed for this reflex; that is intentional per architecture.

## 4.1 NekoClaw source audit

- Source: user-provided AI-generated PNG at `D:/GOSLOParrot/Pixel Asset/NekoClaw.png`.
- Original image is `2048x2048` and opaque (`alphaMin=255`, `alphaMax=255`), so it was not suitable for AR floating UI as-is.
- Generated Unity cutout: `Assets/UI/ParrotApp/Notifications/NekoClaw_Cutout.png`, `1052x1846`, transparent background (`alphaMin=0`, `alphaMax=255`).
- App use: `AppV1MetaUiController.nekoClawSprite` renders `NekoClawReportPaw` behind the nanobot paper stack as a delivery prop only. It does not own note data, write Blackboard, or bypass IntentWorkspace.

## 4.2 Ner custom model audit

- Existing state: `Assets/Scenes/ParrotSmokeScene.unity` contains a root `Ner` GameObject with `MeshFilter`, `MeshRenderer`, and Spine `SkeletonAnimation` using `Assets/Models/Ner/NerSkin2_*`.
- Current gap: the `Ner` GameObject has no `ModelDriver`, no `IParrotController`, and no `Resources/parrot_models/Ner.json` manifest. Therefore it can display/play its local SkeletonAnimation, but Brain/Unity command routing cannot yet target it through `model_id="Ner"`.
- Do not blindly attach `ModelDriver` to `Ner` in the current smoke scene: `ParrotRegistry` is still a P1 single-active registry, so the last registered model can become the default route for empty `model_id` commands.
- To make Ner a real custom model: add a `NerController : IParrotController` that maps capability ids to Spine animation names, add `Resources/parrot_models/Ner.json`, attach `ModelDriver(modelId=Ner)`, and validate `ParrotRegistry.Resolve("Ner")` with `animate(..., model_id="Ner")`.

## 5. Verification record

- Python static/tests:
  - `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py tests/test_brain/test_app_first_version_facade.py tests/test_brain/test_app_v1_monitor.py -q`
  - `uv run ruff check src/parrot/brain/app_first_version.py src/parrot/brain/app_live_state.py src/scripts/prepare_app_v1_device_smoke.py tests/test_unity/test_app_v1_meta_ui_static.py`
- Unity MCP:
  - Active project: `ArSpike`, Unity `2022.3.62f3`, platform `Android`.
  - Active scene before fix lacked `AppV1MetaUI`; this was fixed by the upgrader.
  - Play Mode smoke found `AppV1MetaCanvas`, `PaperNote_DraggableSelectable`, `PaperDropTarget_Trash`, `PaperDropTarget_Workdesk`, `ParrotJoystick_PlaneWalkPad`, `CameraModeOverlay_TransparentWysiwyg`, and `MagnifierFocusOverlay_Draggable`.
  - 2026-05-10 NekoClaw smoke found `NekoClawReportPaw` and `PaperNote_DraggableSelectable` in Play Mode.
  - Console compile/import errors: 0.
  - Play Mode still reports expected LiveKit connection failure when local/server LiveKit is not reachable; this is an environment prerequisite, not a NekoClaw/UI compile failure.
  - 2026-05-10 Mint startup correction: Unity MCP found `AppStartupFlowController`, `LiveKitTokenMintClient`, and `RoomManager`; scene serialization shows `startupFlow` wired and `autoConnectOnStart=0`, `allowEditorTokenFile=0`.
