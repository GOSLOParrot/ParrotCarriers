---
status: draft
status_note: "Sprint4 Phase 4 Photo / Camera core-function design note. Defines immediate photo memory, PhotoNode, awareness policy, notification policy, and blocking-tool budget before implementation."
last_reviewed: 2026-04-29
---

# 设计审计: Photo Awareness & Memory Pipeline

> 日期: 2026-04-29
> 触发: Phase 4 行为矩阵中工具 ④「照相机」的 PhotoEvent / PhotoNode / payload 通道决策
> 状态: **设计待 ratify**。本文用于回答: 拍照第一时间 GOSLO 如何知道发生了什么、是否知道自己被拍、是否要打断对话、照片如何进入短期记忆与 L2-B。
> 核心原则: **拍照是核心功能，不是 Event 附件。PhotoEvent 记录事实，PhotoFramePreview 支撑即时感知，PhotoNode 进入 L2-B 工作记忆。**

---

## 0. TL;DR

Phase 4 不应把照片简化成「上传后返回一个 URI」。那样 GOSLO 第一时间只知道「发生了拍照」，不知道「拍了什么 / 是不是拍我 / 要不要反应」，体感会空。

正确的最小链路是:

```text
用户拍照 / 相机倒计时 / capturePhoto
  │
  ├─ [即时] 低质量 preview + timestamp + context 进入短期内存
  │       PhotoFramePreview(photo_id, captured_at, preview_ref, pose, focus/bbox, candidates)
  │
  ├─ [即时] PhotoEvent 进入 EventEnvelope
  │       记录「拍照发生了」以及 photo_id / preview_ref / policy / awareness_result
  │
  ├─ [即时] L2-B 创建 PhotoNode
  │       kind=photo，挂 Episode / RefBinding / candidate ObjectNode
  │
  ├─ [即时] AwarenessPolicy 判断 GOSLO 是否 aware / 是否通知 / 是否阻塞
  │       UNAWARE_RECORDED / AWARE_SILENT / AWARE_REACT / AWARE_INTERRUPT / STARTLED
  │
  └─ [异步] 高质量照片 upload + caption / identify / Graphiti archive 后补
```

一句话:

> **第一时间存「可感知的低质量 preview + 上下文」，不是只存高质量 payload 的 URI。高质量 payload 慢慢传，GOSLO 的即时反应靠 preview + context + awareness policy。**

---

## 1. 问题边界

### 1.1 不能只回答「照片 payload 走什么通道」

工具 ④ 的真实问题有三层:

| 层 | 问题 | 体感影响 |
|---|---|---|
| 事实层 | 拍照发生了吗？什么时候？谁触发？ | GOSLO 能否知道「刚刚拍了」 |
| 感知层 | 第一时间能不能知道大概拍了什么？是不是拍 GOSLO？ | GOSLO 能否做自然反应 |
| 持久层 | 高质量图片存哪里？如何回查？ | 后续记忆 / 回看 / Graphiti archive |

只传 URI 只能解决持久层，不能解决事实层和感知层。

### 1.2 PhotoEvent / PhotoFramePreview / PhotoNode 三者分工

| 结构 | 所属层 | 生命周期 | 作用 |
|---|---|---|---|
| `PhotoEvent` | L0 EventEnvelope | 长于 session，可进 event log | 记录「拍照发生」这件事实 |
| `PhotoFramePreview` | 短期内存 / cache | TTL，5-30 分钟起步 | 给 GOSLO 第一时间看低质量图和上下文 |
| `PhotoNode` | DSG L2-B | session / episode 工作记忆 | 让照片成为可引用、可连边、可被注意力系统处理的节点 |
| 高质量 `PhotoAsset` | 文件 / 对象存储 / HTTP upload | 持久 | 原图、回看、长期记忆依据 |

Phase 4 的关键不是「选一个」，而是让四者各司其职。

---

## 2. 路径边界: Aware / UnAware 不是单一布尔值

拍照时 GOSLO 可能处于多种意识状态:

| 状态 | 含义 | GOSLO 反应 |
|---|---|---|
| `UNAWARE_RECORDED` | 潜意识记录了拍照，但 GOSLO 主意识不被打扰 | 不说话、不动作；Event/PhotoNode 已写 |
| `AWARE_SILENT` | GOSLO 知道发生拍照，但不打断当前对话 | 可在话后提及；不即时插话 |
| `AWARE_REACT` | GOSLO 知道被拍或可能入镜，做非语言小反应 | 看镜头、歪头、摆姿势、停顿 |
| `AWARE_INTERRUPT` | GOSLO 主动打断当前话轮或阻塞下一步，使用工具/说话 | 「等一下，我看看你拍了什么」 |
| `STARTLED` | 拍照事件强度高，触发惊吓或防御性反应 | 抖一下、回头、暂停当前动作 |

这不是 LLM 自己猜出来的状态，而是 `AwarenessPolicy` 根据事件和当前 ECP/BB 状态计算出来。

---

## 3. Phase 4 最小数据结构

### 3.1 PhotoFramePreview

用于「第一时间可感知」。不进 Graphiti，不长期保存 bytes，可由渲染补充通道或 capturePhoto 低质量副本产生。

```text
PhotoFramePreview
  photo_id: str
  captured_at: float
  preview_ref: str              # memory://photo-preview/{photo_id} or file://cache/...
  preview_mime: str             # image/jpeg or image/webp
  preview_width: int
  preview_height: int
  preview_sha256: str
  ttl_seconds: int

  camera_pose: dict             # AR pose / render camera pose, schema later
  render_source: str            # ar_camera | composite_render | tool_preview

  episode_id: str
  active_focus_ref: str
  active_bbox_ref: str
  candidate_object_refs: list[str]
  caption_hint: str             # optional quick caption, may be empty at creation

  awareness_state: str
  notification_policy: str
```

默认 preview 建议:

- 长边 256 或 512 px。
- JPEG/WebP 低质量压缩。
- TTL 5-30 分钟。
- 存短期 cache，EventEnvelope / BB 只传 `preview_ref`，不传 bytes。

### 3.2 PhotoEvent

记录事实。走 `EventEnvelope`，用于 Observer / event log / downstream consumer。

```text
PhotoEvent
  event_id: str
  event_type: "photo.captured"
  photo_id: str
  captured_at: float
  actor: "user" | "goslo" | "system"

  preview_ref: str
  asset_ref: str                # high-quality asset may be empty at first
  photo_node_uuid: str
  episode_id: str

  awareness_state: str
  notification_policy: str
  blocking_decision: str
```

`PhotoEvent` 不承载图片 bytes。

### 3.3 PhotoNode

Photo 是核心功能，默认进入 L2-B。它不是普通 `OBJECT`，而是媒体/证据节点。

Phase 4 推荐:

```text
NodeKind.PHOTO = "photo"
```

PhotoNode 可先用现有 `SemanticNode(kind=PHOTO, meta={...})` 表达，不急着引入 Python 子类继承。

```text
SemanticNode(kind=PHOTO)
  uuid: photo_node_uuid
  label: "Photo 2026-04-29 18:03:12"
  provenance_stream_id: event_id
  reference_image_path / last_sighting_path: preview or final asset path
  time_span: (captured_at, captured_at)
  meta:
    photo_id
    preview_ref
    asset_ref
    thumbnail_ref
    sha256
    camera_pose
    awareness_state
    caption_hint
```

推荐新增边:

```text
EdgeKind.CAPTURED_DURING   # PhotoNode -> Episode marker / Event node
EdgeKind.DEPICTS           # PhotoNode -> ObjectNode / PersonNode
EdgeKind.FOCUSES_ON        # PhotoNode -> RefBinding target
EdgeKind.ANNOTATED_BY      # PhotoNode -> user note / caption event, later
```

---

## 4. AwarenessPolicy

### 4.1 输入信号

Awareness 判断不应只看「用户按下拍照」。它要综合:

| 信号 | 来源 | 例子 |
|---|---|---|
| 相机准备 | Unity UI / tool event | 打开相机、进入取景、倒计时、快门半按 |
| 注意力 | Focus/BBox / DSG threshold | 当前框选 GOSLO、某个对象、用户一直放大某区域 |
| GOSLO 状态 | EcpState / BB | speaking、thinking、flying、perched、dancing、frozen |
| 用户设置 | app settings | 是否拍照通知 GOSLO、是否允许打断 |
| 事件强度 | Observer | 快门声、闪光、突然近距离、用户说「我要拍你」 |
| 视觉候选 | PhotoFramePreview / L2-B | preview 中是否包含 GOSLO / 当前前景对象 |

### 4.2 输出字段

```text
AwarenessDecision
  awareness_state:
    UNAWARE_RECORDED | AWARE_SILENT | AWARE_REACT | AWARE_INTERRUPT | STARTLED

  notify_llm: bool
  allow_interrupt_speech: bool
  allow_blocking_tool_now: bool
  defer_tool_until_after_turn: bool
  recommended_action: str
  reason: str
```

### 4.3 默认策略建议

Phase 4 默认值可先保守:

| 条件 | 输出 |
|---|---|
| 设置关闭「拍照即时通知」 | `UNAWARE_RECORDED`，只写 Event / PhotoNode |
| GOSLO 正在说话，事件强度低 | `AWARE_SILENT`，话后可见 |
| GOSLO 被 Focus/BBox 指向，且拍照发生 | `AWARE_REACT`，非语言反应 |
| 用户说「我要拍你」或倒计时明显 | `AWARE_REACT` 或 `AWARE_INTERRUPT`，取决于设置 |
| 闪光/突然近距离/强打断事件 | `STARTLED` |
| 用户明确问「刚才拍到什么」 | `AWARE_INTERRUPT`，允许阻塞 tool |

---

## 5. Tool 阻塞预算: GOSLO 必须知道 tool 会不会卡住自己

用户关心的不是「能不能用 tool」，而是 GOSLO 是否知道:

- 它现在正在说话；
- 调某个视觉 tool 会阻塞本轮话语；
- 它可以选择现在打断、话后再看、或只做潜意识记录。

因此每个照片相关 tool / task 应声明成本:

```text
ToolCost
  blocks_speech: bool
  expected_latency_ms: int
  timeout_ms: int
  can_run_after_turn: bool
  can_run_silently: bool
  result_can_notify_later: bool
```

Phase 4 的照片工具建议分三档:

| 能力 | 是否阻塞 | 预算 | 用途 |
|---|---|---|---|
| `photo_preview_caption` | 可阻塞 / 可话后 | 300-800ms | 看低质量 preview，快速说「大概拍到 X」 |
| `identify_photo_subject` | 阻塞 | ≤2s | 在 L2-B / Graphiti 候选里确认拍的是什么 |
| `enrich_photo_memory` | 不阻塞 | 后台 | 高质量 caption、Graphiti archive、长记忆 |

AwarenessPolicy 不直接调用 tool，只给调度器 / LLM 注入「现在是否允许阻塞」的上下文。

---

## 6. 与 Observer / Attention / Trigger 的关系

### 6.1 Observer

Observer 负责记录:

- 用户打开相机；
- 用户倒计时 / 取景 / 拍照；
- capturePhoto ack；
- PhotoFramePreview 创建；
- 高质量 asset upload 完成；
- quick caption / identify 完成。

Observer 不判断「要不要打扰 GOSLO」，只产 EventEnvelope。

### 6.2 Attention / 临时阈值器

Attention 临时阈值器负责:

- Focus/BBox 权重；
- 当前 target 是否达到「值得告诉 GOSLO」的阈值；
- 拍照是否强化当前 target 的注意力权重。

它不存图片，不做 upload，不做 caption。

### 6.3 Trigger

Trigger 可在 Phase 4 末端或 Phase 5 接入:

- 「用户连续拍同一对象」→ 建议建 Episode；
- 「GOSLO 被拍」→ 触发表情 / 姿态；
- 「照片带未知对象」→ 触发后续 identify / Nanobot task；
- 「Episode 结束」→ archive PhotoNode summary 到 Graphiti。

---

## 7. Payload 通道决策

### 7.1 低质量 preview

低质量 preview 是即时感知用，优先走已有/计划中的渲染补充通道或 capturePhoto 的低清副产物。

推荐:

```text
Unity render/camera → low-res JPEG/WebP → short-term cache
EventEnvelope carries preview_ref, not bytes
```

可选实现:

- `memory://photo-preview/{photo_id}`: 进程内或 Redis/本地 cache 的逻辑 ref。
- `file://data/photo_previews/{date}/{photo_id}.webp`: 本机文件路径。
- `http://castle/.../preview/{photo_id}`: 如果已有 HTTP upload 服务。

Phase 4 不建议把 preview bytes 直接塞进 reliable DataChannel；除非做非常小的 inline thumbnail 并严格限大小。

### 7.2 高质量照片

高质量照片走异步 upload:

```text
Unity capturePhoto → HTTP upload / file store → asset_ref
PhotoNode.asset_ref 后补
```

LiveKit File API / ByteStream 可作为 spike，但不作为 Phase 4 默认路径。原因:

- 照片不是实时媒体帧，不需要占用 RTC 语义；
- DataChannel 分块会和 reliable event 链路抢队列；
- HTTP/file store 更适合断点、校验、持久化、回查。

---

## 8. 对 Phase 4 行为矩阵第 4 / 第 5 点的修正回答

### 8.1 第 4 点: PhotoEvent 是否写 L2-B 节点？

修正结论:

> **是。PhotoEvent 默认创建 L2-B PhotoNode。**

但边界要写清:

- PhotoNode 是 `NodeKind.PHOTO`，不是 `NodeKind.OBJECT`。
- PhotoNode 表示「这张照片 / 这份媒体证据」，不是自动生成「照片里有某物」的语义事实。
- PhotoNode 立即挂 Episode / Focus / BBox / candidate Object refs。
- PhotoNode 默认不直接写 Graphiti；Graphiti 写入在 Episode archive、用户显式保存、或照片被确认有长期价值时发生。

这样不会污染 DSG。污染风险来自「把每张照片里的未知物体都自动变 ObjectNode」，不是来自 PhotoNode 本身。

### 8.2 第 5 点: 照片 payload 通道怎么定？

修正结论:

> **拆成低质量 preview 与高质量 asset 两条通道。**

Phase 4 默认:

- 低质量 preview: 第一时间进短期内存 / cache，供 GOSLO 即时 aware 和快速 caption 使用。
- PhotoEvent / PhotoNode: 只存 `preview_ref` / `asset_ref` / metadata，不存 bytes。
- 高质量照片: 异步 HTTP upload / file store，完成后回写 `asset_ref`。
- DataChannel: 只传 EventEnvelope 和 ref，不传高质量 payload。
- LiveKit File API: 作为后续 spike，不做默认协议基础。

---

## 9. Phase 4 最小落地范围

必做:

1. `PhotoEvent` schema。
2. `PhotoFramePreview` schema / cache ref 约定。
3. `NodeKind.PHOTO` + PhotoNode meta 约定。
4. `PhotoEvent -> PhotoNode` writer。
5. `AwarenessDecision` schema。
6. 拍照通知策略: 关闭 / 静默 / 反应 / 可打断。
7. ToolCost 字段，至少让照片相关工具声明是否阻塞 speech。

可推迟:

- 高质量照片持久化的完整 UI。
- LiveKit File API / ByteStream。
- 完整 DSG L3 注意力模块。
- Graphiti prescribed ontology 的 PhotoEntity 细化。
- 多照片相册 / 搜索 / 回看 UI。

---

## 10. 待决问题

1. 低质量 preview 的默认尺寸: 256 长边还是 512 长边？
2. preview cache 的第一版落位: 进程内、Redis、还是本地文件？
3. 拍照通知设置默认值: 默认静默、默认小反应、还是默认通知？
4. GOSLO 被拍照时的默认动作: 看镜头、歪头、摆姿势、还是保持当前行为？
5. `photo_preview_caption` 是否在 Phase 4 做成真正 tool，还是先用现有 `identify_object` 的 captureSnapshot 路径复用？
6. PhotoNode 是否在 Episode 结束时默认进入 Graphiti，还是只在用户显式保存 / 标星时进入？

---

## 11. 关联文档

- `architecture/sprint4_phase4_entry_20260430.md` — Phase 4 入场与工具 ④ 原始问题
- `architecture/audit_identify_object_no_screenshot_20260420.md` — 按需识别 tool 的同步体感红线
- `architecture/sprint4_protocol_v2_ecp.md` — ECP / EventEnvelope / RefBinding 协议背景
- `parrot_behavior_rules.md` — Reflex / Intent / Task 与 tool 阻塞规则
- `src/parrot/dsg/l2b_types.py` — 当前 L2-B SemanticNode / NodeKind / EdgeKind
- `src/parrot/shared/snapshot.py` — Snapshot / PhotoEvent 存储路径约定
---
status: draft
status_note: "Sprint4 Phase 4 Photo / Camera core-function design note. Defines immediate photo memory, PhotoNode, awareness policy, notification policy, and blocking-tool budget before implementation."
last_reviewed: 2026-04-29
---

# 设计审计: Photo Awareness & Memory Pipeline

> 日期: 2026-04-29
> 触发: Phase 4 行为矩阵中工具 ④「照相机」的 PhotoEvent / PhotoNode / payload 通道决策
> 状态: **设计待 ratify**。本文用于回答: 拍照第一时间 GOSLO 如何知道发生了什么、是否知道自己被拍、是否要打断对话、照片如何进入短期记忆与 L2-B。
> 核心原则: **拍照是核心功能，不是 Event 附件。PhotoEvent 记录事实，PhotoFramePreview 支撑即时感知，PhotoNode 进入 L2-B 工作记忆。**

---

## 0. TL;DR

Phase 4 不应把照片简化成「上传后返回一个 URI」。那样 GOSLO 第一时间只知道「发生了拍照」，不知道「拍了什么 / 是不是拍我 / 要不要反应」，体感会空。

正确的最小链路是:

```text
用户拍照 / 相机倒计时 / capturePhoto
  │
  ├─ [即时] 低质量 preview + timestamp + context 进入短期内存
  │       PhotoFramePreview(photo_id, captured_at, preview_ref, pose, focus/bbox, candidates)
  │
  ├─ [即时] PhotoEvent 进入 EventEnvelope
  │       记录「拍照发生了」以及 photo_id / preview_ref / policy / awareness_result
  │
  ├─ [即时] L2-B 创建 PhotoNode
  │       kind=photo，挂 Episode / RefBinding / candidate ObjectNode
  │
  ├─ [即时] AwarenessPolicy 判断 GOSLO 是否 aware / 是否通知 / 是否阻塞
  │       UNAWARE_RECORDED / AWARE_SILENT / AWARE_REACT / AWARE_INTERRUPT / STARTLED
  │
  └─ [异步] 高质量照片 upload + caption / identify / Graphiti archive 后补
```

一句话:

> **第一时间存「可感知的低质量 preview + 上下文」，不是只存高质量 payload 的 URI。高质量 payload 慢慢传，GOSLO 的即时反应靠 preview + context + awareness policy。**

---

## 1. 问题边界

### 1.1 不能只回答「照片 payload 走什么通道」

工具 ④ 的真实问题有三层:

| 层 | 问题 | 体感影响 |
|---|---|---|
| 事实层 | 拍照发生了吗？什么时候？谁触发？ | GOSLO 能否知道「刚刚拍了」 |
| 感知层 | 第一时间能不能知道大概拍了什么？是不是拍 GOSLO？ | GOSLO 能否做自然反应 |
| 持久层 | 高质量图片存哪里？如何回查？ | 后续记忆 / 回看 / Graphiti archive |

只传 URI 只能解决持久层，不能解决事实层和感知层。

### 1.2 PhotoEvent / PhotoFramePreview / PhotoNode 三者分工

| 结构 | 所属层 | 生命周期 | 作用 |
|---|---|---|---|
| `PhotoEvent` | L0 EventEnvelope | 长于 session，可进 event log | 记录「拍照发生」这件事实 |
| `PhotoFramePreview` | 短期内存 / cache | TTL，5-30 分钟起步 | 给 GOSLO 第一时间看低质量图和上下文 |
| `PhotoNode` | DSG L2-B | session / episode 工作记忆 | 让照片成为可引用、可连边、可被注意力系统处理的节点 |
| 高质量 `PhotoAsset` | 文件 / 对象存储 / HTTP upload | 持久 | 原图、回看、长期记忆依据 |

Phase 4 的关键不是「选一个」，而是让四者各司其职。

---

## 2. 路径边界: Aware / UnAware 不是单一布尔值

拍照时 GOSLO 可能处于多种意识状态:

| 状态 | 含义 | GOSLO 反应 |
|---|---|---|
| `UNAWARE_RECORDED` | 潜意识记录了拍照，但 GOSLO 主意识不被打扰 | 不说话、不动作；Event/PhotoNode 已写 |
| `AWARE_SILENT` | GOSLO 知道发生拍照，但不打断当前对话 | 可在话后提及；不即时插话 |
| `AWARE_REACT` | GOSLO 知道被拍或可能入镜，做非语言小反应 | 看镜头、歪头、摆姿势、停顿 |
| `AWARE_INTERRUPT` | GOSLO 主动打断当前话轮或阻塞下一步，使用工具/说话 | 「等一下，我看看你拍了什么」 |
| `STARTLED` | 拍照事件强度高，触发惊吓或防御性反应 | 抖一下、回头、暂停当前动作 |

这不是 LLM 自己猜出来的状态，而是 `AwarenessPolicy` 根据事件和当前 ECP/BB 状态计算出来。

---

## 3. Phase 4 最小数据结构

### 3.1 PhotoFramePreview

用于「第一时间可感知」。不进 Graphiti，不长期保存 bytes，可由渲染补充通道或 capturePhoto 低质量副本产生。

```text
PhotoFramePreview
  photo_id: str
  captured_at: float
  preview_ref: str              # memory://photo-preview/{photo_id} or file://cache/...
  preview_mime: str             # image/jpeg or image/webp
  preview_width: int
  preview_height: int
  preview_sha256: str
  ttl_seconds: int

  camera_pose: dict             # AR pose / render camera pose, schema later
  render_source: str            # ar_camera | composite_render | tool_preview

  episode_id: str
  active_focus_ref: str
  active_bbox_ref: str
  candidate_object_refs: list[str]
  caption_hint: str             # optional quick caption, may be empty at creation

  awareness_state: str
  notification_policy: str
```

默认 preview 建议:

- 长边 256 或 512 px。
- JPEG/WebP 低质量压缩。
- TTL 5-30 分钟。
- 存短期 cache，EventEnvelope / BB 只传 `preview_ref`，不传 bytes。

### 3.2 PhotoEvent

记录事实。走 `EventEnvelope`，用于 Observer / event log / downstream consumer。

```text
PhotoEvent
  event_id: str
  event_type: "photo.captured"
  photo_id: str
  captured_at: float
  actor: "user" | "goslo" | "system"

  preview_ref: str
  asset_ref: str                # high-quality asset may be empty at first
  photo_node_uuid: str
  episode_id: str

  awareness_state: str
  notification_policy: str
  blocking_decision: str
```

`PhotoEvent` 不承载图片 bytes。

### 3.3 PhotoNode

Photo 是核心功能，默认进入 L2-B。它不是普通 `OBJECT`，而是媒体/证据节点。

Phase 4 推荐:

```text
NodeKind.PHOTO = "photo"
```

PhotoNode 可先用现有 `SemanticNode(kind=PHOTO, meta={...})` 表达，不急着引入 Python 子类继承。

```text
SemanticNode(kind=PHOTO)
  uuid: photo_node_uuid
  label: "Photo 2026-04-29 18:03:12"
  provenance_stream_id: event_id
  reference_image_path / last_sighting_path: preview or final asset path
  time_span: (captured_at, captured_at)
  meta:
    photo_id
    preview_ref
    asset_ref
    thumbnail_ref
    sha256
    camera_pose
    awareness_state
    caption_hint
```

推荐新增边:

```text
EdgeKind.CAPTURED_DURING   # PhotoNode -> Episode marker / Event node
EdgeKind.DEPICTS           # PhotoNode -> ObjectNode / PersonNode
EdgeKind.FOCUSES_ON        # PhotoNode -> RefBinding target
EdgeKind.ANNOTATED_BY      # PhotoNode -> user note / caption event, later
```

---

## 4. AwarenessPolicy

### 4.1 输入信号

Awareness 判断不应只看「用户按下拍照」。它要综合:

| 信号 | 来源 | 例子 |
|---|---|---|
| 相机准备 | Unity UI / tool event | 打开相机、进入取景、倒计时、快门半按 |
| 注意力 | Focus/BBox / DSG threshold | 当前框选 GOSLO、某个对象、用户一直放大某区域 |
| GOSLO 状态 | EcpState / BB | speaking、thinking、flying、perched、dancing、frozen |
| 用户设置 | app settings | 是否拍照通知 GOSLO、是否允许打断 |
| 事件强度 | Observer | 快门声、闪光、突然近距离、用户说「我要拍你」 |
| 视觉候选 | PhotoFramePreview / L2-B | preview 中是否包含 GOSLO / 当前前景对象 |

### 4.2 输出字段

```text
AwarenessDecision
  awareness_state:
    UNAWARE_RECORDED | AWARE_SILENT | AWARE_REACT | AWARE_INTERRUPT | STARTLED

  notify_llm: bool
  allow_interrupt_speech: bool
  allow_blocking_tool_now: bool
  defer_tool_until_after_turn: bool
  recommended_action: str
  reason: str
```

### 4.3 默认策略建议

Phase 4 默认值可先保守:

| 条件 | 输出 |
|---|---|
| 设置关闭「拍照即时通知」 | `UNAWARE_RECORDED`，只写 Event / PhotoNode |
| GOSLO 正在说话，事件强度低 | `AWARE_SILENT`，话后可见 |
| GOSLO 被 Focus/BBox 指向，且拍照发生 | `AWARE_REACT`，非语言反应 |
| 用户说「我要拍你」或倒计时明显 | `AWARE_REACT` 或 `AWARE_INTERRUPT`，取决于设置 |
| 闪光/突然近距离/强打断事件 | `STARTLED` |
| 用户明确问「刚才拍到什么」 | `AWARE_INTERRUPT`，允许阻塞 tool |

---

## 5. Tool 阻塞预算: GOSLO 必须知道 tool 会不会卡住自己

用户关心的不是「能不能用 tool」，而是 GOSLO 是否知道:

- 它现在正在说话；
- 调某个视觉 tool 会阻塞本轮话语；
- 它可以选择现在打断、话后再看、或只做潜意识记录。

因此每个照片相关 tool / task 应声明成本:

```text
ToolCost
  blocks_speech: bool
  expected_latency_ms: int
  timeout_ms: int
  can_run_after_turn: bool
  can_run_silently: bool
  result_can_notify_later: bool
```

Phase 4 的照片工具建议分三档:

| 能力 | 是否阻塞 | 预算 | 用途 |
|---|---|---|---|
| `photo_preview_caption` | 可阻塞 / 可话后 | 300-800ms | 看低质量 preview，快速说「大概拍到 X」 |
| `identify_photo_subject` | 阻塞 | ≤2s | 在 L2-B / Graphiti 候选里确认拍的是什么 |
| `enrich_photo_memory` | 不阻塞 | 后台 | 高质量 caption、Graphiti archive、长记忆 |

AwarenessPolicy 不直接调用 tool，只给调度器 / LLM 注入「现在是否允许阻塞」的上下文。

---

## 6. 与 Observer / Attention / Trigger 的关系

### 6.1 Observer

Observer 负责记录:

- 用户打开相机；
- 用户倒计时 / 取景 / 拍照；
- capturePhoto ack；
- PhotoFramePreview 创建；
- 高质量 asset upload 完成；
- quick caption / identify 完成。

Observer 不判断「要不要打扰 GOSLO」，只产 EventEnvelope。

### 6.2 Attention / 临时阈值器

Attention 临时阈值器负责:

- Focus/BBox 权重；
- 当前 target 是否达到「值得告诉 GOSLO」的阈值；
- 拍照是否强化当前 target 的注意力权重。

它不存图片，不做 upload，不做 caption。

### 6.3 Trigger

Trigger 可在 Phase 4 末端或 Phase 5 接入:

- 「用户连续拍同一对象」→ 建议建 Episode；
- 「GOSLO 被拍」→ 触发表情 / 姿态；
- 「照片带未知对象」→ 触发后续 identify / Nanobot task；
- 「Episode 结束」→ archive PhotoNode summary 到 Graphiti。

---

## 7. Payload 通道决策

### 7.1 低质量 preview

低质量 preview 是即时感知用，优先走已有/计划中的渲染补充通道或 capturePhoto 的低清副产物。

推荐:

```text
Unity render/camera → low-res JPEG/WebP → short-term cache
EventEnvelope carries preview_ref, not bytes
```

可选实现:

- `memory://photo-preview/{photo_id}`: 进程内或 Redis/本地 cache 的逻辑 ref。
- `file://data/photo_previews/{date}/{photo_id}.webp`: 本机文件路径。
- `http://castle/.../preview/{photo_id}`: 如果已有 HTTP upload 服务。

Phase 4 不建议把 preview bytes 直接塞进 reliable DataChannel；除非做非常小的 inline thumbnail 并严格限大小。

### 7.2 高质量照片

高质量照片走异步 upload:

```text
Unity capturePhoto → HTTP upload / file store → asset_ref
PhotoNode.asset_ref 后补
```

LiveKit File API / ByteStream 可作为 spike，但不作为 Phase 4 默认路径。原因:

- 照片不是实时媒体帧，不需要占用 RTC 语义；
- DataChannel 分块会和 reliable event 链路抢队列；
- HTTP/file store 更适合断点、校验、持久化、回查。

---

## 8. 对 Phase 4 行为矩阵第 4 / 第 5 点的修正回答

### 8.1 第 4 点: PhotoEvent 是否写 L2-B 节点？

修正结论:

> **是。PhotoEvent 默认创建 L2-B PhotoNode。**

但边界要写清:

- PhotoNode 是 `NodeKind.PHOTO`，不是 `NodeKind.OBJECT`。
- PhotoNode 表示「这张照片 / 这份媒体证据」，不是自动生成「照片里有某物」的语义事实。
- PhotoNode 立即挂 Episode / Focus / BBox / candidate Object refs。
- PhotoNode 默认不直接写 Graphiti；Graphiti 写入在 Episode archive、用户显式保存、或照片被确认有长期价值时发生。

这样不会污染 DSG。污染风险来自「把每张照片里的未知物体都自动变 ObjectNode」，不是来自 PhotoNode 本身。

### 8.2 第 5 点: 照片 payload 通道怎么定？

修正结论:

> **拆成低质量 preview 与高质量 asset 两条通道。**

Phase 4 默认:

- 低质量 preview: 第一时间进短期内存 / cache，供 GOSLO 即时 aware 和快速 caption 使用。
- PhotoEvent / PhotoNode: 只存 `preview_ref` / `asset_ref` / metadata，不存 bytes。
- 高质量照片: 异步 HTTP upload / file store，完成后回写 `asset_ref`。
- DataChannel: 只传 EventEnvelope 和 ref，不传高质量 payload。
- LiveKit File API: 作为后续 spike，不做默认协议基础。

---

## 9. Phase 4 最小落地范围

必做:

1. `PhotoEvent` schema。
2. `PhotoFramePreview` schema / cache ref 约定。
3. `NodeKind.PHOTO` + PhotoNode meta 约定。
4. `PhotoEvent -> PhotoNode` writer。
5. `AwarenessDecision` schema。
6. 拍照通知策略: 关闭 / 静默 / 反应 / 可打断。
7. ToolCost 字段，至少让照片相关工具声明是否阻塞 speech。

可推迟:

- 高质量照片持久化的完整 UI。
- LiveKit File API / ByteStream。
- 完整 DSG L3 注意力模块。
- Graphiti prescribed ontology 的 PhotoEntity 细化。
- 多照片相册 / 搜索 / 回看 UI。

---

## 10. 待决问题

1. 低质量 preview 的默认尺寸: 256 长边还是 512 长边？
2. preview cache 的第一版落位: 进程内、Redis、还是本地文件？
3. 拍照通知设置默认值: 默认静默、默认小反应、还是默认通知？
4. GOSLO 被拍照时的默认动作: 看镜头、歪头、摆姿势、还是保持当前行为？
5. `photo_preview_caption` 是否在 Phase 4 做成真正 tool，还是先用现有 `identify_object` 的 captureSnapshot 路径复用？
6. PhotoNode 是否在 Episode 结束时默认进入 Graphiti，还是只在用户显式保存 / 标星时进入？

---

## 11. 关联文档

- `architecture/sprint4_phase4_entry_20260430.md` — Phase 4 入场与工具 ④ 原始问题
- `architecture/audit_identify_object_no_screenshot_20260420.md` — 按需识别 tool 的同步体感红线
- `architecture/sprint4_protocol_v2_ecp.md` — ECP / EventEnvelope / RefBinding 协议背景
- `parrot_behavior_rules.md` — Reflex / Intent / Task 与 tool 阻塞规则
- `src/parrot/dsg/l2b_types.py` — 当前 L2-B SemanticNode / NodeKind / EdgeKind
- `src/parrot/shared/snapshot.py` — Snapshot / PhotoEvent 存储路径约定
