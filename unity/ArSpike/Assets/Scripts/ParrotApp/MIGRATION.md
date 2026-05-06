# ParrotApp 脚本迁移区（Sprint4 暂存）

> 日期：2026-04-29 (L3 启动)
> 状态：staging — 目录结构是临时分类，正式 App 工作区的 Scripts/ 目录设计与 UI / 流程一起在 Sprint4 Phase 3+ 决定。
> 锚点：`.cursor/memory/architecture/sprint4_protocol_ecp_background_20260429.md`
> Phase 3 L3 入场：⭐ `.cursor/memory/architecture/sprint4_phase3_l3_entry_20260429.md` (authoritative)
> 审计参考：`.cursor/memory/architecture/sprint4_ecp_minimal_audit_20260429.md`
> LiveKit SDK：✅ 已加 `io.livekit.livekit-sdk` (commit `2a7c57d`)

## 当前定位

- **ArSpike** = 正式 AR App 的"接口/白模工作区"（不带美术资产）
- **GOSLOParrot** = 带资产的打包结果（未来）
- **ParrotDev** = Sprint 1–3 测试床；保持冻结，作为 Sprint3 真机调试留档与回归对照

ECP 协议代码以 ArSpike 为新主仓位；ParrotDev 的同名脚本视为 Sprint3 测试副本，不再同步修改。修改 ECP 行为只动 ArSpike 这一份。

## 迁移状态

### L1 + L2 已搬迁 / 已落地

| 文件 | 状态 | 命名空间 | 依赖 | 说明 |
|:--|:--|:--|:--|:--|
| `RPC/EcpDtos.cs` | ✅ Phase 1 | global | `System` + `UnityEngine.JsonUtility` | 纯 DTO；Phase 3 增加 `connection_overall` 字段 |
| `Core/UnityMainThread.cs` | ✅ Phase 3 早期 | `ParrotApp.Core` | `UnityEngine` | 主线程 dispatcher |
| `LiveKit/BrainParticipantResolver.cs` | ✅ Phase 3 早期 | `ParrotApp.LiveKit` | `LiveKit` | 静态 helper |
| `Config/ParrotLifecycleConfig.cs` | ✅ Phase 3 L1 | `ParrotApp.Config` | `UnityEngine` | 17 个可调阈值的 ScriptableObject；IMPL_REF.md §10 真源 |
| `Config/Editor/ParrotLifecycleConfigMenu.cs` | ✅ Phase 3 L1 | `ParrotApp.Config.EditorTools` | `UnityEditor` | `Tools/Parrot/Lifecycle Tuning` 菜单 |
| `Lifecycle/AppLifecycleState.cs` | ✅ Phase 3 L1 | `ParrotApp.Lifecycle` | 无 | 11 状态 enum + wire 字符串化 helper |
| `Lifecycle/AppLifecycleManager.cs` | ✅ Phase 3 L1 | `ParrotApp.Lifecycle` | `UnityEngine` + `Config` + `Health` | FSM 中枢；不依 LiveKit；接受外部信号驱动 |
| `Health/ConnectionHealthState.cs` | ✅ Phase 3 L1 | `ParrotApp.Health` | `System` | 数据快照 + overall 聚合规则 |
| `Health/ConnectionHealthAggregator.cs` | ✅ Phase 3 L1 | `ParrotApp.Health` | `UnityEngine` | producer 单写约束的具体宿主 |
| `Ecp/EcpStateDto.cs` | ✅ Phase 3 L1 | `ParrotApp.Ecp` | `UnityEngine` + `Health` | 周期心跳 + ConnectionHealth wire 形式 |
| `Ecp/LifecycleHeartbeatPublisher.cs` | ✅ Phase 3 L1 | `ParrotApp.Ecp` | `UnityEngine` + `Lifecycle` + `Health` + `Config` | 心跳 + connection.health.changed + intent.disconnect；transport 层接口化（默认 LogHeartbeatTransport stub） |

### L3 — 4 组搬迁路线（按 foundations → chokepoint/transport → publishers → consumers）

> **⭐ 入场锚点**：`.cursor/memory/architecture/sprint4_phase3_l3_entry_20260429.md`
> 编译依赖顺序、组内验收点、命名空间约定、卡壳处置，全在锚点里；**先读锚点再动手**。

#### Group 1 — Foundations ✅

| 文件 | 状态 | 命名空间 | 操作 |
|:--|:--|:--|:--|
| `unity/ArSpike/Assets/csc.rsp` | ✅ Group 1 | — | 已新增 `-define:UNITY_AR_FOUNDATION` |
| `LiveKit/RoomManager.cs` | ✅ Group 1 | `ParrotApp.LiveKit` | 已搬 + 增强：加 `OnConnecting` / `OnParticipantConnected` / `OnParticipantDisconnected` events、`IsDisconnecting` flag + `MarkIntentDisconnecting()`、`JoinIdentity` / `RoomName` 属性；移除 `TriggerGreetingAfterDelay` / `StartEditorReconnectTest` 测试残留 |

#### Group 2 — Chokepoint / Transport / Bridge ✅

| 文件 | 状态 | 命名空间 | 操作 |
|:--|:--|:--|:--|
| `Lifecycle/IGracefulShutdownParticipant.cs` | ✅ Group 2 | `ParrotApp.Lifecycle` | 已新建：解耦 chokepoint 与 publishers 的接口（Group 3 publishers 实现之） |
| `Lifecycle/RoomManagerLifecycleBridge.cs` | ✅ Group 2 | `ParrotApp.Lifecycle` | 已新建：RoomManager events → AppLifecycleManager.Report* + 灌 `room_connected` / `brain_present` / `reconnect_attempt_count` / `last_disconnected_at`；区分 graceful（IsDisconnecting=true）vs 被动断 |
| `Lifecycle/LifecycleShutdownService.cs` | ✅ Group 2 | `ParrotApp.Lifecycle` | 已新建：IMPL_REF.md §2 完整 chokepoint 协程（drain participants → MarkIntent + Disconnect → wait Disconnected event with T_DISCONNECT_WAIT_HARD soft timeout → Dispose → cool-down T_SHUTDOWN_COOLDOWN → ReportDisconnected）；OnApplicationQuit 走同步 DrainCoroutine 兜底 |
| `Ecp/LiveKitDataChannelHeartbeatTransport.cs` | ✅ Group 2 | `ParrotApp.Ecp` | 已新建：实现 `IHeartbeatTransport`，reliable DataChannel topics 固化为 `LiveKitDataChannelHeartbeatTransport.TopicState/Health/IntentDisconnect`；首次 PublishData 成功反向灌 `datachannel_ready` |

#### Group 3 — Publishers ✅

| 文件 | 状态 | 命名空间 | 操作 |
|:--|:--|:--|:--|
| `LiveKit/MicrophonePublisher.cs` | ✅ Group 3 | `ParrotApp.LiveKit` | 已搬 + 实现 `IGracefulShutdownParticipant` (ShutdownOrder=20) + 灌 `audio_publish_attempted` / `audio_published` / `audio_last_error` |
| `LiveKit/ARVideoPublisher.cs` | ✅ Group 3 | `ParrotApp.LiveKit` | 已搬 + 实现 `IGracefulShutdownParticipant` (ShutdownOrder=10) + config 化 `T_FIRST_FRAME_TIMEOUT` / `STALE_FRAME_THRESHOLD_LOW/HIGH_TIER` (动态选) / `T_TIER_COOLDOWN` + 监听 `AppLifecycleManager.OnStateChanged` 暂停 Blit + 灌 `video_publish_attempted` / `video_published` / `video_first_frame` / `video_fresh_frame` (1Hz 翻转检测) / `video_tier` (TierToWire) / `video_lifecycle_reason`(republishing/first_frame_timeout/lifecycle_background) |
| `LiveKit/VideoStateReporter.cs` | ✅ Group 3 | `ParrotApp.LiveKit` | 已搬 + 双轨灰：旧 `onVideoDegraded` RPC 路径 1:1 保留（向下兼容到 Brain Phase 2 收口）+ 同时灌 `video_lifecycle_reason` 做原因细分（track_muted/static_frame/app_backgrounded/ok→空字符串） |

#### Group 4 — Consumers ✅

| 文件 | 状态 | 命名空间 | 操作 |
|:--|:--|:--|:--|
| `Parrot/AnimationDriver.cs` | ✅ Group 4 + GOSLO 模块化 Step 2 | `ParrotApp.Parrot` | 已 1:1 搬；2026-05-06 加 `ReflexEnabled` 公共 flag — manifest 驱动 sin/cos 次级行为开关（默认 true，行为零漂移）|
| `Parrot/ParrotController.cs` | ✅ Group 4 + GOSLO 模块化 Step 2 | `ParrotApp.Parrot` | 已 1:1 搬；2026-05-06 加 `FlyTo(target, modelId)` / `PlayAnimation(name, modelId)` 重载 — 优先走 `ParrotRegistry.Resolve(modelId)` → `IParrotController.ApplyCapability`；fallback 至 `AnimationDriver` / `Animator` / dev-pulse（向后兼容） |
| `RPC/ParrotRpcHandler.cs` | ✅ Group 4 + GOSLO 模块化 Step 2 | `ParrotApp.RPC` | 已搬，保留 ECP-minimal `expires_at` / `active_locks=["body"]` 行为 + 加灌 `rpc_ready`；2026-05-06 加 `_ecp.meta.model_id` 提取 + 透传到 `ParrotController` 路由重载 |
| `RPC/EcpDtos.cs` | ✅ + GOSLO 模块化 Step 2 | global | 2026-05-06 加 `EcpCommandMetaDto` `[Serializable]` typed wrapper（含 `model_id`）+ `EcpCommandDto.meta` 字段 + `EcpCommandDto.ModelId` 便捷只读属性。Brain 端 `EcpCommand.meta dict[str, Any]` 经 JsonUtility 反序列化为该 typed slot；未声明 key（如 future `actor_id`）silently ignored — 安全前向兼容 |
| `LiveKit/VideoTierReceiver.cs` | ✅ Group 4 | `ParrotApp.LiveKit` | 已搬，保留 ECP-minimal `unknown_tier` / `no_video_publisher` reason；本类<b>不</b>灌 `video_tier`（ARVideoPublisher 是 sole producer） |

#### GOSLO 模型模块化 Step 2 — Manifest-driven controller layer ✅

> 2026-05-06 落地。spec：[`goslo_model_manifest_protocol_v1.md`](../../../../../.cursor/memory/architecture/goslo_model_manifest_protocol_v1.md) + [`goslo_modularization_residual_debt_20260506.md`](../../../../../.cursor/memory/architecture/goslo_modularization_residual_debt_20260506.md)
>
> 设计哲学：能力开放注册 + ParrotAnimation enum 8 项 = Brain LLM 词汇表 AND Parrot Reflex 触发器；非鹦鹉模型可完全自定义 capability_id，Reflex 关闭。Wire 0 改动（`EcpCommand.meta` 是 Phase 4 §8 锁内既有 dict 槽）。

| 文件 | 状态 | 命名空间 | 操作 |
|:--|:--|:--|:--|
| `Parrot/IParrotController.cs` | ✅ 新建 | `ParrotApp.Parrot` | Capability 路由契约 — 任何 model 控制器实现该 interface 即可接入。`ApplyCapability(id, paramsJson)` 返回 `false` = capability 未声明 → graceful-ignore；返回 `true` = 已 dispatch。 |
| `Parrot/ModelManifestDto.cs` | ✅ 新建 | `ParrotApp.Parrot` | JsonUtility 适配 DTO，Python `parrot.shared.model_manifest.ModelManifest` 的 C# 镜像；`Resources.Load<TextAsset>("parrot_models/<modelId>")` 读 + 自带 `ParrotReflexEnabled` / `DeclaredCapabilityIds` / `Supports()` 派生属性（与 Python 端语义对齐）。 |
| `Parrot/ParrotRegistry.cs` | ✅ 新建（P1 stub） | `ParrotApp.Parrot` | scene-singleton（参 RoomManager 模式）。P1 单 active：last-registered 控制器 + `Resolve("")` 返回 active；P3 多 actor 真路由由后续 Chat 接管。`EnsureInstance()` 由 ModelDriver 兜底实例化，无需手动布在 prefab 上。 |
| `Parrot/ModelDriver.cs` | ✅ 新建（OPTIONAL component） | `ParrotApp.Parrot` | Awake：`ModelManifestDto.LoadFromResources(modelId)`；Start：反射 `Type.GetType(controller_type)` → AddComponent → `Register(IParrotController)` + 可选 `auto_scale_to_pet_height`（按 renderer.bounds.size.y 推算缩放比）。Inspector `modelId` 字段空 = `"GOSLO_default"`。**未挂 ModelDriver 的旧场景仍能通过 AnimationDriver 直接路径跑**。 |
| `Parrot/GosloLegacyController.cs` | ✅ 新建 | `ParrotApp.Parrot` | `[RequireComponent(typeof(AnimationDriver))]` — IParrotController 的 GOSLO 实现，路由 `capability_id` → `AnimationDriver.SetState/FlyTo`；接受 `ConfigureFromManifest(manifest)` 灌 reflex 标志（`AnimationDriver.ReflexEnabled = manifest.ParrotReflexEnabled`）。无 manifest 时 fallback 全 8 reserved id + reflex on。 |
| `Resources/parrot_models/goslo_default.json` | ✅ 新建 | — | GOSLO 默认 manifest baseline — 8 reserved capability_id 全声明、`auto_scale_to_pet_height=false`（保留现有 prefab 大小）。Step 2 兼容性 sentinel：挂 ModelDriver 用此 manifest 跑，行为应与不挂 ModelDriver 的现有 GOSLO 完全一致。 |

#### 延后（明确不进 L3）

| 文件 | 归属 | 说明 |
|:--|:--|:--|
| `Vision/IFrameCapturer.cs` (XRCpuImage / AsyncGPUReadback 双实现) | `snapshot-identify` todo | spike S4 决出胜者后落地 |
| `captureSnapshot` ECP 化 | `snapshot-identify` todo | 与 IFrameCapturer 一起做 |
| Brain 侧 `connection.health.changed` / `intent.disconnect` event handler | ECP Phase 2 | 等 L0 event 入 EventEnvelope 后再加 |
| `AudioRoutePolicy` producer | Phase 4+ | 蓝牙 OOS，候选 BB 键留 `# CANDIDATE` |

## 与 ParrotDev 的关系

ParrotDev 仍然有这三份文件的同名拷贝。它们继续支持 Dev.unity 测试场景，**直到 Sprint3 测试矩阵的回归需求结束**。规则：

1. **不要双向同步**：修改 ECP 行为只改 ArSpike；ParrotDev 那一份在 Sprint3 留档冻结。
2. **不要在 ParrotDev 加新功能**：新增 Unity ECP handler（如 `captureSnapshot` ECP 化、`focus_region`、`camera_capture`）直接落 ArSpike。
3. **回归 ParrotDev**：如果未来需要在 ParrotDev 真机回归 Sprint3 用例，就从 ArSpike 反向 cp 一次最新版本，跑完测试再丢弃。

## L3 依赖搬迁顺序（已固化在锚点 §2.1）

```
io.livekit.livekit-sdk (Packages/manifest.json) ✅ 已加
        │
        ▼
Assets/csc.rsp  -define:UNITY_AR_FOUNDATION   ← Group 1 起点
        │
        ├─────────────► UnityMainThread (ParrotApp.Core)        ✅ 已搬
        │                       │
        │                       ▼
        ├─────────────► BrainParticipantResolver                 ✅ 已搬
        │                       │
        │                       ▼
        └─────────────► RoomManager  (ParrotApp.LiveKit) ◄── Group 1 必须先搬
                              │
                  ┌───────────┼─────────────────────────────┐
                  ▼           ▼                             ▼
        Group 2          Group 2                        Group 3
   RoomManagerLifecycleBridge  LiveKitDataChannel-          MicrophonePublisher
                                HeartbeatTransport          ARVideoPublisher
                                                            VideoStateReporter
                                                                │
                                                                ▼
                                                            Group 4
                                              ParrotController + AnimationDriver
                                                              │
                                                              ▼
                                              ParrotRpcHandler  +  VideoTierReceiver
```

> Group 顺序硬约束：
> - Group 2 `LiveKitDataChannelHeartbeatTransport` 必须在 `RoomManager` 就位之后，才能拿 `Room.LocalParticipant`。
> - Group 2 `LifecycleShutdownService.ChokepointCoroutine` 必须在所有 publishers 搬完后才能完整跑（`UnpublishTrack` 步骤在没有 publisher 时是 no-op，但行为契约要等 Group 3 完成后才能真验收）。
> - Group 4 `ParrotRpcHandler` / `VideoTierReceiver` 覆盖 ArSpike 现有 stub 时要保留 ECP-minimal 已落地的 `expires_at` 校验、`active_locks=["body"]` / `unknown_tier` / `no_video_publisher` 等行为，不要回退。

## 不搬迁清单

下列 ParrotDev 脚本属于测试束，永远不进 ArSpike：

- `Testing/Runtime/ParrotRuntimeHud.cs`
- `Testing/Runtime/ParrotSelfTestCoordinator.cs`
- `Testing/Runtime/ParrotDiagnosticsLog.cs`
- `Testing/Runtime/ParrotRpcRttProbe.cs`
- `Testing/Runtime/ParrotTestSeq.cs`
- `Testing/Editor/*`（所有 Editor 测试脚本）
- `Core/LauncherUI.cs`（Debug 版 Launcher，正式 App 用 UI Toolkit 重写）
- `AR/TapToPlace.cs`（Sprint 2 验证脚本）
- `Core/SceneProfileManager.cs`（Dev.unity 多 profile 切换器，正式 App 不需要）

## 不允许误读

- 不要把 ParrotDev 的 `LauncherUI.cs` 当作正式 App 启动流程参考；正式 App 启动流程见 `docs/sprint4_research/result/03_App_Flow_and_UI_Layout_Design.md`。
- 不要把 ParrotDev 的 `Dev.unity` 当作正式 App 场景模板；正式场景在 Phase 3+ 与 UI 设计一起重建。
- 不要把"ParrotApp"目录名当作最终命名；它只是 Sprint4 暂存分类，最终结构跟 UI / 流程设计一起拍板。
- 不要在 staging 期间反向把改动同步回 ParrotDev；ParrotDev 已冻结。
