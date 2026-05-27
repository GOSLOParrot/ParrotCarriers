using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace ParrotApp.VisualTools
{
    [DisallowMultipleComponent]
    public class BBoxVisualToolController : VisualToolControllerBase
    {
        [Header("Local Interaction")]
        [SerializeField] private bool enableLocalPointerInput = true;
        [SerializeField] private bool emitLockOnPointerRelease = false;
        [SerializeField] private float minBoxWidth = 0.08f;
        [SerializeField] private float minBoxHeight = 0.08f;
        [SerializeField] private float edgeHandlePixels = 34f;
        [SerializeField] private bool enablePinchResize = true;
        [SerializeField] private bool showDevActionButtons = false;
        [SerializeField] private bool showConfirmShutter = true;
        [SerializeField] private string sampleLabel = "object";
        [SerializeField] private string[] sampleLabelOptions = { "object", "person", "document", "screen", "unknown" };
        [SerializeField] private int sampleColorIndex = 0;

        private enum BBoxInteractionMode
        {
            None,
            Move,
            ResizeLeft,
            ResizeRight,
            ResizeTop,
            ResizeBottom,
            ResizeTopLeft,
            ResizeTopRight,
            ResizeBottomLeft,
            ResizeBottomRight,
        }

        private Canvas _canvas;
        private RectTransform _boxRoot;
        private Text _statusText;
        private Text _lockButtonText;
        private RectTransform _sampleChipRoot;
        private Text _sampleLabelText;
        private Image _sampleColorSwatch;
        private RectTransform _semanticLabelRoot;
        private Text _semanticLabelText;
        private Image _semanticLabelBackground;
        private RectTransform _confirmShutterRoot;
        private RectTransform _feedbackFlash;
        private Text _feedbackBadge;
        private VisualToolShutterBlackoutFeedback _shutterBlackout;
        private Coroutine _feedbackCoroutine;
        private Image _fill;
        private Image[] _edges;
        private Image[] _selectionEdges;
        private Image[] _cornerHandles;
        private readonly List<RectTransform> _captureHiddenOperationRoots = new List<RectTransform>();
        private BBoxInteractionMode _interactionMode = BBoxInteractionMode.None;
        private bool _pointerActive;
        private bool _pinchActive;
        private float _pinchStartDistance;
        private VisualToolRegion _pinchStartRegion;

        protected override string ToolKind => VisualToolKinds.BBox;
        protected override string ToolLabel => "BBox:" + CurrentSampleLabel;
        protected override string SourceSurface => "formal_home.bbox";
        protected override VisualToolRegion DefaultRegion => VisualToolHudMetrics.DefaultBBoxRegion;
        protected override string ConfirmDeliveryPreference => VisualToolDeliveryPreferences.Default;
        protected override float ConfirmAttentionHint => 1.0f;

        private static readonly string[] FallbackSampleLabels =
        {
            "object",
            "person",
            "document",
            "screen",
            "unknown",
        };

        private static readonly string[] SampleColorKeys =
        {
            "red",
            "green",
            "blue",
            "yellow",
            "magenta",
        };

        private static readonly Color[] SampleColors =
        {
            new Color(1f, 0.08f, 0.06f, 0.92f),
            new Color(0.05f, 0.92f, 0.28f, 0.92f),
            new Color(0.10f, 0.36f, 1f, 0.92f),
            new Color(1f, 0.86f, 0.12f, 0.92f),
            new Color(1f, 0.08f, 0.86f, 0.92f),
        };

        private string CurrentSampleLabel => NormalizeSampleLabel(sampleLabel);
        private string CurrentSampleColorKey => SampleColorKeys[NormalizedSampleColorIndex()];
        private Color CurrentSampleColor => SampleColors[NormalizedSampleColorIndex()];

        protected override string BuildMetaJson(string phase)
        {
            string colorKey = CurrentSampleColorKey;
            string colorHex = ColorUtility.ToHtmlStringRGB(CurrentSampleColor);
            return "{"
                   + "\"client\":\"unity_formal_app\","
                   + "\"feature_flag\":\"dev\","
                   + "\"local_render\":\"bbox_sample_overlay\","
                   + "\"phase\":" + VisualToolPacketBuilder.QuoteJson(phase) + ","
                   + "\"sample_label\":" + VisualToolPacketBuilder.QuoteJson(CurrentSampleLabel) + ","
                   + "\"sample_color\":" + VisualToolPacketBuilder.QuoteJson(colorKey) + ","
                   + "\"sample_color_hex\":" + VisualToolPacketBuilder.QuoteJson("#" + colorHex)
                   + "}";
        }

        private void Update()
        {
            if (!FeatureEnabled || !IsOpen || !enableLocalPointerInput)
                return;
            if (HandlePinchResize())
                return;
            HandlePointerInput();
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
            if (_boxRoot == null)
                return;

            bool operationVisible = !IsScreenRegionAssetOverlayHidden;
            var r = CurrentRegion.Clamped();
            _boxRoot.anchorMin = new Vector2(r.x, 1f - r.y - r.height);
            _boxRoot.anchorMax = new Vector2(r.x + r.width, 1f - r.y);
            _boxRoot.offsetMin = Vector2.zero;
            _boxRoot.offsetMax = Vector2.zero;

            Color sampleColor = CurrentSampleColor;
            Color edge = IsLocked
                ? new Color(1f, 0.88f, 0.24f, 0.98f)
                : sampleColor;
            if (_fill != null)
                _fill.color = IsLocked
                    ? new Color(0.45f, 0.36f, 0.05f, 0.04f)
                    : new Color(sampleColor.r, sampleColor.g, sampleColor.b, 0.00f);
            if (_edges != null)
            {
                foreach (var image in _edges)
                {
                    if (image != null) image.color = edge;
                }
            }
            bool selected = IsSelected;
            if (_selectionEdges != null)
            {
                foreach (var image in _selectionEdges)
                {
                    if (image == null) continue;
                    image.gameObject.SetActive(selected && operationVisible);
                    image.color = new Color(1f, 1f, 1f, 0.96f);
                }
            }
            if (_cornerHandles != null)
            {
                foreach (var image in _cornerHandles)
                {
                    if (image == null) continue;
                    image.gameObject.SetActive(selected && operationVisible);
                    image.color = new Color(1f, 1f, 1f, 0.98f);
                }
            }
            if (_sampleChipRoot != null)
                _sampleChipRoot.gameObject.SetActive(selected && IsOpen && operationVisible);
            if (_sampleLabelText != null)
                _sampleLabelText.text = ShortLabel(CurrentSampleLabel.ToUpperInvariant(), "OBJECT", 12);
            if (_sampleColorSwatch != null)
                _sampleColorSwatch.color = new Color(sampleColor.r, sampleColor.g, sampleColor.b, 0.96f);
            if (_semanticLabelRoot != null)
                _semanticLabelRoot.gameObject.SetActive(IsOpen);
            if (_semanticLabelBackground != null)
                _semanticLabelBackground.color = new Color(sampleColor.r, sampleColor.g, sampleColor.b, 0.96f);
            if (_semanticLabelText != null)
                _semanticLabelText.text = ShortLabel(CurrentSampleLabel.ToUpperInvariant(), "OBJECT", 12);
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
                _statusText.text = "BOX " + ShortLabel(LastRenderStatus, "render", 24)
                                   + "\nSAMPLE " + ShortLabel(CurrentSampleLabel, "object", 16)
                                   + "\nHTTP " + ShortLabel(LastHttpStatus, "idle", 32)
                                   + "\nASSET " + ShortLabel(LastAssetStatus, "idle", 30)
                                   + "\n" + (_pinchActive ? "PINCH" : (_interactionMode == BBoxInteractionMode.None
                                       ? (IsLocked ? "LOCK" : "LOCAL")
                                       : _interactionMode.ToString()));
                _statusText.color = LastHttpStatus.Contains("failed") || LastHttpStatus.Contains("missing")
                    ? new Color(0.96f, 0.44f, 0.32f, 0.95f)
                    : new Color(0.72f, 0.96f, 0.58f, 0.95f);
            }
            if (_lockButtonText != null)
                _lockButtonText.text = IsLocked ? "UNLK" : "LOCK";
        }

        private void EnsureOverlay()
        {
            if (_canvas != null) return;

            var root = new GameObject("BBoxVisualToolDevCanvas");
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

            _boxRoot = CreateArea(
                "BBoxVisualToolLocalRegion",
                root.transform,
                Vector2.zero,
                Vector2.zero,
                new Vector2(0.5f, 0.5f),
                Vector2.zero,
                Vector2.zero);

            _fill = _boxRoot.gameObject.AddComponent<Image>();
            _fill.color = new Color(0.16f, 0.28f, 0.10f, 0.12f);
            _fill.raycastTarget = false;

            _edges = new Image[4];
            _edges[0] = CreateEdge("Top", _boxRoot, new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(0.5f, 1f), new Vector2(0f, -3f), new Vector2(0f, 8f));
            _edges[1] = CreateEdge("Bottom", _boxRoot, new Vector2(0f, 0f), new Vector2(1f, 0f), new Vector2(0.5f, 0f), new Vector2(0f, 3f), new Vector2(0f, 8f));
            _edges[2] = CreateEdge("Left", _boxRoot, new Vector2(0f, 0f), new Vector2(0f, 1f), new Vector2(0f, 0.5f), new Vector2(3f, 0f), new Vector2(8f, 0f));
            _edges[3] = CreateEdge("Right", _boxRoot, new Vector2(1f, 0f), new Vector2(1f, 1f), new Vector2(1f, 0.5f), new Vector2(-3f, 0f), new Vector2(8f, 0f));

            _selectionEdges = new Image[4];
            _selectionEdges[0] = CreateEdge("SelectedTop", _boxRoot, new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(0.5f, 1f), new Vector2(0f, 7f), new Vector2(0f, 6f));
            _selectionEdges[1] = CreateEdge("SelectedBottom", _boxRoot, new Vector2(0f, 0f), new Vector2(1f, 0f), new Vector2(0.5f, 0f), new Vector2(0f, -7f), new Vector2(0f, 6f));
            _selectionEdges[2] = CreateEdge("SelectedLeft", _boxRoot, new Vector2(0f, 0f), new Vector2(0f, 1f), new Vector2(0f, 0.5f), new Vector2(-7f, 0f), new Vector2(6f, 0f));
            _selectionEdges[3] = CreateEdge("SelectedRight", _boxRoot, new Vector2(1f, 0f), new Vector2(1f, 1f), new Vector2(1f, 0.5f), new Vector2(7f, 0f), new Vector2(6f, 0f));

            _cornerHandles = new Image[4];
            _cornerHandles[0] = CreateHandle("TopLeft", _boxRoot, new Vector2(0f, 1f), new Vector2(-8f, 8f));
            _cornerHandles[1] = CreateHandle("TopRight", _boxRoot, new Vector2(1f, 1f), new Vector2(8f, 8f));
            _cornerHandles[2] = CreateHandle("BottomLeft", _boxRoot, new Vector2(0f, 0f), new Vector2(-8f, -8f));
            _cornerHandles[3] = CreateHandle("BottomRight", _boxRoot, new Vector2(1f, 0f), new Vector2(8f, -8f));

            CreateSemanticSampleLabel(_boxRoot);
            CreateSampleAttributeStrip(_boxRoot);

            var status = CreateArea(
                "BBoxVisualToolStatus",
                _boxRoot,
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
                _lockButtonText = CreateCaptureHiddenActionButton("BBoxDevLockButton", _boxRoot, 0, 6, "LOCK", ToggleSemanticLock);
                CreateCaptureHiddenActionButton("BBoxDevConfirmButton", _boxRoot, 1, 6, "OK", Confirm);
                CreateCaptureHiddenActionButton("BBoxDevAssetConfirmButton", _boxRoot, 2, 6, "IMG", ConfirmWithScreenRegionAsset);
                CreateCaptureHiddenActionButton("BBoxDevExplicitSendButton", _boxRoot, 3, 6, "C3", ExplicitSendWithScreenRegionAsset);
                CreateCaptureHiddenActionButton("BBoxDevCancelButton", _boxRoot, 4, 6, "X", Cancel);
                CreateCaptureHiddenActionButton("BBoxDevReleaseButton", _boxRoot, 5, 6, "REL", Release);
            }

            if (showConfirmShutter)
                _confirmShutterRoot = CreateConfirmShutter("BBoxVisualToolConfirmShutterButton", root.transform, ConfirmFromShutter);

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
            EndLocalPointerGesture();
        }

        protected override void OnStableInteractionApplied(string phase)
        {
            EndLocalPointerGesture();
        }

        protected override void OnStableInteractionReleased(string phase)
        {
            EndLocalPointerGesture();
        }

        protected override void OnSemanticHttpCompleted(string phase, bool ok, bool hadAsset, string status)
        {
            if (string.Equals(phase, VisualToolPhases.Confirm, System.StringComparison.Ordinal)
                || string.Equals(phase, VisualToolPhases.ExplicitSend, System.StringComparison.Ordinal))
                PlayConfirmFeedback(ok);
        }

        protected override void OnToolClosed(string phase)
        {
            EndLocalPointerGesture();
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
                    _interactionMode = BBoxInteractionMode.None;
                    LastRenderStatus = "bbox_locked_unlock_required";
                    SetStatus("bbox_locked_unlock_required", true);
                    return;
                }

                Vector2 normalized = ScreenToNormalizedTopLeft(pointer.position);
                if (!RegionContains(CurrentRegion, normalized))
                    CurrentRegion = RegionCenteredAt(normalized, CurrentRegion, minBoxWidth, minBoxHeight);
                _interactionMode = HitTestInteraction(pointer.position);
                _pointerActive = true;
                IsSelected = true;
                IsLocked = false;
                LastRenderStatus = "bbox_local_pointer_begin";
                UpdateOverlay();
                return;
            }

            if (!_pointerActive)
                return;

            if (pointer.held && pointer.delta.sqrMagnitude > 0.01f)
            {
                var delta = ScreenDeltaToNormalizedTopLeft(pointer.delta);
                var region = ApplyInteractionDelta(CurrentRegion, delta, _interactionMode);
                string phase = _interactionMode == BBoxInteractionMode.Move
                    ? VisualToolPhases.DragUpdate
                    : VisualToolPhases.ResizeUpdate;
                UpdateLocalRegion(region, phase);
            }

            if (pointer.released)
            {
                _pointerActive = false;
                _interactionMode = BBoxInteractionMode.None;
                if (emitLockOnPointerRelease)
                    Lock();
                else
                    SetStatus("bbox_local_pointer_release", true);
            }
        }

        private bool HandlePinchResize()
        {
            if (!enablePinchResize || Input.touchCount < 2)
            {
                _pinchActive = false;
                _pinchStartDistance = 0f;
                return false;
            }
            if (IsLocked)
            {
                SetStatus("bbox_locked_unlock_required", true);
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
                _interactionMode = BBoxInteractionMode.None;
                _pinchStartDistance = Mathf.Max(1f, distance);
                _pinchStartRegion = CurrentRegion.Clamped();
                IsSelected = true;
                IsLocked = false;
                LastRenderStatus = "bbox_local_pinch_begin";
                UpdateOverlay();
                return true;
            }

            float ratio = distance / Mathf.Max(1f, _pinchStartDistance);
            float nextWidth = Mathf.Clamp(_pinchStartRegion.width * ratio, Mathf.Clamp(minBoxWidth, 0.02f, 0.95f), 0.95f);
            float nextHeight = Mathf.Clamp(_pinchStartRegion.height * ratio, Mathf.Clamp(minBoxHeight, 0.02f, 0.95f), 0.95f);
            Vector2 normalizedCenter = ScreenToNormalizedTopLeft(center);
            UpdateLocalRegion(
                VisualToolRegion.ScreenNormalized(
                    normalizedCenter.x - nextWidth * 0.5f,
                    normalizedCenter.y - nextHeight * 0.5f,
                    nextWidth,
                    nextHeight),
                VisualToolPhases.ResizeUpdate);
            LastRenderStatus = "bbox_local_pinch_resize";
            return true;
        }

        private BBoxInteractionMode HitTestInteraction(Vector2 screenPosition)
        {
            var r = CurrentRegion.Clamped();
            float width = Mathf.Max(1f, Screen.width);
            float height = Mathf.Max(1f, Screen.height);
            float left = r.x * width;
            float right = (r.x + r.width) * width;
            float top = (1f - r.y) * height;
            float bottom = (1f - r.y - r.height) * height;
            float edge = Mathf.Max(10f, edgeHandlePixels);
            bool nearLeft = Mathf.Abs(screenPosition.x - left) <= edge;
            bool nearRight = Mathf.Abs(screenPosition.x - right) <= edge;
            bool nearTop = Mathf.Abs(screenPosition.y - top) <= edge;
            bool nearBottom = Mathf.Abs(screenPosition.y - bottom) <= edge;

            if (nearLeft && nearTop) return BBoxInteractionMode.ResizeTopLeft;
            if (nearRight && nearTop) return BBoxInteractionMode.ResizeTopRight;
            if (nearLeft && nearBottom) return BBoxInteractionMode.ResizeBottomLeft;
            if (nearRight && nearBottom) return BBoxInteractionMode.ResizeBottomRight;
            if (nearLeft) return BBoxInteractionMode.ResizeLeft;
            if (nearRight) return BBoxInteractionMode.ResizeRight;
            if (nearTop) return BBoxInteractionMode.ResizeTop;
            if (nearBottom) return BBoxInteractionMode.ResizeBottom;
            return BBoxInteractionMode.Move;
        }

        private VisualToolRegion ApplyInteractionDelta(
            VisualToolRegion region,
            Vector2 delta,
            BBoxInteractionMode mode)
        {
            var r = region.Clamped();
            float left = r.x;
            float top = r.y;
            float right = r.x + r.width;
            float bottom = r.y + r.height;
            float minWidth = Mathf.Clamp(minBoxWidth, 0.02f, 0.95f);
            float minHeight = Mathf.Clamp(minBoxHeight, 0.02f, 0.95f);

            if (mode == BBoxInteractionMode.Move)
            {
                return VisualToolRegion.ScreenNormalized(left + delta.x, top + delta.y, r.width, r.height);
            }

            if (ResizesLeft(mode))
                left = Mathf.Clamp(left + delta.x, 0f, right - minWidth);
            if (ResizesRight(mode))
                right = Mathf.Clamp(right + delta.x, left + minWidth, 1f);
            if (ResizesTop(mode))
                top = Mathf.Clamp(top + delta.y, 0f, bottom - minHeight);
            if (ResizesBottom(mode))
                bottom = Mathf.Clamp(bottom + delta.y, top + minHeight, 1f);

            return VisualToolRegion.ScreenNormalized(left, top, right - left, bottom - top);
        }

        private string ToggleSemanticLock()
        {
            return IsLocked ? Unlock() : Lock();
        }

        public string SetSampleLabel(string value)
        {
            sampleLabel = NormalizeSampleLabel(value);
            LastRenderStatus = "bbox_sample_label_" + sampleLabel;
            UpdateOverlay();
            return SetStatus(LastRenderStatus, true);
        }

        public string CycleSampleLabel()
        {
            string[] options = EffectiveSampleLabels();
            int index = 0;
            string current = CurrentSampleLabel;
            for (int i = 0; i < options.Length; i++)
            {
                if (string.Equals(NormalizeSampleLabel(options[i]), current, StringComparison.OrdinalIgnoreCase))
                {
                    index = i;
                    break;
                }
            }
            int next = (index + 1) % Mathf.Max(1, options.Length);
            return SetSampleLabel(options[next]);
        }

        public string SetSampleColorIndex(int value)
        {
            sampleColorIndex = Mathf.Abs(value) % SampleColors.Length;
            LastRenderStatus = "bbox_sample_color_" + CurrentSampleColorKey;
            UpdateOverlay();
            return SetStatus(LastRenderStatus, true);
        }

        public string CycleSampleColor()
        {
            return SetSampleColorIndex(NormalizedSampleColorIndex() + 1);
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

        private void EndLocalPointerGesture()
        {
            _pointerActive = false;
            _pinchActive = false;
            _pinchStartDistance = 0f;
            _interactionMode = BBoxInteractionMode.None;
        }

        private static bool ResizesLeft(BBoxInteractionMode mode)
        {
            return mode == BBoxInteractionMode.ResizeLeft
                   || mode == BBoxInteractionMode.ResizeTopLeft
                   || mode == BBoxInteractionMode.ResizeBottomLeft;
        }

        private static bool ResizesRight(BBoxInteractionMode mode)
        {
            return mode == BBoxInteractionMode.ResizeRight
                   || mode == BBoxInteractionMode.ResizeTopRight
                   || mode == BBoxInteractionMode.ResizeBottomRight;
        }

        private static bool ResizesTop(BBoxInteractionMode mode)
        {
            return mode == BBoxInteractionMode.ResizeTop
                   || mode == BBoxInteractionMode.ResizeTopLeft
                   || mode == BBoxInteractionMode.ResizeTopRight;
        }

        private static bool ResizesBottom(BBoxInteractionMode mode)
        {
            return mode == BBoxInteractionMode.ResizeBottom
                   || mode == BBoxInteractionMode.ResizeBottomLeft
                   || mode == BBoxInteractionMode.ResizeBottomRight;
        }

        private static Image CreateEdge(
            string name,
            Transform parent,
            Vector2 anchorMin,
            Vector2 anchorMax,
            Vector2 pivot,
            Vector2 position,
            Vector2 size)
        {
            var rect = CreateArea("BBoxEdge" + name, parent, anchorMin, anchorMax, pivot, position, size);
            var image = rect.gameObject.AddComponent<Image>();
            image.color = new Color(0.50f, 0.88f, 0.42f, 0.82f);
            image.raycastTarget = false;
            return image;
        }

        private static Image CreateHandle(string name, Transform parent, Vector2 anchor, Vector2 position)
        {
            var rect = CreateArea(
                "BBoxSelectedHandle" + name,
                parent,
                anchor,
                anchor,
                new Vector2(0.5f, 0.5f),
                position,
                new Vector2(22f, 22f));
            var image = rect.gameObject.AddComponent<Image>();
            image.color = new Color(1f, 1f, 1f, 0.98f);
            image.raycastTarget = false;
            rect.gameObject.SetActive(false);
            return image;
        }

        private void CreateSemanticSampleLabel(Transform parent)
        {
            _semanticLabelRoot = CreateArea(
                "BBoxSemanticSampleLabel",
                parent,
                new Vector2(0f, 1f),
                new Vector2(0f, 1f),
                new Vector2(0f, 0f),
                new Vector2(0f, 0f),
                new Vector2(132f, 28f));

            _semanticLabelBackground = _semanticLabelRoot.gameObject.AddComponent<Image>();
            _semanticLabelBackground.color = CurrentSampleColor;
            _semanticLabelBackground.raycastTarget = false;

            var textRect = CreateArea(
                "BBoxSemanticSampleLabelText",
                _semanticLabelRoot,
                Vector2.zero,
                Vector2.one,
                new Vector2(0.5f, 0.5f),
                Vector2.zero,
                Vector2.zero);
            _semanticLabelText = textRect.gameObject.AddComponent<Text>();
            _semanticLabelText.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            _semanticLabelText.fontSize = 13;
            _semanticLabelText.alignment = TextAnchor.MiddleCenter;
            _semanticLabelText.horizontalOverflow = HorizontalWrapMode.Wrap;
            _semanticLabelText.verticalOverflow = VerticalWrapMode.Truncate;
            _semanticLabelText.text = ShortLabel(CurrentSampleLabel.ToUpperInvariant(), "OBJECT", 12);
            _semanticLabelText.color = Color.white;
            _semanticLabelText.raycastTarget = false;
        }

        private void CreateSampleAttributeStrip(Transform parent)
        {
            _sampleChipRoot = CreateArea(
                "BBoxSampleAttributeStrip",
                parent,
                new Vector2(0f, 1f),
                new Vector2(0f, 1f),
                new Vector2(0f, 0f),
                new Vector2(0f, 20f),
                new Vector2(186f, 34f));

            var bg = _sampleChipRoot.gameObject.AddComponent<Image>();
            bg.color = new Color(0.03f, 0.03f, 0.025f, 0.78f);
            bg.raycastTarget = false;

            _sampleColorSwatch = CreateSampleColorButton(_sampleChipRoot);
            _sampleLabelText = CreateSampleLabelButton(_sampleChipRoot);
            _sampleChipRoot.gameObject.SetActive(false);
        }

        private Image CreateSampleColorButton(Transform parent)
        {
            var rect = CreateArea(
                "BBoxSampleColorButton",
                parent,
                new Vector2(0f, 0.5f),
                new Vector2(0f, 0.5f),
                new Vector2(0f, 0.5f),
                new Vector2(8f, 0f),
                new Vector2(30f, 24f));
            var image = rect.gameObject.AddComponent<Image>();
            image.color = CurrentSampleColor;
            image.raycastTarget = true;
            var button = rect.gameObject.AddComponent<Button>();
            button.onClick.AddListener(() => CycleSampleColor());
            return image;
        }

        private Text CreateSampleLabelButton(Transform parent)
        {
            var rect = CreateArea(
                "BBoxSampleLabelButton",
                parent,
                new Vector2(0f, 0.5f),
                new Vector2(0f, 0.5f),
                new Vector2(0f, 0.5f),
                new Vector2(46f, 0f),
                new Vector2(132f, 24f));
            var image = rect.gameObject.AddComponent<Image>();
            image.color = new Color(0.08f, 0.10f, 0.09f, 0.92f);
            image.raycastTarget = true;
            var button = rect.gameObject.AddComponent<Button>();
            button.onClick.AddListener(() => CycleSampleLabel());

            var textRect = CreateArea(
                "BBoxSampleLabelText",
                rect,
                Vector2.zero,
                Vector2.one,
                new Vector2(0.5f, 0.5f),
                Vector2.zero,
                Vector2.zero);
            var text = textRect.gameObject.AddComponent<Text>();
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            text.fontSize = 13;
            text.alignment = TextAnchor.MiddleCenter;
            text.horizontalOverflow = HorizontalWrapMode.Wrap;
            text.verticalOverflow = VerticalWrapMode.Truncate;
            text.text = ShortLabel(CurrentSampleLabel.ToUpperInvariant(), "OBJECT", 12);
            text.color = new Color(0.96f, 0.98f, 0.92f, 0.96f);
            text.raycastTarget = false;
            return text;
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
                "BBoxVisualToolConfirmFlash",
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
                "BBoxVisualToolConfirmFeedbackBadge",
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
            if (_selectionEdges != null)
            {
                foreach (var image in _selectionEdges)
                {
                    if (image != null)
                        image.gameObject.SetActive(selectedVisible);
                }
            }
            if (_cornerHandles != null)
            {
                foreach (var image in _cornerHandles)
                {
                    if (image != null)
                        image.gameObject.SetActive(selectedVisible);
                }
            }
            if (_confirmShutterRoot != null)
                _confirmShutterRoot.gameObject.SetActive(visible && showConfirmShutter && FeatureEnabled && IsOpen);
            if (_statusText != null)
                _statusText.gameObject.SetActive(visible);
            if (_sampleChipRoot != null)
                _sampleChipRoot.gameObject.SetActive(visible && IsSelected && IsOpen);
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
            float width = 58f;
            float gap = 8f;
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
            image.color = new Color(0.08f, 0.12f, 0.08f, 0.86f);
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
            text.color = new Color(0.82f, 0.98f, 0.72f, 0.95f);
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
            string text = string.IsNullOrWhiteSpace(primary) ? (fallback ?? "") : primary;
            text = text.Trim();
            if (text.Length <= max) return text;
            return text.Substring(0, Mathf.Max(1, max - 3)) + "...";
        }

        private string[] EffectiveSampleLabels()
        {
            if (sampleLabelOptions == null || sampleLabelOptions.Length == 0)
                return FallbackSampleLabels;

            int usable = 0;
            for (int i = 0; i < sampleLabelOptions.Length; i++)
            {
                if (!string.IsNullOrWhiteSpace(sampleLabelOptions[i]))
                    usable++;
            }
            if (usable == 0)
                return FallbackSampleLabels;

            var result = new string[usable];
            int write = 0;
            for (int i = 0; i < sampleLabelOptions.Length; i++)
            {
                if (!string.IsNullOrWhiteSpace(sampleLabelOptions[i]))
                    result[write++] = NormalizeSampleLabel(sampleLabelOptions[i]);
            }
            return result;
        }

        private int NormalizedSampleColorIndex()
        {
            if (SampleColors.Length == 0)
                return 0;
            int index = sampleColorIndex % SampleColors.Length;
            return index < 0 ? index + SampleColors.Length : index;
        }

        private static string NormalizeSampleLabel(string value)
        {
            string text = string.IsNullOrWhiteSpace(value) ? "object" : value.Trim().ToLowerInvariant();
            char[] chars = text.ToCharArray();
            for (int i = 0; i < chars.Length; i++)
            {
                char c = chars[i];
                bool allowed = (c >= 'a' && c <= 'z')
                               || (c >= '0' && c <= '9')
                               || c == '_'
                               || c == '-';
                if (!allowed)
                    chars[i] = '_';
            }
            text = new string(chars).Trim('_', '-');
            if (string.IsNullOrWhiteSpace(text))
                return "object";
            return text.Length <= 32 ? text : text.Substring(0, 32);
        }
    }
}
