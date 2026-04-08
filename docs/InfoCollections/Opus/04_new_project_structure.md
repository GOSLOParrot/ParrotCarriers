# 新项目结构设计

> 生成日期: 2026-02-24
> 项目代号: parrot-ar-cloud
> 用途: 新 Cursor 项目的目录结构、配置文件、依赖管理方案

---

## 1. 顶层目录结构

```
parrot-ar-cloud/
│
├── .cursor/
│   ├── rules/                     # Cursor AI 行为规则
│   │   ├── workspace.mdc          # 全局工作流 (alwaysApply: true)
│   │   ├── architecture.mdc       # 架构约束 (alwaysApply: false)
│   │   ├── backend-python.mdc     # Python 后端约定 (globs: ["agent/**/*.py"])
│   │   └── unity-client.mdc       # Unity C# 约定 (globs: ["unity-client/**/*.cs"])
│   │
│   └── skills/                    # Cursor Agent Skills (按需加载)
│       ├── livekit-agents/
│       │   └── SKILL.md           # LiveKit Agent 开发参考
│       ├── sva-processors/
│       │   └── SKILL.md           # SVA Processor 模式参考
│       ├── gemini-realtime/
│       │   └── SKILL.md           # Gemini Realtime API 参考
│       └── ar-mapping/
│           └── SKILL.md           # OpenTeach AR 映射参考
│
├── agent/                         # Python 云端 Agent (核心)
│   ├── __init__.py
│   ├── main.py                    # 入口: LiveKit Agent 启动
│   ├── session.py                 # AgentSession 配置与生命周期
│   │
│   ├── perception/                # 感知管线 (Vision Pipeline)
│   │   ├── __init__.py
│   │   ├── tracker.py             # SAM2/DINOv2 追踪与特征提取 (L1)
│   │   ├── processor.py           # DSG Compound Processor (多阶段管线编排)
│   │   ├── stability_gate.py      # L1: ARCore 稳定性门控 (Tier 0-3)
│   │   ├── scene_manager.py       # L1: 场景管理器 (切换/检测)
│   │   ├── scene_profiles.py      # L1: 场景 Profile 定义 (Desktop/Indoor/Outdoor)
│   │   ├── spatial_graph.py       # L2-A: RustworkX 空间拓扑图 (分层 SSG + 场景折叠)
│   │   ├── semantic_cache.py      # L2-B: RustworkX 语义注意力图 (+ Graphiti 后端)
│   │   └── reid.py                # 物体 ReID (DINOv2 向量匹配)
│   │
│   ├── brain/                     # 认知层 (L3 Cognitive Interface)
│   │   ├── __init__.py
│   │   ├── gemini_agent.py        # Gemini Realtime Agent 封装
│   │   ├── context_injector.py    # 视觉上下文 → LLM 状态注入
│   │   ├── observer_timeline.py   # L3: 观察者时间线 (感知+对话事件合流)
│   │   └── cognitive_interface.py # L3: 前额叶接口 (LiveKit事件监听+Graphiti归档)
│   │
│   ├── dispatcher/                # 调度层 (行为树 + 资源锁)
│   │   ├── __init__.py
│   │   ├── behavior_tree.py       # py-trees 行为树 (后端调度核心, Phase 3+)
│   │   ├── resource_locks.py      # 资源锁管理器 (body/voice/vision/background)
│   │   ├── task_priority.py       # 优先级定义和中断矩阵
│   │   ├── router.py              # Reflex / Intent / Task 三级路由 (MVP, 后为 BT 叶节点)
│   │   └── redis_bus.py           # Redis Pub/Sub 封装
│   │
│   ├── protocol/                  # 前后端 DataChannel 通信协议
│   │   ├── __init__.py
│   │   ├── commands.py            # 后端→前端 指令 (body_cmd / head_cmd / emotion_cmd)
│   │   ├── telemetry.py           # 前端→后端 遥测 (ar_telemetry)
│   │   └── events.py              # 前端→后端 事件 (gesture / anim / ui)
│   │
│   ├── memory/                    # 记忆层 (Persistence)
│   │   ├── __init__.py
│   │   ├── adapter.py             # 记忆系统抽象接口
│   │   ├── graphiti_impl.py       # Graphiti 实现 (可选)
│   │   └── mock_impl.py           # 模拟器模式 (开发用)
│   │
│   └── tools/                     # Gemini Tool Definitions
│       ├── __init__.py
│       ├── scene_query.py         # 场景查询工具
│       ├── scene_switch.py        # 场景切换工具 (switch_scene)
│       ├── memory_search.py       # 记忆搜索工具
│       └── body_control.py        # 鹦鹉身体控制工具
│
├── unity-client/                  # Unity AR 客户端 (另一个仓库或子目录)
│   ├── Assets/
│   │   ├── Scripts/
│   │   │   ├── LiveKit/           # LiveKit SDK 集成
│   │   │   ├── Parrot/            # 鹦鹉控制器 (动画/导航/状态)
│   │   │   ├── AR/                # AR 平面/锚点/手势
│   │   │   └── DataBridge/        # DataChannel 数据桥接
│   │   └── Prefabs/
│   └── Packages/
│
├── infra/                         # 基础设施配置
│   ├── docker-compose.yml         # 本地开发: LiveKit + Redis + (Qdrant)
│   ├── docker-compose.cloud.yml   # 云端部署: 阿里云配置
│   ├── Dockerfile.agent           # Agent 容器
│   └── livekit-server.yaml        # LiveKit Server 配置
│
├── reference/                     # 参考仓库 (git submodule 或 .gitignore)
│   ├── livekit-agents/            # 克隆的 livekit/agents
│   ├── vision-agents/             # 克隆的 GetStream/Vision-Agents
│   └── README.md                  # 参考仓库使用说明
│
├── doc/                           # 项目文档
│   ├── architecture.md            # 架构设计文档
│   ├── bus-design.md              # 总线设计 (LiveKit DataChannel 协议)
│   ├── vision-plan.md             # 视觉管线设计
│   └── roadmap.md                 # 路线图与里程碑
│
├── pyproject.toml                 # Python 依赖 & 项目元数据
├── .env.example                   # 环境变量模板
├── .gitignore
└── README.md
```

---

## 2. 配置文件设计

### 2.1 pyproject.toml

```toml
[project]
name = "parrot-ar-cloud"
version = "0.1.0"
description = "Cloud-native AR Parrot Companion powered by LiveKit + Gemini"
requires-python = ">=3.10"
dependencies = [
    "livekit-agents>=1.0",
    "livekit-plugins-google>=1.0",
    "livekit-plugins-silero>=1.0",
    "redis>=5.0",
    "pydantic>=2.0",
    "rustworkx>=0.15",
]

[project.optional-dependencies]
vision = [
    "torch>=2.0",
    "segment-anything-2",
    "transformers",
    "numpy>=1.24",
]
memory = [
    "graphiti-core>=0.18",
    "neo4j>=5.26",
]
dev = [
    "pytest>=8.0",
    "ruff>=0.4",
    "mypy>=1.10",
]

[tool.ruff]
target-version = "py310"
line-length = 120

[tool.mypy]
python_version = "3.10"
strict = true
```

### 2.2 .env.example

```dotenv
# === LiveKit ===
LIVEKIT_URL=wss://your-livekit-server.example.com
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# === Gemini ===
GOOGLE_API_KEY=your_gemini_api_key

# === Redis ===
REDIS_URL=redis://localhost:6379

# === Vision (可选, Phase 3) ===
# QDRANT_URL=http://localhost:6333

# === Memory (可选, Phase 3) ===
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=password
```

### 2.3 docker-compose.yml (本地开发)

```yaml
version: "3.9"
services:
  livekit-server:
    image: livekit/livekit-server:latest
    ports:
      - "7880:7880"
      - "7881:7881"
      - "7882:7882/udp"
    volumes:
      - ./infra/livekit-server.yaml:/etc/livekit.yaml
    command: --config /etc/livekit.yaml

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### 2.4 livekit-server.yaml

```yaml
port: 7880
rtc:
  port_range_start: 50000
  port_range_end: 60000
  use_external_ip: true
keys:
  devkey: devsecret
logging:
  level: info
```

---

## 3. 设计原则

### 3.1 分层隔离

```
Unity Client  ←─ WebRTC + DataChannel ─→  LiveKit Server  ←─→  Python Agent
    (AR/手势/动画)                                              (感知/认知/调度)
```

- Unity 只负责渲染、输入采集、动画执行
- Python 只负责感知、推理、调度
- LiveKit 是唯一的通信通道

### 3.2 适配器模式

所有外部依赖通过接口隔离：

```python
# memory/adapter.py
class MemoryAdapter(ABC):
    @abstractmethod
    async def store_episode(self, episode: Episode) -> None: ...
    
    @abstractmethod
    async def search(self, query: str) -> list[MemoryResult]: ...
```

确保可以用 `mock_impl.py` 在无外部服务时完成开发和测试。

### 3.3 渐进式复杂度

- Phase 1 仅需: `agent/main.py` + `agent/session.py` + LiveKit + Redis
- Phase 2 增加: `agent/dispatcher/` + Unity DataChannel
- Phase 3 增加: `agent/perception/` + `agent/memory/`

每个 Phase 独立可运行、可验证。
