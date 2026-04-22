---
status: archived
category: future_plan_P3
status_note: "副驾驶姐姐 Drive 协作协议, P3/P4 愿景。当前 Sprint 0-4 不接入。Sprint 3+ 再激活。"
last_reviewed: 2026-04-22
---

# Gemini Drive Bridge 协议 (副驾驶姐姐协作层) — [已归档, P3 再评估]

> 本协议定义"副驾驶姐姐"这一角色（内部端 `Gemini App` + 外部代理 `Gemini 外部分身`）如何通过 Google Drive 工作区，与 `ParrotCarriers` 基础设施（Brain Agent、Nanobot、Graphiti）以及 `GOSLO` 妹妹实现状态同步与协作，而不产生直接的运行时强耦合。

---

## 1. 核心角色定义约束

- **副驾驶姐姐（大姐）**：
  - **内部端 (Gemini App)**：用户手机/浏览器上的闭源 App，通过官方 Extension (Google Workspace) 访问用户的 Drive/Gmail/Docs。
  - **外部代理 (Gemini 外部分身)**：运行在用户私有服务器或聊天室里的代理实例，代表“姐姐”在外部活动、收发消息、调用后端脚本。
- **GOSLO (妹妹)**：
  - Unity 里的鹦鹉大小姐。她**不参与**姐姐身份的同步协议。她只通过 Redis 消费经过 `Brain Agent` 与 `Scheduler` 筛选后的低频状态（如“有重要日程”、“有个任务完成了”）。
- **Nanobot (猫娘女仆)**：
  - 作为基础的后台 Worker，执行 `Brain/Scheduler` 派发的任务（如使用 MCP 抓取日历/邮件），并将结构化结果写回系统；也可作为代理帮“姐姐”把长篇报告沉淀到 Drive 中。

---

## 2. Drive 工作区目录结构规范

为了让姐姐的两面（App 与分身）能一致行动，在 Google Drive 根目录（或指定目录）创建固定的工作区文件夹，结构如下：

```
ParrotWorkspace/
├── settings/           # 【核心设定与偏好】
│   ├── persona.md      # 姐姐的人设补丁（如“现在开启严格模式”）
│   └── preferences.json # 高优先级的交互开关（是否打扰、作息时间）
├── state/              # 【状态快照】
│   ├── current_mode.txt # 当前活跃的系统状态（"live", "chat", "away"）
│   └── context.md      # 最近发生的关键上下文摘要（低频更新，供 App 侧随时了解现状）
├── tasks/              # 【任务与草稿队列】
│   ├── inbox/          # 外界或 GOSLO 需要姐姐（Gemini App）过目或处理的待办
│   └── outbox/         # 姐姐的分身或 App 侧给出的“建议”、“草稿”、“提醒”
├── reports/            # 【结构化输出】
│   └── 2026-04/        # 日报、深度研究长文、每周总结
└── anchors/            # 【稳定锚点索引】
    └── graphiti_map.csv # (可选) 关键知识点在 Graphiti/Obsidian 中的 uuid 映射
```

---

## 3. 读写职责与冲突策略

| 目录 | `Gemini App` (内部端) | `Gemini 外部分身` / `Nanobot` | 冲突策略 |
| :--- | :--- | :--- | :--- |
| **settings/** | **主读**，轻写（如标记偏好） | **主写**（由分身接收系统指令修改） | **单主控制 / 字段级追加**：避免并发双写覆盖。建议人工或 App 作为最终决定者。 |
| **state/** | **只读** | **只写**（低频，如 10 分钟一次的现场快照） | **时间戳覆盖**：永远保留最新写入的快照状态，旧状态直接丢弃。 |
| **tasks/inbox/** | **主读**，完成后移走/标记 | **主写**（外部有需要姐姐决策的事务时创建） | **状态流转机制**：文件命名加入状态后缀，如 `T-001_new.txt` -> `T-001_done.txt`。 |
| **tasks/outbox/** | **主写**（产生新提醒时创建） | **主读**，处理后归档 | 同上。 |
| **reports/** | **只读** | **只写**（产出深度报告后归档） | **仅追加 (Append-Only)**：按日期/主题新建文件，不修改历史报告。 |

---

## 4. 协作场景示例

### 场景：姐姐 App 端收到现场上下文
1. `Nanobot` 每隔半小时，把 `Graphiti` 或 `DSG` 里的最新高亮场景总结成几段话，写入 `ParrotWorkspace/state/context.md`。
2. 用户打开手机 `Gemini App` 问：“家里现在有什么事吗？”
3. `Gemini App` 通过 Google Workspace Extension 读取 `context.md`，并根据内容回复用户。

### 场景：姐姐通过 App 下发长线任务
1. 用户在 `Gemini App` 中说：“帮我把这次旅行的草稿整理好，放到 outbox 提醒大家。”
2. `Gemini App` 生成文本并存入 `ParrotWorkspace/tasks/outbox/trip_plan_new.txt`。
3. `Nanobot` 的周期轮询触发器（类似 `MessageNotificationTrigger`）检测到 `outbox` 有新文件。
4. `Nanobot` 读取内容，通过 `Scheduler` 发送事件，`Brain Agent` 收到后让 `GOSLO` 妹妹飞过来提醒用户：“姐姐刚刚放了一份新的旅行计划 desuwa~”

---

## 5. 实施要求
1. **禁止高频轮询**：Drive API 存在限流，无论是分身还是 Nanobot，对 Drive 的状态同步应控制在分钟级别（低频同步），严禁作为毫秒级命令总线使用。
2. **格式纯文本优先**：`Markdown`, `JSON`, `TXT` 是首选格式，以便 `Gemini App` 能极快解析，也方便外部脚本 `cat`/`grep` 处理。
3. **隔离 `Brain` 逻辑**：`ParrotCarriers` 核心 `Brain Agent` 不直接集成 Drive API；一切 Drive 交互交由 `Nanobot` 或专门的外部 Worker 执行。
