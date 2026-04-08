# 学习项目清单 · 从 Opus 蒸馏

> 生成日期: 2026-02-28  
> 来源: docs/InfoCollections/Opus/ 全部文档  
> 用途: 按关键词分类，明确学习内容、原因、专注点

---

## 一、额度刷新时间说明

**Cursor 额度**：按**首次设置计划的日期**每月重置，非自然月。

- 查看方式：访问 [cursor.com/settings](https://cursor.com/settings) → 左侧 **Usage** 面板
- 可查看：本月快速/慢速请求用量、**下次重置日期**
- 未用完的额度**不会累积**到下月

---

## 二、学习项目总表（按类别）

### 2.1 总线骨架（Phase 1 必学）

| 项目 | 仓库/路径 | 学习内容 | 原因 | 专注关键词 |
|:-----|:----------|:---------|:-----|:-----------|
| **agent-starter-python** | livekit-examples/agent-starter-python | 完整语音 Agent 模板、console 模式、LiveKit Cloud 集成 | **P0 最高**：可直接跑，总线骨架起点 | `agent.py` `console` `download-files` |
| **LiveKit Agents** | livekit/agents | AgentSession 编排、STT/LLM/TTS/VAD、Room 模型、事件监听 | 总线核心框架 | `AgentSession` `Room` `event` |
| **python-agents-examples** | livekit-examples/python-agents-examples | 50+ demo、Tool Calling、RPC、多 Agent、Gemini Live Vision | Phase 1 起步模板 | `tool_calling` `rpc` `gemini_live_vision` |
| **agents-example-unity** | livekit-examples/agents-example-unity | Unity + Agent 完整示例、RPC 注册、DataChannel | 3D+摄像头→需改造为 AR | `RegisterRpcMethod` `DataChannel` `Unity` |
| **client-sdk-unity** | livekit/client-sdk-unity | 原生 Android/iOS、RPC、VideoTrack、DataChannel Lossy/Reliable | Unity 客户端集成 | `PublishTrack` `PerformRpc` `Lossy` |
| **vision-demo** | livekit-examples/vision-demo | iOS + Python Gemini 视觉、视频采样 1fps/0.3fps | 带宽优化、视觉 Agent 参考 | `video_input` `fps` |
| **multimodal-agent** | (已归档 2025-10) | — | ❌ 不推荐，用 agent-starter-python | — |
| **gemini_live_vision** | python-agents-examples/docs/examples/gemini_live_vision | 30 行实现视觉 Agent、video_input、proactivity | 极简视觉 Agent 参考 | `video_input` `RoomOptions` |
| **Vision Agent (Grok)** | python-agents-examples/complex-agents/vision | 摄像头视觉、Grok-2 Vision | 多模态视觉参考 | `vision` `camera` |

### 2.2 视觉与 Processor（Phase 3 / DSG）

| 项目 | 仓库/路径 | 学习内容 | 原因 | 专注关键词 |
|:-----|:----------|:---------|:-----|:-----------|
| **SVA Vision-Agents** | GetStream/Vision-Agents | Processor 模式、`attach_agent` 状态注入、Gemini Realtime、YOLO 插件 | DSG 作为复合 Processor 的参考 | `VideoProcessor` `attach_agent` `add_frame_handler` |
| **SAM2** | 官方 demo | Promptable 分割、track ID 管理 | L1 tracker 核心 | `track` `segment` |
| **ConceptGraphs** | concept-graphs/concept-graphs | 多视角融合、class_id 投票、LLM 推导关系 | L2-A 节点设计、LabelBuffer | `clip_ft` `MapObjectList` `vote` |
| **Spark-DSG / Hydra** | MIT-SPARK/Spark-DSG, Hydra | 节点继承体系、LayerId 枚举、DsgLayers | L2-A 类继承、DSGLayer | `NodeAttributes` `SemanticNodeAttributes` `DsgLayers` |
| **FROSS** | 论文 arxiv:2507.19993 | 3D 高斯位置、不确定性、多视角合并 | position_cov 设计 | `gaussian` `Hellinger` |
| **Roboflow/Supervision** | roboflow/supervision | Zone 检测、几何过滤 | 高层语义过滤 | `Zone` `LineCrossing` |

### 2.3 记忆与图谱（Phase 3）

| 项目 | 仓库/路径 | 学习内容 | 原因 | 专注关键词 |
|:-----|:----------|:---------|:-----|:-----------|
| **Graphiti** | getzep/graphiti | Custom Entity、group_id、build_communities、add_episode | L2-B 后端、5 分区 | `group_id` `add_episode` `build_communities` |
| **zep-livekit** | getzep/zep (含 zep-livekit) | ZepUserAgent、ZepGraphAgent、LiveKit 集成 | 参考集成方式，我们自托管 | `ZepGraphAgent` `RoomOptions` |
| **Microsoft GraphRAG** | microsoft/graphrag | Leiden 社区、层次化摘要 | 概念参考，Graphiti 已内置 | `cluster` `community` |

### 2.4 AR 与手势（Phase 2）

| 项目 | 仓库/路径 | 学习内容 | 原因 | 专注关键词 |
|:-----|:----------|:---------|:-----|:-----------|
| **OpenTeach** | aadhithya14/Open-Teach | 坐标系转换、手势 24 关键点、ZMQ 数据格式、moving_average | Unity↔Python 坐标、PositionBuffer | `keypoint_transform` `palm_normal` `moving_average` |
| **AR Foundation / ARCore** | Unity 文档 | Plane、Anchor、Depth、Compass、FeatureMapQuality | L1 StabilityGate、场景管理 | `ARPlane` `TrackingState` `FeatureMapQuality` |
| **XR Hands** | Unity XR Hands | 26 关节、TryGetPose、Grip/Pinch | 手势遥测格式 | `XRHandJoint` `trackingState` |

### 2.5 调度与行为（Phase 2–3）

| 项目 | 仓库/路径 | 学习内容 | 原因 | 专注关键词 |
|:-----|:----------|:---------|:-----|:-----------|
| **py-trees** | spooky-npc/py-trees | Selector/Sequence/Parallel、Blackboard、Decorator | 后端调度器 | `Selector` `memory` `Blackboard` |
| **FlexBE** | ROS | OBE/OCS 分离、分层状态机 | 前后端职责分离 | `OBE` `OCS` |
| **Gabriel Gambetta** | 教程 | 权威服务器 + 客户端预测 | 前后端同步 | `authoritative` `prediction` |
| **Halo AI / The Sims** | 游戏 AI | 优先级中断、Utility AI | 行为树优先级设计 | `priority` `interrupt` |

### 2.6 人格与多角色

| 项目 | 仓库/路径 | 学习内容 | 原因 | 专注关键词 |
|:-----|:----------|:---------|:-----|:-----------|
| **OpenClaw SOUL** | SOUL.md 模板 | 核心原则、边界、语气、持续性 | ParrotSoul 设计 | `SOUL.md` `Continuity` |
| **Inworld Director** | Inworld AI | 编排者不参与内容生成 | L3 设计原则 | `Director` `orchestration` |
| **Livia** | arXiv:2509.05298 | TBC 时间窗、DIMF 重要性过滤、评估框架 | 记忆归档、用户反馈 | `TBC` `DIMF` `evaluation` |

### 2.7 其他参考

| 项目 | 仓库/路径 | 学习内容 | 原因 | 专注关键词 |
|:-----|:----------|:---------|:-----|:-----------|
| **reachy_mini_conversation** | pollen-robotics/reachy_mini_conversation_app | 分层运动、语音反应、YOLO+MediaPipe | 动画分层、视觉可插拔 | `wobble` `SmolVLM` |
| **ARPet / Augpets** | MIT-RH-2/ARPet 等 | AR 宠物行为、平面交互 | 基础参考 | `AR` `pet` |
| **gemini-playground** | livekit-examples/gemini-playground | Gemini Live API 调试 | 开发调试 | `RealtimeModel` |

---

## 三、同一项目多专注点蒸馏

| 项目 | 专注点 A | 专注点 B | 专注点 C |
|:-----|:---------|:---------|:---------|
| **LiveKit** | AgentSession 编排 | RPC + DataChannel 协议 | Unity SDK 原生集成 |
| **SVA** | Processor 帧率控制 | attach_agent 状态注入 | Gemini Realtime 视频输入 |
| **OpenTeach** | 坐标系 palm_normal | 手势数据格式 ZMQ | moving_average 平滑 |
| **Graphiti** | group_id 分区 | Custom Entity Pydantic | build_communities Leiden |
| **Spark-DSG** | 节点继承体系 | DsgLayers 枚举 | Khronos 时间字段 |
| **ConceptGraphs** | 多视角投票 | LLM 推导关系 | clip_ft 等价 DINOv2 |
| **py-trees** | Selector memory | Blackboard 共享 | Parallel SuccessOnAll |

---

## 四、Skill Seekers 拉取优先级

| 优先级 | 仓库 | 拉取关键词 | 作用 |
|:-------|:-----|:-----------|:-----|
| **P0** | livekit-examples/agents-example-unity | `Unity` `Agent` `RPC` `DataChannel` | Phase 1 起步模板，3D→AR 改造 |
| **P0** | livekit-examples/python-agents-examples | `tool_calling` `gemini` `rpc` `multimodal` | 50+ 示例，总线骨架 |
| **P1** | livekit/agents | `AgentSession` `Room` `event` | 核心框架 API |
| **P1** | GetStream/Vision-Agents | `Processor` `VideoProcessor` `attach_agent` | DSG Processor 参考 |
| **P2** | livekit/client-sdk-unity | `PublishTrack` `RegisterRpcMethod` | Unity 客户端 |
| **P2** | getzep/graphiti | `group_id` `add_episode` `build_communities` | 记忆后端 |
