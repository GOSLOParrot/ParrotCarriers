# Sprint4 Phase 3 前置：Lifecycle / 防御性机制 调研汇总

> 日期：2026-04-29
> 状态：调研产物（**未筛选**）。用户人工筛选后会带回 fork 的 Phase 3 实现 chat 启动。
> 输入来源：`docs/sprint4_research/tasks/task1_lifecycle_dataflow_and_video_strategy.md` + `task3_livekit_stability_and_fast_frame_extraction.md` + Sprint3 真机 smoke (`docs/test/p2_5/`) + 本轮 Phase A 联网广搜（GitHub Issues / 官方文档）+ Phase B 接口验证（项目 skill）
> 边界：本文不写 C# / Python 实现代码；只产 **方案对比 + 证据等级 + 状态枚举建议 + 候选 BB 键**。落地由 Phase 3 实现 chat 决定。
> 不允许误读：
> - lifecycle 状态机 ≠ BT 节点；不要把"切后台/重连"塞进 Scheduler / BT。
> - VideoTier 切换属于 Intent 层，不允许塞进 Reflex 做毫秒级反应。
> - DSG L2-B 不接受实时帧写入；视频帧路径产物不应给 L2-B 加新写入口。
> - 蓝牙音频先标 `unsupported_or_experimental`，本轮只预留接管口（候选 BB 键 `session/audio_route_policy`）。
> - 本文不决定 skill 命名 / 是否独立成新 skill；那是用户决策。

---

## 0. 与先前调研的覆盖/缺口对照

对照 `docs/sprint4_research/tasks/task1_lifecycle_dataflow_and_video_strategy.md` 与 `task3_livekit_stability_and_fast_frame_extraction.md`：

| 原始问题 | 先前调研产物 | 已答 / 未答 / 需扩展 |
|:--|:--|:--|
| 切后台 主动断 vs 依赖 ICE Restart | `result/01` §2 给出三种策略（A/B/Hybrid） | **已答策略层面**；未给我们锁定 SDK 版本上的实测阈值 → 本文 §A1 扩展 |
| 切麦克风 / 蓝牙路由 | `result/01` 未深入 | **未答**；本文 §A1 + §B 接口验证回填，蓝牙先标 OOS |
| 网络切换 / ICE 重连 | `result/01` §1-2 提及 | **已答方向**，未答 LiveKit Unity SDK 在我们版本的事件可靠性 → §A1.GitHub #90 / #53 / #226 |
| Graceful shutdown / 30s ICE 残留 | `result/01` 未提；Sprint3 实测踩到 | **未答**；本文 §A1 + IMPL_REF patch §3 |
| AR 帧抓取 vs LiveKit publish 接缝 | `result/01` §3 提及 simulcast/replaceTrack/setParameters；IMPL_REF 已实现 Blit 路径 | **部分答**：先前在 Web/通用层面对比；本文 §A2 + §B 给出 5.1.5 + Unity SDK 实际可用 API |
| 高频截帧不阻塞主线程 | `result/01` §3.4 提到 RTHandles 泄漏；task3 直接问 | **方向答**；本文 §A2 把 XRCpuImage / AsyncGPUReadback 与 LiveKit RPC/ByteStream 接合 |
| 动态码率 / VideoTier | `result/01` §3 推荐 SetParameters | **理论答**；**Phase B 验证 LiveKit Unity SDK 当前版本不暴露 SetParameters** → 必须降级方案，§A3 |
| AR Foundation 后台/旋转黑帧 | `result/01` 未明示 | **未答**；本文 §A2.ARCore 后台 black-screen + Issue #1736 / #1309 / #592 |
| 图像压缩到 RPC 15KB 上限 | task3 直接问 | **未答**；本文 §A2.传输路径 |

**本轮要补**（不重复造轮子）：

1. 在我们锁定的 **Unity 2022.3 LTS + AR Foundation 5.1.5 + LiveKit Unity SDK `2a7c57d7bcad`** 上，先前调研提到的方案哪些 **API 真存在/不存在**。
2. 在 8 个 lifecycle 场景（L1–L8）下哪些是 Sprint3 实测过的、哪些必须做 spike。
3. 先前调研没覆盖的 **graceful shutdown + ARCore pause/resume 黑屏 + LiveKit SDK 重连事件不可靠** 三大坑。

---

## 1. 8 个 lifecycle 场景（Phase 3 调研边界）

> 本表所有方案必须能映射到下面之一；映射不上的方案进 §6 超纲附录，不进主表。

| # | 场景 | Sprint3 状态 | Phase 3 须给出的产物 |
|:--|:--|:--|:--|
| L1 | 冷启动：权限授予 → 入房 → 双轨发布 | ✅ 通过 | 入门 gate 状态枚举 + token/permission/ar/publish 四闸口 |
| L2 | 后台 < 30s 回前台 | ⚠️ 未充分验证 | 短背景策略 + 防抖窗口建议 |
| L3 | 后台 > 5min 回前台（系统回收 ARSession） | ⚠️ 未充分验证 | 长背景：主动释放 + 重新走冷启动链 |
| L4 | 切前后摄 / 关闭并重启 ARSession | ⚠️ 未实测 | 重建顺序：`ARSession.enabled=false` → 等 Tracking Lost → 重建 → republish |
| L5 | 切麦克风设备 | ✅ 已知"扬声器外放污染 Gemini Live" | `AudioRoutePolicy` 状态枚举 + 蓝牙 OOS |
| L6 | 弱网 / 丢包 / SignalReconnect / ICE restart | ⚠️ 未实测 | 信令 vs 媒体两条路径分别监控 + 降级阈值 |
| L7 | 应用退出：graceful Disconnect / 30s ICE 残留 | ✅ 已知 30s 残留 | 显式 Dispose + identity 抢占防御 + cool-down 窗口 |
| L8 | VideoTier 升降档 | ✅ 已设计 ECP setVideoTier；切换副作用未实测 | unpublish→republish 黑帧时长 + 关键帧重协商时序 |

---

## 2. Phase A：策略广搜（**不读本仓 skill**，只看官方/社区）

证据等级：
- **A** = ParrotCarriers 实测（必须能在 `docs/test/p2_5/` 找到对应日志）
- **B** = LiveKit / AR Foundation 官方文档承诺
- **C** = 社区博客 / GitHub Issue / 同类项目经验
- **D** = 推断 / 类比

不允许把 D 写得像 A。

### 2.A1 LiveKit + Unity 在移动端 AR 的连接生命周期（覆盖 L1/L2/L3/L6/L7）

| # | 方案/做法 | 等级 | 来源 | L# | 适用条件 | 已知坑 |
|:--|:--|:--|:--|:--|:--|:--|
| A1.1 | 纯依赖 SDK 自动 quick reconnect（`Reconnecting → Connected`） | C | LiveKit Swift SDK guides/reconnection；Unity SDK 行为类同 | L6 | 信令短抖（< 15s）+ 媒体路径未变 | iOS/Android 飞行模式下事件**严重不稳定**，30s 才触发或不触发（Issue #90 livekit/client-sdk-unity）。SDK 不暴露 `DisconnectReason`（Issue #53 open since 2024-08）。 |
| A1.2 | `OnApplicationPause(true)` 立即 `Room.Disconnect()` 强制重建 | C | Unity Netcode #1824 社区 workaround；Swift SDK manualReconnect 模式 | L2/L3/L7 | 长背景（> 5min）；权限/相机句柄已被系统回收 | 立即断会触发 30s ICE 残留 + identity 抢占；SDK Disconnect race（参考 client-sdk-swift #757 disconnecting/reconnect 状态机修复，Unity SDK 未确认是否同等）；恢复耗时 1.5–3s |
| A1.3 | **混合状态机**（防抖窗口 + 阈值切换）| D | task1 `result/01` §2.3 推荐；Sprint3 已知 30s 残留间接支持 | L2/L3 | 通用移动端 | 阈值是经验值，需在我们设备上实测；蓝牙短暂断流可能误触发 |
| A1.4 | 自维护 connectivity watchdog（不靠 SDK 事件） | C | LiveKit JS #1450（"connection loss detection takes 12-17s"）；Reddit/issue 共识 | L6 | 弱网；移动网络切换 | SDK 内部超时不可配；自维护需要 ping 通道（Reliable DataChannel + heartbeat） |
| A1.5 | Graceful shutdown：`UnpublishTrack` → `Disconnect` → 等待 `Disconnected` event → 显式 `Dispose()` | C | livekit/client-sdk-unity-web #24（hardware camera 不释放）；commit `434009b` 修复 RPC handler leak | L7 | 应用退出 / scene 切换 | Unity SDK Room 是 IDisposable；不显式 Dispose 会导致 RPC handler 累积；C# GC 不及时释放 native handle，下一次 Connect 抢占 identity → 30s 残留 PublishTrack NRE。Sprint3 已踩 |
| A1.6 | 反向：用 `ParticipantAttributes` 当 heartbeat（每 5s 写自己的 last_seen） | C | LiveKit attributes 只读传播；社区有人这么用 | L6 | 多端互监控 | Unity SDK 对 attributes 写入稳定性 SDK 文档承诺、无社区实测。`sprint4_protocol_v2_ecp.md` §14 已挂"开放问题" |
| A1.7 | 蓝牙音频路由：耳机插拔触发采样率重协商 → MicrophoneSource 需重建 | A | `docs/test/p2_5/brain_connected_black_video_20260425.md` "actualRate=24000 vs expectedRate=48000" | L5 | 蓝牙输入或多设备切换 | Sprint3 已锁定为 OOS，但**插拔有线耳机**也会触发；非蓝牙时 48k baseline 已修 |

#### A1 关键社区证据

- **livekit/client-sdk-unity Issue #90**（2025）：iOS 飞行模式下 `Disconnected` / `Reconnecting` 事件严重不稳定（30s+ 才触发，或完全不触发）。被官方标记到 #101 跟踪。**直接证伪 A1.1 在我们场景下可单独依赖**。
- **livekit/client-sdk-unity Issue #53**（2024-08，open）：`Disconnected` event 不携带 `DisconnectReason`。我们没法在业务层区分"用户主动断 / 服务器踢 / ICE 失败 / 信令超时"，只能靠时间戳 + 业务侧标记推断。
- **livekit/client-sdk-unity commit `434009b`**：修复 `OnDisconnect` 时 `RpcMethodInvocationReceived` handler 未取消订阅的 leak。**说明 Sprint3 已修的"重复 RegisterRpcMethod"反过来仍有可能因 SDK 自身漏洞重新引入**；Phase 3 应在 Disconnected → Connected 一周期内复测注册次数。
- **livekit/client-sdk-swift Issue #757**：Disconnect 与 reconnectTask 之间有 race，Room 可能"复活"。Swift 已加 `.disconnecting` 中间态。Unity SDK 未确认是否同等修；Phase 3 spike 必查。
- **livekit/livekit Issue #854**：publish + 立即 unpublish + 立即 republish 会导致服务器 timeout（abandoned publish）。直接关联 L8 setVideoTier unpublish-republish 实现。
- **livekit/client-sdk-js #1852**（2026-02）：`DefaultReconnectPolicy` 对 attempt 0 是 0ms 无 jitter，大房间 thundering herd。我们房间小，不直接受影响，但建议**在我们重连降级路径里也加 1–3s jitter**，避免 Brain + Unity 同时重连撞 token mint。

#### A1 阈值经验

社区共识（C 级）：

- **iOS App Nap / Android Doze**：~30s 内系统会冻结主线程
- **LiveKit 内部连接丢失探测**：12–17s（JS #1450）；Unity SDK 内部超时未公开
- **WebRTC ICE failed**：默认 ~30s
- **Signal websocket pong 超时**：~5s（livekit-server `signalConnectTimeout`）
- **建议防抖窗口**：5s（短抖），30s（强切阈值）
  - < 5s：完全不动，让 SDK quick reconnect
  - 5–30s：上报 `degraded`，不强切；准备重建
  - \> 30s：主动 Disconnect → cool-down 5s → 重新走冷启动 gate

> **注意**：上面阈值是 Phase 3 spike 的起点，不是定值。在我们设备（特别是国内 4G/5G + WiFi 切换）上必须复测。

### 2.A2 AR Foundation 5.1.x 视频帧采集到 LiveKit 的接缝（覆盖 L1/L4/L8 + 黑帧）

| # | 方案/做法 | 等级 | 来源 | L# | 适用条件 | 已知坑 |
|:--|:--|:--|:--|:--|:--|:--|
| A2.1 | `Graphics.Blit(null, _rt, _arCameraBackground.material)` 在 `frameReceived` 内（**当前实现**） | A | `IMPL_REF.md` §2 + Sprint3 真机已通 | L1 | 主视频流推 LiveKit | iOS 后台 → ARCore blank OES texture（Unity issuetracker）→ Blit 出黑帧；ARCameraBackground 在后台/AR Session paused 时不可信 |
| A2.2 | `XRCpuImage.ConvertAsync(callback)` + 主线程外 JPEG 编码 | B | AR Foundation 5.1 docs `Image capture`；XRCpuImage struct 必 Dispose | L1 / 截帧 | CPU 处理（OCR / 自建 CV / JPEG 上传） | AsyncConversion 必显式 Dispose 否则泄漏到 XRCameraSubsystem 销毁；onComplete 回调里 NativeArray 仅在 invocation 内有效，**必须 CopyTo** |
| A2.3 | `AsyncGPUReadback.Request(_rt)` + JPEG 编码 | B | Unity ScriptingAPI；ScreenCapture.CaptureScreenshotIntoRenderTexture 配套 | 截帧 / L8 升档 | GPU → CPU 不阻塞主线程 | 有几帧延迟；SystemInfo.supportsAsyncGPUReadback 需检查；Android 老机型可能 fallback 同步 |
| A2.4 | `Texture2D.ReadPixels` + `EncodeToJPG`（**禁止**） | C | 阻塞主线程 50–200ms（IMPL_REF §陷阱 2） | — | — | 任何场景都不该用；Sprint3 已避开 |
| A2.5 | ARSession.enabled = false → true 重启（**L4 切前后摄路径**） | C | google-ar/arcore-unity-sdk #79；arfoundation-samples #592 | L4 | 切镜头 / 显式重启 | ARCore 1.47-1.50：高频 pause/resume **崩溃**（issue #1736，2025-09）；多次后 ArSession_update 返回 AR_ERROR_FATAL（#1309，session 重建也救不回来）。**禁止高频切换**，Phase 3 给 cool-down 5s。 |
| A2.6 | 后台 ARCore 主动 blank texture 的兜底：保留最后有效帧 | C | arfoundation-samples #592（wontfix） + 评论建议自存最后一帧 | L2 / L3 | iOS/ARCore 后台短暂保活 | 需要在 frameReceived 里再 Blit 一份到 `_lastValidRt`；后台时切换到 `_lastValidRt` 但**不应继续推流给 Brain**（会让 Gemini 描述旧画面） |
| A2.7 | 首帧门：`First AR frame received` 之前**不**调用 `PublishTrack` | A | `brain_connected_black_video_20260425.md` "frames=1 publish"；IMPL_REF §6 | L1 | 冷启动 publish gate | Sprint3 已加；必须固化为 lifecycle FSM 的入境条件 |
| A2.8 | 新鲜帧门：`HasFreshFrame=false` 时降级（mute / videotier / videoDegraded） | A | IMPL_REF §6 已实现 stale 阈值 | L2/L3/L8 | 后台返回、tier 切换、ARCore lost | 当前阈值是固定 N 秒；建议改为 tier-aware（GeminiOnly 可宽松；FULL 必须严格） |
| A2.9 | RPC payload 上限 15KB → 用 `RegisterByteStreamHandler` / `SendFile` 传图 | B | LiveKit docs Sending files & bytes；livekit/client-sdk-js PR #1832 加大 RPC | 截帧 | identify_object 高质量回传 | Unity SDK ByteStream API 已暴露（IMPL_REF §4.B1 方案 B）；但 SDK 是 Developer Preview，稳定性需 spike |

#### A2 关键社区证据

- **Unity Issue Tracker `arcore-black-screen-on-session-pause`**：ARCore 行为变更，pause 时 OES texture 被 blank。AR Foundation 5.x 标 wontfix（refactor 太大）。**直接影响 L2/L3 黑帧策略**。
- **arfoundation-samples #592**：同上，wontfix；评论里官方建议"自存最后一帧 + 用自己 shader 渲染"。
- **google-ar/arcore-android-sdk #1736**（2025-09）：ARCore 1.47/1.50 在快速 pause/resume 下内部 crash。可复现脚本里 `shared_camera_java` 1 分钟内必现。我们的 Sprint4 lifecycle 必须在 ARSession 切换时加 cool-down。
- **google-ar/arcore-android-sdk #1309**：pause/resume 多次后 `ArSession_update` 返回 `AR_ERROR_FATAL`，连重建 session 都救不回来。说明 L4 不能反复切；用户主动切前后摄应限频（建议 1 次 / 2 秒）。

### 2.A3 VideoTier 动态切换（覆盖 L8）

| # | 方案/做法 | 等级 | 来源 | L# | 适用条件 | 已知坑 |
|:--|:--|:--|:--|:--|:--|:--|
| A3.1 | `RTCRtpSender.SetParameters(maxBitrate, maxFramerate)` 运行时调节（**理想方案**） | B | livekit-flutter / client-sdk-js 都暴露；`result/01` §3 推荐 | L8 | 微调档位、不重协商 | **LiveKit Unity SDK 当前版本（FFI bridge）不暴露此 API**；Phase B 验证 → 必须降级到 A3.3 |
| A3.2 | Simulcast 切层（dynacast） | B | LiveKit kb 配置；server 端 dynacast | L8 | 多消费者订阅不同档位 | 移动端硬编多路 → CPU 飙升 + 发热降频（`result/01` §3 已建议**坚决摒弃**）；我们消费者只 1 个 Gemini Live，没必要 |
| A3.3 | UnpublishTrack → 改 RenderTexture 大小 / VideoEncoding → PublishTrack 重发布（**当前实现**） | A | `ARVideoPublisher.cs` tier 重建路径；IMPL_REF §2 | L8 | 任意档位变更 | 重协商关键帧 → 远端**短时黑屏**；livekit/livekit #854：unpublish+republish 过快服务器 timeout；Issue #166（Flutter）：simulcast on 时 republish 黑屏（关键帧请求） |
| A3.4 | 改 RenderTexture 大小但**保留 Track**（in-place resize） | D | 推断；TextureVideoSource 内部 size 协商不确定是否触发 SDP renegotiate | L8 | 想要 0 黑屏 | Spike：未确认 SDK 行为；可能 codec 内部已 fixed resolution，更换会被忽略；建议先验小步实验 |
| A3.5 | 双 Track 设计：Tier-A (low) 常驻 + Tier-B (high) 按需 publish/unpublish | C | LiveKit "screenshare + camera" 双轨模式 | L8 | A10 升档时短时挂高质量轨 | 服务器侧带宽 + 双发布 metadata；Brain 必须 attach 正确 Source；落地复杂度高 |
| A3.6 | 不切 Tier 流，而是按需走 `captureSnapshot` 高质量 JPEG ByteStream | A | IMPL_REF §4 + Sprint4 acceptance #2 | L8 / 截帧 | identify_object 高清不需要持续流 | 已是当前 Sprint4 计划；A3.5 仅当 A10 持续高频识别才需要 |

#### A3 关键社区证据

- **LiveKit Unity SDK README**（GitHub）：仅在 `PublishTrack(track, options)` 接受 `TrackPublishOptions.VideoEncoding`；没有暴露 `RtpSender.SetParameters` 或类似运行时调节方法。
- **livekit/livekit #854**：abandoned publish 即使等 5 分钟也无法 republish；说明 unpublish-republish 时序必须等服务器确认（`UnpublishTrack` 必须 `yield return` 完成）。
- **livekit/client-sdk-flutter #166**：simulcast on 时 toggle camera 黑屏；建议**Sprint4 默认关 simulcast**（IMPL_REF §2 已经 simulcast=true，需要复审是否真有人订阅多档）。

#### A3 推荐立场

> 在 LiveKit Unity SDK 不暴露 `SetParameters` 之前，**只能走 A3.3（unpublish→republish）**。Sprint3 已实现，Sprint4 验收点是**升降档过程中黑帧时长 + 关键帧重协商时序 + Gemini Live 描述漂移**。建议：
> 1. Phase 3 给 setVideoTier 加 cool-down 3s（防 #854 abandoned publish）。
> 2. 升档（GeminiOnly → FULL）必须等"低档轨完全 Unpublish + 高档轨 First frame"再回 ECP `applied` ack（Sprint4 已用同步 Intent 模式）。
> 3. 默认 `Simulcast=false`（除非 A10 同时订阅；我们当前没有）。
> 4. **明确弃用 A3.1/A3.2**，写进 §5 的"弃用"清单。

---

## 3. Phase B：接口验证（在我们锁定版本上能不能跑）

> 锁定版本：Unity 2022.3 LTS + AR Foundation 5.1.5 + LiveKit Unity SDK `2a7c57d7bcad2305a75bc75218e8064ccd5d10bf`
>
> 每条 Phase A 方案三问三答：
> 1. **API 在锁定版本是否存在 / 签名**？
> 2. **IMPL_REF.md 有无相关已踩坑 / 已验证片段**？
> 3. **API 不存在或不稳定时的降级路径**？

### 3.B1 Lifecycle 类（Phase A.A1）

| # | API 存在性 | IMPL_REF 关联 | 降级路径 |
|:--|:--|:--|:--|
| A1.1 quick reconnect | **存在但事件不可靠**：`Room.ConnectionStateChanged` / `Disconnected` event 已暴露，但 Issue #90 表明移动端事件可能 30s+ 才触发 | IMPL_REF §陷阱 9 已警告 "反复 Play/Stop 触发 identity 抢占"；§7 平台后台行为已记录 iOS 后台冻结 | 自维护 watchdog（A1.4）+ 业务层超时；不要把 SDK 事件当唯一真相 |
| A1.2 主动 Disconnect | **存在**：`Room.Disconnect()`（IEnumerator 返回值未确认 yield 行为）；`Room` implements IDisposable | IMPL_REF §6 "断线 / 重连后发布状态污染" 已修复；§陷阱 9 已记录 30s grace period | 必须 `Disconnect → 等 Disconnected event（或自维护 5s 超时）→ Dispose() → cool-down 5s → 新 Connect`；不能立即 Connect |
| A1.3 混合状态机 | 纯业务层；不依赖 SDK 新 API | 无（Sprint3 没做 lifecycle FSM） | 直接落地为 `AppLifecycleManager`（设计稿 §9.2 已挂） |
| A1.4 自维护 watchdog | Reliable DataChannel `PublishData` + heartbeat | IMPL_REF 没明示 heartbeat 设计 | 在 ECP `EcpState` 上行通道里搭顺风车（每 N 秒上报一次 `connection.health`） |
| A1.5 Graceful shutdown + Dispose | `Room.Dispose()` 存在；`UnpublishTrack` 存在；`livekit/client-sdk-unity` commit 434009b 已修 RPC handler leak | IMPL_REF §6 未涵盖 graceful shutdown 流程 | **核心 patch 项**：在 `RoomManager` / `OnApplicationQuit` 强制等待 Disconnected 事件 + 显式 Dispose Room；ParrotApp 入口必须有 graceful shutdown 路径 |
| A1.6 ParticipantAttributes heartbeat | **未在 Unity SDK README / IMPL_REF 看到 attributes 写入示例**；`sprint4_protocol_v2_ecp.md` §14 已挂开放问题 | 无 | **降级到 Reliable DataChannel**（设计稿 §4.2 已偏好）；不为 attributes 牺牲可测性 |
| A1.7 蓝牙采样率重协商 | `MicrophoneSource(deviceName, gameObject, channels, sampleRate)` 存在；client-sdk-unity #169 + #77 揭示 SDK 在某些 Android 上有问题；Sprint3 已配置 48k baseline | IMPL_REF §2 "音频推流对偶" + brain_connected_black_video_20260425 已 fix 非蓝牙；§7 平台后台已记录蓝牙单独问题 | Sprint4 蓝牙先标 OOS（候选 BB 键 `session/audio_route_policy`）；插拔有线耳机检测放在 Phase 3 后做 |

### 3.B2 帧采集类（Phase A.A2）

| # | API 存在性 | IMPL_REF 关联 | 降级路径 |
|:--|:--|:--|:--|
| A2.1 Blit 路径 | `ARCameraManager.frameReceived` 事件 + `ARCameraBackground.material` shader 在 5.1.5 存在 | IMPL_REF §2 + ar-foundation rule §2 双向锁定；当前实现 | 无（这是当前最稳路径） |
| A2.2 XRCpuImage.ConvertAsync | **存在**：`ARCameraManager.TryAcquireLatestCpuImage(out XRCpuImage)`、`XRCpuImage.ConvertAsync(ConversionParams, callback)`；`AsyncConversion` IDisposable | IMPL_REF 未实现 captureSnapshot 路径；§4.B1 仅设计 | 适合 captureSnapshot：在回调里立即 CopyTo + Dispose；外层用 ImageConversion.EncodeArrayToJPG |
| A2.3 AsyncGPUReadback | **存在**：`Rendering.AsyncGPUReadback.Request/RequestIntoNativeArray`；`SystemInfo.supportsAsyncGPUReadback` 需查询 | IMPL_REF §陷阱 2 已记录 ReadPixels 阻塞；未实现 AsyncGPUReadback | 替代 captureSnapshot 路径之二（与 A2.2 选一）。**A2.2 vs A2.3 对比**：A2.2 直接拿 ARCore 原始 buffer 不经 GPU 渲染管线，更快；A2.3 拿的是 `_rt` 已经 Blit 过的结果，能复用 publish 用的 RenderTexture，但多一次 GPU→CPU。Phase 3 实测决定 |
| A2.5 ARSession.enabled toggle | `ARSession.enabled` 属性存在；`ARSession.state` 枚举存在 | ar-foundation-rule §1 + IMPL_REF §7 平台后台 | ARCore #1736 / #1309 警告：限频 1 次 / 2 秒；切换后必须等 `ARSession.state == SessionTracking` 才 republish |
| A2.6 自存最后有效帧 | `RenderTexture` 拷贝 `Graphics.Blit(_rt, _lastValidRt)` 即可 | IMPL_REF 未实现 | 仅做"渲染显示"用，不应推流；切前台后必须等新 First frame 再恢复推流 |
| A2.7 First frame gate | `ARVideoPublisher.HasFreshFrame` / `LastFrameAgeSeconds` 已存在 | IMPL_REF §6 "已实现产地新鲜帧门" | 当前阈值固定；Phase 3 让 tier-aware |
| A2.8 stale 帧降级 | `VideoStateReporter.onVideoDegraded(reason=static_frame)` 已存在 | IMPL_REF §6 已实现 | 扩展 reason 词表：`paused_arcore` / `lifecycle_background` 区分原因 |
| A2.9 ByteStream / SendFile | **存在**：`Room.RegisterByteStreamHandler(topic, handler)` + `LocalParticipant.SendFile(...)`（IMPL_REF §4 提到）；client-sdk-unity SKILL §8 有完整示例 | IMPL_REF §4 已设计 captureSnapshot 方案 B | 高质量截图（>15KB）必走 ByteStream；但 SDK 是 Developer Preview，**Phase 3 必 spike**：发 50KB JPEG 测端到端延迟 + 失败率 |

### 3.B3 VideoTier 类（Phase A.A3）

| # | API 存在性 | IMPL_REF 关联 | 降级路径 |
|:--|:--|:--|:--|
| A3.1 SetParameters | **不存在**（FFI bridge 未暴露 RTCRtpSender） | 无 | 直接弃用，记入 §5 |
| A3.2 Simulcast 切层 | `TrackPublishOptions.Simulcast = true/false` 存在；server-side dynacast 是服务器配置 | IMPL_REF §2 当前 `Simulcast = true`（默认）但**没有多消费者订阅多档**，浪费 CPU；Flutter #166 simulcast 切换黑屏 | Phase 3 默认 `Simulcast = false`；除非 A10 上线后明确订阅 high 层 |
| A3.3 unpublish→republish | `LocalParticipant.UnpublishTrack` + `PublishTrack` 都存在 | IMPL_REF §2 已实现 tier 重建；陷阱 9 已警告 grace period 20-30s | **当前唯一可行路径**；加 cool-down 3s + 等 First frame |
| A3.4 in-place resize | `RenderTexture.Release/Create` 存在；TextureVideoSource 持有 RT 引用，是否触发 SDP renegotiate **未知** | 无 | 标 spike：试 RT.Release 不 unpublish track，看 LiveKit 远端是否能续订 |
| A3.5 双 Track 设计 | API 都存在；但需要 Brain 端订阅过滤逻辑（按 source/name） | IMPL_REF §2 默认单轨 `ar-camera`；命名空间未预留 | 标 spike，仅 A10 落地后展开 |
| A3.6 captureSnapshot 替代升档 | 同 A2.9 | IMPL_REF §4 已设计 | 已采用，Sprint4 主路径 |

#### Phase B 不允许误读复核

- ECP 不替代 Scheduler / BT：本文产出的 lifecycle 状态机（§4 `AppLifecycleState`）是 Unity 客户端的 UI/媒体管理 FSM，**不暴露给后端 BT**；后端只通过 ECP `EcpState.app_lifecycle_state` + `connection.health.changed` 事件感知。
- DSG L2-B 工作记忆：本文不增加任何视频帧 → L2-B 写入路径；`captureSnapshot` 仍走 `SnapshotEvent`（Phase 4 `snapshot-identify` 任务）。
- VideoTier 切换属于 Intent：A3.3 unpublish-republish 的发起方仍是 Brain `set_video_tier` Intent tool（已是同步 Intent，见 brain_connected_black_video_20260425 fix）。**禁止 Reflex 层做毫秒级降档**。

---

## 4. 建议字段 / 状态枚举 / 候选 Blackboard 键（**schema 层面，不写实现**）

### 4.1 `AppLifecycleState`（Unity 侧 FSM）

> 锚点：`sprint4_protocol_v2_ecp.md` §9.2 已挂候选 11 状态；本文细化 transitions。

```text
cold_start
  ├─ permission_gate         (Camera + Mic 未授权)
  ├─ token_gate              (Token mint pending)
  ├─ ar_session_starting     (ARSession.state ≠ SessionTracking)
  ├─ connecting              (Room.Connect pending)
  ├─ connected               (Room connected, 但 First frame 未到)
  └─ running                 (双轨发布完成 + AR fresh frame + Brain in room)

running
  ├─ short_background        (OnApplicationPause(true) < 5s 防抖窗口)
  ├─ long_background         (5–30s,  上报 degraded, 不强切)
  ├─ reconnecting            (SDK Reconnecting 或自维护 watchdog 触发)
  ├─ degraded                (单轨失败 / stale frame / VAD 异常)
  └─ shutting_down           (Disconnect 中, 等待 Disconnected event)

terminal
  └─ disconnected            (Disconnect + Dispose + cool-down)
```

**transitions（建议，不是实现）**：

| 触发 | from | to | guard |
|:--|:--|:--|:--|
| `OnApplicationPause(true)` | running | short_background | 记录 ts |
| `now - pause_ts >= 5s` | short_background | long_background | 上报 `connection.health.changed(state=degraded)` |
| `now - pause_ts >= 30s` | long_background | shutting_down | 进 graceful shutdown |
| `OnApplicationPause(false) before 5s` | short_background | running | 等 First frame 验证；fail → degraded |
| `OnApplicationPause(false) 5–30s` | long_background | reconnecting | 等 SDK reconnect 或 watchdog 30s 超时；fail → cold_start |
| `Disconnected event` | * | shutting_down | 区分主动 vs 被动通过 last_intent_ts 推断 |
| `ARSession.state == None / Stopped` | running | degraded(reason=ar_lost) | 不直接切 ar_session_starting，等用户/policy |
| `videoTier change` | running | running | 不动 FSM；走 §A3.3 |

### 4.2 `ConnectionHealthState`（schema 层；BB 候选键 `session/connection_health`）

> 设计稿 §9.1 已列字段；本文补三组**复合状态**：

```text
overall: healthy | degraded | unhealthy | unknown
  - healthy:    room_connected ∧ brain_present ∧ rpc_ready ∧ video_fresh_frame ∧ audio_published
  - degraded:   room_connected ∧ brain_present ∧ (rpc_ready ∨ datachannel_ready) ∧ ¬(video_fresh_frame ∧ audio_published)
  - unhealthy:  ¬room_connected ∨ ¬brain_present
  - unknown:    冷启动期间 / pause-resume 过渡期

reconnect_attempt_count: int       # 自上次 healthy 起的 reconnect 次数
last_disconnected_at: float        # epoch；用于 30s 残留判定
last_state_change_at: float

# Phase 3 落地 producer：AppLifecycleManager + RoomManager + ARVideoPublisher 各自更新自己负责的子字段
```

### 4.3 `AudioRoutePolicy`（候选 BB 键 `session/audio_route_policy`）

> 设计稿 §9.3；本轮蓝牙仍 OOS。

```text
input_device:    phone_mic | wired_headset_mic | bluetooth_mic(unsupported_or_experimental)
output_device:   phone_speaker | earpiece | wired_headset | bluetooth_a2dp(unsupported_or_experimental)
sample_rate_hz:  16000 | 24000 | 48000      # 当前 baseline=48000
echo_risk:       none | low | high(speakerphone)
status_note:     'phone_mic_48k_headphones_recommended'   # 默认
last_change_at:  float

# Phase 3 落地 producer：MicrophonePublisher 在 Microphone.devices 变化时更新；蓝牙先不订阅检测
# 不允许 Reflex 层根据此键做"自动切麦"，必须留给用户/Intent
```

### 4.4 `MediaRouteEvent`（L0 event；非 BB 键）

> 设计稿 §9.3 已挂；建议字段：

```text
event: media.audio_route.changed | media.video_state.changed
input_device, output_device:    上面枚举值
prev_sample_rate_hz, new_sample_rate_hz
echo_risk
trigger:    user_gesture | os_event | startup | bluetooth_change
ts
```

### 4.5 与 ECP 的接合点

`EcpAck.frontend_state` 已有 `active_locks` / `video_tier`（设计稿 §5.2）。Phase 3 落地时建议**复用同一对象**，不要再发明新结构：

```text
EcpAck.frontend_state += {
  app_lifecycle_state:  上面 AppLifecycleState 枚举
  ar_tracking_state:    SessionInitializing | SessionTracking | None | Limited (AR Foundation 原生枚举字符串)
  connection_overall:   healthy | degraded | unhealthy | unknown    (ConnectionHealthState.overall)
}
```

`EcpState`（reliable DataChannel 周期上报）则承载完整 `ConnectionHealthState` + `AudioRoutePolicy.status_note`。

---

## 5. 三段式输入摘要（给下游 Phase 3 实现 chat）

### 5.1 已确认采用（A/B 级证据 + 与 ECP/RIT 边界不冲突）

| 项 | 依据 | 关联 L# |
|:--|:--|:--|
| 混合状态机（短/长背景 + 防抖 5s/30s） | A1.3 + 阈值经验 + Sprint3 30s 残留实测 | L2/L3 |
| Graceful shutdown：`UnpublishTrack → Disconnect → 等 Disconnected event → Dispose → cool-down 5s` | A1.5 + livekit/client-sdk-unity-web #24 + Sprint3 实测 | L7 |
| 自维护 connectivity watchdog（搭车 EcpState 上行通道） | A1.4 + livekit/client-sdk-unity #90/#53 | L6 |
| Blit + frameReceived 主推流路径不变 | A2.1 + IMPL_REF + Sprint3 已通 | L1 |
| `XRCpuImage.ConvertAsync` 用于 captureSnapshot（**优先**） | A2.2 + AR Foundation 5.1 docs | 截帧 |
| AsyncGPUReadback 作为 captureSnapshot 备选 | A2.3 | 截帧 |
| First frame gate + stale frame 降级 | A2.7/A2.8 + Sprint3 实测 | L1/L2/L3 |
| ByteStream / SendFile 传 >15KB JPEG | A2.9 + IMPL_REF §4 方案 B | 截帧 |
| VideoTier 切换走 unpublish→republish + cool-down 3s | A3.3 + livekit/livekit #854 | L8 |
| 默认 `Simulcast=false`（除非 A10 同时订阅多档） | livekit/client-sdk-flutter #166 + 我们消费者只 Gemini Live | L8 |
| `AppLifecycleState` 11 状态（§4.1）作为 Unity FSM | 设计稿 §9.2 + 本轮细化 | L1–L7 |
| `ConnectionHealthState.overall` 4 态聚合 | 设计稿 §9.1 + 本轮细化 | L6 |
| 音频默认 `phone_mic_48k_headphones_recommended` baseline | A1.7 + Sprint3 fix | L5 |

### 5.2 尚有不确定性（spike，每条带范围 + 验收标准）

| spike # | 范围 | 验收标准 |
|:--|:--|:--|
| S1 | LiveKit Unity SDK Disconnect race / Room resurrection 是否影响 Unity（参考 swift #757） | 在 Unity 上复现脚本：connect → 模拟弱网（adb tc）→ 观察 5 分钟内 Connect/Disconnect 状态切换次数；目标 0 次"复活"。如有则报上游 + 业务层加 `_disconnecting` flag |
| S2 | iOS / Android 飞行模式开关下 `Room.Disconnected` event 触发延迟分布 | 100 次开关采样：触发时间分布、未触发率；目标 `< 5s P95` 触发，未触发率 < 5%；超出则 watchdog 超时阈值改 5s |
| S3 | ByteStream 50KB JPEG 端到端 RTT + 失败率（移动 4G/WiFi） | 100 次采样：P50 < 500ms，P95 < 2s；失败率 < 1%；超出则 captureSnapshot 必须降到 480x270 走 RPC |
| S4 | `XRCpuImage.ConvertAsync` vs `AsyncGPUReadback` 真机性能对比（Pixel 6a / Samsung 中端） | JPEG 480x270 端到端延迟 + 主线程占用；选胜者作为 captureSnapshot 主路径 |
| S5 | `setVideoTier` unpublish→republish 期间黑帧时长 | 测 GeminiOnly→FULL→GeminiOnly 三档跳变；目标黑帧 < 800ms（Gemini Live 1.5s 体感目标内）；超出则改默认仅在用户主动请求时升档 |
| S6 | ARCore pause/resume 高频崩溃（Issue #1736）在我们设备的复现率 | adb 自动脚本 5 分钟运行：crash 率；如 > 5% 必须给 L4 切前后摄加用户确认对话框 |
| S7 | `ParticipantAttributes` 写入 Unity SDK 稳定性（设计稿 §14 开放问题） | 100 次写入观察远端订阅是否收到；< 95% 则放弃 attributes，全走 Reliable DataChannel |
| S8 | 蓝牙耳机插拔检测（不进 Sprint4 实现，但要 spike API） | `AudioSettings.OnAudioConfigurationChanged` 是否在 Android 蓝牙连接时触发；只确认接口存在，不实现 producer |

### 5.3 明确弃用

| 项 | 弃用理由 |
|:--|:--|
| `RTCRtpSender.SetParameters` 运行时调节 | LiveKit Unity SDK FFI bridge 不暴露 |
| Simulcast 在 Sprint4 默认开（`Simulcast=true`） | 单消费者（Gemini Live）+ 移动端硬编多路 → CPU/发热；livekit/client-sdk-flutter #166 切换黑屏；改默认 false |
| 纯依赖 SDK 自动重连，不做自维护 watchdog | livekit/client-sdk-unity #90 / #53 证伪 |
| 把 lifecycle 状态机塞进后端 BT | 违反 Sprint4 三层意识 + ECP 边界（背景锚点 §10） |
| 把 VideoTier 切换塞进 Reflex | VideoTier 属于 Intent；Reflex 不应做秒级以上的 negotiate |
| 蓝牙音频在 Sprint4 实现 | 标 OOS；`session/audio_route_policy` 仅留候选键，无 producer |
| `Texture2D.ReadPixels + EncodeToJPG` 截帧 | 阻塞主线程 50–200ms，IMPL_REF §陷阱 2 已禁用 |
| `Camera.Render() / targetTexture` 抓 ARCameraBackground 帧 | ARCore GPU OES 路径不经标准相机管线（ar-foundation rule §2 已禁用） |
| 动态创建副相机 + RenderTexture 抓帧（`result/01` §3.4 RTHandles 泄漏 UUM-40249） | URP 内存泄漏黑洞；用 Blit 共享 `_rt` 即可 |

---

## 6. 超纲附录（不进主表，仅记录）

- **VAD / push-to-talk 自建路径**：Sprint4 不实现；`brain_connected_black_video_20260425.md` 末尾已识别为 Sprint4 后路。
- **SAM2 / DINOv2 升档**：A10 上线后才需要双 Track 设计 A3.5；本轮不做。
- **WebRTC stats 细粒度采集**：`sprint4_livekit_stability_and_video_strategy.md` §5.2 提"高信号最小数据"；Phase 3 实现里仅做最小 ring buffer，不做长期存储。

---

## 7. 与背景锚点 / 审计 / 设计稿的对齐

| 当前文档约束 | 来源 | 本文是否冲突 |
|:--|:--|:--|
| ECP 不替代 Scheduler / BT | `sprint4_protocol_ecp_background_20260429.md` §3.1 / §10 | 不冲突：本文 §4.1 FSM 是 Unity 侧，不暴露给 BT |
| Unity 只看 ECP，不看 BT 节点 | 同上 | 不冲突：通过 `EcpState.app_lifecycle_state` 上报 |
| DSG L2-B 不接受实时帧 | 同上 | 不冲突：本文不新增 L2-B 写入 |
| Obsidian/Ref 不强制 UUID | 同上 | 与 lifecycle 无关 |
| `tick/last_ecp_ack` 暂为 dict 镜像；Phase 2 升级 | `sprint4_ecp_minimal_audit_20260429.md` A1 | 本文等 Phase 2 完成后再让 `EcpAck.frontend_state` 携带本文 §4.5 字段 |
| 不要在 producer 落地前注册 BB WRITE | 同上 B5 | 本文 §4 仍标候选；Phase 3 producer 实现后才升级 |
| `captureSnapshot` 响应当前是 Sprint3 dict | 同上 B4 | 本文 A2.9 / Spike S3 与 Phase 4 `snapshot-identify` 任务对齐 |

---

## 8. 变更日志

- 2026-04-29：创建。Sprint4 Phase 3 前置调研（Phase A 联网广搜 + Phase B 接口验证），独立于先前 `result/01` / `result/02`。产出已确认采用 / spike / 弃用 三段表，待用户筛选后带回 fork 实现 chat。
