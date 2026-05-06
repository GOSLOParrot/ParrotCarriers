---
status: stage-1-draft
category: chat-4-stage-1
chat_4_stage: "Stage 1 — 4-B-req"
status_note: "Chat 4 接口提炼 Stage 1 — App 流程 inventory。从 ar_app_flow_ui_design §4 8 步逐步展开，每步列触动的能力 + 接口面候选 + 开放问题。**完全不绑代码**——仅 cite doc anchor。"
last_reviewed: 2026-05-07
authoritative_for: "Chat 4 接口提炼的 App 流程驱动源 SSOT；Stage 2 capabilities_inventory 的输入；Stage 3 接口提炼的 driven_by 真源（app-flow:step-N 来源）"
parent_doc: "INDEX.md"
parent_plan: "../architecture/interface_extraction_plan_20260507.md §7.5.3 Stage 1"
ai_priority: high
ai_audience: both
sources:
  - "../architecture/ar_app_flow_ui_design.md (App Flow / UI / 工具柜 / 注意力工具)"
  - "../architecture/ar_feature_vision.md (一句话愿景 + 五维收口)"
  - "../parrot_behavior_rules.md (调度三层 / 意识三层 / Tool 体感红线)"
  - "../architecture/ar_camera_interaction_survey.md (拍照互动调研)"
---

# Chat 4 Stage 1 — App 流程 Inventory

> **本文用途**：把 ar_app_flow_ui_design §4 8 步 App 流程**逐步展开**，每步列：
> 1. 一句话流程描述
> 2. 触动的**能力**（capability candidates，留 Stage 2 反推填实）
> 3. 触动的**接口面**（interface candidates，按拓扑边界初步分桶）
> 4. **开放问题**（如果有）
> 5. **driven_by**（来自哪份 doc 的哪一段）
>
> **重要**：本文**不绑代码** — 不写 `attach_*` / `class XYZ`；只描述"用户体验上需要什么"。代码反推留 Stage 4 grep 验证。

---

## §0 TL;DR

```
8 步 App Flow（来自 ar_app_flow_ui_design §4）：

[1] 启动页 / 主菜单                ← user 选场景 / 管线 / 房间 / 权限
[2] 选择或确认初始配置             ← BrainAgent 管线 / 4 类块预设
[3] 权限与连接检查                  ← 摄像头 / 麦克风 / 网络 / LiveKit / Brain presence
[4] 2D 像素加载动画                 ← Loading screen，无后端接口
[5] 2D 像素转场                     ← 同上
[6] 进入 AR 主场景                  ← Brain agent join / Unity 入房 / 视频流启动
[7] HUD / 工具柜按需展开            ← 用户开关 HUD / 工具柜
[8] 工具或 2D 工作区按需进入        ← 放大镜 / 注意力框 / 拍照 / 报告
```

每步触动的接口面分布：

| 步 | wire | cross-process | in-process | capability |
|:--|:--:|:--:|:--:|:--:|
| 1 | ✅ | ✅ | — | ✅ |
| 2 | ✅ | ✅ | ✅ | ✅ |
| 3 | ✅ | ✅ | ✅ | — |
| 4-5 | — | — | — | — |
| 6 | ✅ | ✅ | ✅ | ✅ |
| 7 | ✅ | — | ✅ | ✅ |
| 8 | ✅ | ✅ | ✅ | ✅ |

---

## §1 step-1 — 启动页 / 主菜单

### §1.1 一句话

User 在 AR 启动后看到一个 2D 像素风菜单，列出"开始 AR 主场景 / 选择房间 / 选择 BrainAgent 管线 / 选择人设 / 选择场景 / 权限检查 / 连接测试 / 音频入口 / 调试面板 / 设置"等候选项。

### §1.2 触动的能力

| capability candidate | 来源 |
|:--|:--|
| `app-launch-menu`（启动页 UI 渲染 + 选项加载）| ar_app_flow §5 |
| `model-block-selector`（模型块 = ID 命名空间 + 注册表 + 加载器）| NEED-P3-B |
| `persona-block-selector`（设定块 = persona file + 加载器）| NEED-P2.5-A |
| `mode-block-selector`（模式块 = BehaviorMode flags）| 已有 set_mode tool |
| `scene-block-selector`（场景块 = SceneType + SceneProfile + bucket 集合）| NEED-P3-B + DSG SceneRegistry |
| `preset-loader`（4 active ID 命名快照）| NEED-P3-C |
| `default-fallback`（列表选择 + 保存预设 + 恢复默认）| NEED-P3-E |

### §1.3 触动的接口面（候选）

| 拓扑 | 接口面 candidate | 状态 |
|:--|:--|:--|
| **wire** | （Brain ↔ Unity）`active_*_id` 4 BB key 切换事件（与 NEED-P3-B 联动）| proposed-new |
| **cross-process** | `data/presets/<preset_id>.json` 读盘 | proposed-new |
| **capability** | 4 类块（model/persona/mode/scene）注册表 API | proposed-new |
| **capability** | `parrot.brain.persona_loader.load(persona_id)` | proposed-new（NEED-P2.5-A）|
| **capability** | Unity menu UI（node-canvas vs 列表 fallback）| proposed-new（NEED-P3-D + NEED-P3-E）|

### §1.4 开放问题

| Q | 推到哪 | 真源 |
|:--|:--|:--|
| 启动页菜单是否就是 4 类块画布？ | DSG 协议升级 chat | NEED-P3-B/D 联动 |
| 调试折叠项 vs 正式选项 边界 | AR 工作区独立 chat | ar_app_flow §5 |
| 启动页是否在 user 进 LiveKit Room 之前完成全部选择？ | DSG 协议升级 chat | 影响 BB key 写入时机 |

### §1.5 driven_by

- ar_app_flow §4 step 1 + §5 启动页候选菜单
- ar_app_flow §3 user 原话："这个是个给我自己用的 demo / 启动页菜单选项 / 像星露谷物语那样"

---

## §2 step-2 — 选择或确认初始配置

### §2.1 一句话

User 在启动页 4 类块（模型 / 设定 / 模式 / 场景）选好后，确认配置（也可加载已有预设），ParrotApp 把 4 个 active ID 写到 BB / 配置文件。

### §2.2 触动的能力

| capability candidate | 来源 |
|:--|:--|
| `preset-save` / `preset-load`（user 命名 + 序列化到 `data/presets/<name>.json`）| NEED-P3-C |
| `active-id-writer`（4 BB key：`global/active_model_id` / `global/active_persona_id` / `global/active_mode` / `global/active_scene`）| NEED-P3-B |
| `config-validator`（4 ID 是否在各自注册表中）| proposed-new |
| `fallback-default`（恢复默认：GOSLO_default + goslo_parrot_default + COMPANION + main_scene）| NEED-P3-E |

### §2.3 触动的接口面（候选）

| 拓扑 | 接口面 candidate | 状态 |
|:--|:--|:--|
| **wire** | Unity → Brain：`config.applied` EcpEvent（4 active ID 通知）| proposed-new |
| **cross-process** | Redis BB write `global/active_*_id` 4 keys | proposed-new |
| **cross-process** | 文件系统 `data/presets/<name>.json` 读写 | proposed-new |
| **in-process** | `mode_watcher` 既有但需扩展到 4 类块联动 | proposed-upgrade |
| **capability** | 4 类块注册表 API | proposed-new |

### §2.4 开放问题

| Q | 推到哪 | 真源 |
|:--|:--|:--|
| 4 类块切换的 atomic 性（是否一组一起切，还是逐个切）？ | DSG 协议升级 chat | NEED-P3-B |
| 切换中途打断（user 正在选 model 时来电话）的恢复语义？ | 同上 + livekit-unity-lifecycle | C7 + NEED-P3-B |

### §2.5 driven_by

- ar_app_flow §4 step 2 + §3 user 原话："模型 / 设定 / 模式 三者可以快速各自切换 / 预设和绑定随意组合"
- goslo_modularization_residual_debt §4.3 4 类块结构

---

## §3 step-3 — 权限与连接检查

### §3.1 一句话

User 进 AR 之前，ParrotApp 检查摄像头 / 麦克风 / 网络 / LiveKit token mint / Brain presence；不通过则给可点击的 fix 提示，通过则允许进 AR。

### §3.2 触动的能力

| capability candidate | 来源 |
|:--|:--|
| `permission-camera` / `permission-mic`（Android runtime permission）| C5 + ar-foundation-samples skill |
| `network-quality-probe`（WiFi 强度 / 弱网检测）| C12 网络质量提示 |
| `livekit-token-mint`（拿 JWT）| 已有 token_mint endpoint |
| `livekit-room-connect`（presence 检测）| 已有 livekit-unity-lifecycle |
| `brain-presence-probe`（Brain agent 是否已 join）| 既有 EcpState 心跳 + connection_health |

### §3.3 触动的接口面（候选）

| 拓扑 | 接口面 candidate | 状态 |
|:--|:--|:--|
| **wire** | `parrot.ecp.health` topic（connection.health.changed）| ✅ locked（Phase 4 §8 L4 inline envelope）|
| **wire** | LiveKit room.connect / disconnect API | ✅ locked（client-sdk-unity）|
| **cross-process** | HTTP `/token_mint` endpoint | evolving |
| **in-process** | LifecycleStateMachine 11 态（Unity 端）| ✅ ratified（livekit-unity-lifecycle skill）|
| **capability** | Permission UI（Android Settings deep-link fallback）| evolving |

### §3.4 开放问题

| Q | 推到哪 | 真源 |
|:--|:--|:--|
| 权限失败的 user-facing 文案 | AR 工作区 chat | ar_app_flow §3 user 原话："启动有点丑" |
| 连接测试是 user-trigger 还是 auto？ | AR 工作区 chat | ar_app_flow §5 |

### §3.5 driven_by

- ar_app_flow §4 step 3 + §5 候选菜单中的"权限检查 / 连接测试"行
- ar_app_flow §3 user 原话："权限和连接那块可能有点不流畅 / 不如做成启动页的菜单选项"

---

## §4 step-4-5 — 加载动画 + 转场

### §4.1 一句话

2D 像素加载动画 + 2D 像素转场。**纯 UI 层，无后端接口面**。

### §4.2 driven_by

- ar_app_flow §4 step 4-5
- ar_app_flow §3 user 原话："正常的 2D 像素加载动画就行"

### §4.3 备注

inventory 时 step-4-5 不产生接口面候选；仅在 INDEX.md 中显式标"无后端接口"。

---

## §5 step-6 — 进入 AR 主场景

### §5.1 一句话

Brain agent join LiveKit room → Unity 端入房 + ARCore session 启动 + WebCam track publish + 视频流启动；GOSLO（鹦鹉）spawn 到 AR 场景；进入"待对话"状态。

### §5.2 触动的能力

| capability candidate | 来源 |
|:--|:--|
| `brain-agent-bootstrap`（attach `event_ingest` / `ecp_state_ingest` / `attention_config_handler` / `transcript_extractor` 等）| LineB + Phase 4 W2 收口 |
| `pipeline-line-a-or-b`（env-gate `PARROT_LLM_PIPELINE`）| LineB |
| `unity-room-connect`（livekit-unity-lifecycle 11 态 boot）| C1 |
| `ar-session-start`（ARCore plane / anchor / camera）| C2 + ar-foundation-api skill |
| `webcam-track-publish`（首帧黑预热 + 设备启发式选择）| ar_feature_vision §二 |
| `goslo-spawn`（ParrotController + ModelDriver 加载 active_model_id manifest）| GOSLO Manifest + Step 2 active ID |
| `gemini-live-session-start`（Phase 4 LineA）/ `stt-llm-tts-pipeline-start`（LineB）| LineB |
| `dsg-l1_5-pool-init`（6 BucketKind + Desktop scene profile）| DSG-POOL-V1 |
| `intent-workspace-attach`（IntentWorkspaceBackend init）| brain_protocol_intent_workspace_v1 |
| `plan-registry-attach`（PlanRegistry init）| brain_protocol_plan_v1 |
| `observer-event-bus-attach`（5 observer 注册）| Phase 4 W1-2 + W6-7 + W8 |

### §5.3 触动的接口面（候选）

| 拓扑 | 接口面 candidate | 状态 |
|:--|:--|:--|
| **wire** | `parrot.ecp.state` 1Hz heartbeat 启动 | ✅ locked（Phase 4 §8 L1）|
| **wire** | `parrot.ecp.health` connection.health.changed | ✅ locked |
| **wire** | LiveKit RPC 7 method 注册（flyTo / animate / setVideoTier / captureSnapshot / capturePhoto / dispatch_task / token_mint）| ✅ locked |
| **wire** | `parrot.ecp.event` topic + EcpEventDispatcher 注册 | ✅ locked（Phase 4 §8 L2）|
| **cross-process** | Redis BB read `global/active_*_id` 4 keys | proposed-new（与 step-2 联动）|
| **cross-process** | Redis Pub/Sub channel 订阅启动 | ✅ ratified（bus_v4）|
| **in-process** | 5 attach helper boot 序 | evolving |
| **in-process** | 5 observer event_bus 注册 | evolving |
| **in-process** | DSG TriggerOutcome 5 路上行注册 | ✅ ratified（DSG-V2）|
| **in-process** | IngestRunner.commit_observation 单一写门 | ✅ ratified |
| **capability** | LineA / LineB pipeline env-gate | ✅ ratified（LineB §2.1）|
| **capability** | ModelDriver 反射实例化 IParrotController | ✅ ratified（GOSLO Step 2）|
| **capability** | Brain Agent boot 序文档化 | proposed-upgrade（doc 散落）|

### §5.4 开放问题

| Q | 推到哪 | 真源 |
|:--|:--|:--|
| Brain Agent boot 序的 deterministic 顺序（哪个 attach 先跑）？ | Chat 4 4-B-in（in_process/attach_helpers.md）| Phase 4 W2 收口 |
| AR session start 失败时 user 看到什么？ | AR 工作区 chat | ar_app_flow §3 user 原话隐含 |

### §5.5 driven_by

- ar_app_flow §4 step 6
- ar_feature_vision §二 现状基线
- LineB §1-§4 双管线兼容性
- Phase 4 §8 §8.7 W1-W8 周次

---

## §6 step-7 — HUD / 工具柜按需展开

### §6.1 一句话

User 在 AR 主场景中点 HUD（屏幕一角 2D 像素图标）→ 展开（横向 / 竖向，user 选）→ 显示状态 / 时间 / 天气 / 连接 / 感知摘要；点工具柜（对角）→ 展开 → 显示工具按钮。**Meta UI，与真实世界 0 互动**。

### §6.2 触动的能力

| capability candidate | 来源 |
|:--|:--|
| `hud-toggle`（开关 HUD）| NEED-IMPL-HUD-001 |
| `hud-direction-selector`（横向 / 竖向 user 选）| 同上 |
| `hud-content-binding`（绑定后端状态）| 状态 = parrot_actions / connection_health / weather（外部 API）|
| `tool-cabinet-toggle`（开关工具柜）| NEED-IMPL-TOOLCAB-001 |

### §6.3 触动的接口面（候选）

| 拓扑 | 接口面 candidate | 状态 |
|:--|:--|:--|
| **wire** | HUD content：从 EcpState 三态 + connection_health + weather（Phase 5+ 外部 API）| evolving |
| **in-process** | HUD 渲染端：BB read `tick/body_state` / `tick/cognitive_state` / `session/connection_health` | evolving |
| **capability** | HUD UI（Unity SO + 展开方向）| proposed-new |
| **capability** | Tool Cabinet UI（Unity SO + 工具按钮注册）| proposed-new |

### §6.4 开放问题

| Q | 推到哪 | 真源 |
|:--|:--|:--|
| 天气 API 接入（外部依赖）？ | AR 工作区 chat | ar_app_flow §6 提及 |
| HUD 展开方向是 per-session 还是 per-user persistent？ | AR 工作区 chat | ar_app_flow §6 |
| Tool Cabinet 工具按钮排序是 user 自定义还是固定？ | AR 工作区 chat | 同上 |

### §6.5 driven_by

- ar_app_flow §4 step 7 + §6 HUD 与工具柜布局

---

## §7 step-8 — 工具或 2D 工作区按需进入

### §7.1 一句话

User 在工具柜中点放大镜 / 注意力框 / 拍照 / 行程单 / 贴图箱 / 任务按钮 / 纸条；每个工具有自己的接口面：

- **放大镜**：放大手机画面（含 UI），倍率可调
- **注意力框 / Bounding Box**：user 拖框圈关注区域 → 触发 GOSLO 注意力 / 识别
- **拍照**：preview EcpEvent + asset HTTP POST 双通道
- **行程单**：日程打勾（占位）
- **贴图箱**：拖贴纸到画面截图打卡（占位）
- **任务按钮**：触发常用动作（占位）
- **纸条 / 报告**：Nanobot / Maid 递交消息（占位）

### §7.2 触动的能力（按工具分）

#### §7.2.1 放大镜 / 海盗望远镜

| capability | 来源 |
|:--|:--|
| `magnifier-with-ratio`（放大手机画面，含 UI；倍率调节）| ar_app_flow §7 |

接口候选：纯 Unity 端（不触动 wire）。

#### §7.2.2 注意力框 / Bounding Box

| capability | 来源 |
|:--|:--|
| `bbox-place`（用户放置 BBox）| Phase 4 §8 L5 + W6-7 ratified |
| `bbox-drag`（拖动）| 同上 — lossy DataChannel |
| `bbox-remove`（user 移除）| 同上 |
| `attention-threshold-anchor`（BBox 1 个直接达阈值）| Phase 4 §8 L9 |
| `attention-config-echo`（Unity SO → Brain BB）| F-05 Echo 全链路 |

#### §7.2.3 拍照

| capability | 来源 |
|:--|:--|
| `photo-capture-preview`（256px JPEG < 8KB + EcpEvent reliable）| Phase 4 §8 L8 + W8 |
| `photo-asset-upload`（HTTP POST `/upload/photo` + Castle 本地 cache）| 同上 |
| `photo-node-write`（NodeKind.PHOTO 与 OBJECT 区分）| Phase 4 §8 L7 |

#### §7.2.4 注意力框 / 放大镜联动（隐式）

> ar_app_flow §8 user 原话："注意力状态/工具还没决定归到 reflex / Intent / task。它应该是 Intent 和 task 级别的"

| capability | 来源 |
|:--|:--|
| `attention-conscious-not-blocking`（GOSLO 理解意图，但不强制中断对话）| NEED-ATTN-Q5 + Q7 |
| `attention-snapshot-trigger`（拖框是否触发 captureSnapshot？）| NEED-ATTN-Q3 |
| `attention-event-emit`（生成 SightingEvent / SceneObservationEvent？）| NEED-ATTN-Q4 |

### §7.3 触动的接口面（候选）

| 拓扑 | 接口面 candidate | 状态 |
|:--|:--|:--|
| **wire** | EcpEvent `bbox.placed` / `bbox.removed` | ✅ locked（Phase 4 §8 L5 + §8.3）|
| **wire** | EcpEvent `focus.anchored` / `focus.released` | ✅ locked（L6 + §8.3）|
| **wire** | EcpEvent `attention.threshold.crossed` | ✅ locked（§8.3）|
| **wire** | EcpEvent `attention.config.echo` | ✅ locked（§8.3 + F-05）|
| **wire** | EcpEvent `photo.taken_preview` + `photo.asset_uploaded` | ✅ locked（§8.3 + W8）|
| **wire** | `parrot.ecp.tick` lossy（BBox/Focus 拖动 30-60Hz）| ✅ locked |
| **cross-process** | HTTP `/upload/photo` (FastAPI 7889) | ✅ ratified（W8）|
| **in-process** | RefBinding lifecycle（BBox/Focus place→remove）| ✅ ratified（W6-7 refs.py）|
| **in-process** | FocusBboxThreshold 累加器 + Echo 全链路 | ⚠️ experimental（Phase 4 临时；详 NEED-ATTN-Q* 升级路径）|
| **in-process** | hint_writer (transient/current_attention_hint) | ✅ ratified |
| **capability** | Photo 双通道接口约定（preview < 8KB + asset HTTP）| ✅ locked（L8）|
| **capability** | Tool Cabinet 工具按钮注册表（每工具有 wire / capability 锚点）| proposed-new |

### §7.4 开放问题

| Q | 推到哪 | 真源 |
|:--|:--|:--|
| 行程单 / 贴图箱 / 任务按钮 / 纸条 / 报告 接口面？ | AR 工作区独立 chat | ar_app_flow §7 |
| 注意力框是否也要触发 captureSnapshot？ | Chat 4 4-B-wire（wire 接口面 cross-link NEED-ATTN-Q3）| ar_app_flow §8 Q3 |
| 注意力框 命令多久过期？ | Chat 4 4-B-wire（cross-link EcpCommand expires_at）| NEED-ATTN-Q6 |
| 用户拖框时 GOSLO 是否立刻停下思考？ | Chat 4 4-B-in（capability `attention-conscious-not-blocking`）| NEED-ATTN-Q2 + Q5 |

### §7.5 driven_by

- ar_app_flow §4 step 8 + §7 工具柜初期道具 + §8 注意力工具的开放问题
- Phase 4 §8 W6-7 / W8 完成报告
- ar_feature_vision §三 4 核心讨论
- ar_camera_interaction_survey（拍照互动调研）

---

## §8 跨步全局议题

### §8.1 与"4 类块预设系统"的整体关联（NEED-P3-B/C/D/E）

step-1 (启动菜单) → step-2 (确认配置) → step-6 (进入 AR 时按 4 active ID 加载) 是一个**贯穿链**。

接口面影响：
- BB 4 keys：`global/active_model_id` / `global/active_persona_id` / `global/active_mode` / `global/active_scene`
- Wire：4 类块切换的 EcpEvent / EcpCommand 待 NEED-P3-B 设计
- Capability：4 类块 ID 命名空间 + 注册表 + 加载器 + active 切换事件

**Chat 4 主场处置**：在 `wire/` / `capability/` 子目录留 proposed-new 占位，cross-link 到 NEED-P3-B 实施 chat。

### §8.2 与"Pause-Resume 接上话" 的整体关联（ar_feature_vision §一）

step-6 后 user 切后台 → step-6 ResumeFromBackground → 恢复对话上下文。

接口面影响：
- livekit-unity-lifecycle 已收口此场景（11 态 FSM）
- ECP `intent.disconnect` / `connection.health.changed`（Phase 4 §8 L4 inline envelope）
- BB `session/connection_health` 4 态聚合

**Chat 4 主场处置**：在 `wire/topic_matrix.md` 显式标 `parrot.ecp.health` / `parrot.ecp.intent_disconnect` 是 inline envelope（不迁移，不动）。

### §8.3 与"GOSLO 自知被什么挡住" 的整体关联（ar_feature_vision §一）

step-6 / step-8 期间，摄像头被遮挡 / 断流时，应有信号回到 Brain（不让 Gemini 幻觉画面）。

接口面影响：
- wire：摄像头遮挡 / 断流的 EcpEvent（**proposed-new**，未在 Phase 4 §8.3 13 个 event_type 中）
- in-process：门控三层（产地 Unity / 路上 LiveKit / 消费端 Brain）协作

**Chat 4 主场处置**：在 `wire/` 子目录创 `wire/camera_occlusion_v1.md` proposed-new 占位（与 NEED-VISION-OCCLUDE-001 cross-link）；推 4-B-wire 实施 chat 决定是否纳入 Chat 4 范围还是推 P3。

---

## §9 给 Stage 2 (4-B-cap) 的输入清单

Stage 2 拿本文 + needs_inventory.md 后，反推能力清单时关注：

1. **每步流程的 capability candidates** 共 ~50 个（§1-§7 各 §x.2 子节）
2. **跨步全局议题 §8** 加 ~5 个能力（4 类块联动 / Pause-Resume / 摄像头遮挡）
3. **每能力必须 cite app-flow:step-N 或 needs:NEED-XX**（不允许 cite code 符号）
4. **能力四态**（应有 / 已有 / 缺 / 漂）：
   - **应有** = §7.2 BBox/Focus/Photo 等 Phase 4 已 lock 的 capability
   - **已有** = 各 step 中 ratified 接口面对应的 capability
   - **缺** = §1-§2 step 中 proposed-new（4 类块 / 启动菜单 / HUD）
   - **漂** = §7.2 attention threshold（Phase 4 临时）/ selection-C / IngestRunner factory

---

## §10 引用

- 父规划稿：[`../architecture/interface_extraction_plan_20260507.md`](../architecture/interface_extraction_plan_20260507.md)
- INDEX：[`INDEX.md`](INDEX.md)
- methodology：[`methodology.md`](methodology.md)
- TODO：[`TODO.md`](TODO.md)
- 配套 Stage 1：[`needs_inventory.md`](needs_inventory.md)
- 真源 doc：[`../architecture/ar_app_flow_ui_design.md`](../architecture/ar_app_flow_ui_design.md) + [`../architecture/ar_feature_vision.md`](../architecture/ar_feature_vision.md) + [`../parrot_behavior_rules.md`](../parrot_behavior_rules.md)

---

## §11 变更日志

- **2026-05-07**：本文创建（Stage 1 — 4-B-req 在主 chat 跑产）。覆盖 8 步 App flow + 跨步全局议题 §8（3 项），共 ~55 capability candidates + ~30 接口面 candidates，按拓扑边界（wire / cross-process / in-process / capability）初步分桶。
