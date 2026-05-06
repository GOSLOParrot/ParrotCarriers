---
status: skeleton
category: interface-overview
last_reviewed: 2026-05-07
ai_priority: high
ai_audience: both
---

# Chat 4 接口提炼工作区 — README

> ParrotCarriers 接口提炼成果 single-source-of-truth 工作区。
>
> 本目录回答：「这个项目里到底有哪些接口？谁是 producer？谁是 consumer？哪些 locked / evolving / proposed？怎么扩展？」

---

## 目录树速览

```
.cursor/memory/interfaces/
├── INDEX.md                       # 单一真源入口（先读）
├── README.md                      # 顶层导览（你正在读）
├── methodology.md                 # 方法论原则（不反推代码！driver 优先）
├── TODO.md                        # 主时间线（接口章节作主时间轴）
│
├── needs_inventory.md             # Stage 1 — 需求清单（4-B-req）
├── app_flow_inventory.md          # Stage 1 — App 流程清单（4-B-req）
├── capabilities_inventory.md      # Stage 2 — 能力四态表（4-B-cap）
│
├── wire/                          # Stage 3 — 跨语言接口
├── cross_process/                 # Stage 3 — Castle 边界外
├── in_process/                    # Stage 3 — Brain Python 内
├── capability/                    # Stage 2 末段 — 能力层副维度
│
├── upgrade_roadmap.md             # Stage 4 — 缺口 + 漂移 + upgrade plan
├── deprecation.md                 # 接口废弃流程
├── extension_points.md            # 第三方扩展占位
├── schema_evolution.md            # schema_version 演进
├── change_impact_table.md         # 变更影响表
│
└── _sync/                         # sub-chat 同步报告 + grep 验证
```

---

## 关键阅读顺序

1. [`methodology.md`](methodology.md) — **必读**，方法论原则（driver 优先 + 不反推代码）
2. [`INDEX.md`](INDEX.md) — 全局接口索引
3. [`TODO.md`](TODO.md) — 主时间线（当前进度 + 下一步）
4. 按主题进入：`needs_inventory.md` / `app_flow_inventory.md` → `capabilities_inventory.md` → 各拓扑边界子目录
5. 完成判据：`../architecture/interface_extraction_plan_20260507.md` §8

---

## 设计原则速记

| 原则 | 一句话 |
|:--|:--|
| **driver 优先** | 拓扑边界（分类）+ App 流程 + 需求 + 能力（内容）→ 接口（derived）|
| **不反推代码** | 既有代码 = 参考 / 升级起点 / 验证锚点；不允许"代码这样写所以接口这样" |
| **0 漂移守 Phase 4 §8** | 13 决策锁 / cs_parity 4/4 / ADR-L1.5-001 §4.1 三触发器 |
| **subdir 隔离** | 每 sub-chat 仅写自己拓扑层子目录；INDEX 由主 chat merge |
| **frontmatter 9 字段强制** | `driven_by` / `upgrade_from` / `producer` / `consumer` / `freeze_test` 等强制填 |
| **status 5 态** | `locked` / `evolving` / `experimental` / `proposed-upgrade` / `proposed-new` |

---

## 与项目其他工作区关系

| 工作区 | 关系 |
|:--|:--|
| `.cursor/memory/architecture/` | 接口提炼**输入**（ADR / decision-locks / completion-reports / 协议设计稿）|
| `.cursor/memory/architecture/dsg/` | DSG 设计 chat 工作区（接口提炼读 DSG 7 协议作输入）|
| `.cursor/memory/lore/ideas.md` | 灵感来源（人类手写，AI 只读）|
| `.cursor/skills/` | 外部技术能力（接口提炼引用 skill 但不在这里维护）|
| `src/parrot/` 源码 | **验证锚点**（不反推） |
| `unity/ArSpike/Assets/Scripts/ParrotApp/` | C# wire mirror（cs_parity 守）|

---

## 父引用

- 规划稿：[`../architecture/interface_extraction_plan_20260507.md`](../architecture/interface_extraction_plan_20260507.md)
- launch prompt：[`../architecture/chat4_interface_refinement_launch_prompt_20260507.md`](../architecture/chat4_interface_refinement_launch_prompt_20260507.md)
- ADR：[`../architecture/adr_protocol_upgrade_and_interface_refinement_background_20260504.md`](../architecture/adr_protocol_upgrade_and_interface_refinement_background_20260504.md)
- 跨 chat 待办登记：[`../architecture/cross_chat_pending_registry_20260507.md`](../architecture/cross_chat_pending_registry_20260507.md)
