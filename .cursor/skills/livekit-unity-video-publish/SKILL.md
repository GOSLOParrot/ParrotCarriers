---
name: livekit-unity-video-publish
description: 一流多采样接缝 — Unity 推流 + LiveKit 分发 + Brain/DSG/identify_object 三路消费端的真实接缝位置
---

# 视频流接缝：一流多采样 (One Stream, Multiple Sampling)

> **适用场景**: 新增视频消费者、调试视频采样、理解 identify_object 缺截图问题时查阅。
>
> 关联审计: `.cursor/memory/architecture/audit_identify_object_no_screenshot_20260420.md`
>
> 实现细节草稿: 本目录 `IMPL_REF.md`

---

## 一、数据流全景

```
Unity (ARVideoPublisher.cs)                     LiveKit Server (Castle)            Python 消费者
1280x720@30fps H.264 1.5Mbps  ──WebRTC推流──>  LocalVideoTrack "ar-camera"  ──订阅──>  多路
                                                                                    │
                                          ┌─────────────────────┬──────────────────┤
                                          │                     │                  │
                                   Brain Agent          DSG Worker          identify_object
                                  video_input=True     VideoStream(track)   captureSnapshot
                                  Gemini Live 自动订阅   A10, Phase 3+        RPC 按需截帧
                                  内部 ~1fps 采样        add_frame_handler    Phase 2.5
                                  云端黑盒，不可取帧      fps=X 独立循环       EncodeToJPG
```

**核心原则**: 推流端 (Unity) 只负责"稳定高质量单源"，不为任何消费者做采样决策。新增消费者不改 Unity 代码。

---

## 二、Unity 推流端

**文件**: `unity/ParrotDev/Assets/Scripts/LiveKit/ARVideoPublisher.cs`

**验证状态**: 代码就绪，真机 AR 端到端未验证（Editor Webcam 回退已可用）

### 两条推流路径

| 路径 | 触发条件 | 帧来源 |
|:-----|:---------|:-------|
| AR 路径 | `#if UNITY_AR_FOUNDATION` + `ARCameraManager` + `ARCameraBackground` 均存在 | `ARCameraBackground.material` → `Graphics.Blit(null, rt, mat)` in `frameReceived` 回调 |
| Editor 回退 | AR 不可用 且 `useWebcamFallback=true` | `WebCamTexture` → `Graphics.Blit(webcam, rt)` Coroutine 循环 |

两条路径共享一个 `RenderTexture` (1280×720, ARGB32) 作为 `TextureVideoSource` 输入。

### 推流参数（已固化代码）

```csharp
// ARVideoPublisher.cs — SetupAndPublish()
var options = new TrackPublishOptions
{
    VideoCodec = VideoCodec.H264,          // H.264 优先
    VideoEncoding = new VideoEncoding
    {
        MaxBitrate = 1_500_000,            // 1.5 Mbps
        MaxFramerate = 30,
    },
    Source = TrackSource.SourceCamera,
};
// H.264 publish 失败时自动重试 VP8 fallback（见代码 ~L108-118）
```

### 推流端不做的事

- 不做采样决策（各消费者自订阅）
- 不做帧率自适应 / StabilityGate / Tier 停推流（均为 Opus 调研，无代码）
- `Graphics.Blit` 必须在 `frameReceived` 回调内执行（ARVideoPublisher.cs 已正确实现）

---

## 三、Brain Agent 消费端

**文件**: `src/parrot/brain/agent.py` 第 131 行

**验证状态**: `video_input=True` 已配置，Gemini Live 视频接入已实现

### 接入点

```python
# agent.py — 创建 AgentSession 时
session = AgentSession(
    ...
    room_options=room_io.RoomOptions(video_input=True),   # ← 这一行开启视频订阅
)
```

### Gemini 内部采样行为

- Gemini Realtime API 自动订阅 LiveKit Room 中的视频轨（无需额外代码）
- 采样节奏由 Gemini 云端决定（约 1fps 说话中 / ~0.3fps 静默）
- **无法从 Gemini 取到它"看的那一帧"** — 如需原始图像做比对或存档，必须 Unity 端另行截帧

### 不需要做的事

- 不需要在 Python 层显式抽帧或用 `VideoStream(track)`
- 不需要为 Gemini 设置采样频率（云端自动）

---

## 四、DSG Worker 消费端（未来 A10，接口预留）

**状态**: ⚠️ 接口预留，Phase 3+ 实现，需要 A10 GPU

### 预留接口位置

```python
# src/parrot/bus/processor_hook.py
class BaseProcessor:
    async def on_video_frame(self, frame) -> None:
        """子类覆写：连续帧分析（SAM2/DINOv2 等）。"""
        pass
```

### 未来实现路径（参考 SVA Processor 模式）

```python
# 未来 DSG Worker 订阅视频轨（livekit-agents VideoStream API）
from livekit.agents import VideoStream

async def process_video(track: RemoteVideoTrack):
    async with VideoStream(track) as stream:
        async for frame in stream:
            await processor.on_video_frame(frame.frame)
```

SVA 的 `add_frame_handler(fps=X)` 按帧率限速模式可在此复用（见 sva-vision-agents skill）。

Bus Worker 注册流程：继承 `BaseProcessor` → Bus 挂载时获取 `RemoteVideoTrack`（`room.remote_participants` 中找 `ar-camera` 轨）→ 构建 `VideoStream` 迭代器。

**Phase 2 不激活此路径。**

---

## 五、identify_object 按需截帧

**文件**: `src/parrot/brain/tools/identify_object.py`

**当前状态**: ⚠️ 缺视觉输入 — 详见审计报告 `audit_identify_object_no_screenshot_20260420.md`

### 当前实现路径（Phase 2.5 之前）

`identify_object` 目前通过 Gemini Live 的对话上下文来"识别"物体：
- Gemini 已在看视频流（`video_input=True`）
- Tool 被调用时，Gemini 结合已看到的画面做文字描述
- **没有原始图片**，无法做图像比对或写入 Graphiti 图像字段

### Phase 2.5 升级路径（captureSnapshot RPC）

```
Python identify_object tool 被调用
  │
  ▼
向 Unity 发 RPC "captureSnapshot"（待实现）
  │
  ▼
Unity: AsyncGPUReadback.Request(_rt) → EncodeToJPG(320×240) → base64
  │                                     ↑ 降分辨率避免 RPC payload 超限
  ▼ (RPC response)
Python: 拿到 base64 图片 → Gemini Vision 比对 / 写入 Graphiti
```

**关键约束**:
- LiveKit RPC response 有大小上限 → 截图建议 320×240 或更小；大图改用 ByteStream API
- 时间轴对齐: 截帧响应中附 `ar_timestamp`，与 Graphiti 事件关联（`SemanticNode.reference_image_path` 字段缺失，见审计 §5.1 B4）
