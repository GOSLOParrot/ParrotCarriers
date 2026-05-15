using System;
using System.Collections;
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
    ///   <see cref="AudioRouteDetector"/>: speaker/wired use 48k,
    ///   bluetooth_sco/a2dp use 16k, and unknown falls back to 48k.</item>
    /// <item>Device selection prefers a <see cref="UnityEngine.Microphone"/> whose
    ///   name contains <c>bluetooth</c>, <c>airpods</c>, or <c>sco</c> while a
    ///   Bluetooth route is active. Otherwise it uses the system default.
    ///   <see cref="preferredDevice"/> can still override this from Inspector.</item>
    /// <item><see cref="AudioRouteDetector"/> owns route detection through
    ///   <c>AudioSettings.OnAudioConfigurationChanged</c> plus polling fallback.
    ///   On changes, this class unpublishes and republishes so the LiveKit native
    ///   source is rebuilt with the new sample rate.</item>
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
    /// <item>Route policy still comes from <see cref="AudioRouteDetector"/>.
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

        [Tooltip("Small debounce to coalesce Bluetooth/SCO route-change bursts before rebuilding the LiveKit audio source.")]
        [SerializeField] private float routeRepublishDebounceSeconds = 0.5f;

        [Header("Session Policy")]
        [Tooltip("False = keep the LiveKit room alive but do not publish microphone audio.")]
        [SerializeField] private bool publishIntentEnabled = true;

        private MicrophoneSource _micSource;
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

        private ConnectionHealthAggregator HealthAggregator =>
            lifecycleManager != null ? lifecycleManager.HealthAggregator : null;

        public bool IsPublishing => _isPublishing;
        public bool PublishAttempted => _publishAttempted;
        public string SelectedDevice => _selectedDevice;
        public string LastError => _lastError;
        public int ConfiguredSampleRate => _configuredSampleRate;
        public int UnityOutputSampleRate => _unityOutputSampleRate;
        public AudioRoutePolicy ActivePolicy => _activePolicy;
        public bool PublishIntentEnabled => publishIntentEnabled;
        public string PreferredDevice => preferredDevice ?? "";
        public string LastManualDeviceStatus { get; private set; } = "auto";
        public int AvailableDeviceCount => Microphone.devices != null ? Microphone.devices.Length : 0;

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

            if (routeDetector == null)
                routeDetector = FindObjectOfType<AudioRouteDetector>();
            if (routeDetector == null)
            {
                routeDetector = gameObject.AddComponent<AudioRouteDetector>();
                Debug.Log("[MicrophonePublisher] no AudioRouteDetector found; auto-added on this GameObject");
            }
            routeDetector.OnRouteChanged += OnAudioRouteChanged;
            _activePolicy = routeDetector.CurrentPolicy;

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

        private void OnRoomConnected()
        {
            if (!publishIntentEnabled)
            {
                Debug.Log("[MicrophonePublisher] publish intent disabled; room stays connected without mic");
                return;
            }
            if (_isPublishing || _publishInProgress) return;
            // Pull the detector before publishing so the route policy is fresh.
            if (routeDetector != null) RefreshActivePolicy(routeDetector.DetectNow(), "room_connected");
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
                StartCoroutine(RequestAndPublish(initialReason: $"policy_enabled:{reason}"));
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

            HealthAggregator?.ReportAudioPublishAttempt(UnixSeconds());
            if (initialReason != null)
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), initialReason);

            yield return Application.RequestUserAuthorization(UserAuthorization.Microphone);

            if (!Application.HasUserAuthorization(UserAuthorization.Microphone))
            {
                _lastError = "permission_denied";
                Debug.LogError("[MicrophonePublisher] ERROR permission_denied");
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), _lastError);
                _publishInProgress = false;
                yield break;
            }

            if (!publishIntentEnabled)
            {
                Debug.Log("[MicrophonePublisher] publish intent disabled after permission gate; aborting");
                _publishInProgress = false;
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), "policy_disabled_after_permission");
                yield break;
            }

            if (Microphone.devices.Length == 0)
            {
                _lastError = "no_microphone_devices";
                Debug.LogWarning("[MicrophonePublisher] ERROR no_microphone_devices");
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), _lastError);
                _publishInProgress = false;
                yield break;
            }

            AudioRoutePolicy publishPolicy = _activePolicy;
            uint publishRouteVersion = _routeVersion;

            string device = SelectDevice(publishPolicy);
            _selectedDevice = device;
            Debug.Log($"[MicrophonePublisher] Using device: '{device}' for policy={publishPolicy}");

            var room = RoomManager.Instance?.Room;
            if (room == null)
            {
                _lastError = "room_missing_after_permission";
                Debug.LogWarning("[MicrophonePublisher] ERROR room_missing_after_permission");
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), _lastError);
                _publishInProgress = false;
                yield break;
            }

            if (!publishIntentEnabled)
            {
                Debug.Log("[MicrophonePublisher] publish intent disabled before track publish; aborting");
                _publishInProgress = false;
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), "policy_disabled_before_publish");
                yield break;
            }

            ConfigureLiveKitMicrophoneSampleRate(device, publishPolicy);

            _micSource = new MicrophoneSource(device, gameObject);
            _audioTrack = LocalAudioTrack.CreateAudioTrack("microphone", _micSource, room);

            var options = new TrackPublishOptions
            {
                Source = TrackSource.SourceMicrophone,
                AudioEncoding = new AudioEncoding { MaxBitrate = 64_000 },
            };

            var publish = room.LocalParticipant.PublishTrack(_audioTrack, options);
            yield return publish;

            if (publish.IsError)
            {
                _lastError = "publish_failed";
                Debug.LogError("[MicrophonePublisher] ERROR publish_failed (PublishTrackInstruction.IsError; SDK exposes no Error details)");
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), _lastError);
                _publishInProgress = false;
                yield break;
            }

            _micSource.Start();
            _isPublishing = true;
            _publishInProgress = false;
            _publishedRouteVersion = publishRouteVersion;
            _lastError = "";
            HealthAggregator?.ReportAudioPublished(true, UnixSeconds(), "");
            Debug.Log(
                $"[MicrophonePublisher] publishing started: device='{device}' route={publishPolicy.RouteName} " +
                $"configuredSampleRate={_configuredSampleRate} unityOutputSampleRate={_unityOutputSampleRate}");

            if (publishRouteVersion != _routeVersion && publishIntentEnabled && !_shutdownInitiated)
            {
                QueueRouteRepublish(
                    _activePolicy,
                    $"route_changed_during_publish_to_{_activePolicy.RouteName}");
            }
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
        /// <b>Bluetooth rule</b>: when detector reports a Bluetooth policy, scan
        /// <c>Microphone.devices</c> for bluetooth/airpods/sco/headset names. If no
        /// explicit device is visible, fall back to the default while keeping the
        /// native source at 16k so SCO can still work behind Android routing.
        /// </summary>
        private string SelectDevice(AudioRoutePolicy policy)
        {
            var devices = Microphone.devices;

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

        public bool CyclePreferredDevice(string reason = "manual_device_cycle")
        {
            var devices = Microphone.devices;
            if (devices == null || devices.Length == 0)
            {
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
            if (devices == null || devices.Length == 0) return "none";
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
            if (routeDetector != null)
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
            if (!_isPublishing && _micSource == null && _audioTrack == null) return;

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
            _isPublishing = false;
            _publishInProgress = false;
            try { _micSource?.Stop(); }
            catch (Exception e) { Debug.LogWarning($"[MicrophonePublisher] Stop microphone failed: {e.Message}"); }
            _micSource = null;
            _audioTrack = null;
        }

        void OnDestroy()
        {
            StopPublishing("destroy");

            if (routeDetector != null)
                routeDetector.OnRouteChanged -= OnAudioRouteChanged;

            var rm = RoomManager.Instance;
            if (rm != null)
            {
                rm.OnConnected -= OnRoomConnected;
                rm.OnDisconnected -= OnRoomDisconnected;
            }
        }

        private static double UnixSeconds()
            => (DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalSeconds;
    }
}
