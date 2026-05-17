# Unity Formal App Audio Route Research - 2026-05-16

Scope: formal Unity App audio routing for iQOO Neo9, Bluetooth headset input/output, phone microphone fallback, app background/resume, and LiveKit track stability.

This note is a research guard for future implementation. Do not treat old Smoke/LineA connectivity scripts as the formal audio-routing mechanism.

## Read Before Implementation

- `codex_workspace/skills/unity_ar_app.md`
- `.cursor/skills/livekit-unity-lifecycle/SKILL.md`
- `.cursor/skills/livekit-unity-lifecycle/IMPL_REF.md` section 7
- `.cursor/skills/client-sdk-unity/SKILL.md`
- `.cursor/skills/livekit-unity-video-publish/IMPL_REF.md`
- `.cursor/memory/architecture/Interface/menu_design_complete_20260507.md` section 7.6.4
- `codex_workspace/design_workspace/backend_interface_map/app/unity_livekit_ecp_sva_data_flow_map_20260515.md`
- `codex_workspace/design_workspace/tasks/APP_WEB_PARALLEL_TODOLIST_20260513.md` APP-015.23 and APP-024

## Existing Code Boundary

`MicrophonePublisher` is useful, but it should be treated as the LiveKit microphone track executor:

- request microphone permission
- publish/unpublish the `TrackSource.SourceMicrophone` track
- rebuild `MicrophoneSource` serially after route changes
- report audio publish health

It must not become the final native Android route owner by itself.

`AudioRouteDetector` is currently a C# telemetry/fallback detector. It can observe `AudioManager.getDevices(...)`, legacy route flags, `AudioSettings.OnAudioConfigurationChanged`, and polling, but it does not provide a production-grade route selection policy.

`AudioRoutePolicyBrainReporter` is a compact Brain observer. It may report `input_route`, `output_route`, and route status through `setLineBAudioRoutePolicy`. Brain may observe and adapt LineB echo policy, but Brain must not directly drive Unity microphone route switching or LiveKit room lifecycle.

`MIC NEXT` / `MIC AUTO` in the formal Settings panel are debug/diagnostic controls for Unity device-name preference. They are not the final phone UX for Bluetooth routing.

## Smoke Script Pollution Boundary

Old LineA/Smoke connectivity work was valuable for proving that:

- Unity can request microphone permission.
- Unity can publish a microphone track into LiveKit.
- Brain can join the same room and receive audio/RPC presence.
- `MicrophonePublisher` can be mounted under the formal runtime services.

It does not prove or define:

- Bluetooth default priority.
- SCO/A2DP input/output policy.
- Android native communication-device switching.
- App coexistence with other media apps.
- Phone background/resume route recovery.
- LineB echo/voiceprint stability under real audio hardware.

Future App work must not copy `ParrotSmokeScene`, old LineA self-check scripts, or `AppV1SmokeReferenceUiController` audio assumptions into the formal route policy.

## External Research Findings

Android official guidance:

- Android exposes communication-device routing APIs through `AudioManager`, including `getAvailableCommunicationDevices()` and `setCommunicationDevice(...)`. These are the correct Android 12+ route-control surfaces for communication use cases.
  Source: https://developer.android.com/reference/android/media/AudioManager
- Several legacy communication-routing calls are no longer the preferred path on modern Android. The formal App should not be built around old speakerphone/SCO toggles as the primary routing API when communication-device routing is available.
  Source: https://developer.android.com/reference/android/media/AudioManager
- Android distinguishes audio device types such as `TYPE_BLUETOOTH_SCO` and `TYPE_BLUETOOTH_A2DP`. A2DP is not the same thing as a bidirectional headset microphone path.
  Source: https://developer.android.com/reference/android/media/AudioDeviceInfo
- Android 12+ Bluetooth device interaction can require `BLUETOOTH_CONNECT` runtime permission in addition to microphone permission.
  Source: https://developer.android.google.cn/develop/connectivity/bluetooth/bt-permissions?hl=en
- Apps that play/capture communication audio must handle audio focus so they do not unnecessarily fight other media apps.
  Source: https://developer.android.com/media/optimize/audio-focus
- Unity's generic audio-device callback cannot be treated as the whole truth for headset routing. Unity has a public issue where `AudioSettings.OnAudioConfigurationChanged` was not called for Bluetooth headset connection on Android/iOS.
  Source: https://issuetracker.unity3d.com/issues/android-ios-audiosettings-dot-onaudioconfigurationchanged-is-not-called-when-connecting-bluetooth-headset

LiveKit guidance:

- LiveKit Android has an `AudioSwitchHandler` that manages audio focus and output device routing for voice sessions. It can route to preferred devices and documents Android device-specific Bluetooth behavior.
  Source: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.audio/-audio-switch-handler/index.html
- LiveKit Android's `AudioSwitchHandler.forceHandleAudioRouting(...)` is an example of the kind of native route owner Unity currently lacks: it takes a target output device and owns the routing side effects for the voice session.
  Source: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.audio/-audio-switch-handler/force-handle-audio-routing.html
- LiveKit publish paths still need microphone permission and a microphone track. In Unity, the App must keep the room connection separate from local media publish/unpublish.
  Source: https://docs.livekit.io/transport/media/publish/
- LiveKit Unity is still a developer-preview SDK and Android audio behavior must
  be phone-proven. Public issue #77 reports `RtcAudioSource` / microphone
  streaming failing on some Android brands/devices even when the same hardware
  works through native Android paths. This does not prove our exact iQOO bug,
  but it is enough to keep Unity-side audio capture and FFI frame delivery as
  separate diagnostics instead of treating `PublishTrack` as proof of speech
  uplink.
  Source: https://github.com/livekit/client-sdk-unity/issues/77
- LiveKit Unity `MicrophoneSource.AudioRead` is an official SDK event emitted
  when samples are captured from the underlying source. The formal App now uses
  it as the first local "SDK source received audio frames" check; it still does
  not prove remote Brain/STT heard the audio if native FFI capture later logs an
  error.
  Source: https://livekit.github.io/client-sdk-unity/api/LiveKit.MicrophoneSource.html

Project skill guidance:

- The LiveKit lifecycle skill says Bluetooth is in formal App scope. With a Bluetooth input route, Unity should default to Bluetooth. Bluetooth/phone mic switching must be serial microphone `unpublish -> rebuild source -> publish`, and must not reconnect the LiveKit room.
- `session/audio_route_policy` remains the observation/control-plane candidate; it is not a license for Brain to switch Unity audio devices implicitly.
- The local LiveKit Unity package exposes `Room.Reconnecting`, `Room.Reconnected`, and `Room.Disconnected`, but the project wrapper still needs watchdog/heartbeat intent signals because mobile disconnect reason/timing cannot be the only truth. Audio route changes are not room reconnect reasons by themselves.

## Round 2 - Formal Layering Decision

The formal phone audio design should use five layers:

| Layer | Owner | Responsibility | Must not do |
|:--|:--|:--|:--|
| L0 Android native route | Future `AndroidAudioRouteManager` bridge | Query available communication devices, observe add/remove/default changes, request/release audio focus, apply `setCommunicationDevice(...)` when allowed, expose permission/device snapshots. | Join LiveKit, call Brain RPC, persist RoomSetting. |
| L1 Unity route policy | Future C# `AudioRouteManager` wrapper | Choose auto/default/manual route, debounce changes, decide whether route transition needs mic republish, publish a stable route snapshot to UI/services. | Guess final route only from `Microphone.devices`, reconnect the room, hide permission failures. |
| L2 LiveKit media executor | `MicrophonePublisher` | Request mic permission, serialize unpublish/rebuild/publish of `TrackSource.SourceMicrophone`, choose sample-rate/source according to accepted route snapshot, report health. | Own Android routing policy or treat A2DP as a microphone input. |
| L3 LiveKit room lifecycle | `RoomManager`, `AppLifecycleManager`, `LiveKitReconnectSupervisor` | Fresh-token reconnect on passive room failure, graceful shutdown, heartbeat/session hold, background/resume state. | Reconnect the room to handle normal headset plug/unplug. |
| L4 Brain/ECP observation | `AudioRoutePolicyBrainReporter`, ECP health/state | Send compact `setLineBAudioRoutePolicy` and lifecycle/health facts so LineB echo policy can adapt. | Switch Unity devices, restart Brain, store durable settings. |

This split keeps the formal App close to Android and LiveKit Android's native
strategy while preserving the current Unity/LiveKit SDK investment. It also
prevents the old smoke path from becoming product behavior.

## Option Comparison

| Option | Verdict | Why |
|:--|:--|:--|
| Keep Unity-only `Microphone.devices` + polling | Reject as final; keep as fallback/diagnostic. | Fast to code, but weak for Bluetooth connect-after-start, SCO/A2DP distinction, audio focus, and OS permission state. Unity callback evidence is not reliable enough. |
| Android native route bridge + current `MicrophonePublisher` executor | Preferred V1. | Matches Android communication-device APIs, mirrors LiveKit Android's dedicated route handler concept, and avoids room reconnect churn. |
| Reconnect LiveKit room on every audio device change | Reject. | Causes token/Brain churn, races with shutdown/identity cool-down, and conflicts with lifecycle skill guidance. |
| Embed LiveKit Android SDK inside Unity only for `AudioSwitchHandler` | Defer/reject for now. | Too invasive beside the Unity SDK/FFI room owner; useful as design reference, not a second client SDK in the App. |
| OS default only with no settings override | Partial fallback only. | Safer than bad manual forcing, but not enough for user-visible debugging or iQOO Bluetooth proof. |

## Phone Strategy

Normal voice/AR mode:

- Ask Android for microphone permission first, then Bluetooth permission when required by platform level.
- Enter a communication audio mode only while the App intends to publish voice.
- Auto route order: explicit user override if valid, otherwise Bluetooth communication headset, then wired/USB headset, then phone microphone/default output.
- If only A2DP is present, treat it as output-only; keep input on Android default/phone mic unless a SCO or communication input appears.
- On route change, do not disconnect LiveKit. Rebuild the microphone track through the executor only when the accepted input route or sample-rate policy changes.
- When another app is already playing media, request focus politely and degrade/report if the OS refuses or changes the route. Do not assume Parrot owns the headset forever.

Silent / 2D workspace / no-dialogue mode:

- Keep LiveKit room and heartbeat alive when the product mode requires session continuity.
- Mute or unpublish microphone according to the current capability mode.
- Continue observing route changes, but defer mic republish until voice intent is enabled again.
- Release or avoid long-lived voice audio focus when the App is not actively doing voice capture.

Background/resume:

- Short background: keep intent state, pause AR/video as required, avoid immediate room reconnect.
- Resume: re-query Android route snapshot, compare route version, republish mic only when voice intent is still enabled and the room is connected.
- Long background or passive disconnect: let `LiveKitReconnectSupervisor` own fresh-token reconnect. After reconnect, rerun Brain sync and then reapply the latest route snapshot.
- Any route/focus error should surface as degraded HUD/health state, not a fake connected/stable status.

## Implementation TODO Before Code

1. Manifest audit: confirm `RECORD_AUDIO`, network, foreground/audio-related permissions, and Android 12+ `BLUETOOTH_CONNECT` handling for the formal package.
2. Native bridge API sketch: define the Java/Kotlin -> C# DTO fields before writing code (`route_version`, available devices, selected input/output, permission state, focus state, route source, error).
3. Unity wrapper design: expose an evented `AudioRouteSnapshot` and user preference (`Auto`, `Bluetooth`, `PhoneMic`, possibly `SystemDefault`) without saving it as RoomSetting yet.
4. `MicrophonePublisher` refactor: consume accepted snapshots from the wrapper, keep current device-name fallback only when native route data is unavailable, and serialize rebuilds behind one queue.
5. Settings UX: replace `MIC NEXT` / `MIC AUTO` as the visible production path with a route status/override panel, while keeping debug controls hidden or clearly marked.
6. Phone proof plan: test iQOO Neo9 with Bluetooth already connected, connect-after-start, disconnect fallback, other media app coexistence, short/long background, LineA and LineB voice, and network reconnect.

## Round 3 - Current Unity Audit Before Implementation

Observed in `unity/ArSpike` on 2026-05-16:

| Area | Current state | Impact |
|:--|:--|:--|
| Android plugin root | No `Assets/Plugins/Android/**` exists. | There is no native Java/Kotlin route owner yet. New native work must create this root deliberately and update the inventory SSOT. |
| Custom Android manifest | `ProjectSettings.asset` has `useCustomMainManifest: 0` and no App-owned `AndroidManifest.xml`. | Unity/package defaults may provide camera/mic through APIs/packages, but Bluetooth and future foreground/audio-service permissions are not explicitly owned by the App yet. |
| Android SDK targets | `AndroidMinSdkVersion: 30`, `AndroidTargetSdkVersion: 0` (Unity default/installed target). | Runtime permission behavior must assume Android 12+ on iQOO Neo9 and check `BLUETOOTH_CONNECT` when target/runtime level requires it. |
| Microphone permission | `AppStartupFlowController` and `MicrophonePublisher` use `Application.RequestUserAuthorization(UserAuthorization.Microphone)`. | OK for current mic gate, but not enough for Bluetooth device interaction or route management. |
| Current route detection | `AudioRouteDetector` calls Android `AudioManager.getDevices(...)` through `AndroidJavaObject`, falls back to legacy flags, and polls/uses `AudioSettings.OnAudioConfigurationChanged`. | Useful telemetry/fallback. It does not call `setCommunicationDevice`, register Android callbacks, request focus, or own permission. |
| Current mic executor | `MicrophonePublisher` already serializes route republish, sets LiveKit `RtcAudioSource.DefaultMicrophoneSampleRate`, treats A2DP as output-only, and only scans BT device names for SCO. | Good executor base. It should be refactored to consume accepted route snapshots from the new route manager rather than owning policy. |
| Brain report | `AudioRoutePolicyBrainReporter` reports compact `setLineBAudioRoutePolicy` and rejects business-error payloads. | Keep as observer. New route manager should feed richer local status to HUD and reporter, but Brain still must not switch devices. |
| Settings UI | `FormalHomeMenuController` exposes audio rescan/report plus `MIC NEXT`/`MIC AUTO`. | Keep as debug until route-manager settings panel exists. Do not make these the user-facing production solution. |

Conclusion: current code has a usable LiveKit mic-track executor and diagnostic
detector, but it lacks the Android-native owner required for production
Bluetooth/SCO/A2DP behavior.

## Round 3 - Native Bridge API Design

Proposed native class:

```text
Assets/Plugins/Android/
  AndroidManifest.xml                    # only App-owned permissions/queries
  src/com/parrotcarriers/audio/AndroidAudioRouteManager.java
```

Unity C# wrapper:

```text
Assets/ParrotApp/Runtime/Scripts/LiveKit/
  AndroidAudioRouteManager.cs            # Android bridge wrapper
  AudioRouteSnapshot.cs                  # Unity DTO / policy snapshot
  AudioRouteManager.cs                   # platform facade, fallback to detector
```

Native methods:

| Method | Direction | Meaning |
|:--|:--|:--|
| `initialize(gameObjectName, callbackMethod)` | Unity -> Android | Capture Activity/AudioManager, register callbacks/listeners, send first snapshot. |
| `refresh()` | Unity -> Android | Force device/focus/permission snapshot. |
| `setRoutePreference(preference)` | Unity -> Android | Store desired route: `auto`, `bluetooth`, `phone_mic`, `system_default`; do not publish mic by itself. |
| `requestCommunicationMode(enabled)` | Unity -> Android | Enter/leave communication-oriented mode and audio focus only while voice capture is intended. |
| `applyPreferredCommunicationDevice()` | Unity -> Android | Try `setCommunicationDevice(...)` when supported and permitted; return success/failure in snapshot. |
| `clearCommunicationDevice()` | Unity -> Android | Release explicit device routing on silent/2D/no-dialogue or shutdown. |
| `dispose()` | Unity -> Android | Unregister listeners/callbacks and abandon focus. |

Unity callback payload should be JSON so the wrapper can log and preserve
forward-compatible fields:

```json
{
  "route_version": 12,
  "timestamp_unix_ms": 1778912345678,
  "source": "android_audio_manager",
  "platform": "android",
  "api_level": 35,
  "preference": "auto",
  "input_route": "bluetooth_sco",
  "output_route": "bluetooth_sco",
  "communication_device_type": "TYPE_BLUETOOTH_SCO",
  "communication_device_name": "Headset",
  "available_inputs": ["builtin_mic", "bluetooth_sco"],
  "available_outputs": ["speaker", "bluetooth_a2dp", "bluetooth_sco"],
  "microphone_permission": "granted",
  "bluetooth_connect_permission": "granted",
  "audio_focus": "granted",
  "mode": "communication",
  "requires_mic_republish": true,
  "recommended_sample_rate_hz": 16000,
  "is_degraded": false,
  "error": ""
}
```

Snapshot vocabulary:

| Field | Values |
|:--|:--|
| `preference` | `auto`, `bluetooth`, `phone_mic`, `system_default` |
| `input_route` | `system_default_microphone`, `phone_mic`, `wired_headset`, `bluetooth_sco`, `unknown` |
| `output_route` | `speaker`, `earpiece`, `wired_headset`, `bluetooth_a2dp`, `bluetooth_sco`, `unknown` |
| `permission` fields | `granted`, `denied`, `not_required`, `unknown` |
| `audio_focus` | `granted`, `delayed`, `denied`, `not_requested`, `abandoned` |
| `mode` | `normal`, `communication`, `silent`, `unknown` |

The Unity wrapper should translate the snapshot into the existing
`AudioRoutePolicy` only at the boundary where `MicrophonePublisher` needs an
input route and sample-rate policy. The original `AudioRouteDetector` remains
the fallback provider when the native bridge is missing, disabled, or fails.

## Round 3 - State Machine

```text
Uninitialized
  -> Initializing
  -> ObservingOnly
  -> VoiceRouteRequested
  -> VoiceRouteActive
  -> RouteChanging
  -> Degraded
  -> ObservingOnly
  -> Disposed
```

State responsibilities:

| State | Meaning | LiveKit media action |
|:--|:--|:--|
| `ObservingOnly` | App is silent, in 2D/no-dialogue, not yet connected, or publish intent is false. Route changes are cached. | No mic publish/rebuild. |
| `VoiceRouteRequested` | START or mode change wants voice. Native bridge requests focus/communication device. | Wait for accepted snapshot before publish where possible. |
| `VoiceRouteActive` | Accepted route is stable enough for capture. | `MicrophonePublisher` may publish or stay published. |
| `RouteChanging` | Android callback/focus/device change detected. | Debounce; republish only if accepted input route/sample-rate changed. |
| `Degraded` | Permission/focus/device/routing failed. | Keep room alive, surface HUD health, stop or keep mic according to failure kind. |
| `Disposed` | App shutdown or service destroyed. | No media action; shutdown chokepoint owns unpublish/disconnect. |

Important invariants:

- `RouteChanging` does not reconnect LiveKit.
- Only one mic republish coroutine may run.
- Route snapshot version must be monotonic; late Android callbacks cannot roll
  Unity back to stale state.
- User override is local runtime setting until a separate persistence task is
  approved; do not write it into RoomProfile silently.
- In 2D/silent/no-dialogue mode, the route manager may observe but should not
  hold voice audio focus indefinitely.

## Round 3 - Implementation Order

1. Add an App-owned Android manifest/plugin root with only required permissions and no unrelated template imports.
2. Add DTO/wrapper classes behind Android compile guards; fallback to existing `AudioRouteDetector` in Editor/non-Android.
3. Mount `AudioRouteManager` under formal `RuntimeServices`; keep `AudioRouteDetector` as fallback/telemetry.
4. Refactor `MicrophonePublisher` to consume `AudioRouteManager` accepted snapshots while preserving current serial republish and health behavior.
5. Refactor `AudioRoutePolicyBrainReporter` to report accepted snapshots and route-manager error/degraded status.
6. Replace visible `MIC NEXT`/`MIC AUTO` with a production Settings route panel; leave debug controls hidden or labeled.
7. Add static tests for manifest/plugin presence, forbidden smoke references, DTO vocabulary, and no room reconnect on route-change code paths.
8. Only after code compiles, run the iQOO Neo9 phone matrix.

## Round 4 - Implementation Status

Implemented on 2026-05-16:

- Added App-owned Android route plugin root:
  `unity/ArSpike/Assets/Plugins/Android/ParrotAudioRoute.androidlib/**`.
- Added explicit manifest permissions for microphone, audio settings, legacy
  Bluetooth, and Android 12+ `BLUETOOTH_CONNECT`.
- Added Java `com.parrotcarriers.audio.AndroidAudioRouteManager` to query
  devices, observe add/remove and communication-device changes, request/release
  communication audio focus, call `setCommunicationDevice(...)` when available,
  and send JSON snapshots to Unity.
- Added Unity DTO/wrapper/facade:
  `AudioRouteSnapshot.cs`, `AndroidAudioRouteManager.cs`, and
  `AudioRouteManager.cs`.
- Refactored `MicrophonePublisher` to consume `AudioRouteManager` accepted
  snapshots, request Android Bluetooth-connect permission before voice capture
  when required, and keep route changes as serial local mic-track rebuilds
  rather than LiveKit room reconnects.
- Refactored `AudioRoutePolicyBrainReporter`, `FormalHomeHudController`, and
  `FormalHomeMenuController` to prefer route-manager status while keeping
  `AudioRouteDetector` as fallback/diagnostic evidence.
- Added static guards in `tests/test_unity/test_app_v1_meta_ui_static.py`.
- Follow-up audit fix: native route preferences are now cached until
  communication mode is active, so startup/settings observation does not apply a
  phone route before the App intends to publish voice. The API-31
  communication-device listener is also isolated in an API-31 nested holder so
  the minSdk 30 build can load the main plugin class and fall back gracefully on
  Android 11.
- Follow-up lifecycle fix: `MicrophonePublisher` now listens to formal
  `AppLifecycleManager.OnStateChanged` and refreshes the accepted route snapshot
  on resume-like connected/running/degraded states, so pause/resume is not
  dependent only on plug/unplug callbacks.
- Android build fix: `ParrotAudioRoute.androidlib` no longer imports
  `com.unity3d.player.UnityPlayer`. Unity C# passes the current Activity and an
  `AndroidJavaProxy` implementation of `AudioRouteSnapshotCallback`; callbacks
  are marshaled through `UnityMainThread.Enqueue` before touching Unity state.
- Android dex fix: the route androidlib manifest and source `build.gradle`
  declare the route package/namespace as `com.parrotcarriers.audio`, and the
  route library disables its own `BuildConfig` generation. This prevents the
  launcher module from colliding with a generated
  `com.parrotcarriers.app.BuildConfig` during dex merge.
- Uplink truth fix: LiveKit `PublishTrack` only proves the track was accepted by
  the room, and Unity `Microphone.GetPosition(...)` only proves the platform
  microphone ring buffer advanced. The formal App now also subscribes to
  LiveKit Unity `MicrophoneSource.AudioRead`; it reports audio published only
  after both the microphone position advances and at least one captured audio
  frame reaches the SDK source. If capture never starts, Unity unpublishes the
  track and reports `microphone_start_timeout` /
  `microphone_start_exception`; if the Unity microphone advances but no SDK
  audio frame appears, it reports `audio_read_timeout`. This prevents the
  formal App from showing fake `audio_published=true` when Android/Unity/LiveKit
  accepted the track but no voice samples are actually entering the uplink path.
- If publish intent is disabled, shutdown starts, or the room disconnects while
  Unity is waiting for microphone samples, the startup attempt aborts and cleans
  up instead of later marking the uplink as published.
- Cleanup fix: local track/source creation or `PublishTrack` failure clears the
  half-built `_micSource` / `_audioTrack` before retry, so a later route change
  or reconnect does not inherit stale local audio state.
- HUD diagnostic update: formal home now separates `UsingMic` from `Uplink` so
  phone tests can distinguish OS route/device selection from actual LiveKit
  microphone capture. The `Uplink` line includes SDK audio-frame count,
  captured channel count, captured sample rate, and latest peak level; use
  these fields before blaming Brain/STT when the user can hear the agent but the
  agent cannot hear the phone.

Validation so far:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- Unity MCP Android APK build to
  `unity/ArSpike/Builds/CodexVerify/ParrotApp-verify.apk` succeeded with
  `errors=0`, `warnings=3`.

Still not proven:

- Runtime Bluetooth permission prompt behavior on iQOO Neo9.
- Bluetooth pre-connected, connect-after-start, disconnect fallback,
  phone-mic fallback, other-media coexistence, pause/resume, LineA and LineB
  voice, and no LiveKit room deadlock.
- Production Settings route override UX. `MIC NEXT` / `MIC AUTO` remain
  diagnostic controls only.

## Formal App Target Policy

Default behavior:

- If a usable Bluetooth communication device is connected, input and output should default to Bluetooth.
- If Bluetooth disconnects, fall back automatically to the phone microphone plus appropriate phone output route.
- If Bluetooth connects while the App is already running, move to Bluetooth automatically.
- If the App is in silent/session-only mode, cache route changes but do not republish the microphone.
- If the user explicitly selects a phone microphone or other input in Settings, keep that preference visible and reversible.
- Route changes rebuild only the local microphone track; they do not trigger LiveKit room reconnect.

Stability behavior:

- Route-change handling must be serialized and debounced.
- Never overlap `UnpublishTrack` / `PublishTrack`.
- Rebuild `MicrophoneSource` after route/sample-rate changes instead of reconfiguring it in place.
- On publish failure, surface degraded HUD/health state; do not fake success.
- On app pause/resume, re-detect route and rebuild mic only when the room is still connected and publish intent remains enabled.
- LineB echo policy reads route state; it does not own device switching.

Coexistence behavior:

- Request appropriate Android audio focus for voice/communication modes.
- Release or avoid voice audio focus in 2D/silent/no-dialogue modes.
- Do not assume the App owns Bluetooth forever if another app is already playing media; route changes must degrade gracefully and report state.

## Implementation Direction

Likely formal components:

- `AndroidAudioRouteManager` native bridge under `Assets/Plugins/Android` or a small Android Java/Kotlin plugin.
- Manifest additions for microphone, audio settings, and Android 12+ Bluetooth connect permission as needed.
- Unity wrapper `AudioRouteManager` that exposes stable route snapshots and user preferences.
- `MicrophonePublisher` remains the LiveKit track executor and subscribes to formal route changes.
- `AudioRoutePolicyBrainReporter` reports accepted route snapshots to Brain after LiveKit/Brain presence.
- Formal Settings page should show:
  - current input route
  - current output route
  - permission state
  - publish state
  - Brain route-policy report state
  - optional user override with clear/auto

## Open Questions

- Which Android API level does the final iQOO Neo9 build target after Unity 2022.3.62f3 packaging?
- Does Unity's generated manifest already merge `RECORD_AUDIO`, or do we need an explicit App-owned manifest?
- Can LiveKit Unity expose enough native audio manager hooks, or do we need a local Android plugin that mirrors LiveKit Android `AudioSwitchHandler` behavior?
- Does forcing `MODE_IN_COMMUNICATION` from the Unity App conflict with LiveKit Unity internals?
- What is the correct UX copy for "Bluetooth output connected but microphone is still phone/default"?

## Acceptance

Do not mark APP-015.23 / APP-024 stable until the formal iQOO Neo9 App proves:

- fresh START with microphone permission
- Bluetooth already connected before START
- Bluetooth connects after START
- Bluetooth disconnects during LiveKit session
- phone mic fallback after disconnect
- app pause/resume while Bluetooth is connected
- app pause/resume after Bluetooth disconnect
- LineA and LineB both continue without LiveKit room deadlock
- route-policy RPC reports business-ok and does not hide `result.success:false`
- HUD reports degraded state when any track rebuild fails

## 2026-05-17 Deep Audit Follow-up

Follow-up record:
`backend_interface_map/app/unity_audio_livekit_deep_audit_20260517.md`.

The broader reread confirms this research direction:

- Keep Android native route ownership plus Unity `AudioRouteManager` and
  `MicrophonePublisher`; do not copy the old ParrotDev/Smoke LineA mic script
  as formal policy.
- Keep A2DP output-only and use Bluetooth SCO / communication input only when
  Android reports a real communication device.
- Keep route changes local to the microphone track. Do not reconnect the
  LiveKit room or mint a new token for headset changes.
- The startup `Microphone.GetPosition(...)` + LiveKit Unity
  `MicrophoneSource.AudioRead` guard is necessary but not sufficient.

P1 implementation update:

- `MicrophonePublisher` now has a steady-state uplink watchdog after publish
  succeeds. It checks `Microphone.IsRecording` when available, detects stale
  `AudioReadFrameCount` / last-frame age, marks degraded state in HUD and
  health, and queues one serialized local mic republish without reconnecting the
  room. This is code-complete but not phone-proven.
- Follow-up iQOO screenshot showed `bt-sco@16k` selected with
  `microphone_start_timeout` and `frames=0`. The first formal mitigation is a
  second local capture attempt at 48 kHz (`bluetooth_sco_capture_48k`), then a
  `phone_default_microphone` 48 kHz fallback, before reporting failure. This
  keeps the same LiveKit room and Brain job; it is not a reconnect or
  token-mint workaround.
- Follow-up iQOO Bluetooth-on/Bluetooth-off screenshots then showed the same
  no-uplink symptom after native routing fell back to `phone_mic`:
  microphone permission and audio focus were granted, but either Unity
  `Microphone.devices` was empty or Unity selected a device and still produced
  no `MicrophoneSource.AudioRead` frames. Formal App response is a native
  Android `AudioRecord` fallback (`AndroidPcmMicCapture` +
  `AndroidPcmMicrophoneSource`) as the final capture attempt after a temporary
  route override. The automatic ladder now keeps that override at
  `system_default` to preserve Bluetooth/A2DP downlink when possible; explicit
  PhoneMic forcing is deferred to a future manual recovery control. This
  fallback is allowed even if Unity lists a mic
  device, provided that the Unity capture attempts timed out at `frames=0`.
  This is a local capture source replacement, not a LiveKit room reconnect,
  token mint, or Brain dispatch. The next phone gate is simple: HUD
  `frames/ch/readSr` must become non-zero before LineA/LineB voice can be
  considered connected.

New P2 follow-up:

- If the HUD shows advancing frames / peak but Brain still cannot hear speech,
  inspect LiveKit Unity `RtcAudioSource` / FFI capture logs before changing
  backend code. `AudioRead` proves Unity-source capture, not remote Brain/STT
  consumption.
- Run APK-level 16 KB alignment verification after the next Android build.
  Package-level arm64 `liblivekit_ffi.so` currently verifies OK, but the APK is
  the final truth for Android 15+ devices.

## 2026-05-17 iQOO AudioRecord Start Fix

New evidence: the phone could hear the agent, but user speech never reached the
agent. HUD showed `LK on` / `Brain on` and valid route permission/focus, but
`Mic wait`, `Uplink not_published`, `frames=0`, and a final
`microphone_start_exception` from the `android_audio_record` fallback. This is a
client-side capture startup failure, not a Brain RPC, Mint, RoomSetting, or STT
failure.

Implementation update:

- The native route owner now treats no-headset AR companion voice as
  phone-mic + speaker, preferring `TYPE_BUILTIN_SPEAKER` before earpiece when
  no Bluetooth SCO or wired communication route is selected.
- Android AudioRecord sample-rate fallback now happens as distinct
  Unity-created LiveKit source attempts. Java `AndroidPcmMicCapture` stays
  strict to the requested rate and only switches between
  `VOICE_COMMUNICATION` and `MIC` within that rate, because LiveKit FFI rejects
  PCM frames whose sample rate differs from the `RtcAudioSource` construction
  rate.
- `AndroidPcmMicrophoneSource` asks Java for `lastError()` when `start()`
  returns false and rolls back `base.Start()` when native startup fails.
- `MicrophonePublisher` caches the last native AudioRecord state/error after a
  failed start so HUD `native=` / `nerr=` remains useful even after local source
  cleanup.
- The empty-device path now tolerates stale/unknown native route snapshots after
  mic permission is granted, so a transient route label cannot block the
  Android default/AudioRecord capture fallback with `no_microphone_devices`.

Validation performed:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28 passed.
- Unity Android Java plugin compiled with Unity 2022.3.62f3 Android classpath.

Next phone gate:

- Rebuild and run on iQOO Neo9.
- Success requires HUD `Uplink` to show non-zero `frames`, `ch`, `readSr`, and
  a visible `peak` response when speaking.
- If it still fails, use HUD `native=` / `nerr=` as the next root-cause input;
  do not infer success from audible agent output alone.

## 2026-05-17 BLE / Callback / Cleanup Follow-up

The next local sweep found three more formal-App risks:

- Bluetooth voice routing must include Android BLE headset devices, not just
  classic SCO. `TYPE_BLE_HEADSET` is now accepted as a communication-device
  target; fallback diagnostics also recognize BLE headset, BLE speaker, and
  hearing-aid output classes. A connected BLE headset should no longer be
  misread as "Bluetooth exists but no voice route".
- Native AudioRecord -> Unity PCM callback failures are now explicit. Java no
  longer swallows `onPcmFrame(...)` exceptions; it emits
  `pcm_callback_failed:*` so the HUD can distinguish JNI/proxy failure from
  AudioRecord init failure, silence, or Brain/STT consumption failure.
- Because the pinned LiveKit Unity package does not honor `stopOnUnpublish`
  inside `LocalParticipant.UnpublishTrack`, the product App now treats local
  source cleanup as its own responsibility. Every retry/republish path detaches,
  stops, and disposes the current source before clearing `_audioTrack`.

Validation remains code-level only until a phone run shows uplink frames and
speech-responsive peak. Do not mark Bluetooth/phone mic production-stable from
these static checks alone.

## 2026-05-17 Output-only Bluetooth Correction

Follow-up issue: normal phone behavior is not "Bluetooth or force speaker".
Many Android devices expose Bluetooth A2DP/BLE output even when no
bidirectional communication mic is selectable. For the App this means:

- if a true communication headset is available (`TYPE_BLUETOOTH_SCO` or
  `TYPE_BLE_HEADSET`), prefer it for both input and output;
- if only output Bluetooth is available (`TYPE_BLUETOOTH_A2DP`,
  `TYPE_BLE_SPEAKER`, hearing-aid style output), preserve that output and use
  the system/default or phone mic for input fallback;
- do not force `phone_mic` automatically, because it can pull downlink audio
  back to speaker/earpiece. Keep that for a future explicit/manual recovery
  action if `system_default` cannot capture.

Implementation update:

- `AndroidAudioRouteManager.chooseCommunicationDevice()` now returns no
  explicit target when output-only Bluetooth is present and no communication
  headset target exists. That leaves Android's system output route intact
  instead of stealing Parrot audio back to phone speaker.
- `MicrophonePublisher` fallback attempts now carry an explicit route override:
  system-default for automatic A2DP-preserving capture retries. PhoneMic is not
  in the automatic ladder.

This is still not a production pass until iQOO screenshots/logs prove non-zero
uplink frames and the desired headset/phone-mic fallback behavior.

Threading note:

- Android `AudioRecord` fallback frames enter Unity through an
  `AndroidJavaProxy` callback on a Java capture thread. The LiveKit Unity
  source path already permits off-main-thread audio reads, but App-owned
  diagnostics on that path must stay pure C# and avoid UnityEngine APIs. The
  formal code now avoids `Mathf.*` in the native PCM callback and peak meter.

## 2026-05-17 Route Truth-source Correction

Follow-up audit after iQOO Bluetooth/phone-mic failures tightened the route
rules:

- `AudioManager.getDevices(...)` is an availability/diagnostic list. It must not
  be used to decide that Bluetooth SCO is the active capture path.
- `AudioManager.getCommunicationDevice()` is the active communication-device
  truth source on API 31+; only that route can promote the mic policy to
  `bluetooth_sco`.
- Java `requires_mic_republish` is a snapshot hint, not a direct rebuild
  command. Unity rebuilds only when the accepted capture class or sample rate
  changes.
- Temporary phone/default-mic recovery must be sticky. Topology callbacks can
  arrive while Android is settling the route; restoring Auto/Bluetooth on those
  callbacks can recreate the exact SCO retry loop the fallback was trying to
  escape.
- Output-only Bluetooth must clear any previously selected speaker/earpiece
  communication device before returning no explicit target. Otherwise the App
  can remain pinned to phone speaker after A2DP connects.

These are formal App rules, not smoke-test rules. They apply to
`Assets/ParrotApp/Runtime/Scripts/LiveKit/**` and
`Assets/Plugins/Android/ParrotAudioRoute.androidlib/**`; old ParrotDev/Smoke
scripts remain connectivity references only.

## 2026-05-17 SCO Settling / Bridge Failure Diagnostics

Follow-up implementation after the route-loop audit:

- SCO is still a valid bidirectional Bluetooth microphone route only when
  Android's active communication device confirms it. However, even a confirmed
  SCO route can need a short async settle period before Unity/LiveKit capture
  produces frames. `MicrophonePublisher` now waits briefly before the first SCO
  probe, then uses a short SCO-specific startup timeout. If the route produces
  no `AudioRead` frames quickly, it falls through to the system/default or
  phone-mic recovery ladder instead of delaying the session through multiple
  full 4-second microphone timeouts.
- Native Android PCM fallback failures are now classified. If
  `AndroidPcmMicrophoneSource` cannot instantiate
  `com.parrotcarriers.audio.AndroidPcmMicCapture`, the surfaced marker is
  `android_pcm_bridge_unavailable:*`. If Java starts but the PCM proxy fails,
  Java already emits `pcm_callback_failed:*`. This keeps APK packaging, JNI
  callback, native AudioRecord init, and Brain/STT consumption as separate
  diagnosis buckets.

Validation remains static/code-level until the rebuilt iQOO App proves non-zero
HUD `frames/ch/readSr/peak`. Do not mark APP-015.23 or APP-024 stable from the
successful static guard alone.

## 2026-05-17 AudioRecord Source / Bluetooth Downlink Correction

Follow-up phone evidence showed a narrower failure: the App could play the
placement greeting, but user speech still did not drive further dialogue. That
means Mint, LiveKit room join, Brain presence, and downlink audio are alive; the
remaining blocker is local uplink capture or LiveKit frame delivery.

Implementation correction:

- `AndroidPcmMicCapture` now tries `MediaRecorder.AudioSource.MIC` before
  `VOICE_COMMUNICATION`. The AudioRecord bridge is a last-resort phone-mic
  fallback after Unity's `MicrophoneSource` has produced no LiveKit
  `AudioRead` frames. On some devices a `VOICE_COMMUNICATION` recorder can
  initialize while the communication stack gates or silences near-end capture,
  so the plain MIC source is the safer product fallback.
- Native AudioRecord state now includes `source_name` so the HUD/debug stream can
  show whether the fallback is actually using `mic` or
  `voice_communication`.
- `AndroidPcmMicrophoneSource.Start()` marks the C# source as started before
  crossing into Java `start(...)`, then rolls it back on exception. This avoids
  dropping the first PCM callbacks on fast devices while preserving retry
  cleanup if the bridge or native recorder fails.
- Automatic AudioRecord retries now keep the route override at
  `system_default` for all retry rates. Forcing `phone_mic` can pin Parrot
  downlink back to the phone speaker; keep that for future explicit/manual
  recovery. The desired automatic behavior is Bluetooth/A2DP downlink retained
  by Android, with the Java bridge capturing the plain phone MIC source.

Phone gate remains open: the next iQOO run must prove non-zero HUD
`frames/ch/readSr/peak` and audible user speech reaching LineA/LineB. If frames
increase but Brain still does not respond, the next bucket is remote
track/STT/Brain consumption rather than Android route selection.

## 2026-05-17 Fake-Silence Uplink Guard

Additional review of the "greeting only" symptom found one more false-success
class: Unity can emit regular `AudioRead` callbacks while the sample peak stays
at digital zero. That would make the local source look alive while Brain only
receives silence.

Implementation correction:

- `MicrophonePublisher` now records the age since source start or the latest
  non-zero peak. If the active source is still `unity_microphone`, frames are
  fresh, and peak remains under the zero threshold for the watchdog window, the
  App marks the uplink degraded with
  `uplink_watchdog_zero_peak_unity_microphone`.
- That recovery sets a one-shot flag so the next publish skips the same Unity
  path and starts with Android `AudioRecord` attempts at 48 kHz, 44.1 kHz, then
  16 kHz. It is still a local mic-track rebuild only: no LiveKit reconnect, no
  token mint, and no Brain job churn.
- HUD adds `nz=` next to `frames/ch/readSr/peak` so the next iQOO run can tell
  whether the source is producing real non-zero samples or only fresh silence.
- Native AudioRecord state JSON now quotes `source_name` correctly before
  `recording`, so `nsrc=mic` / `nsrc=voice_communication` diagnostics are not
  lost.
