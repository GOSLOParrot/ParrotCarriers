---
status: ratified
category: protocol-snapshot
status_note: "Sprint 4 收口 + DSG Chat 2 + GOSLO mod 后的全协议 SSOT。Phase 1 protocol_snapshot_p1.md 是历史；本文是当前真源。任何协议变更走 ADR + bump version + cs_parity 同步。"
last_reviewed: 2026-05-07
authoritative_for: "当前所有协议字段 / enum / 通道 / 锁定值的快速速查；新会话查协议从这里入"
parent_doc: "INDEX.md"
ai_priority: high
ai_audience: both
supersedes: ["protocol_snapshot_p1.md（部分；p1 仍保留作为 Phase 1 历史）"]
related:
  - "architecture/sprint4_phase4_entry_20260430.md §8 (Phase 4 13 决策锁原文)"
  - "architecture/sprint4_phase4_completion_and_final_audit_20260430.md §3 (Phase 4 完成态详)"
  - "architecture/adr_l1_5_source_dispatch_extension_space_20260504.md (ADR-L1.5-001)"
  - "architecture/dsg/dsg_l1_5_implementation_completion_20260506.md (DSG Chat 2 收口)"
  - "architecture/goslo_model_manifest_protocol_v1.md (GOSLO 协议 v1)"
  - "architecture/lineb_implementation_completion_20260504.md (LineB 双管线)"
  - "architecture/bus_v4.md (三层协议拓扑)"
  - "parrot_behavior_rules.md (行为状态机 + 优先级链)"
  - "architecture/module_map_p4_snapshot.md (架构快照)"
---

# Protocol Snapshot P4 — 全协议 SSOT（2026-05-07）

> **本文用途**：当前所有协议契约的单一速查表。新会话查"什么 enum 有几项 / 什么 topic 走什么 / Phase 4 §8 锁了什么"全在这里。
>
> **不要在本文做协议设计** — 只快照现状。任何新协议变更走 ADR + cs_parity 同步过后再回写本文。
>
> **覆盖范围**：Phase 1-4 协议 + DSG Chat 2 + GOSLO mod + LineB 双管线。

---

## §0 全表索引

| § | 协议域 | 字段 / 项数 |
|:--:|:--|:--|
| §1 | LiveKit DataChannel 5 topic | 5 |
| §2 | EcpEvent envelope | 7+3 字段 |
| §3 | EcpEventType 注册表 | **13** |
| §4 | EcpState v1 schema | 7 字段 |
| §5 | EcpAck 11 字段 + ApplyStatus 5 态 | 11 + 5 |
| §6 | EcpCommand + meta dict | 8 字段 |
| §7 | LiveKit RPC 7 method | 7 |
| §8 | RefBinding | 4 字段 + 4 RefKind + 4 RefTargetKind |
| §9 | NodeKind / EdgeKind | 6 + 8 |
| §10 | BB schema | **26 keys** |
| §11 | ParrotAnimation / BodyState / HeadState / BehaviorMode / CognitiveState | 8 + 5 + 4 + 5 flags + 4 |
| §12 | GOSLO ModelManifest + Capability | schema |
| §13 | Photo 双通道 | preview + asset HTTP |
| §14 | HTTP endpoints | 2（/upload/photo + /mint）|
| §15 | Redis namespaces | Pub/Sub + Stream + HASH |
| §16 | Graphiti 5 group_id 分区 | 5 |
| §17 | ObservationSource | 7+1（GOSLO_AUTONOMOUS 加）|
| §18 | DSG L1.5 6 BucketKind | 6 |
| §19 | IntentWorkspace 9 StagedRefKind | 9 |
| §20 | DSG 9 触发器 + TriggerOutcome 5+2 路上行 | 9 + 7 |
| §21 | DSG attention Strategy registries | 4 接口 |
| §22 | LineB env-gate | 1 + ObservationSource 7 verbatim 锁 |
| §23 | Phase 4 §8 13 决策锁（**reference**）| 13 |
| §24 | ADR-L1.5-001 §4.1 三触发器（**reference**）| 3 |
| §25 | cs_parity 4/4 守护 | 4 |

---

## §1 LiveKit DataChannel 5 topic

> 来源：Phase 4 §8 §8.2 通道默认值最终表

| topic | reliability | 频率 | envelope | 用途 |
|:--|:--|:--|:--|:--|
| `parrot.ecp.event` | reliable | 事件驱动 | EcpEvent v1（13 event_type）| Phase 4 新增事件全部走此 |
| `parrot.ecp.state` | reliable | 1Hz + 事件驱动 | EcpStateDto v1 | Unity → Brain 状态心跳 |
| `parrot.ecp.health` | reliable | 事件 | inline envelope（**Phase 3 既有，不迁移**）| connection.health.changed |
| `parrot.ecp.intent_disconnect` | reliable | 事件 | inline envelope（**Phase 3 既有，不迁移**）| Unity 切后台 / 关 app |
| `parrot.ecp.tick` | lossy | 30-60Hz | 自由 dict（最小化）| 拖动 / pose（W6-7 BBox/Focus 拖动）|

---

## §2 EcpEvent envelope（Phase 4 §8 L2 锁）

```python
class EcpEvent:
    # 强制（7）
    event_id: str          # 'evt_<ts_ms_hex>_<rand_hex>' 时间排序格式（UUID v7-style）
    event_type: str        # EcpEventType enum value（13 项，§3）
    created_at: int        # epoch ms
    source: str            # EcpEventSource enum: "unity" | "brain" | "nanobot"（reserve）
    schema_version: int    # 当前 = 1
    payload_bytes: int     # 序列化 size（自检字段）
    payload: dict          # 自由结构（按 event_type 各自定义）

    # 可选（3）
    correlation_id: str | None    # 关联另一个 event（如 sighting.matched 关联 snapshot.captured）
    unity_identity: str | None
    room_id: str | None
```

| 约束 | 锁定值 |
|:--|:--|
| topic | `parrot.ecp.event`（reliable）|
| payload 大小 | **8 KB**（Phase 4 §8 L3）|
| 超 8KB 行为 | Brain `event_ingest` 拒收 → synthesized `event.rejected.oversize` |
| dedup 窗口 | 60s（按 event_id）|

源码真源：`src/parrot/shared/ecp_event.py`

---

## §3 EcpEventType 注册表（13 项）

| event_type | source | 触发时机 | payload 关键字段 |
|:--|:--|:--|:--|
| `snapshot.captured` | unity | captureSnapshot RPC 完成 | snapshot_uuid / captured_at / pose / command_id |
| `sighting.matched` | brain | visual_match 命中 L2-B 候选 | candidate_uuid / score / snapshot_uuid |
| `sighting.unmatched` | brain | visual_match 全 miss | snapshot_uuid / top_candidates |
| `bbox.placed` | unity | User 放置 BBox | bbox_id / corners / pose / correlation_id |
| `bbox.removed` | unity | User 移除 BBox | bbox_id / correlation_id |
| `focus.anchored` | unity | 放大镜锚定 | focus_id / center / radius / pose |
| `focus.released` | unity | 放大镜松手 | focus_id |
| `attention.threshold.crossed` | brain | 阈值器达阈值 | attention_hint_id / weight / subject_ref / correlation_id |
| `attention.config.echo` | unity | RoomManager.OnConnected（含 reconnect/管线切换）+ ContextMenu 兜底 | delta_focus / delta_bbox / threshold / target_ttl_s / schema_version=1 |
| `photo.taken_preview` | unity | capturePhoto 完成 + preview ready | photo_id / preview_jpeg_b64 (< 8KB) / pose / focus_refs / bbox_refs / candidate_subject_uuid / episode_ref |
| `photo.asset_uploaded` | brain | HTTP /upload/photo 接收完 | photo_id / asset_ref / bytes |
| `gesture.recognized` | unity | 手势检测器识别（reserve；当前走 telemetry）| gesture_kind / hand_pose / since |
| `event.rejected.oversize` | brain | event_ingest 8KB 拒收 synthesized | rejected_event_id / size_bytes / reason |

---

## §4 EcpState v1 schema（Phase 4 §8 L1 锁）

```python
class EcpStateDto:
    ts: int                 # epoch ms（dedup 基准）
    body: str               # ParrotBodyState enum value（§11）
    head: str               # HeadState enum value（§11）
    cognitive: str          # CognitiveState enum value（§11）
    active_locks: list[str] # 当前持有的资源锁（如 "body" / "voice"）
    active_command_id: str | None
    last_ack_id: str | None
```

触发：事件驱动（body/head/cognitive 任一变化、active_locks 增减、active_command_id 变化）+ 1Hz 全量心跳 fallback。

GAP-1 fix（2026-05-04）：Brain 端 `attach_ecp_state_ingest` 写 BB `session/ecp_state`。

---

## §5 EcpAck 11 字段 + ApplyStatus 5 态

```python
class EcpAck:
    command_id: str
    status: str              # ApplyStatus 5 态
    ts: int
    expires_at: int | None
    active_locks: list[str]
    active_command_id: str | None
    body_state: str
    head_state: str
    progress: float | None   # 0.0-1.0
    reason: str | None       # 失败 / unchanged 原因
    payload: dict            # 自由扩展槽
```

**ApplyStatus 5 态**（wire-locked）：

| status | 含义 | LLM 体感话术 |
|:--|:--|:--|
| `applied` | 已应用 | "我飞过去了 / 我跳了" |
| `rejected` | 拒绝（资源锁冲突 / 状态机不允许）| "现在不行，因为..." |
| `timeout` | 超时 | "我没飞过去，超时了" |
| `no_target` | 目标不存在 | "找不到目标" |
| `unchanged` | 已经是该状态 | "已经是这样了" |

通道：LiveKit RPC return value（不走 DataChannel）。

---

## §6 EcpCommand + meta dict（GOSLO Step 1 plumbing）

```python
class EcpCommand:
    command_id: str
    method: str               # "flyTo" / "animate" / etc.
    params: dict              # method-specific
    expires_at: int | None
    active_locks_required: list[str]
    meta: dict[str, Any] = {} # ⚠️ 既有自由扩展槽（Phase 1）
```

**meta key 注册表**：

| key | 用途 | 写者 | 读者 |
|:--|:--|:--|:--|
| `model_id` | Active model id（如 GOSLO_default / qfufu_v1）| Brain animate.py / fly_to.py | Unity ParrotRpcHandler → ParrotRegistry.Resolve |

C# 端：`EcpCommandMetaDto` typed mirror（GOSLO Step 2 加）。

**关键**：meta 是既有 dict 字段，**不动 wire schema 顶层字段集**；GOSLO Step 1 仅 plumbing。

---

## §7 LiveKit RPC 7 method

| method | 调用方 | 应答端 | 同步语义 | 关联 brain tool |
|:--|:--|:--|:--|:--|
| `flyTo` | Brain `_rpc_bridge` | Unity ParrotRpcHandler.HandleFlyTo | 同步（await applied/rejected/timeout）| fly_to |
| `animate` | 同 | HandleAnimate | 同步 | animate |
| `setVideoTier` | Brain / PerceptionSupervisor | HandleSetVideoTier | 同步 | set_video_tier |
| `captureSnapshot` | Brain vision/snapshot | HandleCaptureSnapshot | 同步（800ms budget per L11）| identify_object 内部 |
| `capturePhoto` | Brain `_rpc_bridge` | Unity PhotoController.CapturePhoto | 异步（preview + asset HTTP）| （无 brain tool；user 触发）|
| `dispatch_task` | Brain（实际走 Redis Stream，不走 LiveKit RPC）| Scheduler dispatch_task.py | 异步（立即返回 task_id）| dispatch_task |
| `set_mode` | Brain（实际走 BB write，不走 LiveKit RPC）| mode_watcher | 同步（BB write）| set_mode |

注：dispatch_task / set_mode 实际**不通过 LiveKit RPC**，但 Brain tool 调用语义相同。

### §7.1 ChatA app-level RPC addendum（2026-05-09）

以下是 App 菜单/启动业务 RPC，不新增 LiveKit DataChannel topic，也不新增
EcpEventType。它们跑在 LiveKit participant RPC 层，用于 Unity 与 Brain 的
应用状态协商。

| method | 调用方 | 应答端 | 同步语义 | 写入/效果 |
|:--|:--|:--|:--|:--|
| `listMenuBlocks` | Unity menu/startup | Brain `MenuRegistry` | 同步 JSON | none |
| `applyMenuSelection` | Unity menu | Brain `MenuRegistry` | 同步 JSON | `global/active_*` 5 keys |
| `applyPreset` | Unity menu/startup | Brain `PresetLoader` | 同步 JSON | same active keys |
| `saveAsPreset` | Unity menu | Brain `PresetLoader` | 同步 JSON | preset file |
| `applyWorkspace` | Unity 2DWorkspace | Brain `WorkspaceRegistry` | 同步 JSON | `global/active_workspace_id` |
| `setAppCapabilityMode` | Unity startup/lifecycle | Brain `session_policy` + `PerceptionSupervisor` | 同步 JSON | `session/app_capability_mode` + perception profile |
| `onSceneReady` | Unity scene lifecycle | Brain startup gate | 同步 JSON | readiness marker only |
| `onGosloPlaced` | Unity placement lifecycle | Brain startup gate | 同步 JSON | optional first greeting after policy gate |

Security note: each handler must treat `callerIdentity` as an audit input, not
as sufficient authorization by itself. Join-token grants remain the primary
LiveKit permission boundary.

---

## §8 RefBinding（Phase 4 §8 W6-7 锁）

```python
@dataclass(frozen=True)
class RefBinding:
    ref_id: str          # 不可变；Unity 创建时分配
    target_kind: str     # RefTargetKind enum value
    target_id: str       # 解析前 ""，解析后 = L2-B node uuid 或 obsidian path
    revision: int = 0    # 不可变迁移路径；仅在 resolve 时 +1
```

**4 RefKind**：

| RefKind | 创建者 | 销毁者 |
|:--|:--|:--|
| `BBOX` | observer/bbox._on_bbox_placed | observer/bbox._on_bbox_removed |
| `FOCUS` | observer/focus._on_focus_anchored | observer/focus._on_focus_released |
| `PHOTO` | （Phase 4：不通过 RefBinding；走 PhotoNode 直接）| — |
| `SIGHTING` | （Phase 4：不通过 RefBinding；由 sighting EcpEvent 路由）| — |

**4 RefTargetKind**：

| RefTargetKind | 含义 | resolve 触发 |
|:--|:--|:--|
| `UNRESOLVED` | 未解析（默认）| 创建时 |
| `L2B_NODE` | L2-B 语义图节点 | identify_object 命中 / user 确认 |
| `OBSIDIAN_NOTE` | Obsidian SOURCE_X note | Obsidian sync 后 |
| `EXTERNAL` | 外部 ref（URL / 文件路径）| Phase 5+ |

**Phase 4 W6-7 verdict**：所有 RefBinding 都是 UNRESOLVED；hint_writer 100% no-op（设计意图，Phase 5+ resolver 联通）。

---

## §9 NodeKind 6 + EdgeKind 8（DSG-INTENT-EVENT-V1）

**NodeKind 6**：

| NodeKind | Phase 4 强制 |
|:--|:--|
| `OBJECT` | L7：PhotoEvent **不**自动建 ObjectNode |
| `SURFACE` | — |
| `ZONE` | A10 接入后；Phase 4 reserve |
| `PERSON` | — |
| `EVENT` | Plan 主存 IntentWorkspace + L2-B 镜像 reuse `NodeKind.EVENT`，**不动 enum** |
| `PHOTO` | L7：与 OBJECT 区分；observer/photo upsert kind=PHOTO |

**EdgeKind 8**：

| EdgeKind | 用途 | Phase 4 connect 已落地? |
|:--|:--|:--|
| `LOCATED_AT` | OBJECT → SURFACE / ZONE | ✅ |
| `PART_OF` | OBJECT → OBJECT | ✅ |
| `BELONGS_TO` | OBJECT → PERSON | ✅ |
| `MENTIONED_IN` | OBJECT → EVENT | ✅ |
| `OCCURRED_IN` | EVENT → SCENE / location_tag | ✅ |
| `HAS_PHOTO` | EVENT → PHOTO | ❌ defer Phase 5+ |
| `CAPTURED_VIA` | PHOTO → FOCUS / BBOX subject | ❌ defer Phase 5+ |
| `CANDIDATE_SUBJECT` | PHOTO → OBJECT（仅当已有候选）| ❌ defer Phase 5+ |

测试守护：`test_node_kind_enum_six_values` + `test_edge_kind_enum_eight_values`。

---

## §10 BB schema 26 keys（Phase 4 完成态）

> 来源：`src/parrot/shared/bb_schema.py`

**Phase 4 W4-5 / W6-7 / W8 新增或重指派 5 项**：

| key | scope | writer | 状态 |
|:--|:--|:--|:--|
| `transient/current_attention_hint` | transient | dsg.attention.threshold | ✅ ratified |
| `transient/last_sighting_event` | transient | brain.observer.sighting | ⚠️ Finding A — 无写者（doc 与 code 漂移）|
| `global/attention_thresholds` | global | brain._rpc_bridge | ✅ ratified（F-05 Echo 全链路）|
| `tick/cognitive_state` | tick | brain.agent | ✅ ratified（W3.A.1 cognitive_state_tracker）|
| `transient/last_photo_event` | transient | brain.observer.photo | ✅ ratified（W8）|

**Phase 4 之前 21 keys**：详 `src/parrot/shared/bb_schema.py`；包括：

- `tick/body_state` (writer = brain.telemetry_receiver)
- `tick/head_state`
- `tick/last_rpc_ack`
- `session/ecp_state` (writer = brain._rpc_bridge via attach_ecp_state_ingest — GAP-1 fix)
- `session/connection_health`
- `session/audio_route_policy`
- `global/active_model_id`（GOSLO Step 1）
- `global/behavior_mode`（mode_watcher）
- `scheduler/active_tasks`
- `scheduler/last_dispatch_*`
- ...（+ 12 项）

**3 项 # CANDIDATE 残留**（Phase 1-3 历史；Phase 5+ 处置）：
- `session/connection_health` — Phase 3 lifecycle 聚合
- `session/audio_route_policy` — Phase 3 audio policy
- `transient/current_attention_hint` 注释行（实测 key 已移除）

### §10.1 ChatA BB additions（2026-05-09）

ChatA adds two app-level BB keys without changing EcpEvent/DataChannel wire
schema:

| key | scope | writer | 状态 |
|:--|:--|:--|:--|
| `global/active_workspace_id` | global | `brain.preset_loader` | 2DWorkspace active surface |
| `session/app_capability_mode` | session | `brain.session_policy` | LiveKit app capability and silent keepalive policy |

`global/active_workspace_id` belongs to the 2D UI/canvas layer. It must not be
confused with IntentWorkspace staged refs. IntentWorkspace remains the Brain
resource lifecycle layer.

---

## §11 4 行为 enum + 1 head enum

> 来源：`src/parrot/shared/parrot_actions.py` + parrot_behavior_rules §1

**ParrotAnimation 8 项（wire-locked，双重身份）**：

```
idle / fly / dance / wing_flap / perch / sit / head_bob / sleep
```

双重身份：**Brain LLM 词汇表** + **Parrot Reflex 触发条件**（`RESERVED_PARROT_CAPABILITY_IDS`）。

**ParrotBodyState 6 项（wire-locked，互斥）**：

| 状态 | 描述 | 可被打断 |
|:--|:--|:--|
| `IDLE` | 空闲 | 任何状态 |
| `FLYING` | 飞行 | 仅 FREEZE |
| `PERCHING` | 落地过渡 | 完成后→IDLE |
| `PERCHED_ON_HAND` | 站在手上 | 手消失→FLYING |
| `DANCING` | 跳舞 | 语音可打断 |
| `FROZEN` | 冻结 | 仅 UNFREEZE |

**HeadState 4 项**：`HEAD_FORWARD` / `HEAD_LOOK_AT` / `HEAD_TILT` / `HEAD_NOD`

**BehaviorMode 5 flags**：`BASE` / `COMPANION` / `BUTLER` / `RESEARCHER` / `PLAYFUL`（+ `FULL` = 全开）

**CognitiveState 4 项**：`LISTENING` / `THINKING` / `SPEAKING` / `IDLE_MIND`

**优先级链**：

```
FREEZE (1) > FLY_TO/PERCH (2) > SPEAKING (3) > THINKING_ANIMATION (4) > DANCING (5) > IDLE (9)
```

详 [`../parrot_behavior_rules.md §3.2`](../parrot_behavior_rules.md)。

---

## §12 GOSLO ModelManifest + Capability schema

> 来源：`src/parrot/shared/model_manifest.py`

```python
class ModelManifest:
    model_id: str                           # 全局唯一
    display_name: str
    asset_path: str                         # Resources/parrot_models/<model_id>/
    controller_type: str                    # IParrotController C# 类全名
    capabilities: tuple[Capability, ...]
    coordinate_system: CoordinateSystem
    units: Units
    auto_scale_height_meters: float | None
    parrot_animation_alias: dict[str, str]  # 自定义 capability_id → ParrotAnimation enum 别名

class Capability:
    capability_id: str                      # 自由命名（如 idle / fly / dance_q_pose / wave_hand）
    kind: CapabilityKind                    # ANIMATION / POSE / GESTURE / EXPRESSION / CUSTOM
    target: str                             # Unity Animator state name 等
```

**RESERVED_PARROT_CAPABILITY_IDS** = `frozenset(a.value for a in ParrotAnimation)` = 8 项

接入流程详 [`architecture/goslo_model_manifest_protocol_v1.md`](architecture/goslo_model_manifest_protocol_v1.md)。

---

## §13 Photo 双通道（Phase 4 §8 L7 + L8 锁）

```
[User 在 Unity 工具柜点拍照按钮]
    ↓
Unity PhotoController.CapturePhoto()
    ├─→ 通道 ① preview (reliable + EcpEvent)
    │   - 256px JPEG quality cascade 75→60→50→40
    │   - base64 < 8KB
    │   - publish photo.taken_preview
    │   - X-Photo-Preview-Event-Id header（与 ② 关联）
    └─→ 通道 ② asset (HTTP POST)
        - high-quality JPEG
        - POST http://<brain_host>:7889/upload/photo/{photo_id}
        - Castle 本地 cache: data/photos/{yyyy-mm-dd}/{photo_id}.jpg
    ↓
Brain observer/photo → upsert PhotoNode (kind=PHOTO; L7 强制非 ObjectNode)
Brain photo_upload_server → 写盘 → publish photo.asset_uploaded
```

**约束**：EcpEvent / PhotoNode **只存 ref + metadata，绝不存大图 bytes**。

---

## §14 HTTP endpoints

| endpoint | 方法 | 用途 | 鉴权 |
|:--|:--|:--|:--|
| `http://<brain>:7889/upload/photo/{photo_id}` | POST | Photo asset 上传 | 无（Phase 5+ Bearer）|
| `http://<brain>:<port>/mint` | POST | LiveKit JWT 颁发 | Bearer secret recommended; local dev may run open |

ChatA token policy:

- API secret remains server-side. Unity requests only a short-lived join token.
- Grants are scoped to room join, publish, subscribe, and data. No client
  admin/list/create/record grants.
- Default TTL is short because self-hosted LiveKit cannot immediately revoke an
  already-issued token.

---

## §15 Redis namespaces（Bus L2）

### §15.1 Pub/Sub channel namespace

```
parrot.events.firehose            # 全 event 广播
parrot.brain.*                    # Brain 内部 / Brain ↔ 外部
parrot.dsg.*                      # DSG 子系统
parrot.scheduler.*                # Scheduler / py-trees BT
parrot.nanobot.results            # 结果回流（Pub/Sub）
parrot.external.*                 # 外部桥接（reserve）
```

### §15.2 Stream

```
parrot.events.log                 # L0 EventEnvelope 内部审计（Sprint 0；与 Phase 4 EcpEvent 不同）
parrot.scheduler.task_queue       # Scheduler → Nanobot 任务派发（dispatch_task）
```

### §15.3 HASH

```
parrot:resource_locks             # 资源锁（body / voice / dsg_l2b / ...）
parrot:nanobot_heartbeat          # ⚠️ 写者待 4-A NEED-P2.5-NANOBOT-HEARTBEAT
parrot:bb (alt; in-process 主路径) # BB 跨进程一面
```

---

## §16 Graphiti 5 group_id 分区

| group_id | 用途 |
|:--|:--|
| `episodic` | 对话事件（archive_to_graphiti 主目标）|
| `objects` | 物体节点（identify_object 命中后）|
| `personality` | GOSLO 人设记忆（与 NEED-P2.5-A 联动）|
| `vocabulary` | 用户 / GOSLO 共享词汇表 |
| `nanobot_research` | Nanobot research tool 写入 |

---

## §17 ObservationSource 7+1（LineB §1.3 verbatim 锁）

```
USER_TAG_OBSIDIAN  / USER_EXPLICIT  / IDENTIFY_OBJECT  / GEMINI_ORAL  /
CV_A10  / CV_SENTINEL  / MOCK    （7 baseline，LineB 严格保留 verbatim）
GOSLO_AUTONOMOUS  （DSG Chat 2 加，第 8 项）
```

测试守护：`test_observation_source_legacy_seven_preserved` + 11 项 `test_l2b_node_source_dispatch.py`（ADR-L1.5-001 §3）。

---

## §18 DSG L1.5 6 BucketKind

| BucketKind | TTL | max_nodes | scene 切换 |
|:--|:--|:--|:--|
| `OBSIDIAN_REFERENCE_REINFORCE` | 永久（authority）| None | freeze |
| `OBSIDIAN_SETTING_DAILY` | 永久 | None | freeze |
| `OBSIDIAN_SETTING_ROLEPLAY` | 永久 | None | freeze |
| `IDENTIFY_OBJECT_RESULT` | 永久 | None | freeze |
| `GEMINI_ORAL_MENTION` | TTL（fresh）| 限量 | clear |
| `AUTONOMOUS_CURIOSITY` | 300s（fresh）| 限量 | clear |

---

## §19 IntentWorkspace 9 StagedRefKind

```
PLAN_DRAFT / PLAN_AWAITING_USER / INTENT_THREAD /
IDENTIFY_OBJECT_PENDING / MEMORY_RECALL_THREAD /
BBOX_REFERENCE / FOCUS_REFERENCE / PHOTO_REFERENCE /
CUSTOM
```

Backend：InMemoryBackend / DiskBackend（recover() 待 4-A）。

---

## §20 DSG 9 触发器 + TriggerOutcome 5+2 路上行（V2）

**9 触发器**（4 legacy + 5 new）：

```
Legacy:  calendar / message / scene_context / ssot_enrichment
New:     scene_switch / intent_event_boundary / roleplay_mode / goslo_curiosity / idle_archive
```

**TriggerOutcome 5 路上行**（DSG-V2）：

```python
TriggerOutcome(
    commit_observations: list[Observation],     # → L1.5 Pool.admit
    bucket_ops: list[BucketOp],                 # → BucketRegistry.apply
    staged_refs: list[StagedRef],               # → IntentWorkspace.stage
    archive_request: ArchiveRequest | None,     # → Archive.dispatch
    plan_request: PlanProposal | None,          # → PlanRegistry.draft
    dispatch_to_nanobot: NanobotTask | None,    # legacy V1 → Scheduler+Nanobot
    notify_gemini: ContextInjection | None,     # legacy V1 → Brain Context Injector
)
```

`TriggerResult = TriggerOutcome` alias 兼容；单路失败不影响其他路（test_one_channel_failure_does_not_block_others 守）。

V3 升级触发条件：加新上行通道。

---

## §21 DSG attention Strategy registries

```python
# 4 接口（Strategy registries）
PoolAdmissionPolicy(Protocol)             # baseline: DesktopPolicy(theta_admit=0.3)
AttentionDecayPolicy(Protocol)            # baseline: SimpleAttentionDecayPolicy
AttentionMechanism(Protocol)              # baseline: BoundedBfsActivation
                                          # placeholder: SpreadingActivationPlaceholder（**experimental**）
FoldStrategy(Protocol)                    # baseline: NoOpFoldStrategy（**experimental**）
IntentWorkspaceBackend(Protocol)          # InMemoryBackend / DiskBackend

# 注册函数
register_admission_policy / register_attention_decay_policy /
register_attention_mechanism / register_intent_workspace_backend /
register_source_meta_factory / register_phase4_observers
```

---

## §22 LineB env-gate

```bash
PARROT_LLM_PIPELINE=line_a    # 默认 — Phase 4 baseline (Gemini Realtime)
PARROT_LLM_PIPELINE=line_b    # STT-LLM-TTS pipeline (google.STT + google.LLM + google.TTS + silero.VAD)
```

**ObservationSource 7 entries verbatim 锁**（§17）；transcript_extractor 旧名 alias 保留。

---

## §23 Phase 4 §8 13 决策锁（reference）

> 原文：[`architecture/sprint4_phase4_entry_20260430.md §8`](architecture/sprint4_phase4_entry_20260430.md)

| Lock | 锁定值 简述 |
|:--|:--|
| L1 | EcpState 频率 = 事件驱动 + 1Hz 全量心跳 |
| L2 | EcpEvent topic = `parrot.ecp.event` reliable + UUID v7 event_id + 7 强制字段 |
| L3 | EcpEvent payload < 8KB；Brain 拒收 + synthesized event.rejected.oversize |
| L4 | EcpEvent 与现有 inline envelope（health / intent_disconnect）共存，不迁移 |
| L5 | BBox 拖动 lossy + 放置 reliable + EcpEvent；不走 RPC；ON/OFF 显式 |
| L6 | Focus 拖动 lossy + 锚定 reliable + EcpEvent |
| L7 | PhotoEvent 写 PhotoNode（**非** ObjectNode）；3 EdgeKind defer Phase 5+ |
| L8 | Photo 双通道（preview reliable < 8KB + asset HTTP POST → /upload/photo + Castle 本地 cache）|
| L9 | Δ_focus = 0.2 / Δ_bbox = 1.0 / threshold = 1.0；阈值器在 dsg/attention 不塞 BB；F-05 Echo 全链路 |
| L10 | LLM 注入 = 选项 C 主路径（execute 类 tool 检 BB 三态附 reason）；A 保留 fallback；B 显式不实现 |
| L11 | identify_object 1.9s 总预算（800+200+800+100ms）|
| L12 | G1 拆双向（Unity 下行 router EcpEventDispatcher + Python 上行 ingest event_ingest）|
| L13 | dsg/attention/__init__.py 不 export Attention 类（防误读为 L3 已落地）|

---

## §24 ADR-L1.5-001 §4.1 三触发器（reference）

> 原文：[`architecture/adr_l1_5_source_dispatch_extension_space_20260504.md §4.1`](architecture/adr_l1_5_source_dispatch_extension_space_20260504.md)

| 触发器 | 当前 | 升级到 |
|:--|:--|:--|
| ① ≥3 source 字段差异 ≥3 个 | **未触发**（meta dict）| typed Pydantic model |
| ② ≥2 source 行为多态 | **未触发**（Strategy 注册表）| 子类（A10SemanticNode 等）|
| ③ isinstance 反复手写 | **未触发** | typed dispatch + 子类 |

DSG Chat 2 §5 已确认全未触发；继续 meta dict + factory hybrid。

---

## §25 cs_parity 4/4 守护

> 文件：`tests/test_ecp_event/test_cs_parity.py`

| 测试 | 守护 |
|:--|:--|
| `test_event_type_names_match_python_enum` | C# `EcpEventTypeNames` == Python `EcpEventType` 13 项 |
| `test_event_source_names_match_python_enum` | C# `EcpEventSourceNames` == Python 3 项 |
| `test_topic_constants_match_python` | 5 topic 常量字符串相等 |
| `test_cs_dto_file_exists` | `EcpEventDto.cs` 文件存在 |

**任何 Python enum 增减 → C# 必须同步**；CI 阻断单边漂移。

---

## §26 测试基线 + 0 漂移声明

| 维度 | 状态（2026-05-07）|
|:--|:--|
| pytest 全量（除 integration + identify_object pre-existing breakage） | **415/415** ✅ |
| Phase 4 §8 13 锁 | **0 漂移** |
| ADR-L1.5-001 §4.1 三触发器 | **0 触发**（DSG Chat 2 §5 守）|
| cs_parity 4/4 | ✅ |
| ObservationSource 7 entries verbatim | ✅（LineB 守）|
| ParrotAnimation 8 / NodeKind 6 / EdgeKind 8 | 全 freeze test 守 |

---

## §27 后续 upgrade 入口（cross-link）

| 标签 | 修复 chat | 影响协议 |
|:--|:--|:--|
| NEED-P2.5-PLAN-INTEGRATION（4 plan-* TODO）| Chat 4 4-A 实施轨 | Redis Stream payload 加 plan_id/step_id/result_channel |
| NEED-P2.5-NANOBOT-HEARTBEAT | 同上 | parrot:nanobot_heartbeat HSET 写者 |
| NEED-P2.5-ARCHIVE-LLM | 同上 | archive_to_graphiti 真 LLM 蒸馏 |
| TODO(Chat4-disk-recover) | 同上 | DiskBackend.recover() |
| NEED-P2.5-A persona 外置 | DSG 协议升级 chat | brain/personas/ + BB key `global/active_persona_id` |
| NEED-P3-A body_state 解锁 | P3 wire 升级 ADR chat | EcpFrontendState 加 controller_body_state（Option A 推荐）|
| NEED-P3-B 4 类块注册表 | DSG 协议升级 chat | model/persona/mode/scene 4 active BB key + 切换 EcpEvent |
| NEED-P3-C 预设 schema | 同上 | data/presets/<id>.json schema |
| NEED-P3-D node-canvas UI | AR 工作区独立 chat | Unity SO 接口 |
| TODO(P3-Wire-PlanUI) | P3 wire 升级 ADR chat | 新 EcpEventType (plan.proposed / approved / rejected / revised) |
| TODO(P3-fold-bionic) | P3 仿生升级 chat | FoldStrategy 真实施 |
| TODO(P3-attention-spreading) | 同上 | SpreadingActivation 真迭代 |
| TODO(P3-RefHealth) | 同上 | refs.verify_ref 真 URL/Graphiti/Obsidian 验证 |
| TODO(P3-multi-scene) | P3/A10 接入 chat | 多 SceneType profile（HOME_INDOOR / OUTDOOR / LIBRARY / KITCHEN）|
| Castle ↔ Mecha A10 接入 | A10 接入 chat | 新 cross-process 协议 |

详 [`architecture/cross_chat_pending_registry_20260507.md`](architecture/cross_chat_pending_registry_20260507.md)（NEED-* / TODO 真源）。

---

## §28 变更日志

- **2026-05-09 ChatA**：补充 app-level LiveKit RPC addendum、2DWorkspace BB key、app capability mode、token mint 短 TTL/最小 grant 策略。DataChannel 5 topic、EcpEventType 13 项、Phase 4 §8 锁均未新增。
- **2026-05-07**：本文创建（Sprint 4 收口 + DSG Chat 2 + GOSLO mod 后的全协议 SSOT）。补充 protocol_snapshot_p1.md（Phase 1 历史保留），整合 Chat 4 接口提炼工作中的可用协议字段（结构 + enum + 锁）。Chat 4 接口提炼 chat pivot 后的收口产物。
