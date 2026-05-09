# ParrotCarriers 全局索引

> 用途: 项目唯一真相源，供 Cursor 与用户快速定位关键信息
> 更新: 2026-05-09 (路由整理 + 接口分类骨架 + 三新 chat 准备 — Sprint 0-4 已收口产物全量归档至 `docs/sprint_archive/`，顶层 `.cursor/memory/architecture/` 从 67 份瘦身到 20 份；接口分类骨架 `Interface/INDEX.md`；前端工作区边界 `frontend_workspace_boundary.md`；3 份新 chat launch prompt `chat_launches/`；新增 §六 四轴速查)
> 路由: 由 `.cursor/rules/workspace.mdc` (alwaysApply) 指向本文件

**全局约定**:
- **事实源**: 只有 `.cursor/memory/**`。`docs/**` 是**文档库/考古/归档**, 按需 `@` 引用, 不作事实源。
- **两个维度**: 每份架构文档 frontmatter 含 `status` (tentative/ratified/archived/superseded) + `category` (active/reference/archived/historical)。读之前先看 frontmatter。
- **不读 archived**: 除非在追溯历史决策。Sprint 0-4 已收口产物物理外迁到 `docs/sprint_archive/`，下游 chat 不读其正文。

---

## 〇、当前阶段必读 (按序, 不读后续)

> **原则**: 进入任何 Sprint 前, **只读这几份**, 不翻历史。
> **当前**: Sprint 4 Phase 4 **完成** → Phase 5 转换期 (2026-05-04) → DSG Chat 2 + GOSLO 模块化收口 (2026-05-06) → P2.5 App 设计 + Interface pre (2026-05-07) → **路由整理 + 接口分类骨架 + 第二前端工作区准备 (2026-05-09)**
> **协议入场必读**: `protocol_snapshot_p4.md`（全协议 SSOT）+ `bus_v4.md`（拓扑）+ `sprint4_protocol_v2_ecp.md`（ECP 设计稿）+ 2 份 ADR
> **接口入场必读**: ⭐ `architecture/Interface/INDEX.md`（核心/业务分类骨架，避免"复印仓库"）+ `backend_interface_refinement_20260507.md`（Brain Core SSOT）
> **DSG 系列设计 chat 入场必读**: `architecture/dsg/workspace_index.md` → `dsg_current_state_distilled.md`（与 AR 工作区对位）
> **跨 chat master**: ⭐ `architecture/cross_chat_pending_registry_20260507.md`（统一 TODO + NEED 登记表）+ ⭐ `architecture/app_completion_master_audit_20260507.md`（8 场景对账 + 像素画 UI 资产清单）
> **第二前端工作区**（Codex + Unity MCP）入场必读: `architecture/frontend_workspace_boundary.md`（与 Cursor 的边界条款 + mermaid 拓扑）
> **三新 chat 待开 launch prompt**: `architecture/chat_launches/{obsidian_realconnect, web_console, figma_ui_assets_landing}_launch_20260509.md`
> **历史 Sprint 0-4 归档**: `docs/sprint_archive/INDEX.md`（按时间线 / 按 sprint / 按文件类型 三轴聚合，~48 份；不读正文）

| # | 文件 | 读什么 |
|:--|:-----|:-------|
| 1 | `.cursor/memory/architecture/module_map_p2.md` | **全景架构入口** — §〇 项目边界 / §一 模块清单 / §二 数据流 / §九 外挂生态 / §十 DSG 分层 |
| 2 | `.cursor/memory/active_context.md` | 当前进度 + 本周关键路径 |
| 3 | `.cursor/memory/architecture/protocol_snapshot_p4.md` | ⭐ **全协议 SSOT** — enum / topic / BB key / Phase 4 13 决策锁 |
| 4 | `.cursor/memory/architecture/sprint4_protocol_v2_ecp.md` | ECP 协议设计稿：最小合同 / 状态面 / 生命周期 / 实现顺序 |
| 5 | `.cursor/memory/architecture/Interface/INDEX.md` | ⭐ **接口分类骨架**（2026-05-09） — Core/Business 分类 + 4 字段业务模板 + 失败教训 |
| 6 | `.cursor/memory/architecture/backend_interface_refinement_20260507.md` | Brain Core 接口 SSOT（Persona/Menu/Preset/IntentWorkspace/L2-B baseline） |
| 7 | `.cursor/memory/architecture/ar_app_flow_ui_design.md` | 当前 App Flow / UI / 功能入口设计基线 |
| 8 | `.cursor/memory/architecture/dsg/workspace_index.md` | **DSG 工作区入口** — DSG 系列设计 chat 单一入场点；与 AR 工作区对位 |
| 9 | ⭐ `.cursor/memory/architecture/cross_chat_pending_registry_20260507.md` | **跨 chat 待办登记表（master）** — 任何下游 chat 入场前先读 §5 找自己的标签清单 |
| 10 | ⭐ `.cursor/memory/architecture/app_completion_master_audit_20260507.md` | **App 完成度总 chat 主 doc** — 8 场景对账 + 像素画 UI 资产清单 |
| 11 | `.cursor/memory/architecture/frontend_workspace_boundary.md` | 第二前端工作区（Codex+Unity MCP）边界条款 + 拓扑图（2026-05-09） |
| 12 | `.cursor/memory/architecture/chat_launches/` | 三新 chat 待开 launch prompts（Obsidian / Web 控制台 / Figma UI 资产） |
| — | `docs/sprint_archive/INDEX.md` | Sprint 0-4 归档清单（**不读正文**，仅做考古追溯） |

---

## 一、按类别索引

### 1.1 active — 本周活跃, 边读边写 (status: tentative)

> 这些文件在跟代码同步演进，读时注意 frontmatter 的 `status_note`。
> 2026-05-09 整理：移除所有指向已归档 sprint*_*.md 的指针，归档清单见 `docs/sprint_archive/INDEX.md`。

| 文件 | 说明 |
|:-----|:-----|
| `active_context.md` | 当前进度 + 本周关键路径 + 版本锁表 |
| `architecture/ar_feature_vision.md` | 门控 + 自知 + 两轴 + §3.5 三合一 + §六 决策 (tentative 直到 Sprint 1/2 代码落地) |
| `architecture/ar_feature_implementation_plan.md` | Sprint 0-4 任务清单 + 依赖图 (逐 Sprint ratified) |
| `architecture/sprint4_protocol_v2_ecp.md` | ECP 协议设计稿（活跃协议产出）：ECP 最小合同、状态面、Snapshot/Sighting/RefBinding、Lifecycle/Audio、BT 对齐与实施顺序 |
| `architecture/protocol_snapshot_p4.md` | ⭐ **全协议 SSOT**（Phase 4 13 决策锁 + 全 enum/topic/BB key 速查）|
| `architecture/ar_app_flow_ui_design.md` | AR App Flow / UI / 功能入口当前设计基线 |
| `architecture/dsg/workspace_index.md` | **DSG 工作区入口** — DSG 系列设计 chat 单一入场点；与 `ar_workspace_index.md` 对位 |
| `architecture/dsg/dsg_decisions_master.md` | **DSG 决策总表**（master，长期累加）— 用户已决事项 + status 分级 |
| `architecture/dsg/dsg_current_state_distilled.md` | **DSG 全景快照** — 冷读完一份能回答 DSG 全景 |
| `architecture/dsg/opus_dsg_residual_intent.md` | Opus 09/11/12/17/18/19 仍生效的设计意图蒸馏 |
| `architecture/dsg/source_x_lifecycle_status.md` | 7 项现有 source + Obsidian 三分类 + GOSLO 主动 + A10 占位的 lifecycle 现状对照表 |
| `architecture/dsg/open_questions_for_design_chat.md` | Chat 2 需回答的开放问题；§0 已决汇总指向 dsg_decisions_master.md |
| `architecture/adr_protocol_upgrade_and_interface_refinement_background_20260504.md` | **ADR-PROTOCOL-INTERFACE-001** — Sprint4 协议升级 + 接口提炼任务输入；不修改 Phase 4 锁定值 |
| `architecture/adr_l1_5_source_dispatch_extension_space_20260504.md` | **ADR-L1.5-SOURCE-DISPATCH-001** — SemanticNode.source 字段边界 + Meta hook 扩展空间。**任何动 dsg/ 的 chat 必读** |
| `architecture/app_completion_master_audit_20260507.md` | **App 完成度总 chat 主 doc** — 8 场景对账 + 像素画 UI 资产清单 |
| `architecture/cross_chat_pending_registry_20260507.md` | **跨 chat 待办登记表（master）** — 任何下游 chat 入场前先读 §5 找自己的标签清单 |
| **`architecture/Interface/INDEX.md`** | ⭐ **接口分类骨架**（2026-05-09 新建）— 核心/业务分类规则 + 4 字段业务模板 + 失败教训 |
| `architecture/Interface/concept_dictionary_20260507.md` | **概念词典** — ≈100 项术语 + 设计文档路由指引 |
| `architecture/Interface/legacy_issues_split_20260507.md` | **遗留问题二分**（含新 P2.5：2D 独立工作区）— P2.5 / P3 + grep 速查 + 修复 chat 派发表 |
| `architecture/Interface/menu_design_complete_20260507.md` | **完整菜单设计 SSOT** — 三层架构 + 4 类块 + 预设 + 海盗换肤 + 像素画素材清单 |
| `architecture/Interface/goslo_app_game_overview_asset_brief_20260507.md` | App 总览 + 美术资产 brief |
| `architecture/Interface/interface_design_and_how_todo_v0_20260507.md` | （已 superseded → Interface/INDEX.md）12 场景接口栈穷举主表，留作场景清单参考 |
| `architecture/Interface/interface_design_supplement_20260507.md` | （已 superseded → Interface/INDEX.md）v0 之外 7 项新发现 |
| `architecture/backend_interface_refinement_20260507.md` | **Brain Core 接口 SSOT** — Persona / Menu / Preset / IntentWorkspace / L2-B baseline 实测公开接口 |
| `architecture/frontend_workspace_boundary.md` | 第二前端工作区（Codex+Unity MCP）边界条款 + mermaid 拓扑（2026-05-09 新建） |
| `architecture/chat_launches/obsidian_realconnect_launch_20260509.md` | 待开 chat：后端 ↔ Obsidian 真连接 launch prompt |
| `architecture/chat_launches/web_console_launch_20260509.md` | 待开 chat：Web 控制台 read-only 优先 launch prompt |
| `architecture/chat_launches/figma_ui_assets_landing_launch_20260509.md` | 待开 chat：Figma UI 资产入工作区 launch prompt |

### 1.2 reference — 当前稳定事实源 (status: ratified)

> 新决策不翻这些旧决策, 只能追加或 bump 版本号。

| 文件 | 说明 |
|:-----|:-----|
| `architecture/module_map_p2.md` | **模块 P2.5 成熟度矩阵** |
| `architecture/module_map_p4_snapshot.md` | 模块 P4 快照（Phase 4 收口后） |
| `requirements.md` | **67 功能项 + 11 个已确认决策** (需求事实源) |
| `architecture/bus_v4.md` | **Bus v4.2 三层协议 + 拓扑** |
| `architecture/protocol_snapshot_p1.md` | **V1 协议定版** (RPC/Redis/DataChannel/Blackboard，历史) |
| `architecture/protocol_snapshot_p4.md` | **V4 协议 SSOT**（覆盖 V1 大部分；新会话查协议入这里） |
| `architecture/goslo_model_manifest_protocol_v1.md` | GOSLO 模型 manifest 协议 v1 |
| `architecture/scene.md` | 家族角色拓扑 (GOSLO / Maid / Parrot / Gemini 二重身) |
| `parrot_behavior_rules.md` | 鹦鹉行为状态机 + 兼容矩阵 |
| `architecture/ar_camera_interaction_survey.md` | AR 摄影互动问卷 (已回填, 不再改) |
| `architecture/ar_skill_seekers_distillation_report.md` | AR Foundation 5.1 蒸馏报告 |
| `BigIssue.md` | 协议污染复盘 + 设计护栏 (永久护栏) |
| `deploy_snapshot_p2_20260412.md` | Castle 部署快照 |
| `commit_guidelines.md` | 提交规范 + 漂移说明子句 |
| `milestone_p2.md` | P2/P2.5 里程碑 (已完成, 历史归档) |
| `architecture/ar_app_plan.md` | 早期 AR 工程计划 + 问卷追溯；新的 App Flow / UI 以 `architecture/ar_app_flow_ui_design.md` 为准 |

### 1.3 archived — 已物理外迁到 `docs/sprint_archive/`

> **不读正文**, 除非明确要追溯早期决策。
> Sprint 0-4 已收口产物（kickoff / plan / completion / audit / launch_prompt）+ 4 份历史 superseded 共 ~48 份，统一归档于 `docs/sprint_archive/`。
> 单点入口：[`docs/sprint_archive/INDEX.md`](../../docs/sprint_archive/INDEX.md)（按时间线 / 按 sprint / 按文件类型 三轴聚合）

### 1.4 lore — 人类手写, AI 只读

| 文件 | 说明 |
|:-----|:-----|
| `lore/ideas.md` | 用户的阶段性灵感、设计直觉、展望。**AI 不可改**, 不可基于此做设计 |

### 1.5 外部文档库 (非事实源)

| 路径 | 用途 |
|:-----|:-----|
| `docs/sprint_archive/` | **Sprint 0-4 归档**（2026-05-09 整理）— ~48 份已收口 kickoff/plan/completion/audit/launch_prompt + 4 份 superseded。**不读正文**；入口 `docs/sprint_archive/INDEX.md` |
| `docs/InfoCollections/Opus/` | 2026-02 ~ 03 的 26 篇调研文档 (架构起源, 大多已被 `.cursor/memory` 吸收). **按需 @ 引用, 不作依赖源**. 见 `docs/InfoCollections/Opus/INDEX.md` |
| `docs/InfoCollections/HumanPlan/` | 用户早期手写计划 (legacy). **只读追溯**, 不作依赖 |
| `docs/references/skill_seekers_output/` | SDK / 库的源文档蒸馏结果 (LiveKit / Graphiti / SVA / Nanobot). 供 skill 文件引用 |
| `docs/sprint4_research/` | Phase 3 调研产物（task1-6 + result 1-5） |
| `docs/test/p2_5/` | 人手验收矩阵 + Remote Cursor 提示词 |
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
| 模块职责 + 数据流 + 成熟度 | `architecture/module_map_p2.md` + `architecture/module_map_p4_snapshot.md` |
| P2/P2.5 实现清单 + 决策 | `milestone_p2.md` |
| 全局路由规则 | `.cursor/rules/workspace.mdc` |
| DSG 工作区入口 | `architecture/dsg/workspace_index.md` |
| Bus 三层协议 + 拓扑 | `architecture/bus_v4.md` |
| 家族角色与关系 | `architecture/scene.md` |
| 全协议 SSOT | `architecture/protocol_snapshot_p4.md`（V4，当前真源） |
| ECP 协议设计稿 | `architecture/sprint4_protocol_v2_ecp.md` |
| 接口分类骨架 | `architecture/Interface/INDEX.md` |
| 功能需求 + 决策 | `requirements.md` |
| 鹦鹉行为规则 | `parrot_behavior_rules.md` |
| 第二前端工作区边界 | `architecture/frontend_workspace_boundary.md` |
| Sprint 0-4 历史归档 | `docs/sprint_archive/INDEX.md` |

---

## 六、四轴速查（Protocol / Interface / Design / Requirements）

> 2026-05-09 新增：用户要求按四轴清晰索引。本节为 4 个维度的快速查表入口；详细文档落在 `architecture/` 内对应文件。

### 6.1 Protocol — 协议层（"线上跑什么字段"）

| 文件 | 角色 |
|:--|:--|
| ⭐ `architecture/protocol_snapshot_p4.md` | **当前真源** — 全 enum / topic / BB key / Phase 4 13 决策锁 |
| `architecture/bus_v4.md` | Bus v4.2 三层协议 + 拓扑 + East-West / North-South 边界 |
| `architecture/sprint4_protocol_v2_ecp.md` | ECP 协议设计稿（ECP envelope / 状态面 / 生命周期 / BT 对齐） |
| `architecture/adr_protocol_upgrade_and_interface_refinement_background_20260504.md` | ADR-PROTOCOL-INTERFACE-001（升级背景 + 任务输入） |
| `architecture/adr_l1_5_source_dispatch_extension_space_20260504.md` | ADR-L1.5-SOURCE-DISPATCH-001（SemanticNode.source 边界 + Meta hook） |
| `architecture/goslo_model_manifest_protocol_v1.md` | GOSLO 模型 manifest 协议 v1 |
| `architecture/protocol_snapshot_p1.md` | V1 历史定版（RPC/Redis/DataChannel/Blackboard） |

### 6.2 Interface — 接口层（"代码暴露的公开表面"）

| 文件 | 角色 |
|:--|:--|
| ⭐ `architecture/Interface/INDEX.md` | **接口分类骨架（2026-05-09）** — Core/Business 分类规则 + 4 字段业务模板 + 失败教训 |
| `architecture/backend_interface_refinement_20260507.md` | **Brain Core 接口 SSOT** — Persona / Menu / Preset / IntentWorkspace / L2-B baseline |
| `architecture/dsg/workspace_index.md` | DSG 模块接口入口（dsg_protocol_*_v1 系列） |

### 6.3 Design — 设计层（"用户视角与场景如何编织"）

| 文件 | 角色 |
|:--|:--|
| `architecture/ar_feature_vision.md` | 门控 + 自知 + 三合一 + 4-scope BB（设计基线） |
| `architecture/ar_app_flow_ui_design.md` | App Flow / UI / 功能入口设计基线 |
| `architecture/Interface/menu_design_complete_20260507.md` | 完整菜单设计 SSOT（4 类块 + 预设 + 海盗换肤） |
| `architecture/Interface/concept_dictionary_20260507.md` | 概念词典（≈100 项术语 + 路由指引） |
| `architecture/Interface/goslo_app_game_overview_asset_brief_20260507.md` | App 总览 + 美术资产 brief |
| `architecture/dsg/workspace_index.md` | DSG 设计入场（含 dsg_decisions_master + Opus 蒸馏） |
| `architecture/scene.md` | 家族拓扑（GOSLO / Maid / Parrot / Gemini 二重身） |

### 6.4 Requirements — 需求层（"要做什么 / 不做什么 / 待办"）

| 文件 | 角色 |
|:--|:--|
| `requirements.md` | **67 功能项 + 11 个已确认决策**（需求事实源） |
| `milestone_p2.md` | P2/P2.5 里程碑（实现清单 + D-P2.x 决策） |
| ⭐ `architecture/cross_chat_pending_registry_20260507.md` | **跨 chat 待办登记表（master）** — 三大 chat 完成后统一 TODO + NEED 标签 |
| ⭐ `architecture/app_completion_master_audit_20260507.md` | App 完成度 8 场景对账 + 像素画 UI 资产清单 |
| `architecture/Interface/legacy_issues_split_20260507.md` | 遗留问题二分（P2.5 / P3 + grep 速查 + 修复 chat 派发） |
| `architecture/ar_feature_implementation_plan.md` | Sprint 0-4 任务清单 + 依赖图 |
| `architecture/chat_launches/` | 三新 chat 待开 launch prompts（2026-05-09） |

### 6.5 跨工作区边界（meta）

| 文件 | 角色 |
|:--|:--|
| `architecture/frontend_workspace_boundary.md` | Cursor vs Codex+Unity MCP 第二前端工作区边界 + 拓扑 |
| `.cursor/rules/workspace.mdc` | 全局路由 alwaysApply |
| `architecture/ar_workspace_index.md` | AR 工作区聚合入口 |
| `architecture/dsg/workspace_index.md` | DSG 工作区聚合入口 |
