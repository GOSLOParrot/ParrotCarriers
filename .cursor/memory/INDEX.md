# ParrotCarriers 全局索引

> 用途: 项目唯一真相源，供 Cursor 与用户快速定位关键信息  
> 更新: 2026-04-08 (模块划分完成)  
> 路由: 由 `.cursor/rules/workspace.mdc` (alwaysApply) 指向本文件

---

## 一、项目入口

| 条目 | 路径 | 说明 |
|:-----|:-----|:-----|
| 当前进度与下一步 | `.cursor/memory/active_context.md` | 阶段性进度、行动项 |
| **完整功能需求 v2** | `.cursor/memory/requirements.md` | **67 功能项 + 决策 + 准备清单** |
| **模块划分与目录结构** | `.cursor/memory/architecture/module_division.md` | **MFD 框架 + 服务器落位 + 验证矩阵** |
| 总线架构 v4.2 | `.cursor/memory/architecture/bus_v4.md` | 三层协议 + 拓扑 + 降级策略 |
| 架构图 v3 (内部数据流) | `.cursor/memory/architecture/system_core.md` | Brain/DSG/调度器内部设计（当前名 Scheduler，旧稿中也可能写 Dispatcher） |
| 家族拓扑 | `.cursor/memory/architecture/scene.md` | 大姐/妹妹/猫/调度器/Graphiti |
| 路由规则 | `.cursor/rules/workspace.mdc` | 全局 alwaysApply 路由 |
| 架构与决策总览 | `docs/InfoCollections/HumanPlan/legacy.md` | 核心架构决策、部署方案 |
| 服务器部署摘要 | `docs/InfoCollections/HumanPlan/legacy.md` | 当前东京双节点摘要（独立服务器审计文档待补回/清理） |
| Opus 调研索引 | `docs/InfoCollections/Opus/INDEX.md` | 26 篇调研文档入口 |
| Skill 操作索引 | `docs/InfoCollections/SkillSeekers/INDEX.md` | Skill 状态、拉取命令、待办 |
| nanobot 路由说明 | `docs/InfoCollections/SkillSeekers/NANOBOT_LOCATION_AND_ROUTING_REPORT.md` | `nanobot` 参考层与项目级路由层说明 |
| **P2 里程碑** | `.cursor/memory/milestone_p2.md` | **记忆共享 + Scheduler 增强 + DSG 耦合层** |
| 协议快照 v1 | `.cursor/memory/architecture/protocol_snapshot_p1.md` | RPC/Redis/DataChannel/Blackboard 全量 |
| 部署快照 | `.cursor/memory/deploy_snapshot_p2_20260412.md` | Castle 部署配置与密钥 |
| 协议污染复盘 | `.cursor/memory/BigIssue.md` | 历史教训与修正措施 |

---

## 二、目录结构速查（2026-04-08）

> 详见 `.cursor/memory/architecture/module_division.md`

### 2.1 项目结构

```
ParrotCarriers/                       # 主仓库 (GOSLOParrot/ParrotCarriers)
│
├── src/
│   ├── parrot/                       # ★ Python 源码（Bus + Brain + Scheduler）
│   │   ├── bus/                      # 总线框架
│   │   ├── brain/                    # 云端大脑 (Gemini Agent)
│   │   ├── scheduler/                # 调度器 (SimpleRouter)
│   │   ├── dsg/                      # DSG (Phase 2 填充)
│   │   └── shared/                   # 跨模块共享
│   └── scripts/                      # 运维/工具脚本（当前为空）
│
├── unity/                            # ★ Unity AR 客户端（目录已建，项目待初始化）
│
├── infra/                            # ★ Docker/部署配置
│   ├── docker-compose.yml            # Castle 全栈
│   ├── docker-compose.dev.yml        # 笔记本开发
│   ├── livekit/                      # LiveKit 配置文件（livekit.yaml）
│   └── redis/                        # Redis 配置文件（待填充）
│
├── tests/                            # 测试（integration/test_brain/test_bus/test_scheduler）
├── docs/                             # 皇家大图书馆
├── .vscode/                          # 工作区配置
├── pyproject.toml                    # Python 项目配置
├── .env                              # 环境变量
└── .gitignore

GOSLOParrot/nanobot                   # 独立仓库（fork from HKUDS/nanobot）
└── channels/parrot_bus.py            # ★ 新增: Bus channel adapter
```

### 2.2 `docs/` 结构

```
docs/
├── InfoCollections/                  # 人工规划 / 调研遗产 / Skill 路由 / Gemini 审查
│   ├── HumanPlan/                    # 当前保留的高层架构与部署摘要
│   ├── Opus/                         # 01~26 调研遗产
│   ├── SkillSeekers/                 # Skill 拉取状态、命令、专项路由说明
│   └── GPT/                          # Gemini 审查结果归档
├── references/                       # skill_seekers_output（LiveKit/Nanobot/Graphiti/SVA）
├── report/                           # 便于显式调用、生成后可删除的临时审查文件入口
├── design/                           # 预留
└── specifications/                   # 预留
```

### 2.3 `.cursor/` 结构

```
.cursor/
├── memory/                           # 持久记忆
│   ├── architecture/                 # bus_v4.md, system_core.md, scene.md, module_division.md
│   ├── INDEX.md                      # ★ 本文件（唯一真相源）
│   ├── active_context.md             # ★ 当前进度 + 下一步
│   ├── requirements.md               # ★ 完整功能需求清单 v2
│   └── BigIssue.md                   # 协议污染复盘（待用户重构）
├── rules/                            # Cursor 规则
└── skills/                           # 领域技能
```

### 资料放置规则

| 资料类型 | 放置路径 | Cursor 消费方式 |
|:---------|:---------|:----------------|
| 持久记忆（架构、索引、进度） | `.cursor/memory/` | workspace.mdc 路由指向 |
| 已确认决策（防翻案） | `.cursor/memory/requirements.md` §二 | 需求清单 v2 中的 D1~D11 |
| 规则指令（编码约定、路由） | `.cursor/rules/*.mdc` | 自动/智能/globs 加载 |
| 领域技能（LiveKit/SVA/Graphiti/Nanobot） | `.cursor/skills/<name>/SKILL.md` | 动态发现；`nanobot` 优先显式调用 |
| 外部信息+人工审计结论 | `docs/InfoCollections/HumanPlan/` | @doc 引用 |
| AI 调研文档 | `docs/InfoCollections/Opus/` | @doc 引用 |
| Skill 操作状态 | `docs/InfoCollections/SkillSeekers/` | @doc 引用 |
| Skill Seekers 详细数据 | `docs/references/skill_seekers_output/` | @doc 引用 |
| 工作区终端配置 | `.vscode/settings.json` | 不路由，开发环境配置 |

### Cursor 路由机制

```
workspace.mdc (alwaysApply: true)     ← 每次会话自动加载
    │
    ├─→ INDEX.md (本文件)              ← 全局真相源
    ├─→ active_context.md              ← 进度与下一步
    │
    ├─→ .cursor/skills/                ← 动态发现（nanobot 为显式调用优先）
    │
    └─→ 现有 .mdc 规则（按需触发）
         ├── bus-audit-constraints.mdc ← 审计原则（Phase 1 编码护栏）
         ├── deploy-prep-routing.mdc   ← globs: infra/** 触发
         └── docker-best-practices.mdc ← globs: infra/** + Dockerfile* 触发
```

---

## 三、服务器部署（东京双节点）

> 当前摘要来源: `docs/InfoCollections/HumanPlan/legacy.md` §三

| 节点 | 规格 | 部署组件 | 运行模式 |
|:-----|:-----|:---------|:---------|
| **常驻城堡 (The Castle)** | 东京 ecs.g9i.large (2核8G) | LiveKit Server · Redis · (Phase 2: Neo4j) · Brain Agent · Scheduler · Nanobot Worker | 常开 |
| **按需机甲 (The Mecha)** | 东京 ecs.gn7i (A10 抢占式) | SAM2 + DINOv2 · DSG L1/L2-A | 按需开关，无状态 |

- **同 VPC**: 同一可用区，内网延迟 < 0.1ms
- **控制面 vs 数据面**: ecs.g9i.large = 控制面（状态/路由/记忆）；A10 = 数据面（算力，可抛弃）
- **视频流**: Unity → LiveKit (Castle / ecs.g9i.large) → [内网] → SAM2 (A10)

---

## 四、资源对齐矩阵

| 资源 | 需学习的部分 | Cursor 消费 | 状态 |
|:-----|:-------------|:-----------|:-----|
| **LiveKit** | AgentSession、RPC、DataChannel、Room、Unity SDK | `.cursor/skills/` × 5 | ✅ 已拉 |
| **SVA Vision-Agents** | Processor 模式、attach_agent | `.cursor/skills/sva-vision-agents/` | ✅ 已拉 |
| **Graphiti** | 记忆后端、group_id、Neo4j | `.cursor/skills/graphiti/` | ✅ 已拉 |
| **Nanobot** | 后台 Agent、子任务、多实例、heartbeat、cron | `.cursor/skills/nanobot/` + `docs/references/skill_seekers_output/agent/nanobot/` | ✅ 已接入（显式调用优先） |
| **OpenTeach** | 坐标转换、手势遥测 | `.cursor/skills/` （待补拉） | ⏳ 待拉 |
| **py-trees** | 行为树、黑板 | Opus/14 参考 | Phase 3 按需 |

### 模块当前状态

| 目录 | 模块 | 状态 |
|:-----|:-----|:-----|
| `src/parrot/bus/` | 总线框架 | ✅ 骨架已创建（manifest/registry/heartbeat/mounting/processor_hook） |
| `src/parrot/brain/` | 云端大脑 | ✅ 包结构已创建，tools/ 待填充 |
| `src/parrot/scheduler/` | 调度器（Scheduler / 旧稿 Dispatcher） | ✅ 骨架已创建（router/blackboard） |
| `src/parrot/dsg/` | DSG 感知 | Phase 2 填充，Phase 1 只有 bus/processor_hook 接口 |
| `src/parrot/shared/` | 跨模块共享 | ✅ config/redis_client/constants/types |
| `unity/` | Unity AR 客户端 | 目录已创建，Unity 项目待搭建 |
| `infra/` | Docker/部署 | ✅ docker-compose + livekit.yaml 已创建 |
| `GOSLOParrot/nanobot` (独立仓库) | Nanobot Worker | ✅ 已 fork |

---

## 五、快速导航

| 想了解… | 指向 |
|:--------|:-----|
| 当前进度与下一步 | `active_context.md` |
| 全局路由规则 | `.cursor/rules/workspace.mdc` |
| 架构与决策总览 | `docs/InfoCollections/HumanPlan/legacy.md` |
| 服务器部署（东京） | `docs/InfoCollections/HumanPlan/legacy.md` |
| DSG 四层 + 总线通道 | `.cursor/memory/architecture/system_core.md` |
| 家族角色与关系 | `.cursor/memory/architecture/scene.md` |
| Skill 状态与拉取命令 | `docs/InfoCollections/SkillSeekers/INDEX.md` |
| nanobot 当前路由与使用边界 | `docs/InfoCollections/SkillSeekers/NANOBOT_LOCATION_AND_ROUTING_REPORT.md` |
| Cursor rules/skills 机制 | `docs/InfoCollections/Opus/23_directory_audit_and_cursor_routing.md` |
| Skill 完整拉取命令（P0/P1/P2） | `docs/InfoCollections/SkillSeekers/skill_list_comprehensive.md` |
