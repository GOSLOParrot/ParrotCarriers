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
| CFW-12 | pending | Trigger/message HITL state machine. | Current trigger fire remains operator-gated receipt-based execution. |
| CFW-13 | pending | Durable result-destination contract for Plan/Scheduler results. | Needs a reviewed schema before autonomous chained workflows. |

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
