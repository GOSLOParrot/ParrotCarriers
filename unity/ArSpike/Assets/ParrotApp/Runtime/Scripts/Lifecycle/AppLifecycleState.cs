namespace ParrotApp.Lifecycle
{
    /// <summary>
    /// Sprint4 Phase 3 客户端 11 状态生命周期 FSM。
    ///
    /// 所有 transition 规则与触发条件见
    /// <c>.cursor/skills/livekit-unity-lifecycle/IMPL_REF.md §1</c>。
    ///
    /// <b>不允许误读</b>：
    /// <list type="bullet">
    /// <item>这是 <b>Unity 端</b> FSM，<b>不</b>暴露给后端 BT / Scheduler。
    ///   后端通过 <c>EcpState.app_lifecycle_state</c> 字符串感知，自决策。</item>
    /// <item>不能依据本枚举派生后端行为分支；后端只看
    ///   <c>ConnectionHealthState.overall</c> 4 态聚合 +
    ///   <c>connection.health.changed</c> 事件。</item>
    /// </list>
    /// </summary>
    public enum AppLifecycleState
    {
        /// <summary>进程刚启动，尚未取得任何运行时上下文。</summary>
        ColdStart,

        /// <summary>等用户授权（相机 / 麦克风 / 网络）。</summary>
        PermissionGate,

        /// <summary>等业务后端发 join token。</summary>
        TokenGate,

        /// <summary>AR Foundation 拉起 ARSession，等到 <c>SessionTracking</c>。</summary>
        ArSessionStarting,

        /// <summary>正在向 LiveKit 连接（或重连主路径）。</summary>
        Connecting,

        /// <summary>Room 信令已连接，等首帧 / Brain join / RPC ready。</summary>
        Connected,

        /// <summary>正常运行中。</summary>
        Running,

        /// <summary><c>OnApplicationPause(true)</c> 后短背景防抖窗（≤ T_SHORT_BG）。</summary>
        ShortBackground,

        /// <summary>长背景（T_SHORT_BG ≤ now-pause &lt; T_LONG_BG）；上报 degraded，但不强切。</summary>
        LongBackground,

        /// <summary>SDK Reconnecting 或 watchdog 触发；等结果。</summary>
        Reconnecting,

        /// <summary>媒体单轨失败 / stale / VAD 异常等可观测降级，仍保持连接。</summary>
        Degraded,

        /// <summary>正在执行 graceful shutdown chokepoint。</summary>
        ShuttingDown,

        /// <summary>断开终态；新 Connect 必须从 ColdStart 重走。</summary>
        Disconnected,
    }

    /// <summary>
    /// 状态字符串化 helper。EcpState 周期上报里 <c>app_lifecycle_state</c> 字段
    /// 用 snake_case 字符串（与 Python <c>EcpState</c> 模型对齐），不要直接用 enum.ToString()。
    /// </summary>
    public static class AppLifecycleStateNames
    {
        public const string ColdStart = "cold_start";
        public const string PermissionGate = "permission_gate";
        public const string TokenGate = "token_gate";
        public const string ArSessionStarting = "ar_session_starting";
        public const string Connecting = "connecting";
        public const string Connected = "connected";
        public const string Running = "running";
        public const string ShortBackground = "short_background";
        public const string LongBackground = "long_background";
        public const string Reconnecting = "reconnecting";
        public const string Degraded = "degraded";
        public const string ShuttingDown = "shutting_down";
        public const string Disconnected = "disconnected";

        public static string ToWireString(AppLifecycleState state)
        {
            switch (state)
            {
                case AppLifecycleState.ColdStart:         return ColdStart;
                case AppLifecycleState.PermissionGate:    return PermissionGate;
                case AppLifecycleState.TokenGate:         return TokenGate;
                case AppLifecycleState.ArSessionStarting: return ArSessionStarting;
                case AppLifecycleState.Connecting:        return Connecting;
                case AppLifecycleState.Connected:         return Connected;
                case AppLifecycleState.Running:           return Running;
                case AppLifecycleState.ShortBackground:   return ShortBackground;
                case AppLifecycleState.LongBackground:    return LongBackground;
                case AppLifecycleState.Reconnecting:      return Reconnecting;
                case AppLifecycleState.Degraded:          return Degraded;
                case AppLifecycleState.ShuttingDown:      return ShuttingDown;
                case AppLifecycleState.Disconnected:      return Disconnected;
                default:                                  return "unknown";
            }
        }
    }
}
