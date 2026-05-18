# GOSLO Calendar Collaboration Policy Baseline - 2026-05-18

Status: discussion/research baseline before implementing GOSLO-facing calendar
tools and workflow interfaces.

Related reread files:

- `collaboration_flow_workbench_ssot_20260517.md`
- `_tmp/collaboration_flow_workplan_20260517.md`
- `_tmp/l15_graphiti_import_test_20260515.md`
- `_tmp/runtime_flow_memory_upgrade_research_20260513.md`
- `core_interface_candidate_queue_20260513.md`

## User Verbatim Requirements To Preserve

> source-to-DSG buffer policy 其实就是L2-B的组织方式之一和图变化协议之一是吧

> GOSLO通过对话来改变日程要用那个接口，出了修改，也应该含有同步到L1.5池和 L2-B才对

> 一键导入是Web测试，也是接口测试，目的是希望能GOSLO Intent，或nanobot制定计划，或者出现协作时，可以自动拉取Google日程参与计划，协作流里也有human-in-the-loop模块对吧。

> 现在GOSLO 了解日程的工具是？上行通道是？ 是不是还没设计，不然先完成给GOSLO使用的日程工具

> 如果是Intent Plan 和协作流 与 naonobot合作等，就共同制定到IntentWorkspace，实时状态再同步到L2-B

> GOSLO 虽然是Intent，但基本上协作是监控计划，基本是做决策和调用tool指令，复杂操作大部分交给Tasks

> GOSLO复杂反馈和语音推荐决策给User来确认。

> 目前GOSLO好像拿到日程和设置计划派发任务来修改日程的指令工具没搞好，GOSLO只要下指令和监控反馈状态，具体执行是nanobot，L2-B大部分情况是同步IntentWorkspace、黑板等信息的潜意识工作记忆区，同步用的

> Web的测试和接口的目的是提供这几个角色的协作功能，相当于个一个Agent Team的Multitasks 任务加了一个GOSLO的语音交流，让GOSLO能带着User及实时参与Plan的决策

> L2-B在里面的作用不是修改任务的SSOT，而是不需要严格同步SSOT

> 记录下这些重要的初始需求和原话，不要后面完成工具和实现接口

> 包括GOSLO工具、指令，同步状态，怎么符合体感和Reflex

## Core Interpretation

Yes: `source-to-DSG buffer policy` belongs to the L2-B organization and graph
mutation protocol family. It is not a new task SSOT. It decides how source data
such as Google Calendar, Obsidian, Graphiti, App evidence, and nanobot results
become DSG-visible buffer/projection state:

- Source identity and provenance are preserved.
- L1.5 receives normalized observations and source buckets.
- L2-B receives lightweight working-memory pointers, attention/salience, local
  topology, and optional subgraph overlays.
- Graphiti keeps long-term temporal/provenance memory where appropriate.
- IntentWorkspace and Plan/HITL remain the active collaboration/task surfaces.

L2-B should therefore sync and help retrieve/associate, but it should not become
the authoritative task ledger. Plan state, user confirmation, nanobot task
execution, and write-back receipts must remain outside the L2-B topology.

## Role Model

GOSLO:

- Voice/conversation-facing Intent agent.
- Decides what to ask, what to recommend, and which tool/plan command to issue.
- Should get compact status/context tools, not raw backend surgery routes.
- Should monitor Plan/nanobot results and bring complex choices back to the
  user through voice/HITL.
- Should not silently mutate Google Calendar as a conversational side effect.
  After Plan/HITL approval, a dedicated T1 direct Calendar API route is allowed
  for normal fast software-style writes; complex/slow writes may go to T3.
- Should not own L2-B graph persistence or treat memory projection as task
  truth.

Nanobot:

- Background execution worker for complex or slow Tasks.
- Owns the T3 Google Workspace MCP/API execution route through
  Scheduler-dispatched task types such as `calendar_fetch`, `calendar_create`,
  `calendar_patch`, and `calendar_delete`.
- Returns structured receipts/results to Scheduler/Runtime Flow/IntentWorkspace.

Plan/HITL:

- Plan is the explicit task/decision SSOT for multi-step operations.
- HITL gates are the confirmation boundary for user-visible or destructive
  actions such as writing to Google Calendar.
- Calendar write should be plan/gate-driven, not a direct conversational side
  effect.
- After approval, Plan/GOSLO chooses whether execution is a fast T1 direct
  Calendar API write or a T3 Nanobot/Scheduler task.

IntentWorkspace:

- Shared working desk for Plan drafts, Calendar change drafts, nanobot reports,
  and state summaries.
- Good place for GOSLO/User collaboration artifacts.
- Not a permanent source database.

L1.5:

- Normalized observation pool and source buffer.
- Google Calendar read/import should land here as `GOOGLE_CALENDAR`
  observations with provider identity, lifecycle state, and tombstone metadata.

L2-B:

- Subconscious working-memory/index layer over IntentWorkspace, Blackboard,
  L1.5, Graphiti, and other sources.
- Stores pointers, salience, association topology, and bounded subgraph context.
- Does not need strict SSOT synchronization and should not own task truth.

Graphiti:

- Temporal long-term memory and provenance graph.
- Optional audit Episodes can record Calendar import/write decisions later, but
  Graphiti should not be required for every short-lived Calendar state update.

Web Console:

- Operator/test workbench for the same contracts GOSLO and nanobot need.
- One-click import/search/test is useful because it proves the runtime contract,
  not because Web should become the runtime owner.

## Current Code Facts

- `src/parrot/brain/tools/__init__.py` exposes GOSLO tools including
  `calendar_context`, `calendar_change_request`, `calendar_task_status`,
  `dispatch_task`, `query_memory`, `remember`, `manage_episode`, and scene/App
  controls.
- `src/parrot/brain/tools/dispatch_task.py` already documents calendar task
  types: `calendar_fetch`, `calendar_create`, `calendar_patch`, and
  `calendar_delete`. This is the right low-level execution boundary, but it is
  too generic to be the final GOSLO-facing UX.
- `src/parrot/brain/tools/query_memory.py` uses Graphiti natural-language
  subgraph retrieval and can search `goslo`, `maid`, `scene`, `user`,
  `arknights_test`, and `noble_etiquette` partitions. It is not a Calendar
  status tool.
- `src/parrot/brain/app_first_version.py` has `create_calendar_draft()`, which
  stages an Intent-layer Calendar decision draft as an IntentWorkspace
  `calendar_draft` paper note. It does not write Google Calendar.
- `src/parrot/dsg/triggers/calendar_trigger.py` already models the read path as
  `Scheduler -> Nanobot -> Google Workspace MCP -> calendar_result ->
  CalendarTrigger -> L1.5 Pool -> GOOGLE_CALENDAR bucket -> L2-B EVENT nodes`.
- `src/parrot/web_console/memory_ops.py` has Web/ECS read/test/import surfaces:
  Calendar preview, API fetch, Nanobot fetch, fetch dispatch, result history,
  import draft, import plan, and operator-gated import to L1.5.
- `src/parrot/web_console/runtime_flow.py` has Web-only Runtime Flow and Plan
  HITL read/apply receipts.
- `src/parrot/web_console/workflow_action_gates.py` has Web-only workflow action
  gates for trigger/message operations; Calendar write-specific action gates
  still need a concrete capability mapping.

## External API Notes

Official Google Calendar API docs confirm the raw primitives needed by the
nanobot execution layer:

- `events.list` reads events from a calendar and supports free-text query and
  time/window parameters.
- `events.insert` creates an event and requires OAuth authorization plus an
  event body with `start` and `end`.
- `events.patch` updates selected event fields; Google notes patch semantics
  and quota implications.
- Incremental sync uses `syncToken`; if Google returns `410`, the client must
  perform a full resync.
- Push notifications require `events.watch`, a webhook channel, HTTPS callback,
  and channel id/token handling.

Primary docs:

- https://developers.google.com/workspace/calendar/api/v3/reference/events/list
- https://developers.google.com/workspace/calendar/api/v3/reference/events/insert
- https://developers.google.com/workspace/calendar/api/v3/reference/events/patch
- https://developers.google.com/workspace/calendar/api/guides/sync
- https://developers.google.com/workspace/calendar/api/guides/push

## Recommended Architecture: Option C

Preferred option unless later research finds a stronger scheme:

1. GOSLO receives a small, safe Calendar tool surface:
   - `calendar_context`: fetch/refresh/read current Calendar context for an
     Intent or Plan.
   - `calendar_change_request`: draft create/patch/delete intent, stage it to
     IntentWorkspace, and optionally produce a Plan/HITL gate.
   - `calendar_task_status`: check dispatched nanobot task/result state.
2. GOSLO does not write Google Calendar from `calendar_change_request`. It
   issues structured Intent/Plan drafts and monitors receipts.
3. Plan/HITL decides whether a Calendar write is allowed.
4. After approval, GOSLO/Plan chooses the execution route:
   T1 direct Google Calendar API for fast ordinary writes, or
   T3 Nanobot/Scheduler for slow/complex/AgentTeam operations.
5. The selected execution route returns structured result receipts.
6. The result is staged back to IntentWorkspace for GOSLO/User visibility.
7. CalendarTrigger/import policy normalizes the result into L1.5 observations.
8. L2-B receives working-memory pointers/attention/subgraph context from
   IntentWorkspace, Blackboard, Plan state, and L1.5 observations.
9. Optional Graphiti audit Episodes record important user-confirmed decisions
   and durable provenance.

This matches the user's framing: Web proves the interfaces; GOSLO provides the
voice/decision loop; T1 can handle ordinary fast software operations; nanobot
handles complex background execution; L2-B stays a subconscious sync/buffer
layer rather than the task SSOT.

## Non-Goals For The Next Slice

- Do not make L2-B the authoritative Calendar/task database.
- Do not let GOSLO directly mutate Google Calendar without Plan/HITL policy.
- Do not treat Web-only drafts as runtime truth.
- Do not require Graphiti writes for every Calendar sync pulse.
- Do not assume the App has a finished 2D workspace when defining backend
  Calendar/GOSLO tools.

## Immediate Capability Gaps

1. Dedicated GOSLO Calendar tools now exist for context, draft, and status;
   remaining work is approved execution routing and end-to-end receipts.
2. Calendar task schemas are still generic strings inside `dispatch_task`, not typed
   GOSLO-friendly commands with result/status receipts.
3. Calendar write-back needs two approved execution routes: T1 direct Calendar
   API for ordinary fast writes, and T3 Nanobot/Scheduler for complex/slow
   operations. The Intent draft tool must not force either path.
4. Runtime Flow/HITL exists, but Calendar write action gates need capability
   mapping and safe preview/apply receipts.
5. L1.5 import works as a source path, but automatic Calendar result-to-L1.5
   and L2-B visible sync should be verified end-to-end after the GOSLO tool
   layer is added.
6. Incremental sync/watch state is not implemented and should wait until the
   explicit fetch/write capability is solid.

## Next Design Question

Define the first GOSLO-facing Calendar tool contract. Recommended minimal set:

- `calendar_context(intent: str, date: str = "today", include_l2b: bool = true)`
- `calendar_change_request(action, calendar_id, event_id?, draft_event,
  reason, require_user_confirmation: bool = true)`
- `calendar_task_status(task_id?, plan_id?, include_workspace_refs: bool = true)`

The first implementation should be read/preview/draft first, then approved
execution routes, then result sync to IntentWorkspace and optional
L1.5/L2-B/Graphiti projection. Memory projection is not the Calendar task SSOT.

## GOSLO Tool Manual Taxonomy

Every GOSLO-facing tool needs a manual-level docstring. The docstring is not
only developer documentation; it is part of the behavior contract exposed to the
agent. It must say whether the tool is an in-turn thinking tool, a non-blocking
task dispatch, a Plan creator, or a memory/sync utility.

### T0 - Reflex / Body Tools

Purpose:

- Small body or scene actions that preserve conversational continuity.
- Examples: movement, animation, mode/scene controls.

Conversation feel:

- Should feel immediate.
- Should not require long reasoning.
- Should not create a Plan unless the user explicitly asks for a coordinated
  multi-step action.

Manual requirements:

- State expected latency.
- State whether the action is reversible or purely local.
- State whether it can be called during speech without creating a "thinking"
  state.

### T1 - Intent / Thinking Tools

Purpose:

- Quick context reads or small drafts that GOSLO uses while actively thinking in
  the user's turn.
- These can block the conversation briefly in a felt, natural "let me check"
  state.
- Calendar read is a good candidate here because it is expected to be fast
  enough for an Intent turn.

Examples:

- Future `calendar_context`: get today's/relevant schedule context for the
  current Intent.
- `query_memory` when the user asks if GOSLO remembers something.
- Scene/status lookups used to make an immediate recommendation.

Conversation feel:

- GOSLO is still the one thinking and reporting.
- The result should return compact context, not a paper note.
- If the tool becomes slow, it should fall back to T3 task dispatch instead of
  freezing the conversation.

Manual requirements:

- Say "use when GOSLO needs this context before answering."
- Say whether the tool may briefly block the turn.
- Say the maximum expected latency and fallback.
- Say what state may be synced to IntentWorkspace/L1.5/L2-B.
- Say that the tool is not allowed to perform destructive writes unless it
  explicitly creates a HITL/Plan gate.

### T2 - Intent Plan Tools

Purpose:

- GOSLO thinks through the plan itself and creates a structured Plan with
  nanobot task steps, triggers, and HITL gates.
- This is still an Intent-layer action: the voice agent owns the recommendation
  and reports it to the user.

Use when:

- The user is present and wants GOSLO to decide with them.
- The plan is small enough for GOSLO to reason about in the current interaction.
- The outcome should feel like GOSLO saying: "I think we should do A, then B,
  and I need your confirmation before C."

Result route:

- Plan draft/staged ref in IntentWorkspace.
- Pending HITL gate when user confirmation is needed.
- Nanobot tasks are steps inside the Plan, not the whole decision maker.
- L2-B sync is a working-memory projection of the Plan/blackboard/workspace
  state, not the Plan SSOT.

Manual requirements:

- State that GOSLO is the planner and speaker.
- State which steps become nanobot tasks.
- State which steps require HITL.
- State how results return to GOSLO/User.

### T3 - Task Dispatch Tools

Purpose:

- Non-blocking background work delegated to nanobot through Scheduler.
- This is the existing `dispatch_task` category.

Use when:

- Work may take time, use external MCP/API tools, search the web, summarize,
  fetch Calendar data asynchronously, or perform a multi-step operation better
  handled by a worker.
- GOSLO can naturally continue the conversation after dispatch.

Conversation feel:

- GOSLO says the task was sent and can continue talking.
- Completion should return as a result receipt, paper note, Plan step result,
  or later voice summary.

Manual requirements:

- Say "do not use this when GOSLO needs the answer before replying."
- Say "use this when the work can complete later."
- Require structured `params` and a `result_channel`.
- For destructive tasks, require prior user confirmation or a Plan/HITL gate.
- Explain that task state is monitored through Scheduler/nanobot/result ledgers,
  not L2-B.

### T4 - Nanobot Plan Tools

Purpose:

- Ask nanobot to think and produce a Plan or recommendation.
- This is different from T2 because nanobot is the planner/reporter, while
  GOSLO mainly routes the request and later presents or mediates the result.

Use when:

- Planning requires long research, external data, comparison, or slow MCP calls.
- The user can wait for a paper note/report instead of immediate GOSLO
  reasoning.

Result route:

- Nanobot report paper note / workflow result intake.
- User "stamp" or HITL approval can promote the plan to execution.
- GOSLO can summarize the note and ask for confirmation, but the first plan
  artifact came from nanobot.

Manual requirements:

- State that nanobot owns the plan draft.
- State that GOSLO should not pretend it has already completed the reasoning.
- State where the report appears and how the user approves it.

### T5 - Sync / Memory Buffer Tools

Purpose:

- Keep IntentWorkspace, Blackboard, L1.5, L2-B, and Graphiti aligned enough for
  retrieval and association.

Use when:

- A source result needs to become visible to working memory.
- A Plan or task result should be available as contextual memory.
- The system needs graph attention, salience, or bounded subgraph context.

Non-goal:

- These tools do not decide the task truth.
- They do not replace Plan/HITL/nanobot receipts.
- They should not hard-sync every transient field into L2-B.

Manual requirements:

- State source of truth.
- State what is projected and what remains a pointer.
- State whether Graphiti audit Episodes are written or only drafted.

## Plan Tool Split

There are two Plan paths and they must not be confused.

### GOSLO Intent Plan

- GOSLO thinks in the current interaction.
- GOSLO creates or requests a Plan draft.
- GOSLO speaks the recommendation to the user.
- Plan can contain many nanobot tasks and HITL gates.
- This is appropriate for "help me decide how to arrange today" when the user
  expects a conversational decision partner.

### Nanobot Task Plan

- GOSLO dispatches a planning task to nanobot.
- Nanobot performs the slow reasoning/research and returns a paper note/report.
- The user approves/stamps the nanobot report before execution.
- This is appropriate for "research all constraints and propose a schedule"
  when the work can happen in the background.

## Calendar Tool Placement

Calendar read:

- Usually T1 Intent/Thinking.
- It is fast enough to be part of GOSLO's thought turn.
- It should be able to refresh from ECS/Nanobot/API when needed and then expose
  compact state to GOSLO.

Calendar planning:

- T2 if GOSLO should reason with the user now.
- T4 if nanobot should research/optimize and return a paper note.

Calendar write:

- Never a casual direct write.
- Should enter IntentWorkspace as an Intent/Plan draft first.
- `calendar_change_request` only stages that draft. It is not an execution
  tool, does not write Calendar, does not dispatch nanobot, and does not import
  or mutate L1.5/L2-B/Graphiti.
- After Plan/HITL approval, GOSLO/Plan decides the route:
  T1 direct Google Calendar API for normal fast software-style changes, or
  T3 Nanobot/Scheduler when the operation is slow, complex, needs richer
  receipts, or belongs to AgentTeam/Plan workflow.
- After execution, sync the result back to IntentWorkspace and optionally into
  L1.5/L2-B/Graphiti as working-memory or audit projection. These memory layers
  are not the Calendar task SSOT.

## Tool Documentation Template

Each new or upgraded GOSLO tool should document:

- Category: T0/T1/T2/T3/T4/T5.
- Owner: GOSLO, PlanRegistry, Scheduler, Nanobot, Web operator, or sync layer.
- Conversation blocking: immediate, brief thinking, or non-blocking.
- When to use.
- When not to use.
- Write authority and confirmation rules.
- Result destination: voice reply, IntentWorkspace ref, Plan step, paper note,
  L1.5 observation, L2-B projection, Graphiti Episode, or Web receipt.
- Failure behavior and fallback.
- Example call shape.

## Current Dispatch Task Verdict

`dispatch_task` is a usable T3 foundation. It can already send Calendar-related
task types to Scheduler/nanobot, and it can return a task id quickly so GOSLO
can continue the conversation. It still needs future upgrades around typed task
schemas, result-contract selection, and safer Calendar write preconditions, but
it is not blocked for non-destructive background work.

## Implementation Ledger

### 2026-05-18 - T1 `calendar_context`

Implemented the first GOSLO-facing Calendar Intent/Thinking tool:

- File: `src/parrot/brain/tools/calendar_context.py`.
- Registration: `src/parrot/brain/tools/__init__.py`.
- Category: T1 Intent / Thinking.
- Default read path: official Google Calendar OAuth API via the existing
  `fetch_google_calendar_api` receipt helper.
- Optional read path: ECS Nanobot MCP read via `fetch_source=nanobot`, or
  `fetch_source=auto` to try API first then Nanobot.
- Result shape: compact text for GOSLO, with event summaries, read model,
  source used, and source-to-DSG memory buffer preview.
- Mutation policy: read-only. No Google Calendar write, no L1.5 import, no
  L2-B mutation, and no Graphiti write. Non-preview sync requests are
  explicitly downgraded to preview in the returned text.
- Safety/fallback: slow or failed reads return a compact failure message telling
  GOSLO to dispatch a background `calendar_fetch` task if the answer is not
  needed before replying.

### 2026-05-18 - Live Tool Blocking Research And T1/T3 Correction

Primary research sources:

- LiveKit Agents async tools:
  https://docs.livekit.io/agents/logic/tools/async/
- LiveKit Agents function tools:
  https://docs.livekit.io/agents/logic/tools/definition/
- LiveKit Agents turn/interruption handling:
  https://docs.livekit.io/agents/logic/turns/
- Gemini Live API tool use:
  https://ai.google.dev/gemini-api/docs/live-api/tools

Finding:

- LiveKit regular function tools block the agent's next turn until all pending
  tool calls return. LiveKit's intended non-blocking primitive is
  `AsyncToolset`, where the tool gives an early update and then runs in the
  background.
- Gemini Live function calling is sequential by default. The model waits for a
  `FunctionResponse` before continuing. Gemini Live has non-blocking function
  declarations for models that support them, but the client/framework must wire
  that behavior explicitly.
- Therefore a plain LiveKit `@function_tool` on top of Gemini Live should be
  treated as blocking unless we either use LiveKit `AsyncToolset`, Gemini
  non-blocking functions, or implement an app-level quick-return fallback.

Design verdict for current GOSLO Calendar tool:

- Keep `calendar_context` as T1 Intent/Thinking, but only within a short
  thinking budget.
- If the Google Calendar API/Nanobot read returns inside budget, GOSLO uses the
  result in the same turn.
- If it times out or fails, `calendar_context` immediately dispatches a T3
  `calendar_fetch` task and returns a task id, so GOSLO can tell the user that
  Calendar is being checked in the background and continue speaking.
- This is an app-level compatibility bridge until we decide whether to adopt
  LiveKit `AsyncToolset` or Gemini Live `NON_BLOCKING` tool declarations for a
  broader async tool layer.

Implementation correction:

- `src/parrot/brain/tools/calendar_context.py` now wraps API/Nanobot reads with
  the shared `with_budget()` staged-tool helper.
- Default T1 budget is 2.5 seconds, capped between 0.05 and 5.0 seconds.
- Slow or failed reads dispatch `calendar_fetch` with `priority=high`,
  `result_channel=calendar_result`, `source=calendar_context_t1_fallback`, and
  `sync_policy=preview`.
- The fallback is still read-only: no Google Calendar write, no L1.5 import, no
  L2-B mutation, and no Graphiti write happen inside the T1 tool.

### 2026-05-18 - GOSLO Calendar Draft And Status Tools

Implemented the next two GOSLO-facing Calendar tools:

- `calendar_change_request`
  - File: `src/parrot/brain/tools/calendar_change_request.py`.
  - Category: T2 Intent Plan / HITL draft.
  - Purpose: convert GOSLO's proposed Calendar create/patch/delete decision
    into an IntentWorkspace `calendar_draft` paper note.
  - Supported action normalization: create/add/insert/new -> `create`;
    patch/update/edit/modify -> `patch`; delete/remove/cancel -> `delete`.
  - Draft payload records the Intent decision, Plan/step ids when provided,
    HITL requirement, allowed execution routes after approval, and a suggested
    Nanobot task type only for the optional T3 background route.
  - Mutation policy: no direct Google Calendar write, no Nanobot dispatch, no
    L1.5 import, no L2-B mutation, and no Graphiti write. It only stages the
    decision payload for later user/Plan/HITL approval.

- `calendar_task_status`
  - File: `src/parrot/brain/tools/calendar_task_status.py`.
  - Category: T1/T3 monitor.
  - Purpose: let GOSLO check whether a Calendar background task has returned
    without blocking conversation.
  - Read model: bounded Redis ledgers only:
    `parrot.nanobot.dispatch` and `parrot.trigger.results.stream`.
  - It can show a specific `task_id` or recent Calendar task/result rows.
  - Mutation policy: no Google Calendar write, no Nanobot dispatch, no L1.5
    import, no L2-B mutation, and no Graphiti write.

Registration:

- Both tools are exported in `src/parrot/brain/tools/__init__.py`, included in
  `ALL_TOOLS`, and included in `tools_for_active_model()` so GOSLO can see
  them on both body-capable and non-body model profiles.

Current minimal GOSLO Calendar tool surface:

- `calendar_context`: quick T1 schedule read with T3 fallback.
- `calendar_change_request`: T2 draft/HITL staging for writes.
- `calendar_task_status`: quick monitor over background task/result ledgers.

### 2026-05-18 - User Correction: Calendar Draft Is Intent Decision, Not Forced T3

User correction to preserve:

> `calendar_change_request` 是 Intent 层的。
> GOSLO 更多做决策和与用户确定是否要改日程，以及分析是否冲突，来逐步完善 Plan 草稿。
> 具体执行虽然是 T1 很快所以不一定需要 nanobot 来。
> 但也可以决策好就交由 nanobot 做。
> 具体决策 tool 不写死，要让 GOSLO 自己可以决定。
> 要么写清楚，要么直接当成工作流程写，拆成 Plan 和执行。
> 执行要走 T1 还是 T3 自己决定。
> 一般软件的正常流程是 T1，但是我们拆开则自带 fallback，不被阻塞，GOSLO 能自己判断。
> 我们的角色和 AgentTeam 就是这样协作的。

Updated interpretation:

- `calendar_change_request` is an Intent-layer decision/draft tool, not a
  Calendar execution tool and not a forced Nanobot/T3 route.
- GOSLO's primary job here is to reason with the user: whether a change should
  happen, whether it conflicts with current schedule context, and how the
  change should become a Plan/HITL draft.
- The workflow is split into two phases:
  1. **Plan/draft/confirmation phase**: GOSLO uses `calendar_context` and
     user dialogue to analyze conflicts, then uses `calendar_change_request` to
     stage an IntentWorkspace `calendar_draft`.
  2. **Execution phase after approval**: GOSLO/Plan chooses the route based on
     latency, risk, and conversation feel.
- Execution route is deliberately not hardcoded:
  - T1 direct Calendar API execution is the normal software-like path when the
    write is safe, fast, and already approved.
  - T3 Nanobot/Scheduler execution is appropriate when the write should run in
    the background, may be slow, needs richer receipts, or belongs to a larger
    AgentTeam/Plan workflow.
  - T1 tools should keep fallback semantics so the live conversation does not
    freeze if the service is slow.
- `calendar_task_status` lets GOSLO monitor whichever background route exists
  without treating L2-B as the task SSOT.
- L1.5/L2-B/Graphiti sync is still post-result memory/buffer projection, not
  the owner of the Calendar task truth.

Tool wording correction:

- `calendar_change_request` records
  `draft_is_execution_request = false`,
  `execution_route_owner = GOSLO/Plan after Plan/HITL approval`,
  `allowed_execution_routes_after_approval = [T1_DIRECT_GOOGLE_CALENDAR_API,
  T3_NANOBOT_SCHEDULER_TASK]`, and `suggested_nanobot_task_type`.
- The draft keeps the Nanobot task type as a suggested background route, while
  preserving GOSLO/Plan's authority to choose T1 direct execution after HITL
  approval.
