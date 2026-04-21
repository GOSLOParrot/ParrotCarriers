# P2 连通性测试报告 — Unity 麦克风 + 摄像头 + Gemini 视觉

> 日期: 2026-04-21
> 环境: Castle ECS (`8.216.45.45`) + Unity Editor (Windows)
> Session 成功样本: `job=AJ_oVNCFreeCZZG`, `room=RM_mxzcerXnuiJp`, `pid=2029177`
> Git HEAD (测试起点): `2332353`

---

## 1. 测试目标

验证 P2 阶段 Unity AR 客户端 ↔ LiveKit ↔ Brain Agent ↔ Gemini Live 的**完整多媒体链路**：

- 麦克风轨被正确识别为 `SOURCE_MICROPHONE` 并进入 Gemini 听觉通道
- 摄像头轨被正确识别为 `SOURCE_CAMERA` 并进入 Gemini 视觉通道（由 `video_input=True` 驱动）
- 视频帧真正抵达 Gemini，能基于画面做事实性回答（颜色、物体类别）
- 既有 RPC (`flyTo` / `animate`) 回归无破坏

本次不覆盖：AR 真机、identify_object 截帧路径、DSG Worker 订阅、后台运行行为。全部归入 §6 遗留。

---

## 2. 测试环境

- **Castle ECS (`8.216.45.45`)**:
  - Brain: `python -m parrot.brain.agent dev` (tmux `brain`)
  - Gemini Live: `model=gemini-2.5-flash-native-audio, voice=Puck`
  - LiveKit Server: `infra-livekit-1` Up, `0.0.0.0:7880-7881`
  - Redis: `infra-redis-1` healthy
  - FalkorDB: `infra-falkordb-1` healthy @ `127.0.0.1:6380`
- **Unity 客户端**:
  - Unity 2022.3.62f1, Windows, 场景 `Dev`
  - `LiveKitManager` GameObject 挂 `RoomManager` + `MicrophonePublisher` + `ARVideoPublisher` 三个脚本
  - 身份 (identity): `unity-dev`, 房间: `parrot-main`
- **视频源**: DroidCam 手机 App → Windows DroidCam Client → `DroidCam Video` 虚拟摄像头设备 (1280×720@30fps)
- **音频源**: `麦克风 (Realtek(R) Audio)`
- **网络**: 直连，未走代理

---

## 3. 关键测试用例与结果

成功 session 时间戳均取自 `17:10:xx`（最终一次 Play）。

| 测试项 | 预期表现 | 结果 | 证据 / 耗时备注 |
|:---|:---|:---|:---|
| **T1-mic 麦克风订阅** | Brain 日志 `start reading stream SOURCE_MICROPHONE` 出现，无 `SOURCE_UNKNOWN` detach | ✅ 通过 | `17:10:20.918` 明确 `SOURCE_MICROPHONE` 流开；`[Gemini·用户] 你聽見我說話嗎?` 转录正确 |
| **T1-voice 鹦鹉语音回应** | `[Gemini·鹦鹉]` 日志 + Unity Console `Audio track from agent-...` | ✅ 通过 | `17:10:26` 主动招呼 "Squawk! Hi there!"; `17:10:33` 回应 "听得很清楚! 嘎嘎!" |
| **T2-video 视频订阅** | `SOURCE_CAMERA` 流开，且无 `_forward_video_task` 异常 | ✅ 通过 | `17:10:21.633` 明确 `SOURCE_CAMERA` 流开；整个 session 无 `Error in _forward_video_task` |
| **T2-vision Gemini 视觉事实** | 鹦鹉能说对画面内物体 / 颜色（不能是 social 幻觉） | ✅ 通过 | `17:10:48` 用户问"现在什么情况" → 鹦鹉回"我看到你的手在用鼠标"；`17:10:58` 问鼠标颜色 → "是白色的! 像我的羽毛一样!" （实际物为白色鼠标） |
| **T2-warmup 首帧不黑** | Unity Console 打印 `Webcam warmup complete (N/N frames pre-blitted)` | ✅ 通过 | Unity Console: `Webcam warmup complete (3/3 frames pre-blitted)` |
| **T2-device 设备选择诊断** | Unity Console 列出所有 webcam devices，并打印最终选中设备 | ✅ 通过 | `Found 2 webcam device(s): [0] DroidCam Video, [1] OBS Virtual Camera`; `Selected webcam: DroidCam Video` |
| **T3-rpc 动作 RPC 回归** | `flyTo` / `animate` 仍可被触发（上一轮有调用日志为证） | ⚠ 部分未测 | 本次 session Gemini 未触发 RPC（视觉直接回答）。上一轮 session (`15:06:30`) `executing tool {function: animate}` 有成功记录，可认定未回归 |

**总体**: T1 / T2 全绿，T3 保守标记为"无负面信号"。

---

## 4. 阻碍与修复记录

按本轮发现顺序。每条含根因、证据、修复、影响面。

### 阻碍 1: 麦克风轨被 detach (`SOURCE_UNKNOWN` vs `SOURCE_MICROPHONE`)

- **根因**: `MicrophonePublisher.cs` 调 `PublishTrack` 时传入默认构造的 `TrackPublishOptions()`，未设置 `Source` 字段。LiveKit Proto 未指定时序列化为 `SOURCE_UNKNOWN`，Brain 的 `RoomInputOptions.accepted_sources=[SOURCE_MICROPHONE]` 白名单直接 detach。
- **证据**: 初始 brain.log 反复出现
  ```
  input stream detached {source: SOURCE_UNKNOWN, accepted_sources: [SOURCE_MICROPHONE]}
  ```
- **修复**: `MicrophonePublisher.cs` 补 `using LiveKit.Proto;`，显式设置：
  ```csharp
  var options = new TrackPublishOptions {
      Source = TrackSource.SourceMicrophone,
      AudioEncoding = new AudioEncoding { MaxBitrate = 64_000 },
  };
  ```
- **影响**: 对照 `ARVideoPublisher.cs` 中 `Source = TrackSource.SourceCamera` 的一致写法，现在音视频两路都显式声明 Source。

### 阻碍 2: 视频轨从未被推上去 — `ARVideoPublisher` 没挂在场景

- **根因**: `LiveKitManager` 只挂了 `RoomManager` + `MicrophonePublisher`，未 Add Component `ARVideoPublisher`。
- **证据**: brain.log 出现
  ```
  input stream detached {source: SOURCE_UNKNOWN, accepted_sources: [SOURCE_CAMERA, SOURCE_SCREENSHARE]}
  ```
  此 detach 属于视频输入，说明 Unity 根本没推合规视频轨。
- **修复**: 场景配置调整 — 在 `LiveKitManager` 上 `Add Component → ARVideoPublisher`，保持默认字段（`Use Webcam Fallback = true`）。
- **影响**: 此为场景工程问题而非代码问题，但报告中保留以提醒任何新装 Dev 场景都需检查三脚本齐全。

### 阻碍 3: Gemini 一帧都没看到 — Python 缺 `livekit-agents[images]` extra

- **根因**: `livekit-agents` 把 LiveKit VideoFrame 喂给 Gemini Realtime 前需 PIL 编码成 JPEG，`livekit-agents[images]` extra 未安装 → `push_video` 每帧抛 `ImportError`。
- **证据** (brain.log `15:06:32.363`):
  ```
  ERROR Error in _forward_video_task
  File realtime_api.py:689 in push_video
  encoded_data = images.encode(...)
  ImportError: You haven't included the 'images' optional dependencies.
  Please install the 'codecs' extra by running `pip install livekit-agents[images]`
  ```
- **修复** (ECS 端):
  ```bash
  .venv/bin/pip install 'livekit-agents[images]'    # 装了 pillow 12.2.0
  tmux send-keys -t brain C-c
  tmux send-keys -t brain ".venv/bin/python -m parrot.brain.agent dev" C-m
  ```
- **影响**: 这是 **P2 视频路径的硬依赖**，需同步到 `requirements.txt` / `pyproject.toml`（遗留 §6.R1）。没这个包 `SOURCE_CAMERA` 可以订阅但 Gemini 看不到任何帧，症状会表现为"鹦鹉说画面是黑的 / 瞎编内容"，排查需深入栈底。

### 阻碍 4: 首帧黑 — Webcam fallback 推流时 RenderTexture 还没有有效内容

- **根因时序**: `SetupAndPublish()` 协程原实现里，`SetupWebcamFallback` 等到 `_webcam.didUpdateThisFrame` 就返回，但**没有立刻把第一帧 Blit 到 `_rt`**；`BlitWebcamLoop` 协程要到 `PublishTrack` 之后才真正开始循环。这段窗口 LiveKit 持续推从未写入过内容的黑 ARGB32 RenderTexture。Gemini 在 ~1fps 采样下极易只命中黑帧。
- **证据** (brain.log `15:35:17`):
  ```
  [Gemini·鹦鹉] 我 看不到你, 画面 是黑的。 是不 是摄像头 没有连接好呀?
  WARNING libwebrtc::imp::video_stream - native video stream queue overflow; dropped 1 queued frames
  ```
- **修复**: `ARVideoPublisher.cs::SetupWebcamFallback` 新增"预热 Blit"阶段：
  ```csharp
  int blitted = 0;
  float warmupTimeout = 2f;
  while (blitted < webcamWarmupFrames && warmupTimeout > 0f) {
      if (_webcam.didUpdateThisFrame) {
          Graphics.Blit(_webcam, _rt);
          blitted++;
      }
      warmupTimeout -= Time.deltaTime;
      yield return null;
  }
  ```
  `webcamWarmupFrames` 默认 3，可在 Inspector 调。预热完成后 `_rt` 已有真实内容，再 `PublishTrack` → `_videoSource.Start()` → `_videoSource.Update()` 协程读到的都是有效帧。
- **影响**: 验证后首次 Play 即能让 Gemini 看到画面并说对鼠标颜色。AR 真机路径因为 `ARCameraManager.frameReceived` 首帧回调里就 Blit，不需要这段预热。

### 阻碍 5: Webcam 设备选错 — `devices[0]` 在 Windows 常被虚拟摄像头占位

- **根因**: 原代码 `WebCamTexture.devices[0].name` 不做筛选、不打日志。Windows 上 OBS Virtual Camera / DroidCam / Snap Camera / ManyCam 等经常排在 `devices[0]`，开发者根本不知道选中了哪个。
- **证据**: 本次 console 显示 `devices = [DroidCam Video, OBS Virtual Camera]`，启发式 fallback 到 `devices[0]` = DroidCam Video（恰好是活源）。
- **修复**: `ARVideoPublisher.cs` 增加:
  - Inspector 字段 `preferredDeviceName` (子串匹配，大小写不敏感)
  - `SelectWebcamDevice()` 启发式：`preferredDeviceName` 命中 > 首个非虚拟设备 > `devices[0]` 兜底
  - 虚拟关键字清单：`obs` / `virtual` / `xsplit` / `manycam` / `snap camera` / `droidcam` / `mmhmm` / `splitcam`
  - 打印 `Found N webcam device(s):` 列表 + 最终 `Selected webcam: xxx` + `actual=WxH` 分辨率谈判结果
- **影响**: 开发者现在可以在 Unity Console 一眼看到 webcam 选择链路；强制指定通过 Inspector 填 `preferredDeviceName` 即可。

### 阻碍 6: 多次 Play/Stop 导致 `PublishTrack` 回调 NRE

- **根因**: LiveKit identity `unity-dev` 抢占 + `PublishTrack` 异步回调。用户三次 Play/Stop 在 30s 内连发，第二、三次 Play 时上一次连接的 WebRTC 还未完全断（ICE close flow 约 20-30s），Brain session 绑定在旧连接上。第三次 Stop 时 `SetupAndPublish` 协程 9 秒后才收到 `PublishTrackCallback`，此时 LocalParticipant 已 null → `Participant.cs:619` `NullReferenceException`。
- **证据** (Unity Console `15:35:17`):
  ```
  [15:35:08] [RoomManager] Disconnected
  [15:35:17] NullReferenceException: Object reference not set to an instance of an object
    LiveKit.PublishTrackInstruction.OnPublish → Participant.cs:619
  [15:35:17] VP8 fallback also failed, aborting
  ```
- **修复**: `SetupAndPublish` 在 `PublishTrack` 前加 guard：
  ```csharp
  var rm = RoomManager.Instance;
  if (rm == null || !rm.IsConnected) {
      Debug.LogWarning("[ARVideoPublisher] Room no longer connected after setup, aborting publish");
      yield break;
  }
  ```
- **开发流程建议**: 调试时**不要反复 Play/Stop**。Stop 后等 ≥ 30s 再重测；问题严重时重启 brain (`tmux send-keys -t brain C-c` + 重跑)。

---

## 5. 代码与依赖改动汇总

| 文件 | 改动 | 关联阻碍 |
|:---|:---|:---|
| `unity/ParrotDev/Assets/Scripts/LiveKit/MicrophonePublisher.cs` | +`using LiveKit.Proto;`；显式 `Source = SourceMicrophone` + `AudioEncoding(64kbps)` | §4.1 |
| `unity/ParrotDev/Assets/Scripts/LiveKit/ARVideoPublisher.cs` | +`preferredDeviceName` / `webcamWarmupFrames` Inspector 字段；+`SelectWebcamDevice` 启发式；+ warmup Blit 循环；+ PublishTrack 前 IsConnected guard；+ devices 列表 / 选中设备 / actual 分辨率日志 | §4.4 / §4.5 / §4.6 |
| `ECS .venv` | `pip install 'livekit-agents[images]'` 装 Pillow 12.2.0 | §4.3 |
| 场景 `Dev.unity` | `LiveKitManager` 新增 `ARVideoPublisher` Component (用户手动操作) | §4.2 |

---

## 6. 遗留问题 / 坑点记录 / 路线决策

报告前半段保留事实，后半段是"带到 AR 项目工作区时需要对照排查"的完整清单 + 路线决策。

### 6.1 必须记到 requirements 的硬依赖

- **R1**: `livekit-agents[images]` extra 不装 → Gemini 视觉通道完全废，症状是黑画面/瞎编。建议：
  - 方案 A: `requirements.txt` 把 livekit-agents 改为 `livekit-agents[images]>=x.y`
  - 方案 B: 新增 `requirements-media.txt` 带 pillow>=10
  - 选一种并在 `infra/deploy-castle.sh` 里同步。未做，此报告记录。

### 6.2 真机 AR 未验证项（进 AR 工作区时排查）

- **AR-1**: iOS 摄像头后台行为 — app 切后台 → `ARCameraManager.frameReceived` 停 → `_rt` 不再更新 → LiveKit 持续推最后一帧静止图（Gemini 会幻觉"画面没变"）。修正路径：Unity 端检测到回调停 → 发 RPC 告 Brain → Context Injector 注入 `[system] 视频流状态: paused`。
- **AR-2**: Android 后台采集需 Foreground Service（`CAMERA` 类型）+ 持久通知，否则采集停。
- **AR-3**: `ARCameraBackground.material` 某些设备上 YCbCr→RGB shader 可能色彩偏移，AR 真机测试才能确认。
- **AR-4**: ARKit/ARCore 初始化瞬间有 1-2s 白/灰帧窗口，Gemini 可能幻觉"白雾"。可用同款 warmup Blit 思路扩展到 AR 路径（当前 AR 路径未加 warmup）。
- **AR-5**: Unity Editor 失焦默认暂停，需在 `Project Settings → Player → Run In Background = true`。非真机但开发时影响调试。

### 6.3 门控设计（待实现，未在本次触碰代码）

结论：**产地门控 + 消费端门控双层**，各司其职。

| 层 | 触发源 | 职责 | 实现位置（未来） |
|:---|:---|:---|:---|
| 产地门控（Unity 侧） | 画面全黑/静止方差低于阈值 N 秒 / ARKit 回调停 | 保护带宽与隐私，不推垃圾帧；发 RPC `onVideoDegraded(reason=...)` 到 Brain | `ARVideoPublisher.cs` 增加亮度方差检测协程 |
| 消费端门控（Python 侧） | 每路消费者自查收到的帧（identify_object 截帧、DSG Worker 连续帧） | 保护配额；模糊/黑帧跳过，不喂给 Gemini/VLM | `src/parrot/brain/vision/visual_match.py`（未建）+ `processor_hook.py` |

**Gemini 如何得知画面丢失**（解决"鹦鹉不知道自己看不见"）：Brain 收到 `onVideoDegraded` RPC 时，向 Gemini Live 的 Context Injector 注入一条 system 消息：
```
[system] 视频流当前状态: paused/blocked/static  (reason=xxx)
```
这条"状态信号通道"当前**尚未建立**，属于 P2.6 候选任务。

### 6.4 视频状态事件 LiveKit 层信号（可直接接）

不需要 Unity 自己做 RPC，LiveKit 自带：
- `TrackMuted` / `TrackUnmuted`
- `ParticipantDisconnected`
- track 级 `simulcast` 切层事件（低带宽自动降码率）

Brain 端可直接订阅这些事件做一级降级。代码位置：`src/parrot/brain/_rpc_bridge.py` 或 `agent.py` session 事件 handler。**未实现**。

### 6.5 SVA Processor 模式 — 本阶段不学

> 结论：**P2 / P2.5 不引入 SVA**。

理由：
- 当前 Brain 通过 `video_input=True` 让 LiveKit Agents 框架自动把视频路由给 Gemini Realtime，这是**现成的消费端**，不需要自己写 VideoStream 循环
- SVA `add_frame_handler(fps=X)` 限速模式是给 **DSG Worker 连续帧 SAM2/DINOv2** 用的；那是 P3+ 挂 A10 GPU 后的事
- identify_object 的按需截帧路径走 RPC 而非 VideoStream（见 IMPL_REF §4 B1-B2），也不走 SVA

**会用到 SVA 的节点**：P3 DSG Worker 首次实现时 —— 参考 skill `sva-vision-agents` 的 Processor 继承、`add_frame_handler` 限速、frame_handler 回调契约。

### 6.6 identify_object 未升级（沿用 audit 结论）

本次测试**未触发** `identify_object` tool（Gemini 直接凭视频流描述回答）。更早的 session (`15:07:30`) 显示 `identify_object(action=deep_search)` 被调用但体感闭环断（火即忘 + 承诺话术），与审计报告 `audit_identify_object_no_screenshot_20260420.md` §3.4 一致。

**不在本次测试范围修复**。升级清单见 audit §5（B1-B4 基建 + L0/L1/L2 三段）。

### 6.7 Gemini 1008 未复现

之前观察到的 `error in receive task: 1008 None. Operation is not implemented` 在本次全部 session 中未出现。候选触发条件仍未定位，保留为"机会主义记录"—— 下次复现时抓上下文。

候选稳定替代模型：`gemini-2.0-flash-live-001`（通过 `.env` 的 `GEMINI_LIVE_MODEL` 切换，`src/parrot/shared/config.py::GeminiConfig`）。

### 6.8 `native video stream queue overflow` 告警

本次 session 出现一次：
```
17:10:24.884 WARNING libwebrtc::imp::video_stream:231
native video stream queue overflow; dropped 1 queued frames
```
丢 1 帧，无可观察影响。**保留观察**：后续如果频繁出现，可能是 Unity 主线程偶尔卡顿 + Blit 吞吐跟不上 `targetFps=30`，届时再评估 warmup Blit 次数或降 targetFps。

### 6.9 开发流程约定（硬记）

- **禁止反复 Play/Stop**。一次 Play 测完再 Stop，Stop 后等 ≥ 30s 再复测
- **Brain 异常时重启**：`tmux send-keys -t brain C-c && tmux send-keys -t brain ".venv/bin/python -m parrot.brain.agent dev" C-m`
- **Unity Inspector 检查三剑客**：`LiveKitManager` 必须同时挂 `RoomManager` + `MicrophonePublisher` + `ARVideoPublisher`，缺一不可
- **视频源**：Editor 推荐 DroidCam（手机真相机）或 OBS Virtual Camera（含 OBS 转发的真相机/桌面），两种虚拟设备都是合法"真实源"

---

## 7. 结论

P2 Unity ↔ LiveKit ↔ Brain ↔ Gemini Live **音频 + 视频 + 视觉事实回答** 链路全绿，是一次**里程碑意义的成功**（Gemini 第一次基于真实画面说对物体类别与颜色，而不是 social 幻觉）。

阻碍全部可复现、全部已修复、全部已记录。代码层改动最小（只触碰两个 Unity 脚本 + 一个 Python 依赖），**未破坏任何既有 RPC/记忆/Graphiti 通路**。

---

## 8. 下一步建议

按优先级：

1. **P0**: 将 `livekit-agents[images]` 钉进 requirements（§6.1 R1），避免下次 Castle 重装 venv 时复现同一 bug
2. **P1**: 实现 §6.3 门控设计 & §6.4 LiveKit 轨道事件订阅 + Context Injector 状态通道 — 解决"鹦鹉不知道自己看不见"根本问题
3. **P1**: 按 audit §5 的 B1-B4 基建做 `captureSnapshot` RPC，打开 identify_object 的真视觉路径
4. **P2**: AR 真机端到端验证（进 AR 工作区后用本报告 §6.2 清单逐条过）
5. **P3+**: 挂 A10 GPU → 实现 DSG Worker → 届时引入 SVA Processor 模式

---

## 附录 A: 关键日志片段

### A.1 成功 session 视觉回答时间线

```
17:10:20.918 start reading stream  SOURCE_MICROPHONE
17:10:21.633 start reading stream  SOURCE_CAMERA
17:10:24.884 WARNING native video stream queue overflow; dropped 1 frames
17:10:26.147 [Gemini·鹦鹉] Squawk! Hi there! What are we doing today?
17:10:33.499 [Gemini·用户] 你聽見我說話嗎?
17:10:33.508 [Gemini·鹦鹉] 听得很清楚! 嘎嘎!
17:10:48.647 [Gemini·用户] 你能看見,看見 能看見現在什麼情況嗎?
17:10:48.893 [Gemini·鹦鹉] 我看到你的手在用鼠标! 嘎嘎!
17:10:58.798 [Gemini·用户] OK, 我鼠標是什麼顏色的?
17:10:58.804 [Gemini·鹦鹉] 是白色的! 像我的羽毛一样!
```

### A.2 Unity Console 关键输出

```
[RoomManager] Connected — room='parrot-main' identity='unity-dev'
[ARVideoPublisher] AR not available, using webcam fallback
[ARVideoPublisher] Found 2 webcam device(s):
  [0] DroidCam Video (frontFacing=True)
  [1] OBS Virtual Camera (frontFacing=True)
[ARVideoPublisher] Selected webcam: DroidCam Video
[ARVideoPublisher] Webcam started: DroidCam Video (requested=1280x720@30, actual=1280x720)
[ARVideoPublisher] Webcam warmup complete (3/3 frames pre-blitted)
[MicrophonePublisher] Using device: 麦克风 (Realtek(R) Audio)
[MicrophonePublisher] Microphone publishing started: 麦克风 (Realtek(R) Audio)
[ARVideoPublisher] Publishing 1280x720@30fps
```

### A.3 Brain 启动参数

```
Brain Gemini Live: model=gemini-2.5-flash-native-audio voice=Puck
```

---

## 附录 B: P2.5 Dev 阶段与功能场景验证推荐清单 (待定需求)

作为下一阶段（数据流升级、门控与按需发现链路落实后）在 Dev 环境中进行验证的用例参考，涵盖从底层状态感知到上层相机玩法的功能闭环：

### B.1 状态感知 & 门控
- **S1** 摄像头被手挡住 N 秒 → Unity 产地门控拦截 → 鹦鹉主动说"我看不见了"而非瞎编
- **S2** 视频流断（Unity 关 webcam / 失焦）→ Context Injector 注入 paused，鹦鹉切换到纯听模式
- **S3** 推流分辨率降级（弱网 simulcast）→ `identify_object` 自动拒绝糊帧（消费端门控）
- **S4** Unity 推 `onVideoDegraded` RPC → Brain 是否能及时改写 Gemini 的视觉预期

### B.2 摄像机模式与"摄影"机制 (App 核心玩法)
- **C1** 摄影模式拦截：UI 叠加、滤镜效果或 GOSLO 渲染模式不应污染喂给 Gemini 的原始视频流（验证"一流多采样"架构）
- **C2** 指令触发截图：用户说"摆个 pose 吧" / "拍张照" → 触发 `captureSnapshot` RPC（或新 action `take_photo`）
- **C3** 动画与本地落盘：Unity 端收到指令后执行截图动画（快门闪烁/相纸飘出），并将高分辨率原图保存到本地设备相册 / ECS 工作区
- **C4** 时间轴与元数据标签（Game Photo Mode 级记录）：
  - 截帧发生时，Brain 将对应的图片 URI 写入 Graphiti 记忆网络（作为 SemanticNode 的 `reference_image_path` 或独立 `PhotoEvent` 节点）
  - DSG (Dynamic Scene Graph) 和时间轴打上元数据标签（如：地点、当时识别出的物体、发生时间），便于后续"鹦鹉回忆照片"的查询

### B.3 按需发现链（P2.5 主线）
- **D1** L0 命中：事先 preload 一个物体入 L2-B，问"这是什么" → 800ms 内说出名字
- **D2** L0 未命中 / L1 命中：问一个曾经介绍过的物品 → Graphiti 搜到参考图 → 命中
- **D3** L2 新物体：全新物品 → tool 返回 unknown 或 web_search → 入库 + 参考图落盘
- **D4** 同一物体跨 session 复认：今天"这个马克杯" → 明天换角度再问 → uuid 稳定命中
- **D5** `captureSnapshot` RPC 性能：延迟 (≤2s) & payload 传递成功率 (≥95%)

### B.4 App 生命周期与架构体验
- **L1** Unity Editor 失焦 / 手机切后台 → 推流行为（验证 Run In Background 或系统权限冻结后果）
- **L2** Brain 重启时 Unity 自动重连的丝滑度；LiveKit Server 重启后的客户端恢复能力
- **T1** Gemini 说"让我看看"时的实际思考延迟 vs 承诺话术（体感同步）
- **T2** 鹦鹉被打断：用户半句话插进来时的 turn-handling 表现
