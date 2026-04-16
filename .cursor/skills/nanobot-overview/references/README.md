# nanobot 参考摘要

## 仓库定位

`HKUDS/nanobot` 是一个轻量 Agent 平台，包含：

- agent runtime
- subagent / background execution
- channels / gateway
- tools / MCP
- cron / heartbeat
- memory consolidation
- multiple instances

对 `ParrotCarriers` 来说，最重要的不是聊天渠道，而是这些运行时模式。

## 对当前项目最有价值的点

### 1. 后台复杂任务执行

`nanobot` 已经形成了“前台交互 + 后台任务”的运行模式，这对未来的 `nanobot-worker` 很有参考价值：

- 子任务可独立执行
- 长任务不应阻塞主交互
- 失败时仍保留进度或结果线索

### 2. 多实例与工作区隔离

`nanobot` 明确支持多实例运行：

- 独立 config
- 独立 workspace
- 独立 runtime data
- 独立端口

这对 `ParrotCarriers` 里按模块拆分运行时有启发意义。

### 3. heartbeat / cron / memory

`nanobot` 对主动唤醒和定时任务有成熟做法：

- `heartbeat` 适合做周期性低频检查
- `cron` 适合做计划任务
- memory consolidation 适合做后台压缩或长期状态处理

这些能力在当前项目里不一定原样照搬，但非常适合作为“后台 agent 能做什么”的边界参考。

### 4. tools / MCP / gateway

`nanobot` 提供了：

- 工具调用
- MCP 服务器接入
- gateway 作为对外输入输出层

这对思考 `Dispatcher`、`nanobot-worker`、外部 bridge 的边界有帮助，但当前不应直接等同于本项目 Bus 设计。

## 当前不应直接照搬的部分

以下内容当前不应直接作为 `ParrotCarriers` 设计依据：

- 各类聊天渠道接入细节
- 完整 CLI 产品能力
- 作为个人助手产品的默认配置结构
- 以 `nanobot` 为中心的整个平台架构

## 推荐借鉴子主题

1. subagent / background task
2. multiple instances
3. memory consolidation
4. heartbeat / cron
5. gateway 与结果回流
6. tool / MCP 边界
