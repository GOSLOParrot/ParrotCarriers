using System.Text;
using UnityEngine;

/// <summary>
/// <b>Testing/Runtime</b> — on-screen strip + F3 panel. Same build runs on device and in Editor Play.
/// </summary>
[DefaultExecutionOrder(1000)]
public class ParrotRuntimeHud : MonoBehaviour
{
    [SerializeField] private KeyCode toggleKey = KeyCode.F3;
    [SerializeField] private bool startExpandedInDevelopment = false;

    private bool _expanded;
    private ParrotSelfTestCoordinator _self;
    private ParrotRpcRttProbe _rtt;
    private Vector2 _scroll;

    private void Start()
    {
        _self = GetComponent<ParrotSelfTestCoordinator>();
        _rtt = GetComponent<ParrotRpcRttProbe>();
#if DEVELOPMENT_BUILD || UNITY_EDITOR
        _expanded = startExpandedInDevelopment;
#endif
        var rm = RoomManager.Instance;
        if (rm != null)
        {
            rm.OnConnected += () => ParrotDiagnosticsLog.Instance?.Line("HUD: RoomManager.OnConnected");
            rm.OnDisconnected += () => ParrotDiagnosticsLog.Instance?.Line("HUD: RoomManager.OnDisconnected");
        }
    }

    private void Update()
    {
        if (Input.GetKeyDown(toggleKey))
            _expanded = !_expanded;
    }

    private void OnGUI()
    {
        try
        {
            OnGUIImpl();
        }
        catch (System.Exception e)
        {
            Debug.LogWarning($"[ParrotRuntimeHud] OnGUI non-fatal: {e.Message}");
            ParrotDiagnosticsLog.Instance?.Line($"[HUD] OnGUI non-fatal: {e.Message}");
        }
    }

    private void OnGUIImpl()
    {
        const float pad = 8f;
        var snap = _self != null ? _self.LastSnapshot : default;

        var sb = new StringBuilder();
        sb.Append("LiveKit: ");
        sb.Append(snap.Connected ? "ON" : "OFF");
        if (snap.Connected)
            sb.Append($"  room={snap.RoomName}  me={snap.LocalIdentity}");
        sb.AppendLine();
        sb.Append("Brain agent: ").Append(snap.BrainAgentPresent ? "yes" : "no");
        sb.Append("  |  Video pub: ").Append(snap.VideoPublishing ? "yes" : "no");
        sb.Append("  |  Tier: ").Append(snap.VideoTierReceiverPresent ? snap.VideoTier : "—");
        sb.AppendLine();
        sb.Append("AR: ").Append(snap.ArSessionHint);
        if (!string.IsNullOrEmpty(snap.XrLoaderHint) && snap.XrLoaderHint != "n/a")
            sb.Append("  |  ").Append(snap.XrLoaderHint);
        if (snap.LastConnectDurationSeconds.HasValue)
            sb.Append($"  |  last connect: {snap.LastConnectDurationSeconds.Value:F2}s");
        if (_rtt != null && !string.IsNullOrEmpty(_rtt.LastSummary))
            sb.Append("  |  ").Append(_rtt.LastSummary);
        if (!string.IsNullOrEmpty(snap.LastNote))
            sb.Append("  |  ").Append(snap.LastNote);

        var summary = sb.ToString();
        var style = new GUIStyle(GUI.skin.box) { fontSize = 13, alignment = TextAnchor.UpperLeft };
        var summaryHeight = style.CalcHeight(new GUIContent(summary), Screen.width * 0.45f);

        GUI.Box(new Rect(pad, pad, Screen.width * 0.46f, summaryHeight + pad * 2f), summary, style);

        if (!_expanded)
        {
            GUI.Label(new Rect(pad, pad + summaryHeight + pad * 2f, 460, 22), $"Press {toggleKey} for log + self-test (Testing/Runtime)");
            return;
        }

        float panelTop = pad + summaryHeight + pad * 2f + 22f;
        float panelH = Mathf.Min(Screen.height * 0.55f, 420f);
        GUILayout.BeginArea(new Rect(pad, panelTop, Screen.width * 0.48f, panelH), GUI.skin.window);
        GUILayout.Label($"Log file: {ParrotDiagnosticsLog.Instance?.LogFilePath ?? "(no log component)"}");

        GUILayout.BeginHorizontal();
        if (GUILayout.Button("Run self-test", GUILayout.Width(120)) && _self != null)
            _self.RunSelfTestFromUi();
        if (GUILayout.Button("Brain RPC RTT x3", GUILayout.Width(140)) && _rtt != null)
            _rtt.TriggerProbeFromUi(3);
        if (GUILayout.Button("Copy recent log", GUILayout.Width(120)))
            ParrotDiagnosticsLog.Instance?.CopyRecentToClipboard(500);
        GUILayout.EndHorizontal();
        GUILayout.Label(
            "[目的] RTT=Unity→Brain onGosloPlaced 往返，测信令/应用层；不含视频编码与 Gemini。",
            GUI.skin.box);

        _scroll = GUILayout.BeginScrollView(_scroll, GUILayout.ExpandHeight(true));
        var tail = ParrotDiagnosticsLog.Instance != null
            ? ParrotDiagnosticsLog.Instance.GetRecentText(80)
            : "(ParrotDiagnosticsLog not in scene)";
        GUILayout.TextArea(tail, GUILayout.ExpandHeight(true));
        GUILayout.EndScrollView();
        GUILayout.EndArea();
    }
}

