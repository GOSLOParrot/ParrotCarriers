---
name: nanobot
description: 用于 ParrotCarriers 中的后台 Agent、子任务、多实例、队列回流与 heartbeat/cron 边界审计
---

# nanobot

Use this skill when working on `Nanobot` positioning inside `ParrotCarriers`.

## When to Use This Skill

Use this skill when you need to:
- 设计 `nanobot-worker` 作为后台复杂任务 Agent 的职责边界
- 审计子任务 / 子代理 / 后台执行模式
- 审计多实例、独立运行时、配置隔离方式
- 审计 `heartbeat` / `cron` / memory consolidation 的可借鉴边界
- 设计 `Scheduler -> Nanobot -> Redis/Graphiti` 的异步回流路径
- 讨论哪些能力应保留为 `nanobot` 模式启发，而不是直接照搬整个上游架构

## Do Not Use For

Do not use this skill as the default source for:
- LiveKit 房间、RPC、DataChannel 设计
- Unity 客户端接入
- DSG / Vision Processor 内部设计
- 通用聊天渠道接入（Telegram / Discord / Feishu / WeChat 等）
- 当前项目的正式部署方案

Those concerns should still route to:
- `livekit-agents`
- `client-sdk-unity`
- `sva-vision-agents`
- `bus-deploy-livekit-ecs`

## ParrotCarriers Scope

In this project, `nanobot` is treated as:

1. 后台复杂任务执行模式的参考来源
2. 子任务 / 子代理 / 多实例运行方式的参考来源
3. 队列消费、结果回写、非阻塞主交互的参考来源
4. 后续项目专用 `nanobot-worker` 设计输入

It is **not** treated as:

1. 当前项目默认主脑框架
2. 当前项目全部技能路由的总入口
3. 当前项目完整部署真相源

## Recommended Reading Order

1. `docs/references/skill_seekers_output/agent/nanobot/SKILL.md`
2. `docs/references/skill_seekers_output/agent/nanobot/references/README.md`
3. `docs/references/skill_seekers_output/agent/nanobot/references/file_structure.md`
4. `docs/references/skill_seekers_output/agent/nanobot/references/releases.md`
5. `docs/references/skill_seekers_output/agent/nanobot/references/issues.md`

## Output Expectations

When using this skill for ParrotCarriers, prefer outputs like:

1. `nanobot-worker` 的输入 / 输出 / 非目标职责
2. 与 `Scheduler`、`Redis`、`Graphiti` 的最小连接关系
3. 多实例 / 长任务 / 定时任务的可借鉴模式
4. 本阶段不做什么

## Fixed Constraints

1. 不要把上游 `nanobot` 的全量聊天渠道能力直接映射到当前项目
2. 不要因为 `nanobot` 有完整 Agent 平台能力，就提前固化当前项目的完整模块设计
3. 要优先抽取“后台任务执行模式”，而不是“整包产品功能”
4. 若输出涉及 `29~31`，当前应以“计划 / 任务拆解输入”口径表达，而不是设计定稿
