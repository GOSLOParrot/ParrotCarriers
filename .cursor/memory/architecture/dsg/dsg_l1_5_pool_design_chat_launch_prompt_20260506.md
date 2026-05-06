---
status: ratified
category: chat-launch-prompt
status_note: "DSG L1.5 池 + lifecycle 差异化 + L2-B 简单升级 设计 chat（即派发计划 §1.1 Chat 2）的启动背景与提示词。新 chat 启动时 @ 引用本文 + 按 §1 顺序读完入场必读 6 项即可进入设计阶段。"
last_reviewed: 2026-05-06
ai_priority: high
ai_audience: "新启动的 DSG L1.5 池设计 chat（Chat 2）"
parent_doc: "workspace_index.md"
parent_dispatch: "../sprint4_phase4_downstream_chat_dispatch_plan_20260504.md §1.1 Chat 2"
---

# DSG L1.5 池 + Lifecycle + L2-B 简单升级 — 设计 Chat 启动 Prompt

> **本文用途**：派发到新 chat 的"启动背景与提示词"。新 chat 入场时把本文当 entry SSOT；按 §1 顺序读完入场必读 6 项后即可进入设计阶段。
>
> **基调**：本 chat 是 [`sprint4_phase4_downstream_chat_dispatch_plan_20260504.md §1.1 Chat 2`](../sprint4_phase4_downstream_chat_dispatch_plan_20260504.md) 的实际实施 chat。**不重新讨论已 ratified 决策**（详见 §3）。

---

## §0 Mission（一段话使命）

设计 ParrotCarriers DSG 的 **L1.5 预加载 Node 池** + **状态生命周期差异化** + **L2-B 组织方式简单升级**，并产出**协议升级 doc** + **完成报告**。覆盖桌面场景（baseline）+ 跨 Scene 切换的留白空间；优化参数全部走**策略模块化**（菜单可切，默认桌面 Scene 配置）；DSG 现有代码视为骨架，**允许自由重构**，但**严禁触动** Phase 4 §8 决策锁 / ADR-L1.5-001 §4.1 / `parrot_behavior_rules.md §3.7` Observer-Attention 边界。

**关键约束（用户 2026-05-06 原话）**：

> 新调研资料够你做决策了 — 在我们完成设计 L2 组织方式和架构适配时，一起完善需求。可以在设计过程给我提问，但**问最好重要一点、架构方面一点**，**不要**是优化方面的过度工程问题决策和你觉得搞不定的参数设置 — 那些找其他学习项目和网络经验，或者把参数设定**模块化菜单化**，抛给我测试和网络调研。

---

## §1 入场必读（按顺序读完再进入设计）

> **6 项必读**。每读完一项做一句话总结再读下一项；读完 6 项后才允许写设计稿。

### §1.1 工作区入口（先看路由）

1. [`workspace_index.md`](workspace_index.md) — 完整路由 + 阅读模式 + 派发指引；**先看 §1 + §2.4-§2.6**

### §1.2 用户已决事项 SSOT（不再讨论 ratified 条目）

2. [`dsg_decisions_master.md`](dsg_decisions_master.md) — **决策总表**；**优先级最高**。重点：
   - §0 元约束 M1-M5（桌面优先 / 不过度工程 / 仿生混合路径 / **L1.5 ↔ L2 调研后审窗口** / 不动 Phase 4 锁）
   - §1 L1.5 池定位 + §1.2 三层门控
   - §3 Source × Lifecycle 已决条目 + §3.2 **Obsidian 三分类**
   - §4 注意力**双开放路径**（字段层 vs RustworkX 机制层 — 混合实施由本 chat 裁决）
   - §5 工作记忆延迟归档（**新约束** — 与现有 `l2b_graph.archive_episode_to_graphiti` 冲突，本 chat 处理）
   - §6 P3 边界（A10 / VPS / 软件建图等本 chat 不展开）
   - §7.2 仍 TBD 项 + §8 后续审计触发条件

### §1.3 当前理解快照

3. [`dsg_current_state_distilled.md`](dsg_current_state_distilled.md) — DSG 全景。**精读**：
   - §1 四层语义架构 + §2 源码现状速查
   - §3 Source 字段与 factory 现状（含 Phase 4 ADR-L1.5-001 落地形态）
   - §5 状态生命周期现状（含 §5.4 注意力双开放路径）
   - §6 L2-B 组织方式现状（§6.5 简单程度基线）
   - **§11 防爆炸门控分层架构** — 三层门（A10 端 / L1.5 入池 / L2-B 入图）的当前缺口与设计责任分工
   - **§12 工作记忆延迟归档时机** — §12.2 与现有代码的冲突点（`l2b_graph.start_episode` 立即 archive / `runner.commit_observation` TODO(S4.B)）

### §1.4 新蒸馏 4 个 DSG skill（按 dsg-rustworkx-master §0 路由）

4. **入口**：[`.cursor/skills/dsg-rustworkx-master/SKILL.md`](../../../skills/dsg-rustworkx-master/SKILL.md) §0 决策路由表 → 按问题域跳转

   - **L1.5 入口门控** → [`dsg-l1-5-l2a-conceptgraph-distilled`](../../../skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md) §1-§3 + §8a AR Open Questions Q1-Q10
   - **L2-B Node 组织** → [`dsg-l2b-node-organization-options`](../../../skills/dsg-l2b-node-organization-options/SKILL.md) §1（5 选项 A-E）+ §6.5（子图分层 P1-P4）+ §3.2（跨源合并信号）
   - **检索算法 / 注意力扩散** → [`dsg-l2b-node-organization-options`](../../../skills/dsg-l2b-node-organization-options/SKILL.md) §5（5 候选算法）+ [`dsg-attention-schema-papers`](../../../skills/dsg-attention-schema-papers/SKILL.md) §1（GAT/DySAT/AGCN）+ §5.4（Spreading Activation）
   - **跳数硬上界** → [`dsg-rustworkx-master`](../../../skills/dsg-rustworkx-master/SKILL.md) §3.5 + [`dsg-attention-schema-papers`](../../../skills/dsg-attention-schema-papers/SKILL.md) §1.3（AGCN 实证 4 跳有用 / 10 跳噪声）
   - **仿生 4 范式 RustworkX 落地** → [`dsg-rustworkx-master`](../../../skills/dsg-rustworkx-master/SKILL.md) §3 + §1.2 骨架 vs 血肉范式
   - **节点指针 vs 存储** → [`dsg-l2b-node-organization-options`](../../../skills/dsg-l2b-node-organization-options/SKILL.md) §4 + [`dsg-attention-schema-papers`](../../../skills/dsg-attention-schema-papers/SKILL.md) §5.3（Hippocampal Indexing）

### §1.5 既有约束（接口面 / 行为契约 / 模块边界）

5. **不可动 ROW**：
   - [Phase 4 §8 13 决策锁](../sprint4_phase4_entry_20260430.md) — 尤其 L1（NodeKind 6 / EdgeKind 8 不增删）/ L7（PhotoEvent 不自动建 ObjectNode）/ L9（attention threshold 数值 + 模块边界）/ L11（identify_object 1.9s 预算）/ L13（dsg/attention/__init__ 不 export Attention 类）
   - [ADR-L1.5-001 §4.1](../adr_l1_5_source_dispatch_extension_space_20260504.md) 子类化 3 条触发器 — 当前**全部未触发**；本 chat 设计若触发，必须起新 ADR `supersedes: [ADR-L1.5-001]`
   - [`parrot_behavior_rules.md §3.7`](../../parrot_behavior_rules.md) — Observer 不写 SemanticNode.attention / Attention 不抓帧 / 不写 Graphiti / `dsg/attention/threshold.py` 不塞 BB
   - [`module_map_p2.md §10 / §11`](../module_map_p2.md) — DSG 四层架构 + §11.2 MemoryValidity 过滤器位置（P3）+ §11.4 Observer L3（P3）

### §1.6 按需深读

6. **按需 @ 引用**（不必通读，遇到具体设计点回查）：
   - [`opus_dsg_residual_intent.md`](opus_dsg_residual_intent.md) — Opus 17/18/19 仍生效设计意图
   - [`source_x_lifecycle_status.md`](source_x_lifecycle_status.md) — 7 source × lifecycle 现状对照表（含 Obsidian 三分类）
   - [`open_questions_for_design_chat.md`](open_questions_for_design_chat.md) — Q1-Q4 完整问题清单 + 用户 Q&A 原文
   - `NewZone/distill_output/` — 6 份 Gemini 蒸馏（ConceptGraph / RustworkX docs+repo / SLM / HippoRAG / AriGraph）
   - `NewZone/RustworkX 图模拟研究案例.md` — §119-§122 仿生 4 范式
   - [LineB 完成报告](../lineb_implementation_completion_20260504.md) — `transcript_extractor` 改名 + GEMINI_ORAL source 现接收任何 LLM 助手的口头提及

---

## §2 设计范围（in / out scope）

### §2.1 In scope（**本 chat 必产**）

**A. L1.5 预加载 Node 池**

- 池物理形态裁决（独立 `L1_5Pool` 类 vs 合并入 `L2BGraph` — 详见 [dsg_decisions_master §1.1](dsg_decisions_master.md)）
- 入池条件（触发事件清单 + `confirmation` 默认值矩阵 + 幂等键）
- 出池条件（TTL / 池上限 / 淘汰 priority 链：特殊状态 > 父类状态 > 时间）
- **桌面 1 主桶 + 2 特殊桶**（Obsidian 设定桶 + Google 日程桶）落地形态
- 策略模块化（**每个优化点抛给策略层**，桌面 baseline 默认值 + Scene 切换菜单）

**B. 状态生命周期差异化（按 source）**

- Obsidian 三分类落地（Ref-加强 / 设定-日常 / 设定-Roleplay）— §3.2 master 已锁字段集 + 桶分配
- GOSLO 主动发现 enum 处理（3 选 1：新 enum / source_meta.triggered_by / 独立 filter）
- USER_EXPLICIT 拆 USER_VERBAL / USER_UI 实施
- GEMINI_ORAL "泛泛之谈" vs "当前场景实体"区分规则
- IDENTIFY_OBJECT 命中节点降级规则（lastSeen 永久 + 其他状态字段简化）
- A10 占位（**Node 基础类设计时考虑扩展性即可**，详细设计推 P3）
- 跨 source 状态机（先共用一套 EXPECTED → ACTIVE → PERIPHERAL → GHOST 或类似；测试期不衰减）

**C. L2-B 组织方式简单升级（保留复杂仿生空间）**

- 单图 vs 子图分层（桌面起步单图 + Cluster 边连接特殊桶；P1-P4 选项裁决）
- 索引 / 查询基线（按需建索引，不过度优化）
- **注意力实现路径裁决**（字段层 vs RustworkX 机制层 vs 混合 — 见 master §4 双开放）
- 检索算法选型（PPR / Spreading Activation / 限深 BFS / GAT / 子图同构 — 5 选 N + strategy pattern）
- **复杂仿生设计空间预留位置**（哪些字段 / 接口 / 注释要在简单升级时加，让 Phase 5+ 仿生升级"插入"而不重构）

**D. 工作记忆延迟归档管线**（[master §5](dsg_decisions_master.md)）

- 序列化 schema（JSON / JSONL）+ 硬盘路径约定（`data/conversations/{conv_id}/...`）
- 对话边界判定（什么算"对话结束"）
- 与现有 `l2b_graph.start_episode` 立即 archive 路径的冲突解决方案
- 与 `runner.commit_observation` 内 `TODO(S4.B)` 描述的修正
- nanobot 闲时检测信号（与 `nanobot` skill 协同）

**E. 触发器协议升级**（用户 2026-05-06 原话："写好完成报告和 DSG 和升级相关部分的 ParrotCarriers 协议，比如触发器协议"）

- 现有 4 触发器（Calendar / Message / SceneContext / SsotEnrichment）的入池 / 出池信号集成
- 新增触发器（如：Scene 切换 / Obsidian 设定一键导入 / GOSLO 主动好奇 / Episode close / nanobot 闲时归档）的协议规范
- 触发器 → L1.5 池 + L2-B 工作记忆图的接口契约（参考 ECP wire 风格但不上 wire；纯 Python 内部）
- `obs_log` / `EcpEvent` / Redis Pub/Sub 三路 observability 信号矩阵

**F. L1.5 ↔ L2 适配回审**（[master §8](dsg_decisions_master.md) 触发条件 — Chat 2 sign off 后**必须**做）

- 回审 master 所有 `provisional-revisit-after-L2-design` 条目
- 如新调研给出更优解 → 新决策 `supersedes` 旧条目（注 status 变更 + 链接到新决策位置）
- 锁面交互核对（[`open_questions §Q4.1-Q4.5`](open_questions_for_design_chat.md)）：ADR-L1.5-001 §4.1 是否触发 / Phase 4 §8 是否触动 / cs_parity / Observer-Attention 边界 / 测试基线

**G. 完成报告**

- `architecture/dsg/dsg_l1_5_implementation_completion_<date>.md`（参考 [`lineb_implementation_completion_20260504.md`](../lineb_implementation_completion_20260504.md) 风格）
- 字段集合：实施清单 / 测试结果 / Phase 4 锁 0 漂移证据 / Finding / 与现有 doc 的衔接 / git diff

### §2.2 Out of scope（**本 chat 不做**）

| 项 | 推到哪 | 原因 |
|:--|:--|:--|
| A10 详细接入（CV Flow / SAM2 + DINOv2 / ConceptGraph 集成 / reid_hash 跨源） | P3 / A10 独立设计 chat | [master §6](dsg_decisions_master.md) |
| AR 坐标 + 手机传感器 + 软件建图导入 + VPS 对齐 | P3 | [master §6](dsg_decisions_master.md) |
| MemoryValidity 过滤器具体 Ebbinghaus 衰减公式 + 置信度阈值 | P3 | [`module_map_p2.md §11.2`](../module_map_p2.md) |
| 不可能事件检测（电视瞬移）/ 同类第二实例用户确认 | P3 | [master §1.2 §6](dsg_decisions_master.md) |
| Unity wire 任何字段改动 | 永不（违反 ADR-L1.5-001 Q1）| [master §M5](dsg_decisions_master.md) |
| 真机 spike 验收 | 真机 chat | dispatch §1.3 真机 spike |
| Sprint 5 后续编排（接口提炼 / 独立审计 / 总结报告）| Chat 4-7 | [dispatch_plan §1.2 §1.3](../sprint4_phase4_downstream_chat_dispatch_plan_20260504.md) |
| ChatBot 降级模式 / Cat Maid 协作 | Phase 5+ | dispatch §2 |

---

## §3 硬约束（**严禁触动**）

> 任何想绕过此节的设计，必须先回头与用户讨论；本 chat 单方面修改后续设计稿即无效。

### §3.1 Phase 4 §8 决策锁 13 条 0 漂移

详见 [`sprint4_phase4_entry_20260430.md §8`](../sprint4_phase4_entry_20260430.md)。本 chat 最敏感的 5 条：

| Lock | 不能动什么 |
|:--|:--|
| L1 | `NodeKind` 6 项 / `EdgeKind` 8 项 enum value（增删需新 schema_version + 新 ADR）|
| L7 | PhotoEvent 不自动建 ObjectNode |
| L9 | Δ_focus=0.2 / Δ_bbox=1.0 / threshold=1.0；阈值器在 `dsg/attention` 不塞 BB |
| L11 | identify_object 1.9s 总预算 |
| L13 | `dsg/attention/__init__.py` 不 export Attention 类符号 |

### §3.2 ADR-L1.5-001 §4.1 子类化 3 条触发器

引自 [ADR-L1.5-001](../adr_l1_5_source_dispatch_extension_space_20260504.md)：

> **当满足以下条件之一**时升级到子类（option 3 dispatch）：
>
> 1. L1.5 预加载 Node 池 design（即本 chat）发现 ≥3 个 source 需要的字段差异 ≥3 个
> 2. ≥2 个 source 需要**行为多态**（不只是数据 shape），如 A10 节点 `touch()` 时自动 decay confidence 而 user 节点不 decay
> 3. 类型系统强制 dispatch 的需求被反复手写 isinstance 验证

**本 chat 设计完后必须显式回答**：3 条触发是否触发？

- 触发 → 起新 ADR `supersedes: [ADR-L1.5-001]`
- 全部未触发 → 设计稿声明"3 触发器仍未满足，继续走 meta dict + factory hybrid"

### §3.3 Observer / Attention 边界（[parrot_behavior_rules §3.7](../../parrot_behavior_rules.md)）

- ❌ Observer 写 SemanticNode.attention
- ❌ Attention 抓帧 / 写 Graphiti
- ❌ `dsg/attention/threshold.py` 塞 BB（违反 L9）

### §3.4 跨语言契约守护

- 任何动 `EcpEventType` / `EcpEventSource` / topic 常量 → `tests/test_ecp_event/test_cs_parity.py` 4/4 必失败
- 当前期望：**不动 wire**（按 ADR-L1.5-001 Q1 决定 source 仅 Python 内部）
- 触发器协议升级**仅在 Python 内部** — 不动 EcpEvent，不上 Unity wire

### §3.5 测试基线维持

- 当前 234/234 pytest（含 ADR-L1.5-001 +11 项）
- 设计落地后**必须**新增测试覆盖：
  - L1.5 池入 / 出池 happy path
  - 各 source factory 注册 + 取出
  - lifecycle 状态转换（EXPECTED → ACTIVE → GHOST 等）
  - 工作记忆延迟归档管线（对话期间不写 Graphiti / 序列化 / nanobot 闲时归档）
  - 触发器协议契约（4 既有 + 新增触发器）
  - 与已有 cs_parity / 11 项 source dispatch 测试 0 冲突

---

## §4 允许动作（**自由发挥范围**）

> 用户原话："目前 DSG 相关代码都过于简陋只是骨架，不需太过在意，可自行选择修改，重构，和相关协议的升级"。

✅ **允许**：

- 重构 `src/parrot/dsg/` 内任何文件（含 `l2b_types.py` / `l2b_graph.py` / `ingest/` / `triggers/` / `attention/`）— 但不动 §3 锁定项
- 引入新模块 / 新文件（如 `parrot.dsg.l1_5_pool` / `parrot.dsg.archive_buffer` / `parrot.dsg.l2b_strategies`）
- 升级触发器协议（**Python 内部** — 不上 Unity wire）
- 起新 ADR（如触发 §3.2 升级条件 / 工作记忆归档管线 / 触发器协议升级）
- 修订 `dsg_decisions_master.md` `provisional-revisit-after-L2-design` 条目（用 supersede 而非删除）
- 修改 `runner.commit_observation` 的 `TODO(S4.B)` 描述（per [master §5.2](dsg_decisions_master.md)）
- 修改 `l2b_graph.archive_episode_to_graphiti` 调用时机（per [master §5.1](dsg_decisions_master.md)）
- 重命名 / 重组 `parrot.dsg.ingest.*_filter.py`（如拆 USER_VERBAL / USER_UI，加 GOSLO_AUTONOMOUS filter）

❌ **禁止**：

- 触动 §3 任何锁
- 直接删除 `dsg_decisions_master.md` 既有 ratified 条目
- 跳过测试（任何新增模块必须有对应单测）
- 引入 source 字段到 Unity wire（违反 ADR-L1.5-001 Q1）

---

## §5 输出物（Deliverables）

### §5.1 主设计稿

**文件名**：`architecture/dsg/dsg_l1_5_pool_and_lifecycle_design_<date>.md`

**结构建议**：

```
§0 TL;DR + 决策摘要表
§1 范围 + 元约束（链接 master §0）
§2 L1.5 池架构（物理形态 / 入出池 / 桶分配 / 策略模块化）
§3 状态生命周期差异化（按 source × NodeKind 双轴）
§4 L2-B 简单升级（单图 / 子图 / 注意力路径 / 检索算法）
§5 工作记忆延迟归档管线（三阶段 + 序列化 schema）
§6 触发器协议升级（既有 4 + 新增 N + 接口契约）
§7 复杂仿生设计空间预留点
§8 与既有代码的兼容性证明（Phase 4 §8 0 漂移）
§9 测试计划（happy path / 状态转换 / 触发器契约 / cs_parity 守护）
§10 ADR-L1.5-001 §4.1 触发条件核对（必填）
§11 master `provisional-revisit-after-L2-design` 条目回审（必填）
§12 引用源
```

### §5.2 协议升级 doc

**文件名**：`architecture/dsg/dsg_protocol_upgrade_<topic>_<date>.md`（按主题拆分）

候选主题：

- 触发器协议升级（既有 4 触发器 + 新增触发器的入池 / 出池信号集成）
- 工作记忆延迟归档协议（对话边界 / 序列化 / nanobot 闲时握手）
- L1.5 池接口协议（入池 / 出池 / 查询 / 跨桶桥接）

### §5.3 必要的新 ADR

如果 §3.2 任一触发条件满足，起新 ADR：

- 命名：`architecture/adr_<topic>_<date>.md`
- frontmatter 必填 `supersedes: [ADR-L1.5-001]`（如适用）+ 列出触发的具体条件

### §5.4 完成报告

**文件名**：`architecture/dsg/dsg_l1_5_implementation_completion_<date>.md`

**参考样板**：[`lineb_implementation_completion_20260504.md`](../lineb_implementation_completion_20260504.md)

**字段**：

- §0 TL;DR + 实施清单 / 测试结果 / Phase 4 §8 0 漂移证据
- §1 改动清单（新增 / 修改 / 显式不动）
- §2 设计决策摘录（链接主设计稿）
- §3 测试结果（含 cs_parity / source dispatch 11 / 新增测试基线）
- §4 Phase 4 协议合同 0 漂移评判（链接锁面）
- §5 已知 finding（如有）
- §6 master `provisional-revisit-after-L2-design` 回审结果（哪些 supersede / 哪些保持 / 哪些升 ratified）
- §7 与既有 doc 衔接（含 master / current_state / source_x_lifecycle / open_questions 相应章节更新）
- §8 git diff 验证

### §5.5 master 回写

完成后在 [`dsg_decisions_master.md`](dsg_decisions_master.md) §10 变更日志追加 `2026-XX-XX` 条目，列出新建文件 + 状态升级条目（`provisional-revisit-after-L2-design` → `ratified` 或 `superseded`）。

### §5.6 索引更新

- [`workspace_index.md`](workspace_index.md) §1 文件清单追加新设计稿 / 协议升级 doc / 完成报告
- [`INDEX.md`](../../INDEX.md) §1.1 active 追加（如适用）
- [`active_context.md`](../../active_context.md) 头部追加完成提示
- [`module_map_p2.md`](../module_map_p2.md) §10 / §11 同步更新（如有架构层调整）

---

## §6 提问纪律（**用户最强调的部分**）

### §6.1 应该问用户

✅ **架构 / 模块边界 / 协议结构层** 的关键决策：

- L1.5 池 vs L2-B 是否合并为一类？
- 触发器协议是 Python 内部 enum 还是用 Pydantic schema？
- 工作记忆归档的"对话边界"判定信号是 Brain agent_state 还是 Unity 显式？
- 新 NodeKind enum 增加（如 roleplay 专属）是走 Phase 4 §8 L1 锁内 vs 外？
- 仿生设计预留点放哪些字段（直接影响后续 P3 仿生升级是否需要重构）？

✅ **跨模块协调**：

- 与 `nanobot` skill 闲时检测协同的握手协议？
- 与 `MemoryValidity 过滤器` 接入的接口契约（虽然 P3 实施，但接口应在本 chat 锁形状）？

✅ **超出 master 已决范围且与 ratified 冲突**：

- 如果 4 个新 skill 给出的解法**直接挑战** master 已 ratified 条目，必须先问用户是否 supersede

### §6.2 不应该问用户

❌ **优化参数 / 数值阈值 / 半衰期 / 衰减率**：

- TTL 具体秒数 → 走策略模块化 + 桌面 baseline + 网络调研其他项目（ConceptGraph: obj_min_detections=3 / SLM: TWF τ_eff 等）
- 衰减半衰期 → 同上 + Opus 17 §5.3 起点 + 测试期不启用（master §3.5 已定）
- 池上限节点数 → 桌面 2C8G 性能够 + 不设硬限 + 策略可调（master §1.4）
- 跳数硬上界数值 → 已有锚点（AGCN 实证 4 跳，dsg-rustworkx-master §3.5）— 直接采纳
- IoU / CLIP sim 阈值 → ConceptGraph SKILL §1.2 / §5 已蒸馏 — 直接采纳

❌ **实现细节 / 选项库内候选**：

- L2-B Node 类型选 §1.A vs §1.B vs §1.C（dsg-l2b-node-organization-options 已列）→ 自己依据"桌面最简 + 仿生预留"选；如果难抉择，**做对比表**让用户看完后选
- 检索算法选 PPR vs Spreading Activation → 同上，做对比表
- 子图分层 P1-P4 → 同上，做对比表

**对比表 ≠ 提问**。可以做对比表请用户**裁决**，但不要单独问"用 A 还是 B" — 必须给出对比维度（性能 / 复杂度 / 仿生预留 / 实施成本 / 与既有架构契合度）让用户在表里选。

### §6.3 提问前自查清单

提问前自问：

1. 我能从 4 个新 skill 找到答案吗？
2. 我能从 NewZone/distill_output/ 6 份蒸馏找到答案吗？
3. 我能从 RustworkX 案例.md §119-§122 找到答案吗？
4. 我能从已有项目（HippoRAG / AriGraph / SLM / ConceptGraph）找到先例吗？
5. 这个值能模块化成策略 / 菜单让用户测试期调吗？

**任一**回答"是" → 不问用户，自己消化或写入"策略模块化"。

**全部**回答"否"且涉及**架构 / 模块边界 / 协议结构** → 提问。

---

## §7 成功判据（Sign-off Gate）

### §7.1 设计 sign-off（用户认可设计稿）

- ☑ §5.1 主设计稿落地 + §11 ADR-L1.5-001 §4.1 核对 + §11 master 回审填完
- ☑ §5.2 协议升级 doc（至少触发器协议 1 份）
- ☑ §5.3 必要时新 ADR
- ☑ 用户对设计 sign off

### §7.2 实施 sign-off（代码 + 测试落地）

- ☑ pytest 全绿（≥ 234/234 + 新增基线）
- ☑ 4/4 cs_parity 不动
- ☑ 11/11 source dispatch 测试不动
- ☑ Phase 4 §8 13 条 0 漂移
- ☑ §5.4 完成报告落地
- ☑ §5.5 master 回写 + §5.6 索引更新

### §7.3 收口（Chat 2 退场）

- ☑ master §10 变更日志追加完成条目
- ☑ dispatch_plan §1.1 Chat 2 标 ✅ resolved
- ☑ Chat 4（接口提炼实施）入场 prompt 清晰（如本 chat 影响接口面）

---

## §8 风险与处理

### §8.1 设计触动 ADR-L1.5-001 §4.1 升级条件

**处理**：起新 ADR `supersedes: [ADR-L1.5-001]` 在设计稿之前；用户 sign off 新 ADR 后再继续设计实施。

### §8.2 设计需要新增 EdgeKind / NodeKind enum

**处理**：触动 Phase 4 §8 L1 锁 → **必须**先起 ADR 升 schema_version；不允许在本 chat 单方面增加 enum。

### §8.3 4 新 skill 给出的解法直接挑战 master ratified 条目

**处理**：**先问用户是否 supersede**。不要单方面在设计稿里推翻 ratified。

### §8.4 真机数据缺失导致设计参数无法定

**处理**：策略模块化 + 桌面 baseline 默认 + 留 Scene 切换菜单；不阻塞设计 sign-off；标 finding 留实施后真机调。

### §8.5 工作记忆延迟归档与 nanobot 闲时检测协议未定

**处理**：本 chat 锁**接口形状**（接口签名 / 信号语义）；具体闲时检测信号实施由 P3 nanobot chat 协调。

---

## §9 引用

### §9.1 Master / 决策 / 状态

- [`dsg_decisions_master.md`](dsg_decisions_master.md) — 决策总表（Chat 2 SSOT）
- [`dsg_current_state_distilled.md`](dsg_current_state_distilled.md) — 当前理解快照
- [`source_x_lifecycle_status.md`](source_x_lifecycle_status.md) — source × lifecycle 现状
- [`open_questions_for_design_chat.md`](open_questions_for_design_chat.md) — 开放问题
- [`opus_dsg_residual_intent.md`](opus_dsg_residual_intent.md) — Opus 蒸馏

### §9.2 ADR / 锁

- [ADR-L1.5-001](../adr_l1_5_source_dispatch_extension_space_20260504.md)
- [Phase 4 §8 13 决策锁](../sprint4_phase4_entry_20260430.md)
- [Phase 4 完成报告](../sprint4_phase4_completion_and_final_audit_20260430.md)
- [LineB 完成报告](../lineb_implementation_completion_20260504.md) — 双管线兼容承诺范本

### §9.3 4 个新 DSG skill（按 §1.4 路由表跳转）

- [`dsg-rustworkx-master`](../../../skills/dsg-rustworkx-master/SKILL.md) — **入口**
- [`dsg-l2b-node-organization-options`](../../../skills/dsg-l2b-node-organization-options/SKILL.md)
- [`dsg-attention-schema-papers`](../../../skills/dsg-attention-schema-papers/SKILL.md)
- [`dsg-l1-5-l2a-conceptgraph-distilled`](../../../skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md)

### §9.4 行为契约 / 模块边界

- [`parrot_behavior_rules.md §3.7`](../../parrot_behavior_rules.md)
- [`module_map_p2.md §10 / §11`](../module_map_p2.md)

### §9.5 代码真源

- [`src/parrot/dsg/l1_5_protocol.py`](../../../../src/parrot/dsg/l1_5_protocol.py)
- [`src/parrot/dsg/l2b_types.py`](../../../../src/parrot/dsg/l2b_types.py)
- [`src/parrot/dsg/l2b_graph.py`](../../../../src/parrot/dsg/l2b_graph.py)
- [`src/parrot/dsg/ingest/`](../../../../src/parrot/dsg/ingest/)
- [`src/parrot/dsg/triggers/`](../../../../src/parrot/dsg/triggers/)
- [`src/parrot/dsg/attention/`](../../../../src/parrot/dsg/attention/)
- [`tests/test_dsg/`](../../../../tests/test_dsg/)

### §9.6 派发链上下文

- [`sprint4_phase4_downstream_chat_dispatch_plan_20260504.md §1.1 Chat 2`](../sprint4_phase4_downstream_chat_dispatch_plan_20260504.md)
- [`sprint4_phase4_protocol_and_interface_adr_fork_chat_prompt_20260504.md`](../sprint4_phase4_protocol_and_interface_adr_fork_chat_prompt_20260504.md)（接口提炼 ADR fork chat 启动 prompt — Chat 3 范本，本 chat 是 Chat 2）

---

## §10 启动开局 prompt（**直接发给新 chat 的开场白**）

> **复制下面这段到新 chat 第一条消息**：

```
你是 ParrotCarriers DSG L1.5 池 + Lifecycle 差异化 + L2-B 简单升级 设计 chat（即派发计划 §1.1 Chat 2）。

任务定义文件：
@architecture/dsg/dsg_l1_5_pool_design_chat_launch_prompt_20260506.md

行动顺序：

1. 读完上述文件全文
2. 按其 §1 入场必读 6 项顺序读完（每项一句话总结）
3. 按 §1.4 dsg-rustworkx-master/SKILL.md §0 路由表跳转读对应 sub-skill
4. 按 §6 提问纪律，仅在架构 / 模块边界 / 协议结构层有不可自决的歧义时才问我
5. 优化参数 / 数值阈值 / 实现选项内候选 → 走 §6.1 策略模块化 + 网络调研 + 对比表
6. 按 §5 输出物清单产出设计稿 + 协议升级 doc + 完成报告

硬约束：

- 不动 Phase 4 §8 13 决策锁（详见 §3.1）
- 不动 ADR-L1.5-001（除非触发 §3.2 升级条件，需新 ADR）
- 不动 parrot_behavior_rules §3.7 Observer-Attention 边界
- 不动 cs_parity 跨语言守护（§3.4）
- 桌面 baseline 优先；不过度工程；优化参数策略模块化抛给后续测试

允许动作：

- 重构 DSG 现有 source code（除 §3 锁定项）
- 升级触发器协议（仅 Python 内部，不上 Unity wire）
- 起新 ADR 修订 master provisional 条目

完成判据：

- 设计稿 + 协议升级 doc + 完成报告全部落地
- 234/234 pytest + 新增基线全绿
- master `provisional-revisit-after-L2-design` 条目全部回审完毕
- 用户对设计稿 sign off

开始读 §1 入场必读项 1。
```

---

## §11 变更日志

- **2026-05-06**：本文创建。基于 [dsg_decisions_master.md](dsg_decisions_master.md)（用户已答 Q1.1-Q3.4 第一问后固化）+ 4 新 DSG skill 落地 + LineB 完成 + 用户 2026-05-06 提问纪律明确（架构问 / 优化策略模块化）。新 chat 启动 entry SSOT。
