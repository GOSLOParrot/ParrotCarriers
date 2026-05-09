using System.Collections;
using System.Collections.Generic;
using ParrotApp.Attention;
using ParrotApp.Config;
using ParrotApp.Hands;
using ParrotApp.Lifecycle;
using ParrotApp.Parrot;
using ParrotApp.Photo;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem.UI;
#endif

namespace ParrotApp.UI
{
    /// <summary>
    /// Runtime-built App V1 Meta UI shell.
    ///
    /// The shell owns only visible app controls: startup/menu surfaces, a
    /// low-obstruction HUD, a wood pull-out tool cabinet, draggable Focus and
    /// BBox overlays, the 2D workdesk, and Nanobot paper notes. Camera pixels,
    /// attention events, and hand reflexes stay in the existing controllers.
    /// </summary>
    [DisallowMultipleComponent]
    public class AppV1MetaUiController : MonoBehaviour
    {
        [Header("Startup and existing tool controllers")]
        [SerializeField] private AppStartupFlowController startupFlow;
        [SerializeField] private PhotoController photoController;
        [SerializeField] private FocusController focusController;
        [SerializeField] private BBoxController bboxController;
        [SerializeField] private HandGestureSource handGestureSource;
        [SerializeField] private ParrotController parrotController;

        [Header("Optional sprites")]
        [SerializeField] private Sprite woodDrawerSprite;
        [SerializeField] private Sprite woodButtonSprite;
        [SerializeField] private Sprite smallPaperNoteSprite;
        [SerializeField] private Sprite filledPaperNoteSprite;
        [SerializeField] private Sprite nekoClawSprite;

        private const float ReferenceWidth = 1080f;
        private const float ReferenceHeight = 1920f;

        private Canvas _canvas;
        private RectTransform _startupSurface;
        private RectTransform _transitionSurface;
        private RectTransform _mainSurface;
        private RectTransform _toolDrawer;
        private RectTransform _settingsPanel;
        private RectTransform _cameraOverlay;
        private RectTransform _cameraProPanel;
        private RectTransform _cameraTransitionSlot;
        private RectTransform _workspace;
        private RectTransform _noteStack;
        private RectTransform _activePaperNote;
        private RectTransform _paperDropTargets;
        private RectTransform _trashDropTarget;
        private RectTransform _workdeskDropTarget;
        private RectTransform _parrotJoystickPad;
        private RectTransform _parrotJoystickKnob;
        private RectTransform _magnifierOverlay;
        private RectTransform _magnifierSettings;
        private RectTransform _bboxOverlay;
        private RectTransform _bboxResizeHandle;
        private Text _startupStatus;
        private Text _transitionText;
        private Text _hudText;
        private Text _settingsStatus;
        private Text _cameraLabel;
        private Text _cameraProLabel;
        private Text _cameraTransitionText;
        private Text _cameraZoomLabel;
        private Text _cameraExposureLabel;
        private Text _workspaceText;
        private Text _noteText;
        private Text _paperNoteStateText;
        private Text _paperDropStatusText;
        private Text _parrotWalkLabel;
        private Text _magnifierLabel;
        private Text _bboxLabel;
        private Slider _magnifierSlider;
        private Image _activePaperNoteImage;
        private Outline _paperNoteOutline;

        private bool _drawerOpen;
        private bool _settingsOpen;
        private bool _cameraOpen;
        private bool _cameraProOpen;
        private bool _workspaceOpen;
        private bool _magnifierOpen;
        private bool _magnifierSettingsOpen;
        private bool _bboxOpen;
        private bool _gosloPlaced;
        private bool _paperNoteSelected;
        private bool _parrotWalking;
        private int _noteCount;
        private int _trashCount;
        private int _workdeskDropCount;
        private int _photoRequestCount;
        private int _cameraFilterIndex;
        private float _paperNoteScale = 1f;
        private float _cameraZoom = 1f;
        private float _cameraExposure;
        private float _magnifierScale = 2f;
        private Vector2 _paperInboxPosition;
        private Vector2 _parrotWalkInput;
        private string _capabilityMode = AppCapabilityModeNames.FullARCompanion;
        private string _dialogueState = "waiting_for_placement";
        private string _awarenessMode = "AWARE_SILENT";
        private string _cameraMode = "off";
        private string _activeFocusId = "";
        private string _activeBBoxId = "";
        private string _activePaperTitle = "";
        private string _activePaperBody = "";
        private string _activePaperKind = "system_popup";
        private string _activePaperState = "inbox";
        private readonly string[] _cameraFilters = { "Clear", "Warm", "Noir", "Soft" };
        private readonly List<string> _localDocuments = new();
        private readonly List<string> _trashDocuments = new();

        void Awake()
        {
            ResolveDependencies();
        }

        void OnEnable()
        {
            if (startupFlow != null)
            {
                startupFlow.OnTransitionStarted += OnStartupTransitionStarted;
                startupFlow.OnMainUiReady += OnStartupMainUiReady;
                startupFlow.OnStartupFailed += OnStartupFailed;
            }
        }

        void OnDisable()
        {
            if (startupFlow != null)
            {
                startupFlow.OnTransitionStarted -= OnStartupTransitionStarted;
                startupFlow.OnMainUiReady -= OnStartupMainUiReady;
                startupFlow.OnStartupFailed -= OnStartupFailed;
            }
        }

        void Start()
        {
            EnsureEventSystem();
            BuildUi();
            ShowStartup("Ready. Choose Start AR or Local Preview.");
            AddPaperNote("Nanobot inbox ready", "Waiting for the first report.");
            RefreshHud();
        }

        void Update()
        {
            TickPaperDropTargetWiggle();
            TickParrotJoystick();
        }

        private void ResolveDependencies()
        {
            if (startupFlow == null) startupFlow = FindObjectOfType<AppStartupFlowController>();
            if (photoController == null) photoController = PhotoController.Instance;
            if (focusController == null) focusController = FocusController.Instance;
            if (bboxController == null) bboxController = BBoxController.Instance;
            if (handGestureSource == null) handGestureSource = FindObjectOfType<HandGestureSource>();

            if (photoController == null) photoController = FindObjectOfType<PhotoController>();
            if (focusController == null) focusController = FindObjectOfType<FocusController>();
            if (bboxController == null) bboxController = FindObjectOfType<BBoxController>();
            if (parrotController == null) parrotController = FindObjectOfType<ParrotController>();
        }

        private void BuildUi()
        {
            _canvas = new GameObject("AppV1MetaCanvas").AddComponent<Canvas>();
            _canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            _canvas.sortingOrder = 50;
            var scaler = _canvas.gameObject.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(ReferenceWidth, ReferenceHeight);
            scaler.matchWidthOrHeight = 0.5f;
            _canvas.gameObject.AddComponent<GraphicRaycaster>();

            _startupSurface = BuildStartupSurface();
            _transitionSurface = BuildTransitionSurface();
            _mainSurface = CreateTransparentRoot("MainSurface", _canvas.transform);
            BuildMainSurface(_mainSurface);
        }

        private RectTransform BuildStartupSurface()
        {
            var surface = CreatePanel(
                "StartupSurface",
                _canvas.transform,
                new Color(0.04f, 0.045f, 0.06f, 0.96f));
            Stretch(surface, Vector2.zero, Vector2.zero);

            var title = CreateText("StartupTitle", surface, "GOSLO PARROT", 44, TextAnchor.MiddleCenter);
            Anchor(title.rectTransform, CenterTop(), CenterTop(), CenterTop(), new Vector2(0, -220), new Vector2(620, 90));

            var subtitle = CreateText(
                "StartupSubtitle",
                surface,
                "Mansion AR / App V1",
                22,
                TextAnchor.MiddleCenter);
            Anchor(subtitle.rectTransform, CenterTop(), CenterTop(), CenterTop(), new Vector2(0, -294), new Vector2(520, 48));

            _startupStatus = CreateText(
                "StartupStatus",
                surface,
                "",
                18,
                TextAnchor.MiddleCenter);
            Anchor(_startupStatus.rectTransform, CenterTop(), CenterTop(), CenterTop(), new Vector2(0, -388), new Vector2(720, 96));

            AddSurfaceButton(surface, "START AR", new Vector2(0, -520), StartArFlow);
            AddSurfaceButton(surface, "LOCAL PREVIEW", new Vector2(0, -590), StartLocalPreview);
            AddSurfaceButton(surface, "SILENT SESSION", new Vector2(-170, -676), () => ApplyCapability("SessionOnlySilent"));
            AddSurfaceButton(surface, "VOICE ONLY", new Vector2(0, -676), () => ApplyCapability("VoiceOnlyNoVideo"));
            AddSurfaceButton(surface, "FULL AR", new Vector2(170, -676), () => ApplyCapability("FullARCompanion"));

            var footer = CreateText(
                "StartupFooter",
                surface,
                "Connection, permissions, token mint, and AR readiness stay visible here.",
                16,
                TextAnchor.MiddleCenter);
            Anchor(footer.rectTransform, CenterBottom(), CenterBottom(), CenterBottom(), new Vector2(0, 118), new Vector2(760, 60));
            return surface;
        }

        private RectTransform BuildTransitionSurface()
        {
            var surface = CreatePanel(
                "StartupTransitionSurface",
                _canvas.transform,
                new Color(0.025f, 0.025f, 0.032f, 0.97f));
            Stretch(surface, Vector2.zero, Vector2.zero);

            var title = CreateText("TransitionTitle", surface, "CONNECTING", 34, TextAnchor.MiddleCenter);
            Anchor(title.rectTransform, Center(), Center(), Center(), new Vector2(0, 120), new Vector2(520, 76));

            var barBack = CreatePanel("TransitionProgressBack", surface, new Color(0.18f, 0.16f, 0.20f, 1f));
            Anchor(barBack, Center(), Center(), Center(), new Vector2(0, 24), new Vector2(560, 30));
            var barFill = CreatePanel("TransitionProgressFill", barBack, new Color(0.55f, 0.42f, 0.92f, 1f));
            Stretch(barFill, Vector2.zero, new Vector2(-84, 0));

            _transitionText = CreateText("TransitionText", surface, "", 18, TextAnchor.MiddleCenter);
            Anchor(_transitionText.rectTransform, Center(), Center(), Center(), new Vector2(0, -72), new Vector2(720, 86));

            var localButton = AddSurfaceButton(surface, "SKIP TO LOCAL UI", new Vector2(0, -186), ShowMainUiLocal);
            localButton.gameObject.name = "TransitionSkipLocal";
            surface.gameObject.SetActive(false);
            return surface;
        }

        private void BuildMainSurface(RectTransform root)
        {
            _hudText = BuildHud(root);
            _toolDrawer = BuildToolDrawer(root);
            _settingsPanel = BuildSettingsPanel(root);
            _cameraOverlay = BuildCameraOverlay(root);
            _workspace = BuildWorkspace(root);
            _noteStack = BuildNoteStack(root);
            _paperDropTargets = BuildPaperDropTargets(root);
            _parrotJoystickPad = BuildParrotJoystick(root);
            _magnifierOverlay = BuildMagnifierOverlay(root);
            _bboxOverlay = BuildBBoxOverlay(root);

            _drawerOpen = false;
            _settingsOpen = false;
            RefreshDrawerPosition();
            root.gameObject.SetActive(false);
        }

        private Text BuildHud(RectTransform root)
        {
            var panel = CreatePanel("HUD", root, new Color(0.10f, 0.11f, 0.14f, 0.82f));
            Anchor(panel, TopLeft(), TopLeft(), TopLeft(), new Vector2(24, -24), new Vector2(330, 150));

            var text = CreateText("HUDText", panel, "", 17, TextAnchor.UpperLeft);
            Stretch(text.rectTransform, new Vector2(14, 12), new Vector2(-14, -52));

            var placed = AddSmallButton(panel, "Placed", new Vector2(-86, 20), ReportGosloPlaced);
            placed.gameObject.name = "HUD_ReportGosloPlaced";
            var drawer = AddSmallButton(panel, "Tools", new Vector2(86, 20), ToggleDrawer);
            drawer.gameObject.name = "HUD_ToggleToolCabinet";
            return text;
        }

        private RectTransform BuildToolDrawer(RectTransform root)
        {
            var drawer = CreatePanel(
                "ToolCabinet_WoodDrawer",
                root,
                new Color(0.32f, 0.20f, 0.12f, 0.95f),
                woodDrawerSprite);
            Anchor(drawer, BottomRight(), BottomRight(), BottomRight(), new Vector2(-24, 24), new Vector2(354, 520));

            CreateText("ToolCabinetTitle", drawer, "TOOLS", 20, TextAnchor.MiddleCenter)
                .rectTransform.anchoredPosition = new Vector2(0, 226);

            float y = 172;
            AddToolButton(drawer, "Settings", y, ToggleSettings);
            y -= 54;
            AddToolButton(drawer, "Camera", y, ToggleCameraPreview);
            y -= 54;
            AddToolButton(drawer, "Capture", y, CapturePhoto);
            y -= 54;
            AddToolButton(drawer, "Magnifier", y, ToggleMagnifier);
            y -= 54;
            AddToolButton(drawer, "BoundaryBox", y, ToggleBBox);
            y -= 54;
            AddToolButton(drawer, "Workdesk", y, ToggleWorkspace);
            y -= 54;
            AddToolButton(drawer, "Notes", y, SpawnNanobotNote);
            y -= 54;
            AddToolButton(drawer, "XRHand", y, FireHandBranchGesture);

            var tab = AddToolButton(drawer, "<", 272, ToggleDrawer);
            Anchor(tab.GetComponent<RectTransform>(), LeftCenter(), LeftCenter(), LeftCenter(), new Vector2(-34, 0), new Vector2(34, 82));
            return drawer;
        }

        private RectTransform BuildSettingsPanel(RectTransform root)
        {
            var panel = CreatePanel("AppV1SettingsDialoguePanel", root, new Color(0.045f, 0.048f, 0.060f, 0.92f));
            Anchor(panel, TopLeft(), TopLeft(), TopLeft(), new Vector2(24, -190), new Vector2(420, 504));

            var title = CreateText("SettingsDialogueTitle", panel, "SESSION", 20, TextAnchor.MiddleLeft);
            Anchor(title.rectTransform, TopLeft(), TopLeft(), TopLeft(), new Vector2(22, -20), new Vector2(220, 42));

            AddCameraHudButton(panel, "x", "SettingsDialogueClose", TopRight(), new Vector2(-20, -18), new Vector2(44, 34), ToggleSettings);

            _settingsStatus = CreateText("SettingsDialogueStatus", panel, "", 15, TextAnchor.UpperLeft);
            Stretch(_settingsStatus.rectTransform, new Vector2(22, 72), new Vector2(-22, -208));

            AddSettingsButton(panel, "Quiet", new Vector2(-128, 154), () => ApplyCapability(AppCapabilityModeNames.SessionOnlySilent));
            AddSettingsButton(panel, "Voice", new Vector2(0, 154), () => ApplyCapability(AppCapabilityModeNames.VoiceOnlyNoVideo));
            AddSettingsButton(panel, "Full AR", new Vector2(128, 154), () => ApplyCapability(AppCapabilityModeNames.FullARCompanion));
            AddSettingsButton(panel, "SceneReady", new Vector2(-128, 104), ReportSceneReadyFromSettings);
            AddSettingsButton(panel, "Placed", new Vector2(0, 104), ReportGosloPlaced);
            AddSettingsButton(panel, "Aware", new Vector2(128, 104), ToggleAwarenessMode);
            AddSettingsButton(panel, "Workdesk", new Vector2(-64, 54), ToggleWorkspace);
            AddSettingsButton(panel, "Notes", new Vector2(64, 54), SpawnNanobotNote);

            var footer = CreateText(
                "SettingsRealDeviceFooter",
                panel,
                "Real-device smoke: use LAN host, token mint, LiveKit, Brain upload, AR tracking.",
                13,
                TextAnchor.MiddleLeft);
            Anchor(footer.rectTransform, BottomCenter(), BottomCenter(), BottomCenter(), new Vector2(0, 20), new Vector2(360, 44));

            panel.gameObject.SetActive(false);
            RefreshSettingsPanel();
            return panel;
        }

        private RectTransform BuildCameraOverlay(RectTransform root)
        {
            var overlay = CreateTransparentRoot("CameraModeOverlay_TransparentWysiwyg", root);

            // Camera mode is deliberately WYSIWYG: Unity does not draw a preview
            // frame over the AR camera feed. The thin edges only reserve safe
            // space for touch controls while PhotoController still owns pixels.
            var topEdge = CreatePanel("CameraModeTinyTopEdge", overlay, new Color(0.01f, 0.012f, 0.016f, 0.32f));
            Anchor(topEdge, CenterTop(), CenterTop(), CenterTop(), Vector2.zero, new Vector2(0, 58));
            topEdge.anchorMin = new Vector2(0, 1);
            topEdge.anchorMax = new Vector2(1, 1);

            var bottomEdge = CreatePanel("CameraModeTinyBottomEdge", overlay, new Color(0.01f, 0.012f, 0.016f, 0.34f));
            Anchor(bottomEdge, CenterBottom(), CenterBottom(), CenterBottom(), Vector2.zero, new Vector2(0, 96));
            bottomEdge.anchorMin = new Vector2(0, 0);
            bottomEdge.anchorMax = new Vector2(1, 0);

            _cameraTransitionSlot = CreatePanel("CameraModeTransitionSlot", overlay, new Color(0.02f, 0.024f, 0.032f, 0.40f));
            Anchor(_cameraTransitionSlot, Center(), Center(), Center(), new Vector2(0, 160), new Vector2(360, 56));
            _cameraTransitionText = CreateText("CameraModeTransitionText", _cameraTransitionSlot, "", 18, TextAnchor.MiddleCenter);
            Stretch(_cameraTransitionText.rectTransform, new Vector2(14, 6), new Vector2(-14, -6));
            _cameraTransitionSlot.gameObject.SetActive(false);

            _cameraLabel = CreateText("CameraModeLabel", overlay, "", 16, TextAnchor.MiddleLeft);
            Anchor(_cameraLabel.rectTransform, TopLeft(), TopLeft(), TopLeft(), new Vector2(24, -14), new Vector2(300, 46));

            AddCameraHudButton(overlay, "x", "CameraModeCloseButton", TopRight(), new Vector2(-28, -12), new Vector2(48, 38), CloseCameraOverlay);
            AddCameraHudButton(overlay, "gear", "CameraModeSettingsButton", TopRight(), new Vector2(-84, -12), new Vector2(68, 38), ToggleCameraProSettings);

            _cameraZoomLabel = CreateText("CameraZoomLabel", overlay, "ZOOM\n1.0x", 15, TextAnchor.MiddleCenter);
            Anchor(_cameraZoomLabel.rectTransform, LeftCenter(), LeftCenter(), LeftCenter(), new Vector2(46, -88), new Vector2(76, 54));
            AddCameraRail(overlay, "CameraGestureRail_Zoom", LeftCenter(), new Vector2(42, 86), 0.5f, 4f, _cameraZoom, SetCameraZoom);

            _cameraExposureLabel = CreateText("CameraExposureLabel", overlay, "EV\n0.0", 15, TextAnchor.MiddleCenter);
            Anchor(_cameraExposureLabel.rectTransform, RightCenter(), RightCenter(), RightCenter(), new Vector2(-46, -88), new Vector2(76, 54));
            AddCameraRail(overlay, "CameraExposureRail", RightCenter(), new Vector2(-42, 86), -2f, 2f, _cameraExposure, SetCameraExposure);

            var shutter = AddCameraHudButton(
                overlay,
                "Capture",
                "CameraModeShutterButton",
                BottomCenter(),
                new Vector2(0, 22),
                new Vector2(154, 54),
                CapturePhoto);
            shutter.gameObject.name = "CameraModeShutterButton";

            _cameraProPanel = BuildCameraProSettingsPanel(overlay);
            _cameraProPanel.gameObject.SetActive(false);

            overlay.gameObject.SetActive(false);
            RefreshCameraLabel();
            return overlay;
        }

        private RectTransform BuildCameraProSettingsPanel(RectTransform overlay)
        {
            var panel = CreatePanel("CameraProSettingsPanel", overlay, new Color(0.035f, 0.04f, 0.052f, 0.88f));
            Anchor(panel, RightCenter(), RightCenter(), RightCenter(), new Vector2(-24, 12), new Vector2(316, 432));

            var title = CreateText("CameraProSettingsTitle", panel, "PRO CAMERA", 20, TextAnchor.MiddleLeft);
            Anchor(title.rectTransform, TopLeft(), TopLeft(), TopLeft(), new Vector2(20, -18), new Vector2(210, 44));
            _cameraProLabel = CreateText("CameraProSettingsState", panel, "", 15, TextAnchor.UpperLeft);
            Stretch(_cameraProLabel.rectTransform, new Vector2(20, 70), new Vector2(-20, -204));

            AddCameraHudButton(panel, "Filter", "CameraFilterButton", BottomCenter(), new Vector2(-84, 142), new Vector2(122, 38), CycleCameraFilter);
            AddCameraHudButton(panel, "Ready", "CameraReadyButton", BottomCenter(), new Vector2(84, 142), new Vector2(122, 38), () => SetCameraOverlayMode("photo_ready"));
            AddCameraHudButton(panel, "Preview", "CameraPreviewButton", BottomCenter(), new Vector2(-84, 94), new Vector2(122, 38), () => SetCameraOverlayMode("preview"));
            AddCameraHudButton(panel, "Hide UI", "CameraHideUiButton", BottomCenter(), new Vector2(84, 94), new Vector2(122, 38), ToggleCameraProSettings);

            var stamp = CreatePanel("CameraToolbox_PixelBBoxStamp", panel, new Color(0.78f, 0.74f, 0.56f, 0.94f), smallPaperNoteSprite);
            Anchor(stamp, BottomCenter(), BottomCenter(), BottomCenter(), new Vector2(0, 28), new Vector2(246, 58));
            var stampOutline = stamp.gameObject.AddComponent<Outline>();
            stampOutline.effectColor = new Color(0.12f, 0.10f, 0.08f, 0.90f);
            stampOutline.effectDistance = new Vector2(2, 2);
            var stampText = CreateText("CameraToolbox_PixelBBoxStampText", stamp, "Pixel BBox stamp slot", 14, TextAnchor.MiddleCenter);
            Stretch(stampText.rectTransform, new Vector2(8, 4), new Vector2(-8, -4));

            RefreshCameraProLabel();
            return panel;
        }

        private RectTransform BuildWorkspace(RectTransform root)
        {
            var workspace = CreatePanel("AppV1_2DWorkdesk", root, new Color(0.06f, 0.055f, 0.06f, 0.88f));
            Stretch(workspace, new Vector2(90, 190), new Vector2(-90, -170));
            workspace.gameObject.SetActive(false);

            var desk = CreatePanel("PaperDesk", workspace, new Color(0.62f, 0.48f, 0.30f, 0.98f), filledPaperNoteSprite);
            Stretch(desk, new Vector2(40, 48), new Vector2(-40, -48));

            CreateText("WorkdeskTitle", desk, "2D WORKDESK", 26, TextAnchor.UpperCenter)
                .rectTransform.anchoredPosition = new Vector2(0, -24);
            _workspaceText = CreateText("WorkdeskDocuments", desk, "", 18, TextAnchor.UpperLeft);
            Stretch(_workspaceText.rectTransform, new Vector2(36, 96), new Vector2(-36, -94));

            AddDeskButton(desk, "Accept", new Vector2(-120, -36), AcceptTopDocument);
            AddDeskButton(desk, "Dismiss", new Vector2(0, -36), DismissTopDocument);
            AddDeskButton(desk, "Archive", new Vector2(120, -36), ArchiveTopDocument);
            RefreshWorkspace();
            return workspace;
        }

        private RectTransform BuildNoteStack(RectTransform root)
        {
            var stack = CreateTransparentRoot("NanobotNoteStack", root);
            Anchor(stack, RightCenter(), RightCenter(), RightCenter(), new Vector2(-18, 0), new Vector2(280, 150));

            if (nekoClawSprite != null)
            {
                // The paw is a visual delivery prop only. Paper state stays in
                // the note/workdesk flow, and Nanobot data stays facade-owned.
                var paw = CreatePlainSprite("NekoClawReportPaw", stack, nekoClawSprite);
                Anchor(paw, CenterTop(), CenterTop(), CenterTop(), new Vector2(-78, 74), new Vector2(94, 164));
                paw.localRotation = Quaternion.Euler(0f, 0f, -8f);
            }

            var note = CreatePanel("PaperNote_DraggableSelectable", stack, new Color(0.86f, 0.78f, 0.58f, 0.98f), smallPaperNoteSprite);
            Stretch(note, Vector2.zero, Vector2.zero);
            _activePaperNote = note;
            _activePaperNoteImage = note.GetComponent<Image>();
            _paperInboxPosition = note.anchoredPosition;
            _paperNoteOutline = note.gameObject.AddComponent<Outline>();
            _paperNoteOutline.effectColor = new Color(1f, 1f, 1f, 0f);
            _paperNoteOutline.effectDistance = new Vector2(4, 4);
            AddEvent(note.gameObject, EventTriggerType.PointerClick, _ => SelectPaperNote());
            AddEvent(note.gameObject, EventTriggerType.Scroll, ev => ScalePaperNote(((PointerEventData)ev).scrollDelta.y * 0.08f));
            AddDragHandlers(note, DragPaperNote, EndDragPaperNote);
            _noteText = CreateText("PaperNoteText", note, "", 16, TextAnchor.MiddleLeft);
            Stretch(_noteText.rectTransform, new Vector2(18, 26), new Vector2(-18, -30));

            _paperNoteStateText = CreateText("PaperNoteStateText", note, "", 12, TextAnchor.LowerLeft);
            Stretch(_paperNoteStateText.rectTransform, new Vector2(18, 6), new Vector2(-18, -6));

            AddPaperScaleButton(note, "PaperNoteScaleDown", "-", new Vector2(24, -18), () => ScalePaperNote(-0.12f));
            AddPaperScaleButton(note, "PaperNoteScaleUp", "+", new Vector2(64, -18), () => ScalePaperNote(0.12f));
            return stack;
        }

        private RectTransform BuildPaperDropTargets(RectTransform root)
        {
            var rail = CreateTransparentRoot("PaperNoteDropTargets_RightRail", root);
            Anchor(rail, RightCenter(), RightCenter(), RightCenter(), new Vector2(-18, 0), new Vector2(120, 420));

            _trashDropTarget = CreatePanel("PaperDropTarget_Trash", rail, new Color(0.20f, 0.05f, 0.06f, 0.88f));
            Anchor(_trashDropTarget, CenterTop(), CenterTop(), CenterTop(), new Vector2(0, -42), new Vector2(96, 96));
            var trashOutline = _trashDropTarget.gameObject.AddComponent<Outline>();
            trashOutline.effectColor = new Color(1f, 1f, 1f, 0.90f);
            trashOutline.effectDistance = new Vector2(3, 3);
            CreateCrumpledPaperPlaceholder(_trashDropTarget);
            var trashText = CreateText("PaperDropTrashLabel", _trashDropTarget, "TRASH", 12, TextAnchor.LowerCenter);
            Stretch(trashText.rectTransform, new Vector2(4, 4), new Vector2(-4, -6));

            _workdeskDropTarget = CreatePanel("PaperDropTarget_Workdesk", rail, new Color(0.32f, 0.22f, 0.14f, 0.90f), woodButtonSprite);
            Anchor(_workdeskDropTarget, CenterBottom(), CenterBottom(), CenterBottom(), new Vector2(0, 42), new Vector2(96, 96));
            var deskOutline = _workdeskDropTarget.gameObject.AddComponent<Outline>();
            deskOutline.effectColor = new Color(1f, 1f, 1f, 0.90f);
            deskOutline.effectDistance = new Vector2(3, 3);
            var deskPaper = CreatePanel("PaperDropWorkdeskPaperIcon", _workdeskDropTarget, new Color(0.86f, 0.78f, 0.58f, 0.95f), filledPaperNoteSprite);
            Anchor(deskPaper, Center(), Center(), Center(), new Vector2(0, 6), new Vector2(48, 42));
            var deskText = CreateText("PaperDropWorkdeskLabel", _workdeskDropTarget, "DESK", 12, TextAnchor.LowerCenter);
            Stretch(deskText.rectTransform, new Vector2(4, 4), new Vector2(-4, -6));

            _paperDropStatusText = CreateText("PaperDropStatusText", rail, "", 12, TextAnchor.MiddleCenter);
            Anchor(_paperDropStatusText.rectTransform, Center(), Center(), Center(), Vector2.zero, new Vector2(110, 82));

            rail.gameObject.SetActive(false);
            return rail;
        }

        private RectTransform BuildParrotJoystick(RectTransform root)
        {
            var pad = CreatePanel("ParrotJoystick_PlaneWalkPad", root, new Color(0.035f, 0.04f, 0.055f, 0.58f));
            Anchor(pad, BottomLeft(), BottomLeft(), BottomLeft(), new Vector2(28, 28), new Vector2(176, 176));
            var outline = pad.gameObject.AddComponent<Outline>();
            outline.effectColor = new Color(1f, 1f, 1f, 0.52f);
            outline.effectDistance = new Vector2(2, 2);
            AddEvent(pad.gameObject, EventTriggerType.PointerDown, ev => DragParrotJoystick((PointerEventData)ev));
            AddEvent(pad.gameObject, EventTriggerType.PointerUp, _ => ReleaseParrotJoystick());
            AddDragHandlers(pad, DragParrotJoystick, _ => ReleaseParrotJoystick());

            _parrotJoystickKnob = CreatePanel("ParrotJoystick_Knob", pad, new Color(0.78f, 0.66f, 0.42f, 0.94f));
            Anchor(_parrotJoystickKnob, Center(), Center(), Center(), Vector2.zero, new Vector2(58, 58));
            _parrotJoystickKnob.GetComponent<Image>().raycastTarget = false;

            _parrotWalkLabel = CreateText("ParrotJoystickStatus", pad, "WALK\nidle", 13, TextAnchor.UpperCenter);
            Stretch(_parrotWalkLabel.rectTransform, new Vector2(8, 8), new Vector2(-8, -108));

            var home = AddCameraHudButton(pad, "home", "ParrotJoystickReturnHome", BottomCenter(), new Vector2(0, 8), new Vector2(72, 30), ReturnParrotToDesk);
            home.gameObject.name = "ParrotJoystick_ReturnToDesk";
            return pad;
        }

        private RectTransform BuildMagnifierOverlay(RectTransform root)
        {
            var overlay = CreatePanel("MagnifierFocusOverlay_Draggable", root, new Color(0.14f, 0.14f, 0.18f, 0.30f));
            Anchor(overlay, Center(), Center(), Center(), Vector2.zero, new Vector2(220, 220));
            var outline = overlay.gameObject.AddComponent<Outline>();
            outline.effectColor = Color.white;
            outline.effectDistance = new Vector2(4, 4);
            AddDragHandlers(overlay, DragRect, _ => ReanchorFocusFromOverlay("drag_end"));

            _magnifierLabel = CreateText("MagnifierLabel", overlay, "", 16, TextAnchor.MiddleCenter);
            Stretch(_magnifierLabel.rectTransform, new Vector2(20, 52), new Vector2(-20, -44));

            AddCornerButton(overlay, "x", new Vector2(-28, -28), CloseMagnifier);
            AddCornerButton(overlay, "gear", new Vector2(-84, -28), ToggleMagnifierSettings);

            _magnifierSettings = CreatePanel("MagnifierSettingsGearPanel", overlay, new Color(0.06f, 0.06f, 0.08f, 0.92f));
            Anchor(_magnifierSettings, BottomCenter(), BottomCenter(), BottomCenter(), new Vector2(0, 18), new Vector2(180, 72));
            var sliderGo = new GameObject("MagnificationSlider");
            sliderGo.transform.SetParent(_magnifierSettings, false);
            _magnifierSlider = sliderGo.AddComponent<Slider>();
            _magnifierSlider.minValue = 1f;
            _magnifierSlider.maxValue = 4f;
            _magnifierSlider.value = _magnifierScale;
            _magnifierSlider.onValueChanged.AddListener(SetMagnifierScale);
            Anchor(_magnifierSlider.GetComponent<RectTransform>(), Center(), Center(), Center(), new Vector2(0, -8), new Vector2(132, 24));
            _magnifierSettings.gameObject.SetActive(false);

            overlay.gameObject.SetActive(false);
            return overlay;
        }

        private RectTransform BuildBBoxOverlay(RectTransform root)
        {
            var overlay = CreatePanel("BoundaryBoxOverlay_DraggableResizable", root, new Color(0.05f, 0.08f, 0.12f, 0.22f));
            Anchor(overlay, Center(), Center(), Center(), new Vector2(0, -160), new Vector2(320, 210));
            var outline = overlay.gameObject.AddComponent<Outline>();
            outline.effectColor = Color.white;
            outline.effectDistance = new Vector2(4, 4);
            AddDragHandlers(overlay, DragRect, _ => RecreateBBox("move_end"));

            _bboxLabel = CreateText("BoundaryBoxLabel", overlay, "", 15, TextAnchor.MiddleCenter);
            Stretch(_bboxLabel.rectTransform, new Vector2(20, 36), new Vector2(-20, -36));

            AddCornerButton(overlay, "x", new Vector2(-28, -28), CloseBBox);
            AddCornerButton(overlay, "gear", new Vector2(-84, -28), () => AddPaperNote("BoundaryBox", "Drag to move. Pull the white handle to resize."));

            _bboxResizeHandle = CreatePanel("BoundaryBoxResizeHandle", overlay, Color.white);
            Anchor(_bboxResizeHandle, BottomRight(), BottomRight(), BottomRight(), new Vector2(-8, 8), new Vector2(34, 34));
            AddDragHandlers(_bboxResizeHandle, ResizeBBox, _ => RecreateBBox("resize_end"));

            overlay.gameObject.SetActive(false);
            return overlay;
        }

        private Button AddToolButton(RectTransform parent, string label, float y, UnityEngine.Events.UnityAction action)
        {
            var buttonGo = new GameObject("Tool_" + label);
            buttonGo.transform.SetParent(parent, false);
            var image = buttonGo.AddComponent<Image>();
            image.sprite = woodButtonSprite;
            image.type = woodButtonSprite != null ? Image.Type.Sliced : Image.Type.Simple;
            image.color = woodButtonSprite != null ? Color.white : new Color(0.42f, 0.27f, 0.16f, 1f);
            var button = buttonGo.AddComponent<Button>();
            button.onClick.AddListener(action);
            Anchor(button.GetComponent<RectTransform>(), CenterTop(), CenterTop(), CenterTop(), new Vector2(0, y), new Vector2(258, 42));
            var text = CreateText("Label", button.GetComponent<RectTransform>(), label, 16, TextAnchor.MiddleCenter);
            Stretch(text.rectTransform, Vector2.zero, Vector2.zero);
            return button;
        }

        private Button AddSurfaceButton(RectTransform parent, string label, Vector2 position, UnityEngine.Events.UnityAction action)
        {
            var button = AddToolButton(parent, label, 0, action);
            Anchor(button.GetComponent<RectTransform>(), CenterTop(), CenterTop(), CenterTop(), position, new Vector2(276, 54));
            return button;
        }

        private Button AddSmallButton(RectTransform parent, string label, Vector2 position, UnityEngine.Events.UnityAction action)
        {
            var button = AddToolButton(parent, label, 0, action);
            Anchor(button.GetComponent<RectTransform>(), BottomCenter(), BottomCenter(), BottomCenter(), position, new Vector2(118, 34));
            return button;
        }

        private void AddDeskButton(RectTransform parent, string label, Vector2 position, UnityEngine.Events.UnityAction action)
        {
            var btn = AddToolButton(parent, label, 0, action);
            Anchor(btn.GetComponent<RectTransform>(), BottomCenter(), BottomCenter(), BottomCenter(), position, new Vector2(106, 38));
        }

        private void AddSettingsButton(RectTransform parent, string label, Vector2 position, UnityEngine.Events.UnityAction action)
        {
            var button = AddToolButton(parent, label, 0, action);
            Anchor(button.GetComponent<RectTransform>(), BottomCenter(), BottomCenter(), BottomCenter(), position, new Vector2(112, 38));
        }

        private void AddCornerButton(RectTransform parent, string label, Vector2 anchoredPosition, UnityEngine.Events.UnityAction action)
        {
            var button = AddToolButton(parent, label, 0, action);
            button.gameObject.name = parent.name + "_" + label;
            Anchor(button.GetComponent<RectTransform>(), TopRight(), TopRight(), TopRight(), anchoredPosition, new Vector2(52, 38));
        }

        private void AddPaperScaleButton(
            RectTransform parent,
            string name,
            string label,
            Vector2 anchoredPosition,
            UnityEngine.Events.UnityAction action)
        {
            var button = AddCameraHudButton(parent, label, name, TopLeft(), anchoredPosition, new Vector2(34, 28), action);
            button.gameObject.name = name;
        }

        private Button AddCameraModeButton(RectTransform parent, string label, Vector2 position, UnityEngine.Events.UnityAction action)
        {
            var button = AddToolButton(parent, label, 0, action);
            Anchor(button.GetComponent<RectTransform>(), BottomCenter(), BottomCenter(), BottomCenter(), position, new Vector2(126, 42));
            return button;
        }

        private Button AddCameraHudButton(
            RectTransform parent,
            string label,
            string name,
            Vector2 anchor,
            Vector2 position,
            Vector2 size,
            UnityEngine.Events.UnityAction action)
        {
            var buttonGo = new GameObject(name);
            buttonGo.transform.SetParent(parent, false);
            var image = buttonGo.AddComponent<Image>();
            image.color = new Color(0.015f, 0.018f, 0.024f, 0.62f);
            var button = buttonGo.AddComponent<Button>();
            button.onClick.AddListener(action);
            Anchor(button.GetComponent<RectTransform>(), anchor, anchor, anchor, position, size);
            var text = CreateText("Label", button.GetComponent<RectTransform>(), label, 15, TextAnchor.MiddleCenter);
            Stretch(text.rectTransform, Vector2.zero, Vector2.zero);
            return button;
        }

        private void AddCameraRail(
            RectTransform parent,
            string name,
            Vector2 anchor,
            Vector2 position,
            float minValue,
            float maxValue,
            float value,
            UnityEngine.Events.UnityAction<float> action)
        {
            var rail = CreatePanel(name, parent, new Color(0.015f, 0.018f, 0.024f, 0.38f));
            Anchor(rail, anchor, anchor, anchor, position, new Vector2(46, 282));
            var slider = rail.gameObject.AddComponent<Slider>();
            slider.direction = Slider.Direction.BottomToTop;
            slider.minValue = minValue;
            slider.maxValue = maxValue;
            slider.value = value;
            slider.onValueChanged.AddListener(action);
        }

        private void AddFrameLine(RectTransform parent, string name, Vector2 anchorMin, Vector2 anchorMax)
        {
            var line = CreatePanel(name, parent, new Color(0.85f, 0.90f, 1f, 0.22f));
            line.anchorMin = anchorMin;
            line.anchorMax = anchorMax;
            line.pivot = new Vector2(0.5f, 0.5f);
            line.anchoredPosition = Vector2.zero;
            bool vertical = Mathf.Approximately(anchorMin.x, anchorMax.x);
            line.sizeDelta = vertical ? new Vector2(2, 0) : new Vector2(0, 2);
            var image = line.GetComponent<Image>();
            image.raycastTarget = false;
        }

        private RectTransform CreatePanel(string name, Transform parent, Color color, Sprite sprite = null)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var image = go.AddComponent<Image>();
            image.color = sprite == null ? color : Color.white;
            image.sprite = sprite;
            image.type = sprite != null ? Image.Type.Sliced : Image.Type.Simple;
            return go.GetComponent<RectTransform>();
        }

        private RectTransform CreateTransparentRoot(string name, Transform parent)
        {
            var root = CreatePanel(name, parent, new Color(0, 0, 0, 0));
            var image = root.GetComponent<Image>();
            image.raycastTarget = false;
            Stretch(root, Vector2.zero, Vector2.zero);
            return root;
        }

        private RectTransform CreatePlainSprite(string name, Transform parent, Sprite sprite)
        {
            var rt = CreatePanel(name, parent, Color.white, sprite);
            var image = rt.GetComponent<Image>();
            image.type = Image.Type.Simple;
            image.preserveAspect = true;
            image.raycastTarget = false;
            return rt;
        }

        private void CreateCrumpledPaperPlaceholder(RectTransform parent)
        {
            // Placeholder until a real crumpled-paper sprite is selected. Three
            // offset paper chips read as a waste-paper ball without adding a new
            // asset dependency to the v1 smoke scene.
            var a = CreatePanel("TrashCrumpledPaperPlaceholder_A", parent, new Color(0.76f, 0.68f, 0.48f, 0.95f), smallPaperNoteSprite);
            Anchor(a, Center(), Center(), Center(), new Vector2(-8, 10), new Vector2(40, 32));
            a.localRotation = Quaternion.Euler(0f, 0f, -16f);
            var b = CreatePanel("TrashCrumpledPaperPlaceholder_B", parent, new Color(0.83f, 0.76f, 0.55f, 0.95f), smallPaperNoteSprite);
            Anchor(b, Center(), Center(), Center(), new Vector2(8, 2), new Vector2(38, 34));
            b.localRotation = Quaternion.Euler(0f, 0f, 18f);
            var c = CreatePanel("TrashCrumpledPaperPlaceholder_C", parent, new Color(0.68f, 0.60f, 0.42f, 0.95f), smallPaperNoteSprite);
            Anchor(c, Center(), Center(), Center(), new Vector2(0, -8), new Vector2(36, 26));
            c.localRotation = Quaternion.Euler(0f, 0f, 4f);
        }

        private Text CreateText(string name, Transform parent, string text, int fontSize, TextAnchor anchor)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var label = go.AddComponent<Text>();
            label.text = text;
            label.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            label.fontSize = fontSize;
            label.alignment = anchor;
            label.color = new Color(0.94f, 0.90f, 0.80f, 1f);
            label.horizontalOverflow = HorizontalWrapMode.Wrap;
            label.verticalOverflow = VerticalWrapMode.Truncate;
            label.raycastTarget = false;
            label.rectTransform.sizeDelta = new Vector2(220, 36);
            return label;
        }

        private static void Anchor(
            RectTransform rt,
            Vector2 anchorMin,
            Vector2 anchorMax,
            Vector2 pivot,
            Vector2 anchoredPosition,
            Vector2 size)
        {
            rt.anchorMin = anchorMin;
            rt.anchorMax = anchorMax;
            rt.pivot = pivot;
            rt.anchoredPosition = anchoredPosition;
            rt.sizeDelta = size;
        }

        private static void Stretch(RectTransform rt, Vector2 offsetMin, Vector2 offsetMax)
        {
            rt.anchorMin = Vector2.zero;
            rt.anchorMax = Vector2.one;
            rt.offsetMin = offsetMin;
            rt.offsetMax = offsetMax;
        }

        private static void AddEvent(GameObject go, EventTriggerType type, UnityEngine.Events.UnityAction<BaseEventData> action)
        {
            var trigger = go.GetComponent<EventTrigger>() ?? go.AddComponent<EventTrigger>();
            var entry = new EventTrigger.Entry { eventID = type };
            entry.callback.AddListener(action);
            trigger.triggers.Add(entry);
        }

        private static void AddDragHandlers(
            RectTransform target,
            UnityEngine.Events.UnityAction<PointerEventData> onDrag,
            UnityEngine.Events.UnityAction<PointerEventData> onEndDrag)
        {
            AddEvent(target.gameObject, EventTriggerType.Drag, ev => onDrag((PointerEventData)ev));
            AddEvent(target.gameObject, EventTriggerType.EndDrag, ev => onEndDrag((PointerEventData)ev));
        }

        private static void DragRect(PointerEventData eventData)
        {
            if (eventData.pointerDrag == null) return;
            var rt = eventData.pointerDrag.GetComponent<RectTransform>();
            if (rt == null) return;
            rt.anchoredPosition += eventData.delta;
        }

        private void DragPaperNote(PointerEventData eventData)
        {
            SelectPaperNote();
            if (_activePaperNote == null) return;
            _activePaperNote.anchoredPosition += eventData.delta;
            RefreshPaperDropStatus(eventData);
        }

        private void EndDragPaperNote(PointerEventData eventData)
        {
            if (_activePaperNote == null) return;
            if (PointerInside(_trashDropTarget, eventData))
            {
                MovePaperNoteToTrash();
                return;
            }
            if (PointerInside(_workdeskDropTarget, eventData))
            {
                MovePaperNoteToWorkdesk();
                return;
            }
            RefreshPaperDropStatus(eventData);
        }

        private void DragParrotJoystick(PointerEventData eventData)
        {
            if (_parrotJoystickPad == null || _parrotJoystickKnob == null) return;
            RectTransformUtility.ScreenPointToLocalPointInRectangle(
                _parrotJoystickPad,
                eventData.position,
                null,
                out Vector2 localPoint);
            float radius = Mathf.Min(_parrotJoystickPad.rect.width, _parrotJoystickPad.rect.height) * 0.34f;
            Vector2 clamped = Vector2.ClampMagnitude(localPoint, radius);
            _parrotJoystickKnob.anchoredPosition = clamped;
            _parrotWalkInput = radius > 0f ? clamped / radius : Vector2.zero;
            _parrotWalking = _parrotWalkInput.sqrMagnitude > 0.01f;
            RefreshParrotWalkLabel();
        }

        private void ReleaseParrotJoystick()
        {
            _parrotWalkInput = Vector2.zero;
            _parrotWalking = false;
            if (_parrotJoystickKnob != null) _parrotJoystickKnob.anchoredPosition = Vector2.zero;
            if (parrotController != null) parrotController.EndPlaneWalk();
            RefreshParrotWalkLabel();
        }

        private void ReturnParrotToDesk()
        {
            ResolveDependencies();
            if (parrotController != null)
            {
                parrotController.ReturnToPlaneWalkHome();
                AddPaperNote("Parrot movement", "Return-to-desk command sent through ParrotController.");
            }
            else
            {
                AddPaperNote("Parrot movement", "ParrotController missing; joystick remains a UI smoke control.");
            }
            RefreshParrotWalkLabel();
        }

        private void ResizeBBox(PointerEventData eventData)
        {
            if (_bboxOverlay == null) return;
            Vector2 size = _bboxOverlay.sizeDelta;
            size.x = Mathf.Clamp(size.x + eventData.delta.x, 120f, 720f);
            size.y = Mathf.Clamp(size.y - eventData.delta.y, 90f, 520f);
            _bboxOverlay.sizeDelta = size;
            RefreshBBoxLabel();
        }

        private static bool PointerInside(RectTransform target, PointerEventData eventData)
        {
            return target != null
                && target.gameObject.activeInHierarchy
                && RectTransformUtility.RectangleContainsScreenPoint(target, eventData.position, null);
        }

        private void SelectPaperNote()
        {
            _paperNoteSelected = true;
            if (_paperDropTargets != null) _paperDropTargets.gameObject.SetActive(true);
            if (_paperNoteOutline != null) _paperNoteOutline.effectColor = Color.white;
            RefreshPaperNoteVisual();
            RefreshPaperDropStatus();
        }

        private void DeselectPaperNote()
        {
            _paperNoteSelected = false;
            if (_paperDropTargets != null) _paperDropTargets.gameObject.SetActive(false);
            if (_paperNoteOutline != null) _paperNoteOutline.effectColor = new Color(1f, 1f, 1f, 0f);
            RefreshPaperNoteVisual();
        }

        private void ScalePaperNote(float delta)
        {
            _paperNoteScale = Mathf.Clamp(_paperNoteScale + delta, 0.78f, 1.65f);
            if (_activePaperNote != null) _activePaperNote.localScale = Vector3.one * _paperNoteScale;
            SelectPaperNote();
        }

        private void MovePaperNoteToTrash()
        {
            if (string.IsNullOrEmpty(_activePaperTitle)) return;
            _trashCount++;
            _activePaperState = "trash";
            string doc = _activePaperTitle + ": " + _activePaperBody;
            _trashDocuments.Insert(0, doc);
            _localDocuments.Remove(doc);
            RestorePaperNoteInboxPosition();
            DeselectPaperNote();
            RefreshWorkspace();
            RefreshHud();
        }

        private void MovePaperNoteToWorkdesk()
        {
            if (string.IsNullOrEmpty(_activePaperTitle)) return;
            _workdeskDropCount++;
            _activePaperState = "workdesk";
            _workspaceOpen = true;
            if (_workspace != null) _workspace.gameObject.SetActive(true);
            RestorePaperNoteInboxPosition();
            DeselectPaperNote();
            RefreshWorkspace();
            RefreshHud();
        }

        private void RestorePaperNoteInboxPosition()
        {
            if (_activePaperNote == null) return;
            _activePaperNote.anchoredPosition = _paperInboxPosition;
        }

        private void RefreshPaperDropStatus(PointerEventData eventData = null)
        {
            if (_paperDropStatusText == null) return;
            string hover = "";
            if (eventData != null && PointerInside(_trashDropTarget, eventData)) hover = "\nrelease: trash";
            if (eventData != null && PointerInside(_workdeskDropTarget, eventData)) hover = "\nrelease: desk";
            _paperDropStatusText.text =
                "paper\n" +
                _activePaperState + "\n" +
                "trash " + _trashCount + " / desk " + _workdeskDropCount +
                hover;
        }

        private void RefreshPaperNoteVisual()
        {
            if (_activePaperNoteImage != null)
            {
                _activePaperNoteImage.sprite = SpriteForPaperKind(_activePaperKind);
                _activePaperNoteImage.color = ColorForPaperKind(_activePaperKind);
            }
            if (_paperNoteStateText != null)
            {
                _paperNoteStateText.text =
                    _activePaperKind + " / " + _activePaperState + " / " +
                    _paperNoteScale.ToString("0.0") + "x";
            }
        }

        private Sprite SpriteForPaperKind(string kind)
        {
            if (kind == "calendar_draft" || kind == "workdesk_alert") return filledPaperNoteSprite ?? smallPaperNoteSprite;
            return smallPaperNoteSprite ?? filledPaperNoteSprite;
        }

        private static Color ColorForPaperKind(string kind)
        {
            switch (kind)
            {
                case "nanobot_report":
                    return new Color(0.91f, 0.78f, 0.48f, 0.98f);
                case "calendar_draft":
                    return new Color(0.70f, 0.82f, 0.92f, 0.98f);
                case "workdesk_alert":
                    return new Color(0.88f, 0.72f, 0.88f, 0.98f);
                default:
                    return new Color(0.86f, 0.78f, 0.58f, 0.98f);
            }
        }

        private void TickPaperDropTargetWiggle()
        {
            if (!_paperNoteSelected || _paperDropTargets == null || !_paperDropTargets.gameObject.activeSelf) return;
            float angle = Mathf.Sin(Time.unscaledTime * 12f) * 2.4f;
            if (_trashDropTarget != null) _trashDropTarget.localRotation = Quaternion.Euler(0f, 0f, angle);
            if (_workdeskDropTarget != null) _workdeskDropTarget.localRotation = Quaternion.Euler(0f, 0f, -angle);
        }

        private void TickParrotJoystick()
        {
            if (!_parrotWalking || _parrotWalkInput.sqrMagnitude <= 0.01f) return;
            if (parrotController != null)
            {
                parrotController.WalkOnPlane(_parrotWalkInput, Time.deltaTime);
            }
        }

        private void RefreshParrotWalkLabel()
        {
            if (_parrotWalkLabel == null) return;
            string state = _parrotWalking ? "walking" : "idle";
            _parrotWalkLabel.text = "WALK\n" + state;
        }

        private void StartArFlow()
        {
            ResolveDependencies();
            if (startupFlow == null)
            {
                StartLocalPreview();
                return;
            }
            ShowTransition("Permission gate -> token mint -> LiveKit connect.");
            startupFlow.StartDefault();
        }

        private void StartLocalPreview()
        {
            ShowTransition("Local preview. LiveKit and Brain gates are bypassed for UI smoke.");
            StartCoroutine(ShowLocalPreviewSoon());
        }

        private IEnumerator ShowLocalPreviewSoon()
        {
            yield return new WaitForSeconds(0.45f);
            ShowMainUiLocal();
        }

        private void ApplyCapability(string mode)
        {
            ResolveDependencies();
            _capabilityMode = AppCapabilityModeNames.Normalize(mode);
            _dialogueState = _capabilityMode == AppCapabilityModeNames.SessionOnlySilent
                ? "quiet_keepalive"
                : (_gosloPlaced ? "ready_after_placement" : "waiting_for_placement");
            if (startupFlow != null)
            {
                startupFlow.ApplyCapabilityMode(_capabilityMode);
                if (_mainSurface != null && _mainSurface.gameObject.activeSelf)
                {
                    AddPaperNote("Capability", "Mode requested: " + _capabilityMode + ".");
                }
                else
                {
                    ShowStartup("Capability mode requested: " + _capabilityMode);
                }
            }
            else
            {
                if (_mainSurface != null && _mainSurface.gameObject.activeSelf)
                    AddPaperNote("Capability placeholder", "Mode requested: " + _capabilityMode + ".");
                else
                    ShowStartup("Capability mode placeholder: " + _capabilityMode);
            }
            RefreshSettingsPanel();
            RefreshHud();
        }

        private void OnStartupTransitionStarted(AppStartupConfigDto _)
        {
            ShowTransition("Startup flow entered transition state.");
        }

        private void OnStartupMainUiReady(AppStartupConfigDto _)
        {
            ShowMainUi("Main UI ready. Place GOSLO before greeting.");
        }

        private void OnStartupFailed(string reason)
        {
            ShowStartup("Startup failed: " + reason + ". Check permissions or use Local Preview.");
        }

        private void ShowStartup(string message)
        {
            if (_startupSurface != null) _startupSurface.gameObject.SetActive(true);
            if (_transitionSurface != null) _transitionSurface.gameObject.SetActive(false);
            if (_mainSurface != null) _mainSurface.gameObject.SetActive(false);
            if (_startupStatus != null) _startupStatus.text = message;
        }

        private void ShowTransition(string message)
        {
            if (_startupSurface != null) _startupSurface.gameObject.SetActive(false);
            if (_transitionSurface != null) _transitionSurface.gameObject.SetActive(true);
            if (_mainSurface != null) _mainSurface.gameObject.SetActive(false);
            if (_transitionText != null) _transitionText.text = message;
        }

        private void ShowMainUiLocal()
        {
            ShowMainUi("Local AR preview. Use HUD and tool cabinet for smoke tests.");
        }

        private void ShowMainUi(string message)
        {
            if (_startupSurface != null) _startupSurface.gameObject.SetActive(false);
            if (_transitionSurface != null) _transitionSurface.gameObject.SetActive(false);
            if (_mainSurface != null) _mainSurface.gameObject.SetActive(true);
            AddPaperNote("Startup", message);
            RefreshHud();
        }

        private void ReportGosloPlaced()
        {
            ResolveDependencies();
            _gosloPlaced = true;
            _dialogueState = "ready_after_placement";
            if (startupFlow != null) startupFlow.ReportGosloPlaced();
            AddPaperNote("GOSLO placed", "Greeting gate opened after placement.");
            RefreshSettingsPanel();
            RefreshHud();
        }

        private void ToggleSettings()
        {
            _settingsOpen = !_settingsOpen;
            if (_settingsPanel != null) _settingsPanel.gameObject.SetActive(_settingsOpen);
            RefreshSettingsPanel();
            if (_settingsOpen)
            {
                AddPaperNote("Settings", "Session, dialogue gate, and real-device smoke status are visible.");
            }
        }

        private void ReportSceneReadyFromSettings()
        {
            ResolveDependencies();
            _dialogueState = _gosloPlaced ? "ready_after_placement" : "scene_ready_silent";
            if (startupFlow != null) startupFlow.ReportSceneReady();
            AddPaperNote("Scene ready", "Scene readiness reported; greeting still waits for GOSLO placement.");
            RefreshSettingsPanel();
            RefreshHud();
        }

        private void ToggleAwarenessMode()
        {
            _awarenessMode = _awarenessMode == "UNAWARE_RECORDED"
                ? "AWARE_SILENT"
                : (_awarenessMode == "AWARE_SILENT" ? "AWARE_REACT" : "UNAWARE_RECORDED");
            AddPaperNote("Awareness", _awarenessMode + " selected locally; backend policy remains facade-owned.");
            RefreshSettingsPanel();
            RefreshHud();
        }

        private void ToggleCameraPreview()
        {
            _cameraOpen = !_cameraOpen;
            if (_cameraOverlay != null) _cameraOverlay.gameObject.SetActive(_cameraOpen);
            SetCameraOverlayMode(_cameraOpen ? "preview" : "off");
            if (_cameraOpen) StartCoroutine(ShowCameraTransitionSlot("Camera mode"));
            AddPaperNote("Camera mode", _cameraOpen ? "Clean WYSIWYG capture HUD opened." : "Capture HUD closed.");
            RefreshHud();
        }

        private void CloseCameraOverlay()
        {
            _cameraOpen = false;
            _cameraProOpen = false;
            if (_cameraOverlay != null) _cameraOverlay.gameObject.SetActive(false);
            if (_cameraProPanel != null) _cameraProPanel.gameObject.SetActive(false);
            if (_cameraTransitionSlot != null) _cameraTransitionSlot.gameObject.SetActive(false);
            SetCameraOverlayMode("off");
        }

        private void SetCameraOverlayMode(string mode)
        {
            _cameraMode = mode;
            RefreshCameraLabel();
            RefreshCameraProLabel();
            RefreshSettingsPanel();
            RefreshHud();
        }

        private void ToggleCameraProSettings()
        {
            _cameraProOpen = !_cameraProOpen;
            if (_cameraProPanel != null) _cameraProPanel.gameObject.SetActive(_cameraProOpen);
            RefreshCameraProLabel();
        }

        private void SetCameraZoom(float value)
        {
            _cameraZoom = value;
            RefreshCameraLabel();
            RefreshCameraProLabel();
            RefreshSettingsPanel();
        }

        private void SetCameraExposure(float value)
        {
            _cameraExposure = value;
            RefreshCameraLabel();
            RefreshCameraProLabel();
            RefreshSettingsPanel();
        }

        private void CycleCameraFilter()
        {
            _cameraFilterIndex = (_cameraFilterIndex + 1) % _cameraFilters.Length;
            RefreshCameraProLabel();
        }

        private IEnumerator ShowCameraTransitionSlot(string label)
        {
            if (_cameraTransitionSlot == null || _cameraTransitionText == null) yield break;
            _cameraTransitionText.text = label;
            _cameraTransitionSlot.gameObject.SetActive(true);
            yield return new WaitForSeconds(0.75f);
            if (_cameraTransitionSlot != null) _cameraTransitionSlot.gameObject.SetActive(false);
        }

        private void CapturePhoto()
        {
            ResolveDependencies();
            _cameraOpen = true;
            if (_cameraOverlay != null) _cameraOverlay.gameObject.SetActive(true);
            _photoRequestCount++;
            SetCameraOverlayMode("capture_locked");
            if (photoController != null)
            {
                photoController.CapturePhoto();
                AddPaperNote("Photo requested", "PhotoController is capturing preview + HTTP asset.");
            }
            else
            {
                AddPaperNote("Photo placeholder", "PhotoController missing in scene; capture request stayed local.");
            }
            RefreshHud();
        }

        private void ToggleMagnifier()
        {
            if (_magnifierOpen) CloseMagnifier();
            else OpenMagnifier();
        }

        private void OpenMagnifier()
        {
            ResolveDependencies();
            _magnifierOpen = true;
            _magnifierOverlay.gameObject.SetActive(true);
            ReanchorFocusFromOverlay("open");
            AddPaperNote("Magnifier", "Drag the selected white outline. Gear adjusts magnification.");
        }

        private void CloseMagnifier()
        {
            if (!_magnifierOpen) return;
            _magnifierOpen = false;
            if (focusController != null && !string.IsNullOrEmpty(_activeFocusId))
            {
                focusController.ReleaseFocus(_activeFocusId);
            }
            _activeFocusId = "";
            _magnifierOverlay.gameObject.SetActive(false);
            RefreshHud();
        }

        private void ToggleMagnifierSettings()
        {
            _magnifierSettingsOpen = !_magnifierSettingsOpen;
            _magnifierSettings.gameObject.SetActive(_magnifierSettingsOpen);
        }

        private void SetMagnifierScale(float value)
        {
            _magnifierScale = value;
            if (_magnifierOverlay != null)
            {
                _magnifierOverlay.localScale = Vector3.one * Mathf.Lerp(0.88f, 1.22f, (value - 1f) / 3f);
            }
            RefreshMagnifierLabel();
        }

        private void ReanchorFocusFromOverlay(string reason)
        {
            if (!_magnifierOpen) return;
            ResolveDependencies();
            if (focusController == null)
            {
                _activeFocusId = "";
                RefreshMagnifierLabel();
                return;
            }
            if (!string.IsNullOrEmpty(_activeFocusId)) focusController.ReleaseFocus(_activeFocusId);
            _activeFocusId = focusController.AnchorFocus(
                ToNormalizedCenter(_magnifierOverlay),
                Mathf.Max(_magnifierOverlay.sizeDelta.x, _magnifierOverlay.sizeDelta.y) / ReferenceHeight,
                ToOverlayPose(_magnifierOverlay),
                "app_v1_magnifier_" + reason);
            RefreshMagnifierLabel();
            RefreshHud();
        }

        private void ToggleBBox()
        {
            if (_bboxOpen) CloseBBox();
            else OpenBBox();
        }

        private void OpenBBox()
        {
            ResolveDependencies();
            _bboxOpen = true;
            _bboxOverlay.gameObject.SetActive(true);
            RecreateBBox("open");
            AddPaperNote("BoundaryBox", "Drag the box, resize with the white handle, close with x.");
        }

        private void CloseBBox()
        {
            if (!_bboxOpen) return;
            _bboxOpen = false;
            if (bboxController != null && !string.IsNullOrEmpty(_activeBBoxId))
            {
                bboxController.RemoveBBox(_activeBBoxId);
            }
            _activeBBoxId = "";
            _bboxOverlay.gameObject.SetActive(false);
            RefreshHud();
        }

        private void RecreateBBox(string reason)
        {
            if (!_bboxOpen) return;
            ResolveDependencies();
            if (bboxController == null)
            {
                _activeBBoxId = "";
                RefreshBBoxLabel();
                return;
            }
            if (!string.IsNullOrEmpty(_activeBBoxId)) bboxController.RemoveBBox(_activeBBoxId);
            _activeBBoxId = bboxController.PlaceBBox(
                ToNormalizedCorners(_bboxOverlay),
                ToOverlayPose(_bboxOverlay),
                "app_v1_bbox_" + reason);
            RefreshBBoxLabel();
            RefreshHud();
        }

        private void ToggleWorkspace()
        {
            _workspaceOpen = !_workspaceOpen;
            _workspace.gameObject.SetActive(_workspaceOpen);
            RefreshWorkspace();
        }

        private void ToggleDrawer()
        {
            _drawerOpen = !_drawerOpen;
            RefreshDrawerPosition();
        }

        private void RefreshDrawerPosition()
        {
            if (_toolDrawer == null) return;
            _toolDrawer.anchoredPosition = _drawerOpen ? new Vector2(-24, 24) : new Vector2(306, 24);
        }

        private void SpawnNanobotNote()
        {
            AddPaperNote("Nanobot report", "Drag, scale, trash, or drop this paper into the workdesk.");
        }

        private void FireHandBranchGesture()
        {
            ResolveDependencies();
            if (handGestureSource != null)
            {
                handGestureSource.DebugFireBranchGesture();
                AddPaperNote("XRHand reflex", "index_finger_branch -> PerchOnHand local reflex.");
            }
            else
            {
                AddPaperNote("XRHand placeholder", "HandGestureSource missing. Command flow remains documented.");
            }
        }

        private void AddPaperNote(string title, string body)
        {
            _noteCount++;
            string doc = title + ": " + body;
            _localDocuments.Insert(0, doc);
            _activePaperTitle = title;
            _activePaperBody = body;
            _activePaperKind = InferPaperKind(title);
            _activePaperState = "inbox";
            _paperNoteScale = 1f;
            RestorePaperNoteInboxPosition();
            if (_activePaperNote != null) _activePaperNote.localScale = Vector3.one;
            if (_noteText != null)
            {
                _noteText.text = title + "\n" + body;
            }
            RefreshPaperNoteVisual();
            RefreshPaperDropStatus();
            RefreshWorkspace();
            RefreshHud();
        }

        private static string InferPaperKind(string title)
        {
            string lower = (title ?? "").ToLowerInvariant();
            if (lower.Contains("nanobot")) return "nanobot_report";
            if (lower.Contains("calendar")) return "calendar_draft";
            if (lower.Contains("workdesk") || lower.Contains("document")) return "workdesk_alert";
            return "system_popup";
        }

        private void AcceptTopDocument() => FinishTopDocument("accepted");
        private void DismissTopDocument() => FinishTopDocument("dismissed");
        private void ArchiveTopDocument() => FinishTopDocument("archived");

        private void FinishTopDocument(string action)
        {
            if (_localDocuments.Count == 0)
            {
                AddPaperNote("Workdesk", "No document to " + action + ".");
                return;
            }
            string doc = _localDocuments[0];
            _localDocuments.RemoveAt(0);
            AddPaperNote("Document " + action, doc);
            RefreshWorkspace();
        }

        private void RefreshHud()
        {
            if (_hudText == null) return;
            int focusCount = focusController != null ? focusController.ActiveCount : 0;
            int bboxCount = bboxController != null ? bboxController.ActiveCount : 0;
            _hudText.text =
                "GOSLO\n" +
                "Mode: " + ShortCapabilityName(_capabilityMode) + "\n" +
                "Dialogue: " + ShortDialogueState() + "\n" +
                "Camera: " + _cameraMode + " " + _cameraZoom.ToString("0.0") + "x\n" +
                "Focus " + focusCount + " / BBox " + bboxCount + "\n" +
                "Notes: " + _noteCount + " / Trash " + _trashCount;
        }

        private void RefreshSettingsPanel()
        {
            if (_settingsStatus == null) return;
            _settingsStatus.text =
                "Capability: " + _capabilityMode + "\n" +
                "Dialogue: " + _dialogueState + "\n" +
                "GOSLO placed: " + (_gosloPlaced ? "yes" : "no") + "\n" +
                "Awareness: " + _awarenessMode + "\n" +
                "Camera: " + _cameraMode + " / " + _cameraZoom.ToString("0.0") + "x / " +
                _cameraExposure.ToString("+0.0;-0.0;0.0") + " EV\n\n" +
                "SceneReady does not greet. Placed opens the greeting gate.";
        }

        private static string ShortCapabilityName(string mode)
        {
            switch (mode)
            {
                case AppCapabilityModeNames.SessionOnlySilent:
                    return "Silent";
                case AppCapabilityModeNames.VoiceOnlyNoVideo:
                    return "Voice";
                case AppCapabilityModeNames.VoiceVideoNoActionMonitor:
                    return "Voice+Cam";
                default:
                    return "Full AR";
            }
        }

        private string ShortDialogueState()
        {
            if (_dialogueState == "ready_after_placement") return "ready";
            if (_dialogueState == "quiet_keepalive") return "quiet";
            if (_dialogueState == "scene_ready_silent") return "scene ready";
            return "wait place";
        }

        private void RefreshCameraLabel()
        {
            if (_cameraLabel == null) return;
            _cameraLabel.text = _cameraMode + " / shots " + _photoRequestCount;
            if (_cameraZoomLabel != null) _cameraZoomLabel.text = "ZOOM\n" + _cameraZoom.ToString("0.0") + "x";
            if (_cameraExposureLabel != null) _cameraExposureLabel.text = "EV\n" + _cameraExposure.ToString("+0.0;-0.0;0.0");
        }

        private void RefreshCameraProLabel()
        {
            if (_cameraProLabel == null) return;
            string filter = _cameraFilters[Mathf.Clamp(_cameraFilterIndex, 0, _cameraFilters.Length - 1)];
            _cameraProLabel.text =
                "Mode: " + _cameraMode + "\n" +
                "Zoom: " + _cameraZoom.ToString("0.0") + "x\n" +
                "Exposure: " + _cameraExposure.ToString("+0.0;-0.0;0.0") + " EV\n" +
                "Filter: " + filter + "\n\n" +
                "Grid, lens, DOF, and sticker assets are slots for real-device tuning.";
        }

        private void RefreshWorkspace()
        {
            if (_workspaceText == null) return;
            if (_localDocuments.Count == 0)
            {
                _workspaceText.text = _trashDocuments.Count == 0
                    ? "No paper on the desk yet."
                    : "No active paper on the desk.\n\nTrash holds " + _trashDocuments.Count + " paper note(s).";
                return;
            }
            int count = Mathf.Min(6, _localDocuments.Count);
            _workspaceText.text =
                string.Join("\n\n", _localDocuments.GetRange(0, count)) +
                "\n\nTrash: " + _trashDocuments.Count + " paper note(s).";
        }

        private void RefreshMagnifierLabel()
        {
            if (_magnifierLabel == null) return;
            string id = string.IsNullOrEmpty(_activeFocusId) ? "local" : _activeFocusId;
            _magnifierLabel.text = "MAGNIFIER\n" + _magnifierScale.ToString("0.0") + "x\nfocus " + id;
        }

        private void RefreshBBoxLabel()
        {
            if (_bboxLabel == null) return;
            string id = string.IsNullOrEmpty(_activeBBoxId) ? "local" : _activeBBoxId;
            _bboxLabel.text = "BOUNDARY BOX\n" + Mathf.RoundToInt(_bboxOverlay.sizeDelta.x) +
                              " x " + Mathf.RoundToInt(_bboxOverlay.sizeDelta.y) + "\n" + id;
        }

        private static Vector2 ToNormalizedCenter(RectTransform rt)
        {
            return new Vector2(
                Mathf.Clamp01(0.5f + rt.anchoredPosition.x / ReferenceWidth),
                Mathf.Clamp01(0.5f + rt.anchoredPosition.y / ReferenceHeight));
        }

        private static Vector2[] ToNormalizedCorners(RectTransform rt)
        {
            Vector2 center = ToNormalizedCenter(rt);
            Vector2 half = new Vector2(rt.sizeDelta.x / ReferenceWidth, rt.sizeDelta.y / ReferenceHeight) * 0.5f;
            return new[]
            {
                new Vector2(Mathf.Clamp01(center.x - half.x), Mathf.Clamp01(center.y - half.y)),
                new Vector2(Mathf.Clamp01(center.x + half.x), Mathf.Clamp01(center.y + half.y)),
            };
        }

        private static Pose ToOverlayPose(RectTransform rt)
        {
            Vector2 c = ToNormalizedCenter(rt);
            return new Pose(new Vector3(c.x - 0.5f, c.y - 0.5f, 0.5f), Quaternion.identity);
        }

        private static void EnsureEventSystem()
        {
            if (FindObjectOfType<EventSystem>() != null) return;
            var go = new GameObject("EventSystem");
            go.AddComponent<EventSystem>();
#if ENABLE_INPUT_SYSTEM
            go.AddComponent<InputSystemUIInputModule>();
#else
            go.AddComponent<StandaloneInputModule>();
#endif
        }

        private static Vector2 TopLeft() => new Vector2(0, 1);
        private static Vector2 TopRight() => new Vector2(1, 1);
        private static Vector2 BottomLeft() => new Vector2(0, 0);
        private static Vector2 BottomRight() => new Vector2(1, 0);
        private static Vector2 BottomCenter() => new Vector2(0.5f, 0);
        private static Vector2 CenterTop() => new Vector2(0.5f, 1);
        private static Vector2 CenterBottom() => new Vector2(0.5f, 0);
        private static Vector2 Center() => new Vector2(0.5f, 0.5f);
        private static Vector2 LeftCenter() => new Vector2(0, 0.5f);
        private static Vector2 RightCenter() => new Vector2(1, 0.5f);
    }
}
