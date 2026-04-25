---
name: livekit-unity-video-publish
description: 一流多采样接缝 — Unity 主视频源 + 策略门控 + LiveKit 分发 + Brain/DSG/identify_object 多路消费端边界
status: ratified
status_note: "基于 ARVideoPublisher.cs 实代码和 Sprint4 前置稳定性决策更新。主视频是策略门控共享源, 不再默认固定高质量。"
last_reviewed: 2026-04-25
---

# 视频流接缝：一流多采样 + 策略门控 (One Stream, Multiple Sampling)

> **适用场景**: 新增视频消费者、调试视频采样、设计 Sprint4 视频档位/门控、理解 identify_object 缺截图问题时查阅。
>
> 关联审计: `.cursor/memory/architecture/audit_identify_object_no_screenshot_20260420.md`
>
> Sprint4 稳定性策略: `.cursor/memory/architecture/sprint4_livekit_stability_and_video_strategy.md`
>
> 黑屏/假 ON 复盘: `docs/test/p2_5/brain_connected_black_video_20260425.md`
>
> AR 版本锁/治理规则: `.cursor/rules/ar-foundation.mdc`
>
> 实现细节草稿: 本目录 `IMPL_REF.md`

---

## 一、数据流全景

```
Unity (ARVideoPublisher.cs)                     LiveKit Server (Castle)            Python 消费者
策略门控主视频源 ────────────────WebRTC推流──>  LocalVideoTrack "ar-camera"  ──订阅──>  多路
                                                                                    │
                                          ┌─────────────────────┬──────────────────┤
                                          │                     │                  │
                                   Brain Agent          DSG Worker          identify_object
                                  video_input=True     VideoStream(track)   captureSnapshot
                                  Gemini Live 自动订阅   A10, Phase 3+        RPC 按需截帧
                                  内部 ~1fps 采样        add_frame_handler    Phase 2.5
                                  云端黑盒，不可取帧      fps=X 独立循环       EncodeToJPG
```

**核心原则**: 推流端 (Unity) 负责一个可门控的共享主视频源，而不是固定高质量源。质量档位由 Bus 策略、App 生命周期和消费者需求共同决定；新增消费者不应直接改 Unity 采集管线，而应通过明确的控制信号、订阅策略或补充通道接入。

Sprint4 起必须区分三类视觉需求：

- **Gemini Live 默认对话**: 优先低延迟、稳定音频和持续连接；视频质量可以低于 720p/30fps。
- **identify_object 按需识别**: 通过 `captureSnapshot` 获取低分辨率可存档图片，不依赖 Gemini 黑盒已看帧。
- **A10 / SAM2 / DINOv2 感知任务**: A10 在线且任务需要时，短时请求更高质量或更密采样，不让手机和 Castle 长期承载高档。

---

## 二、AR 版本锁与治理边界

当前 AR 工作区锁定 Unity 2022.3 LTS + AR Foundation/ARCore/ARKit 5.1.x。联网核对后的判断：

- 这是 Sprint3/4 最保守的稳定组合；继续使用 2022.3 LTS 没问题。
- 这是当前项目收口基线，不是永久版本承诺；Sprint4 后若进入长期独立 app 开发，再单独评估迁移到当时最新 LTS。
- AR Foundation 官方说明本体只提供接口，Android/iOS 必须分别安装并启用 ARCore/ARKit provider plug-in。
- `UNITY_AR_FOUNDATION` 不是 Unity 自动宏；当前项目通过 `unity/ParrotDev/Assets/csc.rsp` 显式定义。
- `csc.rsp` 是当前无 asmdef 项目的短期正确做法；若 Sprint4 后拆出 AR assembly，应迁移到 asmdef `versionDefines`，例如 `com.unity.xr.arfoundation` `[5.1,5.2)` → `UNITY_AR_FOUNDATION`。

治理要求：不要在视频/稳定性问题未收口时同时升级 Unity、AR Foundation、ARCore/ARKit 或 LiveKit Unity SDK。版本迁移必须单独开任务并重新验证 XR Simulation、Android ARCore、`frameReceived`、LiveKit 推流、首帧/新鲜帧门和 app 启动门。

---

## 三、Unity 推流端

**文件**: `unity/ParrotDev/Assets/Scripts/LiveKit/ARVideoPublisher.cs`

**验证状态**: Editor Webcam 路径已 E2E；Android P2.5 发现 AR 宏未进入构建导致 fallback/stale，已修 `csc.rsp` 和诊断。真机 AR 路径需重新打包验证。

### 两条推流路径

| 路径 | 触发条件 | 帧来源 |
|:-----|:---------|:-------|
| AR 路径 | `#if UNITY_AR_FOUNDATION` + `ARCameraManager` + `ARCameraBackground` 均存在 | `ARCameraBackground.material` → `Graphics.Blit(null, rt, mat)` in `frameReceived` 回调 |
| Editor 回退 | AR 不可用 且 `useWebcamFallback=true` | `WebCamTexture` → `Graphics.Blit(webcam, rt)` Coroutine 循环 |

两条路径共享一个 `RenderTexture` (1280×720, ARGB32) 作为 `TextureVideoSource` 输入。

### 当前推流参数（开发上限，不是长期默认）

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

这组参数是 Sprint3/P2.5 的开发上限。Sprint4 默认档应重新评估，优先从 Gemini Live 低延迟需求出发，例如 480p/15fps/600-900kbps 量级，再保留 720p/30fps/1.5Mbps 作为调试或 A10 任务触发上限。

### Unity 端闸口

Unity 端适合负责以下门控：

- 首帧门：没有真实帧不宣称视频可用。
- 新鲜帧门：LiveKit 轨道已发布但 `lastAge` 超阈值时必须视为 `static_frame` / stale，而不是 Video OK。
- 生命周期门：切后台、锁屏、权限丢失时主动 mute/暂停/重建。
- 视频档位门：根据 Brain/A10/用户动作切换 publish 参数或重建 track。
- 补充截图门：按需 `captureSnapshot`，不要把所有视觉需求都压到主视频流。

### 推流端不做的事

- 不做重识别或 SAM2/DINOv2 推理。
- 不把 Gemini 黑盒已看帧当成可审计图片来源。
- 不把测试 HUD / 自检按钮的状态当成正式 App 生命周期设计。
- 不在消费者内部私自改 Unity 采集管线；视频档位变化必须走明确控制信号。
- `Graphics.Blit` 必须在 `frameReceived` 回调内执行（ARVideoPublisher.cs 已正确实现）
- `UNITY_AR_FOUNDATION` 是项目显式宏；若构建后 HUD 显示 `AR: UNITY_AR_FOUNDATION off`，真机 AR 相机路径已被编译掉，视频会退到 WebCam fallback。

---

## 四、Brain Agent 消费端

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
- Gemini Live 是流式对话 Agent。Sprint4 默认视频档应优先保证约 1.5s 级别对话体感，而不是追求主视频画质。

### 不需要做的事

- 不需要在 Python 层显式抽帧或用 `VideoStream(track)`
- 不需要为 Gemini 设置采样频率（云端自动）
- 不需要为了 Gemini 默认对话持续推高质量视频；需要高质量时应由识别任务或 A10 在线状态触发。

---

## 五、DSG Worker 消费端（未来 A10，接口预留）

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

### A10 触发升档原则

未来 A10/DSG 不应要求 Unity 永远高质量推流。推荐策略：

- 常态 Gemini 档保持低延迟低码率。
- A10 在线并接到感知任务时，通过 Bus 控制信号请求短时升档。
- DSG Worker 自身仍按 `VideoStream(track)` 或 SVA `add_frame_handler(fps=X)` 限速采样。
- 重计算放在 Mecha/A10，Castle 只维持控制面与 LiveKit 分发。

---

## 六、identify_object 按需截帧

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
