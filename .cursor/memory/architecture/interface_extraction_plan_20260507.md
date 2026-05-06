---
status: draft / pending-user-signoff
category: planning
status_note: "Chat 4 实施前置 — 需求 / 能力 / 接口 / 协议 提炼方案规划稿。本稿不实施代码；产出后 user sign off → fork 进 ADR-PROTOCOL-INTERFACE-001 §7.1 描述的实施阶段。"
last_reviewed: 2026-05-07
parent_doc: "../INDEX.md"
parent_launch_prompt: "chat4_interface_refinement_launch_prompt_20260507.md"
adr_input: "adr_protocol_upgrade_and_interface_refinement_background_20260504.md"
authoritative_for: "Chat 4 实施前的'范围 + 任务划分 + 分类法 + 接口文档结构 + 需求覆盖度 + 起点 + 顺序 + 验收 + 风险 + user 提问'方案规划稿"
related:
  - "cross_chat_pending_registry_20260507.md (Chat 4 实施清单的真源)"
  - "sprint4_phase4_completion_and_final_audit_20260430.md (协议契约最终态)"
  - "sprint4_phase4_entry_20260430.md §8 (13 决策锁 — 不能动)"
  - "lineb_implementation_completion_20260504.md (双管线兼容性范本)"
  - "dsg/dsg_l1_5_implementation_completion_20260506.md (DSG Chat 2 收口)"
  - "goslo_modularization_completion_20260506.md + goslo_modularization_residual_debt_20260506.md (GOSLO 模块化收口)"
  - "module_map_p2.md §10.4 (DSG L1.5 升级后依赖架构图)"
  - "ar_app_flow_ui_design.md (App Flow / UI 基线)"
ai_priority: high
ai_audience: "Chat 4 实施 chat / 独立审计 chat / user 决策 sign off"
---

# Chat 4 — 需求 / 能力 / 接口 / 协议 提炼 方案规划稿

> **本文用途**：Chat 4 实施前的方案规划稿。本稿**只规划不实施**——产出后 user 在 §10 提问清单做关键裁决，sign off 后才 fork 进 ADR-PROTOCOL-INTERFACE-001 §7.1 描述的实施阶段。
>
> **基调**：本稿是规划者视角的"先把脚下踩实再迈步"——读完三大 chat 完成报告 + cross-chat-registry + ADR + Phase 4 §8 + ADR-L1.5-001 + module_map_p2 §10.4 + ar_app_flow_ui_design 后，给出**多方案对比 + 推荐路径 + 必要 user 裁决**。**不预设答案**；不复制粘贴已有 doc 内容凑字数。
>
> **作者**：Chat 4 接口提炼方案规划 chat（2026-05-07）。

---

## §0 TL;DR + 推荐方案

### §0.1 一段话推荐

**推荐**：Chat 4 = **(A) 实施 TODO 物理推完 + (B) 接口面 inventory + 分类 + 单份 SSOT 文档 + (C) freeze test 模式扩展** 三轨**并行**。**起点 = `module_map_p2 §10.4` ASCII 依赖图（已就位，不重画）**。**主分类维度 = 拓扑边界 (wire / cross-process / in-process)**，**副维度 = audience (ai/human/both)**。文档形态 = **单份多文件 SSOT + 机器层 (Pydantic schema export)**。

### §0.2 推荐方案矩阵（一眼决策版）

| 决策项 | 推荐 | 备选（若 user 否决推荐） | user 决策 |
|:--|:--|:--|:--|
| **范围层数** | 4 层全收（协议 / 接口 / 能力 / 需求）；需求层只覆盖与接口相关的 | 仅协议+接口（最小集）；4 层全展开（最大集） | ⏳ §10 Q5 待答 |
| **任务划分** | 3 轨并行：实施 TODO / inventory+doc / freeze test | 串行：先实施再 doc；或仅 doc 不动实施 | ⏳ §10 Q7 待答 |
| **分类主维度** | 拓扑边界（wire / cross-process / in-process） | 抽象层级；audience；角色 | ⏳ §10 Q2 待答 |
| **分类副维度** | audience（ai/human/both） | 稳定性；lifecycle phase | ⏳ §10 Q2 待答 |
| **文档形态** | 单份 SSOT 多文件 + 机器层（Pydantic→JSON Schema export） | 双份（人 vs AI 各一份）；散落不统一 | ⏳ §10 Q3 待答 |
| **起点** | `module_map_p2 §10.4` ASCII 图（不重画，复用） | 重画统一 module map；从 app flow 反推 | ⏳ §10 Q6 待答 |
| **顺序** | 7 项实施 TODO 优先（爆炸半径大），doc/test 与之并行 | 先 doc 后实施；先 test 后 doc | ⏳ §10 Q7 待答 |
| **B 轨提炼策略**（详 §7.5） | driver 主线（req → cap → 接口 by 拓扑边界 → grep 验证）+ bottom-up grep 验证（Z）；分层并行 6 sub-chat；按拓扑层分子目录隔离 | 全套双线并行；从代码反推接口；单 chat 一锅端 / 完全独立；同目录平铺 | ✅ Q9 = Z / Q10 = req-first 5 阶段（**amended**）/ Q11 = layered_parallel / Q12 = subdir_per_layer（**user 2026-05-07 sign off + amended**）|
| **方法论原则**（amendment）| driver = 拓扑边界（分类）+ App 流程 + 需求 + 能力（内容）；接口 = derived；既有代码 = 参考 / 升级起点 / 验证锚点（**不反推**）| 由 §10.4 反推；由 grep 候选驱动；由代码符号当接口起点 | ✅ user 2026-05-07 amendment（**新增条**）|
| **产出目录**（amendment）| `.cursor/memory/interfaces/`（与 architecture/ 同级；新开顶级）| `architecture/interfaces/`（之前提案，已否） | ✅ user 2026-05-07 amendment |
| **MVP 起步**（amendment 后）| T0-T2 仅 4-B-req 跑 2 天定型 needs+app_flow inventory + 方法论合规检查；user 倒查 → 后续 sub-chat 按步展开 | 7 chat 全启动；只启 4-A + 4-B-wire | ✅ Q13 = req-first-2d（**amended**，2026-05-07） |
| **验收基线** | 415/415 → ≥ 423/423（实施 TODO 各加 1+ 测试 + freeze test ≥ 5 项扩展）| 仅守 415/415 不退 | ⏳ §10 Q4 待答（影响 freeze test 数量） |

### §0.3 严重度

| 维度 | 严重度 |
|:--|:--|
| 是否阻塞 Chat 4 实施起跑 | 否 — 只要 §10 提问 sign off，实施 chat 即可启动 |
| 是否触动 Phase 4 §8 13 锁 | 否（推荐方案严格守 0 漂移） |
| 是否触动 ADR-L1.5-001 §4.1 三触发器 | 否（推荐方案不引入 SemanticNode 子类） |
| 是否影响真机 spike 时间 | 否 — Chat 4 实施时长估计 1-2 周，与真机 spike 解耦 |

---

## §1 范围（§3.1 答案）

### §1.1 Chat 4 实施范围 — 推荐 4 层全收

| 层 | 包含什么 | 真源 anchor | Chat 4 处置 |
|:--|:--|:--|:--|
| **协议层（Protocol）** | EcpEvent wire envelope / EcpState / EcpAck / topic / 8KB / RefBinding / NodeKind / EdgeKind / cs_parity 4/4 / `parrot.shared.{ecp_event, bb_schema, ref_binding, ecp}` + DSG 协议 7 份（pool / trigger v2 / intent_event_boundary / archive / scene_snapshot / intent_workspace / plan）+ ModelManifest | Phase 4 §8 13 锁 + DSG Chat 2 7 份协议 + GOSLO Manifest | **0 修改 +** 全量 inventory + 索引 + freeze test 扩展守护 |
| **接口层（Interface）** | Brain↔Unity 跨进程 RPC / DataChannel topic / HTTP `/upload/photo` / Brain 内部 attach helper / Observer hook / DSG TriggerOutcome 5 路上行 / IngestRunner.commit_observation 单一写门 / Plan-and-Execute 8 状态 / IntentWorkspace 9 StagedRefKind / `IParrotController` Unity 端契约 | bus_v4 三层协议 + module_map_p2 §10.4 + ADR §5.2 inventory | **inventory + 分类 + 单份 doc** + 必要的轻量重命名（走 alias 保留兼容，参考 LineB transcript_extractor 范本） |
| **能力层（Capability）** | 10 brain tools（fly_to / animate / dispatch_task / remember / query_memory / query_scene / set_mode / set_video_tier / identify_object / manage_episode / capability_gating 候选）/ ParrotAnimation 8 / ParrotBodyState 5 / BehaviorMode flags 5 / CognitiveState 4 / 9 触发器 / 6 BucketKind / 9 StagedRefKind / 4 RefKind / 4 RefTargetKind | brain/tools/__init__.py + parrot_actions.py + dsg/triggers/ + l1_5/buckets.py + IntentWorkspace + RefBinding | **inventory（每个 capability 标 wire / 内部 / 外部消费方）** + 与"4 类块"（NEED-P3-B 模型/设定/模式/场景）的命名空间映射 |
| **需求层（Requirement）** | requirements.md v2 67 功能项中**与接口相关**的子集（覆盖率检查表）；不展开非接口需求 | requirements.md + ar_app_flow_ui_design.md + milestone_p2.md | **覆盖率检查表**（接口 → 需求的反向映射）+ 缺口清单 → 推 NEED-P2.5-* / NEED-P3-* 标签 |

### §1.2 与三大 chat 完成的部分 0 重叠 — 验证

| 三大 chat 完成的内容 | Chat 4 是否再做 | 理由 |
|:--|:--|:--|
| Phase 4 §8 13 锁 wire schema | ❌ 不再设计 | 已锁，仅 inventory + freeze test 守 |
| LineB STT-LLM-TTS 双管线 + transcript_extractor 改名 | ❌ 不再做 | 兼容性范本，参照其 alias 模式即可 |
| DSG L1.5 + L2-B + Plan + IntentWorkspace + Archive 协议骨架 | ❌ 不再设计 | 7 份协议已 ratified，仅消费 |
| DSG Chat 2 留下的 9 处 `TODO(Chat4-*)` / `TODO(P3-*)` | ✅ Chat 4 主场（处理 5 个 Chat4-* / 不处理 4 个 P3-*） | cross-chat-registry §5 明确推给 Chat 4 |
| GOSLO ModelManifest + IParrotController + AI CLI | ❌ 不再设计 | 协议已 v1，仅 inventory + 与 NEED-P3-B 4 类块映射 |
| GOSLO 残余 7 类 parrot-isms + 4 类块前瞻需求 | ⚠️ 部分纳入 | NEED-P2.5-A persona 外置 + NEED-P3-B 4 类块**不在 Chat 4 主场**（推 DSG 协议升级 chat），但 Chat 4 inventory 时要为它们**预留位置** |

**Chat 4 主场清单**（cross-chat-registry §5 + 本规划稿确认）：

| # | 标签 | 实施 chat 还是 doc chat | 触点 |
|:--|:--|:--|:--|
| 1 | NEED-P2.5-PLAN-INTEGRATION（4 个 TODO(Chat4-plan-*)）| 实施 | scheduler/{nodes,service,blackboard}.py + plan_registry.py + dispatch_task.py + constants.py |
| 2 | NEED-P2.5-NANOBOT-HEARTBEAT | 实施 | bus/nanobot_consumer.py 加心跳写者 |
| 3 | NEED-P2.5-ARCHIVE-LLM | 实施 | dsg/archive/conversation.py:archive_to_graphiti 真 LLM 蒸馏 |
| 4 | TODO(Chat4-disk-recover) | 实施 | intent_workspace_backend.py DiskBackend.recover() |
| 5 | NEED-P3-CAPABILITY-GATING | 可选实施（user 决） | 新 ModelManifestRegistry + brain/agent.py tool 注册过滤 |
| 6 | 接口面 inventory + 分类 + 单份 SSOT 文档 | doc | 新 `architecture/interfaces/INDEX.md` + 多文件分包 |
| 7 | freeze test 扩展（推 cs_parity 模式）| test | tests/test_*/test_freeze_*.py 新增多套 |

---

## §2 任务划分策略（§3.2 答案）

### §2.1 三种策略对比

| 策略 | 描述 | 协议合同稳定性风险 | 实施时长 | 测试覆盖 | 集成成本 | 推荐度 |
|:--|:--|:--|:--|:--|:--|:--|
| **A. 全面同步**（一锅端） | 7 项 TODO + doc + freeze test 一个 chat 内全做完 | 中（任务 5+ 多 wire 触点同时改，cs_parity 守护可能不及时反馈） | 2-3 周 | 高（一站式回归） | 高（合并冲突 / 大 PR） | ⭐⭐ |
| **B. 串行**（先实施 → 后 doc → 后 test） | 7 项 TODO 跑完，再写 doc，再扩 freeze test | 低（一次只改一类） | 3-4 周 | 中（test 滞后到第 3 阶段） | 低（单一 PR） | ⭐⭐ |
| **C. 三轨并行** ⭐ | A 轨实施 / B 轨 doc / C 轨 test 三个 sub-chat 并行 | 低（C 轨 freeze test 持续守护，A 轨改动立刻被锁住） | 1.5-2 周 | 高（test 覆盖与实施同步） | 中（三轨同步对账成本） | ⭐⭐⭐ |

### §2.2 推荐方案 C 的三轨内部进一步排序

**A 轨（实施）内部按爆炸半径排序**：

| 顺序 | 任务 | 爆炸半径 | 必须先做的理由 |
|:--|:--|:--|:--|
| 1 | NEED-P2.5-PLAN-INTEGRATION（4 个 plan-* TODO）| 全 Plan-and-Execute 链路 | 锁住 Plan ↔ Scheduler ↔ Nanobot 接口面，下游 doc 才能稳定 inventory |
| 2 | NEED-P2.5-ARCHIVE-LLM | 对话归档 + Graphiti | LLM 蒸馏接口面定型，影响 Chat 4 文档"知识层"section |
| 3 | NEED-P2.5-NANOBOT-HEARTBEAT | IdleArchiveTrigger 触发条件 | 与上 #2 强耦合（蒸馏前要确认 nanobot 闲） |
| 4 | TODO(Chat4-disk-recover) | IntentWorkspace 恢复 | 独立任务，可塞在任意位置 |
| 5 | NEED-P3-CAPABILITY-GATING（**可选**，user 决） | tool 注册过滤 | 与 GOSLO Manifest registry 同步落地后才有意义 |

**B 轨（doc）按主分类维度（§3）展开**：先写 inventory，再写分类，再写正式 SSOT 文档（单份多文件 + 索引）。

**C 轨（test）扩展 freeze test**：参考 `test_cs_parity` 模式，覆盖更多 axis（NodeKind / EdgeKind / RefKind / BB key namespace / topic 常量 / EcpEventSource enum）。

### §2.3 三轨协调机制

| 协调点 | 机制 |
|:--|:--|
| 跨轨改动同步 | 每轨结束阶段产 mini-completion-report，B 轨 inventory 持续吸收 A 轨改动 |
| 协议合同守护 | C 轨 freeze test 在 A 轨 PR 上**强制 CI 跑**；C 轨自身改动需 B 轨 doc 同步 |
| user 节奏 | 每轨完成 50% 时给 user mini-checkpoint（不必等三轨都完才汇报） |

---

## §3 分类法（§3.3 答案）

### §3.1 主维度候选 — 4 选 1

| 维度 | 例子 | 优 | 缺 | 评估 |
|:--|:--|:--|:--|:--|
| **1. 拓扑边界** ⭐ | wire (cross-language) / cross-process (HTTP/Redis) / in-process (attach helper / DI) | 与 bus_v4 三层协议 + Phase 4 §8 §8.2 通道默认值表**天然对齐**；爆炸半径清晰；CI 守护粒度可独立调 | "同一概念可能横跨边界"问题（如 EcpEvent 既是 wire 又被 Brain 内部消费） | **推荐主维度** |
| **2. 抽象层级** | bytes / topic / schema / behavior contract | 自下而上学习路径清晰 | 与 Phase 4 §8 锁的"接口合同"层级语义重叠；高低层同步成本 | 推荐**作为副维度补强**（不主） |
| **3. 角色** | Unity / Brain / Nanobot / DSG / Scheduler 看 | 读者视角清晰 | 同一接口对多角色都暴露，重复内容多 | 不主，但接口文档**索引**应支持按角色 cross-link |
| **4. audience（人 / AI）** | ai_only / human_only / both | 文档形式选型驱动 | 同接口在 AI 与人之间的描述粒度差异大 | **推荐作为副维度**（每个接口块标 audience） |

### §3.2 推荐主+副维度

```
主维度：拓扑边界
├─ wire（跨语言 / cross-language）
│  • EcpEvent / EcpState / EcpAck / topic / cs_parity 4 项
│  • LiveKit DataChannel 5 topic（state / event / health / intent_disconnect / tick）
│  • LiveKit RPC（flyTo / animate / setVideoTier / captureSnapshot / capturePhoto / dispatch_task / token_mint）
│  • EcpEventDto.cs ↔ EcpEvent.py 字段镜像
│  • RefBinding / NodeKind / EdgeKind / EcpCommandMetaDto C# typed slot
├─ cross-process（同进程外 / Castle 进程边界外）
│  • HTTP `/upload/photo` (FastAPI 7889)
│  • Redis Stream `parrot.events.log` / Pub/Sub `parrot.brain.*` / HASH `parrot:nanobot_heartbeat`
│  • Graphiti `add_episode` / `search` (Bolt :7687)
│  • Castle ↔ Mecha (Phase 5+ A10) 占位接口
└─ in-process（Castle Brain Python 进程内）
   • attach_* helpers（attach_ecp_event_ingest / attach_ecp_state_ingest / attach_telemetry_receiver / attach_attention_config_handler / attach_transcript_listener_to_session）
   • Observer event_bus（snapshot / sighting / bbox / focus / photo）
   • DSG TriggerOutcome 5 路上行 + TriggerRunner._process_result 路由
   • IngestRunner.commit_observation（L2-B 单一写门）
   • IntentWorkspaceBackend Strategy（InMemory / Disk）
   • PoolAdmissionPolicy / FoldStrategy / AttentionDecayStrategy / AttentionMechanism Strategy 注册表
   • _state_context.py + 3 tool wrappers（selection-C 主路径）
   • _budget.py（identify_object 1.9s）
   • parrot.brain.refs / hint_writer

副维度：audience（每个接口块带 frontmatter）
├─ ai_only（dense matrix / table-heavy / cross-link 密）
├─ human_only（narrative / 例子驱动 / 易读但慢）
└─ both（双份层叠：narrative 段 + 紧贴 dense matrix；ai_priority 字段标）
```

### §3.3 ADR §5.3 8 候选维度的取舍

| ADR §5.3 维度 | 取舍 | 理由 |
|:--|:--|:--|
| 1. wire vs internal | ✅ 取（融入主维度"拓扑边界"） | 推荐方案核心 |
| 2. 角色 / 调用方 | ⚠️ 副副维度（仅作索引 cross-link） | 重复内容风险 |
| 3. 稳定性 | ⚠️ frontmatter 字段（每接口块带 stability: locked / evolving / experimental） | 不主分类 |
| 4. audience | ✅ 取（副维度） | 推荐方案核心 |
| 5. lifecycle phase | ❌ 不取 | 跨 phase 接口归类难 |
| 6. domain（state/event/config/behavior/data/RPC）| ⚠️ frontmatter 字段 | 维度交叉风险 |
| 7. 抽象层级 | ⚠️ 副副维度（在每个拓扑边界内部，按抽象层级排）| 不主 |
| 8. deploy 边界 | ⚠️ 副副维度（注脚说明 Castle / Mecha / Editor / 真机）| Phase 5+ 才显著 |

---

## §4 接口文档结构（§3.4 答案）

### §4.1 单份 vs 双份 — 推荐单份 SSOT 多文件 + 机器层

| 形态 | 优 | 缺 | 推荐 |
|:--|:--|:--|:--|
| **单份 SSOT（多文件，audience: both）** ⭐ | 0 重复维护；frontmatter `ai_priority` / `ai_audience` 字段引导阅读路径；与 ADR / completion report 现有风格一致 | 单接口在 AI/人之间粒度需手工调（参考 parrot_behavior_rules 模式） | **推荐** |
| 双份分立（人版 + AI 版） | 各自最优形式 | 维护成本翻倍；漂移风险高（人版改了 AI 版没改）；与 cs_parity 单一真源原则违反 | ❌ 否 |
| 散落（每个 doc 自己定）| 当前现状 | 无 single entry，下游难追 | 否（Chat 4 必须收口）|

### §4.2 单份 SSOT 推荐文件结构

```
.cursor/memory/architecture/interfaces/
├── INDEX.md                        # 单一真相源入口；按主+副维度索引；ai_priority/ai_audience frontmatter
│
├── wire/                           # 主维度：wire（跨语言）
│   ├── ecp_event_v1.md             # EcpEvent envelope + 13 EcpEventType + 8KB + dedup + cs_parity
│   ├── ecp_state_v1.md             # parrot.ecp.state topic + 1Hz + event-driven
│   ├── ecp_ack_v1.md               # RPC return value + active_locks + active_command_id
│   ├── ecp_command_meta_v1.md      # EcpCommand.meta typed slot（GOSLO model_id 入口）+ Unity DTO mirror
│   ├── livekit_rpc_v1.md           # 7 个 RPC method + 同步语义 + 跨语言守护
│   ├── ref_binding_v1.md           # RefBinding wire schema + 4 RefKind + 4 RefTargetKind
│   ├── node_edge_kind_v1.md        # NodeKind 6 / EdgeKind 8（DSG-INTENT-EVENT-V1 已 freeze）
│   ├── photo_double_channel_v1.md  # preview EcpEvent + asset HTTP `/upload/photo` 双通道
│   └── topic_matrix.md             # 5 LiveKit DataChannel topic + reliability + 频率一览
│
├── cross_process/                  # 主维度：cross-process（HTTP / Redis / Graphiti）
│   ├── http_upload_photo.md        # FastAPI 7889 `/upload/photo` + bearer 鉴权（P3+ 才加）
│   ├── redis_pub_sub.md            # parrot.events.firehose + parrot.brain.* + parrot.dsg.* + parrot.scheduler.*
│   ├── redis_stream.md             # parrot.events.log（L0 EventEnvelope，与 Phase 4 EcpEvent 区分）
│   ├── redis_hash.md               # parrot:nanobot_heartbeat / parrot:resource_locks / parrot:bb（实测 keys）
│   ├── graphiti_v1.md              # add_episode / search / group_id 分区 + Phase 3 蒸馏接入点
│   └── castle_to_mecha_placeholder.md  # Phase 5+ A10 GPU Worker 启停信号（占位）
│
├── in_process/                     # 主维度：in-process（Brain Python 进程内）
│   ├── attach_helpers.md           # 5 个 attach_* helper（boot 序 + 拆解机制）
│   ├── observer_event_bus.md       # 5 observer（snapshot / sighting / bbox / focus / photo）
│   ├── dsg_trigger_outcome_v2.md   # TriggerOutcome 5 路上行 + TriggerRunner._process_result
│   ├── ingest_runner.md            # commit_observation 单一写门 + factory dispatch
│   ├── intent_workspace_backend.md # InMemoryBackend / DiskBackend / 9 StagedRefKind
│   ├── pool_admission_policy.md    # PoolAdmissionPolicy + 6 BucketKind
│   ├── attention_strategy.md       # AttentionDecayStrategy / AttentionMechanism / FoldStrategy
│   ├── selection_c_state_context.md # _state_context + 3 tool wrappers
│   ├── identify_object_budget.md   # _budget + 1.9s 三段（Phase 4 §8 L11 锁）
│   └── refs_hint_writer.md         # parrot.brain.refs + hint_writer
│
├── capability/                     # 副维度：能力层（在拓扑边界内为副副维度，但单独成包让下游好找）
│   ├── brain_tools_inventory.md    # 10 brain tools + 各自 wire / 内部 / 外部消费方
│   ├── parrot_actions_v1.md        # ParrotAnimation 8 / ParrotBodyState 5 / BehaviorMode 5 / CognitiveState 4
│   ├── triggers_inventory.md       # 9 triggers（4 legacy + 5 new）+ 5 路上行通道
│   ├── ref_kinds_inventory.md      # 4 RefKind + 4 RefTargetKind + lifecycle
│   ├── bucket_kinds_inventory.md   # 6 BucketKind + AdmissionPolicy + lifecycle
│   ├── staged_ref_kinds.md         # IntentWorkspace 9 StagedRefKind
│   └── model_manifest_v1.md        # GOSLO ModelManifest + Capability + RESERVED_PARROT_CAPABILITY_IDS
│
├── requirement_coverage.md         # 需求层覆盖率检查表（§5）
│
├── deprecation.md                  # 接口废弃 / 替换流程（per ADR §5.5）
├── extension_points.md             # 第三方扩展（SDK / Plugin）占位（per ADR §5.5）
├── schema_evolution.md             # schema_version 演进策略 + freeze test 扩展指南
└── change_impact_table.md          # 变更影响表（接口 → 影响范围 → 测试 → 文档）
```

**总文件数估计**：~30 文件，平均 100-300 行/文件，总量 ~5000 行。

### §4.3 frontmatter 模板

每个接口文件 frontmatter（参考 ADR-PROTOCOL-INTERFACE-001 + parrot_behavior_rules 风格）：

```yaml
---
status: locked | evolving | experimental
category: interface
interface_id: wire-ecp-event-v1                  # 唯一稳定 ID
topology: wire | cross_process | in_process
ai_priority: high | medium | low
ai_audience: ai_only | human_only | both
schema_version: 1
freeze_test: tests/test_ecp_event/test_cs_parity.py  # 守护 freeze test 路径（可多）
producer: src/parrot/shared/ecp_event.py         # 单一真源（code 真源）
consumer: ["unity", "brain.event_ingest", "..."] # 消费方清单
last_locked: 2026-04-30
last_reviewed: 2026-05-07
related: ["wire-ecp-state-v1", "wire-livekit-rpc-v1"]
---
```

### §4.4 多文件 + 索引组织约定

- **INDEX.md** 顶层索引：按主维度（wire / cross_process / in_process）3 表 + 各表内按副维度（audience）+ 副副维度（角色）cross-link
- **每个接口文件自包含**：不靠隔壁文件解释；必要 cross-link 用 `[interface-id](path)` 风格
- **机器可读层（可选）**：CI 自动从 Pydantic schema export JSON Schema → `interfaces/_machine/<interface_id>.schema.json`；与 markdown 同步守护（参考 §8.5 #1）
- **deprecation 与 extension 单独成包**（不分散到各接口文件）

---

## §5 需求覆盖度检查表（§3.5 答案）

### §5.1 67 功能项 → 接口面 反向映射策略

不全展开 67 项；只给覆盖率检查表**模板**。具体填写在 Chat 4 实施 chat 跑。

| 功能项编号 | 一句话需求 | 涉及接口块（interface_id） | 当前覆盖度 | 缺口处置 |
|:--:|:--|:--|:--|:--|
| F01 | 启动连接 LiveKit + token mint | wire-livekit-rpc-v1 / wire-token-mint | ✅ locked | — |
| F02 | identify_object 三段重写 | in-proc-identify-budget / wire-ecp-event-v1 (sighting.*) | ✅ locked (Phase 4 §8 L11) | — |
| ... | ... | ... | ... | ... |
| F44 | Plan-and-Execute 真派发到 Nanobot | wire-livekit-rpc-v1 (dispatch_task) / cross-redis-stream / in-proc-plan-registry | ⚠️ skeleton（NEED-P2.5-PLAN-INTEGRATION）| Chat 4 A 轨 #1 |
| F45 | 闲时归档 → Graphiti 真蒸馏 | cross-graphiti-v1 / in-proc-archive | ⚠️ skeleton（NEED-P2.5-ARCHIVE-LLM）| Chat 4 A 轨 #2 |
| F60 | 4 类块预设系统 | capability-model-manifest / capability-persona / capability-mode / capability-scene | ❌ 缺（NEED-P3-B/C）| 推 DSG 协议升级 chat |
| ... | ... | ... | ... | ... |

### §5.2 12 个 NEED-P2.5/P3 项与 Chat 4 的对应

详见 cross_chat_pending_registry §5（已 grep 实测 ✅）：

| 标签 | Chat 4 处置 |
|:--|:--|
| NEED-P2.5-A persona 外置 | ❌ 不在 Chat 4（推 DSG 协议升级 chat）|
| NEED-P2.5-PLAN-INTEGRATION | ✅ Chat 4 A 轨 #1 |
| NEED-P2.5-NANOBOT-HEARTBEAT | ✅ Chat 4 A 轨 #3 |
| NEED-P2.5-ARCHIVE-LLM | ✅ Chat 4 A 轨 #2 |
| NEED-P2.5-B Unity menu DSG bucket/scene | ❌ 不在 Chat 4（推 AR 工作区独立 chat）|
| NEED-P3-A body_state 解锁 | ❌ 不在 Chat 4（推 P3 wire ADR chat）|
| NEED-P3-B 4 类块注册表 | ❌ 不在 Chat 4（推 DSG 协议升级 chat）|
| NEED-P3-C 预设 schema | ❌ 不在 Chat 4（同上）|
| NEED-P3-D node-canvas UI | ❌ 不在 Chat 4（推 AR 工作区独立 chat）|
| NEED-P3-E 默认菜单 fallback | ❌ 不在 Chat 4（同上）|
| NEED-P3-CAPABILITY-GATING | ⚠️ **可选 Chat 4 A 轨 #5**（user 在 §10 决）|
| TODO(P3-Wire-PlanUI) | ❌ 不在 Chat 4（推 P3 wire ADR chat）|

### §5.3 App flow 链路覆盖检查

| AR App Flow 步骤（per ar_app_flow_ui_design §4） | 接口面是否齐 |
|:--|:--|
| 1. 启动页 / 主菜单 | ⚠️ 需求齐（NEED-P3-B/C/D/E 占位），接口未提炼 — Chat 4 inventory |
| 2. 选择或确认初始配置 | 同上 |
| 3. 权限与连接检查 | ✅ 已有（livekit-unity-lifecycle SKILL）|
| 4-5. 加载 / 转场 | UI 层，无后端接口 |
| 6. 进入 AR 主场景 | ✅ 已有（ParrotApp/Lifecycle）|
| 7. HUD / 工具柜按需展开 | ✅ 已有（capturePhoto / BBox / Focus tool）|
| 8. 工具或 2D 工作区按需进入 | ⚠️ 接口面散落 — Chat 4 inventory 整合 |

---

## §6 起点选择（§3.6 答案）

### §6.1 三起点对比

| 起点 | 描述 | 优 | 缺 | 推荐度 |
|:--|:--|:--|:--|:--|
| **A. App Flow** | 从 ar_app_flow_ui_design §4 启动 → AR 主场景 → 工具柜 → 退出链路反推接口面 | 用户体验视角；与最终 demo 对齐 | 仅覆盖 App 维度，错过 Brain↔Nanobot / DSG 内部 / cross-process 接口；很多 in-process 接口与 App flow 无直接对应 | ⭐⭐ |
| **B. 模块架构** ⭐ | 从 module_map_p2 §10.4 ASCII 依赖图（已有 DSG L1.5 升级后形态）反向追接口面 | 全景覆盖；架构层次清晰；与 bus_v4 三层协议天然对齐；ASCII 图已就位无需重画 | 抽象级别可能过高，需要二次下钻到协议合同细节 | ⭐⭐⭐ |
| **C. 重新划分模块** | 重做一份"最新 module map"，重新划分边界后再提炼接口 | 可能发现现有划分的隐藏问题 | **额外 chat 工作量**（重画 + 再 sign off）；**违反 §1.2 不重叠原则**；DSG Chat 2 §9.3 已确认"模块划分已清晰，不需再开新报告" | ⭐ |

### §6.2 推荐 = B + 不重画 module map

**关键裁定**：**不需要**重新画"最新 module map"。

**理由**：
1. `module_map_p2 §10.4` 已是 DSG Chat 2 收口后的最新形态（2026-05-06 更新）
2. ASCII 图已含完整 9 触发器 + 5 路上行通道 + 6 个下游模块（L1.5 Pool / L2-B / Archive / IntentWorkspace / PlanRegistry / 老路径 Scheduler+Nanobot+ContextInjector）
3. GOSLO 模块化的接口（IParrotController / ModelManifest）是 Unity 端 + Brain tool 元数据透传，**不影响 Brain 内部模块边界**
4. DSG Chat 2 §9.3 user 确认审计：模块划分已清晰

### §6.3 复用 §10.4 的方式

```
B 轨 doc 工作流（基于 §10.4 反向追接口）：

1. 取 §10.4 ASCII 图每一个方框 = 一个模块
2. 取每条箭头 = 一个跨模块接口
3. 标注每个箭头的拓扑边界（wire / cross-process / in-process）
4. 反向 grep 实际 code 对应（attach_*.py / observer/*.py / triggers/*.py / l1_5/*.py / l2b/*.py 等）
5. 对每个接口写一份 interface markdown 文件（按 §4.2 文件结构）
6. INDEX.md 同步索引

ASCII 图未覆盖的（需补）：
- Unity ↔ Brain wire（Phase 4 §8 §8.2 通道默认值表）
- HTTP `/upload/photo`
- Token mint / LiveKit RPC
- Castle ↔ Mecha 占位
- ECP-state ingest pipeline
```

---

## §7 顺序 + 依赖图（§3.7 答案）

### §7.1 三轨并行 — 推荐顺序图

```
Week 1                              Week 2
─────────────────────────────────── ───────────────────────────────────
A 轨（实施）：
  ┌────────────────────────────┐
  │ #1 PLAN-INTEGRATION        │ ──────┐
  │ (4 个 plan-* TODO + dispatch)       │
  └────────────────────────────┘        │
                                        ▼
                            ┌────────────────────────────┐
                            │ #2 ARCHIVE-LLM             │ ──────┐
                            │ (LLM 蒸馏 → Graphiti)       │       │
                            └────────────────────────────┘       │
                                                                 ▼
                                              ┌────────────────────────────┐
                                              │ #3 NANOBOT-HEARTBEAT       │
                                              │ (HSET 写者 + idle 联调)     │
                                              └────────────────────────────┘
                                              ┌────────────────────────────┐
                                              │ #4 disk-recover (并行)     │
                                              └────────────────────────────┘
  ┌────────────────────────────┐
  │ #5 CAPABILITY-GATING (可选) │ — user 在 §10 决；若纳入则与 #1 并行
  └────────────────────────────┘

B 轨（doc）：
  ┌────────────────────────────┐
  │ inventory pass 1           │ ──────┐
  │ (从 §10.4 + Phase 4 §8 取)   │      │
  └────────────────────────────┘       │
                                        ▼
                            ┌────────────────────────────┐
                            │ 分类 + frontmatter 模板     │ ──────┐
                            │ (主维度 wire/cross/in；副维度 audience) │
                            └────────────────────────────┘       │
                                                                 ▼
                                              ┌────────────────────────────┐
                                              │ 30 文件 SSOT + INDEX.md     │
                                              │ (随 A 轨改动持续吸收)        │
                                              └────────────────────────────┘

C 轨（test）：
  ┌────────────────────────────┐
  │ 既有 freeze test 清查       │ ──────┐
  │ (cs_parity 4 + node_kind / │      │
  │  edge_kind / topic 等)      │      │
  └────────────────────────────┘       │
                                        ▼
                            ┌────────────────────────────┐
                            │ freeze test 扩展 ≥5 项      │ ──────┐
                            │ (推 cs_parity 模式)          │       │
                            └────────────────────────────┘       │
                                                                 ▼
                                              ┌────────────────────────────┐
                                              │ A 轨改动 CI 守护 + 收口      │
                                              └────────────────────────────┘

──────────────────────────────────── ────────────────────────────────────
Sync 点：每个 sync 点三轨各自 mini-completion-report 对账
```

### §7.2 哪些必须串行

| 串行链 | 理由 |
|:--|:--|
| A 轨 #1 → A 轨 #2 → A 轨 #3 | Plan dispatch 调 archive_to_graphiti 调 IdleArchiveTrigger（_is_nanobot_idle）有依赖关系 |
| B 轨 inventory → B 轨 分类 → B 轨 SSOT | 必须 inventory 完成才能稳定分类，分类稳定才能写 SSOT |
| C 轨 既有清查 → C 轨 扩展 | 必须知道现有覆盖才能扩 |

### §7.3 哪些可以并行

| 并行 | 理由 |
|:--|:--|
| A 轨 #4 disk-recover 与 A 轨 #1 #2 #3 | 独立模块，无依赖 |
| A 轨 #5 capability-gating（若纳入）与 A 轨 #1 | 独立 axis（model 元数据 vs Plan 派发）|
| A 轨 任何项 与 B 轨 inventory | doc 是被动追踪 |
| A 轨 任何项 与 C 轨 freeze test 扩展 | freeze test 反过来守护 A 轨 |

### §7.4 最小可验证落地（MVP）序列

```
若 user 想"最快看到一个东西落地"，推荐 MVP 序列：

Step 1（1-2 天）: A 轨 #1 PLAN-INTEGRATION 收口（仅 plan-dispatch + plan-step-result-route 两个 TODO，不包括 plan-bb-namespace）
Step 2（半天）: B 轨 写 in_process/plan-and-execute_v1.md 单文件（不全展开 30 文件）
Step 3（半天）: C 轨 加 1 个 plan-* freeze test
Step 4: user 看一眼 → sign off "这个节奏 OK" → 后续按 §7.1 全展开
```

---

## §7.5 B 轨提炼策略附录（user 2026-05-07 sign off + amended）

> 本节回答 user 追问："接口提炼顺序？哪开始？模块独立 vs 一起？双线并行得两份再合并值得吗？如何实现 — 独立工作区？"
>
> **决策 5 项已 sign off**（Q9 = Z / Q10 = req-first amended / Q11 = layered_parallel / Q12 = subdir_per_layer / Q13 = req-first-2d amended）。
>
> **2026-05-07 amendment（user 方法论修正）**：
>
> 1. **driver 方向修正**：接口提炼 driver = (1) 拓扑边界（分类维度）+ (2) App 流程 + 需求 + 能力（驱动内容）；接口是 **derived**。**既有骨架代码 = 参考 / 升级起点 / 验证锚点，不是反推源头**。
> 2. **当前代码定位**："跑通分叉路的几条验证通路验证代码架构设计"——不是终态；接口提炼会驱动既有代码 / 协议**升级**。
> 3. **顺序修正**：4-B-req **先跑**（不是 4-B-wire）；req 提炼出"需求 + App 流程 + 能力清单"作为驱动源 → 4 个其他 sub-chat 各自从 req inventory 驱动接口提炼 → 既有代码反向 grep **验证**（不是反推）。
> 4. **产出目录**：移到 `.cursor/memory/interfaces/`（不是 `architecture/interfaces/`）。

### §7.5.0 方法论原则（amendment 核心）

#### §7.5.0.1 driver 优先级

```
[1st driver: 拓扑边界]               (分类维度，Q2 已锁 wire/cross/in/cap/req)
                ↓ shape
[2nd driver: App 流程 + 需求 + 能力]  (内容来源，从 ar_app_flow §4 8 步 + 67 需求 + 能力清单)
                ↓ derive
[3rd: 接口提炼]                       (按 Q12 子目录归类，状态 locked / evolving / proposed-upgrade / proposed-new)
                ↓ verify
[4th: 既有代码 grep 验证 + 协议 upgrade roadmap]
```

#### §7.5.0.2 既有代码与协议的角色（明确禁止反推）

| 角色 | 允许 | 禁止 |
|:--|:--|:--|
| **参考**（reference） | 看代码理解某个能力**已经怎么实现** | ❌ 拿代码符号当接口列表起点 |
| **升级起点**（upgrade-from） | 在 frontmatter `upgrade_from:` 标"我从哪里升级" | ❌ "代码这样写，所以接口就是这样" |
| **验证锚点**（verification） | 接口提炼完成后，反向 grep 验证 producer/consumer 实证 | ❌ "grep 出来的符号就是接口候选，缺的就漏了" |
| **填洞**（gap-fill） | 缺口反向追到代码哪里要补 | ❌ "代码已经这么干了，接口就这么定" |

**为什么这条原则关键**：当前代码状态 = "跑通分叉路几条验证通路"，**反推会把临时实现锁成正式接口**——比如 `_state_context.py` selection-C 是 Phase 4 临时方案、`FocusBboxThreshold` 是 Phase 4 临时阈值器（per Phase 4 §8 L13 显式禁止 export `Attention` 类），如果反推就会把临时性当永久接口。

### §7.5.1 双线并行 vs 单线 — 决策 Q9 = Z（grep 兜底）

| 方案 | 工时 | 漏检率 | 一致性风险 | 是否选 |
|:--|:--|:--|:--|:--|
| X. 单线 top-down | 1× | 中（漏 5-10 个 in-process 隐式接口）| 低 | ❌ |
| Y. 双线全套并行 → diff → merge | 1.8-2× | 极低 | **高**（两套分类表合并冲突）| ❌ |
| **Z. driver 主线 + bottom-up grep 验证** | 1.2× | 低（driver 漏的 grep 会捞到，作为缺口或漂移登记）| 0 合并冲突 | ✅ |

**理由**：
1. driver 主线（req → cap → 接口）漏的，grep 验证阶段会捞回来——这些通常是隐式 in-process 接口
2. grep 不是 driver，是 verifier；不会污染分类维度
3. wire / cross-process 已在 Phase 4 §8 + bus_v4 + protocol_snapshot_p1 中文档化 90%，driver + grep 双向都覆盖

### §7.5.2 grep 验证脚本（Stage 4 用，不是 Stage 1 driver）

```bash
# 主 chat 在 Stage 4 跑（4-B-req / cap / 4 个层 sub-chat 全部完成后）
# 任务：核对每接口面是否有 producer/consumer 实证 + 找出"代码有但接口未定义"的漂移

# Producer / consumer / 注册侧
rg "^def attach_" src/parrot/                       # attach helper（应在 in_process/）
rg "^def register_" src/parrot/                     # Strategy 注册表
rg "class.*Strategy" src/parrot/dsg/                # AttentionDecayStrategy / FoldStrategy 等
rg "class.*Backend" src/parrot/                     # IntentWorkspaceBackend / DiskBackend
rg "@dataclass" src/parrot/shared/                  # 协议 dataclass 全集
rg "class.*Protocol" src/parrot/                    # Protocol 接口（PoolAdmissionPolicy 等）
rg "Pub/Sub|Redis Stream|Redis Hash" src/parrot/    # Redis 消费侧
rg "TOPIC_|EVENT_TYPE_|RPC_METHOD_" src/parrot/     # wire 常量

# Unity 侧
rg "RegisterMethodAsync|PublishData|DataReceived" unity/ArSpike/Assets/Scripts/ParrotApp/
rg "EcpEvent|EcpCommand|EcpAck|EcpState" unity/ArSpike/Assets/Scripts/ParrotApp/

# 输出对账：
#   - 主线 doc 已覆盖的符号 = ✅ 验证通过
#   - 主线 doc 未覆盖的符号 = ⚠️ 漂移 → 决定补接口或改代码
#   - 主线 doc 有但代码无的接口 = 🆕 缺口 → 推 upgrade_roadmap
```

**输出物**：`interfaces/_sync/grep_verification_20260507.md`（Stage 4 收口产）。

### §7.5.3 提炼顺序 — 决策 Q10 修订为 req-first（5 阶段）

| 阶段 | 子目录 / 文件 | 时长（估）| Driver 来源 | 输出 |
|:--|:--|:--:|:--|:--|
| **1. 需求 + App 流程**（4-B-req）| `interfaces/needs_inventory.md` + `app_flow_inventory.md` | 1.5-2 天 | `ar_app_flow_ui_design.md §4` 8 步 + `requirements.md` 67 项 + `ar_feature_vision.md` + `ar_app_plan.md`（仅追溯）+ `parrot_behavior_rules.md`（行为契约）| 功能需求清单（**不绑代码**）|
| **2. 能力**（4-B-cap）| `interfaces/capabilities_inventory.md` + `capability/` 7 文件 | 1.5 天 | 阶段 1 输出 + 既有 brain tools / triggers / Strategy 集合 | "应有 / 已有 / 缺口 / 漂移" 四态能力表 |
| **3. 接口提炼**（4-B-wire / 4-B-cross / 4-B-in **并行**）| `interfaces/{wire, cross_process, in_process}/` 25 文件 | 4-5 天 | 阶段 2 输出 + Q2 拓扑边界归类 + 既有 Phase 4 §8 / DSG 7 协议（升级起点）| 25 接口文件，每文件 frontmatter 9 字段 + status 含 `proposed-upgrade` / `proposed-new` |
| **4. 代码 grep 验证 + upgrade 缺口收集**（主 chat） | `_sync/grep_verification_*.md` + `upgrade_roadmap.md` | 1 天 | 阶段 3 输出 + grep 脚本（§7.5.2） | 缺口 + 漂移 + upgrade plan |
| **5. INDEX 收口 + 完成报告**（主 chat）| `interfaces/INDEX.md` + `interface_extraction_completion_*.md` | 1 天 | 阶段 1-4 全部 sync report | 单一真源入口 + 完成判据全过 |

**总工期 ~9-10 天**，**4-B-req 是入场 first**（不是 wire）；**4-B-wire / cross / in 在阶段 3 同时启动**（拿到阶段 2 能力清单后并行）。

**理由（amendment 后）**：
1. **driver 优先**：req → cap → 接口（按 Q2 拓扑分类）→ 验证 → upgrade
2. wire 不再是 first：因为它的内容**应该由需求驱动**，而不是 "Phase 4 §8 锁了什么我就 inventory 什么"——wire 也可能有 proposed-upgrade（如 PlanUI wire / body_state 解锁）和 proposed-new（如未来菜单画布的 4 类块切换 wire）
3. 既有代码与协议是 "我从哪里 upgrade" 的锚点，不是 "我从哪里推导" 的源头

### §7.5.4 模块独立 vs 一起 — 决策 Q11 = layered_parallel + 9 字段强制

**6 个 sub-chat 角色（包括主 chat）**：

```
Chat 4 主协调 chat（你的 entry point；本 chat 起步）
│
├── Sub-chat 4-A 实施 TODO（A 轨：scheduler/plan/archive/nanobot/disk-recover）
│
├── Sub-chat 4-B-req  Stage 1：写 needs_inventory + app_flow_inventory   ← FIRST
├── Sub-chat 4-B-cap  Stage 2：写 capabilities_inventory + capability/   ← 串接 4-B-req
├── Sub-chat 4-B-wire   Stage 3：写 wire/ 9 文件      ┐
├── Sub-chat 4-B-cross  Stage 3：写 cross_process/    ├ 并行（依赖 4-B-cap 输出）
├── Sub-chat 4-B-in     Stage 3：写 in_process/       ┘
│
└── Sub-chat 4-C freeze test 扩展（C 轨；与 4-B-wire 并行启动定型）
```

**深入度强制 — 每接口文件 frontmatter 9 字段（amended，从 7 → 9）**：

```yaml
---
status: locked | evolving | experimental | proposed-upgrade | proposed-new
                                          ↑          ↑
                                          ↑   既有但需升级    ↑   应有但代码缺
interface_id: <唯一稳定 ID，如 wire-ecp-event-v1>
topology: wire | cross_process | in_process | capability
ai_priority: high | medium | low
ai_audience: ai_only | human_only | both
schema_version: <int>

driven_by:                                              # ⚠️ amendment 新增
  - "needs:NEED-XX" 或 "app-flow:step-N" 或 "capability:CAP-YY"
  # 强制：每接口必须能追到至少 1 个需求 / 流程步 / 能力（不允许"代码这样写所以接口这样"）

upgrade_from: <既有代码符号或 doc 引用，仅 proposed-upgrade 状态填> # ⚠️ amendment 新增
freeze_test: <test 路径，或 explicit "deferred-to-Chat-N">  # 强制
producer: <code 真源单一行>                                  # 强制 — 验证阶段填
consumer: ["<grep evidence 1>", ...]                        # 强制 — 验证阶段填

last_locked: <YYYY-MM-DD，仅 wire 类必填>
last_reviewed: 2026-05-07
related: ["<interface_id 引用清单>"]
---
```

**关键 — `driven_by` 字段强制阻止从代码反推**：你不能写"看 `attach_ecp_event_ingest` 已经存在所以接口是 X"——必须先 cite 来自 `needs:NEED-FOCUS-BBOX-PLACEMENT`（举例）或 `app-flow:step-7-tool-cabinet` 或 `capability:CAP-attention-anchor`，然后才轮到 producer/consumer/upgrade_from 填实证。

### §7.5.5 工作区隔离 — 决策 Q12 = subdir_per_layer（**目录路径修订**）

```
.cursor/memory/interfaces/                  ⚠️ amendment：移到 .cursor/memory/ 顶级（不是 architecture/）
├── INDEX.md                       # 仅主 chat 写；单一真源入口
├── README.md                      # 顶层导览：方法论 + driver 来源 + 拓扑边界 + 状态约定
├── methodology.md                 # 方法论原则（§7.5.0 amendment 落地）
│
├── needs_inventory.md             # 仅 4-B-req 写（Stage 1）
├── app_flow_inventory.md          # 仅 4-B-req 写（Stage 1）
├── capabilities_inventory.md      # 仅 4-B-cap 写（Stage 2）
│
├── wire/                          # 仅 4-B-wire 写（Stage 3）
│   └── (9 文件)
├── cross_process/                 # 仅 4-B-cross 写（Stage 3）
│   └── (6 文件)
├── in_process/                    # 仅 4-B-in 写（Stage 3）
│   └── (10 文件)
├── capability/                    # 仅 4-B-cap 写（Stage 2 末段）
│   └── (7 文件)
│
├── upgrade_roadmap.md             # Stage 4 输出：缺口 + 漂移 + upgrade plan
├── deprecation.md                 # 接口废弃流程（per ADR §5.5）
├── extension_points.md            # 第三方扩展占位（per ADR §5.5）
├── schema_evolution.md            # schema_version 演进策略
├── change_impact_table.md         # 变更影响表
│
└── _sync/                         # 跨 sub-chat 协调区
    ├── grep_verification_20260507.md       # Stage 4 验证产
    ├── 4-B-req_completion.md
    ├── 4-B-cap_completion.md
    ├── 4-B-wire_completion.md
    ├── 4-B-cross_completion.md
    ├── 4-B-in_completion.md
    └── 4-C_freeze_test_summary.md
```

**关键约束（amendment）**：
| 约束 | 机制 |
|:--|:--|
| **位置移到 `.cursor/memory/interfaces/`** | 与 `architecture/` `lore/` `skills/`（外部）等同级 — 接口提炼是单独主题，不是 architecture 子集 |
| 每个 sub-chat 只写自己的子目录 | 0 merge 冲突；git 树天然隔离 |
| INDEX.md / README.md / methodology.md 仅主 chat 写 | sync 点 merge — 不允许 sub-chat 直写 |
| `_sync/` 各自完成报告 | 主 chat 据此 merge；mini-completion-report 模板（参考 lineb / dsg_l1_5 / goslo_mod 三份）|

### §7.5.6 节奏与 sync 点 — 决策 Q13 修订为 req-first-2d（**MVP 起步**）

```
T0    : 主 chat 立 interfaces/ 目录骨架（INDEX.md + README.md + methodology.md + _sync/）
        启动 4-A（实施轨，独立）
        启动 4-B-req（Stage 1：需求 + App 流程 inventory）  ← FIRST
        启动 4-C 框架定型（与 wire 同启动；先空跑 freeze test framework）

T+2d  : 4-B-req 完成 → sync report → user 看一眼"功能需求 + App 流程清单是否完整"
        ↓ user sign off
T+2d  : 4-B-cap 启动（Stage 2：能力 inventory，串接 req 输出）

T+4d  : 4-B-cap 完成 → sync → user 看一眼"能力清单 + 缺口判定 是否合理"
        ↓ user sign off
T+4d  : 4-B-wire / 4-B-cross / 4-B-in 三 chat **并行**启动（Stage 3：接口提炼）
        4-C freeze test 同步推

T+8d  : 4-B-wire / 4-B-cross / 4-B-in 完成 → sync
        4-C freeze test 第一批落地
        ↓
T+9d  : 主 chat Stage 4 跑 grep 验证 + upgrade_roadmap 落地
        4-A 实施收口

T+10d : Stage 5 主 chat merge INDEX + 完成报告 interface_extraction_completion_20260507.md
```

**总工期 ~10 天**（含 1 天 buffer + 1 天扫尾）。

**MVP 起步（amended）**：T0-T2 仅 4-B-req 跑 2 天，**user 倒查"需求+App 流程清单"是否完整 + 方法论是否被遵守**——这是规划稿落地的"第一个证据"。如果方法论走歪（比如 inventory 写得像在 reverse code），主 chat 可以 abort 重来，成本最低。

### §7.5.7 sub-chat 入场 prompt 模板（amended — 每 sub-chat 必带 driver 声明）

每个 sub-chat 入场 prompt 含：

```
你是 Chat 4 接口提炼实施 chat — sub-chat <X>（仅写 .cursor/memory/interfaces/<X>/）

必读（按顺序）：
1. 父规划稿 + sign-off 决策矩阵：interface_extraction_plan_20260507.md §0.2 + §7.5
2. 父 ADR：adr_protocol_upgrade_and_interface_refinement_background_20260504.md
3. Phase 4 §8 决策锁：sprint4_phase4_entry_20260430.md §8
4. 方法论原则：interfaces/methodology.md（§7.5.0 落地）
5. 驱动来源（视 sub-chat 角色）：
   - 4-B-req: ar_app_flow_ui_design.md §4 8 步 + requirements.md 67 项 + ar_feature_vision.md
   - 4-B-cap: 4-B-req 输出（needs_inventory + app_flow_inventory）
   - 4-B-wire / cross / in: 4-B-cap 输出（capabilities_inventory）+ Q2 拓扑边界归类
6. 既有代码 anchor（仅作 reference / upgrade 起点 / 验证锚点 — 不允许反推）

任务：
- 仅写 .cursor/memory/interfaces/<X>/ 目录下的 N 个 markdown 文件
- 每文件强制 9 字段 frontmatter（§7.5.4 amended 模板）
- 每接口必须 cite driven_by（来自需求 / 流程步 / 能力）— 不允许从 producer 反推
- 状态分级（locked / evolving / experimental / proposed-upgrade / proposed-new）必须明确
- 跨文件 cross-link 用 interface_id（引父 INDEX.md 待主 chat merge）
- 不允许：动其他 sub-chat 目录；重新设计分类维度；触动 Phase 4 §8 锁；从代码符号反推接口

收口：
- 写 _sync/4-B-<X>_completion.md
- 列：覆盖了哪些 driver（needs/app-flow/capability item）；遗留 finding；测试基线 0 漂移证据；产出 freeze test path 清单（cross-link 4-C）

完成判据：
- N 个文件落地 + 9 字段 frontmatter 全填 + driven_by 全 cite + sync report 落地
```

### §7.5.8 风险 — 与 §9 衔接（amended）

| 新增风险 | 严重度 | 修复 |
|:--|:--|:--|
| R10 grep 验证脚本未 catch 某些隐式接口（如 BB writer 单一性约束）| 🟢 low | 主 chat Stage 4 二轮扫尾时手工补充 grep 模式（如 `bb.set\(`）|
| R11 sub-chat 分阶段间引用顺序错（4-B-cap 在 4-B-req 之前启动）| 🟡 mid | §7.5.6 节奏：4-B-req → 4-B-cap → 3 个层 sub-chat 串接强制 |
| R12 4-B-in 深入度超时（10 文件 × 复杂 in-process 实现） | 🟡 mid | §7.5.6 给 1 天 buffer；超时切 split chat（前 5 文件先收，后 5 文件 follow-up）|
| R13 sub-chat 模板理解走样 | 🟡 mid | 4-B-req 是模板定型 chat — 主 chat 收 sync 时审 frontmatter + driven_by 是否被遵守 |
| **R14 反推代码倾向**（amendment 新增）| 🔴 high | methodology.md 明文禁止 + 9 字段 driven_by 强制 cite + sub-chat 入场 prompt 显式约束 + Stage 4 反向校验"每接口的 driven_by 是否真在 Stage 1/2 inventory 里"|
| **R15 既有临时实现被锁成正式接口**（amendment 新增）| 🔴 high | status 强制分级（experimental / proposed-upgrade）+ Phase 4 §8 L13 那种"非 L3 临时实现"必须显式标 experimental + 不允许 locked 状态 |

### §7.5.1 双线并行 vs 单线 — 决策 Q9 = Z（grep 兜底）

| 方案 | 工时 | 漏检率 | 一致性风险 | 是否选 |
|:--|:--|:--|:--|:--|
| X. 单线 top-down | 1× | 中（漏 5-10 个 in-process 隐式接口）| 低 | ❌ |
| Y. 双线全套并行 → diff → merge | 1.8-2× | 极低 | **高**（两套分类表合并冲突）| ❌ |
| **Z. 单线 + bottom-up grep 兜底** | 1.2× | 低（grep 自动覆盖盲区） | 0 合并冲突 | ✅ |

**理由**：
1. 双线全套并行的真痛点不在工时，在"两套分类表合并冲突 — user 要再 sign off 一次维度"
2. 漏检风险主要集中在 in-process 层（attach helper / Strategy 注册表 / observer hook），grep 自动化成本极低（5-8 行 bash），收益高
3. wire / cross-process 已在 Phase 4 §8 + bus_v4 + protocol_snapshot_p1 中文档化 90%，grep 帮助有限

### §7.5.2 grep 兜底脚本（B 轨入场前先跑一次，扫尾再跑一次）

```bash
# 跑一遍把"接口候选符号"全捞出来，与主线 doc 对账
rg "^def attach_" src/parrot/                       # 5+ 个 attach helper
rg "^def register_" src/parrot/                     # Strategy 注册表
rg "class.*Strategy" src/parrot/dsg/                # AttentionDecayStrategy / FoldStrategy 等
rg "class.*Backend" src/parrot/                     # IntentWorkspaceBackend / DiskBackend
rg "@dataclass" src/parrot/shared/                  # 协议 dataclass 全集
rg "class.*Protocol" src/parrot/                    # Protocol 接口（PoolAdmissionPolicy 等）
rg "Pub/Sub|Redis Stream|Redis Hash" src/parrot/    # Redis 消费侧
rg "TOPIC_|EVENT_TYPE_|RPC_METHOD_" src/parrot/     # wire 常量

# Unity 侧
rg "RegisterMethodAsync|PublishData|DataReceived" unity/ArSpike/Assets/Scripts/ParrotApp/
rg "EcpEvent|EcpCommand|EcpAck|EcpState" unity/ArSpike/Assets/Scripts/ParrotApp/

# 输出对账：主线 doc 没覆盖的符号 = 漏检 → B 轨 sub-chat 必须吸收
```

**输出物**：`architecture/interfaces/_sync/grep_candidate_inventory_20260507.md`（候选清单 — 由主 chat 在 4-B-wire 启动前生成）。

### §7.5.3 提炼顺序 — 决策 Q10 = C（拓扑稳定性递减）

| 阶段 | 子目录 | 文件数（估） | 时长（估） | 文档已有量 | 深入难度 |
|:--|:--|:--:|:--:|:--|:--|
| 1 | `interfaces/wire/` | 9 | 2 天 | 90%（Phase 4 §8 + completion 报告 + cs_parity）| 低 |
| 2 | `interfaces/cross_process/` | 6 | 2 天 | 70%（bus_v4 + protocol_snapshot_p1）| 中 |
| 3 | `interfaces/in_process/` ⚠️ | 10 | 2-3 天 | 30%（散落代码注释，主战场）| **高 — 必须 grep 兜底** |
| 4 | `interfaces/capability/` | 7 | 1 天 | 60%（completion 报告摘）| 中 |
| 5 | `requirement_coverage` 等元接口文件 | 5 | 1 天 | n/a（模板）| 低 |

**理由**：
1. 稳定性递减 — wire（13 锁全护）→ requirement（67 项最不稳）
2. 文档已有量递减 — wire 已经被 90% inventory；in-process 几乎只能 reverse code
3. 依赖方向 — 上层引用下层稳定接口；下层定型后上层才有锚点
4. 与 §3.2 推荐主维度目录顺序完美对齐

### §7.5.4 模块独立 vs 一起 — 决策 Q11 = layered_parallel

**5 个 sub-chat 按拓扑层分工 + 共享模板 + 共享 INDEX**：

```
4-B-wire   写 wire/ 9 文件        ← 最先启动，定型模板 + freeze test 模式
4-B-cross  写 cross_process/ 6 文件
4-B-in     写 in_process/ 10 文件  ← 强制用 grep 兜底；最深入区
4-B-cap    写 capability/ 7 文件
4-B-req    写 requirement_coverage / deprecation / extension / schema_evolution / change_impact_table
```

**深入度强制（每个 interface 文件强制 frontmatter 7 字段）**：

```yaml
---
status: locked | evolving | experimental
interface_id: <唯一稳定 ID，如 wire-ecp-event-v1>
topology: wire | cross_process | in_process
ai_priority: high | medium | low
ai_audience: ai_only | human_only | both
schema_version: <int>
freeze_test: <test 路径，或 explicit "deferred-to-Chat-N">    # 强制
producer: <code 真源单一行>                                   # 强制 — grep 实证
consumer: ["<grep evidence 1>", "<grep evidence 2>", ...]    # 强制 — grep 实证
last_locked: <YYYY-MM-DD，仅 wire 类必填>
last_reviewed: 2026-05-07
related: ["<interface_id 引用清单>"]
---
```

**这 3 个强制字段（freeze_test / producer / consumer）会逼出深度** — 不能写"observer/sighting.py 大致是个 sighting 处理器"——必须给 producer 单一代码行 + consumer grep 实证 + freeze test path（或显式 defer）。

**一致性强制**：
- INDEX.md 单一目录树（只主 chat 写）
- 主+副维度在 §3 lock 后所有 sub-chat 必须遵守
- 跨文件 cross-link 用 `[<interface_id>](<path>)` 而不是裸文件名
- 4-C freeze test 统一推 cs_parity 模式（5 sub-chat 都用同一 framework）

### §7.5.5 工作区隔离 — 决策 Q12 = subdir_per_layer

```
.cursor/memory/architecture/interfaces/
├── INDEX.md                       # 仅主 chat 写
├── wire/                          # 仅 4-B-wire 写
│   └── (9 文件)
├── cross_process/                 # 仅 4-B-cross 写
│   └── (6 文件)
├── in_process/                    # 仅 4-B-in 写
│   └── (10 文件)
├── capability/                    # 仅 4-B-cap 写
│   └── (7 文件)
├── requirement_coverage.md        # 仅 4-B-req 写
├── deprecation.md                 # 同上
├── extension_points.md            # 同上
├── schema_evolution.md            # 同上
├── change_impact_table.md         # 同上
│
└── _sync/                         # 跨 sub-chat 协调区
    ├── grep_candidate_inventory_20260507.md       # 主 chat 入场前跑生成
    ├── 4-B-wire_completion.md                     # 4-B-wire 收口产
    ├── 4-B-cross_completion.md
    ├── 4-B-in_completion.md
    ├── 4-B-cap_completion.md
    ├── 4-B-req_completion.md
    └── 4-C_freeze_test_summary.md                 # C 轨同步
```

**关键约束**：
| 约束 | 机制 |
|:--|:--|
| 每个 sub-chat 只写自己的子目录 | 0 merge 冲突；git 树天然隔离 |
| INDEX.md 主 chat 单写 | sync 点 merge — 不允许 sub-chat 直写 INDEX |
| `_sync/` 各自完成报告 | 主 chat 据此 merge；mini-completion-report 模板（参考 lineb / dsg_l1_5 / goslo_mod 三份）|
| sub-chat 入场 prompt | 主 chat 给每 sub-chat 的入场 prompt 模板（详 §7.5.7）|

### §7.5.6 节奏与 sync 点 — 决策 Q13 = wire_first_2d（MVP 起步）

```
T0    : 主 chat 跑 grep 兜底 → 输出 _sync/grep_candidate_inventory_20260507.md
        主 chat 启动 4-A（实施轨）+ 4-B-wire（doc 主 sub-chat）

T+2d  : 4-B-wire 完成 → sync report → user 看一眼模板是否 OK
        ↓ user sign off "模板 OK"
T+2d  : 4-B-cross 启动 / 4-B-in 启动 / 4-C 启动（套用同模板）

T+5d  : 4-B-cross 完成
T+6d  : 4-B-in 完成（多 1 天 buffer 给深入）
T+5d  : 4-C 第一批 freeze test 完成
        ↓ sync
T+6d  : 4-B-cap 启动 / 4-B-req 启动

T+8d  : 4-B-cap / 4-B-req 完成 → 主 chat merge INDEX.md
T+9d  : 主 chat 二轮 grep 兜底扫尾（确认 0 残留候选）
        4-A 实施收口
T+10d : 总收口报告 interface_extraction_completion_20260507.md
```

**总工期 ~10 天**（含 1 天 in-process buffer + 1 天扫尾）。

### §7.5.7 sub-chat 入场 prompt 模板

每个 4-B-* sub-chat 入场 prompt 含：

```
你是 Chat 4 接口提炼实施 chat — sub-chat <X>（仅写 architecture/interfaces/<X>/）

必读（按顺序）：
1. 父规划稿 + sign-off 决策矩阵：interface_extraction_plan_20260507.md §0.2 + §7.5
2. 父 ADR：adr_protocol_upgrade_and_interface_refinement_background_20260504.md
3. Phase 4 §8 决策锁：sprint4_phase4_entry_20260430.md §8
4. 主 chat 跑出的 grep 候选清单：_sync/grep_candidate_inventory_20260507.md
5. 你层目录的源代码 anchor（按 §7.5.3 表格指引）

任务：
- 仅写 architecture/interfaces/<X>/ 目录下的 N 个 markdown 文件
- 每文件强制 7 字段 frontmatter（§7.5.4 模板）
- 每文件强制 producer + consumer grep 实证（不允许仅 doc 描述）
- 跨文件 cross-link 用 interface_id（引父 INDEX.md 待主 chat merge）
- 不允许：动其他 sub-chat 目录；重新设计分类维度；触动 Phase 4 §8 锁

收口：
- 写 _sync/4-B-<X>_completion.md（参考 lineb_implementation_completion 风格 mini）
- 列：覆盖了哪些候选符号；遗留 finding；测试基线 0 漂移证据；产出 freeze test path 清单（cross-link 4-C）

完成判据：
- N 个文件落地 + 7 字段 frontmatter 全填 + grep 实证齐 + sync report 落地
```

### §7.5.8 风险 — 与 §9 衔接

| 新增风险 | 严重度 | 修复 |
|:--|:--|:--|
| R10 grep 兜底脚本未 catch 某些隐式接口（如 BB writer 单一性约束）| 🟢 low | 主 chat 二轮扫尾时手工补充 grep 模式（如 `bb.set\(`）|
| R11 sub-chat 分层间引用顺序错（4-B-cross 引用 4-B-wire 时 wire 还没定型）| 🟡 mid | §7.5.6 节奏：4-B-wire 必须先完成 sync 才允许其他启动 |
| R12 4-B-in 深入度超时（10 文件 × 复杂 in-process 实现） | 🟡 mid | §7.5.6 给 1 天 buffer；超时切 split chat（前 5 文件先收，后 5 文件 follow-up）|
| R13 sub-chat 模板理解走样 | 🟡 mid | 4-B-wire 是模板定型 chat — 主 chat 收 sync 时审 frontmatter 是否被遵守 |

---

## §8 验收判据（§3.8 答案）

### §8.1 测试基线

| 阶段 | 基线 | 守护项 |
|:--|:--|:--|
| 当前（Chat 4 入场前）| **415/415** ✅ | Phase 4 §8 13 / cs_parity 4/4 / ADR-L1.5-001 11/11 / source dispatch 11/11 / 既有 392/392 |
| Chat 4 完成时 | **≥ 423/423** | A 轨 5 项 TODO 各加 ≥1 测试 (5+) + C 轨 freeze test ≥3 项扩展 = +8 净增 |

### §8.2 0 漂移守护清单

| 守护项 | 验证方式 |
|:--|:--|
| Phase 4 §8 13 锁 0 漂移 | `pytest tests/ --ignore=tests/integration` 全绿 + cs_parity 4/4 + 手工 git diff `src/parrot/shared/{ecp_event,bb_schema,ref_binding,ecp}.py` 仅 plumbing 改动 |
| ADR-L1.5-001 §4.1 三触发器 | `tests/test_dsg/test_l2b_node_source_dispatch.py` 11/11 + `test_no_semantic_node_subclass_introduced` |
| LineB 双管线兼容 | ObservationSource 7 entries verbatim + transcript_extractor alias 不破 |
| GOSLO ParrotAnimation enum | `RESERVED_PARROT_CAPABILITY_IDS = frozenset(a.value for a in ParrotAnimation)` 8 项不动 |

### §8.3 Chat 4 完成判据（参考 LineB / DSG Chat 2 / GOSLO mod 三份完成报告格式）

| 判据 | 说明 |
|:--|:--|
| ☑ 7 项 Chat 4 主场任务全部 close | 4 plan-* + nanobot-heartbeat + archive-llm + disk-recover；可选 capability-gating |
| ☑ 接口 SSOT 单份多文件落地 | `architecture/interfaces/INDEX.md` + ~30 接口文件（视实测调） |
| ☑ freeze test 扩展 ≥3 项 | 推 cs_parity 模式到 NodeKind / EdgeKind / RefKind / topic 常量 / EcpEventSource 任意 ≥3 axis |
| ☑ 测试基线 ≥ 423/423 | 不退；新增有效 |
| ☑ Phase 4 §8 13 锁 0 漂移 | git diff 守 |
| ☑ cross-chat-registry §5 Chat 4 行的标签全 close 或显式 defer | 残留必须移到 §8 历史区或注明推哪个 chat |
| ☑ 完成报告 sign-off | 参考 lineb / dsg_l1_5 / goslo_mod 三份完成报告格式产出 `interface_extraction_completion_*.md` |

### §8.4 守住硬约束在规划阶段就锁

本规划稿在以下设计点已显式锁住硬约束：

1. §1.1 范围表 — 协议层显式标"0 修改 + 全量 inventory"
2. §3.2 主分类维度 wire 块下显式 cross-link Phase 4 §8.1 13 锁
3. §4.3 frontmatter 模板含 `last_locked: 2026-04-30`（wire 类）字段
4. §4.2 无任何文件名暗示"重新设计协议合同"
5. §7.1 A 轨任务全程"实施 = plumbing + LLM 蒸馏 + heartbeat 写者"，**0 wire schema / 0 enum / 0 BB key 名字改**
6. §8.2 守护清单显式列每项

---

## §9 风险 + 修复路径

### §9.1 主风险表

| # | 风险 | 严重度 | 触发概率 | 修复路径 |
|:--|:--|:--|:--|:--|
| R1 | 实施 TODO 期间引入 wire 漂移 | 🔴 high | 中 | C 轨 freeze test 在 PR pre-commit 跑；A 轨 #1-#5 任意 PR 必须带 `git diff src/parrot/shared/{ecp_event,bb_schema,ref_binding}.py` 显示空 |
| R2 | 接口分类主维度选错（拓扑边界过早锁定） | 🟡 mid | 低 | B 轨先 inventory 后分类 — 不预设维度；维度从数据浮现 |
| R3 | 单份 SSOT 文档过长 / 难维护 | 🟡 mid | 中 | 多文件分包 + INDEX.md 索引；每文件 100-300 行；frontmatter 引导阅读路径 |
| R4 | NEED-P3-CAPABILITY-GATING 是否纳入 Chat 4 摇摆 | 🟢 low | 高 | §10 user 提问 Q1 显式裁决 |
| R5 | Plan-and-Execute 完整链路（4 个 plan-* TODO）实施时间超估 | 🟡 mid | 中 | §7.4 MVP 序列先验证 plan-dispatch + plan-step-result-route，撑爆再 split chat |
| R6 | 真闲时归档 LLM 蒸馏与 nanobot heartbeat 强耦合，单独验收难 | 🟡 mid | 中 | §7.2 #2 → #3 串行；用 mock 写者先解耦验证 archive 路径，再补 nanobot 真心跳 |
| R7 | freeze test 扩展规模失控（拷贝 cs_parity 模式到 ≥10 axis）| 🟢 low | 低 | §8.1 限定 ≥3 项即可，不强制全覆盖 |
| R8 | doc 与 code 漂移（B 轨写完，A 轨又改了）| 🟡 mid | 中 | §2.3 三轨同步机制 + Chat 4 完成报告显式列 git diff stat |
| R9 | "重新划分模块"诱惑 | 🟢 low | 低 | §6.3 显式裁定不重画 + DSG Chat 2 §9.3 已确认 |

### §9.2 触发回退条件

| 条件 | 回退到 |
|:--|:--|
| Chat 4 实施 chat 中途发现"必须改 wire" | 暂停 → 起新 ADR（按 ADR-PROTOCOL-INTERFACE-001 §7.1 / cross-chat-registry §7 #4）|
| Chat 4 实施 chat 中途发现"必须引入 SemanticNode 子类" | 暂停 → 起新 ADR supersede ADR-L1.5-001 |
| 30 文件分包过粗或过细 | 中途调整文件粒度（小文件合并 / 大文件拆）— 不需要新 ADR，doc 调整即可 |

---

## §10 user 提问清单

> 本节是 user **必答**才能进 Chat 4 实施阶段的关键裁决。**不要每件事都问 user**——只列下面这些真不确定 / 影响大的点。其他可决策都在前面 §1-§9 自决了。
>
> **决策状态**：Q1-Q8 ⏳ 待答；**Q9-Q13 ✅ 已 sign off（user 2026-05-07）**，详见 §7.5。

### Q1. NEED-P3-CAPABILITY-GATING 是否纳入 Chat 4？

**背景**：cross-chat-registry §3.B 标注"Chat 4 增量（轻量，5-15 行 + 1 测试）/ 或 P3 chat（与多模型路由一起做）"。

**含义**：Brain Agent 启动时读 active model manifest 的 `declared_capability_ids`，**只把 model 实现的动作对应的 tool 注册给 LLM**。例：active model 不声明 `fly` → `fly_to` tool 不注册 → LLM 不会调用。

**影响**：
- 取：Chat 4 多 0.5-1 天工作量；非鹦鹉模型 LLM 不会调用 `fly_to`（避免视觉违和）；为 4 类块"模型块"建立运行期接口契约的实施前置
- 舍：留 P3 多模型路由 chat 一起做；Chat 4 工作量更聚焦

**推荐**：**取**（轻量增量；与 GOSLO Step 3 已落 model_id 透传同源；为 NEED-P3-B 4 类块铺路）。

**user 答**：[ ] 取 / [ ] 舍 / [ ] 看实施 chat 决定

---

### Q2. 接口分类主维度 — 4 选 1

| 候选 | 描述 | 推荐 |
|:--|:--|:--|
| A. 拓扑边界（wire / cross-process / in-process） | bus_v4 三层协议 + Phase 4 §8 §8.2 通道默认值表天然对齐 | ⭐ 推荐 |
| B. 抽象层级（bytes / topic / schema / behavior contract）| 自下而上学习路径清晰 | |
| C. 角色（Unity / Brain / Nanobot / DSG / Scheduler）| 读者视角清晰，但同一接口对多角色暴露重复内容 | |
| D. audience（ai/human/both）| 文档形式选型驱动，但同接口在 AI/人之间粒度差异大 | 推荐作副维度 |

**user 答**：[ ] A 推荐 / [ ] B / [ ] C / [ ] D / [ ] 其他

---

### Q3. 文档形态 — 单份 vs 双份

| 候选 | 描述 | 推荐 |
|:--|:--|:--|
| A. 单份 SSOT 多文件 + 机器层（Pydantic→JSON Schema） | 0 重复维护；frontmatter 引导阅读；与 ADR 现有风格一致 | ⭐ 推荐 |
| B. 双份分立（人版 + AI 版） | 各自最优形式，但维护成本翻倍，漂移风险高 | |
| C. 散落（不强制统一） | 当前现状，无 single entry | ❌ 不推荐 |

**user 答**：[ ] A 推荐 / [ ] B / [ ] C

---

### Q4. freeze test 模式扩展范围

**候选**（不互斥，可多选）：

- [ ] NodeKind 6 项 enum（DSG-INTENT-EVENT-V1 已有 freeze；扩展到 wire mirror 守护）
- [ ] EdgeKind 8 项 enum（同上）
- [ ] RefKind / RefTargetKind 4+4 项
- [ ] BB key namespace 26 项（writer 单一性 + scope 守）
- [ ] Topic 常量 5 项（DataChannel）
- [ ] EcpEventSource enum 3+1（unity / brain / nanobot 占位 + 未来）
- [ ] BehaviorMode flags 5 项（参考 cs_parity 模式 mirror 到 Unity）
- [ ] ParrotAnimation 8 项 + GOSLO `RESERVED_PARROT_CAPABILITY_IDS`
- [ ] ObservationSource 7 项（per LineB §1.3 verbatim 守护）

**推荐**：**前 5 项**（NodeKind / EdgeKind / RefKind / BB key namespace / Topic 常量），数量 ≥3 项即满足 §8.1 验收。

**user 答**：[ ] 推荐前 5 项 / [ ] 全选 / [ ] 自选 ____

---

### Q5. 需求覆盖度 — 67 功能项 全检 vs 仅接口相关

| 候选 | 描述 | 推荐 |
|:--|:--|:--|
| A. 仅接口相关子集 | 67 项中过滤出与 wire / cross-process / in-process 接口相关的（估计 ~30 项）| ⭐ 推荐（聚焦 Chat 4 主场） |
| B. 67 项全检 | 每项都标接口面 | 工作量大；非接口需求（UI / 美术 / 文档）填充意义低 |

**user 答**：[ ] A 推荐 / [ ] B

---

### Q6. 起点 — 是否就用 module_map_p2 §10.4？

**推荐**：**就用，不重画**（理由：DSG Chat 2 §9.3 已确认 + ASCII 图含 DSG L1.5 升级后形态 + 重画违反 §1.2 不重叠原则）。

**user 答**：[ ] 同意推荐（就用 §10.4）/ [ ] 重画（要求理由）

---

### Q7. 实施 TODO 与 doc 工作的先后

| 候选 | 描述 | 推荐 |
|:--|:--|:--|
| A. 三轨并行（A 实施 / B doc / C test）| 总工期最短（1.5-2 周）；三轨需协调 | ⭐ 推荐 |
| B. 串行：先实施 → 后 doc → 后 test | 总工期长（3-4 周）；最低协调成本 | |
| C. 先 doc 后实施 | doc 先行可发现实施问题，但 A 轨实施可能颠覆 doc | ❌ 不推荐 |
| D. MVP 起步（§7.4），看一眼后再展开 | 风险最低；user 中途可调整节奏 | 推荐作为 A 的"first 2 days" |

**user 答**：[ ] A 推荐（三轨并行）/ [ ] A + D（先 MVP 试 2 天再三轨）/ [ ] B / [ ] 其他

---

### Q8. Chat 4 实施 chat 由哪个 chat 接？

**候选**：
- A. 单 chat 一锅端（A+B+C 三轨在一个 chat 内 sequential 跑）
- B. 三 chat 并行（A 轨 / B 轨 / C 轨 各自独立 chat，按 §2.3 同步对账）
- C. 主 chat（A+C） + 辅助 chat（B）

**推荐**：**B**（每轨独立 chat，主 chat fork 出三 sub-chat；user 在 sync 点统一对账；三轨完成后再合并出 `interface_extraction_completion_20260507.md`）。

> ⚠️ **本问已被 §7.5 Q11 + Q12 细化**：B 轨实际拆为 5 个 sub-chat（4-B-wire / 4-B-cross / 4-B-in / 4-B-cap / 4-B-req）+ A 轨 + C 轨 = 7 sub-chat 总数；按 Q13 用 wire-first MVP 起步。Q8 此处仅决"主 chat 还是单 chat"框架，§7.5 决"具体几个 sub-chat + 启动节奏"。

**user 答**：[ ] A / [ ] B 推荐 / [ ] C

---

### Q9. B 轨提炼策略 — 单线 vs 双线 vs grep 兜底 ✅ 已 sign off

**user 答（2026-05-07）**：**Z. 单线 top-down + bottom-up grep 兜底**（详 §7.5.1 + §7.5.2）

---

### Q10. 提炼顺序 — 从哪开始？✅ 已 sign off + amended

**user 答（2026-05-07 first sign off）**：C. 拓扑稳定性递减（wire → cross → in → cap → req）

**user amendment（2026-05-07 second pass）**：**req-first 5 阶段**（拓扑边界仍是分类维度，但驱动顺序倒过来）：

```
Stage 1: 4-B-req         需求 + App 流程 inventory     ← FIRST
Stage 2: 4-B-cap         能力 inventory（应有/已有/缺/漂）
Stage 3: 4-B-{wire,cross,in} 三轨**并行** 接口提炼（按 Q12 拓扑边界归类）
Stage 4: 主 chat         代码 grep 验证 + upgrade_roadmap
Stage 5: 主 chat         INDEX 收口 + 完成报告
```

详 §7.5.3 + §7.5.6。

---

### Q11. 模块独立 vs 一起 — 提炼粒度 ✅ 已 sign off

**user 答（2026-05-07）**：**分层并行 + 模板强制**（5 sub-chat 按拓扑层分工，共享 frontmatter 7 字段 + 共享 INDEX.md）（详 §7.5.4）

---

### Q12. sub-chat 工作区隔离方式 ✅ 已 sign off

**user 答（2026-05-07）**：**按拓扑层分子目录**（`interfaces/{wire, cross_process, in_process, capability}/`，每 sub-chat 仅写自己目录）（详 §7.5.5）

---

### Q13. MVP 起步节奏 ✅ 已 sign off + amended

**user 答（2026-05-07 first sign off）**：T0-T2 仅 4-B-wire 跑 2 天定型模板。

**user amendment（2026-05-07 second pass）**：**T0-T2 仅 4-B-req 跑 2 天**（Stage 1 needs + app_flow inventory），**user 倒查"需求清单+方法论是否被遵守（无反推代码）"** → sign off → 后续 sub-chat 按 §7.5.6 amended 节奏图展开。

---

## §11 引用

### §11.1 父 + 派发 + 实施入场清单

- 父 INDEX：[`../INDEX.md`](../INDEX.md)
- 父 launch prompt：[`chat4_interface_refinement_launch_prompt_20260507.md`](chat4_interface_refinement_launch_prompt_20260507.md)
- 派发地图：[`sprint4_phase4_downstream_chat_dispatch_plan_20260504.md §1.2 Chat 4`](sprint4_phase4_downstream_chat_dispatch_plan_20260504.md)
- 实施阶段入场清单：[`adr_protocol_upgrade_and_interface_refinement_background_20260504.md §7.1`](adr_protocol_upgrade_and_interface_refinement_background_20260504.md)
- 跨 chat 待办登记表：[`cross_chat_pending_registry_20260507.md`](cross_chat_pending_registry_20260507.md)

### §11.2 三大 chat 完成报告（基线）

- [`sprint4_phase4_completion_and_final_audit_20260430.md`](sprint4_phase4_completion_and_final_audit_20260430.md) — Phase 4 协议契约最终态
- [`lineb_implementation_completion_20260504.md`](lineb_implementation_completion_20260504.md) — LineB 双管线兼容性范本
- [`dsg/dsg_l1_5_implementation_completion_20260506.md`](dsg/dsg_l1_5_implementation_completion_20260506.md) — DSG Chat 2 收口（含 9 处 TODO 标签）
- [`goslo_modularization_completion_20260506.md`](goslo_modularization_completion_20260506.md) + [`goslo_modularization_residual_debt_20260506.md`](goslo_modularization_residual_debt_20260506.md) — GOSLO 模块化收口

### §11.3 决策锁 + 守护

- [`sprint4_phase4_entry_20260430.md §8`](sprint4_phase4_entry_20260430.md) — Phase 4 13 决策锁
- [`adr_l1_5_source_dispatch_extension_space_20260504.md §4.1`](adr_l1_5_source_dispatch_extension_space_20260504.md) — 子类化 3 触发器锁
- [`module_map_p2.md §10.4`](module_map_p2.md) — DSG L1.5 升级后依赖架构图（推荐起点）
- [`bus_v4.md`](bus_v4.md) — 三层协议基线
- [`ar_app_flow_ui_design.md`](ar_app_flow_ui_design.md) — App Flow / UI 基线（候选起点 A）

### §11.4 既有 launch prompt / 完成报告范本

- [`dsg/dsg_l1_5_pool_design_chat_launch_prompt_20260506.md`](dsg/dsg_l1_5_pool_design_chat_launch_prompt_20260506.md) — DSG Chat 2 launch prompt 风格
- [`goslo_model_modularization_launch_prompt_20260506.md`](goslo_model_modularization_launch_prompt_20260506.md) — GOSLO mod launch prompt 风格

---

## §12 变更日志

- **2026-05-07（创建）**：本规划稿创建。Chat 4 实施前置 — 方案规划稿。基于：
  - launch prompt（chat4_interface_refinement_launch_prompt_20260507.md）§3 21 个关键问题
  - 三大 chat 完成报告（Sprint4 Phase 4 / LineB / DSG Chat 2 / GOSLO mod + residual_debt）
  - cross-chat-registry §5 Chat 4 行 + §6 grep 实测（14 个 TODO 标签实际命中）
  - ADR-PROTOCOL-INTERFACE-001 §5 motivating examples + 候选维度 + inventory + 隐含需求
  - Phase 4 §8 13 决策锁
  - ADR-L1.5-001 §4.1 三触发器锁（DSG Chat 2 已确认全未触发）
  - module_map_p2 §10.4（DSG L1.5 升级后依赖架构图）
  - ar_app_flow_ui_design + bus_v4 + parrot_behavior_rules（侧路确认）
  
  覆盖 §0 TL;DR + §1-§9 全部 21 关键问题 + §10 8 项 user 必答 + §11 引用 + §12 变更日志。**0 实施代码 / 0 触动 Phase 4 §8 13 锁 / 0 触动 ADR-L1.5-001 §4.1 三触发器 / 0 重命名 enum 或 wire 字段**。

- **2026-05-07（Q9-Q13 追加）**：user 追问"提炼顺序 / 独立 vs 一起 / 双线并行是否值得 / 工作区如何"。新增 §7.5 提炼策略附录 + §0.2 决策矩阵更新 5 行 + §10 追加 Q9-Q13 5 项已 sign off：
  - Q9 = Z（单线 top-down + bottom-up grep 兜底；1.2x 工时 / 0 合并冲突）
  - Q10 = C（拓扑稳定性递减：wire → cross → in → cap → req）
  - Q11 = layered_parallel（5 sub-chat 按拓扑层分工 + 共享 frontmatter 模板 + 共享 INDEX）
  - Q12 = subdir_per_layer（`interfaces/{wire, cross_process, in_process, capability}/`，每 sub-chat 仅写自己目录，0 merge 冲突）
  - Q13 = wire_first_2d（T0-T2 仅 4-B-wire 跑 2 天定型模板，user 倒查后再展开）
  
  §7.5 结构：§7.5.1 双线对比 + §7.5.2 grep 兜底脚本 + §7.5.3 5 阶段顺序 + §7.5.4 frontmatter 7 字段强制深入度 + §7.5.5 sub-chat 子目录隔离 + §7.5.6 10 天节奏图 + §7.5.7 sub-chat 入场 prompt 模板 + §7.5.8 4 项新风险（R10-R13）。

- **2026-05-07（amendment — 方法论修正 + 目录修订）**：user 强调"拓扑边界 + App 流程 + 需求 + 能力 优先；接口由这些 derive；骨架代码作参考但不反推"+"产出目录在 `.cursor/memory/` 顶级新开"。重大修订：
  - **§7.5.0 新增方法论原则**：driver 优先级（拓扑边界 → App流程+需求+能力 → 接口 → grep 验证）+ 既有代码角色（参考/升级起点/验证锚点，禁止反推）
  - **§7.5.3 顺序修订**：Q10 amended → req-first 5 阶段（4-B-req → 4-B-cap → 3 个层 sub-chat 并行 → 主 chat 验证 → INDEX 收口）；wire 不再 first
  - **§7.5.4 frontmatter 7 → 9 字段**：新增 `driven_by`（强制 cite 来自 needs/app-flow/capability，禁止从 producer 反推）+ `upgrade_from`（标既有代码升级锚点）；status 新增 `proposed-upgrade` / `proposed-new`
  - **§7.5.5 目录路径修订**：`.cursor/memory/architecture/interfaces/` → `.cursor/memory/interfaces/`（顶级新开，与 architecture / lore / skills 同级）
  - **§7.5.6 节奏修订**：Q13 amended → req-first-2d（不是 wire-first-2d）；T0-T2 仅 4-B-req 跑，user 倒查方法论合规
  - **§7.5.8 新增 R14 R15 风险**：反推代码倾向（high）+ 既有临时实现被锁成正式接口（high）
  - §0.2 决策矩阵 +2 行（方法论原则 + 产出目录）+ Q10 / Q13 标 amended
  - §10 Q10 / Q13 加 amendment 注脚
