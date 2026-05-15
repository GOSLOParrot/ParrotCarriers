using System;
using System.Threading.Tasks;
using LiveKit;
using ParrotApp.Core;
using UnityEngine;

namespace ParrotApp.LiveKit
{
    /// <summary>
    /// 接收 Brain Intent 层 <c>setVideoTier</c> 命令并委托给
    /// <see cref="ARVideoPublisher.ApplyVideoTier"/>。<br/>
    /// 从 ParrotDev 搬迁（Sprint4 Phase 3 / L3 Group 4），保留 ECP-minimal 已落地的所有行为：
    /// <list type="bullet">
    /// <item><c>expires_at</c> 校验 → <see cref="EcpAckJson.Expired"/>。</item>
    /// <item><c>unknown_tier</c> / <c>no_video_publisher</c> 等 reason 走
    ///   <see cref="EcpAckJson.Rejected"/>。</item>
    /// <item>成功路径走 <see cref="EcpAckJson.Completed"/>，<c>frontend_state.video_tier</c>
    ///   带 wire 字符串。</item>
    /// </list>
    /// 增量：命名空间收口为 <c>ParrotApp.LiveKit</c>。本类<b>不</b>灌
    /// <c>video_tier</c> health 字段（<see cref="ARVideoPublisher"/> 已是 sole producer）。
    /// </summary>
    public class VideoTierReceiver : MonoBehaviour
    {
        public enum VideoTier { Unknown, Off, GeminiOnly, Full, Burst }

        public event Action<VideoTier, string> OnTierChanged;

        [Header("Debug")]
        [SerializeField] private bool verboseLogging = true;

        [Header("Track control (optional)")]
        [Tooltip("绑定后 VIDEO_OFF mute 该轨；其他档位 unmute。")]
        [SerializeField] private ARVideoPublisher videoPublisher;

        private const string RPC_METHOD = "setVideoTier";
        private const double ExpiredWarningMinIntervalSeconds = 10.0;

        private Room _rpcRegisteredOnRoom;

        // Brain 默认 Blackboard combo 是 VIDEO_GEMINI_ONLY。
        private VideoTier _currentTier = VideoTier.GeminiOnly;
        private DateTime _lastExpiredWarningUtc = DateTime.MinValue;
        private int _suppressedExpiredWarnings;

        public VideoTier CurrentTier => _currentTier;

        void Start()
        {
            if (videoPublisher == null)
                videoPublisher = FindObjectOfType<ARVideoPublisher>();

            if (videoPublisher == null)
                Debug.LogWarning("[VideoTierReceiver] No ARVideoPublisher in scene — setVideoTier will log tier only");

            var rm = RoomManager.Instance;
            if (rm == null)
            {
                Debug.LogError("[VideoTierReceiver] RoomManager not found");
                return;
            }

            rm.OnConnected += Register;
            if (rm.IsConnected) Register();
        }

        private void Register()
        {
            var room = RoomManager.Instance?.Room;
            if (room == null) return;
            if (_rpcRegisteredOnRoom == room) return;

            _rpcRegisteredOnRoom = room;
            room.LocalParticipant.RegisterRpcMethod(RPC_METHOD, HandleSetVideoTier);
            Debug.Log("[VideoTierReceiver] Registered: setVideoTier");
        }

        private async Task<string> HandleSetVideoTier(RpcInvocationData data)
        {
            if (verboseLogging)
                Debug.Log($"[VideoTierReceiver] setVideoTier <- {data.CallerIdentity}: {data.Payload}");

            SetVideoTierPayload p = default;
            try
            {
                p = JsonUtility.FromJson<SetVideoTierPayload>(data.Payload);

                if (p._ecp != null && p._ecp.IsExpired(EcpAckJson.UnixSeconds()))
                {
                    LogExpiredCommand(p._ecp.command_id);
                    return EcpAckJson.Expired(p._ecp, $"tier={p.video_tier}");
                }

                var tier = ParseTier(p.video_tier);
                if (tier == VideoTier.Unknown)
                {
                    var msg = $"Unknown video_tier value: {p.video_tier}";
                    Debug.LogWarning($"[VideoTierReceiver] {msg}");
                    return EcpAckJson.Rejected(p._ecp, EcpAckJson.ReasonUnknownTier, msg);
                }

                if (videoPublisher == null)
                {
                    var msg = "No ARVideoPublisher in scene";
                    Debug.LogWarning($"[VideoTierReceiver] {msg}");
                    return EcpAckJson.Rejected(p._ecp, EcpAckJson.ReasonNoVideoPublisher, msg);
                }

                var tcs = new TaskCompletionSource<ARVideoPublisher.TierApplyResult>();
                UnityMainThread.Enqueue(() =>
                {
                    try
                    {
                        ApplyTier(tier, p.reason, result => tcs.TrySetResult(result));
                    }
                    catch (Exception ex)
                    {
                        tcs.TrySetException(ex);
                    }
                });
                var apply = await tcs.Task;

                if (!apply.Ok)
                    return EcpAckJson.Rejected(p._ecp, apply.Reason, apply.Detail);

                return EcpAckJson.Completed(
                    p._ecp,
                    EcpFrontendStateDto.ForVideoTier(p.video_tier, p._ecp?.command_id),
                    reason: apply.Reason
                );
            }
            catch (Exception e)
            {
                Debug.LogError($"[VideoTierReceiver] setVideoTier error: {e.Message}");
                return EcpAckJson.Failed(p._ecp, e.Message);
            }
        }

        private void ApplyTier(VideoTier tier, string reason, Action<ARVideoPublisher.TierApplyResult> onComplete)
        {
            var previous = _currentTier;

            var localTier = tier switch
            {
                VideoTier.Off => ARVideoPublisher.VideoTierLocal.Off,
                VideoTier.GeminiOnly => ARVideoPublisher.VideoTierLocal.GeminiOnly,
                VideoTier.Full => ARVideoPublisher.VideoTierLocal.Full,
                VideoTier.Burst => ARVideoPublisher.VideoTierLocal.Burst,
                _ => ARVideoPublisher.VideoTierLocal.Unknown,
            };

            if (localTier == ARVideoPublisher.VideoTierLocal.Unknown)
            {
                onComplete?.Invoke(new ARVideoPublisher.TierApplyResult(false, "unknown_tier", tier.ToString()));
                return;
            }

            videoPublisher.ApplyVideoTier(localTier, result =>
            {
                if (result.Ok)
                {
                    _currentTier = tier;
                    Debug.Log($"[VideoTierReceiver] tier {previous} → {tier} (reason={reason ?? "-"}, applied={result.Reason})");
                    OnTierChanged?.Invoke(tier, reason);
                }
                else
                {
                    Debug.LogWarning($"[VideoTierReceiver] tier {previous} → {tier} failed ({result.Reason}: {result.Detail})");
                }
                onComplete?.Invoke(result);
            });
        }

        private void LogExpiredCommand(string commandId)
        {
            var now = DateTime.UtcNow;
            if ((now - _lastExpiredWarningUtc).TotalSeconds >= ExpiredWarningMinIntervalSeconds)
            {
                string suffix = _suppressedExpiredWarnings > 0
                    ? " (suppressed " + _suppressedExpiredWarnings + " similar expired commands)"
                    : "";
                Debug.LogWarning("[VideoTierReceiver] setVideoTier expired (command_id=" + commandId + ")" + suffix);
                _suppressedExpiredWarnings = 0;
                _lastExpiredWarningUtc = now;
                return;
            }

            _suppressedExpiredWarnings++;
        }

        private static VideoTier ParseTier(string raw)
        {
            if (string.IsNullOrEmpty(raw)) return VideoTier.Unknown;
            switch (raw)
            {
                case "VIDEO_OFF": return VideoTier.Off;
                case "VIDEO_GEMINI_ONLY": return VideoTier.GeminiOnly;
                case "VIDEO_FULL": return VideoTier.Full;
                case "VIDEO_BURST": return VideoTier.Burst;
                default: return VideoTier.Unknown;
            }
        }

        void OnDestroy()
        {
            var rm = RoomManager.Instance;
            if (rm != null) rm.OnConnected -= Register;
            _rpcRegisteredOnRoom = null;
        }

        [Serializable]
        private struct SetVideoTierPayload
        {
            public string video_tier;
            public string reason;
            public EcpCommandDto _ecp;
        }
    }
}
