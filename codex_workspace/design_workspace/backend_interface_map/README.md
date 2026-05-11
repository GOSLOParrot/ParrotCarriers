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
| Unity App | `unity/ArSpike/Assets/Scripts/ParrotApp/` | 正式 App 脚本工作区。 |
| Unity Testbed | `unity/ParrotDev/` | 冻结测试床，不作为新 App 功能落点。 |
| Nanobot | `../nanobot/` | 外挂 Agent / Google 等工具连接侧。 |

## 后端协作一句话

Unity 通过 LiveKit 与 Brain 实时通信；Brain 用 tools / IntentWorkspace 做语义决策；Scheduler 负责长任务和行为树路由；Nanobot 处理后台 / 外部工具任务；DSG 把 Obsidian、照片、Google 日程等 Ref 源规整到 L1.5 桶和 L2-B 潜意识图；Memory / Graphiti 负责长期记忆和检索。
