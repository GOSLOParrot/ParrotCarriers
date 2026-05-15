using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

namespace ParrotApp.Backend
{
    [Serializable]
    public class AppCanvasSnapshotDto
    {
        public float generated_at;
        public string active_workspace_id = "";
        public AppModuleStatusDto[] module_statuses = new AppModuleStatusDto[0];
        public AppWorkspaceDto[] workspaces = new AppWorkspaceDto[0];
        public AppPaperNoteDto[] paper_notes = new AppPaperNoteDto[0];
        public AppPhotoRefDto[] photo_refs = new AppPhotoRefDto[0];
        public AppToolCardDto[] tool_cabinet = new AppToolCardDto[0];
        public AppAssetManifestDto asset_manifest = new AppAssetManifestDto();

        public bool HasUsableHomePayload
        {
            get
            {
                bool hasMenuShell =
                    (module_statuses != null && module_statuses.Length > 0)
                    || (workspaces != null && workspaces.Length > 0)
                    || (tool_cabinet != null && tool_cabinet.Length > 0);

                return generated_at > 0
                       && !string.IsNullOrWhiteSpace(active_workspace_id)
                       && hasMenuShell;
            }
        }
    }

    [Serializable]
    public class AppModuleStatusDto
    {
        public string module_id = "";
        public string state = "";
        public string health = "";
        public string summary = "";
    }

    [Serializable]
    public class AppWorkspaceDto
    {
        public int schema_version;
        public string workspace_id = "";
        public string display_name = "";
        public string kind = "";
        public string description = "";
        public string layout_kind = "";
        public bool enabled = true;
        public bool is_fallback;
    }

    [Serializable]
    public class AppPaperNoteDto
    {
        public string ref_id = "";
        public string title = "";
        public string summary = "";
    }

    [Serializable]
    public class AppPhotoRefDto
    {
        public string ref_id = "";
        public string title = "";
        public string summary = "";
    }

    [Serializable]
    public class AppToolCardDto
    {
        public string tool_id = "";
        public string label = "";
        public string state = "";
        public bool enabled;
        public string summary = "";
        public string asset_slot = "";
        public string[] action_endpoints = new string[0];
    }

    [Serializable]
    public class AppAssetManifestDto
    {
        public int schema_version;
    }

    [Serializable]
    public class AppPersonaOptionDto
    {
        public string persona_id = "";
        public string display_name = "";
        public string description = "";
        public int schema_version;
        public string[] tags = new string[0];
    }

    [Serializable]
    public class AppLineProfileOptionDto
    {
        public int schema_version;
        public string kind = "";
        public string line_profile_id = "";
        public string display_name = "";
        public string line_id = "";
        public AppLineProfileTtsDto tts = new AppLineProfileTtsDto();
        public AppLineProfileVoiceprintDto voiceprint = new AppLineProfileVoiceprintDto();
        public AppLineProfileEchoDto echo = new AppLineProfileEchoDto();
    }

    [Serializable]
    public class AppLineProfileTtsDto
    {
        public string provider = "";
        public string language = "";
        public string voice_name = "";
    }

    [Serializable]
    public class AppLineProfileVoiceprintDto
    {
        public bool enabled;
        public string speaker_state = "";
    }

    [Serializable]
    public class AppLineProfileEchoDto
    {
        public string output_route = "";
        public string handling_mode = "";
    }

    [Serializable]
    public class AppPersonaOptionArrayEnvelope
    {
        public AppPersonaOptionDto[] items = new AppPersonaOptionDto[0];
    }

    [Serializable]
    public class AppLineProfileOptionArrayEnvelope
    {
        public AppLineProfileOptionDto[] items = new AppLineProfileOptionDto[0];
    }

    [Serializable]
    public class AppActionResultDto
    {
        public string action = "";
        public bool success;
        public string message = "";
        public string intent_workspace_ref_id = "";
        public string[] applied_keys = new string[0];
    }

    /// <summary>
    /// App HTTP client for the formal home/menu read model.
    ///
    /// Durable menu and canvas snapshots belong to the App HTTP facade. LiveKit
    /// RPC/ECP stays for latency-sensitive in-room control and status messages,
    /// not for menu save/apply or the full canvas payload.
    /// </summary>
    [DisallowMultipleComponent]
    public class AppHomeMenuClient : MonoBehaviour
    {
        // Deliberately empty by default. A phone build must get this from
        // gitignored Resources/parrot_config.json or an explicit Inspector
        // override; otherwise the menu loader should report a missing endpoint
        // instead of trying the device's own localhost.
        [SerializeField] private string appApiBaseUrl = "";
        [SerializeField] private string bearerSecret = "";

        public string AppApiBaseUrl
        {
            get => appApiBaseUrl;
            set => appApiBaseUrl = (value ?? "").TrimEnd('/');
        }

        public bool HasEndpoint => !string.IsNullOrWhiteSpace(appApiBaseUrl);

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

        public IEnumerator LoadCanvasSnapshot(Action<RequestResult<AppCanvasSnapshotDto>> onComplete)
        {
            if (!HasEndpoint)
            {
                onComplete?.Invoke(RequestResult<AppCanvasSnapshotDto>.Fail("app_api_url_empty"));
                yield break;
            }

            string url = appApiBaseUrl.TrimEnd('/') + "/api/app/canvas";
            using (var req = UnityWebRequest.Get(url))
            {
                ApplyAuth(req);
                yield return req.SendWebRequest();

                if (req.result != UnityWebRequest.Result.Success)
                {
                    onComplete?.Invoke(RequestResult<AppCanvasSnapshotDto>.Fail(req.error ?? "canvas_request_failed"));
                    yield break;
                }

                try
                {
                    var dto = JsonUtility.FromJson<AppCanvasSnapshotDto>(req.downloadHandler.text);
                    if (dto == null || !dto.HasUsableHomePayload)
                    {
                        onComplete?.Invoke(RequestResult<AppCanvasSnapshotDto>.Fail("canvas_snapshot_empty"));
                        yield break;
                    }
                    onComplete?.Invoke(RequestResult<AppCanvasSnapshotDto>.Ok(dto));
                }
                catch (Exception ex)
                {
                    onComplete?.Invoke(RequestResult<AppCanvasSnapshotDto>.Fail("canvas_parse_failed:" + ex.Message));
                }
            }
        }

        public IEnumerator LoadPersonas(Action<RequestResult<AppPersonaOptionDto[]>> onComplete)
        {
            RequestResult<string> result = default;
            yield return LoadText("/api/app/personas", "personas", r => result = r);
            if (!result.Success)
            {
                onComplete?.Invoke(RequestResult<AppPersonaOptionDto[]>.Fail(result.Error));
                yield break;
            }

            try
            {
                var parsed = JsonUtility.FromJson<AppPersonaOptionArrayEnvelope>("{\"items\":" + result.Value + "}");
                onComplete?.Invoke(RequestResult<AppPersonaOptionDto[]>.Ok(
                    parsed != null && parsed.items != null ? parsed.items : new AppPersonaOptionDto[0]));
            }
            catch (Exception ex)
            {
                onComplete?.Invoke(RequestResult<AppPersonaOptionDto[]>.Fail("personas_parse_failed:" + ex.Message));
            }
        }

        public IEnumerator LoadLineProfiles(Action<RequestResult<AppLineProfileOptionDto[]>> onComplete)
        {
            RequestResult<string> result = default;
            yield return LoadText("/api/app/line-profiles", "line_profiles", r => result = r);
            if (!result.Success)
            {
                onComplete?.Invoke(RequestResult<AppLineProfileOptionDto[]>.Fail(result.Error));
                yield break;
            }

            try
            {
                var parsed = JsonUtility.FromJson<AppLineProfileOptionArrayEnvelope>("{\"items\":" + result.Value + "}");
                onComplete?.Invoke(RequestResult<AppLineProfileOptionDto[]>.Ok(
                    parsed != null && parsed.items != null ? parsed.items : new AppLineProfileOptionDto[0]));
            }
            catch (Exception ex)
            {
                onComplete?.Invoke(RequestResult<AppLineProfileOptionDto[]>.Fail("line_profiles_parse_failed:" + ex.Message));
            }
        }

        public IEnumerator ApplyWorkspace(string workspaceId, Action<RequestResult<AppActionResultDto>> onComplete)
        {
            yield return PostActionJson(
                "/api/app/workspace/apply",
                "{\"workspace_id\":\"" + EscapeJson(workspaceId) + "\"}",
                "apply_workspace",
                onComplete);
        }

        public IEnumerator SetCameraMode(string mode, Action<RequestResult<AppActionResultDto>> onComplete)
        {
            yield return PostActionJson(
                "/api/app/camera/mode",
                "{\"mode\":\"" + EscapeJson(mode) + "\"}",
                "set_camera_mode",
                onComplete);
        }

        public IEnumerator SetPhotoAwarenessPolicy(string policy, Action<RequestResult<AppActionResultDto>> onComplete)
        {
            yield return PostActionJson(
                "/api/app/awareness",
                "{\"policy\":\"" + EscapeJson(policy) + "\",\"enabled\":true}",
                "set_photo_awareness",
                onComplete);
        }

        public IEnumerator SetXrHandMode(string mode, Action<RequestResult<AppActionResultDto>> onComplete)
        {
            yield return PostActionJson(
                "/api/app/xrhand/mode",
                "{\"mode\":\"" + EscapeJson(mode) + "\"}",
                "set_xrhand_mode",
                onComplete);
        }

        private IEnumerator LoadText(string path, string label, Action<RequestResult<string>> onComplete)
        {
            if (!HasEndpoint)
            {
                onComplete?.Invoke(RequestResult<string>.Fail("app_api_url_empty"));
                yield break;
            }

            string url = appApiBaseUrl.TrimEnd('/') + path;
            using (var req = UnityWebRequest.Get(url))
            {
                ApplyAuth(req);
                yield return req.SendWebRequest();

                if (req.result != UnityWebRequest.Result.Success)
                {
                    onComplete?.Invoke(RequestResult<string>.Fail(req.error ?? (label + "_request_failed")));
                    yield break;
                }

                onComplete?.Invoke(RequestResult<string>.Ok(req.downloadHandler.text ?? ""));
            }
        }

        private IEnumerator PostActionJson(
            string path,
            string body,
            string label,
            Action<RequestResult<AppActionResultDto>> onComplete)
        {
            if (!HasEndpoint)
            {
                onComplete?.Invoke(RequestResult<AppActionResultDto>.Fail("app_api_url_empty"));
                yield break;
            }

            string url = appApiBaseUrl.TrimEnd('/') + path;
            using (var req = new UnityWebRequest(url, UnityWebRequest.kHttpVerbPOST))
            {
                byte[] bytes = System.Text.Encoding.UTF8.GetBytes(body ?? "{}");
                req.uploadHandler = new UploadHandlerRaw(bytes);
                req.downloadHandler = new DownloadHandlerBuffer();
                req.SetRequestHeader("Content-Type", "application/json");
                ApplyAuth(req);
                yield return req.SendWebRequest();

                if (req.result != UnityWebRequest.Result.Success)
                {
                    onComplete?.Invoke(RequestResult<AppActionResultDto>.Fail(req.error ?? (label + "_request_failed")));
                    yield break;
                }

                try
                {
                    var dto = JsonUtility.FromJson<AppActionResultDto>(req.downloadHandler.text ?? "{}");
                    if (dto == null)
                    {
                        onComplete?.Invoke(RequestResult<AppActionResultDto>.Fail(label + "_empty_response"));
                        yield break;
                    }
                    if (!dto.success)
                    {
                        string message = string.IsNullOrWhiteSpace(dto.message) ? "business_rejected" : dto.message;
                        onComplete?.Invoke(RequestResult<AppActionResultDto>.Fail(label + "_rejected:" + message));
                        yield break;
                    }
                    onComplete?.Invoke(RequestResult<AppActionResultDto>.Ok(dto));
                }
                catch (Exception ex)
                {
                    onComplete?.Invoke(RequestResult<AppActionResultDto>.Fail(label + "_parse_failed:" + ex.Message));
                }
            }
        }

        private void ApplyAuth(UnityWebRequest req)
        {
            if (!string.IsNullOrWhiteSpace(bearerSecret))
                req.SetRequestHeader("Authorization", "Bearer " + bearerSecret);
        }

        private static string EscapeJson(string value)
        {
            return (value ?? "")
                .Replace("\\", "\\\\")
                .Replace("\"", "\\\"");
        }
    }
}
