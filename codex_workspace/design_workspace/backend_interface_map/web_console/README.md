# Web Console Business Interfaces

This directory is owned by the Web Console chat.

Use it for Web-facing business-interface notes: ECS/module health, L1.5/L2-B
visualization, node/photo management, Blackboard, IntentWorkspace, Plan,
Scheduler/Nanobot monitoring, Maid/GOSLO chat observability, and Web-only
admin flows.

## Active Business Interface Index

This README is the local SSOT for active Web Console business-interface files.
Add new Web docs here when they are created, and remove or mark superseded
entries when a file stops being active.

| File | Status | TODO | Scope |
|:--|:--|:--|:--|
| `web_console_step1_console_plan_20260513.md` | approved | WEB-001, WEB-008 | Step 1 requirements, IA, visual direction, implementation order, doc hygiene. |
| `observability_runtime_business_flow_20260513.md` | in_progress | WEB-002, WEB-004, WEB-005, WEB-009, WEB-012 | ECS/module health, `/status`, Blackboard, IntentWorkspace, Plan/task, Scheduler, Nanobot, AgentTeam/Maid Team, collaboration status, LineB voice lab smoke, Runtime Flow, HITL, and trigger palette. |
| `memory_graph_workspace_business_flow_20260513.md` | in_progress | WEB-003, WEB-007, WEB-010, WEB-011 | L1.5, L2-B, Blackboard, IntentWorkspace, node/photo management, Ref binding, Evidence/String Board, real-time memory visualization plan, Visual Memory Operations Cockpit. |
| `graphiti_management_business_flow_20260513.md` | in_progress | WEB-006 | Graphiti/FalkorDB management route: observe/search/draft/dry-run first, Web operator surgery later. |

## Temporary Working Archives

Temporary files are indexed here so they do not become scattered hidden SSOTs.
Promote durable decisions back into the active business files above.

| File | Status | Scope |
|:--|:--|:--|
| `_tmp/runtime_flow_memory_upgrade_research_20260513.md` | temporary-active | React + Vite migration, Runtime Flow workspace, Memory Graph workspace, HITL, runtime-flow read model, audit checklist. |

## Completed Interface Ledger

Audit checkpoint: 2026-05-13. This ledger records implemented Web Console
surfaces that should be preserved while the next large Memory Graph work is
planned. Detailed business rationale stays in the active files above.

| Area | Implemented surface | Business file | Current status |
|:--|:--|:--|:--|
| Console shell | `GET /health`, static `web/console/`, zh/en setting, Obsidian-like layout, active-view refresh loop. | `observability_runtime_business_flow_20260513.md` | Useful foundation; keep simple. |
| Orchestrator status | `GET /api/console/config`, `GET /api/orchestrator/health`, `GET /api/orchestrator/status`; BFF injects Bearer from `PARROT_ORCH_SECRET` server-side. | `observability_runtime_business_flow_20260513.md` | Implemented and tested; no secret leak. |
| Menu/App smoke | `GET /api/app/canvas`, `GET /api/app/modules`, `GET /api/app/line-profiles`, `POST /api/app/line-profiles/apply`, `POST /api/app/workspace/apply`. | `observability_runtime_business_flow_20260513.md`, `memory_graph_workspace_business_flow_20260513.md` | Useful smoke path; not the main next focus. |
| LineB voice lab | `POST /api/app/lineb/audio-route`, `POST /api/app/lineb/tts-segment`, `POST /api/app/lineb/mic-input`, `GET /api/livekit/config`, `POST /api/livekit/web-token`; browser LiveKit audio wiring and event/transcript panes. | `observability_runtime_business_flow_20260513.md` | Implemented smoke; full voice conversation still needs user-approved mic and running agent. |
| Runtime monitor | `GET /api/runtime/monitor`; Scheduler route order/channels/tasks, Nanobot bridge, Plan counts/DAG rows, Blackboard summary, AgentTeam placeholder. | `observability_runtime_business_flow_20260513.md` | Read-only Web surface; not an App DTO. |
| Runtime Flow upgrade | `GET /api/runtime/flow`, `GET /api/runtime/flow/changes`, `GET /api/runtime/hitl/pending`, `POST /api/runtime/hitl/draft-decision`, `POST /api/runtime/hitl/apply-decision`, React swimlane/DAG workspace. | `observability_runtime_business_flow_20260513.md` | First slice implemented; Web-only read model/HITL first, core candidates staged before shared promotion. |
| Trigger and message lab | `GET /api/dsg/triggers/catalog`, `POST /api/dsg/triggers/draft-event`, `POST /api/dsg/triggers/fire-event`, `POST /api/google/messages/check`, `POST /api/google/messages/push-test`. | `observability_runtime_business_flow_20260513.md` | Web-only dry-run/receipt surface; real fire publishes to `CH_DSG_EVENTS` only with explicit operator mode. Gmail check uses Scheduler/Nanobot dispatch. |
| Live memory snapshot | `GET /api/app/live-state?limit=...`; grouped Blackboard key rows, grouped IntentWorkspace ref rows, Ref registry, SVG L2-B graph canvas/detail panel, tool artifacts. | `memory_graph_workspace_business_flow_20260513.md` | Implemented as bounded active-view polling renderer with filters, new-node diff highlight, and soft Intent/Ref-to-L2-B links when linked nodes exist. User audit moved the next focus to WEB-011: large realtime cockpit, direct graph operations, simplified L1.5 cards, trigger palette, and possible changed_since/SSE after the visual model is useful. |
| L1.5/L2-B operator drafts | `GET /api/l15/pool`, `POST /api/l15/bucket-op/draft`, `POST /api/l15/bucket-op`, `POST /api/l15/obsidian-node/draft`, `POST /api/l15/obsidian-node`, `POST /api/l2b/node/draft`, `POST /api/l2b/node`, `POST /api/l2b/node/delete`, `POST /api/l2b/edge/draft`, `POST /api/l2b/edge`. | `memory_graph_workspace_business_flow_20260513.md` | Default dry-run; Web-only receipts. Node create/update routes through `L15Pool.admit(Observation(source=USER_EXPLICIT))`; delete uses `L15Pool.evict`; real edge connect requires operator mode. |
| Graphiti console | `GET /api/graphiti/status`, `POST /api/graphiti/search`, `POST /api/graphiti/episode/draft`, `POST /api/graphiti/episode`; dry-run first. | `graphiti_management_business_flow_20260513.md` | Implemented safe seed; full surgery/operator mode remains future work. |

## Completion Report: Trigger/L1.5/L2-B Draft Slice

Date: 2026-05-13
Status: implemented, documented, and smoke-tested in the local browser
Scope: Web Console only; no Unity/App DTO changes; no direct core SSOT edits.

Completed:

- Added the Web-only management BFF in `src/parrot/web_console/memory_ops.py`
  and mounted its routes from `src/parrot/web_console/server.py`.
- Added Runtime Monitor Trigger Lab for trigger catalog, draft/fire receipts,
  Gmail `message_check` dispatch drafts, and synthetic `message_push` tests.
- Added Memory Graph Operator Workbench for L1.5 pool inspection, bucket op
  drafts, Obsidian three-profile setting-node drafts, L2-B node drafts/delete,
  and L2-B edge drafts.
- Kept dangerous writes behind explicit `operator_mode=true` and
  `dry_run=false`. Default browser actions remain dry-run receipt generation.
- Browser-smoked the restarted `http://127.0.0.1:7893/` server after route
  load; trigger draft and L2-B node draft receipts returned successfully.

Verification:

- `node --check web\console\assets\app.js`
- `uv run python -m py_compile src\parrot\web_console\memory_ops.py src\parrot\web_console\server.py`
- `uv run pytest tests\test_web_console\test_web_console_server.py tests\test_dsg\test_obsidian_true_connection.py tests\test_dsg\test_calendar_true_connection.py tests\test_dsg\test_trigger_outcome_v2.py -q`
- Result at this checkpoint: `29 passed`.

Audit result:

- Routes are indexed in this README and detailed in the active business files.
- No Web-only operator/admin fields were added to App DTOs.
- No new scattered business docs were created for this slice.
- `PARROT_ORCH_SECRET`, LiveKit secrets, and Google credentials are not exposed
  through frontend JSON or DOM.
- Known backend drift remains: `MessageNotificationTrigger` still writes
  message EVENT nodes directly to L2-B. The next backend pass should migrate it
  to `TriggerOutcome.commit_observations` or an equivalent audited receipt
  path so it matches Calendar/Obsidian.

## Completion Report: React Runtime Flow / Memory Workspace First Slice

Date: 2026-05-13
Status: implemented first vertical slice; visual polish and browser smoke are
complete for this checkpoint, with follow-up polish still tracked by WEB-011
and WEB-012
Scope: Web Console only; no Unity/App DTO changes; no direct core SSOT edits.

Completed:

- Added React + Vite source under `web/console_app/` and build output under
  `web/console_dist/`.
- Updated the BFF static root so the same Web Console service prefers the React
  build when `web/console_dist/index.html` exists and falls back to the old
  vanilla console when it does not.
- Added Web-only runtime-flow read model in
  `src/parrot/web_console/runtime_flow.py`.
- Added Runtime Flow routes:
  `GET /api/runtime/flow`, `GET /api/runtime/flow/changes`,
  `GET /api/runtime/hitl/pending`,
  `POST /api/runtime/hitl/draft-decision`, and
  `POST /api/runtime/hitl/apply-decision`.
- Added first backend capability wiring so Plan steps can dispatch through
  Scheduler/Nanobot task metadata and Nanobot result/timeout metadata can report
  back into the Plan registry.
- Fixed the Plan dispatch failure edge case: a dispatch exception now fails the
  step and Plan instead of leaving the step stuck in `DISPATCHED`.
- Fixed the unsupported Plan tool edge case: Plan steps now validate against
  the Scheduler Nanobot task catalog before dispatch, so an unsupported tool
  fails fast instead of being routed away from the Plan result flow.
- Fixed the Runtime Flow changed-since edge case: no-op polls now return
  `changed=false` instead of advancing sequence forever.
- Fixed the Runtime Flow graph-read-model edge hygiene: the stable signature is
  order-insensitive for nodes/edges/events, and graph edges whose endpoints are
  outside the Runtime Flow read model are pruned before React Flow rendering.
- Fixed HITL draft validation for missing Plan ids.
- Fixed HITL draft validation for invalid Plan-state/action pairs; dry-run
  receipts now expose `plan_state` and `valid_actions_for_state` instead of
  promising an action that apply would reject.
- Added Web-only CORE-010 trace hints to Runtime Flow nodes/edges/events:
  `trace_id`, `parent_span_id` where applicable, and redacted `payload_ref`.
- Fixed empty Plan execution settlement so a zero-step Plan completes instead
  of staying active/executing forever.
- Added React Memory Graph Workspace with React Flow L2-B canvas, L1.5 bucket
  board, node/edge dry-run action buttons, detail drawer, and receipts.
- Added React Runtime Flow Workspace with swimlane/DAG graph, event tape,
  manual trigger buttons, HITL cards, and receipt rail.

Verification at this checkpoint:

- `uv run python -m py_compile src\parrot\web_console\runtime_flow.py src\parrot\web_console\server.py src\parrot\brain\plan\plan_registry.py src\parrot\scheduler\service.py`
- `uv run pytest tests\test_brain\test_plan_lifecycle.py tests\test_web_console\test_web_console_server.py -q`
- `cd web\console_app; npm run typecheck`
- `cd web\console_app; npm run build`
- Browser smoke on `http://127.0.0.1:7893/`: React dist served, Memory and
  Runtime pages navigated, LLM trigger draft produced a receipt, zh/en toggle
  worked, and frontend console errors stayed at zero.
- Latest combined focused result: `47 passed`.
- Latest HTTP smoke after service restart:
  `/api/runtime/flow/changes?since=<current sequence>` returns
  `changed=false`.

Audit result:

- Web-only runtime/HITL routes are documented here and in
  `observability_runtime_business_flow_20260513.md`.
- Shared/core implications stay in CORE-010 and CORE-011; no core SSOT file was
  edited.
- Frontend code does not embed `PARROT_ORCH_SECRET`, LiveKit secret, or Google
  credentials.
- Remaining risk: React UI is still a first vertical slice. Direct graph
  drag/connect/reconnect, graph health metrics, and Evidence Board polish remain
  future WEB-011/WEB-012 slices.

### Implemented Web Route Matrix

| Endpoint | Mode | Write path | Notes |
|:--|:--|:--|:--|
| `GET /api/dsg/triggers/catalog` | read | none | Lists registered trigger names, kinds, interval, and sample event hints. |
| `POST /api/dsg/triggers/draft-event` | draft | none | Builds a Redis DSG event receipt and reports matched trigger names. |
| `POST /api/dsg/triggers/fire-event` | dry-run/operator | Publishes to `CH_DSG_EVENTS` only with `operator_mode=true` and `dry_run=false`. | Does not call Brain trigger singletons from the Web process. |
| `POST /api/google/messages/check` | dry-run/operator | Dispatches Scheduler `message_check` only with explicit operator execution. | Gmail/OAuth remains outside the browser; Nanobot/MCP owns the actual check. |
| `POST /api/google/messages/push-test` | dry-run/operator | Publishes synthetic `message_push` through `CH_DSG_EVENTS` only in operator execution. | Used to test message trigger routing. |
| `GET /api/l15/pool` | read | none | Returns Web management snapshot for health, buckets, refs, timeline, and scene. |
| `POST /api/l15/bucket-op/draft` | draft | none | Validates/normalizes bucket operations into a receipt. |
| `POST /api/l15/bucket-op` | dry-run/operator | `L15Pool.apply_bucket_op`. | Dangerous real action requires operator mode. |
| `POST /api/l15/obsidian-node/draft` | draft | none | `daily`/`roleplay` allow UUID-free setting nodes; `ref` requires an Obsidian UUID. |
| `POST /api/l15/obsidian-node` | dry-run/operator | Publishes normalized Obsidian event through `CH_DSG_EVENTS`. | Uses the trigger/L1.5 route, not direct L2-B mutation. |
| `POST /api/l2b/node/draft` | draft | none | Produces a `USER_EXPLICIT` observation receipt for create/update. |
| `POST /api/l2b/node` | dry-run/operator | `L15Pool.admit(Observation(...))`. | Keeps Ingest/L1.5 as the normal write gate. |
| `POST /api/l2b/node/delete` | dry-run/operator | `L15Pool.evict`. | Web operator action; default is preview receipt. |
| `POST /api/l2b/edge/draft` | draft | none | Normalizes `SemanticEdge`-shaped source/target/kind/strength/source/meta; rejects same-node self-edge drafts. |
| `POST /api/l2b/edge` | dry-run/operator | `L2BGraph.connect`. | Real edge connect requires operator mode and returns an audit receipt. |

## Drift Audit

- No implemented Web-only route has been intentionally added to Unity/App DTOs.
- Business-interface files now cover every implemented Web route listed above.
- The current risk is product focus, not undocumented routes: the UI has several
  useful smoke panels, and the Memory Graph now has a first visual renderer with
  operator drafts, but WEB-011 should replace dense component stacking with a
  larger visual operations cockpit before adding more broad admin panels.

### WEB-011.1 Checkpoint

- Memory Graph now has a first cockpit shell in `web/console/`: source rail,
  larger L2-B canvas, selected-node inspector/actions, edge draft controls,
  receipt stream, and advanced Obsidian draft drawer.
- L1.5 bucket cards now include freeze/unfreeze/clear quick draft buttons that
  reuse the existing bucket draft route.
- No route matrix changes were made in this slice. Existing L1.5/L2-B/edge
  routes remain the interface surface.
- Verification signal: `node --check web\console\assets\app.js`, clean
  duplicate-id scan, and in-app browser Memory smoke with no console errors.
- Open follow-up: WEB-011.2/011.3 continue from this shell toward stronger live
  rendering and direct graph operations.

### WEB-011.5 Checkpoint

- Runtime Monitor now has a visible trigger palette for message check/message
  push, LLM context push, scheduler tick, calendar test, and custom DSG event
  drafts.
- No new routes were added. Message actions continue through Nanobot Web routes;
  other presets call the existing DSG trigger draft route.
- Verification signal: `node --check web\console\assets\app.js`, clean
  duplicate-id scan, and in-app browser Runtime smoke with no console errors.

### WEB-011.3/011.6/011.7 Checkpoint

- Empty L2-B canvas state now renders a DSG compartment map for Blackboard,
  IntentWorkspace, Refs, L1.5, and L2-B instead of a mostly empty grid.
- L2-B node draft/dry-run receipts now create a frontend-only ghost node preview
  on the canvas. This preview is renderer state only; it is not persisted and
  does not change the BFF route contract. The receipt area includes an explicit
  `Clear Preview` control.
- Preview nodes are now selectable in the same inspector path as persisted
  L2-B nodes, and staged edge draft receipts draw preview edges when both
  endpoints are visible.
- The central canvas now has a local action bar for create preview, use
  selected, set Edge From/To, draft edge, and clear preview; it reuses existing
  draft/dry-run routes and does not change the BFF route matrix.
- `Clear Preview` also clears stale selected preview nodes and `draft:` UUIDs
  from target/delete/edge fields so later drafts cannot accidentally reuse a
  removed ghost endpoint.
- Same-node edge drafts are rejected in the Web BFF and guarded in the frontend
  so a zero-length invisible self-edge cannot return a success receipt.
- Blackboard and IntentWorkspace rows now render as grouped status-light cards.
- Verification signal: `node --check web\console\assets\app.js`, clean
  duplicate-id scan, and in-app browser Memory smoke. L2-B preview smoke showed
  two `.memory-svg-node.preview` nodes, one `.memory-edge.preview`, selectable
  preview detail, and zero console errors. Canvas-toolbar smoke showed one
  preview node created from the center-stage action bar, selection pill update,
  toolbar clear to zero previews, and zero console errors. Cleanup regression
  smoke confirmed that drafting an edge after clearing previews does not
  resurrect removed `draft:` endpoints. Self-edge smoke confirmed that using
  the same selected node for From and To creates no preview edge and reports a
  local guard receipt with zero console errors.

## Implementation Anchors

Keep active Web Console implementation in these locations:

| Surface | Path | Notes |
|:--|:--|:--|
| BFF / read adapters | `src/parrot/web_console/` | Server-side only; may hold secrets such as `PARROT_ORCH_SECRET` in process env. |
| React frontend source | `web/console_app/` | Formal next Web Console frontend: React + Vite, Memory Graph Workspace, Runtime Flow Workspace. |
| Built/static frontend | `web/console_dist/` | Served by the Web Console BFF when present; `web/console/` remains the legacy vanilla transition/reference shell. |
| Launcher | `src/scripts/start_web_console.py` | Local entrypoint; default port `7893`. |
| Tests | `tests/test_web_console/` | Focused BFF/static route tests. |

## Write Rules

- Default to read-only adapters before writes.
- Use the A-D discipline from `../business_interface_workflow.md`.
- Keep Web-only dashboard/admin flows here, not in Unity DTOs.
- Prefer one stable business file per product surface. Do not create a new doc
  for every sub-step of the same plan.
- If a multi-round implementation or audit needs temporary notes, place them
  under a clearly named temporary Web Console folder, keep them out of the
  shared TODO board, and promote only key decisions or durable findings back
  into the indexed business files.
- If a flow needs a shared field, endpoint, DTO, topic, or BB key, add a row to
  `../core_interface_candidate_queue_20260513.md` instead of editing core SSOT.
- Update `../../tasks/APP_WEB_PARALLEL_TODOLIST_20260513.md` for lane status.
- Keep `../README.md` and this README aligned whenever active Web business
  documents are added, superseded, or renamed.

## Suggested Slice Header

```md
## Slice: <name>

Owner chat: Web Console
Status: intake | proposed | approved | in_progress | blocked_core | done
Related TODO: WEB-###

### A. Source Readback

### B. Existing Core Interfaces

### C. Missing Core Surface

### D. Observable Completion Signal
```
