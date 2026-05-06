---
status: ratified
category: methodology-principle
status_note: "Chat 4 接口提炼方法论原则。**禁止反推代码**；driver = 拓扑边界 + App 流程 + 需求 + 能力。每 sub-chat 入场必读，违反即 abort 重做。"
last_reviewed: 2026-05-07
authoritative_for: "Chat 4 接口提炼方法论 / sub-chat driver_by 字段强制语义 / status 五态语义 / 既有代码与协议的角色定义"
parent_doc: "INDEX.md"
parent_plan: "../architecture/interface_extraction_plan_20260507.md §7.5.0"
ai_priority: high
ai_audience: both
---

# Chat 4 接口提炼方法论原则

> **本文权威性**：所有 sub-chat（4-B-req / cap / wire / cross / in / 4-A 实施 / 4-C freeze test）入场必读；违反即 abort 重做。
>
> **核心立场**：当前 ParrotCarriers 代码状态 = "跑通分叉路的几条验证通路验证代码架构设计可行性"——**不是终态**。接口提炼的目的是**驱动既有代码 / 协议升级**到 user 期望的功能形态，而**不是把临时实现锁成正式接口**。

---

## §1 driver 优先级（核心方法论）

```
[1st driver: 拓扑边界]               ← 分类维度
                ↓ shape
[2nd driver: App 流程 + 需求 + 能力]  ← 内容来源
                ↓ derive
[3rd: 接口提炼]                       ← derived
                ↓ verify
[4th: 既有代码 grep 验证 + 协议 upgrade roadmap]
```

### §1.1 1st driver — 拓扑边界（已 lock）

主维度：`wire / cross_process / in_process / capability`

副维度：`audience: ai_only | human_only | both`

副副维度（frontmatter 字段）：`status` / `domain` / 角色 cross-link

详 [`../architecture/interface_extraction_plan_20260507.md §3.2`](../architecture/interface_extraction_plan_20260507.md)。

### §1.2 2nd driver — App 流程 + 需求 + 能力（内容来源）

| 来源 | 文件 | 写者 |
|:--|:--|:--|
| App 流程 | `../architecture/ar_app_flow_ui_design.md §4`（8 步：启动页 → 主菜单 → 配置 → 权限 → 加载 → 转场 → AR 主场景 → HUD/工具柜 → 工作区） | 4-B-req |
| 需求 | `../requirements.md` 67 项 + `../architecture/ar_feature_vision.md` + `../architecture/ar_app_plan.md`（仅追溯，不驱动） | 4-B-req |
| 能力 | 由 4-B-req 输出 → 4-B-cap 反推 | 4-B-cap |
| 行为契约（红线）| `../parrot_behavior_rules.md` §0.3 / §3.7 | 全员遵守 |

### §1.3 3rd: 接口（derived）

接口面**必须**能追到至少 1 个 driver（needs / app-flow / capability）；否则 frontmatter `driven_by:` 字段无法填写，无法通过 sync 检查。

### §1.4 4th: grep 验证（不是反推）

主 chat Stage 4 跑 grep 脚本，对每接口面：

| grep 结果 | 处置 |
|:--|:--|
| ✅ producer + consumer 实证齐 | 标 verified；接口可入 INDEX |
| ⚠️ doc 有，code 无 producer | 标 `proposed-new`，进 upgrade_roadmap |
| ⚠️ doc 有，code 有但实现缺 consumer | 标 `proposed-upgrade`，进 upgrade_roadmap |
| 🆕 grep 出代码符号但 doc 无 | **不是缺漏**——是**漂移**或**临时实现**；进 upgrade_roadmap 决定锁 / 升 / 删 |

---

## §2 既有代码与协议的角色（明确禁止反推）

| 角色 | 允许 | 禁止 |
|:--|:--|:--|
| **参考**（reference） | 看代码理解某个能力**已经怎么实现** | ❌ 拿代码符号当接口列表起点 |
| **升级起点**（upgrade-from） | 在 frontmatter `upgrade_from:` 标"我从哪里升级" | ❌ "代码这样写，所以接口就是这样" |
| **验证锚点**（verification） | 接口提炼完成后，反向 grep 验证 producer/consumer 实证 | ❌ "grep 出来的符号就是接口候选，缺的就漏了" |
| **填洞**（gap-fill） | 缺口反向追到代码哪里要补 | ❌ "代码已经这么干了，接口就这么定" |

### §2.1 为什么这条原则关键

当前代码状态 = "跑通分叉路几条验证通路"——很多临时实现是 Phase 4 §8 显式标注的 **临时**：

| 临时实现示例 | 显式标注位置 |
|:--|:--|
| `dsg/attention/threshold.py` `FocusBboxThreshold` | Phase 4 §8 §8.5 #3："文件头明写 'Phase 4 临时实现 — 非 L3'" |
| `dsg/attention/__init__.py` 不 export `Attention` 类 | Phase 4 §8 L13："禁止顶层 export Attention 类符号（避免误读为 L3 已落地）" |
| `_state_context.py` selection-C | Phase 4 §8 L10：选项 C 主路径，但 selection-A/B 都被显式 reserve |
| `identify_object` 1.9s budget 三段 | Phase 4 §8 L11：W4-5 specific（option α + Nanobot 同步路由 defer Phase 5+）|
| `IngestRunner._observation_to_node` factory | ADR-L1.5-001：Phase 4→5 transition 临时方案，§4.1 三触发器升 typed/子类 |

如果**反推**这些临时实现 → 把"Phase 4 临时方案"锁成"正式接口"——下一阶段（P3 仿生升级、A10 接入、菜单画布、4 类块）就被钉死在错误抽象。

### §2.2 怎么避免反推（机制）

1. **frontmatter `driven_by:` 字段强制**——必须 cite needs / app-flow / capability，不允许 cite code 符号
2. **status 5 态强制分级**——临时实现必须标 `experimental`，不允许 `locked`
3. **sub-chat 入场 prompt 显式禁止**（§7.5.7）
4. **主 chat Stage 4 反向校验**——每接口的 driven_by 必须真在 Stage 1/2 inventory 里

---

## §3 status 5 态语义

| status | 含义 | 触动 Phase 4 §8 锁 | 例 |
|:--|:--|:--|:--|
| `locked` | Phase 4 §8 已锁；任何变更需新 ADR | 是 | EcpEvent / EcpEventType 13 / cs_parity 4 / Δ_focus=0.2 等 |
| `evolving` | 已落地但允许小步迭代（schema_version 内字段加） | 否 | BB schema 26 keys / RefKind / ParrotAnimation enum 等 |
| `experimental` | Phase 4 临时实现；不允许 lock；待重做 | 否 | FocusBboxThreshold / selection-C / identify_object 1.9s / IngestRunner factory |
| `proposed-upgrade` | 既有但需升级（如 PlanUI wire / body_state 解锁 / capability gating）| 看具体；触 wire 必须新 ADR | 见 cross_chat_pending_registry NEED-* / TODO(P3-*) |
| `proposed-new` | 应有但代码缺（如 4 类块预设 / persona 文件外置）| 看具体 | NEED-P2.5-A persona / NEED-P3-B 4 类块注册表 |

---

## §4 9 字段 frontmatter 模板

每个接口文件**强制**：

```yaml
---
status: locked | evolving | experimental | proposed-upgrade | proposed-new
interface_id: <唯一稳定 ID，如 wire-ecp-event-v1>
topology: wire | cross_process | in_process | capability
ai_priority: high | medium | low
ai_audience: ai_only | human_only | both
schema_version: <int>

driven_by:                                              # ⚠️ 强制
  - "needs:NEED-XX" 或 "app-flow:step-N" 或 "capability:CAP-YY"

upgrade_from: <既有代码符号或 doc 引用>                  # ⚠️ 仅 proposed-upgrade 状态填
freeze_test: <test 路径，或 explicit "deferred-to-Chat-N">  # 强制
producer: <code 真源单一行>                              # 强制 — Stage 4 验证阶段填
consumer: ["<grep evidence 1>", ...]                    # 强制 — Stage 4 验证阶段填

last_locked: <YYYY-MM-DD，仅 wire 类必填>
last_reviewed: 2026-05-07
related: ["<interface_id 引用清单>"]
---
```

---

## §5 拒绝清单（sub-chat 入场必背）

❌ **不允许**：
1. 从代码符号反推接口起点
2. 把 Phase 4 §8 显式标 "Phase 4 临时" 的实现锁成 `locked`
3. 重新设计 Q2 / Q11 / Q12 已 sign off 的拓扑分类
4. 直写 `INDEX.md`（仅主 chat 写）
5. 动其他 sub-chat 子目录的文件
6. 触动 Phase 4 §8 13 决策锁任何一条
7. 引入 `SemanticNode` 子类（违反 ADR-L1.5-001 §4.1 三触发器锁）
8. 接口文件 frontmatter 9 字段缺任意一项
9. `driven_by:` 字段 cite code 符号（必须 cite needs / app-flow / capability）

---

## §6 引用

- 规划稿：[`../architecture/interface_extraction_plan_20260507.md`](../architecture/interface_extraction_plan_20260507.md) §7.5.0 + §7.5.4
- ADR：[`../architecture/adr_protocol_upgrade_and_interface_refinement_background_20260504.md`](../architecture/adr_protocol_upgrade_and_interface_refinement_background_20260504.md)
- Phase 4 §8 锁：[`../architecture/sprint4_phase4_entry_20260430.md §8`](../architecture/sprint4_phase4_entry_20260430.md)
- ADR-L1.5-001：[`../architecture/adr_l1_5_source_dispatch_extension_space_20260504.md`](../architecture/adr_l1_5_source_dispatch_extension_space_20260504.md)
- 行为契约：[`../parrot_behavior_rules.md`](../parrot_behavior_rules.md)
