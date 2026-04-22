using System;
using System.Collections;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

#if UNITY_ANDROID && !UNITY_EDITOR
using UnityEngine.Android;
#endif

/// <summary>
/// Sprint 3 T-U3: Launcher scene controller.
///
/// Flow:
///   1. On Start: request Android runtime permissions (CAMERA, RECORD_AUDIO, INTERNET)
///   2. User taps Connect: validate permissions → fetch LiveKit token (TokenService)
///      → connect RoomManager → load AR scene
///   3. Permission denied: show warning + retry button; do NOT enter AR scene
///
/// Attach to a Canvas GameObject in the Launcher scene.
/// Wire up the serialized fields in Inspector.
/// </summary>
public class LauncherUI : MonoBehaviour
{
    [Header("UI Elements")]
    [SerializeField] private Button connectButton;
    [SerializeField] private Text statusText;
    [SerializeField] private GameObject permissionWarningPanel;
    [SerializeField] private Text permissionWarningText;
    [SerializeField] private Button retryPermissionButton;

    [Header("Scene")]
    [Tooltip("Name of the AR/main scene to load after successful connection")]
    [SerializeField] private string mainSceneName = "Dev";

    [Header("Debug")]
    [SerializeField] private bool skipPermissionsInEditor = true;

    private bool _cameraPermitted;
    private bool _audioPermitted;
    private bool _connecting;

    private static readonly string[] _requiredPermissions =
    {
#if UNITY_ANDROID
        Permission.Camera,
        Permission.Microphone,
#endif
        "android.permission.INTERNET",
    };

    void Start()
    {
        if (connectButton != null) connectButton.onClick.AddListener(OnConnectClicked);
        if (retryPermissionButton != null) retryPermissionButton.onClick.AddListener(RequestPermissions);

        SetStatus("初始化...");
        HidePermissionWarning();

        StartCoroutine(InitSequence());
    }

    private IEnumerator InitSequence()
    {
#if UNITY_EDITOR
        if (skipPermissionsInEditor)
        {
            _cameraPermitted = true;
            _audioPermitted = true;
            SetStatus("就绪（编辑器模式）");
            EnableConnect(true);
            yield break;
        }
#endif
        // Brief delay for UI to settle
        yield return new WaitForSeconds(0.3f);
        RequestPermissions();
    }

    private void RequestPermissions()
    {
#if UNITY_ANDROID && !UNITY_EDITOR
        SetStatus("请求权限中...");
        EnableConnect(false);
        HidePermissionWarning();

        var callbacks = new PermissionCallbacks();
        callbacks.PermissionGranted += OnPermissionGranted;
        callbacks.PermissionDenied += OnPermissionDenied;
        callbacks.PermissionDeniedAndDontAskAgain += OnPermissionDeniedPermanent;

        Permission.RequestUserPermissions(new[] { Permission.Camera, Permission.Microphone }, callbacks);
#else
        _cameraPermitted = true;
        _audioPermitted = true;
        CheckPermissionsReady();
#endif
    }

#if UNITY_ANDROID && !UNITY_EDITOR
    private void OnPermissionGranted(string permission)
    {
        Debug.Log($"[LauncherUI] Permission granted: {permission}");
        if (permission == Permission.Camera) _cameraPermitted = true;
        if (permission == Permission.Microphone) _audioPermitted = true;
        CheckPermissionsReady();
    }

    private void OnPermissionDenied(string permission)
    {
        Debug.LogWarning($"[LauncherUI] Permission denied: {permission}");
        ShowPermissionWarning(
            $"需要权限：{FriendlyName(permission)}。\n请允许权限后重试。"
        );
        EnableConnect(false);
    }

    private void OnPermissionDeniedPermanent(string permission)
    {
        Debug.LogWarning($"[LauncherUI] Permission permanently denied: {permission}");
        ShowPermissionWarning(
            $"权限已永久拒绝：{FriendlyName(permission)}。\n请到系统设置 → 应用 → 权限 中手动开启。"
        );
        EnableConnect(false);
    }

    private static string FriendlyName(string permission)
    {
        if (permission == Permission.Camera) return "摄像头";
        if (permission == Permission.Microphone) return "麦克风";
        return permission;
    }
#endif

    private void CheckPermissionsReady()
    {
        if (_cameraPermitted && _audioPermitted)
        {
            SetStatus("就绪 — 点击连接");
            EnableConnect(true);
            HidePermissionWarning();
        }
    }

    private async void OnConnectClicked()
    {
        if (_connecting) return;
        _connecting = true;
        EnableConnect(false);
        SetStatus("获取 Token...");

        // Fetch token
        bool tokenOk = false;
        string deviceId = SystemInfo.deviceUniqueIdentifier;

        if (TokenService.Instance == null)
        {
            // TokenService not in launcher scene — create one
            var go = new GameObject("TokenService");
            go.AddComponent<TokenService>();
            await System.Threading.Tasks.Task.Delay(100);
        }

        TokenService.Instance.FetchToken(deviceId, (ok) => tokenOk = ok);

        // Wait for token (max 10s)
        float elapsed = 0f;
        while (!TokenService.Instance.IsReady && elapsed < 10f)
        {
            await System.Threading.Tasks.Task.Delay(200);
            elapsed += 0.2f;
        }

        if (!TokenService.Instance.IsReady || string.IsNullOrEmpty(TokenService.Instance.LiveKitToken))
        {
            SetStatus("Token 获取失败 — 检查网络连接");
            EnableConnect(true);
            _connecting = false;
            return;
        }

        SetStatus("连接中...");

        // Update RoomManager with fresh token
        var rm = RoomManager.Instance;
        if (rm == null)
        {
            SetStatus("RoomManager 未找到，请检查场景设置");
            EnableConnect(true);
            _connecting = false;
            return;
        }

        // Connect and load scene
        try
        {
            SetStatus("连接成功 — 进入 AR...");
            await System.Threading.Tasks.Task.Delay(500);
            SceneManager.LoadScene(mainSceneName);
        }
        catch (Exception e)
        {
            SetStatus($"连接失败: {e.Message}");
            EnableConnect(true);
            _connecting = false;
        }
    }

    private void SetStatus(string msg)
    {
        if (statusText != null) statusText.text = msg;
        Debug.Log($"[LauncherUI] {msg}");
    }

    private void EnableConnect(bool enabled)
    {
        if (connectButton != null) connectButton.interactable = enabled;
    }

    private void ShowPermissionWarning(string msg)
    {
        if (permissionWarningPanel != null) permissionWarningPanel.SetActive(true);
        if (permissionWarningText != null) permissionWarningText.text = msg;
    }

    private void HidePermissionWarning()
    {
        if (permissionWarningPanel != null) permissionWarningPanel.SetActive(false);
    }
}
