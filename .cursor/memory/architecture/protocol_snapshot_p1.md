---
status: ratified
category: reference
status_note: "V1 协议定版 (2026-04-12), 代码已验通。新协议变更走 ADR + bump 版本号。"
last_reviewed: 2026-04-22
---

# Mount Protocol V1

> 定版日期: 2026-04-12
> 状态: V1 正式版（可迭代，发现问题随时修订）
> 护栏: "已验证" = 有消费代码且端到端跑通过；"有消费代码" = 有读写代码但未端到端验证；"候选" = 接口定义了但无消费代码
> 项目层级: GOSLOParrot (主项目) → ParrotCarriers (Bus 基建子项目)

---

## 1. RPC 签名 (LiveKit Room RPC)

| RPC 方法 | 方向 | 参数 | 返回 | 状态 |
|:---------|:-----|:-----|:-----|:-----|
| `flyTo` | Brain → Unity | `{"x": float, "y": float, "z": float}` | `"ok"` | **已验证** — sim_unity_client + Brain Agent |
| `animate` | Brain → Unity | `{"animation": ParrotAnimation.value}` | `"ok"` | **已验证** — sim_unity_client + Brain Agent |

**ParrotAnimation 枚举值**: `idle`, `fly`, `dance`, `wing_flap`, `perch`, `sit`, `head_bob`, `sleep`
定义位置: `src/parrot/shared/parrot_actions.py :: ParrotAnimation`

---

## 2. Redis Channel Schema

### 2.1 有消费代码的通道（已验证）

| 常量 | 通道名 | 类型 | 发布方 | 消费方 | 消息格式 |
|:-----|:-------|:-----|:-------|:-------|:---------|
| `CH_SCHEDULER_COMMANDS` | `parrot.scheduler.commands` | Pub/Sub | `dispatch_task` tool | `SchedulerService._listen_commands` | `{"task_id": str, "type": str, "params": dict, "priority": str}` |
| `CH_SCHEDULER_RESULTS` | `parrot.scheduler.results` | Pub/Sub | `SchedulerService._listen_commands` | 集成测试 | `{"task_id": str, "destination": str, "status": "routed"}` |
| `CH_NANOBOT_RESULTS` | `parrot.nanobot.results` | Pub/Sub | `NanobotConsumer` | `SchedulerService._listen_nanobot_results` | `{"task_id": str, "type": str, "status": str, "result": str}` |
| `CH_SCHEDULER_TO_BRAIN` | `parrot.scheduler.to_brain` | Pub/Sub | `SchedulerService._listen_nanobot_results` | `Brain._listen_scheduler_results` | `{"task_id": str, "type": str, "status": str, "result_summary": str, "source_worker": str}` | **有消费代码** — 集成测试待 Redis 验证 |
| `STREAM_NANOBOT_DISPATCH` | `parrot.nanobot.dispatch` | Stream | `SchedulerService._listen_commands` | `NanobotConsumer` | `{"payload": JSON(task)}` |
| `HASH_MODULES` | `parrot.modules` | Hash | `registry` | `registry` | module_id → JSON(manifest) |
| `HASH_HEARTBEAT` | `parrot.heartbeat` | Hash | `heartbeat` | `registry` | module_id → timestamp |

### 2.2 候选通道（已定义常量，无消费代码）

| 常量 | 通道名 | 计划用途 | 预计阶段 |
|:-----|:-------|:---------|:---------|
| `CH_EVENTS_FIREHOSE` | `parrot.events.firehose` | 全局事件广播 | P2+ |
| `CH_BRAIN_DECISIONS` | `parrot.brain.decisions` | Brain 决策日志 | P2 |
| `CH_BRAIN_FOCUS` | `parrot.brain.focus_commands` | Brain 注意力指令 | P2 |
| `CH_DSG_EVENTS` | `parrot.dsg.events` | DSG 节点变化触发器 | P2 (A10) |
| `CH_DSG_SCENE_UPDATE` | `parrot.dsg.scene_update` | DSG 场景更新 | P2 (A10) |
| `CH_DSG_SENTINEL` | `parrot.dsg.sentinel.evidence` | DSG 哨兵证据 | P2 (A10) |
| `CH_EXTERNAL_COMMANDS` | `parrot.external.commands` | 外部渠道命令 | P2 |
| `BB_PARROT_STATE` | `parrot_state` (Hash) | Redis Blackboard 遗留 | 候选移除 |
| `BB_SCENE_CONTEXT` | `scene_context` (Hash) | Redis Blackboard 遗留 | 候选移除 |
| `BB_RESOURCE_LOCKS` | `resource_locks` (Hash) | 资源锁 | P2 |

---

## 3. DataChannel 格式

### 3.1 Unity→Python: 遥测帧 (Lossy, 10Hz)

Topic: `parrot.telemetry`

```json
{
  "pose": {
    "position": {"x": 0.0, "y": 0.0, "z": 0.0},
    "rotation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}
  },
  "timestamp": 1712880000.123,
  "behavior_state": "idle",
  "anim_clip": "idle"
}
```

定义位置: `src/parrot/shared/telemetry.py :: TelemetryFrame`
状态: **候选** — Python 端接收回调已注册，Unity 端发送待 P2 实现

### 3.2 Unity→Python: 事件 (Reliable, event-driven)

Topic: `parrot.event`

```json
{
  "type": "arrived",
  "payload": {"target": [1.0, 2.0, 3.0]},
  "timestamp": 1712880000.456
}
```

定义位置: `src/parrot/shared/telemetry.py :: TelemetryEvent`
状态: **候选**

### 3.3 Python→Unity: 指令 (Reliable, event-driven)

Topic: `parrot.command`
状态: **候选** — P2 实现。目前 Python→Unity 走 RPC (`flyTo`, `animate`)。

---

## 4. py-trees Blackboard Namespace + 读写权限

Namespace: `/scheduler/`

| Key | 类型 | 读权限 | 写权限 | 描述 | 状态 |
|:----|:-----|:-------|:-------|:-----|:-----|
| `active_tasks` | `dict[task_id, TaskInfo]` | Scheduler nodes | DispatchToNanobot, SchedulerService | 当前活跃任务追踪 | **已验证** — BT 节点写入 + result listener 更新 |
| `behavior_mode` | `BehaviorMode` Flag | Scheduler, ParrotSoul | BTRouter init, Brain (P2) | 行为模式 (BASE\|COMPANION) | **有消费代码** — BTRouter 初始化写入；ParrotSoul 消费接口就绪，动态切换待 P2 |
| `current_event` | `dict` | BT nodes (all) | BTRouter.route() | 当前待路由事件 | **已验证** — 每次 route() 写入 |
| `route_result` | `dict` | BTRouter, SchedulerService | BT nodes | BT tick 路由决策结果 | **已验证** — 每次 tick 后读取 |
| `resource_locks` | `dict[channel, holder_id]` | Lock nodes | Lock nodes | 资源互斥锁 | **候选** — P2 |

Blackboard 初始化: `src/parrot/scheduler/blackboard.py :: init_scheduler_blackboard()`
Redis 持久化适配层: `src/parrot/scheduler/blackboard.py :: RedisBlackboardSync` (候选，P2+)

---

## 5. 共享枚举

| 枚举 | 位置 | 值 | 消费方 |
|:-----|:-----|:---|:-------|
| `ParrotAnimation` | `shared/parrot_actions.py` | idle, fly, dance, wing_flap, perch, sit, head_bob, sleep | Brain tools (animate), Unity Animator |
| `ParrotBodyState` | `shared/parrot_actions.py` | idle, flying, perching, dancing, frozen | TelemetryFrame.behavior_state, Unity Animator |
| `BehaviorMode` | `shared/parrot_actions.py` | BASE, COMPANION, BUTLER, RESEARCHER, PLAYFUL | Blackboard /scheduler/behavior_mode, ParrotSoul |

---

## 6. 模块入口 + 端口

| 模块 | 入口命令 | 依赖 |
|:-----|:---------|:-----|
| Brain Agent | `python -m parrot.brain.agent dev` | LiveKit Server, Redis, Google API Key |
| Scheduler | `python src/scripts/start_scheduler.py` | Redis |
| Nanobot Worker (真实) | `python src/scripts/start_nanobot_worker.py` | Redis, nanobot[parrot], OPENROUTER_API_KEY |
| Nanobot Consumer (stub) | `python src/scripts/start_nanobot_worker.py --stub` | Redis |
| Redis | `docker compose -f infra/docker-compose.dev.yml up -d` | Docker |
| LiveKit Server | 同上 docker-compose | Docker |

### 6.1 Nanobot Worker 架构

```
ParrotCarriers Scheduler
    → Redis Stream (parrot.nanobot.dispatch)
        → nanobot gateway (parrot_bus + weixin channels)
            → nanobot AgentLoop (LLM处理)
                → Redis Pub/Sub (parrot.nanobot.results)
                    → Scheduler aggregation
                        → CH_SCHEDULER_TO_BRAIN
                            → Brain 语音反馈

用户微信
    → nanobot gateway (weixin channel, HTTP 长轮询)
        → nanobot AgentLoop (同一实例, 独立 session)
            → 微信回复
```

**真实模式**: `start_nanobot_worker.py` 启动 nanobot gateway，同时运行两个 channel：
- **parrot_bus**: Redis Stream 消费 ParrotCarriers 任务
- **weixin**: HTTP 长轮询接收微信消息（猫娘女仆直接对话）

LLM (Gemini Flash via OpenRouter) 处理任务，结果按 channel 路由。

**Stub 模式**: `start_nanobot_worker.py --stub` 使用内置 NanobotConsumer，echo 回传（无 LLM）。
**无微信模式**: `start_nanobot_worker.py --no-weixin` 只启用 parrot_bus（用于 CI/测试）。

**NANOBOT_TASK_TYPES**: research, summarize, remind, memory_consolidation, vocabulary_learn

---

## 7. 待验证项 (P1.5 遗留 → P2 验证)

- [ ] DataChannel 遥测端到端 (Unity 发送 → Python 接收 → Blackboard)
- [ ] BehaviorMode 动态切换 (Brain 通过 Redis 更新 Blackboard → ParrotSoul 重新拼接 instructions → session.update_instructions)
- [x] CH_SCHEDULER_TO_BRAIN 集成测试在 Redis 环境下端到端验证 — **已验证** (test_nanobot_channel + test_dispatch_chain)
- [ ] RedisBlackboardSync 持久化适配层
- [ ] 资源锁 (/scheduler/resource_locks)
- [x] CH_SCHEDULER_TO_BRAIN 消息的 result_summary 字段填充真实内容 — **已修复** (stub 增加 result 字段; 真实模式由 LLM 输出)
- [ ] Castle 部署端到端验证 (Brain + Scheduler + Nanobot worker on remote server)
- [ ] Nanobot gateway 真实 LLM 处理 + 结果质量 (需 OPENROUTER_API_KEY)

---

## 8. Nanobot 并发能力审计 (V1)

| 项目 | 状态 |
|:-----|:-----|
| 跨 task 并发 | ✅ 不同 task_id = 不同 session，可并行 |
| 默认并发上限 | `NANOBOT_MAX_CONCURRENT_REQUESTS=3`（env 可调） |
| 同 task 内部 | 串行 LLM 迭代（合理设计） |
| 子代理 spawn | ✅ 支持，多子代理可同时跑 |
| 会话隔离 | ✅ chat_id=task_id，独立 session，不串历史 |
| 水平扩展 | 可起多个 consumer（不同 consumerName） |

**V1 已知限制（P2 处理）：**
- ToolRegistry.set_context 共享 → 高并发可能串 channel/chat_id（V1 只有 parrot_bus 一个 channel，不触发）
- parrot_bus xreadgroup count=1 → 逐条消费（V1 够用，P2 可提升 count 或多 consumer）

---

## 9. 微信 Bot 挂载 (V1)

### 9.1 猫娘女仆 (Nanobot) 微信 Bot

**状态**: **已验证** — QR 登录成功 + gateway 双 channel 并行 + Gemini API + 微信收发 200 OK

| 项目 | 值 |
|:-----|:---|
| Channel | `weixin` (nanobot 内置，HTTP 长轮询) |
| 配置 | `parrot_config.json` → `channels.weixin.enabled: true` |
| 人格 | `~/.nanobot/workspace/SOUL.md` (猫娘女仆) |
| 登录 | `nanobot channels login weixin -c config/parrot_config.json` |
| 认证存储 | `~/.nanobot/weixin/account.json` (QR 扫码后自动保存) |
| 与 parrot_bus 关系 | 同一 nanobot 实例，共享 AgentLoop，独立 session |

**双 Channel 并行**: 微信消息和 ParrotCarriers 任务由同一个 nanobot 实例处理，
但走不同 session（chat_id 不同），互不干扰。微信用户直接与猫娘女仆聊天，
ParrotCarriers 任务由 Scheduler 通过 Redis Stream 派发。

### 9.2 GOSLO 微信 Bot (P2 预留)

GOSLO 的微信 Bot 需要第二个 nanobot 实例（不同 config + 不同 workspace + 不同 SOUL.md），
涉及 GOSLO 双身体模式（Gemini Live + 聊天 Bot）的状态同步，计划 P2 实现。

---

## 10. 角色工作模式与多实例架构 (P2)

### 10.1 GOSLO 双身体模式

GOSLO 有两个"身体"，通过 Redis 模式信号协调：

| 身体 | 实现 | 活跃条件 | Channel |
|:-----|:-----|:---------|:--------|
| **Live** | Brain Agent (Gemini RealtimeModel) | Unity AR app 打开时 | LiveKit |
| **Chat** | nanobot 实例 (ParrotSoul 人格) | 常开，Live 在线时转发/静默 | Telegram / 微信 |

**模式信号**: `HASH_GOSLO_MODE = "parrot.goslo.mode"` (Redis Hash)

| 字段 | 值 | 写入方 |
|:-----|:---|:-------|
| `active_body` | `"live"` / `"chat"` | Brain Agent (连接时 live, 断开时 chat) |
| `live_session_id` | Room name | Brain Agent |
| `updated_at` | ISO 8601 timestamp | Brain Agent |

状态: **已实现** — `constants.py` + `brain/agent.py` mount/disconnect 写入

### 10.2 多 nanobot 实例架构

| 实例 | 配置 | Workspace | Channel | 人格 |
|:-----|:-----|:----------|:--------|:-----|
| 猫娘女仆 | `parrot_config.json` | `~/.nanobot/workspace/` | parrot_bus + weixin | 猫娘 SOUL.md |
| GOSLO Chat | `goslo_config.json` | `~/.nanobot/goslo-workspace/` | telegram | ParrotSoul SOUL.md |

**资源**: 两个 nanobot 实例 = 两个独立 Python 进程。单实例空闲 ~50-80MB，2C8G 充裕。
**隔离**: 不同 `--config` + `--workspace` → 不同人格/channel/session，共享 Redis 做跨实例通信。

### 10.3 信息共享策略 (P2 Graphiti 部署后)

| Graphiti 分区 | group_id | 写入方 | 只读方 |
|:-------------|:---------|:-------|:-------|
| GOSLO 记忆 | `goslo` | GOSLO Live + Chat | 猫娘（任务需要时） |
| 猫娘记忆 | `maid` | 猫娘女仆 | GOSLO（查询任务结果时） |
| 场景信息 | `scene` | Brain / DSG | 所有角色 |
| 用户画像 | `user` | 所有角色 | 所有角色 |

**Redis 实时共享层**: 模式信号 (`HASH_GOSLO_MODE`)、任务结果 (`CH_NANOBOT_RESULTS`)、场景快照 (`parrot.scene.snapshot`, P2 候选)

### 10.4 协作架构定位

**ParrotCarriers = 副协作模块 + 信息提供商**，不膨胀为 one-for-all 工作区：
- Redis Bus: 实时调度 + 状态协调（毫秒级）
- Graphiti: 长期记忆 + 知识图谱（分钟级）
- Obsidian: SSOT 文件/知识锚点（通过 MCP Bridge P3+）
- 群聊 UI: LobeChat / Telegram 群（外挂成熟项目 P3）

不引入 AutoGen/CrewAI 等外部协作框架——Agent 是多进程独立实例，Redis Bus 已具备全部路由能力。

### 10.5 关键设计决策

| 决策 | 内容 |
|:-----|:-----|
| D12 | GOSLO 有两个身体：Gemini Live（按需）+ 聊天 bot（常开）。通过 Redis 模式信号协调 |
| D13 | Nanobot 猫娘女仆是独立角色，有自己的人格和聊天 bot。不是 GOSLO 的分身 |
| D14 | 每个角色的 Graphiti 分区独立 (goslo/maid)，Scene/User 分区共享只读 |
| D15 | Gemini Live 开启时，GOSLO Chat bot 转发消息到 Brain，不自主回复 |
| D16 | 微信群聊 = P3 目标；P2 先做各角色 1对1 bot (猫娘微信 + GOSLO Telegram) |
| D17 | ParrotCarriers 定位为副协作模块，外挂 Obsidian/LobeChat 做主工作区 |

---

## 11. V1 版本说明

- 本协议为第一版定版，非终态
- 发现问题随时迭代，不需要等下一个大版本
- Bus 层（ParrotCarriers）和各模块的接口独立，改一个不影响另一个
- Scheduler BT 设计天然支持扩展（加叶子节点 / Parallel composite / 资源锁）
- Nanobot channel 设计支持群聊语义扩展（为 Gemini 二重身 / 外部聊天渠道预留）
- 猫娘女仆微信 Bot 为 V1 首个外部聊天渠道，验证 nanobot 多 channel 并行能力
