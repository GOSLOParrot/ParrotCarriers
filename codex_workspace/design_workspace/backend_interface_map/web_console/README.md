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
| `observability_runtime_business_flow_20260513.md` | approved | WEB-002, WEB-004, WEB-005 | ECS/module health, `/status`, Blackboard, IntentWorkspace, Plan/task, Scheduler, Nanobot, AgentTeam/Maid Team, collaboration status. |
| `memory_graph_workspace_business_flow_20260513.md` | approved | WEB-003, WEB-007 | L1.5, L2-B, node/photo management, Ref binding, Evidence/String Board boundary. |
| `graphiti_management_business_flow_20260513.md` | approved | WEB-006 | Graphiti/FalkorDB management route: observe/search/draft/dry-run first, Web operator surgery later. |

## Implementation Anchors

Keep active Web Console implementation in these locations:

| Surface | Path | Notes |
|:--|:--|:--|
| BFF / read adapters | `src/parrot/web_console/` | Server-side only; may hold secrets such as `PARROT_ORCH_SECRET` in process env. |
| Static frontend | `web/console/` | Obsidian-like console shell and future Web-only renderers. |
| Launcher | `src/scripts/start_web_console.py` | Local entrypoint; default port `7893`. |
| Tests | `tests/test_web_console/` | Focused BFF/static route tests. |

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
