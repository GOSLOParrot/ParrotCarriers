# Unity Audio / LiveKit Deep Audit - 2026-05-17

Scope: formal Unity App on iQOO Neo9, LiveKit Unity microphone uplink,
Bluetooth/SCO/A2DP routing, app background/resume, and the question "why can
the user hear the agent but the agent cannot reliably hear the phone".

This is a decision audit, not a new protocol proposal. It re-reads current
skills, local SSOT/TODO, formal App code, and primary external sources.

## Sources Re-read

Local skills:

- `codex_workspace/skills/unity_ar_app.md`
- `.cursor/skills/livekit-unity-lifecycle/SKILL.md`
- `.cursor/skills/client-sdk-unity/SKILL.md`
- `.cursor/skills/livekit-unity-video-publish/IMPL_REF.md`

Local SSOT / implementation docs:

- `backend_interface_map/app/unity_audio_route_research_20260516.md`
- `backend_interface_map/app/unity_project_inventory_app_ssot_20260513.md`
- `backend_interface_map/app/formal_homepage_hud_menu_plan_20260515.md`
- `tasks/ACTIVE_CONTEXT.md`
- `tasks/APP_WEB_PARALLEL_TODOLIST_20260513.md`

Formal App code audited:

- `Assets/ParrotApp/Runtime/Scripts/LiveKit/MicrophonePublisher.cs`
- `Assets/ParrotApp/Runtime/Scripts/LiveKit/AudioRouteManager.cs`
- `Assets/ParrotApp/Runtime/Scripts/LiveKit/AndroidAudioRouteManager.cs`
- `Assets/Plugins/Android/ParrotAudioRoute.androidlib/**`
- `Assets/ParrotApp/Runtime/Scripts/UI/FormalHomeHudController.cs`
- LiveKit package source:
  `Library/PackageCache/io.livekit.livekit-sdk@7d868ef5cc/Runtime/Scripts/MicrophoneSource.cs`
  and `RtcAudioSource.cs`

Primary external references:

- Android `AudioManager`: `getAvailableCommunicationDevices()` returns devices
  selectable by `setCommunicationDevice(...)`; `getCommunicationDevice()`
  replaces old `isBluetoothScoOn()` / `isSpeakerphoneOn()` for communication
  routing.
  Source: https://developer.android.com/reference/android/media/AudioManager
- Android `AudioDeviceInfo`: `TYPE_BLUETOOTH_A2DP` is A2DP profile, while
  `TYPE_BLUETOOTH_SCO` is the telephony-style Bluetooth communication path;
  `TYPE_BUILTIN_MIC` is the built-in microphone.
  Source: https://developer.android.com/reference/android/media/AudioDeviceInfo
- Android Bluetooth permissions: Android 12+ requires `BLUETOOTH_CONNECT` when
  an app communicates with already-paired Bluetooth devices.
  Source: https://developer.android.com/develop/connectivity/bluetooth/bt-permissions
- Unity Android permissions: `Microphone` use adds/requests `RECORD_AUDIO`,
  but the manifest must declare a permission for the dialog to appear.
  Source: https://docs.unity.cn/2022.1/Documentation/Manual/android-permissions-in-unity.html
- Unity Issue Tracker UUM-48126: `AudioSettings.OnAudioConfigurationChanged`
  is output-side and may not fire for Bluetooth connection if sample rate /
  channel count do not change; input-side recovery should check
  `Microphone.IsRecording`.
  Source: https://issuetracker.unity3d.com/issues/android-ios-audiosettings-dot-onaudioconfigurationchanged-is-not-called-when-connecting-bluetooth-headset
- Unity Issue Tracker UUM-3727: Bluetooth microphone input remains unreliable
  on a small percentage of Android devices; Unity recommends falling back to
  built-in mic if Bluetooth mic issues persist.
  Source: https://issuetracker.unity3d.com/issues/android-the-microphone-recording-is-faulty-when-the-bluetooth-headset-is-connected-to-the-phone-before-opening-the-application
- Unity Issue Tracker UUM-45665: older 2022.3 builds could crash when a
  Bluetooth recording device disconnects while recording. Our editor is newer
  than the fixed version, but this reinforces that unplug/disconnect must be
  treated as a first-class phone test.
  Source: https://issuetracker.unity3d.com/issues/android-crash-when-recording-audio-with-a-connected-bluetooth-audio-device-that-is-later-disconnected-on-android
- LiveKit Android `AudioSwitchHandler`: Android SDK owns audio focus and output
  route management, can prefer device lists, and notes some Android devices need
  `MODE_IN_COMMUNICATION` / `MODE_IN_CALL` for Bluetooth microphones.
  Source: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.audio/-audio-switch-handler/index.html
- LiveKit Unity `MicrophoneSource`: `AudioRead` fires when samples are captured
  from the underlying source and carries data, channel count, and sample rate;
  it is not guaranteed to run on the main thread.
  Source: https://livekit.github.io/client-sdk-unity/api/LiveKit.MicrophoneSource.html
- Android 16 KB page-size guidance: Google Play requires 16 KB page-size support
  for Android 15+ 64-bit devices; `arm64-v8a` / `x86_64` libraries should be
  checked with ELF LOAD alignment and APK zip alignment.
  Source: https://developer.android.com/guide/practices/page-sizes

## Decision Audit

### Decision 1 - Native Android route owner + Unity mic executor remains correct

Verdict: keep.

Reasoning:

- Android's communication routing APIs are the correct primary surface for API
  31+ devices.
- LiveKit Android has a dedicated audio switch layer, which supports our design
  choice that route management is not just `Microphone.devices`.
- The formal App's current split is correct:
  - Android bridge: communication device, audio focus, Bluetooth permission.
  - `AudioRouteManager`: accepted snapshot and policy debounce.
  - `MicrophonePublisher`: LiveKit local microphone track executor.
  - `AudioRoutePolicyBrainReporter`: compact observer for LineB echo policy.
  - Brain/ECP must not switch Unity devices or reconnect the room.

### Decision 2 - A2DP is output-only; SCO is the Bluetooth mic path

Verdict: keep.

Reasoning:

- Android exposes A2DP and SCO as separate device types.
- The formal App's current rule is correct:
  - A2DP may be selected as output, but does not force Bluetooth mic capture.
  - Only a real SCO/BLE communication-input route should switch the input policy
    to a Bluetooth microphone profile.
  - If Bluetooth is enabled but no usable communication input is connected,
    phone/default mic remains the fallback.

### Decision 3 - Route changes rebuild the local mic track only

Verdict: keep.

Reasoning:

- The LiveKit lifecycle skill explicitly says headset changes must not reconnect
  the room.
- Reconnecting the room would churn token, identity, Brain job dispatch, and
  session memory for a local hardware event.
- `MicrophoneSource` locks native source parameters at construction; serial
  unpublish/rebuild/publish is safer than in-place reconfiguration.

### Decision 4 - Startup anti-fake-success guard is now materially better

Verdict: partially complete.

What is complete:

- `PublishTrack` success is not treated as speech uplink proof.
- Startup now waits for:
  - Unity `Microphone.GetPosition(...) > 0`
  - LiveKit Unity `MicrophoneSource.AudioRead` frame count advancing
- `audio_read_timeout` distinguishes "Unity microphone position advanced but
  no LiveKit SDK audio frame arrived".
- HUD exposes `frames`, `ch`, `readSr`, and `peak`.

Remaining limitation:

- `AudioRead` proves samples reached the LiveKit Unity source, not that native
  FFI `CaptureAudioFrame` succeeded or that Brain/STT consumed the remote track.
- The local SDK logs FFI capture callback failures, but the formal HUD does not
  currently surface those native callback results.

### Decision 5 - Do not reuse old ParrotDev/Smoke audio rules

Verdict: keep.

Reasoning:

- ParrotDev/Smoke proved LineA connectivity and a simple microphone publish
  path, but it did not define formal phone audio policy.
- The old path had no Bluetooth/SCO/A2DP split, no native route manager, no
  room/session preservation contract, no steady route republish discipline, and
  no proof against fake audio publish.
- Existing formal code is more aligned with Android and LiveKit lifecycle
  constraints, even though it still needs phone proof.

## Current Completion Status

Code-complete enough for next phone pass:

- Runtime permissions:
  - `RECORD_AUDIO`
  - `MODIFY_AUDIO_SETTINGS`
  - legacy Bluetooth permissions
  - `BLUETOOTH_CONNECT`
- Android native route bridge:
  - enters communication mode only when publishing is intended
  - requests audio focus for voice/communication
  - chooses SCO only when available
  - falls back to phone/default route when Bluetooth is enabled but not
    connected as a communication device
  - exposes snapshots to Unity
- Unity route wrapper:
  - accepts native snapshots
  - falls back to Unity detector for diagnostics
  - emits route-policy changes
- LiveKit mic executor:
  - serializes publish/unpublish/rebuild
  - does not reconnect the LiveKit room for route changes
  - supports Android default mic fallback when Unity lists zero microphones
  - now guards startup success with `MicrophoneSource.AudioRead`
  - after a failed Bluetooth SCO capture, retries SCO at 48 kHz and then falls
    back to `phone_default_microphone` at 48 kHz before declaring the uplink
    failed
- HUD:
  - separates route/device (`UsingMic`) from capture/uplink (`Uplink`)
  - shows frame count, channel count, sample rate, and peak
- 16 KB alignment helper:
  - `tools/verify_so_alignment.ps1` now runs under Windows PowerShell 5
  - current package arm64 `liblivekit_ffi.so` verifies `OK_16KB`

Not complete:

- No iQOO Neo9 proof for LineA/LineB speech uplink after the latest
  `AudioRead` guard.
- No iQOO proof for Bluetooth already connected before START.
- No iQOO proof for Bluetooth connect-after-start.
- No iQOO proof for Bluetooth disconnect fallback during a LiveKit session.
- No iQOO proof for other-media coexistence.
- No iQOO proof for long background/session hold.
- No network-flap reconnect proof.
- No production Settings audio-route UX; `MIC NEXT` / `MIC AUTO` remain
  diagnostics.
- Steady-state microphone watchdog is now code-complete after this audit, but
  its recovery behavior is not phone-proven.
- No HUD signal for LiveKit FFI `CaptureAudioFrame` callback failure.

## Findings

### P1 - Steady-state microphone watchdog

Risk:

The startup guard proves initial capture, but if Android/Unity stops recording
after publish because of Bluetooth disconnect, route reset, app pause/resume, or
audio output reset, `_isPublishing` could remain true until a route callback or
room event triggers a rebuild.

Evidence before the follow-up patch:

- Unity's own resolution note says Bluetooth/input changes should be checked
  with `Microphone.IsRecording`.
- `MicrophonePublisher` already used `Microphone.GetPosition(...)` and
  `AudioReadFrameCount` during startup, but did not continuously check
  `Microphone.IsRecording(device)` or stale `AudioReadFrameCount` after
  `_isPublishing=true`.

Implemented follow-up:

- Added a formal `UplinkRuntimeWatchdog` inside `MicrophonePublisher`:
  - while publishing and publish intent is enabled:
    - check `Microphone.IsRecording(probeDevice)` when available
    - track last `AudioReadFrameCount` time
    - mark degraded if frames stop for a bounded interval
    - queue serial republish, not room reconnect
    - never mint a new token or dispatch a new Brain job for a mic-route glitch
  - publish HUD fields:
    - watchdog state
    - last frame age
    - recording state
    - last recovery reason
  - keep it separate from `AudioRouteDetector`; this is media executor health,
    not route ownership.

Remaining proof:

- iQOO must still prove that Bluetooth disconnect, route reset, pause/resume, or
  Unity input loss actually triggers this watchdog and recovers through a local
  mic-track republish without reconnecting the LiveKit room.

### P1 - Phone proof is still the truth gate

Risk:

The formal App has improved diagnostics, but the route stack cannot be marked
stable until iQOO logs prove the actual device behavior.

Required phone matrix:

1. No Bluetooth: START -> LineA voice -> `frames` rises -> `peak` responds.
2. Bluetooth disabled/no connected device: App must use phone/default mic and
   not get stuck.
3. Bluetooth connected before START: selected route should be SCO only if a
   real communication input exists; otherwise output may be Bluetooth while
   input remains phone/default.
4. Bluetooth connects after START: route snapshot updates, mic rebuilds
   serially, room and Brain job stay alive.
5. Bluetooth disconnects during speech: watchdog/route event detects it,
   republish fallback uses phone/default mic.
6. Background/resume: room/session held, mic rebuilt only if capture stopped.
7. LineB: route policy reaches Brain; echo policy adapts; voiceprint disabled
   remains non-blocking.

### P2 - LiveKit FFI capture callback is not surfaced to HUD

Risk:

If `AudioRead` increments but native `CaptureAudioFrame` returns callback
errors, HUD will still show frames and could mislead us toward Brain/STT.

Current status:

- Local SDK logs `capture callback failed` internally.
- No public App-level event is exposed without patching/wrapping the SDK.

Recommendation:

- First phone run should capture Unity/Android logs and search for
  `RtcAudioSource` warnings/errors.
- If `frames` rises but Brain still cannot hear speech, add a focused SDK-level
  diagnostic patch or wrapper before changing backend.

### P2 - 16 KB warning needs APK-level verification, not package-level panic

Observation:

- `tools/verify_so_alignment.ps1` initially had a PowerShell syntax/count bug;
  fixed in this audit.
- Package-level arm64 `liblivekit_ffi.so` verifies `OK_16KB`.
- Scanning all plugin folders also finds non-Android/Linux and ARMv7 4 KB
  alignments. The Android 15 Google Play requirement is specifically about
  64-bit Android APK/AAB libraries, so final proof must be run on the built APK.

Required follow-up:

- After the next APK build, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\verify_so_alignment.ps1 <apk> -NdkRoot D:\Unity\Editor\2022.3.62f3\Editor\Data\PlaybackEngines\AndroidPlayer\NDK
```

If the APK still warns for `arm64-v8a/liblivekit_ffi.so`, then inspect APK
packaging/zip alignment. If only ARMv7/Linux package folders are bad, do not
block iQOO testing on that.

### P2 - Unity 2022.3.62f3 is newer than known Bluetooth crash fixes, but not a guarantee

Observation:

- UUM-45665 is fixed in 2022.3.13f1; current Unity is 2022.3.62f3.
- UUM-3727 says Bluetooth mic is still unreliable on a small percentage of
  Android devices even after fixes.

Conclusion:

- Staying on Unity 2022.3.62f3 is reasonable for now.
- The fallback-to-phone-mic design is not a compromise; it is aligned with
  Unity's own recommendation for unreliable Bluetooth mic cases.

## Objective Completion Summary

Green:

- Version locks are coherent: Unity 2022.3.62f3, AR Foundation/ARCore/ARKit
  5.2.2, LiveKit Unity pinned to `7d868ef5cc...`.
- Formal scene and directory SSOT exist; old duplicate script roots are
  classified/cleaned.
- RoomSetting/Menu durable data is App HTTP, not RPC.
- LiveKit RPC is no longer abused for RoomSetting snapshots or inline images.
- Formal audio routing architecture is directionally correct.
- Startup fake-audio-success guard is now much stronger.
- AR Mobile demo2 XRI bridge is in the formal path and not a Smoke scene copy.

Yellow:

- Audio uplink is diagnosable but not stable-proven.
- Parrot scale/plane visual fixes need rebuilt phone proof.
- 16 KB package arm64 is OK, but final APK verification is still required.
- XRHands package/define is present in code terms, but phone hand/perch proof is
  pending.

Red:

- No runtime microphone watchdog after initial successful publish.
- No phone evidence for LineB speech under real iQOO mic/Bluetooth.
- No phone evidence for Bluetooth disconnect/reconnect plus app background.

## Recommended Next Implementation Order

1. Rebuild formal Android App so the new `MicrophonePublisher` watchdog and HUD
   fields are on-device.
2. Build APK, run APK-level 16 KB alignment verification.
3. Phone pass on iQOO with LineA:
   - no Bluetooth
   - Bluetooth on but no connected device
   - Bluetooth connected before START
   - connect/disconnect after START
   - background/resume
4. If `frames/peak` are healthy but Brain cannot hear:
   - inspect `RtcAudioSource` FFI logs
   - inspect Brain/agent audio subscription and LineA/LineB server-side receive
5. Only after LineA phone uplink is understood, run LineB speech and echo-policy
   validation.
6. Continue AR placement/Parrot polish after the audio watchdog is in place, so
   the next phone pass can test voice and interaction together.

## Validation After This Audit

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- `powershell -NoProfile -ExecutionPolicy Bypass -File tools\verify_so_alignment.ps1 unity\ArSpike\Library\PackageCache\io.livekit.livekit-sdk@7d868ef5cc\Runtime\Plugins\ffi-android-arm64 -NdkRoot D:\Unity\Editor\2022.3.62f3\Editor\Data\PlaybackEngines\AndroidPlayer\NDK`
  -> arm64 `liblivekit_ffi.so` `OK_16KB`.
- Implementation pass after this audit added `UplinkRuntimeWatchdogLoop`,
  `Microphone.IsRecording` probing, stale `AudioRead` age detection, local mic
  republish recovery, and HUD watchdog fields. Static guard remains
  `28 passed`; phone proof is still pending.
- Follow-up iQOO screenshot showed the narrower failure:
  native route was `bt-sco`, but Unity/LiveKit capture never started
  (`microphone_start_timeout`, `frames=0`, `readSr=0`). This is a local
  capture startup failure, not Brain RPC/STT failure. The formal fix retries
  the same local source as `bluetooth_sco_capture_48k`
  (`sco_capture_48k_retry`) after the normal SCO 16 kHz attempt, without
  reconnecting the LiveKit room, minting a token, or dispatching a new Brain
  job. HUD exposes `fb=` to show whether the retry became active.

## 2026-05-17 Audio Uplink Fix Record

Scope:

- Formal Unity App only: `unity/ArSpike/Assets/ParrotApp/**` plus the formal
  Android route plugin under `unity/ArSpike/Assets/Plugins/Android/**`.
- This is not a Smoke/ParrotDev connectivity-script path and must not be used
  to justify moving old test audio assumptions into the product App.

Completed fixes:

1. Android no-headset voice fallback now prefers `phone_mic + speaker`.
   The previous route choice could prefer `TYPE_BUILTIN_EARPIECE`, which is
   wrong for AR companion hands-free use and made HUD/output interpretation
   confusing.
2. Native `AndroidPcmMicCapture` now stays strict to one requested sample rate
   per Java instance and tries `VOICE_COMMUNICATION`, then raw `MIC`. Broader
   rate fallback is handled in Unity by creating separate LiveKit sources for
   48 kHz, 44.1 kHz, and 16 kHz attempts. This is required because LiveKit FFI
   rejects PCM frames whose sample rate differs from the audio source
   construction rate.
3. Unity `AndroidPcmMicrophoneSource` now asks Java for `lastError()` when
   native `start()` returns false.
4. `AndroidPcmMicrophoneSource.Start()` now rolls back `RtcAudioSource.Start()`
   if native startup fails, preventing a half-subscribed LiveKit source from
   sticking across retries.
5. `MicrophonePublisher` now preserves the last native AudioRecord state/error
   after failed startup, so HUD `native=` / `nerr=` survives cleanup and can
   drive the next diagnosis.
6. The empty-device gate now tolerates stale/unknown native input-route
   snapshots after microphone permission is granted, instead of failing early
   with `no_microphone_devices`.

Major findings:

- The current user-facing symptom is an uplink capture failure. Downlink works:
  the user can hear Parrot/GOSLO. That does not prove microphone capture,
  LiveKit local audio publication, Brain audio receive, or STT receive.
- `LK on` / `Brain on` / audible agent speech is not a valid success marker for
  voice. The minimum phone success marker is HUD `Uplink` showing non-zero
  `frames`, `ch`, `readSr`, and speech-responsive `peak`.
- Valid Android route/permission/focus labels are not enough. iQOO evidence
  showed route/focus could look valid while Unity/LiveKit capture stayed at
  `frames=0`.
- The failure appears with both Bluetooth-on and Bluetooth-off runs, so it is
  not only a Bluetooth/SCO problem. Phone mic fallback and native AudioRecord
  fallback must both be proven.
- If the next build still shows `microphone_start_exception`, use HUD
  `native=` / `nerr=` as the next root-cause input. Do not guess from route
  labels or from the fact that remote audio is audible.

Open gate:

- Rebuild and run on iQOO Neo9. Only mark APP-015.23/APP-024 improved after
  HUD shows non-zero local capture frames. Only after that should LineA/LineB
  Brain hearing/STT be investigated.

## 2026-05-17 Wider LiveKit/Unity Audio Audit

Additional finding:

- The local LiveKit SDK creates a native audio source with a fixed sample rate
  when `RtcAudioSource` is constructed, then rejects `CaptureAudioFrame` payloads
  whose `sample_rate` or `num_channels` differs. Therefore Java-side sample-rate
  fallback is unsafe: it can make Android AudioRecord start at 44.1 kHz or 16 kHz
  while the LiveKit source still expects 48 kHz. The formal App now retries by
  constructing a fresh `AndroidPcmMicrophoneSource` for each candidate rate
  instead of changing rate inside one Java capture instance.

Additional fix:

- `AndroidPcmMicrophoneSource.Start()` now checks its own `_started` guard before
  calling `base.Start()`, and calls `base.Stop()` when native startup fails. This
  keeps the LiveKit `AudioRead` subscription balanced even after
  `microphone_start_exception`.

Still open:

- This is a code-level/stability fix, not a phone pass. The next iQOO run still
  has to prove `Uplink` frames, channel count, sample rate, and peak move while
  speaking.

## 2026-05-17 Follow-up Bug Sweep

Additional findings fixed:

- Android native route selection recognized classic `TYPE_BLUETOOTH_SCO` but
  did not recognize `TYPE_BLE_HEADSET`. On modern earbuds this can make the App
  miss the real communication headset route and fall back to phone output/input
  even though Bluetooth is connected. `AndroidAudioRouteManager` now treats
  BLE headset as a Bluetooth voice communication device; `AudioRouteDetector`
  also recognizes BLE headset/speaker/hearing-aid types for fallback
  diagnostics. Classic SCO still recommends 16 kHz; BLE headset keeps the
  normal 48 kHz LiveKit source unless the retry ladder proves otherwise.
- `AndroidPcmMicCapture` previously swallowed `AndroidJavaProxy` callback
  exceptions while sending PCM to Unity. If the JNI callback signature or
  thread bridge failed, the HUD could only show generic no-uplink symptoms.
  It now reports `pcm_callback_failed:*` through the native state channel and
  exits the capture thread, making HUD `native=` / `nerr=` actionable.
- The pinned LiveKit Unity SDK package accepts `UnpublishTrack(local, true)`
  but currently writes `StopOnUnpublish = false` internally. Formal App cleanup
  therefore cannot assume SDK unpublish tears down the C# source. `MicrophonePublisher`
  now detaches `AudioRead`, stops, and disposes each local source on every failed
  attempt, route rebuild, policy unpublish, and shutdown cleanup.

Validation:

- Unity static guard: `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q`
  -> 28 passed.
- Android route plugin Java compile against Unity 2022.3.62f3 android-36 classpath
  -> passed with deprecation notes only.
