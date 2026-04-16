using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Rendering;
using LiveKit;

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

    private RenderTexture _rt;
    private TextureVideoSource _videoSource;
    private LocalVideoTrack _videoTrack;
    private bool _isPublishing;

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

        var room = RoomManager.Instance?.Room;
        if (room == null) yield break;

        _videoSource = new TextureVideoSource(_rt);
        _videoTrack = LocalVideoTrack.CreateVideoTrack("ar-camera", _videoSource, room);

        var options = new TrackPublishOptions
        {
            VideoCodec = VideoCodec.H264,
            VideoEncoding = new VideoEncoding
            {
                MaxBitrate = 1_500_000,
                MaxFramerate = (uint)targetFps,
            },
            Source = TrackSource.SourceCamera,
        };

        var publish = room.LocalParticipant.PublishTrack(_videoTrack, options);
        yield return publish;

        if (publish.IsError)
        {
            Debug.LogError($"[ARVideoPublisher] Failed to publish video: {publish.Error}");

            // Fallback to VP8 if H264 fails
            options.VideoCodec = VideoCodec.Vp8;
            publish = room.LocalParticipant.PublishTrack(_videoTrack, options);
            yield return publish;

            if (publish.IsError)
            {
                Debug.LogError($"[ARVideoPublisher] VP8 fallback also failed: {publish.Error}");
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
        if (WebCamTexture.devices.Length == 0)
        {
            Debug.LogWarning("[ARVideoPublisher] No webcam found");
            yield break;
        }

        var deviceName = WebCamTexture.devices[0].name;
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

        Debug.Log($"[ARVideoPublisher] Webcam started: {deviceName} ({_webcam.width}x{_webcam.height})");
        _webcamBlit = StartCoroutine(BlitWebcamLoop());
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
