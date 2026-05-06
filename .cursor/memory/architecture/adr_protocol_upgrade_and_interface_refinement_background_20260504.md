---
status: ratified
category: ADR
adr_id: ADR-PROTOCOL-INTERFACE-001
status_note: "ADR 风格的'协议升级介绍 + 接口提炼背景'单文档收集；scope 仅"收集 + 引用 + 派发"，0 修改 Phase 4 entry §8 锁定值与 audit_identify_object §9 实施口径。下游接口提炼 chat 拿本 ADR 当 SSOT 输入。"
last_reviewed: 2026-05-04
decision_owner: "Sprint 4 Phase 4 主 chat fork (本 chat) + 用户 sign off 2026-05-04"
supersedes: []
superseded_by: []
related:
  - ".cursor/memory/architecture/sprint4_phase4_completion_and_final_audit_20260430.md"
  - ".cursor/memory/architecture/sprint4_phase4_entry_20260430.md §8"
  - ".cursor/memory/architecture/sprint4_phase4_brain_self_audit_20260430.md"
  - ".cursor/memory/architecture/sprint4_phase4_online_smoke_completion_20260504.md"
  - ".cursor/memory/architecture/adr_l1_5_source_dispatch_extension_space_20260504.md"
  - ".cursor/memory/architecture/audit_identify_object_no_screenshot_20260420.md §9"
  - ".cursor/memory/architecture/sprint4_phase4_downstream_chat_dispatch_plan_20260504.md"
  - "src/parrot/shared/ecp_event.py"
  - "src/parrot/shared/bb_schema.py"
  - "src/parrot/dsg/l2b_types.py"
  - "src/parrot/shared/ref_binding.py"
ai_priority: high
ai_audience: "下游接口提炼 chat / 独立审计 chat / Sprint 4 总结报告 chat / 多角色架构演进 (Phase 5+) chat"
---

# ADR-PROTOCOL-INTERFACE-001 — Sprint 4 协议升级介绍 + 接口提炼背景

> **本文用途**：Sprint 4 Phase 4 协议升级"升了什么 + 锁了什么 + 留了什么"的单文档收集，作为下游"接口提炼和接口文档完成"chat 的 SSOT 输入。
>
> **scope 边界**：仅收集 + 引用 + 派发；**不实施任何代码改动**、**不动 Phase 4 锁定值**、**不深度展开 §5.1 提到的 2 个 motivating example**、**不裁决双份 vs 单份接口文档**。
>
> **关键基调**（用户 2026-05-04 原话）：
>
> > 我们现在的目的是提炼出 ADR 的收集和背景，已经目前完成的协议 和 对"接口提炼和接口文档完成"这个最终任务，收集协议升级部分的完成任务和约束和遗留问题汇总等等。

---

## §0 TL;DR

| 维度 | 一句话 |
|:--|:--|
| **协议升了什么** | 从 Phase 3 ECP-minimal（per-RPC ack）→ Phase 4 完整 ECP V2：13 EcpEventType + 26 BB key + 4 LiveKit topics + RefBinding + Echo 全链路 + 双通道 Photo + 跨语言契约（test_cs_parity 守护） |
| **接口提炼最终目标** | 把"已锁的 wire 协议合同"提炼成正式接口文档，回答用户 2 个 motivating examples（角色切换 / 双份 vs 单份接口文档） + 隐含需求（schema 演进 / 多 deploy / 多角色 / 稳定性签名） |
| **当前距离最终目标的差距** | wire 协议 ✅ 锁；BB schema ✅ 锁；跨语言守护 ✅；**但**：SDK / 扩展面 / 接口文档组织 / 角色切换面 / schema 演进策略 / 多 deploy 边界 — 全部未提炼。本 ADR **不解决**这些，只 input 给下游 |

---

## §1 Sprint 4 协议升级"升了什么" — 全景介绍

> 本章是什么：让没经历过 Sprint 4 的 chat / 人 5 分钟内理解 Phase 4 协议升级的形状，**不复制已有 doc 内容**，引用为主。

### §1.1 Phase 4 之前的协议状态

| Phase | 协议形态 | 关键 anchor |
|:--|:--|:--|
| Phase 1 (ECP-minimal) | per-RPC `_ecp` envelope（command_id + expires_at + active_locks + ack status 11 项） — 解决 fire-and-forget 与体感分叉 | `architecture/sprint4_ecp_minimal_audit_20260429.md` §2-3 |
| Phase 2 (EcpState schema) | EcpState 周期上报 + connection_health 4 态聚合 + intent.disconnect / health.changed event schema | `architecture/sprint4_protocol_v2_ecp.md` §5.3 |
| Phase 3 (lifecycle / 防御性) | 11 态 Unity FSM + 6 步 graceful shutdown chokepoint + R1-R6+D5 audit fix | `architecture/sprint4_phase3_l3_entry_20260429.md` §7.5 |

### §1.2 Phase 4 升级了什么（W0-W8 周次维度）

> 全部周次完成度见 `sprint4_phase4_completion_and_final_audit_20260430.md` §1.1（不复制）

按"协议层 / 工具层 / 跨语言 / 数据流"四个维度归纳本次升级的真实增量：

| 维度 | 新增 | 真源 |
|:--|:--|:--|
| 协议 wire envelope | `EcpEvent` 跨语言信封（reliable DataChannel topic `parrot.ecp.event`，13 个 event_type，8 KB payload 红线，schema_version=1） | `src/parrot/shared/ecp_event.py` |
| 协议 graph 锚定 | `RefBinding`（`ref_id` / `target_kind` / `target_id` / `revision` 不可变迁移路径） | `src/parrot/shared/ref_binding.py` |
| 协议 NodeKind / EdgeKind 扩展 | + `NodeKind.PHOTO`（与 OBJECT 区分；entry §8.1 L7 结构性强制 PhotoEvent 不自动建 ObjectNode）+ 3 EdgeKind（HAS_PHOTO / CAPTURED_VIA / CANDIDATE_SUBJECT，connect 调用 defer Phase 5+） | `src/parrot/dsg/l2b_types.py` |
| BB schema 新增 5 项 producer | `tick/cognitive_state` (W3.A.1) / `transient/current_attention_hint` (W6-7) / `transient/last_sighting_event` (W4-5) / `global/attention_thresholds` (F-05 Echo) / `transient/last_photo_event` (W8) | `src/parrot/shared/bb_schema.py` |
| 工具 ① perch_to_finger | Unity 全链路（手势 → Reflex → 锚定）+ Brain selection-C cognitive_state_tracker 让 LLM 看到三态 | W3.A.2 + W3.A.1 commit chain |
| 工具 ② identify_object | Brain 三段重写（L0 text fast match / L1 Graphiti / L2 option α）+ 1.9s 总预算 + sighting EcpEvent + observer/sighting 异步 archiver | `audit_identify_object_no_screenshot_20260420.md §9` |
| 工具 ③ Focus / BBox + AttentionHint | RefBinding registry + bbox/focus observer + threshold accumulator + hint_writer + AttentionConfig Echo 全链路（Unity SO → Brain handler → FocusBboxThreshold 读 BB） | W6-7 Brain + W6-7 Unity + F-05 |
| 工具 ④ Photo（双通道） | preview EcpEvent 走 reliable DataChannel + asset HTTP POST 走 photo_upload_server FastAPI on 7889 + Castle 本地 cache `data/photos/{yyyy-mm-dd}/{photo_id}.jpg` + photo.asset_uploaded 回程 EcpEvent | W8 Brain 半边 + Unity W8 半边 |
| 跨语言契约 | `test_cs_parity` 4/4 守护（Python `EcpEventType` / `EcpEventSource` / topic 常量 == C# `EcpEventTypeNames` / `EcpEventSourceNames` / `EcpEventConsts`） | `tests/test_ecp_event/test_cs_parity.py` |
| 数据流升级 | LiveKit reliable DataChannel 4 topic 矩阵（`parrot.ecp.event` / `parrot.ecp.state` / `parrot.ecp.health` / `parrot.ecp.intent_disconnect`）+ lossy `parrot.ecp.tick`（drag UI defer） | entry doc §8.2 表 |

### §1.3 协议合同最终态一览（不复制完成报告，只指引）

> **真源**：`sprint4_phase4_completion_and_final_audit_20260430.md` §3（13 EcpEventType / 26 BB key / topic / NodeKind / EdgeKind / RefBinding kinds 全矩阵）

下游接口提炼 chat **必须**读完成报告 §3 全部 5 个子节，本 ADR 不复制。

---

## §2 Phase 4 已完成任务清单（按周次）

> 本章是什么：周次 → 完成度的索引；全表见完成报告 §1.1。

| 周次 | 状态 | 真源链接 |
|:--|:--|:--|
| W0 决策锁 §8 + audit doc §9 | ✅ | 完成报告 §1.1 |
| W1-2 EcpEvent + RefBinding + observer/attention skeleton + cs_parity | ✅ | 同上 |
| W2 收口 transport wire-up | ✅ | 同上 |
| W3.A.1 selection-C cognitive_state_tracker | ✅ | 同上 |
| W3.A.2 Unity perch_to_finger | ✅ | `architecture/sprint4_phase4_w3_a2_a3_completion_20260430.md` |
| W3.A.3 Unity EcpState 三态 | ✅ | 同上 |
| W3 Animation Minecraft-port | ✅ | `architecture/sprint4_phase4_w3_animation_chat_launch_prompt.md` + animation chat completion |
| W4-5 identify_object 三段重写 | ✅ | 完成报告 §1.1 + audit §9 |
| W6-7 Brain (refs + threshold + hint_writer) | ✅ | 同上 |
| W6-7 Unity (BBox/Focus/SO/EchoPub) | ✅ | `architecture/sprint4_phase4_w6_w7_unity_completion_20260430.md` |
| Brain 自审 13 项 finding | ✅ | `architecture/sprint4_phase4_brain_self_audit_20260430.md` |
| F-05 Echo 全链路 ①+②+③ | ✅ | 同上 + ADR-L1.5-001 §3 |
| W8 Brain 半边（PhotoEvent + photo_upload_server） | ✅ | 完成报告 §1.1 |
| W8 Unity 半边（capturePhoto UI / preview / HTTP） | ✅ | 联机 smoke 报告 §3 |
| 联机 smoke #3/#4/#5 Editor 验证 | ✅ | `architecture/sprint4_phase4_online_smoke_completion_20260504.md` |
| 联机 smoke #1/#2 显式跳过 → 留首版正式 App 真机 | 🔒 defer | 同上 §8 |

---

## §3 Phase 4 锁定约束（接口提炼**绝对不能动**的部分）

> 本章是什么：接口提炼 chat 在做任何"重组 / 重命名 / 重构"之前必须知道的硬约束。

### §3.1 entry §8 决策锁 13 条（L1-L13）

逐条对照 + 0 漂移证据见 `sprint4_phase4_completion_and_final_audit_20260430.md` §5.1。本 ADR 仅列**对接口提炼最敏感的 5 条**：

| Lock | 锁定的接口面 | 不能动什么 |
|:--|:--|:--|
| **L2** | EcpEvent topic + 强制字段 + UUID v7 event_id | topic 名 / 字段集 / event_id 格式 |
| **L3** | EcpEvent payload 8 KB 红线 | 不能加大 / 不能去掉 ingest 拒收 |
| **L9** | Δ_focus=0.2 / Δ_bbox=1.0 / threshold=1.0；阈值器在 dsg/attention 不塞 BB；优先级 explicit > BB > DEFAULT | 数值 / 位置 / 优先级 |
| **L11** | identify_object 1.9s 总预算（800 + 200 + 800 + 100ms） | 数值 / 三段 sync 路径 |
| **L13** | dsg/attention/__init__.py 不 export Attention 类符号（防误读为 L3 已落地） | export 集合 |

### §3.2 audit defended 10 条 + parrot_behavior_rules §0.3 体感红线 + §3.7 边界

| 约束源 | 不能动 |
|:--|:--|
| `audit_identify_object_no_screenshot_20260420.md §9` | identify_object 三段口径 + `_deep_search` 移除 + option α 选定 + budget 数值 |
| `parrot_behavior_rules.md §0.3` | tool 同步/异步与 GOSLO 话术一致（felt experience 红线） |
| `parrot_behavior_rules.md §3.7` | Observer / Attention 边界（Observer 不写 L2-B 节点 attention；Attention 不抓帧 / 不写 Graphiti） |
| Brain 自审 §6.3 硬约束 10 条 | Phase 4 既有 lock 全集合 |

### §3.3 跨语言契约（机器可执行守护）

`test_cs_parity` 4/4 测试在 CI / 本地 pytest 跑时，任何对 `EcpEventType` / `EcpEventSource` / topic 常量的单边改动都会立刻 fail。这是接口提炼**唯一**自动化兜底。其他锁全靠 doc + freeze test。

---

## §4 遗留问题与已知漂移

### §4.1 已 defer 到 Phase 5+ 的项（13 项 — 引用，不复制）

> 真源：`sprint4_phase4_completion_and_final_audit_20260430.md §6`（4 象限：协议 / 工具 / 性能 / 治理）

接口提炼 chat 决定接口面时**应**考虑这些 defer 项的"未来形状"，避免现在锁的接口与未来扩展冲突。例：

- 多角色协作 BB scope `peer/`（影响 BB key 命名空间设计）
- Schema 演进策略（schema_version=1→2 接口签名变更治理）
- 对象存储替换（影响 `photo.asset_uploaded` 的 asset_ref 形态）
- HTTP 鉴权（影响 photo_upload_server 与 token_mint 的接口面）

### §4.2 接口面尚未提炼的部分

详见 §5（核心章节）。一句话概括：**wire 协议 ✅ 锁；SDK / 扩展面 / 接口文档组织 ❌ 未做**。

### §4.3 已知 finding 状态

| 来源 | 数量 | 状态 |
|:--|:--|:--|
| Brain 自审（W3.A.1 + W4-5 + W6-7） | 13 | 10 ✅ resolved + 3 reject (Phase 5+) |
| W6-7 Unity cold-read | 3 (F-A22 / F-A4 / F-A33) | 3 ✅ resolved |
| Phase 4 终一致性审计新发现 | 2 (Finding A: last_sighting_event 无写者；GAP-1: EcpState ingest 缺) | GAP-1 ✅ resolved（`brain/ecp_state_ingest.py` 联机 smoke 期间已落地，commit 见 online_smoke 报告 §0）；Finding A 仍 proposed (Phase 5+) |
| 联机 smoke 6 finding | 6 | 1 ✅ resolved（finding-1 安全组）+ 1 ✅ resolved（finding-3 token agentName）+ 4 noted/proposed (low priority) |

**总**：24 项 finding → 17 ✅ resolved + 7 deferred (low + Phase 5+)。0 项阻塞 Phase 4 完成口径。

真源：
- `sprint4_phase4_brain_self_audit_20260430.md`
- `sprint4_phase4_completion_and_final_audit_20260430.md` §5.5
- `sprint4_phase4_online_smoke_completion_20260504.md` §5

---

## §5 接口提炼任务输入（核心章节 — 给下游 chat）

> 本章是什么：下游接口提炼 chat **必须回答**的问题清单 + 现有 doc inventory + 候选维度 + 现状证据。**本 ADR 不在此节做决策**，仅 input。

### §5.1 用户 2 个 motivating examples 的"问题清单"

> 用户 2026-05-04 原话见 fork chat prompt §3.2。本节列**下游 chat 要回答的子问题**，不深度展开。

#### 例 1：角色切换（GOSLO 鹦鹉 → 别的角色，不能飞 / 不同 body 状态机）

涉及的现有 surface（grep 范围给下游 chat，不在此 ADR 深挖）：

- `parrot.shared.parrot_actions.ParrotBodyState` enum（IDLE / FLYING / PERCHING / PERCHED_ON_HAND / DANCING / FROZEN）
- `parrot.shared.parrot_actions.ParrotAnimation` enum（idle / fly / dance / wing_flap / perch / sit / head_bob / sleep）
- `parrot_behavior_rules.md` §0-§7（行为状态规则全文 — 含状态定义 / 兼容矩阵 / 冲突规则 / Tool 注册表 / 优先级链）
- Brain tools `fly_to.py` / `animate.py`（命名假设鹦鹉能飞）
- `unity/.../Parrot/AnimationDriver.cs`（Minecraft Java Parrot procedural animation port — 鹦鹉特化）
- `EcpFrontendState.body_state` / `head_state`（wire 上的状态字符串目前是 ParrotBodyState 取值）
- `selection-C` 的 `_state_context.py`（tool wrapper 把 body / head / cognitive 注入 LLM — 假设具体角色的状态名）
- `BB tick/body_state` writer = `brain.telemetry_receiver`（Unity 向 Brain 上报的字段假设鹦鹉状态机）

下游 chat 要回答的问题：

- 角色 enum 是要**抽象层**（如 `Body3DRoleProfile`：能/不能飞、有/无翅膀、可/不可悬停）还是**第二层 enum**（不同角色各自 ParrotBodyState 等价物）？
- 行为规则文档是否拆**通用框架** + **角色专属附录**？
- Brain tool 命名是否**重命名**（fly_to → move_to / locomote）+ **per-role tool registry**？
- 状态机 wire 形式：`body_state` 字符串是**角色无关 enum**（IDLE / MOVING / RESTING / EMOTING / FROZEN）还是**角色相关字符串**（Brain 端不解析具体值）？
- Animation 接口：Unity 端 `AnimationDriver` 做**角色无关骨骼接口** + 各角色独立子类？
- `parrot_actions.py` 是否拆 `parrot_actions/` 包 + 每角色一个 module？
- selection-C 状态 header 格式：是否需要 per-role schema_version？
- 测试 `test_cs_parity` 如何守护多角色枚举 一致性？

**裁决放在接口提炼 chat。** 本 ADR 仅列问题。

#### 例 2：接口文档组织方式 + 单份 vs 双份（人 / AI）

涉及的现有 surface：

- 整个 `.cursor/memory/architecture/` 目录（45+ ADR / completion report / 决策锁 / 调研笔记）
- 整个 `.cursor/skills/` 目录（11+ skill packages：livekit-unity-lifecycle / video-publish / ar-foundation-api / ar-foundation-samples / client-sdk-unity / livekit-agents / nanobot / parrot-bus-orchestration / dsg-l1-5-l2a-conceptgraph-distilled / etc.）
- `.cursor/memory/INDEX.md`（全局索引）
- `.cursor/memory/active_context.md`（当前阶段入场）
- `.cursor/rules/workspace.mdc` 等 cursor rules
- 实际"接口"代码（`bb_schema.py` BB key 声明 / `ecp_event.py` enum / `ref_binding.py` schema / `l2b_types.py` enum / `EcpEventDto.cs` mirror / `EcpEventDispatcher.cs`）
- `README.md`（顶层 + Unity workspace README）
- 真机 spike doc / brain log / 联机 smoke completion

下游 chat 要回答的问题：

- 接口文档**组织维度**是哪一种（按 wire vs internal / 按角色 / 按 stable vs evolving / 按 deploy / 按 audience）？见 §5.3 候选维度
- **单份 vs 双份**：哪种 doc 形态可以"AI 看得懂的同时人类也能读"？哪些必须分两份？
- AI-priority frontmatter（`ai_priority: high` / `ai_audience`）的现状形式是否够？需要扩展什么字段？
- 接口文档是否应用**机器可读 schema**（如 OpenAPI / JSON Schema / Pydantic export）+ **人类可读 narrative** 双层（机器 schema 自动生成 narrative）？
- `test_cs_parity` 风格的"freeze test"是否应推广到所有接口面（不只 EcpEventType）？
- 接口文档**vs**当前 ADR / completion report / 决策锁 doc 的边界？是否应有**单一接口文档目录** vs 散落在 architecture/ + skills/？
- 多 chat 协作下的接口文档**owner / writer 单一性**怎么强制（类似 BB single-writer 约束）？

**裁决放在接口提炼 chat。** 本 ADR 仅列问题。

### §5.2 当前已存在的"准接口文档" inventory

> 本章是什么：哪些 doc / SKILL / source 文件**已经在做接口文档的事**；下游 chat 评估它们各自定位是否合适。

| 类别 | 文件 / 目录 | 当前定位 | "准接口文档"性质 |
|:--|:--|:--|:--|
| **决策锁** | `sprint4_phase4_entry_20260430.md §8`（13 锁） | Phase 4 协议合同的 doc 真源 | wire schema + 字段集 + 数值锁 |
| **执行式合同** | `src/parrot/shared/ecp_event.py` / `bb_schema.py` / `ref_binding.py` / `dsg/l2b_types.py` | Pydantic / dataclass / Enum 的 SSOT | 协议合同的 code 真源（**double source of truth 风险**：doc 与 code 同时声明字段，下游需要决定哪一份是"接口文档"） |
| **跨语言守护** | `tests/test_ecp_event/test_cs_parity.py` | freeze test | 跨语言契约的可执行保证 |
| **完成报告** | `sprint4_phase4_completion_and_final_audit_20260430.md §3` | Phase 4 协议契约最终态总览 | 接口现状的"快照" |
| **背景 / 设计稿** | `sprint4_protocol_v2_ecp.md` / `sprint4_protocol_ecp_background_20260429.md` | 设计 intent | 接口"为什么这么设计"的 narrative |
| **行为规则** | `parrot_behavior_rules.md` | 行为状态机 + 优先级 + Tool 注册表 | 用户层接口（GOSLO 行为契约） |
| **审计 / finding** | `sprint4_phase4_brain_self_audit_20260430.md` / `audit_identify_object_no_screenshot_20260420.md §9` | 审计 + 漂移记录 | 接口残留与设计借鉴 |
| **skill packages** | `.cursor/skills/livekit-unity-lifecycle/` / `livekit-unity-video-publish/` / `client-sdk-unity/` / `ar-foundation-api/` / `dsg-l1-5-l2a-conceptgraph-distilled/` etc. | 外部技术能力 + 项目踩坑 | 第三方接口的项目特化文档 |
| **调研索引** | `INDEX.md` / `active_context.md` / `module_map_p2.md` / `bus_v4.md` | 全局导航 | 接口入口路由 |
| **下游派发** | `sprint4_phase4_downstream_chat_dispatch_plan_20260504.md` | chat 路径地图 | 接口文档"谁负责"的元接口 |

**评估给下游**：当前接口"信息"散落 11 类、~60 文件 + ~10 source code 模块。**没有任何一处是"接口文档"的 single entry**。下游 chat 决定如何组织。

### §5.3 接口分类候选维度（不投票，列 8 种供下游评估）

| 维度 | 例子 | 优 | 缺 |
|:--|:--|:--|:--|
| 1. **wire vs internal** | wire = EcpEvent / BB; internal = `_state_context` / `_budget` | 跨进程 / 跨语言边界清楚 | 同一概念可能横跨两边 |
| 2. **角色 / 调用方** | Unity 看的 / Brain 看的 / Nanobot 看的 / 外部 SDK 看的 | 读者视角清晰 | 重复内容；某接口对多角色都暴露 |
| 3. **稳定性** | 锁定（Phase 4 §8）/ evolving (Phase 5+ defer) / experimental | "可以依赖"的承诺面清晰 | 状态会变；分类成本 |
| 4. **audience** | AI / 人 / 双 / 工具自动消费（CI 校验） | 文档形式选型驱动 | 同一接口在 AI 与人之间的描述粒度差异大 |
| 5. **lifecycle phase** | boot / runtime / shutdown / persistent | 与 Brain agent 启动序对齐 | 跨 phase 的接口归类难（如 EcpEvent 全 phase 在用） |
| 6. **domain** | state / event / config / behavior / data / RPC | 与现有协议层级对齐 | 维度交叉（EcpEvent 既是 event 又是 wire） |
| 7. **抽象层级** | bytes / topic / schema / behavior contract | 自下而上学习路径清晰 | 高层抽象与低层 binding 的同步成本 |
| 8. **deploy 边界** | single-process（Brain 内 attach helper）/ inproc Unity（C# DTO）/ cross-process（HTTP / DataChannel）/ cross-host（LiveKit / Castle ↔ Mecha） | 与 deploy_snapshot / Castle docker 对齐 | 边界会演化（Phase 5+ Mecha） |

**下游 chat 不必只选一种** — 可以**主维度 + 副维度**（如主"wire vs internal"+ 副"audience"）；本 ADR 不裁决。

### §5.4 单份 vs 双份现状证据（不裁决）

| 样本 doc | 当前形态 | AI 是否能看懂 | 人是否能看懂 |
|:--|:--|:--|:--|
| `sprint4_phase4_entry_20260430.md §8` | 13 表格 + 长 row | ✅（dense matrix 优化）| ⚠ 表格密度高、缩写多、需要交叉引用 |
| `sprint4_phase4_brain_self_audit_20260430.md` | finding 模板 (severity / confidence / category / problem / proposal) | ✅ | ✅ |
| `sprint4_phase4_completion_and_final_audit_20260430.md` | 11 节 + 5 子节 | ✅ | ⚠ 长度密度大；非直接参与者难追 |
| `parrot_behavior_rules.md` | 行为表 + 兼容矩阵 + 优先级链 | ✅ | ✅（接近双份天然形态）|
| `bb_schema.py` 内 inline 注释 | dataclass + 字段 docstring | ✅ | ✅（read code as doc 模式）|
| `EcpEventDto.cs` C# DTO | `[Serializable]` + 字段 + 注释 | ✅ | ✅ |
| `README.md`（项目顶层） | mixed narrative + bullet | ✅ | ✅ |
| skill `livekit-unity-lifecycle/SKILL.md` | 长 narrative + code reference | ✅ | ✅（适合"对外讲" deploy） |

**给下游的 question**：

- AI-priority doc（`ai_priority: high` frontmatter）的格式（dense matrix / 紧凑表）人能否在不阅读多次的情况下看懂？需要补什么？
- 是否需要"自动 narrative 生成"工具链（从 Pydantic schema 生成 markdown）？
- 是否所有接口文档统一带 `audience: ai_only / human_only / both` 字段？

**本 ADR 不裁决。**

### §5.5 隐含需求清单

下游接口提炼 chat 应在文档组织里**预留位置**（不必现在解答）：

| 隐含需求 | 现状 | 接口文档需要回答 |
|:--|:--|:--|
| Schema 演进策略 | schema_version=1 已锁；v2 迁移规则未定（加字段策略 / 删字段策略 / 旧 client graceful degrade） | 接口文档**版本演进章节**模板 |
| 多 deploy 场景 API 边界 | Castle (Brain agent + HTTP services) / Mecha (Phase 5+ A10) / 真机 / Editor 同模代码 | 接口文档**deploy 维度**索引 |
| 多角色协作时接口共享 vs 分叉 | EcpEventSource 已 reserve `nanobot`；BB scope 未加 `peer/`（`completion_and_final_audit §6.1`）| 接口文档**多 producer / single producer 约束**章节 |
| 稳定性签名（哪些 commit 能影响哪些接口面）| 仅 `test_cs_parity` 4 项；无 commit-level 接口面影响指针 | 接口文档**变更影响表**（接口 → 影响范围 → 测试 → 文档） |
| 接口废弃 / 替换流程 | 已有"deferred / superseded / proposed" 状态；无完整 deprecation 流程 | 接口文档**废弃章节**（warning period / migration guide / removal date） |
| 第三方扩展（SDK / Plugin） | 当前是 monolith Brain；无 plugin 注册接口 | 接口文档**扩展点**章节（如何让外部代码 attach observer / register tool / extend BB scope） |

---

## §6 与 Phase 4 §8 锁定值的兼容性证明

**本 ADR 0 修改 Phase 4 §8 锁定值 / audit §9 实施口径 / EcpEvent / BB schema / topic / 8KB / schema_version 任意常量**。

理由：本 ADR 是**收集 + 引用 + 派发**类型，无代码改动、无新接口设计、无 Phase 4 lock 触动。fork chat 范围（fork prompt §2.2）显式禁止上述任何动作。

测试基线：fork chat 不动 Python / C#，pytest 基线（联机 smoke 报告 §7 = 230/230 + ADR-L1.5-001 +11 = 234/234，本 ADR 不动）保持不变。

---

## §7 下游 chat 派发提示

> 本章是什么：下游 chat 拿到本 ADR 后**该读什么 / 该做什么 / 不该做什么**清单。

### §7.1 下游"接口提炼 chat" 入场清单

**必读（按顺序）**：

1. 本 ADR 全文（input SSOT）
2. `sprint4_phase4_completion_and_final_audit_20260430.md` 全文（协议契约最终态、finding 状态、defer 列表）
3. `sprint4_phase4_entry_20260430.md §8`（13 决策锁 — 不能动的部分）
4. `audit_identify_object_no_screenshot_20260420.md §9`（W4-5 实施口径用户澄清）
5. `adr_l1_5_source_dispatch_extension_space_20260504.md`（前置 ADR — Q1/Q2/Q3 决策格式 + 4 chat 路径）
6. `parrot_behavior_rules.md`（行为状态机 + 优先级 — 例 1 角色切换的 surface）
7. 实测协议合同源码：`src/parrot/shared/ecp_event.py` / `bb_schema.py` / `ref_binding.py` / `dsg/l2b_types.py`
8. 跨语言守护：`tests/test_ecp_event/test_cs_parity.py`

**该做的事**：

- 回答 §5.1 用户 2 个 motivating example 的所有"问题清单"子问题（裁决 + 落地路径）
- 评估 §5.2 inventory 的合并 / 拆分 / 重组方案
- 选定 §5.3 候选维度（主维度 + 副维度）
- 裁决 §5.4 单份 vs 双份（如要双份，给出生成机制）
- 在接口文档里**预留** §5.5 隐含需求的位置
- 产出**正式接口文档**（多文件 / 单文件由 chat 自定）+ 索引（INDEX.md update）+ freeze test（推广 `test_cs_parity` 模式）

**不该做的事**：

- 不动 Phase 4 §8 锁定值（必须先 sign off 升级路径 ADR）
- 不动 `audit_identify_object §9` 实施口径
- 不擅自重命名 EcpEventType / BB key / topic（任何重命名走"加新 + 旧 deprecated"，需新 ADR）
- 不引入子类化 `SemanticNode`（违反 ADR-L1.5-001 §4.1 触发条件）
- 不在接口提炼 chat 内做"实施代码"重写（接口提炼 = doc + 必要的非破坏性 refactor；大重构需独立 chat）
- 不写 SDK code（外部扩展接口面是 Phase 5+，本期只**预留位置**）

### §7.2 下游"独立审计 chat" 入场清单

**必读**：本 ADR + 接口提炼 chat 产出的全部文档 + 现有所有 `architecture/audit_*.md` + `sprint4_phase4_*audit*.md`。

**做的事**：

- cold-read 接口提炼成果，找接口面与 Phase 4 锁定值的隐藏冲突
- 检查接口文档的 `ai_audience` 与实际可读性是否对齐
- 扩展 freeze test（`test_cs_parity` 模式）覆盖更多接口面
- 出 finding 报告（参考 `sprint4_phase4_brain_self_audit_20260430.md` finding 模板）

### §7.3 下游"Sprint 4 总结报告 chat" 入场清单

**必读**：本 ADR + 完成报告 + 联机 smoke 报告 + 接口提炼成果 + 独立审计成果。

**做的事**：

- 综合 Phase 1-4 完成态 + 真机 spike 结果（如果在该 chat 启动前完成）
- 写 P2.5 完成汇报
- 给 Phase 5+ 启动 prompt（路径锁 / 范围 / 验收）

### §7.4 角色替换 / 多 deploy / 多角色协作 chat（Phase 5+ — **不在本期触发**）

只在接口提炼 chat **明确返回了"接口面 ready"信号**之后才启动。本 ADR §5.1 / §5.5 列出的隐含需求是这些 chat 的输入。

---

## §8 引用

### §8.1 上游 anchor（本 ADR 的 input）

- `architecture/sprint4_phase4_completion_and_final_audit_20260430.md` — Phase 4 完成态 + 终一致性审计
- `architecture/sprint4_phase4_entry_20260430.md §8` — Phase 4 决策锁 13 条（**不变**）
- `architecture/sprint4_phase4_brain_self_audit_20260430.md` — Brain 自审 13 项 finding
- `architecture/sprint4_phase4_online_smoke_completion_20260504.md` — 联机 smoke 收口
- `architecture/audit_identify_object_no_screenshot_20260420.md §9` — W4-5 实施口径
- `architecture/adr_l1_5_source_dispatch_extension_space_20260504.md` — Phase 4→5 transition ADR / 4 chat 路径锁
- `architecture/sprint4_phase4_downstream_chat_dispatch_plan_20260504.md` — chat 派发地图
- `architecture/sprint4_phase4_protocol_and_interface_adr_fork_chat_prompt_20260504.md` — 本 fork chat 启动 prompt

### §8.2 实测协议合同源码

- `src/parrot/shared/ecp_event.py` — `EcpEvent` / `EcpEventType` (13) / `EcpEventSource` / topic 常量 / 8KB
- `src/parrot/shared/bb_schema.py` — `BB_KEYS` (26) / `BlackboardKey` / `BbScope`
- `src/parrot/shared/ref_binding.py` — `RefBinding` / `RefKind` / `RefTargetKind`
- `src/parrot/dsg/l2b_types.py` — `NodeKind` (6 含 PHOTO) / `EdgeKind` (8 含 W8 3 个) / `SemanticNode` / `ConfirmationStatus` / `Salience`
- `unity/ArSpike/Assets/Scripts/ParrotApp/Ecp/EcpEventDto.cs` — C# wire mirror
- `unity/ArSpike/Assets/Scripts/ParrotApp/Ecp/EcpEventDispatcher.cs` — Unity 下行 router
- `tests/test_ecp_event/test_cs_parity.py` — 跨语言守护 freeze test

### §8.3 行为契约 / 例 1 角色切换 surface

- `.cursor/memory/parrot_behavior_rules.md` — 行为状态机 + 优先级链 + Tool 注册表
- `src/parrot/shared/parrot_actions.py` — `ParrotBodyState` / `ParrotAnimation` / `BehaviorMode` / `CognitiveState` enums
- `unity/ArSpike/Assets/Scripts/ParrotApp/Parrot/AnimationDriver.cs` — Minecraft Java Parrot procedural animation port

### §8.4 文档组织 / 例 2 接口文档 surface

- `.cursor/memory/INDEX.md` — 全局索引
- `.cursor/memory/active_context.md` — 当前阶段入场 + Phase 4 → 5 转换决策
- `.cursor/memory/architecture/` — 45+ ADR / 完成报告 / 决策锁 / 调研笔记
- `.cursor/skills/` — 11+ skill packages（外部技术能力 + 项目特化）
- `.cursor/rules/workspace.mdc` — workspace cursor rules

### §8.5 既有 ADR 风格参考（本 ADR 借鉴）

- `architecture/adr_l1_5_source_dispatch_extension_space_20260504.md` — frontmatter + Q1/Q2/Q3 三栏决策表 + 触发条件升级路线
- `.cursor/skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md` — skill package 紧凑长 doc 风格

---

**ADR-PROTOCOL-INTERFACE-001 完成**。下游接口提炼 chat 拿本文 + §7.1 必读清单作为入场 SSOT，开始实施接口提炼任务。
