# PhotoNode / ObjectNode / Nanobot / findObject 视觉身份链路需求与启动提示词

更新时间：2026-05-25

## 0. 结论

这条链路必须拆清楚：**照片是照片，物体是物体，裁剪样本是样本，同一物体判断是一个异步/同步可等待的后台任务**。

正确设计不是把所有信息都塞进 PhotoNode，也不是让 PhotoNode 直接变成 ObjectNode。正确链路是：

```text
PhotoNode
  -> 保存原始照片 / 渲染图 / 场景描述 / OCR / 网络调查 / Graphiti 搜索 / nanobot 照片报告索引

PhotoNode -- Edge --> ObjectNode
  -> Edge 记录这张照片和这个物体的关系、bbox、crop、证据、置信度、审核状态

ObjectNode
  -> 保存物体描述索引、物体报告索引、网络调查、Graphiti 信息、findObject 快速标签、参考图、样本索引

ObjectSample / BBox Crop
  -> 保存局部裁剪图、bbox、来源 photo_id、sample_id、审核状态、是否可导出 A10

GOSLO Intent findObject
  -> 触发 nanobot/worker 做“是否同一物体”判断
  -> GOSLO 等待结果
  -> 返回完整证据链：原图、照片描述、bbox crop、候选 ObjectNode、样本对比、判断理由
```

所以本需求的重点是：**分层存储，Edge 连接，nanobot 后台执行，GOSLO Intent 等待结果，findObject 得到完整链条**。

## 1. 不可混淆的边界

### 1.1 PhotoNode 负责照片级信息

PhotoNode 只表达“这张照片/这帧证据本身”：

- 原始图片路径、渲染图路径、预览图路径
- 场景描述：这张图大概是什么场景
- 内容摘要：画面里大概有什么
- OCR / logo / 可见文字
- 针对整张照片的网络搜索、Graphiti 搜索、资料调查
- nanobot 照片报告索引
- 照片里可能出现了哪些物体的弱提示

PhotoNode 不应该直接保存某个局部物体的最终身份，也不应该把“看起来像某个 ObjectNode”写成 confirmed。

### 1.2 ObjectNode 负责物体级信息

ObjectNode 表达“一个可被再次识别的物理物体或语义物体”：

- 物体名称、类别、描述索引字段
- findObject 快速检索标签
- 物体级网络调查、Graphiti 搜索、nanobot 物体报告索引
- 参考图片、最后一次出现图片
- 已接受的 ObjectSample 索引
- 与哪些 PhotoNode 有证据连接
- 用于同物体比较的样本图片

ObjectNode 可以有报告和网络调查，但那是物体级报告，不是照片级报告。

### 1.3 PhotoNode 和 ObjectNode 必须可以有 Edge

不要再写成“PhotoNode 和 ObjectNode 没有关系”。正确说法是：

- 当前代码已经预留 `EdgeKind.CANDIDATE_SUBJECT`、`HAS_EVIDENCE`、`HAS_PHOTO`。
- 新链路需要真正写入 PhotoNode -> ObjectNode 的 Edge。
- Edge 不是装饰，它负责保存“这张照片如何证明这个物体”的证据。

建议 Edge meta：

```json
{
  "photo_id": "",
  "object_uuid": "",
  "edge_status": "candidate|confirmed|rejected|conflicted",
  "evidence_id": "",
  "bbox": {},
  "crop_path": "",
  "sample_id": "",
  "object_ref_id": "",
  "match_confidence": 0.0,
  "match_source": "user_confirmed|nanobot_same_object|a10_reid|manual",
  "review_status": "draft|accepted|rejected|needs_review",
  "created_at_ms": 0
}
```

### 1.4 BBox / Crop / Object Discovery 是样本层，不是照片报告层

下面这些不能和 PhotoNode 的整图描述混在一起：

- BBox 裁剪
- 局部小图
- 照片中的物体发现
- 识图结果
- 判断是不是同一个 Object
- 用于 A10 的训练/检索样本

这些应该进入 `PhotoObjectIndex`、`ObjectSampleDraft`、`ObjectSampleLibrary`，再通过 Edge 连接回 PhotoNode 和 ObjectNode。

### 1.5 同一物体判断由 nanobot/worker 完成，但由 GOSLO Intent 触发并等待

`findObject` 是 GOSLO 的 Intent 行为：用户让 GOSLO 看一个东西、认一个东西、判断是不是旧物体。

但“把所有 ObjectNode、相关子图、描述索引、照片报告、样本图过一遍，再挑候选图片做 LLM/VLM 同物体比较”这件事可以由 nanobot 后台工具完成。

因此实现上应是：

```text
GOSLO identify_object / findObject Intent
-> 创建 same_object_resolver job
-> nanobot/worker 扫描 ObjectNode + 子图 + 样本库 + Photo/Graphiti 报告
-> 候选筛选
-> LLM/VLM 图像对比
-> 返回完整判断链
-> GOSLO 等待结果并自然回复
```

不要把它写成 GOSLO 自己在主对话里手工完成全部比较。

## 2. 当前代码事实

实现前必须先检查这些文件，不要重写已有链路：

- `src/parrot/brain/observer/photo.py`
  - `photo.taken_preview` 创建 `NodeKind.PHOTO` 的 PhotoNode。
  - `photo.asset_uploaded` 更新 `reference_image_path`，写 EvidenceLedger，并把 PHOTO ref stage 到 IntentWorkspace。
  - 当前不自动创建 ObjectNode。

- `src/parrot/brain/intent_workspace.py`
  - 已有 `StagedRefKind.PHOTO` / `DOC` / `RICH_REPORT`。
  - 可以 stage 照片报告、物体报告、样本草稿 manifest、nanobot 报告。

- `src/parrot/brain/vision/evidence.py`
  - `TimeAlignedSampleRef` 已支持 `asset_path`、`region`、`bbox_refs`、`focus_refs`、`meta`。
  - 适合统一索引原图、bbox 区域、crop 证据。

- `src/parrot/brain/vision/evidence_image.py`
  - `prepare_evidence_image(sample)` 已支持按 `sample.region` crop，然后转 VLM 输入。
  - 需要新增“保存 crop 文件并返回路径”的持久化函数。

- `src/parrot/brain/vision/visual_match.py`
  - `describe_image()` 能描述图像。
  - `compare_current_frame()` 能判断当前图是否和候选 reference image 是同一物理物体，但现在还没有接入主流程。

- `src/parrot/brain/tools/identify_object.py`
  - 当前 match 流程是 evidence lookup -> VLM describe -> L2-B 文本匹配 -> Graphiti 文本搜索。
  - 当前 `save_new` 不会把 evidence/crop 保存成 ObjectSample。
  - 当前还没有“GOSLO 等待 nanobot same-object job”的链路。

- `src/parrot/dsg/l2b_types.py`
  - `SemanticNode` 已有 `reference_image_path`、`last_sighting_path`、`source_meta`、`meta`。
  - `EdgeKind` 已有 `HAS_EVIDENCE`、`HAS_PHOTO`、`CANDIDATE_SUBJECT`。

- `src/parrot/dsg/ingest/cv_track_filter.py`
  - 已有 A10/CV worker skeleton，可以把 `SensorFrame.detections` 转成 `Observation`。
  - 但 A10 worker 尚未真正部署，merge 也还没按 visual/reid/sample 做身份判断。

## 3. 照片库 / 样本库路径与 UUID 绑定方案

### 3.1 调研依据

这套方案参考了几类成熟做法：

- CVAT 的 COCO 导出采用 `images/<subset>/...` 和 `annotations/instances_<subset>.json` 分离结构，并支持 bbox、mask、attributes、`track_id`。
- Datumaro 的数据集格式也采用 `images/train|val` 和 `annotations/train.json|val.json` 分离结构，适合后续转换格式。
- FiftyOne 把一张媒体文件当作 Sample，核心字段是 `filepath`、metadata、labels/detections；检测框使用 `[top-left-x, top-left-y, width, height]` 的归一化格式。
- Label Studio 的 bbox 结果按区域保存 `x/y/width/height/rotation`，还能对每个 region 单独添加文本描述和选择项。
- DVC 的 `.dvc` 文件用于追踪大文件或目录，不把大图直接塞进 Git。
- RFC 9562 定义了 UUIDv7，适合作为按时间大致有序、又能分布式生成的记录 ID。

结论：本项目内部采用“**文件资产不可变 + manifest/SQLite 作为权威索引 + 导出目录可再生成**”的模式。

### 3.2 总目录

建议所有视觉资料统一放在：

```text
data/vision/
├── catalog/
│   ├── vision_index.sqlite
│   ├── photos.jsonl
│   ├── photo_objects.jsonl
│   ├── object_samples.jsonl
│   ├── photo_object_edges.jsonl
│   └── identity_bindings.jsonl
├── photos/
│   ├── originals/{yyyy}/{mm}/{dd}/{photo_uuid}.jpg
│   ├── rendered/{yyyy}/{mm}/{dd}/{photo_uuid}_render.jpg
│   ├── thumbs/{yyyy}/{mm}/{dd}/{photo_uuid}.webp
│   └── reports/{yyyy}/{mm}/{dd}/{photo_uuid}.analysis.json
├── photo_objects/
│   └── {yyyy}/{mm}/{dd}/{photo_uuid}/{object_ref_id}.json
├── object_sample_staging/
│   └── {yyyy}/{mm}/{dd}/{photo_uuid}/{object_ref_id}/
│       ├── {sample_uuid}.jpg
│       └── manifest.json
├── object_samples/
│   └── by_object/{object_uuid[0:2]}/{object_uuid}/
│       ├── accepted/{sample_uuid}.jpg
│       ├── rejected/{sample_uuid}.jpg
│       ├── manifest.json
│       └── reports/
├── reports/
│   ├── same_object/{yyyy}/{mm}/{dd}/{job_uuid}.json
│   └── object/{object_uuid[0:2]}/{object_uuid}/{report_uuid}.json
└── exports/
    └── a10/{export_uuid}/
        ├── coco/
        │   ├── images/train/
        │   ├── images/val/
        │   └── annotations/instances_train.json
        └── yolo/
            ├── images/train/
            ├── labels/train/
            └── obj.names
```

规则：

- `photos/originals` 是不可变原始证据。不要覆盖，必要时新建新 photo_uuid。
- `rendered`、`thumbs`、`reports` 是派生物，可以重建。
- `object_sample_staging` 是用户审核前的草稿样本。
- `object_samples/by_object` 只放已经绑定到 ObjectNode 的样本。
- `exports/a10` 是可再生成的导出结果，不作为身份真相来源。
- 路径不是身份，路径只是 locator；身份以 UUID 和 manifest 为准。

### 3.3 UUID 命名规则

建议统一使用带前缀的 UUIDv7 字符串：

```text
ph_{uuid7}      PhotoNode / PhotoRecord
pobj_{uuid7}    照片中的局部物体候选 PhotoObject
os_{uuid7}      ObjectSample / ObjectSampleDraft
obj_{uuid7}     Canonical Object identity，可映射到 L2-B SemanticNode.uuid
pe_{uuid7}      PhotoNode -> ObjectNode Edge
rep_{uuid7}     nanobot / analysis report
job_{uuid7}     same-object resolver job
exp_{uuid7}     A10 export batch
```

当前代码里 `SemanticNode.uuid` 仍可能是 12 位短 ID。实现时不要强行一次性替换全系统，可以先这样兼容：

```json
{
  "canonical_uuid": "obj_...",
  "l2b_uuid": "现有 SemanticNode.uuid",
  "graphiti_entity_uuids": [],
  "ref_ids": [],
  "sample_ids": [],
  "photo_edge_ids": []
}
```

`IdentityRefIndex` 应作为 canonical identity 绑定层，而不是让文件路径、label 或 Graphiti hit 直接决定身份。

### 3.4 绑定表

最少需要这些逻辑表，可以先用 JSONL，稳定后迁到 SQLite：

`PhotoRecord`

```json
{
  "photo_uuid": "ph_...",
  "photo_node_uuid": "ph_...",
  "asset_path": "data/vision/photos/originals/...",
  "rendered_path": "",
  "thumb_path": "",
  "content_sha256": "",
  "evidence_id": "",
  "intent_workspace_ref_id": "",
  "captured_at_ms": 0,
  "width": 0,
  "height": 0,
  "photo_report_path": "",
  "status": "ready|tombstoned"
}
```

`PhotoObjectRecord`

```json
{
  "object_ref_id": "pobj_...",
  "photo_uuid": "ph_...",
  "bbox": {},
  "crop_path": "",
  "sample_draft_id": "os_...",
  "candidate_object_uuid": "",
  "edge_uuid": "",
  "review_status": "draft|accepted|rejected|needs_crop"
}
```

`ObjectSampleRecord`

```json
{
  "sample_uuid": "os_...",
  "object_uuid": "obj_...",
  "photo_uuid": "ph_...",
  "object_ref_id": "pobj_...",
  "crop_path": "",
  "source_asset_path": "",
  "bbox": {},
  "content_sha256": "",
  "visual_description": "",
  "quality_flags": [],
  "review_status": "draft|accepted|rejected|exported_to_a10"
}
```

`PhotoObjectEdgeRecord`

```json
{
  "edge_uuid": "pe_...",
  "photo_uuid": "ph_...",
  "object_uuid": "obj_...",
  "sample_uuid": "os_...",
  "evidence_id": "",
  "bbox": {},
  "crop_path": "",
  "match_confidence": 0.0,
  "match_source": "user_confirmed|nanobot_same_object|a10_reid|manual",
  "edge_status": "candidate|confirmed|rejected|conflicted"
}
```

### 3.5 管理模式

推荐状态流：

```text
PhotoRecord.ready
-> PhotoAnalysisReport.ready
-> PhotoObjectRecord.draft
-> ObjectSampleDraft.draft
-> user accepted/rejected
-> ObjectSampleRecord.accepted
-> PhotoObjectEdgeRecord.confirmed 或 candidate
-> IdentityRefIndex upsert
-> A10 export batch
```

管理规则：

- 原始图不覆盖、不删除；删除走 tombstone。
- crop 可以重新生成，但 accepted sample 不能静默覆盖。
- `content_sha256` 用于去重和完整性校验，不作为业务身份。
- `object_uuid` 只在用户确认、高置信 resolver、或已有稳定 identity 命中时写入。
- `label`、`category`、`find_tags` 只用于召回候选，不是身份。
- Graphiti / 网络搜索结果只作为 report 或 candidate facts，不直接绑定 Object UUID。
- COCO/YOLO 导出永远从 manifest 生成，不手工编辑导出目录作为源数据。
- 大文件目录可用 DVC 跟踪；Git 只跟踪 schema、轻量 manifest 或 `.dvc` 指针。

### 3.6 UUID 绑定流程

```text
1. photo.asset_uploaded
   -> 生成/读取 photo_uuid
   -> 写 PhotoRecord
   -> PhotoNode.uuid = photo_uuid 或在 IdentityRefIndex 中映射

2. 用户 BBox / VLM inventory / A10 detection
   -> 生成 object_ref_id
   -> 写 PhotoObjectRecord
   -> 保存 crop 到 object_sample_staging
   -> 生成 sample_uuid draft

3. nanobot same-object resolver
   -> 扫描 ObjectNode + object_samples + photo edges + reports
   -> 选候选
   -> 图片对比
   -> 输出 SameObjectResolutionReport

4. 结果 matched
   -> sample_uuid.object_uuid = existing object_uuid
   -> 写 PhotoObjectEdgeRecord
   -> 写 L2-B Edge
   -> 写 RefTable / IdentityRefIndex

5. 结果 new_object
   -> 生成 object_uuid
   -> 创建 ObjectNode
   -> sample accepted
   -> 写 PhotoObjectEdgeRecord
   -> 写 RefTable / IdentityRefIndex / Graphiti episode
```

## 4. 数据模型需求

### 4.1 PhotoNode 轻量扩展

不要把完整报告塞进 `SemanticNode` 顶层字段。PhotoNode 只保留轻量索引：

```json
{
  "photo_analysis": {
    "analysis_status": "pending|ready|error",
    "analysis_version": "photo_analysis_v1",
    "report_ref_id": "intent_workspace_ref",
    "report_path": "data/vision/photos/reports/{yyyy}/{mm}/{dd}/{photo_uuid}.analysis.json",
    "scene_summary": "",
    "content_summary": "",
    "web_research_ref": "",
    "graphiti_search_ref": "",
    "object_inventory_ref": "",
    "updated_at_ms": 0
  }
}
```

### 4.2 PhotoAnalysisReport

照片报告只描述整张图，不做同物体绑定。

路径建议：

```text
data/vision/photos/reports/{yyyy}/{mm}/{dd}/{photo_uuid}.analysis.json
```

字段建议：

```json
{
  "schema_version": "photo_analysis_v1",
  "photo_id": "",
  "photo_node_uuid": "",
  "asset_path": "",
  "rendered_preview_path": "",
  "evidence_id": "",
  "scene_summary": "",
  "content_summary": "",
  "ocr_text": [],
  "visible_logo_or_text": [],
  "photo_level_brand_candidates": [],
  "photo_level_web_research": [],
  "photo_level_graphiti_hits": [],
  "possible_object_mentions": [],
  "object_inventory_ref": "",
  "nanobot_report_ref_id": "",
  "nanobot_report_path": "",
  "quality_flags": [],
  "created_at_ms": 0,
  "updated_at_ms": 0
}
```

`possible_object_mentions` 只能是弱提示，例如“画面中可能有一杯奶茶”。它不能替代 ObjectNode，也不能自动创建 confirmed identity。

### 4.3 ObjectNode 轻量扩展

ObjectNode 可以有自己的描述和调查信息，但必须是物体级：

```json
{
  "object_profile": {
    "description_index": "",
    "find_tags": ["milk tea", "cup", "white label"],
    "visual_aliases": [],
    "object_report_ref_ids": [],
    "object_report_paths": [],
    "web_research_ref": "",
    "graphiti_search_ref": "",
    "sample_index_ref": "data/vision/object_samples/by_object/{object_uuid[0:2]}/{object_uuid}/manifest.json",
    "primary_sample_id": "",
    "photo_edge_refs": [],
    "updated_at_ms": 0
  }
}
```

这里的 `find_tags` 是 findObject 的快速筛选字段，不是最终身份。最终身份仍要看 sample、edge、用户确认、Graphiti/IdentityRefIndex。

### 4.4 PhotoObjectIndex

一张照片可以发现多个局部物体。它们是“照片中的候选物体”，不是最终 ObjectNode。

```json
{
  "object_ref_id": "pobj_{photo_id}_{index}",
  "photo_id": "",
  "bbox": {
    "x": 0.0,
    "y": 0.0,
    "width": 0.0,
    "height": 0.0,
    "coordinate_space": "normalized|pixel"
  },
  "crop_path": "data/vision/object_sample_staging/{yyyy}/{mm}/{dd}/{photo_uuid}/{object_ref_id}/{sample_uuid}.jpg",
  "label_guess": "",
  "category_guess": "",
  "visual_description": "",
  "distinctive_features": [],
  "text_or_logo": [],
  "brand_candidates": [],
  "candidate_object_uuid": "",
  "photo_object_edge_id": "",
  "match_candidates": [],
  "confidence": 0.0,
  "source": "user_bbox|vlm_inventory|a10_detection|manual",
  "review_status": "draft|accepted|rejected|needs_crop|exported_to_a10"
}
```

### 4.5 ObjectSampleDraft / ObjectSample

样本库存的是可比对的小图或参考图。

路径建议：

```text
data/vision/object_sample_staging/{yyyy}/{mm}/{dd}/{photo_uuid}/{object_ref_id}/{sample_uuid}.jpg
data/vision/object_sample_staging/{yyyy}/{mm}/{dd}/{photo_uuid}/{object_ref_id}/manifest.json
data/vision/object_samples/by_object/{object_uuid[0:2]}/{object_uuid}/accepted/{sample_uuid}.jpg
data/vision/object_samples/by_object/{object_uuid[0:2]}/{object_uuid}/manifest.json
```

字段建议：

```json
{
  "sample_id": "os_{uuid}",
  "object_uuid": "",
  "photo_id": "",
  "object_ref_id": "",
  "evidence_id": "",
  "source_asset_path": "",
  "crop_path": "",
  "bbox": {},
  "label": "",
  "category": "",
  "visual_description": "",
  "distinctive_features": [],
  "brand_or_model": "",
  "quality_flags": [],
  "review_status": "draft|accepted|rejected|needs_label|exported_to_a10",
  "created_by": "nanobot|user|a10|identify_object",
  "created_at_ms": 0
}
```

## 5. 固定工作流

### Workflow A: Photo-Level Enrichment

目标：只补充 PhotoNode 的整图信息。

触发条件：

- `photo.asset_uploaded`
- IntentWorkspace 中存在 active PHOTO ref 且未分析
- 定时 nanobot worker 扫描 pending PhotoNode

步骤：

1. 读取 PhotoNode 和 PHOTO staged ref。
2. 找到 `TimeAlignedSampleRef` / `asset_path`。
3. 对整张图做 VLM 场景分析。
4. 如有可见文字、logo、包装，再进行网络搜索或 Graphiti 搜索。
5. 生成 `PhotoAnalysisReport`。
6. 把报告 stage 到 IntentWorkspace。
7. 在 PhotoNode `meta["photo_analysis"]` 写轻量摘要和 report path。

禁止事项：

- 不在这个 workflow 中确认 Object UUID。
- 不在这个 workflow 中把 bbox crop 当成 accepted sample。
- 不把网络搜索结果写成 confirmed object identity。

### Workflow B: Object Candidate / BBox Crop / Sample Draft

目标：从照片中形成可审核的局部物体样本。

触发条件：

- 用户画 BBox / MAG。
- PhotoAnalysisReport 建议某区域需要框选。
- A10/CV worker 返回 detection。

步骤：

1. 根据 bbox 生成 `SampleRegion`。
2. 保存 crop 小图到 `object_sample_staging`。
3. 对 crop 小图做 VLM 描述，生成物体级 `visual_description`。
4. 创建 `PhotoObjectIndex` 条目。
5. 创建 `ObjectSampleDraft`。
6. 如果已有候选 ObjectNode，只写 candidate edge，不自动 confirmed。
7. stage 到 IntentWorkspace，供用户筛选、改名、接受、拒绝。

关键要求：

- 同一张照片多个物体必须有多个 `object_ref_id`。
- 每个 crop 必须能追溯到 `photo_id`、`evidence_id`、原图路径、bbox。
- 遮挡、模糊、太小的 crop 默认不能进 accepted sample。

### Workflow C: Nanobot Same-Object Resolver

目标：后台判断“这个 crop/当前 evidence 是否是某个已有 ObjectNode”。

这个 workflow 是 nanobot/worker 工具，不是 GOSLO 主对话自己手动跑。GOSLO 通过 Intent 触发并等待结果。

输入：

- 当前 evidence/crop/sample
- description/category hint
- bbox_ref_id/focus_ref_id/target_time_ms
- 可选 photo_id/object_ref_id

处理步骤：

1. 读取所有 ObjectNode。
2. 读取每个 ObjectNode 的相关子图：
   - ObjectNode 描述索引
   - find_tags
   - reference_image_path
   - ObjectSample manifest
   - 与该 ObjectNode 相连的 PhotoNode Edge
   - 物体级 nanobot 报告
   - Graphiti/IdentityRefIndex 信息
3. 先用文本和标签筛出描述相近的候选。
4. 再读取候选样本图，用 `visual_match.compare_current_frame()` 做同物体比较。
5. 生成 `SameObjectResolutionReport`。
6. 返回给 GOSLO 完整链条。

输出必须包含：

```json
{
  "status": "matched|new_object|ambiguous|no_evidence|error",
  "target_evidence_id": "",
  "target_photo_id": "",
  "target_crop_path": "",
  "photo_report_path": "",
  "best_object_uuid": "",
  "best_confidence": 0.0,
  "candidate_objects": [],
  "compared_samples": [],
  "reasoning_summary": "",
  "recommended_action": "bind_existing|ask_user|save_new|need_better_crop"
}
```

阈值建议：

- `confidence >= 0.75` 且候选唯一：strong suggested match，可等待用户确认或在高权限路径绑定。
- `0.55 <= confidence < 0.75`：只返回候选，不自动绑定。
- 多个相近候选：必须让用户选择。

### Workflow D: GOSLO findObject Intent Integration

目标：`identify_object` / findObject 不是自己完成全部判断，而是触发并等待 nanobot same-object resolver。

建议流程：

```text
GOSLO receives user intent
-> identify_object resolves current evidence/crop
-> create SameObjectResolver job
-> wait for nanobot result within budget or async wait policy
-> result matched: call _on_match and return natural reply
-> result ambiguous: return candidates and ask user
-> result new_object: offer save_new or directly save_new when user asked to remember
```

命中后：

- 更新 ObjectNode `last_sighting_path`。
- 如缺少 `reference_image_path`，写入 accepted sample path。
- 写 L1.5 RefTable。
- 写 IdentityRefIndex。
- 写 PhotoNode -> ObjectNode Edge。
- 返回给 GOSLO 完整证据链，包括原图、照片描述、crop、样本对比和判断理由。

### Workflow E: save_new With Evidence

当前 `identify_object(action="save_new")` 需要升级。

新增参数或内部传递：

- `evidence_id`
- `bbox_ref_id`
- `focus_ref_id`
- `target_time_ms`
- `photo_id`
- `object_ref_id`

保存新物体时：

1. 如果有 evidence/crop，创建 accepted ObjectSample。
2. 创建或更新 ObjectNode。
3. `ObjectNode.reference_image_path = sample.crop_path or evidence.asset_path`。
4. `ObjectNode.last_sighting_path = evidence.asset_path`。
5. 写 ObjectNode `meta["object_profile"]`。
6. 写 PhotoNode -> ObjectNode Edge。
7. 绑定 PHOTO_PATH / sample ref。
8. 写 IdentityRefIndex。
9. 写 Graphiti episode，但品牌/型号/网络搜索只作为候选事实，除非来源明确或用户确认。

### Workflow F: A10 Export / Import

A10/CV worker 需要样本库和 manifest，不需要自然语言报告本身。

导出格式：

- COCO export：保留 bbox、category、attributes、track_id、sample_id、object_uuid。
- YOLO export：导出 `images/`、`labels/`、`obj.names`，bbox 用相对 `cx cy w h`。
- 内部 manifest：保留 object_uuid、photo_id、crop_path、quality_flags、review_status、source。

导入 A10 结果时：

1. A10 输出 `SensorFrame` / `Detection`。
2. `Detection.meta` 带 `sample_id`、`candidate_object_uuid`、`visual_similarity`、`clip_score`、`dino_score`。
3. `CvTrackFilter` 转成 Observation。
4. identity resolver 优先按 `candidate_object_uuid` / `reid_hash` / `sample_id` 合并，再退回 label/kind。

## 6. 后端缺陷清单

必须承认并修：

1. PhotoNode 当前主要绑定照片证据，还没有稳定写 PhotoNode -> ObjectNode Edge。
2. 照片级报告、物体级报告、BBox sample、same-object 判断还没拆成独立模块。
3. `identify_object.save_new` 没有把当前 evidence/crop 保存成 ObjectSample。
4. `visual_match.compare_current_frame()` 已存在但未接入 same-object resolver。
5. 没有 `ObjectSampleLibrary` / manifest / 用户审核状态。
6. BBox crop 现在能作为 VLM 输入，但缺少保存 crop 文件并索引的持久化工具。
7. `CvTrackFilter` 只是 skeleton，A10 结果还没有稳定 merge 策略。
8. `IngestRunner` 现在按 label/kind 合并，容易把同类不同实例误合并。
9. `IdentityRefIndex` 存在但未接入 photo/findObject 流程。
10. GOSLO Intent 还没有“触发 nanobot same-object job 并等待结果”的正式链路。

## 7. 验收标准

最小闭环验收：

1. 上传一张照片后，PhotoNode 被创建，asset_path 写入，EvidenceLedger 有 IMAGE_ASSET。
2. nanobot worker 能生成照片级 `PhotoAnalysisReport`，并 stage 到 IntentWorkspace。
3. PhotoAnalysisReport 不直接 confirmed ObjectNode。
4. 一张照片中可以产生多个 `PhotoObjectIndex` 条目。
5. 每个 bbox 可以保存 crop 小图，并生成 `ObjectSampleDraft`。
6. 用户接受一个 draft 后，它进入 `object_samples/by_object/{object_uuid[0:2]}/{object_uuid}`。
7. PhotoNode 和 ObjectNode 之间可以写 Edge，Edge meta 记录 bbox/crop/sample/evidence/review_status。
8. `identify_object(match)` 会触发/等待 nanobot same-object resolver。
9. same-object resolver 会扫描 ObjectNode、相关子图、描述索引、样本图，再做 VLM 图像对比。
10. 返回给 GOSLO 的结果包含原图、照片描述、crop、候选 ObjectNode、样本对比和判断理由。
11. `identify_object(save_new)` 能带当前 evidence 创建 ObjectNode、reference sample 和 PhotoNode Edge。
12. 低置信度、多候选、模糊 crop 不自动绑定 Object UUID。
13. 可以导出 COCO / YOLO 结构，至少包含图片、bbox、label、object_uuid 映射。
14. 有单元测试覆盖 photo report、object report、bbox crop、manifest idempotency、save_new with evidence、same-object resolver gating、A10 export。

## 8. 给另一个 Chat 的启动提示词

```text
你在 D:\GOSLOParrot\ParrotCarriers 工作。请实现 PhotoNode / ObjectNode / nanobot / findObject 的视觉身份链路。重点不是把所有信息塞到一个节点里，而是拆清楚：

1. PhotoNode：保存照片级信息。
   包括原始图/渲染图、场景描述、整图内容摘要、OCR/logo、网络搜索、Graphiti 搜索、nanobot 照片报告索引。

2. ObjectNode：保存物体级信息。
   包括物体描述索引、findObject 快速标签、物体级网络调查、Graphiti 信息、nanobot 物体报告索引、参考图、样本索引、与 PhotoNode 的证据 Edge。

3. PhotoNode -> ObjectNode Edge：保存这张照片如何证明这个物体。
   Edge meta 要包含 photo_id、object_uuid、bbox、crop_path、evidence_id、sample_id、match_confidence、review_status、match_source。

4. ObjectSample / BBox Crop：保存局部物体样本。
   BBox 裁剪、照片物体发现、识图、同一物体判断，不能混入 PhotoNode 的整图报告。它们应进入 PhotoObjectIndex、ObjectSampleDraft、ObjectSampleLibrary。

5. GOSLO findObject 是 Intent 行为。
   但是判断“是否同一物体”的重任务由 nanobot/worker 工具执行。GOSLO 触发任务并等待结果，拿到完整链条后再回复用户。

请先阅读并遵守这些项目技能/架构边界：
- .cursor/skills/nanobot/SKILL.md
- .cursor/skills/nanobot-overview/SKILL.md
- .cursor/skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md
- .cursor/skills/dsg-l2b-node-organization-options/SKILL.md
- .cursor/skills/sva-vision-agents/SKILL.md
- .cursor/skills/graphiti/SKILL.md

必须先检查这些现有代码，不要重写已有链路：
- src/parrot/brain/observer/photo.py
- src/parrot/brain/intent_workspace.py
- src/parrot/brain/vision/evidence.py
- src/parrot/brain/vision/evidence_image.py
- src/parrot/brain/vision/visual_match.py
- src/parrot/brain/tools/identify_object.py
- src/parrot/dsg/l2b_types.py
- src/parrot/dsg/l2b_graph.py
- src/parrot/dsg/l1_5/ref_table.py
- src/parrot/dsg/identity_ref_index.py
- src/parrot/dsg/ingest/cv_track_filter.py
- src/parrot/dsg/ingest/runner.py

实现目标：
1. 新增 PhotoAnalysisReport 持久化结构，只处理照片级信息，不做 Object UUID confirmed。
2. 新增 ObjectNode object_profile 轻量索引字段，放在 node.meta["object_profile"]，包括 description_index、find_tags、object_report_refs、sample_index_ref、photo_edge_refs。
3. 新增 PhotoObjectIndex / ObjectSampleDraft / ObjectSampleLibrary，路径放在 data/vision/photos/reports、data/vision/object_sample_staging、data/vision/object_samples。
4. 新增 PhotoNode -> ObjectNode Edge 写入工具。Edge meta 必须记录 bbox/crop/sample/evidence/review_status/match_source。
5. 新增 bbox crop 持久化工具：基于 TimeAlignedSampleRef.region 或显式 bbox，把局部区域保存为 crop_path，并记录 photo_id、evidence_id、bbox、source。
6. 新增 nanobot same-object resolver：
   - 输入当前 evidence/crop/sample。
   - 扫描所有 ObjectNode。
   - 读取相关子图、描述索引、find_tags、ObjectSample manifest、PhotoNode Edge、Graphiti/IdentityRefIndex 信息。
   - 先筛描述相似候选，再调用 parrot.brain.vision.visual_match.compare_current_frame 对候选图片做同物体判断。
   - 输出 SameObjectResolutionReport，包含原图、照片描述、crop、候选 ObjectNode、样本对比、判断理由和 recommended_action。
7. 升级 identify_object / findObject：
   - 它是 GOSLO Intent 行为。
   - 它应解析当前 evidence/crop，然后触发 nanobot same-object resolver 并等待结果。
   - 命中后再调用 _on_match，写 ObjectNode、RefTable、IdentityRefIndex、PhotoNode Edge。
   - 模糊、多候选、低置信度时只返回候选给用户确认。
8. 升级 identify_object(action="save_new")：
   - 支持 evidence_id/bbox_ref_id/focus_ref_id/target_time_ms/photo_id/object_ref_id。
   - 有 evidence/crop 时保存 accepted sample。
   - 写 ObjectNode.reference_image_path、last_sighting_path、object_profile。
   - 写 PhotoNode -> ObjectNode Edge。
   - 绑定 RefTable，并尽量接入 IdentityRefIndex。
9. 增加用户审核状态：draft / accepted / rejected / needs_crop / exported_to_a10。未 accepted 的样本不能进入 findObject 强匹配候选。
10. 增加 COCO / YOLO export helper，保留 object_uuid、photo_id、sample_id、bbox、label 映射，供后续 A10/CV worker 使用。
11. 写测试覆盖：photo report idempotency、object profile、photo-object edge、bbox crop、multi-object photo、save_new with evidence、same-object resolver candidate gating、A10 export。

实现顺序建议：
Phase 0：先实现 data/vision 路径、UUIDv7 前缀、manifest/SQLite 索引和 IdentityRefIndex 映射，不要先写业务判断。
Phase 1：PhotoAnalysisReport 与 ObjectNode object_profile schema。
Phase 2：ObjectSampleLibrary + bbox crop 持久化 + manifest 测试。
Phase 3：PhotoNode -> ObjectNode Edge 写入。
Phase 4：nanobot same-object resolver。
Phase 5：identify_object/findObject 等待 resolver 结果，并写 RefTable/IdentityRefIndex/Edge。
Phase 6：COCO/YOLO export + CvTrackFilter merge hint。

边界：
- 不要把图片 bytes 放进 ECP/RPC。
- 不要用文件路径、label、Graphiti hit 直接当身份；路径是 locator，UUID/IdentityRefIndex 才是身份绑定。
- 不要把 PhotoNode 的照片级场景报告和 ObjectNode 的物体级报告混在一起。
- 不要把 BBox crop / ObjectSample / same-object 判断塞进 PhotoAnalysisReport。
- 不要让 nanobot 直接自动 confirmed Object UUID，除非走明确的高置信策略或用户确认。
- 不要把 label/kind 当成稳定身份。
- 不要破坏当前 PhotoNode “照片不是物体”的边界，但要实现 PhotoNode -> ObjectNode Edge。
- 不要删除现有 defense docs；本任务只改后端和必要测试。
```

## 9. 答辩口径

答辩里可以说：

> 当前系统把照片和物体分开建模。照片进入 PhotoNode，保存原图、场景描述、OCR、网络调查和 nanobot 照片报告；物体进入 ObjectNode，保存物体描述索引、参考图、样本索引和物体级报告。它们之间通过 Edge 连接，Edge 记录这张照片里哪个区域、哪张裁剪图、哪条证据指向了哪个物体。  
>  
> findObject 是 GOSLO 的 Intent 行为，但真正的同物体判断可以交给后台 nanobot worker 完成。它会扫描已有 ObjectNode、相关子图和样本库，先筛出描述相似的候选，再用 LLM/VLM 对图片做同物体比较。GOSLO 等待结果后，拿到包括原图、照片描述、crop、候选物体和判断理由在内的一整条证据链，再决定是绑定旧物体、询问用户，还是保存为新物体。
