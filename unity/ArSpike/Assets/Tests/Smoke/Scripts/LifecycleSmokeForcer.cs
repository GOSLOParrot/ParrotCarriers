using UnityEngine;

namespace ParrotApp.Lifecycle
{
    /// <summary>
    /// Smoke-scene-only helper: pushes AppLifecycleManager through
    /// ColdStart → Connecting → Connected in Start() so the
    /// LifecycleHeartbeatPublisher chokepoint does not block heartbeats.
    ///
    /// Start() runs after Awake(), so HealthAggregator is already initialized
    /// when we call ReportRoomConnected(). This avoids the NullReferenceException
    /// that occurred when the scene builder tried to advance state at Editor-time
    /// (before Awake had run).
    ///
    /// This component is safe to leave in a smoke scene but should NOT be used
    /// in the real App scene — real lifecycle transitions come from RoomManager.
    /// </summary>
    [RequireComponent(typeof(AppLifecycleManager))]
    public class LifecycleSmokeForcer : MonoBehaviour
    {
        void Start()
        {
            var lm = GetComponent<AppLifecycleManager>();
            if (lm == null) return;

            // Drive FSM to Connected so the heartbeat publisher fires.
            // Each Transition() call is guarded inside AppLifecycleManager,
            // so calling them in sequence is safe.
            lm.EnterConnecting();
            lm.ReportRoomConnected(); // HealthAggregator is non-null after Awake

            Debug.Log(
                "[LifecycleSmokeForcer] Lifecycle → Connected. " +
                "LifecycleHeartbeatPublisher should now emit 1 Hz heartbeats. " +
                "Check Console for [Heartbeat:LOG] lines.");
        }
    }
}
