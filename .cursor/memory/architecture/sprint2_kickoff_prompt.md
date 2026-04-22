---
status: tentative
status_note: "Sprint 2 下一轮对话的启动 prompt. 用户在新 chat 里直接复制 §A §B 两段做 Round 1 和 Round 2, 中间一回合用户确认后再进 Round 3 写代码. 本文件本身不被 agent 执行, 它是'给下次 agent 看的指挥棒'."
last_reviewed: 2026-04-22
---

# Sprint 2 启动 Prompt — Intent 层 + 两轴模式 + Ingest 过滤器

> 日期: 2026-04-22
> 定位: **下一轮对话的启动说明书**. 在新 chat 里按 §A → 等用户 → §B → 等用户 → §C 三段接力, 模仿 Sprint 1 的 "Round 1 理解 → Round 2 固化 → Round 3 写代码" 三阶节奏.
> 为什么要拆三段: 上下文到 200k 会被自动压缩, 理解等于白理解. **固化必须独立一步落文件, 不能省**.

---

## 0. 新 chat 启动前 —— 用户先贴这段开场白

```
这是 Sprint 2 的开工. 规则:
1. 本轮(Round 1) 只读不写, 读完 5 份必读文档, 回答 6 个问题. 不要动代码.
2. 我点头后 Round 1.5 你把本轮所有理解 + 取舍 + T 任务清单固化到
   `.cursor/memory/architecture/sprint2_plan_20260423.md`, 打 status: ratified.
3. 然后 Round 2 才开始写代码, 每个 T 独立 commit.
4. 到 190k 你自己主动提醒我, 我们就把进度固化一次, 不要等自动压缩.
5. 整个 Sprint 只写代码和必要的设计文档, 不写测试 (我自管), 不写 ADR.

现在开始 Round 1, 照 §A 的 prompt 执行.
```

---

## A. Round 1 prompt — 只理解, 不写代码 (复制给新 agent)

```
# Sprint 2 启动 Round 1 — 只理解, 不写代码

我们刚完成 Sprint 1 (自知底座 + 视频流骨骼 + Gemini 四通道体感). 现在要进入
Sprint 2, 目标是给 GOSLO 装上"条件反射 + 自主神经":

    让 GOSLO 能自己做决策 (Intent 层) — 比如看到 visual_state 降档就主动
    把 video_tier 调低省流量; A10 服务挂了就自动切 DSG_GEMINI_VISION 模式
    只靠 Gemini 转写抽名词.

    这不是"新的功能层", 是把 Sprint 1 的'感知'闭环到'行动'. Router 的
    NotImplementedError("INTENT") 就是这一步要填上的坑.

## 本回合任务 (只读不写)

按顺序读下面 5 份文档, 然后回答 6 个问题. **不要动任何代码文件**.

### 必读 (按顺序)

1. @.cursor/memory/architecture/sprint1_completion_report_20260422.md
   — 重点看 §3 (BB 写入者地图) / §6 (遗留问题与隐患) / §7 (交给 Sprint 2 的硬约束)
2. @.cursor/memory/architecture/ar_feature_implementation_plan.md
   — 重点看 §Sprint 2 整段 (S2.A / S2.B / S2.C) 和 §25 依赖关系图 Sprint 2 段
3. @.cursor/memory/architecture/ar_feature_vision.md
   — 重点看 §3.5 三层意识 + §3.6 两轴模式 + §3.3 视频流三层门控
4. @.cursor/memory/architecture/audit_identify_object_no_screenshot_20260420.md §1.2
   — 体感红线, Sprint 2 的 Intent 层"自主改 BB 不告诉 Gemini"必须守这条
5. @src/parrot/scheduler/router.py + @src/parrot/scheduler/nodes.py +
   @src/parrot/brain/context_injector.py + @src/parrot/brain/vision/state.py +
   @src/parrot/shared/tiers.py + @src/parrot/shared/bb_schema.py
   — Sprint 2 的大部分任务是扩这些现有文件, 必须先看现状

### 回答以下 6 问 (每题 3-5 行, 不要长篇)

Q1. 用你自己的话说明 Sprint 2 要解决的**核心问题**. 不要复述任务单, 说
    "Sprint 1 的自知闭环到哪断了, Sprint 2 怎么续上".

Q2. `session/video_tier` / `session/dsg_mode` 的 writer 字段 bb_schema 写的是
    `brain.perception_supervisor`, 但这个模块不存在. Sprint 2 应该新建这个
    模块, 还是改 bb_schema 的 writer 名? 给你的判断和理由 (不要模糊)。

Q3. Intent 层的决策 (比如"把 video_tier 从 FULL 降到 GEMINI_ONLY") 要不要
    通过 EventEnvelope 走 L0 Stream (`parrot.events.log`)? 还是直接写 BB 即可?
    两者取舍 (事件可追溯 vs 延迟)。

Q4. Ingest 过滤器 (S2.B) 读 SensorFrame 输出 Observation, 这个 Observation
    的流向是: (i) 写 L2-B SemanticNode? (ii) 走 L0 Stream? (iii) 还是两者都?
    说依据 (sprint0 schema 设计 + sprint1 completion §3)。

Q5. S2.C5 "降档时 Injector 注入 system message"  — 但 Sprint 1 已经发现
    role=system 在 Gemini realtime 下被静默吞. Sprint 2 怎么改这条?
    走 C2 (整块 update_instructions) 还是 C3 (role=user) 还是 C4 (speech)?

Q6. 看完必读后, 有没有任务单里**写得不对 / 含糊 / 会踩坑**的地方?
    坦诚说, 没有就说"没有".

## 硬规则 (整个 Sprint 2 适用)

- 只写代码和必要的设计文档, 不写测试 (用户自管), 不写 ADR
- 遇到"扩现有还是新建"的抉择, 优先扩现有
- Schema V1 已锁死, Sprint 2 不要动 shared/*.py 和 dsg/l1_5_protocol.py 的接口
  (除非 Sprint 1 completion §6 明文要求)
- Sprint 1 的"体感红线 (audit §1.2)" 和 "Gemini 四通道硬约束 (sprint1_completion §7.3)"
  在 Sprint 2 继续适用, 不能被新需求打破
- 每个子任务 (T1 / T2 / ...) 做完独立 commit, message 格式 `[S2.T1] ...`

回答完 6 问, 停在这里等我确认.
```

---

## B. Round 1.5 prompt — 固化 Sprint 2 计划 (用户确认 Round 1 后贴这段)

```
# Sprint 2 Round 1.5 — 把理解固化到文件

我点头了. 现在请你照 Sprint 1 的节奏, 把你 Round 1 的所有理解 + 取舍 +
T 任务清单一次性固化到:

    .cursor/memory/architecture/sprint2_plan_20260423.md

结构参考 sprint1_plan_20260422.md, 必须包含:

1. §0 TL;DR 一句话
2. §1 Sprint 2 的"核心问题" — 从 Sprint 1 completion §6 §7 长出来
3. §2 Gemini 四通道 在 Sprint 2 的用法变化 (对比 Sprint 1 表)
4. §3 Intent 层设计 —
   - 事件源 (Perception Supervisor 观察什么)
   - 决策函数 (输入 BB 状态, 输出 BB 修改 或 空)
   - 写 L0 vs 直写 BB 的选择 (Q3 的答案)
   - Arbiter 需要不需要, 不需要的话 Sprint 3/4 再上 (写清楚)
5. §4 两轴模式 (VideoTier × DsgMode) 的状态机图 —
   - 5 条 ALLOWED_COMBOS 怎么触发
   - 降档/升档 hysteresis (Sprint 1 §6.3 的隐患)
   - Unity 动态调参 vs 重建 Track 的选择
6. §5 Ingest 过滤器分工 —
   - 5 个 filter 各自职责
   - Observation 流向 (Q4 的答案)
   - Gemini 转写订阅点 (现在的 agent.py 挂不挂)
7. §6 T 任务清单 T1-TN —
   - 每条写清楚 status / 动作 / 文件 / Commit 格式
   - 像 Sprint 1 那样每条 0.2-0.5 天大小
8. §7 Sprint 2 明确砍掉的事 (避免过度工程)
9. §8 Sprint 3/4 预留 (哪些留 assert + docstring)
10. §9 已知隐患 (从 Sprint 1 §6 继承 + 自己新发现的)

固化后打 `status: ratified`, `last_reviewed: <今天>`, commit 信息
`docs(sprint2): 固化 Sprint 2 执行计划 (Round 1 理解产物)`.

同步修 .cursor/memory/active_context.md 的 "当前阶段" 指针到
"Sprint 2 执行中 — Intent 层 + 两轴模式 + Ingest 过滤器",
开工收口指向这份新的 sprint2_plan.

停在这里等我点头. 我点头后才进 Round 2 写代码.
```

---

## C. Round 2 勘探 —— 固化后才写代码

Round 1.5 固化完 Sprint 2 计划后, 用户会简单说一句 "按你固化的做"。届时 agent 应:

1. 把自己的 todo list 按 sprint2_plan §6 的 T1-TN 建好, T1 status=in_progress
2. 照着 T-任务单逐个 commit, 每个 T 独立
3. 在 context 接近 190k 时主动提醒用户 "接近 190k, 要不要先把进度固化"
4. Sprint 2 收口时写 `sprint2_completion_report_<date>.md` + 更新 active_context

**不要**自己增删 T 或修改 sprint2_plan (除非用户明说), 计划是承诺。

---

## D. 给下次 agent 的三个心法 (不是规则, 是心法)

- **"体感红线"大于"结构美感"**. Sprint 2 会有冲动把 Intent 层做得很学院派 (py-trees 双树 / 多层 Selector / DAG 仲裁). 先用最简实现跑通一条链, 再美化。
- **Gemini 的知觉是被你刷出来的**. 它不会自己"观察"BB, 它看到的就是你 `update_chat_ctx` 送进去的那些字. Sprint 2 每加一个 Intent 决策, 都要问 "这个决策要不要让 Gemini 知道? 通过哪条通道?"
- **L0 Stream 的诱惑**. 很多事件像 L0 候选 (每次 video_tier 降一次就 XADD 一条?), 但 L0 是"单一真相源", 过载会让它变成日志。判据: 下游真的有投影消费者吗? 没有就别写。

---

## E. 风险清单 (从 Sprint 1 completion §6 挑出 Sprint 2 必答的)

| 编号 | 源 | Sprint 2 必须解决 | 方式 |
|:----:|:---|:----------------|:----|
| R1 | §6.1 soul_constraints 双身份 | ✅ | Intent 热更新决定后自然收尾 |
| R2 | §6.3 VisualState 抖动无 hysteresis | ✅ | Intent 降档一定要带 hysteresis, 不然会被抖到死循环 |
| R3 | §6.4 C3 role=user 可能被转写 | ✅ | 真机 smoke 必测, Sprint 2 Intent 通报加多时要先验证 |
| R4 | §6.9 RPC 名称直接漏给用户 | ⚠️ 可选 | Sprint 2 顺手修, 不是硬任务 |
| R5 | §6.7 TRACK_MUTED 未上报 | ✅ | Sprint 2 Unity 侧补 |

其余 §6.2/§6.5/§6.6/§6.8 推 Sprint 3/4 或保持现状。
