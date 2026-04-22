using System;
using System.Collections;
using UnityEngine;
using LiveKit;

/// <summary>
/// Reports producer-side video stream state changes to the Brain via the
/// "onVideoDegraded" RPC (Sprint 1 T5).
///
/// Sprint 1 scope (minimum viable): OnApplicationPause only. AR tracking
/// state is already piped through DataChannel "ar_tracking_state" events
/// (see XRHandTracker / future AR session reporter), so this script does
/// NOT duplicate that route. Brightness variance / blur detection stay on
/// the P3 roadmap.
///
/// RPC contract matches brain/vision/state.py:
///     method  : onVideoDegraded
///     payload : { "reason": "<VisualStateReason.value>", "ts": <unix_sec> }
///     reply   : { "status": "ok" }  (fire-and-forget; Unity never retries)
///
/// Attach to the RoomManager GameObject (or any persistent object in the
/// initial scene). The script auto-hooks into RoomManager.OnConnected.
/// </summary>
public class VideoStateReporter : MonoBehaviour
{
    [Header("Target")]
    [Tooltip("Agent identity prefix to send the RPC to. Matches _rpc_bridge.UNITY_IDENTITY_PREFIX's inverse.")]
    [SerializeField] private string agentIdentityPrefix = "agent-";

    [Header("Timing")]
    [Tooltip("Delay (seconds) between pause-entry and the 'app_backgrounded' RPC. Keeps brief focus blips from noising Gemini.")]
    [SerializeField] private float pauseReportDelay = 0.5f;

    private const string REASON_OK = "ok";
    private const string REASON_APP_BACKGROUNDED = "app_backgrounded";
    private const string RPC_METHOD = "onVideoDegraded";

    private string _lastReportedReason = REASON_OK;
    private Coroutine _pendingPauseReport;

    void Start()
    {
        var rm = RoomManager.Instance;
        if (rm == null)
        {
            Debug.LogError("[VideoStateReporter] RoomManager not found");
            return;
        }

        rm.OnConnected += OnRoomConnected;
        rm.OnDisconnected += OnRoomDisconnected;
    }

    private void OnRoomConnected()
    {
        Debug.Log("[VideoStateReporter] Room connected — reporter armed");
        // Reset internal state at (re)connect time.
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

    /// <summary>
    /// Unity lifecycle: fires when app loses/gains focus (e.g. user switches
    /// app on phone, Unity Editor paused, OS notification overlay).
    /// </summary>
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
            // Expected while Brain is still spawning; don't spam the log.
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
            ResponseTimeout = 3000, // milliseconds
        });

        yield return rpcCall;

        if (rpcCall.IsError)
        {
            // Brain handler shouldn't reject; errors here usually mean the
            // agent went away mid-flight. Leave _lastReportedReason unchanged
            // so the next state transition retries.
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
        foreach (var p in room.RemoteParticipants.Values)
        {
            if (!string.IsNullOrEmpty(p.Identity)
                && p.Identity.StartsWith(agentIdentityPrefix))
            {
                return p.Identity;
            }
        }
        return null;
    }

    private static double UnixSeconds() =>
        (DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalSeconds;

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
    }
}
