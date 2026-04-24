ParrotDev — Testing layout (Unity 2022.3 + AR Foundation 5.1)

Intern / 手测入口: docs/test/p2_5/pipeline_test_matrix_sprint3.md — §0 phases P0→P1→P2, then §A–F, then §3 matrix.
P0 anchor menu: Parrot/Test/Editor/Sequence — Log P0 static checklist done (no Play required).
Remote monitor boot prompt: docs/test/p2_5/remote_cursor_test_monitor_boot_prompt.md

Runtime/  (Scripts/Testing/Runtime/)
  Runs in Player: Editor Play Mode AND device APK.
  Use for: on-screen HUD, ring-buffer + parrot_diagnostics.log, self-test snapshot,
           LiveKit connect duration (from RoomManager), AR session + Editor XRCameraSubsystem hint,
           Unity→Brain RPC RTT probe (onGosloPlaced x3, [RpcRtt] log prefix — signalling only).

Editor/  (Scripts/Testing/Editor/)
  UnityEditor only. Use for: Sprint3 scene augment, add diagnostics root, LiveKit disconnect/reconnect
  smoke tests, Brain RPC RTT menu, AR XR Simulation checklist log (human QA anchor — does not auto-change Project Settings).

Correlate tests: run Editor menu actions → note wall-clock → match Console + parrot_diagnostics.log +
  backend logs on the same timeline.
