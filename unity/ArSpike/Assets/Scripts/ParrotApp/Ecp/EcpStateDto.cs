using System;
using ParrotApp.Health;
using UnityEngine;

namespace ParrotApp.Ecp
{
    /// <summary>
    /// 完整 ConnectionHealthState 的 wire 形式（snake_case 字段名与 Python 对齐）。
    /// 来源：<c>.cursor/skills/livekit-unity-lifecycle/IMPL_REF.md §4.2</c>。
    /// </summary>
    [Serializable]
    public class EcpConnectionHealthDto
    {
        public bool room_connected;
        public bool brain_present;
        public bool rpc_ready;
        public bool datachannel_ready;

        public bool audio_publish_attempted;
        public bool audio_published;
        public string audio_last_error = "";

        public bool video_publish_attempted;
        public bool video_published;
        public bool video_first_frame;
        public bool video_fresh_frame;
        public string video_tier = "";
        public string video_lifecycle_reason = "";

        public string ar_tracking_state = "";

        public int reconnect_attempt_count;
        public double last_disconnected_at;

        public string overall = ConnectionOverallNames.Unknown;
        public double last_state_change_at;

        public static EcpConnectionHealthDto FromSnapshot(in ConnectionHealthState s)
        {
            return new EcpConnectionHealthDto
            {
                room_connected = s.RoomConnected,
                brain_present = s.BrainPresent,
                rpc_ready = s.RpcReady,
                datachannel_ready = s.DataChannelReady,

                audio_publish_attempted = s.AudioPublishAttempted,
                audio_published = s.AudioPublished,
                audio_last_error = s.AudioLastError ?? "",

                video_publish_attempted = s.VideoPublishAttempted,
                video_published = s.VideoPublished,
                video_first_frame = s.VideoFirstFrame,
                video_fresh_frame = s.VideoFreshFrame,
                video_tier = s.VideoTier ?? "",
                video_lifecycle_reason = s.VideoLifecycleReason ?? "",

                ar_tracking_state = s.ArTrackingState ?? "",

                reconnect_attempt_count = s.ReconnectAttemptCount,
                last_disconnected_at = s.LastDisconnectedAt,

                overall = ConnectionOverallNames.ToWireString(s.Overall),
                last_state_change_at = s.LastStateChangeAt,
            };
        }
    }

    /// <summary>
    /// Sprint4 Phase 3 周期上报 payload。
    ///
    /// <b>用途</b>：Unity → Brain 周期把当前前端状态机快照灌过去，
    /// 让后端 / Gemini 不再靠"我刚发了 RPC"猜测前端状态。
    ///
    /// <b>传输</b>：Reliable DataChannel（IMPL_REF.md §3.1 / §8）；
    /// ParticipantAttributes 暂未确认稳定性（spike S7 待跑）。
    ///
    /// <b>字段</b>：与 <c>sprint4_protocol_v2_ecp.md §5.3 EcpState</c> 对齐 +
    /// 周期上报版本嵌入完整 <see cref="EcpConnectionHealthDto"/>（决策见
    /// <c>INDEX_for_phase3.md §1 #13</c>）。
    /// </summary>
    [Serializable]
    public class EcpStateDto
    {
        public string schema_version = "ecp.v2.alpha";
        public double ts;
        public string unity_identity = "";
        public string room_id = "";

        // body / cognitive
        public string body_state = "";
        public string head_state = "";
        public string cognitive_state = "";

        // command tracking
        public string active_command_id = "";
        public string[] queued_command_ids = new string[0];
        public string[] active_locks = new string[0];
        public string last_ack_id = "";

        // media + AR
        public string video_tier = "";

        // lifecycle
        public string app_lifecycle_state = "";
        public string ar_tracking_state = "";

        // 完整 ConnectionHealth（per-command ack 不带这个，只 4 态摘要进 EcpFrontendStateDto.connection_overall）
        public EcpConnectionHealthDto connection_health;

        public static EcpStateDto BuildHeartbeat(
            string unityIdentity,
            string roomId,
            string appLifecycleState,
            in ConnectionHealthState health,
            string videoTier = null,
            string activeCommandId = null,
            string lastAckId = null)
        {
            double now = (DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalSeconds;
            return new EcpStateDto
            {
                ts = now,
                unity_identity = unityIdentity ?? "",
                room_id = roomId ?? "",
                app_lifecycle_state = appLifecycleState ?? "",
                ar_tracking_state = health.ArTrackingState ?? "",
                video_tier = videoTier ?? health.VideoTier ?? "",
                active_command_id = activeCommandId ?? "",
                last_ack_id = lastAckId ?? "",
                connection_health = EcpConnectionHealthDto.FromSnapshot(health),
            };
        }

        public string ToJson() => JsonUtility.ToJson(this);
    }
}
