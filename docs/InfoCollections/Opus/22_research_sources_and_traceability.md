# 调研溯源清单 · 关键发现存档

> 生成日期: 2026-02-24
> 用途: 保留所有调研中发现的关键事实和 URL，确保设计决策可溯源
> 原则: 只保留"影响了设计决策的关键发现"，不重复设计文档的内容

---

## 0. 溯源策略

### 为什么需要这个文档

设计文档 (doc 09-19) 中融合了调研结论，但以下信息会丢失：
- 某个设计选择是基于哪篇文档/哪个 API 做出的
- 原始 URL 和版本号 (API 会变)
- 关键的"不能做"发现 (被否决的方案)

### 这个文档保留什么

```
✅ 影响决策的关键发现 + 来源 URL
✅ 被否决的方案和否决原因
✅ API 版本号和关键限制
❌ 不重复设计文档的详细设计
❌ 不保留完整的网页内容
```

### 对话原文在哪

Cursor 自动保存了完整的对话历史 (含所有 WebSearch/WebFetch 结果):
- 文件: `agent-transcripts/b0e6f321-a036-4e88-84d4-7bc332f045dc.jsonl`
- 大小: ~150KB
- 格式: JSONL (每行一个对话/工具调用事件)
- 如需精确溯源某个发现，可在此文件中搜索关键词

---

## 1. LiveKit Agents

### 关键发现

| 发现 | 来源 | 影响了哪个决策 |
|:-----|:-----|:-------------|
| `multimodal-agent-python` 已归档 (2025-10) | [livekit-examples README](https://github.com/livekit-examples/python-agents-examples) | 用 `agent-starter-python` 而非旧模板 |
| AgentSession 统一编排 STT/LLM/TTS/VAD | [docs.livekit.io/agents](https://docs.livekit.io/agents/) | ADR-001: 采用 LiveKit 做 infra |
| `update_chat_ctx()` 可主动注入上下文 | [AgentSession API](https://docs.livekit.io/agents/build/agent-session/) | L3 上下文注入方式 |
| `conversation_item_added` 事件可获取完整对话 | [LiveKit Event 文档](https://docs.livekit.io/agents/) | L3 Observer 时间线设计 |
| `function_tools_executed` 事件可获取 Tool Call 结果 | 同上 | Graphiti 归档来源 |
| DataChannel 支持 Reliable/Unreliable 双模式 | [LiveKit DataChannel](https://docs.livekit.io/home/get-started/data-channels/) | 前后端通信协议设计 |
| LiveKit Unity SDK 支持 WebGL + 原生平台 | [Unity SDK 文档](https://docs.livekit.io/transport/sdk-platforms/unity-web/) | Phase 1 Unity 集成 |

### 被否决的方案

- ❌ 直连 Gemini BidiGenerateContent WebSocket — LiveKit 已封装更好
- ❌ Stream Edge (SVA 的网络层) — 我们用 LiveKit 替代

---

## 2. SVA Vision-Agents

### 关键发现

| 发现 | 来源 | 影响了哪个决策 |
|:-----|:-----|:-------------|
| Processor 模式: 视频处理器可插拔 | [SVA GitHub](https://github.com/GetStream/Vision-Agents) | L1 多处理器架构设计 |
| `attach_agent()` + 事件系统注入 LLM 上下文 | SVA 源码 `vision_agents/core/processors/` | ADR: Context Injection 方式 |
| `gemini.Realtime(fps=3)` 直接传视频帧 | SVA 文档 | Gemini 视频输入方式 |
| YOLO Processor 可独立启停 | SVA YOLO 插件 | L1 处理器按 Tier 启停 |
| SVA 假设固定摄像头 — 不处理运动模糊 | SVA 应用场景分析 | ADR: 需要 StabilityGate |

### 与我们的关键差异

- SVA = 固定摄像头 (三脚架/墙壁)；我们 = 手持手机 (剧烈运动)
- SVA = 单帧检测；我们 = 有状态的 DSG (多帧追踪+图构建)

---

## 3. Spark-DSG / Hydra (MIT-SPARK)

### 关键发现

| 发现 | 来源 | 影响了哪个决策 |
|:-----|:-----|:-------------|
| 节点继承: `NodeAttributes → SemanticNodeAttributes → ObjectNodeAttributes` | [node_attributes.h (C++ header)](https://github.com/MIT-SPARK/Spark-DSG/blob/main/include/spark_dsg/node_attributes.h) | ADR-015: DSG 节点类继承体系 |
| 所有节点共享 `position` 字段 | 同上 | DSGNode 基类必须有位置 |
| `DsgLayers` 枚举分层 (OBJECTS/PLACES/ROOMS/BUILDING) | Spark-DSG Python binding | DSGLayer 枚举设计 |
| `is_active` / `is_predicted` 属性 | node_attributes.h | NodeState 设计灵感 |
| Khronos 扩展增加 `first_observed_ns` / `last_observed_ns` | KhronosObjectAttributes | `created_at` / `last_seen` 字段 |

### 被否决的方案

- ❌ 直接使用 Spark-DSG Python 包 — C++ 依赖太重, 在 RustworkX 上重新实现

---

## 4. ConceptGraphs (ICRA 2024)

### 关键发现

| 发现 | 来源 | 影响了哪个决策 |
|:-----|:-----|:-------------|
| CLIP embedding 多视角融合是核心 | [ConceptGraphs 论文](https://concept-graphs.github.io/) | DINOv2 embedding 存储和融合策略 |
| `class_id` 用多帧投票而非单次检测 | ConceptGraphs 源码 MapObjectList | ADR: LabelBuffer 投票机制 |
| 物体表示: clip_ft + text_ft + pcd + bbox | ConceptGraphs 代码结构 | ObjectNode 字段设计 |
| LLM 推导物体间关系 (而非纯几何推断) | 论文 §3.3 | L2-B 语义关系来源之一 |

### 与我们的关键差异

- ConceptGraphs 有 RGB-D (深度相机)；我们只有 RGB + ARCore 估计深度
- ConceptGraphs 用 CLIP；我们用 DINOv2 (更好的实例区分)
- ConceptGraphs 离线处理；我们需要实时

---

## 5. Graphiti (Zep)

### 关键发现

| 发现 | 来源 | 影响了哪个决策 |
|:-----|:-----|:-------------|
| `group_id` 参数可实现命名空间隔离 | [Graphiti 文档](https://help.getzep.com/graphiti/) | ADR: Graphiti 分区策略 |
| 自定义实体类型用 Pydantic `BaseModel` | [Custom Entity Types 文档](https://help.getzep.com/graphiti/core-concepts/custom-entity-and-edge-types) | ADR-016: Graphiti 自定义实体 |
| 内置 Leiden 社区检测 (`build_communities()`) | [Communities 文档](https://help.getzep.com/graphiti/core-concepts/communities) | 不需要额外引入 Microsoft GraphRAG |
| `search()` 支持三范围: 节点/边/社区 | Graphiti API | L2-B 检索策略 |
| `add_episode()` 是写入的核心接口 | Graphiti API | remember Tool 实现方式 |

---

## 6. ARCore / AR Foundation

### 关键发现

| 发现 | 来源 | 影响了哪个决策 |
|:-----|:-----|:-------------|
| iQOO Neo9 **被 ARCore 官方支持** | [ARCore 支持设备列表](https://developers.google.com/ar/devices) | 设备确认 |
| ARCore Depth API: 单目深度估计, 精度 ±10-30cm | [Depth API 文档](https://developers.google.com/ar/develop/java/depth/quickstart) | 体积估算精度限制 |
| 3D BoundingBox: AR Foundation 6.0 有接口但 ARCore 后端支持有限 | [ARBoundingBoxManager 文档](https://docs.unity3d.com/Packages/com.unity.xr.arfoundation@6.0/manual/) | ADR-012: 三层体积估算 |
| 持久化锚点需要 Google Cloud 授权 | [Persistent Anchors 文档](https://docs.unity3d.com/Packages/com.unity.xr.arcore@6.2/manual/features/anchors/persistent-anchors.html) | 跨会话恢复需要 Cloud 配置 |
| `ARPlane.boundary`: 返回凸多边形顶点 | [ARPlane API](https://docs.unity3d.com/Packages/com.unity.xr.arfoundation@6.4/manual/features/plane-detection/arplane.html) | 鹦鹉运动边界约束 |
| `FeatureMapQuality`: 0/1/2 三级映射质量 | [ARCore Session API](https://developers.google.com/ar/reference/java/com/google/ar/core/Session) | ADR: 锚点创建质量门控 |
| `Scene Semantics`: 像素级语义分割但仅室外 | ARCore 文档 | 室内不可用, 不采用 |
| Unity Input System 传感器: Gyroscope/Accelerometer/MagneticField/Attitude | [Unity Sensor 文档](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.4/manual/Sensors.html) | telemetry 字段设计 |
| `Input.compass.trueHeading`: 罗盘绝对方向 | [Unity Compass API](https://docs.unity3d.com/6000.2/Documentation/ScriptReference/Compass.html) | 方位感知设计 |
| 安卓传感器完整列表: 加速度/陀螺/磁力/气压/光线/接近/计步 | [Android Sensors Overview](https://developer.android.com/develop/sensors-and-location/sensors/sensors_overview) | 传感器审计 |

### 被否决的方案

- ❌ ARCore Geospatial API 用于室内导航 — VPS 基于街景数据, 室内不可用
- ❌ 环境网格 (ARMeshManager) — 安卓无 LiDAR, 网格质量差
- ❌ Scene Semantics — 仅支持室外 11 类语义

---

## 7. OpenTeach (NYU Robot Learning)

### 关键发现

| 发现 | 来源 | 影响了哪个决策 |
|:-----|:-----|:-------------|
| VR 手部 24 个关键点 (`OCULUS_NUM_KEYPOINTS = 24`) | [openteach/constants.py](https://github.com/aadhithya14/Open-Teach/blob/main/openteach/constants.py) | 手势数据维度参考 |
| 坐标系转换用 `palm_normal = cross(index_knuckle, pinky_knuckle)` 建立局部坐标系，再求旋转矩阵 `np.linalg.solve()` | [keypoint_transform.py](https://github.com/aadhithya14/Open-Teach/blob/main/openteach/components/detector/keypoint_transform.py) | Unity 左手系 ↔ Python 右手系 转换策略 |
| 通信层用 ZMQ (PUB/SUB)，VR 端发 `absolute:x,y,z|x,y,z|...` 字符串格式 | [oculus.py](https://github.com/aadhithya14/Open-Teach/blob/main/openteach/components/detector/oculus.py) | 我们改用 LiveKit DataChannel 但数据格式可参考 |
| 移动平均 (`moving_average`, window=5) 做平滑 | [vectorops.py](https://github.com/aadhithya14/Open-Teach/blob/main/openteach/utils/vectorops.py) | PositionBuffer 设计灵感 |
| 频率控制 `FrequencyTimer(VR_FREQ=60)` | openteach/utils/timer.py | 前端遥测频率参考 |
| 组件化架构: Component 基类 → detector / operators / sensors / recorders | openteach/components/ 目录结构 | 模块化设计参考 |

### 与我们的关键差异

- OpenTeach = Meta Quest 3 (VR 手套)；我们 = 安卓手机摄像头 + AR Foundation
- OpenTeach = 双手操控机器人；我们 = 单手握持手机观察鹦鹉
- OpenTeach = ZMQ 直连；我们 = LiveKit DataChannel
- OpenTeach 手部数据来自 VR 控制器；我们来自 XR Hands (摄像头识别)

### XR Hands 数据格式 (Unity AR Foundation)

| 发现 | 来源 |
|:-----|:-----|
| 每只手 **26 个追踪点** (含手腕/掌心/指尖) | [XR Hands 1.6.3 数据模型](https://docs.unity3d.com/Packages/com.unity.xr.hands@1.6/manual/hand-data/xr-hand-data-model.html) |
| `XRHandJoint.TryGetPose()` 返回位置(m) + 旋转(四元数) | [XRHandJoint API](https://docs.unity3d.com/Packages/com.unity.xr.hands@1.6/api/UnityEngine.XR.Hands.XRHandJoint.html) |
| 额外属性: 关节半径、线速度、角速度 | 同上 |
| 手势级数据: Grip/Pinch position+rotation, Poke position | XR Hands 数据模型 |
| Unity 使用**左手坐标系** (Z 正前), Provider 层已转换 | XR Hands 文档 |
| `trackingState` 包含 `WillNeverBeValid` 标记 | XRHandJoint API |

---

## 8. LiveKit Unity SDK (原生 Android)

### 关键发现 — **重大修正**

| 发现 | 来源 | 影响了哪个决策 |
|:-----|:-----|:-------------|
| **`client-sdk-unity` 支持原生 Android/iOS/Windows/macOS/Linux** (不仅是 WebGL!) | [GitHub client-sdk-unity](https://github.com/livekit/client-sdk-unity) | **ADR 修正: 无需用 WebGL SDK** |
| 最新版 v1.3.3 (2024-12), FFI v0.12.43 | [Releases](https://github.com/livekit/client-sdk-unity/releases) | 版本锁定 |
| 连接 API: `room.Connect(url, token)` 返回 IEnumerator | README 示例代码 | Unity 协程集成 |
| 发布摄像头: `CameraVideoSource(Camera.main)` → `PublishTrack()` | README 示例 | AR 视频上传到 LiveKit 服务器 |
| **RPC 支持**: `RegisterRpcMethod()` + `PerformRpc()` | README 示例 | 替代部分 DataChannel 用途 |
| **文本流**: `SendText()` / `StreamText()` 增量式 | README 示例 | 上下文注入的替代方案 |
| **字节流**: `SendFile()` / `StreamBytes()` | README 示例 | AR 数据传输 |
| 数据接收: `room.DataReceived += (data, participant, kind) => ...` | README 示例 | 事件驱动接收 |
| Reliable (有序, 最大 15KB) / Lossy (无序, 推荐 1300B) | [Data packets 文档](https://docs.livekit.io/home/client/data/packets) | telemetry 用 Lossy, commands 用 Reliable |

### 原有认知的修正

- ❌ 旧认知: "LiveKit Unity SDK 只支持 WebGL" → ✅ 实际: `client-sdk-unity` 支持**所有平台**包括原生 Android
- ❌ 旧认知: "需要 WebGL 版做前端" → ✅ 实际: 原生 SDK 功能更丰富(RPC, 文本流, 字节流)
- 这意味着我们可以直接在 Unity Android 原生构建中使用 LiveKit SDK，**不需要 WebGL 桥接**

### 示例仓库

- [livekit-examples/unity-example](https://github.com/livekit-examples/unity-example) — 官方 Unity 示例
- [livekit-examples/vision-demo](https://github.com/livekit-examples/vision-demo) — iOS 前端 + Python 后端 Gemini 视觉

---

## 9. py-trees 行为树

### 关键发现

| 发现 | 来源 | 影响了哪个决策 |
|:-----|:-----|:-------------|
| 三种核心 Composite: Selector(优先级) / Sequence(顺序) / Parallel(并发) | [Composites 文档](https://py-trees.readthedocs.io/en/devel/composites.html) | ADR: 后端调度器用行为树 |
| Selector `memory=True`: 锁定正在运行的分支, 不会被低优先级打断 | Composites 文档 | 高优先级任务中断设计 |
| Selector `memory=False`: 每次 tick 从头评估, 高优先级可抢占 | 同上 | 安全检查类行为用无记忆 Selector |
| Parallel 策略: `SuccessOnAll` / `SuccessOnOne` / `SuccessOnSelected` | Composites 文档 | 并发任务完成条件 |
| **Blackboard**: key-value 存储, Client 注册 READ/WRITE 权限 | [Blackboard 文档](https://py-trees.readthedocs.io/en/devel/blackboards.html) | 行为间数据共享机制 |
| Decorator 修饰器: Timeout / Retry / OneShot / EternalGuard / StatusToBlackboard | [Decorators 文档](https://py-trees.readthedocs.io/en/devel/decorators.html) | 超时/重试/条件守卫 |
| **"永远不需要创建新的 Composite 子类"** — 仅用 5 种元素组合 | Composites 文档 Philosophy | 避免过度设计 |
| 当前版本 2.4.0, Python 3.9+, 2025 新增 `ForEach` 装饰器 | [PyPI py-trees](https://pypi.org/project/py-trees/) | 版本确认 |
| ROS 集成: `py_trees_ros` 前端数据采集 → Blackboard → 行为树 | [ROS Tutorial](http://docs.ros.org/en/melodic/api/py_trees_ros/html/tutorials.html) | 传感器 → Blackboard → 决策的模式 |

### 对我们架构的影响

```
已确认 py-trees 可以满足我们的调度器需求:
  - Selector(memory=False) → 安全/健康检查 (每 tick 重评估)
  - Sequence(memory=True) → 多步骤任务 (fly_to → land → animate)
  - Parallel(SuccessOnAll) → 飞行 + 说话同时进行
  - Blackboard → DSG 状态共享
  - Decorator.Timeout → 防止任务卡死
```

---

## 10. OpenClaw SOUL 系统

### 关键发现

| 发现 | 来源 | 影响了哪个决策 |
|:-----|:-----|:-------------|
| SOUL.md 是纯 Markdown, 存在 `~/.openclaw/workspaces/[agent]/SOUL.md` | [OpenClaw 文档](https://docs.openclaw.ai/reference/templates/SOUL) | ParrotSoul 文件格式 |
| 5 个文件组成人格: SOUL.md → IDENTITY.md → USER.md → CLAUDE.md → TOOLS.md | [指南](https://www.thecaio.ai/blog/openclaw-system-prompt-guide) | 我们只需 1 个 SOUL + Graphiti 动态部分 |
| 核心哲学: "有真实观点", "别说'好问题!'", "先自己查再问" | SOUL.md 官方模板 | 鹦鹉人格设计原则 |
| 文件每次会话启动时注入 system prompt ("读自己醒来") | [OpenClaw 解释](https://openclawsoul.org/what-is-openclaw-soul.html) | Gemini instructions 注入方式 |
| souls.directory: 24+ 预制人格模板 (技术/专业/玩耍/健康) | [souls.directory](https://souls.directory/) | 可参考已有模板 |
| "Continuity" 段落: 文件是记忆, 读它/更新它 | SOUL.md 模板 | 与 Graphiti 长期记忆的配合 |

### 实际 SOUL.md 模板结构 (已获取原文)

```markdown
# SOUL.md - Who You Are
## Core Truths        ← 核心原则 (帮助/有观点/先自查/挣信任/尊重隐私)
## Boundaries         ← 行为边界 (不代替发言/不发半成品/公开操作先问)
## Vibe               ← 语气风格 (简练/不谄媚/不是机器人)
## Continuity         ← 持续性 (每次读文件醒来/更新要告知用户)
```

---

## 11. 虚拟角色 AI 参考

### Inworld AI Character Brain

| 发现 | 来源 | 影响了哪个决策 |
|:-----|:-----|:-------------|
| 三层架构: Perception(感知) → Cognition(认知) → Expression(表达) | [Character Brain](https://inworld.ai/character-brain) | 与我们 L1→L2→L3 对应 |
| 可配置: personality / knowledge / memories / emotional states | Character Brain 文档 | 鹦鹉人格维度参考 |
| 内置幻觉控制 (hallucination control) | 同上 | Gemini 回复约束 |
| 多角色编排 (multi-character orchestration) | 同上 | 未来多宠物场景 |
| TTS 延迟 < 250ms | Inworld 官网 | 性能基准参考 |

### Livia: 情感感知 AR 伙伴 (2025 论文) — **新发现, 高度相关**

| 发现 | 来源 | 影响 |
|:-----|:-----|:-----|
| **模块化 AI 代理**: 情感分析 / 对话生成 / 记忆管理 / 行为编排 | [arXiv:2509.05298](https://arxiv.org/abs/2509.05298) | 与我们 Observer 拆分非常相似 |
| **Temporal Binary Compression (TBC)**: 渐进式时间压缩长期记忆 | 同上 | Graphiti 归档策略参考 |
| **Dynamic Importance Memory Filter (DIMF)**: 动态重要性过滤 | 同上 | L2-B 注意力机制参考 |
| 用户评估: 统计显著降低孤独感, 提升情感联系 | 同上 | 证明方向可行 |
| 自适应人格进化 + 真实感 AR 具身 | 同上 | 与 ParrotSoul 进化对应 |

### Niantic Spatial × Hume AI: Project Jade

| 发现 | 来源 | 影响 |
|:-----|:-----|:-----|
| 第一人称视角 + VPS 厘米级定位 + 大地理空间模型 | [Niantic Blog](https://www.nianticspatial.com/blog/ai-location-peridot) | AR 场景理解的商业级方案参考 |
| Hume AI Empathic Voice Interface: 情感智能语音 | [Hume AI 案例](https://www.hume.ai/blog/case-study-hume-niantic) | 语音交互的情感维度 |
| 伙伴名 "Dot", 跑在 Snap Spectacles 上 | AWE 2025 演示 | 竞品分析 |

### Reachy Mini Conversation App

| 发现 | 来源 | 影响 |
|:-----|:-----|:-----|
| OpenAI Realtime API + fastrtc 低延迟音频循环 | [GitHub](https://github.com/pollen-robotics/reachy_mini_conversation_app) | LiveKit 替代 fastrtc 的对照 |
| 分层运动系统: 主动作队列 + 语音反应 wobble 混合 | 同上 | 鹦鹉动画分层设计参考 |
| 可选本地视觉 (SmolVLM2) 或云端 (GPT) | 同上 | 我们的 L1 本地 vs 云端策略 |
| YOLO + MediaPipe 作为可选视觉插件 | 同上 | 视觉处理器可插拔的佐证 |

### Google DeepMind SIMA 2

| 发现 | 来源 | 影响 |
|:-----|:-----|:-----|
| 通用具身代理, 能推理/对话/自主学习 | [arXiv:2512.04797](https://arxiv.org/html/2512.04797) | 长期方向参考 |

---

## 12. 游戏 AI 行为树实践

### 关键发现

| 发现 | 来源 | 影响 |
|:-----|:-----|:-----|
| 行为树是游戏 AI 工业标准 (Halo, The Last of Us) | [GeneralistProgrammer 教程](https://generalistprogrammer.com/tutorials/game-ai-behavior-trees-complete-implementation-tutorial) | 确认技术选型正确 |
| 三层节点: Composite → Decorator → Leaf (Task/Condition) | 同上 | py-trees 对应 |
| 每帧从根到叶评估, 紧急动作通过树结构优先级中断 | 同上 | 我们的 tick 频率需要设计 |
| Unity 开源 BT: [kietran99/BehaviorTree](https://github.com/kietran99/BehaviorTree) (99★, 可视化编辑器) | GitHub | 前端参考 (如果需要) |
| Unity 开源 BT: [Sterberino/open-behavior-trees](https://github.com/Sterberino/open-behavior-trees) | GitHub | 前端参考 |

---

## 13. Zep × LiveKit 集成 (Graphiti 记忆)

### 关键发现 — **新增重要发现**

| 发现 | 来源 | 影响了哪个决策 |
|:-----|:-----|:-------------|
| **`zep-livekit` 官方包**: `ZepUserAgent` + `ZepGraphAgent` 直接在 LiveKit Agent 中使用 Graphiti | [Zep 文档](https://help.getzep.com/livekit-memory) | **ADR 新增: 可直接用官方集成** |
| `ZepGraphAgent` 支持自定义实体模型 + `search_filters` + `facts_limit` | 同上 | Graphiti 集成方式 |
| 安装: `pip install zep-livekit zep-cloud "livekit-agents[openai,silero]>=1.0.0"` | 同上 | 依赖确认 |
| Room-based memory isolation: 每个 Room 一个隔离的记忆上下文 | 同上 | 与 `group_id` 分区配合 |
| P95 检索延迟 < 250ms | [Zep Blog](https://blog.getzep.com/zep-livekit/) | 实时性确认 |
| 自动捕获语音对话 turn → Graphiti | Zep 文档 | 减少手动 Graphiti 写入代码 |

### 对架构的影响

这个发现意味着我们可能**不需要完全自建 Graphiti 归档管线** — Zep 官方已经提供了 LiveKit Agent ↔ Graphiti 的集成包。`ZepGraphAgent` 已经实现了:
1. 自定义实体类型 (Pydantic)
2. 自动对话记忆
3. 结构化知识检索
4. Room 级隔离

我们需要评估是直接用 `zep-livekit` 还是自建 (自建更灵活但工作量大)。

---

## 14. LiveKit 多 Agent 架构

### 关键发现

| 发现 | 来源 | 影响 |
|:-----|:-----|:-----|
| `function_tool` 是 Agent 间通信的推荐方式 | [LiveKit KB](https://kb.livekit.io/articles/9330389701-building-multi-agent-architectures-with-livekit-agents) | Nanobot ↔ 主 Agent 通信 |
| `UserData` 类做无状态上下文传递 | 同上 | Agent 跨调用状态管理 |
| 示例: 医疗分诊 → 多部门路由 → 上下文保持 | [python-agents-examples](https://github.com/livekit-examples/python-agents-examples) | 角色切换参考 |
| 50+ 聚焦 demo + 20+ 生产级应用 | python-agents-examples 仓库 | Phase 1 学习资源 |

---

## 15. Gemini Live Vision Recipe (LiveKit 官方)

### 关键发现

| 发现 | 来源 | 影响 |
|:-----|:-----|:-----|
| 完整的 Gemini 视觉 Agent 只需 ~30 行 Python | [LiveKit Recipe](https://docs.livekit.io/recipes/gemini_live_vision/) | M1 极简实现参考 |
| 模型: `gemini-2.5-flash-native-audio-preview` | 同上 | 模型选择 |
| `proactivity=True`: 模型自主决定何时发言 | 同上 | 鹦鹉主动说话能力 |
| `enable_affective_dialog=True`: 情感对话 | 同上 | 鹦鹉表情/语气 |
| `RoomOptions(video_input=True)` 即可接收视频 | 同上 | 最简视频输入 |
| 视频采样: 说话时 1fps, 静默时 0.3fps | [Vision Demo](https://github.com/livekit-examples/vision-demo) | 带宽优化参考 |

### 示例代码 (已获取完整源码)

```python
class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful voice AI assistant...")

session = AgentSession(
    llm=google.beta.realtime.RealtimeModel(
        model="gemini-2.5-flash-native-audio-preview-12-2025",
        proactivity=True,
        enable_affective_dialog=True
    ),
    vad=ctx.proc.userdata["vad"],
)
await session.start(room=ctx.room, agent=Assistant(),
    room_options=room_io.RoomOptions(video_input=True))
```

---

## 16. 新发现的相关项目与教程

### AR 宠物类项目

| 项目 | 内容 | URL | 相关度 |
|:-----|:-----|:----|:-------|
| **Augpets** (UWB-ARSandbox) | 多人 AR 宠物游戏, AR Foundation + 行为系统 | [项目页](https://seanmiles.dev/projects/augpets) | 高 — 宠物行为 + 平面交互 |
| **MIT-RH-2/ARPet** | Unity AR 宠物, QCAR 集成 | [GitHub](https://github.com/MIT-RH-2/ARPet) | 中 — 基础参考 |
| **Auki Labs AR Pet** | 1.5h 教程, 手势追踪 + 宠物生成 + 交互 | [教程](https://aukilabs.com/posemesh/learn/lesson/lesson/interactive-ar-pet) | 中 — 手势交互参考 |

### LiveKit 视觉/多模态教程

| 资源 | 内容 | URL |
|:-----|:-----|:----|
| **Gemini Live Vision Recipe** | 30 行实现视觉 Agent | [LiveKit Docs](https://docs.livekit.io/recipes/gemini_live_vision/) |
| **Vision Demo** | iOS + Python Gemini 视觉完整示例 | [GitHub](https://github.com/livekit-examples/vision-demo) |
| **50+ Python 示例** | 从入门到生产级多 Agent | [GitHub](https://github.com/livekit-examples/python-agents-examples) |
| **Multi-Agent KB** | LiveKit 多 Agent 架构最佳实践 | [KB Article](https://kb.livekit.io/articles/9330389701-building-multi-agent-architectures-with-livekit-agents) |
| **视频教程** | 构建实时多模态 AI 助手 | [YouTube](https://www.youtube.com/watch?v=_0PcGMxw_Hs) |

### Graphiti 集成教程

| 资源 | 内容 | URL |
|:-----|:-----|:----|
| **Zep × LiveKit 集成** | 官方语音 Agent + 持久记忆 | [Zep Docs](https://help.getzep.com/livekit-memory) |
| **Zep × LangGraph** | Graphiti + LangGraph Agent | [Zep Docs](https://help.getzep.com/graphiti/integrations/lang-graph-agent) |
| **Graphiti 介绍博客** | 实时知识图谱概念 | [Medium](https://medium.com/@sajidreshmi94/real-time-knowledge-graphs-for-ai-agents-using-graphiti-131df80e4063) |

---

## 17. 其他参考 (概念级)

| 项目 | 借鉴了什么 | 来源 | 深度 |
|:-----|:----------|:-----|:-----|
| **Microsoft GraphRAG** | Leiden 层次化社区检测概念 | [GitHub](https://github.com/microsoft/graphrag) | 中 — 确认 Graphiti 已内置 |
| **FROSS** | 3D 高斯位置不确定性概念 | [论文](https://arxiv.org/abs/2507.19993) | 浅 — 取概念 |
| **3DSSG (Stanford)** | 空间关系类型定义 | 论文引用 | 浅 — 取关系枚举 |
| **AirLoc** | 物体级室内重定位 | [论文](https://sairlab.org/airloc/) | 浅 — 了解可行性 |
| **Roboflow/Supervision** | Zone 检测几何过滤 | [GitHub](https://github.com/roboflow/supervision) | 浅 |
| **CrewAI** | 多 Agent 协作概念 | 提及 | 极浅 |

---

## 18. 待拉取的参考仓库 (Phase 1 启动时)

进入新项目时，以下仓库值得 clone 到 `reference/` 目录:

```bash
# P0: Phase 1 必须
git clone --depth 1 https://github.com/livekit/agents.git reference/livekit-agents
git clone --depth 1 https://github.com/livekit-examples/python-agents-examples.git reference/livekit-examples
git clone --depth 1 https://github.com/livekit/client-sdk-unity.git reference/livekit-unity-sdk

# P1: Phase 2 前拉取
git clone --depth 1 https://github.com/GetStream/Vision-Agents.git reference/vision-agents
git clone --depth 1 https://github.com/getzep/graphiti.git reference/graphiti
git clone --depth 1 https://github.com/aadhithya14/Open-Teach.git reference/openteach
git clone --depth 1 https://github.com/pollen-robotics/reachy_mini_conversation_app.git reference/reachy-mini
git clone --depth 1 https://github.com/livekit-examples/agents-example-unity.git reference/agents-example-unity
git clone --depth 1 https://github.com/getzep/zep.git reference/zep  # 含 zep-livekit 源码

# P2: 需要时再拉
git clone --depth 1 https://github.com/MIT-SPARK/Spark-DSG.git reference/spark-dsg
git clone --depth 1 https://github.com/concept-graphs/concept-graphs.git reference/concept-graphs
git clone --depth 1 https://github.com/spooky-npc/py-trees.git reference/py-trees
```

**用 `--depth 1` 浅克隆节省空间。** 这些仓库将作为:
1. Cursor Skill Seeker 的输入源
2. 代码实现时的参考
3. 设计决策的可溯源依据

---

## 20. Zep-LiveKit 深度适配分析

### 架构层次

```
zep-livekit v0.1.0 (2025-08-27)
  ├── ZepUserAgent (会话记忆 — Thread-based)
  │   └── 自动: add_messages → get_user_context → 注入 system prompt
  ├── ZepGraphAgent (知识图谱记忆 — Graph-based)
  │   └── 手动: search(query, group_id) → facts/entities/episodes → 注入 context
  └── 底层: zep-cloud ≥3.4.3 (Zep Cloud API) 或 graphiti (自托管)
```

### 关键限制与隐藏点

| 点 | 发现 | 来源 | 对我们的影响 |
|:---|:-----|:-----|:-----------|
| **zep-cloud 依赖** | zep-livekit 依赖 `zep-cloud` SDK (Zep Cloud API) | [PyPI](https://pypi.org/project/zep-livekit/) | 直接用 = 必须用 Zep Cloud |
| **Zep CE 已废弃** | Zep Community Edition (自托管) 已停止支持 | [FAQ](https://help.getzep.com/faq) | **不能用 Zep CE 自托管** |
| **Graphiti 独立可用** | Graphiti 是独立开源项目 (Apache 2.0), 可自托管 | [Graphiti GitHub](https://github.com/getzep/graphiti) | 可绕过 Zep Cloud |
| **单类型分类** | 每个节点/边只能归属一个类型, 不支持多类型 | [自定义实体文档](https://help.getzep.com/v2/customizing-graph-structure) | 节点类型设计需精确 |
| **group_id 隔离** | 完全隔离, 跨 namespace 需多次查询 | [Namespacing 文档](https://help.getzep.com/graphiti/core-concepts/graph-namespacing) | 符合我们的分区需求 |
| **v0.1.0 成熟度** | 包仅 v0.1.0, 下载量极低 (月 ~200) | PyPI 统计 | 生产风险, 但可阅读源码改造 |

### 多角色归档需求适配

```
需求: 鹦鹉/管家/研究者 等角色各自的记忆需独立但可交叉查询

方案 A: Zep Cloud (直接用 zep-livekit)
  ✅ ZepUserAgent 自动对话记忆 (零代码)
  ✅ group_id 分区 (每角色一个 namespace)
  ❌ 依赖 Zep Cloud (付费, 数据不在本地)
  ❌ 包不成熟 (v0.1.0)
  ❌ 自定义 DSG→Graphiti 同步仍需自建

方案 B: Graphiti 自托管 (绕过 zep-livekit)
  ✅ 完全自主控制
  ✅ Apache 2.0 开源
  ✅ 支持 Neo4j / OpenAI / Gemini / Anthropic
  ✅ group_id 同样可用
  ❌ 需自建 LiveKit ↔ Graphiti 桥接代码
  ❌ 需自建 user/thread 管理
  ❌ 需自己运维 Neo4j

方案 C: 混合 (后期评估)
  Phase 3+: 如果 Zep Cloud 提供了自托管不具备的关键能力再考虑
```

### 决策 (ADR-030)

**方案 B (Graphiti 自托管)**, 理由:
1. **数据主权**: 所有记忆数据自己持有, 不放第三方云 (Zep Cloud 是黑盒)
2. **可视化+编辑**: Neo4j Browser (localhost:7474) 直接查看/编辑图谱, 后续可建管理控制台
3. **成熟度**: Graphiti 22k+ stars, Apache 2.0
4. **多角色**: `group_id` 原生支持命名空间隔离
5. **参考价值**: zep-livekit 源码可作为 "怎么在 LiveKit Agent 中集成记忆" 的模板

---

## 21. LiveKit Tool Forwarding (Agent→Unity RPC)

### 关键发现 — **对架构影响极大**

| 发现 | 来源 | 影响 |
|:-----|:-----|:-----|
| `@function_tool` + `perform_rpc()` = Gemini Tool Call 直接转发到 Unity 前端 | [Tool 文档](https://docs.livekit.io/agents/build/tools/) | **fly_to / describe_object 等 Tool 的实现方式** |
| Agent 端: `room.local_participant.perform_rpc(destination, method, payload)` | RPC 文档 | Python Agent → Unity C# |
| Unity 端: `room.RegisterRpcMethod("fly_to", handler)` | [client-sdk-unity](https://github.com/livekit/client-sdk-unity) | Unity 注册处理器 |
| Payload 格式: JSON 字符串, 最大 15KB | RPC 文档 | 足够传 DSG 命令 |
| 支持超时和错误码 | RPC 文档 | 异常处理 |
| **官方 Unity Agent 示例** | [agents-example-unity](https://github.com/livekit-examples/agents-example-unity) | 完整参考 |

### 这意味着什么

我们之前设计的 `fly_to` / `describe_object` / `focus_on` 等 Gemini Tool:

```
旧设计: Gemini → Tool Call → Python Agent 处理 → DataChannel JSON → Unity 解析执行
新发现: Gemini → Tool Call → @function_tool → perform_rpc("fly_to", payload) → Unity handler
```

**RPC 是 LiveKit 原生支持的模式**, 比我们手动设计 DataChannel JSON 协议更干净:
- 有类型安全 (method name + payload)
- 有超时控制 (response_timeout)
- 有错误处理 (RpcError codes)
- 有双向返回值 (Unity 可返回执行结果给 Agent)

---

## 22. Livia 论文详细分析

> arXiv:2509.05298, UC Berkeley + NYU, 2025-08
> 完整论文已获取并阅读, 关键内容摘录如下

### 与我们项目的对照表

| 维度 | Livia | 我们的 AR 鹦鹉 | 差异 |
|:-----|:------|:------------|:-----|
| **目标** | 情感支持伙伴, 减轻孤独 | 互动伴侣 + 空间感知 | 我们更偏空间交互 |
| **前端** | Unity + ARKit (iOS) | Unity + ARCore (Android) | 平台不同 |
| **Agent 架构** | 4 专用 Agent (情感/对话/记忆/编排) | 4 层 DSG + Observer | 我们更重空间感知 |
| **记忆** | SQLite + TBC/DIMF | Graphiti + group_id | 我们更重知识图谱 |
| **情感** | RoBERTa + CNN-LSTM (文本+语音) | Gemini 内置 (affective_dialog) | 我们更轻量 |
| **人格** | 3 元素 (Fire/Water/Earth) | SOUL.md + BehaviorMode | 我们更灵活 |
| **AR** | Blender + ARKit, 表情同步 | AR Foundation + ARCore | 类似 |
| **通信** | 未明确 | LiveKit (WebRTC) | 我们有实时音视频通道 |

### 值得借鉴的核心技术

**1. Temporal Binary Compression (TBC)**
- 按指数时间窗口分层压缩: 最近保留细节, 越老越粗
- Epoch 定义: 日→周→月, 每层内 pairwise summarization
- 结果: 50KB → 15KB, 重要事件召回 92%

**对我们**: Graphiti 的 `add_episode()` + Leiden 社区检测已有类似效果, 但 TBC 的"层级时间窗"概念可用于 Archive Observer 的归档策略 — 比如最近 1 小时的对话逐条归档, 1 天前的合并为摘要, 1 周前的只保留关键事实。

**2. Dynamic Importance Memory Filter (DIMF)**
- 每条记忆一个 importance score (情感强度 + 用户反馈 + 上下文独特性)
- 定期修剪低分记忆
- 用户可纠正 ("别忘了这个!")

**对我们**: 与 L2-B 的注意力机制 (novelty_gain / habituation_decay) 高度对应。DIMF 的"用户反馈集成"是我们没设计的 — 如果鹦鹉要忘记什么, 用户说"别忘"就能保留。

**⚠️ 总体评价**: Livia 本质是"戴了 AR 帽子的聊天机器人" — AR 仅用于展示, 不理解场景/物体/空间关系。
与我们的根本区别: Livia 的 AR 是**展示层** (好看但不理解世界), 我们的 AR 是**感知层** (DSG 在构建世界模型)。
参考价值: 记忆管理 (TBC/DIMF) + 评估方法 (50人/4周) >> 架构本身。

**3. Behavior Orchestration Agent**
- 混合模型: 显式规则 + 强化学习 (用户反馈)
- 基于情感状态/历史/参与策略 主动触发交互
- 语气/礼貌分类器 确保对话质量

**对我们**: 对应我们的 L3 + 行为树。"基于情感主动触发"与我们的 `proactivity=True` 对应。

**4. 评估方法**
- 50 用户, 200 条对话, 2 独立标注者 (Cohen's κ = 0.82)
- 38 人 4 周纵向跟踪, 日均 7.9 次对话 × 4.8 分钟
- 量化: 情感识别 88%, 加语音后焦虑识别 92%
- 质性: "Livia felt like a real friend who actually remembers what I said yesterday"

**对我们**: 未来做用户测试时, 这套评估框架可直接参考。

---

## 23. 新发现的教程与资源 (本轮补充)

| 资源 | 内容 | URL | 相关度 |
|:-----|:-----|:----|:-------|
| **agents-example-unity** | LiveKit Agent + Unity 官方完整示例 | [GitHub](https://github.com/livekit-examples/agents-example-unity) | **极高** — Phase 1 起步模板 |
| **LiveKit Tool Forwarding 文档** | Agent Tool Call → 前端 RPC | [Docs](https://docs.livekit.io/agents/build/tools/) | **极高** — fly_to 实现方式 |
| **LiveKit RPC 文档** | 双向 RPC 完整 API | [Docs](https://docs.livekit.io/home/client/data/rpc) | **极高** — 前后端通信 |
| **Unity AR 平面放置教程** | AR Foundation 基础 | [Unity Learn](https://learn.unity.com/tutorial/placing-an-object-on-a-plane-in-ar) | 高 — 鹦鹉放置 |
| **AR 平面检测配置教程** | AR Foundation + ARCore 设置 | [Unity Learn](https://learn.unity.com/tutorial/configuring-plane-detection-for-ar-foundation) | 高 — 环境设置 |
| **Graphiti Namespacing 文档** | group_id 完整 API 和示例 | [Docs](https://help.getzep.com/graphiti/core-concepts/graph-namespacing) | 高 — 记忆分区 |
| **Graphiti 自托管 Docker 教程** | Neo4j + Graphiti Docker Compose | [GuardKit](https://guardkit.ai/setup/graphiti-setup/) | 高 — 部署方式 |
| **Gemini Playground** | Gemini Live API 完整参考实现 | [GitHub](https://github.com/livekit-examples/gemini-playground) | 中 — Gemini 调试 |

---

## 24. 溯源查找指南

如果你需要找到某个设计决策的原始依据:

```
1. 先看本文档 (22) — 找到对应的"关键发现"和 URL
2. 如果需要更多细节 — 看对应的设计文档 (doc 09-19)
3. 如果需要原始对话 — 搜索 agent-transcripts/*.jsonl
4. 如果需要源码 — 拉取 reference/ 仓库查看
```
