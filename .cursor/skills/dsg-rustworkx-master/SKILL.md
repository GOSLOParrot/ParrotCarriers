---
name: dsg-rustworkx-master
description: >
  RustworkX 使用技巧 + DSG 结合技巧 + 仿生使用技巧 + 跨 skill 决策与论文索引。
  这是 DSG 设计 chat 的"主入口"——回答"该查哪个 skill / 用 RustworkX 哪个 API / 走哪条仿生路径"。
ai_audience: "DSG L1.5 / L2-A / L2-B 设计 chat 的总入口"
last_reviewed: 2026-05-05
related_skills:
  - "dsg-l1-5-l2a-conceptgraph-distilled (A10 入口门控 + L2-A 语义抽象的具体机制)"
  - "dsg-attention-schema-papers (注意力 / 图式 / 自动加工 / 临床脑图谱 / 记忆理论论文索引)"
  - "dsg-l2b-node-organization-options (L2-B Node 组织方式选项清单)"
  - "graphiti (已用 — Graphiti GraphRAG 接入)"
related_distill_outputs:
  - "NewZone/distill_output/dsg/concept-graphs (Gemini 蒸馏，ConceptGraph 仓库)"
  - "NewZone/distill_output/dsg/rustworkx-docs (Gemini 蒸馏，rustworkx.org 官方文档子集)"
  - "NewZone/distill_output/dsg/rustworkx-repo (Gemini 蒸馏，rustworkx 全仓库)"
  - "NewZone/distill_output/dsg/superlocalmemory (Gemini 蒸馏，SLM 仓库)"
  - "NewZone/distill_output/dsg_l2b_org_raw/HippoRAG (Gemini 蒸馏，海马索引 RAG)"
  - "NewZone/distill_output/dsg_l2b_org_raw/AriGraph (Gemini 蒸馏，episodic+semantic 双类节点)"
related_research_doc:
  - "NewZone/RustworkX 图模拟研究案例.md (案例研究综述)"
related_papers:
  - "rustworkx: A High-Performance Graph Library for Python, arXiv:2110.15221"
  - "见 dsg-attention-schema-papers SKILL §1–§4 的完整论文索引"
---

# RustworkX × DSG 综合 Skill — 决策与跨 Skill 索引

> **本 SKILL 是决策 / 索引型**。它**不重复** API 文档（去 rustworkx-docs Gemini 版查），
> **不重复**论文摘要（去 dsg-attention-schema-papers 查），**不重复** ConceptGraph 门控
> （去 dsg-l1-5-l2a-conceptgraph-distilled 查）。
>
> 它做三件事：
> 1. **决策路由**：当前问题该查哪个 skill / Gemini 蒸馏产出
> 2. **使用技巧**：RustworkX SDK 在 DSG 流式实时场景下的实操要点
> 3. **仿生模板**：把案例.md 的 4 个范式落到具体 RustworkX API

---

## 0. 决策路由表（"我现在该查哪个 skill"）

### 0.1 按 DSG 层路由

| 设计问题所在层 | 主查 skill | 配套查 |
|:--|:--|:--|
| **L1.5 入口门控**（detection → admit/reject） | `dsg-l1-5-l2a-conceptgraph-distilled` §1 | 本 SKILL §3.2（仿生 bypass） |
| **L1.5 → L2-A 抽象** | `dsg-l1-5-l2a-conceptgraph-distilled` §4 | `dsg-attention-schema-papers` §2 (Schema Theory) |
| **L2-A 注意力分配** | `dsg-attention-schema-papers` §1 (GAT/DySAT/AGCN) | 本 SKILL §3.3 |
| **L2-B Node 组织方式（类型 / 字段 / 跨源连接）** | `dsg-l2b-node-organization-options` 全文 | `HippoRAG` + `AriGraph` Gemini 蒸馏 |
| **L2-B 工作记忆图操作（API 层）** | `rustworkx-docs` Gemini + 本 SKILL §2 | — |
| **L2-B 检索（联想式 / PPR）** | `dsg-l2b-node-organization-options` §5 | `dsg-attention-schema-papers` §5.4（Spreading Activation） |
| **L2-B 是指针还是存储？** | `dsg-l2b-node-organization-options` §4 | `dsg-attention-schema-papers` §5.3（Hippocampal Indexing） |
| **Graphiti 预加载到 L2-B** | `dsg-l2b-node-organization-options` §3 | `graphiti` skill |
| **节点衰减 / 遗忘** | `superlocalmemory` Gemini §C（TWF 衰减方程） | 本 SKILL §3.4 |
| **跨帧关联 / ReID** | `dsg-l1-5-l2a-conceptgraph-distilled` §3 | — |
| **AR 锚点漂移问题** | `dsg-l1-5-l2a-conceptgraph-distilled` §8a | — |
| **图健康度监控** | `dsg-attention-schema-papers` §4 (ASD/MDD) | 本 SKILL §2.4 |

### 0.2 按 RustworkX 操作问题路由

| 我想做什么 | 去查哪里 |
|:--|:--|
| 学 PyDiGraph 的 API 接口 | `rustworkx-docs` Gemini SKILL §1–§6 |
| 看 vf2_mapping 怎么用 | `rustworkx-repo` Gemini SKILL §5（含 node_matcher 例子） |
| 看 PyO3 / GIL 释放细节 | `rustworkx-repo` Gemini SKILL §B + 本 SKILL §2.2 |
| 看大厂仓库怎么用 RustworkX 做记忆图 | `superlocalmemory` Gemini SKILL（实战） |
| 看图模拟仿生范式总结 | `NewZone/RustworkX 图模拟研究案例.md` §119–§122 |

### 0.3 按问题域路由

| 问题域 | 入口 |
|:--|:--|
| 仿生注意力如何在图上落地 | `dsg-attention-schema-papers` §1 + 本 SKILL §3.3 |
| L2-B Node 类型应该分几类 | `dsg-l2b-node-organization-options` §1 |
| 海马索引 vs 内容存储抉择 | `dsg-l2b-node-organization-options` §4 |
| 联想检索（PPR / Spreading Activation） | `dsg-l2b-node-organization-options` §5 |
| 子图同构 / 经验匹配 | `rustworkx-docs` Gemini §D + 本 SKILL §2.5 |
| 信息流行病学 / 传播模型 | `案例.md` §34–§48 |
| 认知安全 / 旁路攻击 | `案例.md` §67–§79（先了解后再决定是否设计反射边） |

---

## 1. RustworkX 在 DSG 中的核心定位

### 1.1 为什么 DSG L2-B 选 RustworkX 而不是 NetworkX

> 来源：`案例.md` §13–§32 + `rustworkx-docs` Gemini SKILL Key Concepts

| 维度 | NetworkX | RustworkX | DSG 偏好 |
|:--|:--|:--|:--|
| 计算架构 | Python 对象引用 | Rust 连续索引（u32） | RustworkX（4B 节点上限，DSG 长尾累积） |
| 特征向量中心性 | 慢（秒级） | 7.10ms 基准 | RustworkX（实时焦点追踪需要） |
| GIL | 持有 | 在长循环中释放 | RustworkX（多线程友好） |
| 节点 ID 稳定性 | 需自己维护 | StableGraph 内置 | RustworkX（DSG 节点删除不影响其他索引） |
| 社区发现 | 原生支持 | 缺，需自定义或外接 igraph | NetworkX 占优；DSG 需要时可外挂 |
| I/O 格式 | GML/DOT/GraphML/GEXF | Edge List + GraphML 较有限 | DSG 内部不强需广泛 I/O |
| 带符号权重 | 完全支持 | 部分受限 | DSG 抑制性边需自行实现 |

### 1.2 RustworkX 在 DSG 中只承担"骨架"，不承担"血肉"

这是案例.md §9 + §119 的核心范式：

```
┌──────────────────────────────────────┐
│  Topology (RustworkX, Rust 内存)      │
│  - PyDiGraph 节点索引 + 边索引         │
│  - 拓扑遍历 / 中心性 / 子图同构       │
└────┬─────────────────────────────────┘
     │ Python 回调 / payload
┌────▼─────────────────────────────────┐
│  Payloads (Python 对象, 可频繁更新)    │
│  - 节点语义 (clip_ft, schema attrs)  │
│  - 边权重函数（衰减、信任、注意力）    │
│  - 时间戳 / num_detections           │
└──────────────────────────────────────┘
```

**DSG 设计含义**：高频更新的状态（衰减权重、注意力评分、计数器）用 Python 对象挂在节点/边上，
**绝不**重建拓扑；只有真删除/插入节点才动 RustworkX 内部索引。

---

## 2. RustworkX 使用技巧（DSG 实操要点）

### 2.1 节点索引稳定性 — DSG 节点 UUID 怎么落

- `PyDiGraph.add_node(payload)` → 返回 u32 索引；删除节点后**索引不复用**，留 gap
- DSG 推荐：**双 ID 结构**
  - RustworkX 内部 u32 索引 = 短期工作映射
  - DSG 业务 UUID = 持久层标识
  - 维护 `dict[uuid → rwx_idx]` + `dict[rwx_idx → uuid]` 双向表
- 引用：`rustworkx-docs` Gemini SKILL Key Concepts；本 skill 来自 `案例.md` §9

### 2.2 GIL 释放 — 何时能让 DSG 主线程不阻塞

- RustworkX 长循环（Dijkstra / VF2 / centrality）会调用 `py.allow_threads(...)` 释放 GIL
- **意味着**：DSG 后台衰减循环可以与前台检索**真并行**（非伪并发）
- **不意味着**：所有 RustworkX API 都释放 GIL；当算法需要回调 Python `weight_fn`/`heuristic_fn` 时，
  GIL 会重新获取
- 引用：`rustworkx-repo` Gemini SKILL §B PyO3

### 2.3 Bulk API > 单次调用 — DSG 批处理的硬约束

| 用 | 不用 |
|:--|:--|
| `add_nodes_from([...])` | 循环 `add_node` |
| `extend_from_edge_list([...])` | 循环 `add_edge` |
| `extend_from_weighted_edge_list([...])` | 循环带权 `add_edge` |
| `remove_nodes_from([...])` | 循环 `remove_node` |

DSG 含义：每帧的多个 detection 应**累积一帧后批量入图**，不要逐 detection commit。

### 2.4 图健康度监控 — 用中心性指标做异常检测

- `betweenness_centrality(g)` — 桥节点定位（一旦失效图分裂）
- `closeness_centrality(g)` — 节点平均到达成本
- `eigenvector_centrality(g)` — 全局影响力（迭代收敛）
- `pagerank(g)` — 抗噪版本的影响力
- DSG 用法：周期跑这些指标 → 与"健康基线"比对 → 检测**记忆塌陷**（参考 §4.2 MDD 模式）

### 2.5 子图同构 / 经验匹配 — VF2++ 实操要点

- `is_isomorphic(g1, g2, node_matcher=fn, edge_matcher=fn, id_order=False, call_limit=N)`
- **`call_limit` 是关键**：限定状态空间访问数；超限即放弃返回 False
- 仿生隐喻（案例 §109）：相当于 "舌尖现象（Tip-of-the-tongue）" — 资源耗尽后停止搜索
- DSG 含义：子图同构匹配应**永远带 call_limit**（建议初值 1000–10000，按规模调）
- `vf2_mapping(g_pattern, g_data, ...)` 返回所有匹配生成器，可早期 break

### 2.6 在线 vs 离线 API 的边界

| 在线安全（每帧/每次都可调） | 离线推荐（周期性 / 后台跑） |
|:--|:--|
| `add_node`, `add_edge`（O(1)） | `betweenness_centrality`（昂贵） |
| `neighbors`, `successors`（邻接查询） | `eigenvector_centrality`（迭代） |
| `bfs_successors` （限深度） | `pagerank`（迭代） |
| `dijkstra_shortest_path_lengths`（单源） | `all_pairs_dijkstra_path_lengths`（O(V²)） |
| `is_isomorphic` 带严格 `call_limit` | `is_isomorphic` 不带 call_limit |
| `topological_sort`（DAG） | 整图 DBSCAN / community detection |

### 2.7 边权重的两种语义 — DSG 的取舍

- **静态权重**：`add_edge(u, v, 0.7)` — payload 是数值，不会变
- **动态权重函数**：`weight_fn=lambda payload: my_decay_score(payload, time.now())`
  - 算法运行时回调，DSG 衰减可以"懒计算"
  - **代价**：回调进入 Python，丢失 GIL 释放优势
- DSG 抉择：
  - 高频路径（每次检索）→ 静态权重 + 后台异步刷新
  - 低频路径（健康检查）→ 动态权重函数

---

## 3. 仿生使用技巧（4 个范式 × RustworkX 落地）

> 来源：`案例.md` §119–§122 总结的四个范式，每个映射到具体 RustworkX API

### 3.1 范式一：拓扑与状态解耦

**案例 §119 原文**：
> 网络连通性骨架（RustworkX 静态索引）与突触实时脉冲态（顶点/边上轻量动态参数）绝对解耦

**RustworkX 落地**：
- 拓扑（不变）：`add_node` / `add_edge` 调用次数受控（事件驱动），不每帧重建
- 状态（变）：节点 payload 是可变 Python 对象（dict），更新时不动拓扑
  ```python
  # 推荐：状态更新只动 payload，不删边重建
  node_data = g.get_node_data(idx)  # 引用，不复制
  node_data['activation'] *= decay_factor
  node_data['last_seen'] = now()
  ```
- **反模式**：用 `remove_edge + add_edge` 改边权 → 触发索引重排，性能灾难

### 3.2 范式二：深度短路旁路（Bypass）机制

**案例 §120 原文**：
> 优秀图谱中预设具备超低激活阈值与极高信道权重的特异性边，将感知输入直接连到决策输出，
> 在所有路径算法中被赋予最高优先级

**RustworkX 落地**：
- 设计：在 PyDiGraph 中预先 `add_edge(perception_node, action_node, weight=0.0)`（极低成本）
- 检索：`dijkstra_shortest_path_lengths(g, source=perception_node, weight_fn=...)`
  会**自动**优先走旁路（最短路径 = 旁路）
- 但要小心：`案例 §67–§79`（认知安全节）警告：**这种边是攻击面**
  - 如果 attacker 能注入感知输入，触发的动作不经审议
  - **设计抉择**：DSG 是否需要这种边？由设计 chat 决定，不预先采纳

### 3.3 范式三：生物学惩罚与遗忘

**案例 §121 原文**：
> 边权重置于衰变方程下，后台异步时钟周期持续修剪 + 量子化降维，构建自我净化过滤阀门

**RustworkX 落地**：
- 衰变方程实现：见 `superlocalmemory` Gemini SKILL §C（TWF: τ_eff = τ_base / trust_score）
- 后台循环（伪代码）：
  ```python
  # 后台线程；GIL 在重算法时释放
  while True:
      for edge_idx in g.edge_indices():
          edge_data = g.get_edge_data_by_index(edge_idx)
          edge_data['weight'] *= exp(-dt / edge_data['tau_eff'])
          if edge_data['weight'] < THRESHOLD:
              prune_queue.add(edge_idx)
      g.remove_edges_from(list(prune_queue))   # 批量删除
      sleep(BACKGROUND_INTERVAL)
  ```
- 量子化：节点 embedding 存储用 int8 / fp16，方差自然增加（Fisher-Rao 度量）；
  RustworkX 不参与，是 payload 层的事情
- 论文锚点：见 `dsg-attention-schema-papers` §3.1 双系统加工——这是慢通道，
  不该阻塞前台检索

### 3.4 范式四：高界限拓扑管控（防过度全局化）

**案例 §122 原文**：
> 严禁跨全图无限期随机游走或不受限的全局消息传递；用 VF2 + 限流阀值的局部子图同构校验，
> 把注意力聚合约束在有限深度的自我中心子图（Ego-subgraphs）内

**RustworkX 落地**：
- 自我中心子图：
  ```python
  # 取节点 v 的 k 跳子图（不要超过 4 跳，见 §3.5）
  ego = rustworkx.bfs_search(g, [v_idx], visitor=...)  # 限深度 BFS
  ego_subgraph = g.subgraph(list(ego))
  ```
- 同构校验时**必带 call_limit**（§2.5）
- 注意力计算限制在 ego_subgraph 内（不在全 g 上跑）
- **论文锚点**：`dsg-attention-schema-papers` §1.3（AGCN）实证 2：
  - 4 跳内同簇邻居 > 50%（有用）
  - >10 跳几乎无同簇（噪声）
  - DSG 设计建议：跳数硬上界初值取 4

### 3.5 跳数选择小抄（综合 §3.4 + 论文）

| 任务 | 推荐跳数上界 | 引用 |
|:--|:--|:--|
| 当前帧 detection 关联现有节点 | 2–3 跳 | ConceptGraph 默认（empirical） |
| L2-A 注意力聚合 | 3–4 跳 | AGCN 实证 2 (`dsg-attention-schema-papers` §1.3) |
| 长程上下文检索 | 5–8 跳 | AGCN 实证 2，>10 引入噪声 |
| 全图遍历 | 永远不要 | `案例.md` §122 |

---

## 4. 跨 Skill 论文索引（一目录通览）

> 完整摘要见 `dsg-attention-schema-papers/SKILL.md`；本节是**反向**索引（从论文 → 用途）

### 4.1 RustworkX 与图论基础

| 论文 | 用途 |
|:--|:--|
| Treinish et al., 2022 — *rustworkx: A High-Performance Graph Library for Python*, arXiv:2110.15221 | 引擎本身的论文（性能基准 + 设计选择） |
| Δ-Motif, arXiv:2508.21287 | 子图同构并行化（如果未来 RustworkX 不够，可考虑 GPU） |

### 4.2 注意力机制 → DSG 注意力分配

| 论文 | RustworkX 落地点 |
|:--|:--|
| GAT (1710.10903) | 注意力函数挂边 payload，邻域内 softmax |
| DySAT (1812.09430) | 时间维度注意力——节点状态序列加权 |
| AGCN (2509.15024) | 跳数硬上界（→ §3.4） |
| G-HAM (PMID 31562095) | 多通道传感器→图节点的层级注意力 |

### 4.3 图式 / 联想 → DSG 检索方式

| 论文 | RustworkX 落地点 |
|:--|:--|
| Bartlett 1932 | 检索是**重构**而非复读——节点应是 schema 重构态 |
| Rumelhart 1980 | 节点的"必填+可选+子图式"结构定义 |
| Anderson 1977 | top-down 任务驱动检索（不是被动余弦相似） |
| Schneider-Shiffrin 1977 | L1.5 自动 vs L2-A 受控的分层动机 |
| Naito 2009 | 旁路边设计参考（§3.2）——风险高，慎用 |

### 4.4 临床脑图谱 → DSG 健康度监控

| 论文 | RustworkX 落地点 |
|:--|:--|
| ASD sMRI 网络分析 | 用 betweenness/clustering 指标做异常分类（§2.4） |
| MDD 全脑共识网络 | 模块化破坏作为"记忆塌陷"反模式信号 |

### 4.5 SuperLocalMemory（实战参考）

| SLM 组件 | DSG 借鉴点 |
|:--|:--|
| 9 层架构（L4 知识图谱） | DSG L1.5 / L2-A / L2-B 层次划分参考（不照抄） |
| TWF 信任加权遗忘 | 衰变方程的工程实现（注意 SLM 用 Leiden 聚类，需 igraph，**不是纯 RustworkX**） |
| 6 通道 RRF 检索 | 多通道融合是 DSG 检索的可参考范式 |
| MCP daemon `127.0.0.1:8767` | 总线集成参考 |
| `--json` envelope | agent-native 输出格式参考 |
| LoCoMo 74.8% 局部分数 | 现实世界基准——衡量 DSG 应达水平 |

> **重要校正**：案例.md §54 写"SLM 通过底层 RustworkX 构建 9 层"——实际从仓库可见，
> SLM 在 L4 用 RustworkX，但其他层（聚类）依赖 `python-igraph` + `leidenalg`。
> 不要被案例文字过度引导，蒸馏的 `superlocalmemory` Gemini 版是真实参考。

---

## 5. 关键决策抉择（**已识别但不预先回答**）

> 这些是 DSG 设计 chat 必须回答的问题。本 SKILL 只**列出**它们，**不给答案**。

### 5.1 节点 ID 策略
- DSG 节点 UUID 用什么生成？时间戳 / hash / 自增？
- RustworkX 内部 u32 索引何时持久化（重启恢复）？

### 5.2 衰减节奏
- 衰减循环间隔多少？（SLM 没明示；论文都没给硬数字）
- 衰减是均匀全图还是分层（高活跃区域慢扫，冷区域快扫）？

### 5.3 跳数硬上界
- AGCN 给的 4 跳是 Cora 学术网络的；DSG 物理空间认知图的合适上界？
- 不同任务（实时关联 vs 检索）是否需要不同上界？

### 5.4 旁路边
- DSG 是否预编译"感知 → 动作"反射边？（§3.2）
- 若是，怎么防认知漏洞攻击？（案例 §67–§79）

### 5.5 多通道融合
- 借 SLM 6 通道 RRF 还是自研？
- ParrotCarriers 的"通道"如何定义（视觉 / 语音 / AR 锚点）？

### 5.6 健康度监控阈值
- 用 ASD/MDD 范本（betweenness 分布 / 聚类系数 / 模块化）监控 DSG 健康
- 但临床阈值不能搬——DSG 的"健康基线"如何建立？

### 5.7 与 ConceptGraph 的差异交付
- DSG 不照搬 ConceptGraph 的 obj_min_detections=3 阈值（参 `dsg-l1-5-l2a-conceptgraph-distilled` §0.5.1）
- DSG 流式实时场景的 sim_threshold 该取多少？

---

## 6. 用法速记（"如何使用本 SKILL"）

1. **打开本 SKILL** → 看 §0 决策路由表 → 跳到对应 sibling skill 或 Gemini 蒸馏产出
2. **看 RustworkX 实操技巧** → §2
3. **看仿生范式落地** → §3（跳数 / 衰减 / 旁路 / 解耦）
4. **看论文索引** → §4（反向索引：从论文找 RustworkX 用法）
5. **遇到设计抉择** → §5 列了 7 个未答问题；不要在本 SKILL 里直接给答案

> **本 SKILL 不放代码示例**——代码示例在：
> - 通用 API：`rustworkx-docs` Gemini SKILL
> - 实战：`rustworkx-repo` Gemini SKILL §"Practical Code Examples"
> - 业务实战：`superlocalmemory` Gemini SKILL "Quick Reference"

---

## 7. 不蒸馏的内容

| 跳过 | 在哪里 |
|:--|:--|
| RustworkX 完整 API 参考 | `rustworkx-docs` Gemini SKILL |
| RustworkX 测试代码 / How-To Guides | `rustworkx-repo` Gemini SKILL references |
| ConceptGraph 门控阈值表 | `dsg-l1-5-l2a-conceptgraph-distilled` §1.2 / §5 |
| GAT / DySAT 论文摘要 | `dsg-attention-schema-papers` §1 |
| Schema Theory 摘要 | `dsg-attention-schema-papers` §2 |
| SLM 实操命令 | `superlocalmemory` Gemini SKILL "Quick Reference" |
| 案例.md 全文叙事 | `NewZone/RustworkX 图模拟研究案例.md` |
