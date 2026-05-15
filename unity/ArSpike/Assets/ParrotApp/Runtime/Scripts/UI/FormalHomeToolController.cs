using System;
using ParrotApp.Backend;
using ParrotApp.Lifecycle;
using ParrotApp.LiveKit;
using ParrotApp.Photo;
using UnityEngine;
using UnityEngine.UI;

namespace ParrotApp.UI
{
    /// <summary>
    /// Formal homepage owner for the first real toolbar camera action.
    ///
    /// This controller deliberately does not issue Brain RPCs and does not send
    /// image bytes through LiveKit. CAM delegates to PhotoController, which owns
    /// the split path: compact photo.taken_preview ECP metadata plus HTTP upload
    /// of the full image asset. MAG/BOX are intentionally deferred until the
    /// phone stability pass and the refreshed SVA/ECP visual-evidence contract.
    /// </summary>
    [DisallowMultipleComponent]
    public class FormalHomeToolController : MonoBehaviour
    {
        [SerializeField] private RoomManager roomManager;
        [SerializeField] private FormalMainReadyGate mainReadyGate;
        [SerializeField] private PhotoController photoController;

        [Header("Mobile Runtime")]
        [SerializeField] private bool requireNonLoopbackPhotoUploadOnDevice = true;

        private Canvas _canvas;
        private Text _statusText;

        public bool MagnifierOpen => false;
        public bool BBoxOpen => false;
        public string ActiveFocusId => "";
        public string ActiveBBoxId => "";
        public string LastToolStatus { get; private set; } = "tools_idle";

        private void Awake()
        {
            ResolveServices();
        }

        private void Start()
        {
            ResolveServices();
            ConfigurePhotoUploadEndpoint();
            EnsureUi();
            SetVisible(false);
        }

        public string CapturePhoto()
        {
            ResolveServices();
            ConfigurePhotoUploadEndpoint();
            EnsureUi();

            if (!CanSendToolEvents())
                return SetStatus("photo_waits_main_ready_or_brain", false);
            if (photoController == null)
                return SetStatus("photo_controller_missing", false);
            if (RequiresPhoneSafeUploadEndpoint() && photoController.IsUploadEndpointLoopback)
                return SetStatus("photo_upload_endpoint_not_phone_safe", false);

            SetVisible(true);
            photoController.CapturePhoto();
            return SetStatus("photo_capture_requested", true);
        }

        public string ToggleMagnifier()
        {
            return SetStatus("magnifier_deferred_phone_stability", false);
        }

        public string ToggleBBox()
        {
            return SetStatus("bbox_deferred_phone_stability", false);
        }

        public string CloseMagnifier()
        {
            return SetStatus("magnifier_deferred_phone_stability", false);
        }

        public string CloseBBox()
        {
            return SetStatus("bbox_deferred_phone_stability", false);
        }

        public void CloseAllTools()
        {
            SetVisible(false);
            LastToolStatus = "tools_idle";
        }

        private void ResolveServices()
        {
            if (roomManager == null) roomManager = RoomManager.Instance ?? FindObjectOfType<RoomManager>();
            if (mainReadyGate == null) mainReadyGate = FindObjectOfType<FormalMainReadyGate>();
            if (photoController == null) photoController = PhotoController.Instance ?? FindObjectOfType<PhotoController>();
            if (photoController == null) photoController = gameObject.AddComponent<PhotoController>();
        }

        private void ConfigurePhotoUploadEndpoint()
        {
            if (photoController == null) return;
            var config = ParrotRuntimeConfig.Load();
            if (!string.IsNullOrWhiteSpace(config.photoUploadUrl)
                && photoController.TryConfigureUploadEndpoint(config.photoUploadUrl))
                return;

            if (!string.IsNullOrWhiteSpace(config.photoUploadHost) && config.photoUploadPort > 0)
                photoController.ConfigureUploadEndpoint(config.photoUploadHost, config.photoUploadPort);
        }

        private bool CanSendToolEvents()
        {
            return mainReadyGate != null
                   && mainReadyGate.IsReady
                   && roomManager != null
                   && roomManager.IsConnected;
        }

        private bool RequiresPhoneSafeUploadEndpoint()
        {
            return requireNonLoopbackPhotoUploadOnDevice && !Application.isEditor;
        }

        private string SetStatus(string status, bool ok)
        {
            LastToolStatus = string.IsNullOrWhiteSpace(status) ? "tools_idle" : status;
            if (_statusText != null)
            {
                _statusText.text = LastToolStatus;
                _statusText.color = ok
                    ? new Color(0.70f, 0.95f, 0.62f, 0.95f)
                    : new Color(0.96f, 0.44f, 0.32f, 0.95f);
            }
            return LastToolStatus;
        }

        private void SetVisible(bool visible)
        {
            if (_canvas != null) _canvas.gameObject.SetActive(visible);
        }

        private void EnsureUi()
        {
            if (_canvas != null) return;

            var root = new GameObject("FormalHomeToolCanvas");
            root.transform.SetParent(transform, false);
            _canvas = root.AddComponent<Canvas>();
            _canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            _canvas.sortingOrder = 74;

            var scaler = root.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(2800f, 1260f);
            scaler.matchWidthOrHeight = 0.5f;
            root.AddComponent<GraphicRaycaster>();

            var status = CreateArea(
                "FormalHomeToolStatus",
                root.transform,
                new Vector2(0f, 0f),
                new Vector2(0f, 0f),
                new Vector2(0f, 0f),
                new Vector2(28f, 24f),
                new Vector2(520f, 42f));
            _statusText = status.gameObject.AddComponent<Text>();
            _statusText.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            _statusText.fontSize = 16;
            _statusText.alignment = TextAnchor.MiddleLeft;
            _statusText.horizontalOverflow = HorizontalWrapMode.Wrap;
            _statusText.verticalOverflow = VerticalWrapMode.Truncate;
            _statusText.text = LastToolStatus;
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
            image.raycastTarget = true;
            return rect;
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

        private static void CreateText(string name, Transform parent, string textValue, int fontSize)
        {
            var rect = CreateArea(
                name,
                parent,
                Vector2.zero,
                Vector2.one,
                new Vector2(0.5f, 0.5f),
                Vector2.zero,
                new Vector2(-18f, -18f));
            var text = rect.gameObject.AddComponent<Text>();
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            text.fontSize = fontSize;
            text.alignment = TextAnchor.MiddleCenter;
            text.horizontalOverflow = HorizontalWrapMode.Wrap;
            text.verticalOverflow = VerticalWrapMode.Truncate;
            text.color = new Color(0.96f, 0.92f, 0.78f, 0.95f);
            text.text = textValue;
        }

    }
}
