# Observability Runtime Business Flow (2026-05-13)

Owner: Web Console chat  
Status: in_progress
Category: Web Console business interface  
Scope: ECS/module health, orchestrator status, Blackboard, IntentWorkspace, Plan/task, Scheduler, Nanobot, AgentTeam/Maid Team, GOSLO/Nanobot collaboration  
Updated: 2026-05-13  
Related TODO: WEB-002, WEB-004, WEB-005, WEB-009, WEB-012
Sources: `src/parrot/castle/orchestrator/status.py`, `src/parrot/castle/orchestrator/server.py`, `src/parrot/scheduler/**`, `src/parrot/brain/intent_workspace.py`, `src/parrot/brain/plan/**`, `.cursor/memory/architecture/Interface/app_web_parallel_routes_agent_team_20260513.md`

## 2026-05-13 Direction Update: Runtime Flow Workspace

The old Runtime Monitor remains useful as a read source, but the next formal
Web Console surface is a React + Vite Runtime Flow Workspace. It is separate
from the Memory Graph Workspace.

Runtime Flow owns:

- GOSLO Intent, Plan, HITL gates, Blackboard, IntentWorkspace, Scheduler,
  Nanobot, messages, manual triggers, and receipts.
- A swimlane/DAG renderer where one operator can follow:
  `Intent -> Plan -> Human Gate -> Scheduler -> Nanobot -> Result ->
  Blackboard/IntentWorkspace -> Trigger/Message/Graphiti`.
- A bottom event tape and right-side detail/action drawer instead of stacked
  raw panels.
- Web-only read model routes first: `GET /api/runtime/flow` and
  `GET /api/runtime/flow/changes?since=...`.
- HITL V1 routes: pending gates, decision draft, and decision apply. Default
  behavior is dry-run/operator-safe.

This is a Web business interface until App/Web confirm shared consumers. New
shared surfaces are staged in the core candidate queue, not promoted directly
to `.cursor/memory/architecture/Interface/**`.

### Runtime Flow Route Matrix

| Endpoint | Mode | Purpose | Core status |
|:--|:--|:--|:--|
| `GET /api/runtime/flow` | read | Build lanes, nodes, edges, events, receipts, and pending HITL gates from existing runtime monitors and registries. | Implemented Web-only first; candidate CORE-010 if shared. |
| `GET /api/runtime/flow/changes?since=<sequence>` | read | Return bounded changed-since polling diff for active React workspaces. V1 returns the full snapshot/events when the sequence advances. | Implemented Web-only first; extends CORE-009 candidate if shared. |
| `GET /api/runtime/hitl/pending` | read | List pending human gates for Plan confirmation actions. | Implemented Web-only first; candidate CORE-011 if shared. |
| `POST /api/runtime/hitl/draft-decision` | draft | Validate approve/reject/revise/cancel/resume decisions and return receipt. | Implemented Web-only operator BFF first. |
| `POST /api/runtime/hitl/apply-decision` | dry-run/operator | Apply a decision only under explicit operator mode; default request path is dry-run. | Implemented Web-only operator BFF first. |

### Backend Capability Status

- Done in the first WEB-012 backend slice:
  `PlanRegistry.start_executing()` dispatches ready steps through an injectable
  dispatch function, and dispatched tasks carry `plan_id`, `step_id`, and a
  result channel.
- Done in the first WEB-012 backend slice:
  Scheduler Nanobot result and timeout paths call back into the Plan registry
  when task metadata contains `plan_id` and `step_id`.
- Fixed in the WEB-012 backend slice:
  Plan dispatch exceptions now fail the affected step and Plan instead of
  leaving the step stuck in `DISPATCHED` with an error string.
- Fixed in the review pass:
  Plan step dispatch now validates the Scheduler Nanobot task catalog before
  dispatch. Unsupported tool types fail the Plan immediately instead of being
  routed outside the Plan result/timeout return path.
- Fixed in the review pass:
  Runtime Flow changed-since now uses a stable content signature, so a no-op
  poll can return `changed=false`; HITL decision drafts reject missing Plan ids;
  empty Plans complete on start instead of staying in `executing`; and dangling
  graph edges are pruned before the React Flow Runtime renderer receives the
  snapshot.
- Done in Web-only V1:
  HITL pending/draft/apply routes expose Plan confirmation decisions without
  promoting a shared App DTO.
- Remaining gap:
  durable cross-process runtime trace and human-gate DTOs are not yet ratified.
  They remain CORE-010 and CORE-011 until App/Web lane confirmation.

### Implementation Signal: WEB-012 React Runtime Flow First Slice

Date: 2026-05-13

Implemented code:

- `src/parrot/web_console/runtime_flow.py`
- Runtime/HITL route mounts in `src/parrot/web_console/server.py`
- Plan dispatch upgrade in `src/parrot/brain/plan/plan_registry.py`
- Scheduler result/timeout return path in `src/parrot/scheduler/service.py`
- React workspace in `web/console_app/`
- Built static output in `web/console_dist/`

Runtime Flow data model V1:

- `sequence` and `generated_at` identify the snapshot.
- `lanes` describe the visual swimlanes.
- `nodes` and `edges` are graph-renderer read models, not core DTOs.
- `events` is a bounded event tape for recent runtime facts.
- `pending_human_gates` lists Web-reviewable Plan gates.
- `audit` marks the model as Web-only and points at CORE-010/CORE-011.

HITL V1 decisions:

- `approve`: draft/receipt path for accepting a pending gate.
- `approve_and_start`: dry-run or operator-gated transition toward execution.
- `reject`: mark the gate rejected.
- `revise`: capture revision text as the next operator instruction.
- `cancel`: cancel the target plan.
- `resume`: resume a paused/revised plan when explicitly allowed.

Boundary:

- No Unity/App DTOs changed.
- No `.cursor/memory/architecture/Interface/**` file changed.
- The routes are Web BFF interfaces until the user and both lanes approve a
  shared runtime-flow or human-gate contract.

Verification:

- `uv run pytest tests\test_brain\test_plan_lifecycle.py tests\test_web_console\test_web_console_server.py tests\test_dsg\test_obsidian_true_connection.py tests\test_dsg\test_calendar_true_connection.py tests\test_dsg\test_trigger_outcome_v2.py -q`
  -> `46 passed`.
- `uv run python -m py_compile src\parrot\web_console\runtime_flow.py src\parrot\web_console\server.py src\parrot\brain\plan\plan_registry.py src\parrot\scheduler\service.py`
- `cd web\console_app; npm run typecheck`
- `cd web\console_app; npm run build`
- Browser smoke: React Runtime Flow served on `http://127.0.0.1:7893/`,
  manual LLM trigger draft produced a receipt, zh/en toggle worked, and browser
  console errors stayed at zero.
- HTTP smoke after the review fixes:
  `/api/runtime/flow/changes?since=<current sequence>` returned
  `changed=false`.

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
  placeholders, breathing status lights, a simplified overview-first home
  screen, collapsed detail sections for raw/complex data, and a settings dialog
  with English/Chinese language switching.
- Verified desktop and mobile screenshots with headless Edge. Current local
  orchestrator run returns `/status` 200 through the BFF, while the console
  correctly marks the system `degraded` because Redis/Blackboard/Brain live
  data is absent in this local session.

Extension for WEB-009:

- Local `.env` now holds `PARROT_ORCH_SECRET`; `src/scripts/start_web_console.py`
  and `python -m parrot.castle.orchestrator` both load `.env` for local
  developer runs. The secret is a static bearer value, not a time-expiring
  token; rotate it by changing the env/file value and restarting services.
- BFF added App/LineB/Menu smoke routes:
  `/api/app/canvas`, `/api/app/modules`, `/api/app/line-profiles`,
  `/api/app/line-profiles/apply`, `/api/app/workspace/apply`,
  `/api/app/lineb/audio-route`, `/api/app/lineb/tts-segment`,
  `/api/app/lineb/mic-input`, and `/api/app/live-state`.
- BFF also added Web-side LiveKit join-token support:
  `/api/livekit/config` and `/api/livekit/web-token`. The route mints a
  short-lived browser participant token server-side and does not expose
  `LIVEKIT_API_SECRET` to the frontend; the UI stores the token only for the
  current browser session and renders redacted token metadata.
- Static frontend is split into three Web places instead of one crowded page:
  `Ops Health`, `LineB Voice`, and `Menu Canvas`.
- The LineB Voice place now includes browser LiveKit audio client wiring:
  `Connect Audio` loads the LiveKit JS SDK, joins the configured room with the
  BFF-minted token, starts browser audio, publishes the local microphone, and
  attaches remote audio tracks to hidden audio elements. This stays Web-only
  and does not add any fields to App DTOs.
- LineB Voice also renders Web-local LiveKit event panes: token mint,
  connect, signal reconnect, full reconnect, disconnect, remote audio attach,
  `TranscriptionReceived`, and `lk.transcription` data-topic messages. These
  panes are current-browser observability only; persistent conversation history
  remains owned by Graphiti/DSG archive flows.
- Browser-verified control-path smoke:
  LineB no-video route applies through the BFF, simulated mic/asr input returns
  `user_turn`, LineB profile selection stays on active LineB profiles only,
  LiveKit Web token mint returns a redacted UI receipt with no raw JWT in the
  page, Menu Canvas renders module/tool/workspace nodes, and workspace apply
  can switch the visible canvas state.
- Boundary: automatic browser verification did not click `Connect Audio`
  because that requests microphone permission and transmits the short-lived
  LiveKit token to the configured room. Real no-video conversation verification
  still requires an explicit user-approved mic permission click plus a running
  server-side LineB/LiveKit Agents session.

Extension for WEB-004 / WEB-005:

- Web BFF added `/api/runtime/monitor` through
  `src/parrot/web_console/runtime_monitor.py`. This is a Web-only read model;
  it does not promote Scheduler internals, Nanobot worker details, or AgentTeam
  placeholders into App DTOs or the shared core SSOT.
- Static frontend now has a dedicated `Runtime Monitor` view separate from the
  simplified Ops home screen. It renders Scheduler route order/channels/task
  types/active tasks, Nanobot report bridge state, Plan counts/list rows,
  Blackboard declared/present summary, and the V1 fixed `CatMaid Team`
  placeholder.
- GOSLO/Nanobot collaboration is shown as safe channel/status topology:
  Scheduler command channel -> Nanobot dispatch stream -> Nanobot result
  channel -> Scheduler-to-Brain return. Chatroom/message-send/admin controls
  remain future Web operator workflows that need draft/receipt/audit handling.
- The collaboration topology now has a Web-only `channel_flow` read model and a
  visual flow renderer: Scheduler Commands -> Nanobot Dispatch -> Nanobot
  Worker -> Nanobot Results -> Brain Return. Each stage carries channel/status
  summary only; raw channel admin remains out of the browser.

Extension for Plan DAG rendering:

- `src/parrot/web_console/runtime_monitor.py` now includes Web-only Plan DAG
  data in `/api/runtime/monitor`: step dependencies, started/completed
  timestamps, result refs, related node/ref ids, staged ref id, blackboard
  namespace, and a bounded `dag.nodes` / `dag.edges` shape.
- The frontend Runtime Monitor renders each Plan as a compact phase/step DAG
  when steps exist, while keeping Scheduler/Nanobot/Plan internals read-only.
- The Plan DAG read model now also includes bounded step hints:
  `ready_step_ids`, `blocked_step_ids`, and `critical_step_ids`. The frontend
  marks ready/blocked/critical nodes, emphasizes selected edges, and lets the
  operator click a step to inspect expected tool, Nanobot task id, dependencies,
  result ref/summary, timestamps, and errors.
- This stays a Web read adapter. It does not promote py-trees internals,
  Nanobot task payloads, or Plan UI DTOs into the App lane.

Extension for Trigger Lab and Gmail message smoke:

- Web BFF added the trigger management surface:
  `GET /api/dsg/triggers/catalog`, `POST /api/dsg/triggers/draft-event`, and
  `POST /api/dsg/triggers/fire-event`.
- The route catalog reads registered DSG triggers and exposes kind/interval and
  sample event hints. Draft/fire returns a receipt with matched trigger names.
  Real fire publishes to `CH_DSG_EVENTS` only when `dry_run=false` and
  `operator_mode=true`; it does not instantiate or call Brain trigger singletons
  inside the Web process.
- Web BFF added `POST /api/google/messages/check` and
  `POST /api/google/messages/push-test`. The check route drafts/dispatches
  Scheduler `message_check` work for Nanobot Google Workspace/Gmail MCP; the
  push-test route drafts/publishes a synthetic `message_push` DSG event.
- Frontend Runtime Monitor now has a collapsed Trigger Lab with trigger catalog,
  editable event JSON, draft/fire dry-run buttons, Gmail check dry-run, message
  push dry-run, and receipt output.
- Audit note: `MessageNotificationTrigger` still writes message EVENT nodes
  directly to L2-B internally. This is a known backend drift from Calendar and
  Obsidian, which use L1.5/TriggerOutcome commit paths. The next backend pass
  should migrate it to `TriggerOutcome.commit_observations` or add an equivalent
  receipt/audit boundary.

### Interface Matrix: Trigger Lab And Message Checks

Checkpoint: 2026-05-13. These are Web-only operator-safe business interfaces.
They exist to test trigger routing and Nanobot message dispatch without giving
the browser direct Gmail OAuth, direct Brain trigger singletons, or raw Redis
admin access.

| Endpoint | Purpose | Backend adapter | Safety rule |
|:--|:--|:--|:--|
| `GET /api/runtime/monitor` | Read Scheduler, Nanobot, Plan DAG/hints, Blackboard, AgentTeam placeholder, and collaboration channel flow. | `build_runtime_monitor_snapshot()` | Read-only Web monitor. |
| `GET /api/dsg/triggers/catalog` | Show trigger name/kind/interval and sample event hints. | `trigger_catalog()` | Read-only trigger discovery. |
| `POST /api/dsg/triggers/draft-event` | Draft an event envelope and list likely matched triggers. | `draft_trigger_event()` | Draft only; no Redis publish. |
| `POST /api/dsg/triggers/fire-event` | Publish a DSG event for the running trigger listener. | `fire_trigger_event()` -> `CH_DSG_EVENTS` | Default dry-run; real publish requires `operator_mode=true` and `dry_run=false`. |
| `POST /api/google/messages/check` | Draft/dispatch Nanobot Gmail/Workspace `message_check`. | `dispatch_message_check()` -> Scheduler dispatch | Default dry-run; browser never holds Gmail credentials. |
| `POST /api/google/messages/push-test` | Draft/publish a synthetic `message_push` event. | `push_test_message()` -> trigger event path | Default dry-run; real event requires operator mode. |

Current drift / fix target:

- `CalendarTrigger` and Obsidian ingestion produce `TriggerOutcome`
  upload-channel data that the runner can commit through L1.5.
- `MessageNotificationTrigger` still creates message EVENT nodes with direct
  `self._graph.upsert_node(...)`. This should be refactored to return
  `commit_observations` or a comparable audited receipt so Web message tests
  exercise the same path as Calendar/Obsidian.

### Investigation: Runtime Visual Rendering Interfaces

Checkpoint: 2026-05-13. Runtime data is present enough for visual grouping, but
not yet shaped as an operator-grade live canvas.

Existing fields:

- Scheduler exposes route order, destinations, Redis channels, Nanobot task
  types, best-effort active tasks, and channel-flow stage summaries.
- Nanobot exposes module status, busy flag, report count, last active time,
  report refs, dispatch stream, and result channel.
- Plans expose active/archive counts, current plan, state counts, compact step
  rows, dependency edges, and Web-only ready/blocked/critical step hints.
- Blackboard summary exposes declared/present counts and present keys by scope.
- Collaboration summary exposes Scheduler command channel, Nanobot dispatch
  stream, Nanobot result channel, Brain return channel, and high-level chatroom
  boundary.

Next Web-only interface work:

1. Add receipt drawers for recent dispatch/result summaries once the worker
   exposes bounded result receipts.
2. Evaluate whether Plan/Blackboard need a durable `changed_since` or SSE lane
   after the polling DAG/activity views prove useful.
3. Keep chatroom/message-send/admin controls draft/receipt-first; do not expose
   raw channel internals or credentials in the UI.

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

## Requirement Reframe: WEB-011 Runtime Flow And Trigger Palette

Owner chat: Web Console
Status: approved
Related TODO: WEB-011
Research anchors: React Flow interaction model, Cytoscape.js subgraph/compound
layouts, py-trees Blackboard activity model, Nanobot task/cron/worker patterns.

### Requirements Captured

- Runtime Monitor should not remain a dense list of mini panels. It needs a
  visual flow workspace for Scheduler, Nanobot, Plan/task, Blackboard activity,
  IntentWorkspace refs, and Brain return flow.
- Plan/task visualization should be a larger DAG/timeline workspace, with
  phase/step nodes, ready/blocked/critical styling, dependencies, Nanobot task
  ids, result refs, and receipt history.
- Blackboard should show a live activity/ownership view: scope, writer,
  key state, reads/writes, event-driven keys, recent changes, and links to
  plans/intents where current data supports it.
- IntentWorkspace should be shown as active intent/ref groups with owner,
  role, expiry/pressure, related node/ref ids, and visible connections to
  L2-B or Plan steps.
- Trigger controls should be manual buttons, not only editable JSON:
  `message_push`, `message_check`, `llm_context_push`, Calendar test,
  Obsidian setting node, Graphiti episode, and custom DSG event draft/fire.
- Manual trigger fire must remain receipt-first: draft, match triggers,
  dry-run receipt, optional operator execution. The browser must not directly
  call Brain trigger singletons or hold Google/LiveKit/server secrets.

### Implementation Order

1. Keep `/api/runtime/monitor` as the polling read model while the visual
   workspace is being shaped.
2. Turn the current channel-flow strip into a large visual Runtime Flow page:
   Scheduler Commands -> Nanobot Dispatch -> Nanobot Worker -> Results ->
   Brain/Blackboard/IntentWorkspace.
3. Move Plan DAG into the large workspace, not a compact row-only card.
4. Add a trigger palette with safe preset buttons and receipt timeline.
5. Add recent dispatch/result receipt drawers once Scheduler/Nanobot exposes
   bounded receipt summaries.
6. Evaluate `changed_since` or SSE only after the visual model is useful;
   promote to core only if App also needs the same runtime event stream.

### Audit Notes

- WEB-011 does not add Unity/App DTO requirements.
- Message/Gmail actions stay through Scheduler/Nanobot paths, not browser
  OAuth.
- Raw channel administration, process restart, or config surgery remain
  Web-only operator flows and must use dry-run/audit receipts.

### Implementation Round: WEB-011.5 First Trigger Palette

Status: in_progress

Changed in this slice:

- Moved common trigger actions out of the raw Trigger Lab drawer and into a
  visible Runtime trigger palette.
- Added preset buttons for `message_check`, `message_push`,
  `llm_context_push`, `scheduler_tick`, `calendar_event`, and
  `web_console_custom`.
- Message actions still use the existing Nanobot/Web routes:
  `POST /api/google/messages/check` and `POST /api/google/messages/push-test`.
- LLM/scheduler/calendar/custom presets write the raw event textarea and call
  `POST /api/dsg/triggers/draft-event`, so the browser still receives a safe
  draft receipt rather than calling Brain trigger singletons.

Verification:

- `node --check web\console\assets\app.js`
- Duplicate `id="..."` scan for `web/console/index.html`: clean.
- In-app browser Runtime smoke:
  trigger palette is visible, the LLM context push preset returns a receipt,
  and no console errors are reported.

Remaining work:

- Add grouped catalog-driven trigger buttons once the catalog shape is rich
  enough for stable labels.
- Add a receipt timeline instead of a single receipt block.
- Add explicit operator execution copy before any non-dry-run fire path.
