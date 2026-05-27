# Observability Runtime Business Flow (2026-05-13)

Owner: Web Console chat  
Status: in_progress
Category: Web Console business interface  
Scope: ECS/module health, orchestrator status, Blackboard, IntentWorkspace, Plan/task, Scheduler, Nanobot, AgentTeam/Maid Team, GOSLO/Nanobot collaboration  
Updated: 2026-05-15
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
| `GET /api/runtime/flow/stream?since=<sequence>` | read/SSE | Stream the same bounded changed-since envelope as `runtime_flow_delta_v1` events for the active React Runtime page. It is a read-only EventSource surface and keeps operator receipts separate. | Implemented Web-only first; extends CORE-009/CORE-010 candidate only if shared. |
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
- Fixed in the 2026-05-14 CORE-010/011 review pass:
  Runtime Flow nodes/edges/events now carry Web-only `trace_id` and
  `payload_ref` hints where available, duplicate graph ids are normalized, and
  HITL decision drafts validate the requested action against the current Plan
  state before returning a success receipt.
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
- `nodes` and `edges` are graph-renderer read models, not core DTOs. `source`
  and `target` on edges are graph endpoint ids; they are not the same field as
  event `source`.
- `trace_id` and `payload_ref` on nodes/edges/events are Web-only CORE-010
  hints. Current strongest trace is `plan:<plan_id>` across Plan, step,
  Scheduler, and Nanobot queue edges when Plan metadata is present.
- `events` is a bounded event tape for recent runtime facts. Its shape mirrors
  trace/span vocabulary (`trace_id`, `span_id`, `parent_span_id`,
  `entity_kind`, `entity_id`, `op`, `status`, `source`, `writer`, `summary`,
  `created_at`, `payload_ref`) but remains Web-only until CORE-010 is approved.
- `pending_human_gates` lists Web-reviewable Plan gates. Its V1 fields are
  `gate_id`, `target_kind`, `target_id`, `trace_id`, `state`, `prompt`,
  `summary`, `plan_state`, `options`, `valid_actions_for_state`,
  `operator_required_for_execute`, `created_at`, `expires_at`, and
  `payload_ref`.
- `audit` marks the model as Web-only and points at CORE-010/CORE-011.

HITL V1 decisions:

- `approve`: draft/receipt path for accepting a pending gate.
- `approve_and_start`: dry-run or operator-gated transition toward execution.
- `reject`: mark the gate rejected.
- `revise`: capture revision text as the next operator instruction.
- `cancel`: cancel the target plan.
- `resume`: resume a paused/revised plan when explicitly allowed.

HITL draft receipts now include `plan_state` and, on invalid state/action
pairs, `valid_actions_for_state`. Apply receipts include `plan_state_after`
when execution succeeds. These fields are useful for Web operator safety, but
remain CORE-011 candidates rather than shared App DTO fields.

2026-05-14 review note:

- Pending gate `options` now come from the same Plan-state policy as
  draft/apply validation, so the UI should not display impossible decisions.
- Non-Plan gate targets, for example `trigger:<id>` and `message:<id>`, return
  `unsupported_hitl_target` until their backend state transitions and receipts
  are explicitly implemented. They must not be promoted as shared CORE-011
  targets yet.
- React Runtime Flow now consumes the gate `options` field for button rendering
  instead of hard-coding approve buttons. The UI also shows the configured
  refresh interval and keeps Runtime graph positions lane-local for easier
  scanning.
- React Runtime Flow now reads the existing `GET /api/dsg/triggers/catalog`
  route and renders registered trigger chips grouped by kind. This keeps the
  manual dry-run palette aligned with the real trigger registry without adding
  a new Web route or calling Brain trigger singletons from the browser.
- Runtime trigger group headings are localized through the same zh/en copy table
  as the rest of the console. Runtime action and HITL request failures now
  create local failure receipts, keeping the operator audit trail visible even
  when a BFF call fails.

2026-05-14 typed schema upgrade result:

- WEB-012.15 added a Web-only typed schema layer in
  `parrot.web_console.runtime_flow_models` for Runtime Flow rows, snapshots,
  changed-since envelopes, HITL gates, and receipts. The route JSON stays
  compatible with the React console.
- CORE-010 remains a candidate read model. The implementation may clarify the
  event writer field internally, but graph edge `source` / `target` must remain
  route-compatible React Flow endpoints.
- CORE-011 remains limited to Plan HITL gates. HITL receipts now expose
  `core_candidate=CORE-011` when relevant. Trigger/message targets keep
  explicit `unsupported_hitl_target` receipts until their backend state
  machines are designed.
- 2026-05-16 realtime slice adds Web-only Runtime Flow SSE:
  `GET /api/runtime/flow/stream`. It wraps the same
  `runtime_flow_delta_v1` changed-since envelope as
  `/api/runtime/flow/changes`, emits `stream_open` / `runtime_delta` /
  `stream_close`, and does not dispatch Scheduler tasks, mutate Blackboard, or
  send Nanobot messages.
- React opens the Runtime SSE stream only while the Runtime Flow page is active
  and falls back to polling if EventSource fails. Receipt/history streams stay
  separate from this read model.
- This slice does not create WebSocket and does not add App/Unity DTOs.

Boundary:

- No Unity/App DTOs changed.
- No `.cursor/memory/architecture/Interface/**` file changed.
- The routes are Web BFF interfaces until the user and both lanes approve a
  shared runtime-flow or human-gate contract.

Verification:

- `uv run pytest tests\test_brain\test_plan_lifecycle.py tests\test_web_console\test_web_console_server.py tests\test_dsg\test_obsidian_true_connection.py tests\test_dsg\test_calendar_true_connection.py tests\test_dsg\test_trigger_outcome_v2.py -q`
  -> `48 passed`.
- `uv run python -m py_compile src\parrot\web_console\runtime_flow.py src\parrot\web_console\runtime_flow_models.py src\parrot\web_console\server.py src\parrot\brain\plan\plan_registry.py src\parrot\scheduler\service.py`
- `cd web\console_app; npm run typecheck`
- `cd web\console_app; npm run build`
- Browser smoke: React Runtime Flow served on `http://127.0.0.1:7893/`,
  manual LLM trigger draft produced a receipt, zh/en toggle worked without
  mojibake, and browser console errors stayed at zero.
- React trigger-catalog smoke: Runtime page showed registered trigger chips,
  including `event_driven` and `on_demand`, next to the manual Message/Runtime/
  Mode action groups; browser console errors stayed at zero.
- Bugfix smoke: zh mode showed localized action groups (`消息`, `运行`, `模式`),
  the LLM dry-run button produced a `dsg.trigger.draft_event` receipt, and
  browser console errors stayed at zero.
- HTTP smoke after the typed schema upgrade:
  `/api/runtime/flow` returned
  `typed_schema=parrot.web_console.runtime_flow_models`; non-Plan HITL draft
  returned `unsupported_hitl_target` with `core_candidate=CORE-011`; and
  `/api/runtime/flow/changes?since=<current sequence>` returned
  `changed=false`.
- 2026-05-16 Runtime SSE verification:
  `tests\test_web_console\test_web_console_server.py` -> `49 passed`;
  `npm run typecheck`; `npm run build`; and `py_compile` for
  `server.py`, `runtime_flow.py`, and `runtime_flow_models.py`.
- Browser smoke after local service restart:
  Runtime page showed `实时 / SSE · LIVE`, the Runtime navigation opened
  cleanly, and browser console errors stayed at zero.

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
- Static frontend: legacy skeleton in `web/console/index.html` and
  `web/console/assets/*`; WEB-012 formal React build in `web/console_dist/`
  is served first when present.
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
- React Runtime Flow now has a formal `LiveKit / Brain Bridge` panel. It
  calls the same BFF token routes, joins the configured room without requiring
  a camera, attaches remote agent audio, records connection/transcript events,
  and can publish browser screen share as the `web-console-screen` track. This
  is the no-camera laptop path for LineB/Web voice and evidence smoke.
- The React bridge also has a read-only `检查采样` smoke button. It calls
  `GET /api/vision/evidence/screen-share-smoke`, which checks sampler status,
  frame-cache freshness, nearest stored evidence near `now`, and whether the
  latest/nearest evidence carries a screen-share source hint. The route returns
  the receipt directly and does not write pending `EVIDENCE_REQUEST` rows when
  the smoke fails.
- Bugfix note: this smoke receipt must not mark a generic fresh camera/test
  frame as a successful screen-share verification. Success now requires both
  freshness and a screen-share-looking source (`web-console-screen`,
  `screenshare`, `screen_share`, or compatible metadata) on the same candidate
  row. Otherwise a stale screen-share status plus a fresh camera frame could
  pass by accident. Failed checks return a warning-style server receipt with
  separate `fresh_any_evidence`, `likely_screen_share`, `fresh_screen_share`,
  and `screen_share_confirmed` fields.
- Realtime usability note: the Runtime Time/Evidence panel now polls
  `/api/vision/evidence/status` and `/api/vision/evidence/timeline` every 3s
  while the Runtime page is mounted. Poll failures are silent to avoid flooding
  the receipt rail. Screen-share start and `检查采样` also poke the evidence
  panel, so sampler/frame-cache freshness is visible without a manual page
  refresh.
- 2026-05-15 usability follow-up: `检查采样` now renders its server verdict
  inline inside `LiveKit / Brain Bridge` as a compact diagnostic card. It shows
  ready/not-ready, fresh evidence, screen-source match, fresh screen frame,
  sampler/frame-cache counts, and server `next_steps`; failed smoke therefore
  explains whether the blocker is missing screen-share permission, absent Brain
  sampler, stale frames, or non-screen evidence.
- Security posture for the React bridge: the short-lived token stays in
  component state only, receipts render token length/metadata instead of the
  raw token, and the browser LiveKit SDK log level is reduced to warning so
  diagnostics do not echo join-token payloads or long connection parameters.
- Browser-verified control-path smoke:
  LineB no-video route applies through the BFF, simulated mic/asr input returns
  `user_turn`, LineB profile selection stays on active LineB profiles only,
  LiveKit Web token mint returns a redacted UI receipt with no raw JWT in the
  page, Menu Canvas renders module/tool/workspace nodes, and workspace apply
  can switch the visible canvas state.
- Browser-verified LiveKit room smoke on 2026-05-15: the React bridge minted a
  Web token, joined the configured room, reached `connected`, and subscribed to
  a remote `agent-* / audio / microphone` track. That proves the Web browser
  can see the Brain/LiveKit Agent when it is in the same room. The smoke then
  disconnected cleanly. It did not click microphone or screen-share permission
  prompts; those remain explicit user-approved actions.
- Sampler follow-up on 2026-05-15: `parrot.brain.vision.livekit_sampler` now
  accepts LiveKit screen-share source spellings such as `SOURCE_SCREEN_SHARE`
  in addition to name hints like `web-console-screen`, and its latest-frame
  summaries include `publication_source` so the Web receipt can distinguish
  screen-share evidence from generic camera evidence.
- Research pass on 2026-05-15:
  - LiveKit's current screen-share guide recommends JS
    `room.localParticipant.setScreenShareEnabled(true)` and describes screen
    share as a normal published video track. Follow-up implementation now uses
    `setScreenShareEnabled(true)` when available and falls back to
    `getDisplayMedia()` + `publishTrack(track, { source, name })` for older
    clients. The fallback remains more dependent on source/name metadata
    staying consistent.
  - LiveKit Python docs expose `VideoStream.from_track()` /
    `VideoStream.from_participant()` and `VideoFrameEvent.timestamp_us`, so the
    current Brain sampler design can keep media-time evidence without using
    Gemini's hidden video-input frames.
  - LiveKit Agents video input can automatically receive camera/screen-share
    tracks, but the docs say only the single most recently published video track
    is used and frames are model input. Therefore `video_input=True` remains
    useful for conversation perception but not as an auditable evidence source;
    `frame_cache` / `TemporalEvidenceLedger` stays the canonical evidence path.
  - MDN documents that `getDisplayMedia()` requires transient user activation
    and permissions are not persisted. Therefore the final Web no-camera smoke
    cannot be fully automated by backend tests: the user must click screen
    share, choose a source, then run `检查采样`.
  - Source anchors:
    `https://docs.livekit.io/transport/media/screenshare/`,
    `https://docs.livekit.io/reference/python/livekit/rtc/video_stream.html`,
    `https://docs.livekit.io/agents/multimodality/vision/video/`,
    `https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getDisplayMedia`.
- Boundary: real no-video conversation verification still requires the user to
  approve browser microphone and/or screen share. If the server-side
  LineB/LiveKit Agents session is absent, the Web bridge can still join the
  room but will not receive `agent-*` tracks or transcript events.

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
- 2026-05-17 UI audit/fix: React Runtime Flow preset actions now share the
  top-level Settings `Mode`. Web Console is a test bench, so default Mode is
  real operator execution: `message_check` dispatches Scheduler/Nanobot work
  and trigger presets call `/api/dsg/triggers/fire-event` with
  `dry_run=false` and `operator_mode=true`. Switching Mode to preview keeps the
  same buttons on draft/dry-run paths. The browser still never owns Google OAuth
  or calls Brain trigger singletons directly.
- 2026-05-14 cleanup: `MessageNotificationTrigger` now returns
  `TriggerOutcome.commit_observations` with
  `ObservationSource.GOOGLE_MESSAGE`. Message EVENT nodes enter L2-B through
  L1.5/Ingest like Calendar and Obsidian. This removes the previous direct
  `self._graph.upsert_node(...)` drift.
- 2026-05-14 cleanup: `TriggerRunner.fire_event()` now routes both
  `EVENT_DRIVEN` and `ON_DEMAND` triggers. Web fire/draft remains receipt-first
  and still publishes only to `CH_DSG_EVENTS` for real operator execution, but
  scene/roleplay style on-demand triggers no longer require a private Web-side
  singleton call.

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
| `POST /api/google/calendar/fetch` | Draft/dispatch Nanobot Google Calendar `calendar_fetch`. | `dispatch_google_calendar_fetch()` -> Scheduler dispatch | Default dry-run; browser never holds Google OAuth; results return as `calendar_result` for `CalendarTrigger`. |
| `GET /api/google/calendar/results` | Read recent Scheduler fan-out rows for `calendar_result`. | `google_calendar_result_history()` -> `STREAM_TRIGGER_RESULTS` | Read-only Web observability; payloads are bounded and secret-redacted. |

Route defaults remain conservative if a raw caller omits execution fields, but
the React Web Console's global Settings `Mode` now defaults execute/fire/import
buttons to real operator testing. Preview Mode is the explicit way to force
those buttons back to dry-run receipts.

2026-05-15 Google Calendar sync note:

- Current runtime is manual/operator dispatch plus `CalendarTrigger` periodic
  polling. It is not yet Google push/watch realtime.
- Real fetch can work when Scheduler, Nanobot, Google Workspace MCP credentials,
  and the result listener are running. Web only sends the safe dispatch receipt.
- Scheduler now keeps a bounded `STREAM_TRIGGER_RESULTS` ledger when it fans
  Nanobot results to `CH_TRIGGER_RESULTS`, so Web can show recent Calendar
  result history without subscribing to Pub/Sub after the fact.
- Calendar cancelled/deleted rows use the WEB-014.15 historical tombstone
  policy: keep the Google identity and EVENT Node, set tombstone metadata, and
  lower L2-B confirmation/salience/attention so stale reminders stop without
  losing sync reconciliation state.
- Backend realtime should be server-side Google Calendar `watch` plus
  incremental syncToken storage. Web should observe the resulting
  `calendar_result` / L1.5 / L2-B changes via changed-since or future
  SSE/WebSocket, not browser OAuth.
- 2026-05-16 user decision: manual fetch/import with preview/operator receipt is
  enough for Google Calendar V1. Watch/syncToken moves to stage 2 after source
  import policy and SSE read streams are stable. Google Calendar itself does
  not require Redis; Redis is useful in this repo as the Scheduler/Nanobot
  cross-process result ledger and Web observability bus.

2026-05-23 Nanobot result content ownership note:

- A Nanobot result has two different products: a worker report/artifact and one
  or more trigger projections. The worker report is the Nanobot-facing summary
  and structured payload returned from Google Workspace/MCP/API work. Trigger
  projections are downstream interpretations such as Calendar/Gmail
  Observations, C3 status notices, safe-turn speech, and future Plan/archive
  requests.
- Triggers must not be treated as the owner of the original worker result and
  must not silently discard it after conversion. `TriggerOutcome` should project
  the result into `commit_observations`, `bucket_ops`, `staged_refs`,
  `plan_request`, or `notify_gemini`, while the original worker report remains
  available through a result artifact, a source locator, or a bounded receipt.
- For user-visible Google/Nanobot work (`calendar_fetch`, `message_check`, and
  later Calendar write tasks), the target contract is: compact event metadata
  enters L1.5/L2-B, notification text enters C3/safe-turn delivery only when
  policy allows, and the readable report/original locator is staged as an
  `IntentWorkspace` ref or 2D workdesk paper note. The App/Web 2D workdesk must
  be able to show a selectable Nanobot report/card rather than relying only on
  the trigger notification text.
- Current implementation status: Calendar read results are parsed by
  `CalendarTrigger` into L1.5/L2-B metadata and Web has a bounded
  `calendar_result` ledger. Gmail/message results are parsed by
  `MessageNotificationTrigger` into `GOOGLE_MESSAGE` metadata plus C3/speech
  policy. The 2D workdesk has a generic `stage_nanobot_report` / paper-note
  facility, but Scheduler/TriggerRunner do not yet automatically stage every
  user-visible Nanobot result into `IntentWorkspace`. This is an explicit
  product gap, not permission for triggers to drop worker content.
- Full Gmail bodies, OAuth tokens, and private mailbox payloads must not be
  copied into L2-B or Web snapshots by default. Preserve canonical originals as
  provider locators such as `gmail://<account>/<message_id>` or Gmail links, and
  let Nanobot/Google Workspace fetch expanded content on demand for GOSLO or
  the 2D workdesk under the existing credential boundary.
- Calendar EVENT lifecycle should preserve Google event status (`confirmed`,
  `tentative`, `cancelled`) and add Parrot lifecycle overlays such as
  `scheduled`, `tentative`, `cancelled_tombstone`, `expired`,
  `completed_manual`, or `postponed/rescheduled`. Google Tasks is a separate
  API with task statuses such as `needsAction` / `completed` and should not be
  silently merged into Calendar event status.

Current protocol status:

- `CalendarTrigger`, `ObsidianIngestTrigger`, `GosloCuriosityTrigger`, and
  `MessageNotificationTrigger` now produce `TriggerOutcome` upload-channel
  data that the runner can commit through L1.5.
- `SceneSwitchTrigger`, `RoleplayModeTrigger`, and similar on-demand triggers
  are reachable through the same `fire_event` router; their events use `kind`
  instead of the legacy scene-alert `type` field.
- `TriggerResult` remains a back-compat alias for legacy imports. It is not the
  preferred implementation style for new trigger code.
- 2026-05-14 source cleanup: DSG trigger implementations have been moved to
  import and construct `TriggerOutcome` directly; the remaining
  `TriggerResult` references are the compatibility/source-guard tests.

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
- React continuation expands the visible preset set to message check, message
  push, LLM context push, scheduler tick, calendar test, scene switch, and
  roleplay-open. Scene and roleplay presets use `kind=scene_switch` and
  `kind=roleplay_mode` to match the current on-demand trigger protocol.
- Message actions still use the existing Nanobot/Web routes:
  `POST /api/google/messages/check` and `POST /api/google/messages/push-test`.
- LLM/scheduler/calendar/custom presets write the raw event textarea and call
  `POST /api/dsg/triggers/draft-event`, so the browser still receives a safe
  draft receipt rather than calling Brain trigger singletons.
- React continuation replaces the single receipt block with a receipt timeline
  that summarizes matched triggers/errors first and keeps raw JSON available in
  the same card.

Verification:

- `node --check web\console\assets\app.js`
- Duplicate `id="..."` scan for `web/console/index.html`: clean.
- In-app browser Runtime smoke:
  trigger palette is visible, the LLM context push preset returns a receipt,
  and no console errors are reported.
- React browser smoke on `http://127.0.0.1:7893/`: Runtime trigger palette and
  scene-switch preset visible; LLM dry-run returns `dsg.trigger.draft_event`
  with matched trigger text; Chinese copy is readable; console errors remain
  zero.

Remaining work:

- Add grouped catalog-driven trigger buttons once the catalog shape is rich
  enough for stable labels.
- Add explicit operator execution copy before any non-dry-run fire path.

## 2026-05-15 Runtime Flow Responsibility Clarification

Owner: Web Console lane
Status: in_progress
Category: requirement / interface-boundary
Scope: WEB-012, CORE-010, CORE-011
Source: user clarification on Runtime Flow / collaboration-flow workspace

Runtime Flow is the whole-system collaboration workspace, not the L2-B graph
renderer and not the detailed Ref-file manager.

Primary responsibilities:

- Visualize GOSLO Intent -> Plan/HITL -> Blackboard -> IntentWorkspace ->
  Scheduler -> Nanobot -> Message/Trigger collaboration as lanes, DAGs, event
  tape, receipts, and later workflow nodes.
- Support manual Plan import as a receipt-first Web action.
- Support manual Nanobot task dispatch with an explicit result destination,
  for example `view_only`, `return_to_goslo`, `return_to_app`,
  `stage_to_intent_workspace`, or `write_to_memory_draft`.
- Support message send/receive and trigger fire/testing through existing safe
  BFF routes and future typed task routes; the browser must not hold Google,
  LiveKit, Redis, or server secrets.
- Support human-in-the-loop gates where the target state machine is real.
  Today Plan HITL is implemented; trigger/message HITL remains unsupported
  until those target state machines exist.

Interaction direction:

- The page should become a simple ComfyUI-like workflow board for collaboration
  routing: Plan nodes, Nanobot task nodes, result destination nodes, message
  nodes, HITL gates, and trigger nodes.
- It should keep a clear event/receipt timeline so an operator can see where a
  task went and who wrote the result.
- It may link to L2-B/Memory details, but detailed Node/Ref/file/photo editing
  stays on the Memory operation page.
- 2026-05-16 user decision: the first layout should be hybrid. Use swimlanes
  for the system overview, then open a ComfyUI-style workflow detail for a
  selected Plan, Nanobot task, HITL gate, or message/trigger chain.
- Next HITL expansion order is Google imports and Graphiti imports, then
  evidence/photo promotion. Trigger/message HITL should wait until those target
  state machines are real.
- C4/interruption candidates are urgent calendar/reminder, high-surprise
  Awareness, explicit user rule, or operator-triggered event. Ordinary source
  imports and evidence/photo hints default to C3/no-interrupt delivery unless a
  session policy says otherwise.

Data-model notes:

- WEB-012.19 tracks the larger workflow page.
- WEB-012.20 tracks manual Nanobot task destination and receipt modeling.
- Durable trace gaps stay in CORE-010.
- HITL/action-gate gaps stay in CORE-011 and should not be promoted beyond Plan
  gates until real trigger/message state machines exist.

## 2026-05-15 Time-Aligned Evidence / identify_object Slice

Owner: Web Console lane
Status: in_progress
Category: backend interface / observability / vision evidence
Scope: WEB-015, CORE-012
Source: user-approved Time-Aligned Evidence plan

### Time/Evidence Placement And Use

The React `Time / Evidence` panel belongs to the `Runtime Flow` workspace, not
to the L2-B / Memory Graph operation page. Its job is to show the current
runtime evidence chain:

- LiveKit/Brain room connection evidence, especially no-camera screen-share
  tracks.
- Brain `livekit_sampler` freshness and frame-cache freshness.
- Temporal evidence rows for video frames, image assets, BBox/Focus/magnifier
  attention, ASR, and future CV detections.
- Manual `request evidence`, `检查采样`, and `stage hint` debugging for
  IntentWorkspace/GOSLO context injection.

User workflow:

1. Open `协作流` / Runtime Flow.
2. Use `LiveKit / Brain 连接` to mint a token and connect to the room.
3. If the machine has no camera, publish browser screen share as
   `web-console-screen`.
4. Watch the `Time / Evidence` panel for `LiveKit sampler` and frame-cache
   `fresh/stale` badges.
5. Press `检查采样`; success means fresh evidence also looks like a screen-share
   source. A generic camera/test frame must not count as a successful
   screen-share smoke.
6. Use `请求 Evidence` to locate nearest stored evidence by time and `暂存提示`
   to stage a `visual_evidence_hint` into IntentWorkspace.

Boundary with Memory/L2-B:

- Memory Graph / L2-B consumes evidence later as Ref/Node/source material; it
  should not own LiveKit room sampling, screen-share permission, ASR timing, or
  BBox/Focus runtime capture controls.
- L2-B pages can later display evidence-linked Nodes/Refs and graph changes,
  but the runtime proof that "this frame existed at this time" stays in
  Runtime Flow.

Implemented:

- Added backend-first `parrot.brain.vision.evidence` with `TimebaseStamp`,
  `TimeAlignedSampleRef`, `SampleRegion`, and a bounded in-process
  `TemporalEvidenceLedger`.
- V1 does not change ECP/RPC top-level schemas. It reads optional
  `EcpEvent.payload["timebase"]`, `EcpCommand.meta["timebase"]`, and legacy
  fields such as `ts_ms`, `timestamp`, and `observed_at`.
- `observer.snapshot`, `observer.photo`, and `FocusBboxThreshold` mirror
  storage-backed snapshot/photo/attention events into the ledger.
- HTTP photo upload now accepts optional sample-time metadata through
  `X-Parrot-Timebase` JSON or discrete `X-Parrot-Clock-Domain`,
  `X-Parrot-Wall-Time-Ms`, `X-Parrot-Media-Time-Us`, `X-Parrot-Sequence`, and
  `X-Parrot-Source-Id` headers. The upload server forwards this as
  `photo.asset_uploaded.payload.timebase`; old clients that do not send it
  still work and simply fall back to estimated envelope time in the ledger.
- `identify_object` now resolves stored evidence by `evidence_id`,
  `bbox_ref_id`, `focus_ref_id`, or `target_time_ms`; if no image/frame is
  available it records a pending evidence request and continues L0/L1
  text/Graphiti matching. The old snapshot RPC path remains a disabled
  compatibility hook and is not called by this tool.
- 2026-05-15 bugfix: BBox/Mag/Focus refs are now resolution anchors. A stored
  asset linked by `bbox_ref_id` / `focus_ref_id` is preferred over the room's
  latest unrelated frame; if only a `bbox_focus` event exists, its sample time
  is used to find the nearest stored frame. 2026-05-15 review follow-up: if the
  requested BBox/Focus ref is missing entirely and no explicit `target_time_ms`
  was supplied, the resolver records a pending focus-linked request and returns
  `None` instead of using the newest unrelated frame. This keeps a user's
  selected region aligned with the evidence sent to VLM/search.
- Added storage-backed `parrot.brain.vision.frame_cache` as the first producer
  ingress for auditable encoded frames. LiveKit/SVA processors can call
  `record_livekit_frame_bytes()` after selecting/rate-limiting a track frame;
  the function writes an image asset, preserves room/track/participant/source
  ids, sequence, media timestamp, and records a `VIDEO_FRAME` ledger row.
- Added `parrot.brain.vision.livekit_sampler` as the first automatic producer
  adapter. `brain_entrypoint()` now starts a room-scoped low-FPS sampler that
  scans existing remote video publications, handles `track_subscribed` /
  reconnect-style events, encodes LiveKit `VideoFrame` objects to JPEG, and
  writes through `record_livekit_frame_bytes()`. The sampler is stopped during
  room disconnect/restart cleanup.
- The sampler now writes a secret-free status file
  (`PARROT_LIVEKIT_FRAME_SAMPLER_STATUS_PATH`, default
  `data/vision/livekit_sampler_status.json`) with active tracks, recorded frame
  count, last event, room id, and last error summary. Web status includes it as
  `livekit_sampler`, so the Runtime Time/Evidence panel can distinguish
  `status_file_missing` from an active frame consumer.
- Frame-cache and sampler status now expose freshness-oriented observability:
  `fresh_window_ms`, `latest_frame_age_ms`, `latest_frame_fresh`, and per-track
  latest frame summaries. These are Web/debug status fields, not promoted
  top-level Unity/App DTO fields.
- Added manual smoke helper `src/scripts/smoke_livekit_frame_sampler.py`; it
  joins the configured LiveKit room as a subscriber, attaches the sampler, waits
  for remote video frames, and prints sampler/frame-cache status without
  printing API secrets or JWTs.
- Added `parrot.brain.vision.evidence_image` as the stored-image/crop bridge
  for VLM calls. It dereferences local `asset_path`, applies optional
  normalized or pixel `SampleRegion`, encodes a bounded JPEG, and calls the
  existing Gemini `describe_image()` helper. `identify_object` uses that compact
  visual hint to enrich L0/L1 search text when stored evidence is available.
- Added `parrot.brain.vision.evidence_awareness` as the GOSLO staging policy
  for ready visual evidence. It stages a compact `visual_evidence_hint` document
  into IntentWorkspace, writes `transient/evidence_awareness_notice`, and uses
  `session_policy.should_generate_reply()` to decide whether a safe-turn
  notification is allowed. It does not call `generate_reply`; C3/C4 delivery
  remains session-owned.
- Wired `transient/evidence_awareness_notice` into `ContextInjector` as a
  session-owned C3 chat-context hint. Allowed notices carry the evidence id,
  staged ref id, reason, and an explicit no-interrupt cue into Gemini's chat
  context. Silent notices remain layer-1 only; V1 does not trigger C4 speech.
- Web routes now expose:
  - `GET /api/vision/evidence/status`
  - `GET /api/vision/evidence/timeline`
  - `POST /api/vision/evidence/request`
  - `POST /api/vision/evidence/stage-hint`
  - `POST /api/vision/evidence/memory-draft`
  - `POST /api/vision/evidence/frame-cache/upload`
  - `POST /api/vision/evidence/tool-lifecycle`
  - `GET /api/vision/evidence/screen-share-smoke`
  - `GET /api/vision/evidence/{evidence_id}`
  - `POST /api/app/test/visual-attention`
- App routes `POST /api/app/visual-tool/event` and
  `POST /api/app/visual-tool/asset/{asset_id}`, plus ECP event
  `visual_tool.lifecycle`, now cover BBox/MAG controller milestones and
  rendered crop/preview bytes. BBox `confirm` defaults to C3/no-interrupt; MAG
  `confirm` defaults to IntentWorkspace-only; `explicit_send` can request C3.
- React Runtime Flow includes a compact Time/Evidence panel for ledger status,
  recent evidence rows, manual evidence request, BBox/Focus test events,
  preview-only Memory Draft receipts, and a Web/operator `Cache Frame` smoke
  action.
- 2026-05-15 audit fix: `POST /api/vision/evidence/memory-draft` receipts now
  expose top-level `audit`, `core_candidate`, and `core_candidates`. The audit
  explicitly marks `read_only`, `no_l15_mutation`, `no_l2b_mutation`, and
  `no_ref_binding_mutation`, so Web receipt rendering and SSOT review can
  distinguish preview from execute.
- React build output now writes stable tracked bundle names (`assets/app.js`
  and `assets/styles.css`). The Web BFF serves `/` and `/assets/*` with
  `Cache-Control: no-store`, so local reloads do not stay pinned to stale
  bundles while deployments no longer depend on untracked hash files. The older
  tracked hash bundles were removed on 2026-05-15; new builds should keep this
  directory to the stable entrypoints unless the release strategy changes.

Interface boundary:

- Implemented Web/backend behavior is consolidated in
  `.cursor/memory/architecture/Interface/time_aligned_evidence_interface_20260515.md`.
  That SSOT does not promote Unity/App top-level DTO fields; shared promotion
  remains gated by CORE-012 review, live screen-share/Unity video smoke, and
  App lane field selection.
- `EcpEvent.created_at` is envelope creation time, not producer sample time.
- `TimebaseStamp.estimated=true` is used when falling back from missing
  sample-time metadata.
- Image bytes are not embedded in ECP/DataChannel payloads. VLM and Web debug
  surfaces must dereference HTTP/storage assets or future frame-cache files.
- VLM describe V1 only reads local `asset_path`; `asset_uri` without a local
  stored file is not fetched implicitly inside `identify_object`.
- Evidence Awareness V1 may stage context and mark `notify_goslo=true`.
  `ContextInjector` is now the session-owned delivery bridge for C3 hints and
  keeps `allow_interrupt=false`; C4 safe-turn speech is still pending review.
- BBox/Focus threshold V1 now remains conservative but connected: after ledger
  + Blackboard + `attention.threshold.crossed`, `FocusBboxThreshold` asks the
  evidence-awareness bridge to resolve the nearest stored frame/photo by
  BBox/Focus ref and producer timebase, then stage a `visual_evidence_hint`
  when evidence is available. Missing evidence becomes a pending request. The
  bridge does not capture frames, write L2-B, call `generate_reply`, or set
  `allow_interrupt=true`.
- BBox/magnifier are evidence/ref tools, not NodeKind special cases. App/Web
  should model their long-lived graph effect through CORE-012 evidence refs and
  the new CORE-013 graph-link policy candidate instead of inventing
  toolbar-specific L2-B node subclasses.
- CORE-014 is implemented as backend/App V1 in
  `parrot.brain.vision.tool_lifecycle`. It is still deliberately smaller than
  DSG L3 attention: it records semantic tool milestones, evidence refs, and
  delivery receipts; graph promotion and future L3 consumption remain separate
  policy layers.
- `POST /api/vision/evidence/frame-cache/upload` is a local Web/operator debug
  ingress; it is not the production LiveKit sampler and it does not belong in
  Unity/App DTOs.
- Fresh/stale status is derived from the producer sample timestamp and a local
  freshness window. It is for operator visibility and evidence selection, not a
  substitute for App-side video lifecycle telemetry.
- The automatic sampler code path exists, but CORE-012 remains draft until a
  real Unity/LiveKit video smoke verifies track selection, reconnect behavior,
  and storage load. Crop/VLM comparison and App/Web field review are still
  required before SSOT promotion.

Awareness intake and notification layers:

| Layer | Current Parrot channel | LiveKit/agent meaning | Notification strength | Current policy |
|:--|:--|:--|:--|:--|
| L0 storage | Temporal Evidence Ledger, L1.5 RefTable, Photo asset path | Not in chat context | Durable evidence only | Never speaks; producer/sample source must be explicit. |
| L1 working set | IntentWorkspace staged refs (`PHOTO`, `visual_evidence_hint`) | Discoverable by tools/read models, not automatically noticed | Soft context | GOSLO may inspect when a tool/turn looks at IntentWorkspace; staging alone is not a strong notification. |
| L2 blackboard notice | `transient/current_attention_hint`, `transient/photo_awareness_notice`, `transient/evidence_awareness_notice` | Session-owned bridge can decide whether to push context | Audited notification decision | Blackboard notice records source/policy/reason; unsupported keys stay local. |
| C3 chat-context hint | `ContextInjector._push_status_user()` via `session.update_chat_ctx` | Persistent chat context item for later turns | Strong notice, no speech | Evidence and Photo Awareness can reach this layer; message says do not interrupt. |
| C4 safe-turn speech | `session.generate_reply(...)` | Proactive spoken reply / TTS turn | Strong notice with speech | Disabled for Photo/Evidence V1; future safe-turn policy only, never default interrupt. |

Research anchors:

- LiveKit `ChatContext` is the ordered conversation history sent to the LLM on
  each turn, and can be modified/persisted with `update_chat_ctx`. This maps to
  Parrot C3, not to passive IntentWorkspace storage.
- LiveKit `generate_reply()` asks the agent to produce a response and can take
  per-reply instructions or custom chat context. This maps to Parrot C4 and is
  stronger than C3 because it schedules speech.
- LiveKit speech/turn docs expose `allow_interruptions` and explicit
  interruption control. Parrot Photo/Evidence Awareness V1 keeps
  `allow_interrupt=false` and does not call C4 from utility code.

Current intake behavior:

- Evidence Awareness: `parrot.brain.vision.evidence_awareness` stages
  `visual_evidence_hint` refs into IntentWorkspace, writes
  `transient/evidence_awareness_notice`, and `ContextInjector` converts allowed
  notices into C3 hints with evidence/ref ids. It does not speak.
- Photo Awareness: `parrot.brain.photo_awareness` stages preview refs into
  IntentWorkspace according to the App menu policy and writes
  `transient/photo_awareness_notice`. 2026-05-15 continuation wires that notice
  into `ContextInjector`: `UNAWARE_RECORDED` stays L1/L2 only; `AWARE_SILENT`
  and `AWARE_REACT` can become C3 hints after a preview ref is staged or a
  preview-missing decision is explicit. Pending preview-ref notices are held at
  layer 1 to avoid pushing incomplete context.
- Attention threshold: `FocusBboxThreshold` writes ledger + Blackboard +
  `attention.threshold.crossed`, then calls the audited WEB-015.12 bridge. The
  bridge resolves a nearby stored frame/photo from the Temporal Evidence Ledger
  and stages an Evidence Awareness `visual_evidence_hint`; ContextInjector may
  later deliver it as a C3 no-interrupt hint according to session policy. It
  still does not auto-promote to C4 speech or mutate L2-B.

Trigger body-feel taxonomy update:

- 2026-05-15 creates the core SSOT
  `.cursor/memory/architecture/Interface/goslo_trigger_awareness_taxonomy_20260515.md`.
  It separates trigger family (`photo`, `calendar`, `message`, `scene`,
  `memory`, `curiosity`, etc.) from delivery/body-feel level
  (`L0`, `L1`, `L2`, `C3`, `C4`, `I0`). A Photo trigger can therefore be a
  quiet stored asset, a C3 notice, or a future C4/safe-turn prompt depending on
  menu policy and priority; the same is true for Calendar and message triggers.
- Normal Photo awareness is C3 when the menu policy permits notification; the
  "off" setting stays storage/IntentWorkspace only. C4/interrupt is reserved
  for high-priority reviewed cases such as urgent calendar rows or future L3
  surprise/urgency thresholds.
- Legacy `TriggerOutcome.notify_gemini` is now compatibility wording only.
  `TriggerRunner` maps it to `ContextInjector.inject_status_notice()` by
  default, and trigger implementations should not directly call
  `_notify_brain()` before returning the same outcome. This avoids duplicate
  injection and keeps ordinary triggers from speaking over the user.
- Future Web trigger visualization should use clustered groups by trigger
  family and badges/intensity for delivery level, priority, urgency, surprise,
  confidence, and cooldown instead of trying to draw every trigger as a raw
  Runtime Flow node.
- App animation/body-language ownership is only recorded as an intake:
  listening/ASR partials may drive a subtle head tilt; C3 can drive a glance;
  high surprise can drive a peek; C4/interrupt-class events can drive explicit
  alert animation after App review.

Validation:

- `.venv\Scripts\python.exe -m pytest tests\test_brain\test_time_aligned_evidence.py tests\test_ecp_event\test_identify_object.py tests\test_web_console\test_web_console_server.py -q` -> `51 passed`.
- 2026-05-15 continuation: same focused pytest set now includes frame-cache
  route/ledger tests -> `53 passed`.
- 2026-05-15 continuation: same focused pytest set now includes automatic
  sampler encoding/fake-room track tests -> `55 passed`.
- 2026-05-15 continuation: added sampler status persistence, Web status
  exposure, frontend status readout, and manual LiveKit room smoke script.
  Focused pytest set remains `55 passed`; `npm run typecheck`, `npm run build`,
  and `git diff --check` passed.
- 2026-05-15 continuation: added stored-image/crop VLM describe V1. Focused
  identify/evidence pytest subset -> `18 passed`; full focused WEB-015 set now
  includes crop/VLM tests.
- 2026-05-15 continuation: added evidence-awareness staging, Web
  `stage-hint`, and `transient/evidence_awareness_notice`. Focused Web/evidence
  route subset -> `51 passed`.
- 2026-05-15 continuation final check: focused WEB-015 set
  (`time_aligned_evidence`, `identify_object`, `web_console_server`) ->
  `59 passed`; `npm run typecheck`, `npm run build`, `git diff --check`, secret
  literal scan, route smoke, and browser smoke passed. The running 7893 server
  now serves `assets/app-543b6d2f.js`.
- 2026-05-15 continuation: added ContextInjector C3 delivery for
  `transient/evidence_awareness_notice`. Focused WEB-015 plus injector test set
  covers C3 routing, silent suppression, evidence staging, identify_object, and
  Web evidence routes -> `61 passed`.
- 2026-05-15 continuation: added frame-cache/sampler freshness fields and Web
  Time/Evidence fresh/stale badges. `tests/test_brain/test_time_aligned_evidence.py`
  -> `11 passed`; focused WEB-015 pytest set -> `61 passed`; frontend
  typecheck/build passed with `assets/app-5b8dfb08.js`; browser smoke found the
  Runtime Time/Evidence panel and fresh/stale status with no dev-console logs.
- `web/console_app/node_modules/.bin/tsc.cmd --noEmit` passed.
- `web/console_app/node_modules/.bin/vite.cmd build` passed with stable tracked
  assets; the live `http://127.0.0.1:7893/` page now serves
  `assets/app.js` / `assets/styles.css` with no-store caching.
- Local route smoke on `http://127.0.0.1:7893`: `POST
  /api/vision/evidence/frame-cache/upload` cached a PNG test frame as
  `video_frame`; `POST /api/vision/evidence/request` resolved the nearest
  frame with `asset_exists=true`.
- Browser smoke: Runtime Flow shows Time/Evidence panel, exposes the `Cache
  Frame` button, clicking it adds a frame-cache receipt, and console errors
  stayed at zero.
- 2026-05-15 chain audit: focused module/route suite covering timebase parsing,
  frame-cache upload, fake LiveKit sampler, photo upload/observer, snapshot
  metadata, BBox/Focus threshold evidence, Web evidence routes, safe photo
  asset reads, and `identify_object` no-snapshot-RPC behavior -> `58 passed`.
- 2026-05-15 BBox/Mag ref-anchor bugfix validation:
  `.venv\Scripts\python.exe -m pytest tests\test_brain\test_time_aligned_evidence.py tests\test_ecp_event\test_threshold_emit.py -q`
  -> `23 passed`.
- 2026-05-15 expanded evidence/Web route regression after the ref-anchor fix:
  `.venv\Scripts\python.exe -m pytest tests\test_brain\test_time_aligned_evidence.py tests\test_ecp_event\test_threshold_emit.py tests\test_ecp_event\test_identify_object.py tests\test_web_console\test_web_console_server.py -q`
  -> `71 passed`.
- 2026-05-15 continuation: wired Photo Awareness notices into
  `ContextInjector` C3 delivery. Focused injector/photo/evidence tests ->
  `28 passed`; App facade/monitor regression tests -> `40 passed`;
  `git diff --check` passed with CRLF warnings only.
- 2026-05-15 continuation: wired `attention.threshold.crossed` into the
  conservative evidence-awareness bridge. Focused regression set covering
  Time/Evidence, BBox/Focus threshold, `identify_object`, Web console routes,
  and ContextInjector -> `81 passed`.
- 2026-05-15 continuation: added preview-only Evidence -> Memory draft route
  and React Time/Evidence button. Route/source-meta tests -> `3 passed`;
  focused Web/DSG/Time-Evidence regression -> `95 passed`; frontend
  typecheck/build passed; browser smoke confirmed the Runtime Time/Evidence
  panel, `Memory Draft` button, and zero dev-console errors.
- 2026-05-15 continuation: added Trigger/Awareness taxonomy SSOT and fixed the
  legacy `notify_gemini` path so ordinary trigger notifications route to C3
  exactly once through `TriggerRunner`. Focused trigger/calendar/message/
  evidence-awareness tests -> `23 passed`.
- 2026-05-15 continuation: added read-only backend screen-share smoke verifier
  `GET /api/vision/evidence/screen-share-smoke` and routed React `检查采样`
  through it. Web route tests -> `45 passed`; Time/Evidence/threshold/
  `identify_object` regression -> `34 passed`; frontend typecheck/build passed.
- 2026-05-15 bugfix: tightened screen-share smoke success so the same evidence
  candidate must be both fresh and screen-share-like. Regression test covers
  stale screen-share sampler status plus fresh camera frame -> warning, not
  success; follow-up fixed `next_steps` so the stale-screen case does not tell
  the operator to use Memory Draft. Web route tests -> `46 passed`.
- 2026-05-15 continuation: React Runtime screen share now prefers LiveKit's
  `setScreenShareEnabled(true)` and falls back to the previous
  `getDisplayMedia + publishTrack` bridge only when the helper is unavailable.
  It also listens for local screen-share unpublish events so the UI state
  clears when the browser share picker stops the track. Frontend typecheck/build
  and focused Web/Time-Evidence regression passed.
- 2026-05-15 bugfix: the React bridge now requires
  `setScreenShareEnabled(true)` to return a local screen-share publication
  before marking the UI as sharing. If the user cancels the picker or the SDK
  returns no publication, Web records only the error receipt and suppresses the
  misleading `screen_share_stop` event. Local SDK source review confirmed
  LiveKit JS `2.18.10` exposes `Track.Source.ScreenShare` as `screen_share`
  while the Python sampler may report proto names such as `SOURCE_SCREEN_SHARE`;
  the backend smoke verifier accepts both spellings. Regression now covers the
  JS `screen_share` spelling. Focused Web/Time-Evidence regression -> `81
  passed`; frontend typecheck/build and browser Runtime smoke passed.
- 2026-05-15 SSOT consolidation: created
  `.cursor/memory/architecture/Interface/time_aligned_evidence_interface_20260515.md`
  and updated the Interface index, `.cursor/memory/INDEX.md`, CORE-012
  candidate notes, and this Web README pointer. Audit result: Web/backend
  Time-Aligned Evidence behavior is documented as active SSOT; shared Unity/App
  DTO promotion remains explicitly blocked rather than implied.
