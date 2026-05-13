using System;
using System.Collections;
using System.Text;
using ParrotApp.Config;
using UnityEngine;
using UnityEngine.Networking;

namespace ParrotApp.Backend
{
    public class OrchestratorClient : MonoBehaviour
    {
        [SerializeField] private string orchestratorBaseUrl = "";
        [SerializeField] private string bearerSecret = "";

        public bool HasEndpoint => !string.IsNullOrWhiteSpace(orchestratorBaseUrl);

        private void Awake()
        {
            LoadRuntimeConfig();
        }

        private void LoadRuntimeConfig()
        {
            var config = ParrotRuntimeConfig.Load();
            if (!string.IsNullOrWhiteSpace(config.orchestratorUrl))
                orchestratorBaseUrl = config.orchestratorUrl.TrimEnd('/');
            if (!string.IsNullOrWhiteSpace(config.orchestratorSecret))
                bearerSecret = config.orchestratorSecret;
        }

        public IEnumerator ApplyRoomProfile(
            AppStartupConfigDto config,
            bool forceReconnect,
            Action<OrchestratorResult> onComplete)
        {
            if (!HasEndpoint)
            {
                onComplete?.Invoke(OrchestratorResult.Skipped("orchestrator_url_empty"));
                yield break;
            }

            config = config ?? AppStartupConfigDto.Default();
            config.Normalize();
            string body = "{"
                          + "\"room_profile_id\":" + JsonQuote(config.room_profile_id) + ","
                          + "\"line_id\":" + JsonQuote(config.line_id) + ","
                          + "\"line_profile_id\":" + JsonQuote(config.line_profile_id) + ","
                          + "\"force_reconnect\":" + (forceReconnect ? "true" : "false")
                          + "}";
            yield return PostJson("/apply_room_profile", body, onComplete);
        }

        public IEnumerator SetActiveLine(
            string lineId,
            string lineProfileId,
            bool forceReconnect,
            Action<OrchestratorResult> onComplete)
        {
            if (!HasEndpoint)
            {
                onComplete?.Invoke(OrchestratorResult.Skipped("orchestrator_url_empty"));
                yield break;
            }

            string body = "{"
                          + "\"line_id\":" + JsonQuote(lineId) + ","
                          + "\"line_profile_id\":" + JsonQuote(lineProfileId) + ","
                          + "\"force_reconnect\":" + (forceReconnect ? "true" : "false")
                          + "}";
            yield return PostJson("/set_active_line", body, onComplete);
        }

        public IEnumerator ForceUnityReconnect(string reason, Action<OrchestratorResult> onComplete)
        {
            if (!HasEndpoint)
            {
                onComplete?.Invoke(OrchestratorResult.Skipped("orchestrator_url_empty"));
                yield break;
            }

            string body = "{\"reason\":" + JsonQuote(reason) + "}";
            yield return PostJson("/force_unity_reconnect", body, onComplete);
        }

        private IEnumerator PostJson(string path, string body, Action<OrchestratorResult> onComplete)
        {
            string url = orchestratorBaseUrl.TrimEnd('/') + path;
            byte[] bytes = Encoding.UTF8.GetBytes(body ?? "{}");
            using (var req = new UnityWebRequest(url, UnityWebRequest.kHttpVerbPOST))
            {
                req.uploadHandler = new UploadHandlerRaw(bytes);
                req.downloadHandler = new DownloadHandlerBuffer();
                req.SetRequestHeader("Content-Type", "application/json");
                if (!string.IsNullOrWhiteSpace(bearerSecret))
                    req.SetRequestHeader("Authorization", "Bearer " + bearerSecret);

                yield return req.SendWebRequest();
                if (req.result != UnityWebRequest.Result.Success)
                {
                    onComplete?.Invoke(OrchestratorResult.Fail(req.error ?? "orchestrator_request_failed"));
                    yield break;
                }

                string text = req.downloadHandler.text ?? "";
                if (text.Contains("\"status\":\"error\"") || text.Contains("\"status\": \"error\""))
                {
                    onComplete?.Invoke(OrchestratorResult.Fail("orchestrator_status_error"));
                    yield break;
                }

                onComplete?.Invoke(OrchestratorResult.Ok(text));
            }
        }

        private static string JsonQuote(string value)
        {
            if (value == null) return "\"\"";
            return "\"" + value.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";
        }
    }

    public struct OrchestratorResult
    {
        public bool Success;
        public bool SkippedRequest;
        public string Payload;
        public string Error;

        public static OrchestratorResult Ok(string payload)
            => new OrchestratorResult { Success = true, Payload = payload ?? "", Error = "" };

        public static OrchestratorResult Skipped(string reason)
            => new OrchestratorResult { Success = true, SkippedRequest = true, Payload = "", Error = reason ?? "" };

        public static OrchestratorResult Fail(string error)
            => new OrchestratorResult { Success = false, Payload = "", Error = error ?? "" };
    }
}
