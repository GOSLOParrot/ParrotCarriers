using System;
using System.Collections.Generic;
using System.Text;
using LiveKit;
using LiveKit.Proto;
using ParrotApp.LiveKit;
using UnityEngine;

namespace ParrotApp.Ecp
{
    /// <summary>
    /// Sprint4 Phase 4 L12 — Unity 下行 router (Brain → Unity).
    ///
    /// 监听 <see cref="Room"/> 的 <c>DataReceived</c> 事件，按 LiveKit topic 把
    /// payload 分发到 Phase 4 各 handler。topic 与 entry doc §8.2 锁定值对齐：
    /// <list type="bullet">
    /// <item><c>parrot.ecp.event</c> — Phase 4 EcpEvent (brain → unity)</item>
    /// <item><c>parrot.ecp.state</c> — Phase 3 EcpState（已存在，本类不接管）</item>
    /// <item><c>parrot.ecp.tick</c> — Phase 4 lossy gesture/pose/focus drag</item>
    /// </list>
    ///
    /// <b>L12 拆双向</b>：本类是 <b>Unity 下行 router</b>（接 Brain 发来的事件）。
    /// Python 上行 ingest = <c>src/parrot/brain/event_ingest.py</c>。两者共用
    /// <c>EcpEventDto</c> wire 格式但属于不同方向。
    ///
    /// <b>Phase 4 W1-2 范围（当前）</b>：
    /// <list type="bullet">
    /// <item>注册 <c>Room.DataReceived</c> 回调</item>
    /// <item>按 topic 分发到 typed handler 字典</item>
    /// <item>解析 EcpEventDto 并按 event_type 二级路由</item>
    /// </list>
    /// 实际 handler（attention.threshold.crossed 弹气泡 / sighting.matched 高亮等）
    /// 是 W3+ 工作；本类只有路由骨架 + 默认 log handler。
    ///
    /// <b>不做（与 §3.7 Observer/Attention 边界一致）</b>：
    /// <list type="bullet">
    /// <item>不做 ECP 内部状态机推进 — <see cref="EcpStateDto"/> 走
    ///   <c>LifecycleHeartbeatPublisher</c></item>
    /// <item>不做 Bridge ack 回写 — 那是 RPC 路径职责</item>
    /// <item>不写 BB 等价物（Unity 端没有 BB；状态归 ECP/Lifecycle/Health 管）</item>
    /// </list>
    /// </summary>
    public class EcpEventDispatcher : MonoBehaviour
    {
        [Tooltip("将本组件挂到与 RoomManager 同一物体；自动 Find 也可。")]
        [SerializeField] private RoomManager roomManager;

        /// <summary>
        /// 单例 — 与 RoomManager / ConnectionHealthAggregator 同一模式，方便
        /// 其他 UI 组件取 dispatcher 注册自己的 handler 而不需 GetComponent
        /// 满天飞。
        /// </summary>
        public static EcpEventDispatcher Instance { get; private set; }

        // event_type → handler list. 多个 handler 同时注册时按注册顺序触发。
        private readonly Dictionary<string, List<Action<EcpEventDto>>> _handlers = new();
        private readonly List<Action<EcpEventDto>> _wildcardHandlers = new();

        // Observability counters — 镜像 Python EcpEventIngest 的字段命名
        public int ReceivedCount { get; private set; }
        public int DispatchedCount { get; private set; }
        public int MalformedCount { get; private set; }
        public int OversizeCount { get; private set; }
        public int UnknownTopicCount { get; private set; }

        private bool _subscribed;

        void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(this);
                return;
            }
            Instance = this;
        }

        void Start()
        {
            if (roomManager == null)
            {
                roomManager = RoomManager.Instance;
                if (roomManager == null)
                {
                    Debug.LogWarning(
                        "[EcpEventDispatcher] No RoomManager found at Start. " +
                        "Call SetRoomManager() once one is available.");
                    return;
                }
            }
            TrySubscribe();
        }

        public void SetRoomManager(RoomManager rm)
        {
            roomManager = rm;
            TrySubscribe();
        }

        // ─── public registration API ──────────────────────────────

        /// <summary>
        /// Register a handler for a specific event_type
        /// (e.g. <see cref="EcpEventTypeNames.AttentionThresholdCrossed"/>).
        /// </summary>
        public void RegisterHandler(string eventType, Action<EcpEventDto> handler)
        {
            if (string.IsNullOrEmpty(eventType) || handler == null) return;
            if (!_handlers.TryGetValue(eventType, out var list))
            {
                list = new List<Action<EcpEventDto>>();
                _handlers[eventType] = list;
            }
            list.Add(handler);
        }

        /// <summary>Wildcard handler — fired for every event after typed handlers.</summary>
        public void RegisterWildcard(Action<EcpEventDto> handler)
        {
            if (handler != null) _wildcardHandlers.Add(handler);
        }

        // ─── DataChannel binding ──────────────────────────────────

        private void TrySubscribe()
        {
            if (_subscribed || roomManager == null) return;
            // RoomManager exposes Room as a property; we wait for OnConnected
            // (Room may be null until then).
            roomManager.OnConnected += OnRoomConnected;
            roomManager.OnDisconnected += OnRoomDisconnected;
            if (roomManager.IsConnected)
            {
                OnRoomConnected();
            }
        }

        private void OnRoomConnected()
        {
            var room = roomManager?.Room;
            if (room == null)
            {
                Debug.LogWarning("[EcpEventDispatcher] OnRoomConnected but Room is null");
                return;
            }
            // LiveKit Unity SDK exposes a generic data event on the Room
            // object. Signature mirrors v1.x: (data, participant, kind, topic).
            // If the SDK signature drifts in a future bump, the build will
            // break here loud and clear — preferred over silent-no-op.
            try
            {
                room.DataReceived += OnDataReceived;
                _subscribed = true;
                Debug.Log("[EcpEventDispatcher] Room.DataReceived subscribed");
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[EcpEventDispatcher] DataReceived hook failed: {ex.Message}");
            }
        }

        private void OnRoomDisconnected()
        {
            // RoomManager replaces Room on reconnect; we re-subscribe in the
            // next OnRoomConnected. No need to manually unsubscribe — old
            // Room is disposed, the delegate target dies with it.
            _subscribed = false;
        }

        private void OnDataReceived(byte[] data, Participant participant, DataPacketKind kind, string topic)
        {
            ReceivedCount++;

            if (topic != EcpEventConsts.TopicEcpEvent)
            {
                // Not our topic. Other dispatchers (state heartbeat handler,
                // health-changed inline envelope handler, etc.) own the rest.
                UnknownTopicCount++;
                return;
            }

            if (data == null || data.Length == 0)
            {
                MalformedCount++;
                return;
            }

            if (data.Length > EcpEventConsts.PayloadLimitBytes * 2)
            {
                // Even with envelope overhead, > 2× cap is malformed input.
                // We don't try to parse — Brain side will reject before we
                // care.
                OversizeCount++;
                return;
            }

            string json;
            try
            {
                json = Encoding.UTF8.GetString(data);
            }
            catch (Exception ex)
            {
                MalformedCount++;
                Debug.LogWarning($"[EcpEventDispatcher] UTF8 decode failed: {ex.Message}");
                return;
            }

            EcpEventDto dto;
            try
            {
                // JsonUtility cannot deserialize the wire shape directly
                // because of the `payload_json` ↔ `payload` (string vs
                // object) trick on the publish side. Phase 4 W2 ships a
                // small parser; for W1 we accept that downstream handlers
                // see an empty payload until a Phase 4 parser lands.
                dto = JsonUtility.FromJson<EcpEventDto>(json);
                if (dto == null)
                {
                    MalformedCount++;
                    return;
                }
            }
            catch (Exception ex)
            {
                MalformedCount++;
                Debug.LogWarning($"[EcpEventDispatcher] JSON parse failed: {ex.Message}");
                return;
            }

            DispatchedCount++;

            if (_handlers.TryGetValue(dto.event_type, out var list))
            {
                foreach (var h in list)
                {
                    try { h(dto); }
                    catch (Exception ex)
                    {
                        Debug.LogWarning(
                            $"[EcpEventDispatcher] handler for {dto.event_type} threw: {ex.Message}");
                    }
                }
            }

            foreach (var h in _wildcardHandlers)
            {
                try { h(dto); }
                catch (Exception ex)
                {
                    Debug.LogWarning(
                        $"[EcpEventDispatcher] wildcard handler threw on {dto.event_type}: {ex.Message}");
                }
            }
        }

        void OnDestroy()
        {
            if (Instance == this) Instance = null;
        }
    }
}
