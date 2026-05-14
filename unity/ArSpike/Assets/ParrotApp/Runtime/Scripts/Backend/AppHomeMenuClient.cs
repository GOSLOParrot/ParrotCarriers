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
        public string workspace_id = "";
        public string display_name = "";
        public string kind = "";
        public bool enabled = true;
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
    }

    [Serializable]
    public class AppAssetManifestDto
    {
        public int schema_version;
    }

    /// <summary>
    /// App HTTP client for the formal home/menu read model.
    ///
    /// Durable menu and canvas snapshots belong to the App HTTP facade. LiveKit
    /// RPC/ECP stays for compact in-room control and status messages, not for
    /// the full canvas payload.
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

        private void ApplyAuth(UnityWebRequest req)
        {
            if (!string.IsNullOrWhiteSpace(bearerSecret))
                req.SetRequestHeader("Authorization", "Bearer " + bearerSecret);
        }
    }
}
