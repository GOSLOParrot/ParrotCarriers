# nanobot 版本演进摘要

## 当前最相关版本

### `v0.1.4.post6` - 2026-03-27

与当前项目最相关的信号：

- agent runtime 被进一步拆成可组合部件
- shared `AgentRunner` 被抽出
- lifecycle hooks 统一
- subagent 失败时仍保留进度
- provider 层去掉 `litellm`，改用原生 SDK
- end-to-end streaming 更完整
- 多实例与运行时隔离继续增强

对 `ParrotCarriers` 的启发：

- 后台 worker 可以设计成可组合运行时
- 子任务失败时也应有可回收结果或进度
- 模块拆分时要优先考虑运行时边界，而不是先堆产品功能

### `v0.1.4.post5` - 2026-03-16

与当前项目最相关的信号：

- async background memory consolidation
- channel/plugin 架构继续解耦
- workspace guard 与 Windows 兼容性增强
- `--config` / `--workspace` 多实例模式更加清晰

对 `ParrotCarriers` 的启发：

- 后台任务和状态压缩适合异步化
- 多实例路径和运行时隔离是正式能力，不只是临时技巧

### `v0.1.4.post4` - 2026-03-08

与当前项目最相关的信号：

- 多实例支持成熟
- `--config` 与 `--workspace` 形成稳定模式
- MCP 更稳
- cron 更稳
- 安全默认更严格

对 `ParrotCarriers` 的启发：

- 后续若拆多个 worker，需要从一开始考虑配置、状态、端口隔离
- 外部工具接入应明确安全边界与超时边界

## 总结

如果只抓一条主线，`nanobot` 最近几版最值得借鉴的并不是渠道增多，而是：

1. runtime 拆分
2. subagent / background task
3. multiple instances
4. memory / heartbeat / cron
5. 安全与失败恢复
