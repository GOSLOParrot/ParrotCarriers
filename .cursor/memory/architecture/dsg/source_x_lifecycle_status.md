---
status: ratified
category: workspace-snapshot
status_note: "现有 ObservationSource 7 项 + 规划中的 GOSLO 主动发现 + Phase 5+ A10 占位的 source × 当前 lifecycle 处理状态对照表。仅记录现状，不设计差异化生命周期（Chat 2 的活）。"
last_reviewed: 2026-05-04
ai_priority: medium
ai_audience: "DSG 设计 chat — 在做 lifecycle 差异化设计前看哪个 source 当前哪条路径已通 / 哪条路径还是占位"
parent_doc: "workspace_index.md"
---

# Source × Lifecycle 现状对照表

> **本文用途**：把每一个 ObservationSource（已有的 7 项 + 规划中的 GOSLO 主动发现 + 与 A10 入口未来的 FrameSource 对应关系）当前是如何走完"upstream → IngestFilter → Observation → IngestRunner → SemanticNode → episode close → Graphiti archive"链路的，列成一表给 Chat 2 当起点。
>
> **本文不做**：不设计新 lifecycle、不裁决"哪个 source 应该有衰减"、不写 schema。

---

## §1 总览（按当前接入状态分类）

| Source | 当前状态 | 接入路径 | factory 注册 |
|:--|:--|:--|:--|
| `USER_TAG_OBSIDIAN` | ✅ 已接入 | Obsidian 双向链同步 → `user_tag_filter.py` → IngestRunner | 默认（空 dict）|
| `USER_EXPLICIT` | ✅ 已接入 | 用户口头 / UI → `text_source_filter.py` 派发 | 默认 |
| `IDENTIFY_OBJECT` | ✅ 已接入 | Brain `identify_object` tool 命中 → `tool_result_filter.py` | 默认 |
| `GEMINI_ORAL` | ✅ 已接入 | Gemini Live 转录 → `gemini_transcript_extractor.py` → `text_source_filter.py` | 默认 |
| `CV_A10` | 🟡 占位 | `cv_track_filter.py` 已存在但未连真实 A10 producer | 默认 |
| `CV_SENTINEL` | 🟡 占位 | 同 cv_track，未连真实 Sentinel | 默认 |
| `MOCK` | ✅ 测试桩 | 测试 fixture 用 | 默认 |
| **GOSLO 主动发现** | ❌ **未列入 enum** | 当前没有对应 ObservationSource 值；走哪个 filter 也未定 | 不存在 |
| **未来 A10 入口（per ConceptGraph）** | 🟡 上游合同已锁，下游 enum 已占位 | `FrameSource.A10_SAM2_DINOV2` / `A10_YOLO_WORLD` → `cv_track_filter` → `CV_A10` Observation | 默认（Chat 2 决定要不要扩） |

---

## §2 详细对照表

### §2.1 已接入的 4 个 source

#### USER_TAG_OBSIDIAN — Obsidian 双向链（**2026-05-06 用户决策：拆 3 子类**）

> 用户在 Q2.1 明确：Obsidian 来源**不是一类**，而是 3 个子类按"用法"分。详见 [dsg_decisions_master §3.2](dsg_decisions_master.md)。

| 子类 | 用途 | UUID 绑定 | 永久权威 | 进 L1.5 池 | 进 L2-B 节点 | 桶 | Graphiti 分区 |
|:--|:--|:--|:--|:--|:--|:--|:--|
| **Obsidian-Ref-加强** | 加强既有节点的 Ref（不是节点本身）| 是 | — | ❌ 不进 | 作为其他节点的 `meta.obsidian_uuid` 引用 | — | 生活区 |
| **Obsidian-设定-日常** | 介绍家里沙发 / 大家具 / 公用场景；可作其他节点引用 | 是（节点）| 是 | ✅ 进 | ✅ 是节点本身 | Obsidian 设定桶 | 生活区 |
| **Obsidian-设定-Roleplay** | Roleplay 模式自定义；人工维护；不日常使用；可把家设成中世纪 | 是 | 是 | ✅ 进（roleplay 模式时）| ✅ 是节点本身 | Roleplay 临时桶 | **roleplay 自定义区**（不污染生活区）|

**3 子类共享的字段填法**：

| 维度 | 现状 |
|:--|:--|
| 入口 | Obsidian 笔记中 `[[link]]` 双向链同步脚本（`src/scripts/sync_obsidian_to_graphiti.py`）|
| Filter | `dsg/ingest/user_tag_filter.py`（**Chat 2 设计：filter 内部按子类派发**）|
| 创建路径 | preload 时建 EXPECTED 节点；Filter 触发时升级为 TENTATIVE/CONFIRMED |
| `confirmation` 默认 | TENTATIVE（filter emit）→ 升 CONFIRMED（user-sourced 高 authority）|
| `salience` | FOREGROUND（user-sourced 升级）|
| `attention` | from_observation 默认 0.6（CONFIRMED）/ 0.35（其他）|
| `evidence_score` | 默认 0；30s repeat-seen +0.25；Graphiti enrich +0.15 |
| `provenance_stream_id` | 由 user_tag_filter 传入 |
| `obsidian_uuid` | 必填（双向链 uuid）|
| `source_meta` | **Chat 2 实施**：装 `{obsidian_path, file_mtime, double_link_count, profile: "ref"\|"daily"\|"roleplay"}` |
| GHOST 转换 | **无**（设定子类永远不 decay；Ref 子类不参与 lifecycle）|
| TTL | **无**（永不过期）|

**Chat 2 要解决的关键 gap**（Q2.1 已答）：

- ✅ **决定**：3 子类的"权威永久"标记 — 设定子类（日常 + Roleplay）永远不被低 authority 覆盖
- 🟡 **deferred-to-design**：Push-style 增量同步是否绕过 Graphiti 中转
- 🟡 **deferred-to-design**：roleplay 子类是否新增 NodeKind enum 值
- 🟡 **deferred-to-design**：一键切换 / 删除 roleplay 桶的接口形态

#### USER_EXPLICIT — 用户口头 / UI（**Q2.3 用户已决：拆 USER_VERBAL / USER_UI**）

| 维度 | 现状 |
|:--|:--|
| 入口 | 用户对 Gemini 说"那是张三的杯子" / Unity UI 主动标注 |
| Filter | `text_source_filter.py`（按 source 派发；USER_EXPLICIT 走"高 authority"分支）|
| `confirmation` 默认 | TENTATIVE → 30s repeat-seen 自动升 CONFIRMED |
| `salience` | FOREGROUND |
| `attention` | from_observation 默认 0.6（CONFIRMED）/ 0.35（其他）|
| GHOST 转换 | **无** |
| TTL | **无** |
| 关键 gap | "用户口头"与"UI 标注"是同一 source 但 confidence 来源不同 |
| Chat 2 已决 | ✅ 拆 USER_VERBAL（口头）+ USER_UI（UI 标注），具体实施留 Chat 2 |

#### IDENTIFY_OBJECT — Brain tool 命中（**Q2.3 用户已决：lastSeen 永久 + 状态字段不必多**）

| 维度 | 现状 |
|:--|:--|
| 入口 | LLM 调 `identify_object` tool → 三段流（L0 text fast match / L1 Graphiti / L2 option α）|
| Filter | `dsg/ingest/tool_result_filter.py`（命中结果转 Observation）|
| `confirmation` 默认 | CONFIRMED（高 authority）|
| `salience` | ACTIVE（不自动 FOREGROUND，等 user 介入）|
| `attention` | from_observation 默认 0.6 |
| `reference_image_path` | 命中时填入 `data/snapshots/objects/{uuid}/reference.jpg` |
| `last_sighting_path` | 后续 sighting 滚动更新 |
| GHOST 转换 | **无** |
| TTL | **无** — `lastSeen` 永久保留；其他降级状态不必那么多（"对话持续时间好像有个上限，平时不会用那么久"）|
| MemoryValidity 衔接 | graphiti 前的 `MemoryValidity 过滤器`（[`module_map_p2 §11.2`](../module_map_p2.md)，PLANNED P3）负责长期有效期判定 |
| Chat 2 已决 | ✅ lastSeen 永久 + 状态字段简化；具体降级规则按具体场景具体设计 |

#### GEMINI_ORAL — Gemini Live 口头提及（**Q2.3 用户已决：拆"泛泛之谈" vs "当前场景实体"**）

> **注**：[LineB](../lineb_implementation_completion_20260504.md) 完成后该 source 模块已改名为 `transcript_extractor.py`（旧名 alias 保留向后兼容）；任何 LLM 助手的口头提及都走这条 source，不局限 Gemini Realtime。

| 维度 | 现状 |
|:--|:--|
| 入口 | Gemini Live / LineB STT 转录文本 → `transcript_extractor.py` 抽实体 |
| Filter | `text_source_filter.py`（GEMINI_ORAL 分支，priority 30）|
| `confirmation` 默认 | TENTATIVE |
| `salience` | ACTIVE |
| `attention` | from_observation 默认 0.35 |
| GHOST 转换 | **无** |
| TTL | **无** |
| 关键 gap | Gemini 口头提及的实体可能是泛泛之谈（"我喜欢咖啡"）vs 当前场景实体（"那杯咖啡"）|
| Chat 2 已决 | ✅ **必须区分**；具体规则参考 [`dsg-l2b-node-organization-options §3.2`](../../../skills/dsg-l2b-node-organization-options/SKILL.md) 跨源合并信号（embedding sim / canonical_name / 共现 / 时空一致）|

### §2.2 占位但未真实接入的 source

#### CV_A10 — A10 视觉管线（**Q2.4 用户已决：推迟到 P3 / A10 独立设计 chat**）

| 维度 | 现状 |
|:--|:--|
| 入口 | **未接入** — A10 节点未启动；`l1_5_protocol.SensorFrame.source = A10_SAM2_DINOV2 / A10_YOLO_WORLD` 是 enum 占位 |
| Filter | `cv_track_filter.py` 文件存在但 `process_frame` 几乎是 stub |
| `_SOURCE_PRIORITY` | 60 |
| factory | 默认空 dict；候选字段（[`dsg-l1-5-l2a-conceptgraph-distilled §3.4`](../../../skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md)）：`clip_ft / track_id / num_frames_seen / vlm_object_tag / bbox_3d_center / last_seen_frame` |
| 关键 gap | A10 producer / cv_track_filter / ConceptGraph 门控阈值都未接入 |
| Chat 2 行动 | **不展开**；只在 Node 基础类设计时考虑扩展性（factory hook 已就位）；详细设计推到 P3 / A10 独立设计 chat |
| P3 要解决 | (1) A10 适配 AR 坐标 + 手机传感器数据 (2) SAM2 + DINOv2 + ConceptGraph 集成 (3) 软件建图导入 + VPS (4) 不可能事件 / 同类第二实例规则 (5) 跨源 ReID（reid_hash） |

#### CV_SENTINEL — 笔记本残血版

| 维度 | 现状 |
|:--|:--|
| 入口 | **未接入** — Sentinel 是 P4 的 fallback，不是 P2.5 路径 |
| Filter | 与 cv_track_filter 共用 |
| `_SOURCE_PRIORITY` | 40 |
| 关键 gap | 与 CV_A10 类似 |
| Chat 2 要回答 | Sentinel 与 A10 共用 cv_track_filter 还是各自一个？|

#### MOCK — 测试桩

| 维度 | 现状 |
|:--|:--|
| 入口 | 测试 fixture |
| `_SOURCE_PRIORITY` | 10（最低）|
| 关键 gap | 无 |
| Chat 2 要回答 | 不必（测试用，不参与 lifecycle 设计）|

### §2.3 未列入 enum 的 source

#### GOSLO 主动发现 — Brain 自主好奇（**Q2.2 用户已决方向**）

| 维度 | 现状 / 决策 |
|:--|:--|
| 概念定位 | GOSLO 主动观察周围环境（"咦，那个新东西是什么？"）→ 触发 identify_object → 创建节点 |
| 入口 | 当前路径：Brain context injector 看到注意力 hint → LLM 自主调 identify_object → 走 IDENTIFY_OBJECT source |
| **Q2.2.a enum 处理**（仍 TBD）| 3 选 1 由 Chat 2 决定：(1) 新增 `GOSLO_AUTONOMOUS` enum / (2) `source_meta.triggered_by` 字段细分 / (3) 独立 filter |
| **优先级**（已决）| ✅ 主动发现节点 priority **<** 被用户问出来的节点 |
| **TTL**（已决）| ✅ 短 TTL（避免 GOSLO 好奇刷屏）；具体时长 Chat 2 定 |
| **是否参与 L2-B + 观察者 + 时间轴 + L3**（已决）| ✅ 参与全链路（包括对话快照记录、Ref 信息留档、L3 / 用户情绪状态归档）|
| **是否阻塞对话**（仍 TBD）| 🟡 用户原话"我现在不知道是否 GOSLO 使用了这个工具就会说话，毕竟这个工具是主动发现会阻塞对话，再看吧"|

> **注**：加新 enum **不动 wire**（ADR-L1.5-001 §2.1 Q1 决定 source 仅 Python 层）/ **不触发 cs_parity**（不在 EcpEventSource）/ 会影响 `_SOURCE_PRIORITY` 排序需在 ADR 修订说明。

### §2.4 未来 A10 入口与 ConceptGraph 蒸馏的对应

| ConceptGraph 概念 | 本工作区位置 |
|:--|:--|
| frame-level association（IoU + CLIP）| 上游 producer（A10 节点）的事，不进 ObservationSource；产物是 `Detection` |
| 多帧 vote 决定是否 admit | 上游 producer 的事；产物是 `SensorFrame` |
| `clip_ft` / `track_id` 跨帧融合 | A10 producer 维护；接入 L2-B 时进 `source_meta` |
| L2-A 节点描述（VLM caption + LLM refine）| L2-A 占位；当前不接入 L2-B |
| 关系边（on / in / 邻接）| L2-A 边；当前 L2-B EdgeKind 不重叠 |

详见 [ConceptGraph SKILL §7 与 ParrotCarriers 现状的差异分析](../../../skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md)。

---

## §3 公共字段赋值矩阵

> 即"任意 source 的 Observation → SemanticNode 时，字段如何被填"。

| SemanticNode 字段 | 默认值 / 赋值规则 | 备注 |
|:--|:--|:--|
| `uuid` | `uuid4()[:12]` | 自生成 |
| `kind` | `obs.kind`（默认 OBJECT）| Observation 显式指定 |
| `label` | `obs.label` | 必填 |
| `graphiti_uuid` | `obs.graphiti_uuid` | 仅 Graphiti 已知节点带 |
| `obsidian_uuid` | `obs.obsidian_uuid` | 仅 Obsidian 双向链节点带 |
| `description` | `obs.description` | 可选 |
| `known_facts` | `[obs.description]` if obs.description else `[]` | 后续 merge 追加 |
| `confirmation` | `obs.confirmation`（默认 TENTATIVE）| 30s repeat-seen → CONFIRMED；高 authority merge → 升级 |
| `evidence_score` | `obs.confidence` | repeat-seen +0.25；Graphiti enrich +0.15 |
| `attention` | 0.6 (CONFIRMED) / 0.35 (其他) | from_observation；后续 attention/threshold 不写这里 |
| `salience` | ACTIVE 默认；user-sourced 升 FOREGROUND；preload 默认 BACKGROUND | runner._observation_to_node |
| `novelty` | 1.0 默认 | **当前无衰减写者** |
| `habituation_count` | 0 | **当前无累加写者** |
| `last_attended` | now | `touch()` 更新 |
| `last_seen_this_session` | now | `touch()` 更新 |
| `interaction_count` | 0 | `touch()` +1 |
| `episode_id` | "" | `assign_node_to_current_episode()` 设置 |
| `provenance_stream_id` | `obs.provenance_stream_id` | L0 EventEnvelope id |
| `time_span` | (0.0, None) | EVENT-kind 才用 |
| `reference_image_path` | `obs.reference_image_path` | identify_object 命中或用户上传 |
| `last_sighting_path` | `obs.last_sighting_path` | sighting 时滚动 |
| `source` | `obs.source.value` | from_observation 注入 |
| `source_meta` | `factory(obs)` | **所有 source 当前返回 `{}`** |

**关键观察**：所有 source 的差异**仅体现**在 `_SOURCE_PRIORITY` 数值和 `salience` 升级（user-sourced），其他字段填法**完全一致**。这是"**简单**"的真实形状 — Chat 2 设计差异化时这是基线。

**2026-05-06 Q2.3 用户已决**：`_SOURCE_PRIORITY` 数值表当前不动；**留切换开关** — 受场景切换 / 触发器 / GOSLO 状态影响（如 roleplay 模式时调权重）。具体开关形态由 Chat 2 决定。

---

## §4 触发现状与 Chat 2 入口

每行的"Chat 2 要回答"集中起来 → [open_questions_for_design_chat.md](open_questions_for_design_chat.md) + [dsg_decisions_master.md](dsg_decisions_master.md) §3-§4。

---

## §5 P3 / A10 独立设计 chat 边界

以下推到 P3，Chat 2 不展开（只在设计稿里**预留位置 + 显式标 P3**）：

| 项 | 来源 | 关联 source |
|:--|:--|:--|
| A10 接入 + ConceptGraph 集成 | Q2.4 已决 | CV_A10 |
| A10 节点自动 confidence decay（外观漂移）| ConceptGraph SKILL §8a Q8 | CV_A10 |
| A10 与 IDENTIFY_OBJECT 节点跨源 ReID（reid_hash）| Q2.4 已决 | CV_A10 + IDENTIFY_OBJECT |
| AR 坐标 + 手机传感器 + SAM2/DINOv2 适配 | Q2.4 已决 | CV_A10 |
| 软件建图导入 Map → Unity + VPS 对齐 | Q2.4 已决 | L2-A 占位 |
| 不可能事件（电视瞬移）报错不进 L1.5 标不可信 | dsg_decisions_master §1.2 | 跨 source |
| 同类第二实例需用户确认才进 L2-B | dsg_decisions_master §1.2 | 跨 source |
| MemoryValidity 过滤器 Ebbinghaus 衰减公式 + 置信度阈值 | [`module_map_p2 §11.2`](../module_map_p2.md) | 全 source 归档时 |
