---
status: tentative
status_note: "问卷部分已完成回收 (见 ar_feature_vision.md §六/§八). 工程计划五维问卷结论已并入 ar_feature_implementation_plan.md, 本文件保留作需求追溯。"
last_reviewed: 2026-04-22
---

# AR App 工程计划

> 日期: 2026-04-20
> 状态: 初版 — 硬事实已整理，待用户填写问卷后收敛需求
> 前置: P1.5 Bus 已验证 / P2 Graphiti+FalkorDB 已实现 / Castle 待首次拉起
> 关联: `milestone_p2.md` Phase 2 C1-C12 / `requirements.md` §四-C

---

## 一、硬事实（代码已有 / 已验证）

以下信息均来自仓库现有代码和已验证的部署报告，不含未实现的设计假设。

### 1.1 Unity 客户端已有代码

| 文件 | 功能 | 验证状态 |
|:-----|:-----|:---------|
| `unity/ParrotDev/Assets/Scripts/LiveKit/RoomManager.cs` | LiveKit Room 连接 + 音频自动播放 + 单例 | P1 笔记本模拟验证通过 |
| `unity/ParrotDev/Assets/Scripts/LiveKit/ARVideoPublisher.cs` | AR/Webcam → RenderTexture → LiveKit VideoTrack (1280x720@30fps, H.264/1.5Mbps, VP8 fallback) | 代码就绪，端到端未验证 |
| `unity/ParrotDev/Assets/Scripts/Parrot/ParrotRpcHandler.cs` | RPC 接收: flyTo / animate → ParrotController | P1 sim_unity_client 验证通过 |
| `unity/ParrotDev/Assets/Scripts/Parrot/ParrotController.cs` | 方块移动 + 颜色反馈 (Phase 1 dev placeholder) | P1 验证通过 |
| `unity/ParrotDev/Assets/Scripts/XRHands/XRHandTracker.cs` | XR Hands 骨架 | 代码就绪，未验证 |
| `unity/ParrotDev/Assets/Scripts/XRHands/PerchOnHand.cs` | 鹦鹉停手上 | 代码就绪，未验证 |

### 1.2 requirements.md C1-C12 完成状态

| ID | 功能 | Phase | 完成状态 | 说明 |
|:---|:-----|:------|:---------|:-----|
| C1 | LiveKit 连接 | 1 | **done** | `RoomManager.cs` P1 笔记本验证通过 |
| C2 | AR Foundation 基础 | 1 | **not-started** | 无 AR 项目容器，需创建 ParrotAR Unity 项目后再做 |
| C3 | 鹦鹉模型+基础动画 | 1 | **code-ready** | `ParrotController.cs` 方块占位 + 程序化 pulse；无真实 Animator；`GOSLO.glb` (29KB) 已在 Assets |
| C4 | RPC Handler | 1 | **done** | `ParrotRpcHandler.cs` flyTo/animate P1 sim_unity_client 验证通过 |
| C5 | 遥测上报 | 1 | **code-ready** | `XRHandTracker.cs` 手部遥测 DataChannel 已写；AR Pose 遥测字段缺失（Opus 11 设计，无代码） |
| C6 | TTS Speaker | 1 | **done** | `RoomManager.cs` 自动音频播放 P1 验证通过 |
| C7 | APP 生命周期管理 | 1 | **not-started** | `OnApplicationPause` 通知 Agent 未实现 |
| C8 | XR Hands 手势输入 | 2 | **code-ready** | `XRHandTracker.cs` 骨架已写，需 `com.unity.xr.hands` 包，未编译验证 |
| C9 | 手势反射动作 | 2 | **not-started** | 依赖 C8 + Scheduler reflex 节点，均未实现 |
| C10 | 鹦鹉高级动画 | 2 | **not-started** | 依赖用户制作 fly/dance/idle/perch 动画 |
| C11 | 平面行走 | 2 | **not-started** | 依赖 C2 AR Foundation + C3 动画 |
| C12 | 网络质量提示 | 2 | **not-started** | 弱网 UI 反馈未实现 |

### 1.3 Python 后端已有接口

| 模块 | 已实现 | 视频采样相关 |
|:-----|:-------|:------------|
| `brain/agent.py` | AgentSession + Gemini RealtimeModel (`video_input=True`) | Gemini Live 已能"看"视频流（云端黑盒） |
| `brain/tools/identify_object.py` | match / save_new / deep_search 三档 | **缺视觉输入** — 见审计报告 |
| `bus/processor_hook.py` | D0 BaseProcessor 抽象接口 | on_video_frame / on_telemetry 占位 |
| `dsg/l2b_types.py` | SemanticNode 数据结构 | **缺 reference_image_path 字段** — 见审计报告 §5.1 B4 |
| `brain/_rpc_bridge.py` | Agent → Unity RPC 转发 | 已验证: flyTo / animate |

### 1.4 LiveKit Unity SDK 已知事实

- 版本: v1.3.5, UPM git URL 安装
- `Room.Connect(url, token, options)` — 三参数必传
- `ConnectInstruction` 只有 `IsError` / `IsDone`，无 `.Error` 字符串
- RPC: `LocalParticipant.RegisterRpcMethod(name, handler)`
- TextureVideoSource: `new TextureVideoSource(rt)` → `LocalVideoTrack.CreateVideoTrack(name, source, room)`
- 详见: `.cursor/rules/livekit-unity-sdk.mdc`

### 1.5 视频流架构（已确认设计）

**"一条流多处采样"** — 来自 `Opus/10_architecture_diagram.md` v3:

```
Unity AR Camera → RenderTexture → LiveKit VideoTrack ("ar-camera")
                                       │
                    ┌──────────────────┬┴──────────────────┐
                    │                  │                    │
            Gemini Live           DSG Worker          captureSnapshot
         (video_input=True)    (A10, Phase 3+)       (RPC, Phase 2.5)
         自动看、自动采样       独立订阅 ≤30fps       按需抓帧 →
         云端黑盒、不可取帧     SAM2+DINOv2          EncodeToJPG → base64
```

### 1.6 部署拓扑

- Castle (2C8G): LiveKit Server + Redis + FalkorDB + Brain Agent + Scheduler + Nanobot
- Unity app 通过 WebRTC 连 Castle LiveKit (7880 端口)
- VPN/代理必须对 Castle IP 配 DIRECT 规则（UDP 丢包问题）

---

## 二、调研索引（指引，不复制内容）

以下文档包含 AR App 相关的调研结论。在实现阶段按需查阅，**标注为"调研，无代码"的均未经代码验证，不是确认需求**。

| 主题 | 出处 | 状态 | 一句话摘要 |
|:-----|:-----|:-----|:----------|
| StabilityGate 四级 | `Opus/11_L1_vision_design.md` §2 | 调研，无代码 | 基于 ARCore TrackingState 的帧门控，4 级稳定度 |
| ar_telemetry 10Hz | `Opus/11_L1_vision_design.md` §2.2 | 调研，无代码 | Unity→Python Lossy DataChannel 遥测帧字段 |
| 设备选型/基线 | `Opus/12_scene_and_timeline_design.md` | 调研建议 | Snapdragon 870+/Android 10+/ARCore 设备推荐 |
| SceneProfile 参数化 | `Opus/12_scene_and_timeline_design.md` §1.2 | 调研，无代码 | OUTDOOR/INDOOR/DESKTOP 不同处理器配置 |
| preload_object_semantics | `Opus/17_dsg_node_and_trigger_design.md` §L579 | 调研，无代码 | L2-B 预加载物体时携带参考图的契约 |
| Gemini 看图识别 + 权威链 | `Opus/19_anomaly_ghost_expectation_vision.md` ADR-028 | 调研，无代码 | identify_object 深度验证的权威链设计 |
| 视频流拓扑 v3 | `Opus/10_architecture_diagram.md` 总架构图 | 已采纳为设计基线 | 一流多采样：Unity 推流 → Gemini/DSG/Tool 三路消费 |
| ARCore/LiveKit 版本决策 | `Opus/22_research_sources_and_traceability.md` | 部分采纳 | CameraVideoSource → PublishTrack 路径选择 |
| identify_object 缺截图 | `.cursor/memory/architecture/audit_identify_object_no_screenshot_20260420.md` | 已知缺陷 | 缺视觉输入 + B1-B4 基建 + L0-L2 三段递进升级路径 |
| 行为状态机 | `.cursor/memory/parrot_behavior_rules.md` | 设计，无 Unity 实现 | 6 状态 + 兼容矩阵 |
| 9 场景压测 | `requirements.md` §十 | 需求级 | 9 个使用场景 → 功能 ID 映射 |

---

## 三、AR App 需求问卷（待用户填写）

> 以下问题决定了 AR App 的工程边界和实现优先级。可以简短回答（一句话 / 选项即可），未决定的标"TBD"。

### A. 功能边界（P2 做什么不做什么）

1. P2 的 AR App **最小可玩版本**长什么样？（第一个可验证场景）
   - [ ] (a) 鹦鹉在 AR 平面上 idle + 语音对话（验证视频流+语音全链路）
   - [ ] (b) 鹦鹉飞到指定位置 + 语音 + 识物（验证 RPC + identify_object）
   
   b怎么样



2. C2 AR Foundation 平面检测：桌面 / 地面 / 墙面分别需要吗？（P2 范围）

    我p2就先完成桌面场景就行了，你可以看看桌面场景需要完成哪些部分。

3. C8/C9 XR Hands：P2 做还是先跑通无手势版本？（C8 code-ready，未编译验证）
    
    我希望我比手势 伸出一根食指他能想鸟一样飞到我的手指中段。


4. 像素画小纸条：P2 MVP 还是 P3？
   - 如果 P2: UI Canvas + 2D Sprite + RPC 触发？还是世界空间 3D 便签？

    UI就好，给猫娘女仆一些自己给我传达消息的通道。

5. identify_object 按需发现：P2 首测范围？（当前实现依赖 Gemini 自描述，无截图）
    这个的升级和数据流设计一起解决，两个都是我们下一次测试的主要内容。


### B. 设备与环境

6. 首个目标机型是什么？（确认 ARCore 兼容性和 Android API level）
    IQOO NEO9

7. 是否需要非 AR 回退模式？（不支持 ARCore 的设备上降级到 2D 模式）
    不需要。我们这个就是AR项目，2D模式相当于再补充一个副项目（比如查看提醒/处理文档/整理文件/2D互动）
    我们先集中完成3D互动模式，同时多探索一点，让可扩展性变强。

8. iOS 什么时候考虑？（目前代码只有 Android/ARCore 路径）
    超级后面，等我买得起设备

9. 是否需要 Editor 开发模式（Webcam 替代 AR）长期支持？
    我不确定，这个很重要吗

### C. App 启动与生命周期（C7 优先级 P0）
    这个要深入探讨， 你可以调查市面上的AR互动软件和AI文档处理软件/个人知识库项目 先总结一些框架。



10. 冷启动流程：直接进 AR？还是先有个 2D 连接界面？
    做个启动界面吧，方便我以后加东西（比如你说的2D项目）

11. LiveKit Token 从哪来？（内嵌？启动时请求服务器？dev 模式读文件可以，但正式版呢）
    我也想知道，能通过API来算的，你帮我找到个好点的解决办法。

12. 用户拒绝相机/麦克风权限时怎么办？（C7 相关）
    我去，按照方便的来，我不太懂。退回菜单吧，这两个有点必须。

13. 前后台切换策略：`OnApplicationPause` 时如何处理？
    - [ ] (a) 暂停 AR Session + 暂停 LiveKit 推流（resume 后等 `SessionTracking` 再恢复）
    - [ ] (b) 断开 LiveKit Room（resume 后重连）
    - [ ] (c) 先不做，手动重启也行
    我不确定，我觉得有两个模式，1.在后台跑的时候，可以保持摄像头和语音和GeminiLive连接，并通知转换GOSLO现在的处境和状态。2.保持Gemini Live的连接不断，同时断掉视频和语音连接，并通知GOSLO现在的处境 和状态。
    最重要的问题在于怎么让GOSLO理解目前的处境，有没有相应的预设模式，和GOSLO在一些处境下怎么不乱编处境和信息（比如，没法行动却说让我飞过去看看，比如没法看见目前状态却瞎编我看得到等等。）

### D. 鹦鹉放置与交互

14. 首次放置方式：
    - [ ] (a) 用户点击 AR 检测到的平面
    - [ ] (b) 自动选择最大平面
    - [ ] (c) 飞入动画，自动落地
    a吧，就像Minecraft一样没错吧。

15. 第一句话谁先说？（用户开口 vs 鹦鹉主动打招呼）
    打招呼吧，简单的早上好，中午好，下午好，晚上好就不错。

16. 视频上行策略：
    - [ ] (a) 入房即推，全程开
    - [ ] (b) 按需开关（省流量，节省 Gemini 配额）
    - [ ] (c) 当前 1280x720@30fps 是否需要调整？
    可开可关。
    上行视频流只需要一条高质量的，各个模块按需采样，两地的门控还需要真机测试，但需要对门控留有空间和基础测试，比如先完成给Gemini Live 要怎么样最优采样。

### E. 美术与动画

17. 动画制作清单确认：fly / dance / idle / thinking / land / perch — 哪些 P2 必做？

    我在想办法，不知道要用代码复制Minecraft还是手搓。

18. 动画风格：
    - [ ] (a) Minecraft 方块关键帧（用户手工）
    - [ ] (b) Mixamo 现成动画适配
    - [ ] (c) P2 先用程序化动画（`ParrotController.cs` 已有 pulse）过渡
    我想学习Minecraft，但我们其实应该完成更丰富的动作，你用程序写就好，问题是要我先找找Minecraft的动作代码做参考吗？

19. Minecraft 鹦鹉模型当前状态？
    - [ ] (a) 已有，路径: ___
    - [ ] (b) 还在制作
    - [ ] (c) 先用 `GOSLO.glb` (29KB) 过渡
    c就是Minecraft的带骨架3D模型了

20. UI 需求：有 HUD 吗？只有纸条？菜单？设置页？

    这个真的难倒我了，现在的AI设计这些的能力够强吗？
    还是需要我先设计出布局。
    风格我希望极简一点，画面干净一点。
    菜单 包括功能HUD的开关什么的都藏好一点？
    
