---
status: ratified
category: ADR
adr_id: ADR-L1.5-001
status_note: "Phase 4 → 5 transition ADR. Records Q1 (Python only) / Q2 (meta+factory hybrid) / Q3 (fork chat ADR-only) decisions about adding source field to SemanticNode + extension space for future per-source dispatch. NOT a Phase 4 lock change — purely additive."
last_reviewed: 2026-05-04
decision_owner: "本 chat (Sprint 4 Phase 4 主 chat) + 用户 sign off 2026-05-04"
supersedes: []
superseded_by: []
related:
  - ".cursor/memory/architecture/sprint4_phase4_completion_and_final_audit_20260430.md"
  - ".cursor/memory/architecture/sprint4_phase4_brain_self_audit_20260430.md"
  - ".cursor/memory/architecture/audit_identify_object_no_screenshot_20260420.md §9.1"
  - "src/parrot/dsg/l2b_types.py — Source dispatch module-level comment"
  - "src/parrot/dsg/ingest/runner.py — _source_for_node() resolver"
ai_priority: high
ai_audience: "未来任何动 dsg/l2b_types.py / dsg/ingest/runner.py / dsg/l1_5_protocol.py / 加新 ingest source 的 chat 必读"
---

# ADR-L1.5-001 — L1.5 Source 字段 + 扩展空间设计

> **简单原则**：Phase 4 锁定的协议合同不动；为 Phase 5+ 的"按 source dispatch 不同 Node 状态/生命周期/子类"留前向空间，**但不在 Phase 5+ 设计落地前选定 axis**。
>
> **关键基调**（用户 2026-05-04 原话）：
> > 我们需要先做的是给 L1.5 加一个来源字段或者记录来源的方式，并留下根据不同入口来源（比如 A10 入口等）选择不同的状态比如 Node 成为不同子类的空间。

---

## §0 TL;DR

| 维度 | 决定 |
|:--|:--|
| **Q1 — source 字段去哪？** | Python only — `SemanticNode.source` + `SemanticNode.source_meta`。**不上 Unity wire**。 |
| **Q2 — 怎么留扩展空间？** | Meta dict + factory hook 混合：`source_meta: dict[str, Any]` + `_SOURCE_META_FACTORIES` 注册表 + `SemanticNode.from_observation()` classmethod。**不引入子类**。 |
| **Q3 — 协议升级 + 接口提炼 ADR 在哪做？** | Fork chat 只做 ADR + 要求归纳；接口提炼真实施 + 独立审计派发独立 chat。 |
| Phase 4 影响 | 0 协议合同变更（entry §8 决策锁不动）；仅 SemanticNode 加 2 字段 + 1 classmethod；IngestRunner 路径 refactor 走 factory；带向后兼容 fallback |
| 测试基线 | +11 项（`tests/test_dsg/test_l2b_node_source_dispatch.py`）|

---

## §1 问题陈述

### §1.1 现状

Phase 4 收口时 L2-B `SemanticNode` 是**单一 dataclass + `kind: NodeKind` enum 字段**（OBJECT/SURFACE/ZONE/PERSON/EVENT/PHOTO 6 项）。`SensorFrame` 已携带 `source: FrameSource`（A10_SAM2_DINOV2 等 7 项）；`Observation` 已携带 `source: ObservationSource`（USER_*/IDENTIFY_OBJECT/GEMINI_ORAL/CV_*/MOCK 7 项）。**但 `IngestRunner._observation_to_node` 在创建 SemanticNode 时显式丢掉了 `obs.source`** — 节点上只剩 `provenance_stream_id`（指向 L0 事件 id 的弱关联），认证 / 优先级时靠 `_source_for_node()` 用 identifier 反推 USER_TAG_OBSIDIAN / IDENTIFY_OBJECT / GEMINI_ORAL 三选一启发式。

### §1.2 问题

1. **信息丢失**：节点不记 source，"这个节点最初是 A10 还是 Gemini 还是 user 创建的"必须回溯 L0 才能知道，下游处理无法 dispatch。
2. **无前向空间**：未来 Phase 5+ 接入 A10 视觉管线时，需要让 A10-source 节点带自己的 `track_id` / `reid_hash` / `yolo_class_votes` 等扩展字段；当前 schema 没空间装。
3. **过早子类化的风险**：用户 audit §9.1 明确"具体的多样化 Node 状态和生命周期设计在 L2-B 完善过程中完成，效果未知"——立刻引入子类会锁错 axis，未来重构成本远高于现在 meta dict + factory 留出的抽象。

### §1.3 为什么现在做（不推后到 Phase 5）

- **Phase 4 → 5 的 cleanest seam**：Phase 4 协议合同已锁 0 漂移；接口提炼 chat / DSG 完善 chat 都需要"source 已经能 propagate 到 Node"作为前置假设。先把 source 字段 + 扩展 hook 落地，下游 chats 拿到的是稳定接口面。
- **改动成本极小**：2 字段 + 1 classmethod + 1 factory dict + IngestRunner 1 处 refactor。完整向后兼容（默认值保留旧行为）。

---

## §2 决策（Q1 / Q2 / Q3）

### §2.1 Q1 — source 字段在哪一层？

**决定**：**Python only**（Brain `dsg/l2b_types.py` + `dsg/ingest/base.py` + `dsg/ingest/runner.py`）。**不上 Unity wire**（不动 EcpEvent payload schema、不动 BB key 结构、不加新 EcpEventType）。

**理由**：

| 方案 | Python only ✅ | 上 Unity wire ❌ |
|:--|:--|:--|
| A10 入口 | A10 是 Brain-side CV pipeline，永远不通过 Unity DataChannel | 加字段对 Unity 来说是死字段 |
| 现有 wire 来源标识 | EcpEventSource enum 已经够（unity / brain / nanobot 占位）| 与已有重叠 |
| 跨语言契约稳定性 | Python enum 增减不动 cs_parity | 任何 wire 字段动会触发 cs_parity 守护 → 协议合同变更 |
| Phase 4 §8 锁 | 0 漂移 | 直接违反 entry §8 §8.5 #4 enum 锁 |

**反对理由审视**：用户的"不同入口源"包含 Unity 用户主动操作（USER_EXPLICIT 走 LLM tool 调用 → ObservationSource）。这条路径在 Phase 4 已经走 EcpEvent + Brain 端 Observation，**不需要在 wire 上额外打 source tag**——EcpEventSource = unity 已经隐含了这一层。

### §2.2 Q2 — 怎么留扩展空间？

**决定**：**Meta dict + factory hook 混合**。

实施面：

```python
# src/parrot/dsg/l2b_types.py 新增

@dataclass
class SemanticNode:
    ...
    # 新字段（Phase 4 → 5 transition, 2026-05-04, ADR-L1.5-001）
    source: str = ""                                       # ObservationSource.value 或 ""
    source_meta: dict[str, Any] = field(default_factory=dict)  # 自由扩展槽

    @classmethod
    def from_observation(cls, obs: "Any") -> "SemanticNode":
        """工厂方法 — 通过 _SOURCE_META_FACTORIES 派发"""
        source_value = obs.source.value
        factory = _resolve_source_meta_factory(source_value)
        source_meta = factory(obs)
        return cls(source=source_value, source_meta=source_meta, ...)


_SOURCE_META_FACTORIES: dict[str, Callable] = {}

def register_source_meta_factory(source_value: str, factory: Callable) -> None:
    """新 ingest source（A10 / Sentinel / 未来）调本函数注册自己的
    source_meta builder。SemanticNode 不动。"""
    _SOURCE_META_FACTORIES[source_value] = factory
```

**为什么不选其他方案**：

| 方案 | 优点 | 致命缺点 |
|:--|:--|:--|
| 1️⃣ **只加字段（无 factory）** | 改动最小 | 没扩展面；A10 想塞 reid_hash 还是要改 SemanticNode |
| 2️⃣ **Meta dict + factory 混合**（**选定**） | 0 lock-in；新 source 注册即可；典型可演化路径清晰 | 类型系统帮不上忙（dict + Any）；IDE / lint 看不见结构 |
| 3️⃣ **基类 + 子类 dispatch** | 类型系统强制；isinstance 可 dispatch | **立刻锁死子类边界**——audit §9.1 明确"效果未知"，不该现在做 |

**option 3 的延迟原则**：当**满足以下条件之一**时升级到子类：
- L1.5 预加载 Node 池 design（独立 chat）发现 ≥3 个 source 需要的字段差异 ≥3 个
- ≥2 个 source 需要**行为多态**（不只是数据 shape），如 A10 节点 `touch()` 时自动 decay confidence 而 user 节点不 decay
- 类型系统强制 dispatch 的需求被反复手写 isinstance 验证

### §2.3 Q3 — 协议升级 + 接口提炼 ADR 在哪做？

**决定**：

| Chat | 范围 |
|:--|:--|
| 本 chat（已落 Sprint 4 主线） | 完成本 ADR + Deliverable A/B/C/D（§3 列表） |
| Fork chat（任务 2，本 chat fork 出去）| 协议升级 + 接口提炼**要求归纳 + ADR**（不实施代码）|
| 接口提炼 chat（独立派发）| 实施 ADR 的接口设计 + 重构 |
| 独立审计 chat | cold-read 接口提炼成果 |

**理由**：用户 2026-05-04 原话明确"任务 2 是此 chat 的 fork chat 内完成足够多的协议升级和接口提炼的要求归纳和 ADR；然后我们开始 chat 接口提炼和独立审计"——4 chat 路径已锁。

---

## §3 实施清单（Deliverable B 已落，本文 ADR 是 §3 的最终文档）

| 项 | 文件 | 状态 |
|:--|:--|:--|
| `SemanticNode.source` + `source_meta` 字段 | `src/parrot/dsg/l2b_types.py` | ✅ landed |
| `SemanticNode.from_observation()` classmethod | 同上 | ✅ landed |
| `_SOURCE_META_FACTORIES` 注册表 + `register_source_meta_factory()` | 同上 | ✅ landed |
| `IngestRunner._observation_to_node` 走 factory | `src/parrot/dsg/ingest/runner.py` | ✅ landed |
| `_source_for_node()` 优先 `node.source`，fallback 启发式 | 同上 | ✅ landed |
| 11 项测试 | `tests/test_dsg/test_l2b_node_source_dispatch.py` | ✅ landed |
| 模块级注释（高优 AI 可读）| `dsg/l2b_types.py` 顶部 + 字段处 + 与 ADR 反向引用 | ✅ landed |

---

## §4 后续升级路线（**给未来 chat 看**）

### §4.1 触发条件 → 升级路径

| 当出现 | 当前形态 | 升级为 |
|:--|:--|:--|
| A10 source 想稳定塞 ≥3 字段（reid_hash / track_id / yolo_class_votes / ...） | meta dict | 新建 `parrot.dsg.l2b_source_meta.A10NodeMeta` Pydantic model；`SemanticNode.source_meta` 类型仍为 `dict[str, Any]` 但**约定** A10 source 塞 `A10NodeMeta.model_dump()`；factory return typed model 然后 dump |
| ≥3 sources 各自有稳定 schema | 多个 model 共存 | 用 `Annotated[Union[...], Field(discriminator="source")]` discriminated union 收口；source_meta 类型升级为该 union |
| ≥2 sources 行为差异（非数据差异）| 单一 SemanticNode | 引入子类：`A10SemanticNode(SemanticNode)` / `UserSemanticNode(SemanticNode)`；新 isinstance dispatch；Factory 改 `register_source_node_class()`；source_meta 仍可作为 fallback |
| L1.5 预加载 Node 池 lifecycle 跨 source 差异化（A10 自动衰减 / user 永不衰减）| `touch()` 单一实现 | 升子类后子类各自 override `touch()` / `decay()` |

### §4.2 不允许提前做的事

- **不要**在 L1.5 preloaded Node 池 design 落定前升级到 option 3（子类 dispatch）— 会锁错 axis
- **不要**在 Q2 选定的 meta dict 之外引入"半结构化"中间方案（如 `meta: dict[str, Any]` + `meta_schema: str`）— 同样的复杂度，没有 model 强制
- **不要**把 source 字段加到 Unity wire（违反 Q1 + entry §8.5 #4）

### §4.3 ADR 修订条件

本 ADR 状态升 `superseded` 当：
- L1.5 预加载 Node 池 design chat 落定且建议子类化
- 接口提炼 chat 决定升级到 typed source_meta union
- 出现新 ingest source 而 factory hook 不够用（罕见）

升级时新 ADR 必须显式 `supersedes: [ADR-L1.5-001]` 并解释 axis 为何此时变成可锁定的。

---

## §5 与既有协议合同的兼容性证明

| 检查项 | 结果 |
|:--|:--|
| Phase 4 entry §8 决策锁 L1-L13 | 不变 |
| EcpEvent / EcpEventType / topic / 8KB / schema_version 常量 | 不变 |
| BB key 名字 / scope / writer 字段 | 不变 |
| Unity wire 任意字段 | 不变 |
| `test_cs_parity` 跨语言守护 | 不影响（仅 Python 改动） |
| 测试基线 | +11（test_dsg/test_l2b_node_source_dispatch.py）|
| 已知 pre-existing breakage | `test_ecp_event/test_identify_object.py` env-gate import 路径冲突，与本 ADR 无关 — 留独立审计 chat 修 |

---

## §6 引用

- `architecture/sprint4_phase4_entry_20260430.md` §8 — Phase 4 决策锁（**不变**）
- `architecture/sprint4_phase4_completion_and_final_audit_20260430.md` — Phase 4 收口
- `architecture/audit_identify_object_no_screenshot_20260420.md` §9.1 — 用户原话锚点（"效果未知 / L2-B 完善过程中完成"）
- `src/parrot/dsg/l2b_types.py` — "Source dispatch" 模块级注释（实施层）
- `src/parrot/dsg/ingest/runner.py` — `_source_for_node()` 解析顺序
- `tests/test_dsg/test_l2b_node_source_dispatch.py` — 验证新行为 + 向后兼容
