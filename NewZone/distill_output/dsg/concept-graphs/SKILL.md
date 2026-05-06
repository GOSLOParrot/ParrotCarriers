# ConceptGraphs: Open-Vocabulary 3D Scene Graphs for Perception and Planning

This documentation describes the `concept-graphs` skill, designed for local codebase analysis of the `cg-clone` project. It provides detailed insights into the architecture, design patterns, and operational procedures for generating open-vocabulary 3D scene graphs from RGB-D data.

The `concept-graphs` skill enables robust analysis of 3D scenes by integrating cutting-edge vision models (like SAM, YOLO-World, CLIP, LLaVA) with a 3D mapping pipeline. It focuses on identifying, tracking, and semantically describing objects within a scene, ultimately building a rich, relational scene graph.

## Table of Contents
1.  [Description](#description)
2.  [When to Use This Skill](#when-to-use-this-skill)
3.  [Key Concepts](#key-concepts)
    *   [A. Entry Gating and Object Association](#a-entry-gating-and-object-association)
    *   [B. Computer Vision Detection & Segmentation](#b-computer-vision-detection--segmentation)
    *   [C. Re-Identification and Cross-Frame Association](#c-re-identification-and-cross-frame-association)
    *   [D. L2-A Semantic Abstraction & Scene Graph Generation](#d-l2-a-semantic-abstraction--scene-graph-generation)
4.  [⚡ Quick Reference](#-quick-reference)
5.  [⚙️ Configuration Patterns](#️-configuration-patterns)
6.  [📖 Project Documentation](#-project-documentation)
7.  [📚 Available References](#-available-references)
8.  [Practical Usage Guidance for Gemini](#practical-usage-guidance-for-gemini)

## Description

The `concept-graphs` skill facilitates local codebase analysis for `cg-clone`, a project focused on generating open-vocabulary 3D scene graphs. This skill provides documentation and analysis generated directly from the source code, helping users understand and interact with the `concept-graphs` framework.

**Path:** `C:\Users\Bin\AppData\Local\Temp\cg-clone`
**Files Analyzed:** 0
**Languages:** Python
**Analysis Depth:** Surface

**Analysis Performed:**
- ✅ API Reference (C2.5)
- ✅ Dependency Graph (C2.6)
- ✅ Design Patterns (C3.1)
- ✅ Test Examples (C3.2)
- ✅ Configuration Patterns (C3.4)
- ✅ Architectural Analysis (C3.7)
- ✅ Project Documentation (C3.9)

## When to Use This Skill

Use this skill when you need to:
- Understand the codebase architecture and design patterns for 3D scene graph generation.
- Find implementation examples and usage patterns for object detection, mapping, and semantic abstraction.
- Review API documentation extracted from the `concept-graphs` code.
- Check configuration patterns and best practices for running the pipeline.
- Explore test examples and real-world usage of ConceptGraphs.
- Navigate the codebase structure efficiently, especially regarding object-level processing.

## Key Concepts

This section outlines the core technical concepts and mechanisms within the `concept-graphs` codebase, prioritized by their importance in object processing and scene graph generation.

### A. Entry Gating and Object Association

Entry gating refers to the process of filtering, associating, and merging 2D detections into coherent 3D objects over multiple frames. It ensures that only robust and consistent object observations contribute to the final 3D map.

*   **`filter_gobs`**: Filters frame-level 2D detections based on criteria like mask area, confidence, background skipping, and bounding box ratios. This is the first line of defense against spurious detections.
*   **`gobs_to_detection_list`**: Converts raw 2D detections (gobs) into `DetectionList` objects, incorporating depth information for 3D unprojection.
*   **`compute_match_batch`**: The primary mechanism for per-frame object association, determining if a new 2D detection corresponds to an existing 3D `MapObject`. This uses methods like `sim_sum` or `sep_thresh`.
*   **`compute_spatial_similarities`**: Calculates geometric overlap between masks (e.g., IoU, GIoU) to assess spatial correspondence.
*   **`compute_visual_similarities`**: Computes semantic similarity between object features, typically using CLIP cosine similarity, to link objects across views or frames.
*   **`aggregate_similarities`**: Combines spatial and visual similarities, often weighted by a `phys_bias`, to make a robust association decision.
*   **`sim_threshold`, `semantic_threshold`, `physical_threshold`**: Critical thresholds that gate the association and merging process, controlling the strictness of matching.
*   **`merge_detections_to_objects`**: Decides whether a new detection should create a new 3D `MapObject` or be merged into an existing one.
*   **`merge_obj2_into_obj1`**: Performs an in-place merge of two `MapObject` instances, typically by weighting and averaging their CLIP features and combining point clouds.
*   **`filter_objects`**: A post-processing step that removes objects that do not meet persistence criteria, such as `obj_min_detections` (minimum number of observations) or `obj_min_points` (minimum points in the fused point cloud).
*   **`merge_overlap_objects`**: A post-hoc merging strategy for duplicate 3D objects based on combined overlap, visual, and text similarities.
*   **`pcd_denoise_dbscan`**: Applies DBSCAN clustering for noise removal on the aggregated point clouds of 3D objects.
*   **Key Terms**: `gating`, `frame-level association`, `multi-frame voting`, `IoU threshold`, `visual similarity threshold`, `cosine similarity`, `mask matching`, `detection clustering`, `association policy`, `persistence threshold`, `spurious detection filter`, `cross-view aggregation`, `view consistency`.

### B. Computer Vision Detection & Segmentation

This component handles the initial 2D object detection and segmentation from RGB-D frames, generating masks and extracting features crucial for 3D mapping and semantic understanding.

*   **`gsa_variant`**: A configuration parameter that selects the underlying 2D detection and segmentation backbone (e.g., `ram`, `tag2text`, `grounded_sam`, `yolo-world`).
*   **`clip_ft`**: Represents the per-mask CLIP image feature, L2-normalized and typically averaged across all 2D detections contributing to a 3D object. These features capture the visual semantics.
*   **`text_ft`**: Represents per-mask CLIP text features derived from models like RAM (Recognize Anything Model) tags, providing textual semantic descriptions.
*   **`DetectionList`**: A data structure holding a list of per-frame detection dictionaries, serving as the input for 3D object mapping.
*   **`MapObjectList`**: A data structure containing the list of 3D fused object dictionaries, representing the output of the 3D mapping pipeline.
*   **Key Terms**: `open-vocabulary detection`, `open-vocabulary segmentation`, `zero-shot detection`, `mask proposal`, `dense prediction`, `DINOv2 features`, `SAM2 mask decoder`, `YOLO-World detection`, `RAM tagging`, `Grounded-SAM`, `Tag2Text`, `foundation model`, `vision encoder`.

### C. Re-Identification and Cross-Frame Association

Re-identification (ReID) is the process of consistently linking the same physical object across different frames or views, maintaining its identity throughout the mapping process.

*   **`F.normalize`**: Utilized for L2 normalization of CLIP features after weighted averaging during object merging, ensuring consistent feature scaling for similarity comparisons.
*   **`contain_number`, `contain_area_thresh`, `contain_mismatch_penalty`**: Parameters used in sophisticated containment checks and penalty calculations to refine association decisions, especially for nested or overlapping objects.
*   **Key Terms**: `re-identification`, `ReID`, `instance association`, `tracking across frames`, `visual descriptor`, `embedding similarity`, `identity consistency`, `appearance feature`, `feature aggregation`, `view fusion`.

### D. L2-A Semantic Abstraction & Scene Graph Generation

This is the final stage where the geometrically and visually consistent 3D objects are enriched with human-understandable semantic information and organized into a scene graph. This involves leveraging Large Language Models (LLMs) and Vision-Language Models (VLMs).

*   **`extract_node_captions`**: Generates initial per-object VLM captions, typically taking the top-k most confident captions.
*   **`refine_node_captions`**: Uses an LLM to consolidate multiple initial captions for an object into a single, concise `object_tag` (final semantic node label), improving clarity and consistency.
*   **`build_scenegraph`**: Constructs the 3D scene graph by first computing an overlap matrix between objects, then using a Minimum Spanning Tree (MST) approach to select salient edges, and finally employing an LLM for relation extraction between objects.
*   **`object_tag`**: The refined, single semantic label for each 3D object, serving as the node label in the scene graph.
*   **`caption_dict`**: Stores raw VLM captions, LLM responses, and the final `object_tag` for each object.
*   **`DEFAULT_PROMPT`**: The specific prompt used to guide the LLM in extracting relational predicates, often including spatial information like `bbox_extent` and `bbox_center` along with `object_tag`s.
*   **`minimum_spanning_tree`**: Used over the object overlap adjacency matrix to select a relevant subset of potential relationships for LLM processing, avoiding combinatorial explosion.
*   **`object_relation`**: The output of LLM relation extraction, describing the relationship between two objects (e.g., "a on b", "b in a").
*   **Key Terms**: `semantic abstraction`, `scene graph node`, `object descriptor`, `node description`, `hierarchical class`, `affordance reasoning`, `relational edge`, `predicate extraction`, `scene context`, `spatial relation`, `scene-level reasoning`.

## ⚡ Quick Reference

Here are practical code examples for common tasks within the `concept-graphs` framework.

### 1. Run Streamlined 2D Detection (YOLO-World + MobileSAM)

This script simplifies the 2D detection process, often used as a quicker alternative to `generate_gsa_results.py`. Configuration is managed via Hydra YAML files.

```bash
# Ensure you are in the 'conceptgraph' directory
cd conceptgraph

# Run the streamlined detection script
# Configuration is loaded from hydra_configs/streamlined_detections.yaml
python scripts/streamlined_detections.py
```

### 2. Extract 2D Detections and Features (ConceptGraphs-Detect variant)

This command runs the detection and segmentation pipeline using a tagging model (RAM) and Grounding-DINO for class-aware bounding boxes, then SAM for segmentation.

```bash
SCENE_NAME=room0
# Ensure dataset_root and dataset_config are set as environment variables or provided
# Example: export REPLICA_ROOT=/path/to/Replica
#          export REPLICA_CONFIG_PATH=${CG_FOLDER}/conceptgraph/dataset/dataconfigs/replica/replica.yaml
python scripts/generate_gsa_results.py \
    --dataset_root $REPLICA_ROOT \
    --dataset_config $REPLICA_CONFIG_PATH \
    --scene_id $SCENE_NAME \
    --class_set ram \
    --box_threshold 0.2 \
    --text_threshold 0.2 \
    --stride 5 \
    --add_bg_classes \
    --accumu_classes \
    --exp_suffix withbg_allclasses
```

### 3. Run the 3D Object Mapping System (ConceptGraphs-Detect variant)

This command builds an object-based 3D map by processing the 2D detections and features generated in the previous step, performing object association and merging.

```bash
SCENE_NAME=room0
THRESHOLD=1.2 # Example threshold for similarity matching
python slam/cfslam_pipeline_batch.py \
    dataset_root=$REPLICA_ROOT \
    dataset_config=$REPLICA_CONFIG_PATH \
    stride=5 \
    scene_id=$SCENE_NAME \
    spatial_sim_type=overlap \
    mask_conf_threshold=0.25 \
    match_method=sim_sum \
    sim_threshold=${THRESHOLD} \
    dbscan_eps=0.1 \
    gsa_variant=ram_withbg_allclasses \
    skip_bg=False \
    max_bbox_area_ratio=0.5 \
    save_suffix=overlap_maskconf0.25_simsum${THRESHOLD}_dbscan.1
```

### 4. Visualize the Object-based Mapping Results

Once the `pkl.gz` output file is generated by the mapping pipeline, use this command to visualize the 3D objects. Keyboard callbacks (`b`, `c`, `r`, `f`, `i`) allow interactive exploration.

```bash
# Replace /path/to/output.pkl.gz with your actual result file
python scripts/visualize_cfslam_results.py --result_path /path/to/output.pkl.gz
```

### 5. Extract Object Captions and Build Scene Graphs

This sequence of commands performs the semantic abstraction, generating per-object captions and then building the relational scene graph. **Requires OpenAI API key.**

```bash
export OPENAI_API_KEY=<your GPT-4 API KEY here>
SCENE_NAME=room0
PKL_FILENAME=output.pkl.gz # Change this to your actual mapping output file

# 1. Extract per-object VLM captions
python scenegraph/build_scenegraph_cfslam.py \
    --mode extract-node-captions \
    --cachedir ${REPLICA_ROOT}/${SCENE_NAME}/sg_cache \
    --mapfile ${REPLICA_ROOT}/${SCENE_NAME}/pcd_saves/${PKL_FILENAME}

# 2. Refine captions into single object_tags using LLM
python scenegraph/build_scenegraph_cfslam.py \
    --mode refine-node-captions \
    --cachedir ${REPLICA_ROOT}/${SCENE_NAME}/sg_cache \
    --mapfile ${REPLICA_ROOT}/${SCENE_NAME}/pcd_saves/${PKL_FILENAME}

# 3. Build the scene graph by extracting relations using LLM
python scenegraph/build_scenegraph_cfslam.py \
    --mode build-scenegraph \
    --cachedir ${REPLICA_ROOT}/${SCENE_NAME}/sg_cache \
    --mapfile ${REPLICA_ROOT}/${SCENE_NAME}/pcd_saves/${PKL_FILENAME}
```

### 6. Visualize the Object Map with Scene Graph

Visualize the generated 3D object map with its associated scene graph. Press `g` in the viewer to toggle scene graph display.

```bash
SCENE_NAME=room0
# Assuming scene_map_cfslam_pruned.pkl.gz and cfslam_object_relations.json are generated
python scripts/visualize_cfslam_results.py \
    --result_path ${REPLICA_ROOT}/${SCENE_NAME}/sg_cache/map/scene_map_cfslam_pruned.pkl.gz \
    --edge_file ${REPLICA_ROOT}/${SCENE_NAME}/sg_cache/cfslam_object_relations.json
```

## ⚙️ Configuration Patterns

*From C3.4 configuration analysis*

The `concept-graphs` project utilizes YAML and JSON files for configuration, particularly leveraging the `Hydra` framework for managing experimental settings. This allows for flexible and composable configurations.

**Configuration Files Analyzed:** 19
**Total Settings:** 243
**Patterns Detected:** 0 (No specific "patterns" in the sense of reusable code blocks, but diverse configurations are present)

**Configuration Types and Examples:**
- `environment.yml`: Specifies a Conda environment setup (3 settings).
- `conceptgraph/replica_room0.json`: General configuration for a specific replica room (7 settings).
- `conceptgraph/configs/slam_pipeline/base.yaml`: Base configuration for the SLAM pipeline (47 settings).
- `conceptgraph/dataset/dataconfigs/*.yaml`: Dataset-specific configurations, e.g., `hm3d.yaml` (8 settings), `replica.yaml` (29 settings).
- `conceptgraph/hydra_configs/*.yaml`: Hydra-specific configuration compositions, e.g., `base_detections.yaml` (20 settings), `streamlined_detections.yaml` (4 settings). These often override or extend base settings.

*See `references/config_patterns/` for detailed configuration analysis*

## 📖 Project Documentation

*Extracted from markdown files in the project (C3.9)*

The project includes several key documentation files providing context and instructions.

**Total Documentation Files:** 3
**Categories:** 2

### Overview
- **README.md**: The main project README, covering project overview, updates, setup instructions, and how to run the core ConceptGraphs pipeline and experiments.
- **README_streamlined_detection.md**: Details on an updated, simpler, and faster script for 2D detections using Hydra for configuration.

### Other
- **README.md** (`conceptgraph\scripts\scannet_process\README.md`): Likely specific instructions for ScanNet dataset processing.

*See `references/documentation/` for all project documentation*

## 📚 Available References

This skill includes detailed reference documentation categorized as follows:

-   **Dependencies**: `references/dependencies/` - Provides the dependency graph and analysis for the project.
-   **Patterns**: `references/patterns/` - Details any detected design patterns within the codebase.
-   **Configuration**: `references/config_patterns/` - Offers in-depth analysis of configuration files and their structures.
-   **Documentation**: `references/documentation/` - Contains raw and processed project documentation files.

## Practical Usage Guidance for Gemini

To effectively leverage this documentation, Gemini should focus on the following:

1.  **Prioritize Key Concepts**: The "Key Concepts" section is paramount. It distills the most critical technical aspects (Entry Gating, CV Stack, ReID, Semantic Abstraction) that define how ConceptGraphs operates. When asked about underlying mechanisms, object filtering, association, or scene graph generation, refer heavily to this section.
2.  **Use Quick Reference for Actions**: For common operational tasks such as running detection, mapping, or scene graph generation, consult the "⚡ Quick Reference" section. It provides actionable, concise code examples.
3.  **Understand Configuration with `hydra_configs`**: When discussing configuration, highlight the use of `Hydra` and the composable nature of `hydra_configs/*.yaml` files as described in `README_streamlined_detection.md` and the "Configuration Patterns" section.
4.  **Identify Core Keywords**: Pay close attention to keywords and symbol clusters mentioned in `skill_seeker_focus.md` (e.g., `filter_gobs`, `sim_threshold`, `object_tag`, `build_scenegraph`). These represent the critical functions and data structures within the codebase.
5.  **Focus on Object-Level Processing**: The skill's primary value lies in its ability to process individual objects through detection, tracking, fusion, and semantic description. Emphasize these steps when explaining the pipeline.
6.  **Avoid Out-of-Scope Topics**: Explicitly ignore details related to SLAM/pose estimation (beyond what's needed for 3D unprojection), Open3D visualization specifics (beyond basic key callbacks), dataset loading mechanics, or benchmark numbers, as these are out of the designated focus.
7.  **Consult `README.md` for Setup**: For detailed setup instructions (conda environment, installing Grounded-SAM, LLaVA), refer to the main `README.md` within the `references/documentation/` folder.

By following this guidance, Gemini can provide highly relevant and effective assistance regarding the `concept-graphs` skill, focusing on its unique capabilities in object-centric 3D scene understanding and graph generation.