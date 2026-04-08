# 新项目 Cursor Skills 设计

> 生成日期: 2026-02-24
> 用途: 为新项目 `parrot-ar-cloud` 设计 `.cursor/skills/` 的 Skill 文件内容框架

---

## 1. Skills 架构

```
.cursor/skills/
├── livekit-agents/
│   └── SKILL.md          # LiveKit Agent 开发参考
├── sva-processors/
│   └── SKILL.md          # SVA Processor 模式参考
├── gemini-realtime/
│   └── SKILL.md          # Gemini Realtime API 参考
└── ar-mapping/
    └── SKILL.md          # OpenTeach AR 映射参考
```

**与 Rules 的分工**:
- Rules (`.cursor/rules/`): 全局规范、约束、禁止事项 → 声明式、被动匹配
- Skills (`.cursor/skills/`): 领域知识、API 参考、编程模式 → 过程式、按需加载

---

## 2. Skill: livekit-agents

```markdown
# LiveKit Agents 开发参考

当开发 LiveKit Agent 相关功能、配置 AgentSession、处理 Room 事件、
使用 DataChannel 通信时使用此 Skill。

## 核心概念

### AgentSession 创建
AgentSession 是 LiveKit Agent 框架的编排核心：

```python
from livekit.agents import AgentSession
from livekit.plugins import google, silero

session = AgentSession(
    stt="deepgram/nova-3",
    llm="google/gemini-2.5-flash",
    tts="cartesia/sonic-3:...",
    vad=silero.VAD.load(),
)
await session.start(room=ctx.room, participant=ctx.participant)
```

生命周期: Initializing → Starting → Running → Closing

### 工具定义
```python
from livekit.agents import function_tool

@function_tool
async def fly_to_object(target: str) -> str:
    """让鹦鹉飞到指定物体"""
    # 发送指令到 Unity
    return f"正在飞向 {target}"
```

### DataChannel 通信
```python
# 发送数据到 Unity
await room.local_participant.publish_data(
    payload=json.dumps({"cmd": "fly_to", "target": "hand"}).encode(),
    reliable=True,
    topic="commands",
)

# 接收数据
@room.on("data_received")
def on_data(data: bytes, participant, kind):
    msg = json.loads(data.decode())
```

### 事件系统
```python
session.on("user_started_speaking", handler)
session.on("agent_started_speaking", handler)
session.on("tool_call_started", handler)
```

## 关键参考
- 官方文档: https://docs.livekit.io/agents/
- Python 示例库: https://github.com/livekit-examples/python-agents-examples
- Unity SDK: https://github.com/livekit/client-sdk-unity-web
- 本地参考: reference/livekit-agents/ 和 reference/livekit-examples/
```

---

## 3. Skill: sva-processors

```markdown
# SVA Processor 模式参考

当设计视觉处理管线、实现视频帧分析、将检测结果注入 LLM 上下文时使用此 Skill。

## Processor 模式核心

SVA (Stream Vision-Agents) 使用 Processor 作为视觉分析的核心抽象。
我们借鉴其思想，在 LiveKit Agent 框架上实现类似模式。

### SVA 原始 Processor 结构
```python
from vision_agents.core.processors import VideoProcessor

class ObjectDetectionProcessor(VideoProcessor):
    name = "object_detection"

    async def process_video(self, track, participant_id, shared_forwarder=None):
        self._forwarder = shared_forwarder
        self._forwarder.add_frame_handler(self._on_frame, fps=5.0, name="detection")

    async def _on_frame(self, frame):
        detections = self.model.predict(frame)
        # 将检测结果注入 agent 状态
        await self._agent.events.emit("detections_updated", detections)

    def attach_agent(self, agent):
        self._agent = agent
```

### 我们的适配版本
在 LiveKit 框架中，等价实现为:

```python
class VisionProcessor:
    """SVA-inspired video processor for LiveKit Agent"""

    def __init__(self, session: AgentSession):
        self._session = session

    async def process_frame(self, frame) -> dict:
        # 分析帧，返回结构化结果
        detections = await self._run_detection(frame)
        return {"objects": detections, "timestamp": time.time()}

    async def inject_context(self, detections: dict):
        # 将检测结果作为上下文提供给 Gemini 的下一次 turn
        # 替代旧项目的 XML <SCENE_GRAPH_UPDATE> 注入
        context_text = self._format_detections(detections)
        # 通过 session 的上下文变量注入
        self._session.update_context({"scene_state": context_text})
```

### 关键设计原则
1. **帧率分流**: 高帧率(30fps)给追踪，低帧率(1-5fps)给LLM
2. **状态注入而非消息注入**: 更新 agent 的上下文变量，不是发送额外消息
3. **异步非阻塞**: 视觉处理不能阻塞语音管线

## 关键参考
- SVA 文档: https://visionagents.ai/core/processors-core
- SVA GitHub: https://github.com/GetStream/Vision-Agents
- 本地参考: reference/vision-agents/
```

---

## 4. Skill: gemini-realtime

```markdown
# Gemini Realtime API 参考

当配置 Gemini 模型参数、设计 Tool Use、处理音视频流交互时使用此 Skill。

## 通过 LiveKit 使用 Gemini

在新架构中，我们不直接使用 Gemini BidiGenerateContent WebSocket。
而是通过 LiveKit 的 Gemini 插件进行集成。

### 基础配置
```python
from livekit.agents import AgentSession
from livekit.plugins import google

session = AgentSession(
    llm="google/gemini-2.5-flash",
    # 或使用明确的插件配置
    llm=google.LLM(model="gemini-2.5-flash"),
)
```

### 视觉集成
通过 LiveKit Gemini 插件实现视频帧传输:
- 默认采样率可配置 (建议 1-3 fps)
- 自动处理 frame 编码和传输
- 支持 PCM 16-bit 24kHz 音频流

### Tool Use 规范
```python
@function_tool
async def search_memory(query: str) -> str:
    """搜索鹦鹉的记忆库"""
    results = await memory_adapter.search(query)
    return json.dumps([r.to_dict() for r in results])

@function_tool
async def control_parrot(action: str, target: str = "") -> str:
    """控制鹦鹉执行动作
    
    Args:
        action: fly_to, land, look_at, dance
        target: 目标物体或位置
    """
    await dispatcher.dispatch_intent(action, target)
    return f"执行: {action} {target}"
```

### 重要注意事项
- Tool Call 会暂停语音生成，产生 0.5-2s 延迟
- 高频动作（表情、嘴型）不应使用 Tool Call，而是通过 DataChannel 旁路控制
- Gemini 只输出意图，不直接控制 Unity 渲染

## 关键参考
- LiveKit Gemini 示例: reference/livekit-examples/docs/examples/gemini_live_vision/
- Gemini Live API Guide: https://ai.google.dev/gemini-api/docs/live-guide
- Gemini Cookbook: https://github.com/google-gemini/cookbook
```

---

## 5. Skill: ar-mapping

```markdown
# AR 映射与手势控制参考

当实现 Unity AR 功能、处理手势数据、设计坐标映射逻辑时使用此 Skill。

## 坐标系转换

### Unity (左手系, Y-up) ↔ Python (右手系, Z-up)
```python
def unity_to_python(pos: tuple) -> tuple:
    """Unity (x, y, z) → Python (x, z, -y)"""
    x, y, z = pos
    return (x, z, -y)

def python_to_unity(pos: tuple) -> tuple:
    """Python (x, y, z) → Unity (x, -z, y)"""
    x, y, z = pos
    return (x, -z, y)
```

## 手势数据格式

### DataChannel 遥测 (Unity → Python, 10Hz)
```json
{
    "type": "telemetry",
    "timestamp": 1708765432.123,
    "hand": {
        "state": "open",
        "palm_position": [0.3, 1.2, 0.5],
        "palm_normal": [0.0, 1.0, 0.0],
        "confidence": 0.95
    },
    "head_pose": {
        "position": [0.0, 1.6, 0.0],
        "rotation": [0.0, 0.0, 0.0, 1.0]
    }
}
```

### 手势分类
| 手势 | DataChannel 值 | 鹦鹉反应 | 路由 |
|:-----|:--------------|:---------|:-----|
| 手掌张开 (Open) | `"state": "open"` | 飞到手上 | Reflex (无LLM) |
| 握拳 (Fist) | `"state": "fist"` | 飞走 | Reflex |
| 指向 (Point) | `"state": "point"` | 看向指向方向 | Reflex |
| 挥手 (Wave) | `"state": "wave"` | 跳舞/互动 | Intent (LLM) |

## 反射指令格式 (Python → Unity)
```json
{
    "type": "reflex_command",
    "action": "fly_to_hand",
    "target_position": [0.3, 1.2, 0.5],
    "urgency": "immediate",
    "ttl_ms": 500
}
```

## 关键参考
- OpenTeach: https://open-teach.github.io/
- LiveKit Unity SDK: https://docs.livekit.io/transport/sdk-platforms/unity-web/
- Unity XR Hands: https://docs.unity3d.com/Packages/com.unity.xr.hands@1.3/
```

---

## 6. Skill 生成策略

### 使用 Skill Seeker 自动生成

在拉取参考仓库后，可以使用 Cursor 的 Skill 生成能力来补充细节：

1. 在 Cursor 中打开 `reference/livekit-agents/` 
2. 让 Agent 阅读关键源码并生成 Skill
3. 手动精炼自动生成的 Skill，删除冗余信息

### 手动精炼原则

- 每个 Skill 文件 < 300 行
- 只保留我们项目实际使用的 API 子集
- 包含正确/错误示例
- 标注参考来源和验证日期
- 随项目演进持续更新
