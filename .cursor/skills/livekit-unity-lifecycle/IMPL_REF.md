---
name: livekit-unity-lifecycle / IMPL_REF
description: 实现侧速查 — AppLifecycleManager FSM、Room graceful shutdown chokepoint、connection_health 聚合、ARCore 后台 blank/crash 防御、setVideoTier 切换副作用、可调参数表（建议挂 ScriptableObject + 后续接 app 菜单）
---

# LiveKit Unity Lifecycle / 防御性机制 — 实现侧速查

> **本文用途**：让 Phase 3 实现 chat 在写 `AppLifecycleManager` / `RoomManager` graceful shutdown / `ConnectionHealthState` 聚合时**一次 Read 就能拿全实现要点**。
>
> **决策原因 / 证据等级 / 替代方案对比**：进 `docs/sprint4_research/result/05_lifecycle_and_defensive_design.md`。本文不复述决策原因，只列**当前实现要点 + 已确定参数 + 已知坑**。
>
> **状态**：tentative。Phase 3 落地后逐节升 ratified。
>
> **最后验证**：2026-04-29（Sprint4 Phase 3 前置调研产物 + Patch 3/4/5/6/7/9/10）。

---

## 0. 总览

```text
                ┌────────────────────────────────────────────┐
                │            AppLifecycleManager             │
                │   (Unity client FSM — 不暴露给后端 BT)     │
                └─────────────┬──────────────────────────────┘
                              │
       ┌──────────────┬───────┴───────┬──────────────────────┐
       │              │               │                      │
       ▼              ▼               ▼                      ▼
RoomManager   ARVideoPublisher  MicrophonePublisher   VideoTierReceiver
(graceful     (听 lifecycle:   (听 lifecycle:        (听 lifecycle:
shutdown      首帧门 / stale   设备切换 / 采样率)    cool-down 窗口)
+ watchdog)   / 后台 blank兜底)        │                      │
       │                               │                      │
       └─────────► ConnectionHealthState ◄────────────────────┘
                       │
                       ▼
                 EcpState 上行
                 (reliable DataChannel)
```

## 1. AppLifecycleState（11 状态 FSM）

```text
COLD START 链路
  cold_start → permission_gate → token_gate → ar_session_starting → connecting → connected → running

RUNNING 子状态
  running ├─ short_background    (OnApplicationPause(true), 0–5s)
          ├─ long_background     (5–30s, 上报 degraded)
          ├─ reconnecting        (SDK Reconnecting OR watchdog 触发)
          ├─ degraded            (单轨失败 / stale / VAD 异常)
          └─ shutting_down       (Disconnect 中)

TERMINAL
  disconnected (Disconnect + Dispose + cool-down 完成)
```

### 1.1 关键 transitions（不是穷举）

| 触发 | from | to | guard / side effect |
|:--|:--|:--|:--|
| `OnApplicationPause(true)` | running | short_background | 记录 `pause_ts = Time.realtimeSinceStartup`；**不**立即 mute / unpublish |
| `now - pause_ts ≥ T_SHORT_BG` | short_background | long_background | 上报 `connection.health.changed(state=degraded, reason=lifecycle_background)` |
| `now - pause_ts ≥ T_LONG_BG` | long_background | shutting_down | 进 graceful shutdown chokepoint（§2） |
| `OnApplicationPause(false)` 在 short 内 | short_background | running | 等 ARSession `SessionTracking` + 一次 `frameReceived` 实际触发再恢复 publish；**禁止**在过渡期推黑帧 |
| `OnApplicationPause(false)` 在 long 内 | long_background | reconnecting | 等 SDK reconnect 或 watchdog `T_WATCHDOG_HARD` 超时；fail → cold_start 链路重走 |
| `Room.Disconnected event` | * | shutting_down | 区分主动 vs 被动：用 `last_intent_disconnect_ts` 推断（设计稿 §5 可加 `intent.disconnect` event） |
| `ARSession.state == None / Stopped` | running | degraded(reason=ar_lost) | **不**直接切 `ar_session_starting`；让用户/Intent 决定 |
| `videoTier change request` | running | running | **不动** FSM；走 §6 cool-down |

### 1.2 已知坑

- `OnApplicationPause` 在 Editor 默认仅在窗口失焦时触发；真机才是产品行为。Sprint3 已有 `ParrotRuntimeHud` 类的测试束代码混淆此边界，**不要**复用测试束 `OnApplicationFocus` 路径作为产品入口。
- **不要**让 lifecycle FSM 直接驱动 BT 节点；后端通过 `EcpState` 感知，自决策。

---

## 2. Graceful shutdown chokepoint（Patch 3）

> 目的：消除 Sprint3 已踩的"30s ICE 残留 + identity 抢占 + RPC handler leak"组合坑。所有应用退出 / scene 切换 / long_background 强切路径**都必须**走此 chokepoint。

### 2.1 步骤（schema 层；实现在 `RoomManager` 或独立 `LifecycleShutdownService`）

```text
[shutting_down 入口]
  1. UnpublishTrack(_videoTrack)           // 等待协程完成
  2. UnpublishTrack(_audioTrack)           // 等待协程完成
  3. Room.Disconnect()                     // 不立即 Dispose
  4. 等 Room.Disconnected event            // 自维护 5s 超时兜底（T_DISCONNECT_WAIT_HARD）
  5. Room.Dispose()                        // 显式释放 native handle + RPC handler
  6. cool-down T_SHUTDOWN_COOLDOWN         // 默认 5s，避免 30s ICE 残留下的 identity 抢占
  7. 进入 disconnected 终态
[新 Connect 必须从 cold_start 链路重走]
```

### 2.2 已知坑

- iOS 飞行模式下 `Disconnected` event 可能**完全不触发**（Issue #90）→ 必须自维护超时（步骤 4 兜底）。
- `Room` implements `IDisposable`，但 C# GC 不及时释放 native handle 会让下一次 Connect 抢占 identity。**必须显式 `Dispose()`**。
- LiveKit Unity SDK commit `434009b` 已修 `RpcMethodInvocationReceived` handler leak；但 reconnect 周期里仍可能 race（参考 swift Issue #757）。Phase 3 spike S1 必查。
- **不要**在 `OnDestroy` 调用 `Room.Disconnect()` 然后立即 return —— Unity 销毁顺序无法保证 SDK 内部协程跑完。要走 `OnApplicationQuit` + 协程或 `async Task` 保证执行。

---

## 3. 自维护 connectivity watchdog（Patch 4）

> 目的：不依赖 SDK `Disconnected` event 作为唯一真相。LiveKit Unity SDK 在移动端事件不可靠（Issue #90 30s+ 才触发或不触发；Issue #53 `DisconnectReason` 缺失）。

### 3.1 设计要点

- **传输**：搭车 ECP `EcpState` 上行通道（reliable DataChannel），不另起 channel。频率 `T_HEARTBEAT_INTERVAL`（默认 5s）。
- **判定**：
  - Brain 端 `T_HEARTBEAT_SOFT` 未收到 → 视为 `degraded`，不强切；
  - Brain 端 `T_HEARTBEAT_HARD` 未收到 → 视为 `unhealthy`，触发降级（不强制重连，由用户/Intent 决定）；
- Unity 端 `RoomManager.IsConnected` 仍作为 cheap signal，但 **不能**作为唯一真相源。
- 自维护超时与 SDK 事件**双轨并行**：哪个先触发哪个生效（OR 关系），不互相覆盖。

### 3.2 已知坑

- 不要给 watchdog 加自动重连：避免 livekit/client-sdk-js #1852 thundering herd 类反模式；重连决策留给 lifecycle FSM 的 `long_background → shutting_down` 路径。
- heartbeat 内容应至少包含 `lifecycle_state` + `last_state_change_at` + `unity_identity`，不要复制完整 `EcpState`（带宽浪费）。

---

## 4. ConnectionHealthState 聚合（候选 BB 键 `session/connection_health`）

> 设计稿 §9.1 已列原始字段。本节只补**复合聚合规则** + **producer 路由**。

### 4.1 字段聚合（overall 4 态）

| overall | 条件 |
|:--|:--|
| `healthy` | room_connected ∧ brain_present ∧ rpc_ready ∧ video_fresh_frame ∧ audio_published |
| `degraded` | room_connected ∧ brain_present ∧ (rpc_ready ∨ datachannel_ready) ∧ ¬(video_fresh_frame ∧ audio_published) |
| `unhealthy` | ¬room_connected ∨ ¬brain_present |
| `unknown` | 冷启动期间 / pause-resume 过渡期 / ARSession 未 SessionTracking |

### 4.2 producer 分工（Phase 3 落地必读）

| 字段 | producer | 来源信号 |
|:--|:--|:--|
| `room_connected` | RoomManager | `Room.Connect/Disconnect/Reconnecting/Connected` 事件 |
| `brain_present` | RoomManager | 监听 `ParticipantConnected/Disconnected` 过滤 `agent-*` identity |
| `rpc_ready` | ParrotRpcHandler | `RegisterRpcMethod` 完成 + 一次 RTT 探测成功 |
| `datachannel_ready` | XRHandTracker / 任何 PublishData 用户 | 第一次 PublishData 成功 |
| `audio_publish_attempted` / `audio_published` / `audio_last_error` | MicrophonePublisher | publish 协程返回 + OnDisconnected 清理 |
| `video_publish_attempted` / `video_published` / `video_first_frame` / `video_fresh_frame` / `video_tier` | ARVideoPublisher | 已存在；扩展 `_lifecycle_reason`（`paused_arcore` / `lifecycle_background` 区分原因） |
| `ar_tracking_state` | SceneProfileManager 或新 ARLifecycleProbe | `ARSession.state` 字符串化 |
| `last_state_change_at` | AppLifecycleManager | 每次任何子字段变化更新 |
| `reconnect_attempt_count` | RoomManager | 自上次 healthy 起的 reconnect 次数 |
| `last_disconnected_at` | RoomManager | 用于 30s 残留判定 |

### 4.3 已知坑

- 不要让多个 producer 抢写同一字段（"漏抽象"反模式）。每字段单一 producer。
- 移除 `session/connection_health` 候选标记（审计 B5）必须等 producer 全部就位 + `bb_schema.py` type_hint 升回精确类型。

---

## 5. ARCore / AR Foundation 后台行为（Patch 5）

> 双向引用：`ar-foundation.mdc` rule §2 + `livekit-unity-video-publish/IMPL_REF.md` §7 平台后台。本节只补 **lifecycle 侧的处置策略**。

### 5.1 后台 blank OES texture

- ARCore 1.x 在 pause 时主动 blank 外部 OES texture（Unity issuetracker `arcore-black-screen-on-session-pause`；arfoundation-samples #592 wontfix）。
- `_arCameraBackground.material` 在后台/AR Session paused 时**不可信**；Blit 出黑帧。
- **处置**：
  1. `OnApplicationPause(true)` → `ARVideoPublisher` 收到 lifecycle 事件 → **暂停** Blit（不是 unpublish track，仅暂停产帧）；
  2. （可选）维护 `_lastValidRt`（在 `frameReceived` 里 `Graphics.Blit(_rt, _lastValidRt)`），仅做**本地 UI 显示**；
  3. **禁止**在过渡期把 `_lastValidRt` 推流给 Brain（会让 Gemini 描述旧画面，污染 turn）；
  4. `OnApplicationPause(false)` → 等 `ARSession.state == SessionTracking` + 一次新 `frameReceived` 实际触发再恢复 publish。

### 5.2 pause/resume 高频崩溃

- ARCore 1.47/1.50 在快速 `ArSession_pause/resume` 下内部 crash（google-ar/arcore-android-sdk #1736，2025-09，Pixel 6a 1 分钟内必现）。
- 多次后 `ArSession_update` 返回 `AR_ERROR_FATAL`（#1309），重建 session 也救不回。
- **处置**：
  - 用户切前后摄 / 重启 AR Session 限频 `T_AR_SESSION_TOGGLE_MIN`（默认 2s）；
  - 高频请求加用户确认对话框；
  - Phase 3 spike S6 测我们设备的 crash 率，> 5% 必须收紧到 3s。

### 5.3 已知坑

- `ARSession.enabled = false` 仅暂停 ARCore，**不**释放 RenderTexture / TextureVideoSource；不要据此推断"视频轨已暂停"。
- 非 ARCore 路径（WebCam fallback / XR Simulation）不走 OES texture，blank 问题不存在；但 lifecycle FSM 应统一对待。

---

## 6. setVideoTier 切换副作用（Patch 6 #14, #15）

> 双向引用：`livekit-unity-video-publish/IMPL_REF.md` §2 publish 配置 + §陷阱。

### 6.1 当前唯一可行路径

LiveKit Unity SDK FFI bridge **不暴露** `RTCRtpSender.SetParameters`；运行时调节 maxBitrate/maxFramerate **无 API**。Sprint4 VideoTier 切换只能：

```text
UnpublishTrack(_videoTrack)
   ↓ (等 unpublish 协程完成)
   ↓ cool-down T_TIER_COOLDOWN (默认 3s, 防 livekit/livekit #854 abandoned publish)
   ↓
改 RenderTexture 大小 / VideoEncoding 参数
   ↓
PublishTrack(new options)
   ↓ 等 First frame 实际到达
   ↓
回 ECP `applied` ack（保持 Brain `set_video_tier` 同步 Intent 模式）
```

### 6.2 已知坑

- `Simulcast=true` + 单消费者拓扑 → 移动端硬编多路 → CPU 飙升 + 发热降频；livekit/client-sdk-flutter #166 揭示 simulcast on 时切换黑屏。**Sprint4 默认 `Simulcast=false`**，除非 A10 同时订阅多档（届时再 spike）。
- `UnpublishTrack` + 立即 `PublishTrack` 太快会导致 server timeout（livekit/livekit #854 abandoned publish），**5 分钟后仍无法 republish**。cool-down 必须 ≥ 3s。
- Phase 3 spike S5 测黑帧时长（GeminiOnly→FULL→GeminiOnly），P95 < 800ms 才算可用；超出则 setVideoTier 改"仅在用户主动请求时升档"，不再后端自动调节。

### 6.3 SDK 升级行为变更（2026-04-29 16KB 对齐补丁同步落地）

- **`IRemoteTrack.SetEnabled` 从 no-op 变成真生效**（client-sdk-unity PR #250）。Sprint3 测试床若依赖"调 SetEnabled(false) 但远端仍在收帧"做延迟切换，会出现行为漂移。
  - **本仓库现状**：`ARVideoPublisher.TrySetPublishMuted` 走 `((ILocalTrack)_videoTrack).SetMute(...)`，**不在影响面**。
  - 若未来 receiver 端要做 selective subscription，请走 `IRemoteTrack.SetEnabled` 这条新路径，避免再用临时 hack。
- **AudioStream catchup**（PR #260）：远端音频从背景恢复时的"咔哒"已修复，但首包到达延迟可能微变。`RoomManager._remoteAudioStreams` 的强引用 + `Dispose()` 路径不变。
- 升级后 Phase 3/4 真机回归 checklist 增补：S5 setVideoTier 黑帧 + 远端语音连续性两条都要重测一次。

---

## 7. AudioRoutePolicy（候选 BB 键 `session/audio_route_policy`，Sprint4 仅 baseline）

> 设计稿 §9.3。Sprint4 蓝牙 OOS。

### 7.1 baseline schema

```text
input_device:    phone_mic | wired_headset_mic | bluetooth_mic(unsupported_or_experimental)
output_device:   phone_speaker | earpiece | wired_headset | bluetooth_a2dp(unsupported_or_experimental)
sample_rate_hz:  16000 | 24000 | 48000      # 当前 baseline=48000
echo_risk:       none | low | high(speakerphone)
status_note:     'phone_mic_48k_headphones_recommended'  # 默认
last_change_at:  float
```

### 7.2 Sprint4 落地约束

- Sprint4 **不**写 producer；候选 BB 键保留 `# CANDIDATE — no writer yet (Phase X)` 标记（审计 B5 反模式护栏）。
- 蓝牙输入/输出**显式**标 `unsupported_or_experimental`，`MicrophonePublisher` **不**自动选蓝牙。
- 非蓝牙 48k baseline 已修（Sprint3 brain_connected_black_video fix）；Sprint4 不退回。
- **禁止** Reflex 层自动切麦；任何路由变更走 Intent 或用户。

### 7.3 spike S8（不实现 producer）

仅确认 Android 上 `AudioSettings.OnAudioConfigurationChanged` 是否在蓝牙连接 / 有线插拔时触发；接口可用即闭项，producer 留 Phase 4+。

---

## 8. ParticipantAttributes 稳定性未确认（Patch 7）

- LiveKit Unity SDK README / 现有 IMPL_REF 都**未**明示 attributes 写入示例；设计稿 §14 已挂开放问题。
- Sprint4 EcpState 周期上报**先用 Reliable DataChannel**（设计稿 §4.2 已偏好）；不为 attributes 牺牲可测性。
- Phase 3 spike S7：100 次写入观察远端订阅，< 95% 成功率则放弃 attributes 路径。

---

## 9. DisconnectReason 缺失对 Brain 的影响（Patch 9）

- `livekit/client-sdk-unity` Issue #53（open since 2024-08）：`Disconnected` event 不携带 `DisconnectReason`。
- Brain Agent 无法区分"用户主动断 / 服务器踢 / ICE 失败 / 信令超时"。
- **处置**：在 ECP 通道里加显式 `intent.disconnect` event（layer=intent，actor=unity 或 brain），让 Brain 知道是 graceful 还是被动断。否则 Gemini 会把弱网误读为用户离开。
- 实现位置建议：`AppLifecycleManager` 进入 `shutting_down` 时通过 ECP event 路径上报；不要复用 `EcpAck`（那是 per-command）。

---

## 10. 建议可调参数表（用户特别要求：集合至一处，方便后续接 app 菜单）

> Phase 3 实现时建议挂 `ScriptableObject`（如 `ParrotLifecycleConfig.asset`）；字段同时暴露给开发者菜单（`Tools/Parrot/Lifecycle Tuning`）和未来 app 设置面板。**这些值是 spike 起点，不是定值**；S1–S8 跑完后再固化。

| 参数 | 默认值 | 单位 | 用途 | 关联 spike |
|:--|:--|:--|:--|:--|
| `T_SHORT_BG` | 5 | 秒 | OnApplicationPause(true) 短背景防抖窗 | — |
| `T_LONG_BG` | 30 | 秒 | 长背景强切阈值（进 shutting_down） | S2 |
| `T_DISCONNECT_WAIT_HARD` | 5 | 秒 | graceful shutdown 步骤 4 等 Disconnected event 超时 | S2 |
| `T_SHUTDOWN_COOLDOWN` | 5 | 秒 | Disconnect → 新 Connect cool-down，避免 30s ICE 残留 | — |
| `T_HEARTBEAT_INTERVAL` | 5 | 秒 | EcpState heartbeat 频率 | — |
| `T_HEARTBEAT_SOFT` | 15 | 秒 | watchdog 软超时 → degraded | — |
| `T_HEARTBEAT_HARD` | 30 | 秒 | watchdog 硬超时 → unhealthy | — |
| `T_AR_SESSION_TOGGLE_MIN` | 2 | 秒 | 用户切前后摄/重启 AR Session 最小间隔 | S6 |
| `T_TIER_COOLDOWN` | 3 | 秒 | setVideoTier unpublish→republish cool-down | S5 |
| `T_FIRST_FRAME_TIMEOUT` | 3 | 秒 | publish 后等 First frame 超时（超时降级 stale） | S5 |
| `STALE_FRAME_THRESHOLD_LOW_TIER` | 2 | 秒 | GeminiOnly 档 stale 阈值（宽松） | — |
| `STALE_FRAME_THRESHOLD_HIGH_TIER` | 0.5 | 秒 | FULL 档 stale 阈值（严格） | — |
| `BYTESTREAM_RPC_THRESHOLD_BYTES` | 15360 | bytes | 大于此值改走 ByteStream / SendFile | S3 |
| `SNAPSHOT_DEFAULT_WIDTH` | 480 | 像素 | captureSnapshot 默认宽 | S3 / S4 |
| `SNAPSHOT_DEFAULT_HEIGHT` | 270 | 像素 | captureSnapshot 默认高 | S3 / S4 |
| `SNAPSHOT_JPEG_QUALITY` | 75 | 0-100 | captureSnapshot JPEG 压缩质量 | — |
| `SIMULCAST_DEFAULT` | false | bool | 默认关；A10 上线后 spike 决定 | — |

> **建议代码注释规范**：每个参数定义处加 `// see livekit-unity-lifecycle/IMPL_REF.md §10` 注释，让代码读者直接跳到本表。**禁止**在多处硬编码同名常数（"协议污染" 反模式）。

---

## 11. spike 清单（Phase 3 实现前必跑）

> 完整 spike 范围 + 验收标准在 `docs/sprint4_research/result/05_lifecycle_and_defensive_design.md` §5.2 + `docs/sprint4_research/result/INDEX_for_phase3.md`。本节只列**入口 + 关联本文章节**。

| spike | 关联本文 | 验收速查 |
|:--|:--|:--|
| S1 LiveKit Unity SDK Disconnect race | §2 graceful shutdown | adb tc 弱网 5min；Room "复活" 0 次 |
| S2 飞行模式 Disconnected event 触发延迟 | §3 watchdog | 100 次采样 P95 < 5s |
| S3 ByteStream 50KB JPEG RTT | §10 BYTESTREAM_RPC_THRESHOLD_BYTES | P50<500ms / P95<2s / 失败<1% |
| S4 XRCpuImage vs AsyncGPUReadback | video-publish §4 | 480x270 主线程占用对比 |
| S5 setVideoTier 黑帧时长 | §6 + §10 T_TIER_COOLDOWN | P95 < 800ms |
| S6 ARCore pause/resume crash 率 | §5 + §10 T_AR_SESSION_TOGGLE_MIN | < 5% |
| S7 ParticipantAttributes 稳定性 | §8 | < 95% 成功 → 弃用 |
| S8 蓝牙/有线插拔检测 API | §7 | 接口存在即闭项 |

---

## 12. 变更日志

- 2026-04-29：创建。承载 `result/05_lifecycle_and_defensive_design.md` 调研产物的实现侧速查；Patch 3/4/5/6/7/9 主体；Patch 6 #13（重连不可靠）独立条目。可调参数表是用户筛查后明确要求的"集合至一处可调参数表，方便后续加入 app 菜单"。
