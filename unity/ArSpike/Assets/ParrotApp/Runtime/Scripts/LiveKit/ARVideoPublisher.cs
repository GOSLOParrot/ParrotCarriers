using System;
using System.Collections;
using LiveKit;
using LiveKit.Proto;
using ParrotApp.Config;
using ParrotApp.Health;
using ParrotApp.Lifecycle;
using UnityEngine;

#if UNITY_AR_FOUNDATION
using UnityEngine.XR.ARFoundation;
#endif

namespace ParrotApp.LiveKit
{
    /// <summary>
    /// 把摄像头像素发布为 LiveKit 视频轨。<br/>
    /// 从 ParrotDev 搬迁（Sprint4 Phase 3 / L3 Group 3）。差异：
    /// <list type="bullet">
    /// <item>命名空间收口为 <c>ParrotApp.LiveKit</c>。</item>
    /// <item>三个硬编阈值改读 <see cref="ParrotLifecycleConfig"/>：
    ///   <c>T_FIRST_FRAME_TIMEOUT</c> / <c>STALE_FRAME_THRESHOLD_LOW_TIER</c> /
    ///   <c>STALE_FRAME_THRESHOLD_HIGH_TIER</c> / <c>T_TIER_COOLDOWN</c>。</item>
    /// <item>监听 <see cref="AppLifecycleManager.OnStateChanged"/>：进
    ///   <c>ShortBackground</c> / <c>LongBackground</c> 暂停 Blit（<b>不</b> unpublish track）+
    ///   灌 <c>video_lifecycle_reason="lifecycle_background"</c>；回 Running/Connected
    ///   等首帧再恢复（IMPL_REF.md §5.1）。</item>
    /// <item>实现 <see cref="IGracefulShutdownParticipant"/>，让 chokepoint 步骤 1 等本组件完成 unpublish。</item>
    /// <item>本类是 <c>video_publish_attempted</c> / <c>video_published</c> /
    ///   <c>video_first_frame</c> / <c>video_fresh_frame</c> / <c>video_tier</c> /
    ///   <c>video_lifecycle_reason</c> 的<b>唯一</b> producer（IMPL_REF.md §4.2）。
    ///   <c>VideoStateReporter</c> 走 Group 3 双轨灰，只补充 reason 细分，不抢字段。</item>
    /// </list>
    ///
    /// <b>不允许误读</b>（与锚点一致）：
    /// <list type="bullet">
    /// <item>本类<b>不</b>消费实时帧，<b>不</b>写 DSG L2-B；只产视频轨。</item>
    /// <item>VideoTier 切换是 Intent，不是 Reflex；切换走 <see cref="ApplyVideoTier"/> +
    ///   cool-down，<b>不</b>用任何高频回调。</item>
    /// </list>
    /// </summary>
    public class ARVideoPublisher : MonoBehaviour, IGracefulShutdownParticipant
    {
        public struct TierApplyResult
        {
            public bool Ok;
            public string Reason;
            public string Detail;

            public TierApplyResult(bool ok, string reason, string detail = "")
            {
                Ok = ok;
                Reason = reason;
                Detail = detail;
            }
        }

        [Header("Video Settings")]
        [SerializeField] private int width = 1280;
        [SerializeField] private int height = 720;
        [SerializeField] private int targetFps = 30;

        [Header("Tier Encoding Presets")]
        [Tooltip("Bitrate for VIDEO_FULL (bps)")]
        [SerializeField] private int fullBitrate = 1_000_000;
        [SerializeField] private int fullFps = 30;
        [Tooltip("Bitrate for VIDEO_GEMINI_ONLY (bps)")]
        [SerializeField] private int geminiOnlyBitrate = 300_000;
        [SerializeField] private int geminiOnlyFps = 15;

        [Header("AR Components (assign if AR Foundation available)")]
        [SerializeField] private Camera arCamera;
        [SerializeField] private FormalArRuntimeBootstrap arRuntimeBootstrap;

        [Header("Dev Fallback")]
        [Tooltip("AR 路径不可用时回落 WebCamTexture（spike / Editor 用，正式 AR build 走真 ARCore）。")]
        [SerializeField] private bool useWebcamFallback = false;

        [Tooltip("子串匹配（不区分大小写）；空时优先选第一个非虚拟设备。")]
        [SerializeField] private string preferredDeviceName = "";

        [Tooltip("publish 前预 Blit 多少帧到 RenderTexture，避免首帧黑。")]
        [SerializeField] private int webcamWarmupFrames = 3;

        [Header("Lifecycle Integration")]
        [Tooltip("可选；为空时 FindObjectOfType。监听 OnStateChanged 切 Blit 暂停。")]
        [SerializeField] private AppLifecycleManager lifecycleManager;

        private ParrotLifecycleConfig Config =>
            lifecycleManager != null ? lifecycleManager.Config : null;

        private ConnectionHealthAggregator HealthAggregator =>
            lifecycleManager != null ? lifecycleManager.HealthAggregator : null;

        private RenderTexture _rt;
        private TextureVideoSource _videoSource;
        private LocalVideoTrack _videoTrack;
        private bool _isPublishing;
        private bool _publishMuted;
        private bool _isRebuilding;
        private bool _setupInProgress;
        private int _videoPublishGeneration;

        // lifecycle 暂停 Blit 标志：true 时 OnARFrameReceived / BlitWebcamLoop 不写新帧
        private bool _blitPaused;

        private int _producedFrameCount;
        private float _lastProducedFrameTime = -1f;
        private string _videoSourceLabel = "none";
        private string _lastPublishError = "";
        private bool _firstFrameHealthReported;
        private bool _lastFreshState;
        private float _nextFreshnessCheckAt;

        public enum VideoTierLocal { Unknown, Off, GeminiOnly, Full, Burst }
        private VideoTierLocal _currentTier = VideoTierLocal.GeminiOnly;

        public event Action<bool> OnPublishMutedChanged;

        public bool IsPublishing => _isPublishing;
        public bool IsPublishMuted => _publishMuted;
        public int ProducedFrameCount => _producedFrameCount;
        public string VideoSourceLabel => _videoSourceLabel;
        public string LastPublishError => _lastPublishError;
        public float LastFrameAgeSeconds =>
            _lastProducedFrameTime < 0f ? -1f : Time.realtimeSinceStartup - _lastProducedFrameTime;

        public float StaleFrameThresholdSeconds => CurrentStaleThreshold();

        public bool HasFreshFrame =>
            _producedFrameCount > 0
            && LastFrameAgeSeconds >= 0f
            && LastFrameAgeSeconds <= CurrentStaleThreshold();

        // Dev fallback
        private WebCamTexture _webcam;
        private Coroutine _webcamBlit;
        private bool _webcamReady;

#if UNITY_AR_FOUNDATION
        private ARCameraManager _arCameraManager;
        private ARCameraBackground _arCameraBackground;
#endif

        // ─── IGracefulShutdownParticipant ────────────────────────────────

        public int ShutdownOrder => 10; // 视频先 (10) / 音频后 (20)

        public IEnumerator UnpublishAndStop(string reason)
        {
            if (_videoTrack != null)
            {
                var room = RoomManager.Instance?.Room;
                if (room != null)
                {
                    if (LifecycleShutdownService.IsSynchronousQuitDrain)
                    {
                        Debug.Log($"[ARVideoPublisher] sync quit drain skips waiting for UnpublishTrack (reason={reason})");
                    }
                    else
                    {
                        Debug.Log($"[ARVideoPublisher] chokepoint UnpublishTrack (reason={reason})");
                        yield return room.LocalParticipant.UnpublishTrack(_videoTrack, stopOnUnpublish: true);
                    }
                }
            }
            StopPublishingLocal($"chokepoint:{reason}");
        }

        // ─── lifecycle ────────────────────────────────────────────────────

        void Start()
        {
            if (lifecycleManager == null)
                lifecycleManager = FindObjectOfType<AppLifecycleManager>();
            if (lifecycleManager != null)
                lifecycleManager.OnStateChanged += HandleLifecycleChanged;

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

        void Update()
        {
            // 周期性 fresh / stale 翻转检测；config 可能没挂时退化为 1 Hz
            if (!_isPublishing) return;
            if (Time.unscaledTime < _nextFreshnessCheckAt) return;
            _nextFreshnessCheckAt = Time.unscaledTime + 1f;

            if (HealthAggregator == null) return;
            bool fresh = HasFreshFrame && !_publishMuted && !_blitPaused;
            if (fresh != _lastFreshState)
            {
                _lastFreshState = fresh;
                HealthAggregator.ReportVideoFreshFrame(fresh, UnixSeconds());
            }
        }

        private void HandleLifecycleChanged(AppLifecycleState prev, AppLifecycleState next)
        {
            // 进短/长后台：暂停 Blit；不动 track（IMPL_REF.md §5.1）
            if (next == AppLifecycleState.ShortBackground
                || next == AppLifecycleState.LongBackground)
            {
                if (!_blitPaused)
                {
                    _blitPaused = true;
                    HealthAggregator?.ReportVideoLifecycleReason("lifecycle_background", UnixSeconds());
                    Debug.Log($"[ARVideoPublisher] Blit paused (lifecycle={next})");
                }
            }
            // 回 Connected/Running：清暂停 + 等下一次帧再恢复 fresh 状态
            else if (next == AppLifecycleState.Connected || next == AppLifecycleState.Running)
            {
                if (_blitPaused)
                {
                    _blitPaused = false;
                    HealthAggregator?.ReportVideoLifecycleReason("", UnixSeconds());
                    Debug.Log($"[ARVideoPublisher] Blit resumed (lifecycle={next})");
                }
            }
        }

        private void OnRoomConnected()
        {
            if (_isPublishing || _setupInProgress) return;
            StartCoroutine(SetupAndPublish());
        }

        private IEnumerator SetupAndPublish()
        {
            _setupInProgress = true;
            int generation = _videoPublishGeneration;
            HealthAggregator?.ReportVideoPublishAttempt(UnixSeconds());
            HealthAggregator?.ReportVideoTier(TierToWire(_currentTier), UnixSeconds());

            _rt = new RenderTexture(width, height, 0, RenderTextureFormat.ARGB32);
            _rt.Create();
            _webcamReady = false;
            _producedFrameCount = 0;
            _lastProducedFrameTime = -1f;
            _videoSourceLabel = "none";
            _lastPublishError = "";
            _firstFrameHealthReported = false;
            _lastFreshState = false;

            yield return EnsureArRuntimeForPublish();
            if (CancelSetupIfNeeded(generation))
                yield break;
            bool arAvailable = TrySetupAR();
            bool useWebcam = useWebcamFallback;

#if UNITY_EDITOR
            if (!arAvailable && !useWebcam)
            {
                Debug.LogWarning(
                    "[ARVideoPublisher] Editor: AR camera path unavailable — forcing webcam fallback.");
                useWebcam = true;
            }
#elif UNITY_STANDALONE
            if (!arAvailable && !useWebcam)
            {
                Debug.LogWarning(
                    "[ARVideoPublisher] Standalone: AR path unavailable — forcing webcam fallback.");
                useWebcam = true;
            }
#endif

            float firstFrameTimeout = Config != null ? Config.T_FIRST_FRAME_TIMEOUT : 8f;

            if (!arAvailable && useWebcam)
            {
                Debug.Log("[ARVideoPublisher] AR not available, using webcam fallback");
                yield return SetupWebcamFallback();
                if (CancelSetupIfNeeded(generation))
                    yield break;
                if (!_webcamReady)
                {
                    _lastPublishError = "webcam_fallback_no_frames";
                    Debug.LogError("[ARVideoPublisher] ERROR webcam_fallback_no_frames");
                    HealthAggregator?.ReportVideoPublished(false, UnixSeconds());
                    _setupInProgress = false;
                    yield break;
                }
            }
            else if (!arAvailable)
            {
                _lastPublishError = "no_video_source";
                Debug.LogWarning("[ARVideoPublisher] ERROR no_video_source");
                HealthAggregator?.ReportVideoPublished(false, UnixSeconds());
                _setupInProgress = false;
                yield break;
            }
            else
            {
                yield return WaitForFirstFrame("AR", firstFrameTimeout);
                if (CancelSetupIfNeeded(generation))
                    yield break;
                if (_producedFrameCount == 0)
                {
                    _lastPublishError = "ar_path_no_frames";
                    Debug.LogError("[ARVideoPublisher] ERROR ar_path_no_frames");
                    HealthAggregator?.ReportVideoLifecycleReason("first_frame_timeout", UnixSeconds());
                    HealthAggregator?.ReportVideoPublished(false, UnixSeconds());
                    _setupInProgress = false;
                    yield break;
                }
            }

            var rm = RoomManager.Instance;
            if (rm == null || !rm.IsConnected)
            {
                _lastPublishError = "room_disconnected_before_publish";
                HealthAggregator?.ReportVideoPublished(false, UnixSeconds());
                _setupInProgress = false;
                yield break;
            }
            var room = rm.Room;
            if (room == null)
            {
                _lastPublishError = "room_missing_before_publish";
                HealthAggregator?.ReportVideoPublished(false, UnixSeconds());
                _setupInProgress = false;
                yield break;
            }

            _videoSource = new TextureVideoSource(_rt);
            _videoTrack = LocalVideoTrack.CreateVideoTrack("ar-camera", _videoSource, room);

            // 默认按 _currentTier（Brain 默认 VIDEO_GEMINI_ONLY）发布；
            // 若 Brain 在我们 publish 完成前已发 setVideoTier，VideoTierReceiver 会 RebuildTrack。
            int initBitrate;
            int initFps;
            switch (_currentTier)
            {
                case VideoTierLocal.Full:
                    initBitrate = fullBitrate;
                    initFps = fullFps;
                    break;
                case VideoTierLocal.Burst:
                    initBitrate = fullBitrate * 2;
                    initFps = fullFps;
                    break;
                default:
                    initBitrate = geminiOnlyBitrate;
                    initFps = geminiOnlyFps;
                    break;
            }
            targetFps = initFps;

            var options = new TrackPublishOptions
            {
                VideoCodec = VideoCodec.H264,
                VideoEncoding = new VideoEncoding
                {
                    MaxBitrate = (ulong)initBitrate,
                    MaxFramerate = initFps,
                },
                Source = TrackSource.SourceCamera,
            };
            Debug.Log($"[ARVideoPublisher] Initial publish tier={_currentTier} bitrate={initBitrate} fps={initFps}");

            var publish = room.LocalParticipant.PublishTrack(_videoTrack, options);
            yield return publish;
            if (CancelSetupIfNeeded(generation))
                yield break;

            if (publish.IsError)
            {
                Debug.LogError("[ARVideoPublisher] ERROR publish_h264_failed; trying VP8");
                options.VideoCodec = VideoCodec.Vp8;
                publish = room.LocalParticipant.PublishTrack(_videoTrack, options);
                yield return publish;
                if (CancelSetupIfNeeded(generation))
                    yield break;

                if (publish.IsError)
                {
                    _lastPublishError = "publish_vp8_failed";
                    HealthAggregator?.ReportVideoPublished(false, UnixSeconds());
                    _setupInProgress = false;
                    yield break;
                }
            }

            _videoSource.Start();
            StartCoroutine(_videoSource.Update());
            _isPublishing = true;
            int postPublishFrameBaseline = _producedFrameCount;
            yield return WaitForFramesAfterPublish(postPublishFrameBaseline, 1, firstFrameTimeout, generation);
            if (CancelSetupIfNeeded(generation))
                yield break;
            if (_producedFrameCount <= postPublishFrameBaseline)
            {
                _lastPublishError = "video_publish_no_post_publish_frame";
                HealthAggregator?.ReportVideoLifecycleReason("first_frame_timeout", UnixSeconds());
                HealthAggregator?.ReportVideoPublished(false, UnixSeconds());
                Debug.LogWarning("[ARVideoPublisher] published track but no fresh post-publish frame arrived");
            }
            else
            {
                HealthAggregator?.ReportVideoLifecycleReason("", UnixSeconds());
                HealthAggregator?.ReportVideoPublished(true, UnixSeconds());
            }

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

        private IEnumerator WaitForFramesAfterPublish(
            int baselineFrameCount,
            int requiredFrames,
            float timeoutSeconds,
            int generation)
        {
            float remaining = Mathf.Max(0.1f, timeoutSeconds);
            int targetFrameCount = baselineFrameCount + Mathf.Max(1, requiredFrames);
            while (!IsVideoGenerationCancelled(generation)
                   && _producedFrameCount < targetFrameCount
                   && remaining > 0f)
            {
                remaining -= Time.deltaTime;
                yield return null;
            }
        }

        private void RecordProducedFrame(string sourceLabel)
        {
            _videoSourceLabel = sourceLabel;
            _producedFrameCount++;
            _lastProducedFrameTime = Time.realtimeSinceStartup;
            if (!_firstFrameHealthReported && HealthAggregator != null)
            {
                _firstFrameHealthReported = true;
                HealthAggregator.ReportVideoFirstFrame(UnixSeconds());
            }
        }

        // ─── AR Foundation 路径 ───────────────────────────────────────────

        private bool TrySetupAR()
        {
#if UNITY_AR_FOUNDATION
            if (arCamera == null) arCamera = Camera.main;
            if (arCamera == null) return false;

            _arCameraManager = arCamera.GetComponent<ARCameraManager>();
            _arCameraBackground = arCamera.GetComponent<ARCameraBackground>();

            if (_arCameraManager == null || _arCameraBackground == null) return false;

            _arCameraManager.frameReceived -= OnARFrameReceived;
            _arCameraManager.frameReceived += OnARFrameReceived;
            Debug.Log("[ARVideoPublisher] AR Foundation camera attached");
            return true;
#else
            return false;
#endif
        }

        private IEnumerator EnsureArRuntimeForPublish()
        {
            if (_currentTier == VideoTierLocal.Off)
                yield break;
            if (Application.isEditor || !Application.isMobilePlatform)
                yield break;

            if (arRuntimeBootstrap == null)
                arRuntimeBootstrap = FindObjectOfType<FormalArRuntimeBootstrap>();
            if (arRuntimeBootstrap == null)
                yield break;

            yield return arRuntimeBootstrap.EnsureArRuntimeReady();
            if (arRuntimeBootstrap.XrLifecycleFailed)
            {
                _lastPublishError = string.IsNullOrWhiteSpace(arRuntimeBootstrap.LastStatus)
                    ? "ar_runtime_prepare_failed"
                    : "ar_runtime_prepare_failed:" + arRuntimeBootstrap.LastStatus;
                Debug.LogWarning("[ARVideoPublisher] " + _lastPublishError);
            }
        }

#if UNITY_AR_FOUNDATION
        private void OnARFrameReceived(ARCameraFrameEventArgs args)
        {
            if (_blitPaused) return; // lifecycle 后台暂停期间不写新帧（IMPL_REF.md §5.1）
            if (_rt == null || _arCameraBackground == null) return;

            var mat = _arCameraBackground.material;
            if (mat == null) return;

            Graphics.Blit(null, _rt, mat);
            RecordProducedFrame("AR");
        }
#endif

        // ─── WebCam dev fallback ──────────────────────────────────────────

        private IEnumerator SetupWebcamFallback()
        {
            var devices = WebCamTexture.devices;
            if (devices.Length == 0)
            {
                Debug.LogWarning("[ARVideoPublisher] ERROR no_webcam_devices");
                yield break;
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
                Debug.LogWarning("[ARVideoPublisher] ERROR webcam_failed_to_start");
                yield break;
            }

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
                Debug.LogWarning("[ARVideoPublisher] ERROR webcam_no_warmup_frames");
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
                    if (d.name.IndexOf(preferredDeviceName, StringComparison.OrdinalIgnoreCase) >= 0)
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
                if (!_blitPaused && _webcam.didUpdateThisFrame)
                {
                    Graphics.Blit(_webcam, _rt);
                    RecordProducedFrame("WebCam");
                }
                yield return null;
            }
        }

        // ─── 运行时静音控制 ────────────────────────────────────────────────

        public void SetPublishMuted(bool muted)
        {
            TrySetPublishMuted(muted, out _);
        }

        private bool TrySetPublishMuted(bool muted, out string error)
        {
            error = "";
            if (_publishMuted == muted) return true;

            if (_videoTrack != null)
            {
                try
                {
                    ((ILocalTrack)_videoTrack).SetMute(muted);
                }
                catch (Exception e)
                {
                    error = e.Message;
                    Debug.LogWarning($"[ARVideoPublisher] SetPublishMuted({muted}) failed: {e.Message}");
                    return false;
                }
            }

            _publishMuted = muted;
            Debug.Log($"[ARVideoPublisher] publish muted → {muted}");
            OnPublishMutedChanged?.Invoke(muted);
            return true;
        }

        // ─── 动态 tier 切换 ───────────────────────────────────────────────

        public void ApplyVideoTier(VideoTierLocal newTier)
        {
            ApplyVideoTier(newTier, null);
        }

        public void ApplyVideoTier(VideoTierLocal newTier, Action<TierApplyResult> onComplete)
        {
            if (_currentTier == newTier)
            {
                onComplete?.Invoke(new TierApplyResult(true, "unchanged"));
                return;
            }
            var prev = _currentTier;

            Debug.Log($"[ARVideoPublisher] Tier change: {prev} → {newTier}");

            if (newTier == VideoTierLocal.Off)
            {
                if (TrySetPublishMuted(true, out var muteError))
                {
                    _currentTier = newTier;
                    HealthAggregator?.ReportVideoTier(TierToWire(newTier), UnixSeconds());
                    onComplete?.Invoke(new TierApplyResult(true, "applied"));
                }
                else
                {
                    onComplete?.Invoke(new TierApplyResult(false, "mute_failed", muteError));
                }
                return;
            }

            if (prev == VideoTierLocal.Off)
            {
                if (!TrySetPublishMuted(false, out var unmuteError))
                {
                    onComplete?.Invoke(new TierApplyResult(false, "unmute_failed", unmuteError));
                    return;
                }
            }

            if (!_isPublishing)
            {
                _currentTier = newTier;
                HealthAggregator?.ReportVideoTier(TierToWire(newTier), UnixSeconds());
                onComplete?.Invoke(new TierApplyResult(true, "pending_publish"));
                return;
            }

            if (_isRebuilding)
            {
                onComplete?.Invoke(new TierApplyResult(false, "rebuild_in_progress"));
                return;
            }

            StartCoroutine(RebuildTrack(newTier, result =>
            {
                if (result.Ok)
                {
                    _currentTier = newTier;
                    HealthAggregator?.ReportVideoTier(TierToWire(newTier), UnixSeconds());
                }
                onComplete?.Invoke(result);
            }));
        }

        private IEnumerator RebuildTrack(VideoTierLocal tier, Action<TierApplyResult> onComplete = null)
        {
            _isRebuilding = true;
            int generation = _videoPublishGeneration;
            HealthAggregator?.ReportVideoLifecycleReason("republishing", UnixSeconds());

            yield return StartCoroutine(SendTrackRebuildingRpc(true));
            if (CancelRebuildIfNeeded(generation, onComplete))
            {
                yield break;
            }

            var rm = RoomManager.Instance;
            if (rm == null || !rm.IsConnected || rm.Room == null)
            {
                _isRebuilding = false;
                HealthAggregator?.ReportVideoLifecycleReason("", UnixSeconds());
                onComplete?.Invoke(new TierApplyResult(false, "room_not_connected"));
                yield break;
            }
            var room = rm.Room;

            if (_videoTrack != null)
            {
                _videoSource?.Stop();
                yield return room.LocalParticipant.UnpublishTrack(_videoTrack, stopOnUnpublish: true);
                Debug.Log("[ARVideoPublisher] Track unpublished for rebuild");
                _videoTrack = null;
                _isPublishing = false;
                HealthAggregator?.ReportVideoPublished(false, UnixSeconds());
            }

            // cool-down 必须 ≥ 3s（IMPL_REF.md §6 / livekit/livekit #854 abandoned publish）
            float coolDown = Config != null ? Config.T_TIER_COOLDOWN : 3f;
            float waited = 0f;
            while (waited < coolDown)
            {
                yield return null;
                if (CancelRebuildIfNeeded(generation, onComplete))
                {
                    yield break;
                }
                waited += Time.unscaledDeltaTime;
            }

            (int bitrate, int fps) = tier switch
            {
                VideoTierLocal.Full => (fullBitrate, fullFps),
                VideoTierLocal.Burst => (fullBitrate * 2, fullFps),
                _ => (geminiOnlyBitrate, geminiOnlyFps),
            };

            _videoSource = new TextureVideoSource(_rt);
            _videoTrack = LocalVideoTrack.CreateVideoTrack("ar-camera", _videoSource, room);

            var options = new TrackPublishOptions
            {
                VideoCodec = VideoCodec.H264,
                VideoEncoding = new VideoEncoding
                {
                    MaxBitrate = (ulong)bitrate,
                    MaxFramerate = fps,
                },
                Source = TrackSource.SourceCamera,
            };

            var publish = room.LocalParticipant.PublishTrack(_videoTrack, options);
            yield return publish;
            if (CancelRebuildIfNeeded(generation, onComplete))
            {
                yield break;
            }

            if (publish.IsError)
            {
                Debug.LogWarning("[ARVideoPublisher] H264 republish failed, trying VP8");
                options.VideoCodec = VideoCodec.Vp8;
                publish = room.LocalParticipant.PublishTrack(_videoTrack, options);
                yield return publish;
                if (CancelRebuildIfNeeded(generation, onComplete))
                {
                    yield break;
                }
            }

            if (!publish.IsError)
            {
                _videoSource.Start();
                StartCoroutine(_videoSource.Update());
                _isPublishing = true;
                int postPublishFrameBaseline = _producedFrameCount;
                float firstFrameTimeout = Config != null ? Config.T_FIRST_FRAME_TIMEOUT : 8f;
                yield return WaitForFramesAfterPublish(postPublishFrameBaseline, 1, firstFrameTimeout, generation);
                if (CancelRebuildIfNeeded(generation, onComplete))
                {
                    yield break;
                }
                if (_producedFrameCount <= postPublishFrameBaseline)
                {
                    _lastPublishError = "rebuild_no_post_publish_frame";
                    HealthAggregator?.ReportVideoLifecycleReason("first_frame_timeout", UnixSeconds());
                    HealthAggregator?.ReportVideoPublished(false, UnixSeconds());
                    Debug.LogWarning("[ARVideoPublisher] rebuilt track but no fresh post-publish frame arrived");
                    onComplete?.Invoke(new TierApplyResult(false, "rebuild_no_post_publish_frame"));
                }
                else
                {
                    HealthAggregator?.ReportVideoLifecycleReason("", UnixSeconds());
                    HealthAggregator?.ReportVideoPublished(true, UnixSeconds());
                    if (_publishMuted)
                        ((ILocalTrack)_videoTrack).SetMute(true);
                    Debug.Log($"[ARVideoPublisher] Track rebuilt: {bitrate / 1000}kbps/{fps}fps (tier={tier})");
                    onComplete?.Invoke(new TierApplyResult(true, "applied"));
                }
            }
            else
            {
                _lastPublishError = "rebuild_publish_failed";
                Debug.LogError("[ARVideoPublisher] ERROR rebuild_publish_failed");
                HealthAggregator?.ReportVideoPublished(false, UnixSeconds());
                onComplete?.Invoke(new TierApplyResult(false, "rebuild_publish_failed"));
            }

            HealthAggregator?.ReportVideoLifecycleReason("", UnixSeconds());
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
            double ts = UnixSeconds();
            string payload = $"{{\"reason\":\"{reason}\",\"ts\":{ts:F3}}}";

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
        }

        // ─── cleanup ──────────────────────────────────────────────────────

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

            if (lifecycleManager != null)
                lifecycleManager.OnStateChanged -= HandleLifecycleChanged;
        }

        private void OnRoomDisconnected()
        {
            StopPublishingLocal("room_disconnected");
        }

        private void StopPublishingLocal(string reason)
        {
            _videoPublishGeneration++;
            _isRebuilding = false;
            if (!_isPublishing && _videoSource == null && _videoTrack == null
                && _webcamBlit == null && _webcam == null && _rt == null)
                return;

            _isPublishing = false;
            _setupInProgress = false;
            _videoSource?.Stop();
            _videoSource = null;
            _videoTrack = null;
            HealthAggregator?.ReportVideoPublished(false, UnixSeconds());

            if (_webcamBlit != null) { StopCoroutine(_webcamBlit); _webcamBlit = null; }
            if (_webcam != null) { _webcam.Stop(); Destroy(_webcam); _webcam = null; }
            if (_rt != null) { _rt.Release(); Destroy(_rt); _rt = null; }

            Debug.Log($"[ARVideoPublisher] Local video publish state cleared ({reason})");
        }

        // ─── helpers ──────────────────────────────────────────────────────

        private bool IsVideoGenerationCancelled(int generation)
        {
            return generation != _videoPublishGeneration
                   || RoomManager.Instance?.IsConnected != true;
        }

        private bool CancelSetupIfNeeded(int generation)
        {
            if (!IsVideoGenerationCancelled(generation))
                return false;
            _setupInProgress = false;
            _isPublishing = false;
            _videoSource?.Stop();
            _videoSource = null;
            _videoTrack = null;
            _lastPublishError = "video_setup_cancelled";
            HealthAggregator?.ReportVideoPublished(false, UnixSeconds());
            return true;
        }

        private bool CancelRebuildIfNeeded(int generation, Action<TierApplyResult> onComplete)
        {
            if (!IsVideoGenerationCancelled(generation))
                return false;
            _isRebuilding = false;
            _isPublishing = false;
            _videoSource?.Stop();
            _videoSource = null;
            _videoTrack = null;
            HealthAggregator?.ReportVideoLifecycleReason("", UnixSeconds());
            HealthAggregator?.ReportVideoPublished(false, UnixSeconds());
            onComplete?.Invoke(new TierApplyResult(false, "rebuild_cancelled"));
            return true;
        }

        private float CurrentStaleThreshold()
        {
            // FULL / Burst 走严格阈值；GeminiOnly / Off / Unknown 走宽松阈值
            if (Config == null) return 3f;
            switch (_currentTier)
            {
                case VideoTierLocal.Full:
                case VideoTierLocal.Burst:
                    return Config.STALE_FRAME_THRESHOLD_HIGH_TIER;
                default:
                    return Config.STALE_FRAME_THRESHOLD_LOW_TIER;
            }
        }

        private static string TierToWire(VideoTierLocal tier)
        {
            switch (tier)
            {
                case VideoTierLocal.Off: return "VIDEO_OFF";
                case VideoTierLocal.GeminiOnly: return "VIDEO_GEMINI_ONLY";
                case VideoTierLocal.Full: return "VIDEO_FULL";
                case VideoTierLocal.Burst: return "VIDEO_BURST";
                default: return "";
            }
        }

        private static double UnixSeconds()
            => (DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalSeconds;
    }
}
