---
status: draft / launch-prompt-v2
category: chat-launch-prompt
status_note: "Sub-Chat B v2 启动 prompt — 替换 v1（backend_interface_refinement_chat_launch_prompt_20260507.md，保留作历史）。新增：① 工作区域硬边界（DSG / Brain / Scheduler / Bus 后端）② 代码先行（先读 src/parrot/ 实际代码再写 doc）③ DSG 工作区文档 drift 修复 ④ 工作区完整性 audit。原则：代码先行，不让文档过度工程领跑。"
last_reviewed: 2026-05-07
ai_priority: high
ai_audience: "Sub-Chat B 后端模块视角 + DSG 工作区文档维护 chat"
parent_doc: "app_completion_master_audit_20260507.md"
supersedes: "backend_interface_refinement_chat_launch_prompt_20260507.md"
---

# Sub-Chat B v2 — DSG/Brain 工作区调研 + 后端模块接口 chat

## §0 Mission（一段话）

代码先行 → 把 `src/parrot/` + `architecture/dsg/` + `Interface/` 4 文件读进来 → 修 DSG 工作区文档与代码 / Interface/ 设计的 drift → 写 1 份后端模块接口提炼 doc（8 场景）→ audit DSG 工作区干净完整。**不写代码 / 不动 wire / 不重写 SSOT / 不重新审计已交付内部**；不让 doc 跑在 code 前面。

---

## §1 工作区域（硬边界）

| 范围 | 路径 | 角色 |
|:--|:--|:--|
| **可读 代码** | `src/parrot/dsg/` | DSG 主场（L1.5 / L2-B / triggers / ingest / attention / archive）|
| **可读 代码** | `src/parrot/brain/{plan/, intent_workspace*.py, observer/, tools/, agent.py, soul.py}` | Brain 后端 |
| **可读 代码** | `src/parrot/scheduler/` | Scheduler 后端（plan-* TODO 主场）|
| **可读 代码** | `src/parrot/bus/` + `src/parrot/memory/` + `src/parrot/shared/` | 总线 / 记忆 / 共享 |
| **可读 代码** | `tests/test_dsg/` + `tests/test_brain/` + `tests/test_scheduler/` | 测试基线（验证守护）|
| **可读 + 可改 doc** | `architecture/dsg/*.md` | DSG 工作区文档（修 drift OK；不重写 SSOT）|
| **可读 + 可改 doc** | `architecture/Interface/*.md` | Interface 工作区文档（同上）|
| **可读 + 可改入口** | `architecture/dsg/workspace_index.md` | 加 §1.4 Interface 交集 + 修 broken link |
| **只读 引用** | `architecture/sprint4_phase4_entry_20260430.md §8` | Phase 4 §8 13 锁（不动）|
| **只读 引用** | `architecture/protocol_snapshot_p4.md` | 协议 SSOT（不重写）|
| **只读 引用** | `architecture/cross_chat_pending_registry_20260507.md` | NEED-* / TODO 真源（不发明）|
| **只读 引用** | `architecture/adr_l1_5_source_dispatch_extension_space_20260504.md` | ADR-L1.5-001 决策锁（不动）|
| **只读 引用** | `architecture/ar_*.md` | AR 工作区（Sub-Chat A 主场；本 chat 仅引用交集 — Unity 事件接口 / EcpEvent / RefBinding） |
| **❌ 不读 / 不动** | `unity/ArSpike/` / `unity/ParrotDev/` | Unity 代码（Sub-Chat A 主场）|
| **❌ 不写代码** | 任何 `.py` / `.cs` 修改 | 全部都不允许 |

> **注脚（2026-05-07 增量）**：`memory/MemoryValidity 过滤器` PLANNED（`module_map_p2 §11.2`）= UI 别名"有效期预测模块"。**本 chat 范围内 backend 不实现**——仅 canvas 菜单占位（见 `menu_design_complete §4.7` + NEED-P3-FILTER / NEED-P3-VALIDITY 已登记 `cross_chat_pending_registry §4.I / §4.J`）。Task 1 代码现状审查时如发现 `src/parrot/memory/` 暂无该模块，**正常**——不要标 drift。

---

## §2 入场必读（≤ 6 份；按顺序读完再做事）

1. **本文件**（任务定义）
2. ⭐ `architecture/Interface/interface_design_and_how_todo_v0_20260507.md` §5（12 场景接口签名）+ supplement §1（7 项新发现）
3. ⭐ `architecture/Interface/concept_dictionary_20260507.md` §1-§5（≈80 后端概念）+ §10（同义词追溯）
4. ⭐ `architecture/Interface/legacy_issues_split_20260507.md` §1-§2（要解决 / P3 完成 二分；NEED-* 全清单）
5. ⭐ `architecture/dsg/dsg_current_state_distilled.md` + `dsg_decisions_master.md` — DSG 全景 + 决策 SSOT
6. **代码扫一遍**（不细读；建索引）：
   - `src/parrot/dsg/` 各文件 + 类一句话职责
   - `src/parrot/brain/{plan/, intent_workspace*, observer/}` 同上
   - `src/parrot/scheduler/{nodes,service,blackboard}.py` 同上
   - `tests/` 测试基线 (`pytest -q --collect-only` 或 ls)

> **冷读完**应 ≤ 90 分钟；3 完成报告（DSG Chat 2 / GOSLO mod / LineB）只读 §1（落地清单）+ §3（测试结果），**不读全文**。

---

## §3 4 个任务（按权重 + 推进顺序）

### Task 1 — 代码现状审查（**先读代码再写 doc**；权重 30%）

目标：搞清楚 `src/parrot/` 现在**真实**有什么、哪些 NEED-P2.5-* 阻塞代码 / 哪些 ratified 但 Interface/ 漏写。

**做法**：
- ① 列各子模块文件清单 + 类清单（每模块 1-2 行）
- ② 对照 `Interface/concept_dictionary §2-§5`（80 后端概念）→ 哪些命名已 ratified / 哪些 v0 描述但代码还没 / 哪些代码有但 v0 漏写 / 哪些是 standalone experimental（已知漂移 §3）
- ③ 对照 `Interface/legacy_issues §1`（要解决 P2.5 范围）→ 12 个 TODO(Chat4-*) / TODO(P3-*) 在源码中 grep 是否一一对应
- ④ 输出 1 张表（**不超 80 行**）：「真实代码状态 vs Interface/v0 描述 vs cross_chat_pending_registry 标签」3 列对账

**做不做的事**：
- ✅ 做：grep 验证标签一一对应 / 模块文件清单 / 测试守护项 mapping
- ❌ 不做：审计已交付能力的内部接口正确性（3 完成报告是真源；不重新跑）

**输出锚点**：写到 Task 3 主产物 doc §0 或附录。

### Task 2 — DSG 工作区文档 drift 修复（权重 30%）

> Interface/ 4 文件 2026-05-07 加了几个新概念（Obsidian 3 子类 / 4 级视觉自我感知 / 防爆炸 3 层门控 / 工作记忆三阶段归档 / 2 Scene baseline / GOSLO_AUTONOMOUS source 落地等），DSG 工作区里旧文档可能有 drift。

**修哪些 doc**（按重要度）：

| Doc | 修什么 | 不动 |
|:--|:--|:--|
| `dsg/workspace_index.md` | §1.4 加 Interface 工作区交集 + broken link 修 + §1.2 Chat 2 启动 prompt 链接是否还有效 | 不重写 §1-§7 |
| `dsg/dsg_current_state_distilled.md` | 检查 §3.1（7 项 ObservationSource）是否已含 GOSLO_AUTONOMOUS 第 8 项；如缺，补 1 行（DSG Chat 2 §1.2 已落地）| 不动 §1-§10 |
| `dsg/dsg_decisions_master.md` | 检查 §0 status 是否已含「Chat 2 实施完成回审」的更新（§10 变更日志已有；查 §1-§7 状态字段是否同步）| 不动用户已决条目 |
| `dsg/source_x_lifecycle_status.md` | 加 GOSLO_AUTONOMOUS 第 8 项 + 5 个新触发器影响（如缺）| 不重写 |
| `dsg/open_questions_for_design_chat.md` | 检查 §0 已决汇总是否完整指向 master | 不动用户原话 Q&A |
| `dsg/dsg_l1_5_implementation_completion_20260506.md` | 仅检查 §7 「与既有 doc 衔接」是否已加 Interface/ 引用；如缺加 1 行 | 不动 §1-§9 落地证据 |

**原则**：
- 修 drift 不是大改；patch 不超过 5 行 / doc
- 不重写决策 / 不修改 ratified 状态
- 引用而非复制

### Task 3 — 8 场景后端模块接口提炼 doc（**主产物**；权重 30%）

输出文件：`architecture/backend_interface_refinement_<date>.md`（v1 fork prompt 已规定路径，沿用）

**结构**（参考 v1 prompt §2.1，**只补不动**）：

```
§0 TL;DR + Task 1 代码现状对账表
§1 接口稳定面分级（ratified / experimental / placeholder 三档）
§2 8 场景 × 5 元素子章节
  - 模块拆解（涉及哪些 Python 模块 / Unity 组件）
  - 接口稳定面（每模块标 ratified / experimental / placeholder + 引证 3 完成报告 §X）
  - 跨模块 binding（plan_request → PlanRegistry.draft / commit_observations → L1.5 Pool.admit 等）
  - LineB 兼容守护证据（哪些接口 pipeline-agnostic）
  - Phase 4 §8 0 漂移证据（触及哪些锁项 + 都 0 漂移）
§3 跨模块 binding 总表（5 路 TriggerOutcome × 6 下游 + 13 EcpEventType × 3 通道 + 4 active BB key + 4-scope BB namespace）
§4 LineB 兼容守护硬约束（7 ObservationSource verbatim + cs_parity 4/4 + Phase 4 §8 13 锁）
§5 与 Sub-Chat A 接口（后端事件 → 用户 UI 反馈 mapping）
§6 防爆炸 3 层门控 + 工作记忆三阶段延迟归档（Interface/supplement §1.5 / §1.6 配套）
§7 引用源
§8 变更日志
```

**长度上限**：≤ 800 行；引用 ≥ 30 个 SSOT 章节锚点。

**防失败模式**（user 5/7 钦定 — "几乎只是把仓库复制了一半"）：

| ❌ 禁止 | ✅ 允许 |
|:--|:--|
| 把 `dsg/l1_5/buckets.py` 完整 schema 抄进 doc | 引用 `protocol_snapshot_p4 §18` + 一句话说明使用方式 |
| 重列 EcpCommand / EcpAck / EcpEvent 字段表 | 引 `protocol_snapshot_p4 §2-§6` + 一句话场景关联 |
| 完整代码 inventory 9 个 Trigger | 引 `dsg_protocol_trigger_v2 §5` + 5 路上行使用方式 |
| 列 5 路 TriggerOutcome 字段类型 / 默认值 | 给该场景的 mermaid binding chain（≤ 15 行）|

### Task 4 — 工作区完整性 audit（**轻量**；权重 10%）

> 只做 6 个小检查，不超过 30 分钟。

| 检查项 | 标准 | 修复方式 |
|:--|:--|:--|
| broken link | grep DSG 工作区所有 `[...](path)` 链接 | 修路径 / 删孤儿 |
| frontmatter `related:` | Interface/ 4 文件已加？ | 加 1 行 |
| INDEX.md §〇 第 12 行 | Interface 工作区已登记？ | 如缺加 1 行 |
| AR / DSG 工作区交集 | EcpEvent / PhotoNode / RefBinding 边界 | 标 §交集；不重写 |
| TODO 标签 grep 一致 | `rg "TODO\(Chat4-"` / `rg "TODO\(P3-"` 数量与 cross_chat_pending_registry §2 对账 | 不动源码；记录差异 |
| 测试基线 | `pytest -q --collect-only ` 是否收集 415 项（Phase 4 §8 守护项不破）| 不跑测试；只 collect |

**输出**：写到 Task 3 主产物 doc 末尾 §audit 小节（**不**单独产 1 份 audit doc）。

---

## §4 输出物清单（**3 份**：1 主 + 2 patch）

| # | 文件 | 类型 | 长度 |
|:--|:--|:--|:--|
| 1 | `architecture/backend_interface_refinement_<date>.md` | 主产物（Task 3 + Task 1 摘要表 + Task 4 audit）| ≤ 800 行 |
| 2 | `architecture/dsg/workspace_index.md` | patch（Task 2）| ≤ 30 行新增 |
| 3 | `architecture/dsg/dsg_current_state_distilled.md` + 其他 dsg/ doc | patch（Task 2）| ≤ 5 行/doc |

> 其他 doc 修 drift 走 inline patch（≤ 5 行 / doc）；不单独列输出。

---

## §5 硬约束（违反即停）

1. **代码先行** — Task 1 没读完代码不允许写 Task 3
2. **不写代码 / 测试** — 全部 `.py` 不动；Sonnet 4.6 实施 chat 才动
3. **不动 wire / enum / BB key** — Phase 4 §8 13 锁 + cs_parity 4/4 + ADR-L1.5-001
4. **不重写 SSOT**（Interface/ 4 文件 / protocol_snapshot_p4 / module_map_p4_snapshot / 3 完成报告 / cross_chat_pending_registry / 3 ADR）
5. **不发明新 NEED-* 标签** — `cross_chat_pending_registry §3 / §4` 是真源
6. **不重新审计已交付能力的内部接口** — 3 完成报告是证据；只 audit 覆盖度
7. **防失败模式** — Task 3 §3 表格规则严格执行（引用而非复制）
8. **不超 3 份新 doc / patch**
9. **8 场景必须全覆盖** — 不允许"P3 化某场景"
10. **不进 AR 工作区代码** — `unity/ArSpike/` 是 Sub-Chat A 主场；本 chat 仅引用交集
11. **不动用户原话 / 已决条目** — `dsg_decisions_master` ratified 条目 / `open_questions §Q&A 原文` 不动

---

## §6 启动开局 prompt（直接复制到新 chat）

```
你是 ParrotCarriers Sub-Chat B v2（DSG/Brain 工作区调研 + 后端模块接口 chat）。

任务定义：
@architecture/backend_interface_chat_launch_prompt_v2_20260507.md

工作区域硬边界：
- 可读代码: src/parrot/{dsg,brain,scheduler,bus,memory,shared}/ + tests/
- 可读+可改doc: architecture/dsg/*.md + architecture/Interface/*.md + dsg/workspace_index.md
- 只读引用: protocol_snapshot_p4 / sprint4_phase4_entry §8 / cross_chat_pending_registry / 3 ADR / ar_*.md (仅交集)
- ❌ 不读: unity/ArSpike/ / unity/ParrotDev/
- ❌ 不写代码 / 不写测试 / 不跑 pytest（只 collect-only）

行动顺序（4 任务）：
1. 读 §2 入场必读 6 份（3 完成报告只读 §1+§3，不读全文）
2. Task 1 代码现状审查（30% — 先读 src/parrot/ 各模块；3 列对账表）
3. Task 2 DSG 工作区文档 drift 修复（30% — patch ≤ 5 行/doc）
4. Task 3 主产物 doc 8 场景后端模块视角（30% — ≤ 800 行；引用 ≥ 30 SSOT 锚点）
5. Task 4 工作区完整性 audit（10% — 6 小检查写到主 doc 末尾）

硬约束（11 条，§5）：
- 代码先行 / 不写代码 / 不动 wire / 不重写 SSOT
- 不发明新 NEED-* / 不重新审计已交付内部 / 不超 3 份输出
- 8 场景全覆盖 / 防失败模式（引用而非复制）/ 不进 AR 工作区代码 / 不动用户原话

防失败模式（user 5/7 钦定 — "几乎只是把仓库复制了一半"）：
不抄源码 schema / 不重列 wire 字段表 / 不重画 SSOT 已有的图。
允许：引用 SSOT §X + 一句话使用方式 + 跨模块 binding mermaid (≤ 15 行)。

提问纪律（§7）：
- 应该问 user：Task 1 代码现状对账表中如发现 ratified 但 Interface 漏写的能力是否补到 doc / 主 doc mermaid 是否要画
- 不应该问：协议字段（去 protocol_snapshot_p4）/ NEED-* 细节（去 cross_chat_pending_registry）/ 已交付内部接口（去完成报告）

成功判据：
- Task 1 对账表 ≤ 80 行 + 12 TODO 标签 grep 一一对应
- Task 2 patch ≤ 5 行/doc
- Task 3 主 doc 8 场景每个 5 元素填齐 + ≥ 30 SSOT 锚点
- Task 4 audit 6 检查项写到主 doc 末尾
- pytest collect-only 显示 415+ 项（守护项 0 漂移）

如发现某场景必须改 wire / 发明新模块 → 在 doc 标 BLOCKED-BY-NEW-ADR + 引用对应 NEED 标签；
不当场设计 ADR。

开始读 §2 入场必读项 1（本文件）。
```

---

## §7 提问纪律

✅ **应该问 user**：
- Task 1 代码现状对账表中发现「ratified 但 Interface 漏写」的能力，是否值得补到 Task 3 主 doc 8 场景里
- Task 3 §3 跨模块 binding 总表是 mermaid 还是 ASCII（user 偏好）
- 4-scope BB namespace audit 在 Task 3 §3 写到什么粒度（全表 26 keys / 仅 4 active key）
- Sub-Chat A 完成后是否要 wait Sub-Chat B 再合并（建议各自独立交付，互引用）

❌ **不应该问 user**：
- 任何 NEED-* 标签的细节（去 `cross_chat_pending_registry §3 / §4`）
- 任何已交付能力的内部接口（去 3 完成报告 §1 / §3）
- 任何协议字段（去 `protocol_snapshot_p4` 28 章）
- 模块边界（去 `module_map_p4_snapshot` §2）
- DSG 决策（去 `dsg_decisions_master` ratified 条目）
- AR 用户视角（Sub-Chat A 范围）

---

## §8 变更日志

- **2026-05-07 v2**：本文创建。replace v1（保留作历史）。新增：工作区域硬边界 / 代码先行 / DSG 工作区文档 drift 修复 / 工作区完整性 audit；输出从 1 份扩到 3 份（1 主 + 2 patch）；防失败模式硬规则（user 5/7 钦定）。
- **2026-05-07 v2.1（增量注脚）**：§1 加 MemoryValidity P3 占位注脚（canvas 菜单层声明；backend 不实现；新 NEED-P3-FILTER + NEED-P3-VALIDITY 同步登记至 `cross_chat_pending_registry §4.I / §4.J`）。不影响 §3 4 任务结构。
- **2026-05-07 v2.2（build mode）**：scope 升级为 Build — 允许在本 chat 写代码完成菜单后端接口化、4-scope BB 升级、IntentWorkspace 完成、L2-B baseline 真算法（用户钦定 S2 + L2 baseline real）。落地清单见 `architecture/backend_interface_refinement_20260507.md §0`。仍不动 wire / cs_parity / Phase 4 §8 锁；Plan UI / Obsidian 3 子类 / 多 SceneType profile / GAT-PPR / 4 类块 unified registry 仍推后续 chat。