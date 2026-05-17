# Collaboration Flow Workplan (2026-05-17)

Status: temporary-active
Durable SSOT: `../collaboration_flow_workbench_ssot_20260517.md`
Rule: before each implementation slice, reread the SSOT, this workplan, and the
relevant backend code. After each slice, add verification and review notes here.

## Questionnaire Index

| Id | Question | Current answer |
|:--|:--|:--|
| Q1 | Is the collaboration-flow page ready to become a real workbench? | Yes for first slice. Existing Runtime Flow already has read model, HITL, SSE, trigger catalog, and receipts. It lacks capability search/workflow drafting/Plan import. |
| Q2 | Is GOSLO Intent a simple switch? | No. Treat it as routing policy over L0/L1/L2/C3/C4/I0, operator gates, and result destinations. |
| Q3 | Should trigger categories mirror Graphiti edge ontology? | No. Trigger/Edge categories are view/filter/algorithm metadata. Graphiti raw facts/entities/episodes remain preserved. |
| Q4 | What is pure Nanobot compatibility? | A capability can become a Scheduler/Nanobot task when it maps to `NANOBOT_TASK_TYPES` and has serializable inputs/result channel metadata. |
| Q5 | What is Plan compatibility today? | `PlanStepProposal.expected_tool` must be a Scheduler/Nanobot task type. `result_destination` is not durable yet and should be shown as preview metadata. |
| Q6 | What is true trigger fire today? | `POST /api/dsg/triggers/fire-event` publishes only with `operator_mode=true` and `dry_run=false`; otherwise it returns a safe preview receipt. |
| Q7 | What can be real in first implementation? | Backend capability catalog, frontend search, local workflow draft insertion, and true trigger draft/fire from inserted nodes. |
| Q8 | What remains future? | Durable workflow storage, trigger/message HITL state machines, Plan result-destination schema, full Graphiti/L2-B transform recipes, and autonomous ref repair. |
| Q9 | Should Parrot copy a single external workflow product? | No. Borrow portable artifacts, HITL gates, typed ports, receipt logs, API/CLI parity, and secrets separation from multiple tools; keep Parrot's Graphiti/L2-B/GOSLO semantics. |
| Q10 | Should CLI be supported? | Yes, but as a thin Parrot control plane after `workflow_schema_v1`, not as CLI-first UX and not as a nanobot gateway replacement. |
| Q11 | What is the next safest implementation slice? | `workflow_schema_v1` plus Web import/export/diff preview; then a minimal CLI `workflow validate`. |
| Q12 | What counts as drift? | Static UI nodes, generic code/HTTP nodes, global Intent toggle, Graphiti flattening, Nanobot generic prompt pretending to be a typed task, or memory writes without route-specific operator gates. |

## TODO Before

- [x] Re-read `parrot-cursor-skill-bridge`.
- [x] Re-read nanobot/Graphiti/RustWorkX local skills.
- [x] Inspect Runtime Flow, trigger catalog, Plan, Scheduler, Graphiti/L2-B,
  Ref routes, and current React Runtime page.
- [x] Research external workflow/HITL/agent references and record links.
- [x] Record user original requirements and stable decisions in SSOT.
- [x] Add backend capability catalog route.
- [x] Add frontend search and workflow draft UI.
- [x] Verify true route calls and record results.

## Implementation Tasks

| Id | Status | Task | Verification |
|:--|:--|:--|:--|
| CFW-0 | done | Research + SSOT/workplan setup. | Docs created and README indexed. |
| CFW-1 | done | Backend `GET /api/runtime/capabilities/catalog`. | Route test passed; HTTP smoke returned Graphiti rows with `true_state=ecs_proxy`. |
| CFW-2 | done | Frontend type/API client. | `npm run typecheck` passed. |
| CFW-3 | done | Runtime Flow searchable capability catalog UI. | Runtime page now loads backend catalog, searches rows, and filters by kind. |
| CFW-4 | done | Insert selected capability into workflow draft list/canvas. | UI supports Insert, Enter, and double-click into local workflow draft. |
| CFW-5 | done | Execute inserted trigger nodes through existing draft/fire route. | HTTP smoke returned `dsg.trigger.draft_event`, matched `intent_event_boundary`, channel `parrot.dsg.events`. |
| CFW-6 | done | Draft workflow -> PlanProposal route. | Backend unit test creates a Plan in `AWAITING_USER_CONFIRMATION`; HTTP smoke previews nested workflow -> `ref_scan` step. |
| CFW-7 | done-first-slice | Nanobot-compatible Plan/Task dispatch preview. | Compatible capability nodes become `PlanStepProposal.expected_tool` values from `NANOBOT_TASK_TYPES`; direct task execution remains Scheduler/Nanobot-gated. |
| CFW-8 | done-first-slice | Result destination policy design and Plan gap note. | Catalog exposes `result_destinations`; durable Plan result routing remains a documented follow-up. |
| CFW-9 | done | Post-implementation review/bugfix/ECS release if needed. | First slice committed/pushed as `1137475` and ECS services were updated/restarted. |
| CFW-10 | done | Durable Web workflow draft registry. | Added save/list/get/delete routes, secret redaction, local UI save/load/delete controls, and `workflow_id` Plan import. |
| CFW-11 | done-first-slice | Whole workflow run/preview. | `POST /api/runtime/workflow/run` splits trigger nodes to DSG trigger routes and Nanobot-compatible nodes to Plan/HITL without changing Scheduler schema. |
| CFW-12 | done-first-slice | Trigger/message HITL state machine. | Added Web-only workflow action gates for trigger nodes and `message_check`; still separate from Plan HITL and not a shared App DTO. |
| CFW-13 | done-first-slice | Durable result-destination contract for Plan/Scheduler results. | Added `workflow_result_contract_v1` preview and carries result routes in Plan step inputs; Scheduler enforcement remains a reviewed follow-up before autonomous chained workflows. |
| CFW-14 | done-first-slice | Workflow result intake and reviewed result-route consumption. | Added Web-only result intake for `workflow_result_contract_v1`; operator mode can stage reviewed results to IntentWorkspace and records a bounded Web ledger. |
| CFW-15 | done-first-slice | Interaction-mode catalog and filter. | Capability rows now carry `interaction_modes` on the L0/L1/L2/C3/C4/I0 ladder; React Runtime can filter capabilities by mode. C4/I0 stay future-policy definitions with no automatic execution. |
| CFW-16 | done-research | Comparative architecture and CLI decision research. | Recorded `../collaboration_flow_architecture_cli_research_20260517.md`: Web remains the primary workbench; a thin Parrot CLI is recommended later for catalog/workflow validation, import/export, Plan draft, result-intake preview, and ECS smoke. |
| CFW-17 | done-research | Deep objective scheme analysis and next-slice gates. | Expanded `../collaboration_flow_architecture_cli_research_20260517.md` with Dify/Langflow/Flowise/AutoGen patterns, core/non-core requirements, task distribution, TODO pre/during/after, drift audit, true-connection test matrix, and recommendation to start with `workflow_schema_v1` + Web import/export/diff. |
| CFW-18 | done | `workflow_schema_v1` validator and redacted export/import helper. | Added shared validate/export/import-preview helpers and routes on both 7893 Web BFF and 8790 app-monitor parity surface. Tests cover good/bad JSON, diff preview, secret redaction, and catalog rows. |
| CFW-19 | done-first-slice | Web import/export/diff preview for workflow drafts. | Runtime Flow now has Validate, Export, Import preview, Load import, JSON artifact textarea, and diff summary. Imported artifacts still persist only through the existing Save route after operator review. |
| CFW-20 | done-first-slice | Thin CLI first slice: `workflow validate` and `catalog list`. | Added `python -m parrot.web_console.flow_cli` with JSON-first `catalog list` and `workflow validate`; it reuses backend catalog/schema helpers, performs no writes, returns nonzero for invalid workflows, redacts secrets, and accepts UTF-8 BOM JSON from Windows tools. |
| CFW-21 | done-first-slice | True-connection smoke pack for local/ECS workflow artifact path. | Local 7894 and ECS 8790 both proved save/validate/export/import-preview/delete with redaction; ECS also proved Plan draft still maps the imported workflow to `ref_scan`. |
| CFW-22 | done-ecs | Thin CLI workflow export/import dry-run. | Added `workflow export <workflow_id>` and `workflow import <workflow.json> --target-workflow ...` to `python -m parrot.web_console.flow_cli`; both reuse backend schema helpers, emit JSON/table receipts, redact secrets, and perform no writes. Local and ECS CLI smoke passed after release. |

## First Slice Design

Backend catalog route:

```text
GET /api/runtime/capabilities/catalog
```

Expected shape:

```json
{
  "success": true,
  "action": "runtime.capabilities.catalog",
  "capabilities": [],
  "groups": {},
  "audit": {
    "web_only": true,
    "true_connection_standard": "..."
  }
}
```

Capability kinds:

- `runtime_read`
- `hitl_gate`
- `trigger`
- `nanobot_task`
- `graphiti_search`
- `l2b_graph_op`
- `ref_op`
- `source_import`
- `evidence_op`
- `workflow_template`

Execution policies:

- `read_only`
- `draft_only`
- `operator_gated`
- `nanobot_dispatch`
- `external_oauth`
- `ecs_proxy`

Result destinations:

- `view_only`
- `return_to_goslo`
- `return_to_app`
- `stage_to_intent_workspace`
- `write_to_memory_draft`
- `write_graphiti_episode`
- `materialize_l2b`

Frontend first slice:

- Load catalog once with Runtime Flow.
- Search across title, description, route, tags, trigger name, task type.
- Filter by capability kind/policy through simple chips.
- Insert into a local workflow draft.
- For inserted trigger nodes, call existing trigger draft/fire route using the
  capability-provided sample payload.

## True-Connection Smoke Plan

Local:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_web_console\test_web_console_server.py -q
cd web\console_app; npm run typecheck; npm run build
```

HTTP:

```powershell
Invoke-RestMethod http://127.0.0.1:7893/api/runtime/capabilities/catalog
```

Trigger from inserted node:

```json
{
  "trigger_name": "intent_event_boundary",
  "dry_run": false,
  "operator_mode": true,
  "event": {
    "type": "intent_boundary",
    "kind": "workflow_capability_fire",
    "source": "runtime_flow_workbench"
  }
}
```

Expected operator result: published to `CH_DSG_EVENTS`, or explicit Redis error
receipt if Redis is unreachable. Dry-run result alone is not final success.

## Ledger

- 2026-05-17: Created SSOT/workplan after rereading local skills, current
  Runtime/Graphiti/L2-B docs, route/code baseline, and external references.
- 2026-05-17: Implemented the first Collaboration Flow workbench slice:
  backend capability catalog, Runtime page capability search/filter, workflow
  draft insertion, trigger draft/fire from inserted nodes, and workflow draft ->
  HITL Plan import route. Fixed two compatibility bugs found during true HTTP
  smoke: `runtime.workflow.plan_draft` now accepts both top-level
  `workflow_nodes` and nested `workflow.nodes`, and Graphiti import-plan accepts
  `selected_hits` as an alias for `hits`.
- 2026-05-17 verification: `pytest tests/test_web_console/test_web_console_server.py -q`
  reported `90 passed`; `npm run typecheck` passed; `npm run build` passed with
  only the existing 507.75 KiB chunk warning; `git diff --check` reported only
  CRLF warnings. Local 7893 was restarted with
  `PARROT_WEB_CONSOLE_GRAPHITI_URL=http://8.216.45.45:8790` and
  `PARROT_WEB_CONSOLE_GRAPHITI_TIMEOUT_S=240`.
- 2026-05-17 true-connection smoke: `GET /api/runtime/capabilities/catalog`
  returned Graphiti capability rows with `true_state=ecs_proxy`; nested
  `POST /api/runtime/workflow/plan-draft` returned one compatible `ref_scan`
  Plan step; trigger draft returned `matched=intent_event_boundary` on
  `parrot.dsg.events`; Graphiti status returned partitions including
  `noble_etiquette`; `POST /api/graphiti/subgraph/search` on
  `noble_etiquette` query `greeting rank etiquette note` returned `3` hits,
  `7` nodes, and `3` edges; `POST /api/graphiti/subgraph/import-plan` with
  `selected_hits` returned success with `2` observations, `2` bundle facts, and
  `3` bundle entities.
- 2026-05-17: Implemented CFW-10 durable Web workflow draft registry:
  `GET/POST/DELETE /api/runtime/workflows/drafts`, `GET
  /api/runtime/workflows/drafts/{workflow_id}`, and `workflow_id` support in
  `/api/runtime/workflow/plan-draft`. Drafts preserve capability nodes,
  result-destination metadata, tags, and audit fields while redacting likely
  secret/token/password/API-key fields. React Runtime can save, load, delete,
  and re-import saved workflow drafts. Verification: focused compile/tests and
  frontend typecheck passed; full Web routes reported `91 passed`; `npm run
  build` passed with the existing chunk warning. HTTP smoke on restarted 7893
  saved `wf-smoke`, listed it, loaded it with `[REDACTED]` token payload,
  imported it by `workflow_id` into one `ref_scan` Plan step, then deleted it.
- 2026-05-17 ECS deployment fix: after pushing CFW-10, remote `8790`
  `parrot-app-monitor` returned 404 for `/api/runtime/workflows/drafts`
  because app-monitor is not the full 7893 Web BFF. Added the runtime
  capability catalog, workflow plan-draft, and workflow draft registry routes
  to `src/parrot/brain/app_monitor_server.py` as the ECS-facing parity slice.
  Verification: `py_compile` passed; `tests/test_brain/test_app_v1_monitor.py`
  reported `11 passed`; focused Web workflow tests passed.
- 2026-05-17 remote proof after commit `74f6d27`: ECS `/opt/parrot/ParrotCarriers`
  and `/opt/parrotcarriers` both fast-forwarded to `74f6d27`; `parrot-app-monitor`,
  `parrot-scheduler`, `parrot-goslo-chat`, `parrot-maid`,
  `parrot-orchestrator`, and `parrot-brain` restarted active. Remote
  `http://8.216.45.45:8790` smoke returned workflow catalog registry row,
  saved `ecs-smoke-workflow`, loaded `[REDACTED]` for `api_token`, imported it
  by `workflow_id` into one `ref_scan` Plan step, and deleted it.
- 2026-05-17: Implemented CFW-11 whole workflow run/preview route:
  `POST /api/runtime/workflow/run`. The route loads inline nodes or a saved
  `workflow_id`, sends trigger nodes through the existing DSG trigger
  draft/fire path, sends Nanobot-compatible nodes through
  `/api/runtime/workflow/plan-draft`, and reports unsupported nodes as skipped.
  This deliberately stays a Web orchestration route rather than a shared
  Scheduler workflow protocol. Verification: Web route tests `91 passed`;
  app-monitor tests `11 passed`; frontend typecheck/build passed. Local 7893
  HTTP smoke saved `wf-run-smoke`, ran it in preview, got one
  `dsg.trigger.draft_event` receipt matched to `intent_event_boundary`, one
  `runtime.workflow.plan_draft` receipt with one `ref_scan` step, then deleted
  the draft.
- 2026-05-17: Released CFW-11 to ECS as commit `206f315`. Both
  `/opt/parrot/ParrotCarriers` and `/opt/parrotcarriers` fast-forwarded to the
  same commit, then `parrot-app-monitor`, `parrot-scheduler`,
  `parrot-goslo-chat`, `parrot-maid`, `parrot-orchestrator`, and
  `parrot-brain` were restarted and verified active. Remote `8790` smoke saved
  `ecs-run-smoke-20260517213107`, ran `POST /api/runtime/workflow/run` in
  preview, returned one `dsg.trigger.draft_event` receipt matched to
  `intent_event_boundary`, one `runtime.workflow.plan_draft` receipt with one
  `ref_scan` step, then deleted the draft.
- 2026-05-17: Implemented CFW-13 first slice:
  `POST /api/runtime/workflow/result-contract`. The contract is
  `workflow_result_contract_v1`, returns per-node result routes, destination
  counts, and route-state counts, and is copied into Nanobot-compatible Plan
  step inputs as `result_routes`. This makes result destinations visible to
  Nanobot/Scheduler dispatch payloads without making Scheduler enforce chained
  routing yet.
- 2026-05-17: Released CFW-13 to ECS as commit `8902965`. Remote `8790` smoke
  saved `ecs-result-contract-smoke-20260517214654`, returned
  `workflow_result_contract_v1` with destination counts
  `stage_to_intent_workspace:1`, `return_to_goslo:2`, `view_only:1`, confirmed
  `scheduler_enforced=false`, confirmed Plan preview carried two result routes
  on the `ref_scan` step, then deleted the draft.
- 2026-05-17: Implemented CFW-12 first slice:
  `GET/POST/DELETE /api/runtime/workflow/action-gates` and
  `POST /api/runtime/workflow/action-gates/decision`. The state machine stores
  Web-only pending gates for trigger workflow nodes and `message_check`, lets
  operators preview/apply/reject/cancel, and applies by calling the existing
  trigger or message routes only under operator execution.
- 2026-05-17 CFW-12 validation: Python compile passed for the touched runtime
  files; Web Console route tests reported `91 passed`; app-monitor route tests
  reported `11 passed`; frontend `npm run typecheck` and `npm run build`
  passed with the existing chunk-size warning. Local `7893` smoke saved
  `local-action-gate-smoke-*`, created trigger and message gates, previewed
  trigger apply through `dsg.trigger.draft_event`, applied a real operator
  `reject` decision on the message gate (`state=rejected`), listed two gates,
  and cleaned up both gates plus the workflow draft.
- 2026-05-17 remote CFW-12 proof after commit `f749acc`: ECS
  `/opt/parrot/ParrotCarriers` and `/opt/parrotcarriers` fast-forwarded to
  `f749acc`, six services restarted active, and `8790` saved
  `ecs-action-gate-smoke-*`. The catalog exposed
  `runtime.workflow.action_gates`; trigger and `message_check` gates were
  created; trigger apply ran with `operator_mode=true`/`dry_run=false` and
  returned `dsg.trigger.fire_event` with `published=true`; message reject
  returned `state=rejected`; both gates and the draft were deleted.
- 2026-05-17: Implemented CFW-14 first slice:
  `GET/POST/DELETE /api/runtime/workflow/result-intake`. The route consumes
  `workflow_result_contract_v1` or a saved workflow draft, selects result routes
  by `workflow_node_id`/`capability_id`, previews route application, and in
  `operator_mode=true`/`dry_run=false` stages only
  `stage_to_intent_workspace` as a `RICH_REPORT` with role
  `workflow_result`. `view_only` and `return_to_goslo` remain receipt/context
  drafts, while Graphiti/L2-B/materialization destinations are blocked until
  explicit route-specific operator flows are reviewed.
- 2026-05-17 CFW-14 validation: Python compile passed for the touched runtime
  files; Web Console route tests reported `91 passed`; app-monitor route tests
  reported `11 passed`; frontend `npm run typecheck` and `npm run build`
  passed with the existing chunk-size warning. Local `7893` smoke saved
  `local-result-intake-smoke-*`, confirmed catalog row
  `runtime.workflow.result_intake`, previewed result intake with
  `would_stage=true` and `recorded=false`, then applied operator intake with
  `recorded=true`, `staged_ref_count=1`, and result-intake list count `1`.
- 2026-05-17 remote CFW-14 proof after commit `f942e2a`: ECS
  `/opt/parrot/ParrotCarriers` and `/opt/parrotcarriers` fast-forwarded to
  `f942e2a`, six services restarted active, and `8790` saved
  `ecs-result-intake-smoke-*`. The catalog exposed
  `runtime.workflow.result_intake`; preview intake returned
  `recorded=false` and `would_stage=true`; operator intake returned
  `recorded=true`, `staged_ref_count=1`, entry `wri_f7936482c893`, and list
  count `1`; the temporary workflow draft was deleted.
- 2026-05-17 CFW-14 bugfix: result-intake route states now distinguish
  `preview`, `applied`, and `blocked`. Dry-run `view_only`/`return_to_goslo`
  no longer report `applied=true`, and operator attempts whose destinations
  are all blocked no longer create an `applied` ledger entry. Regression smoke
  on local `7893` returned `view_state=preview`, `view_applied=false`,
  `blocked_entry_state=blocked`, and `blocked_count=1`.
- 2026-05-17 CFW-14 cleanup bugfix: result-intake entries now support
  `DELETE /api/runtime/workflow/result-intake/{entry_id}` on both Web Console
  and app-monitor, so true 7893/8790 smoke rows can be cleaned through the
  public operator route instead of manual SSH file edits. React Runtime exposes
  the delete action in the result-intake ledger list.
- 2026-05-17 CFW-15 interaction-mode slice: `GET /api/runtime/capabilities/catalog`
  now returns stable `interaction_modes` definitions for `L0`, `L1`, `L2`,
  `C3`, `C4`, and `I0`, and every capability row carries inferred
  `interaction_modes` derived from execution policy, modules, tags, and result
  destinations. The route supports `interaction_mode=` filtering on Web Console
  and ECS app-monitor. React Runtime exposes a mode filter next to the existing
  kind/search controls and shows mode chips in capability rows. This is a
  read-model/policy classification layer only; C4 safe-turn speech and I0
  interruption remain explicit future policy, not executable workflow nodes.
- CFW-15 review fix: the first live smoke showed `runtime.flow.snapshot`
  incorrectly classified as C3 because it references IntentWorkspace as a
  module. The inference was tightened so C3 is derived from explicit
  `return_to_goslo` / `stage_to_intent_workspace` result destinations, not from
  module membership alone. Retest: snapshot modes are `L0,L2`, while C3 filter
  still returns context-capable rows.
- 2026-05-17 CFW-16 research: reviewed the existing Collaboration Flow SSOT,
  nanobot SDK/CLI notes, ECS release workflow, and official docs for LangGraph,
  Claude Code, OpenAI Codex CLI, ComfyUI, Node-RED, n8n, Temporal, and Prefect.
  Recorded the comparative decision in
  `../collaboration_flow_architecture_cli_research_20260517.md`: use Web as the
  primary operator workbench, add a thin Parrot CLI later for validation,
  import/export, Plan draft, result-intake preview, and true-connection smokes,
  and keep nanobot as an embedded worker rather than a CLI/gateway control
  plane.
- 2026-05-17 CFW-17 deepening: added Dify, Langflow, Flowise, and AutoGen
  Studio to the comparison, then hardened the Parrot-specific gates. The next
  recommended slice is not a broad workflow engine or broad CLI; it is
  `workflow_schema_v1` plus Web import/export/diff preview, followed by a
  minimal `workflow validate` CLI. The documented non-core/drift list blocks
  generic Code Nodes, arbitrary HTTP nodes, direct C4/I0 execution, direct
  Graphiti/L2-B writes without route-specific gates, and nanobot gateway/CLI as
  the main control plane.
- 2026-05-17 CFW-18/19 implementation: added shared
  `workflow_schema_v1` helpers in `workflow_drafts.py` plus
  `POST /api/runtime/workflow/validate`,
  `GET /api/runtime/workflow/export`, and
  `POST /api/runtime/workflow/import-preview` on both 7893 Web Console and
  8790 app-monitor. The schema normalizes nodes/edges, keeps safe unknown
  fields under `extensions`, redacts secret-like keys, validates good/bad
  workflows, and returns a non-mutating import diff. Runtime Flow now exposes
  Validate, Export, Import preview, Load import, a JSON artifact field, and an
  import-diff summary while leaving persistence behind the existing Save
  operator action.
- 2026-05-17 CFW-18/19 validation: `py_compile` passed for
  `workflow_drafts.py`, `server.py`, `app_monitor_server.py`, and
  `capability_catalog.py`; Web Console route tests reported `91 passed`;
  app-monitor route tests reported `11 passed`; frontend `npm run typecheck`
  passed; `npm run build` passed with the existing 523 KiB chunk warning; and
  `git diff --check` reported only existing CRLF warnings. A temporary local
  HTTP smoke on port `7894` saved `wf-schema-smoke`, validated it, exported
  `workflow_schema_v1`, import-previewed a diff with `wf-trigger` added and
  `wf-ref-scan` kept, confirmed `smoke-secret` was redacted, then deleted the
  draft.
- 2026-05-17 remote CFW-18/19 proof after commit `24b0ef5`: ECS
  `/opt/parrot/ParrotCarriers` fast-forwarded to `24b0ef5`, editable install
  completed, and six services restarted active. Remote `8790` exposed catalog
  rows `runtime.workflow.validate`, `runtime.workflow.export`, and
  `runtime.workflow.import_preview`; saved `ecs-schema-smoke-20260517233147`;
  validated it; exported `workflow_schema_v1`; import-previewed `wf-trigger`
  as added and `wf-ref-scan` as kept; confirmed `ecs-schema-secret` was
  redacted; Plan draft still produced one `ref_scan` step; and the temporary
  draft was deleted.
- 2026-05-17 CFW-20 implementation: added
  `python -m parrot.web_console.flow_cli` as the first thin Parrot Flow CLI.
  `catalog list` calls the same `build_runtime_capability_catalog()` helper as
  Web/ECS and supports query/kind/policy/interaction-mode/limit filters.
  `workflow validate` reads a file or stdin, calls
  `validate_workflow_artifact()`, emits JSON by default, supports table output,
  returns exit code `2` for invalid workflows or invalid JSON, and performs no
  writes. A Windows smoke initially exposed UTF-8 BOM JSON as invalid; the CLI
  now reads files with `utf-8-sig`, matching the earlier Google OAuth encoding
  lesson.
- 2026-05-17 CFW-20 validation: `py_compile` passed for `flow_cli.py`; focused
  CLI tests reported `5 passed`; full Web Console route tests remained
  `91 passed`; command smoke for `catalog list --kind workflow_template --q
  workflow_schema --limit 2` returned workflow schema rows; command smoke for
  `workflow validate` returned `workflow_schema_v1`, workflow id `cli-smoke`,
  and did not print `cli-smoke-secret`.
- 2026-05-17 CFW-22 implementation: extended
  `python -m parrot.web_console.flow_cli` with `workflow export <workflow_id>`
  and `workflow import <workflow.json> --target-workflow <workflow.json>`.
  Export calls `export_workflow_artifact()` against the configured local draft
  store. Import calls `preview_workflow_import()` and is dry-run only:
  `would_save=false`, no draft persistence, no Plan dispatch, no trigger fire,
  no Graphiti/L2-B write.
- 2026-05-17 CFW-22 local validation: `py_compile` passed for `flow_cli.py`;
  focused CLI tests reported `8 passed`; full Web Console route tests remained
  `91 passed`; CLI smoke exported `cli-export-smoke` with
  `cli-export-secret` redacted and import-previewed `cli-import-smoke` with
  `wf-trigger` added, `wf-ref-scan` kept, and `cli-import-secret` redacted.
- 2026-05-17 CFW-22 ECS validation: committed/pushed `e2fc57c5`
  (`Add flow CLI export import preview`) and released with
  `infra/ecs-release.ps1 -Branch master -AllowLocalDirty`; all six ECS services
  returned active. Remote CLI smoke on `/opt/parrot/ParrotCarriers` exported
  `ecs-cli-export-*` from a temporary draft store with
  `ecs-cli-export-secret` redacted, then import-previewed
  `ecs-cli-import` against `ecs-cli-target` with `wf-trigger` added,
  `wf-ref-scan` kept, `ecs-cli-import-secret` redacted, and
  `would_save=false`.
