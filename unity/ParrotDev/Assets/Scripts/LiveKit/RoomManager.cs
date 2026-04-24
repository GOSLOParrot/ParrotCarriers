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
///
/// <b>Scope note (product vs test):</b> this class proves <b>room connectivity</b> and carries
/// <see cref="LastConnectDurationSeconds"/> / test-only disconnect helpers — it is <b>not</b> the
/// specification for the full AR App <b>cold-start → token → UX → AR scene</b> flow (that flow is
/// still split across Launcher/Dev and not yet designed as one product story). Do not treat
/// connectivity smoke tests as the architectural baseline for final launch behaviour.
///
/// <b>Channels (do not conflate):</b> LiveKit <b>room + RPC + DataChannel</b> here are the
/// <b>control / supplemental signalling plane</b> for Sprint 3 bus tests. The <b>camera pixel
/// track</b> to Gemini is owned by <see cref="ARVideoPublisher"/> (device / XR Sim / WebCam
/// harness — see that class for “supplemental probe vs product-quality capture”). Sprint 4
/// reports must keep those conclusions separate.
/// </summary>
public class RoomManager : MonoBehaviour
{
    [Header("LiveKit Connection")]
    [Tooltip("LiveKit server URL. Local dev: ws://localhost:7880")]
    [SerializeField] private string serverUrl = "ws://localhost:7880";

    [Tooltip("JWT join token — generate with src/scripts/generate_token.py")]
    [SerializeField] private string joinToken = "";

    [Tooltip(
        "Auto-connect on Start() using the inspector/file token.\n" +
        "Set to FALSE in Launcher scene — LauncherUI will call Connect() after fetching a fresh token.\n" +
        "Leave TRUE in Dev.unity so the scene connects immediately for dev iteration.")]
    [SerializeField] private bool autoConnectOnStart = true;

    public Room Room { get; private set; }
    public bool IsConnected { get; private set; }
    public static RoomManager Instance { get; private set; }

    /// <summary>Seconds for the last successful <see cref="ConnectToRoom"/> (for Testing/HUD).</summary>
    public float? LastConnectDurationSeconds { get; private set; }

    public event Action OnConnected;
    public event Action OnDisconnected;

    void Awake()
    {
        if (Instance != null && Instance != this)
        {
            // Launcher keeps the connected RoomManager across scene load. In Dev.unity the
            // LiveKitManager object also hosts publishers/reporters; destroy only this
            // duplicate component so those scene-local components can bind to Instance.
            Destroy(this);
            return;
        }
        Instance = this;
        DontDestroyOnLoad(gameObject);
    }

    void Start()
    {
        if (!autoConnectOnStart)
        {
            Debug.Log("[RoomManager] autoConnectOnStart=false — waiting for LauncherUI.Connect()");
            return;
        }

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

    /// <summary>Test harness: leave room without destroying this component. Uses cached token on reconnect.</summary>
    public void DisconnectForTesting()
    {
        if (Room == null)
        {
            Debug.Log("[RoomManager] DisconnectForTesting: no active Room");
            return;
        }

        try
        {
            Debug.Log("[RoomManager] DisconnectForTesting");
            Room.Disconnect();
        }
        catch (Exception e)
        {
            Debug.LogWarning($"[RoomManager] DisconnectForTesting: {e.Message}");
        }
    }

    /// <summary>Reconnect using the current <c>joinToken</c> (Inspector or last <see cref="Connect"/>).</summary>
    public void ReconnectUsingCachedCredentials()
    {
        if (string.IsNullOrWhiteSpace(joinToken))
        {
            Debug.LogWarning(
                "[RoomManager] Reconnect skipped — no joinToken. Paste in Inspector or place unity_join_token.txt.");
            return;
        }

        StartCoroutine(ConnectToRoom());
    }

#if UNITY_EDITOR
    /// <summary>Editor menu: disconnect then reconnect after delay (data-flow / resilience smoke test).</summary>
    public void StartEditorReconnectTest(float delaySeconds = 1f)
    {
        StartCoroutine(EditorReconnectAfterDelay(delaySeconds));
    }

    private IEnumerator EditorReconnectAfterDelay(float delaySeconds)
    {
        DisconnectForTesting();
        yield return new WaitForSecondsRealtime(delaySeconds);
        ReconnectUsingCachedCredentials();
    }
#endif

    private IEnumerator ConnectToRoom()
    {
        var t0 = Time.realtimeSinceStartup;
        LastConnectDurationSeconds = null;

        if (Room != null)
        {
            Debug.Log("[RoomManager] Replacing existing Room (disconnect previous)");
            try
            {
                Room.Disconnect();
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[RoomManager] Disconnect previous room: {e.Message}");
            }

            Room = null;
            IsConnected = false;
            yield return null;
        }

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
            LastConnectDurationSeconds = null;
            yield break;
        }

        LastConnectDurationSeconds = Time.realtimeSinceStartup - t0;
        Debug.Log(
            $"[RoomManager] Connected — room='{Room.Name}' identity='{Room.LocalParticipant.Identity}' "
            + $"(connect {LastConnectDurationSeconds:F2}s)");
        IsConnected = true;
        OnConnected?.Invoke();

        // Sprint 3 S3.D4: trigger GOSLO greeting after 500ms (gives Brain time to start session)
        StartCoroutine(TriggerGreetingAfterDelay(0.5f));
    }

    private IEnumerator TriggerGreetingAfterDelay(float delaySeconds)
    {
        yield return new WaitForSeconds(delaySeconds);

        string brainId = BrainParticipantResolver.FindBrainParticipantId(Room);
        if (string.IsNullOrEmpty(brainId))
        {
            Debug.Log("[RoomManager] onSceneReady skipped — Brain not yet in room");
            yield break;
        }

        int hour = DateTime.Now.Hour;
        string timeHint = hour < 12 ? "morning" : hour < 18 ? "afternoon" : "evening";
        string payload = $"{{\"event\":\"scene_ready\",\"time_of_day\":\"{timeHint}\"}}";

        var rpcCall = Room.LocalParticipant.PerformRpc(new PerformRpcParams
        {
            DestinationIdentity = brainId,
            Method = "onSceneReady",
            Payload = payload,
            ResponseTimeout = 5000,
        });
        yield return rpcCall;

        if (rpcCall.IsError)
            Debug.LogWarning($"[RoomManager] onSceneReady error: {rpcCall.Error?.Message}");
        else
            Debug.Log($"[RoomManager] onSceneReady sent (time_of_day={timeHint})");
    }   // end TriggerGreetingAfterDelay

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
