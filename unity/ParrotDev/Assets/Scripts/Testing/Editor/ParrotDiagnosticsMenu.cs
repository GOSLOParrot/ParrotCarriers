using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

/// <summary>
/// <b>Testing/Editor</b> — adds runtime diagnostics root to the <b>open scene</b> (same prefab as Sprint3 Augment).
/// </summary>
public static class ParrotDiagnosticsMenu
{
    private const string MenuPath = "Parrot/Test/Editor/Add Runtime Diagnostics (HUD + Log + SelfTest)";

    [MenuItem(MenuPath)]
    public static void AddDiagnosticsRoot()
    {
        if (UnityEngine.Object.FindObjectOfType<ParrotDiagnosticsLog>() != null)
        {
            EditorUtility.DisplayDialog(
                "Parrot Diagnostics",
                "ParrotDiagnosticsLog already exists in the scene.",
                "OK");
            return;
        }

        var go = new GameObject("ParrotDiagnostics");
        Undo.RegisterCreatedObjectUndo(go, "ParrotDiagnostics");
        go.AddComponent<ParrotDiagnosticsLog>();
        go.AddComponent<ParrotSelfTestCoordinator>();
        go.AddComponent<ParrotRpcRttProbe>();
        go.AddComponent<ParrotRuntimeHud>();

        EditorSceneManager.MarkSceneDirty(SceneManager.GetActiveScene());
        Debug.Log("[ParrotDiagnosticsMenu] Added ParrotDiagnostics. Press F3 in Play Mode.");

        EditorUtility.DisplayDialog(
            "Parrot Diagnostics",
            "Added 'ParrotDiagnostics' (Testing/Runtime scripts).\n\n" +
            "Play: HUD + F3 (self-test, log tail, Brain RPC RTT x3); device log: persistentDataPath/parrot_diagnostics.log\n\nSave the scene.",
            "OK");
    }
}
