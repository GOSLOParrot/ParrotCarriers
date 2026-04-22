using System;
using System.Collections;
using System.IO;
using UnityEngine;
using LiveKit;

/// <summary>
/// Manages LiveKit Room lifecycle: connect, audio playback, disconnect.
/// Singleton — persists across scenes via DontDestroyOnLoad.
///
/// Brain Agent finds Unity via identity prefix "unity" (_rpc_bridge.py).
/// </summary>
public class RoomManager : MonoBehaviour
{
    [Header("LiveKit Connection")]
    [Tooltip("LiveKit server URL. Local dev: ws://localhost:7880")]
    [SerializeField] private string serverUrl = "ws://localhost:7880";

    [Tooltip("JWT join token — generate with src/scripts/generate_token.py")]
    [SerializeField] private string joinToken = "";

    public Room Room { get; private set; }
    public bool IsConnected { get; private set; }
    public static RoomManager Instance { get; private set; }

    public event Action OnConnected;
    public event Action OnDisconnected;

    void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }
        Instance = this;
        DontDestroyOnLoad(gameObject);
    }

    void Start()
    {
        if (string.IsNullOrWhiteSpace(joinToken))
            TryLoadTokenFromParrotDevFile();

        if (!string.IsNullOrWhiteSpace(joinToken))
        {
            Debug.Log($"[RoomManager] Join token length={joinToken.Length}, connecting...");
            StartCoroutine(ConnectToRoom());
        }
        else
        {
            Debug.LogWarning(
                "[RoomManager] No token. Run: python src/scripts/generate_token.py "
                + "(writes unity/ParrotDev/unity_join_token.txt) or paste JWT into Inspector, then Save Scene.");
        }
    }

    /// <summary>
    /// Editor/本机联调：与 generate_token.py 默认输出路径一致，避免场景里忘保存空 token。
    /// Application.dataPath = .../ParrotDev/Assets → 上一级为 ParrotDev。
    /// </summary>
    private void TryLoadTokenFromParrotDevFile()
    {
        try
        {
            var path = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "unity_join_token.txt"));
            if (!File.Exists(path))
                return;

            var t = File.ReadAllText(path).Trim();
            if (string.IsNullOrEmpty(t))
                return;

            joinToken = t;
            Debug.Log($"[RoomManager] Loaded join token from file ({t.Length} chars): {path}");
        }
        catch (Exception e)
        {
            Debug.LogWarning($"[RoomManager] Could not read unity_join_token.txt: {e.Message}");
        }
    }

    /// <summary>Call at runtime to connect with a fresh token.</summary>
    public void Connect(string token, string url = null)
    {
        joinToken = token;
        if (!string.IsNullOrEmpty(url)) serverUrl = url;
        StartCoroutine(ConnectToRoom());
    }

    private IEnumerator ConnectToRoom()
    {
        Room = new Room();

        Room.TrackSubscribed += OnTrackSubscribed;
        Room.ParticipantConnected += p =>
            Debug.Log($"[RoomManager] + {p.Identity}");
        Room.ParticipantDisconnected += p =>
            Debug.Log($"[RoomManager] - {p.Identity}");
        Room.Disconnected += _ =>
        {
            Debug.Log("[RoomManager] Disconnected");
            IsConnected = false;
            OnDisconnected?.Invoke();
        };

        Debug.Log($"[RoomManager] Connecting to {serverUrl} ...");
        var connect = Room.Connect(serverUrl, joinToken, new RoomOptions());
        yield return connect;

        if (connect.IsError)
        {
            Debug.LogError(
                "[RoomManager] Connection failed (check: Docker LiveKit on :7880, token not expired, Brain worker registered). "
                + "Regenerate: python src/scripts/generate_token.py");
            yield break;
        }

        Debug.Log($"[RoomManager] Connected — room='{Room.Name}' identity='{Room.LocalParticipant.Identity}'");
        IsConnected = true;
        OnConnected?.Invoke();

        // Sprint 3 S3.D4: trigger GOSLO greeting after 500ms (gives Brain time to start session)
        StartCoroutine(TriggerGreetingAfterDelay(0.5f));
    }

    private IEnumerator TriggerGreetingAfterDelay(float delaySeconds)
    {
        yield return new WaitForSeconds(delaySeconds);

        string brainId = null;
        foreach (var id in Room.RemoteParticipants.Keys)
        {
            if (!id.StartsWith("unity", StringComparison.OrdinalIgnoreCase))
            { brainId = id; break; }
        }
        if (brainId == null)
        {
            Debug.Log("[RoomManager] Greeting skipped — Brain not yet in room");
            yield break;
        }

        // Determine time-of-day greeting hint
        int hour = DateTime.Now.Hour;
        string timeHint = hour < 12 ? "morning" : hour < 18 ? "afternoon" : "evening";
        string payload = $"{{\"event\":\"scene_ready\",\"time_of_day\":\"{timeHint}\"}}";

        try
        {
            var rpc = Room.LocalParticipant.PerformRpc(
                destinationIdentity: brainId,
                method: "onSceneReady",
                payload: payload,
                responseTimeout: 5.0f
            );
            yield return new WaitUntil(() => rpc.IsCompleted);
            Debug.Log($"[RoomManager] onSceneReady sent (time_of_day={timeHint})");
        }
        catch (Exception e)
        {
            Debug.LogWarning($"[RoomManager] onSceneReady RPC failed: {e.Message}");
        }

    private void OnTrackSubscribed(
        IRemoteTrack track,
        RemoteTrackPublication publication,
        RemoteParticipant participant)
    {
        if (track is RemoteAudioTrack audioTrack)
        {
            Debug.Log($"[RoomManager] Audio track from {participant.Identity}");
            var go = new GameObject($"Audio_{participant.Identity}");
            go.transform.SetParent(transform);
            var source = go.AddComponent<AudioSource>();
            source.spatialBlend = 0f;
            var stream = new AudioStream(audioTrack, source);
        }
    }

    void OnDestroy()
    {
        Room?.Disconnect();
        Room = null;
        if (Instance == this) Instance = null;
    }
}
