using System;
using System.Collections;
using LiveKit;
using LiveKit.Proto;
using ParrotApp.Health;
using ParrotApp.Lifecycle;
using UnityEngine;

namespace ParrotApp.LiveKit
{
    /// <summary>
    /// 把本机麦克风编码为 LiveKit 本地音频轨。<br/>
    /// 从 ParrotDev 搬迁（Sprint4 Phase 3 / L3 Group 3），并在 Phase 3 后段补上
    /// 蓝牙路由 + 采样率自适应（详见类内 §"Bluetooth audio compatibility"）。
    /// <list type="bullet">
    /// <item>命名空间收口为 <c>ParrotApp.LiveKit</c>。</item>
    /// <item>实现 <see cref="IGracefulShutdownParticipant"/>，让
    ///   <c>LifecycleShutdownService</c> 在 chokepoint 步骤 1 等本组件 unpublish。</item>
    /// <item><see cref="ConnectionHealthAggregator"/> 灌入：本类是
    ///   <c>audio_publish_attempted</c> / <c>audio_published</c> / <c>audio_last_error</c>
    ///   的<b>唯一</b> producer（IMPL_REF.md §4.2）。蓝牙补丁不引入第二 producer。</item>
    /// </list>
    ///
    /// <b>Bluetooth audio compatibility (Sprint4 Phase 3 后段)</b>：
    /// <list type="number">
    /// <item>采样率不再固定 48k baseline；从 <see cref="AudioRouteDetector"/> 读
    ///   <see cref="AudioRoutePolicy.PreferredSampleRate"/>（speaker/wired 48k；
    ///   bluetooth_sco/a2dp 16k；unknown 48k 安全默认）。</item>
    /// <item>设备选择：BT 路由活跃时优先选名字含 <c>bluetooth</c>/<c>airpods</c>/<c>sco</c>
    ///   的 <see cref="UnityEngine.Microphone"/> 设备；否则系统默认（[0]）。
    ///   <see cref="preferredDevice"/> 仍可在 Inspector 显式覆盖。</item>
    /// <item>路由切换检测由 <see cref="AudioRouteDetector"/> 负责
    ///   （<c>AudioSettings.OnAudioConfigurationChanged</c> + 兜底 polling）。
    ///   收到事件后本类执行 unpublish-republish，让 LiveKit native source 用新采样率重建。</item>
    /// <item>路由切换 reason 字符串透传到 <c>audio_last_error</c>：
    ///   <c>route_changed_&lt;old&gt;_to_&lt;new&gt;</c>。republish 成功后被 ""
    ///   清空（语义：当前已恢复 healthy）；失败则被 publish_failed 等覆盖。</item>
    /// </list>
    ///
    /// <b>不在 Sprint4 Phase 3 范围（明确不做）</b>：
    /// <list type="bullet">
    /// <item>UI 设备选择器、用户手动 push-to-talk、外放回声策略（独立 Phase 4 任务）。</item>
    /// <item>把 <see cref="AudioRoutePolicy"/> 灌进候选 BB 键
    ///   <c>session/audio_route_policy</c> 或 <c>EcpFrontendState</c>
    ///   （留 # CANDIDATE，等 ECP 协议升级一起做）。</item>
    /// <item>iOS native <c>AVAudioSession</c> bridge（Detector 用 device-name fallback）。</item>
    /// </list>
    /// // AudioRoutePolicy producer hook reserved for Sprint4 Phase 4
    /// </summary>
    public class MicrophonePublisher : MonoBehaviour, IGracefulShutdownParticipant
    {
        [Tooltip("空时按当前路由（蓝牙 / 系统默认）选；非空则始终强制使用此 device 名。")]
        [SerializeField] private string preferredDevice = "";

        [Tooltip("Inspector 兜底：当 AudioRouteDetector 拿不到（比如 Editor 第一帧），" +
                 "用此值作为 fallback。运行时若 Detector 提供 policy 则会被覆盖。")]
        [SerializeField] private int fallbackSampleRate = 48000;

        [Tooltip("可选；为空时尝试 GetComponentInParent / FindObjectOfType。")]
        [SerializeField] private AppLifecycleManager lifecycleManager;

        [Tooltip("可选；为空时 FindObjectOfType；仍为空则在本 GameObject 上 AddComponent。")]
        [SerializeField] private AudioRouteDetector routeDetector;

        private MicrophoneSource _micSource;
        private LocalAudioTrack _audioTrack;
        private bool _isPublishing;
        private bool _publishInProgress;
        private bool _publishAttempted;
        private bool _shutdownInitiated;
        private string _selectedDevice = "";
        private string _lastError = "";
        private int _configuredSampleRate;
        private int _unityOutputSampleRate;
        private AudioRoutePolicy _activePolicy = AudioRoutePolicy.Default();

        private ConnectionHealthAggregator HealthAggregator =>
            lifecycleManager != null ? lifecycleManager.HealthAggregator : null;

        public bool IsPublishing => _isPublishing;
        public bool PublishAttempted => _publishAttempted;
        public string SelectedDevice => _selectedDevice;
        public string LastError => _lastError;
        public int ConfiguredSampleRate => _configuredSampleRate;
        public int UnityOutputSampleRate => _unityOutputSampleRate;
        public AudioRoutePolicy ActivePolicy => _activePolicy;

        // ─── IGracefulShutdownParticipant ────────────────────────────────

        public int ShutdownOrder => 20; // 视频先 (10)，音频后 (20)，其他 (100)

        public IEnumerator UnpublishAndStop(string reason)
        {
            _shutdownInitiated = true; // 阻止后续 OnAudioRouteChanged 触发 republish

            if (_audioTrack != null)
            {
                var room = RoomManager.Instance?.Room;
                if (room != null)
                {
                    Debug.Log($"[MicrophonePublisher] chokepoint UnpublishTrack (reason={reason})");
                    yield return room.LocalParticipant.UnpublishTrack(_audioTrack, stopOnUnpublish: true);
                }
            }
            StopPublishing($"chokepoint:{reason}");
        }

        // ─── lifecycle ────────────────────────────────────────────────────

        void Start()
        {
            if (lifecycleManager == null)
                lifecycleManager = FindObjectOfType<AppLifecycleManager>();

            if (routeDetector == null)
                routeDetector = FindObjectOfType<AudioRouteDetector>();
            if (routeDetector == null)
            {
                routeDetector = gameObject.AddComponent<AudioRouteDetector>();
                Debug.Log("[MicrophonePublisher] no AudioRouteDetector found; auto-added on this GameObject");
            }
            routeDetector.OnRouteChanged += OnAudioRouteChanged;
            _activePolicy = routeDetector.CurrentPolicy;

            var rm = RoomManager.Instance;
            if (rm == null)
            {
                Debug.LogWarning("[MicrophonePublisher] RoomManager not found");
                return;
            }

            rm.OnConnected += OnRoomConnected;
            rm.OnDisconnected += OnRoomDisconnected;
            if (rm.IsConnected) OnRoomConnected();
        }

        private void OnRoomConnected()
        {
            if (_isPublishing || _publishInProgress) return;
            // 进 publish 之前主动拉一次 detector，确保 policy 是最新的
            if (routeDetector != null) _activePolicy = routeDetector.DetectNow();
            StartCoroutine(RequestAndPublish(initialReason: null));
        }

        /// <summary>
        /// 主 publish 协程。<paramref name="initialReason"/> 在 republish 路径下用于
        /// 把 route_changed_* 透传到 health.audio_last_error，让外部观察者能看到原因；
        /// 路由切换成功后正常的 success path（<see cref="ReportAudioPublished"/> 传 ""）
        /// 会清空该字段。冷启动正常路径传 <c>null</c>，行为与 Phase 3 L3 一致。
        /// </summary>
        private IEnumerator RequestAndPublish(string initialReason)
        {
            _publishInProgress = true;
            _publishAttempted = true;
            _lastError = initialReason ?? "";

            HealthAggregator?.ReportAudioPublishAttempt(UnixSeconds());
            if (initialReason != null)
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), initialReason);

            yield return Application.RequestUserAuthorization(UserAuthorization.Microphone);

            if (!Application.HasUserAuthorization(UserAuthorization.Microphone))
            {
                _lastError = "permission_denied";
                Debug.LogError("[MicrophonePublisher] ERROR permission_denied");
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), _lastError);
                _publishInProgress = false;
                yield break;
            }

            if (Microphone.devices.Length == 0)
            {
                _lastError = "no_microphone_devices";
                Debug.LogWarning("[MicrophonePublisher] ERROR no_microphone_devices");
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), _lastError);
                _publishInProgress = false;
                yield break;
            }

            string device = SelectDevice(_activePolicy);
            _selectedDevice = device;
            Debug.Log($"[MicrophonePublisher] Using device: '{device}' for policy={_activePolicy}");

            var room = RoomManager.Instance?.Room;
            if (room == null)
            {
                _lastError = "room_missing_after_permission";
                Debug.LogWarning("[MicrophonePublisher] ERROR room_missing_after_permission");
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), _lastError);
                _publishInProgress = false;
                yield break;
            }

            ConfigureLiveKitMicrophoneSampleRate(device, _activePolicy);

            _micSource = new MicrophoneSource(device, gameObject);
            _audioTrack = LocalAudioTrack.CreateAudioTrack("microphone", _micSource, room);

            var options = new TrackPublishOptions
            {
                Source = TrackSource.SourceMicrophone,
                AudioEncoding = new AudioEncoding { MaxBitrate = 64_000 },
            };

            var publish = room.LocalParticipant.PublishTrack(_audioTrack, options);
            yield return publish;

            if (publish.IsError)
            {
                _lastError = "publish_failed";
                Debug.LogError("[MicrophonePublisher] ERROR publish_failed (PublishTrackInstruction.IsError; SDK exposes no Error details)");
                HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), _lastError);
                _publishInProgress = false;
                yield break;
            }

            _micSource.Start();
            _isPublishing = true;
            _publishInProgress = false;
            _lastError = "";
            HealthAggregator?.ReportAudioPublished(true, UnixSeconds(), "");
            Debug.Log(
                $"[MicrophonePublisher] publishing started: device='{device}' route={_activePolicy.RouteName} " +
                $"configuredSampleRate={_configuredSampleRate} unityOutputSampleRate={_unityOutputSampleRate}");
        }

        /// <summary>
        /// 根据当前 <paramref name="policy"/> 设置 LiveKit native source 期望采样率。
        ///
        /// <b>口径来源</b>：<c>livekit-unity-sdk.mdc §"Android 麦克风采样率不要跟随
        /// 不稳定路由漂移"</c>。Sprint3 brain_connected_black_video 修复确认：
        /// <list type="bullet">
        /// <item>不能用 <c>AudioSettings.outputSampleRate</c>（路由切换后不可靠）。</item>
        /// <item>必须在 <see cref="MicrophoneSource"/> 构造前设
        ///   <see cref="RtcAudioSource.DefaultMicrophoneSampleRate"/>。</item>
        /// <item>和实际路由对齐才能避免 <c>InvalidState: sample_rate and num_channels don't match</c>。</item>
        /// </list>
        /// </summary>
        private void ConfigureLiveKitMicrophoneSampleRate(string device, AudioRoutePolicy policy)
        {
            _unityOutputSampleRate = AudioSettings.outputSampleRate;
            int targetRate = policy.PreferredSampleRate > 0
                ? policy.PreferredSampleRate
                : (fallbackSampleRate > 0 ? fallbackSampleRate : 48000);

            RtcAudioSource.DefaultMicrophoneSampleRate = (uint)targetRate;
            _configuredSampleRate = targetRate;
            Debug.Log(
                $"[MicrophonePublisher] LiveKit microphone sample rate configured: {targetRate}Hz " +
                $"(route={policy.RouteName}, Unity output={_unityOutputSampleRate}Hz, device='{device}')");
        }

        /// <summary>
        /// 设备枚举与选择。优先级：<see cref="preferredDevice"/> &gt; 蓝牙路由匹配 &gt;
        /// Microphone.devices[0]（系统默认）。
        ///
        /// <b>蓝牙优先口径</b>：当 detector 给出蓝牙 policy 时，遍历 <c>Microphone.devices</c>
        /// 找名字含 bluetooth/airpods/sco/headset 的项；找不到则 fallback 默认设备
        /// （此情形下 native source 仍按 16k 配，让 SCO 即使在 device list 看不到也能工作）。
        /// </summary>
        private string SelectDevice(AudioRoutePolicy policy)
        {
            var devices = Microphone.devices;

            if (!string.IsNullOrEmpty(preferredDevice))
            {
                foreach (var d in devices)
                    if (d == preferredDevice) return d;
                Debug.LogWarning(
                    $"[MicrophonePublisher] preferredDevice '{preferredDevice}' not found; " +
                    $"falling back to route-aware selection");
            }

            if (policy.IsBluetooth)
            {
                foreach (var d in devices)
                {
                    var lower = d?.ToLowerInvariant() ?? "";
                    if (lower.Contains("bluetooth") || lower.Contains("airpods")
                        || lower.Contains("sco") || lower.Contains("headset"))
                    {
                        return d;
                    }
                }
                Debug.Log(
                    "[MicrophonePublisher] BT policy active but no BT device name in Microphone.devices; " +
                    "using default[0] (Android 通常默认 = SCO 路由源)");
            }

            return devices[0];
        }

        // ─── 路由切换 ────────────────────────────────────────────────────

        private void OnAudioRouteChanged(AudioRoutePolicy oldPolicy, AudioRoutePolicy newPolicy)
        {
            // 即使没在推流也要更新缓存，下次 publish 直接走新档
            _activePolicy = newPolicy;

            if (_shutdownInitiated)
            {
                Debug.Log($"[MicrophonePublisher] route change ignored (shutdown in progress): {oldPolicy} → {newPolicy}");
                return;
            }

            // 还没开始推流：仅更新缓存即可
            if (!_isPublishing && !_publishInProgress)
            {
                Debug.Log($"[MicrophonePublisher] route cached pre-publish: {oldPolicy} → {newPolicy}");
                return;
            }

            // 当前 publish 协程在跑：跳过这次，detector 的 polling 兜底会再触发
            if (_publishInProgress)
            {
                Debug.Log($"[MicrophonePublisher] route change during publish-in-progress; will catch up on next poll: {oldPolicy} → {newPolicy}");
                return;
            }

            if (RoomManager.Instance?.Room == null)
            {
                Debug.Log("[MicrophonePublisher] route change but room missing; skip republish");
                return;
            }

            string reason = $"route_changed_{oldPolicy.RouteName}_to_{newPolicy.RouteName}";
            StartCoroutine(RepublishForRouteChange(newPolicy, reason));
        }

        /// <summary>
        /// 路由切换重发布：先 unpublish 旧轨（让对端 Brain 收到 unpublish 事件做 graceful
        /// 处理），再用新 policy 跑 <see cref="RequestAndPublish"/>。
        ///
        /// <b>为什么不能 in-place reconfigure</b>：LiveKit <c>MicrophoneSource</c> 的采样率
        /// 在构造时就锁进了 native audio source；不重建会重现 Sprint3
        /// <c>actualRate=X expectedRate=Y</c> 的 InvalidState。
        /// </summary>
        private IEnumerator RepublishForRouteChange(AudioRoutePolicy newPolicy, string reason)
        {
            Debug.Log($"[MicrophonePublisher] republishing for {reason}; new policy={newPolicy}");
            _publishInProgress = true; // 阻止并发的 OnRoomConnected / OnAudioRouteChanged

            HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), reason);
            _lastError = reason;

            var room = RoomManager.Instance?.Room;
            if (_audioTrack != null && room != null)
            {
                yield return room.LocalParticipant.UnpublishTrack(_audioTrack, stopOnUnpublish: true);
            }

            // 静默清理本地资源：preserve lastError = reason，让 health 上保留
            // route_changed_* 直到新 publish 成功（成功路径会把 lastError 清空）
            StopPublishingInner();

            // RequestAndPublish 会先灌一次 ReportAudioPublished(false,..,reason) 再走 attempt → success
            _publishInProgress = false; // 让 RequestAndPublish 自己 set true
            yield return RequestAndPublish(initialReason: reason);
        }

        // ─── 收尾 ────────────────────────────────────────────────────────

        private void OnRoomDisconnected()
        {
            StopPublishing("room_disconnected");
        }

        private void StopPublishing(string reason)
        {
            if (!_isPublishing && _micSource == null && _audioTrack == null) return;

            StopPublishingInner();
            HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), "");
            Debug.Log($"[MicrophonePublisher] Microphone publishing stopped ({reason})");
        }

        /// <summary>
        /// 不写 health 的"纯本地资源清理"：路由切换 republish 路径用，避免 ""
        /// 把 <c>route_changed_*</c> 提前清空。
        /// </summary>
        private void StopPublishingInner()
        {
            _isPublishing = false;
            _publishInProgress = false;
            try { _micSource?.Stop(); }
            catch (Exception e) { Debug.LogWarning($"[MicrophonePublisher] Stop microphone failed: {e.Message}"); }
            _micSource = null;
            _audioTrack = null;
        }

        void OnDestroy()
        {
            StopPublishing("destroy");

            if (routeDetector != null)
                routeDetector.OnRouteChanged -= OnAudioRouteChanged;

            var rm = RoomManager.Instance;
            if (rm != null)
            {
                rm.OnConnected -= OnRoomConnected;
                rm.OnDisconnected -= OnRoomDisconnected;
            }
        }

        private static double UnixSeconds()
            => (DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalSeconds;
    }
}
