using System;
using System.Collections;
using ParrotApp.Lifecycle;
using UnityEngine;

namespace ParrotApp.LiveKit
{
    /// <summary>
    /// Production reconnect owner for passive LiveKit disconnects.
    /// It never reuses the cached JWT: every attempt asks token-mint for a
    /// fresh room token, then lets AppStartupFlowController re-sync Brain RPCs.
    /// </summary>
    public class LiveKitReconnectSupervisor : MonoBehaviour
    {
        [SerializeField] private RoomManager roomManager;
        [SerializeField] private AppLifecycleManager lifecycleManager;
        [SerializeField] private AppStartupFlowController startupFlow;

        [Header("Backoff")]
        [SerializeField] private bool automaticReconnect = true;
        [SerializeField] private float initialBackoffSeconds = 1f;
        [SerializeField] private float maxBackoffSeconds = 20f;
        [SerializeField] private float jitterSeconds = 0.35f;
        [SerializeField] private int maxAttemptsPerDrop = 5;
        [SerializeField] private float attemptTimeoutSeconds = 40f;

        private Coroutine _reconnectLoop;
        private int _attemptCount;
        private bool _everConnected;
        private string _pendingReason = "";

        public int AttemptCount => _attemptCount;
        public bool ReconnectPending => _reconnectLoop != null;
        public string PendingReason => _pendingReason;

        private void OnEnable()
        {
            Bind();
        }

        private void Start()
        {
            Bind();
        }

        private void OnDisable()
        {
            Unbind();
        }

        private void Bind()
        {
            if (roomManager == null) roomManager = RoomManager.Instance ?? FindObjectOfType<RoomManager>();
            if (lifecycleManager == null) lifecycleManager = FindObjectOfType<AppLifecycleManager>();
            if (startupFlow == null) startupFlow = FindObjectOfType<AppStartupFlowController>();
            if (roomManager == null) return;

            roomManager.OnConnected -= HandleConnected;
            roomManager.OnDisconnected -= HandleDisconnected;
            roomManager.OnConnected += HandleConnected;
            roomManager.OnDisconnected += HandleDisconnected;

            if (roomManager.IsConnected)
                HandleConnected();
        }

        private void Unbind()
        {
            if (roomManager == null) return;
            roomManager.OnConnected -= HandleConnected;
            roomManager.OnDisconnected -= HandleDisconnected;
        }

        private void HandleConnected()
        {
            _everConnected = true;
            _attemptCount = 0;
            _pendingReason = "";
            if (_reconnectLoop != null)
            {
                StopCoroutine(_reconnectLoop);
                _reconnectLoop = null;
            }
        }

        private void HandleDisconnected()
        {
            if (!automaticReconnect) return;
            if (!_everConnected) return;
            if (roomManager != null && roomManager.IsDisconnecting) return;
            QueueReconnect("passive_room_disconnected");
        }

        public void QueueReconnect(string reason)
        {
            if (!automaticReconnect) return;
            _pendingReason = string.IsNullOrWhiteSpace(reason) ? "passive_room_disconnected" : reason;
            if (_reconnectLoop != null) return;
            _reconnectLoop = StartCoroutine(ReconnectLoop());
        }

        private IEnumerator ReconnectLoop()
        {
            while (automaticReconnect && !IsTerminalState())
            {
                while (IsBackgroundState())
                    yield return null;

                if (IsTerminalState())
                    break;

                if (roomManager != null && roomManager.IsConnected)
                    break;

                if (maxAttemptsPerDrop > 0 && _attemptCount >= maxAttemptsPerDrop)
                {
                    lifecycleManager?.ReportDegraded("fresh_token_reconnect_exhausted");
                    Debug.LogWarning(
                        $"[LiveKitReconnectSupervisor] exhausted attempts after {_attemptCount} tries ({_pendingReason})");
                    break;
                }

                float delay = ComputeBackoffSeconds(_attemptCount);
                _attemptCount++;
                lifecycleManager?.ReportReconnecting($"fresh_token_backoff:{_pendingReason}");
                if (delay > 0f)
                    yield return new WaitForSeconds(delay);

                if (IsTerminalState())
                    break;
                if (IsBackgroundState())
                    continue;

                if (startupFlow == null) startupFlow = FindObjectOfType<AppStartupFlowController>();
                if (startupFlow == null)
                {
                    Debug.LogWarning("[LiveKitReconnectSupervisor] no AppStartupFlowController; cannot mint fresh token");
                    break;
                }

                if (!startupFlow.RequestFreshTokenReconnect($"auto:{_pendingReason}"))
                {
                    Debug.LogWarning(
                        $"[LiveKitReconnectSupervisor] fresh reconnect request rejected: {startupFlow.LastError}");
                    continue;
                }

                float deadline = Time.realtimeSinceStartup + Mathf.Max(1f, attemptTimeoutSeconds);
                while (startupFlow.FreshReconnectInProgress && Time.realtimeSinceStartup < deadline)
                    yield return null;

                if (roomManager != null && roomManager.IsConnected)
                    break;

                lifecycleManager?.ReportDegraded(
                    string.IsNullOrWhiteSpace(startupFlow.LastError)
                        ? "fresh_token_reconnect_failed"
                        : startupFlow.LastError);
            }

            _reconnectLoop = null;
        }

        private float ComputeBackoffSeconds(int zeroBasedAttempt)
        {
            float baseDelay = Mathf.Max(0f, initialBackoffSeconds)
                              * Mathf.Pow(2f, Mathf.Max(0, zeroBasedAttempt));
            float capped = Mathf.Min(Mathf.Max(0f, maxBackoffSeconds), baseDelay);
            float jitter = jitterSeconds > 0f ? UnityEngine.Random.Range(0f, jitterSeconds) : 0f;
            return capped + jitter;
        }

        private bool IsBackgroundState()
        {
            if (lifecycleManager == null) return false;
            return lifecycleManager.CurrentState == AppLifecycleState.ShortBackground
                   || lifecycleManager.CurrentState == AppLifecycleState.LongBackground;
        }

        private bool IsTerminalState()
        {
            if (lifecycleManager == null) return false;
            return lifecycleManager.CurrentState == AppLifecycleState.ShuttingDown
                   || lifecycleManager.CurrentState == AppLifecycleState.Disconnected
                   || lifecycleManager.CurrentState == AppLifecycleState.ColdStart;
        }
    }
}
