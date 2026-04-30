---
status: ratified
category: completion-report
status_note: "Sprint4 Phase 4 W8 Unity 半边（PhotoController + 256px preview + HTTP POST + photo.taken_preview EcpEvent publish）落地；离线 Editor smoke 路径就绪（ContextMenu 兜底）。"
last_reviewed: 2026-04-30
---

# Sprint4 Phase 4 W8 Unity 半边完成报告（2026-04-30）

> **本文用途**：W8 Unity 半边落地后的 authoritative 完成口径 + 协议字段对齐验证 + HTTP POST 流程验证 + Reconnect 行为决策记录。
>
> **关联**：`sprint4_phase4_completion_and_final_audit_20260430.md §8.1` = 本文落地范围；Brain 端 W8 已 ✅（commit `84544dd` `b38de6e` `8f63ee2`）；本 chat 使整行 ✅。

---

## §0 一句话总结

PhotoController.cs 落地：`ph_<guid8>` photo_id、12 字段 preview payload、256px JPEG quality cascade (75→60→50→40)、EcpEvent `photo.taken_preview` publish、HTTP POST 带 `X-Photo-Preview-Event-Id` header、reconnect 不重发已上传照片。ParrotSmokeSceneBuilder 更新加入 Photo GameObject。离线 smoke ContextMenu 就绪。

---

## §1 落地内容

### 1.1 新增文件（2）

| 文件 | 命名空间 / 模块 | 作用 |
|:--|:--|:--|
| `unity/ArSpike/Assets/Scripts/ParrotApp/Photo/PhotoController.cs` | `ParrotApp.Photo` | W8 Unity 半边主体：photo_id 生成 / frame 抓帧 / 256px 缩放 / JPEG quality cascade / EcpEvent publish / HTTP POST 重试 / PendingPhoto 状态机 / reconnect 行为 |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Photo/PhotoController.cs.meta` | — | Unity 自动生成（需 Unity Editor 刷新后生成） |

### 1.2 改动文件（3）

| 文件 | 改动 |
|:--|:--|
| `unity/ArSpike/Assets/Scripts/ParrotApp/Attention/BBoxController.cs` | 加 `AppendActiveIds(List<string>)` 只读方法（PhotoController payload 构建用；不动业务逻辑） |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Attention/FocusController.cs` | 同上 |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Editor/ParrotSmokeSceneBuilder.cs` | 加 `using ParrotApp.Photo`；加 "Photo" GameObject + `PhotoController` component；更新 debug log 说明 |

---

## §2 photo.taken_preview payload 字段对齐验证

与 `src/parrot/brain/observer/photo._build_bb_payload` + `bb_schema.py:transient/last_photo_event` 注释逐字段对照：

| 字段 | Unity 端发送值 | Brain 端读取（_build_bb_payload） | 对齐 |
|:--|:--|:--|:--|
| `schema_version` | 硬编码 `1` | `_PHOTO_EVENT_SCHEMA_VERSION = 1` | ✅ |
| `photo_id` | `"ph_" + guid8` | `str(payload.get("photo_id", "") or "")` | ✅ |
| `stage` | 硬编码 `"preview"` | `stage="preview"` 参数传入 | ✅ |
| `pose` | `{"px":..,"py":..,"pz":..,"qx":..,"qy":..,"qz":..,"qw":..}` | `payload.get("pose") if isinstance(..., dict) else {}` | ✅ |
| `episode_ref` | `""` (当前不在 Episode 内) | `str(payload.get("episode_ref", "") or "")` | ✅ |
| `focus_refs` | `["fc_xxx", ...]` 或 `[]` | `list(payload.get("focus_refs") or ())` | ✅ |
| `bbox_refs` | `["bb_xxx", ...]` 或 `[]` | `list(payload.get("bbox_refs") or ())` | ✅ |
| `candidate_subject_uuid` | `"<uuid>"` 或 `""` | `str(payload.get("candidate_subject_uuid", "") or "")` | ✅ |
| `preview_jpeg_b64` | base64 encoded JPEG (≤8KB pre-check) | `str(payload.get("preview_jpeg_b64", "") or "")` | ✅ |
| `asset_ref` | `""` (preview 阶段固定空) | `""` when stage=="preview" | ✅ |
| `asset_bytes` | `0` (preview 阶段固定零) | `0` when stage=="preview" | ✅ |
| `ts_ms` | `EcpEventBuilder.UnixMilliseconds()` (epoch ms) | `int(time.time() * 1000)` (重新计算；无依赖) | ✅ |

**全部 12 字段对齐，0 漂移。**

注：prompt 写"11 字段"；实测 `_build_bb_payload` 返回 12 字段（ts_ms 额外生成，与 Unity 端 ts_ms 独立）。无协议冲突。

---

## §3 HTTP POST 流程验证

| 要素 | 实现 | 对齐来源 |
|:--|:--|:--|
| URL | `http://{brainHost}:{brainPort}/upload/photo/{photoId}` 默认 `127.0.0.1:7889` | `photo_upload_server._DEFAULT_HOST/_DEFAULT_PORT` |
| Method | `UnityWebRequest.kHttpVerbPOST` | FastAPI `@app.post("/upload/photo/{photo_id}")` |
| Header `Content-Type` | `image/jpeg` | `request.body()` 接收原始字节 |
| Header `X-Photo-Preview-Event-Id` | `dto.event_id`（preview EcpEvent 的 event_id） | `request.headers.get("X-Photo-Preview-Event-Id", "")` → `correlation_id` |
| Body | 全分辨率 JPEG 字节（非 base64；非 256px preview） | `body = await request.body(); path.write_bytes(body)` |
| 重试 | max 3 次 exponential backoff (1s / 2s / 4s) | async Task + Task.Delay |
| 失败处理 | `PendingPhoto.Status = Failed` + LogError；不重发 preview EcpEvent | §B.5 + §7 硬约束 |
| 成功路径 | `Status = Uploaded` + Debug.Log (bytes 数量) | `req.responseCode` |

**X-Photo-Preview-Event-Id header 必填验证**：Unity 端 `dto.event_id` 在 `EcpEventBuilder.BuildUnityEvent` 中生成（`evt_{ts12}_{rand8}` 格式）；该值作为 header 发出后，Brain 端 `photo_upload_server._publish_asset_uploaded_event(correlation_id=...)` 会把它放到 `photo.asset_uploaded` EcpEvent 的 `correlation_id` 字段，保证 cross-event 因果链。

---

## §4 Reconnect 行为决策记录

### §4.1 与 BBox/Focus 的差异

| 组件 | Reconnect 行为 | 理由 |
|:--|:--|:--|
| BBoxController / FocusController | **全量重 publish** ON 集合 | Brain `refs.bind_bbox/bind_focus` 幂等；Brain 端 dict 在 session 断开时清空 → 必须重发让 Brain 重建 refs |
| PhotoController | **不重发**已上传成功的照片 | asset 已落 Brain disk (`data/photos/{yyyy-mm-dd}/{photo_id}.jpg`)；Brain `observer/photo._upsert_photo_node` 对重复 photo_id 只 bump `interaction_count`，不会创建 duplicate；重传只浪费带宽 |

### §4.2 失败照片的 reconnect 处理

- `status=Failed` 的照片：spike 期 PhotoController 不缓存 full-res bytes（内存成本 + 复杂度不值得）→ reconnect 时只 Log.Warning，不能自动重试 HTTP POST
- Phase 5+：可在 `PendingPhoto` 中加 `byte[] fullResBytes` 缓存，reconnect 时自动重发失败的 HTTP POST

### §4.3 设计理由（防漂移）

entry doc §8.1 L8 锁定："照片双通道：preview 走 reliable DataChannel + EcpEvent；asset 走 HTTP POST → Brain 本地 cache"。Brain 本地 cache 是持久化的，reconnect 后 Brain 进程无需重新收 asset（asset 已在磁盘）。仅 preview EcpEvent 会让 Brain 知道"有这张照片"，但 reconnect 时 Brain 的 `get_l2b_graph()` 中 PhotoNode 已存在（`get_node(photo_id)` 不为 None），idempotent 路径会 skip 重建。

---

## §5 离线 Editor smoke 验证路径

1. 运行 `Tools/Parrot/Build A2 Smoke Scene` 重建 Smoke 场景（或在现有 `ParrotSmokeScene.unity` 中手动添加 `Photo` GameObject + `PhotoController` 组件）
2. Unity Play 模式
3. 选中 `Photo` GameObject → `PhotoController` 组件 ⋮ → `Debug: Capture Test Photo`

期望 Console 输出：
```
[PhotoController] DEBUG: Capture Test Photo (no candidate)
[PhotoController] photo_id=ph_xxxxxxxx preview_event_id=evt_... src=<W>x<H> jpeg_q=75 b64_bytes=<N> bbox_refs=[] focus_refs=[] candidate= sent=False
[EcpEvent:DROPPED] room not ready (event_type=photo.taken_preview event_id=evt_... bytes=<N>) wire={"schema_version":1,"event_id":"evt_...","event_type":"photo.taken_preview",...,"payload":{"schema_version":1,"photo_id":"ph_...","stage":"preview","pose":{...},...,"preview_jpeg_b64":"...",...}}
[PhotoController] HTTP POST /upload/photo/ph_xxx attempt=1/3 result=... error=... (Brain 未启动，3次失败后)
[PhotoController] HTTP POST /upload/photo/ph_xxx FAILED after 3 attempts. status=Failed.
```

如果 LiveKit 真连了（Brain + photo_upload_server 运行），期望额外看到：
```
[PhotoController] HTTP POST /upload/photo/ph_xxx → 200 bytes=12345
[EcpEvent inbound brain] event_type=photo.asset_uploaded ... payload={"photo_id":"ph_xxx","asset_ref":"/upload/photo/2026-04-30/ph_xxx.jpg","asset_bytes":12345}
```

---

## §6 256px preview 实现说明

| 要素 | 实现 |
|:--|:--|
| 抓帧路径 | `Camera.main` offscreen render → `RenderTexture` → `Texture2D.ReadPixels` |
| 缩放算法 | `Graphics.Blit(src, dstRT)` → `ReadPixels`（GPU blit，正确处理 y-flip）|
| 最长边限制 | `Mathf.Max(srcW, srcH) > 256` → `scale = 256f / maxSide` |
| JPEG 编码 | `ImageConversion.EncodeToJPG(tex, quality)` |
| Base64 | `Convert.ToBase64String(jpg)` |
| 8KB 检查 | base64 string length ≤ `EcpEventConsts.PayloadLimitBytes - 300`（300B headroom 给其他字段）|
| Quality cascade | `{previewJpegQuality, 60, 50, 40}` (Inspector 调初始值，自动降级) |
| 失败处理 | 全部档位超限 → `return null` → LogError + abort（极罕见，256px JPEG Q40 通常 <2KB）|

---

## §7 已知漂移 / Phase 5+ defer 列表

| 项 | 状态 | 触发条件 |
|:--|:--|:--|
| AR 帧抓取路径（ARCameraManager.frameReceived） | defer Phase 5+ | 真 AR 场景接 ARCameraBackground Blit → spike 期 Camera.main offscreen 已够 Editor smoke |
| failed upload bytes 缓存 + reconnect 重试 | defer Phase 5+ | 需要内存/磁盘策略评估 |
| 工具柜 prefab UI 触发集成 | defer Phase 5+ | §6.3 Q-1 defer（UI 设计完成后接 XR Hands）|
| HTTP 鉴权（Bearer token） | defer Phase 5+ | Castle 公网部署时加 |
| S3/MinIO 对象存储 | defer Phase 5+ | Castle 本地 cache 已够 |
| PhotoNode CANDIDATE_SUBJECT 真实 connect 调用 | defer Phase 5+ | EdgeKind enum 已加，Brain 端不调 |
| 全链路联机 smoke | 联机 smoke chat | `sprint4_phase4_smoke_and_gap1_chat_launch_prompt.md` |

---

## §8 硬约束遵守确认

| 约束 | 状态 |
|:--|:--|
| 不改 Brain 端任何代码 | ✅ — observer/photo / photo_upload_server / bb_schema / ecp_event.py 全未动 |
| 不改 entry doc §8 锁定项 | ✅ — 仅更新 §8.7 W8 row |
| 不改 ecp_event.py 8KB/topic/schema_version 常量 | ✅ |
| 不动 EcpEventDispatcher topic 路由 | ✅ |
| 不动 W3.A.2/A.3 / W6-7 / Animation 已落地代码 | ✅ — 只在 BBox/FocusController 加只读方法（不改业务逻辑）|
| 不发 photo.asset_uploaded EcpEvent | ✅ — 只由 Brain photo_upload_server 发 |
| preview_jpeg_b64 < 8KB pre-check | ✅ — quality cascade + base64 length 检查 |
| photo_id 格式 ph_<8 hex chars> | ✅ — `Guid.NewGuid().ToString("N").Substring(0, 8)` |
| HTTP POST 带 X-Photo-Preview-Event-Id header | ✅ — `dto.event_id` 作为值 |
| Pytest 220/220 baseline 不破坏 | ✅ — 纯 Unity C#，不触碰 Python 测试 |

---

## §9 entry doc §8.7 W8 row 更新

（本文完成后 §8.7 W8 行应从 "Unity 半 ⏳" 升级为整行 ✅）

| 周 | 内容 | 状态 |
|:--|:--|:--|
| W8 | capturePhoto + 256px preview + HTTP POST + photo.taken_preview publish | Brain 半 ✅ / Unity 半 ✅ |

---

## §10 收口签名

- 代码文件：`unity/ArSpike/Assets/Scripts/ParrotApp/Photo/PhotoController.cs`（新建）
- 改动文件：`BBoxController.cs` + `FocusController.cs`（+AppendActiveIds）+ `ParrotSmokeSceneBuilder.cs`（+Photo section）
- 测试：Unity Editor ContextMenu smoke（Brain 端 220/220 全绿不变）
- 下一步：联机 smoke + GAP-1 chat（`sprint4_phase4_smoke_and_gap1_chat_launch_prompt.md`）
