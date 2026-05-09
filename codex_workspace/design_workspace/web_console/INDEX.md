# Web 控制台设计区

> 当前不抢跑完整 Web。Web 控制台先作为后端可视化 / 调试 / 管理能力候选池，等 App 设计清楚后再反推页面。

## 现在的定位

- Read-only 优先。
- 先模仿 App 的流程，看哪些后端状态需要被监控。
- 不替代 Obsidian 文件管理，也不替代 Google Calendar Web 管理。

## 未来可监控内容

| 区域 | 可视化对象 |
|:--|:--|
| Bus | 模块注册、心跳、通道堵塞、LiveKit / Redis 状态。 |
| Brain | GOSLO 当前 persona / mode / scene / model、IntentWorkspace refs、最近工具调用。 |
| Scheduler | BT 当前路径、Nanobot dispatch、任务超时 / 结果。 |
| DSG | Buckets、RefTable、L2-B 节点 / 边、注意力分数、Timeline。 |
| Blackboard | Google 部分状态、session / task / tick 关键值。 |
| Nanobot | 正在干什么、最近结果、失败原因。 |

## 暂缓的内容

- 大型配置后台。
- 复杂写操作。
- 在 Web 里编辑 Obsidian 或 Google 原始内容。
- 在 App 第一版之前先定完整 Web 信息架构。

## 2026-05-09 草案

- `monitoring_demo_scope_20260509.md`：只读 smoke monitor 范围，用于验证连接层，不作为最终 Web 控制台设计。

## 2026-05-10 已落地 smoke monitor

- 实现：`src/parrot/brain/app_monitor_server.py`
- 启动：`src/scripts/start_app_monitor_server.py --host 127.0.0.1 --port 7892`
- 已验证区块：`Module Rail`、`Canvas Workspace`、`Paper Notes`、`L2-B Topology`
- 仍是 read-only 调试工具，不是正式控制台。
