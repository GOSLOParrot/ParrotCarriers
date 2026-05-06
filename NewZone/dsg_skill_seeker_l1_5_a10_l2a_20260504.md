---
status: ratified
category: skill-seeker-task-spec
status_note: "Skill seeker 派发任务包 — 用户派往独立 workspace 用仓库蒸馏 skill 完成。范围：DSG 1.5 A10 入口门控 + L2-A 语义抽象层。明确不碰：L2-B (本仓库已自有) / L1.5 预加载 Node 池设计 (用户自己设计任务 1.4)。"
last_reviewed: 2026-05-04
target_repo_primary: "ConceptGraphs (concept-graphs.github.io / github.com/concept-graphs/concept-graphs)"
target_repos_secondary:
  - "OK-Robot (concept-graphs 后续 / nyu-grail)"
  - "OpenScene (3D scene understanding open-vocab)"
  - "RAM (Recognize Anything Model — open-vocab tagging)"
  - "Florence-2 (Microsoft open-vocab detection)"
  - "Grounded-SAM (open-vocab + SAM2 兼容)"
output_format: "SKILL.md (沿 .cursor/skills/graphiti/SKILL.md 模式)"
output_workspace: "独立 workspace，由用户派出"
ai_priority: high
ai_audience: "派出 chat 的执行助手；不归本主 chat 实施"
---

# Skill Seeker 任务包 — DSG 1.5 A10 入口 + L2-A 语义抽象层（仓库蒸馏）

> **本文用途**：定义一个明确范围的"仓库蒸馏 / SKILL 提取"任务，由用户派往独立 workspace 完成。**本主 chat 不实施**。
>
> **关键基调**（用户 2026-05-04 原话）：
> > 你先给我 DSG 1.5 A10 入口部分 和 L2-A 部分（L2-B 不需要这个）（学 ConceptGraph 门控和技术栈的 仓库蒸馏 skill 英语关键词任务，我自己派到新工作区自己完成的）

---

## §0 任务一句话

把 **ConceptGraph + 关联现代 open-vocab 仓库** 的 "**1.5 A10 入口侧的门控/检测/聚类**" 和 "**L2-A 语义抽象层**" 部分蒸馏成 ParrotCarriers 风格的 SKILL.md，给后续 DSG L1.5/L2-A 设计 chat 当输入资料。**严格不碰** L2-B（ParrotCarriers 已有自己的 RustworkX 工作记忆图，不要替换）和 L1.5 预加载 Node 池设计（用户自己做任务 1.4）。

---

## §1 范围（in / out）

### §1.1 In scope（要蒸馏）

| 主题 | ConceptGraph 中的对应 | 我们要拿什么 |
|:--|:--|:--|
| **A10 入口门控**（CV pipeline → 何时让一个检测/分割结果进入 DSG） | ConceptGraph 的 frame-level association + iou/visual sim 门控 | 门控阈值的设计原理 + 多帧 vote 策略 + 何时新建 vs 合并节点 |
| **A10 入口技术栈**（CV 模型组合）| SAM2 / DINOv2 / YOLO-World / Grounded-SAM / RAM 等组合 | 各模型在 pipeline 里的角色边界（分割 vs 描述 vs 类标 vs 重识别）+ 推理时序 |
| **L2-A 语义抽象**（节点的 class/category/affordance 抽象） | ConceptGraph 的 LLM 描述、层次类、语义嵌入 | 一个 detection 经过哪几步从 pixel → semantic node（描述 / 嵌入 / 关系）|
| **跨帧关联 / 重识别**（同一个物体多帧/多视角合并）| ConceptGraph 的 cross-view aggregation | 关联策略（IoU + visual similarity + spatial proximity）+ 失效场景 |
| **门控失败的可观测性**（什么时候 silently drop 一个 detection）| 散落在 ConceptGraph 多个文件 | 错误分类 + 原因日志格式 |

### §1.2 Out of scope（**严禁**蒸馏到 SKILL）

| 主题 | 为什么不要 |
|:--|:--|
| **L2-B 工作记忆图组织方式** | 我们有自己的 `parrot.dsg.l2b_graph` (RustworkX-backed)；不要用 ConceptGraph 的 LangChain / Open3D 等替换 |
| **L1.5 预加载 Node 池** | 用户自己做任务 1.4 |
| **3D scene 重建 / mesh / SLAM** | 我们 AR Foundation 已经处理 pose + 平面，不需要重建 mesh |
| **完整端到端 demo / GUI** | 我们要的是技术构件，不是套用 demo |
| **特定数据集 benchmark** (Replica / ScanNet)| 不相关，跳过 |
| **任何对 LiveKit / Unity / Brain agent 的"建议接入方式"** | 蒸馏出的 SKILL 是只读资料，不做产品集成建议 |

---

## §2 目标仓库 + 论文（按优先级）

### §2.1 主仓库（必读）

```
仓库: concept-graphs/concept-graphs
URL: https://github.com/concept-graphs/concept-graphs
论文: ConceptGraphs: Open-Vocabulary 3D Scene Graphs for Perception and Planning
      https://concept-graphs.github.io/
关注目录:
  - conceptgraph/slam/        ← 跨帧关联 / 节点合并门控
  - conceptgraph/scenegraph/  ← 节点抽象 + 关系抽象
  - conceptgraph/dataset/     ← 看 detection → node 的入口流程
  - configs/                  ← 阈值参数（IoU / sim 等）
忽略:
  - conceptgraph/llava/       ← 改用 Gemini，跳
  - 任何 viz/ 可视化代码      ← 与我们无关
```

### §2.2 次要仓库（按需查 — 不全读）

| 仓库 | 关注点 | 理由 |
|:--|:--|:--|
| `nyu-grail/OK-Robot` | ConceptGraph 后续工作 | 看 pipeline 在物理任务中的简化 |
| `vincent-leguen/OpenScene` | open-vocab 3D segmentation | 开放词汇的"类标"流程参考 |
| `xinyu1205/recognize-anything` | RAM / RAM++ 标签生成 | 给 SAM 分割结果起标签的方法 |
| `microsoft/Florence-2` | Open-vocab detection + caption | 跟 YOLO-World 互补的现代选择 |
| `IDEA-Research/Grounded-SAM` | SAM + 文本提示 | A10 入口"用文本指明感兴趣的东西"路径 |

### §2.3 关键论文

按必读 → 选读：

1. **ConceptGraphs**（Gu et al., ICRA 2024） — 主参考
2. **OpenMask3D**（Takmaz et al., NeurIPS 2023） — 开放词汇 mask 处理
3. **DINOv2**（Oquab et al., 2024） — visual feature backbone（ReID 基础）
4. **SAM2**（Ravi et al., 2024） — 当前 SOTA 分割 backbone
5. **YOLO-World**（Cheng et al., CVPR 2024） — 开放词汇检测
6. **Recognize Anything**（Zhang et al., 2023） — 给 mask 起标签

---

## §3 英语关键词清单（仓库 / 论文检索用）

### §3.1 入口门控相关

```
gating, frame-level association, multi-frame voting, IoU threshold,
visual similarity threshold, cosine similarity, mask matching,
detection clustering, association policy, persistence threshold,
spurious detection filter, cross-view aggregation, view consistency
```

### §3.2 检测 / 分割 / 描述 stack 相关

```
open-vocabulary detection, open-vocabulary segmentation,
zero-shot detection, mask proposal, dense prediction, detection
backbone, segmentation backbone, foundation model, vision encoder,
DINOv2 features, SAM2 mask decoder, YOLO-World detection,
RAM tagging, Grounded-SAM
```

### §3.3 ReID / 跨帧关联

```
re-identification, ReID, instance association, tracking across frames,
visual descriptor, embedding similarity, identity consistency,
appearance feature, feature aggregation, view fusion
```

### §3.4 语义抽象 / L2-A

```
semantic abstraction, scene graph node, object descriptor, node
description, hierarchical class, affordance reasoning, relational
edge, predicate extraction, scene context, spatial relation,
scene-level reasoning
```

### §3.5 失败模式 / 可观测性

```
detection failure mode, missed detection, false positive filter,
duplicate node prevention, ambiguous association, low-confidence
gate, drop reason, association log
```

---

## §4 输出格式（执行该 task 的 chat 的 deliverable）

输出一个 SKILL.md 文件，结构按 `.cursor/skills/graphiti/SKILL.md` 风格（参考其 frontmatter + Quick Reference + Key Concepts + Practical Usage 段落分布）。

### §4.1 必须的章节

```
---
name: dsg-l1-5-l2a-conceptgraph-distilled
description: ConceptGraph + open-vocab vision stack 蒸馏 — A10 入口门控 + L2-A 语义抽象。
             用于 DSG L1.5 / L2-A 设计 chat 的资料层；不是 L2-B 替代品。
---

# DSG 1.5 A10 入口 + L2-A — ConceptGraph 蒸馏

## 0. 范围与不做事项（最重要！）
   - in / out scope（拷贝本任务包 §1）
   - 严禁覆盖 ParrotCarriers L2-B 的注意

## 1. A10 入口门控
   - 门控决策树（什么时候让一个 detection 进 DSG）
   - 阈值参数表（IoU / visual sim / persistence）
   - 多帧 vote 策略
   - 失败模式 + drop reason 分类

## 2. A10 入口技术栈
   - 模型组合矩阵（SAM2 / DINOv2 / YOLO-World / RAM / Grounded-SAM）
   - 各模型在 pipeline 里的角色 + 输入输出 + GPU 成本
   - 推理时序（哪些可并行 / 哪些串行）

## 3. 跨帧关联 / 重识别
   - 关联策略（IoU + sim + spatial）
   - ReID embedding 选择（DINOv2 / 其他）
   - 失败场景（视角剧烈变化 / 遮挡 / 形变）

## 4. L2-A 语义抽象
   - detection → semantic node 的 N 步流程
   - 节点描述生成（LLM / VLM）
   - 关系 / 边 抽象
   - 与 L2-B 工作记忆 (我们已有) 的接口契约

## 5. 关键阈值与配置
   - 集中表格 — 来自 ConceptGraph configs/，标注每个的语义

## 6. 引用源代码 / 论文
   - file:line 引用 + 论文段落引用

## 7. 已知与 ParrotCarriers 现状的差异
   - 我们 SemanticNode 的 source_meta 字段会装什么
   - 我们 IngestRunner 的 commit_observation 与 ConceptGraph node-add 的差异
   - 我们没有但 ConceptGraph 有的能力（标注哪些是 Phase 5+ 才考虑）

## 8. 不蒸馏的清单（明确告诉读者跳过了什么）
```

### §4.2 SKILL.md frontmatter 字段

参考 `graphiti` skill 的 frontmatter 风格：

```yaml
---
name: dsg-l1-5-l2a-conceptgraph-distilled
description: <一句话用途>
distilled_from:
  - "<ConceptGraph repo + commit hash>"
  - "<其他 secondary repo + 关键文件路径>"
distilled_papers:
  - "<论文 1 引用>"
last_reviewed: <date>
ai_audience: "DSG L1.5 / L2-A 设计 chat（不替代 L2-B）"
---
```

### §4.3 不要做的事（**派出 chat 的硬约束**）

1. **不要**给出 ParrotCarriers 的实施代码 — SKILL 是资料，不是 PR
2. **不要**建议改 `parrot.dsg.l2b_graph` / `parrot.dsg.l2b_types` — 那是产品代码，不是蒸馏对象
3. **不要**在 SKILL 里塞"我们应该用 X 替换 Y" — 留给后续设计 chat 决定
4. **不要**全文 paste 整个仓库源码 — 抓关键 file:line + 关键函数签名 + 阈值表
5. **不要**蒸馏 SLAM / 3D 重建 / 可视化 / 数据集 benchmark
6. **不要**蒸馏 ConceptGraph 自己用的 LLM 调用方式（我们用 Gemini，蒸出来用不上）

---

## §5 派出 chat 的启动 prompt 模板

派该 task 时给 fresh chat 的提示：

```text
你是 ConceptGraph 仓库蒸馏助手。任务源 spec：
.cursor/memory/architecture/dsg_skill_seeker_l1_5_a10_l2a_20260504.md

第一步：读完 spec 全文。
第二步：clone / 浏览 §2 列出的仓库 + §2.3 论文摘要。
第三步：按 §3 关键词在仓库里 grep / 在论文里检索。
第四步：按 §4 章节结构产出一个 SKILL.md，写入
        .cursor/skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md

硬约束：§1.2 + §4.3 全部不可违反。

完成后回复：
  - SKILL.md 路径
  - 蒸馏覆盖了哪些 §4.1 章节
  - 跳过了什么 + 为什么（直接拷 §1.2 即可）
```

---

## §6 后续衔接

蒸馏完成后的 SKILL.md 是 **DSG L1.5 / L2-A 设计 chat** 的输入资料（不是设计本身）。设计 chat 的范围（用户自己做任务 1.4）：

- L1.5 预加载 Node 池设计（除 A10 入口部分）
- L1.5 状态生命周期
- L2-A 与现有 L2-B 的集成边界

那时蒸馏的 SKILL 当参考；如果发现 SKILL 漏了什么，回头补蒸馏。

---

## §7 引用

- 用户任务定义：本 chat 2026-05-04 conversation §P 范围确认 + 任务 1.1
- ParrotCarriers 现状：`adr_l1_5_source_dispatch_extension_space_20260504.md`
- 既有 skill 范式参考：`.cursor/skills/graphiti/SKILL.md`
- 既有 DSG L1.5 协议（**不要在 SKILL 里复述**，只引用）：`src/parrot/dsg/l1_5_protocol.py`
