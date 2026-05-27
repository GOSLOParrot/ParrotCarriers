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

## 2026-05-17 Output-only Bluetooth Follow-up

Additional risk found:

- The Android route owner was still too aggressive in `auto` mode. If a
  headset exposed only A2DP/BLE speaker/hearing-aid output, and no selectable
  SCO/BLE headset communication device, `chooseCommunicationDevice()` fell
  through to speaker/earpiece. That can explain the phone symptom where Parrot
  is audible from the phone speaker even while Bluetooth is connected.

Fix:

- `AndroidAudioRouteManager` now leaves the communication device unset when
  output-only Bluetooth is present but no bidirectional communication headset is
  selectable. This preserves the Android system output route instead of stealing
  downlink audio back to speaker/earpiece.
- `MicrophonePublisher` capture fallback now keeps automatic phone/default-mic
  and AudioRecord retries on a temporary `system_default` route override. This
  keeps the room/Brain job stable while matching normal phone behavior:
  Bluetooth output when available, phone/default mic as the input fallback.
  Forced `phone_mic` is deferred to a future explicit/manual recovery control
  because it can pin Parrot output back to the phone speaker.

Validation:

- Unity static guard: `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q`
  -> 28 passed.
- Android route plugin Java compile against Unity 2022.3.62f3 android-36 classpath
  -> passed with deprecation notes only.

Phone gate remains open: the next iQOO run must show HUD uplink frames/peak and
must verify whether Bluetooth downlink stays on the headset when the device is
output-only.

## 2026-05-17 Callback-thread Hygiene

Additional defensive cleanup:

- Native AudioRecord frames arrive through an Android Java callback thread, not
  the Unity main thread. LiveKit `RtcAudioSource` is designed to accept audio
  callbacks off the main thread, but the formal App should not add unrelated
  UnityEngine API calls to that hot path.
- `AndroidPcmMicrophoneSource.OnNativePcmFrame()` and
  `MicrophonePublisher.OnMicrophoneAudioRead()` now use pure C# math for length,
  channel, and peak calculations instead of `Mathf.*` calls. This keeps
  `pcm_callback_failed:*` focused on real JNI/LiveKit failures rather than
  avoidable Unity thread-affinity risks.

## 2026-05-17 Route-loop Bug Report Fix

User phone evidence plus a full local audit found a route loop that could make
the formal App look connected while user speech never reached LiveKit.

Confirmed root causes and fixes:

- `AudioRouteDetector.TryDetectAndroidDevices()` no longer treats
  `AudioManager.getDevices(GET_DEVICES_INPUTS)` as the active microphone route.
  That API is an availability list. Active Bluetooth mic policy now requires
  `getCommunicationDevice()` confirmation; otherwise A2DP remains output-only
  and capture stays on phone/default mic.
- `AudioRouteManager` starts from `AudioRoutePolicy.Default()` and accepts the
  native route snapshot as the Android truth source. The fallback detector stays
  diagnostic/fallback only.
- `requires_mic_republish` from Java no longer triggers
  `OnRoutePolicyChanged` when the C# capture policy did not change. Java still
  reports the snapshot to HUD/Brain observers, but the mic executor only rebuilds
  when the input capture class or sample rate changes.
- `ApplyTemporaryNativePreference(...)` no longer restores the user's durable
  Auto/Bluetooth preference on `device_added` or `device_removed`. Temporary
  phone/default-mic fallback is sticky until user preference changes or a new
  session starts, because restoring on headset topology events can immediately
  undo the fallback that made uplink work.
- `MicrophonePublisher` removed the eager `RequestCommunicationMode(true)` from
  `OnRoomConnected()` and policy-enabled entry. The publish coroutine remains
  the owner of microphone permission, communication mode, source creation, and
  local-track publish. Snapshot churn during startup should not unpublish a
  just-created track unless it changes the capture class/sample rate.
- Republish suppression now covers the route settle time plus the microphone
  startup timeout, so a fallback route change cannot queue an immediate rebuild
  while the current capture attempt is still proving frames.
- `AudioRoutePolicyBrainReporter` no longer creates an `AudioRouteManager`.
  The route manager must be owned by formal runtime services / mic publisher,
  not by an observer.
- Output-only Bluetooth now clears an already-pinned speaker/earpiece
  communication device before returning no target. This is important when the
  user starts without Bluetooth, the App selects speaker for communication, and
  then an A2DP headset connects: clearing lets Android keep Bluetooth downlink
  while Unity uses phone/default mic fallback.

Validation:

- Android route plugin Java compile against Unity 2022.3.62f3 android-36
  classpath -> passed with deprecation notes only.
- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- `git diff --check` -> no whitespace errors; CRLF warnings only.

Phone gate remains open: iQOO must still prove non-zero HUD `Uplink`
`frames/ch/readSr/peak` for Bluetooth connected, Bluetooth disabled,
connect-after-start, disconnect fallback, LineA, LineB, and pause/resume.

## 2026-05-17 SCO Probe / Native Bridge Diagnostics Fix

The route-loop report also identified two remaining failure shapes:

- A real Android SCO communication route can be reported before the voice path
  is actually ready. The App now waits a short `capture_route_settle` window
  before probing SCO, but it also caps SCO probe startup to a short timeout.
  If SCO still produces no Unity/LiveKit `AudioRead` frames, the executor falls
  through to the system/default or phone-mic recovery path instead of spending
  repeated full microphone timeouts on a dead headset path.
- If the Android `AudioRecord` bridge is missing from the APK or cannot create
  `com.parrotcarriers.audio.AndroidPcmMicCapture`, the HUD/native error now
  reports `android_pcm_bridge_unavailable:*` instead of a generic
  `InvalidOperationException`. This makes the next phone run actionable: a
  bridge-packaging problem, a native AudioRecord init problem, and a Brain/STT
  hearing problem should not look the same.

Validation:

- Android route plugin Java compile against Unity 2022.3.62f3 android-36
  classpath -> passed with deprecation notes only.
- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.

Phone gate remains open: next iQOO proof must show either increasing HUD
`frames/ch/readSr/peak`, or a specific `native=` / `nerr=` blocker such as
`android_pcm_bridge_unavailable:*` or `pcm_callback_failed:*`.

## 2026-05-17 Greeting-only Uplink Follow-up

Latest iQOO screenshots show the important split clearly: the placement
greeting can be heard, but user speech still does not produce follow-up
conversation. Treat this as a formal uplink bug, not a Mint/Brain/downlink
failure.

Correction applied:

- Native `AndroidPcmMicCapture` now prefers `MediaRecorder.AudioSource.MIC`
  before `VOICE_COMMUNICATION`. The latter can initialize in Android
  communication mode while still gating or silencing near-end capture on some
  phones. Since this bridge is already the last-resort fallback after Unity
  microphone capture failed, plain MIC is the safer default.
- `source_name` is now included in AudioRecord state JSON. HUD/debug can tell
  whether the native fallback is using `mic` or `voice_communication`.
- `AndroidPcmMicrophoneSource` accepts Java PCM callbacks immediately during
  native `start(...)` and rolls back `_started` on startup exception. This closes
  a race where fast Android frames could be discarded before the C# source marked
  itself active.
- Automatic AudioRecord retry route override remains `system_default` for all
  rates. This avoids pinning downlink to the phone speaker through an automatic
  `phone_mic` override; explicit PhoneMic can be added later as a manual recovery
  control after the basic iQOO uplink is proven.

Validation required on phone:

- HUD `Uplink` must show increasing `frames`, non-zero `ch/readSr`, and a
  non-flat `peak`.
- If those are non-zero and Brain still does not respond, the next investigation
  is remote track subscription / Brain STT ingestion rather than Android local
  capture.

## 2026-05-17 Fake-Silence Guard Follow-up

The previous startup guard proved "no frames" is not accepted as success, but
it did not catch "fresh frames with digital-zero PCM". That case can still
sound exactly like the phone report: Parrot can greet through downlink, while
user speech never reaches the model.

Code correction:

- `MicrophonePublisher` now treats a fresh Unity `MicrophoneSource` stream with
  sustained zero peak as fake uplink. The watchdog reports
  `uplink_watchdog_zero_peak_unity_microphone`, degrades audio health, and
  triggers a one-shot rebuild that starts with native Android `AudioRecord`
  instead of repeating the same Unity microphone source.
- The fallback keeps `system_default` route override, preserving the existing
  split: Android may keep Bluetooth/A2DP downlink while native AudioRecord
  captures plain MIC input.
- The formal HUD now shows `nz=` as the age since source start or latest
  non-zero peak. On a good phone run, `frames` should increase and `peak` should
  move above zero when the user speaks. If `frames/peak/nz` look healthy and
  Brain still stays silent, the local Android route layer is no longer the
  primary suspect; move to LiveKit remote-track / AgentSession STT intake.

## 2026-05-17 RoomIO Active Unity Binding Follow-up

The latest phone evidence proved another split: placement `onGosloPlaced`
could trigger an audible greeting, but user speech still did not produce
follow-up conversation. That can happen even when local capture is healthy:
LiveKit Agents `RoomIO` auto-selects the first accepted remote participant when
`participant_identity` is not set. In the long-lived Castle room, an old Unity
client, Web/diagnostic participant, or previous phone session can be present
before the current phone. Brain can still answer RPCs room-wide, so the first
greeting works, while AgentSession audio/video input remains linked to the
wrong participant.

Correction applied:

- Brain now treats the formal App's `onSceneReady` and `onGosloPlaced` RPC
  caller identity as the authoritative current Unity phone.
- On either RPC, Brain calls `session.room_io.set_participant(caller_identity)`
  when the caller identity starts with `unity`.
- This is an AgentSession input rebind only. It does not reconnect the Unity
  room, remint a token, dispatch a new Brain job, change RoomSetting, or modify
  the local Android audio route.

Next phone proof:

- If HUD `frames/ch/readSr/peak/nz` show real uplink and Brain still does not
  answer, check Castle Brain logs for the new `RoomIO input participant rebound`
  line and for `[Gemini·用户]`/LineB transcript events from the current Unity
  identity.
- If no rebound line appears, Unity did not call the placement/session RPC from
  the expected identity.
- If rebound appears but no transcript appears, continue with STT/model intake
  rather than more Android route work.

## 2026-05-17 Unity / Android / LiveKit Compatibility Sweep

External issue sweep:

- Unity official issue UUM-3727 confirms Android Bluetooth microphone input is
  still unreliable on a small percentage of devices even after Bluetooth audio
  fixes, and Unity's own recommendation is to fall back to the built-in mic
  when Bluetooth mic issues persist. This matches the formal App decision that
  Bluetooth SCO is attempted but phone/default MIC remains the reliable
  fallback.
- LiveKit Unity SDK README still marks the Unity SDK as Developer Preview, not
  production-ready. A current Unity SDK issue also reports Android audio-source
  streaming failures on some device families while the native Android SDK works,
  so a Unity-side AudioRecord fallback and phone proof are required.
- LiveKit Unity issue #169 reports silent mono-audio receive failures under
  default stereo output settings. Our current symptom is uplink, not downlink,
  because the placement greeting is audible; still, Android/Unity audio output
  mode must stay on the compatibility checklist before release.
- Android's audio-input sharing docs confirm a capture client can receive
  silence when another higher-priority app captures audio, and that active
  input devices can change between built-in mic and Bluetooth headset. The HUD
  `peak/nz/native/nerr` fields are therefore required, not just a boolean
  "mic on" indicator.
- Android 12+ Bluetooth permissions require `BLUETOOTH_CONNECT` for paired
  device communication. The formal Android library declares it and
  `MicrophonePublisher` requests it at runtime before route setup.
- Android 15+ 16 KB page-size support remains a packaging gate for native
  libraries. This is not the current "greeting only" symptom because LiveKit is
  loading and playing audio, but every release APK must keep running the
  alignment checker for `liblivekit_ffi.so` and other arm64 native libraries.

Current simulated state matrix:

| Condition | Expected formal behavior | Current status / remaining risk |
|:--|:--|:--|
| No Bluetooth, phone mic | Keep media/default route, speaker/phone output, Unity mic first, AudioRecord fallback if Unity frames fail. | Code path exists; iQOO still needs non-zero `frames/ch/readSr/peak/nz` proof. |
| Bluetooth output only / A2DP | Keep output on headset if Android owns it; do not force SCO; capture via phone/default mic fallback. | Code now clears stale speaker/earpiece communication device for output-only Bluetooth; phone proof pending. |
| Bluetooth SCO / BLE headset mic | Try active communication route only when `getCommunicationDevice()` confirms it; short SCO probe, then 48 kHz/system/default/AudioRecord fallback. | Code path exists; Unity official docs say BT mic can still fail, so phone mic fallback is product policy, not a temporary hack. |
| Bluetooth enabled but no connected device | Must never block START or mic publish; fall through to phone/default route. | Code no longer treats Bluetooth preference as a hard gate; phone proof pending. |
| Other app using mic / assistant / recorder | Android may silence this app even when route/focus look healthy. | Missing native `AudioRecordingCallback` / `isClientSilenced()` telemetry; HUD zero-peak guard partially covers the symptom. |
| App pause/resume or route reset | Keep LiveKit room/session; rebuild local mic/video only as needed. | Lifecycle refresh/watchdog exist; background and reconnect are still unproven on iQOO. |
| Long-lived room with stale Unity participant | RPC greeting can work while RoomIO listens to old participant. | Brain now rebinds RoomIO on `onSceneReady`/`onGosloPlaced`; Castle deployment + log proof required. |

Compatibility verdict:

The architecture is not fundamentally conflicting, but the overlap is fragile:
Unity's Android mic abstraction, Android's communication-device routing, and
LiveKit Unity's Developer Preview audio bridge each have known edge cases. The
safe production stance is exactly the current split: Android native route
truth, Unity/LiveKit local mic executor, serial track rebuild only, phone/default
MIC as reliable fallback, and Brain RoomIO rebinding to the active Unity phone.
The next blocker is evidence, not another protocol rewrite: one rebuilt iQOO
pass must pair HUD local capture fields with Castle Brain logs.

## 2026-05-18 iQOO Live Run - Uplink Starts, Then Android Silences It

Fresh ADB/LogCat review after the rebuilt iQOO run changes the current
diagnosis:

- The App is no longer in the old "no uplink ever starts" state. Unity logs
  show LiveKit connected in about 1.66s, Brain/agent audio subscribed, AR video
  first frame published, and `MicrophonePublisher` started the App-owned
  `android_audio_record` source on `speaker@48000Hz`.
- The successful start line was:
  `publishing started: device='android_audio_record' ... audioReadFrames=1`.
  The phone HUD also showed fresh AR frames and a non-zero local audio peak in
  the user screenshot. This means local capture and LiveKit track publication
  initially worked.
- Android `dumpsys audio` later records the same package's active recorder as
  `rec update ... silenced pack:com.parrotcarriers.app`, followed by
  `rec release ... silenced`, around the same time Unity logged
  `ARVideoPublisher Blit paused (lifecycle=ShortBackground)`.
- Therefore the current "responds at first, then stops hearing me" blocker is
  most likely Android lifecycle/audio policy silencing or releasing the local
  recorder after focus/background/route changes. It is not proven to be
  LiveKit server capacity, Mint, Brain dispatch, or RoomSetting.

Code follow-up:

- `MicrophonePublisher.OnApplicationFocus(true)` no longer republishes during
  `_publishInProgress`. The old path could tear down a just-started
  `AndroidAudioRecord` track on focus-regain callbacks.
- Focus regain now only schedules a delayed health probe. It rebuilds the
  local mic track if `AudioRead` frames are stale or the native recorder has
  stopped; otherwise it keeps the existing track.
- This remains a local media repair only: no LiveKit room reconnect, no Mint
  token refresh, no Brain redispatch.

Open proof / next instrumentation:

- The next phone pass must start from fresh LogCat (`adb logcat -c`), keep the
  App foreground for at least 2-3 minutes, then intentionally test app switch,
  Bluetooth connect/disconnect, and network flap as separate cases.
- HUD must show `frames/ch/readSr/peak/nz/wd/native/nerr` continuously. If
  `frames` stop and `wd=` changes to a recovery reason, check that the local
  mic track rebuilds without room reconnect.
- The 3-5s response delay is not yet attributed. PC control-plane health for
  App API, Mint, and Orchestrator is around 120-130ms, but the missing metric is
  end-to-end voice timing: client capture -> LiveKit publish -> Brain
  STT/VAD -> LLM -> TTS -> LiveKit downlink. Add latency telemetry before
  blaming LiveKit server size or ECS CPU.

## 2026-05-18 Auto Route Correction

User review clarified the intended phone behavior: network locality is useful
for latency comparison, but Bluetooth/mic selection is a local Android route
problem. The formal App should follow the phone's route policy: when a real
Bluetooth SCO / BLE headset / wired communication capture device is available,
`auto` may enter Android communication mode and select it; when only output
Bluetooth/A2DP exists, keep media mode so Parrot output stays on the headset and
capture falls back to phone/default mic.

Bug found:

- `AndroidAudioRouteManager.shouldKeepMediaModeForDefaultCapture()` had become
  too broad and returned true for `auto` unconditionally.
- That could prevent the App from selecting a valid Bluetooth headset
  communication device, making "Bluetooth connected" behave like phone/default
  capture forever.

Fix:

- `system_default` and `phone_mic` still stay media-safe in the route-lab
  bridge. The current formal demo default does not depend on this bridge
  because `simplePhoneMicMode=true` bypasses Android communication routing.
- `auto` now checks `hasSelectableCommunicationCaptureDevice()`.
- If Android exposes SCO / BLE headset / wired / USB headset capture, `auto`
  proceeds to `MODE_IN_COMMUNICATION` and `setCommunicationDevice`.
- If no such capture device exists, `auto` stays media-safe and preserves the
  phone/default mic path.

This is still a local route repair only: it does not reconnect the room, mint a
new token, or dispatch a new Brain job. The next iQOO build should compare:

- Bluetooth connected before START: HUD `input_route` should become
  `bluetooth_sco` only if Android exposes a selectable communication headset.
- A2DP/output-only Bluetooth: HUD output should show Bluetooth/A2DP while input
  remains phone/default mic.
- Bluetooth off/no device: START and uplink must not block; phone/default mic
  remains the fallback.

## 2026-05-18 Phone Route Regression After Laptop Restart

Evidence from iQOO after restarting the laptop Castle backend:

- Unity HUD showed `LK on / Brain on / Mic pub`, `Uplink published`, non-zero
  local audio `peak`, and `wd=healthy`.
- LiveKit server logs showed both Unity and Brain participants active; Unity
  published an audio track and Brain published its agent audio track.
- Android `dumpsys audio` showed the App recorder active and `not silenced`,
  but the global audio session had `Requested mode = MODE_NORMAL`,
  `Actual mode = MODE_NORMAL`, and the route snapshot/HUD had
  `audio_focus=abandoned`.
- Brain logs showed normal startup/registering but no later user-turn evidence.

Conclusion:

- This was not Mint, RoomSetting, or laptop LiveKit reachability.
- The formal App had a false-good state: the mic track existed, but Android
  route ownership was relaxed back to media mode. That can make the App look
  connected while Realtime voice turns do not reliably trigger.

Superseding decision:

- The route-lab Java bridge is no longer used by the formal default App audio
  path. It keeps its previous media-safe semantics behind
  `simplePhoneMicMode=false`.
- The default fix is now simpler: `MicrophonePublisher.simplePhoneMicMode=true`
  avoids Android communication routing entirely and returns to the proven
  ParrotDev-style Unity phone microphone path.

Next proof:

- Rebuild the Android app after the simple phone-mic change.
- HUD should show `simple phone mic / route lab off` and uplink route
  `simple_phone_mic_48k`.
- Do not use `audio_focus=abandoned` as the primary pass/fail signal in simple
  mode; the pass/fail signal is whether Brain hears the phone mic reliably.

## 2026-05-18 Stable Demo Audio Baseline

User decision after repeated iQOO proof attempts: stop making the formal demo
depend on the Bluetooth/SCO/AudioRecord route ladder. The route-aware design is
not deleted, but it is now an experiment behind `simplePhoneMicMode=false`.

Current formal default:

- `MicrophonePublisher.simplePhoneMicMode=true`.
- Unity publishes exactly one `MicrophoneSource` track using the default phone
  microphone device, fixed to `simple_phone_mic_48k`.
- The publish path does not request Bluetooth permission, does not call
  `AudioRouteManager.RequestCommunicationMode(...)`, does not subscribe to
  route-change republish events, does not start the App-owned Android
  `AudioRecord` source, and does not promote zero-peak Unity mic frames into
  Android AudioRecord.
- Settings-page mic cycling is ignored and reported as
  `ignored:simple_phone_mic_mode`.
- HUD/menu labels must make the mode visible as `simple phone mic / route lab
  off` so a later test cannot confuse this with production Bluetooth routing.

Reason:

- ParrotDev's simple phone-mic path was the only proven stable voice path.
- The formal route ladder fixed several real bugs but produced regressions that
  blocked the real App loop: delayed/unstable speech, route churn, false-good
  states, and Bluetooth behavior that was harder to reason about than Android's
  own phone default.
- The immediate product goal is a stable phone App for AR placement, model
  control, LineA/LineB conversation, and homepage testing. Bluetooth/SCO input
  can return later as a focused lab feature with its own phone matrix.

Future route-lab rule:

- Re-enabling `simplePhoneMicMode=false` must be treated as a separate
  Bluetooth/SCO feature branch, not as the default formal App path.
- It must pass: Bluetooth connected before START, connect-after-start,
  disconnect fallback, other-media coexistence, app pause/resume, LineA,
  LineB, and no room reconnect/token mint/Brain redispatch on local device
  changes.

## 2026-05-18 LineA One-Question-One-Answer Policy

User decision: for the current phone demo, disable LineA voice barge-in so the
conversation behaves as simple question -> answer -> next question. This is not
a Unity mic mute hack. It is a Brain/Gemini Live session policy.

Implementation:

- `src/parrot/brain/linea_turn_policy.py` owns the LineA policy.
- Default `PARROT_LINEA_BARGE_IN_ENABLED` is unset/`0`, so LineA builds Google
  Realtime with `RealtimeInputConfig(activity_handling=NO_INTERRUPTION)`.
- This keeps Gemini Live's native automatic activity/end-of-turn detection, but
  prevents start-of-activity from cutting off the active model response.
- `PARROT_LINEA_BARGE_IN_ENABLED=1` restores provider defaults for a deliberate
  low-latency overlap lab only.
- `src/parrot/brain/line_status.py` exposes `turn_policy`,
  `barge_in_enabled`, and `activity_handling` in the LineA readiness payload.

Important nuance:

- LiveKit Agents 1.5.5 rejects `AgentSession(allow_interruptions=False)` while
  a RealtimeModel still exposes server-side turn detection. Do not "fix" this
  by forcing the deprecated session flag. The valid LineA lever is Google
  Realtime `activity_handling=NO_INTERRUPTION`.
- This reduces self-interruption and echo-driven barge-in, but it is not the
  final echo-cancellation solution. Phone speaker echo can still be heard by the
  model as later input if the acoustic route is bad. For demo stability, combine
  this with the simple phone-mic baseline and, when possible, isolated output.

Validation:

- `uv run pytest tests/test_brain/test_linea_turn_policy.py -q`
- `uv run pytest tests/test_brain/test_app_first_version_facade.py -q`
- `uv run python -m py_compile src/parrot/brain/agent.py src/parrot/brain/line_status.py src/parrot/brain/linea_turn_policy.py`

## 2026-05-19 Local Half-Duplex Phone-Mic Gate

User decision: keep the current demo path simple and stable:

- phone microphone is the only default uplink source;
- Parrot/agent downlink speech locally mutes the already-published uplink track;
- the LiveKit room is not reconnected;
- the local audio track is not unpublished for agent speech;
- Android Bluetooth/SCO communication routing is not forced or stolen.

Implementation:

- `RoomManager` keeps the strong `AudioStream` references and records local
  `AudioSource` objects for playback; only `agent-*` / `brain` downlink
  sources feed the microphone gate.
- Each frame, `RoomManager` samples Brain/agent remote audio output peak
  locally with `AudioSource.GetOutputData(...)`. If the peak is above the
  small speech threshold, it holds `RemoteAudioPlaybackActive` for a short tail
  window.
- `MicrophonePublisher` polls `RoomManager.RemoteAudioPlaybackActive`. On state
  changes it calls `((ILocalTrack)_audioTrack).SetMute(muted)` on the existing
  local audio track. This uses the pinned LiveKit Unity SDK's supported mute
  path and preserves the current track/room/session.
- HUD now exposes `gate=clear|mute`, `gpk=<remote peak>`, and
  `gr=<gate reason>` beside the microphone uplink status.

Reason:

- This directly addresses external-speaker echo and Gemini self-interruption
  without depending on Android Bluetooth microphone behavior.
- It is compatible with LineA and LineB because it is local downlink-vs-uplink
  gating, not a provider-specific RPC or backend policy.
- It is deliberately not a replacement for production echo cancellation,
  Bluetooth route UX, or LineB voiceprint/echo policy. Those remain later
  route-lab/phone-stability work.

Phone proof required:

- With phone speaker output, Parrot speech should set HUD `gate=mute` while it
  talks and return to `gate=clear` after the tail.
- User speech after Parrot finishes should still reach Brain without room
  reconnect, token mint, Brain redispatch, or `UnpublishTrack`.
- With Bluetooth output, this should not force SCO/communication mode; if
  Android routes output to the headset naturally, the same phone-mic uplink gate
  still applies.
