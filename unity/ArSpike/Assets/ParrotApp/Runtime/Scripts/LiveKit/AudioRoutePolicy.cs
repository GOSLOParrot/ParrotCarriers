using System;

namespace ParrotApp.LiveKit
{
    /// <summary>
    /// Coarse audio route categories used by the formal phone app.
    ///
    /// The names line up with Android AudioManager route concepts and the
    /// future iOS AVAudioSession bridge, but the enum deliberately stays small:
    /// it only covers the routes needed for the current LiveKit/LineB phone
    /// work. More detailed USB/HDMI/car routes should be added with a protocol
    /// upgrade, not as one-off UI strings.
    /// </summary>
    public enum AudioRouteKind
    {
        Unknown = 0,
        Speaker,
        Earpiece,
        WiredHeadset,
        /// <summary>Bluetooth bidirectional headset path; Android headset microphones usually require SCO.</summary>
        BluetoothSco,
        /// <summary>
        /// Bluetooth output-only route. It must not be treated as a Bluetooth
        /// microphone input unless the OS also exposes a SCO input route.
        /// </summary>
        BluetoothA2dp,
    }

    /// <summary>
    /// Immutable snapshot of Unity's local audio route policy.
    ///
    /// This struct is a local runtime input for <see cref="MicrophonePublisher"/>
    /// sample-rate selection and route-change republish decisions. It does not
    /// write health, ECP, or Blackboard directly. <see cref="AudioRoutePolicyBrainReporter"/>
    /// mirrors the compact input/output route policy to Brain after LiveKit and
    /// Brain presence are available.
    /// </summary>
    public readonly struct AudioRoutePolicy : IEquatable<AudioRoutePolicy>
    {
        public AudioRouteKind Kind { get; }

        /// <summary>Stable external value: speaker, earpiece, wired_headset, bluetooth_sco, bluetooth_a2dp, or unknown.</summary>
        public string RouteName { get; }

        /// <summary>Recommended LiveKit native microphone sample rate for this route.</summary>
        public int PreferredSampleRate { get; }

        public bool IsBluetooth =>
            Kind == AudioRouteKind.BluetoothSco || Kind == AudioRouteKind.BluetoothA2dp;

        public AudioRoutePolicy(AudioRouteKind kind, string routeName, int preferredSampleRate)
        {
            Kind = kind;
            RouteName = string.IsNullOrEmpty(routeName) ? "unknown" : routeName;
            PreferredSampleRate = preferredSampleRate > 0 ? preferredSampleRate : 48000;
        }

        public static AudioRoutePolicy Default()
            => new AudioRoutePolicy(AudioRouteKind.Unknown, "unknown", 48000);

        /// <summary>
        /// Returns the standard policy for <paramref name="kind"/>.
        ///
        /// Speaker, earpiece, wired headset, and A2DP stay at 48 kHz. SCO uses
        /// 16 kHz to avoid LiveKit native source mismatches on Android headset
        /// microphone capture. A2DP is output-only, so it must not force the
        /// Unity microphone source into the SCO policy unless Android exposes a
        /// real SCO input route.
        /// </summary>
        public static AudioRoutePolicy ForKind(AudioRouteKind kind)
        {
            switch (kind)
            {
                case AudioRouteKind.BluetoothSco:
                    return new AudioRoutePolicy(kind, RouteNameOf(kind), 16000);
                case AudioRouteKind.BluetoothA2dp:
                case AudioRouteKind.WiredHeadset:
                case AudioRouteKind.Speaker:
                case AudioRouteKind.Earpiece:
                    return new AudioRoutePolicy(kind, RouteNameOf(kind), 48000);
                default:
                    return Default();
            }
        }

        public static string RouteNameOf(AudioRouteKind kind)
        {
            switch (kind)
            {
                case AudioRouteKind.Speaker: return "speaker";
                case AudioRouteKind.Earpiece: return "earpiece";
                case AudioRouteKind.WiredHeadset: return "wired_headset";
                case AudioRouteKind.BluetoothSco: return "bluetooth_sco";
                case AudioRouteKind.BluetoothA2dp: return "bluetooth_a2dp";
                default: return "unknown";
            }
        }

        public bool Equals(AudioRoutePolicy other)
            => Kind == other.Kind
               && RouteName == other.RouteName
               && PreferredSampleRate == other.PreferredSampleRate;

        public override bool Equals(object obj) => obj is AudioRoutePolicy o && Equals(o);

        public override int GetHashCode()
        {
            unchecked
            {
                int h = (int)Kind;
                h = (h * 397) ^ (RouteName?.GetHashCode() ?? 0);
                h = (h * 397) ^ PreferredSampleRate;
                return h;
            }
        }

        public static bool operator ==(AudioRoutePolicy a, AudioRoutePolicy b) => a.Equals(b);
        public static bool operator !=(AudioRoutePolicy a, AudioRoutePolicy b) => !a.Equals(b);

        public override string ToString() => $"{RouteName}@{PreferredSampleRate}Hz";
    }
}
