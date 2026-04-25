using System;
using System.Collections;
using System.IO;
using UnityEngine;
using LiveKit;

#if UNITY_AR_FOUNDATION
using UnityEngine.XR.ARFoundation;
#endif

#if UNITY_AR_FOUNDATION && UNITY_EDITOR
using Unity.XR.Management;
using UnityEngine.XR.ARSubsystems;
#endif

/// <summary>
/// <b>Testing/Runtime</b> — 周期快照（~1.5s）+ 可选启动后一次性自检协程；Editor 与真机均可。<br/>
/// AR 子系统提示仅在 <c>UNITY_EDITOR</c> 且项目显式定义 <c>UNITY_AR_FOUNDATION</c> 时用 <c>LoaderUtility</c>（Unity 2022.3 / AR Foundation 5.1）。<br/>
/// <b>仅测试束</b>：与 <see cref="ParrotRuntimeHud"/> 配合；真机勿依赖 F3，见 <c>docs/test/p2_5/mobile_runtime_harness_zh.md</c>。<br/>
/// 多通道摘要（视频 / 音频 / RPC / DataChannel）见 <c>docs/test/p2_5/unity_channels_audit_mobile_zh.md</c>。
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
        public string VideoSource;
        public int VideoFrameCount;
        public float VideoLastFrameAgeSeconds;
        public bool VideoFrameFresh;
        public float VideoStaleThresholdSeconds;
        public string VideoLastError;
        public bool VideoTierReceiverPresent;
        public string VideoTier;
        public bool MicPublisherPresent;
        public bool MicPublishing;
        public bool MicPublishAttempted;
        public string MicDevice;
        public string MicLastError;
        public bool ParrotRpcHandlerPresent;
        public bool XrHandTrackerPresent;
        public bool SceneProfileManagerPresent;
        public bool VideoStateReporterPresent;
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
            {
                s.VideoPublishing = pub.IsPublishing;
                s.VideoSource = pub.VideoSourceLabel ?? "";
                s.VideoFrameCount = pub.ProducedFrameCount;
                s.VideoLastFrameAgeSeconds = pub.LastFrameAgeSeconds;
                s.VideoFrameFresh = pub.HasFreshFrame;
                s.VideoStaleThresholdSeconds = pub.StaleFrameThresholdSeconds;
                s.VideoLastError = pub.LastPublishError ?? "";
            }

            var vtr = UnityEngine.Object.FindObjectOfType<VideoTierReceiver>();
            s.VideoTierReceiverPresent = vtr != null;
            if (vtr != null)
                s.VideoTier = vtr.CurrentTier.ToString();

            var mic = UnityEngine.Object.FindObjectOfType<MicrophonePublisher>();
            s.MicPublisherPresent = mic != null;
            if (mic != null)
            {
                s.MicPublishing = mic.IsPublishing;
                s.MicPublishAttempted = mic.PublishAttempted;
                s.MicDevice = mic.SelectedDevice ?? "";
                s.MicLastError = mic.LastError ?? "";
            }

            s.ParrotRpcHandlerPresent = UnityEngine.Object.FindObjectOfType<ParrotRpcHandler>() != null;
            s.XrHandTrackerPresent = UnityEngine.Object.FindObjectOfType<XRHandTracker>() != null;
            s.SceneProfileManagerPresent = UnityEngine.Object.FindObjectOfType<SceneProfileManager>() != null;
            s.VideoStateReporterPresent = UnityEngine.Object.FindObjectOfType<VideoStateReporter>() != null;

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

#if UNITY_EDITOR || UNITY_STANDALONE
        if (!File.Exists(Path.GetFullPath(Path.Combine(Application.dataPath, "..", "unity_join_token.txt"))))
            L("INFO: unity_join_token.txt not found next to ParrotDev (desktop/dev-token path only; normal for Launcher/Mint flows).");
        else
            L("OK: unity_join_token.txt exists (desktop/dev-token path).");
#else
        L("INFO: Skipping unity_join_token.txt check on device build; true device path should use Launcher/Mint or injected token.");
#endif

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

        if (snap.ArVideoPublisherPresent && snap.VideoPublishing && snap.VideoFrameFresh)
            L($"OK: ARVideoPublisher is publishing fresh frames (source={snap.VideoSource}, frames={snap.VideoFrameCount}, lastAge={snap.VideoLastFrameAgeSeconds:F2}s).");
        else if (snap.ArVideoPublisherPresent && snap.VideoPublishing)
            L($"WARN: ARVideoPublisher track is published but frames are stale (source={snap.VideoSource}, frames={snap.VideoFrameCount}, lastAge={snap.VideoLastFrameAgeSeconds:F2}s, stale>{snap.VideoStaleThresholdSeconds:F1}s). Gemini may see black or old frames.");
        else if (snap.ArVideoPublisherPresent)
            L($"WARN: ARVideoPublisher present but not publishing yet (source={snap.VideoSource}, frames={snap.VideoFrameCount}, error='{snap.VideoLastError}').");
        else
            L("WARN: No ARVideoPublisher in scene.");

        if (snap.VideoTierReceiverPresent)
            L($"OK: VideoTierReceiver tier={snap.VideoTier}.");
        else
            L("WARN: No VideoTierReceiver (Brain setVideoTier will not apply).");

        if (snap.MicPublisherPresent && snap.MicPublishing)
            L($"OK: MicrophonePublisher is publishing (voice track to room, device='{snap.MicDevice}').");
        else if (snap.MicPublisherPresent)
            L($"WARN: MicrophonePublisher present but not publishing (attempted={snap.MicPublishAttempted}, device='{snap.MicDevice}', error='{snap.MicLastError}').");
        else
            L("WARN: No MicrophonePublisher — no local voice track (Gemini Live / Brain cannot hear you).");

        if (snap.ParrotRpcHandlerPresent)
            L("OK: ParrotRpcHandler present (Brain→Unity flyTo/animate path).");
        else
            L("WARN: No ParrotRpcHandler — Brain→Unity animation RPC will fail.");

        if (snap.XrHandTrackerPresent)
            L("OK: XRHandTracker present (Lossy DataChannel parrot.event / hand_gesture when connected).");
        else
            L("INFO: No XRHandTracker (hand telemetry DataChannel optional).");

        if (snap.SceneProfileManagerPresent)
            L("OK: SceneProfileManager Instance (setScene RPC after connect).");
        else
            L("WARN: No SceneProfileManager — setScene to Brain may be skipped.");

        if (snap.VideoStateReporterPresent)
            L("OK: VideoStateReporter present (Unity→Brain visual state RPC).");
        else
            L("WARN: No VideoStateReporter in scene — TRACK_MUTED / visual degrade RPC path missing.");

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
