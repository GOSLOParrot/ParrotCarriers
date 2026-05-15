# Web Console Major Roadmap (2026-05-15)

Owner: Web Console chat
Status: active roadmap / user-reviewed decisions recorded
Category: Web Console business interface roadmap
Scope: Memory Graph Workspace, Runtime Flow Workspace, realtime transport, L1.5/L2-B/Graphiti/Google/Obsidian imports, CORE-009/010/013 staging
Source: User asked to fix the long-running Web mainline order, research gates, dependency map, true-vs-fake implementation standard, and a decision questionnaire before further large implementation.

## Purpose

This file is the Web Console mainline map. It does not replace the module
business files:

- `memory_graph_workspace_business_flow_20260513.md` remains the Memory/L1.5/L2-B/Ref/Evidence interface file.
- `observability_runtime_business_flow_20260513.md` remains the Runtime Flow, Scheduler, Nanobot, HITL, trigger, and Time/Evidence interface file.
- `graphiti_management_business_flow_20260513.md` remains the Graphiti/FalkorDB interface file.

The goal here is to keep the big roadmap from disappearing into scattered
chat notes and to make each implementation round start from the right research
and architecture context.

## Non-Negotiable Pre-Implementation Gate

Every major Web slice below must begin with a short source readback before code
changes. This readback is a gate, not a formality.

| Gate | Required readback | Why |
|:--|:--|:--|
| Skill gate | `parrot-cursor-skill-bridge`, then the relevant source skills: `dsg-rustworkx-master`, `dsg-l2b-node-organization-options`, `dsg-l1-5-l2a-conceptgraph-distilled`, `dsg-attention-schema-papers`, `graphiti`, `py-trees`, `nanobot`, `parrot-bus-orchestration`, and LiveKit skills only when touching LiveKit. | Prevents UI intuition from inventing backend semantics. |
| Code gate | Current implementation files for the touched surface, such as `src/parrot/dsg/l2b*`, `src/parrot/dsg/l1_5/*`, `src/parrot/web_console/*`, `web/console_app/src/*`, Scheduler/Nanobot modules, and existing tests. | Skills can be stale; current code is authoritative. |
| Interface gate | Web business docs, `APP_WEB_PARALLEL_TODOLIST_20260513.md`, and `core_interface_candidate_queue_20260513.md`. | Keeps Web-only operator/admin fields out of Unity/App DTOs. |
| UX gate | At least one concrete UI pattern review for the page type being changed: graph editor, graph monitor, source board, Runtime Flow, HITL, receipt timeline, or toolbar interaction. | Avoids dense stacked panels and text-only controls. |
| Verification gate | Define the route, receipt, test, and browser smoke that prove the feature is real. | Avoids demo-only panels being mistaken for implemented capability. |

## Fixed Mainline Order

This is the intended order. Small bugfixes can happen between steps, but major
feature work should not jump over its substrate.

| Order | Mainline | Primary TODOs | Blocking relationship | Completion standard |
|:--|:--|:--|:--|:--|
| 0 | Current foundation audit | WEB-011, WEB-012, WEB-014, WEB-015, WEB-016 | Already mostly done; keep auditing. | Existing React pages, BFF routes, dry-run receipts, and current tests stay green. |
| 1 | RustWorkX/L2-B graph policy and "subconscious" rewrite rules | WEB-016 | This is the next architectural base. Realtime and imports should reuse its delta/policy vocabulary. | Typed overlay/rewrite/read receipt model; import destination policies; examples for Web pages; no silent whole-graph rewrite. |
| 2 | Incremental delta and realtime transport | WEB-013.2, WEB-012.11, CORE-009/010/013 | Depends on stable graph/runtime event vocabulary from order 1. | SSE or WebSocket prototype over changed-since sequence/events, reconnect behavior, bounded payloads, no frontend secrets. |
| 3 | Memory Graph operation page cleanup and true graph operations | WEB-011, WEB-013.5, WEB-014.6 | Depends on order 1 for operation semantics; benefits from order 2 for live feel. | WYSIWYG Node/Edge/subgraph selection, edit/delete/draft/apply receipts, clean toolbar/drawers, L1.5 Source Board separated from selected-object detail. |
| 4 | Source imports into L1.5/L2-B/subgraphs | WEB-014, CORE-008/013 | Depends on order 1 import destination policy; realtime from order 2 makes results visible. | Graphiti search/export, Obsidian source packs, Google Calendar fetch/sync preview/import, and Arknights test import each have preview, operator gate, receipt, tests, and visible target subgraph. |
| 5 | Runtime Flow collaboration page upgrade | WEB-012.17, WEB-012.19, WEB-012.20, CORE-010/011 | Can run after order 2, but should share the same event/reconnect style. | Clear collaboration graph: Intent -> Plan/HITL -> Blackboard -> IntentWorkspace -> Scheduler -> Nanobot -> Message/Trigger, with real actions and result destinations. |
| 6 | Full-screen L2-B monitor and algorithm/animation layer | WEB-013.4, WEB-013.7, WEB-013.9, WEB-016.6 | Depends on graph adapter and realtime enough to avoid fake animation. | Fullscreen graph view with filters, clusters/subgraphs, attention/trigger animations, and React-Force-Graph or equivalent renderer adapter. |
| 7 | SSOT promotion review | CORE-009, CORE-010, CORE-011, CORE-013 | Only after typed schema, tests, and user review. | Promote only reviewed fields into core SSOT; keep Web-only operator actions out of App DTOs. |

## Direct Timing Answers

The schedule should be by gates, not dates.

1. **RustWorkX graph transform and subconscious-rule research starts next.**
   It is the next big architecture slice because it defines what "import into a
   subgraph", "connect by rule", "fold cluster", "promote to main graph",
   "spreading activation", "PPR", and "LLM instead of graph mutation" mean.
   It must produce Web Console examples for the Memory page, the future
   full-screen L2-B monitor, and source import receipts before more real apply
   routes are added.
2. **Realtime starts after the delta vocabulary is stable.** Current polling
   changed-since is useful, but it is not enough for the target feel. The first
   realtime milestone should reuse the Memory/Runtime sequence shape, not
   invent a second protocol. SSE is the likely first transport for read-only
   streams; WebSocket only becomes necessary for bidirectional low-latency
   actions.
3. **WebConsole interaction cleanup should happen in two layers.** Small bugfix
   polish continues now. The serious layout/interaction upgrade starts after
   the graph-policy gate, because the toolbar and right-click/floating detail
   behavior must reflect real Node/Edge/subgraph operations rather than just
   moving buttons around.
4. **Google/Graphiti/Obsidian/Arknights true import comes after import policy.**
   Many BFF routes already exist in preview/dry-run form, but the "one-click
   import into a specific subgraph" experience needs persistent overlay/import
   destination semantics first. Arknights real import specifically needs a
   user-approved dry-run source list and copyright-safe compact summaries.
5. **Runtime Flow collaboration upgrade comes after the realtime/event base.**
   Runtime Flow already has a typed Web-only read model and Plan HITL V1. The
   next meaningful jump is durable trace/result events plus a cleaner workflow
   page. Without those, it becomes another static status board.

## 2026-05-16 User Decisions Recorded

This section resolves the questionnaire below. Keep it as the active policy
unless the user explicitly changes the product direction.

### A. Page Split and Layout

- Keep the current React Flow Memory page as the **L2-B operation/editor page**.
  It focuses on detailed Node/Edge/subgraph editing, Graphiti-preloaded Node
  review, UUID/Ref/source binding, subgraph construction, rollback-friendly
  saves, and operator-gated strong writes.
- Build a separate future **full-screen L2-B render/monitor page**. It should
  be graph-first, visually quiet, lower-text, and suited to realtime topology,
  attention/trigger animation, clustering, local graph depth, and algorithm
  overlays. The user will provide the final page layout later.
- The operation page should use a clean right-side icon/tool dock. Selecting a
  tool reveals only that tool's controls and details; do not stack unrelated
  component blocks in the main graph surface.
- Selected Node/Edge/subgraph detail may have a compact floating card near the
  object plus a full right drawer for deeper edits. L1.5 Source Board must not
  be mixed with selected-object details.

### B. Graph Policy and Write Ownership

- Default import destination policy:
  - `workspace_only` for IntentWorkspace drafts and unresolved working refs.
  - `index_pointer` for large/low-frequency source documents and immutable
    external source material.
  - `isolated_compartment` for Graphiti search packs, Obsidian source packs,
    Google Calendar batches, and Arknights test packs until the operator
    promotes or connects them.
  - `connect_by_rule` only as an explicit bounded operator batch.
  - `promote_to_main_graph` only after preview, receipt, and audit review.
- A subgraph may be a visual overlay, temporary workspace, and import
  compartment, but those roles must stay separate in fields/receipts. Do not
  overload semantic `NodeKind` to mean workspace membership or "buff".
- React Flow operation page can support real L2-B Node/Edge/subgraph apply when
  backed by route, operator mode, audit receipt, and rollback/backup posture.
  It must not pretend that editing an L2-B projection edits Graphiti source
  facts, Obsidian source files, or Google source records.
- Graphiti durable changes go through Graphiti/FalkorDB operator APIs and
  Graphiti receipts. Obsidian and Google source records are treated as source
  imports/pointers/tombstones unless a dedicated source adapter says otherwise.
- The first real graph transforms should be conservative: wrap selection,
  create/fold overlay, draft cross-links, promote selected compartment, split or
  tombstone stale clusters, and send selected context to LLM. Whole-graph
  rewrites are forbidden without a bounded rule and audit.

### C. Realtime Transport

- Use SSE first for Memory/Runtime read streams. It fits the current need:
  one-way server-to-browser updates with `EventSource`, reconnect behavior, and
  named event support. WebSocket is deferred until true bidirectional
  low-latency editing requires it.
- Keep the business interfaces separated by module, then extract the stable
  shared core subset through candidate review. Do not force one monolithic
  realtime DTO across unrelated surfaces.
- Operator action receipts should use a separate receipt stream from graph or
  runtime delta streams.

### D. Source Imports

- Google Calendar V1 completion means manual fetch/import with preview,
  operator receipt, and visible target subgraph. Google watch/syncToken is a
  second-stage backend sync feature. Redis is not required by Google Calendar
  itself; in this repo it is useful for cross-process Scheduler/Nanobot/result
  ledgers and Web observability.
- Calendar EVENT nodes should preserve Google event `status` values
  (`confirmed`, `tentative`, `cancelled`) and add a Parrot lifecycle overlay
  such as `scheduled`, `tentative`, `cancelled_tombstone`, `expired`,
  `completed_manual`, or `postponed/rescheduled`. Google Tasks is separate; it
  has `needsAction` / `completed`, date-only due semantics, and should not be
  silently merged with Calendar events.
- Obsidian `roleplay` is a mode/profile that can contain many source packs. It
  is not a singleton fixed bucket.
- `Arknights_test` is a large test pack, not only a worldbuilding note. Use
  compact original summaries, facts, source URL or source description, and
  temporal/state-change metadata. Prefer PRTS "剧情摘要/剧情速览" style
  material where available, but do not store long copyrighted plot text.
  Episodes should be split into roughly 300-800 Chinese characters each, e.g.
  base profile, archive 1, archive 2, relationship changes, and chapter state
  transitions rather than one merged blob.

### E. Runtime Flow and HITL

- Runtime Flow layout should be hybrid: swimlane overview first, then a
  ComfyUI-style workflow detail when drilling into Plan/Nanobot/HITL.
- Manual Nanobot result destinations can include `view_only`,
  `return_to_goslo`, `return_to_app`, `stage_to_intent_workspace`, and
  `write_to_memory_draft`, with receipts making the destination explicit.
- Next HITL targets after Plan are Google imports and Graphiti imports, then
  evidence/photo promotion. Trigger/message HITL comes later after their state
  machines are clear.
- C4/interruption candidates are urgent calendar/reminder, high-surprise
  Awareness, explicit user rule, or operator-triggered event. Default source
  imports and photo/evidence hints should stay C3/no-interrupt unless policy
  says otherwise.

### F. Visual Language

- React Flow remains the editor/workflow canvas. React-Force-Graph is the first
  choice for the future full-screen L2-B monitor because it supports canvas
  rendering, custom node/link drawing, force tuning, click/hover/drag
  interactions, and link particles for trigger/attention animation.
- Keep algorithm visuals subtle by default: color, size, opacity, pulse, and
  directional particles. Explicit overlays for activation/decay/cluster/edge
  confidence should be toggleable, not always-on.
- Receipt/history rails default collapsed unless the user is actively
  inspecting an operation.

### G. Safety and Apply Policy

- Prefer real implementation over decorative panels. A claim is real only when
  the route/state path, receipt, tests or browser smoke, docs, and no-secret
  check exist.
- Destructive or persistent operator applies should create a durable audit
  record and, for destructive changes, a backup/export or rollback story.
- Web-only operator actions stay out of Unity/App DTOs. Shared fields move only
  through the candidate queue and SSOT review.

## WEB-016 Kickoff Scope

The next implementation slice starts from WEB-016 and must produce concrete
examples before new persistent apply routes:

1. Re-run the source gate for RustWorkX/L2-B/L1.5/attention/Graphiti plus the
   current backend code.
2. Write the graph-policy examples for Web pages: Memory editor, full-screen
   monitor, Graphiti import, Google import, Obsidian source packs, and
   IntentWorkspace overlays.
3. Stabilize `GraphOverlay`, `GraphRewriteDraft`, `GraphDeltaEvent`, and
   receipt vocabulary enough for SSE design.
4. Define the write ownership matrix: L2-B apply, L1.5 admit, Graphiti durable
   edit, source immutable import, and operator-only DB surgery.
5. Only after that, start the SSE stream and UI cleanup slices.

External docs checked for this decision pass:

- React-Force-Graph README/API for canvas/WebGL force graph rendering,
  `graphData`, stable `nodeId`, link `source`/`target`, interactions, and
  directional particle examples:
  <https://github.com/vasturiano/react-force-graph>
- MDN Server-Sent Events / `EventSource` for one-way event streams, named
  events, reconnection ids/retry, and keep-alive comments:
  <https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events>
- Google Calendar Events API for event `status`, cancelled event behavior, and
  incremental-sync deletion caveats:
  <https://developers.google.com/workspace/calendar/api/v3/reference/events>
- Google Calendar sync/watch docs for stage-2 server-side realtime:
  <https://developers.google.com/workspace/calendar/api/guides/sync> and
  <https://developers.google.com/workspace/calendar/api/guides/push>
- Google Tasks API for separate task status semantics:
  <https://developers.google.com/tasks/reference/rest/v1/tasks>
- RustWorkX PyDiGraph API for topology mutation, subgraph, edge update/delete,
  connectivity, PageRank, and isomorphism primitives:
  <https://www.rustworkx.org/apiref/rustworkx.PyDiGraph.html>

## True Implementation vs Fake Implementation

| Claim | True implementation means | Fake or incomplete means |
|:--|:--|:--|
| "Realtime" | A bounded sequence/delta stream with reconnect behavior, stale/fresh state, tests, and a browser smoke. | A manual refresh button, broad polling repaint, or CSS animation without data deltas. |
| "Node/Edge CRUD" | Backend route, dry-run receipt, operator-gated apply if claimed, test coverage, visible canvas result, and audit fields. | Frontend-only ghost nodes labeled as saved, or raw JSON fields with no route. |
| "Import to subgraph" | Source preview, destination policy, L1.5 admit path, overlay/subgraph receipt, visible target view, and rollback/audit story. | Search results drawn locally without L1.5/receipt/provenance. |
| "Graph transform" | A bounded rule with input selection, output draft, risk/audit receipt, tests, and no whole-graph mutation by surprise. | A decorative cluster box or an unbounded graph rewrite. |
| "Runtime collaboration" | Plan/Scheduler/Nanobot/message events are traceable across modules with action receipts and result destinations. | A diagram that does not read real runtime state or dispatch through backend routes. |
| "HITL" | A real pending gate state machine with approve/reject/revise/cancel semantics and dry-run/operator policy. | A modal button that only adds a local receipt. |

## Design and Architecture Principles

- L2-B remains the RustWorkX working-memory topology plus semantic payloads.
  Workspace membership, active IntentWorkspace state, and "buff" behavior are
  overlays or lifecycle flags, not new semantic NodeKind by default.
- L1.5 is the admission, source-pack, ref-health, and bucket policy layer. It
  should not be reduced to a visual subgraph, but it can import into an
  isolated subgraph, an index pointer, workspace-only, or main graph promotion
  depending on policy.
- IntentWorkspace is a working set and planning context for GOSLO Intent. It is
  not a strong notification channel by itself. Strong notification belongs to
  explicit ContextInjector / Awareness / trigger delivery levels.
- Graphiti is a temporal context graph. Imports should preserve time order,
  provenance, source URL/description, and state changes. Direct FalkorDB writes
  stay Web operator mode only.
- Graph analysis must be useful. Prefer bounded ego graph, spreading
  activation, PPR, WCC/orphan health, and explicit "send selected context to
  LLM" over impressive but unbounded whole-graph magic.

## Decision Questionnaire for User Review

### A. Page Split and Layout

1. Should the current React Flow Memory page stay primarily as an **editor**
   while the new full-screen L2-B page becomes the **monitor/knowledge graph**?
2. On the Memory editor page, should L1.5 Source Board open from a left dock, a
   right drawer, or a top toolbar popover?
3. Should selected Node/Edge/subgraph details be floating near the object, in a
   right drawer, or both with a compact hover card plus full drawer?
4. Which interactions should be WYSIWYG first: drag connect Edge, context menu,
   toolbar command, keyboard shortcuts, or command palette?

### B. Graph Policy

5. Default import destination: `workspace_only`, `index_pointer`,
   `isolated_compartment`, `promote_to_main_graph`, or `connect_by_rule`?
6. Is a subgraph a semantic object, a visual overlay, a temporary workspace, or
   all three with separate fields?
7. Which graph transforms should get real apply first: wrap selection, fold
   cluster, compare two subgraphs, connect by rule, promote to main graph,
   split cluster, tombstone, or send context to LLM?
8. Should automatic edge creation be conservative and manual-first, or should
   there be operator-approved batches that create many edges at once?

### C. Realtime Transport

9. Is SSE enough for first realtime, or do you want WebSocket from the start?
10. Should realtime streams be Web-only first, or should we design for App HUD
    consumption immediately?
11. What freshness does the UI need: 1s, 3s, 5s, or event-immediate?
12. Should operator action receipts be in the same stream as memory/runtime
    deltas, or in a separate receipt stream?

### D. Source Imports

13. For Google Calendar, is the first true version manual fetch/import enough,
    or must server-side Google watch/syncToken be part of "done"?
14. For cancelled Google events, confirm the current historical tombstone
    policy: keep EVENT Node, lower attention, do not delete by default?
15. For Obsidian, should `roleplay` be a mode/profile containing many source
    packs, not a single fixed bucket?
16. Should Obsidian sample files be created only after a preview list, and
    should they live under `GOSLO/Settings/Daily`, `GOSLO/Settings/Roleplay`,
    `GOSLO/Refs`, and `Worlds/Arknights_test`?
17. For Graphiti Arknights import, approve compact original summaries/facts
    plus source URL/description only, with chapter/time/state-change metadata?

### E. Runtime Flow and HITL

18. Should Runtime Flow look more like swimlanes, a ComfyUI-style workflow
    board, or a hybrid with swimlane overview plus workflow detail?
19. Manual Nanobot task result destination choices: `view_only`,
    `return_to_goslo`, `return_to_app`, `stage_to_intent_workspace`, or
    `write_to_memory_draft`?
20. Which HITL targets should come after Plan: triggers, messages, Google
    imports, Graphiti imports, or evidence/photo promotion?
21. What should count as C4/interruption: only urgent calendar/reminder,
    high-surprise Awareness, explicit user rule, or operator-triggered event?

### F. Visual Language

22. Should the graph monitor visually follow Obsidian local graph, graph DB
    explorer, or a more neural/activation animation style?
23. How visible should algorithmic signals be: subtle color/size/pulse, or
    explicit overlays for activation, decay, cluster, edge confidence, and
    trigger fire?
24. Should the right-side receipt/history rail default collapsed everywhere?
25. What should be icon-only versus text label in the toolbar?

### G. Safety and Apply Policy

26. Which operations may have real apply buttons in Web operator mode first:
    Node create/update/delete, Edge create/update/delete, Obsidian import,
    Calendar import, Graphiti export, graph transform, or evidence promotion?
27. Do real destructive operations need backup/export before execution?
28. Should every operator apply create a durable audit record, or is receipt
    timeline plus tests enough for the first local version?

## Audit Cadence

Every implementation round:

- Update this roadmap only when order or policy changes.
- Update the exact module business file for routes/fields.
- Update the Web TODO checklist status.
- Add shared gaps only to the core candidate queue.
- Run targeted backend tests plus frontend typecheck/build when code changed.
- Browser smoke the changed page when frontend changed.
- Scan for secret leakage when routes touch LiveKit, Google, Graphiti, or
  orchestrator config.

Every three major rounds:

- Reconcile Web README, root backend interface index, TODO board, candidate
  queue, completed route ledger, and product drift.
- Decide whether a candidate can move toward core SSOT or must stay Web-only.
