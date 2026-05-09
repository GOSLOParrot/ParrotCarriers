---
status: ratified
category: completion-report
status_note: "Sprint4 Phase 4 W6-7 Unity 半边（BBox / Focus UI gestures + ParrotAttentionConfig SO + EcpEvent publish + Echo 路径 ①+②）落地；F-05 Echo path ① + ② 接通，③ deferred。"
last_reviewed: 2026-04-30
---

# Sprint4 Phase 4 W6-7 Unity 半边完成报告（2026-04-30）

> **本文用途**：W6-7 Unity 半边落地后的 authoritative 完成口径 + F-05 Echo 路径 ①+② 接通证据 + 已知漂移 + 后续工作明确分发。
>
> **关联**：`sprint4_phase4_entry_20260430.md §8.7` W6-7 行 = 本文落地范围；`sprint4_phase4_brain_self_audit_20260430.md §3.2 F-05` = Echo 路径 prerequisite gap 的 prerequisite 修复。
>
> **关键基调**：本 chat 严守 Unity 半边 + Echo 路径 ①+② 范围；Brain 半边 W6-7 已落地的 observer/threshold/refs/bb_schema 全保持 read-only。

---

## §0 一句话总结

Unity W6-7 全套生产就绪：BBoxController / FocusController / ParrotAttentionConfig SO / EcpEventPublisher / AttentionConfigEchoPublisher 全部落地；Brain 端 attention_config_handler.py 接通 Echo 写 BB；188/188 全绿（179 baseline + 9 echo handler tests）。**FocusBboxThreshold 读 BB 注入参数（Echo step ③）留给后续 Brain chat 的 1 行改动**。

---

## §1 落地内容

### 1.1 新增文件（9）

| 文件 | 命名空间 / 模块 | 作用 |
|:--|:--|:--|
| `unity/ArSpike/Assets/Scripts/ParrotApp/Ecp/EcpEventPublisher.cs` | `ParrotApp.Ecp` | Unity → Brain EcpEvent 发包 Singleton（`parrot.ecp.event` reliable）；与 `LiveKitDataChannelHeartbeatTransport` 平级，专管 Phase 4 EcpEvent topic；`logEvenWhenDropped` 兜底让离线 smoke 可见 wire JSON |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Config/ParrotAttentionConfig.cs` | `ParrotApp.Config` | Δ_focus / Δ_bbox / threshold / target_ttl_s 4 字段 SO（与 `ParrotLifecycleConfig` 同模式）；`ToWireJson()` 输出 BB schema 一致字面量 + `OnValidate` 自检 |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Attention/BBoxController.cs` | `ParrotApp.Attention` (新目录) | BBox UI 状态机：`PlaceBBox` / `RemoveBBox` / `RemoveAll` 公共 API + ContextMenu 调试入口；§B.6 reconnect 重 publish；payload 包含 `bbox_id`（Brain 端 observer/threshold 索引）+ corners/pose/label 为 Phase 5+ 准备 |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Attention/FocusController.cs` | `ParrotApp.Attention` | Focus 放大镜 UI；`AnchorFocus` / `ReleaseFocus` / `ReleaseAll`；同 BBox 的 reconnect 行为 |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Attention/AttentionConfigEchoPublisher.cs` | `ParrotApp.Attention` | F-05 Echo path Unity 半边：订阅 `RoomManager.OnConnected` → `EchoNow()` 发 `attention.config.echo` EcpEvent；ContextMenu `Debug: Echo Now` 兜底 |
| `src/parrot/brain/attention_config_handler.py` | `parrot.brain` | F-05 Echo path Brain 半边：subscribe via `event_ingest` → 校验 5 字段 + schema_version + threshold > 0 + 数值类型 → 写 BB `global/attention_thresholds` (writer = `brain._rpc_bridge` 保持 bb_schema 声明) |
| `tests/test_ecp_event/test_attention_config_echo.py` | pytest | 9 个 test：register / 5 字段 / 非 default 值 / missing 字段 / 非数值 / threshold 0 / 错 schema_version / reconnect 覆写 / writer 字符串校验 |

### 1.2 改动文件（5）

| 文件 | 改动 |
|:--|:--|
| `src/parrot/shared/ecp_event.py` | `EcpEventType` 加 `ATTENTION_CONFIG_ECHO = "attention.config.echo"` + 注释（payload schema + 触发时机） |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Ecp/EcpEventDto.cs` | `EcpEventTypeNames` 镜像加 `AttentionConfigEcho`；`test_cs_parity.py` 自动校验通过 |
| `src/parrot/brain/agent.py` | `attach_ecp_event_ingest` 之后加 `attention_config_handler.register(ingest)` + log 字符串扩 |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Editor/ParrotSmokeSceneBuilder.cs` | 加 Attention GameObject（4 component）+ 自动创建 / 复用 `Assets/ParrotApp/Config/ParrotAttentionConfig.asset` + 引用拖线 |
| `tests/test_ecp_event/test_ecp_event.py` | `test_event_type_registry_matches_entry_doc_8_3` 加 `attention.config.echo` 到 expected 集合 |

### 1.3 Doc 同步（2）

| 文件 | 改动 |
|:--|:--|
| `architecture/sprint4_phase4_entry_20260430.md` | §8.3 表加 `attention.config.echo` 行；§8.1 L9 ⚠ 注从"未接通"升级为"①+② 已接通，③ deferred" |
| `architecture/sprint4_phase4_brain_self_audit_20260430.md` | §3.2 F-05 status 从 `proposed` 升级为 `partially-resolved`（含具体落地内容 + 剩余 ③ 边界） |

---

## §2 测试基线

| 套 | 改前 | 改后 | Δ |
|:--|:--|:--|:--|
| `tests/test_ecp_event/` | 143 | 152 | +9（新 echo handler tests） |
| `tests/` 全量（除 integration） | 179 | **188** | +9 |
| `tests/integration/*` | 失败 | 失败 | 0（pre-existing 环境问题：Redis/Graphiti 未起；与本 chat 改动无关，已对照 stash 验证） |

测试执行：`.venv\Scripts\python.exe -m pytest tests/ --ignore=tests/integration -q` → **188 passed in 3.85s**。

跨语言对齐：`pytest tests/test_ecp_event/test_cs_parity.py -v` → **4 passed**（含新 `attention.config.echo`）。

---

## §3 F-05 Echo path 接通状态

### 3.1 prerequisite chain 当前状态

```
① Unity SO + EchoPublisher → publish EcpEvent
   [LANDED — AttentionConfigEchoPublisher / ParrotAttentionConfig.ToWireJson]

② Brain attention_config_handler 写 BB global/attention_thresholds
   [LANDED — attention_config_handler.py + agent.py wire-up]

③ FocusBboxThreshold.__init__ 读 BB 注入构造参数
   [DEFERRED — 触动 dsg/attention/threshold.py，本 chat 锁定文件，
    留给独立 Brain chat 的 1 行改动]
```

### 3.2 BB key # CANDIDATE 标记

`bb_schema.py:global/attention_thresholds` 的 # CANDIDATE 标记**保留**直至 step ③ 完成（届时 + 一个 doc-only chat 移除标记）。本 chat 不动 bb_schema.py（audit constraint）。

### 3.3 触发覆盖

| 触发 | Unity 行为 | Brain 行为 |
|:--|:--|:--|
| 初次连接 (`RoomManager.OnConnected`) | `AttentionConfigEchoPublisher.EchoNow()` publish 一次 | `attention_config_handler` 写 BB |
| Reconnect / Brain 管线切换（§B.6） | 同上，每次重连必发 | BB 覆写（idempotent overwrite） |
| Inspector ContextMenu `Debug: Echo Now` | 兜底手动同步 | 同上 |
| SO Inspector live-edit | **不自动 publish**（避免风暴）；用户手动 `Echo Now` | — |

---

## §4 §B.6 — Brain 管线切换 / reconnect 行为（统一锁）

用户 sign-off 时追加的设计点。所有 Phase 4 W6-7 新增 Unity 状态在 reconnect 时**全量重 publish**，Unity 持有 source-of-truth：

| 组件 | OnDisconnected | OnConnected（含 reconnect） |
|:--|:--|:--|
| `AttentionConfigEchoPublisher` | 不动 | EchoNow() 全量重发 |
| `BBoxController` | 保留 `_active` Dictionary | 遍历当前 ON 集合 → 全部重 publish `bbox.placed`（Brain `refs.bind_bbox` 幂等） |
| `FocusController` | 同 BBox | 同 BBox（`refs.bind_focus` 幂等） |
| Brain `attention_config_handler` | — | 收 echo → 直写 BB（覆写） |

**显式不做**：
- 不区分 transient blip vs pipeline switch（同型 LiveKit 事件，做区分 = 多状态机 = 多 bug 面）
- 不做 reconnect 期间 publish 排队；reliable transport disconnect 期间发包走 `EcpEventPublisher.DroppedNoRoomCount` 早退路径，OnConnected 一来即发
- 不依赖 audit F-06 `reset_refs_for_session` 在 disconnect 清 RefBinding（Unity 重 publish 命中 refs.py 幂等保护，无 stale ref 问题）

---

## §5 离线 Editor smoke 验证

**已实测**：build smoke scene → Play → 触发 ContextMenu。无 LiveKit 环境下：

| 触发 | Console 输出（关键证据） |
|:--|:--|
| Play 启动 | `[Heartbeat:LOG] {"sequence_id":1,..."body_state":"idle","head_state":"HEAD_FORWARD"...}`（W3.A.3 1Hz tick） |
| Attention.AttentionConfigEchoPublisher 启动 | `[AttentionConfigEchoPublisher] EchoNow sent=False payload={"delta_focus":0.2,"delta_bbox":1.0,"threshold":1.0,"target_ttl_s":30,"schema_version":1}`<br/>`[EcpEvent:DROPPED] room not ready (event_type=attention.config.echo ...) wire={"schema_version":1,"event_id":"evt_...","event_type":"attention.config.echo",...,"payload":{"delta_focus":0.2,...}}` |
| BBox `Debug: Place Test BBox` | `[EcpEvent:DROPPED] event_type=bbox.placed ... wire=...{"payload":{"bbox_id":"bb_<guid8>","corners":[[0.2,0.3],[0.8,0.7]],"pose":{...},"label":"test_bbox"}}` |
| BBox `Debug: Remove Last BBox` | `[EcpEvent:DROPPED] event_type=bbox.removed ... wire=...{"payload":{"bbox_id":"bb_<guid8>"}}` |
| Focus `Debug: Anchor Test Focus` | `[EcpEvent:DROPPED] event_type=focus.anchored ... wire=...{"payload":{"focus_id":"fc_<guid8>","center":[0.5,0.5],"radius":0.15,...}}` |

**离线 smoke 不能验证的部分**（需要 LiveKit + Brain 联机）：
- BB `global/attention_thresholds` 是否被 Brain handler 写入
- BBox 放置 → Brain `observer/bbox.py` 创建 RefBinding → `FocusBboxThreshold` 累加 → cross threshold → publish `attention.threshold.crossed`
- 5 次 Focus 锚定累加 cross 路径
- `EcpEventDispatcher` 收到 brain-source `attention.threshold.crossed` 的 wildcard log

这些**需要 LiveKit 真连接**的项留给"联机 smoke" — 与 GAP-1（W3 EcpState ingest）一起在独立 chat 跑，作为 §0.2 验收 #5 的最后闭环。

---

## §6 设计漂移 / 审计点

### 6.1 ⚠ 中 — 后续 chat 处理

| 编号 | 议题 | 影响 | 建议处置 |
|:--|:--|:--|:--|
| **F-05 step ③** | `FocusBboxThreshold.__init__` 读 BB 注入构造参数 | 当前阈值器永远跑硬编码 DEFAULTS；Echo 写 BB 但无消费方 | **新开"FocusBboxThreshold BB injection" Brain chat**：~5 行 `__init__` 改动（`open_bb_client` 读 → 覆盖 `delta_focus` / `delta_bbox` / `threshold` / `target_ttl_s` 默认参数）+ 1 测试。完成后 doc-only chat 移除 bb_schema.py 的 # CANDIDATE 标记 |
| C-1 | `test_attention_config_echo.py::_reset` 没真清 BB 那个 key | 测试间偶然依赖前一 test 的 BB 状态？实测不影响（每 test 都先 publish 后读，非 read-before-write） | 可推迟。Phase 5+ 加 `unset` 公共 API 时一并补 |

### 6.2 ⚠ 低 — 设计选择记录

| 编号 | 议题 | 当前选择 | 替代 |
|:--|:--|:--|:--|
| C-2 | `EcpEventPublisher.logOnSuccess` Editor 默认 true | spike 期方便看包；真机上线前应改 false（会刷 log） | Inspector 可调 |
| C-3 | BBox / Focus controller 持有 Dictionary 不持久化 | 关 App = 用户的"我不感兴趣了"信号（§3.7 + threshold.py docstring） | Phase 5+ 如果要做 session resume 再重新 spec |
| C-4 | `AttentionConfigEchoPublisher` 不监听 SO 的 OnValidate 自动 publish | Editor live-edit 不是 spike 主路径；自动发会让 reconnect 路径产生重复风暴 | 用户在 Inspector 改完手动点 `Debug: Echo Now` |
| C-5 | `attention_config_handler` 物理在 `brain/`（非 `brain/observer/`） | §3.7 Observer 是"记录"语义；config Echo 是控制面 sync，不是事件记录 | 边界对齐 |
| C-6 | BBox / Focus payload 含 `corners` / `pose` / `radius` 但 Brain W6-7 只读 `bbox_id` / `focus_id` / `label` | Phase 5+ identify_object 联动时直接用，避免后续加字段升 schema_version | — |

### 6.3 ❓ 待用户决策项

| 编号 | 问题 | 备选 |
|:--|:--|:--|
| Q-1 | BBox / Focus controller 的真实 UI 触发是什么？ | 当前 ContextMenu 兜底；待 GOSLO 反馈 + AR 场景 UI 设计完成后接 XR Hands 手势 / 屏幕拖框 / 工具柜 prefab |
| Q-2 | `parrot.ecp.tick` lossy drag 事件何时 spec？ | W6-7 显式不做；待 GOSLO 反馈 UI 设计 + 用户体感校准后再 spec drag payload schema |

---

## §7 范围外明确不做（防过度延伸）

本 chat **绝不**做的事（与硬约束 1-10 + audit defended 一致）：

1. ~~改 Brain 端 observer / threshold / refs / bb_schema~~ → 全部 read-only
2. ~~改 W3.A.2/A.3 已落地的 perch_to_finger / EcpState 三态相关代码~~ → 不动 1 行
3. ~~改 entry doc §8 锁定值 / audit doc §9 锁定项~~ → 仅添加新行 + 升级 status note
4. ~~改 ecp_event.py 的 8KB / topic / schema_version 常量~~ → 仅加 enum 值
5. ~~改 EcpEventDispatcher 的 topic 路由~~ → 不动
6. ~~实现 Step ③ FocusBboxThreshold 读 BB~~ → defer（threshold.py 锁定）
7. ~~实现 lossy `parrot.ecp.tick` 拖动事件~~ → defer（待 UI 设计）
8. ~~做 Brain `reset_refs_for_session` 在 disconnect 自动清~~ → audit F-06，独立路径（refs 幂等保护已够 reconnect 场景）
9. ~~改任何 Unity LiveKit 真实推流 / RoomManager 业务~~ → 只用 RoomManager 的 OnConnected / IsConnected 事件
10. ~~做联机 smoke~~ → 留给"联机 smoke + GAP-1" chat

---

## §8 后续 chat 入场提示词

### 8.1 "FocusBboxThreshold BB injection" Brain chat（解 F-05 step ③）

```text
你是 ParrotCarriers Sprint4 Phase 4 — F-05 Echo path step ③ 接通助手
（FocusBboxThreshold 读 BB global/attention_thresholds 注入构造参数）。

## 第一步（不可跳过）

读 .cursor/memory/architecture/sprint4_phase4_w6_w7_unity_completion_20260430.md
全文，特别是 §3.1 + §6.1 F-05 step ③。然后读 src/parrot/dsg/attention/threshold.py
顶部 docstring + DEFAULT 常量 + __init__ 当前签名。

## 范围

修改 src/parrot/dsg/attention/threshold.py:FocusBboxThreshold.__init__：
- 在使用 DEFAULT_* 之前先 open_bb_client(name="threshold_bootstrap",
  writer="dsg.attention.threshold").get("global/attention_thresholds")
- 读到 → 覆盖 delta_focus / delta_bbox / threshold / target_ttl_s
- 读不到 / schema_version 不匹配 → 用 DEFAULT_*（向后兼容）
- 加 1 个 test：spy BB 读出 → 验证 __init__ 用了 BB 值

## 不允许

不动 EcpEvent enum / DTO / event_ingest / publisher / observer / refs /
bb_schema 任何字段。Unity 半边完全不动。
跑 pytest tests/ --ignore=tests/integration → 期望 189/189。

## 收口

完成后单独跑一个 doc-only chat，把 bb_schema.py:global/attention_thresholds
的 # CANDIDATE 标记移除，更新 entry doc §8.1 L9 ⚠ 注为 "Echo 全链路接通"。
```

### 8.2 "联机 smoke + GAP-1 (EcpState ingest)" 后续 chat

W6-7 Unity + F-05 step ③ 都落地后：跑全链路 Editor → Brain → Editor，验证 §0.2 验收 #5（W3 EcpState 三态 LLM-surface 闭合 + W4-5 identify_object 同步预算 + W6-7 Echo + threshold cross 完整体感）。

---

## §9 引用

- 决策锁：`sprint4_phase4_entry_20260430.md` §8（authoritative）
- F-05 起源：`sprint4_phase4_brain_self_audit_20260430.md` §3.2 F-05
- W3.A.2/A.3 接合点：`sprint4_phase4_w3_a2_a3_completion_20260430.md`
- Observer/Attention 边界：entry doc §3.7
- 跨语言契约：`tests/test_ecp_event/test_cs_parity.py`
- bb_schema producer 真源：`src/parrot/shared/bb_schema.py:global/attention_thresholds`

---

## §10 前向兼容自审 — ChatBot / Live audio / 协作模式（用户 2026-04-30 追加锁）

> **关键基调**（用户 sign-off 时原话）：
> > ChatBot 在视频语音对话进行时其实不一定要完全同步，能用和通知消息发消息
> > 进行给任务调度器发东西就行，其实就是个 Nanobot 挂的 ChatBot，一个有
> > GOSLO 的意识，一个有 Cat Maid 的意识。
>
> **本节用途**：在 W6-7 落地后审计是否与"未来要做的 ChatBot 降级 / Live 视频
> 语音对话延伸 / 后期状态同步 / 协作模式"四条主线冲突。**当前 chat 不实现
> 这四条**（仍专注 W6-7 收口），仅记录边界让后续 chat 继承。

### §10.1 BB-中心化对齐（ChatBot 设计基线）

用户答了那个 rhetorical question：**ChatBot 不做 full state sync，BB 对齐 +
scheduler 通知就够**。这与 W6-7 的设计**完全契合**：

| W6-7 产出 | BB 可见范围 | ChatBot 接入方式 |
|:--|:--|:--|
| `global/attention_thresholds` | `BbScope.GLOBAL` | 直接读，不需要 LiveKit Room；Cat Maid Nanobot subagent 想知道当前 Δ / threshold → 一行 `bb.get` |
| `transient/current_attention_hint` | `BbScope.TRANSIENT` | 同上；threshold cross 后 ChatBot 也能看到"用户最近在意 X" |
| EcpEvent 流（`bbox.placed` / `attention.config.echo` 等） | 仅 LiveKit Room 内可见 | ChatBot **不需要**直接消费；Live agent 已经把结果落到 BB |

**结论**：ChatBot 经 BB 对齐路径**已天然就绪**；W6-7 没引入"必须 wire LiveKit
才能消费"的状态。

### §10.2 ChatBot 降级模式（无 Live agent 时的 Echo 行为）

**场景**：用户切到纯 ChatBot 模式（Live 视频语音不在线）。

**当前 W6-7 的限制**：
- `attention_config_handler.register(ingest)` 在 `brain.agent.brain_entrypoint`
  里 wire（line 386），即 **Live agent 启动时才挂**
- 纯 ChatBot 模式下若无 Live agent → 无 `event_ingest` → Echo 不到 Brain
- BUT：`global/attention_thresholds` 是持久化 BB key，**前次 Live session 写
  入的值在 ChatBot 模式仍可读**

**未来 ChatBot 降级 chat 的选项**（**不是本 chat 范围**）：
1. **A — 持久化 fallback**：纯 ChatBot 启动时若 BB key 已有值就用，否则用
   `dsg/attention/threshold.py:DEFAULT_*` 直读 → 不需要任何 Echo wire
2. **B — Nanobot 自挂 mini-handler**：Cat Maid Nanobot subagent 启动时自己挂
   一个 attention_config_handler 等价物，从配置文件 / Nanobot persona 读取
   阈值
3. **C — 跨模式 BB writer**：把 `attention_config_handler.register` 提升到
   "总线启动" 而不是 "Live agent 启动"，让 ChatBot 模式也能用同一 ingest
   （但 ChatBot 模式无 LiveKit Room → ingest 还是收不到 EcpEvent，本质是
   配置注入路径需重设计）

**推荐 A**（最小 surface），但这是 ChatBot chat 的决策。本 chat 不锁。

### §10.3 Live 视频语音对话 — W6-7 与现行 Live 模式无冲突

| 现行 Live 模式机制 | W6-7 是否动 |
|:--|:--|
| `parrot.ecp.state` topic（W3.A.3 EcpState 心跳 + 三态） | ✗ 不动 |
| `parrot.ecp.health` / `parrot.ecp.intent_disconnect` inline envelope | ✗ 不动 |
| Gemini Live RealtimeModel + ParrotAssistant tools | ✗ 不动 |
| ConnectionHealthAggregator + AppLifecycleManager | ✗ 不动 |
| RoomManager.OnConnected 已存在事件 | ✓ **新订阅**（Echo + BBox/Focus reconnect 重 publish）— **不抢占现有订阅者**（`AnimationDriver` / `RoomManagerLifecycleBridge` 都是独立 listeners） |
| ParticipantAttribute（spike S7 待定） | ✗ 不动 |

**关键不变量**：W6-7 只**增加** RoomManager.OnConnected 的 listener，不替换
任何现有 listener；Action 是 multicast delegate，新 listener 不互斥。

### §10.4 协作模式（GOSLO + Cat Maid 同时活跃）

**用户描述**："一个有 GOSLO 的意识，一个有 Cat Maid 的意识"。

**W6-7 对协作的支持面**：

| 协作场景 | W6-7 是否阻塞 | 理由 |
|:--|:--|:--|
| GOSLO Live 主导对话 + Cat Maid Nanobot 跑后台任务 | ✗ 不阻塞 | Cat Maid 经 BB 读 attention hint；scheduler 通知走现有 CH_SCHEDULER_TO_BRAIN（agent.py L451 已 wire） |
| 双 Brain 同时想响应同一 BBox | ⚠ 留 hook | `FocusBboxThreshold._publish_attention_event` 当前固定走 BRAIN source 单 publisher；多 Brain 想 join → 走 scheduler 协调，不要让两个 publisher 抢同一 BB writer (`dsg.attention.threshold` single producer 锁，bb_schema.py 已声明) |
| Cat Maid 想自己改 attention 阈值 | ⚠ Phase 5+ 决策 | 当前 `global/attention_thresholds` writer = `brain._rpc_bridge`（Unity SO 单一真源）；Cat Maid 想加自己的偏好 → 走另一条 BB key 或 Phase 5+ multi-producer 协调，本 chat 不开这个口 |
| GOSLO ↔ Cat Maid 模式切换 | ✗ 不阻塞 | LiveKit Room 重连场景已在 §B.6 覆盖；BB 持久化 |

**§3.7 Observer/Attention 边界 + 单 producer 原则**保护协作模式不退化为
multi-writer 战争。

### §10.5 后期状态同步 — 设计空间已隔离

W6-7 用的 wire/BB 通道：

| 通道 | 拥有者 | 后期 state sync 是否需要复用 |
|:--|:--|:--|
| `parrot.ecp.event` topic + `EcpEvent` envelope | Phase 4 wire envelope | 后期 state sync 应**新拓 topic**（如 `parrot.state.sync` 或走 ParticipantAttribute），不要复用 `parrot.ecp.event` 的 8KB / 60s dedup 语义 |
| BB `global/attention_thresholds` | Unity SO Echo（W6-7） | 后期 state sync 不应复用此 key；想做"双 Brain 共享当前 state"加新 key |
| RoomManager.OnConnected 事件 | multicast delegate | 后期可加更多 listener，互不干扰 |

**结论**：W6-7 设计**没有占用后期 state sync 必需的资源**；后期 chat 拓新
topic / 新 BB key 即可，不需要回头改 W6-7。

### §10.6 给后续 4 条主线 chat 的入场提示

| chat 主线 | 进入前必读 | 与 W6-7 的接合点 |
|:--|:--|:--|
| **F-05 step ③（已 spec，本 doc §8.1）** | `dsg/attention/threshold.py` + 本 doc §3.1 | `__init__` 读 BB `global/attention_thresholds`（W6-7 已写入） |
| **联机 smoke + GAP-1** | W3.A.2/A.3 completion + 本 doc §5 | 验 attention.config.echo + bbox.placed + threshold.crossed 全链路 |
| **ChatBot 降级模式** | 本 doc §10.2 + parrot_behavior_rules `parrot_behavior_rules.md` `chat_only_text` 状态 | Cat Maid Nanobot 经 BB 读 attention 配置；选择 §10.2 A/B/C 之一 |
| **协作模式 / 双意识** | 本 doc §10.4 + entry doc §3.7 | 不破坏 single-producer-per-key；多 Brain 协调走 scheduler |

---

## §11 收口签名

- 代码 commit：`4bd3475` (`feat(unity+brain): Phase 4 W6-7 Unity attention UI + Echo path ①+② (F-05)`)
- doc-only follow-up commit：`<本 doc §10/§11 落地后填>`
- 测试基线：`pytest tests/ --ignore=tests/integration -q` → **188/188 全绿**
- 跨语言对齐：`tests/test_ecp_event/test_cs_parity.py` → **4/4 全绿**
- 硬约束：10 条 audit defended 全部守住（threshold.py / observer/* / refs.py /
  bb_schema.py / W3.A.2/A.3 / _rpc_bridge.py / EcpEventDispatcher topic 路由 /
  ecp_event.py 8KB+topic+schema_version 常量 / lossy parrot.ecp.tick 拖动事件
  — 无一动）
- F-05 状态：① + ② LANDED；③ DEFERRED 给独立 Brain chat
- §B.6 reconnect / Brain 管线切换：BBox / Focus / Echo 全量重发已实施；refs.py +
  BB overwrite 双重幂等保护
- §10 前向兼容：ChatBot 降级 / Live audio / 协作 / 后期状态同步 4 主线均无冲突，
  接合点已 spec
