---
status: skeleton / chat-4-active
category: interface-ssot
status_note: "Chat 4 接口提炼总入口 — 单一真源 INDEX。在 sub-chat 完成 sync 后由主 chat merge 落实。当前 = 阶段 0 骨架建立，等 4-B-req 启动写 needs_inventory + app_flow_inventory。"
last_reviewed: 2026-05-07
authoritative_for: "Chat 4 全局接口提炼成果索引 / sub-chat 间 cross-link 解析 / interface_id 命名空间真源"
parent_doc: "../INDEX.md"
parent_plan: "../architecture/interface_extraction_plan_20260507.md"
ai_priority: high
ai_audience: both
---

# Chat 4 接口提炼 SSOT — INDEX

> **入口规则**：所有接口提炼成果通过本 INDEX 索引；sub-chat 不直写 INDEX，由主 chat 在 sync 点 merge。
>
> **当前状态**：T0 骨架建立（2026-05-07）。**4-B-req 尚未启动**——待 user 决定"在主 chat 直接跑"还是"fork 4-B-req sub-chat"。

---

## §0 阅读路径（按 audience）

| audience | 入口 |
|:--|:--|
| **新接手 chat / 想理解全貌** | `README.md`（顶层导览）→ `methodology.md`（方法论原则）→ 本 INDEX → 按主维度选拓扑边界子目录 |
| **AI（dense matrix 优先）** | 本 INDEX §1-§4（拓扑边界三表）+ 各接口文件 frontmatter 9 字段 |
| **写 sub-chat 的 chat** | `../architecture/interface_extraction_plan_20260507.md` §7.5 + `methodology.md` + 本 INDEX 相关子目录 |
| **找单个接口** | grep `interface_id` 字段（每接口唯一）|

---

## §1 拓扑边界 — wire（跨语言 / cross-language）

> Phase 4 §8 13 锁全部归属此层；cs_parity 4/4 在此层守护。**0 漂移要求**。

| interface_id | 文件 | status | driven_by | last_locked |
|:--|:--|:--|:--|:--|
| _(待 4-B-wire Stage 3 写)_ | `wire/<file>.md` | — | — | — |

预期文件清单（详 `../architecture/interface_extraction_plan_20260507.md` §4.2）：

- `wire/ecp_event_v1.md` — EcpEvent envelope + 13 EcpEventType + 8KB + dedup
- `wire/ecp_state_v1.md` — parrot.ecp.state topic + 1Hz + event-driven
- `wire/ecp_ack_v1.md` — RPC return value + active_locks
- `wire/ecp_command_meta_v1.md` — EcpCommand.meta typed slot
- `wire/livekit_rpc_v1.md` — 7 RPC method
- `wire/ref_binding_v1.md` — RefBinding wire schema
- `wire/node_edge_kind_v1.md` — NodeKind 6 / EdgeKind 8
- `wire/photo_double_channel_v1.md` — preview EcpEvent + asset HTTP 双通道
- `wire/topic_matrix.md` — 5 LiveKit DataChannel topic 一览

---

## §2 拓扑边界 — cross_process（同进程外 / Castle 边界外）

| interface_id | 文件 | status | driven_by | producer |
|:--|:--|:--|:--|:--|
| _(待 4-B-cross Stage 3 写)_ | `cross_process/<file>.md` | — | — | — |

预期文件清单：

- `cross_process/http_upload_photo.md` — FastAPI 7889 `/upload/photo`
- `cross_process/redis_pub_sub.md` — 各 channel
- `cross_process/redis_stream.md` — parrot.events.log
- `cross_process/redis_hash.md` — parrot:nanobot_heartbeat / parrot:resource_locks
- `cross_process/graphiti_v1.md` — add_episode / search / group_id
- `cross_process/castle_to_mecha_placeholder.md` — Phase 5+ A10 占位

---

## §3 拓扑边界 — in_process（Castle Brain Python 进程内）

> 主战场 — 代码 grep 验证最重要的层；隐式接口集中地。

| interface_id | 文件 | status | driven_by | producer |
|:--|:--|:--|:--|:--|
| _(待 4-B-in Stage 3 写)_ | `in_process/<file>.md` | — | — | — |

预期文件清单：

- `in_process/attach_helpers.md` — 5 个 attach_* helper（boot 序）
- `in_process/observer_event_bus.md` — 5 observer (snapshot/sighting/bbox/focus/photo)
- `in_process/dsg_trigger_outcome_v2.md` — 5 路上行
- `in_process/ingest_runner.md` — commit_observation 单一写门
- `in_process/intent_workspace_backend.md` — InMemory / Disk
- `in_process/pool_admission_policy.md` — 6 BucketKind
- `in_process/attention_strategy.md` — Decay / Mechanism / Fold strategies
- `in_process/selection_c_state_context.md` — _state_context + 3 tool wrappers
- `in_process/identify_object_budget.md` — _budget 1.9s
- `in_process/refs_hint_writer.md` — refs / hint_writer

---

## §4 拓扑边界 — capability（能力层副维度，单独成包）

| interface_id | 文件 | status | driven_by |
|:--|:--|:--|:--|
| _(待 4-B-cap Stage 2 写)_ | `capability/<file>.md` | — | — |

预期文件清单：

- `capability/brain_tools_inventory.md` — 10 brain tools
- `capability/parrot_actions_v1.md` — ParrotAnimation / BodyState / BehaviorMode / CognitiveState
- `capability/triggers_inventory.md` — 9 triggers
- `capability/ref_kinds_inventory.md` — 4 RefKind / 4 RefTargetKind
- `capability/bucket_kinds_inventory.md` — 6 BucketKind
- `capability/staged_ref_kinds.md` — 9 StagedRefKind
- `capability/model_manifest_v1.md` — GOSLO ModelManifest

---

## §5 上游驱动 inventory（amendment 后的 driver 真源）

| 文件 | 角色 | 写者 |
|:--|:--|:--|
| `needs_inventory.md` | Stage 1 — 67 需求项 + 8 步 App 流程 → 功能需求清单（**不绑代码**）| 4-B-req |
| `app_flow_inventory.md` | Stage 1 — `ar_app_flow_ui_design §4` 8 步逐步 → 触动什么能力 | 4-B-req |
| `capabilities_inventory.md` | Stage 2 — 能力四态表（应有 / 已有 / 缺 / 漂）| 4-B-cap |

---

## §6 收口产物（主 chat 写）

| 文件 | 角色 |
|:--|:--|
| `upgrade_roadmap.md` | Stage 4 — 缺口 + 漂移 + upgrade plan（推 NEED-* 标签）|
| `deprecation.md` | 接口废弃流程（per ADR §5.5）|
| `extension_points.md` | 第三方扩展占位（per ADR §5.5）|
| `schema_evolution.md` | schema_version 演进策略 |
| `change_impact_table.md` | 变更影响表 |

---

## §7 sub-chat sync 区

| sub-chat | sync report 路径 | 状态 |
|:--|:--|:--|
| 4-A 实施轨 | `_sync/4-A_implementation_completion.md` | ⏳ 待启动 |
| 4-B-req（Stage 1）| `_sync/4-B-req_completion.md` | ⏳ 待启动 |
| 4-B-cap（Stage 2）| `_sync/4-B-cap_completion.md` | ⏳ 待启动 |
| 4-B-wire（Stage 3）| `_sync/4-B-wire_completion.md` | ⏳ 待启动 |
| 4-B-cross（Stage 3）| `_sync/4-B-cross_completion.md` | ⏳ 待启动 |
| 4-B-in（Stage 3）| `_sync/4-B-in_completion.md` | ⏳ 待启动 |
| 4-C freeze test | `_sync/4-C_freeze_test_summary.md` | ⏳ 待启动 |
| 主 chat Stage 4 验证 | `_sync/grep_verification_20260507.md` | ⏳ 待启动 |

---

## §8 关联

- 父规划稿：[`../architecture/interface_extraction_plan_20260507.md`](../architecture/interface_extraction_plan_20260507.md)
- 父 ADR：[`../architecture/adr_protocol_upgrade_and_interface_refinement_background_20260504.md`](../architecture/adr_protocol_upgrade_and_interface_refinement_background_20260504.md)
- Phase 4 §8 锁：[`../architecture/sprint4_phase4_entry_20260430.md`](../architecture/sprint4_phase4_entry_20260430.md)
- 跨 chat 待办登记表：[`../architecture/cross_chat_pending_registry_20260507.md`](../architecture/cross_chat_pending_registry_20260507.md)
- 方法论原则：[`methodology.md`](methodology.md)
- 顶层导览：[`README.md`](README.md)
- TODO 主时间线：[`TODO.md`](TODO.md)

---

## §9 变更日志

- **2026-05-07**：本 INDEX 创建（T0 骨架建立）。目录树 + 子目录占位 + 预期文件清单 + 7 sub-chat sync 区。等 4-B-req 启动后由其填 §5 inventory 头部。
