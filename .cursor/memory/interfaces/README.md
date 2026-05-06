---
status: ratified-salvage
category: working-notes
status_note: "Chat 4 接口提炼任务 pivot 后保留的 4 件高价值文件。其余 44 件（wire / cross / in / capability / inventory / sync / 元接口 / INDEX / README / TODO 等）已删除——它们基本上是已有 doc 的 reorganization 而非新价值。"
last_reviewed: 2026-05-07
parent_doc: "../INDEX.md"
ai_priority: medium
ai_audience: both
---

# Interfaces 工作区 — Pivot 后保留区

> **Pivot 说明（2026-05-07）**：Chat 4 "接口提炼"任务最初产出 49 文件，但绝大多数是把已有协议 / 完成报告 / behavior_rules / DSG 协议等内容 reorganize 成"接口面"视角——**没有产生新价值**，反而让 INDEX 冗余。User 决定止损，转向**直接推进 App 实施**，让接口在实施中自然浮现。
>
> **保留 4 件**因为它们在已有 doc 之外有独立价值；其余 44 件已删除。
>
> **正式 SSOT 收口**：
> - 架构图 → [`../architecture/module_map_p4_snapshot.md`](../architecture/module_map_p4_snapshot.md)
> - 协议全集 → [`../protocol_snapshot_p4.md`](../protocol_snapshot_p4.md)

---

## §1 保留的 4 件 + 1 sync

| 文件 | 价值 | 何时用 |
|:--|:--|:--|
| [`methodology.md`](methodology.md) | "不反推代码 + driver 优先 + status 5 态"通用编码原则 | 任何写设计 doc / 接口 spec 时 |
| [`upgrade_roadmap.md`](upgrade_roadmap.md) | 18 项整合 backlog（5 high + 8 mid + 5 low），与 cross-chat-registry 对账 | 推下游 chat 时 |
| [`change_impact_table.md`](change_impact_table.md) | "改 X 影响 Y"通用 reference table | 改协议 / wire / enum 前回查 |
| [`_sync/grep_verification_20260507.md`](_sync/grep_verification_20260507.md) | 真审计发现：13 attach helpers vs 5 doc / 命名漂（AttentionDecayStrategy vs AttentionDecayPolicy）| 引用为 audit 证据 |

---

## §2 已删除的 44 件（不可恢复，git 可追）

按目录：

| 目录 / 类型 | 数 | 删除理由 |
|:--|:--:|:--|
| `wire/*.md` | 9 | reorganize Phase 4 §8 + completion 报告 — 已在 protocol_snapshot_p4 收口 |
| `cross_process/*.md` | 6 | reorganize bus_v4 + protocol_snapshot_p1 — 同上 |
| `in_process/*.md` | 10 | reorganize completion 报告 — 同上 |
| `capability/*.md` | 7 | reorganize behavior_rules + parrot_actions enums — 已在 protocol_snapshot_p4 收口 |
| `needs_inventory.md` + `app_flow_inventory.md` | 2 | reorganize requirements.md + ar_app_flow_ui_design.md |
| `capabilities_inventory.md` | 1 | reorganize 已有 + 6 场景模拟（场景成 app 实施时的天然 test case，不需独立 doc）|
| `deprecation.md` + `extension_points.md` + `schema_evolution.md` | 3 | template-only，价值低 |
| `INDEX.md` + `README.md` + `TODO.md` | 3 | pivot 后无意义 |
| `_sync/4-B-{req,cap,wire}_completion.md` + `interface_extraction_completion_20260507.md` | 4 | sync 历史，无 forward 价值 |
| **总** | **44** | |

---

## §3 Pivot 后下一步

User 直接进入 **app 实施**。接口在实施中自然浮现：

- 写代码时遇到的具体接口问题，**就地修**（修代码 + 同步 protocol_snapshot_p4 §x 章节）
- 不再追求"先写接口 doc 再写代码"
- methodology.md §2 的"不反推代码"原则**仍然适用**（不要看 X 已经怎么写的就锁成正式接口；问"为什么这样设计"）

---

## §4 关联

- 父 INDEX：[`../INDEX.md`](../INDEX.md)
- Pivot 后正式 SSOT：[`../architecture/module_map_p4_snapshot.md`](../architecture/module_map_p4_snapshot.md) + [`../protocol_snapshot_p4.md`](../protocol_snapshot_p4.md)
- 上游规划稿（标 superseded）：[`../architecture/interface_extraction_plan_20260507.md`](../architecture/interface_extraction_plan_20260507.md)
- 跨 chat 待办登记表：[`../architecture/cross_chat_pending_registry_20260507.md`](../architecture/cross_chat_pending_registry_20260507.md)
