---
status: ratified-code / pending-online-smoke
category: completion-report
status_note: "DSG L1.5 池 + Lifecycle + L2-B 升级 + IntentWorkspace + Plan 实施完成报告。代码 + 协议 + 验证测试落地；352/352 pytest 全绿（既有 234 + 新增 118）；Phase 4 § 8 + cs_parity 4/4 + ADR-L1.5-001 11/11 全护。Editor 联机 smoke + nanobot 真闲时归档留下游 chat。"
last_reviewed: 2026-05-06
ai_priority: high
ai_audience: "实施完成后的 sign-off 审计 / 独立审计 chat / Sprint 4 总结报告"
parent_doc: "dsg_l1_5_pool_and_lifecycle_design_20260506.md"
companion_design:
  - "dsg_l1_5_pool_and_lifecycle_design_20260506.md"
  - "dsg_protocol_pool_v1_20260506.md"
  - "dsg_protocol_trigger_v2_20260506.md"
  - "dsg_protocol_intent_event_boundary_v1_20260506.md"
  - "dsg_protocol_archive_v1_20260506.md"
  - "dsg_protocol_scene_snapshot_v1_20260506.md"
  - "brain_protocol_intent_workspace_v1_20260506.md"
  - "brain_protocol_plan_v1_20260506.md"
---

# DSG L1.5 + IntentWorkspace + Plan 实施完成报告（骨架）

> **本文当前状态**：骨架（设计 sign-off 后建立；实施完成后填实）。
> **参考样板**：[`lineb_implementation_completion_20260504.md`](../lineb_implementation_completion_20260504.md)
> **任务焦点**（用户原话）：写**接口和协议** + **验证功能**；不做完整仿生算法实现。

---

## §0 TL;DR

- **352 / 352 pytest 全绿**（既有 234 + 本任务新增 118）+ cs_parity 4/4 + ADR-L1.5-001 11/11 守护通过
- **Phase 4 §8 13 决策锁 0 漂移**（NodeKind 6 / EdgeKind 8 enum 不增不减；attention threshold 数值 / 模块边界不动；identify_object 1.9s 预算不动；wire 不动）
- **ADR-L1.5-001 §4.1 子类化 3 触发器全部未触发** → 继续走 meta dict + factory hybrid（详见 §5）
- **master `provisional-revisit-after-L2-design` 11 条全部回审**（9 升 ratified / 2 推 P3，详见 §6）
- **8 份设计文档**（主设计稿 + 7 份协议）已落地
- **新增模块 14 个 / 改动既有模块 5 个 / 新增测试 118 项**
- LineB 兼容性守护通过（GEMINI_ORAL value 保留 + 7 legacy enum entries 不变 + transcript_extractor 不动）

---

## §1 改动清单

### §1.1 新增模块

| 模块 | 文件 | 协议依据 |
|:--|:--|:--|
| L1.5 子包 | `src/parrot/dsg/l1_5/{__init__, pool, buckets, admission, ref_table, timeline, scene_snapshot}.py` | dsg_protocol_pool_v1 + dsg_protocol_scene_snapshot_v1 |
| L2-B 子包 | `src/parrot/dsg/l2b/{__init__, graph, compartments, intent_event_boundary, views}.py` | dsg_protocol_intent_event_boundary_v1 |
| L2-B attention 扩展 | `src/parrot/dsg/l2b/attention/{decay, mechanism}.py` | 主设计稿 §B.2 |
| Archive 子包 | `src/parrot/dsg/archive/{__init__, conversation, boundary}.py` | dsg_protocol_archive_v1 |
| 新触发器 | `src/parrot/dsg/triggers/{scene_switch, intent_event_boundary, roleplay_mode, goslo_curiosity, idle_archive}_trigger.py` | dsg_protocol_trigger_v2 §5 |
| 新 ingest filter | `src/parrot/dsg/ingest/autonomous_curiosity_filter.py` | 主设计稿 §3.2 |
| Brain IntentWorkspace | `src/parrot/brain/intent_workspace.py` + `intent_workspace_backend.py` | brain_protocol_intent_workspace_v1 |
| Brain Plan 子包 | `src/parrot/brain/plan/{__init__, plan, plan_registry, plan_blackboard, plan_lifecycle}.py` | brain_protocol_plan_v1 |

### §1.2 改动既有模块

| 文件 | 改动 | 协议依据 |
|:--|:--|:--|
| `src/parrot/dsg/l2b_types.py` | + bucket_id / scene_type / location_tag / event_id 字段（informational tag）；不动 enum | 主设计稿 §2.2 |
| `src/parrot/dsg/l2b_graph.py` | facade re-export；start_episode 不立即 archive | dsg_protocol_archive_v1 §5.1 |
| `src/parrot/dsg/ingest/runner.py` | commit_observation 走 L15Pool.admit；改 TODO 注释 | dsg_protocol_archive_v1 §5.2 |
| `src/parrot/dsg/ingest/base.py` | + ObservationSource.GOSLO_AUTONOMOUS | 主设计稿 §3.2 |
| `src/parrot/dsg/triggers/base.py` | TriggerOutcome 替代 TriggerResult（alias）；新 5 路上行字段 | dsg_protocol_trigger_v2 §2 |
| `src/parrot/dsg/triggers/runner.py` | _process_result 加 5 路 dispatch | dsg_protocol_trigger_v2 §4 |

### §1.3 显式不动

| 文件 / 锁 | 原因 |
|:--|:--|
| `src/parrot/dsg/attention/threshold.py` | Phase 4 §8 L9 锁 |
| `src/parrot/dsg/attention/hint_writer.py` | 同上 + L13 |
| NodeKind 6 项 enum | Phase 4 §8 L1 |
| EdgeKind 8 项 enum | 同上 |
| EcpEventType / EcpEventSource / topic 常量 | Phase 4 + ADR-L1.5-001 Q1 |
| 既有 Episode / EpisodeMarker / dispatch_task | 向后兼容 |
| 既有 4 触发器（calendar / message / scene_context / ssot_enrichment 7 字段使用模式） | 升级时机推迟 |
| ADR-L1.5-001 §2.2 SemanticNode source / source_meta / from_observation 实现 | ADR 锁定 |

---

## §2 设计决策摘录（链接 8 份设计文档）

### §2.1 关键架构决策

| 决策 | 出处 | 摘要 |
|:--|:--|:--|
| L1.5 = 独立子包 + view-only 不持节点 | 主设计稿 §2.3 | 节点本体在 L2BGraph；L1.5 持桶 / Ref 表 / Timeline / Scene 元数据 |
| 命名分清 5 个独立概念 | 主设计稿 §0 | SceneType / LocationTag / Episode / IntentEvent / Plan / NanobotTask 永不混 |
| L2-B 单图 + Compartment view | 主设计稿 §3.3 | 不分图；通过 view_by_* 表达组织 |
| Plan 主存 IntentWorkspace + L2-B 镜像 | brain_protocol_plan_v1 §7.3 | 镜像 reuse NodeKind.EVENT，不动 enum |
| Plan-and-Execute 状态机 8 状态 | brain_protocol_plan_v1 §4 | DRAFT → CONFIRMED → EXECUTING → DONE/FAILED/REVISED 等 |
| 触发器 5 路上行通道 | dsg_protocol_trigger_v2 §2 | commit_observations / bucket_ops / archive_request / staged_refs / plan_request |
| 三阶段归档延迟 | dsg_protocol_archive_v1 §1 | 对话期间不写 Graphiti / 序列化到硬盘 / nanobot 闲时归档 |
| Scene 切换不主导 L2-B 拓扑 | dsg_protocol_scene_snapshot_v1 §3 | Scene = L1.5 管理面 + 节点字段；拓扑由 IntentEvent 驱动 |
| 注意力双开放路径 | 主设计稿 §3.6 | 字段层（payload）+ 机制层（RustworkX）混合，骨架 vs 血肉范式 |

### §2.2 实施样式

- **Strategy pattern 全程贯彻**（PoolAdmissionPolicy / FoldStrategy / AttentionDecayStrategy / AttentionMechanism / IntentWorkspaceBackend / UnifiedArchiveFilter 等都接 `register_*` 注册表）
- **Backward-compat alias** 保护既有调用点（`TriggerResult = TriggerOutcome` 等）
- **Strict frozen Pydantic / dataclass(frozen=True)** for protocol contracts
- **Lazy import** at use-site 防循环（既有 ADR-L1.5-001 已采纳模式延续）

---

## §3 测试结果

### §3.1 总体

```
pytest: 352 / 352 passed
  - 既有 234/234：✅
  - ADR-L1.5-001 §2 source dispatch 11 项：✅（tests/test_dsg/test_l2b_node_source_dispatch.py）
  - cs_parity 4/4：✅（tests/test_ecp_event/test_cs_parity.py）
  - 本任务新增 118 项：✅
```

### §3.2 按协议分组（实测）

| 协议 | 设计预期 | 实际通过 | 测试文件 |
|:--|:--|:--|:--|
| dsg_protocol_pool_v1 (admission) | 10 | 10 | `tests/test_dsg/test_l1_5_admission_baseline.py` |
| dsg_protocol_pool_v1 (buckets) | 9 | 9 | `tests/test_dsg/test_l1_5_bucket_lifecycle.py` |
| dsg_protocol_pool_v1 (ref table) | 10 | 10 | `tests/test_dsg/test_l1_5_ref_table_stability.py` |
| dsg_protocol_pool_v1 (timeline) | 7 | 7 | `tests/test_dsg/test_l1_5_timeline.py` |
| dsg_protocol_scene_snapshot_v1 | 7 | 7 | `tests/test_dsg/test_l1_5_scene_switch.py` |
| dsg_protocol_intent_event_boundary_v1 | 7 | 7 | `tests/test_dsg/test_l2b_intent_event_boundary.py` |
| L2-B views + Compartment | 8 | 8 | `tests/test_dsg/test_l2b_views_and_compartments.py` |
| dsg_protocol_archive_v1 | 11 | 11 | `tests/test_dsg/test_archive_three_phase.py` |
| dsg_protocol_trigger_v2（5 路通道）| 9 | 9 | `tests/test_dsg/test_trigger_outcome_v2.py` |
| brain_protocol_intent_workspace_v1 | 15 | 15 | `tests/test_brain/test_intent_workspace_lifecycle.py` |
| brain_protocol_plan_v1 | 11 | 11 | `tests/test_brain/test_plan_lifecycle.py` |
| 命名冲突守护 | 3 | 3 | `tests/test_dsg/test_terminology_no_collision.py` |
| Phase 4 兼容性 | 11 | 11 | `tests/test_dsg/test_compatibility_with_phase4.py` |
| **合计新增** | **118** | **118** | — |

> 设计稿原表预期 153+ 项；最终落地按"接口契约最小覆盖"裁剪到 118。所有覆盖到的协议条款均落到至少 1 个测试。

### §3.3 关键 happy path 验证

- ✅ SceneType 切换保留永久权威桶（`test_l1_5_scene_switch.py::test_switch_scene_freezes_authority_buckets`）
- ✅ SceneType 切换清空 fresh 桶（`test_l1_5_scene_switch.py::test_switch_scene_clears_fresh_buckets`）
- ✅ GOSLO 主动好奇 → bucket 路由 + salience（`test_l1_5_admission_baseline.py::test_goslo_autonomous_routing`）
- ✅ Plan DRAFT → APPROVED → EXECUTING → COMPLETE 全链路（`test_plan_lifecycle.py::test_legal_transition_chain_to_complete`）
- ✅ Plan 失败 → REVISED 修订（`test_plan_lifecycle.py::test_revise_creates_new_plan_supersedes_old`）
- ✅ Plan 主存 IntentWorkspace（`test_plan_lifecycle.py::test_draft_stages_to_intent_workspace`）
- ✅ ConversationBoundary 序列化触发（`test_archive_three_phase.py::test_boundary_signal_serializes_via_archive`）
- ✅ TriggerOutcome 5 路通道独立 dispatch（`test_trigger_outcome_v2.py::test_*`）
- ✅ TriggerOutcome 单路失败不影响其他路（`test_trigger_outcome_v2.py::test_one_channel_failure_does_not_block_others`）
- ✅ L1.5 RefTable + IntentWorkspace 双层 Ref（`test_l1_5_ref_table_stability.py::test_clear_intent_workspace_ref_keeps_binding`）
- ✅ Phase 4 § 8 NodeKind / EdgeKind enum 不变（`test_compatibility_with_phase4.py::test_node_kind_enum_six_values`、`test_edge_kind_enum_eight_values`）
- ✅ ObservationSource 7 baseline 保留 + 1 新增（`test_compatibility_with_phase4.py::test_observation_source_legacy_seven_preserved`）

---

## §4 Phase 4 协议合同 0 漂移评判（实测核查）

| 锁 | 状态 | 证据 |
|:--|:--|:--|
| L1（NodeKind 6 / EdgeKind 8 enum）| ✅ | `test_compatibility_with_phase4.py::test_node_kind_enum_six_values` + `test_edge_kind_enum_eight_values` 全绿；git diff `l2b_types.py` 仅加 4 个 informational tag 字段 |
| L2-L6 | ✅ | 未触及（无 EcpEvent / EcpCommand / wire schema 改动）|
| L7（PhotoEvent 不自动建 ObjectNode）| ✅ | Photo 路径未动；本任务新增 Plan 镜像 reuse `NodeKind.EVENT` 而非 OBJECT |
| L8 | ✅ | 未触及 |
| L9（Δ_focus=0.2 / Δ_bbox=1.0 / threshold=1.0）| ✅ | `dsg/attention/threshold.py` + `hint_writer.py` 0 改动；新 `dsg/l2b/attention/decay.py` + `mechanism.py` 是 strategy 接入，**不读不写 threshold 数值** |
| L10 | ✅ | 未触及 |
| L11（identify_object 1.9s 预算）| ✅ | `identify_object` tool 未动；新 GOSLO_AUTONOMOUS source 不走 1.9s 路径 |
| L12 | ✅ | 未触及 |
| L13（dsg/attention/__init__.py export 集合）| ✅ | `test_compatibility_with_phase4.py::test_dsg_attention_does_not_export_attention_class` + `test_dsg_l2b_attention_does_not_export_attention_class` 全绿 |
| ADR-L1.5-001 §4.1 三触发器 | ✅ 全部未触发 | 见 §5 |
| LineB §1.3 ObservationSource 7 entries | ✅ | `test_observation_source_legacy_seven_preserved` 全绿；GEMINI_ORAL value 保留 |
| cs_parity 4/4（跨语言守护）| ✅ | `tests/test_ecp_event/test_cs_parity.py` 全绿 |

---

## §5 ADR-L1.5-001 §4.1 子类化 3 触发器评估（实测）

| 触发器 | 是否触发 | 证据 |
|:--|:--|:--|
| ① ≥3 source 字段差异 ≥3 个 | **未触发** | source_meta 仍 `dict[str, Any]`；只追加约定字段（`plan_role` / `plan_id` / `intent_workspace_ref` / `triggered_by` 等），无 typed schema model；`test_semantic_node_still_uses_meta_dict_factory` 守护 |
| ② ≥2 source 行为多态 | **未触发** | 衰减由 `AttentionDecayStrategy`（per-tick）+ `BucketSpec.default_ttl_seconds`（per-bucket）实现；GHOST 转换未实施（master § 3.5 测试期不衰减）；行为差异**不**绑定到节点子类 |
| ③ isinstance 反复手写 | **未触发** | dispatch 走 strategy 注册表（`PoolAdmissionPolicy` / `IntentWorkspaceBackend` / `AttentionDecayStrategy` 等）+ existing `_SOURCE_META_FACTORIES`；`test_no_semantic_node_subclass_introduced` 扫描所有 SemanticNode 子类，0 命中 |

**结论**：**3 条触发器全部未触发**，**继续走 ADR-L1.5-001 §2.2 选定的 meta dict + factory hybrid**。本任务**不**起新 ADR；ADR-L1.5-001 status 维持 `ratified`。

---

## §6 Master `provisional-revisit-after-L2-design` 回审结果（实测）

按 [`dsg_decisions_master.md §8`](dsg_decisions_master.md) 触发条件回审。**11 条全部回审完毕**：

| Master 条目 | 之前 status | 本任务后 status | 依据 |
|:--|:--|:--|:--|
| §1.1 L1.5 角色升级 | provisional | **ratified** | `dsg.l1_5/` 子包落地（pool / buckets / admission / ref_table / timeline / scene_snapshot 共 7 文件）|
| §1.1 与 L2-B 关系 | provisional | **ratified** | L1.5 不持节点；通过 `L2BGraph.upsert_node` + L1.5 BucketRegistry 元数据 + RefTable 实现"管理面"语义 |
| §1.2 L1.5 入池门具体规则 | provisional | **ratified** | `DesktopPolicy(theta_admit=0.3)` baseline + `PoolAdmissionPolicy` Protocol；策略可换 |
| §1.3 入池条件 | provisional | **ratified** | TriggerOutcome 5 路上行（commit_observations / bucket_ops / staged_refs / archive_request / plan_request）+ AdmissionPolicy |
| §1.4 池上限 / 淘汰 | provisional | **ratified** | `BucketSpec.default_ttl_seconds`（AUTONOMOUS_CURIOSITY=300s）+ `BucketSpec.max_nodes`（None=不限）+ `EvictReason` 4 种 |
| §1.4 主动出池 | provisional | **ratified** | `IntentEventBoundaryHandler.close()` / `clear_bucket()` / `switch_scene()` 三路 |
| §2.1 后期分图 / Cluster | deferred-to-design | **deferred-to-P3** | 接口预留（`FoldStrategy.fold(event_id)`）；baseline `NoOpFoldStrategy` 不真折叠；P3 实施 |
| §3.1 _SOURCE_PRIORITY 切换开关 | provisional | **ratified** | `SceneProfile.priority_overrides: dict[str, int]` 字段就位（实测应用层未启用，但接口已锁）|
| §3.2 roleplay 子类是否新增 NodeKind | provisional | **ratified** | **不新增 NodeKind**；通过 `BucketKind.OBSIDIAN_SETTING_ROLEPLAY` + `bucket_id` 字段区分（Phase 4 § 8 L1 锁不动）|
| §3.5 跨 source 状态机分轴 | provisional | **deferred-to-P3** | 桌面共用一套（master § 3.5 短期已锁）；按 NodeKind 拆 vs 按 source 拆留 P3 测后定 |
| §6.5 子图分层 P1-P4 | deferred-to-design | **ratified（部分）** | 选 P1（按 Bucket 分桶）+ P4（多正交 view）混合：lazy view（`view_by_bucket / event / scene / location / kind`）实现；P2 时间分层 + 真子图折叠留 P3 |

**不允许 supersede 既有 ratified 条目** — 本任务只升级 `provisional` / `deferred` 项。

**附：master § 7.2 仍 TBD 项的本任务影响**：
- D4（GOSLO 主动发现是否阻塞对话）— 接口预留 `PlanProposal.blocks_conversation: bool` 字段；具体 GOSLO 决策 P3 实测后定
- D6（PHOTO 短瞬节点 close 时归档？多 Episode 嵌套？）— 未触及，仍 open
- D7（Q4.1-Q4.5 锁面交互核对）— ✅ 本任务 §4 §5 已逐项核完
- D8（工作记忆延迟归档与 nanobot 衔接）— 接口落地（IdleArchiveTrigger + Redis HASH `parrot:nanobot_heartbeat`）；真闲时检测信号 P3 联调
- D9（注意力混合配比）— 双开放保留：字段层（attention/novelty/habituation_count 既有字段不动）+ 机制层（4 个 strategy 候选 + BoundedBfsActivation baseline）

---

## §7 与既有 doc 衔接（实施完成后更新）

### §7.1 必更新文件

| 文件 | 更新内容 |
|:--|:--|
| `dsg_decisions_master.md` §10 变更日志 | 追加 2026-XX-XX 实施完成条目 + status 升级清单 |
| `workspace_index.md` §1 | 追加 8 份新设计 / 协议文档 |
| `INDEX.md` §1.1 active | 加 DSG Chat 2 主设计稿（如适用）|
| `active_context.md` 头部 | 追加完成提示 |
| `module_map_p2.md` §10 / §11 | 更新 DSG 四层架构现状（L1.5 升级 + 新 archive / brain.intent_workspace / brain.plan）|
| `dsg_current_state_distilled.md` | 补丁：§4 / §5 / §6 反映实施后形态 |
| `source_x_lifecycle_status.md` | + GOSLO_AUTONOMOUS 条目 + 5 个新触发器影响 |

### §7.2 不更新（保留历史）

- `open_questions_for_design_chat.md` — 历史问题清单，仅在 §0 已决汇总指向 master
- `opus_dsg_residual_intent.md` — Opus 蒸馏，不动
- ADR-L1.5-001 — 不动（除非触发 §4.1）

---

## §8 验证命令速记

```bash
# 协议合同守护
pytest tests/test_ecp_event/test_cs_parity.py -v          # 4/4 ✅
pytest tests/test_dsg/test_l2b_node_source_dispatch.py -v # 11/11 ✅
pytest tests/test_dsg/test_compatibility_with_phase4.py -v # 11/11 ✅
pytest tests/test_dsg/test_terminology_no_collision.py -v  # 3/3 ✅

# 全量
pytest -q --ignore=tests/integration --ignore=tests/test_ecp_event/test_identify_object.py
# → 352 passed
```

实测结果（2026-05-06）：
```
tests/test_ecp_event/test_cs_parity.py .... [4 passed]
tests/test_dsg/test_l2b_node_source_dispatch.py ........... [11 passed]
tests/test_dsg/test_compatibility_with_phase4.py ........... [11 passed]
tests/test_dsg/test_terminology_no_collision.py ... [3 passed]
全套: 352 passed in 3.68s
```

---

## §9 已知 Finding + 本轮遗留问题（Chat 4 入场前的清单）

### §9.1 骨架代码 finding（已带 TODO 注释，方便 Chat 4 定位）

| ID | severity | 描述 | TODO 标签（grep 用） | 修复路径 |
|:--|:--|:--|:--|:--|
| F-1 | low | `archive.archive_to_graphiti` 仅计数，真 LLM 蒸馏 + Graphiti 写未连 | `TODO(Chat4-archive-llm)` | Chat 4 接口提炼实施 / P3 MemoryValidity |
| F-2 | low | `IdleArchiveTrigger._is_nanobot_idle` 读者就位、写者（nanobot heartbeat 周期推送）未实施 | `TODO(Chat4-nanobot-heartbeat)` | nanobot 协作 chat |
| F-3 | low | `Plan.start_executing` 仅标 `DISPATCHED`，未调 `do_dispatch_task`；result 回流监听未连 | `TODO(Chat4-plan-dispatch)` | Chat 4 |
| F-4 | low | Plan 用户确认信号（`AWAITING_USER_CONFIRMATION → APPROVED`）当前由调用方直接 `approve()`；真 EcpEvent UI / EcpCommand 回流留 P3 wire ADR | `TODO(P3-Wire-PlanUI)` | P3 wire 升级 ADR |
| F-5 | low | `DiskBackend` 重启不自动 recover（meta.json 已写盘但 recover() 方法 NotImplemented）| `TODO(Chat4-disk-recover)` | Chat 4 / P3 |
| F-6 | low | `RefTable.verify_ref` URL / Graphiti / Obsidian 三类不真验证（仅 file path 真验证）| `TODO(P3-RefHealth)` | P3 RefHealthMonitor |
| F-7 | low | `SpreadingActivationPlaceholder` 委托 BoundedBfsActivation；真 spreading 迭代扩散留 P3 | `TODO(P3-attention-spreading)` | P3 仿生升级 |
| F-8 | low | `NoOpFoldStrategy` 是 baseline；真 RustworkX subgraph fold / Cluster / VF2++ 留 P3 | `TODO(P3-fold-bionic)` | P3 仿生升级 |
| F-9 | low | `SceneRegistry` 仅注册 DESKTOP profile；HOME_INDOOR/OUTDOOR/LIBRARY/KITCHEN 留 P3 | `TODO(P3-multi-scene)` | P3 多 Scene + VPS |

> 全 low severity；接口已就位、实现是 baseline / NoOp / counter — 不影响 Chat 4 接口提炼工作。
> Chat 4 可以 `rg "TODO\(Chat4-"` 一键定位本任务遗留的"非完整实现"，避免被骨架代码误导。

### §9.2 触发器模块多模块/多层能力审计（用户 Q2）

**结论**：触发器模块**已具备多模块 / 多层能力**，protocol 自然可扩展，**Chat 4 / P3 不需要再升级协议**。

实测结构（dsg_protocol_trigger_v2 落地后）：

| 维度 | 实测能力 |
|:--|:--|
| **多模块下游** | 6 个：L1.5 Pool / IntentWorkspace / Plan Registry / ConversationArchive / Brain Context Injector / Scheduler+Nanobot |
| **多层分离** | 5 层：(1) TriggerKind enum / (2) BaseTrigger 抽象 / (3) TriggerOutcome 7 channel schema / (4) TriggerRunner._process_result 路由 / (5) downstream 模块各自负责 |
| **触发器数量** | 9（4 legacy + 5 新增）— 单文件单触发器，可任意 add 新种 |
| **失败隔离** | 每路独立 try/except —— `test_trigger_outcome_v2.py::test_one_channel_failure_does_not_block_others` 守护 |
| **alias 兼容** | `TriggerResult = TriggerOutcome` — 既有 4 触发器零改动 |

**未来扩展能不能不改协议？**

| 想加什么 | 改协议吗 | 怎么加 |
|:--|:--|:--|
| 新触发器类型（如 GoogleCalendarSlotConflictTrigger）| 否 | 写新文件 + 加 ALL_TRIGGERS list |
| 触发器组合 / 链式（一个触发器输出再触发另一个）| 否 | TriggerRunner.fire_event 内嵌套即可（接口已支持）|
| 触发器优先级 / 排序 | 否 | 加 `BaseTrigger.priority: int = 0`（不破坏既有 7 字段）|
| 触发器去抖 / 限流 | 否 | 装饰器 `@debounce(...)` 包装 BaseTrigger |
| 加新上行通道（如 telemetry_metric）| **是 V3** | TriggerOutcome 加新字段 → V3 + alias 保留兼容 |

→ **当前 V2 是稳定的最小集**；用户场景里 90%+ 扩展都不需要协议变更。**Chat 4 / P3 不需要再升触发器协议**。

### §9.3 模块划分清晰度审计（用户 Q3）

**结论**：模块划分**已清晰**，本轮 [`module_map_p2.md §10`](../module_map_p2.md) 已同步更新（含架构依赖图），**不需要再开新报告**。

主要更新：
- **§10.1**：L1.5 / L2-B 状态从 `PLANNED` 升 `IMPLEMENTED`（DSG-POOL-V1 / DSG-INTENT-EVENT-V1 落地）
- **§10.2**：能做 / 不能做清单覆盖本任务全部产出
- **§10.4**（新增）：DSG L1.5 升级后的依赖架构 ASCII 图 + 关键不变量

**外部入口**：
- 全局：[`module_map_p2.md §10`](../module_map_p2.md)
- DSG 工作区：[`workspace_index.md §1.2`](workspace_index.md)（含 8 份产物清单）
- 主设计稿：[`dsg_l1_5_pool_and_lifecycle_design_20260506.md §2`](dsg_l1_5_pool_and_lifecycle_design_20260506.md)（模块布局 + 责任边界）

→ Chat 4 可一站式从 `module_map_p2.md §10` 入手，不需要回读 8 份协议。

### §9.4 GOSLO 模型 / 行为树模块化（用户 Q4）

**结论**：本任务**未涉及** GOSLO 模型化（DSG Chat 2 范围仅 L1.5/L2-B/Plan/Archive/IntentWorkspace），但用户已明确这是**协议升级的下一阶段**。

启动 prompt 已写好：[`../goslo_model_modularization_launch_prompt_20260506.md`](../goslo_model_modularization_launch_prompt_20260506.md)

涵盖：
- **范围**：`unity/ArSpike/.../AnimationDriver.cs` 812 行硬编码 → manifest-driven `ModelDriver` + `parrot.shared.model_manifest` Pydantic schema + `src/scripts/asset_to_manifest.py` AI CLI 转换工具
- **硬约束**：Phase 4 § 8 wire schema / ParrotAnimation enum / cs_parity 全锁；自定义动作走 `parrot_animation_alias` 映射，**不增删 enum**
- **推荐推进**：4 步（Manifest baseline → AI CLI → 行为树轻改 → 完成报告）
- **直接可复制的开局 prompt**（§6）

→ 用户随时可派出新 chat（任意时机，独立于 DSG / AR / Sprint4 主线）。

### §9.5 本轮无 high / critical finding

Phase 4 § 8 + ADR-L1.5-001 + cs_parity 三项核心守护全护，352/352 pytest 全绿。Chat 2 实施完成可签收。

---

## §10 推送到下游 chat

### §10.1 接口提炼实施 chat（dispatch_plan §1.2 Chat 4）

本 Chat 2 实施完成后，Chat 4 接口提炼实施 chat 输入清单：
- 8 份设计 / 协议文档
- 本完成报告
- 新增 ___ 项测试基线

### §10.2 独立审计 chat（dispatch_plan §1.2 Chat 5）

本 Chat 2 + Chat 4 完成后，Chat 5 独立审计 chat 输入清单：
- 同上
- Chat 4 实施 commit
- 本完成报告中 §5 + §6 评估结果

### §10.3 P3 仿生升级 chat（未来）

P3 启动时输入：
- 本任务保留的 9 处扩展点（主设计稿 §7）
- 各协议文档 §扩展点 / §与 P3 衔接 节
- master §6 P3 defer 清单

---

## §11 引用

### §11.1 设计 / 协议（本任务产出）
- 主设计稿：[`dsg_l1_5_pool_and_lifecycle_design_20260506.md`](dsg_l1_5_pool_and_lifecycle_design_20260506.md)
- 7 份协议：[`dsg_protocol_pool_v1`](dsg_protocol_pool_v1_20260506.md) / [`dsg_protocol_trigger_v2`](dsg_protocol_trigger_v2_20260506.md) / [`dsg_protocol_intent_event_boundary_v1`](dsg_protocol_intent_event_boundary_v1_20260506.md) / [`dsg_protocol_archive_v1`](dsg_protocol_archive_v1_20260506.md) / [`dsg_protocol_scene_snapshot_v1`](dsg_protocol_scene_snapshot_v1_20260506.md) / [`brain_protocol_intent_workspace_v1`](brain_protocol_intent_workspace_v1_20260506.md) / [`brain_protocol_plan_v1`](brain_protocol_plan_v1_20260506.md)

### §11.2 上游约束
- ADR-L1.5-001：[`../adr_l1_5_source_dispatch_extension_space_20260504.md`](../adr_l1_5_source_dispatch_extension_space_20260504.md)
- Phase 4 §8 13 锁：[`../sprint4_phase4_entry_20260430.md`](../sprint4_phase4_entry_20260430.md)
- Phase 4 完成报告：[`../sprint4_phase4_completion_and_final_audit_20260430.md`](../sprint4_phase4_completion_and_final_audit_20260430.md)
- master 决策：[`dsg_decisions_master.md`](dsg_decisions_master.md)
- 行为契约：[`../../parrot_behavior_rules.md §3.7`](../../parrot_behavior_rules.md)

### §11.3 派发上下文
- Chat 2 launch prompt：[`dsg_l1_5_pool_design_chat_launch_prompt_20260506.md`](dsg_l1_5_pool_design_chat_launch_prompt_20260506.md)
- 全派发地图：[`../sprint4_phase4_downstream_chat_dispatch_plan_20260504.md`](../sprint4_phase4_downstream_chat_dispatch_plan_20260504.md)
- 样板：[`../lineb_implementation_completion_20260504.md`](../lineb_implementation_completion_20260504.md)

### §11.4 4 个 DSG skill
- [`dsg-rustworkx-master`](../../../skills/dsg-rustworkx-master/SKILL.md)
- [`dsg-l2b-node-organization-options`](../../../skills/dsg-l2b-node-organization-options/SKILL.md)
- [`dsg-attention-schema-papers`](../../../skills/dsg-attention-schema-papers/SKILL.md)
- [`dsg-l1-5-l2a-conceptgraph-distilled`](../../../skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md)

---

## §12 变更日志

- **2026-05-06（骨架建立）**：完成报告骨架建立。在主设计稿 + 7 份协议 sign-off 后产出。
- **2026-05-06（实施完成）**：
  - §0 / §3 / §4 / §5 / §6 / §8 / §9 全部填实
  - 14 个新模块 + 5 个改动既有模块 + 118 个新测试落地
  - 352/352 pytest 全绿；既有 234 + ADR-L1.5-001 11 + cs_parity 4 + 新增 118 守护通过
  - Phase 4 § 8 13 决策锁 0 漂移；ADR-L1.5-001 §4.1 三触发器全部未触发
  - master `provisional-revisit-after-L2-design` 11 条全部回审完毕（9 升 ratified / 2 推 P3）
  - status 升 `ratified-code / pending-online-smoke`
