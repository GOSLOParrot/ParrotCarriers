using UnityEditor;
using UnityEngine;

/// <summary>
/// <b>Testing/Editor</b> — logs a fixed checklist aligned with AR Foundation <b>5.1.x</b> + Unity <b>2022.3 LTS</b>
/// workspace skills (XR Simulation for editor iteration; no Unity 6 / AF 6).
/// Does not modify project settings; use as a human QA reminder + log correlation anchor.
/// </summary>
public static class ParrotArEditorChecklist
{
    [MenuItem("Parrot/Test/Editor/AR — Log XR Simulation checklist (to Console)", false, 20)]
    public static void LogXrSimulationChecklist()
    {
        const string block =
            "[Parrot AR checklist — Editor / XR Simulation — AF 5.1 + 2022.3]\n"
            + "1) Edit → Project Settings → XR Plug-in Management\n"
            + "2) Editor tab: enable XR Simulation (Unity XR Simulation loader)\n"
            + "3) Window → XR → XR Simulation — add virtual planes / env; navigate WASD\n"
            + "4) Android tab: enable Google ARCore for device builds (not the same as Editor Simulation)\n"
            + "5) Play: AR Session state + plane tap (TapToPlace) — compare with parrot_diagnostics.log timestamps\n"
            + "— End checklist —";

        Debug.Log(block);
        ParrotDiagnosticsLog.Instance?.Line(block.Replace("\n", " | "));
    }
}
