using System;
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
        [SerializeField] private bool showDevActionButtons = true;

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
        private Image _fill;
        private Image[] _edges;
        private BBoxInteractionMode _interactionMode = BBoxInteractionMode.None;
        private bool _pointerActive;

        protected override string ToolKind => VisualToolKinds.BBox;
        protected override string ToolLabel => "BBox";
        protected override string SourceSurface => "formal_home.bbox";
        protected override VisualToolRegion DefaultRegion => VisualToolRegion.ScreenNormalized(0.30f, 0.26f, 0.40f, 0.30f);
        protected override string ConfirmDeliveryPreference => VisualToolDeliveryPreferences.Default;
        protected override float ConfirmAttentionHint => 1.0f;

        private void Update()
        {
            if (!FeatureEnabled || !IsOpen || !enableLocalPointerInput)
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

            var r = CurrentRegion.Clamped();
            _boxRoot.anchorMin = new Vector2(r.x, 1f - r.y - r.height);
            _boxRoot.anchorMax = new Vector2(r.x + r.width, 1f - r.y);
            _boxRoot.offsetMin = Vector2.zero;
            _boxRoot.offsetMax = Vector2.zero;

            Color edge = IsLocked
                ? new Color(0.72f, 0.98f, 0.46f, 0.96f)
                : new Color(0.50f, 0.88f, 0.42f, 0.82f);
            if (_fill != null)
                _fill.color = IsLocked
                    ? new Color(0.18f, 0.36f, 0.12f, 0.18f)
                    : new Color(0.16f, 0.28f, 0.10f, 0.12f);
            if (_edges != null)
            {
                foreach (var image in _edges)
                {
                    if (image != null) image.color = edge;
                }
            }

            if (_statusText != null)
            {
                _statusText.text = "BOX " + ShortLabel(LastRenderStatus, "render", 24)
                                   + "\nHTTP " + ShortLabel(LastHttpStatus, "idle", 32)
                                   + "\nASSET " + ShortLabel(LastAssetStatus, "idle", 30)
                                   + "\n" + (_interactionMode == BBoxInteractionMode.None
                                       ? (IsLocked ? "LOCK" : "LOCAL")
                                       : _interactionMode.ToString());
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

            var scaler = root.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(2800f, 1260f);
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
            _edges[0] = CreateEdge("Top", _boxRoot, new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(0.5f, 1f), new Vector2(0f, -2f), new Vector2(0f, 4f));
            _edges[1] = CreateEdge("Bottom", _boxRoot, new Vector2(0f, 0f), new Vector2(1f, 0f), new Vector2(0.5f, 0f), new Vector2(0f, 2f), new Vector2(0f, 4f));
            _edges[2] = CreateEdge("Left", _boxRoot, new Vector2(0f, 0f), new Vector2(0f, 1f), new Vector2(0f, 0.5f), new Vector2(2f, 0f), new Vector2(4f, 0f));
            _edges[3] = CreateEdge("Right", _boxRoot, new Vector2(1f, 0f), new Vector2(1f, 1f), new Vector2(1f, 0.5f), new Vector2(-2f, 0f), new Vector2(4f, 0f));

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
                _lockButtonText = CreateActionButton("BBoxDevLockButton", _boxRoot, 0, 6, "LOCK", ToggleSemanticLock);
                CreateActionButton("BBoxDevConfirmButton", _boxRoot, 1, 6, "OK", Confirm);
                CreateActionButton("BBoxDevAssetConfirmButton", _boxRoot, 2, 6, "IMG", ConfirmWithScreenRegionAsset);
                CreateActionButton("BBoxDevExplicitSendButton", _boxRoot, 3, 6, "C3", ExplicitSendWithScreenRegionAsset);
                CreateActionButton("BBoxDevCancelButton", _boxRoot, 4, 6, "X", Cancel);
                CreateActionButton("BBoxDevReleaseButton", _boxRoot, 5, 6, "REL", Release);
            }
        }

        protected override void SetOverlayVisibleForScreenRegionAsset(bool visible)
        {
            if (_canvas != null)
                _canvas.gameObject.SetActive(visible && FeatureEnabled && IsOpen);
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

        protected override void OnToolClosed(string phase)
        {
            EndLocalPointerGesture();
        }

        private void HandlePointerInput()
        {
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

        private void EndLocalPointerGesture()
        {
            _pointerActive = false;
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
    }
}
