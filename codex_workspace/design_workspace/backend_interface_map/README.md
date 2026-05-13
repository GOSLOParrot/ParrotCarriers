# 后端设计与业务接口索引

> 用途：让 App / Web / 2D 工作区设计时知道“后端有什么、怎么协作、该看哪些代码和协议、业务接口怎么写”。

## 先读这 6 个源

| 目标 | 文件 |
|:--|:--|
| 后端全局模块和数据流 | `.cursor/memory/architecture/module_map_p2.md` |
| 当前协议字段 / topic / BB key | `.cursor/memory/architecture/protocol_snapshot_p4.md` |
| Bus 三层通信拓扑 | `.cursor/memory/architecture/bus_v4.md` |
| 核心接口纪律 | `.cursor/memory/architecture/Interface/INDEX.md` |
| **接口 bug + 修复 SSOT（3 轮 10 bug）** | **`.cursor/memory/architecture/Interface/audit_log_index_20260511.md`** ← 改 RoomSetting / LineB / ECP / disconnect 前先扫一眼，避免重复踩同型坑 |
| Brain / Menu / Preset / IntentWorkspace 核心接口 | `.cursor/memory/architecture/backend_interface_refinement_20260507.md` |
| 用户 idea + 三大真连接现状 | `.cursor/memory/architecture/user_ideas_and_backend_capability_brief_20260509.md` |

## 设计时的读法

1. 先从 `module_map_p2.md` 看模块职责，不从代码乱猜。
2. 涉及 Unity / Brain wire 时，看 `protocol_snapshot_p4.md` 和 `bus_v4.md`。
3. 涉及菜单画布 / Persona / Preset / IntentWorkspace 时，看 `backend_interface_refinement_20260507.md`。
4. 涉及 Obsidian / Google / PhotoNode / L1.5 桶时，看 `user_ideas_and_backend_capability_brief_20260509.md` 和 `dsg/workspace_index.md`。
5. 需要写业务接口时，用 `business_interface_workflow.md` 的 A-D 模板。
6. **改 RoomSetting / LineB / ECP / disconnect 路径前先扫 `audit_log_index_20260511.md`**：3 轮 10 bug 已修复 + 共性模式（module-level mutable state 必须在 `_on_room_disconnected` 里 reset）已总结，避免重复踩坑。
- 菜单画布外部模块入口：`menu_canvas_external_modules_business_flow.md`。
- 第一版 App 统一业务 facade：`app_v1_core_business_interface_coverage_20260510.md`。

## 2026-05-13 App/Web 并行写入位置

| 路线 | 业务接口写入位置 | 说明 |
|:--|:--|:--|
| Unity App | `app/` | 启动页、RoomSetting、HUD、菜单画布、工具柜、游戏/模型交互、App 侧报告/工作区入口。 |
| Web Console | `web_console/` | ECS/module health、L1.5/L2-B、节点/照片、Blackboard、IntentWorkspace、Plan、Scheduler/Nanobot、AgentTeam/MCP 管理。 |
| Shared core candidates | `core_interface_candidate_queue_20260513.md` | 未获用户确认前只记录候选，不改核心 SSOT。 |

核心接口批准后才写入 `.cursor/memory/architecture/Interface/**`，并带
`source_chat` / `writer` / `approved_by` / `origin_business_doc` 元数据。

## Lane Index Discipline

Each lane directory owns its README index. The root
`backend_interface_map/README.md` points to the lane, and the lane README lists
the active business files.

| Lane | Local index | Rule |
|:--|:--|:--|
| Unity App | `app/README.md` | App chat maintains App business-interface files only. |
| Web Console | `web_console/README.md` | Web chat maintains Web business-interface files only. |

Do not scatter Web Console notes outside `web_console/`. If a temporary
multi-round audit or implementation note is needed, keep it in a clearly marked
temporary folder under the owning lane and promote only durable decisions back
to the indexed business file.

## Active App Business Interface Index

Durable App-facing business interface files live under `app/` and are indexed
again in `app/README.md`.

| File | Scope |
|:--|:--|
| `app/startup_roomsetting_app_interface_20260513.md` | Startup page, RoomSetting, START transition, LineB/LiveKit status, main-ready contract. |
| `app/canvas_menu_ref_workspace_app_interface_20260513.md` | Canvas menu, renderer-agnostic node/edge boundary, App-side Ref workspace. |
| `app/unity_project_inventory_app_ssot_20260513.md` | Unity App directory/resource/scene inventory SSOT and cleanup rules. |

Do not create one-off App interface files for every small step. Add durable
decisions to these module-level files unless ownership or lifecycle changes.

## Active Web Business Interface Index

Durable Web Console business interface files live under `web_console/` and are
indexed again in `web_console/README.md`. The root index only lists the active
Web surfaces; route matrices, completion ledgers, and checkpoint notes stay in
the lane README and module-level Web files.

| File | Scope |
|:--|:--|
| `web_console/web_console_step1_console_plan_20260513.md` | Web Console requirements, IA, Obsidian-like baseline, later Papers Please-inspired interaction lane, and doc hygiene. |
| `web_console/observability_runtime_business_flow_20260513.md` | ECS/module health, orchestrator `/status`, Runtime Monitor, React Runtime Flow Workspace, Blackboard/Plan/Scheduler/Nanobot observability, HITL, LineB voice smoke, and trigger palette. |
| `web_console/memory_graph_workspace_business_flow_20260513.md` | L1.5 pool, L2-B React visual workspace, Blackboard/IntentWorkspace memory renderer, node/photo management, Ref/Evidence Board, and Visual Memory Operations Cockpit. |
| `web_console/graphiti_management_business_flow_20260513.md` | Graphiti/FalkorDB observe/search/episode draft/dry-run and future Web operator surgery. |

Do not create one-off Web interface files for every UI slice. Add durable
decisions to these module-level files, keep implementation checkpoints in
`web_console/README.md`, and send shared core gaps to
`core_interface_candidate_queue_20260513.md`.

## 共性纪律（2026-05-11 audit 三轮总结）

> **任何在 `parrot/brain/**` 里声明的 module-level mutable state（`_dict` /
> `_list` / `_set` / `OrderedDict`）必须在同一 PR 里同时：**
> 1. 添加 `reset_*_on_session_end()` 函数
> 2. 在 `agent.py::_on_room_disconnected` 完成 wire-up
>
> 否则就是潜伏 dead code，下次 disconnect 时旧 session 的尾巴污染下一个
> session 的开头。本仓库已经在 RefBinding / LineB audio guard / EcpState
> ingest 三处踩过这个坑（详见 `audit_log_index_20260511.md` §3）。

## 代码入口速查

| 模块 | 代码入口 | 设计含义 |
|:--|:--|:--|
| Brain | `src/parrot/brain/` | Gemini Live、工具调用、菜单 / preset / persona、IntentWorkspace。 |
| Bus | `src/parrot/bus/` + `src/parrot/shared/constants.py` | 模块挂载、Redis 通道、长任务派发基础设施。 |
| Scheduler | `src/parrot/scheduler/` | py-trees 行为树、Nanobot 任务路由、黑板。 |
| DSG | `src/parrot/dsg/` | L1.5 Pool / Buckets / RefTable、L2-B 图、触发器、ingest filters。 |
| Memory | `src/parrot/memory/` | Graphiti / FalkorDB / 对话归档。 |
| Unity App | `unity/ArSpike/Assets/ParrotApp/` | 正式 App 脚本工作区。 |
| Unity Testbed | `unity/ParrotDev/` | 冻结测试床，不作为新 App 功能落点。 |
| Nanobot | `../nanobot/` | 外挂 Agent / Google 等工具连接侧。 |

## 后端协作一句话

Unity 通过 LiveKit 与 Brain 实时通信；Brain 用 tools / IntentWorkspace 做语义决策；Scheduler 负责长任务和行为树路由；Nanobot 处理后台 / 外部工具任务；DSG 把 Obsidian、照片、Google 日程等 Ref 源规整到 L1.5 桶和 L2-B 潜意识图；Memory / Graphiti 负责长期记忆和检索。

