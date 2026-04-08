# ParrotCarriers 模块划分与目录结构 (2026-04-08)

> 关联: `requirements.md` v2 + `bus_v4.md` v4.2
> 原则: Module-First Development (MFD) — 先模块边界，后协议细节

---

## 一、模块总览（MFD 三类 × 服务器落位）

### Core 模块（自研核心，不可替换）

| 模块 | 角色 | 运行位置 | 参与层级 | Phase |
|:-----|:-----|:---------|:---------|:------|
| **bus** | 总线框架：模块注册、心跳、挂载协议、Processor 挂载接口 | Castle / 笔记本(dev) | L1+L2 | 1 |
| **brain** | 云端大脑：AgentSession + Gemini + Tool Forwarding | Castle | L1+L2+L3 | 1 |
| **scheduler** | 调度器：SimpleRouter → 三级调度 → py-trees | Castle | L1+L2 | 1 |
| **dsg** | 视觉感知：SAM2 + YOLO + L2-A/B | Mecha A10 | L1+L2+L3 | 2 |

### Integration 模块（fork/改造上游，需持续同步）

| 模块 | 上游 | 改造点 | 运行位置 | Phase |
|:-----|:-----|:-------|:---------|:------|
| **nanobot** | HKUDS/nanobot (fork) | 新增 `channels/parrot_bus.py` 适配器 | Castle | 1 |

### Glue 模块（pip 依赖，不改源码）

| 包 | 用途 | 引入方式 |
|:---|:-----|:---------|
| livekit-agents | Brain Agent 框架 + Room 连接 | `pip install livekit-agents[google]` |
| graphiti-core | 知识图谱读写（Phase 2） | `pip install graphiti-core` |
| redis | L2 状态层客户端 | `pip install redis` |

---

## 二、仓库策略

### 双仓库架构

```
GOSLOParrot/ParrotCarriers    ← 主仓库（Bus + Brain + Scheduler + DSG + Unity + Infra）
GOSLOParrot/nanobot            ← fork 仓库（HKUDS/nanobot 改造）
```

**为什么 nanobot 单独仓库：**
- 需要跟踪上游更新（git remote add upstream）
- nanobot 有自己的依赖树和配置系统
- `parrot_bus.py` 是在 nanobot 的 `channels/` 目录下新增的适配器
- 开发时通过 `pip install -e ../nanobot` 本地联调

### 参考仓库（clone 来读，不 fork）

```
refs/agent-starter-python/     ← livekit-examples/agent-starter-python
refs/python-agents-examples/   ← livekit-examples/python-agents-examples
refs/agents-example-unity/     ← livekit-examples/agents-example-unity
```

这些放在 ParrotCarriers 外部（笔记本某个参考目录），不纳入 git。

---

## 三、ParrotCarriers 目录结构（Phase 1 目标）

```
ParrotCarriers/
│
├── .cursor/                          # 作战指挥室（已有，不变）
│   ├── memory/                       # 持久记忆
│   │   ├── architecture/             # bus_v4.md, system_core.md, scene.md, module_division.md
│   │   ├── INDEX.md
│   │   ├── active_context.md
│   │   ├── requirements.md
│   │   └── BigIssue.md
│   ├── rules/                        # Cursor 规则
│   └── skills/                       # 领域技能
│
├── src/                              # ★ Python 源码根目录
│   ├── parrot/                       # 顶级包: parrot
│   │   ├── __init__.py
│   │   │
│   │   ├── bus/                      # Core: 总线框架
│   │   │   ├── __init__.py
│   │   │   ├── manifest.py           # ModuleManifest dataclass
│   │   │   ├── registry.py           # 模块注册 + 发现（Redis Hash）
│   │   │   ├── heartbeat.py          # Bus 心跳管理
│   │   │   ├── mounting.py           # 模块挂载协议（路径 A + 路径 B）
│   │   │   └── processor_hook.py     # D0: DSG Processor 挂载接口（参考 SVA base_processor）
│   │   │
│   │   ├── brain/                    # Core: 云端大脑
│   │   │   ├── __init__.py
│   │   │   ├── agent.py              # AgentSession + Gemini RealtimeModel 入口
│   │   │   ├── soul.py               # ParrotSoul 人格注入
│   │   │   ├── context.py            # Context Injector (Phase 2 填充)
│   │   │   └── tools/                # Brain function_tools
│   │   │       ├── __init__.py
│   │   │       ├── fly_to.py         # B4
│   │   │       ├── animate.py        # B5
│   │   │       ├── dispatch_task.py  # B11: Brain → Scheduler → Nanobot
│   │   │       └── _rpc_bridge.py    # Tool → RPC 转发公共逻辑
│   │   │
│   │   ├── scheduler/                # Core: 调度器
│   │   │   ├── __init__.py
│   │   │   ├── router.py             # E1: SimpleRouter (if-else 优先级)
│   │   │   └── blackboard.py         # E3: Redis Blackboard 读写封装
│   │   │
│   │   ├── dsg/                      # Core: DSG（Phase 2 填充，Phase 1 只有接口）
│   │   │   ├── __init__.py
│   │   │   └── README.md             # "Phase 2: A10 就绪后实现"
│   │   │
│   │   └── shared/                   # 跨模块共享
│   │       ├── __init__.py
│   │       ├── config.py             # 环境变量加载 (.env)
│   │       ├── redis_client.py       # Redis 连接工厂
│   │       ├── constants.py          # Redis channel 名、Room 名等常量
│   │       └── types.py              # 共享类型定义
│   │
│   └── scripts/                      # 开发/运维脚本
│       ├── start_brain.py            # 启动 Brain Agent
│       ├── start_scheduler.py        # 启动 Scheduler
│       └── health_check.py           # 模块健康检查
│
├── unity/                            # ★ Unity AR 客户端（独立 Unity 项目）
│   ├── ParrotAR/                     # Unity 项目根
│   │   ├── Assets/
│   │   │   ├── Scripts/
│   │   │   │   ├── LiveKit/          # C1: LiveKit 连接
│   │   │   │   ├── RPC/              # C4: RPC Handler
│   │   │   │   ├── Parrot/           # C3: Animator HSM
│   │   │   │   └── Telemetry/        # C5: 遥测上报
│   │   │   ├── Models/               # Minecraft 鹦鹉模型
│   │   │   ├── Animations/           # 鹦鹉动画
│   │   │   └── Audio/                # 鹦鹉声音
│   │   ├── Packages/
│   │   └── ProjectSettings/
│   └── README.md
│
├── infra/                            # ★ 部署配置
│   ├── docker-compose.yml            # Castle 全栈: LiveKit + Redis + (Phase 2: Neo4j)
│   ├── docker-compose.dev.yml        # 笔记本本地开发: Redis only
│   ├── livekit/
│   │   └── livekit.yaml              # LiveKit Server 配置
│   ├── redis/
│   │   └── redis.conf                # Redis 配置（内存限制等）
│   └── .env.castle                   # Castle 环境变量模板
│
├── docs/                             # 皇家大图书馆（已有，不变）
│
├── tests/                            # 测试
│   ├── test_bus/                     # Bus 框架测试
│   ├── test_brain/                   # Brain Agent 测试
│   ├── test_scheduler/               # Scheduler 测试
│   └── integration/                  # 集成测试（模块间通信）
│
├── pyproject.toml                    # Python 项目配置（依赖、入口点）
├── .env                              # 本地环境变量（已有）
├── .gitignore                        # （已有，需更新）
└── README.md                         # 项目说明（待写）
```

### nanobot fork 目录结构（GOSLOParrot/nanobot，独立仓库）

```
nanobot/                              # fork from HKUDS/nanobot
├── ...                               # 上游原始结构保持
├── channels/
│   ├── ...                           # 上游已有的渠道 (wechat/telegram/...)
│   └── parrot_bus.py                 # ★ 新增: ParrotCarriers Bus channel adapter
├── config/
│   └── parrot.toml                   # ★ 新增: ParrotCarriers 专用配置
└── ...
```

---

## 四、模块 → 服务器落位

### Phase 1 运行时拓扑

```
┌──────────────────────────────────────────┐
│  笔记本（开发环境）                        │
│                                          │
│  Docker Desktop:                         │
│    └── Redis (dev)                       │
│                                          │
│  Cursor venv:                            │
│    ├── parrot.bus       (Bus 框架)       │
│    ├── parrot.brain     (Brain Agent)    │
│    ├── parrot.scheduler (Scheduler)      │
│    └── nanobot          (pip -e ../nanobot) │
│                                          │
│  Unity Editor:                           │
│    └── ParrotAR         (连接本地或 Castle) │
└──────────────────────────────────────────┘
              │
              │ (开发完成 → 部署)
              ▼
┌──────────────────────────────────────────┐
│  Castle ECS (2C8G, 东京)                  │
│                                          │
│  Docker Compose:                         │
│    ├── LiveKit Server                    │
│    ├── Redis                             │
│    └── (Phase 2: Neo4j)                  │
│                                          │
│  进程:                                    │
│    ├── Brain Agent      (systemd/docker) │
│    ├── Scheduler        (systemd/docker) │
│    └── Nanobot Worker   (systemd/docker) │
└──────────────────────────────────────────┘
              │
              │ (Phase 2, 同 VPC 内网)
              ▼
┌──────────────────────────────────────────┐
│  Mecha A10 (按需 Spot, 东京)              │
│                                          │
│  进程:                                    │
│    └── DSG Worker       (连接 Castle)    │
└──────────────────────────────────────────┘
```

### 模块 × 服务器对照表

| 模块 | 笔记本(dev) | Castle(prod) | Mecha A10 | 手机 |
|:-----|:----------:|:------------:|:---------:|:----:|
| bus 框架 | ✅ | ✅（嵌入各模块） | ✅（嵌入 DSG） | — |
| brain | ✅ | ✅ | — | — |
| scheduler | ✅ | ✅ | — | — |
| nanobot | ✅ | ✅ | — | — |
| dsg | — | — | ✅ | — |
| unity | ✅(Editor) | — | — | ✅(APK) |
| LiveKit Server | — | ✅(Docker) | — | — |
| Redis | ✅(Docker) | ✅(Docker) | — | — |
| Neo4j | — | ✅(Docker, P2) | — | — |

---

## 五、Phase 1 验证矩阵

Phase 1 Bus-first 需要验证的 5 条核心链路：

| # | 链路 | 起点 → 终点 | 层级 | 验证标准 |
|:--|:-----|:-----------|:-----|:---------|
| V1 | Brain ↔ Unity (语音) | Gemini TTS → LiveKit → Unity Speaker | L1 | 听到语音回复 |
| V2 | Brain → Unity (指令) | fly_to Tool → RPC → Unity Animator | L1 | 鹦鹉执行动作 |
| V3 | Brain → Scheduler → Nanobot | dispatch_task → Redis Stream → Nanobot 消费 | L2 | Nanobot 收到并执行任务 |
| V4 | 模块注册与心跳 | 各模块 → Redis Hash → Bus 监控 | L2 | 所有模块显示 online |
| V5 | Nanobot → Bus (结果回写) | Nanobot 完成 → Redis → Scheduler/Brain | L2 | Brain 收到任务结果 |

---

## 六、你的并行工作清单

在我进行 fork 和代码骨架搭建的同时，你可以做以下工作：

### 立即可做

| # | 任务 | 预计耗时 | 说明 |
|:--|:-----|:---------|:-----|
| U1 | **确认 Python 版本** | 5 分钟 | 在 Cursor terminal 跑 `python --version`，确认 ≥ 3.11 |
| U2 | **Docker Desktop 启动 Redis** | 10 分钟 | `docker run -d --name parrot-redis -p 6379:6379 redis:7-alpine` |
| U3 | **fork HKUDS/nanobot** | 5 分钟 | GitHub 上 fork 到 `GOSLOParrot/nanobot` |
| U4 | **clone 参考仓库** | 15 分钟 | clone `agent-starter-python` + `python-agents-examples` 到笔记本某个参考目录 |

### 可并行推进（不阻塞 Phase 1）

| # | 任务 | 说明 |
|:--|:-----|:-----|
| U5 | **Minecraft 鹦鹉资产收集** | 找模型/动画/声音，确认 Unity 导入格式 |
| U6 | **Castle ECS 访问调查** | SSH key、安全组、Docker 安装情况 |
| U7 | **Unity 开发环境** | Unity 2022 LTS + AR Foundation + 创建空 ParrotAR 项目 |
| U8 | **浏览 agent-starter-python 示例** | 了解 LiveKit Agent 怎么写，为 Brain Agent 做准备 |

### 需要但不紧急

| # | 任务 | 说明 |
|:--|:-----|:-----|
| U9 | **Gemini API 测试** | 用 .env 中的 key 调一次 Gemini API 确认可用 |
| U10 | **LiveKit Cloud 免费测试（可选）** | 在 Castle 部署前，可先用 LiveKit Cloud 验证 Agent 连接 |
