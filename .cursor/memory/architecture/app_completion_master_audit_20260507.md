---
status: ratified-master-audit
category: master-audit
status_note: "App 完成度 + DSG 必要升级 总 chat 主 doc。基于 §1 入场必读 12 项产出：8 场景对账表 + 5 发现 + Sub-Chat A/B 派发清单 + 像素画 UI 资产清单（用户自管美术）。本 doc 不重写 SSOT，仅做 inventory + 引用 + 派发。"
last_reviewed: 2026-05-07
authoritative_for: "App 端到端完成度对账（8 场景 × 4 列）+ Sub-Chat A/B 入场必读基线 + user 自管像素画美术资产清单"
parent_doc: "../INDEX.md"
sources:
  - "app_completion_master_chat_launch_prompt_20260507.md (本 chat 启动 prompt)"
  - "../protocol_snapshot_p4.md (协议 SSOT)"
  - "module_map_p4_snapshot.md (架构 quick-ref)"
  - "cross_chat_pending_registry_20260507.md (NEED-* / TODO 真源)"
  - "ar_app_flow_ui_design.md (App Flow / UI 基线)"
  - "dsg/dsg_l1_5_implementation_completion_20260506.md"
  - "goslo_modularization_completion_20260506.md"
  - "goslo_modularization_residual_debt_20260506.md"
  - "goslo_model_manifest_protocol_v1.md"
  - "lineb_implementation_completion_20260504.md"
  - "sprint4_phase4_entry_20260430.md §8"
  - "sprint4_protocol_v2_ecp.md"
  - "../parrot_behavior_rules.md §3.7"
related:
  - "app_flow_requirements_interface_chat_launch_prompt_20260507.md (Sub-Chat A 派发)"
  - "backend_interface_refinement_chat_launch_prompt_20260507.md (Sub-Chat B 派发)"
  - "../upgrade_roadmap.md (Chat 4 残余 18 项 cross-link)"
---

# App 完成度 + DSG 必要升级 — 主 Audit Doc

> **本文用途**：上一轮"接口提炼几乎只是把仓库复制了一半"失败后，由总 chat 产出的纠偏对账 doc。
>
> **写作硬约束**：
> 1. **不重写**任何 SSOT（protocol_snapshot_p4 / module_map_p4_snapshot / 3 完成报告 / cross_chat_pending_registry）—— 仅引用
> 2. **不发明**新 NEED-* 标签 —— 全部从 cross_chat_pending_registry §3/§4 取词
> 3. **不写代码** —— 纯 markdown inventory + 派发
> 4. **不动 wire / enum / namespace** —— Phase 4 §8 13 锁全护
>
> **本 chat 收口判据**：8 场景对账表清晰 + 5 finding + Sub-Chat A/B 入场 prompt 互不重叠 + INDEX 入口 + user sign-off。

---

## §0 TL;DR

| 维度 | 结论 |
|:--|:--|
| 8 核心场景对账（§1） | 7/8 场景**协议层够用**（已落地能力 + 既有 NEED-* 标签即可解决）；1/8 BLOCKED-BY-NEW-ADR（场景 5 Plan UI wire）|
| 用户钦定核心验证（场景 6 菜单画布 4 类块） | Model / Mode / Scene 3 块 ✅；Persona 块 ❌ NEED-P2.5-A；预设 schema ❌ NEED-P3-C；UI ❌ NEED-P3-D/E |
| 当前协议 SSOT 状态 | Phase 4 §8 13 锁 + cs_parity 4/4 + ADR-L1.5-001 11/11 + ObservationSource 7 entries verbatim 全护；415/415 pytest |
| 数据流连接安全策略 | ① EcpEvent 8KB 红线 + 60s dedup ② Photo 双通道（preview reliable < 8KB + asset HTTP）③ Echo 全链路注入（避免 Brain/Unity 阈值漂移）④ LineB env-gate 无 silent fallback ⑤ 3 通道速率红线（reliable / lossy / RPC 不可串）|
| ECP 状态 | Phase 4 W0-W8 完成 + 联机 smoke #3/#4/#5 ✅；#1/#2 显式 defer 真机 spike；LineB 双管线兼容性结构 PASS / 联机待 6-axis Editor smoke |
| 派发结果（4 个修复 chat 路径）| Sub-Chat A（用户视角 App Flow）+ Sub-Chat B（后端模块视角）+ Chat 4 4-A 实施轨（已存在）+ DSG 协议升级 chat（菜单画布主线）+ AR 工作区独立 chat（菜单 UI）+ P3 wire ADR chat（Plan UI + body_state）|
| 像素画 UI 资产 | §6 附录 9 类 30+ 项清单（user 自管美术；Sub-Chat A 以占位推进） |

---

## §1 §A 8 场景对账表（核心交付物）

> **行 = user 钦定的 8 个核心场景**（来自启动 prompt §2.1 #1-#8）。
> **列 = 4 维**：涉及模块 / 已交付能力 / 缺口（NEED-* 标签）/ 修复 chat 派发。
> **每行 ≤ 1 表格行 + 1 句话能力 + 1 句话缺口**（防失败模式 R2）。

### §1.1 场景 1 — GOSLO 在 AR 房间陪伴对话（最基础）

| 列 | 内容 |
|:--|:--|
| 涉及模块 | `brain/agent` (LineA RealtimeModel / LineB env-gate) + `brain/soul` + `brain/tools/{animate, fly_to, set_mode}` + `brain/cognitive_state_tracker` + `Unity ParrotApp/Parrot/{ParrotController, ParrotRpcHandler, ModelDriver, GosloLegacyController}` + LiveKit Audio Track + EcpState 1Hz |
| 已交付能力 | ✅ Phase 4 §8 协议合同 0 漂移；selection-C `_state_context` 三态 reason 注入；GOSLO Step 1-5 ModelManifest plumbing；Echo 全链路 attention thresholds（防 Brain/Unity 阈值漂移）；GOSLO_default manifest baseline；fallback 链 IParrotController → AnimationDriver → Animator |
| 缺口 | ⚠️ NEED-P2.5-A persona 外置（`brain/soul.py` 内联硬编码"You are Parrot"，换非鹦鹉模型 LLM 嗓音不变 — 视觉违和）|
| 派发 | DSG 协议升级 chat（与场景 6 4 类块统一设计）/ Sub-Chat A 此场景为 baseline |

### §1.2 场景 2 — GOSLO 主动好奇看场景物体 → 触发识别 / 入池 / 反馈

| 列 | 内容 |
|:--|:--|
| 涉及模块 | `dsg/triggers/goslo_curiosity_trigger` + `dsg/ingest/runner.commit_observation` + `dsg/l1_5/{pool, buckets, admission}` (`AUTONOMOUS_CURIOSITY` Bucket TTL 300s) + `dsg/ingest/base.ObservationSource.GOSLO_AUTONOMOUS`（第 8 项）+ `dsg/ingest/autonomous_curiosity_filter` |
| 已交付能力 | ✅ DSG Chat 2 收口（118 新测 + 415 pytest）；GOSLO_AUTONOMOUS source（ADR-L1.5-001 §1.1 锁，第 8 项）；TriggerOutcome V2 5 路上行（commit_observations / bucket_ops / staged_refs / archive_request / plan_request）；test_l1_5_admission_baseline.test_goslo_autonomous_routing 守护 |
| 缺口 | A10 真识别 = `TODO(P3-multi-scene)` placeholder（当前桌面 baseline；多 SceneType profile 留 P3）；GOSLO LLM "主动好奇"行为本身受 NEED-P2.5-A persona 外置影响 |
| 派发 | A10 接入 chat（Phase 5+）/ Sub-Chat B 确认 commit_observation 接口面稳定性 / DSG 协议升级 chat（persona 外置）|

### §1.3 场景 3 — 拍照 → 展示 → GOSLO 评论（W8 photo + 富文本回程 + IntentWorkspace stage）

| 列 | 内容 |
|:--|:--|
| 涉及模块 | Unity `ParrotApp/Photo/PhotoController` (双通道 preview + asset)；Brain `observer/photo` + `photo_upload_server` (FastAPI 7889)；Brain BB `transient/last_photo_event`；EcpEventType `photo.taken_preview` / `photo.asset_uploaded`；NodeKind.PHOTO + 3 EdgeKind defer Phase 5+；IntentWorkspace `PHOTO_REFERENCE` StagedRefKind |
| 已交付能力 | ✅ Phase 4 §8 L7+L8 锁；Phase 4 W8 验收离线 Brain+Unity 全绿；preview 256px JPEG quality cascade 75→60→50→40 + base64 < 8KB；high-quality asset HTTP POST → Castle 本地 cache；PendingPhoto reconnect 不重发；3 ContextMenu 兜底；21 测试 |
| 缺口 | 联机 smoke ⏳（defer 真机 spike）；GOSLO "评论"行为 prompt 级 = NEED-P2.5-A 影响；Unity 工具柜拍照按钮 UI = `ar_app_flow_ui_design §7` 占位（NEED-P2.5-B Unity menu）|
| 派发 | 真机 spike chat（联机 smoke）/ DSG 协议升级 chat（persona）/ AR 工作区独立 chat（拍照按钮 UI 入口）/ Sub-Chat A 写"用户视角拍照流程 + 占位 UI" |

### §1.4 场景 4 — GOSLO 派发 nanobot 长任务（research）→ 解阻塞 → result 回流 → 富文本批改/汇报展示

| 列 | 内容 |
|:--|:--|
| 涉及模块 | `brain/tools/dispatch_task` → `scheduler/nodes.DispatchToNanobot` → Redis Stream `parrot.scheduler.task_queue` → Nanobot Worker（HKUDS fork + parrot_bus channel + research tool）→ Pub/Sub `parrot.nanobot.results` → `scheduler/service._listen_nanobot_results` → BB notification → LLM context inject；**Plan-and-Execute**：`brain/plan/{plan, plan_registry, plan_blackboard, plan_lifecycle}` 8 状态机 |
| 已交付能力 | ✅ Phase 1 dispatch_task 链路（M1 验收 V3）；Plan 8 状态机 11/11 测试；IntentWorkspace 主存 + L2-B 镜像 reuse `NodeKind.EVENT`（不动 enum）；`parrot:nanobot_heartbeat` HASH 读者就位（reader = IdleArchiveTrigger）|
| 缺口（4 个一锅端，**Chat 4 4-A 主场**）| ① NEED-P2.5-PLAN-INTEGRATION（5 项 plan-* TODO：start_executing 真调 do_dispatch_task / scheduler 路由 plan_id+step_id+result_channel / active_tasks BB 写 / report_step_result 回流 / timeout 路由）② NEED-P2.5-NANOBOT-HEARTBEAT（writer 缺）③ NEED-P2.5-ARCHIVE-LLM（archive_to_graphiti 仅计数，真 LLM 蒸馏未连）④ TODO(Chat4-disk-recover)（DiskBackend.recover()）；富文本批改/汇报展示 UI = NEED-P3-D node-canvas |
| 派发 | **Chat 4 4-A 实施轨**（high priority — 见 `upgrade_roadmap.md §1`）/ AR 工作区独立 chat（汇报展示 UI）/ Sub-Chat B 此场景 = 接口稳定面最重要的提炼对象（5 路上行通道 × 6 下游模块）|

### §1.5 场景 5 — GOSLO 进 Intent 制定 Plan → 用户在 Unity menu 确认 → 派发执行（Plan UI wire）

| 列 | 内容 |
|:--|:--|
| 涉及模块 | `brain/plan/plan_registry` 8 状态：DRAFT → AWAITING_USER_CONFIRMATION → APPROVED / REJECTED / REVISED → EXECUTING → DONE / FAILED；IntentWorkspace `PLAN_DRAFT` / `PLAN_AWAITING_USER` StagedRefKind；Brain → Unity Plan UI（**当前 wire 不通**）|
| 已交付能力 | ✅ Plan 状态机 + revise 创建新 plan supersedes；test_plan_lifecycle 11/11；test_draft_stages_to_intent_workspace；test_legal_transition_chain_to_complete |
| 缺口（**BLOCKED-BY-NEW-ADR**）| TODO(P3-Wire-PlanUI) — 当前 `submit_for_confirmation` 由调用方直接 `approve()`；真 EcpEvent UI / EcpCommand 回流未实施。需新 EcpEventType（`plan.proposed` / `plan.approved` / `plan.rejected` / `plan.revised`）+ Unity Plan card UI（Mermaid / Gantt / step list / approve button）+ EcpCommand `APPROVE_PLAN` / `REJECT_PLAN` / `CANCEL_PLAN` / `REVISE_PLAN` 回流 + Brain RPC bridge 接收用户决策。**触动 Phase 4 §8 wire 锁**，必须新 ADR + cs_parity 全过 |
| 派发 | **P3 wire 升级 ADR chat**（建议与 NEED-P3-A body_state 解锁 同 ADR）/ AR 工作区独立 chat（Plan card UI）/ Sub-Chat A 在场景 5 写"占位 stub UI"（不停等）|

### §1.6 场景 6 — 菜单画布 4 类块切换 + 预设保存 / 恢复（**核心验证接口能力成果**）

> **user 钦定**（启动 prompt §0）："菜单能够完成画布是一个重要的验证接口能力成果。"

| 列 | 内容 |
|:--|:--|
| 涉及模块 | 4 active BB key（`global/active_model_id` / `global/active_persona_id` / `global/active_mode` / `global/active_scene_id`）+ 4 注册表（ModelManifestRegistry / persona_loader / mode_watcher / SceneRegistry）+ 预设 JSON schema + Unity menu node-canvas UI |
| 已交付能力 | **3/4 块齐**：① **Model 块** ✅ ModelManifest Pydantic + ModelDriver + ParrotRegistry + GosloLegacyController + asset_to_manifest CLI + EcpCommand.meta["model_id"] wire 不动 ② **Mode 块** ✅ BehaviorMode 5 flags + set_mode tool + global/behavior_mode + mode_watcher（Phase 1） ③ **Scene 块** ✅ SceneType + SceneProfile + SceneRegistry + SceneSwitchOutcome + 永久权威 freeze / fresh clear（DSG Chat 2 收口）|
| 缺口（5 项一锅端，**DSG 协议升级 chat 主场**）| ❌ ① **Persona 块** = NEED-P2.5-A（外置 + loader + BB key）❌ ② NEED-P3-B 4 类块统一注册表 ❌ ③ NEED-P3-C 预设 schema（`data/presets/<id>.json`）❌ ④ NEED-P3-D Unity menu UI = node-canvas（ComfyUI / n8n 风）❌ ⑤ NEED-P3-E 默认菜单 fallback（列表 + 保存 + 恢复默认）|
| 派发 | **DSG 协议升级 chat**（菜单画布主线 — NEED-P2.5-A + NEED-P3-B + NEED-P3-C 一锅端）/ **AR 工作区独立 chat**（NEED-P3-D + NEED-P3-E UI 实施）/ Sub-Chat B 此场景 = 4 类块接口面提炼的真验证场景 |

### §1.7 场景 7 — LineA（Gemini Live）↔ LineB（STT-LLM-TTS）切换 — 行为不变

| 列 | 内容 |
|:--|:--|
| 涉及模块 | `brain/agent._build_session(pipeline, config)` + `_resolve_pipeline()` env-gate（`PARROT_LLM_PIPELINE=line_a` 默认 / `line_b`）+ `dsg/ingest/transcript_extractor`（pipeline-agnostic + 旧名 alias 保留）+ ObservationSource 7 entries verbatim 锁 |
| 已交付能力 | ✅ LineB 实施完成（lineb_implementation_completion）；structural PASS（Phase 4 §8 13 锁 0 漂移 + cs_parity 4/4 不破 + ObservationSource 7 entries verbatim）；234/234 pytest；无 silent fallback；`livekit-plugins-silero` 已装；Multi-Agent Handoff 脚本可运行 |
| 缺口 | Editor 联机 6-axis 双跑 smoke ⏳（FINDING-LB-1 ADC 部署门槛 / FINDING-LB-2 STT 构造期校验 / FINDING-LB-3 text_source_filter regex 与 ASR 转写风格差异 — 留 axis-5 联机确认）|
| 派发 | **LineB Editor smoke chat**（独立 follow-up）/ Sub-Chat B 把"7 ObservationSource entries verbatim + cs_parity 4/4 + Phase 4 §8"作为接口稳定性硬约束之一 |

### §1.8 场景 8 — 场景切换（桌面 → 户外占位）+ 永久权威 Bucket 跨切保留 + 对话延迟归档触发

| 列 | 内容 |
|:--|:--|
| 涉及模块 | `dsg/triggers/scene_switch_trigger` + `dsg/l2b/intent_event_boundary.IntentEventBoundaryHandler.switch_scene` + `dsg/l1_5/scene_snapshot.SceneRegistry.SceneSwitchOutcome` + `dsg/l1_5/buckets.BucketSpec`（永久权威 freeze / fresh clear）+ ConversationBoundary（多信号 OR）+ Archive 3-Phase Pipeline + IdleArchiveTrigger |
| 已交付能力 | ✅ test_l1_5_scene_switch 7/7（含 freeze authority + clear fresh）；3 阶段归档管线（hot / cold / nanobot 闲时归档）；ConversationBoundary 序列化触发；6 BucketKind（OBSIDIAN_REFERENCE_REINFORCE / OBSIDIAN_SETTING_DAILY / OBSIDIAN_SETTING_ROLEPLAY 永久；IDENTIFY_OBJECT_RESULT 永久；GEMINI_ORAL_MENTION TTL；AUTONOMOUS_CURIOSITY 300s TTL）|
| 缺口 | TODO(P3-multi-scene) — 当前仅 DESKTOP profile；HOME_INDOOR / OUTDOOR / LIBRARY / KITCHEN 留 P3；多 Scene + VPS A10 接入 |
| 派发 | **P3 / A10 接入 chat**（multi-scene profile）/ Sub-Chat B 把 SceneRegistry + BucketKind freeze 语义作为 lifecycle 接口稳定性证据 |

---

## §2 §A 5 个发现（总结）

### Finding-1：协议层 + ECP 当前已经够用 — 7/8 场景 0 wire 改动可支撑

Sprint 4 Phase 4（13 §8 锁 + 13 EcpEventType + 5 LiveKit topic + 26 BB key）+ DSG Chat 2（DSG-POOL-V1 + DSG-INTENT-EVENT-V1 + DSG-V2 触发器 + Plan + IntentWorkspace + Archive 3-Phase 8 协议）+ GOSLO 模块化（ModelManifest + IParrotController + EcpCommand.meta["model_id"]）= 8 场景中 **7/8 不需要新 wire**；唯一 BLOCKED-BY-NEW-ADR 的是**场景 5 Plan UI wire**（NEED-P3-A body_state 解锁 + TODO(P3-Wire-PlanUI) 建议合到 1 个 P3 wire ADR — 见 `upgrade_roadmap.md §2 #8 + #13`）。

### Finding-2：用户钦定核心验证（场景 6 菜单画布 4 类块）— 已落 3/4，缺口集中在 Persona + Preset + UI

Model / Mode / Scene 三块**全部齐**（GOSLO mod + Phase 1 BehaviorMode + DSG Chat 2 SceneRegistry）。唯一未抽离 = **Persona 块（brain/soul.py 内联硬编码）**。短路径建议：**DSG 协议升级 chat 把 NEED-P2.5-A + NEED-P3-B + NEED-P3-C 一锅端**（4 active BB key 齐 → 预设 = 4 ID 命名快照）。Unity menu node-canvas UI（NEED-P3-D + NEED-P3-E）= **AR 工作区独立 chat 范围**，与后端协议解耦推进，不互相阻塞。这是 user 钦定接口能力成果验证场景 — 跑通即说明 4 类块接口面够清晰。

### Finding-3：Plan-and-Execute 主链路最大单一缺口 = NEED-P2.5-PLAN-INTEGRATION（5 项 plumbing + 0 wire）

`PlanRegistry.start_executing` 仅标 `step.state = DISPATCHED` **未真调** `do_dispatch_task`；NanobotTask result 回流到 `Scheduler._listen_nanobot_results` **未路由**给 `PlanRegistry.report_step_result`。这是 **Chat 4 4-A 主场**（`upgrade_roadmap.md §1 #1` high priority），无 wire 改动，纯 plumbing。完成后 + NEED-P2.5-ARCHIVE-LLM + NEED-P2.5-NANOBOT-HEARTBEAT 三件套 = 场景 4 端到端可跑。

### Finding-4：LineA↔LineB 双管线结构 PASS / 联机待 6-axis Editor smoke

LineB 实施完成报告证明 Phase 4 协议合同对 LLM 类型解耦（structural PASS — 0 wire / 0 BB key / 0 EcpEventType / 0 ObservationSource enum 改动）。但 Editor 6-axis 联机 smoke 待跑（cognitive_state 时序 / selection-C reason 接受 / identify_object 1.9s 预算分布 / attention.threshold.crossed 反应延迟 / **DSG 文本提取层稳定性 axis-5 是关键** / Multi-Agent Handoff bonus）。**Sub-Chat B 应把"LineB 兼容守护"列为接口稳定性硬约束之一**（特别是 ObservationSource 7 entries verbatim + transcript_extractor pipeline-agnostic）。

### Finding-5：UI 美术资产是当前显式 gap — user 自管，本 doc §6 附录给清单

Sprint 4 全部用占位资产（GOSLO.glb 真模型已替换；2D 像素 HUD / 工具柜 / 启动页菜单 / 纸条 / 猫爪 / 放大镜 / 注意力框 全未做美术）。`ar_app_flow_ui_design.md` 已锁定**风格 = 2D 像素风 Meta UI**（不与真实世界互动）+ **主题 = 大小姐宅邸（主） + 海盗（P3 换肤）**。本 doc §6 附录给出 9 类 30+ 项资产清单（user 自管美术）；**Sub-Chat A 应把"以占位资产推进，资产到位再换"作为 UI 流程实施的硬约束**，避免被资产堵塞。

---

## §3 派发清单（核心交付物 2 — Sub-Chat A / B 入场范围）

### §3.1 Sub-Chat A — App Flow / 需求接口 chat

| 维度 | 内容 |
|:--|:--|
| **视角** | **用户视角**（user 操作 → UI 反馈 → Unity 端点 → 期望结果）|
| **输入** | 本 doc §1 + `ar_app_flow_ui_design.md` + `requirements.md` §四 C 段（Unity 客户端 12 项功能）+ Phase 4 §8 锁（避免越界）|
| **输出文件** | `architecture/app_flow_requirements_interface_<date>.md`（≤ 1 份）|
| **覆盖** | 8 场景的**用户操作流程** + UI 入口 + Unity 事件 + happy path / 失败路径 + 占位策略（资产/wire 未到位时） |
| **不做** | Backend 内部接口设计（Sub-Chat B 范围）；任何代码实施；任何超出 8 场景范围扩张；任何 wire / enum / BB key 改动；任何菜单 UI 控件像素细节（留 AR 工作区 chat） |
| **完成判据** | 8 场景每个有：① 用户操作步骤 ② 期望 UI 反馈 ③ 调用的 Unity 端点 / EcpEvent / EcpCommand ④ 失败路径 ⑤ 占位策略 |
| **入场 prompt** | 见独立文件 `app_flow_requirements_interface_chat_launch_prompt_20260507.md` |

### §3.2 Sub-Chat B — DSG / Brain 后端接口提炼 chat

| 维度 | 内容 |
|:--|:--|
| **视角** | **模块视角**（后端模块边界 + 接口稳定面 + 跨模块 binding）|
| **输入** | 本 doc §1 + `protocol_snapshot_p4.md`（28 章 全协议 SSOT）+ 3 完成报告（DSG Chat 2 / GOSLO mod / LineB）+ `cross_chat_pending_registry_20260507.md` + 3 ADR（PROTOCOL-INTERFACE-001 + L1.5-001 + Phase 4 §8）+ `module_map_p4_snapshot.md` |
| **输出文件** | `architecture/backend_interface_refinement_<date>.md`（≤ 1 份）|
| **覆盖** | 8 场景**后端模块拆解** + 接口稳定面 audit + 跨模块协作 surface（特别是 5 路 TriggerOutcome × 6 下游模块 + 3 ECP 通道 × 13 EcpEventType + 4 active BB key）|
| **不做** | UI / 用户视角（Sub-Chat A 范围）；改 wire / 改 enum；任何代码实施；接口 surface 的实际重构；发明新 NEED-* 标签（cross_chat_pending_registry §3/§4 是真源） |
| **完成判据** | 8 场景每个有：① 模块拆解 ② 接口稳定面（已 ratified vs experimental）③ 跨模块 binding（如 plan_request → PlanRegistry.draft / commit_observations → L1.5 Pool.admit）④ LineB 兼容守护证据 ⑤ Phase 4 §8 0 漂移 |
| **入场 prompt** | 见独立文件 `backend_interface_refinement_chat_launch_prompt_20260507.md` |

### §3.3 与既有修复 chat 的关系（不冲突 / 不重复）

| 既有 chat（cross_chat_pending_registry §5） | 处理标签 | 与 Sub-Chat A/B 关系 |
|:--|:--|:--|
| **Chat 4 4-A 实施轨**（已存在）| NEED-P2.5-PLAN-INTEGRATION + NANOBOT-HEARTBEAT + ARCHIVE-LLM + disk-recover + capability-gating | **不重复** — Sub-Chat B 仅做 inventory，不实施；Chat 4 实施 |
| **DSG 协议升级 chat**（菜单画布主线，未启动）| NEED-P2.5-A + NEED-P3-B + NEED-P3-C | **不重复** — Sub-Chat B 仅 inventory persona/preset 接口面，不设计 schema；DSG 协议升级 chat 真设计 |
| **AR 工作区独立 chat**（菜单 UI，未启动）| NEED-P2.5-B + NEED-P3-D + NEED-P3-E | **不重复** — Sub-Chat A 写"用户视角占位 UI 流程"；AR 工作区 chat 真做 UI 控件 |
| **P3 wire 升级 ADR chat**（未启动）| NEED-P3-A + TODO(P3-Wire-PlanUI) | **不重复** — Sub-Chat A 在场景 5 写占位 stub UI；P3 ADR chat 真升级 wire |
| **LineB Editor smoke chat**（未启动）| FINDING-LB-1/2/3 + axis 1-6 | **不重复** — Sub-Chat B 把 LineB 列为接口稳定性硬约束证据；LineB smoke chat 真跑联机 |
| **P3 仿生升级 chat**（未启动）| TODO(P3-fold-bionic) + spreading + RefHealth | 8 场景**不直接覆盖** — 留 P3 chat 自管 |
| **P3 / A10 接入 chat**（未启动）| TODO(P3-multi-scene) + Castle↔Mecha | 场景 8 + 场景 2（A10 真识别）部分覆盖 — Sub-Chat B 仅 inventory placeholder 接口面 |

---

## §4 与现有 SSOT 的引用关系

| SSOT 文件 | 引用方式 | 不重写 |
|:--|:--|:--|
| `protocol_snapshot_p4.md` 28 章 | 本 doc §1 引用 §3 EcpEventType / §10 BB key / §17 ObservationSource / §18 BucketKind / §19 StagedRefKind / §20 9 Triggers + 5 路上行 / §23 Phase 4 §8 13 锁 / §27 跨链表 | ✅ 0 修改 |
| `module_map_p4_snapshot.md` 8 章 | 本 doc §1 引用 §1 部署拓扑 + §2 模块清单 + §4 主数据流 3 路径 | ✅ 0 修改 |
| `cross_chat_pending_registry_20260507.md` | 本 doc §3 引用 §3/§4/§5 修复 chat 路径 | ✅ 0 修改 / 0 新发明 NEED 标签 |
| 3 完成报告（DSG Chat 2 / GOSLO mod / LineB）| 本 doc §1 已交付能力列引用 §1 落地清单 + §3 测试结果 | ✅ 不审计已交付内容；只 audit user 期望覆盖 |
| `ar_app_flow_ui_design.md` | 本 doc §1 + §6 附录引用风格基线 + 工具柜道具列表 | ✅ 0 修改 |
| `parrot_behavior_rules.md §3.7` | 本 doc §1 引用观察者 vs 注意力模块边界 + Tool 体感红线 | ✅ 0 修改 |
| `sprint4_phase4_entry_20260430.md §8` | 本 doc §1 + §2 Finding-1 引用 13 决策锁 | ✅ 0 修改 |
| `sprint4_protocol_v2_ecp.md` | 本 doc §1 引用 ECP V2 设计 4 层（L0 EventEnvelope / Blackboard / EcpCommand+Ack / DSG-Ref 证据层）| ✅ 0 修改 |

---

## §5 引用源

- 启动 prompt：[`app_completion_master_chat_launch_prompt_20260507.md`](app_completion_master_chat_launch_prompt_20260507.md)
- 协议 SSOT：[`../protocol_snapshot_p4.md`](../protocol_snapshot_p4.md)
- 架构 quick-ref：[`module_map_p4_snapshot.md`](module_map_p4_snapshot.md)
- 跨 chat 真源：[`cross_chat_pending_registry_20260507.md`](cross_chat_pending_registry_20260507.md)
- App Flow 基线：[`ar_app_flow_ui_design.md`](ar_app_flow_ui_design.md)
- 需求清单：[`../requirements.md`](../requirements.md)
- 3 完成报告：DSG Chat 2 / GOSLO mod / LineB（路径见启动 prompt §1.2）
- GOSLO Manifest 协议：[`goslo_model_manifest_protocol_v1.md`](goslo_model_manifest_protocol_v1.md)
- GOSLO 残余债：[`goslo_modularization_residual_debt_20260506.md`](goslo_modularization_residual_debt_20260506.md)
- Chat 4 upgrade roadmap：[`../upgrade_roadmap.md`](../upgrade_roadmap.md)
- 行为契约：[`../parrot_behavior_rules.md §3.7`](../parrot_behavior_rules.md)
- Phase 4 §8 锁：[`sprint4_phase4_entry_20260430.md §8`](sprint4_phase4_entry_20260430.md)
- ECP V2 设计：[`sprint4_protocol_v2_ecp.md`](sprint4_protocol_v2_ecp.md)
- 派发文件：[`app_flow_requirements_interface_chat_launch_prompt_20260507.md`](app_flow_requirements_interface_chat_launch_prompt_20260507.md) + [`backend_interface_refinement_chat_launch_prompt_20260507.md`](backend_interface_refinement_chat_launch_prompt_20260507.md)

---

## §6 附录 — 像素画 UI 资产清单（user 自管美术）

> **本附录用途**：user 在启动 prompt 之外**特别要求**给出"需要完成像素画风格 UI 资产的表格"。
>
> **风格基线**（来自 `ar_app_flow_ui_design.md` §1 + §2）：
> - **2D 像素风 Meta UI** — 不与真实世界互动（不需要遮挡 / 碰撞 / 物理）
> - **主题（Phase 4-5）= 大小姐宅邸**（西式 / 维多利亚 / 蕾丝 / 暖色调）
> - **主题（P3 换肤）= 海盗**（深蓝 / 木质 / 黄铜 / 望远镜元素）
> - **参考风格**：星露谷物语（Stardew Valley）+ Paper Please + Last Report
>
> **优先级**（沿用 P0 = Sprint 4-5 必须 / P1 = P2.5 验证期 / P2 = P3 换肤 / P3 = 远期）：
>
> **使用方式**：user 按表逐项产出；Sub-Chat A 实施 UI 流程时**用占位推进**（Unity Editor placeholder sprite / 默认色块 + 标签），资产到位后批量替换；不阻塞协议 / 流程实施。

### §6.1 类 1 — 启动页（Splash / Boot）

| # | 资产 | 用途 | 规格建议 | 帧数 / 状态 | 优先级 |
|:--|:--|:--|:--|:--|:--|
| 1.1 | 启动 Logo（GOSLOParrot / ParrotCarriers）| 进入应用第一帧 | 320×240 px / 24-32 色板 | 静态 | P0 |
| 1.2 | 2D 像素加载动画 | 加载阶段循环（"正在 xxx"占位由文字承担）| 64×64 px sprite | 6-8 帧循环 | P0 |
| 1.3 | 启动专场过场动画 | 加载完成 → AR 场景的过渡（GOSLO 飞入 / 鹦鹉羽毛飞舞）| 320×240 px | 12-24 帧 | P0 |
| 1.4 | 启动页菜单背景（大小姐宅邸主题）| 类星露谷主菜单背景 | 1080×1920 px（竖）+ 1920×1080（横）| 静态 + 微动效（窗帘飘动 / 烛光闪）| P0 |
| 1.5 | 菜单按钮 9 项（开始 AR / 房间 / 管线 / 人设 / 权限 / 连接测试 / 音频 / 调试 / 设置）| 启动页菜单 | 240×48 px | normal / hover / pressed 3 态 | P0 |

### §6.2 类 2 — HUD（屏幕一角，可开关收纳）

| # | 资产 | 用途 | 规格建议 | 状态 | 优先级 |
|:--|:--|:--|:--|:--|:--|
| 2.1 | HUD 收纳态 icon | 收起时的小图标 | 48×48 px | static + tap pulse | P0 |
| 2.2 | HUD 横向展开背景 | 横屏时的 HUD 板 | 480×96 px | 9-slice 可拉伸 | P0 |
| 2.3 | HUD 竖向展开背景 | 竖屏时的 HUD 板 | 96×480 px | 9-slice 可拉伸 | P0 |
| 2.4 | HUD 状态图标（连接 / 音频 / 视频 / Brain 在房 / 网络 4 项）| 状态显示 | 24×24 px each | active / inactive / warning / error 4 态 | P0 |
| 2.5 | HUD 时间钟 | 时间显示 | 像素字体 + 8×8 钟表 icon | 静态文字 | P0 |
| 2.6 | HUD 天气 icon（晴 / 阴 / 雨 / 雪 4 项）| 天气显示 | 24×24 px | 6-8 帧微动效 | P1 |

### §6.3 类 3 — 工具柜（HUD 对角，可展开）

| # | 资产 | 用途 | 规格建议 | 状态 | 优先级 |
|:--|:--|:--|:--|:--|:--|
| 3.1 | 工具柜收纳态 icon | 收起时的小图标 | 48×48 px | static + tap pulse | P0 |
| 3.2 | 工具柜横向 / 竖向展开背景 | 工具栏底板 | 同 HUD 9-slice | — | P0 |
| 3.3 | 工具柜分隔线 / 拖手 | 折叠 / 展开方向 toggle | 16×16 px | — | P0 |

### §6.4 类 4 — 工具柜道具（占位优先 + 后续美化）

| # | 资产 | 用途 | 规格建议 | 状态 | 优先级 |
|:--|:--|:--|:--|:--|:--|
| 4.1 | **放大镜**（基础）| 放大手机画面 + UI；倍率可调 | 64×64 px icon + 圆形 alpha 蒙版（可拖动）| idle / dragging / zoom-in 3 态 | P0 |
| 4.1b | **海盗望远镜**皮肤 | 放大镜的 P3 换肤 | 同上 | — | P2 |
| 4.2 | **注意力框 / Bounding Box** | 用户拖动 2D 框圈出关注区域 | 4 角 corner sprite + 边框 9-slice | idle / dragging / placed / removing 4 态 | P0 |
| 4.3 | 简易行程单（待办 + 打勾）| 任务列表占位 | 240×320 px panel | empty / 1-N items | P1 |
| 4.4 | 2D 贴图箱（截图打卡）| 拖出贴纸到画面 | 96×96 px box icon + 6-12 张贴纸 | 各贴纸独立 | P2 |
| 4.5 | 任务按钮（4-6 个常用动作）| 触发 fly_to / animate / dispatch_task 等 | 64×64 px each | normal / hover / pressed 3 态 | P0 |
| 4.6 | 设置按钮 | 设置入口 | 同上 | — | P0 |
| 4.7 | 相机模式按钮（拍照 / 录制 placeholder）| 拍照入口 | 同上 | — | P0 |
| 4.8 | 2D 工作区入口按钮（报告 / 行程 / 反馈）| 进入 2D 工作区 | 同上 | — | P1 |

### §6.5 类 5 — 反馈消息（猫爪 + 纸条）

| # | 资产 | 用途 | 规格建议 | 状态 | 优先级 |
|:--|:--|:--|:--|:--|:--|
| 5.1 | 2D 像素猫爪 | 从屏幕边伸出，抓住纸条 | 96×128 px | 6-8 帧伸入 / 6-8 帧抽回 | P1 |
| 5.2 | 像素纸条（白底）| 纸条本体 | 240×96 px（折叠）+ 480×320 px（展开）| folded / expanding / expanded / shredding 4 态 | P1 |
| 5.3 | 纸条上的可读文字区域 | 文本展示 | 像素字体 12-16 px / 中英文双语 | — | P1 |
| 5.4 | 工作桌 + 垃圾桶（拖入目标）| 处理纸条的两个目标 | 各 128×128 px | accept / reject / hover 3 态 | P1 |

### §6.6 类 6 — 2D 工作区（Paper Please / Last Report 风）

| # | 资产 | 用途 | 规格建议 | 状态 | 优先级 |
|:--|:--|:--|:--|:--|:--|
| 6.1 | AR 画面遮挡背景（变暗 alpha）| 进入工作区时压暗 AR | 全屏 alpha gradient | 0% → 70% 黑 | P1 |
| 6.2 | 工作桌纹理 | 主操作区 | 1920×1080 px | 静态 | P1 |
| 6.3 | 文件夹 / 印章 / 红绿戳 | Paper Please 风操作元素 | 各 64×64 px / 96×96 px | normal / pressed | P2 |
| 6.4 | 2D 工作区入口过场（折叠展开）| 进入 / 退出动画 | 全屏 | 12 帧 | P1 |

### §6.7 类 7 — Plan 卡片 UI（NEED-P3-Wire-PlanUI 留 P3 ADR）

| # | 资产 | 用途 | 规格建议 | 状态 | 优先级 |
|:--|:--|:--|:--|:--|:--|
| 7.1 | Plan 卡片底板 | Plan UI 容器 | 480×640 px | normal / awaiting / approved / rejected / executing 5 态 | P2 |
| 7.2 | Step 列表行 | 单 step 显示 | 480×64 px | pending / running / done / failed 4 态 | P2 |
| 7.3 | Approve / Reject / Revise / Cancel 按钮 | 用户决策 | 各 96×48 px | 同 §6.5 3 态 | P2 |

### §6.8 类 8 — 角色 / 模型相关（GOSLO + 多模型）

| # | 资产 | 用途 | 规格建议 | 状态 | 优先级 |
|:--|:--|:--|:--|:--|:--|
| 8.1 | GOSLO 真模型 | 已交付（GOSLO.glb 29KB）| — | 已交付 | ✅ done |
| 8.2 | GOSLO Q 版头像（菜单 / 通知用）| 2D 头像 | 96×96 px | idle / talking / sleeping 3 态 | P1 |
| 8.3 | 自定义模型预览图（preview_image 字段）| ModelManifest preview | 256×256 px | 静态 | P1（per model）|
| 8.4 | 模型块 / 设定块 / 模式块 / 场景块（节点画布块外观）| NEED-P3-D node-canvas 节点 | 各 192×96 px | 4 颜色区分 + connection port | P2 |

### §6.9 类 9 — 字体 / 微动效 / 通用

| # | 资产 | 用途 | 规格建议 | 优先级 |
|:--|:--|:--|:--|:--|
| 9.1 | 像素字体（中英双语）| 全局 | 8 px / 12 px / 16 px 三套 | P0 |
| 9.2 | Loading dots / blinking cursor | 通用微动效 | 8×8 px 各 | P0 |
| 9.3 | 粒子效果（星光 / 羽毛 / 心形）| GOSLO 互动反馈 | 16×16 px each | P1 |
| 9.4 | 按钮 9-slice 边框（3 套：默认 / 激活 / 警告）| 全局复用 | 32×32 px 9-slice | P0 |
| 9.5 | 提示气泡（GOSLO 头顶 emoji）| 状态显示（开心 / 困惑 / 思考）| 64×64 px | 6-8 种表情 | P1 |

### §6.10 总计 + 占位策略

- **P0 必交付**（Sprint 4-5 推 UI 流程时缺一行不行的）：约 **18 项**（启动页 5 + HUD 6 + 工具柜 3 + 道具 P0 4 个 + 字体 + 9-slice + loading）
- **P1 可后期补**（占位推进，体验完整化前补）：约 **10 项**
- **P2 P3 换肤 / 远期**：约 **6 项**

**占位策略**（Sub-Chat A 必须遵守）：
1. 实施 UI 流程时使用 Unity Editor 默认 sprite + UI Toolkit placeholder
2. 用色块 + 文字标签代替最终 sprite（如紫色方块 + "MAGNIFIER"）
3. 所有 UI 控件先实现交互 + 事件 wire，sprite 替换走单独 PR
4. 美术资产到位后批量替换，不再改 wire / 流程

---

## §7 变更日志

- **2026-05-07**：本文创建。App 完成度总 chat 主 doc 收口产物。8 场景对账 + 5 finding + Sub-Chat A/B 派发 + 像素画 UI 资产清单（user bonus 要求）。0 wire 改动 / 0 新 NEED 标签发明 / 0 SSOT 重写。