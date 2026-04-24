using UnityEditor;
using UnityEngine;

/// <summary>
/// <b>Testing/Editor</b> — Play Mode: trigger Unity→Brain RPC RTT probe (same as F3 HUD button).
/// </summary>
public static class ParrotEditorRpcTests
{
    private const string Prefix = "Parrot/Test/Editor/RPC — ";

    [MenuItem(Prefix + "Brain RTT (onGosloPlaced x3, Play Mode)", false, 20)]
    public static void RunBrainRttProbe()
    {
        if (!Application.isPlaying)
        {
            EditorUtility.DisplayDialog("Parrot", "Enter Play Mode first.", "OK");
            return;
        }

        var probe = UnityEngine.Object.FindObjectOfType<ParrotRpcRttProbe>();
        if (probe == null)
        {
            EditorUtility.DisplayDialog(
                "Parrot",
                "No ParrotRpcRttProbe in scene.\nUse: Parrot/Test/Editor/Add Runtime Diagnostics (HUD + Log + SelfTest)",
                "OK");
            return;
        }

        ParrotDiagnosticsLog.Instance?.Line("[EditorTest] Brain RPC RTT x3 (menu)");
        probe.TriggerProbeFromUi(3);
    }
}
