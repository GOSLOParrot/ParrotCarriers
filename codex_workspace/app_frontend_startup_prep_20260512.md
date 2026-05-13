# App Frontend Startup Prep — ECS Orchestrator Handoff (2026-05-12)

Purpose: start App frontend work from the new ECS control plane without mixing
core interfaces and business UI. This file is a Codex-side working map; durable
core contracts remain in `.cursor/memory/architecture/Interface/`.

## 1. Current Backend Control Plane

Existing core surfaces, no new core API required for the first startup slice:

| Surface | Owner | Consumer | Notes |
|:---|:---|:---|:---|
| Token mint `POST /mint` | `src/parrot/castle/token_mint.py` | Unity App | Existing `LiveKitTokenMintClient`; Unity never holds LiveKit API secret. |
| Orchestrator `GET /status` | `src/parrot/castle/orchestrator/status.py` | Web console, HUD badge | Aggregates runtime_config, Brain snapshot, drift, processes, containers, preflight, crash, restart stats. |
| Orchestrator writes | `src/parrot/castle/orchestrator/server.py` | Unity startup, operator | `/set_active_line`, `/apply_room_profile`, `/force_unity_reconnect`, `/restart_component`, `/clear_runtime_config`, `/rolling_restart_brain`. |
| Runtime config | `src/parrot/castle/runtime_config.py` | Brain, orchestrator | `file > BB > env > default`; orchestrator is the intended file writer. |
| Tier registry | `data/registries/setting_change_tier.json` | Brain, Unity | C# mirror already exists at `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/UI/SettingChangeTierDto.cs`. |
| RoomSetting read model | `src/parrot/brain/room_setting.py` | Unity startup/menu | `compatibility` now exposes `tier`, `tier_label`, `tier_summary`, `tier_summary_zh`, `tier_ui_action`. |
| Existing Brain RPCs | `src/parrot/brain/agent.py` | Unity after LiveKit join | `applyRoomProfile`, `setAppCapabilityMode`, `applyWorkspace`, `onSceneReady`, `onGosloPlaced`, plus menu canvas RPC mirrors. |

## 2. Route Split

Unity App first:

| App route | Core surface | Business owner |
|:---|:---|:---|
| Startup Line / RoomProfile selection | RoomSetting compatibility + orchestrator `/apply_room_profile` or `/set_active_line` | Unity startup UI |
| Startup Maid Team selection | Fixed `CatMaid Team` V1 placeholder first; future `agent_team_id` core field after approval | Unity startup UI |
| Tier 0 menu action | Existing Brain RPC / BB-backed facade | Unity menu canvas |
| Tier 1 reconnect action | Orchestrator write with `force_reconnect=true` after confirm | Unity startup/menu |
| Tier 2 process restart | Orchestrator `/restart_component` and `/status` polling | Unity menu, likely debug-gated |
| Tier 3 operator-only | No App write | UI prompt only |
| HUD running badge | Orchestrator `/status.brain_runtime_snapshot` + `selection_drift` | Unity HUD |

Web console first:

| Web route | Core surface | Business owner |
|:---|:---|:---|
| ECS/module health | Orchestrator `/status` via server-side client | `src/parrot/web_console` BFF or existing monitor |
| Menu/canvas status | `AppFirstVersionFacade().canvas_snapshot()` | read-only dashboard |
| DSG/L2-B snapshot | existing `app_monitor_server` and DSG read helpers | read-only visualization |
| Blackboard/IntentWorkspace/Plan/Nanobot monitor | existing Python read adapters where available | read-only dashboard; missing reads become interface-gap notes |
| AgentTeam / MCP admin | Web-only business interface after approval | profile editor, apply/restart flow, MCP status |

Keep App business code under `unity/ArSpike/**`. Keep Web business code under
`src/parrot/web_console/**` + `web/console/**` when it is created. Do not put
Web-only dashboard concerns into Unity DTOs, and do not put App-specific button
flow into core interface docs.

## 3. Gaps To Confirm Before Adding Core Interfaces

No new backend core endpoint is needed yet. Confirmed decision on 2026-05-13:
the first App implementation assumes a self-use trusted device and may use a
dev-local orchestrator secret for Tier 1 startup/menu switches. Production must
not embed `PARROT_ORCH_SECRET` in the APK; it should use a short-lived scoped
control token or a server-side BFF.

Report back before adding any of these:

| Item | Why it matters | Recommendation |
|:---|:---|:---|
| `/status` auth wording | Completion report says read-only, but current code/tests require Bearer when `PARROT_ORCH_SECRET` is set. | Treat as server-side secret in Web BFF; Unity HUD badge can wait or use a dev-only secret injection path. |
| Unity orchestrator secret storage | `Resources/parrot_config.json` is convenient but not safe for a real secret. | Add config fields in examples only; actual secret should be build-time/dev-local injection before production. |
| Tier action names | Registry has `confirm_with_progress_bar` / `operator_only`; C# helper maps by tier. | Keep helper tier-based; normalize names only if UI needs string dispatch. |
| Web write controls | Writing through Web would expose Bearer and widen blast radius. | Keep P3 Web console read-only until user explicitly approves write UX. |
| Missing Web read adapters | L1.5 / Plan / Nanobot live views may lack clean read APIs. | Document each missing read as field C in the business A-D table before adding core surfaces. |

Tier policy:

| Tier | Self-use App | Production direction |
|:---:|:---|:---|
| 0 | Direct menu RPC / BB-backed facade. | Same. |
| 1 | Confirm dialog, then call orchestrator with a dev-local secret. | Confirm dialog, then exchange for a short-lived token scoped to line/profile switching. |
| 2 | Debug-folded action only. | Local unlock / admin confirmation before process restart. |
| 3 | Not exposed in App. | Operator console only. |

## 4. Parallel Worktree Plan

Codex can support parallel work through separate worktrees/branches if we keep
write scopes disjoint:

| Workstream | Suggested branch | Write scope |
|:---|:---|:---|
| Unity App startup | `codex/app-startup-orchestrator` | `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/**`, `unity/ArSpike/Assets/ParrotApp/Resources/*.example`, App-side docs |
| Web console read model | `codex/web-console-status` | `src/parrot/web_console/**`, `web/console/**`, Web-side docs |
| Shared SSOT/prep | current prep branch | `.cursor/memory/**`, `codex_workspace/**` |

Both App and Web can consume the same core SSOT. Shared C# DTOs, core Python
schemas, and `.cursor/memory` docs should be touched by only one stream at a
time.

## 5. First Unity Startup Slice

1. Add a Unity `OrchestratorClient` for `GetStatusAsync`,
   `SetActiveLineAsync`, `ApplyRoomProfileAsync`, `ForceUnityReconnectAsync`,
   and `RestartComponentAsync`.
2. Extend `parrot_config.json.example` with orchestrator URL fields, without
   committing a real secret.
3. In startup selection, compute tier from RoomSetting compatibility or local
   registry mirror.
4. For cold start, write selected RoomProfile/Line through orchestrator before
   LiveKit connect; keep the existing `applyRoomProfile` Brain RPC after join
   as the in-room BB/profile sync.
5. For an already connected room, Tier 1 asks for confirmation and calls
   orchestrator with `force_reconnect=true`.
6. Add a small HUD badge for running line/profile from `/status`.

## 6. 2026-05-13 Parallel Route Addendum

Durable decision doc:
`.cursor/memory/architecture/Interface/app_web_parallel_routes_agent_team_20260513.md`.

Operational workflow:
`codex_workspace/app_web_parallel_workflow_20260513.md`.

Ratified route:

1. Unity App and Web Console can proceed in parallel as separate business
   workstreams.
2. Shared core interfaces stay in `.cursor/memory/architecture/Interface/**`.
3. Unity App owns mobile startup, HUD, menu rendering, game completion, tools,
   and report/workspace entry.
4. Web Console owns dense observability, L1.5/L2-B/Plan/Blackboard/Nanobot
   monitoring, node/photo management, AgentTeam/MCP admin, and process status.
5. `RoomSetting` now includes `Maid Team` in addition to Model, Room, Persona,
   Line, and Scene. For V1, render `CatMaid Team` as the only selectable team
   until a core `agent_team_id` field is approved.
