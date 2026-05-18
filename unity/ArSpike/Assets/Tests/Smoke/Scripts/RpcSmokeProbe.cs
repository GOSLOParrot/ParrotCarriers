#if UNITY_EDITOR || DEVELOPMENT_BUILD
using System;
using System.Collections;
using System.Text;
using System.Threading.Tasks;
using LiveKit;
using ParrotApp.LiveKit;
using UnityEngine;

namespace ParrotApp.Tests.Smoke
{
    /// <summary>
    /// Development-only LiveKit RPC probe.
    ///
    /// This is intentionally kept under Assets/Tests/Smoke so formal App RPC
    /// ownership stays in ParrotApp.Runtime. Add it to a temporary GameObject
    /// in Play Mode or a smoke scene, then run the context menu command.
    /// </summary>
    public sealed class RpcSmokeProbe : MonoBehaviour
    {
        private const string Source = "unity_rpc_smoke_probe";

        [Header("Room")]
        [SerializeField] private RoomManager roomManager;
        [SerializeField] private bool runOnConnected;
        [SerializeField] private float brainWaitSeconds = 8f;
        [SerializeField] private int responseTimeoutMs = 3000;

        [Header("Probe Calls")]
        [SerializeField] private bool registerLocalEchoMethod = true;
        [SerializeField] private string localEchoMethod = "unitySmokeProbeEcho";
        [SerializeField] private bool callSceneReady = true;
        [SerializeField] private bool callCameraOff = true;
        [SerializeField] private bool callXrHandOff = true;

        public string LastBrainIdentity { get; private set; } = "";
        public string LastSummary { get; private set; } = "not_run";
        public string LastError { get; private set; } = "";
        public string LastRawResponse { get; private set; } = "";

        private Coroutine _running;
        private Room _echoRegisteredRoom;

        private void OnEnable()
        {
            BindRoomManager();
            if (roomManager != null)
            {
                roomManager.OnConnected -= HandleConnected;
                roomManager.OnConnected += HandleConnected;
                roomManager.OnDisconnected -= HandleDisconnected;
                roomManager.OnDisconnected += HandleDisconnected;
                if (roomManager.IsConnected)
                    HandleConnected();
            }
        }

        private void OnDisable()
        {
            if (roomManager != null)
            {
                roomManager.OnConnected -= HandleConnected;
                roomManager.OnDisconnected -= HandleDisconnected;
            }
        }

        [ContextMenu("RPC Smoke: Run Probe")]
        public void RunProbeFromContextMenu()
        {
            RunProbeNow();
        }

        public void RunProbeNow()
        {
            if (_running != null)
                StopCoroutine(_running);
            _running = StartCoroutine(RunProbe("manual"));
        }

        private void HandleConnected()
        {
            TryRegisterLocalEcho();
            if (runOnConnected)
                RunProbeNow();
        }

        private void HandleDisconnected()
        {
            _echoRegisteredRoom = null;
            LastSummary = "room_disconnected";
        }

        private IEnumerator RunProbe(string reason)
        {
            BindRoomManager();
            LastError = "";
            LastRawResponse = "";
            LastSummary = "running";

            var room = roomManager != null ? roomManager.Room : null;
            if (room == null || roomManager == null || !roomManager.IsConnected)
            {
                Fail("room_not_connected");
                _running = null;
                yield break;
            }

            TryRegisterLocalEcho();
            LogRoomSnapshot(room, reason);

            string brainId = "";
            float deadline = Time.realtimeSinceStartup + Mathf.Max(0.1f, brainWaitSeconds);
            while (string.IsNullOrEmpty(brainId) && Time.realtimeSinceStartup < deadline)
            {
                brainId = BrainParticipantResolver.FindBrainParticipantId(room);
                if (!string.IsNullOrEmpty(brainId))
                    break;
                yield return new WaitForSeconds(0.25f);
            }

            if (string.IsNullOrEmpty(brainId))
            {
                Fail("brain_not_present");
                _running = null;
                yield break;
            }

            LastBrainIdentity = brainId;
            int ok = 0;
            int failed = 0;

            if (callSceneReady)
                yield return CallBrain(room, brainId, "onSceneReady",
                    "{\"source\":\"" + Source + "\",\"reason\":\"" + EscapeJson(reason) + "\"}",
                    result => Count(result, ref ok, ref failed));

            if (callCameraOff)
                yield return CallBrain(room, brainId, "setCameraMode",
                    "{\"mode\":\"off\",\"source\":\"" + Source + "\"}",
                    result => Count(result, ref ok, ref failed));

            if (callXrHandOff)
                yield return CallBrain(room, brainId, "setXrHandMode",
                    "{\"mode\":\"off\",\"source\":\"" + Source + "\"}",
                    result => Count(result, ref ok, ref failed));

            LastSummary = failed == 0
                ? $"ok calls={ok} brain={brainId}"
                : $"failed ok={ok} failed={failed} brain={brainId} last_error={LastError}";
            Debug.Log($"[RpcSmokeProbe] DONE {LastSummary}");
            _running = null;
        }

        private IEnumerator CallBrain(
            Room room,
            string brainId,
            string method,
            string payload,
            Action<bool> onComplete)
        {
            float started = Time.realtimeSinceStartup;
            Debug.Log($"[RpcSmokeProbe] -> {brainId}.{method} payload={payload}");

            var rpcCall = room.LocalParticipant.PerformRpc(new PerformRpcParams
            {
                DestinationIdentity = brainId,
                Method = method,
                Payload = payload,
                ResponseTimeout = Mathf.Max(500, responseTimeoutMs),
            });

            yield return rpcCall;

            float elapsedMs = (Time.realtimeSinceStartup - started) * 1000f;
            if (rpcCall.IsError)
            {
                string transportError = rpcCall.Error != null
                    ? $"{rpcCall.Error.Code}:{rpcCall.Error.Message}"
                    : "rpc_transport_error";
                LastError = $"{method}:transport:{transportError}";
                Debug.LogWarning(
                    $"[RpcSmokeProbe] FAIL method={method} transport={transportError} elapsed_ms={elapsedMs:0}");
                onComplete?.Invoke(false);
                yield break;
            }

            string response = rpcCall.Payload ?? "";
            LastRawResponse = response;
            if (IsBusinessError(response, out string status, out string reason))
            {
                LastError = $"{method}:business:{status}:{reason}";
                Debug.LogWarning(
                    $"[RpcSmokeProbe] FAIL method={method} business_status={status} " +
                    $"reason={reason} elapsed_ms={elapsedMs:0} raw={response}");
                onComplete?.Invoke(false);
                yield break;
            }

            Debug.Log(
                $"[RpcSmokeProbe] OK method={method} elapsed_ms={elapsedMs:0} raw={response}");
            onComplete?.Invoke(true);
        }

        private void TryRegisterLocalEcho()
        {
            if (!registerLocalEchoMethod)
                return;

            BindRoomManager();
            var room = roomManager != null ? roomManager.Room : null;
            if (room == null || room.LocalParticipant == null)
                return;
            if (_echoRegisteredRoom == room)
                return;

            try
            {
                room.LocalParticipant.RegisterRpcMethod(localEchoMethod, HandleLocalEcho);
                _echoRegisteredRoom = room;
                Debug.Log($"[RpcSmokeProbe] Registered local echo RPC: {localEchoMethod}");
            }
            catch (Exception ex)
            {
                LastError = "local_echo_register:" + ex.Message;
                Debug.LogWarning($"[RpcSmokeProbe] Local echo register failed: {ex.Message}");
            }
        }

        private Task<string> HandleLocalEcho(RpcInvocationData data)
        {
            string caller = data != null ? data.CallerIdentity : "";
            string payload = data != null ? data.Payload : "";
            string response = "{\"status\":\"ok\",\"method\":\"" + EscapeJson(localEchoMethod)
                              + "\",\"caller\":\"" + EscapeJson(caller)
                              + "\",\"payload\":\"" + EscapeJson(payload) + "\"}";
            Debug.Log($"[RpcSmokeProbe] local echo <- {caller}: {payload}");
            return Task.FromResult(response);
        }

        private void BindRoomManager()
        {
            if (roomManager == null)
                roomManager = RoomManager.Instance ?? FindObjectOfType<RoomManager>();
        }

        private void LogRoomSnapshot(Room room, string reason)
        {
            var participants = new StringBuilder();
            if (room != null && room.RemoteParticipants != null)
            {
                foreach (var participant in room.RemoteParticipants.Values)
                {
                    if (participants.Length > 0)
                        participants.Append(",");
                    participants.Append(participant.Identity);
                }
            }

            string local = room?.LocalParticipant?.Identity ?? "";
            Debug.Log(
                $"[RpcSmokeProbe] room='{room?.Name}' local='{local}' reason='{reason}' " +
                $"remote_count={room?.RemoteParticipants?.Count ?? 0} remotes=[{participants}]");
        }

        private void Fail(string reason)
        {
            LastError = reason;
            LastSummary = "failed:" + reason;
            Debug.LogWarning($"[RpcSmokeProbe] FAIL {reason}");
        }

        private static void Count(bool ok, ref int okCount, ref int failedCount)
        {
            if (ok) okCount++;
            else failedCount++;
        }

        private static bool IsBusinessError(string payload, out string status, out string reason)
        {
            status = "";
            reason = "";
            if (string.IsNullOrWhiteSpace(payload))
                return false;

            try
            {
                var envelope = JsonUtility.FromJson<RpcStatusEnvelope>(payload);
                if (envelope == null)
                    return false;
                status = envelope.status ?? "";
                reason = !string.IsNullOrWhiteSpace(envelope.reason)
                    ? envelope.reason
                    : envelope.message ?? "";
                return string.Equals(status, "error", StringComparison.OrdinalIgnoreCase);
            }
            catch (Exception)
            {
                return false;
            }
        }

        private static string EscapeJson(string value)
        {
            return (value ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"");
        }

        [Serializable]
        private sealed class RpcStatusEnvelope
        {
            public string status = "";
            public string reason = "";
            public string message = "";
        }
    }
}
#endif
