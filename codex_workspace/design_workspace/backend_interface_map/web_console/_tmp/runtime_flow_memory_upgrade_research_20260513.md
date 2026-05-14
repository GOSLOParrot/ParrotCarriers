# Runtime Flow + Memory Graph React Upgrade Research (2026-05-13)

Owner: Web Console chat  
Status: temporary-active  
Category: Web Console temporary research / audit archive  
Scope: React + Vite migration, Runtime Flow workspace, Memory Graph workspace, HITL, runtime-flow read model  
Updated: 2026-05-13  
Source pointers: `APP_WEB_PARALLEL_TODOLIST_20260513.md`, `observability_runtime_business_flow_20260513.md`, `memory_graph_workspace_business_flow_20260513.md`, `core_interface_candidate_queue_20260513.md`

This temporary file is a working archive for the multi-round React upgrade. It
must not become a permanent second SSOT. Promote durable decisions back into
the Web lane business files and the shared TODO board.

## Research Conclusions

- The Web Console task has outgrown the vanilla static frontend. Memory graph
  CRUD, Runtime Flow swimlanes, HITL gates, receipts, filters, and drawers need
  component-level state and graph interaction patterns.
- Use React + Vite for the new formal console frontend under
  `web/console_app/`. Keep the existing `web/console/` vanilla console as
  reference/transition only.
- Use React Flow first for both workspaces:
  - Memory Graph Workspace: L2-B node/edge operations, preview nodes, edge
    reconnect, selected-node detail.
  - Runtime Flow Workspace: swimlane/DAG graph for Intent -> Plan/HITL ->
    Blackboard -> IntentWorkspace -> Scheduler -> Nanobot -> Trigger/Message.
- React Flow research anchors used for this decision:
  - `https://reactflow.dev/learn/layouting/sub-flows`: parent/child grouping
    and subflow behavior for swimlanes and grouped workspaces.
  - `https://reactflow.dev/api-reference/hooks/use-edges-state`: controlled
    node/edge state as the first implementation pattern.
  - `https://reactflow.dev/api-reference/utils/reconnect-edge`: reconnect
    semantics for future L2-B edge retarget drafts.
- Keep Cytoscape.js as the future dense-graph candidate, especially if compound
  subgraphs or large graph layout become the dominant bottleneck.
- Cytoscape.js research anchor:
  - `https://js.cytoscape.org/`: compound nodes, built-in gestures, subgraph
    layouts, and headless analysis keep it useful after graphs become dense.
- Runtime observability should use an OpenTelemetry-like trace/span read model
  for UI rendering, but this is a Web BFF read model first, not a ratified App
  DTO.
- Runtime observability research anchors:
  - `https://opentelemetry.io/docs/concepts/signals/traces/`: spans, span
    events, span links, and async producer/consumer relationships.
  - `https://docs.langchain.com/oss/python/langchain/observability`:
    agent traces should reveal tools, prompts, decisions, and execution steps.
- HITL V1 should mirror interrupt/checkpoint workflows: expose pending gates,
  draft decisions, and explicit apply receipts. Real side effects stay
  operator-gated.
- HITL research anchor:
  - `https://docs.langchain.com/oss/python/langchain/human-in-the-loop`:
    safe agent actions pause, persist state, then resume with approve/edit/reject
    decisions. Web V1 adds cancel/resume for Plan lifecycle fit.

## Required Doc Sync

Each implementation slice must update:

- `APP_WEB_PARALLEL_TODOLIST_20260513.md`
- `web_console/README.md`
- `observability_runtime_business_flow_20260513.md` for Runtime Flow/HITL
- `memory_graph_workspace_business_flow_20260513.md` for Memory Graph
- `core_interface_candidate_queue_20260513.md` only for shared/core gaps

Do not write React migration notes into App docs. Do not promote Web operator
fields to `.cursor/memory/architecture/Interface/**` until App/Web confirmation.

## Audit Checklist

- Route matrix updated.
- Web business index updated.
- Shared core gaps staged only in candidate queue.
- No Unity/App DTO pollution.
- `PARROT_ORCH_SECRET`, LiveKit secrets, and Google credentials are absent from
  frontend JSON and DOM.
- Runtime Flow/HITL routes default to dry-run/read-only where applicable.
- Memory Graph writes still go through L1.5/Ref/receipt paths unless explicitly
  operator-gated.
- UI is split into Memory and Runtime Flow pages, not one dense panel.
- Tests cover route shape, secret non-leak, frontend build, and browser smoke.

## Implementation Ledger

- 2026-05-13: Plan approved to migrate Web Console to React + Vite and split
  Memory Graph Workspace from Runtime Flow Workspace.
- 2026-05-13: Added Web-only runtime-flow backend:
  `GET /api/runtime/flow`, `GET /api/runtime/flow/changes`,
  `GET /api/runtime/hitl/pending`, `POST /api/runtime/hitl/draft-decision`,
  and `POST /api/runtime/hitl/apply-decision`.
- 2026-05-13: Added first backend capability wiring for
  Plan -> Scheduler/Nanobot -> Plan result/timeout flow. `PlanRegistry` can now
  dispatch ready steps through an injectable dispatch function and Scheduler can
  report Nanobot result/timeout metadata back to the Plan registry.
- 2026-05-13: Fixed Plan dispatch failure settlement. Dispatch exceptions now
  mark the step and Plan failed instead of leaving a dispatched step stuck with
  only an error string.
- 2026-05-14: Review pass fixed three edge cases:
  `/api/runtime/flow/changes` no longer advances forever on no-op polling,
  HITL draft rejects missing Plan ids, and empty Plans complete on start.
- 2026-05-14: Review pass fixed Plan unsupported-tool hangs by adding a
  Scheduler task catalog and validating Plan step `expected_tool` before
  dispatch.
- 2026-05-14: Review pass also hardened Runtime Flow graph hygiene:
  changed-since signatures are order-insensitive, and dangling edges are pruned
  before React Flow receives the graph snapshot.
- 2026-05-14: CORE-010/011 review pass added Web-only trace hints
  (`trace_id`, `parent_span_id`, `payload_ref`) to Runtime Flow rows and made
  HITL draft receipts state-aware (`plan_state`, `valid_actions_for_state`).
- 2026-05-14: HITL consistency pass made pending gate `options` come from the
  same Plan-state policy as draft/apply validation, added explicit
  `unsupported_hitl_target` receipts for non-Plan gates, and included event
  `source`/`writer` in changed-since signatures.
- 2026-05-13: Created `web/console_app/` React + Vite frontend and build output
  in `web/console_dist/`. The BFF static root now prefers `web/console_dist`
  when present while keeping the old vanilla `web/console/` as reference.
- 2026-05-13: First React workspaces implemented:
  Memory Graph Workspace with React Flow L2-B canvas, L1.5 bucket board,
  node/edge dry-run receipts, and detail drawer; Runtime Flow Workspace with
  swimlane/DAG, event tape, manual trigger buttons, HITL cards, and receipt
  rail.
- 2026-05-14: Runtime Flow React UI pass fixed zh/en copy rendering, exposed
  the configured auto-refresh interval in the live pill, arranged Runtime nodes
  by lane-local row, and made HITL gate cards render backend-provided actions
  instead of hard-coded approve buttons.
- 2026-05-14: Approved backend/DTO upgrade begins. WEB-012.15 records a
  Web-only typed schema layer for Runtime Flow rows and receipts before any
  shared DTO/SSOT promotion. CORE-010 and CORE-011 remain candidates; Plan HITL
  is the only implemented gate target, and trigger/message HITL stays explicit
  unsupported until a real state machine exists.
- 2026-05-14: WEB-012.15/012.16 implemented. Runtime Flow nodes, edges, events,
  snapshots, changed-since envelopes, HITL gates, and HITL receipts now
  serialize through `parrot.web_console.runtime_flow_models`. Route smoke
  confirms the typed schema audit field, no-op changed-since remains false, and
  non-Plan HITL receipts expose `core_candidate=CORE-011`.
- 2026-05-14: React Web Console UX continuation implemented. Memory Graph now
  supports direct React Flow drag/connect edge drafts with frontend preview
  edges and selected-edge inspection. Runtime Flow now has a grouped manual
  trigger palette for message, LLM, scheduler, calendar, scene-switch, and
  roleplay dry-runs. The shared receipt rail is now a timeline with compact
  status/summary before raw JSON, and the zh copy in React source is readable.
- 2026-05-14: Trigger protocol cleanup pass confirmed that
  `DSG-TRIGGER-V2` / `TriggerOutcome` is the active trigger output protocol.
  `MessageNotificationTrigger` now commits `GOOGLE_MESSAGE` observations
  through L1.5/Ingest, `TriggerRunner.fire_event()` routes `ON_DEMAND`
  triggers, and trigger source files now use `TriggerOutcome` directly. The
  old `TriggerResult` name remains only as a compatibility alias/test, while
  early `SceneTrigger` scene-alert envelopes remain a separate input
  compatibility path pending future typed event review.
- Previous verification checkpoint: focused backend tests including
  Obsidian/Calendar/TriggerOutcome regressions report `44 passed`; React
  typecheck/build pass; browser smoke confirms React dist on port `7893`,
  Memory/Runtime navigation, LLM trigger receipt, zh/en toggle, and zero console
  errors.
- 2026-05-14: Review verification updated to `48 passed`; frontend
  typecheck/build still pass; HTTP no-op changed-since smoke returns
  `changed=false`.
- 2026-05-14: Trigger protocol cleanup verification updated to `64 passed` for
  focused DSG/Web Console trigger, L1.5, TriggerOutcome, and Web route tests,
  including a source guard that keeps new trigger implementations on the
  `TriggerOutcome` name.
- 2026-05-14: React UX verification: `npm run typecheck` and `npm run build`
  pass; `tests/test_web_console/test_web_console_server.py` reports
  `17 passed`; browser smoke on `http://127.0.0.1:7893/` confirms Runtime
  trigger palette, scene-switch preset, LLM dry-run receipt, Memory node draft
  receipt and preview, readable Chinese copy, and zero console errors.
- 2026-05-14: React UX continuation 2: Memory Graph L1.5 bucket board now
  shows pool health, capacity pressure, current scene, per-bucket node meters,
  frozen/open state, and last activity. Runtime Flow now consumes
  `/api/dsg/triggers/catalog` and renders registered trigger chips grouped by
  kind next to the manual dry-run palette. Verification repeated frontend
  typecheck/build, Web route tests (`17 passed`), browser Memory/Runtime smoke,
  and secret scan with no raw secret in React source/dist.
- 2026-05-14: Bugfix pass: Memory placeholder DSG compartment nodes are no
  longer valid L2-B edge draft endpoints; failed node/edge receipts no longer
  create ghost previews; Runtime group headings are localized; Runtime/HITL/
  Memory action failures now become local failure receipts instead of unhandled
  browser promise errors. Verification: frontend typecheck/build pass, Web route
  tests report `17 passed`, Runtime LLM dry-run receipt appears, and browser
  console errors remain zero.
- 2026-05-14: L1.5 card continuation: React Memory now exposes the existing
  Obsidian setting-node draft route as a compact card with `daily`, `roleplay`,
  and `ref` profiles. Browser smoke confirmed a successful daily UUID-free
  draft receipt and the expected `ref_profile_requires_obsidian_uuid` failure
  receipt with zero console errors. Follow-up bugfix added a local `ref` missing
  UUID guard and warning before any BFF call. No backend route, App DTO, or
  shared core contract changed.
- 2026-05-14: Obsidian draft bugfix: whitespace-only labels now normalize to
  `Web Console setting` in the BFF, preventing empty generated note-key
  segments. Local frontend receipts now include a random suffix, avoiding key
  collisions during rapid repeated local guard failures. Verification: Web route
  tests `17 passed`, frontend typecheck/build pass, and browser receipt-id smoke
  showed two unique local failure receipts with zero console errors.
- 2026-05-14: Final React checkpoint audit: reconciled actual
  `src/parrot/web_console/server.py` route mounts with the Web README and active
  Runtime/Memory business files. The top-level Web interface ledger now indexes
  `web/console_dist/` as the formal React shell and includes
  `GET /api/memory/blackboard/activity` next to the live memory snapshot. Secret
  scan found only generic env-var references/fake test values, no raw local
  secret. WEB-012.14 is marked done, while CORE-010/CORE-011 remain candidate
  review items and no App/Unity DTO was changed by this audit.
- 2026-05-14: Memory Graph direct operation continuation: successful node
  drafts now auto-stage edge endpoints; staged endpoints reveal an edge
  operation panel; swap and retarget draft actions reuse the existing
  `/api/l2b/edge/draft` dry-run route; React Flow `onReconnect` is wired for
  edge-handle retarget gestures. Browser smoke confirmed the panel, retarget
  receipt, one preview edge, and zero console errors. No backend route, App DTO,
  or shared core contract changed.
- 2026-05-14: Memory Graph terminology/interaction polish: user audit found the
  old dry-run wording, record-rail label, node/edge draft labels, and the empty
  L2-B placeholder blocks confusing. UI copy now presents dry-run as
  preview/`预演`, the right rail as records/`操作记录`, graph terms as
  `Node`/`Edge`, and raw JSON behind a collapsible detail. Empty L2-B now shows
  a non-connectable Obsidian-like status overlay instead of fake graph nodes.
  React Flow uses loose connection mode and stores node positions from
  node-change events. Research anchor: React Flow `ConnectionMode.Loose` and
  Obsidian Graph View filter/local graph patterns.
- 2026-05-14: Memory Graph custom node slice: replaced default React Flow L2-B
  node boxes with compact Obsidian-like Memory Node cards. Each Memory Node now
  exposes top/right/bottom/left handles under loose connection mode, so edge
  previews are no longer restricted to top-to-bottom pairing. Draft node/edge ids
  now include a random suffix to avoid rapid-click collisions. Verification:
  frontend typecheck/build and Web route tests passed; local HTTP checks returned
  `200` for `/` and `/api/app/live-state`. Browser visual smoke was attempted,
  but the in-app browser automation bridge timed out again, so manual visual
  review is still required for this slice.
- 2026-05-14: Memory Graph canvas-create slice: empty-canvas double-click now
  drafts a Node at the clicked React Flow coordinate using
  `screenToFlowPosition`, not deprecated pane-relative `project()` math. React
  Flow double-click zoom is disabled on this workspace so the create gesture is
  stable. Verification: frontend typecheck/build, Web route tests, static
  awkward-label scan, `git diff --check`, and local HTTP checks passed. Browser
  visual smoke was retried and timed out at the automation bridge again, so the
  open browser still needs manual refresh/visual confirmation.
- 2026-05-14: Selection-state bugfix: React Flow clears internal selection on
  blank-pane click, but the Web drawer was keeping its own stale selected
  object. Blank-pane click now clears the Web detail selection, and custom Node
  / Edge selected props are driven from that same state so the canvas highlight
  and drawer do not diverge. Verification: frontend typecheck/build, Web route
  tests, static awkward-label scan, `git diff --check`, and local HTTP checks
  passed.
- 2026-05-14: View recovery controls: added Web-only `Focus` and `Layout`
  controls to the React Memory canvas. `Focus` fits the selected Node or the two
  endpoints of the selected Edge; `Layout` reapplies a local circular layout to
  visible Nodes. This is intentionally a frontend view-state improvement only
  and does not change L2-B, L1.5, Ref, App DTO, or core interface contracts.
  Verification: frontend typecheck/build, Web route tests, static awkward-label
  scan, `git diff --check`, and local HTTP checks passed.
- 2026-05-14: Homepage/edge UX bugfix slice: Memory view polling now caps at 5s
  even when the server default is 15s, but this is still polling rather than
  true realtime. React Flow Memory Nodes now expose source and target handles on
  top/right/bottom/left, and preview/persisted edges carry or infer handle ids
  so they do not fall back to top-to-top rendering. Left navigation and the
  records rail are collapsible, with records default collapsed to protect canvas
  width. React Flow controls, minimap, attribution, and edge labels are
  dark-mode styled. Topbar summaries and the empty-state body copy were
  removed/reduced. No backend DTO or core interface changed.
  Verification: frontend typecheck/build, Web route tests, static awkward-label
  scan, `git diff --check`, and local HTTP checks passed.
- 2026-05-14: Memory Canvas toolbar / L2-B monitor prep slice: the current
  ReactFlow page is explicitly preserved as Memory Canvas/editor, while a new
  WEB-013 full-screen L2-B realtime graph monitor is planned separately. The
  canvas toolbar now defaults to a compact row and moves Edge endpoint inputs
  into an expandable drawer. Visible Node handles are now one dot per side, with
  separate hidden `target-*` anchors and `source-*` anchors used for React Flow
  edge rendering. This follows React Flow's loose connection model while
  avoiding the confusing doubled handle dots and top/top fallback. Empty L2-B
  state now renders as a semi-transparent status overlay, not a solid component
  block. Research anchors recorded: React Flow ConnectionMode/Handles docs and
  force-graph Canvas/dynamic data examples. No backend route, App DTO, or core
  interface changed.

## Pending Core / Data Model Review

These are not promoted to core SSOT yet. They need App/Web lane confirmation
before any `.cursor/memory/architecture/Interface/**` edit:

- CORE-010 `RuntimeFlowTraceReadModel`: may become shared if Unity/App needs a
  compact runtime trace/status stream. Current implementation is Web-only.
  Field audit result: event `source` means read-model writer/system, while edge
  `source`/`target` are React Flow endpoint ids; this needs explicit naming if
  promoted. `trace_id=plan:<plan_id>` is clean for Plan -> Scheduler ->
  Nanobot visibility, but Graphiti commit events and persistent cross-process
  result spans are still not durable.
- CORE-011 `RuntimeHumanGate`: may become shared if App also renders or writes
  approvals. Current implementation is Web BFF/operator-safe. Field audit
  result: Plan gates are clean enough for Web V1 after state-aware validation;
  trigger/message gates are not implemented yet, so the candidate must not be
  promoted as a general HITL DTO until those target kinds exist.
- Plan dispatch result metadata is now implemented in backend code as a local
  capability upgrade, but a durable cross-process Plan/Nanobot trace DTO still
  belongs in CORE-010/CORE-011 review.
