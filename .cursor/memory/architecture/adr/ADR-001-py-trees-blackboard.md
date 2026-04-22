---
status: accepted
adr_id: ADR-001
supersedes: ""
superseded_by: ""
date: 2026-04-22
deciders: "用户 + AI (P2 期决定)"
---

# ADR-001: 用 py-trees 做 Blackboard + BT 核心

## 1. 背景

P2 规划调度器时需要一个**行为树 + 共享 Blackboard**的组合, 用于:
- Brain tool 调用后的状态迁移 (fly_to → flying → perched)
- 多触发器并发 (日程 / 消息 / SSOT 充实 / 场景上下文) 时的优先级仲裁
- 跨进程 Blackboard 订阅 (L1 状态分发给 Unity, Gemini, DSG)

Python 生态里 BT 实现不少: py-trees / BehaviorTree.CPP (via pybind) / 自研 tiny BT / asyncio-based。

## 2. 决策

**选 py-trees 2.x**, 用其 Blackboard V2 作为 L1 运行态缓存的主数据结构。

关键约束:
- Blackboard key 按 `domain/key` 命名 (`vision/state`, `body/cognitive_state`)
- `parrot_behavior_rules.md` 列出的状态集 = Blackboard 的 canonical key 集 (单一真相源)
- **Blackboard 不存历史**, 查历史走 L0 Redis Stream (见 `timeline_api.md §1`)
- BT tick 频率与 Unity RPC 频率解耦 (Unity 走 event-driven, BT 走 pull on demand)

## 3. 备选方案

| 方案 | 放弃原因 | 备注 |
|:-----|:---------|:-----|
| BehaviorTree.CPP (pybind 桥接) | C++ 栈引入构建链 + Windows/WSL debug 痛 | 性能不是瓶颈, 不必上 C++ |
| 自建 tiny BT | 团队 (AI agent 为主) 维护负担高, 没 visualizer | py-trees 的 display 工具直接能画 tick 流程 |
| 纯 asyncio state machine | 缺多触发器优先级仲裁的成熟模式 | 状态机不等于 BT, 抢占/屏蔽语义写手 fragile |
| SMACH / ROS2 BT | 绑 ROS 生态, 部署链太重 | 我们**不**跑在 ROS |

## 4. 后果

**好**:
- Blackboard V2 的 pub/sub 订阅自然匹配 "L1 是大家共享的公告板" 语义
- py-trees 的 Parallel/Selector/Sequence 直接覆盖当前 4 个触发器的优先级
- Visualizer (`py-trees-render`) 便于调试

**坏 / trade-off**:
- py-trees 的 tick 是同步的, 挂长 IO 要用 `Behaviour.initialise()` + async bridge (`scheduler/async_bridge.py` 已写)
- Blackboard 跨进程分发靠我们自己的 Redis 投影 (Sprint 1 做), py-trees 原生只管进程内

**未知 / 需监控**:
- 当触发器数量超过 ~20, py-trees Parallel 的仲裁成本? 目前 4 个不是问题

## 5. 关联

- 代码: `src/parrot/scheduler/` (`blackboard.py`, `bt_router.py`, `async_bridge.py`)
- 技能: `.cursor/skills/py-trees/SKILL.md`
- 规则: `parrot_behavior_rules.md` (Blackboard canonical keys)
- 验证闸门: P2 P2.5 已过 Gate 2 (Brain 语音 + tool 往返)

## 6. Review 点

- 如果 Sprint 2+ 触发器 ≥10, 跑 benchmark 看 tick 开销
- 如果需要跨进程 BT 共享 (极少见), 评估 `behaviortree.cpp` via gRPC
- 如果 Blackboard V2 的订阅模型支撑不了 L1 场景, 考虑换成直接 Redis pub/sub
