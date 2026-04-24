using UnityEditor;
using UnityEngine;

/// <summary>
/// <b>Testing/Editor</b> — writes <c>[SEQ]</c> markers for phase alignment (see docs/test/p2_5/pipeline_test_matrix_sprint3.md §0).
/// </summary>
public static class ParrotEditorSequenceMarkers
{
    private const string Prefix = "Parrot/Test/Editor/Sequence — ";

    [MenuItem(Prefix + "Log P0 static checklist done (no Play required)", false, 5)]
    public static void LogP0Done()
    {
        ParrotTestSeq.Mark("P0-done static: Console cleared + 0 compile errors + XR/Player settings reviewed (honor system)");
        EditorUtility.DisplayDialog(
            "Parrot",
            "Logged [SEQ] P0-done to Console.\nIf in Play Mode with ParrotDiagnosticsLog, it also goes to parrot_diagnostics.log.\nOtherwise paste this line into your §F report.",
            "OK");
    }
}
