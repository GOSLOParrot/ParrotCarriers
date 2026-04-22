---
status: ratified
status_note: "Sprint 1 开工前的设计固化。Round 1 重读 4 份必读 + ar_feature_vision + audit_identify_object + 5 个 skill 后, 对着 Gemini Live 实际 API 行为 (2026-01 LiveKit issue #4875 官方确认) 做的方案收口。用户在 2026-04-22 Round 1.5 确认 '按你顺的做', 现落文防止上下文坍缩。"
last_reviewed: 2026-04-22
progress: "T1-T10 ✅ all done at HEAD 2026-04-22. Sprint 1 closed; next is Sprint 2 S2-Intent (autonomous action layer) + LiveKit path-layer gating (§9.1 G1.1 P3)."
---

# Sprint 1 设计收口 — 视频流骨骼 + 自知四路信号 + Gemini 四通道体感

> 日期: 2026-04-22
> 定位: **开工前设计固化**, 不是架构文档, 是"Round 2 写代码时的唯一 checklist"
> 前置依赖 (读过, 结论已提炼, 不必重读):
> - `ar_feature_implementation_plan.md` Sprint 1 段 (原任务单 S1.A-G)
> - `sprint0_completion_report_20260422.md` §10 (遗留问题)
> - `ar_feature_vision.md` §3.1/§3.3/§3.5 (三层门控 + 四级 VisualState + 三层意识分发)
> - `audit_identify_object_no_screenshot_20260420.md` §1.2 (tool 同步/异步 × GOSLO 话术 体感红线)
> - `shared/bb_schema.py` (Schema V1 锁死, 19 key × 4 scope)
> - `scheduler/router.py` / `scheduler/nodes.py` / `brain/context_injector.py` / `brain/telemetry_receiver.py` / `brain/tools/_rpc_bridge.py` (现状)

---

## 0. Sprint 1 一句话收口

**Sprint 1 = 把视频流从产地到 Gemini 的完整生命周期落成系统骨骼, 并用对 Gemini Live 的四条通知通道**。自知 Blackboard、意识分发、Intent 层都是骨骼里的"神经系统"段, 不是目的。验收用例 1/2/3 = 视频降档/恢复 + RPC 失败反馈, 就是这根骨骼的三个核心场景。

---

## 1. Gemini Live 四通道真实行为 (业内踩过的坑, 不是设计选择, 是硬约束)

| 通道 | API | 用途 | 硬约束 (**Sprint 1 代码必须避开**) |
|:-----|:----|:-----|:----------------------------------|
| **C1 语音** | 自然轮 + `generate_reply()` | GOSLO 说话 / 听用户 | Gemini Live 只有 user/model 两个角色. 不是通知通道, 是主线 |
| **C2 系统指令** | `session.update_instructions(text)` | 切人格 / 换 Scene / 换 constraints 表 | **整体替换**. 换一次要带完整 prompt. 高频用会冲掉上下文. **Sprint 1 只在 Scene/VisualState 跨档时用** |
| **C3 chat 上下文插入** | `session.update_chat_ctx(ctx)` | 把过去事件变成 "GOSLO 记得发生过的事" | **Gemini realtime 下 role=system 被静默丢弃** (livekit#4497 / #4875, 2026-01 官方确认). **Sprint 1 走这条必须用 role=user, 前缀 `[状态]`** |
| **C4 主动开口** | `session.generate_reply(instructions=msg)` | 让 Gemini 立刻按这段话说 | 必触发语音输出. 用多了变神经质. **Sprint 1 只在跳变事件用 (blocked / paused 切换 / 回来打招呼)** |
| **C5 视频输入** | `RoomOptions(video_input=True)` | Gemini 云端看 LiveKit 视频轨 | Gemini 看的那一帧我们取不到. 识物要图必须另外 RPC `captureSnapshot` |
| **C6 工具回值** | `@function_tool` 返回 str | tool 结果同步回 Gemini | 最干净的一条. audit §1.2 "体感红线" 本质就是 C6 必须同步等 |

**References**: [livekit/agents#4497](https://github.com/livekit/agents/issues/4497) / [livekit/agents#4875](https://github.com/livekit/agents/issues/4875) / [Vertex Live API best practices](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api/best-practices)

---

## 2. GOSLO 三层意识 → Gemini 四通道 真实映射 (取代原任务单"送 system message"的说法)

| 意识层 | Gemini 触达方式 | 实际 API | 频率 | 典型事件 |
|:-------|:---------------|:---------|:-----|:---------|
| **层① 潜意识** | 不触达 | 只写 Blackboard + Redis `parrot.obs_log` | 每事件 | 视频单帧糊 / Tracking LIMITED < 5s / body IDLE→LOOKING_AT |
| **层② 自主行动** | 不触达 | 改 Blackboard + 本地 `soul_constraints` dict | 每决策 | 连续 3s 糊 → 降 VisualState / 消费端自跳过糊帧 |
| **层③ 通报轻** | **C3** `update_chat_ctx(role=user, "[状态] ...")` | 事件驱动, 同 state 3s 去重 | 每数轮 | visual_state 跳变 / body FROZEN / RPC rejected |
| **层③ 通报重** | **C4** `generate_reply(instructions="...")` | 罕见, 跨档跳变才用 | 每十分钟级 | App 后台 >30s 回来 / blocked 触发 |
| **跨层 Soul 切档** | **C2** `update_instructions()` | 极罕见 | 每次 Scene/Mode 切换 | Scene DESKTOP→AR / BehaviorMode 切换 |
| **跨层 Tool 同步** | **C6** function_tool return | tool 调用时 | tool 每次 | identify_object / fly_to (同步等结果) |

**关键原则三条**:
1. LLM 是听众, 不是轮询器 — 所有状态变化由 Injector 主动 push
2. turn 开头快照摘要 (Voyager 式) + 瞬时事件两条路并行, 都走 C3, 不冲突
3. 失败反馈 > 成功反馈 (BrainBody-LLM 洞察) — 走 C3 轻 / C4 重都行, 不能沉默

---

## 3. 视频流骨骼 (Sprint 1 主轴, 三层门控落在哪)

```
┌─────────────┐    ┌──────────────┐    ┌───────────────┐    ┌──────────────┐
│ ① Unity 产地 │ →  │ ② LiveKit 路 │ →  │ ③ Python 消费 │ →  │ ④ Gemini Live │
│ 产地门控    │    │ (Sprint 1 不 │    │ (Sprint 1 不 │    │  云端黑盒     │
│ S1 做       │    │  做, §9.1 G1 │    │  做, Sprint 2 │    │              │
│             │    │  .1 P3 储备) │    │  消费端过滤)  │    │              │
└──────┬──────┘    └──────────────┘    └───────┬───────┘    └──────┬───────┘
       │ onVideoDegraded RPC (C5 硬约束: 信号单独走)                │
       │                                        │                   │
       ▼                                        ▼                   ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ Blackboard (单一真相源)                                                   │
│  session/visual_state   = VisualState (active/degraded/paused/blocked)    │
│  session/visual_reason  = VisualStateReason (app_backgrounded/blocked/...) │
│  tick/ar_tracking_state = TRACKING/LIMITED/NOT_TRACKING                   │
│  tick/last_rpc_ack      = {ok, rpc_name, reason}                          │
└───────────────────────────────┬───────────────────────────────────────────┘
                                │
                                ▼
                  ┌─────────────────────────────┐
                  │ ContextInjector (Sprint 1)   │
                  │ 按 §2 映射表 走 C2/C3/C4    │
                  └─────────────────────────────┘
```

**Sprint 1 必做**: 产地层 + BB 汇总 + Injector 通道分发
**Sprint 1 不做**: LiveKit 路上层 (§9.1 G1.1 P3) / 消费端过滤 (Sprint 2) / Burst 档 (P3)

---

## 4. 与 audit_identify_object 的协作体系 (§1.2 "体感红线" 在 Sprint 1 的对应)

audit §1.2 原文: **"tool 的同步/异步行为, 必须和 GOSLO 说出口的话一致"**。

Sprint 1 的通道映射表就是这条红线在"状态通知"侧的对应。**统一原则**:

| 场景 | audit §1.2 对应 | Sprint 1 对应 |
|:-----|:---------------|:--------------|
| "GOSLO 说了但没做" | tool 火即忘 + 同步返回承诺话术 = 错 | C4 generate_reply("我飞过去") 但 fly_to 被 reject 且 Injector 漏报 = 错 |
| "GOSLO 做了但没说" | tool 同步完 + 不返回 = 错 | BB 改了但 Injector 该走 C3 时没送 = 错 |
| "幕后黑工 GOSLO 扛" | tool 内部派 Nanobot 同步等 = 对 | 层②自主行动只改 BB 不通知 Gemini = 对 |
| "失败必报" | tool 失败返回明确错误 | C3 走 `[状态] RPC fly_to rejected: out_of_bounds` |

**Sprint 1 Injector 的 `_decide_layer(event)` 必须保证: BB 的每一次层③级变化, Gemini 要么通过 C3/C4 收到, 要么通过 tool 回值 (C6) 收到. 永远不能 "BB 改了 Gemini 却以为没改"**。

识物升级 (Sprint 4 S4.B) 时, identify_object 走 C6 同步闭环, 里面失败了会写 `tick/last_rpc_ack` 同时 C3 补一条 — 这就是两套体系打通的点。

---

## 5. Sprint 1 任务清单 T1-T10 (10 个独立 commit, 每个 0.2-0.5 天)

### 5.1 必做 (视频流骨骼闭环)

| # | 状态 | 动作 | 文件 | Commit |
|:--|:----:|:-----|:-----|:-------|
| **T1** | ✅ | `scheduler/blackboard.py` 按 `shared/bb_schema.BB_KEYS` 的 19 key 分 scope 挂 py-trees Client, writer 模块拿 WRITE 其他 READ. **真实 API**: `open_bb_client(name, writer)` 返回裸 py-trees Client, caller 用 `client.set("key")/client.get("key")`. py-trees 原生 `AttributeError` 兜底单一 writer 契约 | `scheduler/blackboard.py` | `d9f8c32 [S1.A1]` |
| **T2** | ✅ | `brain/vision/__init__.py` + 收进 Sprint 0 `snapshot.py`/`visual_match.py` 两个草稿 | `brain/vision/*` | `670a01b chore(sprint0)` |
| **T3** | ✅ | `telemetry_receiver` 收到 behavior_state / hand_gesture / ar_tracking_state → 写 `tick/body_state` / `transient/hand_gesture` / `tick/ar_tracking_state`; 注 `head_state` 声明但 Sprint 1 没 emitter, 留空 | `telemetry_receiver.py` | `f2a8ecf [S1.A2-3]` |
| **T4** | ✅ | `_rpc_bridge.call_unity_rpc` 每次出结果 (成功 / 超时 / transport error / Unity 应用层 reject) 都写 `tick/last_rpc_ack = {ok, rpc, reason, detail, ts}`; 另加 `set_scene(scene)` 写 `session/scene` | `_rpc_bridge.py` | `ea4d412 [S1.A4]` |
| **T5** | ✅ | Unity `VideoStateReporter.cs` 新建: `OnApplicationPause` + `ARTrackingState` 两路 (亮度方差 P3) 变化时 RPC `onVideoDegraded(reason, ts)`; Brain `_rpc_bridge` 注册 RPC 入境 handler → 写 `session/visual_reason` (枚举 VisualStateReason); `tick/ar_tracking_state` T3 已接, 这里只补 `OnApplicationPause` → `APP_BACKGROUNDED` 这一路 | 新 C# + `_rpc_bridge.py` 扩 | `[S1.T5]` |
| **T6** | ✅ | `brain/vision/state.py` 薄壳 (Sprint 0 已有草稿): 订阅 `session/visual_reason` + `tick/ar_tracking_state` + `tick/last_rpc_ack` 三路 BB 变化, 融合决策 → 写 `session/visual_state` (枚举: active/degraded/paused/blocked) | 新文件 (或把 Sprint 0 草稿收口) | `[S1.T6]` |
| **T7** | ✅ | `context_injector.py` 扩: 订阅 BB 变化, `_decide_layer(key, old, new)` 返回层①/②/③, 层③走 **C3 `update_chat_ctx(role=user, 前缀[状态])`** (轻) 或 **C4 `generate_reply(instructions=...)`** (重, blocked/paused 跳变); turn 开头附 3 字段状态摘要 | `context_injector.py` 扩 | `[S1.T7]` |
| **T8** | ✅ | `brain/soul.py` 加模块级 `SOUL_CONSTRAINTS` dict (4 VisualState × {allow/deny}, 只填 visual 层); Injector 按当前 VisualState 查表, 把 `allow/deny` 拼进 C3 状态段. **不做**热更新, **不做** C2 update_instructions 重写 Soul (留 Sprint 2) | `soul.py` 扩 + `context_injector.py` 读 | `[S1.T8]` |
| **T9** | ✅ | `shared/constants.py` 加 `STREAM_OBS_LOG = "parrot.obs_log"`; `brain/obs_log.py` 新: `log_event(kind, layer, payload)` helper, 用 `xadd` 写 Redis Stream; Injector `_decide_layer` 每次调用同时写一份 (所有层都记) | `constants.py` 扩 + 新文件 | `[S1.T9]` |

### 5.2 Sprint 2 预留 (Sprint 1 只加 assert + docstring)

| # | 状态 | 动作 | 文件 |
|:--|:----:|:-----|:-----|
| **T10** | ✅ | `shared/event_log.py::EventLayer` docstring 加 "Sprint 1 只路由 REFLEX/TASK, INTENT 预留 Sprint 2"; `scheduler/router.py` 的 `BTRouter.route` 开头加 `if event.get("layer") == "intent": raise NotImplementedError("Intent 层由 Sprint 2 S2 Intent 任务补全")` | `event_log.py` docstring + `router.py` 扩 |

### 5.4 Sprint 1 commit 台账 (按顺序)

| T | commit | 说明 |
|:-:|:-------|:-----|
| T1 | `d9f8c32 [S1.A1]` | `open_bb_client(name, writer)` |
| T2 | `670a01b chore(sprint0)` | `brain/vision/` 包 + snapshot/visual_match 草稿 |
| T3 | `f2a8ecf [S1.A2-3]` | telemetry 写 body_state / ar_tracking_state / hand_gesture |
| T4 | `ea4d412 [S1.A4]` | `_rpc_bridge` 写 `tick/last_rpc_ack` + `session/scene` |
| T5 | `a24ef89 [S1.T5]` | Unity `VideoStateReporter` + `onVideoDegraded` RPC → `session/visual_reason` |
| T6 | `6cdc462 [S1.T6]` | `brain/vision/state.py` VisualState fusion → `session/visual_state` |
| T7 | `357c525 [S1.T7]` | Injector BB 订阅 + C3/C4 分发 |
| T8 | `66180fe [S1.T8]` | `soul.SOUL_CONSTRAINTS` + Injector 拼 constraint body |
| T9 | `47a968f [S1.T9]` | `STREAM_OBS_LOG` + `brain/obs_log.log_obs_event` + Injector audit |
| T10 | `18fedd6 [S1.T10]` | Router 拒绝 `EventLayer.INTENT` + event_log Sprint 2 标记 |

### 5.3 Sprint 1 明确砍掉 (和上一轮 Q3 判断的修正)

- ❌ 独立 `brain/consciousness/dispatcher.py` → 合进 `context_injector.py` 的 `_decide_layer`
- ❌ 独立 `brain/consciousness/soul_constraints.py` → 写进 `soul.py` 作为模块常量
- ❌ `brain/consciousness/` 子目录 → 不建
- ❌ S1.F `HandleIntent` 节点 / S1.G `BodyChannelLock` → 无事件可路由, 纸面 Lock 无价值, 延到 Sprint 2
- ❌ S1.C6 Soul 读 constraints 热更新 → Sprint 2 做
- ❌ S1.C7 failure 拉 Graphiti 记忆 → `inject_memory` 已有, Sprint 1 不扩
- ❌ LiveKit 路上层门控 → §9.1 G1.1 P3 储备

---

## 6. Schema V1 不动, Bus 协议 V1 可演进的边界

### 6.1 ✅ Sprint 1 可以改 (运行时挂载 / 内聚 API / 新增协议入口)

- `scheduler/blackboard.py` 运行时 `register_key` 挂载 — 这是 BB_KEYS **消费方**, 不是 schema
- `brain/_rpc_bridge.py` 新增 RPC 入口 `onVideoDegraded` — 跨进程协议扩展
- `brain/context_injector.py` 内部方法扩展 — API 内聚
- `shared/constants.py` 新增 stream/topic 常量 — 纯新增

### 6.2 ❌ Sprint 1 不碰 (Sprint 0 Schema V1 锁死)

- `shared/bb_schema.py::BB_KEYS` 字段名 — 只对齐不改名
- `shared/event_log.py` / `snapshot.py` / `tiers.py` / `vision_state.py` 接口
- `dsg/l1_5_protocol.py` / `dsg/ingest/base.py` — Sprint 2 才用
- `shared/parrot_actions.py::BehaviorMode` — 已用中
- `shared/parrot_actions.py` **不加** `layer` 字段 (EventEnvelope.layer 已存在, 不重复)

### 6.3 命名对齐 (Sprint 0 §10.4 遗留问题决议)

Schema 里预占的 writer 名:
- `brain.vision.state` → **T6 真实建**
- `brain.perception_supervisor` → Sprint 2 建, Sprint 1 不建空壳
- `brain.gesture_source` → **不建**, writer 改成 `brain.telemetry_receiver` (和 head 同一个写者)

→ Sprint 1 会在 T1 commit 里顺手微调 `bb_schema.py` 一行: `transient/hand_gesture` writer 从 `brain.gesture_source` 改成 `brain.telemetry_receiver`. 这是唯一一处动 Schema V1, 属于"命名对齐, 不是改接口", 且 Sprint 0 §10.4 已登记为 Sprint 1 归属。

---

## 7. 和 audit_identify_object 的协作约束 (写 Sprint 1 代码时的引用)

Sprint 1 代码**不碰** `identify_object.py` (那是 Sprint 4), 但必须给它铺好两样:

1. **`tick/last_rpc_ack`** (T4) — Sprint 4 L2 γ 选项 (tool 派 Nanobot 同步等) 需要一个统一的失败回灌点, T4 就是它
2. **Injector 的 C3 通道** (T7) — Sprint 4 identify_object 不管用 α/β/γ 哪个选项, tool 内部失败时都能往 obs_log (T9) + BB (`tick/last_rpc_ack`) 写, Injector 自动通报 Gemini, 不需要 tool 再手动调 generate_reply

**红线**: Sprint 1 Injector 的 C3/C4 不能处理 tool 调用本身的同步 (tool 走 C6 自己回). **Injector 只处理 "BB 状态变化"**, 不处理 "tool 正在被 Gemini 调用"。两套体系在 BB 层汇合, 代码上解耦。

---

## 8. 开工顺序 + 依赖图

```
T1 (Blackboard 对齐, 所有后续的基座)
 │
 ├─► T2 (vision 包骨架, 后面 T6 要放)
 │
 ├─► T3 (telemetry → BB, 独立)
 │
 ├─► T4 (RPC ack → BB, 独立)
 │
 ├─► T5 (Unity 产地 → BB via RPC handler)
 │    │
 │    └─► T6 (VisualState 融合, 读 T4/T5 写的 BB)
 │          │
 │          └─► T7 (Injector 分发)
 │                │
 │                └─► T8 (soul_constraints 拼接)
 │
 ├─► T9 (obs_log, T7 顺手调它)
 │
 └─► T10 (Sprint 2 预留, 独立)
```

**关键路径**: T1 → T5 → T6 → T7 (视频流骨骼闭环 = 验收用例 1/2)
**平行可并行**: T2/T3/T4/T9/T10 和关键路径独立
**依赖 T7 完成**: T8

---

## 9. 验收用例 (复制自原任务单, 调整为 Sprint 1 范围)

```
1. Editor Play → 用手遮摄像头 (触发 Unity 产地门控的亮度方差)
   → Brain 终端日志: [video] state=degraded reason=low_brightness
   → Gemini 通过 C3 收到 turn 开头 [状态] 块, 不再说 "你桌上有..."

2. Editor Play → Stop → 30s+ 后 Play
   → Brain 日志: [video] state=active reason=resumed
   → Injector 走 C4 generate_reply → Gemini 主动说 "又见面啦"

3. Brain 派 fly_to(远点) → Unity 拒 (out_of_bounds)
   → BB: tick/last_rpc_ack = {ok:False, rpc_name:"fly_to", reason:"out_of_bounds"}
   → Injector 走 C3 → Gemini 下一轮看到 [状态] fly_to rejected: out_of_bounds

4. Redis XADD parrot.obs_log — 每次 BB 层③变化都有一条
   → tail_obs_log.py (可选, Sprint 2 再做) 能看到完整历史
```

---

## 10. 未解锁风险登记 (写代码时可能踩, 不提前解决)

| # | 风险 | 触发信号 | 应对 |
|:--|:-----|:---------|:-----|
| R1 | py-trees Blackboard Client 不支持 `/` 分隔的嵌套 key 名 | T1 `register_key("session/visual_state", ...)` 报错 | 改成平铺 `session_visual_state` + 保留 name 字段作展示 |
| R2 | `update_chat_ctx` 在高频调用时触发 Gemini 端限流 | T7 跑多 turn 后 Injector 报 rate limit | 加最小 3s 去重 (同 state 同 reason 不重送) |
| R3 | `generate_reply` 打断 Gemini 正在说的话 | T7 C4 在 Gemini speaking 时被触发, 体感断裂 | 检查 `tick/cognitive_state == SPEAKING` 时 C4 延后 / 降级为 C3 |
| R4 | Unity 亮度方差 coroutine 耗 CPU | T5 真机 fps 降 | 5s 采一次, 不是每帧 |
| R5 | `transient/hand_gesture` 2s 过期没实现 | 测试时手势残留 | T3 里简化为"写当前值, 由 Injector 读时判 `now - since < 2s`", 不做 cleanup 任务 |

---

## 11. Round 2 开工规则 (整个 Sprint 1 适用)

- **每个 T 独立 commit**, 消息格式 `[S1.T{N}] {动作}`
- **不写架构文档** (本文件是**唯一例外**, 是"设计固化" 不是"架构文档")
- **不写 ADR**, 不动 `.cursor/rules/`
- **不写测试** (用户自设计)
- **遇到"扩现有 vs 新建"** 优先扩, 除非职责明显不匹配
- **Schema V1 不动** (只在 T1 命名对齐一行微调, 属 §10.4 遗留)
- **每做完一个 T, 更新 `.cursor/memory/active_context.md` 下一步段**

---

*本文件维护*: Sprint 1 每个 T 完成后在本文件 §5 对应行加 ✅ + 完成日期. 不合并进 `ar_feature_implementation_plan.md`, 那是计划, 这是收口。Sprint 1 完成后保留作为"实际做了什么"的事实记录, 给 Sprint 2 开工参考。
