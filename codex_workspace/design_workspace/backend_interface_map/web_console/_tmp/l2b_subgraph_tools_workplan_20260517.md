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
- [x] Promote durable result summaries to active docs and TODO board.

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

### S1.1 - `noble_etiquette` Partition Sync Bugfix

Status: implemented and verified

Problem:

- ECS/app-monitor `GET /api/graphiti/status` exposed `noble_etiquette`, but the
  local 7893 BFF normalized that partition back to `goslo` because the local
  `PARTITIONS` allowlist had not been updated.
- This made Web Console searches look like empty `goslo` searches even when the
  operator selected the new etiquette test partition.

Implemented:

- Added `PARTITIONS.NOBLE_ETIQUETTE = "noble_etiquette"`.
- Added the partition to `PARTITIONS.values()`.
- Added the partition to GOSLO `query_memory` tool routing.
- Added the partition to the React Source Board select.
- Updated Web route status test expectations.

Live smoke after restarting 7893:

- `GET http://127.0.0.1:8790/api/graphiti/status`: available, partitions
  include `noble_etiquette`.
- Restarted `http://127.0.0.1:7893/` with
  `PARROT_WEB_CONSOLE_GRAPHITI_URL=http://127.0.0.1:8790`.
- `GET http://127.0.0.1:7893/api/graphiti/status`: remote proxy enabled and
  partitions include `noble_etiquette`.
- `POST /api/graphiti/subgraph/search` with partition `noble_etiquette` now
  preserves `partition=noble_etiquette` instead of normalizing to `goslo`.
- Sample searches for `大小姐 贵族 礼仪`, `礼仪`, `贵族`, `大小姐`, `淑女`,
  `etiquette`, `noble`, and `lady` currently returned 0 hits from 8790. This
  is a data/search-result state, not the previous partition-routing bug.

Verification:

- `.venv\Scripts\python.exe -m py_compile src\parrot\memory\graphiti_client.py src\parrot\brain\tools\query_memory.py src\parrot\brain\graphiti_console.py`
- `.venv\Scripts\python.exe -m pytest tests\test_web_console\test_web_console_server.py -q`
  - Result: `84 passed`.
- `npm run typecheck`
- `npm run build`
- `git diff --check -- ...`
  - Result: no whitespace errors; only existing LF/CRLF warnings.

### S1.2 - Graphiti Episode/Entity Fallback Search

Status: implemented and verified offline; live etiquette retry deferred until
the user's import finishes.

Problem:

- Direct FalkorDB inspection showed `noble_etiquette` can contain
  `Episodic` nodes whose `content` has the imported text, while the existing
  cold-index fallback only scanned fact edges (`edge.fact`).
- That meant a freshly imported or edge-light Graphiti partition could be real
  and non-empty, but Web natural-language search still returned zero hits
  until Graphiti's main search/index path produced fact results.

Implemented:

- Kept Graphiti public/low-level search as the primary path.
- Kept the existing read-only fact-edge fallback as the first fallback because
  facts are still the best import candidates when present.
- Added a second read-only FalkorDB fallback over Graphiti nodes/Episodes when
  fact fallback returns no rows.
- The node fallback searches `name`, `summary`, and `content`, with null-safe
  predicates, and returns preserved Graphiti rows as `graphiti_episode` or
  `graphiti_entity`.
- Top-level receipts now report the actual fallback strategy from returned
  rows (`falkordb_partition_fact_scan` or `falkordb_partition_node_scan`)
  instead of always claiming fact scan.
- One-click import-plan envelopes now distinguish direct Episode/Entity hits
  from fact edges. A direct Episode hit creates a `graphiti_episode` Ref draft
  and episode bundle section, not a fake `graphiti_edge_uuid`.

Architecture boundary:

- This is not a new ontology and not a Graphiti mutation path.
- L2-B still receives preserved Graphiti envelopes; Episode/entity fallback is
  only a search/read rescue path for cold indexes or source-heavy imports.
- Large book/source refs should still be represented later through
  IdentityRefIndex / RefNode / Graphiti audit Episodes rather than by packing
  every file path into L2-B graph topology.

Verification:

- Added `test_graphiti_search_falls_back_to_episode_node_scan`, using a fake
  Graphiti driver where `search()` and fact fallback return empty rows but an
  `Episodic` node content row matches.
- Added
  `test_graphiti_subgraph_import_plan_preserves_episode_hit_without_fact_edge`
  so Episode fallback rows stay Episode refs/bundle rows through import-plan.
- `.venv\Scripts\python.exe -m py_compile src\parrot\brain\graphiti_console.py src\parrot\memory\graphiti_client.py src\parrot\brain\tools\query_memory.py`
- `.venv\Scripts\python.exe -m pytest tests\test_web_console\test_web_console_server.py -q`
  - Result: `86 passed`.

Live retry plan:

- Do not hammer `noble_etiquette` while the user is still importing large
  sources.
- After the import window, retry through 7893 -> 8790:
  `/api/graphiti/status`, `/api/graphiti/subgraph/search` with
  `partition=noble_etiquette`, and then `/api/graphiti/subgraph/import-plan`.
  Success means Web returns at least one preserved Graphiti row/bundle section
  from real imported data and the import-plan keeps raw Graphiti envelopes.

### S1.3 - Live ECS `noble_etiquette` Proof

Status: implemented, deployed to ECS app-monitor, and live-smoked

Deployment:

- Deployed the updated `src/parrot/brain/graphiti_console.py` to ECS
  `/opt/parrot/ParrotCarriers/src/parrot/brain/graphiti_console.py`.
- Backed up the previous remote file under
  `/opt/parrot/ParrotCarriers/codex_backups/m20_noble_episode_fallback_20260517174445`.
- Remote compile passed:
  `cd /opt/parrot/ParrotCarriers && .venv/bin/python -m py_compile src/parrot/brain/graphiti_console.py`.
- Restarted `parrot-app-monitor`; service returned `active`, PID `148490`.

FalkorDB true-data check:

- `GRAPH.LIST` includes `noble_etiquette`.
- `noble_etiquette` currently has `38` nodes and `70` edges.
- Sample `Episodic` rows include
  `noble_etiquette_01_greeting_rank`,
  `noble_etiquette_02_table_seating`,
  `noble_etiquette_03_correspondence_tone`, and
  `noble_etiquette_04_host_guest_boundary`.
- Sample Entity rows include `greeting_rank`, `noble_etiquette_v1`,
  `original_project_text`, `etiquette note`, and `relative rank`.

Live search proof after deploy:

- `POST http://127.0.0.1:8790/api/graphiti/subgraph/search` and the same call
  through `http://127.0.0.1:7893` both return real data for
  `partition=noble_etiquette`.
- Query `etiquette`, `limit=3`:
  `3 hit(s), 8 node(s)`, first hit UUID
  `ed386742-4e4e-4065-8151-6511960902b9`, kind `graphiti_fact`,
  text `Greeting rank etiquette requires deferring substantive topics.`
- Phrase probes also return real facts:
  `inventorying private rooms` -> `Guests are expected to avoid inventorying private rooms.`;
  `restrained warmth` -> written request tone fact;
  `single clear ask` -> correspondence tone fact;
  `without reordering` -> table seating fact.
- Chinese probes `礼仪` and `贵族礼仪` still returned 0 for the current data.
  Current sample content is English/topic-keyed, so this is not a connection
  failure by itself.

Live import-plan proof:

- Selected two real `noble_etiquette` hits from 7893 and posted to
  `/api/graphiti/subgraph/import-plan` with requested
  `dry_run=false/operator_mode=true`.
- Receipt correctly forced preview mode:
  `dry_run=true`, `operator_mode=false`.
- Bundle counts: `facts=2`, `entities=4`, `episodes=2`, `communities=0`.
- L2-B/RustWorkX preview:
  `projection_kind=graphiti_bundle_to_l2b_rustworkx_preview`,
  `l2b_nodes=6`, `l2b_edges=2`, `rustworkx nodes=6`, `rustworkx edges=6`.
- Policies stayed correct:
  `preserve_raw_graphiti=true`, `direct_l2b_write=false`.

Caveat:

- The live graph currently looks like the earlier small etiquette fixture, not
  several full books. If the user expected full book imports, the next check is
  the import job target: partition/group_id, FalkorDB graph name, and whether
  the import wrote to the ECS 6380/8790 environment used by Web Console.

### S1.4 - True Episode Write Bugfix and Full-Book Canary

Status: implemented locally, deployed to ECS app-monitor, true-write canary
passed

Bug found:

- The local Project Gutenberg source exists at
  `Noble Etiquette/pg35123.txt` (`519,313` bytes, `9,688` lines).
- A deterministic importer was added at
  `src/scripts/import_noble_etiquette_to_graphiti.py`. Dry-run found
  `67` candidate Episodes for `partition=noble_etiquette`.
- The first real write canary failed with DeepSeek:
  `BadRequestError: response_format type is unavailable`.
- Root cause: the installed `graphiti_core.llm_client.openai_generic_client`
  sends `response_format={"type":"json_schema"}` whenever Graphiti passes a
  Pydantic `response_model`; DeepSeek's official chat completion docs currently
  list `response_format.type` values as `text` or `json_object`.

Fix:

- Added `GraphitiLLMConfig.deepseek_json_schema_enabled`, controlled by
  `GRAPHITI_DEEPSEEK_JSON_SCHEMA_ENABLED`.
- When `GRAPHITI_LLM_PROVIDER=deepseek` but the json-schema opt-in flag is not
  set, Graphiti extraction/reranking now reports `requested_provider=deepseek`
  but uses effective provider `gemini`.
- `graphiti_provider_status()` now explains the fallback with
  `fallback_reason=deepseek_json_schema_response_format_disabled`.
- `ParrotConfig.google_api_key` now reads env at instantiation time so tests and
  restarted services observe the current runtime secret without leaking it.

Deployment:

- Deployed `src/parrot/shared/config.py` and
  `src/parrot/memory/graphiti_client.py` to ECS app-monitor.
- Re-deployed `src/parrot/brain/app_monitor_server.py`,
  `src/parrot/web_console/memory_ops.py`, and
  `src/parrot/web_console/graph_policy.py` after finding the live 8790
  import-plan route was stale/missing the L2-B transform preview.
- Remote backup:
  `/opt/parrot/ParrotCarriers/codex_backups/m22_graphiti_provider_fallback_*`,
  `m22_app_monitor_import_plan_route_*`, and
  `m22_graphiti_import_plan_preview_*`.
- Remote compile passed and `parrot-app-monitor` restarted active.
- Live 8790 status after restart:
  `requested_provider=deepseek`, `provider=gemini`, `model=gemini-2.5-flash`,
  `secret_configured=true`, `embedding_provider=gemini`.

True write proof:

- Ran
  `src/scripts/import_noble_etiquette_to_graphiti.py --apply --limit 2 --base-url http://127.0.0.1:8790 --timeout-s 420 --continue-on-error`.
- Both selected Episodes wrote successfully:
  `noble_etiquette_pg35123_intro_introduction_001` (`9,358` chars) and
  `noble_etiquette_pg35123_intro_introduction_002` (`9,007` chars).
- The two writes took about `146s` and `163s`; a full `67`-Episode import at
  that size would be a long-running job, so full-book import should be run as an
  explicit operator job with logs/progress rather than hidden inside Web.

Live data proof after write:

- Direct FalkorDB counts for `noble_etiquette` rose to `158` nodes and `282`
  edges.
- `MATCH (n:Episodic) WHERE n.name STARTS WITH 'noble_etiquette_pg35123'`
  returned `2` Episodes; all Episodic nodes returned `6`.
- 8790 and 7893 both search the newly extracted content. Query
  `Florence Hartley etiquette politeness`, `strategy=iterative_hybrid`,
  `depth=2`, returned `11 hit(s), 24 node(s)`.
- First real hit:
  `Florence Hartley is the author of "The Ladies' Book of Etiquette, and Manual of Politeness".`
- 8790 and 7893 import-plan over selected hits still force preview mode and return
  `graphiti_bundle_to_l2b_rustworkx_preview`, preserved raw Graphiti envelopes,
  pointer-style Graphiti entity nodes, `graphiti_fact` edges, and
  `direct_l2b_write=false`.
- Live 8790 proof over two hits returned `l2b_nodes=6`, `l2b_edges=2`,
  RustWorkX `nodes=6/edges=6`, `preserve_raw_graphiti=true`, and
  `direct_l2b_write=false`.

Remaining risk:

- The true importer works, but throughput is slow with large 9k-character
  Episodes. The next design slice should add a visible long-running import job
  lane with resume/skip-existing/progress and an operator choice between
  chapter-size Episodes, smaller extraction chunks, or Ref-only source
  manifests plus selective extraction.

### S1.5 - Importer Bugfix Review

Status: implemented, tested, and deployed to ECS script path

Bugs found:

- The importer stripped the Gutenberg text to `INTRODUCTION.` and then still
  used a hard-coded `index < 250` guard to skip table-of-contents chapters.
  In the real file this skipped the first body `CHAPTER I.` as well, so the
  first canary Episodes were named as `intro` while containing intro plus early
  chapter content.
- The importer wrote `source_file` as a local absolute Windows path in Episode
  bodies. That path is not a stable Ref after the data lands in ECS Graphiti.
- If the Graphiti API returned HTTP 200 with `success=false`, the CLI printed
  `error_count>0` but could still exit with status `0`.

Fix:

- Removed the `CONTENTS.` block before chunking and replaced the line-number
  guard with an explicit contents-state check.
- Default Episode names/source descriptions now use `v2`
  (`noble_etiquette_pg35123_v2_*`) so future corrected imports do not collide
  with the two earlier buggy canary Episode names.
- Episode bodies now write `source_file: Noble Etiquette/pg35123.txt` by
  default, with `--source-file-ref` available for an operator-supplied stable
  locator.
- CLI apply now exits non-zero when any Graphiti API row reports
  `success=false`.

Verification:

- Added `tests/test_scripts/test_import_noble_etiquette_to_graphiti.py`.
- New tests cover TOC skipping with real body Chapter I preservation,
  repo-relative `source_file` refs, and non-zero exit on API-level failure.
- Focused script tests: `3 passed`.
- Combined Web/script tests: `89 passed`.
- Real dry-run after fix returns `intro=1`, `chapter_01=2`, `chapter_02=3`,
  total `67`, with first names:
  `noble_etiquette_pg35123_v2_intro_introduction_001`,
  `noble_etiquette_pg35123_v2_chapter_01_conversation_001`.
- Deployed the updated script to ECS and remote `py_compile` passed. Remote
  dry-run confirms `episode_prefix=noble_etiquette_pg35123_v2` and
  `source_file_ref=Noble Etiquette/pg35123.txt`.

### S1.6 - Ladies Etiquette Importer Handoff Check

Status: checked on ECS, one default-mode mismatch fixed

User handoff claim:

- `src/scripts/import_ladies_etiquette_book_to_graphiti.py` is complete on ECS.
- Target shape: full 26 chapters, 76 text sub-episodes, prescribed ontology with
  `Role / Occasion / Item / Rule`, six custom edge types, saga chain
  `ladies_book_of_etiquette`, and custom extraction instructions.

Checks:

- The script was present on ECS but not yet present in this local workspace, so
  it was copied down for review and future push.
- ECS `py_compile` passed.
- ECS `Graphiti.add_episode` signature was inspected from the installed
  `graphiti_core`; it supports `entity_types`, `edge_types`, `edge_type_map`,
  `custom_extraction_instructions`, `saga`, and
  `saga_previous_episode_uuid`.
- The script dry-run parser returns all 26 chapters, no missing chapter numbers,
  and chunk counts sum to 76. Chapter XXI splits into 11 chunks; XIV, XIX, and
  XXIV are present.

Bug fixed:

- The script default generated one extra glossary episode per chapter, so a
  plain `--apply` would have written `102` episodes (`76 + 26`) despite the
  stated target being 76 sub-episodes.
- Fixed default behavior so glossary generation is opt-in via
  `--with-glossary`; `--no-glossary` remains as a harmless compatibility flag.
- Updated the script to import public `get_llm_clients` instead of private
  `_build_llm_clients`. `graphiti_client.py` now exports `get_llm_clients` and
  keeps `_build_llm_clients = get_llm_clients` as a compatibility alias.

Verification:

- Local `py_compile` passed for the importer and `graphiti_client.py`.
- Local Web tests passed after the public export change.
- Remote dry-run now shows `with_glossary=false` and
  `total_sub_episodes=76`.
- Remote dry-run with `--with-glossary` shows `total_sub_episodes=102`.

### S1.7 - Preview UUID / Materialized UUID Boundary Bugfix

Status: fixed, tested, committed, pushed, deployed, and live-smoked

Bug found:

- 8790/7893 true Graphiti search and import-plan were working, but the L2-B
  context probe could be misread as broken after import-plan. The reason was a
  boundary leak: import-plan returns preview projection UUIDs such as
  `graphiti:noble_etiquette:entity:*`, while
  `/api/l2b/subgraphs/context` reads only the live `get_l2b_graph()` state by
  durable L2-B UUID. If the preview UUID has not been operator-materialized into
  L2-B, context must report a missing live node, not silently imply Graphiti
  search failed.

Fix:

- `graphiti.subgraph.import_plan` now returns explicit
  `direct_graphiti_write=false`, `direct_l2b_write=false`,
  `materialization_state=preview_only_not_materialized`, and a
  `context_route_policy` explaining that `/api/l2b/subgraphs/context` requires
  materialized L2-B UUIDs.
- `l2b.subgraph.context` now identifies missing `graphiti:` preview UUIDs with
  `missing_graphiti_preview_node_uuids`,
  `context_lookup_hint=graphiti_preview_uuid_requires_l2b_materialization`, and
  `policies.materialized_l2b_uuid_required=true`.

Verification:

- Focused local regression tests passed using a repo-local temp dir on `D:`
  because `C:` was full: `2 passed`.
- Commit `b593f9e` was pushed to `origin/master`.
- ECS release updated `/opt/parrot/ParrotCarriers` to `b593f9e`, reinstalled the
  editable package, and restarted `parrot-orchestrator`,
  `parrot-app-monitor`, `parrot-scheduler`, `parrot-maid`,
  `parrot-goslo-chat`, and `parrot-brain`; all six returned `active`.
- Existing local `7893` was restarted with
  `PARROT_WEB_CONSOLE_GRAPHITI_URL=http://127.0.0.1:8790` and timeout `240s`.
- Live 7893 status now reports `remote: graphiti-core importable`,
  `remote_enabled=true`, `remote_base=http://127.0.0.1:8790`, and
  `noble_etiquette` present.
- Live 7893 search for `Florence Hartley etiquette politeness` returned
  `2 hit(s), 6 node(s)` with bundle counts `facts=2`, `entities=4`,
  `episodes=2`.
- Live 7893 import-plan over those real hits returned `success=true`,
  `selected=2`, `direct_l2b_write=false`,
  `materialization_state=preview_only_not_materialized`, `l2b_nodes=6`,
  `l2b_edges=2`, and `rustworkx_preview.available=true`.

Next design implication:

- The next real apply slice must be an operator-gated materialization route that
  resolves Graphiti source UUIDs through IdentityRefIndex/CORE-015 into durable
  L2-B UUIDs. Until that exists, import-plan is a faithful Graphiti/L2-B
  projection preview, not a live L2-B topology write.
