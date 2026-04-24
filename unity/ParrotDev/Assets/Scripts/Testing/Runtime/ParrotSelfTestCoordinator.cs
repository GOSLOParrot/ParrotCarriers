using System;
using System.Collections;
using System.IO;
using UnityEngine;
using LiveKit;

#if UNITY_AR_FOUNDATION && UNITY_EDITOR
using Unity.XR.Management;
using UnityEngine.XR.ARFoundation;
using UnityEngine.XR.ARSubsystems;
#endif

/// <summary>
/// <b>Testing/Runtime</b> — periodic snapshot + optional one-shot checklist. Runs on device and Editor Play.
/// AR loader hint uses <c>LoaderUtility</c> only in Editor + AR define (Unity 2022.3 / AR Foundation 5.1 pattern).
/// <b>Test harness only</b> — snapshots aid regression and log correlation; not a substitute for a designed app launch/connect flow.
/// </summary>
public class ParrotSelfTestCoordinator : MonoBehaviour
{
    [Serializable]
    public struct Snapshot
    {
        public float UtcTime;
        public bool RoomManagerPresent;
        public bool Connected;
        public string RoomName;
        public string LocalIdentity;
        public int RemoteParticipantCount;
        public bool BrainAgentPresent;
        public bool TokenFilePresent;
        public int TokenFileChars;
        public bool ArVideoPublisherPresent;
        public bool VideoPublishing;
        public bool VideoTierReceiverPresent;
        public string VideoTier;
        public string ArSessionHint;
        public float? LastConnectDurationSeconds;
        public string XrLoaderHint;
        public string LastNote;
    }

    [SerializeField] private bool runOneShotSelfTestOnStart = true;
    [SerializeField] private float snapshotIntervalSeconds = 1.5f;

    public Snapshot LastSnapshot { get; private set; }

    private float _nextSnapshot;

    private void Start()
    {
        if (runOneShotSelfTestOnStart)
            StartCoroutine(OneShotSelfTest());
    }

    private void Update()
    {
        if (Time.unscaledTime < _nextSnapshot)
            return;
        _nextSnapshot = Time.unscaledTime + snapshotIntervalSeconds;
        LastSnapshot = BuildSnapshot();
    }

    public Snapshot BuildSnapshot()
    {
        var s = new Snapshot
        {
            UtcTime = Time.realtimeSinceStartup,
            LastNote = "",
            XrLoaderHint = "n/a",
        };

        try
        {
            var rm = RoomManager.Instance;
            s.RoomManagerPresent = rm != null;
            if (rm != null)
            {
                s.Connected = rm.IsConnected;
                s.LastConnectDurationSeconds = rm.LastConnectDurationSeconds;
                var room = rm.Room;
                if (room != null)
                {
                    s.RoomName = room.Name ?? "";
                    s.LocalIdentity = room.LocalParticipant?.Identity ?? "";
                    s.RemoteParticipantCount = room.RemoteParticipants?.Count ?? 0;
                    s.BrainAgentPresent = !string.IsNullOrEmpty(
                        BrainParticipantResolver.FindBrainParticipantId(room));
                }
            }

            var tokenPath = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "unity_join_token.txt"));
            if (File.Exists(tokenPath))
            {
                s.TokenFilePresent = true;
                try
                {
                    s.TokenFileChars = File.ReadAllText(tokenPath).Trim().Length;
                }
                catch
                {
                    s.TokenFileChars = -1;
                }
            }

            var pub = UnityEngine.Object.FindObjectOfType<ARVideoPublisher>();
            s.ArVideoPublisherPresent = pub != null;
            if (pub != null)
                s.VideoPublishing = pub.IsPublishing;

            var vtr = UnityEngine.Object.FindObjectOfType<VideoTierReceiver>();
            s.VideoTierReceiverPresent = vtr != null;
            if (vtr != null)
                s.VideoTier = vtr.CurrentTier.ToString();

#if UNITY_AR_FOUNDATION
            var ars = UnityEngine.Object.FindObjectOfType<ARSession>();
            if (ars != null)
                s.ArSessionHint = ARSession.state.ToString();
            else
                s.ArSessionHint = "no ARSession";
#else
            s.ArSessionHint = "UNITY_AR_FOUNDATION off";
#endif

#if UNITY_AR_FOUNDATION && UNITY_EDITOR
            try
            {
                var sub = LoaderUtility.GetActiveLoader()?.GetLoadedSubsystem<XRCameraSubsystem>();
                s.XrLoaderHint = sub != null ? "XRCameraSubsystem:yes" : "XRCameraSubsystem:no";
            }
            catch (Exception e)
            {
                s.XrLoaderHint = "loader:" + e.Message;
            }
#endif
        }
        catch (Exception e)
        {
            s.LastNote = "snapshot: " + e.Message;
        }

        return s;
    }

    public IEnumerator OneShotSelfTest()
    {
        var log = ParrotDiagnosticsLog.Instance;
        void L(string m)
        {
            Debug.Log("[SelfTest] " + m);
            log?.Line(m);
        }

        ParrotTestSeq.Mark("P1-step5-selftest-START");
        L("── Parrot self-test start (Testing/Runtime) ──");
        yield return null;

        if (RoomManager.Instance == null)
            L("FAIL: RoomManager missing in scene.");
        else
            L("OK: RoomManager present.");

        var rm = RoomManager.Instance;
        if (rm != null && rm.LastConnectDurationSeconds.HasValue)
            L($"INFO: last LiveKit connect took {rm.LastConnectDurationSeconds.Value:F2}s");

        if (!File.Exists(Path.GetFullPath(Path.Combine(Application.dataPath, "..", "unity_join_token.txt"))))
            L("WARN: unity_join_token.txt not found next to ParrotDev (optional if token in Inspector).");
        else
            L("OK: unity_join_token.txt exists.");

        yield return new WaitForSecondsRealtime(3f);

        var snap = BuildSnapshot();
        if (snap.Connected)
            L($"OK: LiveKit connected room='{snap.RoomName}' me='{snap.LocalIdentity}'.");
        else
            L("WARN: Not connected after 3s (check URL/token/LiveKit/Brain).");

        if (snap.BrainAgentPresent)
            L("OK: Brain participant in room (agent-* or identity brain).");
        else if (snap.Connected)
            L("WARN: No Brain participant yet (Brain may join later).");

        if (snap.ArVideoPublisherPresent && snap.VideoPublishing)
            L("OK: ARVideoPublisher is publishing.");
        else if (snap.ArVideoPublisherPresent)
            L("WARN: ARVideoPublisher present but not publishing yet.");
        else
            L("WARN: No ARVideoPublisher in scene.");

        if (snap.VideoTierReceiverPresent)
            L($"OK: VideoTierReceiver tier={snap.VideoTier}.");
        else
            L("WARN: No VideoTierReceiver (Brain setVideoTier will not apply).");

        L($"AR session: {snap.ArSessionHint}  |  {snap.XrLoaderHint}");
        L("── Parrot self-test end ──");
        ParrotTestSeq.Mark("P1-step5-selftest-END");
    }

    public void RunSelfTestFromUi()
    {
        StopAllCoroutines();
        StartCoroutine(OneShotSelfTest());
    }
}
