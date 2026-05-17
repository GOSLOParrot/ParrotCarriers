# Graphiti / L2-B / Ref Identity Workplan (2026-05-17)

Status: temporary-active
Owner: Web Console chat
Parent docs:

- `../graphiti_l2b_ref_identity_design_20260517.md`
- `../graphiti_management_business_flow_20260513.md`
- `../memory_graph_workspace_business_flow_20260513.md`
- `../../core_interface_candidate_queue_20260513.md`

This is the temporary workbench for finishing CORE-015 and the next
Graphiti-to-L2-B materialization slice. Durable decisions must be promoted back
to the parent docs above; this file is allowed to be detailed and operational.

## Target

Build a real, testable path from Graphiti search/import and external refs into
L2-B without losing information:

1. Graphiti remains the temporal memory/provenance graph.
2. L2-B remains the rustworkx runtime projection with stable L2-B UUIDs.
3. `MemoryIdentityRefIndex` owns canonical UUID equivalence and mutable
   external locators.
4. Ref files/URLs/photos/ECS paths are managed through RefIndex health and
   repair workflows, not by assuming paths never move.
5. Graphiti fact edges can become L2-B edges only after endpoint UUIDs resolve.
6. Web Console can test each step with receipts, preview/apply split, and
   no hidden App DTO pollution.

## Working Index

| Area | File / route | Role |
|:--|:--|:--|
| Durable design | `../graphiti_l2b_ref_identity_design_20260517.md` | Decision record and phased architecture. |
| Current temp workbench | `_tmp/graphiti_l2b_ref_identity_workplan_20260517.md` | Questionnaire, TODO-before/during/after gates, and step-by-step execution ledger. |
| Candidate queue | `../../core_interface_candidate_queue_20260513.md` | Shared CORE-015 candidate fields and promotion notes. |
| Backend skeleton | `src/parrot/dsg/identity_ref_index.py` | File-backed IdentityRecord/RefRecord prototype. |
| Web BFF routes | `/api/memory/identity-ref-index*` | Snapshot, draft, and operator apply receipts. |
| Graphiti source routes | `/api/graphiti/subgraph/*` | Search, export draft, import plan, and L1.5 export. |
| Current tests | `tests/test_web_console/test_web_console_server.py` | Route and persistence regression coverage. |

## Research Questionnaire Index

Use these questions before each implementation slice. Answers should be short,
file-backed, and linked to the code or docs that prove them.

| ID | Question | Proof needed | Current answer |
|:--|:--|:--|:--|
| Q0 | What exact user-visible goal is this slice proving? | One sentence plus route/UI/test signal. | Prove durable UUID/ref binding before Graphiti edge materialization. |
| Q1 | Which system owns this truth: Graphiti, L2-B, IdentityMap, RefIndex, L1.5, nanobot, git, or App? | Ownership table and write path. | IdentityMap owns UUID equivalence; RefIndex owns locators; Graphiti owns provenance/facts. |
| Q2 | What local code already does this partially? | `rg`/file references. | `RefTable`, `RefBinding`, `L15Pool`, `L2BGraph`, Graphiti Web routes. |
| Q3 | Which official or skill docs are relevant and current? | Source list. | Graphiti docs, rustworkx docs, Parrot Graphiti/RustWorkX/L2-B skills. |
| Q4 | What data must be preserved raw? | Field list and sample payload. | Done for M3: export-draft/import-plan receipts now carry `graphiti_raw_envelopes`, endpoint/episode UUIDs, raw labels/custom attrs, and CORE-015 `identity_ref_drafts`. |
| Q5 | What is the canonical identity rule? | Merge/conflict policy. | Done for M2: one existing signal merges; explicit or multi-canonical overlap marks `conflicted` and preserves evidence without auto-rebinding existing records. |
| Q6 | What makes a Ref healthy, stale, moved, or broken? | Verifier matrix. | Done for M1: local paths are checked directly; URLs/ECS/remote locators stay `unknown`; supplied Graphiti/Obsidian UUID maps are testable. |
| Q7 | How does a Graphiti edge become an L2-B edge? | Resolver flow and preconditions. | Done for M5 backend: `resolve-graphiti` previews endpoint state; `apply-graphiti-edge` re-resolves, then writes only when source/target are `resolved_l2b` and the operator gate is open. |
| Q8 | Which EdgeKind classes are filters/views, not relation ontology? | EdgeKind/view mapping. | Coarse view classes only; raw relation remains metadata. |
| Q9 | What should nanobot/git/MCP do here? | Workflow boundary. | Done for M7: Web drafts a `ref_scan` nanobot contract; git stores reviewable manifests; MCP checks locators; Parrot index remains authority. |
| Q10 | What is deliberately not implemented in this slice? | Non-goal list. | No direct FalkorDB surgery; no Graphiti ontology migration; no App DTO promotion. |
| Q11 | What is the smallest route/API proof? | Route contract and tests. | Snapshot/draft/apply/verify/resolve-graphiti/apply-graphiti-edge exist; Graphiti export/import plan emits raw envelopes; materialized edge apply is backend-tested. |
| Q12 | What is the Web UI proof? | Visible control and receipt. | Done through M7: existing Graphiti Source Board loads IdentityIndex, verifies refs, resolves/materializes Graphiti edges, and now drafts a Ref Scan Plan receipt. |
| Q13 | What needs ECS/live smoke? | Command or route plus expected result. | Done for M12: 7893 was restarted with `PARROT_WEB_CONSOLE_GRAPHITI_URL=http://8.216.45.45:8790`; ECS 8790 accepted a non-dry-run Graphiti Episode write into `arknights_test`; 7893 `/api/graphiti/subgraph/search` then returned 9 hits / 19 nodes / 9 edges with depth-2 iterative Graphiti searches; local operator import admitted 2 L1.5 observations. |
| Q14 | What docs must be updated after the slice? | TODO/Web README/business/core candidate list. | This workbench plus parent docs and TODO board. |

## TODO-Before Gate

No implementation slice starts until these are checked.

| Gate | Status | Task | Exit signal |
|:--|:--|:--|:--|
| B0 | done | Load Parrot skill bridge and relevant Graphiti/RustWorkX/L2-B skill context. | Skill source read or already summarized in current working docs. |
| B1 | done | Re-read current durable design and current code ownership. | `graphiti_l2b_ref_identity_design_20260517.md` plus `identity_ref_index.py` referenced. |
| B2 | done | Define non-goals for this phase. | No direct DB surgery, no App DTO promotion, no Graphiti ontology migration. |
| B3 | done | Create this temporary workbench and index it. | Web README temporary archive row exists. |
| B4 | done | Decide next implementation slice. | M1 Ref health verifier matrix selected first. |
| B5 | done | Define verification before editing. | Focused IdentityRefIndex route tests, full Web route tests, and backend `py_compile`. |

## TODO-During Tasks

These are the implementation slices. Only one should be `in_progress` at a
time.

| ID | Status | Task | Scope | Verification |
|:--|:--|:--|:--|:--|
| M1 | done | Ref health verifier matrix | Added deterministic local path, URL-not-checked, remote-not-checked, Graphiti UUID status-map, and Obsidian UUID status-map verification through `POST /api/memory/identity-ref-index/verify`. Operator apply can persist computed ref health. | Focused route tests for ok/missing/unknown; full Web route tests `63 passed`; no network in unit tests. |
| M2 | done | Merge/conflict policy | Added `conflicts[]`, explicit states `weak` / `confirmed` / `conflicted` / `tombstoned`, signal-overlap merge, and conflict preservation without auto-overwrite or ref rebind. | Route tests cover duplicate Graphiti UUID, conflicting L2-B UUID, and non-conflicting alias/ref merge; full Web route tests `64 passed`. |
| M3 | done | Graphiti raw envelope route | Extended Graphiti export draft/import plan to attach raw fact/node/episode envelope candidates and CORE-015 `identity_ref_drafts`; operator L1.5 export also carries `graphiti_raw` in Observation meta. | Graphiti subgraph route tests assert raw labels/custom attrs/source/target/episode preservation; full Web route tests `64 passed`. |
| M4 | done | GraphitiResolver backend | Added read-only `POST /api/memory/identity-ref-index/resolve-graphiti`; resolves Graphiti source/target/fact UUIDs through IdentityRefIndex and returns L2-B edge drafts only when both endpoints are `resolved_l2b`. | Tests cover both endpoints resolved, one missing, both missing, and conflicted source; full Web route tests `66 passed`. |
| M5 | done | Materialized L2-B edge apply | Added operator route `POST /api/memory/identity-ref-index/apply-graphiti-edge`. It re-runs CORE-015 endpoint resolution, preserves raw Graphiti metadata, and then delegates the actual write to `apply_l2b_edge -> L2BGraph.connect(SemanticEdge)`. | Route tests prove preview/operator gate, raw metadata preservation, and no unresolved endpoint write; full Web route tests `68 passed`. |
| M6 | done | Web UI surfacing | Added Graphiti Source Board controls for IdentityRefIndex snapshot, ref verification, Graphiti edge endpoint resolution, preview edge apply, and operator materialize-to-L2-B. Built assets land in `web/console_dist` for the existing 7893 Web Console path. | `npm run typecheck` passed; `npm run build` passed. |
| M7 | done | Nanobot/git/MCP ref scan plan | Added `POST /api/memory/identity-ref-index/ref-scan-plan`, registered Scheduler task type `ref_scan`, classified local/url/ECS/Graphiti/Obsidian refs into MCP check plans, and surfaced a `Ref Scan Plan` control in the existing 7893 Graphiti Source Board. | Plan-only dry-run; no ECS, Graphiti, L2-B, file, manifest, or App DTO mutation. Focused CORE-015 tests `8 passed`; full Web route tests `69 passed`; `npm run typecheck` and `npm run build` passed. |
| M8 | done | Ref scan dispatch/result intake | Added operator-gated `POST /api/memory/identity-ref-index/ref-scan-dispatch`, read-only `GET /api/memory/identity-ref-index/ref-scan-results`, result parsing for Scheduler ledger rows with `memory_ref_scan_result`, and Source Board buttons for dispatch/results. Dispatch enqueues only a read-only `ref_scan` task with `allow_mutation=false`; result intake does not repair refs automatically. | Focused CORE-015 tests `12 passed`; full Web route tests `73 passed`; `npm run typecheck` and `npm run build` passed. |
| M9 | done | Fallback ref_scan worker implementation | Implemented structured `ref_scan` handling in the Parrot fallback `NanobotConsumer`: local paths are stat/hash checked read-only, ECS/URL/Graphiti/opaque locators remain explicit `unknown` until MCP/remote checkers run, and any `allow_mutation=true` task is refused. | `py_compile` passed; focused worker + CORE-015 tests `15 passed`; Web route + worker tests `76 passed`. |
| M10 | done | Live MCP/ECS ref_scan smoke | Added `src/scripts/smoke_ref_scan.py` and ran a real read-only dispatch through Scheduler/Nanobot against ECS Redis via SSH tunnel on isolated `REDIS_DB=15`. The Web ledger returned a `memory_ref_scan_result` row with 4 refs: local Obsidian path `ok` + SHA-256, URL/ECS/Graphiti pointer explicit `unknown` requiring MCP/remote checkers, and 2 manifest-delta proposals only. | No manifest write, RefIndex health update, L2-B write, Graphiti mutation, ECS file write, or App DTO mutation. Command used local code with ECS Redis transport, not a remote code deployment. |
| M11 | done | Optional read-only remote checkers | Added opt-in `ref_scan` URL HEAD and Graphiti search-probe checkers, plus a guarded ECS local stat/hash checker that requires ECS-side confirmation before mapping `ecs://` locators to local paths. The existing 7893 Source Board now has a `Remote probes` checkbox that passes `remote_checks=[url, ecs, graphiti]` into plan/dispatch receipts. | `py_compile` passed; worker + Web route tests `79 passed`; `npm run typecheck` and `npm run build` passed; live ECS Redis smoke with `--remote-checks` returned URL 404 as `missing`, Graphiti search-probe as `unknown` with no exact smoke UUID, ECS as guarded `unknown`, and no writes. |
| M12 | done | Real Graphiti multi-hop import/search | Upgraded `/api/graphiti/subgraph/search` to accept `strategy`, `depth`, `expansion_limit`, and optional `focal_node_uuid`. `iterative_hybrid` performs real follow-up Graphiti searches from discovered endpoint/fact terms, dedupes hits, returns search_plan, preserves Graphiti raw envelopes and search_context, and feeds the existing selected-hit L1.5 export/import path. The 7893 Source Board now exposes Strategy/Depth/Focal UUID controls. `query_memory` now uses the same Graphiti subgraph path for GOSLO Intent natural-language memory lookup. | `py_compile` passed; Web route tests `74 passed`; focused Graphiti tests `2 passed`; `npm run typecheck` and `npm run build` passed. Live ECS smoke: non-dry-run Episode write to 8790, 7893 true search returned 9 hits / 19 nodes / 9 edges, Intent `query_memory` returned the same Graphiti facts, and operator L1.5 import admitted 2 nodes. |

## TODO-After Gate

Every completed M-task must do these.

| Gate | Status | Task | Exit signal |
|:--|:--|:--|:--|
| A0 | done | Run focused tests. | M12 `py_compile` passed for `graphiti_console`, Web BFF, app-monitor, and `query_memory`; focused multi-hop/export tests passed. |
| A1 | done | Run relevant full tests/build. | M12 Web route tests report `74 passed`; `npm run typecheck` and `npm run build` passed; live 7893/ECS Graphiti smoke passed with a true Episode write, search, Intent query, and L1.5 operator import. |
| A2 | done | Update parent durable design note. | Durable M12 multi-hop search/import conclusion promoted. |
| A3 | done | Update TODO board. | WEB-014.6/014.9/014.17 record M12 completion. |
| A4 | done | Update Web README route/status index. | Web README notes Strategy/Depth/Focal UUID controls, 7893 -> 8790 true search, and M12 live smoke status. |
| A5 | done | Update CORE-015 candidate note if fields changed. | No App/shared DTO fields changed; M11 stays Web/Scheduler/Nanobot receipt plumbing plus read-only checker policy. |
| A6 | done | Record remaining risks. | Next recommended task is true Graphiti UUID CRUD lookup route and ECS-side nanobot/MCP checker deployment, then reviewed write-back design. |

## Current Step Choice

M12 is complete. Next task should be M13: add true Graphiti UUID CRUD/lookup
for exact entity/fact/episode inspection and deploy/restart the ECS 8790
app-monitor so its subgraph endpoint returns full raw Graphiti envelopes without
requiring the local 7893 BFF to reconstruct from the older `/api/graphiti/search`
shape.

Reason:

- M1 now gives refs a deterministic health vocabulary.
- M2 now gives Graphiti/L2-B/ref UUID collisions an explicit `conflicted`
  state and preserves evidence instead of silently rebinding records.
- M3 keeps raw Graphiti fact/entity/episode evidence in receipts and
  Observation meta, and emits CORE-015 identity/ref draft payloads.
- M4 previews endpoint resolution and blocks missing/conflicted endpoints.
- M5 materializes already-resolved Graphiti fact edges through the existing
  L2-B edge writer and preserves raw Graphiti metadata.
- M6 surfaces IdentityRefIndex snapshot/health, resolver preview, and
  materialized edge apply controls inside the existing Graphiti Source Board.
- M7 created the dry-run contract for remote/ECS/URL ref health.
- M8 can dispatch that contract through Scheduler/Nanobot and read
  `memory_ref_scan_result` rows back from the Scheduler ledger without creating
  a hidden repair/write path.
- M9 makes the local fallback nanobot produce structured scan results for local
  refs and explicit unknown rows for remote refs.
- M10 proves the dispatch/result return path over ECS Redis transport.
- M11 proves optional URL and Graphiti remote probes can run through the same
  path, while ECS path probing remains correctly guarded outside ECS.
- M12 proves true Graphiti write/search/import over the existing 7893 -> ECS
  8790 path and moves GOSLO Intent memory lookup onto the same subgraph query
  route.

Completed M12 verification:

- `py_compile` for `src/parrot/brain/graphiti_console.py`,
  `src/parrot/web_console/server.py`, `src/parrot/brain/app_monitor_server.py`,
  and `src/parrot/brain/tools/query_memory.py`.
- Web route tests: `74 passed`.
- Focused Graphiti multi-hop/operator tests: `2 passed`.
- `npm run typecheck` passed.
- `npm run build` passed and updated `web/console_dist`.
- 7893 was restarted with
  `PARROT_WEB_CONSOLE_GRAPHITI_URL=http://8.216.45.45:8790`.
- ECS 8790 accepted non-dry-run Episode write
  `codex_m12_graphiti_live_smoke_*` into `arknights_test`.
- 7893 `/api/graphiti/subgraph/search` returned 9 hits / 19 nodes / 9 edges
  for `Amiya Rhodes Island Chernobog live smoke` with depth 2 and four real
  Graphiti search calls in `search_plan`.
- Intent `query_memory(..., "arknights_test", 2)` returned the same Graphiti
  facts as bounded subgraph context.
- Operator import with `dry_run=false` and `operator_mode=true` admitted 2
  L1.5 nodes from returned Graphiti hits.

## Execution Ledger

| Time | Entry |
|:--|:--|
| 2026-05-17 | Created workbench, questionnaire index, TODO-before/during/after gates, and selected M1 as next implementation target. |
| 2026-05-17 | Completed M1 Ref health verifier matrix: `POST /api/memory/identity-ref-index/verify`, deterministic local/URL/remote/Graphiti/Obsidian health checks, operator-only health persistence, focused tests 2 passed, full Web route tests 63 passed. |
| 2026-05-17 | Completed M2 merge/conflict policy: single existing identity signal merges, explicit or multi-canonical overlap records `conflicted`, conflicting UUIDs/refs are preserved without auto-rebinding, focused tests 3 passed, full Web route tests 64 passed. |
| 2026-05-17 | Completed M3 Graphiti raw envelope route: export-draft/import-plan now carry `graphiti_raw_envelopes` and CORE-015 `identity_ref_drafts`; operator export carries `graphiti_raw` in Observation meta; focused Graphiti subgraph tests 5 passed, full Web route tests 64 passed. |
| 2026-05-17 | Completed M4 GraphitiResolver backend: `POST /api/memory/identity-ref-index/resolve-graphiti` resolves source/target/fact UUIDs, returns pointer candidates for missing endpoints, blocks conflicted endpoints, and never writes L2-B; focused IdentityRefIndex tests 5 passed, full Web route tests 66 passed. |
| 2026-05-17 | Completed M5 materialized L2-B edge apply: `POST /api/memory/identity-ref-index/apply-graphiti-edge` re-resolves Graphiti fact endpoints, blocks unresolved endpoints, and delegates resolved writes to `apply_l2b_edge -> L2BGraph.connect(SemanticEdge)` with raw Graphiti metadata preserved; focused tests 7 passed, full Web route tests 68 passed. |
| 2026-05-17 | Completed M6 Web UI surfacing: Graphiti Source Board now has IdentityIndex count/load, Ref verifier, Graphiti Edge resolver preview, preview edge apply, and operator materialize-to-L2-B controls wired to CORE-015 routes; `npm run typecheck` and `npm run build` passed. |
| 2026-05-17 | Completed M7 Nanobot/git/MCP ref scan plan: `POST /api/memory/identity-ref-index/ref-scan-plan` drafts a plan-only `ref_scan` task with local/url/ECS/Graphiti/Obsidian locator checks, git manifest diff policy, and disallowed mutation list; existing Graphiti Source Board now exposes `Ref Scan Plan`; focused tests 8 passed, full Web route tests 69 passed, `npm run typecheck` and `npm run build` passed. |
| 2026-05-17 | Completed M8 ref scan dispatch/result intake: `POST /api/memory/identity-ref-index/ref-scan-dispatch` operator-enqueues read-only `ref_scan` tasks; `GET /api/memory/identity-ref-index/ref-scan-results` reads `memory_ref_scan_result` rows from the Scheduler ledger; existing Graphiti Source Board now exposes Dispatch Scan and Scan Results; focused tests 12 passed, full Web route tests 73 passed, `npm run typecheck` and `npm run build` passed. |
| 2026-05-17 | Completed M9 fallback `ref_scan` worker: Parrot `NanobotConsumer` now returns structured read-only local path stat/hash results, explicit unknown remote URL/ECS/Graphiti rows, manifest delta proposals, and mutation refusal for `allow_mutation=true`; focused worker + CORE-015 tests 15 passed; Web route + worker tests 76 passed. |
| 2026-05-17 | Completed M10 live `ref_scan` smoke: added `src/scripts/smoke_ref_scan.py`, verified local missing-Redis skip behavior, then ran through an SSH tunnel to Castle/ECS Redis DB15. Scheduler -> Nanobot -> Scheduler ledger returned `memory_ref_scan_result` for 4 refs: local path ok/hash, URL/ECS/Graphiti explicit unknown requiring MCP checkers, 2 manifest-delta proposals, and no automatic mutation. |
| 2026-05-17 | Completed M11 optional remote checkers: `ref_scan` can now run URL HEAD and Graphiti search-probe read-only when requested, ECS local path stat/hash is guarded by ECS-side confirmation, the 7893 Source Board exposes `Remote probes`, and live ECS Redis smoke with `--remote-checks` returned URL `missing`, Graphiti `unknown`, ECS guarded `unknown`, local path `ok/hash`, and zero automatic writes. |
| 2026-05-17 | Completed M12 real Graphiti search/import: `/api/graphiti/subgraph/search` now supports `strategy`, `depth`, `expansion_limit`, and optional `focal_node_uuid`; `iterative_hybrid` performs real follow-up Graphiti searches, returns a search_plan, preserves raw/search context, and feeds the existing Graphiti -> L1.5 import path. 7893 was restarted with ECS 8790 as Graphiti proxy; a non-dry-run `arknights_test` Episode write succeeded on ECS, 7893 true search returned 9 hits / 19 nodes / 9 edges, Intent `query_memory` returned the same facts, and operator import admitted 2 L1.5 nodes. |
