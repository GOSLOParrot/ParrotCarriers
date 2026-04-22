---
status: ratified
status_note: "Sprint 2 的事实记录 — 代码已落地, 单元/smoke 级别自证, 真机端到端 smoke 留给用户自管。只描述'既成事实', 不含未验证设计。"
last_reviewed: 2026-04-23
---

# Sprint 2 完成报告 — Intent 层自主 + 两轴模式 + DSG Ingest 过滤器

> 日期: 2026-04-23
> 作者: Agent (Composer) + 用户决策
> 定位: **事实记录**, 不是计划, 只记"Sprint 2 实际交付了什么 + 留了什么坑给 Sprint 3"
> 关联文档:
> - `sprint1_completion_report_20260422.md` (Sprint 1 留下的 5 个已知坑)
> - `sprint2_plan_20260423.md` (Round 2 开工前的上下文固化件, T1-T12 的唯一 checklist)
> - `ar_feature_vision.md` §3.5 Intent 层 / §3.6 两轴模式 / §3.7 Ingest 过滤器
> - `audit_identify_object_no_screenshot_20260420.md` §7 "体感红线" (依然是灵魂)

---

## 0. TL;DR (三行说完)

Sprint 2 **只做了一件事**: 把 GOSLO 从**感知链路就位**推到**自主闭环就位**: Unity/AR 的可见性信号 + 外部 A10 健康信号 → `PerceptionSupervisor` 1 Hz 决策 → `session/video_tier` × `session/dsg_mode` → Injector C3/C4 + Unity `setVideoTier` RPC + DSG 过滤器准入。同时把 Gemini 转写 + identify_object + 用户标签 + A10 CV 四路全部拉进 `IngestRunner → L2-B 语义图`。

- **12 个 T commit** (`8feec5f [S2.T1]` → `37cdd37 [S2.T12]`) + 2 个 doc commit (开工 + 收尾)
- **核心突破**: Intent 层不是事件路由的延伸, 而是**有状态的控制器** (hysteresis) + 专用 BB writer; Router 的 `HandleIntent` 只是 acknowledge, 不做 BB 写, 解耦生产者/路由/消费者
- **刻意不做**: LiveKit Unity SDK 动态再编码 (PublishTrack 不可变, Sprint 3 连 AR 一起重建) / Graphiti 写回 (Sprint 4, 先让本地 L2-B 稳) / Soul 按 DsgMode 分档 (Sprint 4+, 要代码实证)

---

## 1. 范围 — 12 个 T 实际做了什么

| T | commit | 实际动作 | 意图 |
|:--|:-------|:---------|:-----|
| **T1** | `8feec5f` | 新 `brain/perception_supervisor.py` 骨架 + `DEFAULT_COMBO` 启动写入 | Supervisor 作为 `session/video_tier` + `session/dsg_mode` 的唯一 writer 落地; Context Injector 的首次 C3 播报有 ground-truth 可读 |
| **T2** | `33c2fe0` | `perception_supervisor.decide()` 纯函数 + hysteresis 时窗 + A10 健康 probe (env stub) + 1 Hz 控制循环 | 真正 autonomous: 视觉连续 DEGRADED 15s → 降档, A10 down 30s → 降档, 连续 up 60s + 视觉 OK → 升档; 决策面和副作用面物理隔离 |
| **T3** | `d698377` | `scheduler/nodes.py HandleIntent` + `router.py` 改 4 叶 Selector, 删 `NotImplementedError` | 对称: Reflex / Intent / Nanobot / BrainDirect 四路; Intent 不做 BB 写 (生产者已经写好), 只做路由 acknowledge |
| **T4** | `7ec0f61` | Supervisor `_on_decision_committed` 写 `EventEnvelope(layer=INTENT, kind=intent.tier_change)` 进 `STREAM_EVENT_LOG` + `log_obs_event("intent_decision", layer=2)` | 两条审计面: L0 跨进程事件流 + L2 观测日志; 给 Sprint 3 "Reverse Provenance Expansion" 和技能蒸馏留原料 |
| **T5** | `ad83c65` | Injector `_classify_video_tier` / `_classify_dsg_mode` + `_TIER_C3_CUES` / `_MODE_C3_CUES` | BB 写完立刻有嘴; 常规降/升档走 C3 状态句, 升到 `VIDEO_FULL` 走 C4 (Gemini 会 "醒" 说一句), 节奏感参照 SVA 的 processor-after-turn 经验 |
| **T6** | `7a0e2e0` | `dsg/ingest/{text_source,tool_result,user_tag,cv_track}_filter.py` 4 个纯函数过滤器 + `__init__.py` 导出 | 过滤器只做 `payload → Observation[]`; 名称 (`text_source_filter` 等) 是 `mode_controller` 准入白名单的键 |
| **T7** | `7cfbf1f` | `dsg/ingest/gemini_transcript_extractor.py` + `agent.py _attach_gemini_transcript_to_terminal` 钩子 | Gemini 四通道里 C1 的副产物 (user/assistant 转写) 现在也喂语义图; `_SKIP_PREFIXES` 前缀白名单挡住 `[状态]` / `[Gemini·...]` 回环 |
| **T8** | `9b3947f` | `dsg/ingest/runner.py` — `IngestRunner.commit_outcome/commit_observation` | Observation 的唯一落地入口: 按 `_SOURCE_PRIORITY` 合并, "见到第二次" 在时窗内把 TENTATIVE → CONFIRMED, 每条都写 `obs_log`; Graphiti 写回留 `TODO(S4.B)` |
| **T9** | `45770c9` | `dsg/mode_controller.py` + runner 挂钩 | 一张 `FILTER_SETS[DsgMode]` 表说清每档允许哪几个过滤器; 过滤器本身零耦合 BB, runner 在 commit 前查一次 |
| **T10** | `dbe496b` | `_rpc_bridge.push_video_tier` + Unity `VideoTierReceiver.cs` + `ARVideoPublisher.SetPublishMuted` | Intent 决策的下行一把: Supervisor → RPC → Unity; `VIDEO_OFF` 走 `ILocalTrack.SetMute(true)` 现在就能看到 track 黑屏; 真正的 bitrate/fps 再编码留 Sprint 3 |
| **T11** | `dbe496b` (同) | `VideoStateReporter.cs` 订阅 `ARVideoPublisher.OnPublishMutedChanged` → `onVideoDegraded(reason=track_muted)` | Unity 侧 mute/unmute 变化现在能回到 `session/visual_reason = TRACK_MUTED` (Sprint 1 §6.7 遗留); 链路闭环: Supervisor 降 → RPC → Unity mute → reporter → BB → Injector |
| **T12** | `37cdd37` | `bb_schema.py` 删 `global/soul_constraints` key + `soul.py` 注释说明 + `agent.py` attach Supervisor & ModeController | Sprint 1 §6.1 双身份坑收口; `SOUL_CONSTRAINTS` 单一事实源 (模块级 dict); Boot 顺序: telemetry_receiver → Injector → Supervisor → ModeController → triggers |

12 个 T 全部 commit, 代码量 ~1,800 行 (不含 doc)。

---

## 2. 数据流 — Sprint 2 之后长什么样

```
┌──────────────── 感知采入 (Sprint 1 已装 + Sprint 2 接线) ────────────────┐
│  Unity OnApplicationPause    ─┐                                         │
│  Unity AR tracking_state      ├─► onVideoDegraded(reason)               │
│  Unity ARVideoPublisher mute  ─┘                                        │
│                                │                                        │
│                                ▼                                        │
│  brain/vision/state.py  ──► session/visual_reason + session/visual_state│
└────────────────────────────────┬────────────────────────────────────────┘
                                 │                    ▲
                                 │                    │ (C3 push)
 ┌───────────────────────────────┼────────────────────┼──────────────┐
 │  Sprint 2 新增: 自主闭环       ▼                    │              │
 │                                                                    │
 │  perception_supervisor.decide (pure)                               │
 │    ┌──────────────────────────┴──────────────────────────┐        │
 │    │  hysteresis: degraded_since / a10_down_since /      │        │
 │    │  a10_up_since / manual_override_until               │        │
 │    └──────────────┬──────────────────────────────────────┘        │
 │                   │                                                │
 │  每 1Hz 决策:      │                                                │
 │    visual ≥15s degraded   → VIDEO_GEMINI_ONLY + DSG_GEMINI_VISION │
 │    A10 down ≥30s           → 同上                                  │
 │    A10 up ≥60s + 视觉 OK   → VIDEO_FULL + DSG_FULL                 │
 │                   │                                                │
 │                   ▼                                                │
 │    BB write: session/video_tier, session/dsg_mode                  │
 │                   │                                                │
 │    ┌──────────────┼─────────────────────────────┐                  │
 │    │              │                             │                  │
 │    ▼              ▼                             ▼                  │
 │  L0 XADD        L2 obs_log                 push_video_tier RPC     │
 │  intent.tier_change  intent_decision        setVideoTier (Unity)   │
 │                                                     │              │
 │                                           ┌─────────▼───────┐      │
 │                                           │ VideoTierReceiver│     │
 │                                           │  + ARVideoPublisher│   │
 │                                           │    SetPublishMuted│   │
 │                                           └─────────┬───────┘      │
 │                                                     │              │
 │                                           OnPublishMutedChanged    │
 │                                                     │              │
 │                                                     ▼              │
 │                                           VideoStateReporter       │
 │                                           onVideoDegraded(track_muted)│
 │                                                                    │
 └────────────────────────────────────────────────────────────────────┘

┌───────────────── Context Injector C3/C4 分派 (Sprint 2 扩) ────────────┐
│  _WATCHED_BB_KEYS 现在包含:                                             │
│    session/visual_state, session/visual_reason, tick/last_rpc_ack,      │
│    session/behavior_mode, session/video_tier, session/dsg_mode          │
│  _classify_video_tier:  降档/升档/OFF → C3; ↑VIDEO_FULL → C4           │
│  _classify_dsg_mode:    所有 DsgMode 变化 → C3                          │
└─────────────────────────────────────────────────────────────────────────┘

┌───────────────── DSG Ingest 过滤器 (Sprint 2 新) ────────────────────────┐
│  Gemini user/assistant 转写 ──► GeminiTranscriptExtractor ──┐           │
│  identify_object 结构化返回 ───────────────────────────────┐├►          │
│  用户 Obsidian 双链同步  ──────────────────────────────────┤├► IngestRunner │
│  A10 CV 轨迹 (Sprint 3 供)  ──────────────────────────────┘┘  │         │
│                                                              │         │
│  每个 filter 产 Observation[]  ────────────────────────────►│          │
│                                                              │         │
│           mode_controller.is_enabled(filter_name)?          │         │
│           (读 session/dsg_mode, 1 Hz cache)                  ▼         │
│                                                                       │
│           IngestRunner.commit_observation                             │
│             ├─ 找已有节点 → 按 _SOURCE_PRIORITY 合并                    │
│             ├─ 见到第二次 + 同 bbox → TENTATIVE → CONFIRMED            │
│             └─ log_obs_event("ingest_upsert", layer=1)                │
│                 │                                                     │
│                 ▼                                                     │
│            L2-B SemanticNode 图 (内存)                                │
│            TODO(S4.B): Graphiti 写回 (暂缓)                           │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3. Blackboard Writer Map (Sprint 2 新增写入者粗体)

| key | writer | 动作驱动 |
|:----|:-------|:---------|
| global/session_id | `brain.agent` | 启动 |
| global/behavior_mode | `brain.tools.set_mode` | Gemini tool 调用 |
| session/room_id, unity_identity, connected_since | `brain.agent` | connect |
| session/scene | `brain._rpc_bridge` | `set_scene()` |
| **session/video_tier** | **`brain.perception_supervisor`** | **1 Hz decide** + 启动 DEFAULT_COMBO |
| **session/dsg_mode** | **`brain.perception_supervisor`** | 同上 |
| session/visual_reason | `brain.vision.state` | `onVideoDegraded` RPC + (Sprint 2 T11) Unity mute |
| session/visual_state | `brain.vision.state` | 每次 reason 变化后 fuse |
| session/persona_snapshot | `brain.agent` | 启动 / persona 更新 |
| tick/ar_tracking_state | `brain.telemetry_receiver` | DataChannel |
| tick/last_rpc_ack | `brain._rpc_bridge` | 每次 `call_unity_rpc` 返回 |
| tick/current_event | `scheduler.router` | 每事件 tick 内 |

未变的 writer 都保持 Sprint 1 的边界不乱动。

---

## 4. Gemini 四通道映射 (Sprint 2 扩展)

| 通道 | 触发源 | 载荷示例 | 节奏 |
|:-----|:-------|:---------|:-----|
| C1 turn-taking | Gemini Live 内建 | 用户说话 / GOSLO 回复 | 自然 |
| C2 update_instructions | Scene 切换 + 跨档 `VIDEO_OFF↔其他` | 重建 soul_constraints 段 | 低频 |
| C3 chat_ctx (`role=user` + `[状态]`) | visual_state / visual_reason / video_tier 小变 / dsg_mode / last_rpc_ack 失败 | `[状态] 视频流降档 (GEMINI_ONLY)` | 事件驱动 |
| C4 generate_reply(instructions=) | 视觉 blocked 从无到有 + **升到 VIDEO_FULL** | `请向用户说明视觉已恢复` | 重要变化 |
| C5 video_input | `RoomOptions(video_input=True)` | Unity Track | 连续 |
| C6 function_tool 返回 | 10 个 tool 同步返回 | `{"ok": true, ...}` | 调用驱动 |

Sprint 2 重点扩 C3 (两个新 BB key) + C4 (升档强调)。

---

## 5. 审计面 (Sprint 2 新)

| 面 | 存储 | 写入者 | 消费方向 |
|:---|:-----|:-------|:---------|
| L0 `parrot.events.log` (XADD stream) | Redis Stream | Supervisor (新 INTENT 层) + 已有 reflex/task | Scheduler Router + 未来跨进程订阅 |
| L2 `parrot.obs_log` | Redis Stream | Supervisor (intent_decision) + Runner (ingest_upsert / ingest_mode_dropped) + Injector (已有) | 反思 / 技能蒸馏 / 离线报告 |

每一次 Intent 决策都有双记录: L0 供实时路由审计, L2 供离线反思。

---

## 6. 已知遗留 / 边界 (给 Sprint 3 的信)

### 6.1 LiveKit Unity SDK `PublishTrack` 不可变 【高】

- Sprint 2 `VIDEO_OFF` 走 `ILocalTrack.SetMute(true)`, 能把画面黑掉
- Sprint 2 `VIDEO_GEMINI_ONLY / VIDEO_FULL / VIDEO_BURST` 之间**不改实际 bitrate/fps**, 只改 BB + Unity 侧 event; Gemini/Injector 通过 BB 知道档位, Unity 视频产能不变
- Sprint 3 AR 重建时一并做: `UnpublishTrack` → `PublishTrack(new TrackPublishOptions{...})`, 参考 `ar_feature_implementation_plan.md Sprint 3`

### 6.2 Graphiti 写回暂停 【中】

- `IngestRunner` 的 L2-B 只写内存 rustworkx 图, 断电丢失
- `TODO(S4.B)` 位置已预留; Sprint 4 再把 CONFIRMED 节点批量 flush 到 Graphiti (配合短期记忆收束)
- 期间用户侧用 Obsidian 双链手工兜底, runner 已经把 UserTag 标为最高权威, 不会被覆盖

### 6.3 A10 健康 probe 是 stub 【中】

- `PARROT_A10_HEALTH_URL` 没设就默认 True; Sprint 2 的 A10 down hysteresis 永远不会触发
- 待 Sprint 3 A10 真实上线: 端点 + Redis heartbeat + stateful ping (配合 `bus-deploy-livekit-ecs` 技能)

### 6.4 Soul 按 DsgMode 分档未做 【低】

- Sprint 1 `SOUL_CONSTRAINTS` 只有 `VisualState` 四档 (ACTIVE/DEGRADED/PAUSED/BLOCKED)
- `DsgMode` 维度目前**只被 Injector 看到** (C3 状态句), Soul 的 allow/deny 表还没按 mode 再分
- 在 Sprint 4 基于真实 trace 决定要不要分, 避免表格膨胀

### 6.5 Ingest 过滤器的 `TextSourceFilter` 名词抽取很糙 【低】

- 正则提取英文 2-4 单词短语; 中文完全没做
- 依赖 L2-B 的 "第二次见到才 CONFIRMED" 去噪, 近期用用户标签和 identify_object 压噪
- Sprint 3 或 4 引入小型 NER (spaCy / Gemini side channel) 再升级

### 6.6 `ModeController` fallback 偏宽松 【低】

- BB 里还没写 `session/dsg_mode` 时, fallback = `DSG_GEMINI_VISION` 的过滤器集; 允许 text_source 在启动初期跑
- 考虑: 用户实际启动延迟 ~2s, Supervisor initialize() 瞬间写入 DEFAULT_COMBO, 窗口极小, 当前策略优于 "等 BB 就位"

---

## 7. Sprint 2 结构性决策 (从 Sprint 1 升级的)

### 7.1 Intent 层: **生产者写 BB + Router 只 ack** (不是 Router 写 BB)

- Reflex: 是 Router 写 (副作用无处可放)
- **Intent: 生产者 (PerceptionSupervisor) 写, Router 只 ack**
- Task (Nanobot): 也是生产者 (Nanobot 子进程) 写

结论: **"Router 写 BB" 是 Reflex 的特殊模式**, 不是通用规则; Intent / Task 都是事件生产者 + 事件路由双独立, Router 只当事件总线。

### 7.2 两轴 (VideoTier × DsgMode) 是**正交**而非线性

- Sprint 1 设计阶段曾考虑用单一 "档位" 0-3; Sprint 2 落地确认: 两轴实际解耦
- `VIDEO_OFF + DSG_TEXT_ONLY` 是正常值 (用户显式关闭摄像头), 不是降档
- `VIDEO_FULL + DSG_TEXT_ONLY` 也合法 (视频流但暂不做 CV; 延迟降档前的过渡态)
- 见 `shared/tiers.py ALLOWED_COMBOS`

### 7.3 Filter 是**纯函数**, Runner 是**副作用容器**

- 过滤器零 BB 读、零 Redis 写、零 L2-B 改
- Runner 是所有副作用的单点: `mode_controller` 准入 + L2-B upsert + `obs_log` 审计
- 好处: Sprint 3 加 "离线 replay" 只需把 filter 跑一遍就能重放观察, Runner 单点换成 dry_run

### 7.4 Ingest 的 "权威层级" 是 **字段内写死**, 不是 BB 可调

- `ObservationSource` 枚举 + `_SOURCE_PRIORITY` 表定义 4 源 (USER_TAG_OBSIDIAN > IDENTIFY_OBJECT > A10_CV_TRACK > GEMINI_TRANSCRIPT)
- 不走 BB 热更新, 避免 "权威可运行时改" 带来的审计灾难
- Sprint 5+ 如需调整, 再评估是否落 BB

---

## 8. Sprint 3 入场必读 (交接)

1. **第一件事**: 读 `sprint3_plan_*.md` (尚未写, 计划 2026-04-28 进)
2. **第二件事**: 把 **A10 真的拉起来** — `bus-deploy-livekit-ecs` 技能 + A10 GPU 机甲按需拉起; 没 A10, Supervisor 的升/降档都是 stub
3. **第三件事**: Unity AR 重建 + `PublishTrack` 动态换码 — 这是 Sprint 3 的骨头
4. 切忌在 Sprint 3 之前合并 Sprint 4 的 Graphiti 写回; 每个 sprint 只动一个结构层

Sprint 3 目标 (预判, 不保证):

- A10 上线 + `identify_object` 走 L2-B 读 (audit §7 Path 2/3 闭环)
- Unity AR 重建 + 动态 bitrate/fps
- `HandleIntent` 再加一路 "用户主动切档" 事件 (set_video_tier tool)
- `TimelineNavigator` 初版 (ar_feature_vision §3.8)

---

## 附录: 12 commit 台账

```
8feec5f [S2.T1] perception_supervisor skeleton + DEFAULT_COMBO startup write
33c2fe0 [S2.T2] perception_supervisor decision loop + A10 health stub + hysteresis
d698377 [S2.T3] HandleIntent leaf + router 4-leaf Selector (drop NotImplementedError)
7ec0f61 [S2.T4] Supervisor: Intent decision XADD to L0 + obs_log audit
ad83c65 [S2.T5] Injector: classify video_tier + dsg_mode (C3 cues, C4 on upgrade-to-FULL)
7a0e2e0 [S2.T6] 4 concrete Ingest filters: text_source / tool_result / user_tag / cv_track
7cfbf1f [S2.T7] Gemini transcript extractor + agent.py hook (anti-echo guard)
9b3947f [S2.T8] Ingest runner: Observation -> L2-B upsert with authority merge
45770c9 [S2.T9] mode_controller: BB-driven filter enablement + runner wiring
dbe496b [S2.T10+T11] setVideoTier RPC round-trip + TRACK_MUTED reporter + ARVideoPublisher.SetPublishMuted
37cdd37 [S2.T12] soul_constraints dual-identity close + attach supervisor & mode_controller in agent.py
```
