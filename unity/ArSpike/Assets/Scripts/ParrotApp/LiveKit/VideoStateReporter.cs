using System;
using System.Collections;
using LiveKit;
using ParrotApp.Health;
using ParrotApp.Lifecycle;
using UnityEngine;

namespace ParrotApp.LiveKit
{
    /// <summary>
    /// 旧 <c>onVideoDegraded</c> RPC 路径（Sprint1 T5 继承）的 ArSpike 搬迁版本。<br/>
    /// 双轨灰策略（Sprint4 Phase 3 / L3 Group 3）：
    /// <list type="bullet">
    /// <item>旧 <c>onVideoDegraded</c> RPC 仍发，让 Brain 端的
    ///   <c>VisualStateReason</c> fusion 兼容到 Phase 2 收口
    ///   （ECP event handler 接管前不能断老路径）。</item>
    /// <item>同时灌 <see cref="ConnectionHealthAggregator.ReportVideoLifecycleReason"/>
    ///   做<b>原因细分</b>（<c>track_muted</c> / <c>static_frame</c> /
    ///   <c>app_backgrounded</c>）；<b>不</b>抢 ARVideoPublisher 的
    ///   <c>video_publish_attempted</c> / <c>video_published</c> /
    ///   <c>video_first_frame</c> / <c>video_fresh_frame</c> 字段。</item>
    /// </list>
    ///
    /// <b>注意</b>：本组件订阅 <c>OnApplicationPause</c> 是 Sprint1 行为残留；
    /// AR App 正式生命周期由 <see cref="AppLifecycleManager"/> 统一处置（IMPL_REF.md §1.1）。
    /// 本组件保留 OnApplicationPause 路径只是为了让 Brain 旧 visual fusion 不出现行为回退；
    /// 等 Phase 2 切换到 <c>connection.health.changed</c> 事件链后整段可以删除。
    /// </summary>
    public class VideoStateReporter : MonoBehaviour
    {
        [Header("Target")]
        [Tooltip("Agent identity 前缀，与 _rpc_bridge.UNITY_IDENTITY_PREFIX 互补。")]
        [SerializeField] private string agentIdentityPrefix = "agent-";

        [Header("Timing")]
        [Tooltip("OnApplicationPause(true) 后等多少秒再报 'app_backgrounded'，避免短焦点切换噪音。")]
        [SerializeField] private float pauseReportDelay = 0.5f;

        [Header("Publisher (optional)")]
        [Tooltip("如果绑定，会监听 OnPublishMutedChanged 把 TRACK_MUTED / OK 转发给 Brain。")]
        [SerializeField] private ARVideoPublisher videoPublisher;

        [Tooltip("frame freshness 检查频率（秒）。")]
        [SerializeField] private float frameFreshnessCheckSeconds = 1f;

        [Header("Lifecycle (optional, 灌 health reason 用)")]
        [SerializeField] private AppLifecycleManager lifecycleManager;

        private const string REASON_OK = "ok";
        private const string REASON_APP_BACKGROUNDED = "app_backgrounded";
        private const string REASON_TRACK_MUTED = "track_muted";
        private const string REASON_STATIC_FRAME = "static_frame";
        private const string RPC_METHOD = "onVideoDegraded";

        private ConnectionHealthAggregator HealthAggregator =>
            lifecycleManager != null ? lifecycleManager.HealthAggregator : null;

        private string _lastReportedReason = REASON_OK;
        private Coroutine _pendingPauseReport;
        private float _nextFrameFreshnessCheck;

        void Start()
        {
            if (videoPublisher == null)
                videoPublisher = FindObjectOfType<ARVideoPublisher>();
            if (lifecycleManager == null)
                lifecycleManager = FindObjectOfType<AppLifecycleManager>();

            var rm = RoomManager.Instance;
            if (rm == null)
            {
                Debug.LogError("[VideoStateReporter] RoomManager not found");
                return;
            }

            rm.OnConnected += OnRoomConnected;
            rm.OnDisconnected += OnRoomDisconnected;

            if (videoPublisher != null)
                videoPublisher.OnPublishMutedChanged += OnPublisherMutedChanged;
        }

        private void Update()
        {
            if (videoPublisher == null || Time.unscaledTime < _nextFrameFreshnessCheck) return;

            _nextFrameFreshnessCheck = Time.unscaledTime + Mathf.Max(0.25f, frameFreshnessCheckSeconds);
            if (!videoPublisher.IsPublishing || videoPublisher.IsPublishMuted) return;

            // 与 ParrotDev 同口径的 producer 侧 freshness 检查；不做图像理解。
            TryReport(videoPublisher.HasFreshFrame ? REASON_OK : REASON_STATIC_FRAME);
        }

        private void OnPublisherMutedChanged(bool muted)
        {
            TryReport(muted ? REASON_TRACK_MUTED : REASON_OK);
        }

        private void OnRoomConnected()
        {
            Debug.Log("[VideoStateReporter] Room connected — reporter armed");
            _lastReportedReason = REASON_OK;
        }

        private void OnRoomDisconnected()
        {
            if (_pendingPauseReport != null)
            {
                StopCoroutine(_pendingPauseReport);
                _pendingPauseReport = null;
            }
        }

        void OnApplicationPause(bool paused)
        {
            if (paused)
            {
                if (_pendingPauseReport != null) StopCoroutine(_pendingPauseReport);
                _pendingPauseReport = StartCoroutine(ReportPauseDelayed(REASON_APP_BACKGROUNDED));
            }
            else
            {
                if (_pendingPauseReport != null)
                {
                    StopCoroutine(_pendingPauseReport);
                    _pendingPauseReport = null;
                }
                TryReport(REASON_OK);
            }
        }

        private IEnumerator ReportPauseDelayed(string reason)
        {
            yield return new WaitForSecondsRealtime(pauseReportDelay);
            TryReport(reason);
            _pendingPauseReport = null;
        }

        private void TryReport(string reason)
        {
            if (reason == _lastReportedReason) return;

            // 双轨：旧 RPC 路径（向下兼容）+ 灌 health reason（IMPL_REF.md §4.2）
            // 注意：health reason 字段是"细分"，不是 first-class 状态；ARVideoPublisher
            // 仍然是 video_published / video_fresh_frame 的 sole producer。
            // ok 状态在 HealthAggregator 里以"空字符串"表示无降级原因。
            string healthReason = reason == REASON_OK ? "" : reason;
            HealthAggregator?.ReportVideoLifecycleReason(healthReason, UnixSeconds());

            StartCoroutine(SendReportCoroutine(reason));
        }

        private IEnumerator SendReportCoroutine(string reason)
        {
            var rm = RoomManager.Instance;
            var room = rm?.Room;
            if (room == null || !rm.IsConnected)
            {
                Debug.LogWarning($"[VideoStateReporter] Room not connected — dropping '{reason}'");
                yield break;
            }

            string agentIdentity = FindAgentIdentity(room);
            if (string.IsNullOrEmpty(agentIdentity))
            {
                Debug.Log($"[VideoStateReporter] No agent yet — skipped '{reason}'");
                yield break;
            }

            string payload = $"{{\"reason\":\"{EscapeJson(reason)}\",\"ts\":{UnixSeconds():F3}}}";
            Debug.Log($"[VideoStateReporter] -> {agentIdentity}: {payload}");

            var rpcCall = room.LocalParticipant.PerformRpc(new PerformRpcParams
            {
                DestinationIdentity = agentIdentity,
                Method = RPC_METHOD,
                Payload = payload,
                ResponseTimeout = 3000,
            });

            yield return rpcCall;

            if (rpcCall.IsError)
            {
                Debug.LogWarning(
                    $"[VideoStateReporter] RPC error: {rpcCall.Error?.Code} {rpcCall.Error?.Message}");
            }
            else
            {
                _lastReportedReason = reason;
            }
        }

        private string FindAgentIdentity(Room room)
        {
            var id = BrainParticipantResolver.FindBrainParticipantId(room);
            if (!string.IsNullOrEmpty(id)) return id;
            foreach (var p in room.RemoteParticipants.Values)
            {
                if (!string.IsNullOrEmpty(p.Identity)
                    && p.Identity.StartsWith(agentIdentityPrefix))
                    return p.Identity;
            }
            return null;
        }

        private static double UnixSeconds()
            => (DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalSeconds;

        private static string EscapeJson(string s) =>
            s?.Replace("\\", "\\\\").Replace("\"", "\\\"") ?? "";

        void OnDestroy()
        {
            var rm = RoomManager.Instance;
            if (rm != null)
            {
                rm.OnConnected -= OnRoomConnected;
                rm.OnDisconnected -= OnRoomDisconnected;
            }
            if (videoPublisher != null)
            {
                videoPublisher.OnPublishMutedChanged -= OnPublisherMutedChanged;
            }
        }
    }
}
