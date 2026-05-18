# L2-B Subgraph And Graphiti Encoding Research TODO

Date: 2026-05-19
Owner: Codex Web Console / Graphiti / L2-B thread

## Stable User Notes

- Dragging ReactFlow nodes is fixed.
- The next issue is Graphiti imported test data showing mojibake in `content`, especially the `laptop_profile_test` episode `aaad5b1e-506e-4099-8e26-c0f26c4e81ed`.
- Future test imports must not produce Chinese mojibake.
- The current UI wording around "subgraph" is confusing:
  - Graphiti search returns a search-result subgraph/bundle.
  - Web "new subgraph" appears to create a L2-B overlay/draft, not a durable independent graph.
  - "Import subgraph" is better understood as one-click materialization of a selected external-source bundle into L2-B.
- Next desired capability:
  - Import Google Calendar subgraphs.
  - Import other source subgraphs or individual nodes.
  - Add a simple L2-B graph transform button: after loading/selecting nodes or a subgraph, restructure the selected L2-B nodes into a rule-based work subgraph.
  - This transform must not mutate Graphiti or other external sources.

## Encoding Issue Record

Observed payload:

- `source_meta.graphiti_partition`: `laptop_profile_test`
- `source_meta.graphiti_kind`: `episode`
- `meta.graphiti_raw.content`: mojibake such as `GOSLO æ¬æº...`
- L2-B correctly preserves `meta.graphiti_raw`, so L2-B is currently preserving bad upstream source data rather than proving it corrupted the text itself.

Local evidence:

- `src/scripts/import_laptop_profile_to_graphiti.py` displays mojibake if read by Windows PowerShell with its legacy default encoding, but displays correct Chinese when read with `Get-Content -Encoding UTF8`.
- The user-observed episode name `laptop_profile_plain_notes_20260518_a` and source description `goslo-laptop-profile-extra-text-20260518` are not the default rows produced by `src/scripts/import_laptop_profile_to_graphiti.py`.
- Current best hypothesis: the polluted row came from an extra/ad-hoc Graphiti write path or an API/client payload that already contained UTF-8 text decoded as a legacy single-byte encoding before `Graphiti.add_episode(...)`.
- The existing Graphiti and L2-B projection path intentionally preserves raw Graphiti data, so display-time decoding would hide the source problem and would violate the "preserve raw Graphiti" rule if used as the primary fix.

Encoding guard requirement:

- All future Chinese test import scripts must keep source files as UTF-8 and use explicit `encoding="utf-8"` for external text.
- Add a preflight guard before `add_episode` for expected Chinese fields.
- Reject or warn on mojibake signatures such as `Ã`, `æ`, `ç`, `鐢`, `绗`, `�`, especially when the script claims to import Chinese test facts.
- Add a smoke assertion that the imported partition can return both Chinese and English aliases correctly, e.g. `联想拯救者`, `Lenovo Legion laptop`, `杨枝甘露`, `mango pomelo sago`, `G504`.
- Clean or retire polluted `laptop_profile_test` rows after the fixed import path exists. Until then, prefer a fresh partition for verification.

## Current Subgraph Taxonomy

There are currently multiple "subgraph" concepts. They should stay separate in UI text and API docs.

### 1. Graphiti Search Subgraph / Bundle

Source: Graphiti/FalkorDB.

Shape:

- Produced by `/api/graphiti/subgraph/search`.
- Packaged as `graphiti_search_subgraph_bundle`.
- Contains Graphiti hits, raw envelopes, sections for facts/entities/episodes/communities, and an L2-B projection preview.
- It is not in L2-B until materialized.

Correct user-facing wording:

- "Graphiti 检索结果"
- "Graphiti bundle"
- "一键导入 Graphiti 检索结果到 L2-B"

Avoid wording:

- "导入子图" by itself, because it makes users think a separate Graphiti subgraph object is being moved wholesale.

### 2. L2-B Materialized Source Pack

Source: L2-B live RustworkX graph.

Shape:

- Produced by `/api/graphiti/subgraph/materialize-l2b` with `dry_run=false` and `operator_mode=true`.
- Writes deterministic pointer nodes/edges into the live L2-B graph.
- Does not write Graphiti/FalkorDB.
- Preserves raw Graphiti under node/edge metadata.
- Uses deterministic UUID policy like `graphiti:{partition}:{kind}:{graphiti_uuid}`.

Meaning:

- This is the current true "one-click import" path.
- It turns the selected Graphiti search bundle into L2-B pointer topology.
- It should be reloadable through live L2-B state and queryable by `/api/l2b/subgraphs/context`.

### 3. L2-B Live Context / Ego Subgraph

Source: L2-B live RustworkX graph.

Shape:

- Produced by `/api/l2b/subgraphs/context`.
- Read-only.
- Expands selected L2-B node UUIDs by depth, capped at 4.
- Returns an overlay with `overlay_kind=live_l2b_ego_subgraph`.
- Does not expose RustworkX integer indices.
- Does not mutate topology.

Meaning:

- This is an inspection view over the canonical L2-B graph.
- It is not a separate durable graph.

### 4. L2-B Draft Overlay / New Subgraph

Source: Web Console operator draft.

Shape:

- Produced by `/api/l2b/subgraphs/draft`.
- Creates a `GraphOverlay` draft with `overlay_kind=foldable_subgraph`.
- Current `apply_route` is empty.
- Frontend "New subgraph" adds a preview node with `kind=subgraph`, `preview=true`, and description "Backend overlay persistence is a later operator-gated route."

Meaning:

- New subgraph is not fully implemented as durable L2-B state yet.
- It is best treated as a visualization/review overlay until an operator-gated apply route exists.

### 5. Future L2-B Work Subgraph / Rule Transform

Source: L2-B only.

Desired shape:

- Select nodes or a current L2-B context overlay.
- Choose a simple rule:
  - by source partition,
  - by node kind,
  - by connected component,
  - by depth from selected node,
  - by edge kind,
  - by calendar day/time bucket,
  - by salience/attention bucket.
- Preview the cluster/subgraph.
- Operator applies the transform.
- Apply should create/update a L2-B overlay or grouping node and membership metadata/edges.
- Must not write Graphiti/FalkorDB or mutate external files/Refs.

Minimal decision implemented on 2026-05-19:

- Do not add `NodeKind.SUBGRAPH` yet.
- A durable work-subgraph is represented as a normal L2-B `EVENT` grouping node with:
  - `category="l2b_work_subgraph"`,
  - `source_meta.node_role="l2b_work_subgraph"`,
  - bounded `meta.source_pack` summary,
  - `CONTAINS` edges from the grouping node to member L2-B nodes.
- This keeps the current RustworkX/L2-B schema stable and still gives Web/GOSLO a selectable UUID anchor.
- A richer `NodeKind.SUBGRAPH` or overlay-store can still be added later if the graph transform system needs it.

## Current API Truth Table

| Capability | Route | Writes L2-B | Writes Graphiti | Status |
| --- | --- | --- | --- | --- |
| Graphiti natural language search | `/api/graphiti/subgraph/search` | No | No | True query/read path |
| Graphiti import plan | `/api/graphiti/subgraph/import-plan` | No | No | Preview only |
| Graphiti materialize to L2-B | `/api/graphiti/subgraph/materialize-l2b` | Yes, operator gated | No | True import path |
| L2-B live context | `/api/l2b/subgraphs/context` | No | No | True read path |
| L2-B new subgraph draft | `/api/l2b/subgraphs/draft` | No | No | Preview overlay only |
| L2-B work-subgraph apply | `/api/l2b/subgraphs/apply` | Yes, operator gated | No | True L2-B grouping path |
| L2-B transform draft | `/api/l2b/transforms/draft` | No | No | Preview only |
| Google Calendar import | `/api/google/calendar/import` | Yes, via L1.5 then optional work-subgraph | No | True source-pack import path |
| Obsidian vault import | `/api/l15/obsidian-vault/import` | Yes, via L1.5 then optional work-subgraph | No | True source-pack import path |

## Laptop Port And Read/Write Alignment

Observed laptop topology on 2026-05-19:

- `7893`: host Web Console BFF. React Console should normally call this stable browser-facing API. It owns environment selection, auth/header forwarding, proxying, operation receipts, and ECS/laptop switching.
- `18790`: Docker `app-monitor` service, exposed from container port `8790`. It is the laptop Web/App monitor backend used by the BFF.
- `17889`: Docker Brain/photo-upload server, exposed from container port `7889`. This is the process-local Brain room surface that reads the same in-memory L2-B graph the LiveKit Brain job is using.

Important bug class:

- `app-monitor` reads `/api/app/live-state` and `/api/l2b/snapshot` from Brain when `PARROT_APP_MONITOR_BRAIN_LIVE_STATE_URL=http://brain:7889` is configured.
- If operator writes are executed only inside `app-monitor`, the next live-state refresh reads Brain again and the Web canvas appears to lose nodes.
- Fix direction: keep React pointed at `7893`, keep `7893 -> 18790` as the normal configured route, but forward real operator writes from `18790` to Brain `17889/7889` when Brain live-state proxying is enabled.
- This is not browser persistence and not a separate L2-B store. It is read/write process alignment for the current Brain room.

Implemented checkpoint:

- Brain/photo-upload now exposes operator-gated write routes for L2-B node/edge operations, L2-B work-subgraph apply, Graphiti materialize-to-L2-B, Google Calendar import, and Obsidian vault import.
- App-monitor forwards real writes (`operator_mode=true` or `dry_run=false`) to Brain unless `_brain_proxy_disable=true`.
- App-monitor adds `data.brain_write_proxy` to returned receipts so Web can confirm the write landed in the Brain room job.
- Photo upload remains outside the global operator auth boundary so existing App image upload is not broken.

## TODO Before Implementation

1. Re-read this document plus:
   - `graphiti_management_business_flow_20260513.md`
   - `graphiti_l2b_ref_identity_design_20260517.md`
   - `memory_graph_workspace_business_flow_20260513.md`
   - Graphiti skill notes for episodes/entities/facts/group_id/search.
   - DSG L2-B node organization notes for pointer nodes, compartments, and views.
2. Decide UI naming:
   - Rename Graphiti button/labels from generic "导入子图" to "一键导入检索结果到 L2-B".
   - Rename "New subgraph" to "新建工作子图草稿" or "新建 Overlay 草稿" until persistence exists.
3. Decide whether durable L2-B work subgraph is:
   - overlay-only metadata,
   - a real `NodeKind.SUBGRAPH` node with membership edges,
   - or both, with overlay as the UI view and grouping node as the durable anchor.
4. Confirm whether corrupted `laptop_profile_test` should be cleaned in place or superseded by a new clean partition.

## Implementation TODO Candidates

1. Add a mojibake preflight helper/test for Graphiti import scripts.
2. Add `laptop_profile_test` to the Web Graphiti partition UI options or make options backend-driven from `/api/graphiti/status`.
3. Add UI helper text/tooltips for Graphiti parameters:
   - partition,
   - limit,
   - strategy,
   - recipe,
   - depth,
   - focal UUID,
   - node labels,
   - edge types,
   - destination.
4. Add a L2-B transform preview button for "wrap selected nodes as work subgraph".
5. Add an operator-gated apply route for durable L2-B work subgraph, after the representation decision is made.
6. Add a Google Calendar source-pack import route using the same source-to-L2-B materialization policy, separate from Graphiti.

## Implementation Checkpoint 2026-05-19

Completed in the first implementation pass:

- Added `src/parrot/memory/encoding_guard.py`.
  - Detects strong mojibake signals before Graphiti provenance writes.
  - Current strong signals include replacement characters, C1 control characters from UTF-8 decoded as latin-1/Windows-1252, and multi-token GBK/UTF-8 mojibake patterns.
- Updated `src/parrot/brain/graphiti_console.py`.
  - `/api/graphiti/episode/draft` now returns an `encoding_guard` report and warning when text looks corrupted.
  - `/api/graphiti/episode` blocks real writes when the guard is suspicious.
  - Dry-runs remain allowed so the operator can inspect the exact failed draft.
- Updated `src/scripts/import_laptop_profile_to_graphiti.py`.
  - The dry-run/apply path now preflights all local profile facts and returns code `2` if a suspicious body is found.
  - Verified the current six laptop profile facts render as correct UTF-8 Chinese and are not blocked.
- Updated `web/console_app/src/App.tsx`.
  - Graphiti partition options now include `laptop_profile_test` and merge any partitions returned by `/api/graphiti/status`.
  - UI wording now distinguishes "Graphiti search bundle/results" from L2-B subgraph/work-subgraph drafts.
  - Search parameter labels are explicit: strategy, recipe, depth, focal UUID, node labels, edge types.
- Added tests:
  - `tests/test_shared/test_encoding_guard.py`
  - `test_graphiti_episode_write_blocks_suspected_mojibake` in `tests/test_web_console/test_web_console_server.py`

Verification:

- `python -m pytest tests/test_shared/test_encoding_guard.py tests/test_web_console/test_web_console_server.py -q`
  - 102 passed in the first pass.
- `python -m py_compile src/parrot/memory/encoding_guard.py src/parrot/brain/graphiti_console.py src/scripts/import_laptop_profile_to_graphiti.py`
  - passed.
- `npm run typecheck` in `web/console_app`
  - passed.
- `npm run build` in `web/console_app`
  - passed, with the existing Vite chunk-size warning.
- `python src/scripts/import_laptop_profile_to_graphiti.py`
  - dry-run prints clean Chinese facts for `laptop_profile_test`.
- Restarted the local Web BFF on `127.0.0.1:7893`.
  - `GET /api/console/config` returned `200`.
  - Bad UTF-8/latin-1 mojibake draft returns `encoding_guard.suspicious=true`.
  - Bad mojibake real write returns `success=false`, `message=episode_body failed encoding guard`, and `write_blocked_reason=suspected_mojibake`.

Residual decisions:

- The polluted existing Graphiti rows in `laptop_profile_test` still need either in-place cleanup or retirement through a fresh clean test partition.
- Durable L2-B work-subgraph representation is still undecided:
  - overlay-only metadata,
  - real `NodeKind.SUBGRAPH` node plus membership edges,
  - or both.
- Google Calendar source-pack import should reuse the Graphiti materialization style, but should remain a separate source adapter, not a fake Graphiti bundle.

## Implementation Checkpoint 2026-05-19 B

Completed in the second implementation pass:

- Added `src/parrot/web_console/source_pack.py`.
  - Defines a small Source Pack envelope for external-source import previews and receipts.
  - It is a Web/operator contract, not a new SSOT and not a Graphiti replacement.
  - It preserves source identity, provider refs, source refs, item ids, and a bounded raw summary.
- Added operator-gated L2-B work-subgraph apply route:
  - `POST /api/l2b/subgraphs/apply`
  - Exposed on both Web BFF and App Monitor/Brain (`127.0.0.1:7893` can proxy operator writes to `127.0.0.1:18790`).
  - Real write requires `dry_run=false` and `operator_mode=true`.
  - Writes only L2-B RustworkX state.
  - Never writes Graphiti/FalkorDB or external files.
  - Uses an `EVENT` grouping node plus `CONTAINS` membership edges.
- Updated Google Calendar import:
  - Draft/plan/apply receipts now include `source_pack`.
  - Operator apply still goes through `L15Pool.admit(...)`.
  - After L1.5 returns admitted L2-B node UUIDs, the route materializes a L2-B work-subgraph by default.
  - `materialize_work_subgraph=false` can skip the grouping step.
- Updated Obsidian vault import:
  - Draft/plan/apply receipts now include `source_pack`.
  - Operator apply still goes through `UserTagFilter -> L15Pool.admit(USER_TAG_OBSIDIAN)`.
  - After L1.5 returns admitted L2-B node UUIDs, the route materializes a L2-B work-subgraph by default.
- Updated `SemanticNode.from_observation(...)`.
  - It now preserves `Observation.time_span`, so Google Calendar EVENT nodes retain event time ranges inside L2-B.
- Updated Web Console React app:
  - Added API client binding for `/api/l2b/subgraphs/apply`.
  - The work-subgraph tool panel now has an Apply button.
  - Preview mode returns an apply preview receipt.
  - Operator mode writes the L2-B grouping node/edges and refreshes live memory.

Verification:

- `python -m py_compile src/parrot/dsg/l2b_types.py src/parrot/web_console/source_pack.py src/parrot/web_console/memory_ops.py src/parrot/web_console/server.py`
  - passed.
- `python -m pytest tests/test_web_console/test_web_console_server.py -q`
  - 103 passed.
- `python -m pytest tests/test_brain/test_app_v1_monitor.py -q`
  - 16 passed.
- `npm run typecheck` in `web/console_app`
  - passed.
- `npm run build` in `web/console_app`
  - passed, with the existing Vite chunk-size warning.

Current semantics after this checkpoint:

- Graphiti search bundles still use their dedicated materializer because they must preserve raw Graphiti nodes/facts/episodes.
- Google Calendar and Obsidian now use the shared Source Pack language, but they do not pretend to be Graphiti bundles.
- L2-B work-subgraphs are runtime graph organization anchors, not external-source SSOTs.
- External source mutation remains out of scope for these import routes.

## TODO After Implementation

1. True-connection test:
   - search clean Graphiti partition,
   - materialize selected bundle into L2-B,
   - refresh live state,
   - use `/api/l2b/subgraphs/context` on materialized UUIDs.
2. Encoding test:
   - verify Chinese text displays correctly in Web JSON inspector and node labels/facts.
3. Source-boundary audit:
   - verify L2-B transforms do not call Graphiti writes.
   - verify raw Graphiti payload is preserved.
   - verify external Refs are referenced by pointer/locator, not copied blindly.
4. UI audit:
   - verify terminology no longer implies Graphiti has been mutated by L2-B work transforms.
   - verify draft-only actions are visually separate from true write actions.
