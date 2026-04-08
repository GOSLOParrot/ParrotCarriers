# DSG 节点抽象设计 · 触发器协议 · 参考项目对应

> 生成日期: 2026-02-24
> 核心问题:
> 1. 当前 MVP 设计还缺什么？
> 2. L2-A / L2-B 的节点类继承体系怎么设计？
> 3. L2-B 与 Graphiti 的对接设计 (自定义实体类型)
> 4. 各层各模块的触发器和事件协议
> 5. 每个层/模块该学习哪些 SSG / GraphRAG 项目
> 6. 场景特化设计 (Desktop / Indoor MVP)

---

## 0. 当前架构评估与缺失清单

### 0.1 已完成的设计 (Phase 0)

| # | 设计内容 | 文档 | 成熟度 |
|:--|:---------|:-----|:-------|
| 1 | 四层仿生架构定义 | `09`, `10` | ★★★★★ 清晰 |
| 2 | L1 StabilityGate + SceneManager | `11`, `12` | ★★★★☆ 框架清晰，阈值需实测 |
| 3 | L2-A SpatialGraph 基础封装 | `09` §2 | ★★★☆☆ 有 API 骨架，无完整节点体系 |
| 4 | L2-B SemanticAttentionGraph + 注意力 | `09` §3 | ★★★☆☆ 注意力模型好，节点体系不完整 |
| 5 | L3 CognitiveInterface + Timeline | `09` §4, `12` §3 | ★★★★☆ 清晰 |
| 6 | Gemini Tool 定义 | `09` §4.3 | ★★★☆☆ 基础版，缺 fly_to/remember |
| 7 | 场景折叠/展开 | `12` §2 | ★★★★☆ 清晰 |
| 8 | SOUL + 记忆分区 | `13` | ★★★★☆ 概念清晰 |
| 9 | 行为树 + 资源锁 | `14` | ★★★☆☆ 框架设计好，Phase 1 用简化版 |
| 10 | 前后端同步协议 | `14` §3 | ★★★★☆ 清晰 |
| 11 | APP 生命周期 + 网络降级 | `16` (口头) | ★★★☆☆ 有方案，未文档化 |

### 0.2 MVP 前仍需完成的设计

| # | 缺失项 | 重要性 | 本文覆盖 |
|:--|:-------|:-------|:---------|
| **A** | **DSG 节点类继承体系** — L2-A/L2-B 的基类、继承类完整定义 | P0 (代码骨架依赖) | §1-2 |
| **B** | **Graphiti 自定义实体类型** — L2-B ↔ Graphiti 的 Schema 对齐 | P0 (记忆系统依赖) | §3 |
| **C** | **完整触发器协议** — 每层的输入/输出事件格式 | P0 (模块集成依赖) | §4 |
| **D** | **场景特化节点** — Desktop/Indoor 下节点和边的差异 | P1 (Phase 1 实现依赖) | §6 |
| **E** | **Gemini Tool 完整清单** — 包括 fly_to / remember / describe_object | P1 | §4.5 |
| **F** | L1 输出格式定义 — tracker.py 的精确输出 Schema | P1 | §4.1 |
| **G** | ReID 匹配策略细节 — DINOv2 embedding 距离阈值、多视角融合 | P2 (实测定) | 略 |
| **H** | 注意力参数调优 — 衰减速率/半衰期/增益常数 | P2 (实测定) | 略 |

---

## 1. L2-A 节点类继承体系 (空间拓扑)

### 1.1 设计参考: Spark-DSG 的节点继承

Spark-DSG (MIT-SPARK) 的 C++ 节点继承体系是目前最成熟的 3D DSG 实现:

```
NodeAttributes (base: position, last_update_time, is_active, is_predicted, metadata)
├── SemanticNodeAttributes (+name, color, bounding_box, semantic_label, semantic_feature)
│   ├── ObjectNodeAttributes (+mesh_connections, registered, world_R_object)
│   │   └── KhronosObjectAttributes (+first/last_observed_ns, mesh, trajectory_*)
│   ├── RoomNodeAttributes (+semantic_class_probabilities)
│   ├── PlaceNodeAttributes (+distance_to_obstacle, num_basis_points, frontiers)
│   └── Place2dNodeAttributes (+boundary, ellipse_matrix)
└── AgentNodeAttributes (+timestamp, world_R_body, dbow_ids)
```

**核心启示**:
1. **所有节点共享 position** — DSG 节点必须有空间位置
2. **语义层基于空间层继承** — 先有空间位置，再加语义属性
3. **每层有专用属性类** — 而非用一个万能 Dict
4. **时间信息不可少** — `first_observed_ns` / `last_observed_ns` 对 Khronos 时序至关重要

### 1.2 设计参考: ConceptGraphs 的对象表示

ConceptGraphs 采用 Dict-based 方案，每个物体包含:

| 字段 | 类型 | 用途 |
|:-----|:-----|:-----|
| `clip_ft` | Tensor (D,) | CLIP 视觉特征 (多视角融合后) |
| `text_ft` | Tensor (D,) | CLIP 文本特征 (从 caption 生成) |
| `pcd` | PointCloud | 3D 点云 (多视角融合) |
| `bbox` | OrientedBoundingBox | 3D 有向包围盒 |
| `class_id` | ndarray | 语义类别 ID (多视角投票) |
| `inst_color` | RGB | 实例颜色 |

**核心启示**:
1. **CLIP embedding 是核心** — 多视角融合后的特征向量是物体身份的基础
2. **多视角投票** — `class_id` 不是一次检测的结果，而是多帧投票
3. **我们的等价物**: DINOv2 embedding = ConceptGraphs 的 clip_ft

### 1.3 我们的 L2-A 节点继承体系

```python
from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, field
from enum import IntEnum, Enum
from typing import Optional
import time
import uuid as uuid_lib

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  层级枚举
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class DSGLayer(IntEnum):
    """空间图分层 (借鉴 Spark-DSG/Hydra 的 DsgLayers)"""
    OBJECTS = 0      # 物理物体 (杯子、手机、书)
    SURFACES = 1     # 承载面 (桌面、地面、手掌、架子)
    ZONES = 2        # 功能区域 (工作区、厨房区、沙发区)
    # Phase 2:
    # ROOMS = 3      # 房间 (客厅、卧室)
    # BUILDING = 4   # 建筑

class NodeState(Enum):
    """节点可见性状态 (物理恒常性的核心, ADR-013)"""
    ACTIVE = "active"          # 当前帧可见且被追踪
    OCCLUDED = "occluded"      # 短暂遮挡 (预计很快回来)
    OUT_OF_VIEW = "out_of_view"  # 离开视野但仍在当前场景
    LOST = "lost"              # 超时未见，可能被移走了
    ANCHORED = "anchored"      # 有 ARCore 锚点固定位置

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  基类
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class DSGNode(ABC):
    """所有 DSG 节点的抽象基类 — L2-A 和 L2-B 共享"""
    uuid: str = field(default_factory=lambda: str(uuid_lib.uuid4()))
    layer: DSGLayer = DSGLayer.OBJECTS
    created_at: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    state: NodeState = NodeState.ACTIVE
    confidence: float = 1.0

    def age(self) -> float:
        return time.time() - self.created_at

    def since_last_seen(self) -> float:
        return time.time() - self.last_seen

@dataclass
class SpatialNode(DSGNode):
    """L2-A 空间节点基类 — 所有有物理位置的节点"""
    position_3d: tuple[float, float, float] = (0.0, 0.0, 0.0)
    position_cov: tuple[float, ...] = (0.1, 0.1, 0.1)  # 位置不确定性 (借鉴 FROSS 高斯)
    velocity: tuple[float, float, float] = (0.0, 0.0, 0.0)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  L2-A 具体节点类
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class ObjectNode(SpatialNode):
    """L2-A 物体节点 — 一个被追踪的物理物体

    对标:
    - Spark-DSG ObjectNodeAttributes (bounding_box, semantic_label, semantic_feature)
    - ConceptGraphs MapObjectList (clip_ft, bbox, class_id)
    """
    layer: DSGLayer = DSGLayer.OBJECTS

    # 身份
    class_label: str = ""                      # 类别标签 ("cup", "phone")
    class_confidence: float = 0.0              # 分类置信度
    class_votes: dict[str, int] = field(default_factory=dict)  # 多帧投票 (学 ConceptGraphs)

    # 追踪
    track_id: int = -1                         # SAM2 tracker 分配的 track ID
    dino_embedding: Optional[bytes] = None     # DINOv2 特征 (ReID 核心, 等价于 ConceptGraphs clip_ft)
    embedding_timestamp: float = 0.0           # embedding 提取时间

    # 几何 (简化版 — 我们没有点云，只有 2D mask)
    bbox_2d: Optional[tuple[int, int, int, int]] = None    # 最新帧的 2D bbox (x, y, w, h)
    estimated_size: Optional[tuple[float, float, float]] = None  # 估计 3D 尺寸 (来自深度+mask)

    # 关联
    on_surface_uuid: Optional[str] = None      # 所在承载面 UUID
    portable: bool = False                     # 是否可被携带跨场景

    def vote_class(self, label: str):
        self.class_votes[label] = self.class_votes.get(label, 0) + 1
        best = max(self.class_votes, key=self.class_votes.get)
        self.class_label = best
        total = sum(self.class_votes.values())
        self.class_confidence = self.class_votes[best] / total

@dataclass
class SurfaceNode(SpatialNode):
    """L2-A 承载面节点 — AR 平面、桌面、手掌

    对标: Spark-DSG PlaceNodeAttributes / Place2dNodeAttributes
    """
    layer: DSGLayer = DSGLayer.SURFACES

    surface_type: str = "horizontal"   # "horizontal" | "vertical" | "hand"
    area: float = 0.0                  # 面积 (m²)
    boundary_points: list[tuple[float, float, float]] = field(default_factory=list)
    ar_plane_id: Optional[str] = None  # ARCore/AR Foundation 平面 ID
    anchor_id: Optional[str] = None    # ARCore 锚点 ID (持久化位置)

    # 承载关系自动推断用
    normal: tuple[float, float, float] = (0.0, 1.0, 0.0)   # 法向量
    elevation: float = 0.0             # 高度 (相对地面)

@dataclass
class ZoneNode(SpatialNode):
    """L2-A 功能区域节点 — 由多个 Surface 和 Object 聚类产生

    对标: Spark-DSG RoomNodeAttributes
    """
    layer: DSGLayer = DSGLayer.ZONES

    zone_name: str = ""                # "工作区" / "厨房区" / "沙发区"
    zone_type: str = "functional"      # "functional" | "spatial"
    radius: float = 1.0                # 区域半径 (m)
    member_surfaces: list[str] = field(default_factory=list)  # 包含的 Surface UUID
    member_objects: list[str] = field(default_factory=list)   # 包含的 Object UUID

    # Phase 2: 自动从 ARCore 平面分布推断
    auto_detected: bool = False

@dataclass
class HandNode(SpatialNode):
    """L2-A 用户手部节点 — 特殊的交互实体"""
    layer: DSGLayer = DSGLayer.OBJECTS  # 手是 OBJECTS 层但有特殊属性

    hand_side: str = "right"           # "left" | "right"
    gesture: str = "none"              # "open" | "closed" | "pointing" | "pinch" | "none"
    gesture_confidence: float = 0.0
    is_holding: Optional[str] = None   # 持握的物体 UUID

@dataclass
class ParrotAnchorNode(SpatialNode):
    """L2-A 鹦鹉停靠点 — 标记鹦鹉可以停靠/飞到的位置"""
    layer: DSGLayer = DSGLayer.OBJECTS

    anchor_type: str = "surface"       # "surface" | "hand" | "shoulder" | "free"
    target_surface_uuid: Optional[str] = None
    landing_offset: tuple[float, float, float] = (0.0, 0.0, 0.0)
    is_occupied: bool = False          # 鹦鹉当前是否在这个点

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  L2-A 边类型
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SpatialRelation(Enum):
    """空间关系类型 — 学习 3DSSG + ConceptGraphs"""
    ON_SURFACE = "on_surface"        # 物体在某承载面上
    NEAR = "near"                    # 距离接近 (阈值由 SceneProfile 定)
    HELD_BY = "held_by"              # 被手持握
    INSIDE = "inside"                # 在容器内
    ABOVE = "above"                  # 在...上方 (不接触)
    NEXT_TO = "next_to"              # 紧挨着
    PART_OF_ZONE = "part_of_zone"    # 属于某 Zone
    PARROT_AT = "parrot_at"          # 鹦鹉停在此处

@dataclass
class SpatialEdge:
    """L2-A 空间关系边"""
    relation: SpatialRelation
    confidence: float = 1.0
    last_verified: float = field(default_factory=time.time)
    distance: Optional[float] = None   # 两节点间距离 (m)
```

### 1.4 L2-A 层级关系图

```
Zone("工作区")                          Zone("厨房区")
  │ PART_OF_ZONE                          │ PART_OF_ZONE
  ├── Surface("桌面")                     └── Surface("台面")
  │     │ ON_SURFACE                            │ ON_SURFACE
  │     ├── Object("杯子")                      ├── Object("水壶")
  │     ├── Object("键盘")                      └── Object("碗")
  │     ├── Object("手机")
  │     └── ParrotAnchor("桌面停靠点")
  │
  └── Surface("地面-工作区")
        │ ON_SURFACE
        └── Object("背包")

Hand("右手") ──HELD_BY──→ Object("笔")
```

---

## 2. L2-B 节点类继承体系 (语义注意力)

### 2.1 设计理念: 与 L2-A 平行但独立

L2-B 的每个节点通过 UUID 与 L2-A 对应节点关联，但属性完全不同:
- **L2-A 回答"在哪里"** — 位置、几何、空间关系
- **L2-B 回答"是什么/为什么重要"** — 语义、注意力、情感、记忆关联

```
L2-A: ObjectNode(uuid="abc", position=(1.2, 0.8, -0.5), class_label="cup")
  │ UUID 关联
  ▼
L2-B: ObjectSemanticNode(uuid="abc", tags=["奶奶的杯子","易碎"], attention=0.85)
  │ Graphiti 预加载
  ▼
Graphiti: EntityNode(name="蓝色杯子", group_id="objects", summary="主人奶奶留下的...")
```

### 2.2 L2-B 节点继承体系

```python
from __future__ import annotations

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  L2-B 注意力相关枚举
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Salience(Enum):
    """注意力显著性等级"""
    FOREGROUND = "foreground"      # 当前焦点 (Gemini 正在谈论 / 刚出现)
    ACTIVE = "active"              # 活跃关注 (注意力权重 > 0.4)
    BACKGROUND = "background"      # 背景存在 (权重 0.1-0.4)
    PERIPHERAL = "peripheral"      # 边缘意识 (权重 < 0.1, 快被遗忘)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  L2-B 基类
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class SemanticNode(DSGNode):
    """L2-B 语义节点基类 — 每个被认知的实体都有"""

    # 注意力系统 (仿生)
    attention_weight: float = 0.5        # [0, 1] 总注意力权重
    novelty_score: float = 1.0           # 新奇度 (首次=1.0, 衰减)
    habituation_count: int = 0           # 被关注次数 (习惯化因子)
    last_attended: float = 0.0           # 上次受关注时间
    salience: Salience = Salience.BACKGROUND

    # 语义标签 (多来源)
    semantic_tags: list[str] = field(default_factory=list)       # ["易碎", "常用"]
    user_given_name: Optional[str] = None                        # 用户起的名字 ("奶奶的杯子")

    # 情感
    emotional_valence: float = 0.0       # [-1, 1] 情感效价 (正面/负面)
    emotional_source: str = ""           # 情感来源 ("用户反应" / "记忆关联")

    # Graphiti 关联 (预加载缓存)
    graphiti_entity_uuid: Optional[str] = None  # Graphiti 中对应 EntityNode 的 UUID
    community_id: Optional[str] = None
    community_summary: Optional[str] = None
    related_memories: list[str] = field(default_factory=list)   # 关联的记忆片段 (前5条)

    def is_notable(self) -> bool:
        """是否值得告诉 Gemini"""
        return self.attention_weight > 0.4 or self.salience == Salience.FOREGROUND

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  L2-B 具体节点类
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class ObjectSemanticNode(SemanticNode):
    """L2-B 物体语义节点 — 物体的"认知档案" """

    class_label: str = ""
    category: str = ""                   # 大类: "容器" / "工具" / "装饰" / "食物"
    typical_location: str = ""           # 通常在哪: "桌面" / "厨房"
    owner_relation: str = ""             # 归属: "主人的" / "奶奶的" / "共用"
    material: str = ""                   # 材质: "陶瓷" / "金属" / "塑料"
    color_description: str = ""          # 颜色描述: "蓝色" / "透明"
    is_precious: bool = False            # 用户标记为珍贵

    # 使用统计 (帮助理解用户习惯)
    interaction_count: int = 0           # 被用户拿起/放下的次数
    last_interaction: float = 0.0

@dataclass
class SurfaceSemanticNode(SemanticNode):
    """L2-B 承载面语义节点"""

    surface_name: str = ""               # "主人的工作桌" / "茶几"
    typical_objects: list[str] = field(default_factory=list)  # 常见物品
    usage_pattern: str = ""              # "工作" / "休息" / "吃饭"

@dataclass
class ZoneSemanticNode(SemanticNode):
    """L2-B 区域语义节点"""

    zone_label: str = ""                 # "工作区" / "休息区"
    atmosphere: str = ""                 # "安静" / "热闹"
    time_pattern: str = ""               # "深夜常用" / "白天常用"

@dataclass
class PersonSemanticNode(SemanticNode):
    """L2-B 人物语义节点 — 主要是用户自己"""

    person_role: str = "owner"           # "owner" | "guest" | "family"
    current_activity: str = ""           # "工作" / "休息" / "做饭"
    mood_estimate: str = ""              # "专注" / "放松" / "疲惫" (从行为推断)

@dataclass
class EventCapsuleNode(SemanticNode):
    """L2-B 事件胶囊节点 — contract_nodes() 后产生的折叠节点"""

    event_summary: str = ""              # Gemini 给的事件总结
    participating_uuids: list[str] = field(default_factory=list)
    started_at: float = 0.0
    ended_at: float = 0.0
    archived_to_graphiti: bool = False   # 是否已归档

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  L2-B 边类型
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SemanticRelation(Enum):
    """语义关系类型"""
    ASSOCIATED_WITH = "associated_with"    # 通用关联 (ConceptGraphs LLM-derived edges)
    REMINDS_OF = "reminds_of"              # 记忆唤起 ("这个杯子让我想起...")
    USED_FOR = "used_for"                  # 功能关联 ("杯子用来喝水")
    BELONGS_TO = "belongs_to"              # 归属关系 ("杯子属于主人")
    CO_OCCURRED_WITH = "co_occurred_with"  # 共现关系 (在同一事件中出现)
    PART_OF_EVENT = "part_of_event"        # 参与某个事件胶囊

@dataclass
class SemanticEdge:
    """L2-B 语义关系边"""
    relation: SemanticRelation
    strength: float = 0.5          # [0, 1] 关联强度
    source: str = "observation"    # "graphiti" | "gemini" | "observation" | "cooccurrence"
    created_at: float = field(default_factory=time.time)
```

### 2.3 L2-A ↔ L2-B 完整对应表

| L2-A 节点类 | L2-B 对应类 | UUID 共享 | 说明 |
|:-----------|:-----------|:---------|:-----|
| `ObjectNode` | `ObjectSemanticNode` | 是 | 1:1 对应，L2-A 发现即注册 L2-B |
| `SurfaceNode` | `SurfaceSemanticNode` | 是 | Surface 也有语义 ("主人的工作桌") |
| `ZoneNode` | `ZoneSemanticNode` | 是 | Zone 也有语义 ("安静的工作区") |
| `HandNode` | `PersonSemanticNode` | 否 | 手→人，语义上是"主人"不是"手" |
| `ParrotAnchorNode` | (无) | — | 纯空间用途，无独立语义 |
| (无) | `EventCapsuleNode` | — | L2-B 独有，事件折叠后产生 |

---

## 3. Graphiti 自定义实体类型 — 与 L2-B 的桥梁

### 3.1 Graphiti 的自定义能力验证

Graphiti 支持通过 Pydantic `BaseModel` 定义自定义实体和边类型。关键约束:
- **受保护字段**: `uuid`, `name`, `group_id`, `labels`, `created_at`, `summary`, `attributes`, `name_embedding` 不能用作自定义属性
- **所有自定义字段必须 Optional** — 因为 LLM 提取不一定能填满所有字段
- **edge_type_map 约束边** — 指定哪些实体对之间可以有哪种边

### 3.2 Graphiti 自定义实体类型定义

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ━━━━━━━━━ objects 分区的实体类型 ━━━━━━━━━

class PhysicalObject(BaseModel):
    """物理物体的持久化知识 (group_id="objects")
    
    L2-B ObjectSemanticNode 的持久化版本。
    L2-B 是实时工作记忆，Graphiti 是长期记忆。
    """
    category: Optional[str] = Field(None, description="物品大类: 容器/工具/装饰/食物/电子/文具")
    material: Optional[str] = Field(None, description="材质: 陶瓷/金属/塑料/玻璃/木头/布")
    color: Optional[str] = Field(None, description="颜色描述")
    typical_location: Optional[str] = Field(None, description="通常在哪个区域")
    owner_relation: Optional[str] = Field(None, description="和谁的关系: 主人的/奶奶的/共用")
    is_precious: Optional[bool] = Field(None, description="是否被主人标记为珍贵")
    origin_story: Optional[str] = Field(None, description="来历故事")

class Place(BaseModel):
    """地点/区域的持久化知识 (group_id="objects")"""
    place_type: Optional[str] = Field(None, description="桌面/房间/区域")
    typical_activity: Optional[str] = Field(None, description="在此处常做的事")
    typical_time: Optional[str] = Field(None, description="常使用的时间段")

# ━━━━━━━━━ personality 分区的实体类型 ━━━━━━━━━

class Person(BaseModel):
    """人物的持久化知识 (group_id="personality")"""
    relationship: Optional[str] = Field(None, description="和鹦鹉/主人的关系")
    preferences: Optional[str] = Field(None, description="已知偏好")
    habits: Optional[str] = Field(None, description="行为习惯")
    emotional_notes: Optional[str] = Field(None, description="情感相关观察")

class Habit(BaseModel):
    """用户习惯 (group_id="personality")"""
    frequency: Optional[str] = Field(None, description="频率: 每天/经常/偶尔")
    time_of_day: Optional[str] = Field(None, description="通常发生时间")
    context: Optional[str] = Field(None, description="发生的场景/上下文")

# ━━━━━━━━━ vocabulary 分区的实体类型 ━━━━━━━━━

class Concept(BaseModel):
    """概念/词汇 (group_id="vocabulary")"""
    domain: Optional[str] = Field(None, description="领域: 技术/生活/艺术/游戏")
    explanation: Optional[str] = Field(None, description="简要解释")
    learned_from: Optional[str] = Field(None, description="从哪里学到的")

# ━━━━━━━━━ 自定义边类型 ━━━━━━━━━

class OwnershipEdge(BaseModel):
    """归属关系边"""
    ownership_type: Optional[str] = Field(None, description="拥有/继承/借用/共用")
    since_when: Optional[str] = Field(None, description="从什么时候开始")
    emotional_weight: Optional[str] = Field(None, description="情感重要性: 高/中/低")

class UsageEdge(BaseModel):
    """使用关系边"""
    usage_purpose: Optional[str] = Field(None, description="使用目的")
    frequency: Optional[str] = Field(None, description="使用频率")

class LocationEdge(BaseModel):
    """位置关系边"""
    location_type: Optional[str] = Field(None, description="常放/有时放/偶尔放")
    specific_spot: Optional[str] = Field(None, description="具体位置描述")
```

### 3.3 Graphiti 配置汇总

```python
GRAPHITI_ENTITY_TYPES = {
    "PhysicalObject": PhysicalObject,
    "Place": Place,
    "Person": Person,
    "Habit": Habit,
    "Concept": Concept,
}

GRAPHITI_EDGE_TYPES = {
    "Ownership": OwnershipEdge,
    "Usage": UsageEdge,
    "Location": LocationEdge,
}

GRAPHITI_EDGE_TYPE_MAP = {
    ("Person", "PhysicalObject"): ["Ownership", "Usage"],
    ("PhysicalObject", "Place"): ["Location"],
    ("Person", "Place"): ["Usage"],
    ("Person", "Habit"): ["RELATES_TO"],
    ("Person", "Person"): ["RELATES_TO"],
    ("Entity", "Entity"): ["RELATES_TO"],  # fallback
}
```

### 3.4 L2-B ↔ Graphiti 数据流

```
ObjectSemanticNode (L2-B 实时)             PhysicalObject (Graphiti 持久)
─────────────────────────                  ────────────────────────────
class_label: "cup"                    ←→   (通过 name 关联)
category: "容器"                       ←    category: "容器"
material: "陶瓷"                       ←    material: "陶瓷"
color_description: "蓝色"             ←    color: "蓝色"
typical_location: "桌面"               ←    typical_location: "桌面"
owner_relation: "奶奶的"               ←    owner_relation: "奶奶的"
is_precious: True                      ←    is_precious: True
                                            origin_story: "主人奶奶留下的..."

semantic_tags: ["奶奶的杯子","易碎"]    ←    (从 Graphiti search 结果提取)
community_id: "cm_kitchenware"         ←    (Leiden 社区 ID)
community_summary: "厨房用品社区..."     ←    (社区摘要)
related_memories: ["主人昨天用它喝茶"]   ←    (关联 episode)

attention_weight: 0.85                      (纯 L2-B 运行时，不持久化)
novelty_score: 0.3                          (纯 L2-B 运行时)
emotional_valence: 0.6                 ←    (可以从 personality 分区推断)
```

**加载方向**: Graphiti → L2-B (预加载)
**写入方向**: L2-B 通过 L3 ArchiveObserver → Graphiti (event_end 归档)

### 3.5 Graphiti 写入时使用自定义类型

```python
async def preload_object_semantics(
    graphiti: Graphiti,
    uuid: str,
    class_label: str,
) -> dict:
    """L2-B 注册新物体时，从 Graphiti 预加载语义"""
    
    from graphiti_core.search.search_filters import SearchFilters

    obj_results = await graphiti.search(
        query=f"object {class_label}",
        group_ids=["objects"],
        search_filter=SearchFilters(node_labels=["PhysicalObject"]),
    )

    pref_results = await graphiti.search(
        query=f"user preference {class_label}",
        group_ids=["personality"],
        search_filter=SearchFilters(node_labels=["Person"]),
    )

    return {
        "tags": _extract_tags(obj_results),
        "community_id": _extract_community(obj_results),
        "community_summary": _extract_summary(obj_results),
        "memories": _extract_facts(obj_results + pref_results),
        "emotional_valence": _estimate_valence(pref_results),
    }

async def archive_episode_with_types(
    graphiti: Graphiti,
    episode_body: str,
    group_id: str,
    source_description: str,
):
    """带自定义类型的 episode 归档"""
    await graphiti.add_episode(
        name=f"ep_{time.time():.0f}",
        episode_body=episode_body,
        source_description=source_description,
        reference_time=datetime.now(timezone.utc),
        entity_types=GRAPHITI_ENTITY_TYPES,
        edge_types=GRAPHITI_EDGE_TYPES,
        edge_type_map=GRAPHITI_EDGE_TYPE_MAP,
        group_id=group_id,
    )
```

---

## 4. 各层触发器与事件协议

### 4.1 L1 → L2-A: 物理追踪事件

L1 (tracker.py + noise filter) 输出的是**经过过滤的、有意义的变化**，而非原始帧数据。

```python
@dataclass
class L1Event:
    """L1 视觉管线输出事件"""
    timestamp: float
    event_type: str         # 见下表
    track_id: int           # SAM2 track ID
    payload: dict           # 事件特化数据

# L1 输出事件类型:
L1_EVENTS = {
    # 物体生命周期
    "TRACK_STARTED":    # 新 track 开始 → payload: {bbox_2d, class_label, confidence, frame_embedding}
    "TRACK_UPDATED":    # track 位置更新 → payload: {bbox_2d, position_3d, velocity}
    "TRACK_OCCLUDED":   # track 被遮挡 → payload: {last_position_3d, occluded_by}
    "TRACK_LOST":       # track 超时丢失 → payload: {last_seen_timestamp}
    "TRACK_RECOVERED":  # 之前丢失的 track 重新出现 → payload: {was_lost_for_seconds}
    
    # AR 平面
    "PLANE_DETECTED":   # 新平面 → payload: {ar_plane_id, center, normal, area, boundary}
    "PLANE_UPDATED":    # 平面扩展/缩小 → payload: {ar_plane_id, new_area, new_boundary}
    "PLANE_REMOVED":    # 平面消失 → payload: {ar_plane_id}

    # 手部 (如果可用)
    "HAND_DETECTED":    # 手出现 → payload: {hand_side, gesture, joints_3d}
    "HAND_GESTURE":     # 手势变化 → payload: {hand_side, old_gesture, new_gesture}
    "HAND_LOST":        # 手离开画面 → payload: {hand_side}

    # 元数据
    "STABILITY_CHANGED": # StabilityGate 级别变化 → payload: {old_tier, new_tier}
}
```

### 4.2 L2-A → L2-B: 空间事件

L2-A 在处理 L1 事件后，产生更高级别的空间语义事件：

```python
@dataclass
class L2AEvent:
    """L2-A 空间图输出事件"""
    timestamp: float
    event_type: str
    object_uuid: str
    payload: dict

L2A_EVENTS = {
    # 物体注册与身份
    "OBJECT_REGISTERED":  # 新物体入图 → payload: {class_label, position_3d, surface_uuid}
    "OBJECT_IDENTIFIED":  # ReID 成功确认身份 → payload: {old_label, confirmed_label, match_score}
    "OBJECT_MERGED":      # 两个 track 被确认为同一物体 → payload: {merged_uuid, absorbed_uuid}

    # 空间状态变化
    "OBJECT_MOVED":       # 物体位置变化超过阈值 → payload: {old_pos, new_pos, delta, velocity}
    "OBJECT_STATE_CHANGED": # 可见性状态变化 → payload: {old_state, new_state} (ACTIVE→OCCLUDED 等)
    "OBJECT_REAPPEARED":  # 之前 OUT_OF_VIEW 的物体回到视野 → payload: {was_gone_seconds}

    # 关系变化
    "RELATION_ADDED":     # 新关系产生 → payload: {relation, target_uuid}
    "RELATION_REMOVED":   # 关系消失 → payload: {relation, target_uuid}
    "OBJECT_PICKED_UP":   # 物体被拿起 (从 Surface 到 Hand) → payload: {from_surface, hand_uuid}
    "OBJECT_PUT_DOWN":    # 物体被放下 → payload: {on_surface}

    # Surface/Zone
    "SURFACE_REGISTERED": # 新承载面 → payload: {surface_type, area}
    "ZONE_FORMED":        # 新功能区域形成 → payload: {zone_name, member_count}
}
```

### 4.3 L2-B → L3: 语义注意力事件 (触发器)

L2-B 只推送**值得 L3 关注的事件** — 注意力阈值过滤是核心:

```python
@dataclass
class L2BTrigger:
    """L2-B 语义注意力触发器 (推送给 L3)"""
    timestamp: float
    trigger_type: str
    object_uuid: str
    attention_weight: float
    payload: dict

L2B_TRIGGERS = {
    # 注意力级别的事件 (过滤后)
    "NOVELTY_ALERT":      # 新物体且注意力高 → payload: {class_label, tags, community_summary}
    "ATTENTION_PEAK":     # 注意力超过阈值 → payload: {reason, tags}
    "ATTENTION_DECAY":    # 注意力衰减到 peripheral → payload: {was_foreground_for_seconds}
    "MEMORY_MATCH":       # Graphiti 预加载命中重要记忆 → payload: {matching_memory, emotional_valence}

    # 语义级别事件
    "INTERACTION_DETECTED": # 用户与物体交互 (拿起/放下) → payload: {interaction_type}
    "CLUSTER_NOTABLE":    # 一组物体形成有意义的聚类 → payload: {cluster_uuids, possible_meaning}
    "EMOTIONAL_SHIFT":    # 情感效价发生变化 → payload: {old_valence, new_valence, cause}
    "REUNION":            # 场景展开后的"久别重逢" → payload: {scene_id, top_attended}
}
```

### 4.4 L3 ↔ Gemini: 认知交互

**上行 (L3 → Gemini)**: 通过 `update_chat_ctx()` 注入 `[SCENE]` 标签的消息

```python
CONTEXT_INJECTION_TYPES = {
    "[SCENE_NEW]":        # 发现新物体: "发现一个蓝色杯子在桌上。标签: 奶奶的杯子, 易碎"
    "[SCENE_CHANGE]":     # 场景变化: "杯子被拿起了" / "有人进入房间"
    "[SCENE_RESTORED]":   # 场景恢复: "回到桌面场景, 上次关注: 杯子, 键盘"
    "[PERIODIC_SENSE]":   # 定时快照: 氛围+关注物体+场景概要
    "[RESEARCH_DONE]":    # Nanobot 后台结果: "花瓶来历调查完成: ..."
    "[MEMORY_RECALL]":    # 记忆唤起: "这个场景让我想起上次..."
}
```

**下行 (Gemini → L3)**: 通过 function_tool

```python
GEMINI_TOOLS = {
    # 已有设计 (09_dsg_technology_selection.md §4.3)
    "event_end":          # 事件结束 → L2-B fold + Graphiti 归档
    "focus_on":           # top-down 注意力 → L2-B 聚焦
    "query_scene":        # 场景查询 → L2-A + L2-B 返回摘要
    "switch_scene":       # 场景切换 → L1 SceneManager

    # 新增 (需要实现)
    "fly_to":             # 鹦鹉飞到目标 → dispatcher → Unity body_cmd
    "describe_object":    # 描述某物体的详细信息 → L2-B + Graphiti cross-search
    "remember":           # 主动记忆: "记住这个杯子是奶奶的" → Graphiti personality/objects
    "dispatch_task":      # 委派后台任务 → Redis Queue → Nanobot
}
```

### 4.5 完整的 Gemini Tool 定义 (MVP)

```python
@function_tool
async def fly_to(target: str, speed: str = "normal") -> str:
    """飞到指定的物体或位置旁边。

    Args:
        target: 物体 UUID 或名称 (如 "蓝色杯子" 或 "uuid:abc123")
        speed: 飞行速度 "slow" | "normal" | "fast"
    """
    resolved = await resolve_target(target)  # UUID 或名称 → 精确位置
    if not resolved:
        return "找不到这个目标，你能描述一下它在哪吗？"
    await dispatcher.dispatch_body_command({
        "cmd": "fly_to",
        "target_position": resolved.position_3d,
        "target_surface": resolved.on_surface_uuid,
        "speed": speed,
    })
    return f"正在飞往 {resolved.class_label}"

@function_tool
async def describe_object(object_uuid: str) -> str:
    """获取某个物体的详细信息，包括在 DSG 中的空间位置和记忆。

    Args:
        object_uuid: 物体的 UUID
    """
    spatial = l2a.get_node(object_uuid)
    semantic = l2b.get_node(object_uuid)
    
    memory = await graphiti_cross_search(
        query=f"object {semantic.class_label if semantic else 'unknown'}",
        group_ids=["objects", "personality", "episodic"],
    )
    
    return format_object_description(spatial, semantic, memory)

@function_tool
async def remember(fact: str, category: str = "episodic") -> str:
    """主动记住一个事实或观察。

    Args:
        fact: 要记住的内容 (如 "这个杯子是主人奶奶的遗物")
        category: 记忆分区 "episodic" | "objects" | "personality" | "vocabulary"
    """
    await graphiti.add_episode(
        name=f"parrot_memory_{time.time():.0f}",
        episode_body=fact,
        source_description="鹦鹉主动记忆",
        group_id=category,
        entity_types=GRAPHITI_ENTITY_TYPES,
        edge_types=GRAPHITI_EDGE_TYPES,
        edge_type_map=GRAPHITI_EDGE_TYPE_MAP,
    )
    return f"已记住 ({category}): {fact[:50]}..."

@function_tool
async def dispatch_task(task_type: str, subject: str, details: str = "") -> str:
    """委派一个后台研究任务给 Nanobot。

    Args:
        task_type: "research" | "summarize" | "compare"
        subject: 任务主题
        details: 额外说明
    """
    await redis_bus.enqueue_task({
        "type": task_type,
        "subject": subject,
        "details": details,
        "soul_prefs": parrot_soul.get_preferences(),
    })
    return f"已委派: {task_type} — {subject}"
```

### 4.6 触发器全景矩阵

| 源 → 目标 | 事件格式 | 传输机制 | 频率 | 过滤 |
|:----------|:---------|:---------|:-----|:-----|
| Unity → L1 | `ar_telemetry` JSON | DataChannel | 10Hz | 无 |
| L1 → L2-A | `L1Event` | Python async callback | 1-5Hz | NoiseFilter |
| L2-A → L2-B | `L2AEvent` | Python async callback | 事件驱动 | 仅有意义的变化 |
| L2-B → L3 | `L2BTrigger` | drain_triggers() 队列 | 事件驱动 | attention > 阈值 |
| L3 → Gemini | `[SCENE_*]` chat ctx | update_chat_ctx() | 0.1-1Hz | _is_significant() |
| Gemini → L3 | Tool Call | LiveKit function_tool | Gemini 主导 | — |
| L3 → L2-B | Focus/Fold 指令 | Python async call | Gemini 主导 | — |
| L3 → Graphiti | Episode 归档 | async add_episode() | event_end 时 | — |
| Graphiti → L2-B | 预加载数据 | async search() | 新物体注册时 | — |
| Nanobot → L3 | 任务完成 | Redis Pub/Sub | 异步 | — |
| 后端 → Unity | body_cmd JSON | DataChannel | 事件驱动 | — |

---

## 5. 各层需要学习的参考项目

### 5.1 L1 (视网膜 / Physical Tracks)

| 学习对象 | 学什么 | 我们怎么用 |
|:---------|:-------|:----------|
| **SVA Processor 模式** | 帧率控制、activity throttle、多处理器编排 | StabilityGate + SceneProfile 配置化 |
| **SVA 高尔夫教练** | 单目姿态分析、动作序列检测 | Phase 2 桌面场景的手部动作分析 |
| **SVA 安防监控** | 多目标追踪、ReID | tracker + reid.py 设计 |
| **SAM2 官方 demo** | Promptable Visual Segmentation、track ID 管理 | tracker.py 核心 |
| **EdgeTAM** (Meta) | 移动端优化的 SAM2 变体 | 如果需要在前端做轻量追踪 |

### 5.2 L2-A (背侧通路 / Spatial Topology)

| 学习对象 | 学什么 | 我们怎么用 |
|:---------|:-------|:----------|
| **Spark-DSG / Hydra** (MIT) | **分层节点属性继承**: NodeAttributes → SemanticNodeAttributes → ObjectNodeAttributes → KhronosObjectAttributes；**LayerId 分层枚举**: OBJECTS / PLACES / ROOMS / BUILDINGS / AGENTS | 直接借鉴其继承体系设计 `DSGNode → SpatialNode → ObjectNode/SurfaceNode/ZoneNode`；参考其 Layer 枚举设计我们的 `DSGLayer` |
| **ConceptGraphs** (ICRA 2024) | **开放词汇 3D 场景图**: 不需要预定义类别的物体发现；**多视角融合**: CLIP embedding 累积投票决定物体身份；**LLM 推导 inter-object 关系**: 用 GPT-4 推断物体间关系 (而非纯几何) | `ObjectNode.class_votes` 多帧投票机制；`dino_embedding` 等价于 CLIP feature；未来 L2-A 关系边也可引入 LLM 推断 |
| **FROSS** (ICCV 2025) | **3D 高斯位置表示**: 均值+协方差表示位置不确定性；**Hellinger 距离**: 多视角合并同一物体观测；**增量在线更新**: 不是全局重建而是逐帧融合 | `position_cov` 字段；多视角观测融合逻辑 |
| **3DSSG** (Stanford) | **空间关系标注体系**: ON / NEAR / IN / ABOVE 等标准化关系；**层级化场景图**: Object → Room → Building | `SpatialRelation` 枚举设计的参考 |

### 5.3 L2-B (腹侧通路 / Semantic Attention)

| 学习对象 | 学什么 | 我们怎么用 |
|:---------|:-------|:----------|
| **ConceptGraphs** (语义面) | LLM 推导的物体间语义关系 (不只空间) | `SemanticRelation` 边类型: ASSOCIATED_WITH, USED_FOR 等 |
| **Microsoft GraphRAG** | **Leiden 社区检测**: 层级化社区发现；**Entity → Community → Summary**: 从实体到社区到全局摘要的三层结构；**SearchFilters**: 按 node_label / edge_type 过滤 | Graphiti 的 `build_communities()` 就是这个；`community_id` / `community_summary` 字段设计 |
| **Graphiti (Zep)** | **Custom Entity Types**: Pydantic 定义自定义实体/边；**group_id 命名空间**: 分区隔离；**Temporal KG**: 时间感知的知识图谱 | §3 的全部设计；`add_episode()` 的 `entity_types` 参数 |
| **注意力神经科学** | **Posner 注意力模型**: 外源性(bottom-up) + 内源性(top-down)；**新奇/习惯化二因子**: 新奇度衰减 + 反复接触导致习惯化 | `AttentionSystem` 的 `bottom_up_update` / `top_down_focus` / `tick` |
| **Hindsight Framework** (2025) | 四网络记忆: 世界事实/Agent经验/实体摘要/信念 | Graphiti 5分区的理论依据 |

### 5.4 L3 (前额叶 / Cognitive Interface)

| 学习对象 | 学什么 | 我们怎么用 |
|:---------|:-------|:----------|
| **Inworld AI Director Layer** | **编排者不参与内容生成**: 只管理轮次、话题流转、上下文一致性 | L3 CognitiveInterface 的设计原则 |
| **LiveKit AgentSession Events** | `conversation_item_added`, `function_tools_executed` 等事件的精确格式和触发时机 | ObserverTimeline 的事件捕获 |
| **OpenClaw SOUL** | 可编程灵魂: SOUL.md + MEMORY.md + HEARTBEAT.md | ParrotSoul + refresh_from_graphiti() |
| **CrewAI** | 角色化 Agent 的记忆分层: 短期/长期/实体/外部 | Graphiti 分区对应 |

### 5.5 调度器 + 前后端同步

| 学习对象 | 学什么 | 我们怎么用 |
|:---------|:-------|:----------|
| **py-trees** | Python 行为树: Selector/Sequence/Parallel 组合；Blackboard 机制 | Phase 3 行为树调度器 |
| **Halo AI / The Sims** | 游戏 AI 的优先级中断和 Utility AI | 优先级子树 + 资源锁设计 |
| **Gabriel Gambetta 教程** | 权威服务器 + 客户端预测 | 前后端同步模式 |
| **FlexBE** | OBE/OCS 分离 (可操作专家/可操作客户端系统) | 前后端状态机职责分离 |

### 5.6 项目学习优先级路线图

```
Phase 1 (Voice Skeleton + Basic AR)
├── 必学: LiveKit Agents examples, DataChannel 协议
├── 参考: SVA processor 模式 (帧率控制)
└── 了解: Unity AR Foundation + LiveKit Unity SDK

Phase 2 (Reflex & Control)
├── 必学: py-trees 行为树, Gabriel Gambetta 权威服务器
├── 参考: Halo AI 优先级中断
└── 了解: FlexBE OBE/OCS

Phase 3 (Vision & Memory)
├── 必学: ConceptGraphs (节点设计 + 多视角融合), Graphiti custom types
├── 必学: Spark-DSG/Hydra (分层 DSG 概念)
├── 参考: FROSS (位置不确定性), Microsoft GraphRAG (社区检测)
└── 了解: 3DSSG (关系标注体系), 注意力神经科学文献
```

---

## 6. 场景特化设计 (Desktop / Indoor MVP)

### 6.1 Desktop 场景 — 节点与边的特化

桌面场景的特点: 小空间、物体密集、精确追踪、手部交互频繁

```
Desktop Scene Graph (典型状态)
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Zone 层:
  [ZoneNode] "工作区" (auto, radius=0.8m)

Surface 层:
  [SurfaceNode] "桌面" (horizontal, AR plane, area=0.6m², anchor)
  [SurfaceNode] "显示器底座" (horizontal, small)

Object 层:
  [ObjectNode] "蓝色杯子" (ON_SURFACE→桌面, ReID=confirmed, precious)
  [ObjectNode] "键盘" (ON_SURFACE→桌面)
  [ObjectNode] "鼠标" (ON_SURFACE→桌面, NEAR→键盘)
  [ObjectNode] "手机" (ON_SURFACE→桌面, state=ACTIVE)
  [ObjectNode] "笔" (HELD_BY→右手)
  [HandNode] "右手" (gesture=holding, is_holding=笔)
  [ParrotAnchorNode] "桌面停靠点" (on 桌面, landing_offset=(0, 0.05, 0))
```

**Desktop 特化参数**:

| 参数 | Desktop 值 | Indoor 值 | 原因 |
|:-----|:----------|:----------|:-----|
| discoverer_fps | 2.0 | 1.0 | 桌面视角小，变化更密集 |
| tracker_max_targets | 15 | 30 | 桌面物体少但要精确 |
| reid_enabled | True | True | — |
| action_analyzer_enabled | **True** | False | 桌面的手部动作有意义 |
| stable_velocity_thresh | 0.05 | 0.1 | 桌面要求更稳才启动精确追踪 |
| default_zone_size | 0.8m | 3.0m | — |
| novelty_half_life | 120s | 60s | 桌面物体变化慢 |
| ON_SURFACE 距离阈值 | 0.05m | 0.15m | 桌面物体贴近表面 |
| NEAR 距离阈值 | 0.3m | 1.0m | 桌面"近"的定义更小 |

**Desktop 特有的触发器逻辑**:

```python
class DesktopTriggerRules:
    """Desktop 场景的触发器特化规则"""

    def should_trigger_interaction(self, event: L2AEvent) -> bool:
        """桌面场景: 物体被拿起/放下是重要事件"""
        return event.event_type in ("OBJECT_PICKED_UP", "OBJECT_PUT_DOWN")

    def should_trigger_arrangement_change(self, events: list[L2AEvent]) -> bool:
        """桌面场景: 多个物体位置变化 = 重新布局 (值得通知)"""
        moved = [e for e in events if e.event_type == "OBJECT_MOVED"]
        return len(moved) >= 3  # 3个以上物体移动 = 重新布局

    def should_trigger_hand_proximity(self, hand: HandNode, objects: list[ObjectNode]) -> list[str]:
        """桌面场景: 手接近物体 → 提前关注"""
        approaching = []
        for obj in objects:
            dist = _distance(hand.position_3d, obj.position_3d)
            if dist < 0.15:  # 手距物体 15cm
                approaching.append(obj.uuid)
        return approaching
```

### 6.2 Indoor 场景 — 节点与边的特化

室内场景的特点: 大空间、物体分散、多区域、人物进出、移动频繁

```
Indoor Scene Graph (典型状态)
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Zone 层:
  [ZoneNode] "客厅沙发区" (radius=2.5m)
  [ZoneNode] "电视区" (radius=2.0m)
  [ZoneNode] "过道" (radius=1.5m)

Surface 层:
  [SurfaceNode] "地面" (horizontal, AR plane, area=12m², anchor)
  [SurfaceNode] "茶几" (horizontal, area=0.4m²)
  [SurfaceNode] "沙发" (horizontal, area=1.2m²)
  [SurfaceNode] "电视柜" (horizontal, area=0.8m²)

Object 层:
  [ObjectNode] "电视" (ON_SURFACE→电视柜, state=ANCHORED)
  [ObjectNode] "遥控器" (ON_SURFACE→茶几, state=ACTIVE)
  [ObjectNode] "抱枕" (ON_SURFACE→沙发, state=ACTIVE)
  [ObjectNode] "杂志" (ON_SURFACE→茶几, state=OUT_OF_VIEW)
  [PersonSemanticNode] "主人" (current_activity="休息", NEAR→沙发)
  [ParrotAnchorNode] "茶几停靠点" (on 茶几)
  [ParrotAnchorNode] "沙发扶手停靠点" (on 沙发)
```

**Indoor 特化参数**: (见上表 Indoor 列)

**Indoor 特有的触发器逻辑**:

```python
class IndoorTriggerRules:
    """Indoor 场景的触发器特化规则"""

    def should_trigger_zone_transition(self, old_zone: str, new_zone: str) -> bool:
        """室内: 用户从一个区域走到另一个区域是重要事件"""
        return old_zone != new_zone

    def should_trigger_large_object(self, obj: ObjectNode) -> bool:
        """室内: 大家具不需要频繁更新 (ANCHORED 就行)"""
        return obj.estimated_size and max(obj.estimated_size) > 0.5

    def should_reduce_attention(self, node: ObjectSemanticNode) -> bool:
        """室内: 家具类物体快速习惯化"""
        furniture = {"chair", "table", "sofa", "tv", "shelf", "door"}
        return node.class_label in furniture and node.habituation_count > 3
```

### 6.3 Desktop → Indoor 场景切换时的节点处理

```python
async def desktop_to_indoor_transition(
    scene_manager: SceneManager,
    l2a: SpatialGraph,
    l2b: SemanticAttentionGraph,
):
    """从桌面切换到室内场景的完整流程"""

    # 1. 检查是否有跨场景携带的物体 (如用户手里拿着手机)
    portable_objects = l2a.get_portable_objects()
    
    # 2. 折叠桌面场景
    desktop_snapshot_a = l2a.fold_scene("desktop_current")
    desktop_snapshot_b = l2b.fold_scene("desktop_current")
    
    # 3. 切换 SceneProfile
    scene_manager.apply_profile(SCENE_PROFILES[SceneType.INDOOR])
    
    # 4. 尝试展开之前的室内场景 (如果有)
    if l2a.has_frozen_scene("indoor_last"):
        l2a.unfold_scene("indoor_last")
        l2b.unfold_scene("indoor_last")
    else:
        pass  # 新场景，从空白开始
    
    # 5. 将携带物体注入新场景
    for obj_uuid in portable_objects:
        await l2a.transfer_object(obj_uuid, "indoor_current")
        await l2b.carry_semantic_node(obj_uuid)  # 语义节点也跟着走
    
    # 6. 通知 L3
    return {
        "type": "SCENE_TRANSITION",
        "from": "desktop",
        "to": "indoor",
        "carried_objects": portable_objects,
        "restored_objects": l2a.get_active_object_count(),
    }
```

---

## 7. 调研清单与下一步行动

### 7.1 Phase 0 剩余调研 (建议在开始编码前完成)

| # | 调研项 | 优先级 | 方法 | 产出 |
|:--|:-------|:-------|:-----|:-----|
| R1 | **ConceptGraphs 源码阅读** — 重点 `slam_classes.py` 多视角融合逻辑 | P0 | 读源码 | L2-A 多帧投票 + DINOv2 融合细节 |
| R2 | **Spark-DSG Python API** — 实际跑一下 `python_api.py` example | P1 | pip install spark-dsg + 跑 demo | 理解层级查询 API |
| R3 | **Graphiti add_episode + custom types** — 实测 group_id + custom entity | P0 | 本地 Neo4j + Graphiti demo | 验证 §3 设计可行性 |
| R4 | **LiveKit 事件精确测试** — 确认 conversation_item_added 的精确数据格式 | P0 | 跑一个最小 Agent + 打印事件 | 验证 L3 Timeline 数据源 |
| R5 | **py-trees 快速上手** — Selector/Sequence/Parallel 组合验证 | P1 | pip install py-trees + 跑 demo | 行为树调度器原型 |
| R6 | **RustworkX contract_nodes** — 验证折叠操作在有边的图上的行为 | P0 | 写 mini test | 确认 L2-B fold 语义 |

### 7.2 Phase 1 编码顺序建议

```
Week 1: 骨架
├── agent/main.py + session.py (LiveKit 连接)
├── agent/protocol/ (DataChannel JSON Schema)
├── agent/tools/ (基础 Tool: query_scene, fly_to, switch_scene)
└── APP 生命周期 + 网络降级 (先骨架后完善)

Week 2: 感知管线
├── agent/perception/tracker.py (SAM2 mock → 真实)
├── agent/perception/stability_gate.py
├── agent/perception/scene_manager.py + scene_profiles.py
└── L1Event 输出格式实现

Week 3: DSG 图
├── agent/perception/spatial_graph.py (L2-A 完整实现, 本文 §1)
├── agent/perception/semantic_cache.py (L2-B 完整实现, 本文 §2)
├── agent/perception/reid.py
└── L2-A ↔ L2-B 事件连接

Week 4: 认知层 + 记忆
├── agent/brain/cognitive_interface.py (L3)
├── agent/brain/observer_timeline.py
├── agent/memory/graphiti_impl.py (本文 §3 的自定义类型)
└── 端到端: L1 → L2-A → L2-B → L3 → Gemini → 鹦鹉说话
```

---

## 8. 决策总结

| 决策项 | 选择 | 理由 |
|:-------|:-----|:-----|
| L2-A 节点基类 | `DSGNode → SpatialNode → ObjectNode/SurfaceNode/ZoneNode/HandNode/ParrotAnchorNode` | 借鉴 Spark-DSG 的继承体系，适配我们的 AR 环境 |
| L2-B 节点基类 | `DSGNode → SemanticNode → ObjectSemanticNode/SurfaceSemanticNode/ZoneSemanticNode/PersonSemanticNode/EventCapsuleNode` | 与 L2-A 平行但独立，UUID 关联 |
| Graphiti 自定义类型 | PhysicalObject / Place / Person / Habit / Concept + OwnershipEdge / UsageEdge / LocationEdge | 利用 Graphiti 原生 custom entity types 能力 |
| L2-A/L2-B 分开设计 | 两个独立 RustworkX 图，UUID 关联 | L2-A 由物理世界驱动，L2-B 由注意力驱动，时间尺度不同 |
| 触发器分层设计 | L1Event → L2AEvent → L2BTrigger → ContextInjection | 每层做过滤，避免信息洪水 |
| 场景特化 | Desktop/Indoor 各有自己的阈值、触发规则、典型节点结构 | 同一节点体系，不同参数配置 |
| 主要参考项目 | L2-A: Spark-DSG(继承) + ConceptGraphs(融合) + FROSS(不确定性)；L2-B: GraphRAG(社区) + Graphiti(类型) + 注意力神经科学 | 每层有不同的最佳实践来源 |
