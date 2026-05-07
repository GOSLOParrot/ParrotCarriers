---
status: stage-4-completion
category: upgrade-plan
chat_4_stage: "Stage 4"
status_note: "Chat 4 Stage 4 upgrade_roadmap — 缺口 + 漂移 + upgrade plan 收口。来自 grep_verification + Stage 1+2+3 残留 + cross-chat-registry 12 NEED-* 对账。每项标修复 chat 路径 + 优先级 + 触发条件。"
last_reviewed: 2026-05-07
authoritative_for: "Chat 4 之后的 upgrade 总入口；推 NEED-* / TODO(Chat4-*) / TODO(P3-*) 标签到对应修复 chat"
parent_doc: "INDEX.md"
ai_priority: high
ai_audience: both
sources:
  - "_sync/grep_verification_20260507.md (Stage 4 grep)"
  - "../architecture/cross_chat_pending_registry_20260507.md (12 NEED-* 标签)"
  - "_sync/4-B-req_completion.md (Stage 1)"
  - "_sync/4-B-cap_completion.md (Stage 2)"
  - "_sync/4-B-wire_completion.md (Stage 3 wire)"
---

# Chat 4 Upgrade Roadmap（2026-05-07）

> 接口提炼 chat 收尾的"未来工作"清单。**Chat 4 不主场修这些**——本文是把缺口 / 漂移 / Phase 5+ 工作分流到对应修复 chat 的总图。

---

## §0 TL;DR

| 类别 | 数 |
|:--|:--|
| **High priority — Chat 4 主场剩余实施**（4-A 实施轨）| 5 |
| **Mid priority — proposed-upgrade**（推 P3 / 协议升级）| 8 |
| **Low priority — 命名 / 注释 / 文档完善** | 5 |
| **Total** | **18** |

---

## §1 High priority — Chat 4 4-A 实施轨（5 项）

> 这些是 Chat 4 主场——4-A 实施轨完成后，本节标 ✅ resolved。

| # | 标签 | 修复 | 影响接口文件（producer 待回填）| 优先级 |
|:--|:--|:--|:--|:--|
| 1 | NEED-P2.5-PLAN-INTEGRATION（4 plan-* TODO + bb-namespace）| `plan_registry.start_executing` 真调 dispatch_task；scheduler 路由 plan_id/step_id；timeout 处理 | `cross_process/redis_stream.md §2.1` + `in_process/dsg_trigger_outcome_v2.md` plan_request 通道 + `in_process/intent_workspace_backend.md` § 4 | 🔴 high |
| 2 | NEED-P2.5-ARCHIVE-LLM | archive_to_graphiti 真 LLM 蒸馏 + Graphiti.add_episode | `cross_process/graphiti_v1.md §3.2` + `in_process/dsg_trigger_outcome_v2.md` archive_request 通道 | 🟡 mid（4-A 主场）|
| 3 | NEED-P2.5-NANOBOT-HEARTBEAT | nanobot 心跳 HSET 写者 | `cross_process/redis_hash.md §3.1` | 🟡 mid（4-A 主场）|
| 4 | TODO(Chat4-disk-recover) | DiskBackend.recover() 真路径 | `in_process/intent_workspace_backend.md §3.1` | 🟢 low（4-A 主场）|
| 5 | NEED-P3-CAPABILITY-GATING（**user §10 Q1 待答**）| Brain ModelManifestRegistry stub + tool 注册过滤 | 新接口 wire/ecp_command_meta_v1.md §5 升级 + 新 in_process/capability_gating.md | 🟡 mid（取舍）|

---

## §2 Mid priority — proposed-upgrade（推下游 chat，8 项）

| # | 标签 | 修复 chat | 接口影响 |
|:--|:--|:--|:--|
| 6 | NEED-P2.5-A persona 外置 | DSG 协议升级 chat（与 4 类块设定块统一）| 新 capability/persona_v1.md + wire/preset_change_v2.md |
| 7 | NEED-P2.5-B Unity menu DSG bucket / scene UI | AR 工作区独立 chat | 新 capability/menu_ui_v1.md |
| 8 | NEED-P3-A body_state 解锁 | P3 wire 升级 ADR chat | wire/ecp_state_v1.md §6 升级 |
| 9 | NEED-P3-B 4 类块注册表 | DSG 协议升级 chat | 新 wire/preset_change_v2.md + capability/{model/persona/mode/scene}_block_v1.md |
| 10 | NEED-P3-C 预设 schema | 同上 | 新 capability/preset_v1.md + cross_process/preset_storage_v1.md |
| 11 | NEED-P3-D node-canvas UI | AR 工作区独立 chat | 新 capability/node_canvas_ui_v1.md |
| 12 | NEED-P3-E 默认菜单 fallback | 同上 | capability/menu_ui_v1.md §fallback |
| 13 | TODO(P3-Wire-PlanUI) | P3 wire 升级 ADR chat | 新 wire/plan_ui_v2.md（plan.proposed / plan.approved 等 EcpEventType）|

---

## §3 P3 仿生升级（5 项）

| # | 标签 | 修复 chat | 接口影响 |
|:--|:--|:--|:--|
| 14 | TODO(P3-fold-bionic) | P3 仿生升级 chat | `in_process/attention_strategy.md §2`（FoldStrategy 真实施）|
| 15 | TODO(P3-attention-spreading) | 同上 | `in_process/attention_strategy.md §1.3`（SpreadingActivationPlaceholder → 真 spreading）|
| 16 | TODO(P3-RefHealth) | 同上 / DSG 协议升级 chat | `in_process/refs_hint_writer.md §5`（refs.verify_ref 真验证）|
| 17 | TODO(P3-multi-scene) | P3 / A10 接入 chat | `in_process/pool_admission_policy.md §6`（多 SceneType profile）|
| 18 | A10 接入 / Castle ↔ Mecha | A10 接入 chat | `cross_process/castle_to_mecha_placeholder.md` |

---

## §4 Low priority — 命名 / 注释 / 文档完善（来自 grep 验证）

| # | 类别 | 修复 |
|:--|:--|:--|
| L1 | attach_helpers.md §1 列表扩展到 13 attach helper（grep §1 发现）| Chat 4 末段或 4-A 实施轨末段（5 分钟工作量）|
| L2 | attention 命名一致化（AttentionDecayStrategy vs AttentionDecayPolicy）| 推 P3 / DSG 协议升级 chat（避免 wire 影响）|
| L3 | observer_event_bus.md §2 加 register_phase4_observers 显式描述 | Chat 4 末段（doc 微调）|
| L4 | 4-C freeze test 推扩展 #6：RPC method name 常量化 + cs_parity（grep §5）| 4-C 落地时考虑 |
| L5 | NodeKind / EdgeKind / RefKind / RefTargetKind 4 项 freeze test cs_parity（推 4-C 前 5 项之首）| 4-C 落地（推荐 user §10 Q4 选前 5）|

---

## §5 漂移已知项（不需修，但 doc 化）

| 项 | 状态 | 处置 |
|:--|:--|:--|
| `transient/last_sighting_event` BB key 无写者（Phase 4 终审计 Finding A）| proposed (low priority) | observer_event_bus.md §5 已标 |
| Phase 4 临时实现 6 项 standalone（FocusBboxThreshold / selection-C / 1.9s budget / IngestRunner factory / SpreadingActivationPlaceholder / archive_to_graphiti）| experimental | 接口 frontmatter 已全标 status=experimental |
| Phase 4 W6-7 RefBinding 100% UNRESOLVED | 设计意图（不是 bug）| ref_binding_v1.md §5 + refs_hint_writer.md §4 已标 |
| LineB STT-LLM-TTS 时序差异（200-600ms 多）| pending Editor smoke axis-1 | selection_c_state_context.md §4 已标；推 LineB Editor smoke chat |

---

## §6 修复 chat 路径汇总（与 cross-chat-registry §5 对账）

| 修复 chat | 处理项 |
|:--|:--|
| **Chat 4 4-A 实施轨** | #1-#5（NEED-P2.5-PLAN-INTEGRATION + ARCHIVE-LLM + NANOBOT-HEARTBEAT + disk-recover + capability-gating 可选） |
| **Chat 4 4-C freeze test** | L4 + L5（推 RPC method name + NodeKind/EdgeKind/RefKind cs_parity） |
| **Chat 4 末段（doc 微调）** | L1 + L3 |
| **DSG 协议升级 chat（菜单画布主线）** | #6 + #9 + #10 + L2（部分） |
| **AR 工作区独立 chat（菜单 UI）** | #7 + #11 + #12 |
| **P3 wire 升级 ADR chat** | #8 + #13 |
| **P3 仿生升级 chat** | #14 + #15 + #16 + L2（部分） |
| **P3 / A10 接入 chat** | #17 + #18 |
| **LineB Editor smoke chat** | LineB 时序差异验证 |

---

## §7 cross-link

- 父 sync：[`_sync/grep_verification_20260507.md`](_sync/grep_verification_20260507.md)
- cross-chat-registry：[`../architecture/cross_chat_pending_registry_20260507.md`](../architecture/cross_chat_pending_registry_20260507.md)（NEED-* + TODO(Chat4-*) + TODO(P3-*) 真源）
- methodology：[`methodology.md`](methodology.md)
- INDEX：[`INDEX.md`](INDEX.md)
