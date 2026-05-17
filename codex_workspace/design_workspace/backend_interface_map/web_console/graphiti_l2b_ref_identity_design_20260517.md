# Graphiti / L2-B / Ref Identity Design Note (2026-05-17)

Owner: Web Console chat
Status: in_progress
Scope: WEB-014, WEB-016, CORE-006, CORE-013, proposed CORE-015
Sources: Parrot `graphiti`, `dsg-rustworkx-master`, and
`dsg-l2b-node-organization-options` skills; current local code audit; official
Graphiti and rustworkx docs.

## Research Anchors

Official Graphiti docs confirm that Graphiti is more than an installed graph
backend:

- Graphiti builds temporal context graphs from entities, facts/relationships,
  and episodes, with provenance back to source episodes and temporal validity.
- Episode ingestion supports text, message, JSON, reference time, source
  description, and bulk import.
- Graphiti search supports broad natural-language hybrid search, node-distance
  reranking, and lower-level configurable recipes over edges, nodes, and
  communities.
- Graphiti custom entity and edge types are Pydantic models passed into
  `add_episode`, with explicit edge type maps.
- Graphiti CRUD supports node/edge save, delete, and get-by-uuid operations.

Official rustworkx docs confirm that `PyDiGraph` is an in-memory graph skeleton
with integer node/edge indices and arbitrary Python payloads. Those indices are
runtime handles, not business identity. L2-B therefore needs durable UUIDs and
explicit `uuid -> rwx_idx` maps outside rustworkx.

Reference URLs:

- https://github.com/getzep/graphiti
- https://help.getzep.com/graphiti/core-concepts/adding-episodes
- https://help.getzep.com/graphiti/core-concepts/custom-entity-and-edge-types
- https://help.getzep.com/graphiti/working-with-data/searching
- https://help.getzep.com/graphiti/working-with-data/crud-operations
- https://www.rustworkx.org/apiref/rustworkx.PyDiGraph.html

## Current Local Audit

Current Web Console state is not empty. The important pieces already exist:

- `src/parrot/brain/graphiti_console.py` implements status/search, bounded
  subgraph search, export draft, import plan, and operator-gated export through
  L1.5. It preserves Graphiti provenance and returns `edge_drafts`, but does
  not pretend Graphiti fact edges are already persisted L2-B edges. M16 adds
  `graphiti_bundle`, a schema-versioned package that keeps raw Graphiti hits,
  lookup rows, SearchConfig/search-plan evidence, identity/ref drafts, and
  L2-B import overlays together.
- `src/parrot/web_console/server.py` exposes `/api/graphiti/subgraph/search`,
  `/api/graphiti/subgraph/export-draft`,
  `/api/graphiti/subgraph/import-plan`, and
  `/api/graphiti/subgraph/export`.
- `src/parrot/dsg/l2b_types.py` gives `SemanticNode` stable `uuid`,
  `graphiti_uuid`, `obsidian_uuid`, `source_meta`, and `meta`. `SemanticEdge`
  now carries `graphiti_uuid`, Graphiti endpoint UUIDs, `ref_ids`,
  `view_classes`, and `meta`.
- `src/parrot/dsg/l2b_graph.py` maintains `_uuid_to_idx` and uses rustworkx
  indices only as runtime handles. However, `preload_from_graphiti()` is still
  a legacy weak path: it searches one partition and regex-parses `(uuid=...)`
  from fact text instead of preserving full Graphiti raw node/edge/episode
  shape.
- `src/parrot/dsg/ingest/base.py` and `src/parrot/dsg/ingest/runner.py`
  preserve selected Graphiti source fields in `source_meta`; the runner merges
  by provider identity first, then falls back to kind+label. It deliberately
  does not write back to Graphiti in the commit path.
- `src/parrot/dsg/l1_5/ref_table.py` has `GRAPHITI_UUID`, `OBSIDIAN_UUID`,
  `PHOTO_PATH`, `URL`, and other ref kinds. It is currently in-memory and its
  URL/Graphiti/Obsidian health verification is marked TODO.
- `src/parrot/dsg/l1_5/pool.py` binds Obsidian, Graphiti, photo, Google
  Calendar, and Google Message provider refs after admission. Google provider
  identity and Graphiti/Obsidian UUIDs are already preferred lookup signals.
- `src/parrot/brain/refs.py` and `src/parrot/shared/ref_binding.py` model
  session-scoped `RefBinding` targets, including `L2B_NODE`, `GRAPHITI_UUID`,
  `EPISODE`, and `UNRESOLVED`, but this is not yet a durable cross-process
  identity map.

## Edge Classification Decision

Edge kinds must not become a one-to-one mirror of every Graphiti extracted
predicate. Graphiti already extracts relation/fact text, source and target
entities, temporal provenance, and custom edge attributes.

For L2-B, `EdgeKind` should be a filter/view/algorithm channel:

- `semantic`
- `spatial`
- `temporal`
- `identity`
- `ref`
- `evidence`
- `graphiti`
- `hierarchy`

The original Graphiti fact text, relation label, source/target Graphiti UUIDs,
episode UUIDs, score, source URL, source description, and raw payload should be
kept in metadata. This gives Web filters and L2-A spatial displays a stable
coarse vocabulary without throwing away Graphiti's own relation extraction.

## Problem Statement

Only importing Episodes is not enough for ParrotCarriers.

Episodes are excellent provenance. They answer: what source event produced this
memory, when, and in what partition? They do not by themselves answer the
current operational questions:

- Which L2-B node is the canonical runtime projection of this Graphiti entity?
- Which Graphiti fact edge maps to which L2-B edge draft or persisted edge?
- Which Obsidian note, local photo, ECS path, URL, Google event, or large file
  is the current best locator for that entity?
- Which locators moved, broke, were replaced, or changed content hash?
- Which UUID should A10 / App / Web / Graphiti / nanobot use when talking about
  the same real-world object?

Graphiti manages memory graph facts and provenance. It should not be treated as
the only source of truth for mutable file paths or external refs.

## Proposed Architecture

### IdentityMap

Introduce a durable identity layer that owns canonical binding:

```text
IdentityRecord
  canonical_uuid
  l2b_uuid
  graphiti_entity_uuids[]
  graphiti_edge_uuids[]
  graphiti_episode_uuids[]
  obsidian_uuids[]
  ref_ids[]
  provider_keys[]          # google_calendar:calendar_id:event_id, message ids, etc.
  aliases[]
  confidence
  resolution_state         # weak | confirmed | conflicted | tombstoned
  created_at
  updated_at
  last_verified_at
  graphiti_raw             # raw source envelope fragments, not normalized away
  conflicts[]              # preserved collisions requiring operator resolution
  meta
```

This lets Graphiti UUID, Obsidian UUID, provider id, and L2-B UUID all bind to
one canonical entity without making any one system's id pretend to be universal.

### RefIndex / RefNode

Introduce a durable ref layer for files, URLs, photos, docs, ECS paths, and
external objects:

```text
RefRecord
  ref_id
  kind                  # obsidian_doc | photo | url | ecs_path | local_path | google_event | graphiti_entity
  canonical_uuid
  canonical_uri         # parrot://refs/{ref_id}
  locators[]            # mutable local/ECS/URL/Obsidian path candidates
  content_hash
  size
  mime_type
  version
  valid_from
  valid_to
  health                # ok | missing | moved | stale | forbidden | unknown
  managed_by            # user | nanobot | git | mcp | external
  git_commit
  last_seen
  meta
```

The L2-B node should usually hold a compact `ref_ids[]` pointer, not a large
file payload or a permanent assumption that a path never moves.

### Raw Graphiti Envelope

When importing Graphiti search results or preloading Graphiti into L2-B, preserve
the raw shape under a metadata envelope:

```text
graphiti_raw
  node / edge / episode class
  uuid
  labels
  name
  summary
  fact
  valid_at / invalid_at / created_at
  group_id / partition
  source_node_uuid
  target_node_uuid
  episode_uuids
  score / rerank metadata
  custom attributes
```

The current selective `source_meta` copy is good as a V1 visible surface, but
the long-term bridge should avoid silent data loss.

### Graphiti Subgraph Bundle

M16 introduces `graphiti_bundle` on Graphiti subgraph search, export draft,
operator export, and import-plan receipts. This is the reviewable unit for
"one-click import" and should be read before implementing future L2-B preload
or RustWorkX transform work.

The bundle is not an L2-B ontology. It preserves:

- `raw_envelopes`: the selected Graphiti hit envelopes.
- `sections.facts`: Graphiti fact/edge rows with raw payloads.
- `sections.entities`: endpoint/entity rows from raw payloads or UUID lookup.
- `sections.episodes`: episode lookup rows or episode UUID pointers.
- `sections.communities`: community rows when returned by Graphiti search.
- `search`: strategy, Graphiti recipe, node-label / edge-type filters,
  SearchConfig receipt data, and lookup summary.
- `edge_drafts` and `identity_ref_drafts`: L2-B/CORE-015 preview overlays.
- `l2b_projection_policy`: explicit statement that L2-B preserves raw
  Graphiti data and only materializes edges after endpoint UUID resolution.
- `import_overlay`: added by import-plan with CORE-013 destination policy and
  apply preconditions.

Future preload/import code should consume this bundle first. It should not
reconstruct Graphiti facts by parsing display labels, nor persist rustworkx
indices as identity. Graphiti UUIDs, L2-B UUIDs, and RefIndex canonical UUIDs
remain the durable join keys.

M19 implements the first controlled consumer of this bundle:
`graphiti_bundle_projection`. The transform is deliberately preview-only. It
maps bundle sections into L2-B pointer nodes and `graphiti_fact` preview edges,
preserves raw Graphiti rows in metadata, adds episode support links when
episode UUIDs are present, and runs a transient `rustworkx.PyDiGraph` to show
topology counts/components. The returned `uuid_to_rwx_idx_preview` is for
debugging only; `rwx_idx_policy=ephemeral_do_not_persist` is part of the
contract because rustworkx indices are graph-local handles, not source
identity.

### GraphitiResolver

Add a resolver pipeline:

```text
Graphiti search hit
  -> Graphiti raw envelope
  -> IdentityMap lookup/create
  -> RefIndex lookup/create for source refs
  -> L2-B node pointer or existing canonical node
  -> L2-B edge draft with Graphiti endpoint UUIDs
  -> operator/apply route materializes edge only after endpoint UUIDs resolve
```

If either endpoint is missing in L2-B, create a pointer/overlay candidate rather
than dropping the edge or inventing a false endpoint. Persisted L2-B edges use
coarse `EdgeKind.GRAPHITI_FACT` or another view kind, with the precise fact and
relation label preserved in metadata.

## Nanobot + Git + MCP Role

The user's proposed direction is good if responsibilities stay split:

- nanobot executes scans, moves, imports, Google/Obsidian/MCP fetches, health
  checks, and repair proposals.
- git tracks small text manifests, Obsidian notes, and reviewable ref-index
  changes.
- MCP connects to external systems and tools.
- Parrot `RefIndex` / `IdentityMap` remains the authority for current binding.
- Graphiti receives episodes/facts/provenance about changes and can be searched
  for history and associations.

Avoid direct Graphiti/FalkorDB database surgery as the normal path. Use Graphiti
API / Parrot resolver / L1.5 admission first. Direct DB surgery should be
operator-only migration or emergency repair with backup, audit receipt, and a
follow-up provenance episode.

## Objective Answer To The Current Questions

- Graphiti can really search. The Web Console already has natural-language
  Graphiti search and bounded subgraph export routes, and recent live smoke
  against 7893 returned real `arknights_test` hits.
- Graphiti can be imported toward L2-B through L1.5 admission, edge drafts,
  IdentityRef previews, and now the M16 `graphiti_bundle`. Full node/edge
  materialized import still needs `GraphitiResolver` plus durable IdentityMap
  before resolved edges become RustWorkX topology.
- The current UUID binding is useful but skeletal. L2-B UUID, Graphiti UUID,
  Obsidian UUID, Google provider IDs, and session RefBinding ids exist, but
  there is no durable cross-process identity table.
- Ref management is the biggest missing foundation. Current `RefTable` is
  in-memory and does not verify URL, Graphiti UUID, or Obsidian UUID health.
- Unified Episode should remain the provenance stream. It should not replace a
  durable RefIndex / IdentityMap. The best design is Episode + IdentityMap +
  RefIndex, with Graphiti custom types added after the core binding model is
  stable.
- Edge categories should stay coarse for filters, spatial views, and algorithms.
  Graphiti's extracted relation/fact data should be preserved as raw/provenance
  metadata, not compressed into a fixed enum.

## Phased Work

P0, current documentation:

- Record this research note.
- Link it from Web README, TODO, Graphiti business flow, Memory business flow,
  and core candidate queue.

P1, durable skeleton:

- Add a `MemoryIdentityRefIndex` candidate implementation behind Web-only
  routes or local storage.
- Persist `IdentityRecord` and `RefRecord` with read/list/draft-update routes.
- Add health checks for local path, URL, Obsidian UUID, and Graphiti UUID.

2026-05-17 first backend slice:

- Added `src/parrot/dsg/identity_ref_index.py` as a file-backed CORE-015
  prototype.
- Added Web routes `GET /api/memory/identity-ref-index`,
  `POST /api/memory/identity-ref-index/draft`, and
  `POST /api/memory/identity-ref-index/apply`.
- The draft route does not persist. The apply route persists only with
  `dry_run=false` and `operator_mode=true`.
- The route receipts explicitly report no direct L2-B write, no direct
  Graphiti/FalkorDB write, no file move, and no App DTO mutation.
- Tests now cover draft/no-persist, dry-run apply/no-persist, operator
  persistence, and JSON reload.

Remaining P1 work: locator health verification and merge/conflict policy.

2026-05-17 M1 continuation:

- Added deterministic health verification through
  `POST /api/memory/identity-ref-index/verify`.
- The verifier checks local paths directly, reports URL/ECS/remote locators as
  `unknown` until a nanobot/MCP-backed checker is added, and accepts explicit
  Graphiti/Obsidian UUID status maps for deterministic tests.
- Dry-run verification reports health without persisting. Operator apply can
  persist computed RefRecord health to the local IdentityRefIndex JSON.
- Validation: focused IdentityRefIndex route tests passed; full Web route tests
  now report 63 passed.

2026-05-17 M2 continuation:

- Added explicit merge/conflict policy to `MemoryIdentityRefIndex.upsert`.
- One matching existing identity signal (`l2b_uuid`, Graphiti entity/edge/
  episode UUID, Obsidian UUID, provider key, or ref id) merges into that
  canonical record.
- Explicit cross-canonical writes or multiple matched canonical records record
  `conflicts[]`, set affected identities to `conflicted`, and preserve
  conflicting UUID/ref evidence without auto-overwriting the existing owner.
- Ref id collisions do not silently rebind the existing `RefRecord`; receipts
  expose `merge_report`, `conflict_count`, and `conflicts`.
- Validation: focused IdentityRefIndex route tests now report 3 passed; full
  Web route tests now report 64 passed; backend `py_compile` passed.

2026-05-17 M3 continuation:

- `POST /api/graphiti/subgraph/export-draft` now returns
  `graphiti_raw_envelopes` for selected hits. The envelope preserves fact text,
  Graphiti edge UUID, source/target entity UUIDs, episode UUIDs, source URL/
  description, score, labels, custom attributes, and the raw serialized hit.
- The same draft returns CORE-015 `identity_ref_drafts` for Graphiti fact,
  entity-pointer, and episode-pointer candidates. These are preview-only and
  must be applied through `/api/memory/identity-ref-index/apply` after operator
  review.
- `POST /api/graphiti/subgraph/import-plan` forwards the raw envelopes and
  identity/ref drafts alongside CORE-013 placement policy, and now lists
  CORE-015 as part of the import plan.
- Real operator export through L1.5 also carries `graphiti_raw` in Observation
  meta and USER_EXPLICIT source metadata, so L2-B no longer only receives a
  lossy fact-text subset.
- Validation: focused Graphiti subgraph route tests report 5 passed; full Web
  route tests report 64 passed; backend `py_compile` passed.

Remaining P1/P2 work after M3: GraphitiResolver endpoint resolution and
materialized edge path. M4/M5 below close the backend path; Web UI surfacing
remains.

2026-05-17 M4 continuation:

- Added read-only GraphitiResolver preview route:
  `POST /api/memory/identity-ref-index/resolve-graphiti`.
- The resolver accepts `edge_drafts`, `edges`, or a single source/target/fact
  UUID payload. It resolves Graphiti source/target entity UUIDs and fact UUIDs
  through CORE-015 `MemoryIdentityRefIndex`.
- Endpoint status is explicit: `resolved_l2b`, `canonical_only`, `missing`,
  `conflicted`, `tombstoned`, or `blank`.
- A later L2-B edge write is allowed only when both source and target endpoints
  are `resolved_l2b`. Missing endpoints return operator-review pointer
  candidates; conflicted endpoints block materialization.
- Receipts report `direct_l2b_write=false`, `direct_graphiti_write=false`, and
  `mutated=false`; this route only previews resolver state.
- Validation: focused IdentityRefIndex route tests now report 5 passed; full
  Web route tests now report 66 passed; backend `py_compile` passed.

2026-05-17 M5 continuation:

- Added materialized L2-B edge apply route:
  `POST /api/memory/identity-ref-index/apply-graphiti-edge`.
- The route re-runs GraphitiResolver before writing, so it does not trust stale
  client drafts. It blocks missing, canonical-only, conflicted, tombstoned, or
  blank source/target endpoints.
- When both endpoints are `resolved_l2b` and `operator_mode=true` with
  `dry_run=false`, the route delegates to the existing
  `apply_l2b_edge -> L2BGraph.connect(SemanticEdge)` write path.
- Applied edges preserve Graphiti fact UUID, source/target entity UUIDs,
  canonical UUID metadata, ref ids, selected raw Graphiti edge payload, and
  `EdgeKind.GRAPHITI_FACT` / Graphiti view classes.
- Validation: focused IdentityRefIndex/Graphiti edge tests now report 7 passed;
  full Web route tests now report 68 passed; backend `py_compile` passed.

Remaining P2 work: Web UI surfacing for the IdentityRefIndex snapshot, health,
resolver preview, and materialized Graphiti edge apply controls.

2026-05-17 M6 continuation:

- Surfaced the CORE-015 backend path in the existing React Graphiti Source
  Board instead of creating a separate Web Console.
- The card can load `GET /api/memory/identity-ref-index`, run deterministic
  `POST /api/memory/identity-ref-index/verify`, resolve current Graphiti
  `edge_drafts` through `POST /api/memory/identity-ref-index/resolve-graphiti`,
  preview `apply-graphiti-edge`, and operator-apply a selected resolved fact
  edge into L2-B.
- The UI still does not write Graphiti/FalkorDB or bypass L2-B. Materialization
  goes through the M5 CORE-015 route and then the existing L2-B edge writer.
- `npm run build` refreshes `web/console_dist`, so the existing 7893 static
  Web Console path receives the controls.
- Validation: `npm run typecheck` passed; `npm run build` passed.

Remaining P2/P3 work: nanobot/git/MCP ref scan and repair contracts for URL,
ECS, Obsidian, and file locator health.

2026-05-17 M7 continuation:

- Added a plan-only Nanobot/git/MCP ref scan contract:
  `POST /api/memory/identity-ref-index/ref-scan-plan`.
- The route reads CORE-015 `RefRecord`s and drafts a `ref_scan` task payload
  with `result_channel=memory_ref_scan_result`, a proposed git manifest path,
  local/url/ECS/Graphiti/Obsidian locator classifications, MCP check names,
  expected result fields, and explicit disallowed operations.
- It does not stat local files, call ECS, query Graphiti, write the manifest,
  update RefIndex health, mutate L2-B, mutate Graphiti/FalkorDB, or touch App
  DTOs. The normal write-back remains later operator review through
  IdentityRefIndex verify/apply receipts.
- Registered `ref_scan` in the Scheduler Nanobot task catalog so future
  dispatch validation recognizes the task type, but M7 intentionally does not
  add an execute route.
- Surfaced the dry-run contract in the existing Graphiti Source Board through
  a `Ref Scan Plan` button and compact row preview, with the full receipt in
  the operation rail.
- Validation: backend `py_compile` passed; focused CORE-015 route tests now
  report 8 passed; full Web Console route tests report 69 passed; frontend
  `npm run typecheck` and `npm run build` passed.

Remaining P3 work: operator-gated ref-scan dispatch, bounded result-history
readback, and reconciliation rules for read-only scan reports before any
repair/write workflow is added.

2026-05-17 M8 continuation:

- Added operator-gated ref scan dispatch:
  `POST /api/memory/identity-ref-index/ref-scan-dispatch`.
- Dispatch reuses the M7 plan route, requires `operator_mode=true` and
  `dry_run=false`, and enqueues a Scheduler/Nanobot `ref_scan` task with
  `scan_mode=read_only` and `allow_mutation=false`.
- Added read-only result intake:
  `GET /api/memory/identity-ref-index/ref-scan-results`.
- Result intake reads the existing Scheduler trigger-result ledger and filters
  rows whose result channel is `memory_ref_scan_result`. It parses result
  samples, manifest deltas, warnings, and scan ids, but does not write
  RefIndex health or repair any locator.
- The existing Graphiti Source Board now exposes `Dispatch Scan` and
  `Scan Results` beside the M7 `Ref Scan Plan` button. The global Web Settings
  mode controls whether dispatch is preview or real operator enqueue.
- Validation: focused CORE-015 tests now report 12 passed; full Web Console
  route tests report 73 passed; frontend `npm run typecheck` and
  `npm run build` passed.

Remaining P3 work: implement or configure the actual nanobot/MCP worker
behavior for `ref_scan`, then run a read-only live smoke against local/ECS/URL/
Graphiti refs before adding any RefIndex health write-back or repair route.

2026-05-17 M9 continuation:

- Implemented structured `ref_scan` behavior in the Parrot fallback
  `NanobotConsumer`.
- Local path locators are checked read-only with `Path.stat()` and bounded
  SHA-256 hashing. The fallback worker proposes manifest deltas for health/hash
  updates but does not write manifests or RefIndex health.
- URL, ECS, Graphiti, and opaque locators return explicit `unknown` results
  with reasons such as `ecs_path_not_checked_by_fallback` or
  `graphiti_pointer_not_checked_by_fallback`; those are reserved for the real
  MCP/remote checker.
- Any task that asks for `allow_mutation=true` is refused with
  `ref_scan_worker_refuses_mutation`.
- Validation: worker + CORE-015 focused tests report 15 passed; Web route +
  worker tests report 76 passed.

2026-05-17 M10 continuation:

- Added `src/scripts/smoke_ref_scan.py` as a repeatable read-only smoke for
  CORE-015 ref scanning.
- The script creates a temporary IdentityRefIndex with local, URL, ECS, and
  Graphiti pointer refs, starts the normal SchedulerService and Parrot fallback
  NanobotConsumer, dispatches `ref_scan`, and waits for
  `memory_ref_scan_result` in the Web result-history reader.
- Local Redis was not running, so the smoke first proved a clean
  `Redis unavailable` skip path, then ran through an SSH tunnel to Castle/ECS
  Redis on isolated `REDIS_DB=15` to avoid production DB0.
- The successful ledger row had 4 ref results: the temporary local Obsidian
  document returned `ok` with SHA-256, while URL, ECS path, and Graphiti pointer
  refs returned explicit `unknown` rows that require MCP/remote checkers.
- The worker proposed 2 manifest deltas for the local ref health/hash and made
  no writes to manifests, RefIndex health, L2-B, Graphiti/FalkorDB, ECS files,
  or App DTOs.

2026-05-17 M11 continuation:

- Added opt-in read-only remote checker execution to the Parrot fallback
  `ref_scan` worker.
- URL refs can run `HEAD` only, with no response-body read. `2xx/3xx` returns
  `ok`, `404/410` returns `missing`, auth or transport failures stay
  `unknown`.
- Graphiti refs can run a read-only search-probe through
  `PARROT_WEB_CONSOLE_GRAPHITI_URL` / `PARROT_GRAPHITI_REMOTE_URL`; exact UUID
  hits return `ok`, but misses stay `unknown` with
  `graphiti_search_probe_is_not_uuid_crud_lookup` because search is not a true
  CRUD lookup.
- ECS refs can run local stat/hash only when the worker is explicitly confirmed
  to be running on ECS (`ecs_local_check_confirmed` or worker-side env). The
  local fallback does not map `ecs://` paths by default, preventing false local
  path checks on Windows/dev machines.
- The existing 7893 Graphiti Source Board now exposes a `Remote probes`
  checkbox that passes `remote_checks=[url, ecs, graphiti]` into
  `ref-scan-plan` and `ref-scan-dispatch`.
- Live smoke through ECS Redis DB15 with `--remote-checks` returned: local file
  `ok` plus SHA-256, URL `missing` with HTTP 404, Graphiti pointer `unknown`
  through the real 8790 probe, ECS `unknown` because ECS-local execution was
  not confirmed, and no writes to manifests, RefIndex, L2-B, Graphiti, ECS, or
  App DTOs.
- Validation: backend `py_compile` passed; worker + Web route tests report
  79 passed; frontend `npm run typecheck` and `npm run build` passed.

Remaining P3 work: replace the Graphiti search-probe with a real UUID CRUD/
lookup route where available, run ECS path stat/hash inside an ECS-confirmed
nanobot/MCP worker, and only then design reviewed write-back routes.

P2, Graphiti import upgrade:

- Replace legacy `preload_from_graphiti()` text-regex UUID extraction with a
  Graphiti raw-envelope import path.
- Add `GraphitiResolver` to map Graphiti entity/edge/episode UUIDs to canonical
  UUIDs and L2-B UUIDs.
- Materialize Graphiti fact edges only after endpoint resolution.

P3, nanobot/git/MCP management:

- Operator-gated nanobot ref-scan dispatch and ref-health result intake are now
  implemented and live-smoked through the Scheduler/Nanobot ledger.
- Optional read-only URL HEAD and Graphiti search-probe checkers are now
  implemented. ECS stat/hash remains guarded until an ECS-confirmed worker or
  MCP filesystem checker is running.
- Next, add a true Graphiti UUID CRUD lookup route and run ECS stat/hash in the
  ECS worker context.
- Store reviewable manifest deltas in git for refs that are files/docs only
  after scan receipts are reviewed.
- Emit Graphiti episodes when refs move, break, repair, or change hash, but do
  not let Episode provenance replace IdentityMap/RefIndex authority.

P4, Graphiti ontology upgrade:

- Add custom Graphiti entity/edge types for Parrot `Ref`, `Asset`,
  `ExternalLocator`, and `CanonicalObject` only after P1/P2 prove the data
  model.
- Keep custom types additive; do not make the initial system depend on a large
  ontology migration.

2026-05-17 M12 continuation:

- Web Graphiti subgraph search now exposes bounded strategy controls instead of
  a single one-shot query. `hybrid` keeps the classic natural-language search;
  `iterative_hybrid` performs real follow-up Graphiti searches from endpoint and
  fact terms found in prior results; `node_distance` passes an optional focal
  Graphiti UUID where the active Graphiti API supports it.
- L2-B remains a projection/import target, not a Graphiti replacement. The
  search result rows now carry `search_context`, `search_plan`, and raw envelope
  fields so the selected-hit import path can preserve Graphiti provenance and
  fact/entity UUIDs while still writing through L1.5.
- GOSLO Intent `query_memory` now uses the same Graphiti subgraph search path,
  so natural-language memory lookup can return Graphiti facts plus a bounded
  node/edge count instead of a detached 5-fact list.
- Live proof: the 7893 BFF was restarted with
  `PARROT_WEB_CONSOLE_GRAPHITI_URL=http://8.216.45.45:8790`; ECS 8790 accepted
  a non-dry-run `arknights_test` Episode write; 7893 then returned 9 hits,
  19 nodes, and 9 edges for a depth-2 Graphiti search; operator import admitted
 2 L1.5 nodes.
- Remaining limitation: the currently running ECS 8790 `/api/graphiti/search`
  shape may not yet return the full raw Graphiti model fields until the updated
  app-monitor code is deployed/restarted. The local/updated route preserves
  full raw envelopes when Graphiti returns them; M13 should add exact UUID CRUD
  lookup for entity/fact/episode inspection.

2026-05-17 M13 continuation:

- `/api/graphiti/lookup` now performs true Graphiti UUID CRUD lookup via
  official `get_by_uuid` helpers for entity nodes, episodic nodes, entity
  edges/facts, and episodic edges. For FalkorDB, lookup is explicitly scoped to
  the Graphiti `group_id` graph such as `arknights_test`; the default `parrot`
  graph is not assumed to contain partition data.
- Subgraph search now enriches each hit with raw Graphiti fact/source/target
  objects and episode UUID candidates before L1.5 import. This keeps L2-B as a
  projection/buff layer while preserving Graphiti's original temporal fact and
  provenance model.
- The lightweight 7893 Web BFF now proxies real Episode writes and
  operator-gated subgraph export to ECS 8790 when
  `PARROT_WEB_CONSOLE_GRAPHITI_URL` is configured. Browser code still never
  receives database credentials.
- ECS FalkorDB persistence was corrected: the Docker volume now mounts
  `/var/lib/falkordb/data`, the actual path used by the FalkorDB image, and
  Redis args are supplied through `REDIS_ARGS` with AOF/everysec/noeviction.
  This fixed the earlier false success mode where search worked in-process but
  data disappeared after restart.
- After FalkorDB restart, Graphiti hybrid search can return zero even when the
  persisted partition graph still contains facts. The Web adapter therefore
  includes a bounded read-only fallback over the Graphiti partition graph. It is
  not a replacement ontology; it returns Graphiti UUID/fact/source/target rows,
  then the same UUID lookup/enrichment path restores raw objects.

M13 live proof:

- 7893 wrote a non-dry-run Episode to ECS 8790 `arknights_test`.
- After real FalkorDB container restart and app-monitor restart, FalkorDB still
  reported `arknights_test` graph data and 7893 search returned 8 hits,
  13 nodes, and 8 edges for the persisted proof query.
- Enrichment found 16/16 requested Graphiti UUID objects.
- Operator export ran through ECS with `dry_run=false` and
  `operator_mode=true`, returning 2 raw envelopes, 2 Graphiti edge drafts, and
  5 IdentityRef drafts.

2026-05-17 M14 research deep dive:

This pass checked Parrot local skills plus current official Graphiti,
rustworkx, and FalkorDB docs. It is research/design hardening for the next
write-back slice; no production schema is ratified here.

Primary source anchors checked:

- Zep Graphiti Adding Episodes:
  `https://help.getzep.com/graphiti/core-concepts/adding-episodes`
- Zep Graphiti Searching:
  `https://help.getzep.com/graphiti/working-with-data/searching`
- Zep Graphiti CRUD Operations:
  `https://help.getzep.com/graphiti/working-with-data/crud-operations`
- Zep Graphiti Graph Namespacing:
  `https://help.getzep.com/graphiti/core-concepts/graph-namespacing`
- Zep Graphiti Custom Entity and Edge Types:
  `https://help.getzep.com/graphiti/core-concepts/custom-entity-and-edge-types/`
- Zep Graphiti MCP Server:
  `https://help.getzep.com/graphiti/getting-started/mcp-server`
- Zep Graphiti LLM Configuration:
  `https://help.getzep.com/graphiti/configuration/llm-configuration`
- rustworkx PyDiGraph reference:
  `https://www.rustworkx.org/stable/0.13/apiref/rustworkx.PyDiGraph.html`
- rustworkx introduction:
  `https://www.rustworkx.org/stable/0.12/tutorial/introduction.html`
- FalkorDB Docker persistence:
  `https://docs.falkordb.com/operations/durability/persistence.html`
- FalkorDB Docker/Compose operations:
  `https://docs.falkordb.com/operations/docker.html`
- Zep temporal graph paper:
  `https://blog.getzep.com/content/files/2025/01/ZEP__USING_KNOWLEDGE_GRAPHS_TO_POWER_LLM_AGENT_MEMORY_2025011700.pdf`

Key corrections and decisions:

- Graphiti remains the temporal/provenance owner. Episodes are ingestion-event
  source history, and entity/fact objects trace back to those episodes. L2-B
  must not flatten this into only an `EdgeKind`.
- `group_id` is a first-class namespace. In FalkorDB-backed live testing it is
  also an operational graph-scope concern, so lookup/search/export must carry
  partition explicitly and must not fall back to a default `parrot` graph.
- Graphiti search is real natural-language/hybrid retrieval and supports
  configurable search/reranking paths, including node-distance-style retrieval
  around a focal UUID where the active API supports it. Web should expose the
  strategy/depth/focal controls, but import must still preserve the raw
  Graphiti fact/node/episode envelope.
- Graphiti CRUD lookup by UUID is the exact proof path for entity/fact/episode
  inspection. A search probe is useful for discovery, but it is not UUID
  authority.
- Custom Graphiti entity/edge types are powerful but should be additive. The
  docs allow new custom types for new episodes while old nodes still work; to
  reclassify older data, the safe path is re-ingestion into a new graph. So
  Parrot should not start with a giant ontology migration.
- `EdgeKind` is a Web/L2-B view/filter/runtime class, not a mirror of every
  Graphiti predicate. The Graphiti predicate/name/fact/custom attributes stay
  in raw metadata; EdgeKind only answers "how can Web filter or L2-B route this
  edge?"
- rustworkx integer indices are graph-local handles only. Official docs state
  removed node/edge indices can leave holes and can be reused after removal.
  Therefore persistent identity is always external: `canonical_uuid`,
  `graphiti_uuid`, `l2b_uuid`, and maps such as `uuid -> rwx_idx` /
  `rwx_idx -> uuid` must be rebuildable.
- FalkorDB durability depends on the correct data mount and Redis args. The
  official Docker persistence path is `/var/lib/falkordb/data`; production
  compose examples use `REDIS_ARGS` for AOF, fsync cadence, memory limits, and
  auth. Our M13 ECS persistence fix matches this direction.

Ref/UUID architecture conclusion:

- A single Episode-only model is not enough for mutable external refs. Episodes
  are excellent audit/provenance records, but file paths, URLs, Obsidian note
  paths, ECS paths, photo paths, cloud ids, and git object refs need a mutable
  RefIndex layer with health, hash, version, move, and repair metadata.
- The next durable schema should be split into:
  `IdentityBinding`, `GraphitiRecordRef`, `ExternalRefRecord`, and
  `RefMoveEvent`.
- `IdentityBinding` owns equivalence across canonical UUID, L2-B UUID,
  Graphiti entity/fact/episode UUIDs, Obsidian UUIDs, App refs, and external
  object ids.
- `GraphitiRecordRef` is an immutable-ish pointer:
  `{partition, graphiti_uuid, graphiti_kind, raw_type_labels, last_lookup_at,
  lookup_status}`.
- `ExternalRefRecord` owns mutable locators:
  `{ref_uuid, owner_identity_uuid, locator_kind, locator_value,
  content_hash, git_ref, health, last_checked_at, repair_policy}`.
- `RefMoveEvent` records locator moves/renames/repairs and emits a Graphiti
  audit Episode, but it does not rewrite old Episode history.

Nanobot + git + MCP recommendation:

- This is the right control plane if roles stay separated. Nanobot proposes and
  runs bounded scans, MCP performs filesystem/cloud/remote checks, git records
  reviewable manifest deltas, and Web operator mode applies changes.
- Do not let Nanobot directly rewrite Graphiti, RefIndex, or ECS files without
  an operator-gated plan/apply receipt.
- For a moved ref, update RefIndex locator state and write a Graphiti audit
  Episode such as "ref X moved from A to B"; do not mutate historical source
  Episodes.
- Direct FalkorDB surgery remains an operator/debug escape hatch only, with
  backup, dry-run, and audit Episode. Normal paths should go through Graphiti
  API, RefIndex, or L2-B operator routes.

M14 implementation target:

- Design and implement reviewed write-back routes for IdentityBinding and
  ExternalRefRecord, starting with preview/apply and no silent mutation.
- Extend live smoke from "search/import/export works" to "a Graphiti result can
  be bound to refs, refs can be health-checked, and a reviewed locator update
  creates RefIndex state plus a Graphiti audit Episode."
- Add canaries after ECS restart: partition graph exists, exact UUID lookup
  works, natural-language search returns expected facts or uses the bounded
  read-only fallback with a warning, and imported L2-B objects preserve raw
  Graphiti envelopes.

2026-05-17 M14 first implementation checkpoint:

- Added `MemoryIdentityRefIndex.upsert_graphiti_ref_writeback()` as the first
  reviewed write-back helper. It binds a single Graphiti record pointer to one
  or more mutable external refs without writing Graphiti or moving files.
- Added Web routes:
  `POST /api/memory/identity-ref-index/graphiti-ref/draft` and
  `POST /api/memory/identity-ref-index/graphiti-ref/apply`.
- The route receipt explicitly names the four M14 concepts:
  `IdentityBinding`, `GraphitiRecordRef`, `ExternalRefRecord`, and
  `RefMoveEvent`.
- `GraphitiRecordRef` preserves `{partition, graphiti_uuid, graphiti_kind,
  raw_type_labels, lookup_status}` plus the raw Graphiti envelope in identity
  metadata.
- `ExternalRefRecord` writes through the existing RefIndex JSON shape and can
  carry locators, content hash, git commit, health, and `managed_by`. A
  Graphiti pointer by itself is not enough to create one; the write-back helper
  requires at least one real ref signal: locator, canonical URI, or content
  hash.
- `RefMoveEvent` is drafted when a ref gets a new locator. The first route
  records the locator state in RefIndex but does not move or delete files.
- The receipt includes a Graphiti audit Episode draft. By default it is not
  written; the next live canary should explicitly decide when to call
  `/api/graphiti/episode` through the existing 7893 -> ECS 8790 path.
- Verification: backend `py_compile` passed for `identity_ref_index.py`,
  `memory_ops.py`, `server.py`, and the Web route test module; full Web route
  tests report `82 passed`.
- Live canary: local updated Web BFF used
  `PARROT_WEB_CONSOLE_GRAPHITI_URL=http://8.216.45.45:8790`, searched ECS
  Graphiti partition `arknights_test` for `Amiya Chernobog`, received
  `4 hit(s), 9 node(s)`, selected real fact UUID
  `0ea2009c-402d-4332-81b4-31fa57e67688`, then applied a temporary
  IdentityRefIndex binding through the new Graphiti-ref apply route with
  `dry_run=false` / `operator_mode=true`. The temp index persisted
  `identity_count=1` and `ref_count=1`; direct Graphiti and L2-B writes stayed
  false, and the audit Episode stayed `draft_only`.
- Audit write canary: enabling `write_graphiti_audit_episode=true` performs a
  second explicit write after RefIndex persistence. The default 60s remote
  proxy timeout produced a clean timeout receipt and no Graphiti write; with
  `PARROT_WEB_CONSOLE_GRAPHITI_TIMEOUT_S=240`, the same route wrote the audit
  Episode through 7893 -> ECS 8790. The receipt reported
  `direct_graphiti_write=true`, `graphiti_audit_episode_written=true`, and
  mutation scope `memory_identity_ref_index_json_and_graphiti_audit_episode`.
- UI surfacing checkpoint: the existing 7893 React Source Board now exposes a
  Graphiti Ref Write-back panel inside the Export plan. The operator can choose
  a generated Graphiti fact/entity/episode Ref draft, edit Ref ID/kind/locator,
  preview the M14 write-back receipt, and explicitly opt into the audit Episode
  write during apply. `npm run typecheck` and `npm run build` passed, the built
  dist was served by restarted 7893, and runtime smoke confirmed real ECS
  `arknights_test` search plus search -> export-draft -> identity_ref_drafts ->
  Graphiti-ref draft.
- Bugfix checkpoint: empty locator write-back no longer produces a fake
  `ExternalRefRecord` with `locators=[]`. The backend filters empty
  `external_refs`, the UI omits an external ref when the locator field is
  blank, and the 7893 runtime smoke confirmed
  `external_payloads=0`, `external_records=0`, `move_events=0` while still
  allowing the GraphitiRecordRef identity binding.

2026-05-17 M15 SearchConfig recipe checkpoint:

- Web Graphiti search now distinguishes "how to expand locally" from "which
  Graphiti retrieval recipe to ask for." `/api/graphiti/search` and
  `/api/graphiti/subgraph/search` accept `search_recipe`, `node_labels`, and
  `edge_types`.
- When the local Graphiti object exposes low-level `_search` or `search_`, the
  adapter loads Graphiti SearchConfig recipes and calls the low-level method
  with `query=...`, `group_id=...`, `config=...`, and `search_filter=...`.
  Supported recipe aliases cover combined, edge, node, and community retrieval
  families: RRF, MMR, cross-encoder, node-distance, and episode-mentions where
  Graphiti exposes that recipe.
- The route receipt includes a `search_config` audit object with `mode`,
  requested recipe, mapped recipe constant, low-level availability, and fallback
  reason if low-level search is unavailable or fails. This keeps live Web tests
  honest instead of silently pretending a recipe ran.
- Node-label and edge-type filters are passed as Graphiti SearchFilters when the
  installed Graphiti version supports them. They are filter/view controls for
  retrieval and inspection; they are not a request to predefine one local
  `EdgeKind` for every Graphiti predicate.
- The 7893 Graphiti Source Board now exposes separate local expansion Strategy
  and Graphiti Recipe selectors plus Node labels / Edge types inputs. This lets
  operators test Graphiti's own retrieval behavior from Web while still using
  `iterative_hybrid` for multi-hop expansion before L1.5/L2-B import.
- Subgraph preview now upgrades endpoint placeholder nodes when the same UUID
  is later returned as a full Graphiti entity hit, so L2-B preview can preserve
  richer raw entity payloads without discarding the fact-edge context.
- Verification: backend `py_compile` passed for Graphiti/Web/test files, full
  Web route tests report `83 passed`, and frontend `npm run typecheck` /
  `npm run build` passed. A focused Web regression proves `combined_rrf`,
  `node_labels`, and `edge_types` reach `_search(**kwargs)` with partition
  `group_id`, bounded config limit, and filter payload. The response records
  `search_config.mode="_search"` and recipe `COMBINED_HYBRID_SEARCH_RRF`.
- 7893 runtime smoke: restarted the existing sidecar Web Console with ECS
  Graphiti proxy and 240s timeout. The built frontend contains the separate
  Strategy / Recipe / label / edge-type controls, and a
  `strategy=iterative_hybrid + search_recipe=combined_rrf + Entity/CrisisFact`
  route call against `arknights_test` returned `3 hit(s), 7 node(s), 3 edge(s)`.
  Because ECS 8790 is not yet running this M15 adapter, that live receipt did
  not include low-level `_search` mode; deploy the M15 app-monitor code before
  using live receipts as SearchConfig proof.
- M16 follow-up completed the first bundle preservation layer: Graphiti
  subgraph search, export draft, operator export, and import-plan receipts now
  carry `graphiti_bundle` with raw envelopes, fact/entity/episode/community
  sections, exact lookup payloads, SearchConfig/search-plan data, preview edge
  drafts, IdentityRef drafts, and L2-B import overlay. Remaining work is UI
  section rendering plus ECS/app-monitor deployment and live canary proof.
- M17 follow-up completed the first UI/read-model layer: the Source Board now
  renders bundle section counts, search/lookup summary, projection policy,
  import overlay, and sample raw rows. Live 7893 canary proves real ECS
  Graphiti data enters the local bundle path; ECS adapter deployment remains
  the blocker for remote `_search` mode proof.
- M18 follow-up removed that ECS blocker. App-monitor now forwards
  `search_recipe`, `node_labels`, and `edge_types`, exposes remote
  `/api/graphiti/subgraph/import-plan`, and runs the same
  SearchConfig/bundle adapter on ECS 8790. Remote canaries against
  `arknights_test / Amiya Chernobog` returned `search_config.mode="_search"`,
  `fallback=false`, bundle counts
  `facts=3/entities=4/episodes=3/communities=0`, UUID lookup `10/10`, and
  import overlay destination `isolated_compartment`. This proves the
  Graphiti-owned raw bundle can be fetched directly from ECS before any L2-B
  projection or RustWorkX transform.
- M19 follow-up adds the first RustWorkX/L2-B projection over that remote
  bundle. Import-plan now embeds `l2b_transform_preview` and the bundle overlay
  includes `transform_preview`. Remote 8790 and local 7893 canaries both prove
  the path against true Graphiti data: `_search`, first fact UUID
  `0ea2009c-402d-4332-81b4-31fa57e67688`, bundle counts
  `facts=3/entities=4/episodes=3/communities=0`, projection counts
  `l2b_nodes=3`, `l2b_edges=1`, `episode_links=2`, and RustWorkX
  `nodes=3/edges=3`. The policy still blocks direct L2-B writes and treats
  rustworkx indices as ephemeral preview handles.

## 2026-05-17 M20 Review and Research Gate

This gate reviews whether the M12-M19 Graphiti/L2-B path still matches the
original requirement: one-click import should run a real Graphiti search,
retrieve a bounded multi-hop bundle with complete Graphiti information, preserve
Graphiti's own result/fact/entity/episode data, and add only an L1.5/L2-B
projection layer for fast review, buffering, and graph algorithms.

Review verdict:

- The current path matches the search/import-preview part of the requirement.
  M18/M19 proved true ECS Graphiti `_search(SearchConfig)` through remote 8790
  and local 7893 passthrough, with raw bundle sections and import-plan
  projection receipts.
- It is not yet complete for durable materialization. `l2b_transform_preview`
  is a preview-only consumer. Final apply must still bind Graphiti UUIDs through
  `IdentityBinding` and operator routes before persisting L2-B nodes/edges.
- The current Node/Edge split is not considered drift. It is an intentional
  projection layer: L2-B Node/Edge kinds exist for Web filtering, spatial/view
  grouping, RustWorkX topology, and future L2-A/L2-B algorithms. They must not
  mirror every Graphiti predicate as a local enum.
- The possible drift is the temporary preview UUID shape
  `graphiti:{partition}:{kind}:{uuid}`. That is acceptable for receipts, but it
  must not become the canonical L2-B UUID without passing through
  `IdentityBinding`.

Node/Edge audit:

- Graphiti remains the semantic and temporal source of truth. Its UUID, labels,
  fact text, source/target UUIDs, valid-time metadata, raw envelope, and episode
  provenance stay inside `graphiti_bundle`.
- L2-B preview nodes are pointer/index nodes, not a copied Graphiti ontology.
  They carry `graphiti_uuid`, `graphiti_kind`, `partition`, raw labels, and raw
  payload metadata so the original Graphiti data can be recovered.
- L2-B preview edges such as `graphiti_fact` and episode support links are
  algorithm/view edges. Graphiti's extracted relationship name/fact is payload
  metadata, not a hard-coded local `EdgeKind`.
- Edge categories should be used to filter views and choose algorithms
  (`mentions`, `graphiti_fact`, `spatial`, `cross_source`, `ref_support`,
  etc.). They should not be used as a brittle one-to-one translation table for
  every Graphiti edge type.

UUID and Ref management conclusion:

- Stable identity is the canonical UUID in `IdentityBinding`. RustWorkX indices
  are runtime handles only; `rwx_idx_policy=ephemeral_do_not_persist` is the
  correct policy and should stay visible in receipts.
- `GraphitiRecordRef` owns immutable-ish Graphiti pointers:
  `{partition, graphiti_uuid, graphiti_kind, raw_type_labels, lookup_status}`.
- `ExternalRefRecord` owns mutable locators: Obsidian paths, ECS paths, URLs,
  photo paths, large-file paths, cloud ids, content hashes, and git refs.
- `RefMoveEvent` owns approved moves/repairs. It can emit a Graphiti audit
  Episode but should not rewrite the original source Episode.
- Episode-only storage is insufficient for mutable refs. Graphiti Episodes are
  excellent provenance/audit records, but current locator truth needs a
  RefIndex/database layer with health, hash, move, and repair state.

Database / Nanobot / MCP / git operating model:

- Normal Graphiti writes should go through Graphiti APIs or the existing
  7893 -> ECS 8790 route. Direct FalkorDB surgery is an operator/debug escape
  hatch only, with backup, dry-run, and audit receipt.
- Ref writes should go through IdentityRefIndex routes first. The current
  file-backed JSON index is acceptable as a Web/BFF prototype, but a later
  DB-backed index is needed for transactionality, concurrent writers, and
  larger ref sets.
- Nanobot is the background executor for bounded scans/checks. It should not be
  the hidden source of truth and should not directly mutate Graphiti, L2-B, or
  files without an operator-reviewed plan/apply receipt.
- MCP is the checker/tool boundary for external systems such as filesystem,
  Obsidian, Google, URLs, ECS-local probes, and future cloud providers.
- git is useful for reviewable small manifest changes and Obsidian/source-pack
  deltas. It is not the database; it should record/referee text manifests and
  config, while RefIndex stores current locator state.

Version locks and live locations:

- `pyproject.toml` pins `graphiti-core[falkordb,google-genai]>=0.28,<0.29` and
  `rustworkx>=0.15,<1.0`.
- `uv.lock` / ECS currently resolve `graphiti-core==0.28.2`,
  `rustworkx==0.17.1`, `falkordb==1.6.0`, `neo4j==6.1.0`, and FastAPI
  `0.136.1`.
- Local 7893 does not need local Graphiti packages when it is configured as a
  BFF proxy to ECS 8790. True Graphiti tests should set
  `PARROT_WEB_CONSOLE_GRAPHITI_URL=http://8.216.45.45:8790` unless local
  Graphiti dependencies are installed.
- Official version/document anchors recorded for future implementation gates:
  - Graphiti overview:
    https://help.getzep.com/graphiti/getting-started/overview
  - Graphiti search and SearchConfig recipes:
    https://help.getzep.com/graphiti/working-with-data/searching
  - Graphiti Episodes/provenance:
    https://help.getzep.com/graphiti/core-concepts/adding-episodes
  - Graphiti graph namespacing / `group_id`:
    https://help.getzep.com/graphiti/core-concepts/graph-namespacing
  - Graphiti custom entity/edge filters:
    https://help.getzep.com/graphiti/core-concepts/custom-entity-and-edge-types/
  - Graphiti 0.28.2 PyPI provenance:
    https://pypi.org/project/graphiti-core/0.28.2/
  - RustWorkX 0.17.1 docs:
    https://www.rustworkx.org/
  - RustWorkX VF2 mapping:
    https://www.rustworkx.org/apiref/rustworkx.digraph_vf2_mapping.html

Research refs to keep attached to L2-B/RustWorkX design:

- HippoRAG, NeurIPS 2024 / arXiv:2405.14831:
  KG + Personalized PageRank supports multi-hop retrieval over long-term
  memory. Parrot use: seed Graphiti/L2-B retrieval from query/focal UUID, then
  bounded PPR/spreading activation over pointer nodes.
- AriGraph, arXiv:2407.04363:
  agent memory graph integrates episodic and semantic memories. Parrot use:
  keep Graphiti Episodes/provenance plus L2-B semantic/pointer projection
  rather than flattening everything into one node type.
- Graph Attention Networks, arXiv:1710.10903:
  attention weights over local neighborhoods. Parrot use: local activation
  scoring should stay neighborhood/ego-subgraph based by default.
- DySAT, arXiv:1812.09430:
  structural and temporal self-attention for dynamic graphs. Parrot use:
  future L2-B attention should include temporal evolution instead of only
  static degree/centrality.
- GraphGPS, arXiv:2205.12454:
  combines local message passing with global attention and structural
  encodings. Parrot use: treat global attention as an explicit offline/preview
  mode, not the default realtime L2-B operation.
- AGCN, arXiv:2509.15024:
  warns that GNNs can over-localize while Transformers over-globalize. Parrot
  use: keep bounded ego-subgraphs, selected global bridges, and receipt-visible
  depth/strategy choices.
- rustworkx JOSS/arXiv:2110.15221:
  supports using RustWorkX as the high-performance topology engine while Python
  payloads/UUIDs remain the semantic and persistence layer.

Implementation constraints for M20+:

- Materialization must be operator-gated and receipt-first.
- The apply path should consume `graphiti_bundle`, preserve raw envelopes, bind
  endpoint UUIDs through IdentityRefIndex, then create L2-B nodes/edges only
  when the canonical UUID decision is explicit.
- Ref sync should update `ExternalRefRecord` current locator state and emit
  Graphiti audit Episodes for history; it should not edit old Episodes.
- Any multi-hop or "subconscious" graph transform should declare seed nodes,
  depth/hop bound, recipe, filters, ranking method, and whether it is online
  preview, offline analysis, or durable apply.
