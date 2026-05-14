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
- Create/update/delete node actions and edge draft actions call existing
  Web-only dry-run/draft routes and append receipts.
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
- L1.5 bucket actions are presented as bucket cards, with raw/payload work kept
  behind advanced flows.

Remaining WEB-011 work:

- Create-on-canvas pointer gestures still need a dedicated follow-up slice.
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
| `GET /api/memory/blackboard/activity` | Inspect recent py-trees Blackboard activity. | `build_blackboard_activity_snapshot()` -> `Blackboard.activity_stream` | Read-only, Web-only, bounded, summaries-only; starts activity capture if py-trees has not enabled it yet. |

### Audit: 2026-05-13 Requirement Alignment

Useful pieces completed:

- `GET /api/app/live-state?limit=...` is a valid Web read model for Blackboard,
  IntentWorkspace, Ref registry, L2-B, and tool-artifact inspection.
- The Memory Graph view proves the browser can poll and render these surfaces
  without leaking writes or pulling Web-only fields into App DTOs.
- The renderer already has lanes for Blackboard, IntentWorkspace, Refs, L2-B,
  and tool artifacts, so it can become the shell for a better graph/canvas.
- L1.5/L2-B operator drafts now exist and are documented. They default to
  dry-run and produce receipts before any real write.

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

- No server-side `changed_since` or event stream exists yet. Start with the
  current polling `sequence`; add a Web-only diff endpoint only when the visual
  base needs less noise or lower latency.
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

1. Only after these polling views are useful, evaluate a Web-only `changed_since`
   endpoint or SSE lane. Do not promote this to core unless the App needs the
   same stream.
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
