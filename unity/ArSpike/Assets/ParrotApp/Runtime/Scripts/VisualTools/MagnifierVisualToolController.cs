using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace ParrotApp.VisualTools
{
    [DisallowMultipleComponent]
    public class MagnifierVisualToolController : VisualToolControllerBase
    {
        [Header("Magnifier")]
        [SerializeField] private float zoom = 2.0f;
        [SerializeField] private float minZoom = 1.0f;
        [SerializeField] private float maxZoom = 4.0f;
        [SerializeField] private float zoomStep = 0.25f;
        [SerializeField] private bool enableLocalPointerInput = true;
        [SerializeField] private bool emitDwellTicks = true;
        [SerializeField] private float dwellAfterStillSeconds = 1.25f;
        [SerializeField] private float dwellTickIntervalSeconds = 2.5f;
        [SerializeField] private float minLensWidth = 0.10f;
        [SerializeField] private float minLensHeight = 0.10f;
        [SerializeField] private bool enablePinchResizeAndZoom = true;
        [SerializeField] private bool showDevActionButtons = false;
        [SerializeField] private bool showConfirmShutter = true;
        [SerializeField] private bool enableLiveLensRender = true;
        [SerializeField] private float liveLensFrameIntervalSeconds = 0.12f;
        [SerializeField] private int liveLensCameraMaxDimension = 960;

        private Canvas _canvas;
        private RectTransform _lensRoot;
        private RectTransform _confirmShutterRoot;
        private RectTransform _liveLensViewport;
        private RawImage _liveLensImage;
        private RectTransform _zoomRailRoot;
        private RectTransform _zoomRailFill;
        private RectTransform _feedbackFlash;
        private Text _feedbackBadge;
        private VisualToolShutterBlackoutFeedback _shutterBlackout;
        private Coroutine _feedbackCoroutine;
        private Coroutine _liveLensCoroutine;
        private Texture2D _liveLensTexture;
        private Text _statusText;
        private Text _lockButtonText;
        private Image _lensFill;
        private Image[] _selectionOutlines;
        private bool _pointerActive;
        private bool _pinchActive;
        private float _pinchStartDistance;
        private float _pinchStartZoom;
        private VisualToolRegion _pinchStartRegion;
        private float _lastLocalMotionAt = -999f;
        private float _lastDwellTickAt = -999f;
        private readonly List<RectTransform> _captureHiddenOperationRoots = new List<RectTransform>();

        protected override string ToolKind => VisualToolKinds.Mag;
        protected override string ToolLabel => "MAG";
        protected override string SourceSurface => "formal_home.mag";
        protected override VisualToolRegion DefaultRegion => VisualToolHudMetrics.DefaultMagnifierRegion;
        protected override string PreviewDeliveryPreference => VisualToolDeliveryPreferences.IntentOnly;
        protected override string ConfirmDeliveryPreference => VisualToolDeliveryPreferences.IntentOnly;
        protected override string ExplicitSendDeliveryPreference => VisualToolDeliveryPreferences.C3;
        protected override float ConfirmAttentionHint => 0.35f;

        private void Update()
        {
            if (!FeatureEnabled || !IsOpen)
                return;
            if (HandlePinchResizeAndZoom())
                return;
            if (enableLocalPointerInput)
                HandlePointerInput();
            HandleMouseWheelZoom();
            HandleDwellTick();
        }

        protected override string BuildMetaJson(string phase)
        {
            return "{"
                   + "\"client\":\"unity_formal_app\","
                   + "\"feature_flag\":\"dev\","
                   + "\"local_render\":\"mag_live_lens\","
                   + "\"phase\":" + VisualToolPacketBuilder.QuoteJson(phase) + ","
                   + "\"live_lens\":" + (enableLiveLensRender ? "true" : "false") + ","
                   + "\"zoom\":" + zoom.ToString("R", System.Globalization.CultureInfo.InvariantCulture)
                   + "}";
        }

        protected override void UpdateOverlay()
        {
            if (!showDevHud)
                return;
            if (_canvas == null && (!FeatureEnabled || !IsOpen))
                return;
            EnsureOverlay();
            if (_canvas != null)
                _canvas.gameObject.SetActive(FeatureEnabled && IsOpen);
            if (_lensRoot == null)
                return;

            bool operationVisible = !IsScreenRegionAssetOverlayHidden;
            var r = CurrentRegion.Clamped();
            _lensRoot.anchorMin = new Vector2(r.x, 1f - r.y - r.height);
            _lensRoot.anchorMax = new Vector2(r.x + r.width, 1f - r.y);
            _lensRoot.offsetMin = Vector2.zero;
            _lensRoot.offsetMax = Vector2.zero;

            if (_lensFill != null)
                _lensFill.color = Color.white;
            if (_liveLensViewport != null)
                _liveLensViewport.gameObject.SetActive(enableLiveLensRender && _liveLensImage != null);
            if (_selectionOutlines != null)
            {
                bool selected = IsSelected;
                foreach (var image in _selectionOutlines)
                {
                    if (image == null) continue;
                    image.gameObject.SetActive(selected && operationVisible);
                    image.color = new Color(1f, 1f, 1f, 0.96f);
                }
            }
            if (_zoomRailRoot != null)
                _zoomRailRoot.gameObject.SetActive(operationVisible);
            if (_zoomRailFill != null)
            {
                float t = Mathf.InverseLerp(Mathf.Max(0.25f, minZoom), Mathf.Max(minZoom, maxZoom), zoom);
                _zoomRailFill.anchorMax = new Vector2(Mathf.Clamp01(t), 1f);
                _zoomRailFill.offsetMin = Vector2.zero;
                _zoomRailFill.offsetMax = Vector2.zero;
            }
            if (_confirmShutterRoot != null)
            {
                VisualToolHudMetrics.ApplyResponsiveShutterLayout(_confirmShutterRoot);
                _confirmShutterRoot.gameObject.SetActive(showConfirmShutter && operationVisible && FeatureEnabled && IsOpen);
            }
            ApplyRegisteredOperationRootsVisible(operationVisible);
            if (_feedbackFlash != null && !operationVisible)
                _feedbackFlash.gameObject.SetActive(false);
            if (_feedbackBadge != null)
            {
                VisualToolHudMetrics.ApplyResponsiveShutterFeedbackLayout(_feedbackBadge.rectTransform);
                if (!operationVisible)
                    _feedbackBadge.gameObject.SetActive(false);
            }

            if (_statusText != null)
            {
                _statusText.gameObject.SetActive(operationVisible);
                _statusText.text = "MAG x" + zoom.ToString("0.0")
                                   + " " + ShortLabel(LastRenderStatus, "render", 18)
                                   + "\nHTTP " + ShortLabel(LastHttpStatus, "idle", 30)
                                   + "\nASSET " + ShortLabel(LastAssetStatus, "idle", 28)
                                   + "\n" + (_pinchActive ? "PINCH" : (_pointerActive ? "DRAG" : (IsLocked ? "LOCK" : "LOCAL")));
                _statusText.color = LastHttpStatus.Contains("failed") || LastHttpStatus.Contains("missing")
                    ? new Color(0.96f, 0.44f, 0.32f, 0.95f)
                    : new Color(0.96f, 0.86f, 0.48f, 0.95f);
            }
            if (_lockButtonText != null)
                _lockButtonText.text = IsLocked ? "UNLK" : "LOCK";
        }

        private void EnsureOverlay()
        {
            if (_canvas != null) return;

            var root = new GameObject("MagnifierVisualToolDevCanvas");
            root.transform.SetParent(transform, false);
            _canvas = root.AddComponent<Canvas>();
            _canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            _canvas.sortingOrder = 73;
            root.AddComponent<GraphicRaycaster>();
            EnsureEventSystemForDevCanvas();
            _shutterBlackout = root.AddComponent<VisualToolShutterBlackoutFeedback>();

            var scaler = root.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = VisualToolHudMetrics.IqooNeo9LandscapeReferenceResolution;
            scaler.matchWidthOrHeight = 0.5f;

            _lensRoot = CreateArea(
                "MagnifierVisualToolLocalLens",
                root.transform,
                Vector2.zero,
                Vector2.zero,
                new Vector2(0.5f, 0.5f),
                Vector2.zero,
                Vector2.zero);

            _selectionOutlines = CreateSelectionOutlines(_lensRoot);

            var lensSprite = CreateArea(
                "MagnifierVisualToolSprite",
                _lensRoot,
                Vector2.zero,
                Vector2.one,
                new Vector2(0.5f, 0.5f),
                Vector2.zero,
                Vector2.zero);
            _lensFill = lensSprite.gameObject.AddComponent<Image>();
            _lensFill.sprite = VisualToolPixelSprites.Magnifier();
            _lensFill.preserveAspect = true;
            _lensFill.color = Color.white;
            _lensFill.raycastTarget = false;

            CreateLiveLensViewport(_lensRoot);

            _zoomRailRoot = CreateArea(
                "MagnifierZoomRail",
                _lensRoot,
                new Vector2(0.5f, 0f),
                new Vector2(0.5f, 0f),
                new Vector2(0.5f, 0f),
                new Vector2(0f, -74f),
                new Vector2(150f, 12f));
            var railImage = _zoomRailRoot.gameObject.AddComponent<Image>();
            railImage.color = new Color(0.03f, 0.04f, 0.05f, 0.84f);
            railImage.raycastTarget = false;
            _zoomRailFill = CreateArea(
                "MagnifierZoomRailFill",
                _zoomRailRoot,
                Vector2.zero,
                new Vector2(0.5f, 1f),
                new Vector2(0f, 0.5f),
                Vector2.zero,
                Vector2.zero);
            var railFillImage = _zoomRailFill.gameObject.AddComponent<Image>();
            railFillImage.color = new Color(0.70f, 0.90f, 1f, 0.94f);
            railFillImage.raycastTarget = false;

            var status = CreateArea(
                "MagnifierVisualToolStatus",
                _lensRoot,
                new Vector2(0f, 1f),
                new Vector2(1f, 1f),
                new Vector2(0f, 0f),
                new Vector2(8f, 8f),
                new Vector2(-16f, 48f));
            _statusText = status.gameObject.AddComponent<Text>();
            _statusText.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            _statusText.fontSize = 14;
            _statusText.alignment = TextAnchor.UpperLeft;
            _statusText.horizontalOverflow = HorizontalWrapMode.Wrap;
            _statusText.verticalOverflow = VerticalWrapMode.Truncate;
            _statusText.raycastTarget = false;

            if (showDevActionButtons)
            {
                _lockButtonText = CreateCaptureHiddenActionButton("MagnifierDevLockButton", _lensRoot, 0, 8, "LOCK", ToggleSemanticLock);
                CreateCaptureHiddenActionButton("MagnifierDevConfirmButton", _lensRoot, 1, 8, "OK", Confirm);
                CreateCaptureHiddenActionButton("MagnifierDevAssetConfirmButton", _lensRoot, 2, 8, "IMG", ConfirmWithScreenRegionAsset);
                CreateCaptureHiddenActionButton("MagnifierDevExplicitSendButton", _lensRoot, 3, 8, "C3", ExplicitSendWithScreenRegionAsset);
                CreateCaptureHiddenActionButton("MagnifierDevZoomOutButton", _lensRoot, 4, 8, "-", () => AdjustZoom(-zoomStep));
                CreateCaptureHiddenActionButton("MagnifierDevZoomInButton", _lensRoot, 5, 8, "+", () => AdjustZoom(zoomStep));
                CreateCaptureHiddenActionButton("MagnifierDevCancelButton", _lensRoot, 6, 8, "X", Cancel);
                CreateCaptureHiddenActionButton("MagnifierDevReleaseButton", _lensRoot, 7, 8, "REL", Release);
            }

            if (showConfirmShutter)
                _confirmShutterRoot = CreateConfirmShutter("MagnifierVisualToolConfirmShutterButton", root.transform, ConfirmFromShutter);

            CreateConfirmFeedback(root.transform);
        }

        protected override void SetOverlayVisibleForScreenRegionAsset(bool visible)
        {
            if (_canvas != null)
                _canvas.gameObject.SetActive(FeatureEnabled && IsOpen);
            if (visible)
                UpdateOverlay();
            else
                ApplyCaptureOperationVisibility(false);
        }

        protected override void OnScreenRegionAssetCapturedForFeedback(string phase)
        {
            if (string.Equals(phase, VisualToolPhases.Confirm, StringComparison.Ordinal)
                || string.Equals(phase, VisualToolPhases.ExplicitSend, StringComparison.Ordinal))
                _shutterBlackout?.Play();
        }

        protected override void OnPreviewOpened()
        {
            ResetLocalInspectionTiming(endPointerGesture: true, resetDwellTick: true);
            StartLiveLensRendering();
        }

        protected override void OnStableInteractionApplied(string phase)
        {
            ResetLocalInspectionTiming(endPointerGesture: true, resetDwellTick: false);
        }

        protected override void OnStableInteractionReleased(string phase)
        {
            ResetLocalInspectionTiming(endPointerGesture: true, resetDwellTick: true);
        }

        protected override void OnSemanticHttpCompleted(string phase, bool ok, bool hadAsset, string status)
        {
            if (string.Equals(phase, VisualToolPhases.Confirm, System.StringComparison.Ordinal)
                || string.Equals(phase, VisualToolPhases.ExplicitSend, System.StringComparison.Ordinal))
                PlayConfirmFeedback(ok);
        }

        protected override void OnToolClosed(string phase)
        {
            ResetLocalInspectionTiming(endPointerGesture: true, resetDwellTick: true);
            StopLiveLensRendering();
        }

        private void HandlePointerInput()
        {
            if (Input.touchCount >= 2)
                return;
            _pinchActive = false;
            _pinchStartDistance = 0f;
            if (!TryReadPrimaryPointer(out var pointer))
                return;

            if (pointer.pressed)
            {
                if (IsPointerOverUi(pointer))
                    return;
                if (IsLocked)
                {
                    _pointerActive = false;
                    _lastLocalMotionAt = Time.unscaledTime;
                    LastRenderStatus = "mag_locked_unlock_required";
                    SetStatus("mag_locked_unlock_required", true);
                    return;
                }

                Vector2 normalized = ScreenToNormalizedTopLeft(pointer.position);
                if (!RegionContains(CurrentRegion, normalized))
                    CurrentRegion = RegionCenteredAt(normalized, CurrentRegion, minLensWidth, minLensHeight);
                _pointerActive = true;
                IsSelected = true;
                IsLocked = false;
                _lastLocalMotionAt = Time.unscaledTime;
                LastRenderStatus = "mag_local_pointer_begin";
                UpdateOverlay();
                return;
            }

            if (!_pointerActive)
                return;

            if (pointer.held && pointer.delta.sqrMagnitude > 0.01f)
            {
                var r = CurrentRegion.Clamped();
                var delta = ScreenDeltaToNormalizedTopLeft(pointer.delta);
                UpdateLocalRegion(
                    VisualToolRegion.ScreenNormalized(r.x + delta.x, r.y + delta.y, r.width, r.height),
                    VisualToolPhases.DragUpdate);
                _lastLocalMotionAt = Time.unscaledTime;
            }

            if (pointer.released)
            {
                _pointerActive = false;
                _lastLocalMotionAt = Time.unscaledTime;
                SetStatus("mag_local_pointer_release", true);
            }
        }

        private bool HandlePinchResizeAndZoom()
        {
            if (!enablePinchResizeAndZoom || Input.touchCount < 2)
            {
                _pinchActive = false;
                _pinchStartDistance = 0f;
                return false;
            }
            if (IsLocked)
            {
                SetStatus("mag_locked_unlock_required", true);
                return true;
            }

            var a = Input.GetTouch(0);
            var b = Input.GetTouch(1);
            if (IsPointerOverUi(new PointerSample { pointerId = a.fingerId })
                || IsPointerOverUi(new PointerSample { pointerId = b.fingerId }))
                return true;

            float distance = Vector2.Distance(a.position, b.position);
            Vector2 center = (a.position + b.position) * 0.5f;
            if (!_pinchActive
                || _pinchStartDistance <= 1f
                || a.phase == TouchPhase.Began
                || b.phase == TouchPhase.Began)
            {
                _pinchActive = true;
                _pointerActive = false;
                _pinchStartDistance = Mathf.Max(1f, distance);
                _pinchStartZoom = zoom;
                _pinchStartRegion = CurrentRegion.Clamped();
                IsSelected = true;
                IsLocked = false;
                LastRenderStatus = "mag_local_pinch_begin";
                UpdateOverlay();
                return true;
            }

            float ratio = distance / Mathf.Max(1f, _pinchStartDistance);
            zoom = Mathf.Clamp(_pinchStartZoom * ratio, Mathf.Max(0.25f, minZoom), Mathf.Max(minZoom, maxZoom));
            float nextWidth = Mathf.Clamp(_pinchStartRegion.width * ratio, Mathf.Clamp(minLensWidth, 0.02f, 0.95f), 0.80f);
            float nextHeight = Mathf.Clamp(_pinchStartRegion.height * ratio, Mathf.Clamp(minLensHeight, 0.02f, 0.95f), 0.80f);
            Vector2 normalizedCenter = ScreenToNormalizedTopLeft(center);
            UpdateLocalRegion(
                VisualToolRegion.ScreenNormalized(
                    normalizedCenter.x - nextWidth * 0.5f,
                    normalizedCenter.y - nextHeight * 0.5f,
                    nextWidth,
                    nextHeight),
                VisualToolPhases.ResizeUpdate);
            LastRenderStatus = "mag_local_pinch_resize";
            _lastLocalMotionAt = Time.unscaledTime;
            return true;
        }

        private void HandleMouseWheelZoom()
        {
            float wheel = Input.mouseScrollDelta.y;
            if (Mathf.Abs(wheel) < 0.01f) return;
            if (IsLocked)
            {
                SetStatus("mag_locked_unlock_required", true);
                return;
            }
            AdjustZoom(wheel * zoomStep);
        }

        private void HandleDwellTick()
        {
            if (!emitDwellTicks || _pointerActive || IsLocked)
                return;
            float now = Time.unscaledTime;
            if (now - _lastLocalMotionAt < Mathf.Max(0.2f, dwellAfterStillSeconds))
                return;
            if (now - _lastDwellTickAt < Mathf.Max(0.5f, dwellTickIntervalSeconds))
                return;
            _lastDwellTickAt = now;
            DwellTick();
        }

        public string SetZoom(float value)
        {
            if (IsLocked)
                return SetStatus("mag_locked_unlock_required", true);
            zoom = Mathf.Clamp(value, Mathf.Max(0.25f, minZoom), Mathf.Max(minZoom, maxZoom));
            LastRenderStatus = "mag_local_zoom_changed";
            UpdateOverlay();
            return SetStatus("mag_local_zoom_" + zoom.ToString("0.0"), true);
        }

        public string AdjustZoom(float delta)
        {
            return SetZoom(zoom + delta);
        }

        private string ToggleSemanticLock()
        {
            return IsLocked ? Unlock() : Lock();
        }

        private string ConfirmFromShutter()
        {
            string status = ConfirmWithScreenRegionAsset();
            if (!IsBackendCompletionPendingStatus(status))
                PlayConfirmFeedback(ToolStatusLooksOk(status));
            return status;
        }

        private void PlayConfirmFeedback(bool ok)
        {
            if (_feedbackBadge == null || _feedbackFlash == null || _canvas == null)
                return;
            if (_feedbackCoroutine != null)
                StopCoroutine(_feedbackCoroutine);
            _feedbackCoroutine = StartCoroutine(ConfirmFeedbackRoutine(ok));
        }

        private IEnumerator ConfirmFeedbackRoutine(bool ok)
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

        private static bool ToolStatusLooksOk(string status)
        {
            if (string.IsNullOrWhiteSpace(status)) return false;
            string s = status.ToLowerInvariant();
            return !(s.Contains("failed")
                     || s.Contains("missing")
                     || s.Contains("error")
                     || s.Contains("off")
                     || s.Contains("disabled"));
        }

        private void ResetLocalInspectionTiming(bool endPointerGesture, bool resetDwellTick)
        {
            if (endPointerGesture)
                _pointerActive = false;
            _pinchActive = false;
            _pinchStartDistance = 0f;
            _lastLocalMotionAt = Time.unscaledTime;
            if (resetDwellTick)
                _lastDwellTickAt = -999f;
        }

        private void StartLiveLensRendering()
        {
            if (!enableLiveLensRender || _liveLensCoroutine != null)
                return;
            _liveLensCoroutine = StartCoroutine(LiveLensRenderLoop());
        }

        private void StopLiveLensRendering()
        {
            if (_liveLensCoroutine != null)
            {
                StopCoroutine(_liveLensCoroutine);
                _liveLensCoroutine = null;
            }
            if (_liveLensImage != null)
                _liveLensImage.texture = null;
            if (_liveLensTexture != null)
            {
                Destroy(_liveLensTexture);
                _liveLensTexture = null;
            }
        }

        private IEnumerator LiveLensRenderLoop()
        {
            while (enableLiveLensRender && FeatureEnabled && IsOpen)
            {
                yield return new WaitForEndOfFrame();
                if (!enableLiveLensRender || !FeatureEnabled || !IsOpen)
                    break;

                string error;
                bool rendered = TryRenderLiveLensFromCamera(out error) || TryRenderLiveLensFromScreen(out error);
                if (rendered)
                {
                    LastRenderStatus = "mag_live_lens_rendering";
                }
                else if (!string.IsNullOrWhiteSpace(error))
                {
                    LastRenderStatus = "mag_live_lens_unavailable:" + error;
                }
                UpdateOverlay();

                yield return new WaitForSecondsRealtime(Mathf.Max(0.03f, liveLensFrameIntervalSeconds));
            }
            _liveLensCoroutine = null;
        }

        private bool TryRenderLiveLensFromCamera(out string error)
        {
            error = "";
            var cam = Camera.main;
            if (cam == null)
            {
                error = "camera_missing";
                return false;
            }

            int screenWidth = Mathf.Max(1, Screen.width);
            int screenHeight = Mathf.Max(1, Screen.height);
            int maxDimension = Mathf.Clamp(liveLensCameraMaxDimension, 160, 2048);
            float scale = Mathf.Min(1f, maxDimension / (float)Mathf.Max(screenWidth, screenHeight));
            int captureWidth = Mathf.Max(1, Mathf.RoundToInt(screenWidth * scale));
            int captureHeight = Mathf.Max(1, Mathf.RoundToInt(screenHeight * scale));

            RenderTexture rt = RenderTexture.GetTemporary(captureWidth, captureHeight, 24, RenderTextureFormat.ARGB32);
            RenderTexture previousActive = RenderTexture.active;
            RenderTexture previousTarget = cam.targetTexture;
            try
            {
                cam.targetTexture = rt;
                cam.Render();
                RenderTexture.active = rt;
                return ReadLiveLensPixelsFromActiveTexture(captureWidth, captureHeight, out error);
            }
            catch (Exception ex)
            {
                error = "camera_render_failed:" + ex.GetType().Name;
                return false;
            }
            finally
            {
                cam.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                RenderTexture.ReleaseTemporary(rt);
            }
        }

        private bool TryRenderLiveLensFromScreen(out string error)
        {
            error = "";
            try
            {
                return ReadLiveLensPixelsFromActiveTexture(Mathf.Max(1, Screen.width), Mathf.Max(1, Screen.height), out error);
            }
            catch (Exception ex)
            {
                error = "screen_read_failed:" + ex.GetType().Name;
                return false;
            }
        }

        private bool ReadLiveLensPixelsFromActiveTexture(int sourceWidth, int sourceHeight, out string error)
        {
            error = "";
            if (_liveLensImage == null)
            {
                error = "live_lens_image_missing";
                return false;
            }

            Rect rect = LiveLensPixelRect(sourceWidth, sourceHeight);
            int width = Mathf.Max(1, Mathf.RoundToInt(rect.width));
            int height = Mathf.Max(1, Mathf.RoundToInt(rect.height));
            EnsureLiveLensTexture(width, height);
            _liveLensTexture.ReadPixels(rect, 0, 0, false);
            _liveLensTexture.Apply(false);
            _liveLensImage.texture = _liveLensTexture;
            _liveLensImage.color = new Color(1f, 1f, 1f, 0.90f);
            return true;
        }

        private Rect LiveLensPixelRect(int sourceWidth, int sourceHeight)
        {
            var r = CurrentRegion.Clamped();
            float screenWidth = Mathf.Max(1f, Screen.width);
            float screenHeight = Mathf.Max(1f, Screen.height);
            float lensDiameterPixels = Mathf.Min(
                Mathf.Max(1f, r.width * screenWidth * 0.82f),
                Mathf.Max(1f, r.height * screenHeight * 0.58f));
            float safeZoom = Mathf.Clamp(zoom, Mathf.Max(0.25f, minZoom), Mathf.Max(minZoom, maxZoom));
            float sourceWidthNormalized = Mathf.Clamp(lensDiameterPixels / screenWidth / safeZoom, 0.01f, 1f);
            float sourceHeightNormalized = Mathf.Clamp(lensDiameterPixels / screenHeight / safeZoom, 0.01f, 1f);
            float centerX = r.x + r.width * 0.5f;
            float centerY = r.y + r.height * 0.30f;
            var source = VisualToolRegion.ScreenNormalized(
                centerX - sourceWidthNormalized * 0.5f,
                centerY - sourceHeightNormalized * 0.5f,
                sourceWidthNormalized,
                sourceHeightNormalized);

            int x = Mathf.Clamp(Mathf.RoundToInt(source.x * sourceWidth), 0, sourceWidth - 1);
            int y = Mathf.Clamp(Mathf.RoundToInt((1f - source.y - source.height) * sourceHeight), 0, sourceHeight - 1);
            int width = Mathf.Clamp(Mathf.RoundToInt(source.width * sourceWidth), 1, sourceWidth - x);
            int height = Mathf.Clamp(Mathf.RoundToInt(source.height * sourceHeight), 1, sourceHeight - y);
            return new Rect(x, y, width, height);
        }

        private void EnsureLiveLensTexture(int width, int height)
        {
            if (_liveLensTexture != null && _liveLensTexture.width == width && _liveLensTexture.height == height)
                return;
            if (_liveLensTexture != null)
                Destroy(_liveLensTexture);
            _liveLensTexture = new Texture2D(width, height, TextureFormat.RGB24, false);
            _liveLensTexture.wrapMode = TextureWrapMode.Clamp;
            _liveLensTexture.filterMode = FilterMode.Point;
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

        private Text CreateCaptureHiddenActionButton(
            string name,
            Transform parent,
            int index,
            int total,
            string label,
            Func<string> action)
        {
            var text = CreateActionButton(name, parent, index, total, label, action);
            var root = text != null ? text.transform.parent as RectTransform : null;
            if (root != null)
                _captureHiddenOperationRoots.Add(root);
            return text;
        }

        private void ApplyRegisteredOperationRootsVisible(bool visible)
        {
            for (int i = 0; i < _captureHiddenOperationRoots.Count; i++)
            {
                var root = _captureHiddenOperationRoots[i];
                if (root != null)
                    root.gameObject.SetActive(visible && showDevActionButtons);
            }
        }

        private void ApplyCaptureOperationVisibility(bool visible)
        {
            bool selectedVisible = visible && IsSelected;
            if (_selectionOutlines != null)
            {
                foreach (var image in _selectionOutlines)
                {
                    if (image != null)
                        image.gameObject.SetActive(selectedVisible);
                }
            }
            if (_zoomRailRoot != null)
                _zoomRailRoot.gameObject.SetActive(visible);
            if (_confirmShutterRoot != null)
                _confirmShutterRoot.gameObject.SetActive(visible && showConfirmShutter && FeatureEnabled && IsOpen);
            if (_statusText != null)
                _statusText.gameObject.SetActive(visible);
            if (_feedbackFlash != null)
                _feedbackFlash.gameObject.SetActive(false);
            if (_feedbackBadge != null && !visible)
                _feedbackBadge.gameObject.SetActive(false);
            ApplyRegisteredOperationRootsVisible(visible);
        }

        private static Text CreateActionButton(
            string name,
            Transform parent,
            int index,
            int total,
            string label,
            Func<string> action)
        {
            float width = 48f;
            float gap = 6f;
            float x = -((total - 1) * (width + gap)) * 0.5f + index * (width + gap);
            var rect = CreateArea(
                name,
                parent,
                new Vector2(0.5f, 0f),
                new Vector2(0.5f, 0f),
                new Vector2(0.5f, 0f),
                new Vector2(x, -46f),
                new Vector2(width, 32f));
            var image = rect.gameObject.AddComponent<Image>();
            image.color = new Color(0.12f, 0.10f, 0.06f, 0.88f);
            image.raycastTarget = true;
            var button = rect.gameObject.AddComponent<Button>();
            button.onClick.AddListener(() => action?.Invoke());

            var textRect = CreateArea(
                name + "Label",
                rect,
                Vector2.zero,
                Vector2.one,
                new Vector2(0.5f, 0.5f),
                Vector2.zero,
                Vector2.zero);
            var text = textRect.gameObject.AddComponent<Text>();
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            text.fontSize = 12;
            text.alignment = TextAnchor.MiddleCenter;
            text.horizontalOverflow = HorizontalWrapMode.Overflow;
            text.verticalOverflow = VerticalWrapMode.Truncate;
            text.text = label;
            text.color = new Color(0.98f, 0.88f, 0.56f, 0.96f);
            text.raycastTarget = false;
            return text;
        }

        private static Image[] CreateSelectionOutlines(Transform parent)
        {
            var offsets = new[]
            {
                new Vector2(-5f, 0f),
                new Vector2(5f, 0f),
                new Vector2(0f, -5f),
                new Vector2(0f, 5f),
                new Vector2(-4f, -4f),
                new Vector2(-4f, 4f),
                new Vector2(4f, -4f),
                new Vector2(4f, 4f),
            };
            var images = new Image[offsets.Length];
            for (int i = 0; i < offsets.Length; i++)
            {
                var rect = CreateArea(
                    "MagnifierSelectedWhitePixelOutline" + i,
                    parent,
                    Vector2.zero,
                    Vector2.one,
                    new Vector2(0.5f, 0.5f),
                    offsets[i],
                    Vector2.zero);
                var image = rect.gameObject.AddComponent<Image>();
                image.sprite = VisualToolPixelSprites.Magnifier();
                image.preserveAspect = true;
                image.color = new Color(1f, 1f, 1f, 0.96f);
                image.raycastTarget = false;
                image.gameObject.SetActive(false);
                images[i] = image;
            }
            return images;
        }

        private void CreateLiveLensViewport(Transform parent)
        {
            _liveLensViewport = CreateArea(
                "MagnifierLiveLensViewport",
                parent,
                new Vector2(0.11f, 0.47f),
                new Vector2(0.89f, 0.94f),
                new Vector2(0.5f, 0.5f),
                Vector2.zero,
                Vector2.zero);
            var maskImage = _liveLensViewport.gameObject.AddComponent<Image>();
            maskImage.sprite = VisualToolPixelSprites.WhiteCircle();
            maskImage.preserveAspect = true;
            maskImage.color = Color.white;
            maskImage.raycastTarget = false;
            var mask = _liveLensViewport.gameObject.AddComponent<Mask>();
            mask.showMaskGraphic = false;

            var textureRect = CreateArea(
                "MagnifierLiveLensTexture",
                _liveLensViewport,
                Vector2.zero,
                Vector2.one,
                new Vector2(0.5f, 0.5f),
                Vector2.zero,
                Vector2.zero);
            _liveLensImage = textureRect.gameObject.AddComponent<RawImage>();
            _liveLensImage.color = new Color(1f, 1f, 1f, 0.90f);
            _liveLensImage.raycastTarget = false;
            _liveLensImage.uvRect = new Rect(0f, 0f, 1f, 1f);
        }

        private static RectTransform CreateConfirmShutter(string name, Transform parent, Func<string> action)
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

        private void CreateConfirmFeedback(Transform parent)
        {
            _feedbackFlash = CreateArea(
                "MagnifierVisualToolConfirmFlash",
                parent,
                Vector2.zero,
                Vector2.one,
                new Vector2(0.5f, 0.5f),
                Vector2.zero,
                Vector2.zero);
            var flashImage = _feedbackFlash.gameObject.AddComponent<Image>();
            flashImage.color = new Color(1f, 1f, 1f, 0f);
            flashImage.raycastTarget = false;
            _feedbackFlash.gameObject.SetActive(false);

            var badge = CreateArea(
                "MagnifierVisualToolConfirmFeedbackBadge",
                parent,
                new Vector2(0.5f, 0f),
                new Vector2(0.5f, 0f),
                new Vector2(0.5f, 0f),
                Vector2.zero,
                VisualToolHudMetrics.ShutterFeedbackSize);
            VisualToolHudMetrics.ApplyResponsiveShutterFeedbackLayout(badge);
            _feedbackBadge = badge.gameObject.AddComponent<Text>();
            _feedbackBadge.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            _feedbackBadge.fontSize = 18;
            _feedbackBadge.alignment = TextAnchor.MiddleCenter;
            _feedbackBadge.horizontalOverflow = HorizontalWrapMode.Wrap;
            _feedbackBadge.verticalOverflow = VerticalWrapMode.Truncate;
            _feedbackBadge.raycastTarget = false;
            _feedbackBadge.gameObject.SetActive(false);
        }

        private static string ShortLabel(string primary, string fallback, int max)
        {
            string text = string.IsNullOrWhiteSpace(primary) ? (fallback ?? "") : primary;
            text = text.Trim();
            if (text.Length <= max) return text;
            return text.Substring(0, Mathf.Max(1, max - 3)) + "...";
        }
    }
}
