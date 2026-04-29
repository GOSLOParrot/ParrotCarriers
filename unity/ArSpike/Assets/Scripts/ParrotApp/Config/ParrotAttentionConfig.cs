using UnityEngine;

namespace ParrotApp.Config
{
    /// <summary>
    /// Sprint4 Phase 4 W6-7 attention 阈值菜单（Focus / BBox 累加权重 + 阈值 + TTL）。
    ///
    /// <b>设计来源</b>：<c>architecture/sprint4_phase4_entry_20260430.md §8.1 L9</c>
    /// (锁定起步数值 0.2 / 1.0 / 1.0 / 30.0) + <c>parrot/dsg/attention/threshold.py</c>
    /// (Brain 端 <c>FocusBboxThreshold</c> 消费这些值)。
    ///
    /// <b>Brain 端读取路径</b>：本 SO 在 <c>RoomManager.OnConnected</c>（含 reconnect /
    /// Brain 管线切换）时由 <c>AttentionConfigEchoPublisher</c> 通过 EcpEvent
    /// <c>attention.config.echo</c> 发到 Brain；Brain 端 <c>attention_config_handler</c>
    /// 写 BB <c>global/attention_thresholds</c>。
    ///
    /// <b>F-05 prerequisite chain（用户 sign off 后）</b>：
    /// <list type="number">
    /// <item>① Unity SO + EchoPublisher → publish EcpEvent（本类 + EchoPublisher 落地）</item>
    /// <item>② Brain attention_config_handler 收到 → 写 BB global/attention_thresholds（落地）</item>
    /// <item>③ FocusBboxThreshold.__init__ 读 BB 注入构造参数 → <b>本 chat 不做</b>（要改
    ///     <c>dsg/attention/threshold.py</c>，那是 Brain 后续 chat 的 1 行改动）</item>
    /// </list>
    /// 完成 ①+② 后 BB key 已有 producer，从 # CANDIDATE 升级到 producer-wired；
    /// FocusBboxThreshold 仍跑硬编码 DEFAULTS 直到 ③ 落地。
    ///
    /// <b>Wire 格式</b>（与 <c>bb_schema.py:global/attention_thresholds</c> 注释逐字对齐）：
    /// <code>{"delta_focus":0.2,"delta_bbox":1.0,"threshold":1.0,"target_ttl_s":30.0,"schema_version":1}</code>
    ///
    /// <b>不要</b>把这里的字段拆给 BBox/Focus controller 自己持有 —— SO 是 single source
    /// of truth，UI 一律读这里，Brain 端读 BB 镜像；这样 Inspector 改一次两边都同步。
    /// </summary>
    [CreateAssetMenu(
        fileName = "ParrotAttentionConfig",
        menuName = "Parrot/Attention Config",
        order = 51)]
    public class ParrotAttentionConfig : ScriptableObject
    {
        public const int SchemaVersion = 1;

        [Header("Δ weights (entry doc §8.1 L9)")]

        [Tooltip("焦点单次贡献权重（accumulator）。默认 0.2 = 5 次 Focus 累加到 threshold。" +
                 "see entry doc §8.1 L9")]
        [Min(0f)] public float deltaFocus = 0.2f;

        [Tooltip("BBox 单次贡献权重。默认 1.0 = 1 次 BBox 直接 cross threshold（用户主动" +
                 "放置等同'确认'语义）。see entry doc §8.1 L9")]
        [Min(0f)] public float deltaBbox = 1.0f;

        [Header("Threshold")]

        [Tooltip("Brain 端 FocusBboxThreshold 累加 weight ≥ threshold 时 publish " +
                 "attention.threshold.crossed。默认 1.0。see entry doc §8.1 L9")]
        [Min(0.0001f)] public float threshold = 1.0f;

        [Header("TTL")]

        [Tooltip("无新输入时累加 state 的 TTL（秒）；超时该 target 被 Brain 端 evict。" +
                 "默认 30s（'用户注意力 sticky 30s of silence'，Phase 5+ DSG L3 替换）。" +
                 "see entry doc §8.1 L9")]
        [Min(1f)] public float targetTtlSeconds = 30.0f;

        // ─── wire serialization ─────────────────────────────────────

        /// <summary>
        /// 输出与 <c>bb_schema.py:global/attention_thresholds</c> 锁定 schema
        /// 完全一致的 JSON 字面量。<b>不</b>用 JsonUtility（字段命名风格不一致 +
        /// JsonUtility 不支持 default-value 控制），手 roll 5 字段。
        /// </summary>
        public string ToWireJson()
        {
            // InvariantCulture 避免 zh-CN locale 把 0.2 写成 "0,2"
            var ci = System.Globalization.CultureInfo.InvariantCulture;
            return "{"
                + "\"delta_focus\":" + deltaFocus.ToString("R", ci) + ","
                + "\"delta_bbox\":" + deltaBbox.ToString("R", ci) + ","
                + "\"threshold\":" + threshold.ToString("R", ci) + ","
                + "\"target_ttl_s\":" + targetTtlSeconds.ToString("R", ci) + ","
                + "\"schema_version\":" + SchemaVersion
                + "}";
        }

        // ─── inspector self-checks ──────────────────────────────────

        private void OnValidate()
        {
            if (threshold <= 0f)
            {
                Debug.LogWarning(
                    "[ParrotAttentionConfig] threshold ≤ 0 makes accumulator meaningless; clamping to 0.0001");
                threshold = 0.0001f;
            }
            if (deltaBbox > 0f && deltaBbox > threshold * 5f)
            {
                Debug.LogWarning(
                    $"[ParrotAttentionConfig] deltaBbox ({deltaBbox}) >> threshold ({threshold}); " +
                    "BBox will always cross immediately and dominate Focus accumulator. " +
                    "Intentional? entry doc §8.1 L9 default ratio 5×.");
            }
            if (targetTtlSeconds < 1f)
            {
                Debug.LogWarning(
                    "[ParrotAttentionConfig] targetTtlSeconds < 1s clamped to 1s (eviction would race ingest)");
                targetTtlSeconds = 1f;
            }
        }
    }
}
