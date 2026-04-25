using System;
using System.Threading.Tasks;
using UnityEngine;
using LiveKit;

/// <summary>
/// Receives the Brain's Intent-layer video-tier commands (Sprint 2 T10).
///
/// The Python side <c>brain.perception_supervisor</c> decides when to flip
/// the (video_tier × dsg_mode) combo and pushes the video half here via the
/// RPC <c>setVideoTier</c>. DSG mode changes do NOT come through this path —
/// they live entirely inside the Python Bus and never touch Unity.
///
/// RPC contract (mirrors _rpc_bridge.push_video_tier):
///     method  : setVideoTier
///     payload : { "video_tier": "VIDEO_OFF"|"VIDEO_GEMINI_ONLY"|"VIDEO_FULL"|"VIDEO_BURST",
///                 "reason": "<human-readable cause>" }
///     reply   : { "status": "ok",    "tier": "...",         "applied": <bool> }
///             | { "status": "error", "message": "...",      "tier": "..." }
///
/// Sprint 2 scope (stub, intentional): this script acknowledges the tier
/// change and raises a Unity event so other components (future
/// ARVideoPublisher.SetEncoding) can subscribe. It does NOT re-publish the
/// track with new bitrate/fps — LiveKit Unity SDK PublishTrack options are
/// immutable after publish, so Sprint 3 will handle the actual republish
/// flow together with the AR rebuild. For now a VIDEO_OFF request only
/// mutes the track via <c>SetMuted(true)</c>, which IS supported at
/// runtime and is the one transition that has user-visible value in
/// Sprint 2 (privacy / obstruction states).
///
/// Attach alongside ParrotRpcHandler / ARVideoPublisher on a persistent
/// scene object.
/// </summary>
public class VideoTierReceiver : MonoBehaviour
{
    public enum VideoTier { Unknown, Off, GeminiOnly, Full, Burst }

    /// <summary>Raised on every accepted tier change, on the Unity main thread.</summary>
    public event Action<VideoTier, string> OnTierChanged;

    [Header("Debug")]
    [Tooltip("Log every setVideoTier payload as it arrives.")]
    [SerializeField] private bool verboseLogging = true;

    [Header("Track control (optional)")]
    [Tooltip("If assigned, VIDEO_OFF will mute the publisher's track and any higher tier will unmute it. Leave null during dev if you don't want the stream to disappear.")]
    [SerializeField] private ARVideoPublisher videoPublisher;

    private const string RPC_METHOD = "setVideoTier";

    /// <summary>Avoid duplicate <c>RegisterRpcMethod</c> if <see cref="RoomManager.OnConnected"/> fires again for the same <see cref="Room"/>.</summary>
    private Room _rpcRegisteredOnRoom;

    private VideoTier _currentTier = VideoTier.Unknown;

    public VideoTier CurrentTier => _currentTier;

    void Start()
    {
        if (videoPublisher == null)
            videoPublisher = UnityEngine.Object.FindObjectOfType<ARVideoPublisher>();

        if (videoPublisher == null)
            Debug.LogWarning("[VideoTierReceiver] No ARVideoPublisher in scene — setVideoTier will log tier only (no track control).");

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
        if (_rpcRegisteredOnRoom == room)
            return;

        _rpcRegisteredOnRoom = room;
        room.LocalParticipant.RegisterRpcMethod(RPC_METHOD, HandleSetVideoTier);
        Debug.Log("[VideoTierReceiver] Registered: setVideoTier");
    }

    private async Task<string> HandleSetVideoTier(RpcInvocationData data)
    {
        if (verboseLogging)
        {
            Debug.Log($"[VideoTierReceiver] setVideoTier <- {data.CallerIdentity}: {data.Payload}");
        }

        try
        {
            var p = JsonUtility.FromJson<SetVideoTierPayload>(data.Payload);
            var tier = ParseTier(p.video_tier);
            if (tier == VideoTier.Unknown)
            {
                var msg = $"Unknown video_tier value: {p.video_tier}";
                Debug.LogWarning($"[VideoTierReceiver] {msg}");
                return $"{{\"status\":\"error\",\"message\":\"{EscapeJson(msg)}\",\"tier\":\"{EscapeJson(p.video_tier)}\"}}";
            }

            var tcs = new TaskCompletionSource<bool>();
            UnityMainThread.Enqueue(() =>
            {
                try
                {
                    ApplyTier(tier, p.reason);
                    tcs.SetResult(true);
                }
                catch (Exception ex)
                {
                    tcs.SetException(ex);
                }
            });
            await tcs.Task;

            return $"{{\"status\":\"ok\",\"tier\":\"{EscapeJson(p.video_tier)}\",\"applied\":true}}";
        }
        catch (Exception e)
        {
            Debug.LogError($"[VideoTierReceiver] setVideoTier error: {e.Message}");
            return $"{{\"status\":\"error\",\"message\":\"{EscapeJson(e.Message)}\"}}";
        }
    }

    /// <summary>
    /// Sprint 3: apply tier by delegating to ARVideoPublisher.ApplyVideoTier
    /// which handles both mute (VIDEO_OFF) and full track rebuilds
    /// (VIDEO_GEMINI_ONLY ↔ VIDEO_FULL) via UnpublishTrack → PublishTrack.
    /// </summary>
    private void ApplyTier(VideoTier tier, string reason)
    {
        var previous = _currentTier;
        _currentTier = tier;

        if (videoPublisher != null)
        {
            // Map VideoTierReceiver.VideoTier → ARVideoPublisher.VideoTierLocal
            var localTier = tier switch
            {
                VideoTier.Off        => ARVideoPublisher.VideoTierLocal.Off,
                VideoTier.GeminiOnly => ARVideoPublisher.VideoTierLocal.GeminiOnly,
                VideoTier.Full       => ARVideoPublisher.VideoTierLocal.Full,
                VideoTier.Burst      => ARVideoPublisher.VideoTierLocal.Burst,
                _                    => ARVideoPublisher.VideoTierLocal.Unknown,
            };

            if (localTier != ARVideoPublisher.VideoTierLocal.Unknown)
                videoPublisher.ApplyVideoTier(localTier);
        }

        Debug.Log($"[VideoTierReceiver] tier {previous} → {tier} (reason={reason ?? "-"})");
        OnTierChanged?.Invoke(tier, reason);
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

    private static string EscapeJson(string s) =>
        s?.Replace("\\", "\\\\").Replace("\"", "\\\"") ?? "";

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
    }
}
