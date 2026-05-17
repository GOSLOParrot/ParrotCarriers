using System;
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
        [SerializeField] private bool showDevActionButtons = true;

        private Canvas _canvas;
        private RectTransform _lensRoot;
        private Text _statusText;
        private Text _lockButtonText;
        private Image _lensFill;
        private Image _rim;
        private bool _pointerActive;
        private float _lastLocalMotionAt = -999f;
        private float _lastDwellTickAt = -999f;

        protected override string ToolKind => VisualToolKinds.Mag;
        protected override string ToolLabel => "MAG";
        protected override string SourceSurface => "formal_home.mag";
        protected override VisualToolRegion DefaultRegion => VisualToolRegion.ScreenNormalized(0.42f, 0.34f, 0.22f, 0.22f);
        protected override string PreviewDeliveryPreference => VisualToolDeliveryPreferences.IntentOnly;
        protected override string ConfirmDeliveryPreference => VisualToolDeliveryPreferences.IntentOnly;
        protected override string ExplicitSendDeliveryPreference => VisualToolDeliveryPreferences.C3;
        protected override float ConfirmAttentionHint => 0.35f;

        public override string BeginPreview()
        {
            _lastLocalMotionAt = Time.unscaledTime;
            _lastDwellTickAt = -999f;
            return base.BeginPreview();
        }

        private void Update()
        {
            if (!FeatureEnabled || !IsOpen)
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
                   + "\"local_render\":\"mag_overlay\","
                   + "\"phase\":" + VisualToolPacketBuilder.QuoteJson(phase) + ","
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

            var r = CurrentRegion.Clamped();
            _lensRoot.anchorMin = new Vector2(r.x, 1f - r.y - r.height);
            _lensRoot.anchorMax = new Vector2(r.x + r.width, 1f - r.y);
            _lensRoot.offsetMin = Vector2.zero;
            _lensRoot.offsetMax = Vector2.zero;

            if (_lensFill != null)
                _lensFill.color = IsLocked
                    ? new Color(0.95f, 0.78f, 0.30f, 0.22f)
                    : new Color(0.92f, 0.82f, 0.44f, 0.15f);
            if (_rim != null)
                _rim.color = IsLocked
                    ? new Color(0.98f, 0.86f, 0.42f, 0.98f)
                    : new Color(0.85f, 0.75f, 0.42f, 0.86f);

            if (_statusText != null)
            {
                _statusText.text = "MAG x" + zoom.ToString("0.0")
                                   + " " + ShortLabel(LastRenderStatus, "render", 18)
                                   + "\nHTTP " + ShortLabel(LastHttpStatus, "idle", 30)
                                   + "\nASSET " + ShortLabel(LastAssetStatus, "idle", 28)
                                   + "\n" + (_pointerActive ? "DRAG" : (IsLocked ? "LOCK" : "LOCAL"));
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

            var scaler = root.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(2800f, 1260f);
            scaler.matchWidthOrHeight = 0.5f;

            _lensRoot = CreateArea(
                "MagnifierVisualToolLocalLens",
                root.transform,
                Vector2.zero,
                Vector2.zero,
                new Vector2(0.5f, 0.5f),
                Vector2.zero,
                Vector2.zero);

            _lensFill = _lensRoot.gameObject.AddComponent<Image>();
            _lensFill.color = new Color(0.92f, 0.82f, 0.44f, 0.15f);
            _lensFill.raycastTarget = false;

            var rimRect = CreateArea(
                "MagnifierVisualToolRim",
                _lensRoot,
                Vector2.zero,
                Vector2.one,
                new Vector2(0.5f, 0.5f),
                Vector2.zero,
                Vector2.zero);
            _rim = rimRect.gameObject.AddComponent<Image>();
            _rim.color = new Color(0.85f, 0.75f, 0.42f, 0.86f);
            _rim.raycastTarget = false;

            var crossH = CreateArea(
                "MagnifierVisualToolCrossH",
                _lensRoot,
                new Vector2(0f, 0.5f),
                new Vector2(1f, 0.5f),
                new Vector2(0.5f, 0.5f),
                Vector2.zero,
                new Vector2(0f, 2f));
            var crossHImage = crossH.gameObject.AddComponent<Image>();
            crossHImage.color = new Color(0.95f, 0.90f, 0.62f, 0.58f);
            crossHImage.raycastTarget = false;

            var crossV = CreateArea(
                "MagnifierVisualToolCrossV",
                _lensRoot,
                new Vector2(0.5f, 0f),
                new Vector2(0.5f, 1f),
                new Vector2(0.5f, 0.5f),
                Vector2.zero,
                new Vector2(2f, 0f));
            var crossVImage = crossV.gameObject.AddComponent<Image>();
            crossVImage.color = new Color(0.95f, 0.90f, 0.62f, 0.58f);
            crossVImage.raycastTarget = false;

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
                _lockButtonText = CreateActionButton("MagnifierDevLockButton", _lensRoot, 0, 8, "LOCK", ToggleSemanticLock);
                CreateActionButton("MagnifierDevConfirmButton", _lensRoot, 1, 8, "OK", Confirm);
                CreateActionButton("MagnifierDevAssetConfirmButton", _lensRoot, 2, 8, "IMG", ConfirmWithScreenRegionAsset);
                CreateActionButton("MagnifierDevExplicitSendButton", _lensRoot, 3, 8, "C3", ExplicitSendWithScreenRegionAsset);
                CreateActionButton("MagnifierDevZoomOutButton", _lensRoot, 4, 8, "-", () => AdjustZoom(-zoomStep));
                CreateActionButton("MagnifierDevZoomInButton", _lensRoot, 5, 8, "+", () => AdjustZoom(zoomStep));
                CreateActionButton("MagnifierDevCancelButton", _lensRoot, 6, 8, "X", Cancel);
                CreateActionButton("MagnifierDevReleaseButton", _lensRoot, 7, 8, "REL", Release);
            }
        }

        protected override void SetOverlayVisibleForScreenRegionAsset(bool visible)
        {
            if (_canvas != null)
                _canvas.gameObject.SetActive(visible && FeatureEnabled && IsOpen);
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

        private static string ShortLabel(string primary, string fallback, int max)
        {
            string text = string.IsNullOrWhiteSpace(primary) ? (fallback ?? "") : primary;
            text = text.Trim();
            if (text.Length <= max) return text;
            return text.Substring(0, Mathf.Max(1, max - 3)) + "...";
        }
    }
}
