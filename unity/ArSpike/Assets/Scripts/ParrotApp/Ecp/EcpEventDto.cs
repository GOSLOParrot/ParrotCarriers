using System;
using System.Text;
using UnityEngine;

namespace ParrotApp.Ecp
{
    /// <summary>
    /// Sprint4 Phase 4 跨语言 wire envelope DTO (mirror of
    /// <c>parrot.shared.ecp_event.EcpEvent</c>).
    ///
    /// <b>命名注意</b>：Python 端类名是 <c>EcpEvent</c>（<b>不</b>是
    /// <c>EventEnvelope</c>）。<c>parrot.shared.event_log.EventEnvelope</c> 是
    /// Sprint 0 已存在的 L0 Redis Stream 内部封装，与本类的 wire 用途冲突。
    /// 详见 <c>architecture/sprint4_phase4_entry_20260430.md §8.0</c>。
    ///
    /// <b>JsonUtility 兼容</b>：<see cref="payload_json"/> 是字符串而不是字典/对象。
    /// JsonUtility 不支持任意键的 <c>Dictionary&lt;string, object&gt;</c>；按 entry
    /// doc §8.1 L2 锁定的契约，payload 在 wire 上是嵌套 JSON object，但 Unity 端
    /// 用字符串字段持有它的<b>字面文本</b>，由调用方 (<see cref="EcpEventBuilder"/>)
    /// 在 <see cref="ToWireJson"/> 时直接拼接，避免双重转义。Brain 端
    /// <c>parrot.brain.event_ingest</c> 把 payload 当成 JSON object 解析。
    ///
    /// <b>Payload 大小红线</b>：8 KB（<see cref="EcpEventConsts.PayloadLimitBytes"/>）。
    /// Unity 端必须在 publish 前 pre-check；Brain 端会拒收并发
    /// <c>event.rejected.oversize</c>（synthesized brain-source event）。
    /// </summary>
    [Serializable]
    public class EcpEventDto
    {
        public int schema_version = EcpEventConsts.SchemaVersion;
        public string event_id = "";
        public string event_type = "";
        public long created_at;  // Unix epoch milliseconds
        public string source = "";

        public string unity_identity = "";
        public string room_id = "";
        public string correlation_id = "";

        public int payload_bytes;

        /// <summary>
        /// payload 的 JSON 字面文本（已是合法 JSON object）。<b>不要</b>把这里当成
        /// "raw string payload" — wire 上它会作为 object 嵌入 envelope。Builder /
        /// <see cref="ToWireJson"/> 在拼接时直接插入而不是再转义一次。
        /// </summary>
        public string payload_json = "{}";
    }

    public static class EcpEventConsts
    {
        public const int SchemaVersion = 1;
        public const int PayloadLimitBytes = 8 * 1024;

        // Topic constants — duplicated from
        // `LiveKitDataChannelHeartbeatTransport.TopicState/Health/IntentDisconnect`
        // intentionally; both files reference the same wire contract and we
        // do not want a one-way include dependency.
        public const string TopicEcpEvent = "parrot.ecp.event";
        public const string TopicEcpState = "parrot.ecp.state";
        public const string TopicEcpTick = "parrot.ecp.tick";
    }

    /// <summary>
    /// Source enum mirror — string constants instead of <c>enum</c> because
    /// JsonUtility does not round-trip enums by string name.
    /// </summary>
    public static class EcpEventSourceNames
    {
        public const string Unity = "unity";
        public const string Brain = "brain";
        public const string Nanobot = "nanobot";  // reserved
    }

    /// <summary>
    /// Event type registry mirror (Python <c>EcpEventType</c> enum).
    /// Adding a value here MUST stay in lockstep with
    /// <c>src/parrot/shared/ecp_event.py:EcpEventType</c>; the
    /// <c>tests/test_ecp_event/test_ecp_event_cs_parity.py</c> guard catches
    /// silent drift on CI.
    /// </summary>
    public static class EcpEventTypeNames
    {
        // Tool ② — identify_object full chain
        public const string SnapshotCaptured = "snapshot.captured";
        public const string SightingMatched = "sighting.matched";
        public const string SightingUnmatched = "sighting.unmatched";

        // Tool ③ — Focus / BBox attention
        public const string BboxPlaced = "bbox.placed";
        public const string BboxRemoved = "bbox.removed";
        public const string FocusAnchored = "focus.anchored";
        public const string FocusReleased = "focus.released";
        public const string AttentionThresholdCrossed = "attention.threshold.crossed";

        // Tool ④ — camera / photo
        public const string PhotoTakenPreview = "photo.taken_preview";
        public const string PhotoAssetUploaded = "photo.asset_uploaded";

        // Tool ① — gesture (optional Phase 4)
        public const string GestureRecognized = "gesture.recognized";

        // Defensive — emitted by Brain ingest on payload > 8KB
        public const string EventRejectedOversize = "event.rejected.oversize";
    }

    /// <summary>
    /// 推荐的 EcpEvent 构造路径。封装 event_id 生成、created_at 时间戳、
    /// payload_bytes 计算、8KB pre-check。
    /// </summary>
    public static class EcpEventBuilder
    {
        /// <summary>
        /// 构造一个 Unity-source EcpEvent。<paramref name="payloadJson"/> 必须是
        /// <b>合法 JSON object</b>（如 <c>"{\"x\":1}"</c>）；空 payload 传 <c>"{}"</c>。
        /// 返回 <c>null</c> 表示 payload 超过 8KB —— 调用方必须切到
        /// HTTP upload + asset_ref 路径（entry doc §8.1 L8）。
        /// </summary>
        public static EcpEventDto BuildUnityEvent(
            string eventType,
            string payloadJson,
            string unityIdentity = "",
            string roomId = "",
            string correlationId = "")
        {
            if (string.IsNullOrEmpty(payloadJson)) payloadJson = "{}";
            int size = Encoding.UTF8.GetByteCount(payloadJson);
            if (size > EcpEventConsts.PayloadLimitBytes)
            {
                Debug.LogWarning(
                    $"[EcpEvent] payload {size}B > {EcpEventConsts.PayloadLimitBytes}B cap" +
                    $" — caller must use HTTP upload + asset_ref instead (event_type={eventType})");
                return null;
            }

            return new EcpEventDto
            {
                event_id = GenerateEventId(),
                event_type = eventType ?? "",
                created_at = UnixMilliseconds(),
                source = EcpEventSourceNames.Unity,
                unity_identity = unityIdentity ?? "",
                room_id = roomId ?? "",
                correlation_id = correlationId ?? "",
                payload_bytes = size,
                payload_json = payloadJson,
            };
        }

        /// <summary>
        /// Time-sortable event_id. Format mirrors Python
        /// <c>parrot.shared.ecp_event.generate_event_id</c>:
        /// <c>evt_{ts_ms_hex_12}_{rand_hex_8}</c>. The 12-char hex prefix is
        /// the Unix epoch ms, so events sort lexicographically by arrival.
        /// </summary>
        public static string GenerateEventId()
        {
            long tsMs = UnixMilliseconds();
            // 12-char zero-padded hex of ms epoch
            string tsHex = tsMs.ToString("x12");

            // 8-char random hex (4 bytes) — Guid is fine, we only use the
            // first 4 bytes
            string randHex = Guid.NewGuid().ToString("N").Substring(0, 8);
            return $"evt_{tsHex}_{randHex}";
        }

        public static long UnixMilliseconds()
        {
            return (long)((DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalMilliseconds);
        }

        /// <summary>
        /// Serialize an <see cref="EcpEventDto"/> to the exact wire JSON.
        /// Special-cases <see cref="EcpEventDto.payload_json"/> by inlining
        /// it as an object (rather than as a string) so the wire shape
        /// matches the Pydantic model on the Python side.
        /// </summary>
        public static string ToWireJson(EcpEventDto dto)
        {
            if (dto == null) return "";

            // We hand-roll because JsonUtility would emit `payload_json` as a
            // string field, but the wire contract is `"payload": { ... }`.
            // Order of fields matches Pydantic dump order; not protocol-
            // significant but keeps test diffs readable.
            var sb = new StringBuilder(256);
            sb.Append('{');
            sb.Append("\"schema_version\":").Append(dto.schema_version).Append(',');
            sb.Append("\"event_id\":").Append(Quote(dto.event_id)).Append(',');
            sb.Append("\"event_type\":").Append(Quote(dto.event_type)).Append(',');
            sb.Append("\"created_at\":").Append(dto.created_at).Append(',');
            sb.Append("\"source\":").Append(Quote(dto.source)).Append(',');
            sb.Append("\"unity_identity\":").Append(Quote(dto.unity_identity ?? "")).Append(',');
            sb.Append("\"room_id\":").Append(Quote(dto.room_id ?? "")).Append(',');
            sb.Append("\"correlation_id\":").Append(Quote(dto.correlation_id ?? "")).Append(',');
            sb.Append("\"payload_bytes\":").Append(dto.payload_bytes).Append(',');
            sb.Append("\"payload\":").Append(string.IsNullOrEmpty(dto.payload_json) ? "{}" : dto.payload_json);
            sb.Append('}');
            return sb.ToString();
        }

        private static string Quote(string s)
        {
            if (s == null) return "\"\"";
            // Tight-loop JSON string escape — only the chars JsonUtility
            // would escape. We don't have unicode-non-ASCII trouble because
            // unity_identity / event_id / etc are ASCII-only by contract.
            var sb = new StringBuilder(s.Length + 2);
            sb.Append('"');
            foreach (char c in s)
            {
                switch (c)
                {
                    case '\\': sb.Append("\\\\"); break;
                    case '"': sb.Append("\\\""); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    default:
                        if (c < 0x20)
                            sb.AppendFormat("\\u{0:x4}", (int)c);
                        else
                            sb.Append(c);
                        break;
                }
            }
            sb.Append('"');
            return sb.ToString();
        }
    }
}
