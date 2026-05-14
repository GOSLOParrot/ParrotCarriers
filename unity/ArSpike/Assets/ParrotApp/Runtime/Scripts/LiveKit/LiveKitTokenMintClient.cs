using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

namespace ParrotApp.LiveKit
{
    /// <summary>
    /// Minimal client for the existing Castle token mint service
    /// (src/parrot/castle/token_mint.py).
    /// </summary>
    public class LiveKitTokenMintClient : MonoBehaviour
    {
        [Tooltip("Token mint endpoint, e.g. http://127.0.0.1:7888/mint")]
        [SerializeField] private string mintEndpoint = "http://127.0.0.1:7888/mint";

        [Tooltip("Optional PARROT_MINT_SECRET. Empty means dev-mode open mint.")]
        [SerializeField] private string bearerSecret = "";

        [Serializable]
        private class RuntimeConfigDto
        {
            public string mintUrl = "";
            public string mintSecret = "";
            public string liveKitUrl = "";
            public string room = "";
        }

        [Serializable]
        private class MintRequestDto
        {
            public string room;
            public string identity;
        }

        [Serializable]
        public class MintResponseDto
        {
            public string token = "";
            public string url = "";
            public long expires_at;
        }

        public struct MintResult
        {
            public bool Ok;
            public MintResponseDto Response;
            public string Error;

            public MintResult(bool ok, MintResponseDto response, string error)
            {
                Ok = ok;
                Response = response;
                Error = error ?? "";
            }
        }

        public string MintEndpoint
        {
            get => mintEndpoint;
            set => mintEndpoint = value ?? "";
        }

        public string BearerSecret
        {
            get => bearerSecret;
            set => bearerSecret = value ?? "";
        }

        private void Awake()
        {
            LoadRuntimeConfig();
        }

        private void LoadRuntimeConfig()
        {
            // Shared D3 runtime config: gitignored Resources/parrot_config.json.
            // The file may also include liveKitUrl/room for ParrotDev compatibility;
            // this client only owns mint endpoint and bearer auth.
            var asset = Resources.Load<TextAsset>("parrot_config");
            if (asset == null)
                return;

            try
            {
                var config = JsonUtility.FromJson<RuntimeConfigDto>(asset.text);
                if (config == null)
                    return;

                if (!string.IsNullOrWhiteSpace(config.mintUrl))
                    mintEndpoint = NormalizeMintEndpoint(config.mintUrl);
                if (!string.IsNullOrWhiteSpace(config.mintSecret))
                    bearerSecret = config.mintSecret;

                Debug.Log("[TokenMint] loaded parrot_config from Resources");
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[TokenMint] failed to parse parrot_config: {ex.Message}");
            }
        }

        public IEnumerator Mint(string roomId, string identity, Action<MintResult> onComplete)
        {
            if (string.IsNullOrWhiteSpace(mintEndpoint))
            {
                onComplete?.Invoke(new MintResult(false, null, "mint_endpoint_empty"));
                yield break;
            }

            // Token mint is the security boundary. Unity never receives the
            // LiveKit API secret; it asks the backend for a short-lived room
            // token bound to this room and participant identity.
            var body = JsonUtility.ToJson(new MintRequestDto
            {
                room = string.IsNullOrWhiteSpace(roomId) ? "parrot-main" : roomId,
                identity = string.IsNullOrWhiteSpace(identity) ? "unity-app" : identity,
            });
            var bytes = Encoding.UTF8.GetBytes(body);

            using (var req = new UnityWebRequest(mintEndpoint, UnityWebRequest.kHttpVerbPOST))
            {
                req.uploadHandler = new UploadHandlerRaw(bytes);
                req.downloadHandler = new DownloadHandlerBuffer();
                req.SetRequestHeader("Content-Type", "application/json");
                if (!string.IsNullOrWhiteSpace(bearerSecret))
                    req.SetRequestHeader("Authorization", $"Bearer {bearerSecret}");
                else if (!mintEndpoint.StartsWith("http://127.0.0.1", StringComparison.OrdinalIgnoreCase)
                         && !mintEndpoint.StartsWith("http://localhost", StringComparison.OrdinalIgnoreCase))
                    Debug.LogWarning("[TokenMint] no bearer secret configured for a non-local endpoint");

                yield return req.SendWebRequest();

                if (req.result != UnityWebRequest.Result.Success)
                {
                    onComplete?.Invoke(new MintResult(false, null, req.error ?? "request_failed"));
                    yield break;
                }

                try
                {
                    var response = JsonUtility.FromJson<MintResponseDto>(req.downloadHandler.text);
                    if (response == null || string.IsNullOrWhiteSpace(response.token))
                    {
                        onComplete?.Invoke(new MintResult(false, response, "token_missing"));
                        yield break;
                    }
                    onComplete?.Invoke(new MintResult(true, response, ""));
                }
                catch (Exception ex)
                {
                    onComplete?.Invoke(new MintResult(false, null, $"parse_failed:{ex.Message}"));
                }
            }
        }

        private static string NormalizeMintEndpoint(string value)
        {
            string endpoint = (value ?? "").Trim();
            if (endpoint.Length == 0)
                return endpoint;

            endpoint = endpoint.TrimEnd('/');
            // Castle exposes token mint at /mint. The phone config sometimes
            // stores only the service root (:7888); normalize that root so the
            // formal App and quick scripts exercise the same endpoint.
            if (endpoint.EndsWith("/mint", StringComparison.OrdinalIgnoreCase))
                return endpoint;
            return endpoint + "/mint";
        }
    }
}
