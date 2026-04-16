# nanobot 文件结构摘要

## 关键目录

```text
nanobot/
├── agent/        # 核心 agent runtime
├── bus/          # 消息路由
├── channels/     # 外部渠道适配
├── cli/          # 命令行入口
├── config/       # 配置与路径解析
├── cron/         # 定时任务
├── heartbeat/    # 周期唤醒
├── providers/    # LLM provider
├── session/      # 会话管理
├── skills/       # skill loader / builtin skills
└── tools/        # tools 与 spawn / shell / filesystem / mcp / web
```

## 与 ParrotCarriers 最相关的模块

### `agent/`

关注这些能力：

- `loop.py`
- `runner.py`
- `subagent.py`
- `memory.py`
- `skills.py`

这些文件反映了：

- agent 主循环
- 子任务执行
- memory consolidation
- skill 加载和任务组织

### `bus/`

虽然上游 `bus` 与当前项目不是同一语义层，但它能提供：

- 任务路由
- 事件转发
- 结果回流

这对未来 `Dispatcher -> nanobot-worker` 的异步协作方式有借鉴意义。

### `cron/` 与 `heartbeat/`

这两个目录适合用来研究：

- 周期性任务触发
- 主动唤醒边界
- 后台低频维护任务

### `config/`

可借鉴：

- 多实例配置
- workspace 隔离
- runtime 数据隔离

### `tools/`

可借鉴：

- 工具注册
- shell / filesystem 安全边界
- MCP 工具接入

## 当前项目建议阅读顺序

1. `agent/`
2. `config/`
3. `cron/` + `heartbeat/`
4. `bus/`
5. `tools/`

## 当前不优先阅读

- 大量聊天渠道实现细节
- 各渠道平台权限与接入配置
- 完整个人助手产品化功能
