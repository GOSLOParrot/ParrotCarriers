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
