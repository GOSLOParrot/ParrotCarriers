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
| Q3 | Which official or skill docs are relevant and current? | Source list. | M14 refresh checked Zep Graphiti adding/search/CRUD/namespacing/custom types/MCP/LLM docs, rustworkx PyDiGraph docs, FalkorDB Docker persistence/compose docs, Zep temporal graph paper, and Parrot Graphiti/RustWorkX/L2-B skills. M15 implementation follows Graphiti's lower-level SearchConfig recipe model for combined/edge/node/community search while keeping L2-B as a projection layer. M16 follows the skill guidance that Graphiti remains the temporal/provenance graph and rustworkx indices remain volatile runtime handles. Durable source anchors are recorded in `../graphiti_l2b_ref_identity_design_20260517.md`. |
| Q4 | What data must be preserved raw? | Field list and sample payload. | Done for M16: search/export/import-plan receipts now carry `graphiti_bundle` with `raw_envelopes`, fact/entity/episode/community sections, raw lookup payloads, search plan/config, IdentityRef drafts, edge drafts, and an L2-B projection/import overlay. |
| Q5 | What is the canonical identity rule? | Merge/conflict policy. | Done for M2: one existing signal merges; explicit or multi-canonical overlap marks `conflicted` and preserves evidence without auto-rebinding existing records. |
| Q6 | What makes a Ref healthy, stale, moved, or broken? | Verifier matrix. | Done for M1: local paths are checked directly; URLs/ECS/remote locators stay `unknown`; supplied Graphiti/Obsidian UUID maps are testable. |
| Q7 | How does a Graphiti edge become an L2-B edge? | Resolver flow and preconditions. | Done for M5 backend: `resolve-graphiti` previews endpoint state; `apply-graphiti-edge` re-resolves, then writes only when source/target are `resolved_l2b` and the operator gate is open. |
| Q8 | Which EdgeKind classes are filters/views, not relation ontology? | EdgeKind/view mapping. | Coarse view classes only; raw relation remains metadata. |
| Q9 | What should nanobot/git/MCP do here? | Workflow boundary. | Done for M7: Web drafts a `ref_scan` nanobot contract; git stores reviewable manifests; MCP checks locators; Parrot index remains authority. |
| Q10 | What is deliberately not implemented in this slice? | Non-goal list. | No direct FalkorDB surgery; no Graphiti ontology migration; no App DTO promotion. |
| Q11 | What is the smallest route/API proof? | Route contract and tests. | Snapshot/draft/apply/verify/resolve-graphiti/apply-graphiti-edge exist; M14 adds semantic `graphiti-ref/draft` and `graphiti-ref/apply` routes for GraphitiRecordRef + ExternalRefRecord + RefMoveEvent review. |
| Q12 | What is the Web UI proof? | Visible control and receipt. | Done through M7: existing Graphiti Source Board loads IdentityIndex, verifies refs, resolves/materializes Graphiti edges, and now drafts a Ref Scan Plan receipt. |
| Q13 | What needs ECS/live smoke? | Command or route plus expected result. | Done through M18: ECS 8790 is now deployed with the SearchConfig/bundle adapter. Remote `/api/graphiti/search` and `/api/graphiti/subgraph/search` return `search_config.mode="_search"` for `combined_rrf`; remote subgraph search returns `graphiti_bundle` counts `facts=3/entities=4/episodes=3/communities=0` with UUID lookup `10/10`; 7893 -> 8790 returns the same `_search`/bundle proof. |
| Q14 | What docs must be updated after the slice? | TODO/Web README/business/core candidate list. | This workbench plus parent docs and TODO board. |

## Pre-Implementation Readback

Read this block before editing code or splitting the next TODO item. It is the
short review summary for the M14 research pass.

Must-read anchors:

- Durable research: `../graphiti_l2b_ref_identity_design_20260517.md`,
  section `2026-05-17 M14 research deep dive`.
- Current task state: this file, sections `Current Step Choice`,
  `TODO-During Tasks`, and `Execution Ledger`.
- Shared candidate boundary:
  `../../core_interface_candidate_queue_20260513.md`, `CORE-015`.
- Business flow summary:
  `../graphiti_management_business_flow_20260513.md`,
  section `2026-05-17 M14 research update`.
- Lane TODO: `../../tasks/APP_WEB_PARALLEL_TODOLIST_20260513.md`,
  `WEB-014.17`.

Review outcome:

- Graphiti owns temporal memory, provenance, entity/fact extraction, and raw
  Episode history. L2-B must preserve Graphiti raw envelopes instead of
  flattening results into local edge labels.
- `group_id` is mandatory partition scope for add, search, lookup, export,
  fallback scan, and import. Never assume the default graph contains partition
  data.
- Graphiti natural-language/hybrid search is valid for discovery and subgraph
  expansion. Exact UUID proof must use CRUD lookup, not a search-probe.
- Custom Graphiti entity/edge types are additive guidance for new ingestion.
  Do not start with a large ontology migration or one custom edge type per Web
  visual filter.
- RustworkX node/edge indices are volatile graph handles. Persist business
  identity through canonical/L2-B/Graphiti/ref UUIDs and rebuild
  `uuid <-> rwx_idx` maps.
- EdgeKind is a view/filter/runtime class. Graphiti predicate/name/fact text,
  source/target UUIDs, labels, attributes, and episodes stay in metadata.
- Episode-only ref management is insufficient for moving external files. Use a
  mutable RefIndex/IdentityBinding layer and record moves/repairs as audit
  Episodes.
- Nanobot + MCP + git is acceptable only as an operator-gated scan/repair
  control plane: propose, check, record manifest deltas, then apply through Web
  receipts.

Implementation requirements before the next slice:

1. State the user-visible proof in one sentence.
2. Name the owner of truth for every field touched: Graphiti, RefIndex,
   IdentityBinding, L2-B, L1.5, nanobot, git, or Web.
3. List the raw Graphiti fields that must survive the route/receipt/import.
4. Keep preview/apply split and operator-mode gates for every write.
5. Include an ECS/live canary when the feature claims real Graphiti or ref
   connectivity.
6. Update this workbench, the durable design note, the business flow note, the
   TODO board, and CORE-015 candidate text after the slice.

## TODO-Before Gate

No implementation slice starts until these are checked.

| Gate | Status | Task | Exit signal |
|:--|:--|:--|:--|
| B0 | done | Load Parrot skill bridge and relevant Graphiti/RustWorkX/L2-B skill context. | Skill source read or already summarized in current working docs. |
| B1 | done | Re-read current durable design and current code ownership. | `graphiti_l2b_ref_identity_design_20260517.md` plus `identity_ref_index.py` referenced. For M14+, also read `Pre-Implementation Readback` above before editing or splitting TODO. |
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
| M13 | done | True Graphiti UUID lookup + ECS persistence | Added `/api/graphiti/lookup` using Graphiti official `get_by_uuid` helpers scoped to the partition graph, enriched subgraph hits with full fact/source/target/episode raw objects, proxied 7893 Episode writes and operator subgraph exports to ECS 8790, added app-monitor export routes, and fixed FalkorDB persistence by mounting the real data path plus `REDIS_ARGS` (`appendonly yes`, `appendfsync everysec`, `noeviction`). Added a bounded FalkorDB partition-graph fallback when Graphiti hybrid search returns zero after restart but persisted facts are present. | `py_compile` passed; Web route tests `79 passed`; `npm run typecheck` and `npm run build` passed earlier in the slice. Live ECS smoke: 7893 wrote a non-dry-run Episode through ECS, searched persisted `arknights_test` after app/FalkorDB restart, returned 8 hits / 13 nodes / 8 edges with lookup 16/16, and operator export ran remotely with `dry_run=false`, `operator_mode=true`, 2 raw envelopes, 2 edge drafts, and 5 IdentityRef drafts. |
| M14 | done | Reviewed Graphiti Ref/UUID write-back design | Research pass completed before coding. First implementation slice adds semantic M14 routes: `POST /api/memory/identity-ref-index/graphiti-ref/draft` and `POST /api/memory/identity-ref-index/graphiti-ref/apply`. They bind one GraphitiRecordRef to reviewed ExternalRefRecords, draft RefMoveEvents for new/moved locators, preserve raw Graphiti envelopes in identity metadata, and generate a Graphiti audit Episode draft. Default apply persists only the IdentityRefIndex JSON under operator mode; audit Episode write is opt-in through `write_graphiti_audit_episode=true`. UI slice now surfaces this in the existing 7893 Graphiti Source Board: Export plan shows Ref drafts, operator can choose a Graphiti fact/entity/episode pointer, set Ref ID/kind/locator, preview the write-back, and optionally write the audit Episode during apply. Bugfix: a Graphiti pointer with no locator, canonical URI, or content hash now binds only the GraphitiRecordRef identity and skips empty ExternalRefRecord / RefMoveEvent drafts. | `py_compile` passed; full Web route tests report `82 passed`; `npm run typecheck` and `npm run build` passed after UI surfacing and bugfix. Live canary through `PARROT_WEB_CONSOLE_GRAPHITI_URL=http://8.216.45.45:8790` searched `arknights_test`, got 4 hits / 9 nodes, selected real Graphiti fact UUID `0ea2009c-402d-4332-81b4-31fa57e67688`, and persisted a temp RefIndex binding with `identity_count=1` / `ref_count=1` while leaving direct Graphiti/L2-B writes false and audit Episode as `draft_only`. Audit-write canary with `PARROT_WEB_CONSOLE_GRAPHITI_TIMEOUT_S=240` and `write_graphiti_audit_episode=true` wrote the audit Episode to ECS 8790 with `direct_graphiti_write=true`, `graphiti_audit_episode_written=true`, and mutation scope `memory_identity_ref_index_json_and_graphiti_audit_episode`. Running 7893 was restarted with ECS proxy/240s timeout; runtime smoke confirmed the new draft route, true ECS search (`3 hit(s), 7 node(s)`, lookup success), search -> export-draft -> identity_ref_drafts -> M14 write-back draft path, and an empty external-ref regression returns `external_payloads=0`, `external_records=0`, `move_events=0`. |
| M15 | done | Graphiti SearchConfig recipe adapter | `/api/graphiti/search` and `/api/graphiti/subgraph/search` now accept `search_recipe`, `node_labels`, and `edge_types`. When local Graphiti exposes low-level `_search` or `search_`, recipe names map to Graphiti SearchConfig recipes such as combined RRF/MMR/cross-encoder, edge RRF/MMR/node-distance/episode-mentions/cross-encoder, node RRF/MMR/node-distance/episode-mentions/cross-encoder, and community RRF. The adapter passes partition scope, focal UUID, bounded limits, and optional SearchFilters through the official Graphiti search layer; if low-level search fails it falls back to public `search()` and records the fallback reason in `search_config`. The 7893 Source Board now exposes separate expansion Strategy and Graphiti Recipe controls plus Node labels / Edge types fields, so Web can combine local multi-hop expansion with Graphiti's own retrieval modes. | `py_compile` passed for Graphiti/Web/test files; focused Graphiti route regressions passed (`4 passed`); full Web route tests report `83 passed`; `npm run typecheck` and `npm run build` passed; `git diff --check` had only CRLF warnings. New regression proves `combined_rrf`, `node_labels`, and `edge_types` reach `_search(**kwargs)` as config/filter/group_id, and `search_plan` records mode `_search` plus recipe `COMBINED_HYBRID_SEARCH_RRF`. Subgraph preview now upgrades endpoint placeholder nodes when a real Graphiti entity hit for the same UUID is returned, preserving entity raw payload instead of freezing the earlier source/target placeholder. 7893 was restarted with ECS proxy/240s timeout; static smoke found the separate Strategy/Recipe/filter controls in `assets/app.js`; runtime route smoke sent `strategy=iterative_hybrid + search_recipe=combined_rrf + Entity/CrisisFact` to ECS and returned `3 hit(s), 7 node(s), 3 edge(s)`. Because ECS 8790 is not yet running the M15 adapter, that live receipt did not include low-level `_search` mode; deploy M15 to ECS/app-monitor before expecting `mode=_search` in live receipts. |
| M16 | done | Graphiti subgraph bundle preservation | Search/export/import-plan receipts now include `graphiti_bundle`, a reviewable package with `schema_version=1`, raw Graphiti hit envelopes, sections for facts/entities/episodes/communities, enriched lookup payloads, selected UUID sets, subgraph renderer data, edge drafts, identity/ref drafts, search plan/config, and L2-B projection policy. Import-plan adds an `import_overlay` with CORE-013 destination policy and apply preconditions. This does not write Graphiti/FalkorDB directly and does not convert Graphiti predicates into local EdgeKind enums. | Full Web route tests report `83 passed`. Regression coverage proves export-draft preserves bundle facts/entities/episodes, SearchConfig search receipts carry recipe/filter data inside the bundle, enriched UUID lookup raw objects are preserved inside bundle sections, and import-plan overlays destination/apply policy onto the same bundle. |
| M17 | done | Bundle section UI + live 7893 canary | The existing 7893 React Source Board now renders a `Graphiti bundle` panel from receipt data. It shows schema/selection counts, fact/entity/episode/community section counts, search strategy/recipe/lookup/search-plan summary, projection policy, import overlay destination when present, and sample fact/entity/episode/community rows. This is a UI/read-model surfacing layer; it does not add a new backend DTO or mutate Graphiti/L2-B. | `npm run typecheck` and `npm run build` passed; built assets contain the bundle panel strings/classes; full Web route tests still report `83 passed`. 7893 was restarted on PID 53552 with `PARROT_WEB_CONSOLE_GRAPHITI_URL=http://8.216.45.45:8790` and 240s timeout. Live route canary through 7893 searched `arknights_test / Amiya Chernobog`, returned true Graphiti UUID `0ea2009c-402d-4332-81b4-31fa57e67688`, formed bundle counts `facts=3/entities=4/episodes=0/communities=0`, and import-plan overlay destination `isolated_compartment`. `search_plan[0].search_config.mode` stayed null because ECS 8790 still needs the M15/M16 adapter deployed. |
| M18 | done | ECS/app-monitor deployment + remote `_search` proof | Fixed `src/parrot/brain/app_monitor_server.py` so ECS 8790 forwards `search_recipe`, `node_labels`, and `edge_types` to Graphiti, and added the missing app-monitor `/api/graphiti/subgraph/import-plan` route. Deployed the minimal backend file set to ECS with backups, compiled remote code, and restarted `parrot-app-monitor`. | Local checks: app-monitor tests `9 passed`, Web route tests `83 passed`, and backend `py_compile` passed. Remote 8790 canary: `/api/graphiti/search` and `/api/graphiti/subgraph/search` returned `mode="_search"`, `fallback=false`, `low_level="_search"`, first fact UUID `0ea2009c-402d-4332-81b4-31fa57e67688`, bundle counts `facts=3/entities=4/episodes=3/communities=0`, and UUID lookup `10/10`. Remote import-plan returned overlay destination `isolated_compartment`; 7893 -> 8790 canary returned the same `_search` and bundle proof. |
| M19 | done | Graphiti bundle -> L2-B/RustWorkX projection preview | Added CORE-013 transform kind `graphiti_bundle_projection` and wired Graphiti import-plan to embed `l2b_transform_preview` plus `graphiti_bundle.import_overlay.transform_preview`. The transform consumes preserved bundle sections, creates pointer-style L2-B preview Nodes/Edges with raw Graphiti payloads intact, builds episode support links, runs an in-memory `rustworkx.PyDiGraph` topology preview, and states that rustworkx indices are ephemeral preview handles. | Local checks: backend `py_compile`, full Web route tests `83 passed`, frontend `npm run typecheck`, and `npm run build` passed. ECS 8790 was deployed with `graph_policy.py` and `memory_ops.py`, backed up under `codex_backups/m19_graphiti_transform_20260517164126`, compiled, and restarted to PID `127087`. Remote 8790 and local 7893 passthrough both returned `_search`, `fallback=false`, bundle counts `facts=3/entities=4/episodes=3/communities=0`, selected fact UUID `0ea2009c-402d-4332-81b4-31fa57e67688`, import-plan success `true`, L2-B preview counts `nodes=3/edges=1/episode_links=2`, rustworkx preview `nodes=3/edges=3`, and `rwx_idx_policy=ephemeral_do_not_persist` with `direct_l2b_write=false`. |
| M20R | done | Review/research gate before materialized apply | Audited M12-M19 against the original requirement: true Graphiti search/import preview now works through ECS 8790 and 7893, raw `graphiti_bundle` is preserved, and L2-B/RustWorkX adds a preview-only projection. Confirmed that local Node/Edge kinds are view/algorithm categories rather than Graphiti predicate mirrors. Recorded the remaining gaps: preview UUIDs are not canonical UUIDs, RefIndex is still file-backed rather than DB-backed, and durable materialization still needs an operator-gated apply path through IdentityRefIndex. | Durable review added to `graphiti_l2b_ref_identity_design_20260517.md` with official Graphiti/RustWorkX version/doc anchors and research refs: Graphiti SearchConfig/Episodes/group_id/custom types, `graphiti-core==0.28.2`, `rustworkx==0.17.1`, HippoRAG, AriGraph, GAT, DySAT, GraphGPS, AGCN, and rustworkx JOSS/arXiv. |

## TODO-After Gate

Every completed M-task must do these.

| Gate | Status | Task | Exit signal |
|:--|:--|:--|:--|
| A0 | done | Run focused tests. | M19 backend `py_compile` passed; Web route tests still report `83 passed`. |
| A1 | done | Run relevant full tests/build. | Frontend `npm run typecheck` and `npm run build` passed; remote ECS 8790 and local 7893 canaries both returned real `_search` receipts, `graphiti_bundle` sections, and L2-B/RustWorkX projection preview counts. |
| A2 | done | Update parent durable design note. | Durable M19 Graphiti bundle projection conclusion promoted. |
| A3 | done | Update TODO board. | WEB-014 records M19 projection preview and ECS/7893 true-connection proof. |
| A4 | done | Update Web README route/status index. | Web README notes Graphiti bundle -> L2-B/RustWorkX preview surfacing and ECS/7893 proof. |
| A5 | done | Update CORE-015 candidate note if fields changed. | No App/shared DTO fields changed; M19 is Web/backend CORE-013/CORE-015 receipt plumbing plus preview topology proof. |
| A6 | done | Record remaining risks. | Next recommended task is M20: add operator-reviewed apply paths from previewed bundle pointers into IdentityRefIndex/L1.5/L2-B with rollback/audit, plus fuller UI selection of which bundle sections should materialize. |

## Current Step Choice

M20R is complete as a review/research gate. ECS 8790 and the existing 7893 Web
Console can both search real Graphiti through `_search(SearchConfig)`, preserve
a full `graphiti_bundle`, and preview how the selected bundle projects into
L2-B / RustWorkX without materializing topology or persisting rustworkx
indices. The next implementation slice should be M20 apply design: operator
materialization from `graphiti_bundle` into IdentityRefIndex + selected L1.5 /
L2-B nodes/edges, with canonical UUID binding, rollback/audit receipts, and no
direct FalkorDB/file mutation hidden inside the route.

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
- M13 proves exact Graphiti UUID lookup/enrichment, ECS 8790 write/import
  proxying, and FalkorDB persistence across app/container restarts.
- M14 research proves the remaining gap is not Graphiti search/import itself;
  it is controlled write-back for mutable refs and identity bindings without
  using Episode history as the only source of locator truth.
- M14 first implementation route proves the reviewed write-back shape without
  direct Graphiti or file mutation by default: it persists current locator state
  in RefIndex and emits a Graphiti audit Episode draft for operator review.
- M15 proves Web can call Graphiti's configurable recipe path instead of only
  normal public search: strategy/filter controls pass into `_search(SearchConfig)`
  where available, and the receipt records whether low-level search or fallback
  search ran.
- M16 makes the one-click import preview preserve a complete Graphiti bundle:
  Graphiti facts/entities/episodes/raw lookup/search plan stay intact, while
  L1.5/L2-B add only lightweight projection and import-policy overlays.
- M17 makes that preserved bundle operator-visible in the existing 7893 Web
  Console and proves the path against true ECS Graphiti data.
- M18 removes the ECS adapter blocker: the remote app-monitor itself now
  forwards Graphiti recipe/filter controls, returns `_search` receipts, returns
  bundle section counts, and exposes remote import-plan overlay receipts.
- M19 uses that proven remote bundle as the input for a controlled
  `graphiti_bundle_projection` transform. L2-B gets pointer-style preview
  nodes, preview `graphiti_fact` edges, episode support links, raw Graphiti
  metadata, and an in-memory RustWorkX topology summary; Graphiti remains the
  source of truth and real L2-B writes remain separate operator actions.
- M20R verifies that this shape is aligned with the original design intent:
  Edge/Node categories are for filters, spatial views, and RustWorkX algorithms,
  not a brittle one-to-one Graphiti predicate translation. It also fixes the
  boundary for refs: Graphiti Episodes are provenance/audit, while current
  mutable locator truth belongs in IdentityRefIndex/ExternalRefRecord and later
  a DB-backed index.

Completed M19 verification:

- Local backend `py_compile` passed for M19 files.
- Local Web route tests: `83 passed`.
- Frontend `npm run typecheck` and `npm run build` passed.
- Remote deployment: `graph_policy.py` and `memory_ops.py` backed up under
  `/opt/parrot/ParrotCarriers/codex_backups/m19_graphiti_transform_20260517164126`,
  compiled on ECS, and `parrot-app-monitor` restarted to PID `127087`.
- Remote 8790 `/api/graphiti/subgraph/search` with
  `search_recipe=combined_rrf`, `node_labels=["Entity"]`, and
  `edge_types=["CrisisFact"]` returned `mode="_search"`, `fallback=false`,
  first UUID `0ea2009c-402d-4332-81b4-31fa57e67688`, and bundle counts
  `facts=3/entities=4/episodes=3/communities=0`.
- Remote 8790 `/api/graphiti/subgraph/import-plan` on that real hit returned
  `projection_kind=graphiti_bundle_to_l2b_rustworkx_preview`,
  `selected_count=1`, `l2b_nodes=3`, `l2b_edges=1`, `episode_links=2`,
  RustWorkX preview `node_count=3`, `edge_count=3`, and
  `rwx_idx_policy=ephemeral_do_not_persist`; `direct_l2b_write=false`.
- Local 7893 -> ECS canary returned the same `_search`, bundle, projection,
  and RustWorkX preview proof; served assets include
  `L2-B transform preview`, `ephemeral preview only`, and `l2b preview nodes`.

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
| 2026-05-17 | Completed M13 true Graphiti UUID lookup and ECS persistence: `/api/graphiti/lookup` now uses partition-scoped Graphiti CRUD lookup; subgraph search enriches hits with full raw fact/source/target/episode objects; 7893 proxies real Episode writes and operator subgraph export to ECS 8790; app-monitor exposes export routes; FalkorDB volume now mounts `/var/lib/falkordb/data` with AOF/noeviction via `REDIS_ARGS`; after real FalkorDB restart, 7893 still returned persisted `arknights_test` hits via bounded partition-graph fallback and lookup 16/16, then remote operator export succeeded. |
| 2026-05-17 | Started M14 reviewed Ref/UUID write-back design: reread Parrot Graphiti/RustWorkX/L2-B skills and checked official Zep Graphiti, rustworkx, FalkorDB, and Zep temporal graph sources. Durable conclusion: keep Graphiti raw temporal data intact, keep rustworkx indices volatile, split mutable refs from Episodes, and use nanobot + MCP + git only as an operator-gated scan/repair control plane. |
| 2026-05-17 | Implemented M14 first write-back slice: `MemoryIdentityRefIndex.upsert_graphiti_ref_writeback()` plus Web routes `POST /api/memory/identity-ref-index/graphiti-ref/draft` and `/graphiti-ref/apply`. Draft/apply receipts include `IdentityBinding`, `GraphitiRecordRef`, `ExternalRefRecord`, `RefMoveEvent` drafts, and a Graphiti audit Episode draft. Default apply writes only the IdentityRefIndex JSON; no L2-B, Graphiti/FalkorDB, ECS/file, or App DTO mutation occurs unless a future explicit audit write route is enabled. Focused tests: `13 passed`. |
| 2026-05-17 | Ran M14 live canary with real ECS Graphiti search: local updated BFF used `PARROT_WEB_CONSOLE_GRAPHITI_URL=http://8.216.45.45:8790`, searched `arknights_test` for `Amiya Chernobog`, received `4 hit(s), 9 node(s)`, selected real fact UUID `0ea2009c-402d-4332-81b4-31fa57e67688`, and applied a temp RefIndex binding through `/api/memory/identity-ref-index/graphiti-ref/apply` with `dry_run=false` / `operator_mode=true`. Result: `identity_count=1`, `ref_count=1`, `direct_graphiti_write=false`, `direct_l2b_write=false`, audit Episode `draft_only`. |
| 2026-05-17 | Ran M14 audit Episode write canary: first attempt with the default 60s remote timeout produced a clean timeout receipt and no Graphiti write; second attempt with `PARROT_WEB_CONSOLE_GRAPHITI_TIMEOUT_S=240` succeeded through 7893 -> ECS 8790. The receipt reported `direct_graphiti_write=true`, `graphiti_audit_episode_written=true`, mutation scope `memory_identity_ref_index_json_and_graphiti_audit_episode`, and remote message `episode written`. |
| 2026-05-17 | Surfaced M14 in the existing 7893 React Source Board: added Graphiti Ref Write-back controls under Export plan, wired `api.memoryIdentityRefGraphitiRefDraft/Apply`, preserved Ref draft raw envelopes, exposed Ref ID/kind/locator plus an explicit audit Episode checkbox, built `web/console_dist`, restarted 7893 with `PARROT_WEB_CONSOLE_GRAPHITI_URL=http://8.216.45.45:8790` and `PARROT_WEB_CONSOLE_GRAPHITI_TIMEOUT_S=240`, then smoke-tested runtime route activation and real ECS search -> export draft -> identity_ref_drafts -> Graphiti-ref draft. |
| 2026-05-17 | Fixed M14 empty-external-ref bug: Graphiti write-back no longer creates `ExternalRefRecord` or `RefMoveEvent` rows from only `ref_id`/`ref_kind`; it now requires a locator, canonical URI, or content hash. Focused regression `3 passed`, full Web route tests `82 passed`, frontend typecheck/build passed, and 7893 runtime smoke returned `external_payloads=0`, `external_records=0`, `move_events=0` for the empty-locator case. |
| 2026-05-17 | Completed M15 Graphiti SearchConfig adapter: `search_recipe`, `node_labels`, and `edge_types` now flow through `/api/graphiti/search` and `/api/graphiti/subgraph/search` into Graphiti `_search(SearchConfig)` or `search_` when available. Web exposes separate local expansion Strategy and Graphiti Recipe controls, plus label/type filter inputs. Focused regression proves `combined_rrf` reaches `_search` with partition `group_id`, bounded config limit, and filter payload; receipts record `search_config.mode=_search` and the recipe constant. Full Web route tests now report `83 passed`, frontend typecheck/build passed, 7893 was restarted with ECS proxy/240s timeout, and runtime smoke returned true ECS results for `strategy=iterative_hybrid + search_recipe=combined_rrf` while noting ECS must receive this M15 code before live receipts can show `_search` mode. |
| 2026-05-17 | Completed M16 Graphiti subgraph bundle preservation: `/api/graphiti/subgraph/search`, `/export-draft`, `/export`, and `/import-plan` now carry `graphiti_bundle` with raw envelopes, fact/entity/episode/community sections, search plan/config, lookup payloads, edge drafts, identity/ref drafts, and L2-B projection/import overlays. Full Web route tests report `83 passed`; the next live step is deploying this adapter to ECS/app-monitor and smoking real bundle receipts through 7893 -> 8790. |
| 2026-05-17 | Completed M17 Graphiti bundle UI + live 7893 canary: Source Board renders bundle counts, search/lookup summary, projection/import overlay, and sample fact/entity/episode/community rows. Frontend typecheck/build passed, Web route tests remain `83 passed`, 7893 restarted with ECS proxy, and live `arknights_test` search/import-plan returned true Graphiti UUID `0ea2009c-402d-4332-81b4-31fa57e67688`, bundle counts `3/4/0/0`, and overlay destination `isolated_compartment`. ECS adapter deployment remains required for remote `_search` mode proof. |
| 2026-05-17 | Completed M18 ECS/app-monitor deployment: app-monitor now forwards Graphiti SearchConfig recipe/filter inputs and exposes `/api/graphiti/subgraph/import-plan`; deployed `app_monitor_server.py`, `graphiti_console.py`, and `memory_ops.py` to ECS with backup, restarted `parrot-app-monitor`, and verified remote 8790 plus 7893 passthrough return `_search`, `fallback=false`, bundle counts `facts=3/entities=4/episodes=3/communities=0`, UUID lookup `10/10`, and import overlay `isolated_compartment`. |
| 2026-05-17 | Completed M19 Graphiti bundle -> L2-B/RustWorkX projection preview: added `graphiti_bundle_projection`, import-plan `l2b_transform_preview`, Source Board `L2-B transform preview` rows, and tests. Deployed `graph_policy.py` and `memory_ops.py` to ECS with backup, restarted `parrot-app-monitor` to PID `127087`, and verified both remote 8790 and 7893 passthrough return real `_search` bundle data plus projection counts `l2b_nodes=3`, `l2b_edges=1`, `episode_links=2`, RustWorkX `nodes=3/edges=3`, `rwx_idx_policy=ephemeral_do_not_persist`, and `direct_l2b_write=false`. |
| 2026-05-17 | Completed M20R review/research gate: audited Node/Edge/UUID/Ref design against the original Graphiti-to-L2-B requirement, confirmed current Node/Edge categories are intentional view/algorithm projections, marked preview UUID and file-backed RefIndex as remaining gaps, and recorded official Graphiti/RustWorkX docs plus research refs in the durable design note before any materialized apply work. |
