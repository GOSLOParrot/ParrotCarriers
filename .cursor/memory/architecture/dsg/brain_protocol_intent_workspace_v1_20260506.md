---
status: draft
category: protocol-spec
protocol_id: BRAIN-INTENT-WS-V1
status_note: "Brain Intent 层资源暂存协议 V1 — IntentWorkspace 大文件常驻 + StagedRefKind 9 类 + Backend strategy + 与 L1.5 RefTable 衔接 + IntentEvent 级自动 evict。借鉴 Cursor / Claude / OpenAI Assistants v2 / LlamaIndex 模式。"
last_reviewed: 2026-05-06
ai_priority: high
ai_audience: "实施 chat / Brain Intent 层使用者 / nanobot 富文本回流接入者"
parent_doc: "dsg_l1_5_pool_and_lifecycle_design_20260506.md"
companion_protocols:
  - "dsg_protocol_pool_v1_20260506.md"
  - "dsg_protocol_trigger_v2_20260506.md"
  - "dsg_protocol_intent_event_boundary_v1_20260506.md"
  - "brain_protocol_plan_v1_20260506.md"
---

# BRAIN-INTENT-WS-V1 — Brain IntentWorkspace 协议

> **协议 ID**：BRAIN-INTENT-WS-V1
> **范围**：`src/parrot/brain/intent_workspace.py` + `intent_workspace_backend.py`。
> **职责**：GOSLO Intent 层"当前正在读 / 正在分析 / 正在使用"的大文件常驻内存空间。
> **不在范围**：节点本体（在 L2-B）/ 轻量 Ref UUID 绑定（在 L1.5 RefTable）/ 长期归档（在 Graphiti）。

---

## §0 术语表

参见 [主设计稿 §0](dsg_l1_5_pool_and_lifecycle_design_20260506.md)。本协议关注：
- `IntentEvent`（认知边界）— IntentWorkspace 的主生命周期 owner
- `Plan`（计划）— 一种 StagedRefKind
- `Bucket` / `Compartment` 与本协议正交（不直接交互）

---

## §1 设计起源

### §1.1 用户原话锚定（2026-05-06）

> 上述所说的 Ref 内存空间，我想应该是给 GOSLO Intent 层使用的，用来存放 GOSLO 正在使用的大文件，比如照片、nanobot 除了一般文本汇报外的其他富文本或者多模态大型汇报文件，需要 GOSLO 亲自读的文件等等。
> 
> 具体这个工作区和内存空间，应该市面上或者很多成熟的项目（比如 cursor、ClaudeCode、以及很多 AI 项目）应该都有了很成熟的设计经验了，直接猛抄就行了。

### §1.2 借鉴的成熟模式

| 项目 | 模式 | 我们抄什么 |
|:--|:--|:--|
| **Cursor** | workspace context = 显式 attach + 自动 RAG retrieval | 显式 stage + Intent-scoped 自动 evict |
| **Claude Desktop / API** | conversation-thread-scoped attachments | per-IntentEvent lifecycle |
| **OpenAI Assistants v2 with code_interpreter** | thread.attachments + file_ids | `RefHandle` 句柄 + content-addressable |
| **LangChain / LlamaIndex** | DocumentStore + ContextStore 分离 | RefTable（轻）+ IntentWorkspace（重）分离 |
| **VS Code working set** | 同时打开的文件集合 | `list_active(intent_event_id)` 返回当前活跃集 |

---

## §2 模块边界

### §2.1 IntentWorkspace 持有 / 不持有

| 持有 | 形态 |
|:--|:--|
| `dict[ref_id, StagedRef]` | 内存索引（payload 在 backend）|
| `Backend` strategy 实例 | InMemoryBackend / DiskBackend / 未来 Redis |
| `MemoryPressureMonitor` | 容量告警 |
| `IntentEventLifecycleHook` | 监听 IntentEvent close → 批量 evict |

| 不持有 | 真主在 |
|:--|:--|
| SemanticNode 本体 | L2BGraph |
| 轻量 Ref UUID 绑定 | L1.5 RefTable |
| Plan 状态机（DRAFT/CONFIRMED/...）| brain.plan.PlanRegistry |
| 长期记忆 | Graphiti |
| 当场写 Graphiti 的能力 | dsg.archive |

### §2.2 落位

```
src/parrot/brain/
├── intent_workspace.py             ← IntentWorkspace 主类
├── intent_workspace_backend.py     ← Backend Protocol + InMemoryBackend + DiskBackend
└── ...
```

---

## §3 StagedRefKind + StagedRef Schema

```python
class StagedRefKind(str, Enum):
    PHOTO = "photo"                       # data/snapshots/objects/{uuid}/reference.jpg
    DOC = "doc"                            # Obsidian / 用户上传 doc
    URL = "url"                            # web 快照（lazy fetch）
    MERMAID = "mermaid"                    # 文本图源
    RICH_REPORT = "rich_report"            # nanobot 富文本汇报（非纯文本）
    VIDEO_SHORT = "video_short"            # 短视频片段（≤ MB 级）
    AUDIO_CLIP = "audio_clip"              # 短音频片段
    PLAN = "plan"                          # Plan 主存（brain_protocol_plan_v1）
    OTHER = "other"


class PayloadSource(str, Enum):
    DISK_PATH = "disk_path"                # payload = Path
    INLINE_BYTES = "inline_bytes"          # payload = bytes（≤ N MB 内存常驻）
    INLINE_TEXT = "inline_text"            # payload = str
    URL = "url"                            # payload = url string（lazy fetch）


@dataclass(frozen=True)
class StagedRef:
    ref_id: str                            # uuid4().hex[:16]
    kind: StagedRefKind
    payload_source: PayloadSource
    payload: Path | bytes | str            # 按 payload_source 区分
    metadata: StagedRefMetadata


@dataclass(frozen=True)
class StagedRefMetadata:
    origin: str                            # "tool:identify_object" / "trigger:goslo_curiosity" / "nanobot_task:xyz"
    related_node_uuid: str = ""             # 若与某 L2-B 节点关联
    related_intent_event_id: str = ""       # 若属某 IntentEvent
    related_plan_id: str = ""               # 若属某 Plan
    size_bytes: int = 0
    loaded_at: float = 0.0
    last_accessed_at: float = 0.0
    auto_evict_on_intent_close: bool = True
    expires_at: float = 0.0                 # 0.0 = 跟随 IntentEvent；非 0 = 绝对过期时间
    custom_meta: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StagedRefRequest:
    """触发器 → IntentWorkspace 的上行通道（dsg_protocol_trigger_v2 用）"""
    kind: StagedRefKind
    payload_source: PayloadSource
    payload_value: Any                      # path / bytes / str
    metadata: StagedRefMetadata
```

---

## §4 IntentWorkspace 接口

```python
class IntentWorkspace:
    """GOSLO Intent 层的 Ref 内存暂存空间。
    
    生命周期：
      stage → fetch（多次）→ list_active → evict（手动 / 自动 IntentEvent close 批量 / 容量压力下）
    
    存储：
      strategy backend — InMemory baseline / Disk baseline / 未来 Redis / S3 / FAISS
    """

    def __init__(
        self,
        backend: "IntentWorkspaceBackend | None" = None,
        max_memory_bytes: int = 256 * 1024 * 1024,   # 桌面 baseline 256MB
    ): ...

    async def stage(self, request: StagedRefRequest) -> RefHandle:
        """加载 Ref 进 workspace。
        
        步骤：
          1. 生成 ref_id = uuid4().hex[:16]
          2. backend.put(ref_id, payload) — 写入存储后端
          3. 更新内存索引 dict[ref_id, StagedRef]
          4. 写 Timeline marker（通过 L1.5 Pool）— 可选
          5. 返回 RefHandle（含 ref_id + metadata 引用）
        
        不变量：
          - 幂等检查（同 (kind, payload value hash) 已 stage → 返回既有 RefHandle）— 防止重复 stage
        """

    async def stage_from_path(
        self,
        path: Path,
        kind: StagedRefKind,
        metadata: StagedRefMetadata,
    ) -> RefHandle:
        """便利方法 — 从硬盘文件 stage（自动 PayloadSource=DISK_PATH）"""

    def fetch(self, ref_id: str) -> StagedRef | None:
        """获取已 stage 的 Ref；更新 last_accessed_at"""

    def fetch_payload(self, ref_id: str) -> Path | bytes | str | None:
        """便利方法 — 直接拿 payload"""

    def list_active(
        self,
        intent_event_id: str | None = None,
        kinds: frozenset[StagedRefKind] | None = None,
    ) -> list[RefHandle]:
        """列出当前活跃 Ref（给 GOSLO Context Injector 拉清单）
        
        过滤：
          - intent_event_id = None → 全部活跃
          - intent_event_id 显式 → 仅该 IntentEvent 的
          - kinds 过滤 → 仅指定类型
        """

    def evict(self, ref_id: str) -> bool:
        """手动 evict 单个 Ref；返回是否实际 evict"""

    def evict_intent(self, intent_event_id: str) -> int:
        """批量 evict — IntentEvent close 时自动调（auto_evict_on_intent_close=True 的）
        
        返回 evict 数量。
        """

    def evict_expired(self) -> int:
        """主动扫描 expires_at 过期的 Ref；周期性调用"""

    def memory_pressure(self) -> "PressureReport":
        """容量报告 — 用于决策是否需要主动 evict 低优先级 Ref"""

    async def close(self) -> None:
        """全清；agent disconnect 时调"""


@dataclass(frozen=True)
class RefHandle:
    """引用句柄 — 不含 payload，含 ref_id + metadata 引用"""
    ref_id: str
    kind: StagedRefKind
    metadata: StagedRefMetadata
    
    def __repr__(self) -> str:
        return f"RefHandle({self.kind.value}/{self.ref_id})"


@dataclass(frozen=True)
class PressureReport:
    backend_usage_bytes: int
    backend_total_capacity: int
    pressure_level: PressureLevel
    candidate_evictions: tuple[str, ...]   # 推荐 evict 的 ref_id（按优先级排）

class PressureLevel(str, Enum):
    OK = "ok"                              # < 60% 容量
    WATCH = "watch"                        # 60-80%
    WARN = "warn"                          # 80-95%
    CRITICAL = "critical"                  # > 95% — 主动 evict
```

---

## §5 IntentWorkspaceBackend strategy

### §5.1 接口

```python
class IntentWorkspaceBackend(Protocol):
    """存储后端协议 — 实现替换不影响 IntentWorkspace 上层 API"""

    async def put(self, ref_id: str, payload, metadata: StagedRefMetadata) -> None: ...
    async def get(self, ref_id: str) -> StagedRef | None: ...
    async def delete(self, ref_id: str) -> bool: ...
    def usage(self) -> int:
        """当前已用字节数"""
    def list_ref_ids(self) -> list[str]: ...
    async def close(self) -> None: ...
```

### §5.2 InMemoryBackend（桌面 baseline）

```python
class InMemoryBackend(IntentWorkspaceBackend):
    """全内存 — 桌面 baseline。
    
    适用：≤ 256MB 总容量；桌面 ≤ 几十个 Ref。
    限制：进程重启数据丢失（不持久）。
    """
    def __init__(self):
        self._store: dict[str, StagedRef] = {}

    async def put(self, ref_id, payload, metadata) -> None: ...
    async def get(self, ref_id) -> StagedRef | None: ...
    async def delete(self, ref_id) -> bool: ...
    def usage(self) -> int:
        return sum(self._size(ref) for ref in self._store.values())
    ...
```

### §5.3 DiskBackend（备选 baseline，PHOTO/VIDEO 用）

```python
class DiskBackend(IntentWorkspaceBackend):
    """落盘 + 内存元数据索引 — 大文件场景 baseline。
    
    适用：PHOTO / VIDEO_SHORT 等 > 1MB 类型。
    路径：data/intent_workspace/{ref_id}.{ext}
    """
    def __init__(self, base_path: Path = Path("data/intent_workspace")):
        self._base = base_path
        self._index: dict[str, StagedRefMetadata] = {}
    ...
```

### §5.4 注册 / 替换

```python
def register_intent_workspace_backend(backend: IntentWorkspaceBackend) -> None: ...
def get_intent_workspace() -> IntentWorkspace: ...
```

→ 测试时通过 `set_intent_workspace_for_test(ws)` 注入 mock。

---

## §6 与 L1.5 RefTable 的衔接

### §6.1 双层 Ref 架构

```
L1.5 RefTable（轻量绑定，O(1) 查询）
  RefBinding(node_uuid, kind, ref_value, intent_workspace_ref_id)
    ↓ 反向查找：lookup_by_ref(kind, value) → node_uuid
    ↓ 正向枚举：list_refs_of_node(node_uuid) → [RefBinding, ...]
    ↓ 健康度：ref_health_report() → [RefHealth, ...]

IntentWorkspace（重量缓存，按需加载）
  StagedRef(ref_id, kind, payload, metadata)
    ↓ 主入口：stage(StagedRefRequest) → RefHandle
    ↓ 获取：fetch(ref_id) → StagedRef
    ↓ 列表：list_active(intent_event_id) → [RefHandle, ...]
    ↓ Evict：evict / evict_intent / evict_expired
```

### §6.2 衔接路径

```python
# 1. 触发器找到 photo → stage 到 IntentWorkspace + bind 到 L1.5 RefTable
async def on_curiosity_event(event):
    photo_path = Path(event["photo_path"])
    related_node = event["related_node_uuid"]
    
    # stage 到 IntentWorkspace
    ws = get_intent_workspace()
    handle = await ws.stage_from_path(
        photo_path,
        kind=StagedRefKind.PHOTO,
        metadata=StagedRefMetadata(
            origin="trigger:goslo_curiosity",
            related_node_uuid=related_node,
            related_intent_event_id=current_intent_event_id(),
            auto_evict_on_intent_close=True,
        ),
    )
    
    # bind 到 L1.5 RefTable
    pool = get_l1_5_pool()
    pool.bind_ref(
        node_uuid=related_node,
        kind=RefKind.PHOTO_PATH,
        ref_value=str(photo_path),
        intent_workspace_ref_id=handle.ref_id,
    )

# 2. GOSLO Intent 层用 ref：先查 RefTable，再 fetch IntentWorkspace
async def goslo_analyze_node(node_uuid):
    pool = get_l1_5_pool()
    ws = get_intent_workspace()
    
    bindings = pool.list_refs_of_node(node_uuid)
    for binding in bindings:
        if binding.kind == RefKind.PHOTO_PATH and binding.intent_workspace_ref_id:
            staged = ws.fetch(binding.intent_workspace_ref_id)
            if staged:
                # 用 staged.payload 给 GOSLO（多模态 prompt）
                ...
```

### §6.3 Evict 联动

```python
# IntentEvent close → 触发 IntentWorkspace.evict_intent → 同步清理 L1.5 RefTable.intent_workspace_ref_id 字段
async def on_intent_event_close(event_id):
    ws = get_intent_workspace()
    evicted_ref_ids = await ws.evict_intent(event_id)
    
    pool = get_l1_5_pool()
    for ref_id in evicted_ref_ids:
        # 找到所有引用这个 ref_id 的 RefBinding，清空 intent_workspace_ref_id 字段
        # （RefBinding 本身保留，仅清空 IntentWorkspace 引用 — Ref 元数据健在）
        pool.clear_intent_workspace_ref(ref_id)
```

---

## §7 与 Plan 的关联

详见 [`brain_protocol_plan_v1_20260506.md`](brain_protocol_plan_v1_20260506.md) §6。

简表：

| Plan 阶段 | IntentWorkspace 行为 |
|:--|:--|
| DRAFT | `stage(kind=PLAN, related_plan_id=plan_id)` — Plan 主存 |
| AWAITING_USER_CONFIRMATION | 不动（仅元数据 last_accessed_at 更新） |
| APPROVED | 不动；同时 stage Plan 内引用的资源（PlanStep 关联 photo 等）|
| EXECUTING | NanobotTask 完成 → result 若是 RICH_REPORT → stage(RICH_REPORT, related_plan_id) |
| DONE / FAILED / CANCELLED | evict_intent(intent_event_id)（plan-related refs auto evict）|

---

## §8 协议合同 0 漂移核对

| 检查项 | 状态 |
|:--|:--|
| Phase 4 §8（全部 13 锁）| ✅ 不动 — IntentWorkspace 在 Brain 内部，不动 wire / 不动 NodeKind / 不动 attention |
| ADR-L1.5-001 | ✅ 不动 — IntentWorkspace 不动 SemanticNode 字段 |
| `parrot_behavior_rules §3.7` | ✅ IntentWorkspace 不抓帧 / 不写 Graphiti / 不读写 attention |
| `tests/test_ecp_event/test_cs_parity.py` 4/4 | ✅ 不动 wire |

---

## §9 测试覆盖

```python
# tests/test_brain/test_intent_workspace_lifecycle.py
def test_stage_returns_handle(): ...
def test_stage_idempotent_on_same_payload_hash(): ...
def test_fetch_returns_staged_ref(): ...
def test_fetch_updates_last_accessed_at(): ...
def test_list_active_filters_by_intent_event_id(): ...
def test_list_active_filters_by_kinds(): ...
def test_evict_removes_from_index(): ...
def test_evict_intent_removes_all_intent_scoped(): ...
def test_evict_intent_keeps_other_intent_refs(): ...
def test_evict_expired_scans_expires_at(): ...
def test_close_clears_all(): ...

# tests/test_brain/test_intent_workspace_backend.py
def test_in_memory_backend_put_get_delete(): ...
def test_in_memory_backend_usage_tracks_bytes(): ...
def test_disk_backend_persists_to_path(): ...
def test_disk_backend_survives_restart(): ...
def test_swap_backend_via_register(): ...

# tests/test_brain/test_intent_workspace_pressure.py
def test_pressure_ok_below_60(): ...
def test_pressure_warn_above_80(): ...
def test_pressure_critical_above_95(): ...
def test_candidate_evictions_orders_by_lru(): ...

# tests/test_brain/test_ref_handle_node_binding.py
def test_stage_then_bind_ref_table(): ...
def test_intent_event_close_evicts_and_clears_ref_table(): ...
def test_dual_layer_lookup_node_to_payload(): ...
```

→ 共 **22 项新测试**。

---

## §10 扩展点

| 扩展点 | 当前 baseline | P3+ 升级 |
|:--|:--|:--|
| `IntentWorkspaceBackend` | InMemory / Disk | Redis（多进程共享）/ S3（云持久）/ FAISS（embedding 索引）|
| Eviction 算法 | LRU + auto_evict_on_intent_close | LFU / TWF / 用户重要性加权 |
| 内存压力告警 | 静态阈值（60/80/95%） | 动态 + 用户配置 + 操作系统 mem 信号 |
| 跨进程共享 | 单进程 InMemory | Redis backend 多进程 / Castle 集群 |
| 内容寻址 | metadata.payload_value hash 幂等检查 | content-addressable 全局去重 |
| stage 限速 | 无 | 突发保护 / rate limiting |
| 大文件流式 | 全加载 | 流式 read（VIDEO_SHORT 切片）|

---

## §11 引用

- 主设计稿：[`dsg_l1_5_pool_and_lifecycle_design_20260506.md`](dsg_l1_5_pool_and_lifecycle_design_20260506.md)
- L1.5 Pool 协议：[`dsg_protocol_pool_v1_20260506.md`](dsg_protocol_pool_v1_20260506.md)
- 触发器协议：[`dsg_protocol_trigger_v2_20260506.md`](dsg_protocol_trigger_v2_20260506.md)
- IntentEventBoundary 协议：[`dsg_protocol_intent_event_boundary_v1_20260506.md`](dsg_protocol_intent_event_boundary_v1_20260506.md)
- Plan 协议：[`brain_protocol_plan_v1_20260506.md`](brain_protocol_plan_v1_20260506.md)
- 借鉴模式参考（外部）：Cursor workspace / Claude Desktop attachments / OpenAI Assistants v2 thread.attachments / LlamaIndex DocumentStore + ContextStore

---

## §12 变更日志

- **2026-05-06**：本协议 V1 创建。IntentWorkspace 完整 API（stage / fetch / list_active / evict 系列）+ 9 项 StagedRefKind + Backend strategy（InMemory / Disk）+ L1.5 RefTable 双层衔接 + Plan 关联 + 22 项验证测试 + 7 处扩展点。
