using System.Text;
using UnityEngine;

/// <summary>
/// <b>Testing/Runtime</b> — 左上角状态条 + 日志/自检面板（IMGUI）。<br/>
/// <b>桌面</b>：默认用键盘 <see cref="toggleKey"/>（如 F3）展开/收起。<br/>
/// <b>真机（Android/iOS 或 Handheld）</b>：无物理键盘，在状态条下方绘制<strong>大触控按钮</strong>，
/// 无需 F3 即可打开面板、运行自检、复制最近日志；详见仓库 <c>docs/test/p2_5/mobile_runtime_harness_zh.md</c>。<br/>
/// 挂在与 <see cref="ParrotSelfTestCoordinator"/>、<see cref="ParrotDiagnosticsLog"/> 同一物体上（如 Dev 场景的 ParrotDiagnostics）。
/// </summary>
[DefaultExecutionOrder(1000)]
public class ParrotRuntimeHud : MonoBehaviour
{
    [Header("Desktop")]
    [Tooltip("编辑器 / Windows 等带键盘环境：按下此键切换日志面板。")]
    [SerializeField] private KeyCode toggleKey = KeyCode.F3;

    [Tooltip("Development Build 或 Editor 启动时是否默认展开面板。")]
    [SerializeField] private bool startExpandedInDevelopment = false;

    [Header("Handheld (真机)")]
    [Tooltip("触控主按钮最小高度（dp 约 44 为可点区域参考）。")]
    [SerializeField] private float touchButtonMinHeight = 48f;

    private bool _expanded;
    private ParrotSelfTestCoordinator _self;
    private ParrotRpcRttProbe _rtt;
    private Vector2 _scroll;
    private GUIStyle _touchButtonStyle;

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

    /// <summary>Android/iOS 或 Unity 报告的 Handheld，走触控条；否则走键盘 F3 提示。</summary>
    private static bool PreferTouchHarnessControls()
    {
#if UNITY_ANDROID || UNITY_IOS
        return true;
#else
        return SystemInfo.deviceType == DeviceType.Handheld;
#endif
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

    private GUIStyle TouchButtonStyle()
    {
        if (_touchButtonStyle != null)
            return _touchButtonStyle;
        _touchButtonStyle = new GUIStyle(GUI.skin.button)
        {
            fontSize = Mathf.Max(14, GUI.skin.button.fontSize + 2),
            wordWrap = true,
            alignment = TextAnchor.MiddleCenter,
        };
        return _touchButtonStyle;
    }

    private void OnGUIImpl()
    {
        const float pad = 8f;
        float panelWidth = Screen.width * 0.46f;
        float baseX = pad;

        var snap = _self != null ? _self.LastSnapshot : default;

        var sb = new StringBuilder();
        sb.Append("LiveKit: ");
        sb.Append(snap.Connected ? "ON" : "OFF");
        if (snap.Connected)
            sb.Append($"  room={snap.RoomName}  me={snap.LocalIdentity}");
        sb.AppendLine();
        sb.Append("Brain agent: ").Append(snap.BrainAgentPresent ? "yes" : "no");
        sb.Append("  |  Video pub: ").Append(snap.VideoPublishing ? (snap.VideoFrameFresh ? "yes" : "stale") : "no");
        if (snap.ArVideoPublisherPresent)
            sb.Append($"({snap.VideoSource}/{snap.VideoFrameCount}, age={snap.VideoLastFrameAgeSeconds:F1}s)");
        sb.Append("  |  Tier: ").Append(snap.VideoTierReceiverPresent ? snap.VideoTier : "—");
        sb.AppendLine();
        sb.Append("Audio pub: ").Append(snap.MicPublishing ? "yes" : "no");
        if (snap.MicPublisherPresent && snap.MicConfiguredSampleRate > 0)
            sb.Append($"({snap.MicConfiguredSampleRate / 1000f:F0}k)");
        sb.Append("  |  RPC in(fly/anim): ").Append(snap.ParrotRpcHandlerPresent ? "yes" : "—");
        sb.Append("  |  Hand DC: ").Append(snap.XrHandTrackerPresent ? "yes" : "—");
        sb.Append("  |  VisRPC: ").Append(snap.VideoStateReporterPresent ? "yes" : "—");
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
        var boxStyle = new GUIStyle(GUI.skin.box) { fontSize = 13, alignment = TextAnchor.UpperLeft };
        float summaryHeight = boxStyle.CalcHeight(new GUIContent(summary), panelWidth);

        GUI.Box(new Rect(baseX, pad, panelWidth, summaryHeight + pad * 2f), summary, boxStyle);

        // 状态条下沿：后续控件统一从这里往下排（真机两行按钮 / 桌面一行提示）
        float yAfterSummary = pad + summaryHeight + pad * 2f;

        if (PreferTouchHarnessControls())
        {
            float btnH = Mathf.Max(44f, touchButtonMinHeight);
            float innerW = panelWidth - pad * 2f;
            float halfGap = 6f;
            float halfW = (innerW - halfGap) * 0.5f;
            var btnSt = TouchButtonStyle();

            // 主入口：展开完整日志窗口（内含 RTT、长日志）；真机无 F3
            var rOpen = new Rect(baseX + pad, yAfterSummary, innerW, btnH);
            string openLabel = _expanded ? "收起日志 / 自检面板" : "打开日志 / 自检面板（真机）";
            if (GUI.Button(rOpen, openLabel, btnSt))
                _expanded = !_expanded;
            yAfterSummary += btnH + 6f;

            // 折叠时也提供一键自检 / 复制，不必先进面板
            if (!_expanded)
            {
                var rSelf = new Rect(baseX + pad, yAfterSummary, halfW, btnH);
                var rCopy = new Rect(baseX + pad + halfW + halfGap, yAfterSummary, halfW, btnH);
                if (GUI.Button(rSelf, "运行自检", btnSt) && _self != null)
                    _self.RunSelfTestFromUi();
                if (GUI.Button(rCopy, "复制最近日志", btnSt))
                    ParrotDiagnosticsLog.Instance?.CopyRecentToClipboard(500);
                yAfterSummary += btnH + 6f;
            }
        }
        else
        {
            if (!_expanded)
            {
                GUI.Label(new Rect(baseX, yAfterSummary, panelWidth, 22),
                    $"按 {toggleKey} 打开日志与自检（Testing/Runtime）");
                return;
            }

            yAfterSummary += 22f;
        }

        if (!_expanded)
            return;

        float panelTop = yAfterSummary;
        float panelH = Mathf.Min(Screen.height * 0.55f, 420f);
        GUILayout.BeginArea(new Rect(baseX, panelTop, panelWidth, panelH), GUI.skin.window);
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
