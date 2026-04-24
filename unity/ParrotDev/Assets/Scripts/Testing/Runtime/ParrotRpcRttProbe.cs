using System.Collections;
using UnityEngine;
using LiveKit;

/// <summary>
/// <b>Testing/Runtime</b> — Unity→Brain <see cref="Room.LocalParticipant.PerformRpc"/> round-trip
/// using the existing <c>onGosloPlaced</c> handler (trivial JSON ack, no extra Brain RPC contract).
/// <b>Test purpose:</b> control-plane / signalling latency — not video bitrate, not Gemini inference time.
/// P2.5 harness; do not treat as end-user SLA.
/// </summary>
public class ParrotRpcRttProbe : MonoBehaviour
{
    /// <summary>Short human-readable result for HUD (e.g. "RTT 42ms (n=3)").</summary>
    public string LastSummary { get; private set; } = "";

    public void TriggerProbeFromUi(int samples = 3)
    {
        if (samples < 1) samples = 1;
        StopAllCoroutines();
        StartCoroutine(RunProbeCoroutine(samples, 8000));
    }

    public IEnumerator RunProbeCoroutine(int samples, int timeoutMs)
    {
        var log = ParrotDiagnosticsLog.Instance;
        void L(string m)
        {
            Debug.Log("[RpcRtt] " + m);
            log?.Line("[RpcRtt] " + m);
        }

        LastSummary = "";
        var rm = RoomManager.Instance;
        if (rm == null || !rm.IsConnected || rm.Room == null)
        {
            LastSummary = "skip: not connected";
            L("FAIL: RoomManager not connected.");
            yield break;
        }

        string brainId = BrainParticipantResolver.FindBrainParticipantId(rm.Room);
        if (string.IsNullOrEmpty(brainId))
        {
            LastSummary = "skip: no brain";
            L("FAIL: No Brain participant (agent-* or identity brain).");
            yield break;
        }

        L($"INFO: destination={brainId} method=onGosloPlaced samples={samples} timeoutMs={timeoutMs}");
        ParrotTestSeq.Mark("P1-step6-rtt-START");

        float sumMs = 0f;
        int ok = 0;
        for (int i = 0; i < samples; i++)
        {
            float t0 = Time.realtimeSinceStartup;
            var rpcCall = rm.Room.LocalParticipant.PerformRpc(new PerformRpcParams
            {
                DestinationIdentity = brainId,
                Method = "onGosloPlaced",
                Payload = "{\"rtt_probe\":true,\"i\":" + i + "}",
                ResponseTimeout = timeoutMs,
            });
            yield return rpcCall;
            float dtMs = (Time.realtimeSinceStartup - t0) * 1000f;

            if (rpcCall.IsError)
                L($"sample {i + 1}/{samples} FAIL {dtMs:F0}ms err={rpcCall.Error?.Message}");
            else
            {
                ok++;
                sumMs += dtMs;
                L($"sample {i + 1}/{samples} OK {dtMs:F0}ms");
            }

            yield return new WaitForSecondsRealtime(0.12f);
        }

        LastSummary = ok == samples
            ? $"RTT avg {sumMs / samples:F0}ms (n={samples})"
            : $"RTT partial ok={ok}/{samples}";
        L("INFO: " + LastSummary);
        ParrotTestSeq.Mark("P1-step6-rtt-END " + LastSummary);
    }
}
