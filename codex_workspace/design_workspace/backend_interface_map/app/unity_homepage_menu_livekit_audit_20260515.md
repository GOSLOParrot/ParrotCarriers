# Unity Homepage / Menu / LiveKit Stability Audit (2026-05-15)

Owner: Unity App chat
Status: active audit
Scope: APP-015, APP-018, APP-021, APP-022, APP-023, APP-024

This audit records the current formal App state before homepage implementation.
It corrects the ECP boundary: ECP is a broad embodied-control protocol plane,
not only a DataChannel heartbeat or one RPC transport.

The detailed channel map for implementation planning is
`unity_livekit_ecp_sva_data_flow_map_20260515.md`.

## A. Source Readback

- Formal Unity entry remains `Assets/ParrotApp/Scenes/ParrotApp_Startup.unity`.
  The formal scene contains `RuntimeServices` and the startup UI controller. It
  does not mount `UI/AppV1SmokeReferenceUiController.cs`.
- App HTTP surfaces exist on app-monitor for RoomSetting, personas, line
  profiles, canvas, modules, tool cabinet, and assets.
- Brain in-room RPC handlers now expose only compact real-time controls:
  `applyRoomProfile`, `setAppCapabilityMode`, `applyWorkspace`, media/photo
  toggles, LineB audio diagnostics, and reconnect governance. Older menu read
  and persistence RPC wrappers are no longer registered.
- RoomSetting read/write is HTTP-first. The obsolete RoomSetting snapshot RPC
  is not an active App dependency. `applyRoomProfile` over LiveKit RPC is only
  a post-join Brain sync after HTTP apply.
- ECP currently spans `EcpCommand` / `EcpAck`, `EcpState`, `EcpEvent`, lossy
  ticks, command causality, frontend state, evidence/ref links, and L0 audit.
  LiveKit DataChannel and LiveKit RPC are transports under that larger
  protocol.

## B. Current Completion

Completed:

- Non-phone formal START probe passed after the ECS restart: App HTTP
  RoomSetting snapshot/save/apply, orchestrator LineB prewrite, Mint, LiveKit
  join, Brain participant, `applyRoomProfile` business-ok,
  `setAppCapabilityMode` business-ok, and `parrot.ecp.state` heartbeat publish.
- Startup page is landscape-phone targeted and no longer the near-square
  prototype. START and `experience_mode` are on the same control row.
- RoomSetting has backend `New` and `Save` paths. If `appApiUrl` points to ECS
  and any required write bearer is present, saved RoomProfiles persist on ECS.
  2026-05-15 probe saved `room_codex_persistence_probe` and reloaded it from
  ECS without changing active Room.
- The user-facing `Theme` row maps to `skin_id`. Environment or surface
  classification should remain automatic and not become a desktop/indoor/outdoor
  RoomSetting row.

Not complete:

- The formal homepage is not implemented. `MainReadySurface` is a hold screen,
  not final menu/workspace design.
- Main-ready ownership now has a formal owner: `FormalMainReadyGate` calls
  `ReportRunning()` only after transport/Brain/DataChannel and home gates are
  satisfied. `FormalHomeHudController` satisfies `hud_loaded`;
  `FormalHomeMenuLoader` satisfies `menu_snapshot_loaded` from App HTTP only
  after a real workspace/menu shell payload is parsed, with bounded retry;
  `FormalModelReadyReporter` satisfies `model_resolved`; and
  `FormalArRuntimeBootstrap` stays mounted but does not auto-start on the
  startup page. `FormalArSessionBaselineReporter` calls it on demand for
  video/AR modes to mount ARSession/ARCameraManager/ARCameraBackground before
  owning `ar_session_baseline_clean` and waits for mobile
  `ARSessionState.SessionTracking`.
  Menu snapshot parsing now uses a JsonUtility-safe timestamp field and AR
  baseline checks clear terminal coroutine refs, avoiding stale loader state.
  `FormalMainReadyGate` self-reevaluates while waiting so loader failures can
  degrade instead of silently hanging.
  The final touch drawer, model placement, and phone AR/video proof are still
  not complete.
- iQOO Neo9 phone validation for microphone, Bluetooth/SCO/A2DP, app
  background/resume, AR/video, reconnect, and no fake success is still pending.

## C. Menu Load / Save Verdict

- RoomSetting load/new/save/apply should stay on App HTTP.
- Full canvas/menu snapshots should stay on App HTTP or a future paged/compact
  HTTP read model. Current full snapshots are too large for routine RPC.
- LiveKit RPC stays for compact in-room controls such as workspace switch,
  capability mode, media/module toggles, audio route policy, reconnect
  governance, and post-join Brain sync.
- Formal mobile menu persistence must be designed through App HTTP. The old
  Brain menu RPC wrappers are removed from active registration so new homepage
  code cannot accidentally build on them.

## C2. Legacy Menu / RPC Cleanup Table

This table is now applied to the active Brain room RPC surface.

| Surface | Verdict | Reason |
|:--|:--|:--|
| `getRoomSettingSnapshot` Brain RPC | Delete/forbid reintroduction | Startup RoomSetting load/edit/save is App HTTP before LiveKit. This RPC is not an active dependency. |
| `applyRoomProfile` Brain RPC | Keep compact post-join sync | START already applies RoomProfile through App HTTP, then uses RPC only to sync Brain's in-room context and catch business errors. |
| `setAppCapabilityMode` Brain RPC | Keep compact control | It updates Brain/session/perception policy after LiveKit joins and supports silent/voice/video capability modes. |
| `onSceneReady`, `onGosloPlaced`, `setScene` | Keep placement gates | Greeting must remain gated by explicit placement; `setScene` is internal vision baseline, not RoomSetting UI scene selection. |
| `applyWorkspace` Brain RPC | Keep compact control | In-session workspace switch should not force HTTP-only round trips or LiveKit disconnect. 2D pause policy still needs implementation. |
| `setPhotoAwareness`, `setCameraMode`, `setXrHandMode` | Keep compact module toggles for now | They are small in-room App controls. Formal menu may also expose HTTP/operator equivalents, but mobile interaction can use compact RPC after Brain is present. |
| `setLineBAudioRoutePolicy` | Keep and wire from Unity | Brain already has the receiver; Unity still needs to become a formal route-policy producer on phone. |
| `registerLineBTtsSegment`, `classifyLineBMicInput`, `verifyLineBVoiceprintEmbedding` | Keep backend diagnostic/control surface; do not expose blindly in HUD | Useful for LineB/voiceprint/echo plumbing, but homepage should surface summarized readiness and route policy, not raw debug controls by default. |
| `listMenuBlocks` | Removed from active Brain RPC | Full homepage/canvas reads stay App HTTP. If a compact block list is needed later, add a new explicit HTTP or paged read model. |
| `applyMenuSelection` | Removed from active Brain RPC | Overlapped with RoomProfile/settings selection and could confuse formal menu semantics. Design accepted menu apply actions through HTTP plus specific compact RPCs only where latency matters. |
| `applyPreset`, `saveAsPreset` | Removed from active Brain RPC | Preset/menu persistence belongs to App HTTP. Do not expose mobile "save menu" through LiveKit RPC. |
| `forceUnityReconnect` Brain RPC | Keep ops/runtime control, not menu save | Used for Tier 1/runtime switch coordination. Formal reconnect owner still needs fresh-token/backoff logic. |
| `AppV1SmokeReferenceUiController` local UI actions | Reference-only | Useful interaction patterns only. Do not mount wholesale; formal HUD/menu needs new owner and App HTTP loader. |

## D. Mint / Config Verdict

- Mint design is reasonable for the phone path: Unity requests a short-lived
  LiveKit token and never receives the LiveKit API secret.
- Token mint owns Unity identity Brain dispatch. Unity must still wait for
  Brain presence plus business-ok RPC payloads, so Mint success or LiveKit join
  alone is never success.
- Phone and Editor use the same `Resources/parrot_config.json` shape. The
  values differ by environment: Editor may use localhost, while phone must use
  public ECS or a domain for `mintUrl`, `liveKitUrl`, `appApiUrl`, and
  `orchestratorUrl`.
- Current static bearer values are acceptable only for personal/dev-local
  testing in a gitignored config. Production mobile should replace them with
  device/session auth and HTTPS/WSS.

## E. Stability Status

| Area | Current State | Gap Before Phone-Stable |
|:--|:--|:--|
| Duplicate START / connect | `RoomManager` has a connect-in-flight guard and START ignores reentry. | Need phone UI recovery for cancelled/failed START. |
| Fake success | START now requires HTTP apply, LiveKit join, Brain participant, business-ok RPCs, heartbeat, and main-ready HUD/menu/model/AR gates. Menu payloads must include a real workspace/menu shell, and mobile AR baseline waits for `SessionTracking`. | Still needs phone proof; final homepage must show degraded/missing gates clearly. |
| Silent keepalive | Capability mode can disable mic/video while keeping room and Brain policy alive. | Needs final HUD state and 2D workspace policy profile. |
| 2D workspace pause | `applyWorkspace` switches in-session without disconnect. | Need explicit mic/video/tier pause rules for 2D workspace and resume. |
| Reconnect | `LiveKitReconnectSupervisor` exists for passive post-main-ready drops: it uses fresh Mint tokens, bounded backoff, LiveKit reconnect, Brain RPC re-sync, and heartbeat rebinding. START while already connected to a Tier1/LineB-changing Room uses graceful shutdown plus fresh reconnect instead of hard-failing. FSM degraded reporting now works from token/AR/connecting/reconnecting failure paths. Debug cached-token reconnect remains Editor-only. | Need user-visible degraded HUD and iQOO Neo9 network/background proof. |
| Background / resume | Lifecycle FSM handles short/long background and AR video blit pause. | Must be validated on iQOO Neo9; reconnect behavior after long background is not production-proven. |
| Bluetooth / mic route | `AudioRouteDetector` plus `MicrophonePublisher` republish mic on route changes and adjust sample rate. | Android API 31+ route detection still uses deprecated flags; no manual device picker; needs real phone proof. |
| Audio route policy to Brain | Brain RPC `setLineBAudioRoutePolicy` exists, and `AudioRoutePolicyBrainReporter` now publishes Unity route policy after Brain presence with separate `input_route` / `output_route`. | Needs iQOO Neo9 Bluetooth/SCO/A2DP logs; no manual device picker yet. |
| AR/video | `ARVideoPublisher` publishes AR or fallback video and supports tiers/mute/rebuild. | Real ARCore camera/video publish needs phone proof; final homepage must show video health. |
| ECP downstream events | Unity can publish `EcpEvent` and `EcpState`; incoming dispatcher now parses object payloads into `payload_json`. | Do not depend on full downstream menu/event UI until formal homepage consumers are built. |

## F. Script / Asset Reference Rules

Formal sources to build from:

- `Runtime/Scripts/Startup/ParrotAppStartupUiController.cs` for startup shell.
- `Runtime/Scripts/Lifecycle/**`, `LiveKit/**`, `Ecp/**`, `Backend/**` for
  runtime service flow.
- `Runtime/Scripts/Attention/**`, `Photo/**`, `Parrot/**`, `Hands/**` for
  future homepage tool integration.
- `Art/Startup/Resources/StartupPaperCraft/**` for startup sprites.
- `Art/AppV1/**` for curated future homepage slots.
- `Models/GOSLO.glb` and `Models/Ner/**` for model work.

Reference/test only:

- `Runtime/Scripts/UI/AppV1SmokeReferenceUiController.cs` is useful for HUD,
  tool drawer, paper notes, workdesk, camera panel, Focus/BBox overlays, and
  joystick ideas. It is already demoted/renamed as Smoke/reference-only and
  must not be mistaken for production App UI.
- `Assets/Tests/Smoke/**` and `Assets/Tests/NerTuning/**` are test/tuning
  evidence only. Ner tuning has useful cheek/pickup/walk capability references,
  but it is not a phone lifecycle implementation.
- The archived Sprint4 migration note is useful for script lineage and producer
  ownership, not as an active implementation source.

Search note: no explicit "Minecraft" asset or script namespace was found in the
formal `Assets/ParrotApp/**` tree. Current reusable game-like references are the
curated pixel/wood/paper AppV1 slots and Ner Spine capability actions.

## G. Next Implementation Order

0. Responsibility audit for ECP, LiveKit data flow, Mint, App HTTP, RPC,
   SVA/video, Brain/DSG/GOSLO/Scheduler, and Unity local state is complete in
   `unity_livekit_ecp_sva_data_flow_map_20260515.md`. Treat that map as the
   homepage-prep gate.
1. Extract useful reference patterns from `AppV1SmokeReferenceUiController`
   into a formal homepage plan without mounting the old controller.
2. Build formal menu load/save on App HTTP. The old Brain menu RPC wrappers
   have been removed; add only specific compact in-room controls under the
   ECP/RPC command bridge when latency requires it.
3. Prove RoomSetting `New`/`Save` persistence from the formal Unity App path.
4. Add connection stability services: fresh-token reconnect/backoff, degraded
   HUD, 2D workspace pause policy, route-policy publication, ECP event payload
   parsing, and no-fake-success error strings.
5. Continue formal homepage integration. Gate reporters now exist; future UI
   must bind to them instead of calling `ReportRunning()` directly.
6. Add the accepted touch menu/tool drawer on top of the App HTTP snapshot,
   then add compact RPC controls only for in-room actions. Do not treat the
   startup hold screen as homepage.
7. Use iQOO Neo9 as the production verification scene for mic, Bluetooth,
   app-switch, AR/video, reconnect, and voice media.

## H. Observable Status

- START non-phone chain and the LiveKit/ECP/SVA data-flow map are complete
  enough to unblock homepage design.
- Homepage/menu implementation is not complete.
- Phone/device stability is not complete.
- No shared core SSOT was changed in this audit. If APP-022 finds missing
  shared DTOs or ECP topics, add them to `core_interface_candidate_queue_20260513.md`.
