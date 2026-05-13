---
name: livekit-unity-video-publish
description: Use when working with the AR video pipeline — Unity publish to LiveKit, Gemini Live consume, Python on-demand frame capture, DSG Worker interface, captureSnapshot RPC vs ByteStream, AR camera blit / RenderTexture / TextureVideoSource, Simulcast / VideoTier 推流配置, 黑帧 / stale 帧 / 首帧门
---

# 视频流接缝：一流多采样 + AR 版本锁

ParrotCarriers 的视频管线: Unity 推一条可门控的共享主视频轨到 LiveKit Server，多个消费者按各自节奏独立采样。本实现参考描述真实代码、当前状态、AR 版本锁和 Sprint3/4 继续完善的治理边界。

> **原则**: 区分“已实现代码”“已验证现象”“Sprint4 设计”。不要把 HUD 的 `Video pub: yes` 当成真实画面健康；必须同时看首帧、新鲜帧、AR profile、tier ack。
>
> **配套 skill**：`.cursor/skills/livekit-unity-lifecycle/IMPL_REF.md` —— Room 重连 / 切后台 / graceful shutdown / connection_health / ARCore 后台 blank / setVideoTier 副作用 都搬到那边；本 skill 只负责**数据流主题**（推流 / 多采样 / 截帧 / 黑帧门）。本 skill 与 lifecycle skill 互相不重叠，遇到冲突以本 skill 为数据流真源、lifecycle skill 为 lifecycle 真源。
>
> **本 skill 边界**：仅描述 Unity → LiveKit Server → 多消费者的数据流接缝。**不**承载 Room 生命周期、连接健康、关闭流程；**不**承载 AppLifecycleState FSM；**不**承载 audio route policy。
>
> **最后验证**: 2026-04-29 — Sprint4 Phase 3 前置调研产物（`docs/sprint4_research/result/05_lifecycle_and_defensive_design.md`）+ Patch 1/2/5/6/8/10 合入。在此之前最近一次真机验证 2026-04-25 P2.5 ECS 测试（`docs/test/p2_5/brain_connected_black_video_20260425.md`），AR 路径未进入 Android 构建已修复，待真机回归。

---

## 1. 数据流全景

```
Unity (ARVideoPublisher.cs)                    LiveKit Server (Castle)
AR/WebCam → RenderTexture → 可门控主视频轨 ──推流──>  LocalVideoTrack "ar-camera"
                                                        │
                              ┌─────────────────────────┼──────────────────────┐
                              │                          │                      │
                              ▼                          ▼                      ▼
                   Brain Agent                    identify_object          DSG Worker
                (video_input=True)              按需截帧 (B1-B2 基建)    独立订阅 VideoTrack
                Gemini Live 内部采样            RPC → Unity → base64     (未来 A10, Phase 3+)
                低延迟优先, 不取帧              不依赖 Gemini 黑盒帧       on_video_frame 接口
```

---

## 2. Unity 推流端（真实代码）

文件: `unity/ParrotDev/Assets/Scripts/LiveKit/ARVideoPublisher.cs`

### AR 版本锁 / 编译宏

当前项目锁定 Unity 2022.3 LTS + AR Foundation/ARCore/ARKit 5.1.x。联网核对后保留此组合：Unity LTS 适合生产锁版和稳定修复；AR Foundation 5.1 官方说明本体只提供接口，目标平台必须安装并启用 provider plug-in；Android 需 Google ARCore XR Plug-in。这个锁定是 Sprint3/4 收口策略，不是永久版本承诺。

`UNITY_AR_FOUNDATION` 不是 Unity 自动宏。当前项目无 asmdef，使用 `unity/ParrotDev/Assets/csc.rsp` 显式定义：

```text
-define:UNITY_AR_FOUNDATION
```

短期这是正确修复：Unity 官方自定义 scripting symbols 文档说明 `Assets/csc.rsp` 会在脚本编译前生效，适合无 asmdef / batch / CI 场景。长期若 AR 工作区拆 assembly，应迁移为 asmdef `versionDefines`，例如 package `com.unity.xr.arfoundation` expression `[5.1,5.2)` define `UNITY_AR_FOUNDATION`。

**AR 路径** (`#if UNITY_AR_FOUNDATION`):
```csharp
// ARCameraManager.frameReceived 回调中:
Graphics.Blit(null, _rt, _arCameraBackground.material);
// _rt 是 RenderTexture(1280, 720, 0, RenderTextureFormat.ARGB32)
```

**Editor 回退** (`useWebcamFallback = true`, 已在 P2 测试 E2E 通):
```csharp
// 1. 列出并选择设备（新：避开虚拟摄像头）
string deviceName = SelectWebcamDevice(WebCamTexture.devices);
// preferredDeviceName 命中 > 首个非虚拟 > devices[0] 兜底
// 虚拟关键字: obs / virtual / xsplit / manycam / snap camera / droidcam / mmhmm / splitcam

_webcam = new WebCamTexture(deviceName, width, height, targetFps);
_webcam.Play();

// 2. 等到 didUpdateThisFrame (首帧有效信号)
while (!_webcam.didUpdateThisFrame && timeout > 0f) { ... yield return null; }

// 3. 【P2 关键修复】首帧预热 Blit — 防止 LiveKit 推黑帧
//    原 bug: SetupWebcamFallback 返回后立即 PublishTrack，
//    但 BlitWebcamLoop 协程还没跑，_rt 是黑的 ARGB32，
//    Gemini 低采样率下只看到黑 → 幻觉 "画面是黑的"。
int blitted = 0;
while (blitted < webcamWarmupFrames && warmupTimeout > 0f) {
    if (_webcam.didUpdateThisFrame) {
        Graphics.Blit(_webcam, _rt);
        blitted++;
    }
    yield return null;
}
// 4. 启动持续 Blit 循环
_webcamBlit = StartCoroutine(BlitWebcamLoop());
```

**推流配置** (两路径共用同一 `_rt`，按当前 tier 选择码率/FPS):
```csharp
// PublishTrack 前必做 IsConnected guard — 防止 Stop 后回调 NRE
if (!RoomManager.Instance.IsConnected) yield break;

_videoSource = new TextureVideoSource(_rt);
_videoTrack = LocalVideoTrack.CreateVideoTrack("ar-camera", _videoSource, room);

var options = new TrackPublishOptions {
    VideoCodec = VideoCodec.H264,          // VP8 fallback on error
    VideoEncoding = new VideoEncoding {
        MaxBitrate = (ulong)initBitrate,   // GeminiOnly 默认 300kbps
        MaxFramerate = initFps,            // GeminiOnly 默认 15fps
    },
    Source = TrackSource.SourceCamera,     // ← 必填，否则 Brain 按 SOURCE_UNKNOWN detach
    Simulcast = false,                     // ← Sprint4 默认 false（单消费者拓扑）；见陷阱 #15
};
```

`VIDEO_FULL` / `VIDEO_BURST` 不是常态默认。Sprint4 默认应优先 Gemini Live 低延迟体验，只有 A10/识别任务需要时短时升档。

**setVideoTier 切换路径**：FFI bridge **不暴露** `RTCRtpSender.SetParameters`，运行时调码率/帧率**无 API**。VideoTier 切换只能：`UnpublishTrack` → cool-down `T_TIER_COOLDOWN` → `PublishTrack(new options)` → 等 First frame → 回 ECP `applied`。完整流程 + 黑帧时长验收（spike S5）见 `livekit-unity-lifecycle/IMPL_REF.md` §6 + §10 可调参数表。

**音频推流对偶**（`MicrophonePublisher.cs`，同样必填 Source）:
```csharp
var options = new TrackPublishOptions {
    Source = TrackSource.SourceMicrophone,    // ← P2 修复前漏这行
    AudioEncoding = new AudioEncoding { MaxBitrate = 64_000 },    // Opus 64kbps 语音基线
};
```

**当前状态**:

- Editor + WebCam 路径 2026-04-21 P2 测试 E2E 通（Gemini 说对白色鼠标）。
- Android P2.5 发现 `UNITY_AR_FOUNDATION off`，AR 路径未进入构建；已通过 `csc.rsp` 修复。
- 真机 AR 路径仍需重新打包验证：HUD 应显示 AR Foundation active，`SceneProfileManager` 应选 `AR_HANDHELD`，`ARVideoPublisher` 应显示 `source=AR` 且 fresh frame age 小于 stale 阈值。

---

## 3. Brain Agent 消费端（真实代码）

文件: `src/parrot/brain/agent.py`

`AgentSession` 用 `video_input=True` 启动 → LiveKit Agents 框架自动将房间内的 VideoTrack 路由给 Gemini RealtimeModel。

**硬依赖**（P2 踩坑）: `livekit-agents[images]` extra **必装**，否则 `_forward_video_task` 每帧抛 `ImportError` → Gemini 一帧都看不到，症状是"鹦鹉说画面是黑的"或幻觉编造。
```bash
pip install 'livekit-agents[images]'    # 拉 Pillow
```
需同步写进 `requirements.txt` / `pyproject.toml`。

**Gemini 内部采样行为**（来自 Gemini API 文档，非代码控制）:
- 说话时约 1 fps，静默时约 0.3 fps
- **我们无法取帧、无法留存、无法复用** — 这是云端黑盒
- Gemini 调用 `identify_object` 时只能传文字描述，**不能传图**

**关键限制**: Gemini 能"看"，但 Python 代码层拿不到那一帧的图片数据。需要层 2 基建才能让 tool 代码做图像比对/存储。

---

## 4. Python 按需截帧（B1-B2 基建，待实现）

当 `identify_object` 等 tool 需要实际图片数据时，通过 RPC 向 Unity 请求截帧。

### B1: Unity 端 `captureSnapshot` RPC

在 `ARVideoPublisher.cs` 或新建 `SnapshotService.cs` 中注册:

```csharp
room.LocalParticipant.RegisterRpcMethod("captureSnapshot", HandleCaptureSnapshot);

private async Task<string> HandleCaptureSnapshot(RpcInvocationData data)
{
    // 见下方两条候选路径；不要在主线程 ReadPixels（陷阱 #2）
    // 返回 JSON: { "snapshot_id": "<uuid>", "timestamp": <unix_ms>, "data": "<base64>" } 或 ByteStream descriptor
}
```

**两条候选采集路径**（spike S4 选定主路径）：

| 路径 | 来源 | 何时用 | 何时不可用 |
|:--|:--|:--|:--|
| **A. `XRCpuImage.ConvertAsync`** | `ARCameraManager.TryAcquireLatestCpuImage` | AR 路径，需要相机原始 YUV / 高质量 JPEG，且非阻塞主线程 | WebCam fallback / XR Simulation 不可用 |
| **B. `AsyncGPUReadback.Request(_rt)`** | 共享 `_rt` RenderTexture | 任何路径都通用（AR / WebCam / Simulation），与现有推流管线复用 `_rt` | GPU readback 1–2 帧延迟 |

**Sprint4 实现建议**：
- AR 路径优先 A（`ARCameraManager.TryAcquireLatestCpuImage` + `ConvertAsync`，arfoundation-samples `CpuImageSample.cs` 实现模式可直抄）；
- WebCam fallback / XR Simulation 路径用 B；
- 在 `ARVideoPublisher` 上加薄抽象 `IFrameCapturer`，两路径都实现，运行时按 `SceneProfile` 选择；
- **绝不**在 RPC handler 里同步 `Texture2D.ReadPixels`（主线程 50–200ms 阻塞 → 心跳超时 → watchdog 误判 → 雪崩）。

**传输方式选择**（基于 RPC ~15KB 上限）：

| 大小 | 路径 | 备注 |
|:--|:--|:--|
| ≤ 15KB（480x270 JPEG q75 约 8-12KB） | RPC response | Sprint3 已用此路径，单次 RTT |
| > 15KB（≥ 50KB 高质量 JPEG / 多张） | `LocalParticipant.SendFile()` / Room.RegisterByteStreamHandler / SendStreamReader | LiveKit Unity SDK 已支持；Phase 3 spike S3 测 RTT P95，验收 P50<500ms / P95<2s / 失败<1% |

阈值参数（`BYTESTREAM_RPC_THRESHOLD_BYTES` 默认 15360）见 `livekit-unity-lifecycle/IMPL_REF.md` §10 可调参数表。

**当前状态**: 未实现，是 `identify_object` 视觉升级的前置件。

### B2: Python 端 `capture_current_frame()`

新建 `src/parrot/brain/vision/snapshot.py`:

```python
async def capture_current_frame() -> SnapshotResult | None:
    # 1. perform_rpc("captureSnapshot", destination=unity_identity)
    # 2. 超时 < 2s，失败返回 None
    # 3. 解码 base64 → bytes
    # 返回 SnapshotResult(snapshot_id, timestamp_ms, image_bytes)
```

Python 端需要知道 Unity 参与者的 identity（`_rpc_bridge.py` 中已有查找 `unity-*` 的逻辑）。

### 时间轴对齐（B2 的附属要求）

截帧时返回的 `timestamp` (Unix ms) 可与 Python 侧缓存的 `ar_telemetry` 帧通过时间差匹配（200ms 容差），将快照关联到当时的 tracking_state。这是 DSG 模块（sighting 记录、SemanticNode 更新）需要的上下文。

```python
# 示例: 找到最接近截帧时刻的 ar_telemetry
best = min(telemetry_buffer, key=lambda t: abs(t["timestamp"] - snapshot_ts_ms), default=None)
```

**当前状态**: 设计，无代码。

---

## 5. DSG Worker 连续帧分析（接口预留，Phase 3+）

文件: `src/parrot/bus/processor_hook.py`

`BaseProcessor` 抽象接口已预留 `on_video_frame` / `on_telemetry` / `get_scene_snapshot`。DSG Worker 实现此接口后可作为独立 LiveKit 参与者订阅 VideoTrack。

```python
class DSGProcessor(BaseProcessor):  # Phase 3+, 需要 A10 GPU
    async def on_video_frame(self, frame: Any) -> None:
        # SAM2 + DINOv2 + YOLO-World 处理
        ...
    async def on_telemetry(self, data: dict) -> None:
        # ARCore 遥测驱动 StabilityGate
        ...
```

**当前状态**: 接口已定义，DSGProcessor 未实现，Phase 2 不做。参考 SVA `add_frame_handler(fps=X)` 模式。

---

## 6. 状态监控与门控（部分已实现，Sprint4 继续完善）

设计路线（见 `Test/p2/connectivity_report_p2.md` §6.3-6.4 与 `docs/test/p2_5/brain_connected_black_video_20260425.md`）：

- **已实现：产地新鲜帧门（Unity 侧）**: `ARVideoPublisher.HasFreshFrame` 根据 `ProducedFrameCount` 和 `LastFrameAgeSeconds` 判断；`VideoStateReporter` 将 stale 帧上报为 `static_frame`，恢复时上报 `ok`。
- **已实现：HUD / 自检不再假 OK**: 发布轨存在但帧 stale 时显示 `Video pub: stale(... age=Xs)`，自检输出 WARN。
- **待实现：图像质量门**: 亮度方差低于阈值 N 秒 / 模糊 / 遮挡 → 发 RPC `onVideoDegraded(reason=dark_frame|blur_frame|obstructed)` 到 Brain。
- **消费端门控（Python 侧）**: identify_object 截帧、DSG Worker 连续帧自查糊帧/黑帧 → 跳过
- **已实现：Gemini 状态感知入口**: Brain 收到 `onVideoDegraded` → `brain.vision.state` 写 `session/visual_reason` / `session/visual_state` → Context Injector 注入视觉状态约束。
- **可直接订阅的 LiveKit 事件**（无需 Unity 自实现）: `TrackMuted` / `TrackUnmuted` / `ParticipantDisconnected` / simulcast 切层

**当前状态**: 新鲜帧门和状态上报已落地；亮度/模糊/遮挡检测、consumer-side frame QA、正式 app 启动门仍是 Sprint4 工作。

---

## 7. 平台后台采集行为（进 AR 工作区排查）

| 平台 | 麦克风 | 摄像头 | 要点 |
|:---|:---|:---|:---|
| iOS | ✓ (需 `UIBackgroundModes = audio`) | ✗ 被系统冻结 | 后台时 `ARCameraManager.frameReceived` 停 → _rt 不再更新 → LiveKit 持续推最后一帧 |
| Android | ✓ | ✓（受 ARCore 主动 blank 影响，见下方） | 需 Foreground Service（`CAMERA` 类型）+ 持久通知 |
| Unity Editor | ✓ | ✓ | Editor 失焦默认暂停，需 `Run In Background = true` |

**iOS 后果尤其坑**：Gemini 会以为画面一直没变，出现"鹦鹉在描述半小时前的东西"。后台/前台过渡的处置策略见 `livekit-unity-lifecycle/IMPL_REF.md` §5（不在本 skill 重复）。

**Android ARCore 黑屏额外坑**（Patch 5 调研 2026-04-29）：
- ARCore 在 pause 时**主动**把外部 OES texture blank 掉（Unity issuetracker `arcore-black-screen-on-session-pause` 已 wontfix；arfoundation-samples #592 same）。`_arCameraBackground.material` 在 pause / `ARSession.state != SessionTracking` 时**不可信**，Blit 出黑帧。
- 数据流侧的处置：`OnApplicationPause(true)` 暂停 Blit（但不 unpublish track）；`OnApplicationPause(false)` 后等 `ARSession.state == SessionTracking` + 一次新 `frameReceived` 实际触发再恢复 Blit。完整 lifecycle 联动见 lifecycle skill §5。
- 高频 ARSession pause/resume 会触发 ARCore 内部 crash（google-ar/arcore-android-sdk #1736 / #1309）；前后摄切换 / 重启 AR 限频 ≥ 2s（参数 `T_AR_SESSION_TOGGLE_MIN`）。

---

## 陷阱

1. **RPC payload 上限 15KB** — 全尺寸 JPEG 超出，需降分辨率或用 ByteStream / SendFile API
2. **AsyncGPUReadback 而非 ReadPixels** — ReadPixels 阻塞 Unity 主线程 50-200ms
3. **大于 15KB 的图片必须走 ByteStream** — `LocalParticipant.SendFile()` / `Room.RegisterByteStreamHandler` / `SendStreamReader` 在 LiveKit Unity SDK 已暴露；不要尝试 RPC 分片或 DataChannel 拼包（Lossy DataChannel 上限约 1200B，Reliable 也不适合大 payload）。阈值参数 `BYTESTREAM_RPC_THRESHOLD_BYTES` 见 lifecycle skill §10
4. **Gemini 黑盒** — `video_input=True` 后 Python 代码取不到 Gemini 看到的帧，必须走 B1-B2
5. **`TrackPublishOptions.Source` 必填**（P2 踩坑）— 漏填 → `SOURCE_UNKNOWN` → Brain 白名单 detach → 该轨完全看不到/听不到。音视频两路都有这个坑
6. **Webcam fallback 首帧黑**（P2 踩坑）— 推流前必须 warmup Blit 有效帧到 `_rt`；纯等 `didUpdateThisFrame` 不够
7. **Windows `WebCamTexture.devices[0]` 常是虚拟摄像头**（P2 踩坑）— 用启发式过滤 `obs/virtual/droidcam/...`，并打印完整设备列表方便诊断
8. **`livekit-agents[images]` extra 必装** — 缺 Pillow 则 Gemini 一帧都看不到，栈底 ImportError（P2 踩坑）
9. **反复 Play/Stop 会触发 identity 抢占 + NRE**（P2 踩坑）— LiveKit grace period 约 20-30s；调试时 Stop 后等够时间再复测；PublishTrack 前加 `IsConnected` guard。**完整 graceful shutdown 流程**（unpublish→Disconnect→等事件→Dispose→cool-down）搬到 `livekit-unity-lifecycle/IMPL_REF.md` §2，本 skill 不再展开
10. **`UNITY_AR_FOUNDATION` 不会自动出现**（P2.5 踩坑）— 包已安装但宏未定义时，真机 AR 路径会被编译掉，HUD 显示 `AR: UNITY_AR_FOUNDATION off`
11. **Video pub yes 不是画面健康**（P2.5 踩坑）— LiveKit track 可存在但 `_rt` 长时间不更新；必须看 `HasFreshFrame` / `lastAge`
12. **只安装 provider 不等于启用 provider** — AR Foundation 官方说明目标平台必须有 provider plug-in；Unity 还需要在 XR Plug-in Management 为 Android/iOS 启用对应 loader
13. **ARCore 后台主动 blank OES 纹理**（Sprint4 调研 2026-04-29）— 详见 §7 Android 部分；过渡期 Blit 必须暂停，否则会推黑帧给 Gemini 污染 turn
14. **`RTCRtpSender.SetParameters` 在 LiveKit Unity SDK 不暴露**（Sprint4 调研 2026-04-29）— FFI bridge 没透传；运行时调 maxBitrate/maxFramerate **无 API**。VideoTier 切换只能 `UnpublishTrack`+`PublishTrack`（见 §2 setVideoTier 切换路径），并加 cool-down `T_TIER_COOLDOWN`（≥ 3s）防 livekit/livekit #854 abandoned publish
15. **Simulcast 默认 true 但单消费者拓扑不需要**（Sprint4 调研 2026-04-29）— `TrackPublishOptions.Simulcast=true` 在移动端上多路硬编 → CPU 飙升 + 发热降频；client-sdk-flutter #166 揭示 simulcast on 时切层会黑屏。Sprint4 默认 `Simulcast=false`，A10 多档订阅时再单独 spike

---

## 快速导航

| 想了解… | 去哪里 |
|:--------|:------|
| 视频发布 Unity 代码 | `unity/ParrotDev/Assets/Scripts/LiveKit/ARVideoPublisher.cs`（Sprint4 起搬迁到 `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/`） |
| 麦克风发布 Unity 代码 | `unity/ParrotDev/Assets/Scripts/LiveKit/MicrophonePublisher.cs` |
| Brain Agent 视频输入配置 | `src/parrot/brain/agent.py` |
| DSG Processor 接口 | `src/parrot/bus/processor_hook.py` |
| identify_object 视觉升级审计 | `.cursor/memory/architecture/audit_identify_object_no_screenshot_20260420.md` |
| Brain 黑屏/假 ON 复盘 | `docs/test/p2_5/brain_connected_black_video_20260425.md` |
| AR 版本锁 / 编译宏规则 | `.cursor/rules/ar-foundation.mdc` |
| P2 连通性测试完整踩坑记录 | `Test/p2/connectivity_report_p2.md` |
| 总架构图 (mermaid, "一流多采样"出处) | `docs/InfoCollections/Opus/10_architecture_diagram.md` |
| SemanticNode 类型 | `src/parrot/dsg/l2b_types.py` |
| **Lifecycle / 防御性 / Graceful shutdown / 重连 / VideoTier 切换 cool-down** | `.cursor/skills/livekit-unity-lifecycle/IMPL_REF.md` |
| **可调参数表（统一一处）** | `livekit-unity-lifecycle/IMPL_REF.md` §10 |
| **Sprint4 Phase 3 决策索引** | `docs/sprint4_research/result/INDEX_for_phase3.md` |
| **Phase 3 厚稿（lifecycle 决策原因）** | `docs/sprint4_research/result/05_lifecycle_and_defensive_design.md` |

