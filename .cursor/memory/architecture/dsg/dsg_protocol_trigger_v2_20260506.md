---
status: draft
category: protocol-spec
protocol_id: DSG-TRIGGER-V2
status_note: "DSG 触发器协议 V2 — TriggerOutcome 替代 TriggerResult（alias 保留）+ 5 路上行通道 + 5 个新触发器。仅 Python 内部，不上 Unity wire。"
last_reviewed: 2026-05-06
ai_priority: high
ai_audience: "实施 chat / 触发器作者 / 独立审计 chat"
parent_doc: "dsg_l1_5_pool_and_lifecycle_design_20260506.md"
companion_protocols:
  - "dsg_protocol_pool_v1_20260506.md"
  - "dsg_protocol_intent_event_boundary_v1_20260506.md"
  - "dsg_protocol_archive_v1_20260506.md"
  - "brain_protocol_intent_workspace_v1_20260506.md"
  - "brain_protocol_plan_v1_20260506.md"
---

# DSG-TRIGGER-V2 — 触发器协议 V2

> **协议 ID**：DSG-TRIGGER-V2
> **范围**：`src/parrot/dsg/triggers/` 内 BaseTrigger / TriggerRunner / 5 个新触发器。
> **核心升级**：`TriggerResult` → `TriggerOutcome` + 新增 5 路上行通道。
> **不在范围**：上 Unity wire（违反 ADR-L1.5-001 Q1）/ Brain 直接读写 L2-B（违反 Ingest 唯一入口不变量）。

---

## §0 术语表（与主设计稿 §0 等同）

参见 [`dsg_l1_5_pool_and_lifecycle_design_20260506.md §0`](dsg_l1_5_pool_and_lifecycle_design_20260506.md)。

---

## §1 升级动机

### §1.1 既有 TriggerResult 的不足

```python
# 既有 src/parrot/dsg/triggers/base.py
@dataclass
class TriggerResult:
    trigger_name: str
    summary: str
    nodes_affected: list[str]
    dispatch_to_nanobot: bool
    nanobot_task: dict[str, Any] | None
    notify_gemini: bool
    notification_text: str
```

只有 2 路上行：
- `dispatch_to_nanobot` → Scheduler / Nanobot（Task 层异步）
- `notify_gemini` → Brain Context Injector（GOSLO 上报）

**缺口**（用户 2026-05-06 原话："潜意识协作面"）：
- 触发器**无法直接写池**（只能通过 Redis Pub/Sub 间接通知 trigger_listener）
- 触发器**无法管桶**（Obsidian 一键导入 / roleplay 切换无 API）
- 触发器**无法触发归档**（IdleArchiveTrigger 无落点）
- 触发器**无法 stage 大文件**（GosloCuriosityTrigger 找到 photo 后无处放）
- 触发器**无法提案 Plan**（GOSLO 主动好奇若值得做 Plan，无路径）

### §1.2 Plan-and-Execute 模式对触发器协议的要求

用户原话锚定的协作流程：
> 鹦鹉 Intent 阻塞对话安排 Plan，给用户 UnityApp 展示 Plan，用户确定后派发，然后鹦鹉就不阻塞了，可以对话，出现问题汇报。

→ 触发器是 **"出现问题汇报"** 的入口（NanobotTask 完成 / 失败 → trigger fire → Brain 重新进 Intent）。
→ 触发器需要能**提案 Plan**（GosloCuriosity 发现需要做长任务时）。
→ 触发器需要能**stage 大文件到 IntentWorkspace**（让 GOSLO Intent 层用）。

---

## §2 TriggerOutcome（升级版，alias 兼容 TriggerResult）

```python
@dataclass
class TriggerOutcome:
    """触发器统一输出。
    
    向后兼容：TriggerResult = TriggerOutcome（alias 保留），既有 4 个触发器零改动。
    新增 5 路上行通道（commit_observations / bucket_ops / archive_request / staged_refs / plan_request）
    给新触发器用。
    """
    # ─── 既有保留 ───
    trigger_name: str = ""
    summary: str = ""
    nodes_affected: list[str] = field(default_factory=list)
    dispatch_to_nanobot: bool = False
    nanobot_task: dict[str, Any] | None = None
    notify_gemini: bool = False
    notification_text: str = ""
    
    # ─── 新增 5 路上行通道（DSG-TRIGGER-V2，2026-05-06）───
    commit_observations: tuple["Observation", ...] = ()
    """走 IngestRunner 进 L1.5 池 — admit() → AdmitOutcome
    
    用例：
      - SsotEnrichmentTrigger 发现 Obsidian 节点 → 转 Observation 入池
      - GosloCuriosityTrigger 找到 unknown 物体 → GOSLO_AUTONOMOUS Observation 入池
      - SceneContextTrigger 检测到场景物体 → Observation
    
    不变量：仍走 IngestRunner（Ingest 是唯一 L2-B 写入门）。
    """
    
    bucket_ops: tuple["BucketOp", ...] = ()
    """走 L15Pool.apply_bucket_op — BucketOpResult
    
    用例：
      - SceneSwitchTrigger → freeze 永久权威桶 + clear fresh 桶
      - RoleplayModeTrigger → register / clear ROLEPLAY_TEMP 桶
      - 一键 import Google 日程 → BucketOp(IMPORT, GOOGLE_CALENDAR, items=[...])
    
    Schema：参见 dsg_protocol_pool_v1 §2.2
    """
    
    archive_request: "ArchiveRequest | None" = None
    """走 ConversationArchive.enqueue — 触发对话快照序列化或入归档队列
    
    用例：
      - IdleArchiveTrigger 检测 nanobot heartbeat idle ≥ N min → 触发 idle archive flow
      - SceneSwitchTrigger 切换前 → snapshot 当前 scene
      - Episode close trigger → enqueue_for_idle_archive
    
    Schema：参见 dsg_protocol_archive_v1 §3
    """
    
    staged_refs: tuple["StagedRefRequest", ...] = ()
    """走 IntentWorkspace.stage — RefHandle
    
    用例：
      - GosloCuriosityTrigger 发现 photo → stage(PHOTO) 给 GOSLO 看
      - NanobotResult trigger 接收富文本汇报 → stage(RICH_REPORT)
      - SsotEnrichmentTrigger 找到 Obsidian doc → stage(DOC)
    
    Schema：参见 brain_protocol_intent_workspace_v1 §3
    """
    
    plan_request: "PlanProposal | None" = None
    """走 PlanRegistry.draft — Plan(state=DRAFT)
    
    用例：
      - GosloCuriosityTrigger 发现需要做长任务（多步研究 / 多次查询）→ 提案 Plan
      - NanobotResult trigger 接收"任务失败需重试" → 提案修订版 Plan
    
    Schema：参见 brain_protocol_plan_v1 §3
    """
```

### §2.1 向后兼容承诺

```python
# 既有代码保持工作（既有 4 个触发器零改动）
TriggerResult = TriggerOutcome   # alias
```

既有触发器（calendar / message / scene_context / ssot_enrichment）当前只用旧 7 个字段；**升级时机**：
- `ssot_enrichment_trigger` 立即升级（用 `commit_observations` 替代既有 Redis Pub/Sub 间接路径）
- 其他既有 3 个**本 chat 不动**（保持 7 字段使用模式）

---

## §3 BucketOp / ArchiveRequest / StagedRefRequest / PlanProposal Schema

### §3.1 BucketOp

```python
class BucketOpKind(str, Enum):
    REGISTER = "register"
    IMPORT = "import"
    FREEZE = "freeze"
    UNFREEZE = "unfreeze"
    CLEAR = "clear"
    UNREGISTER = "unregister"

@dataclass(frozen=True)
class BucketOp:
    op: BucketOpKind
    kind: "BucketKind"
    payload: dict[str, Any] = field(default_factory=dict)
    # IMPORT: payload={items: list[Observation]}
    # REGISTER: payload={spec: BucketSpec}
    # 其他: payload={}

@dataclass(frozen=True)
class BucketOpResult:
    op: BucketOp
    success: bool
    bucket_handle: "BucketHandle | None" = None
    affected_nodes: int = 0
    error: str = ""
```

### §3.2 ArchiveRequest

```python
class ArchiveRequestKind(str, Enum):
    SERIALIZE_NOW = "serialize_now"              # 立即序列化（Scene switch / Episode close 前）
    ENQUEUE_FOR_IDLE = "enqueue_for_idle"        # 入闲时归档队列（IdleArchiveTrigger）
    SCAN_AND_ARCHIVE = "scan_and_archive"        # nanobot 闲时被唤醒：扫硬盘队列 → 写 Graphiti

@dataclass(frozen=True)
class ArchiveRequest:
    kind: ArchiveRequestKind
    target: ArchiveTarget                         # CONVERSATION / EPISODE / SCENE / PLAN
    target_id: str
    metadata: dict[str, Any] = field(default_factory=dict)

class ArchiveTarget(str, Enum):
    CONVERSATION = "conversation"
    EPISODE = "episode"
    SCENE_SNAPSHOT = "scene_snapshot"
    PLAN = "plan"
```

详见 [`dsg_protocol_archive_v1_20260506.md`](dsg_protocol_archive_v1_20260506.md) §3。

### §3.3 StagedRefRequest

```python
@dataclass(frozen=True)
class StagedRefRequest:
    kind: "StagedRefKind"
    payload_source: PayloadSource
    metadata: dict[str, Any] = field(default_factory=dict)
    auto_evict_on_intent_close: bool = True
    auto_evict_after_seconds: float | None = None    # None = 跟随 IntentEvent
    expected_node_uuid: str = ""                     # 若与某节点关联，绑定 RefTable
    expected_intent_event_id: str = ""

class PayloadSource(str, Enum):
    DISK_PATH = "disk_path"                          # payload = path string
    INLINE_BYTES = "inline_bytes"                    # payload = bytes
    INLINE_TEXT = "inline_text"                      # payload = str
    URL = "url"                                       # payload = url string (lazy fetch)
```

详见 [`brain_protocol_intent_workspace_v1_20260506.md`](brain_protocol_intent_workspace_v1_20260506.md) §3。

### §3.4 PlanProposal

```python
@dataclass(frozen=True)
class PlanProposal:
    """触发器向 GOSLO 提案 Plan；GOSLO 评估后决定是否真做 PlanRegistry.draft。"""
    proposed_by: str                                  # trigger_name
    title: str
    rationale: str                                    # 为什么需要 Plan
    suggested_steps: tuple[PlanStepProposal, ...]
    suggested_intent_event_kind: str = ""
    related_node_uuids: tuple[str, ...] = ()
    related_staged_ref_ids: tuple[str, ...] = ()
    estimated_duration_s: float = 0.0
    blocks_conversation: bool = False                  # 阻塞对话 = Intent 层

@dataclass(frozen=True)
class PlanStepProposal:
    step_id: str                                      # 提案者临时 ID（GOSLO 起 Plan 时可重赋值）
    title: str
    expected_tool: str = ""                            # 哪个 Brain function tool / NanobotTask 类型
    inputs: dict[str, Any] = field(default_factory=dict)
    depends_on: tuple[str, ...] = ()                   # step_id 依赖
```

详见 [`brain_protocol_plan_v1_20260506.md`](brain_protocol_plan_v1_20260506.md) §3。

---

## §4 TriggerRunner._process_result 升级

```python
class TriggerRunner:
    async def _process_result(self, outcome: TriggerOutcome) -> None:
        """处理 TriggerOutcome 的所有上行通道。
        
        顺序（避免相互依赖死锁）：
          1. bucket_ops             先管桶（影响 admit 路由）
          2. commit_observations    再入池
          3. staged_refs            stage 大文件
          4. archive_request        入归档队列
          5. plan_request           draft Plan
          6. dispatch_to_nanobot    既有，触发异步任务
          7. notify_gemini          既有，上报 Brain
        
        每路独立 try/except；任意一路失败不阻塞其他路（log + 继续）。
        """
        log_trigger_outcome(outcome)
        
        # ─── 1. bucket_ops ───
        for op in outcome.bucket_ops:
            try:
                result = await get_l1_5_pool().apply_bucket_op(op)
                if not result.success:
                    logger.warning("bucket_op failed: %s — %s", op, result.error)
            except Exception:
                logger.exception("bucket_op dispatch failed: %s", op)
        
        # ─── 2. commit_observations ───
        if outcome.commit_observations:
            try:
                runner = get_ingest_runner()
                for obs in outcome.commit_observations:
                    await runner.commit_observation(obs)
            except Exception:
                logger.exception("commit_observations dispatch failed")
        
        # ─── 3. staged_refs ───
        if outcome.staged_refs:
            try:
                ws = get_intent_workspace()
                for req in outcome.staged_refs:
                    await ws.stage(req)
            except Exception:
                logger.exception("staged_refs dispatch failed")
        
        # ─── 4. archive_request ───
        if outcome.archive_request:
            try:
                await dispatch_archive_request(outcome.archive_request)
            except Exception:
                logger.exception("archive_request dispatch failed")
        
        # ─── 5. plan_request ───
        if outcome.plan_request:
            try:
                registry = get_plan_registry()
                await registry.draft(outcome.plan_request)
            except Exception:
                logger.exception("plan_request dispatch failed")
        
        # ─── 6. dispatch_to_nanobot（既有保留）───
        if outcome.dispatch_to_nanobot and outcome.nanobot_task:
            await self._dispatch_nanobot(outcome.nanobot_task)
        
        # ─── 7. notify_gemini（既有保留）───
        if outcome.notify_gemini and outcome.notification_text and self._session:
            try:
                await self._session.generate_reply(instructions=outcome.notification_text)
            except Exception:
                logger.debug("notify_gemini failed for %s", outcome.trigger_name)
```

---

## §5 5 个新触发器

### §5.1 SceneSwitchTrigger（ON_DEMAND）

```python
class SceneSwitchTrigger(BaseTrigger):
    """触发：set_scene tool 调用 → switch SceneType。
    
    输出：
      - bucket_ops:
          - FREEZE OBSIDIAN_SETTING_DAILY  (preserved across SceneType)
          - FREEZE OBSIDIAN_SETTING_ROLEPLAY (preserved if active)
          - CLEAR GOOGLE_CALENDAR  (fresh on switch)
          - CLEAR AUTONOMOUS_CURIOSITY  (fresh on switch — 短 TTL 自然清)
      - archive_request: SERIALIZE_NOW(SCENE_SNAPSHOT, scene_id=old_scene)
      - notify_gemini: "切换到 {new_scene_id} 场景了"
    """
    name = "scene_switch_trigger"
    kinds = [TriggerKind.ON_DEMAND]
    
    async def on_event(self, event: dict) -> TriggerOutcome | None:
        if event.get("kind") != "scene_switch":
            return None
        # 实现细节见 dsg_protocol_scene_snapshot_v1
        ...
```

### §5.2 IntentEventBoundaryTrigger（EVENT_DRIVEN）

```python
class IntentEventBoundaryTrigger(BaseTrigger):
    """触发：tool call boundary / nanobot result return / long idle / explicit。
    
    输出：
      - 调 IntentEventBoundaryHandler.on_new_event(reason, src_node_uuids)
      - 旧 event 节点降权（attention *= decay_factor，桌面默认 0.7）
      - bucket_ops: 无（不动桶）
      - 不发 commit_observations / staged_refs（这是边界标注，不入池）
      - notify_gemini=False（潜意识层；除非 reason=EXPLICIT_REPORT_BACK）
    """
    name = "intent_event_boundary_trigger"
    kinds = [TriggerKind.EVENT_DRIVEN]
    
    async def on_event(self, event: dict) -> TriggerOutcome | None:
        if event.get("kind") not in ("tool_call_start", "nanobot_result", "long_idle", "intent_explicit"):
            return None
        ...
```

详见 [`dsg_protocol_intent_event_boundary_v1_20260506.md`](dsg_protocol_intent_event_boundary_v1_20260506.md)。

### §5.3 RoleplayModeTrigger（ON_DEMAND）

```python
class RoleplayModeTrigger(BaseTrigger):
    """触发：用户切换 roleplay 模式（set_mode tool 或显式信号）。
    
    输出（开 roleplay）：
      - bucket_ops: REGISTER OBSIDIAN_SETTING_ROLEPLAY + IMPORT roleplay 设定 items
    输出（关 roleplay）：
      - bucket_ops: CLEAR ROLEPLAY_TEMP + UNREGISTER OBSIDIAN_SETTING_ROLEPLAY
      - archive_request: SERIALIZE_NOW(roleplay snapshot 留档)
    """
    name = "roleplay_mode_trigger"
    kinds = [TriggerKind.ON_DEMAND]
    ...
```

### §5.4 GosloCuriosityTrigger（EVENT_DRIVEN）

```python
class GosloCuriosityTrigger(BaseTrigger):
    """触发：dsg/attention/threshold.py 检测到 unknown object + GOSLO 意图允许主动好奇。
    
    输出：
      - commit_observations: GOSLO_AUTONOMOUS Observation × 1
      - staged_refs: stage(PHOTO) 当前帧给 GOSLO Intent 层用（如配 photo）
      - plan_request: 若评估需要 Plan（如多步研究）→ PlanProposal
      - notify_gemini: 短文本提示（"看到了一个 chair 不认识"）
    
    边界（master §3.3 / parrot_behavior_rules §3.7）：
      - 不直接调 identify_object（GOSLO 自主决策走不走 Intent 层）
      - 不直接写 Graphiti（走 archive 管线）
      - 不阻塞对话（除非 PlanProposal.blocks_conversation=True 且 GOSLO 接受）
    """
    name = "goslo_curiosity_trigger"
    kinds = [TriggerKind.EVENT_DRIVEN]
    interval_seconds = 0  # event-driven, no period
    ...
```

### §5.5 IdleArchiveTrigger（PERIODIC）

```python
class IdleArchiveTrigger(BaseTrigger):
    """触发：周期检查 nanobot heartbeat 是否 idle ≥ N min。
    
    Idle 判定：Redis HASH parrot:nanobot_heartbeat 最后心跳 > N min 前
    + Brain agent 当前不在 Intent 层（无 active IntentEvent）。
    
    输出：
      - archive_request: SCAN_AND_ARCHIVE(CONVERSATION, conv_id=*)
        — 扫 data/conversations/ 下所有 unprocessed 目录
        — 触发 nanobot 唤醒去做 unified_filter + LLM → Graphiti
    """
    name = "idle_archive_trigger"
    kinds = [TriggerKind.PERIODIC]
    interval_seconds = 600.0  # 桌面 baseline 10min；策略可调
    ...
```

---

## §6 协议合同 0 漂移核对

| 检查项 | 状态 |
|:--|:--|
| Phase 4 §8 L1（NodeKind / EdgeKind enum）| ✅ 不动 |
| Phase 4 §8 L9（attention threshold）| ✅ 不动 — 触发器仅读 BB hint，不动数值 |
| ADR-L1.5-001 §2.1 Q1（source 仅 Python）| ✅ TriggerOutcome 全 Python 内部 |
| ADR-L1.5-001 §2.2 Q2（meta+factory hybrid）| ✅ 不动 SemanticNode；commit_observations 走 IngestRunner 既有路径 |
| `parrot_behavior_rules §3.7` Observer-Attention 边界 | ✅ 触发器不抓帧 / 不写 Graphiti / 不直接动 attention 字段 |
| `tests/test_ecp_event/test_cs_parity.py` 4/4 | ✅ 不动 EcpEventType / EcpEventSource / topic |
| 测试基线 234/234 + ADR-L1.5-001 11 项 | ✅ 既有 4 个触发器零改动（仅 ssot_enrichment 升级，含旧 7 字段） |

---

## §7 测试覆盖

```python
# tests/test_dsg/test_trigger_outcome_v2_5_channels.py
def test_trigger_outcome_alias_back_compat(): ...
def test_outcome_with_no_new_channels_runs_legacy_path(): ...
def test_bucket_ops_dispatched_in_order(): ...
def test_commit_observations_routed_to_ingest_runner(): ...
def test_staged_refs_routed_to_intent_workspace(): ...
def test_archive_request_routed_to_archive_module(): ...
def test_plan_request_routed_to_plan_registry(): ...
def test_one_channel_failure_does_not_block_others(): ...
def test_processing_order_bucket_ops_before_commit(): ...

# tests/test_dsg/test_scene_switch_trigger.py
def test_scene_switch_freezes_authority_buckets(): ...
def test_scene_switch_clears_fresh_buckets(): ...
def test_scene_switch_serializes_old_snapshot(): ...

# tests/test_dsg/test_intent_event_boundary_trigger.py
def test_intent_event_open_marks_timeline(): ...
def test_intent_event_close_decays_old_nodes(): ...
def test_intent_event_does_not_emit_observations(): ...

# tests/test_dsg/test_roleplay_mode_trigger.py
def test_roleplay_open_registers_temp_bucket(): ...
def test_roleplay_close_clears_temp_bucket(): ...

# tests/test_dsg/test_goslo_curiosity_trigger.py
def test_curiosity_emits_goslo_autonomous_observation(): ...
def test_curiosity_stages_photo_to_intent_workspace(): ...
def test_curiosity_proposes_plan_when_long_task(): ...
def test_curiosity_short_ttl_in_autonomous_bucket(): ...

# tests/test_dsg/test_idle_archive_trigger.py
def test_idle_detection_via_nanobot_heartbeat(): ...
def test_idle_skipped_when_intent_active(): ...
def test_archive_request_scans_disk_queue(): ...
```

→ 共 **20 项新测试**（既有 ~10 项触发器测试不动）。

---

## §8 扩展点

| 扩展点 | 当前 | P3+ 升级方向 |
|:--|:--|:--|
| 新触发器类型 | 9 个（既有 4 + 新 5） | 任意 add — 接口稳定 |
| TriggerOutcome 路 | 7 路（既有 2 + 新 5） | 加路需新协议版本 V3 + alias 保留 |
| GosloCuriosityTrigger 触发条件 | attention threshold + DSG event | 加更细粒度（语义新颖度 / 用户兴趣 / 对话上下文）|
| IdleArchiveTrigger idle 判定 | nanobot heartbeat | 加 Brain CPU / Mem 压力 / 用户活跃度 |
| Plan 提案智能 | 触发器手工填 | LLM 评估"这个 trigger 是否值得 Plan" |

---

## §9 引用

- 主设计稿：[`dsg_l1_5_pool_and_lifecycle_design_20260506.md`](dsg_l1_5_pool_and_lifecycle_design_20260506.md)
- Pool 协议：[`dsg_protocol_pool_v1_20260506.md`](dsg_protocol_pool_v1_20260506.md)
- IntentEventBoundary 协议：[`dsg_protocol_intent_event_boundary_v1_20260506.md`](dsg_protocol_intent_event_boundary_v1_20260506.md)
- Archive 协议：[`dsg_protocol_archive_v1_20260506.md`](dsg_protocol_archive_v1_20260506.md)
- IntentWorkspace 协议：[`brain_protocol_intent_workspace_v1_20260506.md`](brain_protocol_intent_workspace_v1_20260506.md)
- Plan 协议：[`brain_protocol_plan_v1_20260506.md`](brain_protocol_plan_v1_20260506.md)
- 既有触发器代码：`src/parrot/dsg/triggers/{base,runner,calendar,message,scene_context,ssot_enrichment}_trigger.py`

---

## §10 变更日志

- **2026-05-06**：本协议 V2 创建。TriggerOutcome 替代 TriggerResult（alias 保留）+ 5 路上行通道 + 5 个新触发器接口骨架 + 20 项验证测试。既有 4 个触发器零改动。
