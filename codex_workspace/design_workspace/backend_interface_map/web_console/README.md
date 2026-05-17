# Web Console Business Interfaces

This directory is owned by the Web Console chat.

Use it for Web-facing business-interface notes: ECS/module health, L1.5/L2-B
visualization, node/photo management, Blackboard, IntentWorkspace, Plan,
Scheduler/Nanobot monitoring, Maid/GOSLO chat observability, and Web-only
admin flows.

## Active Business Interface Index

This README is the local SSOT for active Web Console business-interface files.
Add new Web docs here when they are created, and remove or mark superseded
entries when a file stops being active.

| File | Status | TODO | Scope |
|:--|:--|:--|:--|
| `web_console_step1_console_plan_20260513.md` | approved | WEB-001, WEB-008 | Step 1 requirements, IA, visual direction, implementation order, doc hygiene. |
| `web_console_major_roadmap_20260515.md` | active roadmap | WEB-017, WEB-011, WEB-012, WEB-013, WEB-014, WEB-016 | Fixed Web Console mainline order, research gates before large implementation, dependency map, true-vs-fake implementation standard, realtime/import/RustWorkX timing, and 2026-05-16 resolved user decisions. |
| `observability_runtime_business_flow_20260513.md` | in_progress | WEB-002, WEB-004, WEB-005, WEB-009, WEB-012, WEB-015 | ECS/module health, `/status`, Blackboard, IntentWorkspace, Plan/task, Scheduler, Nanobot, AgentTeam/Maid Team, collaboration status, LineB voice lab smoke, Runtime Flow, HITL, trigger palette, and Time/Evidence debug surface. |
| `memory_graph_workspace_business_flow_20260513.md` | in_progress | WEB-003, WEB-007, WEB-010, WEB-011, WEB-013, WEB-016 | L1.5, L2-B, Blackboard, IntentWorkspace, node/photo management, Ref binding, Evidence/String Board, real-time memory visualization plan, Memory Canvas, planned full-screen L2-B monitor, and CORE-013 graph rewrite/subgraph overlay policy. |
| `graphiti_management_business_flow_20260513.md` | in_progress | WEB-006 | Graphiti/FalkorDB management route: observe/search/draft/dry-run first, Web operator surgery later. |
| `graphiti_l2b_ref_identity_design_20260517.md` | in_progress | WEB-014, WEB-016, CORE-006, CORE-013, CORE-015 | Durable research/design note for Graphiti raw preservation, L2-B UUID resolution, Edge filter/view classes, IdentityMap, RefIndex/RefNode, and nanobot/git/MCP ref management ownership. |
| `collaboration_flow_workbench_ssot_20260517.md` | active_design | WEB-012, CORE-010, CORE-011, CORE-015 | Runtime/Collaboration Flow workbench SSOT for searchable capability catalog, triggers/modules insertion, workflow draft, Plan/Nanobot compatibility, GOSLO behavior modes, and true-connection standards. |
| `collaboration_flow_architecture_cli_research_20260517.md` | active_research | WEB-012, CORE-010, CORE-011, CORE-015 | Comparative architecture research for LangGraph/Claude Code/Codex/ComfyUI/Node-RED/n8n/Temporal/Prefect patterns, Web layout direction, and the Web-plus-thin-CLI decision. |

## Temporary Working Archives

Temporary files are indexed here so they do not become scattered hidden SSOTs.
Promote durable decisions back into the active business files above.

| File | Status | Scope |
|:--|:--|:--|
| `_tmp/runtime_flow_memory_upgrade_research_20260513.md` | temporary-active | React + Vite migration, Runtime Flow workspace, Memory Graph workspace, HITL, runtime-flow read model, audit checklist. |
| `_tmp/l15_graphiti_import_test_20260515.md` | temporary-active | L1.5 source board, Obsidian profile import, Google Calendar mapping, Graphiti natural-language search, Arknights test partition, and Graphiti-to-L2-B subgraph export. |
| `_tmp/graphiti_l2b_ref_identity_workplan_20260517.md` | temporary-active | CORE-015 questionnaire index, TODO-before/during/after gates, completed M1 health verifier, completed M2 merge/conflict policy, completed M3 Graphiti raw envelopes, completed M4 GraphitiResolver preview, completed M5 L2-B edge apply, completed M6 Source Board controls, completed M7 ref scan plan, completed M8 dispatch/results intake, completed M9 fallback ref_scan worker, completed M10 live ECS Redis ref_scan smoke, completed M11 optional URL/Graphiti/ECS-guard remote probes, completed M12/M13 true Graphiti search/UUID lookup/ECS persistence, completed M14 Graphiti Ref write-back, completed M15 SearchConfig recipe/filter adapter, completed M16 Graphiti subgraph bundle preservation, completed M17 bundle UI, completed M18 ECS/app-monitor SearchConfig deployment, completed M19 Graphiti bundle -> L2-B/RustWorkX preview, completed M20R review/research gate, and execution ledger. |
| `_tmp/l2b_subgraph_tools_workplan_20260517.md` | temporary-active | L2-B operation-page subgraph tools research index, true-connection standard, TODO-before/during/after gates, implementation ledger for live bounded subgraph context, `noble_etiquette` partition sync, Graphiti Episode/Entity fallback search, and 7893 -> 8790 live import-plan proof. |
| `_tmp/collaboration_flow_workplan_20260517.md` | temporary-active | Collaboration Flow questionnaire index, TODO-before/during/after gates, external workflow/HITL/agent research references, capability catalog/workflow draft implementation plan, and verification ledger. |

## Related Project Skill Drafts

| Skill | Status | Scope |
|:--|:--|:--|
| `codex_workspace/codex_skills/react-force-graph-l2b/SKILL.md` | draft | WEB-013 full-screen L2-B realtime graph renderer, React-Force-Graph adapter, Obsidian-like graph filters/groups/local graph behavior, and trigger/attention animation references. |

## Completed Interface Ledger

Audit checkpoint: 2026-05-13. This ledger records implemented Web Console
surfaces that should be preserved while the next large Memory Graph work is
planned. Detailed business rationale stays in the active files above.

| Area | Implemented surface | Business file | Current status |
|:--|:--|:--|:--|
| Console shell | `GET /health`, static `web/console_dist/` React build with legacy `web/console/` fallback, zh/en setting, Obsidian-like layout, active-view refresh loop. | `observability_runtime_business_flow_20260513.md` | React + Vite is the formal route; legacy vanilla remains transition/reference only. |
| Orchestrator status | `GET /api/console/config`, `GET /api/orchestrator/health`, `GET /api/orchestrator/status`; BFF injects Bearer from `PARROT_ORCH_SECRET` server-side. | `observability_runtime_business_flow_20260513.md` | Implemented and tested; no secret leak. |
| Menu/App smoke | `GET /api/app/canvas`, `GET /api/app/modules`, `GET /api/app/line-profiles`, `POST /api/app/line-profiles/apply`, `POST /api/app/workspace/apply`. | `observability_runtime_business_flow_20260513.md`, `memory_graph_workspace_business_flow_20260513.md` | Useful smoke path; not the main next focus. |
| LineB voice lab / React LiveKit Bridge | `POST /api/app/lineb/audio-route`, `POST /api/app/lineb/tts-segment`, `POST /api/app/lineb/mic-input`, `GET /api/livekit/config`, `POST /api/livekit/web-token`; browser LiveKit audio wiring, React Runtime bridge, screen-share publish, screen-share sample check, event/transcript panes. | `observability_runtime_business_flow_20260513.md` | Implemented smoke; React bridge joined the configured room and subscribed to an `agent-*` audio track. Full no-camera conversation still needs user-approved mic/screen-share clicks and a running agent. |
| Runtime monitor | `GET /api/runtime/monitor`; Scheduler route order/channels/tasks, Nanobot bridge, Plan counts/DAG rows, Blackboard summary, AgentTeam placeholder. | `observability_runtime_business_flow_20260513.md` | Read-only Web surface; not an App DTO. |
| Runtime Flow upgrade | `GET /api/runtime/flow`, `GET /api/runtime/flow/changes`, `GET /api/runtime/flow/stream`, `GET /api/runtime/hitl/pending`, `POST /api/runtime/hitl/draft-decision`, `POST /api/runtime/hitl/apply-decision`, React swimlane/DAG workspace. | `observability_runtime_business_flow_20260513.md` | First slice implemented; Web-only read model/HITL first, core candidates staged before shared promotion. 2026-05-16 adds a read-only SSE wrapper over `runtime_flow_delta_v1`; receipt/action streams remain separate. |
| Collaboration Flow workbench | `GET /api/runtime/capabilities/catalog`, `GET/POST/DELETE /api/runtime/workflows/drafts`, `GET /api/runtime/workflows/drafts/{workflow_id}`, `POST /api/runtime/workflow/plan-draft`, `POST /api/runtime/workflow/result-contract`, `GET/POST/DELETE /api/runtime/workflow/result-intake`, `POST /api/runtime/workflow/run`, `GET/POST/DELETE /api/runtime/workflow/action-gates`, `POST /api/runtime/workflow/action-gates/decision`, React Runtime capability catalog/search/filter, durable Web workflow draft registry, trigger draft/fire from inserted nodes, workflow draft -> HITL Plan import, result-route preview/intake, whole-workflow preview/run, trigger/message action gates, result-intake cleanup, and L0/L1/L2/C3/C4/I0 interaction-mode filtering. | `collaboration_flow_workbench_ssot_20260517.md`, `_tmp/collaboration_flow_workplan_20260517.md` | 2026-05-17 first through seventh slices implemented after workflow/HITL/agent research. Catalog classifies true routes by kind, execution policy, ascent channel, interaction module, information tag, interaction mode, Plan/Nanobot compatibility, result destination, and true-connection state. `plan-draft` creates real HITL Plans only for Nanobot-compatible capabilities and can now import by saved `workflow_id`; compatible steps carry `workflow_result_contract_v1` result routes in Plan inputs. `result-intake` consumes that contract or a saved workflow and can operator-stage reviewed results to IntentWorkspace as `workflow_result` rich reports while blocking Graphiti/L2-B/materialization destinations; individual intake rows can now be deleted through the public Web/app-monitor route for smoke cleanup. `workflow/run` composes existing true routes: trigger nodes go to DSG trigger draft/fire receipts, Nanobot-compatible nodes go to Plan/HITL, and unsupported nodes are skipped. Action gates persist Web-only pending trigger and `message_check` actions, let operators preview/apply/reject/cancel, and execute only through existing trigger/message routes under operator mode. React Runtime can search/filter by interaction mode, save/load/delete Web-only workflow drafts, preview routes, intake results, delete intake entries, run the whole draft, create action gates, and operate pending gates; storage redacts likely secret/token/API-key fields. Local 7893 true smoke with ECS Graphiti proxy proved capability catalog, durable draft save/list/get/delete, workflow-id Plan import, whole-workflow run preview, trigger draft, Graphiti status, `noble_etiquette` subgraph search, `selected_hits` import-plan preview, action-gate preview/operator reject cleanup, and result-intake IntentWorkspace staging. ECS `8790` app-monitor exposes the same runtime workflow subset; remote smoke after `f749acc` proved action-gate real trigger publish, and remote smoke after `f942e2a` proved result-intake preview plus operator IntentWorkspace staging with ledger entry `wri_f7936482c893`. Shared Scheduler workflow storage, Scheduler-enforced result routing, C4/I0 safe-turn/interrupt execution, and shared trigger/message HITL promotion remain future work. |
| Trigger and message lab | `GET /api/dsg/triggers/catalog`, `POST /api/dsg/triggers/draft-event`, `POST /api/dsg/triggers/fire-event`, `POST /api/google/messages/check`, `POST /api/google/messages/push-test`. | `observability_runtime_business_flow_20260513.md` | Web-only receipt surface; real fire publishes to `CH_DSG_EVENTS` only with explicit operator mode. React Runtime preset buttons now obey the global Settings `Mode`: the browser defaults to real operator testing, while preview mode still calls draft/dry-run paths. Gmail check uses Scheduler/Nanobot dispatch; message results now enter L1.5 as `GOOGLE_MESSAGE` observations. |
| Trigger/Awareness taxonomy | No new route; documents `TriggerOutcome`, Photo/Evidence Awareness, ContextInjector C3/C4 policy, and future clustered trigger rendering. | `observability_runtime_business_flow_20260513.md`, `.cursor/memory/architecture/Interface/goslo_trigger_awareness_taxonomy_20260515.md` | Classifies trigger families separately from delivery/body-feel levels. Legacy `notify_gemini` is now treated as C3 by default; C4/interrupt remains explicit future policy. |
| Live memory snapshot | `GET /api/app/live-state?limit=...`, `GET /api/memory/live-state/changes?since=...&limit=...`, `GET /api/memory/live-state/stream?since=...`, `GET /api/memory/blackboard/activity?limit=...`; grouped Blackboard key rows, grouped IntentWorkspace ref rows, Ref registry, React Flow L2-B graph/detail panel, bounded changed-since events, bounded SSE memory deltas, and bounded Blackboard activity rows. | `memory_graph_workspace_business_flow_20260513.md` | Implemented as bounded active-view renderer with filters, new-node diff highlight, and soft Intent/Ref-to-L2-B links when linked nodes exist. 2026-05-15 Memory changed-since V1 lets React skip no-op broad snapshot repainting. 2026-05-16 adds a Web-only read SSE wrapper over the same `memory_runtime_delta_v1` event shape; receipt stream remains separate. |
| L1.5/L2-B operator drafts | `GET /api/l15/pool`, `GET /api/l15/obsidian-vault/scan`, `POST /api/l15/obsidian-vault/import-draft`, `POST /api/l15/obsidian-vault/import-plan`, `POST /api/l15/obsidian-vault/import`, `POST /api/l15/bucket-op/draft`, `POST /api/l15/bucket-op`, `POST /api/l15/obsidian-node/draft`, `POST /api/l15/obsidian-node`, `POST /api/l2b/node/draft`, `POST /api/l2b/node`, `POST /api/l2b/node/delete`, `POST /api/l2b/edge/draft`, `POST /api/l2b/edge`, `POST /api/l2b/edge/update`, `POST /api/l2b/edge/delete`, `POST /api/l2b/graph-policy/import-draft`, `POST /api/l2b/subgraphs/draft`, `POST /api/l2b/subgraphs/context`, `POST /api/l2b/transforms/draft`, `GET /api/l2b/analysis/health`, `POST /api/refs/binding/draft`, `POST /api/refs/binding/apply`, `GET /api/memory/identity-ref-index`, `POST /api/memory/identity-ref-index/draft`, `POST /api/memory/identity-ref-index/apply`, `POST /api/memory/identity-ref-index/graphiti-ref/draft`, `POST /api/memory/identity-ref-index/graphiti-ref/apply`, `POST /api/memory/identity-ref-index/verify`, `POST /api/memory/identity-ref-index/resolve-graphiti`, `POST /api/memory/identity-ref-index/apply-graphiti-edge`, `POST /api/memory/identity-ref-index/ref-scan-plan`, `POST /api/memory/identity-ref-index/ref-scan-dispatch`, `GET /api/memory/identity-ref-index/ref-scan-results`, `GET /api/photos/asset/{day}/{photo_id}`. | `memory_graph_workspace_business_flow_20260513.md`, `graphiti_l2b_ref_identity_design_20260517.md` | Backend routes remain receipt/audit gated. Node create/update routes through `L15Pool.admit(Observation(source=USER_EXPLICIT))`; delete uses `L15Pool.evict`; real edge connect/update/delete requires operator mode. Edge update/delete identify runtime edges by endpoints plus optional kind/source filters instead of exposing RustWorkX edge indexes. WEB-016 adds CORE-013 candidate-only graph policy drafts for import destination, subgraph overlays, live bounded subgraph context, transforms, and read-only health metrics; no apply route or shared DTO promotion yet. React Memory Canvas now exposes policy/overlay/context/transform/health controls plus the global Settings `Mode`: default real operator testing sends direct Node/Edge/bucket actions to apply routes with `dry_run=false` / `operator_mode=true`, while preview mode keeps them as dry-run receipts. Source Board Graphiti/Obsidian/Google can all preview a unified source -> L1.5 -> L2-B import plan before any operator apply; import-plan receipts are forced draft-only, and empty source selections return `policy_skipped_reason` with no destination policy. L2-B fallback de-dup uses stable source IDs first, then `NodeKind + exact label`; visible labels/tags are not graph-wide unique identity keys. Session RefBinding now has CORE-006 draft/apply receipts that update only the session registry. CORE-015 IdentityRefIndex has a file-backed Web prototype for canonical UUID equivalence and mutable ref locators, deterministic health verification for local paths, unknown URL/remote locators, supplied Graphiti/Obsidian UUID status maps, `merge_report` / `conflicts[]` receipts for duplicate Graphiti/L2-B/ref signals, semantic M14 Graphiti-ref write-back draft/apply routes that bind GraphitiRecordRef to ExternalRefRecords and draft RefMoveEvents/audit Episodes, a read-only GraphitiResolver preview that resolves fact endpoints, an operator-only `apply-graphiti-edge` route that materializes already-resolved Graphiti facts through the existing L2-B edge writer with raw metadata preserved, a plan-only `ref-scan-plan` route for Nanobot/MCP/git ref health checks, an operator-gated read-only `ref-scan-dispatch`, and a read-only `ref-scan-results` ledger view. M10 live smoke proved Scheduler -> Nanobot -> Scheduler ledger over ECS Redis DB15. M11 adds opt-in URL HEAD and Graphiti search-probe checkers plus an ECS-local stat/hash checker guarded by ECS-side confirmation; live smoke with `--remote-checks` returned URL 404 as `missing`, Graphiti search-probe as `unknown`, ECS as guarded `unknown`, local path ok/hash, and no automatic write-back. It preserves collisions without auto-rebinding existing records and does not write Graphiti/FalkorDB, Obsidian, ECS files, manifests, RefIndex health, or App DTOs. Photo thumbnails are read-only cache-root previews and do not expose arbitrary local paths. |
| Source Board CORE-015 controls | Existing Graphiti Source Board controls inside 7893 static Console | `web/console_app/src/App.tsx`, `api.ts` | The Graphiti card now loads IdentityIndex counts, runs deterministic ref verification, drafts a `Ref Scan Plan` Nanobot/MCP/git contract, optionally requests `Remote probes`, dispatches read-only `ref_scan` tasks through Scheduler/Nanobot, reads `memory_ref_scan_result` ledger rows, resolves Graphiti edge drafts, previews `apply-graphiti-edge`, operator-materializes selected resolved facts into L2-B through CORE-015, and surfaces M14 Graphiti Ref Write-back controls for generated fact/entity/episode Ref drafts. Operators can preview RefIndex write-back, edit Ref ID/kind/locator, and explicitly opt into Graphiti audit Episode writes. M15 adds a separate Graphiti SearchConfig Recipe selector plus Node label / Edge type filter inputs, so Web can combine local multi-hop Strategy with Graphiti combined/edge/node/community retrieval recipes before import. M16 backend receipts attach `graphiti_bundle`; M17 renders that bundle directly in the Source Board with fact/entity/episode/community counts, search/lookup summary, projection policy, import overlay, and sample rows. M19 adds `L2-B transform preview` rows from the import overlay, including preview node/edge samples and rustworkx ephemeral-index policy. M10 adds a repeatable backend smoke script proving that ledger path against ECS Redis DB15; M11 extends it with `--remote-checks` for URL HEAD and Graphiti search-probe validation. `npm run build` writes the updated controls to `web/console_dist`, so no separate Web Console port is required. |
| Graphiti console | `GET /api/graphiti/status`, `POST /api/graphiti/search`, `POST /api/graphiti/episode/draft`, `POST /api/graphiti/episode`, `POST /api/graphiti/lookup`, `POST /api/graphiti/subgraph/search`, `POST /api/graphiti/subgraph/export-draft`, `POST /api/graphiti/subgraph/import-plan`, `POST /api/graphiti/subgraph/export`; preview/apply split. | `graphiti_management_business_flow_20260513.md` | Implemented safe seed plus `arknights_test`/DeepSeek config and Graphiti-to-L1.5 subgraph export receipts. React Source Board supports selected-hit subgraph preview, inline Export plan, `edge_drafts`, `graphiti_raw_envelopes`, CORE-015 `identity_ref_drafts`, unified import plan with CORE-013 destination policy, tolerant search limit parsing, normalized partition provenance, empty-hit `policy_skipped_reason`, and an `Import to L1.5` action that now obeys global Settings `Mode` (default real operator testing, preview mode dry-run). M12 adds Strategy / Depth / Focal UUID controls and an `iterative_hybrid` mode that performs real follow-up Graphiti searches and returns a `search_plan`; GOSLO Intent `query_memory` uses the same subgraph path. M13 adds exact Graphiti UUID lookup/enrichment and ECS 8790 write/export proxying. M15 adds SearchConfig recipe/filter controls and receipts that show whether low-level `_search` or fallback public search ran. M16 adds `graphiti_bundle` on search/export/import-plan receipts: raw envelopes, fact/entity/episode/community sections, lookup payloads, search plan/config, edge/ref drafts, and L2-B import overlay are preserved together. M18 deploys this adapter to ECS app-monitor, so 8790 itself and 7893 passthrough now prove `_search`, bundle counts, UUID lookup, and import overlay against real Graphiti data. M19 adds a preview-only Graphiti bundle -> L2-B/RustWorkX projection inside import-plan receipts, preserving raw Graphiti payloads and marking rustworkx indices as non-persistent preview handles. 2026-05-17 live partition fix adds `noble_etiquette` to the local allowlist, Source Board selector, and GOSLO `query_memory` routing so 7893 no longer normalizes that test partition back to `goslo`; live smoke shows proxy/status route accepts the partition, while sampled etiquette queries currently return 0 hits from 8790. If the lightweight 7893 BFF lacks local Graphiti dependencies, status/search can read through an explicit `PARROT_WEB_CONSOLE_GRAPHITI_URL` / `PARROT_GRAPHITI_REMOTE_URL` app-monitor target such as local/ECS `8790`; this proxy is opt-in. Full Graphiti/FalkorDB surgery and direct L2-B Edge writes remain future operator work. |
| Google Calendar source import | `POST /api/google/calendar/fetch`, `GET /api/google/calendar/results`, `POST /api/google/calendar/preview`, `POST /api/google/calendar/import-draft`, `POST /api/google/calendar/import-plan`, `POST /api/google/calendar/import`; Scheduler/Nanobot fetch request or raw event -> normalized CalendarTrigger event -> `GOOGLE_CALENDAR` Observation -> optional L1.5 admit. | `memory_graph_workspace_business_flow_20260513.md`, `observability_runtime_business_flow_20260513.md` | Preview/plan buttons remain explicit previews; fetch/import execute buttons obey global Settings `Mode` and default to real operator testing. Calendar import preserves event time fields during L1.5 import, returns Web-only mapping rows plus a unified CORE-013 destination plan, reads a bounded Scheduler trigger-result ledger without browser-held Google OAuth, and marks cancelled/deleted rows as historical tombstone EVENT nodes rather than evicting by default. |
| Time-aligned evidence debug | `GET /api/vision/evidence/status`, `GET /api/vision/evidence/timeline`, `POST /api/vision/evidence/request`, `POST /api/vision/evidence/stage-hint`, `POST /api/vision/evidence/memory-draft`, `POST /api/vision/evidence/frame-cache/upload`, `POST /api/vision/evidence/tool-lifecycle`, `GET /api/vision/evidence/screen-share-smoke`, `GET /api/vision/evidence/{evidence_id}`, `POST /api/app/test/visual-attention`; React Runtime Time/Evidence panel. | `observability_runtime_business_flow_20260513.md`, `memory_graph_workspace_business_flow_20260513.md`, `.cursor/memory/architecture/Interface/time_aligned_evidence_interface_20260515.md` | Web/backend-first CORE-012 prototype now has an Interface SSOT for implemented backend/Web behavior, without promoting Unity/App top-level DTO fields. Consumes optional ECP payload/meta `timebase`; records photo/snapshot/attention/frame rows; `identify_object` requests stored evidence instead of old snapshot RPC and will not attach a missing BBox/Focus ref to the room's newest unrelated frame. `parrot.brain.vision.frame_cache.record_livekit_frame_bytes()` is the storage-backed producer entry point, the Web upload route is only an operator/debug ingress, and `parrot.brain.vision.livekit_sampler` is the Brain room-scoped low-FPS LiveKit track consumer. `/api/vision/evidence/status` includes secret-free `livekit_sampler` status plus frame-cache/sampler freshness fields (`latest_frame_age_ms`, `latest_frame_fresh`, per-track summaries including `publication_source`), and `src/scripts/smoke_livekit_frame_sampler.py` is the manual real-room video ingestion smoke. The sampler recognizes camera and screen-share publications, including `SOURCE_SCREEN_SHARE`; React Runtime now prefers LiveKit `setScreenShareEnabled(true)` for screen-share publish, falls back to manual `getDisplayMedia + publishTrack`, and its `检查采样` button calls server-side read-only smoke verdict `GET /api/vision/evidence/screen-share-smoke`, which requires a single fresh candidate row with screen-share-looking source hints, renders the verdict inline with next steps, and does not write pending evidence rows on failure. `parrot.brain.vision.evidence_image` prepares local stored images/crops for VLM describe, letting `identify_object` enrich L0/L1 search without inline image transport. `parrot.brain.vision.evidence_awareness` stages `visual_evidence_hint` refs into IntentWorkspace and writes `transient/evidence_awareness_notice`; Photo Awareness writes `transient/photo_awareness_notice` for App menu notification levels; `ContextInjector` consumes allowed evidence/photo notices as C3 chat-context hints and deliberately keeps C4/speech as a later safe-turn policy. WEB-015.12 adds the conservative `attention.threshold.crossed` auto bridge: nearest stored frame/photo is staged as `visual_evidence_hint` or recorded as a pending request, with no capture, no L2-B write, and no direct speech/interrupt. WEB-015.14 adds the CORE-014 BBox/MAG lifecycle backend/App V1 surface: `/api/app/visual-tool/event`, `/api/app/visual-tool/asset/{asset_id}`, ECP `visual_tool.lifecycle`, and Web debug `/api/vision/evidence/tool-lifecycle`; BBox confirm defaults to C3, MAG confirm defaults to IntentWorkspace-only, and C4 requests are downgraded. WEB-015.9 adds `memory-draft`, a preview-only Evidence -> L1.5/Ref/L2-B promotion receipt with no apply route until CORE-012/CORE-006 review. Live Unity/Web screen-share/LiveKit video smoke, reference-image VLM compare, and C4 safe-turn review remain WEB-015 follow-ups. |

## Completion Report: Trigger/L1.5/L2-B Draft Slice

Date: 2026-05-13
Status: implemented, documented, and smoke-tested in the local browser
Scope: Web Console only; no Unity/App DTO changes; no direct core SSOT edits.

Completed:

- Added the Web-only management BFF in `src/parrot/web_console/memory_ops.py`
  and mounted its routes from `src/parrot/web_console/server.py`.
- Added Runtime Monitor Trigger Lab for trigger catalog, draft/fire receipts,
  Gmail `message_check` dispatch drafts, and synthetic `message_push` tests.
- Added Memory Graph Operator Workbench for L1.5 pool inspection, bucket op
  drafts, Obsidian three-profile setting-node drafts, L2-B node drafts/delete,
  and L2-B edge drafts.
- Kept dangerous writes behind explicit `operator_mode=true` and
  `dry_run=false`. As of 2026-05-17, the React Web Console has a global
  Settings `Mode`: default is real operator testing for execute/import/fire
  buttons; preview mode is still available for dry-run receipts.
- Browser-smoked the restarted `http://127.0.0.1:7893/` server after route
  load; trigger draft and L2-B node draft receipts returned successfully.

Verification:

- `node --check web\console\assets\app.js`
- `uv run python -m py_compile src\parrot\web_console\memory_ops.py src\parrot\web_console\server.py`
- `uv run pytest tests\test_web_console\test_web_console_server.py tests\test_dsg\test_obsidian_true_connection.py tests\test_dsg\test_calendar_true_connection.py tests\test_dsg\test_trigger_outcome_v2.py -q`
- Result at this checkpoint: `29 passed`.

Audit result:

- Routes are indexed in this README and detailed in the active business files.
- No Web-only operator/admin fields were added to App DTOs.
- No new scattered business docs were created for this slice.
- `PARROT_ORCH_SECRET`, LiveKit secrets, and Google credentials are not exposed
  through frontend JSON or DOM.
- 2026-05-14 cleanup: `MessageNotificationTrigger` now returns
  `TriggerOutcome.commit_observations` and uses the new
  `ObservationSource.GOOGLE_MESSAGE` / `BucketKind.GOOGLE_MESSAGE` path. It no
  longer writes message EVENT nodes directly to L2-B.
- 2026-05-14 cleanup: `TriggerRunner.fire_event()` now reaches `ON_DEMAND`
  triggers as well as `EVENT_DRIVEN` triggers, so Web draft/fire events can
  exercise scene/roleplay triggers through the same bus-facing path.
- 2026-05-14 cleanup: DSG trigger source files now use `TriggerOutcome`
  directly. `TriggerResult` remains only as a tested compatibility alias.

## Completion Report: React Runtime Flow / Memory Workspace First Slice

Date: 2026-05-13
Status: implemented first vertical slice; visual polish and browser smoke are
complete for this checkpoint, with follow-up polish still tracked by WEB-011
and WEB-012
Scope: Web Console only; no Unity/App DTO changes; no direct core SSOT edits.

Completed:

- Added React + Vite source under `web/console_app/` and build output under
  `web/console_dist/`.
- Updated the BFF static root so the same Web Console service prefers the React
  build when `web/console_dist/index.html` exists and falls back to the old
  vanilla console when it does not.
- Added Web-only runtime-flow read model in
  `src/parrot/web_console/runtime_flow.py`.
- Added Runtime Flow routes:
  `GET /api/runtime/flow`, `GET /api/runtime/flow/changes`,
  `GET /api/runtime/hitl/pending`,
  `POST /api/runtime/hitl/draft-decision`, and
  `POST /api/runtime/hitl/apply-decision`.
- Added first backend capability wiring so Plan steps can dispatch through
  Scheduler/Nanobot task metadata and Nanobot result/timeout metadata can report
  back into the Plan registry.
- Fixed the Plan dispatch failure edge case: a dispatch exception now fails the
  step and Plan instead of leaving the step stuck in `DISPATCHED`.
- Fixed the unsupported Plan tool edge case: Plan steps now validate against
  the Scheduler Nanobot task catalog before dispatch, so an unsupported tool
  fails fast instead of being routed away from the Plan result flow.
- Fixed the Runtime Flow changed-since edge case: no-op polls now return
  `changed=false` instead of advancing sequence forever.
- Fixed the Runtime Flow graph-read-model edge hygiene: the stable signature is
  order-insensitive for nodes/edges/events, and graph edges whose endpoints are
  outside the Runtime Flow read model are pruned before React Flow rendering.
- Fixed HITL draft validation for missing Plan ids.
- Fixed HITL draft validation for invalid Plan-state/action pairs; dry-run
  receipts now expose `plan_state` and `valid_actions_for_state` instead of
  promising an action that apply would reject.
- Fixed HITL pending gate drift: visible gate buttons now reuse the same
  state-aware Plan policy as draft/apply validation, and non-Plan gates return
  explicit `unsupported_hitl_target` receipts until trigger/message HITL is
  designed.
- Added Web-only CORE-010 trace hints to Runtime Flow nodes/edges/events:
  `trace_id`, `parent_span_id` where applicable, and redacted `payload_ref`.
- Fixed empty Plan execution settlement so a zero-step Plan completes instead
  of staying active/executing forever.
- Added React Memory Graph Workspace with React Flow L2-B canvas, L1.5 bucket
  board, node/edge dry-run action buttons, detail drawer, and receipts.
- Added React Runtime Flow Workspace with swimlane/DAG graph, event tape,
  manual trigger buttons, HITL cards, and receipt rail.
- 2026-05-14 React UI continuation: Memory Graph now supports direct
  React Flow drag/connect edge drafts with frontend-only preview edges, and
  Runtime Flow now uses a grouped trigger palette plus receipt timeline for
  message, LLM, scheduler, calendar, scene-switch, and roleplay dry-runs.
- 2026-05-14 React UX continuation: Memory Graph now shows L1.5 pool health,
  capacity pressure, current scene, per-bucket node meters, frozen/open state,
  and last activity. Runtime Flow now reads `/api/dsg/triggers/catalog` and
  renders registered trigger chips by trigger kind next to the manual presets.
- Fixed React Runtime Flow UI drift: Chinese labels now render through stable
  zh/en copy, the live pill shows the backend refresh interval, Runtime nodes
  are arranged by lane-local rows, and HITL cards render action buttons from
  backend `options` / `valid_actions_for_state`.
- Added Web-only typed Runtime Flow models in
  `parrot.web_console.runtime_flow_models`. Runtime Flow rows, snapshots,
  changed-since envelopes, HITL gates, and HITL receipts now serialize through
  this typed layer while keeping the existing route JSON compatible.

Verification at this checkpoint:

- `uv run python -m py_compile src\parrot\web_console\runtime_flow.py src\parrot\web_console\runtime_flow_models.py src\parrot\web_console\server.py src\parrot\brain\plan\plan_registry.py src\parrot\scheduler\service.py`
- `uv run pytest tests\test_brain\test_plan_lifecycle.py tests\test_web_console\test_web_console_server.py -q`
- `cd web\console_app; npm run typecheck`
- `cd web\console_app; npm run build`
- Browser smoke on `http://127.0.0.1:7893/`: React dist served, Memory and
  Runtime pages navigated, LLM trigger draft produced a receipt, zh/en toggle
  worked, and frontend console errors stayed at zero.
- Latest React smoke: Runtime trigger palette and scene-switch preset visible,
  LLM dry-run produced `dsg.trigger.draft_event` with matched trigger text,
  Memory node draft produced an `l2b.node.draft` receipt and preview node,
  Chinese copy rendered normally, and console errors stayed at zero.
- Latest React UX smoke: Memory page shows L1.5 pool health labels
  (`池健康`, `压力`, `最后活动` in zh); Runtime page shows registered trigger chips including
  `event_driven` and `on_demand`; console errors stayed at zero.
- Latest bugfix smoke: Runtime action groups are localized in zh
  (`消息`, `运行`, `模式`), the LLM dry-run button produced a receipt, and console
  errors stayed at zero. Memory graph placeholders are no longer draftable
  L2-B edge endpoints; node/edge previews only render after success receipts.
- Latest L1.5 smoke: React Memory includes an Obsidian setting-node draft card
  for `daily`, `roleplay`, and `ref`. Daily draft produced a
  `l15.obsidian_node.draft` receipt, and `ref` without UUID now shows a warning
  and produces the expected `ref_profile_requires_obsidian_uuid` local failure
  receipt with zero console errors.
- Latest Obsidian draft bugfix: whitespace-only labels now normalize to
  `Web Console setting`, so generated `obsidian_note_key` values do not end in
  an empty label segment. Local frontend receipts now include a random suffix so
  rapid repeated guard failures do not collide in the receipt timeline.
- Latest Web route focused result: `17 passed` for
  `tests/test_web_console/test_web_console_server.py`.
- Latest combined focused result: `48 passed`.
- Latest HTTP smoke after service restart:
  `/api/runtime/flow/changes?since=<current sequence>` returns
  `changed=false`.

Audit result:

- Web-only runtime/HITL routes are documented here and in
  `observability_runtime_business_flow_20260513.md`.
- Shared/core implications stay in CORE-010 and CORE-011; no core SSOT file was
  edited.
- Frontend code does not embed `PARROT_ORCH_SECRET`, LiveKit secret, or Google
  credentials.
- Remaining risk: React UI is still a first vertical slice. Selected-edge
  reconnect/retarget, richer trigger sample editing, operator execution guard
  copy, and Evidence Board polish remain future WEB-011/WEB-012 slices.

### Implemented Trigger/L1.5/L2-B Route Matrix

| Endpoint | Mode | Write path | Notes |
|:--|:--|:--|:--|
| `GET /api/dsg/triggers/catalog` | read | none | Lists registered trigger names, kinds, interval, and sample event hints. |
| `POST /api/dsg/triggers/draft-event` | draft | none | Builds a Redis DSG event receipt and reports matched trigger names. |
| `POST /api/dsg/triggers/fire-event` | dry-run/operator | Publishes to `CH_DSG_EVENTS` only with `operator_mode=true` and `dry_run=false`. | Does not call Brain trigger singletons from the Web process. |
| `POST /api/google/messages/check` | dry-run/operator | Dispatches Scheduler `message_check` only with explicit operator execution. | Gmail/OAuth remains outside the browser; Nanobot/MCP owns the actual check. |
| `POST /api/google/messages/push-test` | dry-run/operator | Publishes synthetic `message_push` through `CH_DSG_EVENTS` only in operator execution. | Used to test message trigger routing. |
| `GET /api/l15/pool` | read | none | Returns Web management snapshot for health, buckets, refs, timeline, and scene. |
| `POST /api/l15/bucket-op/draft` | draft | none | Validates/normalizes bucket operations into a receipt. |
| `POST /api/l15/bucket-op` | dry-run/operator | `L15Pool.apply_bucket_op`. | Dangerous real action requires operator mode. |
| `POST /api/l15/obsidian-node/draft` | draft | none | `daily`/`roleplay` allow UUID-free setting nodes; `ref` requires an Obsidian UUID. |
| `POST /api/l15/obsidian-node` | dry-run/operator | Publishes normalized Obsidian event through `CH_DSG_EVENTS`. | Uses the trigger/L1.5 route, not direct L2-B mutation. |
| `POST /api/l2b/node/draft` | draft | none | Produces a `USER_EXPLICIT` observation receipt for create/update. |
| `POST /api/l2b/node` | dry-run/operator | `L15Pool.admit(Observation(...))`. | Keeps Ingest/L1.5 as the normal write gate. |
| `POST /api/l2b/node/delete` | dry-run/operator | `L15Pool.evict`. | Web operator action; default is preview receipt. |
| `POST /api/l2b/edge/draft` | draft | none | Normalizes `SemanticEdge`-shaped source/target/kind/strength/source/meta; rejects same-node self-edge drafts. |
| `POST /api/l2b/edge` | dry-run/operator | `L2BGraph.connect`. | Real edge connect requires operator mode and returns an audit receipt. |
| `GET /api/photos/asset/{day}/{photo_id}` | read | none | Serves existing photo cache assets from `PARROT_PHOTO_CACHE_ROOT/day/photo_id.jpg` only after day/photo_id validation and cache-root containment checks. |
| `POST /api/l2b/graph-policy/import-draft` | draft | none | CORE-013 candidate-only import destination policy: workspace-only, index pointer, isolated compartment, main graph promotion, or connect-by-rule. |
| `POST /api/l2b/subgraphs/draft` | draft | none | CORE-013 candidate-only foldable/isolated subgraph overlay preview; no persistent overlay store yet. |
| `POST /api/l2b/transforms/draft` | draft | none | CORE-013 candidate-only graph transform preview; includes wrap/compare/draft-link/promote/split/tombstone/send-to-LLM options. |
| `GET /api/l2b/analysis/health` | read | none | Read-only graph health preset: node/edge counts, orphan Nodes, WCC count/largest WCC, and kind/bucket/source distributions. |

## Drift Audit

- No implemented Web-only route has been intentionally added to Unity/App DTOs.
- Business-interface files now cover every implemented Web route. The top
  ledger indexes the full route groups, while the table above tracks the
  operator/draft memory-management routes that were most likely to drift.
- The current risk is product focus, not undocumented routes: the UI has several
  useful smoke panels, and the Memory Graph now has a first visual renderer with
  operator drafts, but WEB-011 should replace dense component stacking with a
  larger visual operations cockpit before adding more broad admin panels.

### Final Compliance Audit: 2026-05-14 React Checkpoint

- Actual BFF route list was reconciled against this README and the active
  Runtime/Memory/Graphiti business files. `web/console_dist/` hosting and
  `GET /api/memory/blackboard/activity` are now indexed at the top level.
- The latest Web work stays inside `src/parrot/web_console/`,
  `web/console_app/`, `web/console_dist/`, `tests/test_web_console/`, and this
  Web business-interface directory. Unrelated App/Unity worktree files were not
  touched by this audit.
- No App/Unity DTO received Web-only operator fields. CORE-010/CORE-011 remain
  candidate-review items until the user approves shared promotion.
- Secret scan found only generic `PARROT_ORCH_SECRET` references and fake test
  values. The raw local secret, LiveKit secrets, and Google credentials are not
  present in React source/dist or Web business docs.
- Verification at this checkpoint: Web route tests `17 passed`; React
  typecheck/build passed; Memory browser smoke produced expected receipts with
  zero console errors.

### WEB-011.1 Checkpoint

- Memory Graph now has a first cockpit shell in `web/console/`: source rail,
  larger L2-B canvas, selected-node inspector/actions, edge draft controls,
  receipt stream, and advanced Obsidian draft drawer.
- L1.5 bucket cards now include freeze/unfreeze/clear quick draft buttons that
  reuse the existing bucket draft route.
- React Memory now exposes the existing Obsidian setting-node draft route as a
  compact card. It is receipt-only, keeps `daily`/`roleplay` UUID-free, and lets
  the frontend guard `ref` drafts that omit an Obsidian UUID before calling the
  BFF.
- No route matrix changes were made in this slice. Existing L1.5/L2-B/edge
  routes remain the interface surface.
- Verification signal: `node --check web\console\assets\app.js`, clean
  duplicate-id scan, and in-app browser Memory smoke with no console errors.
- Open follow-up: WEB-011.2/011.3 continue from this shell toward stronger live
  rendering and direct graph operations.

### WEB-011.5 Checkpoint

- Runtime Monitor now has a visible trigger palette for message check/message
  push, LLM context push, scheduler tick, calendar test, scene switch,
  roleplay-open, and custom DSG event drafts.
- No new routes were added. Message actions continue through Nanobot Web routes;
  other presets call the existing DSG trigger draft route.
- React continuation replaced the single raw receipt block with a receipt
  timeline so operators can see the last dry-run results without opening a
  dense JSON panel first.
- React continuation also reads the existing trigger catalog route and shows
  kind-grouped registry chips, so operators can compare manual presets with
  real registered `startup`, `periodic`, `event_driven`, and `on_demand`
  triggers before firing anything.
- Verification signal: `node --check web\console\assets\app.js`, clean
  duplicate-id scan, and in-app browser Runtime smoke with no console errors.

### WEB-011.3/011.6/011.7 Checkpoint

- Empty L2-B canvas state now renders a DSG compartment map for Blackboard,
  IntentWorkspace, Refs, L1.5, and L2-B instead of a mostly empty grid.
- L2-B node draft/dry-run receipts now create a frontend-only ghost node preview
  on the canvas. This preview is renderer state only; it is not persisted and
  does not change the BFF route contract. The receipt area includes an explicit
  `Clear Preview` control.
- Preview nodes are now selectable in the same inspector path as persisted
  L2-B nodes, and staged edge draft receipts draw preview edges when both
  endpoints are visible.
- The central canvas now has a local action bar for create preview, use
  selected, set Edge From/To, draft edge, and clear preview; it reuses existing
  draft/dry-run routes and does not change the BFF route matrix.
- `Clear Preview` also clears stale selected preview nodes and `draft:` UUIDs
  from target/delete/edge fields so later drafts cannot accidentally reuse a
  removed ghost endpoint.
- Same-node edge drafts are rejected in the Web BFF and guarded in the frontend
  so a zero-length invisible self-edge cannot return a success receipt.
- Placeholder DSG compartment nodes are not valid L2-B edge endpoints, and
  failed node/edge draft receipts no longer create ghost preview nodes or lines.
- Frontend action failures are converted into local failure receipts instead of
  unhandled browser promise errors.
- Blackboard and IntentWorkspace rows now render as grouped status-light cards.
- Verification signal: `node --check web\console\assets\app.js`, clean
  duplicate-id scan, and in-app browser Memory smoke. L2-B preview smoke showed
  two `.memory-svg-node.preview` nodes, one `.memory-edge.preview`, selectable
  preview detail, and zero console errors. Canvas-toolbar smoke showed one
  preview node created from the center-stage action bar, selection pill update,
  toolbar clear to zero previews, and zero console errors. Cleanup regression
  smoke confirmed that drafting an edge after clearing previews does not
  resurrect removed `draft:` endpoints. Self-edge smoke confirmed that using
  the same selected node for From and To creates no preview edge and reports a
  local guard receipt with zero console errors.

### WEB-011.19 Checkpoint

- Added Web-only Memory changed-since polling route:
  `GET /api/memory/live-state/changes?since=...&limit=...`.
- The route wraps the existing `/api/app/live-state` read model but keeps a
  separate Web sequence based on stable memory content, not on every read.
- No-op polls return `changed=false`, an empty event list, and no snapshot, so
  React Memory can avoid broad canvas repainting when L2-B, Blackboard,
  IntentWorkspace, and Ref content has not changed.
- The route emits a small bounded event list for operators and marks CORE-009 /
  CORE-010 only as shared candidates. No App/Unity DTO was changed.
- This remains polling/diff, not SSE/WebSocket. The future full-screen L2-B
  monitor should reuse this sequence/event shape if it moves to SSE/WebSocket.
- Local smoke after restarting the stale 7893 process confirmed the endpoint
  returns `changed=false` with `snapshot=null` on no-op follow-up polls, and the
  in-app browser loaded the React Memory page with zero console errors.

### WEB-014.11 Checkpoint

- `Refs/Photos` is now a Source Board tab and a selected-Node read surface.
  The Source Board handles retarget/unresolve drafts through
  `POST /api/refs/binding/draft`; the floating Node inspector only displays
  matching RefBinding, IntentWorkspace, and Photo asset/episode evidence.
- `GET /api/photos/asset/{day}/{photo_id}` is now the Web-only read path for
  thumbnails. It only serves files under the photo cache root and reuses the
  upload-side photo id safety rule.
- The selected-Node Ref/Photo display is renderer/read-model only. It does not
  add a bind/unbind/apply route and does not promote CORE-006 into Unity/App
  DTOs.
- Validation signal: Web route tests `37 passed`, `npm run typecheck`,
  `npm run build`, browser Node-detail smoke with zero console errors, and
  frontend/backend secret scan.

### WEB-014.17 M13 Checkpoint

- Graphiti UUID lookup is now real: `/api/graphiti/lookup` uses partition-
  scoped Graphiti CRUD helpers and subgraph search enriches fact/source/target
  hits with raw Graphiti objects before L1.5 import.
- The existing 7893 Web Console can act as a lightweight BFF while ECS owns
  Graphiti: non-dry-run Episode writes and operator subgraph export proxy to
  8790 when `PARROT_WEB_CONSOLE_GRAPHITI_URL` is set.
- ECS FalkorDB persistence was fixed by mounting `/var/lib/falkordb/data` and
  enabling AOF/noeviction through `REDIS_ARGS`.
- Live smoke after a real FalkorDB restart returned persisted `arknights_test`
  search results through 7893, enriched 16/16 Graphiti UUID objects, and
  executed remote operator export with raw envelopes/edge drafts preserved.

### WEB-014.17 M14 Checkpoint

- Added semantic CORE-015 write-back routes:
  `POST /api/memory/identity-ref-index/graphiti-ref/draft` and
  `/graphiti-ref/apply`.
- The routes bind a reviewed GraphitiRecordRef to ExternalRefRecords, draft
  RefMoveEvents for locator changes, preserve raw Graphiti envelopes, and
  return a Graphiti audit Episode draft.
- Empty locator write-back is filtered: a GraphitiRecordRef can bind identity
  by itself, but ExternalRefRecords and RefMoveEvents are created only when a
  reviewed locator, canonical URI, or content hash exists.
- Default apply writes only the IdentityRefIndex JSON and does not write L2-B,
  Graphiti/FalkorDB, files/ECS paths, manifests, or App DTOs.
- Live canary used real ECS Graphiti `arknights_test`, selected fact UUID
  `0ea2009c-402d-4332-81b4-31fa57e67688`, and persisted a temporary RefIndex
  binding with `identity_count=1` and `ref_count=1`.
- Audit-write canary then enabled `write_graphiti_audit_episode=true`: 60s
  timeout failed cleanly, while
  `PARROT_WEB_CONSOLE_GRAPHITI_TIMEOUT_S=240` wrote the audit Episode to ECS
  Graphiti via 7893 -> 8790 and returned `direct_graphiti_write=true`.
- UI surfacing is now in the 7893 Graphiti Source Board Export plan. After
  `npm run build`, 7893 was restarted with ECS proxy/240s timeout and runtime
  smoke confirmed real ECS search plus search -> export draft ->
  identity_ref_drafts -> Graphiti-ref draft.
- Regression validation: full Web route tests report `82 passed`; runtime smoke
  for the blank-locator case returned `external_payloads=0`,
  `external_records=0`, and `move_events=0`.

### WEB-014.17 M16 Checkpoint

- Graphiti search/export/import-plan receipts now preserve `graphiti_bundle`.
- The bundle separates Graphiti facts, endpoint entities, episode pointers or
  lookup rows, communities, raw envelopes, search plan/config, edge drafts, and
  IdentityRef drafts.
- L2-B adds only projection/import overlay policy: raw Graphiti data is
  preserved, direct Graphiti/FalkorDB writes stay false, and fact-edge
  materialization still requires resolved L2-B endpoint UUIDs.
- Validation signal: full Web route tests report `83 passed`. ECS/app-monitor
  still needs this adapter deployed before live 7893 receipts can prove M15
  `_search` mode plus M16 bundle sections remotely.

### WEB-014.17 M17 Checkpoint

- The existing 7893 Source Board now renders a `Graphiti bundle` panel from
  receipt data instead of requiring operators to open raw JSON details.
- The panel exposes schema/selected count, fact/entity/episode/community
  section counts, strategy/recipe/lookup/search-plan summary, projection policy,
  import overlay destination, and sample rows for facts/entities/episodes.
- Validation signal: `npm run typecheck`, `npm run build`, and Web route tests
  `83 passed`.
- Live canary: restarted 7893 with
  `PARROT_WEB_CONSOLE_GRAPHITI_URL=http://8.216.45.45:8790`; 7893 status showed
  remote proxy, subgraph search returned real Graphiti UUID
  `0ea2009c-402d-4332-81b4-31fa57e67688`, bundle counts
  `facts=3/entities=4/episodes=0/communities=0`, and import-plan overlay
  destination `isolated_compartment`.
- Remaining caveat: ECS 8790 still needs the M15/M16 adapter before live
  receipts can prove remote `search_config.mode=_search`.

### WEB-014.17 M18 Checkpoint

- Fixed app-monitor route parity: ECS 8790 now forwards Graphiti
  `search_recipe`, `node_labels`, and `edge_types`, and exposes
  `/api/graphiti/subgraph/import-plan`.
- Deployed the minimal Graphiti backend file set to ECS with backups, compiled
  remotely, and restarted `parrot-app-monitor`.
- Validation signal: app-monitor tests report `9 passed`; Web route tests
  still report `83 passed`.
- Remote canary: ECS 8790 `/api/graphiti/search` and
  `/api/graphiti/subgraph/search` for `Amiya Chernobog / arknights_test`
  returned `search_config.mode="_search"`, `fallback=false`,
  `low_level="_search"`, first UUID
  `0ea2009c-402d-4332-81b4-31fa57e67688`, and bundle counts
  `facts=3/entities=4/episodes=3/communities=0`.
- Import-plan canary: ECS 8790 returned `import_overlay.destination` as
  `isolated_compartment`, one fact section, four IdentityRef drafts, and one
  L1.5 observation while staying draft-only.
- 7893 passthrough canary now shows the same remote `_search` mode and bundle
  counts; served assets include the `Graphiti bundle` UI.

### WEB-014.17 M19 Checkpoint

- Added preview-only CORE-013 transform kind `graphiti_bundle_projection`.
  `POST /api/l2b/transforms/draft` can now consume a preserved
  `graphiti_bundle` and return `projection_kind=graphiti_bundle_to_l2b_rustworkx_preview`.
- Graphiti import-plan embeds that same transform under
  `data.l2b_transform_preview` and
  `graphiti_bundle.import_overlay.transform_preview`.
- The projection creates pointer-style L2-B preview nodes, `graphiti_fact`
  preview edges, episode support links, Graphiti fact pointers, and a
  `rustworkx.PyDiGraph` topology summary while preserving raw Graphiti payloads.
- Policy remains strict: `direct_l2b_write=false`,
  `direct_graphiti_write=false`, and
  `rwx_idx_policy=ephemeral_do_not_persist`.
- Validation signal: backend `py_compile`, Web route tests `83 passed`,
  frontend `npm run typecheck`, and `npm run build` passed.
- ECS 8790 was updated with `graph_policy.py` and `memory_ops.py`, backed up
  under `codex_backups/m19_graphiti_transform_20260517164126`, compiled, and
  restarted to PID `127087`.
- Remote 8790 and 7893 passthrough canaries both returned true Graphiti
  `_search`, first fact UUID `0ea2009c-402d-4332-81b4-31fa57e67688`, bundle
  counts `facts=3/entities=4/episodes=3/communities=0`, import-plan success,
  L2-B preview counts `nodes=3/edges=1/episode_links=2`, and RustWorkX preview
  counts `nodes=3/edges=3`.

### WEB-014.18 / WEB-016.13 M22 True Graphiti Write Canary

- Fixed ECS Graphiti writes after discovering the provider mismatch: Graphiti
  asks its OpenAI-compatible client for `json_schema` structured output, while
  DeepSeek's current public chat completion docs only list `text` and
  `json_object` response formats. `GRAPHITI_DEEPSEEK_JSON_SCHEMA_ENABLED` now
  gates the DeepSeek path; otherwise status shows requested DeepSeek but uses
  effective Gemini for Graphiti extraction.
- Added `src/scripts/import_noble_etiquette_to_graphiti.py` for deterministic
  PG35123 imports from `Noble Etiquette/pg35123.txt`, with dry-run, apply,
  skip-existing, and remote 8790 write support.
- Deployed `config.py` and `graphiti_client.py` to ECS app-monitor, then
  refreshed `app_monitor_server.py`, `memory_ops.py`, and `graph_policy.py`
  after confirming 8790 had a stale/missing import-plan preview route. Backups
  are under `codex_backups/m22_graphiti_provider_fallback_*`,
  `m22_app_monitor_import_plan_route_*`, and
  `m22_graphiti_import_plan_preview_*`; compile/restart succeeded.
- True write proof: two `noble_etiquette_pg35123_intro_introduction_*`
  Episodes wrote through 8790, direct FalkorDB counts reached `158` nodes /
  `282` edges, and `pg35123` Episodic count is `2`.
- True search/import proof: 8790 and 7893 search
  `Florence Hartley etiquette politeness` returns `11 hit(s), 24 node(s)`;
  8790 import-plan over selected hits returns preview-only
  `graphiti_bundle_to_l2b_rustworkx_preview`, `l2b_nodes=6`, `l2b_edges=2`,
  RustWorkX `nodes=6/edges=6`, raw Graphiti preserved, and
  `direct_l2b_write=false`.

### WEB-016.14 M23 Importer Bugfix

- Fixed the PG35123 importer before full import. The first version cropped the
  text to `INTRODUCTION.` but still skipped TOC chapter headings by magic line
  number, which also skipped the real body `CHAPTER I.` in this file.
- Corrected imports now remove the `CONTENTS.` block and use
  `noble_etiquette_pg35123_v2_*` Episode names/source descriptions, avoiding
  collision with the two earlier buggy canary Episodes.
- Episode bodies now write repo-relative `source_file:
  Noble Etiquette/pg35123.txt` by default, with `--source-file-ref` available
  for future MCP/git-managed locators.
- The CLI now exits non-zero when Graphiti returns JSON with `success=false`.
- Added script tests for chunking, source refs, and failure exit status;
  focused script tests pass (`3 passed`), combined Web/script tests pass
  (`89 passed`). Updated importer was deployed to ECS and remote dry-run passed.

### WEB-014.17 M20R Review Gate

- Reviewed the M12-M19 implementation against the original Graphiti-to-L2-B
  requirement. Current status: real Graphiti `_search(SearchConfig)` works via
  ECS 8790 and 7893, raw `graphiti_bundle` data is preserved, and L2-B /
  RustWorkX currently adds a preview-only projection layer.
- Node/Edge design is intentionally a view/algorithm projection, not a drifted
  Graphiti ontology copy. Graphiti fact names, labels, UUIDs, source/target
  UUIDs, episode provenance, and raw envelopes stay in bundle metadata.
- Remaining gaps are now explicit: preview UUIDs are not canonical L2-B UUIDs,
  the RefIndex prototype is file-backed rather than database-backed, and durable
  apply still needs operator-gated materialization through IdentityRefIndex.
- Added durable research anchors to
  `graphiti_l2b_ref_identity_design_20260517.md`: official Graphiti
  SearchConfig/Episodes/group_id/custom-type docs, `graphiti-core==0.28.2`,
  RustWorkX `0.17.1`, HippoRAG, AriGraph, GAT, DySAT, GraphGPS, AGCN, and the
  rustworkx paper.
- Next slice remains M20 implementation: selected bundle sections -> canonical
  IdentityBinding -> Ref/locator state -> optional L1.5/L2-B materialization,
  with rollback/audit receipts and no hidden direct FalkorDB or file mutation.

## Implementation Anchors

Keep active Web Console implementation in these locations:

| Surface | Path | Notes |
|:--|:--|:--|
| BFF / read adapters | `src/parrot/web_console/` | Server-side only; may hold secrets such as `PARROT_ORCH_SECRET` in process env. |
| React frontend source | `web/console_app/` | Formal next Web Console frontend: React + Vite, Memory Graph Workspace, Runtime Flow Workspace. |
| Built/static frontend | `web/console_dist/` | Served by the Web Console BFF when present; `web/console/` remains the legacy vanilla transition/reference shell. |
| Launcher | `src/scripts/start_web_console.py` | Local entrypoint; default port `7893`; supports local overrides for orchestration, Graphiti proxy URL/timeout, Nanobot API URL, and Google credentials path. |
| Tests | `tests/test_web_console/` | Focused BFF/static route tests. |

### 2026-05-18 True-Connection Follow-up

- ECS `8790` app-monitor now has the read-only Google Calendar smoke subset:
  `POST /api/google/calendar/preview`,
  `POST /api/google/calendar/api-fetch`, and
  `POST /api/google/calendar/nanobot-fetch`.
- The full `7893` Web BFF remains the richer source/import surface; the ECS
  subset exists so the browser can prove Google Calendar connectivity from the
  same service family as Graphiti/L2-B/runtime workflow smokes.
- `src/scripts/start_web_console.py` now accepts explicit Graphiti, Nanobot,
  and Google credential overrides so local `7893` true-proxy runs are
  repeatable instead of depending on hidden shell state.
- Google Calendar official API fetch now also discovers the ECS/nanobot OAuth
  mount at `~/.nanobot/google-workspace-credentials`, the same location used by
  the Nanobot Google Workspace MCP path.
- ECS proof after `e9289bd`: 8790 Calendar API fetch, Calendar Nanobot fetch,
  Graphiti `noble_etiquette` subgraph search, Graphiti import-plan preview,
  operator L2-B materialization, and L2-B context read all succeeded.
- Service-user OAuth install rule: app-monitor runs as `parrot`, so ECS
  credentials must be installed under
  `/home/parrot/.nanobot/google-workspace-credentials` with `parrot:parrot`
  ownership; `/root/.nanobot/...` is not enough for the HTTP service.

## Write Rules

- Default to read-only adapters before writes.
- Use the A-D discipline from `../business_interface_workflow.md`.
- Keep Web-only dashboard/admin flows here, not in Unity DTOs.
- Prefer one stable business file per product surface. Do not create a new doc
  for every sub-step of the same plan.
- If a multi-round implementation or audit needs temporary notes, place them
  under a clearly named temporary Web Console folder, keep them out of the
  shared TODO board, and promote only key decisions or durable findings back
  into the indexed business files.
- If a flow needs a shared field, endpoint, DTO, topic, or BB key, add a row to
  `../core_interface_candidate_queue_20260513.md` instead of editing core SSOT.
- Update `../../tasks/APP_WEB_PARALLEL_TODOLIST_20260513.md` for lane status.
- Keep `../README.md` and this README aligned whenever active Web business
  documents are added, superseded, or renamed.

## Suggested Slice Header

```md
## Slice: <name>

Owner chat: Web Console
Status: intake | proposed | approved | in_progress | blocked_core | done
Related TODO: WEB-###

### A. Source Readback

### B. Existing Core Interfaces

### C. Missing Core Surface

### D. Observable Completion Signal
```
