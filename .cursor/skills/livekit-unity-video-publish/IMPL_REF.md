---
name: livekit-unity-video-publish
description: Use when working with the AR video pipeline — Unity publish to LiveKit, Gemini Live consume, Python on-demand frame capture, DSG Worker interface
---

# 视频流接缝：一流多采样 (One Stream, Multiple Sampling)

ParrotCarriers 的视频管线: Unity 推一条高质量视频轨到 LiveKit Server，多个消费者按各自节奏独立采样。本 skill 描述各接缝的真实代码实现和当前状态。

> **原则**: 只写有代码/验证支撑的事实。StabilityGate 联动 / 帧率自适应 / Tier 0 停推流 是 Opus 调研设计，无代码，不写在这里。

---

## 1. 数据流全景

```
Unity (ARVideoPublisher.cs)                    LiveKit Server (Castle)
1280x720@30fps H.264 1.5Mbps  ──推流──>  单一 LocalVideoTrack "ar-camera"
                                                        │
                              ┌─────────────────────────┼──────────────────────┐
                              │                          │                      │
                              ▼                          ▼                      ▼
                   Brain Agent                    identify_object          DSG Worker
                (video_input=True)              按需截帧 (B1-B2 基建)    独立订阅 VideoTrack
                Gemini Live 内部采样            RPC → Unity → base64     (未来 A10, Phase 3+)
                  云端黑盒, 不可取帧             同步返回给 tool            on_video_frame 接口
```

---

## 2. Unity 推流端（真实代码）

文件: `unity/ParrotDev/Assets/Scripts/LiveKit/ARVideoPublisher.cs`

**AR 路径** (`#if UNITY_AR_FOUNDATION`):
```csharp
// ARCameraManager.frameReceived 回调中:
Graphics.Blit(null, _rt, _arCameraBackground.material);
// _rt 是 RenderTexture(1280, 720, 0, RenderTextureFormat.ARGB32)
```

**Editor 回退** (`useWebcamFallback = true`):
```csharp
_webcam = new WebCamTexture(deviceName, width, height, targetFps);
// BlitWebcamLoop 协程持续 Graphics.Blit(_webcam, _rt)
```

**推流配置** (两路径共用同一 `_rt`):
```csharp
_videoSource = new TextureVideoSource(_rt);
_videoTrack = LocalVideoTrack.CreateVideoTrack("ar-camera", _videoSource, room);

var options = new TrackPublishOptions {
    VideoCodec = VideoCodec.H264,          // VP8 fallback on error
    VideoEncoding = new VideoEncoding {
        MaxBitrate = 1_500_000,
        MaxFramerate = 30,
    },
    Source = TrackSource.SourceCamera,
};
```

**当前状态**: 代码就绪，AR 真机端到端未验证（Editor + WebCam 回退可在 P1 条件下测）。

---

## 3. Brain Agent 消费端（真实代码）

文件: `src/parrot/brain/agent.py`

`AgentSession` 用 `video_input=True` 启动 → LiveKit Agents 框架自动将房间内的 VideoTrack 路由给 Gemini RealtimeModel。

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
    // AsyncGPUReadback.Request(_rt) — 不阻塞主线程
    // 回调中 EncodeToJPG(quality: 75)
    // 返回 JSON: { "snapshot_id": "<uuid>", "timestamp": <unix_ms>, "data": "<base64>" }
}
```

**传输方式选择**:
- RPC payload 上限 15KB — JPEG 75% at 1280x720 约 80-100KB，**超出上限**
- 方案 A: 压缩到 480x270 约 8-12KB — 可走 RPC response
- 方案 B: 使用 `LocalParticipant.SendFile()` / ByteStream API (LiveKit SDK v1.3.5+)
- 方案 C: 先发 RPC 触发，再用 DataStream 传图

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

## 陷阱

1. **RPC payload 上限 15KB** — 全尺寸 JPEG 超出，需降分辨率或用 ByteStream API
2. **AsyncGPUReadback 而非 ReadPixels** — ReadPixels 阻塞 Unity 主线程 50-200ms
3. **不走 DataChannel 传图** — Lossy DataChannel 上限约 1200B，Reliable 也不适合大 payload
4. **Gemini 黑盒** — `video_input=True` 后 Python 代码取不到 Gemini 看到的帧，必须走 B1-B2

---

## 快速导航

| 想了解… | 去哪里 |
|:--------|:------|
| 视频发布 Unity 代码 | `unity/ParrotDev/Assets/Scripts/LiveKit/ARVideoPublisher.cs` |
| Brain Agent 视频输入配置 | `src/parrot/brain/agent.py` |
| DSG Processor 接口 | `src/parrot/bus/processor_hook.py` |
| identify_object 视觉升级审计 | `.cursor/memory/architecture/audit_identify_object_no_screenshot_20260420.md` |
| 总架构图 (mermaid, "一流多采样"出处) | `docs/InfoCollections/Opus/10_architecture_diagram.md` |
| SemanticNode 类型 | `src/parrot/dsg/l2b_types.py` |
