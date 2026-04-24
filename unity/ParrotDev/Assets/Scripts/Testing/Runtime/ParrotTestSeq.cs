using UnityEngine;

/// <summary>
/// <b>Testing/Runtime</b> — ordered <c>[SEQ]</c> lines for <c>parrot_diagnostics.log</c> alignment with
/// <c>docs/test/p2_5/pipeline_test_matrix_sprint3.md</c> phases P0/P1/P2. Safe when <see cref="ParrotDiagnosticsLog"/> is missing (falls back to <c>Debug.Log</c> only).
/// </summary>
public static class ParrotTestSeq
{
    public static void Mark(string tag)
    {
        var line = "[SEQ] " + tag;
        Debug.Log(line);
        var log = ParrotDiagnosticsLog.Instance;
        if (log != null)
            log.Line(line);
    }
}
