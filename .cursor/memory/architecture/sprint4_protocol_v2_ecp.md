---
status: tentative
category: active
status_note: "Sprint4 Protocol V2 / ECP 正式设计稿。先作为实现合同入口，字段在最小 ECP envelope 代码落地并通过四个验证工具后再冻结。"
last_reviewed: 2026-04-29
---

# Sprint4 Protocol V2 / ECP 设计稿

> 用途：把 Sprint3 已验证的数据流、现有 V1 协议雏形、ECP 目标驱动控制、App 生命周期状态、DSG L2-B / Graphiti / Obsidian / Ref 边界统一为 Sprint4 可实现的最小协议面。  
> 背景锚点：`.cursor/memory/architecture/sprint4_protocol_ecp_background_20260429.md`  
> 计划来源：`c:\Users\Bin\.cursor\plans\sprint4_协议升级_31652b8a.plan.md`

## 1. 总体定位

Protocol V2 不是重写 ParrotCarriers 的总线协议，而是把已经存在的半成品合同收拢到同一个事件和状态面：

- `src/parrot/shared/event_log.py` 已有 L0 `EventEnvelope` 和 `EventLayer`。
- `src/parrot/shared/bb_schema.py` 已有 Blackboard key manifest。
- `src/parrot/shared/snapshot.py` 已有 `SnapshotEnvelope` / `BBox` / `CameraPose`。
- `src/parrot/shared/tiers.py` 已有 `VideoTier` x `DsgMode` 合法矩阵。
- `src/parrot/brain/tools/_rpc_bridge.py` 已有 Unity RPC 转发和 `tick/last_rpc_ack` 回灌。
- `src/parrot/dsg/ingest/base.py` 已有 DSG `Observation` / `ObservationSource`。
- `src/parrot/dsg/l2b_types.py` 已有 L2-B node 的 `graphiti_uuid`、`obsidian_uuid`、`reference_image_path`、`last_sighting_path`。
- Unity 已有 `ParrotRpcHandler`、`VideoTierReceiver`、`VideoStateReporter`、`MicrophonePublisher`、`RoomManager` 等实际通道。

Sprint4 的协议升级目标是让这些合同能共同回答四个问题：

1. 后端为什么发出某个目标命令。
2. Unity 是否真实接受、拒绝、过期、执行或失败。
3. 感知证据、状态变化和记忆绑定如何互相追溯。
4. App 生命周期、媒体状态和用户工具如何进入同一状态面，而不是散落在 HUD 文案里。

## 2. 非目标

Sprint4 不做这些事：

- 不实现完整 Line B 自建 ASR / TTS / VLM，只预留事件边界。
- 不把 Runtime HUD / SelfTest / `Dev.unity` 升级成正式接口。
- 不把 Graphiti 当实时帧数据库。
- 不强行把所有 Obsidian Ref UUID 化。
- 不让 Unity 理解后端 BT 森林细节；Unity 只理解 ECP 命令和状态机回执。
- 不一次性替换全部旧 RPC；第一阶段只包装 `flyTo`、`animate`、`setVideoTier`。

## 3. 协议分层

Protocol V2 分为四层。

### 3.1 L0 EventEnvelope

L0 是因果和审计源，使用 `EventEnvelope`：

- 每次状态变化、ECP 命令、ECP 回执、snapshot、sighting、ref binding 都应能落为一条 L0 event。
- `kind` 允许 Sprint4 期间继续开放，但新增事件名必须以模块域名前缀组织，例如 `ecp.command.issued`、`ecp.ack.received`、`snapshot.captured`。
- `layer` 使用现有 `EventLayer`：`reflex`、`intent`、`task`。
- `provenance_parent` 用于串联 turn → command → ack → snapshot → sighting → L2-B node → Graphiti episode。

### 3.2 Blackboard 当前状态

Blackboard 是当前状态快照，不是事实历史。新增状态必须先判断是否属于：

- `global/*`：跨 session 稳定配置和用户画像。
- `session/*`：LiveKit room 生命周期内有效。
- `tick/*`：最近一次 telemetry / ack / frame 的快照。
- `transient/*`：秒级 consume-then-expire 的事件或缓存。

Sprint4 最小新增或标准化的状态键建议：

- `session/connection_health`：连接与媒体状态摘要。
- `session/audio_route_policy`：当前音频输入/输出路线策略。
- `session/ecp_state`：Unity 最近上报的前端状态机快照。
- `tick/last_ecp_ack`：最近一次 ECP 回执。后续可替代或扩展 `tick/last_rpc_ack`。
- `transient/current_attention_hint`：Focus / Bounding Box 当前注意力输入。
- `transient/last_sighting_event`：最近一次视觉/注意力证据。

这些键在代码落地前仍是候选。实现时必须更新 `src/parrot/shared/bb_schema.py`，不要在业务代码里偷偷写未登记 key。

### 3.3 ECP 命令与回执

ECP 是后端决策层到 Unity 前端执行层的协议出口。它负责：

- 目标命令。
- 命令生命周期。
- 前端状态机回执。
- 过期和取消。
- 失败原因。
- 与 turn / sighting / snapshot / body channel 的关联。

ECP 不负责：

- 决定哪个任务该赢。该职责属于 Scheduler / BT / Arbiter。
- 直接写 Graphiti。Graphiti 写入应走归档器或 MemoryWriter。
- 暴露 BT 节点名给 Unity 或 Gemini。

### 3.4 DSG / Ref 证据层

感知和记忆侧不直接复用 ECP 命令。它们通过事件关联：

- `SnapshotEvent` 表示按需截图或用户拍照产生的图像证据。
- `SightingEvent` 表示某个物体/区域/注意力线索被观察到。
- `AttentionHintEvent` 表示用户用 Focus / Bounding Box 给出的注意力输入。
- `RefBinding` 表示 L2-B node / Graphiti node / Episode / Snapshot / Photo 与 Obsidian 或其他 Ref 资料的引用关系。

## 4. 传输选择

### 4.1 LiveKit RPC

用于可靠 request / response：

- `ecpCommand`：统一 ECP goal 入口。
- `captureSnapshot`：按需抓帧。
- `setVideoTier`：第一阶段可继续保留旧入口，同时成为 `ecpCommand(kind=set_video_tier)` 的兼容实现。

第一阶段不要删除旧 `flyTo`、`animate`、`setVideoTier`。应先让 Python ECP wrapper 生成 envelope，再调用旧 RPC；Unity 侧再逐步增加 `ecpCommand` handler。

### 4.2 Reliable DataChannel 或 Participant Attributes

用于小型状态同步：

- `EcpState`。
- `SpeechStateEvent`。
- `ConnectionHealthState`。
- `MediaRouteEvent`。

若 LiveKit Unity SDK 对 attributes 支持不稳定，先用 reliable DataChannel；不要为了 attributes 牺牲可测性。

### 4.3 Lossy DataChannel

用于高频遥测：

- XR Hands pose。
- 手势 tracking。
- AR tracking state。
- Bounding Box 拖动过程。
- Focus 放大镜连续位置。

Lossy 通道只能传“当前输入趋势”，不能承载最终事实。松手确认、拍照确认、识物结果必须走 reliable / RPC / L0 event。

## 5. ECP 最小合同

### 5.1 EcpCommand

`EcpCommand` 是 Brain / Scheduler / Arbiter 下发给 Unity 的目标命令。

候选字段：

```json
{
  "schema_version": "ecp.v2.alpha",
  "command_id": "cmd_...",
  "kind": "move_to",
  "issued_at": 1777390000.123,
  "valid_after": 1777390000.123,
  "expires_at": 1777390003.123,
  "layer": "intent",
  "priority": 50,
  "interruptibility": "interruptible",
  "source": {
    "actor": "brain.tool.fly_to",
    "turn_id": "turn_...",
    "sighting_id": "",
    "snapshot_uuid": "",
    "parent_event_id": ""
  },
  "target": {
    "body_channel": "body",
    "state": "flying",
    "position": { "x": 0.0, "y": 0.0, "z": 0.0 }
  },
  "expected_duration_ms": 1500,
  "fallback_behavior": "idle",
  "meta": {}
}
```

最小 `kind` 集合：

- `move_to`：兼容旧 `flyTo`。
- `animate`：兼容旧 `animate`。
- `set_video_tier`：兼容旧 `setVideoTier`。
- `perch_to_finger`：第一阶段手势验证目标。
- `focus_region`：Focus / Bounding Box 最小后端接口。
- `camera_capture`：相机功能目标。
- `capture_snapshot`：认知层按需抓帧。

`interruptibility` 候选值：

- `non_interruptible`：开始后不应被普通命令打断。
- `interruptible`：可被更高优先级命令打断。
- `preemptive`：命令本身用于打断当前动作，例如 freeze / emergency return。
- `queueable`：前端可排队，过期前仍有效。

### 5.2 EcpAck

`EcpAck` 是 Unity 对某条命令的真实状态回执。成功发送 RPC 不等于动作成功，只有 ack 才能改变后端对身体/前端状态的判断。

候选字段：

```json
{
  "schema_version": "ecp.v2.alpha",
  "command_id": "cmd_...",
  "ack_id": "ack_...",
  "status": "accepted",
  "reason": "",
  "frontend_state": {
    "body_state": "flying",
    "head_state": "head_forward",
    "cognitive_state": "thinking",
    "active_locks": ["body"],
    "video_tier": "VIDEO_GEMINI_ONLY"
  },
  "received_at": 1777390000.140,
  "started_at": 1777390000.180,
  "completed_at": 0.0,
  "detail": {},
  "meta": {}
}
```

`status` 候选值：

- `received`：Unity 已收到，但尚未判定。
- `accepted`：已接受并将执行。
- `queued`：已排队，等待 micro-lock 或前置动作完成。
- `running`：执行中。
- `completed`：完成。
- `rejected`：拒绝执行。
- `expired`：到达时已过期或空间上下文失效。
- `cancelled`：被主动取消。
- `preempted`：被更高优先级命令抢占。
- `failed`：执行中失败。
- `unchanged`：请求与当前状态一致。

`reason` 候选值：

- `applied`
- `unchanged`
- `no_unity`
- `no_room`
- `no_video_publisher`
- `permission_denied`
- `expired`
- `micro_lock`
- `illegal_transition`
- `incompatible_state`
- `transport`
- `malformed`
- `timeout`

### 5.3 EcpState

`EcpState` 是 Unity 前端状态机的快照，用于让后端和 Gemini 不再靠“我刚发了 RPC”猜测前端状态。

最小字段：

- `ts`
- `unity_identity`
- `room_id`
- `body_state`
- `head_state`
- `cognitive_state`
- `active_command_id`
- `queued_command_ids`
- `active_locks`
- `last_ack_id`
- `video_tier`
- `app_lifecycle_state`
- `ar_tracking_state`
- `connection_health`（Phase 3 新增，可空，类型见 §5.4）
- `meta`

#### Phase 3 注释（2026-04-29）

- `EcpState` 通过 reliable DataChannel 周期上报，频率 `T_HEARTBEAT_INTERVAL`（默认 5s，见 livekit-unity-lifecycle/IMPL_REF.md §10）。冷启动 / pause-resume 过渡期允许 `connection_health=null`，消费方等同 `overall=unknown`。
- `EcpAck.frontend_state` **不**整体携带 `connection_health`；它只通过 `connection_overall` 字段（4 态聚合 healthy/degraded/unhealthy/unknown）反向回灌。完整健康面只走 `EcpState`（决策来源：`docs/sprint4_research/result/INDEX_for_phase3.md §1 #13`）。
- `app_lifecycle_state` 取自 Unity 端 11 状态 FSM 的字符串化：`cold_start / permission_gate / token_gate / ar_session_starting / connecting / connected / running / short_background / long_background / reconnecting / degraded / shutting_down / disconnected`。**后端 BT / Scheduler 不允许枚举推演**，只能消费这一字符串和 `connection_overall`。

### 5.4 EcpConnectionHealth（Phase 3 新增）

`EcpConnectionHealth` 是 Unity `ConnectionHealthState` 的 wire 形式，单字段 producer 路由见 `livekit-unity-lifecycle/IMPL_REF.md §4.2`。

最小字段（snake_case wire name；与 Python `EcpConnectionHealth` Pydantic 模型一一对应）：

- `room_connected`、`brain_present`、`rpc_ready`、`datachannel_ready`
- `audio_publish_attempted`、`audio_published`、`audio_last_error`
- `video_publish_attempted`、`video_published`、`video_first_frame`、`video_fresh_frame`、`video_tier`、`video_lifecycle_reason`
- `ar_tracking_state`
- `reconnect_attempt_count`、`last_disconnected_at`
- `overall`（healthy / degraded / unhealthy / unknown，与 `EcpFrontendState.connection_overall` 一致）
- `last_state_change_at`

`overall` 聚合规则：见 IMPL_REF.md §4.1 / Unity `ConnectionHealthState.ComputeOverall()`。

不在本结构里的字段（属于其他状态面）：
- 媒体路由（`AudioRoutePolicy`）走独立 `media.audio_route.changed` 事件 + `session/audio_route_policy` BB 候选键。
- AR plane / anchor / hand pose 不进 health；它们走 telemetry / snapshot / sighting。

## 6. 事件词汇

Sprint4 最小事件名：

- `ecp.command.issued`
- `ecp.ack.received`
- `ecp.state.reported`
- `connection.health.changed`
- `media.audio_route.changed`
- `media.video_state.changed`
- `snapshot.requested`
- `snapshot.captured`
- `sighting.observed`
- `attention.hint.updated`
- `ref.binding.created`
- `photo.captured`
- `intent.tier_change`，沿用 `PerceptionSupervisor` 现有事件。

所有事件 payload 里至少应包含：

- 自己的 id，例如 `command_id`、`snapshot_uuid`、`sighting_id`、`binding_id`。
- 相关上游 id，例如 `source_turn_id`、`source_command_id`、`source_snapshot_uuid`、`parent_event_id`。
- `actor` 仍放在 `EventEnvelope.actor`，payload 内不要重复制造多个 actor 真相源。

## 7. Snapshot / Sighting / Attention

### 7.1 SnapshotEvent

`SnapshotEvent` 是对 `SnapshotEnvelope` 的事件化包装。

最小字段：

- `snapshot_uuid`
- `request_id`
- `source`
- `captured_at`
- `width`
- `height`
- `payload_kind`
- `payload_path` 或 `payload_uri`
- `camera_pose`
- `source_command_id`
- `source_turn_id`
- `purpose`: `identify_object` / `camera_mode` / `reference_image` / `debug`

按需识物和相机功能都可以使用 `SnapshotEnvelope`，但语义不同：

- `identify_object` 的 snapshot 是认知证据。
- 相机功能的 photo 是用户资料或创作输入。

不要把用户每次拍照都默认写成场景事实。

### 7.2 SightingEvent

`SightingEvent` 是“看见或注意到”的证据，不等于确认事实。

最小字段：

- `sighting_id`
- `snapshot_uuid`
- `source`: `identify_object` / `focus_tool` / `bounding_box` / `cv_a10` / `gemini_oral`
- `bbox`
- `label`
- `confidence`
- `candidate_graphiti_uuid`
- `candidate_l2b_uuid`
- `confirmation`: 默认 `tentative`
- `observed_at`
- `source_turn_id`
- `source_command_id`

Focus / Bounding Box 只能生成 `SightingEvent` 或 `AttentionHintEvent`，默认不能直接写 CONFIRMED。

### 7.3 AttentionHintEvent

`AttentionHintEvent` 表示用户正在把注意力放到某个区域。

最小字段：

- `hint_id`
- `source`: `focus_magnifier` / `bounding_box` / `gesture`
- `bbox`
- `screen_point`
- `world_ray`
- `strength`
- `phase`: `dragging` / `confirmed` / `cancelled`
- `expires_at`

拖动过程走 lossy DataChannel；`phase=confirmed` 走 reliable / RPC 并写 L0 event。

## 8. RefBinding 最小合同

`RefBinding` 是引用关系，不是事实本身。

候选字段：

```json
{
  "binding_id": "refb_...",
  "target_type": "l2b_node",
  "target_uuid": "node_...",
  "ref_type": "obsidian_file",
  "ref_locator": "Objects/white-mouse.md",
  "authority": "user",
  "created_at": 1777390000.123,
  "source_event_id": "1777390000123-0",
  "summary": "用户维护的白色鼠标资料",
  "meta": {}
}
```

`target_type` 候选值：

- `graphiti_node`
- `l2b_node`
- `episode`
- `snapshot`
- `photo`

`ref_type` 候选值：

- `obsidian_file`
- `obsidian_block`
- `photo`
- `diary`
- `external_uri`
- `snapshot`

`authority` 候选值：

- `user`
- `system`
- `identify_object`
- `graphiti`
- `importer`

Graphiti node UUID 是和 L2-B node 高效适配的重要锚点。Obsidian Ref 不强制 UUID 化，可使用 vault path、frontmatter id、block id 或外部 URI，但绑定关系必须稳定可追踪。

## 9. 连接与媒体状态

### 9.1 ConnectionHealthState

正式 App 不应靠 Runtime HUD 文案判断是否可用。`ConnectionHealthState` 应明确拆开：

- `room_connected`
- `brain_present`
- `rpc_ready`
- `datachannel_ready`
- `audio_publish_attempted`
- `audio_published`
- `audio_last_error`
- `video_publish_attempted`
- `video_published`
- `video_first_frame`
- `video_fresh_frame`
- `video_tier`
- `ar_tracking_state`
- `last_state_change_at`

`RoomManager.IsConnected` 只能证明 room 信令连接，不证明 Brain 在房、音频可用、视频有新鲜帧或 RPC 可用。

### 9.2 AppLifecycleManager

建议新增 Unity 侧 App lifecycle 服务，而不是继续把生命周期逻辑分散在 `RoomManager` / `VideoStateReporter` / `MicrophonePublisher` 里。

最小状态：

- `cold_start`
- `permission_gate`
- `token_gate`
- `connecting`
- `connected`
- `ar_session_starting`
- `running`
- `short_background`
- `long_background`
- `reconnecting`
- `degraded`
- `disconnected`

移动端后台策略采用混合状态机：

1. `OnApplicationPause(true)` 记录时间戳，发送 `connection.health.changed` 或 `media.video_state.changed`。
2. 短暂停顿窗口内恢复时，允许 SDK 自恢复。
3. 超过阈值后，主动释放 room / audio / video / AR session 资源。
4. 回前台后重新进入 token / permission / room / media publish gate。

阈值先作为 App 配置，不写死在测试 HUD。

### 9.3 AudioRoutePolicy

Sprint3 证明非蓝牙 48k baseline 可用，但外放回声和设备切换属于正式 App 策略。

最小策略：

- 默认 `phone_mic_48k_headphones_recommended`。
- 明确识别 `speaker_echo_risk`，外放时不要假定 Gemini VAD 稳定。
- 蓝牙输入/输出先标记为 `unsupported_or_experimental`，不让 `MicrophonePublisher` 靠隐式设备选择决定产品行为。
- 设备切换必须生成 `MediaRouteEvent`，包含输入设备、输出路线、采样率、回声风险。
- 自建 Line B ASR/VAD 以后可以接管更复杂的 echo cancellation；Sprint4 只预留边界。

## 10. ECP 与 RIT / BT / BT 森林

ECP、Reflex / Intent / Task、BT Router、`parrot_behavior_rules.md`、未来 BT 森林是同一控制链的不同层。

控制链：

```text
User/Sensor/Tool Event
  -> EventLayer classifier
  -> Scheduler / BT Router
  -> Reflex / Intent / Task subtree
  -> Arbiter / resource channel lock
  -> EcpCommand
  -> Unity frontend FSM
  -> EcpAck / EcpState
  -> Blackboard + L0 EventEnvelope
```

职责边界：

- RIT 回答事件时间尺度和 Gemini 是否等待。
- BT 回答当前上下文下走哪个策略分支。
- `parrot_behavior_rules.md` 回答动作兼容矩阵和体感红线。
- Arbiter 回答多个候选动作最终谁赢。
- ECP 回答命令如何传输、过期、取消和回执。
- Unity FSM 回答本地是否能平滑执行。

Sprint4 的最小 Arbiter 只需三个资源通道：

- `body_channel`
- `head_channel`
- `vision_channel`

后续 BT 森林可以按 `Scene` / `BehaviorMode` / `VisualState` / `BodyState` 选择不同 root，但所有树最终输出统一 `EcpCommand`，不要把树结构暴露给 Unity。

## 11. 四个验证工具的协议使用

### 11.1 核心对话 / 简单指令 / 飞到手指

验证内容：

- Line A Gemini Live 继续可用。
- `flyTo` / `animate` 通过 ECP wrapper 等待 ack。
- 手势 telemetry 走 lossy DataChannel。
- `perch_to_finger` 用 `expires_at` 防止用户手已经移动后鹦鹉飞向旧位置。

### 11.2 按需发现物体

验证内容：

- `captureSnapshot` 产生 `SnapshotEnvelope`。
- `snapshot.captured` 写 L0 event。
- `identify_object` 生成 `SightingEvent`。
- L2-B 先做快速候选，Graphiti 再扩搜。
- 未确认时返回 unknown + snapshot，不让 GOSLO 过度承诺。

### 11.3 Focus 放大镜 / Bounding Box

验证内容：

- 拖动过程为 `AttentionHintEvent(phase=dragging)`。
- 松手为 `phase=confirmed`。
- 后端只提升注意力权重或候选区域，不直接 CONFIRMED。
- 可关联后续 `SightingEvent` 或 `captureSnapshot`。

### 11.4 照相机功能

验证内容：

- 用户拍照生成 `PhotoEvent` 或 `SnapshotEvent(purpose=camera_mode)`。
- 照片可通过 `RefBinding` 绑定到 Graphiti node、L2-B node、Episode 或 Obsidian Ref。
- 默认不把照片当场景事实写入 Graphiti。

## 12. 实施顺序

### Phase 1: 设计和 DTO

1. 新增 Python `shared/ecp.py`，定义 `EcpCommand`、`EcpAck`、`EcpState`、相关 enum。
2. 新增 C# DTO，与 Python 字段对齐。
3. 更新 `bb_schema.py` 候选 key。
4. 保留旧 RPC，先由 Python wrapper 生成 `EcpCommand` 并调用旧 `flyTo` / `animate` / `setVideoTier`。

### Phase 2: Unity 前端状态机回执

1. `ParrotRpcHandler` 返回 `EcpAck` 兼容 JSON。
2. `VideoTierReceiver` 返回 `EcpAck` 兼容 JSON。
3. 增加最小 `FrontendEcpState`，上报 body/head/lock/tier。
4. `tick/last_ecp_ack` 与 `tick/last_rpc_ack` 并行一段时间。

### Phase 3: Lifecycle / Audio / Connection

1. 新增 `AppLifecycleManager`。
2. 新增 `ConnectionHealthState` 上报。
3. 把 `MicrophonePublisher` 的设备选择上移为 `AudioRoutePolicy`，本类只执行 publish。
4. `VideoStateReporter` 与 `ARVideoPublisher` 的 first/fresh frame 状态进入统一 health state。

### Phase 4: Snapshot / Identify / Ref

1. 实现 `snapshot.requested` / `snapshot.captured`。
2. 改造 `identify_object` 为 snapshot + L2-B + Graphiti。
3. 实现 `SightingEvent` / `AttentionHintEvent`。
4. 实现 `RefBinding` 最小写入与查询。

## 13. Sprint4 验收标准

Sprint4 协议升级的最小验收只看四件事：

1. GOSLO 下发一个目标命令，Unity 能 accepted / rejected / expired / completed 并回执。
2. 连接、音频、视频状态能进入统一状态面，而不是靠 HUD 判断。
3. 一次按需识物能抓图、写证据、同步返回符合体感的结果。
4. 一个 L2-B node 能绑定 Graphiti UUID 和一个或多个 Ref，不污染实时循环。

## 14. 开放问题

- `EcpState` 用 reliable DataChannel 还是 Participant Attributes，需要根据 LiveKit Unity SDK 当前稳定性实测决定。
- `ecpCommand` 是新增 Unity RPC 统一入口，还是先长期保留旧 RPC + envelope wrapper，需要在 Phase 1 实测后决定。
- `RefBinding` 的持久化位置先放 L2-B graph meta、Graphiti episode，还是单独本地 registry，需要结合现有 `sync_obsidian_to_graphiti.py` 决定。
- 蓝牙音频是否进入 Sprint4 支持范围，目前建议只做显式识别和降级提示。

