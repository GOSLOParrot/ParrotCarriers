# nanobot 位置清单与路由报告

> 状态: 已接入主仓
> 用途: 说明 `HKUDS/nanobot` 当前在主项目中的放置位置、路由方式与使用约束

---

## 1. 当前结论

`nanobot` 已按“两层接入”方式并入主仓：

1. 参考层：
   - `docs/references/skill_seekers_output/agent/nanobot/`
2. 项目级路由层：
   - `.cursor/skills/nanobot/SKILL.md`

这样做的目的，是同时满足两件事：

1. 下一步可以显式调用 `nanobot` 技能参与审计
2. 又不会把上游整包 `nanobot` 知识默认灌入所有任务

---

## 2. 当前定位

在 `ParrotCarriers` 中，`nanobot` 当前定位为：

1. 后台复杂任务 Agent 模式参考
2. 子任务 / 子代理运行时模式参考
3. 多实例 / heartbeat / cron / memory consolidation 参考
4. 未来 `nanobot-worker` 设计输入

当前不把它定位为：

1. 当前项目默认主脑框架
2. LiveKit / Unity / DSG 的主技能来源
3. 当前项目的正式部署真相源

---

## 3. 路由方式

### 3.1 默认路由

当问题涉及以下主题时，可显式使用 `.cursor/skills/nanobot/`：

- 后台复杂任务
- 子任务 / 子代理
- 长任务不阻塞主交互
- 多实例
- heartbeat / cron
- memory consolidation
- `Scheduler -> nanobot-worker -> Redis/Graphiti` 异步回流

### 3.2 不建议默认触发的主题

以下任务不应优先走 `nanobot`：

- LiveKit Room / RPC / DataChannel
- Unity 客户端接入
- DSG Processor 设计
- 通用聊天平台接入
- 当前项目正式部署方案

这些任务仍优先走既有技能：

- `livekit-agents`
- `client-sdk-unity`
- `sva-vision-agents`
- `graphiti`
- `bus-deploy-livekit-ecs`

---

## 4. 与当前阶段的关系

当前项目已完成模块划分，处于 **Phase 1 Bus-first 实施阶段**。

因此 `nanobot` 当前的接入目的不是替代主脑框架，而是：

1. 作为后台复杂任务、多实例、heartbeat/cron 边界的参考输入
2. 支持 `nanobot-worker` 的职责边界继续收敛
3. 为 Phase 1 的异步任务分发与结果回写提供参考

---

## 5. 下一步如何使用

建议在下一步中，把 `nanobot` 主要当作以下审计问题的输入来源：

1. `nanobot-worker` 是否应作为独立后台 worker
2. 它与 `Scheduler` 的接口应是什么粒度
3. 哪些任务适合异步队列
4. 哪些能力应预留为 heartbeat / cron
5. 多实例与运行时隔离是否适合当前项目
