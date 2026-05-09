using System;
using System.Collections;
using LiveKit;
using ParrotApp.Config;
using ParrotApp.LiveKit;
using UnityEngine;

namespace ParrotApp.Lifecycle
{
    /// <summary>
    /// START button business flow for the white-box app workspace.
    ///
    /// Flow:
    /// permissions -> token mint -> transition/loading surface -> LiveKit connect
    /// -> main UI. It intentionally does not greet on connect; greeting is gated
    /// by <see cref="ReportGosloPlaced"/>.
    /// </summary>
    public class AppStartupFlowController : MonoBehaviour
    {
        [Header("Runtime Services")]
        [SerializeField] private RoomManager roomManager;
        [SerializeField] private AppLifecycleManager lifecycleManager;
        [SerializeField] private LifecycleShutdownService shutdownService;
        [SerializeField] private LiveKitTokenMintClient tokenMintClient;
        [SerializeField] private MicrophonePublisher microphonePublisher;
        [SerializeField] private ARVideoPublisher videoPublisher;

        [Header("Defaults")]
        [SerializeField] private AppStartupConfigDto defaultConfig = new AppStartupConfigDto();
        [SerializeField] private float connectTimeoutSeconds = 20f;
        [SerializeField] private float brainRpcReadyTimeoutSeconds = 8f;
        [SerializeField] private float brainRpcRetryIntervalSeconds = 0.5f;

        public AppStartupConfigDto ActiveConfig { get; private set; }
        public StartupPermissionSnapshotDto LastPermissionSnapshot { get; private set; }
        public bool StartupInProgress { get; private set; }
        public string LastError { get; private set; } = "";

        public event Action<AppStartupConfigDto> OnTransitionStarted;
        public event Action<AppStartupConfigDto> OnMainUiReady;
        public event Action<string> OnStartupFailed;

        void Awake()
        {
            ResolveServices();
            defaultConfig.Normalize();
            ActiveConfig = defaultConfig;
        }

        public void StartDefault()
        {
            StartFromConfig(defaultConfig);
        }

        public void StartFromJson(string configJson)
        {
            AppStartupConfigDto dto = null;
            try
            {
                dto = string.IsNullOrWhiteSpace(configJson)
                    ? AppStartupConfigDto.Default()
                    : JsonUtility.FromJson<AppStartupConfigDto>(configJson);
            }
            catch (Exception ex)
            {
                Fail($"config_parse_failed:{ex.Message}");
                return;
            }
            StartFromConfig(dto ?? AppStartupConfigDto.Default());
        }

        public void StartFromConfig(AppStartupConfigDto config)
        {
            if (StartupInProgress)
            {
                Debug.LogWarning("[AppStartupFlow] START ignored: startup already in progress");
                return;
            }
            StartCoroutine(RunStartup(config ?? AppStartupConfigDto.Default()));
        }

        public void ApplyCapabilityMode(string mode)
        {
            string normalized = ApplyCapabilityModeLocal(mode);
            StartCoroutine(CallBrainRpc(
                "setAppCapabilityMode",
                $"{{\"mode\":{Quote(normalized)}}}",
                "capability_mode",
                waitForBrain: true));
        }

        private string ApplyCapabilityModeLocal(string mode)
        {
            ResolveServices();
            string normalized = AppCapabilityModeNames.Normalize(mode);
            bool micEnabled = AppCapabilityModeNames.MicrophoneEnabled(normalized);
            bool videoEnabled = AppCapabilityModeNames.VideoEnabled(normalized);

            // Keep this local media gate ahead of the Brain RPC. During startup
            // the room may not exist yet, but the mic/video intent still needs
            // to be settled before publishers see OnRoomConnected.
            microphonePublisher?.SetPublishIntent(micEnabled, normalized);

            if (videoPublisher != null)
            {
                // SessionOnlySilent and VoiceOnlyNoVideo both keep signaling
                // alive while preventing camera frames from reaching Gemini.
                var tier = videoEnabled
                    ? (normalized == AppCapabilityModeNames.FullARCompanion
                        ? ARVideoPublisher.VideoTierLocal.Full
                        : ARVideoPublisher.VideoTierLocal.GeminiOnly)
                    : ARVideoPublisher.VideoTierLocal.Off;
                videoPublisher.ApplyVideoTier(tier);
            }

            return normalized;
        }

        public void EnterSilentKeepAlive()
        {
            // reason: This is not a disconnect path. It keeps the room,
            // heartbeat, DataChannel, and menu RPCs alive while suppressing
            // user audio and Brain-initiated speech through session policy.
            ApplyCapabilityMode(AppCapabilityModeNames.SessionOnlySilent);
        }

        public void RequestDialogueShutdown(string reason = "user_requested_dialogue_shutdown")
        {
            ResolveServices();

            // Mute first so no late audio frame leaks while the graceful
            // chokepoint drains tracks, disconnects, disposes, and cools down.
            microphonePublisher?.SetPublishIntent(false, $"shutdown:{reason}");

            if (shutdownService == null)
            {
                Debug.LogError(
                    "[AppStartupFlow] RequestDialogueShutdown requires LifecycleShutdownService; " +
                    "not calling Room.Disconnect directly.");
                return;
            }

            shutdownService.RequestShutdown(reason);
        }

        public void SwitchWorkspace(string workspaceId)
        {
            if (ActiveConfig == null) ActiveConfig = AppStartupConfigDto.Default();
            ActiveConfig.workspace_id = string.IsNullOrWhiteSpace(workspaceId) ? "mansion_hub" : workspaceId;

            // reason: 2DWorkspace is an in-session surface switch. It must not
            // call LifecycleShutdownService or RoomManager.Disconnect.
            StartCoroutine(CallBrainRpc(
                "applyWorkspace",
                $"{{\"workspace_id\":{Quote(ActiveConfig.workspace_id)}}}",
                "workspace_switch",
                waitForBrain: true));
        }

        public void ReportSceneReady()
        {
            if (ActiveConfig == null) ActiveConfig = AppStartupConfigDto.Default();
            StartCoroutine(CallBrainRpc(
                "onSceneReady",
                BuildPlacementPayload(),
                "scene_ready",
                waitForBrain: true));
        }

        public void ReportGosloPlaced()
        {
            if (ActiveConfig == null) ActiveConfig = AppStartupConfigDto.Default();
            StartCoroutine(CallBrainRpc(
                "onGosloPlaced",
                BuildPlacementPayload(),
                "goslo_placed",
                waitForBrain: true));
        }

        private IEnumerator RunStartup(AppStartupConfigDto config)
        {
            StartupInProgress = true;
            LastError = "";
            ResolveServices();

            ActiveConfig = config;
            ActiveConfig.Normalize();
            ApplyCapabilityModeLocal(ActiveConfig.capability_mode);

            LastPermissionSnapshot = null;
            yield return RequestPermissions(ActiveConfig);
            if (LastPermissionSnapshot == null || !LastPermissionSnapshot.IsOk)
            {
                Fail(LastPermissionSnapshot?.failure_reason ?? "permission_check_failed");
                StartupInProgress = false;
                yield break;
            }

            OnTransitionStarted?.Invoke(ActiveConfig);
            lifecycleManager?.EnterTokenGate();

            if (roomManager != null && roomManager.IsConnected)
            {
                string requestedRoom = ActiveConfig.room_id ?? "";
                string connectedRoom = roomManager.RoomName ?? "";
                if (!string.IsNullOrWhiteSpace(requestedRoom)
                    && !string.IsNullOrWhiteSpace(connectedRoom)
                    && !string.Equals(requestedRoom, connectedRoom, StringComparison.Ordinal))
                {
                    Fail($"livekit_room_already_connected:{connectedRoom}");
                    StartupInProgress = false;
                    yield break;
                }

                bool reusedPolicySynced = false;
                yield return CallBrainRpc(
                    "setAppCapabilityMode",
                    $"{{\"mode\":{Quote(ActiveConfig.capability_mode)}}}",
                    "startup_reuse_capability_mode",
                    waitForBrain: true,
                    onComplete: ok => reusedPolicySynced = ok);
                if (!reusedPolicySynced)
                {
                    lifecycleManager?.ReportDegraded("brain_rpc_policy_sync_timeout");
                    Fail("brain_rpc_policy_sync_timeout");
                    StartupInProgress = false;
                    yield break;
                }

                OnMainUiReady?.Invoke(ActiveConfig);
                StartupInProgress = false;
                yield break;
            }

            string token = ActiveConfig.join_token;
            string url = ActiveConfig.livekit_url;
            if (string.IsNullOrWhiteSpace(token))
            {
                LiveKitTokenMintClient.MintResult mint = default;
                yield return tokenMintClient.Mint(
                    ActiveConfig.room_id,
                    ResolveUnityIdentity(ActiveConfig),
                    result => mint = result);
                if (!mint.Ok)
                {
                    Fail($"token_mint_failed:{mint.Error}");
                    StartupInProgress = false;
                    yield break;
                }
                token = mint.Response.token;
                url = mint.Response.url;
            }

            lifecycleManager?.EnterArSessionStarting();
            roomManager.Connect(token, string.IsNullOrWhiteSpace(url) ? null : url);

            float deadline = Time.realtimeSinceStartup + connectTimeoutSeconds;
            while (roomManager != null && !roomManager.IsConnected
                   && Time.realtimeSinceStartup < deadline)
            {
                yield return null;
            }

            if (roomManager == null || !roomManager.IsConnected)
            {
                Fail("livekit_connect_timeout");
                StartupInProgress = false;
                yield break;
            }

            bool policySynced = false;
            yield return CallBrainRpc(
                "setAppCapabilityMode",
                $"{{\"mode\":{Quote(ActiveConfig.capability_mode)}}}",
                "startup_capability_mode",
                waitForBrain: true,
                onComplete: ok => policySynced = ok);
            if (!policySynced)
            {
                lifecycleManager?.ReportDegraded("brain_rpc_policy_sync_timeout");
                Fail("brain_rpc_policy_sync_timeout");
                StartupInProgress = false;
                yield break;
            }

            OnMainUiReady?.Invoke(ActiveConfig);
            StartupInProgress = false;
        }

        private IEnumerator RequestPermissions(AppStartupConfigDto config)
        {
            lifecycleManager?.EnterPermissionGate();
            var snap = new StartupPermissionSnapshotDto
            {
                microphone_required = AppCapabilityModeNames.MicrophoneEnabled(config.capability_mode),
                camera_required = AppCapabilityModeNames.VideoEnabled(config.capability_mode),
                network_reachable = Application.internetReachability != NetworkReachability.NotReachable,
            };

            if (snap.microphone_required && !Application.HasUserAuthorization(UserAuthorization.Microphone))
                yield return Application.RequestUserAuthorization(UserAuthorization.Microphone);
            snap.microphone_authorized = !snap.microphone_required
                                         || Application.HasUserAuthorization(UserAuthorization.Microphone);

            if (snap.camera_required && !Application.HasUserAuthorization(UserAuthorization.WebCam))
                yield return Application.RequestUserAuthorization(UserAuthorization.WebCam);
            snap.camera_authorized = !snap.camera_required
                                     || Application.HasUserAuthorization(UserAuthorization.WebCam);

            if (!snap.network_reachable) snap.failure_reason = "network_unreachable";
            else if (!snap.microphone_authorized) snap.failure_reason = "microphone_permission_denied";
            else if (!snap.camera_authorized) snap.failure_reason = "camera_permission_denied";

            LastPermissionSnapshot = snap;
        }

        private IEnumerator CallBrainRpc(
            string method,
            string payload,
            string reason,
            bool waitForBrain = false,
            Action<bool> onComplete = null)
        {
            Room room = null;
            string brainId = "";
            float deadline = Time.realtimeSinceStartup + Mathf.Max(0f, brainRpcReadyTimeoutSeconds);

            while (true)
            {
                room = roomManager != null ? roomManager.Room : RoomManager.Instance?.Room;
                if (room != null)
                {
                    brainId = BrainParticipantResolver.FindBrainParticipantId(room);
                    if (!string.IsNullOrEmpty(brainId)) break;
                }

                if (!waitForBrain || Time.realtimeSinceStartup >= deadline)
                {
                    string missing = room == null ? "no room" : "brain not present";
                    Debug.LogWarning($"[AppStartupFlow] RPC {method} skipped: {missing} ({reason})");
                    onComplete?.Invoke(false);
                    yield break;
                }

                // Brain may join slightly after Unity's Room.Connect completes.
                // Keep startup policy synchronization deterministic instead of
                // losing the first RPC during participant discovery.
                yield return new WaitForSeconds(Mathf.Max(0.1f, brainRpcRetryIntervalSeconds));
            }

            var rpcCall = room.LocalParticipant.PerformRpc(new PerformRpcParams
            {
                DestinationIdentity = brainId,
                Method = method,
                Payload = string.IsNullOrEmpty(payload) ? "{}" : payload,
                ResponseTimeout = 3000,
            });
            yield return rpcCall;

            if (rpcCall.IsError)
            {
                Debug.LogWarning($"[AppStartupFlow] RPC {method} failed ({reason}): {rpcCall.Error?.Message}");
                onComplete?.Invoke(false);
                yield break;
            }

            onComplete?.Invoke(true);
        }

        private string BuildPlacementPayload()
        {
            string timeOfDay = DateTime.Now.Hour < 12
                ? "morning"
                : (DateTime.Now.Hour < 18 ? "afternoon" : "evening");
            return "{"
                   + "\"time_of_day\":" + Quote(timeOfDay) + ","
                   + "\"scene_id\":" + Quote(ActiveConfig.scene_id) + ","
                   + "\"workspace_id\":" + Quote(ActiveConfig.workspace_id) + ","
                   + "\"capability_mode\":" + Quote(ActiveConfig.capability_mode)
                   + "}";
        }

        private void ResolveServices()
        {
            if (roomManager == null) roomManager = RoomManager.Instance ?? FindObjectOfType<RoomManager>();
            if (lifecycleManager == null) lifecycleManager = FindObjectOfType<AppLifecycleManager>();
            if (shutdownService == null) shutdownService = FindObjectOfType<LifecycleShutdownService>();
            if (tokenMintClient == null) tokenMintClient = FindObjectOfType<LiveKitTokenMintClient>();
            if (tokenMintClient == null) tokenMintClient = gameObject.AddComponent<LiveKitTokenMintClient>();
            if (microphonePublisher == null) microphonePublisher = FindObjectOfType<MicrophonePublisher>();
            if (videoPublisher == null) videoPublisher = FindObjectOfType<ARVideoPublisher>();
        }

        private string ResolveUnityIdentity(AppStartupConfigDto config)
        {
            if (!string.IsNullOrWhiteSpace(config.unity_identity)) return config.unity_identity;
            string raw = SystemInfo.deviceUniqueIdentifier;
            if (string.IsNullOrWhiteSpace(raw)) raw = SystemInfo.deviceName;
            if (string.IsNullOrWhiteSpace(raw)) raw = Guid.NewGuid().ToString("N");
            string cleaned = raw.Replace(" ", "_").Replace(":", "").Replace("-", "");
            if (string.IsNullOrWhiteSpace(cleaned)) cleaned = Guid.NewGuid().ToString("N");
            return "unity-" + cleaned.Substring(0, Math.Min(24, cleaned.Length));
        }

        private void Fail(string reason)
        {
            LastError = reason ?? "unknown";
            Debug.LogWarning($"[AppStartupFlow] failed: {LastError}");
            OnStartupFailed?.Invoke(LastError);
        }

        private static string Quote(string s)
        {
            if (s == null) return "\"\"";
            return "\"" + s.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";
        }
    }
}
