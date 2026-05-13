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
| `observability_runtime_business_flow_20260513.md` | in_progress | WEB-002, WEB-004, WEB-005, WEB-009, WEB-011 | ECS/module health, `/status`, Blackboard, IntentWorkspace, Plan/task, Scheduler, Nanobot, AgentTeam/Maid Team, collaboration status, LineB voice lab smoke, Runtime Flow and trigger palette. |
| `memory_graph_workspace_business_flow_20260513.md` | in_progress | WEB-003, WEB-007, WEB-010, WEB-011 | L1.5, L2-B, Blackboard, IntentWorkspace, node/photo management, Ref binding, Evidence/String Board, real-time memory visualization plan, Visual Memory Operations Cockpit. |
| `graphiti_management_business_flow_20260513.md` | in_progress | WEB-006 | Graphiti/FalkorDB management route: observe/search/draft/dry-run first, Web operator surgery later. |

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
| `POST /api/l2b/edge/draft` | draft | none | Normalizes `SemanticEdge`-shaped source/target/kind/strength/source/meta. |
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
- Blackboard and IntentWorkspace rows now render as grouped status-light cards.
- Verification signal: `node --check web\console\assets\app.js`, clean
  duplicate-id scan, and in-app browser Memory smoke. L2-B preview smoke showed
  two `.memory-svg-node.preview` nodes, one `.memory-edge.preview`, selectable
  preview detail, and zero console errors. Canvas-toolbar smoke showed one
  preview node created from the center-stage action bar, selection pill update,
  toolbar clear to zero previews, and zero console errors. Cleanup regression
  smoke confirmed that drafting an edge after clearing previews does not
  resurrect removed `draft:` endpoints.

## Implementation Anchors

Keep active Web Console implementation in these locations:

| Surface | Path | Notes |
|:--|:--|:--|
| BFF / read adapters | `src/parrot/web_console/` | Server-side only; may hold secrets such as `PARROT_ORCH_SECRET` in process env. |
| Static frontend | `web/console/` | Obsidian-like console shell and future Web-only renderers. |
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
