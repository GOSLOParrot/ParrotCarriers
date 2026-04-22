---
status: tentative
status_note: "S0.C 产出的 API 约定。Sprint 1 接入 dispatcher 写入端、Sprint 4 接入 PhotoEvent 写入端后, 所有投影方向都跑通, 再升 ratified。"
last_reviewed: 2026-04-22
---

# GOSLO 时间轴 API 约定 (Timeline API Contract)

> 本文件是 `sprint0_preflight.md §1` 的**代码可读版摘要**, 面向 Sprint 1+ 的开发者。
> 讨论源头请读 preflight §1 (Chronos / REMem / SEEM / eventure / Claru 2026 前沿对齐)。
> 本文不复述调研, 只写**如何写代码才合规**。

---

## 0. TL;DR — 3 条硬规则

1. **所有状态变化事件先写 L0 Redis Stream** (`parrot.events.log`), 再投影到 L1/L2/L3。**不准绕过**。
2. **任何 L2-B / L3 节点必须带 `provenance_stream_id`**, 指回 L0 的条目 id (Redis XADD 返回值)。空字符串只允许 preload 场景 (事件流之前的数据)。
3. **L1 Blackboard 不是时间轴**, 只存"现在"。查历史一律走 L0 replay 或 L2/L3 投影。

---

## 1. 四层时间轴定位

| 层 | 技术位置 | 用途 | 谁写 | 谁读 |
|:---|:---------|:-----|:-----|:-----|
| **L0** Raw Event Stream | `parrot.events.log` Redis Stream | 唯一真相源, 永不删 (P3 前) | Sprint 1 dispatcher + 所有 BB 写入 + RPC ack + 异常 | Sprint 1+ 投影消费者; 审计; replay |
| **L1** Blackboard | py-trees Blackboard V2 (`src/parrot/scheduler/blackboard.py`) | 当前状态缓存, 无历史 | Sprint 1 BB 订阅 L0 后写 | BT 节点, soul_constraints |
| **L2** Graphiti Episode | Graphiti `add_episode()`, 4 分区 | 对话 turn / Gist 级长期记忆 | `conversation_writer`, `identify_object::_save_new_object` | `query_memory`, ContextInjector, triggers |
| **L3** DSG L2-B Event Node | `dsg/l2b_types.py`, RustworkX 图 + Graphiti 归档 | 结构化事件 / Fact 级 | `identify_object`, `manage_episode`, Sprint 4 PhotoEvent | triggers, query_scene |

---

## 2. 写入侧 API (Producer Contract)

### 2.1 Sprint 0 (当前) 能用的

**只有 schema 锁定**, 没有实际 Producer helper。Sprint 1 之前禁止写 L0。手动 `redis.xadd()` 绕过 `EventEnvelope` **禁止**, 会破坏 schema 不变量。

```python
from parrot.shared.event_log import EventEnvelope, EventLayer
from parrot.shared.constants import STREAM_EVENT_LOG

env = EventEnvelope(
    kind="bb.vision.state_changed",
    layer=EventLayer.INTENT,
    actor="brain.context_injector",
    payload={"from": "active", "to": "degraded", "reason": "low_brightness"},
)
# Sprint 1+ 才有的写入调用 (这里只是示意):
stream_id = await redis.xadd(STREAM_EVENT_LOG, env.to_xadd_fields())
```

### 2.2 `kind` 命名约定

格式: `<domain>.<subject>.<verb_past>`, 全小写, 点号分隔。

| 示例 | 场景 |
|:-----|:-----|
| `bb.vision.state_changed` | Blackboard vision/state 变化 |
| `bb.body.cognitive_state_changed` | Blackboard body/cognitive_state 变化 |
| `rpc.fly_to.rejected` | Unity RPC 拒绝 |
| `rpc.animate.acked` | Unity RPC 成功 |
| `dispatcher.intent.decided` | Intent 层决策 |
| `dispatcher.arbiter.conflict` | body 通道抢占冲突 |
| `l2b.node.created` | L2-B 新节点 |
| `l2b.episode.started` | Episode 开启 |
| `tool.identify_object.matched` | identify_object tool 命中 |
| `perception.l15.frame` | L1.5 detection frame (Sprint 2+) |
| `exception.brain.unhandled` | Brain 未捕获异常 |

**不要用**: 现在时 (`node_creating`)、副作用动词 (`create_node` 像命令不像事件)、驼峰、下划线 (`l2b_node_created` 错, `l2b.node.created` 对)。

### 2.3 `layer` 选择 (对应 Sprint 1 S1.F 三级调度)

| EventLayer | 何时用 | 投影行为 |
|:----------|:-------|:---------|
| `REFLEX` | ms 级身体反射 (手势 → fly_to, 张手 → perch) | 只写 L0 + 更新 L1 BB; Gemini **不通知** |
| `INTENT` | s-min 级模式/约束调整 (切 video_tier, 更新 soul_constraints) | 只写 L0 + 更新 L1 BB; Gemini **不通知** |
| `TASK` | min+ 级外部任务 (Nanobot dispatch, tool 调用, 用户可感知结果) | 写 L0 + L1 BB + Gemini 通知 (通过 ContextInjector) |

**错误案例**: 用 `TASK` 发一个 "每秒 30 次" 的 perception frame 事件, 会把 Gemini 淹没。高频事件一律 `REFLEX` 或不进 L0 (走 L1 直通如 telemetry 那样)。

### 2.4 `provenance_parent` 何时填

- 事件是对**某个 L0 事件的直接响应** → 填上那个事件的 stream id
  - 例: `identify_object` 因 `tool.identify_object.requested` 返回 `tool.identify_object.matched` → `provenance_parent` = 请求事件的 stream id
- 事件是**周期性/独立产生** (如心跳、上游 perception frame) → 留空

---

## 3. 投影消费侧 API (Projection Contract)

### 3.1 投影消费者的共同规则

1. **只读 L0**, 不回写 L0
2. **幂等**: 同一条 L0 事件重复投影不破坏状态 (Redis Stream 消费者挂起重连会 replay)
3. **最终一致**: 投影延迟允许, 但不准跳事件
4. **失败要能 replay**: 通过 consumer group 的 pending list 兜底 (Sprint 1 规划时细化)

### 3.2 L1 Blackboard 投影 (Sprint 1)

```python
# Sprint 1 伪代码 (当前未实现):
async for msg in stream_group_read():
    env = EventEnvelope.from_xadd_fields(msg.fields)  # Sprint 1 实现
    if env.kind.startswith("bb."):
        path, _, key = env.kind[3:].rpartition(".")  # "vision.state_changed" → ("vision", "state_changed")
        blackboard.set(f"{path}/{key}", env.payload["to"])
```

### 3.3 L2 Graphiti Episode 投影 (已部分实现)

**现状**: `conversation_writer` 直接写 Graphiti, **没经过 L0**。Sprint 1 S1.E `obs_log` 先并行记录一份到 L0 不阻塞现有路径, Sprint 4 再把 Graphiti 写入改成"经 L0 投影触发"。

**过渡期规则**: 目前 `conversation_writer` / `identify_object::_save_new_object` 的 Graphiti 写入**先写 L0 再写 Graphiti**, 失败不回滚 (容忍最终一致), 拉不到 Graphiti 只影响读路径, 不影响 L0 真相源。

### 3.4 L3 L2-B Event Node 投影 (Sprint 4 PhotoEvent 起正式化)

**现状 S0.B**: 节点结构已加 `provenance_stream_id` 字段, 填值是 Sprint 1+ 的事。节点仍由 `identify_object` / `manage_episode` 直接创建 (bypass L0), 和 §3.3 一样走"先 L0 再 L3"的过渡期规则。

---

## 4. 禁止清单 (一句话规则)

| # | 禁止 | 为什么 |
|:--|:-----|:-------|
| 1 | 绕过 `EventEnvelope` 直接 `redis.xadd` 到 `parrot.events.log` | Schema 漂移, 破坏 replay |
| 2 | 在 L1 BB 存 list/history | BB 是"现在", 查历史走 L0 |
| 3 | 跳过 `provenance_stream_id` 创建 L2-B / L3 节点 (Sprint 1+) | 断链, Reverse Provenance Expansion 失效 |
| 4 | 用 `TASK` layer 发高频事件 | 淹 Gemini |
| 5 | 在 `payload` 里塞非 JSON 可序列化对象 (datetime, numpy array) | XADD 编码失败 |
| 6 | 同一 `kind` 字符串分散多处用 | 重构噩梦; 集中定义在 `shared/constants.py::EVENT_KIND_*` (Sprint 1 再做) |

---

## 5. 关联文件

- `src/parrot/shared/event_log.py` — `EventEnvelope` 定义 (S0.A)
- `src/parrot/shared/constants.py::STREAM_EVENT_LOG` — Stream key 常量
- `src/parrot/dsg/l2b_types.py` — `provenance_stream_id` 字段 (S0.B)
- `src/parrot/dsg/l1_5_protocol.py` — L1.5 detection schema (S0.7)
- `sprint0_preflight.md §1` — 设计背景与前沿调研对齐
- `sprint0_preflight.md §10.1` — 为什么 L2-B SemanticNode 还是 dataclass (deferred)
- `ar_feature_implementation_plan.md` Sprint 1 S1.E `obs_log` — 首个写入端预计位置

---

## 6. 演进计划 (何时升 ratified)

- **升 tentative → ratified** 条件: Sprint 1 S1.E `obs_log` 真实写入 + L1 BB 订阅投影跑通 + 3 闸门过。
- **当前状态** (2026-04-22): Sprint 0 S0.A/B/C/7 schema 全部锁定, 写入端零实现, 投影端零实现。
