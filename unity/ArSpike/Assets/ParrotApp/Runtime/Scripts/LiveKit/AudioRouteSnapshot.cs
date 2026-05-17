using System;

namespace ParrotApp.LiveKit
{
    public enum AudioRoutePreference
    {
        Auto = 0,
        Bluetooth,
        PhoneMic,
        SystemDefault,
    }

    /// <summary>
    /// Unity-side DTO for the App-owned Android route bridge.
    ///
    /// This is local runtime state. It is not RoomSetting persistence and it is
    /// not a full ECP payload. Brain only receives a compact observer report
    /// through <see cref="AudioRoutePolicyBrainReporter"/>.
    /// </summary>
    [Serializable]
    public class AudioRouteSnapshotDto
    {
        public int route_version;
        public long timestamp_unix_ms;
        public string source = "unknown";
        public string platform = "unknown";
        public int api_level;
        public string preference = "auto";
        public string input_route = "system_default_microphone";
        public string output_route = "unknown";
        public string communication_device_type = "";
        public string communication_device_name = "";
        public string[] available_inputs = Array.Empty<string>();
        public string[] available_outputs = Array.Empty<string>();
        public string microphone_permission = "unknown";
        public string bluetooth_connect_permission = "unknown";
        public string audio_focus = "not_requested";
        public string mode = "normal";
        public string reason = "";
        public bool requires_mic_republish;
        public int recommended_sample_rate_hz = 48000;
        public bool is_degraded;
        public string error = "";

        public bool HasError => is_degraded || !string.IsNullOrWhiteSpace(error);

        public AudioRoutePolicy ToPolicy()
        {
            var kind = KindFromRoutes(input_route, output_route);
            var policy = AudioRoutePolicy.ForKind(kind);
            if (recommended_sample_rate_hz > 0 && recommended_sample_rate_hz != policy.PreferredSampleRate)
                return new AudioRoutePolicy(kind, policy.RouteName, recommended_sample_rate_hz);
            return policy;
        }

        public string DeviceSummary()
        {
            string inputs = available_inputs == null || available_inputs.Length == 0
                ? "none"
                : string.Join(",", available_inputs);
            string outputs = available_outputs == null || available_outputs.Length == 0
                ? "none"
                : string.Join(",", available_outputs);
            return "native:inputs=[" + inputs + "],outputs=[" + outputs + "],comm="
                   + (communication_device_type ?? "");
        }

        public static string PreferenceWireValue(AudioRoutePreference preference)
        {
            switch (preference)
            {
                case AudioRoutePreference.Bluetooth:
                    return "bluetooth";
                case AudioRoutePreference.PhoneMic:
                    return "phone_mic";
                case AudioRoutePreference.SystemDefault:
                    return "system_default";
                default:
                    return "auto";
            }
        }

        public static AudioRouteKind KindFromRoutes(string inputRoute, string outputRoute)
        {
            if (EqualsRoute(inputRoute, "bluetooth_sco") || EqualsRoute(outputRoute, "bluetooth_sco"))
                return AudioRouteKind.BluetoothSco;
            if (EqualsRoute(inputRoute, "wired_headset") || EqualsRoute(outputRoute, "wired_headset"))
                return AudioRouteKind.WiredHeadset;
            // This policy drives the microphone source, not durable output UI.
            // If Android says the input is phone/default mic, keep the capture
            // policy on the phone route even when the output route is A2DP.
            // The output route remains available on the snapshot for HUD/Brain
            // reports without forcing a local mic-track rebuild.
            if (EqualsRoute(inputRoute, "phone_mic") || EqualsRoute(inputRoute, "system_default_microphone"))
                return AudioRouteKind.Speaker;
            if (EqualsRoute(outputRoute, "speaker"))
                return AudioRouteKind.Speaker;
            if (EqualsRoute(outputRoute, "earpiece"))
                return AudioRouteKind.Earpiece;
            if (EqualsRoute(outputRoute, "bluetooth_a2dp"))
                return AudioRouteKind.BluetoothA2dp;
            return AudioRouteKind.Unknown;
        }

        private static bool EqualsRoute(string a, string b)
            => string.Equals(a, b, StringComparison.OrdinalIgnoreCase);
    }
}
