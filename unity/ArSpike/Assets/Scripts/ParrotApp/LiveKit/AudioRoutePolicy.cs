using System;

namespace ParrotApp.LiveKit
{
    /// <summary>
    /// 当前音频路由分类。命名与 Android <c>AudioManager</c> 的 is*On 系列、iOS
    /// <c>AVAudioSession.currentRoute.outputs[].portType</c> 大致对齐，但只保留 Sprint4
    /// 真机 spike 实际需要区分的几档；细分（USB / HDMI / CarAudio …）等到 Phase 4
    /// 协议升级时再加。
    /// </summary>
    public enum AudioRouteKind
    {
        Unknown = 0,
        Speaker,
        Earpiece,
        WiredHeadset,
        /// <summary>蓝牙双向链路（mic 录音用）。Android 大多数 headset 的输入只能通过 SCO。</summary>
        BluetoothSco,
        /// <summary>蓝牙仅输出（A2DP）。如果 mic 同时活跃，系统通常 fallback 到 SCO；
        /// 这里保留 A2DP 档位是为了让外层 detect 到"只放不录"路由也能告知 publisher。</summary>
        BluetoothA2dp,
    }

    /// <summary>
    /// 当前会话的音频路由策略快照（不可变 struct）。
    ///
    /// <b>Sprint4 范围说明</b>：本 struct <b>仅在 ArSpike LiveKit 子目录内</b>消费，
    /// 用于 <see cref="MicrophonePublisher"/> 决定 native source 采样率与 republish 触发。
    /// <b>不</b>下沉到 <c>EcpFrontendState</c>、<b>不</b>进 Blackboard，<b>不</b>新增
    /// ConnectionHealth 字段；avoid 与 Phase 4 协议升级冲突。
    ///
    /// <b>// AudioRoutePolicy producer hook reserved for Sprint4 Phase 4</b>
    /// — 后续把 <see cref="RouteName"/> / <see cref="PreferredSampleRate"/> /
    ///   <c>echo_policy</c> / <c>publish_intent</c> 暴露给 Brain 端时，把
    ///   <see cref="AudioRouteDetector"/> 升格为唯一 producer，灌到候选 BB 键
    ///   <c>session/audio_route_policy</c> 与 <c>EcpState</c>。
    /// </summary>
    public readonly struct AudioRoutePolicy : IEquatable<AudioRoutePolicy>
    {
        public AudioRouteKind Kind { get; }

        /// <summary>对外稳定字符串：speaker / earpiece / wired_headset / bluetooth_sco /
        /// bluetooth_a2dp / unknown。用于日志、health <c>audio_last_error</c> 透传、
        /// 以及未来 EcpState <c>audio_route</c> 字段。</summary>
        public string RouteName { get; }

        /// <summary>本路由推荐的 LiveKit native source sample rate（Hz）。允许域 {16000,
        /// 24000, 48000}（Sprint4 用户口径）；具体映射见 <see cref="ForKind"/>。</summary>
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
        /// 根据 <paramref name="kind"/> 返回标准 policy。
        ///
        /// <b>采样率口径</b>（与 <c>livekit-unity-sdk.mdc</c> §"Android 麦克风采样率不要跟随
        /// 不稳定路由漂移" + Sprint3 brain_connected_black_video 修复一致）：
        /// <list type="bullet">
        /// <item><b>speaker / earpiece / wired_headset</b>: 48000 Hz（baseline，不破坏非蓝牙音质）。</item>
        /// <item><b>bluetooth_sco</b>: 16000 Hz（SCO 物理上限，强行 48k 会跑出
        ///   <c>actualRate=16000 expectedRate=48000</c> InvalidState）。</item>
        /// <item><b>bluetooth_a2dp</b>: 16000 Hz（mic 路径系统通常 fallback SCO，按 SCO 处理）。</item>
        /// <item><b>unknown</b>: 48000 Hz（安全默认，比 16k 误判破坏面更小）。</item>
        /// </list>
        /// </summary>
        public static AudioRoutePolicy ForKind(AudioRouteKind kind)
        {
            switch (kind)
            {
                case AudioRouteKind.BluetoothSco:
                case AudioRouteKind.BluetoothA2dp:
                    return new AudioRoutePolicy(kind, RouteNameOf(kind), 16000);
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
