using System;
using System.Collections;
using ParrotApp.Backend;
using ParrotApp.VisualTools;
using UnityEngine;
using UnityEngine.EventSystems;
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
        [SerializeField] private bool enablePinchViewZoom = true;
        [SerializeField] private float minViewZoom = 1.0f;
        [SerializeField] private float maxViewZoom = 3.0f;

        private readonly string[] _filters = { "natural", "paper", "low_light" };

        private Canvas _canvas;
        private RectTransform _overlayRoot;
        private RectTransform _proPanel;
        private RectTransform _transitionSlot;
        private RectTransform _feedbackFlash;
        private RectTransform _shutterButtonRoot;
        private Text _modeLabel;
        private Text _zoomLabel;
        private Text _exposureLabel;
        private Text _proLabel;
        private Text _statusLabel;
        private Text _transitionText;
        private Text _feedbackBadge;
        private Slider _zoomSlider;
        private Slider _exposureSlider;
        private VisualToolShutterBlackoutFeedback _shutterBlackout;

        private string _mode = "off";
        private string _pendingMode = "";
        private string _lastHttpStatus = "camera_http_idle";
        private string _lastPhotoStatus = "camera_photo_idle";
        private float _zoom;
        private float _exposure;
        private int _filterIndex;
        private bool _proOpen;
        private Coroutine _modeApplyCoroutine;
        private Coroutine _feedbackCoroutine;
        private float _pinchStartDistance;
        private float _pinchStartZoom = 1f;
        private Camera _zoomCamera;
        private float _baseCameraFieldOfView;
        private float _baseCameraOrthographicSize;
        private bool _hasCameraZoomBase;
        private FormalHomeToolController _photoUploadEventSource;
        private string _pendingPhotoId = "";
        private string _lastBlackoutPhotoId = "";

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

        private void OnDestroy()
        {
            BindPhotoUploadEvents(null);
        }

        private void Update()
        {
            if (IsOpen)
            {
                VisualToolHudMetrics.ApplyResponsiveShutterLayout(_shutterButtonRoot);
                HandlePinchViewZoom();
            }
            else
            {
                _pinchStartDistance = 0f;
            }
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
                ResetCameraViewZoom();
                SetVisible(false);
            }
            else if (showOverlay && showOverlayForPreviewModes)
            {
                SetVisible(true);
                ApplyCameraViewZoom();
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
            MarkPhotoCaptureStatus(status, ok);
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
            bool pendingUpload = ok && IsPhotoUploadPendingStatus(status);
            string photoId = TryExtractPhotoIdFromStatus(status);
            if (pendingUpload)
                _pendingPhotoId = photoId;
            else
                _pendingPhotoId = "";
            _lastPhotoStatus = pendingUpload
                ? "camera_photo_upload_pending"
                : ok
                ? "camera_photo_requested"
                : "camera_photo_failed:" + ShortLabel(status, "unknown", 24);
            LastCameraStatus = string.IsNullOrWhiteSpace(status) ? _lastPhotoStatus : status;
            if (pendingUpload)
                PlayShutterBlackout(photoId);
            if (!pendingUpload)
                PlayCaptureFeedback(ok);
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
            _zoom = Mathf.Clamp(value, Mathf.Max(minZoom, minViewZoom), Mathf.Max(maxZoom, maxViewZoom));
            LastCameraStatus = "camera_zoom_" + _zoom.ToString("0.0");
            ApplyCameraViewZoom();
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
            BindPhotoUploadEvents(homeToolController);
        }

        private void BindPhotoUploadEvents(FormalHomeToolController source)
        {
            if (_photoUploadEventSource == source)
                return;
            if (_photoUploadEventSource != null)
                _photoUploadEventSource.OnPhotoUploadCompleted -= HandlePhotoUploadCompleted;
            _photoUploadEventSource = source;
            if (_photoUploadEventSource != null)
                _photoUploadEventSource.OnPhotoUploadCompleted += HandlePhotoUploadCompleted;
        }

        private void HandlePhotoUploadCompleted(string photoId, string status, bool ok)
        {
            if (ShouldIgnorePhotoUploadCompletion(photoId))
                return;
            _pendingPhotoId = "";
            _lastPhotoStatus = ok
                ? "camera_photo_upload_ok"
                : "camera_photo_upload_failed:" + ShortLabel(status, "unknown", 24);
            LastCameraStatus = string.IsNullOrWhiteSpace(status) ? _lastPhotoStatus : status;
            PlayCaptureFeedback(ok);
            RefreshUi();
        }

        private void EnsureUi()
        {
            if (_canvas != null) return;

            var root = new GameObject("FormalCameraModeCanvas");
            root.transform.SetParent(transform, false);
            _canvas = root.AddComponent<Canvas>();
            _canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            _canvas.sortingOrder = 71;
            _shutterBlackout = root.AddComponent<VisualToolShutterBlackoutFeedback>();

            var scaler = root.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = VisualToolHudMetrics.IqooNeo9LandscapeReferenceResolution;
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

            _shutterButtonRoot = CreateShutterButton(
                "FormalCameraModeShutterButton",
                _overlayRoot,
                CapturePhotoFromCameraMode);

            _proPanel = CreatePanel(
                "CameraProSettingsPanel",
                _overlayRoot,
                new Vector2(1f, 0.5f),
                new Vector2(1f, 0.5f),
                new Vector2(1f, 0.5f),
                new Vector2(-24f, 12f),
                new Vector2(330f, 320f),
                new Color(0.035f, 0.04f, 0.052f, 0.88f));

            CreateText("FormalCameraProSettingsTitle", _proPanel, new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(0f, 1f), new Vector2(20f, -18f), new Vector2(-40f, 44f), 20, TextAnchor.MiddleLeft).text = "PRO CAMERA";
            _proLabel = CreateText("FormalCameraProSettingsState", _proPanel, new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(0f, 1f), new Vector2(20f, -70f), new Vector2(-40f, 150f), 15, TextAnchor.UpperLeft);
            CreateButton("FormalCameraFilterButton", _proPanel, new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(-82f, 142f), new Vector2(122f, 38f), "Filter", CycleFilter);
            CreateButton("FormalCameraProReadyButton", _proPanel, new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(82f, 142f), new Vector2(122f, 38f), "Ready", () => RequestModeApply("photo_ready"));
            CreateButton("FormalCameraProPreviewButton", _proPanel, new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(-82f, 94f), new Vector2(122f, 38f), "Preview", () => RequestModeApply("preview"));
            CreateButton("FormalCameraHideUiButton", _proPanel, new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(82f, 94f), new Vector2(122f, 38f), "Hide UI", ToggleProSettings);

            _zoomLabel = CreateText("FormalCameraZoomLabel", _proPanel, new Vector2(0f, 0f), new Vector2(0f, 0f), new Vector2(0f, 0f), new Vector2(18f, 8f), new Vector2(72f, 42f), 13, TextAnchor.MiddleCenter);
            _zoomSlider = CreateSlider("CameraGestureRail_Zoom", _proPanel, new Vector2(0f, 0f), new Vector2(0f, 0f), new Vector2(0f, 0f), new Vector2(98f, 14f), new Vector2(190f, 24f), minZoom, maxZoom, _zoom, SetZoom);
            _exposureLabel = CreateText("FormalCameraExposureLabel", _proPanel, new Vector2(0f, 0f), new Vector2(0f, 0f), new Vector2(0f, 0f), new Vector2(18f, 52f), new Vector2(72f, 42f), 13, TextAnchor.MiddleCenter);
            _exposureSlider = CreateSlider("CameraExposureRail", _proPanel, new Vector2(0f, 0f), new Vector2(0f, 0f), new Vector2(0f, 0f), new Vector2(98f, 58f), new Vector2(190f, 24f), minExposure, maxExposure, _exposure, SetExposure);
            _zoomLabel.gameObject.SetActive(false);
            _zoomSlider.gameObject.SetActive(false);
            _exposureLabel.gameObject.SetActive(false);
            _exposureSlider.gameObject.SetActive(false);

            var stamp = CreatePanel("CameraToolbox_PixelBBoxStamp", _proPanel, new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(0f, 28f), new Vector2(246f, 58f), new Color(0.78f, 0.74f, 0.56f, 0.94f));
            CreateText("FormalCameraPixelBBoxStampText", stamp, Vector2.zero, Vector2.one, new Vector2(0.5f, 0.5f), Vector2.zero, Vector2.zero, 14, TextAnchor.MiddleCenter).text = "Pixel BBox stamp slot";

            _feedbackFlash = CreatePanel(
                "FormalCameraModeCaptureFlash",
                _overlayRoot,
                Vector2.zero,
                Vector2.one,
                new Vector2(0.5f, 0.5f),
                Vector2.zero,
                Vector2.zero,
                new Color(1f, 1f, 1f, 0f));
            _feedbackFlash.gameObject.SetActive(false);
            var feedbackImage = _feedbackFlash.GetComponent<Image>();
            if (feedbackImage != null)
                feedbackImage.raycastTarget = false;
            _feedbackBadge = CreateText(
                "FormalCameraModeCaptureBadge",
                _overlayRoot,
                new Vector2(0.5f, 0f),
                new Vector2(0.5f, 0f),
                new Vector2(0.5f, 0f),
                new Vector2(0f, 164f),
                new Vector2(160f, 42f),
                18,
                TextAnchor.MiddleCenter);
            VisualToolHudMetrics.ApplyResponsiveShutterFeedbackLayout(_feedbackBadge.rectTransform);
            _feedbackBadge.gameObject.SetActive(false);
        }

        private void SetVisible(bool visible)
        {
            if (_canvas != null) _canvas.gameObject.SetActive(visible);
        }

        private void RefreshUi()
        {
            if (_canvas == null) return;
            VisualToolHudMetrics.ApplyResponsiveShutterLayout(_shutterButtonRoot);
            if (_feedbackBadge != null)
                VisualToolHudMetrics.ApplyResponsiveShutterFeedbackLayout(_feedbackBadge.rectTransform);
            if (_zoomSlider != null && !Mathf.Approximately(_zoomSlider.value, _zoom))
                _zoomSlider.SetValueWithoutNotify(_zoom);
            if (_exposureSlider != null && !Mathf.Approximately(_exposureSlider.value, _exposure))
                _exposureSlider.SetValueWithoutNotify(_exposure);
            if (_modeLabel != null)
                _modeLabel.text = "CAM " + ModeLabel(_mode) + "  " + _zoom.ToString("0.0") + "x";
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
                   && !status.Contains("not_phone_safe")
                   && !status.Contains("rejected")
                   && !status.Contains("too_large");
        }

        private static bool IsPhotoUploadPendingStatus(string status)
        {
            return !string.IsNullOrWhiteSpace(status)
                   && status.IndexOf("photo_capture_requested", StringComparison.OrdinalIgnoreCase) >= 0;
        }

        private static string TryExtractPhotoIdFromStatus(string status)
        {
            if (string.IsNullOrWhiteSpace(status))
                return "";
            int colon = status.LastIndexOf(':');
            if (colon < 0 || colon >= status.Length - 1)
                return "";
            string id = status.Substring(colon + 1).Trim();
            return id.StartsWith("ph_", StringComparison.OrdinalIgnoreCase) ? id : "";
        }

        private bool ShouldIgnorePhotoUploadCompletion(string photoId)
        {
            if (string.IsNullOrWhiteSpace(_pendingPhotoId))
                return true;
            if (string.IsNullOrWhiteSpace(photoId))
                return true;
            return !string.Equals(_pendingPhotoId, photoId, StringComparison.OrdinalIgnoreCase);
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

        private static RectTransform CreateShutterButton(
            string name,
            Transform parent,
            Func<string> action)
        {
            var rect = CreateArea(
                name,
                parent,
                new Vector2(0.5f, 0f),
                new Vector2(0.5f, 0f),
                new Vector2(0.5f, 0f),
                Vector2.zero,
                VisualToolHudMetrics.BottomShutterSize);
            VisualToolHudMetrics.ApplyResponsiveShutterLayout(rect);
            var image = rect.gameObject.AddComponent<Image>();
            image.sprite = VisualToolPixelSprites.ShutterCircle();
            image.preserveAspect = true;
            image.color = new Color(1f, 1f, 1f, 0.96f);
            image.raycastTarget = true;
            var button = rect.gameObject.AddComponent<Button>();
            button.onClick.AddListener(() => action?.Invoke());

            var inner = CreateArea(
                name + "Inner",
                rect,
                new Vector2(0.5f, 0.5f),
                new Vector2(0.5f, 0.5f),
                new Vector2(0.5f, 0.5f),
                Vector2.zero,
                VisualToolHudMetrics.BottomShutterSize * 0.72f);
            var innerImage = inner.gameObject.AddComponent<Image>();
            innerImage.sprite = VisualToolPixelSprites.ShutterCircle();
            innerImage.preserveAspect = true;
            innerImage.color = new Color(0.08f, 0.065f, 0.055f, 0.94f);
            innerImage.raycastTarget = false;
            return rect;
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

        private void PlayShutterBlackout(string photoId = "")
        {
            EnsureUi();
            if (!string.IsNullOrWhiteSpace(photoId)
                && string.Equals(_lastBlackoutPhotoId, photoId, StringComparison.OrdinalIgnoreCase))
                return;
            if (!string.IsNullOrWhiteSpace(photoId))
                _lastBlackoutPhotoId = photoId;
            _shutterBlackout?.Play();
        }

        private void PlayCaptureFeedback(bool ok)
        {
            EnsureUi();
            if (!IsOpen)
                return;
            if (_feedbackCoroutine != null)
                StopCoroutine(_feedbackCoroutine);
            _feedbackCoroutine = StartCoroutine(CaptureFeedbackRoutine(ok));
        }

        private IEnumerator CaptureFeedbackRoutine(bool ok)
        {
            if (_feedbackBadge != null)
            {
                _feedbackBadge.text = ok ? "OK" : "FAIL";
                _feedbackBadge.color = ok
                    ? new Color(0.72f, 1f, 0.62f, 1f)
                    : new Color(1f, 0.36f, 0.28f, 1f);
                _feedbackBadge.gameObject.SetActive(true);
            }

            if (_feedbackFlash != null)
                _feedbackFlash.gameObject.SetActive(false);

            yield return new WaitForSecondsRealtime(0.75f);
            if (_feedbackBadge != null)
                _feedbackBadge.gameObject.SetActive(false);
            _feedbackCoroutine = null;
        }

        private void HandlePinchViewZoom()
        {
            if (!enablePinchViewZoom || Input.touchCount < 2)
            {
                _pinchStartDistance = 0f;
                return;
            }

            var a = Input.GetTouch(0);
            var b = Input.GetTouch(1);
            if (IsFingerOverUi(a.fingerId) || IsFingerOverUi(b.fingerId))
                return;

            float distance = Vector2.Distance(a.position, b.position);
            if (_pinchStartDistance <= 1f
                || a.phase == TouchPhase.Began
                || b.phase == TouchPhase.Began)
            {
                _pinchStartDistance = Mathf.Max(1f, distance);
                _pinchStartZoom = Mathf.Max(0.1f, _zoom);
                LastCameraStatus = "camera_zoom_pinch_start";
                RefreshUi();
                return;
            }

            float nextZoom = _pinchStartZoom * distance / Mathf.Max(1f, _pinchStartDistance);
            _zoom = Mathf.Clamp(nextZoom, Mathf.Max(1f, minViewZoom), Mathf.Max(minViewZoom, maxViewZoom));
            LastCameraStatus = "camera_zoom_" + _zoom.ToString("0.0");
            ApplyCameraViewZoom();
            RefreshUi();
        }

        private static bool IsFingerOverUi(int fingerId)
        {
            return EventSystem.current != null && EventSystem.current.IsPointerOverGameObject(fingerId);
        }

        private void ApplyCameraViewZoom()
        {
            if (_zoomCamera == null)
                _zoomCamera = Camera.main;
            if (_zoomCamera == null)
                return;

            if (!_hasCameraZoomBase)
            {
                _baseCameraFieldOfView = _zoomCamera.fieldOfView;
                _baseCameraOrthographicSize = _zoomCamera.orthographicSize;
                _hasCameraZoomBase = true;
            }

            float zoomValue = Mathf.Clamp(_zoom, Mathf.Max(1f, minViewZoom), Mathf.Max(minViewZoom, maxViewZoom));
            if (_zoomCamera.orthographic)
                _zoomCamera.orthographicSize = Mathf.Max(0.01f, _baseCameraOrthographicSize / zoomValue);
            else
                _zoomCamera.fieldOfView = Mathf.Clamp(_baseCameraFieldOfView / zoomValue, 12f, _baseCameraFieldOfView);
        }

        private void ResetCameraViewZoom()
        {
            if (_zoomCamera == null)
                _zoomCamera = Camera.main;
            if (_zoomCamera != null && _hasCameraZoomBase)
            {
                if (_zoomCamera.orthographic)
                    _zoomCamera.orthographicSize = _baseCameraOrthographicSize;
                else
                    _zoomCamera.fieldOfView = _baseCameraFieldOfView;
            }
            _zoom = Mathf.Clamp(defaultZoom, Mathf.Max(minZoom, minViewZoom), Mathf.Max(maxZoom, maxViewZoom));
            _pinchStartDistance = 0f;
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
