using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Rendering;
using LiveKit;
using LiveKit.Proto;

#if UNITY_AR_FOUNDATION
using UnityEngine.XR.ARFoundation;
#endif

/// <summary>
/// Publishes camera pixels to LiveKit as one <b>video track</b> (Brain / Gemini Live may subscribe).
///
/// <b>Test harness vs shipped AR app (read before Sprint 4 / AR workspace)</b><br/>
/// • This class is used in <b>P2.5 / Sprint 3 bus + perf + data-flow testing</b> — not the final
///   AR app launch UX or quality gate.<br/>
/// • <b>Editor XR Simulation</b> and <b>physical device ARCore</b> differ (camera, IMU, latency).
///   Neither is “wrong”; Editor is convenience only. <b>Do not</b> treat Editor sim pixels as the
///   product definition of “high quality video”.<br/>
/// • <b>Supplemental / on-demand (harness)</b>: XR Simulation (or Editor forced WebCam) images are
///   acceptable for <b>connectivity, tier/mute lifecycle, short clips, screenshots, rough perf</b>.
///   Treat them as a <b>probe track</b>, not as the AR app’s committed “main perception stream”.<br/>
/// • <b>Primary / product-quality capture (future app)</b>: reserved for the real-device pipeline
///   (e.g. ARCore camera + agreed tier/bitrate + app start policy). Sprint 4 may add explicit
///   switching (e.g. test menus) — prefer <b>not</b> using full-screen rendered GameView as the
///   long-term high-rate source (costly); separate identify / burst capture design belongs in
///   Sprint 4 docs, not inferred from this harness alone.<br/>
/// • <b>Other “supplemental channels”</b> in the stack: LiveKit <b>RPC + DataChannel</b> carry control
///   and state (e.g. scene, video tier, RPC tools). They are <b>not</b> this video track; do not
///   conflate DataChannel/RPC results with camera quality conclusions.
///
/// <b>Sources (this component)</b><br/>
/// • <b>AR path</b> (device or XR Simulation when AR Foundation is active): ARCameraBackground blits
///   AR camera output → RenderTexture → TextureVideoSource.<br/>
/// • <b>WebCam fallback</b>: WebCamTexture when AR path is unavailable or explicitly enabled.
///   Standalone (Win/Mac/Linux) Dev builds mirror Editor: if AR is inactive and the checkbox is off,
///   webcam is still forced so LiveKit gets a video track (camera pixels, not the game window).
///
/// Sprint 3 T-U5: dynamic track republish (UnpublishTrack → PublishTrack) for tier changes;
/// sends <c>track_rebuilding</c> RPC so PerceptionSupervisor skips degraded-window ticks.
///
/// Requires RoomManager connected.
/// </summary>
public class ARVideoPublisher : MonoBehaviour
{
    [Header("Video Settings")]
    [SerializeField] private int width = 1280;
    [SerializeField] private int height = 720;
    [SerializeField] private int targetFps = 30;

    [Header("Tier Encoding Presets (Sprint 3 T-U5)")]
    [Tooltip("Bitrate for VIDEO_FULL (bps)")]
    [SerializeField] private int fullBitrate = 1_000_000;
    [Tooltip("FPS for VIDEO_FULL")]
    [SerializeField] private int fullFps = 30;
    [Tooltip("Bitrate for VIDEO_GEMINI_ONLY (bps)")]
    [SerializeField] private int geminiOnlyBitrate = 300_000;
    [Tooltip("FPS for VIDEO_GEMINI_ONLY")]
    [SerializeField] private int geminiOnlyFps = 15;

    [Header("AR Components (assign if AR Foundation available)")]
    [SerializeField] private Camera arCamera;

    [Header("Dev Fallback")]
    [Tooltip(
        "When AR path (ARCameraManager+Background) is missing or inactive, use WebCamTexture. "
        + "Harness-only: not the product AR stream. Editor/Standalone Player may still force webcam if AR is off — see class doc.")]
    [SerializeField] private bool useWebcamFallback = true;

    [Tooltip("Substring match (case-insensitive). Leave empty for auto (prefers first non-virtual device).")]
    [SerializeField] private string preferredDeviceName = "";

    [Tooltip("How many real frames to pre-blit to RenderTexture before publishing (avoids first-frame black).")]
    [SerializeField] private int webcamWarmupFrames = 3;

    [Tooltip("Harness guard: wait this long for first AR/WebCam frame before deciding the source is not producing pixels.")]
    [SerializeField] private float firstFrameTimeoutSeconds = 8f;
    [Tooltip("Frames older than this are treated as stale even if the LiveKit track is still published.")]
    [SerializeField] private float staleFrameThresholdSeconds = 3f;

    private RenderTexture _rt;
    private TextureVideoSource _videoSource;
    private LocalVideoTrack _videoTrack;
    private bool _isPublishing;
    private bool _publishMuted;
    private bool _isRebuilding;
    private bool _setupInProgress;
    private int _producedFrameCount;
    private float _lastProducedFrameTime = -1f;
    private string _videoSourceLabel = "none";
    private string _lastPublishError = "";

    // Sprint 3: current tier for rebuild decisions
    public enum VideoTierLocal { Unknown, Off, GeminiOnly, Full, Burst }
    private VideoTierLocal _currentTier = VideoTierLocal.GeminiOnly;

    /// <summary>
    /// Fires whenever SetPublishMuted flips the track's muted state.
    /// Consumed by VideoStateReporter to forward the change to the Brain
    /// as a TRACK_MUTED / OK degrade reason (Sprint 2 T11).
    /// </summary>
    public event Action<bool> OnPublishMutedChanged;

    public bool IsPublishing => _isPublishing;
    public bool IsPublishMuted => _publishMuted;
    public int ProducedFrameCount => _producedFrameCount;
    public string VideoSourceLabel => _videoSourceLabel;
    public string LastPublishError => _lastPublishError;
    public float LastFrameAgeSeconds =>
        _lastProducedFrameTime < 0f ? -1f : Time.realtimeSinceStartup - _lastProducedFrameTime;
    public float StaleFrameThresholdSeconds => staleFrameThresholdSeconds;
    public bool HasFreshFrame =>
        _producedFrameCount > 0 &&
        LastFrameAgeSeconds >= 0f &&
        LastFrameAgeSeconds <= staleFrameThresholdSeconds;

    // Dev fallback
    private WebCamTexture _webcam;
    private Coroutine _webcamBlit;
    private bool _webcamReady;

#if UNITY_AR_FOUNDATION
    private ARCameraManager _arCameraManager;
    private ARCameraBackground _arCameraBackground;
#endif

    void Start()
    {
        var rm = RoomManager.Instance;
        if (rm == null)
        {
            Debug.LogWarning("[ARVideoPublisher] RoomManager not found, waiting...");
            return;
        }

        rm.OnConnected += OnRoomConnected;
        rm.OnDisconnected += OnRoomDisconnected;
        if (rm.IsConnected) OnRoomConnected();
    }

    private void OnRoomConnected()
    {
        if (_isPublishing || _setupInProgress) return;
        StartCoroutine(SetupAndPublish());
    }

    private IEnumerator SetupAndPublish()
    {
        _setupInProgress = true;
        _rt = new RenderTexture(width, height, 0, RenderTextureFormat.ARGB32);
        _rt.Create();
        _webcamReady = false;
        _producedFrameCount = 0;
        _lastProducedFrameTime = -1f;
        _videoSourceLabel = "none";
        _lastPublishError = "";

        bool arAvailable = TrySetupAR();
        bool useWebcam = useWebcamFallback;

#if UNITY_EDITOR
        // Harness: avoid zero-video in Editor when Augment set useWebcamFallback=false but AR
        // path is inactive (XR Sim off, missing components, or AR scripting stripped). This is
        // NOT a product decision — Sprint 4 / AR app may require explicit loader + start policy.
        if (!arAvailable && !useWebcam)
        {
            Debug.LogWarning(
                "[ARVideoPublisher] Editor harness: AR camera path unavailable — forcing webcam fallback "
                + "(for XR Sim AR pixels: enable XR Simulation + AR camera; then turn useWebcamFallback off).");
            useWebcam = true;
        }
#elif UNITY_STANDALONE
        // Win/Mac/Linux Player: no AR session in typical Dev build — same zero-video trap as Editor.
        // Product AR builds use device IL2CPP + AR Foundation; standalone harness uses webcam only.
        if (!arAvailable && !useWebcam)
        {
            Debug.LogWarning(
                "[ARVideoPublisher] Standalone harness: AR path unavailable — forcing webcam fallback "
                + "(captures camera, not the game window; for XR Sim / device AR use an AR-enabled build).");
            useWebcam = true;
        }
#endif

        if (!arAvailable && useWebcam)
        {
            Debug.Log("[ARVideoPublisher] AR not available, using webcam fallback");
            yield return SetupWebcamFallback();
            if (!_webcamReady)
            {
                _lastPublishError = "webcam_fallback_no_frames";
                Debug.LogError("[ARVideoPublisher] ERROR webcam_fallback_no_frames: WebCam fallback failed to produce frames; aborting video publish");
                _setupInProgress = false;
                yield break;
            }
        }
        else if (!arAvailable)
        {
            _lastPublishError = "no_video_source";
            Debug.LogWarning("[ARVideoPublisher] ERROR no_video_source: No AR camera path and webcam fallback disabled");
            _setupInProgress = false;
            yield break;
        }
        else
        {
            yield return WaitForFirstFrame("AR", firstFrameTimeoutSeconds);
            if (_producedFrameCount == 0)
            {
                _lastPublishError = "ar_path_no_frames";
                Debug.LogError("[ARVideoPublisher] ERROR ar_path_no_frames: AR path was present but produced no camera frames; aborting video publish");
                _setupInProgress = false;
                yield break;
            }
        }

        var rm = RoomManager.Instance;
        if (rm == null || !rm.IsConnected)
        {
            _lastPublishError = "room_disconnected_before_publish";
            Debug.LogWarning("[ARVideoPublisher] ERROR room_disconnected_before_publish: Room no longer connected after setup, aborting publish");
            _setupInProgress = false;
            yield break;
        }
        var room = rm.Room;
        if (room == null)
        {
            _lastPublishError = "room_missing_before_publish";
            Debug.LogWarning("[ARVideoPublisher] ERROR room_missing_before_publish: Room missing before video publish");
            _setupInProgress = false;
            yield break;
        }

        _videoSource = new TextureVideoSource(_rt);
        _videoTrack = LocalVideoTrack.CreateVideoTrack("ar-camera", _videoSource, room);

        // BUG-A2 fix (Sprint 3 audit 2026-04-23):
        // Previous code hardcoded 1_500_000 bps which contradicts Brain's DEFAULT_COMBO
        // (VIDEO_GEMINI_ONLY = 300 kbps / 15 fps written to Blackboard at startup).
        // Now we read _currentTier (defaults to GeminiOnly in field initializer, line ~65)
        // so the initial publish matches the Brain's expected state without a round-trip RPC.
        //
        // If the Brain has already sent a setVideoTier before publish completes (race),
        // VideoTierReceiver.ApplyTier() will call RebuildTrack() and reconcile.
        int initBitrate;
        int initFps;
        switch (_currentTier)
        {
            case VideoTierLocal.Full:
                initBitrate = fullBitrate;
                initFps     = fullFps;
                break;
            case VideoTierLocal.Burst:
                initBitrate = fullBitrate * 2;
                initFps     = fullFps;
                break;
            default:   // GeminiOnly (default) and Off (will be muted immediately after)
                initBitrate = geminiOnlyBitrate;
                initFps     = geminiOnlyFps;
                break;
        }
        // Sync the live targetFps so the capture loop starts at the right rate.
        targetFps = initFps;

        var options = new TrackPublishOptions
        {
            VideoCodec = VideoCodec.H264,
            VideoEncoding = new VideoEncoding
            {
                MaxBitrate = (ulong)initBitrate,   // VideoEncoding.MaxBitrate is ulong
                MaxFramerate = initFps,
            },
            Source = TrackSource.SourceCamera,
        };
        Debug.Log($"[ARVideoPublisher] Initial publish tier={_currentTier} bitrate={initBitrate} fps={initFps}");

        var publish = room.LocalParticipant.PublishTrack(_videoTrack, options);
        yield return publish;

        if (publish.IsError)
        {
            Debug.LogError("[ARVideoPublisher] ERROR publish_h264_failed: Failed to publish video (H264), falling back to VP8 (PublishTrackInstruction.IsError; no Error details in SDK)");

            options.VideoCodec = VideoCodec.Vp8;
            publish = room.LocalParticipant.PublishTrack(_videoTrack, options);
            yield return publish;

            if (publish.IsError)
            {
                _lastPublishError = "publish_vp8_failed";
                Debug.LogError("[ARVideoPublisher] ERROR publish_vp8_failed: VP8 fallback also failed, aborting (PublishTrackInstruction.IsError; no Error details in SDK)");
                _setupInProgress = false;
                yield break;
            }
        }

        _videoSource.Start();
        StartCoroutine(_videoSource.Update());
        _isPublishing = true;

        // Apply any mute state that was set before the track was published.
        // SetPublishMuted() may be called by VideoTierReceiver during boot
        // (e.g. VIDEO_OFF arrives while SetupAndPublish is still running).
        // The call-site caches _publishMuted but can only call SetMute on a
        // live track; so we replay the request here now that the track exists.
        if (_publishMuted)
        {
            try
            {
                ((ILocalTrack)_videoTrack).SetMute(true);
                Debug.Log("[ARVideoPublisher] Applied pre-publish mute (VIDEO_OFF was set during setup)");
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[ARVideoPublisher] Pre-publish mute apply failed: {e.Message}");
            }
        }

        Debug.Log($"[ARVideoPublisher] Publishing {width}x{height}@{targetFps}fps source={_videoSourceLabel} frames={_producedFrameCount} (muted={_publishMuted})");
        _setupInProgress = false;
    }

    private IEnumerator WaitForFirstFrame(string sourceLabel, float timeoutSeconds)
    {
        float remaining = Mathf.Max(0.1f, timeoutSeconds);
        while (_producedFrameCount == 0 && remaining > 0f)
        {
            remaining -= Time.deltaTime;
            yield return null;
        }

        if (_producedFrameCount > 0)
            Debug.Log($"[ARVideoPublisher] First {sourceLabel} frame received (frames={_producedFrameCount})");
    }

    private void RecordProducedFrame(string sourceLabel)
    {
        _videoSourceLabel = sourceLabel;
        _producedFrameCount++;
        _lastProducedFrameTime = Time.realtimeSinceStartup;
    }

    // ── AR Foundation path ──────────────────────────────────────────

    private bool TrySetupAR()
    {
#if UNITY_AR_FOUNDATION
        if (arCamera == null) arCamera = Camera.main;
        if (arCamera == null) return false;

        _arCameraManager = arCamera.GetComponent<ARCameraManager>();
        _arCameraBackground = arCamera.GetComponent<ARCameraBackground>();

        if (_arCameraManager == null || _arCameraBackground == null)
            return false;

        // Reconnect tests can call SetupAndPublish more than once in the same scene.
        // Remove first so the harness does not double-count frames after a room reconnect.
        _arCameraManager.frameReceived -= OnARFrameReceived;
        _arCameraManager.frameReceived += OnARFrameReceived;
        Debug.Log("[ARVideoPublisher] AR Foundation camera attached");
        return true;
#else
        return false;
#endif
    }

#if UNITY_AR_FOUNDATION
    private void OnARFrameReceived(ARCameraFrameEventArgs args)
    {
        if (_rt == null || _arCameraBackground == null) return;

        var mat = _arCameraBackground.material;
        if (mat == null) return;

        Graphics.Blit(null, _rt, mat);
        RecordProducedFrame("AR");
    }
#endif

    // ── Webcam dev fallback ─────────────────────────────────────────

    private IEnumerator SetupWebcamFallback()
    {
        var devices = WebCamTexture.devices;
        if (devices.Length == 0)
        {
            Debug.LogWarning("[ARVideoPublisher] ERROR no_webcam_devices: No webcam found");
            yield break;
        }

        Debug.Log($"[ARVideoPublisher] Found {devices.Length} webcam device(s):");
        for (int i = 0; i < devices.Length; i++)
        {
            Debug.Log($"  [{i}] {devices[i].name} (frontFacing={devices[i].isFrontFacing})");
        }

        string deviceName = SelectWebcamDevice(devices);
        Debug.Log($"[ARVideoPublisher] Selected webcam: {deviceName}");

        _webcam = new WebCamTexture(deviceName, width, height, targetFps);
        _webcam.Play();

        float timeout = 5f;
        while (!_webcam.didUpdateThisFrame && timeout > 0f)
        {
            timeout -= Time.deltaTime;
            yield return null;
        }

        if (!_webcam.isPlaying)
        {
            Debug.LogWarning("[ARVideoPublisher] ERROR webcam_failed_to_start: Webcam failed to start");
            yield break;
        }

        Debug.Log($"[ARVideoPublisher] Webcam started: {deviceName} " +
                  $"(requested={width}x{height}@{targetFps}, actual={_webcam.width}x{_webcam.height})");

        int blitted = 0;
        float warmupTimeout = 2f;
        while (blitted < webcamWarmupFrames && warmupTimeout > 0f)
        {
            if (_webcam.didUpdateThisFrame)
            {
                Graphics.Blit(_webcam, _rt);
                RecordProducedFrame("WebCam");
                blitted++;
            }
            warmupTimeout -= Time.deltaTime;
            yield return null;
        }
        Debug.Log($"[ARVideoPublisher] Webcam warmup complete ({blitted}/{webcamWarmupFrames} frames pre-blitted)");

        if (blitted == 0)
        {
            Debug.LogWarning("[ARVideoPublisher] ERROR webcam_no_warmup_frames: Webcam started but produced no warmup frames");
            yield break;
        }

        _webcamReady = true;
        _webcamBlit = StartCoroutine(BlitWebcamLoop());
    }

    private string SelectWebcamDevice(WebCamDevice[] devices)
    {
        if (!string.IsNullOrEmpty(preferredDeviceName))
        {
            foreach (var d in devices)
            {
                if (d.name.IndexOf(preferredDeviceName, System.StringComparison.OrdinalIgnoreCase) >= 0)
                    return d.name;
            }
            Debug.LogWarning($"[ARVideoPublisher] preferredDeviceName '{preferredDeviceName}' not matched, using auto");
        }

        string[] virtualKeywords =
        {
            "obs", "virtual", "xsplit", "manycam", "snap camera", "droidcam", "mmhmm", "splitcam"
        };
        foreach (var d in devices)
        {
            string lower = d.name.ToLowerInvariant();
            bool isVirtual = false;
            foreach (var kw in virtualKeywords)
            {
                if (lower.Contains(kw)) { isVirtual = true; break; }
            }
            if (!isVirtual) return d.name;
        }

        return devices[0].name;
    }

    private IEnumerator BlitWebcamLoop()
    {
        while (_webcam != null && _webcam.isPlaying)
        {
            if (_webcam.didUpdateThisFrame)
            {
                Graphics.Blit(_webcam, _rt);
                RecordProducedFrame("WebCam");
            }
            yield return null;
        }
    }

    // ── Runtime mute control (Sprint 2 T10) ─────────────────────────

    /// <summary>
    /// Mute or unmute the published video track at runtime. Safe to call
    /// before the track is published (caches the desired state and applies
    /// on publish). Used for VIDEO_OFF transitions.
    /// </summary>
    public void SetPublishMuted(bool muted)
    {
        if (_publishMuted == muted) return;
        _publishMuted = muted;

        if (_videoTrack != null)
        {
            try
            {
                ((ILocalTrack)_videoTrack).SetMute(muted);
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[ARVideoPublisher] SetPublishMuted({muted}) failed: {e.Message}");
            }
        }

        Debug.Log($"[ARVideoPublisher] publish muted → {muted}");
        OnPublishMutedChanged?.Invoke(muted);
    }

    // ── Dynamic track rebuild (Sprint 3 T-U5) ────────────────────────

    /// <summary>
    /// Apply a new video tier by rebuilding the LiveKit track with updated
    /// encoding options. VIDEO_OFF uses mute (no rebuild needed). Other
    /// tier transitions go through UnpublishTrack → PublishTrack.
    ///
    /// During rebuild, sends "track_rebuilding" RPC to Brain (D4 decision)
    /// so PerceptionSupervisor skips the degraded-timer window.
    /// </summary>
    public void ApplyVideoTier(VideoTierLocal newTier)
    {
        if (_currentTier == newTier) return;
        var prev = _currentTier;
        _currentTier = newTier;

        Debug.Log($"[ARVideoPublisher] Tier change: {prev} → {newTier}");

        if (newTier == VideoTierLocal.Off)
        {
            SetPublishMuted(true);
            return;
        }

        // Unmute first if coming from Off
        if (prev == VideoTierLocal.Off)
            SetPublishMuted(false);

        // If not yet publishing (track not created), next SetupAndPublish will use correct preset
        if (!_isPublishing || _isRebuilding) return;

        // Rebuild track with new encoding options
        StartCoroutine(RebuildTrack(newTier));
    }

    private IEnumerator RebuildTrack(VideoTierLocal tier)
    {
        _isRebuilding = true;

        // Notify Brain: track is temporarily down (D4 — suppress degraded timer)
        yield return StartCoroutine(SendTrackRebuildingRpc(true));

        var rm = RoomManager.Instance;
        if (rm == null || !rm.IsConnected || rm.Room == null)
        {
            _isRebuilding = false;
            yield break;
        }
        var room = rm.Room;

        // Unpublish existing track.
        // NOTE: C# prohibits `yield return` inside a try block that has a catch clause (CS1626).
        // UnpublishTrackInstruction does not expose .IsError (unlike PublishTrackInstruction);
        // PublishTrackInstruction exposes IsError but not Error details in this SDK.
        // We just yield-and-proceed; LiveKit cleans up the track internally.
        if (_videoTrack != null)
        {
            _videoSource?.Stop();
            // stopOnUnpublish: true — also stops the local track source on the server side.
            yield return room.LocalParticipant.UnpublishTrack(_videoTrack, stopOnUnpublish: true);
            Debug.Log("[ARVideoPublisher] Track unpublished for rebuild");
            _videoTrack = null;
            _isPublishing = false;
        }

        // Brief pause to let LiveKit process the unpublish
        yield return new WaitForSeconds(0.3f);

        // Re-publish with new options
        (int bitrate, int fps) = tier switch
        {
            VideoTierLocal.Full  => (fullBitrate, fullFps),
            VideoTierLocal.Burst => (fullBitrate * 2, fullFps),
            _                    => (geminiOnlyBitrate, geminiOnlyFps),
        };

        _videoSource = new TextureVideoSource(_rt);
        _videoTrack = LocalVideoTrack.CreateVideoTrack("ar-camera", _videoSource, room);

        var options = new TrackPublishOptions
        {
            VideoCodec = VideoCodec.H264,
            VideoEncoding = new VideoEncoding
            {
                MaxBitrate = (ulong)bitrate,   // VideoEncoding.MaxBitrate is ulong
                MaxFramerate = fps,
            },
            Source = TrackSource.SourceCamera,
        };

        var publish = room.LocalParticipant.PublishTrack(_videoTrack, options);
        yield return publish;

        if (publish.IsError)
        {
            Debug.LogWarning("[ARVideoPublisher] H264 republish failed, trying VP8");
            options.VideoCodec = VideoCodec.Vp8;
            publish = room.LocalParticipant.PublishTrack(_videoTrack, options);
            yield return publish;
        }

        if (!publish.IsError)
        {
            _videoSource.Start();
            StartCoroutine(_videoSource.Update());
            _isPublishing = true;
            if (_publishMuted)
                ((ILocalTrack)_videoTrack).SetMute(true);
            Debug.Log($"[ARVideoPublisher] Track rebuilt: {bitrate / 1000}kbps/{fps}fps (tier={tier})");
        }
        else
        {
            _lastPublishError = "rebuild_publish_failed";
            Debug.LogError("[ARVideoPublisher] ERROR rebuild_publish_failed: Track rebuild failed completely (PublishTrackInstruction.IsError; no Error details in SDK)");
        }

        // Notify Brain: rebuilding complete (resume normal visual state tracking)
        yield return StartCoroutine(SendTrackRebuildingRpc(false));
        _isRebuilding = false;
    }

    private IEnumerator SendTrackRebuildingRpc(bool rebuilding)
    {
        var room = RoomManager.Instance?.Room;
        if (room == null) yield break;

        string brainId = BrainParticipantResolver.FindBrainParticipantId(room);
        if (string.IsNullOrEmpty(brainId)) yield break;

        string reason = rebuilding ? "track_rebuilding" : "ok";
        double ts = (DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalSeconds;
        string payload = $"{{\"reason\":\"{reason}\",\"ts\":{ts:F3}}}";

        // Mirror VideoStateReporter coroutine pattern — ResponseTimeout in ms
        var rpcCall = room.LocalParticipant.PerformRpc(new PerformRpcParams
        {
            DestinationIdentity = brainId,
            Method = "onVideoDegraded",
            Payload = payload,
            ResponseTimeout = 3000,
        });
        yield return rpcCall;

        if (rpcCall.IsError)
            Debug.LogWarning($"[ARVideoPublisher] onVideoDegraded({reason}) error: {rpcCall.Error?.Message}");
        else
            Debug.Log($"[ARVideoPublisher] onVideoDegraded(reason={reason}) sent → Brain");
    }

    // ── Cleanup ─────────────────────────────────────────────────────

    void OnDestroy()
    {
        StopPublishingLocal("destroy");

#if UNITY_AR_FOUNDATION
        if (_arCameraManager != null)
            _arCameraManager.frameReceived -= OnARFrameReceived;
#endif

        if (_webcamBlit != null) StopCoroutine(_webcamBlit);
        if (_webcam != null) { _webcam.Stop(); Destroy(_webcam); }

        _videoSource?.Stop();
        if (_rt != null) { _rt.Release(); Destroy(_rt); }

        var rm = RoomManager.Instance;
        if (rm != null)
        {
            rm.OnConnected -= OnRoomConnected;
            rm.OnDisconnected -= OnRoomDisconnected;
        }
    }

    private void OnRoomDisconnected()
    {
        StopPublishingLocal("room_disconnected");
    }

    private void StopPublishingLocal(string reason)
    {
        if (!_isPublishing && _videoSource == null && _videoTrack == null
            && _webcamBlit == null && _webcam == null && _rt == null)
            return;

        _isPublishing = false;
        _setupInProgress = false;
        _videoSource?.Stop();
        _videoSource = null;
        _videoTrack = null;

        if (_webcamBlit != null)
        {
            StopCoroutine(_webcamBlit);
            _webcamBlit = null;
        }
        if (_webcam != null)
        {
            _webcam.Stop();
            Destroy(_webcam);
            _webcam = null;
        }
        if (_rt != null)
        {
            _rt.Release();
            Destroy(_rt);
            _rt = null;
        }

        Debug.Log($"[ARVideoPublisher] Local video publish state cleared ({reason})");
    }
}
