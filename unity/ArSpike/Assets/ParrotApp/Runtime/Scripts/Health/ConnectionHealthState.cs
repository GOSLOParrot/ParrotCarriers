using System;

namespace ParrotApp.Health
{
    /// <summary>
    /// 4 态聚合，来自 IMPL_REF.md §4.1。Brain / Gemini 只看这一个字段，
    /// 不要让后端推断 11 个 lifecycle 子状态。
    /// </summary>
    public enum ConnectionOverall
    {
        Unknown,
        Healthy,
        Degraded,
        Unhealthy,
    }

    public static class ConnectionOverallNames
    {
        public const string Unknown = "unknown";
        public const string Healthy = "healthy";
        public const string Degraded = "degraded";
        public const string Unhealthy = "unhealthy";

        public static string ToWireString(ConnectionOverall overall)
        {
            switch (overall)
            {
                case ConnectionOverall.Healthy:   return Healthy;
                case ConnectionOverall.Degraded:  return Degraded;
                case ConnectionOverall.Unhealthy: return Unhealthy;
                default:                          return Unknown;
            }
        }
    }

    /// <summary>
    /// IMPL_REF.md §4.2 的 producer 分工的"快照"形式。
    ///
    /// <b>这是值类型快照，不是状态机</b>：
    /// 由 <c>ConnectionHealthAggregator</c> 在每次任意子字段变化时整体重建。
    /// Heartbeat / EcpState 周期上报时直接拷贝当前 snapshot 到 wire payload。
    ///
    /// <b>single-producer-per-field 约束</b>：
    /// 不要让两个组件同时调 <see cref="ConnectionHealthAggregator"/> 的同一个 setter。
    /// IMPL_REF.md §4.2 表已经为每个字段指定了唯一 producer。
    /// </summary>
    [Serializable]
    public struct ConnectionHealthState
    {
        // ─── Room / signaling ────────────────────────────────────────────
        public bool RoomConnected;
        public bool BrainPresent;
        public bool RpcReady;
        public bool DataChannelReady;

        // ─── Audio publish ───────────────────────────────────────────────
        public bool AudioPublishAttempted;
        public bool AudioPublished;
        public string AudioLastError;

        // ─── Video publish ───────────────────────────────────────────────
        public bool VideoPublishAttempted;
        public bool VideoPublished;
        public bool VideoFirstFrame;
        public bool VideoFreshFrame;
        public string VideoTier;
        public string VideoLifecycleReason;     // paused_arcore / lifecycle_background / ...

        // ─── AR ──────────────────────────────────────────────────────────
        public string ArTrackingState;          // SessionTracking / Limited / None / ...

        // ─── Reconnect counters ──────────────────────────────────────────
        public int ReconnectAttemptCount;
        public double LastDisconnectedAt;       // unix seconds; 0 means never

        // ─── Aggregate ───────────────────────────────────────────────────
        public ConnectionOverall Overall;
        public double LastStateChangeAt;        // unix seconds

        /// <summary>
        /// IMPL_REF.md §4.1 决策表的可执行版本。
        ///
        /// <b>R5 修复（VIDEO_OFF tier 不强制要求 fresh frame）</b>：<br/>
        /// <c>VIDEO_OFF</c> 是 Brain 主动选择的合法档位（语音对话模式 / 省流量），
        /// 不是降级。原本无条件要求 <see cref="VideoFreshFrame"/> 会让 OFF tier
        /// 永远落到 <see cref="ConnectionOverall.Degraded"/>，并触发假
        /// <c>connection.health.changed</c> 事件，让 Brain 误判媒体出问题。<br/>
        /// 空字符串档位 ("" — 还没上报)<b>仍</b>视为"期待视频活跃"，避免冷启动期
        /// 在视频未起时 Aggregator 提前给出 Healthy。
        /// </summary>
        public static ConnectionOverall ComputeOverall(in ConnectionHealthState s)
        {
            if (!s.RoomConnected || !s.BrainPresent)
                return ConnectionOverall.Unhealthy;

            bool videoExpectedActive =
                !string.Equals(s.VideoTier, "VIDEO_OFF", StringComparison.Ordinal);
            bool videoOk = !videoExpectedActive || s.VideoFreshFrame;

            if (s.RpcReady && videoOk && s.AudioPublished)
                return ConnectionOverall.Healthy;

            // degraded: 信令/transport 在线，但媒体或 RPC 有缺
            if (s.RpcReady || s.DataChannelReady)
                return ConnectionOverall.Degraded;

            // 信令在线但 RPC 都没起：仍叫 unknown 而不是 healthy/degraded —
            // 给冷启动 / pause-resume 过渡期一个合法位置。
            return ConnectionOverall.Unknown;
        }

        public ConnectionHealthState WithOverall(ConnectionOverall o, double nowUnix)
        {
            var s = this;
            s.Overall = o;
            s.LastStateChangeAt = nowUnix;
            return s;
        }

        /// <summary>初始全零快照，<c>Overall = Unknown</c>。</summary>
        public static ConnectionHealthState Initial()
        {
            return new ConnectionHealthState
            {
                Overall = ConnectionOverall.Unknown,
                AudioLastError = "",
                VideoTier = "",
                VideoLifecycleReason = "",
                ArTrackingState = "",
            };
        }
    }
}
