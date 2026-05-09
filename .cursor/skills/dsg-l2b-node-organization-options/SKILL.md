---
name: dsg-l2b-node-organization-options
description: >
  DSG L2-B（RustworkX 潜意识索引）的 Node / Edge 组织方式**候选选项**清单。
  对接来源：L1.5 入口 Node + Graphiti（已有 skill）+ 其他参考源。
  这是**选项库**，不是设计——具体方案由后续设计 chat 决定。
ai_audience: "DSG L2-B 设计 chat（结合 ParrotCarriers 已定架构调整）"
last_reviewed: 2026-05-05
distilled_from_primary:
  - "HippoRAG (Gutiérrez et al., NeurIPS 2024, arXiv:2405.14831) — 海马索引 + PPR 检索"
  - "AriGraph (Anokhin et al., 2024, arXiv:2407.04363) — episodic + semantic 双类节点"
distilled_from_classic_concepts:
  - "Hippocampal Indexing Theory (Teyler & Rudy, 2007) — 节点是指针不是存储"
  - "CLS Theory (McClelland, McNaughton, O'Reilly, 1995) — 快/慢双系统"
  - "Spreading Activation (Collins & Loftus, 1975) — 联想检索算法"
  - "Episodic vs Semantic Memory (Tulving, 1972) — 双类记忆理论基础"
related_distill_raw_archived:
  # 2026-05-09 NewZone/ 物理删除；HippoRAG / AriGraph 蒸馏精华已入本 SKILL §1.5 / §6 / §8
  - "HippoRAG (NeurIPS'24) → 本 SKILL §6 + §354 行索引"
  - "AriGraph → 本 SKILL §6 + §355 行索引"
related_skills:
  - "graphiti (已用 — Graphiti GraphRAG 接入)"
  - "dsg-rustworkx-master (路由总入口)"
  - "dsg-attention-schema-papers (注意力/图式/记忆论文索引)"
  - "dsg-l1-5-l2a-conceptgraph-distilled (L1.5 入口 Node 来源之一)"
---

# DSG L2-B Node 组织方式 — 选项清单（**非设计**）

> **本 SKILL 是选项库**。每条都标注：**来源 / 真实度 / 与 ParrotCarriers 既有架构的契合度**。
> 设计 chat 来时根据 ParrotCarriers 实际架构选择/裁剪/合并。
>
> **不在本 SKILL 中决定的事项**：节点持久化格式、并发模型、淘汰策略具体阈值、
> 与 LiveKit/Unity 的 wire format。

---

## 0. 索引明确：论文 / 仿生算法 / 组织方式 三栏

| 论文 / 仓库 | 仿生算法 / 机制 | 提供的组织方式建议 | 真实度 |
|:--|:--|:--|:--|
| **HippoRAG** (NeurIPS'24) | Personalized PageRank 扩散激活 | 双类节点：entity (cortical concept) + passage (episodic pointer)；同义边合并；增量索引 | ✅ 一手仓库蒸馏 |
| **AriGraph** (2024) | Episodic ↔ Semantic 桥接边 | 双类节点：episodic (时间戳事件) + semantic (实体属性)；triplet 抽取建图；node merge | ✅ 一手仓库蒸馏 |
| **SLM** (qualixar) | TF-IDF + Leiden 聚类 + 多 Profile + 渐进压缩 | 多 Profile/桶子图、渐进压缩、二元节点+关系；**与 DSG 9 层结构直接对照**（§1.5） | ✅ 一手仓库蒸馏 |
| **Graphiti** (已有 skill) | 时间有效性 + group_id 多分区 | EntityNode / EpisodicNode / CommunityNode 三类；prescribed + learned ontology | ✅ 已有 skill 在用 |
| **Hippocampal Indexing** (Teyler-Rudy 2007) | 海马存指针、皮层存内容 | "节点是 pointer" vs "节点存储" 的二分 | ⚠️ 公知概念 |
| **CLS Theory** (McClelland 1995) | 快/慢双系统互补 | L1.5 (快) ↔ L2-A/B (慢整合) 的双速架构动机 | ⚠️ 公知概念 |
| **Spreading Activation** (Collins-Loftus 1975) | 节点激活按边权重扩散 | 检索算法：种子节点 → 衰减扩散 → top-k | ⚠️ 公知概念 |
| **Tulving 1972** | Episodic vs Semantic 二分 | Node 类型分类的理论根基 | ⚠️ 公知概念 |

> **公知概念**：理论框架成熟、被广泛引用，但本 skill 没有逐字读原文；用作概念锚点不作论据。

---

## 1. Node 类型分类的候选选项

### 1.1 选项 A — 双类（Episodic / Semantic）— 来自 AriGraph + Tulving 1972

```
EpisodicNode
  - 来源：单次具体事件（观察 / 对话 / 用户输入）
  - 字段：timestamp, source_event_id, raw_payload_pointer
  - 生命周期：天然有效期短，可衰减

SemanticNode
  - 来源：从多个 episode 提炼的稳定实体/概念
  - 字段：canonical_name, attributes_dict, embedding
  - 生命周期：长期，跨会话稳定
```

桥接：`episodic --MENTIONS--> semantic`（episode 引用其涉及的语义实体）

**契合 ParrotCarriers 的点**：
- L1.5 入口的 CV detection 天然是 episodic（每帧一观察）
- Graphiti 的 EntityNode / EpisodicNode 已经是这个范式
- AR 锚点本身有时间戳 → episodic 友好

**不契合 / 需调整**：
- ParrotCarriers 节点来源**多源异构**（CV + 语音 + 用户输入 + Graphiti 预加载），
  仅二分可能不够，需要看是否要细分

### 1.2 选项 B — 三类（Entity / Passage / Pointer）— 来自 HippoRAG

```
EntityNode    # 概念节点（cortical concept）
  - 字段：name, embedding, source_count

PassageNode   # 文段/事件节点（hippocampal index 模式 — 是指针不是内容）
  - 字段：content_pointer (URI / DB row id), timestamp
  - **关键设计**：节点本身**不存内容**，只存指向外部存储的指针

SynonymEdge   # 同义边（用于节点去重/合并）
RelationEdge  # 关系边（OpenIE 三元组）
```

**契合点**：
- "节点是指针不是存储"模式直接对应"潜意识索引"角色
- 与 L2-B = RustworkX 内存图的轻量需求匹配（不要把大 payload 塞内存图）
- 和 Graphiti 的 EpisodicNode（含原始文本 episode）形成互补：L2-B 存指针，
  Graphiti 存原始 episode

**不契合 / 需调整**：
- HippoRAG 是 OpenIE 三元组驱动；ParrotCarriers 入口（CV detection / AR 锚点）
  不是文本三元组，需要适配

### 1.3 选项 C — 多源混合（按 source_meta 区分）

```
Node (统一类型)
  - source: enum {CV_L15, GRAPHITI, USER_INPUT, AR_ANCHOR, ...}
  - source_meta: dict (各 source 自己的字段约定)
  - canonical_id: str  # 跨源去重的统一 ID
  - last_seen / activation: float
```

边按 source 标记：`source_edge: enum {SAME_SOURCE, CROSS_SOURCE_LINK, ...}`

**契合点**：
- 直接体现"L2-B 是潜意识索引、连接异构来源"的角色
- 易于实现"按源筛选"、"按源衰减不同速度"

**不契合 / 需调整**：
- 缺少类型区分（episodic vs semantic 的语义层差异被抹平）
- 易演化为"什么都往里塞"的反模式

### 1.4 选项 D — 复合（episodic/semantic × source 双正交标签）

```
Node
  - kind: {episodic, semantic}       # 来自 AriGraph/Tulving
  - source: {CV_L15, GRAPHITI, ...}  # 来自异构入口
  - is_pointer: bool                 # 海马索引模式标记
  - payload | content_pointer        # 二选一（按 is_pointer）
```

**契合点**：
- 同时表达"什么类型的记忆"和"哪里来的"——两个独立维度
- `is_pointer` 让"潜意识索引 vs 直接存储"在节点级别可选

**不契合 / 需调整**：
- 字段较多，初期可能用不到——按需开放

### 1.5 选项 E — SLM 风格多层池架构对比（**重要：架构相似性**）

> 来自 SLM 仓库 Gemini 蒸馏（原 `NewZone/distill_output/dsg/superlocalmemory/` 2026-05-09 物理删除；精华已入本节正文）

SLM 与 ParrotCarriers DSG **高度结构相似**——两者都是中间层认知架构。**对照表**：

| SLM 9 层 | ParrotCarriers DSG（用户定义） | Node 组织含义 |
|:--|:--|:--|
| L1 Data Ingestion | 多源数据持久层（下层） | 原始事件入口 |
| L2 Memory Processing | L1.5 Node 池 + 规范化 | 标准化为 Node 候选 |
| L3 Context Engine | L1.5 池上层（任务上下文匹配） | 当前会话相关 Node 筛选 |
| **L4 Knowledge Graph (RustworkX)** | **L2-B（RustworkX 潜意识索引）** | **核心组织层** |
| L5 Adaptive Learning | L3 观察层 + Processor | 模式学习 / soft prompt |
| L6 Privacy | （持久层合规） | 不在 DSG 内 |
| L7 Search & Retrieval | L3 检索 / L2-B 内部检索 | 多通道融合 |
| L8 Multi-Agent | （ParrotCarriers 总线层） | 不在 DSG 内 |
| L9 IDE Integration | LiveKit / Unity wire | 不在 DSG 内 |

**SLM 在 L4 的具体组织（可学）**：
- TF-IDF 抽实体 + Leiden 聚类（**注意**：Leiden 需要 igraph，不是纯 RustworkX）
- **多 Profile 隔离**（不同项目/客户独立子图）→ 直接对应你说的"多 Node 桶"
- **渐进式总结压缩**：老节点被分层压缩归档（节省内存）
- 实体节点 + 关系边的二元简单结构（不细分 episodic/semantic）

**契合点（直接学习）**：
- **多 Profile / 多桶 → 子图天然分层**（直接服务 §6.5）
- **渐进压缩**作为 L2-B 衰减的一种工程实现（与 TWF / 量子化互补）
- "中间层"角色的代码组织参考（看 SLM 的 `src/` 文件分包）

**不契合 / 需调整**：
- SLM 是离线 Workspace 工具；DSG 是在线 AR + 语音
- SLM 节点二元简单；DSG 多源异构需要更细分类
- SLM 用 Leiden + igraph；ParrotCarriers 选纯 RustworkX 路线

---

## 2. Edge 类型分类的候选选项

| 边类型 | 含义 | 源参考 |
|:--|:--|:--|
| `MENTIONS` | episodic → semantic（该事件涉及该实体） | AriGraph |
| `SYNONYM` / `COREF` | 节点合并/同义指向 | HippoRAG |
| `RELATION` | OpenIE 风格三元组关系 | HippoRAG |
| `TEMPORAL_NEXT` | 时序后继（episodic 之间） | Graphiti（时间有效性） |
| `SPATIAL_NEAR` | AR 空间接近 | ParrotCarriers AR 特有 |
| `CROSS_SOURCE_LINK` | 跨源同实体桥接（CV-L15 节点 ↔ Graphiti 节点） | 选项 C/D 的衍生 |
| `INHIBITORY` | 抑制性边（带负权） | 案例.md §29 注：RustworkX 原生有限 |
| `BYPASS_SHORTCUT` | 反射式快路径 | 案例.md §120（**风险高**，慎用） |

---

## 3. 跨源连接方式（Graphiti / 其他 Ref → L2-B 索引）

### 3.1 预加载策略候选

| 策略 | 描述 | 取舍 |
|:--|:--|:--|
| **眼前预加载（Eager）** | 启动时全量同步 Graphiti 实体到 L2-B 节点 | 启动慢、内存大、检索快 |
| **懒加载（Lazy）** | L2-B 只存指针，第一次访问时拉取 Graphiti | 启动快、首次查询慢 |
| **热区预加载（Hot-set Eager）** | 按使用频率/重要性预加载 top-N | 折中、需要重要性评分 |
| **双层缓存** | L2-B 内存 + Graphiti 持久层，LRU 同步 | 复杂、最灵活 |

### 3.2 跨源节点合并的判定信号

| 信号 | 来源参考 |
|:--|:--|
| 实体 embedding 余弦相似度 > θ | HippoRAG synonym edge |
| canonical_name 字符串匹配 | Graphiti dedup |
| 共现频次（appear in same episode） | AriGraph |
| 时空一致性（同一时刻同一空间） | ParrotCarriers AR 特有 |

> **不在本 SKILL 决定**：阈值 θ 取多少、签证策略（merge 自动/人工/弱合并）—— 设计 chat 决定。

---

## 4. 海马索引模式（is_pointer）的应用建议

> 来自 Teyler & Rudy 2007 的"hippocampal indexing theory"：海马区**不存储**记忆内容，
> 只存储指向新皮层 trace 的索引。

**在 DSG L2-B 中的对应**：

| 节点类型 | 推荐 is_pointer | 原因 |
|:--|:--|:--|
| 高频访问的**索引型** Node（实体名、概念） | False（直接存内容/embedding） | 命中即用 |
| 低频访问的**事件型** Node（具体观察） | True（存指针指向 Graphiti / object store） | 节省内存 |
| **跨源桥接** Node | True（指向源 Graphiti 节点 ID） | 不复制，只引用 |
| **检索热点** Node | False | 缓存命中 |

**好处**：L2-B 内存图保持瘦身，潜意识扩散激活（PPR / spreading activation）只走索引层；
真正需要 payload 时再去对应源拉取。

---

## 5. 检索算法候选（潜意识联想式）

| 算法 | 来源 | 适用 | 注意 |
|:--|:--|:--|:--|
| **Personalized PageRank** | HippoRAG | 多种子节点扩散 | 需迭代收敛，O(V) 每次 |
| **Spreading Activation** | Collins-Loftus 1975 | 单种子衰减扩散 | 简单、低成本、可外挂注意力函数 |
| **限深 BFS + 评分** | 案例.md §122 范式四 | 实时低延迟 | 跳数硬上界 4（见 dsg-rustworkx-master §3.5） |
| **GAT 风格邻域注意力** | dsg-attention-schema-papers §1.1 | 节点激活打分 | 可作"外挂注意力算法"（无需训练时手工设权重） |
| **子图同构** | RustworkX vf2_mapping + call_limit | 经验匹配 | 必带 call_limit 防舌尖现象（案例.md §109） |

> **重要**：用户场景是"灵活组织 + 潜意识索引"——**注意力算法可以是外挂插件**，
> 不必在 L2-B 内核固化某一种。设计 chat 应保留 strategy pattern。

---

## 6. 与 ParrotCarriers 既有架构的接口约束（**已知**）

| 既有组件 | L2-B 接口形态 | 来源 |
|:--|:--|:--|
| **L1.5 入口** | 接收不同类的 Node（CV detection / AR 锚点 / 其他源） | 用户已定 |
| **Graphiti** | L2-B 索引 Graphiti 节点；具体接入策略 §3 | graphiti skill 在用 |
| **L2-A 语义抽象** | L2-A 输出语义节点 → L2-B 索引 | dsg-l1-5-l2a-conceptgraph-distilled §4 |
| **RustworkX** | L2-B 底层骨架 | dsg-rustworkx-master §1 |

---

## 6.5 L2-B 内部分层 / 子图组织选项（**用户提示：L2-B 总层下也可分层**）

L2-B 不必是单一扁平图。以下是子图/分层组织的候选模式：

### 6.5.1 选项 P1 — 按 Source 分桶（每源独立子图）

```
L2-B
├── google_calendar_subgraph   # Google 今日日程 Node 桶
├── obsidian_subgraph          # Obsidian 设定桶
├── roleplay_temp_subgraph     # 临时 RolePlay 设定桶
├── cv_l15_subgraph            # L1.5 CV 入口桶
└── cross_subgraph_links       # 跨桶桥接边
```

- **优点**：源隔离清晰、按桶独立衰减、易并发
- **缺点**：跨源检索需要先聚合再去重；潜意识扩散激活跨桶时复杂
- **来源参考**：SLM 多 Profile 模式 + 用户原话

### 6.5.2 选项 P2 — 按时间尺度分层（短期/中期/长期）

```
L2-B
├── working_memory_layer    # 当前会话/最近 N 帧（高激活、易衰减）
├── short_term_layer        # 当日（中等衰减）
└── long_term_layer         # 跨会话稳定（极慢衰减）
```

- **优点**：天然映射 CLS 双系统理论（dsg-attention-schema-papers §5.2）
- **缺点**：节点跨层迁移需要规则（提升/下沉条件）
- **来源参考**：CLS Theory + 海马 → 皮层 systems consolidation

### 6.5.3 选项 P3 — 按 Node 类型分层（episodic / semantic / pointer）

```
L2-B
├── pointer_layer    # 是 pointer 的节点（瘦身的索引层）
├── semantic_layer   # 实体/概念节点（稠密激活）
└── episodic_layer   # 事件节点（稀疏，时间标记）
```

- **优点**：与海马索引理论 + AriGraph 双类节点直接对应
- **缺点**：层间频繁桥接边可能数量爆炸

### 6.5.4 选项 P4 — Hybrid（多正交维度）

```
L2-B 节点同时被多个 view 索引：
- view_by_source: {google, obsidian, roleplay, cv, ...}
- view_by_kind: {episodic, semantic}
- view_by_layer: {working, short, long}
```

RustworkX 实现：
- 主图 = 全部节点 + 全部边
- View = 按属性筛选的子图（`g.subgraph([nodes_filtered_by_attr])`）
- 可以是 lazy 视图（不复制底层数据）

- **优点**：最灵活，三种正交维度自由组合
- **缺点**：实现复杂，索引维护成本高

### 6.5.5 跨子图边的语义

| 边类型 | 用途 |
|:--|:--|
| `INTRA_SUBGRAPH` | 同一桶/层内部边（高频遍历） |
| `CROSS_SUBGRAPH` | 跨桶/层桥接（潜意识联想跨域激活） |
| `LAYER_PROMOTION` | 短期 → 长期迁移记录（systems consolidation 类比） |

> **不在本 SKILL 决定**：用 P1/P2/P3/P4 哪种，每层节点上限，跨子图扩散允许深度。

---

## 7. 留给设计 chat 的开放问题（**不在本 SKILL 答**）

1. 选 §1 的哪个选项（A/B/C/D 或自创混合）？
2. is_pointer 模式的存储后端是什么（Graphiti / SQLite / 内存对象池）？
3. 跨源合并的相似度阈值 θ？
4. 检索算法选 §5 哪一个作为默认？是否支持插件式切换？
5. 衰减节奏 / 淘汰策略具体公式？
6. AR 锚点漂移时（见 dsg-l1-5-l2a-conceptgraph-distilled §8a）L2-B 节点的位置字段如何处理？
7. 与 LiveKit / Unity wire format 的边界？
8. L2-B 内部分层选 §6.5 的 P1/P2/P3/P4 哪种？是否多维正交（P4）？
9. 节点跨层迁移规则（提升/下沉条件）？
10. 各层 / 各桶的衰减速率不同？

---

## 8. 快速参考：原始素材去哪查

| 我想看 | 去 |
|:--|:--|
| HippoRAG 完整蒸馏（PPR / OpenIE / 节点字段） | 本 SKILL §6（原 `NewZone/distill_output/dsg_l2b_org_raw/HippoRAG/SKILL.md` 2026-05-09 删除） |
| AriGraph 完整蒸馏（双类节点 / triplet / 工作集） | 本 SKILL §6（原 `NewZone/distill_output/dsg_l2b_org_raw/AriGraph/SKILL.md` 2026-05-09 删除） |
| Graphiti 节点类型 / group_id / 时间有效性 | `.cursor/skills/graphiti/SKILL.md` |
| 注意力算法摘要（GAT/DySAT/AGCN/G-HAM） | `.cursor/skills/dsg-attention-schema-papers/SKILL.md` §1 |
| 经典记忆理论（Tulving/CLS/Hippocampal Indexing/Spreading Act） | 本 SKILL §0 索引 + dsg-attention-schema-papers §5（待加） |
| RustworkX 实操技巧 | `.cursor/skills/dsg-rustworkx-master/SKILL.md` §2 |
| 案例研究综述（仿生范式） | `.cursor/skills/dsg-rustworkx-master/SKILL.md` §3.5（原 `NewZone/RustworkX 图模拟研究案例.md` §119–§122 已蒸馏入该 skill） |
