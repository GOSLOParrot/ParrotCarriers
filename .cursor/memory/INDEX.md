# ParrotCarriers 全局索引

> 用途: 项目唯一真相源，供 Cursor 与用户快速定位关键信息
> 更新: 2026-05-07 (DSG Chat 2 + GOSLO 模块化 双 chat 收口 → 跨 chat 待办登记表落地；408/408 pytest；Phase 4 §8 + cs_parity 4/4 + ADR-L1.5-001 11/11 三守护通过；模块化产出 14 + 改动 5 + 新测试 118/57；App 完成度总 chat 主 doc + Sub-Chat A/B 入场 prompt + 像素画 UI 资产清单；**P2.5 App 设计 + 接口/能力 提炼 pre 产物**：Interface/ 工作区 5 份文件（接口设计 v0 + 补丁 + 概念词典 + 遗留问题 + 菜单设计）；新增 P2.5 需求：2D 工作区（nanobot 汇报 + Google 日程批改 + 工作区模块连接）)
> 路由: 由 `.cursor/rules/workspace.mdc` (alwaysApply) 指向本文件

**全局约定**:
- **事实源**: 只有 `.cursor/memory/**`。`docs/InfoCollections/**` 是**文档库/考古资料**, 按需 `@` 引用, 不作事实源。
- **两个维度**: 每份架构文档 frontmatter 含 `status` (tentative/ratified/archived/superseded) + `category` (active/reference/archived/historical)。读之前先看 frontmatter。
- **不读 archived**: 除非在追溯历史决策。

---

## 〇、当前阶段必读 (按序, 不读后续)

> **原则**: 进入任何 Sprint 前, **只读这几份**, 不翻历史。
> **当前**: Sprint 4 Phase 4 **完成** → Phase 5 转换期 (2026-05-04) → DSG Chat 2 + GOSLO 模块化收口 (2026-05-06) → 跨 chat 待办登记表 + **P2.5 App 设计 + Interface 接口提炼 pre** (2026-05-07)
> **Phase 4→5 补读**（下游 chat 必读，接口提炼 / dsg 动代码前）: `adr_protocol_upgrade_and_interface_refinement_background_20260504.md` + `adr_l1_5_source_dispatch_extension_space_20260504.md`
> **DSG 系列设计 chat 入场必读**: `architecture/dsg/workspace_index.md` → `dsg_current_state_distilled.md`（与 AR 工作区对位）
> **下游 chat（Chat 4 / DSG 协议升级 / AR menu / P3 wire ADR）入场必读**: ⭐ `architecture/cross_chat_pending_registry_20260507.md` — 三大 chat（Sprint4 / DSG Chat 2 / GOSLO mod）完成后的统一 TODO + NEED 登记表，含 grep 索引 / 严重度 / 修复 chat 路径表
> **App 完成度审计入场**（Sub-Chat A / B 启动前必读 + 任何 user-visible 流程 chat 启动前必读）: ⭐ `architecture/app_completion_master_audit_20260507.md` — 8 场景对账表是 user-visible 完成度的 SSOT；§6 像素画 UI 资产清单是 user 自管美术依据
> **Interface 工作区**（P2.5 App 设计 + 接口/能力提炼 pre；Sonnet 4.6 实施 + Opus 4.7 ×2 调研）: `architecture/Interface/` — 5 文件（接口设计 v0 + 补丁 + 概念词典 + 遗留问题 + 菜单设计）；**任何 user-visible UI / 接口提炼 / 命名审计 / 菜单实施 chat 必读**
> **新 P2.5 需求**（2026-05-07）: 2D 独立工作区（nanobot 汇报 + Google 日程批改 + 工作区模块连接）— 见 `architecture/Interface/legacy_issues_split_20260507.md §1` + 本表 §〇 第 12 行

| # | 文件 | 读什么 |
|:--|:-----|:-------|
| 1 | `.cursor/memory/architecture/module_map_p2.md` | **全景架构入口** — §〇 项目边界 / §一 模块清单 / §二 数据流 / §九 外挂生态 / §十 DSG 分层 / §十一 时间轴 |
| 2 | `.cursor/memory/active_context.md` | 头部 + 本周关键路径 (先确认自己在哪一步) |
| 3 | `.cursor/memory/architecture/sprint4_pre_entry_prompt_and_plan.md` | Sprint4 前置、测试束隔离、数据流 / 协议 V2 / 后端接口提炼 |
| 4 | `.cursor/memory/architecture/sprint4_protocol_ecp_background_20260429.md` | Sprint4 协议 / ECP 背景锚点：用户原话、RIT/BT/BT 森林关系、DSG/Graphiti/Obsidian/Ref 边界 |
| 5 | `.cursor/memory/architecture/sprint4_protocol_v2_ecp.md` | Sprint4 Protocol V2 / ECP 正式设计稿：最小合同、状态面、生命周期、实现顺序 |
| 6 | `.cursor/memory/architecture/sprint4_phase4_entry_20260430.md` | ⭐ **Phase 4 入场锚点（authoritative）** — Sprint4 终极目标 + 验收 / Phase 1-3 已落地清单 / 协议整体性 7 个再理解点 / 行为矩阵填表起点 / 观察者 vs 注意力模块边界 / 启动序 / Ref 路由 |
| 7 | `.cursor/memory/architecture/sprint4_phase3_l3_entry_20260429.md` | Phase 3 L3 收口承接（已完成）— L1+L2 + 4 组拆分 + R1-R6+D5 audit fix；Phase 4 主线**承接**而非**重读** |
| 8 | `.cursor/memory/architecture/ar_app_flow_ui_design.md` | 当前 App Flow / UI / 功能入口设计基线 |
| 9 | `.cursor/memory/architecture/dsg/workspace_index.md` | **DSG 工作区入口**（2026-05-04 新增；2026-05-06 增补决策总表 + 4 新 skill + NewZone 素材池）— DSG 系列设计 chat（L1.5 池 / lifecycle / L2-B 升级 / Phase 5+ A10）入场必读；与 AR 工作区对位。冷读完 `dsg_current_state_distilled.md` 一份能回答 DSG 全景；用户已决事项进 `dsg_decisions_master.md`（master，长期累加） |
| 10 | ⭐ `.cursor/memory/architecture/cross_chat_pending_registry_20260507.md` | **跨 chat 待办登记表（master）** — 三大 chat（Sprint4 主线 / DSG Chat 2 / GOSLO 模块化）完成后的统一 TODO + NEED 标签登记。覆盖 16 文件 26 处源码标签 + 4 P2.5 NEED + 8 P3 NEED + 6 修复 chat 路径表。任何下游 chat 入场前先读 §5 找自己的标签清单。**新 NEED 标签必须先入本表再加到源码注释。** |
| 11 | ⭐ `.cursor/memory/architecture/app_completion_master_audit_20260507.md` | **App 完成度 + DSG 必要升级 总 chat 主 doc**（2026-05-07）— 8 场景对账表（涉及模块 / 已交付能力 / 缺口 NEED-* / 派发）+ 5 个发现 + Sub-Chat A/B 派发清单 + **像素画 UI 资产清单**（user 自管美术 9 类 30+ 项）。Sub-Chat A（`app_flow_requirements_interface_chat_launch_prompt_20260507.md`，用户视角）+ Sub-Chat B（`backend_interface_refinement_chat_launch_prompt_20260507.md`，后端模块视角）入场必读；上一轮"接口提炼几乎只是把仓库复制了一半"失败后的纠偏产物。 |
| 12 | ⭐ `.cursor/memory/architecture/Interface/` | **Interface 工作区**（P2.5 App 设计 + 接口/能力提炼 pre，2026-05-07）— 5 文件：① `interface_design_and_how_todo_v0_20260507.md`（接口设计 v0，12 场景+4 横切，Sonnet 4.6 抄码主表）② `interface_design_supplement_20260507.md`（v0 补丁+7 项新发现+完整性确认）③ `concept_dictionary_20260507.md`（≈100 项术语+设计文档路由指引）④ `legacy_issues_split_20260507.md`（遗留问题 P2.5/P3 二分，含新 P2.5：**2D 独立工作区** = nanobot 汇报批改 + Google 日程批改 + 工作区模块连接）⑤ `menu_design_complete_20260507.md`（完整菜单设计 SSOT）。任何 user-visible UI / 接口提炼 / 命名审计必读。 |

---

## 一、按类别索引

### 1.1 active — 本周活跃, 边读边写 (status: tentative)

> 这些文件在跟代码和 Sprint4 前置同步演进，读时注意 frontmatter 的 `status_note`。

| 文件 | 说明 |
|:-----|:-----|
| `active_context.md` | 当前进度 + 本周关键路径 + 版本锁表 |
| `architecture/ar_feature_vision.md` | 门控 + 自知 + 两轴 + §3.5 三合一 + §六 决策 (tentative 直到 Sprint 1/2 代码落地) |
| `architecture/ar_feature_implementation_plan.md` | Sprint 0-4 任务清单 + 依赖图 (逐 Sprint ratified) |
| `architecture/sprint4_pre_entry_prompt_and_plan.md` | Sprint4 前置入口：测试束隔离、数据流升级、协议 V2 / ECP、DSG L2-B、后端接口提炼 |
| `architecture/sprint4_protocol_ecp_background_20260429.md` | Sprint4 Protocol / ECP 背景锚点：保留用户关键原话、三条任务交集、RIT/BT/BT 森林与 Ref 边界 |
| `architecture/sprint4_protocol_v2_ecp.md` | Sprint4 Protocol V2 / ECP 正式设计稿：ECP 最小合同、状态面、Snapshot/Sighting/RefBinding、Lifecycle/Audio、BT 对齐与实施顺序 |
| `architecture/sprint4_ecp_minimal_audit_20260429.md` | ECP-minimal 第一批落地后的审计与漂移记录：A1-A5 / B1-B5 / C 段，附 Phase 2 入场清单（archived，但 Phase 2 启动前必读） |
| `architecture/sprint4_phase3_l3_entry_20260429.md` | Phase 3 L3 入场锚点（**已收口承接**）— L1+L2 已完成内容、4 组拆分（foundations / chokepoint+transport / publishers / consumers）、ParrotApp 命名空间约定、§7.5 R1-R6+D5 audit 修复记录 |
| `architecture/sprint4_phase4_entry_20260430.md` | ⭐ **Phase 4 入场锚点**（authoritative）— Sprint4 终极目标重申 + 验收口径 / Phase 1-3 落地清单 / 协议整体性 7 个再理解点（含 §3.3 行为矩阵 + §3.7 观察者 vs 注意力模块边界）/ 启动序 / 给新 chat 的开局 prompt |
| `architecture/ar_app_flow_ui_design.md` | AR App Flow / UI / 功能入口当前设计基线 |
| `architecture/dsg/workspace_index.md` | **DSG 工作区入口**（2026-05-04 新建；2026-05-06 增补）— DSG 系列设计 chat 单一入场点；与 `ar_workspace_index.md` 对位 |
| `architecture/dsg/dsg_decisions_master.md` | **DSG 决策总表**（master，2026-05-06 新建，长期累加）— Chat 2 入场 SSOT；用户已决事项 + status 分级（ratified / provisional / deferred-to-design / deferred-to-P3 / tbd）|
| `architecture/dsg/dsg_current_state_distilled.md` | **DSG 当前全景理解快照**（核心，2026-05-06 增补 §11 防爆炸门控分层 + §12 工作记忆延迟归档）— 冷读完一份能回答 DSG 全景 |
| `architecture/dsg/opus_dsg_residual_intent.md` | Opus 09/11/12/17/18/19 仍生效的设计意图蒸馏（distill+cite）— 2026-05-06 修正 attention 双开放路径 |
| `architecture/dsg/source_x_lifecycle_status.md` | 7 项现有 source + Obsidian 三分类 + GOSLO 主动 + A10 占位的 lifecycle 处理现状对照表（2026-05-06 增补 Q2.x 已决条目）|
| `architecture/dsg/open_questions_for_design_chat.md` | Chat 2 需回答的开放问题（含用户 Q&A 原文）；§0 已决汇总指向 dsg_decisions_master.md |
| `architecture/dsg/dsg_l1_5_pool_design_chat_launch_prompt_20260506.md` | **Chat 2 启动 prompt**（2026-05-06 新建）— 入场必读 / scope / 锁 / 提问纪律 / 输出物 / 开局 prompt |
| `architecture/lineb_implementation_completion_20260504.md` | **Line B 完成报告**（Sprint 4 Phase 5+）— STT-LLM-TTS 双管线兼容性验证；Phase 4 §8 0 漂移；234/234 pytest |
| `architecture/sprint4_phase4_completion_and_final_audit_20260430.md` | **Phase 4 完成报告 + 终一致性审计** — 234/234 pytest + Echo/Photo 全链路 + §8 决策锁 13 条 0 漂移。所有下游 chat 入场必读 |
| `architecture/sprint4_phase4_online_smoke_completion_20260504.md` | **联机 smoke 收口**（2026-05-04）— smoke #3/#4/#5 ✅；#1/#2 显式 defer 到真机集成测试 |
| `architecture/sprint4_phase4_downstream_chat_dispatch_plan_20260504.md` | **全下游 chat 派发地图** — Step 1-7 顺序 + 各 chat 角色 / 输入 / 输出边界 |
| `architecture/adr_protocol_upgrade_and_interface_refinement_background_20260504.md` | **ADR-PROTOCOL-INTERFACE-001**（fork chat 产出）— Sprint4 协议升级总结 + 接口提炼任务输入。下游接口提炼 chat 必读；不修改 Phase 4 锁定值 |
| `architecture/adr_l1_5_source_dispatch_extension_space_20260504.md` | **ADR-L1.5-SOURCE-DISPATCH-001** — Q1 SemanticNode.source 字段边界 + Q2 Meta dict/factory hook 扩展空间 + Q3 chat 路径锁。**任何动 dsg/ 的 chat 必读** |
| `architecture/sprint4_deferred_issues_and_bugs_20260504.md` | Phase 4 遗留问题 + pre-existing breakage 汇总（独立审计 chat 处理）|
| `architecture/dsg_skill_seeker_l1_5_a10_l2a_20260504.md` | ConceptGraph 蒸馏任务包（派出独立 workspace，Chat 1）|
| `architecture/app_completion_master_audit_20260507.md` | **App 完成度总 chat 主 doc** — 8 场景对账 + Sub-Chat A/B 派发 + 像素画 UI 资产清单 |
| `architecture/app_flow_requirements_interface_chat_launch_prompt_20260507.md` | Sub-Chat A 启动 prompt（用户视角 App Flow + 新 P2.5 2D 工作区子任务）|
| `architecture/backend_interface_refinement_chat_launch_prompt_20260507.md` | Sub-Chat B 启动 prompt（后端模块视角 + 新 P2.5 Google 日程桶联动子任务）|
| **`architecture/Interface/interface_design_and_how_todo_v0_20260507.md`** | **接口设计 v0（P2.5 pre）** — 12 场景+4 横切关注点；Sonnet 4.6 抄码主表 |
| **`architecture/Interface/interface_design_supplement_20260507.md`** | **接口设计补丁** — v0 之外 7 项新发现 + 完整性确认 + 文档索引段落 |
| **`architecture/Interface/concept_dictionary_20260507.md`** | **概念词典** — ≈100 项术语 + 设计文档路由指引 |
| **`architecture/Interface/legacy_issues_split_20260507.md`** | **遗留问题二分（含新 P2.5：2D 工作区）** — P2.5 要解决（30+ 项）+ P3（40+ 项）+ grep 速查 + 修复 chat 派发表 |
| **`architecture/Interface/menu_design_complete_20260507.md`** | **完整菜单设计 SSOT** — 三层架构 + 4 类块 + 预设系统 + 海盗换肤 + 像素画素材清单 |

### 1.2 reference — 当前稳定事实源 (status: ratified)

> 新决策不翻这些旧决策, 只能追加或 bump 版本号。

| 文件 | 说明 |
|:-----|:-----|
| `architecture/module_map_p2.md` | **模块 P2.5 成熟度矩阵** (优先看这份, 不看 module_division.md) |
| `requirements.md` | **67 功能项 + 11 个已确认决策** (需求事实源) |
| `architecture/bus_v4.md` | **Bus v4.2 三层协议 + 拓扑** |
| `architecture/protocol_snapshot_p1.md` | **V1 协议定版** (RPC/Redis/DataChannel/Blackboard) |
| `architecture/scene.md` | 家族角色拓扑 (GOSLO / Maid / Parrot / Gemini 二重身) |
| `parrot_behavior_rules.md` | 鹦鹉行为状态机 + 兼容矩阵 |
| `architecture/ar_camera_interaction_survey.md` | AR 摄影互动问卷 (已回填, 不再改) |
| `architecture/audit_identify_object_no_screenshot_20260420.md` | identify_object 审计 (Sprint 4 执行) |
| `architecture/ar_skill_seekers_distillation_report.md` | AR Foundation 5.1 蒸馏报告 |
| `BigIssue.md` | 协议污染复盘 + 设计护栏 (永久护栏) |
| `deploy_snapshot_p2_20260412.md` | Castle 部署快照 |
| `commit_guidelines.md` | 提交规范 + 漂移说明子句 |
| `milestone_p2.md` | P2/P2.5 里程碑 (已完成, 历史归档) |
| `architecture/ar_app_plan.md` | 早期 AR 工程计划 + 问卷追溯；新的 App Flow / UI 以 `architecture/ar_app_flow_ui_design.md` 为准 |

### 1.3 archived — 已归档, 仅作历史追溯 (status: archived / superseded)

> **不读**, 除非明确要追溯早期决策。读时会看到文件顶部的归档提示。

| 文件 | 归档原因 |
|:-----|:---------|
| `architecture/system_core.md` | v3 愿景 (2026-03-18), 被 `module_map_p2.md` + `protocol_snapshot_p1.md` 覆盖 |
| `architecture/module_division.md` | Phase 1 基线 (2026-04-08), 被 `module_map_p2.md` 覆盖 |
| `architecture/gemini_drive_bridge.md` | P3 愿景, Sprint 0-4 不相关 |
| `architecture/verification_plan_google.md` | P3 愿景, Sprint 0-4 不相关 |

### 1.4 lore — 人类手写, AI 只读

| 文件 | 说明 |
|:-----|:-----|
| `lore/ideas.md` | 用户的阶段性灵感、设计直觉、展望。**AI 不可改**, 不可基于此做设计 |

### 1.5 外部文档库 (非事实源)

| 路径 | 用途 |
|:-----|:-----|
| `docs/InfoCollections/Opus/` | 2026-02 ~ 03 的 26 篇调研文档 (架构起源, 大多已被 `.cursor/memory` 吸收). **按需 @ 引用, 不作依赖源**. 见 `docs/InfoCollections/Opus/INDEX.md` |
| `docs/InfoCollections/HumanPlan/` | 用户早期手写计划 (legacy). **只读追溯**, 不作依赖 |
| `docs/references/skill_seekers_output/` | SDK / 库的源文档蒸馏结果 (LiveKit / Graphiti / SVA / Nanobot). 供 skill 文件引用 |
| `NewZone/distill_output/dsg/` | **DSG 蒸馏素材池**（2026-05-06 新增）— ConceptGraph / RustworkX docs+repo / SuperLocalMemory 4 份 Gemini 蒸馏。**不进 `.cursor/skills/`**（避免上下文污染）；按需 @ 引用 |
| `NewZone/distill_output/dsg_l2b_org_raw/` | **DSG L2-B 组织专题素材池**（2026-05-06 新增）— HippoRAG / AriGraph 2 份 Gemini 蒸馏 |
| `NewZone/skill_distill_bundle/` | 6 份 focus 配置（重新蒸馏用）|
| `NewZone/RustworkX 图模拟研究案例.md` | RustworkX 仿生研究案例综述（§119-§122 仿生 4 范式）|

### 1.6 Skills（DSG 系列 — 2026-05-06 新增 4 个）

| Skill | 角色 |
|:-----|:-----|
| `.cursor/skills/dsg-rustworkx-master/` | DSG 设计 chat 总入口路由 + RustworkX 实操 + 仿生 4 范式 + 跨 skill 论文索引 |
| `.cursor/skills/dsg-l2b-node-organization-options/` | L2-B Node/Edge 组织 5 选项 + 子图分层 P1-P4 + 跨源合并信号 |
| `.cursor/skills/dsg-attention-schema-papers/` | 13 篇论文索引（GAT / DySAT / AGCN / G-HAM / Schema / Hippocampal Indexing / Spreading Activation / CLS / Tulving / ASD/MDD）|
| `.cursor/skills/dsg-l1-5-l2a-conceptgraph-distilled/` | A10 入口门控 + L2-A 语义抽象（A10 Phase 5+ 接入参考）|

---

## 二、目录结构速查 (2026-04-20)

> 详见 `.cursor/memory/architecture/module_map_p2.md` (模块职责 + 成熟度)

### 2.1 项目结构

```
ParrotCarriers/                       # 主仓库 (GOSLOParrot/ParrotCarriers)
│
├── src/
│   ├── parrot/                       # Python 源码 (Bus + Brain + Scheduler + DSG + Memory)
│   │   ├── bus/                      # 总线框架 (注册/心跳/挂载/NanobotConsumer)
│   │   ├── brain/                    # 云端大脑 (Gemini Agent + 上下文 + 遥测)
│   │   │   └── tools/               # 10 个 function_tool (Gemini 可调)
│   │   ├── scheduler/               # 调度器 (py-trees BT + Blackboard V2)
│   │   ├── dsg/                      # DSG 感知耦合层 (L2-B + Graphiti + 触发器)
│   │   │   └── triggers/            # 4 个背景触发器 (日程/消息/SSOT/场景)
│   │   ├── memory/                   # 记忆子系统 (Graphiti + FalkorDB + 对话归档)
│   │   └── shared/                   # 跨模块共享 (config/redis/constants/types)
│   └── scripts/                      # 运维/工具脚本
│       ├── sim_unity_client.py       # Unity 模拟 (--mic --full --video)
│       ├── sim_dsg_desktop.py        # L1 输出模拟 (桌面场景)
│       ├── sync_obsidian_to_graphiti.py  # Obsidian → Graphiti scene 同步
│       ├── generate_token.py         # LiveKit Token 生成
│       ├── run_dev.py                # 一键启动开发栈
│       ├── start_nanobot_worker.py   # 真实 Nanobot gateway 启动
│       ├── start_goslo_chat.py       # GOSLO Chat Telegram bot
│       └── start_scheduler.py        # Scheduler 独立启动
│
├── unity/ParrotDev/                  # Unity AR 客户端
│   └── Assets/Scripts/
│       ├── LiveKit/                  # RoomManager, ARVideoPublisher
│       ├── Parrot/                   # ParrotController, ParrotRpcHandler
│       └── XRHands/                  # XRHandTracker, PerchOnHand
│
├── infra/                            # Docker/部署配置
│   ├── docker-compose.yml            # Castle 全栈 (Redis + LiveKit + FalkorDB)
│   ├── docker-compose.dev.yml        # 本地开发栈
│   ├── deploy-castle.sh              # Castle 部署脚本
│   ├── env-castle.template           # 环境变量模板
│   └── livekit/                      # LiveKit 配置
│
├── tests/                            # 测试
│   ├── test_bus/                     # 总线单元测试
│   ├── test_scheduler/               # 调度器测试
│   └── integration/                  # 集成测试 (dispatch chain, graphiti chain)
│
├── docs/test/p2_5/                   # 人手验收矩阵 + Remote Cursor 提示词（Git 跟踪；根目录 Test/ 仍 gitignore）
│   └── ECS_RUN_REPORTS/             # 远端单次跑报告 report-*.md（防与主矩阵冲突）
├── FilePort2/                        # 未 ignore 的投递说明（见 README）；大文件仍用 FilePort/（ignore）
│
├── docs/                             # 文档
├── .cursor/                          # Cursor 配置
│   ├── memory/                       # 持久记忆 (架构/进度/需求/里程碑)
│   ├── rules/                        # 工作区规则 (.mdc)
│   └── skills/                       # 领域技能 (LiveKit/Graphiti/SVA/Nanobot/py-trees)
│
├── pyproject.toml                    # Python 项目配置
└── .env                              # 环境变量

GOSLOParrot/nanobot                   # 独立仓库 (fork from HKUDS/nanobot)
├── nanobot/channels/
│   ├── parrot_bus.py                 # Bus channel adapter (Redis Stream + Graphiti)
│   └── goslo_mode.py                 # GOSLO 模式感知中间件
└── config/                           # parrot_config.json, goslo_config.json
```

### 2.2 `.cursor/` 结构

```
.cursor/
├── memory/                           # 持久记忆
│   ├── architecture/                 # 架构文档 (按 §1.1 active / §1.2 reference / §1.3 archived 分类)
│   ├── INDEX.md                      # 本文件（唯一真相源）
│   ├── active_context.md             # 当前进度 + 下一步
│   ├── requirements.md               # 完整功能需求清单 v2
│   ├── milestone_p2.md               # P2/P2.5 里程碑 (实现清单 + 架构决策)
│   ├── parrot_behavior_rules.md      # 鹦鹉行为状态/兼容矩阵/冲突规则
│   ├── deploy_snapshot_p2_20260412.md # Castle 部署快照
│   ├── BigIssue.md                   # 协议污染复盘
│   └── commit_guidelines.md          # 提交指南
├── rules/                            # Cursor 规则
│   ├── workspace.mdc                 # 全局路由 (alwaysApply)
│   ├── bus-audit-constraints.mdc     # 审计护栏
│   ├── deploy-prep-routing.mdc       # infra/** 触发
│   ├── docker-best-practices.mdc     # Docker 触发
│   ├── livekit-unity-sdk.mdc         # Unity SDK 规则
│   └── ar-foundation.mdc            # AR Foundation 版本约束+已知坑
└── skills/                           # 领域技能 (按需发现)
    ├── livekit-agents/               # LiveKit Agents SDK
    ├── client-sdk-unity/             # LiveKit Unity SDK
    ├── livekit-unity-video-publish/  # 视频流采集与多处采样 (One Stream Multiple Sampling)
    ├── graphiti/                     # Graphiti API
    ├── nanobot-overview/             # Nanobot 上游架构
    ├── nanobot/                      # ParrotCarriers 中的 Nanobot 审计
    ├── sva-vision-agents/            # SVA Vision-Agents Processor 模式
    ├── py-trees/                     # py-trees 行为树
    ├── bus-deploy-livekit-ecs/       # 阿里云 ECS 部署
    └── parrot-bus-orchestration/     # Bus 任务编排
```

### 资料放置规则

| 资料类型 | 放置路径 | Cursor 消费方式 |
|:---------|:---------|:----------------|
| 持久记忆 (事实源) | `.cursor/memory/` | workspace.mdc 路由指向, **唯一真相源** |
| 已确认决策 (防翻案) | `.cursor/memory/requirements.md` §二, `milestone_p2.md` §九 | 需求清单 + 里程碑中的 D-P2.x |
| 规则指令 (编码约定、路由) | `.cursor/rules/*.mdc` | 自动/智能/globs 加载 |
| 领域技能 (能力) | `.cursor/skills/<name>/SKILL.md` | 动态发现; `nanobot` 优先显式调用 |
| 调研文档 (文档库, 非事实源) | `docs/InfoCollections/Opus/` | `@` 引用, 按需追溯 |
| SDK 蒸馏 (文档库) | `docs/references/skill_seekers_output/` | skill 文件内部引用 |

---

## 三、服务器部署（东京双节点）

| 节点 | 规格 | 部署组件 | 运行模式 |
|:-----|:-----|:---------|:---------|
| **常驻城堡 (The Castle)** | 东京 ecs.g9i.large (2核8G) | LiveKit Server, Redis, FalkorDB, Brain Agent, Scheduler, Nanobot Worker | 常开 |
| **按需机甲 (The Mecha)** | 东京 ecs.gn7i (A10 抢占式) | SAM2 + DINOv2, DSG L1/L2-A | 按需开关，无状态 |

- **同 VPC**: 同一可用区，内网延迟 < 0.1ms
- **控制面 vs 数据面**: ecs.g9i.large = 控制面（状态/路由/记忆）；A10 = 数据面（算力，可抛弃）
- **视频流**: Unity → LiveKit (Castle) → [内网] → SAM2 (A10)

Castle 进程布局:
```
┌───────────────────────────────────────┐
│  Docker:                              │
│  ├── Redis         (127.0.0.1:6379)   │
│  ├── LiveKit Server (0.0.0.0:7880)    │
│  └── FalkorDB      (127.0.0.1:6380)   │
│                                       │
│  tmux sessions:                       │
│  ├── brain:  Brain Agent (Gemini Live)│
│  ├── maid:   Nanobot Worker (猫娘)    │
│  └── goslo-chat: GOSLO Chat (Telegram)│
└───────────────────────────────────────┘
```

---

## 四、模块当前状态

> 详见 `.cursor/memory/architecture/module_map_p2.md` 的成熟度矩阵

| 包 | 模块 | 状态 |
|:---|:-----|:-----|
| `bus/` | 总线框架 (注册/心跳/挂载/NanobotConsumer) | VERIFIED |
| `brain/` | 云端大脑 (Gemini + 10 tools + 上下文 + 遥测) | VERIFIED (核心) / IMPLEMENTED (P2.5 工具) |
| `scheduler/` | 调度器 (py-trees BT + Blackboard + 超时) | VERIFIED |
| `dsg/` | DSG 耦合层 (L2-B + 4 触发器 + Graphiti 接口) | IMPLEMENTED (待端到端验证) |
| `memory/` | Graphiti + FalkorDB + 对话归档 | VERIFIED (客户端) / IMPLEMENTED (归档) |
| `shared/` | 配置/Redis/常量/类型/遥测 | VERIFIED |
| Unity C# | RoomManager + RPC + ARVideo + XRHands | VERIFIED (P1) / DESIGNED (AR/XR) |
| nanobot (外部) | parrot_bus + weixin + goslo_mode | VERIFIED |

---

## 五、快速导航

| 想了解… | 指向 |
|:--------|:-----|
| 当前进度与下一步 | `active_context.md` |
| 模块职责 + 数据流 + 成熟度 | `architecture/module_map_p2.md` |
| P2/P2.5 实现清单 + 决策 | `milestone_p2.md` |
| 全局路由规则 | `.cursor/rules/workspace.mdc` |
| DSG 四层 + 内部数据流 | `architecture/system_core.md` (v3 愿景) |
| Bus 三层协议 + 拓扑 | `architecture/bus_v4.md` |
| 家族角色与关系 | `architecture/scene.md` |
| V1 协议全量 | `architecture/protocol_snapshot_p1.md` |
| 功能需求 + 决策 | `requirements.md` |
| 鹦鹉行为规则 | `parrot_behavior_rules.md` |
