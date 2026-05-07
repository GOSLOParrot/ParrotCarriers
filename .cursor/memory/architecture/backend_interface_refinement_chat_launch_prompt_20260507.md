---
status: draft / launch-prompt
category: chat-launch-prompt
status_note: "Sub-Chat B 入场 prompt — DSG / Brain 后端接口提炼 chat（模块视角）。从总 chat（app_completion_master_audit_20260507.md）派发。只产 1 份 doc，不写代码、不动 wire、不重叠 Sub-Chat A 范围。"
last_reviewed: 2026-05-07
ai_priority: high
ai_audience: "新启动的 DSG / Brain 后端接口提炼 chat（模块视角）"
parent_doc: "app_completion_master_audit_20260507.md"
related:
  - "../protocol_snapshot_p4.md (协议 SSOT)"
  - "module_map_p4_snapshot.md (架构 quick-ref)"
  - "cross_chat_pending_registry_20260507.md (NEED-* 真源)"
  - "app_flow_requirements_interface_chat_launch_prompt_20260507.md (Sub-Chat A 互不重叠)"
---

# Sub-Chat B — DSG / Brain 后端接口提炼 chat 启动 Prompt

## §0 Mission

把总 chat §1 8 场景对账表的"后端模块边界 + 接口稳定面 + 跨模块 binding"提炼成**1 份 doc**。**视角 = 模块视角**；**不做用户视角 UI 流程**（那是 Sub-Chat A 范围）。**接口提炼真正落地** = 在中间真实业务上下文里**自然形成**，不在纸上做 schema 设计。

> **失败教训**（user 2026-05-07 原话）：上一轮"接口提炼几乎只是把仓库复制了一半"。本 chat 严禁照抄源码，**只做 inventory + 稳定性 audit + 跨模块 binding 表**。

## §1 入场必读（按顺序，≤ 6 份）

1. ⭐ [`app_completion_master_audit_20260507.md`](app_completion_master_audit_20260507.md) — 总 chat 主 doc（§1 8 场景 + §2 5 finding + §3.2 Sub-Chat B 范围）
2. ⭐ [`../protocol_snapshot_p4.md`](../protocol_snapshot_p4.md) — 全协议 SSOT（28 章；重点 §1-§22）
3. ⭐ [`module_map_p4_snapshot.md`](module_map_p4_snapshot.md) — 架构 quick-ref（§2 模块清单 + §4 主数据流 3 路径）
4. ⭐ [`cross_chat_pending_registry_20260507.md`](cross_chat_pending_registry_20260507.md) — 12 NEED-* + 9 TODO 真源（**严禁发明新标签**）
5. **3 完成报告**（已交付能力的唯一证据；只 audit 是否覆盖 user 期望，不重新审计内部）：
   - [`dsg/dsg_l1_5_implementation_completion_20260506.md §1 + §3`](dsg/dsg_l1_5_implementation_completion_20260506.md)
   - [`goslo_modularization_completion_20260506.md §1 + §3`](goslo_modularization_completion_20260506.md)
   - [`lineb_implementation_completion_20260504.md §1 + §4`](lineb_implementation_completion_20260504.md)
6. **3 ADR**（不动；引用即可）：
   - [`adr_protocol_upgrade_and_interface_refinement_background_20260504.md`](adr_protocol_upgrade_and_interface_refinement_background_20260504.md)
   - [`adr_l1_5_source_dispatch_extension_space_20260504.md`](adr_l1_5_source_dispatch_extension_space_20260504.md)
   - [`sprint4_phase4_entry_20260430.md §8`](sprint4_phase4_entry_20260430.md)

> **冷读完 6 份应 ≤ 90 分钟**。3 完成报告每份只读 §1（落地清单）+ §3（测试结果）就够；不要读全文。

## §2 Scope（in / out）

### §2.1 In scope

**1 份 doc**：`architecture/backend_interface_refinement_<date>.md`

结构：
```
§0 TL;DR
§1 接口稳定面分级（ratified / experimental / placeholder 三档）
§2 8 场景的后端模块拆解（每场景 1 子章节）
  §2.1 场景 1 GOSLO AR 陪伴对话 — 模块拆解 / 接口稳定面 / 跨模块 binding / LineB 兼容守护 / Phase 4 §8 0 漂移证据
  ...（场景 2-8 同结构）
§3 跨模块 binding 总表（5 路 TriggerOutcome × 6 下游 + 13 EcpEventType × 3 通道 + 4 active BB key）
§4 LineB 兼容守护硬约束（7 ObservationSource entries verbatim + cs_parity 4/4 + Phase 4 §8 13 锁）
§5 与 Sub-Chat A 的接口（后端事件 → 用户 UI 反馈的 mapping）
§6 引用源
§7 变更日志
```

**每场景子章节必须给出**：
- ① 后端模块拆解（涉及哪些 Python 模块 / Unity 组件）
- ② 接口稳定面（每模块标 ratified / experimental / placeholder + 引证 3 完成报告）
- ③ 跨模块 binding（如 plan_request → PlanRegistry.draft / commit_observations → L1.5 Pool.admit）
- ④ LineB 兼容守护证据（哪些接口必须 pipeline-agnostic）
- ⑤ Phase 4 §8 0 漂移证据（哪些锁项被该场景触及；都 0 漂移）

### §2.2 Out of scope（**严禁触动**）

| 项 | 推到哪 |
|:--|:--|
| 用户视角 UI 流程 | Sub-Chat A |
| 改 wire / 改 enum / 改 BB key | 永不（Phase 4 §8 锁）|
| 设计 ADR / 协议升级 | P3 wire ADR chat / DSG 协议升级 chat |
| 写代码 / 测试 | Chat 4 4-A 实施轨 |
| 重写 SSOT 字段表 / 重画架构图 | protocol_snapshot_p4 + module_map_p4_snapshot 是真源 |
| 发明新 NEED-* 标签 | cross_chat_pending_registry §3/§4 是真源 |
| 重新审计已交付能力的内部接口 | 3 完成报告是证据；只 audit 覆盖度 |
| 接口 surface 的实际重构 | Chat 4 4-A 实施轨 |
| 写超过 1 份新 doc | 强制硬上限 |

### §2.3 防失败模式（user 5/7 原话："几乎只是把仓库复制了一半"）

❌ **禁止行为**：
- 把 `src/parrot/dsg/l1_5/buckets.py` 完整 schema 抄进 doc
- 把 `EcpCommand` / `EcpAck` / `EcpEvent` 字段表重列一遍
- 把 9 个 Trigger 完整代码 inventory
- 把 5 路 TriggerOutcome 字段类型 / 默认值全列

✅ **允许行为**：
- 引用 `protocol_snapshot_p4.md §20` + 一句话说明该场景如何用 5 路上行
- 引用 `dsg_l1_5_implementation_completion §1.1` + 表明该模块属于场景 X 的 ratified 接口稳定面
- 用 mermaid / ASCII 图画出场景 4 的"Plan → Scheduler → Nanobot → result 回流"binding chain（≤ 15 行）

## §3 硬约束

1. **不重写 SSOT** — protocol_snapshot_p4 / module_map_p4_snapshot / cross_chat_pending_registry / 3 完成报告 只引用
2. **8 场景必须全覆盖** — 不允许"这个场景没什么后端"（场景 1 也有 brain.agent + LiveKit Audio）
3. **接口稳定性必填** — 每模块标 ratified / experimental / placeholder + 引证完成报告 §X
4. **LineB 兼容守护必填** — 每场景标该场景哪些接口必须 pipeline-agnostic（特别看 ObservationSource 7 entries）
5. **Phase 4 §8 0 漂移证据必填** — 每场景列触及的锁项 + 都 0 漂移
6. **不超 1 份 doc**

## §4 输出物

`architecture/backend_interface_refinement_<date>.md` ≤ 1 份，建议 ≤ 800 行（含 ≥ 30 个 SSOT 章节锚点引用）。

## §5 启动开局 prompt（直接复制到新 chat）

```
你是 ParrotCarriers DSG / Brain 后端接口提炼 chat（Sub-Chat B，模块视角）。

任务来源：总 chat 主 doc app_completion_master_audit_20260507.md §3.2 派发清单。
任务定义文件：
@architecture/backend_interface_refinement_chat_launch_prompt_20260507.md

行动顺序：
1. 读完 §1 入场必读 6 项（3 完成报告每份只读 §1 + §3，不读全文）
2. 每项一句话总结写 cog 里，不输出
3. 按 §2.1 doc 结构 §0-§7 逐节写
4. 每场景子章节按 5 元素填齐（模块拆解 / 接口稳定面 / 跨模块 binding / LineB 守护 / Phase 4 §8 0 漂移）
5. user sign-off 后即可独立交付

硬约束（违反即停）：
- 不动 wire / 不动 enum / 不动 BB key
- 不发明新 NEED-* 标签（cross_chat_pending_registry §3/§4 是真源）
- 不重写 SSOT 字段表（protocol_snapshot_p4 / module_map_p4_snapshot 真源）
- 不重新审计已交付能力的内部接口（3 完成报告是证据；只 audit 覆盖度）
- 不写代码 / 不写测试 / 不设计 schema
- 不超 1 份 doc
- 8 场景必须全覆盖

防失败模式（user 5/7 钦定）：
不抄源码 / 不重列字段表 / 不重画 SSOT 已有的图。
允许：引用 SSOT §X + 一句话说明该场景如何使用 + 跨模块 binding mermaid（≤ 15 行）。

成功判据：
- 8 场景每个有 5 元素（模块拆解 / 接口稳定面 / 跨模块 binding / LineB 守护 / Phase 4 §8 0 漂移）
- ≥ 30 个 SSOT 章节锚点引用
- 与 Sub-Chat A 互不重叠（A=用户视角 / B=后端模块视角）
- ≤ 800 行 markdown

如果发现某场景必须改 wire / 发明新模块 → 在 doc 中标 BLOCKED-BY-NEW-ADR 并引用
对应 NEED-* 已有标签（去 cross_chat_pending_registry 找）；不当场设计 ADR。

开始读 §1 入场必读项 1（app_completion_master_audit_20260507.md）。
```

## §6 提问纪律

✅ **应该问 user**：
- LineB 6-axis 联机 smoke 是否阻塞 Sub-Chat B（建议：不阻塞；但 axis-5 DSG 文本提取层稳定性是 finding，需在 §4 标）
- Sub-Chat A 完成后是否要 wait Sub-Chat B 再合并（建议：各自独立交付，互引用）
- §3 跨模块 binding 总表是否需要画 mermaid 图（≤ 15 行）；user 偏好简单 ASCII 还是 mermaid

❌ **不应该问 user**：
- 任何 NEED-* 标签的细节（去 cross_chat_pending_registry §3/§4 查）
- 任何已交付能力的内部接口（去完成报告 §1 + §3 查）
- 任何协议字段（去 protocol_snapshot_p4 查）
- 模块边界（去 module_map_p4_snapshot 查）

## §7.5 入场必读补充（2026-05-07 Interface 工作区建立后更新）

> **新增文件**：读完 §1 原 6 份后，**额外读**以下 3 份（已含接口设计全集 + 概念词典 + 遗留问题）：

| 文件 | 读什么 |
|:--|:--|
| ⭐ `architecture/Interface/interface_design_and_how_todo_v0_20260507.md` | §2 名词概念表 + §3 Skill 决策表 + §4 算法决策表 + §5 全 12 场景接口签名 + §6 跨场景 binding 表 |
| `architecture/Interface/interface_design_supplement_20260507.md` | §1.1 Obsidian 3 子类 IngestFilter + §1.3 4-scope BB + §1.4 2 Scene baseline + §1.5 三阶段延迟归档 + §1.6 3 层防爆炸门控 + §3 Sub-Chat B 额外子任务 T-B1-T-B6 |
| ⭐ `architecture/Interface/legacy_issues_split_20260507.md` | §1（P2.5 要解决 30+ 项） + §5 修复 chat 派发表 + **§1.10（新 P2.5：2D 工作区 + Google 日程桶联动）** |

### §2.1.1 增补子任务（来自 interface_design_supplement §3）

- **T-B1** Obsidian 3 子类 IngestFilter 改造（不动 enum；用 meta.profile 区分 ref / daily / roleplay）
- **T-B2** soul.py 4 级视觉自我感知段加载（配合 NEED-P2.5-A persona 外置）
- **T-B3** BB key 4-scope namespace audit + Injector 注入策略矩阵（CC-4 增量）
- **T-B4** SceneType enum 升 2 baseline（DESKTOP_WEBCAM + AR_HANDHELD；不破 cs_parity）
- **T-B5** 工作记忆三阶段延迟归档约束确认（配合 Chat4-archive-llm）
- **T-B6** 3 层防爆炸门控数值基线（L1.5 入池门 + L2-B 入图门；A10 deferred）
- **T-B7（新 P2.5）** Google 日程桶联动后端接口设计：
  - Google 桶开关 = 菜单里设置 / 菜单画布 Google 块连接 → `BucketKind.GOOGLE_CALENDAR` 激活
  - 前端批改日程 → nanobot tasks 同步 → 写 Blackboard（`scheduler/active_tasks` + 状态同步）
  - **若 Google 桶已开**：L2-B 有 Google Node → 可加入 IntentWorkspace（IntentWorkspace.stage(PLAN_AWAITING_USER) + IntentEventBoundaryHandler 处理）
  - **若 Google 桶未开**：nanobot 本地处理同步到 Google 日程 API；不进 L2-B 不进 IntentWorkspace
  - `BucketKind.GOOGLE_CALENDAR` ✅ **已在代码中定义**（`buckets.py:33` + `scene_snapshot.py:74` fresh 桶 + `scene_switch_trigger.py:53` 切 Scene 时 CLEAR；`dsg_protocol_pool_v1 §168` 桌面 4 桶之一）；`protocol_snapshot_p4 §18` 只列 6 项是文档漏记，不影响代码
  - 2D 工作区前端接口：WorkspaceModuleConnector（类菜单画布）→ 连上不同模块（GOSLO=IntentWorkspace / 黑板 / Nanobot）= 所见即所得

## §8 变更日志

- **2026-05-07**：本文创建。Sub-Chat B 入场 prompt（后端模块视角）。
- **2026-05-07（Interface 工作区建立）**：追加 §7.5 新增必读 3 份文件 + §2.1.1 增补子任务 T-B1-T-B7（含新 P2.5 需求：Google 日程桶联动后端接口 + 2D 工作区模块连接）。