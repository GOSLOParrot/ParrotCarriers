# Ner Unity Tuning Isolation Audit Report

> Date: 2026-05-11
> Scope: Ner mouse tuning scene isolation, real controller pollution check, and next-step tuning risk.

## Verdict

The Ner mouse tuning scene is isolated from the real app entry path after this audit.

- `Assets/NerTuningTest` remains the only location for the mouse tuning scene, prefab, materials, builder, harness, and acceptance probe.
- `EditorBuildSettings.asset` does not include `Assets/NerTuningTest/Scenes/NerMouseTuningScene.unity`; only `Assets/Scenes/SampleScene.unity` is enabled.
- No `NerTuning`, `NerMouseTuningHarness`, `NerTuningAcceptanceProbe`, or `NerMouseTuningScene` references were found outside `Assets/NerTuningTest`.
- The two test MonoBehaviours were wrapped with `#if UNITY_EDITOR`, so they do not enter player/runtime builds.
- No real controller file was changed in this cleanup pass.

## Cleanup Applied

- `unity/ArSpike/Assets/NerTuningTest/Scripts/NerMouseTuningHarness.cs`
  - Added a file-level `#if UNITY_EDITOR` guard.
  - Keeps mouse-only cheek pinch, face-center tap, body click, pickup, wheel/keyboard tuning out of app runtime.

- `unity/ArSpike/Assets/NerTuningTest/Scripts/NerTuningAcceptanceProbe.cs`
  - Added a file-level `#if UNITY_EDITOR` guard.
  - Keeps tuning-only acceptance probes out of app runtime.

No production `ParrotApp/Parrot` controller or interactor code was deleted, because the audit did not find test-scene-only names or harness references inside those files.

## Verification

- Searched `Assets` and `ProjectSettings` outside `Assets/NerTuningTest`; no tuning scene or harness references were found.
- Ran Unity script refresh/compile request; Editor console returned `0` errors and `0` warnings.
- Ran Python regression:
  - `.\.venv\Scripts\python.exe -m pytest tests\test_unity\test_app_v1_meta_ui_static.py tests\test_brain\test_menu_workspace.py tests\test_brain\test_tools_model_id.py tests\test_shared\test_model_manifest.py -q`
  - Result: `59 passed`.

## External Interaction Reference

Public materials for `トリッカル・もちもちほっペ大作戦` consistently describe a mobile `iOS/Android` touch-therapy card RPG where cheek pulling is a core direct-touch interaction across many scenes:

- Gamer: https://www.gamer.ne.jp/news/202508140023/
- Niconico/PR Times program note: https://prtimes.jp/a/?c=96446&f=d96446-905-1e9bf620d7db2f9ba84bfee623758471.pdf&r=905
- GameWith: https://gamewith.jp/trickcal
- AppMedia: https://appmedia.jp/preceding-play/79364207

These sources confirm the interaction direction, but do not publish implementation-level thresholds, animation timings, or spring curves. Those values still need local tuning.

## Mouse vs Phone Risk

The test scene is good for fast iteration, but it is not a full mobile/AR acceptance substitute.

- Mouse is a precise single pointer with hover/wheel affordances.
- Phone touch has finger occlusion, larger contact area, jitter, cancellation, and multi-touch.
- Android accessibility guidance recommends touch targets of at least `48dp x 48dp`, around `9mm`.
- Unity Input System touch support exposes `primaryTouch`, `touches`, `touchId`, and `EnhancedTouch`; production touch work should track touch identity rather than assume mouse-like input.

References:

- MDN Pointer Events: https://developer.mozilla.org/en-US/docs/Web/API/Pointer_events
- MDN Multi-touch: https://developer.mozilla.org/en-US/docs/Web/API/Touch_events/Multi-touch_interaction
- Android touch target guidance: https://support.google.com/accessibility/android/answer/7101858?hl=en
- Unity Input System Touch: https://docs.unity.cn/Packages/com.unity.inputsystem%401.0/manual/Touch.html

## Current Real-App Risks

- `NerCheekPinchInteractor.cs` and `NerPickupPlaceInteractor.cs` still use legacy `UnityEngine.Input` APIs. That is a real app/mobile risk when the project is configured for the new Input System.
- This audit intentionally did not rewrite those production interactors, because the request was to prevent test-scene tuning from affecting the real controller.
- The next production pass should migrate those interactors to Input System or `EnhancedTouch`, then verify on device.

## Tuning Acceptance Checklist

Use the isolated scene for feel tuning only:

- Model loads with full visible skin, not partial attachments.
- Left cheek region triggers cheek pinch; right cheek remains disabled for the current test target.
- Cheek drag has a smaller deformation limit and a springy release.
- Face-center single tap triggers the pat reaction; long press there does not become pickup.
- Body tap triggers the body reaction.
- Body long press enters pickup and keeps one continuous held loop.
- Dragging pickup does not restart held animation.
- Pointer vertical movement changes lift height in the test scene.
- WASD movement is test-only translation unless real walk animation assets are added.

## Status

- Completed: test scene folder isolation audit.
- Completed: Build Settings exclusion check.
- Completed: test script player-build exclusion via `UNITY_EDITOR`.
- Partial: mobile/AR input parity; production interactors still need a separate Input System pass.
- Not verified in this report: real device AR touch behavior, ASR/TTS/LineB echo suppression, and final production prefab entry path.
