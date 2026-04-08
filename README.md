# ParrotCarriers

> RFC 1149: IPoAC, but powered by parrots.

GOSLOParrot 的通信总线子项目 — 构建 Unity AR + 三层 Bus 传输骨架。

## 架构

```
Unity AR 客户端 ←→ LiveKit Room ←→ Brain Agent (Gemini)
                                         ↓
                                    Scheduler → Redis Stream → Nanobot Worker
                                         ↓
                                    Redis Blackboard (状态共享)
```

**三层总线 (Bus v4.2):**
- **L1** — LiveKit 实时层 (语音/RPC/DataChannel)
- **L2** — Redis 状态层 (Pub/Sub + Stream + Blackboard)
- **L3** — Graphiti 知识层 (Phase 2)

## 快速开始

```bash
# 1. 安装依赖
python -m venv .venv
.venv/Scripts/activate   # Windows
pip install -e ".[dev]"

# 2. 启动 Redis + LiveKit Server
docker compose -f infra/docker-compose.dev.yml up -d

# 3. Brain Agent (Dev 模式)
python -m parrot.brain.agent dev

# 4. Scheduler
python src/scripts/start_scheduler.py

# 5. Nanobot Worker
pip install -e ../nanobot[parrot]
python src/scripts/start_nanobot_worker.py

# 6. Unity Client — 见 unity/ParrotDev/README.md
```

## 项目结构

```
src/parrot/           Python 源码根
├── bus/              总线框架 (注册/心跳/挂载/Processor 接口)
├── brain/            云端大脑 (Gemini Agent + Tools)
├── scheduler/        调度器 (SimpleRouter + Blackboard)
├── dsg/              DSG 感知 (Phase 2)
└── shared/           跨模块共享 (config/redis/constants/types)

unity/ParrotDev/      Unity 开发客户端
infra/                部署配置 (Docker Compose + LiveKit)
tests/                单元测试 + 集成测试
```

## 测试

```bash
pytest tests/test_bus/ -v        # 单元测试
pytest tests/integration/ -v     # 集成测试 (需 Redis)
```

## 部署

见 `infra/deploy-castle.sh` — Castle ECS (2C8G, 东京) 最小部署。

## 关联仓库

- [`GOSLOParrot/nanobot`](https://github.com/GOSLOParrot/nanobot) — HKUDS/nanobot fork, 含 `parrot_bus.py` 适配器
