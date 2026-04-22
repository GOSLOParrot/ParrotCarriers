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
/// Publishes AR camera background frames to LiveKit as a video track.
/// Brain Agent subscribes via video_input=True → Gemini Live sees the camera feed.
///
/// AR mode (device): ARCameraBackground → CommandBuffer.Blit → RenderTexture → TextureVideoSource
/// Dev fallback (editor): WebCamTexture → RenderTexture → TextureVideoSource
///
/// Sprint 3 T-U5: supports dynamic track republishing (UnpublishTrack →
/// PublishTrack with new options) for VIDEO_FULL ↔ VIDEO_GEMINI_ONLY tier
/// transitions. During rebuild, sends "track_rebuilding" RPC to Brain so
/// PerceptionSupervisor does NOT count the gap as a degraded timer tick.
///
/// Attach to a GameObject in the scene. Requires RoomManager to be connected.
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
    [Tooltip("Use webcam in Editor when AR is unavailable")]
    [SerializeField] private bool useWebcamFallback = true;

    [Tooltip("Substring match (case-insensitive). Leave empty for auto (prefers first non-virtual device).")]
    [SerializeField] private string preferredDeviceName = "";

    [Tooltip("How many real frames to pre-blit to RenderTexture before publishing (avoids first-frame black).")]
    [SerializeField] private int webcamWarmupFrames = 3;

    private RenderTexture _rt;
    private TextureVideoSource _videoSource;
    private LocalVideoTrack _videoTrack;
    private bool _isPublishing;
    private bool _publishMuted;
    private bool _isRebuilding;

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

    // Dev fallback
    private WebCamTexture _webcam;
    private Coroutine _webcamBlit;

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
        if (rm.IsConnected) OnRoomConnected();
    }

    private void OnRoomConnected()
    {
        if (_isPublishing) return;
        StartCoroutine(SetupAndPublish());
    }

    private IEnumerator SetupAndPublish()
    {
        _rt = new RenderTexture(width, height, 0, RenderTextureFormat.ARGB32);
        _rt.Create();

        bool arAvailable = TrySetupAR();

        if (!arAvailable && useWebcamFallback)
        {
            Debug.Log("[ARVideoPublisher] AR not available, using webcam fallback");
            yield return SetupWebcamFallback();
        }
        else if (!arAvailable)
        {
            Debug.LogWarning("[ARVideoPublisher] No video source available");
            yield break;
        }

        var rm = RoomManager.Instance;
        if (rm == null || !rm.IsConnected)
        {
            Debug.LogWarning("[ARVideoPublisher] Room no longer connected after setup, aborting publish");
            yield break;
        }
        var room = rm.Room;
        if (room == null) yield break;

        _videoSource = new TextureVideoSource(_rt);
        _videoTrack = LocalVideoTrack.CreateVideoTrack("ar-camera", _videoSource, room);

        var options = new TrackPublishOptions
        {
            VideoCodec = VideoCodec.H264,
            VideoEncoding = new VideoEncoding
            {
                MaxBitrate = 1_500_000,
                MaxFramerate = targetFps,
            },
            Source = TrackSource.SourceCamera,
        };

        var publish = room.LocalParticipant.PublishTrack(_videoTrack, options);
        yield return publish;

        if (publish.IsError)
        {
            Debug.LogError("[ARVideoPublisher] Failed to publish video (H264), falling back to VP8");

            options.VideoCodec = VideoCodec.Vp8;
            publish = room.LocalParticipant.PublishTrack(_videoTrack, options);
            yield return publish;

            if (publish.IsError)
            {
                Debug.LogError("[ARVideoPublisher] VP8 fallback also failed, aborting");
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

        Debug.Log($"[ARVideoPublisher] Publishing {width}x{height}@{targetFps}fps (muted={_publishMuted})");
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
    }
#endif

    // ── Webcam dev fallback ─────────────────────────────────────────

    private IEnumerator SetupWebcamFallback()
    {
        var devices = WebCamTexture.devices;
        if (devices.Length == 0)
        {
            Debug.LogWarning("[ARVideoPublisher] No webcam found");
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
            Debug.LogWarning("[ARVideoPublisher] Webcam failed to start");
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
                blitted++;
            }
            warmupTimeout -= Time.deltaTime;
            yield return null;
        }
        Debug.Log($"[ARVideoPublisher] Webcam warmup complete ({blitted}/{webcamWarmupFrames} frames pre-blitted)");

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
                Graphics.Blit(_webcam, _rt);
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

        // Unpublish existing track
        if (_videoTrack != null)
        {
            try
            {
                _videoSource?.Stop();
                var unpub = room.LocalParticipant.UnpublishTrack(_videoTrack);
                yield return unpub;
                _videoTrack = null;
                _isPublishing = false;
                Debug.Log("[ARVideoPublisher] Track unpublished for rebuild");
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[ARVideoPublisher] UnpublishTrack failed: {e.Message}");
            }
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
                MaxBitrate = bitrate,
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
            Debug.LogError("[ARVideoPublisher] Track rebuild failed completely");
        }

        // Notify Brain: rebuilding complete (resume normal visual state tracking)
        yield return StartCoroutine(SendTrackRebuildingRpc(false));
        _isRebuilding = false;
    }

    private IEnumerator SendTrackRebuildingRpc(bool rebuilding)
    {
        var room = RoomManager.Instance?.Room;
        if (room == null) yield break;

        // Match VideoStateReporter pattern: agent-* prefix
        string brainId = null;
        foreach (var p in room.RemoteParticipants.Values)
        {
            if (!string.IsNullOrEmpty(p.Identity) && p.Identity.StartsWith("agent-"))
            { brainId = p.Identity; break; }
        }
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
        _isPublishing = false;

#if UNITY_AR_FOUNDATION
        if (_arCameraManager != null)
            _arCameraManager.frameReceived -= OnARFrameReceived;
#endif

        if (_webcamBlit != null) StopCoroutine(_webcamBlit);
        if (_webcam != null) { _webcam.Stop(); Destroy(_webcam); }

        _videoSource?.Stop();
        if (_rt != null) { _rt.Release(); Destroy(_rt); }

        var rm = RoomManager.Instance;
        if (rm != null) rm.OnConnected -= OnRoomConnected;
    }
}
