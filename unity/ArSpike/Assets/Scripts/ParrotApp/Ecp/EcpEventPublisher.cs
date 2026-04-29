using System;
using System.Text;
using LiveKit;
using ParrotApp.LiveKit;
using UnityEngine;

namespace ParrotApp.Ecp
{
    /// <summary>
    /// Sprint4 Phase 4 W6-7 — Unity → Brain EcpEvent publisher.
    ///
    /// 把 <see cref="EcpEventDto"/> 通过 LiveKit reliable DataChannel
    /// (topic = <see cref="EcpEventConsts.TopicEcpEvent"/>) 发到 Brain。
    /// Brain 端镜像 = <c>src/parrot/brain/event_publisher.py</c>
    /// (<c>EcpEventPublisher</c>)，两者方向不同但共用 wire 格式。
    ///
    /// <b>定位 — 与 <see cref="LiveKitDataChannelHeartbeatTransport"/> 的关系</b>：
    /// <list type="bullet">
    /// <item><c>LiveKitDataChannelHeartbeatTransport</c> 专管 EcpState / health /
    ///   intent_disconnect 三个 inline-envelope topic（Phase 2 锁定，不动）</item>
    /// <item><c>EcpEventPublisher</c> 专管 Phase 4 新增 <c>parrot.ecp.event</c>
    ///   topic（EcpEvent 跨语言 wire envelope）</item>
    /// </list>
    /// 两个类共享 <see cref="RoomManager"/> 和 PublishData 调用栈，但负责不同的
    /// wire 契约，<b>不要</b>合并：合并会污染 transport 的 single-purpose 语义。
    ///
    /// <b>失败策略</b>（与 <c>LiveKitDataChannelHeartbeatTransport.PublishJson</c> 一致）：
    /// <list type="bullet">
    /// <item>room null / not connected → 静默吞 + <see cref="DroppedNoRoomCount"/>++
    ///   （lifecycle 期间 publisher 应该早就被外部门控）</item>
    /// <item>PublishData 抛 exception → <c>Debug.LogWarning</c> + <see cref="FailedCount"/>++</item>
    /// <item>不做 retry / queue / dedup —— reliable transport 自带重传，Brain
    ///   <c>event_ingest</c> 60s window 去重</item>
    /// </list>
    ///
    /// <b>Editor 离线 smoke 模式</b>：<see cref="logEvenWhenDropped"/> = true 时，
    /// room 不可用也会 <c>Debug.Log</c> dump wire JSON，方便在 Smoke 场景里
    /// 验证 builder / payload 形状（不需要拉起真 LiveKit）。
    /// </summary>
    public class EcpEventPublisher : MonoBehaviour
    {
        [Tooltip("Editor smoke 用：room 不可用 / 发送失败时也把 wire JSON 打到 Console。")]
        [SerializeField] private bool logEvenWhenDropped = true;

        [Tooltip("成功 publish 时也打一行简短 log（Editor smoke 验证用，真机调成 false）。")]
        [SerializeField] private bool logOnSuccess = true;

        [Tooltip("RoomManager 引用；空时 Start 时 Find。")]
        [SerializeField] private RoomManager roomManager;

        public static EcpEventPublisher Instance { get; private set; }

        public int PublishedCount { get; private set; }
        public int DroppedNoRoomCount { get; private set; }
        public int FailedCount { get; private set; }

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
                roomManager = RoomManager.Instance;
        }

        void OnDestroy()
        {
            if (Instance == this) Instance = null;
        }

        public void SetRoomManager(RoomManager rm) => roomManager = rm;

        // ─── public publish API ───────────────────────────────────────

        /// <summary>
        /// 发一个已构造好的 <see cref="EcpEventDto"/>。
        /// 返回 true = 真发到 wire；false = 因 room 状态吞掉或抛异常。
        /// </summary>
        public bool Publish(EcpEventDto dto)
        {
            if (dto == null)
            {
                FailedCount++;
                Debug.LogWarning("[EcpEventPublisher] Publish: dto null");
                return false;
            }

            string wire = EcpEventBuilder.ToWireJson(dto);

            var room = roomManager != null ? roomManager.Room : null;
            bool roomReady = roomManager != null && roomManager.IsConnected && room != null;

            if (!roomReady)
            {
                DroppedNoRoomCount++;
                if (logEvenWhenDropped)
                {
                    Debug.Log(
                        $"[EcpEvent:DROPPED] room not ready (event_type={dto.event_type} " +
                        $"event_id={dto.event_id} bytes={dto.payload_bytes}) wire={wire}");
                }
                return false;
            }

            try
            {
                var payload = Encoding.UTF8.GetBytes(wire);
                room.LocalParticipant.PublishData(
                    payload,
                    reliable: true,
                    topic: EcpEventConsts.TopicEcpEvent);
                PublishedCount++;
                if (logOnSuccess)
                {
                    Debug.Log(
                        $"[EcpEvent:SENT] event_type={dto.event_type} event_id={dto.event_id} " +
                        $"bytes={dto.payload_bytes} corr={dto.correlation_id}");
                }
                return true;
            }
            catch (Exception ex)
            {
                FailedCount++;
                Debug.LogWarning(
                    $"[EcpEventPublisher] PublishData failed (event_type={dto.event_type}): {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// 便捷构造：调 <see cref="EcpEventBuilder.BuildUnityEvent"/> 后立即 publish。
        /// payloadJson 必须是合法 JSON object 字面量；超 8KB 时返回 false。
        /// </summary>
        public bool PublishUnityEvent(
            string eventType,
            string payloadJson,
            string correlationId = "")
        {
            string identity = roomManager != null ? roomManager.JoinIdentity : "";
            string roomName = roomManager != null ? roomManager.RoomName : "";
            var dto = EcpEventBuilder.BuildUnityEvent(
                eventType: eventType,
                payloadJson: payloadJson,
                unityIdentity: identity,
                roomId: roomName,
                correlationId: correlationId);
            if (dto == null)
            {
                FailedCount++;
                return false;
            }
            return Publish(dto);
        }
    }
}
