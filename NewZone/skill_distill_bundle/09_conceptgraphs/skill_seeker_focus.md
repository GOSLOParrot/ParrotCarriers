# Skill Seeker distillation focus (injected for Gemini enhance)

> **Repo:** concept-graphs/concept-graphs | **Pin:** main (2026-05-04)

Prioritize accurate coverage of these English symbols and keyword clusters when rewriting SKILL.md.
Focus is: **A10 entry gating + L2-A semantic abstraction**. Ignore SLAM/3D-reconstruction/visualization.

## §A — Entry Gating

- `filter_gobs` — frame-level detection filter (mask_area_threshold, mask_conf_threshold, skip_bg, max_bbox_area_ratio)
- `gobs_to_detection_list` — 2D gobs → 3D DetectionList with depth unprojection
- `compute_match_batch` — per-frame object association (sim_sum / sep_thresh)
- `compute_spatial_similarities` — IoU / GIoU / overlap matrix (M×N)
- `compute_visual_similarities` — CLIP cosine similarity matrix (M×N)
- `aggregate_similarities` — phys_bias weighted aggregation
- `sim_threshold`, `semantic_threshold`, `physical_threshold` — gate thresholds
- `merge_detections_to_objects` — new-node vs merge decision
- `merge_obj2_into_obj1` — in-place object merge with weighted CLIP feature average
- `filter_objects` — persistence gate (obj_min_detections, obj_min_points)
- `merge_overlap_objects` — post-hoc duplicate merge (overlap + visual + text sim)
- `pcd_denoise_dbscan` — DBSCAN noise removal on point cloud
- `gating`, `frame-level association`, `multi-frame voting`, `IoU threshold`
- `visual similarity threshold`, `cosine similarity`, `mask matching`
- `detection clustering`, `association policy`, `persistence threshold`
- `spurious detection filter`, `cross-view aggregation`, `view consistency`

## §B — CV Detection / Segmentation Stack

- `gsa_variant` — detection backbone selector (ram / tag2text / grounded_sam)
- `clip_ft` — per-mask CLIP image feature (L2-normalized, averaged across detections)
- `text_ft` — per-mask CLIP text feature from RAM tags
- `DetectionList` — list of per-frame detection dicts
- `MapObjectList` — list of 3D fused object dicts
- `compute_similarities` — `MapObjectList.compute_similarities()` for query matching
- `open-vocabulary detection`, `open-vocabulary segmentation`
- `zero-shot detection`, `mask proposal`, `dense prediction`
- `DINOv2 features`, `SAM2 mask decoder`, `YOLO-World detection`
- `RAM tagging`, `Grounded-SAM`, `Tag2Text`
- `foundation model`, `vision encoder`

## §C — ReID / Cross-Frame Association

- `re-identification`, `ReID`, `instance association`, `tracking across frames`
- `visual descriptor`, `embedding similarity`, `identity consistency`
- `appearance feature`, `feature aggregation`, `view fusion`
- `F.normalize` — L2 normalization of CLIP features after weighted average
- `contain_number`, `contain_area_thresh`, `contain_mismatch_penalty`

## §D — L2-A Semantic Abstraction

- `extract_node_captions` — per-object VLM caption generation (top-k by confidence)
- `refine_node_captions` — multi-caption → single `object_tag` via LLM
- `build_scenegraph` — compute overlap matrix → MST → LLM relation extraction
- `object_tag` — final semantic node label (output of refine step)
- `caption_dict` — per-object caption and LLM response storage
- `semantic abstraction`, `scene graph node`, `object descriptor`, `node description`
- `hierarchical class`, `affordance reasoning`, `relational edge`, `predicate extraction`
- `scene context`, `spatial relation`, `scene-level reasoning`
- `minimum_spanning_tree` — MST over overlap adjacency for edge selection
- `object_relation` — one of: "a on b", "b on a", "a in b", "b in a", "none of these"
- `DEFAULT_PROMPT` — LLM relation extraction prompt (bbox_extent + bbox_center + object_tag)

## §E — Failure Modes / Observability

- `detection failure mode`, `missed detection`, `false positive filter`
- `duplicate node prevention`, `ambiguous association`, `low-confidence gate`
- `drop reason`, `association log`
- `min_views_per_object` — prune objects with too few observations
- `invalid`, `FAIL` — LLM response failure sentinel values

## §F — Key Config Parameters (base.yaml)

- `mask_area_threshold: 25`
- `mask_conf_threshold: 0.2`
- `spatial_sim_type: iou` / `match_method: sep_thresh`
- `semantic_threshold: 0.5`, `physical_threshold: 0.5`
- `obj_min_detections: 3`
- `merge_overlap_thresh: 0.7`, `merge_visual_sim_thresh: 0.7`, `merge_text_sim_thresh: 0.7`
- `downsample_voxel_size: 0.025`

## What NOT to focus on (out of scope)

- SLAM / pose estimation / gradslam
- Open3D visualization / rendering
- Dataset loading (Replica, ScanNet, AI2Thor)
- LLaVA-specific inference code
- Benchmark numbers / evaluation metrics
- Docker / conda environment setup
