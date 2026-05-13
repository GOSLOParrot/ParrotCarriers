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
- 2026-05-13: Created `web/console_app/` React + Vite frontend and build output
  in `web/console_dist/`. The BFF static root now prefers `web/console_dist`
  when present while keeping the old vanilla `web/console/` as reference.
- 2026-05-13: First React workspaces implemented:
  Memory Graph Workspace with React Flow L2-B canvas, L1.5 bucket board,
  node/edge dry-run receipts, and detail drawer; Runtime Flow Workspace with
  swimlane/DAG, event tape, manual trigger buttons, HITL cards, and receipt
  rail.
- Previous verification checkpoint: focused backend tests including
  Obsidian/Calendar/TriggerOutcome regressions report `44 passed`; React
  typecheck/build pass; browser smoke confirms React dist on port `7893`,
  Memory/Runtime navigation, LLM trigger receipt, zh/en toggle, and zero console
  errors.
- 2026-05-14: Review verification updated to `46 passed`; frontend
  typecheck/build still pass; HTTP no-op changed-since smoke returns
  `changed=false`.

## Pending Core / Data Model Review

These are not promoted to core SSOT yet. They need App/Web lane confirmation
before any `.cursor/memory/architecture/Interface/**` edit:

- CORE-010 `RuntimeFlowTraceReadModel`: may become shared if Unity/App needs a
  compact runtime trace/status stream. Current implementation is Web-only.
- CORE-011 `RuntimeHumanGate`: may become shared if App also renders or writes
  approvals. Current implementation is Web BFF/operator-safe.
- Plan dispatch result metadata is now implemented in backend code as a local
  capability upgrade, but a durable cross-process Plan/Nanobot trace DTO still
  belongs in CORE-010/CORE-011 review.
