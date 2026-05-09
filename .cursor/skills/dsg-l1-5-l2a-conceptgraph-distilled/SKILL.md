---
name: dsg-l1-5-l2a-conceptgraph-distilled
description: >
  ConceptGraph + open-vocab vision stack 蒸馏 — A10 入口门控 + L2-A 语义抽象。
  用于 DSG L1.5 / L2-A 设计 chat 的资料层；不是 L2-B 替代品。
distilled_from:
  - "concept-graphs/concept-graphs (main branch, 2026-05-04)"
  - "conceptgraph/slam/mapping.py — 相似度计算与对象合并"
  - "conceptgraph/slam/utils.py — 门控过滤 + 跨帧关联 + merge"
  - "conceptgraph/slam/slam_classes.py — MapObjectList / DetectionList"
  - "conceptgraph/slam/cfslam_pipeline_batch.py — 主循环 + 阈值决策"
  - "conceptgraph/scenegraph/build_scenegraph_cfslam.py — L2-A 节点描述 + 关系边"
  - "conceptgraph/configs/slam_pipeline/base.yaml — 官方默认阈值"
distilled_papers:
  - "ConceptGraphs: Open-Vocabulary 3D Scene Graphs for Perception and Planning (Gu et al., ICRA 2024)"
  - "DINOv2 (Oquab et al., 2024) — visual backbone 参考"
  - "SAM2 (Ravi et al., 2024) — 分割 backbone 参考"
  - "Recognize Anything / RAM (Zhang et al., 2023) — 开放词汇标签生成"
  - "Grounded-SAM (IDEA Research) — 文本提示分割"
last_reviewed: 2026-05-04
ai_audience: "DSG L1.5 / L2-A 设计 chat（不替代 L2-B）"
---

# DSG 1.5 A10 入口 + L2-A — ConceptGraph 蒸馏

> **这个 SKILL 是什么**：从 ConceptGraph 仓库提炼的技术资料，服务于 ParrotCarriers DSG
> L1.5（A10 入口侧）和 L2-A（语义抽象层）的设计。它是**只读参考**，不是实施 PR，不替代
> `parrot.dsg.l2b_graph`。

---

## 0. 范围与严格不做事项

### 0.1 In Scope（本 SKILL 覆盖）

| 主题 | ConceptGraph 对应 | 提取要点 |
|:--|:--|:--|
| **A10 入口门控** | `filter_gobs()` + `compute_match_batch()` + `sim_threshold` | 门控决策树、阈值表、多帧 vote 策略 |
| **A10 技术栈** | Grounded-SAM + RAM + CLIP | 各模型角色边界 + 推理时序 |
| **跨帧关联 / ReID** | `compute_spatial_similarities()` + `compute_visual_similarities()` + `merge_obj2_into_obj1()` | IoU+CLIP 组合策略 + 特征融合方式 |
| **L2-A 语义抽象** | `extract_node_captions()` + `refine_node_captions()` + `build_scenegraph()` | pixel → semantic node 的 4 步流程 |
| **门控失败的可观测性** | `filter_gobs()` 跳过条件 + `filter_objects()` | drop reason 分类 |

### 0.2 Out of Scope（严禁蒸馏进 SKILL）

| 主题 | 原因 |
|:--|:--|
| **L2-B 工作记忆图结构** | ParrotCarriers 有自己的 `parrot.dsg.l2b_graph`（RustworkX），不用 ConceptGraph 的 LangChain/Open3D 替换 |
| **L1.5 预加载 Node 池** | 用户自己做任务 1.4 |
| **3D 重建 / mesh / SLAM** | AR Foundation 已处理 pose+平面 |
| **完整端到端 demo / GUI / 可视化** | 与我们无关 |
| **Replica / ScanNet benchmark** | 不相关 |
| **LLaVA 调用方式** | 我们用 Gemini；LLaVA 的具体 API 不蒸馏 |
| **LiveKit / Unity / Brain 集成建议** | SKILL 是只读资料，不做产品集成建议 |

---

## 0.5 仓库蒸馏产出对比（Gemini enhance vs 自建）

> **蒸馏日期**：2026-05-04；skill-seekers 3.5.0 + Gemini enhance
> **蒸馏产出路径（archived）**：原 `NewZone/distill_output/dsg/concept-graphs/SKILL.md` + `NewZone/skill_distill_bundle/09_conceptgraphs/skill_seeker_focus.md` 2026-05-09 物理删除；精华已入本 SKILL §0.5 ~ §4。

Gemini enhance 版相比本文**额外覆盖**的内容：

### 0.5.1 推荐（README）参数 vs base.yaml 默认值差异

来自 README 中 `cfslam_pipeline_batch.py` 的实际运行示例，与 `base.yaml` 默认值不同：

| 参数 | base.yaml 默认 | README 推荐示例 | 含义 |
|:--|:--|:--|:--|
| `spatial_sim_type` | `iou` | `overlap` | README 推荐 overlap（点云近邻），比纯 IoU 更准但更慢 |
| `match_method` | `sep_thresh` | `sim_sum` | README 推荐 sim_sum 加权求和模式 |
| `sim_threshold` | `0` | `1.2` | sim_sum 模式下的实用阈值（默认 0 相当于无门控） |
| `mask_conf_threshold` | `0.2` | `0.25` | README 稍微提高置信度门 |
| `max_bbox_area_ratio` | `1.0` | `0.5` | README 将最大 bbox 比例降至 0.5（过滤整图误检） |
| `dbscan_eps` | `0.05 m` | `0.1 m` | README 使用更大的 DBSCAN 邻域半径 |
| `skip_bg` | `True` | `False`（搭配 `ram_withbg_allclasses`） | 某些实验保留背景类 |

> **关键启示**：`sim_threshold=0` 等于没有相似度门控，**实用场景需要设 >0**。

### 0.5.2 Hydra Config 组合模式

ConceptGraph 使用 Hydra 管理配置，有两套入口：

```bash
# 传统入口（手动参数传入）
python slam/cfslam_pipeline_batch.py \
    spatial_sim_type=overlap match_method=sim_sum sim_threshold=1.2 ...

# 新版 streamlined 入口（hydra_configs/ 组合，更简洁）
# 配置文件: conceptgraph/hydra_configs/streamlined_detections.yaml
# 使用 YOLO-World + MobileSAM（比 Grounded-SAM 快）
python scripts/streamlined_detections.py
```

`hydra_configs/` 下的 YAML 通过 Hydra compose 覆盖 `slam_pipeline/base.yaml`，可以做实验性参数切换。

### 0.5.3 三阶段 CLI 流程（README 来源）

```bash
# Step 1: 生成 2D 检测结果（RAM + Grounding-DINO + SAM）
python scripts/generate_gsa_results.py \
    --class_set ram --box_threshold 0.2 --text_threshold 0.2 \
    --stride 5 --add_bg_classes --accumu_classes

# Step 2: 3D 对象映射（帧级门控 + 关联 + 合并）
python slam/cfslam_pipeline_batch.py \
    spatial_sim_type=overlap mask_conf_threshold=0.25 \
    match_method=sim_sum sim_threshold=1.2 dbscan_eps=0.1 \
    gsa_variant=ram_withbg_allclasses skip_bg=False max_bbox_area_ratio=0.5

# Step 3: L2-A 语义抽象（三步）
python scenegraph/build_scenegraph_cfslam.py --mode extract-node-captions  # VLM 描述
python scenegraph/build_scenegraph_cfslam.py --mode refine-node-captions    # LLM 精炼
python scenegraph/build_scenegraph_cfslam.py --mode build-scenegraph        # 关系图
```

---

## 1. A10 入口门控

### 1.1 门控决策树

每一帧 detection 进入 DSG 前经过两道门：

```
RGB 帧
  │
  ▼  [第一道门：帧级过滤 filter_gobs()]
  ├─ mask 像素面积 < mask_area_threshold (25px) → DROP (太小)
  ├─ skip_bg=True 且 class ∈ {wall,floor,ceiling} → DROP (背景)
  ├─ 非背景 bbox 面积 > max_bbox_area_ratio * 图像面积 → DROP (太大)
  ├─ confidence < mask_conf_threshold (0.2) → DROP (置信低)
  └─ 通过 → 进入 gobs_to_detection_list()
       │
       ▼  [三维提升]
       ├─ 深度图 unprojection → 相机系点云
       ├─ 变换到世界系
       ├─ DBSCAN 去噪 → 保留最大簇
       ├─ 3D bbox 体积 < 1e-6 → DROP (退化点云)
       └─ 通过 → DetectionList fg_detection_list
            │
            ▼  [第二道门：帧-地图关联 compute_match_batch()]
            ├─ 如果 objects 为空 → 直接 ADMIT（首帧全部进入）
            ├─ 计算 MxN spatial_sim (IoU/GIoU/overlap)
            ├─ 计算 MxN visual_sim (CLIP cosine sim)
            ├─ agg_sim = (1+phys_bias)*spatial + (1-phys_bias)*visual
            │    ├─ 使用 sep_thresh: spatial>0.5 AND visual>0.5
            │    └─ 使用 sim_sum: agg_sim > sim_threshold (default 0)
            ├─ agg_sim[i].max() == -inf → 新建节点 (ADMIT as new)
            └─ 否则 → 合并进匹配节点 (MERGE into argmax obj)
```

**关键源码位置：**
- `slam/utils.py:filter_gobs()` — 第一道门
- `slam/utils.py:gobs_to_detection_list()` — 三维提升 + 点云检查
- `slam/cfslam_pipeline_batch.py:compute_match_batch()` — 第二道门
- `slam/mapping.py:merge_detections_to_objects()` — 新建 vs 合并决策

### 1.2 阈值参数表（来自 `configs/slam_pipeline/base.yaml`）

| 参数 | 默认值 | 语义 | 影响 |
|:--|:--|:--|:--|
| `mask_area_threshold` | 25 px | 2D mask 最小像素数 | 过小的 mask 直接丢弃 |
| `mask_conf_threshold` | 0.2 | Grounded-SAM 置信度下限 | 低置信检测不进 DSG |
| `max_bbox_area_ratio` | 1.0 | bbox 最大图像面积比例 | 防止误检整图 |
| `min_points_threshold` | 16 | 3D PCD 最少点数 | 深度退化时丢弃 |
| `semantic_threshold` | 0.5 | sep_thresh 模式下视觉相似度下限 | CLIP cosine sim 门 |
| `physical_threshold` | 0.5 | sep_thresh 模式下空间相似度下限 | IoU 门 |
| `sim_threshold` | 0 | sim_sum 模式下聚合相似度下限 | 两者加权和的门 |
| `phys_bias` | 0.0 | 空间 vs 视觉的权重偏置 | 0=等权，正值偏向空间 |
| `contain_mismatch_penalty` | 0.5 | 容纳关系不匹配时的惩罚 | 防止小物体错配大容器 |
| `obj_min_detections` | 3 | 最终保留的最少检测次数 | 少于 3 帧的节点被删除 |
| `obj_min_points` | 0 | 最终保留的最少 3D 点数 | 0=不按点数过滤 |
| `merge_overlap_thresh` | 0.7 | 合并时点云重叠比例下限 | 重叠不够不合并 |
| `merge_visual_sim_thresh` | 0.7 | 合并时 CLIP 视觉相似度下限 | 视觉不像不合并 |
| `merge_text_sim_thresh` | 0.7 | 合并时文本嵌入相似度下限 | 语义不像不合并 |

### 1.3 多帧 Vote 策略（持久性门控）

ConceptGraph **不做逐帧实时 vote**，而是：

1. **帧内立即关联**：每帧检测实时 match → 合并或新建（在线模式）
2. **周期性事后过滤**（可配置间隔）：
   - `denoise_interval: 20` — 每 20 帧跑一次 DBSCAN 去噪
   - `filter_interval: -1` — 默认只在最后运行 `filter_objects()`
   - `merge_interval: -1` — 默认只在最后运行 `merge_objects()`
3. **最终过滤**：整个序列跑完后，`obj_min_detections=3` 淘汰低频节点

这意味着 ConceptGraph 的"持久性"是通过**最终过滤**而非实时 vote 实现的。
对于 ParrotCarriers 的实时场景，这个设计需要调整为流式累积计数。

### 1.4 门控失败分类

| 失败类型 | 触发条件 | 来源函数 |
|:--|:--|:--|
| `SMALL_MASK` | `mask.sum() < max(mask_area_threshold, 10)` | `filter_gobs()` |
| `LOW_CONF` | `confidence < mask_conf_threshold` | `filter_gobs()` |
| `LARGE_BBOX` | `bbox_area > max_bbox_area_ratio * image_area` | `filter_gobs()` |
| `BG_CLASS` | `class_name in ["wall","floor","ceiling"]` | `filter_gobs()` |
| `SPARSE_PCD` | `len(pcd.points) < min_points_threshold` | `gobs_to_detection_list()` |
| `DEGENERATE_BBOX` | `pcd_bbox.volume() < 1e-6` | `gobs_to_detection_list()` |
| `SIM_BELOW_THRESH` | `agg_sim < sim_threshold`（不新建也不合并，会在后期被 filter 淘汰） | `compute_match_batch()` |
| `INSUFFICIENT_VIEWS` | `num_detections < obj_min_detections` | `filter_objects()` |

ConceptGraph **没有**为每次 drop 写结构化日志；这是 ParrotCarriers 需要自己补充的可观测性。

---

## 2. A10 入口技术栈

### 2.1 模型组合矩阵

ConceptGraph 的主流水线（`gsa_variant: ram`）：

| 模型 | 角色 | 输入 | 输出 | GPU 成本 |
|:--|:--|:--|:--|:--|
| **RAM** (Recognize Anything) | 开放词汇标签生成 | RGB 图 | 标签列表（str[]） | 低（仅图像分类） |
| **Grounding DINO** | 文本引导检测 | RGB + 标签文本 | xyxy bbox + confidence | 中 |
| **SAM** (SAM2) | 实例分割 | RGB + bbox prompt | binary mask | 高（但 amortized） |
| **CLIP** (image encoder) | 视觉 ReID 特征 | 裁剪后的 mask 区域 | L2-norm embedding (D=512/768) | 低（推理快） |
| **CLIP** (text encoder) | 文本语义特征 | RAM 标签文字 | L2-norm text embedding | 极低 |
| **LLM/VLM** | 节点描述生成（L2-A，离线） | 裁剪图 + mask | 自然语言描述 | 高（批量离线） |

> **注**：ConceptGraph 原始实现用 LLaVA 作 VLM；ParrotCarriers 改用 Gemini，接口等价。

### 2.2 各模型的角色边界

```
原始帧
  │
  ├─► RAM ──────────────────────────── 给整帧打开放标签（无坐标）
  │     └── 标签列表 ──► Grounding DINO ── 产出 N 个 (xyxy, conf, class_label)
  │                          └── xyxy ──► SAM ────── 产出 N 个 binary mask
  │
  ├─► CLIP image encoder ─────────────── 对每个 mask crop 提取 clip_ft
  └─► CLIP text encoder ──────────────── 对每个 class_label 提取 text_ft
       └── clip_ft + text_ft ──► gobs dict (后续门控和关联使用)
```

**关键边界原则：**
- RAM 决定"检测什么"（开放词汇 token 集合）
- Grounding DINO 决定"在哪里"（bbox）
- SAM 决定"精确形状"（mask），不决定语义
- CLIP image 决定"看起来像什么"（ReID 基础）
- CLIP text 决定"文字上像什么"（merge 时文本相似度对照）

### 2.3 推理时序

```
串行依赖链：
RAM → Grounding DINO → SAM → [CLIP image, CLIP text](可并行)

可并行化：
- 多个 mask 的 CLIP image 编码可 batch
- CLIP text 编码可预缓存（同一标签不重复计算）

瓶颈：SAM（mask decoder 逐 prompt）
优化选项（原仓库未实现）：
- SAM Everything 模式（一次产所有 mask，再用 DINO 匹配）
- 批量 bbox prompt → 减少 SAM forward pass 次数
```

---

## 3. 跨帧关联 / 重识别

### 3.1 关联策略（IoU + Visual + Spatial）

```python
# slam/mapping.py

def compute_spatial_similarities(cfg, detection_list, objects):
    """返回 MxN spatial_sim 矩阵"""
    # 支持: "iou", "giou", "iou_accurate", "giou_accurate", "overlap"
    # 默认: "iou"（2D/3D axis-aligned bbox IoU）

def compute_visual_similarities(cfg, detection_list, objects):
    """返回 MxN visual_sim 矩阵"""
    # F.cosine_similarity(det_clip_ft, obj_clip_ft)

def aggregate_similarities(cfg, spatial_sim, visual_sim):
    """聚合方式 sim_sum：
    sims = (1 + phys_bias) * spatial + (1 - phys_bias) * visual
    phys_bias=0 → 等权
    phys_bias>0 → 偏向空间
    """
```

**匹配决策（`compute_match_batch()`）：**
```python
# 两种模式：
# sep_thresh: spatial > physical_threshold AND visual > semantic_threshold
# sim_sum: agg_sim > sim_threshold

# 每个 detection 只匹配一个 object（argmax），
# 多个 detection 可以匹配同一个 object（允许多帧合并到同一节点）
for i in row_max.argsort(descending=True):
    if row_max[i] > cfg.sim_threshold:
        assign_mat[i, row_argmax[i]] = 1
```

### 3.2 特征融合方式（跨帧平均）

```python
# slam/utils.py:merge_obj2_into_obj1()
# clip_ft：加权均值（按检测次数）后 L2 归一化
obj1['clip_ft'] = (obj1['clip_ft'] * n_obj1 + obj2['clip_ft'] * n_obj2) / (n_obj1 + n_obj2)
obj1['clip_ft'] = F.normalize(obj1['clip_ft'], dim=0)

# text_ft：同样加权均值后 L2 归一化
obj1['text_ft'] = (obj1['text_ft'] * n_obj1 + obj2['text_ft'] * n_obj2) / (n_obj1 + n_obj2)
obj1['text_ft'] = F.normalize(obj1['text_ft'], dim=0)
```

> 特征越来越多帧融合后，CLIP 特征会向"平均外观"漂移。
> 遮挡或旋转后出现的新外观会被稀释，这是 ReID 的主要弱点。

### 3.3 ReID 特征选择

ConceptGraph 原始使用 **CLIP image encoder**（ViT-H/14 或 ViT-L/14）。
DINOv2 被论文提及为更强的 dense feature backbone（ReID 替代选项），但仓库代码中未见直接集成。

| 特征 | 优势 | 弱点 |
|:--|:--|:--|
| CLIP image (ViT-L) | 开箱即用；文本-图像对齐 | 对 low-level 纹理差异不敏感 |
| DINOv2 (ViT-L) | dense feature，patch 级别精度高 | 没有文本对齐，需要额外的相似度定义 |
| CLIP text | 可与语言查询直接比较 | 依赖文本标签质量 |

### 3.4 失败场景

| 场景 | 后果 | ConceptGraph 原始处理 |
|:--|:--|:--|
| 视角剧烈变化（>90°） | CLIP cosine sim 下降 → 可能新建重复节点 | 无；依赖 merge_objects 事后合并 |
| 遮挡后重现 | 跟丢 → 新建节点 → 后期 MST 关联可合并 | merge_overlap_thresh 只对空间重叠有效 |
| 相似物体（同类多实例）| CLIP 难以区分 → 误合并 | 无主动预防 |
| 快速运动（帧率不足）| IoU 为 0 → 新建节点 | stride 参数可降低帧率跳跃 |
| 光照突变 | CLIP 特征不稳定 | 无 |

---

## 4. L2-A 语义抽象

### 4.1 Detection → Semantic Node 的 4 步流程

```
Step 1: 2D Detection → 3D MapObject
  输入: (mask, xyxy, class_name, conf, clip_ft, text_ft)
  操作: 深度 unprojection → 世界系 PCD → bbox
  输出: MapObject dict（见 §4.2 数据结构）

Step 2: 多帧积累 → 对象成熟
  操作: 跨帧 merge（§3），CLIP 特征加权平均
  门：num_detections >= obj_min_detections(3)
  输出: 稳定 MapObject（clip_ft 已收敛）

Step 3: VLM 描述生成（离线 / 批处理）
  操作: 
    ① 对每个对象取置信度最高的 top-k(10) detection
    ② crop + 可选 mask blackout
    ③ VLM query = "Describe the central object in the image."
    ④ 收集 k 个自然语言 caption
  输出: caption_dict = {"id": N, "captions": [...], "low_confidences": [...]}
  
  小目标跳过条件: image_crop 面积 < 70*70 px（标记为 low_confidence）

Step 4: LLM 描述精炼 → object_tag
  操作: 把 k 个 caption 发给 GPT-4（ParrotCarriers: Gemini）
  提示结构（推断）: 多描述 → 单一精炼标签
  输出 JSON:
    {
      "object_tag": "wooden chair",    ← 精炼后的语义节点标签
      "summary": "...",               ← 一句话描述
      "possible_tags": [...]          ← 候选标签（备用）
    }
  失败处理: tag="invalid"/"FAIL" 的节点从图中删除
```

**关键源码位置：**
- `scenegraph/build_scenegraph_cfslam.py:extract_node_captions()` — Step 3
- `scenegraph/build_scenegraph_cfslam.py:refine_node_captions()` — Step 4

### 4.2 MapObject 数据结构（节点的原始表示）

```python
{
    # 来源追踪
    'image_idx':      [int, ...],        # 各 detection 对应的帧索引
    'mask_idx':       [int, ...],        # 各 detection 在帧中的 mask 索引
    'color_path':     [str, ...],        # RGB 图像路径（用于 VLM 回溯）
    
    # 语义信息
    'class_name':     [str, ...],        # RAM/Grounding-DINO 给出的类名（每帧可能不同）
    'class_id':       [int, ...],        # 全局类 ID
    
    # 跟踪统计
    'num_detections': int,               # 累计关联次数（持久性指标）
    'conf':           [float, ...],      # 各 detection 的置信度
    
    # 2D 信息
    'mask':           [np.ndarray, ...], # 二值 mask
    'xyxy':           [[x1,y1,x2,y2],...], # bbox
    'pixel_area':     [int, ...],        # mask 像素数
    
    # 3D 表示
    'pcd':            o3d.PointCloud,    # 融合后的世界系点云
    'bbox':           o3d.OrientedBoundingBox, # 3D 有向包围盒
    'n_points':       [int, ...],        # 各帧 PCD 点数
    
    # 特征向量（ReID 核心）
    'clip_ft':        torch.Tensor(D,),  # CLIP 图像特征，L2 归一化，加权平均
    'text_ft':        torch.Tensor(D,),  # CLIP 文本特征，L2 归一化，加权平均
    
    # L2-A 阶段追加（离线）
    'caption_dict':   {                  # VLM 描述结果
        'id': int,
        'captions': [str, ...],          # Step 3 原始描述
        'response': {                    # Step 4 LLM 精炼结果
            'object_tag': str,
            'summary': str,
            'possible_tags': [str, ...],
        }
    },
}
```

### 4.3 关系 / 边 抽象（L2-A 图边）

**关系提取流程：**

```
MapObject 列表（有 object_tag 的）
  │
  ▼ compute_overlap_matrix() → NxN 点云重叠矩阵
  │  重叠率 = 物体 i 中距物体 j 点云 < downsample_voxel_size 的点比例
  │
  ▼ 构建加权邻接矩阵（重叠率 > 0.01 的边）
  │
  ▼ MST（最小生成树）→ 减少关系查询数量（节省 LLM 调用）
  │
  ▼ LLM Relation Prompt（每对相邻节点）:
      输入: object1.tag + bbox_extent + bbox_center
             object2.tag + bbox_extent + bbox_center
      输出 JSON: { "object_relation": "a on b" | "b on a" |
                                     "a in b" | "b in a" |
                                     "none of these",
                   "reason": str }
  │
  ▼ scenegraph_edges = [(node_i, node_j, relation_str), ...]
    过滤: relation == "none of these" → 不产生边
```

**关系类型定义（5 类）：**
- `"a on b"` — a 常放在 b 上面（cup on table）
- `"b on a"` — b 常放在 a 上面
- `"a in b"` — a 常放在 b 里面（apple in bowl）
- `"b in a"` — b 常放在 a 里面
- `"none of these"` — 无明显拓扑关系 → 不产生边

**与 ParrotCarriers L2-B 的接口契约：**
> L2-A 的输出是"语义节点 + 拓扑关系"；L2-B（我们自己的 RustworkX 图）负责在运行时
> 存储和查询这些节点。L2-A 不定义图的存储结构——它只定义节点的语义内容。

---

## 5. 关键阈值与配置汇总

> 来源：`conceptgraph/configs/slam_pipeline/base.yaml`

### 5.1 帧级过滤阈值

| 参数 | 值 | 单位 | 语义说明 |
|:--|:--|:--|:--|
| `mask_area_threshold` | 25 | px² | 2D mask 最小像素面积 |
| `mask_conf_threshold` | 0.2 | [0,1] | Grounded-SAM 置信度下限 |
| `max_bbox_area_ratio` | 1.0 | 图像面积比例 | 误检整图的防护（默认不限制） |
| `min_points_threshold` | 16 | 点数 | 3D 点云最小密度 |

### 5.2 关联阈值

| 参数 | 值 | 模式 | 语义说明 |
|:--|:--|:--|:--|
| `spatial_sim_type` | `"iou"` | — | 空间相似度计算方式 |
| `match_method` | `"sep_thresh"` | — | 关联决策方式 |
| `semantic_threshold` | 0.5 | sep_thresh | CLIP 视觉相似度下限 |
| `physical_threshold` | 0.5 | sep_thresh | IoU 空间相似度下限 |
| `sim_threshold` | 0 | sim_sum | 聚合相似度下限 |
| `phys_bias` | 0.0 | sim_sum | 空间权重偏置 |
| `contain_area_thresh` | 0.95 | — | 认定"包含"的面积比例 |
| `contain_mismatch_penalty` | 0.5 | — | 容纳关系不匹配时的降分 |

### 5.3 点云处理参数

| 参数 | 值 | 语义说明 |
|:--|:--|:--|
| `downsample_voxel_size` | 0.025 m | 体素下采样粒度 |
| `dbscan_remove_noise` | True | 是否跑 DBSCAN 去噪 |
| `dbscan_eps` | 0.05 m | DBSCAN 邻域半径 |
| `dbscan_min_points` | 10 | DBSCAN 最小点数 |

### 5.4 持久性过滤参数

| 参数 | 值 | 语义说明 |
|:--|:--|:--|
| `obj_min_detections` | 3 | 最终保留的最少关联帧数 |
| `obj_min_points` | 0 | 最终保留的最少 3D 点数（0=不限） |
| `merge_overlap_thresh` | 0.7 | merge_overlap_objects 的点云重叠率门 |
| `merge_visual_sim_thresh` | 0.7 | merge_overlap_objects 的 CLIP 视觉相似度门 |
| `merge_text_sim_thresh` | 0.7 | merge_overlap_objects 的文本相似度门 |

### 5.5 周期性操作间隔

| 参数 | 值 | 语义说明 |
|:--|:--|:--|
| `denoise_interval` | 20 | 每 20 帧跑一次 DBSCAN 去噪（重） |
| `filter_interval` | -1 | 仅在最后运行（-1=跳过） |
| `merge_interval` | -1 | 仅在最后运行（-1=跳过） |

---

## 6. 引用源代码 / 论文

### 6.1 核心代码引用

| 功能 | 文件 | 关键函数 |
|:--|:--|:--|
| 帧级 detection 过滤 | `conceptgraph/slam/utils.py` | `filter_gobs()` |
| Detection → 3D 点云 | `conceptgraph/slam/utils.py` | `gobs_to_detection_list()`, `create_object_pcd()` |
| 空间相似度 | `conceptgraph/slam/mapping.py` | `compute_spatial_similarities()` |
| 视觉相似度 | `conceptgraph/slam/mapping.py` | `compute_visual_similarities()` |
| 关联决策 | `conceptgraph/slam/cfslam_pipeline_batch.py` | `compute_match_batch()` |
| 合并操作 | `conceptgraph/slam/utils.py` | `merge_obj2_into_obj1()` |
| 持久性过滤 | `conceptgraph/slam/utils.py` | `filter_objects()` |
| 后期批量合并 | `conceptgraph/slam/utils.py` | `merge_overlap_objects()`, `merge_objects()` |
| 节点描述生成 | `conceptgraph/scenegraph/build_scenegraph_cfslam.py` | `extract_node_captions()` |
| 描述精炼 | `conceptgraph/scenegraph/build_scenegraph_cfslam.py` | `refine_node_captions()` |
| 关系图构建 | `conceptgraph/scenegraph/build_scenegraph_cfslam.py` | `build_scenegraph()` |
| 默认配置 | `conceptgraph/configs/slam_pipeline/base.yaml` | 全文 |

### 6.2 论文关键段落

- **ConceptGraphs §3.1**：Frame-level association pipeline（IoU + CLIP sim 的具体公式）
- **ConceptGraphs §3.2**：Object-level representation（clip_ft weighted average 的理论依据）
- **ConceptGraphs §4**：Scene graph construction（LLM 关系提取的实验验证）
- **RAM 论文 §3**：RAM tagging 的开放词汇工作原理
- **DINOv2 §4.2**：Dense patch feature 与 ReID 的关联分析

---

## 7. 与 ParrotCarriers 现状的差异分析

### 7.1 我们的 SemanticNode.source_meta 会装什么

基于 ConceptGraph 的 MapObject 结构，对应到 `source_meta` 字段：

```python
# 推测的 source_meta 内容（等设计 chat 确认）
source_meta = {
    "detection_origin": "grounded_sam" | "sam2_prompted" | ...,
    "clip_ft": list[float],          # 用于后续 ReID 比较
    "num_frames_seen": int,          # 对应 num_detections
    "min_conf": float,               # 历次检测中最低置信度
    "initial_class_name": str,       # 初始 RAM/DINO 分类
    "vlm_object_tag": str | None,    # L2-A 精炼后的标签（可选，离线填入）
    "bbox_3d_center": [x, y, z],     # 对应 bbox.center
    "last_seen_frame": int,          # 最近一次关联的帧号
}
```

### 7.2 IngestRunner.commit_observation 与 ConceptGraph node-add 的差异

| 维度 | ConceptGraph | ParrotCarriers (推测) |
|:--|:--|:--|
| 触发方式 | 批处理（整个序列跑完再建图）| 流式（帧到即处理，commit_observation 实时） |
| VLM 描述 | 离线（跑完后统一调 LLaVA/GPT-4） | 需要在线或异步（用 Gemini，延迟可控） |
| 持久性 | 事后过滤（obj_min_detections） | 应为实时计数 + 滑动窗口 |
| 关系边构建 | 离线 MST + LLM | TBD（L2-A 设计 chat 的核心问题） |
| 数据结构 | Python dict + Open3D | parrot.dsg SemanticNode + RustworkX |

### 7.3 ConceptGraph 有但 ParrotCarriers 暂无的能力

| 能力 | ConceptGraph 实现 | 我们的状态 | 何时考虑 |
|:--|:--|:--|:--|
| 精确 3D 有向包围盒 | `o3d.OrientedBoundingBox` | AR Foundation 只有 AABB 平面锚点 | Phase 5+ |
| 体素下采样点云 | `pcd.voxel_down_sample(0.025m)` | 无 PCD | Phase 5+（需深度相机） |
| DBSCAN 去噪 | `pcd_denoise_dbscan()` | 无 | Phase 5+ |
| 点云重叠计算（FAISS） | `compute_overlap_matrix()` | 无 | Phase 5+ |
| MST 关系边 | `minimum_spanning_tree()` | TBD | L2-A 设计 chat 决定 |
| 多 caption 精炼 | GPT-4 批量 refine | 可替换为 Gemini | L2-A 设计 chat |

---

## 8a. AR 场景特有问题记录（已知 Open Questions）

> **记录规则**：仅记录在 AR Foundation + 桌面锚点场景下，将 ConceptGraph 门控/关联/置信度机制
> 迁移到 ParrotCarriers 时**已识别的问题**。**不包含解决方案或建议**，留给后续设计 chat 决定。

### 8a.1 位置锚点与门控相关

**Q1. AR 追踪漂移破坏 IoU 有效性**
AR Foundation 的 VIO 追踪有累积误差，世界坐标系会逐渐漂移。当锚点漂移时，前一帧对象的 3D bbox 在当前帧的 IoU 值会下降——即使物理上是同一物体。此时 ConceptGraph 的 `sim_threshold` 机制不能区分"物体移动了"和"坐标系漂移了"。**问题**：IoU-based 空间相似度对 AR 漂移场景的可靠性边界在哪里？

**Q2. 桌面平面锚点漂移的传递性**
AR Foundation 中物体位置锚点通常附着于平面锚点（ARAnchor）。若桌面平面的 AR 锚点因追踪丢失或重定位而偏移，桌面上所有对象的"理论位置"是否应跟随平面锚点整体偏移？如果是，则 DSG 层的节点位置需要何时、以何种方式跟随 AR 平面锚点更新？**问题**：对象节点的 world-frame 坐标是否应与其所在平面的 AR 锚点绑定，还是应独立存储？

**Q3. AR 追踪丢失/恢复导致的批量节点误创建**
AR Foundation 追踪丢失后重定位时，所有现有锚点可能同时偏移。这会导致已有节点的 bbox 与新帧检测的 IoU 全部归零，进而触发门控判定"全是新对象"，批量创建重复节点。**问题**：如何在 DSG 层感知到"这是追踪恢复事件"而非"这是新物体出现"？

**Q4. 桌面有物体时可信度的空间歧义**
当相机以斜角观察桌面时，桌面上的物体在 2D 投影中可能重叠（前景遮挡后景）。同一物体的两个相邻帧 2D mask 在 IoU 上可能很低（视角变化大），但物理上是同一个。**问题**：在桌面对象密集摆放场景下，`physical_threshold`（IoU 门）是否需要根据视角变化量动态调整？

### 8a.2 置信度冲突相关

**Q5. AR 锚点置信度与视觉置信度的冲突**
AR Foundation 为每个锚点提供独立的追踪状态（Tracking / Limited / None）。ConceptGraph 的 `conf` 字段是 Grounded-SAM 的检测置信度。两者描述不同维度的可信度：前者表示"位置是否可信"，后者表示"这是该物体的概率"。**问题**：当 AR 锚点追踪状态为 Limited（低位置可信度）但视觉置信度高时，这个节点的门控状态如何？

**Q6. 深度不确定性导致的多候选 3D 位置**
AR Foundation 的深度估计（LiDAR 或 stereo）在物体边缘处不确定性高。同一 2D detection 可能对应多个候选 3D 位置。在 ConceptGraph 的流程中，`gobs_to_detection_list` 假设每个 mask 有一个确定的 3D 点云，但深度不确定时会产生形变点云。**问题**：深度噪声对最终 3D bbox 的影响有多大，以及这如何影响跨帧 IoU 的可靠性？

**Q7. 相似对象互混的置信度问题**
桌面上摆放多个同类但不同实例的物体（如多个杯子）。CLIP 特征对同类对象之间的区分度有限，`merge_visual_sim_thresh=0.7` 的阈值可能将不同实例误判为同一对象。**问题**：在桌面上存在同类多实例的场景下，基于 CLIP 的视觉相似度是否仍能作为可靠的"同一对象"判断依据？

### 8a.3 特征退化相关

**Q8. 多帧特征平均的漂移问题（外观漂移）**
ConceptGraph 用 `clip_ft` 加权均值随时间积累。当相机从不同角度观察同一对象时，CLIP 特征会向"平均外观"漂移，导致当前视角的特征与积累特征之间相似度下降。在 AR 中用户会频繁走动，视角变化比 SLAM 数据集更剧烈。**问题**：多视角快速变化下，积累特征的收敛时间和退化速率是否超出 ConceptGraph 设计预期？

**Q9. 遮挡重现后的 ReID 失效**
用户在 AR 场景中走动时会遮挡并重新看到同一物体。重现时的 CLIP 特征（新视角）可能与积累特征相差较大，导致跨帧关联失败并创建重复节点。ConceptGraph 依赖事后 `merge_overlap_objects` 处理，但在实时场景中无法等待离线合并。**问题**：在流式实时处理约束下，遮挡重现的 ReID 失效是否为常态，其频率是否高到不可接受？

**Q10. 小物体深度错误导致 3D bbox 误置**
桌面上的小物体（如钥匙、笔）在 AR 深度估计中误差相对更大（噪声/物体尺度比高）。错误的深度会使 3D bbox 浮在桌面上方或陷入桌面内，导致 3D IoU 为 0 而 CLIP 视觉相似度仍高。**问题**：ConceptGraph 的 `min_points_threshold` 和 `obj_min_points` 是否足以过滤因深度错误产生的退化节点，还是会让这类错误节点持久化？

---

## 8. 不蒸馏的清单（明确跳过了什么）

以下内容**已确认跳过**，理由见 §0.2：

| 跳过内容 | 对应 ConceptGraph 文件 | 跳过理由 |
|:--|:--|:--|
| L2-B 图存储 | `conceptgraph/scenegraph/*.py` 中的图结构 | ParrotCarriers 自有 RustworkX |
| SLAM / 位姿估计 | `gradslam` 依赖部分 | AR Foundation 处理 |
| Open3D 可视化 | `conceptgraph/utils/vis.py` | 与我们无关 |
| `datasets_common.py` 数据集加载 | Replica/ScanNet 格式 | 与 AR Foundation 帧流无关 |
| LLaVA 具体 API | `conceptgraph/llava/llava_model.py` | 用 Gemini 替代 |
| OK-Robot 任务规划层 | `nyu-grail/OK-Robot` 上层 | 超出蒸馏范围 |
| Benchmark 数字 | 论文 Table 1-3 | 不相关 |
| Docker / 环境配置 | `environment.yml` | 不相关 |
