---
status: ratified / launch-prompt
category: chat-launch-prompt
status_note: "Chat 4 接口提炼实施前置 — 需求 / 能力 / 接口 提炼方案规划 chat 启动提示词。本 chat **不实施**，只产出 planning doc 让用户 sign off；sign off 后才进 ADR-PROTOCOL-INTERFACE-001 §7.1 描述的实施阶段。"
last_reviewed: 2026-05-07
authoritative_for: "Chat 4 实施前的'范围 + 分类 + 顺序 + 起点'方案规划入场 prompt + 必读索引（含三大 chat 完成报告）"
parent_doc: "../INDEX.md"
parent_dispatch: "sprint4_phase4_downstream_chat_dispatch_plan_20260504.md §1.2 Chat 4"
related:
  - "adr_protocol_upgrade_and_interface_refinement_background_20260504.md §7.1 (实施阶段入场清单 — 本 chat 之后用)"
  - "cross_chat_pending_registry_20260507.md (跨 chat 待办登记表 — 本 chat 关键输入)"
---

# Chat 4 — 需求 / 能力 / 接口 提炼 方案规划 启动 Prompt

> **本文用途**：派发到新 chat 的"启动背景 + 必读索引"。本 chat **只规划不实施** —— 产出方案 doc 让 user sign off；sign off 后才进入 [ADR-PROTOCOL-INTERFACE-001 §7.1](adr_protocol_upgrade_and_interface_refinement_background_20260504.md) 描述的实施阶段。
>
> **基调（user 2026-05-07 原话）**：
> > 让启动 chat 先完成一个让我满意的"需求功能提炼 + 能力提炼 + 接口提炼"的方案和计划：任务先后 / 是否独立 task / 各方案的影响 / 怎么分类 / 怎么全面覆盖需求 / 起点（app flow / 模块图 / 重新划分）。
>
> 本 chat **不预先帮你设计**——它**调研三大 chat 完成报告 + 现有协议契约 + 跨 chat 待办**后，**自己**给出多套方案对比 + 推荐路径 + 必要时澄清问题。

---

## §0 Mission（一段话）

读完 §1 必读 → 自筛补读 → 产出**接口提炼方案规划文档**（含范围 / 分类 / 顺序 / 起点 / 各方案对比 / 推荐 + 理由 / 风险 / 验收判据） → user sign off。**不写实施代码**；**不动协议合同**；**不擅自重命名 enum / wire 字段**。

---

## §1 必读索引（按优先级；分两批，**先批 1 后批 2**）

### §1.1 批 1 — 三大 chat 完成报告（**先读完这 4 份再继续**）

> 这 4 份是"现状全景"。读完前不要急着做规划。

| # | 文件 | 读什么 |
|:--|:--|:--|
| 1 | [`sprint4_phase4_completion_and_final_audit_20260430.md`](sprint4_phase4_completion_and_final_audit_20260430.md) | Phase 4 协议契约**最终态**（§3）+ finding / defer 列表 + 真机 #1/#2 显式 defer 决策。这是基线。 |
| 2 | [`lineb_implementation_completion_20260504.md`](lineb_implementation_completion_20260504.md) | LineB STT-LLM-TTS 双管线兼容性承诺验证；ObservationSource 7 entries verbatim 锁；transcript_extractor 改名（旧名 alias 保留）。**是兼容性范本，必看 §1.3**。 |
| 3 | [`dsg/dsg_l1_5_implementation_completion_20260506.md`](dsg/dsg_l1_5_implementation_completion_20260506.md) | DSG Chat 2 收口报告：14 新模块 + 5 改动 + 118 新测试；§9 finding + 9 处 `TODO(Chat4-*)` / `TODO(P3-*)` 标签登记。**Chat 4 实施清单 50% 来自这里**。 |
| 4 | [`goslo_modularization_completion_20260506.md`](goslo_modularization_completion_20260506.md) + [`goslo_modularization_residual_debt_20260506.md`](goslo_modularization_residual_debt_20260506.md) | GOSLO 模型化收口（5 步 + 暗线审计）：协议哲学（ParrotAnimation 双重身份）+ 残余 7 类 parrot-isms + 4 类块菜单画布前瞻需求。**Chat 4 实施清单另一半来自这里**。 |

### §1.2 批 2 — 跨 chat 待办登记表（**批 1 读完后立刻读**）

| # | 文件 | 读什么 |
|:--|:--|:--|
| 5 | ⭐ [`cross_chat_pending_registry_20260507.md`](cross_chat_pending_registry_20260507.md) | 三大 chat 完成后的统一 TODO + NEED 标签登记。**直接对应 Chat 4 范围**：§5 修复 chat 路径表里"Chat 4（接口提炼实施）"行 = 你要做的事。grep 命令在 §6。 |

### §1.3 批 3 — 协议契约 + 决策锁（**做规划前最后确认**）

| # | 文件 | 读什么 |
|:--|:--|:--|
| 6 | [`adr_protocol_upgrade_and_interface_refinement_background_20260504.md`](adr_protocol_upgrade_and_interface_refinement_background_20260504.md) | ADR-PROTOCOL-INTERFACE-001 — 接口提炼**输入**（user 2 个 motivating examples + 现有"准接口文档" inventory + 8 候选分类维度 + 单/双份现状证据 + 5 项隐含需求）。**§7.1 是实施阶段入场清单（本 chat sign off 后用）**。 |
| 7 | [`sprint4_phase4_entry_20260430.md §8`](sprint4_phase4_entry_20260430.md) | Phase 4 § 8 13 决策锁 — **不能动的部分**。规划方案不得违反任何一条。 |
| 8 | [`adr_l1_5_source_dispatch_extension_space_20260504.md`](adr_l1_5_source_dispatch_extension_space_20260504.md) | ADR-L1.5-001 — DSG source dispatch + 4 chat 路径锁。继续 meta+factory hybrid（DSG Chat 2 已确认 §4.1 三触发器全部未触发）。 |

### §1.4 批 4 — 需求 / 能力来源（**有针对性按需读**）

| # | 文件 | 读什么 |
|:--|:--|:--|
| 9 | [`ar_app_flow_ui_design.md`](ar_app_flow_ui_design.md) | App 流程 + UI 设计基线 — **需求来源**。如果方案选"按 app flow 起点"，这是真源。 |
| 10 | [`requirements.md`](../requirements.md) v2 | 67 功能项 + 决策记录 — 需求层 SSOT。 |
| 11 | [`milestone_p2.md`](milestone_p2.md) | P2 / P2.5 范围与已完成项；"功能验收"目标。 |
| 12 | [`module_map_p2.md`](module_map_p2.md) | **全景架构入口**：§一 模块清单 / §二 数据流 / §九 外挂生态 / §十 DSG 分层（**§10.4 含 DSG Chat 2 后的依赖架构 ASCII 图**）/ §十一 时间轴。如果方案选"按模块架构起点"，这是真源。 |
| 13 | [`parrot_behavior_rules.md`](../parrot_behavior_rules.md) | 行为状态机 + **三层架构**（body / head / cognitive）+ 优先级链 + tool 注册表。Observer / Attention 边界（§3.7）是 DSG / Brain 的硬约束。 |

### §1.5 批 5 — 模块互动方式（按"为什么这样接"补读，**按需挑读**）

| 主题 | 读什么 |
|:--|:--|
| **Obsidian 怎么用** | `dsg/source_x_lifecycle_status.md` §2.1（三分类：Ref-加强 / 设定-日常 / 设定-Roleplay）+ `src/parrot/dsg/ingest/user_tag_filter.py` + `src/scripts/sync_obsidian_to_graphiti.py` |
| **Nanobot 怎么用** | `bus_v4.md` §Nanobot 适配 + `src/parrot/bus/nanobot_consumer.py` + `nanobot/channels/parrot_bus.py`（fork 仓 — 上游审）+ `cross_chat_pending_registry §3.B` Plan↔Nanobot 协议升级路径 |
| **ECP 怎么用** | `sprint4_protocol_v2_ecp.md`（设计稿）+ `sprint4_protocol_ecp_background_20260429.md`（背景 / RIT/BT/BT 森林边界）+ `src/parrot/shared/ecp.py` + `src/parrot/shared/ecp_event.py` |
| **行为模式三层** | `parrot_behavior_rules.md`（body / head / cognitive 三层）+ `src/parrot/shared/parrot_actions.py`（4 enum：ParrotAnimation 8 / ParrotBodyState 5 / CognitiveState 4 / BehaviorMode flags 5）+ `src/parrot/brain/observer/{focus,bbox,sighting}.py` |
| **DSG 三层门控** | `dsg/dsg_l1_5_pool_and_lifecycle_design_20260506.md` §3 + `dsg/dsg_protocol_pool_v1_20260506.md` § 1.2 |
| **Plan-and-Execute 三阶段** | `dsg/brain_protocol_plan_v1_20260506.md` § 4（DRAFT → AWAITING → APPROVED → EXECUTING → DONE/FAILED/REVISED）+ `dsg/brain_protocol_intent_workspace_v1_20260506.md` |
| **协议三层 + 桥接** | `protocol_snapshot_p1.md`（RPC / Redis / DataChannel）+ `bus_v4.md` v4.2（三层 Bus）+ `goslo_model_manifest_protocol_v1.md`（Manifest 是第 4 层 model 协议）|
| **DSG 工作区入口** | `dsg/workspace_index.md` + `dsg/dsg_decisions_master.md` — DSG 系列设计 chat 决策 SSOT |

---

## §2 自筛规则（Self-filter）

读完 §1.1 + §1.2 + §1.3 后，你应该已经能回答：

- [ ] "Chat 4 范围是什么"（cross-chat-registry §5 给出明确清单）
- [ ] "Phase 4 § 8 哪些不能动"（13 决策锁全列）
- [ ] "上一份输入 ADR §5 提了哪些 motivating examples"

如果**任何一条还答不上来 → 回去补读**。读完后再读 §1.4 / §1.5。**不要带着问题写规划稿**。

补读决策树：
- 想做"按 app flow 起点"方案 → 必读 §1.4 #9 / #10
- 想做"按模块架构起点"方案 → 必读 §1.4 #12 + §1.5 模块互动
- 想做"重新划分模块"方案 → 必读 §1.4 #12 + §1.5 全部 + 旧 `module_division.md`（archived，仅追溯）
- 想做"按抽象层（协议 / 接口 / 能力 / 需求）起点"方案 → 必读 §1.3 #6 全文（ADR 已经按层划好了）

---

## §3 规划稿必须回答的关键问题

> 你的规划稿（§4）必须给每个问题一个**明确答案 + 理由**。如果某问题需要 user 裁决，列在 §4.6 提问清单。

### §3.1 范围

1. Chat 4 实施范围是哪些层？（**协议** / **接口** / **能力** / **需求**？）逐层定义边界。
2. 与三大 chat 已完成的部分 0 重叠吗？哪些必然是 Chat 4 主场？哪些只补 TODO？

### §3.2 任务划分策略

3. 独立 task 推进 vs 全面同步 vs 分阶段？
4. 各方案的"协议合同稳定性"风险对比（Phase 4 § 8 锁 / cs_parity / ADR-L1.5-001 三条触发器）？
5. 各方案的"实施时长 / 测试覆盖 / 集成成本"权衡？

### §3.3 分类法

6. 接口分类的**主维度**选什么？（按 app flow / 按模块 / 按抽象层 / 按生命周期 / 按消费者）
7. **副维度**（如有）？
8. ADR §5.3 8 候选分类维度的取舍 + 理由。

### §3.4 接口文档结构

9. 单份 vs 双份（`ai_audience` 区分）？ADR §5.4 已有现状证据，给方案。
10. 多文件分包还是单文件？分包按什么？
11. 索引 / 目录 / 交叉引用怎么组织？

### §3.5 需求覆盖度

12. 67 功能项里哪些跟接口提炼相关？（不必每条详写，给"覆盖率检查表"模板）
13. 当前 cross_chat_registry 的 NEED-P2.5/P3 共 12 项，Chat 4 接什么？
14. App flow 里"启动 → 连接 → 进 AR → 工具调用 → 退出"链路上每一步的接口面是否齐？

### §3.6 起点选择

15. 起点是 app flow？模块架构？还是先重新划分模块？
16. **关键问题**：是否需要重新画一份"最新 module map"？还是用 `module_map_p2 §10.4` 已有 DSG 升级后的依赖图就够？
17. 如果重新画，复用哪些既有图层？

### §3.7 顺序

18. 先做哪步？后做哪步？为什么？
19. 哪些可以并行？哪些必须串行？
20. 推荐"最小可验证落地"序列（先做出最小协议骨架，再迭代补全）。

### §3.8 验收判据

21. 怎么判定 Chat 4 完成？（参考 LineB / DSG Chat 2 / GOSLO mod 三份完成报告的判据格式）
22. 测试基线维持：408/408 → ?/?
23. Phase 4 § 8 + cs_parity + ADR-L1.5-001 守护必须 0 漂移；如何在规划阶段就锁住这一点？

---

## §4 输出物

### §4.1 主交付：方案规划文档

**文件路径**：`architecture/interface_extraction_plan_20260507.md`

**结构建议**（参考 ADR / launch_prompt 风格）：

```
§0 TL;DR + 推荐方案 + 严重度 + 理由（user 看一眼能决策）
§1 范围（§3.1 答案）
§2 任务划分策略（§3.2 + 多方案对比表）
§3 分类法（§3.3 + 副维度）
§4 接口文档结构（§3.4 单/双 / 多文件 / 索引）
§5 需求覆盖度检查表（§3.5）
§6 起点选择（§3.6 + 是否需要重画 module map）
§7 顺序 + 依赖图（§3.7 + 并行 / 串行表）
§8 验收判据（§3.8 + 测试基线锁）
§9 风险 + 修复路径
§10 user 提问清单（哪些需要你裁决）
§11 引用源（必读索引追溯）
```

### §4.2 多方案对比（在 §2 / §3 / §6 内嵌）

每个有选项的问题都给一个**对比表**（不只一个候选），格式参考 GOSLO launch_prompt §2 / DSG Chat 2 §C 表风格。

### §4.3 提问清单（**user 必答**才能进实施阶段）

把"chat 自决到一定程度后还剩的真正不确定点"列在 §10 提问清单。**不要每件事都问 user**——可决策的自决；用对比表让 user 在表里选。

---

## §5 不该做的事

- ❌ **不写实施代码**（任何 `.py` / `.cs` / `.json` 真改）—— 这是 ADR §7.1 实施阶段的事
- ❌ **不动 Phase 4 § 8 13 决策锁**任意一条（要动须先起新 ADR）
- ❌ **不擅自重命名** EcpEventType / BB key / topic / NodeKind / EdgeKind / ParrotAnimation 等 enum 值
- ❌ **不引入** SemanticNode 子类（违反 ADR-L1.5-001 §4.1 三条触发器锁）
- ❌ **不复制粘贴**三大完成报告里的内容凑字数 —— 规划稿的价值是**在已有产出上裁决 / 排序 / 推荐**
- ❌ **不预设答案**让 user 鉴定 —— 给多方案对比 + 推荐 + 理由

---

## §6 完成判据（Sign-off Gate）

- ☑ 方案规划文档 §0-§10 落地
- ☑ §3 21 个关键问题全部有明确答案（包括"defer 到 user 裁决"也算答案，但要在 §10 列清楚）
- ☑ 至少 3 个起点方案（app flow / 模块架构 / 抽象层）有对比表
- ☑ 至少 2 个分类维度方案有对比表
- ☑ 至少 1 个推荐顺序图（含依赖标注）
- ☑ user sign off 推荐方案（或选其他方案）
- ☑ Sign off 后才能 fork 进 ADR §7.1 描述的实施阶段（写代码 / 动接口）

---

## §7 启动开局 prompt（**直接发给新 chat 的开场白**）

> 复制下面这段到新 chat 第一条消息。

```
你是 ParrotCarriers 接口提炼方案规划 chat（Chat 4 实施前置）。

任务定义文件：
@architecture/chat4_interface_refinement_launch_prompt_20260507.md

行动顺序：
1. 读完上述文件全文
2. 按其 §1.1 批 1（4 份完成报告）逐份读完，每份给一句话总结
3. 读 §1.2 批 2（跨 chat 待办登记表 §5 + §6 grep 命令真跑一遍）
4. 读 §1.3 批 3（ADR + Phase 4 § 8 锁 + ADR-L1.5-001）
5. 自筛补读 §1.4 / §1.5（按 §2 决策树）
6. 产出方案规划稿（§4 结构）— 多方案对比 + 推荐 + 理由
7. 在 §10 列出真正需要 user 裁决的提问

硬约束（§5）：
- 不写实施代码
- 不动 Phase 4 § 8 13 决策锁
- 不重命名 enum / wire 字段
- 不引入 SemanticNode 子类
- 不预设答案

完成判据（§6）：
- 方案稿 §0-§10 落地 + 21 个关键问题有答 + 至少 3 起点对比 + 至少 2 分类维度对比 + 推荐顺序图 + user sign off

开始读 §1.1 批 1 第 1 份。
```

---

## §8 引用

- 父 INDEX：[`../INDEX.md`](../INDEX.md)
- 派发地图：[`sprint4_phase4_downstream_chat_dispatch_plan_20260504.md §1.2 Chat 4`](sprint4_phase4_downstream_chat_dispatch_plan_20260504.md)
- 实施阶段入场清单：[`adr_protocol_upgrade_and_interface_refinement_background_20260504.md §7.1`](adr_protocol_upgrade_and_interface_refinement_background_20260504.md)
- 跨 chat 待办登记表：[`cross_chat_pending_registry_20260507.md`](cross_chat_pending_registry_20260507.md)
- 既有 launch prompt 范本：[`dsg/dsg_l1_5_pool_design_chat_launch_prompt_20260506.md`](dsg/dsg_l1_5_pool_design_chat_launch_prompt_20260506.md) + [`goslo_model_modularization_launch_prompt_20260506.md`](goslo_model_modularization_launch_prompt_20260506.md)

---

## §9 变更日志

- **2026-05-07**：本文创建。Chat 4 实施前置 — 方案规划 chat 启动 prompt。基于 user 2026-05-07 原话："让启动 chat 先完成一个让我满意的方案和计划 / 任务先后 / 是否独立 task / 各方案的影响 / 怎么分类 / 起点选择"。覆盖三大 chat（Sprint4 / DSG Chat 2 / GOSLO mod）完成报告 + 跨 chat 待办登记表 + Phase 4 § 8 锁 + ADR-PROTOCOL-INTERFACE-001 §5 motivating examples。
