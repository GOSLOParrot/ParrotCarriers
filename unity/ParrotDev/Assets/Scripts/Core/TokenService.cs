using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

/// <summary>
/// Sprint 3 T-P4: Fetches a LiveKit room token from the Castle Token Mint service.
///
/// Flow:
///   1. POST /mint with Bearer PARROT_MINT_SECRET → receive JWT token + LiveKit URL
///   2. Cache token in PlayerPrefs for 24h (TTL from server expires_at field)
///   3. On failure / expired → fall back to Resources/parrotdev.json
///      (UnityWebRequest to StreamingAssets is not used here — keep fallback
///      as a Resources TextAsset named "parrotdev" so Editor + device behave the same.)
///
/// Config source (D3 decision): Resources/parrot_config.json (compiled into APK,
/// gitignored). Contains { "mintUrl": "...", "mintSecret": "...", "liveKitUrl": "..." }.
/// </summary>
public class TokenService : MonoBehaviour
{
    private const string PREFS_TOKEN_KEY = "parrot_livekit_token";
    private const string PREFS_EXPIRES_KEY = "parrot_token_expires_at";
    private const string PREFS_LIVEKIT_URL_KEY = "parrot_livekit_url";
    private const string FALLBACK_ASSET = "parrotdev";

    [Serializable]
    private class MintConfig
    {
        public string mintUrl = "";
        public string mintSecret = "";
        public string liveKitUrl = "";
        public string room = "parrot-main";
    }

    [Serializable]
    private class MintRequest
    {
        public string room;
        public string identity;
    }

    [Serializable]
    private class MintResponse
    {
        public string token;
        public string url;
        public long expires_at;
    }

    [Serializable]
    private class FallbackConfig
    {
        public string token;
        public string url;
    }

    public static TokenService Instance { get; private set; }

    private MintConfig _config;

    public string LiveKitToken { get; private set; }
    public string LiveKitUrl { get; private set; }
    public bool IsReady { get; private set; }

    void Awake()
    {
        if (Instance != null && Instance != this) { Destroy(gameObject); return; }
        Instance = this;
        DontDestroyOnLoad(gameObject);
        LoadConfig();
    }

    private void LoadConfig()
    {
        var asset = Resources.Load<TextAsset>("parrot_config");
        if (asset != null)
        {
            try
            {
                _config = JsonUtility.FromJson<MintConfig>(asset.text);
                Debug.Log("[TokenService] Loaded parrot_config from Resources");
                return;
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[TokenService] Failed to parse parrot_config: {e.Message}");
            }
        }
        _config = new MintConfig();
        Debug.LogWarning("[TokenService] parrot_config.json not found in Resources — using defaults");
    }

    /// <summary>
    /// Fetch a fresh token (or use cached). Call before connecting to LiveKit.
    /// Invokes <paramref name="onDone"/> with success=true on any valid token.
    /// </summary>
    public void FetchToken(string deviceId, Action<bool> onDone)
    {
        StartCoroutine(FetchTokenCoroutine(deviceId, onDone));
    }

    private IEnumerator FetchTokenCoroutine(string deviceId, Action<bool> onDone)
    {
        // Check cached token (valid for 24h minus 5 min buffer)
        var cachedToken = PlayerPrefs.GetString(PREFS_TOKEN_KEY, "");
        var expiresAt = PlayerPrefs.GetInt(PREFS_EXPIRES_KEY, 0);
        var cachedUrl = PlayerPrefs.GetString(PREFS_LIVEKIT_URL_KEY, "");

        if (!string.IsNullOrEmpty(cachedToken) && expiresAt > DateTimeOffset.UtcNow.ToUnixTimeSeconds() + 300)
        {
            Debug.Log("[TokenService] Using cached token (not expired)");
            LiveKitToken = cachedToken;
            LiveKitUrl = cachedUrl;
            IsReady = true;
            onDone?.Invoke(true);
            yield break;
        }

        if (string.IsNullOrEmpty(_config.mintUrl))
        {
            Debug.LogWarning("[TokenService] mintUrl not configured — falling back to StreamingAssets");
            yield return LoadFallback(onDone);
            yield break;
        }

        // Build mint request
        string identity = $"unity-{deviceId}";
        var requestBody = JsonUtility.ToJson(new MintRequest { room = _config.room, identity = identity });
        var bodyBytes = Encoding.UTF8.GetBytes(requestBody);

        using var req = new UnityWebRequest(_config.mintUrl, "POST")
        {
            uploadHandler = new UploadHandlerRaw(bodyBytes),
            downloadHandler = new DownloadHandlerBuffer(),
        };
        req.SetRequestHeader("Content-Type", "application/json");
        if (!string.IsNullOrEmpty(_config.mintSecret))
            req.SetRequestHeader("Authorization", $"Bearer {_config.mintSecret}");

        Debug.Log($"[TokenService] Requesting token from {_config.mintUrl} (identity={identity})");
        yield return req.SendWebRequest();

        if (req.result != UnityWebRequest.Result.Success)
        {
            Debug.LogWarning($"[TokenService] Mint request failed ({req.responseCode}): {req.error} — falling back");
            yield return LoadFallback(onDone);
            yield break;
        }

        // C# prohibits `yield return` inside a catch clause (CS1631).
        // Parse in a local scope; record failure, then yield outside the catch.
        MintResponse resp = default;
        string parseError = null;
        try
        {
            resp = JsonUtility.FromJson<MintResponse>(req.downloadHandler.text);
        }
        catch (Exception e)
        {
            parseError = e.Message;
        }
        if (parseError != null)
        {
            Debug.LogWarning($"[TokenService] Failed to parse mint response: {parseError} — falling back");
            yield return LoadFallback(onDone);
            yield break;
        }

        if (string.IsNullOrEmpty(resp.token))
        {
            Debug.LogWarning("[TokenService] Mint response has empty token — falling back");
            yield return LoadFallback(onDone);
            yield break;
        }

        // Cache to PlayerPrefs
        PlayerPrefs.SetString(PREFS_TOKEN_KEY, resp.token);
        PlayerPrefs.SetInt(PREFS_EXPIRES_KEY, (int)resp.expires_at);
        PlayerPrefs.SetString(PREFS_LIVEKIT_URL_KEY, resp.url);
        PlayerPrefs.Save();

        LiveKitToken = resp.token;
        LiveKitUrl = string.IsNullOrEmpty(resp.url) ? _config.liveKitUrl : resp.url;
        IsReady = true;
        Debug.Log($"[TokenService] Token minted and cached (expires_at={resp.expires_at})");
        onDone?.Invoke(true);
    }

    private IEnumerator LoadFallback(Action<bool> onDone)
    {
        var asset = Resources.Load<TextAsset>(FALLBACK_ASSET);
        if (asset != null)
        {
            try
            {
                var fb = JsonUtility.FromJson<FallbackConfig>(asset.text);
                LiveKitToken = fb.token;
                LiveKitUrl = fb.url;
                IsReady = true;
                Debug.Log("[TokenService] Using fallback token from Resources (parrotdev)");
                onDone?.Invoke(true);
                yield break;
            }
            catch (Exception e)
            {
                Debug.LogError($"[TokenService] Fallback parse error: {e.Message}");
            }
        }

        Debug.LogError("[TokenService] No token available — check parrot_config or parrotdev.json");
        IsReady = false;
        onDone?.Invoke(false);
    }

    /// <summary>Invalidate cached token (call after auth failure).</summary>
    public void ClearCache()
    {
        PlayerPrefs.DeleteKey(PREFS_TOKEN_KEY);
        PlayerPrefs.DeleteKey(PREFS_EXPIRES_KEY);
        PlayerPrefs.DeleteKey(PREFS_LIVEKIT_URL_KEY);
        PlayerPrefs.Save();
        LiveKitToken = null;
        LiveKitUrl = null;
        IsReady = false;
    }
}
