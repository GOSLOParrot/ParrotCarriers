using System;
using System.Collections;
using ParrotApp.Backend;
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
    /// First formal homepage menu renderer.
    ///
    /// The data source is App HTTP through <see cref="FormalHomeMenuLoader"/>.
    /// This controller deliberately keeps durable saves and full canvas payloads
    /// out of LiveKit RPC. Menu-owned V1 apply actions use App HTTP:
    /// workspace switch, camera mode, photo awareness, and XR hand mode. LiveKit
    /// RPC remains only for session diagnostics or latency-sensitive runtime
    /// controls with an explicit owner.
    /// </summary>
    [DisallowMultipleComponent]
    public class FormalHomeMenuController : MonoBehaviour
    {
        private enum HomePanelKind
        {
            None,
            CanvasMenu,
            Settings
        }

        [SerializeField] private AppStartupFlowController startupFlow;
        [SerializeField] private AppLifecycleManager lifecycleManager;
        [SerializeField] private RoomManager roomManager;
        [SerializeField] private FormalMainReadyGate mainReadyGate;
        [SerializeField] private AppHomeMenuClient homeMenuClient;
        [SerializeField] private FormalHomeMenuLoader menuLoader;
        [SerializeField] private FormalModelPlacementController modelPlacementController;
        [SerializeField] private FormalHomeToolController homeToolController;
        [SerializeField] private FormalCameraModeController cameraModeController;
        [SerializeField] private BBoxVisualToolController bboxVisualToolController;
        [SerializeField] private MagnifierVisualToolController magnifierVisualToolController;
        [SerializeField] private AudioRouteManager audioRouteManager;
        [SerializeField] private AudioRouteDetector audioRouteDetector;
        [SerializeField] private AudioRoutePolicyBrainReporter audioRouteReporter;
        [SerializeField] private MicrophonePublisher microphonePublisher;

        [Header("Layout")]
        [SerializeField] private bool openDrawerOnLoad = false;
        [SerializeField] private int maxModuleRows = 5;
        [SerializeField] private int maxToolRows = 6;
        [SerializeField] private int maxNoteRows = 3;

        private Canvas _canvas;
        private RectTransform _toolbarRoot;
        private RectTransform _demoPlacementButtonRoot;
        private RectTransform _drawerRoot;
        private RectTransform _settingsPanelRoot;
        private RectTransform _workspaceStrip;
        private RectTransform _quickActionStrip;
        private RectTransform _moduleList;
        private RectTransform _toolList;
        private RectTransform _noteRail;
        private Text _headerText;
        private Text _statusText;
        private Text _cameraActionText;
        private Text _awarenessActionText;
        private Text _handActionText;
        private Text _modelPlacementActionText;
        private Text _demoPlacementButtonText;
        private Text _audioRouteActionText;
        private Text _micDeviceNextText;
        private Text _micDeviceAutoText;
        private Text _settingsAudioRouteText;
        private Image _statusDot;
        private Button _cameraActionButton;
        private Button _awarenessActionButton;
        private Button _handActionButton;
        private Button _modelPlacementActionButton;
        private Button _demoPlacementButton;
        private Button _audioRouteActionButton;
        private Button _micDeviceNextButton;
        private Button _micDeviceAutoButton;
        private bool _visible;
        private HomePanelKind _activePanel = HomePanelKind.None;
        private float _tick;
        private AppCanvasSnapshotDto _snapshot;
        private AppPersonaOptionDto[] _personas = Array.Empty<AppPersonaOptionDto>();
        private AppLineProfileOptionDto[] _lineProfiles = Array.Empty<AppLineProfileOptionDto>();
        private string _selectorError = "";
        private string _cameraMode = "off";
        private string _awarenessPolicy = "UNAWARE_RECORDED";
        private string _xrHandMode = "off";
        private string _pendingCameraMode = "";
        private string _pendingAwarenessPolicy = "";
        private string _pendingXrHandMode = "";
        private bool _audioRouteReportPending;
        private bool _workspaceApplyPending;
        private FormalModelPlacementController _subscribedPlacementController;
        private FormalCameraModeController _subscribedCameraModeController;

        private void OnEnable()
        {
            Bind();
        }

        private void Start()
        {
            Bind();
            EnsureUi();
            SetVisible(false);
            if (menuLoader != null && menuLoader.Loaded && menuLoader.LastSnapshot != null)
                RenderSnapshot(menuLoader.LastSnapshot);
        }

        private void OnDisable()
        {
            Unbind();
        }

        private void Update()
        {
            if (!_visible) return;
            _tick += Time.unscaledDeltaTime;
            if (_tick < 0.35f) return;
            _tick = 0f;
            RefreshStatus();
            RefreshWorkspaceInteractable();
            RefreshQuickActions();
        }

        private void Bind()
        {
            if (startupFlow == null) startupFlow = FindObjectOfType<AppStartupFlowController>();
            if (lifecycleManager == null) lifecycleManager = FindObjectOfType<AppLifecycleManager>();
            if (roomManager == null) roomManager = RoomManager.Instance ?? FindObjectOfType<RoomManager>();
            if (mainReadyGate == null) mainReadyGate = FindObjectOfType<FormalMainReadyGate>();
            if (homeMenuClient == null) homeMenuClient = FindObjectOfType<AppHomeMenuClient>();
            if (menuLoader == null) menuLoader = FindObjectOfType<FormalHomeMenuLoader>();
            if (modelPlacementController == null) modelPlacementController = FindObjectOfType<FormalModelPlacementController>();
            if (homeToolController == null) homeToolController = FindObjectOfType<FormalHomeToolController>();
            ResolveCameraModeController();
            if (bboxVisualToolController == null) bboxVisualToolController = FindObjectOfType<BBoxVisualToolController>();
            if (magnifierVisualToolController == null) magnifierVisualToolController = FindObjectOfType<MagnifierVisualToolController>();
            if (audioRouteManager == null) audioRouteManager = FindObjectOfType<AudioRouteManager>();
            if (audioRouteDetector == null) audioRouteDetector = FindObjectOfType<AudioRouteDetector>();
            if (audioRouteReporter == null) audioRouteReporter = FindObjectOfType<AudioRoutePolicyBrainReporter>();
            if (microphonePublisher == null) microphonePublisher = FindObjectOfType<MicrophonePublisher>();

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

            if (menuLoader != null)
            {
                menuLoader.OnSnapshotLoaded -= HandleSnapshotLoaded;
                menuLoader.OnSnapshotLoadFailed -= HandleSnapshotLoadFailed;
                menuLoader.OnSelectorCatalogLoaded -= HandleSelectorCatalogLoaded;
                menuLoader.OnSelectorCatalogLoadFailed -= HandleSelectorCatalogLoadFailed;
                menuLoader.OnSnapshotLoaded += HandleSnapshotLoaded;
                menuLoader.OnSnapshotLoadFailed += HandleSnapshotLoadFailed;
                menuLoader.OnSelectorCatalogLoaded += HandleSelectorCatalogLoaded;
                menuLoader.OnSelectorCatalogLoadFailed += HandleSelectorCatalogLoadFailed;
            }

            if (_subscribedPlacementController != modelPlacementController)
            {
                if (_subscribedPlacementController != null)
                    _subscribedPlacementController.OnPlacementStateChanged -= HandlePlacementStateChanged;
                _subscribedPlacementController = modelPlacementController;
                if (_subscribedPlacementController != null)
                    _subscribedPlacementController.OnPlacementStateChanged += HandlePlacementStateChanged;
            }

            SyncCameraModeSubscription();
        }

        private void ResolveCameraModeController()
        {
            if (cameraModeController == null)
                cameraModeController = FindObjectOfType<FormalCameraModeController>();
            SyncCameraModeSubscription();
        }

        private void SyncCameraModeSubscription()
        {
            if (_subscribedCameraModeController == cameraModeController)
                return;
            if (_subscribedCameraModeController != null)
            {
                _subscribedCameraModeController.OnModeApplyPending -= HandleCameraModeApplyPending;
                _subscribedCameraModeController.OnModeApplySucceeded -= HandleCameraModeApplySucceeded;
                _subscribedCameraModeController.OnModeApplyFailed -= HandleCameraModeApplyFailed;
            }
            _subscribedCameraModeController = cameraModeController;
            if (_subscribedCameraModeController != null)
            {
                _subscribedCameraModeController.OnModeApplyPending += HandleCameraModeApplyPending;
                _subscribedCameraModeController.OnModeApplySucceeded += HandleCameraModeApplySucceeded;
                _subscribedCameraModeController.OnModeApplyFailed += HandleCameraModeApplyFailed;
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
            if (menuLoader != null)
            {
                menuLoader.OnSnapshotLoaded -= HandleSnapshotLoaded;
                menuLoader.OnSnapshotLoadFailed -= HandleSnapshotLoadFailed;
                menuLoader.OnSelectorCatalogLoaded -= HandleSelectorCatalogLoaded;
                menuLoader.OnSelectorCatalogLoadFailed -= HandleSelectorCatalogLoadFailed;
            }
            if (_subscribedPlacementController != null)
            {
                _subscribedPlacementController.OnPlacementStateChanged -= HandlePlacementStateChanged;
                _subscribedPlacementController = null;
            }
            if (_subscribedCameraModeController != null)
            {
                _subscribedCameraModeController.OnModeApplyPending -= HandleCameraModeApplyPending;
                _subscribedCameraModeController.OnModeApplySucceeded -= HandleCameraModeApplySucceeded;
                _subscribedCameraModeController.OnModeApplyFailed -= HandleCameraModeApplyFailed;
                _subscribedCameraModeController = null;
            }
        }

        private void HandleCameraModeApplyPending(string mode)
        {
            _pendingCameraMode = NormalizeCameraMode(mode);
            RefreshQuickActions();
        }

        private void HandleCameraModeApplySucceeded(string mode)
        {
            _cameraMode = NormalizeCameraMode(mode);
            _pendingCameraMode = "";
            RefreshQuickActions();
        }

        private void HandleCameraModeApplyFailed(string mode, string error)
        {
            _pendingCameraMode = "";
            RefreshQuickActions();
        }

        private void HandleTransitionStarted(AppStartupConfigDto _)
        {
            _snapshot = null;
            _personas = Array.Empty<AppPersonaOptionDto>();
            _lineProfiles = Array.Empty<AppLineProfileOptionDto>();
            _selectorError = "";
            ClearPendingCompactControls();
            _audioRouteReportPending = false;
            _workspaceApplyPending = false;
            homeToolController?.CloseAllTools();
            cameraModeController?.SetModeLocal("off");
            bboxVisualToolController?.Release();
            magnifierVisualToolController?.Release();
            SetVisible(false);
            ClearContent();
        }

        private void HandleStartupMainReady(AppStartupConfigDto _)
        {
            EnsureUi();
            SetVisible(true);
            SetStatus("Loading menu", warning: true);
            if (menuLoader != null && menuLoader.Loaded && menuLoader.LastSnapshot != null)
                RenderSnapshot(menuLoader.LastSnapshot);
        }

        private void HandlePlacementStateChanged(FormalModelPlacementController placement)
        {
            if (placement != null)
                modelPlacementController = placement;
            RefreshQuickActions();
            RefreshStatus();
        }

        private void HandleStartupFailed(string _)
        {
            SetVisible(false);
        }

        private void HandleSnapshotLoaded(AppCanvasSnapshotDto snapshot)
        {
            RenderSnapshot(snapshot);
        }

        private void HandleSnapshotLoadFailed(string error)
        {
            EnsureUi();
            SetVisible(true);
            ClearContent();
            SetActivePanel(HomePanelKind.CanvasMenu);
            SetStatus(string.IsNullOrWhiteSpace(error) ? "Menu unavailable" : error, warning: false);
            RefreshQuickActions();
        }

        private void HandleSelectorCatalogLoaded(AppPersonaOptionDto[] personas, AppLineProfileOptionDto[] lineProfiles)
        {
            _personas = personas ?? Array.Empty<AppPersonaOptionDto>();
            _lineProfiles = lineProfiles ?? Array.Empty<AppLineProfileOptionDto>();
            _selectorError = menuLoader != null ? (menuLoader.LastSelectorError ?? "") : "";
            if (_snapshot != null)
                RenderTools(_snapshot);
        }

        private void HandleSelectorCatalogLoadFailed(string error)
        {
            _selectorError = error ?? "";
            if (_snapshot != null)
                RenderTools(_snapshot);
            RefreshStatus();
        }

        private void HandleMainReadyGateChanged(FormalMainReadySnapshot _)
        {
            RefreshStatus();
            RefreshWorkspaceInteractable();
            RefreshQuickActions();
        }

        private void RenderSnapshot(AppCanvasSnapshotDto snapshot)
        {
            _snapshot = snapshot;
            EnsureUi();
            SetVisible(true);
            _activePanel = openDrawerOnLoad ? HomePanelKind.CanvasMenu : HomePanelKind.None;
            ApplyDrawerState();

            ClearContent();
            RenderHeader(snapshot);
            DeriveQuickControlState(snapshot);
            RenderWorkspaces(snapshot);
            RenderModules(snapshot);
            RenderTools(snapshot);
            RenderNotes(snapshot);
            RefreshStatus();
            RefreshQuickActions();
        }

        private void EnsureUi()
        {
            if (_canvas != null) return;

            var root = new GameObject("FormalHomeMenuCanvas");
            root.transform.SetParent(transform, false);
            _canvas = root.AddComponent<Canvas>();
            _canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            _canvas.sortingOrder = 72;

            var scaler = root.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(2800f, 1260f);
            scaler.matchWidthOrHeight = 0.5f;
            root.AddComponent<GraphicRaycaster>();

            _toolbarRoot = CreatePanel("FormalHomeToolbar", root.transform, new Vector2(1f, 0f), new Vector2(1f, 0f), new Vector2(1f, 0f), new Vector2(-32f, 30f), new Vector2(642f, 104f), new Color(0.10f, 0.075f, 0.050f, 0.72f));
            CreateToolbarButton("ToolButtonCamera", 0, 6, "CAM", CapturePhotoTool);
            CreateToolbarButton("ToolButtonMagnifier", 1, 6, "MAG", ToggleMagnifierTool);
            CreateToolbarButton("ToolButtonBBox", 2, 6, "BOX", ToggleBBoxTool);
            CreateToolbarButton("ToolButtonCanvasMenu", 3, 6, "MENU", ToggleDrawer);
            CreateToolbarButton("ToolButtonWorkspace", 4, 6, "2D", TryOpen2DWorkspace);
            CreateToolbarButton("ToolButtonSettings", 5, 6, "SET", ToggleSettingsPanel);
            _demoPlacementButton = CreateDemoPlacementButton(root.transform, out _demoPlacementButtonRoot, out _demoPlacementButtonText);

            _drawerRoot = CreatePanel("FormalHomeMenuDrawer", root.transform, new Vector2(1f, 0.5f), new Vector2(1f, 0.5f), new Vector2(1f, 0.5f), new Vector2(-28f, 0f), new Vector2(720f, 820f), new Color(0.09f, 0.075f, 0.055f, 0.84f));
            _settingsPanelRoot = CreatePanel("FormalHomeSettingsPanel", root.transform, new Vector2(1f, 0.5f), new Vector2(1f, 0.5f), new Vector2(1f, 0.5f), new Vector2(-28f, 0f), new Vector2(620f, 430f), new Color(0.09f, 0.075f, 0.055f, 0.86f));
            _workspaceStrip = CreatePanel("FormalHomeWorkspaceStrip", _drawerRoot, new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(0.5f, 1f), new Vector2(0f, -108f), new Vector2(-38f, 104f), new Color(0.10f, 0.08f, 0.055f, 0.68f));

            _headerText = CreateText("FormalHomeMenuHeader", _drawerRoot, new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(0.5f, 1f), new Vector2(0f, -22f), new Vector2(-36f, 74f), 25, TextAnchor.MiddleLeft);
            _statusDot = CreateDot("FormalHomeMenuStatusDot", _drawerRoot, new Vector2(1f, 1f), new Vector2(1f, 1f), new Vector2(1f, 1f), new Vector2(-28f, -26f), new Vector2(20f, 20f));
            _statusText = CreateText("FormalHomeMenuStatus", _drawerRoot, new Vector2(0f, 0f), new Vector2(1f, 0f), new Vector2(0.5f, 0f), new Vector2(0f, 22f), new Vector2(-42f, 58f), 17, TextAnchor.MiddleLeft);

            CreateText("FormalHomeSettingsHeader", _settingsPanelRoot, new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(0.5f, 1f), new Vector2(0f, -24f), new Vector2(-40f, 58f), 22, TextAnchor.MiddleLeft).text = "Settings";
            CreateText("FormalHomeSettingsHint", _settingsPanelRoot, new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(0.5f, 1f), new Vector2(0f, -78f), new Vector2(-40f, 46f), 14, TextAnchor.MiddleLeft).text = "Session controls";

            _quickActionStrip = CreateArea("FormalHomeQuickActionStrip", _settingsPanelRoot, new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(0.5f, 1f), new Vector2(0f, -152f), new Vector2(-38f, 80f));
            _cameraActionButton = CreateQuickAction("QuickCameraMode", 0, 5, CycleCameraMode, out _cameraActionText);
            _awarenessActionButton = CreateQuickAction("QuickPhotoAwareness", 1, 5, TogglePhotoAwareness, out _awarenessActionText);
            _handActionButton = CreateQuickAction("QuickXrHandMode", 2, 5, CycleXrHandMode, out _handActionText);
            _modelPlacementActionButton = CreateQuickAction("ModelPlacementPlaceButton", 3, 5, PlaceModelPreview, out _modelPlacementActionText);
            _audioRouteActionButton = CreateQuickAction("QuickAudioRouteRefresh", 4, 5, RefreshAudioRoutePolicy, out _audioRouteActionText);
            _settingsAudioRouteText = CreateText("SettingsAudioRouteStatus", _settingsPanelRoot, new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(0.5f, 1f), new Vector2(0f, -236f), new Vector2(-40f, 92f), 14, TextAnchor.MiddleLeft);
            _micDeviceNextButton = CreateButton("MicDeviceCycleButton", _settingsPanelRoot, new Vector2(0f, 1f), new Vector2(0f, 1f), new Vector2(0f, 0.5f), new Vector2(24f, -316f), new Vector2(180f, 52f), new Color(0.23f, 0.16f, 0.095f, 0.84f), CycleMicrophoneDevicePreference);
            _micDeviceNextText = CreateText("MicDeviceCycleLabel", _micDeviceNextButton.transform, Vector2.zero, Vector2.one, new Vector2(0.5f, 0.5f), Vector2.zero, Vector2.zero, 13, TextAnchor.MiddleCenter);
            _micDeviceAutoButton = CreateButton("MicDeviceAutoButton", _settingsPanelRoot, new Vector2(0f, 1f), new Vector2(0f, 1f), new Vector2(0f, 0.5f), new Vector2(220f, -316f), new Vector2(180f, 52f), new Color(0.18f, 0.13f, 0.085f, 0.84f), ClearMicrophoneDevicePreference);
            _micDeviceAutoText = CreateText("MicDeviceAutoLabel", _micDeviceAutoButton.transform, Vector2.zero, Vector2.one, new Vector2(0.5f, 0.5f), Vector2.zero, Vector2.zero, 13, TextAnchor.MiddleCenter);

            _moduleList = CreateArea("FormalHomeModuleList", _drawerRoot, new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(0.5f, 1f), new Vector2(0f, -226f), new Vector2(-38f, 170f));
            _toolList = CreateArea("FormalHomeToolList", _drawerRoot, new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(0.5f, 1f), new Vector2(0f, -430f), new Vector2(-38f, 340f));
            _noteRail = CreateArea("FormalHomeNoteRail", _drawerRoot, new Vector2(0f, 0f), new Vector2(1f, 0f), new Vector2(0.5f, 0f), new Vector2(0f, 104f), new Vector2(-38f, 140f));
            ApplyDrawerState();
        }

        private void RenderHeader(AppCanvasSnapshotDto snapshot)
        {
            string workspace = snapshot != null ? snapshot.active_workspace_id : "";
            if (string.IsNullOrWhiteSpace(workspace)) workspace = "workspace";
            _headerText.text = "Home  " + workspace;
        }

        private void RenderWorkspaces(AppCanvasSnapshotDto snapshot)
        {
            ClearChildren(_workspaceStrip);
            var workspaces = snapshot?.workspaces ?? Array.Empty<AppWorkspaceDto>();
            int count = Mathf.Min(workspaces.Length, 5);
            for (int i = 0; i < count; i++)
            {
                var ws = workspaces[i];
                float gap = 10f;
                float width = Mathf.Clamp((620f - (count - 1) * gap) / Mathf.Max(1, count), 96f, 178f);
                float x = -((count - 1) * (width + gap)) * 0.5f + i * (width + gap);
                var button = CreateButton("WorkspaceTab_" + SafeName(ws.workspace_id), _workspaceStrip, new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(x, 0f), new Vector2(width, 72f), WorkspaceColor(ws), null);
                var id = ws.workspace_id ?? "";
                var layoutKind = ws.layout_kind ?? "";
                button.onClick.AddListener(() => TrySwitchWorkspace(id, layoutKind));
                button.interactable = ws.enabled && CanApplyMenuHttp() && !_workspaceApplyPending;

                var text = CreateText("WorkspaceTabLabel", button.transform, Vector2.zero, Vector2.one, new Vector2(0.5f, 0.5f), Vector2.zero, Vector2.zero, 18, TextAnchor.MiddleCenter);
                text.text = ShortLabel(ws.display_name, ws.workspace_id, 18);
            }
        }

        private void RenderModules(AppCanvasSnapshotDto snapshot)
        {
            ClearChildren(_moduleList);
            var modules = snapshot?.module_statuses ?? Array.Empty<AppModuleStatusDto>();
            int count = Mathf.Min(modules.Length, Mathf.Max(1, maxModuleRows));
            for (int i = 0; i < count; i++)
            {
                var module = modules[i];
                var row = CreateRow("ModuleRow_" + SafeName(module.module_id), _moduleList, i, 42f, ModuleColor(module.health));
                CreateText("ModuleLabel", row, Vector2.zero, Vector2.one, new Vector2(0.5f, 0.5f), new Vector2(12f, 0f), new Vector2(-24f, 0f), 16, TextAnchor.MiddleLeft).text =
                    ShortLabel(module.module_id, "module", 18) + "  " + ShortLabel(module.state, module.health, 18);
            }
            if (count == 0)
                CreateEmptyLine(_moduleList, "No modules");
        }

        private void RenderTools(AppCanvasSnapshotDto snapshot)
        {
            ClearChildren(_toolList);
            int rowIndex = 0;
            RenderAudioRouteRow(ref rowIndex);
            RenderSelectorRows(ref rowIndex);

            var tools = snapshot?.tool_cabinet ?? Array.Empty<AppToolCardDto>();
            int count = Mathf.Min(tools.Length, Mathf.Max(1, maxToolRows - rowIndex));
            for (int i = 0; i < count; i++)
            {
                var tool = tools[i];
                int row = rowIndex + i;
                var button = CreateButton("ToolCard_" + SafeName(tool.tool_id), _toolList, new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(0.5f, 1f), new Vector2(0f, -row * 62f), new Vector2(-2f, 52f), ToolColor(tool), null);
                button.interactable = false;

                var text = CreateText("ToolCardLabel", button.transform, Vector2.zero, Vector2.one, new Vector2(0.5f, 0.5f), new Vector2(14f, 0f), new Vector2(-18f, 0f), 16, TextAnchor.MiddleLeft);
                text.text = ShortLabel(tool.label, tool.tool_id, 20) + "  " + ShortLabel(tool.state, tool.enabled ? "ready" : "off", 16);
            }
            if (count == 0 && rowIndex == 0)
                CreateEmptyLine(_toolList, "No tools");
        }

        private void RenderSelectorRows(ref int rowIndex)
        {
            if (_toolList == null) return;

            var active = startupFlow != null ? startupFlow.ActiveConfig : null;
            string persona = active != null ? active.persona_id : "";
            string lineProfile = active != null ? active.line_profile_id : "";

            CreateSelectorLine(
                "SelectorPersona",
                rowIndex++,
                "Persona",
                SelectorLabel(FindPersonaLabel(persona), persona, _personas.Length));
            CreateSelectorLine(
                "SelectorLineProfile",
                rowIndex++,
                "Line",
                SelectorLabel(FindLineProfileLabel(lineProfile), lineProfile, _lineProfiles.Length));

            if (!string.IsNullOrWhiteSpace(_selectorError))
            {
                CreateSelectorLine(
                    "SelectorCatalogDegraded",
                    rowIndex++,
                    "Catalog",
                    ShortLabel(_selectorError, "degraded", 34),
                    warning: true);
            }
        }

        private void RenderAudioRouteRow(ref int rowIndex)
        {
            if (_toolList == null) return;
            CreateSelectorLine(
                "AudioRouteStatus",
                rowIndex++,
                "Audio",
                AudioRouteStatusLabel(),
                audioRouteReporter != null && !string.IsNullOrWhiteSpace(audioRouteReporter.LastReportError));
        }

        private void DeriveQuickControlState(AppCanvasSnapshotDto snapshot)
        {
            var tools = snapshot?.tool_cabinet ?? Array.Empty<AppToolCardDto>();
            foreach (var tool in tools)
            {
                if (tool == null || string.IsNullOrWhiteSpace(tool.state)) continue;
                if (string.Equals(tool.tool_id, "camera", StringComparison.OrdinalIgnoreCase))
                    _cameraMode = tool.state.Trim();
            }

            var modules = snapshot?.module_statuses ?? Array.Empty<AppModuleStatusDto>();
            foreach (var module in modules)
            {
                if (module == null || string.IsNullOrWhiteSpace(module.state)) continue;
                if (string.Equals(module.module_id, "xr_hand", StringComparison.OrdinalIgnoreCase))
                    _xrHandMode = module.state.Trim();
                if (string.Equals(module.module_id, "photo_camera", StringComparison.OrdinalIgnoreCase))
                    _cameraMode = module.state.Trim();
            }

            ResolveCameraModeController();
            cameraModeController?.SetModeLocal(_cameraMode, !string.Equals(_cameraMode, "off", StringComparison.OrdinalIgnoreCase));
        }

        private void CycleCameraMode()
        {
            if (!CanApplyMenuHttp())
            {
                SetStatus("Camera waits App HTTP", warning: false);
                return;
            }
            if (!string.IsNullOrWhiteSpace(_pendingCameraMode))
            {
                SetStatus("Camera HTTP pending " + _pendingCameraMode, warning: true);
                return;
            }

            string nextMode = NextCameraMode(_cameraMode);
            _pendingCameraMode = nextMode;
            ResolveCameraModeController();
            cameraModeController?.MarkHttpPending(nextMode);
            StartCoroutine(ApplyCameraModeHttp(nextMode));
            RefreshQuickActions();
            SetStatus("Camera HTTP " + nextMode, warning: true);
        }

        private void TogglePhotoAwareness()
        {
            if (!CanApplyMenuHttp())
            {
                SetStatus("Awareness waits App HTTP", warning: false);
                return;
            }

            string nextPolicy = string.Equals(_awarenessPolicy, "AWARE_SILENT", StringComparison.OrdinalIgnoreCase)
                ? "UNAWARE_RECORDED"
                : "AWARE_SILENT";
            _pendingAwarenessPolicy = nextPolicy;
            StartCoroutine(ApplyPhotoAwarenessHttp(nextPolicy));
            RefreshQuickActions();
            SetStatus("Photo HTTP " + AwarenessShortLabel(nextPolicy), warning: true);
        }

        private void CycleXrHandMode()
        {
            if (!CanApplyMenuHttp())
            {
                SetStatus("Hands wait App HTTP", warning: false);
                return;
            }

            string nextMode = NextXrHandMode(_xrHandMode);
            _pendingXrHandMode = nextMode;
            StartCoroutine(ApplyXrHandModeHttp(nextMode));
            RefreshQuickActions();
            SetStatus("Hands HTTP " + nextMode, warning: true);
        }

        private void RefreshAudioRoutePolicy()
        {
            if (!CanSendCompactControl())
            {
                SetStatus("Audio route waits Brain", warning: false);
                return;
            }
            if (audioRouteReporter == null)
            {
                audioRouteReporter = FindObjectOfType<AudioRoutePolicyBrainReporter>();
                if (audioRouteReporter == null)
                {
                    SetStatus("Audio route reporter missing", warning: false);
                    return;
                }
            }

            _audioRouteReportPending = true;
            if (audioRouteManager != null)
                audioRouteManager.RefreshCurrentPolicy("formal_home_manual_rescan");
            audioRouteReporter.RefreshAndReportCurrentPolicy("formal_home_manual_rescan");
            RefreshQuickActions();
            if (_snapshot != null)
                RenderTools(_snapshot);
            SetStatus("Audio route reporting", warning: true);
        }

        private void CycleMicrophoneDevicePreference()
        {
            if (microphonePublisher == null)
            {
                microphonePublisher = FindObjectOfType<MicrophonePublisher>();
                if (microphonePublisher == null)
                {
                    SetStatus("Microphone publisher missing", warning: false);
                    return;
                }
            }

            if (!microphonePublisher.CyclePreferredDevice("formal_home_mic_device_cycle"))
            {
                SetStatus("No microphone devices", warning: false);
                RefreshQuickActions();
                return;
            }

            SetStatus("Mic " + MicrophonePreferenceShortLabel(), warning: true);
            RefreshQuickActions();
        }

        private void ClearMicrophoneDevicePreference()
        {
            if (microphonePublisher == null)
            {
                microphonePublisher = FindObjectOfType<MicrophonePublisher>();
                if (microphonePublisher == null)
                {
                    SetStatus("Microphone publisher missing", warning: false);
                    return;
                }
            }

            microphonePublisher.ClearPreferredDevice("formal_home_mic_device_auto");
            SetStatus("Mic auto", warning: true);
            RefreshQuickActions();
        }

        private void PlaceModelPreview()
        {
            if (modelPlacementController == null)
                modelPlacementController = FindObjectOfType<FormalModelPlacementController>();
            if (modelPlacementController == null)
            {
                SetStatus("Placement owner missing", warning: false);
                return;
            }

            if (modelPlacementController.HasPlacedModel)
            {
                modelPlacementController.ClearPlacedModel();
                SetStatus("Model cleared", warning: true);
                RefreshQuickActions();
                return;
            }

            modelPlacementController.PlaceAtDefaultPreview();
            SetStatus(modelPlacementController.LastPlacementStatus, modelPlacementController.HasPlacedModel);
            RefreshQuickActions();
        }

        private void CapturePhotoTool()
        {
            if (homeToolController == null)
                homeToolController = FindObjectOfType<FormalHomeToolController>();
            if (homeToolController == null)
            {
                SetStatus("Photo owner missing", warning: false);
                return;
            }

            string status = homeToolController.CapturePhoto();
            bool photoOk = !status.Contains("missing") && !status.Contains("waits") && !status.Contains("not_phone_safe");
            ResolveCameraModeController();
            if (photoOk)
                cameraModeController?.SetModeLocal("capture_locked");
            cameraModeController?.MarkPhotoCaptureStatus(status, photoOk);
            SetStatus(status, photoOk);
        }

        private void ToggleMagnifierTool()
        {
            if (magnifierVisualToolController == null)
                magnifierVisualToolController = FindObjectOfType<MagnifierVisualToolController>();
            if (magnifierVisualToolController == null)
            {
                SetActivePanel(HomePanelKind.CanvasMenu);
                SetStatus("MAG controller missing", warning: false);
                return;
            }

            string status = magnifierVisualToolController.ToggleTool();
            if (!magnifierVisualToolController.FeatureEnabled)
                SetActivePanel(HomePanelKind.CanvasMenu);
            SetStatus(ToolStatusForMenu(status, "MAG after phone stability"), ToolStatusLooksOk(status));
        }

        private void ToggleBBoxTool()
        {
            if (bboxVisualToolController == null)
                bboxVisualToolController = FindObjectOfType<BBoxVisualToolController>();
            if (bboxVisualToolController == null)
            {
                SetActivePanel(HomePanelKind.CanvasMenu);
                SetStatus("BOX controller missing", warning: false);
                return;
            }

            string status = bboxVisualToolController.ToggleTool();
            if (!bboxVisualToolController.FeatureEnabled)
                SetActivePanel(HomePanelKind.CanvasMenu);
            SetStatus(ToolStatusForMenu(status, "BOX after phone stability"), ToolStatusLooksOk(status));
        }

        private void TryOpen2DWorkspace()
        {
            SetActivePanel(HomePanelKind.CanvasMenu);
            var workspaces = _snapshot?.workspaces ?? Array.Empty<AppWorkspaceDto>();
            foreach (var workspace in workspaces)
            {
                if (workspace == null || !workspace.enabled) continue;
                if (string.Equals(workspace.layout_kind, "2d_workspace", StringComparison.OrdinalIgnoreCase))
                {
                    TrySwitchWorkspace(workspace.workspace_id, workspace.layout_kind);
                    return;
                }
            }

            SetStatus("2D workspace is not available in this room", warning: false);
        }

        private void RenderNotes(AppCanvasSnapshotDto snapshot)
        {
            ClearChildren(_noteRail);
            int written = 0;
            var notes = snapshot?.paper_notes ?? Array.Empty<AppPaperNoteDto>();
            for (int i = 0; i < notes.Length && written < maxNoteRows; i++, written++)
                CreateNoteLine("PaperNote_" + written, notes[i].title, notes[i].summary, written);

            var photos = snapshot?.photo_refs ?? Array.Empty<AppPhotoRefDto>();
            for (int i = 0; i < photos.Length && written < maxNoteRows; i++, written++)
                CreateNoteLine("PhotoRef_" + written, photos[i].title, photos[i].summary, written);

            if (written == 0)
                CreateEmptyLine(_noteRail, "No notes");
        }

        private void TrySwitchWorkspace(string workspaceId, string layoutKind)
        {
            if (string.IsNullOrWhiteSpace(workspaceId)) return;
            if (!CanApplyMenuHttp())
            {
                SetStatus("Workspace waits App HTTP", warning: false);
                return;
            }
            if (_workspaceApplyPending)
            {
                SetStatus("Workspace apply pending", warning: true);
                return;
            }

            _workspaceApplyPending = true;
            StartCoroutine(ApplyWorkspaceHttp(workspaceId, layoutKind));
            RefreshWorkspaceInteractable();
            SetStatus("Workspace HTTP " + workspaceId + WorkspacePolicyLabel(layoutKind), warning: true);
        }

        private IEnumerator ApplyWorkspaceHttp(string workspaceId, string layoutKind)
        {
            RequestResult<AppActionResultDto> result = default;
            yield return homeMenuClient.ApplyWorkspace(workspaceId, r => result = r);
            _workspaceApplyPending = false;

            if (result.Success)
            {
                if (_snapshot != null)
                {
                    _snapshot.active_workspace_id = workspaceId;
                    RenderHeader(_snapshot);
                    RenderWorkspaces(_snapshot);
                }
                SetStatus("Workspace applied " + ShortLabel(workspaceId, "workspace", 24), warning: true);
            }
            else
            {
                SetStatus("Workspace HTTP failed " + ShortLabel(result.Error, "unknown", 28), warning: false);
            }

            RefreshWorkspaceInteractable();
            RefreshQuickActions();
        }

        private IEnumerator ApplyCameraModeHttp(string mode)
        {
            RequestResult<AppActionResultDto> result = default;
            yield return homeMenuClient.SetCameraMode(mode, r => result = r);
            _pendingCameraMode = "";
            if (result.Success)
            {
                _cameraMode = mode;
                ResolveCameraModeController();
                cameraModeController?.MarkHttpResult(mode, true);
                SetStatus("Camera " + _cameraMode, warning: true);
            }
            else
            {
                ResolveCameraModeController();
                cameraModeController?.SetModeLocal(_cameraMode);
                cameraModeController?.MarkHttpResult(_cameraMode, false, result.Error);
                SetStatus("Camera HTTP failed " + ShortLabel(result.Error, "unknown", 28), warning: false);
            }
            RefreshQuickActions();
        }

        private IEnumerator ApplyPhotoAwarenessHttp(string policy)
        {
            RequestResult<AppActionResultDto> result = default;
            yield return homeMenuClient.SetPhotoAwarenessPolicy(policy, r => result = r);
            _pendingAwarenessPolicy = "";
            if (result.Success)
            {
                _awarenessPolicy = policy;
                SetStatus("Photo " + AwarenessShortLabel(_awarenessPolicy), warning: true);
            }
            else
            {
                SetStatus("Photo HTTP failed " + ShortLabel(result.Error, "unknown", 28), warning: false);
            }
            RefreshQuickActions();
        }

        private IEnumerator ApplyXrHandModeHttp(string mode)
        {
            RequestResult<AppActionResultDto> result = default;
            yield return homeMenuClient.SetXrHandMode(mode, r => result = r);
            _pendingXrHandMode = "";
            if (result.Success)
            {
                _xrHandMode = mode;
                SetStatus("Hands " + _xrHandMode, warning: true);
            }
            else
            {
                SetStatus("Hands HTTP failed " + ShortLabel(result.Error, "unknown", 28), warning: false);
            }
            RefreshQuickActions();
        }

        private bool CanSendCompactControl()
        {
            var health = lifecycleManager?.HealthAggregator != null
                ? lifecycleManager.HealthAggregator.Snapshot
                : ConnectionHealthState.Initial();
            return startupFlow != null
                   && roomManager != null
                   && roomManager.IsConnected
                   && health.BrainPresent;
        }

        private bool CanApplyMenuHttp()
        {
            return homeMenuClient != null && homeMenuClient.HasEndpoint;
        }

        private void RefreshStatus()
        {
            if (_statusText == null) return;
            if (menuLoader != null && !string.IsNullOrWhiteSpace(menuLoader.LastError))
            {
                SetStatus(menuLoader.LastError, warning: false);
                return;
            }

            var missing = mainReadyGate != null ? mainReadyGate.LastMissingGates : "";
            bool ready = mainReadyGate != null && mainReadyGate.IsReady;
            bool controlReady = CanSendCompactControl();
            bool menuHttpReady = CanApplyMenuHttp();
            string text = ready ? "Ready" : "Gates " + (string.IsNullOrWhiteSpace(missing) ? "loading" : ShortLabel(missing, "loading", 44));
            if (!menuHttpReady) text += "  menu http wait";
            if (!controlReady) text += "  live controls wait";
            SetStatus(text, warning: ready || controlReady || menuHttpReady);
        }

        private void RefreshWorkspaceInteractable()
        {
            if (_workspaceStrip == null) return;
            bool canSend = CanApplyMenuHttp() && !_workspaceApplyPending;
            var buttons = _workspaceStrip.GetComponentsInChildren<Button>(true);
            var workspaces = _snapshot?.workspaces ?? Array.Empty<AppWorkspaceDto>();
            for (int i = 0; i < buttons.Length; i++)
            {
                bool enabled = i < workspaces.Length && workspaces[i] != null && workspaces[i].enabled;
                buttons[i].interactable = canSend && enabled;
            }
        }

        private void RefreshQuickActions()
        {
            bool canApplyMenu = CanApplyMenuHttp();
            bool canSend = CanSendCompactControl();
            bool audioPending = audioRouteReporter != null && audioRouteReporter.ReportPending;
            if (_audioRouteReportPending && !audioPending)
            {
                _audioRouteReportPending = false;
                SetStatus(
                    audioRouteReporter != null && !string.IsNullOrWhiteSpace(audioRouteReporter.LastReportError)
                        ? "Audio route failed " + ShortLabel(audioRouteReporter.LastReportError, "unknown", 24)
                        : "Audio route " + AudioRouteShortLabel(),
                    audioRouteReporter == null || string.IsNullOrWhiteSpace(audioRouteReporter.LastReportError));
                if (_snapshot != null)
                    RenderTools(_snapshot);
            }

            if (_cameraActionButton != null) _cameraActionButton.interactable = canApplyMenu && string.IsNullOrWhiteSpace(_pendingCameraMode);
            if (_awarenessActionButton != null) _awarenessActionButton.interactable = canApplyMenu && string.IsNullOrWhiteSpace(_pendingAwarenessPolicy);
            if (_handActionButton != null) _handActionButton.interactable = canApplyMenu && string.IsNullOrWhiteSpace(_pendingXrHandMode);
            if (_modelPlacementActionButton != null)
                _modelPlacementActionButton.interactable = modelPlacementController != null
                                                           && (modelPlacementController.HasPlacedModel
                                                               || modelPlacementController.CanPlaceNow);
            if (_demoPlacementButton != null)
                _demoPlacementButton.interactable = modelPlacementController != null
                                                    && (modelPlacementController.HasPlacedModel
                                                        || modelPlacementController.CanPlaceNow);
            if (_audioRouteActionButton != null) _audioRouteActionButton.interactable = canSend && !audioPending;
            if (_micDeviceNextButton != null) _micDeviceNextButton.interactable = microphonePublisher != null;
            if (_micDeviceAutoButton != null) _micDeviceAutoButton.interactable = microphonePublisher != null && !string.IsNullOrWhiteSpace(microphonePublisher.PreferredDevice);

            if (_cameraActionText != null)
                _cameraActionText.text = "CAM\n" + PendingOrCurrentLabel(_cameraMode, _pendingCameraMode, "off");
            if (_awarenessActionText != null)
                _awarenessActionText.text = "PHOTO\n" + (string.IsNullOrWhiteSpace(_pendingAwarenessPolicy) ? AwarenessShortLabel(_awarenessPolicy) : "...");
            if (_handActionText != null)
                _handActionText.text = "HAND\n" + PendingOrCurrentLabel(_xrHandMode, _pendingXrHandMode, "off");
            if (_modelPlacementActionText != null)
                _modelPlacementActionText.text =
                    (modelPlacementController != null && modelPlacementController.HasPlacedModel ? "CLEAR\n" : "PLACE\n")
                    + PlacementShortLabel();
            if (_demoPlacementButtonText != null)
                _demoPlacementButtonText.text = modelPlacementController != null && modelPlacementController.HasPlacedModel
                    ? "CLEAR"
                    : "";
            if (_audioRouteActionText != null)
                _audioRouteActionText.text = "AUDIO\n" + (audioPending ? "..." : AudioRouteShortLabel());
            if (_micDeviceNextText != null)
                _micDeviceNextText.text = "MIC\nNEXT";
            if (_micDeviceAutoText != null)
                _micDeviceAutoText.text = "MIC\nAUTO";
            if (_settingsAudioRouteText != null)
                _settingsAudioRouteText.text =
                    "Audio  " + ShortLabel(AudioRouteStatusLabel(), "unknown", 64)
                    + "\nMic    " + ShortLabel(MicrophoneStatusLabel(), "unknown", 64);
        }

        private string PlacementShortLabel()
        {
            if (modelPlacementController == null)
                modelPlacementController = FindObjectOfType<FormalModelPlacementController>();
            if (modelPlacementController == null) return "owner?";
            if (modelPlacementController.HasPlacedModel) return "done";
            if (startupFlow == null || !startupFlow.MainUiReadyOnce) return "wait";
            if (!modelPlacementController.CanPlaceNow) return "gates";
            return "ready";
        }

        private void SetStatus(string text, bool warning)
        {
            if (_statusText != null)
                _statusText.text = string.IsNullOrWhiteSpace(text) ? "Loading" : ShortLabel(text, "Loading", 72);
            if (_statusDot != null)
                _statusDot.color = warning
                    ? new Color(0.38f, 0.90f, 0.48f, 0.95f)
                    : new Color(0.94f, 0.32f, 0.24f, 0.95f);
        }

        private void ToggleDrawer()
        {
            SetActivePanel(_activePanel == HomePanelKind.CanvasMenu ? HomePanelKind.None : HomePanelKind.CanvasMenu);
        }

        private void ToggleSettingsPanel()
        {
            SetActivePanel(_activePanel == HomePanelKind.Settings ? HomePanelKind.None : HomePanelKind.Settings);
        }

        private void SetActivePanel(HomePanelKind panel)
        {
            _activePanel = panel;
            ApplyDrawerState();
        }

        private void ApplyDrawerState()
        {
            if (_drawerRoot != null)
                _drawerRoot.gameObject.SetActive(_visible && _activePanel == HomePanelKind.CanvasMenu);
            if (_settingsPanelRoot != null)
                _settingsPanelRoot.gameObject.SetActive(_visible && _activePanel == HomePanelKind.Settings);
            if (_toolbarRoot != null)
                _toolbarRoot.gameObject.SetActive(_visible);
            if (_demoPlacementButtonRoot != null)
                _demoPlacementButtonRoot.gameObject.SetActive(_visible);
        }

        private void SetVisible(bool visible)
        {
            _visible = visible;
            if (_canvas != null)
            {
                _canvas.gameObject.SetActive(visible);
                ApplyDrawerState();
            }
        }

        private void ClearContent()
        {
            if (_workspaceStrip != null) ClearChildren(_workspaceStrip);
            if (_moduleList != null) ClearChildren(_moduleList);
            if (_toolList != null) ClearChildren(_toolList);
            if (_noteRail != null) ClearChildren(_noteRail);
        }

        private static RectTransform CreatePanel(string name, Transform parent, Vector2 anchorMin, Vector2 anchorMax, Vector2 pivot, Vector2 position, Vector2 size, Color color)
        {
            var rect = CreateArea(name, parent, anchorMin, anchorMax, pivot, position, size);
            var image = rect.gameObject.AddComponent<Image>();
            image.sprite = LoadSprite("paper_status_panel");
            image.type = image.sprite != null ? Image.Type.Sliced : Image.Type.Simple;
            image.color = color;
            image.raycastTarget = false;
            return rect;
        }

        private static RectTransform CreateArea(string name, Transform parent, Vector2 anchorMin, Vector2 anchorMax, Vector2 pivot, Vector2 position, Vector2 size)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var rect = go.AddComponent<RectTransform>();
            rect.anchorMin = anchorMin;
            rect.anchorMax = anchorMax;
            rect.pivot = pivot;
            rect.anchoredPosition = position;
            rect.sizeDelta = size;
            return rect;
        }

        private static Button CreateButton(string name, Transform parent, Vector2 anchorMin, Vector2 anchorMax, Vector2 pivot, Vector2 position, Vector2 size, Color color, Action onClick)
        {
            var rect = CreatePanel(name, parent, anchorMin, anchorMax, pivot, position, size, color);
            var image = rect.GetComponent<Image>();
            if (image != null)
                image.raycastTarget = true;
            var button = rect.gameObject.AddComponent<Button>();
            if (onClick != null)
                button.onClick.AddListener(() => onClick());
            return button;
        }

        private Button CreateQuickAction(string name, int index, int count, Action onClick, out Text label)
        {
            float width = Mathf.Max(104f, 500f / Mathf.Max(1, count) - 10f);
            float x = (index - (count - 1) * 0.5f) * (width + 10f);
            var button = CreateButton(
                name,
                _quickActionStrip,
                new Vector2(0.5f, 0.5f),
                new Vector2(0.5f, 0.5f),
                new Vector2(0.5f, 0.5f),
                new Vector2(x, 0f),
                new Vector2(width, 58f),
                new Color(0.23f, 0.16f, 0.095f, 0.84f),
                onClick);
            label = CreateText(name + "Label", button.transform, Vector2.zero, Vector2.one, new Vector2(0.5f, 0.5f), Vector2.zero, Vector2.zero, 13, TextAnchor.MiddleCenter);
            return button;
        }

        private Button CreateToolbarButton(string name, int index, int count, string label, Action onClick)
        {
            float width = 88f;
            float gap = 14f;
            float x = -((count - 1) * (width + gap)) * 0.5f + index * (width + gap);
            var button = CreateButton(
                name,
                _toolbarRoot,
                new Vector2(0.5f, 0.5f),
                new Vector2(0.5f, 0.5f),
                new Vector2(0.5f, 0.5f),
                new Vector2(x, 0f),
                new Vector2(width, 78f),
                new Color(0.22f, 0.16f, 0.095f, 0.84f),
                onClick);

            var icon = CreateArea(name + "PixelIcon", button.transform, new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0f, 12f), new Vector2(32f, 32f));
            var iconImage = icon.gameObject.AddComponent<Image>();
            iconImage.color = ToolbarIconColor(index);
            iconImage.raycastTarget = false;

            var text = CreateText(name + "Label", button.transform, new Vector2(0f, 0f), new Vector2(1f, 0f), new Vector2(0.5f, 0f), new Vector2(0f, 5f), new Vector2(-8f, 24f), 11, TextAnchor.MiddleCenter);
            text.text = label;
            return button;
        }

        private Button CreateDemoPlacementButton(Transform parent, out RectTransform root, out Text label)
        {
            var rect = CreateArea(
                "ARMobileTemplatePlaceButton",
                parent,
                new Vector2(0.5f, 0f),
                new Vector2(0.5f, 0f),
                new Vector2(0.5f, 0f),
                new Vector2(0f, 34f),
                new Vector2(116f, 116f));
            root = rect;

            var bg = rect.gameObject.AddComponent<Image>();
            bg.sprite = LoadArMobileTemplateSprite("ActivationButtonOpaque");
            bg.type = bg.sprite != null ? Image.Type.Simple : Image.Type.Sliced;
            bg.color = new Color(1f, 1f, 1f, bg.sprite != null ? 0.98f : 0.68f);
            bg.raycastTarget = true;

            var button = rect.gameObject.AddComponent<Button>();
            button.onClick.AddListener(PlaceModelPreview);

            var icon = CreateArea(
                "ARMobileTemplatePlaceIcon",
                rect,
                new Vector2(0.5f, 0.5f),
                new Vector2(0.5f, 0.5f),
                new Vector2(0.5f, 0.5f),
                new Vector2(0f, 4f),
                new Vector2(58f, 58f));
            var iconImage = icon.gameObject.AddComponent<Image>();
            iconImage.sprite = LoadArMobileTemplateSprite("Icon-Cube");
            iconImage.color = iconImage.sprite != null ? Color.white : new Color(0.94f, 0.90f, 0.82f, 1f);
            iconImage.raycastTarget = false;

            label = CreateText(
                "ARMobileTemplatePlaceLabel",
                rect,
                new Vector2(0f, 0f),
                new Vector2(1f, 0f),
                new Vector2(0.5f, 0f),
                new Vector2(0f, 8f),
                new Vector2(-8f, 24f),
                12,
                TextAnchor.MiddleCenter);
            label.color = new Color(0.95f, 0.90f, 0.80f, 1f);
            return button;
        }

        private static Text CreateText(string name, Transform parent, Vector2 anchorMin, Vector2 anchorMax, Vector2 pivot, Vector2 position, Vector2 size, int fontSize, TextAnchor alignment)
        {
            var rect = CreateArea(name, parent, anchorMin, anchorMax, pivot, position, size);
            var text = rect.gameObject.AddComponent<Text>();
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            text.fontSize = fontSize;
            text.alignment = alignment;
            text.horizontalOverflow = HorizontalWrapMode.Wrap;
            text.verticalOverflow = VerticalWrapMode.Truncate;
            text.color = new Color(0.95f, 0.90f, 0.80f, 1f);
            text.raycastTarget = false;
            return text;
        }

        private static Image CreateDot(string name, Transform parent, Vector2 anchorMin, Vector2 anchorMax, Vector2 pivot, Vector2 position, Vector2 size)
        {
            var rect = CreateArea(name, parent, anchorMin, anchorMax, pivot, position, size);
            var image = rect.gameObject.AddComponent<Image>();
            image.sprite = LoadSprite("status_red");
            image.color = new Color(0.94f, 0.32f, 0.24f, 0.95f);
            image.raycastTarget = false;
            return image;
        }

        private static RectTransform CreateRow(string name, Transform parent, int index, float height, Color color)
        {
            return CreatePanel(name, parent, new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(0.5f, 1f), new Vector2(0f, -index * (height + 8f)), new Vector2(-2f, height), color);
        }

        private void CreateNoteLine(string name, string title, string summary, int index)
        {
            var row = CreateRow(name, _noteRail, index, 36f, new Color(0.20f, 0.16f, 0.10f, 0.70f));
            CreateText("NoteText", row, Vector2.zero, Vector2.one, new Vector2(0.5f, 0.5f), new Vector2(12f, 0f), new Vector2(-14f, 0f), 14, TextAnchor.MiddleLeft).text =
                ShortLabel(title, summary, 46);
        }

        private void CreateSelectorLine(string name, int index, string label, string value, bool warning = false)
        {
            var color = warning
                ? new Color(0.30f, 0.20f, 0.10f, 0.78f)
                : new Color(0.16f, 0.13f, 0.085f, 0.78f);
            var row = CreateRow(name, _toolList, index, 42f, color);
            CreateText("SelectorText", row, Vector2.zero, Vector2.one, new Vector2(0.5f, 0.5f), new Vector2(12f, 0f), new Vector2(-14f, 0f), 14, TextAnchor.MiddleLeft).text =
                ShortLabel(label, "Selector", 12) + "  " + ShortLabel(value, "loading", 42);
        }

        private void CreateEmptyLine(RectTransform parent, string label)
        {
            var row = CreateRow("Empty_" + SafeName(label), parent, 0, 38f, new Color(0.13f, 0.10f, 0.075f, 0.58f));
            CreateText("EmptyText", row, Vector2.zero, Vector2.one, new Vector2(0.5f, 0.5f), new Vector2(12f, 0f), new Vector2(-12f, 0f), 14, TextAnchor.MiddleLeft).text = label;
        }

        private static void ClearChildren(RectTransform parent)
        {
            if (parent == null) return;
            for (int i = parent.childCount - 1; i >= 0; i--)
            {
                var child = parent.GetChild(i).gameObject;
                if (Application.isPlaying) UnityEngine.Object.Destroy(child);
                else UnityEngine.Object.DestroyImmediate(child);
            }
        }

        private static Sprite LoadSprite(string name)
        {
            return Resources.Load<Sprite>("StartupPaperCraft/" + name);
        }

        private static Sprite LoadArMobileTemplateSprite(string name)
        {
            return Resources.Load<Sprite>("ARMobileTemplate/UI/Sprites/" + name);
        }

        private static Color WorkspaceColor(AppWorkspaceDto ws)
        {
            if (ws == null || !ws.enabled) return new Color(0.14f, 0.12f, 0.095f, 0.65f);
            return new Color(0.28f, 0.21f, 0.13f, 0.86f);
        }

        private static Color ModuleColor(string health)
        {
            if (string.Equals(health, "healthy", StringComparison.OrdinalIgnoreCase))
                return new Color(0.16f, 0.26f, 0.15f, 0.72f);
            if (string.Equals(health, "degraded", StringComparison.OrdinalIgnoreCase))
                return new Color(0.28f, 0.22f, 0.11f, 0.72f);
            return new Color(0.24f, 0.13f, 0.10f, 0.72f);
        }

        private static Color ToolColor(AppToolCardDto tool)
        {
            if (tool != null && tool.enabled)
                return new Color(0.20f, 0.15f, 0.095f, 0.82f);
            return new Color(0.12f, 0.10f, 0.085f, 0.56f);
        }

        private static Color ToolbarIconColor(int index)
        {
            switch (index)
            {
                case 0: return new Color(0.75f, 0.52f, 0.32f, 1f);
                case 1: return new Color(0.78f, 0.68f, 0.42f, 1f);
                case 2: return new Color(0.55f, 0.72f, 0.48f, 1f);
                case 3: return new Color(0.46f, 0.62f, 0.78f, 1f);
                case 4: return new Color(0.68f, 0.55f, 0.78f, 1f);
                default: return new Color(0.82f, 0.78f, 0.66f, 1f);
            }
        }

        private static string NextCameraMode(string mode)
        {
            if (string.Equals(mode, "off", StringComparison.OrdinalIgnoreCase))
                return "preview";
            if (string.Equals(mode, "preview", StringComparison.OrdinalIgnoreCase))
                return "photo_ready";
            if (string.Equals(mode, "photo_ready", StringComparison.OrdinalIgnoreCase))
                return "capture_locked";
            return "off";
        }

        private static string NormalizeCameraMode(string mode)
        {
            if (string.Equals(mode, "preview", StringComparison.OrdinalIgnoreCase))
                return "preview";
            if (string.Equals(mode, "photo_ready", StringComparison.OrdinalIgnoreCase))
                return "photo_ready";
            if (string.Equals(mode, "capture_locked", StringComparison.OrdinalIgnoreCase))
                return "capture_locked";
            return "off";
        }

        private static string NextXrHandMode(string mode)
        {
            if (string.Equals(mode, "off", StringComparison.OrdinalIgnoreCase))
                return "tracking";
            if (string.Equals(mode, "tracking", StringComparison.OrdinalIgnoreCase))
                return "gesture_select";
            return "off";
        }

        private static string AwarenessShortLabel(string policy)
        {
            if (string.Equals(policy, "AWARE_SILENT", StringComparison.OrdinalIgnoreCase))
                return "silent";
            if (string.Equals(policy, "AWARE_REACT", StringComparison.OrdinalIgnoreCase))
                return "react";
            return "record";
        }

        private static string WorkspacePolicyLabel(string layoutKind)
        {
            if (string.Equals(layoutKind, "2d_workspace", StringComparison.OrdinalIgnoreCase))
                return "  voice/no video";
            if (string.Equals(layoutKind, "ar_workspace", StringComparison.OrdinalIgnoreCase)
                || string.Equals(layoutKind, "ar_companion", StringComparison.OrdinalIgnoreCase))
                return "  full AR";
            return "";
        }

        private void ClearPendingCompactControls()
        {
            _pendingCameraMode = "";
            _pendingAwarenessPolicy = "";
            _pendingXrHandMode = "";
        }

        private static string PendingOrCurrentLabel(string current, string pending, string fallback)
        {
            return string.IsNullOrWhiteSpace(pending)
                ? ShortLabel(current, fallback, 18)
                : "...";
        }

        private static string ToolStatusForMenu(string status, string flagOffLabel)
        {
            if (string.IsNullOrWhiteSpace(status)) return flagOffLabel;
            if (status.Contains("dev_flag_off")) return flagOffLabel;
            if (status.Contains("http_missing")) return status + " / check App HTTP";
            return status;
        }

        private static bool ToolStatusLooksOk(string status)
        {
            if (string.IsNullOrWhiteSpace(status)) return false;
            return !status.Contains("missing")
                   && !status.Contains("failed")
                   && !status.Contains("dev_flag_off")
                   && !status.Contains("not_phone_safe");
        }

        private string AudioRouteStatusLabel()
        {
            if (audioRouteManager != null)
            {
                var snapshot = audioRouteManager.CurrentSnapshot;
                string managerStatus = "in " + AudioRouteLabel(audioRouteManager.CurrentPolicy.RouteName)
                                       + " / src " + AudioRouteSourceLabel(audioRouteManager.LastDetectionSource);
                if (snapshot != null)
                {
                    managerStatus = "in " + AudioRouteLabel(snapshot.input_route)
                                    + " / out " + AudioRouteLabel(snapshot.output_route)
                                    + " / " + snapshot.recommended_sample_rate_hz + "Hz"
                                    + " / " + AudioRouteSourceLabel(snapshot.source);
                    if (!string.IsNullOrWhiteSpace(snapshot.audio_focus))
                        managerStatus += " / focus " + ShortLabel(snapshot.audio_focus, "focus", 12);
                }
                if (!string.IsNullOrWhiteSpace(audioRouteManager.LastError))
                    managerStatus += " / local fail " + ShortLabel(audioRouteManager.LastError, "error", 18);
                return managerStatus;
            }

            if (audioRouteReporter == null)
            {
                if (audioRouteDetector != null)
                    return "local out " + AudioRouteLabel(audioRouteDetector.CurrentPolicy.RouteName)
                           + " / " + audioRouteDetector.CurrentPolicy.PreferredSampleRate + "Hz";
                return "route unknown";
            }

            string reporterStatus = "in " + AudioRouteLabel(audioRouteReporter.LastInputRoute)
                                    + " / out " + AudioRouteLabel(audioRouteReporter.LastOutputRoute)
                                    + " / " + audioRouteReporter.LastPreferredSampleRate + "Hz"
                                    + " / " + AudioRouteSourceLabel(audioRouteReporter.LastDetectionSource);
            if (audioRouteReporter.ReportPending)
                return reporterStatus + " / pending";
            if (!string.IsNullOrWhiteSpace(audioRouteReporter.LastReportError))
                return reporterStatus + " / fail " + ShortLabel(audioRouteReporter.LastReportError, "error", 20);
            if (audioRouteReporter.ReportSuccessCount > 0)
                return reporterStatus + " / synced";
            return reporterStatus + " / not sent";
        }

        private string MicrophoneStatusLabel()
        {
            if (microphonePublisher == null)
                return "publisher missing";

            string pref = string.IsNullOrWhiteSpace(microphonePublisher.PreferredDevice)
                ? "auto"
                : "manual " + microphonePublisher.PreferredDevice;
            string selected = string.IsNullOrWhiteSpace(microphonePublisher.SelectedDevice)
                ? "not published"
                : microphonePublisher.SelectedDevice;
            string status = string.IsNullOrWhiteSpace(microphonePublisher.LastManualDeviceStatus)
                ? "auto"
                : microphonePublisher.LastManualDeviceStatus;
            return pref
                   + " / selected " + selected
                   + " / devices " + microphonePublisher.AvailableDeviceCount
                   + " / " + status;
        }

        private string MicrophonePreferenceShortLabel()
        {
            if (microphonePublisher == null)
                return "missing";
            if (string.IsNullOrWhiteSpace(microphonePublisher.PreferredDevice))
                return "auto";
            return ShortLabel(microphonePublisher.PreferredDevice, "manual", 20);
        }

        private string AudioRouteShortLabel()
        {
            if (audioRouteManager != null)
                return AudioRouteLabel(audioRouteManager.CurrentPolicy.RouteName);
            if (audioRouteReporter == null)
                return "unknown";
            return AudioRouteLabel(audioRouteReporter.LastOutputRoute);
        }

        private static string AudioRouteSourceLabel(string source)
        {
            if (string.Equals(source, "get_devices", StringComparison.OrdinalIgnoreCase))
                return "devices";
            if (string.Equals(source, "legacy_flags", StringComparison.OrdinalIgnoreCase))
                return "legacy";
            if (string.Equals(source, "android_error", StringComparison.OrdinalIgnoreCase))
                return "error";
            return ShortLabel(source, "unknown", 10);
        }

        private static string AudioRouteLabel(string route)
        {
            if (string.Equals(route, "system_default_microphone", StringComparison.OrdinalIgnoreCase))
                return "system";
            if (string.Equals(route, "bluetooth_sco", StringComparison.OrdinalIgnoreCase))
                return "bt-sco";
            if (string.Equals(route, "bluetooth_a2dp", StringComparison.OrdinalIgnoreCase))
                return "bt-a2dp";
            if (string.Equals(route, "wired_headset", StringComparison.OrdinalIgnoreCase))
                return "wired";
            return ShortLabel(route, "unknown", 12);
        }

        private string FindPersonaLabel(string personaId)
        {
            if (string.IsNullOrWhiteSpace(personaId)) return "";
            foreach (var persona in _personas)
            {
                if (persona == null) continue;
                if (string.Equals(persona.persona_id, personaId, StringComparison.OrdinalIgnoreCase))
                    return persona.display_name;
            }
            return "";
        }

        private string FindLineProfileLabel(string lineProfileId)
        {
            if (string.IsNullOrWhiteSpace(lineProfileId)) return "";
            foreach (var profile in _lineProfiles)
            {
                if (profile == null) continue;
                if (string.Equals(profile.line_profile_id, lineProfileId, StringComparison.OrdinalIgnoreCase))
                    return profile.display_name;
            }
            return "";
        }

        private static string SelectorLabel(string displayName, string id, int optionCount)
        {
            string value = string.IsNullOrWhiteSpace(displayName) ? id : displayName;
            if (string.IsNullOrWhiteSpace(value)) value = "loading";
            if (optionCount > 0) value += " (" + optionCount + ")";
            return value;
        }

        private static string ShortLabel(string primary, string fallback, int max)
        {
            string text = string.IsNullOrWhiteSpace(primary) ? (fallback ?? "") : primary;
            text = text.Trim();
            if (text.Length <= max) return text;
            return text.Substring(0, Mathf.Max(1, max - 3)) + "...";
        }

        private static string SafeName(string value)
        {
            if (string.IsNullOrWhiteSpace(value)) return "empty";
            var chars = value.ToCharArray();
            for (int i = 0; i < chars.Length; i++)
            {
                if (!char.IsLetterOrDigit(chars[i]) && chars[i] != '_' && chars[i] != '-')
                    chars[i] = '_';
            }
            return new string(chars);
        }
    }
}
