# 复杂度审计 · MVP 分级 · 过度设计检查

> 生成日期: 2026-02-24
> 核心问题:
> 1. MVP 任务有没有清晰分级？
> 2. 这么多 if-else 设计会不会导致性能下降？
> 3. 有没有过度设计？哪些可以砍掉？

---

## 1. 诚实的复杂度审计

### 1.1 我们设计了多少东西？

截至目前的 19 篇文档中：

| 指标 | 数量 | 评价 |
|:-----|:-----|:-----|
| ADR (架构决策) | 28 个 | **偏多** — Phase 0 通常 5-10 个就够 |
| 设计的类/结构 | ~290 个定义 | **偏多** — MVP 不需要这么多类 |
| 核心结论 | 32 条 | 信息密度高，但对实施来说信息过载 |
| 文档总页数 | ~2000 行设计文本 | **显著偏多** — 还没写一行生产代码 |

### 1.2 if-else 密度分析

把所有设计中的条件分支列出来：

```
L1 层:
  StabilityGate          → 4 个 Tier (4 分支)
  FrameQualityChecker    → blur 阈值 (1 分支)
  PhoneOrientationDetector → 4 种朝向 (4 分支)
  CameraObstructionDetector → 3 种遮挡 (3 分支)
  CompassHealthMonitor   → 3 种故障 (3 分支)
  LabelBuffer            → 投票逻辑 (1 分支)
  PositionBuffer         → 阈值过滤 (1 分支)
  ActivityThrottle       → 3 级降频 (3 分支)
  DiscovererPromptStrategy → 场景词汇 (3 分支)
  DarkFrameDetector      → 亮度阈值 (1 分支)
                          ─────────────────────
                          合计: ~26 个条件分支

L2-A 层:
  NodeState 转换         → 6 种状态 × ~4 种转换 (~24 种)
  TTL 策略               → 6 种节点类型 × 4 种超时 (~24 种)
  EvidenceAccumulator    → 8 种证据 + 不对称逻辑 (~12 分支)
  FrustumCheck           → 1 分支
  ExpectationChecker     → 4 种偏离类型
  ReID 触发条件          → 4 触发 + 4 不触发 (8 条件)
  ON_SURFACE 推断        → 高度交叉验证 (2 分支)
                          ─────────────────────
                          合计: ~75 个条件分支

L2-B 层:
  注意力计算             → 新奇/衰减/聚焦 (3 个公式)
  Salience 分级          → 4 级
  显著性过滤             → 阈值判断 (1 分支)
                          ─────────────────────
                          合计: ~8 个条件分支

L3 层:
  触发器过滤             → attention 阈值 (1 分支)
  ContextInjection 选择  → 6 种注入类型
                          ─────────────────────
                          合计: ~7 个条件分支

异常处理:
  13 种异常 × 各自的检测+降级  → ~26 个分支

其他:
  LabelAuthority         → 5 级权威 (5 分支)
  NodeConfidence 6维     → 6 个计算函数 (~18 分支)
  NavigationConstraints  → 3 种停靠判断 (3 分支)
                          ─────────────────────
总计: ~180+ 个条件分支
```

### 1.3 性能影响: 不是问题

**if-else 本身不影响性能。** 原因：

```
实际性能开销对比:

SAM2 推理 (1帧):      ~30ms GPU     ← 这是大头
YOLO-World (1帧):     ~20ms GPU     ← 这是大头
DINOv2 (1次):         ~10ms GPU     ← 按需
Gemini API (1次):     ~200-500ms    ← 网络延迟

180 个 Python if-else:  <0.01ms CPU  ← 完全可忽略

if-else 的 CPU 开销约占总开销的 0.001%。
即使写 1000 个 if-else 也不会成为瓶颈。
```

**所以性能不是问题。真正的问题是别的。**

---

## 2. 真正的问题: 实施复杂度

### 2.1 问题不是 if-else 性能，而是...

| 真正的问题 | 影响 | 严重性 |
|:-----------|:-----|:-------|
| **认知负担** | 开发者（你）需要记住 180+ 条规则来写代码 | **高** |
| **调试困难** | 状态组合爆炸: 6 状态 × 4 Tier × 13 异常 = ~312 种情况 | **高** |
| **测试覆盖** | 不可能为 312 种情况都写测试 | **高** |
| **耦合风险** | 一个模块改了阈值，可能影响另一个模块的行为 | **中** |
| **过早优化** | 很多异常处理（镜面反射、罗盘失效）在 MVP 中可能永远不会遇到 | **高** |
| **设计膨胀** | 每次讨论都增加新的条件分支，没有人砍过 | **高** |

### 2.2 过度设计的证据

诚实地说，以下设计在 MVP 阶段**过度了**：

| 设计 | 来自 | 为什么过度 | MVP 是否需要 |
|:-----|:-----|:-----------|:-----------|
| 6 维置信度模型 | doc 18 | 6 个维度各有公式，实际 MVP 用 1-2 个就够 | ❌ 简化 |
| 13 种异常处理矩阵 | doc 19 | MVP 只需处理 3-4 种常见异常 | ❌ 砍到 4 种 |
| EvidenceAccumulator 不对称逻辑 | doc 19 | 确认/否定的精细区分是 Phase 2 的优化 | ❌ 先用简单版 |
| ExpectationChecker 4 种偏离 | doc 19 | MISSING 是核心, 其余 3 种是锦上添花 | ⚠️ 只留 MISSING |
| CompassHealthMonitor | doc 18 | 罗盘功能本身是 P1, 监控器是 P2 | ❌ |
| PhoneOrientationDetector | doc 19 | 聪明但 MVP 不需要 | ❌ |
| 5 个 Graphiti 分区 | doc 13 | MVP 只需 1 个分区就够 (episodic) | ⚠️ 砍到 2 |
| Observer 拆分为 4 个 | doc 13 | MVP 一个 Observer 就行 | ❌ |
| py-trees 行为树 | doc 14 | MVP 用简单 priority if-else 就行 | ❌ 先简化 |
| 4 通道资源锁 | doc 14 | MVP 身体通道互斥就够 | ❌ |
| FrustumCheck | doc 19 | 精巧但 MVP 先不区分负面证据条件 | ❌ |
| BehaviorMode Flag 叠加 | doc 14 | MVP 只有一个基础模式 | ❌ |
| YOLO-World 场景化词汇 | doc 19 | MVP 用固定词汇表 | ❌ |
| Nanobot 后台任务 | doc 13 | Phase 3 | ❌ |
| 细粒度 Gemini 裁切识别 | doc 19 | Gemini 自己看视频帧就够 | ⚠️ Phase 2 |

---

## 3. MVP 必须做 vs 可以砍掉

### 3.1 三层金字塔: 必须 / 应该 / 以后

```
                    ▲
                   ╱ ╲
                  ╱ M1 ╲         MVP-必须: 不做就不能用
                 ╱ 8 项  ╲       (Phase 1-2 必须交付)
                ╱─────────╲
               ╱    M2     ╲     MVP-应该: 不做体验差但能用
              ╱   12 项     ╲    (Phase 2-3 交付)
             ╱───────────────╲
            ╱      M3         ╲   以后再做: 锦上添花
           ╱     很多项        ╲  (Phase 3+ 或永远不做)
          ╱─────────────────────╲
```

### 3.2 M1: 必须做 (8 项, 不做就不能用)

| # | 功能 | 最简实现 | 复杂度 |
|:--|:-----|:---------|:-------|
| 1 | **LiveKit Agent 骨架** | AgentSession + Gemini Realtime | 低 |
| 2 | **DataChannel 协议** | JSON 指令/遥测双向通道 | 低 |
| 3 | **Unity AR 基础** | AR Foundation + 鹦鹉模型 + 基础动画 | 中 |
| 4 | **StabilityGate (简版)** | 只分 3 级: Lost / Moving / Stable | 低 |
| 5 | **L1 视觉管线 (简版)** | SAM2 追踪 + YOLO-World 发现 (不做 ReID) | 中 |
| 6 | **L2-A 空间图 (简版)** | RustworkX 图 + ObjectNode + SurfaceNode (无 Zone/Hand) | 中 |
| 7 | **fly_to Tool** | 查 L2-A 位置 → DataChannel body_cmd | 低 |
| 8 | **APP 生命周期** | OnApplicationPause → DataChannel → Tier 0 | 低 |

**注意: M1 不包括 ReID、Graphiti、注意力机制、行为树。**
Phase 1 的鹦鹉只需要：能说话 + 能看到物体 + 能飞过去。

### 3.3 M2: 应该做 (12 项, 不做体验差)

| # | 功能 | 比 M1 增加了什么 | Phase |
|:--|:-----|:---------------|:------|
| 1 | **DINOv2 ReID** | 物体跨帧一致性 (不会重复建节点) | 2 |
| 2 | **remember Tool** | Graphiti 单分区写入 | 2 |
| 3 | **Graphiti 基础** | 1 个分区 (episodic), 基本读写 | 2 |
| 4 | **网络降级** | 连接质量监听 + 降码率 | 2 |
| 5 | **节点状态 3 种** | ACTIVE / OCCLUDED / LOST (不需要 EXPECTED/ANCHORED) | 2 |
| 6 | **帧质量检查** | Laplacian 模糊检测 | 2 |
| 7 | **L2-B 简版** | RustworkX 图 + 简单新奇度分 (不做完整注意力) | 3 |
| 8 | **场景折叠** | 基础的 fold/unfold (不做预期偏离) | 3 |
| 9 | **自主微行为** | 空闲时随机小动画 | 2 |
| 10 | **鹦鹉平面行走** | 在 AR 平面上走动/跳舞 | 2 |
| 11 | **手势响应** | 张手→飞来 (简单版, 不做意图确认) | 2 |
| 12 | **ActivityThrottle** | 无变化时降低扫描频率 | 2 |

### 3.4 M3: 以后再做 (Phase 3+)

以下全部推迟, 不在 MVP 范围:

```
推迟:
  - 6 维置信度模型 → 用简单的 confidence 单值
  - EvidenceAccumulator → 用简单的 "看到 3 帧 = 确认"
  - ExpectationChecker → 先不做预期偏离
  - EXPECTED 状态 + 幽灵节点管理 → 先不做跨会话恢复
  - 持久化锚点 → 先不做
  - 罗盘/方位感知 → 先不做
  - 13 种异常处理 → 只做 "Lost/模糊/暗" 3 种
  - 标签权威链 → 用 YOLO 标签就行
  - 细粒度 Gemini 裁切识别 → Gemini 看整帧就行
  - py-trees 行为树 → 用简单 priority if-else
  - 4 通道资源锁 → body 互斥就行
  - Observer 拆分 4 个 → 1 个 Observer
  - Graphiti 5 分区 → 1 个分区
  - Nanobot 后台任务 → 不做
  - BehaviorMode 模式叠加 → 只有基础模式
  - SceneProfile 场景特化 → 固定参数
  - 节点 TTL 差异化 → 统一 TTL
  - L2-B 注意力机制完整版 → 简单新奇度分
  - ZoneNode / HandNode → 先不建模
```

---

## 4. 重新审视: 设计到底合不合理？

### 4.1 哪些 if-else 是合理的

| 设计 | 合理? | 原因 |
|:-----|:------|:-----|
| StabilityGate 分级 | **非常合理** | 核心门控, 不做就模糊帧烧 GPU |
| 帧质量检查 | **合理** | 一行代码, 省大量 GPU |
| NodeState 状态机 | **合理** | 物体状态是 DSG 的核心概念 |
| 标签投票 | **合理** | 简单滑动窗口, 解决真实的标签跳变问题 |
| 位置阈值过滤 | **合理** | 简单阈值, 减少 90% 的无意义事件 |
| Tier 控制处理器启停 | **合理** | 这就是 StabilityGate 的意义 |

### 4.2 哪些 if-else 是过早优化

| 设计 | 过早? | 原因 |
|:-----|:------|:-----|
| 13 种异常矩阵 | **是** | 先实现再遇到问题再加 |
| 6 维置信度 | **是** | 用单个 confidence 浮点数就够 |
| 不对称证据累积 | **是** | 先用对称的, 遇到问题再优化 |
| FrustumCheck | **是** | 精巧但 MVP 不需要 |
| CompassHealthMonitor | **是** | 罗盘功能都还没接 |
| YOLO 场景化词汇 | **是** | 固定词汇表先跑起来 |

### 4.3 有没有更好的架构？

**当前架构的方向是正确的**，问题不在架构，在实施粒度：

```
架构层面 (方向正确, 不需要改):
  ✅ 四层 DSG 分层 — 职责清晰
  ✅ LiveKit 做 infra — 成熟可靠
  ✅ RustworkX 做图 — 性能好
  ✅ Gemini 做认知 — 能力强
  ✅ StabilityGate 门控 — 解决真实问题
  ✅ DataChannel 前后端通信 — 标准方案

实施粒度 (需要简化):
  ❌ 节点类 5 种 → MVP 只需 2 种 (Object + Surface)
  ❌ 置信度 6 维 → MVP 用 1 个 float
  ❌ 异常处理 13 种 → MVP 只处理 3 种
  ❌ Graphiti 5 分区 → MVP 用 1 个
  ❌ 触发器 4 层过滤 → MVP 用 2 层
```

---

## 5. 建议: Phase 1 的实际实施方案

### 5.1 极简 MVP (Phase 1 第一天就能跑)

```python
# Phase 1: 整个 L1+L2 管线只需要这么多代码

class SimpleTier(IntEnum):
    LOST = 0
    UNSTABLE = 1
    STABLE = 2

class SimpleGate:
    def update(self, tracking_state, velocity) -> SimpleTier:
        if tracking_state == "None":
            return SimpleTier.LOST
        if velocity > 0.5:
            return SimpleTier.UNSTABLE
        return SimpleTier.STABLE

class SimpleNode:
    uuid: str
    label: str          # YOLO 给的标签
    position: tuple     # ARCore 投影的位置
    confidence: float   # 单个数字, 0-1
    last_seen: float    # 上次看到的时间
    is_active: bool     # 看得到 vs 看不到

class SimpleGraph:
    nodes: dict[str, SimpleNode]
    surfaces: dict[str, ARPlane]
    
    def add_or_update(self, track_id, label, position): ...
    def mark_lost(self, uuid): ...
    def get_nearby(self, position, radius) -> list: ...

class SimpleL1:
    gate: SimpleGate
    tracker: SAM2Tracker
    discoverer: YOLOWorldDiscoverer
    
    async def process(self, frame, telemetry):
        tier = self.gate.update(telemetry)
        if tier == SimpleTier.LOST:
            return None
        tracks = await self.tracker.track(frame)
        if tier == SimpleTier.STABLE:
            new = await self.discoverer.discover(frame, tracks)
            tracks.extend(new)
        return tracks
```

**就这么多。** 没有:
- 没有 LabelBuffer (标签跳变? 先忍着)
- 没有 PositionBuffer (位置抖动? 先忍着)
- 没有 EvidenceAccumulator (简单 3 帧确认)
- 没有 NodeState 6 种状态 (只有 active/lost)
- 没有异常检测 (手机倒了? 先不管)
- 没有 ReID (物体重复? 先忍着)

### 5.2 什么时候加回复杂度？

**遇到真实问题时**。这是关键原则。

```
Phase 1: 跑起来
  → 发现标签老是跳 → 加 LabelBuffer ✓
  → 发现物体位置抖 → 加 PositionBuffer ✓  
  → 发现 GPU 白烧 → 加 ActivityThrottle ✓
  → 发现模糊帧崩溃 → 加 FrameQualityChecker ✓

Phase 2: 基本可用
  → 发现物体重复建节点 → 加 DINOv2 ReID ✓
  → 发现来电崩溃 → 完善 APP 生命周期 ✓
  → 发现弱网卡死 → 加网络降级 ✓
  → 发现物体消失没反应 → 加简单的 ExpectationChecker ✓

Phase 3: 体验提升
  → 发现记忆太乱 → 加 Graphiti 分区 ✓
  → 发现跨会话不记得 → 加持久锚点 ✓
  → 发现注意力平淡 → 加完整注意力机制 ✓
  → 发现行为优先级乱 → 加行为树 ✓
```

### 5.3 文档 11-19 的价值

**这些文档不是浪费。** 它们是:

```
✅ 预研地图 — 知道遇到问题时往哪个方向走
✅ 设计储备 — 不需要临时设计, 拿来用就行
✅ 风险识别 — 知道 180 个可能的坑在哪里
✅ 技术选型 — RustworkX/Graphiti/ARCore 的能力边界已经清楚

❌ 不是实施计划 — 不应该一次性全部实现
❌ 不是 MVP 需求 — 大部分是 Phase 3+ 的细节
```

**正确的使用方式**: 把它们当成**字典**而非**清单**。遇到问题时来查，不是照着从头到尾实现。

---

## 6. 最终结论

### 6.1 回答你的三个问题

**Q1: MVP 任务有没有分级？**
> 之前有 P0/P1/P2 但分散在不同文档且不断膨胀。本文重新整理了三层金字塔: M1(8项必须) / M2(12项应该) / M3(推迟)。

**Q2: if-else 会导致性能下降吗？**
> 不会。180 个 if-else < 0.01ms，而 SAM2 一帧 30ms。性能瓶颈永远在 GPU 模型推理和网络延迟，不在 Python 条件分支。

**Q3: 有没有过度设计？**
> **有。** 诚实地说，大约 60% 的设计是 MVP 不需要的。核心架构方向正确 (四层 DSG + LiveKit + StabilityGate)，但很多细节 (6 维置信度、13 种异常、不对称证据) 是 Phase 3 才需要的优化。

### 6.2 建议的行动

```
1. 立刻: 按 M1 的 8 项开始写代码 (Phase 1)
2. 原则: 先能跑, 遇到问题再查文档加复杂度
3. 文档: 11-19 作为设计储备字典, 不是实施清单
4. 心态: "先跑起来的烂代码 > 永远不跑的完美设计"
```
