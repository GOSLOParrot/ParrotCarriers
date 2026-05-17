# L2-B Subgraph Tools Workplan - 2026-05-17

Status: temporary-active
Owner: Web Console lane
Scope: L2-B Memory Canvas subgraph tools, true L2-B/Graphiti read paths, and
operator-visible graph transformation previews. Promote durable decisions back
to `memory_graph_workspace_business_flow_20260513.md`,
`graphiti_management_business_flow_20260513.md`, and
`graphiti_l2b_ref_identity_design_20260517.md`.

## Target

Make the L2-B operation page useful for real subgraph work after large Graphiti
imports, without flattening Graphiti into a lossy local model:

- Graphiti remains the provenance/search graph and raw Graphiti records stay
  preserved in receipts.
- L2-B/RustWorkX is the bounded working-memory projection used for fast local
  topology, views, attention, and transformation previews.
- Web Console can test a real read path: selected L2-B UUIDs -> live bounded
  ego subgraph -> WCC/cluster context -> overlay/transform draft.
- Any write/materialization path remains explicit operator work. Preview-only
  receipts must say so.

## Research Index

### Skill / Local Sources

1. `parrot-cursor-skill-bridge`
   - Routed this task to the DSG/RustWorkX/L2-B skills before touching code.
2. `.cursor/skills/dsg-rustworkx-master/SKILL.md`
   - RustWorkX owns topology, but `rwx_idx` is ephemeral.
   - Stable identity must be UUID-based.
   - Online subgraph work must be bounded; depth caps and call limits are not
     optional for future expensive algorithms.
3. `.cursor/skills/dsg-l2b-node-organization-options/SKILL.md`
   - Current Node/Edge classes are view/algorithm categories, not a forced copy
     of Graphiti ontology.
   - Graphiti should be represented as preserved source pointers and raw
     envelopes until canonical identity/ref materialization is reviewed.
4. `.cursor/skills/dsg-attention-schema-papers/SKILL.md`
   - Retrieval should be local/ego-subgraph first.
   - Avoid global over-activation; schema reconstruction should be bounded and
     explicit about jump/depth.

### Official / External Sources

1. React Flow Sub Flows, updated 2026-03-25:
   `https://reactflow.dev/learn/layouting/sub-flows`
   - `parentId` is the current parent-node option; `parentNode` is deprecated.
   - Group/subflow nodes are good for visual grouping, but this is not a
     backend semantic graph by itself.
2. React Flow Node type:
   `https://reactflow.dev/api-reference/types/node`
   - Node fields include `parentId`, `extent`, and `expandParent`; useful later
     for visual foldable groups.
3. rustworkx 0.17.1 docs:
   `https://www.rustworkx.org/`
   - Current project version is 0.17.1; use this as the docs/version lock.
4. rustworkx `PyDAG.subgraph` docs:
   `https://www.rustworkx.org/dev/apiref/rustworkx.PyDAG.subgraph.html`
   - Subgraphs are new graph objects and can share node/edge payload references;
     do not treat copied subgraphs as a persistence boundary.
5. rustworkx connectivity docs:
   `https://www.rustworkx.org/dev/api/algorithm_functions/connectivity_and_cycles.html`
   - WCC/connected components are legitimate read-only cluster primitives.
6. Graphiti Searching:
   `https://help.getzep.com/graphiti/working-with-data/searching`
   - Public `search()` is hybrid; low-level `_search(SearchConfig)` can return
     nodes, edges, and communities and has recipe presets.
7. Graphiti Graph Namespacing:
   `https://help.getzep.com/graphiti/core-concepts/graph-namespacing`
   - `group_id` namespaces nodes/edges and should map to our partition field.
8. Graphiti Custom Entity/Edge Types:
   `https://help.getzep.com/graphiti/core-concepts/custom-entity-and-edge-types`
   - Custom Pydantic entity/edge types exist, but existing nodes continue to
     work if types are added later. Do not freeze a bad ontology too early.
9. Zep Graph Search BFS reference:
   `https://help.getzep.com/searching-the-graph`
   - BFS origin node UUIDs are a first-class retrieval bias in the managed API;
     our local L2-B tool should mirror the same "origin + bounded context"
     mental model.

## Requirement Restatement

The user wants the Web Console to test real data after importing large etiquette
books into Graphiti. A successful slice is not "another dry run". It needs at
least one route/control that proves:

1. It reads live L2-B state through `get_l2b_graph()`.
2. It uses stable UUIDs only; no RustWorkX internal index is exposed.
3. It returns a bounded subgraph context with nodes, edges, WCC/cluster context,
   and an overlay draft suitable for a later apply path.
4. It can sit after real Graphiti search/import-plan receipts without stripping
   raw Graphiti record metadata from already materialized L2-B edges/nodes.
5. It preserves the current architecture: Graphiti search/import remains the
   source/provenance path, L1.5/L2-B is the local working-memory buff/projection.

## TODO Before Implementation

- [x] Read relevant Parrot skills.
- [x] Check current L2-B policy routes and React Memory Canvas controls.
- [x] Check current L2-B graph API for safe read-only traversal.
- [x] Check official React Flow, rustworkx, and Graphiti docs.
- [x] Record this workplan before edits.
- [x] Re-read this file immediately before code changes.

## TODO During Implementation

- [x] Add a read-only backend route for live L2-B subgraph context.
- [x] Keep response explicit about `read_only`, `dry_run`, `true_connection`,
      depth cap, missing selections, and no apply route.
- [x] Serialize selected/ego nodes and edges with Graphiti/Ref metadata intact
      where the L2-B payload already has it.
- [x] Add API client method.
- [x] Add Memory Canvas subgraph control for live context inspection.
- [x] Keep existing overlay/transform previews working.

## TODO After Implementation

- [x] Add focused backend tests with a real in-memory `L2BGraph`.
- [x] Typecheck/build frontend if React files changed.
- [x] Run focused Web Console tests.
- [x] Run `git diff --check`; tolerate existing CRLF warnings only if they are
      outside the new content.
- [x] Audit against the original requirement:
      - real connection?
      - Graphiti raw preservation?
      - UUID/ref friendliness?
      - bounded graph transform?
      - no premature ontology lock?
- [ ] Promote durable result summaries to active docs and TODO board.

## Initial Implementation Decision

First slice: add `POST /api/l2b/subgraphs/context`.

Request shape:

- `node_uuids`: selected stable L2-B UUIDs.
- `depth`: bounded local expansion, clamped to `0..4`.
- `label`: optional overlay label.
- `include_clusters`: default true.

Response shape:

- `selected_node_uuids`, `missing_node_uuids`.
- `nodes`: selected + bounded ego nodes from live `L2BGraph`.
- `edges`: live directed edges whose endpoints both live in the included node
  set.
- `clusters`: WCC clusters touching the selection.
- `overlay`: draft-only `GraphOverlay` over those live node UUIDs.
- `true_connection`: `used_live_l2b_graph=true`, source=`get_l2b_graph`,
  no RustWorkX index exposure, no writes.

Deferred:

- Persistent overlay apply route.
- React Flow `parentId` group materialization.
- Graphiti remote search from this exact route. Graphiti search already lives
  under `/api/graphiti/subgraph/*`; this route consumes the materialized L2-B
  side after import/materialization.
- Expensive graph matching/VF2 and PageRank. Those need separate bounded
  algorithm gates.

## Implementation Ledger

### S1 - Live L2-B Subgraph Context

Status: implemented and verified

Files:

- `src/parrot/web_console/graph_policy.py`
- `src/parrot/web_console/server.py`
- `web/console_app/src/api.ts`
- `web/console_app/src/App.tsx`
- `web/console_app/src/styles.css`
- `tests/test_web_console/test_web_console_server.py`

Implemented:

- Added `POST /api/l2b/subgraphs/context`.
- Route reads `parrot.dsg.l2b_graph.get_l2b_graph()`.
- Request expands stable selected L2-B UUIDs by depth `0..4` over a local
  undirected adjacency built from live directed L2-B edges.
- Response returns selected/missing UUIDs, live node rows, live edge rows,
  WCC clusters touching the selection, and a draft `GraphOverlay`.
- Node rows preserve existing L2-B Graphiti/Obsidian/ref-ish fields:
  `graphiti_uuid`, `obsidian_uuid`, facts, tags, source/source_meta, meta,
  provenance stream, reference image path, and last sighting path.
- Edge rows preserve existing Graphiti/Ref metadata:
  `graphiti_uuid`, source/target Graphiti UUIDs, `ref_ids`, view classes, and
  raw edge `meta`.
- Receipt is forced read-only (`dry_run=true`, `operator_mode=false`) even if
  a caller asks for apply flags. Requested execution flags are echoed under
  `requested_execution.ignored_for_context=true`.
- React Memory Canvas subgraph tool now exposes `Depth` and `Inspect context`.
  The panel displays live node/edge/cluster counts and a true-connection line.

True-connection judgement:

- Pass: the route reads the real in-process L2-B graph through
  `get_l2b_graph()`, not a frontend fixture.
- Pass: backend regression uses a real `L2BGraph` instance and confirms live
  graph node/edge/ref/Graphiti metadata comes back.
- Pass: no RustWorkX integer index appears in the response.
- Pass: no L2-B write, Graphiti write, FalkorDB write, or overlay persistence
  occurs.
- Deferred: running 7893 must be restarted/reloaded before the new FastAPI
  route is active in an already-open browser session.

Verification:

- `.venv\Scripts\python.exe -m py_compile src\parrot\web_console\graph_policy.py src\parrot\web_console\server.py`
- `.venv\Scripts\python.exe -m pytest tests\test_web_console\test_web_console_server.py -q`
  - Result: `84 passed`.
- `npm run typecheck`
- `npm run build`
- `git diff --check -- ...`
  - Result: no whitespace errors; only existing LF/CRLF warnings.

Audit against requirement:

- Fits: gives L2-B operation page a real subgraph inspection path after Graphiti
  materialization/import.
- Fits: keeps Graphiti search/import-plan as the natural-language/provenance
  source path instead of hiding it behind L2-B.
- Fits: L2-B context is a bounded local buff/projection, not a lossy Graphiti
  replacement.
- Fits: Edge/Node classifications remain filter/algorithm-friendly and do not
  attempt to map every Graphiti relationship type into a fixed local enum.
- Remaining upgrade: add an operator-reviewed apply/materialization route for
  selected projection nodes/refs/edges only after rollback/audit storage is
  designed.
