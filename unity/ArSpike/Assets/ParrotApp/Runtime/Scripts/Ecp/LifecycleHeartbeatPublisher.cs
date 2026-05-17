using System;
using ParrotApp.Config;
using ParrotApp.Health;
using ParrotApp.Lifecycle;
using ParrotApp.Parrot;
using UnityEngine;

namespace ParrotApp.Ecp
{
    /// <summary>
    /// 周期 EcpState 上行 + connection.health.changed 事件触发的统一宿主。
    /// 设计来源：<c>.cursor/skills/livekit-unity-lifecycle/IMPL_REF.md §3 / §4 / §9</c>。
    ///
    /// <b>不直接调 LiveKit SDK</b>：
    /// 通过 <see cref="IHeartbeatTransport"/> 发包；真实 transport（Reliable
    /// DataChannel / ParticipantAttributes）在 LiveKit SDK 进入 ArSpike 后落地。
    /// 默认绑定 <see cref="LogHeartbeatTransport"/>，让骨架可单独跑。
    ///
    /// <b>spike S7 之前不要选 ParticipantAttributes</b>：见 IMPL_REF.md §8。
    ///
    /// <b>Sprint4 Phase 4 W3.A.3 — 双触发 EcpState（事件驱动 + 1Hz 全量心跳）</b>
    /// （entry doc §8.1 L1 锁定）：
    /// <list type="bullet">
    /// <item>1Hz 全量心跳保留：Update tick 走 <see cref="SendHeartbeat"/>，
    ///   即使无变化也每秒 1 次（Brain ingest 接通后用作 keep-alive）</item>
    /// <item>事件触发：订阅 <see cref="AnimationDriver"/> 的 producer events
    ///   <c>OnBodyStateWireChanged</c> / <c>OnHeadStateWireChanged</c>，
    ///   外部通过 <see cref="ReportActiveCommand"/> / <see cref="ClearActiveCommand"/>
    ///   注入 active_command_id / active_locks 变化 → 立即调 SendHeartbeat</item>
    /// <item>去重：每次发包前比对 sig = body|head|cogn|locks|cmd；同一帧内
    ///   多 producer fire 落入 <c>MinSendIntervalSeconds</c> = 50ms 的合并窗口</item>
    /// <item>sequence_id 单调递增：Brain ingest 接通后 (unity_identity, sequence_id)
    ///   做去重 key</item>
    /// <item>chokepoint 保护、intent.disconnect 触发、health.changed 节流——
    ///   全部 Phase 3 R1-R6+D5 audit 通过的防御性结构保留不动</item>
    /// </list>
    ///
    /// <b>cognitive_state</b>：Unity 永远填 ""，由 Brain
    /// <c>cognitive_state_tracker</c>（Gemini agent_state_changed）直接写
    /// BB <c>tick/cognitive_state</c>。EcpState wire 字段保留只是 schema
    /// 完整性。
    ///
    /// <b>GAP-1（W3.A.2 commit 已记录）</b>：当前 Brain 端没有消费
    /// <c>parrot.ecp.state</c> topic 写入 BB tick keys 的 ingest，本类按
    /// 规范上行的字段 Brain 端暂时不会落 BB。验收 3 的 LLM-surface 待
    /// Brain ingest chat 接通后才能闭合；本类提供的 wire 字段 + sequence_id
    /// 是为那时准备好的契约。
    /// </summary>
    [RequireComponent(typeof(AppLifecycleManager))]
    public class LifecycleHeartbeatPublisher : MonoBehaviour
    {
        [Tooltip("空时使用 LogHeartbeatTransport（仅打印），LiveKit transport 上线后通过代码注入。")]
        [SerializeField] private bool useLogTransportInEditor = true;

        [Tooltip("body/head wire producer。空时 Awake 兜底 FindObjectOfType<AnimationDriver>。")]
        [SerializeField] private AnimationDriver animationDriver;

        public IHeartbeatTransport Transport { get; set; }
        public string UnityIdentity { get; set; } = "";
        public string RoomId { get; set; } = "";

        /// <summary>
        /// 静态访问点，让 <see cref="ParrotApp.RPC.ParrotRpcHandler"/> 等外部
        /// producer 在 RPC handler 进出时调 <see cref="ReportActiveCommand"/> /
        /// <see cref="ClearActiveCommand"/>，不需要满天飞 GetComponent。
        /// </summary>
        public static LifecycleHeartbeatPublisher Instance { get; private set; }

        private AppLifecycleManager _lifecycle;
        private ParrotLifecycleConfig Config => _lifecycle != null ? _lifecycle.Config : null;
        private float _nextSendAt = 0f;

        // 节流"connection.health.changed"事件：抖动期 1s 最多发一次
        private float _lastHealthEventAt = 0f;
        private ConnectionOverall _lastHealthOverall = ConnectionOverall.Unknown;
        private const float HealthEventMinIntervalSeconds = 1f;

        // ─── A.3 三态 + active command 缓存 + 去重节流 ───────────────────

        private string _bodyStateWire = "idle";
        private string _headStateWire = "HEAD_FORWARD";
        // cognitive 不在 Unity 改动；EcpState wire 字段永远 ""，由 Brain BB 管。
        private string _activeCommandId = "";
        private string[] _activeLocks = Array.Empty<string>();
        private long _sequenceId = 0;

        // 重入 + 同帧合并：事件回调 + 1Hz tick 都可能进 SendHeartbeat
        private bool _sending = false;
        private string _lastSentSignature = "";
        private float _lastSentAtUnscaled = 0f;
        private AnimationDriver _subscribedAnimationDriver;
        private float _nextAnimationDriverBindAt = 0f;
        // 同一 frame 内多 producer event 合并到一条；1Hz tick 间隔 = 1000ms 远 > 50ms 不影响
        private const float MinSendIntervalSeconds = 0.05f;
        private const float AnimationDriverBindRetrySeconds = 0.5f;

        protected virtual void Awake()
        {
            _lifecycle = GetComponent<AppLifecycleManager>();
            if (Transport == null && useLogTransportInEditor)
                Transport = new LogHeartbeatTransport();

            if (animationDriver == null)
                animationDriver = FindObjectOfType<AnimationDriver>();

            // Singleton — 同场景只允许一个 publisher。Awake 早于 OnEnable 执行，
            // OnEnable 才订阅事件，Instance 在订阅之前就位是安全顺序。
            if (Instance != null && Instance != this)
            {
                Debug.LogWarning(
                    "[LifecycleHeartbeatPublisher] Duplicate publisher detected — " +
                    "destroying the new one to keep RPC handler ReportActiveCommand 1:1.");
                Destroy(this);
                return;
            }
            Instance = this;
        }

        protected virtual void OnDestroy()
        {
            UnbindAnimationDriver();
            if (Instance == this) Instance = null;
        }

        protected virtual void OnEnable()
        {
            if (_lifecycle != null)
            {
                _lifecycle.OnStateChanged += HandleLifecycleChanged;
                if (_lifecycle.HealthAggregator != null)
                    _lifecycle.HealthAggregator.OnChanged += HandleHealthChanged;
            }

            EnsureAnimationDriverBound();
        }

        protected virtual void OnDisable()
        {
            if (_lifecycle != null)
            {
                _lifecycle.OnStateChanged -= HandleLifecycleChanged;
                if (_lifecycle.HealthAggregator != null)
                    _lifecycle.HealthAggregator.OnChanged -= HandleHealthChanged;
            }
            UnbindAnimationDriver();
        }

        protected virtual void Update()
        {
            if (Transport == null || _lifecycle == null || Config == null) return;
            EnsureAnimationDriverBound();

            if (_lifecycle.CurrentState == AppLifecycleState.Disconnected
                || _lifecycle.CurrentState == AppLifecycleState.ShuttingDown
                || _lifecycle.CurrentState == AppLifecycleState.ColdStart)
            {
                return;
            }

            if (Time.unscaledTime >= _nextSendAt)
            {
                SendHeartbeatTick();
                _nextSendAt = Time.unscaledTime + Config.T_HEARTBEAT_INTERVAL;
            }
        }

        // ─── public producer-injection API ──────────────────────────────

        /// <summary>
        /// 由 RPC handler / Intent 入口 在命令开始执行时调一次。
        /// active_command_id 或 active_locks 任一变化触发立即上报。
        /// </summary>
        public void ReportActiveCommand(string commandId, string[] locks)
        {
            string newCmd = commandId ?? "";
            string[] newLocks = locks ?? Array.Empty<string>();
            if (_activeCommandId == newCmd && LocksEqual(_activeLocks, newLocks)) return;
            _activeCommandId = newCmd;
            _activeLocks = newLocks;
            MaybeSendHeartbeat("active_command_set");
        }

        /// <summary>
        /// 命令结束时调；只在 commandId 与当前正在跟踪的一致时清空，
        /// 防止后到的命令抢断后又被前一个的 finally 清错。
        /// </summary>
        public void ClearActiveCommand(string commandId)
        {
            if (_activeCommandId != (commandId ?? "")) return;
            _activeCommandId = "";
            _activeLocks = Array.Empty<string>();
            MaybeSendHeartbeat("active_command_clear");
        }

        /// <summary>
        /// Local Unity producers that do not pass through an RPC ack path can
        /// still surface body state through the same EcpState heartbeat stream.
        /// AnimationDriver remains the preferred producer when present; this is
        /// the formal fallback for local UI controls and non-standard models.
        /// </summary>
        public void ReportBodyState(string bodyStateWire)
        {
            string normalized = string.IsNullOrWhiteSpace(bodyStateWire)
                ? "idle"
                : bodyStateWire.Trim();
            if (_bodyStateWire == normalized) return;
            _bodyStateWire = normalized;
            MaybeSendHeartbeat("body_state_external");
        }

        // ─── producer event handlers ─────────────────────────────────────

        private void HandleBodyStateWire(string wire)
        {
            if (_bodyStateWire == wire) return;
            _bodyStateWire = wire ?? "";
            MaybeSendHeartbeat("body_state_change");
        }

        private void HandleHeadStateWire(string wire)
        {
            if (_headStateWire == wire) return;
            _headStateWire = wire ?? "";
            MaybeSendHeartbeat("head_state_change");
        }

        private void EnsureAnimationDriverBound()
        {
            if (_subscribedAnimationDriver != null && animationDriver == _subscribedAnimationDriver)
                return;

            if (_subscribedAnimationDriver != null)
                UnbindAnimationDriver();

            if (animationDriver == null)
            {
                if (Time.unscaledTime < _nextAnimationDriverBindAt)
                    return;
                _nextAnimationDriverBindAt = Time.unscaledTime + AnimationDriverBindRetrySeconds;
                animationDriver = FindObjectOfType<AnimationDriver>();
            }
            if (animationDriver == null)
                return;

            animationDriver.OnBodyStateWireChanged += HandleBodyStateWire;
            animationDriver.OnHeadStateWireChanged += HandleHeadStateWire;
            _subscribedAnimationDriver = animationDriver;

            _bodyStateWire = AnimationDriver.BodyStateToWire(animationDriver.CurrentState);
            _headStateWire = AnimationDriver.HeadStateToWire(animationDriver.CurrentHeadState);
            MaybeSendHeartbeat("animation_driver_bound");
        }

        private void UnbindAnimationDriver()
        {
            if (_subscribedAnimationDriver == null)
                return;

            _subscribedAnimationDriver.OnBodyStateWireChanged -= HandleBodyStateWire;
            _subscribedAnimationDriver.OnHeadStateWireChanged -= HandleHeadStateWire;
            if (animationDriver == _subscribedAnimationDriver)
                animationDriver = null;
            _subscribedAnimationDriver = null;
        }


        // ─── send paths ─────────────────────────────────────────────────

        private void MaybeSendHeartbeat(string trigger)
        {
            if (_sending) return; // 重入锁
            // chokepoint 同步：事件触发期间 lifecycle 在终态 / 启动态也不发
            if (_lifecycle == null
                || _lifecycle.CurrentState == AppLifecycleState.Disconnected
                || _lifecycle.CurrentState == AppLifecycleState.ShuttingDown
                || _lifecycle.CurrentState == AppLifecycleState.ColdStart)
            {
                return;
            }
            if (Transport == null || Config == null) return;

            string sig = ComputeSig();
            float now = Time.unscaledTime;
            if (sig == _lastSentSignature && (now - _lastSentAtUnscaled) < MinSendIntervalSeconds)
            {
                // 同一 sig 50ms 内重复触发：合并为一条（同 frame 多 producer fire 的情况）
                return;
            }

            _sending = true;
            try
            {
                SendHeartbeatInternal(trigger);
                _lastSentSignature = sig;
                _lastSentAtUnscaled = now;
                // 事件触发已发，重置 1Hz 计时器避免立刻又发
                _nextSendAt = now + Config.T_HEARTBEAT_INTERVAL;
            }
            finally { _sending = false; }
        }

        private void SendHeartbeatTick()
        {
            // 1Hz 全量心跳：不参与 sig 去重，但仍走 _sending 重入锁
            if (_sending) return;
            _sending = true;
            try
            {
                SendHeartbeatInternal("tick_1hz");
                _lastSentSignature = ComputeSig();
                _lastSentAtUnscaled = Time.unscaledTime;
            }
            finally { _sending = false; }
        }

        private void SendHeartbeatInternal(string trigger)
        {
            try
            {
                _sequenceId++;
                var snapshot = _lifecycle.HealthAggregator.Snapshot;
                var dto = EcpStateDto.BuildHeartbeat(
                    unityIdentity: UnityIdentity,
                    roomId: RoomId,
                    appLifecycleState: AppLifecycleStateNames.ToWireString(_lifecycle.CurrentState),
                    health: snapshot,
                    videoTier: snapshot.VideoTier,
                    activeCommandId: _activeCommandId,
                    bodyStateWire: _bodyStateWire,
                    headStateWire: _headStateWire,
                    cognitiveStateWire: "", // Unity 不知 cognitive，由 Brain BB 管
                    activeLocks: _activeLocks,
                    sequenceId: _sequenceId);
                Transport.SendHeartbeat(dto);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[LifecycleHeartbeatPublisher] heartbeat send failed (trigger={trigger}): {ex.Message}");
            }
        }

        private string ComputeSig()
        {
            // 紧凑 sig，sig 只用于去重比较，不上 wire
            return string.Concat(
                _bodyStateWire, "|",
                _headStateWire, "|",
                _activeCommandId, "|",
                string.Join(",", _activeLocks));
        }

        private static bool LocksEqual(string[] a, string[] b)
        {
            if (a == null || b == null) return a == b;
            if (a.Length != b.Length) return false;
            for (int i = 0; i < a.Length; i++)
                if (a[i] != b[i]) return false;
            return true;
        }

        private void HandleLifecycleChanged(AppLifecycleState prev, AppLifecycleState next)
        {
            // intent.disconnect 的明示触发：lifecycle 进入 ShuttingDown 时上行一次（IMPL_REF.md §9）。
            if (next == AppLifecycleState.ShuttingDown && Transport != null)
            {
                try
                {
                    Transport.SendIntentDisconnect(
                        unityIdentity: UnityIdentity,
                        roomId: RoomId,
                        reason: "lifecycle:shutting_down");
                }
                catch (Exception ex)
                {
                    Debug.LogWarning($"[LifecycleHeartbeatPublisher] intent.disconnect send failed: {ex.Message}");
                }
            }
        }

        private void HandleHealthChanged(ConnectionHealthState s)
        {
            if (Transport == null) return;
            if (s.Overall == _lastHealthOverall) return;

            // 1Hz 节流，防止抖动期事件风暴
            if (Time.unscaledTime - _lastHealthEventAt < HealthEventMinIntervalSeconds)
                return;

            _lastHealthOverall = s.Overall;
            _lastHealthEventAt = Time.unscaledTime;

            try
            {
                Transport.SendHealthChanged(
                    unityIdentity: UnityIdentity,
                    roomId: RoomId,
                    health: s);
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[LifecycleHeartbeatPublisher] health.changed send failed: {ex.Message}");
            }
        }
    }

    /// <summary>
    /// 解耦传输层：让本 publisher 不依赖 LiveKit SDK，可单测、可 stub。
    ///
    /// 真实 transport 在 RoomManager 搬迁完成后实现 LiveKit DataChannel 版本。
    /// </summary>
    public interface IHeartbeatTransport
    {
        /// <summary>周期 EcpState（reliable）。</summary>
        void SendHeartbeat(EcpStateDto state);

        /// <summary>connection.health.changed 事件（reliable）。</summary>
        void SendHealthChanged(string unityIdentity, string roomId, ConnectionHealthState health);

        /// <summary>intent.disconnect 事件（reliable，graceful shutdown 入口）。</summary>
        void SendIntentDisconnect(string unityIdentity, string roomId, string reason);
    }

    /// <summary>
    /// Editor / spike 期占位 transport：只打日志，不真发到 LiveKit。
    /// 替换成真实 transport 时不需要改 Publisher 代码。
    /// </summary>
    public class LogHeartbeatTransport : IHeartbeatTransport
    {
        public void SendHeartbeat(EcpStateDto state)
        {
            Debug.Log($"[Heartbeat:LOG] {state.ToJson()}");
        }

        public void SendHealthChanged(string unityIdentity, string roomId, ConnectionHealthState health)
        {
            Debug.Log(
                $"[Heartbeat:LOG] connection.health.changed " +
                $"identity={unityIdentity} room={roomId} overall={ConnectionOverallNames.ToWireString(health.Overall)}");
        }

        public void SendIntentDisconnect(string unityIdentity, string roomId, string reason)
        {
            Debug.Log(
                $"[Heartbeat:LOG] intent.disconnect identity={unityIdentity} room={roomId} reason={reason}");
        }
    }
}
