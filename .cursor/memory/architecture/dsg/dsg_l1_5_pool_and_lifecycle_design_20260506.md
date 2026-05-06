---
status: draft
category: design-doc
status_note: "DSG L1.5 池 + Lifecycle 差异化 + L2-B 简单升级 + IntentWorkspace + Plan 协议主设计稿。Chat 2 主交付物。锁名词、锁模块边界、引用 8 份协议文档展开细节。"
last_reviewed: 2026-05-06
ai_priority: high
ai_audience: "DSG Chat 2 实施 chat / 独立审计 chat / 后续 P3 仿生升级 chat"
parent_doc: "workspace_index.md"
parent_dispatch: "../sprint4_phase4_downstream_chat_dispatch_plan_20260504.md §1.1 Chat 2"
related:
  - "dsg_decisions_master.md"
  - "dsg_current_state_distilled.md"
  - "../adr_l1_5_source_dispatch_extension_space_20260504.md"
  - "../sprint4_phase4_entry_20260430.md"
  - "../../parrot_behavior_rules.md"
companion_protocols:
  - "dsg_protocol_pool_v1_20260506.md"
  - "dsg_protocol_trigger_v2_20260506.md"
  - "dsg_protocol_intent_event_boundary_v1_20260506.md"
  - "dsg_protocol_archive_v1_20260506.md"
  - "dsg_protocol_scene_snapshot_v1_20260506.md"
  - "brain_protocol_intent_workspace_v1_20260506.md"
  - "brain_protocol_plan_v1_20260506.md"
---

# DSG L1.5 池 + Lifecycle + L2-B 简单升级 + IntentWorkspace + Plan — 主设计稿

> **本文用途**：Chat 2 主交付物。建立**模块边界 / 命名 / 全局 invariants / 协议引用关系**。具体协议细节在 8 份 companion 文档展开。
>
> **任务定位**（用户原话 2026-05-06）：
> > 写**接口和协议**，而不是完成全部设计。架构扩展性需要够大，完成能力接口、一些验证功能，来验证协议有接口能力覆盖我们的需求。
>
> 因此本文与 7 份协议 + 完成报告**优先输出 API surface + protocol contracts + 验证测试**；具体仿生算法、衰减公式、PPR/Spreading Activation 全实现都**留 P3**。

---

## §0 官方术语表（**所有文档头部原样植入，禁止冲突命名**）

### §0.1 5 个独立概念（防混淆）

| 中文 | **官方名称** | 触发源 | 主存储 | 节点字段 / 持有者 | 持续期 |
|:--|:--|:--|:--|:--|:--|
| 场景类型（preset） | **`SceneType`** | `set_scene` tool / 手机传感器（P3）/ VPS（P3） | L1.5 `SceneRegistry` + `SceneProfile` | Node `scene_type: str`（informational） | 跨 session（物理设定） |
| 物理位置 | **`LocationTag`** | 用户 / 检测 / VPS（P3） | Node 字段 | Node `location_tag: str`（informational） | 跨 session（物理布局） |
| 对话段（既有） | **`Episode`** | `manage_episode` tool（start / close） | L2-B `EpisodeMarker` | Node `episode_id: str` | per-session |
| 认知边界（**新**） | **`IntentEvent`** | tool call / nanobot result / long idle / explicit | L2-B `IntentEventBoundaryHandler` + Compartment | Node `event_id: str` | 1+ per Episode |
| 计划（**新**） | **`Plan`** | GOSLO Intent 阻塞对话期间制定 | **IntentWorkspace**（主）+ L2-B 镜像 | Node 镜像走 `NodeKind.EVENT` + `source_meta.plan_role` | per IntentEvent |
| 计划步骤 | **`PlanStep`** | Plan 创建时分解 | IntentWorkspace（Plan 内部）+ L2-B 镜像 | 同上 | per Plan |
| 异步任务（既有） | **`NanobotTask`** | `dispatch_task` tool（fire-and-forget） | Scheduler + Nanobot | Redis Stream + result channel | per task |
| L1.5 桶 | **`Bucket`**（L1.5 域专用，不出现在 L2-B） | 触发器导入 / 用户切换 | L1.5 `BucketRegistry` | L1.5 内部映射 + Node `bucket_id: str` | 跨 session |
| L2-B 拓扑分组 | **`Compartment`**（L2-B 域专用，不出现在 L1.5） | EventBoundaryHandler / view_by_* | L2-B `compartments.py`（视图） | 不存数据，是 lazy view | 计算时存在 |

### §0.2 命名硬规则（违反 → `test_terminology_no_collision.py` fail）

1. **`Event` 永远写 `IntentEvent` 全名**（防与 `Episode` / `NanobotTask` 混）
2. **`Scene` 单写默认 `SceneType`**（指物理位置时必须写 `LocationTag`）
3. **`Task` 单写默认 `NanobotTask`**（指 Plan 内子单位时必须写 `PlanStep`）
4. **`Bucket`** = L1.5 专用，**不出现**在 `parrot.dsg.l2b/`
5. **`Compartment`** = L2-B 专用，**不出现**在 `parrot.dsg.l1_5/`
6. 既有 `Episode` / `EpisodeMarker` / `episode_id` / `dispatch_task` **不重命名**（向后兼容）

### §0.3 层级总图

```
Episode (Gemini conversation segment, per-session)
└── IntentEvent  (GOSLO cognitive focus window, 1+ per Episode)
    └── [可选] Plan  (Plan-and-Execute 模式；存于 IntentWorkspace，镜像到 L2-B)
        ├── PlanStep × N  (Plan 内部分解)
        │   └── NanobotTask × M  (部分 PlanStep 派发为异步任务)
        └── PlanBlackboard  (py-trees BB 子命名空间 plan/{plan_id}/*)

横切：
  SceneType     informational tag, 跨 Episode
  LocationTag   informational tag, 跨 Episode
  Bucket (L1.5) 跨 IntentEvent / 跨 Episode（永久权威桶跨 SceneType）
  Compartment   per-IntentEvent / per-Bucket / per-SceneType view
```

---

## §1 范围 + 元约束

### §1.1 In scope（本 chat 必产）

参考 [launch prompt §2.1](dsg_l1_5_pool_design_chat_launch_prompt_20260506.md)：

- **A** L1.5 预加载 Node 池（[`dsg_protocol_pool_v1`](dsg_protocol_pool_v1_20260506.md)）
- **B** 状态生命周期差异化（同上 + lifecycle policy strategy）
- **C** L2-B 简单升级（Compartment view + IntentEventBoundary，[`dsg_protocol_intent_event_boundary_v1`](dsg_protocol_intent_event_boundary_v1_20260506.md)）
- **D** 工作记忆延迟归档（[`dsg_protocol_archive_v1`](dsg_protocol_archive_v1_20260506.md)）
- **E** 触发器协议升级 V2（[`dsg_protocol_trigger_v2`](dsg_protocol_trigger_v2_20260506.md)）
- **F** Scene 切换协议（[`dsg_protocol_scene_snapshot_v1`](dsg_protocol_scene_snapshot_v1_20260506.md)）
- **G** Brain Intent 层资源暂存（[`brain_protocol_intent_workspace_v1`](brain_protocol_intent_workspace_v1_20260506.md)）
- **H** Plan-and-Execute 协议（[`brain_protocol_plan_v1`](brain_protocol_plan_v1_20260506.md)）

### §1.2 Out of scope（**本 chat 不做**）

| 项 | 推到哪 | 锚点 |
|:--|:--|:--|
| A10 详细接入（CV Flow / SAM2 / DINOv2 / ConceptGraph） | P3 / A10 独立 chat | [master §6](dsg_decisions_master.md) |
| AR 坐标 + 手机传感器 + VPS + 软件建图 | P3 | 同上 |
| MemoryValidity Ebbinghaus 衰减公式 | P3 | [`module_map_p2 §11.2`](../module_map_p2.md) |
| 不可能事件 / 同类第二实例规则 | P3 | [master §1.2](dsg_decisions_master.md) |
| 完整仿生算法（PPR / Spreading Activation / 注意力衰减实数 / GAT 训练） | P3+ | [`dsg-rustworkx-master §3`](../../../skills/dsg-rustworkx-master/SKILL.md) |
| 完整 Compartment 折叠机制 | P3+ | 本文 §3.4 留接口 |
| Unity wire 字段动 | **永不**（ADR-L1.5-001 Q1）| [master §M5](dsg_decisions_master.md) |
| Plan 显示给用户 / 用户确认 Plan 的 EcpEvent 字段 | wire 升级独立 chat（P3）| 本文 §3.6 留接口锚点 |
| RichReport 富文本 / mermaid / 跳转按钮的 Unity 渲染 | 同上（wire 升级）| 同上 |

### §1.3 元约束（链接 [master §0](dsg_decisions_master.md)）

- **M1** 桌面场景优先；其他场景具体场景具体设计
- **M2** 不过度消耗注意力；优先用 4 新 DSG skill 选项库
- **M3** 注意力路径**字段层 + RustworkX 机制层混合**，不预选单一
- **M4** L1.5 ↔ L2 调研后审窗口（master `provisional-revisit-after-L2-design` 条目本 chat sign-off 后回审）
- **M5** 不动 Phase 4 §8 决策锁 / ADR-L1.5-001 §4.1 升级条件 / `parrot_behavior_rules §3.7` Observer-Attention 边界

---

## §2 模块布局

### §2.1 新模块清单

```
src/parrot/dsg/l1_5/                       【新子包】L1.5 管理面（不持有节点）
├── __init__.py                            公开 API：admit / lookup / bucket_ops / scene ops
├── pool.py                                L15Pool 类（singleton）— 元数据管理面
├── buckets.py                             Bucket / BucketKind / BucketRegistry / BucketSpec
├── admission.py                           PoolAdmissionPolicy strategy + DesktopPolicy baseline
├── ref_table.py                           UUID 绑定表（轻量）+ Ref 健康度
├── timeline.py                            时间轴元数据 — 仅事件边界标注
└── scene_snapshot.py                      Scene 切换快照元数据 + 序列化触发协议

src/parrot/dsg/l2b/                        【新子包】L2-B 工作记忆图（节点本体）
├── __init__.py                            facade — 转发既有 l2b_graph.py
├── graph.py                               L2BGraph（升级版，单 PyDiGraph）
├── compartments.py                        Compartment view + cross-compartment edge 标记
├── intent_event_boundary.py               IntentEventBoundaryHandler — 标签 + 降权 baseline
├── views.py                               view_by_compartment / event / bucket / scene / kind
└── attention/
    ├── threshold.py                       【既有，不动】Phase 4 W6-7
    ├── hint_writer.py                     【既有，不动】Phase 4 F-05
    ├── decay.py                           【新】AttentionDecayPolicy strategy（默认 noop）
    └── mechanism.py                       【新】AttentionMechanism strategy（4 算法 + 限深 BFS baseline）

src/parrot/dsg/archive/                    【新子包】对话延迟归档
├── __init__.py
├── conversation.py                        ConversationArchive — 序列化 schema + 硬盘队列
└── boundary.py                            ConversationBoundaryDetector — 多信号 OR

src/parrot/dsg/triggers/                   【既有，升级】
├── base.py                                【改】TriggerOutcome 替代 TriggerResult（alias 兼容）
├── runner.py                              【改】_process_result 加 5 路上行处理
├── scene_switch_trigger.py                【新】set_scene → bucket freeze + snapshot
├── intent_event_boundary_trigger.py       【新】tool call / idle → IntentEvent boundary
├── roleplay_mode_trigger.py               【新】roleplay 桶 register / clear
├── goslo_curiosity_trigger.py             【新】attention threshold + unknown → 主动 stage
├── idle_archive_trigger.py                【新】nanobot heartbeat idle → 归档管线
└── （既有 calendar / message / scene_context / ssot_enrichment 4 个保留）

src/parrot/dsg/ingest/                     【既有，少量改动】
├── base.py                                【改】+ ObservationSource.GOSLO_AUTONOMOUS
├── runner.py                              【改】走 L15Pool.admit；改 TODO(S4.B) 注释
├── autonomous_curiosity_filter.py         【新】GOSLO 主动好奇 → Observation
└── （既有 5 filter 不动）

src/parrot/brain/intent_workspace.py       【新】IntentWorkspace 单文件
src/parrot/brain/intent_workspace_backend.py 【新】Backend strategy（InMemory / Disk）
src/parrot/brain/plan/                     【新子包】Plan 模块
├── __init__.py
├── plan.py                                Plan / PlanStep / PlanState dataclass
├── plan_registry.py                       active plans + lookup
├── plan_blackboard.py                     py-trees BB 子命名空间 plan/{plan_id}/*
└── plan_lifecycle.py                      DRAFT → CONFIRMED → EXECUTING → DONE/FAILED
```

### §2.2 既有模块改动清单

```
src/parrot/dsg/l2b_types.py
  + bucket_id: str = "main"           (L1.5 Bucket tag)
  + scene_type: str = ""              (SceneType tag)
  + location_tag: str = ""            (LocationTag tag)
  + event_id: str = ""                (IntentEvent tag — 命名锁定写法)
  + 约定 source_meta["intent_workspace_ref"]   (string ref_id, 无强 schema)
  + 约定 source_meta["plan_role"]              ("plan_root" | "plan_step" | "" 默认)
  + 约定 source_meta["plan_id"]                (Plan 镜像节点的 plan_id)
  ※ NodeKind / EdgeKind 6+8 项 enum 完全不动（Phase 4 §8 L1）

src/parrot/dsg/l2b_graph.py
  → 改 facade，从 parrot.dsg.l2b.graph re-export get_l2b_graph 等符号
  → start_episode() 不再立即 create_task(archive_episode_to_graphiti)，改为 enqueue_for_idle_archive
  → archive_episode_to_graphiti 保留（idle archive 时 nanobot 调用）

src/parrot/dsg/ingest/runner.py
  → commit_observation 走 L15Pool.admit 而非直 _find_existing
  → TODO(S4.B) 注释改为：禁止当场写回；走 dsg_protocol_archive_v1 三阶段管线

src/parrot/dsg/triggers/base.py
  → TriggerResult 改为 TriggerOutcome（alias 保留）
  → 新增 5 路上行字段（commit_observations / bucket_ops / archive_request / staged_refs / plan_request）

src/parrot/dsg/triggers/runner.py
  → _process_result 加新 5 路 dispatch
```

### §2.3 模块责任边界（**严格 invariant**）

| 模块 | 持有什么 | 不持有什么 | 边界来源 |
|:--|:--|:--|:--|
| `dsg.l1_5.pool` | Bucket 元数据 / Ref 表 / Timeline / Scene Snapshot 元数据 / AdmissionPolicy | 节点本体 / 边 / 拓扑 | 用户原话："独立 Pool 的职责只有方便性能管理" |
| `dsg.l2b.graph` | 节点本体（SemanticNode）/ 边（SemanticEdge）/ RustworkX 拓扑 | Bucket 注册表 / Plan 主存 / 大文件 payload | Phase 4 §8 L1 + ADR-L1.5-001 |
| `dsg.l2b.compartments` | Compartment view 计算逻辑 | 数据（视图是 lazy） | 本文 §3.4 |
| `dsg.l2b.attention` | threshold + hint_writer + decay policy + mechanism strategy | 不抓帧 / 不写 Graphiti / 不塞 BB（threshold 模块）| Phase 4 §8 L9 + L13 + parrot_behavior_rules §3.7 |
| `dsg.archive` | 序列化 schema + 硬盘队列 + ConversationBoundary 检测 | 当场写 Graphiti | master §5 + dsg_protocol_archive_v1 |
| `brain.intent_workspace` | StagedRef 重量缓存（Brain Intent 层资源） | 节点 / 边 / Bucket | 用户原话："给 GOSLO Intent 层使用" |
| `brain.plan` | Plan / PlanStep / PlanBlackboard / PlanLifecycle | 节点本体（仅镜像）/ 大文件 payload（在 IntentWorkspace） | 用户原话："IntentWorkspace 为主，L2-B 读 IntentWorkspace" |
| `dsg.ingest.runner` | Observation → SemanticNode commit 唯一入口 | preload（Graphiti 自有节点 mirror，例外） | ingest/base.py docstring + master §1.2 |
| `dsg.triggers.runner` | 5 路上行 dispatch（commit / bucket_ops / archive / staged_refs / plan_request） | 直接读写 L2-B（必须经 IngestRunner） | base.py docstring 不变量 |

---

## §3 关键设计要点

### §3.1 L1.5 Pool（详见 [`dsg_protocol_pool_v1`](dsg_protocol_pool_v1_20260506.md)）

- **物理形态**：单 `L15Pool` singleton（per-process），**不持有节点**
- **桶**：`Main` / `ObsidianSettingDaily` / `ObsidianSettingRoleplay` / `GoogleCalendar` / `AutonomousCuriosity` / 跨 Scene 永久 / 临时
- **入池门**：`PoolAdmissionPolicy` strategy + `DesktopPolicy` baseline（confidence + 加权投票 + IntentEvent 关联）
- **出池门**：TTL + 池上限 + priority chain（特殊状态 > 父类状态 > 时间）
- **Ref 表**：轻量 UUID 绑定（Graphiti / Obsidian / 内存 / 硬盘）+ 健康度
- **扩展点**：所有 strategy 接口可换第三方实现（Redis / FAISS / LlamaIndex 等）

### §3.2 状态生命周期差异化（详见 [`dsg_protocol_pool_v1`](dsg_protocol_pool_v1_20260506.md) §3）

- **Obsidian 三分类**（master §3.2 已锁）：Ref-加强 / 设定-日常 / 设定-Roleplay
- **GOSLO 主动发现**：新增 `ObservationSource.GOSLO_AUTONOMOUS`（priority=50，介于 GEMINI_ORAL 和 IDENTIFY_OBJECT）
- **USER_EXPLICIT 拆**：USER_VERBAL / USER_UI（在 filter 内分流，enum 仍单一）
- **GEMINI_ORAL 拆**："泛泛之谈" vs "当前场景实体"（在 filter 内分流，跨源合并信号）
- **IDENTIFY_OBJECT lastSeen 永久**（master §3.4 已锁）；其他状态字段简化
- **跨 source 状态机**：桌面起步共用一套 `EXPECTED → ACTIVE → PERIPHERAL → GHOST`；测试期不衰减

### §3.3 L2-B 简单升级（详见 [`dsg_protocol_intent_event_boundary_v1`](dsg_protocol_intent_event_boundary_v1_20260506.md)）

- **单 `PyDiGraph`**（不分图）+ Compartment **lazy view**
- 节点 4 标签字段（`bucket_id` / `scene_type` / `location_tag` / `event_id`）
- view 方法：`view_by_compartment` / `view_by_event` / `view_by_bucket` / `view_by_scene` / `view_by_kind`

### §3.4 IntentEventBoundary（认知边界）

- **触发**：`tool call boundary` / `nanobot result return` / `long idle` / `explicit`
- **桌面 baseline**：标签 + 降权（不真折叠）
- **仿生升级路径**（接口已留，实现 P3）：
  - `FoldStrategy.fold(event_id)` → RustworkX subgraph 折叠
  - Cluster 折叠（rustworkx-master §3.4 范式四）
  - Spreading Activation 跨通道（dsg-attention-schema-papers §5.4）
  - VF2++ 子图同构识别经验（dsg-rustworkx-master §2.5）
- **跳数硬上界**：4 跳（AGCN 实证，dsg-rustworkx-master §3.5）

### §3.5 Scene 切换（详见 [`dsg_protocol_scene_snapshot_v1`](dsg_protocol_scene_snapshot_v1_20260506.md)）

- **桌面 baseline**：单 `SceneType="desktop"`
- **切换主路径**：`SceneRegistry.switch(new_scene_id, profile)` → freeze 永久权威 Bucket / 切换 CV Flow / 切换 DsgMode / 序列化旧 Scene snapshot
- **Scene ≠ IntentEvent ≠ LocationTag**（§0.1 锁名）
- **不主导 L2-B 拓扑**（拓扑由 IntentEvent 驱动）；只是节点字段 + L1.5 管理面

### §3.6 IntentWorkspace（Brain Intent 层资源暂存，详见 [`brain_protocol_intent_workspace_v1`](brain_protocol_intent_workspace_v1_20260506.md)）

- **落位**：`src/parrot/brain/intent_workspace.py`（Brain 端）
- **职责**：GOSLO 当前正在读的大文件常驻内存；IntentEvent close 自动批量 evict
- **Backend strategy**：InMemory（baseline）/ Disk / 未来 Redis / S3 / FAISS
- **借鉴**：Cursor workspace context / Claude Desktop attachments / OpenAI Assistants v2 thread.attachments / LlamaIndex DocumentStore 模式

### §3.7 Plan-and-Execute（详见 [`brain_protocol_plan_v1`](brain_protocol_plan_v1_20260506.md)）

- **流程**（用户原话锚定）：
  1. 鹦鹉 Intent 阻塞对话 → 制定 Plan
  2. Plan 通过 IntentWorkspace 暂存 + EcpEvent 通知 Unity 渲染（wire 升级 P3，本 chat 留接口）
  3. 用户在 Unity 确认（wire 升级 P3）
  4. APPROVED → 派发 NanobotTask × N
  5. 鹦鹉解除阻塞 → 恢复对话
  6. NanobotTask 完成 / 出错 → trigger fire → Brain 接收汇报
- **Plan 主存**：IntentWorkspace（StagedRefKind.PLAN）
- **L2-B 镜像**：reuse `NodeKind.EVENT`（Phase 4 §8 L1 锁不动）+ `source_meta.plan_role` / `source_meta.plan_id`
- **PlanBlackboard**：py-trees BB 子命名空间 `plan/{plan_id}/...`（与既有 `scheduler/` / `transient/` / `session/` 同级）

---

## §4 工作记忆延迟归档（详见 [`dsg_protocol_archive_v1`](dsg_protocol_archive_v1_20260506.md)）

- **三阶段管线**（master §5 已锁）：
  ```
  对话期间 (Hot)
    L2-B + InMemory snapshot + RefTable + Timeline + IntentWorkspace
    → 不写 Graphiti
          ↓ ConversationBoundary 触发（agent disconnect / Episode close / long idle / explicit）
  对话结束 (Cold Storage)
    parrot.dsg.archive.ConversationArchive.serialize(conv_id)
    → data/conversations/{conv_id}/{snapshot.json,refs.jsonl,timeline.jsonl,episodes.jsonl,plans.jsonl}
          ↓ IdleArchiveTrigger（nanobot heartbeat idle ≥ N min）
  归档 (Archive Flow)
    unified_filter (含 MemoryValidity 占位接口) + LLM
    → Graphiti.add_episode (per Episode batch)
  ```
- **冲突解决**：
  - `l2b_graph.start_episode()` 移除立即 archive 调用
  - `runner.commit_observation` 的 `TODO(S4.B)` 注释改为新管线指引

---

## §5 触发器协议升级 V2（详见 [`dsg_protocol_trigger_v2`](dsg_protocol_trigger_v2_20260506.md)）

`TriggerOutcome` 替代 `TriggerResult`（alias 保留）—— **5 路上行通道 + 既有 2 路保留**：

```python
@dataclass
class TriggerOutcome:
    # 既有保留
    trigger_name: str
    summary: str
    nodes_affected: list[str]
    dispatch_to_nanobot: bool
    nanobot_task: dict[str, Any] | None
    notify_gemini: bool
    notification_text: str
    # 新增 5 路上行
    commit_observations: tuple["Observation", ...] = ()    # → IngestRunner 入 L1.5 池
    bucket_ops: tuple["BucketOp", ...] = ()                # → L15Pool 桶管理
    archive_request: "ArchiveRequest | None" = None        # → ConversationArchive
    staged_refs: tuple["StagedRefRequest", ...] = ()       # → IntentWorkspace.stage
    plan_request: "PlanProposal | None" = None             # → PlanRegistry.draft
```

**5 个新触发器**：
- `SceneSwitchTrigger` (ON_DEMAND) — set_scene → bucket freeze + snapshot
- `IntentEventBoundaryTrigger` (EVENT_DRIVEN) — tool / idle → IntentEvent
- `RoleplayModeTrigger` (ON_DEMAND) — roleplay 桶 register / clear
- `GosloCuriosityTrigger` (EVENT_DRIVEN) — attention threshold + unknown
- `IdleArchiveTrigger` (PERIODIC) — nanobot idle → 归档

---

## §6 协议合同 0 漂移核对

| 锁 | 状态 | 守护 |
|:--|:--|:--|
| Phase 4 §8 L1（NodeKind 6 / EdgeKind 8）| 0 漂移 | 仅加 informational 字段 + reuse NodeKind.EVENT 镜像 Plan |
| Phase 4 §8 L7（PhotoEvent 不自动建 ObjectNode）| 0 漂移 | Plan 镜像不影响 PhotoEvent 路径 |
| Phase 4 §8 L9（attention threshold 数值 + 模块边界）| 0 漂移 | dsg/attention/threshold.py / hint_writer.py 不动 |
| Phase 4 §8 L11（identify_object 1.9s 预算）| 0 漂移 | identify_object 不动 |
| Phase 4 §8 L13（dsg/attention/__init__.py export 集合）| 0 漂移 | 新增 decay.py / mechanism.py 不 export 顶层符号 |
| ADR-L1.5-001 §4.1 子类化 3 触发器 | **本 chat 后核对**（§9）| 详见本文 §9 |
| `parrot_behavior_rules §3.7` Observer-Attention 边界 | 0 漂移 | dsg/attention/threshold.py 仍不塞 BB |
| `tests/test_ecp_event/test_cs_parity.py` 4/4 | 0 漂移 | 不动 EcpEventType / EcpEventSource / topic |

---

## §7 复杂仿生设计空间预留点

> 本 chat **不**实施仿生算法；下方接口在 baseline 实现里都是 noop / 标签 / 限深，仅留 strategy 接入点：

| 接入点 | 接口 | 桌面 baseline | P3+ 仿生升级 |
|:--|:--|:--|:--|
| 注意力衰减 | `AttentionDecayPolicy.decay(node, now) -> float` | noop（返回原值）| TWF (`τ_eff = τ_base / trust`)，量子化（int8） |
| 注意力机制 | `AttentionMechanism.activate(seeds, depth) -> list[(uuid, score)]` | 限深 BFS + evidence 加权 | PPR / Spreading Activation / GAT-style softmax / VF2++ |
| 入池审议 | `PoolAdmissionPolicy.evaluate(obs) -> AdmitDecision` | 30s repeat-seen + confidence 阈值 | 加权投票 / 多帧累积 / 跨源融合 |
| 折叠机制 | `FoldStrategy.fold(event_id) -> FoldResult` | noop | RustworkX subgraph 折叠 / Cluster |
| 跨通道边 | `CrossEventChannel.connect(src, dst) -> list[edge]` | 返回所有跨 event 边 | 衰减权重 / 联想阈值 / 抑制性边 |
| 不可能事件检测 | `ImpossibleEventDetector.check(obs) -> Anomaly | None` | noop | 时空一致性 / 物理约束 |
| Ref 健康度 | `RefHealthMonitor.score(ref) -> Health` | binary（绑定/失效）| Ebbinghaus / 访问频次 / 时间衰减 |
| Plan 推断 | `PlanInferer.suggest(intent) -> PlanProposal` | 手工调（GOSLO LLM 直接产生）| LangChain Plan-and-Execute / Tree-of-Thought |
| 健康度监控 | `GraphHealthMonitor.report(graph) -> Health` | 节点数 / 边数 / 孤立度 | betweenness / clustering / 模块化（ASD/MDD 范本） |

---

## §8 测试覆盖（**核心：验证协议接口能力覆盖需求**）

```
tests/test_dsg/
├── test_admission_baseline.py             admit / reject / score path（dsg_protocol_pool_v1）
├── test_bucket_lifecycle.py               import / freeze / clear（含 roleplay 一键删除）
├── test_ref_table_stability.py            UUID 绑定 + 健康度
├── test_timeline_event_alignment.py       Timeline marker（Plan / IntentEvent / Episode 对齐）
├── test_scene_switch_baseline.py          SceneProfile switch（dsg_protocol_scene_snapshot_v1）
├── test_scene_preserve_authority.py       永久权威桶跨 SceneType 保留
├── test_trigger_outcome_v2_5_channels.py  TriggerOutcome 5 路上行（dsg_protocol_trigger_v2）
├── test_intent_event_boundary_minimum.py  baseline 标签 + 降权 / fold=noop
├── test_archive_three_phase.py            hot / cold / idle 三阶段（dsg_protocol_archive_v1）
├── test_l2b_views.py                      view_by_compartment / event / bucket / scene / kind
├── test_terminology_no_collision.py       ★ 名词冲突守护（Event / Scene / Task 单写禁止）
└── test_compatibility_with_phase4.py      Phase 4 §8 + cs_parity 4/4 + ADR-L1.5-001 11/11

tests/test_brain/
├── test_intent_workspace_lifecycle.py     stage / fetch / evict / evict_intent
├── test_intent_workspace_backend.py       InMemory + Disk backend swap
├── test_ref_handle_node_binding.py        IntentWorkspace ↔ RefTable ↔ Node 三元
├── test_plan_lifecycle.py                 DRAFT → CONFIRMED → EXECUTING → DONE
├── test_plan_intent_workspace_binding.py  Plan stage / L2-B 镜像 / PlanBlackboard
└── test_plan_to_nanobot_dispatch.py       PlanStep → NanobotTask 派发 + result 回流
```

→ 当前 234/234 + 上述 18 项新增。Phase 4 §8 + cs_parity + ADR-L1.5-001 11 项**全部不动**。

---

## §9 ADR-L1.5-001 §4.1 子类化 3 触发器核对（**实施完成时填**）

> 实施完成后**必须**回填本节。如触发任一条件 → 起新 ADR `supersedes: [ADR-L1.5-001]`。

| 触发器 | 是否触发 | 证据 |
|:--|:--|:--|
| ① ≥3 source 字段差异 ≥3 个 | **预测：不触发**（A10 字段在 P3 才接入；本 chat source_meta 未稳定 schema）| 实施完填 |
| ② ≥2 source 行为多态 | **预测：不触发**（衰减 / GHOST 转换通过 strategy 实现，不绑节点子类）| 实施完填 |
| ③ isinstance 反复手写 | **预测：不触发**（dispatch 走 strategy 表 + factory）| 实施完填 |

→ 预期结论：**继续走 meta dict + factory hybrid**（ADR-L1.5-001 §2.2 选定方案）。

---

## §10 master `provisional-revisit-after-L2-design` 回审（**实施完成时填**）

> 实施完成后**必须**回审 [master](dsg_decisions_master.md) 所有 `provisional-revisit-after-L2-design` 条目，逐条标 `ratified` / `superseded` / 保持。

| master 条目 | 当前 status | 本 chat 后预期 |
|:--|:--|:--|
| §1.1 L1.5 角色升级 | provisional | → **ratified**（落到 `dsg.l1_5/` 子包）|
| §1.1 与 L2-B 关系 | provisional | → **ratified**（L1.5 不持节点，view + 元数据）|
| §1.2 L1.5 入池门具体规则 | provisional | → **ratified**（DesktopPolicy baseline + strategy 接口）|
| §1.3 入池条件 | provisional | → **ratified**（trigger 5 路 + AdmissionPolicy）|
| §1.4 池上限 / 淘汰 | provisional | → **ratified**（Priority chain + strategy）|
| §1.4 主动出池 | provisional | → **ratified**（IntentEvent close / Episode close / Scene switch）|
| §2.1 后期分图 / Cluster | deferred-to-design | → **deferred-to-P3**（接口预留，不实施）|
| §3.1 _SOURCE_PRIORITY 切换开关具体形态 | provisional | → **ratified**（SceneProfile 携带 priority overrides）|
| §3.2 roleplay 子类是否新增 NodeKind | provisional | → **ratified**（不新增；reuse 现有 + bucket_id 区分）|
| §3.5 跨 source 状态机分轴 | provisional | → **deferred-to-P3** |
| §6.5 子图分层 P1-P4 选项裁决 | deferred | → **ratified**（选 P1+P3 hybrid，view-style 实现）|

---

## §11 引用

### §11.1 Master / 状态 / 决策
- [`dsg_decisions_master.md`](dsg_decisions_master.md)
- [`dsg_current_state_distilled.md`](dsg_current_state_distilled.md)
- [`source_x_lifecycle_status.md`](source_x_lifecycle_status.md)
- [`open_questions_for_design_chat.md`](open_questions_for_design_chat.md)

### §11.2 ADR / Phase 4 锁
- [ADR-L1.5-001](../adr_l1_5_source_dispatch_extension_space_20260504.md)
- [Phase 4 §8 13 决策锁](../sprint4_phase4_entry_20260430.md)
- [Phase 4 完成报告](../sprint4_phase4_completion_and_final_audit_20260430.md)

### §11.3 4 个 DSG skill
- [`dsg-rustworkx-master`](../../../skills/dsg-rustworkx-master/SKILL.md)
- [`dsg-l2b-node-organization-options`](../../../skills/dsg-l2b-node-organization-options/SKILL.md)
- [`dsg-attention-schema-papers`](../../../skills/dsg-attention-schema-papers/SKILL.md)
- [`dsg-l1-5-l2a-conceptgraph-distilled`](../../../skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md)

### §11.4 7 份 companion 协议文档
- [`dsg_protocol_pool_v1_20260506.md`](dsg_protocol_pool_v1_20260506.md)
- [`dsg_protocol_trigger_v2_20260506.md`](dsg_protocol_trigger_v2_20260506.md)
- [`dsg_protocol_intent_event_boundary_v1_20260506.md`](dsg_protocol_intent_event_boundary_v1_20260506.md)
- [`dsg_protocol_archive_v1_20260506.md`](dsg_protocol_archive_v1_20260506.md)
- [`dsg_protocol_scene_snapshot_v1_20260506.md`](dsg_protocol_scene_snapshot_v1_20260506.md)
- [`brain_protocol_intent_workspace_v1_20260506.md`](brain_protocol_intent_workspace_v1_20260506.md)
- [`brain_protocol_plan_v1_20260506.md`](brain_protocol_plan_v1_20260506.md)

### §11.5 行为契约 / 模块边界
- [`parrot_behavior_rules.md §3.7`](../../parrot_behavior_rules.md)
- [`module_map_p2.md §10 / §11`](../module_map_p2.md)

### §11.6 派发上下文
- [Chat 2 launch prompt](dsg_l1_5_pool_design_chat_launch_prompt_20260506.md)
- [`sprint4_phase4_downstream_chat_dispatch_plan_20260504.md §1.1 Chat 2`](../sprint4_phase4_downstream_chat_dispatch_plan_20260504.md)

---

## §12 变更日志

- **2026-05-06**：本文创建。Chat 2 主交付物。术语表锁定 + 模块布局 + 协议引用关系 + 9 项扩展点接口预留。配套 7 份协议文档 + 1 份完成报告骨架同期产出。
