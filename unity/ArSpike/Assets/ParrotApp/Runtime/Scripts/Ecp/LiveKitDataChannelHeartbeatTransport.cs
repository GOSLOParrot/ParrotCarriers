using System;
using System.Text;
using LiveKit;
using ParrotApp.Health;
using ParrotApp.LiveKit;
using UnityEngine;

namespace ParrotApp.Ecp
{
    /// <summary>
    /// 真实 <see cref="IHeartbeatTransport"/> 实现：通过 LiveKit Reliable DataChannel
    /// 把 <see cref="EcpStateDto"/> / <c>connection.health.changed</c> /
    /// <c>intent.disconnect</c> 上行到 Brain。
    ///
    /// <b>Topics</b>（与设计稿 §5.3 对齐；Brain 端 Phase 2 会加 handler 订阅）：
    /// <list type="bullet">
    /// <item><c>parrot.ecp.state</c> — 周期 EcpState 心跳</item>
    /// <item><c>parrot.ecp.health</c> — connection.health.changed 事件（4 态翻转）</item>
    /// <item><c>parrot.ecp.intent_disconnect</c> — intent.disconnect 事件（IMPL_REF.md §9）</item>
    /// </list>
    ///
    /// <b>设计立场</b>：
    /// <list type="bullet">
    /// <item>本类只负责<b>发包</b>，不维护重试 / 队列；Reliable DataChannel 自带重传，
    ///   Brain 端 watchdog（IMPL_REF.md §3）对错过的包负责。</item>
    /// <item>第一次成功 PublishData 反向灌
    ///   <see cref="ConnectionHealthAggregator.ReportDataChannelReady"/>，让
    ///   <c>datachannel_ready</c> 字段有 producer。</item>
    /// <item><see cref="LifecycleHeartbeatPublisher"/> 在 lifecycle ∈ {ColdStart,
    ///   ShuttingDown, Disconnected} 时不调本类；本类不做二次过滤。</item>
    /// </list>
    /// </summary>
    public class LiveKitDataChannelHeartbeatTransport : IHeartbeatTransport
    {
        public const string TopicState = "parrot.ecp.state";
        public const string TopicHealth = "parrot.ecp.health";
        public const string TopicIntentDisconnect = "parrot.ecp.intent_disconnect";

        private readonly RoomManager _roomManager;
        private readonly ConnectionHealthAggregator _health;
        private bool _datachannelReadyReported;

        /// <param name="roomManager">必传；通常是 <c>RoomManager.Instance</c></param>
        /// <param name="health">可选；如果传入会在第一次 PublishData 成功后灌
        /// <c>datachannel_ready=true</c></param>
        public LiveKitDataChannelHeartbeatTransport(
            RoomManager roomManager,
            ConnectionHealthAggregator health = null)
        {
            _roomManager = roomManager
                ?? throw new ArgumentNullException(nameof(roomManager));
            _health = health;
        }

        public void SendHeartbeat(EcpStateDto state)
        {
            if (state == null) return;
            PublishJson(TopicState, state.ToJson(), reliable: true);
        }

        public void SendHealthChanged(string unityIdentity, string roomId, ConnectionHealthState health)
        {
            // 用 EcpConnectionHealthDto 的 wire 形式包到一个独立 envelope；topic 携带语义。
            var dto = EcpConnectionHealthDto.FromSnapshot(health);
            string body = JsonUtility.ToJson(dto);
            string envelope = BuildEventEnvelope(
                eventName: "connection.health.changed",
                unityIdentity: unityIdentity,
                roomId: roomId,
                body: body);
            PublishJson(TopicHealth, envelope, reliable: true);
        }

        public void SendIntentDisconnect(string unityIdentity, string roomId, string reason)
        {
            // 简短 payload —— Brain 解析 reason / lifecycle 进入 ShuttingDown 的来源
            string body = $"{{\"reason\":{Quote(reason)}}}";
            string envelope = BuildEventEnvelope(
                eventName: "intent.disconnect",
                unityIdentity: unityIdentity,
                roomId: roomId,
                body: body);
            PublishJson(TopicIntentDisconnect, envelope, reliable: true);
        }

        // ─── helpers ──────────────────────────────────────────────────────

        private void PublishJson(string topic, string json, bool reliable)
        {
            if (string.IsNullOrEmpty(json)) return;

            var room = _roomManager?.Room;
            if (room == null || !_roomManager.IsConnected)
            {
                // 不打 warning 风暴：lifecycle publisher 应该在 Disconnected 期间就不调本类；
                // 真到这里属于偶发竞态，吞掉。
                return;
            }

            try
            {
                var payload = Encoding.UTF8.GetBytes(json);
                room.LocalParticipant.PublishData(payload, reliable: reliable, topic: topic);

                if (!_datachannelReadyReported && _health != null)
                {
                    _datachannelReadyReported = true;
                    _health.ReportDataChannelReady(true, UnixSeconds());
                }
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[Heartbeat:DC] PublishData(topic={topic}) failed: {ex.Message}");
            }
        }

        private static double UnixSeconds()
            => (DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalSeconds;

        private static string Quote(string s)
        {
            if (s == null) return "\"\"";
            var escaped = s.Replace("\\", "\\\\").Replace("\"", "\\\"");
            return "\"" + escaped + "\"";
        }

        /// <summary>
        /// 简化的事件 envelope（不引入 Newtonsoft）。结构与设计稿 §5.3 事件层概要一致：
        /// <c>{event, unity_identity, room_id, ts, body: { ... }}</c>。
        /// body 已经是合法 JSON，不再二次转义。
        /// </summary>
        private static string BuildEventEnvelope(
            string eventName,
            string unityIdentity,
            string roomId,
            string body)
        {
            var sb = new StringBuilder(256);
            sb.Append('{');
            sb.Append("\"event\":").Append(Quote(eventName)).Append(',');
            sb.Append("\"unity_identity\":").Append(Quote(unityIdentity ?? "")).Append(',');
            sb.Append("\"room_id\":").Append(Quote(roomId ?? "")).Append(',');
            sb.Append("\"ts\":").Append(UnixSeconds().ToString("F3", System.Globalization.CultureInfo.InvariantCulture)).Append(',');
            sb.Append("\"body\":").Append(string.IsNullOrEmpty(body) ? "{}" : body);
            sb.Append('}');
            return sb.ToString();
        }
    }
}
