# 参考项目调研报告

> 生成日期: 2026-02-24
> 用途: 新项目从各学习对象中提炼可借鉴的模式 (Pattern)，而非照搬代码

---

## 1. LiveKit Agents — 基础设施骨架

### 仓库信息
- **核心框架**: https://github.com/livekit/agents (5.9k stars)
- **Python 示例**: https://github.com/livekit-examples/python-agents-examples (249 stars)
- **Unity 示例**: https://github.com/livekit-examples/agents-example-unity
- **文档**: https://docs.livekit.io/agents/

### 核心架构概念

**AgentSession** 是 LiveKit Agents 的编排核心：
```python
session = AgentSession(
    stt="deepgram/nova-3",
    llm="google/gemini-2.5-flash",
    tts="cartesia/sonic-3:...",
    vad=silero.VAD.load(),
)
```

生命周期: `Initializing → Starting → Running → Closing`

### 我们借鉴的 Pattern

| Pattern | 描述 | 用于我们的模块 |
|:--------|:-----|:--------------|
| **AgentSession 编排** | 统一管理 STT/LLM/TTS/VAD 管线 | 语音交互层 |
| **DataChannel 通信** | Reliable/Unreliable 双模数据通道 | Unity ↔ Python 指令传输 |
| **Room-based 架构** | 每个会话一个 Room，参与者模型 | 鹦鹉=Agent Participant |
| **Event-driven 模式** | `on/off/once` 事件监听 | 状态变化通知 |
| **Console 模式** | `python agent.py console` 本地调试 | 开发阶段快速验证 |
| **Tool Calling** | Agent 通过函数工具执行动作 | Gemini Intent → 动作调度 |

### 关键示例

| 示例 | 价值 | 路径 |
|:-----|:-----|:-----|
| Gemini Live Vision | Gemini 实时视觉集成 | `docs/examples/gemini_live_vision/` |
| Tool Calling | 工具调用基础 | `docs/examples/tool_calling/` |
| State Tracking | NPC 状态管理 (rapport system) | `docs/examples/state_tracking/` |
| Agent Transfer | 多 Agent 切换 | `docs/examples/agent_transfer/` |
| RPC State Management | 跨端状态 CRUD | `docs/examples/rpc_agent/` |
| Vision Agent (Grok) | 摄像头视觉 | `complex-agents/vision/` |

### 注意事项
- `multimodal-agent-python` 已于 2025年10月归档，不再推荐
- 推荐使用 `agent-starter-python` 作为新项目起点
- Python 3.10+ 要求

---

## 2. Stream Vision Agents (SVA) — 视觉上下文注入

### 仓库信息
- **GitHub**: https://github.com/GetStream/Vision-Agents (6.1k stars)
- **文档**: https://visionagents.ai/
- **最新版本**: v0.3.6 (2026年2月)

### 核心架构：Processor 模式

SVA 的精髓是 **Processor**——视频/音频处理器，可以分析媒体流并将结果注入 LLM 上下文。

```python
from vision_agents.core.processors import VideoProcessor

class MyVideoProcessor(VideoProcessor):
    name = "my_video_processor"

    async def process_video(self, track, participant_id, shared_forwarder=None):
        self._forwarder = shared_forwarder
        self._forwarder.add_frame_handler(self._on_frame, fps=5.0, name="handler")

    async def _on_frame(self, frame):
        # 分析帧 → 注入状态
        pass

    def attach_agent(self, agent: "Agent"):
        # 注册到 agent 事件系统，实现状态注入
        self._agent = agent
```

### 我们借鉴的 Pattern

| Pattern | 描述 | 替代旧设计 |
|:--------|:-----|:----------|
| **Processor State Injection** | 视觉处理结果通过事件系统注入 LLM | 替代旧 XML `<SCENE_GRAPH_UPDATE>` 注入 |
| **Gemini Realtime 原生集成** | `gemini.Realtime(fps=3)` 直接传视频帧 | 替代旧 `BidiGenerateContent` 手写 WebSocket |
| **YOLO Processor 插件** | 即插即用的 YOLO 姿态/检测处理器 | 替代旧 YOLO-World 手工集成 (YOLO 降级为辅助发现，SAM2为主) |
| **Edge 网络** | Stream Edge 提供 < 30ms 延迟 | 我们用 LiveKit 替代 Stream Edge |
| **会话管理** | 内存/持久化双模式对话存储 | 参考其模式设计记忆系统 |

### 关键实现：上下文注入机制

SVA 的上下文注入通过 Processor 的 `attach_agent()` 事件系统实现：
1. Processor 分析视频帧（如 YOLO 检测人体姿态）
2. 检测结果通过注册的事件系统推送
3. Agent 将处理结果自动融合到 LLM 的下一次 turn 中

### 在 LiveKit 中的等价实现

SVA 使用 Stream Edge 网络，我们使用 LiveKit。在 LiveKit 中，等价的上下文注入方式为：

```python
class ParrotBrain(Agent):
    async def on_user_turn_completed(self, turn_ctx, new_message):
        # 等价于 SVA 的 Processor State Injection
        if self._dsg_processor.has_update():
            scene_summary = self._dsg_processor.get_scene_summary()
            new_message.content.append(f"\n[SCENE_CONTEXT]\n{scene_summary}")
```

或通过 `update_chat_ctx()` 主动注入：
```python
chat_ctx = self.chat_ctx.copy()
chat_ctx.add_message(role="user", content=[scene_update_text])
await self.update_chat_ctx(chat_ctx)
```

### DSG 作为 SVA Processor 的升级

我们的 DSG 不是简单的 SVA Processor (单帧检测)，而是**多阶段有状态复合 Processor**：
- SVA: `VideoFrame → YOLO → detections → inject`
- DSG: `VideoFrame → SAM2+DINOv2(L1) → SpatialGraph(L2-A) ← Graphiti(L2-B) → inject`

**策略**: 借鉴 SVA 的 Processor 思想，但 DSG 的实现复杂度远超 SVA 单帧 Processor。

---

## 3. OpenTeach — AR 手势映射

### 仓库信息
- **主页**: https://open-teach.github.io/
- **GitHub**: https://github.com/NYU-robot-learning/Open-Teach-API
- **控制器**: https://github.com/nyu-robot-learning/openteach-controllers

### 核心能力

- 基于 Meta Quest 3 的 VR/MR 遥操作
- 自然手势追踪 (90Hz)
- 多机器人平台支持
- 38+ 任务验证

### 我们借鉴的 Pattern

| Pattern | 描述 | 用于我们的模块 |
|:--------|:-----|:--------------|
| **坐标系转换** | Unity 左手系 ↔ Python 右手系 | 手势/位姿数据传输 |
| **高频遥测** | 90Hz 手势数据采集 | XR Hands → DataChannel |
| **Redis Pub/Sub** | 控制指令的实时分发 | 反射指令调度 |
| **模块化控制器** | 传感器/执行器分离 | 鹦鹉动画控制与感知分离 |

### 关键差异

OpenTeach 面向精密机器人操控，我们面向 AR 虚拟角色。关键差异：
- 我们不需要力反馈
- 我们的延迟容忍度更高（AR 动画可以插值平滑）
- 我们需要的是手势识别（Open/Close/Point），不是精确的关节角度

---

## 4. 补充参考项目

### YOLO-World (或者更轻量的 YOLOv8/v10)
- **用途**: 视觉 L1 层的辅助发现、哨兵模式 (DSG Sentinel) 的特征匹配与未知物体兜底。
- **定位**: 非主发现路径（主发现路径为 SAM2 全分割），用于补充开放词汇标签或在特定硬件（如笔记本端）提供廉价的特征对比支持。

### MIT-SPARK/Hydra + Spark-DSG — 3D 空间场景图
- **用途**: L2-A 空间拓扑设计的理论参考
- **借鉴**: 分层场景图 (Objects→Surfaces→Zones→Rooms)、增量在线更新
- **GitHub**: https://github.com/MIT-SPARK/Hydra (910 stars)
- **Python 数据结构**: https://github.com/MIT-SPARK/Spark-DSG (`pip install spark-dsg`)
- **注意**: 我们不直接使用 Spark-DSG (C++依赖重)，而是在 RustworkX 上实现其分层理念

### FROSS — 快速实时 3D SSG
- **用途**: L2-A 位置模型的理论参考
- **借鉴**: 用 3D 高斯分布表示物体位置(含不确定性)、增量合并多视角观测
- **论文**: https://arxiv.org/abs/2507.19993 (ICCV 2025)
- **注意**: 需要 RGB-D 输入，我们只取其概念不用其代码

### Graphiti — 时序知识图谱 + Leiden 社区检测
- **用途**: L2-B 语义缓存的持久化后端
- **借鉴**: `build_communities()` Leiden 社区检测、三范围搜索、增量社区更新
- **文档**: https://help.getzep.com/graphiti/core-concepts/communities
- **关键**: 内置的社区检测已覆盖 GraphRAG 的折叠/聚类需求，无需额外引入 Microsoft GraphRAG

### Microsoft GraphRAG — 图增强检索 (概念参考)
- **用途**: 理解 Leiden 层次化社区检测和社区摘要的设计思路
- **借鉴**: 层次化社区 → 摘要 → 检索的管线设计
- **GitHub**: https://github.com/microsoft/graphrag
- **注意**: 面向离线大规模文本分析，不直接使用，Graphiti 已内置等价能力

### Roboflow/Supervision
- **用途**: 几何过滤（判断物体空间关系）
- **借鉴**: Zone 检测、Line Crossing 等高层语义过滤
- **GitHub**: https://github.com/roboflow/supervision

### LiveKit Unity SDK
- **用途**: Unity 客户端 WebRTC 集成
- **借鉴**: Room 连接、DataChannel API、音频处理
- **文档**: https://docs.livekit.io/transport/sdk-platforms/unity-web/

---

## 5. 学习项目映射到 Cursor Skills

每个参考项目应生成对应的 Cursor Skill，供开发时按需引用：

| 参考项目 | Skill 名称 | 内容要点 |
|:---------|:----------|:---------|
| LiveKit Agents | `livekit-agents` | AgentSession API、事件模型、DataChannel 用法 |
| SVA Vision-Agents | `sva-processors` | Processor 模式、Gemini Realtime 集成、状态注入 |
| OpenTeach | `ar-mapping` | 坐标转换、手势数据格式、Redis 通信模式 |
| Gemini API | `gemini-realtime` | Realtime API 参数、Tool Use 规范、音视频格式 |

**建议**: 拉取各仓库后，使用 Skill Seeker 工具自动生成 Skill 骨架，再手工精炼。
