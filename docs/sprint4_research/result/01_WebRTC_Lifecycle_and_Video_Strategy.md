> **用户反馈与筛选要求记录 (2026-04-27)**：
> "这个有点用... 音频设备切换 / Unity22.3 AR App 切屏幕 / LiveKit 断连接/假死等问题 等的问题处理防御最佳实践 （有一些的价值），以及一些视频流来源的收集方式策略... 找了不错的多种方案进行对照，算是有效的指导文件。"
> *筛选动作：保留移动端生命周期防御（切后台、网络切换）的具体策略对比，保留双桥墩视频流（Simulcast vs ReplaceTrack vs SetParameters）的工程对比。剔除泛泛而谈的理论。*

# 移动端 WebRTC 生命周期的防御性编程与正交视频数据流控制策略

## 1. 移动端底层系统挂起机制与 WebRTC 状态机的冲突本质

在搭载 Unity 2022.3 与 AR Foundation 的移动端（Android/iOS）环境中，WebRTC 的底层连接面临极高的脆弱性。

*   **操作系统的网络与硬件剥夺**：当 Unity 触发 `OnApplicationPause(true)` 时，iOS 的 App Nap 与 Android 的 Doze 模式会迅速冻结主线程，切断后台 Socket 访问。更致命的是，系统会强制收回摄像头和麦克风的硬件访问句柄。如果业务层未主动释放，底层 C++ 媒体引擎会抛出捕获失败异常，导致应用切回前台后画面黑屏或音频静音（假死）。
*   **ICE 断点局限**：WebRTC 依赖 ICE 发送 STUN 绑定请求保活。切后台时，保活请求超时，状态降级为 `disconnected` 或 `failed`。唤醒时，单靠网络层恢复已无法重建完整的音视频上下文（因为硬件句柄已失效）。

## 2. 移动端 WebRTC 生命周期防御策略的架构博弈

处理移动端网络切换与切后台行为的防御性编程策略主要分化为两大阵营：

### 策略 A：基于底层委托的被动重连机制（ICE Restart）
*   **机制**：业务层不干预，任由 SDK 触发内部重试（生成新 SDP，重新收集 Candidates）。
*   **优势（无损性）**：对于极短时的网络切换（如几秒内 WiFi 切 4G），ICE Restart 可在不销毁底层 `RTCPeerConnection` 的前提下恢复，保留现有 Track 对象，用户无感知。
*   **致命劣势**：在锁屏或切后台等长时间休眠中，若信令通道被关，ICE Restart 会彻底卡死。且由于系统强制剥夺了相机权限，旧的 LocalTrack 已成僵尸对象，重连后推送的也是黑屏。

### 策略 B：基于业务层干预的主动释放与重建策略 (Disconnect & Reconnect)
*   **机制**：捕获 `OnApplicationPause(true)` 瞬间，立即发送挂起信令，调用 `Room.Disconnect()`，彻底销毁媒体渲染组件并释放 LocalTrack。唤醒时，重新申请硬件授权并 `Room.Connect()`。
*   **优势（绝对可控）**：彻底消除系统强制回收资源与底层引擎状态机的死锁陷阱，唤醒成功率近 100%。
*   **劣势**：恢复耗时较长（1.5秒 - 3秒），会触发大规模连入/离线事件广播，增加信令服务器压力。

### 推荐实践：混合状态机防御架构 (Hybrid State Machine)
结合 Unity 限制，最佳实践是**时间窗口控制机制**：
1.  触发 `OnApplicationPause(true)` 时，记录时间戳，发送轻量级 RPC 标记 Suspended 状态，但不立即断开 WebRTC。
2.  若在防抖窗口（如 5 秒）内恢复，依赖底层 ICE Restart 处理短时跳跃。
3.  若超过阈值，无论 LiveKit 状态如何，强行绕过 SDK，立即执行 `Room.Disconnect()` 清理资源，随后发起全新的 `Room.Connect()` 冷启动。

## 3. 双桥墩架构下正交视频流与质量控制的工程演进

在我们的架构中，视频策略采用“双桥墩”模型：
*   **桥墩 1（连续低画质流核心）**：维持极低分辨率（如 160x90）、低帧率（10-15 FPS）、低码率（50-150kbps）的稳定流，专供 Gemini Live 消费。
*   **桥墩 2（旁路按需高清截帧流）**：独立通道，通过 RPC 触发，利用底层直接捕捉高清静态原画传回。

### 动态推流参数重协商：Simulcast vs ReplaceTrack vs SetParameters

当后端的 Tool 发送 RPC 指令要求改变视频质量时，前端有三种执行方式：

1.  **多路复用（Simulcast）—— 移动端的性能悖论**
    *   *机制*：硬件同时生成高、中、低多路流。
    *   *坑点*：在移动端同时维护多路硬件编码会导致 CPU 占用飙升、严重发热降频。中低端 Android 甚至会强制降级为软解。对于单一 LLM 消费者，极度浪费算力。**坚决摒弃**。
2.  **轨道替换（ReplaceTrack）—— 高效但有隐患**
    *   *机制*：本地修改相机参数生成新 Track，调用 `replaceTrack()` 无缝替换。
    *   *坑点*：替换瞬间需要重新进行关键帧协商（PLI/Keyframe 请求），若编码器初始化过慢，会导致远端画面出现几百毫秒到一秒的卡顿或黑屏。
3.  **参数直接修改（SetParameters）—— 最佳实践**
    *   *机制*：直接响应 RPC 指令调用 `RTCRtpSender.SetParameters`，实时调整 `maxBitrate` 和 `maxFramerate`。
    *   *优势*：在维持现有编解码器上下文的同时，通过协议层的拥塞控制以极致平滑的方式完成网络负载的收放。

### 致命陷阱规避：XRCpuImage 与多相机的显存泄漏
在实现桥墩 2（按需高清截图）时，若在 Unity URP 中动态创建副相机并输出到 RenderTexture，会触发底层的 RTHandles 内存泄漏黑洞（UUM-40249），导致 OOM 崩溃。
*   **规避指南**：绝对禁止动态创建额外相机。应利用 CommandBuffer 在主 AR 相机渲染管线的末端（如 `OnRenderImage`）执行内存拷贝（Blit）至托管的静态 RenderTexture。完成二进制流编码后，务必立即调用 `.Release()` 销毁显存绑定。

---

## 补遗（2026-04-29，Sprint4 Phase 3 前置调研）

> **输入来源**：本节是 task1 / task3 + Sprint3 真机实测（`docs/test/p2_5/`）+ 本轮 Phase A 联网广搜 + Phase B 接口验证（项目 skill）的结论合并。
> **完整产物**：`docs/sprint4_research/result/05_lifecycle_and_defensive_design.md`（包含 §A1/A2/A3 对比表 + Phase B 三问三答 + spike 清单 + 弃用清单 + 候选 BB 键）。
> **本节作用**：在不覆盖原文情况下，补正几条在我们锁定版本（Unity 2022.3 LTS + AR Foundation 5.1.5 + LiveKit Unity SDK `2a7c57d7bcad`）上**和原文偏差** / **原文未覆盖**的关键点。

### 1. 与原文 §2 防御策略的对齐与偏差

原文推荐"混合状态机"（5s 防抖 → 强切）整体方向**仍正确**；以下是基于在我们 SDK 版本上的实测/社区证据补正：

- **原文假设 SDK 事件可信**：实测不可信。`livekit/client-sdk-unity` Issue #90 表明 iOS 飞行模式下 `Disconnected` / `Reconnecting` event 可能 30s+ 才触发或完全不触发；`Disconnected` event 也不携带 `DisconnectReason`（Issue #53，open since 2024-08）。**Phase 3 必须自维护 connectivity watchdog**（搭车 ECP `EcpState` 上行通道每 N 秒上报，5s/30s 双阈值），不能纯依赖 SDK 事件。
- **30s ICE 残留 / identity 抢占**（Sprint3 已踩，原文未提）：必须做 graceful shutdown：`UnpublishTrack → Room.Disconnect → 等 Disconnected event（自维护 5s 超时） → Room.Dispose() → cool-down 5s → 新 Connect`。`livekit/client-sdk-unity` commit `434009b` 已修 `RpcMethodInvocationReceived` handler leak，但 reconnect 周期里仍有 race（参考 swift SDK Issue #757 disconnecting/reconnect 状态修复）。
- **阈值经验**：原文给"5s 防抖"是数量级合理但**不是定值**。Phase 3 spike 范围：< 5s 完全不动让 SDK 处理 / 5–30s 上报 `degraded` 不强切 / > 30s 强切。

### 2. 与原文 §3 数据流策略的偏差

原文按 Web 通用层面给的 simulcast / replaceTrack / setParameters 三方案对比，在 LiveKit Unity SDK 上**只剩一个方案能用**：

| 原文方案 | Unity SDK 实测 | 处置 |
|:--|:--|:--|
| Simulcast | API 存在（`TrackPublishOptions.Simulcast`），但单消费者（Gemini Live）+ 移动端硬编多路 → CPU 飙升；livekit/client-sdk-flutter #166 切换黑屏 | 本节**弃用**；Phase 3 默认 `Simulcast=false` |
| ReplaceTrack | LiveKit Unity SDK 暴露 `UnpublishTrack` + `PublishTrack` 两步组合，等价于 ReplaceTrack；**livekit/livekit Issue #854** 警告：unpublish + 立即 republish 会 server timeout（abandoned publish），**5 分钟后仍无法 republish** | 必须加 cool-down ≥ 3s + 等 Unpublish 完成事件再 PublishTrack |
| SetParameters | LiveKit Unity SDK FFI bridge **不暴露** `RTCRtpSender.SetParameters`；只有 publish 时配置 `VideoEncoding.MaxBitrate/MaxFramerate`，没有运行时调节 | **明确弃用** |

**结论**：在我们锁定 SDK 版本上，Sprint4 VideoTier 切换**只能走** unpublish→republish + cool-down 3s + 等 First frame，且 Brain 的 `set_video_tier` 必须保持同步 Intent 模式（Sprint3 brain_connected_black_video 已 fix）。

### 3. 原文未覆盖：AR Foundation / ARCore 后台行为

**ARCore 主动 blank OES texture**（Unity issuetracker `arcore-black-screen-on-session-pause`，AR Foundation 标 wontfix；arfoundation-samples #592）—— pause 时 `_arCameraBackground.material` 变黑，原文 §1 假设的"ICE 保活时仍有最后一帧"在 ARCore 上**不成立**。Phase 3 必须：

- 切前台后等 `ARSession.state == SessionTracking` + 一次 `frameReceived` 实际触发再恢复 publish；
- 后台期间**不**继续推黑帧（避免 Gemini Live 误以为画面没变）；可选：自存最后有效帧 `_lastValidRt` 仅做本地 UI 显示。

**ARCore pause/resume 高频崩溃**（google-ar/arcore-android-sdk #1736，2025-09，1.47/1.50 复现）：高频 `ArSession_pause/resume` 会触发 ARCore 内部 crash；多次后 `ArSession_update` 返回 `AR_ERROR_FATAL`（#1309，重建 session 也救不回）。

> Phase 3 落地约束：用户切前后摄 / 重启 AR Session 必须**限频 1 次 / 2 秒**；连续触发应给用户确认对话框。

### 4. 原文未覆盖：截帧路径在我们版本上的可用性

原文 §3.4 警告 RTHandles 泄漏（仍成立）。但**正向方案**在 5.1.5 上有两条干净路径，原文未明示：

| 路径 | API | 优势 | 取舍 |
|:--|:--|:--|:--|
| `XRCpuImage.ConvertAsync` | `ARCameraManager.TryAcquireLatestCpuImage(out)` + `XRCpuImage.ConvertAsync(ConversionParams, callback)`（5.1.5 docs） | 直接拿 ARCore 原始 buffer，不经 GPU pipeline；最低延迟 | `XRCpuImage` / `AsyncConversion` 都必显式 Dispose；onComplete 回调里 NativeArray 仅 invocation 内有效，必须 CopyTo |
| `AsyncGPUReadback.Request(_rt)` | `Rendering.AsyncGPUReadback`；`SystemInfo.supportsAsyncGPUReadback` 需查询 | 复用 publish 用的 `_rt`，与现有管线零冲突 | 几帧延迟；老 Android 可能 fallback 同步 |

> Phase 3 spike S4：在 Pixel 6a / Samsung 中端实测两路径 480x270 JPEG 端到端延迟 + 主线程占用，选胜者。

### 5. 原文未覆盖：> 15KB JPEG 必走 ByteStream

LiveKit RPC payload 上限 ~15KB（IMPL_REF §陷阱 1）。Unity SDK 已暴露 `RegisterByteStreamHandler` / `SendFile`（client-sdk-unity SKILL §8）。

> Phase 3 spike S3：50KB JPEG 在移动 4G/WiFi 上端到端 RTT P50 < 500ms / P95 < 2s / 失败率 < 1%；超出则 captureSnapshot 必须降到 480x270 走 RPC。

### 6. 与 Sprint4 ECP / 三层意识 / 测试束隔离的边界对齐

下面边界**不允许**在 Phase 3 落地里被本补遗章节带偏：

- 本补遗的 lifecycle 状态机是 Unity 客户端 FSM，**不暴露给后端 BT**；后端通过 `EcpState.app_lifecycle_state` + `connection.health.changed` 事件感知。详见 `sprint4_protocol_ecp_background_20260429.md` §10。
- VideoTier 切换属于 Intent，禁止塞进 Reflex 做毫秒级反应（背景锚点 §10）。
- DSG L2-B 工作记忆不接受实时帧；本补遗不新增 L2-B 写入路径。
- 蓝牙音频先标 `unsupported_or_experimental`；候选 BB 键 `session/audio_route_policy` 保留但 Sprint4 不写 producer（`sprint4_ecp_minimal_audit_20260429.md` B5）。

### 7. Phase 3 实现入场前的最小复核清单

- [ ] 读 `result/05_lifecycle_and_defensive_design.md` §5 三段式（采用 / spike / 弃用）。
- [ ] 读 `sprint4_ecp_minimal_audit_20260429.md` §"不允许误读" + "Phase 2 入场清单"。
- [ ] 读 `sprint4_protocol_v2_ecp.md` §9（Lifecycle / ConnectionHealth / AudioRoutePolicy）。
- [ ] 落地任何新 BB 键之前先实现 producer，避免重蹈 `global/soul_constraints` 反模式（审计 B5）。
- [ ] 任何对 IMPL_REF.md 的修改走 patch 提案（见 `result/05` + 本节后续 IMPL_REF patch 清单），不直接改源文件。