---
status: draft
category: protocol-spec
protocol_id: DSG-ARCHIVE-V1
status_note: "工作记忆延迟归档协议 V1 — 三阶段管线（对话期间不写 Graphiti / 对话结束序列化 / nanobot 闲时归档）+ ConversationBoundaryDetector 多信号 OR + 与 l2b_graph.start_episode 立即 archive 的冲突解决方案。"
last_reviewed: 2026-05-06
ai_priority: high
ai_audience: "实施 chat / nanobot 协作 chat / P3 MemoryValidity 实施 chat / 独立审计 chat"
parent_doc: "dsg_l1_5_pool_and_lifecycle_design_20260506.md"
companion_protocols:
  - "dsg_protocol_pool_v1_20260506.md"
  - "dsg_protocol_trigger_v2_20260506.md"
  - "brain_protocol_intent_workspace_v1_20260506.md"
  - "brain_protocol_plan_v1_20260506.md"
---

# DSG-ARCHIVE-V1 — 工作记忆延迟归档协议

> **协议 ID**：DSG-ARCHIVE-V1
> **范围**：`src/parrot/dsg/archive/` 子包 + `dsg/triggers/idle_archive_trigger.py` + `dsg.l2b_graph.start_episode` 改动。
> **核心约束**（master §5 ratified）：对话期间**不写 Graphiti**；对话结束序列化到硬盘；nanobot 闲时统一过滤 + LLM → Graphiti。
> **不在范围**：MemoryValidity 具体 Ebbinghaus 衰减公式（P3）/ unified_filter LLM prompt 设计（接口预留，实现 P3）。

---

## §0 术语表

参见 [主设计稿 §0](dsg_l1_5_pool_and_lifecycle_design_20260506.md)。本协议关注：
- `Episode`（对话段）
- `IntentEvent`（认知边界）
- `Plan`（计划）
- `Conversation`（**新概念**）= 一次完整的对话流程。1+ Episode；通常 1 Conversation = 1 session。

---

## §1 三阶段管线

### §1.1 总图

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: 对话期间 (Hot Path)                                  │
│   - L2-B 工作记忆图（节点 + 边 + Compartment view）            │
│   - InMemorySnapshot（L1.5 Pool 元数据）                      │
│   - RefTable（L1.5 轻量绑定）                                  │
│   - Timeline（L1.5 Append-only marker 列表）                  │
│   - IntentWorkspace（Brain 大文件暂存）                        │
│   - PlanRegistry / PlanBlackboard（Brain Plan 状态）           │
│   ★ 不写 Graphiti                                              │
│   ★ episode close 不立即 archive — 改 enqueue                │
└─────────────────────┬────────────────────────────────────────┘
                      │ ConversationBoundaryDetector 触发（§2）
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: 对话结束 (Cold Storage)                              │
│   ConversationArchive.serialize(conv_id)                      │
│   → data/conversations/{conv_id}/                             │
│       ├── snapshot.json                  L2-B 节点 / 边快照    │
│       ├── refs.jsonl                     RefTable             │
│       ├── timeline.jsonl                 Timeline marker 序列  │
│       ├── episodes.jsonl                 EpisodeMarker 列表    │
│       ├── intent_events.jsonl            IntentEvent 状态序列  │
│       ├── plans.jsonl                    Plan / PlanStep 状态  │
│       └── intent_workspace_refs.jsonl    StagedRef 元数据      │
│   ★ 写入硬盘队列（archived_to_graphiti=False 标记）             │
└─────────────────────┬────────────────────────────────────────┘
                      │ IdleArchiveTrigger PERIODIC 检查
                      │（nanobot heartbeat idle ≥ N min）
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: 归档 (Archive Flow)                                  │
│   nanobot 唤醒 → 扫 data/conversations/                       │
│   → unified_filter（含 MemoryValidity 占位接口，P3 实施）       │
│      + LLM 蒸馏（提取 Episodic 关键事件 + Semantic 实体属性）   │
│   → Graphiti.add_episode(per Episode batch)                   │
│   → 标记 archived_to_graphiti=True                             │
└─────────────────────────────────────────────────────────────┘
```

### §1.2 关键不变量

1. Phase 1 期间 **`l2b_graph.start_episode()` 不创建 archive task**（与既有代码冲突，§5 解决）
2. Phase 1 期间 **`runner.commit_observation` 不写回 Graphiti**（与既有 TODO(S4.B) 冲突，§5 解决）
3. Phase 2 序列化是**纯写盘**（不调 Graphiti / 不调 nanobot）
4. Phase 3 归档由**nanobot worker 主动**（不阻塞 Brain agent）

---

## §2 ConversationBoundaryDetector

### §2.1 触发信号（多信号 OR — master §5 + Q-D 已锁）

```python
class ConversationBoundary(str, Enum):
    AGENT_DISCONNECT = "agent_disconnect"
    """Brain agent 关闭（disconnect 钩子触发）"""
    
    EPISODE_CLOSE = "episode_close"
    """manage_episode tool close 调用"""
    
    LONG_IDLE = "long_idle"
    """app 长时无活动（默认 30 min；策略可调）"""
    
    EXPLICIT_END = "explicit_end"
    """Unity 显式信号 / set_scene 切换 / 用户显式"""

@dataclass(frozen=True)
class ConversationBoundaryEvent:
    boundary: ConversationBoundary
    conv_id: str                         # 当前 conversation id
    triggered_at: float
    triggering_actor: str = ""           # "agent" / "tool:manage_episode" / ...
    metadata: dict[str, Any] = field(default_factory=dict)
```

### §2.2 ConversationBoundaryDetector 接口

```python
class ConversationBoundaryDetector:
    """监听多路信号，检测对话边界 → 触发 ConversationArchive.serialize"""

    async def start(self) -> None:
        """启动 — Brain agent 启动时调"""

    async def stop(self) -> None:
        """关闭 — agent disconnect 调"""

    def register_listener(
        self,
        boundary: ConversationBoundary,
        listener: Callable[[ConversationBoundaryEvent], Awaitable[None]],
    ) -> None: ...

    async def signal_boundary(self, event: ConversationBoundaryEvent) -> None:
        """显式信号入口（Brain tool / Unity 调用）"""

    def current_conv_id(self) -> str:
        """当前 conversation id；启动时生成 conv_{int(now)}_{hex[:4]}"""

    def configure_idle_threshold(self, seconds: float) -> None:
        """配置 LONG_IDLE 阈值（默认 30 min）"""
```

### §2.3 四种信号源接入

| 信号 | 接入点 | 调用 |
|:--|:--|:--|
| `AGENT_DISCONNECT` | `parrot.brain.agent.on_disconnect` 钩子 | `detector.signal_boundary(AGENT_DISCONNECT)` |
| `EPISODE_CLOSE` | `parrot.brain.tools.manage_episode.do_close()` | 同上 |
| `LONG_IDLE` | 后台 task — 监听 L1.5 Timeline / Brain 工作活动 | 同上 |
| `EXPLICIT_END` | Brain tool / Unity DataChannel 信号 | 同上 |

→ 一旦任一信号触发，立即调 `ConversationArchive.serialize(conv_id)`，写盘 + enqueue idle archive。

---

## §3 ArchiveRequest 协议（触发器上行通道）

```python
class ArchiveRequestKind(str, Enum):
    SERIALIZE_NOW = "serialize_now"
    """立即序列化（Scene 切换前 / Episode close 前 / 显式）"""
    
    ENQUEUE_FOR_IDLE = "enqueue_for_idle"
    """入闲时归档队列 — 等 nanobot idle 时扫描"""
    
    SCAN_AND_ARCHIVE = "scan_and_archive"
    """nanobot 闲时被唤醒：扫 data/conversations/ → unified_filter + LLM → Graphiti"""

class ArchiveTarget(str, Enum):
    CONVERSATION = "conversation"
    EPISODE = "episode"
    SCENE_SNAPSHOT = "scene_snapshot"
    PLAN = "plan"

@dataclass(frozen=True)
class ArchiveRequest:
    kind: ArchiveRequestKind
    target: ArchiveTarget
    target_id: str                       # conv_id / episode_id / scene_id / plan_id
    metadata: dict[str, Any] = field(default_factory=dict)
```

**用途**：
- `SceneSwitchTrigger` → `ArchiveRequest(SERIALIZE_NOW, SCENE_SNAPSHOT, scene_id)`
- `RoleplayModeTrigger` close → `ArchiveRequest(SERIALIZE_NOW, SCENE_SNAPSHOT, "roleplay_temp")`
- 默认 episode close（既有）→ `ArchiveRequest(ENQUEUE_FOR_IDLE, EPISODE, episode_id)`
- `IdleArchiveTrigger` → `ArchiveRequest(SCAN_AND_ARCHIVE, CONVERSATION, "*")`

---

## §4 ConversationArchive

### §4.1 接口

```python
class ConversationArchive:
    """对话快照序列化 + 闲时归档队列管理。"""

    def __init__(self, base_path: Path = Path("data/conversations")):
        self._base = base_path

    async def serialize(self, conv_id: str) -> ArchivePath:
        """Phase 2 — 写盘。
        
        步骤：
          1. 创建 data/conversations/{conv_id}/ 目录
          2. 从 L2BGraph + L15Pool + IntentWorkspace + PlanRegistry 拉数据
          3. 序列化各 jsonl 文件
          4. 写 metadata.json（含 archived_to_graphiti=False / created_at / sources）
          5. 返回 ArchivePath（含目录路径 + 文件清单）
        
        不变量：
          - 纯写盘，不调 Graphiti
          - 幂等（同 conv_id 重复 serialize → 覆盖；新生成的事件并入）
        """

    async def enqueue_for_idle_archive(
        self, target: ArchiveTarget, target_id: str
    ) -> None:
        """加入闲时归档队列（写 archive_queue.jsonl）"""

    def list_pending(self) -> list[PendingArchive]:
        """列出待归档（archived_to_graphiti=False）"""

    async def archive_to_graphiti(
        self, archive_path: ArchivePath
    ) -> ArchiveOutcome:
        """Phase 3 — 写 Graphiti（nanobot 闲时调）。
        
        步骤：
          1. 读取 conv_id 目录 jsonl
          2. 调 unified_filter（MemoryValidity 占位接口，P3 实施）
          3. 调 LLM 蒸馏 — 按 Episode 分批
          4. Graphiti.add_episode（per Episode batch，partition=goslo）
          5. 标记 archived_to_graphiti=True（写 metadata.json）
          6. 返回 ArchiveOutcome（成功 / 失败 / 跳过条目数）
        """


@dataclass(frozen=True)
class ArchivePath:
    conv_id: str
    base_dir: Path
    files: dict[str, Path]               # "snapshot": .../snapshot.json, ...

@dataclass(frozen=True)
class PendingArchive:
    archive_path: ArchivePath
    target: ArchiveTarget
    target_id: str
    created_at: float
    archived_to_graphiti: bool = False

@dataclass(frozen=True)
class ArchiveOutcome:
    success: bool
    archived_episodes: int
    archived_intent_events: int
    archived_plans: int
    skipped_by_filter: int
    error: str = ""
```

### §4.2 序列化 schema（jsonl 文件示例）

#### `snapshot.json`
```json
{
  "schema_version": 1,
  "conv_id": "conv_20260506_1840_a7c3",
  "captured_at": 1746543600.0,
  "node_count": 42,
  "edge_count": 67,
  "compartments": {
    "main": [...uuid list...],
    "obsidian_setting_daily": [...],
    "google_calendar": [...]
  },
  "current_scene_type": "desktop",
  "current_intent_event_id": "ev_..."
}
```

#### `refs.jsonl`（L1.5 RefTable）
```json
{"node_uuid": "n_...", "kind": "graphiti_uuid", "ref_value": "g_...", "bound_at": ..., "intent_workspace_ref_id": ""}
{"node_uuid": "n_...", "kind": "photo_path", "ref_value": "data/snapshots/objects/.../reference.jpg", ...}
```

#### `timeline.jsonl`
```json
{"marker_id": "...", "kind": "episode_start", "ts": ..., "payload": {"episode_id": "ep_..."}}
{"marker_id": "...", "kind": "intent_event_open", "ts": ..., "payload": {"event_id": "ev_...", "reason": "tool_call_boundary"}}
{"marker_id": "...", "kind": "plan_drafted", "ts": ..., "payload": {"plan_id": "pl_...", "title": "..."}}
{"marker_id": "...", "kind": "nanobot_dispatched", "ts": ..., "payload": {"task_id": "..."}}
```

#### `episodes.jsonl`
```json
{"episode_id": "ep_...", "title": "...", "started_at": ..., "ended_at": ..., "summary": "...", "participating_node_uuids": [...]}
```

#### `intent_events.jsonl`
```json
{"event_id": "ev_...", "reason": "tool_call_boundary", "opened_at": ..., "closed_at": ..., "member_node_uuids": [...], "related_plan_id": ""}
```

#### `plans.jsonl`
```json
{"plan_id": "pl_...", "title": "...", "state": "DONE", "drafted_at": ..., "approved_at": ..., "completed_at": ..., "steps": [{"step_id": "...", "title": "...", "result_ref_id": "..."}]}
```

#### `intent_workspace_refs.jsonl`
```json
{"ref_id": "...", "kind": "photo", "metadata": {...}, "staged_at": ..., "evicted_at": ...}
```

→ **6 份 jsonl**，按需展开；schema_version=1，未来升级走 `schema_version: 2`。

---

## §5 与既有代码的冲突解决

### §5.1 `l2b_graph.start_episode()` 不再立即 archive

#### 既有实现
```python
def start_episode(self, title: str = "", trigger_source: str = "") -> EpisodeMarker:
    if self._current_episode_id:
        old_ep = self.close_current_episode()
        if old_ep:
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.archive_episode_to_graphiti(old_ep.episode_id))   # ★ 与新约束冲突
            except RuntimeError:
                pass
    ...
```

#### 改动后
```python
def start_episode(self, title: str = "", trigger_source: str = "") -> EpisodeMarker:
    if self._current_episode_id:
        old_ep = self.close_current_episode()
        if old_ep:
            # 不再立即 archive；交给闲时归档管线
            from parrot.dsg.archive.conversation import enqueue_episode_for_idle_archive
            try:
                # synchronous enqueue (写盘 jsonl)
                enqueue_episode_for_idle_archive(old_ep.episode_id)
            except Exception:
                logger.exception("L2B: enqueue_for_idle_archive failed")
    ...
```

→ `archive_episode_to_graphiti` **方法保留**（被 `ConversationArchive.archive_to_graphiti` 内部调用，仍是写 Graphiti 的真路径），但**不再被 `start_episode` 直接调用**。

### §5.2 `runner.commit_observation` TODO 注释更新

#### 既有
```python
# TODO(S4.B): write-back to Graphiti here for CONFIRMED nodes.
```

#### 改动后
```python
# DSG-ARCHIVE-V1 (2026-05-06): NEVER write-back to Graphiti here.
# CONFIRMED nodes flow through the three-phase delayed archive pipeline:
#   Phase 1 (this method): commit only to L2-B in-memory + L1.5 Pool metadata
#   Phase 2 (ConversationArchive.serialize): on conversation boundary, dump to disk
#   Phase 3 (nanobot idle): unified_filter + LLM → Graphiti
# Detail: dsg_protocol_archive_v1_20260506.md
```

---

## §6 协议合同 0 漂移核对

| 检查项 | 状态 |
|:--|:--|
| Phase 4 §8 L1（NodeKind / EdgeKind enum）| ✅ 不动 |
| Phase 4 §8 L7（PhotoEvent 不自动建 ObjectNode）| ✅ 归档侧不影响 PhotoEvent 路径 |
| Phase 4 §8 L11（identify_object 1.9s 预算）| ✅ 不动 — 归档异步 |
| ADR-L1.5-001 §2.1 Q1（source 仅 Python）| ✅ Archive 全 Python 内部 |
| `parrot_behavior_rules §3.7` | ✅ Archive 不抓帧 / 不直读 attention |
| `tests/test_ecp_event/test_cs_parity.py` 4/4 | ✅ 不动 wire |
| 测试基线 234/234 + ADR-L1.5-001 11 项 | ✅ 既有 archive_episode_to_graphiti 仍存在 + 既有测试不动 |

---

## §7 测试覆盖

```python
# tests/test_dsg/test_archive_three_phase.py
def test_phase1_commit_does_not_write_graphiti(): ...
def test_phase2_serialize_writes_jsonl_files(): ...
def test_phase2_serialize_idempotent_on_repeat(): ...
def test_phase3_archive_to_graphiti_marks_archived(): ...
def test_start_episode_no_longer_creates_archive_task(): ...
def test_start_episode_enqueues_for_idle_archive(): ...
def test_runner_commit_observation_never_writes_graphiti(): ...

# tests/test_dsg/test_conversation_boundary_detector.py
def test_boundary_signal_agent_disconnect(): ...
def test_boundary_signal_episode_close(): ...
def test_boundary_signal_long_idle(): ...
def test_boundary_signal_explicit_end(): ...
def test_multiple_signals_first_wins(): ...
def test_idle_threshold_configurable(): ...

# tests/test_dsg/test_archive_request_routing.py
def test_serialize_now_request_writes_immediately(): ...
def test_enqueue_for_idle_writes_queue_only(): ...
def test_scan_and_archive_consumes_pending(): ...

# tests/test_dsg/test_archive_jsonl_schema.py
def test_snapshot_schema_v1(): ...
def test_refs_jsonl_one_line_per_binding(): ...
def test_timeline_jsonl_chronological(): ...
def test_episodes_jsonl_includes_member_nodes(): ...
def test_intent_events_jsonl_includes_reason(): ...
def test_plans_jsonl_includes_steps(): ...
def test_intent_workspace_refs_jsonl_no_payload_only_metadata(): ...
```

→ 共 **23 项新测试**。Phase 3 真 LLM 蒸馏走 stub（不需真 LLM 在线）。

---

## §8 与 P3 衔接

### §8.1 MemoryValidity 过滤器接入点

```python
# Phase 3 unified_filter 接口（接口 V1，实施 P3）
class UnifiedArchiveFilter(Protocol):
    def filter(
        self,
        node: SemanticNode,
        archive_context: ArchiveContext,
    ) -> FilterDecision: ...

class FilterDecision(str, Enum):
    KEEP = "keep"                         # 进 Graphiti
    SKIP = "skip"                         # 不进 Graphiti（无价值 / 已过期）
    SUMMARIZE = "summarize"                # 蒸馏后再进
```

桌面 baseline `KeepAllFilter`（接口预留，P3 替换为 `MemoryValidityFilter`）：
```python
class KeepAllFilter(UnifiedArchiveFilter):
    def filter(self, node, ctx) -> FilterDecision:
        return FilterDecision.KEEP
```

P3 实施 `MemoryValidityFilter`（[`module_map_p2 §11.2`](../module_map_p2.md)）：
- Ebbinghaus 衰减公式
- 置信度阈值
- 用户重要性标记

### §8.2 nanobot 闲时检测协议

```python
# 与 nanobot skill 协同（详见 .cursor/skills/nanobot/SKILL.md）

# 写心跳：parrot.bus.nanobot_consumer
HASH_NANOBOT_HEARTBEAT = "parrot:nanobot_heartbeat"
# fields: {worker_id: last_heartbeat_ts}

# 读心跳：IdleArchiveTrigger
async def is_nanobot_idle(min_idle_seconds: float = 600) -> bool:
    last_ts = await redis.hget(HASH_NANOBOT_HEARTBEAT, "main_worker")
    return last_ts and (time.time() - float(last_ts)) > min_idle_seconds
```

---

## §9 引用

- 主设计稿：[`dsg_l1_5_pool_and_lifecycle_design_20260506.md`](dsg_l1_5_pool_and_lifecycle_design_20260506.md)
- Pool 协议：[`dsg_protocol_pool_v1_20260506.md`](dsg_protocol_pool_v1_20260506.md)
- 触发器协议：[`dsg_protocol_trigger_v2_20260506.md`](dsg_protocol_trigger_v2_20260506.md)
- IntentWorkspace 协议：[`brain_protocol_intent_workspace_v1_20260506.md`](brain_protocol_intent_workspace_v1_20260506.md)
- Plan 协议：[`brain_protocol_plan_v1_20260506.md`](brain_protocol_plan_v1_20260506.md)
- master 决策：[`dsg_decisions_master.md §5`](dsg_decisions_master.md)
- 既有代码：`src/parrot/dsg/l2b_graph.py:start_episode / archive_episode_to_graphiti`
- 既有 TODO：`src/parrot/dsg/ingest/runner.py:commit_observation`
- nanobot skill：[`.cursor/skills/nanobot/SKILL.md`](../../../skills/nanobot/SKILL.md)
- MemoryValidity 占位：[`../module_map_p2.md §11.2`](../module_map_p2.md)

---

## §10 变更日志

- **2026-05-06**：本协议 V1 创建。三阶段管线 + ConversationBoundaryDetector + ArchiveRequest schema + 6 jsonl 序列化格式 + 与既有 `start_episode` / `commit_observation` 冲突解决方案 + 23 项验证测试 + UnifiedArchiveFilter 接口（P3 接入）+ nanobot 闲时检测协议。
