# Sprint4 Phase 4 入场锚点（2026-04-30）

> **本文用途**：Sprint4 Phase 4（整体协议升级）的启动准备。承接 Phase 1（ECP-minimal）+ Phase 2（EcpState schema）+ Phase 3（lifecycle / 防御性 / LiveKit 数据流稳定化），把"协议升级真正要回答的问题"集中在一处，让新 chat 进来读完即可建立**整体性**理解，再决定 Phase 4 范围 / 顺序 / 验收。
>
> **状态**：authoritative。修改本文 = 修改 Phase 4 计划。
>
> **不写硬约束章**。Phase 3 §0 / 背景 §10 / `parrot_behavior_rules.md` 已完整定义，本文 link 不 copy。
>
> **关键基调**（用户 2026-04-29 原话）：
>
> > Sprint4 验证的是"协议升级后怎么提升 GOSLO 使用体感"。数据流升级和 DSG/Graphiti/Ref 绑定是基础内容，**但是为了协议升级提供验证工具**。

---

## §0 Sprint4 终极目标 + Phase 4 验收口径

### 0.1 Sprint4 终极目标（背景 §1 verbatim）

- 统一数据流连接健壮性（LiveKit / AR Foundation / 前后台 / 重连 / 音频路由）
- 完成协议 V2 / ECP：从纯 RPC → 目标驱动、状态同步、可过期、前端状态机回执
- 明确 DSG L2-B / Graphiti / Obsidian / Ref 的最小接口与写入边界
- 用四个 App 工具验证协议能力：① 对话+手势+飞到手指 / ② 按需发现物体 / ③ Focus+BBox / ④ 照相机

### 0.2 Phase 4 验收口径（Phase 3 之后必须打通的最小闭环）

1. **工具 ① 跑通**：手势 → `perch_to_finger` → 锚定手上状态 → 歪头（"怎么了？"），体感闭环（GOSLO 说话和动作不分叉）
2. **工具 ② 跑通**：`identify_object` 同步 `captureSnapshot` + L2-B 候选 + Graphiti 扩搜，不再 fire-and-forget；同步体感闭环（背景 §8.2 + audit_identify_object）
3. **ECP frontend_state 至少 body / head / cognitive 三态对齐 LLM**：LLM 知道 GOSLO 当下状态，不会"跳舞时说出门散步"
4. **RefBinding + 至少一种 Event 落地**（SnapshotEvent 或 PhotoEvent），从 Unity 走到 L2-B / Graphiti 且**不污染实时帧循环**
5. **全链路 Editor 跑通**；P2.5 鹦鹉到手后真机 spike 不阻塞

工具 ③ ④ 是否进 Phase 4：由新 chat 在 §3.3 行为矩阵表填完后判断（如果协议设计自然包住 → 一起做；如果会撑爆 Phase 4 → 推 Phase 5）。

---

## §1 已落地能力清单 + 说明书路由

### 1.1 后端 Python（`src/parrot/`）

| 模块 | 已落 | Phase 4 触及面 |
|:--|:--|:--|
| `bus/` | 总线骨架 + Processor 接口（Sprint 0/1） | 不动 |
| `brain/` | Gemini Agent + 10 function tools | 工具 ② 重写 `identify_object`；可能新增 `attention_focus` / `confirm_bbox` 工具 |
| `brain/tools/_rpc_bridge.py` | ECP-minimal Phase 1 mirror | Phase 4 扩 frontend_state 三态字段 |
| `scheduler/router.py` | 4 叶浅 Selector（Reflex / Intent / Nanobot / BrainDirect） | Phase 4 视需要扩子树；不强求 BT 森林 |
| `scheduler/blackboard.py` + `bb_schema.py` | BB V2 + ECP-minimal candidate keys | Phase 4 落多个 # CANDIDATE 的 producer |
| `dsg/` | L2-B Rustworkx + 4 触发器 | Phase 4 视需要新增 Snapshot/Sighting/Attention 触发器 |
| `memory/` | Graphiti client + 对话归档 | Phase 4 提供 RefBinding 写入路径 |

### 1.2 Unity ArSpike（`unity/ArSpike/Assets/Scripts/ParrotApp/`）

| 命名空间 | 已落 | Phase 4 触及面 |
|:--|:--|:--|
| `Config` | `ParrotLifecycleConfig` SO（17 阈值） | 视需要新增 `ParrotMediaConfig` / `ParrotIdentitiesConfig`（M4，可选） |
| `Core` | `UnityMainThread` | 不动 |
| `Ecp` | `EcpStateDto` + `LifecycleHeartbeatPublisher` + `LiveKitDataChannelHeartbeatTransport` | **扩** body / head / cognitive 字段；视需要扩 `EventEnvelope` 通道 |
| `Health` | `ConnectionHealthAggregator` + 4 态聚合 | 不动；保持 single-producer-per-field |
| `Lifecycle` | `AppLifecycleManager`（11 态 FSM）+ `LifecycleShutdownService`（6 步 chokepoint）+ `RoomManagerLifecycleBridge` + `IGracefulShutdownParticipant` | R1-R6+D5 audit 已修；D2/D3 RequestConnect/Reset 视 UI 入口需要再决定 |
| `LiveKit` | `RoomManager` / `ARVideoPublisher` / `MicrophonePublisher`（蓝牙增强见独立 chat）/ `VideoStateReporter` / `BrainParticipantResolver` / `VideoTierReceiver` | **G1**：补 `Room.DataReceived` 路由（Brain → Unity 事件下行；工具 ②③ 前提） |
| `Parrot` | `AnimationDriver` + `ParrotController` | 工具 ① 加 perch_to_finger 锚定 + 歪头序列 |
| `RPC` | `ParrotRpcHandler`（ECP-minimal: `expires_at` + `active_locks`）+ `EcpDtos` | 视工具 ②③ 新增 RPC（如 `captureSnapshot` / `confirmBoundingBox`） |

### 1.3 ECP 已落进度

- **Phase 1**（ECP-minimal）：DTO + RPC bridge mirror + Unity DTO + handler ack 校验 ✅
- **Phase 2**（schema）：`EcpState` 周期上报 + `connection_health` 4 态聚合 + `connection.health.changed` / `intent.disconnect` event schema ✅（schema 定义；Brain 端 handler 待 Phase 4）
- **Phase 3**（lifecycle / 防御性）：11 态 FSM + 6 步 graceful chokepoint + LiveKit 真实 transport + R1-R6+D5 audit 修复 ✅

### 1.4 详细说明书路由（深度文档不重写，只指路）

| 主题 | 文档 |
|:--|:--|
| Sprint4 大背景 / 用户原话 / 三任务交集 | `architecture/sprint4_protocol_ecp_background_20260429.md` |
| 协议正式稿（最小合同 / 状态面 / 实施顺序） | `architecture/sprint4_protocol_v2_ecp.md` |
| Phase 1 ECP-minimal 审计（A/B/C 段 + 漂移记录 + Phase 2 入场清单） | `architecture/sprint4_ecp_minimal_audit_20260429.md` |
| Phase 3 L3 收口（4 组搬迁 + R1-R6+D5 audit fix） | `architecture/sprint4_phase3_l3_entry_20260429.md` §7.5 |
| 行为状态机 + 三层调度 + 体感红线 + 工具注册表 | `parrot_behavior_rules.md` |
| identify_object 升级设计源 | `architecture/audit_identify_object_no_screenshot_20260420.md` |
| App Flow / UI 基线 | `architecture/ar_app_flow_ui_design.md` |
| LiveKit Unity 实现速查 | `.cursor/skills/livekit-unity-lifecycle/IMPL_REF.md` + `.cursor/skills/livekit-unity-video-publish/IMPL_REF.md` |
| Unity AR Spike 搬迁状态 | `unity/ArSpike/Assets/Scripts/ParrotApp/MIGRATION.md` |

---

## §2 已知遗留问题（不预先分配，待 §3 整体理解后再决策）

| 编号 | 问题 | 影响 | Phase 4 候选方向（不是定论） |
|:--|:--|:--|:--|
| D1 | SDK Reconnecting event 未订阅 | 静默重连看不到 | gate 在 P2.5 真机 spike |
| D2 | `RoomManager.Connect` 未收口到 lifecycle 包装 | UI 直连 RPC | 视 UI 入口需求 |
| D3 | 无 `RequestColdStartReset` | 手动重连不便 | 视 HUD 工具需求 |
| D4 | `ReportDisconnected` 双写 health（行为正确） | 美学 | 推迟 |
| D6 | Bridge `isReconnect` 白名单语义 | 可读性 | 推迟 |
| **G1** | `Room.DataReceived` 路由未写 | **Brain → Unity 事件下行通路缺失** | **Phase 4 必看**（工具 ②③ 前提） |
| G2 | `ar_tracking_state` 无 producer | health 该字段空 | 等 SceneProfileManager |
| G3 | Brain 端 `unknown` 持续阈值 | 事件假阳性 | Phase 4 写 handler 时定 |
| M2 | Editor HUD / Force Shutdown / Simulate Pause | spike 调试不便 | Phase 4 早期可补（spike 之前用得上） |
| M3-M5 | Inspector readonly / 多 SO / EditorWindow | 调试便利 | 推迟 |
| **ⓐ** | bb_schema 多个 # CANDIDATE keys 还没 producer | 协议候选未落地 | **Phase 4 协议设计时一并落** |
| **ⓑ** | `EventEnvelope` L0 层未实现 | 因果链路缺失 | **Phase 4 启动时决定做不做**（影响工具 ②③ Ref 落地） |
| **ⓒ** | `RefBinding` 数据结构未实现 | 工具 ③④ 没法落 Ref | **Phase 4 必做**（验收 4 前提） |
| **ⓓ** | `SnapshotEvent` / `SightingEvent` / `PhotoEvent` / `AttentionHint` schema 全空白 | 4 工具 Ref 接口缺 | **Phase 4 必做**（按需新增） |
| **ⓔ** | `identify_object` 完全重写（同步 captureSnapshot + L2-B 候选 + Graphiti 扩搜） | 当前默认未注册 | **Phase 4 工具 ②** |
| ⓕ | Scheduler 仍是 4 叶浅 Selector | 没 BT 森林雏形 | Phase 4 视需要扩；不强求 |
| **ⓖ** | DSG L3 注意力模块 vs 观察者模块**职责未分** | 模块边界混淆风险 | **Phase 4 启动前必须澄清边界**（见 §3.7） |

---

## §3 协议整体性必须重新理解的 7 个点（启动前自检表）

> **新 chat 进来第一件事**：把 §3.3 行为矩阵填完整 + 过 §3.7 模块职责分离，**用户 sign off 后**再写代码。

### 3.1 蓝牙音频兼容（独立 chat 异步推进）

- 已派独立 chat 实现 MicrophonePublisher 蓝牙路由 + AudioRoutePolicy struct
- Phase 4 主线**假设**蓝牙到位；如果独立 chat 还没并入 ArSpike，Phase 4 启动时先确认 hand-off 文档
- 是否把 AudioRoutePolicy ECP 化、是否写 `session/audio_route_policy` BB key（# CANDIDATE 状态）→ **Phase 4 决策**

### 3.2 协议 = ECP + Scheduler + DSG/Graphiti 交互（不只是 ECP）

四个工具触发不同链路组合：

| 工具 | ECP 路径 | Scheduler 层 | DSG 触及 | Graphiti 触及 | Ref 输出 |
|:--|:--|:--|:--|:--|:--|
| ① 对话 + 简单手势 + 飞到手指 | 手势 → Reflex → `flyTo` ECP；简单指令 → Intent | Reflex / Intent | 不触及 | 不触及 | 无 |
| ② 按需发现物体 | `identify_object` Intent + `captureSnapshot` reliable | Intent + Task（搜索） | L2-B 候选匹配 | 扩搜 + UUID 绑定 | SnapshotEvent / SightingEvent |
| ③ Focus 放大镜 + BBox | 拖动 lossy DataChannel + 松手 reliable / RPC | Reflex（拖动）+ Intent（确认） | L2-B AttentionHint（**权重累加**） | 不直写 | RefBinding 锚到 L2-B Node |
| ④ 照相机 | reliable RPC `capturePhoto` + photo upload | Intent | 不触及 | 不直写 | PhotoEvent + Episode Ref |

**核心约束**：4 个工具不能各自发明接口，必须统一在 `EventEnvelope` / `Blackboard` / `EcpCommand` / `RefBinding` 这一层（背景 §7）。

### 3.3 Reflex / Intent / Task × 行为矩阵（**Phase 4 启动第一步必填**）

> 用 `parrot_behavior_rules.md §0.1 / §0.2 / §0.3 / §4.3` 现成口径填。

| 行为 | 调度层 | 意识层 | 阻塞对话 | 写 BB | 写 Graphiti | 写 L2-B | 上报 LLM | 状态同步通道 |
|:--|:--|:--|:--|:--|:--|:--|:--|:--|
| `flyTo`（GOSLO 自身） | Intent | 层②，失败升③ | 是 | 是 | 否 | 否 | 失败时 `last_rpc_ack` | RPC + EcpAck |
| 手势 → `perch_to_finger` | Reflex | 层①+② | 否 | 是（锚定） | 否 | 否 | 否（除非冲突） | DataChannel + EcpState |
| **手势成功后锚定动作（飞到手 + 歪头"怎么了？"）** | **Intent**（自动接续） | **层②** | **否**（自主） | **是**（body=PERCHED_ON_HAND, head=HEAD_TILT） | 否 | 否 | **否**（动作本身是表达） | EcpState（三态字段） |
| `identify_object` | Intent | 层②/③ | **是** | 是 | 通过 archiver | 候选写入 | 同步 tool 结果 | RPC + EcpAck + SnapshotEvent |
| Focus 放大镜拖动中 | Reflex（透传不仲裁） | 层① | 否 | transient | 否 | 否 | 否 | lossy DataChannel |
| **Focus 放大镜锚定（注意力权重累加，慢）** | Intent | 层② | 否 | 是（AttentionHint w_focus） | 否 | 是（候选权重 +Δ_focus，**Δ 较小**） | **达阈值才报** | reliable DataChannel |
| BBox 拖动中 | Reflex（透传） | 层① | 否 | transient | 否 | 否 | 否 | lossy |
| **BBox 锚定（确认器 + 高权重 Focus ON）** | Intent | 层② | 否 | 是（AttentionHint w_bbox） | 否 | 是（候选权重 +Δ_bbox，**Δ 较大**） | **更早达阈值；用户主动放置等同"确认"语义** | reliable / RPC |
| 拍照（用户主动） | Intent | 层③（用户主动） | 否（短） | 是 | 否（PhotoEvent **不**默认入 Graphiti） | 是 PhotoEvent | 是（"我拍了"） | RPC + PhotoEvent |

**两条用户级补充**：

- **Focus 放大镜 vs BBox 区分度**（用户 2026-04-29）：
  - 放大镜本身就有"放大查看文件"的功能，**不那么烦人** → 注意力权重 Δ 较小，阈值较高，避免每次放大都打扰 LLM
  - BBox 是**确认器** + 更高权重的 Focus ON → 用户放置 BBox 表达明确意图，权重 Δ 较大，更早达阈值上报 LLM
  - **共同模式**：两者都不是"放下立刻报 LLM"，而是**累加注意力权重，到阈值才触发上报**；阈值由 §3.7 注意力模块判定

- **手势 perch_to_finger 成功的锚定动作**（用户 2026-04-29）：
  - 手势检测 → Reflex 触发飞行 → 飞到食指**中段指节**为成功判定点
  - 成功后**自动接续 Intent**：锚定 body=PERCHED_ON_HAND + head=HEAD_TILT（歪头"怎么了？"表达）
  - 这是工具 ① 验收的具体体感判据，必须落到 ECP frontend_state 三态字段同步

### 3.4 ECP frontend_state 对齐 + LLM 注意力同步

**问题**：GOSLO 跳舞时不该说"咱们出门散步吧"。LLM 必须知道当下身体 / 头部 / 认知状态 + 当前进行的命令。

**Phase 4 必决**：
1. `body_state` / `head_state` / `cognitive_state` 是 EcpState **顶层字段**，还是嵌进 `frontend_state` dict？
2. 周期上报频率（5Hz 心跳？事件驱动？）— 涉及 §3.5 多通道速率
3. **LLM 注入路径**（核心决策，§3.6 候选 3 选 1 或混合）：
   - 选项 A：每轮 turn 前刷新 system prompt 末段（侵入大、烧 token）
   - 选项 B：注册 `query_my_state` tool，LLM 想知道时自己调（被动、可能忘）
   - 选项 C：写 BB；执行类 tool（`animate` / `fly_to`）在执行前检查并附加 reason 给 LLM（隐式、对齐 §0.3 体感红线，**推荐**）
4. `parrot_behavior_rules.md §3.2 优先级链` 怎么编码到 EcpState，让 LLM 理解"我跳舞中，FREEZE 之外只有飞行能打断"

### 3.5 ECP 多通道多速率 — 哪些可快速切换 / 哪些会崩

| 通道 | 用途 | 速率 | 可靠性 | 切换是否安全 |
|:--|:--|:--|:--|:--|
| LiveKit RPC | `flyTo` / `animate` / `setVideoTier` / `captureSnapshot` | 按需 | reliable | ❌ 不能换通道 |
| DataChannel reliable | EcpState 心跳 / health.changed / intent.disconnect / EventEnvelope（候选） | 1Hz / 事件 | reliable | ⚠️ 可换 ParticipantAttribute（spike S7 待跑） |
| DataChannel lossy | 手势 / pose / Focus / BBox 拖动 | 30-60Hz | lossy | ❌ 不能换 reliable（**会爆队列**） |
| Audio Track | Mic 上行 / TTS 下行 | 实时 | RTC | ❌ 固定 |
| Video Track | 主视频源（按 tier） | 30/15/5fps | RTC | ⚠️ 切 tier 走 cool-down（IMPL_REF.md §6） |

**Phase 4 可能新增**：
- `EventEnvelope` 走哪条？reliable DataChannel？还是 RPC？
- `RefBinding` 写入：reliable DataChannel + 后端持久化，还是 RPC 同步？
- `SnapshotEvent` payload：JPEG bytes 走 DataChannel 还是 LiveKit File API？

**红线**（已知）：
- 30Hz 拖动塞 reliable → 队列爆，整条 reliable 链路堵死（Sprint3 案例）
- EcpState 心跳塞 lossy → 新接入丢首帧 → 永远不知 Unity 状态
- RPC 当事件流（高频调）→ 每个 RPC ack 等待，序列化变慢

### 3.6 Gemini + LiveKit + LLM 注入通道（已有代码骨架）

| 通道 | 入口 | 作用 | 何时用 |
|:--|:--|:--|:--|
| **System prompt** | `livekit-agents` `AgentSession` 初始化 | 静态人设 + 行为规则 | 会话起始 |
| **Function tool** | `src/parrot/brain/tools/*.py`（10 个） | LLM 主动调，同步等结果 | LLM 决策需外部信息 / 触发 GOSLO 行为 |
| **Tool result** | tool 函数返回值 | 同步结果回灌 LLM | 紧跟 tool 调用 |
| **Conversation context** | LiveKit Audio Track + ASR | 用户语音 | 实时 |
| **DataChannel inbound**（**G1 待补**） | `Room.DataReceived` | Brain → Unity 事件下行 | 事件驱动 |
| **Blackboard write** | `bb_schema.py` 多个 producer | 内部状态共享，LLM **不直接读** | 后端协调 |
| **Subagent / Nanobot** | `dispatch_task` tool | 长任务委派 | Task 层 |

**Phase 4 决策点**：§3.4 的 body/head/cognitive 三态走哪条注入路径（推荐 C：BB + 执行类 tool 隐式带 reason）。

### 3.7 DSG L3 — 注意力模块 vs 观察者模块**职责分离**（用户 2026-04-29）

> 这一节是 Phase 4 启动**强制澄清**的边界。两个模块以前混在一个名字里，必须分开。

| 模块 | 职责 | 触发输入 | 输出 | 不做 |
|:--|:--|:--|:--|:--|
| **观察者**（Observer） | **检测事件 + 决定何时打点 / 快照** —— "记录"职责 | 实时事件流（手势 / 视觉降级 / 用户主动操作 / 命令完成） | SnapshotEvent / SightingEvent / PhotoEvent / EcpAck 摘要 → EventEnvelope | 不做"判断要不要触发触发器"；不做注意力权重计算 |
| **注意力模块**（Attention，**DSG L3 候选**） | **收集数据触发触发器** —— "判断"职责 | 观察者输出 + L2-B 候选权重 + Focus/BBox 累加权重 | 触发器调用（如"达阈值上报 LLM"） | 不直接抓帧；不直接写 Graphiti；不做事件检测 |

**结论**：
- **Phase 4 范围**：观察者模块的最小可用版本（配合工具 ② ③ ④ 的 Event 落地）
- **DSG L3 注意力模块**：**后续设计**，不进 Phase 4。当前 Focus/BBox 的"达阈值上报"可以用一个**轻量临时阈值器**承接（不是完整 L3 注意力模块）
- **命名**：以前所有"observer / attention 混用"的旧称都按本表两栏正名；新代码**不允许**把两个职责放进同一个类

---

## §4 Phase 4 启动序（推荐流程）

> 不写"分组工作流"，因为协议范围由 §3 整体理解决定。但下面的**启动顺序**是不可调的：

1. **第 1 步：填 §3.3 行为矩阵**（新 chat 第一动作）
   - 把当前所有已知行为 + 工具 ① ② ③ ④ 的子行为按 8 列填齐
   - 不能填的格子 = Phase 4 必须先回答的协议设计问题
   - **用户 sign off** 后才能动代码

2. **第 2 步：澄清 §3.7 观察者 vs 注意力边界**
   - 落到具体类名 / 命名空间 / Python module 路径
   - 写进 entry doc §3.7 表格的"代码入口"列（本文档发布时该列暂空）

3. **第 3 步：决定 ⓐ-ⓖ 7 条新增遗留项的 Phase 4 范围**
   - 必做：G1 + ⓒ + ⓓ + ⓔ + ⓖ
   - 视范围：ⓐ + ⓑ + ⓕ + 工具 ③ ④
   - 推迟：D1-D6 / G2-G3 / M3-M5

4. **第 4 步：协议增量设计 + 实现**
   - 按工具 ① → ② → ③ → ④ 顺序（如果 ③ ④ 进 Phase 4）
   - 工具 ① 是 ECP frontend_state 三态对齐的**最简验证**，必须最先打通
   - 工具 ② 是 SnapshotEvent + L2-B 候选 + Graphiti 扩搜的**全链路验证**
   - 工具 ③ ④ 是 RefBinding + AttentionHint 的**Ref 落地验证**

5. **第 5 步：验收**
   - 按 §0.2 五条逐一勾
   - P2.5 鹦鹉到手后真机 spike 在另一节奏推进，**不阻塞 Phase 4 验收**

---

## §5 文件路由 / Ref 表

按主题分类。新 chat 不必读全部，按 §3 / §4 当前关注点拉取。

### 5.1 协议主线

- `architecture/sprint4_protocol_ecp_background_20260429.md` — 大背景 + 用户原话
- `architecture/sprint4_protocol_v2_ecp.md` — 协议正式稿
- `architecture/sprint4_ecp_minimal_audit_20260429.md` — Phase 1 审计 + 漂移
- `architecture/sprint4_phase3_l3_entry_20260429.md` — Phase 3 收口 + R1-R6+D5 audit fix
- `parrot_behavior_rules.md` — 三层调度 + 体感红线 + 工具注册表

### 5.2 工具 ② identify_object

- `architecture/audit_identify_object_no_screenshot_20260420.md` — 升级设计源
- `src/parrot/brain/tools/identify_object.py` — 当前实现（默认未注册）
- `src/parrot/brain/tools/_rpc_bridge.py` — ECP-minimal mirror

### 5.3 工具 ① 手势 / 飞到手指

- `parrot_behavior_rules.md` §1.1 身体状态 + §5 PerchOnHand
- `unity/ArSpike/Assets/Scripts/ParrotApp/Parrot/AnimationDriver.cs`
- `unity/ArSpike/Assets/Scripts/ParrotApp/RPC/ParrotRpcHandler.cs`（`flyTo` handler）

### 5.4 工具 ③ ④ Focus / BBox / 照相

- 当前**无现成实现**；Phase 4 新建
- 设计参考：`architecture/ar_app_flow_ui_design.md`（工具柜布局 + 道具入口）

### 5.5 数据流 / Lifecycle / 健康

- `.cursor/skills/livekit-unity-lifecycle/IMPL_REF.md`
- `.cursor/skills/livekit-unity-video-publish/IMPL_REF.md`
- `.cursor/skills/client-sdk-unity/SKILL.md`
- `unity/ArSpike/Assets/Scripts/ParrotApp/MIGRATION.md`

### 5.6 DSG / Graphiti / Memory / Ref

- `.cursor/skills/graphiti/SKILL.md`
- `src/parrot/dsg/triggers/` — 当前 4 触发器（calendar / message / ssot / scene_context）
- `src/parrot/memory/` — Graphiti client + 对话归档
- 背景 §6 — RefBinding 最小理解

### 5.7 蓝牙音频（独立 chat 异步）

- 独立 chat 自管理；Phase 4 启动前确认 hand-off 文档（用户独立维护，文件名待用户告知）

---

## §6 给新 chat 的开局 prompt（一段话）

```text
你是 ParrotCarriers Sprint4 Phase 4（整体协议升级）实现助手。think in English ,用中文回答。

## 第一步（不可跳过）

读 `.cursor/memory/architecture/sprint4_phase4_entry_20260430.md` 全文。
不要先翻其他历史文档；本文已把 Sprint4 大背景、Phase 1-3 落地、协议整体性
7 个再理解点、遗留问题、启动序、Ref 路由全部聚合好了。

## 第二步（必做）

按 entry doc §4 启动序：
1. 填齐 §3.3 行为矩阵（8 列 × 所有当前 + 工具①②③④ 子行为）
2. 澄清 §3.7 观察者 vs 注意力模块边界（落到具体 Python module 路径）
3. 给 ⓐ-ⓖ 7 条新增遗留项分配 Phase 4 范围
4. 用户 sign off 后才动代码

## 不允许（硬约束）

不重复 Phase 3 §0 / 背景 §10 / parrot_behavior_rules 已写过的约束 — 它们
仍然生效，但 entry doc 不 copy 一遍，避免漂移。

## Sprint4 终极目标（不要忘）

验证"协议升级后怎么提升 GOSLO 使用体感"。数据流升级和 DSG/Graphiti/Ref 绑
定是基础内容，但**是为了协议升级提供验证工具**。
```

---

## §6.x 平台版本锁补丁（2026-04-29，与 Phase 4 启动序解耦但必须 Phase 3 真机回归前完成）

**触发**：Google Play 自 2025-11-01 起强制 64-bit App 走 16KB ELF 对齐，Android 15+ ARM64 真机 `dlopen` 失败 → 冷启动闪退。SDK 内嵌 `liblivekit_ffi.so` 与 `libarcore_sdk_c.so` 在原 pin 下都是 4KB 对齐。

**补丁内容**：

| 项 | 旧值 | 新值 | 备注 |
|---|---|---|---|
| `io.livekit.livekit-sdk` | `2a7c57d`（2026-04-10） | `7d868ef`（main HEAD, 含 PR #263 → FFI v0.12.53, 2026-04-23） | 两个工程同步升 |
| `com.unity.xr.arcore` | 5.1.5 | 5.2.2 | `libarcore_sdk_c.so` 16KB 对齐 |
| `com.unity.xr.arfoundation` | 5.1.5 | 5.2.2 | 同档 |
| `com.unity.xr.arkit` | 5.1.5 | 5.2.2 | 同档（iOS 不受 16KB 影响，但配套版本统一） |
| Unity Editor | 2022.3.62f3 | **保持** | 2022.3.56f1+ 引擎层已支持 16KB |

**对 Phase 3/4 既有代码的影响**（已 grep 全 `unity/**/*.cs` 审计完毕，详见 `.cursor/skills/client-sdk-unity/SKILL.md` 顶部 NOTICE 区"行为变更"表）：

- `IRemoteTrack.SetEnabled` 从 no-op 变成真生效（PR #250）→ **本仓库不中招**（视频档位走 `ILocalTrack.SetMute`）
- AudioStream catchup（PR #260）→ 远端音频从背景恢复"咔哒"已修复 → 行为只会更稳，但 Phase 3 真机回归仍要复测一次
- `VideoFrame::new()` Rust 端 breaking → **本仓库不中招**（走 `TextureVideoSource` 包装）
- Reader IDisposable（PR #233/#258）→ **本仓库不中招**（未用 RegisterByteStreamHandler）

**结论：本次升级 0 处 C# 代码改动**。

**Phase 3 真机回归 checklist 增补**：

1. 出包前跑 `pwsh tools/verify_so_alignment.ps1 <apk_or_so_dir>` 真验所有 arm64 `.so` 都是 `align 2**14`。
2. S5 setVideoTier 黑帧 P95（GeminiOnly→FULL→GeminiOnly）回归一次。
3. 远端语音从 OnApplicationPause 恢复后的连续性（无"咔哒"+ 无丢段）回归一次。
4. ARCore 5.2.2 升级后 ARFoundation 5.1 → 5.2 的 `XRCameraSubsystem` / `frameReceived` / `XRCpuImage` API 行为复测一次（理论无变更）。

**联动文档**：

- `.cursor/skills/client-sdk-unity/SKILL.md` 顶部 NOTICE 区
- `.cursor/skills/livekit-unity-lifecycle/IMPL_REF.md` §6.3
- `.cursor/skills/ar-foundation-api/SKILL.md` + `ar-foundation-samples/SKILL.md` 顶部 NOTICE
- `.cursor/rules/ar-foundation.mdc` §0–§1
- `tools/verify_so_alignment.ps1`（出包/CI 自检脚本）

---

## §7 引用

- `architecture/sprint4_protocol_ecp_background_20260429.md` — 背景锚点
- `architecture/sprint4_protocol_v2_ecp.md` — 协议正式稿
- `architecture/sprint4_ecp_minimal_audit_20260429.md` — Phase 1 审计
- `architecture/sprint4_phase3_l3_entry_20260429.md` — Phase 3 入场 + R1-R6+D5 fix
- `parrot_behavior_rules.md` — 行为状态机 + 三层调度 + 体感红线
- `architecture/audit_identify_object_no_screenshot_20260420.md` — 工具 ② 设计源
- `architecture/ar_app_flow_ui_design.md` — UI / 工具柜 / 道具入口
- `unity/ArSpike/Assets/Scripts/ParrotApp/MIGRATION.md` — Unity 搬迁状态
