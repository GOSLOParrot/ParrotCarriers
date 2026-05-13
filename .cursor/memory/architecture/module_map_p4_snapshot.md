---
status: ratified
category: architecture-snapshot
status_note: "Sprint 4 收口 + DSG Chat 2 + GOSLO mod 之后的最新模块架构 单一清晰图。补充 module_map_p2.md（保留为 detail），本文是 quick reference snapshot。"
last_reviewed: 2026-05-07
authoritative_for: "当前架构状态的 quick reference / 部署拓扑 / 模块成熟度速查"
parent_doc: "../INDEX.md"
ai_priority: high
ai_audience: both
related:
  - "module_map_p2.md (详细模块清单 + 数据流，本文是其精简版)"
  - "bus_v4.md (三层协议 + Mermaid 拓扑)"
  - "../protocol_snapshot_p4.md (协议 SSOT)"
  - "scene.md (家族拓扑)"
---

# Module Map P4 Snapshot — 2026-05-07

> **本文用途**：单图速查当前架构形态。详细数据流 / Phase 1-3 历史看 [`module_map_p2.md`](module_map_p2.md)；协议字段看 [`../protocol_snapshot_p4.md`](../protocol_snapshot_p4.md)。

---

## §1 部署拓扑（双节点 + 同 VPC）

```
                    ┌──────────────────────────────────────────┐
                    │         移动端 (Mobile / 真机)            │
                    │  ┌────────────────────────────────────┐  │
                    │  │  Unity ArSpike (ParrotApp)         │  │
                    │  │  ─ Lifecycle (11 态 FSM)           │  │
                    │  │  ─ Ecp (Dispatcher / Publisher)    │  │
                    │  │  ─ RPC (ParrotRpcHandler)          │  │
                    │  │  ─ Photo (W8 双通道)               │  │
                    │  │  ─ Attention (BBox/Focus/Echo)     │  │
                    │  │  ─ Parrot (ModelDriver/Registry/   │  │
                    │  │            IParrotController)      │  │
                    │  └────────────────────────────────────┘  │
                    └─────────────┬────────────────────────────┘
                                  │ WebRTC + LiveKit (5 topic + RPC + Track)
                                  │ HTTPS POST /upload/photo
                                  ▼
        ┌────────────────────────────────────────────────────────────┐
        │     Castle 常驻 (Tokyo ECS, 2C8G) — 同 VPC East-West        │
        │  ┌────────────────────────────────────────────────────┐    │
        │  │  LiveKit Server (Room "parrot-main")               │    │
        │  │  ↕ Track / RPC / DataChannel routing               │    │
        │  └─────────────────────┬──────────────────────────────┘    │
        │                        │                                    │
        │  ┌─────────────────────▼──────────────────────────────┐    │
        │  │  Brain Agent (Python) — LineA / LineB env-gate     │    │
        │  │   ├─ tools/ (10 function tools)                     │    │
        │  │   ├─ observer/ (5 observer + event_bus)             │    │
        │  │   ├─ intent_workspace + plan/ (Plan-and-Execute)    │    │
        │  │   ├─ refs + cognitive_state_tracker                 │    │
        │  │   ├─ photo_upload_server (FastAPI on 7889)          │    │
        │  │   └─ attach_* helpers (13 attach 函数)              │    │
        │  └────┬───────────────────────────────────────┬───────┘    │
        │       │                                       │            │
        │       │ in-process function call             │ Redis      │
        │       ▼                                       ▼            │
        │  ┌────────────────────┐            ┌──────────────────┐    │
        │  │  DSG (耦合层)       │            │  Scheduler       │    │
        │  │  ├─ l1_5/ Pool     │            │  ├─ py-trees BT  │    │
        │  │  ├─ l2b/ Graph     │            │  ├─ Blackboard   │    │
        │  │  ├─ triggers/ ×9   │            │  └─ Locks (mgr)  │    │
        │  │  ├─ archive/ 3-Phase│           └────────┬─────────┘    │
        │  │  ├─ ingest/ Runner │                     │ Redis Stream │
        │  │  └─ attention/     │                     ▼              │
        │  │     (Phase 4 临时) │            ┌──────────────────┐    │
        │  └────────────────────┘            │  Nanobot Worker  │    │
        │       │                            │  (HKUDS fork)    │    │
        │       │ Bolt :7687                  └──────────────────┘    │
        │       ▼                                                     │
        │  ┌────────────────────┐                                     │
        │  │  Memory (Graphiti  │            ┌──────────────────┐    │
        │  │  + FalkorDB)       │            │  Redis           │    │
        │  │  5 group_id 分区    │            │  BB / PubSub /   │    │
        │  └────────────────────┘            │  Stream / HASH   │    │
        │                                    └──────────────────┘    │
        └─────────────────────────────────────────┬───────────────────┘
                                                  │ Redis Channel (Phase 5+ 触发)
                                                  ▼
        ┌────────────────────────────────────────────────────────────┐
        │     Mecha 按需 (A10 抢占式 GPU)  — Phase 5+ 接入            │
        │  ┌──────────────────────────────────────────────────┐      │
        │  │  L1 视觉管线 (SAM2 + YOLO-World + DINOv2 ReID)    │      │
        │  │  ─ ConceptGraph SKILL 蒸馏入口                   │      │
        │  │  当前：placeholder；A10 接入 chat 启动           │      │
        │  └──────────────────────────────────────────────────┘      │
        └────────────────────────────────────────────────────────────┘
```

---

## §2 模块清单 + 状态（2026-05-07）

| 模块 | 位置 | 状态 | 主源 |
|:--|:--|:--|:--|
| **Castle 常驻** | | | |
| `bus/` | Castle | ✅ ratified（Sprint 0/1）| 注册 / 心跳 / 挂载 |
| `bus/nanobot_consumer.py` | Castle | ⚠️ ratified（4-A 增强：心跳 HSET 写者）| NEED-P2.5-NANOBOT-HEARTBEAT |
| `brain/agent.py` | Castle | ✅ ratified（LineA/B env-gate）| LineB 双管线 |
| `brain/tools/` | Castle | ✅ ratified（10 tools）| brain_tools_inventory |
| `brain/tools/identify_object.py` | Castle | ⚠️ **experimental**（W4-5 1.9s 实施口径） | Phase 4 §8 L11 |
| `brain/tools/_state_context.py` | Castle | ⚠️ **experimental**（Phase 4 选项 C 主路径） | Phase 4 §8 L10 |
| `brain/observer/` | Castle | ✅ ratified（5 observer）| Phase 4 W1-2 + W6-7 + W8 |
| `brain/event_ingest.py` | Castle | ✅ ratified | Phase 4 W2 |
| `brain/event_publisher.py` | Castle | ✅ ratified | Phase 4 W2 |
| `brain/ecp_state_ingest.py` | Castle | ✅ ratified（GAP-1 fix）| Phase 4 联机 smoke |
| `brain/refs.py` | Castle | ✅ ratified | Phase 4 W6-7 |
| `brain/cognitive_state_tracker.py` | Castle | ✅ ratified | Phase 4 W3.A.1 |
| `brain/attention_config_handler.py` | Castle | ✅ ratified（F-05 Echo 全链路） | Phase 4 W6-7 |
| `brain/photo_upload_server.py` | Castle | ✅ ratified（FastAPI on 7889）| Phase 4 W8 |
| `brain/intent_workspace.py` + `intent_workspace_backend.py` | Castle | ⚠️ ratified（4-A: DiskBackend.recover() 待补） | DSG Chat 2 + TODO(Chat4-disk-recover) |
| `brain/plan/` | Castle | ⚠️ ratified（4-A: NEED-P2.5-PLAN-INTEGRATION 5 项 plumbing） | DSG Chat 2 |
| `brain/soul.py` | Castle | ⚠️ ratified（NEED-P2.5-A persona 外置推下游） | brain B2 |
| `scheduler/` | Castle | ⚠️ ratified（4-A: 5 plan-* TODO） | py-trees BT + NEED-P2.5-PLAN-INTEGRATION |
| `dsg/l1_5/` | Castle | ✅ ratified（DSG-POOL-V1）| DSG Chat 2 |
| `dsg/l2b/` | Castle | ✅ ratified（DSG-INTENT-EVENT-V1）| DSG Chat 2 |
| `dsg/triggers/` | Castle | ✅ ratified（9 triggers + V2 alias）| DSG Chat 2 |
| `dsg/archive/` | Castle | ⚠️ ratified（4-A: NEED-P2.5-ARCHIVE-LLM 真蒸馏）| DSG Chat 2 + cross-chat-registry §3.D |
| `dsg/ingest/` | Castle | ⚠️ **experimental**（factory dispatch — Phase 4→5 transition）| ADR-L1.5-001 |
| `dsg/attention/threshold.py` | Castle | ⚠️ **experimental**（Phase 4 临时阈值器，非 L3） | Phase 4 §8 L13 |
| `dsg/l2b/attention/mechanism.py` SpreadingActivationPlaceholder | Castle | ⚠️ **experimental**（委托 BoundedBfsActivation） | TODO(P3-attention-spreading) |
| `dsg/l2b/intent_event_boundary.py` NoOpFoldStrategy | Castle | ⚠️ **experimental** | TODO(P3-fold-bionic) |
| `memory/graphiti_client.py` | Castle | ✅ ratified（5 partition） | Phase 2-3 |
| `memory/conversation_writer.py` | Castle | ✅ ratified | Phase 3 |
| `shared/ecp.py` + `ecp_event.py` + `bb_schema.py` + `ref_binding.py` + `parrot_actions.py` + `model_manifest.py` | Castle | ✅ ratified（Phase 4 §8 13 锁 + GOSLO Step 1） | wire 真源 |
| **Mobile** | | | |
| `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/` | Mobile | ✅ ratified（白模 + ECP DTO）| ECP 工作区 |
| `ParrotApp/Lifecycle/` | Mobile | ✅ ratified（11 态 + perch_to_finger）| Phase 4 W3.A.2/A.3 |
| `ParrotApp/Ecp/` | Mobile | ✅ ratified（EcpEventDispatcher / Publisher / DTOs）| Phase 4 W1-2 + W6-7 |
| `ParrotApp/Attention/` | Mobile | ✅ ratified（BBox/Focus/Echo） | Phase 4 W6-7 |
| `ParrotApp/Photo/` | Mobile | ✅ ratified（W8 双通道） | Phase 4 W8 |
| `ParrotApp/Parrot/` | Mobile | ✅ ratified（ModelDriver + Registry + GosloLegacyController） | GOSLO Step 2 |
| **Phase 5+ placeholder** | | | |
| Mecha A10 GPU Worker | Mecha | 🚧 placeholder | A10 接入 chat |
| LobeChat Bridge | — | 🚧 placeholder | needs:H3 |
| MCP Sidecar | — | 🚧 placeholder | needs:H1 |

---

## §3 三层 Bus 协议（精简）

| 层 | 技术 | 延迟 | 负载 |
|:--|:--|:--|:--|
| **L1 实时** | LiveKit Room (WebRTC) | <50ms | 音视频 / RPC / DataChannel（5 topic）|
| **L2 状态** | Redis | <5ms | BB / Pub/Sub / Stream / HASH |
| **L3 知识** | Graphiti + FalkorDB（替代 Neo4j） | <500ms | 5 group_id 分区情景记忆 |

详 [`bus_v4.md`](bus_v4.md) Mermaid 拓扑 + [`../protocol_snapshot_p4.md`](../protocol_snapshot_p4.md) 字段。

---

## §4 主数据流（3 条主路径）

### §4.1 命令路径（Brain → Unity，同步）

```
LLM tool 调用 (fly_to / animate / set_video_tier)
    ↓
brain/tools/_state_context.py (selection-C wrap，附 reason)
    ↓ EcpCommand + meta:{model_id}
brain/tools/_rpc_bridge.py
    ↓ LiveKit RPC (reliable，同步 await)
Unity ParrotRpcHandler.HandleXxx
    ↓ EcpCommand.meta.model_id
ParrotRegistry.Resolve(model_id) → IParrotController
    ↓
具体 Controller (GosloLegacyController) → AnimationDriver → 动画播放
    ↓ EcpAck (applied / rejected / timeout / no_target / unchanged)
LLM 同步话术
```

### §4.2 事件路径（Unity → Brain，异步）

```
User 操作 (BBox 拖动 / Focus 锚定 / Photo 拍摄)
    ↓
Unity Ecp/EcpEventPublisher (reliable DataChannel topic parrot.ecp.event)
    ↓ EcpEvent (13 type 之一)
brain/event_ingest.py (parse + dedup + 8KB check)
    ↓
brain/observer/event_bus.py (5 observer)
    ↓
[bbox/focus] → refs.bind → threshold._add_weight → 跨阈值 → emit attention.threshold.crossed → BB transient/current_attention_hint
[sighting]   → IngestRunner.commit_observation → L2-B SemanticNode upsert + Bucket admit + (异步 archiver to Graphiti)
[photo]      → upsert PhotoNode + BB last_photo_event；asset HTTP → photo_upload_server → publish photo.asset_uploaded
```

### §4.3 任务派发路径（Brain → Nanobot → Brain，跨进程异步）

```
LLM 调用 dispatch_task tool
    ↓ Brain → Scheduler (in-process)
scheduler/nodes.py:DispatchToNanobot
    ↓ XADD parrot.scheduler.task_queue (Redis Stream)
[Nanobot Worker XREADGROUP]
    ↓ 执行任务
[Nanobot] Pub/Sub → parrot.nanobot.results
    ↓
scheduler/service.py:_listen_nanobot_results
    ↓ ⚠️ NEED-P2.5-PLAN-INTEGRATION 4-A 主场：路由 plan_id/step_id → PlanRegistry.report_step_result
    ↓
Brain BB notification
    ↓
LLM (异步上下文) → "我查到了..."
```

---

## §5 跨语言契约（cs_parity 4/4 守护）

| 守护项 | 测试 |
|:--|:--|
| EcpEventType 13 项 | `test_event_type_names_match_python_enum` |
| EcpEventSource 3 项 | `test_event_source_names_match_python_enum` |
| Topic 常量 5 项 | `test_topic_constants_match_python` |
| C# DTO 文件存在 | `test_cs_dto_file_exists` |

任何 wire 改动 → cs_parity 必须同步过 → 否则 CI 阻断。

---

## §6 Sprint 4 收口里程碑

| 里程碑 | 状态 |
|:--|:--|
| Phase 1 ECP-minimal | ✅ 2026-04 |
| Phase 2 EcpState schema | ✅ 2026-04 |
| Phase 3 lifecycle / 防御性 | ✅ 2026-04 |
| Phase 4 W0-W8 协议 V2 + 4 工具 | ✅ 2026-04-30 |
| Phase 4 联机 smoke #3/#4/#5 | ✅ 2026-05-04（Editor）|
| Phase 4 联机 smoke #1/#2 | ⏳ defer 真机 spike |
| LineB 双管线 | ✅ 2026-05-04 |
| DSG Chat 2（L1.5 + L2-B + Plan + IntentWorkspace + Archive 8 协议）| ✅ 2026-05-06 |
| GOSLO 模块化（Manifest + IParrotController + AI CLI）| ✅ 2026-05-06 |
| Chat 4 接口提炼 | ⚠️ pivot — 转 app 实施驱动；本文 + protocol_snapshot_p4 是收口 |

---

## §7 cross-link

- 详细模块清单：[`module_map_p2.md`](module_map_p2.md)
- Mermaid 拓扑（含 Castle / Mecha / 模块详细）：[`bus_v4.md`](bus_v4.md)
- 协议 SSOT：[`../protocol_snapshot_p4.md`](../protocol_snapshot_p4.md)
- Phase 4 §8 决策锁：[`sprint4_phase4_entry_20260430.md §8`](sprint4_phase4_entry_20260430.md)
- 跨 chat 待办登记：[`cross_chat_pending_registry_20260507.md`](cross_chat_pending_registry_20260507.md)
- 行为契约：[`../parrot_behavior_rules.md`](../parrot_behavior_rules.md)
- DSG 工作区：[`dsg/workspace_index.md`](dsg/workspace_index.md)
- AR 工作区：[`ar_workspace_index.md`](ar_workspace_index.md)

---

## §8 变更日志

- **2026-05-07**：本文创建。Sprint 4 收口 + DSG Chat 2 + GOSLO mod 之后的最新模块架构 quick reference snapshot；Chat 4 接口提炼 pivot 后的收口产物。

