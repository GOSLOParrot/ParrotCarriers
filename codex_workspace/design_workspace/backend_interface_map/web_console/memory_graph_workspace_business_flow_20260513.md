# Memory Graph Workspace Business Flow (2026-05-13)

Owner: Web Console chat  
Status: in_progress
Category: Web Console business interface  
Scope: L1.5 management, L2-B visualization, node/photo management, Ref binding, Evidence/String Board  
Updated: 2026-05-13  
Related TODO: WEB-003, WEB-007, WEB-010, WEB-011
Sources: `src/parrot/brain/l2b_monitor.py`, `src/parrot/dsg/l1_5/**`, `src/parrot/brain/observer/photo.py`, `src/parrot/brain/refs.py`, `codex_workspace/design_workspace/backend_interface_map/web_console/graphiti_management_business_flow_20260513.md`, Obsidian Canvas/JSON Canvas/React Flow/Cytoscape.js research anchors, `D:/GOSLOParrot/Pixel Asset`

## 2026-05-13 Direction Update: React Memory Graph Workspace

The Memory Graph work is now a formal React + Vite workspace, not another
panel added to the vanilla console. It is separate from Runtime Flow.

Memory Graph owns:

- L1.5 bucket/pool management.
- L2-B large graph canvas and direct node/edge dry-run CRUD.
- Graphiti/FalkorDB operator drawers and search/draft links.
- Ref, photo, Evidence/String Board rendering over shared Ref/Edge candidates.
- Bucket board, selected-node drawer, receipt/event drawer, and graph filters.

Runtime collaboration surfaces such as Plan, Scheduler, Nanobot, message
receipt flow, and HITL belong to WEB-012 / Runtime Flow Workspace.

Frontend direction:

- Source: `web/console_app/` React + Vite.
- Graph: React Flow first for direct graph CRUD/reconnect patterns.
- Dense graph candidate: Cytoscape.js only after React Flow proves insufficient.
- State: React hooks/reducers first; no Redux/Zustand until complexity
  requires it.

### Implementation Signal: React Memory Graph First Slice

Date: 2026-05-13

Implemented code:

- React source: `web/console_app/src/App.tsx`,
  `web/console_app/src/api.ts`, `web/console_app/src/types.ts`,
  `web/console_app/src/styles.css`
- Build output: `web/console_dist/`
- BFF static switch: `src/parrot/web_console/server.py` now serves the React
  build first when available and falls back to legacy `web/console/`.

Current React Memory behavior:

- `GET /api/app/live-state` remains the primary live read model for L2-B,
  Blackboard, IntentWorkspace, refs, and tool artifacts.
- `GET /api/l15/pool` feeds the bucket/source board.
- L2-B Nodes/Edges render in a large React Flow canvas. Empty data now uses a
  non-connectable Obsidian-like empty-state overlay with status chips; the old
  Blackboard/Intent/Refs/L2-B placeholder boxes were removed because they looked
  like real graph Nodes.
- Selecting a node opens a detail drawer with safe JSON detail.
- Create/update/delete node actions and edge actions use the global Settings
  `Mode`: default real operator testing calls apply routes with receipts;
  preview mode uses the existing dry-run/draft routes.
- 2026-05-14 React continuation: dragging from one React Flow node to another
  now drafts an L2-B edge through the existing Web BFF and draws a
  frontend-only preview edge. Clicking an edge opens the same inspector path.
  The receipt rail is now a timeline with a short summary before raw JSON.
- 2026-05-14 React continuation 3: successful node drafts auto-stage From/To
  edge endpoints, staged endpoints reveal a compact edge-operation panel, and
  selected/staged edges can swap endpoints or draft a retarget preview. React
  Flow `onReconnect` is wired, but it still creates a new Web dry-run edge
  preview instead of mutating an existing L2-B edge.
- 2026-05-14 terminology/interaction polish: Chinese UI now uses `Node` and
  `Edge` in the graph workspace, `dry-run` is presented as `预演`, and the
  right rail is `操作记录` with raw JSON collapsed behind details. React Flow
  now uses `ConnectionMode.Loose` so handles can connect without the confusing
  source-top/target-bottom restriction, and controlled node positions are
  updated from node-change events so preview Nodes can be dragged.
- 2026-05-14 graph interaction polish: Memory Nodes now use a custom
  Obsidian-like React Flow node renderer with four directional handles and a
  compact kind/id meta line. Draft node/edge ids now carry a random suffix so
  rapid repeated preview operations do not collide in React state.
- 2026-05-14 canvas-create polish: double-clicking an empty Memory Graph pane
  drafts a Node at the clicked React Flow coordinate through the existing
  `/api/l2b/node/draft` dry-run route. Default double-click zoom is disabled in
  this workspace so the gesture creates content instead of unexpectedly moving
  the camera.
- 2026-05-14 selection bugfix: clicking blank canvas now clears the Web detail
  selection, and React Flow Node/Edge `selected` props are driven from the same
  Web selection state. This prevents the right drawer from showing a stale
  object after the canvas itself has already cleared selection.
- 2026-05-14 viewport controls: the Memory canvas now has Web-only `Focus` and
  `Layout` controls. `Focus` centers the selected Node or both endpoints of a
  selected Edge; with no selection it fits the full graph. `Layout` reapplies a
  local circular layout to visible Nodes and then fits the viewport. These
  controls do not change L2-B data or App DTOs.
- 2026-05-17 panel and label-namespace bugfix: the active Memory tool dock and
  selected Node/Edge inspector are independent canvas panels. Operators can
  focus, close, drag by the header, and resize each panel, matching the intended
  Photoshop-like workspace direction without introducing a full dock framework.
  Follow-up polish adds a draggable icon-toolbar grip; the toolbar can snap to
  side edges and switch to a vertical dock, while floating panels snap to canvas
  edges and nearby panel edges on drag/release and after resize. The active
  tool dock and selection inspector default to a right-side stacked dock sized
  from the current canvas, then keep that dock when the operation-record rail is
  expanded/collapsed until the operator manually drags a panel elsewhere. Panel
  resizing uses explicit left-edge, bottom-edge, and bottom-left handles so
  right-docked panels can be expanded without hunting for the browser's native
  bottom-right resize corner.
  Backend fallback de-dup no longer treats the visible `label` as a global key:
  stable source identities (`obsidian_uuid`, `graphiti_uuid`, Google provider
  ids) still win first, then fallback lookup uses `NodeKind + exact label`.
  This allows `object:desk` and `zone:desk` to coexist while same-kind repeat
  writes still merge through L1.5/Ingest. Tags remain free-form labels and are
  not identity keys.
- 2026-05-14 homepage cleanup: Memory view polling is capped at 5s in the React
  shell, while Runtime keeps the configured BFF cadence. This remains polling,
  not true realtime; SSE/changed-since remains the next CORE-009 candidate.
  React Flow edges now store or infer `sourceHandle`/`targetHandle`, and Memory
  Nodes expose both source and target handles on all four sides, fixing the
  top-to-top fallback seen in the browser. Left navigation and the right records
  rail can collapse, React Flow controls/minimap/edge labels are dark-mode
  styled, records default collapsed to protect canvas width, and topbar/
  empty-state explanatory copy was reduced.
- L1.5 bucket actions are presented as bucket cards, with raw/payload work kept
  behind advanced flows.

Remaining WEB-011 work:

- Persisted edge edit/delete semantics still need an operator-gated backend
  policy. Current retarget is a draft/preview, not an in-place mutation.
- The next visual-quality slice should move from simple positioned nodes to a
  cleaner local-graph layout inspired by Obsidian Graph View: graph first,
  filters/groups/local depth second, raw payload last.
- L2-B graph-health metrics, source/bucket pressure visuals, and component/
  traversal summaries still need bounded backend computation.
- Evidence/String Board remains a renderer over CORE-006/CORE-007 candidates;
  no separate board storage model has been created.
- Browser smoke for this checkpoint confirmed the React Memory page is served
  through the normal Web Console service on port `7893` with no frontend console
  errors. Repeat this audit after each React UI slice.
- 2026-05-14 React smoke confirmed readable Chinese copy, visible connect hint,
  `l2b.node.draft` receipt, frontend preview node, receipt timeline, and zero
  console errors.
- 2026-05-14 React retarget smoke confirmed that two node drafts auto-filled
  endpoints, showed the edge-operation panel, `重定向草稿` produced an
  `l2b.edge.draft` receipt plus one preview edge, and browser console errors
  stayed at zero.
- 2026-05-14 terminology/interaction verification: `npm run typecheck` and
  `npm run build` passed; static scan confirmed the previous awkward graph and
  record Chinese labels are absent from React source/dist; local HTTP smoke
  returned `200` for `/` and `/api/app/live-state`. In-app browser automation
  timed out during this round, so visual click/drag smoke should be repeated
  when the browser bridge recovers.
- 2026-05-14 canvas-create verification: `npm run typecheck`, `npm run build`,
  Web route tests, static awkward-label scan, `git diff --check`, and local HTTP
  checks passed after adding empty-canvas double-click Node creation. Browser
  automation timed out again, so the visual double-click gesture remains a
  manual smoke item in the open browser.

## 2026-05-16 Memory Graph Policy Decisions

Source: user-reviewed Web major roadmap questionnaire; `dsg-rustworkx-master`,
`dsg-l2b-node-organization-options`, `dsg-attention-schema-papers`,
`graphiti`, and `react-force-graph-l2b` skill readback.

### Page Split

- The current React Flow page is the **L2-B operation/editor page**. It should
  specialize in WYSIWYG subgraph construction, detailed Node/Edge edits,
  Graphiti-preloaded Node review, UUID/Ref/source binding, subgraph save/rollback
  receipts, and operator-gated strong L2-B writes.
- The future full-screen L2-B page is the **render/monitor page**. It should use
  a force/canvas renderer such as React-Force-Graph, show more graph and less
  text, and focus on realtime topology, local graph depth, filters/groups,
  algorithm overlays, and attention/trigger animation.
- L1.5 Source Board belongs to a right-side source/tool dock or drawer, not in
  the selected Node/Edge inspector. Selecting a tool opens only that tool's
  controls. Avoid stacked mixed-purpose component blocks.

### Write Ownership Matrix

| Surface | What Web may edit | Durable owner | First safe policy |
|:--|:--|:--|:--|
| L2-B Node/Edge | Node create/update/delete, Edge create/update/delete, subgraph overlay apply when backend route/audit exists. | DSG L1.5/L2-B. | Default preview/dry-run; real apply requires operator mode, receipt, and rollback/backup posture for destructive operations. |
| Graphiti | Search, export to L1.5/L2-B, and future Graphiti API-level node/edge/fact surgery. | Graphiti API/FalkorDB operator adapter. | Do not pretend L2-B edits mutate Graphiti facts. Persistent Graphiti changes need Graphiti receipt/audit and operator mode. |
| Obsidian | Scan, preview, import source packs, bind by path/metadata. | Obsidian vault/source file. | Treat source files as immutable imports from Web unless a dedicated vault-edit flow is designed. `roleplay` is a mode/profile containing many source packs. |
| Google Calendar | Manual fetch/import V1, preview normalized events and mapping rows. | Google Calendar / Scheduler/Nanobot fetch result. | Preserve provider identity and status. Watch/syncToken is second-stage backend sync, not browser OAuth. |
| IntentWorkspace | Stage refs/context or request GOSLO Intent edits. | GOSLO Intent workspace/Plan files. | Do not model IntentWorkspace membership as semantic `NodeKind`; use overlay/lifecycle flags and explicit task/workspace flows. |

### Import Destination Defaults

- `workspace_only`: unresolved IntentWorkspace refs, temporary human working
  sets, and drafts that are not ready to index.
- `index_pointer`: large or immutable source documents where L2-B should store
  a lightweight pointer plus summary/tags/ref.
- `isolated_compartment`: default for Graphiti search packs, Obsidian source
  packs, Google Calendar batches, and Arknights test imports.
- `connect_by_rule`: explicit bounded operator batch only.
- `promote_to_main_graph`: explicit promotion after preview, receipt, and
  audit review.

### Graph Transform Examples To Build First

- Wrap selected Nodes/Edges as a foldable overlay/subgraph.
- Draft cross-links between two selected compartments using bounded rules.
- Promote selected compartment Nodes into the main graph.
- Split/tombstone stale or cancelled clusters without deleting provider
  identity by default.
- Send selected subgraph context to an LLM when free-form analysis is more
  useful than graph mutation.

### Delta Vocabulary Before SSE

Implementation checkpoint: 2026-05-16.

- Backend typed vocabulary now lives in `parrot.web_console.graph_policy` as
  Web-only `GraphDeltaOp`, `GraphDeltaEntityKind`, and expanded
  `GraphDeltaEvent`.
- `GET /api/memory/live-state/changes` advertises
  `event_schema=memory_runtime_delta_v1`, and every event row now carries
  `event_id`, `graph_scope`, `trace_id`, `receipt_id`, `patch`, and
  `redacted` fields. This is still polling changed-since, not SSE yet.
- `GET /api/memory/live-state/stream` is the first Web-only SSE route. It is a
  thin read-only wrapper over the same changed-since envelope and emits
  `stream_open`, `memory_delta`, and `stream_close` events. It has a bounded
  `max_events` test/debug cap, keep-alive comments, and no binary payloads.
- React Memory now opens an `EventSource` to the SSE route when the browser
  supports it. The old polling path remains active as a fallback for initial
  load, disconnects, and browsers without EventSource.
- Future SSE routes should stream the same event rows instead of inventing a
  second graph/event shape. Operator receipts remain a separate stream.
- `GraphDeltaEvent` uses stable business ids and optional patch data so React
  Flow editor and React-Force-Graph monitor can share the backend event
  vocabulary without sharing renderer layout state.
- Verification: Web route tests `48 passed`, React `npm run typecheck`,
  React `npm run build`, `py_compile` for the touched Web Console backend
  modules, and in-app browser smoke on `http://127.0.0.1:7893/` passed. The
  browser showed the Memory page with `SSE` transport and zero console errors
  after restarting the local Web Console service.

### Source Board Operator Import Checkpoint

Implementation checkpoint: 2026-05-16.

- Graphiti, Obsidian, and Google Calendar all share the same operator-safety
  posture: preview/import-plan first, then a visible secondary `Import to
  L1.5` action only when the operator explicitly executes with
  `operator_mode=true` and `dry_run=false`.
- Graphiti operator import admits selected search hits through L1.5 as
  `USER_EXPLICIT` observations and keeps Graphiti fact relationships as
  receipt `edge_drafts`; it does not directly mutate FalkorDB or RustWorkX
  edges.
- Obsidian operator import rescans the vault server-side and writes through
  `UserTagFilter -> L15Pool.admit`; `daily` and `roleplay` are still
  UUID-free setting profiles, while `ref` stays a binding profile.
- Source edits invalidate stale receipts: Calendar JSON edits, Obsidian vault
  path changes, rescans, selected-note toggles, and cleared selections all
  reset old preview/import state before new receipts are shown.
- The three `Import to L1.5` buttons use a synchronous in-flight guard plus
  disabled UI state. A second click during an operator import returns
  `operator_import_in_flight` locally instead of issuing a duplicate L1.5 admit.
- Successful Graphiti, Obsidian, and Google Calendar operator imports now
  trigger an immediate Memory refresh in React: `/api/app/live-state` plus
  `/api/l15/pool`, then emit a visible `memory.refresh_after_import` receipt
  with refreshed L2-B, L1.5 Pool, Blackboard, and IntentWorkspace counts. This
  is a UI consistency hook only; SSE/polling remains the realtime transport
  and no backend route/DTO shape changed. The refresh receipt is marked as an
  executed safe read (`dry_run=false`, `operator_mode=false`) so it does not
  look like a draft apply.
- Verification for this checkpoint: focused Graphiti/Obsidian operator import
  tests `2 passed`, full Web route tests `58 passed`, React `npm run
  typecheck`, React `npm run build`, and exact secret scan passed. The
  live-refresh/refresh-receipt continuation revalidated full Web route tests
  (`58 passed`), React `typecheck`/`build`, exact secret scan, and browser smoke
  with zero console errors.

### Calendar and Source Node Notes

- Google Calendar EVENT nodes should preserve Google `status`
  (`confirmed`, `tentative`, `cancelled`) and add Parrot lifecycle overlays such
  as `scheduled`, `tentative`, `cancelled_tombstone`, `expired`,
  `completed_manual`, or `postponed/rescheduled`. Google Tasks has separate
  task status and must not be silently folded into Calendar events.
- Edge kinds and metadata must remain extensible. RustWorkX carries topology;
  business UUIDs, edge kinds, confidence, source, provenance, and lifecycle live
  in payloads/receipts so new kinds can be added without renderer rewrites.

## Slice: Memory Graph Workspace

### A. Source Readback

- `build_l2b_snapshot()` already exposes a bounded read-only L2-B graph
  snapshot without requiring Web to learn RustworkX internals.
- L1.5 already has Pool, Buckets, RefTable, timeline, scene snapshot, and
  admission concepts for external refs such as Obsidian, photos, Google
  Calendar, URLs, and other future sources.
- Photo observer code stages photo refs through IntentWorkspace/L1.5/L2-B;
  Graphiti/FalkorDB management stays in the dedicated Graphiti business file.

### B. Existing Core Interfaces

Yes for read-only visualization and inspection.

Initial composition:

- L2-B graph view: `build_l2b_snapshot(limit=...)`.
- Photo refs: `AppFirstVersionFacade.list_photo_refs()` and IntentWorkspace
  PHOTO refs.
- Ref inspection: current session RefBinding registry plus L1.5 RefTable
  reads where available.
- L1.5 management: start with status, bucket list, rejected/admitted counts,
  and ref health summaries before any mutation.
- L1.5 management is not Web-exclusive: the App phone/menu path also needs a
  safe subset, so shared read/write shape belongs in the core candidate queue.

### C. Missing Core Surface

Read-only Web views can start with Web-owned adapters.

Shared write or renderer-agnostic board contracts require the candidate queue:

| Candidate | Needed for | Route |
|:--|:--|:--|
| CORE-006 `MemoryRefBindingApi` | Add/remove/retarget refs and typed visual edges shared by App and Web. | Candidate queue; no SSOT edit yet. |
| CORE-007 `CanvasMenuCoreV1` | Shared canvas/read/apply/preset boundary and typed canvas nodes/edges. | Candidate queue; no SSOT edit yet. |
| CORE-008 `L15ManagementApi` | L1.5 bucket/ref/source health and safe management subset shared by Web Console and App phone/menu surfaces. | Candidate queue; no SSOT edit yet. |

Web-only node CRUD and photo management can be designed under Web business
interfaces, but risky writes must use operator mode with dry-run, audit, and
rollback/backup posture. App DTOs must not receive Graphiti/FalkorDB operator
fields.

### D. Observable Completion Signal

- Web renders L1.5 bucket/ref health and shows whether each source path is
  healthy, unverified, stale, broken, missing, or adapter-not-yet-built.
- Web can distinguish L1.5 operations that are App-safe from Web-operator-only
  actions before any write is implemented.
- Web renders a bounded L2-B graph with node kind, confirmation, attention,
  salience, bucket/source, edge kind, strength, and cross-compartment markers.
- Node detail drawer shows source refs, Graphiti UUIDs when present, photo refs,
  episode/event ids, and last-seen/activation indicators if the source exposes
  them.
- Photo management shows staged previews/assets, related node id, expiry, and
  awareness linkage without pretending Python owns Unity pixels.
- Evidence/String Board can render typed refs and edges with a Web-selected
  layout, but stores no separate board-specific graph model.
- Any CRUD or surgery action first produces a draft/dry-run/audit entry and
  clearly labels whether it is Web-only or shared-core-blocked.

### Implementation Signal: 2026-05-13

Done for the first WEB-003 read-only slice:

- Static frontend first enabled the `Memory Graph` place in legacy
  `web/console/`; WEB-012 now serves the React + Vite Memory workspace from
  `web/console_dist/` when the build is present.
- Data source is the existing Web BFF route `GET /api/app/live-state?limit=80`,
  backed by `src/parrot/brain/app_live_state.py`.
- The view renders Blackboard declared/present count, IntentWorkspace refs,
  RefBinding count, L2-B node/edge count, placeholder graph lanes when no nodes
  exist, and tool-artifact presence cards for camera/photo awareness, focus,
  BoundaryBox, workdesk notes, XRHand, and settings.
- Browser verification at `http://127.0.0.1:7893/` showed the local snapshot as
  `Blackboard 0/55`, `Refs 0`, `L2-B 0/0`, four memory lanes, four placeholder
  graph nodes, six tool cards, and no frontend console errors.
- Boundary: this slice is read-only. L1.5 bucket management, node/photo CRUD,
  Ref/Edge retargeting, and Evidence/String Board editing remain future Web
  operator flows with draft/dry-run/audit; shared DTO gaps stay in CORE-006,
  CORE-007, and CORE-008.

Done for the first WEB-010 visual slice:

- The Memory Graph view now splits live read surfaces into Blackboard key rows,
  IntentWorkspace ref rows, L2-B graph canvas, tool artifacts, and one detail
  panel instead of relying only on summary cards.
- L2-B rendering uses a bounded SVG graph canvas. When real L2-B nodes/edges
  are present it draws nodes, edge lines, cross-compartment dashed markers,
  attention-based node radius/tone, top-attention labels, and click selection.
- When L2-B is empty, the same area shows a graph-shaped placeholder linking
  Blackboard, IntentWorkspace, Refs, and L2-B so the operator sees the intended
  data flow without fake memory data.
- Blackboard rows show key, scope, writer, and safe summary. IntentWorkspace
  rows show title/ref id, kind, owner, and expiry. Selecting a key/ref/node
  updates the detail panel.
- Browser verification at `http://127.0.0.1:7893/` confirmed the new panels
  render, selection updates details, and there are no frontend console errors.

Done for the first operator-safe WEB-003 / WEB-010 draft slice:

- Web-only BFF module `src/parrot/web_console/memory_ops.py` added the L1.5
  and L2-B management adapters without changing App DTOs.
- New read route: `GET /api/l15/pool` returns pool health, buckets, ref health,
  timeline, and current scene. It is a Web management snapshot, not a shared
  App contract.
- New L1.5 draft/apply routes:
  `/api/l15/bucket-op/draft`, `/api/l15/bucket-op`,
  `/api/l15/obsidian-node/draft`, and `/api/l15/obsidian-node`.
  Daily/roleplay Obsidian setting nodes may be UUID-free; `profile=ref`
  requires an Obsidian UUID. Real apply publishes the normalized Obsidian event
  to `CH_DSG_EVENTS` only with explicit operator mode.
- New L2-B draft/apply routes:
  `/api/l2b/node/draft`, `/api/l2b/node`, `/api/l2b/node/delete`,
  `/api/l2b/edge/draft`, and `/api/l2b/edge`. Node create/update drafts use
  `Observation(source=USER_EXPLICIT)` and real apply goes through
  `L15Pool.admit`; delete goes through `L15Pool.evict`; edge apply uses
  `SemanticEdge` and writes only in operator mode.
- Frontend Memory Graph now fetches both `/api/app/live-state` and
  `/api/l15/pool`, keeps the main graph simple, and places L1.5/Obsidian/L2-B
  draft receipts in a collapsed Operator Workbench.
- L2-B Node CRUD controls now expose create draft/create dry-run/update
  dry-run/delete dry-run. Update dry-run requires a target UUID and carries it
  as `observation.meta.target_node_uuid`; it still goes through
  `L15Pool.admit(Observation(source=USER_EXPLICIT))` rather than direct graph
  mutation.
- L2-B Edge controls now expose both edge draft and edge dry-run. Edge dry-run
  calls `/api/l2b/edge` with `operator_mode=false`, validates the
  `SemanticEdge` shape, and returns `would_apply` plus operator-only guard
  metadata without mutating the graph.
- Operator Workbench now exposes L1.5 bucket operation controls for
  `freeze`/`unfreeze`/`clear`/`import` draft and dry-run receipts. Real bucket
  mutation remains blocked unless server-side `operator_mode=true` is
  explicitly provided.
- The L2-B SVG renderer now has kind/source/bucket/min-attention filters and
  highlights new or changed nodes between polling snapshots with a green
  breathing marker. This is still polling diff, not SSE/WebSocket.

Done for the first WEB-010 grouping/link visual slice:

- Blackboard rows now render as `scope / writer` groups instead of one flat
  list. Event-driven keys are tagged so operator eyes can separate durable
  state from reactive keys.
- IntentWorkspace rows now render as `role-or-kind / owner` groups and mark
  refs that already link to a node or intent event.
- The L2-B SVG renderer now draws soft IntentWorkspace and RefBinding links to
  visible L2-B nodes when `related_node_uuid` or `resolved_l2b_targets` are
  present. This is a renderer overlay; it does not create a new board storage
  model or shared DTO field.
- Blackboard keys and IntentWorkspace refs now reuse the same client-side
  polling diff pass: changed rows get a green marker and localized `changed`
  badge, while the first load stays quiet to avoid visual noise.
- The L2-B graph now has Web-only bounded render modes: full graph, selected
  node neighborhood, and top-attention subset. These modes only change the
  client-side SVG projection of `GET /api/app/live-state`; they do not add a
  new backend route or alter L2-B DTOs.
- Visible L2-B edges now show lightweight path hints: selected-node edges are
  emphasized, low-density graphs show edge-kind badges, and `cross_compartment`
  edges get a localized cross-compartment badge. This remains renderer-only.
- A Web-only Blackboard activity route now exposes
  `GET /api/memory/blackboard/activity?limit=...` from
  `py_trees.blackboard.Blackboard.activity_stream`. The browser renders it in a
  collapsed Blackboard Activity drawer; values are summaries-only, bounded, and
  read-only.
- The browser smoke on `http://127.0.0.1:7893/` after server restart showed
  `L2-B 0 / 0`, three Blackboard groups, one graph canvas, and no fresh console
  errors. The local session has no L2-B nodes, so ref-link count was correctly
  zero.

### Interface Matrix: L1.5/L2-B Operator Drafts

Checkpoint: 2026-05-13. These routes are Web Console business interfaces, not
shared App DTOs. They are intentionally receipt-first so later Web operator
flows can be audited without inventing a second memory write path.

| Endpoint | Purpose | Backend adapter | Safety rule |
|:--|:--|:--|:--|
| `GET /api/l15/pool` | Inspect pool health, buckets, ref health, timeline, and scene snapshot. | `build_l15_pool_snapshot()` | Read-only Web management view. |
| `POST /api/l15/bucket-op/draft` | Preview freeze/unfreeze/clear/import-style bucket operations. | `draft_l15_bucket_op()` | Draft only; no pool mutation. |
| `POST /api/l15/bucket-op` | Execute a bucket operation when explicitly allowed. | `apply_l15_bucket_op()` -> `L15Pool.apply_bucket_op` | Default dry-run; real apply requires `operator_mode=true`. |
| `POST /api/l15/obsidian-node/draft` | Draft an Obsidian setting/ref node event. | `draft_obsidian_setting_node()` | `daily`/`roleplay` can be UUID-free; `ref` must bind an Obsidian UUID. |
| `POST /api/l15/obsidian-node` | Publish normalized Obsidian node event to the trigger bus. | `apply_obsidian_setting_node()` -> `CH_DSG_EVENTS` | Default dry-run; real publish requires operator mode. |
| `POST /api/l2b/node/draft` | Draft L2-B node create/update as an explicit user observation. | `draft_l2b_node()` | No direct graph mutation. |
| `POST /api/l2b/node` | Admit a user-explicit observation through L1.5. | `apply_l2b_node()` -> `L15Pool.admit` | Keeps L1.5/Ingest as the write gate. |
| `POST /api/l2b/node/delete` | Draft/execute L2-B node eviction. | `delete_l2b_node()` -> `L15Pool.evict` | Default dry-run; real eviction is operator-only. |
| `POST /api/l2b/edge/draft` | Draft source/target/kind/strength/source/meta for a semantic edge. | `draft_l2b_edge()` | Validates edge shape and rejects same-node self-edge drafts. |
| `POST /api/l2b/edge` | Connect two L2-B nodes with a `SemanticEdge`. | `apply_l2b_edge()` -> `L2BGraph.connect` | Operator-only real write; receipt includes audit hints. |
| `POST /api/l2b/edge/update` | Draft/execute replacement of an existing L2-B edge payload. | `apply_l2b_edge_update()` -> `L2BGraph.update_edge_between` | Default dry-run; matches by endpoints plus optional `match_kind` / `match_source`, not by RustWorkX edge index. |
| `POST /api/l2b/edge/delete` | Draft/execute L2-B edge removal. | `delete_l2b_edge()` -> `L2BGraph.remove_edge_between` | Default dry-run; real delete requires operator mode and removes the first matching directed edge. |
| `GET /api/memory/blackboard/activity` | Inspect recent py-trees Blackboard activity. | `build_blackboard_activity_snapshot()` -> `Blackboard.activity_stream` | Read-only, Web-only, bounded, summaries-only; starts activity capture if py-trees has not enabled it yet. |

2026-05-17 operator-mode audit:

- React Memory Canvas now uses the top-level Settings `Mode` for direct
  L2-B/L1.5 edits. Default is real operator testing, so direct Node create,
  Edge create/update/delete, Node delete, L1.5 bucket freeze/unfreeze/clear,
  Obsidian setting-node publish, and Source Board execute buttons call their
  apply routes with `dry_run=false` and `operator_mode=true`. Switching Mode to
  preview keeps those same buttons on dry-run receipts.
- This does not change the architecture boundary: Node create/update still goes
  through `L15Pool.admit(Observation(source=USER_EXPLICIT))`, Node delete still
  goes through `L15Pool.evict`, and Edge surgery still uses endpoint plus
  optional kind/source matching rather than exposing RustWorkX edge indexes.
- Destructive operator deletes ask for browser confirmation. Source-import
  plans (`Graphiti`, `Google Calendar`, `Obsidian`) still show explicit
  preview/import-plan receipts, but their execute/import buttons obey the same
  global Mode rather than carrying separate local dry-run toggles.

### Audit: 2026-05-13 Requirement Alignment

Useful pieces completed:

- `GET /api/app/live-state?limit=...` is a valid Web read model for Blackboard,
  IntentWorkspace, Ref registry, L2-B, and tool-artifact inspection.
- The Memory Graph view proves the browser can poll and render these surfaces
  without leaking writes or pulling Web-only fields into App DTOs.
- The renderer already has lanes for Blackboard, IntentWorkspace, Refs, L2-B,
  and tool artifacts, so it can become the shell for a better graph/canvas.
- L1.5/L2-B operator routes now exist and are documented. Backend routes still
  require operator flags for real writes, while the React test bench defaults
  to real connection Mode and leaves preview Mode available for dry-run audits.

Current drift / insufficiency:

- The implemented Memory Graph is still a bounded polling renderer. It now has
  client-side L2-B/Blackboard/IntentWorkspace diff highlighting, but no
  SSE/WebSocket lane exists yet.
- L2-B now has graph filters, draft CRUD receipts, bounded render modes, and
  visible edge path hints, but it does not yet offer traversal depth,
  cross-source link inspection, or graph health metrics.
- Blackboard now groups by scope/writer, highlights row changes between
  polling snapshots, and exposes a backend-backed py-trees activity drawer. It
  still does not provide a durable cross-process history or SSE stream.
- IntentWorkspace now groups refs by role/kind owner and can draw visible links
  to L2-B / RefBinding targets, but Graphiti UUID/provenance linking is still
  partial.
- Evidence/String Board remains a boundary/design note, not an implemented Web
  board.

Conclusion: keep the completed smoke/read models, but shift the next Web-heavy
task toward real-time rendering of the memory system. More generic panels or
operator buttons should wait until the L2-B/Blackboard/IntentWorkspace visual
base is genuinely useful.

### Investigation: Real-Time Rendering Interfaces

Checkpoint: 2026-05-13. Source readback used `src/parrot/brain/app_live_state.py`,
`src/parrot/brain/l2b_monitor.py`, `src/parrot/web_console/runtime_monitor.py`,
`src/parrot/brain/plan/plan.py`, and `src/parrot/brain/plan/plan_registry.py`.

Existing fields are enough for the first visual pass:

- `GET /api/app/live-state` returns `generated_at` and `sequence`, so the Web
  renderer can keep client-side polling diffs without changing core contracts.
- Blackboard rows already include `key`, `scope`, `writer`, `type_hint`,
  `event_driven`, `exists`, `summary`, plus `scopes` and `present_keys`.
- IntentWorkspace rows already include `ref_id`, `kind`, `owner_id`, `origin`,
  `role`, `workspace_id`, `title`, `related_node_uuid`,
  `related_intent_event_id`, `payload_source`, size, expiry, and pressure.
- Ref registry rows expose `counts_by_kind` and `resolved_l2b_targets`, which
  can drive visual ref-to-node links before a full shared Ref API is ratified.
- L2-B nodes expose `uuid`, `label`, `kind`, `attention`, `salience`,
  `confirmation`, `bucket_id`, `event_id`, `scene_type`, `location_tag`, and
  `source`; edges expose `source`, `target`, `kind`, `strength`,
  `edge_source`, and `cross_compartment`.
- Plan rows from `/api/runtime/monitor` expose plan id/title/state,
  intent/episode links, step counts, step states, step ids, expected tools,
  `nanobot_task_id`, `result_ref_id`, and errors. The underlying plan model
  also has `depends_on`, so a Web DAG adapter can be added without inventing a
  new Plan system.

Gaps to handle in the Web lane first:

- Web-only Memory changed-since V1 now exists as
  `GET /api/memory/live-state/changes?since=...&limit=...`. It wraps the
  current live-state snapshot, keeps a stable content sequence for Web, and
  lets React skip no-op repainting. It is still polling/diff, not an event
  stream.
- py-trees Blackboard activity is now visible through a bounded Web drawer, but
  it remains an in-process recent activity stream, not durable history.
- Plan rendering now has a Web-only DAG, ready/blocked/critical hints, and
  clickable step detail. It is still polling, not a streaming task timeline.
- L2-B graph health still lacks traversal-depth, top-attention path, component,
  and subgraph metrics. Per the rustworkx skill, keep whole-graph algorithms
  server-side and bounded; the browser should render selected subgraphs.
- Ref/Edge retargeting and board storage remain CORE-006/CORE-007 territory.
  Web can render links from current fields, but shared write contracts should
  stay in the candidate queue until App/Web both confirm them.

Next implementation order:

1. Use the Web-only changed-since route as the Memory polling baseline. Only
   after the monitor design is stable, evaluate SSE/WebSocket over the same
   sequence/event vocabulary. Do not promote this to core unless the App needs
   the same stream.
2. Add L2-B graph-health metrics when the server can compute bounded component,
   traversal-depth, or top-attention path summaries safely.

## Next Large Plan: WEB-010 Real-Time Memory Visualizer

Owner chat: Web Console
Status: in_progress
Related TODO: WEB-010

Purpose: turn the existing read-only memory snapshot into an operator-grade
real-time visualization for L2-B, Blackboard, and IntentWorkspace. This is a
large task and should start with research/planning before implementation.

### Phase 0. Audit And Research

- Inventory exact fields emitted by `build_app_live_state()`,
  `build_l2b_snapshot()`, Blackboard schema, IntentWorkspace handles, and
  RefBinding registry.
- Research graph interaction patterns for dense operational graphs: Obsidian
  graph/canvas, React Flow edge editing, Cytoscape.js subgraph exploration, and
  evidence/string-board workspaces.
- Decide the first renderer split: management graph first, Evidence/String Board
  later as a separate renderer over shared Ref/Edge data.

### Phase 1. Real-Time Read Model

- Keep `GET /api/app/live-state` as the stable polling baseline.
- Add a Web-only diff/event stream only after the polling renderer proves useful
  enough to justify it. Candidate transports: short-interval polling with
  sequence numbers first, then SSE/WebSocket if visual latency becomes a real
  problem.
- Preserve ownership boundaries: Blackboard/IntentWorkspace/L2-B remain the
  writers; Web only reads until operator drafts exist.

### Phase 2. Visual Renderer

- L2-B graph canvas: render actual nodes and edges with kind, source, attention,
  salience, confidence, activation, and top-attention highlights when present.
- Blackboard view: group by scope and writer, show present/missing/event-driven
  state, and show safe summaries before raw values.
- IntentWorkspace view: group refs by role/kind/owner/expiry, show memory
  pressure, and draw visual links to L2-B nodes / RefBinding targets where
  available.
- Detail drawer: one selected node/ref/key shows provenance, source refs,
  Graphiti IDs, episode/event ids, last-seen/expiry, and audit-safe actions.

### Phase 3. Interaction Boundary

- Add filtering/search/layout controls before any write controls.
- Operator actions such as node CRUD, ref retarget, edge edit, or trigger fire
  must generate drafts/dry-runs/receipts first.
- Do not create a separate Evidence Board storage model. Board modes consume
  shared Ref/Edge data plus renderer/style ids after CORE-006/CORE-007 are
  confirmed.

## Renderer Boundary

Evidence Board, String Board, graph canvas, and node table are Web renderers.
They may choose different layouts and interaction patterns, but they should
consume the same future Ref/Edge DTOs as App once CORE-006/CORE-007 are
confirmed.

Renderer choices must stay behind data-level indirection:

- `edge_kind`: semantic relation such as supports, contradicts, seen-with,
  same-entity, task-blocks, provenance, red-string, or manual-hypothesis.
- `visual_style_id`: lane-selected look such as plain-line, red-string,
  dashed-audit, photo-pin, or future game/workbench styles.
- `renderer_id`: Web graph, Web evidence board, Unity canvas menu, Unity 2D
  workspace, or future scene-specific renderer.
- `workspace_id`: board/canvas/workspace instance, so the same Ref/Edge can be
  visualized differently without duplicating memory.

Start with the same plain canvas renderer for Web and App if that is the fastest
path, but keep Red String, Murder Board, Evidence Board, and future board modes
as renderer/style choices, not separate storage models.

## Management Surface

The comprehensive Web view should eventually cover these operations, with read
models first and writes behind draft/dry-run/audit:

- L1.5: list buckets/sources, inspect admission/rejection, verify source health,
  mark/repair stale refs, and expose the App-safe management subset.
- L2-B: bounded visualize/search/filter, inspect node/edge payloads, draft node
  CRUD, draft edge CRUD, merge/alias/correction proposals, and manual trigger
  fire/manage where the backend exposes a safe trigger envelope.
- Ref/Edge: create, delete, retarget, annotate, set edge kind, set visual style,
  and link photos/docs/UI artifacts to L2-B or Graphiti IDs.
- Photos: staged preview, source path, related node/ref, expiry, awareness
  linkage, and operator repair without claiming ownership of Unity pixels.
- Evidence/String Board: Web version of board layout, WYSIWYG edge editing, and
  audit-aware action history.

## Interaction Research Queue

Base management uses the Obsidian-like console and canvas. After the core panels
are complete, evaluate richer interactions for the board/workbench layer:

- Papers Please-style desk: documents/photos as objects, stamps, rulebook,
  queue, comparison, contradiction markers, and operator decision receipts.
- React Flow-style editing: handles, reconnect edge, context menu, minimap,
  lasso/grouping, undo/redo, and save/restore.
- Cytoscape-style graph exploration: render only relevant subgraphs, switch
  layout by question, and avoid whole-graph noise.
- Asset management: use address/label-style indirection similar to Unity
  Addressables for board skins, pins, strings, stamps, paper, and future game
  assets. Keep these asset ids outside the shared memory DTO payload.

## Requirement Reframe: WEB-011 Visual Memory Operations Cockpit

Owner chat: Web Console
Status: approved
Related TODO: WEB-011
Research anchors: React Flow terms/reconnect/performance docs, Cytoscape.js
compound nodes/layout docs and layout tutorial, JSON Canvas 1.0 spec, D3 force
paper/docs, VIS 2024 overview+detail compound graph paper.

### Current State Answer

- Current Web Console views are not push real-time. The frontend has an
  active-view timer (`refreshMs`, default 15 seconds), a manual Refresh button,
  and Pause/Resume. Only the active view is refreshed on the timer.
- The current Memory Graph already does polling diff highlights for L2-B,
  Blackboard, and IntentWorkspace rows, but it still feels like manual refresh
  because there is no Web event stream, no low-latency changed-since endpoint,
  and too much of the interaction lives in dense forms.
- Menu Canvas hot-switch is partly present through
  `POST /api/app/workspace/apply` plus canvas refresh. It is not yet a complete
  hot-switch UX because it lacks optimistic selection, receipt timeline,
  transition/highlight of changed canvas nodes, automatic active canvas diff,
  and failure rollback messaging.

### Product Requirements Captured

- Replace the crowded Memory Graph/Operator Workbench with a large visual
  operations cockpit. The first screen should be a big graph/workspace area,
  not a stack of cards and forms.
- DSG whole-state visualization should show L2-B, Blackboard,
  IntentWorkspace, Refs, Plan/task, and trigger/runtime signals as connected
  lanes or compartments.
- Blackboard, IntentWorkspace, and L2-B should update automatically. Start with
  faster active-view polling plus sequence diffs; move to Web-only
  `changed_since` or SSE only when the renderer proves useful enough.
- L2-B CRUD should be direct-manipulation first: select node on canvas,
  inspect, edit label/kind/source, create node from the canvas, delete with
  receipt, drag/connect edges, and reconnect/retarget edges through a dry-run
  receipt.
- Advanced JSON and dangerous operator actions must move to drawers. Default
  interaction should be click, select, filter, drag, connect, and confirm.
- L1.5 management should become simple bucket/source cards with health,
  capacity pressure, freeze/unfreeze/verify/clear/import draft buttons, and
  compact receipts. Raw payload JSON stays behind an advanced drawer.
- Trigger management should have manual action buttons and a trigger palette:
  message push, Gmail/Nanobot message check, LLM/context push, Calendar test,
  Obsidian setting node, Graphiti episode, and DSG custom event draft/fire.
  Real fire stays operator-mode only.
- Visualizations may become separate workspaces/pages when the data is complex:
  `Memory Ops`, `Runtime Flow`, `Menu Canvas`, and later
  `Evidence/String Board`. The nav should not force all visualizations into one
  scroll-heavy page.
- Visual style remains Obsidian-like for normal console/control surfaces.
  Papers Please-style desk interactions are later, for focused evidence/task
  workflows after the plain operational cockpit is useful.

### Research Conclusions

- React Flow is a good reference for direct graph editing: custom nodes,
  handles/ports, draggable connection lines, selected node/edge state,
  selection boxes, custom edges, and reconnect flows. This informs the L2-B
  CRUD interaction model even if the current static frontend does not migrate
  to React immediately.
- Cytoscape.js is the best near-term reference for dense operational graphs:
  compound nodes, subgraph layouts, viewport events, layout choice by question,
  and running layouts on subsets. This matches L2-B/Blackboard/IntentWorkspace
  compartments better than a hand-grown SVG once graphs become dense.
- JSON Canvas is useful as an import/export/layout reference for board-like
  workspaces because it has explicit node/edge arrays and positioned nodes. It
  should not become the core memory DTO.
- D3 force remains useful for lightweight animated breathing layouts and small
  live graphs, but direct editing, edge handles, and large-graph operations are
  easier to keep sane with a graph/canvas library.
- Overview+detail compound graph research supports the product direction:
  keep high-level groups salient while allowing focused expansion into nested
  detail, instead of flattening everything into one dense node cloud.

### Detailed TODO Order

1. Audit current refresh/hot-switch facts.
   Record every active polling route, refresh interval, manual refresh button,
   and current workspace apply path. Do not call it real-time until an event or
   changed-since lane exists.

2. Split the Memory Graph page into a cockpit shell.
   Top: compact live status and transport indicator. Center: large visual
   canvas. Left: filter/source buckets. Right: inspector/actions. Bottom:
   receipt/timeline. Raw JSON and broad forms move into collapsible drawers.

3. Build active-view live baseline.
   Lower the Memory Ops active polling interval only for this workspace, show
   a visible live/pause/manual state, diff by `sequence`, animate new/changed
   nodes with green breathing markers, and avoid full visual rebuilds when the
   selected item can be preserved.

4. Render DSG whole-state as compartments.
   L2-B graph is central. Blackboard keys, IntentWorkspace refs, Refs, Plan
   steps, and trigger receipts become grouped side/halo compartments with
   visible links to selected L2-B nodes where current fields support it.

5. Direct L2-B canvas operations.
   Click node to inspect. Double-click or toolbar create to draft a new node.
   Edit selected node in the inspector. Delete selected node via dry-run
   receipt. Drag from a node handle to create an edge draft. Reconnect edge
   endpoints via draft receipt. Real writes remain explicit operator mode.

6. Simplify L1.5 pool management.
   Replace the bucket form stack with source/bucket cards: status, count,
   pressure, last activity, health reason, and action buttons. Advanced payload
   JSON stays in a drawer for import/debug only.

7. Add a manual trigger/action palette.
   Buttons should generate draft receipts for common operator actions:
   `message_push`, `message_check`, `llm_context_push`, `calendar_event`,
   `obsidian_setting_node`, `graphiti_episode`, and custom DSG event. Execute
   stays dry-run by default unless operator mode is explicit.

8. Complete Menu Canvas hot-switch UX.
   Workspace/profile choices become large chips or a visual switcher. Apply
   uses the existing route, shows an optimistic pending state, then refreshes
   the canvas with changed-node highlights and a receipt/failure message.

9. Evaluate transport upgrade.
   If active polling still feels stale after the cockpit is usable, add a
   Web-only `changed_since` endpoint for Memory Ops. Promote a shared stream
   candidate only if App also needs the same realtime sequence/diff contract.

10. Library decision checkpoint.
    If vanilla SVG becomes hard to maintain, evaluate a bounded migration:
    Cytoscape.js first for dense Memory Ops graphs; React Flow later only if
    workflow/editor semantics dominate; tldraw later for Evidence/String Board
    freeform desk work.

11. Audit after every implementation round.
    Check route index, business docs, no App DTO pollution, no secret leak,
    no broad admin controls without receipts, no UI density regression, and
    browser smoke/console errors.

### Implementation Round: WEB-011.1 First Cockpit Shell

Status: done

Changed in this slice:

- Replaced the Memory page's dense stack of panels with a first cockpit shell:
  compact Memory lanes, left L1.5 source rail, larger central L2-B canvas,
  right selected-node inspector/actions, bottom Blackboard/Intent/Tool lanes,
  and an advanced drawer for Obsidian setting-node drafts.
- Preserved existing Web BFF routes and DOM ids for L1.5, L2-B node, L2-B edge,
  Blackboard, IntentWorkspace, and receipt flows. No new route or shared DTO was
  added in this slice.
- Added direct selected-node helpers: clicking a L2-B node fills safe
  update/delete UUID targets, and inspector buttons can set the selected node as
  edge `From` or `To`.
- Added first L1.5 bucket-card quick actions. Each visible bucket now has
  freeze/unfreeze/clear buttons that fill the existing bucket operation form and
  call the existing draft route. Import/raw JSON stays in the drawer.
- Increased the L2-B SVG workspace coordinate system from `720x360` to
  `960x520` and fixed the narrow-viewport filter-bar overflow found in browser
  smoke.
- Changed the Memory active-view cadence from global 15s polling to a bounded
  5s polling loop while the Memory view is active. This is still polling, not a
  push stream.

Verification:

- `node --check web\console\assets\app.js`
- Duplicate `id="..."` scan for `web/console/index.html`: clean.
- In-app browser smoke at `http://127.0.0.1:7893/`:
  Memory nav opens, cockpit strings are present, no console errors, and the
  1280px viewport no longer clips the filter controls.
- L1.5 quick action smoke: `main` freeze draft button returned a receipt through
  the existing bucket draft route with no console errors.

Round audit:

- No App/Unity DTOs were changed.
- No Web-only operator field was promoted to shared core.
- No secret is rendered into frontend JSON or DOM.
- Business notes stayed in this file plus the Web lane TODO board; no scattered
  new docs were created.
- Remaining product risk: with zero L2-B nodes, the central graph is still a
  placeholder. WEB-011.3 should be tested again once real nodes exist or after a
  dry-run/create path can display staged nodes.

### Implementation Round: WEB-011.3/011.6/011.7 Visual Feedback Patch

Status: in_progress

Changed in this slice:

- Reworked the empty L2-B canvas state into a DSG compartment map. Even when
  there are no L2-B nodes, the central workspace now shows Blackboard,
  IntentWorkspace, Refs, L1.5, and L2-B as visible state compartments instead of
  a mostly empty grid.
- Added frontend-only L2-B draft preview state. Successful L2-B node draft/apply
  dry-run receipts now render a ghost node on the canvas. Delete/update receipts
  mark matching existing nodes when present. Edge receipts are staged for ghost
  edge rendering when both endpoints are visible.
- Preview nodes now participate in the same selected-node affordances as
  persisted L2-B nodes: clicking the ghost node keeps the detail inspector on
  the node, exposes preview status, and lets the operator set Edge From/To from
  the visual selection.
- Added a center-stage canvas action bar for the common graph operations:
  create preview, use selected, set Edge From/To, draft edge, and clear preview.
  These buttons reuse the existing Web dry-run/draft routes and do not add a
  backend interface.
- Fixed a preview cleanup bug: `Clear Preview` now clears stale selected ghost
  nodes and any `draft:` UUIDs left in target/delete/edge fields so later edge
  drafts cannot resurrect a removed preview endpoint.
- Fixed a self-edge bug: From and To with the same UUID previously returned a
  success receipt but produced a zero-length invisible edge. The frontend now
  guards it locally, and the Web BFF returns `self_edge_not_allowed` if called
  directly.
- Fixed a placeholder-endpoint bug: the DSG compartment nodes used for the
  empty/overview canvas are visual read-model markers, not L2-B nodes, so they
  are no longer allowed to populate edge From/To or create React Flow draft
  edges.
- Fixed a receipt-trust bug: node and edge ghost previews now render only after
  a successful draft receipt. Failed API/network actions produce local failure
  receipts and do not create optimistic canvas artifacts.
- Added an explicit `Clear Preview` control in the receipt area so renderer-only
  draft state cannot be mistaken for committed L2-B data.
- Blackboard rows now render as status-light cards grouped by scope/writer.
- IntentWorkspace rows now render as status-light cards grouped by role/owner.

Interface boundary:

- No backend route or shared DTO changed in this patch.
- The ghost preview is a Web renderer state derived from existing receipts. It
  is not persisted and does not imply a committed L2-B node.
- Blackboard and IntentWorkspace rendering still consumes the existing
  `/api/app/live-state` read model.

Verification:

- `node --check web\console\assets\app.js`
- Duplicate `id="..."` scan for `web/console/index.html`: clean.
- In-app browser Memory smoke:
  DSG state map strings are present and no console errors were reported.
- L2-B create preview smoke:
  clicking the former create-dry-run button produced one
  `.memory-svg-node.preview` with no console errors.
- L2-B preview edge smoke:
  after reloading `http://127.0.0.1:7893/`, the browser created two dry-run
  preview nodes, staged one edge draft between them, rendered one
  `.memory-edge.preview`, and confirmed the selected preview-node detail panel
  included preview state with zero console errors.
- Canvas toolbar smoke:
  after reloading the Web Console, all seven toolbar controls were present; the
  toolbar create action produced one `.memory-svg-node.preview`, selecting it
  updated the canvas selection pill, and toolbar clear removed the preview with
  zero console errors.
- Preview cleanup regression smoke:
  created two preview nodes, staged one preview edge, cleared previews, then
  clicked draft edge again. Preview nodes stayed at `0`, preview edges stayed at
  `0`, the selection pill returned to the generic selection label, and browser
  console errors stayed at `0`.
- Self-edge regression smoke:
  created one preview node, set it as both From and To through the canvas
  toolbar, then clicked draft edge. The browser rendered `0` preview edges,
  showed the local guard receipt, and reported `0` console errors.
- Edge retarget smoke:
  after reloading the React Web Console, two successful node drafts auto-filled
  From/To, the edge-operation panel appeared without requiring a precise click
  on a thin line, `重定向草稿` returned an `l2b.edge.draft` receipt, one
  `.react-flow__edge.preview-edge` rendered, swap copy was visible, and browser
  console errors stayed at `0`.

Remaining work:

- Add dedicated Blackboard/Intent visual lanes instead of only grouped cards.
- Consider auto-expiry for stale frontend previews after a later usability pass.

### Implementation Round: WEB-011.4 L1.5 Health Visual Patch

Status: in_progress

Changed in this slice:

- React Memory Graph now renders a compact L1.5 pool health strip above the
  bucket board. It surfaces total admitted nodes, Ref count, capacity pressure,
  and current scene from the existing `/api/l15/pool` read model.
- Bucket cards now include proportional node-count meters, frozen/open state,
  and last-activity text. This makes the pool board usable as a quick status
  surface instead of a dense list of nearly identical bucket names.
- React Memory now includes a compact Obsidian setting-node draft card. It uses
  the existing `/api/l15/obsidian-node/draft` route, supports the three backend
  profiles (`daily`, `roleplay`, `ref`), keeps `daily` and `roleplay`
  UUID-free, and surfaces the `ref` UUID requirement as a local warning/failure
  receipt before the BFF call.
- BFF normalization now treats blank/whitespace-only setting labels as missing
  and falls back to `Web Console setting`. This keeps generated
  `obsidian_note_key` values meaningful for UUID-free setting drafts.
- No backend route, shared DTO, or App-facing contract changed in this slice.
  The UI still consumes the existing Web-only L1.5 management snapshot and
  existing bucket/Obsidian draft routes.

Verification:

- `cd web\console_app; npm run typecheck`
- `cd web\console_app; npm run build`
- `uv run pytest tests\test_web_console\test_web_console_server.py -q`
  -> `17 passed`.
- In-app browser smoke at `http://127.0.0.1:7893/`: Memory page rendered the
  L1.5 pool health labels (`池健康`, `压力`, `最后活动` in zh) with zero console
  errors.
- Obsidian card smoke: `daily` draft produced a `l15.obsidian_node.draft`
  receipt; switching to `ref` without UUID showed the UUID warning and produced
  `ref_profile_requires_obsidian_uuid`; browser console errors stayed at zero.
- Regression coverage: Web route tests assert the blank-label fallback, and
  browser smoke confirmed rapid repeated local guard failures produce distinct
  receipt ids with zero console errors.
- Bugfix verification: frontend typecheck/build passed, Web route tests
  reported `17 passed`, and browser smoke kept Memory/Runtime console errors at
  zero after the preview guard changes.

Audit:

- No App/Unity DTOs were changed.
- No Web-only operator field was promoted to shared core.
- No raw `PARROT_ORCH_SECRET`, LiveKit secret, or Google credential was found in
  the React source or dist output.

## 2026-05-14 L2-B Realtime Graph Reframe

Owner: Web Console lane
Status: in_progress
Category: requirement / implementation-plan
Scope: WEB-011, WEB-013, CORE-008, CORE-009 candidate review
Source: user audit on the React Memory Canvas, `dsg-rustworkx-master`,
`dsg-l2b-node-organization-options`, React Flow docs, force-graph docs.

The current React Flow Memory page is now treated as a **Memory Canvas /
operator draft page**. It is useful for safe previews, staging Edge receipts,
inspecting selected items, and testing L1.5/L2-B BFF routes. It is not the
final dense L2-B knowledge-graph monitor.

The next L2-B page should be separate and full-screen:

- React Flow stays available for canvas/workflow/editing patterns.
- React-Force-Graph or another Canvas/WebGL graph renderer is the first
  candidate for the full-screen L2-B monitor because the view should emphasize
  realtime topology, clustering, filters, attention/salience, and continuous
  status rather than form-heavy editing.
- Cytoscape.js remains a later candidate for compound/subgraph/cluster
  exploration if L2-B needs stronger graph-analysis UI affordances.
- The renderer should be selected behind a component adapter so the route/API
  does not become tied to one graph engine.

L2-B/RustworkX architecture notes to preserve before backend changes:

- RustworkX is the topology skeleton, not the business DTO. Stable DSG UUIDs
  must stay as business ids, with RustworkX integer indices kept as internal
  working mappings.
- Heavy memory content should remain in source stores or payload pointers when
  possible; L2-B should carry lightweight labels, kind/source, attention,
  salience, activation/decay, provenance, and relation metadata needed for
  traversal/visualization.
- Source buckets/subgraphs such as Google Calendar, Obsidian settings,
  WorkIntent/workflow, Graphiti, Ref, and L1.5 observations should be visible
  as filters or subgraph groupings. One-click import/preload must route through
  L1.5, trigger, Graphiti, or explicit Web operator receipts, not direct hidden
  mutation of L2-B.
- Bounded graph operations are preferred for realtime UI: ego graph expansion,
  limited-depth BFS, selected-node neighborhood, local PPR/spreading activation
  views, and offline or throttled health/cluster/community calculations.
- Missing shared fields for realtime graph streaming, visual style ids, or
  graph health metrics belong in the core candidate queue before any App/Unity
  DTO promotion.

Current UI bugfixes from this slice:

- The Memory Canvas toolbar is collapsed by default; Edge endpoint inputs and
  clear controls live inside an expandable tool drawer.
- Four visible directional connection dots are kept for each Memory Node, but
  the implementation maps them to separate `source-*` / `target-*` React Flow
  handles so Edge rendering attaches to the intended side instead of falling
  back to top/top.
- The empty L2-B status overlay is now semi-transparent and visually distinct
  from real graph Nodes.
- React Flow controls/minimap remain dark-mode styled.

Open interface questions:

1. `GET /api/l2b/graph/changes?since=...` or an SSE/WebSocket equivalent is
   needed for the full-screen monitor. This is a Web-only CORE-009 candidate
   until the App lane needs the same stream.
2. Node/Edge CRUD completeness needs explicit route and receipt coverage for
   labels/tags, subgraphs, clusters, and source bucket assignment.
3. Import/preload buttons need exact mappings for Google Calendar bucket,
   Obsidian setting buckets, WorkIntent subgraph/workflow, and selected
   Graphiti/Ref slices.

## 2026-05-15 Three-Page Responsibility Split

Owner: Web Console lane
Status: in_progress
Category: requirement / interface-boundary
Scope: WEB-011, WEB-012, WEB-013, CORE-006, CORE-008, CORE-009, CORE-010
Source: user clarification on Memory Graph, Runtime Flow, and new L2-B monitor

The Web Console now has three deliberately separate work surfaces:

1. **Memory Graph operation page (current React Flow page / WEB-011)**
   - Bias: safe management and editing workflows.
   - Owns L1.5 pool management, L2-B draft/edit preview, Node/Edge CRUD
     completeness, label/tag/subgraph/cluster management, Node detail,
     bound Ref/file/photo management, Graphiti/Ref link inspection, and
     operator-safe receipts.
   - May show the IntentWorkspace-related L2-B subgraph as context for
     human guidance, but must not model that as direct IntentWorkspace
     mutation. IntentWorkspace is a GOSLO Intent-layer workspace; actions that
     guide or modify it must become GOSLO Intent/task/workspace-file/Plan-edit
     requests with receipts.

2. **Runtime Flow / collaboration-flow page (WEB-012)**
   - Bias: whole-system collaboration state.
   - Owns GOSLO Intent -> Plan/HITL -> Blackboard -> IntentWorkspace ->
     Scheduler -> Nanobot -> Message/Trigger flow, manual Plan import,
     manual Nanobot task dispatch, message send/receive, result-destination
     choice, HITL gates, and simplified workflow wiring.
   - Should feel closer to a simple ComfyUI-like workflow board than a dense
     memory CRUD form.

3. **Full-screen L2-B realtime graph monitor (new WEB-013 page)**
   - Bias: realtime topology rendering and operator insight.
   - Owns full-viewport L2-B graph visualization, animation, filtering,
     source buckets, clusters, local graph depth, Graphiti natural-language
     search-to-subgraph, selected Node/Edge inspection, and trigger/attention
     visual effects.
   - Does not own detailed Ref-file management, detailed Plan management,
     Nanobot task workflow, or IntentWorkspace workflow editing.

### React-Force-Graph / Obsidian Research Anchors

Confirmed source references for the new WEB-013 renderer track:

| Source | Useful For |
|:--|:--|
| `https://github.com/vasturiano/react-force-graph` | React bindings for 2D/3D/VR/AR force-directed graph components; API props for graph data, custom canvas nodes, link styling, particles, click/hover callbacks, and d3 force tuning. |
| `https://github.com/vasturiano/react-force-graph/tree/master/example` | Example catalog including large graph, click-to-focus, dynamic data, expandable nodes, highlight, directional particles, image/text nodes, and fixed dragged nodes. |
| `https://vasturiano.github.io/react-force-graph/example/large-graph/` | Large-graph rendering reference for the full-screen monitor direction. |
| `https://reactflow.dev/learn/customization/handles` and `https://reactflow.dev/api-reference/types/connection-mode` | Current Memory Canvas connection/handle behavior; React Flow stays useful for editor/workflow canvases. |
| `https://obsidian.md/help/plugins/graph` | Product interaction reference: filters, groups, local graph, node/link display controls, arrows, node size, link thickness, animation, and force controls. |
| `https://d3js.org/d3-force` | Force simulation concepts for tuning center/repel/link forces and later exposing safe graph layout controls. |

Repo-local draft skill:

- `codex_workspace/codex_skills/react-force-graph-l2b/SKILL.md`

### Interface Notes

- WEB-013 needs a bounded L2-B graph read model that can feed multiple
  renderers. Candidate shape stays under CORE-009 until shared consumers are
  reviewed.
- Graphiti natural-language search should return a bounded subgraph read slice
  with provenance/partition info. It must not become direct FalkorDB mutation.
- Attention, salience, activation, decay, spreading activation, and trigger
  fire effects should start as renderer overlays over existing read fields.
  Any semantic change to those fields requires the attention-schema skill and
  candidate review.
- Manual Node/Edge writes on any page remain receipt-first and operator-gated
  where dangerous. L1.5 remains the safe default write path.

## 2026-05-15 L1.5 / RolePlay / Source Import Conclusions

Owner: Web Console lane
Status: in_progress
Category: requirement / interface-boundary
Scope: WEB-011, WEB-014, CORE-006, CORE-008, CORE-009
Source: user clarification, `src/parrot/dsg/l1_5/pool.py`,
`src/parrot/dsg/ingest/user_tag_filter.py`,
`src/parrot/dsg/triggers/calendar_trigger.py`, Graphiti skill, DSG L1.5/L2-B
skills, PRTS/Graphiti/DeepSeek web research

### RolePlay Meaning

The design correction is important:

- `roleplay` is currently an Obsidian ingest **profile**. In the existing code
  it routes UUID-free roleplay setting notes to the roleplay setting bucket.
- Product-wise, RolePlay is a **mode**. A mode can activate many source packs:
  persona notes, scene notes, relationship notes, world rules, style rules,
  temporary context, and future roleplay-specific refs.
- Therefore the Web UI should not imply that there is only one "RolePlay
  bucket". The L1.5 source board should show `profile=roleplay` plus multiple
  source-pack cards or virtual groups. The backend can keep the current
  compatibility bucket while the Web read model groups by source metadata.

Practical rule:

- `daily` and `roleplay`: setting profiles, UUID-free creation allowed.
- `ref`: binding profile, must target an existing Node/Graphiti UUID/ref.
- Multiple RolePlay imports should become multiple source instances under the
  roleplay profile, not multiple hidden L2-B write paths.

### L1.5 Source Board Direction

The next L1.5 refactor should shift from "bucket form stack" to "source
board":

| Source card | Web intent | Write/read boundary |
|:--|:--|:--|
| Obsidian | Scan/preview/import `daily`, `roleplay`, and `ref` notes. | Existing Obsidian event/UserTagFilter/L1.5 path; no UUID required except `ref`. |
| Google Calendar | Inspect raw event, normalized event, and Observation metadata. | Existing Calendar trigger/L1.5 path; preserve time/provenance fields. |
| Graphiti | Search partition, preview bounded subgraph, export selected hits. | Graphiti API read first; export becomes L1.5 observations, not direct L2-B mutation. |
| Manual Node | Create/update/delete/edit selected Node via receipts. | Existing Web-only L2-B draft/apply routes through L1.5 where applicable. |
| Ref/file/photo | Bind or retarget external refs. | CORE-006-aligned drafts; Web-only repairs stay operator gated. |

### 2026-05-15 Current Backend Slice

- Graphiti source-card backend is now present as Web-only routes:
  `/api/graphiti/subgraph/search`,
  `/api/graphiti/subgraph/export-draft`, and
  `/api/graphiti/subgraph/export`.
- Exported hits are converted to `Observation(source=USER_EXPLICIT)` and
  admitted through L1.5. Selected Graphiti provenance is preserved in source
  metadata; there is still no direct L2-B or FalkorDB write in this path.
- `arknights_test` is available as a test partition for Graphiti search/export
  and future full-screen L2-B renderer tests.
- The React source-board UI still needs to expose these routes alongside
  Obsidian, Google Calendar, Manual Node, and Ref/file/photo cards.

### 2026-05-15 Source Board UI Slice

- React Memory page now exposes a first Source Board in the right drawer:
  Graphiti, Obsidian, Google Calendar preview, and Manual Node guidance are
  split into separate source cards instead of one dense L1.5 form stack.
- Graphiti card supports partition selection, natural-language search,
  read-only canvas preview of returned hits, and export-draft receipts.
- 2026-05-15 continuation: Source Board now uses source tabs so only one source
  work area is open at a time. Graphiti search results have explicit hit
  selection, selected-hit counts, subgraph Node/Edge counts, canvas preview for
  selected subgraph Nodes/Edges, export-draft receipts, and dry-run apply
  receipts through `/api/graphiti/subgraph/export`.
- 2026-05-15 Graphiti export-plan continuation: Graphiti export receipts now
  include `subgraph`, `edge_drafts`, and `edge_write_policy`. The Source Board
  shows an inline Export plan so operators can distinguish L1.5 observations
  from preview-only Graphiti Edge drafts that still require resolved L2-B UUIDs.
- Obsidian card keeps `daily` / `roleplay` / `ref` profile behavior. The copy
  keeps RolePlay as a mode/profile, not a singleton bucket. The card can now
  scan a vault, select ready notes, and request a batch import preview receipt.
- 2026-05-15 Obsidian import-plan continuation: selected-note import receipts
  now render an inline Import plan in the Source Board. Operators can see the
  target L1.5 bucket, bind policy, Observation source/kind/tags, original note
  path, and explicit selected-note errors before dry-run apply. This is a UI
  clarity change over the existing `UserTagFilter -> L15Pool.admit` route; it
  does not add a new App DTO or bypass runtime `ObsidianIngestTrigger`.
- 2026-05-15 Ref/photo source-card continuation: Source Board now has a
  `Refs/Photos` tab. It reads current RefBinding registry rows, session PHOTO
  RefBindings, IntentWorkspace PHOTO refs, and L2-B Photo Nodes from live-state
  and can produce `refs.binding.draft` receipts for a target kind/id. A follow-up
  bugfix makes `target_kind=unresolved` explicit: the receipt reports
  `operation=unresolve_ref`, `would_resolve=false`, and `would_unresolve=true`
  instead of pretending to resolve to a durable target. This is draft-only and
  labeled `CORE-006`; no Web apply route is exposed until the shared RefBinding
  API and App-safe subset are reviewed.
- 2026-05-15 selected Node detail continuation: the floating Node inspector now
  includes a read-only `Refs / Photos` section when the selected L2-B Node has
  matching RefBinding rows, IntentWorkspace refs, or Photo asset/episode fields
  in its snapshot metadata. This keeps Ref/file/photo evidence visible near the
  Node while preserving the existing Web-only draft boundary for mutations.
- 2026-05-15 photo thumbnail continuation: Web Console now exposes
  `GET /api/photos/asset/{day}/{photo_id}` as a read-only preview route for
  cached photo uploads. The route resolves only under `PARROT_PHOTO_CACHE_ROOT`,
  validates the day and photo id, and returns `no-store` JPEG responses. React
  converts existing `/upload/photo/...` refs or cache paths into this route for
  selected Node and Source Board thumbnails; it does not expose local file paths
  directly and does not add any bind/unbind write surface.
- 2026-05-16 Graphiti Source Board bugfix: the Graphiti tab now renders a
  sanitized provider/status strip, clears stale graph previews after failed
  searches or manual selection clearing, and preserves Graphiti fact/source/
  target Edges when generating the CORE-013 import-destination policy preview.
  Selection changes now also refresh the read-only canvas preview in place,
  using the same Graphiti id normalization as the policy preview.
- 2026-05-16 review fix continuation: Graphiti API exceptions now clear stale
  export/import-plan state and render the exception inline in the Graphiti card.
  The Graphiti import-plan receipt also carries the upstream export draft
  receipt id, whether that id came from the Graphiti console's top-level
  `receipt_id` or the Web BFF's nested `receipt.receipt_id`.
- Google Calendar card now uses the calendar preview route to show raw event,
  normalized event, and Observation metadata. Real import/apply remains a later
  operator-gated step. 2026-05-16 UI bugfix: Calendar preview/import failures
  now show the inline reason in the active card (`policy_skipped_reason`,
  receipt error, local exception, or `no_calendar_events`) and clear stale
  normalized event / mapping / destination-policy previews so operators do not
  mistake old data for the current failed request.
- Manual Node card points users back to the canvas toolbar, keeping direct
  Node/Edge draft operations near the graph instead of mixing them with source
  imports.

### 2026-05-15 Memory Toolbar / Edge Surgery Slice

- React Memory page now uses an icon toolbar over the graph instead of a wide
  form strip. Tools are grouped as Node, Edge, Subgraph, Filter, Tag, State
  color, L1.5 Pool, and Settings, with hover tooltips and a single expanding
  tool dock.
- L1.5 Pool / Source Board moved into the Pool tool dock, so selected
  Node/Edge inspection no longer shares the same static right drawer as pool
  management.
- Selected Node/Edge details now render as a floating canvas inspector. It
  shows Node status/source/bucket/tags or Edge endpoints/kind/strength/source
  and raw JSON details, with preview delete/update actions nearby.
- Node state visualization is still simple but explicit: confirmed,
  tentative/expected, uncertain/ghost, and alert states map to small color
  markers. This is renderer-only and can later bind to attention/decay fields.
- Subgraph creation is currently a visual grouping preview box on the canvas.
  It is intentionally not a persistent L2-B core model yet; backend subgraph
  storage remains a future candidate after the user finalizes the UI design.
- RustWorkX capability audit for this slice: L2-B keeps stable business UUIDs
  and does not expose RustWorkX edge indexes in Web DTOs. Edge update/delete
  routes identify the target by endpoints plus optional kind/source filters.
  If parallel-edge surgery needs exact selection, promote a stable edge id
  into `SemanticEdge.meta` before exposing it as a shared interface.
- Current Edge payload is not just from/to: snapshot and receipts include
  `kind`, `strength`, `edge_source`, `created_at`, `cross_compartment`, and
  free-form `meta`. This matches the existing `SemanticEdge` extension surface.
- Bugfix continuation: Tag draft input is now independent from Edge `meta`
  state, the floating inspector close glyph is ASCII-stable, and the
  endpoint/kind/source Edge update/delete path has direct L2-B regression
  coverage.
- Filter continuation: React Flow Edge rendering now filters out any Edge whose
  source or target Node is hidden by the active Node-kind filter, preventing
  dangling React Flow edges and the warnings/layout oddities they cause.
- Selection continuation: if the active Filter hides the currently selected
  Node or Edge, the floating inspector clears itself instead of showing stale
  details for an item that is no longer visible on the canvas.

### 2026-05-15 L2-B / RustWorkX Capability Inventory

Owner: Web Console lane
Status: first_pass_complete
Category: backend-capability / renderer-prep
Scope: WEB-011.12, WEB-011.15, WEB-013.1, WEB-013.3, WEB-013.7
Source: `dsg-rustworkx-master`, `dsg-l2b-node-organization-options`,
`dsg-l1-5-l2a-conceptgraph-distilled`, `dsg-attention-schema-papers`,
Graphiti skill, `src/parrot/dsg/l2b_graph.py`,
`src/parrot/dsg/l2b_types.py`, `src/parrot/dsg/l2b/*`,
`src/parrot/brain/l2b_monitor.py`, and official React-Force-Graph /
React Flow / Obsidian Graph / D3 force docs.

Core backend reality:

| Area | Current capability | Web rendering implication |
|:--|:--|:--|
| Identity | `SemanticNode.uuid` is the stable business id; `_rx_index` is internal to `L2BGraph`. | Web and future renderer adapters must never persist or expose RustWorkX node/edge indexes. |
| Node kind | `object`, `surface`, `zone`, `person`, `event`, `photo`. | Use kind filters and distinct visual markers, but keep shapes configurable. |
| Node semantic payload | `label`, `category`, `description`, `known_facts`, `tags`, `typical_location`, `graphiti_uuid`, `obsidian_uuid`. | Detail drawer can show useful semantic data today; large content remains a Ref/Graphiti/Obsidian pointer. |
| Node runtime state | `attention`, `novelty`, `habituation_count`, `salience`, `last_attended`, `confirmation`, `evidence_score`. | Full-screen monitor can map this to size, color, opacity, glow, pulse, and stale/fresh badges without changing semantics. |
| Node grouping labels | `bucket_id`, `event_id`, `scene_type`, `location_tag`, `source`, `source_meta`, `meta`. | Primary filters/groups should be source bucket, event, scene, location, kind, attention, and ref-bound status. |
| Image/provenance | `provenance_stream_id`, `time_span`, `reference_image_path`, `last_sighting_path`. | Photo/ref panels and Node badges can show provenance and image binding; detailed file repair stays Web operator-only. |
| Edge payload | `kind`, `strength`, `source`, `created_at`, `meta`; `connect()` stamps `cross_compartment` / axes when event/bucket/scene/location differ. | Edge visuals should support kind color, strength width, source/provenance label, age, and cross-compartment styling. |
| Edge surgery | Web-only update/delete matches by endpoints plus optional kind/source filters. | Good enough for first operator UI; exact parallel-edge selection needs a stable edge id in `SemanticEdge.meta` or candidate DTO. |
| Views | `view_by_bucket`, `view_by_event`, `view_by_scene`, `view_by_location`, `view_by_kind` are filtered node lists, not RustWorkX subgraphs. | Treat these as filter views, not persisted subgraph models. |
| Clustering | `ConnectedComponentsClusterStrategy` produces read-only WCC clusters; `NoOpClusterStrategy` exists. | Cluster overlays can be shown now; persistent cluster Nodes remain future design. |
| Attention | `BoundedBfsActivation` and `IterativeSpreadingActivation` are read-only strategies with max-depth capped at 4; cross-compartment edges can be downweighted. | Local graph / ego expansion and trigger animation can visualize activation without mutating Node attention. |
| Intent boundary | `IntentEventBoundaryHandler` can open/close events, attach high-attention Nodes, optional simple decay, and list cross-event channels. | Runtime Flow owns collaboration state; Memory/L2-B pages may filter/visualize event subgraphs. |
| Graphiti bridge | L2-B can preload/enrich/archive episodes through Graphiti; Web Graphiti subgraph export currently goes through L1.5 observations. | Graphiti search-to-subgraph should remain read/preview/export-through-L1.5, not FalkorDB direct mutation. |

2026-05-15 App/Web policy clarification:

- Do not solve IntentWorkspace/L2-B linkage by adding `WorkspaceNodeKind` or
  making IntentWorkspace an L1.5 bucket. `NodeKind` stays semantic; workspace
  membership, staged refs, source-pool state, attention/buff state, and
  promotion policy are overlays or `source_meta`/`meta` until they deserve
  typed models.
- New candidate CORE-013 tracks the missing graph-link policy: per ref/source
  item, choose workspace-only, pointer Node, isolated compartment, promotion to
  main graph, or connect-by-rule. Web should render these as receipts and
  filters while the backend keeps rustworkx as topology plus bounded rewrite
  rules.
- 2026-05-15 user clarification extends CORE-013 into a planned
  graph-rewrite/transform/incremental-update policy. One-click import must be
  able to choose main graph, isolated/foldable subgraph, workspace-only, or
  connect-by-rule. Operators should be able to wrap selected Nodes or clusters
  into a named subgraph, fold it, compare/aggregate it with another subgraph
  such as a Calendar source slice, draft cross-subgraph links, and still choose
  "send selected context to LLM" when graph mutation is not useful.

Research / architecture gate for WEB-016:

- Required source readback before implementation: `parrot-cursor-skill-bridge`,
  `dsg-rustworkx-master`, `dsg-l2b-node-organization-options`,
  `dsg-l1-5-l2a-conceptgraph-distilled`, `dsg-attention-schema-papers`,
  Graphiti skill, and current `src/parrot/dsg/l2b_*` / `l1_5` code.
- Key constraint from RustWorkX skill: topology is the skeleton; high-frequency
  attention, buff, decay, and workspace activation belong to payload/overlay
  state. Only real node/edge insertion/removal should mutate topology.
- Key constraint from attention skills: avoid whole-graph attention by default;
  prefer bounded ego-subgraphs, WCC/cluster overlays, and explicit call limits
  for subgraph matching.
- Key product constraint: graph analysis is valuable only when it gives a
  stable audit trail, local neighborhood recall, health metrics, or reusable
  import/link decisions. For broad semantic judgment, selected subgraph context
  should be sent to an LLM instead of forcing a graph transform.

WEB-016 first design vocabulary:

| Concept | Meaning | First action |
|:--|:--|:--|
| Import destination | Where a source item lands: workspace-only, pointer, isolated compartment, main graph, or connect-by-rule. | Add receipt fields before real writes. |
| Foldable subgraph overlay | Named visual/semantic wrapper over existing Node UUIDs. | Store as overlay, not `NodeKind`. |
| Graph transform | Operator-audited operation such as wrap, aggregate, compare, split, promote, tombstone, or draft links. | Dry-run first; bounded affected set. |
| Incremental update | Recompute only affected ego-subgraph and emit node/edge/subgraph deltas. | Reuse Memory changed-since vocabulary. |
| Analysis preset | WCC/orphan/stale/degree/centrality/ego activation/PPR/VF2-style check. | Document when useful vs LLM. |

WEB-016 research gate result (2026-05-15):

Owner chat: Web Console
Status: first_pass_complete
Category: architecture gate / CORE-013 candidate preparation
Scope: L2-B graph rewrite, L1.5 import destination policy, subgraph overlays,
incremental memory deltas, and graph-analysis presets.
Source readback: `parrot-cursor-skill-bridge`, `dsg-rustworkx-master`,
`dsg-l2b-node-organization-options`,
`dsg-l1-5-l2a-conceptgraph-distilled`,
`dsg-attention-schema-papers`, plus current code in
`src/parrot/dsg/l2b_types.py`, `src/parrot/dsg/l2b_graph.py`,
`src/parrot/dsg/l2b/views.py`, `src/parrot/dsg/l2b/clustering.py`,
`src/parrot/dsg/l2b/compartments.py`, `src/parrot/dsg/l1_5/pool.py`,
`src/parrot/web_console/memory_live_state.py`, and
`web/console_app/src/graphModel.ts`.

Existing backend capability readback:

| Area | Current implementation | Design consequence |
|:--|:--|:--|
| Topology owner | `L2BGraph` owns a RustWorkX `PyDiGraph` and a stable business `uuid -> rx_index` map. | Never expose RustWorkX integer indexes in Web/Core DTOs; use UUIDs plus receipts. |
| Node semantics | `NodeKind` is intentionally small: object/surface/zone/person/event/photo. Source-specific extension lives in `source`, `source_meta`, and `meta`. | Do not add `WorkspaceNodeKind` for IntentWorkspace activation or pool membership. Use overlays and typed source-meta candidates only after fields stabilize. |
| Edge payload | `SemanticEdge` already carries kind, strength, source, created_at, and free-form meta. Connect/update/delete exist by endpoints plus optional kind/source filters. | Edge UI can support edit/delete now, but exact parallel-edge surgery needs a future stable edge id in meta or a CORE-013/CORE-006 candidate. |
| Compartments/views | Bucket/event/scene/location/kind are lazy filters and cross-compartment edge tags, not separate stored graphs. | Subgraph and pool UI must not pretend every filter is a semantic graph mutation. |
| Clustering | Connected-components clustering is read-only WCC over filtered nodes. | Clusters are safe as visual overlays; writing synthetic Cluster nodes is deferred. |
| Attention | Bounded BFS and iterative spreading activation are read-only and capped around local neighborhoods; cross-compartment edges can be downweighted. | Use activation animation/analysis as preview/receipt data, not as silent Node rewrites. |
| L1.5 | `L15Pool` owns admission, bucket assignment, Ref binding, scene switch, and timeline; actual Node bytes live in L2-B. | Imports from Obsidian/Google/Graphiti/manual/photo should enter through L1.5 unless explicitly preview-only. |
| Realtime read | Memory changed-since exists as Web-only stable-signature polling over live state. | Incremental graph deltas should reuse `sequence` / `changed` vocabulary before considering SSE/WebSocket. |

Algorithm tiering for the first implementation:

| Tier | Suitable operations | Not suitable |
|:--|:--|:--|
| Online / interaction-safe | Add/update/delete Node through L1.5, endpoint-based Edge draft/update/delete, WCC cluster read, orphan/stale health, bounded ego BFS, local spreading activation preview, direct source/bucket/event filters. | Whole-graph rewrites, unbounded semantic matching, long centrality sweeps on every UI tick. |
| Background / operator-triggered | Degree distribution, centrality/PageRank/PPR experiments, community detection, graph health snapshots, import recommendation batches. | Blocking user drag/connect interactions or silently mutating topology. |
| Gated / offline | VF2/subgraph-isomorphism, experience matching, large source-pack dedup, bulk merge/split plans. | Running without call limits, audit receipts, or operator review. |

First implementation order after this gate:

1. Add Web/backend-only typed draft models for `ImportDestinationPolicy`,
   `GraphOverlay`, `GraphRewriteDraft`, `GraphTransformReceipt`, and
   `GraphDeltaEvent`. Keep them out of Unity/App DTOs.
2. Add dry-run BFF routes for import destination preview, subgraph overlay
   preview, transform preview, and graph health readout. Suggested route family:
   `/api/l2b/graph-policy/import-draft`, `/api/l2b/subgraphs/draft`,
   `/api/l2b/transforms/draft`, and `/api/l2b/analysis/health`.
3. Wire Source Board import controls so Google Calendar, Obsidian source packs,
   Graphiti subgraphs, manual Nodes, and evidence/photo refs can choose
   workspace-only, pointer, isolated/foldable subgraph, main graph promotion, or
   connect-by-rule.
4. Extend the React graph model with overlay rows and graph-health badges while
   keeping React Flow as the edit canvas and React-Force-Graph as the future
   full-screen monitor candidate.
5. Only after dry-run receipts and tests pass, review which CORE-013 fields are
   stable enough for shared SSOT wording.

2026-05-15 WEB-016 first backend slice:

Implemented Web-only CORE-013 draft/read routes:

| Endpoint | Purpose | Safety |
|:--|:--|:--|
| `POST /api/l2b/graph-policy/import-draft` | Preview where a source item lands: workspace-only, index pointer, isolated compartment, main graph promotion, or bounded connect-by-rule. Returns `ImportDestinationPolicy`, optional `GraphOverlay`, proposed Edge drafts, write path, and reason. | Dry-run receipt only; no L1.5/L2-B mutation and no apply route yet. |
| `POST /api/l2b/subgraphs/draft` | Preview a foldable/isolated subgraph overlay with id, label, membership, refs, source, collapse state, and meta. | Draft/read-model only; overlay persistence is still pending. |
| `POST /api/l2b/transforms/draft` | Preview graph operations: wrap selection, aggregate/compare subgraphs, draft cross-links, promote, split, tombstone stale cluster, or send selected context to LLM. | Draft receipt only; no whole-graph rewrite and no operator apply route yet. |
| `GET /api/l2b/analysis/health` | Read graph health: node/edge counts, orphan count, WCC count/largest WCC, and kind/bucket/source distributions. | Read-only online-safe preset; centrality/PPR/VF2 remain future operator/offline work. |

2026-05-15 WEB-016 React wiring slice:

- Memory Canvas subgraph tool now calls the CORE-013 import policy,
  subgraph-overlay, and graph-transform draft routes. It uses the current
  selected Node/Edge context and still produces dry-run receipts only.
- The state tool now reads `GET /api/l2b/analysis/health` and renders a compact
  health card for Node/Edge/orphan/WCC/largest-component/tier status.
- Graphiti Source Board now exposes import-destination policy preview before
  Graphiti export. This is separate from `/api/graphiti/subgraph/export*`: the
  policy receipt answers "where should this selected result land?", while the
  export receipt answers "what L1.5 observations and Graphiti Edge drafts would
  be created?".
- Validation for this slice: `npm run typecheck`, `npm run build`,
  `tests/test_web_console/test_web_console_server.py -q` (`42 passed`), browser
  smoke on `http://127.0.0.1:7893/`, and `git diff --check` all passed. The
  browser smoke opened L1.5 Pool and confirmed Graphiti/policy controls with no
  console errors.
- 2026-05-15 bugfix: `GET /api/l2b/analysis/health` is a read-only health
  payload, not a normal receipt envelope with `data`. React now stores it as
  graph-health state and creates a local `l2b.analysis.health` record for the
  receipt timeline, so the record rail no longer shows an empty generic
  `receipt`. Graphiti policy previews also preserve selected Graphiti Edge
  provenance (`source_graphiti_uuid`, `target_graphiti_uuid`, fact/label, and
  write policy) in draft Edge `meta`.

New Web-only typed model layer: `src/parrot/web_console/graph_policy.py`
defines `ImportDestinationPolicy`, `GraphOverlay`, `GraphRewriteDraft`,
`GraphTransformReceipt`, and `GraphDeltaEvent`. These are implementation
prototypes for CORE-013, not ratified shared DTOs.

When to use graph analysis vs LLM:

- Use graph analysis when the answer depends on local neighborhood structure,
  provenance/ref binding, repeated import policy, stale/orphan health, bounded
  attention spread, or an auditable operator decision.
- Use an LLM over selected context when the task is broad narrative judgment,
  ambiguous semantic comparison, roleplay interpretation, or a one-off
  synthesis that does not benefit from persistent topology.
- The UI must offer "send selected subgraph/context to LLM" beside mutation
  actions so graph transforms stay useful rather than decorative.

Important gaps:

- Memory changed-since V1 exists as a Web-only polling diff route over the
  full live-state snapshot, but there is still no SSE/WebSocket stream and no
  durable per-edge/per-node delta ledger for L2-B graph deltas.
- No built-in graph health metrics in the read model yet: degree, density,
  orphan count, WCC count, centrality, PageRank, or stale-node distribution.
- No persistent subgraph/cluster storage model yet; current subgraph UI is
  visual preview only.
- No `GraphRewritePolicy` / workspace overlay policy yet; L1.5 pools and
  visual subgraphs can feel identical until bounded automatic link rules and
  promotion/isolation receipts exist.
- No stable first-class Edge id beyond endpoint/kind/source matching.
- No typed per-source `source_meta` models yet; the current dict extension
  surface is intentional until source-specific fields stabilize.
- No PPR implementation yet; current recall uses bounded BFS or iterative
  spreading activation. PPR remains a later HippoRAG-style candidate.
- No VF2/subgraph-isomorphism operator path yet; if added, it must use strict
  call limits and stay offline or explicitly bounded.

Renderer preparation:

- Added `web/console_app/src/graphModel.ts`, a dependency-free adapter that
  converts `/api/app/live-state` L2-B snapshots into `L2BRenderableGraph`.
- The adapter keeps `nodes` and `links` engine-neutral for React Flow,
  React-Force-Graph, or a future dense graph engine.
- It maps Node visual states from current backend fields:
  `alert`, `confirmed`, `tentative/expected`, `uncertain`, `ghost`, `default`.
- It filters Nodes by kind/source/bucket/event/min-attention/ref-bound and
  removes Links whose endpoints are not visible, matching the recent canvas
  bugfix.

Official renderer research distilled:

- React-Force-Graph supports 2D/3D/VR/AR force graphs with `nodes` / `links`,
  custom canvas Node rendering, link width/color/labels/arrows, directional
  particles, click/hover/drag callbacks, camera centering/zoom, and d3 force
  tuning. This fits WEB-013's full-screen monitor.
- React Flow remains the editing/workflow canvas. Its official docs confirm
  controlled `nodes` / `edges`, custom node/edge types, edge reconnect, loose
  connection mode, and keyboard delete/select behavior, which fit WEB-011 and
  Runtime Flow better than a force graph.
- Obsidian Graph View's relevant pattern is global graph plus filters, groups,
  display toggles, force controls, and local graph depth. L2-B monitor should
  borrow that interaction model instead of permanent dense panels.
- D3 force concepts should be exposed as safe view controls only: center,
  repel/charge, link force, and link distance. They must not change L2-B
  semantics.

Shared-interface rule:

- The adapter and renderer fields are Web-only. If multiple consumers need a
  streamed graph delta or stable Edge id, record it in CORE-009 / candidate
  queue before promoting it to shared SSOT.

### 2026-05-15 Source Preview Routes

Implemented after the first UI slice:

| Endpoint | Purpose | Safety |
|:--|:--|:--|
| `GET /api/l15/obsidian-vault/scan` | Scan a local vault path and classify ready/invalid Obsidian notes for `daily`, `roleplay`, and `ref` profiles. | Read-only; no file writes, no trigger publish, import remains operator-gated. |
| `POST /api/l15/obsidian-vault/import-draft` | Rescan selected Obsidian note paths and convert them through `UserTagFilter` into reviewable L1.5 observations. | Draft only; no Redis publish and no L1.5/L2-B mutation. |
| `POST /api/l15/obsidian-vault/import-plan` | Join selected Obsidian note import preview with CORE-013 destination policy so Source Board shows one source -> L1.5 -> L2-B plan. Empty/invalid selections return `policy_skipped_reason` and no graph placement policy. | Draft only; no Redis publish, no L1.5/L2-B mutation, no App DTO. |
| `POST /api/l15/obsidian-vault/import` | Apply selected Obsidian notes to L1.5 for Web operator testing. | Default dry-run; real import requires `operator_mode=true` and uses `L15Pool.admit`, not App DTOs. |
| `POST /api/google/calendar/fetch` | Draft/dispatch a Scheduler/Nanobot `calendar_fetch` task that should return `calendar_result`. | Default dry-run; real dispatch requires operator mode. Browser never holds Google OAuth. |
| `POST /api/google/calendar/preview` | Show raw Google/Nanobot event, normalized `CalendarTrigger` event, and `GOOGLE_CALENDAR` Observation metadata. | Read-only; no L1.5 commit, no Google OAuth in browser. |
| `POST /api/google/calendar/import-draft` | Convert selected/test Calendar events into reviewable `GOOGLE_CALENDAR` observations for L1.5 import. | Draft only; no L1.5/L2-B mutation. |
| `POST /api/google/calendar/import-plan` | Join Calendar import preview, mapping rows, and CORE-013 destination policy into a single reviewable source-pack plan. Empty event payloads return `policy_skipped_reason` and no graph placement policy. | Draft only; manual fetch/import V1; watch/syncToken stays future server-side work. |
| `POST /api/google/calendar/import` | Apply Calendar observations to L1.5 for Web operator testing. | Default dry-run; real import requires `operator_mode=true` and `dry_run=false`, then uses `L15Pool.admit`. |

The React Source Board now consumes these routes. Obsidian scan can load a
single note into the existing draft form or select multiple notes for a batch
import preview or import-apply preview. Calendar preview/import preview renders
normalized event and Observation rows directly in the Google Calendar source
card.

2026-05-15 boundary fix: Obsidian vault scan/import now treats selected note
paths as explicit operator intent. A selected note filtered out by `profiles`
returns `selected_profile_mismatch`; a selected note beyond the requested
import `limit` returns `selected_path_over_limit`; invalid selected notes return
`note_not_import_ready`; missing paths return `selected_path_not_found`.
Invalid `limit` input returns a Web receipt error instead of raising a route
exception. This is Web-only receipt semantics and does not change App DTOs or
the runtime trigger protocol.

2026-05-16 continuation: Obsidian and Google Calendar now have unified
`import-plan` routes matching Graphiti. The plan receipt carries the source
normalization rows, selected-note/calendar errors, `import_policy`,
`import_draft`, flow steps, and the future apply route/preconditions in one
place. This keeps the Source Board consistent: preview source data first,
review L1.5 observations and CORE-013 destination/overlay policy second, then
use the existing operator-gated import route only if a real write is intended.

2026-05-16 bugfix: Graphiti, Obsidian, and Google import-plan receipts now skip
CORE-013 destination-policy drafting when the source side has no importable
observations/items. The receipt remains useful (`success=false`,
`policy_skipped_reason=*`, errors/warnings preserved), but the UI must not show
a fake isolated-compartment/subgraph plan for an empty source selection.

2026-05-16 review fix: `import-plan` endpoints are always draft-only receipts.
Even if a caller sends `dry_run=false` or `operator_mode=true`, the top-level
receipt stays `dry_run=true` and `operator_mode=false`; requested flags are
recorded only under `requested_execution`. This keeps review plans separate
from apply receipts and avoids misleading audit trails.

2026-05-16 UI follow-up: the React Source Board now renders
`policy_skipped_reason` inline for Graphiti, Obsidian, and Google import-plan
cards. Empty or invalid import sources should be visible as a clear blocked
state in the source card, not only discoverable in the raw receipt stream. A
follow-up fixed the Obsidian card's local state mapping so the backend
`policy_skipped_reason` is not dropped before render. The Graphiti card now
uses the same inline warning surface for no-selection export/apply attempts,
instead of only pushing a receipt rail entry. Empty Graphiti search also clears
stale preview state and shows `missing_query` in the card itself.

2026-05-15 Calendar import boundary: Google Calendar now has the same two-step
Web operator shape as Obsidian and Graphiti. The draft route returns raw events,
normalized events, and observations for review. The import route defaults to
apply preview and only admits observations into L1.5 when both operator mode
and non-dry-run execution are explicit. The React Source Board labels this as
preview/import preview rather than exposing raw dry-run jargon.

2026-05-15 Calendar fetch/source-card continuation: the Source Board no longer
only uses a fixed synthetic event. It accepts pasted Google API or Nanobot JSON
(`items`, `events`, or `calendar_events`) and sends that raw payload to the same
preview/import routes. `POST /api/google/calendar/fetch` drafts the real
Scheduler/Nanobot fetch task shape and returns the `calendar_result` flow so an
operator can verify the Google Workspace MCP path without putting OAuth in the
browser.

2026-05-16 Calendar dispatch bugfix: the real Google Calendar fetch dispatch is
now guarded in the React Source Board. `Dispatch Fetch` uses
`operator_mode=true` and can enqueue work through Scheduler/Nanobot, so the UI
disables the button while the request is in flight and emits a local
`operator_fetch_in_flight` receipt instead of double-dispatching a task. This
does not change the Web BFF route shape or move Google credentials into the
browser.

2026-05-16 source import-plan audit guard: Graphiti, Obsidian, and Google
Calendar now share a route-matrix regression for their `import-plan` contracts.
Even if the caller requests `dry_run=false` and `operator_mode=true`, the plan
routes must return draft-only receipts, keep the requested execution under
`requested_execution`, expose the later operator apply preconditions, cite
CORE-008/CORE-013, and avoid raw secret or direct FalkorDB write leakage. Full
Web route tests now report `59 passed`; React build/typecheck, exact secret
scan, diff check, and in-app browser smoke passed.

2026-05-16 source import Landing map: the React Source Board now renders a
compact `Source -> L1.5 -> L2-B` landing visualization for Graphiti, Obsidian,
and Google Calendar import plans. It shows the selected source, L1.5
Observation count, destination policy, Edge draft count when relevant, apply
route, and operator gate. This is intentionally a Web rendering/readability
layer over existing receipts; it does not introduce a shared DTO and does not
turn preview/import-plan into an apply operation.

### Graphiti / Arknights Temporal Import Principle

The Arknights test data should not be modeled as one static encyclopedia state.
Graphiti is useful because it can preserve evolving facts:

- Use episode segmentation by chapter, arc, or major event.
- Attach `reference_time` or deterministic chapter/order metadata to each
  episode so Graphiti can extract temporal validity and superseded facts.
- Store source URL when an individual source link is extractable. If a source
  is an index or manually summarized aggregate, store the parent URL plus
  chapter/section id in `source_description`.
- Keep imported content as compact original summaries/facts, not long copied
 剧情 text. PRTS `剧情一览` is a source index anchor; the importer should use it
  for links and chapter ordering, then store only concise derived summaries and
  provenance.

### Google Calendar Mapping Reminder

Calendar data already has a strong shape for Node conversion. The source board
should show these three levels side by side:

1. Raw Nanobot/Google event payload.
2. Normalized calendar event: `id`, `calendar_id`, `title`, `start_time`,
   `end_time`, `timezone`, `location`, `description`, `html_link`, `etag`,
   `updated`, `status`, and `ical_uid`.
3. L2-B observation/source metadata after Calendar trigger conversion.

This makes it visible whether a calendar event loses time, identity, or
provenance before it becomes a Node.

2026-05-15 bugfix: the Web import route now preserves `observed_at` and
`time_span` when it rehydrates draft Observations for real operator import. This
matters because Calendar EVENT nodes should render on a timeline and later
refresh by `calendar_id` + `calendar_event_id`, not become timeless generic
notes.

2026-05-15 continuation: Calendar preview/import receipts now include Web-only
`mapping_rows`. Each row is a readable operator mapping from raw Google/Nanobot
event identity to L1.5 `google_calendar`, L2-B EVENT action, merge key, provider
Ref key, and IntentWorkspace policy. This is only a receipt/readability layer;
it does not promote a new App DTO. WEB-014.15 now uses a historical tombstone
policy for cancelled/deleted rows: keep the provider identity and L2-B EVENT
Node, set `calendar_lifecycle=cancelled/deleted`, `is_tombstone=true`, and lower
the node to GHOST/peripheral/low-attention state instead of default eviction.

### Google Calendar True Sync Boundary

Current implemented path:

1. Web Source Board operator clicks fetch preview or real dispatch.
2. `POST /api/google/calendar/fetch` drafts or dispatches `calendar_fetch`.
3. Scheduler routes `calendar_fetch` to Nanobot.
4. Nanobot uses the Google Workspace MCP / Google Calendar credentials outside
   the browser and returns `calendar_result`.
5. Scheduler rewrites that result for `CH_TRIGGER_RESULTS` and writes a bounded
   `STREAM_TRIGGER_RESULTS` observability row for Web/result-history reads.
6. `CalendarTrigger` normalizes the result and emits
   `TriggerOutcome.commit_observations`.
7. Trigger runner admits `GOOGLE_CALENDAR` Observations into the L1.5
   `google_calendar` bucket.
8. L1.5 / Ingest merges by stable provider identity into L2-B EVENT nodes and
   binds a lightweight Ref key: `google_calendar:{calendar_id}:{event_id}`.

This means Web can truly request a Google Calendar fetch when Scheduler,
Nanobot, credentials, and the result listener are running. It cannot and should
not fetch Google directly from the browser.

2026-05-15 continuation: `GET /api/google/calendar/results` reads the bounded
Scheduler-owned `STREAM_TRIGGER_RESULTS` ledger and filters for
`calendar_result`. The Web Source Board uses this as a recent result-history
view; it is an observability read model, not a replacement for
`CH_TRIGGER_RESULTS` or the L1.5 commit path. Payloads are secret-redacted before
returning to the browser.

Realtime target:

- Google Calendar official push notifications use service-side `watch`
  channels and webhook callbacks. The notification says a watched resource
  changed; it is not the event body itself.
- Google Calendar official incremental sync uses an initial full sync to store
  `nextSyncToken`, then repeated sync requests with the previous token to pull
  changed and deleted entries.
- Therefore the next backend upgrade should be: service-side watch/webhook or
  scheduled delta fetch -> persisted sync token/result receipt -> `calendar_result`
  event -> CalendarTrigger -> L1.5. Web should render this through the Memory
  change stream / future SSE-WebSocket layer, not hold Google OAuth.
- Deletion/cancellation policy is now a Web-first backend model: incremental
  sync cancelled/deleted entries become historical tombstone EVENT nodes. This
  keeps Google reconciliation identity visible while preventing stale reminders.
  Eviction can still be added later as an explicit operator repair action, not
  as the default sync behavior.

References:

- [Google Calendar push notifications](https://developers.google.com/workspace/calendar/api/guides/push)
- [Google Calendar incremental synchronization](https://developers.google.com/workspace/calendar/api/guides/sync)

IntentWorkspace boundary:

- Plain Calendar read/sync data belongs to L1.5 -> L2-B as EVENT memory.
- IntentWorkspace is for GOSLO Intent-layer drafts, edit plans, confirmations,
  rich temporary reports, and user-guided changes. A calendar fetch should not
  silently mutate IntentWorkspace.
- If a user/GOSLO plan says “prepare for this event,” “change this schedule,”
  or “send this to a worker,” Web should submit a GOSLO/Plan/HITL request or
  an IntentWorkspace guidance draft. Nanobot does the tool work; GOSLO/Plan
  owns the decision about whether the result returns to the user, GOSLO,
  App, L2-B memory, or a pending HITL gate.

## Implementation Round: WEB-011.19 Memory Changed-Since V1

Owner chat: Web Console
Status: done
Category: business-interface implementation note
Scope: WEB-010, WEB-011.2, WEB-011.18, WEB-011.19, CORE-009 candidate
Source: `parrot-cursor-skill-bridge`, `dsg-rustworkx-master`,
`dsg-l1-5-l2a-conceptgraph-distilled`, `src/parrot/brain/app_live_state.py`,
`src/parrot/web_console/memory_live_state.py`,
`src/parrot/web_console/server.py`, and `web/console_app/src/App.tsx`.

What changed:

- Added Web-only route `GET /api/memory/live-state/changes?since=...&limit=...`.
- The route consumes the existing `build_app_live_state()` snapshot but keeps a
  Web-specific stable content sequence. The root snapshot `sequence`,
  `generated_at`, and expiry bookkeeping are treated as transport noise, while
  nested business fields remain part of the signature.
- `changed=false` responses intentionally omit the full snapshot so the React
  Memory page can keep its current canvas state without repainting every poll.
- `changed=true` responses include the full snapshot plus a bounded operator
  event summary for L2-B, Blackboard, IntentWorkspace, Ref registry, and top
  attention Nodes.
- React Memory now calls this changed-since route in its active refresh loop.
  Runtime Flow already uses its own `/api/runtime/flow/changes` route.

Boundaries:

- This is polling/diff, not SSE/WebSocket and not a promise of true realtime.
- No Web operator action fields were added to Unity/App DTOs.
- CORE-009 remains a candidate. If the future full-screen L2-B monitor moves to
  SSE/WebSocket, it should reuse this `since` / `sequence` / `changed` /
  `events` / `snapshot` envelope instead of inventing another shape.

Validation:

- Focused route test covers initial changed response, no-op poll, content
  change after an L2-B Node insert, Web-only audit flags, and snapshot omission
  on no-op.
- Frontend typecheck/build pass after switching React Memory to the new route.

## Implementation Round: WEB-015 Time-Aligned Evidence Linkage

Owner chat: Web Console
Status: in_progress
Category: memory/vision evidence interface note
Scope: WEB-015, CORE-006, CORE-012
Source: user Time-Aligned Evidence plan, LiveKit/SVA/DSG attention skills,
`src/parrot/brain/vision/evidence.py`, `identify_object`, and Web BFF routes.

Memory impact:

- Photo uploads and snapshot metadata now register storage-backed evidence rows
  with the temporal ledger. This gives future L2-B/Ref/Graphiti operations a
  stable `evidence_id` and asset pointer instead of relying on inline image
  payloads.
- BBox/Focus threshold crossings now register `bbox_focus` evidence rows with
  subject/ref metadata and attention weight. This is observability-only today;
  it does not mutate L2-B directly.
- `identify_object` can attach `evidence_id` and storage asset pointers to
  sighting matched/unmatched events. L2-B text matching still works when no
  stored visual sample exists.

Boundary:

- `TimeAlignedSampleRef` is not yet a ratified App DTO. It is a Web/backend
  prototype feeding CORE-012.
- The Runtime `Time / Evidence` panel is not part of the Memory/L2-B operation
  page. Runtime Flow owns LiveKit sampling, browser screen-share permission,
  ASR/BBox/Focus time alignment, sampler freshness, and GOSLO runtime evidence
  notification policy.
- Memory Graph / L2-B consumes evidence later as Ref/Node/source material. It
  may display evidence-linked nodes, refs, photos, or board edges, but it
  should not become the place where runtime sampling or screen-share proof is
  controlled.
- Evidence Board / Ref binding should reference evidence ids and storage refs
  through CORE-006/CORE-012 once reviewed; no separate Web-only board storage
  model should be invented.
- WEB-015.9 first slice adds Web-only `POST
  /api/vision/evidence/memory-draft`. It is a preview/receipt bridge from
  `TimeAlignedSampleRef` to Memory: it returns a draft
  `Observation(source=USER_EXPLICIT)` for `L15Pool.admit`, an optional CORE-006
  RefBinding draft when a BBox/Focus/Photo ref is present, and a mapping that
  explains Temporal Evidence Ledger -> IntentWorkspace/Ref -> L1.5 -> L2-B.
  There is deliberately no apply route yet; real Memory writes wait for
  CORE-012/CORE-006 review and live screen-share smoke.
- Real frame cache smoke, crop/region persistence, reference-image VLM
  comparison, and apply policy remain pending WEB-015 follow-ups before L2-B
  can safely promote visual detections.
