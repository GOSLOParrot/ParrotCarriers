using System;
using UnityEngine;

namespace ParrotApp.LiveKit
{
    /// <summary>
    /// Formal App audio-route facade.
    ///
    /// Android native code owns communication-device routing and audio focus.
    /// This C# component owns the stable route snapshot, fallback/diagnostic detector, and
    /// route-change event that the LiveKit microphone executor consumes.
    /// </summary>
    [DisallowMultipleComponent]
    public class AudioRouteManager : MonoBehaviour
    {
        [SerializeField] private bool preferNativeAndroid = true;
        [SerializeField] private AudioRouteDetector fallbackDetector;
        [SerializeField] private AudioRoutePreference preference = AudioRoutePreference.Auto;

        public AudioRoutePolicy CurrentPolicy { get; private set; } = AudioRoutePolicy.Default();
        public AudioRouteSnapshotDto CurrentSnapshot { get; private set; }
        public string LastDetectionSource { get; private set; } = "unknown";
        public string LastDeviceSummary { get; private set; } = "";
        public string LastError { get; private set; } = "";
        public bool NativeAvailable => _native != null && _native.IsAvailable;
        public AudioRoutePreference Preference => preference;

        public event Action<AudioRoutePolicy, AudioRoutePolicy> OnRoutePolicyChanged;
        public event Action<AudioRouteSnapshotDto> OnSnapshotChanged;

        private AndroidAudioRouteManager _native;
        private int _lastNativeRouteVersion;
        private bool _subscribedFallback;
        private bool _temporaryNativePreferenceActive;

        private void OnEnable()
        {
            ResolveFallbackDetector();
            SubscribeFallbackDetector();
            CurrentPolicy = fallbackDetector != null ? fallbackDetector.CurrentPolicy : AudioRoutePolicy.Default();

            if (preferNativeAndroid)
            {
                _native = new AndroidAudioRouteManager(OnAndroidAudioRouteSnapshot);
                if (_native.IsAvailable)
                {
                    _native.SetRoutePreference(AudioRouteSnapshotDto.PreferenceWireValue(preference));
                    _native.Refresh();
                }
            }

            if (!NativeAvailable)
                ApplyFallbackPolicy("enable_fallback");
        }

        private void OnDisable()
        {
            if (_subscribedFallback && fallbackDetector != null)
                fallbackDetector.OnRouteChanged -= OnFallbackRouteChanged;
            _subscribedFallback = false;

            _native?.Dispose();
            _native = null;
        }

        public AudioRoutePolicy RefreshCurrentPolicy(string trigger = "manual_rescan")
        {
            if (NativeAvailable)
            {
                _native.Refresh();
                return CurrentPolicy;
            }

            ResolveFallbackDetector();
            if (fallbackDetector != null)
            {
                ApplyPolicy(fallbackDetector.RefreshCurrentPolicy(trigger), trigger, BuildFallbackSnapshot(trigger));
                return CurrentPolicy;
            }
            return CurrentPolicy;
        }

        public void SetPreference(AudioRoutePreference nextPreference)
        {
            preference = nextPreference;
            _temporaryNativePreferenceActive = false;
            if (NativeAvailable)
                _native.SetRoutePreference(AudioRouteSnapshotDto.PreferenceWireValue(preference));
            RefreshCurrentPolicy("route_preference_changed");
        }

        public void ApplyTemporaryNativePreference(AudioRoutePreference nextPreference, string trigger)
        {
            // Capture recovery can briefly force the Android communication
            // device away from a dead SCO mic without changing the user's
            // durable App preference. The next headset topology change restores
            // the public preference so Auto can prefer Bluetooth again.
            if (!NativeAvailable)
            {
                RefreshCurrentPolicy(trigger ?? "temporary_route_preference_unavailable");
                return;
            }

            _temporaryNativePreferenceActive = true;
            _native.SetRoutePreference(AudioRouteSnapshotDto.PreferenceWireValue(nextPreference));
            RefreshCurrentPolicy(trigger ?? "temporary_route_preference_changed");
        }

        public void RequestCommunicationMode(bool enabled)
        {
            if (NativeAvailable)
                _native.RequestCommunicationMode(enabled);
        }

        public void ApplyPreferredCommunicationDevice()
        {
            if (NativeAvailable)
                _native.ApplyPreferredCommunicationDevice();
        }

        public void ClearCommunicationDevice()
        {
            if (NativeAvailable)
                _native.ClearCommunicationDevice();
        }

        public void OnAndroidAudioRouteSnapshot(string json)
        {
            if (string.IsNullOrWhiteSpace(json)) return;
            try
            {
                var snapshot = JsonUtility.FromJson<AudioRouteSnapshotDto>(json);
                if (snapshot == null) return;
                if (snapshot.route_version > 0 && snapshot.route_version < _lastNativeRouteVersion)
                {
                    Debug.Log("[AudioRouteManager] ignoring stale native route snapshot v" + snapshot.route_version);
                    return;
                }
                _lastNativeRouteVersion = Mathf.Max(_lastNativeRouteVersion, snapshot.route_version);
                if (_temporaryNativePreferenceActive && ShouldRestoreTemporaryPreference(snapshot.reason))
                {
                    _temporaryNativePreferenceActive = false;
                    if (NativeAvailable)
                        _native.SetRoutePreference(AudioRouteSnapshotDto.PreferenceWireValue(preference));
                    return;
                }
                ApplyPolicy(snapshot.ToPolicy(), "native:" + snapshot.reason, snapshot);
            }
            catch (Exception e)
            {
                LastError = "native_snapshot_parse_failed:" + e.Message;
                Debug.LogWarning("[AudioRouteManager] native snapshot parse failed: " + e.Message);
                ApplyFallbackPolicy("native_snapshot_parse_failed");
            }
        }

        private void ResolveFallbackDetector()
        {
            if (fallbackDetector == null)
                fallbackDetector = FindObjectOfType<AudioRouteDetector>();
            if (fallbackDetector == null)
                fallbackDetector = gameObject.AddComponent<AudioRouteDetector>();
        }

        private void SubscribeFallbackDetector()
        {
            if (_subscribedFallback || fallbackDetector == null) return;
            fallbackDetector.OnRouteChanged += OnFallbackRouteChanged;
            _subscribedFallback = true;
        }

        private void OnFallbackRouteChanged(AudioRoutePolicy oldPolicy, AudioRoutePolicy newPolicy)
        {
            if (NativeAvailable)
            {
                // Keep the fallback detector warm for diagnostics, but native
                // snapshots remain the accepted route source on Android.
                return;
            }
            ApplyPolicy(newPolicy, "fallback_route_changed", BuildFallbackSnapshot("fallback_route_changed"));
        }

        private static bool ShouldRestoreTemporaryPreference(string reason)
        {
            // Do not restore on communication_device_changed: our own temporary
            // phone-mic fallback can trigger that callback while the capture
            // retry is still settling. Actual headset topology changes arrive
            // through device_added/device_removed.
            return string.Equals(reason, "device_added", StringComparison.OrdinalIgnoreCase)
                   || string.Equals(reason, "device_removed", StringComparison.OrdinalIgnoreCase);
        }

        private void ApplyFallbackPolicy(string trigger)
        {
            ResolveFallbackDetector();
            var policy = fallbackDetector != null ? fallbackDetector.DetectNow() : AudioRoutePolicy.Default();
            ApplyPolicy(policy, trigger, BuildFallbackSnapshot(trigger));
        }

        private AudioRouteSnapshotDto BuildFallbackSnapshot(string reason)
        {
            var policy = fallbackDetector != null ? fallbackDetector.CurrentPolicy : CurrentPolicy;
            return new AudioRouteSnapshotDto
            {
                route_version = _lastNativeRouteVersion,
                timestamp_unix_ms = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
                source = fallbackDetector != null ? fallbackDetector.LastDetectionSource : "unity_fallback_missing",
                platform = Application.platform.ToString(),
                preference = AudioRouteSnapshotDto.PreferenceWireValue(preference),
                input_route = InputRouteFor(policy),
                output_route = policy.RouteName,
                available_inputs = Array.Empty<string>(),
                available_outputs = Array.Empty<string>(),
                microphone_permission = Application.HasUserAuthorization(UserAuthorization.Microphone) ? "granted" : "unknown",
                bluetooth_connect_permission = "unknown",
                audio_focus = "not_requested",
                mode = "normal",
                reason = reason ?? "",
                requires_mic_republish = true,
                recommended_sample_rate_hz = policy.PreferredSampleRate,
                is_degraded = false,
                error = "",
            };
        }

        private void ApplyPolicy(AudioRoutePolicy policy, string trigger, AudioRouteSnapshotDto snapshot)
        {
            var old = CurrentPolicy;
            CurrentPolicy = policy;
            CurrentSnapshot = snapshot;
            LastDetectionSource = snapshot != null ? snapshot.source : "unknown";
            LastDeviceSummary = snapshot != null ? snapshot.DeviceSummary() : "";
            LastError = snapshot != null ? (snapshot.error ?? "") : "";
            OnSnapshotChanged?.Invoke(snapshot);

            bool changed = !old.Equals(policy);
            if (changed || (snapshot != null && snapshot.requires_mic_republish))
            {
                Debug.Log("[AudioRouteManager] route accepted via " + trigger + ": " + old + " -> " + policy);
                OnRoutePolicyChanged?.Invoke(old, policy);
            }
        }

        private static string InputRouteFor(AudioRoutePolicy policy)
        {
            switch (policy.Kind)
            {
                case AudioRouteKind.BluetoothSco:
                    return "bluetooth_sco";
                case AudioRouteKind.WiredHeadset:
                    return "wired_headset";
                default:
                    return "system_default_microphone";
            }
        }
    }
}
