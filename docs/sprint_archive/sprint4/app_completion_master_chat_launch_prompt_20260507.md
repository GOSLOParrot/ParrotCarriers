---
status: draft / launch-prompt
category: chat-launch-prompt
status_note: "App 完成度 + DSG 必要升级 总 Chat 启动提示词 — 上一轮接口提炼 chat 失败（'几乎只是把仓库复制了一半'）后的纠偏方案：先做需求与能力对账，再 fork 两个并行 sub-chat（App 流程需求 + DSG/Brain 后端接口提炼）。本 chat 只产 2 份纯文档，不写代码、不重构、不复制仓库。"
last_reviewed: 2026-05-07
ai_priority: high
ai_audience: "新启动的 App 完成度总 chat（master chat），随后 fork 出 App-Flow chat + DSG/Brain-Interface chat"
parent_doc: "../INDEX.md"
related:
  - "cross_chat_pending_registry_20260507.md (跨 chat TODO/NEED master)"
  - "../protocol_snapshot_p4.md (当前协议全表)"
  - "module_map_p4_snapshot.md (当前架构 quick-ref)"
  - "ar_app_flow_ui_design.md (App Flow / UI 设计基线)"
  - "../requirements.md (67 功能项需求)"
---

# App 完成度 + DSG 必要升级 — 总 Chat 启动 Prompt

> **本文用途**：上一轮接口提炼 chat 失败后的**纠偏方案启动 prompt**。
>
> **失败教训**（user 2026-05-07 原话）：
> > 接口提炼的计划非常失败，几乎只是把仓库复制了一半。
>
> **纠偏路线**：
> 1. **先做需求与能力对账**（master chat = 本 chat 的接收者）
> 2. **fork 两个并行 sub-chat**（App-Flow 需求接口 + DSG/Brain 后端接口提炼）
> 3. **每个 sub-chat 只产 1 份文档**（共 2 份），不写代码、不复制仓库
> 4. **接口提炼真正落地** = 等 DSG 骨架升级 + Unity App 完成在中间真实业务上下文里**自然形成**，不在纸上做
>
> **基调**：本 chat 是**总入口**，做需求 inventory → 能力 audit → fork 派发；不做实施。

---

## §0 Mission（一段话使命）

把"App 当前能做什么"+"DSG 当前能做什么"+"两边距离 user 期望的核心场景还差什么"对齐到**两份纸**：
- **App Flow 需求接口 doc**（App 用户视角；UI 流程 + 用户操作 → Unity / Brain 端点 → 期望结果）
- **DSG / Brain 后端接口提炼 doc**（后端模块视角；既有接口的稳定面 + 仍需要补的契约 + 跨模块协作的 surface）

**核心验证场景**（user 钦定的"接口能力成果验证"，2026-05-07）：
> **菜单能够完成画布**是一个重要的验证接口能力成果。

如果 4 类块（Model / Persona / Mode / Scene）+ 预设 + 节点画布的菜单能跑通，说明：
- L1.5 Pool / SceneRegistry / BehaviorMode / ModelManifest 4 个模块的接口面够清晰
- BB key + 预设 schema + active_*_id 4 路 binding 闭环
- Unity menu UI ↔ Brain ↔ DSG 后端的 wire / event / RPC 三路通道齐全

→ 总 chat 的成功判据 = **2 份 doc 落地 + 两条核心场景的接口契约清晰可被 sub-chat 实施**。

---

## §1 入场必读（按顺序读完再启动 fork）

> **核心约束**：每读一份做一句话总结。读完 6 份后再决定派发清单；**不要回头读 Phase 1-3 历史档**（那些已被 p4 snapshot 取代）。

### §1.1 真源 quick-ref（先读这两份，10 分钟内吃完）

1. ⭐ [`protocol_snapshot_p4.md`](../protocol_snapshot_p4.md) — **当前协议全表 SSOT**（13 EcpEventType / 26 BB key / NodeKind 6 / EdgeKind 8 / ParrotAnimation 8 / Phase 4 §8 13 锁 / GOSLO Manifest schema / Photo 双通道 / RefBinding 等 14 节）
2. ⭐ [`module_map_p4_snapshot.md`](module_map_p4_snapshot.md) — **当前架构 quick reference**（部署拓扑 + 模块清单 + 5 个新子包就位证据）

### §1.2 已交付能力（3 份完成报告）

3. [`dsg/dsg_l1_5_implementation_completion_20260506.md`](dsg/dsg_l1_5_implementation_completion_20260506.md) §1 + §3 — DSG Chat 2 落地的 14 模块 + 118 测试覆盖
4. [`goslo_modularization_completion_20260506.md`](goslo_modularization_completion_20260506.md) §1 + §3 — GOSLO mod 落地的 Manifest + ModelDriver + animate/fly_to model_id
5. [`lineb_implementation_completion_20260504.md`](lineb_implementation_completion_20260504.md) §1 — LineA / LineB 双管线 pipeline-agnostic 接入面（**关键**：DSG 多源 Ref 推送的核心承诺）

### §1.3 跨 chat 待办登记（**唯一真源**，新 chat 不再发明新标签）

6. ⭐ [`cross_chat_pending_registry_20260507.md`](cross_chat_pending_registry_20260507.md) — §3 P2.5 NEED 清单（A/B/PLAN-INTEGRATION/NANOBOT-HEARTBEAT/ARCHIVE-LLM）+ §4 P3 NEED 清单（A-H）+ §5 修复 chat 路径表

### §1.4 App / 用户期望

7. [`ar_app_flow_ui_design.md`](ar_app_flow_ui_design.md) — **当前 App Flow / UI 设计基线**（启动页 / HUD / 工具柜 / 放大镜 / 注意力框 / 功能入口）
8. [`requirements.md`](../requirements.md) — 67 功能项需求清单（**只看前 §1-§3 总览**，不要逐条钻；fork 出去的 sub-chat 才钻）

### §1.5 GOSLO 残余债（菜单画布 4 类块的需求来源）

9. [`goslo_modularization_residual_debt_20260506.md`](goslo_modularization_residual_debt_20260506.md) §4.3 — 菜单画布 4 类块（Model / Persona / Mode / Scene）的概念图 + NEED-P3-B/C/D/E

### §1.6 行为契约 / 协议边界（避免越界）

10. [`../parrot_behavior_rules.md §3.7`](../parrot_behavior_rules.md) — Observer / Attention / DSG 边界（不可越）
11. [`sprint4_phase4_entry_20260430.md §8`](sprint4_phase4_entry_20260430.md) — Phase 4 § 8 13 决策锁（wire 不动）
12. [`sprint4_protocol_v2_ecp.md`](sprint4_protocol_v2_ecp.md) — ECP V2 设计（Brain ↔ Unity 目标驱动 + 状态同步契约）

> **共 12 份。冷读完所有 12 份应该用 ≤ 90 分钟**。如果读完每份不能一句话总结，回头再扫一遍那一份。

---

## §2 Scope（in / out）

### §2.1 In scope（本总 chat 必产）

**A. 需求与能力对账表（**核心交付物 1 份**）**

只产**一张**对账表 + 一段总结。表的结构：

| user 期望场景 | 涉及模块 | 已交付能力（引证 §1.2 报告）| 缺口（引证 §1.3 NEED-* 标签） | 修复 chat 派发 |
|:--|:--|:--|:--|:--|

至少覆盖以下 **8 个核心场景**：App当中，AR Spike里

1. **GOSLO 在 AR 房间陪伴对话**（最基础场景）
2. **GOSLO 主动好奇看场景物体 → 触发识别 / 入池 / 反馈**（DSG 物体触发脚本 + L2-B 多源 Ref 推送的最小验证）
3. **拍照 → 展示 → GOSLO 评论**（W8 photo + 富文本回程 + IntentWorkspace stage）
4. **GOSLO 派发 nanobot 长任务（如 research）→ 解阻塞继续对话 → result 回流 → 富文本批改 / 汇报展示**（Plan-and-Execute 完整闭环）
5. **GOSLO 进 Intent 制定 Plan → 用户在 Unity menu 确认 → 派发执行**（Plan UI wire — NEED-P3-Wire-PlanUI）
6. **菜单画布 4 类块切换 + 预设保存 / 恢复**（NEED-P3-B/C/D/E — **核心验证接口能力成果**）
7. **从 LineA（Gemini Live）切换到 LineB（STT-LLM-TTS） / 反向 — 行为不变**（双管线 pipeline-agnostic 验证 + L2-B 同 source 入池）
8. **场景切换（桌面 → 户外占位）+ 永久权威 Bucket 跨切保留 + 对话延迟归档触发**（DSG SceneSwitchTrigger + ConversationBoundary）

**B. fork 派发清单（**核心交付物 2 份**）**

为下两个 sub-chat 各写一份精简的入场 prompt（≤ 100 行/份）：

- **Sub-Chat A：App Flow / 需求接口 chat**
  - 输入：本 chat 的对账表 §A + ar_app_flow_ui_design.md
  - 输出：`architecture/app_flow_requirements_interface_<date>.md`
  - 视角：**用户视角**（user 操作 → UI 反馈 → 后端期望）
  - 焦点：UI 流程 + Unity 端点 + 各场景的 happy path / 失败路径
  - **不做**：Backend 内部接口设计；任何代码实施；任何超出 8 场景的范围扩张

- **Sub-Chat B：DSG / Brain 后端接口提炼 chat**
  - 输入：本 chat 的对账表 §A + protocol_snapshot_p4 + 完成报告 + cross_chat_pending_registry
  - 输出：`architecture/backend_interface_refinement_<date>.md`
  - 视角：**模块视角**（接口稳定面 + 跨模块 surface）
  - 焦点：8 场景背后的 backend 模块边界、契约稳定性、跨模块 binding
  - **不做**：UI / 用户视角；改 wire / 改 enum；任何代码实施；接口 surface 的实际重构

### §2.2 Out of scope（**本总 chat 严禁触动**）

| 项 | 推到哪 |
|:--|:--|
| 改任何源码 / 重构 / 移文件 | 本 chat 不允许 — 这是上一轮 chat 失败的根源 |
| 改任何 wire / enum / namespace | 永不（Phase 4 §8 锁） |
| 设计任何新协议 / 新模块 | 任意 sub-chat 之后才考虑（先做需求 inventory） |
| 写任何代码 / 测试 | 留 Chat 4 实施 chat |
| 写超过 2 份新 doc（除入场 prompt） | 强制约束 — 多写就是退回失败模式 |
| 重写已有 doc（cross_chat_pending_registry / protocol_snapshot / module_map）| 严禁 — 这些是 SSOT，新 chat 引用而非改写 |
| 提出大架构升级（如 Plan namespace 入 BB schema 等）| 留 P3 ADR chat |
| 设计 4 类块菜单画布的具体 UI 控件 | 留 AR menu 独立 chat |

---

## §3 硬约束（**严禁触动**）

### §3.1 不重复劳动

- **`cross_chat_pending_registry_20260507.md` 是 NEED-* 标签的唯一真源**。新 chat 想用新需求，先入登记表（§7 维护规则），不直接发明
- **`protocol_snapshot_p4.md` 是协议字段唯一真源**。要查"什么 enum 几项 / 什么 channel 走什么"全在那
- **3 份完成报告**（DSG Chat 2 / GOSLO mod / LineB）是已交付能力的唯一证据。**不要重新审计**已交付内容；只 audit 是否覆盖 user 期望

### §3.2 不发明新协议 / 新模块

总 chat **不写 ADR**。如发现现有 8 场景**必须**新协议才能跑（如 Plan UI 的 EcpEventType）：
- 在对账表标 `BLOCKED-BY-NEW-ADR` + 引用 `NEED-P3-A` 等已存在标签
- **不**当场设计 ADR；推 P3 ADR chat 处理

### §3.3 不写代码骨架

总 chat 输出**纯 markdown**。Sub-chat 启动时也只写 markdown。代码在 Chat 4 实施 chat 才动。

### §3.4 不超 2 份输出 + 2 份 fork prompt

**强制硬上限**：4 份新 doc（含 2 份 fork prompt）。多 1 份就是失败。

---

## §4 推荐推进顺序

```
Step 1（30-60 min）：读 §1 12 份必读 → 一句话总结写在 cog 里（不输出）
Step 2（30 min）：写 §A 对账表（8 场景 × 4 列）
Step 3（10 min）：写 §A 总结段（5 个发现 / 缺口 / 优先级）
Step 4（30 min）：写 Sub-Chat A 入场 prompt（≤ 100 行）
Step 5（30 min）：写 Sub-Chat B 入场 prompt（≤ 100 行）
Step 6：交付，请 user sign-off → fork 两个 sub-chat 并行启动
```

**总耗时上限：3 小时**。超时即停 + ask user。

---

## §5 输出物（Deliverables，**仅 4 份**）

### §5.1 主 doc（**1 份**）

**文件名**：`architecture/app_completion_master_audit_<date>.md`

**结构**：
```
§0 TL;DR — 8 场景能力 / 缺口 / 修复 chat 路径
§1 §A 对账表（8 场景 × 4 列）
§2 §A 总结（5 个发现）
§3 派发清单（Sub-Chat A / B 各自范围 + 输出 doc 名 + 完成判据）
§4 与现有 SSOT 的引用关系（用 / 不重复 / 不改写 §1-§3 真源）
§5 引用源
§6 变更日志
```

### §5.2 Sub-Chat A 入场 prompt（**1 份**）

**文件名**：`architecture/app_flow_requirements_interface_chat_launch_prompt_<date>.md`

**结构**（参考本文格式但**精简**）：
```
§0 Mission（用户视角 App Flow 需求接口 doc）
§1 入场必读（≤ 6 份；含本 chat §A 对账表）
§2 Scope（8 场景的用户视角拆解）
§3 硬约束（不写代码 / 不动 wire / 不超出 8 场景）
§4 输出物（1 份 doc）
§5 启动开局 prompt（直接复制到新 chat）
```

### §5.3 Sub-Chat B 入场 prompt（**1 份**）

**文件名**：`architecture/backend_interface_refinement_chat_launch_prompt_<date>.md`

**结构**：
```
§0 Mission（模块视角 DSG/Brain 后端接口提炼 doc）
§1 入场必读（≤ 6 份；含本 chat §A 对账表 + protocol_snapshot_p4 + 3 完成报告）
§2 Scope（8 场景的后端模块拆解 + 接口稳定面 audit）
§3 硬约束（不写代码 / 不动 wire / 不重新发明 NEED 标签）
§4 输出物（1 份 doc）
§5 启动开局 prompt
```

### §5.4 索引更新（**1 份小 patch**）

更新 `INDEX.md` §〇 加 1 行入口：本主 doc 的 ⭐ 引用。

---

## §6 提问纪律（最后一道防线）

### §6.1 应该问 user

✅ 8 场景**必须 vs 应当 vs 可选**优先级（fork 前确认 Sub-Chat A 的 happy path 范围）
✅ Sub-Chat A 完成后是否要 wait Sub-Chat B 再合并 / 还是各自独立交付
✅ 菜单画布的"列表 fallback"是否在第一版必交付（NEED-P3-E）
✅ Plan UI wire 升级（NEED-P3-Wire-PlanUI）是否阻塞 Sub-Chat A — 若是，Sub-Chat A 用占位 stub UI 还是停等

### §6.2 不应该问 user

❌ 任何 NEED-* 标签的细节（去登记表 §3 / §4 查）
❌ 任何已交付能力的内部接口（去完成报告 §1 / §3 查）
❌ 任何协议字段（去 protocol_snapshot_p4 查）
❌ 各场景的 UI 控件 / 像素细节（留 AR menu 独立 chat）

---

## §7 风险与处理

### §7.1 风险 R1：本 chat 又复制半个仓库

**症状**：开始大量 quote 既有 doc 内容
**处理**：每次想 quote 时，先检查能否仅 link + 引用章节号

### §7.2 风险 R2：8 场景对账表写得太大

**症状**：对账表 > 200 行 / 每场景写满 5+ 段背景
**处理**：每场景 ≤ 1 行表格行 + 1 句话能力 + 1 句话缺口；想写更多就 fork 出去给 sub-chat

### §7.3 风险 R3：发明新 NEED 标签

**症状**：在对账表里出现 `NEED-P2.5-X` / `NEED-P3-Y` 等登记表里没有的标签
**处理**：先检查 cross_chat_pending_registry §2.1 / §2.2 是否已有；若真新，先写到登记表 §3 / §4 + 加 grep 索引行，再回引

### §7.4 风险 R4：Sub-Chat A / B 范围互相重叠

**症状**：两份 fork prompt 都说"覆盖 GOSLO 拍照展示"
**处理**：A = **用户操作 → UI / Unity 端点**；B = **后端模块 → 协议契约**。同一场景两边各写自己的角度，不重叠

---

## §8 启动开局 prompt（**直接发给新 chat 的开场白**）

> **复制下面这段到新 chat 第一条消息**：

```
你是 ParrotCarriers App 完成度 + DSG 必要升级 总 Chat（master chat）。

任务背景：上一轮接口提炼 chat 失败（"几乎只是把仓库复制了一半"）。
本 chat 是纠偏方案的总入口，做需求 inventory + 能力 audit + fork 派发，
不做实施、不写代码、不复制仓库。

任务定义文件（先读）：
@architecture/app_completion_master_chat_launch_prompt_20260507.md

行动顺序：
1. 按 §1 入场必读 12 项顺序读完（每项一句话总结，写在自己 cog 里）
2. 按 §4 推荐推进顺序，写 §5.1 主 doc（对账表 + 总结）
3. 写 §5.2 / §5.3 两份 sub-chat 入场 prompt
4. 更新 INDEX.md §〇 加入口
5. 请 user sign-off → fork 两个 sub-chat 并行启动

硬约束（违反即停）：
- 不改任何源码 / 不动 wire / 不动 enum / 不动 namespace
- 不发明新 NEED 标签（cross_chat_pending_registry §2 是唯一真源）
- 不重写已有 SSOT（protocol_snapshot_p4 / module_map_p4 / 3 完成报告）
- 不超 4 份新 doc（含 2 份 fork prompt）
- 总耗时 ≤ 3 小时；超时停 + ask user

成功判据：
- 8 场景对账表清晰
- 5 个 finding / 缺口 / 优先级总结
- 2 份 sub-chat 入场 prompt 互不重叠（A=用户视角 / B=模块视角）
- INDEX.md 加入口
- user sign-off 后即可 fork 启动

如果发现任何场景**必须**改 wire / 发明新模块 → 在对账表标
"BLOCKED-BY-NEW-ADR" 并引用对应 NEED-P3-A / G 等已有标签；
不当场设计 ADR。

开始读 §1 入场必读项 1（protocol_snapshot_p4.md）。
```

---

## §9 引用

- 跨 chat 待办登记：[`cross_chat_pending_registry_20260507.md`](cross_chat_pending_registry_20260507.md)
- 协议 SSOT：[`../protocol_snapshot_p4.md`](../protocol_snapshot_p4.md)
- 架构 quick-ref：[`module_map_p4_snapshot.md`](module_map_p4_snapshot.md)
- 完成报告 3 份：DSG Chat 2 / GOSLO mod / LineB（路径见 §1.2）
- App Flow 基线：[`ar_app_flow_ui_design.md`](ar_app_flow_ui_design.md)
- 需求清单：[`../requirements.md`](../requirements.md)
- 残余债（菜单画布需求源）：[`goslo_modularization_residual_debt_20260506.md`](goslo_modularization_residual_debt_20260506.md)
- 行为契约：[`../parrot_behavior_rules.md`](../parrot_behavior_rules.md)
- Phase 4 锁：[`sprint4_phase4_entry_20260430.md §8`](sprint4_phase4_entry_20260430.md)
- ECP V2 设计：[`sprint4_protocol_v2_ecp.md`](sprint4_protocol_v2_ecp.md)

---

## §10 变更日志

- **2026-05-07**：本文创建。上一轮接口提炼 chat 失败的纠偏方案启动 prompt。
  - 路线：纸面 inventory + audit → fork 2 并行 sub-chat → 实施层做接口提炼（在中间真实业务上下文里自然形成）
  - 硬约束：仅 4 份新 doc / 不写代码 / 不动 wire / 不发明 NEED 标签 / 总耗时 ≤ 3 小时
  - 成功判据：8 场景对账表 + 2 sub-chat fork prompt + INDEX 入口 + user sign-off
