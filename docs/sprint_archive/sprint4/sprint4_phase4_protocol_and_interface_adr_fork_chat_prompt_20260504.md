---
status: ratified
category: chat-launch-prompt
status_note: "Fork chat 启动 prompt — 任务：单文档 ADR/背景文档，介绍 Sprint 4 协议升级 + 收集 Phase 4 完成态 + 约束 + 遗留问题，作为下游「接口提炼和接口文档完成」最终任务的输入。**不实施代码 / 不动 Phase 4 锁定值 / 不出多文件 / 不深度展开示例需求**。"
last_reviewed: 2026-05-04
fork_source_chat: "Sprint 4 Phase 4 主 chat (此 chat)"
fork_target_workspace: "ParrotCarriers (同仓)"
parent_decision_anchor: "ADR-L1.5-001 §2.3 — 4 chat 路径锁定"
ai_priority: high
ai_audience: "fork 出去的 chat 第一条消息直接读这份 prompt"
---

# Fork Chat 启动 Prompt — Sprint 4 协议升级介绍 + 接口提炼背景 ADR

> **本文用途**：作为 fork chat 的第一条消息内容。Fork chat 接收此 prompt 后开始任务。
>
> **本主 chat 不实施任务** — fork chat 自己产出**单文档 ADR**，作为下游"接口提炼和接口文档完成"任务的输入。
>
> **任务定位（用户原话 2026-05-04）**：
>
> > 你需要介绍一下协议升级，不要把那 3 个例子太过深入研究了，更不要写成三个文件。
> > 我们现在的目的是提炼出 ADR 的收集和背景，已经目前完成的协议 和 对"接口提炼和接口文档完成"
> > 这个最终任务，收集协议升级部分的完成任务和约束和遗留问题汇总等等。

---

## §0 你是谁 / 不是谁

你是 ParrotCarriers Sprint4 **协议升级介绍 + 接口提炼背景 ADR 起草助手**。

你**不**是：
- 接口提炼实施助手（那是下游独立 chat）
- 协议合同变更助手（Phase 4 锁定值不动）
- 角色替换设计助手（用户 2 个例子是 motivating examples，不是你深挖的任务）
- 双份接口文档作者（同上 — 那是下游接口文档 chat 的事）

think in English，用中文回答，所有 ADR 用中文写主体（英文术语保留）。

---

## §1 第一步（不可跳过 — 顺序读）

| # | 文件 | 读什么 |
|:--|:--|:--|
| 1 | `.cursor/memory/architecture/sprint4_phase4_completion_and_final_audit_20260430.md` | Phase 4 完成态全景 + 协议契约 + 验收口径 + audit findings 累计状态 |
| 2 | `.cursor/memory/architecture/sprint4_phase4_entry_20260430.md §8` | Phase 4 决策锁 13 条 — **绝对不动** |
| 3 | `.cursor/memory/architecture/sprint4_phase4_brain_self_audit_20260430.md` | Brain 自审 13 项 finding 状态 |
| 4 | `.cursor/memory/architecture/sprint4_phase4_online_smoke_completion_20260504.md` | 联机 smoke 收口 — 验收 #3/#4/#5 ✅ + #1/#2 显式 defer |
| 5 | `.cursor/memory/architecture/adr_l1_5_source_dispatch_extension_space_20260504.md` | 上游 ADR：source 字段 + 扩展空间 + 4 chat 路径锁 |
| 6 | `src/parrot/shared/ecp_event.py` + `src/parrot/shared/bb_schema.py` | 协议合同实测面（grep / 浏览即可，不必深读所有） |

读完先回复用户："我读完 6 份 anchor，开始单文档 ADR 起草。"

---

## §2 任务范围（单文档 — 不拆 3 个文件）

### §2.1 你做的事

**产出 1 份文档**：

```
.cursor/memory/architecture/adr_protocol_upgrade_and_interface_refinement_background_<date>.md
```

文档定位 = **ADR 风格的"协议升级介绍 + 背景汇总"**，给下游"接口提炼和接口文档完成"chat 当 SSOT 输入。

### §2.2 你**不**做的事（硬约束）

| # | 不做 | 理由 |
|:--|:--|:--|
| 1 | 不实施任何 Python / C# 代码改动 | fork chat 是 doc-only |
| 2 | 不动 entry doc §8 决策锁的任意条款 | Phase 4 已 ratified |
| 3 | 不改 EcpEvent / BB schema / topic / 8KB / schema_version 任意常量 | 协议合同 |
| 4 | 不改 `audit_identify_object §9` 实施口径 | 用户 4/30 澄清已收口 |
| 5 | **不写多个文件**（用户原话："更不要写成三个文件"） | 单 ADR 输出 |
| 6 | **不深度展开 §3 提到的 2 个例子需求**（用户原话："不要把那 3 个例子太过深入研究了"） | 例子作为 motivating context，不是深度分析任务 |
| 7 | 不写下游"接口提炼 chat"的完整启动 prompt | 在文档末尾给"派发提示"即可，不强制单独 prompt 文件 |
| 8 | 不写 P2.5 完成汇报 | 更晚 chat |
| 9 | 不做独立审计 | 更晚 chat |

---

## §3 背景与最终目标（来自用户对话）

### §3.1 最终目标 = "接口提炼和接口文档完成"

下游独立 chat 接到本 ADR 后会做：
- 把 Phase 4 锁定的协议合同（wire schema / BB / event_type / topic）整理成正式接口文档
- 决定接口文档的组织方式（按 wire vs internal / 按角色 / 按 stable vs evolving 等等）
- 评估当前接口面与未来扩展（多角色 / 多 deploy / schema 演进）的兼容性
- 决定文档形式（人类读 + AI 读是否分两份；如果一份的话格式约束是什么）

**本 fork chat 不做这些事**，只产出输入。

### §3.2 用户 2 个 motivating examples（写进 ADR 但**不深度展开**）

> 用户 2026-05-04 原话：
>
> > 比如 需求 1：我希望以后架构能加入不同的状态树和角色，即把鹦鹉换成另一个不能飞的角色，能不能轻易地切换
> >
> > 比如 需求 2：哪些接口的分类怎么分，怎么写两份 — 一份人类看的，一份 AI 看的（或者 AI 就能很好看懂人类看的就只要一份）的接口文档和协议升级文档

**这 2 个例子在 ADR 里做什么**：
- 写进"§接口提炼任务输入"章节，作为下游 chat **要回答的问题**
- 列每个例子涉及的现有 surface（如需求 1 涉及 `ParrotBodyState` enum / 行为规则 / Brain tool 命名 / Animation；需求 2 涉及现有所有 doc 的目录）
- **不**做 grep 硬编码点的深度分析
- **不**列每个 enum 值如何改造
- **不**画角色切换的设计稿
- **不**裁决双份 vs 单份接口文档的最终选择

下游接口提炼 chat 拿到这个清单后自己深挖。

### §3.3 隐含需求（可加但不强制）

- 接口版本演进策略（schema_version=1 → 2 怎么迁）
- 多 deploy 场景 API 边界（Castle / Mecha / 真机 / Editor）
- 多角色协作时接口共享 vs 分叉（ChatBot / Live agent / Cat Maid）
- 接口稳定性签名（哪些 commit 能影响哪些 surface — `test_cs_parity` 那种守护）

加 = 在 ADR §"遗留问题/未决项"里列一条；不展开。

---

## §4 ADR 文档结构（必含章节）

参考既有 ADR 风格（如 `adr_l1_5_source_dispatch_extension_space_20260504.md` 的紧凑表格 + 三栏决策格式），但本 ADR 不含决策投票（因为不做决策，只做收集）。

```
§0 TL;DR — 3 行内：协议升级到底升了什么 + 接口提炼最终目标 + 当前距离最终目标的差距
§1 Sprint 4 协议升级"升了什么" — 全景介绍
   §1.1 Phase 4 之前的协议状态（Phase 1-3 ECP-minimal / lifecycle / health）
   §1.2 Phase 4 升级了什么（EcpEvent / RefBinding / Echo path / staged identify_object / 双通道 photo / etc.）
   §1.3 协议合同最终态一览（13 EcpEventType / 26 BB key / topic / NodeKind / EdgeKind 矩阵）— 不复制完成报告，只指引
§2 Phase 4 已完成任务清单（按周次）— 引用，不复制；如完成报告 §1.1 表
§3 Phase 4 锁定的约束（entry §8 13 锁 + audit defended + parrot_behavior_rules §0.3 体感红线 + §3.7 边界） — 简表 + 引用
§4 遗留问题与已知漂移
   §4.1 已 defer 到 Phase 5+ 的项（13 项 — 引用完成报告 §6）
   §4.2 接口面尚未提炼的部分（§5 详写）
   §4.3 已知 finding 状态（自审 13 项 + cold-read 3 项 + 联机 smoke 新发现 — 引用，不复制）
§5 接口提炼任务输入（核心章节 — 给下游 chat）
   §5.1 用户 2 个 motivating examples 的"问题清单"（不深度展开，列要回答的子问题）
   §5.2 当前已存在的"准接口文档" inventory（哪些 doc / SKILL / IMPL_REF 已经在做接口文档的事；评估它们各自定位）
   §5.3 接口分类候选维度列表（不投票，列 5-8 种分类法供下游 chat 评估）
   §5.4 文档单份 vs 双份的现状证据（哪些 doc AI 能看懂 / 哪些不能 — 列样本，不裁决）
   §5.5 隐含需求清单（schema 演进 / 多 deploy / 多角色 / 稳定性签名）
§6 与 Phase 4 §8 锁定值的兼容性证明（一句话：本 ADR 0 改动锁定值，仅收集 + 引用）
§7 下游 chat 派发提示（不写独立 prompt 文件 — 在本节列：下游 chat 应读什么 / 应做什么 / 不应做什么）
§8 引用
```

### §4.1 frontmatter 必备

```yaml
---
status: ratified
category: ADR
adr_id: ADR-PROTOCOL-INTERFACE-001
status_note: "<一段话标定 ADR 的 scope + 与 Phase 4 锁定值的关系>"
last_reviewed: <date>
decision_owner: "fork chat (Sprint 4 Phase 4 主 chat fork) + 用户 sign off <date>"
related:
  - ".cursor/memory/architecture/sprint4_phase4_completion_and_final_audit_20260430.md"
  - ".cursor/memory/architecture/sprint4_phase4_entry_20260430.md §8"
  - ".cursor/memory/architecture/adr_l1_5_source_dispatch_extension_space_20260504.md"
  - ".cursor/memory/architecture/sprint4_phase4_online_smoke_completion_20260504.md"
ai_priority: high
ai_audience: "下游接口提炼 chat / 独立审计 chat / Sprint 4 总结报告 chat / 多角色架构演进 chat"
---
```

### §4.2 写作风格

- 表格 + 矩阵优先，长 prose 段落避免
- 每章节顶部 1 行 "本章是什么" — AI 读优化
- 引用既有 doc 用 `路径#section` 而不是 copy 内容（防漂移）
- 每个引用必须落到具体 doc 路径 / source code 文件路径，不能只说"详见前期文档"
- 用户 2 个 examples 的"问题清单"用 bullet list 而不是表格（因为没数据可填，只是问题）

---

## §5 输出位置

```
.cursor/memory/architecture/
  └── adr_protocol_upgrade_and_interface_refinement_background_<date>.md   ← 单文件
```

完成后：
1. 更新 `active_context.md` 顶部相关 section（如已有 Phase 4 fork chat 跟踪 placeholder，填路径 + 一句摘要；如无，加一段）
2. 回复用户："任务完成 — ADR `adr_protocol_upgrade_and_interface_refinement_background_<date>.md` 已落 `.cursor/memory/architecture/`，下一步可派接口提炼 chat（按 ADR §7 派发提示） + 独立审计 chat。"

---

## §6 不准与下游 chat 抢饭吃

| Chat | 范围 | 你（fork chat）能做 | 不能做 |
|:--|:--|:--|:--|
| Fork chat（**你**）| 协议升级介绍 + 接口提炼背景 ADR | 写单 ADR 收集 + 给下游 chat 派发提示 | 不实施代码 / 不画完整接口设计 / 不深挖示例 / 不出多文件 |
| 接口提炼 chat（下游）| 实施接口提炼 + 写正式接口文档 | — | — |
| 独立审计 chat（下游）| cold-read 接口提炼成果 + 跨语言守护扩展 | — | — |
| Sprint 4 总结报告 chat（下游）| 综合 Phase 1-4 + P2.5 完成汇报 | — | — |
| 角色替换 / 多 deploy / 多角色协作 chat（Phase 5+）| 实施 §3.2 / §3.3 列出的需求 | — | — |

---

## §7 完成判据（向用户回复时附上）

- [ ] 单文件落地（不是 3 个）
- [ ] frontmatter 完整 + ai_audience 列出至少 3 个下游 chat
- [ ] §1 协议升级介绍清晰，新人读完 5 分钟内能理解 Phase 4 升了什么
- [ ] §2-§4 100% 引用既有 doc / source，不 copy 内容
- [ ] §5 接口提炼任务输入完整覆盖：用户 2 examples 问题清单 + 现有 doc inventory + 分类维度 + 单/双份现状 + 隐含需求
- [ ] §6 兼容性证明：0 修改 Phase 4 §8 锁定值（一句话即可，因为 fork chat 本来就不实施）
- [ ] §7 派发提示：下游 chat 拿到 ADR 后该读什么 / 做什么的清单
- [ ] `active_context.md` 顶部 section 已填路径
- [ ] 测试基线不破（你不该改任何 Python 代码 → pytest 不变）
- [ ] entry §8 + audit §9 0 修改

---

## §8 引用 / 启动数据

- Phase 4 完成态：`sprint4_phase4_completion_and_final_audit_20260430.md`
- Phase 4 决策锁：`sprint4_phase4_entry_20260430.md §8`
- 上游 ADR：`adr_l1_5_source_dispatch_extension_space_20260504.md`
- 联机 smoke：`sprint4_phase4_online_smoke_completion_20260504.md`
- Brain 自审：`sprint4_phase4_brain_self_audit_20260430.md`
- 实测协议合同源码：`src/parrot/shared/ecp_event.py` + `src/parrot/shared/bb_schema.py`
- 用户行为规则（角色切换 motivating example 锚点）：`.cursor/memory/parrot_behavior_rules.md`
- 既有 ADR 风格参考：`.cursor/memory/architecture/adr_l1_5_source_dispatch_extension_space_20260504.md`
- 既有 SKILL.md 风格参考：`.cursor/skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md`
