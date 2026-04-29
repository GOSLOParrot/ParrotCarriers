using System;
using LiveKit;
using ParrotApp.Health;
using ParrotApp.LiveKit;
using UnityEngine;

namespace ParrotApp.Lifecycle
{
    /// <summary>
    /// �?<see cref="RoomManager"/> �?LiveKit 事件翻译�?
    /// <see cref="AppLifecycleManager"/> �?transition 调用 + �?
    /// <see cref="ConnectionHealthAggregator"/> 的字段�?
    ///
    /// <b>设计立场</b>（与锚点 sprint4_phase3_l3_entry_20260429.md §0 一致）�?
    /// <list type="bullet">
    /// <item>本类�?b>翻译�?/b>：只�?RoomManager event �?Lifecycle / Health setter�?
    ///   不引入新决策、不�?BT 行为路由�?/item>
    /// <item>single-producer-per-field（IMPL_REF.md §4.2）：本类�?
    ///   <c>room_connected</c> / <c>brain_present</c> /
    ///   <c>reconnect_attempt_count</c> / <c>last_disconnected_at</c> �?b>唯一</b> producer�?
    ///   其他组件不能调对�?setter�?/item>
    /// </list>
    ///
    /// <b>挂载</b>：与 <see cref="AppLifecycleManager"/> �?GameObject；自动找
    /// <see cref="RoomManager.Instance"/>（也可在 Inspector 里指定）�?
    /// </summary>
    [RequireComponent(typeof(AppLifecycleManager))]
    public class RoomManagerLifecycleBridge : MonoBehaviour
    {
        [Tooltip("Optional. Falls back to RoomManager.Instance (singleton) when null.")]
        [SerializeField] private RoomManager roomManager;

        [Tooltip("Brain identity prefix; must match BrainParticipantResolver detection logic.")]
        [SerializeField] private string brainIdentityPrefix = "agent-";

        private AppLifecycleManager _lifecycle;

        // �?property 而非缓存字段：AppLifecycleManager.HealthAggregator 在它自身
        // �?Awake 里初始化；本�?Awake 顺序不保证在它之后，缓存 null 会永久失效�?
        private ConnectionHealthAggregator Health =>
            _lifecycle != null ? _lifecycle.HealthAggregator : null;

        // 本类持有的累计计数器；跨 reconnect 周期累加，由 lifecycle 决定何时归零
        private int _reconnectAttemptCount;

        // 跟踪当前已识别的 brain 远端 identity（防�?ParticipantConnected/Disconnected
        // 风暴里多�?toggle brain_present）。空字符�?= 当前�?brain�?
        private string _currentBrainIdentity = "";

        private static double UnixSeconds()
            => (DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalSeconds;

        protected virtual void Awake()
        {
            _lifecycle = GetComponent<AppLifecycleManager>();
        }

        protected virtual void OnEnable()
        {
            BindRoomManager();
        }

        protected virtual void Start()
        {
            // RoomManager singleton 可能�?Awake 之后才初始化（Script Execution Order）�?
            // �?Start 里再尝试一次绑定，幂等�?
            BindRoomManager();
        }

        protected virtual void OnDisable()
        {
            UnbindRoomManager();
        }

        private void BindRoomManager()
        {
            if (roomManager == null) roomManager = RoomManager.Instance;
            if (roomManager == null) return;

            // 幂等：先 unbind �?bind，避免重复订�?
            roomManager.OnConnecting -= HandleConnecting;
            roomManager.OnConnected -= HandleConnected;
            roomManager.OnDisconnected -= HandleDisconnected;
            roomManager.OnParticipantConnected -= HandleParticipantConnected;
            roomManager.OnParticipantDisconnected -= HandleParticipantDisconnected;

            roomManager.OnConnecting += HandleConnecting;
            roomManager.OnConnected += HandleConnected;
            roomManager.OnDisconnected += HandleDisconnected;
            roomManager.OnParticipantConnected += HandleParticipantConnected;
            roomManager.OnParticipantDisconnected += HandleParticipantDisconnected;
        }

        private void UnbindRoomManager()
        {
            if (roomManager == null) return;
            roomManager.OnConnecting -= HandleConnecting;
            roomManager.OnConnected -= HandleConnected;
            roomManager.OnDisconnected -= HandleDisconnected;
            roomManager.OnParticipantConnected -= HandleParticipantConnected;
            roomManager.OnParticipantDisconnected -= HandleParticipantDisconnected;
        }

        // ─── RoomManager event handlers ───────────────────────────────────

        private void HandleConnecting()
        {
            // 区分首次 Connect vs reconnect：currentState �?ColdStart/PermissionGate/TokenGate/ArSessionStarting
            // 时是首次；其他都�?reconnect 路径�?
            var state = _lifecycle.CurrentState;
            bool isReconnect =
                state == AppLifecycleState.Reconnecting
                || state == AppLifecycleState.LongBackground
                || state == AppLifecycleState.Degraded
                || state == AppLifecycleState.Disconnected
                || state == AppLifecycleState.Connected
                || state == AppLifecycleState.Running;

            if (isReconnect)
            {
                _reconnectAttemptCount++;
                Health?.ReportReconnectAttempt(_reconnectAttemptCount, UnixSeconds());
                _lifecycle.ReportReconnecting("RoomManager.OnConnecting (reconnect)");
            }
            else
            {
                _lifecycle.EnterConnecting();
            }
        }

        private void HandleConnected()
        {
            var now = UnixSeconds();
            // RoomManager �?room_connected / brain_present �?sole producer�?
            // 这里只灌 room_connected=true；brain_present �?ParticipantConnected 路径�?
            Health?.ReportRoomConnected(true, now);
            _lifecycle.ReportRoomConnected();

            // 重连成功后回�?healthy 区间，counter �?0
            _reconnectAttemptCount = 0;
            Health?.ReportReconnectAttempt(0, now);

            // 如果远端已有 brain（可能在我们订阅前就 join 了），手动扫一�?
            ScanForBrainParticipant();
        }

        private void HandleDisconnected()
        {
            var now = UnixSeconds();
            Health?.ReportRoomConnected(false, now);
            Health?.ReportBrainPresent(false, now);
            _currentBrainIdentity = "";

            // 区分 graceful vs 被动：依�?RoomManager.IsDisconnecting flag
            // graceful 路径�?LifecycleShutdownService 已经�?lifecycle 推到 ShuttingDown�?
            // 这里只灌 health；被动路径才�?lifecycle�?
            if (roomManager != null && roomManager.IsDisconnecting)
            {
                // graceful：等 chokepoint 自己推到 Disconnected
                Debug.Log("[Bridge] Disconnect was intentional (chokepoint); not auto-transitioning lifecycle");
            }
            else
            {
                // 被动失联：进 Reconnecting，让 watchdog / 用户决定后续
                _lifecycle.ReportReconnecting("RoomManager.OnDisconnected (passive)");
            }
        }

        private void HandleParticipantConnected(RemoteParticipant participant)
        {
            if (IsBrainIdentity(participant?.Identity))
            {
                _currentBrainIdentity = participant.Identity;
                Health?.ReportBrainPresent(true, UnixSeconds());
            }
        }

        private void HandleParticipantDisconnected(RemoteParticipant participant)
        {
            if (string.IsNullOrEmpty(participant?.Identity)) return;
            if (string.Equals(participant.Identity, _currentBrainIdentity, StringComparison.Ordinal))
            {
                _currentBrainIdentity = "";
                Health?.ReportBrainPresent(false, UnixSeconds());
                // 二次扫描：可能房间里还有其他 agent-* identity
                ScanForBrainParticipant();
            }
        }

        // ─── helpers ──────────────────────────────────────────────────────

        private void ScanForBrainParticipant()
        {
            if (roomManager?.Room == null) return;
            var brainId = BrainParticipantResolver.FindBrainParticipantId(roomManager.Room);
            if (string.IsNullOrEmpty(brainId)) return;
            if (string.Equals(brainId, _currentBrainIdentity, StringComparison.Ordinal)) return;

            _currentBrainIdentity = brainId;
            Health?.ReportBrainPresent(true, UnixSeconds());
        }

        private bool IsBrainIdentity(string identity)
        {
            if (string.IsNullOrEmpty(identity)) return false;
            if (identity.StartsWith(brainIdentityPrefix, StringComparison.Ordinal)) return true;
            if (string.Equals(identity, "brain", StringComparison.OrdinalIgnoreCase)) return true;
            return false;
        }
    }
}
