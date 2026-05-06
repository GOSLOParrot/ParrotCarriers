---
status: active / chat-4-timeline
category: timeline-spine
status_note: "Chat 4 接口提炼**主时间线**——以接口文档章节 + 目录 + TODO 为 spine。所有 sub-chat 进度反映在本文。每完成一个 sync 点，主 chat 更新本文。"
last_reviewed: 2026-05-07
authoritative_for: "Chat 4 进度跟踪 / 当前 in-progress sub-chat / 下一步派发指引"
parent_doc: "INDEX.md"
parent_plan: "../architecture/interface_extraction_plan_20260507.md"
ai_priority: high
ai_audience: both
---

# Chat 4 接口提炼主时间线 — TODO 总表

> **本文用途**：以接口文档章节 + 目录 + TODO 作为 Chat 4 主时间线。所有 sub-chat 起停 / sync / 完成都反映在本文。
>
> **更新规则**：每个 sub-chat 完成 sync 时，主 chat 把 ☐ 改 ☑ 并附 commit 引用。

---

## §0 当前阶段（实时）

```
[2026-05-07 02:05]
✅ T0 — 规划稿 sign-off + 5 项决策（Q9-Q13）+ amendment 落地（driver 优先 / 不反推 / 目录修订）
✅ T0 — interfaces/ 目录骨架建立（INDEX.md / README.md / methodology.md / TODO.md / 5 子目录）
✅ T0 — Q14 决策：主 chat 直接跑 4-B-req

[2026-05-07 02:30]
✅ T0+ — 4-B-req 完成（needs_inventory.md + app_flow_inventory.md + sync report）
☐ ⏳ T0+ — user 倒查 sync report §4 → sign off
☐ T+2d → T+4d — 4-B-cap 启动（待 sign off 后；选项：主 chat 继续 / fork sub-chat）
☐ T+4d sync 2 — capabilities_inventory 完成
☐ T+4d → T+8d — 4-B-{wire, cross, in} 三 chat 并行
☐ T+9d sync 3 — Stage 4 grep 验证 + upgrade_roadmap
☐ T+10d — Stage 5 INDEX 收口 + 完成报告
```

---

## §1 Stage 1 — 4-B-req 需求 + App 流程 inventory

**起始日**：T0（待启动）  
**预计完成**：T+2d  
**写入位置**：`needs_inventory.md` + `app_flow_inventory.md`

### §1.1 输入清单（必读，按顺序）

- [ ] [`../parrot_behavior_rules.md`](../parrot_behavior_rules.md) — 行为契约（红线 §0.3 / Observer-Attention §3.7）
- [ ] [`../architecture/ar_app_flow_ui_design.md §4`](../architecture/ar_app_flow_ui_design.md) — App Flow 8 步基线
- [ ] [`../architecture/ar_app_flow_ui_design.md §5-§8`](../architecture/ar_app_flow_ui_design.md) — 启动菜单 / HUD / 工具柜 / 注意力工具 8 个开放问题
- [ ] [`../requirements.md`](../requirements.md) — 67 功能项 + 决策记录
- [ ] [`../architecture/ar_feature_vision.md`](../architecture/ar_feature_vision.md) — AR 特性愿景 + 架构收口（含 Phase 5+ 预期）
- [ ] [`../architecture/ar_feature_implementation_plan.md`](../architecture/ar_feature_implementation_plan.md) — Sprint 0-4 实施计划
- [ ] [`../architecture/ar_camera_interaction_survey.md`](../architecture/ar_camera_interaction_survey.md) — AR 摄影互动调研
- [ ] [`../architecture/ar_app_plan.md`](../architecture/ar_app_plan.md) — 早期工程计划（**仅追溯，不驱动**）

### §1.2 待产出（4-B-req 写）

- [x] `needs_inventory.md`：
  - [x] 67 功能项分组（A-H 8 组保留原 ID）
  - [x] 每项标 Chat 4 处置（inventory-only / proposed-upgrade / proposed-new / out-of-scope）+ 拓扑边界候选
  - [x] §2 cross-chat-registry NEED-* 12 项收口
  - [x] §3 14 隐式需求（启动菜单 / HUD / 工具柜 / 注意力工具 8 问 / vision 4 核心 / 行为契约红线）

- [x] `app_flow_inventory.md`：
  - [x] 8 步 App flow 逐步展开（§1-§7 + §4-§5 加载/转场无后端接口）
  - [x] 每步 §x.2 触动的能力 candidates（~55 个）
  - [x] 每步 §x.3 触动的接口面 candidates（~30 个，按拓扑边界初步分桶）
  - [x] 每步 §x.4 开放问题
  - [x] §8 跨步全局议题（4 类块预设链 + Pause-Resume + 摄像头遮挡）

### §1.3 完成判据

- [x] needs_inventory.md + app_flow_inventory.md 落地
- [x] 每项需求 / 每步流程都 cite doc anchor（不引 code 符号）
- [x] §2 方法论合规检查通过（详 _sync/4-B-req_completion.md §2）
- [ ] ⏳ user 倒查 _sync/4-B-req_completion.md §4 → sign off

### §1.4 sync report 落点

✅ [`_sync/4-B-req_completion.md`](_sync/4-B-req_completion.md) — 已产

---

## §2 Stage 2 — 4-B-cap 能力四态表

**起始日**：T+2d（4-B-req sign off 后）  
**预计完成**：T+4d  
**写入位置**：`capabilities_inventory.md` + `capability/` 7 文件

### §2.1 输入

- [ ] Stage 1 输出（needs_inventory + app_flow_inventory）
- [ ] [`../architecture/module_map_p2.md §10.4`](../architecture/module_map_p2.md) — DSG 升级后依赖架构图
- [ ] [`../architecture/sprint4_phase4_completion_and_final_audit_20260430.md §3`](../architecture/sprint4_phase4_completion_and_final_audit_20260430.md) — 协议契约最终态
- [ ] [`../architecture/dsg/dsg_l1_5_implementation_completion_20260506.md`](../architecture/dsg/dsg_l1_5_implementation_completion_20260506.md) — DSG Chat 2 收口
- [ ] [`../architecture/goslo_modularization_completion_20260506.md`](../architecture/goslo_modularization_completion_20260506.md) — GOSLO 模块化收口
- [ ] [`../architecture/cross_chat_pending_registry_20260507.md`](../architecture/cross_chat_pending_registry_20260507.md) — 跨 chat 待办登记

### §2.2 待产出

- [ ] `capabilities_inventory.md` 能力四态表（应有 / 已有 / 缺 / 漂）
- [ ] `capability/brain_tools_inventory.md`（10 brain tools）
- [ ] `capability/parrot_actions_v1.md`（4 enum）
- [ ] `capability/triggers_inventory.md`（9 triggers）
- [ ] `capability/ref_kinds_inventory.md`（4 + 4）
- [ ] `capability/bucket_kinds_inventory.md`（6）
- [ ] `capability/staged_ref_kinds.md`（9）
- [ ] `capability/model_manifest_v1.md`（GOSLO Manifest + Capability）

### §2.3 完成判据

- [ ] 每能力 frontmatter 9 字段 + driven_by 必填
- [ ] 缺口标记清晰（与 cross-chat-registry NEED-* 对账 100%）
- [ ] 漂移标记清晰（既有但 Phase 4 §8 标 experimental 的临时实现一律标 experimental）

### §2.4 sync report 落点

`_sync/4-B-cap_completion.md`

---

## §3 Stage 3 — 4-B-{wire, cross, in} 三 chat 并行接口提炼

**起始日**：T+4d（4-B-cap sign off 后）  
**预计完成**：T+8d  
**写入位置**：`wire/` + `cross_process/` + `in_process/`

### §3.1 4-B-wire（9 文件，2 天）

- [ ] `wire/ecp_event_v1.md`
- [ ] `wire/ecp_state_v1.md`
- [ ] `wire/ecp_ack_v1.md`
- [ ] `wire/ecp_command_meta_v1.md`
- [ ] `wire/livekit_rpc_v1.md`
- [ ] `wire/ref_binding_v1.md`
- [ ] `wire/node_edge_kind_v1.md`
- [ ] `wire/photo_double_channel_v1.md`
- [ ] `wire/topic_matrix.md`

输入：Stage 2 capability + Phase 4 §8 + cs_parity tests + DSG 7 协议 wire 部分

sync report：`_sync/4-B-wire_completion.md`

### §3.2 4-B-cross（6 文件，2 天）

- [ ] `cross_process/http_upload_photo.md`
- [ ] `cross_process/redis_pub_sub.md`
- [ ] `cross_process/redis_stream.md`
- [ ] `cross_process/redis_hash.md`
- [ ] `cross_process/graphiti_v1.md`
- [ ] `cross_process/castle_to_mecha_placeholder.md`

sync report：`_sync/4-B-cross_completion.md`

### §3.3 4-B-in（10 文件，2-3 天，主战场）

- [ ] `in_process/attach_helpers.md`
- [ ] `in_process/observer_event_bus.md`
- [ ] `in_process/dsg_trigger_outcome_v2.md`
- [ ] `in_process/ingest_runner.md`
- [ ] `in_process/intent_workspace_backend.md`
- [ ] `in_process/pool_admission_policy.md`
- [ ] `in_process/attention_strategy.md`
- [ ] `in_process/selection_c_state_context.md`
- [ ] `in_process/identify_object_budget.md`
- [ ] `in_process/refs_hint_writer.md`

⚠️ in_process 是隐式接口最多的层；4-B-in 必须严守"不反推代码"原则——所有 driven_by 必须 cite Stage 1/2 输出。

sync report：`_sync/4-B-in_completion.md`

---

## §4 Stage 4 — 主 chat 验证 + upgrade_roadmap

**起始日**：T+8d  
**预计完成**：T+9d

- [ ] 主 chat 跑 grep 验证脚本（详 [`../architecture/interface_extraction_plan_20260507.md §7.5.2`](../architecture/interface_extraction_plan_20260507.md)）
- [ ] 输出 `_sync/grep_verification_20260507.md`
  - [ ] ✅ 验证通过的接口面
  - [ ] ⚠️ 漂移：代码有但 doc 无
  - [ ] 🆕 缺口：doc 有但代码无
- [ ] 输出 `upgrade_roadmap.md`
  - [ ] 缺口清单 → 推 NEED-* / TODO(Chat4-*) / TODO(P3-*) 标签（与 cross-chat-registry §5 同步）
  - [ ] 漂移清单 → 决定锁 / 升 / 删
  - [ ] 优先级排序（high / mid / low）
  - [ ] 修复 chat 路径（哪个标签去哪个 chat）

---

## §5 Stage 5 — INDEX 收口 + 完成报告

**起始日**：T+9d  
**预计完成**：T+10d

- [ ] 主 chat 把 6 个 sync report merge 到 `INDEX.md`
- [ ] 写 `deprecation.md` / `extension_points.md` / `schema_evolution.md` / `change_impact_table.md`
- [ ] 写 `interface_extraction_completion_20260507.md`（参考 lineb / dsg_l1_5 / goslo_mod 三份完成报告格式）
- [ ] 测试基线 ≥ 423/423 + Phase 4 §8 13 锁 0 漂移 + cs_parity 4/4
- [ ] cross-chat-registry §8 历史区追加 Chat 4 close 的标签
- [ ] active_context.md 头部追加完成提示

---

## §6 4-A 实施轨（与 B 轨并行）

**起始日**：T0  
**预计完成**：T+9d

按爆炸半径排序：

- [ ] **#1 NEED-P2.5-PLAN-INTEGRATION**（4 个 plan-* TODO）
  - [ ] TODO(Chat4-plan-dispatch) — `plan_registry.py:118,141`
  - [ ] TODO(Chat4-plan-nanobot-correlation) — `scheduler/nodes.py:56` + `dispatch_task.py:34,45`
  - [ ] TODO(Chat4-plan-step-result-route) — `scheduler/service.py:137,168` + `constants.py:18`
  - [ ] TODO(Chat4-plan-step-timeout) — `scheduler/service.py:191`
  - [ ] TODO(Chat4-plan-bb-namespace) — `scheduler/blackboard.py:22`
- [ ] **#2 NEED-P2.5-ARCHIVE-LLM** — `dsg/archive/conversation.py:402,432`
- [ ] **#3 NEED-P2.5-NANOBOT-HEARTBEAT** — `bus/nanobot_consumer.py` 加心跳写者
- [ ] **#4 TODO(Chat4-disk-recover)** — `intent_workspace_backend.py:115`
- [ ] **#5 NEED-P3-CAPABILITY-GATING**（**user §10 Q1 待答**）— Brain ModelManifestRegistry stub + tool 注册过滤

sync report：`_sync/4-A_implementation_completion.md`

---

## §7 4-C freeze test 扩展（与 B 轨并行）

**起始日**：T+4d（与 4-B-wire 同启动）  
**预计完成**：T+8d

推荐前 5 项扩展（**user §10 Q4 待答**）：

- [ ] NodeKind 6 项 freeze test（推 cs_parity 模式）
- [ ] EdgeKind 8 项 freeze test
- [ ] RefKind / RefTargetKind 4+4 项 freeze test
- [ ] BB key namespace 26 项 freeze test
- [ ] Topic 常量 5 项 freeze test

sync report：`_sync/4-C_freeze_test_summary.md`

---

## §8 user §10 待答 / 已答清单

### §8.1 已 sign off（Q9-Q13 amended）

- [x] Q9 = Z（driver 主线 + bottom-up grep 验证）
- [x] Q10 = req-first 5 阶段（amended）
- [x] Q11 = layered_parallel
- [x] Q12 = subdir_per_layer（**目录路径修订到 `.cursor/memory/interfaces/`**）
- [x] Q13 = req-first-2d（amended）

### §8.2 待答（Q1-Q8）

- [ ] Q1: NEED-P3-CAPABILITY-GATING 是否纳入 Chat 4？（推荐：取）
- [ ] Q2: 接口分类主+副维度（推荐：拓扑边界 + audience；amendment 已隐含 sign off，但要不要正式标记？）
- [ ] Q3: 文档形态（推荐：单份 SSOT 多文件 + 机器层；amendment 已隐含）
- [ ] Q4: freeze test 扩展范围（推荐：前 5 项）
- [ ] Q5: 需求覆盖度（推荐：仅接口相关子集；4-B-req 范围影响）
- [ ] Q6: 起点 module_map_p2 §10.4（amendment：作 capability 推导参考，**不主驱动**；req-first amended 后 §10.4 仅是 4-B-cap 输入之一）
- [ ] Q7: 实施 TODO 与 doc 先后（推荐：A+D，先 MVP 试 2 天再三轨）
- [ ] Q8: Chat 4 实施 chat 框架（推荐：B 三 chat 并行；已被 Q11+Q12 细化为 7 sub-chat）

### §8.3 amendment 后新增决策点

- [ ] Q14: **4-B-req 在主 chat 跑还是 fork sub-chat？**
  - 主 chat 跑：上下文热（已读完所有完成报告 + ADR + Phase 4 §8 + module_map）；token 消耗大但快
  - fork sub-chat：clean context；新 chat 重读必读清单（参考 §7.5.7 入场 prompt 模板）；token 利用更优但需 1-2 小时启动成本
  - **user 答**：[ ] 主 chat / [ ] fork sub-chat

---

## §9 commit 检查点

每个 sync 落地时建议 commit（参考 `../commit_guidelines.md`）：

- [ ] commit 1（T0）：interfaces/ 骨架 + 规划稿 amendment（INDEX / README / methodology / TODO / 5 子目录占位）
- [ ] commit 2（T+2d）：Stage 1 — needs + app_flow inventory
- [ ] commit 3（T+4d）：Stage 2 — capabilities + capability/ 7 文件
- [ ] commit 4（T+8d）：Stage 3 — 25 接口文件
- [ ] commit 5（T+9d）：Stage 4 — grep 验证 + upgrade_roadmap
- [ ] commit 6（T+10d）：Stage 5 — INDEX 收口 + 完成报告

---

## §10 关联

- 父规划稿：[`../architecture/interface_extraction_plan_20260507.md`](../architecture/interface_extraction_plan_20260507.md)
- INDEX：[`INDEX.md`](INDEX.md)
- README：[`README.md`](README.md)
- methodology：[`methodology.md`](methodology.md)
- 跨 chat 待办登记：[`../architecture/cross_chat_pending_registry_20260507.md`](../architecture/cross_chat_pending_registry_20260507.md)

---

## §11 变更日志

- **2026-05-07**：本 TODO 创建（T0 骨架建立）。Q9-Q13 已 sign off + amendment 已落地。等 Q14（4-B-req 在主 chat 跑还是 fork）决策启动 Stage 1。
