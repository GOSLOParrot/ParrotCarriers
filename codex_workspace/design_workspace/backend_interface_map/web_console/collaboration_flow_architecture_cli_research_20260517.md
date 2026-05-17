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
