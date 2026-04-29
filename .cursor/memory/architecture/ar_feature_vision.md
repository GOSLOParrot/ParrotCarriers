---
status: tentative
status_note: "§3.5 三合一 / §六 决策 / §3.6 两轴 均未被代码验证。代码落地后 (Sprint 1-2) 对应章节逐段升到 ratified。"
last_reviewed: 2026-04-22
---

> 创建: 2026-04-21
> 维护者: 用户 + AI (用户主导方向 / AI 整理与对齐现有代码)
> 定位: P2.5 / P3 AR 互动玩法的**设计愿景 + 深度讨论**，不是需求合同，不是需求问卷
> 关联:
> - `ar_camera_interaction_survey.md` (用户需要填完的问卷 — 触发方式 / 美化 / 存储)
> - `ar_app_flow_ui_design.md` (当前 App Flow / UI / 功能入口设计基线)
> - `ar_app_plan.md` (早期硬事实 + C1-C12 进度表 + 五维问卷追溯)
> - `audit_identify_object_no_screenshot_20260420.md` (identify_object 升级路径，本文的 §门控 决定它怎么改)
> - `Test/p2/connectivity_report_p2.md` (真实测试阻碍 6 条 + 已知遗留)
>
> **阅读顺序建议**：§一→§二→§三→§四→§五。不要跳着读。
> §五是"数据流和架构需要设计什么东西来支持这些功能"的收口清单。

---

## 一、愿景一句话

GOSLO 是一只**能自知在看什么、被什么挡住**的 AR 鹦鹉。她不是一个黑盒识别系统，她是一个**对自己感知状态有体感的伙伴**——看不见时会坦白、场景切换时会自然转场、被按暂停再醒过来时能接上话。

所有花哨玩法（摆 pose / 拍立得 / 回忆杀）都是这个基底上的糖衣。基底不稳，糖衣会塌。

---

## 二、现状基线 (从 Test/p2 报告钉死)

**已真实验证跑通 (2026-04-21 17:10 session)**:
- Unity → LiveKit → Brain → Gemini 音视频双通道端到端
- Gemini 看到 DroidCam 画面, 准确说出"白色的鼠标"(不是 social 幻觉)
- 麦克风/摄像头 Track Source 都已显式标注, 不会再被 detach
- Webcam 预热 Blit 解决首帧黑
- Webcam 设备启发式选择 (避开 OBS Virtual)

**已知但未解决（这些是本文的设计起点）**:
1. **鹦鹉不知道自己看不见** — 摄像头被遮挡/断流时没有信号回到 Gemini，它会幻觉画面
2. **Play/Stop 抢占 identity** — 调试期反复进出会导致 ICE 残留 30s，PublishTrack NRE
3. **App 后台行为未验证** — Editor 失焦 + 手机切后台两种场景全部空白
4. **`livekit-agents[images]` 是硬依赖** — 没写进 requirements, 任何人重建 venv 都会踩
5. **identify_object 缺截图 + 路径 ②/③ 混淆** — audit 报告已分析, 但数据流未升级

---

## 三、四个核心讨论 (你主动提的，必须说透)

这四个讨论决定了后面所有代码怎么写。顺序不能乱。

---

### 3.1 门控责任划分 — 产地/路上/消费端三层

> **结论先行**：门控不能一层做完。必须**三层协作**，各司其职，不重复劳动。

#### 为什么不能一层做完

- **Unity 做全部门控**: 省带宽但决策视野窄——它不知道 Gemini 当前在问什么，不知道 identify_object 是否正要截帧，它做的所有决策都只基于"我这边看上去不稳"。
- **Python 做全部门控**: Gemini 已经看到垃圾帧了，配额已经烧了。太晚。
- **LiveKit 做全部门控**: LiveKit 只知道传输层（丢包/码率/TrackMuted），不知道画面内容是否有信息。

#### 三层职责清单

| 层 | 负责的门控 | 决策依据 | 已知信号 | 动作 |
|:---|:-----------|:---------|:---------|:-----|
| **① Unity 产地层**（价廉物美） | 画面级 "黑/静止/运动过猛" | `_rt` 像素亮度方差 / ARCore TrackingState / 加速度计 | ARCameraBackground 首帧前（白雾）/ 权限未授予 / OnApplicationPause | 降采样推流 / 暂停推流 / **RPC 主动告知 Brain** `onVideoDegraded(reason)` |
| **② LiveKit 传输层**（免费，直接订阅） | 带宽 / Track 状态 | `TrackMuted` / `ParticipantDisconnected` / simulcast layer 切层 | 事件驱动，无需轮询 | Brain 侧 `_rpc_bridge.py` 或 `agent.py` session handler 订阅 |
| **③ Python 消费端**（精细控制） | "这帧模糊没信息我不喂给 VLM" | 拿到帧后自己做亮度/锐度/特征点判断 | 每路消费者独立（identify_object / DSG Worker） | 消费者自跳过 / fallback 不同策略 |

#### 抗干扰强 = 信号冗余

- 每层都**不依赖**另一层完全正确。Unity 漏报一个黑画面，LiveKit 还能感知 Muted；LiveKit 没反应，Python 收到帧也能自己判模糊。
- 三层的结论都**走同一个"视觉状态通道"**，由 Brain 的 Context Injector 汇总→注入 Gemini system message。Gemini 是唯一接收方，不接收原始信号。

#### 具体到哪个 reason 该在哪层判

| reason (Gemini 需要知道的) | 判定层 | 实现路径 |
|:-----------|:-------|:---------|
| `paused` (App 切后台) | Unity | `OnApplicationPause(true)` → RPC |
| `blocked` (被手挡/糊) | Unity 产地 + Python 消费端 双判 | Unity 亮度方差 + Python 消费端收帧后再验 |
| `static` (画面不动但不黑) | Unity | `_rt` 像素差分 N 秒阈值 |
| `tracking_limited` (AR 追踪丢失) | Unity | `ARCamera.TrackingState` 变化 |
| `network_muted` (传输问题) | LiveKit 事件层 | Brain 订阅 `TrackMuted` |
| `low_bitrate` (simulcast 降级) | LiveKit 事件层 | Brain 订阅 simulcast layer 切层 |
| `blur_frame` (单帧模糊) | Python 消费端 | 消费者拿到帧自判 |

#### Gemini 视角 (最终体感)

不管三层内部谁判定的，Gemini 收到的都是统一的 Context Injector 注入：

```
[system] 视觉状态变化: video_state=paused, reason=app_backgrounded, since=17:32:10
```

GOSLO 的 Soul prompt 里告诉它："视觉状态不是 active 时, 不要对画面内容做断言; 用听觉/记忆撑对话; 变回 active 时可以自然提'欸又能看见了'。"

#### 待你确认

- **G1**: 三层协作这个大方向 OK 吗? 还是倾向"先只做 Unity 一层"快速上线?
- **G2**: "视觉状态" 作为一个独立的、被 Gemini 可感知的字段 (而不是藏在数据里)——这个设计是否接受?

---

### 3.2 App 多次切到后台怎么办

> **核心观察**: 这个问题其实是**两个独立的问题叠在一起**，要拆开。

#### 问题 A: AR 能不能接回来 (感知层)

**平台硬事实**:
- **ARCore (Android)**: `ArSession_pause()` / `resume()` 是官方推荐做法, 但 2025 年已知 bug (ARCore SDK 1.47-1.50 在快速反复切换时**会崩溃**)。Pixel 6a / Android 16 100% 可复现。**这不是我们能修的**。
- **ARKit (iOS)**: 有 `sessionShouldAttemptRelocalization` 返回 true → 自动尝试 relocalize。支持保存 `ARWorldMap` 实现"隔天回来接着玩"。
- **推论**: Android 短时切后台 (<5min) OK, 长时间切后台必须 reset session（丢失 anchor）。iOS 路径未来如果做, 可走 ARWorldMap 体验更好。

**P2/P2.5 范围内**:
- 切后台 → `OnApplicationPause(true)` → 停 AR Session + 停 Publish Track
- 切回前台 → 等 `ARSession.state == SessionTracking` 再恢复发布 (AR 路径先不加 warmup Blit, 等首次真机验证)
- ≥ 3 分钟切后台 → 直接 reset AR Session, 不尝试 relocalize (Android 坑太多)

#### 问题 B: LiveKit Room 状态和 Gemini Session 怎么接 (连接层)

**已知事实**:
- LiveKit Room 在 app pause 时会继续尝试保活 ≤30s (ICE keepalive)
- 超过 30s 被服务端 force disconnect, 触发 `ParticipantDisconnected`
- Brain 侧 Gemini Live session 仍然活着 (session 是 Brain 进程的, 和 Unity 连接无关)
- Test 报告 §4.6 说过: Play/Stop 30s 内连发会抢占 identity → 第二次 Play 时旧 WebRTC 没断完 → PublishTrack NRE

**P2/P2.5 设计**:
- Unity 端: `OnApplicationPause(true)` → 主动 `Room.Disconnect()` (不靠服务端超时, 自己清理)
- Unity 端: `OnApplicationPause(false)` → 检查 LiveKit 连接状态, 断了就重连 (复用现有 token 如未过期)
- Brain 端: 订阅 `ParticipantDisconnected` → Context Injector 注入 `[system] 用户离开了 AR (或手机切到后台了)`
- Brain 端: 订阅 `ParticipantConnected` 重新出现 → Context Injector 注入 `[system] 用户回来了` + GOSLO 可以主动说"欸你回来啦!"（符合 ADR-028 风格）

**不做的事 (P2)**:
- 不做 Token 自动刷新 (当前从文件读, token 1h 过期, 够用)
- 不做 ARWorldMap 持久化 (Android 坑, iOS 还没进范围)
- 不做"隔天续场" (那是 P3+ 的体感设计)

#### 待你确认

- **L1**: "离开 3min 以上 reset session 丢 anchor" 这个牺牲可以接受吗？还是你希望尽可能保留 (代价是 Android 崩溃概率)
- **L2**: 回来时 GOSLO 主动打招呼的人格设定——是**每次**都主动, 还是**只有超过 N 分钟**才主动?

---

### 3.3 GOSLO 自我视觉状态的认知与表达

> **这是 §3.1 门控在 Soul 层的延续**。门控告诉 Gemini "发生了什么", Soul 决定她"怎么说"。

#### 四级视觉自我感知

参照 Opus 11 StabilityGate 的精神但**不搬它的字段**, 用我们自己的四级：

| 级别 | 语义 | Gemini 应有反应 | 允许的话术示例 |
|:-----|:-----|:----------------|:--------------|
| `active` | 看得清, 在动 | 正常描述画面 | "你桌上的杯子是蓝色的" |
| `degraded` | 看得到但糊/暗/抖 | **不做视觉断言**, 可以用"好像""似乎" | "好像有什么东西, 看不太清" |
| `paused` | 主动暂停 (App 后台/用户请求) | 完全不提画面, 转语音/记忆 | "虽然我现在看不见, 但上次你跟我聊过..." |
| `blocked` | 被挡了 (手/物体) | 主动提醒, 不编造 | "我被挡住了! 你把手拿开呀~" |

这四级**必须写进 `soul.py` 的 instructions**, 不能只靠事实注入——因为 LLM 会"好心帮忙"去猜没看见的东西。

#### 抗干扰的具体设计

- **不要让 GOSLO 自己判断视觉状态**。Gemini 容易过度自信 ("我觉得我看得清"), 判断权归门控系统。
- Context Injector 注入的 message **带时间戳**, Gemini 能分辨"刚切到 paused"vs"paused 很久了"。
- Soul 里写: **收到 `blocked` 时必须先抱怨, 再尝试其他交互** (不能跳过抱怨直接聊别的, 会显得冷漠)。
- Soul 里写: **收到 `paused` 时要转向听觉模式**, 不要反复问 "画面回来了吗?" (烦人)。

#### 待你确认

- **V1**: 这四级的颗粒度合适吗? 太粗/太细?
- **V2**: 是否接受"Soul 强制约束话术"而不是 Gemini 自由发挥?
- **V3**: 失去视觉时, GOSLO 可以靠什么撑对话?
  - [ ] (a) 只靠用户当前的语音
  - [ ] (b) 主动从 Graphiti 拉最近记忆 ("对了, 我们早上聊过...")
  - [ ] (c) 讲段子/背景 (鹦鹉絮叨人设)

---

### 3.4 GOSLO 行为模式 + 桌面场景 (预留切换)

> **你明确提出"留模式切换/场景切换的设计"**。这一节给骨架，不给实现细节。

#### 模式 (Mode) vs 场景 (Scene) vs 身体状态 (Body State) — 三者不同

- **身体状态** (已定义): IDLE / FLYING / PERCHING / ... — 见 `parrot_behavior_rules.md`
- **场景 (Scene)**: 当前物理环境描述 — 桌面 / AR 房间 / 户外 / 2D 回退 (无 AR)
- **模式 (Mode)**: GOSLO 的行为风格偏好 — 本期已有 `BehaviorMode` 枚举 (BASE/COMPANION, 见 `shared/parrot_actions.py`)

三者**正交**: 同一个模式可以在不同场景运行, 同一个场景可以切模式。

#### P2 首批上线的 Scene 清单 (只两个)

| Scene | 何时用 | 关键差异 | Unity 变化 | Brain 变化 |
|:------|:-------|:---------|:-----------|:-----------|
| `DESKTOP_WEBCAM` | Editor 开发 / 无 AR 设备 | 无平面检测, 2D 背景 | ARVideoPublisher 走 Webcam 路径 | Soul 知道"我现在在屏幕里看你, 不在你房间里飞" |
| `AR_HANDHELD` | Android 手机 AR 模式 | 有 ARCore 平面/anchor | ARVideoPublisher 走 AR 路径 | Soul 知道"我在你的真实空间里飞, 可以说'你桌上那个...'" |

#### 模式切换机制 (不实现, 只留接口)

- Unity 启动时读 config (或 Inspector) 决定初始 Scene, 发 RPC `setScene(scene_name)` 告诉 Brain
- Brain 在 Soul 里**按 Scene 分支 instructions** (像当前 BehaviorMode 的做法, 复用 `get_instructions(mode, scene)`)
- 运行时切换: 新增 Brain tool `set_scene(scene: str)` - 但这**不是 P2 主线**
- DSG / identify_object / 截帧的行为都**读 Scene** 调整——DESKTOP 下不触发"AR 平面上的物体"类工具

#### P3+ 场景储备 (不做, 只登记)

- `AR_WORLD_LOCKED` (有预建图 / LiDAR, 支持 ARWorldMap 锚点)
- `OUTDOOR_LIGHT_SHOW` (户外暗, 更倾向语音对话少视觉)
- `MULTIPLAYER_PRESENCE` (光遇式, 别的用户的 GOSLO 也能出现)

#### 待你确认

- **S1**: P2 上线就先支持 DESKTOP_WEBCAM + AR_HANDHELD 两个 Scene 足够吗?
- **S2**: 场景切换由 Unity 决定 (config/Inspector) 还是 Gemini 决定 (tool)? 我建议 Unity 决定——Gemini 不该能自己选场景。

---

### 3.5 Proprioception — GOSLO 自知架构 (§3.1/§3.3/§3.4 的统一底座)

> **你抓到的最关键的点**: 视觉门控 / 身体状态机 / 行为树 / 行为模式 / 场景切换, 这五件事**本质是同一个问题**——
> **系统内部的"事实"怎么实时、可靠、不漏地暴露给 Gemini Live**, 让它像人一样"自知"自己的身体和环境。
>
> 这一节不是玩法, 是底座。没有它, §3.1-§3.4 会各写各的、互相打架、注入冲突。

#### 参考的前沿实践 (钉死原理, 不照抄)

| 来源 | 我们借鉴的东西 | 我们**不**借鉴的东西 |
|:-----|:--------------|:-------------------|
| **MASMP** (ArXiv 2510.18395, 星际 II) | LLM 外挂 FSM/BT 状态约束 + 记忆槽跨 tick 保留战术变量 | 整个 RTS 决策循环, 我们不是回合制游戏 |
| **BrainBody-LLM** (ArXiv 2402.08546, 机器人) | **双 LLM + 闭环状态反馈**, 高层 LLM 不直接控制电机, 出错重规划 | 我们是单 Gemini + Brain agent, 不分 Brain/Body 两个 LLM |
| **InCoRo** (ArXiv 2402.05188) | 每 tick 把 robot proprioception (执行器状态) + 视觉 grounding 一起注入 | 连续 code 重写执行, 我们是 tool-call 语义 |
| **ELLMER** (Nature MI 2025) | 40Hz 力/视觉反馈回路, 用 **感知层**纠正 **语言层** 幻觉 | 力反馈 (我们没有) |
| **Voyager** (Minecraft) | **agent state 作为 prompt 段**, self-verification 闭环 | 终身技能库 (我们 P2 不做) |
| **Unreal BT + Blackboard** | **Blackboard 作为单一真相源 + 事件驱动**, 不是每 tick 轮询 | 我们后端是 Python py-trees + Nanobot, 不是 UE BT |
| **LimboAI Scope Chain** | Blackboard 作用域嵌套 (全局/场景/单 agent) | 我们不做多 agent 共享 |

#### 核心洞察 (Why Proprioception, Why Now)

1. **LLM 的幻觉根源 = 缺 grounding**: BrainBody-LLM / InCoRo / ELLMER 都指向同一件事——**语言层一旦脱离感知状态就编造**。GOSLO 上我们已经在视觉上踩到 (§3.1 的痛), 在身体状态上还没踩但迟早会踩 (Gemini 说"我飞过去" 但 Unity 其实 FROZEN 了)。
2. **但 LLM 也不能被淹没**: 如果把每一帧、每一次 BT tick、每一次状态机变化都塞进上下文, 配额秒光。
3. **解法 = 分层 Blackboard + 事件驱动注入**: 把所有"事实"汇聚到**一个 Blackboard** (单一真相源), 由 Injector **事件驱动**决定哪些变化需要送到 Gemini、以什么形式、什么节流。

#### GOSLO Blackboard 架构 (四作用域)

参照 LimboAI scope chain + Unreal Blackboard, 分四层, 嵌套、互不覆盖:

```
┌─ Global Scope (跨 session 持久, 从 Graphiti/config 加载)
│  ├─ user_profile (名字, 偏好, 关键记忆索引)
│  ├─ behavior_mode (BASE / COMPANION / ...)
│  └─ persistent_prefs (视觉四级容忍度, 话术风格)
│
├─ Session Scope (本次 LiveKit room 期间活着)
│  ├─ room_id, unity_identity, connected_since
│  ├─ scene (DESKTOP_WEBCAM / AR_HANDHELD)
│  └─ visual_state (active / degraded / paused / blocked) ← §3.3
│
├─ Tick Scope (每次 Unity telemetry / RPC ack 刷新)
│  ├─ body_state (IDLE / FLYING / PERCHING / ...) ← parrot_behavior_rules §1.1
│  ├─ head_state (HEAD_FORWARD / HEAD_LOOK_AT / ...) ← §1.2
│  ├─ cognitive_state (LISTENING / THINKING / SPEAKING) ← §1.3
│  ├─ ar_tracking_state (TRACKING / LIMITED / NOT_TRACKING)
│  └─ last_rpc_ack (success / queued / rejected + reason)
│
└─ Transient Scope (秒级事件, 消费即失效)
   ├─ just_captured_photo (ts, path, pose)
   ├─ hand_gesture_detected (open_palm / closed_fist, 只保留 2s)
   └─ user_interruption (用户插话事件)
```

**读权限**: Injector / Soul / 所有 Python 模块随便读。
**写权限**: 每个字段**钉死由哪个模块写**, 其他模块只读, 避免多头污染。
- `visual_state` → VideoStateManager (§3.1 汇总)
- `body_state` → Unity telemetry 收集器 (不是 Brain 推断)
- `behavior_mode` / `scene` → 显式 RPC 或 tool 触发
- `cognitive_state` → Gemini session handler (turn 开始/结束时更新)

#### 事件驱动注入 (不是每 tick 广播)

参照 Unreal BT "passive listen for events", 而不是 "constantly check"。

**注入策略矩阵** (Injector 读 Blackboard 变化, 决定怎么给 Gemini):

| 状态字段 | 变化时怎么办 | 送进 Gemini 的形式 | 节流 |
|:---------|:------------|:------------------|:-----|
| `visual_state` (§3.3) | 变化即送 | system message: `[video] state=X, reason=Y, since=ts` | 同 state 3s 内不重送 |
| `body_state` | 变化即送, 但仅"重要跳变" (IDLE↔FLYING / FROZEN 进出) | system message: `[body] now FLYING to (x,y,z)` | 事件驱动, 不节流 |
| `scene` | 变化即送 | 换 Soul prompt + system message: `[scene] now DESKTOP` | 罕见, 不节流 |
| `behavior_mode` | 变化即送 | 切 Soul 分支, 并口头提示 | 罕见 |
| `cognitive_state` | **不送** | LLM 自己就是这个状态, 送了是噪音 | — |
| `ar_tracking_state` | 仅变化到 NOT_TRACKING 时送 | 合并进 `visual_state=degraded, reason=ar_lost` | — |
| `last_rpc_ack` | 仅**失败**送 ("你让我飞, 但我被冻住了") | system message: `[action] fly_to rejected: frozen` | 事件驱动 |
| `hand_gesture_detected` | 开始就送, 持续中不重送 | system message: `[input] user showed open_palm` | 去重 |
| `just_captured_photo` | 变化即送 | system message + 可选 tool 回调 | 事件驱动 |

**关键原则** (三条, 都是别人血泪经验):

1. **LLM 是听众, 不是轮询器**。所有状态变化由 Injector 主动 push, Gemini 绝不主动问"我现在什么状态"——它会瞎猜。
2. **仅事件驱动 ≠ 仅瞬时通知**。每次新 turn 开始, Injector 自动把当前 Blackboard 的**快照摘要**作为 turn 开头 system message 附上 (Voyager 模式)。**瞬时事件 + turn 快照**两条路并行, 不冲突。
3. **失败反馈 > 成功反馈**。BrainBody-LLM 的核心洞察: 正常执行不必汇报, 失败必须汇报。Gemini 说了 `fly_to` 但 Unity queued/rejected 了, 必须明确告诉它 (不然它以为飞了)。

#### 🆕 三层意识分发模型 — 潜意识 / 自主行动 / 通报 (2026-04-21 追加, 2026-04-22 升级)

> **缘起**: 用户在 P1/G2/V2 决策中抓住的共同线头 ——
> "GOSLO 了解但不多嘴"、"门控/状态机/行为树/行为模式要统一收口"、"学 SVA 和机器人控制的约束模式"。
> 本节把这个直觉钉死成可落地的工程约束。
>
> **🔥 2026-04-22 关键发现**: 用户提到的 `requirements.md E2` **Reflex/Intent/Task 三级调度** (`scheduler/router.py` 只实现了 2 级, 缺 Intent 中间层)、本节"三层意识分发"、以及 2026 前沿 **CTHA Temporal Hierarchy + NVIDIA GR00T N1.6 System1-System2** —— **是同一个架构思想的三个侧面**。
> 下面 §`三合一统一视图` 做收口。

#### 借鉴的成熟范式 (经典 + 2026 前沿并置)

| 范式 | 年代 | 借过来的关键概念 |
|:-----|:----|:-----------------|
| **Gat 1998 三层架构 (3T)** — NASA Ames + CMU | 1998 | **Deliberator (思考, >1s) / Sequencer (排程, 10-500ms) / Reactive (反射, <10ms)** 三层, 由低到高逐层抽象, 不同时间尺度 |
| **Brooks 1986 Subsumption** | 1986 | 高层**通过 inhibit / suppress 信号**影响低层, 但低层仍是自治的 (低层不必"征得高层同意"即可动作) |
| **🔥 NVIDIA GR00T N1.6** (2025-12) — 机器人界最强开源基础模型 | 2025-12 | **System 1 (Diffusion 动作, 120Hz) + System 2 (VLM 视觉语言, 10Hz) 联合优化** —— 双系统是**工程公认**最强架构, 用于 1X/Agility/Figure/Agibot 等所有主流人形机器人 |
| **🔥 DPT-Agent** (ArXiv 2502.11882) | 2025-02 | System 1 = **FSM + code-as-policy** / System 2 = **ToM + 异步 Reflection**. 关键点: **System 2 通过"生成 code 片段"来更新 System 1 的 FSM**, 不直接下命令 |
| **🔥 CTHA** (ArXiv 2601.10738, ICLR 2026) — 约束式时间层级 | 2026-01 | **3 层时间尺度** (Reflex ms-s / Tactical s-min / Strategic min-hr) + **三个硬约束**: Message Contract / Authority Manifold / Arbiter Resolution. 47% 失败级联减少, 2.3× sample efficiency |
| **HiPER** (ArXiv 2602.16165) | 2026-02 | **Plan-Execute 显式分离** + **Hierarchical Advantage Estimation**, 高层 subgoal + 低层 action 分别 credit assignment |
| **VIGIL** (arxiv 2512.07094) | 2025-12 | **外挂反思层**做 self-healing, EmoBank 记录 soft failure, **不打扰主 agent 对话**, 靠事件日志做异步反思 |
| **agentguard-llm** | 2026 | **失败分类** (RATE_LIMIT / TOKEN_LIMIT / HALLUCINATED_TOOL / SILENT_FAIL) + "retryable 与否"决策表 |
| **MDPI 2025 Semantic Mediation** (Algorithms 18/12/773) | 2025 | **LLM 做仲裁/中介**, 不再是硬编码 priority arbiter; 反射层输出由 LLM 语义融合 |
| **VIRF** (OpenReview wb05ver1k8, ICLR 2026) | 2025-10 | 神经符号混合, **Logic Tutor 通过解释性反馈教 LLM Apprentice 修正 plan**, HAR 0% |

#### GOSLO 三层意识分发模型

把一个"内部事实"(比如视觉掉帧 / 身体冻结 / RPC 失败 / 手势检测) 送到系统里以后, 它应该**被分到哪一层消化**, 有三个选项:

```
┌────────────────────────────────────────────────────────────────────┐
│ 层 ③ 通报层 (Conscious Report)                                     │
│ 把事实显式送进 Gemini system message, 让 Gemini 知道并可以谈论       │
│ 延迟: 立即 (事件驱动, 新 turn 前送达)                                │
│ 代价: 占上下文, 有噪音风险                                           │
├────────────────────────────────────────────────────────────────────┤
│ 层 ② 行动层 (Autonomous Action)                                    │
│ 由 Python 代码或 BT 节点**自主处理**, 处理后**仅写 Blackboard**,    │
│ 不告诉 Gemini (除非处理失败才升级到层③)                              │
│ 延迟: 10-500ms                                                     │
│ 代价: 需要写自主策略, 但一旦写对, Gemini 世界线干净                  │
├────────────────────────────────────────────────────────────────────┤
│ 层 ① 潜意识层 (Subconscious)                                       │
│ 仅写进 Blackboard 历史 + VIGIL 式 Observation Log, Gemini **永不知** │
│ 延迟: 无(旁路, 不阻塞)                                              │
│ 代价: 0, 只为日后审计 / 反思 / 技能蒸馏用                            │
└────────────────────────────────────────────────────────────────────┘
```

**核心原则 (对应用户 P1/G2/V2 的定稿)**:

1. **层①默认吸收, 层②默认处理, 层③只在"不得不"时送**。宁可沉默, 不可吵。
2. **层③的触发条件** (以下任一, 借 agentguard 分类学):
   - **用户感知差异 (User-Observable Divergence)**: Gemini 说了"我会飞过去", 但 Unity 冻住了 — 用户会看见差异, 必须通报。
   - **Gemini 表述基于的事实变化**: 视觉从 active → blocked, Gemini 正在描述画面, 必须通报不然继续幻觉。
   - **多次自主处理失败**: 层②重试 3 次仍失败, 升级到层③。
   - **用户显式操作**: 主动拍照 / 切场景 — 这是用户的"身体动作", 必须让 Gemini 同步。
3. **VIGIL 并行**: 无论层①②③, **每个事件都额外进 Observation Log** (Redis Stream, P3 接 Graphiti), 异步做 soft-failure 反思 + 技能蒸馏。**不阻塞主对话**。
4. **Subsumption 反向**: 层②可以**抑制**层③ (比如 "正在重试中, 别告诉 Gemini"), 层③可以**抑制**层② (比如 "这件事太大, 我直接接管告诉用户吧"); 但任何一层永远不能 suppress 层① (日志一定要全)。

#### 按事件分配 "意识层" (回到我们的实际字段)

| 事件 | 层① 潜意识 | 层② 自主行动 | 层③ 通报 Gemini |
|:-----|:----------|:------------|:-----------------|
| **视频单帧模糊 (<100ms)** | ✅ (进 ObsLog) | ✅ 消费端自跳过 | ❌ 不送 |
| **连续 3s 模糊 → degraded** | ✅ | ❌ | ✅ `[video] state=degraded` |
| **ARCore Tracking LIMITED <5s** | ✅ | ✅ Unity 稳一稳, 不重建 | ❌ |
| **ARCore Tracking NOT_TRACKING >5s** | ✅ | ❌ | ✅ `[video] reason=ar_lost` |
| **body_state: IDLE → LOOKING_AT** (Gemini 自然看了眼) | ✅ | ✅ Unity 自行处理 | ❌ |
| **body_state: IDLE → FROZEN** (资源冲突被踢) | ✅ | ✅ 尝试释放 | ✅ `[body] now FROZEN` |
| **RPC fly_to 被 queue (1s 内清)** | ✅ | ✅ 等完后再 ack | ❌ (如果最终成功) |
| **RPC fly_to rejected (明确拒绝)** | ✅ | ❌ | ✅ `[action] fly_to rejected: out_of_bounds` |
| **识别物体低置信 (<0.6)** | ✅ | ✅ identify_object 自己走 deep_search | ❌ |
| **识别物体两次失败** | ✅ | ❌ | ✅ `[tool] identify_object twice_failed` |
| **手势 open_palm 检测到** | ✅ | ✅ Scheduler 反射发 fly_to_hand | ❌ (动作自然发生, Gemini 看视频自然看到) |
| **用户主动拍照** | ✅ | — | ✅ `[input] photo_captured` (因为用户操作 Gemini 必须知) |
| **App 切到后台 <30s** | ✅ | ✅ Unity 暂停推流 | ❌ |
| **App 后台 >30s** | ✅ | ✅ | ✅ `[session] paused, stream off` + 回来时 `[session] resumed after Xs` |

**读法**: ✅ 表示"这一层需要做事", 事件从左到右升级。同一事件可以同时在多层 (ObsLog 总是记, 自主行动过程中也许最终还要通报)。

#### Soul 话术约束 (V2 决策的升级)

以前想法是"硬写 if visual_state=X then 说 Y", 这是 Brute-force。
**正确做法** (学 Gat 3T 的 Sequencer 层): **Soul 里只写"允许的动作集" + "禁止的断言集"**, 具体措辞由 Gemini 生成。

示例 (伪 prompt, 不是真 code):

```
[visual_state=blocked]
禁止断言: "我看见...", "你桌上有...", 任何画面描述
允许动作: 抱怨被挡 / 请求用户让开 / 从记忆聊 / 安静等
提示语气: 温和疑惑, 不要焦虑
```

这套约束表**本身就写在 Blackboard** (`global/soul_constraints`), Injector 根据当前 visual_state 选择哪张表送进 system message。好处:
- 约束可以热更新 (改 config 不改代码)
- 调试方便 (log 里直接看哪张表生效)
- 扩展性好 (新增 state 只加一张表)

#### 对三个实施文件的影响

| 文件 | 影响 |
|:-----|:----|
| `ar_feature_implementation_plan.md` Sprint 1 | S1.C "visual_state 四级 + Injector" 扩展为"三层意识分发"; 新增 S1.E `ObservationLog` 模块 (Redis Stream) |
| `audit_identify_object_no_screenshot_20260420.md` | 升级 identify_object 的"自主重试 vs 通报"判断按本节分配表 |
| `parrot_behavior_rules.md` | 每条状态转移补一列"对应意识层" |

---

#### 为什么不直接把 Unity 状态机 / 后端 BT 的节点暴露给 Gemini

很诱人, 但是错的:
- **暴露实现细节 = 放大幻觉**: Gemini 看到 `SelectorNode.tick()` 之类会**编造**这些节点的语义。
- **每个节点 tick 都注入 = 配额爆炸**: 现有 py-trees BT 几十个节点, Gemini 会被淹没。
- **Gemini 不需要知道"怎么实现"**: 它只需要知道"现在在什么状态、上一个动作成没成"。

所以 Blackboard 是**抽象边界**: BT/FSM 内部怎么实现随便, 只要把结论写到 Blackboard 的固定字段, Gemini 就能理解。

#### Soul 里怎么消费这些

`soul.py` 的 `get_instructions()` 现在只吃 `mode`, 需要扩展:

```
get_instructions(
    mode: BehaviorMode,     # COMPANION / BASE
    scene: Scene,           # DESKTOP_WEBCAM / AR_HANDHELD
    visual_state: VisualState,   # active / degraded / paused / blocked
    # body_state 不进 instructions, 只进 turn system message (高频变化)
) -> str
```

Instructions 本体写抽象规则 ("当 visual_state=blocked 时必须先抱怨"), 不写具体值 (具体值由 Injector 每 turn 注入)。

#### 这一节和已有文档的关系

| 已有文档 | 本节对它做了什么 |
|:---------|:----------------|
| `parrot_behavior_rules.md` (身体/头部/认知状态表) | **复用**, 它定义了字段枚举值, 本节定义字段怎么流通 |
| `ar_app_plan.md` C1-C12 | C7 (状态机 RPC) / C8 (认知状态) 的落地容器 |
| `audit_identify_object_no_screenshot` | Blackboard 为 identify_object 提供 `visual_state` gate (模糊帧不截) |
| `SKILL.md livekit-unity-video-publish` | 五段接缝里的 "视觉状态回灌" 在本节明确为 Blackboard 写入动作 |

#### 现状代码对齐 (2026-04-21 代码审计)

> 这节不是提议, 是**确认你已经在做的事**。检查下面这张表, 能对上, 证明 §3.5 不是从零起楼, 是往现有地基上加层。

| §3.5 设计点 | 现有代码 | 状态 |
|:-----------|:--------|:----|
| py-trees Blackboard V2 单一真相源 | `src/parrot/scheduler/blackboard.py` 已用 `py_trees.blackboard.Client` + namespace `scheduler` | ✅ 已有 |
| 作用域 / 命名空间 | `BB_NS="scheduler"` + 4 个 key + 每个 key 钉 WRITE 归属 | ✅ 已有, 扩域即可 |
| 事件驱动 Tick | `service.py::_listen_commands` Redis 消息才 tick | ✅ 已有 |
| Selector 回退 (Reflex→Nanobot→Direct) | `router.py` 三叶 Selector | ✅ 已有 |
| BehaviorMode 作为 BB 字段 + Pub/Sub 广播 | `mode_watcher.py` 完整实现, Soul 热切 instructions | ✅ 已有 |
| 跨进程共享 (Brain↔Scheduler↔DSG) | `RedisBlackboardSync` 骨架在, 未接主流程 | 🟡 骨架在 |
| 失败反馈 (Nanobot 任务超时) | `service.py::_check_timeouts` | ✅ 已有 |
| **失败反馈 (RPC ack rejected)** | `_rpc_bridge.py` 未回灌 Blackboard | ❌ 未做 |
| Turn 开头快照摘要 (Voyager 式) | `context_injector.py` 无此逻辑 | ❌ 未做 |
| 视觉状态四级写进 BB | 整个 `vision/state` 域未建 | ❌ 未做 |
| 身体/头部/认知 telemetry → BB | `telemetry_receiver.py` 收了但没写 BB | ❌ 未做 |

**结论**: py-trees Blackboard 的选型事实上已经被代码钉死, 我之前给你四个候选 (dict / Redis / py-trees / 待定) 的 P2 决策点**作废**——**复用现有 py-trees + 扩域 + 补 Redis sync**。

---

#### 🆕 三合一统一视图 — E2 三级调度 × 三层意识分发 × CTHA (2026-04-22)

> **一句话**: 你之前备设计的 `requirements.md E2` **"Reflex / Intent / Task"**、本节新加的"潜意识 / 自主行动 / 通报"、2026 前沿的 **CTHA Temporal Hierarchy + GR00T System1-System2** —— 是**同一个东西, 三个视角**。
> 之所以看着像三个概念, 是因为分别从"调度 / 意识 / 时间尺度"三个轴投影过来。现在要把它们**合并成一个三层结构**, 避免各写各的。

**统一三层结构** (每层只定义一次, 各轴的对应关系固定):

| 层号 | **时间尺度** (CTHA) | **调度层** (E2) | **意识层** (§3.5) | **GR00T 类比** | **代码位置** | **典型事件** |
|:-----|:-------------------|:---------------|:------------------|:---------------|:------------|:-------------|
| **L1** 反射 | ms-s (Reflex) | **reflex** | **潜意识** | System 1 (120Hz) | `scheduler/router.py::HandleReflex` + Unity 本地 | 张手→GOSLO 飞来; ARTracking Lost → 自动切 `VIDEO_GEMINI_ONLY` |
| **L2** 战术 | s-min (Tactical) | **intent** ⚠️**缺** | **自主行动** | — (需自建) | **🆕 `HandleIntent` 节点需新增** | 视频质量连续差 10s → 主动切档; 有人进 scene → 更新 soul_constraints |
| **L3** 战略 | min-hr (Strategic) | **task** | **通报** | System 2 (VLM 10Hz) | `DispatchToNanobot` + `context_injector` + Gemini Live | 用户直接问话; Nanobot 长研究; 异常堆积 → 通报 Gemini |

**关键缺口**: 当前 `router.py` **只有 L1 (HandleReflex) + L3 (DispatchToNanobot / BrainDirect)**, **L2 Intent 层完全缺失**。用户在 `requirements.md E2` 和 `milestone_p2.md` 里已备 PLANNED, 但未实现。

**CTHA 三约束落到我们的工程上**:

| CTHA 约束 | 对应的工程要求 | 在 GOSLO 里具体怎么做 |
|:----------|:--------------|:----------------------|
| **Message Contract Constraints** (层间消息类型化) | 层与层之间只能通过**固定 schema** 的包交流 | Blackboard 的 **3 个作用域 key 就是 Contract** — `vision/*`, `body/*`, `session/*` 只写定义好的字段, 不写自由 dict |
| **Authority Manifold Constraints** (每层只能在自己的时间尺度做决策) | L1 不准 await long tool, L3 不准直接操作 body | `soul_constraints` 表按"**可调 tool 集**"分层: L1 只能写 reflex_direct, L2 只能改 mode/video_tier, L3 才能调 web_search/dispatch_task |
| **Arbiter Resolution Constraints** (冲突仲裁) | 多层同时要动身体时, 按**优先级 + 时间紧急度**仲裁 | `ResourceLockManager` (requirements.md E5, 也是 PLANNED) —— body 通道互斥, L1 > L2 > L3, 高层只能"取消"低层动作, 不能"抢占正在执行的 L1" (Brooks Subsumption) |

**落到 Sprint 1 的影响** (不推翻原计划, 只补一个任务组):

| 追加任务 | 位置 | 与已列任务的关系 |
|:---------|:-----|:----------------|
| **S1.F — E2 Intent 层补全** (新增) | `src/parrot/scheduler/nodes.py` 加 `HandleIntent` + `router.py` Selector 从 3 叶改 4 叶 (Reflex → Intent → Nanobot → BrainDirect) | 是 S1.C "意识分发器 dispatcher.py" 的**调度层双胞胎** — dispatcher 决定"该送哪层", router 决定"该谁干" |
| **S1.G — Arbiter/ResourceLock 最小版** (新增) | `scheduler/locks.py` (requirements.md E5 PLANNED) | body 通道三层优先级互斥, 只做**最简版** (不实现完整的抢占协议, P3 再扩) |

这两项不是"新加了两个 Sprint", 是把 E2/E5 这两个早就备在 `requirements.md` 里的 PLANNED 项**顺手落到 Sprint 1**, 因为它们和三层意识分发是**同一个结构**, 分开做反而要改两次代码。

---

#### 待你确认 (修订, P1-P4 精简为 P1-P2)

- ~~P1 (原)~~: ✅ 底座架构已隐含采纳 (代码已跑通), 无需再决策
- ~~P2 (原)~~: ✅ py-trees (c 选项) 已事实选定, 无需再决策
- **P3**: 失败反馈的颗粒度——每次 RPC ack 失败都送, 还是连续失败 N 次才送? (改为 P1)
- **P4**: turn 开头快照摘要是否加 (Voyager 式)? (改为 P2)
  - 利: Gemini 不会在长对话中"忘记"身体状态
  - 弊: 每 turn 固定消耗一段 token

---

### 3.6 DSG 工作模式 + 视频流档位 — 两轴正交设计

> **你补上的最关键一块**: A10 关闭时 DSG 不该停摆, 也不该切换物理位置 (笔记本 Sentinel 跨太平洋延迟 + 时间戳对齐成本太高 → P4 备选)。
> **DSG 永远跑在 Castle 2C8G**, 变的是**上游 L1.5 数据源**和**视频流档位**, 这是两个**正交**的开关。

#### 核心澄清 (把你之前的 Sentinel 表述纠正清楚)

- **Sentinel ≠ 笔记本**, Sentinel 是"**L1.5 轻量 CV**"这个**档位**, 物理上跑在哪由算力决定
- **笔记本跑 CV 喂 Castle DSG** = P4 备选方案 (东京回程延迟 + 时间戳对齐, 成本太高)
- **DSG 本体始终在 Castle 2C8G**, A10/笔记本/未来任何 CV 服务只是 L1.5 数据的**可插拔来源**
- 所以这里要设计的不是"DSG 在哪跑", 而是"**上游断了/降级了, DSG 自己怎么换档**"

#### 两个正交轴

**轴 A — VideoTier (Unity 推什么 + Python 订什么)**

| Tier | 推流码率 | 分辨率 | fps | Gemini 订阅 | Python CV 订阅 | 何时用 |
|:-----|:--------|:-------|:----|:------------|:--------------|:------|
| `VIDEO_OFF` | 0 | — | 0 | ❌ | ❌ | 纯语音对话 / 用户显式关摄像头 / 省流量 |
| `VIDEO_GEMINI_ONLY` | ~500kbps | 640×480 | 10 | ✅ | ❌ | **A10 关**, 只让 Gemini Live 看, CV 管线不开 |
| `VIDEO_FULL` | ~1.5Mbps | 1280×720 | 30 | ✅ | ✅ | A10 开, SAM2+DINOv2 要消费帧 |
| `VIDEO_BURST` | 短时 `VIDEO_FULL` | 同上 | 30 | ✅ | ✅ | 只在 identify_object / 摄影触发时临时拉满 (P3+) |

**轴 B — DsgMode (DSG 内部工作模式)**

| Mode | L1.5 来源 | 过滤器路径 | 写什么 Node | 什么 Trigger 启用 | 何时用 |
|:-----|:----------|:----------|:-----------|:-----------------|:------|
| `DSG_TEXT_ONLY` | Gemini 口述 / identify_object / user tag (Obsidian) | 文本事实过滤器 | `CONFIRMED` (权威来源) | calendar / message / ssot_enrichment | **A10+视频全关**, 纯对话 |
| `DSG_GEMINI_VISION` | Gemini "看到了紫色杯子"转写 / identify_object | 文本+视觉断言过滤器 (防幻觉, 见下) | `TENTATIVE`→`CONFIRMED` | + scene_context | **A10 关, 视频只给 Gemini** |
| `DSG_FULL` | SAM2 全分割 + DINOv2 ReID + YOLO 探测 + 三层缓冲 | L1 粗过滤 + ExpectationChecker | 全量, NEW/MISSING/DISPLACED | 全部启用 | A10 在 |
| `DSG_SENTINEL_AUX` (P4 备选) | 笔记本 YOLO-World 低权重探测 | 延迟容忍过滤器 | `UNCERTAIN` 低权重 | 全部 | 备选, 跨太平洋延迟高 |

#### 轴 A × 轴 B 的合法组合

不是所有组合都有意义, 合法组合只有以下五种:

| # | 组合 | 场景 | 注意 |
|:--|:-----|:-----|:-----|
| C1 | `VIDEO_OFF` + `DSG_TEXT_ONLY` | 省电/通勤/省流量 | GOSLO 明确知道"我闭眼了" (§3.3 视觉状态 paused) |
| C2 | `VIDEO_GEMINI_ONLY` + `DSG_GEMINI_VISION` | **A10 不开的默认档** | 视频流省一半带宽, CV 管线完全不开, DSG 靠 Gemini 口述回灌 |
| C3 | `VIDEO_FULL` + `DSG_FULL` | A10 开, 满血 | P3+ 主力档 |
| C4 | `VIDEO_FULL` + `DSG_GEMINI_VISION` | A10 暂停但视频未降档 (调试期) | 过渡态, 不该常驻 |
| C5 | `VIDEO_BURST` + `DSG_FULL` | 按需拉满 (摄影/identify_object) | P3+, `VIDEO_BURST` 自动回到 `VIDEO_GEMINI_ONLY` |

**非法组合** (要在代码里禁掉): `VIDEO_OFF + DSG_GEMINI_VISION` (CV 收不到帧还想做视觉断言)、`VIDEO_GEMINI_ONLY + DSG_FULL` (CV 管线没帧可吃)。

#### "文本事实过滤器" — A10 关掉时 DSG 的核心组件

> 你原话: **"纯文字流程只要在有效期过滤器模块哪里设计就好了对吧"** —— ✅ 完全正确, 这就是下面这层。

当 DsgMode = `DSG_TEXT_ONLY` 或 `DSG_GEMINI_VISION` 时, L2-B 节点的写入**只有三个合法源**:

```
┌─ Source 1: Gemini 口述转写 (DSG_GEMINI_VISION 模式才启用)
│   "你桌上那个紫色杯子" → 过滤器抽取 → SemanticNode(label="紫色杯子", confirmation=TENTATIVE)
│   过滤规则:
│     - 只提取显式"名词短语 + 位置介词"模式 (不用 LLM 二次分析)
│     - 抽到的节点强制 TENTATIVE, 不可直接 CONFIRMED (防 Gemini 幻觉)
│     - 30s 内若 Gemini 再次提及同一名词 → 升 CONFIRMED
│     - 60s 无复述 → 降 UNCERTAIN, 10min 无复述 → GHOST 清理
│
├─ Source 2: identify_object 命中 (所有模式都启用)
│   权威最高, 直接 CONFIRMED, 可升级其他来源的同名节点
│
└─ Source 3: user 手动标签 (Obsidian 双链同步, 所有模式都启用)
    obsidian_uuid 钉死, 人工标注永不被 GHOST 清理
```

**这个过滤器在代码里叫什么**: 建议命名为 `parrot.dsg.ingest.text_source_filter`, 放在新建的 `dsg/ingest/` 子包里 —— 它是**上游数据进 L2-B 之前的唯一闸门**。

#### DSG 内部 L1.5 数据流 (放在这里, 因为 DsgMode 决定了哪条路开)

```
┌────────────────────────────┐
│ 外部 L1.5 数据源 (可插拔)   │
└──────┬─────────────────────┘
       │
   ┌───┴────────┬───────────────┬────────────────────────┐
   ▼            ▼               ▼                        ▼
 Gemini      identify_object  SAM2/DINOv2/YOLO        user tag
 口述转写     tool 命中       (A10 only)              (Obsidian)
   │            │               │                        │
   └────┬───────┴───────┬───────┴────────────────────────┘
        ▼               ▼
  ┌──────────────────────────────┐
  │ Ingest 过滤器层               │
  │ ├─ text_source_filter         │  ← DsgMode 决定哪条启用
  │ ├─ tool_result_filter          │
  │ ├─ cv_track_filter (A10 only) │
  │ └─ user_tag_filter             │
  └──────┬───────────────────────┘
         ▼
    ┌────────────────────┐
    │ L2-B 语义图 (共用)  │ ← 所有 DsgMode 共用同一张图
    └────┬───────────────┘
         ▼
    ┌────────────────────┐
    │ L3 氛围语义 (共用)  │ ← 同样共用, 不依赖视觉
    └────────────────────┘
```

**关键点**: **L2-B / L3 永远不换**, 换的是 Ingest 过滤器层的**启用集合**。这也正是你说的 "**DSG 本来就跑在 2C8G**" —— DSG 核心 (L2-B/L3/triggers) 跑在 Castle, L1.5 源谁在线用谁。

#### 切换时机 (谁来决定换档)

- **启动时**: Brain 读 config → 查 A10 健康端点 (ping) → 决定初始 `(VideoTier, DsgMode)`
- **运行时自动降档**: A10 心跳失败 30s → 自动 C3→C2 (`DSG_FULL`→`DSG_GEMINI_VISION` + `VIDEO_FULL`→`VIDEO_GEMINI_ONLY`) → 系统 message 告诉 Gemini "大脑的视觉辅助休息了, 我现在用你看到的描述记事"
- **运行时升档**: A10 再次可达 60s → C2→C3, 但**必须等**当前对话轮次结束再切 (避免 instruction 抖动)
- **用户主动**: `set_mode` tool 或 `set_video_tier` RPC 手工拨

#### 代码层面的落点 (给未来实现)

```
shared/tiers.py                   ← 新增: VideoTier, DsgMode 两套枚举 (只做 P2)
dsg/ingest/                       ← 新增: 过滤器子包
  text_source_filter.py
  tool_result_filter.py
  cv_track_filter.py              ← 占位, A10 来了再填
  user_tag_filter.py
dsg/mode_controller.py            ← 新增: DsgMode 状态 + 切换时开关过滤器
brain/perception_supervisor.py    ← 新增: A10 健康检测 + 自动降档
brain/tools/set_video_tier.py     ← 新增: RPC 给 Unity 调整推流档位
Unity/ARVideoPublisher.cs         ← 扩展: 接收 RPC 动态调整码率/分辨率/fps
```

#### 与 §3.1 门控三层的关系

三层门控 (Unity 产地 / LiveKit 路上 / Python 消费端) **全部都在**, 但在不同 `VideoTier` 下**权重不同**:
- `VIDEO_OFF`: 三层全闭嘴 (没流可关)
- `VIDEO_GEMINI_ONLY`: Unity 产地 + LiveKit 路上 门控生效, Python 消费端不介入 (因为 CV 管线关了)
- `VIDEO_FULL`: 三层全开, Python 消费端做模糊/亮度过滤
- `VIDEO_BURST`: 临时开 `VIDEO_FULL`, burst 结束自动回档

#### 待你确认

- **M1**: 两轴正交 (VideoTier × DsgMode) 的这个设计接受吗? 还是合并成一个 `PerceptionTier` 枚举 (但会失去正交性, 比如"视频开但 CV 先暂停做调试")
- **M2**: `DSG_TEXT_ONLY` 下是否允许 Gemini 口述节点写入 (带 `TENTATIVE` 防护)? 你之前倾向"只把纯文字对话结果扔到过滤器加 graphiti"——那这条其实是 `DSG_GEMINI_VISION`, 而 `DSG_TEXT_ONLY` 连 Gemini 口述都不要, 只有 identify_object + user tag
  - [ ] (a) 严守, `DSG_TEXT_ONLY` 完全不吃 Gemini 口述 (更干净, 但会在"视频关对话中"丢失新节点)
  - [ ] (b) 吃, 但标 `SOURCE=gemini_oral` 并强制 TENTATIVE
- **M3**: A10 健康检测由谁做?
  - [ ] (a) Brain 自己 ping (简单)
  - [ ] (b) Bus 框架统一做 (和 heartbeat 集成)
  - [ ] (c) 专门的 Supervisor 进程
- **M4**: 自定义模式的需求强不强? 我建议**不做**——4 种标准模式 + 2 个正交轴已经能覆盖 2×4=8 种组合中合法的 5 种, 自定义会让 Soul prompt 分支失控。你是否同意?

---

## 四、花哨玩法 (问卷已出, 在此只做架构钩子回顾)

详细选项见 `ar_camera_interaction_survey.md`。此处只回答: **玩法怎么挂在 §三 的基底上**。

| 玩法 | 基底依赖 | 新加的架构钩子 |
|:-----|:---------|:--------------|
| 摆 pose + 截图 | §3.3 视觉级 active (糊帧不拍) + §3.1 Python 消费端独立 | `captureSnapshot` RPC + `SnapshotService.cs` |
| 双图分离 (美化/原图) | §3.4 Scene (DESKTOP vs AR 不同滤镜) | Unity RenderPipeline 分层, UI/Parrot/World 三层可独立读回 |
| 照片时间轴 TBM | §3.3 注入的 system message 自带时间戳 | Graphiti `PhotoEvent` 节点 + `SemanticNode.reference_image_path` (audit §5.1 B4) |
| 光遇式空间锚 | §3.4 `AR_WORLD_LOCKED` Scene | P3, 需 ARWorldMap + 位置持久化 (不做) |
| 识物闭环 | §3.1 三层门控 + §3.3 视觉级 | audit 报告 §5 的 L0-L2 三段 |

**不变的原则**: 玩法可以重写, 基底不能。

---

## 五、数据流 & 架构收口清单 (需要设计什么来支持以上功能)

> 这一节是给未来实现者的合同。不是代码, 是**需要新增/修改的架构元素清单**。
> **优先级**: 🔴必须 P2.5 / 🟡 P3 可延 / 🟢 P4+ 储备

### 5.1 Unity 侧

| # | 元素 | 位置 (现有 or 新增) | 优先级 | 依赖 |
|:--|:-----|:-------------------|:-------|:-----|
| U1 | `onVideoDegraded(reason, ts)` RPC 方法 | 新增 `VideoStateReporter.cs` | 🔴 | 无 |
| U2 | `captureSnapshot(max_kb, resolution)` RPC 方法 | 新增 `SnapshotService.cs` | 🔴 | audit B1 |
| U3 | `setScene(scene_name)` RPC 方法 (Unity→Brain 主动告知) | 复用 `_rpc_bridge.py` | 🔴 | 无 |
| U4 | 产地门控协程 (亮度方差 / 静止检测 / TrackingState 监听) | `ARVideoPublisher.cs` 扩展 | 🔴 | U1 |
| U5 | `OnApplicationPause` hook → Room.Disconnect + State 上报 | 新增 `AppLifecycleManager.cs` | 🔴 | U1 |
| U6 | AR 路径首帧 warmup Blit (对齐 Webcam 路径) | `ARVideoPublisher.cs` | 🟡 | 真机阶段 |
| U7 | 视觉分离: 相机渲染时分层 (UI/Parrot/World Raw) | Unity Camera Stack | 🟡 | 视觉双图需求确认 |
| U8 | Scene 切换接收: 收到 Brain 的 `setSceneInstruction` → 切换前端表现 | `SceneProfileManager.cs` | 🟡 | S1 确认 |
| U9 | 后台超时 (≥3min) 后 AR Session Reset 策略 | `AppLifecycleManager.cs` | 🟡 | L1 确认 |
| U10 | Android Foreground Service (CAMERA 类型, 切后台保持采集) | AndroidManifest + Service.cs | 🟢 | 真机 |

### 5.2 Python Brain 侧

| # | 元素 | 位置 (现有 or 新增) | 优先级 | 依赖 |
|:--|:-----|:-------------------|:-------|:-----|
| B1 | `VideoStateManager` (融合三层信号 → 向 Gemini 注入 system msg) | 新增 `brain/vision/state.py` | 🔴 | U1 |
| B2 | LiveKit session 订阅 `TrackMuted` / `ParticipantDisconnected` | `brain/agent.py` session handler | 🔴 | 无 |
| B3 | `capture_current_frame() -> bytes` (封装 U2, 超时+降级) | 新增 `brain/vision/snapshot.py` | 🔴 | U2, audit B2 |
| B4 | Context Injector 新增 `visual_state` 通道 | `brain/context_injector.py` 扩展 | 🔴 | B1 |
| B5 | `Soul.get_instructions(mode, scene, visual_state)` 三参数化 | `brain/soul.py` | 🔴 | B1 |
| B6 | identify_object 改造: 按 §3.1/§3.3 升级 L0-L2 | `brain/tools/identify_object.py` | 🔴 | B3, audit §5 全部 |
| B7 | 消费端门控: Python 收帧后亮度/锐度判断 (给 DSG Worker 用) | 新增 `brain/vision/visual_gate.py` | 🟡 | 无 |
| B8 | `set_scene` tool (Gemini 可主动要求切场景, 可选) | 新增 `brain/tools/set_scene.py` | 🟡 | S2 确认 |
| B9 | Scene 感知的 Soul prompt 分支 | `brain/soul.py` 扩展 | 🔴 | B5 |
| B10 | **`GosloBlackboard` 单一真相源** (四作用域, 见 §3.5) | 新增 `brain/state/blackboard.py` | 🔴 | 无 |
| B11 | **`StateInjector` 事件驱动** (订阅 Blackboard 变化 → 决定送不送 / 怎么送) | 新增 `brain/state/injector.py` | 🔴 | B10, B4 |
| B12 | Unity telemetry ingress → 写 `body_state` / `head_state` / `ar_tracking_state` | `brain/_rpc_bridge.py` 扩展 | 🔴 | B10 |
| B13 | RPC ack 失败反馈路径 (Unity queued/rejected → Blackboard `last_rpc_ack` → Injector) | 贯通 U1/B12/B11 | 🔴 | U1, B11 |
| B14 | Turn 开头快照摘要 (Voyager 式, 可配置开关) | `brain/state/injector.py::on_turn_start()` | 🟡 | P4 决定 |
| B15 | **`VideoTier` / `DsgMode` 枚举** + 合法组合校验 | 新增 `shared/tiers.py` | 🔴 | M1 确认 |
| B16 | **DSG Ingest 过滤器层** (text/tool/cv/user_tag 四过滤器) | 新增 `dsg/ingest/` 子包 | 🔴 | M2 确认 |
| B17 | **`DsgModeController`** — 按模式开关过滤器 + 控制 Trigger 启用集合 | 新增 `dsg/mode_controller.py` | 🔴 | B15, B16 |
| B18 | **`PerceptionSupervisor`** — A10 健康探测 + 自动降档/升档 (轮次结束才切) | 新增 `brain/perception_supervisor.py` | 🔴 | M3 确认 |
| B19 | **`set_video_tier` RPC** (Brain → Unity 主动调推流档位) | 新增 `brain/tools/_rpc_bridge.py` 扩 + Unity `ARVideoPublisher.cs` | 🔴 | U1 |
| B20 | Unity 侧动态码率/分辨率切换 (不重建 Track) | `ARVideoPublisher.cs` 扩展 | 🔴 | B19 |
| B21 | **Gemini 口述名词抽取器** (DSG_GEMINI_VISION 下喂 text_source_filter) | 新增 `dsg/ingest/gemini_transcript_extractor.py` | 🔴 | B16 |
| B22 | **降档通知话术**: 降档时由 Injector 注入 system message (Soul 按 DsgMode 分支话术) | `brain/state/injector.py` + `soul.py` | 🔴 | B5, B18 |

### 5.3 Graphiti / DSG 侧

| # | 元素 | 位置 | 优先级 | 依赖 |
|:--|:-----|:-----|:-------|:-----|
| G1 | `SemanticNode` 新增字段 `reference_image_path`, `last_sighting_path` | `dsg/l2b_types.py` | 🔴 | audit B4 |
| G2 | `PhotoEvent` 节点类型 (时间轴用) | 新增 `dsg/l2b_types.py` 或 `memory/*` | 🟡 | 问卷 D 确认 |
| G3 | `data/snapshots/objects/{uuid}/reference.jpg` 落盘约定 | `.gitignore` + Castle docker volume | 🔴 | audit B3 |
| G4 | `data/photos/{date}/{ts}.jpg` 用户照片落盘 | 同上 | 🟡 | 问卷 C 确认 |
| G5 | `visual_state_history` 轻量记录 (可选, 调试用) | Redis Stream or 内存环 | 🟢 | B1 |

### 5.4 配置 / 部署 / 依赖

| # | 元素 | 位置 | 优先级 |
|:--|:-----|:-----|:-------|
| D1 | `livekit-agents[images]` 钉进 requirements | `pyproject.toml` | 🔴 硬修 |
| D2 | `.env` / `config.py` 新增 Scene 默认值 + 视觉门控阈值 | `shared/config.py` | 🔴 |
| D3 | Castle docker volume for `data/snapshots/` 持久化 | `infra/docker-compose.yml` | 🔴 |
| D4 | 开发流程硬记: 不要连续 Play/Stop (<30s) | `commit_guidelines.md` or README | 🔴 软约定 |
| D5 | `skills/livekit-unity-video-publish/SKILL.md` 扩写门控三层 | 现有 skill | 🟡 |

### 5.5 不列但可能遇到的遗留

- 多端 RPC 路由 (同一房间两个 unity-* identity) — 记在 `active_context.md` 已知风险, 本次不做
- Token 过期自动刷新 — P3
- ARWorldMap / LiDAR 碰撞 — P3+ (lore/ideas.md 已登记)
- XR Hands 手势快速反射 — P3 (不阻塞本期)

---

## 六、决策清单 — 用户定稿 (2026-04-21)

> **规则**: ✅ = 用户定稿 / 🔶 = 需要 AI 跟进 / 📱 = 进菜单 / 📝 = 记录后续可添加。
> 用户已在 2026-04-21 本节过完一遍。标 📱 的项会进 Sprint 3 的菜单规划顺手做一个壳。

### 6.1 自知底座 (P1-P2)

| # | 问题 | 定稿 | 备注 |
|:--|:-----|:-----|:-----|
| **P1** | RPC ack 失败反馈颗粒度 | ✅ **学 SVA / 机器人控制的"潜意识 vs 行动 vs 通报"三层划分**, GOSLO 了解但不多嘴 | 不再是单纯的去重策略, 升级成**失败后是"潜意识消化" / "自主行动 (重试/变通)" / "必须通报用户"** 三分支; AI 调研后补进 §3.5 自知架构 |
| **P2** | Turn 开头快照摘要 | ✅ **要** | 同样学 SVA 工程经验 — 快照里哪些字段是"背景潜意识" / 哪些是"必须显式告诉 Gemini" |

### 6.2 工作模式 (M1-M4)

| # | 问题 | 定稿 | 备注 |
|:--|:-----|:-----|:-----|
| **M1** | 两轴正交 (VideoTier × DsgMode) | ✅ 默认 (接受) | — |
| **M2** | DSG_TEXT_ONLY 下吃 Gemini 口述 | ✅ 默认 (吃但标 TENTATIVE) + 📱 **进菜单** (让用户能关掉, 纯开发/调试时禁用口述入库) | Sprint 3 菜单留开关 |
| **M3** | A10 健康探测由谁 | ✅ AI 决定 — **(a) Brain 自己 ping, 但抽成独立 `PerceptionSupervisor` 类 (单文件, 约 80 行), 方便 P3 搬到 Bus 作 Processor** | 既不膨胀 2C8G, 又为 P3 留搬家口子 |
| **M4** | 自定义模式 | 📝 **先不做, 记录到 `lore/ideas.md` 待后续可添加** | 未来如果"创作模式" / "低耗模式"等有明确业务需求再加 |

### 6.3 门控三层 (G1-G2)

| # | 问题 | 定稿 | 备注 |
|:--|:-----|:-----|:-----|
| **G1** | 三层协作 | ✅ 默认 (Sprint 1 做产地+消费端简版, LiveKit 事件层 P3) + 📝 **记录后续可添加 LiveKit 路上层** | — |
| **G2** | 视觉状态暴露机制 | ✅ **升级为"统一状态收口"** — 学 SVA / 机器人控制, **视觉门控 / 身体状态机 / 行为树 / 行为模式这四个都是把内部状态暴露给 Gemini Live 的不同面, 不能各自散落**, 必须由 §3.5 自知架构统一收口 | 这是本次讨论最关键的洞察, AI 会在 §3.5 补一小节"统一收口原则"并调整 Sprint 1 任务形状 |

### 6.4 后台生命周期 (L1-L2)

| # | 问题 | 定稿 | 备注 |
|:--|:-----|:-----|:-----|
| **L1** | 后台超时 AR Session Reset 阈值 (3min) | ✅ 默认 + 📱 **进菜单** (开发者选项可调) | — |
| **L2** | 回来打招呼 | ✅ + **可以加视觉标识/动画** — 回来时 GOSLO 做一个"醒了一下"的小动画 (展翅/眨眼), 配合 >30s 才口头招呼 | 动画需求进 Sprint 3 动画清单 |

### 6.5 视觉自我感知 (V1-V3)

| # | 问题 | 定稿 | 备注 |
|:--|:-----|:-----|:-----|
| **V1** | 四级颗粒度 | ✅ **先把必要的 4 级分好 (active/degraded/paused/blocked)**, 后续根据鹦鹉行为模式和状态机变化再调整 | P2 阶段不加第 5 级; 如果发现 `degraded` 太粗, 再拆子状态 |
| **V2** | Soul 强制话术 | ✅ **学 SVA / 机器人控制的状态机约束模式** — 不是硬写 if-else 话术, 而是参考机器人控制里"状态 → 允许的动作集"的约束表达 | AI 调研后写进 §3.5 |
| **V3** | 失明时撑对话策略 | ✅ 默认 (从 Graphiti 拉最近记忆) | — |

### 6.6 Scene / Mode (S1-S2)

| # | 问题 | 定稿 | 备注 |
|:--|:-----|:-----|:-----|
| **S1** | P2 Scene 范围 | ✅ **DESKTOP_WEBCAM + AR_HANDHELD** (和默认一致) | — |
| **S2** | Scene 切换归谁 | ✅ **Unity 配置决定, Brain 只接收** (和默认一致) | AI 注: P3 可以加 "Brain 基于 L3 氛围判断主动建议切场景 (但需用户确认)", 目前不做 |

### 6.7 UI 风格三选一 — AI 给评估

| 风格 | AI 完成把握 | 契合度 | 风险 |
|:-----|:----------|:------|:----|
| **Minecraft 原汁原味** (像素 + 体素) | ⭐⭐ 中 | 和 GOSLO 鹦鹉模型一致, 但在 AR 手机屏上**像素 UI 会显得粗糙** | 小字不清, 需要每个组件自制像素 sprite |
| **动森 / 宝可梦卡通** (圆润 + 腮红 + 厚描边) | ⭐⭐⭐ 高 | 最适合"虚拟宠物 + 打招呼"情感定位, 且有大量开源 UI 参考 | 需要插画素材, 但 Unity UI Toolkit + Asset Store 够用 |
| **Apple App 风格** (极简 + SF Pro + 半透明玻璃) | ⭐⭐⭐⭐ 最高 | **AI 最有把握** — 纯 CSS/USS 可实现, 无需任何外部素材 | 情感温度偏低, 但抽屉菜单 + 长按呼出恰好是这种风格的标配 |

**AI 推荐**: ✅ **保底用 Apple 风格** (我最有把握一次做好), 但**预留 Theme 切换接口** (USS 文件切换), 等 P3 你艺术感觉成熟了, 可以直接补"动森皮肤 pack"。

### 6.8 菜单顺手规划 (把上表 📱 项汇总)

进 Sprint 3 的菜单包括:
- 开关: 是否允许 Gemini 口述入 DSG (M2 📱)
- 数值: 后台超时阈值 3min (L1 📱)
- 主题: UI Theme 切换 (6.7 预留)
- 选择: VideoTier 手动下拉 (OFF / GEMINI_ONLY / FULL — 开发者调试用)
- 开关: 是否在 `paused`/`blocked` 时强制话术 (V2 调试开关)

菜单骨架 1 个 `SettingsDrawer.uxml`, 内部分 `General` / `Developer` / `About` 三 Tab。**不做完整设置页**, 只先有入口和 5 个开关。剩下的后面补。

---

## 七、还需要查更多资料吗

**我目前掌握的资料**:
- VRChat / 光遇 / 宝可梦 GO / Monster Hunter Now 的 AR 相机玩法 (§已整合到 survey)
- ARCore / ARKit 官方生命周期 + 真实踩坑记录 (§3.2 已钉死)
- RFC 9317 流媒体 QoE + Netflix VBR + 多方视频联合自适应 (§3.1 三层门控的学术印证)
- 虚拟宠物论文 (Stanford / NSF / Auki) — 场景感知, 占位, 拟人化
- **MASMP (ArXiv 2510.18395) / BrainBody-LLM (2402.08546) / InCoRo (2402.05188) / ELLMER (Nature MI 2025) / Voyager** — LLM + 机器人/游戏 AI 的状态 grounding 范式 (§3.5 自知架构的前沿印证)
- **Unreal BT + Blackboard / LimboAI Scope Chain / Flax Behavior Knowledge** — 游戏 AI 的成熟 Blackboard 设计 (§3.5 四作用域的工程印证)
- **现有代码库审计** (2026-04-21): `scheduler/blackboard.py` / `scheduler/router.py` / `scheduler/nodes.py` / `scheduler/service.py` / `dsg/triggers/*` / `brain/context_injector.py` / `brain/mode_watcher.py` / `dsg/l2b_types.py` — 确认 py-trees + Blackboard + Selector 已跑通, 过滤器层 / 模式控制器 / A10 健康探测是净增

**还可以补但此刻不必须**:
- **[可选] Niantic Lightship ARDK** — 如果你认真考虑 P3 的"多人同场 AR"(光遇式 Presence), 再去调研
- **[可选] Apple Vision Pro / Quest Passthrough 最佳实践** — 如果你未来考虑头显版本
- **[可选] Spout/NDI 视频桥** — VRChat 用, 我们短期不会用, 但未来给"把 Unity 画面投屏到第三方"留钩子

**我的建议**: 目前信息已经**足够支撑 P2.5 完整实现**。再查会拖延。等你回答 §六的清单后, 我们直接进入 audit 报告升级 + 代码设计。

---

## 八、问卷 Gap 回填 (针对 ar_app_plan §三 / ar_camera_interaction_survey)

> 这一节只针对**用户留了 TBD 或"你帮我答"的问题**。其他已打勾项不重复。

### 8.1 桌面场景 (ar_app_plan A2) — 桌面场景具体要完成哪些部分

P2 桌面 AR 目标 = **一个能稳定放在桌面并跟你对话的鹦鹉**。不做墙面/地面。拆 6 件事:

1. **AR Foundation Plane Detection** 限定到 `PlaneDetectionMode.Horizontal` (省电, 桌面够)
2. **最小平面大小过滤** ≥ 0.3m × 0.3m (过滤掉误检的书本角)
3. **点击放置** (对齐 D14 答案): 用户点检测到的桌面 → 发射 ARRaycast → `ParrotController.Place(hitPose)`
4. **放置后锚定** `ARAnchor` — 即便短时 tracking limited, 鹦鹉位置不漂
5. **桌面安全区**: 鹦鹉 flyTo 目标 Y ≥ 平面 Y + 0.02m, X/Z 在平面 bounds 内 (不会飞出桌子掉进虚空)
6. **Editor Webcam 路径**: 无 AR 平面时, 鹦鹉放在一个虚拟平面 `y=0` 上 (这样 Editor 也能调动画)

### 8.2 Editor Webcam 长期保留 (ar_app_plan B9) — 我的立场: **必须保留**

理由 (给你 3 条):
- 每次改 C# 代码都要插手机测 → **开发速度降 5-10 倍**
- 夜里/没有 AR 设备/远程办公 → 没 Editor 就完全不能开发
- CI/自动化测试只能跑 Editor 模式

建议: `SceneProfileManager` (已在 §5.1 U8) 把 `DESKTOP_WEBCAM` 作为**一等公民**, 不是 fallback。

### 8.3 LiveKit Token 方案 (ar_app_plan B11) — 推荐方案

对齐 LiveKit 官方最佳实践 + Castle 已有 Nginx + 你的个人项目规模:

**推荐: 在 Castle 上跑一个极小的 Token Mint HTTP 端点 (`/mint`)**
- 实现: FastAPI 10 行, 复用 `livekit.api.AccessToken` 已在仓库
- 认证: 简单 `X-Parrot-Key` header (.env 里硬编码 UUID, 足够个人项目)
- Unity 端: 启动时 POST `https://castle.your-domain/mint?identity=unity-xxx` 拿 token, 24h 过期
- 降级: 拿不到时回退读 `Assets/StreamingAssets/parrotdev.json` (当前 dev 方案)

**不推荐**: 内嵌 API Key 到 Unity (泄漏) / 每次手写 token (UX 不可接受)
**P3 升级路径**: 过期前 60s 自动 re-mint (`TokenRefreshService.cs`)

### 8.4 动画方案 (ar_app_plan E17-E18) — 不用你找 Minecraft 代码

P2 MVP 必做 4 个动画: **`idle / fly / perch / head_bob`** (land 可合并进 perch, dance/thinking 推 P3)

**实现策略 (程序化 + 关键帧混合)**:
- `idle`: 程序化正弦呼吸 (已有 pulse 拓展, 无需关键帧)
- `head_bob`: 程序化点头 (`SPEAKING` 状态触发)
- `fly`: `ParrotController.FlyTo` 已有贝塞尔曲线骨架, 补翅膀拍动程序化抖动
- `perch`: 落到手指/桌面时锁住 transform, 加一个轻微尾羽摇动 (程序化)

**不做的事**: Mixamo (鸟骨骼不适配) / 你手搓 Minecraft 方块动画 (P2 不值当) / 我写复杂 Animator Controller (程序化够了)

**给你找代码参考是浪费时间** — Minecraft 鹦鹉的拍翅是 2D 双帧切换, 不适合你的 3D 骨架模型。

### 8.5 UI 设计 (ar_app_plan E20) — 你先画一张草图, 我接

我能力评估:
- ✅ 能做: UIToolkit (UXML+USS) / TextMesh Pro / 布局 / 交互逻辑
- ⚠️ 弱: **整体美学决策** (主色调 / 字体 / 圆角大小) — 这属于品味, AI 做出来都中规中矩

建议流程:
1. **你只给 3 样**: 主色 (我猜深灰 + GOSLO 的紫橘?), 字体倾向 (粗圆? 细衬线?), 是否有描边/玻璃拟态
2. **我做**: 启动页 / 菜单抽屉 / 便签条 / 错误提示 四个组件
3. **验证**: Editor 截图给你看, 不满意我改

极简风格 + 功能 HUD 藏 = **抽屉式菜单 + 长按边缘拉出**, P2 这套够了。

### 8.6 桌面平面选择 ≠ iPad 专业 AR — 简化口径

桌面场景下 **不需要** 以下复杂功能 (你没问但我怕误解):
- 多平面合并 / 平面边界精调 / Mesh 生成 — 都不做, Phone AR 桌面不需要
- LiDAR 补强 — iOS Pro 才有, 你 IQOO NEO 无 LiDAR
- 遮挡 (Occlusion) — ARCore Depth API 在 IQOO 不一定稳, P3 再评估

---

## 九、相邻文档与下一步

- **实施计划** 独立文件 `ar_feature_implementation_plan.md` (Sprint 0-4 + 验收标准)
- **本文档** 继续作为"愿景 + 架构合同", 不写 Sprint 细节
- **Sprint 1 设计原点** = §3.5 三层意识分发模型 (2026-04-21 升级)
- **用户定稿决策** = §六 (全部落定, 待 M4/G1 后续可加项已挂下方)

### 9.1 "后续可添加"清单 (用户已同意先不做, 但必须记录)

> 这里登记的事**当前不做**, 但用户已经看过了, 将来想做时回到这里找。
> 不混进 `lore/ideas.md` (那是用户个人灵感区), 不混进 Sprint 计划 (那是开工清单)。

| # | 项 | 原出处 | 触发"该上了"的信号 |
|:--|:--|:-------|:-------------------|
| M4.1 | **自定义工作模式** (创作 / 低耗 / 静音 夜间 等) | §3.6 M4 定稿 | 当 2 种标准模式(DSG_TEXT_ONLY / DSG_GEMINI_VISION)不够用, 或用户多次要求"临时换个模式" |
| G1.1 | **LiveKit 路上层门控** (订阅 TrackMuted / ParticipantDisconnected 事件, 加第三层判断) | §6.3 G1 定稿 | 当产地层 + 消费端门控出现**盲区** (比如 Unity 没死但 ICE 被吃) 会触发 |
| M3.1 | **把 PerceptionSupervisor 搬到 Bus 作为独立 Processor** | §6.2 M3 定稿 | 当 Brain Agent 因为 Gemini 对话高峰, 健康探测轮询影响响应时 |

### 9.2 AI 注意事项

- M3 里已经把 PerceptionSupervisor 抽成独立类 (参见 Sprint 2 任务清单), 后续搬 Bus 只需改一层入口, 不用重写
- M4 如果要加, 数据结构已留: `DsgMode` 是 Enum, 再加一条 + soul_constraints 新增一张表即可, 不会动其他代码
- G1.1 LiveKit 路上层门控: agent 已有 `session.on("participant_disconnected")` 钩子, 开启门控只是消费这些事件写进 dispatcher

---

*本文档维护规则*:
- 用户可以随时追加 / 删除 / 修改（没有 AI 只读约束, 和 `ideas.md` 不同）
- AI 不擅自删除用户写的决策和讨论, 只能补充事实性内容
- §五的架构清单**就是**未来实现的 issue tracker 粗稿, 实际开工时拆到 milestone 管理
