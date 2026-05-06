---
status: stage-1-completion
category: chat-4-sync-report
chat_4_stage: "Stage 1 — 4-B-req"
status_note: "Chat 4 Stage 1 (4-B-req) sync report — needs_inventory + app_flow_inventory 完成；user 倒查方法论合规 + 清单完整后 sign off → Stage 2 (4-B-cap) 启动。"
last_reviewed: 2026-05-07
parent_doc: "../INDEX.md"
ai_priority: high
ai_audience: both
---

# Stage 1 Sync Report — 4-B-req（在主 chat 跑）

> **本文用途**：Stage 1 收口报告。等 user 倒查 → sign off → Stage 2 启动。

---

## §0 TL;DR

| 维度 | 状态 |
|:--|:--|
| 落地文件数 | 2（`needs_inventory.md` + `app_flow_inventory.md`）|
| 覆盖需求总数 | 93（67 functional + 12 NEED-* + 14 隐式）|
| Chat 4 接口面候选数 | ~55 |
| Out-of-scope 数 | ~38 |
| 方法论合规 | ✅（0 引用代码符号；100% cite doc anchor） |
| Phase 4 §8 13 锁 0 漂移 | ✅（仅 inventory，不动锁定值） |
| 测试基线 | 不动（415/415 全绿不变） |

---

## §1 落地文件清单

| 文件 | 路径 | 行数 | 章节 |
|:--|:--|:--:|:--|
| needs_inventory | `.cursor/memory/interfaces/needs_inventory.md` | ~280 | §1 67 项 / §2 12 NEED-* / §3 14 隐式 / §4 范围确认 / §5 全表统计 |
| app_flow_inventory | `.cursor/memory/interfaces/app_flow_inventory.md` | ~360 | §1-§7 8 步逐步 / §8 跨步全局议题 / §9 Stage 2 输入清单 |

---

## §2 方法论合规检查（user 必查）

### §2.1 driven_by 是否 cite doc anchor 而非 code 符号

| 文件 | 检查项 | 状态 |
|:--|:--|:--|
| needs_inventory §1 67 项 | "真源" 列全部 cite `requirements.md` / `cross_chat_pending_registry §X.Y` / `goslo_modularization_residual_debt §X` | ✅ |
| needs_inventory §2 12 NEED-* | 同上 + cite Phase 4 完成报告章节 | ✅ |
| needs_inventory §3 14 隐式 | 全部 cite `ar_app_flow_ui_design §X` / `ar_feature_vision §X` / `parrot_behavior_rules §X` | ✅ |
| app_flow_inventory §1-§7 各 §x.5 driven_by | 全部 cite `ar_app_flow §4 step N` / `ar_feature_vision §X` / Phase 4 §8 §8.X | ✅ |
| app_flow_inventory §1-§7 §x.2 capability candidates | 引"NEED-XX" / "C9 手势反射" 等 doc 符号；**0 引** `attach_*` / `class XYZ` 等 code 符号 | ✅ |

### §2.2 既有代码作为参考的引用边界

| 项 | 说明 |
|:--|:--|
| **已 ratified 的能力**（如 LineB 双管线 / DSG 协议 v1）| 在 inventory 标 "✅ ratified（来源 doc）"，**不打开代码** |
| **Phase 4 临时实现**（FocusBboxThreshold / selection-C / IngestRunner factory）| 显式标 `experimental`（needs_inventory §6 给 Stage 2 提示）|
| **既有 brain tools**（10 个）| 仅 cite 名字 + Phase 标 + cross-chat-registry 缺口；**不解读实现** |
| **Phase 4 §8 13 锁** | 全部标 `✅ locked`，**0 修改任何锁定值** |

### §2.3 status 5 态的应用一致性

| status | 在哪用 | 数量 |
|:--|:--|:--|
| `inventory-only` | needs §1 functional 已落地 | 39 |
| `proposed-upgrade` | needs §1 / §2 / §3 既有需升级 | ~15 |
| `proposed-new` | needs §1 / §2 / §3 应有但缺 | ~9 |
| `out-of-scope` | needs §1 / §2 / §3 推其他 chat | ~38 |

---

## §3 Stage 2 (4-B-cap) 输入就位

Stage 2 拿到的输入：

1. **needs_inventory.md** — 93 需求 → 反推能力
2. **app_flow_inventory.md** — 55 capability candidates 已初步识别
3. **§9（app_flow_inventory）能力四态判定指引**
4. **§6（needs_inventory）四态判定提示** — Phase 4 临时实现必须标 experimental

Stage 2 待产出：

- `capabilities_inventory.md`（能力四态表）
- `capability/` 子目录 7 文件（brain_tools / parrot_actions / triggers / ref_kinds / bucket_kinds / staged_ref_kinds / model_manifest）

---

## §4 user 倒查清单（sign off gate）

### §4.1 完整性（user 必查）

请 user 倒查：

- [ ] **需求清单是否完整**：97 需求 + Chat 4 范围 ~55 是否够？有没有 user 想到但 inventory 没列的需求？
- [ ] **隐式需求是否齐**：§3.1-§3.5（启动菜单 / HUD / 工具柜 / 注意力工具 8 问 / vision 4 核心 / 行为契约红线）是否覆盖 user 期望？
- [ ] **App Flow 是否齐**：8 步 + 3 跨步议题（4 类块预设链 / Pause-Resume / 摄像头遮挡）是否还有遗漏的步骤？
- [ ] **Out-of-scope 是否合理**：38 项推其他 chat 是否全部接受？有没有 user 想纳入 Chat 4 但被推走的？

### §4.2 方法论合规（user 必查）

- [ ] **没有反推代码**：随机抽 5 条接口候选，看其 driven_by 是 NEED-XX / app-flow:step-N 还是 code 符号？
- [ ] **既有代码引用边界**：是否有"代码这样写所以接口这样"的痕迹？
- [ ] **Phase 4 临时实现是否标 experimental**：FocusBboxThreshold / selection-C / IngestRunner factory / identify_object 1.9s 是否被识别为 experimental？

### §4.3 §10 待答问题对 inventory 的影响

inventory 已基于以下推荐答案 draft（Q5 仅接口相关 / Q1 取 capability-gating），如果 user 改变答案，需要补充：

- [ ] **Q5 67 全检 vs 仅接口相关**：当前采"仅接口相关子集"——D2-D5 视觉管线 / F4-F6 nanobot 高级 等被标 out-of-scope。如果 user 选 67 全检，需要扩展这些项的 inventory。
- [ ] **Q1 capability-gating 是否纳入 Chat 4**：当前标"⚠️ §10 Q1 待答"，inventory 已留位置。若 user 选取，4-A 实施轨多 5-15 行；若 user 选舍，标 out-of-scope（推 P3）。

---

## §5 给主 chat / Stage 2 chat 的下一步指引

### §5.1 user sign off 后

- [ ] 主 chat 把 needs_inventory + app_flow_inventory 两份文件 commit（commit 1）
- [ ] 启动 Stage 2（4-B-cap）：
  - 选项 A：在主 chat 跑（继续，token 热）
  - 选项 B：fork 4-B-cap sub-chat（按 §7.5.7 入场 prompt）
- [ ] 同时启动 4-A 实施轨（独立，与 B 轨并行）
- [ ] 4-C 框架定型（与 Stage 3 4-B-wire 同启动；Stage 2 进行中可先 spike 1 个 freeze test 模板）

### §5.2 if user 让我修订

- [ ] 主 chat 收 user 反馈 → 直接 StrReplace needs / app_flow inventory 对应章节
- [ ] 标 `last_reviewed` 更新日期 + §11 变更日志加 amendment 记录
- [ ] 重 sync 后再 sign off

---

## §6 引用

- INDEX：[`../INDEX.md`](../INDEX.md)
- 待 sign off 的两份文件：[`../needs_inventory.md`](../needs_inventory.md) + [`../app_flow_inventory.md`](../app_flow_inventory.md)
- methodology：[`../methodology.md`](../methodology.md)
- 父规划稿：[`../../architecture/interface_extraction_plan_20260507.md`](../../architecture/interface_extraction_plan_20260507.md)
- TODO：[`../TODO.md`](../TODO.md)
