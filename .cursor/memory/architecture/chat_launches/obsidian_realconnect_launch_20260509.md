---
status: tentative / chat-launch-prompt
category: chat-launch
status_note: "待开 chat 启动 prompt — 后端 ↔ Obsidian 真连接（Web 真连接显式 defer，user 原话：我们可以直接用 Obsidian）。Sub-Chat 启动后填本文件 §业务接口字段 A-D 并产出补丁。"
last_reviewed: 2026-05-09
ai_priority: low
ai_audience: "Obsidian 真连接 chat 启动者（启动前读完本文 + Interface/INDEX.md §0 §2）"
parent_doc: "../INDEX.md"
related:
  - "../Interface/INDEX.md (核心/业务二分骨架 + 4 字段业务模板)"
  - "../dsg/dsg_decisions_master.md §3.2 (Obsidian 3 子类决策)"
  - "../Interface/concept_dictionary_20260507.md (Obsidian 子类术语)"
  - "../Interface/legacy_issues_split_20260507.md (P2.5 NEED 标签)"
  - "../adr_l1_5_source_dispatch_extension_space_20260504.md (SemanticNode.source 边界)"
---

# Chat Launch — 后端 ↔ Obsidian 真连接

## §1 Scope

后端 ↔ Obsidian 真 ingest 三子类（Ref-加强 / 设定-日常 / 设定-Roleplay）；建立 user_tag_filter 真连接路径，从"USER_TAG_OBSIDIAN 单类粗暴接入"升级为"3 子类语义分流 + UUID 绑定 + Bucket / Graphiti 分区路由"。

**Web 真连接显式 defer**：user 原话"不一定需要，我们可以直接用 Obsidian"——Web 仅作只读控制台（见 `web_console_launch_20260509.md`），不做 Obsidian Web 写回。

## §2 输入（必读，≤ 3 份）

1. [`../Interface/INDEX.md`](../Interface/INDEX.md) — §0 失败教训 + §2 4 字段业务模板
2. [`../dsg/dsg_decisions_master.md`](../dsg/dsg_decisions_master.md) §3.2 — Obsidian 3 子类决策（已 ratified）
3. [`../adr_l1_5_source_dispatch_extension_space_20260504.md`](../adr_l1_5_source_dispatch_extension_space_20260504.md) — SemanticNode.source 字段边界 + Meta dict/factory hook

可选回读：[`../Interface/concept_dictionary_20260507.md`](../Interface/concept_dictionary_20260507.md) §Obsidian 子类、[`../dsg/source_x_lifecycle_status.md`](../dsg/source_x_lifecycle_status.md) §USER_TAG_OBSIDIAN 现状

## §3 锁（不可动）

- **不动** `protocol_snapshot_p4` 已锁的 Phase 4 §8 13 决策（除非明确升级 ECP 字段）
- **不动** `ADR-L1.5-001` 锁定的 SemanticNode.source 现有 enum
- Obsidian 3 子类边界以 `dsg_decisions_master §3.2` 为准；如发现需要新增第 4 子类，**必须先开子 chat 修订决策**
- **不写**新协议字段（如要新增 BucketKind / Graphiti group_id 等，先在 Cursor 走 protocol upgrade 流程）

## §4 不做（显式 defer）

- Obsidian Web 真连接 / Web 写回
- Obsidian 双向同步（仅 user → backend 单向 ingest）
- Roleplay 子类的 Persona / Mode / skin 三联耦合（独立 chat 处理）
- 多 Vault 支持（先单 Vault 跑通）

## §5 输出物

- [ ] 业务接口字段 A-D 表（按 [`../Interface/INDEX.md`](../Interface/INDEX.md) §2 模板填写，输出到本文件 §6）
- [ ] `src/parrot/dsg/ingest/user_tag_filter.py` 改造（3 子类分流逻辑）
- [ ] 1 份完成报告（实际改动 + 测试结果 + 漂移说明）+ `cross_chat_pending_registry` 更新（划掉对应 NEED）
- [ ] 若发现需要补核心接口（字段 C 非空）→ fork 子 chat 进 protocol upgrade，**不在本 chat 动协议**

## §6 业务接口字段 A-D（chat 启动后填）

> 请按 [`../Interface/INDEX.md`](../Interface/INDEX.md) §2 模板，填完才进入实施。

- **A 模块职责回读**：（待填，≤ 3 项）
- **B 用现有核心接口能否组合实现**：（待填，yes/no）
- **C 需要补哪些核心接口**（仅 B = no 时填）：（待填）
- **D 完成判据**（业务能跑通）：（待填，正向 + 失败 各一条）

## §7 启动指令

启动该 chat 时复制以下到首条消息：

```
请按 .cursor/memory/architecture/chat_launches/obsidian_realconnect_launch_20260509.md
执行 Obsidian 真连接 ingest 改造任务。

入场顺序：
1. 读本 launch prompt 全文 + §2 三份输入
2. 读 .cursor/memory/architecture/Interface/INDEX.md §0 §2 §5
3. 在本 launch prompt §6 填字段 A-D
4. 字段 D 经我确认后再动代码
5. 如字段 C 非空，先停下来 fork 子 chat 走 protocol upgrade
```
