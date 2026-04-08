# 架构图验证报告：new.md vs LiveKit 技术文档 & SVA 最佳实践

> 生成日期: 2026-02-24
> 对象: `doc/new.md` 中的 Mermaid 架构图
> 依据: LiveKit Agents 官方文档 (docs.livekit.io/agents/)、SVA Vision-Agents (visionagents.ai)

---

## 1. 总体评价

你的架构图**方向完全正确**，但有 **3 个需修正的实现细节** 和 **2 个值得强化的设计点**。

### 评分

| 维度 | 评分 | 说明 |
|:-----|:-----|:-----|
| 整体分层 | **正确** | Unity Client → LiveKit Bus → Python Backend → Workers 四层清晰 |
| 双管线分流 | **正确** | Pipeline A (视觉感知 30fps) 与 Pipeline B (认知交互) 分离是标准做法 |
| 调度器设计 | **正确** | Reflex → Redis Pub/Sub, Task → Redis Queue 的三级分流合理 |
| DSG L1/L2 分层 | **正确且有独创性** | L2-A/L2-B 双图设计比 SVA 的简单 Processor 更适合你的需求 |
| Gemini 连接方式 | **需修正** | 图中手动分流 Audio/Video 给 Gemini 与 LiveKit 实际机制不符 |
| SVA 注入标签 | **需修正** | "System Prompt Injection" 不准确，应为 "Chat Context Injection" |
| L2-B 位置 | **需修正** | L2-B 不应在 Workers 区域，应在 Backend 区域或作为跨区域缓存 |

---

## 2. 需修正的 3 个问题

### 问题 1: Gemini 不是手动接收 Audio/Video Stream

**图中画法**:
```
Ingress -- "Audio Stream" --> Gemini
Ingress -- "1fps Video (Downsample)" --> Gemini
```

**LiveKit 实际机制**:

在 LiveKit 中，Gemini Realtime 是作为 `Agent` 的 LLM 存在的。当你设置 `video_input=True`，LiveKit 框架**自动**将用户的音视频流转发给 Gemini：

```python
class ParrotBrain(Agent):
    def __init__(self):
        super().__init__(
            instructions="你是一只聪明的 AR 鹦鹉...",
            llm=google.realtime.RealtimeModel(
                voice="Puck",
                temperature=0.8,
            ),
        )

# LiveKit 框架自动处理音视频路由
session = AgentSession()
await session.start(
    agent=ParrotBrain(),
    room=ctx.room,
    room_options=room_io.RoomOptions(
        video_input=True,  # 自动将视频帧发送给 Gemini
    ),
)
```

默认采样率：说话时 1fps，空闲时 0.3fps。帧自动编码为 JPEG 1024x1024。

**修正建议**: 将 Gemini 画为 Agent 的内部 LLM，而不是独立接收流的外部服务。Audio/Video 由 LiveKit AgentSession 自动路由。

### 问题 2: "System Prompt Injection" 标签不准确

**图中画法**:
```
SVA_Injector -- "System Prompt Injection" --> Gemini
```

**LiveKit 实际机制**:

在 LiveKit 中，上下文注入有两种正确方式：

**方式 A: Chat Context 注入 (推荐)**
```python
class ParrotBrain(Agent):
    async def inject_scene_context(self, scene_state: str):
        chat_ctx = self.chat_ctx.copy()
        chat_ctx.add_message(
            role="user",
            content=[f"[SCENE_UPDATE] {scene_state}"],
        )
        await self.update_chat_ctx(chat_ctx)
```

**方式 B: 在每次 user turn 结束时附加上下文**
```python
class ParrotBrain(Agent):
    async def on_user_turn_completed(self, turn_ctx, new_message):
        if self._latest_scene_state:
            new_message.content.append(
                f"\n[SCENE_CONTEXT]\n{self._latest_scene_state}"
            )
```

**修正建议**: 将 "System Prompt Injection" 改为 "Chat Context Injection (on_user_turn_completed)"。

### 问题 3: L2-B 位置放在 Workers 区域不合理

**图中画法**: `DSG_L2_B` 在 `Workers [Background Ecosystem]` 子图中，与 Graphiti 并列。

**问题**: L2-B 作为"语义缓存"，其读取路径是 **热路径** (每次场景事件都需要查询)，不应和后台工人在同一区域。

**修正建议**: L2-B 应作为 Pipeline A 内部的缓存层，位于 `Backend [Python Cloud Engine]` 子图中。Graphiti 仍在 Workers 中，但 L2-B 是 Graphiti 的**前端缓存**，需要靠近 L2-A。

---

## 3. 符合 LiveKit 最佳实践的 2 个设计亮点

### 亮点 1: 视频分流设计

```
Ingress -- "30fps Video" --> SAM2 [Pipeline A]
(同时 LiveKit 自动抽帧给 Gemini) [Pipeline B]
```

这完全符合 LiveKit 的设计：
- Pipeline A 通过 `rtc.VideoStream(track)` 订阅原始视频帧，送入 SAM2
- Pipeline B 由 LiveKit AgentSession 的 `video_input=True` 自动完成抽帧

两条管线并行、互不干扰。

### 亮点 2: DataChannel 双向通信

```
LK_Data[DataChannel Pub/Sub]
LK_Data -- "Sync State" --> Resource_Table
Redis_Pub --> LK_Data
```

LiveKit DataChannel 支持 Reliable/Unreliable 双模式，用于：
- Reliable: 控制指令 (Action CMD)
- Unreliable: 高频遥测 (Telemetry 10Hz)

这与 LiveKit 官方推荐完全一致。

---

## 4. 符合 SVA 最佳实践的评估

### SVA 的简单 Processor 模式

```python
# SVA: 单阶段 Processor
VideoFrame → YOLO检测 → detections → inject to LLM
```

### 你的 DSG 复合 Processor 模式

```
VideoFrame → SAM2+DINOv2 (L1)
    → Spatial Graph Update (L2-A) ← Preload ← Graphiti Cache (L2-B)
        → Scene State Change Detection
            → Chat Context Injection → Gemini
```

**评估**: 你的设计是 SVA Processor 模式的**合理升级**。SVA 的 Processor 设计为单帧检测，你的 DSG 是多阶段有状态处理。这不是"违反" SVA 模式，而是"扩展"它。

SVA 中的 `attach_agent()` 事件机制 → 在你的设计中对应 `SVA_Injector` 通过 LiveKit Agent 的 `on_user_turn_completed` 或 `update_chat_ctx` 注入上下文。

---

## 5. 修正后的架构关键路径

```
[Unity Client]
  ├── Camera Video → LiveKit WebRTC Upstream
  ├── Mic Audio   → LiveKit WebRTC Upstream
  ├── XR Hands/Pose → LiveKit DataChannel (Unreliable, 10Hz)
  └── Receives: Audio + Action CMD via LiveKit

[LiveKit Server]
  ├── Routes media to Agent Room
  └── DataChannel relay

[Python Agent (Backend)]
  │
  ├── AgentSession (Gemini RealtimeModel, video_input=True)
  │   ├── Auto: Audio → Gemini
  │   ├── Auto: 1fps Video → Gemini
  │   └── Context Injection ← DSG Processor output
  │
  ├── Pipeline A: DSG Compound Processor (独立 VideoStream)
  │   ├── L1: SAM2+DINOv2 追踪 (30fps)
  │   ├── L2-A: 空间拓扑图 (事件驱动更新)
  │   ├── L2-B: 语义缓存 (Graphiti 预加载)
  │   └── Context Injector → Agent.update_chat_ctx()
  │
  ├── Scheduler (Redis)
  │   ├── Reflex: DataChannel → Redis Pub/Sub → Unity
  │   ├── Intent: Gemini Tool Call → Redis Pub/Sub → Unity
  │   └── Task: → Redis Queue → Nanobot
  │
  └── DataChannel I/O

[Workers (Background)]
  ├── Nanobot: 异步任务执行
  ├── Graphiti: 知识图谱持久化 + Leiden 社区检测
  └── 事件回调 → Context Injector
```
