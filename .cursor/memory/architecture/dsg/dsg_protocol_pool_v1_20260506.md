---
status: draft
category: protocol-spec
protocol_id: DSG-POOL-V1
status_note: "DSG L1.5 Pool 协议 V1 — 多源 Node 出口管理面接口 + Bucket + AdmissionPolicy + RefTable + Timeline + SceneRegistry。Python 内部协议，不上 Unity wire。"
last_reviewed: 2026-05-06
ai_priority: high
ai_audience: "实施 chat / 独立审计 chat / 后续 P3 仿生升级 / 第三方 Pool 包替换者"
parent_doc: "dsg_l1_5_pool_and_lifecycle_design_20260506.md"
companion_protocols:
  - "dsg_protocol_trigger_v2_20260506.md"
  - "dsg_protocol_archive_v1_20260506.md"
  - "brain_protocol_intent_workspace_v1_20260506.md"
---

# DSG-POOL-V1 — L1.5 Pool 协议

> **协议 ID**：DSG-POOL-V1
> **范围**：`src/parrot/dsg/l1_5/` 子包对外 API + 内部不变量。
> **不在范围**：节点本体（在 L2-B）/ Plan 主存（在 IntentWorkspace）/ Unity wire 字段（永不动）。

---

## §0 术语表（与主设计稿 §0 等同；任何冲突以主设计稿为准）

| 中文 | 官方名称 | 主存储 |
|:--|:--|:--|
| 场景类型 | `SceneType` | L1.5 SceneRegistry |
| 物理位置 | `LocationTag` | Node 字段 |
| 对话段 | `Episode` | L2-B EpisodeMarker |
| 认知边界 | `IntentEvent` | L2-B IntentEventBoundaryHandler |
| 计划 | `Plan` | IntentWorkspace（主）+ L2-B 镜像 |
| 计划步骤 | `PlanStep` | 同上 |
| 异步任务 | `NanobotTask` | Scheduler + Nanobot |
| L1.5 桶 | `Bucket` | L1.5 BucketRegistry |
| L2-B 拓扑分组 | `Compartment` | L2-B compartments.py（视图）|

**命名硬规则**：`Event` → `IntentEvent`；`Scene` → `SceneType`；`Task` → `NanobotTask`；`Bucket` 不出现在 L2-B；`Compartment` 不出现在 L1.5。

---

## §1 Pool 模块边界

### §1.1 持有什么 / 不持有什么

| Pool 持有 | 形态 |
|:--|:--|
| `BucketRegistry` | dict[BucketKind, BucketHandle]（每桶含 spec + node_uuid set + lifecycle policy）|
| `RefTable` | dict[(RefKind, ref_value), node_uuid]（轻量绑定，不含 payload）|
| `Timeline` | append-only list[TimelineMarker]（仅事件边界标注）|
| `SceneRegistry` | dict[scene_id, SceneProfile] + 当前 scene_id |
| `AdmissionPolicy` | strategy 实例（默认 DesktopPolicy）|
| `_label_cache` | 30s repeat-seen 缓存（既有 IngestRunner 行为搬过来）|

| Pool **不**持有 | 真主在 |
|:--|:--|
| `SemanticNode` 本体 | L2BGraph 单 PyDiGraph |
| `SemanticEdge` 本体 | 同上 |
| 大文件 payload | brain.IntentWorkspace |
| Plan / PlanStep 主体 | brain.IntentWorkspace + brain.plan |
| Compartment view | dsg.l2b.compartments |
| 当场写 Graphiti 的能力 | dsg.archive（三阶段管线后异步写）|

### §1.2 Singleton 约定

```python
_pool: L15Pool | None = None

def get_l1_5_pool() -> L15Pool:
    """Per-process singleton, lazy-init."""
```

测试时通过 `set_pool_for_test(pool)` 注入 mock。

---

## §2 公开 API（**这是协议合同**）

### §2.1 入池 / 出池

```python
@dataclass(frozen=True)
class AdmitOutcome:
    admitted_node_uuids: tuple[str, ...]
    rejected: tuple[RejectedObservation, ...]
    promoted: tuple[str, ...]   # TENTATIVE → CONFIRMED
    bucket_assignments: dict[str, BucketKind]   # node_uuid → bucket

@dataclass(frozen=True)
class RejectedObservation:
    obs_id: str
    reason: AdmitRejectReason
    detail: str = ""

class AdmitRejectReason(str, Enum):
    BELOW_CONFIDENCE = "below_confidence"
    BLOCKED_BY_MODE = "blocked_by_mode"           # DsgMode 不允许该 source
    BLOCKED_BY_BUCKET_FROZEN = "bucket_frozen"
    DUPLICATE_IDEMPOTENT = "duplicate_idempotent"
    IMPOSSIBLE_EVENT = "impossible_event"          # P3 占位（baseline 不实施）
    POOL_AT_CAPACITY = "pool_at_capacity"          # P3 占位
    UNKNOWN_BUCKET = "unknown_bucket"


class L15Pool:
    async def admit(
        self,
        observations: tuple[Observation, ...],
        *,
        target_bucket: BucketKind | None = None,    # None = AdmissionPolicy 自动派发
        ctx: AdmissionContext | None = None,         # 当前 IntentEvent / SceneType / GOSLO state
    ) -> AdmitOutcome:
        """
        将一批 Observation 提交到 L1.5 池。
        
        路径：
          1. AdmissionPolicy.evaluate(obs, ctx)  → AdmitDecision (admit / reject / merge)
          2. 桶分配（target_bucket 显式 OR Bucket._infer_from_source）
          3. _find_existing（bucket-scoped 查找：先在目标桶查，再跨桶）
          4. IngestRunner._merge / _observation_to_node（既有逻辑）
          5. 30s repeat-seen 升 CONFIRMED（既有逻辑搬过来）
          6. 更新 BucketRegistry.{bucket}.node_uuids
          7. 更新 RefTable（如 obs 带 obsidian_uuid / graphiti_uuid）
          8. 写 obs_log "ingest_commit"
          9. 返回 AdmitOutcome
        
        不变量：
          - Ingest 仍是唯一 L2-B 写入门（preload 例外）
          - 不当场写 Graphiti（走 archive 管线）
          - 不动 SemanticNode source 字段（已在 ADR-L1.5-001 落定）
        """

    async def evict(
        self,
        node_uuid: str,
        reason: EvictReason,
    ) -> None:
        """
        从池中移除一个节点。
        
        步骤：
          1. 从 BucketRegistry.{bucket}.node_uuids 移除
          2. 从 RefTable 移除相关 ref binding
          3. L2BGraph.remove_node(uuid) — 真删节点（节点本体在 L2-B）
          4. 写 obs_log "ingest_evict"
        
        被调时机：
          - IntentEvent close 后批量（可选；桌面 baseline 不主动 evict）
          - Scene switch（fresh_bucket_kinds 桶清空）
          - 用户显式（roleplay 退出时 clear roleplay 桶）
          - GOSLO_AUTONOMOUS 短 TTL 到期
        """

class EvictReason(str, Enum):
    TTL_EXPIRED = "ttl_expired"
    BUCKET_CLEARED = "bucket_cleared"
    SCENE_SWITCHED = "scene_switched"
    EXPLICIT = "explicit"
    GHOST_TRANSITION = "ghost_transition"   # P3
```

### §2.2 Bucket 管理

```python
class BucketKind(str, Enum):
    """L1.5 池的桶分类。
    
    桌面 baseline 起步：MAIN + OBSIDIAN_SETTING_DAILY + GOOGLE_CALENDAR + AUTONOMOUS_CURIOSITY 4 个常驻
    + ROLEPLAY_TEMP（按需 register/clear）。
    """
    MAIN = "main"                                       # 主桶（默认）
    OBSIDIAN_SETTING_DAILY = "obsidian_setting_daily"   # 永久权威：日常设定（沙发 / 大家具 / 公用场景）
    OBSIDIAN_SETTING_ROLEPLAY = "obsidian_setting_roleplay"  # 永久权威：roleplay 自定义
    GOOGLE_CALENDAR = "google_calendar"                 # 一键导入今日日程
    AUTONOMOUS_CURIOSITY = "autonomous_curiosity"       # GOSLO 主动好奇（短 TTL）
    ROLEPLAY_TEMP = "roleplay_temp"                     # roleplay 模式临时桶（开关切换）

@dataclass(frozen=True)
class BucketSpec:
    kind: BucketKind
    is_authority: bool = False              # 永久权威（不被低 authority 覆盖、不衰减、不 GHOST）
    default_ttl_seconds: float | None = None  # None = 不过期；用于 GOSLO_AUTONOMOUS 等
    preserved_across_scene_switch: bool = False
    cleared_on_scene_switch: bool = False
    max_nodes: int | None = None             # None = 不限；P3 性能调优用
    admission_policy_overrides: dict[str, Any] = field(default_factory=dict)

class BucketHandle:
    spec: BucketSpec
    node_uuids: set[str]                     # 当前桶内节点 UUID 集合
    frozen: bool = False                     # 永久权威桶可冻结，避免误删
    created_at: float
    last_modified_at: float

class BucketOp(BaseModel):
    """触发器 → L1.5 Pool 的桶管理上行通道（dsg_protocol_trigger_v2 用）"""
    op: BucketOpKind
    kind: BucketKind
    payload: dict[str, Any] = Field(default_factory=dict)
    # op=IMPORT 时 payload={items: [...]}; op=CLEAR/FREEZE 无 payload

class BucketOpKind(str, Enum):
    REGISTER = "register"      # 创建新桶（如 ROLEPLAY_TEMP register）
    IMPORT = "import"          # 一键导入数据（如 Google Calendar 今日日程）
    FREEZE = "freeze"          # 冻结桶（永久权威）
    UNFREEZE = "unfreeze"
    CLEAR = "clear"            # 清空桶（roleplay 退出 / fresh_on_scene_switch）
    UNREGISTER = "unregister"  # 移除桶定义（少用）


class L15Pool:
    def register_bucket(self, spec: BucketSpec) -> BucketHandle:
        """创建新桶；幂等（同 kind 二次调用返回既有 handle）"""

    def get_bucket(self, kind: BucketKind) -> BucketHandle | None:
        """查询桶 handle"""

    def list_buckets(
        self, filter: BucketFilter | None = None
    ) -> list[BucketHandle]:
        """枚举桶（按 frozen / authority / source 过滤）"""

    async def import_bucket(
        self, kind: BucketKind, items: tuple[Observation, ...]
    ) -> AdmitOutcome:
        """一键导入。等价 admit(items, target_bucket=kind)"""

    async def freeze_bucket(self, kind: BucketKind) -> None:
        """冻结桶 — 永久权威桶在 SceneType 切换时调用"""

    async def unfreeze_bucket(self, kind: BucketKind) -> None: ...

    async def clear_bucket(self, kind: BucketKind) -> int:
        """清空桶 — 一键删除 roleplay；返回 evict 节点数"""

    async def apply_bucket_op(self, op: BucketOp) -> BucketOpResult:
        """触发器协议入口（dsg_protocol_trigger_v2 §3）"""
```

### §2.3 Ref 表

```python
class RefKind(str, Enum):
    """Ref 信源类型。轻量绑定（不持 payload；payload 在 IntentWorkspace）"""
    GRAPHITI_UUID = "graphiti_uuid"
    OBSIDIAN_UUID = "obsidian_uuid"
    PHOTO_PATH = "photo_path"                  # data/snapshots/objects/{uuid}/reference.jpg
    URL = "url"
    RICH_DOC = "rich_doc"                       # nanobot 富文本汇报路径
    VIDEO_SHORT = "video_short"                 # 短视频片段路径
    AUDIO_CLIP = "audio_clip"
    OTHER = "other"

@dataclass(frozen=True)
class RefBinding:
    node_uuid: str                              # 绑定的 L2-B 节点
    kind: RefKind
    ref_value: str                              # uuid / path / url
    bound_at: float
    last_verified_at: float                     # 健康度检查最后一次成功访问时间
    intent_workspace_ref_id: str = ""           # 若已 stage 到 IntentWorkspace 则填


@dataclass(frozen=True)
class RefHealth:
    binding: RefBinding
    status: RefHealthStatus
    last_check_error: str = ""

class RefHealthStatus(str, Enum):
    HEALTHY = "healthy"           # 最近访问成功
    UNVERIFIED = "unverified"     # 还没检查
    STALE = "stale"               # 超过 TTL 没访问
    BROKEN = "broken"             # 访问失败（文件不存在 / Graphiti 节点删除等）


class L15Pool:
    def bind_ref(
        self,
        node_uuid: str,
        kind: RefKind,
        ref_value: str,
        intent_workspace_ref_id: str = "",
    ) -> RefBinding:
        """绑定 Ref 到节点；幂等"""

    def lookup_by_ref(
        self, kind: RefKind, ref_value: str
    ) -> str | None:
        """反向查找 → node_uuid"""

    def list_refs_of_node(self, node_uuid: str) -> list[RefBinding]:
        """枚举节点所有 Ref"""

    async def verify_ref(self, binding: RefBinding) -> RefHealth:
        """检查 Ref 是否仍有效（visit Graphiti / 检查 file 存在 / HTTP HEAD URL）"""

    async def ref_health_report(
        self, kinds: frozenset[RefKind] | None = None
    ) -> list[RefHealth]:
        """批量健康度报告 — 桌面 baseline 仅 Graphiti / file path / url 三类"""

    def unbind_ref(self, binding: RefBinding) -> None: ...
```

### §2.4 Timeline

```python
class TimelineMarkerKind(str, Enum):
    EPISODE_START = "episode_start"
    EPISODE_CLOSE = "episode_close"
    INTENT_EVENT_OPEN = "intent_event_open"
    INTENT_EVENT_CLOSE = "intent_event_close"
    PLAN_DRAFTED = "plan_drafted"
    PLAN_CONFIRMED = "plan_confirmed"
    PLAN_COMPLETE = "plan_complete"
    PLAN_FAILED = "plan_failed"
    PLAN_CANCELLED = "plan_cancelled"
    SCENE_SWITCHED = "scene_switched"
    BUCKET_OP = "bucket_op"
    NANOBOT_DISPATCHED = "nanobot_dispatched"
    NANOBOT_RESULT = "nanobot_result"
    AUTONOMOUS_CURIOSITY = "autonomous_curiosity"

@dataclass(frozen=True)
class TimelineMarker:
    marker_id: str
    kind: TimelineMarkerKind
    ts: float
    payload: dict[str, Any]      # {episode_id / intent_event_id / plan_id / bucket_kind / ...}
    related_node_uuids: tuple[str, ...] = ()


class L15Pool:
    def mark(
        self,
        kind: TimelineMarkerKind,
        ts: float | None = None,                     # None = now
        payload: dict[str, Any] | None = None,
        related_node_uuids: tuple[str, ...] = (),
    ) -> TimelineMarker:
        """append-only timeline 标记"""

    def get_timeline(
        self,
        window: tuple[float, float] | None = None,    # (start_ts, end_ts) — None = 全量
        kinds: frozenset[TimelineMarkerKind] | None = None,
    ) -> list[TimelineMarker]:
        """检索 timeline；用于 archive 序列化、Plan 监控、观察者读"""

    def serialize_timeline(self, conv_id: str) -> Path:
        """对话结束时 dump 到 data/conversations/{conv_id}/timeline.jsonl"""
```

### §2.5 SceneRegistry（详细见 [`dsg_protocol_scene_snapshot_v1`](dsg_protocol_scene_snapshot_v1_20260506.md)）

```python
@dataclass(frozen=True)
class SceneProfile:
    scene_id: str                                       # "desktop" / "home" / "outdoor" / "library" / ...
    dsg_mode: DsgMode                                   # 既有 enum
    video_tier_hint: VideoTier
    cv_flow_params: dict[str, Any]
    preserved_bucket_kinds: frozenset[BucketKind]
    fresh_bucket_kinds: frozenset[BucketKind]
    priority_overrides: dict[ObservationSource, int] = field(default_factory=dict)
    location_default: str = ""                           # 默认 LocationTag


class L15Pool:
    def current_scene(self) -> SceneProfile: ...

    async def switch_scene(
        self, new_scene_id: str
    ) -> SceneSwitchOutcome:
        """切换 SceneType。详细见 dsg_protocol_scene_snapshot_v1 §3"""
```

### §2.6 健康度 / 容量

```python
@dataclass(frozen=True)
class PoolHealthReport:
    total_nodes: int                                     # 跨所有桶
    nodes_per_bucket: dict[BucketKind, int]
    refs_total: int
    refs_health_distribution: dict[RefHealthStatus, int]
    timeline_marker_count: int
    current_scene: str
    capacity_pressure: PoolCapacityPressure

class PoolCapacityPressure(str, Enum):
    OK = "ok"                                            # 桌面 baseline 永远 OK（不设硬限）
    WATCH = "watch"                                      # P3 调优起点
    WARN = "warn"
    CRITICAL = "critical"


class L15Pool:
    def health(self) -> PoolHealthReport: ...
```

---

## §3 AdmissionPolicy（strategy）

### §3.1 接口

```python
@dataclass(frozen=True)
class AdmissionContext:
    current_intent_event_id: str = ""
    current_scene: SceneProfile | None = None
    goslo_attention_focus: list[str] = field(default_factory=list)   # node_uuid list
    triggering_actor: str = ""                                          # "ssot_enrichment_trigger" / ...

@dataclass(frozen=True)
class AdmitDecision:
    admit: bool
    target_bucket: BucketKind
    confirmation_override: ConfirmationStatus | None = None
    salience_override: Salience | None = None
    reject_reason: AdmitRejectReason | None = None
    notes: str = ""


class PoolAdmissionPolicy(Protocol):
    """L1.5 入池门 strategy。可在 SceneProfile / 测试 / 用户配置切换。"""

    def evaluate(
        self, obs: Observation, ctx: AdmissionContext
    ) -> AdmitDecision: ...
```

### §3.2 桌面 baseline — `DesktopPolicy`

```python
class DesktopPolicy(PoolAdmissionPolicy):
    """桌面起步策略。规则（与 master §1.2 + §1.3 一致）：

    1. confidence < θ_admit (默认 0.3) → REJECT(BELOW_CONFIDENCE)
    2. 桶冻结 → REJECT(BUCKET_FROZEN)
    3. DsgMode 不允许 source → REJECT(BLOCKED_BY_MODE)
    4. 已存在同 obsidian_uuid / graphiti_uuid / label → MERGE（走 IngestRunner._merge）
    5. 否则 → ADMIT，桶推断：
       - source=USER_TAG_OBSIDIAN + meta.profile=daily → OBSIDIAN_SETTING_DAILY
       - source=USER_TAG_OBSIDIAN + meta.profile=roleplay → OBSIDIAN_SETTING_ROLEPLAY
       - source=GOSLO_AUTONOMOUS → AUTONOMOUS_CURIOSITY
       - 其他 → MAIN
       - 若 ctx.current_scene.priority_overrides 命中 → 用 override

    扩展点（仿生升级，本 chat 不做）：
      - 加权投票（多 source 累积证据）
      - "与当前 IntentEvent 相关性"评分
      - 同类第二实例需用户确认（master §1.2 P3）
      - 不可能事件检测（master §1.2 P3）
    """

    def __init__(
        self,
        theta_admit: float = 0.3,
        repeat_window_s: float = 30.0,
    ): ...
```

### §3.3 注册 / 替换

```python
def register_admission_policy(policy: PoolAdmissionPolicy) -> None:
    """全局替换；测试时用"""

def get_admission_policy() -> PoolAdmissionPolicy: ...
```

---

## §4 与既有模块的衔接

### §4.1 `dsg.ingest.runner` 改动

```python
class IngestRunner:
    async def commit_observation(self, obs: Observation) -> bool:
        # 旧路径：直接 _find_existing → _merge / upsert
        # 新路径：调 L15Pool.admit；Pool 内部仍走 IngestRunner._merge / _observation_to_node
        # 两者非循环（admit 在外层做 policy + bucket 派发，内层走 runner 的 merge 逻辑）
        outcome = await get_l1_5_pool().admit(
            (obs,),
            ctx=AdmissionContext(
                current_intent_event_id=_get_current_intent_event(),
                current_scene=get_l1_5_pool().current_scene(),
            ),
        )
        return bool(outcome.admitted_node_uuids or outcome.promoted)

    # 既有 _find_existing / _merge / _observation_to_node 保留（被 Pool 内部调用）

# TODO(S4.B) 注释更新：
#   旧：write-back to Graphiti here for CONFIRMED nodes
#   新：禁止当场写回；走 dsg_protocol_archive_v1 三阶段管线
```

### §4.2 `dsg.l2b_graph` 改动

```python
class L2BGraph:
    def start_episode(self, title: str = "", trigger_source: str = "") -> EpisodeMarker:
        if self._current_episode_id:
            old_ep = self.close_current_episode()
            if old_ep:
                # 旧：loop.create_task(self.archive_episode_to_graphiti(old_ep.episode_id))
                # 新：交给 archive 管线（dsg_protocol_archive_v1）
                from parrot.dsg.archive.conversation import enqueue_episode_for_idle_archive
                enqueue_episode_for_idle_archive(old_ep.episode_id)
        # 其余逻辑不变
```

### §4.3 `dsg.triggers.runner` 改动

参见 [`dsg_protocol_trigger_v2_20260506.md`](dsg_protocol_trigger_v2_20260506.md) §4。

---

## §5 协议合同 0 漂移核对

| 检查项 | 状态 |
|:--|:--|
| Phase 4 §8 L1（NodeKind / EdgeKind enum）| ✅ 不动 — Pool 不增删 enum |
| Phase 4 §8 L7（PhotoEvent 不自动建 ObjectNode）| ✅ 不动 — Pool 不调 PhotoEvent |
| Phase 4 §8 L9（attention threshold）| ✅ 不动 — Pool 不读不写 attention 数值 |
| Phase 4 §8 L11（identify_object 1.9s 预算）| ✅ 不动 — Pool 异步，identify_object 走 IngestRunner 链路不变 |
| Phase 4 §8 L13（dsg/attention export 集合）| ✅ 不动 — Pool 不 export attention 类 |
| ADR-L1.5-001 §2.1 Q1（source 仅 Python）| ✅ 仍 Python only — Pool 全部内部模块 |
| ADR-L1.5-001 §4.1 三触发器 | ⚠️ 实施完核对（预测：不触发 — 详见主设计稿 §9）|
| `parrot_behavior_rules §3.7` | ✅ Pool 不抓帧 / 不写 Graphiti / 不读写 attention BB |
| `tests/test_ecp_event/test_cs_parity.py` 4/4 | ✅ Pool 不动 wire / EcpEventType / EcpEventSource |
| 测试基线 234/234 + ADR-L1.5-001 11 项 | ✅ 既有测试 0 改动 |

---

## §6 测试覆盖

```python
# tests/test_dsg/test_admission_baseline.py
def test_admit_below_confidence_rejected(): ...
def test_admit_above_confidence_admitted(): ...
def test_admit_routes_user_tag_obsidian_to_daily_bucket(): ...
def test_admit_routes_user_tag_obsidian_roleplay_to_roleplay_bucket(): ...
def test_admit_routes_goslo_autonomous_to_autonomous_curiosity_bucket(): ...
def test_admit_30s_repeat_seen_promotes_tentative_to_confirmed(): ...
def test_admit_blocked_by_dsg_mode(): ...
def test_admit_blocked_by_frozen_bucket(): ...
def test_admit_idempotent_on_duplicate_obsidian_uuid(): ...

# tests/test_dsg/test_bucket_lifecycle.py
def test_register_bucket_idempotent(): ...
def test_freeze_bucket_blocks_admit(): ...
def test_clear_bucket_evicts_all_nodes(): ...
def test_import_bucket_one_shot_admit_batch(): ...
def test_unregister_bucket_after_clear(): ...
def test_roleplay_bucket_clear_does_not_touch_main(): ...

# tests/test_dsg/test_ref_table_stability.py
def test_bind_ref_idempotent(): ...
def test_lookup_by_ref_returns_node_uuid(): ...
def test_lookup_returns_none_when_unbound(): ...
def test_verify_ref_healthy_for_existing_file(): ...
def test_verify_ref_broken_for_missing_file(): ...
def test_ref_health_report_aggregates_by_status(): ...
def test_unbind_ref_removes_binding(): ...

# tests/test_dsg/test_timeline_event_alignment.py
def test_mark_episode_start(): ...
def test_mark_intent_event_open_and_close(): ...
def test_mark_plan_lifecycle_markers_in_order(): ...
def test_get_timeline_window_filters_by_ts(): ...
def test_get_timeline_filters_by_kinds(): ...
def test_serialize_timeline_to_jsonl(): ...

# tests/test_dsg/test_pool_health.py
def test_health_report_node_count(): ...
def test_health_report_per_bucket(): ...
def test_health_report_capacity_pressure_ok_when_unset(): ...
```

→ 共 **27 项新测试**。所有测试**仅验证协议接口能力**，不验证仿生实现细节。

---

## §7 扩展点（**给未来 P3 / 第三方 Pool 包替换者**）

| 扩展点 | 当前实现 | P3+ 升级方向 |
|:--|:--|:--|
| `PoolAdmissionPolicy` strategy | DesktopPolicy（confidence + 30s repeat-seen） | 加权投票 / IntentEvent 相关性 / 多帧累积 / 不可能事件 |
| `RefHealthMonitor` | binary（绑定 / 失效） | Ebbinghaus 衰减 / 访问频次 / 时间衰减 |
| `BucketSpec.max_nodes` | None（不限） | 性能调优 + 自动淘汰 |
| `BucketSpec.default_ttl_seconds` | None / GOSLO_AUTONOMOUS=300s | 按 source / kind 差异化 TTL |
| Storage backend | InMemory dict | Redis / SQLite / FAISS embedding 索引 |
| `_label_cache` | dict[label, (ts, source)] | LRU 缓存 / time-bucket 哈希 |
| `serialize_timeline` 格式 | JSONL | 加压缩 / 分片 / 索引 |

→ 都通过 **strategy 注册表 + Backend Protocol** 支持替换（`register_admission_policy` / `register_ref_storage_backend` / 等）。

---

## §8 引用

- 主设计稿：[`dsg_l1_5_pool_and_lifecycle_design_20260506.md`](dsg_l1_5_pool_and_lifecycle_design_20260506.md)
- 触发器协议：[`dsg_protocol_trigger_v2_20260506.md`](dsg_protocol_trigger_v2_20260506.md)
- 归档协议：[`dsg_protocol_archive_v1_20260506.md`](dsg_protocol_archive_v1_20260506.md)
- IntentWorkspace 协议：[`brain_protocol_intent_workspace_v1_20260506.md`](brain_protocol_intent_workspace_v1_20260506.md)
- Scene Snapshot 协议：[`dsg_protocol_scene_snapshot_v1_20260506.md`](dsg_protocol_scene_snapshot_v1_20260506.md)
- master 决策：[`dsg_decisions_master.md`](dsg_decisions_master.md)
- ADR-L1.5-001：[`../adr_l1_5_source_dispatch_extension_space_20260504.md`](../adr_l1_5_source_dispatch_extension_space_20260504.md)
- Phase 4 §8 锁：[`../sprint4_phase4_entry_20260430.md`](../sprint4_phase4_entry_20260430.md)
- 行为契约：[`../../parrot_behavior_rules.md §3.7`](../../parrot_behavior_rules.md)

---

## §9 变更日志

- **2026-05-06**：本协议 V1 创建。L1.5 Pool 完整 API surface（admit / evict / bucket ops / ref table / timeline / scene / health）+ AdmissionPolicy strategy + DesktopPolicy baseline + 27 项验证测试 + 7 处扩展点接口锚点。
