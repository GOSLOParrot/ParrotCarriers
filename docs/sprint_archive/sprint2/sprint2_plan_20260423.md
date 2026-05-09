---
status: ratified
status_note: "Sprint 2 的开工承诺。Round 1 深度审计后的取舍 + 事实对齐 + T 任务清单。每项 T 独立 commit。Sprint 2 收口前本文件视为合同, 不随手改。"
last_reviewed: 2026-04-23
---

# Sprint 2 执行计划 — Intent 层 + 两轴模式 + Ingest 过滤器

> 日期: 2026-04-23
> 定位: **Round 1 理解 + 审计 + 取舍的最终固化**. 后续 Round 2 按 §6 T 任务清单逐个 commit。
> 关联:
> - `sprint1_completion_report_20260422.md` (起跑线, §6 隐患 + §7 硬约束)
> - `ar_feature_vision.md §3.5 / §3.6` (三层意识 + 两轴模式, ratified)
> - `ar_feature_implementation_plan.md §Sprint 2` (任务来源, 本计划对其做了修正, 详见 §6)
> - `audit_identify_object_no_screenshot_20260420.md §1.2` (体感红线)

---

## §0 TL;DR (一句话)

Sprint 2 给 GOSLO 装"条件反射 + 自主神经": 把 Sprint 1 已装好的 (感知→visual_state→嘴巴) 从"只会说"升级为"会自主改 BB 让身体跟上"; 具体是 **PerceptionSupervisor** (A10 健康 + 视觉长期异常 → 自动切 video_tier/dsg_mode) + **HandleIntent** (router 第 4 叶) + **Ingest 过滤器层** (Gemini 转写回灌 L2-B, A10 关了也能喂 DSG) 三件事, 全走 **BB 直写 + L0 审计旁路 + Injector 用现有 C3/C4 通报**, 不开第五条 Gemini 通道。

---

## §1 核心问题 — Sprint 1 的自知闭环断在哪, Sprint 2 怎么续

Sprint 1 把**感知神经**装完: Unity/AR/RPC 信号 → `session/visual_state` → Injector C3/C4 + `SOUL_CONSTRAINTS` → GOSLO 嘴巴. 但三处明显断档:

1. **无自主动作**: `bb_schema.BB_KEYS` 已承诺 `session/video_tier` / `session/dsg_mode` 由 `brain.perception_supervisor` 写, **模块未建**; `router.route` 碰 `layer=="intent"` 硬 raise. 结果: 视觉 DEGRADED 10s 没人会去降 video_tier 省流量, A10 宕机没人会把 dsg_mode 切到 GEMINI_VISION.
2. **无语义回灌**: A10 关闭时 DSG_GEMINI_VISION 应该靠 Gemini 转写喂 L2-B, 但 `dsg/ingest/` 只有 Sprint 0 落地的 base.py + Observation schema, **没有任何具体过滤器实现**, 更没有 "Gemini 转写 → text_source_filter → L2-B upsert" 这条链.
3. **无 Supervisor 审计 trail**: Sprint 1 `STREAM_EVENT_LOG` 空着, 没任何 EventEnvelope 被 XADD 过. 等于 L0 是占位. Sprint 2 第一个真实 producer 应该是 Supervisor.

Sprint 2 把这三断一次续上, **不越界**: Intent 层只改 BB (身体变化由 Injector 代理通报), 过滤器只产 Observation (L2-B 提交由独立 runner 完成), Supervisor 只决策 (降档/升档的判据与 hysteresis 在这一家).

---

## §2 Gemini 四通道在 Sprint 2 的用法变化

与 Sprint 1 的 `sprint1_completion_report §2.1` 表对比, Sprint 2 **不新增**通道, 只扩 C2/C3 的**触发条件**, 和加一类新的 "旁白式" C3 body:

| 通道 | API | Sprint 1 触发 | **Sprint 2 新增触发** |
|:----|:----|:-------------|:---------------------|
| C2 | `update_instructions(text)` | Memory/Scene 整块刷 (inject_memory / inject_scene) | **+** Scene 切换 + 跨档 video_tier (VIDEO_FULL↔VIDEO_OFF) 要重建 soul_constraints 导入段 |
| C3 | `update_chat_ctx(role=user, "[状态] ...")` | visual_state drift + RPC reject | **+** `session/video_tier` 变化 → `[状态] 视频现在省流量, 我靠你的话记事` **+** `session/dsg_mode` 变化 → `[状态] 我的视觉辅助休息了, 靠你来描述吧` |
| C4 | `generate_reply(instructions=...)` | BLOCKED / PAUSED→ACTIVE 回归打招呼 | **+** 升档回满时的"欸我又能看清啦" (heavy=True) — 降档**不**走 C4, 避免每次 A10 抖动都打断对话 |
| C1 / C5 / C6 | — | 不变 | 不变 |

**关键纪律** (来自 Sprint 1 §7.3): C2 频率 < 1/min; C4 省着用 (Sprint 2 只在"跨档回满"一处触发, 不在降档用). 若 Supervisor 1 分钟内触发多次 C2 级调整, 合并到最后一次刷.

---

## §3 Intent 层设计

### §3.1 事件源 (Perception Supervisor 观察什么)

| 输入 | 读法 | 触发决策 |
|:----|:----|:--------|
| `session/visual_state` (BB) | 1Hz 轮询 + hysteresis 计时 | DEGRADED 持续 ≥ `VISUAL_DEGRADE_GRACE_S`(默认 15s) 且当前 tier=FULL → 降到 GEMINI_ONLY |
| A10 health (HTTP ping) | 独立 30s cadence | 失败 ≥ `A10_DOWN_GRACE_S`(默认 30s) → dsg_mode 降档; 恢复 ≥ `A10_UP_STABLE_S`(默认 60s) 且当前 turn 已结束 → 升档 |
| `session/scene` (BB, 未来 Sprint 4) | 变化即触发 | Scene 切换时重置为该 Scene 默认组合 (本 Sprint 只留占位, 不真切) |
| 用户 `set_video_tier` tool (Sprint 2 起有效) | RPC | 手动覆盖, 覆盖后 5min 内不自动降/升 |

### §3.2 决策函数签名 (纯函数)

```python
def decide(
    visual_state: VisualState | None,
    a10_healthy: bool,
    now: float,
    hysteresis: HysteresisState,      # 内部计时状态, 函数返回时被更新
    current: tuple[VideoTier, DsgMode],
    manual_override_until: float,      # 手动覆盖的解除时刻
) -> tuple[VideoTier, DsgMode] | None:  # None = 保持现状
```

纯函数的好处: 单元自证零成本 (Sprint 1 T6 思路), hysteresis 内部状态走结构体而不是 BB, 与 `fusion` 保持同一风格。

### §3.3 写 L0 还是直写 BB — Sprint 2 的答案

**两条都写, 职责不同**:

- **直写 BB** 是**主通路** — Supervisor 调用 `bb.set("session/video_tier", new_tier)` 立即生效, Injector / mode_controller / Unity RPC 在 <10ms 内看到. **BB 是单一真相源**, 这一条不商量.
- **XADD EventEnvelope 到 L0** 是**旁路审计 + 跨进程钩子** — 每次 Supervisor 做决策 (含 None=no-op), 一条 `kind="intent.tier_change" layer=INTENT` 的 envelope 入 `parrot.events.log`. 负载是**决策结果**指纹: `{from: (FULL, DSG_FULL), to: (GEMINI_ONLY, DSG_GEMINI_VISION), cause: "a10_down_30s", hysteresis: {...}}`。
- **不走 Gemini 通知** — Intent 的本分是"自主改 BB", 通知交 Injector 代理 (§2 已约定 C3)。

### §3.4 Arbiter 需要不需要

**不需要**, Sprint 2 砍掉。理由: Sprint 2 只有一个 Intent 源 (Supervisor), 没有并发"两家同时想改 video_tier"的局面。手动 `set_video_tier` RPC 通过 `manual_override_until` 就能压住 Supervisor, 不用 ResourceLock。Arbiter (body 通道互斥) 留给 Sprint 3 S3-Arbiter, 等 HandleReflex/HandleIntent/Nanobot 真正抢 fly_to 时再上。

### §3.5 HandleIntent 节点的真实职责

看审计才搞清楚: Supervisor **不经过 router** (它直接写 BB + XADD L0). HandleIntent 存在的意义:
1. **兜底**: 将来若别的 caller 主动 `scheduler` 推送 `layer=intent` 事件, 能被 route 成 `intent_committed` 而不 raise。
2. **对称**: router Selector 的 4 叶 (Reflex / Intent / Nanobot / BrainDirect) 让三层时间尺度在代码里能看见, 不是 2+1 的尴尬形状。

所以 HandleIntent 的实现极简: 检查 `event.get("layer") == "intent"` → 写 `route_result = {"destination": "intent_committed"}` → SUCCESS。Sprint 2 **不**让它做任何 BB 写入, BB 写入始终是发起方 (Supervisor / tool) 的责任。

---

## §4 两轴模式状态机 (VideoTier × DsgMode)

### §4.1 5 条 ALLOWED_COMBOS 的触发表

| # | 组合 | 进入条件 | 退出条件 |
|:-:|:-----|:--------|:--------|
| C1 | `VIDEO_OFF + DSG_TEXT_ONLY` | 用户 `set_video_tier(OFF)` | 用户恢复 / 5min manual_override_until 过期后 Supervisor 判定 |
| C2 | `VIDEO_GEMINI_ONLY + DSG_GEMINI_VISION` | **默认启动组合** + A10 ping 失败 ≥30s | A10 ping 恢复 ≥60s 且 turn 结束 |
| C3 | `VIDEO_FULL + DSG_FULL` | A10 健康 + 手动触发 / 启动时健康 | A10 down ≥30s → 退到 C2 |
| C4 | `VIDEO_FULL + DSG_GEMINI_VISION` | 过渡态, 自动触发 "A10 down 但视频还没降" (仅在 C3→C2 中间出现一次 tick 级) | 下一 tick 立即退到 C2 |
| C5 | `VIDEO_BURST + DSG_FULL` | **Sprint 2 不实现**, 留给 Sprint 4 S4.C 相机模式触发 | 同上 |

Sprint 2 只真实启用 C2/C3 + 手动 C1, 其他 **占位**。

### §4.2 Hysteresis (抖动抑制)

| 信号 | grace period | 阈值判定 |
|:----|:------------|:--------|
| A10 down | 30s | 连续 3 次 HTTP ping 失败 |
| A10 up | 60s **且** 等当前 turn 结束 | 连续 2 次 HTTP ping 成功 |
| visual_state=DEGRADED 长期 | 15s | `_compute_visual_state` 连续返回 DEGRADED |
| 手动覆盖 | 5min | `set_video_tier` 后 `manual_override_until = now + 300` |

**状态放在 Supervisor 里** (不写 BB), 与 Sprint 1 fusion 的无状态纯函数分工一致. `fusion` 做瞬时合成, `hysteresis` 做时间窗口, 两家互不交叉.

**降档立即, 升档等 turn 结束**:
- 降档: `decide()` 返回新组合, Supervisor 立即 `bb.set + XADD`, Injector 下一 poll 看到并 C3 通报。
- 升档: `decide()` 返回新组合, 但 Supervisor 先检查 `tick/cognitive_state` (Sprint 2 暂用 `None → 假装 turn 结束`, Sprint 3 补), 不是 speaking 才真切.

### §4.3 Unity 动态调参 vs 重建 Track — Sprint 2 的答案

**Sprint 2 不真动 Unity 编码器**. 理由:
- `ARVideoPublisher.cs` 当前 `PublishTrack(options)` 的 `MaxBitrate/MaxFramerate` 在 publish 后不可变, 动态调要么 re-publish track (Sprint 1 §4.6 说过 Play/Stop <30s 就会 ICE 抢占), 要么用 LiveKit SDK 的 SetBitrate (Unity SDK 版本支持不稳).
- Sprint 2 的**关键价值是 Intent 决策闭环 + 话术跟得上**, Unity 侧先**ACK 接收**就足以让 Python 完整自证。
- 真实的动态 tier 切换 (re-publish Track) 留给 Sprint 3 S3.A 做 AR 重建时顺手补。

Sprint 2 的 Unity 做法:
1. `VideoTierReceiver.cs` (新) 注册 RPC `setVideoTier`, 返回 `{"status":"ok"}` + 打 log + 保存当前 tier 到实例字段.
2. `VideoStateReporter.cs` 补 TRACK_MUTED 上报 (Sprint 1 §6.7 遗留)。
3. 真实 re-encoding 逻辑在脚本里留 `TODO(Sprint 3)` + 注释说明原因。

---

## §5 Ingest 过滤器分工

### §5.1 5 个 filter 的职责

| filter | 输入 | 输出 Observation 源 | 置信度起点 | 备注 |
|:-------|:-----|:-------------------|:----------|:-----|
| `text_source_filter` | free text (Gemini 转写 / 用户文字) | GEMINI_ORAL / USER_EXPLICIT | TENTATIVE, 30s 内复述升 CONFIRMED | 抽"名词短语 + 位置介词"; 30s/60s 时间窗状态在 runner 里 |
| `tool_result_filter` | `identify_object` tool 命中的结构化 dict | IDENTIFY_OBJECT | 直接 CONFIRMED | 权威最高, 可覆盖同名 gemini_oral 节点 |
| `user_tag_filter` | Obsidian 双链同步消息 (已在 `dsg/triggers/ssot_enrichment_trigger.py`) | USER_TAG_OBSIDIAN | CONFIRMED | `obsidian_uuid` 钉死, 永不 GHOST |
| `cv_track_filter` | A10 `SensorFrame` (L1.5) | CV_A10 | 高但要 ReID 确认 | **Sprint 2 只留骨架**, 真实 A10 P3 再接 |
| `gemini_transcript_extractor` | LiveKit session event `conversation_item_added` / `user_input_transcribed` | 喂给 `text_source_filter` | — | 不是 IngestFilter, 是 adapter |

### §5.2 Observation 的流向 (Q4 的正式答案)

```
filter.process_text/process_frame()
    → Observation (Pydantic frozen DTO)
    → ingest_runner.commit_observation(obs)
        ├─ 写 L2-B: L2BGraph.upsert_node(SemanticNode)
        ├─ 写 Graphiti: 延后 (Sprint 4 写物体图库时再做)
        └─ 写 obs_log: log_obs_event("ingest_commit", 1, {...})
```

**不走 L0 Stream**: Observation 是"语义候选", 量大, 走 L0 会把 `parrot.events.log` 降格成日志 (kickoff §D 反模式)。

### §5.3 Gemini 转写订阅点 (已查代码)

`agent.py::_attach_gemini_transcript_to_terminal` 已经挂了 `@session.on("user_input_transcribed")` 和 `@session.on("conversation_item_added")` 两个钩子, 目前只 print 和 log. Sprint 2 T7 的做法: **扩展这个函数** (不新建钩子), 在 print 之后把文本喂给 `gemini_transcript_extractor.feed_transcript(text, role)`, extractor 内部调 `text_source_filter.process_text → ingest_runner.commit_observation`. 优点: 保留现有终端调试输出, 同时多走一条回灌链。

### §5.4 mode_controller 的启用集合

```python
FILTER_SETS: dict[DsgMode, frozenset[str]] = {
    DsgMode.DSG_TEXT_ONLY:     frozenset({"tool_result_filter", "user_tag_filter"}),
    DsgMode.DSG_GEMINI_VISION: frozenset({"text_source_filter", "tool_result_filter", "user_tag_filter"}),
    DsgMode.DSG_FULL:          frozenset({"text_source_filter", "tool_result_filter", "user_tag_filter", "cv_track_filter"}),
    DsgMode.DSG_SENTINEL_AUX:  frozenset({"text_source_filter", "tool_result_filter", "user_tag_filter"}),  # P4
}
```

`mode_controller` 从 BB `session/dsg_mode` 读当前 mode, 用上表决定哪些 filter 的 `process_*` 被真正调用. Sprint 2 的 `ingest_runner` 先查 enabled set, 再 dispatch. 不要写"禁用的 filter 也跑但丢弃结果"那种浪费。

---

## §6 T 任务清单 (Round 2 开工按此顺序)

每 T 独立 commit, message 格式 `[S2.T<n>] <一句话>`. 单元/smoke 自证, 不写集成测试。

| T | 动作 | 文件 | Commit 约 |
|:-:|:-----|:-----|:----------|
| **T1** | `brain/perception_supervisor.py` 骨架: class + `start_background()` + 启动期写 DEFAULT_COMBO 到 BB + `_attach_supervisor` | 新 `src/parrot/brain/perception_supervisor.py` | `[S2.T1] perception_supervisor 骨架 + 默认组合写入` |
| **T2** | Supervisor 核心: A10 health stub + `decide()` 纯函数 + hysteresis 结构体 + `_control_loop` 异步循环 | 同上扩 | `[S2.T2] 两轴决策函数 + hysteresis` |
| **T3** | `scheduler/nodes.py::HandleIntent` + `router.py` 改 4 叶 Selector + 删 `NotImplementedError` + `shared/parrot_actions.py` 保持 (layer 字段已在 `shared/event_log.EventLayer`) | `nodes.py` / `router.py` | `[S2.T3] HandleIntent + router 4 叶` |
| **T4** | Supervisor 每次决策 XADD 到 `STREAM_EVENT_LOG` (EventEnvelope, layer=INTENT) + `log_obs_event("intent_decision", 2, ...)` | supervisor 扩 | `[S2.T4] Intent 决策 L0 审计 + obs_log` |
| **T5** | `context_injector` 扩: `_classify_video_tier` / `_classify_dsg_mode` + `_WATCHED_BB_KEYS` 加两 key + 跨档 C2 重刷 (VIDEO_OFF) | `src/parrot/brain/context_injector.py` | `[S2.T5] Injector 扩 tier/mode 分类` |
| **T6** | `dsg/ingest/text_source_filter.py` / `tool_result_filter.py` / `user_tag_filter.py` / `cv_track_filter.py` 四个具体 filter (最后一个骨架) | 新 4 文件 | `[S2.T6] 4 个 Ingest filter 具体实现` |
| **T7** | `dsg/ingest/gemini_transcript_extractor.py` + `agent.py::_attach_gemini_transcript_to_terminal` 扩 feed_transcript | 新 1 文件 + agent.py 扩 | `[S2.T7] Gemini 转写回灌链` |
| **T8** | `dsg/ingest/runner.py` (Observation→L2-B upsert + obs_log) | 新 1 文件 | `[S2.T8] Ingest runner + L2-B 提交` |
| **T9** | `dsg/mode_controller.py` (BB 订阅 + 启用集合 + runner 绑定) | 新 1 文件 | `[S2.T9] mode_controller 按 DsgMode 切过滤器` |
| **T10** | `brain/tools/_rpc_bridge.py::set_video_tier_rpc` + `brain/tools/set_video_tier.py` function_tool + Unity `VideoTierReceiver.cs` | `_rpc_bridge` 扩 + 新 tool + 新 cs | `[S2.T10] set_video_tier RPC 双端` |
| **T11** | `shared/bb_schema.py` 移出 `global/soul_constraints` + `soul.py` 注释说明 (Sprint 1 §6.1 (b)) | bb_schema.py / soul.py | `[S2.T11] soul_constraints 双身份收口` |
| **T12** | Unity `VideoStateReporter.cs` 补 TRACK_MUTED 事件 (Sprint 1 §6.7 / R5) | VideoStateReporter.cs | `[S2.T12] TRACK_MUTED 上报` |
| **T13** | `brain/agent.py` 挂 Supervisor + active_context 更新 + `sprint2_completion_report_20260423.md` | agent.py / active_context / completion | `[S2.T13] Sprint 2 收尾` |

**估算**: T1-T13 约 1-1.5 天工作量. 每个 T 结束自证是"跑 `python -m parrot.brain.agent dev` 不 crash + 相关模块 import 正常", 真机端到端由用户自管。

### §6.1 T 之间的依赖图

```
T1 ─ T2 ─ T4 ─┐
              ├─ T13 收尾
T3 ───────────┤
T5 ───────────┤
              │
T6 ─ T8 ─ T9 ─┤
 │           │
 T7 ─────────┤
             │
T10 ─────────┤
T11 ─ T12 ───┘
```

T1-T4 是 Supervisor/Intent 主干 (必须先完成). T5 依赖 T1 (Injector 要能读 tier/mode BB). T6-T9 是 Ingest 子系统 (T8 依赖 T6, T9 依赖 T6+T8, T7 依赖 T6). T10/T11/T12 是并行杂项. T13 最后。

---

## §7 明确砍掉的事 (避免过度工程)

| 砍掉项 | 理由 | 接收方 |
|:------|:----|:------|
| Arbiter / ResourceLock | Sprint 2 只有 Supervisor 一个 Intent 源, 无并发 | Sprint 3 (body 通道真抢时) |
| Unity 真实动态编码 (re-publish / SetBitrate) | LiveKit SDK 版本相关 + 与 AR 重建冲突 | Sprint 3 S3.A |
| A10 真实健康端点 | A10 未部署 | Sprint 2 只做 stub (可配 URL, 无 URL 时恒返回 healthy 或 unhealthy 看 env) |
| Graphiti 写入 (Ingest → Graphiti) | Sprint 4 identify_object 升级一并做 | Sprint 4 S4.B |
| VIDEO_BURST 模式 | 摄影玩法要才有意义 | Sprint 4 S4.C |
| Scene 真实切换 (DESKTOP↔AR_HANDHELD) | AR 工程未开始 | Sprint 3 S3.B |
| soul_constraints 热更新 / 按 dsg_mode 分档 | 现有 4 档 VisualState 已经够; 新增要跟代码实证 | Sprint 4+ 按需 |
| turn 快照摘要 (Voyager 式) | 当前 Injector 事件驱动够用, 加 turn 摘要会和 C3 C4 争配额 | P4 备选 |

---

## §8 Sprint 3/4 预留 (留 assert + docstring, 不留 TODO)

| 预留点 | 文件 | 形式 |
|:------|:-----|:----|
| Supervisor A10 真端点 | `perception_supervisor.py::_check_a10_health` | env `PARROT_A10_HEALTH_URL` 读, 无则 log + 返 unhealthy (保守) |
| HandleIntent 的 BB 写入 | `scheduler/nodes.py::HandleIntent` | docstring 明确"Sprint 2 不写 BB, 所有 BB 修改由 Supervisor 自持" |
| mode_controller 的 turn 边界 | `dsg/mode_controller.py` | Sprint 3 加 `tick/cognitive_state` 后再启用"升档等 turn" |
| re-publish Track | `ARVideoPublisher.cs` / `VideoTierReceiver.cs` | C# 里 `// TODO(Sprint 3): actually re-encode` |
| Graphiti 提交 | `dsg/ingest/runner.py` | docstring 标 "Sprint 4 S4.B 激活" |

---

## §9 已知隐患 (Sprint 1 §6 继承 + Sprint 2 自审新发现)

### 继承 (Sprint 1 §6 中 Sprint 2 解决的):

- **§6.1 soul_constraints 双身份** → T11 选 (b), 从 BB_KEYS 移出
- **§6.3 VisualState hysteresis** → Supervisor 的 `VISUAL_DEGRADE_GRACE_S=15` 窗口覆盖 (fusion 保持纯函数, hysteresis 在 Supervisor)
- **§6.4 C3 role=user 可能被转写** → 真机 smoke 用户自测, 出问题回退到 C2 局部 append
- **§6.7 TRACK_MUTED 未上报** → T12 补
- **§6.9 _classify_rpc_ack 脱敏** → Sprint 2 顺手用 `_RPC_ALIAS` dict 把 `fly_to` → "飞那边" 这类映射, 不是硬任务

### 新发现:

- **§9.N1 Supervisor 与 Injector 都是 BB poller, 1Hz 级叠加** — Supervisor 决策循环 + Injector poll 都在 agent 进程, 1Hz 两个异步 task. 目前无问题 (CPU 开销可忽略). 若未来扩到更多 BB 轮询者 (≥5), 需改为统一 BB 事件总线 (py-trees 原生不支持, 要自己在 `open_bb_client` 外加一层 pub/sub). Sprint 2 不做。
- **§9.N2 Supervisor XADD 失败会丢审计** — `STREAM_EVENT_LOG` 的 xadd fire-and-forget, Redis 挂时静默丢. 和 `obs_log` 一致的降级哲学, 但 Intent 决策比 obs 更关键. Sprint 2 接受, Sprint 3 如果引入多 agent 合并流再做持久化保证。
- **§9.N3 Gemini 转写回灌有死循环风险** — 若 Injector C3/C4 推了一条 `[状态] ...`, Gemini 是否会 "转写出来" 喂回 text_source_filter → L2-B 写入 → 触发下一轮 Injector? Sprint 2 T7 在 `gemini_transcript_extractor` 里**加一层前缀过滤**: 如果转写文本以 `[状态]` / `[Gemini·` 开头, 直接丢弃, 不喂 filter. 这是最简防线。
- **§9.N4 Ingest runner 线程安全** — L2BGraph 的 `upsert_node` 不是线程安全 (rustworkx PyDiGraph). Sprint 2 的 runner 全走 asyncio (同一 loop, 单线程), 没问题. 若 Sprint 3 引入多进程消费者, 要加锁。
- **§9.N5 HandleIntent 过早成型风险** — Sprint 2 HandleIntent 实现只做"接收 + 打标 intent_committed", 不做实际决策. 万一 Sprint 3 需要让 Intent 事件产生 BB 修改 (比如外部命令), 要重新审视职责边界. 现用 docstring 锁死: "本节点不做 BB 写入, 发起方自持"。
- **§9.N6 Ingest filter 顺序无约束** — 同一条转写文本可能被多个 filter 处理 (text_source + tool_result). Sprint 2 用"源优先级" (USER > IDENTIFY_OBJECT > GEMINI_ORAL) 在 runner 的 upsert 逻辑里消解冲突, 不在 filter 层做. filter 是纯函数, 不互相协作。

---

*本计划维护*: Sprint 2 收口时在每 T 旁边加 ✅ + commit hash; 不动计划本体. 增删 T 要先征得用户点头。
