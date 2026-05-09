# Sprint4 Phase 3 / L3 入场锚点（2026-04-29）

> **本文用途**：把 Phase 3 L3（真实 LiveKit transport / 旧脚本搬迁）的全部背景、决策、依赖顺序、4 组拆分、验收点固化在一处。
> 任何后续 chat 进来 **第一份要读的就是本文**；读完即可直接动手。
>
> **状态**：authoritative。修改本文 = 修改 L3 计划。
>
> **最后验证**：2026-04-29，ArSpike `Packages/manifest.json` 已加 `io.livekit.livekit-sdk` (commit pinned)。

---

## 0. 进入 L3 之前必须先理解的硬约束

> 这一节是"不允许误读"，违反任何一条都意味着 L3 已经走偏。

1. **ECP 不替代 Scheduler / BT**：ECP 只是 Brain ↔ Unity 的**协议边界**。`Scheduler` / `Reflex / Intent / Task` / `BT 森林` 都在后端 Python 侧做决策；ECP 只负责"目标命令 + 回执 + 过期 + 取消 + 状态同步"的合同。L3 不能把 lifecycle 决策塞到 BT。
2. **Lifecycle FSM 在 Unity 端，不暴露给后端**：11 状态枚举 (`AppLifecycleState`) **不**派生后端行为分支。后端只看 `EcpState.app_lifecycle_state` 字符串 + `ConnectionHealthState.overall` 4 态聚合 + `connection.health.changed` 事件。
3. **VideoTier 是 Intent，不是 Reflex**：`setVideoTier` 切换走 §6 cool-down，必须等 ack。Reflex 层（手势、紧急停止）禁止改 video tier。
4. **DSG L2-B 不接受实时帧**：L2-B 是工作记忆，只接受快照 / sighting / refbinding 这类离散事件，不接 `OnARFrameReceived` 流。
5. **Bluetooth 音频 Sprint4 OOS**：候选 BB 键 `session/audio_route_policy` 保留 `# CANDIDATE`，无 producer。`MicrophonePublisher` 只跑非蓝牙 48k baseline。
6. **新代码进 `unity/ArSpike/Assets/Scripts/ParrotApp/`**：不反向污染 `unity/ParrotDev/`。`ParrotDev` 已冻结作 Sprint3 真机回归对照。
7. **所有阈值挂 `ParrotLifecycleConfig` ScriptableObject**：17 个参数，禁止在业务代码中硬编同名常量（"协议污染"反模式，见 IMPL_REF.md §10）。
8. **single-producer-per-field**：`ConnectionHealthAggregator` 每个 setter 只能有一个调用方（IMPL_REF.md §4.2 表）。

---

## 1. L1 + L2 已完成清单（搬迁前必须建立的"承接点"）

### 1.1 Unity ArSpike — L1 纯数据 / 纯 FSM 层（**全部 ParrotApp.* 命名空间**）

| 文件 | 命名空间 | 角色 |
|:--|:--|:--|
| `Config/ParrotLifecycleConfig.cs` | `ParrotApp.Config` | 17 参数 ScriptableObject + `OnValidate` 兜底 |
| `Config/Editor/ParrotLifecycleConfigMenu.cs` | `ParrotApp.Config.EditorTools` | `Tools/Parrot/Lifecycle Tuning` 菜单 |
| `Lifecycle/AppLifecycleState.cs` | `ParrotApp.Lifecycle` | 11 状态 enum + snake_case wire 字符串 |
| `Lifecycle/AppLifecycleManager.cs` | `ParrotApp.Lifecycle` | FSM 中枢；不依 LiveKit；持 `ConnectionHealthAggregator` 引用 |
| `Health/ConnectionHealthState.cs` | `ParrotApp.Health` | 数据快照 + `ComputeOverall` 4 态聚合规则 |
| `Health/ConnectionHealthAggregator.cs` | `ParrotApp.Health` | producer 单写约束的具体宿主；`OnChanged` 事件 |
| `Ecp/EcpStateDto.cs` | `ParrotApp.Ecp` | 周期心跳 wire 形式 + `EcpConnectionHealthDto` |
| `Ecp/LifecycleHeartbeatPublisher.cs` | `ParrotApp.Ecp` | 心跳 + `connection.health.changed` + `intent.disconnect`；`IHeartbeatTransport` 接口化（默认 `LogHeartbeatTransport` stub） |
| `RPC/EcpDtos.cs` | **global**（已有，不动命名空间） | `EcpCommandDto` / `EcpFrontendStateDto` / `EcpAckDto` / `EcpAckJson` |
| `Core/UnityMainThread.cs` | `ParrotApp.Core` | 已搬（Phase 3 早期）|
| `LiveKit/BrainParticipantResolver.cs` | `ParrotApp.LiveKit` | 已搬（Phase 3 早期）|

### 1.2 Python — L2 EcpState / EcpConnectionHealth Pydantic 层

| 类 | 位置 | 角色 |
|:--|:--|:--|
| `ConnectionOverall` enum | `src/parrot/shared/ecp.py` | 与 Unity `ConnectionOverall` 对齐 |
| `EcpFrontendState.connection_overall` | 同上 | per-command ack 携带 4 态摘要 |
| `EcpConnectionHealth` | 同上 | 与 Unity `EcpConnectionHealthDto` 字段一一对齐 |
| `EcpState` | 同上 | 周期心跳容器；`connection_health` 允许 `None`（cold-start 容差） |

### 1.3 设计稿对齐

- `sprint4_protocol_v2_ecp.md` §5.3 / §5.4 — `EcpState` / `EcpConnectionHealth` 落地章节
- `INDEX_for_phase3.md` §1 #13 — 决策"完整 ConnectionHealth 走 EcpState 周期上报，per-command ack 只带 4 态摘要"
- `MIGRATION.md` — 已搬迁 / 待搬迁清单

### 1.4 测试基线

`uv run pytest tests/test_scheduler/test_ecp.py` — 14 passed（含 4 条 Phase 3 新增覆盖）。L3 任何 Python 改动都必须保持这 14 条绿。

---

## 2. L3 关键依赖顺序（编译 / 行为 / 验收三层）

### 2.1 编译依赖（按编译可行性 strict topological order）

```
io.livekit.livekit-sdk (Packages/manifest.json) ✅ 已加
        │
        ▼
Assets/csc.rsp  -define:UNITY_AR_FOUNDATION
        │
        ├─────────────► UnityMainThread (ParrotApp.Core)        ✅ 已搬
        │                       │
        │                       ▼
        ├─────────────► BrainParticipantResolver                 ✅ 已搬
        │                       │
        │                       ▼
        └─────────────► RoomManager  (ParrotApp.LiveKit) ◄── 必须先搬
                              │
                  ┌───────────┼─────────────────────────────┐
                  ▼           ▼                             ▼
   RoomManagerLifecycleBridge  LiveKitDataChannel-          MicrophonePublisher
   (新)                         HeartbeatTransport (新)      ARVideoPublisher (含 lifecycle 集成)
                  │                                          VideoStateReporter
                  ▼                                                │
   AppLifecycleManager (灌信号源)                                  ▼
   ConnectionHealthAggregator (灌字段)              ParrotController + AnimationDriver
                                                              │
                                                              ▼
                                              ParrotRpcHandler  +  VideoTierReceiver
                                              （注：现 ArSpike 已有 RPC/EcpDtos.cs，
                                                handler 文件本身待搬）
```

### 2.2 行为依赖（哪些组件要先就位才能让别人有意义）

- **Heartbeat 真实 transport** 必须在 `RoomManager` 就位之后，才能从 `LogTransport` 切到 DataChannel。否则切了也发不出。
- **`ConnectionHealthAggregator` 的 producer** 必须按 IMPL_REF.md §4.2 表分工：
  - `RoomManager` → `room_connected` / `brain_present` / `reconnect_attempt_count` / `last_disconnected_at`
  - `MicrophonePublisher` → `audio_publish_attempted` / `audio_published` / `audio_last_error`
  - `ARVideoPublisher` → `video_*`
  - `ParrotRpcHandler` → `rpc_ready`
  - `VideoStateReporter` → `video_lifecycle_reason` (双轨：旧 RPC 不动，同时灌新字段)
- **`LifecycleShutdownService` chokepoint** 必须在所有 publishers 搬完后才落地，否则 unpublish 步骤无对象可调。

### 2.3 验收依赖（哪些 spike 阻塞主线，哪些并行）

- **阻塞主线（必跑）**：S1 Disconnect race / S2 飞行模式 Disconnected event 延迟 / S6 ARCore pause 崩溃率
- **并行**：S3 ByteStream 阈值 / S4 XRCpuImage vs AsyncGPUReadback / S5 setVideoTier 黑帧 / S7 ParticipantAttributes / S8 AudioConfigurationChanged
- spike 验收阈值见 `INDEX_for_phase3.md §2`

---

## 3. L3 四组拆分（**每组完成一组就推进 todo**）

> 拆分原则：**foundations → chokepoint/transport → publishers → consumers**，按编译依赖与"组内可独立验证"两个维度切。

### 3.1 Group 1 — Foundations（必跑前置；2 新增 + 1 增强 + 1 csc.rsp）

| 文件 | 操作 | 关键点 |
|:--|:--|:--|
| `unity/ArSpike/Assets/csc.rsp` | 新增 | `-define:UNITY_AR_FOUNDATION`（与 ParrotDev 对齐，让 ARVideoPublisher 编译） |
| `Core/UnityMainThread.cs` | ✅ 已搬完，无需动 | `ParrotApp.Core` 命名空间 |
| `LiveKit/BrainParticipantResolver.cs` | ✅ 已搬完，无需动 | `ParrotApp.LiveKit` 命名空间 |
| `LiveKit/RoomManager.cs` | **新增搬迁 + 增强** | 加 `OnConnecting` / `OnDisconnecting` events、`_disconnecting` flag、暴露 `JoinIdentity` / `RoomName` 给 lifecycle bridge；不动 graceful chokepoint（chokepoint 走 Group 2 单独服务）；RoomManager 仍负责 `_remoteAudioStreams` 的最小 cleanup |

**Group 1 验收**：
- ArSpike 编译通过（在 Editor 中 `Assets > Open C# Project` 然后 build solution，无 error）；
- `RoomManager` 可挂 GameObject，旧 `OnConnected` / `OnDisconnected` 事件保留（兼容），新 `OnConnecting` / `OnDisconnecting` / `_disconnecting` 暴露给 Group 2 使用。

### 3.2 Group 2 — Chokepoint / Transport / Bridge（3 新增）

| 文件 | 操作 | 关键点 |
|:--|:--|:--|
| `Lifecycle/RoomManagerLifecycleBridge.cs` | 新增 | 监听 `RoomManager` events → 调 `AppLifecycleManager.Report*` + 调 `ConnectionHealthAggregator.Report*`；负责 `brain_present` 检测（监听 `ParticipantConnected/Disconnected` 过滤 `agent-*`） |
| `Lifecycle/LifecycleShutdownService.cs` | 新增 | IMPL_REF.md §2 完整 chokepoint 协程：`UnpublishVideo → UnpublishAudio → Room.Disconnect → wait Disconnected event with T_DISCONNECT_WAIT_HARD soft timeout → Room.Dispose → cool-down T_SHUTDOWN_COOLDOWN`；通过 `OnApplicationQuit` 触发；`AppLifecycleManager.OnStateChanged(ShuttingDown)` 也触发 |
| `Ecp/LiveKitDataChannelHeartbeatTransport.cs` | 新增 | 实现 `IHeartbeatTransport`：通过 `Room.LocalParticipant.PublishData(reliable=true, topic=...)` 发包；topics: `parrot.ecp.state` / `parrot.ecp.health` / `parrot.ecp.intent_disconnect`；通过 `HealthAggregator.ReportDataChannelReady(true)` 反向灌成功状态 |

**Group 2 验收**：
- 在 Editor 单独场景里挂 `RoomManager + AppLifecycleManager + RoomManagerLifecycleBridge + LifecycleHeartbeatPublisher + LiveKitDataChannelHeartbeatTransport`，连上本地 LiveKit 后能在 Console 看到 lifecycle transition 日志；
- `OnApplicationQuit` 时 `LifecycleShutdownService` 把所有 4 步走完（即使没有 publishers，UnpublishTrack 步骤是 no-op）；
- DataChannel topic `parrot.ecp.state` 可被 Brain 端在 LiveKit dashboard 看到。

### 3.3 Group 3 — Publishers（3 文件搬迁 + lifecycle 集成 + config 化）

| 文件 | 操作 | 关键点 |
|:--|:--|:--|
| `LiveKit/MicrophonePublisher.cs` | 搬 + 灌 health | 字段全保留；新增构造参数 / FindObjectOfType 拿 `ConnectionHealthAggregator` 引用；`OnRoomConnected` / publish 协程退出时调 `ReportAudioPublishAttempt` / `ReportAudioPublished` |
| `LiveKit/ARVideoPublisher.cs` | 搬 + lifecycle 监听 + config 化 | (a) 三个硬编阈值改读 `ParrotLifecycleConfig`：`firstFrameTimeoutSeconds → T_FIRST_FRAME_TIMEOUT`、`staleFrameThresholdSeconds → STALE_FRAME_THRESHOLD_LOW_TIER`（动态根据当前 tier 选 LOW/HIGH）、`RebuildTrack` 中 `WaitForSeconds(0.3f) → T_TIER_COOLDOWN`；(b) 监听 `AppLifecycleManager.OnStateChanged`：进 `ShortBackground` 暂停 Blit（不 unpublish 轨）+ 灌 `ReportVideoLifecycleReason("lifecycle_background")`；回 `Connected` 等首帧再恢复；(c) `_producedFrameCount` / `HasFreshFrame` / `_videoSourceLabel` 灌 health aggregator |
| `LiveKit/VideoStateReporter.cs` | 搬 + 双轨灰 health | 旧 `onVideoDegraded` RPC 路径不动（向下兼容到 Brain Phase 2 收完事件路径）；同时灌 `ConnectionHealthAggregator.ReportVideoLifecycleReason(reason)` |

**Group 3 验收**：
- ArSpike 编译通过；
- `ConnectionHealthAggregator` 全字段都有 producer（grep `Report.*Audio.*Publish`、`Report.*Video.*` 看分布是否符合 §4.2 表）；
- 所有硬编阈值已替换（grep `firstFrameTimeoutSeconds = 8f` 等不应再出现在 ArSpike 业务代码）。

### 3.4 Group 4 — Consumers（4 文件搬迁；ECP-minimal 已收口）

| 文件 | 操作 | 关键点 |
|:--|:--|:--|
| `Parrot/AnimationDriver.cs` | 1:1 搬 | 业务核心；无依赖改动 |
| `Parrot/ParrotController.cs` | 1:1 搬 | 业务核心；无依赖改动 |
| `RPC/ParrotRpcHandler.cs` | 1:1 搬（覆盖 ArSpike 现有 stub） | 已含 ECP-minimal 整合（`expires_at` 校验、`active_locks=["body"]`）；新增灌 `HealthAggregator.ReportRpcReady(true, now)` |
| `LiveKit/VideoTierReceiver.cs` | 1:1 搬（覆盖 ArSpike 现有 stub） | 已含 ECP-minimal 整合（`expires_at` 校验、`unknown_tier` / `no_video_publisher` reason）；新增灌 `HealthAggregator.ReportVideoTier(tier, now)` |

**Group 4 验收**：
- ArSpike 自包含可跑（即一个 ArSpike Editor session 能完成"连接 → publish 视频 → 接 setVideoTier → 接 flyTo → graceful shutdown"完整链路，无须 ParrotDev 任何脚本）；
- `ParrotDev` 同名文件保持冻结，作为 Sprint3 真机回归对照；
- 跑 `uv run pytest tests/test_scheduler/test_ecp.py` 仍 14 passed。

---

## 4. 命名空间约定

- ArSpike `ParrotApp/` 下所有新文件 **必须**使用 `ParrotApp.<area>` 命名空间（`Core` / `LiveKit` / `Lifecycle` / `Health` / `Ecp` / `Config` / `Vision` / `Parrot` / `RPC`）。
- **例外**：`RPC/EcpDtos.cs` 已存在且无命名空间（global），保持不变以避免对现有代码 cascading 改动。新搬迁的 `RPC/ParrotRpcHandler.cs` 用 `namespace ParrotApp.RPC { ... }`；通过命名空间解析规则可见 global `EcpCommandDto` 等。

## 5. 与 Python 端的对齐点（不是 L3 范围，但 L3 不能撤销）

- `EcpState.app_lifecycle_state` / `EcpState.connection_health.overall` 字段名 **必须** 与 Unity DTO 完全一致（snake_case；`overall` 取值 `unknown` / `healthy` / `degraded` / `unhealthy`）。
- `connection.health.changed` / `intent.disconnect` 事件 schema 由 L3 transport 决定 wire 形式；Brain 端 handler 是 Phase 2 后续工作。本 L3 只保证 **能发出** + **payload 形式与设计稿 §5.3 / §5.4 对齐**。

## 6. 不做（L3 明确不做）

1. **不实现 Brain 侧 `connection.health.changed` / `intent.disconnect` event handler**（`src/parrot/brain/...`）。等 ECP Phase 2 收口（L0 event 入 EventEnvelope）后再加。
2. **不替换 ParrotDev 的同名脚本**。`ParrotDev` 冻结。
3. **不实现 `IFrameCapturer` / `captureSnapshot` ECP 化**。归 `snapshot-identify` todo（Phase 3 后段或 Phase 4）。
4. **不写 `AudioRoutePolicy` producer**。蓝牙 Sprint4 OOS。
5. **不动 `ParticipantAttributes`**。等 spike S7 出结论再决定是否取代 DataChannel transport（设计稿 §14 已留开放问题）。

## 7. 卡壳处置

- **如果 ArSpike 编译失败**：第一步检查 `csc.rsp` 是否包含 `-define:UNITY_AR_FOUNDATION`；第二步检查命名空间冲突（不要同时把 `ParrotDev` 编译进 ArSpike）；第三步看 LiveKit SDK 版本与代码 API 是否对齐（commit `2a7c57d7bcad2305a75bc75218e8064ccd5d10bf`）。
- **如果 LiveKit DataChannel 行为与 ParrotDev 不同**：先在 ParrotDev 反向跑同样 payload 验证 SDK 行为，再回到 ArSpike。**不要**在两侧同时改。
- **如果 spike S1/S2/S6 还没跑**：L3 不阻塞继续，但 L3 完成后必须挂上 spike 红黄绿结果再决定参数固化。

---

## 7.5 L3 收尾审计修复（2026-04-29 下午）

L3 4 组落地后做了一轮系统性审计（一类真实 bug + D 类偏离），R1–R6 + D5 已修复，落地点：

| 编号 | 文件 | 修复要点 |
|:--|:--|:--|
| **R1** [严重] | `LiveKit/RoomManager.cs` | `Connect()` 重入：缓存 `_connecting` Coroutine，新调用前 `StopCoroutine` 旧的，避免两份 `ConnectToRoom` 并行抢 `Room` 字段（Sprint3 `brain_connected_black_video_20260425.md` 同根因） |
| **R2** [严重] | `LiveKit/RoomManager.cs` | `Connect()` / `ReconnectUsingCachedCredentials()` 入口判 `IsDisconnecting` → 警告并 return；防止 chokepoint cool-down 期被新连接打穿 |
| **R3** [中] | `Lifecycle/AppLifecycleManager.cs` | `OnApplicationPause(true)` 覆盖所有非终态/非 ColdStart；新增 `_statePriorToPause` 让 resume 能区分回 Connected 还是回 PreConnect 阶段（TokenGate 等） |
| **R4** [中] | `Lifecycle/AppLifecycleManager.cs` | `OnApplicationPause(false)` 入口主动判 `elapsed >= T_LONG_BG` → 直接 `Transition(ShuttingDown)`，不依赖 iOS 后台 `Update()` tick |
| **R5** [中] | `Health/ConnectionHealthState.cs` | `ComputeOverall` 把 `VideoTier == "VIDEO_OFF"` 排除在 fresh frame 要求之外；空字符串档位仍视为"期待视频活跃"避免冷启动误判 Healthy |
| **R6** [低-中] | `LiveKit/RoomManager.cs` | `OnDestroy` 在 `Disconnect()` 后追加 `(Room as IDisposable)?.Dispose()`，与 chokepoint 步骤 5 对齐，防 Editor 重编译 / scene 切换的 identity 抢占 |
| **D5** [防御] | `Lifecycle/LifecycleShutdownService.cs` | chokepoint 步骤 3-4 的 `OnDisconnected += _ondc` 用 try/finally 包，`Room.Disconnect()` 异常时 `-=` 仍执行，避免每次 chokepoint leak 一份 lambda |

**未修（明确延后到 Phase 4 / 后续审计）**：
- D1 SDK `Reconnecting` event 订阅 — 等 spike S2 真机跑出 SDK 实际行为再决定 watchdog 形式
- D2 `Connect()` 完全收口到 `AppLifecycleManager.RequestConnect()` 包装 — Phase 4 UI 层做
- D3 `RequestColdStartReset()` — 与 M2 HUD 菜单一起做
- D4 `ReportDisconnected` 与 chokepoint step 7 双写 health 字段（行为正确，仅美学问题）— 未改
- D6 Bridge `isReconnect` 白/黑名单语义 — 当前行为正确，仅可读性
- G1 `Room.DataReceived` 路由 — Phase 4 Focus / BBox 实施时补
- G2 `ar_tracking_state` producer — 等 SceneProfileManager / ARLifecycleProbe
- G3 Brain 侧 `unknown` 持续阈值 — Phase 2 handler 实施时定
- M2 / M3 / M4 / M5 菜单 / Inspector / 多个 ScriptableObject / HUD EditorWindow — Phase 3 后段独立 todo

**回归**：`uv run pytest tests/test_scheduler/test_ecp.py` → 14 passed；`ReadLints` 全 ParrotApp 子树 0 errors。

---

## 8. 引用

- `.cursor/skills/livekit-unity-lifecycle/IMPL_REF.md` — 实现速查
- `.cursor/skills/livekit-unity-video-publish/IMPL_REF.md` — 视频发布速查
- `.cursor/memory/architecture/sprint4_protocol_v2_ecp.md` — 协议正式稿
- `.cursor/memory/architecture/sprint4_protocol_ecp_background_20260429.md` — 背景固化
- `.cursor/memory/architecture/sprint4_ecp_minimal_audit_20260429.md` — Phase 1 审计
- `docs/sprint4_research/result/INDEX_for_phase3.md` — Phase 3 决策索引
- `unity/ArSpike/Assets/Scripts/ParrotApp/MIGRATION.md` — 搬迁状态表
