# Observability Runtime Business Flow (2026-05-13)

Owner: Web Console chat  
Status: approved  
Category: Web Console business interface  
Scope: ECS/module health, orchestrator status, Blackboard, IntentWorkspace, Plan/task, Scheduler, Nanobot, AgentTeam/Maid Team, GOSLO/Nanobot collaboration  
Updated: 2026-05-13  
Related TODO: WEB-002, WEB-004, WEB-005  
Sources: `src/parrot/castle/orchestrator/status.py`, `src/parrot/castle/orchestrator/server.py`, `src/parrot/scheduler/**`, `src/parrot/brain/intent_workspace.py`, `src/parrot/brain/plan/**`, `.cursor/memory/architecture/Interface/app_web_parallel_routes_agent_team_20260513.md`

## Slice: Runtime Observability

### A. Source Readback

- Orchestrator `/status` already aggregates runtime config, Brain runtime
  snapshot, selection drift, module heartbeats, container status, boot/crash
  hints, restart stats, and warnings.
- Scheduler uses py-trees and Blackboard routing; Nanobot results are consumed
  and fanned out through Scheduler/Brain paths.
- The App/Web route ratifies the AgentTeam boundary: Maid Team is logical,
  Nanobot instance is a concrete process, and V1 starts with a single default
  team path.

### B. Existing Core Interfaces

Yes for a read-only runtime console skeleton.

Initial composition:

- `GET /status` for ECS/module/process/container/runtime status.
- `PARROT_ORCH_SECRET` controls auth. If set, Web must send
  `Authorization: Bearer <secret>`; if unset, the route is dev-open.
- `AppFirstVersionFacade.canvas_snapshot()` and current monitor adapters can
  seed module cards, paper notes, photo refs, Blackboard, IntentWorkspace, and
  L2-B visibility while a dedicated Web BFF is still thin.
- Scheduler/Plan state can start as read adapters over existing in-process
  registries and Blackboard snapshots.
- Backend menu tables and ECS/module categories should be upgraded as read
  models before Web adds strong process controls.

### C. Missing Core Surface

Read-only Web implementation can begin without changing core SSOT.

Shared or policy-changing gaps are already candidates:

| Candidate | Why Web needs it | Current route |
|:--|:--|:--|
| CORE-001 | Show or select effective `agent_team_id` / `maid_team_id`. | Candidate queue only. |
| CORE-002 | Render a stable AgentTeam registry. | Candidate queue only. |
| CORE-003 | Show active AgentTeam and backing nanobot health in `/status`. | Candidate queue only. |
| CORE-004 | Monitor or route Scheduler tasks by AgentTeam. | Candidate queue only. |
| CORE-005 | Design Web-only Nanobot/MCP admin APIs without polluting App DTOs. | Business interface first. |

Web-only read adapters under a future `src/parrot/web_console/` package do not
become core contracts unless App, Scheduler, or Brain also need the exact
surface.

### D. Observable Completion Signal

- Web loads `/status` and clearly distinguishes connected, degraded, offline,
  unauthorized, and dev-open states.
- Module health shows module id, heartbeat freshness, module type, layers,
  runtime config, selection drift, restart/crash hints, and warnings.
- Blackboard and IntentWorkspace views show scoped keys/refs with empty states
  instead of crashing when py-trees or Redis is absent.
- Plan/task view lists draft, awaiting confirmation, executing, completed,
  failed, cancelled, and revised states when registry data is available.
- Scheduler/Nanobot view shows queue/active/result/timeout signals from
  current adapters or clear "adapter missing" placeholders.
- AgentTeam/Maid Team view shows the fixed `CatMaid Team` V1 placeholder until
  CORE-001/002/003 are confirmed.
- GOSLO/Nanobot collaboration view shows safe task summaries, presence/status,
  and result traces without exposing raw secrets or upstream channel internals.
- Task dispatch, trigger fire/manage, chatroom summaries, and message send
  affordances are allowed as Web operator workflows only after they produce
  drafts/receipts and are separated from App DTOs.

### Implementation Signal: 2026-05-13

Done for WEB-002 skeleton:

- BFF: `src/parrot/web_console/server.py`
- Static frontend: `web/console/index.html`, `web/console/assets/styles.css`,
  `web/console/assets/app.js`
- Launcher: `src/scripts/start_web_console.py`
- Tests: `tests/test_web_console/test_web_console_server.py`
- Local run verified at `http://127.0.0.1:7893/`

Current behavior:

- `GET /api/console/config` exposes orchestrator URL/auth mode without leaking
  `PARROT_ORCH_SECRET`.
- `GET /api/orchestrator/status` proxies orchestrator `/status` through the
  server-side BFF and injects `Authorization: Bearer <secret>` when
  `PARROT_ORCH_SECRET` is available in the Web Console process.
- The frontend renders connection, modules, warnings, selection drift, runtime
  config, brain snapshot, containers, and warnings in the Obsidian-like console
  layer.
- The frontend now includes a visual status topology, visual module heartbeat
  placeholders, and a settings dialog with English/Chinese language switching.
- Verified desktop and mobile screenshots with headless Edge. Current local
  orchestrator run returns `/status` 200 through the BFF, while the console
  correctly marks the system `degraded` because Redis/Blackboard/Brain live
  data is absent in this local session.

## Console Control Scope

The first shell is observability-heavy, but it should leave clear slots for
controlled interaction:

- ECS/module health: categorize modules by layer, owner, process/container,
  heartbeat freshness, restart tier, and menu visibility.
- Scheduler monitor: queue, active task, result, timeout, retry, cancellation,
  manual dispatch draft, and trigger history.
- Blackboard/IntentWorkspace: scoped key/ref browser, safe value preview,
  source owner, freshness, and mutation-blocked labels until a safe operator
  action exists.
- GOSLO/Nanobot/Maid collaboration: presence, room/session summary, task
  messages, result receipts, chatroom/channel plan, and audit-safe message send
  drafts.
- Process controls: restart/apply/config edits stay explicit Web operator mode,
  not default dashboard buttons.

## Operator Boundary

Runtime restart/apply controls are not part of the read-only skeleton. When
they are added, Web must separate:

- shared orchestrator controls that App may also consume;
- Web-only operator controls such as MCP edit/apply, nanobot config editing,
  and process surgery;
- dry-run/confirmation/audit output for any non-read action.
