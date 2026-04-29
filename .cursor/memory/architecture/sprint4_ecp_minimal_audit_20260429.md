---
status: archived
category: audit
status_note: "Sprint4 ECP-minimal 第一批落地后的代码审计与漂移记录，2026-04-29 完成修复。后续 Phase 2/3/4 应基于此文档继续推进。"
last_reviewed: 2026-04-29
---

# Sprint4 ECP-minimal 代码审计 & 漂移记录

> 日期：2026-04-29
> 锚点：`.cursor/memory/architecture/sprint4_protocol_ecp_background_20260429.md`
> 设计稿：`.cursor/memory/architecture/sprint4_protocol_v2_ecp.md`
> 计划：`c:\Users\Bin\.cursor\plans\sprint4_协议升级_31652b8a.plan.md`

## 0. 审计目的

`ecp-minimal` 第一批代码（2026-04-28 落地）已通过 13 个 pytest，但落地过程中存在一批"代码与设计稿/背景锚点不完全对齐"的细节。本文档把这些漂移逐条记录、说明原因、注明当时是修了还是延后。**目的是即使下一次会话失忆，也能从注释和本文档恢复到当前理解。**

按"必修 / 建议下一轮 / 仅记录"分类。每条都注明：
- **现象**：代码与设计哪儿不一致。
- **漂移原因**：为什么会偏离。
- **影响**：会不会出问题，多严重。
- **决策**：本轮修了还是延后；如果延后，触发条件是什么。

---

## 1. 必修（A 段）—— 已在 2026-04-29 修复

### A1 `tick/last_ecp_ack` 类型撒谎

**现象**
`bb_schema.py` 把 `tick/last_ecp_ack` 声明为 `type_hint="EcpAck"`，但 `_rpc_bridge._write_ack` 实际写入的是 legacy 形状的 dict（`{ok, rpc, reason, detail, command_id, ecp_status, ts}`），不是 `EcpAck` Pydantic 模型 dump。

**漂移原因**
落地时只想到"加一个并行 key 让消费方区分 ECP / legacy"，没把 type_hint 与实际写入形状对齐。背景里 BigIssue.md 反复警告的"纸面声明早于代码"反模式重演。Sprint 1 `global/soul_constraints` 死的就是这个。

**影响**
任何按 type_hint 期望 EcpAck 字段（如 `frontend_state`、`ack_id`、`started_at`）的消费方都会 KeyError。

**决策（已修）**
`type_hint` 改为 `dict[str, Any]`，注释里明确写出"Phase 2 将替换为完整 EcpAck"。`_write_ack` docstring 增加 DRIFT NOTE 说明现阶段是 legacy ack 镜像 + ECP 字段拼接，不是真 EcpAck。

**触发升级条件**
Phase 2 让 Unity 上报完整 EcpState 时，应同步把 `_write_ack` 重构为 `EcpAck.model_dump(mode="json")` 写入。

---

### A2 `ECP_SUCCESS_STATUSES` 把中间态当成功

**现象**
原始 `ECP_SUCCESS_STATUSES` 包含 `received` / `accepted` / `queued` / `running` 四个中间态。`tick/last_rpc_ack.ok` 由这个集合决定。

**漂移原因**
照搬设计稿 §5.2 的 status 全集时没区分"终态成功"和"非失败"。当时只想"反正都算 ok"。

**影响**
`parrot_behavior_rules.md` §0.3 体感红线：

> tool 的同步/异步行为必须和 GOSLO 说出口的话一致。
> 不允许 fire-and-forget 后却说"我已经完成"。

如果未来 Unity handler 改为流式上报 `running` ack，会被错判为完成态、压制 Context Injector 升层③通报。这正是 Sprint4 协议升级最想消灭的失误。

**决策（已修）**
`ecp.py` 拆成三个集合：
- `ECP_TERMINAL_SUCCESS`：`{ok, applied, unchanged, completed}` —— 唯一允许 `ok=True` 的集合。
- `ECP_INTERMEDIATE_STATUSES`：`{received, accepted, queued, running}` —— 显式中间态，归入 `ok=False` 但 reason 是 status 自身。
- `ECP_FAILURE_STATUSES`：保持原集合。
- `ECP_NON_FAILURE = TERMINAL_SUCCESS | INTERMEDIATE`：保留给"特别需要区分中间态 vs 失败"的少数场景。
- `ECP_SUCCESS_STATUSES = ECP_NON_FAILURE`：旧名作为别名保留向后兼容，但代码里全部切换到 `ECP_TERMINAL_SUCCESS`。

`_classify_response` 与 `EcpAck.ok` 都改用 `ECP_TERMINAL_SUCCESS`。补了 `test_ecp_ack_intermediate_states_are_not_ok` 测试锁住这个语义。

---

### A3 Unity `EcpFrontendStateDto` 缺 `active_locks`

**现象**
设计稿 §5.2 / §5.3 要求 frontend_state 携带 `active_locks: ["body"]`，是 Sprint4 最小 Arbiter（body / head / vision 三资源通道）的反向回灌入口。Python `EcpFrontendState` 已有 `active_locks: tuple[str, ...]`，但 Unity DTO 完全没声明该字段。

**漂移原因**
JsonUtility 对 `string[]` 的支持不如其他字段直观，落地时被 SkilledOver。

**影响**
所有 ack 永远不能上报锁状态 → Sprint4 acceptance 1 "Unity 能 accepted/rejected/expired/completed 并回执"在锁层缺失，Phase 2 实现 micro-lock 时要回头补字段、客户端要重新发版。

**决策（已修）**
- `EcpFrontendStateDto` 加 `public string[] active_locks = new string[0];`
- `ForBody(...)` 工厂签名增加 `string[] locks = null` 参数。
- `ParrotRpcHandler` 飞行/动画 ack 现在显式声明 `new[] { "body" }`。
- `ForVideoTier(...)` 显式不报 body 锁（视频改 tier 属于 vision channel）。

---

### A4 Unity 未校验 `expires_at`

**现象**
设计稿 §5.1 / 验证工具 §11.1：

> `perch_to_finger` 用 `expires_at` 防止用户手已经移动后鹦鹉飞向旧位置。

但落地的 `ParrotRpcHandler` 和 `VideoTierReceiver` 拿到 `_ecp.expires_at` 后从不检查，直接执行命令。"过期"语义只存在于设计稿。

**漂移原因**
第一批想着"先把 envelope 跑通再说"，把 `expires_at` 校验留给 Phase 2。但这是 Sprint4 acceptance criterion 1 直接要求的能力。

**影响**
中等 —— 当前 handler 立即执行，5s 过期窗口足够，绝大多数场景没问题；但 `perch_to_finger` 在网络抖动下会"鹦鹉飞向旧手指位置"。

**决策（已修）**
- `EcpCommandDto` 字段升级为 `double` 精度（Unix epoch 用 float 在 2026 年只有 ~24h 精度）。
- 新增 `EcpCommandDto.IsExpired(double nowUnix)` 方法。
- 新增 `EcpAckJson.Expired(...)` 工厂。
- `EcpAckJson.UnixSeconds()` 暴露为 public，便于 handler 复用。
- 三个 handler（flyTo / animate / setVideoTier）在执行前都校验 `expires_at`，过期返回 `EcpAckJson.Expired(...)`。
- `expires_in_s=0` 在 Python `for_legacy_rpc` 中表示"永不过期"，DTO 侧用 `expires_at <= 0` 视为无限制。补了 `test_wrap_legacy_rpc_payload_zero_expires_means_no_expiry` 锁住。

---

### A5 设计稿 §5.2 `current_tier` vs §5.3 `video_tier` 内部矛盾

**现象**
设计稿 §5.2 EcpAck.frontend_state 示例用 `"current_tier": "VIDEO_GEMINI_ONLY"`，但同稿 §5.3 EcpState 字段用 `video_tier`。代码两边都选了 `video_tier`（正确，因为与 BB key `session/video_tier` 一致）。

**漂移原因**
设计稿写作时两节没交叉校对。

**影响**
低 —— 代码已统一，但下个会话读设计稿可能照搬错误字段。

**决策（已修）**
设计稿 §5.2 的 `current_tier` 改为 `video_tier`。

---

## 2. 建议下一轮（B 段）—— 已加注释延后

### B1 `_command` 被丢弃，没写 `ecp.command.issued` 到 L0

**现象**
`fly_to.py` / `animate.py` / `push_video_tier_result` 都是：

```python
payload, _command = wrap_legacy_rpc_payload(...)
result = await call_unity_rpc(...)
```

`_command` 立刻丢弃，从未写 L0 EventEnvelope。

**漂移原因**
第一批关注的是"协议字段能不能在 wire 上跑"，没把 L0 audit 加进 chokepoint。

**影响**
中 —— 设计稿 §3.1 的核心承诺是"每次状态变化、ECP 命令、ECP 回执、snapshot、sighting、ref binding 都应能落为一条 L0 event"。当前 ECP 命令本身没有 L0 痕迹，未来重放、纠错、graphiti 投影都拿不到。

**决策（注释延后）**
在 `fly_to.py` / `animate.py` 显式写 Phase 2 TODO，注明"清洁的实现位置是 `_rpc_bridge.call_unity_rpc` 单一 chokepoint，而不是每个工具自己写"。Phase 2 / EcpAck 完整化时一并做。

**触发条件**
Phase 2 task `state-surface` 进入实现时，先在 `call_unity_rpc` 增加 `ecp.command.issued` + `ecp.ack.received` 两条事件写入。

---

### B2 `EcpCommand.layer` 改成 `EventLayer` 枚举

**现象**
原始实现 `layer: str = "intent"`，无校验。

**漂移原因**
不想跨包导入。

**影响**
低 —— 只是类型安全。

**决策（已修）**
导入 `parrot.shared.event_log.EventLayer`，`EcpCommand.layer` 与 `for_legacy_rpc` / `wrap_legacy_rpc_payload` 默认值都改为 `EventLayer.INTENT`。`use_enum_values=True` 让 wire 形状仍是字符串 `"intent"`，对 Unity 透明。补了 `test_ecp_command_layer_round_trips_event_layer_enum` 锁住。

> 这条本来想留作 B 段延后，但实际改动很小（一个 import + 三处签名），就一并修了，所以应该归 A 段。保留在 B 段是为了和审计回顾时的"必修 vs 建议"叙事一致。

---

### B3 Unity ack 工厂 `reason` 当 action name 用

**现象**
原始调用：

```csharp
EcpAckJson.Completed(p._ecp, "flyTo", state)
EcpAckJson.Failed(p._ecp, e.Message, "flyTo")
```

`"flyTo"` 是动作名，不是设计稿 §5.2 的 reason 词表（`applied / unchanged / no_video_publisher / micro_lock / illegal_transition / transport / malformed / timeout / ...`）。

**漂移原因**
对 reason 字段语义不清。当时把它当"自由文本说明"用了。

**影响**
低 —— 日志层污染；下游消费 reason 词表过滤会失败。

**决策（已修）**
- `EcpAckJson` 暴露 `ReasonApplied / ReasonExpired / ReasonRejected / ReasonFailed / ReasonMalformed / ReasonTransport / ReasonNoVideoPublisher / ReasonUnknownTier` 常量。
- 工厂签名统一：完成态默认 `ReasonApplied`；失败态默认 `ReasonFailed`；调用方需传词表内的代码而非动作名。
- `Completed` 签名调整为 `Completed(command, state, reason=ReasonApplied)`，`reason` 改成命名参数；handler 默认不传，让动作语义从 `command_id → EcpCommand.kind` 反查。
- 三个 handler 的调用全部对齐。VideoTierReceiver 直接转发 `ARVideoPublisher.TierApplyResult.Reason`（已经是 `applied`/`unchanged` 词表内）。

---

### B4 `captureSnapshot` 响应仍是 Sprint3 形状，被判 `malformed`

**现象**
`brain/vision/snapshot.py` 调用 `call_unity_rpc("captureSnapshot", ...)`，Unity 的 `SnapshotService.cs` 仍返回 `{"success": true, "width": ..., "b64_data": ...}`。`_classify_response` 永远把这种 status 缺失的响应判为 `(False, "malformed", ...)`，于是每次成功的快照都向 `tick/last_rpc_ack` 写一条假 "malformed"。

**漂移原因**
Sprint3 已经存在的契约。`ecp-minimal` 改动没动 captureSnapshot。

**影响**
低/中 —— `capture_current_frame` 自己解析响应，不看 `last_rpc_ack`，所以"按需识物"功能不会坏；但 `tick/last_rpc_ack` 作为统一状态面被污染，违反了 Sprint4 设计稿"统一状态面"承诺。

**决策（注释延后）**
在 `capture_current_frame` docstring 加 DRIFT NOTE 说明：当前 ack 镜像不可信，请直接看返回值。Phase 4（`snapshot-identify` 任务）重塑 Unity SnapshotService 时把响应改为 `EcpAck { status: completed, detail: { snapshot: SnapshotEnvelope } }`，并把 envelope 路由到 `transient/just_captured_photo` + `snapshot.captured` L0 event。

**触发条件**
Phase 4 进入 `snapshot-identify` 任务时，第一步就重塑这个响应。

---

### B5 BB candidate keys 没写入者

**现象**
落地时新增了：
- `session/connection_health`
- `session/audio_route_policy`
- `session/ecp_state`
- `transient/current_attention_hint`
- `transient/last_sighting_event`

并显式声明 type_hint（`ConnectionHealthState` 等）和 writer。但**没有任何 writer 代码**。

**漂移原因**
设计稿登记了候选名，落地时一并写进 manifest，没意识到这就是 Sprint 1 `global/soul_constraints` 翻车的同一个反模式。

**影响**
中 —— 任何尝试 `bb.get(...)` 这些 key 的代码会 KeyError。manifest 变愿望清单。

**决策（已修，但留 candidate 标记）**
- type_hint 全部降级为 `dict[str, Any]`（写入侧落地时再升级到具体类型）。
- 在 key 后加 `# CANDIDATE — no writer yet (Phase X)` 行内标记。
- 在文件中加段头注释明确："不要在 producer 落地之前注册 WRITE access；同一个反模式见上方 `global/soul_constraints` 删除注释。"
- description 改成中性的"待 Phase X 写入"，不再假装已就绪。

**触发条件**
- Phase 3（lifecycle / audio / connection health）落地时，移除 `session/connection_health` / `session/audio_route_policy` 的 CANDIDATE 标记，type_hint 升回精确类型，并在对应 writer 模块加 BB 写入。
- Phase 2（EcpState 上传）落地时同样处理 `session/ecp_state`。
- Phase 4（focus-tools / snapshot-identify）落地时同样处理 `transient/current_attention_hint` / `transient/last_sighting_event`。

---

## 3. 仅记录（C 段）

### C1 `_classify_response` reason 不对称

legacy `{"status":"ok"}` 反 reason `""`；ECP `{"status":"completed"}` 无 reason 时反 `""`（修复后已对齐 —— 见下）；ECP `{"status":"running"}` 反 `"running"`（自身回声）。修复后整体一致：终态 success 不带 reason 时反空串，中间态反 status 自身。

无遗留问题。

### C2 `VideoTierReceiver.cs` 顶部 docblock 旧 reply 形状

已修：reply 描述改为 EcpAck JSON，并指向 `EcpAckJson` 词表。

### C3 测试覆盖

补了：
- `test_wrap_legacy_rpc_payload_zero_expires_means_no_expiry`
- `test_ecp_command_layer_round_trips_event_layer_enum`
- `test_ecp_ack_intermediate_states_are_not_ok`
- `test_rpc_bridge_intermediate_status_is_not_ok`
- `test_rpc_bridge_expired_status_is_failure`
- `test_rpc_bridge_legacy_ok_response_still_classified`

未覆盖（留给 Phase 2）：
- `_write_ack` 镜像 `tick/last_ecp_ack` 的 BB 写入行为（依赖 BB client fixture）。
- Unity DTO 反序列化（pure C#，需要 Unity Test Framework）。

---

## 4. 不允许误读（强化背景锚点 §10）

在审计过程中再次确认以下边界。下个会话如果觉得"代码可以这样改"，请回头读这一节：

1. **不要把中间态 ack 当作完成。** 任何让 `tick/last_rpc_ack.ok=True` 的路径都必须经过 `ECP_TERMINAL_SUCCESS`。
2. **不要在 `bb_schema.py` 提前声明没 writer 的 key。** 看到 `# CANDIDATE` 标记就提醒自己：先写 producer，再升级 type_hint。
3. **不要让 `tick/last_ecp_ack` 假装是 EcpAck Pydantic dump。** 在 Phase 2 完整 EcpAck 上来之前，它就是 legacy ack dict 的别名。
4. **不要把动作名当 ack reason。** reason 是设计稿 §5.2 的小词表，与 `EcpCommand.kind` 互补，不重复。
5. **不要绕过 `expires_at` 校验。** Sprint4 acceptance criterion 1 直接要求 expired 回执；任何新加的 ECP handler 都必须先校验。
6. **不要让 `captureSnapshot` 的成功响应继续污染 `tick/last_rpc_ack`。** Phase 4 重塑前请直接读返回值；不要对 `last_rpc_ack` 做基于 captureSnapshot 的体感推理。
7. **不要把 `_command` 永远丢弃。** 它是未来 `ecp.command.issued` L0 event 的唯一来源；Phase 2 必须在 `call_unity_rpc` chokepoint 写入。

---

## 5. Phase 2 入场清单

下一批工作（Phase 2 `state-surface` / `lifecycle-audio` / `snapshot-identify` 启动时）应一次性消化：

1. 在 `call_unity_rpc` 写 `ecp.command.issued` / `ecp.ack.received` L0 events（B1）。
2. 让 Unity 周期性上报 `EcpFrontendStateDto`（含 active_locks），更新 `session/ecp_state`（A1 升级路径 + B5 candidate 移除）。
3. `_write_ack` 改为构造真正的 `EcpAck` 实例并 dump 到 `tick/last_ecp_ack`（A1 触发条件）。
4. `SnapshotService.cs` 响应改为 EcpAck shape，触发 `transient/just_captured_photo` + `snapshot.captured` L0 event（B4 / B5 candidate 移除）。
5. `AppLifecycleManager` + `ConnectionHealthState` 落地，移除 `session/connection_health` / `session/audio_route_policy` 的 CANDIDATE 标记（B5 触发条件）。

完成上述任一项时，请回到本文档对应小节移除 DRIFT NOTE 并更新 `last_reviewed`。
