---
status: ratified-dictionary
category: concept-dictionary
status_note: "完整词/字段概念介绍 + 设计文档路由指引。≈100 项概念分 7 类（协议字段 / DSG / Brain-Behavior / Unity-Lifecycle / Bus-Resource / 用户主题美术 / 测试守护）。Sonnet 4.6 写代码遇到不熟悉术语必查。"
last_reviewed: 2026-05-07
ai_priority: high
ai_audience: "Sonnet 4.6 + Opus 4.7 ×2 命名一致性审计"
parent_doc: "../app_completion_master_audit_20260507.md"
---

---
status: ratified-dictionary
category: concept-dictionary
status_note: "完整词/字段概念介绍 + 每个概念到设计文档的路由指引。Sonnet 4.6 写代码遇到不熟悉术语必查；Opus 4.7 ×2 命名一致性审计基线。覆盖 ≈100 项概念分 7 类（协议字段 / DSG / Brain-Behavior / Unity-Lifecycle / Bus-Resource / 用户主题美术 / 测试守护）。"
last_reviewed: 2026-05-07
authoritative_for: "项目术语命名 + 文档锚点路由的单一速查表；新增术语必须先入本表再用于代码 / doc"
parent_doc: "../app_completion_master_audit_20260507.md"
related:
  - "../protocol_snapshot_p4.md (协议 SSOT)"
  - "../module_map_p4_snapshot.md (架构 quick-ref)"
  - "../dsg/dsg_decisions_master.md (DSG 决策真源)"
  - "../dsg/dsg_current_state_distilled.md (DSG 全景蒸馏)"
  - "../ar_feature_vision.md (Proprioception / 三合一意识 / Blackboard 4 scope 真源)"
---

# ParrotCarriers — 词/字段概念全集 + 设计文档路由指引

> **本文用途**：项目所有重要术语 / 字段 / 概念的单一速查表。Sonnet 4.6 写代码遇到不懂术语必查；Opus 4.7 ×2 命名一致性审计基线；用户最终整合时同名概念合并。
>
> **每条结构**：`名词 | 一句话定义 | 关键属性 | 真源 doc 锚点 | 代码位置`
>
> **格式约定**：
> - **粗体名词** = 项目内严格命名（不允许同义词）
> - *斜体名词* = 描述性术语（口语 OK）
> - 锚点格式：`<doc> §X` 或 `<file>:<class>`

---

## §1 协议 / Wire 概念（Phase 4 §8 锁定）

### §1.1 EcpEvent 体系

| # | 名词 | 一句话定义 | 关键属性 | 真源 / 代码 |
|:--|:--|:--|:--|:--|
| 1.1.1 | **EcpEvent** | Phase 4 跨语言 wire envelope | 7 强制 + 3 可选字段；reliable DataChannel；topic `parrot.ecp.event` | `protocol_snapshot_p4 §2`；`src/parrot/shared/ecp_event.py` |
| 1.1.2 | **EcpEventType** | 13 项注册 enum（**永不增删除非新 ADR**）| snapshot.captured / sighting.{matched,unmatched} / bbox.{placed,removed} / focus.{anchored,released} / attention.{threshold.crossed,config.echo} / photo.{taken_preview,asset_uploaded} / gesture.recognized / event.rejected.oversize | `protocol_snapshot_p4 §3`；`Phase 4 §8.3` |
| 1.1.3 | **EcpEventSource** | 来源 enum（3 项）| unity / brain / nanobot（reserve）| `protocol_snapshot_p4 §2`；cs_parity 守 |
| 1.1.4 | **8KB 红线** | EcpEvent.payload ≤ 8KB | 超过 → Brain `event_ingest` 拒收 + synthesized event.rejected.oversize | `Phase 4 §8.1 L3` |
| 1.1.5 | **60s dedup 窗口** | EcpEvent 按 event_id 去重；窗口 60s | event_id = `evt_<ts_ms_hex>_<rand_hex>` UUID v7-style | `Phase 4 §8.1 L2` |

### §1.2 EcpCommand / EcpAck 体系

| # | 名词 | 一句话定义 | 关键属性 | 真源 |
|:--|:--|:--|:--|:--|
| 1.2.1 | **EcpCommand** | Brain → Unity 目标驱动命令 | command_id / method / params / expires_at / active_locks_required / **meta dict** | `protocol_snapshot_p4 §6` |
| 1.2.2 | **EcpCommand.meta["model_id"]** | GOSLO Step 1 多模型路由 plumbing | dict 既有字段；不动 wire schema 顶层 | `goslo_model_manifest_protocol_v1 §2.3` |
| 1.2.3 | **EcpAck** | Unity 真实回执（11 字段）| 走 RPC return value（不走 DataChannel）| `protocol_snapshot_p4 §5` |
| 1.2.4 | **ApplyStatus 5 态** | applied / rejected / timeout / no_target / unchanged | wire-locked；LLM 同步话术映射 | `protocol_snapshot_p4 §5` |

### §1.3 EcpState 周期心跳

| # | 名词 | 一句话定义 | 关键属性 | 真源 |
|:--|:--|:--|:--|:--|
| 1.3.1 | **EcpState** | Unity → Brain 周期心跳 | body / head / cognitive / active_locks / active_command_id / last_ack_id | `protocol_snapshot_p4 §4` |
| 1.3.2 | **EcpState 频率** | 事件驱动 + 1Hz 全量心跳 fallback | 任一字段变化即触发；1Hz 周期保 fallback | `Phase 4 §8.1 L1` |
| 1.3.3 | **GAP-1 fix** | Brain 端 attach_ecp_state_ingest 写 BB session/ecp_state | 联机 smoke chat 内修复 | `protocol_snapshot_p4 §4` |

### §1.4 5 LiveKit DataChannel topic

| # | Topic | 用途 | 可靠性 / 频率 | envelope |
|:--|:--|:--|:--|:--|
| 1.4.1 | `parrot.ecp.event` | Phase 4 新增事件 | reliable / 事件驱动 | EcpEvent v1（13 type）|
| 1.4.2 | `parrot.ecp.state` | Unity → Brain 状态心跳 | reliable / 1Hz + 事件驱动 | EcpStateDto v1 |
| 1.4.3 | `parrot.ecp.health` | connection.health.changed | reliable / 事件 | inline envelope（**不迁移**）|
| 1.4.4 | `parrot.ecp.intent_disconnect` | Unity 切后台 / 关 app | reliable / 事件 | inline envelope（**不迁移**）|
| 1.4.5 | `parrot.ecp.tick` | 拖动 / pose（W6-7 BBox/Focus 拖动）| lossy / 30-60Hz | 自由 dict（最小化）|

### §1.5 RefBinding（Phase 4 §8 W6-7 锁）

| # | 名词 | 一句话定义 | 关键属性 | 真源 |
|:--|:--|:--|:--|:--|
| 1.5.1 | **RefBinding** | Unity → L2-B 节点引用绑定 | ref_id（不可变）/ target_kind / target_id / revision | `protocol_snapshot_p4 §8` |
| 1.5.2 | **RefKind** 4 项 | BBOX / FOCUS / PHOTO / SIGHTING | 创建者 / 销毁者各异 | 同上 |
| 1.5.3 | **RefTargetKind** 4 项 | UNRESOLVED / L2B_NODE / OBSIDIAN_NOTE / EXTERNAL | 解析触发条件各异 | 同上 |
| 1.5.4 | **Phase 4 W6-7 verdict** | 所有 RefBinding 当前 = UNRESOLVED；hint_writer 100% no-op（设计意图）| Phase 5+ resolver 联通 | `protocol_snapshot_p4 §8` |

### §1.6 跨语言守护

| # | 名词 | 一句话定义 | 守护内容 |
|:--|:--|:--|:--|
| 1.6.1 | **cs_parity 4/4** | tests/test_ecp_event/test_cs_parity.py 4 项 | C# `EcpEventTypeNames` ↔ Python `EcpEventType` / EcpEventSourceNames / topic 常量 / DTO 文件存在 |
| 1.6.2 | **NodeKind 6 freeze** | tests/test_dsg/test_compatibility_with_phase4.py:test_node_kind_enum_six_values | DSG-INTENT-EVENT-V1 enum 不增删 |
| 1.6.3 | **EdgeKind 8 freeze** | 同上 :test_edge_kind_enum_eight_values | 同上 |
| 1.6.4 | **ObservationSource 7+1 verbatim** | tests/test_dsg/test_compatibility_with_phase4.py + LineB §1.3 | LineB 兼容守护 |
| 1.6.5 | **ParrotAnimation 8 freeze** | shared/parrot_actions.py | wire-locked 双重身份（Brain LLM 词汇表 + Reflex 触发器） |

---

## §2 DSG 概念（耦合子系统）

### §2.1 四层语义架构（脑区类比）

| # | 层 | 类比 | 职责 | 当前状态 |
|:--|:--|:--|:--|:--|
| 2.1.1 | **L0** | 原始事件流 | Redis Stream `parrot.events.log` EventEnvelope | ✅ VERIFIED Sprint 0 |
| 2.1.2 | **L1** | 感官输入 | Blackboard 短期共享 | ✅ VERIFIED |
| 2.1.3 | **L1.5** | 视觉皮层 | 多源 Node 出口管理池（升级方向）| ✅ DSG-POOL-V1 |
| 2.1.4 | **L2-A** | 背侧通路 (Where) | 空间拓扑 Object→Surface→Zone | PLANNED P3 |
| 2.1.5 | **L2-B** | 腹侧通路 (What) | 语义注意力 + 关联 + IntentEvent | ✅ DSG-INTENT-EVENT-V1 |
| 2.1.6 | **L3** | 长期记忆 | Graphiti + FalkorDB | ✅ IMPLEMENTED |

### §2.2 Scene / Location / IntentEvent 三概念区分

| # | 名词 | 一句话定义 | 关键不是 | 真源 |
|:--|:--|:--|:--|:--|
| 2.2.1 | **SceneType** | preset enum：DESKTOP_WEBCAM / AR_HANDHELD / HOME_INDOOR / OUTDOOR / LIBRARY / KITCHEN / OTHER | ≠ Location（具体位置）/ ≠ IntentEvent（认知边界）| `dsg_protocol_scene_snapshot_v1 §1.1` |
| 2.2.2 | **LocationTag** | scalar tag：study / kitchen / living_room / desk | ≠ SceneType / ≠ Bucket / ≠ Compartment | 同上 §0 |
| 2.2.3 | **IntentEvent** | GOSLO Intent focus（NodeKind.EVENT 镜像）| ≠ SceneType（物理切换不必等于认知切换）| `dsg_protocol_intent_event_boundary_v1` |
| 2.2.4 | **SceneProfile** | dataclass：scene_type / dsg_mode / video_tier_hint / cv_flow_params / preserved_bucket_kinds / fresh_bucket_kinds / priority_overrides / location_default | scene_type → 完整切换契约 | `dsg_protocol_scene_snapshot_v1 §1.1` |
| 2.2.5 | **SceneRegistry** | L1.5 内 Scene 注册表 + 当前 Scene 管理 + switch() | singleton；DESKTOP baseline；2 baseline 待升 | `src/parrot/dsg/l1_5/scene_snapshot.py` |
| 2.2.6 | **SceneSwitchOutcome** | switch() 返回的 freeze + clear 桶清单 + 通知信号 | — | 同上 |

### §2.3 Bucket（L1.5 池）

| # | 名词 | 一句话定义 | TTL / max_nodes / scene 切换 |
|:--|:--|:--|:--|
| 2.3.1 | **OBSIDIAN_REFERENCE_REINFORCE** | Obsidian 加强 Ref（节点 meta，不是节点本身）| 永久 / None / freeze |
| 2.3.2 | **OBSIDIAN_SETTING_DAILY** | 家具 / 公用场景设定节点 | 永久 / None / freeze |
| 2.3.3 | **OBSIDIAN_SETTING_ROLEPLAY** | Roleplay 模式设定节点 | 永久 / None / freeze（仅 roleplay 模式开时）|
| 2.3.4 | **IDENTIFY_OBJECT_RESULT** | identify_object 命中节点 | 永久 / None / freeze |
| 2.3.5 | **GEMINI_ORAL_MENTION** | LLM 助手口头提及（含 LineA / LineB）| TTL（fresh）/ 限量 / clear |
| 2.3.6 | **AUTONOMOUS_CURIOSITY** | GOSLO 主动好奇 | 300s TTL / 限量 / clear |
| 2.3.7 | **GOOGLE_CALENDAR**（dsg_protocol_scene_snapshot 提及）| Google 日程一键导入 | 一键删除 / TTL / 切 Scene clear |

### §2.4 SemanticNode lifecycle

| # | 名词 | 一句话定义 | 真源 |
|:--|:--|:--|:--|
| 2.4.1 | **SemanticNode** | L2-B 节点 Pydantic | `l2b_types.py:SemanticNode` |
| 2.4.2 | **NodeKind 6 项** | OBJECT / SURFACE / ZONE / PERSON / EVENT / PHOTO | wire-locked Phase 4 §8 L1 |
| 2.4.3 | **EdgeKind 8 项** | LOCATED_AT / PART_OF / BELONGS_TO / MENTIONED_IN / OCCURRED_IN / HAS_PHOTO / CAPTURED_VIA / CANDIDATE_SUBJECT | wire-locked |
| 2.4.4 | **ConfirmationStatus 5 态** | EXPECTED / TENTATIVE / UNCERTAIN / CONFIRMED / GHOST | enum 值 |
| 2.4.5 | **Salience 5 态** | ALERT / FOREGROUND / ACTIVE / BACKGROUND / PERIPHERAL | enum 值 |
| 2.4.6 | **EpisodeMarker** | Episode 单元 | `l2b_types.py` |
| 2.4.7 | **evidence_score** | [0.0, 1.0] | repeat-seen +0.25；Graphiti enrich +0.15；≥0.6 自动升 CONFIRMED |
| 2.4.8 | **attention** | [0.0, 1.0] | 默认 0.6（CONFIRMED）/ 0.35（其他）；Phase 4 attention 模块**不直写** |
| 2.4.9 | **novelty / habituation_count** | 衰减字段 / 累加计数 | 当前**无 writer**（衰减留 P3）|
| 2.4.10 | **last_attended / last_seen_this_session / interaction_count** | touch() 维护 | runtime 字段 |
| 2.4.11 | **provenance_stream_id** | L0 EventEnvelope id | Sprint 0 S0.B 引入 |
| 2.4.12 | **time_span / reference_image_path / last_sighting_path** | EVENT 节点 / snapshot path / rolling sighting | 各 Source 不同时机赋值 |
| 2.4.13 | **source / source_meta** | ObservationSource.value / 自由扩展槽 | ADR-L1.5-001 §2.1 / §2.2 |
| 2.4.14 | **bucket_id / scene_type / location_tag / event_id** | informational tag（不动 enum）| DSG Chat 2 加 |

### §2.5 ObservationSource 7+1

| # | Source | priority | 用途 |
|:--|:--|:--|:--|
| 2.5.1 | **USER_TAG_OBSIDIAN** | 100 | Obsidian SSOT 双向链（含 3 子类 meta.profile） |
| 2.5.2 | **USER_EXPLICIT** | 95 | 用户口头/UI 主动声明 |
| 2.5.3 | **IDENTIFY_OBJECT** | 80 | Brain tool 命中结果 |
| 2.5.4 | **GOSLO_AUTONOMOUS**（第 8 项）| 70 | GOSLO 主动好奇（DSG Chat 2 加） |
| 2.5.5 | **CV_A10** | 60 | A10 视觉管线（Phase 5+ 占位）|
| 2.5.6 | **CV_SENTINEL** | 40 | 笔记本 Sentinel YOLO（Phase 5+ 占位）|
| 2.5.7 | **GEMINI_ORAL** | 30 | LineA / LineB LLM 口头提及 |
| 2.5.8 | **MOCK** | 10 | 测试桩 |

### §2.6 Obsidian 3 子类（**重要新约束**，dsg_decisions_master §3.2）

| # | 子类 | 用途 | 是否进 L2-B 节点 | meta.profile |
|:--|:--|:--|:--|:--|
| 2.6.1 | **Obsidian-Ref-加强** | 加强既有节点的 Ref | ❌ 仅作为他人节点 meta.obsidian_uuid | "ref" |
| 2.6.2 | **Obsidian-设定-日常** | 家具 / 公用场景 | ✅ 是节点本身 | "daily" |
| 2.6.3 | **Obsidian-设定-Roleplay** | Roleplay 自定义 | ✅ 是节点本身（roleplay 模式时）| "roleplay" |

### §2.7 IntentWorkspace / 9 StagedRefKind

| # | 名词 | 一句话定义 | 真源 |
|:--|:--|:--|:--|
| 2.7.1 | **IntentWorkspace** | Brain 大文件常驻容器 | `brain/intent_workspace.py` |
| 2.7.2 | **StagedRef** | IntentWorkspace 内单条引用 | `brain_protocol_intent_workspace_v1` |
| 2.7.3 | **9 StagedRefKind** | PLAN_DRAFT / PLAN_AWAITING_USER / INTENT_THREAD / IDENTIFY_OBJECT_PENDING / MEMORY_RECALL_THREAD / BBOX_REFERENCE / FOCUS_REFERENCE / PHOTO_REFERENCE / CUSTOM | `protocol_snapshot_p4 §19` |
| 2.7.4 | **InMemoryBackend / DiskBackend** | 2 种 Backend strategy | DiskBackend.recover() = TODO(Chat4-disk-recover) |

### §2.8 Plan-and-Execute

| # | 名词 | 一句话定义 |
|:--|:--|:--|
| 2.8.1 | **Plan** | Brain 内 8 状态机：DRAFT → AWAITING_USER_CONFIRMATION → APPROVED / REJECTED / REVISED → EXECUTING → DONE / FAILED |
| 2.8.2 | **NanobotTask** | Plan 一个 step 派给 nanobot 的派发实例（plan_id × step_id 关联）|
| 2.8.3 | **PlanRegistry** | 主存 IntentWorkspace + L2-B 镜像（reuse `NodeKind.EVENT`，不动 enum）|
| 2.8.4 | **revise** | 创建新 plan + supersedes 旧 |

### §2.9 Triggers V2 + 5 路上行

| # | 名词 | 一句话定义 |
|:--|:--|:--|
| 2.9.1 | **TriggerOutcome** | 9 个 Trigger 的统一输出 |
| 2.9.2 | **5 路上行通道** | commit_observations / bucket_ops / staged_refs / archive_request / plan_request |
| 2.9.3 | **2 legacy 通道** | dispatch_to_nanobot / notify_gemini |
| 2.9.4 | **9 Triggers** | calendar / message / scene_context / ssot_enrichment（4 legacy）+ scene_switch / intent_event_boundary / roleplay_mode / goslo_curiosity / idle_archive（5 new）|
| 2.9.5 | **alias 兼容** | TriggerResult = TriggerOutcome（既有 4 触发器零改动）|

### §2.10 ConversationBoundary / Archive 3-Phase

| # | 名词 | 一句话定义 |
|:--|:--|:--|
| 2.10.1 | **ConversationBoundary** | 多信号 OR（话题切换 / silence > 阈值 / scene_switch / mode_switch / explicit user） |
| 2.10.2 | **Episode** | Conversation 时段单位 |
| 2.10.3 | **Archive 3-Phase** | hot 内存 → cold 硬盘序列化 → nanobot 闲时归档（**新约束**）|
| 2.10.4 | **6 jsonl schema** | conversation 归档分 6 类 jsonl | `dsg_protocol_archive_v1` |

### §2.11 Compartment view / Subgraph fold

| # | 名词 | 一句话定义 |
|:--|:--|:--|
| 2.11.1 | **Compartment view** | L2-B 单图 + 5 lazy view（view_by_bucket / event / scene / location / kind）；不分图 |
| 2.11.2 | **FoldStrategy** | RustworkX 子图折叠 strategy |
| 2.11.3 | **NoOpFoldStrategy** | baseline（不真折叠）|
| 2.11.4 | **跳数硬上界 4 跳** | dsg-rustworkx-master §3.5 + AGCN 实证 |

### §2.12 Strategy registries

| # | 名词 | 一句话定义 |
|:--|:--|:--|
| 2.12.1 | **PoolAdmissionPolicy** | DesktopPolicy(theta_admit=0.3) baseline |
| 2.12.2 | **AttentionDecayPolicy** | SimpleDecay baseline |
| 2.12.3 | **AttentionMechanism** | BoundedBfsActivation baseline / SpreadingActivationPlaceholder（experimental）|
| 2.12.4 | **register_source_meta_factory** | 新 source 注册 meta factory |
| 2.12.5 | **register_phase4_observers** | Phase 4 observer 注册 helper |

### §2.13 防爆炸 3 层门控

| # | 层 | 当前规则 | 设计责任 |
|:--|:--|:--|:--|
| 2.13.1 | **A10 端 CV Flow** | IoU + CLIP sim + persistence threshold + obj_min_detections=3 | A10 chat（P3+）|
| 2.13.2 | **L1.5 入池门** | 30s repeat-seen → CONFIRMED；缺投票 / 注意力 / 事件相关性 / 跳数 | Chat 2（已部分） |
| 2.13.3 | **L2-B 入图门** | _find_existing 顺序匹配；缺不可能事件检测 / 同类第二实例确认 | P3 |

---

## §3 Brain / Behavior 概念

### §3.1 三层调度 / 三合一意识

| # | 三视图 | 一句话定义 |
|:--|:--|:--|
| 3.1.1 | **Reflex / Intent / Task** | parrot_behavior_rules §0.1 三层调度 |
| 3.1.2 | **Subconscious / Autonomous Action / Conscious Report** | ar_feature_vision §3.5 三层意识分发 |
| 3.1.3 | **System1 / System1+部分System2 / System2+反思** | NVIDIA GR00T N1.6 + DPT-Agent + CTHA 工业范式 |
| 3.1.4 | **三合一统一视图** | ar_feature_vision §3.5 钉死：三视图是同一架构的三个侧面 |

### §3.2 Persona vs Mode vs Model（4 类块菜单画布前置）

| # | 名词 | 一句话定义 | 当前状态 |
|:--|:--|:--|:--|
| 3.2.1 | **Persona**（设定块）| LLM 嗓音 / 人设；NEED-P2.5-A 外置 | brain/soul.py 内联硬编码（待外置）|
| 3.2.2 | **Mode**（模式块）| BehaviorMode 5 flags + ROLEPLAY flag（NEED-P3-MODE-ROLEPLAY）| ✅ set_mode tool + mode_watcher |
| 3.2.3 | **Model**（模型块）| Unity 视觉模型 + capability 集合 | ✅ ModelManifest + ModelDriver + ParrotRegistry |
| 3.2.4 | **Scene**（场景块）| SceneType + SceneProfile | ✅ SceneRegistry（DESKTOP only；2 baseline 待升）|
| 3.2.5 | **预设 Preset** | 4 active ID 命名快照（model + persona + mode + scene） | ❌ NEED-P3-C |

### §3.3 Observer vs Attention 模块（**职责分离**）

| # | 模块 | 能做 | 不能做 |
|:--|:--|:--|:--|
| 3.3.1 | **Observer**（观察者）| 检测事件 + 决定何时打点 / 快照 | 不写 L2-B 节点 attention；不做注意力权重计算 |
| 3.3.2 | **Attention**（注意力）| 收集数据触发触发器（"判断"） | 不抓帧；不写 Graphiti；不做事件检测 |
| 3.3.3 | **Phase 4 范围** | Observer + 临时阈值器（FocusBboxThreshold）；非 L3 完整模块 | 完整 L3 留 P3 |

### §3.4 selection-C / Echo / Proprioception

| # | 名词 | 一句话定义 | 真源 |
|:--|:--|:--|:--|
| 3.4.1 | **selection-C** | LLM 注入主路径：execute 类 tool 在 execute 前检查 BB body / head / cognitive 三态附 reason | Phase 4 §8 L10 |
| 3.4.2 | **Echo 全链路** | Unity ScriptableObject 阈值 → publish `attention.config.echo` → Brain 写 BB `global/attention_thresholds` → FocusBboxThreshold 读 | Phase 4 §8 L9 + F-05 |
| 3.4.3 | **Proprioception 4 级**（视觉自我感知）| active / degraded / paused / blocked | ar_feature_vision §3.3 |
| 3.4.4 | **Soul 8 条强制话术** | 4 级各 2 条话术约束（不允许 LLM 自由发挥）| 同上 |
| 3.4.5 | **三层视觉门控** | Unity 产地 / LiveKit 传输 / Python 消费端 | ar_feature_vision §3.1 |

### §3.5 Blackboard 4 scope（**重要架构**）

| # | Scope | 持久度 | 写者 | 例子 |
|:--|:--|:--|:--|:--|
| 3.5.1 | **Global** | 跨 session | Graphiti / config 加载 / RPC 显式 | active_persona_id / active_model_id / active_scene_id / behavior_mode / attention_thresholds（Echo）|
| 3.5.2 | **Session** | 本次 LiveKit room | session handler | room_id / unity_identity / scene / **visual_state** / ecp_state / connection_health / audio_route_policy |
| 3.5.3 | **Tick** | 每次 telemetry / RPC ack | telemetry receiver / RPC bridge | body_state / head_state / cognitive_state / ar_tracking_state / last_rpc_ack |
| 3.5.4 | **Transient** | 秒级 consume-then-expire | observers | just_captured_photo / hand_gesture / current_attention_hint / last_sighting_event |

### §3.6 LineA vs LineB pipeline-agnostic

| # | 名词 | 一句话定义 |
|:--|:--|:--|
| 3.6.1 | **LineA** | Gemini Realtime（默认）|
| 3.6.2 | **LineB** | STT-LLM-TTS（google.STT + google.LLM + google.TTS + silero.VAD）|
| 3.6.3 | **PARROT_LLM_PIPELINE** | env-gate 切换；line_a / line_b（无 silent fallback）|
| 3.6.4 | **transcript_extractor** | pipeline-agnostic listener bridge（旧名 alias 保留）|
| 3.6.5 | **structural PASS** | Phase 4 §8 13 锁 0 漂移 + cs_parity 4/4 + ObservationSource 7 verbatim |

### §3.7 BehaviorMode 5 flags

| # | Flag | 用途 |
|:--|:--|:--|
| 3.7.1 | **BASE** | 基线 |
| 3.7.2 | **COMPANION** | 陪伴模式 |
| 3.7.3 | **BUTLER** | 管家模式 |
| 3.7.4 | **RESEARCHER** | 研究员模式 |
| 3.7.5 | **PLAYFUL** | 顽皮模式 |
| 3.7.6 | **FULL** | 全开 |

---

## §4 Unity / Lifecycle 概念

### §4.1 ParrotApp 命名空间（GOSLO 模块化）

| # | 名词 | 一句话定义 | 真源 |
|:--|:--|:--|:--|
| 4.1.1 | **IParrotController** | Capability 路由契约接口 | `Parrot/IParrotController.cs` |
| 4.1.2 | **ModelDriver** | manifest 加载 + 反射实例化 + 自动缩放 + 注册 | `Parrot/ModelDriver.cs` |
| 4.1.3 | **ParrotRegistry** | scene-singleton P1 stub（last-registered active；P3 多 actor 占位）| `Parrot/ParrotRegistry.cs` |
| 4.1.4 | **GosloLegacyController** | IParrotController 实现（包装 AnimationDriver） | `Parrot/GosloLegacyController.cs` |
| 4.1.5 | **fallback 链** | IParrotController → AnimationDriver → Animator → dev pulse；旧场景 0 漂移 | `goslo_modularization_completion §3.2` |

### §4.2 ModelManifest

| # | 字段 | 一句话定义 |
|:--|:--|:--|
| 4.2.1 | **schema_version / manifest_version** | 1 / 1 |
| 4.2.2 | **model_id** | 全场景唯一（如 GOSLO_default / qfufu_v1）|
| 4.2.3 | **asset_path** | Unity Resources 路径 |
| 4.2.4 | **controller_type** | MonoBehaviour 全限定类名 |
| 4.2.5 | **forward_axis / up_axis** | +Z / +Y |
| 4.2.6 | **unit_meters / default_pet_height_m / auto_scale_to_pet_height** | 1.0 / 0.20 / true |
| 4.2.7 | **capabilities** | tuple[Capability, ...] |
| 4.2.8 | **declared_capability_ids** | frozenset 派生属性 |
| 4.2.9 | **parrot_reflex_enabled** | 任意 reserved id 命中 → True | 派生属性 |

### §4.3 AppLifecycleState 11 态 FSM

| # | 状态 | 一句话定义 |
|:--|:--|:--|
| 4.3.1 | Unbooted | 未启动 |
| 4.3.2 | Booting | 启动中 |
| 4.3.3 | Booted | 已启动 |
| 4.3.4 | ConnectingLiveKit | 连 LiveKit 中 |
| 4.3.5 | AwaitingPermissions | 等权限 |
| 4.3.6 | SessionWarming | 房间预热 |
| 4.3.7 | SessionReady | 房间就绪 |
| 4.3.8 | SessionLive | 房间运行中 |
| 4.3.9 | SessionPaused | 暂停（OnApplicationPause）|
| 4.3.10 | SessionRecovering | 重连中 |
| 4.3.11 | SessionShuttingDown | 关闭中 |

### §4.4 ConnectionHealthState

| # | 名词 | 一句话定义 |
|:--|:--|:--|
| 4.4.1 | **overall** | healthy / degraded / lost / recovering（4 态聚合）|
| 4.4.2 | **聚合源** | audio + video + brain_presence + ar_tracking |

### §4.5 VideoTier × DsgMode 两轴正交

| # | 轴 | 值 |
|:--|:--|:--|
| 4.5.1 | **VideoTier** | VIDEO_OFF / VIDEO_GEMINI_ONLY / VIDEO_FULL / VIDEO_BURST |
| 4.5.2 | **DsgMode** | DSG_TEXT_ONLY / DSG_GEMINI_VISION / DSG_FULL / DSG_SENTINEL_AUX |
| 4.5.3 | **正交** | 两轴独立切换；A10 关闭时 DSG 仍能部分工作 |

### §4.6 cool-down / hold_seconds

| # | 名词 | 一句话定义 |
|:--|:--|:--|
| 4.6.1 | **hold_seconds=300** | set_video_tier 用户主动切档保留时间（D1 Sprint3）|
| 4.6.2 | **PARROT_OVERRIDE_HOLD_SECONDS** | env 可覆盖 |
| 4.6.3 | **TRACK_REBUILDING reason** | 跳过 Supervisor 降档计时（D4 Sprint3）|

### §4.7 ECP 解耦边界

| # | 名词 | 一句话定义 |
|:--|:--|:--|
| 4.7.1 | **ECP** | Brain ↔ Unity 目标驱动 + 状态同步契约层 |
| 4.7.2 | **ECP 不是** | Scheduler / BT / BT 森林的替代 |
| 4.7.3 | **3 层 ECP 协议** | EcpCommand 下行 + EcpAck 同步回执 + EcpEvent 异步事件 + EcpState 周期心跳 |

---

## §5 Bus / Resource 概念

### §5.1 三层 Bus 协议

| # | 层 | 技术 | 延迟 | 负载 |
|:--|:--|:--|:--|:--|
| 5.1.1 | **L1 实时** | LiveKit Room (WebRTC) | <50ms | 音视频 / RPC / DataChannel（5 topic）|
| 5.1.2 | **L2 状态** | Redis | <5ms | BB / Pub-Sub / Stream / HASH |
| 5.1.3 | **L3 知识** | Graphiti + FalkorDB（替代 Neo4j）| <500ms | 5 group_id 分区 |

### §5.2 服务器双节点

| # | 节点 | 规格 | 部署组件 |
|:--|:--|:--|:--|
| 5.2.1 | **Castle 常驻** | Tokyo ecs.g9i.large 2C8G | LiveKit Server / Redis / FalkorDB / Brain Agent / Scheduler / Nanobot Worker |
| 5.2.2 | **Mecha 按需** | Tokyo gn7i A10 抢占式 | SAM2 + DINOv2 / DSG L1/L2-A |
| 5.2.3 | **同 VPC 内网** | < 0.1ms 延迟 | East-West |

### §5.3 Redis namespaces

| # | 类型 | 名 |
|:--|:--|:--|
| 5.3.1 | **Pub/Sub** | parrot.events.firehose / parrot.brain.* / parrot.dsg.* / parrot.scheduler.* / parrot.nanobot.results / parrot.external.* |
| 5.3.2 | **Stream** | parrot.events.log（L0 内部）/ parrot.scheduler.task_queue（dispatch_task）|
| 5.3.3 | **HASH** | parrot:resource_locks / **parrot:nanobot_heartbeat**（NEED-P2.5）/ parrot:bb |

### §5.4 Graphiti 5 group_id 分区

| # | group_id | 用途 |
|:--|:--|:--|
| 5.4.1 | **episodic** | 对话事件（archive_to_graphiti 主目标）|
| 5.4.2 | **objects** | 物体节点（identify_object 命中后）|
| 5.4.3 | **personality** | GOSLO 人设记忆（与 NEED-P2.5-A 联动）|
| 5.4.4 | **vocabulary** | 用户 / GOSLO 共享词汇表 |
| 5.4.5 | **nanobot_research** | Nanobot research tool 写入 |
| 5.4.6（远期）| **roleplay 自定义区** | Roleplay 子类隔离（dsg_decisions_master §3.2）|

### §5.5 HTTP endpoints

| # | endpoint | 方法 | 用途 |
|:--|:--|:--|:--|
| 5.5.1 | `http://<brain>:7889/upload/photo/{photo_id}` | POST | Photo asset 上传 |
| 5.5.2 | `http://<brain>:<port>/token_mint` | POST | LiveKit JWT 颁发 |

---

## §6 用户主题 / 美术概念

### §6.1 主题 / 角色设定

| # | 名词 | 一句话定义 | 来源 |
|:--|:--|:--|:--|
| 6.1.1 | **大小姐宅邸**（默认主题）| 维多利亚 / 蕾丝 / 暖色调 | lore §2026-04-27 |
| 6.1.2 | **海盗主题**（P3 换肤）| 深蓝 / 木质 / 黄铜 / 海图 | 同上 |
| 6.1.3 | **GOSLO** | 鹦鹉大小姐（默认）/ 大副（海盗）| 同上 |
| 6.1.4 | **Nanobot** | 女仆（默认）/ 水手（海盗）| 同上 |
| 6.1.5 | **User** | （默认）/ 船长（海盗）| 同上 |
| 6.1.6 | **大小姐宅邸 Live** | GOSLO 在 AR 房间日常对话 | 同上 |
| 6.1.7 | **大小姐宅邸 Chat** | GOSLO 通过 Telegram bot 对话 | scene.md |

### §6.2 风格基线

| # | 元素 | 默认（大小姐宅邸）| 海盗换肤（P3）|
|:--|:--|:--|:--|
| 6.2.1 | **2D 像素 Meta UI** | 不与真实世界互动；Stardew Valley 风 | 同 |
| 6.2.2 | **HUD 板** | 像素羊皮纸（白底暖金边）| 老海图 / 卷边 / 黄铜钉 |
| 6.2.3 | **放大镜** | 圆形玻璃 | 海盗望远镜 |
| 6.2.4 | **AR 视野滤镜** | 无 | 半边模糊黑色（眼罩）/ 脏镜片 |
| 6.2.5 | **角色 emoji** | GOSLO + 猫娘 | GOSLO + 戴眼罩 + 水手 |
| 6.2.6 | **纸条** | 现代信封 | 卷起羊皮纸 + 火漆封 |
| 6.2.7 | **猫爪伸出递交** | 柔粉色猫爪 | 海盗手套粗糙手 |

### §6.3 灵感参考

| # | 来源 | 用途 |
|:--|:--|:--|
| 6.3.1 | **Stardew Valley** | 启动页菜单 / 像素角色风 |
| 6.3.2 | **Paper Please** | 2D 工作区批改风 |
| 6.3.3 | **Last Report** | 森林管理员批改报告（lore 钦定 — user 喜欢这个）|

### §6.4 Roleplay vs 主题换肤区分

| # | 概念 | 是什么 | 不是什么 |
|:--|:--|:--|:--|
| 6.4.1 | **Roleplay** | Mode 块的一个 flag；Persona / Obsidian-设定 子类切换 | ≠ 视觉换肤 |
| 6.4.2 | **主题换肤**（海盗）| ScriptableObject swap；纯视觉 | ≠ Persona 切换 |
| 6.4.3 | **联动** | Roleplay 模式开 = Mode 块 + Persona 子类（lore + dsg_decisions_master §3.2） + 海盗换肤 SO swap | 一键切换 |

---

## §7 设计文档路由指引

> 概念 → 真源 doc 锚点的精确映射。Sonnet 4.6 / Opus 4.7 找命名 / 决策依据时按本表回查。

### §7.1 协议 / Wire

| 概念 | 真源 doc | 章节 | 代码 |
|:--|:--|:--|:--|
| EcpEvent / EcpCommand / EcpAck / EcpState 全字段 | `protocol_snapshot_p4.md` | §2-§6 | `src/parrot/shared/{ecp,ecp_event}.py` |
| 13 EcpEventType 注册表 | 同上 | §3 / §8.3 Phase 4 启动集合 | `shared/ecp_event.py:EcpEventType` |
| 5 LiveKit DataChannel topic | `protocol_snapshot_p4.md` | §1 | wire-locked |
| 8KB / 60s dedup / oversize | `sprint4_phase4_entry §8.1 L2-L3` | — | `brain/event_ingest.py` |
| Phase 4 §8 13 决策锁 | `sprint4_phase4_entry_20260430.md` | §8 | — |
| RefBinding 4 RefKind / 4 RefTargetKind | `protocol_snapshot_p4.md` | §8 | `shared/ref_binding.py` |
| GOSLO Manifest schema | `goslo_model_manifest_protocol_v1.md` | §3 | `shared/model_manifest.py` |
| ECP V2 设计哲学 | `sprint4_protocol_v2_ecp.md` | §1-§5 | — |

### §7.2 DSG

| 概念 | 真源 doc | 章节 |
|:--|:--|:--|
| DSG 全景 | `dsg/dsg_current_state_distilled.md` | 全文 |
| DSG 决策总表 | `dsg/dsg_decisions_master.md` | 全文 |
| DSG 工作区入口 | `dsg/workspace_index.md` | 全文 |
| L1.5 池协议 | `dsg/dsg_protocol_pool_v1_20260506.md` | 全文 |
| Trigger V2 5 路上行 | `dsg/dsg_protocol_trigger_v2_20260506.md` | §2 |
| IntentEvent 边界 | `dsg/dsg_protocol_intent_event_boundary_v1_20260506.md` | 全文 |
| 3-Phase 归档 | `dsg/dsg_protocol_archive_v1_20260506.md` | §1 |
| Scene snapshot | `dsg/dsg_protocol_scene_snapshot_v1_20260506.md` | 全文 |
| ADR-L1.5-001 | `adr_l1_5_source_dispatch_extension_space_20260504.md` | §2 / §4 |
| 防爆炸 3 层门控 | `dsg/dsg_current_state_distilled.md` | §11 |
| 工作记忆 3 阶段归档 | `dsg/dsg_current_state_distilled.md` | §12 |
| Obsidian 3 子类 | `dsg/dsg_decisions_master.md` | §3.2 |
| 注意力双开放路径 | `dsg/dsg_decisions_master.md` | §4 |

### §7.3 Brain / Behavior

| 概念 | 真源 doc | 章节 |
|:--|:--|:--|
| Reflex / Intent / Task 三层 | `parrot_behavior_rules.md` | §0.1 |
| Tool 体感红线 | `parrot_behavior_rules.md` | §0.3 / §4.3 |
| Observer / Attention 边界 | `parrot_behavior_rules.md` | §3.7 |
| 三合一意识统一视图 | `ar_feature_vision.md` | §3.5 / §3.6 |
| 4 级视觉自我感知 | `ar_feature_vision.md` | §3.3 |
| Blackboard 4 scope | `ar_feature_vision.md` | §3.6 |
| 三层视觉门控 | `ar_feature_vision.md` | §3.1 |
| 2 Scene baseline | `ar_feature_vision.md` | §3.4 |
| BrainBody-LLM / GR00T / CTHA 借鉴 | `ar_feature_vision.md` | §3.5 表 |

### §7.4 Unity / Lifecycle

| 概念 | 真源 / Skill | 章节 |
|:--|:--|:--|
| AppLifecycleState 11 态 FSM | `livekit-unity-lifecycle/IMPL_REF.md` | §1-§3 |
| OnApplicationPause | 同上 | §2 |
| ARCore 黑帧 | 同上 | §5 |
| setVideoTier 副作用 | 同上 | §6 |
| ConnectionHealthState | 同上 | §4 |
| ParrotApp 三层架构 | `goslo_model_manifest_protocol_v1.md` | §2 |
| LiveKit Unity SDK | `client-sdk-unity/SKILL.md` | 全文 |
| 视频流多采样 | `livekit-unity-video-publish/SKILL.md` | §三 / §四 |

### §7.5 Bus / Resource

| 概念 | 真源 |
|:--|:--|
| 三层 Bus 协议 | `bus_v4.md` |
| Castle / Mecha 拓扑 | `module_map_p4_snapshot.md` §1 |
| Redis namespaces | `protocol_snapshot_p4.md` §15 |
| Graphiti 5 group_id | `protocol_snapshot_p4.md` §16 |
| Token Mint / photo_upload_server | `protocol_snapshot_p4.md` §14 |

### §7.6 用户主题 / 美术

| 概念 | 真源 |
|:--|:--|
| 大小姐 / 海盗 / 角色设定 | `lore/ideas.md` 2026-04-27 |
| 像素 UI 资产清单 | `app_completion_master_audit_20260507.md` §6 |
| 完整菜单设计 | `Interface/menu_design_complete_20260507.md` |
| AR App Flow / UI baseline | `ar_app_flow_ui_design.md` |

### §7.7 工作区入口

| 工作区 | 入口 |
|:--|:--|
| 全局 | `INDEX.md` |
| 当前阶段 | `active_context.md` |
| AR 工作区 | `ar_workspace_index.md` |
| DSG 工作区 | `dsg/workspace_index.md` |
| Interface 工作区（新）| `Interface/interface_design_supplement_20260507.md §4.1` 段落 |

---

## §8 grep 速查

```bash
# 查命名一致性
rg "EcpEventType\." src/    # Python 端
rg "EcpEventTypeNames\." unity/  # C# 端

# 查 wire 锁
rg "Phase 4 §8" .cursor/memory/architecture/

# 查未注册的概念（疑似漂移）
rg "TODO\(.*\)" src/ | rg -v "Chat4-|P3-"   # 非标准 TODO

# 查 NodeKind / EdgeKind / ObservationSource 用法
rg "NodeKind\." src/parrot/dsg/
rg "EdgeKind\." src/parrot/dsg/
rg "ObservationSource\." src/parrot/dsg/

# Skill 大全
ls -la .cursor/skills/
```

---

## §9 维护规则

1. **新增术语**：必须先入本表 §1-§6 对应小节 + §7 路由指引；再在源码用
2. **重命名术语**：必须同步更新本表 + 跨语言守护测试 + cs_parity 4/4
3. **概念合并**：如发现两个名词描述同一事物（如 ECP / Protocol V2 早期混用），在本表 §10 标 `synonym` 并选定 canonical 名
4. **跨语言一致**：Python ↔ C# wire 名字必须 1:1（cs_parity 守）

---

## §10 同义词 / 历史命名（追溯）

| canonical 名 | 同义词 / 历史命名 | 哪里出现 |
|:--|:--|:--|
| **EcpEvent** | EventEnvelope（Phase 4 wire；非 Sprint 0 L0 EventEnvelope！）| `Phase 4 §8.0` 命名冲突解决 |
| **L0 EventEnvelope**（Sprint 0 Redis Stream 内部）| EventEnvelope | `parrot.shared.event_log` |
| **Scheduler** | ~~Dispatcher~~（废弃）| `requirements §三` |
| **Brain Agent** | ~~Brain~~（口语 OK；文档全称）| 同上 |
| **Nanobot Worker** | ~~猫娘女仆~~（口语 OK）| 同上 |
| **transcript_extractor** | gemini_transcript_extractor（旧名 alias 保留）| LineB §1.2 |

---

## §11 变更日志

- **2026-05-07**：本文创建。整合 protocol_snapshot_p4 / module_map_p4_snapshot / dsg_decisions_master / dsg_current_state_distilled / ar_feature_vision / goslo_model_manifest_protocol_v1 / lineb_implementation_completion / parrot_behavior_rules / lore/ideas 全源；≈100 概念分 7 类 + 设计文档路由指引 + grep 速查 + 同义词追溯。