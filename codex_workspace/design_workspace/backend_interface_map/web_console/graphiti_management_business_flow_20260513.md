# Graphiti Management Business Flow (2026-05-13)

Owner chat: Web Console
Status: in_progress
Category: Web Console business interface
Scope: Graphiti/FalkorDB read, search, partitions, visualization, Episode, Graphiti API surgery, FalkorDB operator mode
Updated: 2026-05-13
Related TODO: WEB-006; WEB-007 through shared Ref/Edge rendering boundaries
Sources: `src/parrot/brain/graphiti_console.py`, `src/parrot/brain/app_monitor_server.py`, `src/parrot/memory/graphiti_client.py`, Graphiti skill, DSG L2-B skills

## Slice: Graphiti Console Management

### Implementation Signal 2026-05-13

- `src/parrot/web_console/server.py` now mirrors the existing monitor-safe
  Graphiti routes: `/api/graphiti/status`, `/api/graphiti/search`,
  `/api/graphiti/episode/draft`, and `/api/graphiti/episode`.
- `web/console/` now has a dedicated Graphiti view with dependency/config
  status, partition chips, scoped search result cards, Episode draft, and
  dry-run write preview.
- The Web UI still does not expose FalkorDB direct writes or irreversible
  Graphiti node/edge surgery. Those remain blocked on explicit operator mode,
  backup/export, audit logging, and rollback posture.
- A language bug discovered during Web QA was fixed at the same time:
  `lineb.profile` and `canvas.refs` are no longer swapped between English and
  Chinese dictionaries.
- Related memory-event boundary work now exists outside this Graphiti file:
  Trigger Lab and L1.5/L2-B operator drafts produce dry-run receipts before
  publishing to `CH_DSG_EVENTS` or applying L1.5/L2-B writes. Future Graphiti
  API node/edge/fact surgery should reuse the same receipt posture before any
  durable memory mutation.

### Implemented Interface Matrix

Checkpoint: 2026-05-13. This is the implemented safe seed for Graphiti
management; it is not the full FalkorDB/operator surgery surface.

| Endpoint | Purpose | Backend owner | Safety rule |
|:--|:--|:--|:--|
| `GET /api/graphiti/status` | Dependency/config/partition status. | `graphiti_status()` | Read-only. |
| `POST /api/graphiti/search` | Partition-scoped semantic search. | `search_graphiti()` | Read-only search; bounded limit. |
| `POST /api/graphiti/episode/draft` | Preview an Episode payload. | `draft_episode()` | Draft only; no durable write. |
| `POST /api/graphiti/episode` | Add an Episode through Graphiti. | `add_episode()` | Dry-run remains default; real write must be explicit operator action. |

Investigation note:

- The next Web memory-rendering pass should not start with raw FalkorDB
  controls. L2-B/Blackboard/IntentWorkspace visual usefulness is the immediate
  gap; Graphiti surgery should wait for backup/export, allowlisted mutation
  templates, and audit receipts.

## 2026-05-15 Upgrade Plan: DeepSeek, `arknights_test`, and L2-B Export

Owner: Web Console lane
Status: in_progress
Category: Web Console business interface / implementation plan
Scope: WEB-006, WEB-013, WEB-014, CORE-006, CORE-008, CORE-009
Sources: Graphiti skill, `src/parrot/brain/graphiti_console.py`,
`src/parrot/memory/graphiti_client.py`, DeepSeek official API docs,
Graphiti/Zep episode and temporal fact docs, PRTS Wiki `剧情一览`

### Research Conclusions

- DeepSeek official API docs list an OpenAI-compatible API with
  `base_url=https://api.deepseek.com` and V4 model ids including
  `deepseek-v4-pro` and `deepseek-v4-flash`. The repo must read the API key
  from `DEEPSEEK_API_KEY` or another local ignored secret source, never from a
  committed file or frontend payload.
- Graphiti episode ingestion uses `source_description` and `reference_time`.
  Bulk ingestion exists, but bulk mode should be reserved for empty/test graphs
  because it may skip edge invalidation behavior that matters for evolving
  facts.
- Graphiti/Zep temporal facts track when facts become valid and when they stop
  being valid. For Arknights testing, each episode should represent a chapter,
  arc, or major state change so Graphiti can model timeline and role/faction
  changes instead of flattening lore into static cards.
- PRTS Wiki `剧情一览` is useful as a source index for main story pages. URL
  extraction should be best-effort: store exact story/chapter URLs when links
  are available; otherwise store the parent page URL plus section/chapter id in
  `source_description`.
- 2026-05-16 user decision: `Arknights_test` is a large temporal test pack, not
  only a worldbuilding note. Prefer PRTS Wiki "剧情摘要/剧情速览" style source
  material where available, but ingest only compact original summaries, facts,
  and source URL/description. The important modeling goal is timeline and state
  change: faction changes, relationship changes, character development, and
  chapter/arc transitions should be separate episodes instead of flattened into
  one static status.

### Route Plan

These routes remain Web-only business interfaces until reviewed:

| Endpoint | Purpose | Safety rule |
|:--|:--|:--|
| `POST /api/graphiti/subgraph/search` | Natural-language Graphiti search returning bounded hits/subgraph candidates from one partition. | Read-only; tolerant bounded limit; partition allowlist includes `arknights_test`. |
| `POST /api/graphiti/subgraph/export-draft` | Convert selected Graphiti hits into a planned L1.5/L2-B export receipt with observations, `subgraph`, `edge_drafts`, and edge write policy. | Draft only; no Graphiti or L2-B mutation. Edge drafts are preview-only until L1.5-admitted nodes resolve to L2-B UUIDs. |
| `POST /api/graphiti/subgraph/import-plan` | Join the Graphiti export draft with the CORE-013 import-destination policy so the Source Board shows one coherent Graphiti -> L1.5 -> L2-B plan. Empty hit selections return `policy_skipped_reason` and no graph placement policy. | Draft only; no Graphiti, FalkorDB, L1.5, or L2-B mutation. Real export still goes through `/api/graphiti/subgraph/export` under operator mode; real edges remain a later L2-B edge route after UUID resolution. |
| `POST /api/graphiti/subgraph/export` | Export selected hits to L2-B by admitting observations through L1.5. | Supports dry-run or operator apply; React Settings `Mode` defaults the execute button to `dry_run=false` / `operator_mode=true`. No direct FalkorDB or direct L2-B Edge write. |

Exported observations should use `ObservationSource.USER_EXPLICIT` for the
first Web operator path and preserve Graphiti provenance in source metadata:
partition/group id, hit/fact text, score, Graphiti UUIDs when present,
source node UUID, target node UUID, source description, and source URL.

`edge_drafts` in the export receipt are not persisted L2-B edges. They describe
Graphiti fact source/target UUIDs so the operator can see the intended
subgraph, but actual L2-B edge writes require resolved L2-B node UUIDs after
L1.5 admission and must remain operator-gated.

### 2026-05-15 Implementation Checkpoint

- Implemented provider config in `src/parrot/shared/config.py` and
  `src/parrot/memory/graphiti_client.py`: Graphiti extraction/rerank defaults
  to DeepSeek via `DEEPSEEK_API_KEY`, `https://api.deepseek.com`,
  `deepseek-v4-pro`, and `deepseek-v4-flash`; Gemini remains the fallback and
  embedding provider.
- Implemented the `arknights_test` partition in the partition allowlist and
  Graphiti status/search route shape.
- Implemented Web-only BFF routes:
  `/api/graphiti/subgraph/search`,
  `/api/graphiti/subgraph/export-draft`, and
  `/api/graphiti/subgraph/export`.
- Export is dry-run/operator-gated and writes only through
  `L15Pool.admit(Observation(source=USER_EXPLICIT))`. It does not directly
  write FalkorDB or bypass Graphiti/L1.5 audit receipts.
- 2026-05-16 continuation adds
  `POST /api/graphiti/subgraph/import-plan` in the Web BFF. The route combines
  the Graphiti export draft with `l2b.graph_policy.import_draft` semantics so
  operators can see selected hits, L1.5 observations, Graphiti fact
  `edge_drafts`, destination policy, proposed overlay/draft edges, apply
  preconditions, and CORE-008/CORE-013 status in one receipt.
- 2026-05-16 bugfix: when no Graphiti hits are selected, `import-plan` returns
  `success=false`, `policy_skipped_reason=no_graphiti_observations`, and empty
  `import_policy` / `import_draft` instead of showing a fake destination plan.
- 2026-05-16 review fix: Graphiti `import-plan` now uses the normalized
  partition returned by `draft_graphiti_subgraph_export`, so receipt
  `partition`, Observation provenance, subgraph partition, and import-policy
  `source_id` stay aligned. It also forces top-level draft audit flags
  (`dry_run=true`, `operator_mode=false`) even if the caller sent apply flags.
- 2026-05-16 review fix continuation: Graphiti `import-plan` now preserves the
  export draft receipt id across both receipt shapes used in the Web stack:
  top-level `receipt_id` from `parrot.brain.graphiti_console` and nested
  `receipt.receipt_id` from `parrot.web_console.memory_ops`. This keeps the
  search/export -> destination-policy audit chain visible without changing the
  public route shape.
- The React Source Board now uses that unified import plan for the Graphiti
  policy button. This is still not a real apply path: the apply route remains
  `/api/graphiti/subgraph/export`, and L2-B Edge writes still require resolved
  Node UUIDs plus a separate operator-gated edge route.
- 2026-05-15 continuation: Graphiti search routes now tolerate bad `limit`
  values instead of route-level 500s. Export receipts include `subgraph`,
  `edge_drafts`, and `edge_write_policy`, making the source/target/fact shape
  visible while preserving the L1.5-first write boundary.
- Added `src/scripts/import_arknights_to_graphiti.py` as a dry-run-first
  fixture importer for compact original Arknights temporal episodes with
  source URL/source description and chapter-order metadata.
- Verification: Web Console route tests passed, DSG Obsidian/Calendar/trigger
  regressions passed, script dry-run passed, `py_compile` passed, and exact
  DeepSeek-key scan found no committed secret.

### 2026-05-15 React Source Board Slice

- The Memory page now exposes Graphiti as one tab in the L1.5 Source Board
  instead of mixing it with Obsidian/Calendar controls.
- Search returns the route's bounded `hits` and `subgraph` shape. The UI lets an
  operator select individual hits, previews selected subgraph Nodes/Edges on the
  React Flow canvas as read-only Graphiti preview objects, and keeps export
  actions separate from preview actions.
- `Export Draft` calls `/api/graphiti/subgraph/export-draft`; `Preview Apply`
  calls `/api/graphiti/subgraph/export` with `dry_run=true` and
  `operator_mode=false`. The separate execute/import action now follows the
  global Settings `Mode`, which defaults to real operator testing on the Web
  Console.
- Export receipts now render an inline Export plan in the Source Board: selected
  hits become L1.5 observations, and Graphiti source/target pairs appear as
  Edge drafts with `requires_resolved_l2b_node_uuid` policy.
- 2026-05-16 continuation: the Graphiti Source Board now has a compact status
  strip backed by `GET /api/graphiti/status`, showing provider/model,
  installed/missing state, partition count, and secret-configured booleans
  without exposing secrets. Failed searches and cleared selections now remove
  stale Graphiti preview Nodes/Edges from the Memory canvas.
- 2026-05-16 bugfix: Source Board import-policy preview now matches selected
  hits by both plain hit keys and `graphiti:<uuid>` React Flow preview ids, so
  proposed Graphiti source/target/fact Edges are preserved in
  `POST /api/l2b/graph-policy/import-draft` payloads.
- 2026-05-16 continuation: changing selected Graphiti hits now immediately
  refreshes the canvas preview without spamming the receipt rail. The same id
  normalization is used for preview Edges, so the operator can see the selected
  subgraph before choosing export or import-destination preview.
- 2026-05-16 review fix continuation: Graphiti search/export/import-plan API
  exceptions now clear stale export-plan state and show the exception inline in
  the active source card. A failed request should not leave an older destination
  policy or Edge draft looking like the current plan.
- 2026-05-16 selection-state fix: Graphiti hit selection, select-all,
  clear-selection, and partition/query/limit edits now invalidate the inline
  export/import plan. Preview/export/import buttons are still clickable with no
  selected hits so Web can return a visible `no_hits_selected` receipt instead
  of hiding the blocked state behind disabled controls.
- 2026-05-16 operator-import continuation: the Graphiti Source Board now
  exposes a secondary `Import to L1.5` action. It calls
  `/api/graphiti/subgraph/export` with `dry_run=false` and
  `operator_mode=true`, so selected hits are admitted through L1.5 as
  `USER_EXPLICIT` observations. This is not a FalkorDB write and not a direct
  L2-B Edge write; fact Edges remain `edge_drafts` until resolved L2-B Node
  UUIDs and the separate operator-gated Edge route are available.
- 2026-05-17 execution-mode fix: `Import to L1.5` no longer owns a local dry-run
  toggle. It obeys the global Web Console Settings `Mode`; default mode is real
  operator execution for testing, and preview mode forces the same action to
  return a dry-run receipt.
- Successful Graphiti operator imports now ask React to refresh
  `/api/app/live-state` and `/api/l15/pool` immediately and add a
  `memory.refresh_after_import` receipt with refreshed counts. This confirms
  the L1.5 admit chain in the Record rail without changing the Graphiti BFF
  route shape.
- 2026-05-17 ECS/app-monitor connection audit: when the lightweight Web
  Console BFF on `7893` does not install `graphiti-core`, `graphiti_status()`
  and `search_graphiti()` can proxy read-only status/search to an app-monitor
  Graphiti API if `PARROT_WEB_CONSOLE_GRAPHITI_URL` or
  `PARROT_GRAPHITI_REMOTE_URL` is set. The common local/ECS tunnel target is
  `http://127.0.0.1:8790`. The proxy is opt-in so tests and deployments do not
  silently reach a remote service. It is read-only for status/search; Graphiti
  subgraph export still writes only through the local Web BFF's L1.5 apply path
  unless the Web Console itself is deployed with the intended runtime target.
- The canvas preview is still a Memory operation aid, not the final full-screen
  L2-B graph monitor. WEB-013 owns the later React-Force-Graph/Cytoscape-style
  renderer evaluation.

### `arknights_test` Import Plan

- Add `arknights_test` to the Graphiti partition list/status/search UI.
- Create a dry-run-first import script that generates compact original episode
  summaries and fact candidates for main/major Arknights story arcs.
- Avoid saving long copied plot text. Store derived summaries, source URLs or
  source descriptions, chapter/order metadata, and optional reference times.
- Keep one episode roughly 300-800 Chinese characters. Split a character or
  story pack by source unit: base information, archive/profile segment,
  relationship update, chapter event, and aftermath/state-change segment rather
  than merging them into a single call to `add_episode`.
- If an exact URL cannot be extracted reliably, keep `source_description`,
  source title, parent page URL, and chapter/section hint so later operator
  review can repair provenance without losing the temporal episode.
- Use `deepseek-v4-pro` for Graphiti LLM extraction by default; keep provider
  fallback visible in status.
- Do not treat this test partition as production memory. It is an isolated
  fixture for Graphiti search/export/L2-B subgraph rendering.

### Interface Gaps

No shared core field is promoted yet. Candidate gaps:

- Graphiti-source virtual L1.5 bucket/grouping for UI filters belongs under
  CORE-008 review if the App lane needs a compact read subset.
- Graphiti-search-to-L2-B change events belong under CORE-009 only if App also
  consumes the same realtime/diff stream.
- Ref binding between Graphiti facts/episodes and L2-B Nodes stays aligned with
  CORE-006; Web operator repair actions stay outside App DTOs.

### A. Source Readback

- `src/parrot/brain/graphiti_console.py` already separates status, search,
  draft, and explicit episode writes. It defaults write paths to dry-run.
- `src/parrot/brain/app_monitor_server.py` exposes monitor endpoints:
  `/api/graphiti/status`, `/api/graphiti/search`,
  `/api/graphiti/episode/draft`, and `/api/graphiti/episode`.
- `src/parrot/memory/graphiti_client.py` owns the Graphiti client and partition
  constants (`goslo`, `maid`, `scene`, `user`).
- `src/parrot/dsg/l2b_graph.py` and the DSG interfaces already bridge L2-B and
  Graphiti for preload/search/archive use cases.
- `Interface/obsidian_true_connection_guide_20260509.md` is the boundary rule:
  UI and source integrations should not bypass L1.5/L2-B/ref flows to mutate
  Graphiti directly.
- Graphiti itself is not read-only. Official Graphiti docs describe node/edge
  CRUD, hard delete, and manual fact-triple writes. FalkorDB also supports
  openCypher queries and ships a browser UI for graph visualization and query
  management.

### B. Existing Core Interfaces

The first Web console version can be built from existing Web/business adapters,
then expanded into controlled surgery:

- Observe: status/config/dependency/partition visibility from
  `graphiti_status()`.
- Query: partition-scoped `search_graphiti(query, partition, limit)`.
- Draft: `draft_episode(...)` to preview the exact episode payload.
- Apply: `add_episode(..., dry_run=false)` only behind an operator action; keep
  `dry_run=true` as the default UI path.

This is enough for Web-side inspection and safe manual episode tests. It is the
seed, not the limit.

## Graph Surgery Plan

### 2026-05-17 Graphiti / L2-B / Ref Identity Research

Durable research note:
`graphiti_l2b_ref_identity_design_20260517.md`.

Conclusion:

- Graphiti search is real and should remain exposed in Web. It supports
  natural-language hybrid retrieval, node-distance reranking, configurable
  search recipes, custom entity/edge types, and node/edge CRUD.
- The current Web Graphiti-to-L2-B path is real but partial: search hits can
  become L1.5 observations and edge drafts, but Graphiti fact edges cannot be
  persisted as L2-B edges until endpoint Graphiti UUIDs resolve to L2-B UUIDs.
- `EdgeKind` should not be a hand-built mirror of Graphiti's extracted
  predicates. It should stay a coarse filter/view/algorithm class. Preserve
  Graphiti relation labels, fact text, endpoint UUIDs, episode UUIDs, scores,
  and raw payloads in metadata.
- Episode import is provenance, not identity management. The next shared gap is
  a durable IdentityMap plus RefIndex, staged as CORE-015.
- Nanobot/git/MCP should manage scans, ref health, moves, imports, and manifest
  diffs. Graphiti receives provenance episodes/facts about those changes; it
  should not be the sole authority for mutable ECS/local/Obsidian/URL paths.
- First backend slice added the Web-only CORE-015 routes
  `GET /api/memory/identity-ref-index`,
  `POST /api/memory/identity-ref-index/draft`, and
  `POST /api/memory/identity-ref-index/apply`. These persist only the
  IdentityRefIndex JSON under explicit operator mode; they do not write
  Graphiti/FalkorDB or materialize L2-B fact edges yet.
- M1 continuation added `POST /api/memory/identity-ref-index/verify`, giving
  Graphiti/Obsidian UUIDs and ref locators a deterministic health vocabulary
  before GraphitiResolver tries to materialize fact endpoints.
- M2 continuation added IdentityRefIndex merge/conflict receipts: one existing
  Graphiti/L2-B/ref/provider signal merges into its canonical record, while
  explicit cross-canonical or multi-canonical overlap is preserved in
  `conflicts[]` and marked `conflicted` without auto-rebinding existing owners.
- M3 continuation added raw Graphiti envelope receipts:
  `graphiti_raw_envelopes` preserve fact/entity/episode UUIDs, endpoint UUIDs,
  labels, custom attrs, scores, source refs, and the raw serialized hit;
  `identity_ref_drafts` convert those envelopes into CORE-015 fact/entity/
  episode candidates without writing IdentityRefIndex.
- M4 continuation added a read-only GraphitiResolver preview route under
  IdentityRefIndex. It resolves fact endpoints through CORE-015 and blocks edge
  materialization unless both source and target Graphiti entity UUIDs resolve to
  L2-B UUIDs.
- M5 continuation added `POST /api/memory/identity-ref-index/apply-graphiti-edge`.
  It re-runs endpoint resolution, blocks unresolved/conflicted/tombstoned
  endpoints, and then uses the existing L2-B edge apply route to create a
  `GRAPHITI_FACT` `SemanticEdge` with raw Graphiti metadata preserved.
- M6 continuation exposed these controls in the existing Graphiti Source Board:
  IdentityIndex load/counts, ref verification, edge resolver preview, preview
  edge apply, and operator materialize-to-L2-B. The UI still goes through
  CORE-015 and does not directly write FalkorDB or bypass L2-B.
- M7 continuation added `POST /api/memory/identity-ref-index/ref-scan-plan`
  plus a Source Board `Ref Scan Plan` button. This drafts a Nanobot/MCP/git
  check contract for Graphiti/Obsidian/local/ECS/URL refs while explicitly
  avoiding Graphiti/FalkorDB mutation, L2-B mutation, manifest writes, file
  moves, or ECS writes.
- M8 continuation added `POST /api/memory/identity-ref-index/ref-scan-dispatch`
  and `GET /api/memory/identity-ref-index/ref-scan-results`. Dispatch is
  operator-gated and queues only read-only `ref_scan` work; results are read
  back from the Scheduler ledger as review receipts and do not automatically
  mutate Graphiti, L2-B, RefIndex health, manifests, or ECS files.
- M9 continuation gave the Parrot fallback `NanobotConsumer` structured
  `ref_scan` behavior: local paths are checked read-only, remote URL/ECS/
  Graphiti locators remain explicit unknowns for future MCP checkers, manifest
  deltas are proposals only, and mutation requests are refused.
- M10 continuation live-smoked that path: `src/scripts/smoke_ref_scan.py`
  created temporary local/URL/ECS/Graphiti refs, dispatched `ref_scan` through
  Scheduler/Nanobot, and read back a `memory_ref_scan_result` ledger row. The
  successful run used an SSH tunnel to Castle/ECS Redis on isolated DB15. It
  proved the result return path and kept Graphiti pointer refs as explicit
  `unknown` until a real Graphiti/MCP lookup checker is implemented.
- M11 continuation added opt-in read-only probes to that same path. URL refs
  can run HEAD-only checks; Graphiti refs can call the app-monitor/Web Graphiti
  search API as a bounded probe; ECS refs are not mapped to local paths unless
  the worker is explicitly confirmed to be running on ECS. Live smoke with
  `--remote-checks` hit the real 8790 Graphiti API and returned a clear warning
  that search-probe is not a true UUID CRUD lookup, so the next Graphiti work is
  an explicit UUID lookup route rather than pretending search misses prove
  absence.

| Plane | Owner | Use for | Write shape |
|:--|:--|:--|:--|
| Ref management | App + Web | Add/remove/list/resolve refs that point at L2-B nodes, Graphiti UUIDs, episodes, photos, docs, or UI artifacts. | Shared core candidate; narrow DTO; reversible where possible. |
| Graphiti API | Web | Episode writes, node/edge CRUD, fact triples, partition-scoped searches, entity corrections. | Graphiti adapter methods with dry-run, audit record, and operator confirmation. |
| FalkorDB surgery | Web operator | Raw property fixes, label/edge inspection, emergency cleanup, direct Cypher experiments. | Server-side allowlisted Cypher templates first; raw query only in dev/operator mode after backup/export. |

The important split: App gets partial memory surgery through the Ref layer. Web
gets full memory surgery, including Graphiti API operations and FalkorDB
debug/admin tools.

## Last-Seen Decision

Default path: keep `last_seen` as a Graphiti-level semantic write for durable
memory, using the existing `parrot.dsg.interfaces.update_last_seen(...)` pattern
as the seed. It currently writes an episode directly through Graphiti; it does
not need Nanobot in the hot path.

Use this split:

| Case | Preferred path | Why |
|:--|:--|:--|
| Durable “object was seen” memory | DSG/L2-B event -> Graphiti episode/fact | Preserves provenance, partitioning, and future temporal search. |
| High-frequency pose/position updates | Runtime/L2-B state first, summarize to Graphiti | Avoids flooding long-term memory with frame-level noise. |
| Operator repair/backfill | Web FalkorDB surgery | Useful for exact property fixes, but bypasses Graphiti provenance unless Web writes an audit event too. |
| Scheduled audit/report/import cleanup | Nanobot or Scheduler task | Good for monitored background work, not for per-sighting latency. |

Trigger rule: add triggers at the normalized memory-event boundary, not at each
storage implementation. Graphiti writes, FalkorDB repair writes, and future
Nanobot jobs should all emit or record the same audit/trigger envelope. If a
path bypasses Graphiti and writes FalkorDB directly, Web must create the audit
record explicitly.

## Web Feature Set

- Partition browser: `goslo`, `maid`, `scene`, `user`, plus counts and recent
  episodes/entities/edges.
- Search: semantic Graphiti search and FalkorDB/Cypher query result rendering.
- Visual graph: node/edge canvas from selected query results, with label/type
  filters, inspect drawer, and ref badges.
- Episode management: list/search/add/draft; update/delete only with provenance
  warnings because episodes are source history.
- Entity/edge management: create/update/delete entity nodes and entity edges
  through Graphiti classes where possible.
- Fact triples: add a source node, target node, and relationship/fact using
  Graphiti `add_triplet`.
- Ref surgery: add/cancel/retarget refs between App artifacts, L2-B nodes,
  Graphiti UUIDs, episodes, and external files.
- L2-B bridge: show which Graphiti entities/facts are loaded into or linked
  from L2-B; L2-B CRUD stays in the Memory Graph workspace and should emit the
  same audit/trigger envelope when it causes Graphiti-visible changes.
- Trigger management: manual fire/manage belongs at the normalized memory-event
  boundary. Graphiti writes, L2-B corrections, and FalkorDB repairs should use
  comparable draft/audit records.
- FalkorDB tools: connect to FalkorDB Browser when available; expose a safer
  in-console query panel for allowlisted `MATCH`/`RETURN`/limited `SET`/`DELETE`
  workflows.
- Evidence/String Board: Web can render a board-style graph for memory surgery,
  but it should consume the same Ref/edge DTO as App instead of inventing a
  separate storage format.

### C. Missing Core Surface

No new core surface is required for a Web-only Graphiti/FalkorDB operator panel.

Promote a candidate to `../core_interface_candidate_queue_20260513.md` only if
another lane needs the same contract. Likely future candidates:

| Candidate | Promote only if | Notes |
|:--|:--|:--|
| `GraphitiStatusSnapshot` | Unity HUD or Scheduler also needs memory health. | Keep read-only and coarse. |
| `MemoryWriteDraft` | App and Web both need the same draft/approval flow. | Should produce episodes or IntentWorkspace drafts, not raw graph mutation. |
| `MemoryCorrectionDraft` | Node merge/alias/correction becomes shared. | Route through L1.5/L2-B/ref binding first. |
| `MemoryRefBindingApi` | App and Web both need add/remove/retarget refs. | This is the main shared candidate; App should use this instead of raw Graphiti/FalkorDB writes. |

Direct entity/node CRUD against Graphiti or FalkorDB can be implemented, but it
stays Web-operator only until there is a backup, dry-run, audit log, and
rollback story.

2026-05-17 M12 update:

- The existing Web Graphiti search surface is no longer only a one-shot
  search. `/api/graphiti/subgraph/search` accepts `strategy`, `depth`,
  `expansion_limit`, and optional `focal_node_uuid`. The first supported
  expansion strategy, `iterative_hybrid`, performs additional real Graphiti
  searches from discovered entity/fact terms and returns a `search_plan` so the
  operator can see which Graphiti queries ran.
- The 7893 Source Board exposes Strategy / Depth / Focal UUID controls and
  still imports selected Graphiti hits through L1.5 rather than direct L2-B or
  FalkorDB mutation.
- GOSLO Intent `query_memory` now uses this same subgraph search path, so the
  agent can perform natural-language Graphiti retrieval with bounded subgraph
  context.
- Live smoke on 2026-05-17 wrote a real test Episode to ECS 8790
  `arknights_test`, then queried through 7893 with depth 2 and imported two
  returned hits into L1.5 under operator mode. This proves connection + import;
  exact Graphiti UUID CRUD lookup remains the next upgrade.

2026-05-17 M13 update:

- Exact UUID lookup is now implemented at `/api/graphiti/lookup` and uses
  Graphiti official `get_by_uuid` helpers scoped to the requested partition
  graph. It can inspect entity/fact/episode UUIDs without relying on fuzzy
  search misses.
- Subgraph search enriches hits with full raw Graphiti fact/source/target
  lookup objects before L1.5 import, so L2-B receives a complete Graphiti
  evidence envelope instead of a lossy EdgeKind conversion.
- The local 7893 BFF proxies non-dry-run Episode writes and operator subgraph
  export to ECS 8790 when `PARROT_WEB_CONSOLE_GRAPHITI_URL` is configured.
- ECS FalkorDB persistence now mounts the actual image data path
  `/var/lib/falkordb/data` and enables AOF/everysec/noeviction through
  `REDIS_ARGS`. After a real FalkorDB restart, 7893 still found persisted
  `arknights_test` facts and enriched 16/16 requested Graphiti UUID objects.
- Because Graphiti hybrid search can be cold after restart while persisted
  facts exist, Web has a bounded read-only FalkorDB partition-graph fallback.
  It only returns Graphiti UUID/fact/source/target rows and then uses the same
  lookup/enrichment path; it is not a separate ontology or direct write path.

2026-05-17 M14 research update:

- Official Graphiti docs confirm the Web Console should treat Episodes as
  ingestion/provenance history, Graphiti search as hybrid/natural-language
  retrieval, and CRUD `get_by_uuid` as the exact inspection path for
  entity/fact/episode UUIDs. This matches the current 7893 -> ECS 8790 test
  bench direction.
- Graphiti `group_id` namespacing must stay visible in every Web operation:
  add Episode, search, lookup, export, import, and fallback scans. The
  partition is not optional state hidden in the server.
- Custom Graphiti entity/edge types should be introduced only as additive
  extraction guidance after the Ref/Identity model is stable. Web should not
  solve L2-B filtering by inventing one Graphiti edge type per visual view.
- rustworkx docs correct the identity policy: graph indices are stable only as
  runtime handles and may be reused after deletion. L2-B must keep external
  UUID maps and rebuild graph handles instead of persisting rustworkx indices.
- Ref management needs a mutable RefIndex/IdentityBinding layer next to
  Graphiti, not inside Episode text alone. Moving a file should update
  RefIndex and emit a Graphiti audit Episode; historical Episodes should stay
  historical.
- Nanobot + git + MCP is a good management loop only if Web keeps plan/apply
  control: nanobot proposes scans/repairs, MCP checks file/cloud/ECS state,
  git records manifest deltas, and Graphiti records audit Episodes after
  approved changes.

2026-05-17 M14 implementation update:

- Web now has semantic CORE-015 write-back routes for this research result:
  `POST /api/memory/identity-ref-index/graphiti-ref/draft` and
  `POST /api/memory/identity-ref-index/graphiti-ref/apply`.
- These routes are narrower than the generic IdentityRefIndex apply route:
  they require a Graphiti UUID, build a GraphitiRecordRef, bind reviewed
  ExternalRefRecords, draft RefMoveEvents for locator changes, and return a
  Graphiti audit Episode draft.
- Bugfix boundary: an empty locator does not create a placeholder
  ExternalRefRecord. GraphitiRecordRef-only identity binding is allowed, but
  mutable external refs require locator, canonical URI, or content hash.
- Default operator apply persists only the IdentityRefIndex JSON. It does not
  write L2-B, mutate Graphiti/FalkorDB, move files, update ECS paths, or change
  App DTOs.
- The next business proof should start from a real Graphiti search/lookup
  result, bind an Obsidian/ECS/local/file ref through this route, verify
  RefIndex persistence, then explicitly decide whether to write the generated
  audit Episode through `/api/graphiti/episode`.
- Live canary completed for the first half of that proof: the local updated BFF
  searched real ECS Graphiti `arknights_test`, selected fact UUID
  `0ea2009c-402d-4332-81b4-31fa57e67688`, and applied a temporary RefIndex
  binding with `dry_run=false` / `operator_mode=true`. Direct Graphiti and
  L2-B writes stayed false; the audit Episode was returned as `draft_only`.
- Audit write canary also passed when the operator explicitly set
  `write_graphiti_audit_episode=true`. Because ECS Graphiti writes may take
  longer than normal search/lookup, the successful canary used
  `PARROT_WEB_CONSOLE_GRAPHITI_TIMEOUT_S=240`; the receipt reported remote
  message `episode written` and mutation scope
  `memory_identity_ref_index_json_and_graphiti_audit_episode`.
- The existing 7893 React Source Board now exposes that business path under the
  Graphiti Export plan: selected search hits produce `identity_ref_drafts`, the
  operator chooses a Graphiti fact/entity/episode pointer, edits Ref ID/kind and
  locator/URL, previews the M14 write-back, and optionally enables the audit
  Episode write during apply. Runtime smoke after restarting 7893 with ECS
  proxy and 240s timeout confirmed true ECS search and search -> export draft ->
  identity_ref_drafts -> Graphiti-ref draft.
- Regression validation: the blank-locator write-back case now returns no
  external ref payloads, no ExternalRefRecords, and no RefMoveEvents.

2026-05-17 M15 SearchConfig update:

- `/api/graphiti/search` and `/api/graphiti/subgraph/search` now accept
  `search_recipe`, `node_labels`, and `edge_types` in addition to the existing
  partition/query/limit/focal controls.
- When local Graphiti exposes low-level `_search` or `search_`, Web maps recipe
  aliases to Graphiti SearchConfig recipes for combined, edge, node, and
  community search families. The route passes `group_id`, bounded config limit,
  optional focal UUID, and optional SearchFilters into Graphiti instead of
  inventing a local relation taxonomy.
- The receipt records `search_config.mode`, the requested recipe, the mapped
  recipe constant, low-level availability, and fallback reason if Web had to
  call public `search()` instead. This gives operators a truthful answer to
  "did this run Graphiti's recipe path or not?"
- The 7893 Source Board now exposes local expansion Strategy separately from
  Graphiti Recipe, plus Node labels / Edge types inputs. Edge type inputs are
  retrieval filters and view aids; they are not a plan to mirror every Graphiti
  predicate into a local `EdgeKind`.
- Focused regression proves `combined_rrf` plus filters reach `_search` as
  config/filter/group_id, and subgraph preview upgrades endpoint placeholders
  when Graphiti also returns the full entity node for the same UUID. Full Web
  route tests report `83 passed`, frontend typecheck/build passed, and the
  restarted 7893 sidecar returned true ECS results for
  `strategy=iterative_hybrid + search_recipe=combined_rrf` with `Entity` /
  `CrisisFact` filters. Live ECS receipts will show `_search` mode only after
  ECS/app-monitor is deployed with this M15 adapter.
2026-05-17 M16 Graphiti bundle update:

- `/api/graphiti/subgraph/search`, `/export-draft`, `/export`, and
  `/import-plan` now return `graphiti_bundle` as the reviewable unit for
  one-click import.
- The bundle preserves raw Graphiti selected-hit envelopes, fact/entity/
  episode/community sections, enriched UUID lookup payloads, search plan/config,
  Graphiti recipe/filter settings, edge drafts, and CORE-015 identity/ref
  drafts.
- Import-plan adds `graphiti_bundle.import_overlay` with CORE-013 destination
  policy, import draft, apply route, and operator preconditions. This is an
  overlay on preserved Graphiti data, not a conversion into local EdgeKind
  enums.
- L2-B remains a rustworkx projection layer: bundle receipts explicitly keep
  `preserve_raw_graphiti=true`, `direct_graphiti_write=false`,
  `direct_falkordb_write=false`, and `edge_materialization_policy` requiring
  resolved L2-B node UUIDs.
- Regression validation: full Web route tests report `83 passed`. The next
  live proof should deploy the M15/M16 adapter to ECS/app-monitor and verify
  a real 7893 -> 8790 receipt with `_search` mode plus bundle section counts.

2026-05-17 M17 Source Board bundle UI:

- The 7893 React Source Board now renders a `Graphiti bundle` review panel
  whenever search/export/import-plan receipts include `graphiti_bundle`.
- Operators can see bundle schema/selection count, facts/entities/episodes/
  communities, strategy/recipe/search-plan/lookup summary, projection policy,
  import overlay destination, and sample raw Graphiti rows without opening the
  JSON receipt rail.
- This is still read-model/UI surfacing: no new backend DTO, no direct
  Graphiti/FalkorDB write, and no L2-B edge materialization without resolved
  endpoint UUIDs.
- Validation: frontend typecheck/build passed, Web route tests remain
  `83 passed`, and 7893 live canary against ECS Graphiti returned true
  `arknights_test` bundle counts `facts=3/entities=4/episodes=0/communities=0`
  with first fact UUID `0ea2009c-402d-4332-81b4-31fa57e67688`. Remote
  `_search` mode proof still requires deploying the M15/M16 adapter to ECS
  8790.

2026-05-17 M18 ECS/app-monitor SearchConfig deployment:

- ECS 8790 now runs the Graphiti adapter itself, rather than relying on the
  local 7893 BFF to preserve bundle/search metadata.
- App-monitor route parity was fixed: `/api/graphiti/search` and
  `/api/graphiti/subgraph/search` forward `search_recipe`, `node_labels`, and
  `edge_types`; `/api/graphiti/subgraph/import-plan` is exposed remotely for
  draft-only L2-B import overlay review.
- Deployment was intentionally narrow: `app_monitor_server.py`,
  `graphiti_console.py`, and `memory_ops.py` were backed up, installed on ECS,
  compiled, and `parrot-app-monitor` was restarted.
- Remote 8790 canary against `arknights_test / Amiya Chernobog` with
  `combined_rrf`, `Entity`, and `CrisisFact` returned
  `search_config.mode="_search"`, `fallback=false`, `low_level="_search"`,
  first fact UUID `0ea2009c-402d-4332-81b4-31fa57e67688`, bundle counts
 `facts=3/entities=4/episodes=3/communities=0`, and UUID lookup `10/10`.
- Remote import-plan returned `import_overlay.destination=isolated_compartment`
  with one fact section, four IdentityRef drafts, and one L1.5 observation
  while preserving the preview-only `dry_run=true/operator_mode=false` policy.
- The existing 7893 Web Console now sees the same remote `_search` and bundle
  proof through `PARROT_WEB_CONSOLE_GRAPHITI_URL=http://8.216.45.45:8790`.

2026-05-17 M19 Graphiti bundle projection preview:

- Graphiti import-plan now calls the CORE-013
  `graphiti_bundle_projection` transform and embeds the result as
  `l2b_transform_preview` plus
  `graphiti_bundle.import_overlay.transform_preview`.
- The transform consumes preserved bundle sections instead of reparsing labels:
  Graphiti entities/episodes/communities become pointer-style L2-B preview
  nodes, facts become `graphiti_fact` preview edges, episode UUIDs become
  support links, and fact records remain available as Graphiti ref pointers.
- Raw Graphiti payloads stay attached under `meta.graphiti_raw` and
  `source_envelope`; L2-B only adds placement/preview metadata. This keeps the
  design aligned with the requirement that L2-B adapts to Graphiti rather than
  breaking or over-normalizing Graphiti data.
- RustWorkX is used only for an in-memory `PyDiGraph` topology preview:
  `node_count`, `edge_count`, weak-component samples, and
  `uuid_to_rwx_idx_preview` are useful review/debug fields, but
  `rwx_idx_policy=ephemeral_do_not_persist` is explicit.
- ECS 8790 was updated with `graph_policy.py` and `memory_ops.py`, backed up,
  compiled, and restarted to PID `127087`.
- True connection proof: both remote 8790 and local 7893 passthrough searched
  `arknights_test / Amiya Chernobog` through `_search`, returned first fact
  UUID `0ea2009c-402d-4332-81b4-31fa57e67688`, bundle counts
  `facts=3/entities=4/episodes=3/communities=0`, and import-plan projection
  counts `l2b_nodes=3`, `l2b_edges=1`, `episode_links=2`, RustWorkX
  `nodes=3/edges=3`, with `direct_l2b_write=false`.

### D. Observable Completion Signal

- Web shows Graphiti dependency/config status and available partitions.
- Web can search a selected partition and render result rows without writing.
- Web can generate an episode draft and compare it with dry-run output.
- A real write requires an explicit operator action and returns the written
  episode metadata or a clear failure message.
- Web can add/delete/retarget a Ref and App can consume the same Ref snapshot.
- Web can run Graphiti API-level create/update/delete on a test partition with
  audit output.
- Web can open or link to FalkorDB Browser for raw graph inspection, and can
  render a selected query result in its own canvas.
- Node correction flows generate drafts or ref/L2-B actions first unless the
  user deliberately enters operator surgery mode.
- `last_seen` live updates do not spam durable memory; durable Graphiti writes
  are batched or semantic, and direct FalkorDB writes carry explicit audit.
