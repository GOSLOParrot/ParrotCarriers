using UnityEngine;

namespace ParrotApp.Config
{
    /// <summary>
    /// Sprint4 Phase 3 集中可调阈值表。
    ///
    /// 17 个参数全部来源于 <c>.cursor/skills/livekit-unity-lifecycle/IMPL_REF.md §10</c>。
    /// 这里是 Unity 侧消费入口，<b>禁止在业务代码中再次硬编同名常量</b>（"协议污染"反模式）。
    /// 默认值是 spike 起点；S1–S8 跑完后再固化。
    ///
    /// 创建一个 asset：在 Project 视图里 <c>Create → Parrot → Lifecycle Config</c>，
    /// 或通过 <c>Tools / Parrot / Lifecycle Tuning</c> 菜单（见
    /// <c>ParrotLifecycleConfigMenu.cs</c>）。
    ///
    /// <b>不要在 Inspector 之外改默认值</b>：所有调整应通过 asset override，
    /// 让 spike 调参可重放、可挂未来 app 设置面板。
    /// </summary>
    [CreateAssetMenu(
        fileName = "ParrotLifecycleConfig",
        menuName = "Parrot/Lifecycle Config",
        order = 50)]
    public class ParrotLifecycleConfig : ScriptableObject
    {
        // ─── Background lifecycle ──────────────────────────────────────────

        // see livekit-unity-lifecycle/IMPL_REF.md §10
        [Header("Background lifecycle")]
        [Tooltip("OnApplicationPause(true) 短背景防抖窗（秒）。see IMPL_REF.md §10")]
        [Min(0f)] public float T_SHORT_BG = 5f;

        // see livekit-unity-lifecycle/IMPL_REF.md §10 / spike S2
        [Tooltip("长背景强切阈值（秒）；超过此值进 shutting_down。see IMPL_REF.md §10 / spike S2")]
        [Min(0f)] public float T_LONG_BG = 30f;

        // ─── Graceful shutdown ────────────────────────────────────────────

        // see livekit-unity-lifecycle/IMPL_REF.md §2 / §10 / spike S2
        [Header("Graceful shutdown")]
        [Tooltip("graceful shutdown 步骤 4 等 Disconnected event 软超时（秒）。see IMPL_REF.md §2 / §10 / spike S2")]
        [Min(0f)] public float T_DISCONNECT_WAIT_HARD = 5f;

        // see livekit-unity-lifecycle/IMPL_REF.md §2 / §10
        [Tooltip("Disconnect → 新 Connect 之间的 cool-down（秒）；避免 30s ICE 残留下的 identity 抢占。see IMPL_REF.md §2 / §10")]
        [Min(0f)] public float T_SHUTDOWN_COOLDOWN = 5f;

        // ─── Connectivity watchdog (heartbeat) ─────────────────────────────

        // see livekit-unity-lifecycle/IMPL_REF.md §3 / §10
        [Header("Connectivity watchdog (heartbeat)")]
        [Tooltip("EcpState heartbeat 频率（秒）。see IMPL_REF.md §3 / §10")]
        [Min(0.5f)] public float T_HEARTBEAT_INTERVAL = 5f;

        // see livekit-unity-lifecycle/IMPL_REF.md §3 / §10
        [Tooltip("watchdog 软超时（秒）→ degraded。see IMPL_REF.md §3 / §10")]
        [Min(0f)] public float T_HEARTBEAT_SOFT = 15f;

        // see livekit-unity-lifecycle/IMPL_REF.md §3 / §10
        [Tooltip("watchdog 硬超时（秒）→ unhealthy。see IMPL_REF.md §3 / §10")]
        [Min(0f)] public float T_HEARTBEAT_HARD = 30f;

        // ─── AR session ────────────────────────────────────────────────────

        // see livekit-unity-lifecycle/IMPL_REF.md §5 / §10 / spike S6
        [Header("AR session")]
        [Tooltip("用户切前后摄/重启 AR Session 最小间隔（秒）。see IMPL_REF.md §5 / §10 / spike S6")]
        [Min(0f)] public float T_AR_SESSION_TOGGLE_MIN = 2f;

        // ─── Video tier switching ──────────────────────────────────────────

        // see livekit-unity-lifecycle/IMPL_REF.md §6 / §10 / spike S5
        [Header("Video tier switching")]
        [Tooltip("setVideoTier unpublish→republish cool-down（秒）。see IMPL_REF.md §6 / §10 / spike S5")]
        [Min(0f)] public float T_TIER_COOLDOWN = 3f;

        // see livekit-unity-lifecycle/IMPL_REF.md §10 / spike S5
        [Tooltip("publish 后等 First frame 超时（秒）；超时降级 stale。see IMPL_REF.md §10 / spike S5")]
        [Min(0f)] public float T_FIRST_FRAME_TIMEOUT = 3f;

        // ─── Fresh frame thresholds ────────────────────────────────────────

        // see livekit-unity-lifecycle/IMPL_REF.md §10 / video-publish skill §6
        [Header("Fresh frame thresholds")]
        [Tooltip("GeminiOnly 档 stale 阈值（秒，宽松）。see IMPL_REF.md §10")]
        [Min(0f)] public float STALE_FRAME_THRESHOLD_LOW_TIER = 2f;

        // see livekit-unity-lifecycle/IMPL_REF.md §10
        [Tooltip("FULL 档 stale 阈值（秒，严格）。see IMPL_REF.md §10")]
        [Min(0f)] public float STALE_FRAME_THRESHOLD_HIGH_TIER = 0.5f;

        // ─── Snapshot & ByteStream ─────────────────────────────────────────

        // see livekit-unity-lifecycle/IMPL_REF.md §10 / spike S3
        [Header("Snapshot & ByteStream")]
        [Tooltip("大于此 byte 数的图片走 ByteStream/SendFile，否则走 RPC。see IMPL_REF.md §10 / spike S3")]
        [Min(1024)] public int BYTESTREAM_RPC_THRESHOLD_BYTES = 15360;

        // see livekit-unity-lifecycle/IMPL_REF.md §10 / spike S3 S4
        [Tooltip("captureSnapshot 默认宽（像素）。see IMPL_REF.md §10 / spike S3 S4")]
        [Min(64)] public int SNAPSHOT_DEFAULT_WIDTH = 480;

        // see livekit-unity-lifecycle/IMPL_REF.md §10 / spike S3 S4
        [Tooltip("captureSnapshot 默认高（像素）。see IMPL_REF.md §10 / spike S3 S4")]
        [Min(64)] public int SNAPSHOT_DEFAULT_HEIGHT = 270;

        // see livekit-unity-lifecycle/IMPL_REF.md §10
        [Tooltip("captureSnapshot JPEG 压缩质量（0–100）。see IMPL_REF.md §10")]
        [Range(1, 100)] public int SNAPSHOT_JPEG_QUALITY = 75;

        // ─── Publish options ───────────────────────────────────────────────

        // see livekit-unity-lifecycle/IMPL_REF.md §10 / video-publish skill 陷阱 #15
        [Header("Publish options")]
        [Tooltip("Simulcast 默认；A10 上线后 spike 决定。see IMPL_REF.md §10 / video-publish 陷阱 #15")]
        public bool SIMULCAST_DEFAULT = false;

        // ──────────────────────────────────────────────────────────────────

        /// <summary>
        /// 在 awake-time 做一次合法性自检。任何字段越界都按默认值复位并打 warning，
        /// 避免 spike 期手抖把 cool-down 设成 0 引发 livekit/livekit #854 abandoned publish。
        /// </summary>
        private void OnValidate()
        {
            ClampMin(ref T_TIER_COOLDOWN, 1f, nameof(T_TIER_COOLDOWN),
                "cool-down < 1s 会触发 abandoned publish (livekit/livekit #854)");
            ClampMin(ref T_DISCONNECT_WAIT_HARD, 1f, nameof(T_DISCONNECT_WAIT_HARD),
                "Disconnect 软超时 < 1s 会让 watchdog 退路失效");
            ClampMin(ref T_SHUTDOWN_COOLDOWN, 1f, nameof(T_SHUTDOWN_COOLDOWN),
                "shutdown cool-down < 1s 会引发 identity 抢占");
            ClampMin(ref T_HEARTBEAT_INTERVAL, 0.5f, nameof(T_HEARTBEAT_INTERVAL),
                "heartbeat 频率 < 0.5s 会浪费 reliable DataChannel 带宽");
            if (T_HEARTBEAT_SOFT >= T_HEARTBEAT_HARD)
            {
                Debug.LogWarning(
                    "[ParrotLifecycleConfig] T_HEARTBEAT_SOFT ≥ T_HEARTBEAT_HARD —— soft 必须严格小于 hard，已强制 soft = hard / 2。");
                T_HEARTBEAT_SOFT = T_HEARTBEAT_HARD / 2f;
            }
        }

        private static void ClampMin(ref float value, float floor, string name, string reason)
        {
            if (value < floor)
            {
                Debug.LogWarning(
                    $"[ParrotLifecycleConfig] {name}={value} < {floor} —— {reason}. 已复位为 {floor}.");
                value = floor;
            }
        }
    }
}
