---
status: accepted
adr_id: ADR-003
supersedes: ""
superseded_by: ""
date: 2026-04-22
deciders: "用户 + AI (P2.5 讨论期决定, 写入 ar_feature_vision.md §3.5)"
---

# ADR-003: 三层意识 (Reflex / Intent / Task) 调度分治

## 1. 背景

讨论 AR 摄影玩法时, 发现"鹦鹉停手" (REFLEX, ms 级) 和"Brain 决定去拍照" (TASK, 分钟级) 如果都走同一条 Gemini Live 对话通道, 会出现:
- 反射延迟被 LLM 对话时钟拖慢 (200ms → 2s)
- Gemini 被高频事件淹 (每次手指移动都通知一次, 等于在他耳朵里塞蝉)

参照 CTHA 和 NVIDIA GR00T N1.6 的 System-1/2 分层, 结合本项目实际路径 (Unity 硬件 + Bus + Gemini + Nanobot), 收敛三层。

## 2. 决策

**三层意识分治**, 每层有明确的时钟尺度、通知边界和写入规则:

| 层 | 时钟 | 典型动作 | 通知 Gemini? | 写 L0 layer |
|:---|:-----|:---------|:-----|:-----|
| **Reflex** | ms | finger perch, fly_to cursor, 张手抓, 撞墙反弹 | **否** | `REFLEX` |
| **Intent** | s-min | video_tier 降档, soul_constraints 更新, dsg_mode 切 | **否** | `INTENT` |
| **Task** | min+ | Nanobot 派工, tool 调用结果, 拍照归档 | **是** (通过 ContextInjector) | `TASK` |

关键约束:
- **Reflex 永远不走 Nanobot**, 直接 body-channel RPC 到 Unity (低延迟)
- **Intent 永远不通知 Gemini**, 只改 Blackboard, Gemini 按需 query
- **Task 的 Gemini 通知走 ContextInjector** (不是直接 push), 降噪
- L0 Event Stream (`EventEnvelope.layer`) 按这三层打标, 消费者自己过滤

## 3. 备选方案

| 方案 | 放弃原因 | 备注 |
|:-----|:---------|:-----|
| 一层直出 Gemini | 被高频事件淹 / 延迟拖慢 | 最初直觉设计, 实测不能用 |
| 两层 System-1/2 | Intent 和 Task 糅在一起, 容易写串 | 纸面漂亮, 代码不好分 |
| 四层 (细拆 Reflex 为 Reactive + Motor) | 当前 Unity 硬件路径没那么多层级 | 假复杂度, 不实装 |

## 4. 后果

**好**:
- Reflex 延迟得到保护 (本地通道, 不经云端 LLM)
- Gemini 不被高频事件淹, 对话质量稳定
- L0 Event layer 标签清晰, 回放/审计按层过滤直接写

**坏 / trade-off**:
- 写代码时必须选对 layer, 选错 (例如把 finger perch 标 `TASK`) 会立刻污染 Gemini context
- 三层之间仍可能有"跨层需求" (例如 Reflex 累积 → 升 Intent → 再升 Task), 需要**升层策略**单独设计 (本 ADR 不管)

**未知 / 需监控**:
- Reflex 累积升 Intent 的合适阈值是什么? (例: 连续 3 次 fly_to 失败 → 升 Intent 通知 Brain 降 tier)
- ContextInjector 的 Task 通知节流策略 (Sprint 1+ 落地时设计)

## 5. 关联

- 设计文档: `ar_feature_vision.md §3.5`
- 代码: `src/parrot/shared/event_log.py::EventLayer` (S0.A), `src/parrot/scheduler/bt_router.py`
- 相关 ADR: ADR-001 (Blackboard 是 Intent 层的主要落点)
- 验证闸门: Sprint 1 S1.F 三级调度收尾时 Gate 2

## 6. Review 点

- 如果 P4 新增"物理仿真身体"层 (如腿部关节), 看是否要 Motor 层从 Reflex 拆出
- 如果 Gemini 换成更便宜/更快的模型, Intent 能否重新合并进 Gemini Live?
- 升层策略 (Reflex → Intent → Task) 首次实装时, 写一个 ADR-00X 记录
