# 场景管理 + 观察者时间线 + LiveKit 上下文获取

> 生成日期: 2026-02-24
> 回答的核心问题:
> 1. 前端设备为**安卓手机**，不是头显
> 2. 场景分类 (室外/室内/桌面) 与切换机制设计
> 3. 场景折叠/展开在 L2-A 和 L2-B 中的实现
> 4. L3 观察者时间线 + LiveKit 上下文获取方案 + Graphiti 归档路径

---

## 0. 前端设备声明：安卓手机

整个架构中 **Unity AR Client** 的目标设备是**安卓手机** (Android 8.0+)，不是 AR 头显或 iOS 设备。

这影响以下设计决策：

| 维度 | 安卓手机约束 | 设计影响 |
|:-----|:-----------|:---------|
| AR SDK | **ARCore** (Google)，非 ARKit | `TrackingState` / `NotTrackingReason` API 来自 ARCore |
| XR Hands | ARCore 手部追踪 (仅限 Pixel 等机型) 或 **MediaPipe Hands** on-device | L1 手势处理需要适配层，不能假设 XR Hand Subsystem 总可用 |
| 性能 | Snapdragon 8 Gen 系列: GPU 编码 + WebRTC 已经吃掉不少电量 | Unity 端只做 AR 采集 + WebRTC 推流 + 渲染，**所有视觉模型在云端** |
| 相机 | 后置主摄 (通常 12-50MP)，但 WebRTC 传输分辨率受限 (720p/1080p) | L1 在云端处理的是 WebRTC 降采样后的帧，非原始分辨率 |
| IMU | 安卓手机 IMU 噪声大于头显 | StabilityGate 的阈值需要实测调整 |
| 网络 | Wi-Fi 为主 (室内)，4G/5G (室外) | LiveKit 自适应码率处理，但室外弱网时需降级策略 |
| 屏幕 | 手持竖屏/横屏，非 HMD 双眼 | AR 渲染 UI 和鹦鹉展示按手机屏幕布局设计 |

### MVP 设备基线

- **最低**: Snapdragon 870 级别, Android 10, ARCore 支持
- **推荐**: Snapdragon 8 Gen 2+, Android 13+

---

## 1. 场景分类与切换机制

### 1.1 从 SVA 学到什么

SVA 的不同实践项目实际上就是**不同场景配置**下同一框架的不同实例化：

| SVA 项目 | 场景特征 | 处理器配置 | 我们能学的 |
|:---------|:---------|:----------|:----------|
| **高尔夫教练** | 室外、固定三脚架、侧面视角、单人全身 | YOLO Pose → 姿态分析 → 教练反馈 | **场景 Profile** 的概念: 不同场景用不同处理器组合 |
| **安防监控** | 室内、固定墙壁、广角、多人 | YOLO 检测 + 人脸识别 + 报警 | **触发器阈值** 因场景而异: 安防低阈值高警觉 |
| **制造质检** | 室内、固定工位、微距、特定物件 | 细粒度检测 + 缺陷分类 | **物体发现策略** 因场景而异: 质检关注特定类别 |
| **体育教练** | 室内、固定、正面/侧面 | YOLO Pose → 动作分析 | **动作分析** 是可选处理器，按场景启用 |
| **RAG 问答** | 通用、固定视角 | 帧截图 → VLM 描述 → RAG 检索 | **Context Injection** 模式: 视觉结果灌入对话上下文 |

**核心学习**: SVA 没有显式的"场景切换"——它通过 **不同的处理器配置 (Processor Config)** 来适应不同场景。我们要做的是**运行时可切换的 Processor Config**。

### 1.2 场景类型定义

```python
from enum import Enum
from dataclasses import dataclass, field

class SceneType(Enum):
    OUTDOOR = "outdoor"
    INDOOR = "indoor"
    DESKTOP = "desktop"

@dataclass
class SceneProfile:
    """场景配置: 定义该场景下 L1 处理器的行为"""
    scene_type: SceneType
    name: str

    # L1 处理器参数
    discoverer_enabled: bool = True
    discoverer_fps: float = 1.0
    discoverer_vocab: list[str] = field(default_factory=list)  # YOLO-World 开放词汇

    tracker_max_targets: int = 20
    reid_enabled: bool = True
    action_analyzer_enabled: bool = False

    # StabilityGate 阈值覆写
    stable_velocity_thresh: float = 0.1
    stable_angular_thresh: float = 0.3
    moving_velocity_thresh: float = 0.5

    # L2-A 空间图参数
    spatial_scale: str = "room"   # "street" | "room" | "tabletop"
    default_zone_size: float = 3.0  # 米, Zone 划分半径

    # L2-B 注意力参数
    novelty_half_life: float = 60.0   # 秒
    habituation_rate: float = 0.05
```

### 1.3 预定义场景 Profile (MVP: 室内 + 桌面)

```python
SCENE_PROFILES: dict[SceneType, SceneProfile] = {
    SceneType.DESKTOP: SceneProfile(
        scene_type=SceneType.DESKTOP,
        name="桌面近距",
        discoverer_fps=2.0,
        discoverer_vocab=["cup", "bottle", "phone", "book", "pen",
                          "keyboard", "mouse", "monitor", "plant", "figure"],
        tracker_max_targets=15,
        reid_enabled=True,
        action_analyzer_enabled=True,   # 桌面场景关注手部动作
        stable_velocity_thresh=0.05,     # 桌面要求更严格的"稳定"
        stable_angular_thresh=0.2,
        spatial_scale="tabletop",
        default_zone_size=0.8,           # 桌面区域较小
        novelty_half_life=120.0,         # 桌面物体变化慢，新奇衰减慢
    ),

    SceneType.INDOOR: SceneProfile(
        scene_type=SceneType.INDOOR,
        name="室内房间",
        discoverer_fps=1.0,
        discoverer_vocab=["person", "chair", "table", "sofa", "tv",
                          "door", "window", "lamp", "shelf", "painting"],
        tracker_max_targets=30,
        reid_enabled=True,
        action_analyzer_enabled=False,    # 室内先不做动作分析
        stable_velocity_thresh=0.1,
        stable_angular_thresh=0.3,
        spatial_scale="room",
        default_zone_size=3.0,
        novelty_half_life=60.0,
    ),

    # Phase 2+ 再实现
    SceneType.OUTDOOR: SceneProfile(
        scene_type=SceneType.OUTDOOR,
        name="室外街道",
        discoverer_fps=0.5,              # 室外帧率低: 节省资源 + 物体频繁进出
        discoverer_vocab=["person", "car", "bicycle", "tree", "building",
                          "sign", "dog", "bench", "streetlight"],
        tracker_max_targets=50,
        reid_enabled=False,               # 室外 ReID 不可靠 (行人匆匆而过)
        action_analyzer_enabled=False,
        stable_velocity_thresh=0.3,       # 室外走路也算"稳定"
        stable_angular_thresh=0.5,
        moving_velocity_thresh=1.0,
        spatial_scale="street",
        default_zone_size=10.0,
        novelty_half_life=30.0,           # 室外物体变化快，新奇衰减快
    ),
}
```

### 1.4 场景切换机制：在哪个模块实现？

**归属: L1 层的 SceneManager 模块**。

理由：
- 场景 Profile 主要影响 L1 处理器的参数配置
- 场景切换时需要通知 L2-A/L2-B 做折叠/展开（见下节），但决策点在 L1
- L1 拥有 ARCore 遥测数据，是判断场景变化的最佳位置

```
L1VisionPipeline
├── StabilityGate          (已有)
├── SceneManager           (新增: 场景分类与切换)
│   ├── SceneClassifier    (判断当前场景类型)
│   └── SceneTransition    (执行切换: 通知 L2 折叠/展开)
├── Tracker                (已有)
├── Discoverer             (已有, 参数由 SceneProfile 控制)
├── Identifier             (已有)
└── ...
```

### 1.5 场景检测逻辑

MVP 中不需要自动场景检测——用户通过语音/Gemini 切换即可：

```python
@function_tool
async def switch_scene(scene_type: str) -> str:
    """切换当前观察场景类型。影响视觉处理器的配置和 DSG 图的管理。
    当用户从桌面走到客厅、或从室内到室外时调用。

    Args:
        scene_type: "desktop" | "indoor" | "outdoor"
    """
    new_type = SceneType(scene_type)
    await scene_manager.transition_to(new_type)
    return f"已切换到 {SCENE_PROFILES[new_type].name} 模式"
```

未来 (Phase 2+) 可以做自动检测：

```python
class SceneClassifier:
    """基于 ARCore 信号的场景类型推断 (Phase 2)"""

    def infer(self, telemetry: dict, l2a_stats: dict) -> SceneType | None:
        planes = telemetry.get("planes_detected", 0)
        plane_area = telemetry.get("total_plane_area", 0)
        avg_object_dist = l2a_stats.get("avg_object_distance", 999)

        # 桌面特征: 单个水平面 + 物体距离近 (<0.8m)
        if planes <= 2 and avg_object_dist < 0.8:
            return SceneType.DESKTOP

        # 室内特征: 多个平面 (地板+桌面+墙壁) + 中等距离
        if planes >= 3 and avg_object_dist < 5.0:
            return SceneType.INDOOR

        # 室外特征: 很少平面 (可能只有地面) + 物体远
        if planes <= 1 and avg_object_dist > 5.0:
            return SceneType.OUTDOOR

        return None  # 不确定，保持当前场景
```

### 1.6 项目结构中的位置

```
agent/
├── perception/
│   ├── l1_pipeline.py        # L1 主管线 (已有设计)
│   ├── stability_gate.py     # 稳定性门控 (已有设计)
│   ├── scene_manager.py      # 🆕 场景管理器
│   ├── scene_profiles.py     # 🆕 场景 Profile 定义
│   ├── ...
```

---

## 2. 场景折叠/展开在 L2-A 和 L2-B 中的实现

### 2.1 核心概念：场景即上下文窗口

当用户从桌面走到客厅，**桌面上的物体不会消失**——它们只是**离开了视野**。DSG 需要：

1. **折叠** (Fold): 将离开场景的图数据压缩归档，释放工作记忆
2. **展开** (Unfold): 当用户回到之前的场景，恢复之前的图状态
3. **共存** (Coexist): 某些物体可能横跨场景 (如用户手持的手机)

这类似于**操作系统的进程挂起/恢复**，或**浏览器标签页的冻结/激活**。

### 2.2 L2-A 场景折叠

```python
@dataclass
class SceneSnapshot:
    """一个场景的冻结快照"""
    scene_type: SceneType
    scene_id: str                              # UUID
    frozen_at: float                           # 时间戳
    spatial_data: bytes                         # RustworkX 图序列化
    node_uuids: set[str]                        # 该场景包含的物体 UUID
    zone_hierarchy: dict                        # Zone 层级结构
    camera_last_pose: tuple | None              # 最后一次相机位姿

class SpatialGraph:
    """L2-A 扩展: 支持场景折叠/展开"""

    def __init__(self):
        self._graph = rx.PyDiGraph()
        self._uuid_to_idx: dict[str, int] = {}
        self._active_scene_id: str = ""
        self._frozen_scenes: dict[str, SceneSnapshot] = {}  # scene_id → 快照

    def fold_scene(self, scene_id: str) -> SceneSnapshot:
        """折叠当前场景: 序列化图 → 存入冻结库 → 清空活跃图"""
        snapshot = SceneSnapshot(
            scene_type=self._current_scene_type,
            scene_id=scene_id,
            frozen_at=time.time(),
            spatial_data=rx.node_link_json(self._graph).encode(),
            node_uuids=set(self._uuid_to_idx.keys()),
            zone_hierarchy=self._export_zones(),
            camera_last_pose=self._last_camera_pose,
        )
        self._frozen_scenes[scene_id] = snapshot

        # 清空活跃图 (但不删除: 冻结保留)
        self._graph = rx.PyDiGraph()
        self._uuid_to_idx.clear()

        return snapshot

    def unfold_scene(self, scene_id: str) -> bool:
        """展开一个冻结场景: 从快照恢复图"""
        if scene_id not in self._frozen_scenes:
            return False

        # 先折叠当前场景 (如果有)
        if self._active_scene_id:
            self.fold_scene(self._active_scene_id)

        snapshot = self._frozen_scenes.pop(scene_id)
        self._graph = rx.PyDiGraph()
        # 从序列化数据恢复
        self._restore_from_snapshot(snapshot)
        self._active_scene_id = scene_id
        return True

    def transfer_object(self, uuid: str, to_scene_id: str):
        """物体跨场景转移 (如用户手持物品走到另一个房间)"""
        if uuid in self._uuid_to_idx:
            node_data = self._graph[self._uuid_to_idx[uuid]]
            # 标记为"跨场景携带"
            node_data.portable = True
            # 不从当前图删除，但在目标场景展开时自动合入
```

### 2.3 L2-B 场景折叠

L2-B 的折叠更语义化——不只是暂停，还涉及**注意力状态的保存和恢复**：

```python
@dataclass
class SemanticSceneSnapshot:
    """L2-B 语义场景快照"""
    scene_id: str
    frozen_at: float
    semantic_data: bytes                        # RustworkX 语义图序列化
    attention_states: dict[str, dict]           # uuid → {weight, novelty, salience, ...}
    active_triggers: list[dict]                 # 未消费的触发器
    top_attended: list[str]                     # 折叠时最受关注的物体

class SemanticAttentionGraph:
    """L2-B 扩展: 支持场景折叠/展开"""

    def fold_scene(self, scene_id: str) -> SemanticSceneSnapshot:
        """折叠: 保存所有注意力状态"""
        attention_states = {}
        for uuid, idx in self._uuid_to_idx.items():
            node = self._graph[idx]
            attention_states[uuid] = {
                "weight": node.attention_weight,
                "novelty": node.novelty_score,
                "salience": node.salience,
                "attend_count": node.attend_count,
                "last_attended": node.last_attended,
                "emotional_valence": node.emotional_valence,
            }

        top_attended = [
            n.uuid for n in self._attention.get_attended(
                [self._graph[i] for i in self._graph.node_indices()], top_k=5
            )
        ]

        snapshot = SemanticSceneSnapshot(
            scene_id=scene_id,
            frozen_at=time.time(),
            semantic_data=rx.node_link_json(self._graph).encode(),
            attention_states=attention_states,
            active_triggers=self._triggers.copy(),
            top_attended=top_attended,
        )

        self._graph = rx.PyDiGraph()
        self._uuid_to_idx.clear()
        self._triggers.clear()
        return snapshot

    def unfold_scene(self, snapshot: SemanticSceneSnapshot):
        """展开: 恢复图 + 注意力状态，但给予"久别重逢"增益"""
        self._restore_from_snapshot(snapshot)

        elapsed = time.time() - snapshot.frozen_at
        for uuid, idx in self._uuid_to_idx.items():
            node = self._graph[idx]
            saved = snapshot.attention_states.get(uuid, {})

            # 恢复基础状态
            node.attention_weight = saved.get("weight", 0.3)
            node.attend_count = saved.get("attend_count", 0)

            # "久别重逢"效应: 长时间不见的场景，回来时有轻微新奇增益
            reunion_boost = min(0.2, elapsed / 3600 * 0.1)  # 每小时 0.1, 上限 0.2
            node.attention_weight = min(1.0, node.attention_weight + reunion_boost)

            # 之前最受关注的物体获得额外恢复增益
            if uuid in snapshot.top_attended:
                node.attention_weight = min(1.0, node.attention_weight + 0.1)
                node.salience = "foreground"
```

### 2.4 场景切换的完整流程

```
用户: "我去客厅看看" (或 Gemini 判断用户在移动)
  │
  ▼
Gemini → Tool Call: switch_scene("indoor")
  │
  ▼
SceneManager.transition_to(INDOOR)
  │
  ├─1→ L2-A.fold_scene("desktop_001")     # 折叠桌面空间图
  ├─2→ L2-B.fold_scene("desktop_001")     # 折叠桌面语义图 + 注意力
  ├─3→ L3.on_scene_transition("desktop→indoor", summary)  # 记录事件边界
  │     └─→ Graphiti.add_episode(scene_transition_event)   # 归档
  ├─4→ L1.apply_profile(SCENE_PROFILES[INDOOR])  # 切换处理器参数
  ├─5→ (如果之前有 indoor 快照)
  │     ├─→ L2-A.unfold_scene("indoor_001")  # 恢复室内空间图
  │     └─→ L2-B.unfold_scene("indoor_001")  # 恢复室内语义图
  │   (如果没有)
  │     └─→ 从空白开始构建新场景
  └─6→ ContextInjector → Gemini: "[SCENE_CHANGE] 从桌面切换到室内房间"

用户: "回去看看桌上的杯子"
  │
  ▼
Gemini → Tool Call: switch_scene("desktop")
  │
  ▼
SceneManager.transition_to(DESKTOP)
  ├─→ L2-A.fold_scene("indoor_001")
  ├─→ L2-B.fold_scene("indoor_001")
  ├─→ L2-A.unfold_scene("desktop_001")     # 桌面回来了！
  ├─→ L2-B.unfold_scene("desktop_001")     # 杯子的注意力权重被恢复 + 久别重逢增益
  └─→ ContextInjector → Gemini: "[SCENE_RESTORED] 回到桌面, 上次关注: 杯子, 笔记本, 手机"
```

### 2.5 Graphiti 中的场景感知

场景切换事件也会写入 Graphiti，这样长期记忆中有"场景"概念：

```python
async def archive_scene_transition(
    self,
    graphiti: Graphiti,
    from_scene: SceneSnapshot,
    to_scene_type: SceneType,
    summary: str,
):
    """场景切换时向 Graphiti 归档"""
    episode_body = (
        f"Scene transition: {from_scene.scene_type.value} → {to_scene_type.value}. "
        f"Objects in previous scene: {', '.join(list(from_scene.node_uuids)[:10])}. "
        f"Summary: {summary}"
    )
    await graphiti.add_episode(
        name=f"scene_transition_{from_scene.scene_id}",
        episode_body=episode_body,
        source_description="DSG Scene Manager",
    )
```

---

## 3. L3 观察者时间线

### 3.1 为什么需要时间线

Gemini Multimodal Live 确实能处理**对话的时间顺序**——它知道"用户先说了A，然后我回了B"。但它**不知道**：
- DSG 层面的事件序列（"杯子先出现，然后被拿起，然后放下"）
- 各层间的因果关系（"因为杯子被拿起[L2-A]，所以注意力提高了[L2-B]"）
- 跨场景的时间跨度（"30分钟前在桌面看到杯子，现在在客厅"）

**Gemini 维护对话时间线，L3 观察者维护感知时间线。两者互补。**

### 3.2 LiveKit 能提供什么上下文？

好消息：**LiveKit 的事件系统可以捕获 Gemini 的完整对话**。

| LiveKit 事件 | 提供的数据 | 可获取的内容 |
|:------------|:----------|:-----------|
| `conversation_item_added` | `ChatMessage` (role, text_content, content[]) | **每一条对话消息** (用户输入 + Gemini 回复)，包括文本、图片、音频转写 |
| `function_tools_executed` | `FunctionCall` + `FunctionCallOutput` (通过 `.zipped()`) | **每次 Tool Call 的调用参数和返回值** (event_end, focus_on, switch_scene 等) |
| `user_input_transcribed` | transcript, language, is_final | 用户语音的实时转写 |
| `agent_state_changed` | old_state, new_state | Agent 状态转换 (listening→thinking→speaking) |

关键代码：

```python
from livekit.agents import (
    ConversationItemAddedEvent,
    FunctionToolsExecutedEvent,
    AgentStateChangedEvent,
)

@session.on("conversation_item_added")
def on_conversation_item(event: ConversationItemAddedEvent):
    """捕获每一条对话消息 (用户+Gemini)"""
    timeline.record_conversation(
        role=event.item.role,
        text=event.item.text_content,
        timestamp=time.time(),
        interrupted=event.item.interrupted,
    )

@session.on("function_tools_executed")
def on_tools_executed(event: FunctionToolsExecutedEvent):
    """捕获每次 Tool Call 的完整信息"""
    for call, output in event.zipped():
        timeline.record_tool_call(
            tool_name=call.function_info.name,
            arguments=call.arguments,
            result=output.content,
            timestamp=time.time(),
        )
```

### 3.3 结论：不需要"依赖观察者来维护上下文"

LiveKit 给了我们两条获取 Gemini 上下文的途径：

| 途径 | 方式 | 适用场景 |
|:-----|:-----|:---------|
| **实时事件流** | `conversation_item_added` + `function_tools_executed` | L3 观察者实时维护时间线 |
| **快照获取** | `session.chat_ctx.messages` | 需要完整上下文时一次性获取 |

**两者结合**：观察者用事件流实时构建时间线，在归档到 Graphiti 时用 `chat_ctx.messages` 补充完整上下文。

### 3.4 L3 观察者时间线设计

```python
from dataclasses import dataclass, field
from collections import deque

@dataclass
class TimelineEvent:
    """时间线上的一个事件"""
    timestamp: float
    event_type: str          # "perception" | "conversation" | "tool_call" | "scene_change" | "boundary"
    source: str              # "L1" | "L2-A" | "L2-B" | "gemini" | "user" | "system"
    content: dict            # 事件内容 (灵活结构)
    episode_id: str = ""     # 所属 episode (由 event_end 划分)

@dataclass
class Episode:
    """一个事件片段 (Gemini event_end 划分的)"""
    episode_id: str
    started_at: float
    ended_at: float | None = None
    summary: str = ""
    events: list[TimelineEvent] = field(default_factory=list)
    participating_objects: set[str] = field(default_factory=set)
    conversation_turns: list[dict] = field(default_factory=list)  # 对话摘要

class ObserverTimeline:
    """L3 观察者维护的感知+对话时间线"""

    MAX_EVENTS = 500  # 内存中保留的最大事件数

    def __init__(self):
        self._events: deque[TimelineEvent] = deque(maxlen=self.MAX_EVENTS)
        self._current_episode: Episode | None = None
        self._archived_episodes: list[str] = []  # episode_id 列表 (内容在 Graphiti)

    # ===== 感知事件记录 (来自 L2-B 触发器) =====

    def record_perception(self, event_type: str, uuid: str, details: dict):
        """L2-B 触发器 → 时间线"""
        evt = TimelineEvent(
            timestamp=time.time(),
            event_type="perception",
            source="L2-B",
            content={"object_uuid": uuid, "trigger": event_type, **details},
            episode_id=self._current_episode.episode_id if self._current_episode else "",
        )
        self._events.append(evt)
        if self._current_episode:
            self._current_episode.events.append(evt)
            self._current_episode.participating_objects.add(uuid)

    # ===== 对话事件记录 (来自 LiveKit 事件) =====

    def record_conversation(self, role: str, text: str, timestamp: float, interrupted: bool):
        """LiveKit conversation_item_added → 时间线"""
        evt = TimelineEvent(
            timestamp=timestamp,
            event_type="conversation",
            source="gemini" if role == "assistant" else "user",
            content={"role": role, "text": text, "interrupted": interrupted},
            episode_id=self._current_episode.episode_id if self._current_episode else "",
        )
        self._events.append(evt)
        if self._current_episode:
            self._current_episode.events.append(evt)
            self._current_episode.conversation_turns.append({
                "role": role, "text": text[:200], "t": timestamp,
            })

    def record_tool_call(self, tool_name: str, arguments: dict, result: str, timestamp: float):
        """LiveKit function_tools_executed → 时间线"""
        evt = TimelineEvent(
            timestamp=timestamp,
            event_type="tool_call",
            source="gemini",
            content={"tool": tool_name, "args": arguments, "result": result},
            episode_id=self._current_episode.episode_id if self._current_episode else "",
        )
        self._events.append(evt)
        if self._current_episode:
            self._current_episode.events.append(evt)

    # ===== Episode 管理 =====

    def start_episode(self, episode_id: str):
        """开始新 episode (首次或 event_end 后自动开始)"""
        self._current_episode = Episode(
            episode_id=episode_id,
            started_at=time.time(),
        )

    def end_episode(self, summary: str) -> Episode:
        """Gemini event_end → 关闭当前 episode"""
        if not self._current_episode:
            return None
        ep = self._current_episode
        ep.ended_at = time.time()
        ep.summary = summary
        self._current_episode = None
        return ep

    # ===== 用于 Graphiti 归档的数据提取 =====

    def compose_episode_body(self, episode: Episode, chat_ctx_messages: list = None) -> str:
        """将 episode 转化为 Graphiti 可消化的文本"""
        lines = [f"Episode: {episode.summary}"]
        lines.append(f"Duration: {episode.ended_at - episode.started_at:.0f}s")
        lines.append(f"Objects: {', '.join(episode.participating_objects)}")

        # 感知事件摘要
        perceptions = [e for e in episode.events if e.event_type == "perception"]
        if perceptions:
            lines.append("Perceptions:")
            for p in perceptions[:20]:
                lines.append(f"  - [{p.content['trigger']}] {p.content.get('object_uuid', '')}")

        # 对话摘要 (来自 LiveKit 事件捕获)
        if episode.conversation_turns:
            lines.append("Conversation:")
            for turn in episode.conversation_turns[:10]:
                role_tag = "User" if turn["role"] == "user" else "Parrot"
                lines.append(f"  - {role_tag}: {turn['text'][:100]}")

        # 如果提供了完整上下文，补充 Gemini 的推理
        if chat_ctx_messages:
            tool_calls = [
                e for e in episode.events if e.event_type == "tool_call"
            ]
            if tool_calls:
                lines.append("Gemini Actions:")
                for tc in tool_calls:
                    lines.append(f"  - {tc.content['tool']}({tc.content['args']})")

        return "\n".join(lines)
```

### 3.5 完整的 L3 → Graphiti 归档路径

```
                    LiveKit Events
                    ┌──────────────────────┐
                    │ conversation_item_    │
                    │   added              │──→ ObserverTimeline.record_conversation()
                    │ function_tools_      │
                    │   executed           │──→ ObserverTimeline.record_tool_call()
                    └──────────────────────┘
                              │
                    L2-B Triggers
                    ┌──────────────────────┐
                    │ NEW_OBJECT           │
                    │ OBJECT_MOVED         │──→ ObserverTimeline.record_perception()
                    │ OBJECT_LOST          │
                    └──────────────────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │  ObserverTimeline    │
                    │  (内存中的事件环)     │
                    │  ┌─ Episode 1 ──┐   │
                    │  │ perceptions  │   │
                    │  │ conversations│   │
                    │  │ tool_calls   │   │
                    │  └──────────────┘   │
                    └──────────┬───────────┘
                               │
                    Gemini Tool: event_end(uuids, summary)
                               │
                               ▼
                    ┌──────────────────────┐
                    │ CognitiveInterface   │
                    │  1. timeline.end_episode()       │
                    │  2. compose_episode_body()       │
                    │  3. l2b.gemini_fold_cluster()    │
                    │  4. graphiti.add_episode()       │ ──→ Graphiti (Neo4j)
                    │  5. timeline.start_episode()     │      三元组提取
                    └──────────────────────┘            │      Leiden 社区聚类
                                                        │      向量化存储
```

### 3.6 更新后的 CognitiveInterface

```python
class CognitiveInterface:
    """L3: 前额叶接口 (更新版: 含时间线 + LiveKit 事件监听)"""

    def __init__(self, session: AgentSession, l2a: SpatialGraph, l2b: SemanticAttentionGraph, graphiti: Graphiti):
        self._session = session
        self._l2a = l2a
        self._l2b = l2b
        self._graphiti = graphiti
        self._timeline = ObserverTimeline()
        self._atmosphere = AtmosphereState()

        # 自动开始第一个 episode
        self._timeline.start_episode(str(uuid4()))

        # 注册 LiveKit 事件监听
        self._setup_livekit_hooks()

    def _setup_livekit_hooks(self):
        """挂载 LiveKit 事件 → 时间线"""

        @self._session.on("conversation_item_added")
        def on_conv(event: ConversationItemAddedEvent):
            self._timeline.record_conversation(
                role=event.item.role,
                text=event.item.text_content or "",
                timestamp=time.time(),
                interrupted=event.item.interrupted,
            )

        @self._session.on("function_tools_executed")
        def on_tools(event: FunctionToolsExecutedEvent):
            for call, output in event.zipped():
                self._timeline.record_tool_call(
                    tool_name=call.function_info.name,
                    arguments=call.arguments,
                    result=str(output.content)[:500],
                    timestamp=time.time(),
                )

    async def handle_event_end(self, participating_uuids: list[str], summary: str):
        """Gemini Tool Call: event_end → 归档完整 episode"""
        # 1. 关闭当前 episode
        episode = self._timeline.end_episode(summary)
        if not episode:
            return

        # 2. L2-B 实时折叠
        self._l2b.gemini_fold_cluster(participating_uuids)

        # 3. 构造 episode body (含对话和感知)
        episode_body = self._timeline.compose_episode_body(episode)

        # 4. Graphiti 异步归档
        asyncio.create_task(
            self._graphiti.add_episode(
                name=f"ep_{episode.episode_id[:8]}",
                episode_body=episode_body,
                source_description="L3 CognitiveInterface",
            )
        )

        # 5. 更新氛围 + 开始新 episode
        self._atmosphere.on_event_boundary()
        self._timeline.start_episode(str(uuid4()))
```

---

## 4. 关键决策总结

| 问题 | 决策 | 理由 |
|:-----|:-----|:-----|
| 前端设备 | 安卓手机 (ARCore) | 用户明确要求 |
| 场景分类 | SceneType: OUTDOOR/INDOOR/DESKTOP | 三级足够覆盖典型使用场景 |
| 场景切换触发 | MVP: Gemini Tool Call `switch_scene()`; Phase 2: 自动检测 | MVP 简化，自动检测需要数据积累 |
| 场景切换归属模块 | L1 SceneManager | L1 拥有 ARCore 遥测 + 控制处理器参数 |
| 场景折叠实现 | L2-A/L2-B 各自维护 SceneSnapshot | 独立序列化，互不影响 |
| L2-B 展开增益 | "久别重逢"注意力增益 | 仿生：离开久的地方回来时会多看几眼 |
| Gemini 上下文获取 | LiveKit `conversation_item_added` + `function_tools_executed` 事件 | **可以获取完整对话和 Tool Call 数据** |
| 观察者时间线 | L3 `ObserverTimeline` 合并感知事件和对话事件 | 两条数据流汇入同一时间线 |
| Graphiti 归档内容 | Episode = 感知事件 + 对话轮次 + Tool Call + 摘要 | 完整的上下文给 Graphiti 做三元组提取 |

---

## 5. MVP 范围与后续扩展

### MVP (Phase 1) 实现

- [x] SceneProfile 定义 (DESKTOP + INDOOR)
- [x] `switch_scene()` Tool (手动切换)
- [x] L2-A / L2-B 场景折叠/展开 (基础版)
- [x] ObserverTimeline (事件记录)
- [x] LiveKit 事件监听 (`conversation_item_added` + `function_tools_executed`)
- [x] Graphiti Episode 归档 (基础版)

### Phase 2 扩展

- [ ] SceneClassifier 自动场景检测
- [ ] OUTDOOR 场景支持
- [ ] 跨场景物体转移 (`transfer_object`)
- [ ] 时间线可视化 (调试用)
- [ ] Episode 智能拆分 (基于对话沉默 + 场景变化的自动边界检测)
