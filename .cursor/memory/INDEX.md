# ParrotCarriers 全局索引

> 用途: 项目唯一真相源，供 Cursor 与用户快速定位关键信息
> 更新: 2026-04-20 (AR App 工程计划 + 视频流采样 skill + AR Foundation 规则)
> 路由: 由 `.cursor/rules/workspace.mdc` (alwaysApply) 指向本文件

---

## 一、项目入口

| 条目 | 路径 | 说明 |
|:-----|:-----|:-----|
| 当前进度与下一步 | `.cursor/memory/active_context.md` | 阶段性进度、行动项 |
| **模块职责/数据流/成熟度** | `.cursor/memory/architecture/module_map_p2.md` | **P2.5 全模块清单 + mermaid 数据流 + 成熟度矩阵** |
| **P2 里程碑** | `.cursor/memory/milestone_p2.md` | **实现清单 + 架构决策 (D-P2-1 ~ D-P2.5)** |
| **完整功能需求 v2** | `.cursor/memory/requirements.md` | **67 功能项 + 决策 + 准备清单** |
| 鹦鹉行为状态规则 | `.cursor/memory/parrot_behavior_rules.md` | 状态机 + 兼容矩阵 + 冲突规则 |
| 模块划分与目录结构 | `.cursor/memory/architecture/module_division.md` | MFD 框架 + 服务器落位 (P1 时代基线) |
| 总线架构 v4.2 | `.cursor/memory/architecture/bus_v4.md` | 三层协议 + 拓扑 + 降级策略 |
| 架构图 v3 (内部数据流) | `.cursor/memory/architecture/system_core.md` | Brain/DSG/调度器愿景设计 (2026-03, 细节已演进) |
| 家族拓扑 | `.cursor/memory/architecture/scene.md` | 大姐/妹妹/猫/调度器/Graphiti |
| 协议快照 V1 | `.cursor/memory/architecture/protocol_snapshot_p1.md` | RPC/Redis/DataChannel/Blackboard 全量 (定版 2026-04-12) |
| 部署快照 | `.cursor/memory/deploy_snapshot_p2_20260412.md` | Castle 部署配置与密钥 |
| 协议污染复盘 | `.cursor/memory/BigIssue.md` | 历史教训与修正措施 |
| Google 生态桥接 | `.cursor/memory/architecture/gemini_drive_bridge.md` | 副驾驶姐姐 Drive 工作区协议 (未来计划) |
| Google 联调计划 | `.cursor/memory/architecture/verification_plan_google.md` | Mock → 真实 OAuth 验证分阶段 (未来计划) |
| **AR App 工程计划** | `.cursor/memory/architecture/ar_app_plan.md` | **硬事实 + 调研索引 + 用户问卷** |
| **视频流采样审计 (identify_object)** | `.cursor/memory/architecture/audit_identify_object_no_screenshot_20260420.md` | **缺截图+体感断裂 + 三段递进升级路径** |
| 调研遗产 | `docs/InfoCollections/Opus/` → 见 `Opus/INDEX.md` | 26 篇调研文档 |
| **灵感 & 展望** (人类手写) | `.cursor/memory/lore/ideas.md` | **AI 只读** — 用户的阶段性灵感、设计直觉、展望 |
| 领域技能 | `.cursor/skills/` | 按需发现；含 `livekit-unity-video-publish` 视频流采样 skill |

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
│   ├── architecture/                 # 10 份架构文档 (bus/system/scene/protocol/module_map/ar_app_plan/audit 等)
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
| 持久记忆（架构、索引、进度） | `.cursor/memory/` | workspace.mdc 路由指向 |
| 已确认决策（防翻案） | `.cursor/memory/requirements.md` §二, `milestone_p2.md` §九 | 需求清单 + 里程碑中的 D-P2.x |
| 规则指令（编码约定、路由） | `.cursor/rules/*.mdc` | 自动/智能/globs 加载 |
| 领域技能 | `.cursor/skills/<name>/SKILL.md` | 动态发现；`nanobot` 优先显式调用 |
| 调研文档 | `docs/InfoCollections/Opus/` | @doc 引用 |

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
