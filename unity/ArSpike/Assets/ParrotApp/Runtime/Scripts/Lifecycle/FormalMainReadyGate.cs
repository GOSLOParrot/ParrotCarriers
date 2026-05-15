using System;
using System.Collections.Generic;
using ParrotApp.Config;
using ParrotApp.Health;
using ParrotApp.LiveKit;
using UnityEngine;

namespace ParrotApp.Lifecycle
{
    [Serializable]
    public class FormalMainReadySnapshot
    {
        public bool ready;
        public string missing_gates = "";
        public string lifecycle_state = "";
        public string connection_overall = "";
        public string room_id = "";
        public string room_profile_id = "";
        public string capability_mode = "";
    }

    /// <summary>
    /// Owns the final START-to-home boundary.
    ///
    /// AppStartupFlowController proves transport and Brain business sync. This
    /// gate waits for the formal home prerequisites before it calls
    /// AppLifecycleManager.ReportRunning(), so a loading hold screen cannot be
    /// mistaken for the real AR homepage.
    /// </summary>
    [DisallowMultipleComponent]
    public class FormalMainReadyGate : MonoBehaviour
    {
        [SerializeField] private AppStartupFlowController startupFlow;
        [SerializeField] private AppLifecycleManager lifecycleManager;
        [SerializeField] private RoomManager roomManager;

        [Header("Transport gates")]
        [SerializeField] private bool requireLiveKitConnected = true;
        [SerializeField] private bool requireBrainPresent = true;
        [SerializeField] private bool requireStartupBrainRpcSynced = true;
        [SerializeField] private bool requireHeartbeatDataChannelReady = true;
        [SerializeField] private bool requireUnityCommandRpcReady = false;
        [Tooltip("Media publish readiness is reported through HUD/health, but should not block entering the AR home surface.")]
        [SerializeField] private bool requireAudioWhenModeNeedsMic = false;
        [Tooltip("AR camera/session readiness gates the home surface; LiveKit publish freshness remains a degradable media status.")]
        [SerializeField] private bool requireVideoWhenModeNeedsVideo = false;

        [Header("Home gates")]
        [SerializeField] private bool requireHudLoaded = true;
        [SerializeField] private bool requireMenuSnapshotLoaded = true;
        [SerializeField] private bool requireModelResolved = true;
        [SerializeField] private bool requireArSessionBaselineClean = true;

        [Header("Observation")]
        [SerializeField] private float degradedAfterSeconds = 12f;
        [SerializeField] private float waitingReevaluateIntervalSeconds = 0.5f;

        private AppStartupFlowController _subscribedStartupFlow;
        private AppLifecycleManager _subscribedLifecycle;
        private AppStartupConfigDto _activeConfig = AppStartupConfigDto.Default();
        private bool _startupTransportReady;
        private bool _startupBrainRpcSynced;
        private bool _hudLoaded;
        private bool _menuSnapshotLoaded;
        private bool _modelResolved;
        private bool _arSessionBaselineClean;
        private bool _runningReported;
        private bool _degradedReported;
        private float _transportReadyAt = -1f;
        private float _nextWaitingEvaluationAt = -1f;
        private FormalMainReadySnapshot _lastSnapshot = new FormalMainReadySnapshot();

        public bool IsReady { get; private set; }
        public string LastMissingGates { get; private set; } = "startup_transport_ready";
        public FormalMainReadySnapshot LastSnapshot => _lastSnapshot;

        public event Action<FormalMainReadySnapshot> OnGateChanged;

        private void OnEnable()
        {
            Bind();
            Evaluate("enable");
        }

        private void Start()
        {
            Bind();
            Evaluate("start");
        }

        private void Update()
        {
            if (!_startupTransportReady || IsReady || _degradedReported || degradedAfterSeconds <= 0f)
                return;

            float now = Time.realtimeSinceStartup;
            if (_nextWaitingEvaluationAt > 0f && now < _nextWaitingEvaluationAt)
                return;

            _nextWaitingEvaluationAt = now + Mathf.Max(0.1f, waitingReevaluateIntervalSeconds);
            Evaluate("waiting_tick");
        }

        private void OnDisable()
        {
            UnbindStartupFlow();
            UnbindLifecycle();
        }

        public void ReportHudLoaded(string detail = "")
        {
            _hudLoaded = true;
            Evaluate("hud_loaded:" + (detail ?? ""));
        }

        public void ReportMenuSnapshotLoaded(string detail = "")
        {
            _menuSnapshotLoaded = true;
            Evaluate("menu_snapshot_loaded:" + (detail ?? ""));
        }

        public void ReportModelResolved(string detail = "")
        {
            _modelResolved = true;
            Evaluate("model_resolved:" + (detail ?? ""));
        }

        public void ReportArSessionBaselineClean(string detail = "")
        {
            _arSessionBaselineClean = true;
            Evaluate("ar_session_baseline_clean:" + (detail ?? ""));
        }

        public void ReportGateInvalidated(string gateName)
        {
            switch (gateName ?? "")
            {
                case "hud_loaded":
                    _hudLoaded = false;
                    break;
                case "menu_snapshot_loaded":
                    _menuSnapshotLoaded = false;
                    break;
                case "model_resolved":
                    _modelResolved = false;
                    break;
                case "ar_session_baseline_clean":
                    _arSessionBaselineClean = false;
                    break;
            }
            Evaluate("gate_invalidated:" + (gateName ?? ""));
        }

        private void Bind()
        {
            if (startupFlow == null) startupFlow = FindObjectOfType<AppStartupFlowController>();
            if (lifecycleManager == null) lifecycleManager = FindObjectOfType<AppLifecycleManager>();
            if (roomManager == null) roomManager = RoomManager.Instance ?? FindObjectOfType<RoomManager>();

            if (_subscribedStartupFlow != startupFlow)
            {
                UnbindStartupFlow();
                _subscribedStartupFlow = startupFlow;
                if (_subscribedStartupFlow != null)
                {
                    _subscribedStartupFlow.OnTransitionStarted += HandleTransitionStarted;
                    _subscribedStartupFlow.OnMainUiReady += HandleStartupMainReady;
                    _subscribedStartupFlow.OnStartupFailed += HandleStartupFailed;
                }
            }

            if (_subscribedLifecycle != lifecycleManager)
            {
                UnbindLifecycle();
                _subscribedLifecycle = lifecycleManager;
                if (_subscribedLifecycle?.HealthAggregator != null)
                    _subscribedLifecycle.HealthAggregator.OnChanged += HandleHealthChanged;
            }
        }

        private void UnbindStartupFlow()
        {
            if (_subscribedStartupFlow == null) return;
            _subscribedStartupFlow.OnTransitionStarted -= HandleTransitionStarted;
            _subscribedStartupFlow.OnMainUiReady -= HandleStartupMainReady;
            _subscribedStartupFlow.OnStartupFailed -= HandleStartupFailed;
            _subscribedStartupFlow = null;
        }

        private void UnbindLifecycle()
        {
            if (_subscribedLifecycle?.HealthAggregator != null)
                _subscribedLifecycle.HealthAggregator.OnChanged -= HandleHealthChanged;
            _subscribedLifecycle = null;
        }

        private void HandleTransitionStarted(AppStartupConfigDto config)
        {
            ResetForStartup(config);
            Evaluate("transition_started");
        }

        private void HandleStartupMainReady(AppStartupConfigDto config)
        {
            _activeConfig = config ?? AppStartupConfigDto.Default();
            _activeConfig.Normalize();
            _startupTransportReady = true;
            _startupBrainRpcSynced = true;
            _transportReadyAt = Time.realtimeSinceStartup;
            _nextWaitingEvaluationAt = _transportReadyAt + Mathf.Max(0.1f, waitingReevaluateIntervalSeconds);
            Evaluate("startup_main_ready");
        }

        private void HandleStartupFailed(string reason)
        {
            _startupTransportReady = false;
            _startupBrainRpcSynced = false;
            _transportReadyAt = -1f;
            _nextWaitingEvaluationAt = -1f;
            Evaluate("startup_failed:" + (reason ?? ""));
        }

        private void HandleHealthChanged(ConnectionHealthState _)
        {
            Evaluate("health_changed");
        }

        private void ResetForStartup(AppStartupConfigDto config)
        {
            _activeConfig = config ?? AppStartupConfigDto.Default();
            _activeConfig.Normalize();
            _startupTransportReady = false;
            _startupBrainRpcSynced = false;
            _hudLoaded = false;
            _menuSnapshotLoaded = false;
            _modelResolved = false;
            _arSessionBaselineClean = false;
            _runningReported = false;
            _degradedReported = false;
            _transportReadyAt = -1f;
            _nextWaitingEvaluationAt = -1f;
            IsReady = false;
            LastMissingGates = "startup_transport_ready";
        }

        private void Evaluate(string reason)
        {
            Bind();

            var missing = new List<string>();
            var health = lifecycleManager?.HealthAggregator != null
                ? lifecycleManager.HealthAggregator.Snapshot
                : ConnectionHealthState.Initial();

            if (!_startupTransportReady)
                missing.Add("startup_transport_ready");
            if (requireLiveKitConnected && !(health.RoomConnected || roomManager?.IsConnected == true))
                missing.Add("livekit_room_connected");
            if (requireBrainPresent && !health.BrainPresent)
                missing.Add("brain_present");
            if (requireStartupBrainRpcSynced && !_startupBrainRpcSynced)
                missing.Add("startup_brain_rpc_synced");
            if (requireHeartbeatDataChannelReady && !health.DataChannelReady)
                missing.Add("heartbeat_datachannel_ready");
            if (requireUnityCommandRpcReady && !health.RpcReady)
                missing.Add("unity_command_rpc_ready");
            if (requireAudioWhenModeNeedsMic
                && AppCapabilityModeNames.MicrophoneEnabled(_activeConfig.capability_mode)
                && !health.AudioPublished)
                missing.Add("microphone_published");
            if (requireVideoWhenModeNeedsVideo
                && AppCapabilityModeNames.VideoEnabled(_activeConfig.capability_mode)
                && !health.VideoPublished)
                missing.Add("video_published");
            if (requireVideoWhenModeNeedsVideo
                && AppCapabilityModeNames.VideoEnabled(_activeConfig.capability_mode)
                && !string.Equals(health.VideoTier, "VIDEO_OFF", StringComparison.Ordinal)
                && !health.VideoFreshFrame)
                missing.Add("video_fresh_frame");
            if (requireHudLoaded && !_hudLoaded)
                missing.Add("hud_loaded");
            if (requireMenuSnapshotLoaded && !_menuSnapshotLoaded)
                missing.Add("menu_snapshot_loaded");
            if (requireModelResolved && !_modelResolved)
                missing.Add("model_resolved");
            if (requireArSessionBaselineClean && !_arSessionBaselineClean)
                missing.Add("ar_session_baseline_clean");

            bool ready = missing.Count == 0;
            string missingText = ready ? "" : string.Join(",", missing);
            bool changed = ready != IsReady || !string.Equals(missingText, LastMissingGates, StringComparison.Ordinal);

            IsReady = ready;
            LastMissingGates = missingText;
            _lastSnapshot = BuildSnapshot(health, ready, missingText);

            if (ready && !_runningReported)
            {
                _runningReported = true;
                lifecycleManager?.ReportRunning();
            }
            else if (!ready && _runningReported)
            {
                if (!_degradedReported)
                {
                    _degradedReported = true;
                    lifecycleManager?.ReportDegraded("main_ready_gate_lost:" + missingText);
                }
            }
            else if (!ready
                     && !_degradedReported
                     && _startupTransportReady
                     && degradedAfterSeconds > 0f
                     && _transportReadyAt > 0f
                     && Time.realtimeSinceStartup - _transportReadyAt >= degradedAfterSeconds)
            {
                _degradedReported = true;
                lifecycleManager?.ReportDegraded("main_ready_waiting:" + missing[0]);
            }

            if (changed)
                OnGateChanged?.Invoke(_lastSnapshot);
        }

        private FormalMainReadySnapshot BuildSnapshot(
            ConnectionHealthState health,
            bool ready,
            string missingText)
        {
            return new FormalMainReadySnapshot
            {
                ready = ready,
                missing_gates = missingText,
                lifecycle_state = lifecycleManager != null ? lifecycleManager.CurrentState.ToString() : "",
                connection_overall = ConnectionOverallNames.ToWireString(health.Overall),
                room_id = _activeConfig.room_id ?? "",
                room_profile_id = _activeConfig.room_profile_id ?? "",
                capability_mode = _activeConfig.capability_mode ?? "",
            };
        }
    }
}
