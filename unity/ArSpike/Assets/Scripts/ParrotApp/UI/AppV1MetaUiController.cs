using System.Collections;
using System.Collections.Generic;
using ParrotApp.Attention;
using ParrotApp.Config;
using ParrotApp.Hands;
using ParrotApp.Lifecycle;
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

        [Header("Optional sprites")]
        [SerializeField] private Sprite woodDrawerSprite;
        [SerializeField] private Sprite woodButtonSprite;
        [SerializeField] private Sprite smallPaperNoteSprite;
        [SerializeField] private Sprite filledPaperNoteSprite;

        private const float ReferenceWidth = 1080f;
        private const float ReferenceHeight = 1920f;

        private Canvas _canvas;
        private RectTransform _startupSurface;
        private RectTransform _transitionSurface;
        private RectTransform _mainSurface;
        private RectTransform _toolDrawer;
        private RectTransform _workspace;
        private RectTransform _noteStack;
        private RectTransform _magnifierOverlay;
        private RectTransform _magnifierSettings;
        private RectTransform _bboxOverlay;
        private RectTransform _bboxResizeHandle;
        private Text _startupStatus;
        private Text _transitionText;
        private Text _hudText;
        private Text _workspaceText;
        private Text _noteText;
        private Text _magnifierLabel;
        private Text _bboxLabel;
        private Slider _magnifierSlider;

        private bool _drawerOpen;
        private bool _workspaceOpen;
        private bool _magnifierOpen;
        private bool _magnifierSettingsOpen;
        private bool _bboxOpen;
        private int _noteCount;
        private float _magnifierScale = 2f;
        private string _activeFocusId = "";
        private string _activeBBoxId = "";
        private readonly List<string> _localDocuments = new();

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
            _workspace = BuildWorkspace(root);
            _noteStack = BuildNoteStack(root);
            _magnifierOverlay = BuildMagnifierOverlay(root);
            _bboxOverlay = BuildBBoxOverlay(root);

            _drawerOpen = false;
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

            var note = CreatePanel("PaperNote_Small", stack, new Color(0.86f, 0.78f, 0.58f, 0.98f), smallPaperNoteSprite);
            Stretch(note, Vector2.zero, Vector2.zero);
            AddEvent(note.gameObject, EventTriggerType.PointerClick, _ => ToggleWorkspace());
            _noteText = CreateText("PaperNoteText", note, "", 16, TextAnchor.MiddleLeft);
            Stretch(_noteText.rectTransform, new Vector2(18, 10), new Vector2(-18, -10));
            return stack;
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

        private void AddCornerButton(RectTransform parent, string label, Vector2 anchoredPosition, UnityEngine.Events.UnityAction action)
        {
            var button = AddToolButton(parent, label, 0, action);
            button.gameObject.name = parent.name + "_" + label;
            Anchor(button.GetComponent<RectTransform>(), TopRight(), TopRight(), TopRight(), anchoredPosition, new Vector2(52, 38));
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

        private Text CreateText(string name, Transform parent, string text, int fontSize, TextAnchor anchor)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var label = go.AddComponent<Text>();
            label.text = text;
            label.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
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

        private void ResizeBBox(PointerEventData eventData)
        {
            if (_bboxOverlay == null) return;
            Vector2 size = _bboxOverlay.sizeDelta;
            size.x = Mathf.Clamp(size.x + eventData.delta.x, 120f, 720f);
            size.y = Mathf.Clamp(size.y - eventData.delta.y, 90f, 520f);
            _bboxOverlay.sizeDelta = size;
            RefreshBBoxLabel();
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
            if (startupFlow != null)
            {
                startupFlow.ApplyCapabilityMode(mode);
                ShowStartup("Capability mode requested: " + mode);
            }
            else
            {
                ShowStartup("Capability mode placeholder: " + mode);
            }
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
            if (startupFlow != null) startupFlow.ReportGosloPlaced();
            AddPaperNote("GOSLO placed", "Greeting gate opened after placement.");
        }

        private void ToggleSettings()
        {
            AddPaperNote("Settings", "Awareness, camera mode, and capability mode stay backend-owned.");
        }

        private void ToggleCameraPreview()
        {
            AddPaperNote("Camera mode", "Preview/photo_ready request belongs to App facade; pixels stay in PhotoController.");
            RefreshHud();
        }

        private void CapturePhoto()
        {
            ResolveDependencies();
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
            AddPaperNote("Nanobot report", "A paper note can expand or move into the workdesk.");
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
            if (_noteText != null)
            {
                _noteText.text = title + "\n" + body;
            }
            RefreshWorkspace();
            RefreshHud();
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
                "Greeting: waits for placement\n" +
                "Notes: " + _noteCount + "\n" +
                "Focus " + focusCount + " / BBox " + bboxCount;
        }

        private void RefreshWorkspace()
        {
            if (_workspaceText == null) return;
            if (_localDocuments.Count == 0)
            {
                _workspaceText.text = "No paper on the desk yet.";
                return;
            }
            int count = Mathf.Min(6, _localDocuments.Count);
            _workspaceText.text = string.Join("\n\n", _localDocuments.GetRange(0, count));
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
        private static Vector2 BottomRight() => new Vector2(1, 0);
        private static Vector2 BottomCenter() => new Vector2(0.5f, 0);
        private static Vector2 CenterTop() => new Vector2(0.5f, 1);
        private static Vector2 CenterBottom() => new Vector2(0.5f, 0);
        private static Vector2 Center() => new Vector2(0.5f, 0.5f);
        private static Vector2 LeftCenter() => new Vector2(0, 0.5f);
        private static Vector2 RightCenter() => new Vector2(1, 0.5f);
    }
}
