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
- Should not directly own Google OAuth, direct Calendar API mutation, or L2-B
  graph persistence.

Nanobot:

- Background execution worker for complex or slow Tasks.
- Owns Google Workspace MCP/API execution through Scheduler-dispatched task
  types such as `calendar_fetch`, `calendar_create`, `calendar_patch`, and
  `calendar_delete`.
- Returns structured receipts/results to Scheduler/Runtime Flow/IntentWorkspace.

Plan/HITL:

- Plan is the explicit task/decision SSOT for multi-step operations.
- HITL gates are the confirmation boundary for user-visible or destructive
  actions such as writing to Google Calendar.
- Calendar write should be plan/gate-driven, not a direct conversational side
  effect.

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
  `dispatch_task`, `query_memory`, `remember`, `manage_episode`, and scene/App
  controls. There is no dedicated `calendar_context` or
  `calendar_change_request` GOSLO tool yet.
- `src/parrot/brain/tools/dispatch_task.py` already documents calendar task
  types: `calendar_fetch`, `calendar_create`, `calendar_patch`, and
  `calendar_delete`. This is the right low-level execution boundary, but it is
  too generic to be the final GOSLO-facing UX.
- `src/parrot/brain/tools/query_memory.py` uses Graphiti natural-language
  subgraph retrieval and can search `goslo`, `maid`, `scene`, `user`,
  `arknights_test`, and `noble_etiquette` partitions. It is not a Calendar
  status tool.
- `src/parrot/brain/app_first_version.py` has `create_calendar_draft()`, which
  stages a Calendar write action as an IntentWorkspace `calendar_draft` paper
  note. It does not write Google Calendar.
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
2. GOSLO does not call Google Calendar directly. It issues structured commands
   and monitors receipts.
3. Plan/HITL decides whether a Calendar write is allowed.
4. Scheduler dispatches nanobot Tasks for actual Google Calendar operations.
5. Nanobot executes against Google Workspace MCP/API and returns structured
   result receipts.
6. The result is staged back to IntentWorkspace for GOSLO/User visibility.
7. CalendarTrigger/import policy normalizes the result into L1.5 observations.
8. L2-B receives working-memory pointers/attention/subgraph context from
   IntentWorkspace, Blackboard, Plan state, and L1.5 observations.
9. Optional Graphiti audit Episodes record important user-confirmed decisions
   and durable provenance.

This matches the user's framing: Web proves the interfaces; GOSLO provides the
voice/decision loop; nanobot does complex execution; L2-B stays a subconscious
sync/buffer layer rather than the task SSOT.

## Non-Goals For The Next Slice

- Do not make L2-B the authoritative Calendar/task database.
- Do not let GOSLO directly mutate Google Calendar without Plan/HITL policy.
- Do not treat Web-only drafts as runtime truth.
- Do not require Graphiti writes for every Calendar sync pulse.
- Do not assume the App has a finished 2D workspace when defining backend
  Calendar/GOSLO tools.

## Immediate Capability Gaps

1. Dedicated GOSLO Calendar tools are missing.
2. Calendar task schemas are generic strings inside `dispatch_task`, not typed
   GOSLO-friendly commands with result/status receipts.
3. Calendar write-back through nanobot is documented as a task type but is not
   yet proven as a Web/GOSLO/HITL end-to-end path.
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

The first implementation should be read/preview/draft first, then one
operator/HITL-gated write path, then automatic state sync to IntentWorkspace,
L1.5, and L2-B.
