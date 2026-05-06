---
status: stage-1-draft
category: chat-4-stage-1
chat_4_stage: "Stage 1 — 4-B-req"
status_note: "Chat 4 接口提炼 Stage 1 — 需求 inventory。从 67 功能项 + cross-chat-registry NEED-* 12 项 + ar_app_flow_ui_design 隐式需求收口；每项标 Chat 4 处置 + 拓扑边界候选 + driver source。**完全不绑代码**——仅 cite doc anchor。"
last_reviewed: 2026-05-07
authoritative_for: "Chat 4 接口提炼的需求层 SSOT；Stage 2 capabilities_inventory 的输入；Stage 3 接口提炼的 driven_by 真源"
parent_doc: "INDEX.md"
parent_plan: "../architecture/interface_extraction_plan_20260507.md §7.5.3 Stage 1"
ai_priority: high
ai_audience: both
sources:
  - "../requirements.md (67 功能项 + 11 决策)"
  - "../architecture/cross_chat_pending_registry_20260507.md (12 NEED-* 标签)"
  - "../architecture/ar_app_flow_ui_design.md (8 步 App flow + 启动菜单 / HUD / 工具柜 / 注意力工具开放问题)"
  - "../architecture/ar_feature_vision.md (一句话愿景 + 4 核心讨论 + 五维收口)"
  - "../parrot_behavior_rules.md (行为契约 + 红线)"
  - "../architecture/ar_camera_interaction_survey.md (拍照互动调研)"
---

# Chat 4 Stage 1 — 需求 Inventory

> **本文用途**：以**驱动源**视角列出 Chat 4 接口提炼需要覆盖的所有需求条目。**不绑代码**，仅 cite doc anchor。
>
> **使用方式**：Stage 2 (4-B-cap) 拿本文 → 反推能力清单 → 写 capabilities_inventory.md；Stage 3 (4-B-{wire,cross,in}) 拿能力清单 → 反推接口面 → 在每个接口文件 frontmatter `driven_by:` 字段 cite 本文 NEED-XX。
>
> **章节安排**：§1 67 功能项（按 A-H 8 组）→ §2 cross-chat-registry NEED-* 12 项 → §3 隐式需求（来自 ar_app_flow + ar_feature_vision + behavior_rules）→ §4 Chat 4 范围确认 → §5 全表统计

---

## §0 TL;DR

| 维度 | 数 |
|:--|:--|
| §1 requirements.md 67 项 | 67 |
| §2 cross-chat NEED-* | 12 |
| §3 隐式需求（user 流程 / 愿景 / 行为契约提取）| 14 |
| **总需求条目** | **93** |
| 其中 Chat 4 主场（接口面提炼范围） | ~55（含 locked / evolving / experimental / proposed-upgrade / proposed-new）|
| 其中 out-of-scope（推其他 chat / Phase 5+）| ~38 |

**关键观察**：

1. **Phase 1-3 完成的功能 ~50 项** — 大多是 `evolving` 或 `experimental` 状态，需要在 Stage 3 接口面**显式标 status**而不是按"locked"对待
2. **Phase 4 §8 真正 locked 的接口面只有 13 条** — wire 层；其他都是 evolving 或临时实现
3. **真正 proposed-new 接口** — 主要在 P3 菜单画布 / 4 类块 / Plan UI / capability gating（共 ~8 项）
4. **Chat 4 主场窄而深** — 大多 inventory 工作是把"已有但散落"的接口收口；少数是补缺

---

## §1 requirements.md 67 项 inventory

> 来源：[`../requirements.md`](../requirements.md) §四
>
> **格式说明**：
> - `Phase` = 原 requirements.md 标定（1 / 1.5 / 2 / 3 / 3+ / 远期）
> - `Chat 4 处置` = `inventory-only`（仅作 inventory 不动）/ `proposed-upgrade`（既有需升级）/ `proposed-new`（应有但缺）/ `out-of-scope`（推其他 chat）
> - `拓扑边界` = wire / cross-process / in-process / capability / multiple

### §1.A 基础设施与传输 (A1-A7)

| ID | 一句话 | Phase | Chat 4 处置 | 拓扑边界 | 既有 / 升级备注 |
|:--|:--|:--|:--|:--|:--|
| A1 | LiveKit Server 自托管 | 1 ✅ | inventory-only | cross-process（部署）| 已 P1 done；接口提炼 = 列入 deploy 章节 |
| A2 | Redis 状态总线 | 1 ✅ | inventory-only | cross-process | 已 P1 done；BB / Pub/Sub / Stream 接口在 §3 cross_process |
| A3 | Neo4j + Graphiti 栈 | 2 ✅（FalkorDB 替代）| inventory-only | cross-process | P2 done；接口在 cross_process/graphiti_v1 |
| A4 | WebRTC 音视频通道 | 1 ✅ | inventory-only | wire | livekit-unity-video-publish skill 已收口 |
| A5 | RPC 指令通道 | 1 ✅ | inventory-only | wire | wire/livekit_rpc_v1（Stage 3）|
| A6 | DataChannel 遥测 | 1 ✅ | inventory-only | wire | wire/topic_matrix（Stage 3）|
| A7 | Docker Compose 编排 | 1 ✅ | out-of-scope | （deploy）| deploy_snapshot 已覆盖；不在接口提炼主场 |

### §1.B 云端大脑 (B1-B14)

| ID | 一句话 | Phase | Chat 4 处置 | 拓扑边界 | 既有 / 升级备注 |
|:--|:--|:--|:--|:--|:--|
| B1 | Agent 骨架（AgentSession + Gemini RealtimeModel）| 1 ✅ | inventory-only | in-process（attach helper）| in_process/attach_helpers + LineB 双管线适配 |
| B2 | ParrotSoul 人设注入 | 1 ✅ | proposed-upgrade | capability | **NEED-P2.5-A persona 外置**（详 §2）；当前硬编码鹦鹉味 |
| B3 | Tool Forwarding | 1 ✅ | inventory-only | wire / capability | wire/livekit_rpc_v1 + capability/brain_tools_inventory |
| B4 | fly_to Tool | 1 ✅ | proposed-upgrade | capability | **NEED-P3-CAPABILITY-GATING**（非飞行模型应不暴露此 tool；详 §2）|
| B5 | animate Tool | 1 ✅ | inventory-only | capability | capability/brain_tools_inventory |
| B6 | focus_on Tool | 2 ⚠️ | proposed-upgrade | capability + wire | 实际形态变成 W6-7 BBox/Focus + threshold；不再是单独 tool；inventory 时澄清现状 |
| B7 | describe_object Tool | 2 ⚠️ | inventory-only | capability | 当前 = `query_scene` tool 的一部分；inventory 列入 |
| B8 | remember Tool | 2 ✅ | inventory-only | capability | capability/brain_tools_inventory（已 ratified）|
| B9 | query_scene Tool | 2 ✅ | inventory-only | capability | 同上 |
| B10 | event_end Tool | 3 ⚠️ | inventory-only | capability | 实际形态 = `manage_episode` tool（命名升级）|
| B11 | dispatch_task Tool | 1 ✅ | proposed-upgrade | wire / capability | **NEED-P2.5-PLAN-INTEGRATION** Chat 4 主场（详 §2）|
| B12 | Context Injector | 2 ✅ | inventory-only | in-process | in_process/selection_c_state_context（_state_context.py 即此）|
| B13 | Observer 系统（4 个）| 3 ⚠️ | inventory-only | in-process | 当前已有 5 observer（snapshot/sighting/bbox/focus/photo）；inventory 列入；**注意**实际数量 ≠ 4，是 5 |
| B14 | Gemini 降级处理 | 2 ⏳ | proposed-new | in-process | LineB 已加 STT-LLM-TTS Phase 5+ 第二条线；显式抛错而非 fallback；inventory 列升级路径 |

### §1.C Unity AR 客户端 (C1-C12)

| ID | 一句话 | Phase | Chat 4 处置 | 拓扑边界 | 既有 / 升级备注 |
|:--|:--|:--|:--|:--|:--|
| C1 | LiveKit 连接 | 1 ✅ | inventory-only | wire / capability | livekit-unity-lifecycle skill |
| C2 | AR Foundation 基础 | 1 ✅ | out-of-scope | （Unity 内部）| ar-foundation-api skill |
| C3 | 鹦鹉模型+基础动画 | 1 ✅ | inventory-only | capability | capability/model_manifest_v1（GOSLO Manifest 已 ratified）|
| C4 | RPC Handler | 1 ✅ | inventory-only | wire | wire/livekit_rpc_v1（C# 端）|
| C5 | 遥测上报（Pose/Hands/Sensors）| 1 ✅ | inventory-only | wire | wire/topic_matrix（lossy + reliable 通道）|
| C6 | TTS Speaker | 1 ✅ | inventory-only | wire | wire 内置 LiveKit audio track |
| C7 | APP 生命周期 | 1 ✅ | inventory-only | wire / cross-process | livekit-unity-lifecycle skill 已收口 |
| C8 | XR Hands 手势输入 | 2 ✅ | inventory-only | capability | 已 W3.A.2 perch_to_finger 落地 |
| C9 | 手势反射动作 | 2 ✅ | inventory-only | in-process / capability | Reflex 层调度（capability/triggers + scheduler 内）|
| C10 | 鹦鹉高级动画（Perch/Dance）| 2 ✅ | inventory-only | capability | capability/parrot_actions_v1（4 enum）|
| C11 | 平面行走 | 2 ⏳ | inventory-only | capability | 当前 fly_to 已包；inventory 标 evolving |
| C12 | 网络质量提示 | 2 ✅ | inventory-only | wire / capability | livekit-unity-lifecycle 已覆盖 connection_health 4 态 |

### §1.D 视觉感知 DSG (D0-D16)

| ID | 一句话 | Phase | Chat 4 处置 | 拓扑边界 | 既有 / 升级备注 |
|:--|:--|:--|:--|:--|:--|
| D0 | DSG Processor 挂载接口 | 1 ✅ | inventory-only | in-process | bus/processor 已落地 |
| D1 | StabilityGate 简版 | 2 ⏳ | inventory-only | in-process | proposed-upgrade（A10 接入时定型）|
| D2 | L1 视觉管线（SAM2 + YOLO-World）| 2 ⏳ | out-of-scope | in-process | A10 接入；P3 阶段 |
| D3 | DINOv2 ReID | 2 ⏳ | out-of-scope | in-process | 同上 |
| D4 | L2-A 空间图简版 | 2 ⏳ | out-of-scope | in-process | P3 阶段；ConceptGraph SKILL 蒸馏已就位 |
| D5 | L2-A 空间查询 API | 2 ⏳ | out-of-scope | capability | 同上 |
| D6 | 节点状态机（ACTIVE/OCCLUDED/LOST）| 2 ⏳ | inventory-only | in-process | DSG L2-B 已部分实现（ConfirmationStatus）|
| D7 | L2-B 语义图简版 | 3 ✅ | inventory-only | in-process | DSG-INTENT-EVENT-V1 + DSG-POOL-V1（DSG Chat 2 已收口）|
| D8 | 触发器输出（NEW/MISSING/DISPLACED）| 2 ✅ | inventory-only | in-process | in_process/dsg_trigger_outcome_v2（5 路上行）|
| D9 | L2-B 完整注意力 | 3+ ⏳ | inventory-only | in-process | proposed-upgrade（双开放路径已留 — 字段 + 机制 strategy）|
| D10 | ExpectationChecker | 3+ ⏳ | out-of-scope | in-process | P3 仿生升级 chat |
| D11 | 场景折叠 | 3 ⏳ | inventory-only | in-process | TODO(P3-fold-bionic) — proposed-upgrade |
| D12 | ActivityThrottle | 2 ⏳ | out-of-scope | in-process | A10 接入时 |
| D13 | 帧质量检查 | 2 ⏳ | out-of-scope | in-process | 同上 |
| D14 | StabilityGate 完整版 | 3 ⏳ | out-of-scope | in-process | P3 |
| D15 | DSG Sentinel 哨兵 | 远期 | out-of-scope | （远期）| 项目方向已变（user 在泉州；笔记本不实用）|
| D16 | ZoneNode / HandNode | 3+ ⏳ | inventory-only | capability | proposed-new — 与 4 类块 / 多场景一起 |

### §1.E 调度器 (E1-E5)

| ID | 一句话 | Phase | Chat 4 处置 | 拓扑边界 | 既有 / 升级备注 |
|:--|:--|:--|:--|:--|:--|
| E1 | SimpleRouter | 1 ✅（已升 BT）| inventory-only | in-process | py-trees BT 已落（D6 决策）|
| E2 | 三级调度（Reflex/Intent/Task）| 2 ✅ | inventory-only | in-process | parrot_behavior_rules §0.1 已 ratified |
| E3 | Redis Blackboard 读写 | 1 ✅ | inventory-only | cross-process / in-process | cross_process/redis + bb_schema 26 keys |
| E4 | py-trees 行为树 | 1.5 ✅ / 3+ 扩展 | inventory-only | in-process | 当前浅层 BT；proposed-upgrade 至完整 (Safety/Priority/Parallel/Idle) |
| E5 | ResourceLockManager | 2 ✅ | inventory-only | in-process | active_locks BB key + EcpAck `active_locks` 字段 |

### §1.F 后台任务 (F1-F6)

| ID | 一句话 | Phase | Chat 4 处置 | 拓扑边界 | 既有 / 升级备注 |
|:--|:--|:--|:--|:--|:--|
| F1 | Nanobot fork + 适配 | 1 ✅ | inventory-only | cross-process | bus/nanobot_consumer + parrot_bus.py |
| F2 | 外部聊天渠道（WeChat/Telegram）| 2 ⏳ | out-of-scope | cross-process | P2.5 后；不在 Chat 4 主场 |
| F3 | 任务消费+结果回写 | 2 ✅ | proposed-upgrade | cross-process / in-process | **NEED-P2.5-PLAN-INTEGRATION** + **NEED-P2.5-NANOBOT-HEARTBEAT** Chat 4 主场（详 §2）|
| F4 | Memory Consolidation | 3 ⏳ | proposed-new | cross-process | **NEED-P2.5-ARCHIVE-LLM** Chat 4 主场（详 §2）|
| F5 | Cron 定时任务 | 3 ⏳ | inventory-only | cross-process | nanobot/cron 占位 |
| F6 | Research 能力 | 3 ⏳ | out-of-scope | cross-process | 推 P3 |

### §1.G 记忆与知识 (G1-G4)

| ID | 一句话 | Phase | Chat 4 处置 | 拓扑边界 | 既有 / 升级备注 |
|:--|:--|:--|:--|:--|:--|
| G1 | Graphiti 基础（1 分区）| 2 ✅ | inventory-only | cross-process | cross_process/graphiti_v1 |
| G2 | Graphiti 5 分区 | 3 ✅ | inventory-only | cross-process | episodic / objects / personality / vocabulary / nanobot_research |
| G3 | 社区检测预加载 | 3 ⏳ | proposed-upgrade | in-process / cross-process | proposed-upgrade（与 D11 fold 一起；P3）|
| G4 | Obsidian SSOT 同步 | 3+ ✅ | inventory-only | cross-process / capability | sync_obsidian_to_graphiti.py 已落地；SOURCE_X §2.1 三分类 |

### §1.H 桥接与生态 (H1-H5)

| ID | 一句话 | Phase | Chat 4 处置 | 拓扑边界 | 既有 / 升级备注 |
|:--|:--|:--|:--|:--|:--|
| H1 | MCP Sidecar | 3 ⏳ | out-of-scope | cross-process | P3+；extension_points.md 占位 |
| H2 | Gemini 二重身 | 远期 | out-of-scope | （远期）| 不在 Chat 4 主场 |
| H3 | LobeChat Bridge | 3+ ⏳ | out-of-scope | cross-process | P3+ |
| H4 | Obsidian Bridge | 3+ ⏳ | inventory-only | cross-process | G4 已落地 sync 脚本；MCP Client / Canvas 同步留 P3 |
| H5 | Web Client 调试 | 2 ⏳ | out-of-scope | cross-process | P3+；已被 Editor 调试替代 |

---

## §2 cross-chat-registry NEED-* 12 项

> 来源：[`../architecture/cross_chat_pending_registry_20260507.md`](../architecture/cross_chat_pending_registry_20260507.md) §3-§4

| ID | 严重度 | Chat 4 处置 | 拓扑边界 | 真源 |
|:--|:--|:--|:--|:--|
| **NEED-P2.5-A** Brain LLM persona 外置 | 🔴 high | out-of-scope（推 DSG 协议升级 chat 与 4 类块设定块一起）| capability | goslo_modularization_residual_debt §2.1 |
| **NEED-P2.5-PLAN-INTEGRATION** Plan ↔ Scheduler ↔ Nanobot 完整路径 | 🟡 mid | ✅ Chat 4 主场（4-A 实施轨 #1）| wire / cross-process / in-process | dsg_l1_5_implementation_completion §9.1 F-3 |
| **NEED-P2.5-NANOBOT-HEARTBEAT** nanobot 心跳写者 | 🟡 mid | ✅ Chat 4 主场（4-A 实施轨 #3）| cross-process | dsg_l1_5_implementation_completion §9.1 F-2 |
| **NEED-P2.5-ARCHIVE-LLM** Phase 3 LLM 蒸馏 → Graphiti | 🟡 mid | ✅ Chat 4 主场（4-A 实施轨 #2）| cross-process / in-process | dsg_l1_5_implementation_completion §9.1 F-1 |
| **NEED-P2.5-B** Unity menu 暴露 DSG bucket / scene 切换 | 🟡 mid | out-of-scope（推 AR 工作区独立 chat）| wire / capability | goslo_modularization_residual_debt §4.1 |
| **NEED-P3-A** EcpFrontendState body_state 解锁评估 | 🟡 mid | proposed-upgrade（doc 占位；实施推 P3 wire ADR chat）| wire | goslo_modularization_residual_debt §2.2 |
| **NEED-P3-B** 4 类块（模型/设定/模式/场景）注册表 | 🔴 high | proposed-new（doc 占位 + 与 NEED-P3-C 一起；推 DSG 协议升级 chat 实施）| capability / wire | goslo_modularization_residual_debt §4.3 |
| **NEED-P3-C** 预设 = 4 active ID 命名快照 | 🟡 mid | proposed-new（同上）| capability / cross-process | 同上 |
| **NEED-P3-D** Unity menu UI = node-canvas | 🟢 low | out-of-scope（AR 工作区独立 chat）| capability（Unity SO 接口）| 同上 |
| **NEED-P3-E** 默认菜单 fallback | 🟢 low | out-of-scope（同上）| capability | 同上 |
| **NEED-P3-CAPABILITY-GATING** tool 暴露按 manifest 过滤 | 🟡 mid | ⚠️ **Chat 4 §10 Q1 待答**（推荐取；轻量 5-15 行）| in-process / capability | goslo_modularization_residual_debt §2.2 #3 |
| **TODO(P3-Wire-PlanUI)** Plan 用户确认 wire 信号 | 🟡 mid | proposed-upgrade（doc 占位 wire 升级；推 P3 wire ADR chat 实施）| wire / capability | dsg_l1_5_implementation_completion §9.1 F-4 |

---

## §3 隐式需求（user 流程 / 愿景 / 行为契约提取）

> 来源：[`../architecture/ar_app_flow_ui_design.md`](../architecture/ar_app_flow_ui_design.md) + [`../architecture/ar_feature_vision.md`](../architecture/ar_feature_vision.md) + [`../parrot_behavior_rules.md`](../parrot_behavior_rules.md)
>
> **这些需求 requirements.md 没明确列**，但 user 在 App flow / Vision / 行为契约里说过；接口提炼必须覆盖。

### §3.1 启动页 / 主菜单类（来自 ar_app_flow_ui_design §5）

| ID | 一句话 | Chat 4 处置 | 拓扑边界 | 真源 |
|:--|:--|:--|:--|:--|
| **NEED-IMPL-MENU-001** 启动页菜单承载可选择项与调试项 | proposed-new | capability | ar_app_flow §5 + §9 |
| **NEED-IMPL-MENU-002** 选择初始房间 / BrainAgent 管线 / 人设 / 场景 | proposed-new（重叠 NEED-P3-B 4 类块）| capability | 同上 |
| **NEED-IMPL-MENU-003** 权限 + 连接测试可作为启动页菜单选项 | proposed-new | wire / capability | 同上 |
| **NEED-IMPL-MENU-004** 启动页菜单不应只是隐藏调试按钮 — 它是功能验证入口 | proposed-new | capability | 同上 |

### §3.2 HUD / 工具柜类（来自 ar_app_flow_ui_design §6-§7）

| ID | 一句话 | Chat 4 处置 | 拓扑边界 | 真源 |
|:--|:--|:--|:--|:--|
| **NEED-IMPL-HUD-001** HUD 可开关 / 可收纳 / 可展开 / 用户选展开方向 | proposed-new | capability（Unity UI 接口）| ar_app_flow §6 |
| **NEED-IMPL-TOOLCAB-001** 工具柜：放大镜（含倍率调节）、注意力框、纸条/报告、任务按钮、贴图箱、行程单 | proposed-new | capability | ar_app_flow §7 |
| **NEED-IMPL-TOOLCAB-002** 注意力框工具的接口语义需进入 ECP / DSG L2-B 设计讨论 | proposed-upgrade | wire / capability / in-process | ar_app_flow §8 6 个开放问题 |

### §3.3 注意力工具 6 开放问题（来自 ar_app_flow_ui_design §8）

| ID | 一句话 | Chat 4 处置 | 拓扑边界 | 真源 |
|:--|:--|:--|:--|:--|
| **NEED-ATTN-Q1** 注意力框归到 Reflex / Intent / Task / 多层协作？ | proposed-upgrade | in-process | ar_app_flow §8 |
| **NEED-ATTN-Q2** GOSLO 应立刻停下思考还是后台先识别？ | proposed-upgrade | in-process / capability | 同上 |
| **NEED-ATTN-Q3** 拖框是否触发 captureSnapshot？ | proposed-upgrade | wire / capability | 同上 |
| **NEED-ATTN-Q4** 注意力框是否生成 SightingEvent / SceneObservationEvent？ | proposed-upgrade | wire | 同上 |
| **NEED-ATTN-Q5** 如何避免打断对话？ | proposed-upgrade | in-process | 同上 |
| **NEED-ATTN-Q6** 临时指一下，命令多久过期？ | proposed-upgrade | wire（EcpCommand expires_at）| 同上 |
| **NEED-ATTN-Q7** ECP 是否需"正在关注某区域，但不强制中断当前说话"？ | proposed-upgrade | wire | 同上 |
| **NEED-ATTN-Q8** 它和 identify_object Path1 是否共用按需视觉证据链？ | proposed-upgrade | in-process | 同上 |

> 注：Q3-Q7 实际已在 Phase 4 W6-7 BBox/Focus + threshold 落地（ar_app_flow §8 写于 2026-04-29，Phase 4 收口于 2026-04-30）；Stage 3 接口面 inventory 时**显式 cross-link** 这些问题在 Phase 4 §8 中的对应锁。

### §3.4 ar_feature_vision §3 四核心讨论（一句话愿景的支撑）

| ID | 一句话 | Chat 4 处置 | 拓扑边界 | 真源 |
|:--|:--|:--|:--|:--|
| **NEED-VISION-GATE-001** 门控三层（产地/路上/消费端）协作 | inventory-only | wire / in-process | ar_feature_vision §3.1 |
| **NEED-VISION-OCCLUDE-001** GOSLO 自知"被什么挡住"（不是黑盒识别）| proposed-upgrade | wire / in-process | ar_feature_vision §一 + §二 |
| **NEED-VISION-SCENE-CONTINUITY-001** 场景切换自然转场 + Pause-Resume 接上话 | inventory-only | wire / in-process | ar_feature_vision §一 |
| **NEED-VISION-ATMOSPHERE-001** 摆 pose / 拍立得 / 回忆杀（糖衣层）| out-of-scope（P3）| capability | ar_feature_vision §一 |

### §3.5 行为契约红线（来自 parrot_behavior_rules §0.3）

| ID | 一句话 | Chat 4 处置 | 拓扑边界 | 真源 |
|:--|:--|:--|:--|:--|
| **NEED-BEHAVIOR-001** Tool 同步/异步与话术一致（不允许"我切好了"但实际未应用）| inventory-only | capability / in-process | parrot_behavior_rules §0.3 |
| **NEED-BEHAVIOR-002** 同步 tool 必须返回 `applied/rejected/timeout/no_target/unchanged` | inventory-only | capability | 同上 |

---

## §4 Chat 4 范围确认

### §4.1 Chat 4 主场（接口面提炼范围）

| 范围 | 数 | 处置 |
|:--|:--|:--|
| Phase 1-3 完成的接口（inventory-only）| ~40 | Stage 3 写接口文件 + 标 status |
| 实施 TODO（4-A 实施轨）| 5 | 详 TODO.md §6 |
| proposed-upgrade（doc 占位 + 推后实施）| ~15 | 接口面有 status=`proposed-upgrade` + upgrade_from 字段 |
| proposed-new（接口设计但代码未实现）| ~5 | 接口面有 status=`proposed-new` |

### §4.2 Out-of-scope（推其他 chat）

| 推到哪 | 项 |
|:--|:--|
| **DSG 协议升级 chat（菜单画布主线）** | NEED-P2.5-A persona 外置 / NEED-P3-B 4 类块 / NEED-P3-C 预设 schema |
| **AR 工作区独立 chat（菜单 UI）** | NEED-P2.5-B Unity menu / NEED-P3-D node-canvas / NEED-P3-E 默认 fallback |
| **P3 wire 升级 ADR chat** | NEED-P3-A body_state 解锁 / TODO(P3-Wire-PlanUI) |
| **P3 仿生升级 chat** | TODO(P3-fold-bionic) / TODO(P3-attention-spreading) / TODO(P3-RefHealth) |
| **P3 / A10 接入 chat** | D1-D5 视觉管线 / D12-D14 / TODO(P3-multi-scene) |
| **远期方向变更（不实施）** | D15 DSG Sentinel / H2 Gemini 二重身 / H3 LobeChat / 等 |

### §4.3 Chat 4 §10 待答影响

| 待答项 | 影响 §1 / §2 / §3 哪些项 |
|:--|:--|
| Q1 capability-gating 是否纳入 | NEED-P3-CAPABILITY-GATING + B4 fly_to 升级 |
| Q4 freeze test 范围 | 影响 wire / capability 章节 freeze_test 字段填充粒度 |
| Q5 需求覆盖度（67 全检 vs 仅接口相关）| 本文 §1 已默认采"仅接口相关子集"——如果 Q5 选 67 全检则要扩 D2-D5 / F4-F6 等 out-of-scope 项的 inventory 行 |

---

## §5 全表统计

| 维度 | 数 |
|:--|:--|
| §1 67 项 inventory-only | 39 |
| §1 67 项 proposed-upgrade | 6 |
| §1 67 项 proposed-new | 0（67 项原本就是 inventory）|
| §1 67 项 out-of-scope | 22 |
| §2 12 NEED-* Chat 4 主场 | 3（PLAN-INTEGRATION + NANOBOT-HEARTBEAT + ARCHIVE-LLM）|
| §2 12 NEED-* doc 占位（proposed-upgrade/new）| 4（CAPABILITY-GATING + body_state + 4 类块 + 预设）|
| §2 12 NEED-* out-of-scope | 5（persona / Unity menu / node-canvas / fallback / Plan UI wire）|
| §3 14 隐式需求 inventory-only | 3 |
| §3 14 隐式需求 proposed-upgrade | 9 |
| §3 14 隐式需求 proposed-new | 4 |
| **总 Chat 4 接口面候选**（inventory + upgrade + new）| **~55** |

---

## §6 给 Stage 2 (4-B-cap) 的输入

Stage 2 拿本文 + `app_flow_inventory.md` 后，反推能力清单时关注以下视角：

1. **每能力是否有 NEED-XX 来源 cite**（driven_by 字段）
2. **每能力的"应有 / 已有 / 缺 / 漂"四态判定**：
   - **应有** = §3 隐式需求 + §2 NEED-* proposed-new
   - **已有** = §1 inventory-only 部分
   - **缺** = §1/§2 proposed-new
   - **漂** = §1 inventory-only 但 Phase 4 §8 标 experimental 的（如 FocusBboxThreshold / selection-C / IngestRunner factory / identify_object 1.9s）
3. **特别注意 Phase 4 临时实现不能锁成 capability locked**（详 methodology.md §3 status 5 态）

---

## §7 引用

- 父规划稿：[`../architecture/interface_extraction_plan_20260507.md`](../architecture/interface_extraction_plan_20260507.md)
- INDEX：[`INDEX.md`](INDEX.md)
- methodology：[`methodology.md`](methodology.md)
- TODO：[`TODO.md`](TODO.md)
- 配套 Stage 1：[`app_flow_inventory.md`](app_flow_inventory.md)

---

## §8 变更日志

- **2026-05-07**：本文创建（Stage 1 Chat 4 = 4-B-req 在主 chat 跑产）。覆盖 67 项 + 12 NEED-* + 14 隐式需求 = 93 需求条目；其中 Chat 4 接口面候选 ~55，out-of-scope ~38。
