---
status: ratified
category: workspace-snapshot
status_note: "DSG 工作区聚合入口 — 把分散在 architecture/ / .cursor/skills/ / docs/InfoCollections/Opus / NewZone/distill_output / src/parrot/dsg/ 的 DSG 设计、决策、调研归到一处。新增 DSG 相关产物时，先在这里登记一行，再决定是否进 INDEX 主表。建立目的是给 DSG 系列设计 chat 当 SSOT 入口（参考 ar_workspace_index.md 模式）。2026-05-06 增补：决策总表 dsg_decisions_master.md + 4 新 DSG skill + NewZone 蒸馏素材池 + LineB 完成报告。"
last_reviewed: 2026-05-06
ai_priority: high
ai_audience: "DSG 系列设计 chat（L1.5 池设计 / 状态生命周期差异化 / L2-B 简单升级 / Phase 5+ A10 接入）入场必读"
parent_doc: "../../INDEX.md"
sibling_workspace: "../ar_workspace_index.md"
---

# DSG 工作区聚合入口

> 创建：2026-05-04（Phase 4 收口 + Phase 5 转换期，与 AR 工作区对位）
> 用途：DSG 模块层（L1.5 / L2-A / L2-B / 触发器 / Ingest 过滤 / Graphiti 桥）相关任务的**单一入口**。下次会话只要打算碰 DSG 的"设计层"，先读这一份再决定继续读什么。
> 边界：本文不复述具体决策；只做**路由 + 角色 + 入口模式**的聚合。深入内容请按链接进对应文件。
> **不做事项**（与本工作区 sign off 的硬约束一致）：不动 ADR-L1.5-001 决策、不动 Phase 4 §8 决策锁、不引入 SemanticNode 子类、不改 ConceptGraph SKILL 蒸馏产物。

---

## 1. 工作区核心产出

### 1.1 决策 / 状态 / 入口（5 份）

| 文件 | 角色 |
|:--|:--|
| `dsg_decisions_master.md` | **决策总表**（master，长期累加）— Chat 2 入场 SSOT；用户已决事项 + status 分级（ratified / provisional / deferred-to-design / deferred-to-P3 / tbd） |
| `dsg_current_state_distilled.md` | **核心**：DSG 当前全景理解蒸馏 — 决策完成点。代码现状 / source / lifecycle / L2-B / 触发器 / Phase 4 锁 / ADR 升级条件 / §11 防爆炸门控分层 / §12 工作记忆延迟归档 |
| `opus_dsg_residual_intent.md` | Opus 09/11/12/17/18/19 中**仍生效**的设计意图蒸馏（distill+cite，原文不动） |
| `source_x_lifecycle_status.md` | 现有 + 规划中的 source × 当前 lifecycle 处理状态对照表（含 Obsidian 三分类 / GOSLO 主动 / A10 占位） |
| `open_questions_for_design_chat.md` | 待设计 chat 回答的开放问题清单（含用户 Q&A 原文）；§0 已决汇总指向 master |

### 1.2 Chat 2 启动 prompt + 8 份产物（2026-05-06 实施完成）

| 文件 | 角色 |
|:--|:--|
| `dsg_l1_5_pool_design_chat_launch_prompt_20260506.md` | **Chat 2 启动 prompt** — 入场必读 6 项 + scope / 锁 / 允许动作 / 提问纪律 / 输出物 / 开局 prompt |
| **`dsg_l1_5_pool_and_lifecycle_design_20260506.md`** | **主设计稿** — 术语表 + 模块布局 + 全局 invariants + 9 处扩展点 |
| `dsg_protocol_pool_v1_20260506.md` | DSG-POOL-V1 — L1.5 Pool 完整 API + Bucket + AdmissionPolicy + RefTable + Timeline |
| `dsg_protocol_trigger_v2_20260506.md` | DSG-TRIGGER-V2 — TriggerOutcome + 5 路上行通道 + 5 个新触发器 |
| `dsg_protocol_intent_event_boundary_v1_20260506.md` | DSG-INTENT-EVENT-V1 — IntentEvent 认知边界 + decay/fold strategy |
| `dsg_protocol_archive_v1_20260506.md` | DSG-ARCHIVE-V1 — 三阶段延迟归档 + ConversationBoundary + 6 jsonl schema |
| `dsg_protocol_scene_snapshot_v1_20260506.md` | DSG-SCENE-V1 — SceneType + LocationTag + 跨切保留 |
| `brain_protocol_intent_workspace_v1_20260506.md` | BRAIN-INTENT-WS-V1 — Brain Intent 层资源暂存（9 StagedRefKind + Backend strategy）|
| `brain_protocol_plan_v1_20260506.md` | BRAIN-PLAN-V1 — Plan-and-Execute 8 状态机 + IntentWorkspace 主存 + L2-B 镜像 |
| **`dsg_l1_5_implementation_completion_20260506.md`** | **完成报告** — 352/352 pytest + Phase 4 § 8 0 漂移 + ADR-L1.5-001 三触发器全未触发 + master 11 条回审完毕 |

阅读顺序（cold start）：

```
workspace_index.md (本文)
  ↓
dsg_current_state_distilled.md (一份能回答全景)
  ↓
dsg_decisions_master.md (用户已决事项作输入，不再讨论 ratified 条目)
  ↓ (按需深读)
opus_dsg_residual_intent.md  +  source_x_lifecycle_status.md
  ↓ (设计前最后一步)
open_questions_for_design_chat.md (回答 deferred-to-design 项)
```

---

## 2. 与已有 architecture/ 文档的引用关系

本工作区**引用**这些 doc 而**不复制**它们的内容。下游 chat 进入实施层时仍以下面文件为准。

### 2.1 DSG 决策与 ADR

| 文件 | 角色 |
|:--|:--|
| `../adr_l1_5_source_dispatch_extension_space_20260504.md` | **ADR-L1.5-001** — Q1 source 字段位置 + Q2 meta+factory 扩展空间 + Q3 chat 路径锁。**任何动 dsg/ 的 chat 必读** |
| `../adr_protocol_upgrade_and_interface_refinement_background_20260504.md` | ADR-PROTOCOL-INTERFACE-001 — 协议升级背景；DSG 工作区与之**互不覆盖**（那份是协议层接口提炼输入） |
| `../sprint4_phase4_completion_and_final_audit_20260430.md` | Phase 4 完成报告 + §3 协议契约最终态（NodeKind 6 项 / EdgeKind 8 项的真源） |
| `../sprint4_phase4_entry_20260430.md` | §8 13 条决策锁（**不可动**），含 L7 PhotoEvent 不自动建 ObjectNode 等 DSG 相关锁 |
| `../audit_identify_object_no_screenshot_20260420.md` | §5.1 B4 reference image 字段约定 + §9.1 用户原话锚点（"L2-B 完善过程中完成，效果未知"） |
| `../sprint0_preflight.md` | Sprint 0 Schema V1 — `provenance_stream_id` / `time_span` / `reference_image_path` / `last_sighting_path` 4 字段引入 |

### 2.2 DSG 派发与外部蒸馏

| 文件 | 角色 |
|:--|:--|
| `../dsg_skill_seeker_l1_5_a10_l2a_20260504.md` | ConceptGraph 蒸馏任务包（已派出独立 workspace 完成）|
| `../../../skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md` | A10 入口 + L2-A 蒸馏产物。**A10 入口部分由 SKILL 承载，本工作区不重复** |
| `../sprint4_phase4_downstream_chat_dispatch_plan_20260504.md` | §1.1 Chat 2（L1.5 Node 池设计）— 本工作区是 Chat 2 的入场前置 |

### 2.3 行为契约与边界

| 文件 | 角色 |
|:--|:--|
| `../../parrot_behavior_rules.md` | Observer / Attention 边界口径（Observer 不写 L2-B 节点 attention；Attention 不抓帧 / 不写 Graphiti） |
| `../module_map_p2.md` | §十 DSG 四层语义架构现状（L1 / L1.5 / L2-A / L2-B 占位 / 实现度）+ §11.2 MemoryValidity 过滤器位置 |
| `../ar_feature_vision.md` | §3.5 三合一意识 + §3.6 Ingest 过滤层位置 |

### 2.4 DSG 系列 cursor skills（4 个 2026-05-06 新增）

> 用户独立完成 RustworkX 调研 + 仓库蒸馏后落地，作为 Chat 2 设计的核心选项库。

| Skill | 角色 | 入口 |
|:--|:--|:--|
| `dsg-rustworkx-master` | **总入口路由** + RustworkX 实操 + 仿生 4 范式 + 跨 skill 论文索引 | [`.cursor/skills/dsg-rustworkx-master/SKILL.md`](../../../skills/dsg-rustworkx-master/SKILL.md) §0 决策路由表 |
| `dsg-l2b-node-organization-options` | Node/Edge 组织 5 选项（A 双类 / B 三类 / C 多源 / D 复合 / E SLM 多 Profile）+ 子图分层 P1-P4 + 跨源合并信号 | [`.cursor/skills/dsg-l2b-node-organization-options/SKILL.md`](../../../skills/dsg-l2b-node-organization-options/SKILL.md) §1 + §6.5 |
| `dsg-attention-schema-papers` | 13 篇论文索引（GAT / DySAT / AGCN / G-HAM / Schema / Hippocampal Indexing / Spreading Activation / CLS / Tulving / ASD/MDD 健康度）| [`.cursor/skills/dsg-attention-schema-papers/SKILL.md`](../../../skills/dsg-attention-schema-papers/SKILL.md) §0 路由表 |
| `dsg-l1-5-l2a-conceptgraph-distilled` | A10 入口门控 + L2-A 语义抽象（A10 Phase 5+ 接入参考）| [`.cursor/skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md`](../../../skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md) §1-§4 |

### 2.5 NewZone 蒸馏素材池（不进 .cursor/skills/，避免上下文污染）

> 6 份 Gemini 蒸馏产出 + 1 份案例研究综述 + 1 份原始派出 spec。**深读**素材，按需 @ 引用，不自动加载。

| 路径 | 蒸馏对象 |
|:--|:--|
| `NewZone/distill_output/dsg/concept-graphs/` | concept-graphs/concept-graphs 仓库（A10 入口 + L2-A）|
| `NewZone/distill_output/dsg/rustworkx-docs/` | rustworkx.org 官方文档子集 |
| `NewZone/distill_output/dsg/rustworkx-repo/` | Qiskit/rustworkx 全仓库（含 PyO3 / GIL） |
| `NewZone/distill_output/dsg/superlocalmemory/` | qualixar/superlocalmemory（9 层 + TWF 衰减）|
| `NewZone/distill_output/dsg_l2b_org_raw/HippoRAG/` | OSU-NLP-Group/HippoRAG（NeurIPS'24）|
| `NewZone/distill_output/dsg_l2b_org_raw/AriGraph/` | AIRI-Institute/AriGraph |
| `NewZone/RustworkX 图模拟研究案例.md` | 案例研究综述（§119-§122 仿生 4 范式）|
| `NewZone/skill_distill_bundle/` | 6 份 focus 配置（重新蒸馏用）|

### 2.6 Sprint 4 Phase 5+ Line B 完成报告

| 文件 | 角色 |
|:--|:--|
| `../lineb_implementation_completion_20260504.md` | LineB STT-LLM-TTS 双管线兼容性验证（Phase 4 §8 0 漂移 + 234/234 pytest）— 与 DSG 间接相关：transcript_extractor 改名（旧名 alias 保留）；GEMINI_ORAL source 现接收任何 LLM 助手的口头提及 |

---

## 3. 源码 surface（DSG 模块文件清单）

| 文件 | 当前职责 |
|:--|:--|
| `src/parrot/dsg/l1_5_protocol.py` | L1.5 SensorFrame / Detection / FrameSource / DetectionAuthority — 跨进程合同 |
| `src/parrot/dsg/l2b_types.py` | NodeKind 6 项 / EdgeKind 8 项 / Salience / ConfirmationStatus / SemanticNode（含 source + source_meta + factory）/ SemanticEdge / EpisodeMarker |
| `src/parrot/dsg/l2b_graph.py` | RustworkX 工作记忆图 — upsert / connect / episode / Graphiti preload + archive |
| `src/parrot/dsg/interfaces.py` | DSG ↔ Graphiti 桥（preload_object_semantics / update_last_seen / get_expected_objects / emit_trigger） |
| `src/parrot/dsg/types.py` | L1 事件类型 / 触发器类型 / ObjectInfo |
| `src/parrot/dsg/expectation_checker.py` | 期望 vs 实际对比（与 Opus 19 EXPECTED 节点关联） |
| `src/parrot/dsg/mode_controller.py` | DsgMode 切换 + 过滤器 enable/disable |
| `src/parrot/dsg/trigger_listener.py` | Redis 触发事件订阅 |
| `src/parrot/dsg/ingest/base.py` | IngestFilter 基类 + Observation / ObservationSource 7 项 / IngestOutcome |
| `src/parrot/dsg/ingest/runner.py` | IngestRunner — Observation → SemanticNode commit；含 _SOURCE_PRIORITY + 30s repeat-seen promotion + factory dispatch |
| `src/parrot/dsg/ingest/{user_tag,tool_result,text_source,cv_track,gemini_transcript_extractor}_filter.py` | 5 个具体过滤器 |
| `src/parrot/dsg/triggers/{calendar,message,scene_context,ssot_enrichment}_trigger.py` | 4 个背景触发器 + runner |
| `src/parrot/dsg/attention/{threshold,hint_writer}.py` | Phase 4 W6-7 attention threshold + hint writer（受 §3.7 边界约束） |

---

## 4. 入口模式（按你下一步要做什么读哪几份）

### 4.1 设计模式（要写新设计稿 — Chat 2 / L1.5 池升级 / lifecycle 差异化 / L2-B 简单升级）

```
本文件 (workspace_index.md)
  → dsg_current_state_distilled.md  (一份吃掉全景)
  → open_questions_for_design_chat.md  (确认要回答哪几条)
  → 按需 source_x_lifecycle_status.md  /  opus_dsg_residual_intent.md
  → 真源 doc：ADR-L1.5-001  +  Phase 4 §8 锁
  → 写设计稿到 architecture/<topic>_design_<date>.md
```

### 4.2 实施模式（设计 sign off 后写代码）

```
设计稿 (architecture/<topic>_design_<date>.md)
  → ADR-L1.5-001 §4.1 触发条件再核对（是否需要升级到子类）
  → 真源代码：src/parrot/dsg/{l2b_types.py, ingest/runner.py, ...}
  → 测试：tests/test_dsg/
  → 漂移说明：commit_guidelines.md
```

### 4.3 审计模式（独立审计 chat）

```
设计稿 + 实施 commit
  → 本工作区 dsg_current_state_distilled.md §9 锁定面（哪些不能动）
  → ADR-L1.5-001 §4.1 升级条件（实施是否触及）
  → audit_identify_object_no_screenshot §9.1（用户口径锚点）
  → 输出 audit_<topic>_<date>.md
```

---

## 5. 不允许误读

1. **本文不是真源**。它是路由 / 入口聚合。具体决策、设计、实施都在被指向的 ADR / source code / SKILL 里；本文出现"决策"字样属于错误，应回到对应文件查核。
2. **本工作区 vs INDEX.md**：INDEX.md 是项目唯一真相源（含 Bus / Brain / Scheduler / DSG / Memory / Unity 全模块）；本文只覆盖 DSG 模块层（L1.5 / L2-A / L2-B / 触发器 / Ingest / Graphiti 桥）的子集。
3. **本工作区 vs ar_workspace_index.md**：AR 工作区覆盖 Unity App / LiveKit / AR Foundation / 真机 spike；DSG 工作区覆盖 DSG 模块层。两边在 EcpEvent / PhotoNode / RefBinding 等接口处有交集，那部分以 Phase 4 §8 决策锁为准。
4. **本工作区 vs ConceptGraph SKILL**：A10 入口（视觉门控 / IoU / CLIP / ReID / L2-A 节点描述）由 [.cursor/skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md](../../../skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md) 承载；本工作区**不重复**，仅在 §8 给跨引用。
5. **新增 DSG 相关产物时**，先在本文 §1 / §2 对应小节登记一行；如该产物影响 INDEX §〇 必读级别，再去 INDEX §〇 加。多数情况只需要登记到本文。

---

## 6. 派发指引（给 Chat 2 / 后续 DSG 设计 chat）

本工作区 sign off 后（用户认可 `dsg_current_state_distilled.md` 的全景描述准确），即可启动：

| 派发 chat | 入场必读 | 输出位置 |
|:--|:--|:--|
| **Chat 2** L1.5 预加载 Node 池 + 状态生命周期设计（除 A10 入口）+ L2-B 简单升级 + L1.5 ↔ L2 适配 | 本工作区 5 份（master 优先）+ 4 个新 DSG skill（按 dsg-rustworkx-master §0 路由）+ ADR-L1.5-001 + Phase 4 §8 + 按需 NewZone 蒸馏素材池 | `architecture/dsg/dsg_l1_5_pool_and_lifecycle_design_<date>.md`（建议进 dsg/ 子目录） |
| **后续实施 chat** | Chat 2 设计稿 + 本工作区 §9 锁 | `src/parrot/dsg/` + `tests/test_dsg/` |
| **独立审计 chat** | Chat 2 设计稿 + 实施 commit + 本工作区 + ADR-L1.5-001 §4.1 | `architecture/audit_dsg_l1_5_<date>.md` |

派发详情见 [../sprint4_phase4_downstream_chat_dispatch_plan_20260504.md](../sprint4_phase4_downstream_chat_dispatch_plan_20260504.md) §1.1。

---

## 1.4 跨工作区交集 — Interface 工作区（2026-05-07 新增）

> Interface 工作区在 `architecture/Interface/`，是 AR + DSG 两个工作区的**接口/设计交集**入口。

**DSG 工作区主要消费**：

| 文件 | DSG 关注点 |
|:--|:--|
| `Interface/concept_dictionary §2` | DSG 概念全集（L1.5-L2-B / ObservationSource / Bucket / Episode / TriggerOutcome / Plan 等 ≈40 项）|
| `Interface/interface_design_supplement §1.1` | **Obsidian 3 子类 Ingest 路径**（NEED-P2.5-OBSIDIAN-3SUB：USER_TAG_OBSIDIAN + meta.profile ref/daily/roleplay）|
| `Interface/interface_design_supplement §1.4` | **2 Scene baseline**（DESKTOP_WEBCAM + AR_HANDHELD；SceneType enum 升级路径 + 不破 cs_parity）|
| `Interface/interface_design_supplement §1.5` | **三阶段延迟归档约束**（hot 内存 → cold 硬盘 → nanobot 闲时；配合 TODO(Chat4-archive-llm-defer)）|
| `Interface/interface_design_supplement §1.6` | **3 层防爆炸门控数值基线**（A10 deferred / L1.5 入池门 / L2-B 入图门）|
| `Interface/legacy_issues_split §2.2` | **4 类块菜单画布 P3-B/C 主线** — 推 DSG 协议升级 chat 实施 |
| `Interface/legacy_issues_split §1.10（新 P2.5）` | **2D 工作区 Google 日程桶联动** — `BucketKind.GOOGLE_CALENDAR` 激活逻辑 + IntentWorkspace 联动 |

**交集约束**（Phase 4 §8 为准）：
- EcpEvent / PhotoNode / RefBinding 三类接口 = AR × DSG 工作区共同遵守 `protocol_snapshot_p4.md §2-§8`
- 4 类块菜单画布 = AR 工作区（UI 层，NEED-P3-D/E）+ DSG 工作区（Persona/Scene 后端，NEED-P3-B/C）共同
- Obsidian 3 子类 = DSG 工作区主场（IngestFilter，NEED-P2.5-OBSIDIAN-3SUB）; AR 工作区（菜单选择 UI）配合
- **新 P2.5 需求（2026-05-07）**：2D 工作区 Google 日程批改 → `BucketKind.GOOGLE_CALENDAR` 联动 + IntentWorkspace — DSG 协议升级 chat + Sub-Chat B T-B7 主场

## 2.7 Google 日程桶联动设计说明（DSG 工作区关注）

> 背景：user 决定 P2.5 额外完成 2D 工作区 Google 日程批改功能。DSG 工作区需要确认以下接口。

**联动逻辑**（待 DSG 协议升级 chat 校准）：

```
前端批改日程（2D 工作区）
   ↓
nanobot tasks 同步状态
   ↓
写 Blackboard (scheduler/active_tasks + 状态)
   ↓
分支判断：
  ├─ 若 BucketKind.GOOGLE_CALENDAR 已激活（菜单里开关 / 菜单画布 Google 块已连接）
  │     → L2-B 有 Google Node（已加入 GOOGLE_CALENDAR 桶）
  │     → 可 stage 到 IntentWorkspace (StagedRefKind.CUSTOM / 或新定义 CALENDAR_REF)
  │     → 触发 IntentEventBoundaryHandler 处理（如计划提醒 → GOSLO 主动通报）
  └─ 若 BucketKind.GOOGLE_CALENDAR 未激活
        → nanobot 本地处理（Tasks 同步到 Google Calendar API）
        → 不进 L2-B / 不进 IntentWorkspace
        → 结果写 Blackboard 供查询
```

**需要确认的接口（Sub-Chat B T-B7 + DSG 协议升级 chat）**：
1. ~~`BucketKind.GOOGLE_CALENDAR` 是否已定义~~ — ✅ **已定义并落地**（`src/parrot/dsg/l1_5/buckets.py:33` = `GOOGLE_CALENDAR = "google_calendar"`；`dsg_protocol_pool_v1 §168` 桌面 4 桶之一；`protocol_snapshot_p4 §18` 只列 6 项是文档漏记）
2. `StagedRefKind` 是否需要新增 `CALENDAR_REF` / 用 `CUSTOM` 兜底
3. 菜单连接开关的 BB key（`global/google_calendar_bucket_enabled: bool`？或直接用 `BucketRegistry` 判断桶是否有节点）
4. `IntentWorkspace.stage()` 调用点（CalendarTrigger 既有路径 vs 2D 工作区批改新路径）

## 7. 变更日志

- 2026-05-04: 创建。聚合 DSG 模块层散落的 ADR / Opus 调研 / SKILL / source code。骨架 4 份新文件 + 路由接入 workspace.mdc / INDEX.md / active_context.md / 派发计划。建立目的是给 Chat 2（L1.5 池设计）当入场前置 SSOT。
- 2026-05-06: 用户回答 Q1.1-Q3.4 第一问后增补：(1) 新增 `dsg_decisions_master.md` 决策总表；(2) 4 个新 DSG skill（dsg-rustworkx-master / dsg-l2b-node-organization-options / dsg-attention-schema-papers / dsg-l1-5-l2a-conceptgraph-distilled）落入 §2.4；(3) NewZone 蒸馏素材池入 §2.5；(4) LineB 完成报告入 §2.6；(5) `dsg_current_state_distilled.md` 加 §11 防爆炸门控分层 + §12 工作记忆延迟归档；(6) `source_x_lifecycle_status.md` Obsidian 拆 3 子类 + Q2.x 已决条目；(7) `opus_dsg_residual_intent.md` 修正 attention 双开放路径（修正上轮"走 RustworkX 而非字段"的偏差）；(8) `open_questions_for_design_chat.md` 头部加 §0 已决汇总 + Q1.7 工作记忆归档时机。
- **2026-05-07（P2.5 App 设计 + Interface 工作区建立）**：新增 §1.4（Interface 工作区交集）+ §2.7（Google 日程桶联动设计说明）。补充**新 P2.5 需求**：2D 工作区 Google 日程批改 → BucketKind.GOOGLE_CALENDAR 联动 + IntentWorkspace — 待 DSG 协议升级 chat + Sub-Chat B T-B7 确认接口。
- **2026-05-06（Chat 2 实施完成）**：本工作区 §1 文件清单追加 8 份新产物：
  - 主设计稿：`dsg_l1_5_pool_and_lifecycle_design_20260506.md`
  - 协议 V1（5 份 DSG + 2 份 Brain）：`dsg_protocol_pool_v1` / `dsg_protocol_trigger_v2` / `dsg_protocol_intent_event_boundary_v1` / `dsg_protocol_archive_v1` / `dsg_protocol_scene_snapshot_v1` / `brain_protocol_intent_workspace_v1` / `brain_protocol_plan_v1`
  - 完成报告：`dsg_l1_5_implementation_completion_20260506.md`（status: ratified-code / pending-online-smoke）
  - 实施落地：14 新模块（`dsg/l1_5/` + `dsg/l2b/` + `dsg/archive/` + `brain/intent_workspace*` + `brain/plan/` + 5 新触发器 + 1 新 ingest filter）+ 5 改动既有模块 + 118 新测试 → **352/352 pytest 全绿**；Phase 4 § 8 + cs_parity 4/4 + ADR-L1.5-001 11/11 三守护通过；ADR-L1.5-001 §4.1 三触发器全部未触发，maintain `ratified`。
