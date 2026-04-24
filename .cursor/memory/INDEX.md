# ParrotCarriers 全局索引

> 用途: 项目唯一真相源，供 Cursor 与用户快速定位关键信息
> 更新: 2026-04-22 (按 category + status 重排, Sprint 0 前置)
> 路由: 由 `.cursor/rules/workspace.mdc` (alwaysApply) 指向本文件

**全局约定**:
- **事实源**: 只有 `.cursor/memory/**`。`docs/InfoCollections/**` 是**文档库/考古资料**, 按需 `@` 引用, 不作事实源。
- **两个维度**: 每份架构文档 frontmatter 含 `status` (tentative/ratified/archived/superseded) + `category` (active/reference/archived/historical)。读之前先看 frontmatter。
- **不读 archived**: 除非在追溯历史决策。

---

## 〇、当前阶段必读 (按序, 不读后续)

> **原则**: 进入任何 Sprint 前, **只读这 4 份**, 不翻历史。
> **当前**: Sprint 0 前置 (2026-04-22)

| # | 文件 | 读什么 |
|:--|:-----|:-------|
| 1 | `.cursor/memory/architecture/module_map_p2.md` | **全景架构入口** — §〇 项目边界 / §一 模块清单 / §二 数据流 / §九 外挂生态 / §十 DSG 分层 / §十一 时间轴 |
| 2 | `.cursor/memory/active_context.md` | 头部 + 本周关键路径 (先确认自己在哪一步) |
| 3 | `.cursor/memory/architecture/sprint0_preflight.md` | §7 最终任务单 + §8 回答 6 件担心 |
| 4 | `.cursor/memory/architecture/ar_feature_implementation_plan.md` + `ar_feature_vision.md §3.5/§六` | 当前 Sprint 任务 + 决策默认值 |

---

## 一、按类别索引

### 1.1 active — 本周活跃, 边读边写 (status: tentative)

> 这 5 份在跟代码同步演进, 读时注意 frontmatter 的 `status_note`。

| 文件 | 说明 |
|:-----|:-----|
| `active_context.md` | 当前进度 + 本周关键路径 + 版本锁表 |
| `architecture/sprint0_preflight.md` | Sprint 0 前置 14 项 (S0.A-N) |
| `architecture/ar_feature_vision.md` | 门控 + 自知 + 两轴 + §3.5 三合一 + §六 决策 (tentative 直到 Sprint 1/2 代码落地) |
| `architecture/ar_feature_implementation_plan.md` | Sprint 0-4 任务清单 + 依赖图 (逐 Sprint ratified) |
| `architecture/ar_app_plan.md` | AR 工程硬事实 + 问卷回填 (tentative 部分) |

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
