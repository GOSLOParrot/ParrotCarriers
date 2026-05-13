---
status: ratified
category: workspace-coordination
status_note: "Cursor 主工作区 vs Codex + Unity MCP 第二前端工作区的分工建议。**单人项目，无硬边界**——两侧都可读写整个仓库；只在改核心接口 / 协议字段 / 锁定决策时要求说明理由。本文 2026-05-09 由原硬边界版改写。"
last_reviewed: 2026-05-09
ai_priority: high
ai_audience: "Cursor + Codex 两侧 chat；任一侧动手前必读"
parent_doc: "../INDEX.md"
related:
  - "../../.cursor/rules/workspace.mdc (全局路由 alwaysApply)"
  - "ar_workspace_index.md (AR 工作区聚合)"
  - "Interface/INDEX.md (接口分类骨架)"
  - "protocol_snapshot_p4.md (协议 SSOT)"
  - "../commit_guidelines.md (提交规范 + 漂移说明子句)"
---

# 第二前端工作区分工建议（Cursor vs Codex + Unity MCP）

> **背景**：user 同时使用 Cursor 与 Codex IDE（带 Unity MCP 插件）作为两个 LLM 工作区。两个工作区**共享同一仓库**（`D:/GOSLOParrot/ParrotCarriers`）+ 同一 SSOT（`.cursor/memory/INDEX.md`）。
> **现实**：本项目是**单人开发**。前端 / 后端 / 协议 / Unity / 文档全部一人维护。两个工作区不是两个团队，是同一个人在两台 IDE 之间切换。
> **本文用途**：给"哪种活在哪个工作区做更顺手"提建议；给"改核心接口 / 协议字段时要做什么"立硬规则。**不强制**任何"必须先在 Cursor / 必须先在 Codex"的流程。

---

## §1 总原则（2 条硬规则 + 其余皆建议）

### 硬规则 H1：改核心接口 / 协议字段 / 决策锁须说明理由

任一工作区改下列对象时，必须在**提交信息（commit message）或代码注释**里写一句"为什么"，并按需更新对应文档：

| 改动对象 | 必须做的事 |
|:--|:--|
| `src/parrot/**` 公开导出（class/function 签名、enum 项、公共字段） | commit msg 写一行理由；如改公开 API，更新 `Interface/INDEX.md §1` 对应条目 |
| `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/**` DTO 字段 | commit msg 写理由；如属新增协议字段，在 `protocol_snapshot_p4.md` cs_parity 表加 1 行 |
| `protocol_snapshot_p4.md` / `bus_v4.md` / `sprint4_protocol_v2_ecp.md` | commit msg 写理由；同步检查 Python + C# 两侧实现是否对齐（cs_parity） |
| `NodeKind` / `EdgeKind` / `EcpEventType` / `EcpEventSource` / topic 常量 | commit msg 写理由 + 引用对应 ADR；如越过 Phase 4 §8 锁，先开 ADR chat |
| Phase 4 §8 13 决策锁 / ADR-L1.5-001 11 项 | commit msg 引用 ADR；新决策须新 ADR |
| `commit_guidelines.md` "重大漂移说明子句" 触发条件 | 按 `commit_guidelines.md` 漂移子句格式写 |

> "理由" 不必长——一句话足够。例：`feat(ecp): + EcpEvent.audio_fade — Codex/Unity 端 lifecycle 切场景需要听觉提示，配合 §3.2 lifecycle 升级`。

### 硬规则 H2：SSOT 写入要登记

`.cursor/memory/INDEX.md` 是唯一真相源。任一工作区**新增** memory 文档（`architecture/**` 顶层文件）时，必须在 INDEX.md §1.1 加一行（路径 + 一句话作用）。改动既有文档不必登记。

### 其余条款 = 建议，不强制

下面 §2 / §3 是"在哪个工作区做更顺手"的建议，**不是硬约束**。Codex 可以自由读写整个仓库，包括 `src/parrot/**` 后端、协议文档、Skills；只要符合 H1 / H2 即可。

---

## §2 分工建议（默认偏好）

### §2.1 Cursor 工作区偏好场景

- 大段 Python 改动 + pytest 跑测（pytest skill stack 在这边）
- DSG / Brain / Scheduler 后端协议设计 + ADR 起草
- `.cursor/memory/architecture/**` 大块文档重写
- skill / rule 维护
- 长链跨模块 grep / 多文件 refactor

### §2.2 Codex + Unity MCP 工作区偏好场景

- Unity Editor 内的 Scene wiring / Prefab 配置（MCP 直接看）
- C# DTO + RoomManager + ParrotController + 视频 / RPC handler 改动（IDE 内编译反馈快）
- Figma 资产导入 + UI 资产摆放 + 像素画落 `unity/ArSpike/Assets/UI/**`
- Unity 端真机 / Editor smoke 调试

### §2.3 两边都顺手

- AR 业务设计文档（既动 C# 又看后端协议）
- Obsidian / Google 日程真连接业务（既动 ingest filter / trigger 又可能动 Unity 提示 UI）
- Web 控制台原型（如果走 Unity WebGL 或 Tauri；纯后端 API 设计偏 Cursor）
- `cross_chat_pending_registry_20260507.md` 待办登记 / close

---

## §3 共享资源 + 自主探索

### §3.1 共享 SSOT（两边都读）

- `.cursor/memory/INDEX.md`：路由真相源
- `.cursor/memory/architecture/protocol_snapshot_p4.md`：协议 SSOT
- `.cursor/memory/architecture/Interface/INDEX.md`：接口分类骨架
- `.cursor/memory/architecture/user_ideas_and_backend_capability_brief_20260509.md`：用户 idea + 后端能力 + 三大真连接现状
- `.cursor/memory/architecture/cross_chat_pending_registry_20260507.md`：跨 chat 待办（双向写）
- `.cursor/memory/lore/ideas.md`：user 自管设计灵感（AI **只读**，从不改）

### §3.2 Codex 自主探索

Codex 启动新任务时**不需要等 Cursor 喂资料**。建议自检流程：

1. 读 `.cursor/memory/INDEX.md` 找入口
2. 读 `architecture/user_ideas_and_backend_capability_brief_20260509.md` 摸 user 当前意图
3. 按任务相关性回查 `Interface/INDEX.md` / `dsg/workspace_index.md` / `ar_workspace_index.md`
4. 按需读 `.cursor/skills/**`（AR Foundation / LiveKit Unity / Graphiti / DSG / py-trees / nanobot 等）
5. `rg` 关键字摸源码现状

### §3.3 跨工作区协调（可选 / 异步）

不强制走 registry。需要异步交接时可写 `cross_chat_pending_registry_20260507.md` 加一行（自由格式即可），方便另一侧 IDE 下次启动时看到。

---

## §4 反模式（仍然禁止）

- ❌ 改 `src/parrot/**` 公开签名 / 协议字段 / Phase 4 §8 锁，**不写理由 commit msg**（违反 H1）
- ❌ 在 `.cursor/memory/lore/ideas.md` 写任何东西（user 自管区）
- ❌ 让 LLM 自动改 `.cursor/memory/INDEX.md` 的"四轴速查 / 关键约束"未经 user 确认
- ❌ 凭空生造协议字段 / enum 项**不引用任何 ADR / 不写理由**（之前 BigIssue.md 协议污染复盘的根因）
- ❌ 不通过 `Interface/INDEX.md §2` 4 字段业务模板就贴大量代码声称是"业务接口"（v0 教训）

---

## §5 验收信号

- 两侧 chat 启动前都能从 INDEX.md §〇 找到本文
- `.cursor/rules/workspace.mdc` §10 含本文链接
- 改协议 / 核心接口的 commit 都能 grep 到一句以上"理由"
- `cross_chat_pending_registry` 不再出现强制性的 `[必须先 Cursor]` / `[必须先 Codex]` 标签——只剩可选异步登记

---

## §6 历史

- 2026-05-09 初版：硬边界版（"Codex 不能产生新协议字段"）
- 2026-05-09 当日修订：改为软分工建议 + 2 条硬规则。原因：单人开发现实，硬边界拖慢同一人在两 IDE 之间切换的实际工作流；改协议须注明理由是更朴素也更可执行的纪律。

