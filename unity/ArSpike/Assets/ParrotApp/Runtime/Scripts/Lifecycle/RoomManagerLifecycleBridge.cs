using System;
using LiveKit;
using ParrotApp.Health;
using ParrotApp.LiveKit;
using UnityEngine;

namespace ParrotApp.Lifecycle
{
    /// <summary>
    /// Translates <see cref="RoomManager"/> LiveKit events into lifecycle and
    /// connection-health updates.
    ///
    /// Design constraints:
    /// <list type="bullet">
    /// <item>This component is a bridge only. It subscribes to RoomManager events
    /// and calls AppLifecycleManager / ConnectionHealthAggregator setters.</item>
    /// <item>It does not introduce reconnect policy, Brain behavior, or audio route
    /// decisions. Those stay in the lifecycle manager, Brain, and audio modules.</item>
    /// <item>It is the single producer for room_connected, brain_present,
    /// reconnect_attempt_count, and last_disconnected_at health fields.</item>
    /// </list>
    /// </summary>
    [RequireComponent(typeof(AppLifecycleManager))]
    public class RoomManagerLifecycleBridge : MonoBehaviour
    {
        [Tooltip("Optional. Falls back to RoomManager.Instance when null.")]
        [SerializeField] private RoomManager roomManager;

        [Tooltip("Brain identity prefix; must match BrainParticipantResolver detection logic.")]
        [SerializeField] private string brainIdentityPrefix = "agent-";

        private AppLifecycleManager _lifecycle;

        // Keep this as a property instead of a cached field. AppLifecycleManager
        // creates the aggregator in its own Awake, and script execution order is
        // not guaranteed across scenes.
        private ConnectionHealthAggregator Health =>
            _lifecycle != null ? _lifecycle.HealthAggregator : null;

        // Accumulates reconnect attempts across reconnect cycles. The lifecycle
        // owner decides when the counter is meaningful to reset.
        private int _reconnectAttemptCount;

        // Tracks the currently recognized Brain participant so disconnect storms
        // do not repeatedly toggle brain_present for unrelated participants.
        private string _currentBrainIdentity = "";

        private static double UnixSeconds()
            => (DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalSeconds;

        protected virtual void Awake()
        {
            _lifecycle = GetComponent<AppLifecycleManager>();
        }

        protected virtual void OnEnable()
        {
            BindRoomManager();
        }

        protected virtual void Start()
        {
            // RoomManager.Instance may appear after this component's Awake.
            // Bind again in Start; the method is idempotent.
            BindRoomManager();
        }

        protected virtual void OnDisable()
        {
            UnbindRoomManager();
        }

        private void BindRoomManager()
        {
            if (roomManager == null) roomManager = RoomManager.Instance;
            if (roomManager == null) return;

            // Idempotent subscription: remove first, then add.
            roomManager.OnConnecting -= HandleConnecting;
            roomManager.OnConnected -= HandleConnected;
            roomManager.OnDisconnected -= HandleDisconnected;
            roomManager.OnParticipantConnected -= HandleParticipantConnected;
            roomManager.OnParticipantDisconnected -= HandleParticipantDisconnected;

            roomManager.OnConnecting += HandleConnecting;
            roomManager.OnConnected += HandleConnected;
            roomManager.OnDisconnected += HandleDisconnected;
            roomManager.OnParticipantConnected += HandleParticipantConnected;
            roomManager.OnParticipantDisconnected += HandleParticipantDisconnected;
        }

        private void UnbindRoomManager()
        {
            if (roomManager == null) return;

            roomManager.OnConnecting -= HandleConnecting;
            roomManager.OnConnected -= HandleConnected;
            roomManager.OnDisconnected -= HandleDisconnected;
            roomManager.OnParticipantConnected -= HandleParticipantConnected;
            roomManager.OnParticipantDisconnected -= HandleParticipantDisconnected;
        }

        private void HandleConnecting()
        {
            var state = _lifecycle.CurrentState;
            bool isReconnect =
                state == AppLifecycleState.Reconnecting
                || state == AppLifecycleState.LongBackground
                || state == AppLifecycleState.Degraded
                || state == AppLifecycleState.Disconnected
                || state == AppLifecycleState.Connected
                || state == AppLifecycleState.Running;

            if (isReconnect)
            {
                _reconnectAttemptCount++;
                Health?.ReportReconnectAttempt(_reconnectAttemptCount, UnixSeconds());
                _lifecycle.ReportReconnecting("RoomManager.OnConnecting (reconnect)");
                return;
            }

            _lifecycle.EnterConnecting();
        }

        private void HandleConnected()
        {
            var now = UnixSeconds();

            // RoomManager/Bridge is the sole producer for room_connected and
            // brain_present. Connected only proves the room transport is up;
            // Brain presence is reported through participant discovery below.
            Health?.ReportRoomConnected(true, now);
            _lifecycle.ReportRoomConnected();

            _reconnectAttemptCount = 0;
            Health?.ReportReconnectAttempt(0, now);

            // Brain may already be in the room before this component subscribes.
            ScanForBrainParticipant();
        }

        private void HandleDisconnected()
        {
            var now = UnixSeconds();
            Health?.ReportRoomConnected(false, now);
            Health?.ReportBrainPresent(false, now);
            _currentBrainIdentity = "";

            if (roomManager != null && roomManager.IsDisconnecting)
            {
                // Graceful disconnect is owned by LifecycleShutdownService. It
                // will move the FSM to Disconnected after Dispose and cooldown.
                Debug.Log("[Bridge] Disconnect was intentional; lifecycle remains owned by the chokepoint");
                return;
            }

            _lifecycle.ReportReconnecting("RoomManager.OnDisconnected (passive)");
        }

        private void HandleParticipantConnected(RemoteParticipant participant)
        {
            if (!IsBrainIdentity(participant?.Identity)) return;

            _currentBrainIdentity = participant.Identity;
            Health?.ReportBrainPresent(true, UnixSeconds());
        }

        private void HandleParticipantDisconnected(RemoteParticipant participant)
        {
            if (string.IsNullOrEmpty(participant?.Identity)) return;
            if (!string.Equals(participant.Identity, _currentBrainIdentity, StringComparison.Ordinal)) return;

            _currentBrainIdentity = "";
            Health?.ReportBrainPresent(false, UnixSeconds());

            // Another agent-* participant may still be present.
            ScanForBrainParticipant();
        }

        private void ScanForBrainParticipant()
        {
            if (roomManager?.Room == null) return;

            var brainId = BrainParticipantResolver.FindBrainParticipantId(roomManager.Room);
            if (string.IsNullOrEmpty(brainId)) return;
            if (string.Equals(brainId, _currentBrainIdentity, StringComparison.Ordinal)) return;

            _currentBrainIdentity = brainId;
            Health?.ReportBrainPresent(true, UnixSeconds());
        }

        private bool IsBrainIdentity(string identity)
        {
            if (string.IsNullOrEmpty(identity)) return false;
            if (identity.StartsWith(brainIdentityPrefix, StringComparison.Ordinal)) return true;
            return string.Equals(identity, "brain", StringComparison.OrdinalIgnoreCase);
        }
    }
}
