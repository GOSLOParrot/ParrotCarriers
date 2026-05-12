# Web Console Step 1 Plan (2026-05-13)

Owner: Web Console chat  
Status: approved  
Category: Web Console planning / information architecture  
Scope: requirements summary, IA, visual direction, implementation TODO shape  
Updated: 2026-05-13  
Related TODO: WEB-001, WEB-008  
Sources: `codex_workspace/app_web_parallel_workflow_20260513.md`, `.cursor/memory/architecture/Interface/app_web_parallel_routes_agent_team_20260513.md`, `codex_workspace/skills/web_console.md`, external research anchors listed below, `D:/GOSLOParrot/Pixel Asset`

## Slice: Web Console Step 1

### A. Source Readback

- The parallel workflow says Web owns Web Console information architecture,
  ECS/module health, L1.5/L2-B, node/photo management, Blackboard,
  IntentWorkspace, Plan, Scheduler, Nanobot, and Web-only admin flows.
- The App/Web route decision says Web may build rich operator UX, while App
  receives only stable preset choices and safe status summaries.
- The Web Console route says read-only first, dense operational UI, and
  `src/parrot/web_console/` plus `web/console/` are the preferred future code
  locations for BFF and frontend.

### B. Existing Core Interfaces

Yes for Step 1 planning and the first read-only shell.

Useful existing seeds:

- Orchestrator status: `src/parrot/castle/orchestrator/server.py` and
  `src/parrot/castle/orchestrator/status.py`.
- Current smoke/read adapters: `src/parrot/brain/app_monitor_server.py`,
  `src/parrot/brain/app_first_version.py`,
  `src/parrot/brain/l2b_monitor.py`, and
  `src/parrot/brain/graphiti_console.py`.
- Scheduler/Plan/Intent state: `src/parrot/scheduler/**`,
  `src/parrot/brain/intent_workspace.py`, and `src/parrot/brain/plan/**`.

### C. Missing Core Surface

No new core surface is required to document Step 1.

Known shared candidates remain in
`../core_interface_candidate_queue_20260513.md`, especially CORE-001 through
CORE-008. Web must not promote those into `.cursor/memory/architecture/Interface/**`
without App/Web confirmation.

### D. Observable Completion Signal

- The shared TODO board has approved Web lane rows WEB-001 through WEB-008.
- `web_console/README.md` indexes every active Web business-interface file.
- Business-interface files are grouped by stable product surface, not by every
  temporary investigation.
- Any future temporary multi-round audit notes go under a clearly marked
  Web Console temporary folder and only key decisions are promoted back into
  the indexed business docs.

## Console IA

Use one operational shell with these first-order views:

| View | Purpose | First data source |
|:--|:--|:--|
| Ops Health | ECS/module health, orchestrator status, runtime config, restart/crash clues. | `/status` |
| Runtime State | Blackboard, IntentWorkspace, Plan/task, Scheduler/Nanobot status. | Existing Brain/Scheduler read adapters first. |
| Memory Graph | L1.5, L2-B, photo refs, Graphiti partitions, Evidence/String Board. | `build_l2b_snapshot`, L1.5/RefTable reads, Graphiti console adapter. |
| Agent Team | Maid Team / AgentTeam status and nanobot instance health. | Existing fixed team placeholder plus CORE-001/002/003 candidates. |
| Collaboration | GOSLO/Nanobot chat observability and task summaries. | Scheduler/Nanobot result streams and safe summaries. |
| Operator Surgery | Graphiti API surgery and FalkorDB operator tools. | Web-only, gated by dry-run/audit/backup posture. |

## Visual Direction

### A. Obsidian-like Console Layer

This is the default Web Console look for dashboards, CRUD, graph views, normal
menu panels, and normal canvas work.

- Use Obsidian as the close reference: left ribbon/navigation, searchable tree,
  tabbed work panes, inspector/right sidebar, command palette/action menu,
  local/global graph switching, backlink-like relation panels, and plain canvas
  cards connected by lines.
- Keep it quiet and workmanlike: compact navigation, dense tables, graph
  panels, diff badges, explicit empty/error states, strong keyboard/search
  affordances, and no marketing hero.
- CRUD and operator forms stay utilitarian: table/list/detail, draft preview,
  audit result, dry-run/apply split, and reversible action history where the
  backend can support it.
- Web can use its own renderers for graph/board views, but storage and typed
  Ref/Edge contracts must stay renderer-agnostic.

### B. Papers Please-inspired Interaction Layer

This is a later, separate interaction language for Evidence/String Board,
document/photo inspection, and richer operator workflows. It must not bleed into
the base admin console skin.

- Interaction pattern: desk/workbench surface, draggable documents/photos,
  side-by-side comparison, stamps/approval/reject marks, audit tape, rulebook or
  checklist drawer, queue/result feedback, and concrete consequences for
  operator actions.
- Candidate asset roots: `D:/GOSLOParrot/Pixel Asset/Paper UI`, `Wood UI.zip`,
  `Book UI V1.zip`, and related pixel UI packs. Do not bind the data model to
  any one asset pack.
- Evidence/String Board can borrow the physical interaction feel, but the board
  still writes typed Ref/Edge operations through the shared memory boundary
  instead of creating a game-only graph format.

## Research Anchors

- [Obsidian Graph view](https://obsidian.md/help/plugins/graph): nodes/lines,
  hover highlighting, context menus, filters, groups, local graph depth,
  display/force controls.
- [Obsidian Canvas](https://obsidian.md/help/plugins/canvas) and
  [JSON Canvas spec](https://jsoncanvas.org/spec/1.0/): infinite 2D cards,
  file/text/link/group nodes, typed edges, and open `.canvas` storage as a
  useful reference shape.
- [React Flow overview](https://reactflow.dev/learn/concepts/terms-and-definitions)
  and [built-in components](https://reactflow.dev/learn/concepts/built-in-components):
  custom nodes/edges, handles, controls, minimap, background grid, context menu,
  drag/drop, undo/redo, and whiteboard features.
- [Cytoscape.js layout guide](https://blog.js.cytoscape.org/2020/05/11/layouts/):
  large graph views should choose relevant subgraphs first, then layout; use
  grid/preset/hierarchical/force layouts by question, not by habit.
- [Unity Addressables overview](https://docs.unity.cn/Packages/com.unity.addressables%401.21/manual/AddressableAssetsOverview.html):
  addresses, groups, labels, and `AssetReference` are a good reference for
  future game asset indirection; do not hard-code renderer assets into Ref/Edge
  DTOs.
- [Papers Please official site](https://papersplea.se/) and
  [Steam page](https://store.steampowered.com/app/239030/Papers_Please/):
  study document-inspection interaction and constrained desk workflow after the
  basic comprehensive panels exist.

## Implementation Order

1. Document Web Step 1 and index business files.
2. Build the Obsidian-like read-only console shell around `/status`, current smoke monitor
   adapters, L2-B snapshot, and Graphiti status/search/draft.
3. Add BFF adapters only where a read model is missing; keep them Web-owned
   unless another lane needs the same contract.
4. Add Graphiti/FalkorDB operator flows only after dry-run, audit, backup, and
   explicit operator mode are represented.
5. Add Evidence/String Board and Papers Please-inspired interactions only after
   the normal management panels cover the required read/write surfaces.
