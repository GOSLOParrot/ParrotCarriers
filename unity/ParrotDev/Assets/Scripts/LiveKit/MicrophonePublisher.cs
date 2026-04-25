using System.Collections;
using UnityEngine;
using LiveKit;
using LiveKit.Proto;

/// <summary>
/// 将本机麦克风编码为 LiveKit <b>本地音频轨</b>（与 <see cref="ARVideoPublisher"/> 的视频轨独立）。<br/>
/// <b>与「没视频能不能对话」的关系</b>：房间连上只保证信令面；<b>语音对话</b>需要本轨发布成功
/// <b>且</b> 房间内存在订阅该轨的 Brain / Agent。Brain 未进房时，本脚本仍会发布，但对端无人收听。<br/>
/// 权限：Android 上与 <see cref="LauncherUI"/> 的 Permission 请求可并存；本脚本仍调用
/// <see cref="Application.RequestUserAuthorization"/> 作为兜底。<br/>
/// 挂载：与 <see cref="RoomManager"/> 同物体或任意在连接后仍激活的物体；Launcher→Dev 时发布器在 Dev 的 LiveKitManager 上、
/// <see cref="RoomManager"/> 在 LauncherRoot 上的组合为当前工程预期布局。
/// </summary>
public class MicrophonePublisher : MonoBehaviour
{
    [Tooltip("Leave empty to use the system default microphone")]
    [SerializeField] private string preferredDevice = "";

    private MicrophoneSource _micSource;
    private LocalAudioTrack _audioTrack;
    private bool _isPublishing;
    private bool _publishInProgress;
    private bool _publishAttempted;
    private string _selectedDevice = "";
    private string _lastError = "";

    /// <summary>麦克风轨已成功 <c>PublishTrack</c> 后为 true（供 HUD / 自检）。</summary>
    public bool IsPublishing => _isPublishing;
    public bool PublishAttempted => _publishAttempted;
    public string SelectedDevice => _selectedDevice;
    public string LastError => _lastError;

    void Start()
    {
        var rm = RoomManager.Instance;
        if (rm == null)
        {
            Debug.LogWarning("[MicrophonePublisher] RoomManager not found");
            return;
        }

        rm.OnConnected += OnRoomConnected;
        rm.OnDisconnected += OnRoomDisconnected;
        if (rm.IsConnected) OnRoomConnected();
    }

    private void OnRoomConnected()
    {
        if (_isPublishing || _publishInProgress) return;
        StartCoroutine(RequestAndPublish());
    }

    private IEnumerator RequestAndPublish()
    {
        _publishInProgress = true;
        _publishAttempted = true;
        _lastError = "";

        yield return Application.RequestUserAuthorization(UserAuthorization.Microphone);

        if (!Application.HasUserAuthorization(UserAuthorization.Microphone))
        {
            _lastError = "permission_denied";
            Debug.LogError("[MicrophonePublisher] ERROR permission_denied: Microphone permission denied");
            _publishInProgress = false;
            yield break;
        }

        if (Microphone.devices.Length == 0)
        {
            _lastError = "no_microphone_devices";
            Debug.LogWarning("[MicrophonePublisher] ERROR no_microphone_devices: No microphone devices found");
            _publishInProgress = false;
            yield break;
        }

        string device = SelectDevice();
        _selectedDevice = device;

        Debug.Log($"[MicrophonePublisher] Using device: {device}");

        var room = RoomManager.Instance?.Room;
        if (room == null)
        {
            _lastError = "room_missing_after_permission";
            Debug.LogWarning("[MicrophonePublisher] ERROR room_missing_after_permission: Room disappeared before audio publish");
            _publishInProgress = false;
            yield break;
        }

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
            _lastError = $"publish_failed:{publish.Error?.Message}";
            Debug.LogError($"[MicrophonePublisher] ERROR publish_failed: Failed to publish audio track ({publish.Error?.Code} {publish.Error?.Message})");
            _publishInProgress = false;
            yield break;
        }

        _micSource.Start();
        _isPublishing = true;
        _publishInProgress = false;
        Debug.Log($"[MicrophonePublisher] Microphone publishing started: {device}");
    }

    private string SelectDevice()
    {
        if (!string.IsNullOrEmpty(preferredDevice))
        {
            foreach (var device in Microphone.devices)
            {
                if (device == preferredDevice)
                    return device;
            }

            Debug.LogWarning(
                $"[MicrophonePublisher] preferredDevice '{preferredDevice}' not found; using default '{Microphone.devices[0]}'");
        }

        return Microphone.devices[0];
    }

    private void OnRoomDisconnected()
    {
        StopPublishing("room_disconnected");
    }

    private void StopPublishing(string reason)
    {
        if (!_isPublishing && _micSource == null && _audioTrack == null)
            return;

        _isPublishing = false;
        _publishInProgress = false;
        try { _micSource?.Stop(); }
        catch (System.Exception e) { Debug.LogWarning($"[MicrophonePublisher] Stop microphone failed ({reason}): {e.Message}"); }
        _micSource = null;
        _audioTrack = null;
        Debug.Log($"[MicrophonePublisher] Microphone publishing stopped ({reason})");
    }

    void OnDestroy()
    {
        StopPublishing("destroy");

        var rm = RoomManager.Instance;
        if (rm != null)
        {
            rm.OnConnected -= OnRoomConnected;
            rm.OnDisconnected -= OnRoomDisconnected;
        }
    }
}
