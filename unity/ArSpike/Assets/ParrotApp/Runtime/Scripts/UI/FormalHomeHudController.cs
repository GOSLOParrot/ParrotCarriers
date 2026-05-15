using System;
using ParrotApp.Config;
using ParrotApp.Health;
using ParrotApp.Lifecycle;
using ParrotApp.LiveKit;
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
        [SerializeField] private AudioRoutePolicyBrainReporter audioRouteReporter;
        [SerializeField] private FormalModelPlacementController modelPlacementController;
        [SerializeField] private FormalArSessionBaselineReporter arSessionBaselineReporter;
        [SerializeField] private FormalArRuntimeBootstrap arRuntimeBootstrap;

        private Canvas _canvas;
        private Text _statusText;
        private Image _statusDot;
        private bool _visible;
        private float _tick;
        private AppStartupConfigDto _activeConfig = AppStartupConfigDto.Default();

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
            if (audioRouteReporter == null) audioRouteReporter = FindObjectOfType<AudioRoutePolicyBrainReporter>();
            if (modelPlacementController == null) modelPlacementController = FindObjectOfType<FormalModelPlacementController>();
            if (arSessionBaselineReporter == null) arSessionBaselineReporter = FindObjectOfType<FormalArSessionBaselineReporter>();
            if (arRuntimeBootstrap == null) arRuntimeBootstrap = FindObjectOfType<FormalArRuntimeBootstrap>();

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
            panelRect.sizeDelta = new Vector2(690f, 236f);
            var panelImage = panel.AddComponent<Image>();
            panelImage.color = new Color(0.08f, 0.07f, 0.06f, 0.62f);

            var dot = new GameObject("FormalHomeHudStatusDot");
            dot.transform.SetParent(panel.transform, false);
            var dotRect = dot.AddComponent<RectTransform>();
            dotRect.anchorMin = new Vector2(0f, 1f);
            dotRect.anchorMax = new Vector2(0f, 1f);
            dotRect.pivot = new Vector2(0f, 1f);
            dotRect.anchoredPosition = new Vector2(18f, -18f);
            dotRect.sizeDelta = new Vector2(18f, 18f);
            _statusDot = dot.AddComponent<Image>();

            var textGo = new GameObject("FormalHomeHudStatusText");
            textGo.transform.SetParent(panel.transform, false);
            var textRect = textGo.AddComponent<RectTransform>();
            textRect.anchorMin = Vector2.zero;
            textRect.anchorMax = Vector2.one;
            textRect.offsetMin = new Vector2(48f, 14f);
            textRect.offsetMax = new Vector2(-18f, -14f);
            _statusText = textGo.AddComponent<Text>();
            _statusText.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            _statusText.fontSize = 17;
            _statusText.alignment = TextAnchor.UpperLeft;
            _statusText.horizontalOverflow = HorizontalWrapMode.Wrap;
            _statusText.verticalOverflow = VerticalWrapMode.Truncate;
            _statusText.color = new Color(0.96f, 0.92f, 0.84f, 1f);
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
            if (alert.Length > 74) alert = alert.Substring(0, 74) + "...";

            _statusText.text =
                $"LK {(connected ? "on" : "off")}  Brain {(health.BrainPresent ? "on" : "wait")}  "
                + $"Mic {(health.AudioPublished ? "on" : "wait")}  Video {(health.VideoFreshFrame ? "fresh" : "wait")}\n"
                + $"Room {_activeConfig.room_profile_id}  Line {_activeConfig.line_id}/{_activeConfig.line_profile_id}\n"
                + $"Audio {AudioRouteHudLabel()}\n"
                + $"AR {ArHudLabel()}  Place {PlacementHudLabel()}\n"
                + $"Home {(ready ? "ready" : "loading")}  {alert}";
        }

        private string ArHudLabel()
        {
            string baseline = arSessionBaselineReporter != null
                ? arSessionBaselineReporter.LastStatus
                : "baseline?";
            string spatial = arRuntimeBootstrap != null
                ? arRuntimeBootstrap.LastSpatialVisualStatus
                : "visual?";
            return ShortLabel(baseline, 24) + " / " + ShortLabel(spatial, 24);
        }

        private string PlacementHudLabel()
        {
            if (modelPlacementController == null)
                modelPlacementController = FindObjectOfType<FormalModelPlacementController>();
            if (modelPlacementController == null)
                return "owner?";
            return ShortLabel(modelPlacementController.LastDiagnosticSummary, 58);
        }

        private string AudioRouteHudLabel()
        {
            if (audioRouteReporter == null)
                return "route unknown";

            string input = ShortRoute(audioRouteReporter.LastInputRoute);
            string output = ShortRoute(audioRouteReporter.LastOutputRoute);
            string source = ShortRouteSource(audioRouteReporter.LastDetectionSource);
            string suffix = audioRouteReporter.ReportPending
                ? " pending"
                : (!string.IsNullOrWhiteSpace(audioRouteReporter.LastReportError)
                    ? " fail " + ShortLabel(audioRouteReporter.LastReportError, 18)
                    : "");
            return "in " + input + " out " + output + " src " + source + suffix;
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

        private static string ShortLabel(string value, int max)
        {
            string text = string.IsNullOrWhiteSpace(value) ? "unknown" : value.Trim();
            if (text.Length <= max) return text;
            return text.Substring(0, Mathf.Max(1, max - 3)) + "...";
        }
    }
}
