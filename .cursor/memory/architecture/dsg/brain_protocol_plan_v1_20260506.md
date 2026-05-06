---
status: draft
category: protocol-spec
protocol_id: BRAIN-PLAN-V1
status_note: "Brain Plan-and-Execute 协议 V1 — Plan / PlanStep / PlanLifecycle / PlanBlackboard + Plan 主存 IntentWorkspace + L2-B 镜像 reuse NodeKind.EVENT。借鉴 LangChain Plan-and-Execute / Cursor Composer / Devin / AutoGPT 模式。Wire 升级（用户确认 Plan UI）留 P3。"
last_reviewed: 2026-05-06
ai_priority: high
ai_audience: "实施 chat / GOSLO Plan 使用者 / 独立审计 chat / Unity wire 升级 chat（P3）"
parent_doc: "dsg_l1_5_pool_and_lifecycle_design_20260506.md"
companion_protocols:
  - "dsg_protocol_pool_v1_20260506.md"
  - "dsg_protocol_trigger_v2_20260506.md"
  - "dsg_protocol_intent_event_boundary_v1_20260506.md"
  - "dsg_protocol_archive_v1_20260506.md"
  - "brain_protocol_intent_workspace_v1_20260506.md"
---

# BRAIN-PLAN-V1 — Plan-and-Execute 协议

> **协议 ID**：BRAIN-PLAN-V1
> **范围**：`src/parrot/brain/plan/` 子包 + `SemanticNode.source_meta.plan_role` 约定。
> **核心模式**（用户原话锚定）：鹦鹉 Intent 阻塞 → 制定 Plan → 用户确认 → 派发 → 解除阻塞 → 异常时汇报。
> **不在范围**：用户在 Unity 确认 Plan 的 EcpEvent 字段（**wire 升级 P3**，本协议留接口）/ Plan UI 渲染细节（Unity App 设计）。

---

## §0 术语表（与主设计稿 §0 等同；强调本协议关键概念）

| 中文 | 官方名称 | 主存储 | L2-B 镜像 |
|:--|:--|:--|:--|
| 计划 | **`Plan`** | **IntentWorkspace**（StagedRefKind.PLAN）| `NodeKind.EVENT` + `source_meta.plan_role="plan_root"` + `source_meta.plan_id` |
| 计划步骤 | **`PlanStep`** | IntentWorkspace（Plan 内部结构）| `NodeKind.EVENT` + `plan_role="plan_step"` + `plan_id` |
| 副黑板 | **`PlanBlackboard`** | py-trees BB 子命名空间 `plan/{plan_id}/...` | — |
| 异步任务 | **`NanobotTask`**（既有名）| Scheduler + Nanobot | — |

**层级关系**：
```
Episode  ⊃  IntentEvent  ⊃  Plan（可选）  ⊃  PlanStep × N  ⊃  NanobotTask × M
                          (per IntentEvent 0+ Plan)
```

→ **不是每个 IntentEvent 都有 Plan**；简单 Intent（直接 tool 调用 + 立即响应）无 Plan；复杂 Intent（多步研究 / 长任务）才进 Plan。

---

## §1 设计起源

### §1.1 用户原话锚定（2026-05-06）

> 我们把这个类似于是 L2-B 里的 GOSLO Intent 层管理的子图叫成 Plan 吧，相当一一个大的时间线子图，里程碑表和副黑板？
> 叫 Plan 子图？这样 GOSLO 可以 make Plan 和监控 tasks 了。
>
> IntentWorkspace 为主，L2-B 读 IntentWorkspace 吧。
>
> Plan 来安排 tasks，这种中大型 Plan to tasks 流程是鹦鹉 Intent 阻塞对话安排 Plan，给用户 UnityApp 展示 Plan，用户确定后派发，然后鹦鹉就不阻塞了，可以对话，出现问题汇报。

### §1.2 借鉴的成熟模式

| 项目 | 模式 | 我们抄什么 |
|:--|:--|:--|
| **LangChain Plan-and-Execute** | Planner LLM → Plan steps → Executor | DRAFT → CONFIRMED → EXECUTING → DONE 状态机 |
| **Cursor Composer** | Plan → User Approves → Apply | "用户确认门" 在 APPROVED 状态前 |
| **Devin** | Plan → Show to user → Execute → Report | Plan 显示给用户 + 异常汇报路径 |
| **AutoGPT / BabyAGI** | Plan → Execute → Reflect → Re-Plan | Plan 失败 → 起新 Plan（修订版）|
| **OpenAI o1 chain-of-thought** | think then respond | Intent 阻塞期间的"想一会儿"模式 |

---

## §2 Plan / PlanStep / PlanState

### §2.1 PlanState

```python
class PlanState(str, Enum):
    DRAFT = "draft"
    """GOSLO 正在制定（Intent 阻塞期间）"""
    
    AWAITING_USER_CONFIRMATION = "awaiting_user_confirmation"
    """已发给用户 UI（wire 升级 P3）；等待 EcpCommand 确认信号"""
    
    APPROVED = "approved"
    """用户确认 → 准备派发 NanobotTask；GOSLO 可解除阻塞"""
    
    EXECUTING = "executing"
    """至少一个 PlanStep 正在执行（NanobotTask in flight）"""
    
    PARTIAL_COMPLETE = "partial_complete"
    """部分 PlanStep 完成；可能等其他 / 用户决定是否继续"""
    
    COMPLETE = "complete"
    """所有 PlanStep 完成"""
    
    FAILED = "failed"
    """Plan 整体失败（不可恢复）"""
    
    CANCELLED = "cancelled"
    """用户取消 / GOSLO 撤销"""
    
    REVISED = "revised"
    """触发新 Plan 替代（修订版）；旧 Plan 标 superseded_by=new_plan_id"""


class PlanStepState(str, Enum):
    PENDING = "pending"
    DISPATCHED = "dispatched"            # 已派发 NanobotTask（task_id 已分配）
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"                   # 依赖失败 / 用户跳过
```

### §2.2 Plan / PlanStep dataclass

```python
@dataclass
class PlanStep:
    step_id: str                          # uuid4().hex[:8]
    title: str
    description: str = ""
    
    # 派发约定
    expected_tool: str = ""                # Brain function tool 名 / NanobotTask 类型
    inputs: dict[str, Any] = field(default_factory=dict)
    
    # 依赖
    depends_on: tuple[str, ...] = ()       # 其他 step_id
    
    # 执行状态
    state: PlanStepState = PlanStepState.PENDING
    nanobot_task_id: str = ""              # 派发后填
    started_at: float = 0.0
    completed_at: float = 0.0
    
    # 结果
    result_summary: str = ""
    result_ref_id: str = ""                # IntentWorkspace StagedRef ref_id（若 result 是 RICH_REPORT）
    error: str = ""


@dataclass
class Plan:
    plan_id: str                          # uuid4().hex[:12]
    title: str
    rationale: str = ""                    # GOSLO 制定的理由
    
    # 时间轴
    drafted_at: float = field(default_factory=time.time)
    approved_at: float = 0.0
    started_executing_at: float = 0.0
    completed_at: float = 0.0
    
    # 状态
    state: PlanState = PlanState.DRAFT
    
    # 关联上下文
    intent_event_id: str = ""              # 所属 IntentEvent
    episode_id: str = ""                    # 所属 Episode
    related_node_uuids: tuple[str, ...] = ()
    related_staged_ref_ids: tuple[str, ...] = ()
    
    # 行为标志
    blocks_conversation: bool = True       # Intent 阻塞模式（默认 True）
    estimated_duration_s: float = 0.0
    
    # 步骤
    steps: list[PlanStep] = field(default_factory=list)
    
    # 修订
    superseded_by: str = ""                # 若被新 Plan 替代
    supersedes: str = ""                    # 替代了哪个旧 Plan
    
    # IntentWorkspace 主存
    staged_ref_id: str = ""                # 自身在 IntentWorkspace 的 ref_id
    
    # PlanBlackboard 命名空间
    blackboard_namespace: str = ""         # plan/{plan_id}/
```

---

## §3 PlanProposal（触发器上行通道）

```python
@dataclass(frozen=True)
class PlanProposal:
    """触发器向 GOSLO 提案 Plan；GOSLO 评估后决定是否真做 PlanRegistry.draft"""
    proposed_by: str                       # trigger_name
    title: str
    rationale: str
    suggested_steps: tuple["PlanStepProposal", ...]
    suggested_intent_event_kind: str = ""
    related_node_uuids: tuple[str, ...] = ()
    related_staged_ref_ids: tuple[str, ...] = ()
    estimated_duration_s: float = 0.0
    blocks_conversation: bool = False

@dataclass(frozen=True)
class PlanStepProposal:
    step_id: str                           # 提案者临时 ID
    title: str
    expected_tool: str = ""
    inputs: dict[str, Any] = field(default_factory=dict)
    depends_on: tuple[str, ...] = ()
```

---

## §4 PlanLifecycle 状态机

```
                ┌──────┐
                │DRAFT │ ← GOSLO 制定 (Intent 阻塞)
                └──┬───┘
                   │ submit_for_confirmation()
                   ▼
       ┌──────────────────────────────┐
       │ AWAITING_USER_CONFIRMATION   │ ← 发给 Unity (wire 升级 P3)
       └──┬─────────────────────────┬─┘
          │ approve()                │ cancel()
          ▼                          ▼
       ┌─────────┐              ┌──────────┐
       │APPROVED │              │CANCELLED │ ← 用户取消
       └────┬────┘              └──────────┘
            │ start_executing() ← 解除 Intent 阻塞
            ▼
       ┌──────────┐
       │EXECUTING │ ← NanobotTask in flight
       └────┬─────┘
            │
   ┌────────┼────────────────┐
   │        │                │
   ▼        ▼                ▼
PARTIAL_  COMPLETE       FAILED
COMPLETE  ← all done    ← unrecoverable
   │ resume_or_revise()
   ▼
EXECUTING / REVISED
```

```python
class PlanLifecycle:
    """Plan 状态转换规则。enforce_transition 在 PlanRegistry 调用。"""

    LEGAL_TRANSITIONS: dict[PlanState, frozenset[PlanState]] = {
        PlanState.DRAFT: frozenset({
            PlanState.AWAITING_USER_CONFIRMATION,
            PlanState.CANCELLED,
        }),
        PlanState.AWAITING_USER_CONFIRMATION: frozenset({
            PlanState.APPROVED,
            PlanState.CANCELLED,
            PlanState.REVISED,
        }),
        PlanState.APPROVED: frozenset({
            PlanState.EXECUTING,
            PlanState.CANCELLED,
        }),
        PlanState.EXECUTING: frozenset({
            PlanState.PARTIAL_COMPLETE,
            PlanState.COMPLETE,
            PlanState.FAILED,
            PlanState.CANCELLED,
        }),
        PlanState.PARTIAL_COMPLETE: frozenset({
            PlanState.EXECUTING,
            PlanState.COMPLETE,
            PlanState.FAILED,
            PlanState.CANCELLED,
            PlanState.REVISED,
        }),
        PlanState.COMPLETE: frozenset({}),
        PlanState.FAILED: frozenset({PlanState.REVISED}),
        PlanState.CANCELLED: frozenset({}),
        PlanState.REVISED: frozenset({}),
    }

    @classmethod
    def can_transition(cls, from_state: PlanState, to_state: PlanState) -> bool: ...

    @classmethod
    def enforce_transition(cls, plan: Plan, to_state: PlanState) -> None:
        """合法 → 改 plan.state；非法 → raise IllegalPlanTransition"""
```

---

## §5 PlanRegistry 接口

```python
class PlanRegistry:
    """Plan 中心管理 — singleton。"""

    async def draft(self, proposal: PlanProposal) -> Plan:
        """从 PlanProposal 创建 Plan(DRAFT)。
        
        步骤：
          1. 生成 plan_id
          2. 把 PlanStepProposal 转 PlanStep
          3. 关联当前 IntentEvent / Episode
          4. 调 IntentWorkspace.stage(kind=PLAN, payload=Plan json) → ref_id
          5. plan.staged_ref_id = ref_id
          6. plan.blackboard_namespace = f"plan/{plan_id}"
          7. 写 Timeline marker PLAN_DRAFTED
          8. 注册到 self._active_plans
          9. 返回 Plan
        """

    async def submit_for_confirmation(self, plan_id: str) -> None:
        """DRAFT → AWAITING_USER_CONFIRMATION。
        
        副作用：
          - 发 EcpEvent 通知 Unity 渲染 Plan UI（wire 升级 P3，本 chat 留接口）
          - 写 Timeline marker
        """

    async def approve(self, plan_id: str) -> None:
        """AWAITING_USER_CONFIRMATION → APPROVED。
        
        副作用：
          - 解除 Intent 阻塞标志（plan.blocks_conversation=False）
          - GOSLO 可继续对话
          - 写 Timeline marker PLAN_CONFIRMED
        """

    async def start_executing(self, plan_id: str) -> None:
        """APPROVED → EXECUTING。
        
        副作用：
          - 派发**无依赖**的 PlanStep 为 NanobotTask（dispatch_task）
          - PlanStep.state = DISPATCHED
          - 监听 NanobotTask result channel
        """

    async def report_step_result(
        self, plan_id: str, step_id: str, result: NanobotTaskResult
    ) -> None:
        """监听 NanobotTask result 回流；更新 PlanStep + 链式派发依赖步骤"""

    async def cancel(self, plan_id: str, reason: str = "") -> None: ...

    async def revise(
        self, old_plan_id: str, new_proposal: PlanProposal
    ) -> Plan:
        """起新 Plan 替代（FAILED / PARTIAL_COMPLETE 后的修订版）"""

    def get(self, plan_id: str) -> Plan | None: ...
    def get_current_plan(self) -> Plan | None:
        """当前 active Plan（最近 DRAFT 或 EXECUTING 的）"""
    def list_active(self) -> list[Plan]: ...
    def list_by_intent_event(self, intent_event_id: str) -> list[Plan]: ...
    def list_by_episode(self, episode_id: str) -> list[Plan]: ...
```

---

## §6 PlanBlackboard

### §6.1 命名空间约定

```
parrot.scheduler.blackboard 既有命名空间：
  scheduler/        Scheduler 内部状态
  transient/        短期共享（attention hint 等）
  session/          session 级（dsg_mode / video_tier）

新增（本协议）：
  plan/{plan_id}/   Plan 范围副黑板（每 Plan 独立）
    /state          PlanState
    /current_step   当前 active step_id
    /step_results   dict[step_id, result_summary]
    /custom         GOSLO 自定义键
```

### §6.2 PlanBlackboardClient

```python
class PlanBlackboardClient:
    """Plan 范围副黑板 — py-trees Blackboard V2 子命名空间封装"""

    def __init__(self, plan_id: str):
        self._namespace = f"plan/{plan_id}/"
        self._client = open_bb_client(name=f"plan_{plan_id}", writer=...)

    def set(self, key: str, value: Any) -> None: ...
    def get(self, key: str, default: Any = None) -> Any: ...
    def delete(self, key: str) -> None: ...
    def all_keys(self) -> list[str]: ...
    
    def cleanup(self) -> None:
        """Plan close 时清理整个 namespace"""
```

---

## §7 与其他协议的关联

### §7.1 与 IntentWorkspace（主存）

```python
# Plan 主存：stage(kind=PLAN)
ws = get_intent_workspace()
plan_handle = await ws.stage(StagedRefRequest(
    kind=StagedRefKind.PLAN,
    payload_source=PayloadSource.INLINE_TEXT,
    payload_value=plan.model_dump_json(),
    metadata=StagedRefMetadata(
        origin=f"plan_registry:{plan.plan_id}",
        related_intent_event_id=plan.intent_event_id,
        related_plan_id=plan.plan_id,
        auto_evict_on_intent_close=False,   # Plan 跨 IntentEvent 存活到 COMPLETE
    ),
))
plan.staged_ref_id = plan_handle.ref_id
```

### §7.2 与 IntentEvent（认知边界）

| Plan 转换 | 触发 IntentEvent | 来源 |
|:--|:--|:--|
| DRAFT 创建 | open new IntentEvent(reason=PLAN_PHASE_CHANGE)（如未在 active）| PlanRegistry.draft |
| APPROVED → EXECUTING | open new IntentEvent(reason=PLAN_PHASE_CHANGE)；解除阻塞 | PlanRegistry.start_executing |
| Step 完成（result 回流）| open new IntentEvent(reason=NANOBOT_RESULT_RETURN, related_plan_id=...) | PlanRegistry.report_step_result |
| COMPLETE / FAILED / CANCELLED | open new IntentEvent(reason=PLAN_PHASE_CHANGE) | PlanRegistry 状态变更 |

### §7.3 与 L2-B（镜像）

```python
# Plan 在 L2-B 镜像（reuse NodeKind.EVENT，不新增 enum — Phase 4 §8 L1 锁不动）
plan_root_node = SemanticNode(
    kind=NodeKind.EVENT,
    label=plan.title,
    description=plan.rationale,
    confirmation=ConfirmationStatus.CONFIRMED,
    salience=Salience.FOREGROUND,
    event_id=plan.intent_event_id,
    source="goslo_autonomous",   # 或 "user_explicit" 取决触发
    source_meta={
        "plan_role": "plan_root",
        "plan_id": plan.plan_id,
        "plan_state": plan.state.value,
    },
    time_span=(plan.drafted_at, plan.completed_at if plan.state == PlanState.COMPLETE else None),
)

# 每个 PlanStep 也镜像为 EVENT 节点
for step in plan.steps:
    step_node = SemanticNode(
        kind=NodeKind.EVENT,
        label=step.title,
        description=step.description,
        event_id=plan.intent_event_id,
        source_meta={
            "plan_role": "plan_step",
            "plan_id": plan.plan_id,
            "step_id": step.step_id,
            "depends_on": list(step.depends_on),
        },
    )

# 边：Plan root → PlanStep（reuse PART_OF_EPISODE，不新增 EdgeKind）
```

→ 关键：**reuse `NodeKind.EVENT` + `source_meta.plan_role`** — 不动 Phase 4 §8 L1（NodeKind / EdgeKind enum）。

### §7.4 与 NanobotTask

```python
# PlanStep → NanobotTask 派发
async def dispatch_step(plan: Plan, step: PlanStep) -> str:
    task_id = await do_dispatch_task(
        task_type=step.expected_tool,   # "summarize" / "research" / "remind" / ...
        params={
            **step.inputs,
            "plan_id": plan.plan_id,
            "step_id": step.step_id,
            "result_channel": CH_NANOBOT_RESULTS,
        },
        priority="normal",
    )
    step.nanobot_task_id = task_id
    step.state = PlanStepState.DISPATCHED
    return task_id

# NanobotTask 完成 result 回流 → PlanRegistry.report_step_result
# 已在 dsg/triggers/runner.py _event_loop 监听 CH_NANOBOT_RESULTS
```

### §7.5 与 Archive

```python
# Plan COMPLETE / FAILED / CANCELLED 后：
# - Plan 元数据进 plans.jsonl（archive Phase 2 序列化）
# - PlanBlackboard 数据 dump 到 plans.jsonl
# - Step results（result_ref_id）保留在 IntentWorkspace 直到 IntentEvent close
# - Plan 自身的 staged_ref_id 在 Plan COMPLETE 时主动 evict（不依赖 IntentEvent close）
```

详见 [`dsg_protocol_archive_v1_20260506.md §4.2 plans.jsonl`](dsg_protocol_archive_v1_20260506.md)。

---

## §8 Wire 升级接口锚点（**P3，本 chat 不做**）

**用户在 Unity 确认 Plan 的协议**（待新 ADR）：

```python
# 新 EcpEventType 候选（本 chat 不动 wire！）
class EcpEventType:
    # ... 既有 ...
    PLAN_PROPOSED = "plan_proposed"            # Brain → Unity：渲染 Plan UI
    PLAN_REVISION_PROPOSED = "plan_revision"

# 新 EcpCommand 候选
class EcpCommand:
    # ... 既有 ...
    APPROVE_PLAN = "approve_plan"              # Unity → Brain：用户确认
    REJECT_PLAN = "reject_plan"
    CANCEL_PLAN = "cancel_plan"
    REVISE_PLAN_REQUEST = "revise_plan"
```

→ **本协议留接口**（PlanRegistry.submit_for_confirmation 时**写 obs_log 占位**），等 wire 升级 ADR 再连真路径。

**桌面 baseline 当前行为**（无 wire）：
- `submit_for_confirmation` → 仅写 obs_log + Timeline marker
- 自动 approve（GOSLO 自决，无用户审）— 测试期模式
- 真用户审 P3 接入 wire 后启用

---

## §9 协议合同 0 漂移核对

| 检查项 | 状态 |
|:--|:--|
| Phase 4 §8 L1（NodeKind / EdgeKind enum）| ✅ 不动 — Plan 镜像 reuse `NodeKind.EVENT` + `EdgeKind.PART_OF_EPISODE` |
| Phase 4 §8 L7（PhotoEvent 不自动建 ObjectNode）| ✅ Plan 不影响 PhotoEvent |
| Phase 4 §8 L11（identify_object 1.9s 预算）| ✅ Plan 异步派发，不影响 |
| ADR-L1.5-001 | ✅ Plan 镜像节点用 source_meta（已锁的扩展槽）|
| `parrot_behavior_rules §3.7` | ✅ Plan 不抓帧 / 不写 Graphiti / 不动 attention threshold |
| `tests/test_ecp_event/test_cs_parity.py` 4/4 | ✅ 不动 wire（PLAN_PROPOSED 等留 P3）|

---

## §10 测试覆盖

```python
# tests/test_brain/test_plan_lifecycle.py
def test_draft_creates_plan_with_id(): ...
def test_draft_stages_to_intent_workspace(): ...
def test_draft_creates_plan_blackboard_namespace(): ...
def test_legal_transition_draft_to_awaiting(): ...
def test_legal_transition_awaiting_to_approved(): ...
def test_legal_transition_approved_to_executing(): ...
def test_legal_transition_executing_to_complete(): ...
def test_illegal_transition_raises(): ...
def test_revise_creates_new_plan_supersedes_old(): ...
def test_cancel_terminal(): ...
def test_failed_can_revise(): ...

# tests/test_brain/test_plan_intent_workspace_binding.py
def test_plan_payload_in_intent_workspace(): ...
def test_plan_l2b_mirror_uses_event_kind(): ...
def test_plan_l2b_mirror_source_meta_plan_role(): ...
def test_plan_l2b_step_nodes_use_event_kind(): ...
def test_plan_l2b_root_to_step_edge_uses_part_of_episode(): ...
def test_plan_complete_evicts_staged_ref(): ...

# tests/test_brain/test_plan_to_nanobot_dispatch.py
def test_start_executing_dispatches_no_dep_steps(): ...
def test_step_dependency_holds_until_parent_done(): ...
def test_step_result_updates_plan_step_state(): ...
def test_all_steps_done_transitions_plan_complete(): ...
def test_step_failure_transitions_plan_failed(): ...

# tests/test_brain/test_plan_blackboard.py
def test_blackboard_namespace_isolated(): ...
def test_blackboard_set_get_delete(): ...
def test_blackboard_cleanup_on_plan_close(): ...

# tests/test_brain/test_plan_intent_event_alignment.py
def test_draft_opens_intent_event_phase_change(): ...
def test_executing_opens_intent_event_phase_change(): ...
def test_step_result_opens_intent_event_nanobot_result(): ...
def test_complete_opens_intent_event_phase_change(): ...
```

→ 共 **27 项新测试**。Wire 升级测试占位（P3 接 wire 后填）。

---

## §11 扩展点

| 扩展点 | 当前 baseline | P3+ 升级 |
|:--|:--|:--|
| Plan 制定 | GOSLO LLM 手写（Intent 阻塞期） | LangChain Plan-and-Execute / Tree-of-Thought 自动分解 |
| 用户确认 wire | 自动 approve（测试期）| EcpEvent + EcpCommand（wire ADR）|
| Step 依赖图 | DAG（无环）| 并行依赖 / 条件依赖 / pause-on-failure |
| Step 失败处理 | 标 FAILED | 自动重试 / fallback / GOSLO 决策修订 |
| 跨 Plan 引用 | 无 | Plan 间引用（结果传递）|
| Plan 模板 | 无 | 常用 Plan 模板库 |
| Plan UI 富文本格式 | obs_log 占位 | Mermaid / Gantt / 跳转按钮（wire ADR）|
| Plan 多模态状态汇报 | 文本 | 图片 / 视频 / mermaid（IntentWorkspace stage）|

---

## §12 引用

- 主设计稿：[`dsg_l1_5_pool_and_lifecycle_design_20260506.md`](dsg_l1_5_pool_and_lifecycle_design_20260506.md)
- L1.5 Pool 协议：[`dsg_protocol_pool_v1_20260506.md`](dsg_protocol_pool_v1_20260506.md)
- 触发器协议：[`dsg_protocol_trigger_v2_20260506.md`](dsg_protocol_trigger_v2_20260506.md)
- IntentEventBoundary 协议：[`dsg_protocol_intent_event_boundary_v1_20260506.md`](dsg_protocol_intent_event_boundary_v1_20260506.md)
- Archive 协议：[`dsg_protocol_archive_v1_20260506.md`](dsg_protocol_archive_v1_20260506.md)
- IntentWorkspace 协议：[`brain_protocol_intent_workspace_v1_20260506.md`](brain_protocol_intent_workspace_v1_20260506.md)
- 既有：`src/parrot/scheduler/blackboard.py`（py-trees Blackboard V2）
- 既有：`src/parrot/brain/tools/dispatch_task.py`
- 既有：`src/parrot/shared/constants.py`（CH_NANOBOT_RESULTS）

---

## §13 变更日志

- **2026-05-06**：本协议 V1 创建。Plan / PlanStep / PlanState 8 状态机 + PlanRegistry 完整 API + PlanBlackboard 子命名空间约定 + IntentWorkspace 主存约定 + L2-B 镜像 reuse `NodeKind.EVENT` + 与 IntentEvent / NanobotTask / Archive 衔接 + 27 项验证测试 + Wire 升级（用户确认）接口锚点（P3 ADR 接入）。
