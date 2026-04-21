using System.Collections;
using UnityEngine;
using LiveKit;
using LiveKit.Proto;

/// <summary>
/// Publishes local microphone audio to LiveKit so Brain Agent / Gemini Live can hear the user.
/// Attach to the same GameObject as RoomManager (or any persistent GameObject).
/// Requires microphone permission — on Editor this is granted automatically.
/// </summary>
public class MicrophonePublisher : MonoBehaviour
{
    [Tooltip("Leave empty to use the system default microphone")]
    [SerializeField] private string preferredDevice = "";

    private MicrophoneSource _micSource;
    private LocalAudioTrack _audioTrack;
    private bool _isPublishing;

    void Start()
    {
        var rm = RoomManager.Instance;
        if (rm == null)
        {
            Debug.LogWarning("[MicrophonePublisher] RoomManager not found");
            return;
        }

        rm.OnConnected += OnRoomConnected;
        if (rm.IsConnected) OnRoomConnected();
    }

    private void OnRoomConnected()
    {
        if (_isPublishing) return;
        StartCoroutine(RequestAndPublish());
    }

    private IEnumerator RequestAndPublish()
    {
        yield return Application.RequestUserAuthorization(UserAuthorization.Microphone);

        if (!Application.HasUserAuthorization(UserAuthorization.Microphone))
        {
            Debug.LogError("[MicrophonePublisher] Microphone permission denied");
            yield break;
        }

        if (Microphone.devices.Length == 0)
        {
            Debug.LogWarning("[MicrophonePublisher] No microphone devices found");
            yield break;
        }

        string device = string.IsNullOrEmpty(preferredDevice)
            ? Microphone.devices[0]
            : preferredDevice;

        Debug.Log($"[MicrophonePublisher] Using device: {device}");

        var room = RoomManager.Instance?.Room;
        if (room == null) yield break;

        _micSource = new MicrophoneSource(device, gameObject);
        _audioTrack = LocalAudioTrack.CreateAudioTrack("microphone", _micSource, room);

        var options = new TrackPublishOptions
        {
            Source = TrackSource.SourceMicrophone,
            AudioEncoding = new AudioEncoding
            {
                MaxBitrate = 64_000,
            },
        };

        var publish = room.LocalParticipant.PublishTrack(_audioTrack, options);
        yield return publish;

        if (publish.IsError)
        {
            Debug.LogError("[MicrophonePublisher] Failed to publish audio track");
            yield break;
        }

        _micSource.Start();
        _isPublishing = true;
        Debug.Log($"[MicrophonePublisher] Microphone publishing started: {device}");
    }

    void OnDestroy()
    {
        _isPublishing = false;

        try { _micSource?.Stop(); }
        catch (System.Exception) { /* SDK MonoBehaviourContext may already be destroyed on scene unload */ }

        var rm = RoomManager.Instance;
        if (rm != null) rm.OnConnected -= OnRoomConnected;
    }
}
