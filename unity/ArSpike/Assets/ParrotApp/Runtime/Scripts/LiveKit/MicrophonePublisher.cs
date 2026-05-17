using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading;
using LiveKit;
using LiveKit.Proto;
using ParrotApp.Health;
using ParrotApp.Lifecycle;
using UnityEngine;

namespace ParrotApp.LiveKit
{
    /// <summary>
    /// Encodes the local microphone as a LiveKit local audio track.<br/>
    /// Migrated from ParrotDev for Sprint4 Phase 3 / L3 Group 3, then extended
    /// with Bluetooth route handling and sample-rate adaptation.
    /// <list type="bullet">
    /// <item>Namespace is narrowed to <c>ParrotApp.LiveKit</c>.</item>
    /// <item>Implements <see cref="IGracefulShutdownParticipant"/> so
    ///   <c>LifecycleShutdownService</c> can wait for audio unpublish during
    ///   chokepoint step 1.</item>
    /// <item><see cref="ConnectionHealthAggregator"/> ownership: this class is the
    ///   <c>audio_publish_attempted</c> / <c>audio_published</c> / <c>audio_last_error</c>
    ///   sole producer per IMPL_REF.md §4.2. The Bluetooth patch does not add a
    ///   second producer.</item>
    /// </list>
    ///
    /// <b>Bluetooth audio compatibility (late Sprint4 Phase 3)</b>:
    /// <list type="number">
    /// <item>The sample rate is no longer hard-coded to 48k. It comes from
    ///   <see cref="AudioRoutePolicy.PreferredSampleRate"/> via
    ///   <see cref="AudioRouteManager"/>: speaker/wired/A2DP use 48k,
    ///   bluetooth_sco uses 16k, and unknown falls back to 48k.</item>
    /// <item>Device selection prefers a <see cref="UnityEngine.Microphone"/> whose
    ///   name contains <c>bluetooth</c>, <c>airpods</c>, or <c>sco</c> only when
    ///   the detector reports a SCO input route. A2DP stays output-only and uses
    ///   Android's default microphone input. <see cref="preferredDevice"/> can
    ///   still override this from Inspector or the Settings page.</item>
    /// <item><see cref="AudioRouteManager"/> owns accepted route snapshots.
    ///   On changes, this class unpublishes and republishes so the LiveKit native
    ///   source is rebuilt with the new sample rate. <see cref="AudioRouteDetector"/>
    ///   remains a fallback/diagnostic provider.</item>
    /// <item>The route-change reason is reported through <c>audio_last_error</c> as
    ///   <c>route_changed_&lt;old&gt;_to_&lt;new&gt;</c>. A successful republish clears
    ///   it to mean the current route is healthy.</item>
    /// </list>
    ///
    /// <b>Manual device preference (formal App V1)</b>:
    /// <list type="bullet">
    /// <item>The Settings page may call <see cref="CyclePreferredDevice"/> or
    ///   <see cref="ClearPreferredDevice"/>. The preference is local to Unity
    ///   and only changes the <see cref="UnityEngine.Microphone"/> device name
    ///   used for the next LiveKit source rebuild.</item>
    /// <item>Route policy comes from <see cref="AudioRouteManager"/>.
    ///   A2DP remains output-only; selecting a named mic does not magically
    ///   make A2DP a Bluetooth microphone route.</item>
    /// </list>
    ///
    /// <b>Out of scope for Sprint4 Phase 3</b>:
    /// <list type="bullet">
    /// <item>Native OS audio-session routing, manual push-to-talk, and speaker echo policy.</item>
    /// <item>This class still does not write Brain policy directly.
    ///   <see cref="AudioRoutePolicyBrainReporter"/> owns the compact
    ///   LiveKit RPC that mirrors the current route to Brain.</item>
    /// <item>Room reconnect, token mint, and Brain job dispatch. Runtime uplink
    ///   recovery only rebuilds the local microphone track.</item>
    /// <item>iOS native <c>AVAudioSession</c> bridge; detector uses device-name fallback.</item>
    /// </list>
    /// // AudioRoutePolicy producer hook reserved for Sprint4 Phase 4
    /// </summary>
    public class MicrophonePublisher : MonoBehaviour, IGracefulShutdownParticipant
    {
        [Tooltip("Empty = select from the current route; non-empty forces this microphone device name.")]
        [SerializeField] private string preferredDevice = "";

        [Tooltip("Inspector fallback used when AudioRouteDetector has no policy yet, for example the first Editor frame.")]
        [SerializeField] private int fallbackSampleRate = 48000;

        [Tooltip("Optional; resolved through GetComponentInParent / FindObjectOfType when empty.")]
        [SerializeField] private AppLifecycleManager lifecycleManager;

        [Tooltip("Optional; resolved through FindObjectOfType or added to this GameObject when empty.")]
        [SerializeField] private AudioRouteDetector routeDetector;

        [Tooltip("Formal App route facade. Android native routing is preferred; AudioRouteDetector remains fallback.")]
        [SerializeField] private AudioRouteManager routeManager;

        [Tooltip("Small debounce to coalesce Bluetooth/SCO route-change bursts before rebuilding the LiveKit audio source.")]
        [SerializeField] private float routeRepublishDebounceSeconds = 0.5f;

        [Header("Session Policy")]
        [Tooltip("False = keep the LiveKit room alive but do not publish microphone audio.")]
        [SerializeField] private bool publishIntentEnabled = true;

        [Tooltip("Android route bridge fallback: when native routing says a mic is granted but Unity reports zero Microphone.devices, pass null to Microphone.Start so Android uses the current default communication input.")]
        [SerializeField] private bool allowAndroidDefaultMicrophoneWhenDeviceListEmpty = true;

        [Tooltip("Android native fallback: if Unity MicrophoneSource publishes but never produces AudioRead frames, retry with the formal AudioRecord-backed source before marking uplink failed.")]
        [SerializeField] private bool allowAndroidAudioRecordAfterUnityTimeout = true;

        [Tooltip("Guard against fake uplink success: after LiveKit PublishTrack succeeds, wait for microphone progress or native Android AudioRecord readiness plus LiveKit audio frames before reporting audio_published=true.")]
        [SerializeField] private float microphoneStartTimeoutSeconds = 4f;

        [Tooltip("When Android reports a SCO route, wait briefly before probing Unity Microphone so the async Bluetooth voice path can settle.")]
        [SerializeField] private float bluetoothScoRouteSettleSeconds = 0.75f;

        [Tooltip("SCO probes must fail fast. If no frames arrive quickly, fall back to system/default phone mic instead of spending several full startup timeouts on a dead headset path.")]
        [SerializeField] private float bluetoothScoStartTimeoutSeconds = 2f;

        [Header("Uplink Watchdog")]
        [Tooltip("After startup capture succeeds, keep checking that microphone recording and LiveKit AudioRead frames remain alive.")]
        [SerializeField] private bool uplinkRuntimeWatchdogEnabled = true;

        [Tooltip("How often the runtime uplink watchdog checks the active microphone source.")]
        [SerializeField] private float uplinkWatchdogIntervalSeconds = 1f;

        [Tooltip("If no LiveKit audio-source frame arrives for this long, republish the local mic track.")]
        [SerializeField] private float uplinkWatchdogStaleSeconds = 2.5f;

        [Tooltip("If Unity MicrophoneSource emits fresh but all-zero frames for this long, treat it as a fake uplink and rebuild with Android AudioRecord.")]
        [SerializeField] private float uplinkWatchdogZeroPeakSeconds = 4f;

        [Tooltip("Peak below this value counts as digital silence for the fake-uplink guard. Real phone mics normally report non-zero room noise.")]
        [SerializeField] private float uplinkWatchdogZeroPeakThreshold = 0.0001f;

        [Tooltip("Small Android route-settle wait before the phone mic fallback starts after SCO capture produced no frames.")]
        [SerializeField] private float phoneMicFallbackRouteSettleSeconds = 0.25f;

        private RtcAudioSource _micSource;
        private LocalAudioTrack _audioTrack;
        private bool _isPublishing;
        private bool _publishInProgress;
        private bool _publishAttempted;
        private bool _shutdownInitiated;
        private string _selectedDevice = "";
        private string _lastError = "";
        private int _configuredSampleRate;
        private int _unityOutputSampleRate;
        private AudioRoutePolicy _activePolicy = AudioRoutePolicy.Default();
        private uint _routeVersion;
        private uint _publishedRouteVersion;
        private Coroutine _routeRepublishCoroutine;
        private string _pendingRouteRepublishReason = "";
        private string _lastPublishStage = "idle";
        private int _audioReadFrameCount;
        private int _lastAudioReadSampleRate;
        private int _lastAudioReadChannels;
        private float _lastAudioReadPeak;
        private long _lastAudioReadUtcTicks;
        private long _lastNonSilentAudioUtcTicks;
        private Coroutine _uplinkWatchdogCoroutine;
        private string _uplinkWatchdogState = "idle";
        private string _uplinkWatchdogLastRecoveryReason = "";
        private bool _uplinkWatchdogMicrophoneRecording;
        private int _uplinkWatchdogRecoveryCount;
        private string _lastCaptureFallbackStatus = "";
        private string _activeAudioSourceKind = "none";
        private string _lastNativeAudioRecordState = "";
        private string _lastNativeAudioRecordError = "";
        private string _lastNativeAudioRecordSource = "";
        private bool _forceAndroidAudioRecordNextPublish;
        private float _suppressRouteRepublishUntil;

        private sealed class CaptureAttemptSpec
        {
            public readonly string DeviceName;
            public readonly string DeviceLabel;
            public readonly AudioRoutePolicy Policy;
            public readonly string Reason;
            public readonly bool ForceAndroidAudioRecord;
            public readonly bool HasRouteOverride;
            public readonly AudioRoutePreference RouteOverridePreference;
            public readonly float StartupTimeoutSeconds;
            public readonly float PreStartDelaySeconds;

            public CaptureAttemptSpec(
                string deviceName,
                string deviceLabel,
                AudioRoutePolicy policy,
                string reason,
                bool forceAndroidAudioRecord = false,
                bool hasRouteOverride = false,
                AudioRoutePreference routeOverridePreference = AudioRoutePreference.SystemDefault,
                float startupTimeoutSeconds = 0f,
                float preStartDelaySeconds = 0f)
            {
                DeviceName = deviceName;
                DeviceLabel = string.IsNullOrWhiteSpace(deviceLabel) ? "android_default_microphone" : deviceLabel;
                Policy = policy;
                Reason = string.IsNullOrWhiteSpace(reason) ? "primary" : reason;
                ForceAndroidAudioRecord = forceAndroidAudioRecord;
                HasRouteOverride = hasRouteOverride;
                RouteOverridePreference = routeOverridePreference;
                StartupTimeoutSeconds = startupTimeoutSeconds;
                PreStartDelaySeconds = preStartDelaySeconds;
            }
        }

        private sealed class CaptureAttemptResult
        {
            public bool Success;
            public string Error = "";
        }

        private ConnectionHealthAggregator HealthAggregator =>
            lifecycleManager != null ? lifecycleManager.HealthAggregator : null;

        public bool IsPublishing => _isPublishing;
        public bool PublishInProgress => _publishInProgress;
        public bool PublishAttempted => _publishAttempted;
        public string SelectedDevice => _selectedDevice;
        public string LastError => _lastError;
        public string LastPublishStage => _lastPublishStage;
        public int ConfiguredSampleRate => _configuredSampleRate;
        public int UnityOutputSampleRate => _unityOutputSampleRate;
        public AudioRoutePolicy ActivePolicy => _activePolicy;
        public AudioRouteManager RouteManager => routeManager;
        public bool PublishIntentEnabled => publishIntentEnabled;
        public string PreferredDevice => preferredDevice ?? "";
        public string LastManualDeviceStatus { get; private set; } = "auto";
        public int AvailableDeviceCount => Microphone.devices != null ? Microphone.devices.Length : 0;
        public uint RouteVersion => _routeVersion;
        public uint PublishedRouteVersion => _publishedRouteVersion;
        public int AudioReadFrameCount => Volatile.Read(ref _audioReadFrameCount);
        public int LastAudioReadSampleRate => Volatile.Read(ref _lastAudioReadSampleRate);
        public int LastAudioReadChannels => Volatile.Read(ref _lastAudioReadChannels);
        public float LastAudioReadPeak => _lastAudioReadPeak;
        public float LastAudioReadAgeSeconds => AgeSecondsSinceTicks(Interlocked.Read(ref _lastAudioReadUtcTicks));
        public float LastNonSilentAudioAgeSeconds => AgeSecondsSinceTicks(Interlocked.Read(ref _lastNonSilentAudioUtcTicks));
        public string UplinkWatchdogState => _uplinkWatchdogState;
        public string UplinkWatchdogLastRecoveryReason => _uplinkWatchdogLastRecoveryReason;
        public bool UplinkWatchdogMicrophoneRecording => _uplinkWatchdogMicrophoneRecording;
        public int UplinkWatchdogRecoveryCount => _uplinkWatchdogRecoveryCount;
        public string LastCaptureFallbackStatus => _lastCaptureFallbackStatus;
        public string ActiveAudioSourceKind => _activeAudioSourceKind;
        public string NativeAudioRecordState
        {
            get
            {
#if UNITY_ANDROID && !UNITY_EDITOR
                if (_micSource is AndroidPcmMicrophoneSource nativePcmSource)
                {
                    _lastNativeAudioRecordState = nativePcmSource.LastNativeState;
                    return nativePcmSource.LastNativeState;
                }
#endif
                return _lastNativeAudioRecordState;
            }
        }

        public string NativeAudioRecordError
        {
            get
            {
#if UNITY_ANDROID && !UNITY_EDITOR
                if (_micSource is AndroidPcmMicrophoneSource nativePcmSource)
                {
                    _lastNativeAudioRecordError = nativePcmSource.LastNativeError;
                    return nativePcmSource.LastNativeError;
                }
#endif
                return _lastNativeAudioRecordError;
            }
        }
        public string NativeAudioRecordSource
        {
            get
            {
#if UNITY_ANDROID && !UNITY_EDITOR
                if (_micSource is AndroidPcmMicrophoneSource nativePcmSource)
                {
                    _lastNativeAudioRecordSource = nativePcmSource.LastNativeSourceName;
                    return nativePcmSource.LastNativeSourceName;
                }
#endif
                return _lastNativeAudioRecordSource;
            }
        }
        public string UplinkDeviceLabel => string.IsNullOrWhiteSpace(_selectedDevice) ? "none" : _selectedDevice;
        public string UplinkStateLabel
        {
            get
            {
                if (_isPublishing) return "published";
                if (_publishInProgress) return "publishing";
                return _publishAttempted ? "not_published" : "idle";
            }
        }

        // IGracefulShutdownParticipant.

        public int ShutdownOrder => 20; // Video first (10), audio next (20), generic participants later (100).

        public IEnumerator UnpublishAndStop(string reason)
        {
            _shutdownInitiated = true; // Prevent later route changes from triggering republish.

            if (_audioTrack != null)
            {
                var room = RoomManager.Instance?.Room;
                if (room != null)
                {
                    if (LifecycleShutdownService.IsSynchronousQuitDrain)
                    {
                        Debug.Log($"[MicrophonePublisher] sync quit drain skips waiting for UnpublishTrack (reason={reason})");
                    }
                    else
                    {
                        Debug.Log($"[MicrophonePublisher] chokepoint UnpublishTrack (reason={reason})");
                        yield return room.LocalParticipant.UnpublishTrack(_audioTrack, stopOnUnpublish: true);
                    }
                }
            }
            StopPublishing($"chokepoint:{reason}");
        }

        // Lifecycle.

        void Start()
        {
            if (lifecycleManager == null)
                lifecycleManager = FindObjectOfType<AppLifecycleManager>();
            if (lifecycleManager != null)
                lifecycleManager.OnStateChanged += OnLifecycleStateChanged;

            if (routeManager == null)
                routeManager = FindObjectOfType<AudioRouteManager>();
            if (routeManager == null)
            {
                routeManager = gameObject.AddComponent<AudioRouteManager>();
                Debug.Log("[MicrophonePublisher] no AudioRouteManager found; auto-added on this GameObject");
            }

            if (routeDetector == null)
                routeDetector = FindObjectOfType<AudioRouteDetector>();
            if (routeDetector == null && routeManager == null)
            {
                routeDetector = gameObject.AddComponent<AudioRouteDetector>();
                Debug.Log("[MicrophonePublisher] no AudioRouteDetector found; auto-added on this GameObject");
            }
            if (routeManager != null)
            {
                routeManager.OnRoutePolicyChanged += OnAudioRouteChanged;
                _activePolicy = routeManager.CurrentPolicy;
            }
            else if (routeDetector != null)
            {
                routeDetector.OnRouteChanged += OnAudioRouteChanged;
                _activePolicy = routeDetector.CurrentPolicy;
            }

            var rm = RoomManager.Instance;
            if (rm == null)
            {
                Debug.LogWarning("[MicrophonePublisher] RoomManager not found");
                return;
            }

            rm.OnConnected += OnRoomConnected;
            rm.OnDisconnected += OnRoomDisconnected;
            if (rm.IsConnected) OnRoomConnected();
        }

        private void OnLifecycleStateChanged(AppLifecycleState oldState, AppLifecycleState newState)
        {
            if (!publishIntentEnabled || _shutdownInitiated) return;
            if (RoomManager.Instance?.IsConnected != true) return;
            if (newState != AppLifecycleState.Connected
                && newState != AppLifecycleState.Running
                && newState != AppLifecycleState.Degraded)
                return;

            // Resume can change Android's communication device without a new
            // plug/unplug callback. Pull a fresh snapshot; normal route-change
            // handling decides whether the LiveKit mic track needs rebuilding.
            if (routeManager != null)
                RefreshActivePolicy(routeManager.RefreshCurrentPolicy("lifecycle_resumed"), "lifecycle_resumed");
            else if (routeDetector != null)
                RefreshActivePolicy(routeDetector.DetectNow(), "lifecycle_resumed");
        }

        private void OnRoomConnected()
        {
            if (!publishIntentEnabled)
            {
                Debug.Log("[MicrophonePublisher] publish intent disabled; room stays connected without mic");
                return;
            }
            if (_isPublishing || _publishInProgress) return;
            // Pull the detector before publishing so the route policy is fresh.
            if (routeManager != null)
            {
                RefreshActivePolicy(routeManager.RefreshCurrentPolicy("room_connected"), "room_connected");
            }
            else if (routeDetector != null) RefreshActivePolicy(routeDetector.DetectNow(), "room_connected");
            StartCoroutine(RequestAndPublish(initialReason: null));
        }

        /// <summary>
        /// Session policy gate used by startup/menu flows.
        ///
        /// reason: SessionOnlySilent and VoiceVideo capability modes need to
        /// keep the LiveKit room alive while enabling/disabling local mic
        /// publishing independently from RoomManager disconnect.
        /// </summary>
        public void SetPublishIntent(bool enabled, string reason = "session_policy")
        {
            if (publishIntentEnabled == enabled)
            {
                if (enabled && RoomManager.Instance?.IsConnected == true
                    && !_isPublishing && !_publishInProgress)
                {
                    StartCoroutine(RequestAndPublish(initialReason: $"policy_enabled:{reason}"));
                }
                return;
            }

            publishIntentEnabled = enabled;
            if (!enabled)
            {
                routeManager?.RequestCommunicationMode(false);
                if (_publishInProgress && !_isPublishing && _audioTrack == null && _micSource == null)
                {
                    Debug.Log($"[MicrophonePublisher] publish disable queued while permission/setup is in progress ({reason})");
                    HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), $"policy_disabled:{reason}");
                    return;
                }
                if (_isPublishing || _publishInProgress || _audioTrack != null || _micSource != null)
                    StartCoroutine(UnpublishForPolicy(reason));
                else
                    HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), $"policy_disabled:{reason}");
                return;
            }

            _shutdownInitiated = false;
            if (RoomManager.Instance?.IsConnected == true && !_isPublishing && !_publishInProgress)
            {
                StartCoroutine(RequestAndPublish(initialReason: $"policy_enabled:{reason}"));
            }
        }

        /// <summary>
        /// Main publish coroutine. During republish, <paramref name="initialReason"/>
        /// carries route_changed_* into health.audio_last_error so observers can see
        /// why audio briefly went unhealthy. The success path clears it with an empty
        /// string; cold-start publish passes <c>null</c> to preserve Phase 3 behavior.
        /// </summary>
        private IEnumerator RequestAndPublish(string initialReason)
        {
            if (!publishIntentEnabled)
            {
                Debug.Log("[MicrophonePublisher] RequestAndPublish skipped: publish intent disabled");
                yield break;
            }

            _publishInProgress = true;
            _publishAttempted = true;
            _lastError = initialReason ?? "";
            _lastPublishStage = "permission_request";

            HealthAggregator?.ReportAudioPublishAttempt(UnixSeconds());
            if (initialReason != null)
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), initialReason);

            yield return Application.RequestUserAuthorization(UserAuthorization.Microphone);

            if (!Application.HasUserAuthorization(UserAuthorization.Microphone))
            {
                _lastError = "permission_denied";
                _lastPublishStage = "permission_denied";
                Debug.LogError("[MicrophonePublisher] ERROR permission_denied");
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), _lastError);
                _publishInProgress = false;
                yield break;
            }

            _lastPublishStage = "android_route_permission";
            yield return RequestAndroidBluetoothPermissionIfNeeded();
            if (routeManager != null)
            {
                routeManager.RequestCommunicationMode(true);
                RefreshActivePolicy(routeManager.RefreshCurrentPolicy("publish_permission_granted"), "publish_permission_granted");
            }
            else if (routeDetector != null)
            {
                RefreshActivePolicy(routeDetector.DetectNow(), "publish_permission_granted");
            }

            if (!publishIntentEnabled)
            {
                Debug.Log("[MicrophonePublisher] publish intent disabled after permission gate; aborting");
                _lastPublishStage = "policy_disabled_after_permission";
                _publishInProgress = false;
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), "policy_disabled_after_permission");
                yield break;
            }

            _lastPublishStage = "select_device";
            AudioRoutePolicy publishPolicy = _activePolicy;
            uint publishRouteVersion = _routeVersion;
            bool useAndroidDefaultMicFallback = ShouldUseAndroidDefaultMicrophoneWhenDeviceListEmpty();
            var devices = Microphone.devices;
            if ((devices == null || devices.Length == 0) && !useAndroidDefaultMicFallback)
            {
                _lastError = "no_microphone_devices";
                _lastPublishStage = "no_microphone_devices";
                Debug.LogWarning("[MicrophonePublisher] ERROR no_microphone_devices");
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), _lastError);
                _publishInProgress = false;
                yield break;
            }

            string device = SelectDevice(publishPolicy, useAndroidDefaultMicFallback);
            string deviceLabel = string.IsNullOrEmpty(device) && useAndroidDefaultMicFallback
                ? "android_default_microphone"
                : device;
            var captureAttempts = BuildCaptureAttempts(publishPolicy, device, deviceLabel);
            _selectedDevice = captureAttempts.Length > 0 ? captureAttempts[0].DeviceLabel : (deviceLabel ?? "");
            Debug.Log(
                $"[MicrophonePublisher] Using device: '{_selectedDevice}' for policy={publishPolicy} " +
                $"attempts={captureAttempts.Length}");

            var room = RoomManager.Instance?.Room;
            if (room == null)
            {
                _lastError = "room_missing_after_permission";
                _lastPublishStage = "room_missing_after_permission";
                Debug.LogWarning("[MicrophonePublisher] ERROR room_missing_after_permission");
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), _lastError);
                _publishInProgress = false;
                yield break;
            }

            if (!publishIntentEnabled)
            {
                Debug.Log("[MicrophonePublisher] publish intent disabled before track publish; aborting");
                _lastPublishStage = "policy_disabled_before_publish";
                _publishInProgress = false;
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), "policy_disabled_before_publish");
                yield break;
            }

            string firstFailure = "";
            for (int i = 0; i < captureAttempts.Length; i++)
            {
                var attempt = captureAttempts[i];
                if (i > 0)
                {
                    _lastCaptureFallbackStatus = "retry:" + attempt.Reason;
                    HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), _lastCaptureFallbackStatus);
                    Debug.Log(
                        $"[MicrophonePublisher] capture retry {i + 1}/{captureAttempts.Length}: " +
                        $"{attempt.Reason} policy={attempt.Policy} device='{attempt.DeviceLabel}'");
                }

                var result = new CaptureAttemptResult();
                yield return PublishCaptureAttempt(room, attempt, publishRouteVersion, result);
                if (result.Success)
                    yield break;

                if (string.IsNullOrWhiteSpace(firstFailure))
                    firstFailure = result.Error;
                if (IsCaptureAbortError(result.Error)
                    || !publishIntentEnabled
                    || _shutdownInitiated
                    || RoomManager.Instance?.IsConnected != true)
                {
                    yield break;
                }
            }

            _lastError = string.IsNullOrWhiteSpace(_lastError)
                ? (string.IsNullOrWhiteSpace(firstFailure) ? "capture_attempts_failed" : firstFailure)
                : _lastError;
            _publishInProgress = false;
            HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), _lastError);
        }

        private CaptureAttemptSpec[] BuildCaptureAttempts(
            AudioRoutePolicy publishPolicy,
            string selectedDevice,
            string selectedDeviceLabel)
        {
            if (_forceAndroidAudioRecordNextPublish)
            {
                _forceAndroidAudioRecordNextPublish = false;
#if UNITY_ANDROID && !UNITY_EDITOR
                if (ShouldUseAndroidAudioRecordFallbackSourceNow())
                {
                    var forcedAttempts = new List<CaptureAttemptSpec>();
                    AddAndroidAudioRecordFallbackAttempts(
                        forcedAttempts,
                        "android_audio_record_after_zero_peak",
                        "android_audio_record_44100_after_zero_peak",
                        "android_audio_record_16000_after_zero_peak");
                    return forcedAttempts.ToArray();
                }
#endif
            }

            float scoProbeTimeout = publishPolicy.Kind == AudioRouteKind.BluetoothSco
                ? Mathf.Max(0.5f, bluetoothScoStartTimeoutSeconds)
                : 0f;
            float scoPreStartSettle = publishPolicy.Kind == AudioRouteKind.BluetoothSco
                ? Mathf.Max(0f, bluetoothScoRouteSettleSeconds)
                : 0f;
            var attempts = new List<CaptureAttemptSpec>
            {
                new CaptureAttemptSpec(
                    selectedDevice,
                    selectedDeviceLabel,
                    publishPolicy,
                    "primary",
                    startupTimeoutSeconds: scoProbeTimeout,
                    preStartDelaySeconds: scoPreStartSettle)
            };

            if (publishPolicy.Kind == AudioRouteKind.BluetoothSco
                && publishPolicy.PreferredSampleRate != 48000)
            {
                // Some Android phones expose a SCO communication route while Unity's
                // Microphone stack still produces frames only at the platform default
                // capture rate. Retry the same local device at 48 kHz before falling
                // back to route churn; this preserves the LiveKit room and Brain job.
                attempts.Add(new CaptureAttemptSpec(
                    selectedDevice,
                    selectedDeviceLabel,
                    new AudioRoutePolicy(AudioRouteKind.BluetoothSco, "bluetooth_sco_capture_48k", 48000),
                    "sco_capture_48k_retry",
                    startupTimeoutSeconds: scoProbeTimeout));
            }

            if (publishPolicy.Kind == AudioRouteKind.BluetoothSco)
            {
                // If SCO capture still cannot produce Unity/LiveKit audio frames,
                // keep the session alive and fall back to the phone/default mic
                // for input. This is a local capture fallback only: it must not
                // reconnect the LiveKit room, mint a new token, or dispatch a new
                // Brain job. Android may keep Bluetooth as the output route.
                attempts.Add(new CaptureAttemptSpec(
                    null,
                    "phone_default_microphone",
                    new AudioRoutePolicy(AudioRouteKind.Speaker, "phone_default_mic_after_sco_failure", 48000),
                    "phone_default_mic_after_sco_failure",
                    hasRouteOverride: true,
                    routeOverridePreference: AudioRoutePreference.SystemDefault));
            }

#if UNITY_ANDROID && !UNITY_EDITOR
            if (allowAndroidAudioRecordAfterUnityTimeout)
            {
                // Public LiveKit Unity issue #77 and iQOO phone screenshots both
                // show a failure class where Unity's MicrophoneSource exists and
                // publishes, but never emits AudioRead frames. This final attempt
                // bypasses UnityEngine.Microphone and feeds LiveKit from Android
                // AudioRecord. Keep every automatic AudioRecord retry on
                // system_default so Android may preserve Bluetooth/A2DP output
                // while the Java bridge captures the phone MIC source. Forcing
                // phone_mic is reserved for explicit/manual recovery because it
                // can pin downlink audio back to the phone speaker. Each rate is
                // a separate LiveKit source because
                // the SDK/FFI rejects PCM frames whose sample rate differs from
                // the source created by RtcAudioSource.DefaultMicrophoneSampleRate.
                // It remains a local-track fallback only: no room reconnect,
                // token mint, or Brain dispatch.
                AddAndroidAudioRecordFallbackAttempts(
                    attempts,
                    "android_audio_record_after_unity_timeout",
                    "android_audio_record_44100_after_unity_timeout",
                    "android_audio_record_16000_after_unity_timeout");
            }
#endif

            return attempts.ToArray();
        }

#if UNITY_ANDROID && !UNITY_EDITOR
        private static void AddAndroidAudioRecordFallbackAttempts(
            List<CaptureAttemptSpec> attempts,
            string reason48000,
            string reason44100,
            string reason16000)
        {
            string reason48 = string.IsNullOrWhiteSpace(reason48000)
                ? "android_audio_record"
                : reason48000;
            string reason44 = string.IsNullOrWhiteSpace(reason44100)
                ? reason48 + "_44100"
                : reason44100;
            string reason16 = string.IsNullOrWhiteSpace(reason16000)
                ? reason48 + "_16000"
                : reason16000;
            attempts.Add(new CaptureAttemptSpec(
                null,
                "phone_default_microphone",
                new AudioRoutePolicy(AudioRouteKind.Speaker, reason48, 48000),
                reason48,
                forceAndroidAudioRecord: true,
                hasRouteOverride: true,
                routeOverridePreference: AudioRoutePreference.SystemDefault));
            attempts.Add(new CaptureAttemptSpec(
                null,
                "phone_default_microphone",
                new AudioRoutePolicy(AudioRouteKind.Speaker, reason44, 44100),
                reason44,
                forceAndroidAudioRecord: true,
                hasRouteOverride: true,
                routeOverridePreference: AudioRoutePreference.SystemDefault));
            attempts.Add(new CaptureAttemptSpec(
                null,
                "phone_default_microphone",
                new AudioRoutePolicy(AudioRouteKind.Speaker, reason16, 16000),
                reason16,
                forceAndroidAudioRecord: true,
                hasRouteOverride: true,
                routeOverridePreference: AudioRoutePreference.SystemDefault));
        }
#endif

        private IEnumerator PublishCaptureAttempt(
            Room room,
            CaptureAttemptSpec attempt,
            uint publishRouteVersion,
            CaptureAttemptResult result)
        {
            uint effectivePublishRouteVersion = publishRouteVersion;
            _publishInProgress = true;
            _selectedDevice = attempt.DeviceLabel ?? "";
            if (attempt.HasRouteOverride)
            {
                // Unity 2022.x can report a Bluetooth SCO route while producing
                // zero MicrophoneSource frames on some Android phones. Passing
                // null to MicrophoneSource is not sufficient if Android's route
                // is still pinned to a dead headset profile. Prefer system
                // default for automatic recovery so A2DP/BLE output can stay on
                // the headset while Android AudioRecord captures the plain phone
                // MIC source. Explicit PhoneMic routing is reserved for a future
                // manual recovery control. This remains a local capture fallback
                // only: no room reconnect, no mint token, and no Brain dispatch.
                string overrideLabel = AudioRouteSnapshotDto.PreferenceWireValue(attempt.RouteOverridePreference);
                _lastPublishStage = "capture_route_override";
                _lastCaptureFallbackStatus = "route_override:" + overrideLabel;
                ApplyCaptureRouteOverride(attempt.RouteOverridePreference, attempt.Reason);
                float settle = Mathf.Max(0f, phoneMicFallbackRouteSettleSeconds);
                if (settle > 0f)
                    yield return new WaitForSeconds(settle);
                effectivePublishRouteVersion = _routeVersion;
            }

            if (attempt.PreStartDelaySeconds > 0f)
            {
                _lastPublishStage = "capture_route_settle";
                _lastCaptureFallbackStatus = string.IsNullOrWhiteSpace(_lastCaptureFallbackStatus)
                    ? "settle:" + attempt.Reason
                    : _lastCaptureFallbackStatus + ";settle:" + attempt.Reason;
                yield return new WaitForSeconds(attempt.PreStartDelaySeconds);
            }

            _lastPublishStage = "configure_sample_rate";
            ConfigureLiveKitMicrophoneSampleRate(_selectedDevice, attempt.Policy);

            bool sourceCreateFailed = false;
            bool requiresUnityMicrophonePosition = true;
            string sourceKind = "unity_microphone";
            try
            {
                _micSource = CreateAudioSourceForAttempt(
                    attempt,
                    out requiresUnityMicrophonePosition,
                    out sourceKind);
                _activeAudioSourceKind = sourceKind;
                if (string.Equals(sourceKind, "android_audio_record", StringComparison.Ordinal))
                {
                    _lastNativeAudioRecordState = "created";
                    _lastNativeAudioRecordError = "";
                    _lastNativeAudioRecordSource = "";
                }
                else
                {
                    _lastNativeAudioRecordState = "";
                    _lastNativeAudioRecordError = "";
                    _lastNativeAudioRecordSource = "";
                }
                _micSource.AudioRead += OnMicrophoneAudioRead;
                _audioTrack = LocalAudioTrack.CreateAudioTrack("microphone", _micSource, room);
                if (!string.Equals(sourceKind, "unity_microphone", StringComparison.Ordinal))
                {
                    _lastCaptureFallbackStatus = string.IsNullOrWhiteSpace(_lastCaptureFallbackStatus)
                        ? "source:" + sourceKind
                        : _lastCaptureFallbackStatus + ";source:" + sourceKind;
                }
            }
            catch (Exception e)
            {
                _lastError = "audio_track_create_failed:" + e.GetType().Name;
                _lastPublishStage = "audio_track_create_failed";
                Debug.LogWarning($"[MicrophonePublisher] ERROR {_lastError}: {e.Message}");
                sourceCreateFailed = true;
            }

            if (sourceCreateFailed)
            {
                StopPublishingInner();
                result.Success = false;
                result.Error = _lastError;
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), _lastError);
                yield break;
            }

            var options = new TrackPublishOptions
            {
                Source = TrackSource.SourceMicrophone,
                AudioEncoding = new AudioEncoding { MaxBitrate = 64_000 },
            };

            _lastPublishStage = "publish_track";
            var publish = room.LocalParticipant.PublishTrack(_audioTrack, options);
            yield return publish;

            if (publish.IsError)
            {
                _lastError = "publish_failed";
                _lastPublishStage = "publish_failed";
                Debug.LogError("[MicrophonePublisher] ERROR publish_failed (PublishTrackInstruction.IsError; SDK exposes no Error details)");
                StopPublishingInner();
                result.Success = false;
                result.Error = _lastError;
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), _lastError);
                yield break;
            }

            _lastPublishStage = "microphone_start";
            int audioReadBaseline = AudioReadFrameCount;
            // Start the zero-peak timer from this capture source's start. A
            // real phone mic usually reports non-zero room noise quickly; if
            // Unity only emits digital zeroes beyond the watchdog window, we
            // promote to Android AudioRecord instead of treating the track as
            // a usable uplink.
            Interlocked.Exchange(ref _lastNonSilentAudioUtcTicks, DateTime.UtcNow.Ticks);
            bool microphoneStartException = false;
            try
            {
                _micSource.Start();
            }
            catch (Exception e)
            {
                CacheNativeAudioRecordDiagnostics();
                _lastError = "microphone_start_exception:" + e.GetType().Name;
                if (!string.IsNullOrWhiteSpace(_lastNativeAudioRecordError))
                    _lastError += ":" + _lastNativeAudioRecordError;
                _lastPublishStage = "microphone_start_exception";
                Debug.LogWarning($"[MicrophonePublisher] ERROR {_lastError}: {e.Message}");
                microphoneStartException = true;
            }

            if (microphoneStartException)
            {
                if (_audioTrack != null)
                    yield return room.LocalParticipant.UnpublishTrack(_audioTrack, stopOnUnpublish: true);
                StopPublishingInner();
                result.Success = false;
                result.Error = _lastError;
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), _lastError);
                yield break;
            }

            string probeDevice = string.IsNullOrEmpty(attempt.DeviceName) ? null : attempt.DeviceName;
            float elapsed = 0f;
            bool microphonePositionReady = !requiresUnityMicrophonePosition;
            bool audioReadReady = false;
            string probeError = requiresUnityMicrophonePosition ? "" : "android_audio_record";
            float timeout = Mathf.Max(
                0.1f,
                attempt.StartupTimeoutSeconds > 0f
                    ? attempt.StartupTimeoutSeconds
                    : microphoneStartTimeoutSeconds);
            while (elapsed < timeout)
            {
                if (!publishIntentEnabled || _shutdownInitiated || RoomManager.Instance?.IsConnected != true)
                {
                    _lastError = !publishIntentEnabled
                        ? "microphone_start_aborted:publish_intent_disabled"
                        : (_shutdownInitiated
                            ? "microphone_start_aborted:shutdown"
                            : "microphone_start_aborted:room_disconnected");
                    _lastPublishStage = "microphone_start_aborted";
                    break;
                }
                if (requiresUnityMicrophonePosition
                    && TryGetMicrophonePosition(probeDevice, out int position, out probeError)
                    && position > 0)
                {
                    microphonePositionReady = true;
                }
                if (AudioReadFrameCount > audioReadBaseline)
                    audioReadReady = true;
                if (microphonePositionReady && audioReadReady)
                    break;

                yield return new WaitForSeconds(0.05f);
                elapsed += 0.05f;
            }

            if (!microphonePositionReady || !audioReadReady)
            {
                if (string.IsNullOrWhiteSpace(_lastError) || !_lastError.StartsWith("microphone_start_aborted", StringComparison.Ordinal))
                {
                    if (!microphonePositionReady)
                    {
                        _lastError = string.IsNullOrWhiteSpace(probeError)
                            ? "microphone_start_timeout"
                            : "microphone_start_timeout:" + probeError;
                        _lastPublishStage = "microphone_start_timeout";
                    }
                    else
                    {
                        _lastError = "audio_read_timeout";
                        _lastPublishStage = "audio_read_timeout";
                    }
                }
                Debug.LogWarning(
                    $"[MicrophonePublisher] ERROR {_lastError} device='{_selectedDevice}' " +
                    $"route={attempt.Policy.RouteName} timeout={timeout:0.0}s " +
                    $"micPositionReady={microphonePositionReady} audioReadReady={audioReadReady} " +
                    $"frames={AudioReadFrameCount - audioReadBaseline}");
                if (_audioTrack != null)
                    yield return room.LocalParticipant.UnpublishTrack(_audioTrack, stopOnUnpublish: true);
                StopPublishingInner();
                result.Success = false;
                result.Error = _lastError;
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), _lastError);
                yield break;
            }

            if (!publishIntentEnabled || _shutdownInitiated || RoomManager.Instance?.IsConnected != true)
            {
                _lastError = !publishIntentEnabled
                    ? "microphone_ready_aborted:publish_intent_disabled"
                    : (_shutdownInitiated
                        ? "microphone_ready_aborted:shutdown"
                        : "microphone_ready_aborted:room_disconnected");
                _lastPublishStage = "microphone_ready_aborted";
                Debug.LogWarning($"[MicrophonePublisher] ERROR {_lastError} after capture became ready");
                if (_audioTrack != null)
                    yield return room.LocalParticipant.UnpublishTrack(_audioTrack, stopOnUnpublish: true);
                StopPublishingInner();
                result.Success = false;
                result.Error = _lastError;
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), _lastError);
                yield break;
            }

            _isPublishing = true;
            _publishInProgress = false;
            _publishedRouteVersion = effectivePublishRouteVersion;
            _lastError = "";
            _lastPublishStage = "published";
            _lastCaptureFallbackStatus = BuildSuccessFallbackStatus(attempt, sourceKind);
            HealthAggregator?.ReportAudioPublished(true, UnixSeconds(), "");
            StartUplinkWatchdog("published");
            Debug.Log(
                $"[MicrophonePublisher] publishing started: device='{_selectedDevice}' route={attempt.Policy.RouteName} " +
                $"configuredSampleRate={_configuredSampleRate} unityOutputSampleRate={_unityOutputSampleRate} " +
                $"audioReadFrames={AudioReadFrameCount} fallback='{_lastCaptureFallbackStatus}'");

            if (effectivePublishRouteVersion != _routeVersion && publishIntentEnabled && !_shutdownInitiated)
            {
                if (RequiresMicRebuild(attempt.Policy, _activePolicy))
                {
                    QueueRouteRepublish(
                        _activePolicy,
                        $"route_changed_during_publish_to_{_activePolicy.RouteName}");
                }
                else
                {
                    Debug.Log(
                        $"[MicrophonePublisher] route version changed during publish without mic rebuild: " +
                        $"{attempt.Policy} -> {_activePolicy}");
                }
            }

            result.Success = true;
            result.Error = "";
        }

        private static bool IsCaptureAbortError(string error)
        {
            return !string.IsNullOrWhiteSpace(error)
                   && (error.StartsWith("microphone_start_aborted", StringComparison.Ordinal)
                       || error.StartsWith("microphone_ready_aborted", StringComparison.Ordinal)
                       || error.StartsWith("permission_", StringComparison.Ordinal)
                       || error.StartsWith("policy_disabled", StringComparison.Ordinal)
                       || error.StartsWith("room_missing", StringComparison.Ordinal));
        }

        private static string BuildSuccessFallbackStatus(CaptureAttemptSpec attempt, string sourceKind)
        {
            string status = attempt != null && attempt.Reason == "primary"
                ? ""
                : "active:" + (attempt?.Reason ?? "unknown");
            if (!string.Equals(sourceKind, "unity_microphone", StringComparison.Ordinal))
            {
                status = string.IsNullOrWhiteSpace(status)
                    ? "source:" + sourceKind
                    : status + ";source:" + sourceKind;
            }
            return status;
        }

        private RtcAudioSource CreateAudioSourceForAttempt(
            CaptureAttemptSpec attempt,
            out bool requiresUnityMicrophonePosition,
            out string sourceKind)
        {
            requiresUnityMicrophonePosition = true;
            sourceKind = "unity_microphone";

#if UNITY_ANDROID && !UNITY_EDITOR
            if (ShouldUseAndroidAudioRecordFallbackSource(attempt))
            {
                // Unity's mobile Microphone API can report an empty device list
                // while Android AudioRecord still captures the active
                // communication input. Use a native PCM source for that case so
                // LiveKit receives real frames instead of a fake published track.
                requiresUnityMicrophonePosition = false;
                sourceKind = "android_audio_record";
                return new AndroidPcmMicrophoneSource(_configuredSampleRate, 1, attempt?.DeviceLabel);
            }
#endif

            return new MicrophoneSource(
                string.IsNullOrEmpty(attempt?.DeviceName) ? null : attempt.DeviceName,
                gameObject);
        }

        /// <summary>
        /// Sets the sample rate expected by the LiveKit native source.
        ///
        /// <b>Source of truth</b>: livekit-unity-sdk.mdc recommends not deriving
        /// Android microphone sample rate from unstable route output state.
        /// Sprint3 brain_connected_black_video confirmed:
        /// <list type="bullet">
        /// <item>Do not use <c>AudioSettings.outputSampleRate</c>; it is unreliable
        /// after route changes.</item>
        /// <item>Set <see cref="RtcAudioSource.DefaultMicrophoneSampleRate"/> before
        /// constructing <see cref="MicrophoneSource"/>.</item>
        /// <item>Match the active route to avoid
        /// <c>InvalidState: sample_rate and num_channels don't match</c>.</item>
        /// </list>
        /// </summary>
        private void ConfigureLiveKitMicrophoneSampleRate(string device, AudioRoutePolicy policy)
        {
            _unityOutputSampleRate = AudioSettings.outputSampleRate;
            int targetRate = policy.PreferredSampleRate > 0
                ? policy.PreferredSampleRate
                : (fallbackSampleRate > 0 ? fallbackSampleRate : 48000);

            RtcAudioSource.DefaultMicrophoneSampleRate = (uint)targetRate;
            _configuredSampleRate = targetRate;
            Debug.Log(
                $"[MicrophonePublisher] LiveKit microphone sample rate configured: {targetRate}Hz " +
                $"(route={policy.RouteName}, Unity output={_unityOutputSampleRate}Hz, device='{device}')");
        }

        /// <summary>
        /// Enumerates and selects the microphone device. Priority:
        /// <see cref="preferredDevice"/> &gt; Bluetooth route match &gt;
        /// Microphone.devices[0] system default.
        ///
        /// <b>Bluetooth rule</b>: only a SCO policy scans
        /// <c>Microphone.devices</c> for bluetooth/airpods/sco/headset names. A2DP
        /// is output-only and keeps Android's default microphone device at the
        /// normal 48k policy.
        /// </summary>
        private string SelectDevice(AudioRoutePolicy policy, bool allowDefaultWhenEmpty)
        {
            var devices = Microphone.devices;
            if (devices == null || devices.Length == 0)
                return allowDefaultWhenEmpty ? null : "";

            if (!string.IsNullOrEmpty(preferredDevice))
            {
                foreach (var d in devices)
                    if (d == preferredDevice) return d;
                Debug.LogWarning(
                    $"[MicrophonePublisher] preferredDevice '{preferredDevice}' not found; " +
                    $"falling back to route-aware selection");
            }

            // A2DP is output-only. Only SCO should make us prefer a Bluetooth
            // microphone device name; otherwise keep Android's default input.
            if (policy.Kind == AudioRouteKind.BluetoothSco)
            {
                foreach (var d in devices)
                {
                    var lower = d?.ToLowerInvariant() ?? "";
                    if (lower.Contains("bluetooth") || lower.Contains("airpods")
                        || lower.Contains("sco") || lower.Contains("headset"))
                    {
                        return d;
                    }
                }
                Debug.Log(
                    "[MicrophonePublisher] SCO policy active but no BT device name in Microphone.devices; " +
                    "using default[0] (Android usually maps default input to the SCO route)");
            }

            return devices[0];
        }

        private void OnMicrophoneAudioRead(float[] data, int channels, int sampleRate)
        {
            Interlocked.Increment(ref _audioReadFrameCount);
            Volatile.Write(ref _lastAudioReadSampleRate, sampleRate);
            Volatile.Write(ref _lastAudioReadChannels, channels);
            Interlocked.Exchange(ref _lastAudioReadUtcTicks, DateTime.UtcNow.Ticks);

            float peak = 0f;
            if (data != null)
            {
                for (int i = 0; i < data.Length; i++)
                {
                    float abs = data[i] < 0f ? -data[i] : data[i];
                    if (abs > peak) peak = abs;
                }
            }
            _lastAudioReadPeak = peak;
            if (peak > Mathf.Max(0.000001f, uplinkWatchdogZeroPeakThreshold))
                Interlocked.Exchange(ref _lastNonSilentAudioUtcTicks, DateTime.UtcNow.Ticks);
        }

        private void StartUplinkWatchdog(string reason)
        {
            if (!uplinkRuntimeWatchdogEnabled)
            {
                _uplinkWatchdogState = "disabled";
                return;
            }

            _uplinkWatchdogState = string.IsNullOrWhiteSpace(reason) ? "healthy" : "healthy:" + reason;
            _uplinkWatchdogLastRecoveryReason = "";
            _uplinkWatchdogMicrophoneRecording = true;
            if (_uplinkWatchdogCoroutine == null)
                _uplinkWatchdogCoroutine = StartCoroutine(UplinkRuntimeWatchdogLoop());
        }

        private void StopUplinkWatchdog(string reason)
        {
            if (_uplinkWatchdogCoroutine != null)
            {
                StopCoroutine(_uplinkWatchdogCoroutine);
                _uplinkWatchdogCoroutine = null;
            }
            _uplinkWatchdogMicrophoneRecording = false;
            _uplinkWatchdogState = string.IsNullOrWhiteSpace(reason) ? "idle" : "idle:" + reason;
        }

        private IEnumerator UplinkRuntimeWatchdogLoop()
        {
            float interval = Mathf.Max(0.2f, uplinkWatchdogIntervalSeconds);
            float staleSeconds = Mathf.Max(interval * 1.5f, uplinkWatchdogStaleSeconds);
            var wait = new WaitForSeconds(interval);

            while (true)
            {
                yield return wait;

                if (!_isPublishing || !publishIntentEnabled || _shutdownInitiated
                    || RoomManager.Instance?.IsConnected != true)
                    break;

                if (_publishInProgress)
                {
                    _uplinkWatchdogState = "waiting_publish";
                    continue;
                }

                string probeDevice = ProbeDeviceNameForSelectedDevice();
                bool recordingKnown;
                bool isRecording;
                string recordingError;
#if UNITY_ANDROID && !UNITY_EDITOR
                if (_micSource is AndroidPcmMicrophoneSource nativePcmSource)
                {
                    CacheNativeAudioRecordDiagnostics(nativePcmSource);
                    recordingKnown = true;
                    isRecording = nativePcmSource.IsNativeRecording;
                    recordingError = nativePcmSource.LastNativeError;
                }
                else
#endif
                {
                    recordingKnown = TryIsMicrophoneRecording(probeDevice, out isRecording, out recordingError);
                }
                _uplinkWatchdogMicrophoneRecording = recordingKnown && isRecording;

                float lastFrameAge = LastAudioReadAgeSeconds;
                // AudioRead freshness is the stronger formal-app signal: quiet rooms still
                // produce captured frames, while Android default inputs can make
                // Microphone.IsRecording(null) noisy or unknown on some devices.
                bool hasRecentFrames = lastFrameAge >= 0f && lastFrameAge <= staleSeconds;
                if (hasRecentFrames)
                {
                    if (ShouldPromoteSilentUnityStreamToAndroidAudioRecord())
                    {
                        string recoveryReason = "uplink_watchdog_zero_peak_unity_microphone";
                        _forceAndroidAudioRecordNextPublish = true;
                        _uplinkWatchdogState = recoveryReason;
                        _uplinkWatchdogLastRecoveryReason = recoveryReason;
                        _uplinkWatchdogRecoveryCount++;
                        _lastError = recoveryReason;
                        _lastPublishStage = "uplink_watchdog_recovering";
                        HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), recoveryReason);
                        Debug.LogWarning(
                            $"[MicrophonePublisher] watchdog promoting silent Unity mic to Android AudioRecord " +
                            $"frames={AudioReadFrameCount} peak={_lastAudioReadPeak:0.000000} " +
                            $"lastNonSilentAge={LastNonSilentAudioAgeSeconds:0.00}s");

                        _uplinkWatchdogCoroutine = null;
                        QueueRouteRepublish(_activePolicy, recoveryReason);
                        yield break;
                    }

                    _uplinkWatchdogState = recordingKnown
                        ? (isRecording ? "healthy" : "healthy_frames_recording_false")
                        : "healthy_frames_recording_unknown";
                    continue;
                }

                string reason = recordingKnown && !isRecording
                    ? "uplink_watchdog_microphone_stopped"
                    : "uplink_watchdog_audio_frames_stale";
                if (!string.IsNullOrWhiteSpace(recordingError))
                    reason += ":" + recordingError;

                _uplinkWatchdogState = reason;
                _uplinkWatchdogLastRecoveryReason = reason;
                _uplinkWatchdogRecoveryCount++;
                _lastError = reason;
                _lastPublishStage = "uplink_watchdog_recovering";
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), reason);
                Debug.LogWarning(
                    $"[MicrophonePublisher] watchdog recovering reason={reason} " +
                    $"device='{_selectedDevice}' lastFrameAge={lastFrameAge:0.00}s " +
                    $"recordingKnown={recordingKnown} isRecording={isRecording}");

                // Headset/route glitches recover by rebuilding only the local mic track;
                // they must not churn the LiveKit room, token mint, or Brain job.
                _uplinkWatchdogCoroutine = null;
                QueueRouteRepublish(_activePolicy, reason);
                yield break;
            }

            _uplinkWatchdogCoroutine = null;
        }

        private bool ShouldUseAndroidDefaultMicrophoneWhenDeviceListEmpty()
        {
            if (!allowAndroidDefaultMicrophoneWhenDeviceListEmpty)
                return false;

            var devices = Microphone.devices;
            if (devices != null && devices.Length > 0)
                return false;

#if UNITY_ANDROID && !UNITY_EDITOR
            if (routeManager == null || !routeManager.NativeAvailable)
                return false;

            bool unityPermissionGranted = Application.HasUserAuthorization(UserAuthorization.Microphone);
            var snapshot = routeManager.CurrentSnapshot;
            if (snapshot == null)
                return unityPermissionGranted;

            bool permissionGranted = string.Equals(
                snapshot.microphone_permission,
                "granted",
                StringComparison.OrdinalIgnoreCase)
                || unityPermissionGranted;
            if (!permissionGranted)
                return false;

            if (string.IsNullOrWhiteSpace(snapshot.input_route)
                || string.Equals(snapshot.input_route, "unknown", StringComparison.OrdinalIgnoreCase))
            {
                // Native route snapshots can briefly be stale or unknown while
                // Android is moving between A2DP/SCO/phone routes. Permission
                // plus a native route bridge is enough to try the default input
                // instead of failing early with no_microphone_devices.
                return true;
            }

            return IsAndroidMicInputRoute(snapshot.input_route);
#else
            return false;
#endif
        }

        private bool ShouldUseAndroidAudioRecordFallbackSource(CaptureAttemptSpec attempt)
        {
            if (attempt == null)
                return false;
            if (attempt.ForceAndroidAudioRecord)
                return ShouldUseAndroidAudioRecordFallbackSourceNow();
            if (!string.IsNullOrEmpty(attempt.DeviceName))
                return false;
            return ShouldUseAndroidDefaultMicrophoneWhenDeviceListEmpty();
        }

        private bool ShouldUseAndroidAudioRecordFallbackSourceNow()
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            if (!allowAndroidAudioRecordAfterUnityTimeout)
                return false;
            if (routeManager == null || !routeManager.NativeAvailable)
                return false;
            if (!Application.HasUserAuthorization(UserAuthorization.Microphone))
                return false;

            var snapshot = routeManager.CurrentSnapshot;
            if (snapshot == null)
                return true;
            bool permissionGranted = string.Equals(
                snapshot.microphone_permission,
                "granted",
                StringComparison.OrdinalIgnoreCase)
                || Application.HasUserAuthorization(UserAuthorization.Microphone);
            if (!permissionGranted)
                return false;

            if (string.IsNullOrWhiteSpace(snapshot.input_route)
                || string.Equals(snapshot.input_route, "unknown", StringComparison.OrdinalIgnoreCase))
            {
                return true;
            }

            return IsAndroidMicInputRoute(snapshot.input_route);
#else
            return false;
#endif
        }

        private bool ShouldPromoteSilentUnityStreamToAndroidAudioRecord()
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            if (!allowAndroidAudioRecordAfterUnityTimeout)
                return false;
            if (!string.Equals(_activeAudioSourceKind, "unity_microphone", StringComparison.Ordinal))
                return false;
            if (AudioReadFrameCount <= 0)
                return false;
            float zeroPeakWindow = Mathf.Max(1f, uplinkWatchdogZeroPeakSeconds);
            float threshold = Mathf.Max(0.000001f, uplinkWatchdogZeroPeakThreshold);
            if (_lastAudioReadPeak > threshold)
                return false;

            float nonSilentAge = LastNonSilentAudioAgeSeconds;
            if (nonSilentAge >= 0f && nonSilentAge < zeroPeakWindow)
                return false;

            float frameAge = LastAudioReadAgeSeconds;
            return frameAge >= 0f && frameAge <= Mathf.Max(0.2f, uplinkWatchdogIntervalSeconds * 1.5f);
#else
            return false;
#endif
        }

        private static bool IsAndroidMicInputRoute(string route)
        {
            return string.Equals(route, "phone_mic", StringComparison.OrdinalIgnoreCase)
                   || string.Equals(route, "system_default_microphone", StringComparison.OrdinalIgnoreCase)
                   || string.Equals(route, "bluetooth_sco", StringComparison.OrdinalIgnoreCase)
                   || string.Equals(route, "wired_headset", StringComparison.OrdinalIgnoreCase);
        }

        private static bool TryGetMicrophonePosition(string deviceName, out int position, out string error)
        {
            position = 0;
            error = "";
            try
            {
                position = Microphone.GetPosition(deviceName);
                return true;
            }
            catch (Exception e)
            {
                error = e.GetType().Name;
                return false;
            }
        }

        private string ProbeDeviceNameForSelectedDevice()
        {
            if (string.IsNullOrWhiteSpace(_selectedDevice))
                return null;
            if (string.Equals(_selectedDevice, "android_default_microphone", StringComparison.OrdinalIgnoreCase))
                return null;
            if (string.Equals(_selectedDevice, "phone_default_microphone", StringComparison.OrdinalIgnoreCase))
                return null;
            return _selectedDevice;
        }

        private void ApplyCaptureRouteOverride(AudioRoutePreference preference, string reason)
        {
            if (routeManager == null)
                return;

            float settle = Mathf.Max(0.25f, phoneMicFallbackRouteSettleSeconds);
            float guard = settle + Mathf.Max(microphoneStartTimeoutSeconds, routeRepublishDebounceSeconds) + 1f;
            _suppressRouteRepublishUntil = Mathf.Max(
                _suppressRouteRepublishUntil,
                Time.unscaledTime + guard);

            try
            {
                routeManager.ApplyTemporaryNativePreference(
                    preference,
                    string.IsNullOrWhiteSpace(reason) ? "capture_route_override" : reason);
                routeManager.RequestCommunicationMode(true);
                RefreshActivePolicy(
                    routeManager.RefreshCurrentPolicy("capture_route_override"),
                    "capture_route_override");
            }
            catch (Exception e)
            {
                _lastCaptureFallbackStatus = "route_override_failed:" + e.GetType().Name;
                Debug.LogWarning("[MicrophonePublisher] capture route override failed: " + e.Message);
            }
        }

        private static bool TryIsMicrophoneRecording(string deviceName, out bool isRecording, out string error)
        {
            isRecording = false;
            error = "";
            try
            {
                isRecording = Microphone.IsRecording(deviceName);
                return true;
            }
            catch (Exception e)
            {
                error = e.GetType().Name;
                return false;
            }
        }

        private void CacheNativeAudioRecordDiagnostics(AndroidPcmMicrophoneSource source = null)
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            var nativePcmSource = source ?? _micSource as AndroidPcmMicrophoneSource;
            if (nativePcmSource == null)
                return;
            _lastNativeAudioRecordState = nativePcmSource.LastNativeState ?? "";
            _lastNativeAudioRecordError = nativePcmSource.LastNativeError ?? "";
            _lastNativeAudioRecordSource = nativePcmSource.LastNativeSourceName ?? "";
#endif
        }

        private static float AgeSecondsSinceTicks(long ticks)
        {
            if (ticks <= 0)
                return -1f;
            double seconds = (DateTime.UtcNow.Ticks - ticks) / (double)TimeSpan.TicksPerSecond;
            if (seconds < 0)
                seconds = 0;
            return (float)seconds;
        }

        public bool CyclePreferredDevice(string reason = "manual_device_cycle")
        {
            var devices = Microphone.devices;
            if (devices == null || devices.Length == 0)
            {
                if (ShouldUseAndroidDefaultMicrophoneWhenDeviceListEmpty())
                {
                    preferredDevice = "";
                    LastManualDeviceStatus = "auto:android_default_microphone";
                    QueueManualDeviceRepublish(reason);
                    return true;
                }
                LastManualDeviceStatus = "no_microphone_devices";
                return false;
            }

            int currentIndex = -1;
            if (!string.IsNullOrEmpty(preferredDevice))
            {
                for (int i = 0; i < devices.Length; i++)
                {
                    if (devices[i] == preferredDevice)
                    {
                        currentIndex = i;
                        break;
                    }
                }
            }
            else if (!string.IsNullOrEmpty(_selectedDevice))
            {
                for (int i = 0; i < devices.Length; i++)
                {
                    if (devices[i] == _selectedDevice)
                    {
                        currentIndex = i;
                        break;
                    }
                }
            }

            if (currentIndex >= 0 && currentIndex >= devices.Length - 1)
            {
                preferredDevice = "";
                LastManualDeviceStatus = "auto";
            }
            else
            {
                preferredDevice = devices[Mathf.Clamp(currentIndex + 1, 0, devices.Length - 1)] ?? "";
                LastManualDeviceStatus = string.IsNullOrEmpty(preferredDevice)
                    ? "auto"
                    : "manual:" + preferredDevice;
            }

            QueueManualDeviceRepublish(reason);
            return true;
        }

        public void ClearPreferredDevice(string reason = "manual_device_auto")
        {
            preferredDevice = "";
            LastManualDeviceStatus = "auto";
            QueueManualDeviceRepublish(reason);
        }

        public string AvailableDevicesLabel(int maxChars = 96)
        {
            var devices = Microphone.devices;
            if (devices == null || devices.Length == 0)
                return ShouldUseAndroidDefaultMicrophoneWhenDeviceListEmpty()
                    ? "android_default_microphone"
                    : "none";
            string joined = string.Join("|", devices);
            if (maxChars > 0 && joined.Length > maxChars)
                joined = joined.Substring(0, maxChars);
            return joined;
        }

        // Route changes.

        private void OnAudioRouteChanged(AudioRoutePolicy oldPolicy, AudioRoutePolicy newPolicy)
        {
            // Cache route state even when not publishing; the next publish uses it.
            RefreshActivePolicy(newPolicy, "route_changed");

            if (!RequiresMicRebuild(oldPolicy, newPolicy))
            {
                Debug.Log($"[MicrophonePublisher] route changed without mic rebuild: {oldPolicy} -> {newPolicy}");
                return;
            }

            if (_publishInProgress && Time.unscaledTime < _suppressRouteRepublishUntil)
            {
                Debug.Log(
                    $"[MicrophonePublisher] route change accepted during capture override without republish: {oldPolicy} -> {newPolicy}");
                return;
            }

            if (!publishIntentEnabled)
            {
                Debug.Log($"[MicrophonePublisher] route cached while publish disabled: {oldPolicy} -> {newPolicy}");
                return;
            }

            if (_shutdownInitiated)
            {
                Debug.Log($"[MicrophonePublisher] route change ignored (shutdown in progress): {oldPolicy} -> {newPolicy}");
                return;
            }

            // Before publish starts, caching is enough.
            if (!_isPublishing && !_publishInProgress)
            {
                Debug.Log($"[MicrophonePublisher] route cached pre-publish: {oldPolicy} -> {newPolicy}");
                return;
            }

            // The current publish coroutine is still running. Queue the route
            // rebuild instead of overlapping UnpublishTrack/PublishTrack calls.
            if (_publishInProgress)
            {
                string pendingReason = $"route_changed_{oldPolicy.RouteName}_to_{newPolicy.RouteName}";
                QueueRouteRepublish(newPolicy, pendingReason);
                Debug.Log($"[MicrophonePublisher] route change queued during publish-in-progress: {oldPolicy} -> {newPolicy}");
                return;
            }

            if (RoomManager.Instance?.Room == null)
            {
                Debug.Log("[MicrophonePublisher] route change but room missing; skip republish");
                return;
            }

            string reason = $"route_changed_{oldPolicy.RouteName}_to_{newPolicy.RouteName}";
            QueueRouteRepublish(newPolicy, reason);
        }

        private void RefreshActivePolicy(AudioRoutePolicy policy, string trigger)
        {
            if (policy.Equals(_activePolicy)) return;
            var oldPolicy = _activePolicy;
            _activePolicy = policy;
            _routeVersion++;
            Debug.Log($"[MicrophonePublisher] active route policy updated via {trigger}: {oldPolicy} -> {policy} (v{_routeVersion})");
        }

        private void QueueRouteRepublish(AudioRoutePolicy policy, string reason)
        {
            _pendingRouteRepublishReason = string.IsNullOrEmpty(reason)
                ? $"route_changed_to_{policy.RouteName}"
                : reason;

            if (_routeRepublishCoroutine != null)
            {
                Debug.Log($"[MicrophonePublisher] route republish already queued; coalescing to {_pendingRouteRepublishReason}");
                return;
            }

            _routeRepublishCoroutine = StartCoroutine(RouteRepublishLoop());
        }

        private void QueueManualDeviceRepublish(string reason)
        {
            if (routeManager != null)
                RefreshActivePolicy(routeManager.RefreshCurrentPolicy("manual_mic_device_preference"), "manual_mic_device_preference");
            else if (routeDetector != null)
                RefreshActivePolicy(routeDetector.DetectNow(), "manual_mic_device_preference");

            string safeReason = string.IsNullOrWhiteSpace(reason)
                ? "manual_mic_device_preference"
                : reason.Trim();

            if (!publishIntentEnabled)
            {
                Debug.Log($"[MicrophonePublisher] mic device preference cached while publish disabled ({safeReason})");
                return;
            }
            if (_shutdownInitiated)
            {
                Debug.Log($"[MicrophonePublisher] mic device preference cached during shutdown ({safeReason})");
                return;
            }
            if (RoomManager.Instance?.Room == null || RoomManager.Instance?.IsConnected != true)
            {
                Debug.Log($"[MicrophonePublisher] mic device preference cached until next room connect ({safeReason})");
                return;
            }
            if (_publishInProgress)
            {
                QueueRouteRepublish(_activePolicy, "mic_device_changed_during_publish");
                return;
            }
            if (!_isPublishing && _audioTrack == null && _micSource == null)
            {
                StartCoroutine(RequestAndPublish(initialReason: "mic_device_changed:" + safeReason));
                return;
            }

            QueueRouteRepublish(_activePolicy, "mic_device_changed:" + safeReason);
        }

        private static bool RequiresMicRebuild(AudioRoutePolicy oldPolicy, AudioRoutePolicy newPolicy)
        {
            return CaptureClass(oldPolicy.Kind) != CaptureClass(newPolicy.Kind)
                   || oldPolicy.PreferredSampleRate != newPolicy.PreferredSampleRate;
        }

        private static int CaptureClass(AudioRouteKind kind)
        {
            switch (kind)
            {
                case AudioRouteKind.BluetoothSco:
                    return 1;
                case AudioRouteKind.WiredHeadset:
                    return 2;
                default:
                    // Speaker, earpiece, A2DP output-only, and unknown all use
                    // the system/default phone microphone capture path.
                    return 0;
            }
        }

        private IEnumerator RouteRepublishLoop()
        {
            while (publishIntentEnabled && !_shutdownInitiated)
            {
                string reason = string.IsNullOrEmpty(_pendingRouteRepublishReason)
                    ? $"route_changed_to_{_activePolicy.RouteName}"
                    : _pendingRouteRepublishReason;
                _pendingRouteRepublishReason = "";

                if (routeRepublishDebounceSeconds > 0f)
                    yield return new WaitForSeconds(routeRepublishDebounceSeconds);

                // Avoid overlapping LiveKit publish instructions. Route events can
                // arrive in bursts while Android moves between A2DP and SCO.
                while (_publishInProgress)
                    yield return null;

                if (!publishIntentEnabled || _shutdownInitiated || RoomManager.Instance?.Room == null)
                    break;

                if (!_isPublishing && _audioTrack == null && _micSource == null)
                    yield return RequestAndPublish(initialReason: reason);
                else
                    yield return RepublishForRouteChange(_activePolicy, reason);

                if (!_isPublishing)
                    break;

                if (_publishedRouteVersion == _routeVersion
                    && string.IsNullOrEmpty(_pendingRouteRepublishReason))
                    break;

                if (string.IsNullOrEmpty(_pendingRouteRepublishReason))
                    _pendingRouteRepublishReason = $"route_changed_retry_to_{_activePolicy.RouteName}";
            }

            _routeRepublishCoroutine = null;
        }

        /// <summary>
        /// Republish after route changes. The old track is unpublished first so the
        /// remote Brain side can observe a graceful unpublish event, then
        /// <see cref="RequestAndPublish"/> rebuilds the source from the new policy.
        ///
        /// <b>Why not reconfigure in place</b>: LiveKit <c>MicrophoneSource</c>
        /// locks the sample rate into the native audio source at construction time.
        /// Reusing the source can recreate the Sprint3
        /// <c>actualRate=X expectedRate=Y</c> InvalidState failure.
        /// </summary>
        private IEnumerator RepublishForRouteChange(AudioRoutePolicy newPolicy, string reason)
        {
            Debug.Log($"[MicrophonePublisher] republishing for {reason}; new policy={newPolicy}");
            _publishInProgress = true; // Prevent concurrent OnRoomConnected / OnAudioRouteChanged publish attempts.

            HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), reason);
            _lastError = reason;

            var room = RoomManager.Instance?.Room;
            if (_audioTrack != null && room != null)
            {
                yield return room.LocalParticipant.UnpublishTrack(_audioTrack, stopOnUnpublish: true);
            }

            // Clean local resources without clearing lastError, preserving
            // route_changed_* until a successful publish clears it.
            StopPublishingInner();

            // RequestAndPublish reports the transient unhealthy reason, then goes attempt -> success.
            _publishInProgress = false; // Let RequestAndPublish own the flag again.
            yield return RequestAndPublish(initialReason: reason);
        }

        private IEnumerator UnpublishForPolicy(string reason)
        {
            _publishInProgress = true;
            var room = RoomManager.Instance?.Room;
            if (_audioTrack != null && room != null)
            {
                Debug.Log($"[MicrophonePublisher] policy UnpublishTrack (reason={reason})");
                yield return room.LocalParticipant.UnpublishTrack(_audioTrack, stopOnUnpublish: true);
            }
            StopPublishingInner();
            _publishInProgress = false;
            routeManager?.RequestCommunicationMode(false);
            HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), $"policy_disabled:{reason}");
            Debug.Log($"[MicrophonePublisher] microphone publish disabled by policy ({reason})");
        }

        // Cleanup.

        private void OnRoomDisconnected()
        {
            StopPublishing("room_disconnected");
        }

        private void StopPublishing(string reason)
        {
            if (!_isPublishing && _micSource == null && _audioTrack == null)
            {
                StopUplinkWatchdog(reason);
                return;
            }

            StopPublishingInner();
            HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), "");
            Debug.Log($"[MicrophonePublisher] Microphone publishing stopped ({reason})");
        }

        /// <summary>
        /// Local cleanup without writing health. The route-change republish path
        /// uses this to avoid clearing <c>route_changed_*</c> before success.
        /// </summary>
        private void StopPublishingInner()
        {
            StopUplinkWatchdog(string.IsNullOrWhiteSpace(_lastError) ? "stopped" : _lastError);
            _isPublishing = false;
            _publishInProgress = false;
            _activeAudioSourceKind = "none";
            var source = _micSource;
            _micSource = null;
            if (source != null)
            {
                // The pinned LiveKit Unity SDK does not dispose our C# source
                // when UnpublishTrack completes, so formal App cleanup owns
                // detaching, stopping, and disposing every retry source.
                source.AudioRead -= OnMicrophoneAudioRead;
                try { source.Stop(); }
                catch (Exception e) { Debug.LogWarning($"[MicrophonePublisher] Stop microphone failed: {e.Message}"); }
                try { (source as IDisposable)?.Dispose(); }
                catch (Exception e) { Debug.LogWarning($"[MicrophonePublisher] Dispose microphone source failed: {e.Message}"); }
            }
            _audioTrack = null;
            if (string.IsNullOrWhiteSpace(_lastError))
                _lastPublishStage = "stopped";
        }

        void OnDestroy()
        {
            StopPublishing("destroy");

            if (routeManager != null)
            {
                routeManager.OnRoutePolicyChanged -= OnAudioRouteChanged;
                routeManager.RequestCommunicationMode(false);
            }
            if (lifecycleManager != null)
                lifecycleManager.OnStateChanged -= OnLifecycleStateChanged;

            if (routeDetector != null)
                routeDetector.OnRouteChanged -= OnAudioRouteChanged;

            var rm = RoomManager.Instance;
            if (rm != null)
            {
                rm.OnConnected -= OnRoomConnected;
                rm.OnDisconnected -= OnRoomDisconnected;
            }
        }

        private IEnumerator RequestAndroidBluetoothPermissionIfNeeded()
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            if (AndroidSdkInt() < 31)
                yield break;
            const string bluetoothConnect = "android.permission.BLUETOOTH_CONNECT";
            if (UnityEngine.Android.Permission.HasUserAuthorizedPermission(bluetoothConnect))
                yield break;

            UnityEngine.Android.Permission.RequestUserPermission(bluetoothConnect);
            float deadline = Time.realtimeSinceStartup + 4f;
            while (!UnityEngine.Android.Permission.HasUserAuthorizedPermission(bluetoothConnect)
                   && Time.realtimeSinceStartup < deadline)
            {
                yield return null;
            }
#else
            yield break;
#endif
        }

#if UNITY_ANDROID && !UNITY_EDITOR
        private static int AndroidSdkInt()
        {
            try
            {
                using (var version = new AndroidJavaClass("android.os.Build$VERSION"))
                    return version.GetStatic<int>("SDK_INT");
            }
            catch (Exception)
            {
                return 0;
            }
        }
#endif

        private static double UnixSeconds()
            => (DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalSeconds;
    }
}
