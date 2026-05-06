---
name: dsg-attention-schema-papers
description: >
  注意力机制（GAT / DySAT / 图聚类 over-globalization）+ 图式理论（Schema Theory）+
  自动/受控加工（Automatic Processing）+ 临床脑图谱（G-HAM, ASD/MDD）的论文索引。
  服务于 ParrotCarriers DSG L2-A/L2-B 的注意力分配、衰减、子图激活、过度全局化防御等设计决策。
distilled_papers:
  - "Veličković et al., 2018 — Graph Attention Networks (GAT), arXiv:1710.10903"
  - "Sankar et al., 2020 — DySAT: Deep Neural Representation Learning on Dynamic Graphs, arXiv:1812.09430"
  - "Yang et al., 2025 — Attention Beyond Neighborhoods: Reviving Transformer for Graph Clustering, arXiv:2509.15024"
  - "Zhang et al., 2019 — Graph-based Hierarchical Attention Model (G-HAM) for Movement Intention Detection from EEG, IEEE TNSRE, PMID 31562095"
  - "Bartlett, F.C., 1932 — Remembering: A Study in Experimental and Social Psychology (Schema Theory 经典)"
  - "Anderson, R.C., 1977 — Schema-directed processes in language comprehension"
  - "Rumelhart, D.E., 1980 — Schemata: The building blocks of cognition"
  - "Schneider & Shiffrin, 1977 — Controlled and automatic human information processing (Psychological Review)"
  - "Naito et al., 2009 — Odd Sensation Induced by Moving-Phantom which Triggers Subconscious Motor Program (案例 §[27])"
  - "Sickafus, E.N. — Heuristics for Solving Technical Problems (TRIZ-style schema heuristics, 案例 §[26])"
  - "ABIDE-based ASD sMRI graph studies (案例 §[29], 二传引用)"
  - "MDD whole-brain consensus network analysis (案例 §[30], 二传引用)"
  - "Tulving 1972 — Episodic vs Semantic Memory (经典)"
  - "McClelland, McNaughton, O'Reilly 1995 — Complementary Learning Systems (经典)"
  - "Teyler & Rudy 2007 — Hippocampal Indexing Theory (经典 — L2-B 指针节点的依据)"
  - "Collins & Loftus 1975 — Spreading Activation Theory (经典)"
last_reviewed: 2026-05-05
ai_audience: "DSG L2-A 注意力分配 / L2-B 衰减与抑制 / 全局拓扑管控的设计 chat"
---

# DSG 注意力机制与图式理论 — 论文索引与机制摘要

> **本 SKILL 是论文索引型资料**：每个条目给出（1）真实引用，（2）核心论点，（3）机制摘要，
> （4）对 ParrotCarriers DSG 的适用面，（5）不适用的边界。**不实施代码，不替代设计 chat。**

## 0. 路由表（按 DSG 决策点）

| DSG 决策问题 | 该问题对应的论文条目 |
|:--|:--|
| 节点注意力分配如何打分？ | §1.1 GAT / §1.2 DySAT |
| 跨时间快照的注意力如何融合？ | §1.2 DySAT |
| 大图全局注意力为什么会反向退化？ | §1.3 AGCN over-globalization |
| EEG / 多通道感官输入如何分层注意力？ | §1.4 G-HAM |
| 检索时如何用"图式（schema）"匹配历史经验？ | §2.1 Bartlett / §2.2 Rumelhart |
| 系统 1 / 系统 2 / 自动 vs 受控如何在 DSG 表达？ | §3.1 Schneider-Shiffrin / §3.2 Naito |
| 图拓扑指标如何标记"病变 / 异常子图"？ | §4.1 ASD / §4.2 MDD |
| L2-B 节点应分几类（episodic/semantic）？ | §5.1 Tulving |
| L1.5/L2-A/L2-B 的速度分层有生物学依据吗？ | §5.2 CLS Theory |
| L2-B 节点是存内容还是存指针？ | §5.3 Hippocampal Indexing |
| L2-B 检索算法最简候选？ | §5.4 Spreading Activation |

---

## 1. 注意力机制系列论文

### 1.1 Veličković et al., 2018 — Graph Attention Networks (GAT)

- **引用**：`arXiv:1710.10903` (Veličković, Cucurullo, Casanova, Romero, Liò, Bengio, ICLR 2018)
- **核心论点**：在图节点上做掩码自注意力（masked self-attention），让节点对其邻居加权聚合，
  权重是隐式学习的（不依赖谱分解、不依赖完整图结构、可归纳学到未见图）。

- **机制摘要**：
  - 共享线性变换 `W ∈ R^{F'×F}` 应用到每个节点特征
  - 注意力函数 `a: R^{F'} × R^{F'} → R` 计算 `e_ij`（节点 j 对 i 的重要度）
  - **掩码注意力**：只对 `j ∈ N_i`（i 的一阶邻居）计算 `e_ij`——把图结构注入注意力
  - SoftMax 在邻域内归一化：`α_ij = softmax_j(e_ij)`
  - 多头（multi-head）K 个独立注意力机制，输出拼接 → 稳定训练
  - 单层注意力函数 = 单层前馈 + LeakyReLU(α=0.2)

- **对 DSG 的适用面（L2-A / L2-B）**：
  - **L2-B**（已有 RustworkX 工作记忆图）：每条边的"激活权重"可以用 GAT 风格的注意力函数
    在线计算，而不必维持一个完整可学习的边权矩阵
  - **掩码注意力**契合"只激活当前帧 / 当前任务相关子图"这种 DSG 局部聚合设计
  - 多头注意力提供"按维度区分注意力源"的能力（例如：空间 vs 视觉 vs 时间）

- **不适用 / 已知陷阱**：
  - 原 GAT 不处理时间维度（→ 需 DySAT）
  - 在大图 / 深层堆叠时仍有过度平滑（over-smoothing）问题
  - 原文用的是端到端可微学习；DSG 在线场景如果不训练，需要手工设定 attention scores
    或用预训练的 W 投影

### 1.2 Sankar et al., 2020 — DySAT

- **引用**：`arXiv:1812.09430` (Sankar, Wu, Gou, Zhang, Yang, WSDM 2020)
- **核心论点**：动态图上的节点表示需要**两个维度的自注意力**——
  结构邻域注意力（同一时刻的邻居） + 时间动态注意力（同一节点的历史快照序列）。

- **机制摘要**：
  - 输入：图快照序列 `{G_1, G_2, ..., G_T}`
  - 第 1 阶段：在每个 `G_t` 上跑结构注意力（GAT 风格）→ 节点的 `t` 时刻嵌入 `h_v^t`
  - 第 2 阶段：在 `{h_v^1, ..., h_v^T}` 序列上跑时间自注意力 → 终态嵌入 `e_v`
  - 比"加时间正则化使快照间嵌入平滑"的早期方法（Zhu 2016 / Li 2017 / Zhou 2018）更强，
    因为后者在节点行为差异大时会失败

- **对 DSG 的适用面**：
  - DSG 节点本身就是**时间演化的**（commit_observation 一帧一帧来），DySAT 的双重注意力
    框架可作为"节点状态在时间序列上如何聚合"的设计参考
  - 时间注意力与"近期帧 > 旧帧"的衰减自然兼容

- **不适用 / 已知陷阱**：
  - DySAT 是离线训练 + 离散快照模型；DSG 是流式增量
  - 它假设节点 ID 在时间快照之间稳定——这正是 DSG L1.5 关联门控要解决的前提
  - 链路预测任务驱动的目标函数与"工作记忆检索"目标不同

### 1.3 Yang et al., 2025 — AGCN: Attention Beyond Neighborhoods

- **引用**：`arXiv:2509.15024` (Yang et al., "Attention Beyond Neighborhoods: Reviving Transformer for Graph Clustering")
- **核心论点**：在**无监督**图聚类场景，GNN 与 Transformer 各自暴露互补的弱点：
  - GNN 过度平滑（over-smoothing） + 过度挤压（over-squashing）：远距离节点被"压扁"
  - Transformer 过度全局化（over-globalization）：远距离高阶邻居淹没了局部模式
  - 实证 1：GCN 在 5 跳邻域内能捕到 50%+ 同类邻居，但跨 10 跳后几乎无同簇邻居 → 全局注意力引入噪声
  - 实证 2：长程依赖确实有用（>4 跳同簇节点存在）但 >10 跳是噪声
  - 实证 3：错聚类的节点 R 比平均高阶距离低 → 失败案例集中在错把局部相似当成同簇

- **机制摘要**：
  - "Graph IS attention"——直接用图结构当 attention bias，而非用 attention 推断结构
  - K-V 缓存技术降低复杂度
  - Pairwise margin contrastive loss 增强 K/V 空间判别力

- **对 DSG 的适用面（重要！）**：
  - **跳数控制**：实证 2 给出"4 跳有用，10 跳是噪声"的硬上界，可作为 DSG 子图遍历深度限制依据
  - **过度全局化防御**：DSG 在做相似检索时不要用全图 cosine sim 一次性比较，应限制在自我中心子图（ego-subgraph）内
  - 案例 §122 总结的"防全局坍塌"范式直接来自这里

- **不适用 / 已知陷阱**：
  - 论文是聚类任务（clustering），不是检索任务（retrieval）；指标维度不同
  - 给出的跳数边界（4 / 10）来自 Cora/Citeseer 学术引文网络，DSG 是物理空间认知图，
    跳数语义需要重新定义

### 1.4 Zhang et al., 2019 — G-HAM (Graph-based Hierarchical Attention Model)

- **引用**：IEEE TNSRE 2019, PMID 31562095, DOI 10.1109/TNSRE.2019.2943362
  ("A Graph-Based Hierarchical Attention Model for Movement Intention Detection from EEG Signals")
- **核心论点**：人头皮上的 EEG 传感器**天然构成图**（节点=电极，边=空间邻接）。
  分层注意力机制可以**同时**锁定时间序列上的判别性周期 + 空间图上的关键节点。
  在 105 受试者的大数据集上做 subject-independent 推理，超越多种 SOTA。

- **机制摘要**：
  - 空间层：图结构 attention 聚合 EEG 节点空间皮层信息
  - 时间层：注意力锁定最具判别性的微观放电周期
  - 分层（hierarchical）：先做时间内的 token 注意力，再做跨节点的空间注意力
  - 跨被试不变模式被显式提取

- **对 DSG 的适用面**：
  - "**多通道传感器 = 图节点**"的建模思想：ParrotCarriers 多模态输入（视觉/语音/AR 锚点）
    可类比为多通道节点
  - 分层注意力（先时间内、再跨节点）可作为 L2-A 多模态融合的层级模板
  - subject-independent 思想 → 用户跨会话不变模式的提取借鉴

- **不适用 / 已知陷阱**：
  - 全监督训练；DSG 是无监督在线
  - EEG 信号有明确的频域特征（α / β / γ 波），DSG 的"信号"是离散的语义事件
  - 模型本身重训练，不能直接搬用；只取**架构层级思想**

---

## 2. 图式理论（Schema Theory）系列

### 2.1 Bartlett, F.C., 1932 — *Remembering*

- **引用**：Bartlett, F.C., *Remembering: A Study in Experimental and Social Psychology*,
  Cambridge University Press, 1932
- **核心论点（Schema 概念的起点）**：记忆不是被动复读，而是受**图式（schema）**影响的**重构**。
  人在回忆时会把缺失/矛盾的细节用先前图式自动填补 → "记忆扭曲"现象。

- **机制摘要**：
  - 图式 = 个体过去经验的有组织表征
  - 召回时不是检索原始数据，而是用图式**重建**
  - 经典实验：英国受试者读印第安民间故事《The War of the Ghosts》后，召回时会无意识地把
    陌生概念替换为本文化中的概念

- **对 DSG 的适用面**：
  - 解释了**为什么不能把 DSG 节点视为"事实快照"**——节点应是经过图式过滤后的"重构产物"
  - 触发 L1.5 / L2-A 设计中的关键问题：检索是返回原始 commit 还是返回 schema 重构态？

- **不适用 / 已知陷阱**：
  - 经典心理学论著，无量化模型；只提供概念基础
  - schema 在 1932 年没有数学化定义；现代实现用 vector / graph 表征

### 2.2 Rumelhart, D.E., 1980 — Schemata: The building blocks of cognition

- **引用**：Rumelhart, D.E., "Schemata: The building blocks of cognition", in
  *Theoretical Issues in Reading Comprehension*, Spiro et al. (eds.), 1980
- **核心论点**：图式具备六大特性：
  1. **变量（variables）**：图式槽位接受不同实体填入
  2. **嵌入性（embedding）**：图式可包含子图式
  3. **抽象层次（levels of abstraction）**：从具体物到抽象概念
  4. **知识表征**：编码"事物如何运作"的过程性知识
  5. **激活式处理**：通过 bottom-up 数据驱动 + top-down 概念驱动并行激活
  6. **不是定义而是典型**：图式描述典型情形，不是必要充分条件

- **对 DSG 的适用面（重要！）**：
  - **变量+槽位** → 在 DSG L2-A 节点中，每类语义节点应有"必填属性 + 可选属性"
  - **嵌入性** → 子图同构（subgraph isomorphism）就是图式嵌入的图论化
  - **bottom-up + top-down 并行** → DSG 检索应同时支持感知驱动（当前帧 → 节点）和
    概念驱动（任务上下文 → 候选节点）

- **不适用 / 已知陷阱**：
  - 经典认知心理学，无可执行算法
  - "典型"一词在 DSG 中需要量化（中心性 / 频率？）

### 2.3 Anderson, R.C., 1977 — Schema-directed processes

- **引用**：Anderson, R.C., "Schema-directed processes in language comprehension",
  in *Cognitive Psychology and Instruction*, 1977
- **核心论点**：理解过程是 schema 引导的**自上而下选择**：
  - schema 决定哪些细节被注意到
  - schema 决定哪些细节被记住
  - schema 决定哪些推理被触发

- **对 DSG 的适用面**：
  - 直接对应"任务上下文 → 主动检索"的模式
  - **注意：schema-directed 解释为什么 DSG 检索不应是被动余弦相似**——
    应让当前任务/查询引导对哪些节点注意

### 2.4 Sickafus, E.N. — *Heuristics for Solving Technical Problems*

- **引用**：案例 §[26]
  http://www.osaka-gu.ac.jp/php/nakagawa/TRIZ/eTRIZ/eSickafusMemorial/...HSTPBook-041111.pdf
- **核心论点**：TRIZ 风格的工程问题求解中，schema 是**技术启发式模板**——
  把当前问题嵌入到已知技术原则的图式中，找出可借用的解决路径。
  与认知心理学的 schema 不同，但提供了**工程化 schema**的范本。

- **对 DSG 的适用面**：
  - 比较弱的相关性；案例引用此文是为了把"schema = 启发式模板"概念落到工程上
  - 仅作侧面背景；优先用 §2.1–§2.3 的认知心理学 schema 概念

---

## 3. 自动 / 受控加工（Automatic vs Controlled Processing）

### 3.1 Schneider & Shiffrin, 1977 — Controlled and automatic human information processing

- **引用**：Schneider, W. & Shiffrin, R.M., *Psychological Review* 84(1), 1977
- **核心论点**：人类信息处理分两类：
  - **受控加工（Controlled）**：串行、慢、费力、容量有限、可灵活调整、依赖工作记忆
  - **自动加工（Automatic）**：并行、快、无意识、容量近无限、固定难改、不占工作记忆
- 切换标志：长期一致映射训练后，某任务从受控 → 自动；新颖映射时则反向

- **对 DSG 的适用面**：
  - DSG **L2-A**（语义抽象，慢推理）↔ 受控加工
  - DSG **L1.5 + L2-B**（快速关联，门控+图遍历）↔ 自动加工
  - 自动加工的"无容量限制"性质提示：L1.5 应是**廉价/总是开**的层；L2-A 才是按需调用

- **不适用 / 已知陷阱**：
  - 1977 年的双系统模型已被批评过于简化；现代认知科学有更细分的分级
  - 不是图论模型；只提供**架构分层动机**

### 3.2 Naito et al., 2009 — Subconscious Motor Program triggered by Moving-Phantom

- **引用**：Naito et al., 2009 (案例 §[27], ResearchGate publication 26262587)
  "Odd Sensation Induced by Moving-Phantom which Triggers Subconscious Motor Program"
- **核心论点**：人在视觉感知到运行中的自动扶梯时，**不可抗拒地**触发针对"乘坐扶梯"的
  隐性运动程序。即使扶梯静止（视觉感知与现实矛盾），运动程序仍然激活，造成奇异感觉。

- **机制摘要**：
  - 视觉刺激 → 长期记忆中"扶梯运动"图式被自动激活
  - 激活路径不经意识审核，直达运动准备区
  - 案例描述为"低阻抗 / 高权重"边——感知节点直连运动节点

- **对 DSG 的适用面**：
  - **快路径（hot path）设计**：DSG 中可设置预编译的"输入感知 → 立即响应"边，绕过 L2-A
  - 案例 §120 的"深度短路旁路（Bypass）机制"范式由此而来
  - 注意：这是 ParrotCarriers 是否需要"反射式响应"的设计抉择，**不要预先采纳**

- **不适用 / 已知陷阱**：
  - 单实验研究，样本不大
  - 在 DSG 中实现"低阻抗预设边"会引入安全风险（认知漏洞，见案例 §67–79 神经编译器讨论）

---

## 4. 临床脑图谱 — 拓扑指标识别异常

### 4.1 ASD（自闭症谱系）sMRI 图分析

- **引用**：案例 §[29]，ABIDE 数据库 + 复杂网络分析（CNA）+ ViT 特征
  ResearchGate publication 393679850 / 311906750（Mathematics of Networks 系列）
- **核心论点**：把每个被试的脑结构 MRI 抽象为加权图（节点=脑区，边=结构连接）。
  ASD 患者 vs 对照组（79 患者 + 105 对照）显示出可分类的拓扑差异。
  机器学习（SVM / Gradient Boosting / Logistic Regression）在该图特征上达高精度自动诊断。

- **对 DSG 的适用面**：
  - 提供"**用图论指标做异常检测**"的方法范本
  - DSG 可借鉴：用 betweenness / clustering coefficient / degree distribution 监控
    自身工作记忆图的健康度（是否过度集中/碎裂/孤立）

- **不适用 / 已知陷阱**：
  - 临床任务 ≠ AI 工作记忆；不要直接套用诊断阈值

### 4.2 MDD（重度抑郁）功能图谱

- **引用**：案例 §[30]，全脑共识网络方法
- **核心论点**：抑郁症患者 vs 健康人的拓扑差异：
  - 健康：**更高节点强度 + 更高聚类系数** → 功能模块化、隔离良好
  - 病患：**模块化破坏** → 默认模式网络（DMN）越界激活，形成自我放大的悲观循环
  - 健康连通分量集中在**中央执行 + 显著性网络**；病患滑入 **DMN 主导**

- **对 DSG 的适用面（重要！）**：
  - 给出"**坏图的拓扑特征**"清单，可作为 DSG 健康度监控的反例
  - DSG 中"工作记忆塌陷为单一无关回路"是真实风险——MDD 模型给出可识别特征
  - "网络隔离破坏 → 自我放大"是反模式信号

- **不适用 / 已知陷阱**：
  - 临床指标的具体阈值不能直接搬

---

## 5. 跨论文的统一观察（DSG 设计抉择层面）

> **本节是对上述论文的归纳，不是新论点**。

| 设计抉择 | 由哪些论文支持 | DSG 层 | 备注 |
|:--|:--|:--|:--|
| 注意力打分应限制在邻域 | §1.1 GAT, §1.3 AGCN | L2-A / L2-B | 严禁全图 cosine 一次比较 |
| 跳数硬上界设计 | §1.3 AGCN（4 跳有用，10 跳噪声） | L2-B 遍历 | DSG 子图扩张需要硬上界 |
| 时间维度独立的注意力 | §1.2 DySAT, §1.4 G-HAM | L2-A | 与空间注意力可分离 |
| 图式槽位 + 嵌入子图式 | §2.2 Rumelhart | L2-A 节点定义 | 节点 schema 需要"必填+可选+子图式" |
| top-down 检索（任务驱动） | §2.3 Anderson | L2-B 检索 | 不能纯余弦相似 |
| 双系统：快路径 + 慢路径 | §3.1 Schneider-Shiffrin | L1.5 vs L2-A | 分层动机 |
| 预编译反射边（可选） | §3.2 Naito | 设计抉择 | 风险高，需另设计 |
| 拓扑健康监控（指标） | §4.1 ASD, §4.2 MDD | DSG 健康度 | 监控 betweenness / clustering / 模块化 |

---

## 5. 记忆架构经典论文（**概念注**，不蒸馏）

> 这一节专门服务 **L2-B Node 组织方式**的设计抉择。每篇仅作概念锚点，未读原文。
> 详情：见 `dsg-l2b-node-organization-options` SKILL §0 索引表。

### 5.1 Tulving, E., 1972 — Episodic vs Semantic Memory

- **引用**：Tulving, E., "Episodic and Semantic Memory", in *Organization of Memory*, 1972
- **核心论点**：人类长时记忆分两类：
  - **Episodic**：关于具体事件的记忆，含时空上下文（"我昨天吃了披萨"）
  - **Semantic**：关于事实和概念的记忆，无时空标记（"披萨是一种食物"）
- **对 DSG 的适用面**：
  - 直接对应 **L2-B Node 类型分类**最经典选项（AriGraph 双类节点的理论依据）
  - L1.5 入口的 CV detection 天然 episodic；L2-A 抽象后产物可视为 semantic
- **不适用 / 注意**：
  - 后续研究（Schacter / Squire）批评二分过简；现代神经科学倾向连续谱
  - 工程上保留二分仍有价值（Node 类型清晰）

### 5.2 McClelland, McNaughton, O'Reilly, 1995 — Complementary Learning Systems (CLS)

- **引用**：McClelland, J.L., McNaughton, B.L., & O'Reilly, R.C., "Why there are complementary learning systems in the hippocampus and neocortex", *Psychological Review* 102(3), 1995
- **核心论点**：大脑用两个互补系统避免"灾难性遗忘 vs 缓慢学习"两难：
  - **海马（快系统）**：快速 episodic 编码，支持立即学习单一经验
  - **新皮层（慢系统）**：缓慢 semantic 整合，跨多次经验提取统计规律
  - 海马在睡眠时**重放（replay）**经验给新皮层，完成知识整合（"systems consolidation"）

- **对 DSG 的适用面**：
  - **架构动机**：L1.5 / L2-A / L2-B 的速度分层有生物学依据
  - **重放机制**：DSG 是否需要后台"重放循环"把 episodic L2-B 节点抽炼为 semantic？设计 chat 决定
  - 与 Schneider-Shiffrin（§3.1）双系统加工是不同层面（CLS 是学习速率分层，S-S 是注意力消耗分层）

- **不适用 / 注意**：
  - "重放"在 AI 里有简化版（experience replay buffer）但与 CLS 原始细节差很多
  - 不可作具体公式；只取架构隐喻

### 5.3 Teyler & Rudy, 2007 — Hippocampal Indexing Theory

- **引用**：Teyler, T.J. & Rudy, J.W., "The hippocampal indexing theory and episodic memory: Updating the index", *Hippocampus* 17(12), 2007
- **核心论点**：海马**不存储**记忆内容，只存储指向新皮层 trace 的**索引**：
  - 经验发生时，新皮层激活分布式神经表征
  - 海马同时编码一个**指针索引**指向那次激活模式
  - 检索时，海马索引被激活 → 触发原皮层 trace → 重现记忆

- **对 DSG 的适用面（重要）**：
  - **直接对应 L2-B = "潜意识索引"角色**——L2-B 节点可以是 pointer 不是 storage
  - 设计选项：节点 `is_pointer` 标记（见 `dsg-l2b-node-organization-options` §4）
  - L2-B 内存图保持瘦身；payload 重的内容委托给 Graphiti / object store

- **不适用 / 注意**：
  - 完整生物学机制涉及"模式分离 / 模式补全"，在 DSG 工程化时只取索引概念
  - 不要以为"指针节点 = 海马 = 完美工程方案"——它带来一致性维护成本

### 5.4 Collins & Loftus, 1975 — Spreading Activation Theory

- **引用**：Collins, A.M. & Loftus, E.F., "A spreading-activation theory of semantic processing", *Psychological Review* 82(6), 1975
- **核心论点**：联想检索 = 节点激活沿边按权重扩散：
  - 概念存于网络节点，关系强度 = 边权
  - 一个概念被想到 → 激活扩散到关联概念，强度随距离衰减
  - "tip-of-the-tongue"现象 = 激活到达但未跨过阈值

- **对 DSG 的适用面**：
  - **检索算法的最古老候选**——比 PPR 更轻量，复杂度低
  - 给 DSG 的"潜意识联想检索"提供最简实现：种子激活 → 衰减扩散 → top-k
  - 与 RustworkX `dijkstra` / `bfs_search` 直接对应

- **不适用 / 注意**：
  - 1975 年模型未量化"激活阈值"具体值；工程化要自己定
  - 与 PPR（HippoRAG）相比，spreading activation 更简单但效果未必差——
    设计 chat 可对比

---

## 6. 不蒸馏 / 不收录的内容

| 跳过 | 理由 |
|:--|:--|
| GAT 的端到端可微训练细节 | DSG 在线场景不训练 |
| DySAT 的链路预测 benchmark | 任务不对齐 |
| AGCN 的 K-V cache 实现 | 太底层，不在 SKILL 范围 |
| G-HAM 的 EEG 信号预处理 | 不是我们输入域 |
| Bartlett 1932 的实验细节 | 概念层引用即可 |
| TRIZ 全部 40 个发明原理 | 仅取 schema 作为启发式概念 |
| ASD/MDD 临床诊断指南 | 我们不做诊断 |

---

## 7. 引用 / 链接索引

- GAT (1710.10903): https://arxiv.org/abs/1710.10903
- DySAT (1812.09430): https://arxiv.org/abs/1812.09430
- AGCN (2509.15024): https://arxiv.org/abs/2509.15024
- G-HAM (PMID 31562095): https://pubmed.ncbi.nlm.nih.gov/31562095/
  DOI: 10.1109/TNSRE.2019.2943362
- Bartlett 1932: Cambridge University Press（古典文献，多版本）
- Rumelhart 1980: in Spiro et al. (eds.), *Theoretical Issues in Reading Comprehension*
- Anderson 1977: in *Cognitive Psychology and Instruction*
- Schneider & Shiffrin 1977: *Psychological Review* 84(1), pp. 1-66
- Naito 2009: https://www.researchgate.net/publication/26262587
- Sickafus TRIZ Heuristics: 案例.md §[26]
- ASD/MDD：案例.md §[29] §[30]
- 案例总文件：`NewZone/RustworkX 图模拟研究案例.md`
