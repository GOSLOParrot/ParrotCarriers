---
status: draft
category: protocol-spec
protocol_id: DSG-INTENT-EVENT-V1
status_note: "L2-B IntentEventBoundary 协议 V1 — 认知边界触发的 L2-B 拓扑机制：标签 / 降权 / 折叠 / 跨通道。桌面 baseline = 标签 + 降权（不真折叠）；P3+ 仿生升级走 RustworkX subgraph / Cluster / Spreading Activation。"
last_reviewed: 2026-05-06
ai_priority: high
ai_audience: "实施 chat / 独立审计 chat / P3 仿生升级 chat"
parent_doc: "dsg_l1_5_pool_and_lifecycle_design_20260506.md"
companion_protocols:
  - "dsg_protocol_pool_v1_20260506.md"
  - "dsg_protocol_trigger_v2_20260506.md"
  - "brain_protocol_plan_v1_20260506.md"
---

# DSG-INTENT-EVENT-V1 — IntentEventBoundary 协议

> **协议 ID**：DSG-INTENT-EVENT-V1
> **范围**：`src/parrot/dsg/l2b/intent_event_boundary.py` + `dsg/triggers/intent_event_boundary_trigger.py`。
> **本质**：GOSLO **认知层**任务边界（与 SceneType 物理切换、Episode 对话段、NanobotTask 异步派发**正交**）。
> **不在范围**：完整折叠机制（P3+，留接口）/ Plan 状态机（在 [`brain_protocol_plan_v1`](brain_protocol_plan_v1_20260506.md)）。

---

## §0 术语表

`IntentEvent` = GOSLO Intent 层的一次"我现在专注于 X"的认知聚焦窗口。1 个 Episode 内嵌多个 IntentEvent。详见 [主设计稿 §0](dsg_l1_5_pool_and_lifecycle_design_20260506.md)。

**与既有概念的关系**：

| | Episode | **IntentEvent** | NanobotTask |
|:--|:--|:--|:--|
| 层 | 对话段 | **认知边界** | 异步任务 |
| 触发 | manage_episode tool | tool call / nanobot result / long idle / explicit | dispatch_task tool |
| 持续 | per-session（用户与 GOSLO 一段对话）| 1+ per Episode | per task |
| 主存 | L2-B EpisodeMarker（既有）| L2-B IntentEventBoundaryHandler 状态（新）| Scheduler + Nanobot |
| 节点字段 | `episode_id` | `event_id` | nanobot_task_id（在 NanobotTask 自己的存储） |

---

## §1 IntentEventBoundary 触发源

| Reason | 触发源 | 频率 |
|:--|:--|:--|
| `TOOL_CALL_BOUNDARY` | GOSLO 调 manage_episode / set_mode / dispatch_task / identify_object（任一）| 中 |
| `NANOBOT_RESULT_RETURN` | NanobotTask 完成 / 失败 result 回流 | 低-中 |
| `LONG_IDLE` | ≥ 配置阈值（桌面默认 5min 无 ingest_commit / tool call）| 低 |
| `PLAN_PHASE_CHANGE` | Plan DRAFT → CONFIRMED / EXECUTING → DONE 等 | 低 |
| `EXPLICIT` | Brain function tool / Trigger 显式调 | 任意 |

```python
class IntentEventReason(str, Enum):
    TOOL_CALL_BOUNDARY = "tool_call_boundary"
    NANOBOT_RESULT_RETURN = "nanobot_result_return"
    LONG_IDLE = "long_idle"
    PLAN_PHASE_CHANGE = "plan_phase_change"
    EXPLICIT = "explicit"
```

---

## §2 IntentEventBoundaryHandler 接口

```python
@dataclass(frozen=True)
class IntentEventState:
    event_id: str
    reason: IntentEventReason
    opened_at: float
    closed_at: float = 0.0
    member_node_uuids: tuple[str, ...] = ()
    triggering_actor: str = ""                       # tool name / trigger name
    related_plan_id: str = ""                         # 若与某 Plan 关联
    related_episode_id: str = ""                      # 当前所在 Episode

class IntentEventBoundaryHandler:
    """L2-B 认知边界处理。
    
    桌面 baseline：
      - 节点字段 event_id 标注（不真折叠）
      - 旧 event 节点 attention *= decay_factor（默认 0.7，策略可调）
      - 跨 event 边保留（不删）
      - FoldStrategy = NoOp
    
    P3+ 仿生升级（接口已留，实现 P3）：
      - FoldStrategy.fold(event_id) → RustworkX subgraph 折叠
      - Cluster 折叠（rustworkx-master §3.4 范式四）
      - Spreading Activation 跨 event 通道（attention-schema-papers §5.4）
      - VF2++ 子图同构识别经验（rustworkx-master §2.5）
    """

    def open(
        self,
        reason: IntentEventReason,
        triggering_actor: str = "",
        related_plan_id: str = "",
        related_node_uuids: tuple[str, ...] = (),
    ) -> IntentEventState:
        """开启新 IntentEvent。
        
        步骤：
          1. 若有 active event（self._current_event_id）→ close(它)
          2. 生成新 event_id = f"ev_{int(now)}_{uuid4().hex[:4]}"
          3. 给当前 active 节点（attention > threshold）打 event_id
          4. 写 Timeline marker INTENT_EVENT_OPEN
          5. 返回 state
        """

    def close(self, event_id: str) -> IntentEventState:
        """关闭 IntentEvent。
        
        步骤：
          1. 调 _decay_strategy.decay(event_id) — baseline noop / P3 真衰减
          2. 调 _fold_strategy.fold(event_id) — baseline noop / P3 真折叠
          3. 写 Timeline marker INTENT_EVENT_CLOSE
          4. 若 event 关联 Plan → 不主动删 Plan 状态（Plan 自己有 lifecycle）
        """

    def current_event_id(self) -> str: ...
    
    def get_event_state(self, event_id: str) -> IntentEventState | None: ...
    
    def list_events(
        self, episode_id: str | None = None
    ) -> list[IntentEventState]: ...

    def cross_event_channel(
        self, src_event_id: str, dst_event_id: str
    ) -> list[SemanticEdge]:
        """获取跨 event 边（关联通道）。
        
        桌面 baseline：返回所有 src/dst event 节点之间的边
        P3+：按通道权重过滤 / Spreading Activation 衰减
        """
```

---

## §3 节点字段使用约定

```python
class SemanticNode:
    # ... 既有字段不动 ...
    event_id: str = ""    # 当前所在 IntentEvent；空 = 未关联到任何 IntentEvent
    # ... 其他新字段（bucket_id / scene_type / location_tag）见主设计稿 §2.2 ...
```

**赋值时机**：
- IngestRunner.commit_observation → 给新建节点打当前 active event_id
- IntentEventBoundaryHandler.open → 给当前 active 节点（attention > threshold）也带上
- IntentEventBoundaryHandler.close → 不动节点 event_id（保留历史归属）

**消费方**：
- L2BGraph.view_by_event(event_id) → 当前 IntentEvent 内的节点
- IntentEventBoundaryHandler.cross_event_channel → 跨 event 边
- ConversationArchive 序列化时按 event_id 分组

---

## §4 桌面 Baseline 实现

### §4.1 NoOpFoldStrategy

```python
class FoldStrategy(Protocol):
    def fold(self, event_id: str, graph: L2BGraph) -> FoldResult: ...

@dataclass(frozen=True)
class FoldResult:
    folded_node_uuids: tuple[str, ...]
    folded_edges_count: int
    cluster_id: str = ""

class NoOpFoldStrategy(FoldStrategy):
    """桌面 baseline — 不真折叠，仅返回成员清单"""
    def fold(self, event_id: str, graph: L2BGraph) -> FoldResult:
        member_uuids = [n.uuid for n in graph.all_nodes() if n.event_id == event_id]
        return FoldResult(folded_node_uuids=tuple(member_uuids), folded_edges_count=0)
```

### §4.2 SimpleDecayStrategy

```python
class AttentionDecayStrategy(Protocol):
    def decay(self, event_id: str, graph: L2BGraph) -> int: ...

class SimpleDecayStrategy(AttentionDecayStrategy):
    """桌面 baseline — 旧 event 节点 attention *= 0.7（策略可调）"""
    def __init__(self, decay_factor: float = 0.7):
        self._factor = decay_factor

    def decay(self, event_id: str, graph: L2BGraph) -> int:
        affected = 0
        for n in graph.all_nodes():
            if n.event_id == event_id:
                n.attention = max(0.0, n.attention * self._factor)
                affected += 1
        return affected
```

### §4.3 NoOpDecayStrategy（测试期）

```python
class NoOpDecayStrategy(AttentionDecayStrategy):
    """测试期不衰减（master §3.5 ratified）"""
    def decay(self, event_id: str, graph: L2BGraph) -> int:
        return 0
```

→ 测试期默认 `NoOpDecayStrategy`；后续 P3 实测后切到 `SimpleDecayStrategy`。

---

## §5 与 Plan 的关联

详见 [`brain_protocol_plan_v1_20260506.md`](brain_protocol_plan_v1_20260506.md) §4。

简表：

| Plan 状态 | IntentEvent 行为 |
|:--|:--|
| DRAFT | 在当前 IntentEvent 内（GOSLO 阻塞对话期间）|
| AWAITING_USER_CONFIRMATION | 同上（仍在阻塞）|
| APPROVED | open 新 IntentEvent(reason=PLAN_PHASE_CHANGE)；释放阻塞 |
| EXECUTING | NanobotTask 派发；当 result 回流 → open 新 IntentEvent(reason=NANOBOT_RESULT_RETURN) |
| DONE / FAILED / CANCELLED | open 新 IntentEvent(reason=PLAN_PHASE_CHANGE, related_plan_id=...) |

→ Plan 生命周期变更**通过 IntentEvent 边界**反映在 L2-B（不直接改节点拓扑）。

---

## §6 协议合同 0 漂移核对

| 检查项 | 状态 |
|:--|:--|
| Phase 4 §8 L1（NodeKind / EdgeKind enum）| ✅ 不增不删 — 复用现有 |
| Phase 4 §8 L9（attention threshold 数值）| ✅ 不动 — IntentEvent 不读不写 threshold |
| ADR-L1.5-001 §4.1 升级条件 | ✅ 未触发 — IntentEvent 处理器不读节点 source |
| `parrot_behavior_rules §3.7` Observer-Attention 边界 | ✅ IntentEvent 改的是 SemanticNode.attention（运行时字段，不是 dsg/attention/threshold.py 边界）— 这是合规的，因为 attention/threshold.py 仍不塞 BB |
| `tests/test_ecp_event/test_cs_parity.py` 4/4 | ✅ 不动 wire |

---

## §7 测试覆盖

```python
# tests/test_dsg/test_intent_event_boundary_minimum.py
def test_open_event_assigns_event_id_to_active_nodes(): ...
def test_close_event_invokes_decay_strategy(): ...
def test_close_event_invokes_fold_strategy(): ...
def test_open_replaces_previous_active_event(): ...
def test_baseline_noop_decay_does_not_change_attention(): ...
def test_simple_decay_strategy_multiplies_factor(): ...
def test_baseline_noop_fold_returns_member_list(): ...
def test_view_by_event_filters_nodes(): ...
def test_cross_event_channel_returns_edges(): ...
def test_event_id_persists_after_close(): ...
def test_timeline_markers_for_open_and_close(): ...

# tests/test_dsg/test_intent_event_plan_alignment.py
def test_plan_phase_change_opens_new_intent_event(): ...
def test_nanobot_result_opens_new_intent_event(): ...
def test_long_idle_opens_new_intent_event(): ...
```

→ 共 **14 项新测试**。

---

## §8 扩展点（P3+ 仿生升级路径）

| 扩展点 | 当前 baseline | P3+ 升级 | 锚点 |
|:--|:--|:--|:--|
| `FoldStrategy` | NoOp | RustworkX subgraph 折叠 / Cluster | rustworkx-master §3.4 |
| `AttentionDecayStrategy` | NoOp（测试）/ Simple 0.7（实测后切） | TWF / Ebbinghaus / 量子化 | superlocalmemory §C / attention-schema-papers §5 |
| `cross_event_channel` | 返回所有边 | 衰减权重 / 抑制性边 / 联想阈值 | rustworkx-master §3.2 / 案例 §122 |
| 跳数硬上界 | 4 跳（AGCN 实证） | 按任务类型分级 | attention-schema-papers §1.3 |
| event 关联 Plan 联想 | event_id + plan_id 字段 join | RustworkX 子图同构 / VF2++ | rustworkx-master §2.5 |
| 健康度监控 | 无 | betweenness / clustering / 模块化 | attention-schema-papers §4 |

---

## §9 引用

- 主设计稿：[`dsg_l1_5_pool_and_lifecycle_design_20260506.md`](dsg_l1_5_pool_and_lifecycle_design_20260506.md)
- 触发器协议：[`dsg_protocol_trigger_v2_20260506.md`](dsg_protocol_trigger_v2_20260506.md)
- Plan 协议：[`brain_protocol_plan_v1_20260506.md`](brain_protocol_plan_v1_20260506.md)
- skills：[`dsg-rustworkx-master §3`](../../../skills/dsg-rustworkx-master/SKILL.md) / [`dsg-attention-schema-papers §1.3 §5.4`](../../../skills/dsg-attention-schema-papers/SKILL.md)
- 既有代码：`src/parrot/dsg/l2b_graph.py` / `src/parrot/dsg/l2b_types.py`

---

## §10 变更日志

- **2026-05-06**：本协议 V1 创建。IntentEventBoundary 桌面 baseline（NoOp fold + NoOp/Simple decay）+ 节点 event_id 字段约定 + Plan 联动 + 14 项验证测试 + 6 处 P3 仿生升级接口锚点。
