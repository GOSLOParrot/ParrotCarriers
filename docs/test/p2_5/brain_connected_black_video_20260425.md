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

7. 2026-04-25 23:31Z phone logs showed a separate audio-track failure.

   Unity/LiveKit emitted `actualRate=24000 expectedRate=48000` followed by `InvalidState — sample_rate and num_channels don't match` and `audio capture failed`. This is not caused by asking about the screen; it means the microphone PCM frames sent into LiveKit did not match the native audio source metadata. On such a device Brain/Gemini may hear clipped, missing, or no user speech, which can look like "GOSLO froze after I asked a visual question".

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
- Fixed the non-Bluetooth Android phone-mic baseline by configuring `RtcAudioSource.DefaultMicrophoneSampleRate` to a fixed 48 kHz before constructing `MicrophoneSource`; HUD/self-test report both configured rate and Unity output rate. Bluetooth input remains a separate app route-policy problem because it can renegotiate to 24 kHz mid-session.

## Retest checklist

- Android HUD should no longer show `AR: UNITY_AR_FOUNDATION off`.
- If ARCore is active, `SceneProfileManager` should choose `AR_HANDHELD`, not `DESKTOP_WEBCAM`.
- `ARVideoPublisher` should log `First AR frame received` and `source=AR`.
- Self-test should show `publishing fresh frames`, not stale.
- If the camera freezes, HUD should show `Video pub: stale(...)` and Brain should receive `onVideoDegraded(reason=static_frame)`.
- When asking GOSLO to switch quality, Brain should not verbally overclaim success before Unity confirms through the RPC/log path.
- Unity Android build should compile past AR scripts. If BuildPlayerWindow reports a GUILayout state error after scripts compile, restart Unity or reset layout and retry before debugging runtime AR.
- With Bluetooth off, phone logs should no longer show repeated `actualRate=48000 expectedRate=16000` or `audio capture failed` after reconnect. HUD/self-test should show the microphone configured rate, e.g. `Audio pub: yes(48k)`.

## Sprint4 implications

- Treat video health as `(track published, fresh frames, visual state, tier ack)`, not a single boolean.
- Keep Gemini default tier low latency; do not use `VIDEO_FULL` as a black-screen recovery button unless frame freshness is already healthy.
- Add an explicit app startup gate: do not announce visual readiness until AR permissions, AR session state, first camera frame, and LiveKit publish are all ready.
- Consider replacing the project-wide `csc.rsp` macro with asmdef `versionDefines` if the Unity scripts are later moved into assemblies.
- Keep a build-stage checklist separate from behavior/runtime tests: Android ARM64, XR Plug-in Management provider enabled, Input Handling policy, and Unity editor layout health can block tests before app logic runs.
- Treat "visual question caused blocking" as two possible overlapping paths during triage: Gemini multimodal generation can timeout, but if phone audio capture is failing at the same time, the agent may simply not receive clean speech.

## 2026-04-26 voice stutter follow-up

Later log5 testing showed connectivity and AR were mostly present: `AR: SessionTracking`, fresh video frames, mic 48 kHz OK, Unity→Brain RPC RTT around 129 ms, and Graphiti conversation archive writing to DB. The remaining bad UX was voice continuity.

Findings:

- The transcript shows many assistant/user fragments interleaving like echo or barge-in, not just slow network.
- Brain sent two startup greetings in the same session: the immediate `session.generate_reply()` and the Unity `onSceneReady` greeting. This can confuse Gemini Live turn detection and make the first user turn feel crowded.
- Unity created remote `AudioStream` as a local variable in `RoomManager.OnTrackSubscribed`. Because `AudioStream` owns native callbacks and has a finalizer, not keeping a strong reference can allow GC to dispose remote playback while the track is still active.
- Graphiti `add_episode` writes succeeded but took 20-46 s in this test window. Treat live Graphiti archiving as a Sprint4 background/idle pipeline concern, not as proof that the realtime voice loop is healthy.
- `mode_watcher` / `context_injector` attempted `AgentSession.update_instructions`, which is absent in the current LiveKit Agents API. This produced noisy errors during mode/scene changes and should not be used as the realtime instruction switch path until the API contract is reworked.
- `identify_object` was not the cause of the first two rounds of stutter, but in the third round it was invoked around the white-mouse exchange and saved two near-duplicate objects. Since the tool still lacks screenshot evidence and same-turn THINKING semantics, it should not be enabled during final audio/connectivity smoke tests.

Fixes applied:

- `RoomManager` now holds remote `AudioStream` instances in a dictionary and disposes them explicitly on room replacement/disconnect/destroy.
- Brain startup greeting is now single-path: Unity `onSceneReady` wins; a 3 s fallback greeting runs only if `onSceneReady` never arrives.
- Programmatic Brain `generate_reply` calls now wait for `session.current_speech` before sending another explicit reply.
- `update_instructions` calls in mode/context paths now degrade to warning instead of throwing when the current AgentSession does not support that API.
- `identify_object` is now opt-in via `PARROT_ENABLE_IDENTIFY_OBJECT_TOOL=1`; default Brain sessions keep it out of `ALL_TOOLS` until the Sprint4 visual-evidence upgrade lands.

## 2026-04-26 final audio observation

The final smoke test was good enough to mark Sprint3 connectivity successful: GOSLO greeted smoothly, continued several turns, and could answer what it saw. The remaining transcript corruption is best explained by speaker echo, not by AR/LiveKit room failure.

Observed pattern:

- Lines spoken by GOSLO were later transcribed as `[Gemini·用户]`.
- The model then treated its own speaker output as a user interruption, producing repeated fragments and barge-in-like turn breaks.
- This is expected behavior for continuous-audio voice agents when acoustic echo cancellation is insufficient: Gemini Live VAD detects activity, but it does not reliably know that the activity is its own prior output.

Implication:

- Sprint3 is complete as a connectivity smoke.
- Sprint4 pre-entry must design audio routing: headset/Bluetooth baseline, speakerphone risk, output device selection, push-to-talk or manual VAD, LiveKit noise/echo cancellation, and possibly a custom ASR/turn-detection path if Gemini Live native audio is not enough.
