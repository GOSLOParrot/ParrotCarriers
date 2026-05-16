using System;
using System.Collections;
using LiveKit;
using ParrotApp.Backend;
using ParrotApp.Config;
using ParrotApp.Ecp;
using ParrotApp.LiveKit;
using ParrotApp.UI;
using UnityEngine;

namespace ParrotApp.Lifecycle
{
    /// <summary>
    /// START button business flow for the white-box app workspace.
    ///
    /// Flow:
    /// permissions -> transition/loading surface -> Tier 1 runtime prewrite
    /// -> App HTTP RoomSetting apply -> token mint -> LiveKit connect
    /// -> Brain RPC sync -> main-ready hold screen. It intentionally does not
    /// greet on connect; greeting is gated by <see cref="ReportGosloPlaced"/>.
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
        [SerializeField] private OrchestratorClient orchestratorClient;
        [SerializeField] private AppRoomSettingClient roomSettingClient;
        [SerializeField] private AppHomeMenuClient homeMenuClient;
        [SerializeField] private LifecycleHeartbeatPublisher heartbeatPublisher;
        [SerializeField] private EcpEventPublisher ecpEventPublisher;
        [SerializeField] private FormalMainReadyGate mainReadyGate;
        [SerializeField] private FormalHomeHudController homeHudController;
        [SerializeField] private FormalHomeMenuLoader homeMenuLoader;
        [SerializeField] private FormalHomeMenuController homeMenuController;
        [SerializeField] private FormalHomeToolController homeToolController;
        [SerializeField] private FormalModelReadyReporter modelReadyReporter;
        [SerializeField] private FormalModelPlacementController modelPlacementController;
        [SerializeField] private FormalModelRemoteController modelRemoteController;
        [SerializeField] private FormalXrHandPerchController xrHandPerchController;
        [SerializeField] private FormalArRuntimeBootstrap arRuntimeBootstrap;
        [SerializeField] private FormalArSessionBaselineReporter arSessionBaselineReporter;

        [Header("Defaults")]
        [SerializeField] private AppStartupConfigDto defaultConfig = new AppStartupConfigDto();
        [SerializeField] private float connectTimeoutSeconds = 20f;
        [SerializeField] private float brainRpcReadyTimeoutSeconds = 8f;
        [SerializeField] private float brainRpcRetryIntervalSeconds = 0.5f;
        [SerializeField] private float tierOneReconnectShutdownTimeoutSeconds = 18f;

        public AppStartupConfigDto ActiveConfig { get; private set; }
        public StartupPermissionSnapshotDto LastPermissionSnapshot { get; private set; }
        public bool StartupInProgress { get; private set; }
        public bool FreshReconnectInProgress => _freshReconnectCoroutine != null;
        public bool MainUiReadyOnce => _mainUiReadyOnce;
        public string LastError { get; private set; } = "";
        public string LastBrainRpcStatus { get; private set; } = "not_sent";

        public event Action<AppStartupConfigDto> OnTransitionStarted;
        public event Action<AppStartupConfigDto> OnMainUiReady;
        public event Action<string> OnStartupFailed;
        public event Action<string> OnWorkspaceSwitchApplied;
        public event Action<string> OnWorkspaceSwitchFailed;
        public event Action<string, string> OnCompactControlApplied;
        public event Action<string, string> OnCompactControlFailed;

        private Coroutine _startupCoroutine;
        private Coroutine _freshReconnectCoroutine;
        private Coroutine _workspaceSwitchCoroutine;
        private bool _hasQueuedWorkspaceSwitch;
        private string _queuedWorkspaceId = "";
        private string _queuedWorkspaceLayoutKind = "";
        private string _confirmedWorkspaceId = "";
        private string _confirmedCapabilityMode = "";
        private bool _mainUiReadyOnce;

        void Awake()
        {
            ResolveServices();
            defaultConfig.Normalize();
            ActiveConfig = defaultConfig;
            RecordConfirmedSessionState();
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
            _startupCoroutine = StartCoroutine(RunStartup(config ?? AppStartupConfigDto.Default()));
        }

        public void CancelStartup(string reason = "startup_cancelled")
        {
            if (_startupCoroutine != null)
            {
                StopCoroutine(_startupCoroutine);
                _startupCoroutine = null;
            }
            if (_freshReconnectCoroutine != null)
            {
                StopCoroutine(_freshReconnectCoroutine);
                _freshReconnectCoroutine = null;
            }
            StartupInProgress = false;
            LastError = reason ?? "startup_cancelled";
            lifecycleManager?.ReportDegraded(LastError);
            Debug.LogWarning($"[AppStartupFlow] START cancelled: {LastError}");
        }

        public bool RequestFreshTokenReconnect(string reason = "fresh_token_reconnect")
        {
            if (!_mainUiReadyOnce)
            {
                LastError = "fresh_reconnect_rejected_before_main_ready";
                return false;
            }
            if (StartupInProgress || _freshReconnectCoroutine != null)
            {
                LastError = "fresh_reconnect_rejected_startup_in_progress";
                return false;
            }

            _freshReconnectCoroutine = StartCoroutine(RunFreshTokenReconnect(reason));
            return true;
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
            SwitchWorkspace(workspaceId, "");
        }

        public void SwitchWorkspace(string workspaceId, string layoutKind)
        {
            if (_workspaceSwitchCoroutine != null)
            {
                _queuedWorkspaceId = workspaceId ?? "";
                _queuedWorkspaceLayoutKind = layoutKind ?? "";
                _hasQueuedWorkspaceSwitch = true;
                Debug.Log("[AppStartupFlow] workspace switch queued: " + NormalizeWorkspaceId(workspaceId));
                return;
            }
            _workspaceSwitchCoroutine = StartCoroutine(SwitchWorkspaceRoutine(workspaceId, layoutKind));
        }

        public void ReportGosloRemovedFromView()
        {
            if (ActiveConfig == null) ActiveConfig = AppStartupConfigDto.Default();
            ActiveConfig.Normalize();

            // Removing the visible model is the same session shape as entering
            // the 2D workspace: keep LiveKit/Brain alive, keep dialogue possible,
            // pause AR/video, and let Brain know GOSLO is no longer in view.
            SwitchWorkspace(ActiveConfig.workspace_id, "2d_workspace");
        }

        public void ReportGosloReturnedToView()
        {
            if (ActiveConfig == null) ActiveConfig = AppStartupConfigDto.Default();
            ActiveConfig.Normalize();

            // Re-placing the already introduced model restores the AR surface
            // policy without repeating the first onGosloPlaced greeting or
            // reconnecting the room.
            SwitchWorkspace(ActiveConfig.workspace_id, "ar_workspace");
        }

        private IEnumerator SwitchWorkspaceRoutine(string workspaceId, string layoutKind)
        {
            if (ActiveConfig == null) ActiveConfig = AppStartupConfigDto.Default();
            ActiveConfig.Normalize();
            EnsureConfirmedSessionState();
            string previousWorkspaceId = _confirmedWorkspaceId;
            string previousCapabilityMode = _confirmedCapabilityMode;
            string targetWorkspaceId = NormalizeWorkspaceId(workspaceId);

            // reason: Workspace switching is an in-session surface change. It
            // may pause AR/video for 2D desks, but it must not call
            // LifecycleShutdownService or RoomManager.Disconnect.
            string policyMode = CapabilityModeForWorkspace(layoutKind);
            bool policyChanged = false;
            if (!string.IsNullOrWhiteSpace(policyMode)
                && !string.Equals(policyMode, previousCapabilityMode, StringComparison.Ordinal))
            {
                policyChanged = true;
                ActiveConfig.capability_mode = ApplyCapabilityModeLocal(policyMode);
                bool policyOk = false;
                yield return CallBrainRpc(
                    "setAppCapabilityMode",
                    $"{{\"mode\":{Quote(ActiveConfig.capability_mode)}}}",
                    "workspace_session_policy",
                    waitForBrain: true,
                    onComplete: ok => policyOk = ok);
                if (!policyOk)
                {
                    ActiveConfig.workspace_id = previousWorkspaceId;
                    ActiveConfig.capability_mode = ApplyCapabilityModeLocal(previousCapabilityMode);
                    lifecycleManager?.ReportDegraded("workspace_session_policy_failed:" + targetWorkspaceId);
                    OnWorkspaceSwitchFailed?.Invoke(targetWorkspaceId);
                    CompleteWorkspaceSwitchRoutine();
                    yield break;
                }
            }

            bool workspaceOk = false;
            yield return CallBrainRpc(
                "applyWorkspace",
                $"{{\"workspace_id\":{Quote(targetWorkspaceId)}}}",
                "workspace_switch",
                waitForBrain: true,
                onComplete: ok => workspaceOk = ok);
            if (!workspaceOk)
            {
                ActiveConfig.workspace_id = previousWorkspaceId;
                if (policyChanged)
                {
                    ActiveConfig.capability_mode = ApplyCapabilityModeLocal(previousCapabilityMode);
                    yield return CallBrainRpc(
                        "setAppCapabilityMode",
                        $"{{\"mode\":{Quote(ActiveConfig.capability_mode)}}}",
                        "workspace_session_policy_rollback",
                        waitForBrain: true);
                }

                lifecycleManager?.ReportDegraded("workspace_switch_failed:" + targetWorkspaceId);
                OnWorkspaceSwitchFailed?.Invoke(targetWorkspaceId);
                CompleteWorkspaceSwitchRoutine();
                yield break;
            }

            ActiveConfig.workspace_id = targetWorkspaceId;
            RecordConfirmedSessionState();
            OnWorkspaceSwitchApplied?.Invoke(ActiveConfig.workspace_id);
            CompleteWorkspaceSwitchRoutine();
        }

        private void CompleteWorkspaceSwitchRoutine()
        {
            _workspaceSwitchCoroutine = null;
            if (!_hasQueuedWorkspaceSwitch)
                return;

            string nextWorkspaceId = _queuedWorkspaceId;
            string nextLayoutKind = _queuedWorkspaceLayoutKind;
            _queuedWorkspaceId = "";
            _queuedWorkspaceLayoutKind = "";
            _hasQueuedWorkspaceSwitch = false;
            SwitchWorkspace(nextWorkspaceId, nextLayoutKind);
        }

        private void EnsureConfirmedSessionState()
        {
            if (ActiveConfig == null)
                ActiveConfig = AppStartupConfigDto.Default();
            ActiveConfig.Normalize();
            if (string.IsNullOrWhiteSpace(_confirmedWorkspaceId))
                _confirmedWorkspaceId = ActiveConfig.workspace_id;
            if (string.IsNullOrWhiteSpace(_confirmedCapabilityMode))
                _confirmedCapabilityMode = ActiveConfig.capability_mode;
        }

        private void RecordConfirmedSessionState()
        {
            if (ActiveConfig == null)
                return;
            ActiveConfig.Normalize();
            _confirmedWorkspaceId = ActiveConfig.workspace_id;
            _confirmedCapabilityMode = ActiveConfig.capability_mode;
        }

        private static string NormalizeWorkspaceId(string workspaceId)
        {
            return string.IsNullOrWhiteSpace(workspaceId) ? "mansion_hub" : workspaceId.Trim();
        }

        private static string CapabilityModeForWorkspace(string layoutKind)
        {
            if (string.Equals(layoutKind, "2d_workspace", StringComparison.OrdinalIgnoreCase))
                return AppCapabilityModeNames.VoiceOnlyNoVideo;
            if (string.Equals(layoutKind, "ar_workspace", StringComparison.OrdinalIgnoreCase)
                || string.Equals(layoutKind, "ar_companion", StringComparison.OrdinalIgnoreCase))
                return AppCapabilityModeNames.FullARCompanion;
            return "";
        }

        private IEnumerator ApplyCompactControlRoutine(
            string controlName,
            string method,
            string payload,
            string value)
        {
            bool ok = false;
            yield return CallBrainRpc(
                method,
                payload,
                controlName,
                waitForBrain: true,
                onComplete: success => ok = success);
            if (ok)
            {
                OnCompactControlApplied?.Invoke(controlName, value);
                yield break;
            }

            lifecycleManager?.ReportDegraded(controlName + "_failed:" + value);
            OnCompactControlFailed?.Invoke(controlName, value);
        }

        public void SetPhotoAwarenessPolicy(string policy)
        {
            string normalized = string.IsNullOrWhiteSpace(policy) ? "AWARE_SILENT" : policy.Trim();
            StartCoroutine(ApplyCompactControlRoutine(
                "photo_awareness",
                "setPhotoAwareness",
                $"{{\"policy\":{Quote(normalized)},\"enabled\":true,\"preview_ttl_seconds\":900}}",
                normalized));
        }

        public void SetCameraMode(string mode)
        {
            string normalized = string.IsNullOrWhiteSpace(mode) ? "preview" : mode.Trim();
            StartCoroutine(ApplyCompactControlRoutine(
                "camera_mode",
                "setCameraMode",
                $"{{\"mode\":{Quote(normalized)}}}",
                normalized));
        }

        public void SetXrHandMode(string mode)
        {
            string normalized = string.IsNullOrWhiteSpace(mode) ? "tracking" : mode.Trim();
            StartCoroutine(ApplyCompactControlRoutine(
                "xrhand_mode",
                "setXrHandMode",
                $"{{\"mode\":{Quote(normalized)}}}",
                normalized));
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
            StartCoroutine(ReportGosloPlacedRoutine());
        }

        private IEnumerator ReportGosloPlacedRoutine()
        {
            bool ok = false;
            yield return CallBrainRpc(
                "onGosloPlaced",
                BuildPlacementPayload(),
                "goslo_placed",
                waitForBrain: true,
                onComplete: success => ok = success);
            if (!ok)
                lifecycleManager?.ReportDegraded("goslo_placed_rpc_failed");
        }

        private IEnumerator RunStartup(AppStartupConfigDto config)
        {
            StartupInProgress = true;
            LastError = "";
            _mainUiReadyOnce = false;
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
                _startupCoroutine = null;
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
                    _startupCoroutine = null;
                    yield break;
                }

                if (RequiresTierOneStartup())
                {
                    yield return RestartConnectedRoomForTierOne(null);
                    StartupInProgress = false;
                    _startupCoroutine = null;
                    yield break;
                }

                bool reusedHttpApplied = false;
                yield return ApplyStartupRoomProfileHttp(ok => reusedHttpApplied = ok);
                if (!reusedHttpApplied)
                {
                    StartupInProgress = false;
                    _startupCoroutine = null;
                    yield break;
                }

                bool reusedRoomSynced = false;
                yield return SyncStartupRoomProfile(
                    "startup_reuse_room_profile",
                    ok => reusedRoomSynced = ok);
                if (!reusedRoomSynced)
                {
                    lifecycleManager?.ReportDegraded("brain_rpc_room_profile_sync_timeout");
                    Fail("brain_rpc_room_profile_sync_timeout");
                    StartupInProgress = false;
                    _startupCoroutine = null;
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
                    _startupCoroutine = null;
                    yield break;
                }

                yield return PrepareArRuntimeForVideoIfNeeded();
                if (!string.IsNullOrEmpty(LastError))
                {
                    StartupInProgress = false;
                    _startupCoroutine = null;
                    yield break;
                }

                BindHeartbeatTransport();
                MarkMainUiReady();
                StartupInProgress = false;
                _startupCoroutine = null;
                yield break;
            }

            bool tierOneReady = false;
            yield return PrepareTierOneRuntimeConfig(ok => tierOneReady = ok);
            if (!tierOneReady)
            {
                StartupInProgress = false;
                _startupCoroutine = null;
                yield break;
            }

            bool roomSettingApplied = false;
            yield return ApplyStartupRoomProfileHttp(ok => roomSettingApplied = ok);
            if (!roomSettingApplied)
            {
                StartupInProgress = false;
                _startupCoroutine = null;
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
                    _startupCoroutine = null;
                    yield break;
                }
                token = mint.Response.token;
                url = mint.Response.url;
            }

            lifecycleManager?.EnterArSessionStarting();
            yield return PrepareArRuntimeForVideoIfNeeded();
            if (!string.IsNullOrEmpty(LastError))
            {
                StartupInProgress = false;
                _startupCoroutine = null;
                yield break;
            }
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
                _startupCoroutine = null;
                yield break;
            }

            BindHeartbeatTransport();

            bool roomSynced = false;
            yield return SyncStartupRoomProfile(
                "startup_room_profile",
                ok => roomSynced = ok);
            if (!roomSynced)
            {
                lifecycleManager?.ReportDegraded("brain_rpc_room_profile_sync_timeout");
                Fail("brain_rpc_room_profile_sync_timeout");
                StartupInProgress = false;
                _startupCoroutine = null;
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
                _startupCoroutine = null;
                yield break;
            }

            MarkMainUiReady();
            StartupInProgress = false;
            _startupCoroutine = null;
        }

        private IEnumerator RunFreshTokenReconnect(string reason)
        {
            StartupInProgress = true;
            LastError = "";
            ResolveServices();

            if (ActiveConfig == null)
                ActiveConfig = AppStartupConfigDto.Default();
            ActiveConfig.Normalize();
            ApplyCapabilityModeLocal(ActiveConfig.capability_mode);

            if (roomManager == null || tokenMintClient == null)
            {
                Fail("fresh_reconnect_missing_runtime_services");
                CompleteFreshReconnect();
                yield break;
            }

            if (roomManager.IsDisconnecting)
            {
                Fail("fresh_reconnect_rejected_chokepoint_running");
                CompleteFreshReconnect();
                yield break;
            }

            lifecycleManager?.ReportReconnecting(reason);

            LiveKitTokenMintClient.MintResult mint = default;
            yield return tokenMintClient.Mint(
                ActiveConfig.room_id,
                ResolveUnityIdentity(ActiveConfig),
                result => mint = result);
            if (!mint.Ok)
            {
                lifecycleManager?.ReportDegraded("fresh_reconnect_token_mint_failed");
                Fail($"fresh_reconnect_token_mint_failed:{mint.Error}");
                CompleteFreshReconnect();
                yield break;
            }

            string url = string.IsNullOrWhiteSpace(mint.Response.url)
                ? ActiveConfig.livekit_url
                : mint.Response.url;
            yield return PrepareArRuntimeForVideoIfNeeded();
            if (!string.IsNullOrEmpty(LastError))
            {
                CompleteFreshReconnect();
                yield break;
            }
            roomManager.Connect(mint.Response.token, string.IsNullOrWhiteSpace(url) ? null : url);

            float deadline = Time.realtimeSinceStartup + connectTimeoutSeconds;
            while (roomManager != null && !roomManager.IsConnected
                   && Time.realtimeSinceStartup < deadline)
            {
                yield return null;
            }

            if (roomManager == null || !roomManager.IsConnected)
            {
                lifecycleManager?.ReportDegraded("fresh_reconnect_livekit_timeout");
                Fail("fresh_reconnect_livekit_timeout");
                CompleteFreshReconnect();
                yield break;
            }

            BindHeartbeatTransport();

            bool roomSynced = false;
            yield return SyncStartupRoomProfile(
                "fresh_reconnect_room_profile",
                ok => roomSynced = ok);
            if (!roomSynced)
            {
                lifecycleManager?.ReportDegraded("fresh_reconnect_room_profile_sync_timeout");
                Fail("fresh_reconnect_room_profile_sync_timeout");
                CompleteFreshReconnect();
                yield break;
            }

            bool policySynced = false;
            yield return CallBrainRpc(
                "setAppCapabilityMode",
                $"{{\"mode\":{Quote(ActiveConfig.capability_mode)}}}",
                "fresh_reconnect_capability_mode",
                waitForBrain: true,
                onComplete: ok => policySynced = ok);
            if (!policySynced)
            {
                lifecycleManager?.ReportDegraded("fresh_reconnect_policy_sync_timeout");
                Fail("fresh_reconnect_policy_sync_timeout");
                CompleteFreshReconnect();
                yield break;
            }

            MarkMainUiReady();
            CompleteFreshReconnect();
        }

        private IEnumerator RestartConnectedRoomForTierOne(Action<bool> onComplete)
        {
            bool tierOneReady = false;
            yield return PrepareTierOneRuntimeConfig(ok => tierOneReady = ok);
            if (!tierOneReady)
            {
                onComplete?.Invoke(false);
                yield break;
            }

            bool roomSettingApplied = false;
            yield return ApplyStartupRoomProfileHttp(ok => roomSettingApplied = ok);
            if (!roomSettingApplied)
            {
                onComplete?.Invoke(false);
                yield break;
            }

            if (shutdownService == null || roomManager == null || tokenMintClient == null)
            {
                Fail("tier1_fresh_reconnect_missing_runtime_services");
                onComplete?.Invoke(false);
                yield break;
            }

            lifecycleManager?.ReportReconnecting("tier1_setting_requires_fresh_livekit_reconnect");
            shutdownService.RequestShutdown("tier1_setting_requires_fresh_livekit_reconnect");

            float shutdownDeadline = Time.realtimeSinceStartup + Mathf.Max(1f, tierOneReconnectShutdownTimeoutSeconds);
            // tier1_fresh_reconnect_waits_for_shutdown_cooldown:
            // RoomManager clears Room before LifecycleShutdownService finishes
            // its cool-down and ReportDisconnected() step. Starting a new room
            // before that final step can let the old shutdown mark the fresh
            // session disconnected. Wait for both the room handle and FSM
            // chokepoint state to settle.
            while (Time.realtimeSinceStartup < shutdownDeadline
                   && roomManager != null
                   && (roomManager.IsConnected
                       || roomManager.IsDisconnecting
                       || roomManager.Room != null
                       || lifecycleManager?.CurrentState == AppLifecycleState.ShuttingDown))
            {
                yield return null;
            }

            if (roomManager == null
                || roomManager.IsConnected
                || roomManager.IsDisconnecting
                || roomManager.Room != null
                || lifecycleManager?.CurrentState == AppLifecycleState.ShuttingDown)
            {
                Fail("tier1_fresh_reconnect_shutdown_timeout");
                onComplete?.Invoke(false);
                yield break;
            }

            // tier1_fresh_reconnect_reenter_token_gate:
            // LifecycleShutdownService correctly leaves the FSM in Disconnected.
            // A user-visible START is allowed to begin a new session from there,
            // but RoomManagerLifecycleBridge will treat OnConnecting as a
            // reconnect and ReportReconnecting intentionally ignores
            // Disconnected. Re-enter the normal startup gates before mint/connect
            // so ReportRoomConnected -> ReportRunning can advance again.
            lifecycleManager?.EnterTokenGate();

            LiveKitTokenMintClient.MintResult mint = default;
            yield return tokenMintClient.Mint(
                ActiveConfig.room_id,
                ResolveUnityIdentity(ActiveConfig),
                result => mint = result);
            if (!mint.Ok)
            {
                lifecycleManager?.ReportDegraded("tier1_fresh_reconnect_token_mint_failed");
                Fail($"tier1_fresh_reconnect_token_mint_failed:{mint.Error}");
                onComplete?.Invoke(false);
                yield break;
            }

            string url = string.IsNullOrWhiteSpace(mint.Response.url)
                ? ActiveConfig.livekit_url
                : mint.Response.url;
            lifecycleManager?.EnterArSessionStarting();
            yield return PrepareArRuntimeForVideoIfNeeded();
            if (!string.IsNullOrEmpty(LastError))
            {
                onComplete?.Invoke(false);
                yield break;
            }
            roomManager.Connect(mint.Response.token, string.IsNullOrWhiteSpace(url) ? null : url);

            float connectDeadline = Time.realtimeSinceStartup + connectTimeoutSeconds;
            while (roomManager != null && !roomManager.IsConnected
                   && Time.realtimeSinceStartup < connectDeadline)
            {
                yield return null;
            }

            if (roomManager == null || !roomManager.IsConnected)
            {
                lifecycleManager?.ReportDegraded("tier1_fresh_reconnect_livekit_timeout");
                Fail("tier1_fresh_reconnect_livekit_timeout");
                onComplete?.Invoke(false);
                yield break;
            }

            BindHeartbeatTransport();

            bool roomSynced = false;
            yield return SyncStartupRoomProfile(
                "tier1_fresh_reconnect_room_profile",
                ok => roomSynced = ok);
            if (!roomSynced)
            {
                lifecycleManager?.ReportDegraded("tier1_fresh_reconnect_room_profile_sync_timeout");
                Fail("tier1_fresh_reconnect_room_profile_sync_timeout");
                onComplete?.Invoke(false);
                yield break;
            }

            bool policySynced = false;
            yield return CallBrainRpc(
                "setAppCapabilityMode",
                $"{{\"mode\":{Quote(ActiveConfig.capability_mode)}}}",
                "tier1_fresh_reconnect_capability_mode",
                waitForBrain: true,
                onComplete: ok => policySynced = ok);
            if (!policySynced)
            {
                lifecycleManager?.ReportDegraded("tier1_fresh_reconnect_policy_sync_timeout");
                Fail("tier1_fresh_reconnect_policy_sync_timeout");
                onComplete?.Invoke(false);
                yield break;
            }

            MarkMainUiReady();
            onComplete?.Invoke(true);
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

        private IEnumerator PrepareArRuntimeForVideoIfNeeded()
        {
            ResolveServices();
            if (ActiveConfig == null)
                ActiveConfig = AppStartupConfigDto.Default();
            ActiveConfig.Normalize();

            if (!AppCapabilityModeNames.VideoEnabled(ActiveConfig.capability_mode))
                yield break;
            if (Application.isEditor || !Application.isMobilePlatform)
                yield break;
            if (arRuntimeBootstrap == null)
                yield break;

            yield return arRuntimeBootstrap.EnsureArRuntimeReady();
            if (arRuntimeBootstrap.XrLifecycleFailed)
            {
                string detail = string.IsNullOrWhiteSpace(arRuntimeBootstrap.LastStatus)
                    ? "unknown"
                    : arRuntimeBootstrap.LastStatus;
                lifecycleManager?.ReportDegraded("ar_runtime_prepare_failed:" + detail);
                Fail("ar_runtime_prepare_failed:" + detail);
            }
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
                    LastBrainRpcStatus = method + ":skipped:" + missing;
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
                LastBrainRpcStatus = method + ":error:" + ShortRuntimeLabel(rpcCall.Error?.Message, 36);
                onComplete?.Invoke(false);
                yield break;
            }

            if (!IsRpcBusinessOk(method, rpcCall.Payload, reason))
            {
                LastBrainRpcStatus = method + ":business_failed";
                onComplete?.Invoke(false);
                yield break;
            }

            LastBrainRpcStatus = method + ":ok";
            onComplete?.Invoke(true);
        }

        private IEnumerator SyncStartupRoomProfile(string reason, Action<bool> onComplete)
        {
            if (ActiveConfig == null) ActiveConfig = AppStartupConfigDto.Default();

            // RoomProfile is the owner of Model / Persona / Line / Scene /
            // Skin defaults. Sync it before capability mode so Brain loads the
            // right persona/context pack before the first AR placement event.
            yield return CallBrainRpc(
                "applyRoomProfile",
                BuildRoomProfilePayload(),
                reason,
                waitForBrain: true,
                onComplete: onComplete);
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
                   + "\"room_profile_id\":" + Quote(ActiveConfig.room_profile_id) + ","
                   + "\"model_id\":" + Quote(ActiveConfig.model_id) + ","
                   + "\"persona_id\":" + Quote(ActiveConfig.persona_id) + ","
                   + "\"line_id\":" + Quote(ActiveConfig.line_id) + ","
                   + "\"line_profile_id\":" + Quote(ActiveConfig.line_profile_id) + ","
                   + "\"experience_mode\":" + Quote(ActiveConfig.experience_mode) + ","
                   + "\"skin_id\":" + Quote(ActiveConfig.skin_id) + ","
                   + "\"capability_mode\":" + Quote(ActiveConfig.capability_mode)
                   + "}";
        }

        private string BuildRoomProfilePayload()
        {
            if (ActiveConfig == null) ActiveConfig = AppStartupConfigDto.Default();
            ActiveConfig.Normalize();
            string displayName = string.IsNullOrWhiteSpace(ActiveConfig.room_profile_id)
                ? "Startup Room"
                : ActiveConfig.room_profile_id;
            return "{"
                   + "\"room_profile_id\":" + Quote(ActiveConfig.room_profile_id) + ","
                   + "\"room_profile\":{"
                   + "\"schema_version\":3,"
                   + "\"kind\":\"room_profile\","
                   + "\"room_profile_id\":" + Quote(ActiveConfig.room_profile_id) + ","
                   + "\"display_name\":" + Quote(displayName) + ","
                   + "\"model_id\":" + Quote(ActiveConfig.model_id) + ","
                   + "\"persona_id\":" + Quote(ActiveConfig.persona_id) + ","
                   + "\"line_id\":" + Quote(ActiveConfig.line_id) + ","
                   + "\"line_profile_id\":" + Quote(ActiveConfig.line_profile_id) + ","
                   + "\"scene_profile_id\":" + Quote(ActiveConfig.scene_id) + ","
                   + "\"experience_mode\":" + Quote(ActiveConfig.experience_mode) + ","
                   + "\"workspace_id\":" + Quote(ActiveConfig.workspace_id) + ","
                   + "\"map_id\":" + Quote(ActiveConfig.workspace_id) + ","
                   + "\"skin_id\":" + Quote(ActiveConfig.skin_id) + ","
                   + "\"setting_file_refs\":" + QuoteArray(ActiveConfig.setting_file_refs) + ","
                   + "\"livekit_room_id\":" + Quote(ActiveConfig.room_id)
                   + "},"
                   + "\"experience_mode\":" + Quote(ActiveConfig.experience_mode)
                   + "}";
        }

        private IEnumerator PrepareTierOneRuntimeConfig(Action<bool> onComplete)
        {
            if (!RequiresTierOneStartup())
            {
                onComplete?.Invoke(true);
                yield break;
            }

            ResolveServices();
            if (orchestratorClient == null || !orchestratorClient.HasEndpoint)
            {
                Fail("orchestrator_required_for_tier1_startup");
                onComplete?.Invoke(false);
                yield break;
            }

            OrchestratorResult result = default;
            yield return orchestratorClient.ApplyRoomProfile(
                ActiveConfig,
                forceReconnect: false,
                onComplete: r => result = r);

            if (!result.Success)
            {
                Fail("orchestrator_apply_room_profile_failed:" + result.Error);
                onComplete?.Invoke(false);
                yield break;
            }

            onComplete?.Invoke(true);
        }

        private bool RequiresTierOneStartup()
        {
            if (ActiveConfig == null) return false;
            if (ActiveConfig.requires_livekit_reconnect) return true;
            if (ActiveConfig.setting_change_tier >= 1) return true;
            if (string.Equals(ActiveConfig.line_id, "line_b", StringComparison.OrdinalIgnoreCase)) return true;
            if (!string.IsNullOrWhiteSpace(ActiveConfig.line_profile_id)
                && ActiveConfig.line_profile_id.StartsWith("lineb", StringComparison.OrdinalIgnoreCase))
                return true;
            return false;
        }

        private IEnumerator ApplyStartupRoomProfileHttp(Action<bool> onComplete)
        {
            ResolveServices();
            if (ActiveConfig == null) ActiveConfig = AppStartupConfigDto.Default();
            ActiveConfig.Normalize();

            if (roomSettingClient == null || !roomSettingClient.HasEndpoint)
            {
                Fail("room_setting_http_apply_required");
                onComplete?.Invoke(false);
                yield break;
            }

            var profile = RoomSettingDtoMapper.FromStartupConfig(
                ActiveConfig,
                ActiveConfig.room_profile_id);
            RequestResult<ApplyRoomProfileResponseDto> result = default;
            yield return roomSettingClient.ApplyRoomProfile(profile, r => result = r);

            if (!result.Success || result.Value == null || !result.Value.success)
            {
                string detail = result.Error;
                if (result.Value != null && result.Value.errors != null && result.Value.errors.Length > 0)
                    detail = string.Join("|", result.Value.errors);
                if (string.IsNullOrWhiteSpace(detail)) detail = "unknown";
                Fail("room_setting_http_apply_failed:" + detail);
                onComplete?.Invoke(false);
                yield break;
            }

            if (result.Value.room_profile != null)
                ActiveConfig = RoomSettingDtoMapper.ToStartupConfig(result.Value.room_profile, ActiveConfig);
            if (result.Value.compatibility != null)
            {
                ActiveConfig.setting_change_tier = result.Value.compatibility.tier;
                ActiveConfig.compatibility_state = result.Value.compatibility.state ?? "";
                ActiveConfig.compatibility_summary = result.Value.compatibility.tier_summary ?? "";
                ActiveConfig.requires_livekit_reconnect = result.Value.compatibility.tier >= 1;
            }
            ActiveConfig.Normalize();
            onComplete?.Invoke(true);
        }

        private void BindHeartbeatTransport()
        {
            ResolveServices();
            if (heartbeatPublisher == null || roomManager == null || !roomManager.IsConnected)
                return;

            heartbeatPublisher.Transport = new LiveKitDataChannelHeartbeatTransport(
                roomManager,
                lifecycleManager != null ? lifecycleManager.HealthAggregator : null);
            heartbeatPublisher.UnityIdentity = roomManager.JoinIdentity;
            heartbeatPublisher.RoomId = string.IsNullOrWhiteSpace(roomManager.RoomName)
                ? (ActiveConfig != null ? ActiveConfig.room_id : "")
                : roomManager.RoomName;
        }

        private bool IsRpcBusinessOk(string method, string payload, string reason)
        {
            if (string.IsNullOrWhiteSpace(payload)) return true;

            try
            {
                var status = JsonUtility.FromJson<RpcStatusEnvelope>(payload);
                if (status != null && string.Equals(status.status, "error", StringComparison.OrdinalIgnoreCase))
                {
                    Debug.LogWarning($"[AppStartupFlow] RPC {method} business error ({reason}): {payload}");
                    return false;
                }
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[AppStartupFlow] RPC {method} status parse warning ({reason}): {ex.Message}");
            }

            if (!string.Equals(method, "applyRoomProfile", StringComparison.Ordinal))
                return true;

            try
            {
                var response = JsonUtility.FromJson<ApplyRoomProfileRpcResponse>(payload);
                if (response != null && response.result != null && !response.result.success)
                {
                    Debug.LogWarning($"[AppStartupFlow] applyRoomProfile rejected ({reason}): {payload}");
                    return false;
                }
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[AppStartupFlow] applyRoomProfile parse warning ({reason}): {ex.Message}");
            }

            return true;
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
            if (orchestratorClient == null) orchestratorClient = FindObjectOfType<OrchestratorClient>();
            if (orchestratorClient == null) orchestratorClient = gameObject.AddComponent<OrchestratorClient>();
            if (roomSettingClient == null) roomSettingClient = FindObjectOfType<AppRoomSettingClient>();
            if (homeMenuClient == null) homeMenuClient = FindObjectOfType<AppHomeMenuClient>();
            if (homeMenuClient == null) homeMenuClient = gameObject.AddComponent<AppHomeMenuClient>();
            if (heartbeatPublisher == null) heartbeatPublisher = FindObjectOfType<LifecycleHeartbeatPublisher>();
            if (heartbeatPublisher == null && lifecycleManager != null)
                heartbeatPublisher = lifecycleManager.gameObject.AddComponent<LifecycleHeartbeatPublisher>();
            if (ecpEventPublisher == null) ecpEventPublisher = EcpEventPublisher.Instance ?? FindObjectOfType<EcpEventPublisher>();
            if (ecpEventPublisher == null)
            {
                var host = roomManager != null
                    ? roomManager.gameObject
                    : (lifecycleManager != null ? lifecycleManager.gameObject : gameObject);
                ecpEventPublisher = host.AddComponent<EcpEventPublisher>();
            }
            if (mainReadyGate == null) mainReadyGate = FindObjectOfType<FormalMainReadyGate>();
            if (mainReadyGate == null)
            {
                var host = lifecycleManager != null
                    ? lifecycleManager.gameObject
                    : (roomManager != null ? roomManager.gameObject : gameObject);
                mainReadyGate = host.AddComponent<FormalMainReadyGate>();
            }
            if (homeHudController == null) homeHudController = FindObjectOfType<FormalHomeHudController>();
            if (homeHudController == null)
            {
                var host = lifecycleManager != null
                    ? lifecycleManager.gameObject
                    : (roomManager != null ? roomManager.gameObject : gameObject);
                homeHudController = host.AddComponent<FormalHomeHudController>();
            }
            if (homeMenuLoader == null) homeMenuLoader = FindObjectOfType<FormalHomeMenuLoader>();
            if (homeMenuLoader == null)
            {
                var host = lifecycleManager != null
                    ? lifecycleManager.gameObject
                    : (roomManager != null ? roomManager.gameObject : gameObject);
                homeMenuLoader = host.AddComponent<FormalHomeMenuLoader>();
            }
            if (homeMenuController == null) homeMenuController = FindObjectOfType<FormalHomeMenuController>();
            if (homeMenuController == null)
            {
                var host = lifecycleManager != null
                    ? lifecycleManager.gameObject
                    : (roomManager != null ? roomManager.gameObject : gameObject);
                homeMenuController = host.AddComponent<FormalHomeMenuController>();
            }
            if (homeToolController == null) homeToolController = FindObjectOfType<FormalHomeToolController>();
            if (homeToolController == null)
            {
                var host = lifecycleManager != null
                    ? lifecycleManager.gameObject
                    : (roomManager != null ? roomManager.gameObject : gameObject);
                homeToolController = host.AddComponent<FormalHomeToolController>();
            }
            if (modelReadyReporter == null) modelReadyReporter = FindObjectOfType<FormalModelReadyReporter>();
            if (modelReadyReporter == null)
            {
                var host = lifecycleManager != null
                    ? lifecycleManager.gameObject
                    : (roomManager != null ? roomManager.gameObject : gameObject);
                modelReadyReporter = host.AddComponent<FormalModelReadyReporter>();
            }
            if (modelPlacementController == null) modelPlacementController = FindObjectOfType<FormalModelPlacementController>();
            if (modelPlacementController == null)
            {
                var host = lifecycleManager != null
                    ? lifecycleManager.gameObject
                    : (roomManager != null ? roomManager.gameObject : gameObject);
                modelPlacementController = host.AddComponent<FormalModelPlacementController>();
            }
            if (modelRemoteController == null) modelRemoteController = FindObjectOfType<FormalModelRemoteController>();
            if (modelRemoteController == null)
            {
                var host = lifecycleManager != null
                    ? lifecycleManager.gameObject
                    : (roomManager != null ? roomManager.gameObject : gameObject);
                modelRemoteController = host.AddComponent<FormalModelRemoteController>();
            }
            if (xrHandPerchController == null) xrHandPerchController = FindObjectOfType<FormalXrHandPerchController>();
            if (xrHandPerchController == null)
            {
                var host = lifecycleManager != null
                    ? lifecycleManager.gameObject
                    : (roomManager != null ? roomManager.gameObject : gameObject);
                xrHandPerchController = host.AddComponent<FormalXrHandPerchController>();
            }
            if (arRuntimeBootstrap == null) arRuntimeBootstrap = FindObjectOfType<FormalArRuntimeBootstrap>();
            if (arRuntimeBootstrap == null)
            {
                var host = lifecycleManager != null
                    ? lifecycleManager.gameObject
                    : (roomManager != null ? roomManager.gameObject : gameObject);
                arRuntimeBootstrap = host.AddComponent<FormalArRuntimeBootstrap>();
            }
            if (arSessionBaselineReporter == null)
                arSessionBaselineReporter = FindObjectOfType<FormalArSessionBaselineReporter>();
            if (arSessionBaselineReporter == null)
            {
                var host = lifecycleManager != null
                    ? lifecycleManager.gameObject
                    : (roomManager != null ? roomManager.gameObject : gameObject);
                arSessionBaselineReporter = host.AddComponent<FormalArSessionBaselineReporter>();
            }
            if (FindObjectOfType<AudioRouteManager>() == null)
            {
                var host = microphonePublisher != null
                    ? microphonePublisher.gameObject
                    : (roomManager != null ? roomManager.gameObject : gameObject);
                host.AddComponent<AudioRouteManager>();
            }
            if (FindObjectOfType<AudioRoutePolicyBrainReporter>() == null)
            {
                var host = microphonePublisher != null
                    ? microphonePublisher.gameObject
                    : (roomManager != null ? roomManager.gameObject : gameObject);
                host.AddComponent<AudioRoutePolicyBrainReporter>();
            }
            if (FindObjectOfType<LiveKitReconnectSupervisor>() == null)
            {
                var host = lifecycleManager != null
                    ? lifecycleManager.gameObject
                    : (roomManager != null ? roomManager.gameObject : gameObject);
                host.AddComponent<LiveKitReconnectSupervisor>();
            }
        }

        private void MarkMainUiReady()
        {
            RecordConfirmedSessionState();
            _mainUiReadyOnce = true;
            OnMainUiReady?.Invoke(ActiveConfig);
        }

        private void CompleteFreshReconnect()
        {
            StartupInProgress = false;
            _freshReconnectCoroutine = null;
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

        private static string ShortRuntimeLabel(string value, int max)
        {
            string text = string.IsNullOrWhiteSpace(value) ? "unknown" : value.Trim();
            if (text.Length <= max) return text;
            return text.Substring(0, Math.Max(1, max - 3)) + "...";
        }

        private static string QuoteArray(string[] values)
        {
            if (values == null || values.Length == 0) return "[]";
            var parts = new string[values.Length];
            for (int i = 0; i < values.Length; i++)
                parts[i] = Quote(values[i]);
            return "[" + string.Join(",", parts) + "]";
        }

        [Serializable]
        private class RpcStatusEnvelope
        {
            public string status = "";
        }

        [Serializable]
        private class ApplyRoomProfileRpcResponse
        {
            public string status = "";
            public ApplyRoomProfileResult result;
        }

        [Serializable]
        private class ApplyRoomProfileResult
        {
            public bool success;
            public string[] errors;
        }
    }
}
