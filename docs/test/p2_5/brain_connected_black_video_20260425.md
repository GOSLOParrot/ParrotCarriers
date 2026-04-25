# Brain connected but Gemini saw black video — 2026-04-25

## Context

P2.5 ECS test showed the Brain agent joined `parrot-main` and voice/RPC paths worked, but the conversation was not smooth and Gemini/GOSLO reported a black screen. Unity HUD said video was on, and Brain attempted `set_video_tier -> VIDEO_FULL`, but the screen did not recover.

## High-signal observations

- LiveKit room and Brain dispatch were healthy: Unity joined, JT_ROOM dispatch succeeded, and `agent-AJ_KLrJbhZ74QfK` joined.
- Unity published a video track, but the producer only logged `frames=1` at publish time.
- Later self-tests showed `lastAge≈29.81s` and then `lastAge≈83.43s`.
- HUD displayed `Video pub: yes`, but that only meant a LiveKit local video track existed. It did not prove new camera pixels were flowing.
- Unity reported `Active profile: DESKTOP_WEBCAM` and `AR: UNITY_AR_FOUNDATION=off` on a real Android test.
- Brain logs showed Gemini saying black screen, then tool calls trying `VIDEO_FULL`.
- A later `setVideoTier` push timed out, so the Brain-side tier state and phone-side track state could diverge.
- Brain also logged `libwebrtc video_stream queue overflow`, consistent with video consumer pressure or repeated track/tier churn during an already unhealthy visual path.

## Root causes found in code

1. `UNITY_AR_FOUNDATION` was treated as if Unity/AR Foundation defined it automatically.

   The project installs `com.unity.xr.arfoundation` 5.1.5, but there was no asmdef `versionDefines`, no `csc.rsp`, and no PlayerSettings scripting define. As a result, Android builds compiled out `ARCameraManager` / `ARCameraBackground` code and fell back to `DESKTOP_WEBCAM`.

2. The test HUD conflated track publication with frame health.

   `ARVideoPublisher.IsPublishing == true` only means `PublishTrack` succeeded. It does not mean the shared `RenderTexture` is receiving fresh AR/WebCam frames.

3. `VideoTierReceiver` defaulted to `Unknown`.

   This made the HUD look like tier routing was missing even though the Brain default is `VIDEO_GEMINI_ONLY`.

4. The Gemini tool response was too optimistic.

   `set_video_tier` commits the Supervisor/Blackboard state synchronously, while the Unity `setVideoTier` RPC is pushed asynchronously. Saying "已切换" before the phone acknowledges is misleading when the RPC later times out.

5. Enabling AR code surfaced compile-time drift hidden by the old `UNITY_AR_FOUNDATION off` state.

   Once `csc.rsp` defined `UNITY_AR_FOUNDATION`, Android Player builds started compiling AR-specific code paths that had not been exercised recently:
   - `ARPlane.extents` is a `Vector2` in AR Foundation 5.1, so area calculation must use `x * y`, not `x * z`.
   - Runtime self-test code that references `ARSession` on Android must import `UnityEngine.XR.ARFoundation` whenever `UNITY_AR_FOUNDATION` is defined, not only in the Editor.
   - Fields only used inside `UNITY_XR_HANDS` blocks should also be declared inside that block, otherwise non-XR-Hands builds emit unused-field warnings.

6. Unity build output included project/editor warnings that are not the black-video root cause.

   These should be handled, but they are separate from the AR camera frame path:
   - Missing ARM64 for Android 64-bit devices is a Player Settings issue and must be fixed before release testing.
   - Active Input Handling set to `Both` can hurt Android input/perf; choose one path when the app input policy is finalized.
   - `GUI Error: Invalid GUILayout state in BuildPlayerWindow` is usually an Editor window/layout state issue during build UI repaint, not an AR pipeline code error. If scripts compile, reset the Unity layout or restart Unity before treating it as runtime failure.

## Fixes applied

- Added `unity/ParrotDev/Assets/csc.rsp` with `-define:UNITY_AR_FOUNDATION` so AR Foundation code is compiled into the Unity project.
- Added producer-side freshness fields to `ARVideoPublisher`: `HasFreshFrame` and `StaleFrameThresholdSeconds`.
- Updated self-test output so a published but stale track becomes a WARN, not OK.
- Updated HUD to show `Video pub: stale(... age=Xs)` when the LiveKit track exists but frames are old.
- Updated `VideoStateReporter` to report `static_frame` to Brain when producer frames go stale, and `ok` when fresh frames resume.
- Changed `VideoTierReceiver` initial tier to `GeminiOnly`.
- Upgraded `set_video_tier` into a synchronous GOSLO Intent behavior: the tool now waits for Unity `setVideoTier` applied/rejected before writing the active tier and returning a same-turn result.
- Updated AR Foundation rule docs to record that `UNITY_AR_FOUNDATION` is project-defined, not Unity-defined.
- Fixed AR Foundation compile drift after enabling the macro: `ARPlane.extents` Vector2 area math, Android `ARSession` import, and an XR Hands conditional-field warning.

## Retest checklist

- Android HUD should no longer show `AR: UNITY_AR_FOUNDATION off`.
- If ARCore is active, `SceneProfileManager` should choose `AR_HANDHELD`, not `DESKTOP_WEBCAM`.
- `ARVideoPublisher` should log `First AR frame received` and `source=AR`.
- Self-test should show `publishing fresh frames`, not stale.
- If the camera freezes, HUD should show `Video pub: stale(...)` and Brain should receive `onVideoDegraded(reason=static_frame)`.
- When asking GOSLO to switch quality, Brain should not verbally overclaim success before Unity confirms through the RPC/log path.
- Unity Android build should compile past AR scripts. If BuildPlayerWindow reports a GUILayout state error after scripts compile, restart Unity or reset layout and retry before debugging runtime AR.

## Sprint4 implications

- Treat video health as `(track published, fresh frames, visual state, tier ack)`, not a single boolean.
- Keep Gemini default tier low latency; do not use `VIDEO_FULL` as a black-screen recovery button unless frame freshness is already healthy.
- Add an explicit app startup gate: do not announce visual readiness until AR permissions, AR session state, first camera frame, and LiveKit publish are all ready.
- Consider replacing the project-wide `csc.rsp` macro with asmdef `versionDefines` if the Unity scripts are later moved into assemblies.
- Keep a build-stage checklist separate from behavior/runtime tests: Android ARM64, XR Plug-in Management provider enabled, Input Handling policy, and Unity editor layout health can block tests before app logic runs.
