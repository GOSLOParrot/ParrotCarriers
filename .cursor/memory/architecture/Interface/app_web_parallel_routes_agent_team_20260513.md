---
status: ratified
category: interface-routing
status_note: "2026-05-13: Ratifies App/Web parallel work split, AgentTeam vs nanobot instance boundary, and Maid Team as a RoomSetting selector."
last_reviewed: 2026-05-13
ai_priority: high
ai_audience: "Codex/Cursor chats touching Unity App frontend, Web console, RoomSetting, Scheduler/Nanobot routing, or ECS control-plane UI."
parent_doc: "INDEX.md"
related:
  - "../backend_interface_refinement_20260507.md"
  - "menu_design_complete_20260507.md"
  - "../ecs_orchestrator_lifecycle_completion_20260512.md"
  - "ecs_orchestrator_codex_guidance_20260512.md"
  - "app_v1_room_setting_room_profile_interface_20260510.md"
  - "../../../../codex_workspace/app_frontend_startup_prep_20260512.md"
---

# App/Web Parallel Routes And AgentTeam Boundary

This document records the 2026-05-13 decision for starting Unity App and Web
Console work in parallel while keeping shared core interfaces clean.

Operational workflow for the two chats lives in:
`codex_workspace/app_web_parallel_workflow_20260513.md`.

## 1. Ratified Decisions

1. `Ner` is a Brain-side model/persona/profile concern. It is not a nanobot
   config or nanobot team example.
2. A nanobot process is an **Agent Unit**: one running config, workspace,
   channel set, MCP set, cron/dream state, and session store.
3. An **AgentTeam** or **Maid Team** is a Parrot logical layer above nanobot.
   It may map to one nanobot instance for V1, or to a group of instances later.
4. `CatMaid Team` V1 starts as one nanobot instance. Do not add multi-instance
   orchestration until the default team path is observable and stable.
5. Startup `RoomSetting` now has six user-facing selectors:
   `Model`, `Room`, `Persona`, `Line`, `Theme`, and `Maid Team`.
   `Theme` writes `skin_id` / UI suite. Internal `scene_profile_id` stays a
   runtime launch baseline and should not be exposed as a desktop/indoor/outdoor
   RoomSetting row.
6. App and Web share core interfaces, but their business interfaces stay
   separate. Missing core surfaces must be reported before implementation.

## 2. Boundary Model

| Layer | Owner | Meaning | Switching model |
|:--|:--|:--|:--|
| Brain Persona / Brain Model | Brain + RoomProfile | GOSLO/Ner/etc. live model, prompt, line, scene context. | Existing RoomSetting / runtime_config / Tier flow. |
| Maid Team / AgentTeam | Parrot control plane | Background agent capability bundle selected by the room. | New logical selector; defaults to `catmaid_team_default`. |
| Nanobot Instance Group | Orchestrator + Scheduler | One or more nanobot workers assigned to a team. | Warm switch or rolling restart when membership/config changes. |
| Nanobot Instance | nanobot fork | A concrete process with config, workspace, channel, MCP, cron, session state. | Restart for provider/MCP/channel config; next message for many workspace file changes. |

## 3. Shared Core Surfaces

Both App and Web may consume these, but neither should fork the contract:

| Core surface | Current owner | Consumers |
|:--|:--|:--|
| Token mint `POST /mint` | `src/parrot/castle/token_mint.py` | Unity App startup. Unity identities request unnamed Brain agent dispatch by default; room join alone is not Brain RPC readiness. |
| Orchestrator `/status` | `src/parrot/castle/orchestrator/status.py` | Web console, App HUD/debug badge. |
| Orchestrator setting writes | `src/parrot/castle/orchestrator/server.py` | Unity self-use startup/menu; Web operator console after approval. |
| Runtime config | `src/parrot/castle/runtime_config.py` | Brain, orchestrator, future AgentTeam selector. |
| Setting tier registry | `data/registries/setting_change_tier.json` | Unity menu, Web console. |
| RoomSetting compatibility | `src/parrot/brain/room_setting.py` | Unity startup/menu; Web inspection. |
| Menu registry / canvas blocks | `src/parrot/brain/menu_registry.py` and menu docs | Unity canvas and Web visualization. |
| Scheduler task routing | `src/parrot/scheduler/service.py` | Brain tools, Nanobot workers, future AgentTeam routing. |

## 4. Unity App Business Route

App work emphasizes mobile UI, startup flow, game completion, and tool use.

| App route | Business scope | Core dependency |
|:--|:--|:--|
| Startup RoomSetting | Select saved Room, Model, Persona, Line, Theme, Maid Team; then START. | RoomSetting + orchestrator runtime writes. |
| Runtime menu canvas | Render 4/5-block menu and tier actions in a mobile/AR-friendly way. | Menu registry + tier registry + Brain RPC mirrors. |
| HUD and debug badge | Show connection, current line/profile/team, lightweight status. | `/status`, Brain snapshot, ECP state. |
| Game/model interactions | Ner/GOSLO model controls, touch, joystick, pickup/place, tools. | Model manifest, `play_capability`, ECP/RPC. |
| Tools and reports | Photo, focus, notes, Nanobot result cards, 2D workspace entry. | Existing photo, scheduler, report/workspace adapters. |

App should not edit nanobot JSON, MCP definitions, or Web console admin state.
It can select a Maid Team preset once a shared core field exists. Until then,
the selector may render `CatMaid Team` as a fixed V1 option.

2026-05-13 App START verification rule: Mint success and LiveKit room join are
only transport readiness. Full START needs Brain participant presence, successful
business RPC payloads, DataChannel heartbeat, and main-ready gate ownership. The
Castle LineB Google STT ADC / token-mint dispatch blocker was reported repaired
on 2026-05-14. Do not treat old tmux Brain logs, service health alone, or Smoke
UI scenes as formal App completion; use Brain participant + business RPC
payloads as the next gate. After Castle `c0f1705`, the 2026-05-14 fast retry
passed post-join `applyRoomProfile` and `setAppCapabilityMode` business-ok
with `ner_lineb_room`. The obsolete Brain RoomSetting read/write RPC surface
has been removed from active backend code; formal RoomSetting
cold-load/edit/save stays on App HTTP before LiveKit connects. The default
LineA RoomProfile still fails correctly against a running LineB Brain and must
remain a real App START failure. Phone RoomSetting/orchestrator proof is
separate; user repaired public ECS routing on 2026-05-14, so App API
RoomSetting returns 2 rooms and Orchestrator health is ok from this workstation.
Next proof is formal Unity/phone START with RoomSetting save/apply, Tier 1
prewrite, and main-ready gates.

2026-05-14 App HTTP selector/security update: `GET /api/app/line-profiles` is
reachable on app-monitor, `GET /api/app/personas` was added for selector-safe
Persona metadata, and app-monitor POST routes can be protected with
`PARROT_APP_MONITOR_SECRET` plus Unity's ignored `appApiSecret`.

## 5. Web Console Business Route

Web work emphasizes observability, management, visualization, and admin flows.

| Web route | Business scope | Core dependency |
|:--|:--|:--|
| ECS/module health | Brain, scheduler, maid, goslo-chat, orchestrator, crash/restart stats. | `/status` and systemd/process adapters. |
| L1.5 management | Source status, staged refs, node/ref lifecycle, import health. | DSG read adapters; new writes require approval. |
| L2-B visualization | Graph, nodes, edges, buckets, ref health, attention/lifecycle overlays. | DSG L2-B read APIs. |
| Photo management | Photo nodes, asset previews, staged refs, awareness linkage. | Photo upload/status + DSG/photo adapters. |
| Blackboard / IntentWorkspace / Plan | Real-time BB keys, workspace refs, plan state and step results. | Read-only adapters first. |
| Scheduler/Nanobot monitor | Queue, active tasks, results, worker/team status, failures. | Scheduler state + Nanobot result stream/status adapters. |
| Maid/GOSLO chat observability | Chatroom plan, bot presence, task summaries, collaboration traces. | Nanobot channel/session summaries; no raw secret exposure. |
| AgentTeam/MCP admin | Edit presets, MCP sets, apply config, restart instances. | Web-only business interface; core additions need approval. |

Web can own rich admin UX. App should receive only the stable preset choice and
safe status summaries.

## 6. Canvas Menu Rule

Both surfaces need canvas/menu awareness, but they render different products:

| Surface | Rendering goal | Must not do |
|:--|:--|:--|
| Unity App | Touch-first mobile/AR menu with compact confirmations and game/tool actions. | Do not add Web-only dashboard payloads to Unity DTOs. |
| Web Console | Dense operational visualization of menu registry, tier policy, BB state, and flows. | Do not make Web dashboard state the source of App runtime truth. |

The shared truth remains the menu registry, tier registry, RoomSetting
compatibility output, and orchestrator/runtime status.

## 7. Hot Switch Policy

| Change | V1 behavior | Notes |
|:--|:--|:--|
| Brain Persona / Room / Line | Tier 0/1 by existing registry; Line/Room cold-start or reconnect path. | Ner stays here. |
| Active Maid Team for future tasks | Can be hot if Scheduler only changes route for new tasks. | Running tasks continue on their original worker/team. |
| Nanobot workspace files | Usually next message/session reads updated bootstrap files. | Existing nanobot context builder reads workspace bootstrap files per prompt. |
| Nanobot provider/MCP/channel config | Restart required. | MCP connections and channels are process lifecycle concerns. |
| Nanobot instance group membership | Warm switch / rolling restart. | Add after CatMaid single-instance path is observable. |

## 8. Core Interface Candidates Requiring Approval

Do not implement these silently. Report them before editing core contracts:

| Candidate | Why |
|:--|:--|
| `agent_team_id` or `maid_team_id` on RoomProfile/RoomSetting effective selection | Lets App startup select the Maid Team and lets Web inspect it. |
| AgentTeam registry, e.g. `data/registries/agent_teams.json` | Stable list of team presets, labels, default nanobot instance group, capabilities, and restart tier. |
| Orchestrator read/apply endpoints for AgentTeam | Needed only when App/Web must change the active team through backend control. |
| `/status` extension for active AgentTeam and nanobot instance health | Needed for HUD badge and Web dashboard. |
| Scheduler task `agent_team_id` routing | Needed before multiple teams or per-team worker groups can run. |
| Nanobot/MCP admin business endpoints | Web-only; must not pollute App DTOs. |

## 9. Parallel Workstreams

| Workstream | Suggested branch | Write scope |
|:--|:--|:--|
| Shared interface prep | `codex/interface-app-web-routes` | `.cursor/memory/**`, `codex_workspace/**` only. |
| Unity App startup/game | `codex/app-startup-maid-team` | `unity/ArSpike/**`, App-side docs and examples. |
| Web console observability | `codex/web-console-observability` | `src/parrot/web_console/**`, `web/console/**`, Web-side docs. |
| Backend AgentTeam core | `codex/backend-agent-team-routing` | Only after user approval of the missing core surfaces above. |

## 10. Start Readiness

Ready now:

- App can begin startup UI, HUD, menu canvas rendering, game/tool surfaces, and
  a fixed `CatMaid Team` selector placeholder.
- Web can begin read-only console skeleton, `/status` dashboard, menu/tier
  visualization, and adapter-gap inventory.
- Scheduler and nanobot default path can remain single-team while UI surfaces
  are built.

Not ready without core additions:

- Dynamic AgentTeam list/apply.
- Multi-nanobot team routing.
- MCP edit/apply/restart flow in Web.
- Deep Plan/Nanobot live state if no clean read adapter exists yet.
