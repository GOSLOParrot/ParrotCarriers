using System;
using ParrotApp.Config;
using ParrotApp.Health;
using ParrotApp.Lifecycle;
using ParrotApp.LiveKit;
using ParrotApp.VisualTools;
using UnityEngine;
using UnityEngine.UI;

namespace ParrotApp.UI
{
    /// <summary>
    /// Minimal production home HUD shell.
    ///
    /// This is deliberately only a status surface. Menu loading, tool drawers,
    /// model controls, and workspace UI get their own loaders and report their
    /// own MainReadyGate states later.
    /// </summary>
    [DisallowMultipleComponent]
    public class FormalHomeHudController : MonoBehaviour
    {
        [SerializeField] private AppStartupFlowController startupFlow;
        [SerializeField] private AppLifecycleManager lifecycleManager;
        [SerializeField] private RoomManager roomManager;
        [SerializeField] private FormalMainReadyGate mainReadyGate;
        [SerializeField] private FormalHomeMenuLoader menuLoader;
        [SerializeField] private LiveKitReconnectSupervisor reconnectSupervisor;
        [SerializeField] private AudioRouteManager audioRouteManager;
        [SerializeField] private AudioRoutePolicyBrainReporter audioRouteReporter;
        [SerializeField] private MicrophonePublisher microphonePublisher;
        [SerializeField] private ARVideoPublisher arVideoPublisher;
        [SerializeField] private FormalModelPlacementController modelPlacementController;
        [SerializeField] private FormalArSessionBaselineReporter arSessionBaselineReporter;
        [SerializeField] private FormalArRuntimeBootstrap arRuntimeBootstrap;
        [SerializeField] private FormalXrHandPerchController xrHandPerchController;
        [SerializeField] private FormalCameraModeController cameraModeController;
        [SerializeField] private BBoxVisualToolController bboxVisualToolController;
        [SerializeField] private MagnifierVisualToolController magnifierVisualToolController;

        private Canvas _canvas;
        private Text _statusText;
        private Image _statusDot;
        private bool _visible;
        private float _tick;
        private AppStartupConfigDto _activeConfig = AppStartupConfigDto.Default();
        private FormalModelPlacementController _subscribedPlacementController;

        private void OnEnable()
        {
            Bind();
        }

        private void Start()
        {
            Bind();
            EnsureHud();
            SetVisible(false);
        }

        private void OnDisable()
        {
            Unbind();
        }

        private void Update()
        {
            if (!_visible) return;
            _tick += Time.unscaledDeltaTime;
            if (_tick < 0.25f) return;
            _tick = 0f;
            Refresh();
        }

        private void Bind()
        {
            if (startupFlow == null) startupFlow = FindObjectOfType<AppStartupFlowController>();
            if (lifecycleManager == null) lifecycleManager = FindObjectOfType<AppLifecycleManager>();
            if (roomManager == null) roomManager = RoomManager.Instance ?? FindObjectOfType<RoomManager>();
            if (mainReadyGate == null) mainReadyGate = FindObjectOfType<FormalMainReadyGate>();
            if (menuLoader == null) menuLoader = FindObjectOfType<FormalHomeMenuLoader>();
            if (reconnectSupervisor == null) reconnectSupervisor = FindObjectOfType<LiveKitReconnectSupervisor>();
            if (audioRouteManager == null) audioRouteManager = FindObjectOfType<AudioRouteManager>();
            if (audioRouteReporter == null) audioRouteReporter = FindObjectOfType<AudioRoutePolicyBrainReporter>();
            if (microphonePublisher == null) microphonePublisher = FindObjectOfType<MicrophonePublisher>();
            if (arVideoPublisher == null) arVideoPublisher = FindObjectOfType<ARVideoPublisher>();
            if (modelPlacementController == null) modelPlacementController = FindObjectOfType<FormalModelPlacementController>();
            if (arSessionBaselineReporter == null) arSessionBaselineReporter = FindObjectOfType<FormalArSessionBaselineReporter>();
            if (arRuntimeBootstrap == null) arRuntimeBootstrap = FindObjectOfType<FormalArRuntimeBootstrap>();
            if (xrHandPerchController == null) xrHandPerchController = FindObjectOfType<FormalXrHandPerchController>();
            if (cameraModeController == null) cameraModeController = FindObjectOfType<FormalCameraModeController>();
            if (bboxVisualToolController == null) bboxVisualToolController = FindObjectOfType<BBoxVisualToolController>();
            if (magnifierVisualToolController == null)
                magnifierVisualToolController = FindObjectOfType<MagnifierVisualToolController>();

            if (startupFlow != null)
            {
                startupFlow.OnTransitionStarted -= HandleTransitionStarted;
                startupFlow.OnMainUiReady -= HandleStartupMainReady;
                startupFlow.OnStartupFailed -= HandleStartupFailed;
                startupFlow.OnTransitionStarted += HandleTransitionStarted;
                startupFlow.OnMainUiReady += HandleStartupMainReady;
                startupFlow.OnStartupFailed += HandleStartupFailed;
            }

            if (mainReadyGate != null)
            {
                mainReadyGate.OnGateChanged -= HandleMainReadyGateChanged;
                mainReadyGate.OnGateChanged += HandleMainReadyGateChanged;
            }

            if (_subscribedPlacementController != modelPlacementController)
            {
                if (_subscribedPlacementController != null)
                    _subscribedPlacementController.OnPlacementStateChanged -= HandlePlacementStateChanged;
                _subscribedPlacementController = modelPlacementController;
                if (_subscribedPlacementController != null)
                    _subscribedPlacementController.OnPlacementStateChanged += HandlePlacementStateChanged;
            }
        }

        private void Unbind()
        {
            if (startupFlow != null)
            {
                startupFlow.OnTransitionStarted -= HandleTransitionStarted;
                startupFlow.OnMainUiReady -= HandleStartupMainReady;
                startupFlow.OnStartupFailed -= HandleStartupFailed;
            }
            if (mainReadyGate != null)
                mainReadyGate.OnGateChanged -= HandleMainReadyGateChanged;
            if (_subscribedPlacementController != null)
            {
                _subscribedPlacementController.OnPlacementStateChanged -= HandlePlacementStateChanged;
                _subscribedPlacementController = null;
            }
        }

        private void HandleTransitionStarted(AppStartupConfigDto config)
        {
            _activeConfig = config ?? AppStartupConfigDto.Default();
            _activeConfig.Normalize();
            SetVisible(false);
        }

        private void HandleStartupMainReady(AppStartupConfigDto config)
        {
            _activeConfig = config ?? AppStartupConfigDto.Default();
            _activeConfig.Normalize();
            EnsureHud();
            SetVisible(true);
            mainReadyGate?.ReportHudLoaded("formal_home_hud_shell");
            Refresh();
        }

        private void HandleStartupFailed(string _)
        {
            SetVisible(false);
        }

        private void HandleMainReadyGateChanged(FormalMainReadySnapshot _)
        {
            Refresh();
        }

        private void HandlePlacementStateChanged(FormalModelPlacementController placement)
        {
            if (placement != null)
                modelPlacementController = placement;
            Refresh();
        }

        private void EnsureHud()
        {
            if (_canvas != null) return;

            var root = new GameObject("FormalHomeHudCanvas");
            root.transform.SetParent(transform, false);
            _canvas = root.AddComponent<Canvas>();
            _canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            _canvas.sortingOrder = 80;

            var scaler = root.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(2800f, 1260f);
            scaler.matchWidthOrHeight = 0.5f;
            root.AddComponent<GraphicRaycaster>();

            var panel = new GameObject("FormalHomeHudPanel");
            panel.transform.SetParent(root.transform, false);
            var panelRect = panel.AddComponent<RectTransform>();
            panelRect.anchorMin = new Vector2(0f, 1f);
            panelRect.anchorMax = new Vector2(0f, 1f);
            panelRect.pivot = new Vector2(0f, 1f);
            panelRect.anchoredPosition = new Vector2(24f, -20f);
            panelRect.sizeDelta = new Vector2(980f, 528f);
            var panelImage = panel.AddComponent<Image>();
            panelImage.color = new Color(0.08f, 0.07f, 0.06f, 0.62f);
            panelImage.raycastTarget = false;

            var dot = new GameObject("FormalHomeHudStatusDot");
            dot.transform.SetParent(panel.transform, false);
            var dotRect = dot.AddComponent<RectTransform>();
            dotRect.anchorMin = new Vector2(0f, 1f);
            dotRect.anchorMax = new Vector2(0f, 1f);
            dotRect.pivot = new Vector2(0f, 1f);
            dotRect.anchoredPosition = new Vector2(18f, -18f);
            dotRect.sizeDelta = new Vector2(18f, 18f);
            _statusDot = dot.AddComponent<Image>();
            _statusDot.raycastTarget = false;

            var textGo = new GameObject("FormalHomeHudStatusText");
            textGo.transform.SetParent(panel.transform, false);
            var textRect = textGo.AddComponent<RectTransform>();
            textRect.anchorMin = Vector2.zero;
            textRect.anchorMax = Vector2.one;
            textRect.offsetMin = new Vector2(48f, 14f);
            textRect.offsetMax = new Vector2(-18f, -14f);
            _statusText = textGo.AddComponent<Text>();
            _statusText.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            _statusText.fontSize = 13;
            _statusText.alignment = TextAnchor.UpperLeft;
            _statusText.horizontalOverflow = HorizontalWrapMode.Wrap;
            _statusText.verticalOverflow = VerticalWrapMode.Overflow;
            _statusText.color = new Color(0.96f, 0.92f, 0.84f, 1f);
            _statusText.raycastTarget = false;
        }

        private void SetVisible(bool visible)
        {
            _visible = visible;
            if (_canvas != null)
                _canvas.gameObject.SetActive(visible);
        }

        private void Refresh()
        {
            if (_statusText == null) return;

            var health = lifecycleManager?.HealthAggregator != null
                ? lifecycleManager.HealthAggregator.Snapshot
                : ConnectionHealthState.Initial();
            bool connected = roomManager != null && roomManager.IsConnected;
            bool ready = mainReadyGate != null && mainReadyGate.IsReady;

            if (_statusDot != null)
            {
                _statusDot.color = ready
                    ? new Color(0.35f, 0.92f, 0.48f, 0.95f)
                    : (connected ? new Color(0.95f, 0.70f, 0.26f, 0.95f) : new Color(0.94f, 0.30f, 0.24f, 0.95f));
            }

            string missing = mainReadyGate != null ? mainReadyGate.LastMissingGates : "main_ready_gate_missing";
            if (string.IsNullOrWhiteSpace(missing)) missing = "none";
            string alert = missing;
            if (startupFlow != null && !string.IsNullOrWhiteSpace(startupFlow.LastError) && !ready)
                alert = "err " + startupFlow.LastError;
            else if (menuLoader != null && !string.IsNullOrWhiteSpace(menuLoader.LastError))
                alert = "menu " + menuLoader.LastError;
            else if (reconnectSupervisor != null && reconnectSupervisor.ReconnectPending)
                alert = "reconnecting";
            if (alert.Length > 120) alert = alert.Substring(0, 120);

            _statusText.text =
                $"LK {(connected ? "on" : "off")}  Brain {(health.BrainPresent ? "on" : "wait")}  "
                + $"Mic {MicPublishSummary(health)}  Video {VideoHudSummary(health)}\n"
                + $"Room {_activeConfig.room_profile_id}  Line {_activeConfig.line_id}/{_activeConfig.line_profile_id}\n"
                + $"Route {AudioRouteHudLabel()}\n"
                + $"UsingMic {MicrophoneDeviceHudLabel()}\n"
                + $"Uplink {UplinkHudLabel()}\n"
                + $"AR {ArHudLabel()}\n"
                + $"Place {PlacementHudLabel()}\n"
                + $"Hand {XrHandHudLabel()}\n"
                + $"Camera {CameraHudLabel()}\n"
                + $"VTool {VisualToolsHudLabel()}\n"
                + $"Home {(ready ? "ready" : "loading")}  {alert}";
        }

        private static string MicPublishSummary(ConnectionHealthState health)
        {
            if (health.AudioPublished)
                return "pub";
            return health.AudioPublishAttempted ? "wait" : "idle";
        }

        private string VideoHudSummary(ConnectionHealthState health)
        {
            if (arVideoPublisher == null)
                arVideoPublisher = FindObjectOfType<ARVideoPublisher>();
            string state = health.VideoFreshFrame ? "fresh" : (health.VideoPublishAttempted ? "wait" : "idle");
            if (arVideoPublisher == null)
                return state + " src=?";
            string source = string.IsNullOrWhiteSpace(arVideoPublisher.VideoSourceLabel)
                ? "none"
                : arVideoPublisher.VideoSourceLabel;
            string error = string.IsNullOrWhiteSpace(arVideoPublisher.LastPublishError)
                ? ""
                : " err=" + ShortLabel(arVideoPublisher.LastPublishError, 18);
            float age = arVideoPublisher.LastFrameAgeSeconds;
            string ageText = age < 0f ? "age=?" : "age=" + age.ToString("0.0");
            return state
                   + " src=" + source
                   + " frames=" + arVideoPublisher.ProducedFrameCount
                   + " " + ageText
                   + error;
        }

        private string ArHudLabel()
        {
            string baseline = arSessionBaselineReporter != null
                ? arSessionBaselineReporter.LastStatus
                : "baseline?";
            string spatial = arRuntimeBootstrap != null
                ? arRuntimeBootstrap.LastSpatialVisualStatus
                : "visual?";
            string xri = arRuntimeBootstrap != null
                ? arRuntimeBootstrap.LastTemplateInteractionStatus
                : "xri?";
            string material = arRuntimeBootstrap != null
                ? arRuntimeBootstrap.LastPlaneMaterialStatus
                : "mat?";
            return SafeLabel(baseline)
                   + " / " + SafeLabel(spatial)
                   + " / " + SafeLabel(xri)
                   + " / " + SafeLabel(material);
        }

        private string PlacementHudLabel()
        {
            if (modelPlacementController == null)
                modelPlacementController = FindObjectOfType<FormalModelPlacementController>();
            if (modelPlacementController == null)
                return "owner?";
            string rpc = startupFlow != null && !string.IsNullOrWhiteSpace(startupFlow.LastBrainRpcStatus)
                ? " " + startupFlow.LastBrainRpcStatus
                : "";
            return SafeLabel(modelPlacementController.LastDiagnosticSummary + rpc);
        }

        private string XrHandHudLabel()
        {
            if (xrHandPerchController == null)
                xrHandPerchController = FindObjectOfType<FormalXrHandPerchController>();
            if (xrHandPerchController == null)
                return "owner?";
            string mounted = xrHandPerchController.PerchMounted ? "mounted " : "wait ";
            return mounted + SafeLabel(xrHandPerchController.LastXrHandStatus);
        }

        private string VisualToolsHudLabel()
        {
            if (bboxVisualToolController == null)
                bboxVisualToolController = FindObjectOfType<BBoxVisualToolController>();
            if (magnifierVisualToolController == null)
                magnifierVisualToolController = FindObjectOfType<MagnifierVisualToolController>();

            return VisualToolHudPart("BOX", bboxVisualToolController)
                   + " / " + VisualToolHudPart("MAG", magnifierVisualToolController);
        }

        private string CameraHudLabel()
        {
            if (cameraModeController == null)
                cameraModeController = FindObjectOfType<FormalCameraModeController>();
            if (cameraModeController == null)
                return "owner?";
            return SafeLabel(cameraModeController.CurrentMode)
                   + " z=" + cameraModeController.Zoom.ToString("0.0")
                   + " ev=" + cameraModeController.Exposure.ToString("0.0")
                   + " http=" + ShortLabel(cameraModeController.LastHttpStatus, 18)
                   + " photo=" + ShortLabel(cameraModeController.LastPhotoStatus, 18);
        }

        private static string VisualToolHudPart(string label, VisualToolControllerBase controller)
        {
            if (controller == null)
                return label + " owner?";
            if (!controller.FeatureEnabled)
                return label + " flag-off";
            string open = controller.IsOpen ? "open" : "idle";
            string local = ShortLabel(controller.LastRenderStatus, 18);
            string http = ShortLabel(controller.LastHttpStatus, 18);
            string asset = ShortLabel(controller.LastAssetStatus, 18);
            return label + " " + open + " " + local + " http=" + http + " asset=" + asset;
        }

        private string AudioRouteHudLabel()
        {
            if (microphonePublisher == null)
                microphonePublisher = FindObjectOfType<MicrophonePublisher>();
            if (microphonePublisher != null && microphonePublisher.SimplePhoneMicMode)
                return "simple phone mic / route lab off";

            if (audioRouteManager != null)
            {
                var snapshot = audioRouteManager.CurrentSnapshot;
                string managerError = string.IsNullOrWhiteSpace(audioRouteManager.LastError)
                    ? ""
                    : " fail " + ShortLabel(audioRouteManager.LastError, 18);
                string native = audioRouteManager.NativeAvailable ? "native" : "fallback";
                string preference = "pref " + ShortRoutePreference(audioRouteManager.Preference);
                if (snapshot != null)
                {
                    string snapshotSuffix =
                        " v" + snapshot.route_version
                        + " " + preference
                        + " bt " + ShortLabel(snapshot.bluetooth_connect_permission, 8)
                        + " focus " + ShortLabel(snapshot.audio_focus, 8)
                        + " mode " + ShortLabel(snapshot.mode, 8);
                    return native
                           + " in " + ShortRoute(snapshot.input_route)
                           + " out " + ShortRoute(snapshot.output_route)
                           + " src " + ShortRouteSource(snapshot.source)
                           + snapshotSuffix
                           + managerError;
                }
                return native
                       + " route " + ShortRoute(audioRouteManager.CurrentPolicy.RouteName)
                       + " src " + ShortRouteSource(audioRouteManager.LastDetectionSource)
                       + " " + preference
                       + managerError;
            }

            if (audioRouteReporter == null)
                return "route unknown";

            string input = ShortRoute(audioRouteReporter.LastInputRoute);
            string output = ShortRoute(audioRouteReporter.LastOutputRoute);
            string source = ShortRouteSource(audioRouteReporter.LastDetectionSource);
            string reporterSuffix = audioRouteReporter.ReportPending
                ? " pending"
                : (!string.IsNullOrWhiteSpace(audioRouteReporter.LastReportError)
                    ? " fail " + ShortLabel(audioRouteReporter.LastReportError, 18)
                    : "");
            return "in " + input + " out " + output + " src " + source + reporterSuffix;
        }

        private string MicrophoneHudLabel()
        {
            return MicrophoneDeviceHudLabel() + " / " + UplinkHudLabel();
        }

        private string MicrophoneDeviceHudLabel()
        {
            if (microphonePublisher == null)
                microphonePublisher = FindObjectOfType<MicrophonePublisher>();
            if (microphonePublisher == null)
                return ReporterHudSuffix("publisher_missing");

            string intent = microphonePublisher.PublishIntentEnabled ? "intent on" : "intent off";
            string mode = microphonePublisher.SimplePhoneMicMode ? "simple-phone-mic" : "route-aware";
            string device = string.IsNullOrWhiteSpace(microphonePublisher.SelectedDevice)
                ? "auto"
                : microphonePublisher.SelectedDevice;
            string manual = string.IsNullOrWhiteSpace(microphonePublisher.LastManualDeviceStatus)
                ? "auto"
                : microphonePublisher.LastManualDeviceStatus;

            return mode
                   + " " + intent
                   + " selected=" + device
                   + " manual=" + manual
                   + " count=" + microphonePublisher.AvailableDeviceCount
                   + " devices=" + microphonePublisher.AvailableDevicesLabel(160);
        }

        private string UplinkHudLabel()
        {
            if (microphonePublisher == null)
                microphonePublisher = FindObjectOfType<MicrophonePublisher>();
            if (microphonePublisher == null)
                return ReporterHudSuffix("publisher_missing");

            string sampleRate = microphonePublisher.ConfiguredSampleRate > 0
                ? microphonePublisher.ConfiguredSampleRate.ToString()
                : "?";
            string error = string.IsNullOrWhiteSpace(microphonePublisher.LastError)
                ? "ok"
                : microphonePublisher.LastError;

            return microphonePublisher.UplinkStateLabel
                   + " stage=" + microphonePublisher.LastPublishStage
                   + " src=" + ShortLabel(microphonePublisher.ActiveAudioSourceKind, 18)
                   + " route=" + ShortRoute(microphonePublisher.ActivePolicy.RouteName)
                   + " sr=" + sampleRate
                   + " frames=" + microphonePublisher.AudioReadFrameCount
                   + " ch=" + microphonePublisher.LastAudioReadChannels
                   + " readSr=" + microphonePublisher.LastAudioReadSampleRate
                   + " peak=" + microphonePublisher.LastAudioReadPeak.ToString("0.000")
                   + " age=" + microphonePublisher.LastAudioReadAgeSeconds.ToString("0.0")
                   + " nz=" + microphonePublisher.LastNonSilentAudioAgeSeconds.ToString("0.0")
                   + " wd=" + ShortLabel(microphonePublisher.UplinkWatchdogState, 24)
                   + " fb=" + ShortLabel(microphonePublisher.LastCaptureFallbackStatus, 24)
                   + " nsrc=" + ShortLabel(microphonePublisher.NativeAudioRecordSource, 14)
                   + " native=" + ShortLabel(microphonePublisher.NativeAudioRecordState, 24)
                   + " nerr=" + ShortLabel(microphonePublisher.NativeAudioRecordError, 18)
                   + " rec=" + (microphonePublisher.UplinkWatchdogMicrophoneRecording ? "on" : "off")
                   + " wr=" + microphonePublisher.UplinkWatchdogRecoveryCount
                   + " v=" + microphonePublisher.PublishedRouteVersion + "/" + microphonePublisher.RouteVersion
                   + " err=" + error
                   + ReporterHudSuffix("");
        }

        private string ReporterHudSuffix(string fallback)
        {
            if (audioRouteReporter == null)
                return string.IsNullOrWhiteSpace(fallback) ? "" : " " + fallback;

            string suffix = string.IsNullOrWhiteSpace(fallback) ? "" : " " + fallback;
            suffix += " brainRoute " + audioRouteReporter.ReportSuccessCount + "/" + audioRouteReporter.ReportAttemptCount;
            if (audioRouteReporter.ReportPending)
                suffix += " pending";
            if (!string.IsNullOrWhiteSpace(audioRouteReporter.LastReportError))
                suffix += " repErr " + ShortLabel(audioRouteReporter.LastReportError, 14);
            return suffix;
        }

        private static string ShortRouteSource(string source)
        {
            if (string.Equals(source, "get_devices", StringComparison.OrdinalIgnoreCase))
                return "devices";
            if (string.Equals(source, "legacy_flags", StringComparison.OrdinalIgnoreCase))
                return "legacy";
            if (string.Equals(source, "android_error", StringComparison.OrdinalIgnoreCase))
                return "error";
            return ShortLabel(source, 10);
        }

        private static string ShortRoute(string route)
        {
            if (string.Equals(route, "system_default_microphone", StringComparison.OrdinalIgnoreCase))
                return "system";
            if (string.Equals(route, "bluetooth_sco", StringComparison.OrdinalIgnoreCase))
                return "bt-sco";
            if (string.Equals(route, "bluetooth_a2dp", StringComparison.OrdinalIgnoreCase))
                return "bt-a2dp";
            if (string.Equals(route, "wired_headset", StringComparison.OrdinalIgnoreCase))
                return "wired";
            if (string.IsNullOrWhiteSpace(route))
                return "unknown";
            return ShortLabel(route, 12);
        }

        private static string ShortRoutePreference(AudioRoutePreference preference)
        {
            switch (preference)
            {
                case AudioRoutePreference.Bluetooth:
                    return "bt";
                case AudioRoutePreference.PhoneMic:
                    return "phone";
                case AudioRoutePreference.SystemDefault:
                    return "system";
                default:
                    return "auto";
            }
        }

        private static string ShortLabel(string value, int max)
        {
            string text = string.IsNullOrWhiteSpace(value) ? "unknown" : value.Trim();
            if (text.Length <= max) return text;
            return text.Substring(0, Mathf.Max(1, max - 3)) + "...";
        }

        private static string SafeLabel(string value)
        {
            return string.IsNullOrWhiteSpace(value) ? "unknown" : value.Trim();
        }
    }
}
