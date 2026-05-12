# Memory Graph Workspace Business Flow (2026-05-13)

Owner: Web Console chat  
Status: approved  
Category: Web Console business interface  
Scope: L1.5 management, L2-B visualization, node/photo management, Ref binding, Evidence/String Board  
Updated: 2026-05-13  
Related TODO: WEB-003, WEB-007  
Sources: `src/parrot/brain/l2b_monitor.py`, `src/parrot/dsg/l1_5/**`, `src/parrot/brain/observer/photo.py`, `src/parrot/brain/refs.py`, `codex_workspace/design_workspace/backend_interface_map/web_console/graphiti_management_business_flow_20260513.md`, Obsidian Canvas/JSON Canvas/React Flow/Cytoscape.js research anchors, `D:/GOSLOParrot/Pixel Asset`

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
