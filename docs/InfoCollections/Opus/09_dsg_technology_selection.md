# DSG 模块技术选型深度调研

> 生成日期: 2026-02-24 (v2: 补充 L2-B RustworkX 设计 + L3 认知层)
> 用途: 为 DSG 四层架构 (L1/L2-A/L2-B/L3) 确定技术实现方案
> 依据: MIT-SPARK/Hydra、Spark-DSG、FROSS、Graphiti、Microsoft GraphRAG、RustworkX、神经科学注意力模型

---

## 1. DSG 四层架构定位

DSG 不是一个简单的 SVA Processor，而是一个**四层仿生复合 Processor**。

```
[SVA 简单 Processor]
  VideoFrame → YOLO → detections → inject

[DSG 四层复合 Processor — 仿生视觉系统]
  L1 (视网膜)    : VideoFrame → SAM2+DINOv2 → 物理追踪
  L2-A (背侧通路) : 追踪事件 → RustworkX 空间图 → "在哪里"
  L2-B (腹侧通路) : 空间事件 + Graphiti预加载 → RustworkX 语义注意力图 → "是什么" + 注意力
  L3 (前额叶接口) : 触发器 + 观察者 + 氛围 → Context Injection ↔ Gemini 事件分割
```

### 生物学映射

| DSG 层 | 脑区类比 | 功能 | 维护者 |
|:-------|:---------|:-----|:-------|
| L1 | 视网膜 (Retina) | 原始信号过滤、噪声抑制 | SAM2 + DINOv2 |
| L2-A | 背侧通路 (Dorsal "Where") | 空间拓扑、位置关系、运动追踪 | Vision Pipeline |
| L2-B | 腹侧通路 (Ventral "What") | 语义联想、注意力分配、身份识别 | 注意力系统 + Graphiti |
| L3 | 前额叶接口 (Prefrontal) | 事件边界、叙事氛围、Gemini 通信 | 观察者 + Gemini 事件分割 |

### 为什么是四层而不是三层

旧设计中 L2-B 是 Graphiti 的被动缓存（Dict），只能存取标签。升级为 RustworkX 图后：
- L2-B 能**主动运算**：注意力衰减、新奇增益、聚类折叠
- L2-B 能**被 Gemini 操纵**：Gemini 通过 L3 下发 "关注杯子" 的 top-down 注意力信号
- L3 独立出来作为 Gemini 的通信层，承载氛围/叙事这类更高层语义

三层各有**不同的时间尺度和维护者**，这是关键的解耦：
- L2-A: 由物理世界驱动（物体移动了→更新）
- L2-B: 由注意力系统驱动（什么值得关注→更新）+ Graphiti 驱动（记忆预加载→更新）
- L3: 由 Gemini 驱动（事件结束了→折叠归档）+ 观察者驱动（定时快照→更新）

---

## 2. L2-A 技术选型：空间拓扑图

### 2.1 需求分析

L2-A 的核心需求（你的描述）：
1. **符合视觉模型产出**: 能接收 SAM2 的 mask/track + DINOv2 的特征向量
2. **学习 SSG（3D Spatial Scene Graph）**: 分层的空间关系图
3. **可扩展**: 新物体进入时能增量添加节点和边
4. **可确认**: 物体重现时能通过 ReID 确认身份
5. **可查询**: 支持"桌上有什么"、"杯子旁边是什么"等空间查询

### 2.2 候选技术调研

#### 方案 A: Spark-DSG (MIT-SPARK)

- **仓库**: https://github.com/MIT-SPARK/Spark-DSG (v1.1.3)
- **安装**: `pip install spark-dsg`（需要 C++ 系统依赖: libzmqpp-dev, nlohmann-json3-dev）
- **设计**: 分层场景图，每层代表不同抽象级别（物体→区域→房间→建筑）
- **Python API**: 有 bindings，含示例 notebook

**优势**:
- 专门为分层 3D 场景图设计，与 SSG 概念完全对齐
- 被 Hydra (910 stars) 验证的生产级数据结构
- 原生支持分层查询（按层遍历节点和边）
- 2026年2月仍在活跃更新

**劣势**:
- C++ 核心，需要编译系统依赖（Docker 中可解决，但增加复杂度）
- 为 SLAM/深度传感器设计，部分 API 假设 3D 点云输入
- 社区较小，遇到问题排查成本高
- 与我们的 2D AR + 半 3D 位姿场景有一定 gap

#### 方案 B: RustworkX + 自定义分层封装

- **仓库**: https://github.com/Qiskit/rustworkx
- **安装**: `pip install rustworkx`（纯 pip，无系统依赖）
- **设计**: 通用高性能图库，Rust 编写，Python 绑定

**优势**:
- **GIL-free**: 图算法在 Rust 线程运行，不阻塞 L1 的视频处理和 Agent 的音频管线
- `contract_nodes()` 原生支持: 实现 Gemini 主导的"事件折叠"
- 纯 pip 安装，Docker 部署零障碍
- API 与 NetworkX 相似，学习成本低
- 在旧项目中已有选型论证，团队有认知基础

**劣势**:
- 无原生分层概念，需要自己实现 Layer 抽象
- 无内置空间查询（需要自定义 "桌上有什么" 等查询逻辑）

#### 方案 C: NetworkX

- 标准 Python 图库，论文中广泛使用（包括 3D Scene Graph for Spatial AI 教程）
- **致命问题**: GIL 阻塞。当 DSG 是复合 Processor 时，图遍历会抢占 GIL，影响并发的音频管线。**不推荐**。

#### 方案 D: FROSS 概念借鉴

- FROSS (2025 ICCV) 实现了实时 3D SSG: RGB-D → 2D 场景图 → 3D 提升 → 全局图合并
- **我们不能直接用 FROSS**（需要 RGB-D 深度输入，我们只有单目 AR 视频）
- **但可以借鉴其核心概念**:
  - 用 3D 高斯分布表示物体位置（含不确定性）
  - 增量在线更新而非批量重建
  - 用 Hellinger 距离合并多视角观测

### 2.3 L2-A 推荐方案

**推荐: 方案 B — RustworkX + 自定义分层封装**

理由：
1. **GIL-free 至关重要**: DSG 现在是复合 Processor，与 Gemini Agent 共存于同一 Python 进程，GIL 阻塞会直接影响语音延迟
2. **部署简洁**: 纯 pip 安装，Docker 无额外依赖
3. **`contract_nodes()` 直接可用**: 这是 Gemini 事件折叠的核心操作
4. **旧项目的 RustworkX 选型论证仍然成立**: 当初的决策逻辑没有过时，反而因为 DSG 变成更复杂的 Processor 而更加合理

**之前文件中 "RustworkX 过度工程化" 的判断是错误的**——那是基于 DSG 可能被简化为 "Processor 状态 + Redis" 的假设。现在你明确了 L2-A 需要 SSG 级别的空间图，RustworkX 不仅不过度，而且是恰好合适的工具。

### 2.4 L2-A 分层封装设计

```python
from enum import IntEnum
import rustworkx as rx

class DSGLayer(IntEnum):
    """场景图层级定义 (借鉴 Spark-DSG/Hydra 的分层理念)"""
    OBJECTS = 0      # 物体节点 (SAM2 Tracks)
    SURFACES = 1     # 承载面 (桌面、地面、手掌)
    ZONES = 2        # 功能区域 (工作区、厨房区)
    # 未来可扩展:
    # ROOMS = 3      # 房间
    # BUILDING = 4   # 建筑

class SpatialNode:
    """L2-A 空间节点"""
    uuid: str                    # 全局唯一 ID
    layer: DSGLayer              # 所属层级
    class_label: str             # 类别 ("cup", "hand", "table")
    position_3d: tuple[float, float, float]  # AR 空间坐标 (from Unity Pose)
    position_cov: list[float]    # 位置协方差 (不确定性, 借鉴 FROSS 高斯思想)
    dino_embedding: bytes | None # DINOv2 特征向量 (用于 ReID)
    semantic_tags: dict          # 从 L2-B 预加载的语义标签
    confidence: float            # 节点置信度
    last_seen: float             # 最后观测时间戳
    state: str                   # "ACTIVE" | "OCCLUDED" | "LOST"

class SpatialEdge:
    """L2-A 空间关系边"""
    relation: str                # "ON_TOP_OF" | "NEAR" | "HELD_BY" | "INSIDE"
    confidence: float            # 关系置信度 (概率性边, 非确定性)
    last_verified: float         # 最后验证时间

class SpatialGraph:
    """L2-A 空间拓扑图 (RustworkX 封装)"""

    def __init__(self):
        self._graph = rx.PyDiGraph()
        self._uuid_to_idx: dict[str, int] = {}

    def add_object(self, node: SpatialNode) -> int:
        """增量添加物体节点"""
        idx = self._graph.add_node(node)
        self._uuid_to_idx[node.uuid] = idx
        return idx

    def update_position(self, uuid: str, pos: tuple, cov: list):
        """更新物体位置 (每帧调用, 必须快)"""
        idx = self._uuid_to_idx[uuid]
        node = self._graph[idx]
        node.position_3d = pos
        node.position_cov = cov

    def add_relation(self, uuid_a: str, uuid_b: str, edge: SpatialEdge):
        """添加/更新空间关系"""
        idx_a = self._uuid_to_idx[uuid_a]
        idx_b = self._uuid_to_idx[uuid_b]
        self._graph.add_edge(idx_a, idx_b, edge)

    def query_on_surface(self, surface_uuid: str) -> list[SpatialNode]:
        """查询: 某个表面上有什么物体"""
        surface_idx = self._uuid_to_idx[surface_uuid]
        children = self._graph.successor_indices(surface_idx)
        return [self._graph[i] for i in children
                if self._graph.get_edge_data(surface_idx, i).relation == "ON_TOP_OF"]

    def query_near(self, uuid: str, radius: float) -> list[SpatialNode]:
        """查询: 某物体附近有什么"""
        target = self._graph[self._uuid_to_idx[uuid]]
        results = []
        for idx in self._graph.node_indices():
            node = self._graph[idx]
            if node.uuid != uuid and _distance(target.position_3d, node.position_3d) < radius:
                results.append(node)
        return results

    def fold_event(self, active_uuids: list[str]) -> int:
        """Gemini 事件折叠: 将一组活跃节点压缩为历史胶囊"""
        indices = [self._uuid_to_idx[u] for u in active_uuids if u in self._uuid_to_idx]
        if len(indices) >= 2:
            capsule_idx = rx.contract_nodes(self._graph, indices, check_cycle=False)
            return capsule_idx
        return -1

    def get_scene_summary(self) -> str:
        """生成当前场景的文本摘要 (用于 Context Injection)"""
        active = [self._graph[i] for i in self._graph.node_indices()
                  if self._graph[i].state == "ACTIVE"]
        lines = []
        for node in active:
            tags = node.semantic_tags.get("summary", "")
            lines.append(f"- {node.class_label} (UUID:{node.uuid[:8]}) "
                        f"at {node.position_3d}, tags: {tags}")
        return "\n".join(lines)
```

---

## 3. L2-B 技术选型：语义注意力图 (RustworkX)

### 3.1 设计变更说明

**v1 方案**（已废弃）: L2-B = Graphiti 的被动 Dict 缓存
**v2 方案**（当前）: L2-B = RustworkX 活图 + 注意力机制 + Graphiti 作为后端存储

变更理由：被动缓存无法支撑注意力机制、触发器、Gemini 主导的聚类折叠等主动运算需求。L2-B 需要与 L2-A 同级的图计算能力。

### 3.2 需求分析

L2-B 的核心需求：
1. **语义联想**: RustworkX 图结构支持 "杯子→咖啡→用户偏好" 的关联遍历
2. **注意力机制**: 仿生注意力权重——新奇增益、习惯衰减、Gemini top-down 聚焦
3. **Graphiti 预加载**: UUID 锁定后自动拉取语义标签/社区摘要到图节点
4. **聚类折叠**: Gemini 通过 L3 的事件分割指令触发 `contract_nodes()` 压缩聚类
5. **触发器**: 状态变化→生成事件→推送给 L3

### 3.3 Graphiti 的角色（后端存储，非 L2-B 本身）

Graphiti 仍然保留，但角色从 "L2-B 本身" 变为 "L2-B 的长期记忆后端"：

```
Graphiti (长期记忆, 异步)
  ↕ preload / commit
L2-B RustworkX (工作记忆, 实时)
  ↕ 事件通知
L3 (认知接口)
```

Graphiti 已内置的 Leiden 社区检测 (`build_communities()`) 为 L2-B 提供"预消化"的语义分组：

```python
await graphiti.build_communities()
results = await graphiti.search("咖啡相关物品")
# entity edges (精确事实) + entity nodes (实体) + community nodes (社区摘要)
```

### 3.4 L2-B 节点与注意力模型

```python
import rustworkx as rx
import time
import math

class SemanticNode:
    """L2-B 语义节点: 物体的 '认知表征'"""
    uuid: str
    class_label: str

    # 从 Graphiti 预加载
    semantic_tags: list[str]         # ["用户最爱", "易碎", "纪念品"]
    community_id: str | None         # Graphiti Leiden 社区 ID
    community_summary: str | None    # 社区摘要文本
    related_memories: list[str]      # 相关记忆片段

    # 注意力系统 (仿生设计)
    attention_weight: float = 0.5    # [0, 1] 当前注意力权重
    novelty_score: float = 1.0       # 新奇度 (首次出现=1.0, 随时间衰减)
    last_attended: float = 0.0       # 上次被关注的时间戳
    attend_count: int = 0            # 被关注次数 (用于习惯化计算)

    # 状态
    emotional_valence: float = 0.0   # 情感效价 [-1, 1]
    salience: str = "background"     # "foreground" | "background" | "peripheral"

class SemanticEdge:
    """L2-B 语义关系边"""
    relation: str          # "ASSOCIATED_WITH" | "PART_OF" | "USED_FOR" | "REMINDS_OF"
    strength: float        # 关联强度 [0, 1]
    source: str            # "graphiti" | "gemini" | "cooccurrence"

class AttentionSystem:
    """仿生注意力机制: 管理 L2-B 所有节点的注意力分配"""

    DECAY_RATE = 0.05        # 习惯化衰减速率
    NOVELTY_HALF_LIFE = 60   # 新奇度半衰期 (秒)
    TOP_DOWN_BOOST = 0.4     # Gemini 自上而下聚焦增益

    def bottom_up_update(self, node: SemanticNode, event_type: str):
        """自下而上注意力 (L2-A 空间事件驱动)"""
        now = time.time()

        if event_type == "NEW_OBJECT":
            node.novelty_score = 1.0
            node.attention_weight = min(1.0, node.attention_weight + 0.3)
            node.salience = "foreground"

        elif event_type == "OBJECT_MOVED":
            node.attention_weight = min(1.0, node.attention_weight + 0.2)

        elif event_type == "OBJECT_LOST":
            node.attention_weight = max(0.0, node.attention_weight - 0.1)
            node.salience = "peripheral"

        node.last_attended = now
        node.attend_count += 1

    def top_down_focus(self, node: SemanticNode):
        """自上而下注意力 (Gemini 通过 L3 下发 focus_on 指令)"""
        node.attention_weight = min(1.0, node.attention_weight + self.TOP_DOWN_BOOST)
        node.salience = "foreground"
        node.last_attended = time.time()

    def tick(self, nodes: list[SemanticNode], dt: float):
        """每帧/每秒调用: 注意力自然衰减"""
        for node in nodes:
            # 习惯化: 被关注次数越多，衰减越快
            habituation = 1 + math.log1p(node.attend_count) * self.DECAY_RATE
            node.attention_weight = max(0.0, node.attention_weight - habituation * dt)

            # 新奇度半衰期衰减
            elapsed = time.time() - node.last_attended
            node.novelty_score = math.exp(-0.693 * elapsed / self.NOVELTY_HALF_LIFE)

            # 降级到 background
            if node.attention_weight < 0.2:
                node.salience = "background"

    def get_attended(self, nodes: list[SemanticNode], top_k: int = 5) -> list[SemanticNode]:
        """获取当前最受关注的 top_k 个节点 (用于 L3 Context Injection)"""
        return sorted(nodes, key=lambda n: n.attention_weight, reverse=True)[:top_k]
```

### 3.5 L2-B 完整封装

```python
class SemanticAttentionGraph:
    """L2-B: 语义注意力图 (腹侧通路 What Pathway)"""

    def __init__(self, graphiti: Graphiti):
        self._graph = rx.PyDiGraph()
        self._uuid_to_idx: dict[str, int] = {}
        self._attention = AttentionSystem()
        self._graphiti = graphiti
        self._triggers: list[dict] = []   # 待消费的事件队列

    async def register_object(self, uuid: str, class_label: str):
        """L2-A 发现新物体 → L2-B 注册语义节点 + Graphiti 预加载"""
        node = SemanticNode(uuid=uuid, class_label=class_label)

        # 异步预加载 Graphiti 语义
        results = await self._graphiti.search(f"object {class_label} UUID:{uuid}")
        node.semantic_tags = self._extract_tags(results)
        node.community_id = self._extract_community_id(results)
        node.community_summary = self._extract_community_summary(results)
        node.related_memories = self._extract_memories(results)

        idx = self._graph.add_node(node)
        self._uuid_to_idx[uuid] = idx

        # 注意力: 新物体 → 高关注
        self._attention.bottom_up_update(node, "NEW_OBJECT")

        # 触发器: 通知 L3
        self._triggers.append({
            "type": "NEW_OBJECT",
            "uuid": uuid,
            "label": class_label,
            "tags": node.semantic_tags,
            "community": node.community_summary,
        })

    def on_spatial_event(self, uuid: str, event_type: str):
        """L2-A 空间事件回调 → 更新注意力"""
        if uuid in self._uuid_to_idx:
            node = self._graph[self._uuid_to_idx[uuid]]
            self._attention.bottom_up_update(node, event_type)
            self._triggers.append({
                "type": event_type,
                "uuid": uuid,
                "label": node.class_label,
                "attention": node.attention_weight,
            })

    def gemini_focus(self, uuid: str):
        """Gemini top-down 注意力: '关注那个杯子'"""
        if uuid in self._uuid_to_idx:
            node = self._graph[self._uuid_to_idx[uuid]]
            self._attention.top_down_focus(node)

    def gemini_fold_cluster(self, uuids: list[str]) -> int:
        """Gemini 事件分割: 将一组关联节点折叠为历史胶囊"""
        indices = [self._uuid_to_idx[u] for u in uuids if u in self._uuid_to_idx]
        if len(indices) >= 2:
            return rx.contract_nodes(self._graph, indices, check_cycle=False)
        return -1

    def drain_triggers(self) -> list[dict]:
        """L3 消费触发器队列"""
        events, self._triggers = self._triggers, []
        return events

    def get_attended_summary(self, top_k: int = 5) -> str:
        """生成当前关注焦点的文本摘要 (给 L3 用)"""
        all_nodes = [self._graph[i] for i in self._graph.node_indices()]
        attended = self._attention.get_attended(all_nodes, top_k)
        lines = []
        for n in attended:
            tags_str = ", ".join(n.semantic_tags[:3]) if n.semantic_tags else "unknown"
            lines.append(
                f"- {n.class_label} (attn:{n.attention_weight:.2f}) [{tags_str}]"
            )
        return "\n".join(lines)
```

### 3.6 Graphiti 社区检测仍然有用

虽然 L2-B 升级为 RustworkX 图，但 Graphiti 的 Leiden 社区检测不浪费：
- **预消化分组**: Graphiti 的社区摘要作为 L2-B 节点的 `community_summary` 字段预加载
- **长期聚类**: Graphiti 在后台异步做大规模知识聚类，结果喂给 L2-B
- **L2-B 的折叠是实时的**: Gemini 事件分割触发的 `contract_nodes()` 是工作记忆内的操作
- **Graphiti 的聚类是历史的**: `build_communities()` 是跨所有历史 episode 的全局聚类

两者互补：**L2-B 做实时工作记忆折叠，Graphiti 做长期历史聚类**。

---

## 4. L3 技术选型：认知接口层

### 4.1 L3 的定位

L3 不是一个图数据结构，而是一个**事件驱动的观察者-调度器层**。它是 DSG 与 Gemini 之间的唯一通信接口。

### 4.2 L3 的组成

```python
class CognitiveInterface:
    """L3: 前额叶接口 (Narrative Layer)"""

    def __init__(self, agent: Agent, l2a: SpatialGraph, l2b: SemanticAttentionGraph):
        self._agent = agent
        self._l2a = l2a
        self._l2b = l2b
        self._atmosphere = AtmosphereState()
        self._event_active = True

    # ===== 观察者 (Observers) =====

    async def observe_triggers(self):
        """消费 L2-B 的触发器，生成上下文注入"""
        events = self._l2b.drain_triggers()
        if not events:
            return

        significant = [e for e in events if self._is_significant(e)]
        if significant:
            context_text = self._format_events(significant)
            chat_ctx = self._agent.chat_ctx.copy()
            chat_ctx.add_message(role="user", content=[f"[SCENE]\n{context_text}"])
            await self._agent.update_chat_ctx(chat_ctx)

    async def periodic_snapshot(self):
        """定时 (每 30s): 生成场景+氛围快照"""
        spatial_summary = self._l2a.get_scene_summary()
        attention_summary = self._l2b.get_attended_summary(top_k=3)
        atmosphere = self._atmosphere.describe()

        snapshot = (
            f"[PERIODIC_SENSE]\n"
            f"Atmosphere: {atmosphere}\n"
            f"Attended: {attention_summary}\n"
            f"Scene: {spatial_summary}"
        )
        # 使用 on_user_turn_completed 而非主动推送，避免打断对话
        self._pending_snapshot = snapshot

    # ===== Gemini 下行指令处理 =====

    async def handle_event_end(self, participating_uuids: list[str]):
        """Gemini Tool Call: event_end → 折叠 L2-B + 归档 Graphiti"""
        # 1. L2-B 实时折叠
        self._l2b.gemini_fold_cluster(participating_uuids)

        # 2. Graphiti 归档 (异步, 不阻塞)
        episode_body = self._compose_episode(participating_uuids)
        asyncio.create_task(self._archive_to_graphiti(episode_body))

        # 3. 更新氛围
        self._atmosphere.on_event_boundary()

    async def handle_focus_on(self, uuid: str):
        """Gemini Tool Call: focus_on(uuid) → top-down 注意力"""
        self._l2b.gemini_focus(uuid)

    # ===== 氛围状态 =====

    def _is_significant(self, event: dict) -> bool:
        """判断事件是否值得推送给 Gemini (避免刷屏)"""
        if event["type"] == "NEW_OBJECT":
            return True
        if event["type"] == "OBJECT_MOVED" and event.get("attention", 0) > 0.5:
            return True
        return False


class AtmosphereState:
    """L3 氛围节点: 维护高层语义状态"""

    def __init__(self):
        self.mood: str = "neutral"           # "focused" | "relaxed" | "curious" | ...
        self.context: str = "idle"           # "deep_work" | "casual_chat" | "exploration"
        self.noise_level: str = "quiet"
        self.event_count: int = 0
        self.last_boundary: float = time.time()

    def on_event_boundary(self):
        self.event_count += 1
        self.last_boundary = time.time()

    def describe(self) -> str:
        elapsed = time.time() - self.last_boundary
        return f"{self.mood}, {self.context}, {int(elapsed)}s since last event"
```

### 4.3 L3 的 Gemini Tool 定义

```python
@function_tool
async def event_end(participating_objects: list[str], summary: str) -> str:
    """当你认为一个话题或活动结束时调用。
    将当前事件中的活跃物体折叠为历史记录。

    Args:
        participating_objects: 参与此事件的物体 UUID 列表
        summary: 对此事件的一句话总结
    """
    await cognitive_interface.handle_event_end(participating_objects)
    return f"事件已归档: {summary}"

@function_tool
async def focus_on(object_uuid: str) -> str:
    """当你想更仔细观察某个物体时调用。
    提升该物体在 DSG 中的注意力权重。

    Args:
        object_uuid: 要关注的物体 UUID
    """
    await cognitive_interface.handle_focus_on(object_uuid)
    return f"已聚焦: {object_uuid}"

@function_tool
async def query_scene(question: str) -> str:
    """查询当前场景的空间和语义信息。

    Args:
        question: 自然语言问题 (如 "桌上有什么" "杯子旁边是什么")
    """
    spatial = l2a.get_scene_summary()
    semantic = l2b.get_attended_summary()
    return f"空间: {spatial}\n语义: {semantic}"
```

---

## 5. 四层交互协议

### 5.1 完整数据流

```
[感知上行: 自下而上]
  L1 (30fps帧) → 过滤 → L2-A (空间事件)
                              ↓
                         L2-B (注意力更新 + 触发器)
                              ↓
                         L3 (观察者生成上下文)
                              ↓
                         Gemini (感知到场景变化)

[认知下行: 自上而下]
  Gemini → Tool: event_end → L3.EventBoundary
                                  ↓
                             L2-B.contract_nodes() (实时折叠)
                                  ↓
                             Graphiti.add_episode() (长期归档)

  Gemini → Tool: focus_on → L3 → L2-B.Attention (top-down 聚焦)

[记忆双向]
  Graphiti → L2-B.preload() (长期记忆 → 工作记忆)
  L2-B 事件归档 → Graphiti.add_episode() (工作记忆 → 长期记忆)
```

### 5.2 事件驱动更新矩阵

| 事件 | L2-A | L2-B | L3 | Graphiti |
|:-----|:-----|:-----|:---|:---------|
| 新物体进入 | add_object() | register + preload + attention↑ | trigger→inject | search() |
| ReID 成功 | confirm_id() | update tags + attention↑ | trigger→inject | search() |
| 物体移动 | update_pos() | attention↑ (if significant) | (阈值过滤) | — |
| 物体消失 | set_state(LOST) | attention↓ | trigger→inject | — |
| 关系变化 | add_relation() | trigger | inject | — |
| Gemini focus_on | — | top_down_focus() | relay | — |
| Gemini event_end | — | contract_nodes() | archive + atmosphere | add_episode() |
| 定时快照 (30s) | — | — | snapshot→inject | — |
| 社区重建 (30min) | — | refresh community tags | — | build_communities() |

---

## 6. 技术栈总结

| 组件 | 技术选择 | 理由 |
|:-----|:---------|:-----|
| **L1 追踪** | SAM2 + DINOv2 + List[Dict] | 30fps 帧处理，噪声过滤 |
| **L2-A 空间图** | RustworkX | GIL-free, contract_nodes, 纯 pip |
| **L2-A 分层** | DSGLayer 枚举 (Objects/Surfaces/Zones) | 借鉴 Spark-DSG/Hydra |
| **L2-A 位置** | 3D 高斯 (均值+协方差) | 借鉴 FROSS |
| **L2-B 语义图** | RustworkX | 与 L2-A 同引擎，支持 contract_nodes 折叠 |
| **L2-B 注意力** | 自定义 AttentionSystem | 仿生：新奇增益/习惯衰减/top-down 聚焦 |
| **L2-B 后端** | Graphiti + Neo4j | 长期记忆，Leiden 社区检测，三范围搜索 |
| **L3 观察者** | Python asyncio 事件循环 | 触发器消费 + 定时快照 + 氛围维护 |
| **L3 → Gemini** | LiveKit Agent update_chat_ctx() | 替代旧 XML 注入 |
| **Gemini → L3** | function_tool (event_end / focus_on) | Gemini 主导事件分割和注意力控制 |

### 三个 RustworkX 图实例

| 图 | 节点类型 | 边类型 | 更新频率 |
|:---|:---------|:-------|:---------|
| L2-A | SpatialNode (位置/层级/置信度) | SpatialEdge (ON_TOP_OF/NEAR/HELD_BY) | 事件驱动 (~1-5Hz) |
| L2-B | SemanticNode (标签/注意力/情感) | SemanticEdge (ASSOCIATED/REMINDS_OF) | 事件驱动 + 注意力 tick |

L2-A 和 L2-B 是**两个独立的 RustworkX 图实例**，通过 UUID 关联。L2-A 的空间事件通过回调通知 L2-B。

---

## 6. 关键参考链接

- Spark-DSG: https://github.com/MIT-SPARK/Spark-DSG
- Hydra (使用 Spark-DSG): https://github.com/MIT-SPARK/Hydra
- FROSS (3D SSG): https://arxiv.org/abs/2507.19993
- RustworkX: https://github.com/Qiskit/rustworkx
- Graphiti Communities: https://help.getzep.com/graphiti/core-concepts/communities
- Microsoft GraphRAG Clustering: https://github.com/microsoft/graphrag/blob/main/graphrag/index/operations/cluster_graph.py
- LiveKit Vision Docs: https://docs.livekit.io/agents/build/vision/
- 3D Scene Graphs with NetworkX: https://learngeodata.eu/3d-scene-graphs-for-spatial-ai-with-networkx-and-openusd
