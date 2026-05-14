using System;
using ParrotApp.Config;
using ParrotApp.Health;
using UnityEngine;

namespace ParrotApp.Lifecycle
{
    /// <summary>
    /// Sprint4 Phase 3 客户端生命周期 FSM 中枢。
    ///
    /// <b>本类不直接调用 LiveKit SDK</b>：
    /// <list type="bullet">
    /// <item>RoomManager / 视频 / 音频 / RPC 等组件通过 <see cref="ReportRoom..."/>
    ///   等 setter 把外部信号灌进来；本类负责状态推演 + 触发回调。</item>
    /// <item>graceful shutdown chokepoint（IMPL_REF.md §2）由
    ///   <c>LifecycleShutdownService</c> 单独执行；本类只负责<b>进入 / 退出</b>
    ///   <see cref="AppLifecycleState.ShuttingDown"/> 状态。</item>
    /// </list>
    ///
    /// <b>FSM 规则源</b>：<c>.cursor/skills/livekit-unity-lifecycle/IMPL_REF.md §1.1</c>。
    ///
    /// <b>设计立场</b>：FSM 只在 Unity 端，不暴露 enum 给后端 BT。后端通过
    /// <c>EcpState.app_lifecycle_state</c> 字符串感知，自决策。
    /// </summary>
    public class AppLifecycleManager : MonoBehaviour
    {
        [Tooltip("ScriptableObject 阈值表；不挂时会创建一个临时实例（spike 期容错）。")]
        [SerializeField] private ParrotLifecycleConfig config;

        [Tooltip("Editor 每帧 OnGUI 输出当前状态，方便单独跑场景调试。")]
        [SerializeField] private bool verboseEditorLog = false;

        public AppLifecycleState CurrentState { get; private set; } = AppLifecycleState.ColdStart;

        /// <summary>
        /// 全局健康聚合器；ParrotApp 子组件通过这个 reference 上报字段。
        /// 见 <see cref="HealthAggregator"/>。
        /// </summary>
        public ConnectionHealthAggregator HealthAggregator { get; private set; }

        public ParrotLifecycleConfig Config => config;

        public event Action<AppLifecycleState, AppLifecycleState> OnStateChanged;

        // 后台时间戳；进 ShortBackground 时记录，用于 T_SHORT_BG / T_LONG_BG 比对
        private double _pauseUnix = 0.0;

        // R3 修复：Pause(true) 之前的 state，让 Pause(false) 知道该回 Connected
        // 还是回到 PreConnect 阶段（如 TokenGate / ArSessionStarting）。
        private AppLifecycleState _statePriorToPause = AppLifecycleState.ColdStart;

        // 防 re-entrant 重复 transition（OnApplicationPause 在 Editor 行为不一致）
        private bool _processingPause = false;

        private static double UnixSeconds()
            => (DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalSeconds;

        // ─── lifecycle ────────────────────────────────────────────────────

        protected virtual void Awake()
        {
            if (config == null)
            {
                Debug.LogWarning(
                    "[AppLifecycleManager] 未挂 ParrotLifecycleConfig — 用临时默认实例。" +
                    "正式运行前请通过 Tools/Parrot/Lifecycle Tuning 创建一份 asset。");
                config = ScriptableObject.CreateInstance<ParrotLifecycleConfig>();
            }
            HealthAggregator = new ConnectionHealthAggregator();
        }

        protected virtual void Update()
        {
            // 只有 ShortBackground 需要按时间晋升
            if (CurrentState == AppLifecycleState.ShortBackground
                || CurrentState == AppLifecycleState.LongBackground)
            {
                double elapsed = UnixSeconds() - _pauseUnix;
                if (CurrentState == AppLifecycleState.ShortBackground && elapsed >= config.T_SHORT_BG)
                {
                    Transition(AppLifecycleState.LongBackground, "T_SHORT_BG elapsed");
                }
                else if (CurrentState == AppLifecycleState.LongBackground && elapsed >= config.T_LONG_BG)
                {
                    Transition(AppLifecycleState.ShuttingDown, "T_LONG_BG elapsed (graceful)");
                }
            }
        }

        /// <summary>
        /// R3 + R4 修复：
        /// <list type="bullet">
        /// <item><b>R3</b>：Pause(true) 不再只覆盖"已连接族"。
        ///   <c>PermissionGate / TokenGate / ArSessionStarting / Connecting</c>
        ///   切到后台时也必须刷 <see cref="_pauseUnix"/> 并进
        ///   <see cref="AppLifecycleState.ShortBackground"/>，否则真机切微信回来 AR session
        ///   被系统回收却没有任何降级信号。<br/>
        ///   只有终态（<c>Disconnected / ShuttingDown</c>）和 <c>ColdStart</c>
        ///   不需要进后台跟踪。</item>
        /// <item><b>R4</b>：iOS 默认 <c>Run In Background = false</c>，<see cref="Update"/>
        ///   在后台不跑，<c>T_LONG_BG</c> 永远等不到。在 Pause(false) 入口主动校验
        ///   elapsed ≥ <c>T_LONG_BG</c>，直接推 <c>ShuttingDown</c>，避免被动等
        ///   LiveKit 服务端 ~180s timeout。</item>
        /// <item>Resume 时根据 <see cref="_statePriorToPause"/> 决定回 <c>Connected</c>
        ///   还是回到原本的 PreConnect 状态，让 token gate / connect 流程能续上。</item>
        /// </list>
        /// </summary>
        protected virtual void OnApplicationPause(bool paused)
        {
            if (_processingPause) return;
            _processingPause = true;
            try
            {
                if (paused)
                {
                    if (IsTerminalOrColdStart(CurrentState)) return;

                    // 只有"首次进入后台"才记 _pauseUnix；OS 重复 Pause(true) 不刷新计时
                    if (CurrentState != AppLifecycleState.ShortBackground
                        && CurrentState != AppLifecycleState.LongBackground)
                    {
                        _pauseUnix = UnixSeconds();
                        _statePriorToPause = CurrentState;
                        Transition(AppLifecycleState.ShortBackground, "OnApplicationPause(true)");
                    }
                }
                else
                {
                    double elapsed = _pauseUnix > 0 ? UnixSeconds() - _pauseUnix : 0.0;

                    // R4: 不依赖 Update() 在后台 tick；resume 时主动判超时
                    if (_pauseUnix > 0
                        && elapsed >= config.T_LONG_BG
                        && !IsTerminalOrColdStart(CurrentState))
                    {
                        Transition(AppLifecycleState.ShuttingDown,
                            $"OnApplicationPause(false) elapsed={elapsed:F1}s >= T_LONG_BG (R4 background-tick fallback)");
                        _pauseUnix = 0.0;
                        return;
                    }

                    if (CurrentState == AppLifecycleState.ShortBackground)
                    {
                        Transition(NextStateAfterShortBackground(),
                            "OnApplicationPause(false) within short_bg");
                    }
                    else if (CurrentState == AppLifecycleState.LongBackground)
                    {
                        Transition(NextStateAfterLongBackground(),
                            "OnApplicationPause(false) after long_bg");
                    }
                    // ShuttingDown / Disconnected：不会因 resume 自动回来，等外部 Connect()
                    _pauseUnix = 0.0;
                }
            }
            finally
            {
                _processingPause = false;
            }
        }

        private static bool IsTerminalOrColdStart(AppLifecycleState s)
            => s == AppLifecycleState.Disconnected
               || s == AppLifecycleState.ShuttingDown
               || s == AppLifecycleState.ColdStart;

        private static bool IsConnectedFamily(AppLifecycleState s)
            => s == AppLifecycleState.Running
               || s == AppLifecycleState.Connected
               || s == AppLifecycleState.Degraded
               || s == AppLifecycleState.Reconnecting;

        /// <summary>
        /// 短后台恢复：连接族 → Connected（等首帧 → Running 由外部 Report 推进）；
        /// PreConnect 族 → 还原原状态，让 token / permission / connecting 流程续上。
        /// </summary>
        private AppLifecycleState NextStateAfterShortBackground()
        {
            if (IsConnectedFamily(_statePriorToPause))
                return AppLifecycleState.Connected;
            // PreConnect 族（PermissionGate / TokenGate / ArSessionStarting / Connecting）
            // 还原原状态。priorToPause 若是默认 ColdStart，回到 Connected 兜底。
            if (_statePriorToPause == AppLifecycleState.ColdStart)
                return AppLifecycleState.Connected;
            return _statePriorToPause;
        }

        /// <summary>
        /// 长后台恢复：连接族 → Reconnecting；PreConnect 族 → 仍然恢复原状态
        /// （token gate 等待时间不该转成 reconnecting）。
        /// </summary>
        private AppLifecycleState NextStateAfterLongBackground()
        {
            if (IsConnectedFamily(_statePriorToPause))
                return AppLifecycleState.Reconnecting;
            if (_statePriorToPause == AppLifecycleState.ColdStart)
                return AppLifecycleState.Reconnecting;
            return _statePriorToPause;
        }

        // ─── 公开 transition 入口（外部信号） ────────────────────────────

        public void EnterPermissionGate() => Transition(AppLifecycleState.PermissionGate, "permission_required");
        public void EnterTokenGate()      => Transition(AppLifecycleState.TokenGate, "token_required");
        public void EnterArSessionStarting()
            => Transition(AppLifecycleState.ArSessionStarting, "ar_session_starting");
        public void EnterConnecting()     => Transition(AppLifecycleState.Connecting, "Connect()");

        /// <summary>RoomManager 报告 Connected 后调用。</summary>
        public void ReportRoomConnected()
        {
            HealthAggregator.ReportRoomConnected(true, UnixSeconds());
            if (CurrentState == AppLifecycleState.Connecting
                || CurrentState == AppLifecycleState.Reconnecting)
            {
                Transition(AppLifecycleState.Connected, "Room.Connected");
            }
        }

        /// <summary>所有就绪条件都满足后（Brain present + RPC ready + first frame）调用。</summary>
        public void ReportRunning()
        {
            if (CurrentState == AppLifecycleState.Connected
                || CurrentState == AppLifecycleState.Reconnecting
                || CurrentState == AppLifecycleState.Degraded)
            {
                Transition(AppLifecycleState.Running, "first_frame + brain_present + rpc_ready");
            }
        }

        /// <summary>媒体 / RPC / VAD 出现可观测降级。</summary>
        public void ReportDegraded(string reason)
        {
            if (CurrentState == AppLifecycleState.Running
                || CurrentState == AppLifecycleState.Connected
                || CurrentState == AppLifecycleState.Reconnecting
                || CurrentState == AppLifecycleState.Connecting
                || CurrentState == AppLifecycleState.ArSessionStarting
                || CurrentState == AppLifecycleState.TokenGate)
            {
                Transition(AppLifecycleState.Degraded, $"degraded:{reason}");
            }
        }

        /// <summary>SDK Reconnecting 或 watchdog 软超时。</summary>
        public void ReportReconnecting(string reason)
        {
            if (CurrentState != AppLifecycleState.ShuttingDown
                && CurrentState != AppLifecycleState.Disconnected)
            {
                Transition(AppLifecycleState.Reconnecting, $"reconnecting:{reason}");
            }
        }

        /// <summary>Room.Disconnected event / 用户主动断 / 长背景超时。</summary>
        public void ReportShuttingDown(string reason)
        {
            if (CurrentState != AppLifecycleState.Disconnected)
            {
                Transition(AppLifecycleState.ShuttingDown, $"shutdown:{reason}");
            }
        }

        /// <summary>graceful shutdown chokepoint 完成（cool-down 也跑完）。</summary>
        public void ReportDisconnected(string reason)
        {
            HealthAggregator.ReportRoomConnected(false, UnixSeconds());
            HealthAggregator.ReportBrainPresent(false, UnixSeconds());
            Transition(AppLifecycleState.Disconnected, $"disconnected:{reason}");
        }

        // ─── 核心 transition ─────────────────────────────────────────────

        private void Transition(AppLifecycleState next, string reason)
        {
            if (CurrentState == next) return;

            var prev = CurrentState;
            CurrentState = next;

            if (verboseEditorLog && Application.isEditor)
                Debug.Log($"[AppLifecycle] {prev} → {next} ({reason})");

            try
            {
                OnStateChanged?.Invoke(prev, next);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[AppLifecycle] OnStateChanged listener threw: {ex}");
            }
        }
    }
}
