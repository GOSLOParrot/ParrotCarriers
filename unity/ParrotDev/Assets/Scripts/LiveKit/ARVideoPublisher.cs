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
/// Attach to a GameObject in the scene. Requires RoomManager to be connected.
/// </summary>
public class ARVideoPublisher : MonoBehaviour
{
    [Header("Video Settings")]
    [SerializeField] private int width = 1280;
    [SerializeField] private int height = 720;
    [SerializeField] private int targetFps = 30;

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
        Debug.Log($"[ARVideoPublisher] Publishing {width}x{height}@{targetFps}fps");
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
    /// on publish). LiveKit Unity SDK supports SetMuted on the live track
    /// without re-publishing, which is the one transition we need for
    /// VIDEO_OFF (privacy / obstruction) in Sprint 2. True bitrate/fps
    /// changes require a full PublishTrack redo and land in Sprint 3.
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
