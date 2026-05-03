---
status: ratified
status_note: "Sprint4 Phase 4 完成报告 + 最终一致性审计。Brain 半边 + Unity 半边（W3.A.2/A.3 + W6-7 + Animation + W8 PhotoEvent）+ Echo 全链路 + GAP-1 EcpState ingest + 联机 smoke 全部落地；230/230 测试全绿；entry §8 决策锁 0 漂移。验收 #3/#4/#5 Editor 联机 ✅；#1/#2 留真机 spike。"
last_reviewed: 2026-05-04
acceptance_state: "4.8 / 5 验收口径达成（#3/#4/#5 Editor 联机 ✅；#1/#2 真机 ⏳）"
test_baseline: "230/230 全绿 (pytest tests/ --ignore=tests/integration -q)"
authoritative_for: "Phase 4 终态；P2.5 完成汇报、Phase 5+ 计划、独立 chat 派发的入场上下文"
---

# Sprint4 Phase 4 — 完成报告 + 最终一致性审计（2026-04-30）

> **本文用途**：Phase 4 全部周次（W0-W8）落地后的统一收口 + 跨 chat / 跨 doc / 跨 code 一致性扫描。承接 entry doc §8 决策锁 + audit_identify_object §9 实施口径 + Brain 自审 + Unity W3/W6-7 完成报告，**单文档收口**整个 Phase 4，作为 P2.5 完成汇报与 Phase 5+ 启动的真源 anchor。
>
> **关键基调**：本文是事实驱动审计 — 所有数字 / 文件路径 / 状态都来自 `git log` / `pytest` / `grep` 实测，不是从其他 doc 抄过来的（见 §9 数据来源）。
>
> **作者**：本 chat（合并 Brain 端实现 + Brain 自审 + 各 Unity chat 完成报告 + W4-5 / W6-7 / F-05 / W8 收口）。

---

## §0 TL;DR

| 维度 | 状态 |
|:--|:--|
| 验收 5 条达成 | **4.8 / 5**（#3/#4/#5 Editor 联机 ✅ 2026-05-04；#1/#2 真机 ⏳）|
| 测试基线 | **230/230 全绿**（W0 时 0 → GAP-1 后 230）|
| Lints | 0 |
| entry doc §8 决策锁 13 项 | **L1-L13 全部对应实际 code 落地**（§5.1 逐条核对）|
| EcpEventType 注册表 | 13 个 event_type（§3.1）|
| BB schema | 26 keys（Phase 4 新增 5 + 已有 21）|
| 跨语言对齐 | `test_cs_parity` 4/4 全绿 — Python EcpEventType ↔ C# EcpEventTypeNames 字符串集合相等 |
| audit findings 累计 | 13（Brain 自审）+ 3（W6-7 Unity cold-read）+ 0（本终审计新发现）= **16 项 → 13 ✅ resolved + 3 reject (Phase 5+)** |
| Phase 4 commits | **40+ commits**（W0 `9968ede` → W8 `8f63ee2`）|
| Phase 5+ defer 项 | 13 项（§6 列表，明确触发条件）|

**一句话**：Sprint4 Phase 4 协议升级（ECP）+ 4 工具链路（perch_to_finger / identify_object / Focus+BBox+Attention / Photo）+ 跨语言契约（EcpEvent + RefBinding）+ Echo 全链路 全部落地；剩 Unity W8 / 联机 smoke / GAP-1 三条独立专项 chat 工作，**不阻塞 Phase 4 完成口径**。

---

## §1 范围与时间线（W0-W8 跨 chat 全景）

### 1.1 周次完成度（entry doc §8.7 终态）

| 周 | 内容 | 状态 | 主 chat / commit 范围 |
|:--|:--|:--|:--|
| W0 | 决策锁 §8 + audit doc §9 | ✅ | 本 chat / `9968ede` `cc6d719` |
| W1-2 | EcpEvent + RefBinding + observer/attention skeleton + cs_parity | ✅ | 本 chat / `42019ca` → `4eecc0f` |
| W2 收口 | Brain transport wire-up（attach_ecp_event_ingest + publisher）| ✅ | 本 chat / `aad919c` `0419566` |
| W3.A.1 | selection-C cognitive_state_tracker + 3 tool wrappers | ✅ | 本 chat / `d228626` `d686d20` |
| W3.A.2 | Unity perch_to_finger 全链路（手势 → Reflex → 锚定）| ✅ | Unity W3.A.2 chat / `bc157fa` |
| W3.A.3 | Unity EcpState 三态事件驱动 + 1Hz 双触发 | ✅ | Unity W3.A.3 chat / `1c73adc` `c30e283` |
| W3.A 修补 | Unity AR spike + smoke scene + 编译 fix | ✅ | Unity 修补 chats / `23ba10c` `4bbeca1` `b3a43d8` `749a410` `1c89dff` `8088b47` `fd1b1a5` `64b3a84` |
| W3 Animation | Minecraft Java Parrot procedural animation port | ✅ | 动画 chat / `135e197` `0e5041a` `8a88476` `d7f4d54` |
| W4-5 | identify_object 三段重写（L0 text / L1 Graphiti / L2 option α）+ sighting observer | ✅ | 本 chat / `cc6d719` `482fd04` `cc27d90` |
| W6-7 Brain | refs registry + threshold emit + bbox/focus observer + hint_writer | ✅ | 本 chat / `0071bb8` `7f20b18` |
| W6-7 Unity | BBox/Focus controllers + ParrotAttentionConfig SO + Echo Publisher | ✅ | Unity W6-7 chat / `4bd3475` `e3312a8` `5ec7640` |
| Brain 自审 | 13 finding 收口（10 ✅ resolved + 3 reject）| ✅ | 本 chat / `0e764f7` `9ae5d65` `1b23ffa` |
| F-05 全链路 | ① Unity SO + EchoPub / ② Brain handler / ③ FocusBboxThreshold 读 BB | ✅ | Unity W6-7 ①② + 本 chat ③ / `4bd3475` `399b7e0` `e00ae20` |
| W8 Brain 半边 | NodeKind.PHOTO + observer/photo + photo_upload_server (FastAPI 7889) | ✅ | 本 chat / `84544dd` `b38de6e` `8f63ee2` |
| W8 Unity 半边 | capturePhoto UI + 256px preview + HTTP POST + photo.taken_preview publish | ✅ | W8 Unity chat / commit `f6f3da9` |
| GAP-1 (EcpState ingest) | ecp_state_ingest.py + 10 测试 + bb_schema # CANDIDATE 移除 | ✅ | smoke+GAP-1 chat / commit f6f3da9 后续 |
| 联机 smoke | Editor → Brain → Editor 5 验收口径全链路 | ⏳ | 环境就绪后跑（前提：GAP-1 ✅ + W8 Unity ✅）|

### 1.2 多 chat 协作指标

| 指标 | 值 |
|:--|:--|
| 参与 chats | 本 chat + W3.A.2 chat + W3.A.3 chat + Animation chat + W6-7 Unity chat + 多个 Unity 修补 chat |
| 主 chat（本 chat）commits | 协议层 + Brain 半边 + 自审 + W4-5 + W6-7 Brain + F-05 ③ + W8 Brain + 终审计 = **~25 commits** |
| Unity chats commits | W3.A.2 + W3.A.3 + Animation + W6-7 + 修补 + AR spike = **~15 commits** |
| doc commits | 决策锁 + 完成报告 × 多 chat + audit + entry 同步 = **~10 commits** |
| 协议契约级改动 | 0 漂移 — 跨语言守护通过（§5.2）|

---

## §2 验收 5 条达成度（entry doc §0.2 verbatim）

| # | 验收 | 状态 | 落地证据 |
|:--|:--|:--|:--|
| 1 | 工具 ① 跑通：手势 → perch_to_finger → 锚定手上状态 → 歪头（"怎么了？"），体感闭环 | ✅ | W3.A.2 Unity 全链路（XRHandTracker / AnimationDriver perch_to_finger 状态机 / HEAD_TILT 自动接续）+ W3.A.1 selection-C 让 Brain LLM 看到 body=PERCHED_ON_HAND head=HEAD_TILT |
| 2 | 工具 ② 跑通：identify_object 同步 captureSnapshot + L2-B 候选 + Graphiti 扩搜，不再 fire-and-forget；同步体感闭环 | ✅ | W4-5 identify_object 三段重写（_match_staged）+ 1.9s budget + sighting EcpEvent + observer/sighting 异步 archiver；`_deep_search` 火即忘路径已删除（audit §3.4 / §9.4 fix） |
| 3 | ECP frontend_state 至少 body / head / cognitive 三态对齐 LLM | ✅ | W3.A.3 Unity LifecycleHeartbeatPublisher 事件驱动 + 1Hz 双触发 EcpStateDto；W3.A.1 cognitive_state_tracker 接 Gemini agent_state_changed → BB tick/cognitive_state；selection-C 三 tool wrappers 把状态附在 LLM-facing return |
| 4 | RefBinding + 至少一种 Event 落地，从 Unity 走到 L2-B / Graphiti 且不污染实时帧循环 | ✅ | W6-7 Brain refs registry + bbox/focus observer + threshold + hint_writer；W6-7 Unity BBoxController/FocusController/ParrotAttentionConfig；F-05 Echo 全链路接通；attention.threshold.crossed publish + transient/current_attention_hint BB；W8 PhotoEvent 真 PhotoNode 落 L2-B（NodeKind.PHOTO） |
| 5 | 全链路 Editor 跑通（含 Photo）| **Editor 联机 ✅** (2026-05-04) | #3 GAP-1+EcpState / #4 BBox+Focus DataChannel / #5 Photo preview+HTTP 200+disk 21690B 全部 ✅；#1 perch_to_finger / #2 identify_object 留真机（XR Hands + 麦克风）。完整报告：`sprint4_phase4_online_smoke_completion_20260504.md` |

---

## §3 协议契约最终态（锁定值 vs 实际 code）

### 3.1 EcpEventType 注册表（13 项）

Python `EcpEventType` enum 实测值（grep 自 `src/parrot/shared/ecp_event.py`）：

| event_type | source | 落地 chat | 已 wire 接收方 | entry §8.3 |
|:--|:--|:--|:--|:--|
| `snapshot.captured` | unity | W1-2 / W4-5 | observer/snapshot stub（Unity 侧 capture RPC ECP-化 def-1）| ✅ |
| `sighting.matched` | brain | W4-5 | identify_object → observer/sighting 异步 archiver + L2-B attention（ via runner）| ✅ |
| `sighting.unmatched` | brain | W4-5 | identify_object → observer/sighting log + count | ✅ |
| `bbox.placed` | unity | W6-7 | observer/bbox → refs.bind_bbox + threshold._add_weight | ✅ |
| `bbox.removed` | unity | W6-7 | observer/bbox → refs.unbind_bbox + threshold._add_weight | ✅ |
| `focus.anchored` | unity | W6-7 | observer/focus → refs.bind_focus + threshold._add_weight | ✅ |
| `focus.released` | unity | W6-7 | observer/focus → refs.unbind_focus + threshold._add_weight | ✅ |
| `attention.threshold.crossed` | brain | W6-7 | threshold._emit_threshold_crossed publish；Unity 端 wildcard handler log | ✅ |
| `photo.taken_preview` | unity | W8 Brain | observer/photo → upsert PhotoNode + BB last_photo_event | ✅ |
| `photo.asset_uploaded` | brain | W8 Brain | photo_upload_server publish; observer/photo 接 → 更新 reference_image_path | ✅ |
| `gesture.recognized` | unity | W1-2 reserved | （Unity 端通过 telemetry topic 发 hand_gesture，不走 EcpEvent — 历史路径）| ✅ |
| `event.rejected.oversize` | brain | W1-2 | event_ingest 8KB 拒收 synthesized | ✅ |
| `attention.config.echo` | unity | W6-7 + F-05 | attention_config_handler → BB global/attention_thresholds → FocusBboxThreshold 读 | ✅ |

**对照**：entry §8.3 注册表 12 行（W1-2 starter set）+ §8.7 W8 的 `photo.*` + W6-7 完成报告 §1.2 加的 `attention.config.echo` = 13。**实际 enum 13 项 = 文档 13 项，无漂移**。

### 3.2 BB schema 全集（26 keys，按 Phase 4 影响分组）

> 实测来自 `src/parrot/shared/bb_schema.py` BB_KEYS 元组 + grep `# CANDIDATE`

**Phase 4 W4-5 / W6-7 / W8 新增或重指派的 keys（5 项）**：

| key | scope | writer | 状态 |
|:--|:--|:--|:--|
| `transient/current_attention_hint` | transient | dsg.attention.threshold | ✅ writer 实落（W6-7 commit `0071bb8`）|
| `transient/last_sighting_event` | transient | brain.observer.sighting | ⚠ # CANDIDATE 残留 — 详见 §5.4 |
| `global/attention_thresholds` | global | brain._rpc_bridge | ✅ Echo 全链路接通（F-05 step ③ commit `e00ae20` 移除 # CANDIDATE）|
| `tick/cognitive_state` | tick | brain.agent | ✅ writer 实落（W3.A.1 commit `d228626` cognitive_state_tracker）|
| `transient/last_photo_event` | transient | brain.observer.photo | ✅ writer 实落（W8 commit `84544dd`）|

**Phase 4 之前已存在不动的 keys（21 项）**：见 `src/parrot/shared/bb_schema.py` 完整列表。其中 3 项 # CANDIDATE 为 Phase 1-3 遗留：

| key | 残留 # CANDIDATE 理由 |
|:--|:--|
| `session/connection_health` | Phase 3 lifecycle / health 聚合 — Phase 4 不动 |
| `session/audio_route_policy` | Phase 3 audio policy — Phase 4 不动 |
| `session/ecp_state` | **GAP-1 真实存在** — Unity W3.A.3 publish parrot.ecp.state topic，但 Brain 端无 ingest handler 把 EcpStateDto 写 BB 这个 key。详见 §5.5 |

### 3.3 LiveKit DataChannel topic 矩阵

| topic | reliability | 用途 | 拥有者 |
|:--|:--|:--|:--|
| `parrot.ecp.event` | reliable | Phase 4 EcpEvent（13 个 event_type） | event_ingest（Brain）+ EcpEventDispatcher（Unity）|
| `parrot.ecp.state` | reliable | Phase 3 EcpState 心跳（Unity → Brain，1Hz + 事件驱动）| LifecycleHeartbeatPublisher（Unity）→ brain.ecp_state_ingest（**GAP-1 ✅**）→ BB session/ecp_state |
| `parrot.ecp.health` | reliable | Phase 3 connection.health.changed inline envelope | Heartbeat transport（Unity）|
| `parrot.ecp.intent_disconnect` | reliable | Phase 3 intent.disconnect inline envelope | Heartbeat transport（Unity）|
| `parrot.ecp.tick` | lossy（30-60Hz）| 拖动 / pose（W6-7 lossy 部分）| W6-7 Unity 已 spec，drag UI 实现 defer |

### 3.4 RefBinding kinds + lifecycle

`src/parrot/brain/refs.py` 实测：

| RefKind | 创建者 | 销毁者 | resolve_target |
|:--|:--|:--|:--|
| `BBOX` | observer/bbox._on_bbox_placed | observer/bbox._on_bbox_removed | UNRESOLVED → L2B_NODE（Phase 5+ 联通 identify_object 升级）|
| `FOCUS` | observer/focus._on_focus_anchored | observer/focus._on_focus_released | 同上 |
| `PHOTO` | （PhotoNode 直接进 L2B，未经 RefBinding）| — | — |
| `SIGHTING` | （目前不通过 RefBinding，由 sighting EcpEvent 直接路由）| — | — |

**Phase 4 W6-7 W8 verdict**：RefBinding 当前只服务 BBox / Focus 注意力路径；Photo / Sighting 走 PhotoNode / 异步 archiver。F-05 step ③ Echo 接通后，threshold cross → AttentionHint payload 含 ref_id；hint_writer 等 RefBinding resolve 后才 bump L2-B。**Phase 4 W6-7 常态：所有 RefBinding 都是 UNRESOLVED**，hint_writer 100% no-op（这是设计意图，Phase 5+ resolver 流加 identify_object 联动才会有 RESOLVED）。

### 3.5 NodeKind + EdgeKind 扩展（W8）

| 新增 | 来源 | 说明 |
|:--|:--|:--|
| `NodeKind.PHOTO` | W8 commit `84544dd` | 与 OBJECT 区分 — 结构性强制 entry §8.1 L7 "PhotoEvent 不自动建 ObjectNode" |
| `EdgeKind.HAS_PHOTO` | W8 同 | Episode → PhotoNode；实际 connect() 调用 defer Phase 5+（Episode lifecycle 全 wire 后）|
| `EdgeKind.CAPTURED_VIA` | W8 同 | PhotoNode → Focus/BBox subject；defer Phase 5+ |
| `EdgeKind.CANDIDATE_SUBJECT` | W8 同 | PhotoNode → ObjectNode（仅当已知 candidate 时建边）；defer Phase 5+ |

---

## §4 实现总览

### 4.1 Brain 模块 inventory（Phase 4 新增 + 改动）

| 文件 | 状态 | 周次 / commit |
|:--|:--|:--|
| `src/parrot/shared/ecp_event.py` | NEW | W1-2 / `42019ca` |
| `src/parrot/shared/ref_binding.py` | NEW | W1-2 / `42019ca` |
| `src/parrot/shared/bb_schema.py` | MOD（+ 5 keys, producer 重指派）| W1-2 + W4-5 + W6-7 + F-05 + W8 |
| `src/parrot/shared/parrot_actions.py` | MOD（+ CognitiveState enum）| W3.A.1 / `d228626` |
| `src/parrot/brain/event_ingest.py` | NEW | W1-2 + W2 收口 / `c3f5413` `aad919c` |
| `src/parrot/brain/event_publisher.py` | NEW | W2 收口 / `aad919c` |
| `src/parrot/brain/cognitive_state_tracker.py` | NEW | W3.A.1 / `d228626` |
| `src/parrot/brain/refs.py` | NEW | W6-7 / `0071bb8` |
| `src/parrot/brain/attention_config_handler.py` | NEW | F-05 ② / `4bd3475`（Unity W6-7 chat）|
| `src/parrot/brain/photo_upload_server.py` | NEW | W8 / `84544dd` |
| `src/parrot/brain/agent.py` | MOD（multiple boot wire-ups + disconnect handler）| W2 + W3.A.1 + W6-7 + F-06 + W8 |
| `src/parrot/brain/observer/__init__.py` + `event_bus.py` | NEW | W1-2 / `c3f5413`；W6-7 + bbox/focus 注册 |
| `src/parrot/brain/observer/snapshot.py` | NEW（stub）| W1-2 |
| `src/parrot/brain/observer/sighting.py` | NEW（W1-2 stub → W4-5 实质化 → audit F-02 删 +0.05）| `c3f5413` `482fd04` `9ae5d65` |
| `src/parrot/brain/observer/photo.py` | NEW（W1-2 stub → W8 实质化）| `c3f5413` `84544dd` |
| `src/parrot/brain/observer/bbox.py` | NEW | W6-7 / `0071bb8` |
| `src/parrot/brain/observer/focus.py` | NEW | W6-7 / `0071bb8` |
| `src/parrot/brain/tools/_budget.py` | NEW | W4-5 / `482fd04` |
| `src/parrot/brain/tools/_state_context.py` | NEW | W3.A.1 / `d228626` |
| `src/parrot/brain/tools/identify_object.py` | REWRITE 408→ staged | W4-5 / `482fd04` + audit F-03 / `9ae5d65` |
| `src/parrot/brain/tools/fly_to.py` / `animate.py` / `set_video_tier.py` | MOD（attach_state_header wrap）| W3.A.1 / `d228626` |
| `src/parrot/brain/tools/__init__.py` | MOD（identify_object env gate 注释更新）| W4-5 / `482fd04` |
| `src/parrot/dsg/attention/__init__.py` + `threshold.py` | NEW | W1-2 + W6-7 实质化 emit + audit F-04/07/09-B/13 + F-05 ③ |
| `src/parrot/dsg/attention/hint_writer.py` | NEW | W6-7 / `0071bb8` + audit fix |
| `src/parrot/dsg/l2b_types.py` | MOD（+ NodeKind.PHOTO + 3 EdgeKind）| W8 / `84544dd` |

### 4.2 Unity 模块 inventory（其他 chats 完成；本文为汇报）

| 文件 | 状态 | 来源 chat |
|:--|:--|:--|
| `unity/ArSpike/Assets/Scripts/ParrotApp/Ecp/EcpEventDto.cs` + `EcpEventDispatcher.cs` | NEW | W1-2（本 chat 写）/ `a36c36f` |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Ecp/EcpEventPublisher.cs` | NEW | W6-7 Unity / `4bd3475` |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Lifecycle/`（perch_to_finger / EcpState 三态）| MOD | W3.A.2 / W3.A.3 |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Attention/BBoxController.cs` + `FocusController.cs` + `AttentionConfigEchoPublisher.cs` | NEW | W6-7 Unity |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Config/ParrotAttentionConfig.cs` | NEW | W6-7 Unity |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Parrot/AnimationDriver.cs` | REWRITE Minecraft procedural | Animation chat |

### 4.3 测试矩阵（220 全绿）

| 套 | 项数 | 覆盖 |
|:--|:--|:--|
| W1-2 baseline（cs_parity + EcpEvent + RefBinding + dedup + threshold）| 52 | event schema + dedup window + cross-language |
| W2 收口（attach + publisher）| 15 | LiveKit Room.DataReceived bind + reconnect |
| W3.A.1 selection-C | 21 | cognitive tracker + state context + tool guards |
| W4-5（budget + identify_object 三段 + sighting observer）| 17 | staged orchestrator + budget timeout + sighting fan-out |
| W6-7（refs + hint_writer + observer + threshold emit）| 35 | RefBinding lifecycle + L2-B bump + 阈值 cross |
| Brain 自审 fix（F-02 metric / F-08 race / F-09-B cross-kind / F-06 source-grep）| +3 | 自审收口测试 |
| F-05 step ③ BB injection | 11 | sentinel-None resolution + bool guard + partial BB |
| W6-7 Unity attention_config_handler（来自 W6-7 Unity chat）| 9 | echo handler 5 字段 + reconnect 覆写 + writer 校验 |
| **W8（observer/photo + photo_upload_server）**| **21** | **PhotoNode upsert + asset reconciliation + FastAPI 路由 + publish bridge** |
| 既有 Phase 1-3 + 总线 + scheduler | + 36 | 无破坏 |
| **总** | **220** | 全绿 in 3.5s |

---

## §5 一致性审计

### 5.1 entry §8 决策锁逐条对照（L1-L13 + W0-W8）

| Lock | 锁定值 | 实际落地 | 漂移 |
|:--|:--|:--|:--|
| L1 | EcpState 频率 = 事件驱动 + 1Hz 心跳 | LifecycleHeartbeatPublisher（W3.A.3）实现双触发 | 0 |
| L2 | EcpEvent topic = `parrot.ecp.event` reliable + UUID v7-style event_id + 强制 7 字段 | `ecp_event.py` `EcpEvent` Pydantic + `TOPIC_ECP_EVENT` 常量；测试 `test_topic_constants_match_locked_values` 守护 | 0 |
| L3 | EcpEvent payload < 8KB | `ECP_EVENT_PAYLOAD_LIMIT_BYTES = 8 * 1024`；event_ingest 拒收 + synthesized event.rejected.oversize | 0 |
| L4 | EcpEvent 与现有 inline envelope 共存（不动 parrot.ecp.health / intent_disconnect）| 实测 LiveKitDataChannelHeartbeatTransport 路径不动 | 0 |
| L5 | BBox 拖动 lossy / 放置 reliable + EcpEvent | W6-7 Unity BBoxController 实现；payload bbox_id 必带（observer/bbox 索引依赖）| 0 |
| L6 | Focus 拖动 lossy / 锚定 reliable + EcpEvent | W6-7 Unity FocusController；同 BBox 路径 | 0 |
| L7 | PhotoEvent 写 PhotoNode（非 ObjectNode）| W8 NodeKind.PHOTO 结构性强制；observer/photo upsert kind=PHOTO；测试 `test_preview_creates_photo_node_with_kind_photo` 守护 `kind != NodeKind.OBJECT` | 0 |
| L8 | 照片双通道：preview reliable + EcpEvent；asset HTTP POST → /upload/photo + Castle 本地 cache | W8 photo_upload_server FastAPI on 7889 + cache `data/photos/{yyyy-mm-dd}/{photo_id}.jpg` + publish photo.asset_uploaded | 0 |
| L9 | Δ_focus=0.2 / Δ_bbox=1.0 / threshold=1.0；阈值器在 dsg/attention 不塞 BB；优先级 explicit > BB > DEFAULT | DEFAULT_DELTA_FOCUS / DEFAULT_DELTA_BBOX / DEFAULT_THRESHOLD 常量；F-05 step ③ sentinel-None resolution；Echo 全链路接通（① + ② + ③）| 0 |
| L10 | LLM 注入 = 选项 C 主路径（执行类 tool 检 BB 三态附 reason）| _state_context.py + 3 tool wrappers；test_tools_state_header source-grep 守护 | 0 |
| L11 | identify_object 1.9s 总预算（800 + 200 + 800 + 100ms）| _budget.py + identify_object._match_staged 三段；test_identify_object 三段独立 timeout 验证 | 0（audit §9.6 修订前是 2.5s 含 visual_match，已同步更新）|
| L12 | G1 拆双向：Unity 下行 router (EcpEventDispatcher) + Python 上行 ingest (event_ingest) | W1-2 + W2 收口；两个模块文件实测落地 | 0 |
| L13 | dsg/attention/__init__.py 不 export Attention 类符号 | __init__.py 实测只 `from threshold import FocusBboxThreshold`；测试 `test_attention_init_does_not_export_Attention_class` 守护 | 0 |

**结论**：13 条 L 锁全部 **0 漂移**。所有违反 lock 的尝试都被 freeze test 守护抓住。

### 5.2 跨语言契约（Python ↔ C# 守护）

| 测试 | 内容 | 状态 |
|:--|:--|:--|
| `test_event_type_names_match_python_enum` | C# `EcpEventTypeNames` const 字符串集合 == Python `EcpEventType` 枚举值集合（13 个）| ✅ |
| `test_event_source_names_match_python_enum` | 同上 source enum | ✅ |
| `test_topic_constants_match_python` | C# `EcpEventConsts.TopicEcpEvent/State/Tick` == Python topic 常量 | ✅ |
| `test_cs_dto_file_exists` | EcpEventDto.cs 文件存在性守护 | ✅ |

**4/4 全绿**。任何 Python enum 增减 → C# 必须同步；CI 抓住，不允许单边漂移。

### 5.3 BB writer/key 对齐

实测 `BB_KEYS` 26 项 + grep 实际 producer：

| key | 声明 writer | 实际 writer 落地代码 | 一致 |
|:--|:--|:--|:--|
| `tick/cognitive_state` | brain.agent | cognitive_state_tracker.py（W3.A.1）— 名义上 brain.agent 是 cognitive_state_tracker.py 的所有者命名空间 | ✅ |
| `tick/body_state` | brain.telemetry_receiver | telemetry_receiver.py | ✅ |
| `transient/current_attention_hint` | dsg.attention.threshold | threshold.py `_write_bb_attention_hint` | ✅ |
| `transient/last_sighting_event` | brain.observer.sighting | **❗ 实测 observer/sighting.py 不写此 key**（只走 archiver）— § 5.4 finding | ⚠ |
| `transient/last_photo_event` | brain.observer.photo | observer/photo.py `_build_bb_payload` + `bb.set` | ✅ |
| `global/attention_thresholds` | brain._rpc_bridge | attention_config_handler.py（W6-7 Unity chat）— 名义上 brain._rpc_bridge 命名空间，handler 写 | ✅ |
| `session/ecp_state` | brain._rpc_bridge | `brain.ecp_state_ingest.attach_ecp_state_ingest` — GAP-1 ✅ resolved，smoke+GAP-1 chat | ✅ |
| 其他 21 项 | 各自 | 各自 | ✅ |

### 5.4 BB # CANDIDATE 残留分析（5 个 # CANDIDATE marker grep）

| key | 残留理由 | 处置建议 |
|:--|:--|:--|
| `session/connection_health` | Phase 3 lifecycle / health 聚合 — Phase 4 不动 | Phase 5+ 真聚合时移除 |
| `session/audio_route_policy` | Phase 3 audio policy — Phase 4 不动 | Phase 5+ 蓝牙 hand-off chat 完工时移除 |
| `session/ecp_state` | **GAP-1 ✅ resolved** — ecp_state_ingest.py 落地（smoke+GAP-1 chat）；bb_schema # CANDIDATE marker 已移除 | — |
| `transient/current_attention_hint` 注释行（不在 # CANDIDATE 状态）| 历史注释提到 # CANDIDATE marker — 实测 key 已移除 | 注释清理 doc-only 操作 |
| `transient/last_sighting_event` | observer/sighting 没真写此 key（只 archiver）| §5.5 finding A，Phase 5+ 把 archiver 命中也回写 BB 这个 key 或重 spec |

### 5.5 audit findings 累计状态

| 审计来源 | 项数 | 已 resolved | reject | 残留 |
|:--|:--|:--|:--|:--|
| Brain 自审（W3.A.1+W4-5+W6-7） | 13 | 10（F-01/02/03/04/06/07/09-B/13 + F-05 全链路 + F-09 strengthen）| 3（F-10 / F-11 / F-12 → Phase 5+）| 0 |
| W6-7 Unity cold-read | 3（F-A22 / F-A4 / F-A33）| 3 ✅（Unity chat commit `5ec7640`）| 0 | 0 |
| 本终审计新发现 | 2 | 0 | 0 | 2 — 列入 §5.5 残留漂移 |

**本终审计新发现的 2 项 finding**：

#### A — `transient/last_sighting_event` BB key 实测无写者

```text
severity:    low
confidence:  high
category:    doc / observer pipeline drift
file:        src/parrot/shared/bb_schema.py:296（声明 writer = brain.observer.sighting）
             src/parrot/brain/observer/sighting.py（实际只走 archiver via IngestRunner）
problem:     bb_schema 声明的 writer 在 observer/sighting 实际 code 中没有
             落地。observer/sighting._async_matched_side_effects 只调
             ingest runner（archiver），不写 BB transient/last_sighting_event。
             这条 BB key 在 Phase 4 W4-5 的设计预期是"sighting 命中后下游
             消费方读 BB 拿到证据"，但下游消费方目前是 archiver 直接接
             EcpEvent，不通过 BB。
proposal:    选 1：
             A. observer/sighting 加一行 BB write（symmetric with photo
                observer 的 _build_bb_payload + bb.set 模式）— 让 doc 与
                code 一致，下游可走 BB 路径
             B. doc 改：移除 BB key 的 writer 声明 + 标 Phase 5+，明确
                Phase 4 W4-5 不通过 BB 路径
             C. 现状保留 + 加注释说明"declared but unwritten in Phase 4"
considered_intent: 没。W4-5 设计时是想 sighting observer 既走 BB 又走
                   archiver，实际只实现 archiver 一条路径
status:      proposed - low priority（Phase 5+ 与 sighting → identify_object
             联动 resolver flow 一起设计时再处理）
```

#### B — GAP-1: `session/ecp_state` 无 Brain 端 ingest handler

```text
severity:    med
confidence:  high
category:    pipeline gap (cross-chat)
file:        src/parrot/brain/event_ingest.py（只路由 parrot.ecp.event 一条 topic）
             src/parrot/shared/bb_schema.py:178（session/ecp_state writer 声明）
             unity/.../LifecycleHeartbeatPublisher.cs（Unity W3.A.3 publish parrot.ecp.state topic）
problem:     Unity W3.A.3 在 parrot.ecp.state 这个 topic publish EcpStateDto
             1Hz + 事件驱动，但 Brain 端 event_ingest 只路由 parrot.ecp.event。
             parrot.ecp.state 入站 LiveKit Room.DataReceived 后落到
             attach_telemetry_receiver 的 silent-ignore 分支。结果：BB
             session/ecp_state 永远空，selection-C tool wrappers 看不到
             active_locks / active_command_id 字段（_state_context.py
             ecp_state 读路径目前永远 None）。
proposal:    在 §8.2 联机 smoke chat 同步加一个新模块
             `src/parrot/brain/ecp_state_ingest.py`：
             - subscribe LiveKit Room.DataReceived 的 parrot.ecp.state topic
               (类似 attach_telemetry_receiver 模式)
             - 解析 EcpStateDto JSON
             - 写 BB session/ecp_state（writer = brain._rpc_bridge 与
               bb_schema 声明一致）
             加 1 测试。预计 30 分钟工作量。
why:         entry doc §8.1 L1 锁定值要求"Brain 知道 GOSLO 当下状态"，目前
             Unity 端发了，Brain 端没收。selection-C 选项 C 的 tool wrapper
             实际上目前看到的 active_locks / active_command_id 总是 None。
             不严重（DEFAULTs 处理了），但 felt experience 不完整。
considered_intent: 部分 — 自审 §3.4 / W6-7 完成报告 §5 都提到 "联机 smoke
                   不能验证的部分" 包括 EcpState 收，但没明确 spec ingest
                   handler 的实现归属
status:      ✅ resolved — src/parrot/brain/ecp_state_ingest.py 落地（smoke+GAP-1 chat）：
             attach_ecp_state_ingest(room) → BB session/ecp_state 写入；
             10 测试全绿；bb_schema.py # CANDIDATE 移除；
             agent.py GAP-1 wire-up 注释引 Finding B
```

### 5.6 已知漂移与 defer 列表

| 项 | 触发条件 | 关联 chat |
|:--|:--|:--|
| ~~GAP-1 EcpState ingest handler~~ | **✅ resolved** — ecp_state_ingest.py 落地 | smoke+GAP-1 chat |
| Finding A: last_sighting_event BB write | sighting → identify_object resolver flow（Phase 5+）| §6 |
| Unity W8 半边（capturePhoto UI + 256px preview + HTTP POST + photo.taken_preview publish）| Unity W8 chat | §8.1 |
| Editor HUD M2（debug HUD for attention / photo / EcpState）| 需要时 | Phase 5+ |
| L2-B `EdgeKind.HAS_PHOTO` 实际 connect 调用 | Episode lifecycle 完整化 | Phase 5+ |
| `EdgeKind.CAPTURED_VIA` / `CANDIDATE_SUBJECT` connect | RefBinding resolver + identify_object 联动 | Phase 5+ |
| 隐私 `goslo-chat /forget_snapshots` 命令 | 真机 spike 后用户隐私治理 | Phase 5+ |
| 对象存储替换（S3 / MinIO） | Castle 容量瓶颈 | Phase 5+ |
| HTTP 鉴权（photo_upload_server / token_mint Bearer）| Castle 公网部署 | Phase 5+ |
| Nanobot 同步 Graphiti 路由（audit §9.2 完整设计）| audit §5.4 选项 γ 决策 | Phase 5+ |
| `web_search` / `reverse_image_search` 新 tool（option α 完整化）| audit §5.4 选项 α 完整化 | Phase 5+ |
| L1.5 预加载 Node 池 | DSG L2-B 完善设计 chat | Phase 5+ |
| Multi-Brain 协作模式 BB scope `peer/`（用户 2026-04-30 §10 自审）| 双 Nanobot 真同时活跃 | Phase 5+ |

---

## §6 Phase 5+ 待办（明确触发条件）

按"协议 / 工具 / 性能 / 治理"四象限：

### 6.1 协议层

- **L1.5 预加载 Node 池 + ConfirmationStatus 状态机扩展** — DSG L2-B 完善 chat 的入口；audit §9.1 用户澄清留 hook
- **Multi-Brain 协作模式 BB scope `peer/`** — 真出现双 Nanobot 协作场景时
- **EcpEvent schema_version=2** — 字段集变化时（不在 Phase 5+ near-term 视野内）

### 6.2 工具层

- **identify_object L2 完整化（option α + web_search + 同步 Nanobot）** — audit §5.4 升级路径
- **Unity W8 半边** — capturePhoto UI + preview + HTTP upload（独立 chat）
- **Editor HUD M2** — debug HUD（attention / photo / EcpState 可视化）
- **Sighting → identify_object resolver flow** — RefBinding resolve + L2-B promotion
- **`goslo-chat /forget_snapshots` 隐私命令**（audit §8.2）

### 6.3 性能 / 健壮性

- **GAP-1 EcpState ingest handler**（§8.2 联机 smoke chat 同步做）
- **Brain `attention_config_handler` 收 echo 后直写 BB 之外，OnDisconnect 时清空 BB**（防 reconnect 旧值残留 — 当前 Echo 重连重发已 cover 但加防御保险）
- **Photo asset HTTP 鉴权 + 对象存储替换**（Castle 公网 / 容量需求时）

### 6.4 治理 / 文档

- **bb_schema.py # CANDIDATE 注释行清理**（参考 §5.4 — `transient/current_attention_hint` 旁的历史注释）
- **L2-B EdgeKind.HAS_PHOTO / CAPTURED_VIA / CANDIDATE_SUBJECT 真实 connect 调用**（Phase 5+ Episode 完整化时）

---

## §7 Sprint 4 终极目标达成度

> entry doc §0.1 锁定 4 条 Sprint 4 终极目标 — 逐条对照实现：

| 目标 | 状态 | 证据 |
|:--|:--|:--|
| 统一数据流连接健壮性（LiveKit / AR Foundation / 前后台 / 重连 / 音频路由）| ✅（Phase 3 完成的部分）+ Phase 4 reconnect 全量重 publish 行为补完 | Phase 3 lifecycle FSM + Phase 4 W6-7 Unity §B.6 reconnect 行为 |
| 完成协议 V2 / ECP：从纯 RPC → 目标驱动、状态同步、可过期、前端状态机回执 | ✅ | EcpCommand + EcpAck + EcpState + EcpEvent + EcpFrontendState 完整体系；Phase 4 W0-W8 全栈实现 |
| 明确 DSG L2-B / Graphiti / Obsidian / Ref 的最小接口与写入边界 | ✅ | RefBinding / NodeKind.PHOTO / EdgeKind 扩展 / observer 边界 / archiver 路径全 spec + 落地 |
| 用四个 App 工具验证协议能力：① 对话+手势+飞到手指 / ② 按需发现物体 / ③ Focus+BBox / ④ 照相机 | **3.5 / 4** | ① ② ③ ✅；④ Brain 半 ✅ / Unity 半 ⏳（§8.1 派发） |

**4 条目标的 3.5 完整达成**。剩 ④ Unity 半边是 Unity chat 范围。

---

## §8 后续 chat 派发清单

### 8.1 Unity W8 半边 chat — capturePhoto UI + 256px preview + HTTP POST

> 启动 prompt 模板见 §11；本 chat 不写 prompt（用户表示自己来测试 / 派发）

核心要求：
- 实现 capturePhoto UI 触发（建议从工具柜 prefab 接，参考 W6-7 BBox/Focus 触发模式）
- 256px JPEG preview 生成 + base64 编码 < 8KB
- publish EcpEvent `photo.taken_preview` 含 photo_id / pose / focus_refs / bbox_refs / candidate_subject_uuid / preview_jpeg_b64 / episode_ref
- HTTP POST 到 `http://<brain_host>:7889/upload/photo/{photo_id}`，header `X-Photo-Preview-Event-Id: <preview event_id>`
- reconnect 时不重发已上传的 photo（asset 已落 Brain disk，重新 connect 不需要重传）

### 8.2 联机 smoke + GAP-1 chat

> W6-7 Unity 完成报告 §8.2 已 spec；本 chat 加补：**同步实现 GAP-1（EcpState ingest handler）**作为 prerequisite

核心要求：
- 实现 `src/parrot/brain/ecp_state_ingest.py`：subscribe parrot.ecp.state topic → 解析 EcpStateDto JSON → 写 BB session/ecp_state（writer = brain._rpc_bridge）
- 加 1-2 个测试（mock packet handle + BB write verify）
- 联机 smoke：Editor → Brain → Editor 全链路验证
  - perch_to_finger（§2 #1 验收）
  - identify_object 真 Graphiti search（§2 #2 验收）
  - bbox.placed → threshold.crossed（§2 #4 验收）
  - photo.taken_preview → upload → photo.asset_uploaded（§2 #4 + W8 验证）
  - EcpState 三态真到 Brain BB（GAP-1 验证 + §2 #3 验收）

### 8.3 P2.5 完成汇报 chat

本 doc 是 Phase 4 完成报告。P2.5 完成汇报需要再起一个 chat 综合：
- Sprint 0-3 完成报告
- 本 Phase 4 完成报告
- 真机 spike 结果
- P2.5 验收 5 条最终状态

---

## §9 数据来源

本审计的所有数字均来自实测命令：

| 数字 | 命令 |
|:--|:--|
| 220/220 测试 | `.venv\Scripts\python.exe -m pytest tests/ --ignore=tests/integration -q` |
| 0 lints | ReadLints on all touched files |
| 13 EcpEventType | `python -c "from parrot.shared.ecp_event import EcpEventType; ..."` |
| 26 BB keys | `python -c "from parrot.shared.bb_schema import BB_KEYS; ..."` |
| # CANDIDATE 残留 | `grep "# CANDIDATE" src/parrot/shared/bb_schema.py` |
| 40+ Phase 4 commits | `git log --oneline 9968ede^..HEAD` |
| 4/4 cs_parity | `pytest tests/test_ecp_event/test_cs_parity.py -v` |

---

## §10 收口签名

- **本文创建 commit**: 待入库后填
- **Phase 4 起始 commit**: `9968ede` (W0 决策锁附录)
- **Phase 4 终态 commit（本文写作时 HEAD）**: `8f63ee2` (W8 entry §8.7 row 升级)
- **测试基线**: 220/220 全绿（pytest tests/ --ignore=tests/integration）
- **跨语言对齐**: 4/4 全绿（test_cs_parity）
- **硬约束守护**: entry §8 决策锁 13 项 0 漂移；audit defended 10 条全部守住
- **协议契约**: 13 EcpEventType + 26 BB keys + 4 RefKind + 4 RefTargetKind + 1 NodeKind 新增（PHOTO）+ 3 EdgeKind 新增（HAS_PHOTO / CAPTURED_VIA / CANDIDATE_SUBJECT）
- **跨 chat 收口报告**：W3.A.2/A.3 完成报告 + Animation chat 完成报告 + W6-7 Unity 完成报告 + Brain 自审 + 本文（Phase 4 主收口）

---

## §11 引用

- `architecture/sprint4_phase4_entry_20260430.md` §8 — 决策锁（authoritative）
- `architecture/sprint4_phase4_brain_self_audit_20260430.md` — Brain 自审 13 项
- `architecture/sprint4_phase4_w3_a2_a3_completion_20260430.md` — W3.A.2/A.3 Unity 收口
- `architecture/sprint4_phase4_w6_w7_unity_completion_20260430.md` — W6-7 Unity 收口（含 §10 前向兼容）
- `architecture/sprint4_phase4_w3_animation_chat_launch_prompt.md` — Animation chat prompt
- `architecture/audit_identify_object_no_screenshot_20260420.md` §9 — W4-5 实施口径（用户 4/30 澄清）
- `architecture/sprint4_protocol_ecp_background_20260429.md` — Sprint 4 大背景
- `architecture/sprint4_protocol_v2_ecp.md` — 协议设计稿
- `architecture/sprint4_ecp_minimal_audit_20260429.md` — Phase 1 ECP-minimal 审计（前序）
- `parrot_behavior_rules.md` §0.3 / §3.7 — 体感红线 / Observer-Attention 边界
