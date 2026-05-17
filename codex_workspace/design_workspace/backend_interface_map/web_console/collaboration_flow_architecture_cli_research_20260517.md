# Collaboration Flow Architecture and CLI Research (2026-05-17)

Owner: Web Console / Runtime Flow line
Status: active_research
Related SSOT: `collaboration_flow_workbench_ssot_20260517.md`

## Purpose

This note records the comparative research for the Collaboration Flow workbench:
what similar systems do well, whether Parrot should support a command line, and
how the Web Console layout should evolve without turning the Scheduler or
Nanobot into a second hidden workflow product.

The short answer:

- Keep Web Console as the primary operator workbench.
- Add a thin Parrot CLI as a companion control plane after the workflow JSON
  schema is stable.
- Do not use nanobot CLI/gateway as the main GOSLO control plane; keep nanobot
  embedded as a worker/task execution target.
- Keep CLI, Web, Scheduler, and ECS release scripts sharing the same catalog,
  workflow JSON, result contract, gates, and receipts.

## Internal Baseline

Current real surfaces already implemented:

- `GET /api/runtime/capabilities/catalog`
- `GET/POST/DELETE /api/runtime/workflows/drafts`
- `GET /api/runtime/workflows/drafts/{workflow_id}`
- `POST /api/runtime/workflow/plan-draft`
- `POST /api/runtime/workflow/run`
- `POST /api/runtime/workflow/result-contract`
- `GET/POST/DELETE /api/runtime/workflow/result-intake`
- `GET/POST/DELETE /api/runtime/workflow/action-gates`
- `POST /api/runtime/workflow/action-gates/decision`
- React Runtime capability search/filter, workflow draft insert/save/load/run,
  action-gate operation, result-intake staging, and L0/L1/L2/C3/C4/I0 filtering.

Stable local decisions to preserve:

- GOSLO Intent is routing and policy, not a single boolean switch.
- `L0/L1/L2/C3/C4/I0` are behavior/interaction modes, not Graphiti edge types.
- Graphiti owns temporal memory, provenance, extracted facts/entities, and
  search semantics. L2-B should preserve Graphiti raw payloads and add pointer,
  projection, fast context, and transform metadata.
- RustWorkX indices are runtime handles. Durable identity must use UUID/ref
  records, not graph-local integer indices.
- Nanobot is a Scheduler-compatible worker/task target. It is not the whole
  GOSLO brain and should not replace the Web workbench.
- The local nanobot research explicitly recommends Python SDK/library embedding
  for ParrotCarriers, not a CLI gateway.
- The canonical ECS code-release path is now `infra/ecs-release.ps1` after
  commit/push, not ad hoc manual service restarts.

## External Systems Reviewed

| System | Useful pattern | Transfer to Parrot | Caution |
|:--|:--|:--|:--|
| LangGraph / LangGraph Platform | Stateful graphs, interrupts, persistence, local CLI/dev server, deployment config. | Keep gates durable and resumable; expose run/thread state through Web; let CLI start local validation/smoke paths. | Do not import LangGraph wholesale unless Scheduler state becomes too hard to reason about. |
| Claude Code | Skills/commands, subagents, hooks, explicit permissions. | Add Web command palette and Parrot workflow skills; use action gates/hooks for deterministic guardrails; keep side tasks isolated. | Hooks with side effects need policy gates; do not allow silent memory writes. |
| OpenAI Codex CLI | Terminal-first agent, local file/command execution, approvals, subagents, scriptable `exec` style. | Good model for thin operator CLI and repeatable smokes; CLI should be composable and evidence-rich. | CLI must not bypass Web/HITL safety or become an autonomous writer to Graphiti/L2-B. |
| ComfyUI | Visual node graph, compact workflow JSON, import/export, queued execution messages. | Make workflow JSON a first-class portable artifact; show receipts/progress per node. | Avoid generic visual-programming sprawl; Parrot nodes must map to true backend capabilities. |
| Node-RED | Palette + workspace + sidebar, flows as tabs, JSON import/export, deploy/lock/enable, context stores. | Use palette/canvas/inspector/event-tape layout; separate workflow definition from runtime context/state. | Node-RED-style free-form functions would break Parrot's typed policy/gate model. |
| n8n | Workflow JSON import/export, CLI backup/import, credentials separated from workflows. | Add Web export/import and later CLI backup/restore; redact credentials and keep OAuth outside workflow JSON. | Imported workflow IDs/credentials can overwrite state in n8n; Parrot should require explicit merge/apply policy. |
| Temporal | Workflows as stateful services; Queries read state, Signals mutate async, Updates validate and return results. | Good future mental model for result intake and Scheduler workflow state: read/query, fire/signal, apply/update. | Full Temporal is likely too heavy until Parrot needs durable distributed workflow execution. |
| Prefect | Deployments, work pools, schedules/events, versioned deployment config, CLI/Python/API options. | Useful later for deployable job templates and infra-separated workers. | It is data-pipeline oriented, not memory-graph/provenance oriented. |

## CLI Decision

Recommendation: support a thin Parrot CLI, but only as a companion control
plane. Web remains the primary design/review surface.

Why yes:

- Real ECS testing needs repeatable smoke commands.
- Workflow JSON needs validation, import/export, and diff tooling.
- CI and release scripts need machine-readable receipts.
- Power users need quick catalog search without opening the browser.
- Codex/agent workers benefit from small composable commands they can call.

Why not CLI-first:

- The user-facing collaboration design is spatial and review-heavy.
- Action gates, result intake, Refs, Graphiti bundles, and L2-B projection need
  visual inspection.
- CLI-only flows make it too easy to bypass operator policy or lose provenance.

Do not use nanobot CLI as this layer:

- Nanobot CLI starts/configures nanobot sessions. Parrot needs a domain CLI for
  Parrot capability catalog, workflow drafts, Plan import, result intake, and
  ECS smoke.
- Parrot already embeds nanobot-like work as Scheduler task execution. The CLI
  should call Parrot BFF/service functions, not create another gateway brain.

## Proposed CLI Shape

Name options:

- `parrot-flow` as a focused executable.
- `python -m parrot.web_console.flow_cli` for the first implementation.
- Later, expose as `parrot flow ...` if the project already grows a top-level
  Parrot CLI.

Initial command set:

```text
parrot-flow catalog list --kind graphiti_search --mode C3 --json
parrot-flow workflow validate workflow.json
parrot-flow workflow export <workflow_id> --out workflow.json
parrot-flow workflow import workflow.json --dry-run
parrot-flow workflow run workflow.json --dry-run --json
parrot-flow plan draft workflow.json --dry-run --json
parrot-flow result-intake preview result.json --contract workflow_result_contract_v1
parrot-flow smoke local --graphiti --workflow --json
parrot-flow smoke ecs --graphiti --workflow --json
```

Release command stance:

- Do not duplicate `infra/ecs-release.ps1`.
- A later `parrot-flow release ecs --branch master` may wrap/check the existing
  script, but the script remains the canonical implementation.

CLI rules:

- JSON output by default for automation; optional compact table output for
  humans.
- Every mutating command must require explicit `--operator-mode` and should
  default to `--dry-run`.
- Never store secrets in workflow JSON; redact tokens/password/API keys in
  exports and receipts.
- Reuse the backend catalog and workflow/result-contract functions where
  possible, rather than creating a parallel schema.
- Exit nonzero on failed receipt, invalid schema, blocked gate, or unavailable
  true connection.
- Accept workflow JSON from file or stdin.

## Web Layout Recommendations

The Web workbench should remain the canonical design surface and borrow the
best ideas from visual workflow tools:

```text
+----------------------+-----------------------------+----------------------+
| Capability Palette   | Workflow Canvas / Swimlanes  | Inspector / Receipts |
| search, filters,     | draft nodes, gates, result   | payload, policy,     |
| modes, modules       | routes, Plan import preview  | raw Graphiti bundle  |
+----------------------+-----------------------------+----------------------+
| Run / Event Tape: latest workflow runs, gate decisions, result intake rows  |
+----------------------------------------------------------------------------+
```

Near-term UI additions:

- Command palette (`Ctrl+K`) for capability search, workflow load, gate jump,
  and smoke/run commands.
- Workflow JSON import/export buttons with redaction and diff preview.
- Node detail inspector that always shows execution policy, interaction modes,
  result destinations, true-connection proof, and raw payload refs.
- Run history/event tape linked to workflow nodes and action gates.
- Clear distinction between `Preview`, `Run`, `Stage result`, and future
  `Deploy/Activate`.

## Option Set

| Option | Description | Pros | Cons | Verdict |
|:--|:--|:--|:--|:--|
| A | Web-first only | Lowest complexity; best for visual review. | Harder to run repeatable smokes/CI/import-export automation. | Good now, incomplete long term. |
| B | Web + thin CLI | Best balance: visual design plus scripted validation/smoke. | Requires shared workflow schema discipline. | Recommended. |
| C | CLI/TUI-first | Fast for operators who live in terminal. | Bad for Graphiti/L2-B visual inspection and user-facing design. | Not recommended as primary. |
| D | External workflow engine | Durable distributed workflow execution. | Heavy migration and semantic mismatch today. | Future-only if Scheduler routing outgrows current model. |

## Broader Builder Patterns

The comparison should not overfit one tool. The useful patterns are repeated
across multiple workflow/agent builders:

| Pattern | Seen in | What to learn | Parrot decision |
|:--|:--|:--|:--|
| Portable workflow artifact | ComfyUI JSON, Node-RED JSON, n8n JSON, Dify DSL/YAML, AutoGen Studio JSON | A workflow must be easy to export, diff, review, and re-import. | Define `workflow_schema_v1` before adding richer canvas features. |
| Web UI plus API/CLI | LangGraph CLI, Codex CLI, n8n CLI, Langflow run API, Flowise API/CLI/SDK, AutoGen Studio CLI serve | Human design and scripted validation should share artifacts. | Web is primary; thin CLI reuses the same schema and receipts. |
| Human input node/gate | LangGraph interrupt, Dify Human Input, Claude hooks/permissions, Parrot HITL/action gates | Human review should be explicit, durable, and route-aware. | Keep Plan HITL and action gates first-class; no silent writes. |
| Variables and secrets separation | Dify variables/env vars, n8n credentials, Langflow API key/header model | Workflow configs should not carry secrets. | Continue redaction; store OAuth/API credentials outside workflow JSON. |
| Typed ports / node categories | Langflow typed ports, ComfyUI nodes, Node-RED palette, Dify nodes | Search/filter needs stable kinds and inputs/outputs. | Capability rows remain typed by kind, policy, mode, module, tag, and destination. |
| Run logs and receipts | Flowise tracing/logs, AutoGen profiling, ComfyUI messages, Dify run ids | Operators need proof of what ran and what changed. | Every workflow run/gate/intake path must return receipts and ledger ids. |
| Reusable subflows | Langflow Run Flow, Node-RED subflows, ComfyUI subgraphs, Dify node reuse | Subflows are powerful but can hide side effects. | Allow workflow templates only after validation and result-contract previews. |
| Iteration/loop nodes | Dify Iteration/Loop, general workflow engines | Useful for batch/refinement, risky for runaway agents. | Future only; require max-count, timeout, and operator-visible progress. |

## Core Requirements

These are the non-negotiable Parrot needs before the page can be called a real
Collaboration Flow Workbench:

1. Real capability discovery.
   `GET /api/runtime/capabilities/catalog` must stay the source for route,
   policy, interaction mode, module, tags, result destinations, and
   true-connection state. Static front-end-only nodes do not count.

2. Portable workflow artifact.
   Saved drafts need a documented `workflow_schema_v1` with nodes, edges,
   capability refs, payload, result destinations, gates, audit, and redaction
   policy. Web import/export and CLI validation must use the same schema.

3. Operator-gated execution.
   Trigger fire, Plan creation, result staging, Graphiti writes, and L2-B
   materialization must remain explicit `operator_mode=true` paths. Dry-run
   receipts are previews, not success proof.

4. True Nanobot/Scheduler compatibility.
   A workflow node is Nanobot-compatible only when it maps to a real
   `NANOBOT_TASK_TYPES` value and can become a `PlanStepProposal.expected_tool`.
   Generic prompt nodes do not count as pure nanobot compatibility.

5. Result contract and intake.
   Workflow runs must produce or carry `workflow_result_contract_v1`. Result
   intake must say which routes are preview, applied, blocked, or unsupported.
   IntentWorkspace staging is implemented; Graphiti/L2-B writes need dedicated
   reviewed routes.

6. Graphiti/L2-B raw preservation.
   Graphiti search/bundle/subgraph payloads must remain available as raw
   envelopes. L2-B can add fast projections and RustWorkX transform previews,
   but must not flatten away Graphiti facts/entities/episodes.

7. Evidence for true connections.
   Local 7893 and ECS 8790 smoke should prove actual endpoints, not just UI
   state. A route can be marked true only after a receipt/ledger/remote status
   proves it.

## Non-Core For Now

These ideas are useful, but implementing them now would likely cause drift:

- Generic JavaScript/Python Code Node.
- Arbitrary HTTP request node with stored credentials.
- C4 safe-turn speech or I0 interruption as runnable workflow nodes.
- Autonomous Graphiti/FalkorDB surgery from a workflow without a route-specific
  operator gate.
- Scheduler-enforced chained workflows before result routing is promoted out of
  Web-only prototypes.
- Full Temporal/Prefect engine migration.
- Nanobot gateway/CLI as the primary control plane.

## Implementation Requirements

Every new collaboration-flow feature should satisfy:

- Shared artifact: either extends `workflow_schema_v1` or explicitly avoids
  workflow storage.
- Shared route proof: route exists in Web BFF and, when needed for ECS testing,
  in app-monitor parity.
- Receipt proof: preview and apply paths return structured receipts with
  `dry_run`, `operator_mode`, `route_state`, and `ledger_id` or skip reason.
- Redaction: likely secret fields are redacted at save/export/receipt time.
- Drift guard: document whether the change is Web-only, shared core candidate,
  or Scheduler/Plan promotion.
- True-connection smoke: local and remote tests define what success means.

## Task Distribution

| Track | Owner surface | Near task | Output |
|:--|:--|:--|:--|
| Research/SSOT | Web docs | Keep this decision doc and workplan current. | Reread gate before implementation. |
| Backend schema | `parrot.web_console` | Add `workflow_schema_v1` validator/export helper. | Shared Python validation used by Web and CLI. |
| Web UI | React Runtime | Import/export/diff workflow artifacts and command palette. | Operator can inspect before run/apply. |
| CLI | New thin Parrot CLI | `catalog list`, `workflow validate`, `workflow run --dry-run`. | Scriptable receipts, no new brain/gateway. |
| Scheduler/Nanobot | Existing Plan path | Keep compatibility through `PlanStepProposal.expected_tool`. | Real Plan/HITL drafts, no hidden generic task type. |
| Graphiti/L2-B | Existing subgraph/source board routes | Preserve raw bundle references in workflow nodes/results. | Graphiti facts remain inspectable after import. |
| ECS/release | `infra/ecs-release.ps1` | Keep release as canonical; CLI may wrap later. | No duplicate deployment logic. |

## TODO Pre / During / After

TODO Pre for the next implementation slice:

- [ ] Reread `collaboration_flow_workbench_ssot_20260517.md`.
- [ ] Reread this architecture/CLI research note.
- [ ] Reread `_tmp/collaboration_flow_workplan_20260517.md`.
- [ ] Inspect `capability_catalog.py`, `runtime_flow.py`, `workflow_drafts.py`,
  `workflow_result_intake.py`, `server.py`, and `app_monitor_server.py`.
- [ ] Pick exactly one slice: schema/export/import, command palette, or CLI
  validate. Do not bundle all three.
- [ ] Define the true-connection smoke before editing code.

TODO During:

- [ ] Keep writes behind `operator_mode=true` and default preview/dry-run where
  possible.
- [ ] Use structured parsing/validation for workflow JSON, not ad hoc string
  checks.
- [ ] Preserve unknown future fields under an `extensions`/`raw` area rather
  than dropping data.
- [ ] Return precise `route_state` and `policy_skipped_reason` for unsupported
  nodes.
- [ ] Keep ECS app-monitor route parity if local Web BFF route is needed for
  true remote testing.

TODO After:

- [ ] Run focused pytest for Web/app-monitor routes.
- [ ] Run frontend typecheck/build if React changed.
- [ ] Smoke local 7893 with one saved/exported/imported workflow.
- [ ] Smoke remote 8790 after commit/push/ECS release when runtime code changed.
- [ ] Audit requirement drift against the table below.
- [ ] Record ledger results in the workplan.

## Requirement Drift Audit

| Requirement | Allowed direction | Drift signal | Review action |
|:--|:--|:--|:--|
| Real backend capabilities | More true routes and better proofs. | Static UI nodes without BFF route. | Block or mark prototype-only. |
| GOSLO behavior modes | More precise policy labels. | Global Intent on/off switch. | Reject; keep per-capability policy. |
| Graphiti/L2-B preservation | More raw bundle refs and overlays. | Flattening Graphiti into L2-B-only node categories. | Require raw envelope preservation. |
| Nanobot compatibility | More real task types via Scheduler catalog. | Generic natural-language task pretending to be typed. | Keep as draft/research, not compatible. |
| CLI support | Thin shared control plane. | CLI writes memory or manages nanobot gateway directly. | Reject or require operator gate. |
| Workflow engine | Better validation and run receipts. | Replacing Scheduler with generic DAG engine too early. | Keep Web orchestration until core promotion is approved. |
| HITL | More durable gates and timeout handling. | Silent auto-approval or hidden side effects. | Block until gate receipt exists. |

## True-Connection Test Matrix

Minimum test matrix for next slices:

| Capability | Local proof | ECS proof | Success means |
|:--|:--|:--|:--|
| Catalog | `GET :7893/api/runtime/capabilities/catalog` | `GET :8790/api/runtime/capabilities/catalog` | Same required ids, modes, and true-state fields exist. |
| Workflow schema | Validate known-good and known-bad JSON. | Same validation through app-monitor or CLI pointed at ECS. | Bad JSON returns structured errors; good JSON preserves unknown safe fields. |
| Import/export | Save draft, export JSON, delete, import, reload. | Repeat on 8790 if route parity exists. | Secret fields redacted; node count and capability ids stable. |
| Plan draft | Run workflow with one `ref_scan` node. | Same on 8790. | Receipt has `workflow_result_contract_v1` and one Plan-compatible step. |
| Trigger gate | Create trigger gate, preview/apply/reject/delete. | Same on 8790 with operator mode only. | Real apply either publishes or returns explicit Redis failure; dry-run alone not success. |
| Result intake | Preview and operator-stage IntentWorkspace row. | Same on 8790. | Applied row has `recorded=true` and can be deleted through public route. |
| Graphiti context | Query partition, import-plan selected hits. | ECS 8790 direct Graphiti path. | Raw `graphiti_bundle` counts are present and L2-B projection is preview-only unless operator route is used. |

## Recommended Next Slice

The safest high-value next slice is `workflow_schema_v1` plus Web
import/export/diff preview. It makes later CLI work honest because the CLI can
validate the same artifact the Web creates. It also supports the user's desire
to design real workflows for nanobot or the whole architecture without forcing
Scheduler workflow promotion yet.

Do not start with a broad CLI. Start with:

1. `workflow_schema_v1` validator and redacted export helper.
2. Web export/import/diff preview.
3. Focused CLI wrapper for `workflow validate` only.
4. Then add `catalog list` and `workflow run --dry-run`.

## Recommended Staging

Stage 1: stabilize artifacts.

- Define a small workflow JSON schema for saved drafts.
- Add Web import/export and diff preview.
- Add validation route/function reused by Web and CLI.
- Keep all writes behind existing gates and receipts.

Stage 2: add thin CLI.

- Implement `python -m parrot.web_console.flow_cli`.
- Support catalog list, workflow validate, workflow run preview, Plan draft,
  result-intake preview, local/ECS smoke.
- Reuse the BFF/service functions and return the same receipt schemas as Web.

Stage 3: promote durable shared workflow storage if needed.

- Add explicit `Draft`, `Reviewed`, `Active`, `Paused`, `Archived` states.
- Add deploy/activate semantics only after Scheduler result enforcement is
  designed.
- Consider Temporal/Prefect only if Parrot needs durable distributed workflow
  execution beyond current Scheduler/Plan/HITL.

## Practical TODO

- Add `workflow_schema_v1` document and validation helper.
- Add Web workflow import/export/diff UI.
- Add command palette for capability/workflow/gate search.
- Add `parrot-flow catalog list` and `workflow validate` first.
- Add `parrot-flow smoke ecs` only after it can call existing release/smoke
  contracts without duplicating ECS deployment logic.
- Keep C4/I0 as future policy-only until safe-turn/interrupt gates are designed.

## Source Index

Internal:

- `collaboration_flow_workbench_ssot_20260517.md`
- `_tmp/collaboration_flow_workplan_20260517.md`
- `.cursor/skills/nanobot-overview/references/skill_seeker_focus.md`
- `.cursor/skills/nanobot-overview/references/documentation/overview/README.md`
- `.cursor/memory/commit_guidelines.md`, Section 8
- `codex_workspace/workflows.md`

External official docs:

- LangGraph interrupts: https://docs.langchain.com/oss/python/langgraph/interrupts
- LangGraph CLI: https://docs.langchain.com/langgraph-platform/cli
- Claude Code subagents: https://docs.claude.com/en/docs/claude-code/sub-agents
- Claude Code hooks: https://docs.claude.com/en/docs/claude-code/hooks-guide
- Claude Code skills/commands: https://docs.claude.com/en/docs/claude-code/slash-commands
- OpenAI Codex CLI: https://developers.openai.com/codex/cli
- OpenAI Codex use cases: https://developers.openai.com/codex/use-cases
- ComfyUI workflow concept: https://docs.comfy.org/development/core-concepts/workflow
- ComfyUI workflow JSON: https://docs.comfy.org/specs/workflow_json
- ComfyUI server/messages: https://docs.comfy.org/development/comfyui-server/comms_messages
- Node-RED flows: https://nodered.org/docs/user-guide/editor/workspace/flows
- Node-RED import/export: https://nodered.org/docs/user-guide/editor/workspace/import-export
- Node-RED context: https://nodered.org/docs/user-guide/context
- n8n workflow import/export: https://docs.n8n.io/workflows/export-import/
- n8n CLI commands: https://docs.n8n.io/hosting/cli-commands/
- Temporal Python workflow message passing: https://docs.temporal.io/develop/python/workflows/message-passing
- Prefect deployments: https://docs.prefect.io/v3/concepts/deployments
- Prefect deployment creation: https://docs.prefect.io/v3/how-to-guides/deployments/create-deployments
- Dify key concepts/workflow/DSL/variables: https://docs.dify.ai/en/use-dify/getting-started/key-concepts#workflow
- Dify Human Input node: https://docs.dify.ai/en/use-dify/nodes/human-input
- Dify orchestration logic: https://docs.dify.ai/en/use-dify/build/orchestrate-node
- Dify Iteration/Loop nodes: https://docs.dify.ai/en/use-dify/nodes/iteration and https://docs.dify.ai/en/use-dify/nodes/loop
- Langflow flows and typed DAG execution: https://docs.langflow.org/concepts-flows
- Langflow flow trigger endpoints: https://docs.langflow.org/api-flows-run
- Flowise introduction/capabilities: https://docs.flowiseai.com/
- AutoGen Studio usage/export/CLI serve: https://autogenhub.github.io/autogen/docs/autogen-studio/usage/
