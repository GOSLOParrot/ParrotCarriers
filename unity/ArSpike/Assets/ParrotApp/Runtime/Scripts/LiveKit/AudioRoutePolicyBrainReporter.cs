using System;
using System.Collections;
using LiveKit;
using UnityEngine;

namespace ParrotApp.LiveKit
{
    /// <summary>
    /// Reports Unity's current phone audio route policy to Brain after LiveKit
    /// connection.
    ///
    /// The detector/publisher still own local mic rebuilding. This component is
    /// the formal Brain producer for the compact `setLineBAudioRoutePolicy`
    /// RPC, so LineB can update `session/audio_route_policy` without guessing
    /// from server-side defaults.
    /// </summary>
    public class AudioRoutePolicyBrainReporter : MonoBehaviour
    {
        private const string RpcMethod = "setLineBAudioRoutePolicy";

        [SerializeField] private RoomManager roomManager;
        [SerializeField] private AudioRouteDetector routeDetector;
        [SerializeField] private MicrophonePublisher microphonePublisher;
        [SerializeField] private float reportDebounceSeconds = 0.4f;
        [SerializeField] private float brainReadyTimeoutSeconds = 6f;

        public int ReportAttemptCount { get; private set; }
        public int ReportSuccessCount { get; private set; }
        public string LastReportError { get; private set; } = "";
        public string LastPayload { get; private set; } = "";

        private Coroutine _reportCoroutine;
        private Action<RemoteParticipant> _participantConnectedHandler;

        void Start()
        {
            ResolveServices();
            if (routeDetector != null)
                routeDetector.OnRouteChanged += OnRouteChanged;
            if (roomManager != null)
            {
                roomManager.OnConnected += OnRoomConnected;
                _participantConnectedHandler = _ => QueueReport("brain_participant_connected");
                roomManager.OnParticipantConnected += _participantConnectedHandler;
                if (roomManager.IsConnected)
                    QueueReport("start_connected");
            }
        }

        void OnDestroy()
        {
            if (routeDetector != null)
                routeDetector.OnRouteChanged -= OnRouteChanged;
            if (roomManager != null)
            {
                roomManager.OnConnected -= OnRoomConnected;
                if (_participantConnectedHandler != null)
                    roomManager.OnParticipantConnected -= _participantConnectedHandler;
            }
        }

        public void ReportCurrentPolicy(string reason = "manual")
        {
            QueueReport(reason);
        }

        private void OnRoomConnected()
        {
            QueueReport("room_connected");
        }

        private void OnRouteChanged(AudioRoutePolicy oldPolicy, AudioRoutePolicy newPolicy)
        {
            QueueReport($"route_changed:{oldPolicy.RouteName}_to_{newPolicy.RouteName}");
        }

        private void QueueReport(string reason)
        {
            if (_reportCoroutine != null)
                StopCoroutine(_reportCoroutine);
            _reportCoroutine = StartCoroutine(ReportAfterDebounce(reason ?? "unknown"));
        }

        private IEnumerator ReportAfterDebounce(string reason)
        {
            if (reportDebounceSeconds > 0f)
                yield return new WaitForSeconds(reportDebounceSeconds);

            ResolveServices();
            ReportAttemptCount++;

            var room = roomManager != null ? roomManager.Room : RoomManager.Instance?.Room;
            if (room == null || roomManager == null || !roomManager.IsConnected)
            {
                LastReportError = "room_not_connected";
                _reportCoroutine = null;
                yield break;
            }

            string brainId = "";
            float deadline = Time.realtimeSinceStartup + Mathf.Max(0f, brainReadyTimeoutSeconds);
            while (string.IsNullOrEmpty(brainId) && Time.realtimeSinceStartup < deadline)
            {
                brainId = BrainParticipantResolver.FindBrainParticipantId(room);
                if (!string.IsNullOrEmpty(brainId)) break;
                yield return new WaitForSeconds(0.25f);
            }

            if (string.IsNullOrEmpty(brainId))
            {
                LastReportError = "brain_not_present";
                _reportCoroutine = null;
                yield break;
            }

            var policy = routeDetector != null ? routeDetector.DetectNow() : AudioRoutePolicy.Default();
            LastPayload = BuildPayload(policy, reason);

            var rpcCall = room.LocalParticipant.PerformRpc(new PerformRpcParams
            {
                DestinationIdentity = brainId,
                Method = RpcMethod,
                Payload = LastPayload,
                ResponseTimeout = 3000,
            });
            yield return rpcCall;

            if (rpcCall.IsError)
            {
                LastReportError = rpcCall.Error != null ? rpcCall.Error.Message : "rpc_transport_error";
                _reportCoroutine = null;
                yield break;
            }

            if (!IsBusinessOk(rpcCall.Payload))
            {
                LastReportError = "rpc_business_error";
                _reportCoroutine = null;
                yield break;
            }

            LastReportError = "";
            ReportSuccessCount++;
            _reportCoroutine = null;
        }

        private string BuildPayload(AudioRoutePolicy policy, string reason)
        {
            bool micEnabled = microphonePublisher == null || microphonePublisher.PublishIntentEnabled;
            bool speakerOutput = policy.Kind == AudioRouteKind.Speaker;
            string inputRoute = InputRouteFor(policy);
            string outputRoute = policy.RouteName;
            return "{"
                   + "\"input_route\":" + Quote(inputRoute) + ","
                   + "\"output_route\":" + Quote(outputRoute) + ","
                   + "\"microphone_enabled\":" + (micEnabled ? "true" : "false") + ","
                   + "\"speaker_output_enabled\":" + (speakerOutput ? "true" : "false") + ","
                   + "\"echo_handling_mode\":\"\","
                   + "\"voiceprint_enabled\":false,"
                   + "\"speaker_state\":\"monitoring\","
                   + "\"source\":\"unity_audio_route_policy\","
                   + "\"reason\":" + Quote(reason)
                   + "}";
        }

        private static string InputRouteFor(AudioRoutePolicy policy)
        {
            switch (policy.Kind)
            {
                case AudioRouteKind.BluetoothSco:
                    return "bluetooth_sco";
                case AudioRouteKind.WiredHeadset:
                    return "wired_headset";
                default:
                    return "system_default_microphone";
            }
        }

        private static bool IsBusinessOk(string payload)
        {
            if (string.IsNullOrWhiteSpace(payload)) return true;
            try
            {
                var status = JsonUtility.FromJson<RpcStatusEnvelope>(payload);
                return status == null
                       || !string.Equals(status.status, "error", StringComparison.OrdinalIgnoreCase);
            }
            catch (Exception)
            {
                return true;
            }
        }

        private void ResolveServices()
        {
            if (roomManager == null) roomManager = RoomManager.Instance ?? FindObjectOfType<RoomManager>();
            if (routeDetector == null) routeDetector = FindObjectOfType<AudioRouteDetector>();
            if (microphonePublisher == null) microphonePublisher = FindObjectOfType<MicrophonePublisher>();
        }

        private static string Quote(string value)
        {
            if (value == null) return "\"\"";
            return "\"" + value.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";
        }

        [Serializable]
        private class RpcStatusEnvelope
        {
            public string status = "";
        }
    }
}
