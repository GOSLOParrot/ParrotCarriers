using System.Text;
using UnityEditor;
using UnityEngine;

/// <summary>
/// <b>Testing/Editor</b> — 编辑模式下扫描**当前打开场景**里与 LiveKit 多通道相关的 MonoBehaviour 是否存在（不入 Play）。<br/>
/// 用于对表 <c>docs/test/p2_5/unity_channels_audit_mobile_zh.md</c>；真机仍以 HUD + 自检日志为准。
/// </summary>
public static class ParrotSceneChannelAudit
{
    private const string MenuPath = "Parrot/Test/Editor/Audit LiveKit channels (open scene, edit mode)";

    [MenuItem(MenuPath)]
    public static void AuditOpenScene()
    {
        var sb = new StringBuilder();
        sb.AppendLine("=== Parrot LiveKit channel audit (edit mode) ===");

        void Line(string label, bool ok, string note = null)
        {
            sb.Append(ok ? "[+] " : "[-] ");
            sb.Append(label);
            if (!string.IsNullOrEmpty(note))
            {
                sb.Append(" — ");
                sb.Append(note);
            }
            sb.AppendLine();
        }

        Line("RoomManager", Object.FindObjectOfType<RoomManager>() != null);
        Line("MicrophonePublisher (voice track)", Object.FindObjectOfType<MicrophonePublisher>() != null);
        Line("ARVideoPublisher (pixel track)", Object.FindObjectOfType<ARVideoPublisher>() != null);
        Line("VideoTierReceiver (Brain→Unity setVideoTier)", Object.FindObjectOfType<VideoTierReceiver>() != null);
        Line("VideoStateReporter (Unity→Brain onVideoDegraded)", Object.FindObjectOfType<VideoStateReporter>() != null);
        Line("ParrotRpcHandler (Brain→Unity flyTo/animate)", Object.FindObjectOfType<ParrotRpcHandler>() != null);
        Line("ParrotRpcRttProbe (harness RTT)", Object.FindObjectOfType<ParrotRpcRttProbe>() != null);
        Line("XRHandTracker (Lossy DataChannel hand_gesture)", Object.FindObjectOfType<XRHandTracker>() != null,
            "optional supplement");
        Line("SceneProfileManager (setScene RPC)", Object.FindObjectOfType<SceneProfileManager>() != null);
        Line("ParrotDiagnostics + SelfTest + HUD", Object.FindObjectOfType<ParrotSelfTestCoordinator>() != null);

        sb.AppendLine("See: docs/test/p2_5/unity_channels_audit_mobile_zh.md");
        var text = sb.ToString();
        Debug.Log(text);
        EditorUtility.DisplayDialog("Parrot channel audit", text, "OK");
    }
}
