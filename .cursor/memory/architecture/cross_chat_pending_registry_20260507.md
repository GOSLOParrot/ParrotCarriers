---
status: ratified
category: cross-chat-registry
status_note: "跨 chat 待办登记表 — 三大 chat（基建+ECP / DSG Chat 2 / GOSLO 模块化）完成后的统一 TODO + NEED 标签登记。任何源码 TODO 标签 + 任何下游 chat 入场 prompt 的'前瞻性需求'清单都从这里取词；本表是真源。"
last_reviewed: 2026-05-07
authoritative_for: "TODO 标签命名规则 / 严重度分级 / 修复 chat 路径 / 真源 doc 链接 / 代码触点 grep 标签"
parent_doc: "../INDEX.md"
sources:
  - "dsg/dsg_l1_5_implementation_completion_20260506.md §9.1 (DSG Chat 2 骨架 finding)"
  - "goslo_modularization_completion_20260506.md §4 (GOSLO mod 残余 + deferred)"
  - "goslo_modularization_residual_debt_20260506.md §2 + §4 (parrot-isms 7 类 + p2.5/p3 前瞻需求)"
  - "sprint4_phase4_entry_20260430.md §8 (Phase 4 决策锁)"
related:
  - "active_context.md (当前阶段)"
  - "INDEX.md (全局真相源)"
---

# 跨 Chat 待办登记表（Cross-Chat Pending Registry）

> **本文用途**：三大 chat 完成后的统一 TODO + NEED 标签真源。
>
> **三大 chat 范围**（按时间顺序）：
> 1. **Sprint4 主线**（基建 + 协议 v1 + ECP + Reflex + Scheduler 主路由）— 2026-04 系列收口
> 2. **DSG Chat 2**（DSG L1.5 + L2-B + IntentEvent + Plan + Archive + IntentWorkspace + Triggers V2）— 2026-05-06 收口
> 3. **GOSLO 模块化**（ModelManifest + IParrotController + animate/fly_to model_id + AI CLI）— 2026-05-06 收口
>
> **使用方式**（grep 友好）：
> - 源码 TODO：`rg "TODO\(Chat4-"` / `rg "NEED-P2\.5-"` / `rg "NEED-P3-"`
> - 下游 chat 入场：直接读本表 §3 → §4 → §5 找到对应任务
> - 真源 doc 引用：每行带 `source: <doc> §X` 锚点

---

## §0 标签命名规则

| 前缀 | 含义 | 修复时机 |
|:--|:--|:--|
| **`TODO(Chat4-*)`** | DSG Chat 2 骨架代码留给 Chat 4（接口提炼实施）的"完整实现"占位 | Chat 4（接口提炼实施）|
| **`TODO(P3-*)`** | DSG Chat 2 骨架留给 P3 仿生升级 / A10 chat 的"非桌面 baseline"占位 | P3 仿生升级 / A10 接入 chat |
| **`NEED-P2.5-*`** | 跨 chat 共识的 P2.5 阶段需求（Sprint 0-4 之内 + 真机 spike 之前）| 对应主题 chat（详见 §3）|
| **`NEED-P3-*`** | 跨 chat 共识的 P3 阶段需求（菜单画布 / 多模型 / 仿生升级 / wire 解锁）| 对应主题 chat（详见 §4）|

> **关键约束**：所有 NEED-* 标签**不直接打到源码**（仅在文档登记 + 在 chat 启动 prompt 引用）。
> 源码注释只用 `TODO(Chat4-*)` / `TODO(P3-*)` 两类（精确到代码触点 + 一句话说明）。

---

## §1 严重度分级

| 级别 | 含义 | 例 |
|:--|:--|:--|
| **🔴 high** | 阻塞核心场景（"非鹦鹉模型也能跑"）/ 阻塞下游 chat 实施 | NEED-P2.5-A persona 外置（换模型 LLM 嗓音不变）|
| **🟡 mid** | 功能受限但 baseline 能跑 / 测试覆盖率 incomplete | NEED-P2.5-PLAN-DISPATCH（Plan 派发 NanobotTask 真路径）|
| **🟢 low** | 命名 / 品牌化 / 优化 / 占位 | TODO(P3-attention-spreading) Spreading Activation 真迭代 |

---

## §2 标签全表（grep 索引）

### §2.1 DSG Chat 2 骨架代码 TODO（已落到源码）

| 标签 | 严重度 | 真源 doc | 代码触点 |
|:--|:--|:--|:--|
| `TODO(Chat4-archive-llm)` | 🟡 | [`dsg/dsg_l1_5_implementation_completion_20260506.md §9.1 F-1`](dsg/dsg_l1_5_implementation_completion_20260506.md) | `src/parrot/dsg/archive/conversation.py:archive_to_graphiti` |
| `TODO(Chat4-nanobot-heartbeat)` | 🟡 | 同上 F-2 | `src/parrot/dsg/triggers/idle_archive_trigger.py:_is_nanobot_idle` |
| `TODO(Chat4-plan-dispatch)` | 🟡 | 同上 F-3 | `src/parrot/brain/plan/plan_registry.py:start_executing` + `submit_for_confirmation` |
| `TODO(Chat4-disk-recover)` | 🟢 | 同上 F-5 | `src/parrot/brain/intent_workspace_backend.py:DiskBackend` |
| `TODO(P3-Wire-PlanUI)` | 🟡 | 同上 F-4 | `src/parrot/brain/plan/plan_registry.py:submit_for_confirmation` |
| `TODO(P3-RefHealth)` | 🟢 | 同上 F-6 | `src/parrot/dsg/l1_5/ref_table.py:verify_ref` |
| `TODO(P3-attention-spreading)` | 🟢 | 同上 F-7 | `src/parrot/dsg/l2b/attention/mechanism.py:SpreadingActivationPlaceholder` |
| `TODO(P3-fold-bionic)` | 🟢 | 同上 F-8 | `src/parrot/dsg/l2b/intent_event_boundary.py:NoOpFoldStrategy` |
| `TODO(P3-multi-scene)` | 🟢 | 同上 F-9 | `src/parrot/dsg/l1_5/scene_snapshot.py:SceneRegistry` |

### §2.2 跨 chat 重叠区 TODO（本登记表 pass 新增）

| 标签 | 严重度 | 真源 doc | 代码触点 |
|:--|:--|:--|:--|
| `TODO(Chat4-plan-nanobot-correlation)` | 🟡 | 本表 §3.B | `src/parrot/scheduler/nodes.py:DispatchToNanobot` + `service.py:_listen_nanobot_results` |
| `TODO(Chat4-plan-step-result-route)` | 🟡 | 本表 §3.B | `src/parrot/scheduler/service.py:_listen_nanobot_results` |
| `TODO(Chat4-plan-step-timeout)` | 🟡 | 本表 §3.B | `src/parrot/scheduler/service.py:_check_timeouts` |
| `TODO(Chat4-plan-bb-namespace)` | 🟢 | 本表 §3.B | `src/parrot/scheduler/blackboard.py` |

### §2.3 GOSLO 模块化残余 / 前瞻需求（doc-only NEED 标签）

详见 §3 / §4，不直接打到源码（避免代码注释膨胀；下游 chat 启动时按主题 grep 本表）。

---

## §3 P2.5 需求清单（NEED-P2.5-*）

> P2.5 = Sprint 0-4 之内 + 真机 spike 之前 + 不破 Phase 4 § 8 锁 的"现阶段就该补"。

### §3.A NEED-P2.5-A：Brain LLM persona 文件外置 🔴 high

**真源**：[`goslo_modularization_residual_debt_20260506.md §2.1 #1`](goslo_modularization_residual_debt_20260506.md) + [`goslo_modularization_completion_20260506.md §4.1 D-1`](goslo_modularization_completion_20260506.md)

**问题**：`brain/soul.py` 的 `CORE_INSTRUCTIONS` / `COMPANION_INSTRUCTIONS` / `PLAYFUL_INSTRUCTIONS` 内联硬编码鹦鹉味儿。换非鹦鹉模型时 LLM 嗓音不变（"You are Parrot... shoulder perching... squawk"），与视觉严重不匹配。

**修法**：
1. 把 `CORE_INSTRUCTIONS` + 各 mode 段抽到外部 `src/parrot/brain/personas/<persona_id>.md`（或 `.toml`）
2. 加载器 `parrot.brain.persona_loader.load(persona_id)`
3. BB key `global/active_persona_id`，默认 `goslo_parrot_default`（旧文本原样搬，0 漂移）
4. **持久层**：与 [`NEED-P3-B`](#§4b-need-p3-b：4-类块注册表) 4 类块的"设定块"统一 — 推荐和 NEED-P3-B 一起做

**修复 chat 候选**：DSG 协议升级 chat（与 Plan-Persona-Mode-Scene 4 类块统一设计）

**已确认 deferred**（user 2026-05-06 sign off）：留 p3 菜单画布 chat 与 4 类块一起做，避免半成品 schema。

### §3.B NEED-P2.5-PLAN-INTEGRATION：Plan ↔ Scheduler ↔ Nanobot 完整路径 🟡 mid

**真源**：[`dsg/dsg_l1_5_implementation_completion_20260506.md §9.1 F-3`](dsg/dsg_l1_5_implementation_completion_20260506.md) + 本表 §2.2

**问题**：DSG Chat 2 的 `PlanRegistry.start_executing` 仅标 `step.state = DISPATCHED`，**未调** `do_dispatch_task` 真派发到 Nanobot；NanobotTask result 回流到 `Scheduler._listen_nanobot_results` 后**未路由**给 `PlanRegistry.report_step_result`。

**修法**：
1. `PlanRegistry.start_executing` 真调 `do_dispatch_task(task_type=step.expected_tool, params={...plan_id, step_id, result_channel}, priority="normal")` → 拿 task_id 存到 `step.nanobot_task_id`
2. `dispatch_task.do_dispatch_task` 接受 `plan_id` / `step_id` 元数据透传到 Redis Stream payload
3. `scheduler/nodes.py:DispatchToNanobot` 把 `plan_id` / `step_id` 写入 `active_tasks[task_id]`（Blackboard `scheduler/active_tasks`）
4. `scheduler/service.py:_listen_nanobot_results` 从 active_tasks 取出 `plan_id` / `step_id`，调 `PlanRegistry.report_step_result(plan_id, step_id, success=...)` 路由
5. `scheduler/service.py:_check_timeouts` 同样路径，路由 `success=False, error="timeout after Ns"`

**修复 chat**：Chat 4（接口提炼实施）

**代码 TODO 标签**：
- `TODO(Chat4-plan-dispatch)` — 已存在于 plan_registry.py
- `TODO(Chat4-plan-nanobot-correlation)` — 本 pass 加到 scheduler/nodes.py + service.py
- `TODO(Chat4-plan-step-result-route)` — 本 pass 加到 service.py
- `TODO(Chat4-plan-step-timeout)` — 本 pass 加到 service.py

### §3.C NEED-P2.5-NANOBOT-HEARTBEAT：nanobot heartbeat 写者 🟡 mid

**真源**：[`dsg/dsg_l1_5_implementation_completion_20260506.md §9.1 F-2`](dsg/dsg_l1_5_implementation_completion_20260506.md)

**问题**：`IdleArchiveTrigger._is_nanobot_idle` 读 Redis HASH `parrot:nanobot_heartbeat`，但写者（nanobot worker 周期 HSET）未实施。

**修法**：在 `parrot.bus.nanobot_consumer` 或 `nanobot/channels/parrot_bus.py` 心跳循环内加 `HSET parrot:nanobot_heartbeat <worker_id> <ts>` 周期写入（建议 60s 一次）。

**修复 chat**：Chat 4（接口提炼实施）/ 或独立 nanobot 协作 chat

### §3.D NEED-P2.5-ARCHIVE-LLM：Phase 3 LLM 蒸馏 → Graphiti 🟡 mid

**真源**：[`dsg/dsg_l1_5_implementation_completion_20260506.md §9.1 F-1`](dsg/dsg_l1_5_implementation_completion_20260506.md)

**问题**：`dsg.archive.conversation.archive_to_graphiti` 仅计数 episode rows，真 LLM 蒸馏 + `Graphiti.add_episode` 未连。

**修法**：
1. 读取 `episodes.jsonl` + 关联节点
2. 调 `unified_filter.filter(node, ctx)` → KEEP/SKIP/SUMMARIZE
3. 调 LLM（Gemini Flash）蒸馏 episode summary
4. 调 `L2BGraph.archive_episode_to_graphiti` 真写 Graphiti（既有方法已就位，只是不再被 start_episode 直接调）
5. 标 `metadata.json` 的 `archived_to_graphiti=True`

**修复 chat**：Chat 4（接口提炼实施）

### §3.E NEED-P2.5-B：Unity menu 暴露 DSG bucket / scene 切换 🟡 mid

**真源**：[`goslo_modularization_residual_debt_20260506.md §4.1`](goslo_modularization_residual_debt_20260506.md)

**问题**：DSG 后端能力齐全（`BucketRegistry` + `SceneRegistry` + `BucketOpKind`），但 Unity menu 端无 UI 入口让用户切换。

**修法**：Unity menu 加 DSG bucket / scene 选择面板 → EcpCommand → Brain → L1.5 Pool。

**修复 chat**：AR 工作区独立 chat（菜单 UI 范围）/ 或与 NEED-P3-D 一起做

---

## §4 P3 需求清单（NEED-P3-*）

> P3 = Sprint 5+ / 真机 spike 之后 / 涉及 wire ADR / 涉及大改架构。

### §4.A NEED-P3-A：EcpFrontendState body_state 解锁评估 🟡 mid

**真源**：[`goslo_modularization_residual_debt_20260506.md §2.2 #2`](goslo_modularization_residual_debt_20260506.md) + [`goslo_modularization_completion_20260506.md §4.2 D-2`](goslo_modularization_completion_20260506.md)

**问题**：`ParrotBodyState` enum 5 项 wire 锁（`idle / flying / perching / dancing / frozen`），仅适合鸟类；非鸟模型上报粒度变粗。

**修法 Option A**（保守，推荐先走）：保留 5 项 wire，加 `EcpFrontendState.controller_body_state: str` 自由字段；Brain LLM 通过 `attach_state_header` 看 controller_body_state；旧 `body_state` 走粗粒度兼容。
**修法 Option B**（激进）：升级 `body_state` 为自由 string；旧 5 项变"标准方言"。

**约束**：触动 Phase 4 § 8 wire schema 锁 → **必须新 ADR + cs_parity 全过**。

**修复 chat**：P3 wire 升级 ADR chat

### §4.B NEED-P3-B：4 类块注册表（模型 / 设定 / 模式 / 场景）🔴 high

**真源**：[`goslo_modularization_residual_debt_20260506.md §4.3`](goslo_modularization_residual_debt_20260506.md)

**问题**：当前 4 类块各自 ad-hoc：
- 模型块（Model）：✅ 已有 `ModelManifest` + `model_id`
- 设定块（Persona）：❌ 未抽离（NEED-P2.5-A）
- 模式块（Mode）：✅ 已有 `BehaviorMode` flags + `set_mode` tool
- 场景块（Scene）：✅ 已有 `SceneType` + `SceneProfile` + `SceneRegistry`

**修法**：每类块需要：
1. ID 命名空间 + 注册表
2. 文件 / 数据格式（manifest / persona / config）
3. 加载器
4. active BB key（`global/active_model_id` / `global/active_persona_id` / `global/active_mode` / `global/active_scene`）
5. 切换事件 / 通知

**修复 chat**：DSG 协议升级 chat（4 类块统一接口设计）/ 与 NEED-P2.5-A 同时做

### §4.C NEED-P3-C：预设 = 4 active ID 命名快照 🟡 mid

**真源**：[`goslo_modularization_residual_debt_20260506.md §4.3`](goslo_modularization_residual_debt_20260506.md)

**问题**：用户希望"进房间选预设来启动" — 当前无预设 schema。

**修法**：定义 `data/presets/<preset_id>.json` schema：
```json
{
  "preset_id": "default",
  "active_model_id": "GOSLO_default",
  "active_persona_id": "goslo_parrot_default",
  "active_mode": ["BASE", "COMPANION"],
  "active_scene_id": "main_scene"
}
```

**修复 chat**：DSG 协议升级 chat（与 NEED-P3-B 一起）

### §4.D NEED-P3-D：Unity menu UI = node-canvas 🟢 low

**真源**：[`goslo_modularization_residual_debt_20260506.md §4.3`](goslo_modularization_residual_debt_20260506.md)

**问题**：用户希望菜单是节点画布（ComfyUI / n8n / Unreal Blueprint 风格）。

**修法**：Unity 端 ScriptableObject 接口约定 + 节点画布 UI（用 GraphView API 或自研）。

**修复 chat**：AR 工作区独立 chat（菜单 UI 范围）

### §4.E NEED-P3-E：默认菜单 fallback 🟢 low

**真源**：[`goslo_modularization_residual_debt_20260506.md §4.3`](goslo_modularization_residual_debt_20260506.md)

**问题**：节点画布是高级用户向；普通用户需要"列表选择 + 保存预设 + 恢复默认"兼容路径。

**修复 chat**：AR 工作区独立 chat（与 NEED-P3-D 配套）

### §4.F NEED-P3-CAPABILITY-GATING：tool 暴露按 manifest capability 过滤 🟡 mid

**真源**：[`goslo_modularization_residual_debt_20260506.md §2.2 #3`](goslo_modularization_residual_debt_20260506.md) + [`goslo_modularization_completion_20260506.md §4.2 D-3`](goslo_modularization_completion_20260506.md)

**问题**：`fly_to` 动词暗示会飞；非飞行模型（人形）调用 `fly_to` 仍触发 `Fly` capability，视觉违和。

**修法**：Brain Agent 启动时读 active model manifest 的 `declared_capability_ids`，**只把 model 实现的动作对应的 tool 注册给 LLM**。例：active model 不声明 `fly` → `fly_to` tool 不注册 → LLM 不会调用。

**架构涉及**：Brain 端需 `ModelManifestRegistry` 副本（GOSLO Step 3 已加 `model_id` 参数但未加 registry）。

**修复 chat**：Chat 4 增量（轻量，5-15 行 + 1 测试）/ 或 P3 chat（与多模型路由一起做）

### §4.G TODO(P3-Wire-PlanUI)：Plan 用户确认 wire 信号 🟡 mid

**真源**：[`dsg/dsg_l1_5_implementation_completion_20260506.md §9.1 F-4`](dsg/dsg_l1_5_implementation_completion_20260506.md)

**问题**：Plan 用户确认信号（`AWAITING_USER_CONFIRMATION → APPROVED`）当前由调用方直接 `approve()`，真 EcpEvent UI / EcpCommand 回流未实施。

**修法**：
1. 新 `EcpEventType.PLAN_PROPOSED`（Brain → Unity 渲染 Plan UI）— **触动 Phase 4 § 8 wire 锁，需新 ADR**
2. Unity DTO + Plan card UI（Mermaid / Gantt / step list / approve button）
3. `EcpCommand.APPROVE_PLAN` / `REJECT_PLAN` / `CANCEL_PLAN` / `REVISE_PLAN` 回流
4. Brain RPC bridge 接收用户决策

**修复 chat**：P3 wire 升级 ADR chat（与 NEED-P3-A 同 ADR）

### §4.H 其他 P3 占位（已落源码 TODO）

| 标签 | 真源 | 代码触点 |
|:--|:--|:--|
| `TODO(P3-fold-bionic)` | DSG Chat 2 §9.1 F-8 | l2b/intent_event_boundary.py:NoOpFoldStrategy |
| `TODO(P3-attention-spreading)` | F-7 | l2b/attention/mechanism.py |
| `TODO(P3-RefHealth)` | F-6 | l1_5/ref_table.py:verify_ref |
| `TODO(P3-multi-scene)` | F-9 | l1_5/scene_snapshot.py:SceneRegistry |

---

## §5 修复 chat 路径汇总

| 修复 chat | 处理标签 |
|:--|:--|
| **Chat 4（接口提炼实施）** | NEED-P2.5-PLAN-INTEGRATION（4 个 TODO(Chat4-plan-*)）+ NEED-P2.5-NANOBOT-HEARTBEAT + NEED-P2.5-ARCHIVE-LLM + TODO(Chat4-archive-llm) + TODO(Chat4-disk-recover) + 可选 NEED-P3-CAPABILITY-GATING（轻量增量）|
| **DSG 协议升级 chat（菜单画布主线）** | NEED-P2.5-A（persona 外置）+ NEED-P3-B（4 类块注册表）+ NEED-P3-C（预设 schema）|
| **AR 工作区独立 chat（菜单 UI）** | NEED-P2.5-B（DSG bucket/scene UI）+ NEED-P3-D（node-canvas UI）+ NEED-P3-E（默认 fallback）|
| **P3 wire 升级 ADR chat** | NEED-P3-A（body_state 解锁）+ TODO(P3-Wire-PlanUI)（Plan UI wire）— 建议同 ADR |
| **P3 仿生升级 chat** | TODO(P3-fold-bionic) + TODO(P3-attention-spreading) + TODO(P3-RefHealth) |
| **P3 / A10 接入 chat** | TODO(P3-multi-scene)（多 SceneType profile）|
| **独立 nanobot 协作 chat** | NEED-P2.5-NANOBOT-HEARTBEAT（与 Chat 4 替代路径）|

---

## §6 grep 速查

```
# 全部 DSG Chat 2 骨架 TODO（Chat 4 应处理）
rg "TODO\(Chat4-" src/

# 全部 DSG Chat 2 骨架 TODO（P3 应处理）
rg "TODO\(P3-" src/

# 全部跨 chat 重叠区 TODO（本 pass 新增，Chat 4 应处理）
rg "TODO\(Chat4-plan-" src/parrot/scheduler/

# 全部 doc-only 前瞻需求（按 chat 分组）
rg "NEED-P2\.5-" .cursor/memory/architecture/
rg "NEED-P3-" .cursor/memory/architecture/
```

---

## §7 维护规则

1. **新 chat 启动时**：把本表 §5 对应该 chat 的标签一行行抄到 chat 启动 prompt §1 入场必读。
2. **chat 实施完成时**：把已 close 的标签从本表 §3 / §4 转移到 §8 历史区（不删，只标 `✅ resolved-by <chat doc>`）。
3. **新增标签**：先在本表 §2 加索引行 + §3 / §4 加详情，再去源码加 TODO 注释（保证 grep 一一对应）。
4. **改 wire / 改 enum / 改 namespace**：先回查 [Phase 4 § 8 锁](sprint4_phase4_entry_20260430.md) → 必须新 ADR → ADR 落地后才更新本表。

---

## §8 已 resolved 历史

（本表创建时为空。chat 实施完成后逐条 archive。）

---

## §9 引用

- DSG Chat 2 完成报告：[`dsg/dsg_l1_5_implementation_completion_20260506.md`](dsg/dsg_l1_5_implementation_completion_20260506.md)
- GOSLO 模块化完成报告：[`goslo_modularization_completion_20260506.md`](goslo_modularization_completion_20260506.md)
- GOSLO 残余债审计：[`goslo_modularization_residual_debt_20260506.md`](goslo_modularization_residual_debt_20260506.md)
- GOSLO Manifest 协议 v1：[`goslo_model_manifest_protocol_v1.md`](goslo_model_manifest_protocol_v1.md)
- Phase 4 § 8 决策锁：[`sprint4_phase4_entry_20260430.md`](sprint4_phase4_entry_20260430.md)

---

## §10 变更日志

- **2026-05-07**：本表创建。三大 chat（Sprint4 + DSG Chat 2 + GOSLO 模块化）完成后的统一 TODO + NEED 标签登记。覆盖 13 个标签（DSG Chat 2 落源码 9 + 跨 chat 新增 4），4 个 P2.5 NEED + 8 个 P3 NEED，6 条修复 chat 路径。
