# Unity App Transport / Interface Taxonomy (2026-05-15)

Owner: Unity App chat
Status: active
Category: App business interface
Scope: APP-018

This document classifies which protocol layer and transport channel owns which
App responsibility. It is a guardrail for the Unity game/App project, LiveKit
room lifecycle, SVA/video pipeline, Brain control surface, ECP, and
menu/homepage loading. Do not treat a connectivity smoke script as proof that
the formal mobile App flow is complete.

## A. Source Readback

- Unity App is a mobile AR/game client. It owns rendering, AR session, model
  driver, touch/input, Android permissions, audio route detection, local HUD,
  and device lifecycle.
- App HTTP facade owns durable App read/write surfaces: RoomSetting, full menu
  and canvas snapshots, selector metadata, saved profiles, and larger read
  models.
- LiveKit owns real-time room transport: audio, video, DataChannel telemetry,
  and small Brain RPC control calls after a Brain participant is present.
- ECP is a broad embodied-control protocol, not merely a DataChannel
  heartbeat. Its current SSOTs are
  `.cursor/memory/architecture/protocol_snapshot_p4.md` and
  `.cursor/memory/architecture/sprint4_protocol_v2_ecp.md`. It spans
  `EcpCommand` / `EcpAck`, `EcpState`, `EcpEvent`, lossy `EcpTick`, command
  causality, frontend state, snapshot/sighting/ref evidence links, and
  L0-event auditability. LiveKit RPC and DataChannel are transports under that
  protocol, not the protocol itself.
- Brain / Scheduler / DSG should not receive full menu snapshots, full canvas
  snapshots, or persistent RoomSetting saves through LiveKit RPC. RPC payloads
  stay compact control-plane messages.
- SVA/video is a media/data-flow module. It should consume video tiers,
  snapshots, and perception requests without becoming the owner of RoomSetting
  or homepage UI state.

## B. Interface Classes

| Class | Channel | Owner | Use For | Do Not Use For |
|:--|:--|:--|:--|:--|
| Durable App HTTP | `GET/POST /api/app/**` | App facade / app-monitor | RoomSetting load/new/save/apply, selector metadata, full canvas/menu read models, workspace read models, phone-safe bootstrap data. | Per-frame telemetry, synchronous Brain action dispatch, audio/video media. |
| Orchestrator HTTP | `POST /apply_room_profile`, `/set_active_line`, `/force_unity_reconnect` | Castle orchestrator | Tier 1 runtime config prewrite, line/profile control, reconnect governance. | Menu rendering, RoomSetting persistence, per-user UI state. |
| Token Mint HTTP | `POST /mint` | Castle token-mint | Short-lived participant token, Unity identity dispatch diagnostics, server-side active Brain dispatch fallback. | Saving settings, listing menus, holding LiveKit API secrets in Unity. |
| LiveKit Media | audio/video tracks | LiveKit + Unity publishers | Microphone, Brain TTS/audio, AR/video publish, camera tier. | Settings persistence, profile snapshots, menu data. |
| ECP Protocol Plane | ECP command/ack/state/event schemas | Brain + Unity + DSG consumers | Embodied command causality, command lifecycle, frontend state, attention/photo/sighting events, snapshot/ref evidence links, connection health, lifecycle audit. | Durable RoomSetting persistence, full menu/canvas snapshots, Web-only admin state, raw Graphiti writes. |
| ECP Reliable DataChannel | `parrot.ecp.state`, `parrot.ecp.event`, `parrot.ecp.health`, `parrot.ecp.intent_disconnect` | Unity publishers / Brain ingest | EcpState heartbeat, EcpEvent facts, connection health changes, explicit disconnect intent, small reliable evidence/status packets. | Full DSG snapshots, full menu/canvas payloads, persistent saves, binary assets. |
| ECP Lossy DataChannel | `parrot.ecp.tick` | Unity interaction streams / Brain consumers | High-frequency transient pose, drag, focus/BBox motion, hand hints where only current tendency matters. | Final facts, placements/removals, photos, command completion, saved settings. |
| LiveKit RPC / ECP Command Bridge | participant RPC, future `ecpCommand`, compact command wrappers | Unity + Brain | Small request/response controls: `flyTo`/`animate`/`setVideoTier`, post-join `applyRoomProfile`, `setAppCapabilityMode`, `onSceneReady`, `onGosloPlaced`, `applyWorkspace`, media/module toggles, audio-route policy, reconnect signal. | RoomSetting snapshot/read/write, full `canvas_snapshot`, large menu payloads, preset/menu persistence, long-running storage APIs. |
| Unity Local | C# services | Unity App | AR/session lifecycle, model/prefab resolution, input devices, Bluetooth/mic route switching, HUD/menu rendering. | Backend source of truth, Brain runtime decisions, secret storage beyond gitignored runtime config. |
| Test/Smoke Scripts | Python/Editor scripts | Test evidence only | Fast non-phone verification of token, room join, Brain presence, RPC business-ok. | Completion evidence for iQOO Neo9 mic/Bluetooth/app-switch/AR/video production behavior. |

## C. Current Decisions

- RoomSetting persistent load/new/save/apply is HTTP-first. The obsolete Brain
  RoomSetting read/write RPC surface stays removed.
- Formal START must apply the selected RoomProfile through App HTTP before
  Mint/LiveKit, after any required Tier 1 orchestrator prewrite.
- `applyRoomProfile` over LiveKit RPC remains only the post-join Brain sync,
  so Brain loads the same current RoomProfile context before capability policy.
- Startup uses only a narrow ECP subset: `EcpState` heartbeat, post-join compact
  RPC controls, and placement gates. Homepage/menu work must review the larger
  ECP command/event/ref model before routing DSG/GOSLO/Scheduler interactions.
- First-pass full homepage/menu snapshot loading now exists through
  `AppHomeMenuClient` + `FormalHomeMenuLoader` using App HTTP `/api/app/canvas`.
  The final touch drawer/control design is still pending; `ParrotAppStartupUiController`
  must remain a startup/hold surface rather than the formal homepage.
- Legacy menu RPC wrappers (`listMenuBlocks`, `applyMenuSelection`,
  `applyPreset`, `saveAsPreset`) are removed from the active Brain room RPC
  registration. Full `canvas_snapshot`, menu read models, and menu/preset
  persistence must come from App HTTP or a future paged HTTP read model.
- Mint active dispatch is a token-mint/server concern. Unity waits for Brain
  presence and business-ok RPC payloads; it must not infer START success from a
  token response or LiveKit room join alone.

## D. Observable Completion Signal

- Static tests assert the formal START path includes App HTTP RoomSetting apply
  before Mint/LiveKit.
- 2026-05-15 non-phone START probe passed App HTTP RoomSetting save/apply,
  Orchestrator LineB prewrite, Mint, LiveKit connect, Brain presence without
  manual dispatch, `applyRoomProfile`, `setAppCapabilityMode`, and
  `parrot.ecp.state` heartbeat publish.
- App TODO board separates startup completion, transport taxonomy, homepage
  design, and real-device lifecycle tests.
- Static tests assert the formal home snapshot uses App HTTP and that model/AR
  gate reporters plus AR runtime bootstrap exist without copying Smoke UI.
- Phone production readiness remains blocked until iQOO Neo9 verifies mic
  permission, Bluetooth/SCO/A2DP route switching, app pause/resume, reconnect,
  AR/video publish, and no fake success states.
