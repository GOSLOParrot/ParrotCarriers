using System;
using System.Collections;
using ParrotApp.Backend;
using UnityEngine;
using UnityEngine.UI;

namespace ParrotApp.UI
{
    /// <summary>
    /// Formal WYSIWYG camera-mode HUD.
    ///
    /// Camera mode changes App capture UI and backend-owned mode state only.
    /// It does not draw a preview frame, does not call legacy snapshot RPC, and
    /// does not move image bytes through LiveKit/RPC. The shutter delegates to
    /// FormalHomeToolController so PhotoController remains the pixel owner.
    /// </summary>
    [DisallowMultipleComponent]
    public class FormalCameraModeController : MonoBehaviour
    {
        [SerializeField] private AppHomeMenuClient homeMenuClient;
        [SerializeField] private FormalHomeToolController homeToolController;
        [SerializeField] private bool showOverlayForPreviewModes = true;
        [SerializeField] private bool showProPanelByDefault = false;
        [SerializeField] private float defaultZoom = 1.0f;
        [SerializeField] private float minZoom = 0.5f;
        [SerializeField] private float maxZoom = 4.0f;
        [SerializeField] private float defaultExposure = 0.0f;
        [SerializeField] private float minExposure = -2.0f;
        [SerializeField] private float maxExposure = 2.0f;

        private readonly string[] _filters = { "natural", "paper", "low_light" };

        private Canvas _canvas;
        private RectTransform _overlayRoot;
        private RectTransform _proPanel;
        private RectTransform _transitionSlot;
        private Text _modeLabel;
        private Text _zoomLabel;
        private Text _exposureLabel;
        private Text _proLabel;
        private Text _statusLabel;
        private Text _transitionText;
        private Slider _zoomSlider;
        private Slider _exposureSlider;

        private string _mode = "off";
        private string _pendingMode = "";
        private string _lastHttpStatus = "camera_http_idle";
        private string _lastPhotoStatus = "camera_photo_idle";
        private float _zoom;
        private float _exposure;
        private int _filterIndex;
        private bool _proOpen;
        private Coroutine _modeApplyCoroutine;

        public string CurrentMode => _mode;
        public string PendingMode => _pendingMode;
        public bool HasPendingHttpRequest => _modeApplyCoroutine != null || !string.IsNullOrWhiteSpace(_pendingMode);
        public string LastCameraStatus { get; private set; } = "camera_mode_idle";
        public string LastHttpStatus => _lastHttpStatus;
        public string LastPhotoStatus => _lastPhotoStatus;
        public bool IsOpen => _canvas != null && _canvas.gameObject.activeSelf;
        public bool ProPanelOpen => _proOpen;
        public float Zoom => _zoom;
        public float Exposure => _exposure;
        public string FilterLabel => _filters[Mathf.Clamp(_filterIndex, 0, _filters.Length - 1)];
        public event Action<string> OnModeApplyPending;
        public event Action<string> OnModeApplySucceeded;
        public event Action<string, string> OnModeApplyFailed;

        private void Awake()
        {
            _zoom = Mathf.Clamp(defaultZoom, minZoom, maxZoom);
            _exposure = Mathf.Clamp(defaultExposure, minExposure, maxExposure);
            Bind();
        }

        private void Start()
        {
            Bind();
            EnsureUi();
            SetVisible(false);
            _proOpen = showProPanelByDefault;
            RefreshUi();
        }

        public string TogglePreviewLocal()
        {
            EnsureUi();
            return RequestModeApply(IsOpen ? "off" : "preview");
        }

        public string SetModeLocal(string mode, bool showOverlay = true)
        {
            EnsureUi();
            _mode = NormalizeMode(mode);
            if (string.Equals(_mode, "off", StringComparison.OrdinalIgnoreCase))
            {
                _proOpen = false;
                SetVisible(false);
            }
            else if (showOverlay && showOverlayForPreviewModes)
            {
                SetVisible(true);
            }

            LastCameraStatus = "camera_mode_" + _mode;
            RefreshUi();
            return LastCameraStatus;
        }

        public string RequestModeApply(string mode)
        {
            Bind();
            EnsureUi();
            string normalized = NormalizeMode(mode);
            string previous = _mode;
            if (HasPendingHttpRequest)
            {
                string pendingMode = string.IsNullOrWhiteSpace(_pendingMode) ? "active" : _pendingMode;
                LastCameraStatus = "camera_http_request_already_pending:" + pendingMode;
                RefreshUi();
                return LastCameraStatus;
            }

            MarkHttpPending(normalized);
            _modeApplyCoroutine = StartCoroutine(ApplyModeHttp(normalized, previous));
            return LastCameraStatus;
        }

        public void MarkHttpPending(string mode)
        {
            EnsureUi();
            _pendingMode = NormalizeMode(mode);
            bool pendingOff = string.Equals(_pendingMode, "off", StringComparison.OrdinalIgnoreCase);
            if (!pendingOff && showOverlayForPreviewModes)
                SetVisible(true);
            else if (pendingOff && string.Equals(_mode, "off", StringComparison.OrdinalIgnoreCase))
                SetVisible(false);
            _lastHttpStatus = "camera_http_pending:" + _pendingMode;
            LastCameraStatus = _lastHttpStatus;
            RefreshUi();
            OnModeApplyPending?.Invoke(_pendingMode);
        }

        public void MarkHttpResult(string mode, bool ok, string error = "")
        {
            string normalized = NormalizeMode(mode);
            _pendingMode = "";
            _lastHttpStatus = ok
                ? "camera_http_ok:" + normalized
                : "camera_http_failed:" + ShortLabel(error, "unknown", 28);
            LastCameraStatus = _lastHttpStatus;
            if (ok)
            {
                SetModeLocal(normalized);
                OnModeApplySucceeded?.Invoke(normalized);
            }
            else
            {
                RefreshUi();
                OnModeApplyFailed?.Invoke(normalized, error ?? "");
            }
        }

        public string CapturePhotoFromCameraMode()
        {
            Bind();
            EnsureUi();
            if (homeToolController == null)
            {
                _lastPhotoStatus = "camera_photo_owner_missing";
                LastCameraStatus = _lastPhotoStatus;
                RefreshUi();
                return LastCameraStatus;
            }

            string status = homeToolController.CapturePhoto();
            bool ok = ToolStatusLooksOk(status);
            if (ok)
                SetModeLocal("capture_locked");
            _lastPhotoStatus = ok ? "camera_photo_requested" : "camera_photo_failed:" + ShortLabel(status, "unknown", 24);
            LastCameraStatus = status;
            RefreshUi();
            return status;
        }

        private IEnumerator ApplyModeHttp(string mode, string previousMode)
        {
            Bind();
            if (homeMenuClient == null)
            {
                SetModeLocal(previousMode);
                MarkHttpResult(mode, false, "home_menu_client_missing");
                _modeApplyCoroutine = null;
                yield break;
            }

            RequestResult<AppActionResultDto> result = default;
            yield return homeMenuClient.SetCameraMode(mode, r => result = r);
            if (result.Success)
            {
                MarkHttpResult(mode, true);
            }
            else
            {
                SetModeLocal(previousMode);
                MarkHttpResult(mode, false, result.Error);
            }
            _modeApplyCoroutine = null;
        }

        public void MarkPhotoCaptureStatus(string status, bool ok)
        {
            _lastPhotoStatus = ok
                ? "camera_photo_requested"
                : "camera_photo_failed:" + ShortLabel(status, "unknown", 24);
            LastCameraStatus = string.IsNullOrWhiteSpace(status) ? _lastPhotoStatus : status;
            RefreshUi();
        }

        public string ToggleProSettings()
        {
            EnsureUi();
            _proOpen = !_proOpen;
            RefreshUi();
            return _proOpen ? "camera_pro_open" : "camera_pro_closed";
        }

        public string SetZoom(float value)
        {
            _zoom = Mathf.Clamp(value, minZoom, maxZoom);
            LastCameraStatus = "camera_zoom_" + _zoom.ToString("0.0");
            RefreshUi();
            return LastCameraStatus;
        }

        public string SetExposure(float value)
        {
            _exposure = Mathf.Clamp(value, minExposure, maxExposure);
            LastCameraStatus = "camera_exposure_" + _exposure.ToString("0.0");
            RefreshUi();
            return LastCameraStatus;
        }

        public string CycleFilter()
        {
            _filterIndex = (_filterIndex + 1) % _filters.Length;
            LastCameraStatus = "camera_filter_" + FilterLabel;
            RefreshUi();
            return LastCameraStatus;
        }

        private void Bind()
        {
            if (homeMenuClient == null) homeMenuClient = FindObjectOfType<AppHomeMenuClient>();
            if (homeToolController == null) homeToolController = FindObjectOfType<FormalHomeToolController>();
        }

        private void EnsureUi()
        {
            if (_canvas != null) return;

            var root = new GameObject("FormalCameraModeCanvas");
            root.transform.SetParent(transform, false);
            _canvas = root.AddComponent<Canvas>();
            _canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            _canvas.sortingOrder = 71;

            var scaler = root.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(2800f, 1260f);
            scaler.matchWidthOrHeight = 0.5f;
            root.AddComponent<GraphicRaycaster>();

            _overlayRoot = CreateArea(
                "FormalCameraModeOverlay_TransparentWysiwyg",
                root.transform,
                Vector2.zero,
                Vector2.one,
                new Vector2(0.5f, 0.5f),
                Vector2.zero,
                Vector2.zero);

            // WYSIWYG means the AR camera feed stays untouched; these edges only
            // reserve touch-safe control space around the real rendered view.
            var topEdge = CreatePanel(
                "FormalCameraModeTinyTopEdge",
                _overlayRoot,
                new Vector2(0f, 1f),
                new Vector2(1f, 1f),
                new Vector2(0.5f, 1f),
                Vector2.zero,
                new Vector2(0f, 58f),
                new Color(0.01f, 0.012f, 0.016f, 0.32f));
            topEdge.offsetMin = new Vector2(0f, -58f);
            topEdge.offsetMax = Vector2.zero;

            var bottomEdge = CreatePanel(
                "FormalCameraModeTinyBottomEdge",
                _overlayRoot,
                new Vector2(0f, 0f),
                new Vector2(1f, 0f),
                new Vector2(0.5f, 0f),
                Vector2.zero,
                new Vector2(0f, 96f),
                new Color(0.01f, 0.012f, 0.016f, 0.34f));
            bottomEdge.offsetMin = Vector2.zero;
            bottomEdge.offsetMax = new Vector2(0f, 96f);

            _modeLabel = CreateText(
                "FormalCameraModeLabel",
                _overlayRoot,
                new Vector2(0f, 1f),
                new Vector2(0f, 1f),
                new Vector2(0f, 1f),
                new Vector2(24f, -12f),
                new Vector2(500f, 46f),
                16,
                TextAnchor.MiddleLeft);

            CreateButton("FormalCameraModeCloseButton", _overlayRoot, new Vector2(1f, 1f), new Vector2(1f, 1f), new Vector2(1f, 1f), new Vector2(-28f, -12f), new Vector2(48f, 38f), "x", () => RequestModeApply("off"));
            CreateButton("FormalCameraModeSettingsButton", _overlayRoot, new Vector2(1f, 1f), new Vector2(1f, 1f), new Vector2(1f, 1f), new Vector2(-86f, -12f), new Vector2(72f, 38f), "gear", ToggleProSettings);
            CreateButton("FormalCameraModeReadyButton", _overlayRoot, new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(-110f, 22f), new Vector2(110f, 54f), "Ready", () => RequestModeApply("photo_ready"));
            CreateButton("FormalCameraModeShutterButton", _overlayRoot, new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(16f, 22f), new Vector2(130f, 54f), "Capture", CapturePhotoFromCameraMode);
            CreateButton("FormalCameraModePreviewButton", _overlayRoot, new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(154f, 22f), new Vector2(126f, 54f), "Preview", () => RequestModeApply("preview"));

            _zoomLabel = CreateText("FormalCameraZoomLabel", _overlayRoot, new Vector2(0f, 0.5f), new Vector2(0f, 0.5f), new Vector2(0f, 0.5f), new Vector2(28f, -72f), new Vector2(96f, 56f), 15, TextAnchor.MiddleCenter);
            _zoomSlider = CreateSlider("CameraGestureRail_Zoom", _overlayRoot, new Vector2(0f, 0.5f), new Vector2(0f, 0.5f), new Vector2(0f, 0.5f), new Vector2(130f, -72f), new Vector2(210f, 30f), minZoom, maxZoom, _zoom, SetZoom);

            _exposureLabel = CreateText("FormalCameraExposureLabel", _overlayRoot, new Vector2(1f, 0.5f), new Vector2(1f, 0.5f), new Vector2(1f, 0.5f), new Vector2(-28f, -72f), new Vector2(96f, 56f), 15, TextAnchor.MiddleCenter);
            _exposureSlider = CreateSlider("CameraExposureRail", _overlayRoot, new Vector2(1f, 0.5f), new Vector2(1f, 0.5f), new Vector2(1f, 0.5f), new Vector2(-130f, -72f), new Vector2(210f, 30f), minExposure, maxExposure, _exposure, SetExposure);

            _transitionSlot = CreatePanel(
                "FormalCameraModeTransitionSlot",
                _overlayRoot,
                new Vector2(0.5f, 0.5f),
                new Vector2(0.5f, 0.5f),
                new Vector2(0.5f, 0.5f),
                new Vector2(0f, 160f),
                new Vector2(430f, 56f),
                new Color(0.02f, 0.024f, 0.032f, 0.40f));
            _transitionText = CreateText("FormalCameraModeTransitionText", _transitionSlot, Vector2.zero, Vector2.one, new Vector2(0.5f, 0.5f), Vector2.zero, Vector2.zero, 18, TextAnchor.MiddleCenter);
            _transitionSlot.gameObject.SetActive(false);

            _proPanel = CreatePanel(
                "CameraProSettingsPanel",
                _overlayRoot,
                new Vector2(1f, 0.5f),
                new Vector2(1f, 0.5f),
                new Vector2(1f, 0.5f),
                new Vector2(-24f, 12f),
                new Vector2(330f, 420f),
                new Color(0.035f, 0.04f, 0.052f, 0.88f));

            CreateText("FormalCameraProSettingsTitle", _proPanel, new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(0f, 1f), new Vector2(20f, -18f), new Vector2(-40f, 44f), 20, TextAnchor.MiddleLeft).text = "PRO CAMERA";
            _proLabel = CreateText("FormalCameraProSettingsState", _proPanel, new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(0f, 1f), new Vector2(20f, -70f), new Vector2(-40f, 150f), 15, TextAnchor.UpperLeft);
            CreateButton("FormalCameraFilterButton", _proPanel, new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(-82f, 142f), new Vector2(122f, 38f), "Filter", CycleFilter);
            CreateButton("FormalCameraProReadyButton", _proPanel, new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(82f, 142f), new Vector2(122f, 38f), "Ready", () => RequestModeApply("photo_ready"));
            CreateButton("FormalCameraProPreviewButton", _proPanel, new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(-82f, 94f), new Vector2(122f, 38f), "Preview", () => RequestModeApply("preview"));
            CreateButton("FormalCameraHideUiButton", _proPanel, new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(82f, 94f), new Vector2(122f, 38f), "Hide UI", ToggleProSettings);

            var stamp = CreatePanel("CameraToolbox_PixelBBoxStamp", _proPanel, new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(0f, 28f), new Vector2(246f, 58f), new Color(0.78f, 0.74f, 0.56f, 0.94f));
            CreateText("FormalCameraPixelBBoxStampText", stamp, Vector2.zero, Vector2.one, new Vector2(0.5f, 0.5f), Vector2.zero, Vector2.zero, 14, TextAnchor.MiddleCenter).text = "Pixel BBox stamp slot";

            _statusLabel = CreateText(
                "FormalCameraModeStatus",
                _overlayRoot,
                new Vector2(0f, 0f),
                new Vector2(0f, 0f),
                new Vector2(0f, 0f),
                new Vector2(24f, 18f),
                new Vector2(760f, 48f),
                13,
                TextAnchor.MiddleLeft);
        }

        private void SetVisible(bool visible)
        {
            if (_canvas != null) _canvas.gameObject.SetActive(visible);
        }

        private void RefreshUi()
        {
            if (_canvas == null) return;
            if (_zoomSlider != null && !Mathf.Approximately(_zoomSlider.value, _zoom))
                _zoomSlider.SetValueWithoutNotify(_zoom);
            if (_exposureSlider != null && !Mathf.Approximately(_exposureSlider.value, _exposure))
                _exposureSlider.SetValueWithoutNotify(_exposure);
            if (_modeLabel != null)
                _modeLabel.text = "CAM " + ModeLabel(_mode) + "  "
                                  + "zoom " + _zoom.ToString("0.0") + "x  "
                                  + "EV " + _exposure.ToString("0.0");
            if (_zoomLabel != null) _zoomLabel.text = "ZOOM\n" + _zoom.ToString("0.0") + "x";
            if (_exposureLabel != null) _exposureLabel.text = "EV\n" + _exposure.ToString("0.0");
            if (_proLabel != null)
                _proLabel.text =
                    "mode    " + ModeLabel(_mode) + "\n"
                    + "filter  " + FilterLabel + "\n"
                    + "http    " + ShortLabel(_lastHttpStatus, "idle", 34) + "\n"
                    + "photo   " + ShortLabel(_lastPhotoStatus, "idle", 34);
            if (_statusLabel != null)
                _statusLabel.text = ShortLabel(LastCameraStatus, "camera", 48)
                                    + "  HTTP " + ShortLabel(_lastHttpStatus, "idle", 36)
                                    + "  Photo " + ShortLabel(_lastPhotoStatus, "idle", 36);
            if (_proPanel != null)
                _proPanel.gameObject.SetActive(_proOpen);
            if (_transitionText != null)
                _transitionText.text = string.IsNullOrWhiteSpace(_pendingMode)
                    ? ModeLabel(_mode)
                    : "HTTP " + ModeLabel(_pendingMode);
            if (_transitionSlot != null)
                _transitionSlot.gameObject.SetActive(!string.IsNullOrWhiteSpace(_pendingMode));
        }

        private static string NormalizeMode(string mode)
        {
            if (string.Equals(mode, "preview", StringComparison.OrdinalIgnoreCase)) return "preview";
            if (string.Equals(mode, "photo_ready", StringComparison.OrdinalIgnoreCase)) return "photo_ready";
            if (string.Equals(mode, "capture_locked", StringComparison.OrdinalIgnoreCase)) return "capture_locked";
            return "off";
        }

        private static string ModeLabel(string mode)
        {
            if (string.Equals(mode, "photo_ready", StringComparison.OrdinalIgnoreCase)) return "photo ready";
            if (string.Equals(mode, "capture_locked", StringComparison.OrdinalIgnoreCase)) return "capture locked";
            if (string.Equals(mode, "preview", StringComparison.OrdinalIgnoreCase)) return "preview";
            return "off";
        }

        private static bool ToolStatusLooksOk(string status)
        {
            if (string.IsNullOrWhiteSpace(status)) return false;
            return !status.Contains("missing")
                   && !status.Contains("failed")
                   && !status.Contains("waits")
                   && !status.Contains("not_phone_safe");
        }

        private static RectTransform CreatePanel(
            string name,
            Transform parent,
            Vector2 anchorMin,
            Vector2 anchorMax,
            Vector2 pivot,
            Vector2 position,
            Vector2 size,
            Color color)
        {
            var rect = CreateArea(name, parent, anchorMin, anchorMax, pivot, position, size);
            var image = rect.gameObject.AddComponent<Image>();
            image.color = color;
            image.raycastTarget = false;
            return rect;
        }

        private static Text CreateButton(
            string name,
            Transform parent,
            Vector2 anchorMin,
            Vector2 anchorMax,
            Vector2 pivot,
            Vector2 position,
            Vector2 size,
            string label,
            Func<string> action)
        {
            var rect = CreateArea(name, parent, anchorMin, anchorMax, pivot, position, size);
            var image = rect.gameObject.AddComponent<Image>();
            image.color = new Color(0.10f, 0.085f, 0.065f, 0.88f);
            image.raycastTarget = true;
            var button = rect.gameObject.AddComponent<Button>();
            button.onClick.AddListener(() => action?.Invoke());
            var text = CreateText(name + "Label", rect, Vector2.zero, Vector2.one, new Vector2(0.5f, 0.5f), Vector2.zero, Vector2.zero, 13, TextAnchor.MiddleCenter);
            text.text = label;
            return text;
        }

        private static Slider CreateSlider(
            string name,
            Transform parent,
            Vector2 anchorMin,
            Vector2 anchorMax,
            Vector2 pivot,
            Vector2 position,
            Vector2 size,
            float min,
            float max,
            float value,
            Func<float, string> onChanged)
        {
            var rect = CreateArea(name, parent, anchorMin, anchorMax, pivot, position, size);
            var slider = rect.gameObject.AddComponent<Slider>();
            slider.minValue = min;
            slider.maxValue = max;
            slider.value = Mathf.Clamp(value, min, max);

            var track = CreateArea(name + "Track", rect, Vector2.zero, Vector2.one, new Vector2(0.5f, 0.5f), Vector2.zero, Vector2.zero);
            var trackImage = track.gameObject.AddComponent<Image>();
            trackImage.color = new Color(0.09f, 0.08f, 0.07f, 0.82f);
            trackImage.raycastTarget = true;

            var fill = CreateArea(name + "Fill", rect, Vector2.zero, new Vector2(0.5f, 1f), new Vector2(0f, 0.5f), Vector2.zero, Vector2.zero);
            var fillImage = fill.gameObject.AddComponent<Image>();
            fillImage.color = new Color(0.72f, 0.58f, 0.32f, 0.86f);
            fillImage.raycastTarget = false;

            var handle = CreateArea(name + "Handle", rect, new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(22f, 36f));
            var handleImage = handle.gameObject.AddComponent<Image>();
            handleImage.color = new Color(0.92f, 0.78f, 0.46f, 0.96f);
            handleImage.raycastTarget = true;

            slider.fillRect = fill;
            slider.handleRect = handle;
            slider.targetGraphic = handleImage;
            slider.onValueChanged.AddListener(v => onChanged?.Invoke(v));
            return slider;
        }

        private static Text CreateText(
            string name,
            Transform parent,
            Vector2 anchorMin,
            Vector2 anchorMax,
            Vector2 pivot,
            Vector2 position,
            Vector2 size,
            int fontSize,
            TextAnchor alignment)
        {
            var rect = CreateArea(name, parent, anchorMin, anchorMax, pivot, position, size);
            var text = rect.gameObject.AddComponent<Text>();
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            text.fontSize = fontSize;
            text.alignment = alignment;
            text.horizontalOverflow = HorizontalWrapMode.Wrap;
            text.verticalOverflow = VerticalWrapMode.Truncate;
            text.color = new Color(0.96f, 0.92f, 0.80f, 0.96f);
            text.raycastTarget = false;
            return text;
        }

        private static RectTransform CreateArea(
            string name,
            Transform parent,
            Vector2 anchorMin,
            Vector2 anchorMax,
            Vector2 pivot,
            Vector2 position,
            Vector2 size)
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

        private static string ShortLabel(string primary, string fallback, int max)
        {
            string text = string.IsNullOrWhiteSpace(primary) ? (fallback ?? "") : primary.Trim();
            if (text.Length <= max) return text;
            return text.Substring(0, Mathf.Max(1, max - 3)) + "...";
        }
    }
}
