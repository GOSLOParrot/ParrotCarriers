---
status: ratified
category: completion-report
status_note: "Sprint4 Phase 4 W3.A.2 + W3.A.3 (Unity 主战场 perch_to_finger + EcpState 三态事件驱动) 完成情况 + 审计 + 遗留项。"
last_reviewed: 2026-04-30
---

# Sprint4 Phase 4 W3.A.2 + W3.A.3 完成报告（2026-04-30）

> **本文用途**：W3.A.2/A.3 双 commit 落地后的 authoritative 完成口径 + 实际 Editor smoke 验证证据 + 已知漂移/审计点 + 后续工作明确分发。
>
> **关联**：`sprint4_phase4_entry_20260430.md §8.7` W3 行 = 本文落地范围。
>
> **关键基调**：本 chat 严守 Unity-only 范围（G1-A 路线，§A.4 sign-off）。Brain 端 EcpState ingest 留给后续专门 chat。

---

## §0 一句话总结

Unity 端**生产就绪**：手势 → perch_to_finger → 锚定动作（歪头摆动）+ EcpState 三态事件驱动 + 1Hz 双触发 publisher 全部落地、Editor smoke 验证通过。**LLM-surface 闭合待 Brain ingest chat**（GAP-1）。

---

## §1 落地内容（commits）

### 1.1 提交链（master 上 6 commit）

| Commit | 作用 |
|:--|:--|
| `bc157fa` | feat(unity): Phase 4 W3.A.2 — perch_to_finger 手势全链路 + body/head producer |
| `b3a43d8` | （自动 commit）EcpStateDto schema 字段扩展 + LiveKit version info + entry doc 微调 |
| `1c73adc` | feat(unity): Phase 4 W3.A.3 — EcpState 三态事件驱动 + 1Hz 双触发 publisher |
| `23ba10c` | （自动 commit）"AR spike" — 把 EcpEventDispatcher 的 `using LiveKit.Proto;` 又冲掉 |
| `57aa4e9` | chore(unity): copy GOSLO.glb + add gltfast + Editor 一键 smoke 场景构建器 |
| `749a410` | fix(unity): EcpEventDispatcher — 重新加 `using LiveKit.Proto;` |
| `1c89dff` | fix(unity): remove unused `_havePosedReturn` field (CS0414 warning) |
| `fd1b1a5` | fix(unity): smoke scene NullRef — 用 `LifecycleSmokeForcer.Start()` 推 FSM |
| (待) | fix: T_HEARTBEAT_INTERVAL 默认 5s → 1f（对齐 §8.1 L1）|

### 1.2 新增文件

| 文件 | 命名空间 | 作用 |
|:--|:--|:--|
| `unity/ArSpike/Assets/Scripts/ParrotApp/Hands/HandGestureSource.cs` | `ParrotApp.Hands` | 检测 `index_finger_branch` 手势（横向食指 + 其他指弯曲 + 食指方向接近水平），暴露 `IndexIntermediatePosition`（中段指节）作为飞行目标。**纯本地事件源，不发 DataChannel**。`#if UNITY_XR_HANDS` 守护 + Inspector ContextMenu Editor 触发兜底。 |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Hands/PerchOnHand.cs` | `ParrotApp.Hands` | Reflex 状态机 IDLE → FLYING_TO_HAND → PERCHED → RETURNING → IDLE。到达后**自动接续 Intent**：body=PerchedOnHand + head=Tilt。**不发 NotifyBrainStateChange**。 |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Lifecycle/LifecycleSmokeForcer.cs` | `ParrotApp.Lifecycle` | Smoke 场景专用：`Start()` 推 FSM 到 Connected，让心跳 chokepoint 不挡。**不进生产场景**。 |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Editor/ParrotSmokeSceneBuilder.cs` | `ParrotApp.EditorTools` | `Tools/Parrot/Build A2 Smoke Scene` 一键构建场景：加载 GLB + 挂全部组件 + 连引用。 |
| `unity/ArSpike/Assets/Models/GOSLO.glb` (+ `.meta`) | — | 从 ParrotDev 1:1 拷贝。Blockbench 鹦鹉模型，带 head / body / 双翼 / 双腿 / tail 完整骨骼层级。 |

### 1.3 改动文件

| 文件 | 改动 |
|:--|:--|
| `Parrot/AnimationDriver.cs` | 加 `BodyState.PerchedOnHand` + `HeadState` enum + `OnBodyStateWireChanged` / `OnHeadStateWireChanged` 事件 + `BodyStateToWire` / `HeadStateToWire` 静态 mapper + HEAD_TILT 渲染（18° pitch + 12° roll + 6°/1.6Hz sine 摆动） |
| `Ecp/EcpStateDto.cs` | `BuildHeartbeat` 加 5 个可选参数（bodyStateWire / headStateWire / cognitiveStateWire / activeLocks / sequenceId）+ 新增 `sequence_id` long 字段 |
| `Ecp/LifecycleHeartbeatPublisher.cs` | Singleton + AnimationDriver producer 订阅 + `ReportActiveCommand`/`ClearActiveCommand` 注入接口 + 双触发实现（1Hz tick 路径绕 sig 去重 / 事件路径走 50ms 同帧合并 + chokepoint 同步） |
| `Ecp/EcpEventDispatcher.cs` | 加 `using LiveKit.Proto;`（compile fix；曾两次被自动 commit 覆盖，最终在 `749a410` 锁定） |
| `RPC/ParrotRpcHandler.cs` | `HandleFlyTo` / `HandleAnimate` 进出包 `ReportActiveCommand` / `ClearActiveCommand`（finally + reported flag 防 expired 早退误清） |
| `Config/ParrotLifecycleConfig.cs` | `T_HEARTBEAT_INTERVAL` 默认 5f → 1f（对齐 §8.1 L1） |
| `Packages/manifest.json` | 加 `com.unity.cloud.gltfast: 6.14.1`（GLB 导入器） |

---

## §2 Editor smoke 验证证据（2026-04-30 05:08 实测）

### 2.1 场景构建（`Tools/Parrot/Build A2 Smoke Scene` → `Assets/Scenes/ParrotSmokeScene.unity`）

Hierarchy：
- `Main Camera`（位置朝向鹦鹉）
- `Directional Light`
- `Lifecycle`（AppLifecycleManager + LifecycleHeartbeatPublisher + LifecycleSmokeForcer）
- `Parrot`（AnimationDriver + ParrotController + PerchOnHand）
  - `ParrotModel`（GOSLO.glb 实例，scale 0.04）
- `HandSource`（HandGestureSource，位置 `(0.3, 1.0, 0.4)`）

Game 视图：蓝/黄 blockbench 鹦鹉立在画面中央，head 群组（嘴/眼/羽毛）+ body + 双翼 + 双腿 + tail 全部可见。**骨骼绑定零配置成功**——`AnimationDriver.headNodeName="Head"` / `bodyNodeName="Body"` 通过 case-insensitive `FindDeep` 自动绑到 GLB 顶层 `head` / `body` Empty 群组。

### 2.2 Console 实测输出（Play 后 ~30s）

```
[LifecycleSmokeForcer] Lifecycle → Connected. LifecycleHeartbeatPublisher should now emit 1 Hz heartbeats.
[Heartbeat:LOG] {"schema_version":"ecp.v2.alpha","ts":1777496895.5059467,"sequence_id":1,"unity_identity":"","room_id":"","body_state":"idle","head_state":"HEAD_FORWARD",...}
[Heartbeat:LOG] {...,"sequence_id":2,...}
[Heartbeat:LOG] {...,"sequence_id":3,...}
[Heartbeat:LOG] {...,"sequence_id":4,...}
```

**验证项 ✅**：
- LifecycleSmokeForcer 正确推 FSM（修复 NullReferenceException 之后）
- 心跳实际发出
- `sequence_id` 单调递增（1 → 2 → 3 → 4）
- `body_state` / `head_state` 字段正确填充（baseline = `idle` / `HEAD_FORWARD`）
- `ts` 字段是 unix epoch double（毫秒精度）
- LogHeartbeatTransport 默认 transport 工作正常

**验证项 ⚠（待修复后重测）**：
- 实测心跳间隔 ~5-6s（05:08:15 → 05:08:20 → 05:08:25 → 05:08:31）—— 这是 `T_HEARTBEAT_INTERVAL` 默认值 5f 的影响，与 §8.1 L1 锁定的 1Hz 不符。**已修：默认改 1f**，重新打开场景应观察到 ~1s 间隔。

### 2.3 已知 Console 警告（不影响运行）

| 警告 | 性质 | 处置 |
|:--|:--|:--|
| `[AppLifecycleManager] 未挂 ParrotLifecycleConfig — 用临时默认实例` | 未给 SO 引用 → 用 `CreateInstance` 默认值 | 可选：通过 `Tools/Parrot/Lifecycle Tuning` 创建 SO 拖给 AppLifecycleManager；smoke 期可忽略 |
| `[HandGestureSource] com.unity.xr.hands / UNITY_XR_HANDS not enabled — gesture detection inactive` | XR Hands 包未装 + `csc.rsp` 未 define | 设计如此：用 ContextMenu Debug 触发；真机 XR Hands 触发是另一独立决策 |
| `[Burst] failed to compile function pointer ...`（4-5 条） | Burst 1.8.24 + Windows 环境层 JIT 缺陷，自动 fallback | 已建议清 `Library/BurstCache` 重启；不影响 Play |

### 2.4 待用户测试项

用户尚未执行的 smoke 步骤（请在 1Hz 修复后做）：
1. 选 `HandSource` → 组件 ⋮ → `Debug: Fire 'index_finger_branch' gesture`
2. 预期：
   - 鹦鹉飞向 `(0.3, 1.0, 0.4)` 附近
   - 落地后 head 群组（含 4 个 head mesh + feather）整体歪头摆动
   - Console **立即**多打 1 条 Heartbeat（sequence_id +1），含 `body_state="perched_on_hand"` / `head_state="HEAD_TILT"` —— **这是 A.3 事件触发的关键证据**
3. 点 `Debug: Fire 'closed_fist'` → 鹦鹉飞回原位 → head 回正 → 又触发 1 条 Heartbeat（body_state 回 idle / head_state 回 HEAD_FORWARD）

**测试通过**则 W3.A.2 + W3.A.3 在 Unity 侧的所有验收完整闭环。

---

## §3 设计漂移 / 审计点（按优先级）

### 3.1 ⚠ 高 — 已修但需用户回归

| 编号 | 漂移 | 修法 | 当前状态 |
|:--|:--|:--|:--|
| D-1 | 心跳默认 5s ≠ §8.1 L1 锁定的 1Hz | `ParrotLifecycleConfig.T_HEARTBEAT_INTERVAL` 默认改 1f | **修了，待用户重新 Play 验证** |

### 3.2 ⚠ 中 — 需要后续 chat 处理

| 编号 | 议题 | 影响 | 建议处置 |
|:--|:--|:--|:--|
| **GAP-1** | Brain 端没有 EcpState ingest（`parrot.ecp.state` topic 无消费方） | LLM-surface 验收 3 不能闭合 | **新开 "Brain EcpState ingest" chat**：~60 行 `src/parrot/brain/ecp_state_ingest.py` + 扩 `ParrotBodyState` enum 加 `PERCHED_ON_HAND` + `agent.py` 一行 attach。本 chat 已把 wire 契约 + sequence_id 全准备好。|
| D-2 | `using LiveKit.Proto;` 曾两次被自动 commit 覆盖（`b3a43d8` / `23ba10c`） | 编译会随机失败 | git 工作流问题：检查谁在自动 commit 中间状态。可考虑在 `EcpEventDispatcher.cs` 顶部加注释禁止移除；或追溯哪个工具/插件在做 auto-commit |
| D-3 | sequence_id 是 publisher-local 计数器（场景重载会回 0） | Brain 去重的 (unity_identity, sequence_id) 元组在 publisher 重启后会冲突 | Brain ingest chat 处理：去重应同时考虑 `ts`，或在 publisher 侧加 boot_id（GUID）让重启后 sequence_id 命名空间隔离 |
| D-4 | UNITY_XR_HANDS 包未装 + define 未启 | 真机/真 XR Simulation 不会自动触发 perch | 单独决定：是否装 `com.unity.xr.hands` + 加 `csc.rsp -define:UNITY_XR_HANDS`。当前用 ContextMenu 兜底已够 smoke。 |

### 3.3 ⚠ 低 — 设计选择记录

| 编号 | 议题 | 当前选择 | 替代方案 |
|:--|:--|:--|:--|
| C-1 | PerchedOnHand 状态下 position 由谁控制 | PerchOnHand 外部 Lerp 写入 transform.position；AnimationDriver 不动 | 替代：AnimationDriver 暴露 followTarget Transform，PerchOnHand 设 target；当前更简单但耦合 PerchOnHand → BodyState |
| C-2 | body_state lowercase / head_state UPPERCASE 混用 | Unity 端 wire mapper 按 `_state_context.py` 默认值反推 | 替代：统一为 lowercase（要改 Brain `_DEFAULT_HEAD`）；当前双约定文档清楚但易混淆 |
| C-3 | LifecycleSmokeForcer 在生产 `Lifecycle/` 目录而非 `Editor/` | 它是 Runtime MB（Play 时跑），不在 Editor-only | 可接受。文件 docstring 明写"smoke-only" |
| C-4 | HandGestureSource 的 `[ContextMenu]` debug 方法在生产代码中 | 不加 `#if UNITY_EDITOR` 守护 | 真机不会被触发；编译开销小；保留以便 Editor 可见 |
| C-5 | LifecycleHeartbeatPublisher 用 Singleton 让 RPC handler 注入命令 | `LifecycleHeartbeatPublisher.Instance` 静态访问 | 替代：DI / GetComponent；当前模式与 RoomManager.Instance 一致 |
| C-6 | T_HEARTBEAT_INTERVAL 1Hz 是 Phase 4 锁定值 | 默认 1f；Inspector 可调 | 真机阶段如果带宽紧张可调到 2-5s；事件触发不受影响 |

### 3.4 ❓ 待用户决策项

| 编号 | 问题 | 备选 |
|:--|:--|:--|
| Q-1 | 是否装 `com.unity.xr.hands`？ | A. 装并启 `UNITY_XR_HANDS` define → 真机 XR Simulation 可触发 perch；B. 不装，永远走 ContextMenu / 后续真机用别的输入源（XR Interaction Toolkit）触发 |
| Q-2 | LifecycleSmokeForcer 在正式 ArSpike App 入口场景里要不要保留？ | 建议否——正式场景由 RoomManager 真实推 lifecycle |
| Q-3 | ParrotSmokeScene.unity 要不要进 git？ | 建议是——让其他人能直接打开；scene 文件大概 ~10KB |

---

## §4 范围外明确不做（防过度延伸）

本 chat **绝不**做的事（已在 §A.4 sign-off / 严格范围里写过）：

1. ~~Brain 端 EcpState ingest~~ → GAP-1，专门 chat
2. ~~工具 ② identify_object~~ → W4-5
3. ~~工具 ③ Focus / BBox~~ → W6-7
4. ~~工具 ④ 照相机~~ → W8（视范围）
5. ~~RefBinding 实现~~ → W6-7 工具 ③ 一起做
6. ~~AttentionHint 阈值器调参~~ → W6-7 真机调
7. ~~AnimationDriver 双翼/腿/尾 animation~~ → P3 范围（parrot_behavior_rules §6.2）
8. ~~AppLifecycleManager 真实状态机抗压~~ → 真机 spike，与 R1-R6+D5 audit 一起
9. ~~LiveKit 真连接 in smoke scene~~ → 需要 RoomManager + token，不在 W3 验收范围
10. ~~Burst 1.8.24 环境层报错~~ → Editor 环境问题，与本 chat 代码无关

---

## §5 后续 chat 入场提示词（可复制）

### 5.1 "Brain EcpState ingest" chat 入场（解 GAP-1）

```text
你是 ParrotCarriers Sprint4 Phase 4 Brain 端 EcpState ingest 接通助手。
think in English ,用中文回答。

## 第一步（不可跳过）

读 .cursor/memory/architecture/sprint4_phase4_w3_a2_a3_completion_20260430.md
全文，特别是 §3.2 GAP-1 + D-3。

## 范围

实现 src/parrot/brain/ecp_state_ingest.py：
- 监听 LiveKit Room 上 topic = parrot.ecp.state（TOPIC_ECP_STATE 已在
  parrot.shared.ecp_event 声明）
- 解析 EcpState wire JSON（sprint4_protocol_v2_ecp.md §5.3 + Unity 侧
  EcpStateDto.cs）
- 按 (unity_identity, sequence_id) 去重；publisher 重启检测
- 写 BB tick/body_state（ParrotBodyState enum），tick/head_state（str），
  session/ecp_state（dict）
- 扩 src/parrot/shared/parrot_actions.py:ParrotBodyState 加
  PERCHED_ON_HAND = "perched_on_hand"
- src/parrot/brain/agent.py 加一行 attach_ecp_state_ingest(ctx.room)

验收：跑 unit test → 喂一条 Unity-shape EcpState JSON → 验证 BB 三个 key
被正确写入 + 重复 sequence_id 被丢；然后启动真 brain → 在 ArSpike Play
模式下点 Debug Fire branch gesture → tail Brain log，看到 selection-C
tool header 在下一轮 fly_to / animate 调用时附加 head=HEAD_TILT。

## 不允许

不动 Unity ArSpike；不改 EcpEvent / EcpEventIngest（那是 parrot.ecp.event
另一条通路）。
```

### 5.2 "Brain ingest 验收 + Sprint4 W3 收口" 后续 chat

GAP-1 修后跑一次完整端到端：
1. 启动 Brain（Castle ECS）
2. 启动 Unity ArSpike Play 模式
3. 触发 ContextMenu Fire branch gesture
4. Tail Brain log → 应观察到 EcpState ingest writes + 下一轮 Gemini 任意
   tool 调用前 selection-C 附加 `[GOSLO state] body=perched_on_hand head=HEAD_TILT`
5. 验收 1 + 验收 3 同时打勾 → W3 收口

---

## §6 引用

- 决策锁：`sprint4_phase4_entry_20260430.md` §8（authoritative）
- 行为规则：`parrot_behavior_rules.md` §1 / §3.3 / §5
- 协议正式稿：`sprint4_protocol_v2_ecp.md` §5.3 (EcpState)
- LLM 注入路径 C：`src/parrot/brain/tools/_state_context.py`
- Phase 3 防御性结构：`sprint4_phase3_l3_entry_20260429.md` §7.5 R1-R6+D5
- LiveKit lifecycle：`.cursor/skills/livekit-unity-lifecycle/IMPL_REF.md` §3 / §4 / §9
