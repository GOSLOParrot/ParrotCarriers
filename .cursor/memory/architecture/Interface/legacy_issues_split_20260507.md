---
status: ratified-inventory
category: legacy-issues
status_note: "完整遗留问题文档（要解决 / P3 完成 二分）。整合 cross_chat_pending_registry + upgrade_roadmap + sprint4_deferred + lore + dsg_decisions_master + ADR-L1.5-001 §4.2 + Phase 4 §8.6 全源。P2.5 要解决 30+ 项 + P3 完成 40+ 项 + 已知漂移 + grep 速查 + 修复 chat 派发表。含新 P2.5 需求：2D 独立工作区（nanobot 汇报批改 + Google 日程批改 + 工作区模块连接）。"
last_reviewed: 2026-05-07
ai_priority: high
ai_audience: "Sonnet 4.6（不要碰的硬约束）+ Opus 4.7 ×2（验证未漏标签）"
parent_doc: "../app_completion_master_audit_20260507.md"
related:
  - "../cross_chat_pending_registry_20260507.md (NEED-* 真源)"
  - "../../upgrade_roadmap.md (Chat 4 残余 18 项)"
  - "../sprint4_deferred_issues_and_bugs_20260504.md"
---

---
status: ratified-inventory
category: legacy-issues
status_note: "完整遗留问题文档（要解决 / P3 完成 二分）— 整合 cross_chat_pending_registry + upgrade_roadmap + sprint4_deferred_issues + lore/ideas + dsg_decisions_master + ADR-L1.5-001 §4.2 + Phase 4 §8.6 全源；此文是 SSOT，不发明新标签，只汇总+分类。"
last_reviewed: 2026-05-07
authoritative_for: "P2.5（要解决）+ P3（完成）+ 已知漂移 + grep 速查 + 修复 chat 派发的单一速查表"
parent_doc: "../app_completion_master_audit_20260507.md"
related:
  - "../cross_chat_pending_registry_20260507.md"
  - "../../upgrade_roadmap.md"
  - "../sprint4_deferred_issues_and_bugs_20260504.md"
  - "../adr_l1_5_source_dispatch_extension_space_20260504.md (§4.2 不允许提前做的事)"
  - "../sprint4_phase4_entry_20260430.md (§8.6 Phase 4 显式不做)"
  - "../dsg/dsg_decisions_master.md (§6 P3 defer 清单)"
  - "../../lore/ideas.md (P2/P3/P3.5 灵感)"
---

# ParrotCarriers — 完整遗留问题（要解决 / P3 完成 二分）

> **本文用途**：把分散在 7+ 份 SSOT 的"遗留问题"汇成 2 张大表（要解决 / P3）+ 1 张已知漂移表 + 1 张 grep 速查 + 1 张修复 chat 派发表。
>
> **不发明新标签**；新增标签必须先入 cross_chat_pending_registry §3/§4。
>
> **二分原则**：
> - **要解决（P2.5）** = Sprint 0-4 范围内 + 真机 spike 之前 + 不破 Phase 4 §8 锁 + 用户已认可推进
> - **P3 完成** = Sprint 5+ / 真机 spike 之后 / 涉及 wire ADR / 涉及大改架构 / 涉及 A10

---

## §0 严重度分级 + 状态字典

| 级别 | 含义 | 例 |
|:--|:--|:--|
| 🔴 **high** | 阻塞核心场景（"非鹦鹉模型也能跑"/"4 类块菜单跑通"等 user 钦定）| NEED-P2.5-A persona 外置 |
| 🟡 **mid** | 功能受限但 baseline 能跑 / 测试覆盖不全 | NEED-P2.5-PLAN-INTEGRATION |
| 🟢 **low** | 命名 / 注释 / 占位 / 优化 | TODO(P3-attention-spreading) |

---

## §1 要解决（P2.5 — Sprint 0-4 + 真机 spike 之前）

### §1.1 Chat 4 4-A 实施轨主场（5 项）

| # | 标签 | 严重度 | 描述 | 代码触点 | 修复 chat |
|:--|:--|:--|:--|:--|:--|
| 1.1.1 | NEED-P2.5-PLAN-INTEGRATION | 🔴 → 🟡 | 5 项 plan-* TODO 一锅端 | `plan_registry.start_executing` + `scheduler/{nodes.py,service.py,blackboard.py}` | Chat 4 4-A |
| 1.1.2 | NEED-P2.5-NANOBOT-HEARTBEAT | 🟡 | nanobot heartbeat HSET writer | `nanobot/channels/parrot_bus.py` 或 `parrot.bus.nanobot_consumer` | Chat 4 4-A |
| 1.1.3 | NEED-P2.5-ARCHIVE-LLM | 🟡 | 真 LLM 蒸馏 + Graphiti.add_episode | `dsg/archive/conversation.py:archive_to_graphiti` | Chat 4 4-A |
| 1.1.4 | TODO(Chat4-disk-recover) | 🟢 | DiskBackend.recover() | `brain/intent_workspace_backend.py:DiskBackend` | Chat 4 4-A |
| 1.1.5 | NEED-P3-CAPABILITY-GATING（可选）| 🟡 | Brain 启动 tool 按 manifest 过滤 | `brain/agent.py:_register_tools` | Chat 4 4-A 增量 / 推 P3 |

### §1.2 Chat 4 4-A 配套（与 1.1.1 一锅端）

| # | 标签 | 严重度 | 描述 | 代码触点 |
|:--|:--|:--|:--|:--|
| 1.2.1 | TODO(Chat4-plan-dispatch) | 🟡 | start_executing 真调 do_dispatch_task | plan_registry.py |
| 1.2.2 | TODO(Chat4-plan-nanobot-correlation) | 🟡 | scheduler 路由 plan_id+step_id+result_channel | scheduler/nodes.py + service.py |
| 1.2.3 | TODO(Chat4-plan-step-result-route) | 🟡 | service._listen_nanobot_results 路由 report_step_result | scheduler/service.py |
| 1.2.4 | TODO(Chat4-plan-step-timeout) | 🟡 | scheduler timeout 路由同样路径 | scheduler/service.py |
| 1.2.5 | TODO(Chat4-plan-bb-namespace) | 🟢 | scheduler/active_tasks BB namespace 注册 | scheduler/blackboard.py |

### §1.3 Chat 4 4-A 三阶段延迟归档（**新约束**，配 1.1.3）

| # | 标签 | 严重度 | 描述 | 代码触点 |
|:--|:--|:--|:--|:--|
| 1.3.1 | TODO(Chat4-archive-llm-defer) | 🟡 | 三阶段延迟归档约束（hot 内存 → cold 硬盘 → nanobot 闲时）| `l2b_graph.py:start_episode` + `dsg/archive/conversation.py` |
| 1.3.2 | TODO(Chat4-conversation-jsonl-schema) | 🟢 | data/conversations/{conv_id}/{snapshot,refs,timeline}.jsonl 格式定义 | 新建 `dsg/archive/conversation_format.py` |
| 1.3.3 | TODO(Chat4-nanobot-idle-detect) | 🟡 | nanobot 闲时检测信号（与 1.1.2 配合）| `dsg/triggers/idle_archive_trigger.py` |

### §1.4 4 类块菜单画布前置（user 钦定 NEED-P3-B 但 NEED-P2.5-A 是前置）

| # | 标签 | 严重度 | 描述 | 修复 chat |
|:--|:--|:--|:--|:--|
| 1.4.1 | NEED-P2.5-A | 🔴 | persona 外置 + 加载器 + BB key + 默认 goslo_parrot_default | DSG 协议升级 chat（与 NEED-P3-B/C 一锅端）|
| 1.4.2 | NEED-P2.5-B | 🟡 | Unity menu 暴露 DSG bucket / scene 切换 | AR 工作区独立 chat |
| 1.4.3 | **NEED-P2.5-OBSIDIAN-3SUB** | 🟡 | Obsidian 3 子类 IngestFilter 改造（用 meta.profile） | DSG 协议升级 chat（与 1.4.1 同 chat） |
| 1.4.4 | **NEED-P2.5-VISUAL-SELF-AWARE** | 🟡 | 4 级视觉自我感知 + Soul 8 条强制话术 | 同 1.4.1（与 persona 外置同 chat） |
| 1.4.5 | **NEED-P2.5-SCENE-2BASELINE** | 🟡 | SceneType 升 2 baseline（DESKTOP_WEBCAM + AR_HANDHELD） | 同 1.4.1（影响 Scene 块）|

### §1.5 测试 / 守护增量

| # | 标签 | 严重度 | 描述 | 修复 chat |
|:--|:--|:--|:--|:--|
| 1.5.1 | CC-1-echo-freeze-test | 🟢 | attention.config.echo payload schema 增量 cs_parity 守护 | Chat 4 4-C freeze test |
| 1.5.2 | CC-3-event-ingest-coverage | 🟢 | event_ingest 8KB / dedup / synthesized 测试覆盖 | Sub-Chat B 验证 |
| 1.5.3 | freeze-test-extension-rpc-method-name | 🟢 | RPC method name 常量化 + cs_parity | Chat 4 4-C |
| 1.5.4 | freeze-test-extension-noderefkind | 🟢 | NodeKind / EdgeKind / RefKind / RefTargetKind 4 项 freeze test cs_parity | Chat 4 4-C |
| 1.5.5 | doc-attach-helpers-13 | 🟢 | attach_helpers.md §1 列表扩展到 13 attach helper | Chat 4 末段 doc 微调 |
| 1.5.6 | doc-observer-event-bus-register | 🟢 | observer_event_bus.md §2 加 register_phase4_observers 显式描述 | Chat 4 末段 doc 微调 |

### §1.6 Editor / 联机 smoke 收口

| # | 标签 | 严重度 | 描述 | 修复 chat |
|:--|:--|:--|:--|:--|
| 1.6.1 | LineB Editor 6-axis 双跑 smoke | 🟡 | cognitive 时序 / selection-C reason / 1.9s 预算 / attention.threshold / DSG 文本提取 / Multi-Agent Handoff | LineB Editor smoke chat |
| 1.6.2 | Phase 4 联机 smoke #1/#2 (perch_to_finger / identify_object) | 🟡 | defer 真机 spike chat | 真机 spike chat |
| 1.6.3 | FINDING-LB-1 ADC 部署门槛 | 🟡 | Google Cloud Service Account JSON 部署 | 同 1.6.1 |
| 1.6.4 | FINDING-LB-2 STT 构造期校验 | 🟢 | doc-only finding | 同 1.6.1 |
| 1.6.5 | FINDING-LB-3 text_source_filter regex 与 ASR 转写差异 | 🟡 | axis-5 联机确认 | 同 1.6.1 |

### §1.7 Pre-existing breakage（独立审计 chat 修）

| # | 标签 | 严重度 | 描述 | 修复 chat |
|:--|:--|:--|:--|:--|
| 1.7.1 | BUG-T1 test_identify_object.py ImportError | 🟢 | id_module._match_staged 路径与 env gate 冲突 | 独立审计 chat |

### §1.8 P2 收尾延期项（不阻塞 Phase 4）

| # | 标签 | 严重度 | 描述 |
|:--|:--|:--|:--|
| 1.8.1 | Brain 优雅退出 | 🟢 | AgentSession cleanup + 心跳停止 + Bus deregister |
| 1.8.2 | Scheduler._connect_livekit 补完 | 🟢 | P1 遗留 stub |
| 1.8.3 | 用户完成 fly/dance/idle/thinking 动画 | 🟢 | Minecraft 风（user 自管美术） |
| 1.8.4 | 像素画小纸条 MVP | 🟢 | UI Canvas + 2D 像素 sprite + RPC 触发（lore §海盗主题 配套）|
| 1.8.5 | Google OAuth 真实联调 | 🟡 | CalendarTrigger / MessageTrigger 用户账号授权 |

### §1.9 P2.5 准备项（部分已完成）

| # | 标签 | 严重度 | 状态 |
|:--|:--|:--|:--|
| 1.9.1 | AR App Flow / UI 设计基线 | ✅ | `ar_app_flow_ui_design.md` 已落 |
| 1.9.2 | AR App 工程计划追溯 | ✅ | `ar_app_plan.md` 已留档 |
| 1.9.3 | 视频流采样 skill | ✅ | `livekit-unity-video-publish/SKILL.md` 已落 |
| 1.9.4 | AR Foundation 规则 | ✅ | `ar-foundation.mdc` 已落 |
| 1.9.5 | Cursor 工作区规则模块隔离策略 | 🟢 | 推 Phase 5+ |
| 1.9.6 | 新 skill 收集（XR Interaction Toolkit / Unity Sentis）| 🟢 | 推 P3 |
| 1.9.7 | 猫娘 cron 任务（Obsidian → Gemini Flash）| 🟡 | 推 nanobot 协作 chat |
| 1.9.8 | 三级调度 Priority 子树 | 🟢 | E2 P2 任务；推 P3 完整 BT |
| 1.9.9 | ResourceLockManager 骨架 | 🟢 | E5 P2 任务；推 P3 |

---

## §2 P3 完成（Sprint 5+ / 真机 spike 之后 / wire ADR / 大改架构 / A10）

### §2.1 wire 升级 ADR chat 范围

| # | 标签 | 严重度 | 描述 | 同 ADR 建议 |
|:--|:--|:--|:--|:--|
| 2.1.1 | NEED-P3-A body_state 解锁评估 | 🟡 | Option A controller_body_state / Option B 升级 string；触动 Phase 4 §8 wire 锁 → 必须新 ADR | 与 2.1.2 同 ADR |
| 2.1.2 | TODO(P3-Wire-PlanUI) | 🟡 | Plan UI 新 EcpEventType（plan.proposed/approved/rejected/revised）+ Plan card UI + EcpCommand 回流；触动 wire | 与 2.1.1 同 ADR |
| 2.1.3 | NEED-P3-CAPABILITY-GATING（动态注册）| 🟡 | active model 切换时动态注销 / 注册 LLM tool；触动 livekit-agents AgentSession | P3 wire ADR 之后 |

### §2.2 4 类块菜单画布主线（DSG 协议升级 chat 主场）

| # | 标签 | 严重度 | 描述 |
|:--|:--|:--|:--|
| 2.2.1 | NEED-P3-B | 🔴 | 4 类块统一注册表（model / persona / mode / scene）每类 ID 命名空间 + 注册表 + 数据格式 + 加载器 + active BB key + 切换事件 |
| 2.2.2 | NEED-P3-C | 🟡 | 预设 schema = 4 active ID 命名快照 (data/presets/<id>.json) |
| 2.2.3 | NEED-P3-MODE-ROLEPLAY | 🟡 | Mode 块加 ROLEPLAY flag（与 Obsidian-设定-Roleplay 联动）|

### §2.3 AR 工作区独立 chat（菜单 UI）

| # | 标签 | 严重度 | 描述 |
|:--|:--|:--|:--|
| 2.3.1 | NEED-P3-D | 🟢 | Unity menu UI = node-canvas（ComfyUI / n8n / Unreal Blueprint 风）|
| 2.3.2 | NEED-P3-E | 🟢 | 默认 fallback 菜单（列表 + 保存 + 恢复默认）|
| 2.3.3 | NEED-P3-PIRATE-SKIN | 🟢 | 海盗主题换肤（眼罩 / 望远镜 / 镜片滤镜 / 半边黑色）ScriptableObject swap |

### §2.4 P3 仿生升级 chat

| # | 标签 | 严重度 | 描述 | 代码触点 |
|:--|:--|:--|:--|:--|
| 2.4.1 | TODO(P3-fold-bionic) | 🟢 | RustworkX subgraph fold / Cluster / VF2++ 真实施 | `dsg/l2b/intent_event_boundary.py:NoOpFoldStrategy` |
| 2.4.2 | TODO(P3-attention-spreading) | 🟢 | Spreading Activation 真迭代扩散 | `dsg/l2b/attention/mechanism.py:SpreadingActivationPlaceholder` |
| 2.4.3 | TODO(P3-RefHealth) | 🟢 | refs.verify_ref URL / Graphiti / Obsidian 三类真验证 | `dsg/l1_5/ref_table.py:verify_ref` |
| 2.4.4 | NEED-P3-NOVELTY-DECAY | 🟢 | novelty 字段衰减算法 | `dsg/l2b/attention/decay.py` |
| 2.4.5 | NEED-P3-HABITUATION | 🟢 | habituation_count 累加路径 | 同上 |
| 2.4.6 | NEED-P3-GHOST-AUTO | 🟢 | confirmation=GHOST 自动转换 | 同上 |

### §2.5 P3 / A10 接入 chat

| # | 标签 | 严重度 | 描述 |
|:--|:--|:--|:--|
| 2.5.1 | TODO(P3-multi-scene) | 🟢 | SceneRegistry 多 SceneType profile（HOME_INDOOR / OUTDOOR / LIBRARY / KITCHEN）|
| 2.5.2 | A10-接入 / Castle ↔ Mecha | 🟡 | 新 cross-process 协议 + Redis Channel + A10 心跳 + spawn / despawn |
| 2.5.3 | A10-source-meta-factory | 🟢 | `register_source_meta_factory("cv_a10", a10_factory)` 装哪些字段 |
| 2.5.4 | A10-confidence-decay | 🟢 | A10 节点自动 confidence decay（外观漂移问题）|
| 2.5.5 | A10-reid-cross-source | 🟢 | A10 ↔ IDENTIFY_OBJECT 节点合并（reid_hash）|
| 2.5.6 | A10-AR-coord-sensors | 🟢 | A10 适配 AR 坐标 + 手机传感器 + SAM2/DINOv2 + 软件建图 + VPS |
| 2.5.7 | NEED-P3-IMPOSSIBLE-EVENT | 🟢 | 不可能事件检测（电视瞬移）→ 不进 L1.5 标不可信 |
| 2.5.8 | NEED-P3-DUP-INSTANCE-CONFIRM | 🟢 | 同类第二实例需用户确认才进 L2-B |
| 2.5.9 | NEED-P3-DSG-CROSS-SOURCE-AXIS | 🟢 | 跨 source 状态机分轴（按 NodeKind / 按 source / 双轴正交）|

### §2.6 多场景 / 新 Scene profile（P3 远期）

| # | 标签 | 严重度 | 描述 |
|:--|:--|:--|:--|
| 2.6.1 | NEED-P3-OUTDOOR-LIGHTSHOW | 🟢 | OUTDOOR_LIGHT_SHOW Scene（户外暗 / 倾向语音少视觉）|
| 2.6.2 | NEED-P3-AR-WORLD-LOCKED | 🟢 | AR_WORLD_LOCKED Scene（预建图 / LiDAR / ARWorldMap）|
| 2.6.3 | NEED-P3-MULTIPLAYER | 🟢 | MULTIPLAYER_PRESENCE Scene（光遇式多用户 GOSLO）|

### §2.7 lore/ideas 灵感（P3 / P3.5 远期）

| # | 标签 | 严重度 | 描述 |
|:--|:--|:--|:--|
| 2.7.1 | NEED-P3-PIRATE-SKIN（同 2.3.3）| 🟢 | 海盗主题换肤 |
| 2.7.2 | NEED-P3-FONT-PIXEL-MODERN | 🟢 | 像素羊皮纸现代文本字体可读性（参考 Last Report / Paper Please） |
| 2.7.3 | NEED-P3-CAT-PAW-PAPER | 🟢 | 猫爪伸出 + 像素纸条递交动效 |
| 2.7.4 | NEED-P3-VPS-PREMAPPED | 🟢 | 自托管 VPS + 预建图 / 3D 禁飞区 |
| 2.7.5 | NEED-P3-iOS-LIDAR | 🟢 | iOS / iPad LiDAR 实时碰撞 |
| 2.7.6 | NEED-P3-iOS-ARWORLDMAP | 🟢 | iOS ARWorldMap "隔天续场" |
| 2.7.7 | NEED-P3.5-MULTI-DEVICE | 🟢 | 多摄像头 / 麦克风指定（DroidCam / OBS / 副摄）|
| 2.7.8 | NEED-P3.5-MULTI-SPEAKER | 🟢 | 多人同时说话选轨 + turn 对齐 |
| 2.7.9 | NEED-P3-VISION-ATTENTION-DRIFT | 🟢 | 视频流持续喂 LLM 时避免注意力漂移（PerceptionSupervisor 升级）|
| 2.7.10 | NEED-P3-WEB-CONSOLE | 🟢 | Web 控制台（复杂管理 / Graphiti 图谱 / 移到 Web 端）|
| 2.7.11 | NEED-P3-CHAT-GROUP | 🟢 | 群聊（Telegram 群 + LobeChat）|
| 2.7.12 | NEED-P3-MEMORY-VALIDITY | 🟢 | MemoryValidity Ebbinghaus 衰减公式 + 置信度阈值 |
| 2.7.13 | NEED-P3-SKILL-DISTILL | 🟢 | Skill Distillation（工作流 → skill 自动提炼）|

### §2.8 ADR-L1.5-001 §4.1 子类化触发条件（**当前未触发，留监控**）

| # | 触发条件 | 当前状态 | 升级动作 |
|:--|:--|:--|:--|
| 2.8.1 | ≥3 source 字段差异 ≥3 个 | 未触发（meta dict）| 升 typed Pydantic model |
| 2.8.2 | ≥2 source 行为多态 | 未触发（Strategy 注册表）| 升 SemanticNode 子类 |
| 2.8.3 | isinstance 反复手写 | 未触发 | 升 typed dispatch |

> **关键**：触发 = 起新 ADR `supersedes: [ADR-L1.5-001]`；当前 0 触发 = 继续 meta dict + factory hybrid。

---

## §3 已知漂移（不修，仅 doc 化；保留追溯）

| # | 项 | 状态 | 处置 |
|:--|:--|:--|:--|
| 3.1 | `transient/last_sighting_event` BB key 无写者（Phase 4 终审计 Finding A） | proposed (low) | observer_event_bus.md §5 已标 |
| 3.2 | Phase 4 临时实现 6 项 standalone | experimental | 接口 frontmatter 全标 status=experimental |
| | - FocusBboxThreshold（Phase 4 临时阈值器，非 L3）| | dsg/attention/threshold.py 文件头明写 |
| | - selection-C `_state_context.py`（Phase 4 W4-5 实施口径）| | brain/tools/_state_context.py |
| | - identify_object 1.9s 预算 | | brain/tools/identify_object.py |
| | - IngestRunner factory dispatch（Phase 4→5 transition）| | dsg/ingest/runner.py |
| | - SpreadingActivationPlaceholder（委托 BoundedBfsActivation）| | dsg/l2b/attention/mechanism.py |
| | - archive_to_graphiti（仅计数）| | dsg/archive/conversation.py |
| 3.3 | Phase 4 W6-7 RefBinding 100% UNRESOLVED | 设计意图（非 bug）| ref_binding_v1.md §5 + refs_hint_writer.md §4 已标 |
| 3.4 | LineB STT-LLM-TTS 时序差异（200-600ms 多）| pending Editor smoke axis-1 | selection_c_state_context.md §4 已标 |
| 3.5 | photo_upload_server hardcoded port 7889 | accepted | Phase 5+ 容器化时改 env-driven |
| 3.6 | 单 PyDiGraph 无 priority queue / TTL eviction / size cap | 设计空间留白 | Chat 2 / P3 仿生升级 chat |
| 3.7 | gemini_transcript_extractor 旧名 alias shim | accepted | 保留向后兼容；不删 |
| 3.8 | DESKTOP_PROFILE 单一 profile（非 2 baseline）| pending NEED-P2.5-SCENE-2BASELINE | DSG 协议升级 chat 修复 |

---

## §4 grep 速查表

```bash
# Chat 4 4-A 主场（要解决）
rg "TODO\(Chat4-" src/

# P3 仿生 / A10
rg "TODO\(P3-" src/

# 跨 chat 文档登记（不在源码 — 仅 markdown）
rg "NEED-P2\.5-" .cursor/memory/architecture/
rg "NEED-P3-" .cursor/memory/architecture/

# Phase 4 §8 0 漂移守护
pytest tests/test_ecp_event/test_cs_parity.py -v          # 4/4
pytest tests/test_dsg/test_l2b_node_source_dispatch.py -v # 11/11
pytest tests/test_dsg/test_compatibility_with_phase4.py -v # 11/11
pytest tests/test_dsg/test_terminology_no_collision.py -v  # 3/3

# 全量 baseline
pytest -q --ignore=tests/integration --ignore=tests/test_ecp_event/test_identify_object.py
# → 415 passed (含 GOSLO mod) / 352 passed (DSG Chat 2 之后 GOSLO 之前)
```

---

## §5 修复 chat 派发表（汇总）

| 修复 chat | 处理标签 | 触发条件 |
|:--|:--|:--|
| **Chat 4 4-A 实施轨**（已存在）| 1.1.1-1.1.5 + 1.2.1-1.2.5 + 1.3.1-1.3.3 + 1.5.1（4-C）+ 1.5.2 + 1.5.3-1.5.4（4-C）+ 1.5.5-1.5.6（doc 末段）| 主战场 |
| **DSG 协议升级 chat**（菜单画布主线）| 1.4.1（NEED-P2.5-A）+ 1.4.3（OBSIDIAN-3SUB）+ 1.4.4（VISUAL-SELF-AWARE）+ 1.4.5（SCENE-2BASELINE）+ 2.2.1-2.2.3（NEED-P3-B/C/MODE-ROLEPLAY）+ 3.8 | 4 类块统一接口设计 |
| **AR 工作区独立 chat**（菜单 UI）| 1.4.2（NEED-P2.5-B）+ 1.8.4（猫爪纸条 MVP）+ 2.3.1-2.3.3（NEED-P3-D/E/PIRATE-SKIN）| 用户视角菜单 UI |
| **P3 wire 升级 ADR chat** | 2.1.1（NEED-P3-A）+ 2.1.2（PlanUI）建议同 ADR | 触动 wire 锁 |
| **P3 仿生升级 chat** | 2.4.1-2.4.6 | 仿生算法落地 |
| **P3 / A10 接入 chat** | 2.5.1-2.5.9 + 2.6.1-2.6.3 | A10 / VPS / 多 Scene |
| **LineB Editor smoke chat** | 1.6.1 + 1.6.3-1.6.5 | LineB 联机 axis 1-6 |
| **真机 spike chat** | 1.6.2 + CC-2 真机验证 | 真机 #1/#2 |
| **独立审计 chat** | 1.7.1 + 任何架构守护 audit | 独立 |
| **独立 nanobot 协作 chat**（备选）| 1.1.2 + 1.3.3 + 1.9.7 | 与 Chat 4 替代路径 |
| **P3 远期 chat（lore 灵感）** | 2.7.1-2.7.13 | P3 远期 |
| **P3.5 玩法扩展 chat** | 2.7.7-2.7.8 | 多设备 / 多 speaker |

---

## §6 维护规则

1. **新 chat 启动时**：把 §5 对应行的标签抄到 chat 启动 prompt §1 入场必读
2. **chat 实施完成时**：把已 close 的标签从 §1 / §2 转移到 §7（不删，标 `✅ resolved-by <chat doc>`）
3. **新增标签**：先在 cross_chat_pending_registry §2 加索引行 + §3 / §4 加详情，**再回查本表 §1 / §2 确认归属**，再去源码加 TODO 注释
4. **改 wire / 改 enum / 改 namespace**：必须新 ADR；ADR 落地后才更新本表

---

## §7 已 resolved 历史（创建时为空，逐条 archive）

（待 chat 实施完成后填）

---

## §8 引用源（汇总）

- 跨 chat 真源：`cross_chat_pending_registry_20260507.md`
- Chat 4 upgrade roadmap：`upgrade_roadmap.md`
- Phase 4 deferred：`sprint4_deferred_issues_and_bugs_20260504.md`
- ADR-L1.5-001 §4.2 不允许提前做：`adr_l1_5_source_dispatch_extension_space_20260504.md`
- Phase 4 §8.6 显式不做：`sprint4_phase4_entry_20260430.md`
- DSG decisions master §6 P3 defer：`dsg/dsg_decisions_master.md`
- lore 灵感：`lore/ideas.md`
- 接口设计 v0：`Interface/interface_design_and_how_todo_v0_20260507.md`
- 接口设计补丁：`Interface/interface_design_supplement_20260507.md`
- 概念词典：`Interface/concept_dictionary_20260507.md`
- 菜单设计：`Interface/menu_design_complete_20260507.md`

---

## §9 变更日志

- **2026-05-07**：本文创建。整合 cross_chat_pending_registry + upgrade_roadmap + sprint4_deferred + lore + dsg_decisions_master + ADR-L1.5-001 §4.2 + Phase 4 §8.6 全源；要解决（P2.5）9 大类 30+ 项 + P3 完成 8 大类 40+ 项 + 已知漂移 8 项 + grep 速查 + 修复 chat 派发表 12 行。