---
status: draft
category: protocol-spec
protocol_id: DSG-SCENE-V1
status_note: "SceneType 切换 + Scene Snapshot 协议 V1 — 桌面 baseline + 留切换接口 + 跨 SceneType 永久权威桶保留 + Node 字段 scene_type/location_tag。Scene 不主导 L2-B 拓扑（拓扑由 IntentEvent 驱动）。"
last_reviewed: 2026-05-06
ai_priority: high
ai_audience: "实施 chat / 独立审计 chat / P3 多 Scene + VPS + 软件建图实施 chat"
parent_doc: "dsg_l1_5_pool_and_lifecycle_design_20260506.md"
companion_protocols:
  - "dsg_protocol_pool_v1_20260506.md"
  - "dsg_protocol_trigger_v2_20260506.md"
  - "dsg_protocol_archive_v1_20260506.md"
---

# DSG-SCENE-V1 — SceneType 切换 + Snapshot 协议

> **协议 ID**：DSG-SCENE-V1
> **范围**：`src/parrot/dsg/l1_5/scene_snapshot.py` + `dsg/triggers/scene_switch_trigger.py` + `SemanticNode.scene_type / location_tag` 字段。
> **核心约束**（master §1 + Q-D 已锁）：SceneType 切换主要走 **L1.5 管理面**（freeze 桶 / 切 CV Flow / 切 DsgMode），**不主导 L2-B 拓扑**（拓扑由 IntentEvent 驱动）。
> **不在范围**：手机传感器接入 / VPS 对齐 / 软件建图 / 多 Scene 子图（**全部 P3**）。

---

## §0 术语表（与主设计稿 §0 等同；强调本协议**关键三概念区分**）

| 中文 | 官方名称 | 是什么 | 不是什么 |
|:--|:--|:--|:--|
| 场景类型 | **`SceneType`** | preset enum：desktop / home / outdoor / library | ≠ Location（具体位置）/ ≠ IntentEvent（认知边界）|
| 物理位置 | **`LocationTag`** | scalar tag：study / kitchen / living_room | ≠ SceneType / ≠ Bucket / ≠ Compartment |
| 认知边界 | **`IntentEvent`** | GOSLO Intent focus | ≠ SceneType（物理切换不必等于认知切换）|

→ **本协议不动 IntentEvent / Plan**；只管 SceneType 与 LocationTag。

---

## §1 SceneProfile

### §1.1 SceneType enum 与 SceneProfile

```python
class SceneType(str, Enum):
    """preset 场景类型（桌面 baseline 起步：仅 DESKTOP；其他留接口）"""
    DESKTOP = "desktop"                   # 桌面工作场景（baseline）
    HOME_INDOOR = "home_indoor"           # 家中室内（P3）
    OUTDOOR = "outdoor"                    # 室外（P3）
    LIBRARY = "library"                    # 图书馆 / 专注场景（P3）
    KITCHEN = "kitchen"                    # 厨房（P3）
    OTHER = "other"                        # fallback

@dataclass(frozen=True)
class SceneProfile:
    scene_type: SceneType
    
    # 模块切换（影响其他子系统）
    dsg_mode: DsgMode                              # 既有 enum
    video_tier_hint: VideoTier                     # 既有 enum
    cv_flow_params: dict[str, Any] = field(default_factory=dict)
    """CV Flow 参数（影响 A10 接入后的视觉门控；桌面 baseline 不接 A10）"""
    
    # L1.5 桶行为
    preserved_bucket_kinds: frozenset[BucketKind] = frozenset({
        BucketKind.OBSIDIAN_SETTING_DAILY,
        BucketKind.OBSIDIAN_SETTING_ROLEPLAY,   # 仅当 roleplay 模式开
    })
    """跨 SceneType 切换保留的桶（永久权威）"""
    
    fresh_bucket_kinds: frozenset[BucketKind] = frozenset({
        BucketKind.GOOGLE_CALENDAR,             # 切 Scene 后日程通常不同
        BucketKind.AUTONOMOUS_CURIOSITY,        # 切 Scene 重新好奇
    })
    """切换时 clear 的桶"""
    
    # AdmissionPolicy override
    priority_overrides: dict[str, int] = field(default_factory=dict)
    """source priority 覆盖（如 roleplay 模式提升 USER_TAG_OBSIDIAN_ROLEPLAY）"""
    
    # 默认 LocationTag（用户切 Scene 时如未指定 location）
    location_default: str = ""

# 桌面 baseline profile
DESKTOP_PROFILE = SceneProfile(
    scene_type=SceneType.DESKTOP,
    dsg_mode=DsgMode.DSG_GEMINI_VISION,
    video_tier_hint=VideoTier.VIDEO_GEMINI_ONLY,
    cv_flow_params={"enabled": False},   # baseline 不接 A10
    location_default="desk",
)
```

### §1.2 SceneRegistry

```python
class SceneRegistry:
    """L1.5 内部 Scene 注册表 + 当前 Scene 管理"""

    def __init__(self):
        self._profiles: dict[SceneType, SceneProfile] = {
            SceneType.DESKTOP: DESKTOP_PROFILE,
        }
        self._current: SceneType = SceneType.DESKTOP

    def register(self, profile: SceneProfile) -> None:
        """注册新 SceneProfile（P3 多 Scene 时用）"""

    def get(self, scene_type: SceneType) -> SceneProfile | None: ...

    def current(self) -> SceneProfile:
        return self._profiles[self._current]

    async def switch(
        self, new_scene_type: SceneType
    ) -> "SceneSwitchOutcome":
        """切换 Scene。详见 §3"""
```

---

## §2 Node 字段

### §2.1 `scene_type` / `location_tag`

```python
class SemanticNode:
    # ... 既有字段 + bucket_id / event_id 不动 ...
    
    scene_type: str = ""
    """所属 SceneType（informational tag）— 桌面 baseline 起步默认 "desktop"。
    
    多 Scene（P3）时记录节点首次出现的 Scene；切 Scene 时不主动改字段。
    用于 view_by_scene(scene_type) 视图过滤。
    """
    
    location_tag: str = ""
    """物理位置标签（informational tag）— 桌面 baseline 默认 "desk"。
    
    用户 / VPS（P3）/ Detection 写入；P3 用于 L2-A 空间推理。
    用于 view_by_location(tag) 视图过滤。
    """
```

### §2.2 字段写入时机

| 来源 | scene_type 赋值 | location_tag 赋值 |
|:--|:--|:--|
| IngestRunner.commit_observation（新建节点）| 当前 SceneRegistry.current().scene_type.value | 当前 SceneProfile.location_default |
| Graphiti preload | 不写（保留空字符串 = 未知；查询时按 fallback）| 同上 |
| 触发器 | 通过 Observation.meta 显式传入 | 同上 |
| 用户显式 set（P3）| 通过 set_scene tool | 通过 set_location tool（P3）|

---

## §3 SceneSwitchOutcome + switch 流程

### §3.1 流程

```
SceneSwitchTrigger.on_event(set_scene)
  ↓
TriggerOutcome:
  bucket_ops:
    - FREEZE OBSIDIAN_SETTING_DAILY
    - FREEZE OBSIDIAN_SETTING_ROLEPLAY (if active)
    - CLEAR GOOGLE_CALENDAR
    - CLEAR AUTONOMOUS_CURIOSITY (TTL natural)
  archive_request:
    - SERIALIZE_NOW(SCENE_SNAPSHOT, scene_id=old)
  notify_gemini:
    - "切换到 {new_scene_type} 场景了"
  ↓
TriggerRunner._process_result:
  1. apply bucket_ops → freeze/clear
  2. archive_request → serialize old scene snapshot
  3. notify_gemini
  ↓
SceneRegistry.switch(new_scene_type):
  1. 写 Timeline marker SCENE_SWITCHED
  2. 调 ModeController（DsgMode 切换）
  3. 调 set_video_tier（VideoTier 切换）
  4. 调 CV Flow 模块（cv_flow_params；A10 接入后）
  5. 更新 _current
  6. 返回 SceneSwitchOutcome
```

### §3.2 SceneSwitchOutcome

```python
@dataclass(frozen=True)
class SceneSwitchOutcome:
    old_scene_type: SceneType
    new_scene_type: SceneType
    switched_at: float
    
    # L1.5 影响
    preserved_buckets: tuple[BucketKind, ...]
    cleared_buckets: tuple[BucketKind, ...]
    affected_node_count: int               # cleared 桶里的节点数
    
    # 跨模块影响
    dsg_mode_change: tuple[DsgMode, DsgMode]   # (old, new)
    video_tier_change: tuple[VideoTier, VideoTier]
    
    # Snapshot 留档
    old_snapshot_path: Path | None = None
    
    # 失败
    success: bool = True
    errors: tuple[str, ...] = ()
```

---

## §4 Scene Snapshot 序列化

### §4.1 Snapshot 内容

切换前 `archive_request: SERIALIZE_NOW(SCENE_SNAPSHOT)` 触发 ConversationArchive 序列化以下到硬盘：

```
data/conversations/{conv_id}/scene_snapshots/{scene_type}_{ts}/
├── scene_metadata.json         SceneProfile + 切换前 timestamp
├── snapshot.json               SceneType 内的节点（filter by scene_type）
├── refs.jsonl                  scene-related refs
└── timeline.jsonl              SCENE_SWITCHED marker + 切前最后 N 条
```

### §4.2 Snapshot schema

#### `scene_metadata.json`
```json
{
  "schema_version": 1,
  "scene_type": "desktop",
  "dsg_mode": "dsg_gemini_vision",
  "video_tier_hint": "video_gemini_only",
  "snapshot_ts": 1746543600.0,
  "duration_in_scene_seconds": 1800.0,
  "node_count": 28,
  "events_in_scene": 5
}
```

→ 桌面 baseline 不真的多 Scene；本 schema 为 P3 多 Scene 切换准备。

---

## §5 LocationTag 与 SceneType 的区分

### §5.1 关键场景示例

| 场景 | SceneType | LocationTag |
|:--|:--|:--|
| 桌面工作 | DESKTOP | desk |
| 在家书房工作 | HOME_INDOOR | study |
| 在家厨房做饭 | HOME_INDOOR | kitchen |
| 在家客厅看电视 | HOME_INDOOR | living_room |
| 图书馆专注 | LIBRARY | library_floor_2 |
| 户外散步 | OUTDOOR | park |

→ **同 SceneType 内可以多 LocationTag**（家里有多个房间）；**不同 SceneType 不能跨**（DESKTOP 节点不能 LocationTag=outdoor）。

### §5.2 切换时机区别

| 维度 | SceneType 切换 | LocationTag 切换 |
|:--|:--|:--|
| 频率 | 低（一天几次）| 中（房间间走动）|
| 触发模块影响 | 大（CV Flow / DsgMode / 桶）| 无（仅标签）|
| Snapshot 留档 | 是 | 否（保留时间序列在 Timeline）|
| 跨切保留 | 永久权威桶 | 节点不变（仅字段更新）|

→ 桌面 baseline 起步：**单 SceneType=DESKTOP + 单 LocationTag=desk**，切换接口完整保留待 P3 实测。

---

## §6 协议合同 0 漂移核对

| 检查项 | 状态 |
|:--|:--|
| Phase 4 §8 L1（NodeKind / EdgeKind enum）| ✅ 不动 |
| Phase 4 §8 锁（其他）| ✅ 不动 |
| ADR-L1.5-001 §2.1 Q1（source 仅 Python）| ✅ scene_type / location_tag 都是 str 字段（informational tag）|
| `parrot_behavior_rules §3.7` | ✅ Scene 不抓帧 / 不写 Graphiti |
| `tests/test_ecp_event/test_cs_parity.py` 4/4 | ⚠️ **set_scene** tool 既有，**本协议不动 wire**；如未来要加 `EcpEventType.SCENE_SWITCHED` 走新 ADR |

---

## §7 测试覆盖

```python
# tests/test_dsg/test_scene_switch_baseline.py
def test_register_scene_profile(): ...
def test_get_scene_profile(): ...
def test_current_scene_default_desktop(): ...
def test_switch_scene_writes_timeline_marker(): ...
def test_switch_scene_changes_dsg_mode(): ...
def test_switch_scene_changes_video_tier_hint(): ...
def test_switch_scene_returns_outcome_with_old_and_new(): ...

# tests/test_dsg/test_scene_preserve_authority.py
def test_obsidian_setting_daily_preserved_across_switch(): ...
def test_obsidian_setting_roleplay_preserved_when_active(): ...
def test_google_calendar_cleared_on_switch(): ...
def test_autonomous_curiosity_cleared_on_switch(): ...
def test_main_bucket_nodes_keep_scene_type_after_switch(): ...

# tests/test_dsg/test_scene_node_fields.py
def test_new_node_assigned_current_scene_type(): ...
def test_new_node_assigned_default_location_tag(): ...
def test_view_by_scene_filters_nodes(): ...
def test_view_by_location_filters_nodes(): ...
def test_graphiti_preload_node_scene_type_empty(): ...

# tests/test_dsg/test_scene_snapshot_serialize.py
def test_serialize_writes_scene_metadata_json(): ...
def test_serialize_filters_nodes_by_scene_type(): ...
def test_serialize_snapshot_path_format(): ...
def test_snapshot_after_switch_includes_archived_marker(): ...
```

→ 共 **20 项新测试**。

---

## §8 与 P3 的衔接

### §8.1 多 Scene + VPS + 软件建图

P3 实施时（A10 + VPS chat）：
- `cv_flow_params` 真用（不同 Scene 用不同 SAM2 / DINOv2 配置）
- 手机传感器接入：自动检测 SceneType 切换（位置 / 加速度 / 光照）
- VPS 对齐：跨 Scene 的 LocationTag 与 AR 锚点联动
- 软件建图：导入 Map → Unity → DSG 节点 LocationTag 自动赋值

### §8.2 多 SceneType 子图（如果未来证明必要）

桌面 baseline **不开多子图**。若 P3 实测证明需要：
- 走 [`dsg-l2b-node-organization-options §6.5 P1 / P4`](../../../skills/dsg-l2b-node-organization-options/SKILL.md)（按 Scene 分子图 / 多正交 view）
- 起新 ADR 升级 SceneRegistry 到多图模式

---

## §9 引用

- 主设计稿：[`dsg_l1_5_pool_and_lifecycle_design_20260506.md`](dsg_l1_5_pool_and_lifecycle_design_20260506.md)
- Pool 协议：[`dsg_protocol_pool_v1_20260506.md`](dsg_protocol_pool_v1_20260506.md)
- 触发器协议：[`dsg_protocol_trigger_v2_20260506.md`](dsg_protocol_trigger_v2_20260506.md)
- Archive 协议：[`dsg_protocol_archive_v1_20260506.md`](dsg_protocol_archive_v1_20260506.md)
- 既有：`src/parrot/shared/tiers.py`（DsgMode / VideoTier / ALLOWED_COMBOS）
- 既有：`src/parrot/brain/tools/set_mode.py`、`set_video_tier.py`
- ConceptGraph SKILL §8a（AR 锚点漂移问题，P3 处理）

---

## §10 变更日志

- **2026-05-06**：本协议 V1 创建。SceneType / LocationTag / IntentEvent 三概念严格区分 + DESKTOP_PROFILE baseline + SceneRegistry.switch 流程 + 4 jsonl Snapshot schema + 20 项验证测试 + P3 多 Scene 升级路径预留。
