---
status: living
category: issue-tracker
created: 2026-05-04
last_reviewed: 2026-05-04
ai_priority: high
ai_audience: "任何后续 chat（Phase 5+ / 接口提炼 / 审计 / 真机 spike）— 已对照代码全面验证，覆盖 Sprint 1-4 全阶段"
verification_note: "所有条目均已对照实际代码验证（2026-05-04）。已修复项移入 §附录。跨越范围：Sprint 1-4 Phase 1-4 + 所有 completion report + audit doc + smoke report。"
sources:
  - "sprint4_phase4_completion_and_final_audit_20260430.md §5-§6"
  - "sprint4_phase4_brain_self_audit_20260430.md §3 §6.2"
  - "sprint4_phase4_online_smoke_completion_20260504.md §5 §8"
  - "sprint4_phase4_w3_a2_a3_completion_20260430.md §3"
  - "sprint4_phase4_w6_w7_unity_completion_20260430.md §6"
  - "sprint4_phase4_w8_unity_completion_20260430.md §0"
  - "sprint4_phase4_smoke_and_gap1_completion_20260430.md §5"
  - "sprint4_ecp_minimal_audit_20260429.md §1-§3"
  - "sprint3_completion_report_20260423.md §6 §8"
  - "audit_photo_awareness_memory_pipeline_20260429.md §9-§10"
  - "sprint4_livekit_stability_and_video_strategy.md §2-§7"
  - "sprint4_phase4_downstream_chat_dispatch_plan_20260504.md §1 §4"
---

# Sprint 1-4 遗留问题与待修复 Bug 整合（2026-05-04）

> **本文用途**：覆盖 Sprint 1-4 全阶段所有**仍开放**的 Bug、Finding、Defer 项、已知漂移。
>
> **验证方法**：每条均对照实际代码（grep / 文件读取）确认仍开放，已修复项见 §附录。
>
> **优先级**：🔴 高（阻塞功能/测试）| 🟡 中（潜在运行时问题）| 🟢 低（样式/doc）| ⏸ defer（Phase 5+ 明确触发）

---

## §0 TL;DR（按优先级排序）

| 编号 | 优先 | 一句话 | 来源阶段 |
|:--|:--|:--|:--|
| BUG-T1 | 🔴 | test_identify_object.py collection 失败（import 拿到 FunctionTool 非模块）| Phase 4 |
| BUG-P1 | 🔴 | `_write_ack` 仍是 legacy dict，`tick/last_ecp_ack` 非真 EcpAck dump | Phase 1 |
| BUG-P2 | 🔴 | `ecp.command.issued` / `ecp.ack.received` L0 events 完全未写入 | Phase 1 |
| BUG-U1 | 🔴 | `SnapshotService.cs` 不存在（ArSpike 无 captureSnapshot Unity 实现）| Sprint 3 |
| BUG-P3 | 🟡 | `ecp_state_ingest` sequence_id 仅 log，无去重逻辑 | Phase 4 |
| BUG-P4 | 🟡 | `session/ecp_state` 不随断连自动清空（OnDisconnect 无清 BB handler）| Phase 4 |
| BUG-P5 | 🟡 | `transient/last_sighting_event` BB key 声明 writer 但代码无实现 | Phase 4 |
| BUG-P6 | 🟢 | `missing_bbox_id` / `missing_focus_id` metric 单一 counter，不区分 placed/removed | Phase 4 |
| BUG-U2 | 🟡 | `sequence_id` publisher-local（重启回 0，无 boot_id 隔离命名空间）| Phase 4 |
| BUG-U3 | 🟡 | `UNITY_XR_HANDS` 包未装，真机手势路径永远不激活 | Phase 4 |
| BUG-U4 | 🟡 | Photo `previewSent=false` 时 PhotoNode 无法从 Brain 侧建立 | Phase 4 |
| GAP-1 | 🟡 | Photo AwarenessPolicy / PhotoFramePreview 完全未实现（设计 doc 仍 draft）| Phase 4 |
| GAP-2 | 🟡 | Sprint 3 外放回声 / Gemini Live VAD 打断自身（L1）| Sprint 3 |
| GAP-3 | 🟡 | 视频生命周期健康分层缺失（fresh frame / tier ack / consumer ack）（L2）| Sprint 3 |
| GAP-4 | 🟢 | 正式 AR Foundation 场景未建（ArSpike 仍是 spike 白模）（L6）| Sprint 3 |
| BB-C | 🟢 | BB schema `# CANDIDATE` 注释残留（4 处）| Phase 1-4 |
| DEFER-x | ⏸ | Phase 5+ 13 项 defer（协议/工具/性能/治理）| Phase 4 |

---

## §1 测试可执行性 Bug（🔴 高优先）

### BUG-T1 — test_identify_object.py collection 失败

```
severity:    🔴 高
confidence:  high（已 pytest 实测：AttributeError exit code 2）
file:        tests/test_ecp_event/test_identify_object.py:25,36

错误:        AttributeError: 'FunctionTool' object has no attribute '_match_staged'

根因:        line 25: from parrot.brain.tools import identify_object as id_module
             → 导入的是 __init__.py 中 @function_tool 装饰后的 FunctionTool 实例，
               而非 identify_object.py 模块本身。
             line 36: _match_staged = id_module._match_staged
             → FunctionTool 无此属性 → collection 阶段崩溃，所有 7 个测试跳过。

修法（1 行）:  将 line 25 改为：
               import parrot.brain.tools.identify_object as id_module
             其余代码已正确通过 id_module._match_staged 访问（line 36），
             通过 _func 访问 FunctionTool 内部协程（line 47），1 行改动即可。

status:      open — completion report §0 test_baseline 注记"pre-existing breakage
             留独立审计 chat 修"；2026-05-04 pytest 实测仍失败
触发修复:    Chat 5（独立审计 chat）或下一个接触 identify_object 的 chat
```

---

## §2 Python 代码层 Bug / 漂移（已代码验证）

### BUG-P1 — `_write_ack` 仍是 legacy dict，非真 EcpAck dump（🔴 高）

```
severity:    🔴 高（协议语义漂移 — 任何期望 EcpAck 字段的消费方会 KeyError）
confidence:  high（代码验证：_rpc_bridge.py:80-89 DRIFT NOTE 仍存在）
file:        src/parrot/brain/tools/_rpc_bridge.py:69-104

问题:        _write_ack 写入 tick/last_ecp_ack 的是 legacy 形状 dict：
             {ok, rpc, reason, detail, command_id, ecp_status, ts}
             而非 EcpAck Pydantic dump（缺少 frontend_state / ack_id /
             started_at / completed_at 等字段）。DRIFT NOTE 从 Sprint4 Phase 1
             （2026-04-29）起一直保留。

来源:        sprint4_ecp_minimal_audit_20260429.md §1 A1 "触发升级条件"：
             "Phase 2 让 Unity 上报完整 EcpState 时，重构为 EcpAck.model_dump(mode='json')"
             Phase 2-4 均未执行此升级。

影响:        context_injector / soul 任何期望 active_locks / frontend_state 的
             消费方读到的是 legacy dict，字段集不匹配。当前靠 None/default 兜底。

proposal:    Phase 5+ 接口提炼 chat 把 _write_ack 升级为真 EcpAck dump；
             需要 Unity Handler 侧同步返回完整字段集。

status:      open — DRIFT NOTE 仍在代码中
触发条件:    接口提炼 chat（Chat 4）或 Phase 5+ 全链路 ECP V2 完整化
```

### BUG-P2 — `ecp.command.issued` / `ecp.ack.received` L0 events 完全未写（🔴 高）

```
severity:    🔴 高（可观测性盲区：Brain 发出的 RPC 命令无 L0 事件记录）
confidence:  high（代码验证：_rpc_bridge.py 无 command_issued / ack_received / CH_ECP 写入）
file:        src/parrot/brain/tools/_rpc_bridge.py（所有 call_unity_rpc 调用点）

问题:        sprint4_ecp_minimal_audit_20260429.md §2 B1 要求在 call_unity_rpc
             chokepoint 写入 ecp.command.issued / ecp.ack.received L0 events。
             Phase 1-4 全部未实现。Brain 发出的每条 RPC 命令在 obs_log / events.log
             中不可追踪，调试时只能靠 Brain 日志人工追查。

proposal:    在 _rpc_bridge.call_unity_rpc 的 before/after 点各写一次 obs_log 条目，
             字段：{command_id, rpc, started_at, completed_at, ok, ecp_status}。
             不需要 Redis Stream 新建，复用现有 obs_log 通道。

status:      open — audit B1 升级条件未触发
触发条件:    Chat 4（接口提炼实施）或 Phase 5+ obs_log 补全 chat
```

### BUG-P3 — ecp_state_ingest sequence_id 仅 log，无去重逻辑（🟡 中）

```
severity:    🟡 中（重连时 1Hz 心跳 sequence_id 重复写 BB，短暂 stale 值）
confidence:  high（代码验证：ecp_state_ingest.py:167 只在 logger.debug 里用 seq，
             无 (unity_identity, sequence_id) 去重 dict）
file:        src/parrot/brain/ecp_state_ingest.py:155-171

问题:        ecp_state_ingest 每次收到 parrot.ecp.state packet 都直接写 BB，
             不检查 (unity_identity, sequence_id) 是否已处理过。
             重连时 Publisher 若从 sequence_id=0 重新开始，可能写入重复/回退的包。
             smoke+GAP-1 completion report §5 明确标注"⚠ 未做"。

proposal:    在 _dispatch 前维护 _seen: dict[str, int]（key=unity_identity,
             value=last_seq），sequence_id ≤ last_seq 则 skip。
             重启检测：若 sequence_id 比 last_seq 小很多（gap > threshold），
             视为 Publisher 重启，重置 last_seq。

status:      open — smoke+GAP-1 completion §5 第一行明确"⚠ 未做"
触发条件:    Phase 5+ 真机重连压测 or 下一次 ecp_state_ingest 相关 chat
```

### BUG-P4 — `session/ecp_state` 不随断连自动清空（🟡 中）

```
severity:    🟡 中（旧 session 值在下次 connect 前被消费方读到）
confidence:  high（代码验证：ecp_state_ingest.py / agent.py 无 OnDisconnected → BB clear）
file:        src/parrot/brain/agent.py（_on_room_disconnected handler）
             src/parrot/brain/ecp_state_ingest.py

问题:        room disconnect 后 BB session/ecp_state 保持上一 session 的值。
             若 reconnect 较慢，_state_context 读到的 active_locks / active_command_id
             来自已失效的上一 session，影响 LLM 注入准确性。
             smoke+GAP-1 completion §5 明确标注"⚠ 未做"。

proposal:    agent.py _on_room_disconnected 加：
               from parrot.brain.ecp_state_ingest import clear_ecp_state_bb
               clear_ecp_state_bb()
             ecp_state_ingest 加 clear_ecp_state_bb() 函数写 None 或 {}。

status:      open — smoke+GAP-1 completion §5 第二行明确"⚠ 未做"
触发条件:    Phase 5+ 防御性加固 chat 或下一次 ecp_state_ingest chat
```

### BUG-P5 — `transient/last_sighting_event` BB key 声明有写者但代码无实现（🟢 低）

```
severity:    🟢 低（doc/code 不一致；下游无消费方依赖此 key）
confidence:  high（代码验证：sighting.py _async_matched_side_effects 只走 archiver，
             无任何 bb.set；bb_schema.py:296 仍有 # CANDIDATE）
file:        src/parrot/shared/bb_schema.py:296
             src/parrot/brain/observer/sighting.py

options:
  A. observer/sighting 加 BB write（参考 photo observer 模式）
  B. 移除 bb_schema writer 声明 + 标 Phase 5+
  C. 现状 + 加注释"declared but unwritten in Phase 4"（最低成本，建议）

status:      open — proposed C 方案
触发条件:    Phase 5+ sighting → RefBinding resolver flow
```

### BUG-P6 — bbox / focus `missing_*_id` metric 不区分 placed vs removed（🟢 低）

```
severity:    🟢 低（observability）
confidence:  high（代码验证：bbox.py:63,82 / focus.py:43,63 同一 counter）
proposal:    拆为 missing_bbox_id_placed + missing_bbox_id_removed（~6 行）
status:      ⏸ defer — Phase 5+ HUD M2 开发时
```

### BB-C — bb_schema `# CANDIDATE` 注释残留（doc-only 清理）

| key | 行号 | 清理时机 |
|:--|:--|:--|
| `session/connection_health` | bb_schema.py:162 | Phase 5+ health 聚合 |
| `session/audio_route_policy` | bb_schema.py:170 | Phase 5+ 蓝牙/音频路由 |
| `transient/last_sighting_event` | bb_schema.py:296 | Phase 5+ sighting resolver（BUG-P5）|
| `transient/current_attention_hint` 历史注释块 | bb_schema.py:267 | 任意 doc-only chat（1 行删除）|

---

## §3 Unity 代码层开放问题（已代码验证）

### BUG-U1 — `SnapshotService.cs` 不存在（🔴 高）

```
severity:    🔴 高（captureSnapshot 工具链在 ArSpike 端无 Unity 实现）
confidence:  high（代码验证：ArSpike 无任何 SnapshotService / AsyncGPUReadback /
             captureSnapshot RPC handler；只有 ParrotLifecycleConfig.cs:101-109
             里的 captureSnapshot 配置字段）
file:        unity/ArSpike/（缺失文件）

问题:        Sprint 3 §9 Arrow#1 已规划"ARVideoPublisher XRCpuImage 帧捕获接口"；
             Sprint 3 simulation audit §截图生命周期 已 spec S4.A 实现路径；
             Phase 4 identify_object / PhotoController 的 capture_current_frame()
             在 Brain 端有实现，但 Unity ArSpike 端没有对应的 RPC handler 来
             响应 captureSnapshot 请求。Brain 的 vision/snapshot.py 调用
             Unity RPC，Unity 侧收不到。

当前状态:    Brain vision/snapshot.py 存在但 Unity 侧 captureSnapshot RPC
             handler 未实现 → identify_object snapshot 路径无法在 ArSpike 端
             正常工作。

proposal:    ArSpike 加 SnapshotRpcHandler.cs：
             响应 "captureSnapshot" RPC → AsyncGPUReadback / ARCameraManager
             → base64 JPEG → return EcpAck shape。
             可参考 sprint3_simulation_audit §截图生命周期 的 spec。

status:      open — Sprint 3 遗留，Phase 4 未实现
触发条件:    验收 #2（identify_object 真机测试）前必须实现
```

### BUG-U2 — `sequence_id` publisher-local，重启后可能与旧 session 冲突（🟡 中）

```
severity:    🟡 中
confidence:  high（代码验证：LifecycleHeartbeatPublisher.cs 无 boot_id；
             EcpStateDto.cs:94 sequence_id 是 publisher-local long）
file:        unity/ArSpike/Assets/Scripts/ParrotApp/Ecp/LifecycleHeartbeatPublisher.cs

问题:        Publisher 每次重启（场景重载 / App 重启）sequence_id 从 0 开始，
             可能与 Brain BUG-P3 提到的去重逻辑（未实现）产生碰撞。

proposal:    Unity 侧加 boot_id（Guid.NewGuid()，每次 Awake 生成），
             作为 EcpStateDto 附加字段。Brain ingest 侧更新去重 key 为
             (unity_identity, boot_id, sequence_id)。

status:      open — sprint4_phase4_w3_a2_a3_completion_20260430.md §3.2 D-3
触发条件:    真机长期使用 + 多次断重连（Phase 5+ 真机 spike）
```

### BUG-U3 — `UNITY_XR_HANDS` 包未装，真机手势路径不激活（🟡 中）

```
severity:    🟡 中（验收 #1 perch_to_finger 真机前置条件）
confidence:  high（代码验证：HandGestureSource.cs:4,37,73,89,103,110,115
             全部 #if UNITY_XR_HANDS 守护；运行时打印"gesture detection inactive"）
file:        unity/ArSpike/Assets/Scripts/ParrotApp/Hands/HandGestureSource.cs

问题:        com.unity.xr.hands 未装 + csc.rsp 未加 define，真机上食指手势
             路径永远不走。当前只能 ContextMenu 触发。

待决策（用户）:
  A. 装 com.unity.xr.hands + csc.rsp -define:UNITY_XR_HANDS
  B. 保持 ContextMenu，通过 XR Interaction Toolkit 触发

status:      Q-1 待用户决策 — sprint4_phase4_w3_a2_a3_completion_20260430.md §3.4
触发条件:    验收 #1 真机测试前必须决策
```

### BUG-U4 — Photo `previewSent=false` 时 PhotoNode 无法从 Brain 侧建立（🟡 中）

```
severity:    🟡 中（设计限制：room 断开时拍照 PhotoNode 丢失）
confidence:  high（代码验证：PhotoController.cs reconnect 逻辑只重试 HTTP POST
             不补发 preview EcpEvent；smoke+GAP-1 completion §5 第五行）
file:        unity/ArSpike/Assets/Scripts/ParrotApp/Photo/PhotoController.cs

问题:        Room 断开时拍照：preview EcpEvent 发送失败（previewSent=false），
             Brain 无 PhotoNode。重连后 HTTP POST 成功，Brain observer.photo 收到
             asset 但无对应 PhotoNode（log: "asset_for_unknown_photo_id"）。
             照片资产孤立，无法关联 L2-B 节点。

proposal:    Phase 5+ 选项：本地存 preview payload（PlayerPrefs/磁盘），
             reconnect 后先补发 preview EcpEvent 再发 HTTP POST。
             目前 FullResJpeg 内存缓存也在 App 重启后丢失。

status:      ⏸ Phase 5+ — smoke+GAP-1 completion §5
触发条件:    Phase 5+ session resume / 照片可靠性保障 chat
```

### Unity 其他 defer 项

| 项 | 优先 | 说明 |
|:--|:--|:--|
| `parrot.ecp.tick` lossy 拖动事件未实现 | 🟢 | BBoxController.cs:18 / FocusController.cs:18 明确注明 OOS |
| Photo AR 正式帧抓取路径（Camera.main spike）| 🟡 | PhotoController.cs:292 — Phase 5+ ARCameraManager.frameReceived |

---

## §4 设计缺口（已设计但代码零实现）

### GAP-1 — Photo AwarenessPolicy / PhotoFramePreview 完全未实现（🟡 中）

```
severity:    🟡 中（功能缺失：GOSLO 拍照时体感空洞）
confidence:  high（代码验证：全代码库无 AwarenessPolicy / AwarenessDecision /
             PhotoFramePreview / AWARE_REACT / UNAWARE_RECORDED 任何符号）
设计文档:    audit_photo_awareness_memory_pipeline_20260429.md（status: draft）

已设计但未做:
  • PhotoFramePreview schema（即时低质量 preview + TTL cache）
  • AwarenessDecision（5 态：UNAWARE_RECORDED/AWARE_SILENT/AWARE_REACT/
    AWARE_INTERRUPT/STARTLED）
  • AwarenessPolicy 输入信号综合（相机准备/注意力/GOSLO状态/用户设置/事件强度）
  • ToolCost 字段（blocks_speech/expected_latency_ms/can_run_after_turn）

当前实际行为:
  拍照 → photo.taken_preview EcpEvent → Brain observer.photo → BB last_photo_event
  GOSLO 无 aware/unaware 意识状态判断，无即时感知反应机制。

设计文档待决问题（§10，全部未定）:
  1. preview 默认尺寸（256 vs 512 长边）
  2. preview cache 落位（进程内/Redis/本地文件）
  3. 拍照通知默认值（静默/小反应/通知）
  4. GOSLO 被拍默认动作（看镜头/歪头/保持当前）
  5. photo_preview_caption 是否在 Phase 5+ 做成真正 tool
  6. PhotoNode 何时默认进 Graphiti

status:      open — 设计 doc status:draft，0 行代码
触发条件:    Phase 5+ Photo awareness / GOSLO 拍照反应 chat
```

### GAP-2 — Sprint 3 遗留 L1：外放回声 / Gemini Live VAD 打断自身（🟡 中）

```
severity:    🟡 中（语音体感问题 — GOSLO 自己说的话被麦克风拾回再触发 Gemini）
confidence:  high（代码验证：MicrophonePublisher 无 echo cancellation 配置；
             Brain agent 无 VAD 策略调整；sprint3_completion_report §8.5 原话记录）
file:        src/parrot/brain/agent.py（无 interrupt/VAD 策略设置）
             unity/ArSpike/Assets/Scripts/ParrotApp/LiveKit/MicrophonePublisher.cs

问题:        Sprint 3 真机测试确认：GOSLO 外放声被手机麦克风拾回 → Gemini Live
             VAD 当作用户输入 → 复读/打断/角色错归因。
             当前代码无任何 echo cancellation 或 interrupt sensitivity 配置。

options:
  A. 蓝牙耳机（规避外放路径）
  B. Gemini Live manual VAD（activityStart/activityEnd）
  C. NO_INTERRUPTION / 降低 interruption sensitivity
  D. LiveKit Agents Silero VAD / noise cancellation plugin
  E. 自建 ASR → 文本/多模态通道（高代价）

status:      open — sprint3_completion_report §6 L1 → §8.5；Phase 4 未处理
触发条件:    正式 AR App 语音体验优化 chat（Phase 5+）
```

---

## §5 Sprint 3 遗留（Phase 4 未解决）

### Sprint 3 L2 — 视频生命周期健康状态分层缺失（🟡 中）

```
severity:    🟡 中
confidence:  high（代码验证：ARVideoPublisher 有 RebuildTrack，但无"fresh frame"
             / "tier ack" / "consumer ack"分层健康检测）

问题:        sprint3_completion_report §6 L2 要求分五层：
             track published / first frame / fresh frame / tier ack / consumer ack。
             Phase 3 实现了 ConnectionHealthAggregator 和 EcpState，但：
             - "fresh frame"检测未实现（video_age 字段是 Brain 侧读 LastFrame 时间，
               Unity 侧无主动上报"当前帧是否 fresh"）
             - "tier ack"语义已通过 EcpAck 部分实现，但 BUG-P1 的 legacy dict 限制了完整性
             - "consumer ack"（Gemini Live 是否真正消费帧）无实现

status:      ⏸ 部分遗留 — Phase 5+ 完整视频生命周期健康 chat
```

### Sprint 3 L4 — Graphiti 写入后台化（已部分完成，性能问题仍存）

```
severity:    🟢 低（架构已后台化，性能待优化）
confidence:  medium（代码验证：conversation_writer.py 有 start_background() +
             periodic_flush + batch；但 20-46s 延迟是 Graphiti/FalkorDB 性能问题）

当前状态:   conversation_writer 有 asyncio.create_task(_periodic_flush()) 后台化；
            但 add_episode 本身在 FalkorDB 上可达 20-46s（sprint3 实测）。
            这不是架构问题，是 FalkorDB 性能问题（2C8G 内存有限）。

status:      ⏸ Phase 5+ 性能优化（降频、限流、降采样策略）
```

### Sprint 3 L6 — 正式 AR Foundation 场景未建（🟢 低）

```
severity:    🟢 低（影响用户体验，不影响后端链路）
confidence:  high（代码验证：ArSpike/Assets/Scenes/ 只有 ParrotSmokeScene.unity）

问题:        sprint3_completion_report §6 L6：正式 AR Foundation 主场景（Launcher +
             平面检测 + 放置 + 锚点持久化 + GOSLO 真实动画）未建。
             当前 ArSpike 是白模/spike 工作区，有 ContextMenu 调试路径。

status:      ⏸ Phase 5+（接口提炼完成后建正式 App）
触发条件:    Chat 4（接口提炼）完成 + 用户 sign off → 正式 AR App 阶段
```

---

## §6 联机 Smoke Findings（4 项仍开放）

> finding-1 安全组 ✅ 修；finding-3 agentName ✅ 修。以下仍开放。

| Finding | 优先 | 说明 | 代码验证 |
|:--|:--|:--|:--|
| **finding-2** photo.asset_uploaded 回程不可见 | 🟢 | EcpEventPublisher.cs:48 `logOnSuccess = false` | 已验证 |
| **finding-4** Editor 切窗口 → OnApplicationPause 断连 | 🟡 | AppLifecycleManager.cs:108 → ShortBackground → intent.disconnect；临时修法：RunInBackground | 已验证 |
| **finding-5** WebRTC ICE 握手 ~32s | 🟡 | STUN/TURN 未优化；本地↔Castle 公网 NAT | 实测 |
| **finding-6** EcpEventPublisher logOnSuccess 默认关 | 🟢 | EcpEventPublisher.cs:48 | 已验证 |

---

## §7 Phase 5+ Defer（13 项，明确触发条件）

### §7.1 协议层（3 项）

| 项 | 触发条件 |
|:--|:--|
| L1.5 预加载 Node 池 + ConfirmationStatus 扩展 | Chat 2 完成后 |
| Multi-Brain BB scope `peer/` | 双 Nanobot 真活跃 |
| EcpEvent schema_version=2 演进策略 | 字段集实质变化时 |

### §7.2 工具层（5 项）

| 项 | 触发条件 |
|:--|:--|
| identify_object L2 完整化（web_search + Nanobot 同步）| Phase 5+ chat |
| Editor HUD M2（Attention / Photo / EcpState）| 调试需要 |
| Sighting → identify_object resolver flow（RefBinding RESOLVED）| Phase 5+ resolver |
| `goslo-chat /forget_snapshots` 隐私命令 | 真机 spike 后 |
| captureSnapshot ECP-化（snapshot.captured 真实路径）| Phase 5+ snapshot chat |

### §7.3 性能 / 健壮性（3 项）

| 项 | 触发条件 |
|:--|:--|
| attention_config_handler OnDisconnect 清 BB | 防御性加固 |
| Photo HTTP 鉴权 + S3/MinIO 对象存储 | 正式部署 |
| W8 reconnect bytes 跨重启持久化（PhotoController FullResJpeg）| Phase 5+ session resume |

### §7.4 治理 / 文档（2 项）

| 项 | 触发条件 |
|:--|:--|
| bb_schema `# CANDIDATE` 注释清理（4处，见 BB-C）| 各自对应 Phase 5+ chat |
| L2-B EdgeKind.HAS_PHOTO / CAPTURED_VIA / CANDIDATE_SUBJECT connect 调用 | Episode lifecycle 完整化 |

---

## §8 LiveKit 稳定性 / 视频策略（Phase 5+ 研究项，0 代码落地）

| 项 | 优先 |
|:--|:--|
| 直连 vs TURN 对照测试 | 🟡 |
| 域名 + TLS/WSS 部署（当前 `ws://<ip>:7880`）| 🟡 |
| host networking 或等价低开销路径 | 🟡 |
| 主视频档位门控落地（Gemini Low/按需识别/A10升档/调试上限）| 🟡 |
| Unity 端首帧 / 生命周期 / 档位闸口 | 🟡 |
| WebRTC 最小高信号指标采集（RTT/loss/jitter）| 🟢 |
| 云端 Bus 闸口（A10 在线 + 识别任务 + 升档控制）| 🟢 |

---

## §9 验收 Defer（真机 #1/#2）

| 验收 | 前提条件 | 何时补 |
|:--|:--|:--|
| **#1 perch_to_finger** | BUG-U3（XR Hands）必须先决策 | 首版正式 App |
| **#2 identify_object 1.9s** | BUG-U1（SnapshotService）必须先实现 | 同上 |

---

## §10 接口层未提炼（Chat 3/4/5 工作对象）

wire 协议已锁 ✅；以下 6 类未提炼：

| 类别 | 下游 Chat |
|:--|:--|
| SDK / 扩展面 | Chat 4 预留扩展点章节 |
| 接口文档组织（11 类 ~60 doc 无 single entry）| Chat 4 选定维度 |
| 单份 vs 双份（人 / AI）| Chat 4 裁决 |
| 角色切换接口面（ParrotBodyState 强绑鹦鹉）| Chat 4 §5.1 例 1 |
| Schema 演进策略（v1 已锁，v2 未定）| Chat 4 版本演进章节 |
| 稳定性签名（commit → 接口面影响）| Chat 5 freeze test 推广 |

---

## §11 下游 Chat 工作项

| Chat | 任务 | 依赖 | 状态 |
|:--|:--|:--|:--|
| Chat 1 | ConceptGraph 蒸馏 | 无 | ⏳ 待派 |
| Chat 2 | L1.5 池设计 | Chat 1 | ⏳ 待做 |
| Chat 3 | 协议+接口 ADR fork | 无 | 🔄 进行中 |
| Chat 4 | 接口提炼实施（含 BUG-P1/P2 升级路径）| Chat 3 | ⏳ 待派 |
| Chat 5 | 独立审计（**含 BUG-T1 修复**）| Chat 4 | ⏳ 待派 |
| Chat 6 | Sprint 4 总结报告 | Chat 4+5 | ⏳ 待派 |
| Chat 7 | P2.5 完成汇报 | 真机 spike | ⏳ 最后 |

**Phase 4 → 5 转换完成 checklist**：
- [ ] Chat 1-7 依次完成
- [ ] BUG-U1 SnapshotService.cs 实现（验收 #2 前置）
- [ ] BUG-U3 XR Hands 决策（验收 #1 前置）
- [ ] 真机 spike → 验收 #1/#2 ✅

---

## §12 快速索引（代码真源）

| 需要看什么 | 代码位置 |
|:--|:--|
| BUG-T1 import 断裂 | `tests/test_ecp_event/test_identify_object.py:25` |
| BUG-P1 _write_ack DRIFT NOTE | `src/parrot/brain/tools/_rpc_bridge.py:80-89` |
| BUG-P2 command_issued 缺失 | `src/parrot/brain/tools/_rpc_bridge.py`（全文无 command_issued）|
| BUG-P3 sequence_id 仅 log | `src/parrot/brain/ecp_state_ingest.py:167` |
| BUG-P4 OnDisconnect 无清 BB | `src/parrot/brain/agent.py:_on_room_disconnected` |
| BUG-P5 last_sighting_event | `src/parrot/shared/bb_schema.py:296` + `sighting.py` |
| BUG-P6 missing_bbox_id | `src/parrot/brain/observer/bbox.py:63,82` |
| BUG-U1 SnapshotService 缺失 | `unity/ArSpike/`（grep SnapshotService → 0 结果）|
| BUG-U2 sequence_id 无 boot_id | `unity/.../Ecp/LifecycleHeartbeatPublisher.cs` |
| BUG-U3 XR Hands 守护 | `unity/.../Hands/HandGestureSource.cs:4,37,73...` |
| BUG-U4 previewSent=false | `unity/.../Photo/PhotoController.cs reconnect 逻辑` |
| GAP-1 AwarenessPolicy 零代码 | 全代码库（grep AwarenessPolicy → 0 结果）|
| GAP-2 外放回声 | sprint3_completion_report.md §6 L1 §8.5 |
| BB-C CANDIDATE 残留 | `src/parrot/shared/bb_schema.py:162,170,267,296` |
| Phase 5+ defer 13 项 | `sprint4_phase4_completion_and_final_audit_20260430.md §6` |

---

## §附录 已修复项（代码验证已修，不再追踪）

| 项 | 修复证据 |
|:--|:--|
| Brain 自审 F-01（sighting docstring）| sighting.py 重写 docstring |
| Brain 自审 F-02（sighting +0.05 L2-B）| _async_matched_side_effects 只走 archiver |
| Brain 自审 F-03（evidence_score 死代码）| identify_object.py:331 注释 "float ≥ 0.0 by design" |
| Brain 自审 F-04（threshold docstring）| threshold.py:16 已改 `{subject_kind}:{subject_id}` |
| Brain 自审 F-06（reset_refs_for_session）| agent.py:566-567 已落 |
| Brain 自审 F-09-B（threshold key `{kind}:{id}`）| threshold.py:355 已改 |
| Brain 自审 F-13（dispatch docstring）| threshold.py:39-40 "Phase 5+ territory. The path is pre-wired..." |
| GAP-1 Finding B（session/ecp_state ingest）| brain/ecp_state_ingest.py 落地 |
| ECP-minimal A1 type_hint（阶段性）| bb_schema type_hint 降为 dict[str,Any] + DRIFT NOTE |
| ECP-minimal A2（ECP_SUCCESS_STATUSES）| ecp.py 拆 TERMINAL_SUCCESS + INTERMEDIATE |
| ECP-minimal A3（active_locks Unity DTO）| EcpStateDto.cs active_locks 字段 |
| smoke finding-1（安全组 7889）| 阿里云入方向规则 |
| smoke finding-3（agentName dispatch）| commit `228ef0d` |
| W3 D-2（EcpEventDispatcher using LiveKit.Proto）| EcpEventDispatcher.cs:5 存在 |
| W6-7 Unity F-A22/F-A4/F-A33 cold-read | commit `5ec7640` |
| Sprint 3 A1-A6 / B1-B5 / simulation audit B1-B5 | sprint3_completion_report §3-§4 |
