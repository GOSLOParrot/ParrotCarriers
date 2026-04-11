using System;
using System.Collections;
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
        if (!string.IsNullOrEmpty(joinToken))
            StartCoroutine(ConnectToRoom());
        else
            Debug.LogWarning("[RoomManager] No token. Paste one from generate_token.py into the Inspector.");
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
            Debug.LogError("[RoomManager] Connection failed");
            yield break;
        }

        Debug.Log($"[RoomManager] Connected — room='{Room.Name}' identity='{Room.LocalParticipant.Identity}'");
        IsConnected = true;
        OnConnected?.Invoke();
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
