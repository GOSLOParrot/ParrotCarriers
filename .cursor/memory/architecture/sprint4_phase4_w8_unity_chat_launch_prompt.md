---
status: ratified
category: chat-launch-prompt
status_note: "用于启动 ArSpike 工具 ④ Unity 半边 chat（capturePhoto UI + 256px preview + HTTP POST + photo.taken_preview publish）。建议模型：Sonnet 4.6 medium thinking。"
last_reviewed: 2026-04-30
---

# Launch Prompt — ArSpike 工具 ④ Unity 半边（PhotoEvent 完整闭环）

> **复制下面 ```text``` 块的内容**到新 chat 即可。预设模型：**Sonnet 4.6 medium thinking**（备选 GPT-5.3 Codex high-fast；不要用 Opus 4.7 / Composer-2 / Gemini）。

```text
你是 ParrotCarriers Sprint4 Phase 4 工具 ④ Unity 半边实现助手
(capturePhoto + 256px preview + HTTP POST + photo.taken_preview EcpEvent
publish)。think in English，用中文回答。

## 第一步（不可跳过）

按顺序读以下 6 份文件 / 区段，**全文** 或 **指定 §**：

1. .cursor/memory/architecture/sprint4_phase4_completion_and_final_audit_20260430.md
   §3.1 (event_type 注册表) + §8.1 (W8 Unity 半边派发说明) + §5 一致性审计
   — 这是 Phase 4 终态 anchor，所有锁定值在这里
2. .cursor/memory/architecture/sprint4_phase4_entry_20260430.md
   §8.1 L7 (PhotoEvent → PhotoNode 不等于 ObjectNode) + L8 (照片双通道)
   + §8.3 (photo.* event_type 注册表)
3. .cursor/memory/architecture/sprint4_phase4_w6_w7_unity_completion_20260430.md
   §1.1 (Unity 模式 inventory)+ §B.6 (reconnect 行为) + §10.4 (协作模式)
   — W6-7 Unity 半边的 BBoxController / FocusController 是你的 mirror 范本
4. src/parrot/brain/observer/photo.py（Brain 端 W8 接收方，**只读**；
   你 publish 的 photo.taken_preview payload 字段必须与这里 _build_bb_payload
   读的字段对齐）
5. src/parrot/brain/photo_upload_server.py（Brain 端 W8 HTTP 接收方，
   **只读**；你 POST 的路径 / header / body 形式必须与这里 upload_photo
   handler 一致）
6. src/parrot/shared/bb_schema.py 找 transient/last_photo_event 注释
   （payload 11 字段 schema_version=1，是你 publish 必须填的字段集）

参考 Unity 既有 mirror 模式（**只读**，不复制粗鲁，按 mirror 模式写新文件）：
- unity/ArSpike/Assets/Scripts/ParrotApp/Attention/BBoxController.cs
  （PlaceBBox / RemoveBBox 公共 API + ContextMenu Debug 入口；payload
  bbox_id 必带 + corners + pose 模式 — Photo 你照搬这个结构）
- unity/ArSpike/Assets/Scripts/ParrotApp/Attention/AttentionConfigEchoPublisher.cs
  （RoomManager.OnConnected 订阅 + EchoNow ContextMenu 兜底 + reconnect
  行为）— Photo 你的 controller 也要在 reconnect 时考虑"是否要重 publish
  已上传过的照片"（详见任务范围 §B.5）
- unity/ArSpike/Assets/Scripts/ParrotApp/Ecp/EcpEventPublisher.cs
  （EcpEventBuilder.BuildUnityEvent + Publisher.Publish + DroppedNoRoom
  log；你直接复用，**不**改这个 Publisher 文件）
- unity/ArSpike/Assets/Scripts/ParrotApp/Ecp/EcpEventDto.cs（EcpEventTypeNames
  里 PhotoTakenPreview / PhotoAssetUploaded 已有；你直接用）

## 任务范围（W8 Unity 半边 — 严格对齐）

### B.1 PhotoController 主体

新建 unity/ArSpike/Assets/Scripts/ParrotApp/Photo/PhotoController.cs
（命名空间 ParrotApp.Photo）：

- **公共 API**：CapturePhoto() / CapturePhotoWithCandidate(string subjectUuid)
  / 配合 ContextMenu Debug 入口（Debug: Capture Test Photo / Capture With
  Candidate）—— UI 真触发后续 chat 可以接，本 chat 用 ContextMenu 兜底
- **photo_id 生成**：格式 "ph_<guid8>"（与 bbox_id "bb_<guid8>" / focus_id
  "fc_<guid8>" 命名空间隔离 — Brain 端 PhotoNode 的 uuid 直接用此 photo_id）
- 持有当前 ON 集合：Dictionary<string, PendingPhoto>，每个 PendingPhoto 含
  photo_id / capture timestamp / asset 上传状态（pending / uploaded / failed）
- 关键依赖：BBoxController / FocusController 取当前 active refs；不直接
  访问 brain.refs（Brain 内部状态），用 Unity 端 controller 自身 dict

### B.2 256px preview JPEG 生成

- 抓帧路径：捕获 ARSession 当前帧 / 主相机 RenderTexture（spike 期允许
  从 Camera.main.targetTexture 抓；正式 AR 路径 W3.A.2 / W3.A.3 已建
  baseline，photo capture 应该兼容 spike + 真 AR 两种来源）
- 缩放到 **最长边 256px**（保持长宽比；用 RenderTexture / Texture2D blit）
- JPEG 编码：UnityEngine.ImageConversion.EncodeToJPG 质量 75（Editor 可
  Inspector 调）
- Base64 编码：System.Convert.ToBase64String
- **必须 < 8 KB**（entry §8.1 L3 锁定值；超过即 publish 失败）。256px JPEG
  Q75 通常 5-7 KB；如超 8 KB 需要降质量 / 降尺寸（不要 crop pose 元数据，
  优先降 JPEG quality 60→50→40）

### B.3 photo.taken_preview EcpEvent payload

publish 调用 EcpEventBuilder.BuildUnityEvent(EcpEventTypeNames.PhotoTakenPreview,
payloadJson, ...)，payload 必须含 11 字段（schema_version=1，与
src/parrot/shared/bb_schema.py:transient/last_photo_event 注释精确对齐）：

  {
    "schema_version": 1,
    "photo_id": "ph_<guid8>",
    "stage": "preview",                   // 固定字符串 "preview"
    "pose": {"px": ..., "py": ..., "pz": ..., "qx": ..., "qy": ..., "qz": ..., "qw": ...},
    "episode_ref": "<episode_id>" | "",   // 当前不在 Episode 内传 ""
    "focus_refs": ["fc_xxx", ...] | [],   // 来自 FocusController 当前 active
    "bbox_refs": ["bb_xxx", ...] | [],    // 来自 BBoxController 当前 active
    "candidate_subject_uuid": "<obj_uuid>" | "",  // 仅 CapturePhotoWithCandidate
    "preview_jpeg_b64": "<base64>",       // 256px JPEG，必 < 8 KB
    "asset_ref": "",                       // preview 阶段固定空（Brain 阶段填）
    "asset_bytes": 0,                      // preview 阶段固定 0
    "ts_ms": <epoch ms>
  }

注意：asset_ref / asset_bytes / stage="asset_uploaded" 是 **Brain 端**
photo_upload_server publish 的 photo.asset_uploaded 事件填的，**Unity 端
绝不**自己 publish photo.asset_uploaded（那是 brain source enum 值）。

### B.4 HTTP POST 全分辨率 asset 上传

publish preview EcpEvent 之后立即（或 Inspector 可调延迟）发 HTTP POST：

- URL: http://<brain_host>:7889/upload/photo/{photo_id}
  （brain_host 默认 127.0.0.1；Inspector 可调 PARROT_BRAIN_HOST，与 Castle
  部署对齐 — 真机走 Castle 公网域名 / 内网 IP，本 chat 仅 Editor 跑通）
- Header: Content-Type: image/jpeg
- **关键 Header**: X-Photo-Preview-Event-Id: <preview event_id>
  （Brain 端 photo_upload_server 用作 photo.asset_uploaded EcpEvent 的
  correlation_id；缺则 Brain 端 fallback 用 photo_id；你必须填以保证
  cross-event 因果链）
- Body: 全分辨率 JPEG 字节（不是 base64；不是 256px preview；是
  原始抓帧的真 JPEG 编码 —— 大小通常 100-500 KB 因相机分辨率而异）
- 推荐用 UnityWebRequest（async / await 包装）；失败重试 max 3 次
  exponential backoff（1s / 2s / 4s）；3 次失败后 PendingPhoto 标
  failed + log，**不**重 publish preview EcpEvent

### B.5 Reconnect 行为（关键不要踩坑）

参考 W6-7 Unity completion §B.6（reconnect 行为统一锁），但 Photo 与
BBox/Focus **不同**：

- **BBox/Focus**：reconnect → 全部重 publish "ON 集合"（refs.bind_bbox 幂等）
- **Photo**：**不重 publish**已上传成功的照片
  - asset 已落 Brain 本地 disk（Castle data/photos/{yyyy-mm-dd}/{photo_id}.jpg），
    重传只是浪费带宽
  - 重 publish preview 也无意义（Brain 端 PhotoNode 已 upsert，幂等检查
    会跳过 — observer/photo._upsert_photo_node 只 bump interaction_count）
  - **唯一例外**：上传失败的 PendingPhoto（status=failed）reconnect 后重试
    HTTP POST，但**不**重发 preview EcpEvent（preview 阶段 Brain 已收）

### B.6 Editor smoke 验证（你 chat 内可跑）

新建 ContextMenu 入口（你的 PhotoController 自己加）：

- "Debug: Capture Test Photo"（无 candidate）→ 验证 preview EcpEvent
  publish + HTTP POST 全流程
- "Debug: Capture With Test Candidate" → 同上但 candidate_subject_uuid
  填一个固定字符串（如 "obj_test_42"）
- "Debug: Capture With Active Refs" → 抓当前 BBoxController / FocusController
  active refs 填进 payload

启动 ParrotSmokeScene + Brain agent dev mode（详见 README）后，期望
Console 输出：

  [EcpEvent:DROPPED] event_type=photo.taken_preview ... wire={"payload":
    {"schema_version":1,"photo_id":"ph_xxx","stage":"preview",...,"preview_jpeg_b64":"..."}}
  [PhotoController] HTTP POST /upload/photo/ph_xxx → 200 bytes=12345

如果 LiveKit 真连了，期望额外看到：

  [EcpEvent inbound brain] event_type=photo.asset_uploaded ... payload=
    {"photo_id":"ph_xxx","asset_ref":"/upload/photo/2026-04-30/ph_xxx.jpg",
     "asset_bytes":12345}

（这是 Brain photo_upload_server 收到 HTTP 后 publish 的回程事件；
EcpEventDispatcher wildcard handler 应该 log 它）

## 不允许（硬约束）

1. 不改 Brain 端任何代码（observer/photo / photo_upload_server / bb_schema /
   ecp_event.py 全锁；W8 Brain 半边已落 + 21 测试守护）
2. 不改 entry doc §8 任意条款（修改即漂移，必须 sign off）
3. 不改 ecp_event.py 的 8KB / topic / schema_version 常量
4. 不动 EcpEventDispatcher 的 topic 路由逻辑（只在它现有 wildcard handler
   基础上加 Photo handler，最多加一个 photo.asset_uploaded 的 typed handler
   做 UI 反馈如"我拍了"动画/语音）
5. 不动 W3.A.2/A.3 / W6-7 / Animation 已落地代码（perch_to_finger /
   EcpState 三态 / BBox/Focus controllers / AnimationDriver）
6. 不发 photo.asset_uploaded EcpEvent（那是 brain source；Unity 发 = source
   enum 错位，跨语言 cs_parity test 不抓但语义错）
7. preview_jpeg_b64 必 < 8 KB（pre-check + reject + log；不让 EcpEvent.build
   抛 ValueError 撞到上层）
8. photo_id 命名 ph_<8 hex chars>（与 bbox_id/focus_id 命名空间隔离 + 与
   Brain observer/photo 的 PhotoNode uuid 直接复用 photo_id 的约定一致）
9. HTTP POST 必带 X-Photo-Preview-Event-Id header（Brain correlation_id
   依赖；失填会导致 photo.asset_uploaded 的 correlation_id fallback 用
   photo_id，cross-event 因果链断）
10. Pytest 全绿（Brain 220/220 baseline 不能破）；Unity 端测试可加但
    不强求（spike 期 Editor smoke 主要靠 ContextMenu + Console log 验）

## 不在本 chat 范围（明确不做）

- AR 场景的"工具柜" prefab UI 触发集成（W6-7 Unity completion §6.3 Q-1
  已留 Phase 5+ defer）— 本 chat 用 ContextMenu 兜底就够
- 真机测试（在另一个独立 chat — sprint4_phase4_smoke_and_gap1_chat_launch_prompt.md）
- BBox/Focus 拖动期间的 lossy parrot.ecp.tick 事件（W6-7 §6.3 Q-2 defer）
- HTTP 鉴权 / Bearer token（Phase 5+ Castle 公网部署时再加）
- 对象存储替换 S3/MinIO（Phase 5+；Brain 端目前 Castle 本地 cache）
- PhotoNode 与 ObjectNode 的 CANDIDATE_SUBJECT 真实 connect 调用
  （Phase 5+；W8 EdgeKind 已加 enum 但 Brain 端不调）

## 完成后必交付

1. 新文件：unity/ArSpike/Assets/Scripts/ParrotApp/Photo/PhotoController.cs
   + 必要的 .meta 文件（Unity 自动生成）
2. ParrotSmokeScene 加挂 PhotoController GameObject + 引用拖线
   （参考 W6-7 ParrotSmokeSceneBuilder.cs Editor menu 模式）
3. Editor 离线 smoke 验证截图 / Console log（粘进完成报告）
4. 完成报告 sprint4_phase4_w8_unity_completion_20260430.md：
   - 落地内容（新文件 / 改动文件）
   - photo.taken_preview payload 字段对齐验证（与 bb_schema.py:
     transient/last_photo_event 注释逐字段对照）
   - HTTP POST 流程验证（Header / Body / 重试策略）
   - Reconnect 行为决策记录（不重发已上传 photo 的理由）
   - 已知漂移 / Phase 5+ defer 列表
5. 不更新 entry doc §8 任意锁定项；只更新 §8.7 W8 row 加 "Unity 半 ✅"
   行（Brain 半已 ✅，本 chat 完成后整行 ✅）

## Sprint 4 终极目标 (不要忘)

工具 ④ Unity 半边落地后，4 个工具的"协议升级 → 体感闭环"全部跑通
（4/4 工具 + 4.5+0.5 = 5/5 验收口径离线达成）。剩真机 spike 在
联机 smoke + 真机 chat 跑。
```

---

## 配套备注（不进 prompt）

| 项 | 说明 |
|:--|:--|
| 模型选择理由 | Sonnet 4.6 medium thinking — Unity C# + 跨 Unity/Brain wire schema 校对 + 文件级动手；与 W3 animation chat 同档；GPT-5.3 Codex 是好备选但 Sonnet 对长 context Unity 场景文件 inspector 拖线指令理解更稳 |
| 预计工作量 | Sonnet 4.6 medium thinking 半天到一天 — 主体 PhotoController.cs ~250-400 行 + smoke 场景挂载 + 完成报告 + Editor 试跑迭代 |
| 风险点 | (a) preview_jpeg_b64 8KB 红线 — 需要质量降级策略；(b) UnityWebRequest 异步 / 主线程同步 — 与 BBoxController 模式对齐；(c) 256px 抓帧 — AR 模式 vs WebCam 模式两种 backend 兼容性 |
| 收口验收 | Editor smoke `[EcpEvent:DROPPED] photo.taken_preview` 日志含完整 11 字段 + HTTP POST 200 / asset 落 Brain disk + 完成报告入库 |
| 后续 chat 衔接 | 完成后下一个 chat = 联机 smoke + GAP-1 chat（见 `sprint4_phase4_smoke_and_gap1_chat_launch_prompt.md`），跑全 5 验收口径 + 真机 spike |
