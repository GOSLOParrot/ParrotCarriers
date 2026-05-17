using System;
using System.Collections;
using ParrotApp.Backend;
using UnityEngine;
using UnityEngine.EventSystems;

namespace ParrotApp.VisualTools
{
    public abstract class VisualToolControllerBase : MonoBehaviour
    {
        [Header("Feature / Dev Gate")]
        [SerializeField] protected bool enableDevFlagOverride = false;
        [SerializeField] protected bool useRuntimeConfigFlag = true;
        [SerializeField] protected bool sendHttpLifecycleEvents = true;
        [SerializeField] protected bool allowLowFrequencyUpdateEvents = false;
        [SerializeField] protected float lowFrequencyUpdateIntervalSeconds = 0.5f;
        [SerializeField] protected bool enableScreenRegionAssetCapture = true;
        [SerializeField] protected bool hideOverlayDuringAssetCapture = true;
        [SerializeField] protected bool sendLifecycleIfAssetCaptureFails = true;
        [SerializeField] protected bool sendLifecycleIfAssetUploadFails = true;
        [SerializeField] protected int minScreenRegionAssetPixels = 8;
        [SerializeField] protected bool showDevHud = true;
        [SerializeField] protected VisualToolHttpClient httpClient;

        private bool _runtimeFlagsLoaded;
        private bool _runtimeDevEnabled;
        private bool _runtimeHttpEnabled = true;
        private float _lastUpdateEventSentAt = -999f;
        private Vector2 _lastMousePosition;
        private bool _hasLastMousePosition;

        public bool IsOpen { get; protected set; }
        public bool IsLocked { get; protected set; }
        public bool IsSelected { get; protected set; }
        public string ToolId { get; protected set; } = "";
        public VisualToolRegion CurrentRegion { get; protected set; }
        public string LastStatus { get; protected set; } = "visual_tool_idle";
        public string LastHttpStatus { get; protected set; } = "visual_tool_http_idle";
        public string LastAssetStatus { get; protected set; } = "visual_tool_asset_idle";
        public string LastRenderStatus { get; protected set; } = "visual_tool_render_idle";
        public string LastReceiptJson { get; protected set; } = "";

        public bool FeatureEnabled
        {
            get
            {
                EnsureRuntimeFlags();
                return enableDevFlagOverride || (useRuntimeConfigFlag && _runtimeDevEnabled);
            }
        }

        protected bool RuntimeHttpEnabled
        {
            get
            {
                EnsureRuntimeFlags();
                return _runtimeHttpEnabled;
            }
        }

        protected abstract string ToolKind { get; }
        protected abstract string ToolLabel { get; }
        protected abstract string SourceSurface { get; }
        protected abstract VisualToolRegion DefaultRegion { get; }
        protected virtual string PreviewDeliveryPreference => VisualToolDeliveryPreferences.Default;
        protected virtual string ConfirmDeliveryPreference => VisualToolDeliveryPreferences.Default;
        protected virtual string ExplicitSendDeliveryPreference => VisualToolDeliveryPreferences.C3;
        protected virtual float ConfirmAttentionHint => 0f;

        protected virtual void Awake()
        {
            ResolveClient();
            CurrentRegion = DefaultRegion;
        }

        protected virtual void Start()
        {
            ResolveClient();
            EnsureRuntimeFlags();
            UpdateOverlay();
        }

        public virtual string ToggleTool()
        {
            if (!FeatureEnabled)
                return SetStatus(ToolKind + "_dev_flag_off_app024_required", false);
            return IsOpen ? Release() : BeginPreview();
        }

        public virtual string BeginPreview()
        {
            if (!FeatureEnabled)
                return SetStatus(ToolKind + "_dev_flag_off_app024_required", false);

            if (string.IsNullOrWhiteSpace(ToolId))
                ToolId = VisualToolPacketBuilder.GenerateToolId(ToolKind);
            CurrentRegion = CurrentRegion.width > 0f && CurrentRegion.height > 0f
                ? CurrentRegion.Clamped()
                : DefaultRegion;
            IsOpen = true;
            IsSelected = true;
            IsLocked = false;
            LastRenderStatus = ToolKind + "_local_overlay_ready";
            UpdateOverlay();
            return EmitPhase(VisualToolPhases.PreviewStart, PreviewDeliveryPreference);
        }

        public virtual string UpdateLocalRegion(VisualToolRegion region, string updatePhase = VisualToolPhases.DragUpdate)
        {
            if (!FeatureEnabled)
                return SetStatus(ToolKind + "_dev_flag_off_app024_required", false);

            CurrentRegion = region.Clamped();
            if (!IsOpen)
                IsOpen = true;
            LastRenderStatus = ToolKind + "_local_region_updated";
            UpdateOverlay();

            if (allowLowFrequencyUpdateEvents && ShouldSendLowFrequencyUpdate())
                return EmitPhase(updatePhase, PreviewDeliveryPreference);

            return SetStatus(ToolKind + "_local_" + updatePhase, true);
        }

        public virtual string Lock()
        {
            if (!EnsureOpenForStablePhase()) return LastStatus;
            IsLocked = true;
            UpdateOverlay();
            return EmitPhase(VisualToolPhases.Lock, PreviewDeliveryPreference);
        }

        public virtual string Unlock()
        {
            if (!EnsureOpenForStablePhase()) return LastStatus;
            IsLocked = false;
            UpdateOverlay();
            return EmitPhase(VisualToolPhases.Unlock, VisualToolDeliveryPreferences.Silent);
        }

        public virtual string DwellTick()
        {
            if (!EnsureOpenForStablePhase()) return LastStatus;
            return EmitPhase(VisualToolPhases.DwellTick, PreviewDeliveryPreference);
        }

        public virtual string Confirm()
        {
            if (!EnsureOpenForStablePhase()) return LastStatus;
            IsLocked = true;
            UpdateOverlay();
            return EmitPhase(VisualToolPhases.Confirm, ConfirmDeliveryPreference, attentionHint: ConfirmAttentionHint);
        }

        public virtual string ExplicitSend()
        {
            if (!EnsureOpenForStablePhase()) return LastStatus;
            IsLocked = true;
            UpdateOverlay();
            return EmitPhase(VisualToolPhases.ExplicitSend, ExplicitSendDeliveryPreference, attentionHint: ConfirmAttentionHint);
        }

        public virtual string ConfirmWithRenderedAsset(byte[] imageBytes, string mimeType = "image/png")
        {
            if (!EnsureOpenForStablePhase()) return LastStatus;
            ApplyStablePhaseLocalState(VisualToolPhases.Confirm);
            if (!RuntimeHttpEnabled || !sendHttpLifecycleEvents)
                return Confirm();
            ResolveClient();
            if (httpClient == null || !httpClient.HasEndpoint)
                return SetStatus(ToolKind + "_asset_http_endpoint_missing", false);

            var packet = BuildPacket(VisualToolPhases.Confirm, ConfirmDeliveryPreference, ConfirmAttentionHint);
            StartCoroutine(UploadAssetThenLifecycle(packet, imageBytes, mimeType));
            return SetStatus(ToolKind + "_asset_confirm_queued", true);
        }

        public virtual string ConfirmWithScreenRegionAsset()
        {
            return QueueScreenRegionAssetLifecycle(
                VisualToolPhases.Confirm,
                ConfirmDeliveryPreference,
                ConfirmAttentionHint);
        }

        public virtual string ExplicitSendWithScreenRegionAsset()
        {
            return QueueScreenRegionAssetLifecycle(
                VisualToolPhases.ExplicitSend,
                ExplicitSendDeliveryPreference,
                ConfirmAttentionHint);
        }

        public virtual string Cancel()
        {
            if (!IsOpen && string.IsNullOrWhiteSpace(ToolId))
                return SetStatus(ToolKind + "_already_idle", true);

            IsOpen = false;
            IsLocked = false;
            IsSelected = false;
            UpdateOverlay();
            string result = EmitPhase(VisualToolPhases.Cancel, VisualToolDeliveryPreferences.Silent);
            ToolId = "";
            return result;
        }

        public virtual string Release()
        {
            if (!IsOpen && string.IsNullOrWhiteSpace(ToolId))
                return SetStatus(ToolKind + "_already_idle", true);

            IsOpen = false;
            IsLocked = false;
            IsSelected = false;
            UpdateOverlay();
            string result = EmitPhase(VisualToolPhases.Release, VisualToolDeliveryPreferences.Silent);
            ToolId = "";
            return result;
        }

        protected VisualToolLifecyclePacket BuildPacket(
            string phase,
            string deliveryPreference,
            float attentionHint = 0f)
        {
            string id = string.IsNullOrWhiteSpace(ToolId)
                ? VisualToolPacketBuilder.GenerateToolId(ToolKind)
                : ToolId;
            ToolId = id;
            var packet = VisualToolPacketBuilder.CreateLifecycle(
                id,
                ToolKind,
                phase,
                CurrentRegion,
                SourceSurface,
                deliveryPreference);
            packet.attention_hint = attentionHint;
            packet.label = ToolLabel;
            packet.meta_json = BuildMetaJson(phase);
            return packet;
        }

        protected virtual string BuildMetaJson(string phase)
        {
            return "{"
                   + "\"client\":\"unity_formal_app\","
                   + "\"feature_flag\":\"dev\","
                   + "\"local_render\":" + VisualToolPacketBuilder.QuoteJson(ToolKind + "_overlay") + ","
                   + "\"phase\":" + VisualToolPacketBuilder.QuoteJson(phase)
                   + "}";
        }

        protected string EmitPhase(
            string phase,
            string deliveryPreference,
            string assetPath = "",
            string mimeType = "",
            float attentionHint = 0f)
        {
            if (!FeatureEnabled)
                return SetStatus(ToolKind + "_dev_flag_off_app024_required", false);

            var packet = BuildPacket(phase, deliveryPreference, attentionHint);
            packet.asset_path = assetPath ?? "";
            packet.mime_type = mimeType ?? "";

            if (!RuntimeHttpEnabled || !sendHttpLifecycleEvents)
            {
                LastHttpStatus = "visual_tool_http_dev_disabled";
                UpdateOverlay();
                return SetStatus(ToolKind + "_" + phase + "_local_only", true);
            }

            ResolveClient();
            if (httpClient == null || !httpClient.HasEndpoint)
            {
                LastHttpStatus = "visual_tool_http_endpoint_missing";
                UpdateOverlay();
                return SetStatus(ToolKind + "_" + phase + "_local_http_missing", false);
            }

            StartCoroutine(SendLifecycle(packet));
            return SetStatus(ToolKind + "_" + phase + "_queued", true);
        }

        protected string SetStatus(string status, bool ok)
        {
            LastStatus = string.IsNullOrWhiteSpace(status) ? ToolKind + "_idle" : status;
            if (!ok && string.IsNullOrWhiteSpace(LastHttpStatus))
                LastHttpStatus = LastStatus;
            UpdateOverlay();
            return LastStatus;
        }

        protected abstract void UpdateOverlay();

        protected virtual void SetOverlayVisibleForScreenRegionAsset(bool visible)
        {
        }

        protected string QueueScreenRegionAssetLifecycle(
            string phase,
            string deliveryPreference,
            float attentionHint)
        {
            if (!EnsureOpenForStablePhase()) return LastStatus;
            ApplyStablePhaseLocalState(phase);
            if (!enableScreenRegionAssetCapture)
                return SetStatus(ToolKind + "_screen_region_asset_disabled", false);
            if (!RuntimeHttpEnabled || !sendHttpLifecycleEvents)
                return EmitPhase(phase, deliveryPreference, attentionHint: attentionHint);
            ResolveClient();
            if (httpClient == null || !httpClient.HasEndpoint)
            {
                LastHttpStatus = "visual_tool_http_endpoint_missing";
                UpdateOverlay();
                return SetStatus(ToolKind + "_screen_asset_http_missing", false);
            }

            var packet = BuildPacket(phase, deliveryPreference, attentionHint);
            StartCoroutine(CaptureScreenRegionAssetThenLifecycle(packet));
            return SetStatus(ToolKind + "_screen_asset_" + phase + "_queued", true);
        }

        protected struct PointerSample
        {
            public Vector2 position;
            public Vector2 delta;
            public bool pressed;
            public bool held;
            public bool released;
            public int pointerId;
        }

        protected bool TryReadPrimaryPointer(out PointerSample sample)
        {
            sample = default;
            if (Input.touchCount > 0)
            {
                Touch touch = Input.GetTouch(0);
                sample.position = touch.position;
                sample.delta = touch.deltaPosition;
                sample.pressed = touch.phase == TouchPhase.Began;
                sample.held = touch.phase == TouchPhase.Moved
                              || touch.phase == TouchPhase.Stationary
                              || touch.phase == TouchPhase.Began;
                sample.released = touch.phase == TouchPhase.Ended
                                  || touch.phase == TouchPhase.Canceled;
                sample.pointerId = touch.fingerId;
                return true;
            }

            Vector2 mouse = Input.mousePosition;
            bool mouseDown = Input.GetMouseButtonDown(0);
            bool mouseHeld = Input.GetMouseButton(0);
            bool mouseUp = Input.GetMouseButtonUp(0);
            if (!mouseDown && !mouseHeld && !mouseUp)
            {
                _hasLastMousePosition = false;
                return false;
            }

            Vector2 delta = _hasLastMousePosition ? mouse - _lastMousePosition : Vector2.zero;
            _lastMousePosition = mouse;
            _hasLastMousePosition = mouseHeld || mouseDown;

            sample.position = mouse;
            sample.delta = delta;
            sample.pressed = mouseDown;
            sample.held = mouseHeld || mouseDown;
            sample.released = mouseUp;
            sample.pointerId = -1;
            return true;
        }

        protected bool IsPointerOverUi(PointerSample sample)
        {
            if (EventSystem.current == null) return false;
            return sample.pointerId >= 0
                ? EventSystem.current.IsPointerOverGameObject(sample.pointerId)
                : EventSystem.current.IsPointerOverGameObject();
        }

        protected static void EnsureEventSystemForDevCanvas()
        {
            if (EventSystem.current != null) return;

            var eventSystem = new GameObject("VisualToolDevEventSystem");
            eventSystem.AddComponent<EventSystem>();
            eventSystem.AddComponent<StandaloneInputModule>();
        }

        protected static Vector2 ScreenToNormalizedTopLeft(Vector2 screenPosition)
        {
            float width = Mathf.Max(1f, Screen.width);
            float height = Mathf.Max(1f, Screen.height);
            return new Vector2(
                Mathf.Clamp01(screenPosition.x / width),
                Mathf.Clamp01(1f - (screenPosition.y / height)));
        }

        protected static Vector2 ScreenDeltaToNormalizedTopLeft(Vector2 deltaPixels)
        {
            float width = Mathf.Max(1f, Screen.width);
            float height = Mathf.Max(1f, Screen.height);
            return new Vector2(deltaPixels.x / width, -deltaPixels.y / height);
        }

        protected static bool RegionContains(VisualToolRegion region, Vector2 normalizedTopLeft)
        {
            var r = region.Clamped();
            return normalizedTopLeft.x >= r.x
                   && normalizedTopLeft.x <= r.x + r.width
                   && normalizedTopLeft.y >= r.y
                   && normalizedTopLeft.y <= r.y + r.height;
        }

        protected static VisualToolRegion RegionCenteredAt(
            Vector2 normalizedTopLeft,
            VisualToolRegion region,
            float minWidth,
            float minHeight)
        {
            var r = region.Clamped();
            float width = Mathf.Max(minWidth, r.width);
            float height = Mathf.Max(minHeight, r.height);
            return VisualToolRegion.ScreenNormalized(
                normalizedTopLeft.x - width * 0.5f,
                normalizedTopLeft.y - height * 0.5f,
                width,
                height);
        }

        protected void ResolveClient()
        {
            if (httpClient == null) httpClient = FindObjectOfType<VisualToolHttpClient>();
            if (httpClient == null) httpClient = gameObject.AddComponent<VisualToolHttpClient>();
        }

        private IEnumerator SendLifecycle(VisualToolLifecyclePacket packet)
        {
            LastHttpStatus = "event_pending:" + packet.interaction_phase;
            UpdateOverlay();
            RequestResult<VisualToolLifecycleResultDto> result = default;
            yield return httpClient.SendLifecycle(packet, r => result = r);
            if (result.Success && result.Value != null)
            {
                LastReceiptJson = result.Value.raw_json ?? "";
                LastHttpStatus = httpClient.LastLifecycleStatus;
                SetStatus(ToolKind + "_" + packet.interaction_phase + "_sent", true);
            }
            else
            {
                LastHttpStatus = string.IsNullOrWhiteSpace(result.Error) ? httpClient.LastLifecycleStatus : result.Error;
                SetStatus(ToolKind + "_" + packet.interaction_phase + "_http_failed", false);
            }
            UpdateOverlay();
        }

        private IEnumerator UploadAssetThenLifecycle(VisualToolLifecyclePacket packet, byte[] imageBytes, string mimeType)
        {
            LastHttpStatus = "asset_pending:" + packet.interaction_phase;
            LastAssetStatus = "asset_pending:" + packet.interaction_phase;
            UpdateOverlay();
            string assetId = packet.tool_id + "_" + packet.interaction_phase + "_" + packet.timebase.wall_time_ms;
            RequestResult<VisualToolAssetUploadResultDto> assetResult = default;
            yield return httpClient.UploadAsset(assetId, imageBytes, mimeType, packet, r => assetResult = r);
            if (!assetResult.Success || assetResult.Value == null)
            {
                LastHttpStatus = string.IsNullOrWhiteSpace(assetResult.Error) ? httpClient.LastAssetStatus : assetResult.Error;
                LastAssetStatus = LastHttpStatus;
                AddMetaField(packet, "asset_status", "asset_upload_failed");
                if (sendLifecycleIfAssetUploadFails)
                {
                    packet.asset_path = "";
                    packet.asset_uri = "";
                    packet.mime_type = "";
                    yield return SendLifecycle(packet);
                }
                else
                {
                    SetStatus(ToolKind + "_asset_upload_failed", false);
                }
                yield break;
            }

            LastAssetStatus = httpClient.LastAssetStatus;

            packet.asset_path = assetResult.Value.asset_path ?? "";
            packet.asset_uri = assetResult.Value.asset_uri ?? "";
            packet.mime_type = string.IsNullOrWhiteSpace(assetResult.Value.mime_type)
                ? (mimeType ?? "image/png")
                : assetResult.Value.mime_type;

            RequestResult<VisualToolLifecycleResultDto> lifecycleResult = default;
            yield return httpClient.SendLifecycle(packet, r => lifecycleResult = r);
            if (lifecycleResult.Success && lifecycleResult.Value != null)
            {
                LastReceiptJson = lifecycleResult.Value.raw_json ?? "";
                LastHttpStatus = httpClient.LastLifecycleStatus;
                SetStatus(ToolKind + "_" + packet.interaction_phase + "_asset_sent", true);
            }
            else
            {
                LastHttpStatus = string.IsNullOrWhiteSpace(lifecycleResult.Error)
                    ? httpClient.LastLifecycleStatus
                    : lifecycleResult.Error;
                SetStatus(ToolKind + "_" + packet.interaction_phase + "_asset_event_failed", false);
            }
            UpdateOverlay();
        }

        private IEnumerator CaptureScreenRegionAssetThenLifecycle(VisualToolLifecyclePacket packet)
        {
            LastRenderStatus = ToolKind + "_screen_region_asset_capture_pending";
            LastAssetStatus = "screen_region_asset_pending:" + packet.interaction_phase;
            bool restoreOverlay = hideOverlayDuringAssetCapture && showDevHud;
            if (restoreOverlay)
                SetOverlayVisibleForScreenRegionAsset(false);
            else
                UpdateOverlay();

            yield return new WaitForEndOfFrame();

            Texture2D texture = null;
            byte[] pngBytes = null;
            string captureError = "";
            try
            {
                var rect = ScreenPixelRect(CurrentRegion);
                if (rect.width < Mathf.Max(1, minScreenRegionAssetPixels)
                    || rect.height < Mathf.Max(1, minScreenRegionAssetPixels))
                {
                    captureError = "screen_region_asset_too_small";
                }
                else
                {
                    texture = new Texture2D((int)rect.width, (int)rect.height, TextureFormat.RGB24, false);
                    texture.ReadPixels(rect, 0, 0, false);
                    texture.Apply(false);
                    pngBytes = texture.EncodeToPNG();
                }
            }
            catch (Exception ex)
            {
                captureError = "screen_region_asset_capture_failed:" + ex.Message;
            }
            finally
            {
                if (texture != null)
                    Destroy(texture);
                if (restoreOverlay)
                    SetOverlayVisibleForScreenRegionAsset(true);
            }

            if (!string.IsNullOrWhiteSpace(captureError) || pngBytes == null || pngBytes.Length == 0)
            {
                LastRenderStatus = string.IsNullOrWhiteSpace(captureError)
                    ? "screen_region_asset_empty"
                    : captureError;
                LastAssetStatus = LastRenderStatus;
                AddMetaField(packet, "asset_status", LastRenderStatus);
                if (sendLifecycleIfAssetCaptureFails)
                {
                    packet.asset_path = "";
                    packet.asset_uri = "";
                    packet.mime_type = "";
                    yield return SendLifecycle(packet);
                }
                else
                {
                    SetStatus(ToolKind + "_screen_asset_capture_failed", false);
                }
                yield break;
            }

            LastRenderStatus = ToolKind + "_screen_region_asset_png";
            yield return UploadAssetThenLifecycle(packet, pngBytes, "image/png");
        }

        private bool EnsureOpenForStablePhase()
        {
            if (!FeatureEnabled)
            {
                SetStatus(ToolKind + "_dev_flag_off_app024_required", false);
                return false;
            }
            if (!IsOpen)
            {
                BeginPreview();
                return IsOpen;
            }
            return true;
        }

        private void ApplyStablePhaseLocalState(string phase)
        {
            if (string.Equals(phase, VisualToolPhases.Confirm, StringComparison.Ordinal)
                || string.Equals(phase, VisualToolPhases.ExplicitSend, StringComparison.Ordinal)
                || string.Equals(phase, VisualToolPhases.Lock, StringComparison.Ordinal))
            {
                IsLocked = true;
                IsSelected = true;
                UpdateOverlay();
            }
        }

        private Rect ScreenPixelRect(VisualToolRegion region)
        {
            var r = region.Clamped();
            int screenWidth = Mathf.Max(1, Screen.width);
            int screenHeight = Mathf.Max(1, Screen.height);
            int x = Mathf.Clamp(Mathf.RoundToInt(r.x * screenWidth), 0, screenWidth - 1);
            int y = Mathf.Clamp(Mathf.RoundToInt((1f - r.y - r.height) * screenHeight), 0, screenHeight - 1);
            int width = Mathf.Clamp(Mathf.RoundToInt(r.width * screenWidth), 1, screenWidth - x);
            int height = Mathf.Clamp(Mathf.RoundToInt(r.height * screenHeight), 1, screenHeight - y);
            return new Rect(x, y, width, height);
        }

        private static void AddMetaField(VisualToolLifecyclePacket packet, string key, string value)
        {
            if (packet == null || string.IsNullOrWhiteSpace(key)) return;
            string meta = string.IsNullOrWhiteSpace(packet.meta_json) ? "{}" : packet.meta_json.Trim();
            if (!meta.StartsWith("{", StringComparison.Ordinal) || !meta.EndsWith("}", StringComparison.Ordinal))
                meta = "{}";
            string body = meta.Length > 2 ? meta.Substring(1, meta.Length - 2).Trim() : "";
            string addition = VisualToolPacketBuilder.QuoteJson(key) + ":" + VisualToolPacketBuilder.QuoteJson(value ?? "");
            packet.meta_json = string.IsNullOrWhiteSpace(body)
                ? "{" + addition + "}"
                : "{" + body + "," + addition + "}";
        }

        private bool ShouldSendLowFrequencyUpdate()
        {
            if (Time.unscaledTime - _lastUpdateEventSentAt < Mathf.Max(0.1f, lowFrequencyUpdateIntervalSeconds))
                return false;
            _lastUpdateEventSentAt = Time.unscaledTime;
            return true;
        }

        private void EnsureRuntimeFlags()
        {
            if (_runtimeFlagsLoaded) return;
            var config = ParrotRuntimeConfig.Load();
            _runtimeDevEnabled = config.visualToolDevEnabled;
            _runtimeHttpEnabled = config.visualToolHttpEnabled;
            _runtimeFlagsLoaded = true;
        }
    }
}
