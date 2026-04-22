---
status: ratified
status_note: "Sprint 1 的事实记录 — 代码已落地, 单元/smoke 级别自证, 真机端到端 smoke 留给用户自管。只描述'既成事实', 不含未验证设计。"
last_reviewed: 2026-04-22
---

# Sprint 1 完成报告 — 自知底座 + 视频流骨骼 + Gemini 四通道体感

> 日期: 2026-04-22
> 作者: Agent (Composer) + 用户决策
> 定位: **事实记录**, 不是计划, 只记"Sprint 1 实际交付了什么 + 留了什么坑给 Sprint 2"
> 关联文档:
> - `sprint0_completion_report_20260422.md` (Schema V1 的起跑线)
> - `sprint1_plan_20260422.md` (Round 2 开工前的上下文固化件, T1-T10 的唯一 checklist)
> - `ar_feature_vision.md` §3.3 / §3.5 / §3.6 (视频流三层门控 / 三层意识 / 两轴模式)
> - `audit_identify_object_no_screenshot_20260420.md` §1.2 (体感红线 —— Sprint 1 的灵魂)

---

## 0. TL;DR (三行说完)

Sprint 1 **只做了一件事**: 把"视频流生命周期 + GOSLO 自知"从产地 (Unity `OnApplicationPause`) 一直串到嘴边 (Gemini Live C3/C4), 中间穿过 `session/visual_state` 这个单一真相源, 让 GOSLO 说话符合身体能力。

- **10 个 T commit** (`d9f8c32` → `18fedd6`) + 2 个 doc commit (`03d7954` 开工固化, `060dbbe` 收尾台账) + 1 个草稿清理 (`670a01b`)
- **核心突破**: Gemini Live 四通道的真实行为 (C3 role=system 静默吞) 先验证再编码, 不是事后打补丁
- **刻意不做**: Intent 层路由 / LiveKit 路上层门控 / 消费端过滤 — 全部推到 Sprint 2, Router 开头 `NotImplementedError` 兜底, 早 caller 拿硬错误比静默误路由好

---

## 1. 范围演化 — 为什么 S1.A-G 变成了 T1-T10

用户在 Sprint 1 Round 1-1.5 做了两次关键校正:

| 阶段 | 触发 | 变化 |
|:-----|:----|:-----|
| **原始 S1.A-G 任务单** | `ar_feature_implementation_plan.md §Sprint 1` | 7 子任务 (blackboard 分域 / 意识 dispatcher 独立文件 / Intent 层 / Arbiter / Soul 约束 / context injector 扩) |
| **Round 1 审视** | Agent 问 Q3 "dispatcher 真的要独立文件吗" | 拍板合进 `context_injector`, 不建 `brain/consciousness/` 子目录 |
| **Round 1.5 体感对齐** | 用户 "GOSLO 行动符合体感 + audit §1.2 协作体系是共通的" | Gemini Live 四通道表重做, 确认 C3 必须 role=user 前缀 `[状态]`; Intent 层无具体事件可路由, 推 Sprint 2 |
| **Round 2 开工发现** | `git log` 看到 `d9f8c32/f2a8ecf/ea4d412` 已有 S1.A1-A4 提交 | T1-T4 就地对齐为 HEAD 既成事实, 从 T5 接着写 |
| **T1-T10 落地** | Round 2 按固化的 sprint1_plan | 每个 T 独立 commit, 单元/smoke 自证, 不写集成测试 (验收代码用户自管) |

**结论**: Sprint 1 的"拆整为 10" 是两态机实证 —— "整片 S1.A-G" 在 Round 1 被体感红线切碎, 重编成 10 个 0.2-0.5 天的 T, 每个 T 是一个可 rollback 的承诺。

---

## 2. 交付物清单 (按 T 对 commit 对文件)

| T | commit | 新建 / 改动 | 核心契约 |
|:-:|:-------|:-----------|:---------|
| T1 | `d9f8c32 [S1.A1]` | `scheduler/blackboard.py` 加 `open_bb_client(name, writer)` | py-trees Client 按 `BB_KEYS.writer` 分 READ/WRITE, 越界写 py-trees 原生 AttributeError |
| T2 | `670a01b chore(sprint0)` | `brain/vision/__init__.py` + 收 Sprint 0 `snapshot.py`/`visual_match.py` 草稿 | schema 对齐但 RPC `captureSnapshot` 未建, Sprint 4 S4.C 才真跑 |
| T3 | `f2a8ecf [S1.A2-3]` | `brain/telemetry_receiver.py` 扩 3 个 writer 路径 | 写 `tick/body_state` / `tick/ar_tracking_state` / `transient/hand_gesture` (后者 bb_schema writer 从 `brain.gesture_source` 改为 `brain.telemetry_receiver`) |
| T4 | `ea4d412 [S1.A4]` | `brain/tools/_rpc_bridge.py` 扩 | 每次 RPC 出结果写 `tick/last_rpc_ack = {ok, rpc, reason, detail, ts}`; `set_scene` 写 `session/scene` |
| T5 | `a24ef89 [S1.T5]` | 新 `unity/ParrotDev/Assets/Scripts/LiveKit/VideoStateReporter.cs` + 新 `brain/vision/state.py` 入境 handler + `brain/agent.py` attach | Unity `OnApplicationPause` → RPC `onVideoDegraded(reason, ts)` → `session/visual_reason` (VisualStateReason 13 值) |
| T6 | `6cdc462 [S1.T6]` | `brain/vision/state.py` 加 `_compute_visual_state` + `recompute_visual_state` + telemetry_receiver 调用 | `session/visual_state` (ACTIVE/DEGRADED/PAUSED/BLOCKED) 由 `{visual_reason, ar_tracking_state}` 融合, 精确优先 → AR 回退 → 默认 ACTIVE / UNKNOWN 时 DEGRADED (保守) |
| T7 | `357c525 [S1.T7]` | `brain/context_injector.py` 大改 | BB 1Hz 轮询 + `_decide_layer(key, old, new)` 返 `(layer, body, heavy)`; 层③ heavy 走 C4 `generate_reply`, 轻走 C3 `update_chat_ctx(role=user, "[状态] ...")`; 每 key 3s 去重; 启动期 sentinel 吃掉首观察 flood |
| T8 | `66180fe [S1.T8]` | `brain/soul.py` 加 `SOUL_CONSTRAINTS` dict + `render_visual_constraints()`; Injector 直接用 constraint 当 C3 body | 4 档 VisualState × {allow/deny} 语言规则和信号同通道送达, 避免"BB 改了 Gemini 却以为没改" |
| T9 | `47a968f [S1.T9]` | `shared/constants.py` 加 `STREAM_OBS_LOG`; 新 `brain/obs_log.py::log_obs_event()`; Injector 每次决策都审计 | fire-and-forget XADD `parrot.obs_log` (MAXLEN 10k), 所有层都记, Layer-1 静默也记 |
| T10 | `18fedd6 [S1.T10]` | `scheduler/router.py::BTRouter.route` 入口 assert; `shared/event_log.py::EventLayer` docstring | `layer=='intent'` → `NotImplementedError("Sprint 2 S2-Intent")`, 早 caller 拿硬错误 |

### 2.1 Gemini Live 通道映射表 (Sprint 1 落地版, 源于 livekit/agents#4875/#3386 + Vertex Live best practices)

| 通道 | API | Sprint 1 用法 | 调用点 |
|:----|:----|:-------------|:------|
| C1 | 自然轮 + `generate_reply()` | 主语音, 不触发通知 | 用户对话 |
| C2 | `session.update_instructions(text)` | Persona / Scene / Memory 整块刷 | Injector `inject_memory` / `inject_scene` |
| C3 | `session.update_chat_ctx(ctx)` role=user 前缀 `[状态]` | 层③轻 — visual_state drift / RPC reject | Injector `_push_status_user` |
| C4 | `session.generate_reply(instructions=...)` | 层③重 — BLOCKED 触发 / PAUSED→ACTIVE 打招呼 | Injector `_push_speech` |
| C5 | `RoomOptions(video_input=True)` | Gemini 云端看 track, 我们取不到帧 | `agent.py` 启动 |
| C6 | `@function_tool` return str | tool 同步反馈 | 既有 fly_to / identify_object / ... |

**关键发现**: Gemini realtime 下 `role=system` 在 `update_chat_ctx` 被静默吞掉 (官方 bug, 未修), Sprint 1 全线统一 role=user + `[状态]` 前缀。这条不是设计选择, 是业内踩过的硬约束。

---

## 3. Blackboard 实际写入者地图 (Sprint 1 收口)

| key (scope/name) | writer 模块 (`bb_schema.py`) | 实际写入点 | Sprint 1 状态 |
|:-----------------|:---------------------------|:----------|:-------------|
| `global/user_profile` | `brain.memory` | 未接 | 占位, Sprint 2+ |
| `global/soul_constraints` | `brain.soul` | **静态 `SOUL_CONSTRAINTS` dict, 未真写 BB** | ⚠️ 矛盾: bb_schema 声明了但 Sprint 1 只作为模块常量读, Sprint 2 要么改 bb_schema 说明"Module constant, not BB-written", 要么真写 BB |
| `session/scene` | `brain.tools._rpc_bridge` (T4 确认) | `set_scene()` tool | ✅ |
| `session/video_tier` | `brain.perception_supervisor` | **模块未建** | ⏸️ Sprint 2 S2.C2 |
| `session/dsg_mode` | `brain.perception_supervisor` | **模块未建** | ⏸️ Sprint 2 S2.C2 |
| `session/visual_state` | `brain.vision.state` | T6 `recompute_visual_state()` | ✅ |
| `session/visual_reason` | `brain.vision.state` | T5 `handle_video_degraded()` | ✅ |
| `tick/body_state` | `brain.telemetry_receiver` | T3 | ✅ |
| `tick/head_state` | `brain.telemetry_receiver` | **没 emitter, 声明占位** | ⏸️ 无上游, Sprint 3/4 加 HMD pose 才有 |
| `tick/ar_tracking_state` | `brain.telemetry_receiver` | T3 | ✅ |
| `tick/last_rpc_ack` | `brain.tools._rpc_bridge` | T4 | ✅ |
| `transient/hand_gesture` | `brain.telemetry_receiver` | T3 | ✅ |
| `transient/...` (其他) | 各模块 | 按需, 大多未触发 | ⏸️ |

---

## 4. Sprint 1 **明确不做** 的事 (和 Sprint 2 前/后的交接)

| 砍掉的项 | 理由 | 接收方 |
|:--------|:----|:------|
| 独立 `brain/consciousness/dispatcher.py` | 职责和 context_injector 重合, 拆出去反增 indirection | 已合进 `context_injector._decide_layer` |
| `brain/consciousness/soul_constraints.py` | 静态表, 不值得独立文件 | 已写进 `soul.SOUL_CONSTRAINTS` |
| S1.F `HandleIntent` 节点 | Sprint 1 没有具体 Intent 事件源 (VisualState→video_tier 要靠 PerceptionSupervisor 才成立) | Sprint 2 S2.C2 + S2-Intent |
| S1.G `BodyChannelLock` / Arbiter | 无并发事件, 纸面 Lock 无价值 | Sprint 2 S2 后半 |
| Soul 约束热更新 + C2 全量重写 persona | 初次接触就上热路径风险大 | Sprint 2 Intent 层接管 |
| LiveKit 路上层门控 (Unity 停推) | 对体感收益极小, 拉低系统复杂度 | §9.1 G1.1 P3 储备 |
| Python 消费端视频过滤 (模糊/锐度) | 属于两轴模式 DSG_FULL 的职责 | Sprint 2 S2.B |

---

## 5. 验证与自证状态

### 5.1 已自证 (单元级, sanity script)

- T6 fusion 精确优先 + AR 回退 + idempotence (`_t6_sanity.py` 临时脚本, 验证后删)
- T7 `_decide_layer` 9 个 case (包括 BLOCKED/PAUSED/DEGRADED/ACTIVE 的 4 向跳变 + RPC 成功/失败 + visual_reason 不双报) (`_t7_sanity.py` 临时脚本)
- T8 `render_visual_constraints` 4 档 + classify 嵌入 constraint body (`_t8_sanity.py`)
- T10 Router `layer=='intent'` raise + 正常 reflex 路由不受影响 (一次性 smoke)

### 5.2 未验证 (留给用户真机)

- **真机端到端**: Unity `OnApplicationPause` → Brain 收 RPC → BB 写 visual_reason → fusion → Injector C4 → Gemini 真的开口说"我被挡住了, 能把挡着的东西挪开吗"
- **回切恢复**: App 后台 >30s → 回来 → Injector 说"视觉恢复, 我又能看清了" (C4 heavy)
- **Gemini 可见性**: role=user `[状态]` 消息会不会被 Gemini **转写**回前端让用户看见 (这是 role=user 的副作用, 业内 SVA / Voyager 的经验说不会, 但在 Gemini Live 上需验证)
- **obs_log Redis 流写入**: `parrot.obs_log` 是否真的有 entry (需要 `XRANGE parrot.obs_log - +`)

### 5.3 刻意不写的测试

任务单明文: "test 我自己设计"。Sprint 1 只写了 3 个临时 sanity 脚本 (都已 git 外删除), 没有持续集成测试套件。

---

## 6. 遗留问题与隐患 (Sprint 2 开工前请先读这段)

### 6.1 `global/soul_constraints` 双身份矛盾 【中等】

- `bb_schema.py` 声明 writer = `brain.soul`, 但 T8 的 `SOUL_CONSTRAINTS` 是**模块级 dict**, 从未真写 BB
- 后果: 如果未来有别的模块 `client.get("global/soul_constraints")` 会 KeyError
- 两选一 (Sprint 2 开工前决定):
  - (a) `soul.py` 加一次 `bb_client.set("global/soul_constraints", SOUL_CONSTRAINTS)` 在模块导入时
  - (b) `bb_schema.py` 把该 key 注释标 "Module constant for read-only reference, not BB-written" 或干脆移出 BB_KEYS
- 选 (b) 更干净 (约束表天然不需要跨进程共享), 但要等 Sprint 2 Intent 层决定要不要热更新

### 6.2 `tick/head_state` 无 emitter 【低】

- bb_schema 声明了但上游 Unity 没发这个 event
- Sprint 1 telemetry_receiver 没 handler
- 无消费者, 暂不影响, Sprint 3/4 加 HMD pose 时再填

### 6.3 VisualState 抖动无滞后 (hysteresis) 【中等】

- 真机场景: AR tracking LIMITED↔TRACKING 快速反复 → `session/visual_state` DEGRADED↔ACTIVE 快速反复 → Injector C3 / C4 被打满
- Sprint 1 的 3s per-key 去重是 **Injector 层**, **不是 fusion 层** —— fusion 本身是无状态的函数
- Sprint 2 建议: `brain/vision/state.py` 加 2s 窗口内至少稳定 N 次才切, 或 DEGRADED→ACTIVE 要求 3s 连续 ACTIVE
- 真机 smoke 出现抖动投诉时再补, 不要过早优化

### 6.4 C3 role=user 可能被 Gemini 转写为用户消息 【需验证】

- `update_chat_ctx(role=user, ...)` 语义是"GOSLO 以为用户说过这句话"
- Gemini Realtime 可能把它当上下文吃 (期望行为), 也可能当本轮 user turn 触发回复 (意外行为)
- 业内经验: SVA / Voyager 说法是"当上下文吃", 不会触发额外 turn, 但我们没在 Gemini Live 上真机验证
- 如果真机发现 GOSLO 会对 `[状态] 视觉状态=blocked ...` 做出"呃, 怎么了"的追问, 需要降级到 C2 局部 append 或改用 "GOSLO 内心旁白: XXX" 句式

### 6.5 obs_log 只在 asyncio loop 里生效 【低】

- `log_obs_event` 靠 `asyncio.get_running_loop() + create_task` 异步写
- 同步上下文 (比如将来某个 sync BB writer) 调用 → 静默丢弃
- 当前所有实际调用者 (Injector `_dispatch`) 都在 asyncio, 不影响
- 如果 Sprint 2 Intent 层是同步节点里决策, 要改用 redis pipe 或主动 asyncio.run (会破坏 event loop)

### 6.6 `brain/vision/snapshot.py` + `visual_match.py` 草稿未跑通 【低】

- 已 git add (T2 收口), schema 对齐
- 依赖 `captureSnapshot` RPC 的 Unity handler (`SnapshotService.cs` + `ParrotRpcHandler` 注册) **都不存在**
- 调用会 3s 超时返错
- 归属: Sprint 4 S4.C (相机模式), Sprint 2/3 identify_object 升级要**写注释说这条链还没通**

### 6.7 Unity `VideoStateReporter.cs` 只做了 OnApplicationPause 【设计如此】

- AR tracking 从 DataChannel `ar_tracking_state` 事件路走 (telemetry_receiver T3), 这里不重复
- 亮度方差 / 锐度检测推 P3
- 视频 Track 被 Unity 主动 mute/unmute → 应该补 `visual_reason=TRACK_MUTED`, 没做 (Sprint 2 做)

### 6.8 Injector `_bb_poll_loop` 和 telemetry_receiver 的 `recompute_visual_state` 双调用 【刻意冗余】

- push (telemetry 写完 ar_tracking_state 立刻 fuse) + pull (Injector 1Hz 兜底 fuse)
- idempotent, 重复调用只在状态变时写 BB, 没副作用
- 如果观察到"ar_tracking 很久不变但 visual_state 却抖", 可以去掉 pull 侧; 暂时保留冗余增鲁棒

### 6.9 `_rpc_bridge` 写 `tick/last_rpc_ack` 触发 Injector C3 "RPC 被拒" 的脱敏 【中等】

- 现在的消息体: `RPC fly_to 被 Unity 拒 (out_of_bounds): 详细...`
- 内部 RPC 名称直接漏给用户, 有泄露内部实现的感觉
- Sprint 2 建议: 在 `_classify_rpc_ack` 里把 `rpc="fly_to"` 映射为面向用户的话术, 比如 "我想飞过去但飞不过去, 好像出边界了"
- 不是 Sprint 1 硬任务, 先记

---

## 7. 交给 Sprint 2 的三个硬约束 (Sprint 2 开工前请必看)

### 7.1 Router 对 INTENT 的假设

`BTRouter.route` 开头会在 `event.layer == "intent"` 时 raise. Sprint 2 第一动作应该是:
1. 新建 `scheduler/nodes.py::HandleIntent` py-trees 节点 (或等价物)
2. 修 `BTRouter` 的 selector children, `HandleIntent` 放 `HandleReflex` 后面
3. **删掉 `route` 里的 `NotImplementedError`**, 这是故意留的跳栏
4. 同步去 `sprint1_plan_20260422.md §5.2` 把 T10 标 ⏸️ 或 ✅ (Sprint 2 成立后自然过渡)

### 7.2 `session/video_tier` + `session/dsg_mode` 的写入责任

两 key 在 `bb_schema` 声明 writer = `brain.perception_supervisor`, **该模块不存在**. Sprint 2 S2.C2 必须建. 建的同时:
- 订阅 `session/visual_state` 变化 + A10 健康 ping
- **决策结果**必须走 Intent 层 (`EventLayer.INTENT`), 写 BB 的同时 XADD 到 `STREAM_EVENT_LOG` (L0)
- **不要**直接 C3/C4 通知 Gemini — Intent 层本分是"自主改 BB", 通知交给 Injector 继续代理 (Injector 要补 `_classify_video_tier` / `_classify_dsg_mode`)

### 7.3 Gemini 四通道边界不要被 Sprint 2 拆散

- C2 `update_instructions` 整块刷, 频率 **< 每分钟一次**, 只在 Scene/VisualTier 跨档的大调整用 (比如 VIDEO_GEMINI_ONLY→VIDEO_OFF)
- C3 role=user `[状态]` 为主力通道, 层③轻全走这里
- C4 `generate_reply` 省着用, 每分钟只触发一次左右
- **不要**自己新开一条 Gemini 通知通道 — 四通道已经够用, 多一条就会有歧义

---

## 8. 数据统计

| 指标 | 数值 |
|:-----|:----|
| Sprint 1 代码 commit | 10 (T1-T10) |
| Sprint 1 doc commit | 3 (`03d7954` 开工固化 + `670a01b` Sprint 0 草稿收尾 + `060dbbe` T5-T10 台账) |
| 净产出 (从 `72981e5` P2 基线到 HEAD `060dbbe`) | 见 `git log --stat 72981e5..HEAD` |
| 新建 Python 模块 | 2 (`brain/vision/state.py`, `brain/obs_log.py`) |
| 新建 C# 脚本 | 1 (`VideoStateReporter.cs`) |
| 显著扩展的既有模块 | 4 (`blackboard.py`, `telemetry_receiver.py`, `_rpc_bridge.py`, `context_injector.py`, `soul.py`) |
| 新 BB 写入路径 | 6 (body_state / ar_tracking_state / hand_gesture / last_rpc_ack / scene / visual_reason / visual_state) |
| 新 Redis Stream | 1 (`parrot.obs_log`, 与 `parrot.events.log` 并列) |
| Gemini 通道实际用到 | 5 / 6 (C1-C4, C6 既有; C5 由 RoomOptions 开) |

---

## 9. 回引 / 交叉索引

- Sprint 0 Schema V1 → Sprint 1 写入者: `sprint0_completion_report §2.1` → 本报告 §3
- 视频流三层门控: `ar_feature_vision §3.3` → 本报告 §2.1 + §7.2
- 三层意识 → Gemini 四通道: `sprint1_plan §2` → 本报告 §2.1
- 体感红线: `audit_identify_object §1.2` → 本报告 §2 T8
- Intent 层延后理由: `sprint1_plan §5.3` → 本报告 §4
- VisualStateReason 13 词: `shared/vision_state.VisualStateReason` → 本报告 §2 T5
- `open_bb_client` 单 writer 契约: `scheduler/blackboard.py` docstring → 本报告 §2 T1

---

## 10. Sprint 2 开工前的状态总结

**GOSLO 现在能**:
- 感知自己视觉被背景 (APP_BACKGROUNDED) / AR 丢跟踪 (AR_LOST/AR_LIMITED) / 未知原因损坏
- 把视觉状态变化以"自我旁白"方式告诉 Gemini (走 role=user C3)
- 跨档跳变 (BLOCKED, PAUSED↔ACTIVE) 主动开口 (C4)
- 说话带行为约束 (SOUL_CONSTRAINTS) — DEGRADED 时自己会用"好像是..."不用"是..."
- RPC 被 Unity 拒绝时告诉 Gemini (而不是假装成功)

**GOSLO 还不能** (Sprint 2 接力):
- 自己决定降低视频码率省流量 (需 Intent 层 + PerceptionSupervisor)
- A10 关闭时从 Gemini 转写里抽取名词当观测 (需 Ingest filter 层 + S2.B)
- 同时 fly_to 和 animate 时仲裁冲突 (需 Arbiter)
- Scene 切换 (Desktop ↔ AR) 时重塑 Gemini persona (需 Injector C2 大刷)

Sprint 1 把"骨架 + 神经"装好了, Sprint 2 要装"条件反射 + 自主神经"。
