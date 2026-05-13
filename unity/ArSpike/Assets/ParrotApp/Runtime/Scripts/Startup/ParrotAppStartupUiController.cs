using System;
using System.Collections;
using ParrotApp.Backend;
using ParrotApp.Config;
using ParrotApp.Lifecycle;
using ParrotApp.LiveKit;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem.UI;
#endif

namespace ParrotApp.UI
{
    /// <summary>
    /// Formal App startup shell for the production scene.
    /// It owns the visible startup flow only; LiveKit connection policy stays in
    /// AppStartupFlowController and RoomManager.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class ParrotAppStartupUiController : MonoBehaviour
    {
        [Header("Runtime Services")]
        [SerializeField] private AppStartupFlowController startupFlow;
        [SerializeField] private AppLifecycleManager lifecycleManager;
        [SerializeField] private RoomManager roomManager;
        [SerializeField] private AppRoomSettingClient roomSettingClient;

        [Header("Paper/Wood Placeholder Resources")]
        [SerializeField] private string resourcePrefix = "StartupPaperCraft/";

        // iQOO Neo9 landscape target: 2800 x 1260 (20:9-ish). The UI still
        // scales down for the Editor Game view, but layout decisions use a
        // wide phone frame instead of the old near-square preview.
        private const float ReferenceWidth = 2800f;
        private const float ReferenceHeight = 1260f;

        private enum VisibleScreen
        {
            Startup,
            RoomSetting,
            Transition,
            Main,
        }

        private Canvas _canvas;
        private Font _font;
        private RectTransform _startupSurface;
        private RectTransform _roomSettingSurface;
        private RectTransform _transitionSurface;
        private RectTransform _mainSurface;
        private RectTransform _transitionFill;
        private RectTransform _modeLeverKnob;
        private Text _startupStatus;
        private Text _selectionSummary;
        private Text _roomSettingSummary;
        private Text _transitionText;
        private Text _hudText;
        private Text _mainText;
        private Text _modeLeverText;
        private Text _roomValueText;
        private Text _modelValueText;
        private Text _personaValueText;
        private Text _lineValueText;
        private Text _sceneValueText;
        private Text _agentTeamValueText;
        private Image _statusIcon;
        private Image _transitionIcon;
        private RoomSettingSnapshotDto _roomSettingSnapshot;
        private RoomProfilePreviewDto _lastPreview;
        private Coroutine _roomSettingLoadCoroutine;
        private Coroutine _previewCoroutine;
        private float _statusTick;
        private float _transitionTick;
        private bool _subscribed;
        private bool _useChinese = true;
        private VisibleScreen _visibleScreen = VisibleScreen.Startup;
        private string _startupMessage = "Ready.";

        private static readonly string[] StartupExperienceModes =
        {
            "ar_companion",
            "2d_hall",
            "room_only",
        };

        private AppStartupConfigDto _config = AppStartupConfigDto.Default();
        private string _displayRoom = "Default GOSLO Room";
        private string _displayAgentTeam = "CatMaid Agent Team";
        private string _roomSettingBackendStatus = "Local fallback";

        private Sprite _backgroundSprite;
        private Sprite _portraitSprite;
        private Sprite _paperTitlePanel;
        private Sprite _paperSummaryPanel;
        private Sprite _paperRoomPanel;
        private Sprite _paperMainPanel;
        private Sprite _paperButton;
        private Sprite _paperButtonSmall;
        private Sprite _paperStatusPanel;
        private Sprite _decorCabinet;
        private Sprite _decorDrawer;
        private Sprite _iconStart;
        private Sprite _iconRoom;
        private Sprite _iconModel;
        private Sprite _iconLine;
        private Sprite _iconScene;
        private Sprite _iconHelp;
        private Sprite _iconWarning;
        private Sprite _iconRecord;
        private Sprite _iconDrawer;
        private Sprite _iconToolbar;
        private Sprite _iconSettings;
        private Sprite _statusGreen;
        private Sprite _statusRed;

        private void Awake()
        {
            ResolveServices();
            LoadSprites();
        }

        private void OnEnable()
        {
            ResolveServices();
            SubscribeStartupFlow();
        }

        private void OnDisable()
        {
            UnsubscribeStartupFlow();
        }

        private void Start()
        {
            ResolveServices();
            EnsureEventSystem();
            BuildUi();
            ShowStartup(Tr("就绪。", "Ready."));
            RefreshSelectionSummary();
            RefreshStatus();
            LoadRoomSettingSnapshotIfNeeded();
        }

        private void Update()
        {
            _statusTick += Time.unscaledDeltaTime;
            if (_statusTick >= 0.25f)
            {
                _statusTick = 0f;
                RefreshStatus();
            }

            if (_transitionSurface != null && _transitionSurface.gameObject.activeSelf)
                TickTransition();
        }

        private void ResolveServices()
        {
            if (startupFlow == null) startupFlow = FindObjectOfType<AppStartupFlowController>();
            if (lifecycleManager == null) lifecycleManager = FindObjectOfType<AppLifecycleManager>();
            if (roomManager == null) roomManager = RoomManager.Instance ?? FindObjectOfType<RoomManager>();
            if (roomSettingClient == null) roomSettingClient = FindObjectOfType<AppRoomSettingClient>();
            if (roomSettingClient == null) roomSettingClient = gameObject.AddComponent<AppRoomSettingClient>();
        }

        private void SubscribeStartupFlow()
        {
            if (_subscribed || startupFlow == null) return;
            startupFlow.OnTransitionStarted += HandleTransitionStarted;
            startupFlow.OnMainUiReady += HandleMainReady;
            startupFlow.OnStartupFailed += HandleStartupFailed;
            _subscribed = true;
        }

        private void UnsubscribeStartupFlow()
        {
            if (!_subscribed || startupFlow == null) return;
            startupFlow.OnTransitionStarted -= HandleTransitionStarted;
            startupFlow.OnMainUiReady -= HandleMainReady;
            startupFlow.OnStartupFailed -= HandleStartupFailed;
            _subscribed = false;
        }

        private void LoadSprites()
        {
            _backgroundSprite = LoadSprite("startup_room_bg");
            _portraitSprite = LoadSprite("paper_model_card");
            _paperTitlePanel = LoadSprite("paper_title_panel");
            _paperSummaryPanel = LoadSprite("paper_summary_panel");
            _paperRoomPanel = LoadSprite("paper_room_panel");
            _paperMainPanel = LoadSprite("paper_main_panel");
            _paperButton = LoadSprite("paper_button");
            _paperButtonSmall = LoadSprite("paper_button_small");
            _paperStatusPanel = LoadSprite("paper_status_panel");
            _decorCabinet = LoadSprite("decor_cabinet");
            _decorDrawer = LoadSprite("decor_wood_storage");
            _iconStart = LoadSprite("icon_start");
            _iconRoom = LoadSprite("icon_room");
            _iconModel = LoadSprite("icon_model");
            _iconLine = LoadSprite("icon_line");
            _iconScene = LoadSprite("icon_scene");
            _iconHelp = LoadSprite("icon_help");
            _iconWarning = LoadSprite("icon_warning");
            _iconRecord = LoadSprite("icon_record");
            _iconDrawer = LoadSprite("icon_drawer");
            _iconToolbar = LoadSprite("icon_toolbar");
            _iconSettings = LoadSprite("icon_settings");
            _statusGreen = LoadSprite("status_green");
            _statusRed = LoadSprite("status_red");
        }

        private Sprite LoadSprite(string resourceName)
        {
            var texture = Resources.Load<Texture2D>(resourcePrefix + resourceName);
            if (texture == null) return null;
            texture.filterMode = FilterMode.Point;
            texture.wrapMode = TextureWrapMode.Clamp;
            return Sprite.Create(
                texture,
                new Rect(0f, 0f, texture.width, texture.height),
                new Vector2(0.5f, 0.5f),
                100f,
                0,
                SpriteMeshType.FullRect);
        }

        private void BuildUi()
        {
            if (_canvas != null) return;

            _font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            if (_font == null) _font = Resources.GetBuiltinResource<Font>("Arial.ttf");

            _canvas = new GameObject("ParrotAppStartupCanvas").AddComponent<Canvas>();
            var uiCamera = Camera.main;
            if (uiCamera != null)
            {
                _canvas.renderMode = RenderMode.ScreenSpaceCamera;
                _canvas.worldCamera = uiCamera;
                _canvas.planeDistance = 1f;
            }
            else
            {
                _canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            }
            _canvas.sortingOrder = 40;

            var scaler = _canvas.gameObject.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(ReferenceWidth, ReferenceHeight);
            scaler.matchWidthOrHeight = 0.5f;
            _canvas.gameObject.AddComponent<GraphicRaycaster>();

            _startupSurface = BuildStartupSurface();
            _roomSettingSurface = BuildRoomSettingSurface();
            _transitionSurface = BuildTransitionSurface();
            _mainSurface = BuildMainSurface();
        }

        private RectTransform BuildStartupSurface()
        {
            var surface = CreateSurface("StartupSurface");
            AddBackground(surface);

            var topStatus = CreatePanel("TopStatus", surface, new Color(0.89f, 0.82f, 0.70f, 0.92f));
            Anchor(topStatus, TopLeft(), TopLeft(), TopLeft(), new Vector2(26f, -22f), new Vector2(260f, 54f));
            _statusIcon = CreateIcon("LiveKitStatusIcon", topStatus, _statusRed, new Vector2(22f, -16f), new Vector2(24f, 24f), TopLeft());
            _startupStatus = CreateText("StartupStatusText", topStatus, "Offline", 17, TextAnchor.MiddleLeft);
            Stretch(_startupStatus.rectTransform, new Vector2(56f, 6f), new Vector2(-14f, -6f));

            var hero = CreatePanel("GosloHeroPaper", surface, new Color(0.92f, 0.84f, 0.70f, 0.94f));
            Anchor(hero, CenterTop(), CenterTop(), CenterTop(), new Vector2(0f, -56f), new Vector2(1760f, 286f));
            AddOutline(hero, new Color(0.12f, 0.10f, 0.09f, 0.35f), new Vector2(3f, 3f));
            var title = CreateText("HeroTitle", hero, AppTitle(), 78, TextAnchor.MiddleCenter);
            Stretch(title.rectTransform, new Vector2(72f, 30f), new Vector2(-72f, -30f));

            AddIconButton(surface, LanguageSwitchLabel(), null, new Vector2(-48f, -28f), new Vector2(108f, 48f), ToggleLanguage, TopRight());

            var summary = CreatePanel("StartupSelectionSummary", surface, new Color(0.90f, 0.80f, 0.64f, 0.88f));
            Anchor(summary, CenterBottom(), CenterBottom(), CenterBottom(), new Vector2(0f, 334f), new Vector2(1520f, 182f));
            AddOutline(summary, new Color(0.12f, 0.10f, 0.09f, 0.18f), new Vector2(1f, 1f));
            _selectionSummary = CreateText("StartupSelectionSummaryText", summary, "", 28, TextAnchor.UpperLeft);
            Stretch(_selectionSummary.rectTransform, new Vector2(28f, 18f), new Vector2(-28f, -18f));

            var controls = CreatePanel("StartupControls", surface, new Color(0f, 0f, 0f, 0f));
            Anchor(controls, CenterBottom(), CenterBottom(), CenterBottom(), new Vector2(0f, 156f), new Vector2(1540f, 118f));
            AddIconButton(controls, Tr("设置", "ROOM"), _iconRoom, new Vector2(-560f, 0f), new Vector2(270f, 86f), ShowRoomSetting);
            AddIconButton(controls, Tr("开始", "START"), _iconStart, new Vector2(-250f, 0f), new Vector2(270f, 86f), StartPressed);
            AddModeLever(controls, new Vector2(300f, 0f), new Vector2(560f, 68f));

            return surface;
        }

        private RectTransform BuildRoomSettingSurface()
        {
            var surface = CreateSurface("RoomSettingSurface");
            surface.gameObject.SetActive(false);
            AddBackground(surface);

            var panel = CreatePanel("RoomSettingPanel", surface, new Color(0.91f, 0.82f, 0.68f, 0.96f));
            Anchor(panel, Center(), Center(), Center(), Vector2.zero, new Vector2(2140f, 900f));
            AddOutline(panel, new Color(0.12f, 0.10f, 0.09f, 0.32f), new Vector2(2f, 2f));

            var title = CreateText("RoomSettingTitle", panel, Tr("房间设置", "Room Setting"), 42, TextAnchor.MiddleLeft);
            Anchor(title.rectTransform, TopLeft(), TopLeft(), TopLeft(), new Vector2(58f, -42f), new Vector2(520f, 72f));
            AddIconButton(panel, Tr("返回", "BACK"), _iconHelp, new Vector2(-88f, -48f), new Vector2(172f, 58f), HideRoomSetting, TopRight());
            AddIconButton(panel, LanguageSwitchLabel(), null, new Vector2(-292f, -48f), new Vector2(108f, 58f), ToggleLanguage, TopRight());
            AddIconButton(panel, Tr("新建", "NEW"), _iconRoom, new Vector2(-776f, -48f), new Vector2(172f, 58f), NewRoomProfilePressed, TopRight());
            AddIconButton(panel, Tr("保存", "SAVE"), _iconSettings, new Vector2(-584f, -48f), new Vector2(172f, 58f), SaveRoomProfilePressed, TopRight());

            _roomValueText = AddSelectorRow(panel, Tr("Room", "Room"), _iconRoom, new Vector2(76f, -138f), ToggleRoom);
            _modelValueText = AddSelectorRow(panel, Tr("Model", "Model"), _iconModel, new Vector2(76f, -224f), ToggleModel);
            _personaValueText = AddSelectorRow(panel, Tr("Persona", "Persona"), _iconHelp, new Vector2(76f, -310f), TogglePersona);
            _lineValueText = AddSelectorRow(panel, Tr("Line", "Line"), _iconLine, new Vector2(76f, -396f), ToggleLine);
            _sceneValueText = AddSelectorRow(panel, Tr("套装", "Theme"), _iconScene, new Vector2(76f, -482f), ToggleTheme);
            _agentTeamValueText = AddSelectorRow(panel, Tr("Agent Team", "Agent Team"), _iconRoom, new Vector2(76f, -568f), SelectAgentTeam);

            var summary = CreatePanel("RoomSettingSummaryPanel", panel, new Color(0.86f, 0.74f, 0.57f, 0.72f));
            Anchor(summary, TopRight(), TopRight(), TopRight(), new Vector2(-72f, -138f), new Vector2(720f, 520f));
            AddOutline(summary, new Color(0.12f, 0.10f, 0.09f, 0.16f), new Vector2(1f, 1f));
            _roomSettingSummary = CreateText("RoomSettingSummaryText", summary, "", 24, TextAnchor.UpperLeft);
            Stretch(_roomSettingSummary.rectTransform, new Vector2(24f, 18f), new Vector2(-24f, -18f));

            AddIconButton(panel, Tr("返回首页", "BACK TO START"), _iconHelp, new Vector2(-676f, 88f), new Vector2(240f, 62f), HideRoomSetting, BottomRight());
            AddIconButton(panel, Tr("保存并返回", "SAVE + BACK"), _iconStart, new Vector2(-390f, 88f), new Vector2(260f, 62f), SaveRoomProfileAndBackPressed, BottomRight());

            return surface;
        }

        private RectTransform BuildTransitionSurface()
        {
            var surface = CreateSurface("TransitionSurface");
            surface.gameObject.SetActive(false);
            AddBackground(surface);

            var panel = CreatePanel("TransitionPanel", surface, new Color(0.91f, 0.82f, 0.68f, 0.96f));
            Anchor(panel, Center(), Center(), Center(), Vector2.zero, new Vector2(720f, 260f));
            AddOutline(panel, new Color(0.12f, 0.10f, 0.09f, 0.32f), new Vector2(2f, 2f));
            _transitionIcon = CreateIcon("TransitionIcon", panel, _iconRecord, new Vector2(64f, -52f), new Vector2(48f, 48f), TopLeft());
            _transitionText = CreateText("TransitionText", panel, Tr("启动中...", "Starting..."), 30, TextAnchor.MiddleLeft);
            Anchor(_transitionText.rectTransform, TopLeft(), TopLeft(), TopLeft(), new Vector2(132f, -48f), new Vector2(500f, 76f));

            var bar = CreatePanel("TransitionProgressBar", panel, new Color(0.18f, 0.13f, 0.10f, 0.88f));
            Anchor(bar, CenterBottom(), CenterBottom(), CenterBottom(), new Vector2(0f, 68f), new Vector2(540f, 28f));
            _transitionFill = CreatePanel("TransitionProgressFill", bar, new Color(0.77f, 0.50f, 0.25f, 0.95f));
            _transitionFill.anchorMin = Vector2.zero;
            _transitionFill.anchorMax = new Vector2(0.15f, 1f);
            _transitionFill.offsetMin = Vector2.zero;
            _transitionFill.offsetMax = Vector2.zero;

            AddIconButton(panel, Tr("取消", "CANCEL"), _iconWarning, new Vector2(0f, 24f), new Vector2(170f, 48f), CancelStartup, CenterBottom());
            return surface;
        }

        private RectTransform BuildMainSurface()
        {
            var surface = CreateSurface("MainReadySurface");
            surface.gameObject.SetActive(false);
            AddBackground(surface);

            var hud = CreatePanel("MainHud", surface, new Color(0.89f, 0.82f, 0.70f, 0.92f));
            Anchor(hud, TopLeft(), TopLeft(), TopLeft(), new Vector2(26f, -22f), new Vector2(390f, 138f));
            _hudText = CreateText("MainHudText", hud, "", 17, TextAnchor.UpperLeft);
            Stretch(_hudText.rectTransform, new Vector2(18f, 16f), new Vector2(-18f, -16f));

            var panel = CreatePanel("MainReadyPanel", surface, new Color(0.91f, 0.82f, 0.68f, 0.96f));
            Anchor(panel, Center(), Center(), Center(), Vector2.zero, new Vector2(780f, 300f));
            AddOutline(panel, new Color(0.12f, 0.10f, 0.09f, 0.32f), new Vector2(2f, 2f));
            _mainText = CreateText("MainReadyText", panel, "", 34, TextAnchor.MiddleCenter);
            Stretch(_mainText.rectTransform, new Vector2(36f, 28f), new Vector2(-36f, -104f));

            AddIconButton(panel, Tr("AR 就绪", "AR READY"), _iconScene, new Vector2(54f, 42f), new Vector2(190f, 54f), ReportSceneReady, BottomLeft());
            AddIconButton(panel, Tr("已放置", "PLACED"), _iconModel, new Vector2(254f, 42f), new Vector2(190f, 54f), ReportGosloPlaced, BottomLeft());
            AddIconButton(panel, Tr("设置", "ROOM"), _iconRoom, new Vector2(454f, 42f), new Vector2(170f, 54f), ShowRoomSetting, BottomLeft());

            return surface;
        }

        private void AddBackground(RectTransform parent)
        {
            var bg = CreateImage("PaperPlaceholderBackground", parent, _backgroundSprite, false);
            Stretch(bg.rectTransform, Vector2.zero, Vector2.zero);
            bg.color = new Color(1f, 1f, 1f, 1f);
        }

        private void StartPressed()
        {
            StartArFlow();
        }

        private void StartArFlow()
        {
            ResolveServices();
            _config.Normalize();
            ShowTransition(Tr("启动中...", "Starting..."));

            if (startupFlow == null)
            {
                HandleStartupFailed("startup_flow_missing");
                return;
            }

            startupFlow.StartFromConfig(CopyConfig(_config));
        }

        private void ShowRoomSetting()
        {
            _visibleScreen = VisibleScreen.RoomSetting;
            SetActive(_startupSurface, false);
            SetActive(_transitionSurface, false);
            SetActive(_mainSurface, false);
            SetActive(_roomSettingSurface, true);
            LoadRoomSettingSnapshotIfNeeded();
            RefreshSelectionSummary();
        }

        private void HideRoomSetting()
        {
            ShowStartup(Tr("就绪。", "Ready."));
        }

        private void CancelStartup()
        {
            startupFlow?.CancelStartup("startup_transition_cancelled");
            ShowStartup(Tr("已取消。", "Cancelled."));
        }

        private void LoadRoomSettingSnapshotIfNeeded()
        {
            ResolveServices();
            if (_roomSettingSnapshot != null || _roomSettingLoadCoroutine != null || roomSettingClient == null)
                return;
            _roomSettingLoadCoroutine = StartCoroutine(LoadRoomSettingSnapshot());
        }

        private IEnumerator LoadRoomSettingSnapshot()
        {
            _roomSettingBackendStatus = Tr("读取 RoomSetting...", "Loading RoomSetting...");
            RefreshSelectionSummary();

            RequestResult<RoomSettingSnapshotDto> result = default;
            yield return roomSettingClient.LoadSnapshot(_config.room_profile_id, r => result = r);
            _roomSettingLoadCoroutine = null;

            if (!result.Success || result.Value == null)
            {
                _roomSettingBackendStatus = Tr("后端未连接，使用本地占位", "Backend unavailable; using local fallback");
                RefreshSelectionSummary();
                yield break;
            }

            _roomSettingSnapshot = result.Value;
            _roomSettingBackendStatus = Tr("RoomSetting 已加载", "RoomSetting loaded");
            ApplyRoomProfileDto(_roomSettingSnapshot.active_room, updateDisplayName: true);
            ApplyCompatibility(_roomSettingSnapshot.compatibility);
            RefreshSelectionSummary();
        }

        private void ScheduleRoomProfilePreview()
        {
            if (_previewCoroutine != null)
                StopCoroutine(_previewCoroutine);
            if (roomSettingClient == null || !roomSettingClient.HasEndpoint)
            {
                ApplyLocalCompatibilityFallback();
                RefreshSelectionSummary();
                return;
            }
            _previewCoroutine = StartCoroutine(PreviewCurrentRoomProfile());
        }

        private IEnumerator PreviewCurrentRoomProfile()
        {
            var profile = RoomSettingDtoMapper.FromStartupConfig(_config, _displayRoom);
            RequestResult<RoomProfilePreviewDto> result = default;
            yield return roomSettingClient.Preview(profile, r => result = r);
            _previewCoroutine = null;

            if (!result.Success || result.Value == null)
            {
                _roomSettingBackendStatus = Tr("预览失败，保留当前选择", "Preview failed; keeping current selection");
                ApplyLocalCompatibilityFallback();
                RefreshSelectionSummary();
                yield break;
            }

            _lastPreview = result.Value;
            _roomSettingBackendStatus = Tr("兼容性已更新", "Compatibility updated");
            ApplyRoomProfileDto(_lastPreview.room_profile, updateDisplayName: false);
            ApplyCompatibility(_lastPreview.compatibility);
            RefreshSelectionSummary();
        }

        private void ApplyRoomProfileDto(RoomProfileDto profile, bool updateDisplayName)
        {
            if (profile == null) return;
            _config = RoomSettingDtoMapper.ToStartupConfig(profile, _config);
            if (updateDisplayName && !string.IsNullOrWhiteSpace(profile.display_name))
                _displayRoom = profile.display_name;
        }

        private void ApplyCompatibility(RoomCompatibilityDto compatibility)
        {
            if (compatibility == null) return;
            _config.setting_change_tier = compatibility.tier;
            _config.compatibility_state = compatibility.state ?? "";
            _config.compatibility_summary = _useChinese && !string.IsNullOrWhiteSpace(compatibility.tier_summary_zh)
                ? compatibility.tier_summary_zh
                : compatibility.tier_summary;
            _config.requires_livekit_reconnect = compatibility.tier >= 1;
        }

        private void ApplyLocalCompatibilityFallback()
        {
            _config.setting_change_tier = _config.line_id == "line_b" ? 1 : 0;
            _config.compatibility_state = _config.line_id == "line_b" ? "tier1_pending" : "ready";
            _config.compatibility_summary = _config.line_id == "line_b"
                ? Tr("需要启动前写入 orchestrator 并重连", "Requires orchestrator prewrite and reconnect")
                : Tr("本地占位：可启动", "Local fallback: ready");
            _config.requires_livekit_reconnect = _config.setting_change_tier >= 1;
        }

        private void SelectDefaultProfile()
        {
            _displayRoom = "Default GOSLO Room";
            _config.room_profile_id = "default";
            _config.pattern_id = "default";
            _config.model_id = "GOSLO_default";
            _config.persona_id = "goslo_parrot_default";
            _config.line_id = "line_a";
            _config.line_profile_id = "linea_gemini_realtime";
            _config.scene_id = "ar_handheld";
            _config.experience_mode = "ar_companion";
            _config.workspace_id = "mansion_hub";
            _config.skin_id = "manor";
            _config.room_id = "parrot-main";
            _config.setting_file_refs = new string[0];
            ApplyLocalCompatibilityFallback();
            RefreshSelectionSummary();
        }

        private void SelectNerLineBProfile()
        {
            _displayRoom = "Ner LineB Test Room";
            _config.room_profile_id = "ner_lineb_room";
            _config.pattern_id = "ner_lineb_room";
            _config.model_id = "ner_skin2";
            _config.persona_id = "ner_companion";
            _config.line_id = "line_b";
            _config.line_profile_id = "lineb_ner_ja_test";
            _config.scene_id = "ar_handheld";
            _config.experience_mode = "ar_companion";
            _config.workspace_id = "mansion_hub";
            _config.skin_id = "ner_mochi_room_v0";
            _config.room_id = "parrot-main";
            _config.setting_file_refs = new[]
            {
                "src/parrot/brain/personas/ner_companion.md",
                "codex_workspace/design_workspace/unity_ar_app/ner_roleplay_setting_obsidian_v0_20260511.md",
                "codex_workspace/design_workspace/unity_ar_app/ner_mochi_scene_v0_20260511.md",
                ".cursor/memory/architecture/Interface/app_v1_lineb_ner_realdevice_config_report_20260511.md",
            };
            ApplyLocalCompatibilityFallback();
            RefreshSelectionSummary();
        }

        private void SelectAgentTeam()
        {
            _displayAgentTeam = _displayAgentTeam == "CatMaid Agent Team" ? "CatMaid Agent Team / V1" : "CatMaid Agent Team";
            RefreshSelectionSummary();
        }

        private void NewRoomProfilePressed()
        {
            ResolveServices();
            if (roomSettingClient == null || !roomSettingClient.HasEndpoint)
            {
                CreateLocalNewRoomDraft();
                return;
            }

            StartCoroutine(NewRoomProfileFromBackend());
        }

        private IEnumerator NewRoomProfileFromBackend()
        {
            _roomSettingBackendStatus = Tr("新建 Room 草稿...", "Creating Room draft...");
            RefreshSelectionSummary();

            RequestResult<NewRoomProfileResponseDto> result = default;
            yield return roomSettingClient.NewRoomProfile(_config.room_profile_id, Tr("新建 Room", "New Room"), r => result = r);

            if (!result.Success || result.Value == null || result.Value.room_profile == null)
            {
                _roomSettingBackendStatus = Tr("新建失败：", "New failed: ") + (result.Error ?? "unknown");
                RefreshSelectionSummary();
                yield break;
            }

            ApplyRoomProfileDto(result.Value.room_profile, updateDisplayName: true);
            ApplyCompatibility(result.Value.compatibility);
            _roomSettingBackendStatus = Tr("新建草稿已加载，保存后持久化", "New draft loaded; save to persist");
            RefreshSelectionSummary();
        }

        private void CreateLocalNewRoomDraft()
        {
            _config.room_profile_id = "local_room_" + DateTime.UtcNow.ToString("HHmmss");
            _config.pattern_id = _config.room_profile_id;
            _displayRoom = Tr("本地草稿", "Local Draft");
            _roomSettingBackendStatus = Tr("后端未连接：本地草稿不会保存", "Backend unavailable: local draft is not saved");
            ApplyLocalCompatibilityFallback();
            RefreshSelectionSummary();
        }

        private void SaveRoomProfilePressed()
        {
            StartCoroutine(SaveCurrentRoomProfile(backToStartup: false));
        }

        private void SaveRoomProfileAndBackPressed()
        {
            StartCoroutine(SaveCurrentRoomProfile(backToStartup: true));
        }

        private IEnumerator SaveCurrentRoomProfile(bool backToStartup)
        {
            ResolveServices();
            if (roomSettingClient == null || !roomSettingClient.HasEndpoint)
            {
                _roomSettingBackendStatus = Tr("后端未连接：无法保存 Room", "Backend unavailable: Room not saved");
                RefreshSelectionSummary();
                yield break;
            }

            var profile = BuildWritableRoomProfileForSave();
            _roomSettingBackendStatus = Tr("保存 Room...", "Saving Room...");
            RefreshSelectionSummary();

            RequestResult<SaveRoomProfileResponseDto> result = default;
            yield return roomSettingClient.SaveRoomProfile(profile, r => result = r);

            if (!result.Success || result.Value == null)
            {
                _roomSettingBackendStatus = Tr("保存失败：", "Save failed: ") + (result.Error ?? "unknown");
                RefreshSelectionSummary();
                yield break;
            }

            ApplyRoomProfileDto(result.Value.room_profile, updateDisplayName: true);
            ApplyCompatibility(result.Value.compatibility);
            _roomSettingBackendStatus = Tr("Room 已保存", "Room saved");
            _roomSettingSnapshot = null;
            RefreshSelectionSummary();
            LoadRoomSettingSnapshotIfNeeded();

            if (backToStartup)
                ShowStartup(Tr("Room 已保存。", "Room saved."));
        }

        private RoomProfileDto BuildWritableRoomProfileForSave()
        {
            if (IsReservedRoomProfileId(_config.room_profile_id))
            {
                _config.room_profile_id = "room_" + DateTime.UtcNow.ToString("yyyyMMddHHmmss");
                _config.pattern_id = _config.room_profile_id;
                if (string.IsNullOrWhiteSpace(_displayRoom) || _displayRoom == "Default GOSLO Room")
                    _displayRoom = Tr("自定义 Room", "Custom Room");
            }

            return RoomSettingDtoMapper.FromStartupConfig(_config, _displayRoom);
        }

        private static bool IsReservedRoomProfileId(string id)
        {
            return string.Equals(id, "default", StringComparison.Ordinal)
                   || string.Equals(id, "ephemeral", StringComparison.Ordinal)
                   || string.Equals(id, "workspace_only", StringComparison.Ordinal);
        }

        private void ToggleModel()
        {
            var models = _roomSettingSnapshot?.selectors?.models;
            if (models != null && models.Length > 0)
            {
                int index = IndexOfModel(models, _config.model_id);
                var next = models[(index + 1 + models.Length) % models.Length];
                _config.model_id = string.IsNullOrWhiteSpace(next.model_id) ? _config.model_id : next.model_id;
                if (_config.model_id == "ner_skin2" && _config.persona_id == "goslo_parrot_default")
                    _config.persona_id = "ner_companion";
                ScheduleRoomProfilePreview();
                return;
            }

            if (_config.model_id == "GOSLO_default")
            {
                _config.model_id = "ner_skin2";
                if (_config.persona_id == "goslo_parrot_default")
                    _config.persona_id = "ner_companion";
                _config.skin_id = "ner_mochi_room_v0";
            }
            else
            {
                _config.model_id = "GOSLO_default";
                if (_config.persona_id == "ner_companion")
                    _config.persona_id = "goslo_parrot_default";
                _config.skin_id = "manor";
            }
            ScheduleRoomProfilePreview();
        }

        private void ToggleRoom()
        {
            var rooms = _roomSettingSnapshot?.selectors?.rooms ?? _roomSettingSnapshot?.rooms;
            if (rooms != null && rooms.Length > 0)
            {
                int index = IndexOfRoom(rooms, _config.room_profile_id);
                var next = rooms[(index + 1 + rooms.Length) % rooms.Length];
                ApplyRoomProfileDto(next, updateDisplayName: true);
                ScheduleRoomProfilePreview();
                return;
            }

            if (_config.room_profile_id == "default") SelectNerLineBProfile();
            else SelectDefaultProfile();
        }

        private void TogglePersona()
        {
            var personas = _roomSettingSnapshot?.selectors?.personas;
            if (personas != null && personas.Length > 0)
            {
                int index = IndexOfPersona(personas, _config.persona_id);
                var next = personas[(index + 1 + personas.Length) % personas.Length];
                _config.persona_id = string.IsNullOrWhiteSpace(next.persona_id) ? _config.persona_id : next.persona_id;
                ScheduleRoomProfilePreview();
                return;
            }

            _config.persona_id = _config.persona_id == "goslo_parrot_default" ? "ner_companion" : "goslo_parrot_default";
            ScheduleRoomProfilePreview();
        }

        private void ToggleLine()
        {
            var lines = _roomSettingSnapshot?.selectors?.lines;
            if (lines != null && lines.Length > 0)
            {
                int index = IndexOfLine(lines, _config.line_id);
                var next = lines[(index + 1 + lines.Length) % lines.Length];
                _config.line_id = string.IsNullOrWhiteSpace(next.line_id) ? _config.line_id : next.line_id;
                _config.line_profile_id = DefaultLineProfileFor(_config.line_id, _config.model_id);
                ScheduleRoomProfilePreview();
                return;
            }

            bool lineA = _config.line_id == "line_a";
            _config.line_id = lineA ? "line_b" : "line_a";
            _config.line_profile_id = lineA
                ? (_config.model_id == "ner_skin2" ? "lineb_ner_ja_test" : "lineb_google_default")
                : "linea_gemini_realtime";
            ScheduleRoomProfilePreview();
        }

        private void ToggleScene()
        {
            var scenes = _roomSettingSnapshot?.selectors?.scenes;
            if (scenes != null && scenes.Length > 0)
            {
                int index = IndexOfScene(scenes, _config.scene_id);
                var next = scenes[(index + 1 + scenes.Length) % scenes.Length];
                string id = SceneId(next);
                _config.scene_id = string.IsNullOrWhiteSpace(id) ? _config.scene_id : id;
                if (_config.scene_id == "desktop_webcam" && _config.experience_mode == "ar_companion")
                    _config.experience_mode = "2d_hall";
                ScheduleRoomProfilePreview();
                return;
            }

            _config.scene_id = _config.scene_id == "ar_handheld" ? "desktop_webcam" : "ar_handheld";
            if (_config.scene_id == "desktop_webcam" && _config.experience_mode == "ar_companion")
                _config.experience_mode = "2d_hall";
            ScheduleRoomProfilePreview();
        }

        private void ToggleTheme()
        {
            var skins = _roomSettingSnapshot?.selectors?.skins;
            if (skins != null && skins.Length > 0)
            {
                int index = IndexOfSkin(skins, _config.skin_id);
                var next = skins[(index + 1 + skins.Length) % skins.Length];
                if (!string.IsNullOrWhiteSpace(next.skin_id))
                    _config.skin_id = next.skin_id;
                ScheduleRoomProfilePreview();
                return;
            }

            switch (_config.skin_id)
            {
                case "manor":
                    _config.skin_id = "ner_mochi_room_v0";
                    break;
                case "ner_mochi_room_v0":
                    _config.skin_id = "pirate";
                    break;
                default:
                    _config.skin_id = "manor";
                    break;
            }
            ScheduleRoomProfilePreview();
        }

        private void TogglePattern()
        {
            _config.pattern_id = _config.pattern_id == "default" ? "quiet_room" : "default";
            RefreshSelectionSummary();
        }

        private void SetCapability(string mode)
        {
            _config.capability_mode = AppCapabilityModeNames.Normalize(mode);
            if (roomManager != null && roomManager.IsConnected && startupFlow != null)
                startupFlow.ApplyCapabilityMode(_config.capability_mode);
            RefreshSelectionSummary();
        }

        private void CycleExperienceMode()
        {
            var modes = ExperienceModeSelectors();
            if (modes != null && modes.Length > 0)
            {
                int index = IndexOfExperienceMode(modes, _config.experience_mode);
                var next = modes[(index + 1 + modes.Length) % modes.Length];
                if (!string.IsNullOrWhiteSpace(next.experience_mode))
                    _config.experience_mode = next.experience_mode;
            }
            else
            {
                int index = ExperienceModeIndex();
                _config.experience_mode = StartupExperienceModes[(index + 1) % StartupExperienceModes.Length];
            }

            if (_config.experience_mode == "ar_companion" && _config.scene_id != "ar_handheld")
                _config.scene_id = "ar_handheld";
            ScheduleRoomProfilePreview();
        }

        private void ReportSceneReady()
        {
            startupFlow?.ReportSceneReady();
            ShowMain(Tr("场景就绪", "Scene Ready"));
        }

        private void ReportGosloPlaced()
        {
            startupFlow?.ReportGosloPlaced();
            ShowMain(Tr("已放置", "Placed"));
        }

        private void HandleTransitionStarted(AppStartupConfigDto config)
        {
            _config = CopyConfig(config);
            ShowTransition(Tr("启动中...", "Starting..."));
        }

        private void HandleMainReady(AppStartupConfigDto config)
        {
            _config = CopyConfig(config);
            ShowMain(Tr("就绪", "Ready"));
        }

        private void HandleStartupFailed(string reason)
        {
            ShowStartup(Tr("启动失败：", "START failed: ") + (string.IsNullOrWhiteSpace(reason) ? Tr("未知", "unknown") : reason));
        }

        private void ShowStartup(string message)
        {
            _visibleScreen = VisibleScreen.Startup;
            _startupMessage = string.IsNullOrWhiteSpace(message) ? "Ready." : message;
            SetActive(_startupSurface, true);
            SetActive(_roomSettingSurface, false);
            SetActive(_transitionSurface, false);
            SetActive(_mainSurface, false);
            RefreshSelectionSummary();
            RefreshStatus();
        }

        private void ShowTransition(string message)
        {
            _visibleScreen = VisibleScreen.Transition;
            SetActive(_startupSurface, false);
            SetActive(_roomSettingSurface, false);
            SetActive(_transitionSurface, true);
            SetActive(_mainSurface, false);
            if (_transitionText != null) _transitionText.text = message;
        }

        private void ShowMain(string message)
        {
            _visibleScreen = VisibleScreen.Main;
            SetActive(_startupSurface, false);
            SetActive(_roomSettingSurface, false);
            SetActive(_transitionSurface, false);
            SetActive(_mainSurface, true);
            if (_mainText != null) _mainText.text = message;
            RefreshStatus();
        }

        private void TickTransition()
        {
            _transitionTick += Time.unscaledDeltaTime;
            float p = 0.16f + Mathf.PingPong(_transitionTick * 0.32f, 0.78f);
            if (_transitionFill != null)
            {
                _transitionFill.anchorMax = new Vector2(Mathf.Clamp01(p), 1f);
                _transitionFill.offsetMin = Vector2.zero;
                _transitionFill.offsetMax = Vector2.zero;
            }
            if (_transitionIcon != null)
                _transitionIcon.rectTransform.localRotation = Quaternion.Euler(0f, 0f, -_transitionTick * 90f);
        }

        private void RefreshSelectionSummary()
        {
            _config.Normalize();
            string text =
                Tr("Room：", "Room: ") + DisplayRoomValue() + "\n" +
                Tr("Model：", "Model: ") + DisplayModelValue() + "\n" +
                Tr("Persona：", "Persona: ") + DisplayPersonaValue() + "\n" +
                Tr("Line：", "Line: ") + DisplayLineValue() + "\n" +
                Tr("套装：", "Theme: ") + DisplayThemeValue() + "\n" +
                Tr("Agent Team：", "Agent Team: ") + DisplayAgentTeamValue();
            text += "\n" + Tr("后端：", "Backend: ") + _roomSettingBackendStatus;
            if (!string.IsNullOrWhiteSpace(_config.compatibility_state)
                || !string.IsNullOrWhiteSpace(_config.compatibility_summary))
            {
                text += "\nTier: " + _config.setting_change_tier + " / "
                        + (string.IsNullOrWhiteSpace(_config.compatibility_state)
                            ? "unknown"
                            : _config.compatibility_state);
                if (!string.IsNullOrWhiteSpace(_config.compatibility_summary))
                    text += "\n" + _config.compatibility_summary;
            }

            if (_selectionSummary != null) _selectionSummary.text = text;
            if (_roomSettingSummary != null) _roomSettingSummary.text = text;
            if (_roomValueText != null) _roomValueText.text = DisplayRoomValue();
            if (_modelValueText != null) _modelValueText.text = DisplayModelValue();
            if (_personaValueText != null) _personaValueText.text = DisplayPersonaValue();
            if (_lineValueText != null) _lineValueText.text = DisplayLineValue();
            if (_sceneValueText != null) _sceneValueText.text = DisplayThemeValue();
            if (_agentTeamValueText != null) _agentTeamValueText.text = DisplayAgentTeamValue();
            RefreshModeLever();
        }

        private void RefreshStatus()
        {
            ResolveServices();
            string lifecycle = lifecycleManager != null ? lifecycleManager.CurrentState.ToString() : "ColdStart";
            bool connected = roomManager != null && roomManager.IsConnected;
            string room = connected ? roomManager.RoomName : "offline";
            string connectTime = roomManager != null && roomManager.LastConnectDurationSeconds.HasValue
                ? roomManager.LastConnectDurationSeconds.Value.ToString("0.0") + "s"
                : "-";

            if (_startupStatus != null && _startupSurface != null && _startupSurface.gameObject.activeSelf)
                _startupStatus.text = connected ? Tr("已连接", "Connected") : Tr("离线", "Offline");
            if (_hudText != null)
            {
                _hudText.text =
                    "LiveKit: " + (connected ? Tr("已连接", "connected") : Tr("离线", "offline")) + "\n" +
                    Tr("状态：", "State: ") + lifecycle + "\n" +
                    Tr("房间：", "Room: ") + room + "\n" +
                    Tr("连接：", "Connect: ") + connectTime + "\n" +
                    "Line: " + _config.line_id;
            }
            if (_statusIcon != null) _statusIcon.sprite = connected ? _statusGreen : _statusRed;
        }

        private string Tr(string zh, string en)
        {
            return _useChinese ? zh : en;
        }

        private string AppTitle()
        {
            return Tr("AR 提醒助手", "GOSLO Parrot");
        }

        private string LanguageSwitchLabel()
        {
            return _useChinese ? "EN" : "中文";
        }

        private void ToggleLanguage()
        {
            _useChinese = !_useChinese;
            RebuildUiForLanguage();
        }

        private void RebuildUiForLanguage()
        {
            var screen = _visibleScreen;
            if (_canvas != null)
            {
                var canvasGo = _canvas.gameObject;
                if (Application.isPlaying) Destroy(canvasGo);
                else DestroyImmediate(canvasGo);
            }

            _canvas = null;
            _startupSurface = null;
            _roomSettingSurface = null;
            _transitionSurface = null;
            _mainSurface = null;
            _transitionFill = null;
            _modeLeverKnob = null;
            _startupStatus = null;
            _selectionSummary = null;
            _roomSettingSummary = null;
            _transitionText = null;
            _hudText = null;
            _mainText = null;
            _modeLeverText = null;
            _roomValueText = null;
            _modelValueText = null;
            _personaValueText = null;
            _lineValueText = null;
            _sceneValueText = null;
            _agentTeamValueText = null;
            _statusIcon = null;
            _transitionIcon = null;

            EnsureEventSystem();
            BuildUi();

            switch (screen)
            {
                case VisibleScreen.RoomSetting:
                    ShowRoomSetting();
                    break;
                case VisibleScreen.Transition:
                    ShowTransition(Tr("启动中...", "Starting..."));
                    break;
                case VisibleScreen.Main:
                    ShowMain(Tr("就绪", "Ready"));
                    break;
                default:
                    ShowStartup(Tr("就绪。", "Ready."));
                    break;
            }
        }

        private int IndexOfModel(ModelSelectorDto[] items, string selected)
            => IndexOf(items, item => item?.model_id, selected);

        private int IndexOfRoom(RoomProfileDto[] items, string selected)
            => IndexOf(items, item => item?.room_profile_id, selected);

        private int IndexOfPersona(PersonaSelectorDto[] items, string selected)
            => IndexOf(items, item => item?.persona_id, selected);

        private int IndexOfLine(LineSelectorDto[] items, string selected)
            => IndexOf(items, item => item?.line_id, selected);

        private int IndexOfScene(SceneSelectorDto[] items, string selected)
            => IndexOf(items, SceneId, selected);

        private int IndexOfSkin(SkinSelectorDto[] items, string selected)
            => IndexOf(items, item => item?.skin_id, selected);

        private int IndexOfExperienceMode(ExperienceModeSelectorDto[] items, string selected)
            => IndexOf(items, item => item?.experience_mode, selected);

        private static int IndexOf<T>(T[] items, Func<T, string> getId, string selected)
        {
            if (items == null || items.Length == 0 || getId == null) return 0;
            for (int i = 0; i < items.Length; i++)
            {
                if (string.Equals(getId(items[i]), selected, StringComparison.Ordinal))
                    return i;
            }
            return 0;
        }

        private static string SceneId(SceneSelectorDto item)
        {
            if (item == null) return "";
            return string.IsNullOrWhiteSpace(item.scene_profile_id) ? item.scene_id : item.scene_profile_id;
        }

        private string DefaultLineProfileFor(string lineId, string modelId)
        {
            var profiles = _roomSettingSnapshot?.selectors?.line_profiles;
            if (profiles != null)
            {
                string firstForLine = "";
                for (int i = 0; i < profiles.Length; i++)
                {
                    var profile = profiles[i];
                    if (profile == null || !string.Equals(profile.line_id, lineId, StringComparison.Ordinal))
                        continue;

                    if (string.IsNullOrWhiteSpace(firstForLine))
                        firstForLine = profile.line_profile_id;
                    if (string.Equals(modelId, "ner_skin2", StringComparison.Ordinal)
                        && string.Equals(profile.line_profile_id, "lineb_ner_ja_test", StringComparison.Ordinal))
                        return profile.line_profile_id;
                }
                if (!string.IsNullOrWhiteSpace(firstForLine))
                    return firstForLine;
            }

            if (string.Equals(lineId, "line_b", StringComparison.Ordinal))
                return string.Equals(modelId, "ner_skin2", StringComparison.Ordinal)
                    ? "lineb_ner_ja_test"
                    : "lineb_google_default";
            return "linea_gemini_realtime";
        }

        private ExperienceModeSelectorDto[] ExperienceModeSelectors()
        {
            var modes = _roomSettingSnapshot?.selectors?.experience_modes;
            return modes != null && modes.Length > 0 ? modes : null;
        }

        private string DisplayRoomValue()
        {
            var rooms = _roomSettingSnapshot?.selectors?.rooms ?? _roomSettingSnapshot?.rooms;
            string display = DisplayName(rooms, item => item?.room_profile_id, item => item?.display_name, _config.room_profile_id);
            if (!string.IsNullOrWhiteSpace(display)) return display;
            return string.IsNullOrWhiteSpace(_displayRoom) ? _config.room_profile_id : _displayRoom;
        }

        private string DisplayModelValue()
        {
            string display = DisplayName(
                _roomSettingSnapshot?.selectors?.models,
                item => item?.model_id,
                item => item?.display_name,
                _config.model_id);
            return string.IsNullOrWhiteSpace(display) ? _config.model_id : display;
        }

        private string DisplayPersonaValue()
        {
            string display = DisplayName(
                _roomSettingSnapshot?.selectors?.personas,
                item => item?.persona_id,
                item => item?.display_name,
                _config.persona_id);
            return string.IsNullOrWhiteSpace(display) ? _config.persona_id : display;
        }

        private string DisplayLineValue()
        {
            string lineDisplay = DisplayName(
                _roomSettingSnapshot?.selectors?.lines,
                item => item?.line_id,
                item => item?.display_name,
                _config.line_id);
            string profileDisplay = DisplayName(
                _roomSettingSnapshot?.selectors?.line_profiles,
                item => item?.line_profile_id,
                item => item?.display_name,
                _config.line_profile_id);

            if (string.IsNullOrWhiteSpace(lineDisplay)) lineDisplay = _config.line_id;
            if (string.IsNullOrWhiteSpace(profileDisplay)) profileDisplay = _config.line_profile_id;
            return lineDisplay + " / " + profileDisplay;
        }

        private string DisplaySceneValue()
        {
            string display = DisplayName(
                _roomSettingSnapshot?.selectors?.scenes,
                SceneId,
                item => item?.display_name,
                _config.scene_id);
            return string.IsNullOrWhiteSpace(display) ? _config.scene_id : display;
        }

        private string DisplayThemeValue()
        {
            string display = DisplayName(
                _roomSettingSnapshot?.selectors?.skins,
                item => item?.skin_id,
                item => item?.display_name,
                _config.skin_id);
            if (!string.IsNullOrWhiteSpace(display)) return display;

            switch (_config.skin_id)
            {
                case "ner_mochi_room_v0":
                    return Tr("Ner 麻糬房间", "Ner Mochi Room");
                case "pirate":
                    return Tr("海盗原型", "Pirate Prototype");
                case "goslo_default":
                    return Tr("GOSLO 经典", "GOSLO Classic");
                default:
                    return Tr("宅邸纸艺", "Mansion Paper");
            }
        }

        private string DisplayExperienceModeValue()
        {
            string display = DisplayName(
                ExperienceModeSelectors(),
                item => item?.experience_mode,
                item => item?.display_name,
                _config.experience_mode);
            if (!string.IsNullOrWhiteSpace(display)) return display;

            switch (_config.experience_mode)
            {
                case "2d_hall":
                    return Tr("2D 工作区", "2D Hall");
                case "room_only":
                    return Tr("轻量房间", "Room Only");
                default:
                    return Tr("AR 伴随", "AR Companion");
            }
        }

        private static string DisplayName<T>(
            T[] items,
            Func<T, string> getId,
            Func<T, string> getDisplayName,
            string selected)
        {
            if (items == null || getId == null || getDisplayName == null) return "";
            for (int i = 0; i < items.Length; i++)
            {
                var item = items[i];
                if (string.Equals(getId(item), selected, StringComparison.Ordinal))
                    return getDisplayName(item) ?? "";
            }
            return "";
        }

        private int ExperienceModeIndex()
        {
            var modes = ExperienceModeSelectors();
            if (modes != null && modes.Length > 0)
                return IndexOfExperienceMode(modes, _config.experience_mode);

            for (int i = 0; i < StartupExperienceModes.Length; i++)
            {
                if (StartupExperienceModes[i] == _config.experience_mode)
                    return i;
            }
            return 0;
        }

        private string DisplayAgentTeamValue()
        {
            if (!_useChinese) return _displayAgentTeam;
            return _displayAgentTeam.Contains("/ V1")
                ? "CatMaid Agent Team / V1 固定"
                : "CatMaid Agent Team";
        }

        private static AppStartupConfigDto CopyConfig(AppStartupConfigDto src)
        {
            if (src == null) src = AppStartupConfigDto.Default();
            var copy = new AppStartupConfigDto
            {
                scene_id = src.scene_id,
                room_id = src.room_id,
                room_profile_id = src.room_profile_id,
                model_id = src.model_id,
                persona_id = src.persona_id,
                pattern_id = src.pattern_id,
                line_id = src.line_id,
                line_profile_id = src.line_profile_id,
                experience_mode = src.experience_mode,
                skin_id = src.skin_id,
                capability_mode = src.capability_mode,
                workspace_id = src.workspace_id,
                livekit_url = src.livekit_url,
                join_token = src.join_token,
                unity_identity = src.unity_identity,
                app_api_url = src.app_api_url,
                orchestrator_url = src.orchestrator_url,
                orchestrator_secret = src.orchestrator_secret,
                setting_change_tier = src.setting_change_tier,
                compatibility_state = src.compatibility_state,
                compatibility_summary = src.compatibility_summary,
                requires_livekit_reconnect = src.requires_livekit_reconnect,
                setting_file_refs = src.setting_file_refs ?? new string[0],
            };
            copy.Normalize();
            return copy;
        }

        private static string ShortCapability(string mode)
        {
            switch (AppCapabilityModeNames.Normalize(mode))
            {
                case AppCapabilityModeNames.SessionOnlySilent:
                    return "Silent keepalive";
                case AppCapabilityModeNames.VoiceOnlyNoVideo:
                    return "Voice only";
                case AppCapabilityModeNames.VoiceVideoNoActionMonitor:
                    return "Voice + camera";
                default:
                    return "Full AR";
            }
        }

        private RectTransform CreateSurface(string name)
        {
            var rt = CreateRect(name, _canvas.transform);
            Stretch(rt, Vector2.zero, Vector2.zero);
            return rt;
        }

        private RectTransform CreatePanel(string name, Transform parent, Color color)
        {
            var rt = CreateRect(name, parent);
            var image = rt.gameObject.AddComponent<Image>();
            image.color = color;
            return rt;
        }

        private Image CreateImage(string name, Transform parent, Sprite sprite, bool preserveAspect)
        {
            var rt = CreateRect(name, parent);
            var image = rt.gameObject.AddComponent<Image>();
            image.sprite = sprite;
            image.color = Color.white;
            image.preserveAspect = preserveAspect;
            return image;
        }

        private Text CreateText(string name, Transform parent, string value, int size, TextAnchor anchor)
        {
            var rt = CreateRect(name, parent);
            var text = rt.gameObject.AddComponent<Text>();
            text.font = _font;
            text.text = value;
            text.fontSize = size;
            text.alignment = anchor;
            text.color = new Color(0.20f, 0.14f, 0.10f, 1f);
            text.horizontalOverflow = HorizontalWrapMode.Wrap;
            text.verticalOverflow = VerticalWrapMode.Truncate;
            return text;
        }

        private Text AddSelectorRow(
            Transform parent,
            string label,
            Sprite icon,
            Vector2 anchoredPosition,
            Action onCycle)
        {
            var row = CreatePanel("SelectorRow" + label.Replace(" ", ""), parent, new Color(0.88f, 0.78f, 0.62f, 0.82f));
            Anchor(row, TopLeft(), TopLeft(), TopLeft(), anchoredPosition, new Vector2(1180f, 66f));
            AddOutline(row, new Color(0.12f, 0.10f, 0.09f, 0.22f), new Vector2(1f, 1f));

            if (icon != null)
                CreateIcon("Icon", row, icon, new Vector2(24f, 0f), new Vector2(30f, 30f), LeftCenter());

            var labelText = CreateText("Label", row, label, 30, TextAnchor.MiddleLeft);
            Anchor(labelText.rectTransform, LeftCenter(), LeftCenter(), LeftCenter(), new Vector2(72f, 0f), new Vector2(220f, 54f));

            var valueText = CreateText("Value", row, "", 28, TextAnchor.MiddleLeft);
            Anchor(valueText.rectTransform, LeftCenter(), LeftCenter(), LeftCenter(), new Vector2(318f, 0f), new Vector2(650f, 54f));

            AddIconButton(row, "<", null, new Vector2(-118f, 0f), new Vector2(52f, 46f), onCycle, RightCenter());
            AddIconButton(row, ">", null, new Vector2(-54f, 0f), new Vector2(52f, 46f), onCycle, RightCenter());
            return valueText;
        }

        private void AddModeLever(Transform parent, Vector2 anchoredPosition, Vector2 size)
        {
            var track = CreatePanel("ModeLever", parent, new Color(0.87f, 0.76f, 0.60f, 0.98f));
            Anchor(track, Center(), Center(), Center(), anchoredPosition, size);
            AddOutline(track, new Color(0.12f, 0.10f, 0.09f, 0.28f), new Vector2(1.5f, 1.5f));

            var button = track.gameObject.AddComponent<Button>();
            var colors = button.colors;
            colors.highlightedColor = new Color(0.98f, 0.88f, 0.68f, 1f);
            colors.pressedColor = new Color(0.86f, 0.66f, 0.42f, 1f);
            button.colors = colors;
            button.onClick.AddListener(CycleExperienceMode);

            _modeLeverKnob = CreatePanel("ModeLeverKnob", track, new Color(0.50f, 0.28f, 0.16f, 0.96f));
            _modeLeverText = CreateText("ModeLeverText", track, "", 28, TextAnchor.MiddleCenter);
            Stretch(_modeLeverText.rectTransform, new Vector2(16f, 4f), new Vector2(-16f, -4f));
            RefreshModeLever();
        }

        private void RefreshModeLever()
        {
            if (_modeLeverText != null)
                _modeLeverText.text = Tr("启动模式：", "PlayMode: ") + DisplayExperienceModeValue();
            if (_modeLeverKnob == null) return;

            int index = ExperienceModeIndex();
            int count = ExperienceModeSelectors()?.Length ?? StartupExperienceModes.Length;
            float t = count <= 1
                ? 0f
                : index / (float)(count - 1);
            var anchor = new Vector2(t, 0.5f);
            var pivot = anchor;
            float x = Mathf.Lerp(10f, -10f, t);
            Anchor(_modeLeverKnob, anchor, anchor, pivot, new Vector2(x, 0f), new Vector2(70f, 42f));
        }

        private Button AddIconButton(
            Transform parent,
            string label,
            Sprite icon,
            Vector2 anchoredPosition,
            Vector2 size,
            Action onClick)
        {
            return AddIconButton(parent, label, icon, anchoredPosition, size, onClick, Center());
        }

        private Button AddIconButton(
            Transform parent,
            string label,
            Sprite icon,
            Vector2 anchoredPosition,
            Vector2 size,
            Action onClick,
            Vector2 anchor)
        {
            var rt = CreatePanel(label.Replace(" ", "") + "Button", parent, new Color(0.89f, 0.81f, 0.66f, 0.98f));
            Anchor(rt, anchor, anchor, anchor, anchoredPosition, size);
            AddOutline(rt, new Color(0.12f, 0.10f, 0.09f, 0.28f), new Vector2(1.5f, 1.5f));

            var button = rt.gameObject.AddComponent<Button>();
            var colors = button.colors;
            colors.normalColor = new Color(1f, 1f, 1f, 1f);
            colors.highlightedColor = new Color(0.98f, 0.88f, 0.68f, 1f);
            colors.pressedColor = new Color(0.86f, 0.66f, 0.42f, 1f);
            button.colors = colors;
            button.onClick.AddListener(() => onClick?.Invoke());

            if (icon != null)
                CreateIcon("Icon", rt, icon, new Vector2(20f, 0f), new Vector2(34f, 34f), LeftCenter());
            var text = CreateText("Label", rt, label, size.y > 60f ? 30 : 22, TextAnchor.MiddleCenter);
            Stretch(text.rectTransform, new Vector2(icon != null ? 52f : 12f, 4f), new Vector2(-12f, -4f));
            return button;
        }

        private Image CreateIcon(string name, Transform parent, Sprite sprite, Vector2 anchoredPosition, Vector2 size, Vector2 anchor)
        {
            var icon = CreateImage(name, parent, sprite, true);
            Anchor(icon.rectTransform, anchor, anchor, anchor, anchoredPosition, size);
            return icon;
        }

        private static RectTransform CreateRect(string name, Transform parent)
        {
            var go = new GameObject(name, typeof(RectTransform));
            go.transform.SetParent(parent, false);
            return go.GetComponent<RectTransform>();
        }

        private static void AddOutline(RectTransform target, Color color, Vector2 distance)
        {
            var outline = target.gameObject.AddComponent<Outline>();
            outline.effectColor = color;
            outline.effectDistance = distance;
        }

        private static void SetPanelSprite(RectTransform target, Sprite sprite)
        {
            if (target == null || sprite == null) return;
            var image = target.GetComponent<Image>();
            if (image == null) return;
            image.sprite = sprite;
            image.type = Image.Type.Simple;
            image.color = Color.white;
        }

        private static void Anchor(RectTransform rt, Vector2 min, Vector2 max, Vector2 pivot, Vector2 position, Vector2 size)
        {
            rt.anchorMin = min;
            rt.anchorMax = max;
            rt.pivot = pivot;
            rt.anchoredPosition = position;
            rt.sizeDelta = size;
        }

        private static void Stretch(RectTransform rt, Vector2 offsetMin, Vector2 offsetMax)
        {
            rt.anchorMin = Vector2.zero;
            rt.anchorMax = Vector2.one;
            rt.pivot = new Vector2(0.5f, 0.5f);
            rt.offsetMin = offsetMin;
            rt.offsetMax = offsetMax;
        }

        private static void SetActive(RectTransform rt, bool value)
        {
            if (rt != null) rt.gameObject.SetActive(value);
        }

        private Sprite _icon_warning()
        {
            return _iconWarning != null ? _iconWarning : _iconHelp;
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

        private static Vector2 TopLeft() => new Vector2(0f, 1f);
        private static Vector2 TopRight() => new Vector2(1f, 1f);
        private static Vector2 BottomLeft() => new Vector2(0f, 0f);
        private static Vector2 BottomRight() => new Vector2(1f, 0f);
        private static Vector2 CenterTop() => new Vector2(0.5f, 1f);
        private static Vector2 CenterBottom() => new Vector2(0.5f, 0f);
        private static Vector2 LeftCenter() => new Vector2(0f, 0.5f);
        private static Vector2 RightCenter() => new Vector2(1f, 0.5f);
        private static Vector2 Center() => new Vector2(0.5f, 0.5f);
    }
}
