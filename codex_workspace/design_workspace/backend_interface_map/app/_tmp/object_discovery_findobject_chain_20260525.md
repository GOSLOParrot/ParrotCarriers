# Object Discovery / findObject Chain Implementation Note

Date: 2026-05-25

## Scope Implemented

This pass upgrades the visual identity chain from "BBox/MAG evidence only" to a
real object-discovery starter path:

1. Photo uploads still create/update `NodeKind.PHOTO` only.
2. `photo.asset_uploaded` now mirrors the asset into `data/vision/catalog/photos.jsonl`.
3. BBox `confirm` / `explicit_send` with a stored asset now creates:
   - `PhotoObjectRecord` in `photo_objects.jsonl`
   - `ObjectSampleRecord` draft in `object_samples.jsonl`
   - a staged crop/manifest under `data/vision/object_sample_staging/...`
   - an IntentWorkspace `RICH_REPORT` ref with role `object_sample_draft`
4. `identify_object(action="save_new")` now accepts current evidence args:
   - `evidence_id`
   - `bbox_ref_id`
   - `focus_ref_id`
   - `target_time_ms`
   - `photo_id`
   - `object_ref_id`
5. `save_new` promotes the evidence/draft to an accepted ObjectSample:
   - copies the sample into `data/vision/object_samples/by_object/.../accepted/`
   - writes object sample manifest
   - updates `ObjectNode.reference_image_path` and `last_sighting_path`
   - writes `PhotoObjectEdgeRecord`
   - writes a L2-B `PhotoNode -> ObjectNode` `CANDIDATE_SUBJECT` edge when both nodes exist
   - binds the accepted sample into L1.5 RefTable
   - writes MemoryIdentityRefIndex JSON when available
6. `identify_object(action="match")` now waits on a same-object resolver before
   the old L0/L1 text paths:
   - scans existing `ObjectNode`s plus accepted object samples
   - compares storage-backed target/reference images through `visual_match`
   - writes a `SameObjectResolutionReport` under `data/vision/reports/same_object/...`
   - short-circuits to the existing matched side-effect path when confidence is strong
7. `photo.asset_uploaded` now creates a photo-level `PhotoAnalysisReport`:
   - writes `data/vision/photos/reports/.../{photo_uuid}.analysis.json`
   - stages the report as `StagedRefKind.RICH_REPORT` with role `photo_analysis_report`
   - updates `PhotoNode.meta["photo_analysis"]` with lightweight report pointers
   - keeps the report photo-level only; no ObjectNode or accepted sample is created
8. Accepted samples can now be exported for A10/CV training/import work:
   - writes `data/vision/exports/a10/{export_uuid}/manifest.json`
   - writes COCO `annotations/instances_train.json` plus copied sample crops
   - writes YOLO `images/train`, `labels/train`, and `obj.names`
   - preserves `object_uuid`, `photo_uuid`, `object_ref_id`, `sample_uuid`, source bbox, quality flags, and review status
9. Accepted samples now also create an object-level report/index:
   - writes `data/vision/reports/object/{object_uuid[0:2]}/{object_uuid}/{report_uuid}.json`
   - stages the report as `StagedRefKind.RICH_REPORT` with role `object_analysis_report`
   - updates `ObjectNode.meta["object_profile"].object_report_paths/ref_ids`
   - summarizes accepted samples and PhotoNode -> ObjectNode evidence edges without mutating identity
10. A10/CV detections can now be imported as reviewable sample drafts:
   - reads storage-backed `SensorFrame.frame_ref`
   - converts detection bbox to `TimeAlignedSampleRef.region`
   - writes `PhotoObjectRecord` + `ObjectSampleRecord` draft with source `a10_detection`
   - stages the draft manifest into IntentWorkspace with role `object_sample_draft`
   - skips detections without bbox and never auto-accepts or auto-merges identity
11. Review rejection now has an explicit helper:
   - `reject_object_sample_draft(...)` appends newer `rejected` rows for the same PhotoObject/ObjectSample ids
   - patches the staging manifest with review metadata
   - keeps the original draft rows as audit trail
   - does not delete crops, write ObjectNodes, write L2-B edges, or bind IdentityRefIndex

## Boundary Decisions

- PhotoNode is still not ObjectNode.
- BBox/MAG image bytes remain HTTP/storage only, never ECP/RPC inline bytes.
- BBox draft samples are not accepted object identity.
- Automatic `identify_object(match)` can record a candidate sample/edge, but it does not promote a sample to accepted.
- Accepted sample promotion happens on the explicit `save_new` path.
- If App does not provide `photo_id`, the sample is still recorded, but the PhotoNode edge is deferred until a photo UUID is available.
- The same-object resolver is worker-compatible and report-driven, but V1 runs
  in-process so GOSLO can wait for a bounded answer without introducing the full
  nanobot runtime yet.
- PhotoAnalysisReport V1 is a storage-backed whole-photo report/index. It can
  hint at bbox/focus refs from the photo payload, but those hints do not become
  object identity.
- A10 exports are derived artifacts generated from accepted ObjectSample
  manifests. Export directories are not identity truth and do not mutate sample
  review status in V1.
- ObjectAnalysisReport V1 is an index/report over already accepted evidence.
  It does not promote drafts, create ObjectNodes, or decide same-object identity.
- A10 import V1 is candidate/draft-only. `CvTrackFilter` remains a pure
  Observation filter; crop persistence and catalog writes live in the vision
  object-discovery layer.
- ObjectSample drafts are staged to IntentWorkspace as reviewable report refs.
  This is UI/review plumbing only; it does not accept or bind object identity.
- Rejection is append-only review state. It makes the latest draft state
  `rejected` and keeps the original draft record/crop for traceability.

## Files Added / Changed

- `src/parrot/brain/vision/object_discovery.py`
  - catalog records, UUID prefixes (`uuid7` when the runtime supports it, `uuid4` fallback), JSONL persistence, sample staging, IntentWorkspace draft refs, draft rejection, accepted sample promotion, edge writing.
- `src/parrot/brain/vision/evidence_image.py`
  - `persist_evidence_crop(...)`.
- `src/parrot/brain/vision/tool_lifecycle.py`
  - BBox confirm/explicit_send calls object-discovery draft writer.
- `src/parrot/brain/observer/photo.py`
  - photo asset upload mirrors into the vision catalog and creates a photo analysis report.
- `src/parrot/brain/vision/photo_analysis.py`
  - photo-level report file, IntentWorkspace report staging, and PhotoNode meta pointer update.
- `src/parrot/brain/vision/a10_export.py`
  - accepted-sample-only COCO/YOLO export helper and export manifest.
- `src/parrot/brain/vision/a10_import.py`
  - storage-backed `SensorFrame` detection to PhotoObject/ObjectSample draft helper.
- `src/parrot/brain/vision/object_analysis.py`
  - object-level report/index over accepted samples and photo-object edges.
- `src/parrot/brain/tools/identify_object.py`
  - `save_new` accepts evidence/photo/object refs and promotes accepted samples.
  - `match` waits on `same_object_resolver` before falling back to L0/L1.
- `src/parrot/brain/vision/same_object_resolver.py`
  - storage-backed same-object candidate scan, visual comparison, and report persistence.
- `tests/test_brain/test_object_discovery_catalog.py`
  - draft, rejection, accepted sample, edge, identity binding, A10 export/import, and save_new coverage.
- `tests/test_brain/test_same_object_resolver.py`
  - accepted sample matching and identify_object short-circuit coverage.
- `tests/test_brain/test_visual_tool_lifecycle.py`
  - BBox asset confirm creates object-discovery draft.

## Remaining Gaps

1. External nanobot/background queue wrapper is still not implemented; the core
   resolver is ready for that worker shape.
2. A10 result import exists as draft-only; CvTrackFilter merge policy is still not implemented.
3. App should pass `photo_id` when a BBox sample is meant to bind to a specific
   PhotoNode; without it, the backend records an unbound sample draft.
4. Resolver `matched` currently routes through the existing match side effects
   and candidate evidence recording; automatic accepted-sample promotion still
   requires the explicit `save_new`/user-confirmed path.

## Tests Run

```text
uv run pytest tests\test_brain\test_object_discovery_catalog.py -q
uv run pytest tests\test_brain\test_visual_tool_lifecycle.py -q
uv run pytest tests\test_ecp_event\test_w8_observer_photo.py tests\test_ecp_event\test_w8_photo_upload_server.py -q
uv run pytest tests\test_ecp_event\test_identify_object.py -q
uv run pytest tests\test_brain\test_time_aligned_evidence.py tests\test_brain\test_evidence_awareness_context_injector.py -q
uv run pytest tests\test_brain\test_same_object_resolver.py tests\test_brain\test_object_discovery_catalog.py tests\test_brain\test_visual_tool_lifecycle.py tests\test_ecp_event\test_identify_object.py -q
uv run pytest tests\test_ecp_event\test_w8_observer_photo.py tests\test_ecp_event\test_w8_photo_upload_server.py tests\test_brain\test_time_aligned_evidence.py tests\test_brain\test_evidence_awareness_context_injector.py -q
uv run pytest tests\test_ecp_event\test_w8_observer_photo.py -q
uv run pytest tests\test_brain\test_same_object_resolver.py tests\test_brain\test_object_discovery_catalog.py tests\test_brain\test_visual_tool_lifecycle.py tests\test_ecp_event\test_identify_object.py tests\test_ecp_event\test_w8_photo_upload_server.py tests\test_brain\test_time_aligned_evidence.py tests\test_brain\test_evidence_awareness_context_injector.py -q
uv run pytest tests\test_brain\test_object_discovery_catalog.py -q
uv run pytest tests\test_brain\test_object_discovery_catalog.py -q
uv run pytest tests\test_brain\test_object_discovery_catalog.py -q
```
