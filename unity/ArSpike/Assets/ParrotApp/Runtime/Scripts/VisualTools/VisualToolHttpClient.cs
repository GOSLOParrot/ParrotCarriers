using System;
using System.Collections;
using System.Text;
using ParrotApp.Backend;
using UnityEngine;
using UnityEngine.Networking;

namespace ParrotApp.VisualTools
{
    [Serializable]
    public class VisualToolEvidenceReceiptDto
    {
        public string evidence_id = "";
        public string kind = "";
        public string status = "";
        public string asset_path = "";
        public string mime_type = "";
    }

    [Serializable]
    public class VisualToolDeliveryReceiptDto
    {
        public string resolved_channel = "";
        public bool notify_goslo;
        public bool allow_interrupt;
    }

    [Serializable]
    public class VisualToolLifecycleResultDto
    {
        public bool success;
        public string error = "";
        public string ref_id = "";
        public string ref_kind = "";
        public VisualToolEvidenceReceiptDto evidence = new VisualToolEvidenceReceiptDto();
        public VisualToolDeliveryReceiptDto delivery = new VisualToolDeliveryReceiptDto();
        public string raw_json = "";
    }

    [Serializable]
    public class VisualToolAssetUploadResultDto
    {
        public bool success;
        public string error = "";
        public string asset_id = "";
        public string asset_path = "";
        public string asset_uri = "";
        public string mime_type = "";
        public VisualToolEvidenceReceiptDto evidence = new VisualToolEvidenceReceiptDto();
        public string raw_json = "";
    }

    [Serializable]
    internal class VisualToolErrorEnvelope
    {
        public string detail = "";
        public string error = "";
    }

    [DisallowMultipleComponent]
    public class VisualToolHttpClient : MonoBehaviour
    {
        [SerializeField] private string appApiBaseUrl = "";
        [SerializeField] private string bearerSecret = "";

        public string AppApiBaseUrl
        {
            get => appApiBaseUrl;
            set => appApiBaseUrl = (value ?? "").TrimEnd('/');
        }

        public bool HasEndpoint => !string.IsNullOrWhiteSpace(appApiBaseUrl);
        public string LastLifecycleStatus { get; private set; } = "visual_tool_http_idle";
        public string LastAssetStatus { get; private set; } = "visual_tool_asset_idle";
        public bool LastLifecycleOk { get; private set; }
        public bool LastAssetOk { get; private set; }

        private void Awake()
        {
            LoadRuntimeConfig();
        }

        private void LoadRuntimeConfig()
        {
            var config = ParrotRuntimeConfig.Load();
            if (!string.IsNullOrWhiteSpace(config.appApiUrl))
                appApiBaseUrl = config.appApiUrl.TrimEnd('/');
            if (!string.IsNullOrWhiteSpace(config.appApiSecret))
                bearerSecret = config.appApiSecret;
        }

        public IEnumerator SendLifecycle(
            VisualToolLifecyclePacket packet,
            Action<RequestResult<VisualToolLifecycleResultDto>> onComplete)
        {
            if (!HasEndpoint)
            {
                LastLifecycleOk = false;
                LastLifecycleStatus = "visual_tool_http_endpoint_missing";
                onComplete?.Invoke(RequestResult<VisualToolLifecycleResultDto>.Fail(LastLifecycleStatus));
                yield break;
            }

            string url = appApiBaseUrl.TrimEnd('/') + "/api/app/visual-tool/event";
            string body = VisualToolPacketBuilder.ToJson(packet);
            byte[] bytes = Encoding.UTF8.GetBytes(body);
            using (var req = new UnityWebRequest(url, UnityWebRequest.kHttpVerbPOST))
            {
                req.uploadHandler = new UploadHandlerRaw(bytes);
                req.downloadHandler = new DownloadHandlerBuffer();
                req.SetRequestHeader("Content-Type", "application/json");
                ApplyAuth(req);
                yield return req.SendWebRequest();

                if (req.result != UnityWebRequest.Result.Success)
                {
                    LastLifecycleOk = false;
                    LastLifecycleStatus = RequestErrorLabel(req, "visual_tool_lifecycle_request_failed");
                    onComplete?.Invoke(RequestResult<VisualToolLifecycleResultDto>.Fail(LastLifecycleStatus));
                    yield break;
                }

                string text = req.downloadHandler.text ?? "";
                try
                {
                    var dto = JsonUtility.FromJson<VisualToolLifecycleResultDto>(text);
                    if (dto == null)
                    {
                        LastLifecycleOk = false;
                        LastLifecycleStatus = "visual_tool_lifecycle_empty_response";
                        onComplete?.Invoke(RequestResult<VisualToolLifecycleResultDto>.Fail(LastLifecycleStatus));
                        yield break;
                    }

                    dto.raw_json = text;
                    LastLifecycleOk = dto.success;
                    LastLifecycleStatus = dto.success
                        ? LifecycleOkLabel(packet, dto)
                        : ErrorLabel(text, "visual_tool_lifecycle_rejected");
                    if (!dto.success)
                    {
                        onComplete?.Invoke(RequestResult<VisualToolLifecycleResultDto>.Fail(LastLifecycleStatus));
                        yield break;
                    }

                    onComplete?.Invoke(RequestResult<VisualToolLifecycleResultDto>.Ok(dto));
                }
                catch (Exception ex)
                {
                    LastLifecycleOk = false;
                    LastLifecycleStatus = "visual_tool_lifecycle_parse_failed:" + ex.Message;
                    onComplete?.Invoke(RequestResult<VisualToolLifecycleResultDto>.Fail(LastLifecycleStatus));
                }
            }
        }

        public IEnumerator UploadAsset(
            string assetId,
            byte[] bytes,
            string mimeType,
            VisualToolLifecyclePacket packet,
            Action<RequestResult<VisualToolAssetUploadResultDto>> onComplete)
        {
            if (!HasEndpoint)
            {
                LastAssetOk = false;
                LastAssetStatus = "visual_tool_asset_endpoint_missing";
                onComplete?.Invoke(RequestResult<VisualToolAssetUploadResultDto>.Fail(LastAssetStatus));
                yield break;
            }
            if (bytes == null || bytes.Length == 0)
            {
                LastAssetOk = false;
                LastAssetStatus = "visual_tool_asset_empty_bytes";
                onComplete?.Invoke(RequestResult<VisualToolAssetUploadResultDto>.Fail(LastAssetStatus));
                yield break;
            }

            string safeAssetId = string.IsNullOrWhiteSpace(assetId)
                ? VisualToolPacketBuilder.GenerateEventId()
                : assetId.Trim();
            string contentType = string.IsNullOrWhiteSpace(mimeType) ? "image/png" : mimeType.Trim();
            string url = appApiBaseUrl.TrimEnd('/') + "/api/app/visual-tool/asset/" + UnityWebRequest.EscapeURL(safeAssetId);
            using (var req = new UnityWebRequest(url, UnityWebRequest.kHttpVerbPOST))
            {
                req.uploadHandler = new UploadHandlerRaw(bytes);
                req.downloadHandler = new DownloadHandlerBuffer();
                req.SetRequestHeader("Content-Type", contentType);
                if (packet != null)
                {
                    req.SetRequestHeader("X-Parrot-Tool-Id", packet.tool_id ?? "");
                    req.SetRequestHeader("X-Parrot-Tool-Kind", packet.tool_kind ?? "");
                    req.SetRequestHeader("X-Parrot-Tool-Phase", packet.interaction_phase ?? "");
                    req.SetRequestHeader("X-Parrot-Source-Surface", packet.source_surface ?? "");
                    req.SetRequestHeader("X-Parrot-Source-Id", packet.tool_event_id ?? "");
                    req.SetRequestHeader("X-Parrot-Description", AssetDescription(packet));
                    req.SetRequestHeader("X-Parrot-Timebase", VisualToolPacketBuilder.TimebaseJson(packet.timebase));
                    req.SetRequestHeader("X-Parrot-Region", VisualToolPacketBuilder.RegionJson(packet.region));
                }
                ApplyAuth(req);
                yield return req.SendWebRequest();

                if (req.result != UnityWebRequest.Result.Success)
                {
                    LastAssetOk = false;
                    LastAssetStatus = RequestErrorLabel(req, "visual_tool_asset_request_failed");
                    onComplete?.Invoke(RequestResult<VisualToolAssetUploadResultDto>.Fail(LastAssetStatus));
                    yield break;
                }

                string text = req.downloadHandler.text ?? "";
                try
                {
                    var dto = JsonUtility.FromJson<VisualToolAssetUploadResultDto>(text);
                    if (dto == null)
                    {
                        LastAssetOk = false;
                        LastAssetStatus = "visual_tool_asset_empty_response";
                        onComplete?.Invoke(RequestResult<VisualToolAssetUploadResultDto>.Fail(LastAssetStatus));
                        yield break;
                    }

                    dto.raw_json = text;
                    LastAssetOk = dto.success;
                    LastAssetStatus = dto.success
                        ? "asset_ok:" + ShortLabel(dto.asset_path, safeAssetId, 34)
                        : ErrorLabel(text, "visual_tool_asset_rejected");
                    if (!dto.success)
                    {
                        onComplete?.Invoke(RequestResult<VisualToolAssetUploadResultDto>.Fail(LastAssetStatus));
                        yield break;
                    }

                    onComplete?.Invoke(RequestResult<VisualToolAssetUploadResultDto>.Ok(dto));
                }
                catch (Exception ex)
                {
                    LastAssetOk = false;
                    LastAssetStatus = "visual_tool_asset_parse_failed:" + ex.Message;
                    onComplete?.Invoke(RequestResult<VisualToolAssetUploadResultDto>.Fail(LastAssetStatus));
                }
            }
        }

        private void ApplyAuth(UnityWebRequest req)
        {
            if (!string.IsNullOrWhiteSpace(bearerSecret))
                req.SetRequestHeader("Authorization", "Bearer " + bearerSecret);
        }

        private static string LifecycleOkLabel(VisualToolLifecyclePacket packet, VisualToolLifecycleResultDto dto)
        {
            string phase = packet != null ? packet.interaction_phase : "";
            string delivery = dto != null && dto.delivery != null ? dto.delivery.resolved_channel : "";
            if (string.IsNullOrWhiteSpace(delivery)) delivery = "accepted";
            return "event_ok:" + ShortLabel(phase, "phase", 16) + "/" + ShortLabel(delivery, "delivery", 22);
        }

        private static string AssetDescription(VisualToolLifecyclePacket packet)
        {
            string label = packet != null && !string.IsNullOrWhiteSpace(packet.label)
                ? packet.label
                : (packet != null ? packet.tool_kind : "");
            string phase = packet != null ? packet.interaction_phase : "";
            return ShortLabel("visual_tool_asset:" + label + ":" + phase, "visual_tool_asset", 96);
        }

        private static string ErrorLabel(string json, string fallback)
        {
            try
            {
                var envelope = JsonUtility.FromJson<VisualToolErrorEnvelope>(json ?? "{}");
                if (envelope != null)
                {
                    if (!string.IsNullOrWhiteSpace(envelope.error)) return envelope.error;
                    if (!string.IsNullOrWhiteSpace(envelope.detail)) return envelope.detail;
                }
            }
            catch
            {
                // Keep the original fallback if the backend returned non-JSON text.
            }
            return fallback;
        }

        private static string RequestErrorLabel(UnityWebRequest req, string fallback)
        {
            string body = req != null && req.downloadHandler != null ? req.downloadHandler.text : "";
            string backendLabel = ErrorLabel(body, "");
            if (!string.IsNullOrWhiteSpace(backendLabel))
                return backendLabel;
            if (req != null && !string.IsNullOrWhiteSpace(req.error))
                return req.error;
            return fallback;
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
