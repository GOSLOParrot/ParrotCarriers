# GOSLOParrot 项目技术参考 — 导师查阅版

> 生成日期: 2026-03-06 | 用途: 项目核心技术栈的简要介绍与文档链接

---

## 参考技术一览表

| 技术 | 简介 | 官方文档 | 仓库 | 项目中的用途 |
|:-----|:-----|:---------|:-----|:-------------|
| **LiveKit** | 开源实时音视频通信框架，基于 WebRTC，支持 Room、RPC、DataChannel | [docs.livekit.io](https://docs.livekit.io/) | [livekit/livekit](https://github.com/livekit/livekit) | 通信总线：Unity ↔ 云端 Agent 的音视频、指令、遥测 |
| **LiveKit Agents** | 实时语音/视觉 AI Agent 框架，统一编排 STT/LLM/TTS/VAD | [docs.livekit.io/agents](https://docs.livekit.io/agents/) | [livekit/agents](https://github.com/livekit/agents) | Brain Agent 骨架，Gemini 语音对话、Tool Call 转发 |
| **SVA Vision-Agents** | GetStream 开源视觉 Agent 框架，Processor 模式处理视频流并注入 LLM | [visionagents.ai](https://visionagents.ai/) | [GetStream/Vision-Agents](https://github.com/GetStream/Vision-Agents) | 借鉴 Processor 可插拔架构、上下文注入机制 |
| **Graphiti** | Zep 开源时序知识图谱，支持 Leiden 社区检测、自定义实体 | [help.getzep.com/graphiti](https://help.getzep.com/graphiti/) | [getzep/graphiti](https://github.com/getzep/graphiti) | 长期记忆后端：情景记忆、物体知识、人格分区 |
| **DSG 综述** | 3D 场景图定义、生成与应用的综述 (RiTA 2022, Springer 2023) | [Springer](https://link.springer.com/chapter/10.1007/978-3-031-26889-2_13) | — | 动态场景图概念、分层结构、生成方法综述 |

---

## 简要说明

### LiveKit
实时通信基础设施。提供 Room 模型、WebRTC 音视频、RPC 可靠指令、DataChannel 遥测。我们选用 LiveKit 替代直连 Gemini WebSocket，因其已封装 STT/TTS/VAD 与多端同步。

### SVA Vision-Agents (GetStream)
面向固定摄像头的视觉 Agent 框架。核心是 **Processor**：视频处理器可插拔，分析结果通过事件系统注入 LLM。我们借鉴其 Processor 模式与上下文注入思路，但项目为手持 AR 场景，需自建 DSG 多帧追踪与稳定性门控。

### Graphiti (Zep / GetStream)
实时知识图谱，支持 `group_id` 分区、自定义实体、Leiden 社区检测。用于鹦鹉的长期记忆（情景/物体/人格/词汇），与 L2-B 语义层配合，实现「飞到奶奶的杯子上」等场景理解。

### DSG (Dynamic Scene Graph)
动态场景图，将摄像头画面转为结构化空间与语义表示。参考综述论文 *A Survey on 3D Scene Graphs: Definition, Generation and Application* 的分层与生成范式，在 RustworkX 上自建 L1(视网膜)→L2-A(空间拓扑)→L2-B(语义注意力)→L3(认知接口) 四层仿生架构。

### GetStream
SVA Vision-Agents 与 Graphiti 的出品方，提供实时通信与 AI 相关开源组件。

---

## 快速链接

| 链接 | 说明 |
|:-----|:-----|
| [LiveKit 文档](https://docs.livekit.io/) | 实时通信、自托管部署 |
| [LiveKit Agents](https://docs.livekit.io/agents/) | Agent 开发、Gemini 集成 |
| [SVA Vision-Agents](https://github.com/GetStream/Vision-Agents) | 视觉 Processor 架构 |
| [Graphiti 文档](https://help.getzep.com/graphiti/) | 知识图谱、社区检测 |
| [DSG 综述论文](https://link.springer.com/chapter/10.1007/978-3-031-26889-2_13) | 3D Scene Graphs: Definition, Generation and Application (RiTA 2022) |
