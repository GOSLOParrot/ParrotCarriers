using System;
using System.Collections;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using ParrotApp.Backend;
using UnityEngine;

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
        private sealed class HttpTextResult
        {
            public bool Success;
            public int StatusCode;
            public string Text = "";
            public string Error = "";

            public static HttpTextResult Ok(int statusCode, string text)
                => new HttpTextResult
                {
                    Success = true,
                    StatusCode = statusCode,
                    Text = text ?? "",
                    Error = ""
                };

            public static HttpTextResult Fail(int statusCode, string text, string error)
                => new HttpTextResult
                {
                    Success = false,
                    StatusCode = statusCode,
                    Text = text ?? "",
                    Error = error ?? ""
                };
        }

        // Match PhotoController's phone-safe HTTP path for local laptop backends.
        private static readonly HttpClient SharedHttpClient = new HttpClient { Timeout = TimeSpan.FromSeconds(10) };
        private static readonly int[] RetryDelaysMs = { 500, 1000, 2000 };

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
            Task<HttpTextResult> task = PostJsonAsync(url, body);
            yield return AwaitHttpTextTask(task);

            HttpTextResult http = ResolveHttpTextTask(task, "visual_tool_lifecycle_request_failed");
            if (!http.Success)
            {
                LastLifecycleOk = false;
                LastLifecycleStatus = RequestErrorLabel(http, "visual_tool_lifecycle_request_failed");
                onComplete?.Invoke(RequestResult<VisualToolLifecycleResultDto>.Fail(LastLifecycleStatus));
                yield break;
            }

            string text = http.Text ?? "";
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
            string url = appApiBaseUrl.TrimEnd('/') + "/api/app/visual-tool/asset/" + Uri.EscapeDataString(safeAssetId);
            Task<HttpTextResult> task = PostBytesAsync(url, bytes, contentType, request =>
            {
                if (packet != null)
                {
                    AddHeader(request, "X-Parrot-Tool-Id", packet.tool_id ?? "");
                    AddHeader(request, "X-Parrot-Tool-Kind", packet.tool_kind ?? "");
                    AddHeader(request, "X-Parrot-Tool-Phase", packet.interaction_phase ?? "");
                    AddHeader(request, "X-Parrot-Source-Surface", packet.source_surface ?? "");
                    AddHeader(request, "X-Parrot-Source-Id", packet.tool_event_id ?? "");
                    AddHeader(request, "X-Parrot-Description", AssetDescription(packet));
                    AddHeader(request, "X-Parrot-Timebase", VisualToolPacketBuilder.TimebaseJson(packet.timebase));
                    AddHeader(request, "X-Parrot-Region", VisualToolPacketBuilder.RegionJson(packet.region));
                }
            });
            yield return AwaitHttpTextTask(task);

            HttpTextResult http = ResolveHttpTextTask(task, "visual_tool_asset_request_failed");
            if (!http.Success)
            {
                LastAssetOk = false;
                LastAssetStatus = RequestErrorLabel(http, "visual_tool_asset_request_failed");
                onComplete?.Invoke(RequestResult<VisualToolAssetUploadResultDto>.Fail(LastAssetStatus));
                yield break;
            }

            string text = http.Text ?? "";
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

        private void ApplyAuth(HttpRequestMessage request)
        {
            if (!string.IsNullOrWhiteSpace(bearerSecret))
                AddHeader(request, "Authorization", "Bearer " + bearerSecret);
        }

        private Task<HttpTextResult> PostJsonAsync(string url, string body)
        {
            return PostBytesAsync(
                url,
                Encoding.UTF8.GetBytes(body ?? ""),
                "application/json",
                request => AddHeader(request, "Accept", "application/json"));
        }

        private async Task<HttpTextResult> PostBytesAsync(
            string url,
            byte[] payload,
            string contentType,
            Action<HttpRequestMessage> configureRequest)
        {
            HttpTextResult last = null;
            int attempts = RetryDelaysMs.Length + 1;
            for (int attempt = 0; attempt < attempts; attempt++)
            {
                if (attempt > 0)
                    await Task.Delay(RetryDelaysMs[attempt - 1]);

                try
                {
                    using (var request = new HttpRequestMessage(HttpMethod.Post, url))
                    using (var content = new ByteArrayContent(payload ?? new byte[0]))
                    {
                        ApplyContentType(content, contentType);
                        request.Content = content;
                        ApplyAuth(request);
                        configureRequest?.Invoke(request);

                        using (var response = await SharedHttpClient.SendAsync(request))
                        {
                            string text = response.Content != null
                                ? await response.Content.ReadAsStringAsync()
                                : "";
                            int statusCode = (int)response.StatusCode;
                            if (response.IsSuccessStatusCode)
                                return HttpTextResult.Ok(statusCode, text);

                            last = HttpTextResult.Fail(
                                statusCode,
                                text,
                                "http_status_" + statusCode);

                            if (!ShouldRetryStatus(statusCode))
                                return last;
                        }
                    }
                }
                catch (Exception ex)
                {
                    last = HttpTextResult.Fail(0, "", ex.GetType().Name + ":" + ex.Message);
                }
            }

            return last ?? HttpTextResult.Fail(0, "", "http_request_failed");
        }

        private static IEnumerator AwaitHttpTextTask(Task<HttpTextResult> task)
        {
            while (task != null && !task.IsCompleted)
                yield return null;
        }

        private static HttpTextResult ResolveHttpTextTask(Task<HttpTextResult> task, string fallback)
        {
            if (task == null)
                return HttpTextResult.Fail(0, "", fallback);
            if (task.IsCanceled)
                return HttpTextResult.Fail(0, "", fallback + ":canceled");
            if (task.IsFaulted)
            {
                Exception ex = task.Exception != null ? task.Exception.GetBaseException() : null;
                return HttpTextResult.Fail(0, "", ex != null ? ex.GetType().Name + ":" + ex.Message : fallback);
            }

            return task.Result ?? HttpTextResult.Fail(0, "", fallback);
        }

        private static void ApplyContentType(ByteArrayContent content, string contentType)
        {
            string value = string.IsNullOrWhiteSpace(contentType) ? "application/octet-stream" : contentType.Trim();
            try
            {
                content.Headers.ContentType = new MediaTypeHeaderValue(value);
            }
            catch
            {
                content.Headers.TryAddWithoutValidation("Content-Type", value);
            }
        }

        private static void AddHeader(HttpRequestMessage request, string name, string value)
        {
            if (request == null || string.IsNullOrWhiteSpace(name))
                return;
            request.Headers.TryAddWithoutValidation(name, value ?? "");
        }

        private static bool ShouldRetryStatus(int statusCode)
        {
            return statusCode == 408 || statusCode == 429 || statusCode >= 500;
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

        private static string RequestErrorLabel(HttpTextResult result, string fallback)
        {
            string body = result != null ? result.Text : "";
            string backendLabel = ErrorLabel(body, "");
            if (!string.IsNullOrWhiteSpace(backendLabel))
                return backendLabel;
            if (result != null && !string.IsNullOrWhiteSpace(result.Error))
                return result.Error;
            if (result != null && result.StatusCode > 0)
                return fallback + ":" + result.StatusCode;
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
