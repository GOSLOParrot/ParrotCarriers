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
  not pretend Graphiti fact edges are already persisted L2-B edges.
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
- Graphiti can be imported toward L2-B, but today it is mostly
  Observation-based L1.5 admission plus edge drafts. Full node/edge materialized
  import needs `GraphitiResolver` plus durable IdentityMap.
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
