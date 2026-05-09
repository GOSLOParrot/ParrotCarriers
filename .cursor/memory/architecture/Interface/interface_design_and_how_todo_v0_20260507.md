---
status: superseded
category: interface-design-historical
superseded_by: "INDEX.md（2026-05-09 路由整理：本文路线已被本目录 INDEX.md 的核心/业务二分骨架取代；12 场景清单仍可参考但不再当接口设计产物）"
status_note: "接口设计 v0 — 12 场景 + 4 横切关注点的接口签名 + How TODO + TODO 注释草稿。原产出路线"自下而上 12 场景穷举"导致仓库被复印半份，已在 2026-05-09 整理时改用核心/业务二分骨架（见 INDEX.md §0 失败教训）。本文不删，留作场景清单参考。"
last_reviewed: 2026-05-07
superseded_at: 2026-05-09
ai_priority: low
ai_audience: "考古追溯 + 业务 chat 启动时对照"我这条业务在 v0 第几场景""
parent_doc: "INDEX.md"
related:
  - "INDEX.md (本目录核心/业务二分骨架，2026-05-09 新建)"
  - "interface_design_supplement_20260507.md (v0 补丁，同样 superseded)"
  - "concept_dictionary_20260507.md (术语查询)"
  - "legacy_issues_split_20260507.md (遗留问题)"
  - "menu_design_complete_20260507.md (菜单设计)"
---

---
status: draft / interface-design-howtodo
category: interface-design
status_note: "喂给 Sonnet 4.6 写代码 + Opus 4.7 调研补漏的接口设计 + How-TODO 列表 v0。基于总 chat 8 场景对账（app_completion_master_audit_20260507.md），加 4 增补场景 + 4 横切关注点。每条接口含：已有能力索引 / 缺口 / 函数签名草稿 / 算法 + Skill 决策 / TODO 注释草稿。本文不实施，只设计 + 索引。"
last_reviewed: 2026-05-07
ai_priority: high
ai_audience: "Sonnet 4.6 实施 chat（按本表 TODO + 接口签名抄码）+ Opus 4.7 调研 chat（补漏 / 校准 / 修订）"
parent_doc: "../app_completion_master_audit_20260507.md"
two_fork_chats:
  - "app_flow_requirements_interface_chat_launch_prompt_20260507.md (Sub-Chat A)"
  - "backend_interface_refinement_chat_launch_prompt_20260507.md (Sub-Chat B)"
related:
  - "../protocol_snapshot_p4.md (协议 SSOT)"
  - "../module_map_p4_snapshot.md (架构 quick-ref)"
  - "../cross_chat_pending_registry_20260507.md (NEED-* 真源)"
  - "../dsg/workspace_index.md (DSG 工作区)"
  - "../goslo_modularization_residual_debt_20260506.md"
  - "../ar_app_flow_ui_design.md"
  - "../sprint4_protocol_v2_ecp.md"
---

# ParrotCarriers — 接口设计 + How-TODO 设计列表 v0

> **本文用途**：把"App 完成度对账"+"DSG 协议升级"+"GOSLO 模块化"+"Sprint 4 Phase 4 协议合同"汇总成 Sonnet 4.6 可直接抄码的**接口设计 + TODO 注释 + 算法/Skill 决策表**。
>
> **使用流程**：
> 1. **Opus 4.7 ×2（Sub-Chat A 用户视角 + Sub-Chat B 模块视角）**：先调研一轮，逐项 verify 本文 §5 接口签名是否覆盖足、函数返回类型是否合理、命名是否与既有 SSOT 一致；产出 patch（不重写本文）
> 2. **Sonnet 4.6**：拿本文 §5 + §2 名词表 + §3 Skill 表 + §4 算法表 + §9 TODO grep 速查抄码；遇到不懂的概念回 §2 / §3 / §4 查
> 3. **里程碑触发我（本 chat AI）来 Review**：每完成 1 个场景 / 1 个横切关注点的代码 → 我做 grep + 测试基线 + Phase 4 §8 0 漂移 audit
>
> **基调**：本文**不重写 SSOT**（protocol_snapshot_p4 / module_map_p4_snapshot / 完成报告），只做"已有能力索引 + 缺口接口 + How TODO"。
>
> **硬约束**：不改 wire / 不改 enum / 不改 BB key / 不发明新 NEED-* 标签 / 415/415 pytest 不破。

---

## §0 阅读说明（Sonnet 4.6 + Opus 4.7 + 我各自怎么用）

| 角色 | 用法 |
|:--|:--|
| **Opus 4.7（Sub-Chat A 用户视角）** | 用本文 §1 增补场景 + §5 「Unity / EcpEvent / EcpCommand」标记的子任务 + §6 跨场景表去验证 `app_flow_requirements_interface_<date>.md` 是否覆盖 |
| **Opus 4.7（Sub-Chat B 模块视角）** | 用本文 §1 增补场景 + §5 「Brain / DSG / scheduler」标记的子任务 + §3 Skill 表 + §4 算法表 去验证 `backend_interface_refinement_<date>.md` 是否覆盖 |
| **Sonnet 4.6** | 主战场。每个场景按以下序列：① 读 §2 名词 ② 读 §3 Skill 表对应行 ③ 读 §4 算法表对应行 ④ 抄 §5 接口签名 ⑤ 抄 §5 TODO 注释 ⑥ 写代码（每个 grep `TODO(Chat4-*` / `NEED-*` 都要解决或留新 TODO 索引）|
| **我（本 chat AI）** | 里程碑（每场景代码完成 / 每横切关注点完成）触发：① grep `TODO(Chat4-` / `NEED-P2.5-` / `NEED-P3-` 残留 ② Phase 4 §8 13 锁 0 漂移 audit ③ cs_parity 4/4 / ObservationSource 7 / NodeKind 6 / EdgeKind 8 全 freeze 测试守 ④ 给修复指导 markdown |

---

## §1 场景与功能覆盖审查（Pass 1：是否有遗漏？）

> 总 chat 主 doc 列了 8 场景。本节做一次 audit：从 `ar_app_flow_ui_design.md` + `parrot_behavior_rules.md` + `requirements.md §四 C 段` + 4 legacy DSG 触发器入手，找出**没单独列但实施时一定会撞到**的功能 / 子任务。

### §1.1 总 chat 8 场景对账（已覆盖）

✅ S1 GOSLO AR 陪伴对话 ✅ S2 主动好奇 ✅ S3 拍照评论 ✅ S4 Plan→nanobot→回流 ✅ S5 Plan UI ✅ S6 4 类块菜单 ✅ S7 LineA↔LineB ✅ S8 场景切换+归档

### §1.2 ⚠ 增补场景（必须额外覆盖）

| # | 增补场景 | 来源 / 依据 | 实施触发位置 |
|:--|:--|:--|:--|
| **S0** | **启动流程**：启动页菜单 → 权限检查 → Token Mint → LiveKit room 连 → AR session start → onSceneReady 问候 | `ar_app_flow_ui_design.md §4-§5` + AR Sprint3 AC1-AC3 / `unity/ParrotDev` 历史经验 + Sprint4 lifecycle skill | Unity `Lifecycle/AppLifecycleManager` 11 态 FSM 启动序 + Brain `agent.py` brain_entrypoint |
| **S1.5** | **手势 perch_to_finger 子任务细化** | `parrot_behavior_rules.md §1.1 + §5` + `sprint4_phase4_entry_20260430 §3.3` 行为矩阵补充第 2 行 | Unity XRHandTracker + Reflex layer + 自动接续 Intent（PERCHED_ON_HAND + HEAD_TILT） |
| **S9** | **HUD / 工具柜交互**：开关 / 收纳 / 横竖向方向选择 + 持久化用户偏好 | `ar_app_flow_ui_design.md §6 + §7` + 用户原话"对角设计减少自动适配" | Unity ParrotApp/Hud/* + ParrotApp/Toolbar/* 新建 |
| **S10** | **视频档位 / 音频路由的运行时调节**：set_video_tier tool / PerceptionSupervisor 自动降档 / 蓝牙 / 耳机插拔 | `parrot_behavior_rules.md §4.3 set_video_tier` + `livekit-unity-lifecycle/SKILL.md` + `livekit-unity-video-publish/SKILL.md` | Unity VideoTierReceiver / MicrophonePublisher 已存在；Brain set_video_tier tool 已存在；缺**用户主动从工具柜切档位**入口（NEED-P2.5-B 一部分） |
| **S11** | **Brain tool 全集合健全性 + capability gating**：remember / query_memory / query_scene / manage_episode / set_mode / dispatch_task / identify_object / capturePhoto / animate / fly_to / set_video_tier 11 项 | `cross_chat_pending_registry §4.F NEED-P3-CAPABILITY-GATING` + `requirements.md §四 B 段` | Brain `_register_tools()` capability gating 增量（Chat 4 4-A 可选） |
| **S12** | **DSG 4 legacy 触发器自主行为**：CalendarTrigger（日程提醒三层）+ MessageNotificationTrigger（Gmail 重要消息）+ SsotEnrichmentTrigger（充实物体）+ SceneContextTrigger | `cross_chat_pending_registry` 隐含 + `dsg_protocol_trigger_v2_20260506.md §5` + 4 触发器源码均已存在 | 4 个触发器在 Sprint 0-4 已 IMPLEMENTED；缺**触发产物到 Brain LLM 的"自然播报"路径**（受 NEED-P2.5-A persona 影响） |

### §1.3 ⚠ 横切关注点（不是场景，但必须实施）

| # | 关注点 | 来源 | 触发位置 |
|:--|:--|:--|:--|
| **CC-1** | **Echo 全链路（attention.config.echo 数据流安全策略）** | `protocol_snapshot_p4 §3 attention.config.echo` + Phase 4 §8 L9 / F-05 | Unity `Attention/AttentionConfigEchoPublisher` + Brain `attention_config_handler` 已落地；CC-1 = 巩固 + 写测试 |
| **CC-2** | **重连 / 切后台 / handoff（lifecycle 防御）** | `livekit-unity-lifecycle/SKILL.md` + `connection.health.changed` event | Unity `Lifecycle/AppLifecycleManager` 11 态 FSM；R1-R6+D5 audit 已修；CC-2 = 真机 spike 验证 |
| **CC-3** | **8KB 拒收 / 60s dedup / oversize synthesized event** | Phase 4 §8 L3 + L2 | Brain `event_ingest.py` 已落地；CC-3 = freeze test + cs_parity 守护增量 |
| **CC-4** | **Reflex / Intent / Task 三层调度的边界** | `parrot_behavior_rules.md §0.1 + §3.7` | scheduler/router 已落地浅层 BT；CC-4 = Reflex 子树新增（手势 / 紧急避障）+ Intent 不被 Task 阻塞 |

### §1.4 显式不在本文范围（推到对应 chat）

| 项 | 推到哪 | 原因 |
|:--|:--|:--|
| L1 真实视觉管线（SAM2 + YOLO-World + DINOv2） | A10 接入 chat | 需 A10 GPU |
| MemoryValidity / Skill Distillation | P3+ chat | 不在 Sprint 4 范围 |
| 多房间 / 多 user / 群聊 | P3+ chat | 同上 |
| Plan UI wire（场景 5）真升级 | P3 wire ADR chat | BLOCKED-BY-NEW-ADR |
| body_state 解锁（场景 6）| 同上 | 同上 |
| 多 SceneType（HOME_INDOOR / OUTDOOR / LIBRARY / KITCHEN）真 profile | P3 / A10 接入 chat | TODO(P3-multi-scene) |
| Spreading Activation 真迭代 / Fold 真实施 / RefHealth 真验证 | P3 仿生升级 chat | TODO(P3-*) |
| Persona 文件外置 schema（NEED-P2.5-A）真设计 | DSG 协议升级 chat（与 4 类块统一）| user 已 sign-off 推下游 |

---

## §2 名词概念索引（Sonnet 4.6 不懂时回查）

> 每条 = **一句话定义** + **代码 / SSOT 锚点**。Sonnet 4.6 写代码遇到不熟悉的术语时**先查这里**，不要自己发明语义。

### §2.1 协议 / Wire 概念

| 名词 | 一句话定义 | 锚点 |
|:--|:--|:--|
| **EcpCommand** | Brain → Unity 目标驱动命令（命令 ID + 过期时间 + active_locks_required + meta dict） | `src/parrot/shared/ecp.py` ; `protocol_snapshot_p4 §6` |
| **EcpAck** | Unity 对单条 EcpCommand 的真实回执（5 态 ApplyStatus）；走 RPC return value | `protocol_snapshot_p4 §5` |
| **EcpEvent** | Phase 4 跨语言 wire envelope；走 reliable DataChannel topic `parrot.ecp.event`；13 EcpEventType；payload < 8KB | `src/parrot/shared/ecp_event.py` ; `protocol_snapshot_p4 §2-§3` |
| **EcpState** | Unity → Brain 周期心跳（body / head / cognitive / active_locks / active_command_id）；事件驱动 + 1Hz | `src/parrot/shared/ecp.py:EcpStateDto` ; `protocol_snapshot_p4 §4` |
| **EcpCommand.meta["model_id"]** | GOSLO Step 1 plumbing；多模型路由不动 wire 顶层 schema | `goslo_model_manifest_protocol_v1 §2.3` |
| **RefBinding** | Unity → L2-B 节点的引用绑定；4 RefKind（BBOX/FOCUS/PHOTO/SIGHTING）+ 4 RefTargetKind | `protocol_snapshot_p4 §8` |
| **5 LiveKit DataChannel topic** | `parrot.ecp.event` reliable / `parrot.ecp.state` reliable / `parrot.ecp.health` inline / `parrot.ecp.intent_disconnect` inline / `parrot.ecp.tick` lossy | `protocol_snapshot_p4 §1` |

### §2.2 DSG 概念（Sonnet 4.6 必读）

| 名词 | 一句话定义 | 锚点 |
|:--|:--|:--|
| **L1 / L1.5 / L2-A / L2-B / L3** | 视网膜 / 视觉皮层 / 背侧通路（空间）/ 腹侧通路（语义）/ 前额叶（叙事归档） | `module_map_p2 §10.1` |
| **Scene** | 物理 / 任务环境（DESKTOP / HOME_INDOOR / OUTDOOR / LIBRARY / KITCHEN）；驱动 L1.5 BucketRegistry freeze/clear + L2-B 切片 | `dsg_protocol_scene_snapshot_v1` ; SceneRegistry ; SceneSwitchOutcome |
| **Bucket** | L1.5 池里的"出口管理面"6 类（OBSIDIAN_REFERENCE_REINFORCE 永久 / OBSIDIAN_SETTING_DAILY 永久 / OBSIDIAN_SETTING_ROLEPLAY 永久 / IDENTIFY_OBJECT_RESULT 永久 / GEMINI_ORAL_MENTION TTL / AUTONOMOUS_CURIOSITY 300s TTL） | `protocol_snapshot_p4 §18` ; `dsg/l1_5/buckets.py` |
| **IntentEvent** | L2-B 边界（不是 Episode），通过 IntentEventBoundaryHandler.close()/clear_bucket()/switch_scene() 三路触发 | `dsg_protocol_intent_event_boundary_v1` |
| **IntentWorkspace** | Brain 大文件常驻容器；9 StagedRefKind（PLAN_DRAFT / PLAN_AWAITING_USER / INTENT_THREAD / IDENTIFY_OBJECT_PENDING / MEMORY_RECALL_THREAD / BBOX_REFERENCE / FOCUS_REFERENCE / PHOTO_REFERENCE / CUSTOM）；InMemory / Disk Backend | `protocol_snapshot_p4 §19` ; `brain/intent_workspace.py` |
| **Plan vs NanobotTask** | Plan = Brain 内 Plan-and-Execute 8 状态机；NanobotTask = Plan 一个 step 派给 nanobot 的派发实例（plan_id × step_id 关联） | `brain/plan/*` ; `cross_chat_pending_registry §3.B` |
| **Episode** | Conversation 时段单位；3 阶段归档（hot 内存 / cold 序列化 / nanobot 闲时归档到 Graphiti） | `dsg_protocol_archive_v1` |
| **ConversationBoundary** | 多信号 OR（话题切换 / silence 阈值 / scene_switch / mode_switch / explicit）触发归档分段 | `dsg_protocol_archive_v1 §1` |
| **ObservationSource 7+1** | USER_TAG_OBSIDIAN / USER_EXPLICIT / IDENTIFY_OBJECT / GEMINI_ORAL / CV_A10 / CV_SENTINEL / MOCK + GOSLO_AUTONOMOUS（第 8 项）| `protocol_snapshot_p4 §17` ; ADR-L1.5-001 §1.1 锁 |
| **Compartment view** | L2-B 单图 + 5 lazy view（view_by_bucket / event / scene / location / kind）；不分图 | `dsg_l1_5_implementation_completion §6 master 11 条` |
| **Subgraph fold** | RustworkX 子图折叠（NoOpFoldStrategy baseline / TODO(P3-fold-bionic) 真实施） | `dsg/l2b/intent_event_boundary.py:NoOpFoldStrategy` |
| **5 路 TriggerOutcome V2** | commit_observations / bucket_ops / staged_refs / archive_request / plan_request（+ 2 legacy：dispatch_to_nanobot / notify_gemini） | `dsg_protocol_trigger_v2 §2` |

### §2.3 Brain / Behavior 概念

| 名词 | 一句话定义 | 锚点 |
|:--|:--|:--|
| **Reflex / Intent / Task** | 三层调度：Reflex（ms-s 反射，绕 LLM）/ Intent（s-min，自身行为）/ Task（min+，异步派发） | `parrot_behavior_rules.md §0.1` |
| **Persona vs Mode vs Model** | Persona = LLM 嗓音（NEED-P2.5-A 外置）/ Mode = 行为 flag（companion / butler / researcher / playful / FULL）/ Model = Unity 视觉模型（GOSLO_default 等） | `goslo_modularization_residual_debt §4.3` |
| **Observer vs Attention 模块** | Observer = 检测事件 + 决定何时打点（"记录"）；Attention = 收集数据触发触发器（"判断"）；**Phase 4 范围只有 Observer + 临时阈值器** | `parrot_behavior_rules §3.7` ; `sprint4_phase4_entry §3.7` |
| **Echo 全链路** | Unity ScriptableObject 阈值 → publish `attention.config.echo` EcpEvent → Brain handler 写 BB `global/attention_thresholds` → FocusBboxThreshold 读；防 Brain/Unity 阈值漂移 | `protocol_snapshot_p4 §3 + Phase 4 §8 L9` |
| **selection-C** | LLM 注入路径主路径：execute 类 tool 在 execute 前检查 BB body / head / cognitive 三态附 reason | Phase 4 §8 L10 |
| **LineA / LineB pipeline-agnostic** | LineA = Gemini Realtime / LineB = STT-LLM-TTS；env-gate `PARROT_LLM_PIPELINE` 切换；ObservationSource 7 entries verbatim 守护跨管线行为不变 | `lineb_implementation_completion §2` |

### §2.4 Unity / Lifecycle 概念

| 名词 | 一句话定义 | 锚点 |
|:--|:--|:--|
| **AppLifecycleState 11 态 FSM** | Unbooted → Booting → Booted → ConnectingLiveKit → AwaitingPermissions → SessionWarming → SessionReady → SessionLive → SessionPaused → SessionRecovering → SessionShuttingDown | `livekit-unity-lifecycle/IMPL_REF.md §1-§3` |
| **ConnectionHealthState** | overall: healthy / degraded / lost / recovering（4 态聚合 = audio + video + brain_presence + ar_tracking）| Phase 3 收口 |
| **ParrotRegistry** | scene-singleton P1 stub（last-registered active）；P3 多 actor 真路由占位 | `Parrot/ParrotRegistry.cs` |
| **fallback 链** | IParrotController → AnimationDriver → Animator → dev pulse；旧场景 0 漂移 | `goslo_modularization_completion §3.2` |
| **VideoTier × DsgMode 两轴正交** | VideoTier（VIDEO_OFF / VIDEO_GEMINI_ONLY / VIDEO_FULL / VIDEO_BURST）× DsgMode（DSG_TEXT_ONLY / DSG_GEMINI_VISION / DSG_FULL / DSG_SENTINEL_AUX） | `module_map_p2 §10.3` |

---

## §3 Skill 决策表（什么场景用哪个 Skill 的哪一节）

> Sonnet 4.6 写代码前**先查这表**，按"场景 → Skill 锚点"读 skill。**只读 SKILL.md + IMPL_REF.md 必要章节**，不要逐文件读 skill 全文。

| 场景 / 子任务 | 主 Skill | 配套 Skill | 关键章节 |
|:--|:--|:--|:--|
| **S0** 启动流程 / 权限 / Token Mint | `livekit-unity-lifecycle/SKILL.md` + `IMPL_REF.md §1-§3` | `client-sdk-unity/SKILL.md` | 11 态 FSM + AppLifecycleManager + RoomManager.OnConnected |
| **S1** GOSLO 对话 + Brain tool 路由 | `livekit-agents/SKILL.md` | `client-sdk-unity` RPC + `livekit-unity-video-publish` | AgentSession + function_tool + RPC Reliable |
| **S1.5** perch_to_finger 手势 | `livekit-unity-lifecycle/IMPL_REF.md §6 setVideoTier` | `parrot_behavior_rules.md §5 PerchOnHand` | Reflex 跨进程触发 + 自动接续 Intent |
| **S2** 主动好奇 + L1.5 Pool | `dsg-rustworkx-master/SKILL.md` | `dsg-l2b-node-organization-options/SKILL.md` + `dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md` + `graphiti/SKILL.md` | RustworkX BFS + spreading + AdmissionPolicy + commit_observation |
| **S3** 拍照 + 双通道 | `livekit-unity-video-publish/IMPL_REF.md §6 capturePhoto` | `livekit-unity-lifecycle/SKILL.md` + `client-sdk-unity` | AsyncGPUReadback + base64 < 8KB + HTTP POST + EncodeToJPG quality cascade |
| **S4** Plan + Nanobot 长任务 | `nanobot/SKILL.md` | `nanobot-overview/SKILL.md` + `livekit-agents/SKILL.md` + `py-trees/SKILL.md` | parrot_bus channel + Redis Stream / Pub-Sub + dispatch_task |
| **S5** Plan UI wire | （**BLOCKED-BY-NEW-ADR — P3 wire 升级 ADR chat**） | — | 新 EcpEventType + Plan card UI + Approve EcpCommand |
| **S6** 4 类块菜单画布 | `dsg-rustworkx-master/SKILL.md` | `goslo_model_manifest_protocol_v1` (已 ratified) | 4 active BB key + 注册表 + 节点画布（节点-边模型） |
| **S7** LineA↔LineB 切换 | `livekit-agents/SKILL.md` §1+§3+§4 | — | env-gate + PipelineAgent + RealtimeAgent + transcript_extractor |
| **S8** 场景切换 + 归档 | `dsg-rustworkx-master/SKILL.md` + `graphiti/SKILL.md` | `dsg-attention-schema-papers` (Hippocampal Indexing 部分) | SceneRegistry.SceneSwitchOutcome + Bucket freeze/clear + 3-Phase 归档 |
| **S9** HUD / 工具柜 | （Unity Editor 自建）| `ar_app_flow_ui_design.md §6-§7` | Canvas + 9-slice + 像素字体 |
| **S10** 视频 / 音频运行时调节 | `livekit-unity-video-publish/SKILL.md §三 + §四` | `livekit-unity-lifecycle/IMPL_REF.md §6` | setVideoTier + cool-down + 蓝牙路由 |
| **S11** Brain tool 全集合 + capability gating | `livekit-agents/SKILL.md` | `goslo_model_manifest_protocol_v1 §3.6 declared_capability_ids` | function_tool + ModelManifestRegistry 副本 |
| **S12** DSG 4 legacy 触发器 | `dsg/triggers/*` 源码 + `dsg_protocol_trigger_v2 §5` | `graphiti/SKILL.md` | calendar / message / ssot / scene_context 现存实现 |
| **CC-1** Echo 全链路 | `livekit-unity-lifecycle/SKILL.md` | — | F-05 Echo + RoomManager.OnConnected 含 reconnect |
| **CC-2** 重连 / 切后台 / handoff | `livekit-unity-lifecycle/IMPL_REF.md §2-§5` | `client-sdk-unity` | OnApplicationPause + ICE restart + ARCore 黑帧 |
| **CC-3** 8KB / dedup / oversize | （直接看 `event_ingest.py`） | — | `protocol_snapshot_p4 §2 + §3` |
| **CC-4** 三层调度边界 | `py-trees/SKILL.md` | `parrot_behavior_rules.md §0.1+§3.2` | Selector + Sequence + Parallel + Blackboard V2 |

### §3.1 Skill 主索引

| Skill | 何时读 |
|:--|:--|
| `dsg-rustworkx-master/SKILL.md` | DSG 设计 chat 总入口 — RustworkX 实操 + 仿生 4 范式 + 跨 skill 论文索引 |
| `dsg-l2b-node-organization-options/SKILL.md` | L2-B Node/Edge 组织 5 选项 + 子图分层 P1-P4 |
| `dsg-attention-schema-papers/SKILL.md` | 13 篇论文（GAT / DySAT / 图聚类 over-globalization 等）|
| `dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md` | A10 入口门控 + L2-A 语义抽象（A10 Phase 5+ 接入参考）|
| `livekit-agents/SKILL.md` | AgentSession + function_tool + TurnHandling + DataChannel + dispatch |
| `client-sdk-unity/SKILL.md` | LiveKit Unity SDK（Room / RPC / DataChannel / Reliable & Lossy）|
| `livekit-unity-lifecycle/SKILL.md` | Room 重连 / SignalReconnect / OnApplicationPause / graceful shutdown / ARCore 后台 / setVideoTier 切换副作用 |
| `livekit-unity-video-publish/SKILL.md` | 一流多采样 + 策略门控 + LiveKit 分发 + Brain/DSG/identify_object 多路消费端边界 |
| `graphiti/SKILL.md` | add_episode / search / 自定义 entity types / Neo4j/FalkorDB / group_id |
| `nanobot/SKILL.md` | parrot_bus channel + Redis 松耦合接口 + 后台 Agent + 子任务 |
| `py-trees/SKILL.md` | Behaviour / Selector / Sequence / Parallel / Blackboard V2 |
| `sva-vision-agents/SKILL.md` | Vision-Agents Processor 模式（VideoProcessor / attach_agent / fps）— A10 接入用 |

---

## §4 算法决策表（What algorithm + 决策依据）

> Sonnet 4.6 写代码遇到"用 BFS 还是 DFS 还是 spreading"等技术选择**先查这表**。每条决策都列**A vs B 选项 + 推荐 + 依据 doc 锚点**。

### §4.1 L2-B 候选检索 / 注意力扩散

| 决策点 | 选项 A | 选项 B | 选项 C | 推荐 | 依据 |
|:--|:--|:--|:--|:--|:--|
| 候选检索算法 | RustworkX `bfs_successors`（限深 BFS）| RustworkX `DiGraph.dijkstra`（带权最短路）| Spreading Activation 真迭代 | **A**（baseline）；C = TODO(P3-attention-spreading) | `dsg/l2b/attention/mechanism.py:BoundedBfsActivation` |
| 子图 fold | `subgraph(node_indices)` 真折叠 | NoOp（baseline）| `subgraph_with_nodes_map`（VF2++ 模式匹配）| **NoOp**（baseline）；A/C = TODO(P3-fold-bionic) | `dsg/l2b/intent_event_boundary.py:NoOpFoldStrategy` |
| Compartment view | 5 lazy view（view_by_bucket / event / scene / location / kind）| 多正交子图（PVR P4 一部分）| 真物理分图（旧设计） | **5 lazy view**（已落地，P4 + P1 混合） | `dsg_l1_5_implementation_completion §6 master 11 条 §6.5` |
| Cluster 检测 | `connected_components`（连通分量）| Leiden Community（社区发现）| K-Means / DBSCAN | **不实施**（Phase 4 范围外） | `requirements.md §四 G3` G3 Phase 3 |
| 注意力衰减 | per-tick `AttentionDecayPolicy.SimpleDecay` | per-bucket TTL（BucketSpec.default_ttl_seconds）| GHOST 转换 | **per-tick + per-bucket 双层（已 ratified）**；GHOST = master § 3.5 测试期不衰减 | `dsg/l2b/attention/decay.py` |

### §4.2 L1.5 Pool 入门 / 出门

| 决策点 | 选项 A | 选项 B | 推荐 | 依据 |
|:--|:--|:--|:--|:--|
| AdmissionPolicy | DesktopPolicy(theta_admit=0.3) baseline | multi-scene profile（HOME_INDOOR / OUTDOOR / ...）| **A**（baseline；B = TODO(P3-multi-scene)）| `dsg/l1_5/admission.py` |
| 主动出池触发 | IntentEventBoundaryHandler.close() | clear_bucket() | switch_scene() | **三路并存**（已 ratified） | `dsg_protocol_intent_event_boundary_v1 §3` |
| Bucket TTL 语义 | 永久权威（OBSIDIAN_REFERENCE_REINFORCE / SETTING_DAILY / SETTING_ROLEPLAY / IDENTIFY_OBJECT_RESULT 4 项）| TTL fresh（GEMINI_ORAL_MENTION / AUTONOMOUS_CURIOSITY 2 项）| **两类共存**（scene 切换 freeze 永久 / clear fresh） | `protocol_snapshot_p4 §18` |
| _SOURCE_PRIORITY 切换 | 静态硬编码 | SceneProfile.priority_overrides 动态 | **B**（已 ratified；接口已锁，应用层未启用 — Sub-Chat B 评估）| master § 3.1 |

### §4.3 ConversationBoundary 信号

| 决策点 | 选项 | 推荐 |
|:--|:--|:--|
| 信号 OR 算法 | 话题切换 LLM 检测 / silence > 阈值 / scene_switch / mode_switch / explicit user 触发 | **5 信号 OR 已实施**；具体阈值留 manage_episode tool LLM 决定 |

### §4.4 Plan-and-Execute 状态机

| 决策点 | 选项 | 依据 |
|:--|:--|:--|
| 状态机 | DRAFT → AWAITING_USER_CONFIRMATION → APPROVED / REJECTED / REVISED → EXECUTING → DONE / FAILED（8 态） | `brain_protocol_plan_v1 §4` |
| User confirmation | 当前由调用方直接 `approve()` | 真 EcpEvent UI = TODO(P3-Wire-PlanUI) |
| revise | 创建新 plan + supersedes 旧 | `test_plan_lifecycle::test_revise_creates_new_plan_supersedes_old` |
| step result 回流 | `plan_id` + `step_id` 透传 → scheduler `active_tasks` BB → `_listen_nanobot_results` 路由 `report_step_result` | NEED-P2.5-PLAN-INTEGRATION（4 plan-* TODO + bb-namespace）|

### §4.5 Photo / Snapshot 数据通道

| 决策点 | 选项 A | 选项 B | 推荐 | 依据 |
|:--|:--|:--|:--|:--|
| Preview 编码 | base64 直传（< 8KB） | HTTP POST | **A**（已 ratified；quality cascade 75→60→50→40）| Phase 4 §8 L8 |
| Asset 高清 | DataChannel 大块 | HTTP POST `/upload/photo/{id}` | **B**（已 ratified；Castle 本地 cache）| 同上 |
| Reconnect 不重发 | PendingPhoto 队列 | drop | **A**（已 ratified）| `goslo_modularization_completion §1.3` 同模式 |

### §4.6 Reflex / Intent / Task 三层（CC-4）

| 决策点 | 选项 | 推荐 |
|:--|:--|:--|
| Scheduler 拓扑 | 4 叶浅 Selector（当前）| 完整 BT 森林（Safety / Priority / Parallel / Idle 4 子树） | **当前浅 Selector + 按需扩 Reflex 子树**；完整 BT = E4 P3+ 扩展 |
| Reflex 触发 | open_palm 手势 → flyTo + 锚定 | 紧急避障 / 低层身体反应 | **first 已 ratified**；后者 P3 |
| Tool 同步语义 | fly_to / animate / set_video_tier / identify_object 同步等 ack | dispatch_task 异步 fire-and-forget | **已 ratified**（parrot_behavior_rules §4.3 体感红线） |

---

## §5 12 个场景 + 4 横切关注点的接口设计 + How TODO（核心）

> 每个场景 / 关注点结构：① 子任务清单 ② 已有能力索引 ③ 缺口接口 ④ 函数签名草稿 ⑤ How TODO 决策 ⑥ TODO 注释草稿。
>
> Sonnet 4.6 抄码顺序：⑥ TODO 注释先抄 → ④ 签名抄 → ⑤ How TODO 边写边查 → ② 已有能力 reference → ③ 缺口确认。

---

### §5.0 S0 — 启动流程（启动页 → 权限 → Token Mint → AR session → 问候）

**子任务清单**：
- T0.1 启动页菜单（5 项 baseline：开始 AR / 房间 / 管线 / 人设 / 权限测试）
- T0.2 权限请求序列（Camera / Mic / Network）
- T0.3 Token Mint（POST `/token_mint`）
- T0.4 LiveKit room 连接 + AR session start
- T0.5 onSceneReady → Brain "你好"语音 + 单问候去重

**已有能力索引**：
- ✅ Token Mint server: `src/parrot/brain/token_mint.py` (port 7888)
- ✅ Unity `Lifecycle/AppLifecycleManager` 11 态 FSM
- ✅ Unity `LiveKit/RoomManager` + Token 文件读取（Resources/parrot_config.json）
- ✅ Brain `agent.py:brain_entrypoint` + onSceneReady 单问候去重（Sprint3 AC3 已修）

**缺口接口**：
- ❌ Unity 启动页菜单 5 项 UI（NEED-P2.5-B 一部分；占位 + 文字按钮即可）
- ❌ 启动页 → AR 主场景的 SceneManager 切换流程（user 自管 Unity Editor 配置）
- ⚠ 权限丢失 fallback（livekit-unity-lifecycle skill 已覆盖；测试用例缺）

**函数签名草稿（Unity C#）**：
```csharp
// unity/ArSpike/Assets/Scripts/ParrotApp/Boot/StartupMenuController.cs (NEW)
public class StartupMenuController : MonoBehaviour {
    public event Action<StartupChoice> OnChoiceMade;

    public enum StartupChoice {
        StartAR, ChooseRoom, ChoosePipeline, ChoosePersona, RunPermissionTest
    }
    public void OnStartARClicked();    // → ChooseRoom 默认 + ChoosePipeline 默认 line_a
    public void OnRunPermissionTestClicked();  // → AppLifecycleManager.RequestPermissionsOnly
}

// 配套事件
public event Action OnSceneReady;  // RoomManager 通知 ParrotController 触发问候
```

**How TODO**：
| 决策点 | 推荐 | 依据 |
|:--|:--|:--|
| 启动页是 Unity Scene（不是 UI overlay） | ✅ 是；`Boot.unity` 独立场景 → `Main.unity` AR 场景 | `ar_app_flow_ui_design §4` |
| 权限请求时机 | AR session start **之前**（避免 AR 初始化失败再回滚 UX） | `livekit-unity-lifecycle/IMPL_REF.md §2` |
| 单问候去重 | 已修；通过 Brain BB `session/greeting_played` flag | Sprint3 AC3 修复记录 |
| 启动页是否含调试折叠 | 第一版含；P3 移到工具柜内 | `ar_app_flow_ui_design §5 调试面板行` |

**TODO 注释草稿**（Sonnet 4.6 抄进 `StartupMenuController.cs` 顶部）：
```csharp
// TODO(S0-startup-menu-baseline): 启动页菜单 5 项 baseline UI（开始 AR / 房间 / 管线 / 人设 / 权限测试）
//   - 占位策略: 紫色方块 + 像素字体文字按钮（参考 master_audit §6.1 Class 1）
//   - 名词索引: 接口设计文档 §2.4 "AppLifecycleState 11 态 FSM"
//   - 决策表: 接口设计文档 §5.0 How TODO 4 行
//   - Skill: livekit-unity-lifecycle/IMPL_REF.md §2 启动序
//   - 缺口标签: NEED-P2.5-B (Unity menu 暴露 DSG bucket / scene 切换接口)
//   - 后续: P3 节点画布 menu 替代（NEED-P3-D / NEED-P3-E）
```

---

### §5.1 S1 — GOSLO AR 陪伴对话（baseline）

**子任务清单**：
- T1.1 LLM 接收语音 → ASR → tool 决策 → 同步 RPC（fly_to / animate / set_video_tier）
- T1.2 selection-C state header（execute 类 tool 检 BB body / head / cognitive 附 reason）
- T1.3 cognitive_state_tracker 监听 `agent_state_changed` 写 BB `tick/cognitive_state`
- T1.4 EcpAck 5 态返回 → LLM 同步话术（"我飞过去了"/"我没飞过去，超时了"）
- T1.5 Echo 全链路（Unity ParrotAttentionConfig SO → publish `attention.config.echo` → Brain 写 BB `global/attention_thresholds`）

**已有能力索引**：
- ✅ Phase 4 §8 13 锁；selection-C `_state_context.py`；cognitive_state_tracker.py；attention_config_handler.py
- ✅ Unity ParrotController + ParrotRpcHandler + AnimationDriver + ModelDriver + GosloLegacyController
- ✅ EcpAck 5 ApplyStatus；EcpState 1Hz + 事件驱动

**缺口接口**：
- ⚠ NEED-P2.5-A persona 外置（不阻塞 baseline；但换非鹦鹉模型 LLM 嗓音不变）
- 无其他 wire 缺口；接口 surface 已稳定

**函数签名草稿**：
```python
# src/parrot/brain/personas/__init__.py (NEW for NEED-P2.5-A; deferred)
def load_persona(persona_id: str) -> PersonaSpec: ...

# 当前 baseline: 不动 brain/soul.py；持续监控 BB key `global/active_persona_id` (默认空 = goslo_parrot_default)
```

**How TODO**：
| 决策点 | 推荐 | 依据 |
|:--|:--|:--|
| selection-C reason 写哪 | tool 函数 docstring 加 "wraps with selection-C" + reason 写到 LLM 看到的 tool result 字符串前缀 | Phase 4 §8 L10 |
| Echo 时机 | RoomManager.OnConnected（含 reconnect / Brain 管线切换）+ ContextMenu 兜底 | Phase 4 §8 L9 F-05 |
| LLM 话术体感 | tool result 必须含 `applied / rejected / timeout / no_target / unchanged` 5 态明显标记 | parrot_behavior_rules §0.3 / §4.3 |

**TODO 注释草稿**：
```python
# TODO(S1-baseline-watch): NEED-P2.5-A persona 外置后回来切换
#   - 当前: brain/soul.py 内联硬编码 (CORE_INSTRUCTIONS / COMPANION_INSTRUCTIONS / PLAYFUL_INSTRUCTIONS)
#   - 触发: BB key `global/active_persona_id` 由 4 类块菜单 set 后切换
#   - 名词索引: 接口设计文档 §2.3 "Persona vs Mode vs Model"
#   - 缺口标签: NEED-P2.5-A; 推到 DSG 协议升级 chat (与 NEED-P3-B/C 4 类块统一)
```

---

### §5.1b S1.5 — 手势 perch_to_finger（增补子场景）

**子任务清单**：
- T1.5.1 XRHandTracker 检测 open_palm 手势
- T1.5.2 Reflex 触发 flyTo（不走 LLM）
- T1.5.3 飞到食指中段 = 成功判定点
- T1.5.4 自动接续 Intent：锚定 PERCHED_ON_HAND + HEAD_TILT（"怎么了？"）
- T1.5.5 EcpState 三态字段同步（body=PERCHED_ON_HAND / head=HEAD_TILT / cognitive=LISTENING）

**已有能力索引**：
- ✅ `unity/ParrotDev/Assets/Scripts/XRHands/{XRHandTracker,PerchOnHand}.cs` (P2.5 测试床版本，需迁移到 ArSpike)
- ✅ AnimationDriver 已支持 perch state；ParrotBodyState.PERCHED_ON_HAND
- ✅ HeadState.HEAD_TILT
- ✅ EcpState 三态字段已锁

**缺口接口**：
- ❌ Reflex 触发 flyTo 不走 LLM 的代码路径（当前 flyTo 都走 brain.tools；需 Unity 端直接派发 EcpCommand 到自身 RPC handler）
- ❌ 自动接续 Intent 的状态机（Reflex 完成 → 自动 Intent 锚定）
- ❌ 食指中段成功判定点（XR Hands joint API 调用）
- ❌ 工具迁移 ParrotDev → ArSpike

**函数签名草稿（Unity C#）**：
```csharp
// unity/ArSpike/Assets/Scripts/ParrotApp/Reflex/PerchToFingerReflex.cs (NEW)
public class PerchToFingerReflex : MonoBehaviour {
    void OnOpenPalmDetected(XRHandJoint indexMidPhalange) {
        // Reflex 不走 Brain；直接构造 EcpCommand → 本地 RPC handler
        var cmd = EcpCommandLocal.ForPerchToFinger(target: indexMidPhalange.position);
        _parrotRpcHandler.HandleFlyTo(cmd);  // 同步等 ack
        // 自动接续 Intent
        _parrotController.SetBody(ParrotBodyState.PERCHED_ON_HAND);
        _parrotController.SetHead(HeadState.HEAD_TILT);
        // EcpState 自动 publish
    }
}
```

**How TODO**：
| 决策点 | 推荐 | 依据 |
|:--|:--|:--|
| Reflex 是否上报 LLM | **否**（Reflex 层①+②；不打扰对话） | parrot_behavior_rules §0.2 |
| 接续 Intent 是否阻塞对话 | **否**（自主行为；不打扰）；EcpState 三态同步即可让 LLM 通过 selection-C "看到" | parrot_behavior_rules 行为矩阵第 3 行 |
| 食指中段判定 | XRHandJointID.IndexProximal vs IndexIntermediate？ | XR Hands subsystem 文档 |
| 与场景 1 selection-C 的关系 | LLM 下一次 turn 通过 BB body=PERCHED_ON_HAND 自动 awareness | Phase 4 §8 L10 |

**TODO 注释草稿**：
```csharp
// TODO(S1.5-perch-to-finger): 手势 perch_to_finger Reflex + 接续 Intent
//   - 算法: XR Hands open_palm 检测 → 本地 EcpCommand 构造 → ParrotRpcHandler.HandleFlyTo
//   - 名词索引: 接口设计文档 §2.3 "Reflex / Intent / Task" + parrot_behavior_rules §1.1 + §5
//   - Skill: livekit-unity-lifecycle/IMPL_REF.md §6 + parrot_behavior_rules §5 PerchOnHand
//   - 决策: 接口设计文档 §5.1b How TODO 4 行 + §4.6 三层调度
//   - 来源迁移: unity/ParrotDev/Assets/Scripts/XRHands/PerchOnHand.cs (测试床)
//   - 体感判据: 飞到食指中段 = Intent layer 成功；body=PERCHED_ON_HAND + head=HEAD_TILT 自动同步
//   - 不阻塞对话: Reflex + 自主 Intent，不通报 LLM (parrot_behavior_rules §0.2 层①+②)
```

---

### §5.2 S2 — GOSLO 主动好奇 → 触发识别 / 入池 / 反馈

**子任务清单**：
- T2.1 GosloCuriosityTrigger fire（条件由 trigger 内部决定）
- T2.2 commit_observation(source=GOSLO_AUTONOMOUS, ...) → IngestRunner
- T2.3 L1.5 Pool.admit → AUTONOMOUS_CURIOSITY Bucket（TTL 300s）
- T2.4 LLM 通过 BB / context 看到新观察 → "诶那是什么？"自然话术

**已有能力索引**：
- ✅ `dsg/triggers/goslo_curiosity_trigger.py` (DSG Chat 2 落地)
- ✅ `dsg/ingest/{base.py:GOSLO_AUTONOMOUS, runner.py:commit_observation, autonomous_curiosity_filter.py}`
- ✅ `dsg/l1_5/{pool.py, buckets.py:AUTONOMOUS_CURIOSITY, admission.py:DesktopPolicy}`
- ✅ test_l1_5_admission_baseline.test_goslo_autonomous_routing 守

**缺口接口**：
- ⚠ A10 真识别（场景 2 当前是 placeholder；TODO(P3-multi-scene) + Castle ↔ Mecha A10 接入 chat）
- ⚠ "GOSLO LLM 看到主动观察后自然反应"= 受 NEED-P2.5-A 影响
- ⚠ Curiosity trigger 的 fire 条件（轮询？阈值？）— Sub-Chat B 验证

**函数签名草稿**：
```python
# 已存在；不新建
# src/parrot/dsg/triggers/goslo_curiosity_trigger.py:GosloCuriosityTrigger.fire(ctx) -> TriggerOutcome
# 输出 TriggerOutcome.commit_observations + (可选) notify_gemini

# 配套：BB context injector 把 "transient/last_curiosity_observation" 推到 LLM context（已 ratified）
```

**How TODO**：
| 决策点 | 选项 A | 选项 B | 推荐 | 依据 |
|:--|:--|:--|:--|:--|
| Trigger fire 条件 | 周期轮询（每 N 秒）| 事件驱动（如 attention.threshold.crossed）| **B**（Phase 4 之后再调；当前 baseline 用 simple polling）| `dsg_protocol_trigger_v2 §5` |
| AUTONOMOUS_CURIOSITY Bucket TTL | 300s | 永久 | **300s**（fresh 桶） | `protocol_snapshot_p4 §18` |
| LLM 自然反应路径 | system prompt 注入 | tool result 注入 | BB context 自动注入 | **C**（已 ratified；不烧 token） | Phase 4 §8 L10 选项 C |

**TODO 注释草稿**：
```python
# TODO(S2-curiosity-fire-condition): GosloCuriosityTrigger fire 条件 baseline
#   - 当前: simple polling (待 Sub-Chat B 校准间隔)
#   - 升级: event-driven 由 attention.threshold.crossed 触发 (推 P3)
#   - 名词索引: 接口设计文档 §2.2 "Bucket" / "ObservationSource 7+1"
#   - Skill: dsg-rustworkx-master/SKILL.md (BFS / spreading)
#   - 决策表: 接口设计文档 §4.1 注意力衰减 + §4.2 AdmissionPolicy
#   - 缺口标签: 当前不阻塞；A10 真识别 = TODO(P3-multi-scene)

# TODO(S2-curiosity-llm-reaction): GOSLO LLM 看到主动观察后自然话术
#   - 当前: 走 BB context injector 自动注入 (selection-C 同模式)
#   - 限制: 受 NEED-P2.5-A persona 影响 (目前是鹦鹉味儿)
#   - 名词索引: 接口设计文档 §2.3 "selection-C"
```

---

### §5.3 S3 — 拍照 → 展示 → GOSLO 评论

**子任务清单**：
- T3.1 用户在工具柜点拍照按钮（NEED-P2.5-B UI 入口）
- T3.2 Unity PhotoController.CapturePhoto() 双通道：preview reliable < 8KB + asset HTTP POST
- T3.3 Brain `observer/photo` 接收 EcpEvent `photo.taken_preview` → upsert PhotoNode (kind=PHOTO; L7 强制非 ObjectNode)
- T3.4 photo_upload_server (FastAPI 7889) 接收 asset → publish `photo.asset_uploaded`
- T3.5 IntentWorkspace.stage(PHOTO_REFERENCE) → LLM 看到照片 → 评论
- T3.6 联机 smoke（真机 spike chat）

**已有能力索引**：
- ✅ Unity `ParrotApp/Photo/{PhotoController, PendingPhotoQueue}` (Phase 4 W8)
- ✅ Brain `observer/photo.py` + `photo_upload_server.py:7889`
- ✅ EcpEventType `photo.taken_preview` / `photo.asset_uploaded`
- ✅ NodeKind.PHOTO + 3 EdgeKind defer Phase 5+
- ✅ IntentWorkspace.stage(PHOTO_REFERENCE) 9 StagedRefKind 之一
- ✅ test 21 个 W8 测试全绿

**缺口接口**：
- ❌ 工具柜"拍照按钮" UI 入口（NEED-P2.5-B / S9 子任务）
- ⚠ 联机 smoke（defer 真机 spike chat）
- ⚠ "GOSLO 评论" = NEED-P2.5-A 影响

**函数签名草稿（Unity C#）**：
```csharp
// unity/ArSpike/Assets/Scripts/ParrotApp/Toolbar/PhotoButtonController.cs (NEW)
public class PhotoButtonController : MonoBehaviour {
    [SerializeField] private PhotoController _photoController;
    public void OnPhotoButtonClicked() {
        _photoController.CapturePhoto();  // 已存在；不动
    }
}
```

**How TODO**：
| 决策点 | 推荐 | 依据 |
|:--|:--|:--|
| Quality cascade | 75 → 60 → 50 → 40 直到 < 8KB | Phase 4 §8 L8（已 ratified） |
| Reconnect 不重发 | PendingPhoto 队列保留；Brain 收 photo.asset_uploaded 后 dequeue | 同上 |
| Brain "评论" 触发 | IntentWorkspace.stage 后 LLM 下一 turn 自动看到 | selection-C |
| 工具柜按钮占位 | 紫色方块 + "📷 PHOTO" 文字 | master_audit §6.4 |

**TODO 注释草稿**：
```csharp
// TODO(S3-photo-button-baseline): 工具柜拍照按钮 UI 入口 (NEED-P2.5-B 一部分)
//   - 占位: 紫色方块 + 像素文字；最终 sprite 见 master_audit §6.4 Class 4 #4.7
//   - 已有能力: PhotoController.CapturePhoto (Phase 4 W8 21 测试)
//   - 名词索引: 接口设计文档 §2.1 "5 LiveKit DataChannel topic"
//   - Skill: livekit-unity-video-publish/IMPL_REF.md §6
//   - 决策表: 接口设计文档 §4.5 Photo 数据通道
```

---

### §5.4 S4 — Plan + Nanobot 长任务（**Chat 4 4-A 主场**）

**子任务清单**：
- T4.1 LLM 调 dispatch_task / 自动建 Plan（Plan 内 step 等价 NanobotTask）
- T4.2 PlanRegistry.start_executing → 真调 do_dispatch_task(plan_id, step_id, result_channel)
- T4.3 scheduler `nodes.DispatchToNanobot` 把 plan_id / step_id 写 BB `scheduler/active_tasks`
- T4.4 Nanobot 执行 → publish to `parrot.nanobot.results`
- T4.5 scheduler `service._listen_nanobot_results` 取 plan_id / step_id → call `PlanRegistry.report_step_result`
- T4.6 timeout 路由 = service._check_timeouts 同样路径
- T4.7 nanobot heartbeat HSET（NEED-P2.5-NANOBOT-HEARTBEAT）
- T4.8 archive_to_graphiti 真 LLM 蒸馏（NEED-P2.5-ARCHIVE-LLM）

**已有能力索引**：
- ✅ `brain/plan/{plan,plan_registry,plan_blackboard,plan_lifecycle}.py` 8 状态机
- ✅ `scheduler/{nodes.py:DispatchToNanobot, service.py:_listen_nanobot_results, _check_timeouts}`
- ✅ `nanobot/channels/parrot_bus.py` (HKUDS fork)
- ✅ Plan 11/11 测试 + dispatch chain 集成测试

**缺口接口**（Chat 4 4-A 主场）：
- ❌ NEED-P2.5-PLAN-INTEGRATION（5 项 plan-* TODO）
- ❌ NEED-P2.5-NANOBOT-HEARTBEAT（writer 缺）
- ❌ NEED-P2.5-ARCHIVE-LLM（真 LLM 蒸馏）
- ❌ TODO(Chat4-disk-recover)（DiskBackend.recover()）

**函数签名草稿**：
```python
# src/parrot/brain/plan/plan_registry.py (existing; 改 start_executing)
class PlanRegistry:
    async def start_executing(self, plan_id: str) -> None:
        plan = self._plans[plan_id]
        for step in plan.steps:
            if step.state != StepState.READY:
                continue
            # ❌ 当前: step.state = DISPATCHED  (仅标)
            # ✅ TODO: 真调 do_dispatch_task
            task_id = await do_dispatch_task(
                task_type=step.expected_tool,
                params={**step.params, "plan_id": plan_id, "step_id": step.step_id,
                        "result_channel": "parrot.nanobot.results"},
                priority="normal",
            )
            step.nanobot_task_id = task_id
            step.state = StepState.DISPATCHED
            # update BB scheduler/active_tasks 内 plan_id/step_id mapping (新增)

    async def report_step_result(
        self, plan_id: str, step_id: str, success: bool, error: str = "",
    ) -> None: ...  # existing
```

```python
# src/parrot/scheduler/service.py (existing; 改 _listen_nanobot_results)
async def _listen_nanobot_results(self):
    async for msg in self._pubsub.listen():
        # ❌ 当前: 仅 update BB scheduler/last_nanobot_result
        # ✅ TODO: 取 plan_id/step_id (从 active_tasks 反查)
        active = self._bb.get("scheduler/active_tasks") or {}
        task_meta = active.get(msg.task_id) or {}
        plan_id = task_meta.get("plan_id")
        step_id = task_meta.get("step_id")
        if plan_id and step_id:
            from parrot.brain.plan.plan_registry import get_plan_registry
            await get_plan_registry().report_step_result(
                plan_id, step_id,
                success=msg.status == "completed",
                error=msg.error or "",
            )
```

**How TODO**：
| 决策点 | 推荐 | 依据 |
|:--|:--|:--|
| plan_id / step_id 走 Redis Stream payload | 顶层字段（不动 wire schema 顶层 — 旧 task payload 是 free dict）| `cross_chat_pending_registry §3.B` |
| BB key | `scheduler/active_tasks` 内每个 task_id mapping `{plan_id, step_id, dispatched_at}` | `bb_schema.py` 既存 key + namespace |
| nanobot heartbeat | HSET `parrot:nanobot_heartbeat` `<worker_id>` `<ts_ms>` 周期 60s | `cross_chat_pending_registry §3.C` |
| archive_to_graphiti 真蒸馏 | 读 jsonl → unified_filter → LLM Gemini Flash 蒸馏 → Graphiti.add_episode | `cross_chat_pending_registry §3.D` |
| timeout 路由 | service._check_timeouts → report_step_result(success=False, error="timeout after Ns") | 同 §3.B |

**TODO 注释草稿**：
```python
# TODO(Chat4-plan-dispatch): NEED-P2.5-PLAN-INTEGRATION step 1 - start_executing 真调 dispatch_task
#   - 当前: step.state = DISPATCHED (仅标)
#   - 已有能力: do_dispatch_task / scheduler.DispatchToNanobot / parrot_bus.py
#   - 名词索引: 接口设计文档 §2.2 "Plan vs NanobotTask"
#   - Skill: nanobot/SKILL.md + livekit-agents/SKILL.md
#   - 决策: 接口设计文档 §5.4 函数签名草稿 1-2 + §4.4 Plan 状态机
#   - 配套 TODO: TODO(Chat4-plan-step-result-route) + TODO(Chat4-plan-step-timeout) + TODO(Chat4-plan-bb-namespace)

# TODO(Chat4-plan-step-result-route): 同上 step 2 - service._listen_nanobot_results 路由 report_step_result
#   - 配套 BB: scheduler/active_tasks 内 plan_id/step_id mapping (新建 + bb_schema 注册)

# TODO(Chat4-archive-llm): NEED-P2.5-ARCHIVE-LLM - 真 LLM 蒸馏 + Graphiti.add_episode
#   - 当前: archive_to_graphiti 仅计数
#   - Skill: graphiti/SKILL.md (add_episode + group_id 分区)
#   - 决策: 接口设计文档 §4.4 Plan 状态机 + ConversationBoundary

# TODO(Chat4-nanobot-heartbeat): NEED-P2.5-NANOBOT-HEARTBEAT - 心跳 HSET writer
#   - 实施位置: parrot.bus.nanobot_consumer 或 nanobot/channels/parrot_bus.py
#   - 周期: 60s; key: parrot:nanobot_heartbeat; field: <worker_id>; value: ts_ms
```

---

### §5.5 S5 — Plan UI wire（**BLOCKED-BY-NEW-ADR**，建议占位 stub）

**子任务清单（占位 stub 版）**：
- T5.1 Sub-Chat A 的 UI 流程文档写"占位 stub UI"流程
- T5.2 PlanRegistry.submit_for_confirmation 当前由调用方直接 approve()；保留 fallback 不实施
- T5.3 P3 wire ADR chat 真升级（含 NEED-P3-A body_state 解锁同 ADR）

**已有能力索引**：
- ✅ Plan 8 状态机；test_plan_lifecycle 11/11
- ✅ DRAFT → AWAITING_USER_CONFIRMATION → APPROVED 路径（仅程序内）

**缺口接口**：
- ❌ TODO(P3-Wire-PlanUI) 整套（新 EcpEventType + Unity DTO + UI + EcpCommand 回流）

**函数签名草稿（占位）**：
```python
# 当前: PlanRegistry.submit_for_confirmation -> AWAITING_USER_CONFIRMATION
# 占位: 立即调 approve() (调用方手动)
# 真升级: P3 wire ADR chat

# Future EcpEventType 占位（不实施；不动 enum）：
# class EcpEventType(...):
#     PLAN_PROPOSED = "plan.proposed"  # P3 ADR 后启用
#     PLAN_APPROVED = "plan.approved"
#     PLAN_REJECTED = "plan.rejected"
#     PLAN_REVISED  = "plan.revised"
```

**How TODO**：
| 决策点 | 推荐 |
|:--|:--|
| Sub-Chat A 占位策略 | "Plan UI 现以列表 + Approve 按钮 stub UI 占位；用户点 Approve = 调用方在程序内 approve()" |
| 不能动 wire | 严守 Phase 4 §8 L1-L13 锁；P3 ADR 之前不加 EcpEventType |

**TODO 注释草稿**：
```python
# TODO(P3-Wire-PlanUI): Plan 用户确认 wire 信号
#   - 当前: submit_for_confirmation 由调用方直接 approve() (test_plan_lifecycle 守)
#   - 真升级: 新 EcpEventType (plan.proposed/approved/rejected/revised) + Unity Plan card UI + EcpCommand 回流
#   - 触动 Phase 4 §8 wire 锁 → 必须新 ADR (建议与 NEED-P3-A body_state 解锁同 ADR)
#   - 修复 chat: P3 wire 升级 ADR chat
```

---

### §5.6 S6 — 4 类块菜单画布（**核心验证 — 不在本文实施，预留接口契约**）

**子任务清单（接口契约 only）**：
- T6.1 4 active BB key 注册（model / persona / mode / scene）
- T6.2 4 注册表（ModelManifestRegistry 已存在 / persona_loader NEED-P2.5-A / mode_watcher 已存在 / SceneRegistry 已存在）
- T6.3 预设 schema `data/presets/<id>.json`
- T6.4 Unity menu UI（占位列表 + 节点画布 P3）

**已有能力索引**：
- ✅ Model 块（GOSLO mod 完成）：ModelManifest + ModelDriver + ParrotRegistry + asset_to_manifest CLI + EcpCommand.meta["model_id"]
- ✅ Mode 块：BehaviorMode 5 flags + set_mode tool + mode_watcher
- ✅ Scene 块：SceneType + SceneProfile + SceneRegistry + SceneSwitchOutcome

**缺口接口**：
- ❌ Persona 块（NEED-P2.5-A 推 DSG 协议升级 chat）
- ❌ NEED-P3-B 4 类块统一注册表
- ❌ NEED-P3-C 预设 schema
- ❌ NEED-P3-D node-canvas UI
- ❌ NEED-P3-E 默认 fallback

**函数签名草稿（推到 DSG 协议升级 chat 真设计）**：
```python
# src/parrot/shared/preset.py (NEW; deferred to DSG 协议升级 chat)
class Preset(BaseModel):
    preset_id: str
    active_model_id: str = "GOSLO_default"
    active_persona_id: str = "goslo_parrot_default"
    active_mode: list[str] = ["BASE", "COMPANION"]  # BehaviorMode flags
    active_scene_id: str = "main_scene"

class PresetLoader:
    def load(preset_id: str) -> Preset: ...
    def apply(preset: Preset) -> None:  # 写 4 个 BB key
        ...
```

**How TODO**：
| 决策点 | 推荐 |
|:--|:--|
| 本文不真设计 schema | DSG 协议升级 chat 主场；本文仅 inventory + 接口契约 |
| 4 个 BB key 命名 | `global/active_{model_id, persona_id, scene_id}` + `global/active_mode`（list） | `requirements.md §四 G`（既有命名约定）|
| 切换事件 | 写 BB → mode_watcher 模式 触发 | 已有 mode_watcher 范式 |

**TODO 注释草稿**：
```python
# TODO(NEED-P3-B): 4 类块统一注册表 (model / persona / mode / scene)
#   - 推 DSG 协议升级 chat (与 NEED-P2.5-A persona 外置 + NEED-P3-C 预设 schema 一锅端)
#   - 已有能力: 3/4 块齐 (Model/Mode/Scene); Persona 缺
#   - 名词索引: 接口设计文档 §2.3 "Persona vs Mode vs Model"
#   - 决策表: 接口设计文档 §5.6 (本节)
```

---

### §5.7 S7 — LineA ↔ LineB 切换（已 PASS 结构性，待 6-axis 联机）

**子任务清单**：
- T7.1 env-gate `PARROT_LLM_PIPELINE` 切换（已实施）
- T7.2 transcript_extractor pipeline-agnostic + 旧名 alias 保留（已实施）
- T7.3 6-axis Editor 联机双跑 smoke（pending — LineB Editor smoke chat）
- T7.4 axis-5 DSG 文本提取层稳定性 verify（FINDING-LB-3）

**已有能力索引**：
- ✅ `brain/agent.py:_build_session(pipeline,config) + _resolve_pipeline()`
- ✅ `dsg/ingest/transcript_extractor.py` + `gemini_transcript_extractor.py` alias shim
- ✅ ObservationSource 7 entries verbatim
- ✅ 234/234 pytest baseline

**缺口接口**：无新接口；CC-3 + LineB Editor smoke chat 处理

**TODO 注释草稿**：
```python
# TODO(S7-line-b-editor-smoke): LineB Editor 6-axis 联机双跑 smoke
#   - 不在本文实施; 推 LineB Editor smoke chat
#   - 6 axis: cognitive_state 时序 / selection-C reason / identify_object 1.9s 预算 / attention.threshold.crossed / DSG 文本提取层稳定性 / Multi-Agent Handoff
#   - finding 锚点: lineb_implementation_completion_20260504 §5
```

---

### §5.8 S8 — 场景切换 + 永久权威 Bucket + 对话延迟归档

**子任务清单**：
- T8.1 SceneSwitchTrigger fire（用户主动切 / DSG 检测）
- T8.2 IntentEventBoundaryHandler.switch_scene → BucketRegistry freeze 永久 / clear fresh
- T8.3 ConversationBoundary 多信号 OR → Archive.dispatch 序列化 jsonl
- T8.4 IdleArchiveTrigger（nanobot 心跳就绪后）→ unified_filter + LLM 蒸馏 → Graphiti.add_episode
- T8.5 4 active BB key（global/active_scene_id）切换通知

**已有能力索引**：
- ✅ DSG Chat 2 全套（118 测试）：SceneRegistry / IntentEventBoundaryHandler / Archive 3-Phase / ConversationBoundary / IdleArchiveTrigger

**缺口接口**：
- ❌ TODO(P3-multi-scene)：多 SceneType profile（HOME_INDOOR / OUTDOOR / LIBRARY / KITCHEN）
- ⚠ NEED-P2.5-NANOBOT-HEARTBEAT（场景 4 主场；S8 受影响）
- ⚠ NEED-P2.5-ARCHIVE-LLM（场景 4 主场；S8 受影响）

**函数签名草稿**：基本无新增；用 DSG Chat 2 已落

**How TODO**：
| 决策点 | 推荐 | 依据 |
|:--|:--|:--|
| Bucket TTL 永久 vs fresh | 4 永久（OBSIDIAN_REFERENCE_REINFORCE / SETTING_DAILY / SETTING_ROLEPLAY / IDENTIFY_OBJECT_RESULT）+ 2 fresh（GEMINI_ORAL_MENTION / AUTONOMOUS_CURIOSITY） | `protocol_snapshot_p4 §18` |
| Scene 是否主导 L2-B 拓扑 | **否**（Scene = L1.5 管理面 + 节点字段；L2-B 拓扑由 IntentEvent 驱动） | `dsg_protocol_scene_snapshot_v1 §3` |
| 多 SceneType profile | TODO(P3-multi-scene)；A10 + VPS | 推 P3 / A10 接入 chat |

**TODO 注释草稿**：
```python
# TODO(P3-multi-scene): 多 SceneType profile (HOME_INDOOR / OUTDOOR / LIBRARY / KITCHEN)
#   - 当前: SceneRegistry 仅 DESKTOP profile
#   - 名词索引: 接口设计文档 §2.2 "Scene"
#   - Skill: dsg-rustworkx-master + dsg-l1-5-l2a-conceptgraph-distilled (A10 入口)
#   - 决策: 接口设计文档 §4.2 AdmissionPolicy + §5.8
#   - 推 P3 / A10 接入 chat
```

---

### §5.9 S9 — HUD / 工具柜交互（增补；UI 流程 + 持久化）

**子任务清单**：
- T9.1 HUD 收纳态 + 横/竖向展开（用户选择方向）
- T9.2 工具柜对角放置 + 横/竖向展开
- T9.3 用户偏好持久化（横/竖向 / HUD 开关 / 工具柜开关）`PlayerPrefs`
- T9.4 道具 P0：放大镜 + 注意力框 + 任务按钮 + 设置 + 拍照按钮 + 2D 工作区入口

**已有能力索引**：无（全部新建）

**缺口接口**：全新 Unity UI 模块

**函数签名草稿（Unity C#）**：
```csharp
// unity/ArSpike/Assets/Scripts/ParrotApp/Hud/HudController.cs (NEW)
public class HudController : MonoBehaviour {
    public enum ExpandDirection { Horizontal, Vertical }
    public ExpandDirection direction;  // 用户在启动页选择
    public void Toggle();
    public void SetDirection(ExpandDirection dir);
}

// unity/ArSpike/Assets/Scripts/ParrotApp/Toolbar/ToolbarController.cs (NEW)
public class ToolbarController : MonoBehaviour { ... }  // 同 HudController 模式

// unity/ArSpike/Assets/Scripts/ParrotApp/Toolbar/Tools/{MagnifierTool, AttentionBoxTool, PhotoButtonController, ...}.cs (NEW per tool)
```

**How TODO**：
| 决策点 | 推荐 | 依据 |
|:--|:--|:--|
| HUD 显示位置 | 屏幕一角；具体 corner 由用户选 | `ar_app_flow_ui_design §6` |
| 自动横竖屏切换 | **否**（用户手动选方向，避免自动适配复杂度） | 同上 + 用户原话 |
| 工具柜对角 | 与 HUD 对角；4 corner 选 1 | 同上 |
| 持久化 | PlayerPrefs（baseline）；P3 升级 ScriptableObject + JSON | 简单 |

**TODO 注释草稿**：
```csharp
// TODO(S9-hud-toolbar-baseline): HUD + 工具柜布局基线
//   - 占位策略: 紫色方块 + 文字按钮; 最终 sprite 见 master_audit §6.2 + §6.3
//   - 用户偏好: 横/竖向展开方向 + HUD/工具柜开关持久化 PlayerPrefs
//   - 名词索引: 接口设计文档 §2.4 "AppLifecycleState 11 态 FSM"
//   - Skill: 无 (Unity Editor 自建)
//   - 决策: 接口设计文档 §5.9 + ar_app_flow_ui_design §6-§7
```

---

### §5.10 S10 — 视频档位 + 音频路由的运行时调节

**子任务清单**：
- T10.1 set_video_tier tool（已存在）+ Unity setVideoTier RPC handler 已存在
- T10.2 PerceptionSupervisor 自动调节（A10 状态 / 视频降级 → 静默 Intent）
- T10.3 工具柜"相机模式"按钮（用户主动切档）
- T10.4 蓝牙 / 耳机插拔（livekit-unity-lifecycle skill 覆盖）

**已有能力索引**：
- ✅ Brain `tools/set_video_tier.py`
- ✅ Unity `LiveKit/VideoTierReceiver.cs` + `MicrophonePublisher.cs`
- ✅ `livekit-unity-lifecycle/SKILL.md` + `livekit-unity-video-publish/SKILL.md`

**缺口接口**：
- ❌ 工具柜"相机模式"UI（NEED-P2.5-B / S9 子任务）
- ⚠ PerceptionSupervisor 仍是浅版本（Sprint3 hold_seconds=300 是 P2.5 baseline）

**函数签名草稿（Unity C#）**：
```csharp
// unity/ArSpike/Assets/Scripts/ParrotApp/Toolbar/Tools/CameraModeTool.cs (NEW)
public class CameraModeTool : MonoBehaviour {
    public void OnTierVideoOff();    // → set_video_tier(VIDEO_OFF)
    public void OnTierGeminiOnly();  // → VIDEO_GEMINI_ONLY
    public void OnTierFull();         // → VIDEO_FULL
}
```

**How TODO**：
| 决策点 | 推荐 | 依据 |
|:--|:--|:--|
| 用户主动切档 vs 自动 | 双路并存；用户优先（hold_seconds=300）| Sprint3 D1 |
| 切档同步 / 异步 | 同步等 Unity ack（GOSLO 自身 Intent 行为） | parrot_behavior_rules §4.3 |
| 蓝牙 / 耳机 | livekit-unity-lifecycle skill 覆盖；本文不重复 | — |

**TODO 注释草稿**：
```csharp
// TODO(S10-camera-mode-toolbar): 工具柜相机模式按钮 (NEED-P2.5-B 一部分)
//   - 已有能力: VideoTierReceiver + set_video_tier tool
//   - Skill: livekit-unity-video-publish/SKILL.md §三 + §四 + livekit-unity-lifecycle/IMPL_REF.md §6
//   - 决策: 接口设计文档 §5.10 + §4.6 三层调度 (Intent 行为, 同步等 ack)
```

---

### §5.11 S11 — Brain tool 全集合 + capability gating

**子任务清单**：
- T11.1 现存 tool 健全性（11 项；详见已有能力）
- T11.2 capability gating（NEED-P3-CAPABILITY-GATING）
- T11.3 manage_episode tool 验证（lineb axis-7 备用）

**已有能力索引**：
- ✅ 11 个 tool：fly_to / animate / set_video_tier / capturePhoto / dispatch_task / remember / query_memory / query_scene / set_mode / identify_object / manage_episode

**缺口接口**：
- ❌ NEED-P3-CAPABILITY-GATING：Brain 启动时按 active model manifest `declared_capability_ids` 过滤 tool 注册（如非飞行模型 → 不注册 fly_to）
- ⚠ identify_object 默认未注册（PARROT_ENABLE_IDENTIFY_OBJECT_TOOL=1 开启）

**函数签名草稿**：
```python
# src/parrot/brain/agent.py:_register_tools (existing; capability gating 增量)
async def _register_tools(session, model_manifest_registry):
    active_model_id = bb.get("global/active_model_id") or "GOSLO_default"
    manifest = model_manifest_registry.get(active_model_id)
    declared = manifest.declared_capability_ids if manifest else None  # None = 全注册 fallback

    for tool in ALL_TOOLS:
        capability_id = tool.metadata.get("capability_id")  # tool 自报 capability
        if declared is None or capability_id is None or capability_id in declared:
            session.register_tool(tool)
```

**How TODO**：
| 决策点 | 推荐 | 依据 |
|:--|:--|:--|
| 哪些 tool 关联 capability | fly_to → "fly" / animate → "dance|wing_flap|head_bob|..." | `protocol_snapshot_p4 §11 ParrotAnimation 8 项` |
| 默认 GOSLO_default | 全 8 项都声明；fallback 全注册 | `goslo_default.json` |
| Chat 4 4-A 是否做 | Chat 4 增量（5-15 行 + 1 测试） | `cross_chat_pending_registry §4.F` |

**TODO 注释草稿**：
```python
# TODO(NEED-P3-CAPABILITY-GATING): Brain 启动时 tool 按 manifest 过滤
#   - 名词索引: 接口设计文档 §2.3 "Persona vs Mode vs Model" + goslo_model_manifest_protocol_v1 §3.6 declared_capability_ids
#   - 已有能力: ModelManifestRegistry (Brain 端副本未建; Chat 4 增量)
#   - 决策: 接口设计文档 §5.11
#   - 推: Chat 4 4-A 增量 (5-15 行 + 1 测试)
```

---

### §5.12 S12 — DSG 4 legacy 触发器自主行为

**子任务清单**：
- T12.1 CalendarTrigger（日程提醒三层 digest/prep/imminent + quiet hours + cooldown）— 已存在
- T12.2 MessageNotificationTrigger（Gmail 重要消息 + episode_id 防冲突）— 已存在
- T12.3 SsotEnrichmentTrigger（Obsidian 充实物体 + L2-B 节点更新）— 已存在
- T12.4 SceneContextTrigger（场景上下文 → notify_gemini）— 已存在

**已有能力索引**：
- ✅ `dsg/triggers/{calendar,message,scene_context,ssot_enrichment}_trigger.py` (4 legacy)
- ✅ TriggerOutcome V2 5 路上行 + alias 兼容

**缺口接口**：
- ⚠ Google OAuth 真实联调（CalendarTrigger / MessageTrigger 需用户账号授权）
- ⚠ TriggerRunner 真启动到 agent.py（Phase 5 已修；Sprint 4 走通）

**TODO 注释草稿**：
```python
# TODO(S12-google-oauth-real-link): CalendarTrigger / MessageTrigger 真 OAuth 联调
#   - 当前: 配置就绪 (deploy_snapshot_p2_20260412)
#   - 缺: 用户账号授权未做 (P2 收尾延期)
#   - 名词索引: 接口设计文档 §2.2 "5 路 TriggerOutcome V2"
#   - Skill: graphiti/SKILL.md (写入路径)
#   - 推: 真机 spike chat / P2 收尾
```

---

### §5.cc1 CC-1 — Echo 全链路（数据流安全策略）

**子任务清单**：
- TCC1.1 Unity `ParrotAttentionConfig` SO 阈值（已存在）
- TCC1.2 `AttentionConfigEchoPublisher` 在 RoomManager.OnConnected（含 reconnect / 管线切换）publish `attention.config.echo`（已存在）
- TCC1.3 Brain `attention_config_handler` 写 BB `global/attention_thresholds`（已存在）
- TCC1.4 `FocusBboxThreshold.__init__` sentinel-None 读 BB 覆盖 DEFAULTS（已存在）
- TCC1.5 ContextMenu 兜底（已存在）

**已有能力索引**：全套已 ratified（Phase 4 W6-7 + F-05 fix）

**缺口接口**：
- ⚠ freeze test 增量：cs_parity 守 attention.config.echo 字段 schema_version=1 + delta_focus / delta_bbox / threshold / target_ttl_s 4 字段

**TODO 注释草稿**：
```python
# TODO(CC-1-echo-freeze-test): Echo 全链路 freeze test 守护
#   - 当前: cs_parity 4/4 守 EcpEventTypeNames + EcpEventSourceNames + topic + DTO 文件存在
#   - 增量: 守 attention.config.echo payload 字段集 (schema_version=1 + 4 数值字段)
#   - 推: Chat 4 4-C freeze test 扩展项
```

---

### §5.cc2 CC-2 — 重连 / 切后台 / handoff（lifecycle 防御）

**子任务清单**：
- TCC2.1 11 态 FSM + R1-R6+D5 audit 已修
- TCC2.2 OnApplicationPause 切后台短/长策略
- TCC2.3 30s ICE 残留防御 + identity 抢占
- TCC2.4 ARCore 黑帧 / pause-resume crash 缓解
- TCC2.5 audio route policy（蓝牙 baseline）

**已有能力索引**：
- ✅ 全 `livekit-unity-lifecycle/SKILL.md` + `IMPL_REF.md` 范围内已实施

**缺口接口**：
- ⚠ 真机 spike 验证（P2.5 真机 spike chat）
- ⚠ 2026-05-09 ChatA 修订：Bluetooth 已进入正式 App 支持范围；仍需真机验证蓝牙 / 手机麦克风往返切换不导致 LiveKit room 崩溃。

**TODO 注释草稿**：
```csharp
// TODO(CC-2-real-device-spike): 真机 spike 验证 11 态 FSM + R1-R6+D5
//   - Skill: livekit-unity-lifecycle/IMPL_REF.md §1-§5
//   - 决策: 接口设计文档 §5.cc2
//   - 推: P2.5 真机 spike chat
```

---

### §5.cc3 CC-3 — 8KB 拒收 / 60s dedup / oversize synthesized event

**子任务清单**：
- TCC3.1 event_ingest.py 已实施 8KB + 60s dedup + synthesized event.rejected.oversize
- TCC3.2 freeze test：8KB 拒收路径 + dedup 路径 + synthesized 路径覆盖率
- TCC3.3 cs_parity 守 EcpEventTypeNames 含 `event.rejected.oversize`

**已有能力索引**：✅ 全实施

**缺口接口**：无；CC-3 = 测试覆盖率守护

**TODO 注释草稿**：
```python
# TODO(CC-3-event-ingest-coverage): event_ingest 8KB / dedup / synthesized 测试覆盖
#   - 当前: 实施完成 (Phase 4 §8 L2 + L3)
#   - 增量: 测试覆盖率 audit (Sub-Chat B 验证)
#   - Skill: 直接看 src/parrot/brain/event_ingest.py
```

---

### §5.cc4 CC-4 — Reflex / Intent / Task 三层调度边界

**子任务清单**：
- TCC4.1 Scheduler 浅 Selector（4 叶 + 3 leaf 已实施）
- TCC4.2 Reflex 子树新增（手势 perch_to_finger 走 Unity 本地 + 紧急避障 P3）
- TCC4.3 Intent 不被 Task 阻塞（dispatch_task 立即返回 task_id）
- TCC4.4 完整 BT 森林（Safety / Priority / Parallel / Idle）= E4 P3+ 扩展

**已有能力索引**：
- ✅ `scheduler/{router,bt_router,bt_nodes,blackboard}.py` + py-trees BT
- ✅ `parrot_behavior_rules.md §0-§8` 行为规则

**缺口接口**：
- ⚠ Reflex 子树 Unity 端（S1.5 perch_to_finger 子任务）
- ⚠ ResourceLockManager 骨架（E5 P2 任务；不阻塞 Phase 4）

**TODO 注释草稿**：
```python
# TODO(CC-4-reflex-tree-unity): Reflex 子树 Unity 本地 (perch_to_finger 等)
#   - 当前: Reflex 在 scheduler.router.HandleReflex (Python 端浅版本)
#   - 升级: Unity 本地直接派发 EcpCommand (绕 Brain LLM)
#   - 名词索引: 接口设计文档 §2.3 "Reflex / Intent / Task" + parrot_behavior_rules §0.1
#   - 关联子任务: TODO(S1.5-perch-to-finger)
#   - Skill: py-trees/SKILL.md + livekit-unity-lifecycle/IMPL_REF.md §6
```

---

## §6 跨场景接口（Sub-Chat A + B 共享 binding 表）

> Sub-Chat A 用本表"Unity 端 → 后端"列；Sub-Chat B 用本表"后端 → Unity 端 + 跨模块"列。

### §6.1 Unity 端事件 → Brain 端点 mapping

| Unity 事件 | EcpEvent type / RPC | Brain 端点 | BB key 写入 |
|:--|:--|:--|:--|
| 用户拖动 BBox | `parrot.ecp.tick` lossy | (drop) | — |
| 用户放置 BBox | EcpEvent `bbox.placed` reliable | `observer/bbox._on_bbox_placed` → refs.bind → threshold._add_weight | `transient/current_attention_hint`（达阈值） |
| 用户拖动 Focus | `parrot.ecp.tick` lossy | (drop) | — |
| 用户锚定 Focus | EcpEvent `focus.anchored` reliable | `observer/focus._on_focus_anchored` | 同上 |
| Unity capture snapshot | EcpEvent `snapshot.captured` reliable | `observer/snapshot` → 转 BB transient | `transient/last_snapshot_event` |
| Unity 拍照 preview | EcpEvent `photo.taken_preview` reliable | `observer/photo` → upsert PhotoNode | `transient/last_photo_event` |
| Unity 拍照 asset | HTTP POST `/upload/photo/{id}` | `photo_upload_server` → publish `photo.asset_uploaded` | — |
| Unity Echo 阈值 | EcpEvent `attention.config.echo` reliable | `attention_config_handler` | `global/attention_thresholds` |
| Unity 手势识别 | EcpEvent `gesture.recognized` reliable + telemetry | (reserve; Phase 4 走 telemetry) | — |
| Unity intent disconnect | inline envelope `parrot.ecp.intent_disconnect` | brain handler graceful | `session/connection_health` |
| Unity 连接 health 变化 | inline envelope `parrot.ecp.health` | brain handler | `session/connection_health` |
| Unity EcpState 心跳 | `parrot.ecp.state` 1Hz / 事件 | `ecp_state_ingest.py` | `session/ecp_state` |

### §6.2 Brain 端 → Unity RPC（同步）

| Brain tool / 来源 | RPC method | Unity handler | EcpAck 5 态 |
|:--|:--|:--|:--|
| `brain.tools.fly_to` | `flyTo` | `ParrotRpcHandler.HandleFlyTo` → ParrotController.FlyTo(target, modelId) | applied / rejected / timeout / no_target / unchanged |
| `brain.tools.animate` | `animate` | `HandleAnimate` → PlayAnimation(name, modelId) | 同 |
| `brain.tools.set_video_tier` / PerceptionSupervisor | `setVideoTier` | `HandleSetVideoTier` → VideoTierReceiver | 同 |
| `brain.tools.identify_object` 内部 | `captureSnapshot` | `HandleCaptureSnapshot` (800ms budget) | 同 |
| `brain.tools.capturePhoto`（即将；当前 user 触发）| `capturePhoto` | `PhotoController.CapturePhoto` | 异步（preview + asset HTTP） |

### §6.3 跨模块 binding（DSG triggers → 5 路上行）

| Trigger 输出通道 | 下游模块 | 接口方法 |
|:--|:--|:--|
| `commit_observations` | L1.5 Pool | `Pool.admit(observation)` → IngestRunner |
| `bucket_ops` | BucketRegistry | `BucketRegistry.apply(op)` |
| `staged_refs` | IntentWorkspace | `IntentWorkspace.stage(staged_ref)` |
| `archive_request` | Archive | `Archive.dispatch(request)` |
| `plan_request` | PlanRegistry | `PlanRegistry.draft(proposal)` |
| `dispatch_to_nanobot`（legacy V1）| Scheduler + Nanobot | `do_dispatch_task(...)` |
| `notify_gemini`（legacy V1）| Brain Context Injector | `inject_to_session_context(...)` |

---

## §7 推荐执行顺序（Sonnet 4.6 工作单）

> 不是绝对路径；是**建议的并发 + 串行**编排，给 Sonnet 4.6 做"先做什么 / 等什么完成再做什么"的指引。

```
Phase A — 并发（无外部依赖；Sonnet 4.6 第一周）
├── S1 baseline 健全性（无新代码；只 audit fly_to / animate 链路 + selection-C）
├── S7 LineA / LineB 切换（已实施；Sub-Chat B 验证 7 ObservationSource verbatim）
├── S12 4 legacy 触发器（已实施；Sub-Chat B 验证 5 路上行）
├── CC-1 Echo 全链路（已实施；Sub-Chat B 加 freeze test）
├── CC-3 event_ingest 守护（已实施；Sub-Chat B 加测试覆盖）
└── §2 名词概念 + §3 Skill 表 + §4 算法表（Sonnet 4.6 通读 + 写到自己的 cog 里）

Phase B — Chat 4 4-A 主场（Sonnet 4.6 第二周；上 Phase A 完成后）
├── TODO(Chat4-plan-dispatch) → start_executing 真调（S4 / NEED-P2.5-PLAN-INTEGRATION 1/4）
├── TODO(Chat4-plan-step-result-route) → service 路由 (S4 / 2/4)
├── TODO(Chat4-plan-step-timeout) (S4 / 3/4)
├── TODO(Chat4-plan-bb-namespace) (S4 / 4/4)
├── TODO(Chat4-archive-llm) → archive_to_graphiti 真蒸馏 (S4 / NEED-P2.5-ARCHIVE-LLM)
├── TODO(Chat4-nanobot-heartbeat) → HSET writer (S4 / NEED-P2.5-NANOBOT-HEARTBEAT)
└── TODO(Chat4-disk-recover) → DiskBackend.recover() (S4 配套)

Phase C — Unity UI baseline（Sonnet 4.6 第二周并发）
├── S0 启动页菜单 5 项 baseline
├── S9 HUD + 工具柜 baseline (横/竖向 + 持久化)
├── S3 拍照按钮 (S9 子任务)
├── S10 相机模式按钮 (S9 子任务)
└── S1.5 perch_to_finger Reflex 迁移 ParrotDev → ArSpike

Phase D — 增量 / 守护（任意时机）
├── CC-2 真机 spike 准备（不实施；推 P2.5 真机 spike chat）
├── S11 capability gating 增量（Chat 4 4-A 末段）
└── S5 占位 stub UI（Sub-Chat A 文档；不实施 wire）

Phase E — 推下游（不在 Sonnet 4.6 范围）
├── S6 4 类块菜单画布 → DSG 协议升级 chat
├── S5 Plan UI wire → P3 wire ADR chat
├── S8 多 SceneType profile → P3 / A10 接入 chat
└── S2 A10 真识别 → A10 接入 chat
```

---

## §8 风险与边界（Sonnet 4.6 不要碰的硬约束）

1. **不动 wire / enum / BB key**（Phase 4 §8 13 锁 + cs_parity 4/4 + ADR-L1.5-001）
2. **不发明新 NEED-* 标签**（cross_chat_pending_registry §3 / §4 是真源）
3. **不做 P3 / A10 范围内的事**（fold-bionic / spreading / RefHealth / multi-scene / Castle↔Mecha）
4. **不重写 SSOT**（protocol_snapshot_p4 / module_map_p4_snapshot / 3 完成报告 / cross_chat_pending_registry / ADR）
5. **不设计 4 类块 schema**（NEED-P3-B/C — 推 DSG 协议升级 chat）
6. **不升 Plan UI wire**（NEED-P3-Wire-PlanUI — 推 P3 wire ADR chat）
7. **不动 Phase 4 §8 13 锁**（特别 L1 NodeKind/EdgeKind / L2 EcpEvent 字段集 / L9 attention 阈值器位置）
8. **不破** ParrotAnimation 8 / ParrotBodyState 6 / BehaviorMode 5 / NodeKind 6 / EdgeKind 8 / ObservationSource 7+1 / EcpEventType 13 任何 enum
9. **不改 livekit-unity-lifecycle 行为**（11 态 FSM 已 ratified；只能加测试不能改 FSM）
10. **测试不破 415/415 baseline**（每个 PR 跑一遍 pytest）

---

## §9 已有 TODO 标签 grep 速查（cross-chat-registry → 代码位置）

| 标签 | 代码位置 | 修复 chat |
|:--|:--|:--|
| `TODO(Chat4-archive-llm)` | `dsg/archive/conversation.py:archive_to_graphiti` | Chat 4 4-A |
| `TODO(Chat4-nanobot-heartbeat)` | `dsg/triggers/idle_archive_trigger.py:_is_nanobot_idle` | Chat 4 4-A |
| `TODO(Chat4-plan-dispatch)` | `brain/plan/plan_registry.py:start_executing` + `submit_for_confirmation` | Chat 4 4-A |
| `TODO(Chat4-plan-nanobot-correlation)` | `scheduler/nodes.py:DispatchToNanobot` + `service.py:_listen_nanobot_results` | Chat 4 4-A |
| `TODO(Chat4-plan-step-result-route)` | `scheduler/service.py:_listen_nanobot_results` | Chat 4 4-A |
| `TODO(Chat4-plan-step-timeout)` | `scheduler/service.py:_check_timeouts` | Chat 4 4-A |
| `TODO(Chat4-plan-bb-namespace)` | `scheduler/blackboard.py` | Chat 4 4-A |
| `TODO(Chat4-disk-recover)` | `brain/intent_workspace_backend.py:DiskBackend` | Chat 4 4-A |
| `TODO(P3-Wire-PlanUI)` | `brain/plan/plan_registry.py:submit_for_confirmation` | P3 wire ADR |
| `TODO(P3-RefHealth)` | `dsg/l1_5/ref_table.py:verify_ref` | P3 仿生 |
| `TODO(P3-attention-spreading)` | `dsg/l2b/attention/mechanism.py:SpreadingActivationPlaceholder` | P3 仿生 |
| `TODO(P3-fold-bionic)` | `dsg/l2b/intent_event_boundary.py:NoOpFoldStrategy` | P3 仿生 |
| `TODO(P3-multi-scene)` | `dsg/l1_5/scene_snapshot.py:SceneRegistry` | P3 / A10 |

**快速 grep**：
```bash
rg "TODO\(Chat4-" src/
rg "TODO\(P3-" src/
rg "NEED-P2\.5-" .cursor/memory/architecture/
rg "NEED-P3-" .cursor/memory/architecture/
```

---

## §10 给 Opus 4.7 的补漏 checklist（两个 Sub-Chat 各 1 份）

### §10.1 Sub-Chat A（用户视角）补漏 checklist

- [ ] §1.2 增补场景 S0 / S1.5 / S9 / S10 是否在 `app_flow_requirements_interface_<date>.md` 全覆盖？
- [ ] §1.3 横切关注点 CC-1 / CC-2 是否有用户视角（Echo 失败时 UI 显示？切后台时用户看到什么？）描述？
- [ ] §5 每场景的"占位策略"列在 Sub-Chat A doc 是否有对应章节？
- [ ] §6.1 Unity 事件 → Brain 端点 mapping 是否被 user 流程消费？
- [ ] §7 Phase C UI baseline 子任务是否在 Sub-Chat A doc 章节有对应？

### §10.2 Sub-Chat B（模块视角）补漏 checklist

- [ ] §1.2 S11 capability gating 是否在 Sub-Chat B doc 接口稳定性面有 audit？
- [ ] §1.3 CC-3 event_ingest 守护是否在 Sub-Chat B doc 接口稳定性面有 audit？
- [ ] §5 每场景的"已有能力索引 + 缺口 NEED-* + How TODO" 是否被 Sub-Chat B doc 转译为模块边界视角？
- [ ] §6.3 5 路 TriggerOutcome × 6 下游模块的 binding 表是否被 Sub-Chat B doc 完整列出？
- [ ] §3 Skill 决策表是否被 Sub-Chat B doc 引用作为接口稳定性证据？
- [ ] §4 算法决策表（A vs B）是否在 Sub-Chat B doc 中作为"接口选择依据"陈列？

---

## §11 变更日志

- **2026-05-07 v0**：本文创建。喂给 Sonnet 4.6 实施 + Opus 4.7 调研 + 我在里程碑 Review 用。
  - §1 场景遗漏审查：补 4 增补场景（S0 / S1.5 / S9 / S10 / S11 / S12）+ 4 横切关注点（CC-1 / CC-2 / CC-3 / CC-4）
  - §2 名词概念表：23 项关键术语索引到代码 / SSOT 锚点
  - §3 Skill 决策表：12 个 skill × 16 场景的"读哪一节"映射
  - §4 算法决策表：5 个领域 × 12+ 决策点的"A vs B"
  - §5 12 场景 + 4 横切关注点的接口设计 + 函数签名草稿 + How TODO + TODO 注释草稿（直接抄码）
  - §6 跨场景 binding 表（Unity ↔ Brain ↔ DSG ↔ Scheduler ↔ Nanobot）
  - §7 推荐执行顺序（Phase A-E）
  - §8 硬约束 10 条（Sonnet 4.6 不要碰）
  - §9 已有 TODO 标签 grep 速查
  - §10 Opus 4.7 补漏 checklist 2 份（两个 Sub-Chat 各 1）
