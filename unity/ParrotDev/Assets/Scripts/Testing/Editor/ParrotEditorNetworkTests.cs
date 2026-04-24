using UnityEditor;
using UnityEngine;

/// <summary>
/// <b>Testing/Editor</b> — Play Mode only: LiveKit <b>connectivity / resilience smoke</b> (disconnect, reconnect, delay).
/// <b>Test purpose:</b> exercise backend + client room lifecycle and log correlation — <b>not</b> the AR App
/// launch/onboarding/connect product design. Safe to extend for coverage; do not cite these menus as
/// the authoritative app connection spec.
/// </summary>
public static class ParrotEditorNetworkTests
{
    private const string Prefix = "Parrot/Test/Editor/Network — ";

    [MenuItem(Prefix + "Disconnect LiveKit (Play Mode)", false, 10)]
    public static void Disconnect()
    {
        if (!Application.isPlaying)
        {
            EditorUtility.DisplayDialog("Parrot", "Enter Play Mode first.", "OK");
            return;
        }

        var rm = RoomManager.Instance;
        if (rm == null)
        {
            EditorUtility.DisplayDialog("Parrot", "No RoomManager in Play Mode.", "OK");
            return;
        }

        ParrotDiagnosticsLog.Instance?.Line("[EditorTest] Disconnect LiveKit (menu)");
        rm.DisconnectForTesting();
    }

    [MenuItem(Prefix + "Reconnect in 1s (Play Mode)", false, 11)]
    public static void ReconnectInOneSecond()
    {
        if (!Application.isPlaying)
        {
            EditorUtility.DisplayDialog("Parrot", "Enter Play Mode first.", "OK");
            return;
        }

        var rm = RoomManager.Instance;
        if (rm == null)
        {
            EditorUtility.DisplayDialog("Parrot", "No RoomManager.", "OK");
            return;
        }

        ParrotDiagnosticsLog.Instance?.Line("[EditorTest] Reconnect in 1s (menu)");
        rm.ReconnectUsingCachedCredentials();
    }

    [MenuItem(Prefix + "Disconnect → wait 1s → Reconnect (Play Mode)", false, 12)]
    public static void DisconnectWaitReconnect()
    {
        if (!Application.isPlaying)
        {
            EditorUtility.DisplayDialog("Parrot", "Enter Play Mode first.", "OK");
            return;
        }

        var rm = RoomManager.Instance;
        if (rm == null)
        {
            EditorUtility.DisplayDialog("Parrot", "No RoomManager.", "OK");
            return;
        }

        ParrotDiagnosticsLog.Instance?.Line("[EditorTest] Disconnect → 1s → Reconnect (menu)");
#if UNITY_EDITOR
        rm.StartEditorReconnectTest(1f);
#endif
    }
}
