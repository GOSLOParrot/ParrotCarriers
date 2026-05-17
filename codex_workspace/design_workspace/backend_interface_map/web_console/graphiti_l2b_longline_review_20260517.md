# Web Console Graphiti / L2-B Longline Review Ledger (2026-05-17)

Owner: Web Console Graphiti/L2-B implementation line
Status: recorded_review
Scope: Web Console 7893, ECS app-monitor 8790, Graphiti/FalkorDB, L1.5/L2-B, IdentityRefIndex, RustWorkX projection, Ref/UUID design

## Purpose

This file is the quick reread ledger for the long Graphiti / L2-B work line.
Before continuing TODO work, read this file together with:

- `codex_workspace/design_workspace/backend_interface_map/web_console/graphiti_l2b_ref_identity_design_20260517.md`
- `codex_workspace/design_workspace/backend_interface_map/web_console/_tmp/graphiti_l2b_ref_identity_workplan_20260517.md`
- `codex_workspace/design_workspace/backend_interface_map/web_console/_tmp/l2b_subgraph_tools_workplan_20260517.md`

The original requirement was not "make a fake dry-run UI." The target was:

- Web Console must connect to the real ECS Graphiti service.
- Graphiti natural-language search and configurable search strategies must be testable from Web.
- One-click subgraph import must be able to take a real Graphiti search result, preserve the full Graphiti result/fact/entity/episode information, and then add only a lightweight L1.5/L2-B buff/projection layer.
- L2-B must not destroy Graphiti data or pretend RustWorkX indices are durable identity.
- UUID and Ref handling must support Graphiti, L2-B, Obsidian, ECS paths, photos, URLs, large files, Google/external provider ids, and later A10/App bindings.

## Current Verdict

The Graphiti Web Console line is now past "installation and sketch" and has a real end-to-end path:

- 7893 can proxy to ECS 8790 for Graphiti status/search.
- Graphiti search can return real partition data from ECS/FalkorDB.
- Search/export/import-plan receipts preserve a `graphiti_bundle` instead of flattening Graphiti into local display strings.
- Web Console has an operator-gated `Graphiti -> L2-B` materialization route.
- Real materialization writes deterministic Graphiti pointer nodes/edges into the L2-B runtime graph, preserves raw Graphiti metadata, and writes IdentityRefIndex payloads by default.
- L2-B context queries can read back the materialized pointer subgraph.

The line is not finished as a full memory/ref operating system:

- Durable Ref lifecycle management is still a prototype.
- IdentityRefIndex is still file-backed, not a DB-backed concurrent authority.
- Nanobot + MCP + git ref scan/repair is designed and partially routed, but not a complete autonomous file manager.
- L2-B graph transform/recomposition algorithms are still first slices, not a mature RustWorkX recipe library.
- Google Calendar/OAuth is a separate integration line and should not be counted as completed by this Graphiti work.

## Evidence Snapshot

Recent relevant commits on `master`:

| Commit | Meaning |
|---|---|
| `76c2472` | Added `/api/graphiti/subgraph/materialize-l2b` and backend Graphiti bundle to L2-B materialization. |
| `15f0cd1` | Fixed materialized node fact cleaning so `None` does not become a user-visible fact string. |
| `1cd7db2` | Routed Web Console Graphiti imports to the L2-B materialization route instead of the older export route. |
| `64b78ea` | Added visible Web UI materialization receipt/results panel. |
| `0feea9b` | Fixed bundle `selected_count` so episode-only/entity-only materialization previews are not counted as empty. |

Local verification previously completed on this line:

- Full `tests/test_web_console/test_web_console_server.py`: `88 passed`.
- Focused Graphiti/L2-B route tests passed for import-plan, materialization, operator gating, context query, episode-only bundle preservation, and monitor route exposure.
- `npm run typecheck` passed.
- `npm run build` passed, with Vite chunk-size warning only.
- `py_compile src/parrot/web_console/memory_ops.py` passed.

Live/runtime verification previously completed:

- 7893 -> ECS 8790 `/api/graphiti/status` succeeded with Graphiti installed and remote proxy enabled.
- `noble_etiquette` partition existed after the user's import.
- A real `noble_etiquette` query returned hits/nodes from ECS Graphiti.
- Real operator materialization smoke wrote Graphiti pointer nodes/edges to L2-B with `direct_l2b_write=true`.
- Reapplying the same materialization skipped duplicate edges, proving the dedupe path.
- `/api/l2b/subgraphs/context` read back the imported context.

Light runtime probe on 2026-05-17 during this review:

- `GET http://127.0.0.1:7893/api/graphiti/status`
  - success: true
  - partitions included: `goslo`, `maid`, `scene`, `user`, `arknights_test`, `noble_etiquette`
  - remote proxy: enabled
  - base URL: `http://8.216.45.45:8790`
- `POST http://127.0.0.1:7893/api/graphiti/subgraph/search`
  - query: `formal introductions rank etiquette`
  - partition: `noble_etiquette`
  - result: `2 hit(s), 5 node(s)`
  - returned real Graphiti fact/entity/episode raw payloads, including fact UUIDs, entity endpoint UUIDs, episode UUIDs, `valid_at`, and source description.
  - note: this specific noble query used the partition fact-scan fallback in the returned search context. It proves real ECS/FalkorDB data access, but it is not itself proof that the low-level Graphiti `SearchConfig` recipe path ran for that query.

## Requirement Compliance Review

### Real ECS Connection

Status: mostly complete for Graphiti.

The current 7893 Web Console can operate as a BFF/proxy to ECS 8790 through:

- `PARROT_WEB_CONSOLE_GRAPHITI_URL`
- `PARROT_GRAPHITI_REMOTE_URL`
- timeout envs such as `PARROT_WEB_CONSOLE_GRAPHITI_TIMEOUT_S`

The status route currently reports local `graphiti_core` missing but remote proxy enabled. That is acceptable for the desktop/Web BFF mode: true Graphiti work is happening on ECS.

Gap:

- ECS release/restart must remain part of code work. A local build alone can leave 7893/8790 running older code and make tests misleading.

### Real Graphiti Search

Status: complete for real data access; SearchConfig proof exists but should be re-smoked when search recipes are changed.

Implemented capabilities:

- `/api/graphiti/status`
- `/api/graphiti/search`
- `/api/graphiti/subgraph/search`
- search partition/group selection
- natural-language query
- bounded subgraph expansion strategy
- search recipe fields such as `search_recipe`, `node_labels`, and `edge_types`
- bundle-level preservation of search plan/search config evidence when available

Important nuance:

- Graphiti itself owns semantic/temporal/fact search.
- Web/L2-B local strategies are expansion/projection strategies, not a replacement for Graphiti search.
- If a route falls back to FalkorDB partition fact scan, that is still real data access, but the receipt should not be described as a low-level Graphiti `SearchConfig` recipe run.

### One-Click Subgraph Import

Status: first real implementation complete.

Implemented path:

```text
Graphiti search
  -> graphiti_bundle
  -> L2-B transform preview
  -> operator-gated materialize-l2b
  -> L2-B pointer nodes/edges
  -> IdentityRefIndex payloads
  -> /api/l2b/subgraphs/context readback
```

The route is:

- `POST /api/graphiti/subgraph/materialize-l2b`

Apply is intentionally gated:

- Preview: `dry_run=true` or missing operator mode means no mutation.
- Real write: `dry_run=false` and `operator_mode=true`.

The implementation writes L2-B only. It explicitly does not write Graphiti/FalkorDB.

### Full Graphiti Information Preservation

Status: aligned with the requirement.

`graphiti_bundle` keeps the Graphiti-owned information instead of over-converting it:

- raw selected hit envelopes
- facts/edges
- source and target entities
- episode pointers and lookup rows
- communities when present
- search/query/strategy metadata
- lookup summaries
- raw payloads in metadata
- L2-B import overlay and projection policy

Materialized L2-B nodes/edges preserve raw Graphiti payloads in `meta` / `source_meta`. This matches the rule: L2-B is a fast working graph and buff layer, not a lossy replacement database.

### L2-B / RustWorkX Role

Status: correct direction, early algorithm layer.

The current L2-B materialization creates deterministic Graphiti pointer UUIDs:

```text
graphiti:{partition}:{kind}:{graphiti_uuid}
```

This is good as a pointer/projection id, but must not become the only canonical identity model.

RustWorkX indices remain runtime handles only. Persistent identity must be:

- canonical UUID in IdentityRefIndex / future IdentityBinding
- Graphiti UUID
- L2-B UUID
- provider ids and external Ref ids
- rebuildable `uuid -> rwx_idx` maps at runtime

### Node And Edge Design

Status: not drift; this is an intentional projection layer.

Graphiti already extracts relations/facts/edges. L2-B Edge categories should not mirror every Graphiti predicate one by one.

L2-B Node/Edge categories exist for:

- Web filtering
- spatial/view grouping
- operator inspection
- L2-A/L2-B algorithm routing
- RustWorkX graph transforms
- ref/identity bridge overlays

Graphiti's exact predicate/fact/relation text stays in raw metadata. Local `EdgeKind` is a coarse view/algorithm channel.

### UUID Binding

Status: useful prototype, not final authority.

What exists:

- L2-B nodes have UUID fields.
- Graphiti UUIDs are preserved on materialized pointers.
- deterministic Graphiti pointer UUIDs are generated.
- IdentityRefIndex can bind Graphiti pointers, L2-B UUIDs, Obsidian UUIDs, provider keys, and ref ids.
- merge/conflict receipts exist.

What remains:

- DB-backed identity storage.
- stronger concurrency semantics.
- a first-class `IdentityBinding` model promoted beyond Web-only JSON.
- operator UI for resolving collisions.
- App/A10 shared DTO promotion.

### Ref Management

Status: designed and partially prototyped; not complete.

Correct split:

- Graphiti Episodes: history/provenance/audit.
- Graphiti facts/entities: semantic temporal graph.
- IdentityRefIndex / future RefIndex: current mutable locator truth.
- Nanobot: executor for scans, health checks, moves, repairs, imports.
- MCP: boundary for external systems.
- git: reviewable small manifest/config/source-text changes, not the runtime database.

Refs that need this model:

- Obsidian documents and UUIDs
- local paths
- ECS paths
- photo paths
- URLs
- large-file paths
- Google/external provider ids
- content hashes
- git refs

Do not rely on "fixed path forever." Moves should update RefIndex/ExternalRefRecord and emit a Graphiti audit Episode. Historical source Episodes should not be rewritten.

### Google Calendar / OAuth

Status: separate line; do not count as closed here.

The user completed a local OAuth authorization and generated credential files for Google Workspace MCP/Nanobot use. The earlier conclusion remains:

- OAuth 2.0 is the auth family already being used.
- Google Calendar itself does not inherently require Redis.
- The current Web Console should test through ECS/Nanobot/Google official API, not fake data.
- Redis may still matter for Nanobot/Scheduler/result-ledger paths, but that is an orchestration detail, not a Google API requirement.

This Graphiti/L2-B line did not finish a full live Google Calendar read path. Keep that as a separate TODO.

## ECS Release Workflow Fixed In Practice

When code changes affect Web Console, Graphiti, app-monitor, L2-B, or ECS runtime, the workflow should be:

1. Audit local changes and avoid staging unrelated dirty files.
2. Run focused tests and frontend build/typecheck as relevant.
3. Commit and push the exact scope.
4. Run the ECS release script, usually:

```powershell
infra/ecs-release.ps1 -Branch master -AllowLocalDirty
```

5. Verify remote services restart and are active:

- `parrot-orchestrator`
- `parrot-app-monitor`
- `parrot-scheduler`
- `parrot-maid`
- `parrot-goslo-chat`
- `parrot-brain`

6. Smoke the actual routes through 7893/8790, not only local dry-runs.

Known release caveat:

- `redis-cli` is missing on ECS, so the release smoke can skip Redis verification. This warning should not be mistaken for Graphiti route failure, but Redis smoke coverage is incomplete until the CLI/checker is fixed.

## Research And Design Anchors

Graphiti anchors:

- Temporal context graph: entities, facts/relationships, episodes, provenance, temporal validity.
- `group_id` / partitioning is the correct namespace boundary.
- `add_episode` supports custom entity and edge types.
- Search can combine semantic, keyword/BM25, graph traversal, reranking, and configurable recipes depending on installed version/API exposure.

RustWorkX anchors:

- RustWorkX is the high-performance in-memory topology engine.
- `PyDiGraph` indices are runtime handles, not durable business ids.
- Use payloads/metadata for semantic state, and external UUID maps for durable identity.
- Use bounded ego-subgraphs, PPR/spreading activation, VF2 with limits, and offline health metrics carefully.

Memory/graph research anchors already recorded in the design doc:

- HippoRAG: KG + Personalized PageRank for multi-hop memory retrieval.
- AriGraph: episodic + semantic memory graph.
- GAT / DySAT / GraphGPS / AGCN: local attention, temporal dynamics, local/global balance.
- rustworkx paper/docs: performance/topology layer.

## Remaining TODO Before Next Implementation

### TODO Before

- Re-read this ledger and `graphiti_l2b_ref_identity_design_20260517.md`.
- Check current git status and avoid unrelated dirty files.
- Verify 7893 status and whether it is local or ECS proxy.
- Run one real `/api/graphiti/subgraph/search` against the target partition.
- If testing SearchConfig recipes, check receipt/search config evidence, not just hit count.
- If testing import, decide explicitly: preview only or operator materialization.

### TODO During

- Continue consuming `graphiti_bundle` as the source unit for imports.
- Preserve raw Graphiti payloads and UUIDs on every projection/materialization.
- Keep Graphiti writes separate from L2-B writes.
- Keep materialization operator-gated.
- Add richer UI for selecting bundle sections, hop/depth, recipe, endpoint resolution, and target destination.
- Build a small RustWorkX recipe layer for bounded ego-subgraph, spreading activation/PPR, and transform previews.
- Build Nanobot + MCP + git Ref scan/repair as a plan/apply workflow through IdentityRefIndex.

### TODO After

- Run focused backend tests.
- Run full Web route tests if shared behavior changed.
- Run `npm run typecheck` and `npm run build` for UI changes.
- Commit/push only the intended scope.
- ECS release/restart if runtime code changed.
- Smoke through 7893/8790:
  - status
  - search
  - import-plan/materialize preview
  - real materialize if appropriate
  - L2-B context readback
  - duplicate reapply behavior

## Upgrade Recommendations

Highest priority:

- Promote IdentityRefIndex from Web file-backed prototype toward a durable DB-backed `IdentityBinding` / `GraphitiRecordRef` / `ExternalRefRecord` / `RefMoveEvent` model.
- Finish Nanobot + MCP + git ref scan/repair with explicit receipts and Graphiti audit Episodes.
- Add Web operator UI for identity conflicts and ref health.
- Add materialization receipts that clearly show whether search was Graphiti low-level SearchConfig, fallback partition scan, or another mode.

Next priority:

- Create a RustWorkX transform recipe module instead of keeping projection logic as ad hoc route helper code.
- Add subgraph import presets:
  - search-only preview
  - entity neighborhood
  - fact endpoints + episodes
  - ref-support import
  - bounded multi-hop import
  - offline analysis / no mutation
- Add persistence/rebuild strategy for L2-B runtime graph after service restart.
- Add ECS smoke for static/dist version and route version so the operator can see whether 7893 and 8790 are running the expected commit.

Keep separate:

- Google Calendar live API integration.
- Unity/App/A10 UUID display and binding.
- Large file/photo/Obsidian file lifecycle automation.

## Final Review Note

The long line has moved from "Graphiti installed and roughly designed" to "Graphiti can be queried through Web, real Graphiti data can be bundled, previewed, materialized into L2-B pointer topology, and read back." That satisfies the first practical milestone.

The next milestone is not more dry-run UI. It is durable identity/ref management and richer controlled graph transforms, while keeping Graphiti as the source temporal graph and L2-B as the fast RustWorkX working layer.
