using System;
using System.Collections;
using System.IO;
using UnityEngine;

/// <summary>
/// Sprint 3 T-U2: Reads the scene profile config and initialises the correct
/// AR/webcam mode. Sends <c>setScene</c> RPC to Brain so Brain can write
/// session/scene to Blackboard.
///
/// Profile selection (automatic):
///   AR_HANDHELD   — running on Android with ARCore available (UNITY_ANDROID + XR session)
///   DESKTOP_WEBCAM — Unity Editor or any non-AR platform (dev path)
///
/// Config override: Resources/parrot_config.json can contain
///   "scene": "AR_HANDHELD" | "DESKTOP_WEBCAM"
/// to force a profile regardless of platform detection.
///
/// The SceneProfileManager must be in the scene BEFORE RoomManager connects
/// so it can inject the correct setScene RPC right after connection.
/// </summary>
public class SceneProfileManager : MonoBehaviour
{
    public enum SceneProfile { DESKTOP_WEBCAM, AR_HANDHELD }

    public static SceneProfileManager Instance { get; private set; }
    public SceneProfile ActiveProfile { get; private set; }

    [Header("Debug Override")]
    [Tooltip("Force a specific scene profile regardless of platform detection. Leave None for auto.")]
    [SerializeField] private SceneProfile? _forceProfile = null;
    [SerializeField] private bool _forceProfileEnabled = false;

    [Serializable]
    private class ProfileConfig
    {
        public string scene = "";
    }

    void Awake()
    {
        if (Instance != null && Instance != this) { Destroy(gameObject); return; }
        Instance = this;
        DontDestroyOnLoad(gameObject);

        ActiveProfile = DetermineProfile();
        Debug.Log($"[SceneProfileManager] Active profile: {ActiveProfile}");
    }

    void Start()
    {
        var rm = RoomManager.Instance;
        if (rm == null)
        {
            Debug.LogWarning("[SceneProfileManager] RoomManager not found — setScene RPC will be deferred");
            return;
        }
        rm.OnConnected += OnRoomConnected;
        if (rm.IsConnected) OnRoomConnected();
    }

    private void OnRoomConnected()
    {
        // Notify Brain which scene we are in
        SendSetSceneRpc(ActiveProfile);
    }

    private SceneProfile DetermineProfile()
    {
        // Inspector force override
        if (_forceProfileEnabled)
            return _forceProfile ?? SceneProfile.DESKTOP_WEBCAM;

        // Config file override
        var configAsset = Resources.Load<TextAsset>("parrot_config");
        if (configAsset != null)
        {
            try
            {
                var cfg = JsonUtility.FromJson<ProfileConfig>(configAsset.text);
                if (!string.IsNullOrEmpty(cfg.scene))
                {
                    if (Enum.TryParse<SceneProfile>(cfg.scene, true, out var parsed))
                    {
                        Debug.Log($"[SceneProfileManager] Config override → {parsed}");
                        return parsed;
                    }
                }
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[SceneProfileManager] Config parse error: {e.Message}");
            }
        }

#if UNITY_ANDROID && !UNITY_EDITOR
        // On Android device — check if AR Foundation XR session is available
        if (IsARAvailable())
            return SceneProfile.AR_HANDHELD;
#endif

        // Editor or non-AR platform → webcam fallback path
        return SceneProfile.DESKTOP_WEBCAM;
    }

    private bool IsARAvailable()
    {
#if UNITY_AR_FOUNDATION
        // Check ARSession state; if it can be started, AR is available
        try
        {
            var state = UnityEngine.XR.ARFoundation.ARSession.state;
            return state != UnityEngine.XR.ARFoundation.ARSessionState.Unsupported &&
                   state != UnityEngine.XR.ARFoundation.ARSessionState.None;
        }
        catch
        {
            return false;
        }
#else
        return false;
#endif
    }

    private void SendSetSceneRpc(SceneProfile profile)
    {
        StartCoroutine(SendSetSceneRpcCoroutine(profile));
    }

    private IEnumerator SendSetSceneRpcCoroutine(SceneProfile profile)
    {
        var room = RoomManager.Instance?.Room;
        if (room == null) yield break;

        // Brain identity prefix matches agentIdentityPrefix in VideoStateReporter
        string brainIdentity = FindBrainIdentity(room);
        if (string.IsNullOrEmpty(brainIdentity))
        {
            Debug.LogWarning("[SceneProfileManager] Brain participant not found — setScene deferred");
            yield break;
        }

        string sceneName = profile == SceneProfile.AR_HANDHELD ? "ar_handheld" : "desktop_webcam";
        string payload = $"{{\"scene\":\"{sceneName}\"}}";

        var rpcCall = room.LocalParticipant.PerformRpc(new PerformRpcParams
        {
            DestinationIdentity = brainIdentity,
            Method = "setScene",
            Payload = payload,
            ResponseTimeout = 5000, // milliseconds
        });
        yield return rpcCall;

        if (rpcCall.IsError)
            Debug.LogWarning($"[SceneProfileManager] setScene RPC error: {rpcCall.Error?.Message}");
        else
            Debug.Log($"[SceneProfileManager] setScene → {sceneName}: ok");
    }

    private static string FindBrainIdentity(Room room)
    {
        foreach (var p in room.RemoteParticipants.Values)
        {
            if (!string.IsNullOrEmpty(p.Identity) && p.Identity.StartsWith("agent-"))
                return p.Identity;
        }
        return null;
    }

    void OnDestroy()
    {
        var rm = RoomManager.Instance;
        if (rm != null) rm.OnConnected -= OnRoomConnected;
    }
}
