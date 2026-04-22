---
status: ratified
status_note: "ADR 目录的入口约定, 稳定"
last_reviewed: 2026-04-22
---

# ADR — Architecture Decision Records

> 源: `sprint0_preflight.md §3.3`
> 定位: **结论类架构决策 + 原因 + 备选方案**的档案, 不复述愿景文档 (`ar_feature_vision.md` / `system_core.md`) 内容。
> ADR 是**事后复盘**, 用来回答"我们 X 时为什么选 Y 而不是 Z"。

---

## 编号规则

- 文件名: `ADR-{三位数}-{kebab-case-标题}.md`
- 示例: `ADR-001-py-trees-blackboard.md`
- 编号**一次性分配, 永不复用**, 即使被 supersede 编号也保留

## 状态 (frontmatter `status`)

| 状态 | 含义 |
|:-----|:-----|
| `proposed` | 提出中, 未决 |
| `accepted` | 已接受 (当前默认) |
| `rejected` | 考虑过但未采纳 (保留记录) |
| `superseded` | 被后续 ADR 替代 (必须 `superseded_by: ADR-xxx`) |
| `deprecated` | 不再适用, 但没新 ADR 替代 |

## 触发写 ADR 的时机

**一定要写**:
1. 选择一个**跨多个模块**的技术栈 (例: py-trees 而非 BehaviorTree.CPP)
2. 拒绝一个**听起来合理的方案** (例: 不用 Neo4j 用 FalkorDB)
3. 立一个**反直觉约束** (例: L2-B 禁止回写 L0)
4. 一个设计**被验证坏**决定改 (supersede 旧 ADR)

**不需要写**:
- 纯代码风格 / 命名约定 (走 `.mdc` 规则)
- 一次性 bug 修复
- 不会影响其他模块的局部决策

---

## 目录索引

| ID | 标题 | 状态 | 记 |
|:---|:-----|:-----|:---|
| ADR-001 | [py-trees as Blackboard / BT 核心](./ADR-001-py-trees-blackboard.md) | accepted | 替代 BehaviorTree.CPP / 自建 BT |
| ADR-002 | [VideoTier × DsgMode 正交分离](./ADR-002-video-tier-dsg-mode-orthogonal.md) | accepted | 算力档位 vs 玩法模式独立演进 |
| ADR-003 | [三层意识 (Reflex/Intent/Task) 调度分治](./ADR-003-three-layer-consciousness.md) | accepted | Reflex/Intent 不通知 Gemini |

---

## 模板

见 [`adr_template.md`](./adr_template.md)。每次新写 ADR 复制一份, 改编号 + 标题, 逐节填。
