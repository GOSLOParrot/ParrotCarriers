using System;
using ParrotApp.Config;
using ParrotApp.Health;
using ParrotApp.Lifecycle;
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
    /// </summary>
    [RequireComponent(typeof(AppLifecycleManager))]
    public class LifecycleHeartbeatPublisher : MonoBehaviour
    {
        [Tooltip("空时使用 LogHeartbeatTransport（仅打印），LiveKit transport 上线后通过代码注入。")]
        [SerializeField] private bool useLogTransportInEditor = true;

        public IHeartbeatTransport Transport { get; set; }
        public string UnityIdentity { get; set; } = "";
        public string RoomId { get; set; } = "";

        private AppLifecycleManager _lifecycle;
        private ParrotLifecycleConfig Config => _lifecycle != null ? _lifecycle.Config : null;
        private float _nextSendAt = 0f;

        // 节流"connection.health.changed"事件：抖动期 1s 最多发一次
        private float _lastHealthEventAt = 0f;
        private ConnectionOverall _lastHealthOverall = ConnectionOverall.Unknown;
        private const float HealthEventMinIntervalSeconds = 1f;

        protected virtual void Awake()
        {
            _lifecycle = GetComponent<AppLifecycleManager>();
            if (Transport == null && useLogTransportInEditor)
                Transport = new LogHeartbeatTransport();
        }

        protected virtual void OnEnable()
        {
            if (_lifecycle != null)
            {
                _lifecycle.OnStateChanged += HandleLifecycleChanged;
                if (_lifecycle.HealthAggregator != null)
                    _lifecycle.HealthAggregator.OnChanged += HandleHealthChanged;
            }
        }

        protected virtual void OnDisable()
        {
            if (_lifecycle != null)
            {
                _lifecycle.OnStateChanged -= HandleLifecycleChanged;
                if (_lifecycle.HealthAggregator != null)
                    _lifecycle.HealthAggregator.OnChanged -= HandleHealthChanged;
            }
        }

        protected virtual void Update()
        {
            if (Transport == null || _lifecycle == null || Config == null) return;

            // 不在已断开 / 关机中态发心跳，避免 watchdog 把"我自己断了"当 unhealthy
            if (_lifecycle.CurrentState == AppLifecycleState.Disconnected
                || _lifecycle.CurrentState == AppLifecycleState.ShuttingDown
                || _lifecycle.CurrentState == AppLifecycleState.ColdStart)
            {
                return;
            }

            if (Time.unscaledTime >= _nextSendAt)
            {
                SendHeartbeat();
                _nextSendAt = Time.unscaledTime + Config.T_HEARTBEAT_INTERVAL;
            }
        }

        // ─── senders ─────────────────────────────────────────────────────

        private void SendHeartbeat()
        {
            try
            {
                var snapshot = _lifecycle.HealthAggregator.Snapshot;
                var dto = EcpStateDto.BuildHeartbeat(
                    unityIdentity: UnityIdentity,
                    roomId: RoomId,
                    appLifecycleState: AppLifecycleStateNames.ToWireString(_lifecycle.CurrentState),
                    health: snapshot,
                    videoTier: snapshot.VideoTier);
                Transport.SendHeartbeat(dto);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[LifecycleHeartbeatPublisher] heartbeat send failed: {ex.Message}");
            }
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
