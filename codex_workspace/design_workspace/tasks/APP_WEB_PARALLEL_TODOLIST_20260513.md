# App/Web Parallel TODO Board (2026-05-13)

This board coordinates two parallel chats. It starts intentionally empty:
the App chat and Web chat decide their own TODO lists with the user inside
their own conversations.

Workflow rules:

- Do not add implementation tasks here until the owning chat has scoped them.
- Use this board for status, ownership, blockers, and links.
- Put detailed business-interface notes in the lane directories under
  `codex_workspace/design_workspace/backend_interface_map/`.
- Put proposed shared core interfaces in
  `codex_workspace/design_workspace/backend_interface_map/core_interface_candidate_queue_20260513.md`.

## Status Legend

| Status | Meaning |
|:--|:--|
| `intake` | Mentioned or discovered, not yet scoped by the owning chat. |
| `proposed` | Owning chat proposed it; waiting for user decision. |
| `approved` | User agreed; ready for implementation planning in that chat. |
| `in_progress` | Owning chat is actively implementing or validating. |
| `blocked_core` | Needs a new shared core interface candidate. |
| `blocked_cross_lane` | Needs the other chat/lane. |
| `done` | Implemented or documented with an observable verification signal. |
| `deferred` | Postponed with a short reason. |

## App Lane

Owner: Unity App chat.

| ID | Status | Item | Business doc | Core candidate | Notes |
|:--|:--|:--|:--|:--|:--|
| APP-001 | in_progress | Startup / RoomSetting six-axis boundary: `Model`, `Room`, `Persona`, `Line`, `Scene`, `Maid Team`. | `backend_interface_map/app/startup_roomsetting_app_interface_20260513.md` | CORE-001, CORE-002 | `Maid Team` starts as fixed `CatMaid Team` placeholder until core `agent_team_id` / registry is confirmed with the user in this chat. |
| APP-002 | in_progress | START transition boundary: permission checks, token mint, LiveKit connect, `applyRoomProfile`, silent connect success, failure states, and IPoAC/progress placeholder. | `backend_interface_map/app/startup_roomsetting_app_interface_20260513.md` |  | Keep progress/loading as a separate transition page after START, not part of the first startup screen. |
| APP-003 | in_progress | LineB / LiveKit status UI audit: readiness, cold-start/restart requirement, `selection_drift`, echo/voiceprint/TTS status, pause/resume/reconnect visibility. | `backend_interface_map/app/startup_roomsetting_app_interface_20260513.md` |  | Line selection is visible in RoomSetting, but runtime Line hot-swap is not promised; show Brain restart/supervisor boundary clearly. |
| APP-004 | in_progress | Canvas menu boundary: reuse `MenuRegistry`, `canvas_snapshot`, typed Ref/Edge data, and tiered setting actions without hard-coding one renderer. | `backend_interface_map/app/canvas_menu_ref_workspace_app_interface_20260513.md` | CORE-007 | Unity owns touch-first rendering; shared core should stay renderer-agnostic. |
| APP-005 | in_progress | Main ready contract: define which HUD, tool drawer, 2D workspace, photo/focus/BBox, model driver, resource, state, and connection modules must be ready when startup completes. | `backend_interface_map/app/startup_roomsetting_app_interface_20260513.md` |  | Startup is not complete just because LiveKit connects; greeting remains gated by scene ready + explicit placement. |
| APP-006 | in_progress | App-side Ref workspace boundary for future 2D workspace / Red String / Evidence Board partial features. | `backend_interface_map/app/canvas_menu_ref_workspace_app_interface_20260513.md` | CORE-006, CORE-007 | App consumes shared candidates and may help refine them with the user here; do not directly write Graphiti/FalkorDB/L2-B from Unity App DTOs. |
| APP-007 | done | Unity App scene/folder hygiene: isolate Smoke scene/scripts under `Assets/Tests/Smoke/**`; keep formal App entry under `Assets/ParrotApp/Scenes/ParrotApp_Startup.unity`. | `backend_interface_map/app/README.md` |  | Formal scene is clean and non-Smoke: Camera, Directional Light, `ParrotAppRoot`; Unity console verified with zero errors/warnings. |
| APP-008 | in_progress | Startup visual/material audit for horizontal phone first screen, RoomSetting entry, START transition, and placeholder loading/progress style. | `backend_interface_map/app/startup_roomsetting_app_interface_20260513.md` |  | Use existing design sources; MagicalUI is the primary candidate family, with wood/paper/adventure as accents. Do not implement final Unity UI until the user approves the finished design image. |

## Web Lane

Owner: Web Console chat.

| ID | Status | Item | Business doc | Core candidate | Notes |
|:--|:--|:--|:--|:--|:--|
| WEB-001 | done | Web Console requirements summary, information architecture, visual direction, and implementation TODO list. | `backend_interface_map/web_console/web_console_step1_console_plan_20260513.md` |  | Step 1 docs and directory discipline are in place. Split visual language remains: Obsidian-like console first; Papers Please-inspired interaction layer later. |
| WEB-002 | done | ECS/module health and orchestrator `/status` console skeleton. | `backend_interface_map/web_console/observability_runtime_business_flow_20260513.md` | CORE-003 | Implemented BFF/static shell in `src/parrot/web_console/` + `web/console/`; includes status topology and zh/en setting. When `PARROT_ORCH_SECRET` is set, BFF sends `Authorization: Bearer <secret>`. |
| WEB-003 | approved | L1.5 management, L2-B visualization, node CRUD boundary, and photo management read model. | `backend_interface_map/web_console/memory_graph_workspace_business_flow_20260513.md` | CORE-006, CORE-008 | Read-only first. L1.5 management is shared with the App phone/menu path; Web-only node/photo operator writes need dry-run/audit. |
| WEB-004 | approved | Blackboard, IntentWorkspace, Plan/task, Scheduler, Nanobot, AgentTeam/Maid Team status monitoring. | `backend_interface_map/web_console/observability_runtime_business_flow_20260513.md` | CORE-001, CORE-002, CORE-003, CORE-004 | Default `CatMaid Team` single-instance path remains observable before dynamic team routing. |
| WEB-005 | approved | GOSLO/Nanobot collaboration, chatroom plan, and task-scheduler monitoring. | `backend_interface_map/web_console/observability_runtime_business_flow_20260513.md` | CORE-004, CORE-005 | Chat observability should expose summaries/status, not raw secrets or upstream channel internals. |
| WEB-006 | approved | Graphiti/FalkorDB management: read, search, partitions, visualization, Episode, Graphiti API node/edge/fact surgery, and FalkorDB operator mode. | `backend_interface_map/web_console/graphiti_management_business_flow_20260513.md` | CORE-006 | FalkorDB direct writes stay Web operator only with dry-run/audit/backup posture. |
| WEB-007 | approved | Web Evidence/String Board using the shared Ref/Edge data model while keeping the Web renderer independent. | `backend_interface_map/web_console/memory_graph_workspace_business_flow_20260513.md` | CORE-006, CORE-007 | Do not invent a separate storage format for board edges; allow Red String and future edge renderers through renderer/style ids. |
| WEB-008 | approved | Web lane doc hygiene and core-change guardrail. | `backend_interface_map/web_console/README.md` |  | Business docs stay under `web_console/`; shared gaps go to the candidate queue, never directly to core SSOT. |

## Shared Blockers

| ID | Status | Blocker | Owner | Linked lane item | Resolution |
|:--|:--|:--|:--|:--|:--|
| _none yet_ | | | | | Add only real cross-lane blockers. |

## Core Candidates Index

Core candidates live in:

`codex_workspace/design_workspace/backend_interface_map/core_interface_candidate_queue_20260513.md`

When approved, move the contract into `.cursor/memory/architecture/Interface/**`
and link the ratified doc back here.
