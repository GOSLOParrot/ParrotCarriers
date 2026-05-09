---
status: ratified
category: completion-report
status_note: "W8 Unity 半边全功能落地（含审计修复 ca913ac）。230/230 全绿。联机 smoke ⏳ 环境就绪后跑。"
last_reviewed: 2026-04-30
commits: "f6f3da9 (初版) + ca913ac (审计修复)"
---

# Sprint4 Phase 4 W8 Unity 半边完成报告（2026-04-30）

---

## §0 完成状态总览

| 功能点 | 状态 | 说明 |
|:--|:--|:--|
| PhotoController.cs 主体 | ✅ 完成 | 含所有 Inspector 字段 + Singleton |
| photo_id 生成 `ph_<guid8>` | ✅ 完成 | 与 BBox/Focus 命名空间隔离 |
| Camera.main 帧抓取 | ✅ 完成（spike 路径） | Editor 离线可用；AR 正式路径 Phase 5+ |
| 256px 缩放（最长边）| ✅ 完成 | GPU Blit，正确处理 Y-flip |
| JPEG quality cascade 75→60→50→40 | ✅ 完成 | Inspector 可调初始值 |
| 8KB pre-check | ✅ 完成 | base64 length ≤ PayloadLimitBytes − 300 |
| 12 字段 photo.taken_preview payload | ✅ 完成 | 与 Brain `_build_bb_payload` 逐字段对齐 |
| EcpEvent publish | ✅ 完成 | 复用 `EcpEventPublisher.Publish(dto)` |
| HTTP POST 4 次总尝试（initial + 1s/2s/4s）| ✅ 完成 | `UnityWebRequest` async/await |
| X-Photo-Preview-Event-Id header | ✅ 完成 | `dto.event_id` 作为值；Brain correlation_id 依赖 |
| PendingPhoto 状态机（Pending/Uploaded/Failed）| ✅ 完成 | |
| full-res bytes 缓存（重试用）| ✅ 完成 | 上传成功后释放（`p.FullResJpeg = null`）|
| previewSent 标记 | ✅ 完成 | 区分 preview 是否真正送达 Brain |
| preview 未送达时明确 Warning | ✅ 完成 | Brain 无 PhotoNode 时 HTTP POST 也继续但 warn |
| Reconnect — Uploaded 不重发 | ✅ 完成 | asset 已落 Brain disk |
| Reconnect — Failed + previewSent=true 重试 HTTP POST | ✅ 完成 | Brain 有 PhotoNode，只缺 asset_ref |
| Reconnect — Failed + previewSent=false 不可恢复 | ✅ 完成（log 警告）| Brain 无 PhotoNode，无法恢复 |
| BBoxController / FocusController AppendActiveIds() | ✅ 完成 | 只读方法，不改业务逻辑 |
| ParrotSmokeSceneBuilder 加 Photo 区段 | ✅ 完成 | |
| ParrotSmokeScene.unity 加挂 PhotoController | ✅ 完成 | fileID 2350000001-3，GUID 00284d5e... |
| 所有 .meta 文件入库 | ✅ 完成 | 8 个 meta 文件 |
| 3 个 ContextMenu Debug 入口 | ✅ 完成 | Capture Test Photo / With Candidate / With Active Refs |
| **AR 正式帧抓取路径** | ⏳ Phase 5+ | `ARCameraManager.frameReceived` 未接；spike 用 Camera.main |
| **工具柜 prefab UI 触发** | ⏳ Phase 5+ | 目前 ContextMenu 兜底 |
| **reconnect 失败 bytes 持久化（跨重启）** | ⏳ Phase 5+ | 当前只缓存内存，App 重启后丢失 |
| **HTTP 鉴权（Bearer token）** | ⏳ Phase 5+ | |
| **S3/MinIO 对象存储** | ⏳ Phase 5+ | 当前 Brain 本地 cache |
| **PhotoNode CANDIDATE_SUBJECT 实际建边** | ⏳ Phase 5+ | EdgeKind enum 已加，调用 defer |
| **联机 smoke 全链路验证** | ⏳ 待环境 | 详见联机 smoke 报告 |

---

## §1 新增 / 改动文件清单

### 1.1 新增文件

| 文件 | 作用 |
|:--|:--|
| `unity/ArSpike/Assets/Scripts/ParrotApp/Photo/PhotoController.cs` | W8 Unity 半边主体（~640 行） |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Photo/PhotoController.cs.meta` | GUID `00284d5e5671f9c4883e68dcc80707eb` |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Photo.meta` | Photo 目录 GUID |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Attention.meta` + 3 子 meta | Attention 目录及各文件 GUID |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Config/ParrotAttentionConfig.cs.meta` | Config GUID |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Ecp/EcpEventPublisher.cs.meta` | Ecp GUID |

### 1.2 改动文件

| 文件 | 改动内容 |
|:--|:--|
| `unity/ArSpike/Assets/Scripts/ParrotApp/Attention/BBoxController.cs` | +`AppendActiveIds(List<string>)` 只读方法 |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Attention/FocusController.cs` | 同上 |
| `unity/ArSpike/Assets/Scripts/ParrotApp/Editor/ParrotSmokeSceneBuilder.cs` | +Photo 区段，+PhotoController 挂载 |
| `unity/ArSpike/Assets/Scenes/ParrotSmokeScene.unity` | +Photo GameObject（fileID 2350000001）+ PhotoController MonoBehaviour |

---

## §2 12 字段 payload 对齐验证

与 `src/parrot/brain/observer/photo._build_bb_payload` + `bb_schema.py` 逐字段核对：

| 字段 | Unity 发送值 | Brain 读取 | 对齐 |
|:--|:--|:--|:--|
| `schema_version` | `1`（硬编码） | `_PHOTO_EVENT_SCHEMA_VERSION = 1` | ✅ |
| `photo_id` | `"ph_" + Guid.NewGuid().ToString("N")[..8]` | `payload.get("photo_id")` | ✅ |
| `stage` | `"preview"`（硬编码） | `stage="preview"` 参数 | ✅ |
| `pose` | `{"px","py","pz","qx","qy","qz","qw"}`（Camera.main） | `payload.get("pose") if isinstance(…, dict) else {}` | ✅ |
| `episode_ref` | `""` | `str(payload.get("episode_ref","") or "")` | ✅ |
| `focus_refs` | `["fc_…"]` 或 `[]` | `list(payload.get("focus_refs") or ())` | ✅ |
| `bbox_refs` | `["bb_…"]` 或 `[]` | `list(payload.get("bbox_refs") or ())` | ✅ |
| `candidate_subject_uuid` | `""` 或传入 uuid | `str(payload.get("candidate_subject_uuid","") or "")` | ✅ |
| `preview_jpeg_b64` | base64，pre-check ≤ 8KB | `str(payload.get("preview_jpeg_b64","") or "")` | ✅ |
| `asset_ref` | `""`（preview 固定空） | `""` when stage=="preview" | ✅ |
| `asset_bytes` | `0`（preview 固定零） | `0` when stage=="preview" | ✅ |
| `ts_ms` | `EcpEventBuilder.UnixMilliseconds()` | Brain 端独立重新计算 | ✅（无依赖） |

**结论：12 字段 0 漂移**。`ts_ms` 双端各自生成，无协议冲突。

---

## §3 HTTP POST 流程验证

| 要素 | 实现值 | 对齐来源 |
|:--|:--|:--|
| URL | `http://{brainHost}:{brainPort}/upload/photo/{photoId}` | `photo_upload_server._DEFAULT_HOST/PORT` |
| Method | POST | FastAPI `@app.post(...)` |
| Content-Type | `image/jpeg` | Brain 用 `request.body()` 接原始字节 |
| `X-Photo-Preview-Event-Id` | `dto.event_id`（preview EcpEvent event_id）| Brain `request.headers.get(...)` → `correlation_id` |
| Body | 全分辨率 JPEG 字节（非 base64，非 256px）| `path.write_bytes(body)` |
| 总尝试次数 | **4 次**（initial + retry 1s/2s/4s） | `retryDelaysMs = {1000,2000,4000}; attempt < 4` |
| 成功 | `Status = Uploaded`；`p.FullResJpeg = null` 释放内存 | |
| 失败（4次全败）| `Status = Failed`；LogError；不重发 preview | |

---

## §4 Reconnect 行为（当前实现，严格对照 §B.5）

| 情形 | 判断条件 | 行为 | 完成 |
|:--|:--|:--|:--|
| 已上传成功 | `Status == Uploaded` | 不重发、不 retry（asset 在 Brain disk）| ✅ |
| 上传失败 + preview 已送达 | `Status == Failed && PreviewSent == true` | `Status = Pending`；重跑 `UploadAssetAsync`（Brain 有 PhotoNode 等 asset）| ✅ |
| 上传失败 + preview 未送达 | `Status == Failed && PreviewSent == false` | LogWarning 不可恢复；不重发（Brain 无 PhotoNode 且无 preview，重 HTTP 也无意义）| ✅（log 行为）|
| 仍在上传中 | `Status == Pending` | 不干预（正在运行中的 async Task）| ✅（自然行为）|

**注意**：reconnect retry 依赖 `PendingPhoto.FullResJpeg` 内存缓存，**App 重启后丢失**。

---

## §5 离线 Editor smoke 验证（ContextMenu 路径）

### 5.1 操作步骤

1. 打开 `ParrotSmokeScene`（已含 Photo GameObject）→ Unity Play
2. Hierarchy 选 `Photo` GameObject → Inspector → PhotoController ⋮ → `Debug: Capture Test Photo`

### 5.2 期望 Console 输出（无 LiveKit 环境）

```
[PhotoController] DEBUG: Capture Test Photo (no candidate)
[PhotoController] photo_id=ph_xxxxxxxx preview_event_id=evt_... src=WxH jpeg_q=75 b64_bytes=N previewSent=False
[PhotoController] photo_id=ph_xxxxxxxx — preview EcpEvent NOT delivered. Brain will receive asset upload but PhotoNode may be missing ...
[EcpEvent:DROPPED] room not ready (event_type=photo.taken_preview ...) wire={...,"payload":{"schema_version":1,"photo_id":"ph_...","stage":"preview",...}}
[PhotoController] HTTP POST retry 1/3 in 1000ms for photo_id=ph_xxx
[PhotoController] HTTP POST retry 2/3 in 2000ms for photo_id=ph_xxx
[PhotoController] HTTP POST retry 3/3 in 4000ms for photo_id=ph_xxx
[PhotoController] HTTP POST /upload/photo/ph_xxx FAILED after 3 attempts. status=Failed.
```

### 5.3 期望输出（联机 LiveKit + Brain 运行时）

```
[PhotoController] photo_id=ph_xxx ... previewSent=True
[EcpEvent:SENT] event_type=photo.taken_preview ...
[PhotoController] HTTP POST /upload/photo/ph_xxx → 200 bytes=<fullResBytes>
[EcpEvent inbound] event_type=photo.asset_uploaded payload={"photo_id":"ph_xxx","asset_ref":"/upload/photo/.../ph_xxx.jpg","asset_bytes":N}
```

---

## §6 硬约束遵守确认

| 约束 | 状态 |
|:--|:--|
| 不发 `photo.asset_uploaded` | ✅（只由 Brain photo_upload_server 发） |
| `preview_jpeg_b64` 必 < 8KB | ✅（quality cascade + base64 pre-check） |
| HTTP POST 必带 `X-Photo-Preview-Event-Id` | ✅ |
| 不改 EcpEventPublisher / EcpEventDispatcher 业务逻辑 | ✅ |
| 不改 Brain 端任何代码 | ✅ |
| 不改 entry §8 锁定项 | ✅ |
| photo_id 格式 `ph_<8 hex>` | ✅ |
| Pytest 230/230 baseline 不破坏 | ✅ |

---

## §7 Commits

| Commit | 内容 |
|:--|:--|
| `f6f3da9` | 初版 PhotoController + BBoxController/FocusController accessor + Builder + 报告 |
| `ca913ac` | 审计修复：reconnect bytes 缓存 + 4 次重试 + previewSent 标记 + scene 加挂 + meta 入库 |
