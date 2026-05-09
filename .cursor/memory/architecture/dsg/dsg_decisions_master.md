---
status: ratified
category: workspace-snapshot
status_note: "DSG 独立工作区的决策总表（master）。长期累加，不带日期；后续可分类。本表覆盖范围超过 L2-B（含 L1.5 池 / Lifecycle / Obsidian 三分类 / 工作记忆归档时机 / 仿生路径 / 防爆炸门控等），是 DSG 系列设计 chat 的 SSOT。每条决策标注 status：ratified / provisional / deferred-to-design / superseded。"
last_reviewed: 2026-05-06
ai_priority: high
ai_audience: "DSG 系列设计 chat 入场必读 — 已决事项不要重新讨论；provisional 条目在 L2-B 组织方式设计 sign off 后回头审计"
parent_doc: "workspace_index.md"
related:
  - "../adr_l1_5_source_dispatch_extension_space_20260504.md"
  - "../sprint4_phase4_completion_and_final_audit_20260430.md"
  - "../sprint4_phase4_entry_20260430.md"
  - "../module_map_p2.md"
  - "../lineb_implementation_completion_20260504.md"
  - "../../parrot_behavior_rules.md"
  - "../../../skills/dsg-rustworkx-master/SKILL.md"
  - "../../../skills/dsg-l2b-node-organization-options/SKILL.md"
  - "../../../skills/dsg-attention-schema-papers/SKILL.md"
  - "../../../skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md"
---

# DSG 决策总表（master）

> **本文是什么**：DSG 独立工作区的"决策总表"。把用户在 [open_questions_for_design_chat.md](open_questions_for_design_chat.md) 上回答的事项 + 后续追加的元约束统一固化在此。**Chat 2 入场不再重读 Q&A 原文，直接以本表为入场 SSOT**。
>
> **本文不做**：不做新设计、不投票、不裁决 deferred-to-design 条目、不修改既有 ADR 决策。
>
> **状态体系**（每条决策的 `status` 字段）：
>
> | status | 含义 |
> |:--|:--|
> | `ratified` | 用户最终决策，不再讨论 |
> | `provisional-revisit-after-L2-design` | **临时决策**；L2-B 组织方式设计 sign off 后**必须**回头审计是否有更好解法（用户 2026-05-06 原话："对之前的某些理解可能需要进行新技能重新决策，如果觉得审计为时尚早的话，我更推荐在我们完成设计 L2 组织方式和架构适配时，一起完善来完成"） |
> | `deferred-to-design` | 留给 Chat 2 设计稿回答 |
> | `deferred-to-P3` | 推到 P3 / A10 独立设计 chat |
> | `superseded` | 被新决策替代，仅作历史 |
> | `tbd` | 用户暂未决（仍开放）|

---

## §0 元约束（贯穿所有决策）

| # | 元约束 | status |
|:--|:--|:--|
| M1 | **桌面场景优先**：所有具体配置 / 阈值先按桌面场景定，不过度工程；其他场景具体场景具体设计 | ratified |
| M2 | **不过度消耗注意力**：不在不必要细节上反复推敲；当 4 个新 DSG skill 已给出选项时，优先用选项库，不重新发明 | ratified |
| M3 | **仿生路径混合不单选**：`字段层（子类 Node 特殊字段）` 和 `RustworkX 机制层（Cluster / 子图 / 折叠 / 跃迁通道 / Spreading Activation / PPR）` **两条路径都开放**；按 [`dsg-rustworkx-master §1.2`](../../../skills/dsg-rustworkx-master/SKILL.md) 骨架 vs 血肉范式：拓扑走 RustworkX，高频状态挂 payload | ratified |
| M4 | **L1.5 ↔ L2 调研后审窗口**：本表里所有 `provisional-revisit-after-L2-design` 条目，在 Chat 2（L2-B 组织方式设计）sign off 后**必须**做一次回审；若 4 新 skill 给出比当前 L1.5 决策更好的解法，按新决策 supersede 旧条目 | ratified |
| M5 | **不动 Phase 4 §8 决策锁 / ADR-L1.5-001 §4.1 升级条件**；本表条目均不触动 wire 协议（仅 Python 内部） | ratified |

---

## §1 L1.5 池定位升级

### 1.1 池 = 多源 Node 出口管理层

| 维度 | 决策 | status |
|:--|:--|:--|
| **L1.5 角色** | 从"纯 Pydantic 合同层"升级为"多源 Node 出口管理池" | provisional-revisit-after-L2-design |
| **物理形态** | 给 L2-B 加一层薄管理层（不是独立进程 / Redis）；具体是新 `L1_5Pool` 类还是合并进 `L2BGraph` 由 Chat 2 决定 | deferred-to-design |
| **所有权** | DSG 模块单例（per-process），不是 per-session / per-Episode | ratified |
| **目的** | 内存管理 + Ref 查找 + 一键增删外部源节点（Google 日程 / Obsidian 设定） | ratified |
| **与 L2-B 的关系** | 池是 L2-B 的方便管理层；source-of-truth 由外部源控制（AR 锚点 / A10 最后位置）；具体合并冲突规则由 Chat 2 设计 | provisional-revisit-after-L2-design |

> **后审触发**：调研 [`dsg-l2b-node-organization-options §6.5`](../../../skills/dsg-l2b-node-organization-options/SKILL.md)（P1 多 Profile / P2 时间分层 / P3 类型分层 / P4 多正交视图）后，"池要不要独立类"可能有更优答案。

### 1.2 防爆炸门控分层（A10 / L1.5 / L2-B 各一道）

| 门控层 | 当前规则 | status |
|:--|:--|:--|
| **A10 端 CV Flow 自合并** | 由 [`dsg-l1-5-l2a-conceptgraph-distilled §1.2-1.4`](../../../skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md) IoU + CLIP sim + persistence threshold + obj_min_detections=3 控制 | ratified（A10 侧）|
| **L1.5 入池** | 置信度门控 + 加权投票 + "注意力足够"+"与当前事件相关才入 L2"；具体阈值由 Chat 2 + [`dsg-rustworkx-master §3.5`](../../../skills/dsg-rustworkx-master/SKILL.md) 跳数硬上界 (4 跳) + [`dsg-attention-schema-papers §1.3`](../../../skills/dsg-attention-schema-papers/SKILL.md) AGCN 实证 综合定 | provisional-revisit-after-L2-design |
| **L2-B 入图** | UUID 对齐已记忆物体 + 不可能事件（如电视瞬移）报错不进 L1.5 标不可信 + 大类背景 Node 合并（杯子 vs 星巴克星冰乐）；同类第二实例需用户确认 | deferred-to-P3（具体规则）/ ratified（原则）|
| **新物体进 L2-B 门** | 看着一样位置冲突 / 不可能事件 → 报错；GOSLO 提示用户确认是同类第二实例后才进 | deferred-to-P3 |

> **关键不变量**（[`ingest/base.py docstring`](../../../../src/parrot/dsg/ingest/base.py)）：Ingest 层是**唯一**让外部观察变成 L2-B SemanticNode 的关卡，preload 例外。

### 1.3 入池条件

| 维度 | 决策 | status |
|:--|:--|:--|
| **触发事件** | 触发器 / 场景切换 / Obsidian 设定节点 / Graphiti preload / GOSLO 主动好奇 / 一键导入 Google 日程；具体清单由 Chat 2 列全 | provisional-revisit-after-L2-design |
| **`confirmation` 默认值矩阵** | 按 source 不同（详见 §4 source × lifecycle 表）；当前所有 source 走同一 IngestRunner 路径 | provisional-revisit-after-L2-design |
| **幂等键** | label / uuid / spatial bbox 三选；具体优先级由 Chat 2 决定 | deferred-to-design |

### 1.4 出池条件

| 维度 | 决策 | status |
|:--|:--|:--|
| **TTL** | 桌面具体场景具体设计；池只记录"当前状态"不记录整个时间轴；时间轴由观察者 + Episode + 对话快照负责 | ratified（原则）|
| **池上限** | 桌面 2C8G 性能够；不主动设硬上限；具体淘汰策略 Chat 2 调研后定 | provisional-revisit-after-L2-design |
| **淘汰算法 priority 链** | **特殊节点状态 > 父类节点状态 > 时间** — 优先淘汰对话无关 / 已 GHOST / 当前未用的节点；时间最 last | ratified |
| **主动出池**（episode close）| 移除池后留档不丢（观察者快照已独立到内存 → 硬盘）；具体哪些节点出池由 Chat 2 决定 | provisional-revisit-after-L2-design |

### 1.5 状态分桶（桌面起步）

| 桶 | 内容 | status |
|:--|:--|:--|
| **主桶** | 通用工作记忆节点（OBJECT / PERSON / SURFACE / EVENT / PHOTO 等）；联想机制 + 触发器作用层 | ratified |
| **Obsidian 设定桶** | Obsidian-设定-日常 + Obsidian-设定-Roleplay（详见 §3.2）；与主桶通过 Cluster 边连接 | ratified |
| **Google 日程一键导入桶** | 当用户想被提醒时导入；可一键从 RustworkX 删除 | ratified |

> 桌面**先 1 主桶 + 2 特殊桶**起步；多 Profile 形态 / 子图分层选项（[`dsg-l2b-node-organization-options §6.5`](../../../skills/dsg-l2b-node-organization-options/SKILL.md) P1-P4）由 Chat 2 调研后裁决。

---

## §2 L2-B 组织方式（与 L1.5 的边界）

### 2.1 单图 vs 多图

| 维度 | 决策 | status |
|:--|:--|:--|
| **桌面起步** | 单 `PyDiGraph`；不分图 | ratified |
| **后期**（仿生升级时）| Cluster / 子图 / 折叠 / 跨子图跃迁通道；具体 P1-P4 选项由 Chat 2 调研裁决 | deferred-to-design |
| **主图原则** | 除特殊 Node 种类（Obsidian 设定 / Google 日程）最好不要分；可开冗余子图 | ratified |
| **NodeKind 拆图** | **不**按 NodeKind（PERSON / OBJECT / EVENT / PHOTO）拆主图 | ratified |
| **Episode 拆图** | **不**按 episode 拆 | ratified |
| **跨子图边语义** | RustworkX 提供 Cluster 折叠 + 跨子图 / Cluster 跃迁通道；详见 [`dsg-rustworkx-master §3`](../../../skills/dsg-rustworkx-master/SKILL.md) | ratified（机制可行性）|

### 2.2 索引 / 查询

| 维度 | 决策 | status |
|:--|:--|:--|
| **label 反向索引** | 按需 — 不过度优化 | deferred-to-design |
| **注意力查询性能** | 桌面节点数 << 100，不必担心；具体阈值由 Chat 2 测后定 | provisional-revisit-after-L2-design |
| **"按 source 查询"路径** | 当前 runner 线性扫描；如有需要 Chat 2 加索引 | deferred-to-design |

---

## §3 Source × Lifecycle 调整

### 3.1 SOURCE_PRIORITY 切换开关

| 维度 | 决策 | status |
|:--|:--|:--|
| **数值表** | 当前 [`runner._SOURCE_PRIORITY`](../../../../src/parrot/dsg/ingest/runner.py) 7 项不动 | ratified |
| **切换开关** | **留切换开关** — 受场景切换 / 触发器 / GOSLO 状态影响（如 roleplay 模式时调权重）；具体开关形态 Chat 2 决定 | ratified（设计原则）/ deferred-to-design（具体形态）|

### 3.2 Obsidian 三分类（**重要修正**）

> 上轮文档 [source_x_lifecycle_status.md §2.1](source_x_lifecycle_status.md) 把 USER_TAG_OBSIDIAN 当一类处理；现在拆 3 子类。

| 子类 | 用途 | UUID 绑定 | 永久权威 | 是否进 L1.5 池 | 是否进 L2-B 节点 | 桶 | Graphiti 分区 |
|:--|:--|:--|:--|:--|:--|:--|:--|
| **Obsidian-Ref-加强** | 加强既有节点的 Ref（不是节点本身）| 是 | — | ❌ 不进 | 作为其他节点的 `meta.obsidian_uuid` 引用 | — | 生活区 |
| **Obsidian-设定-日常** | 介绍家里沙发 / 大家具 / 公用场景；可作其他节点引用 | 是（节点）| 是 | ✅ 进 | ✅ 是节点本身（NodeKind=OBJECT/SURFACE/PERSON 等）| Obsidian 设定桶 | 生活区 |
| **Obsidian-设定-Roleplay** | Roleplay 模式自定义；人工维护；不日常使用；可把家设成中世纪 / 物品设成 XXX | 是 | 是 | ✅ 进（roleplay 模式时）| ✅ 是节点本身（roleplay 专属或通用 NodeKind 由 Chat 2 决定）| Roleplay 临时桶 | **roleplay 自定义区**（不污染生活区） |

| 维度 | 决策 | status |
|:--|:--|:--|
| **三分类必要性** | ratified — 不能合并为一类 |  |
| **L2-B 节点是否要新增 enum 值** | 设定节点在现有 NodeKind 内（OBJECT / SURFACE / PERSON 等）；roleplay 是否新增 NodeKind 由 Chat 2 决定 | provisional-revisit-after-L2-design |
| **`source_meta` 字段** | Obsidian 节点装 `{obsidian_path, file_mtime, double_link_count, profile: "daily"\|"roleplay"}` 等 | ratified（字段集合） |
| **Push-style 增量同步** | 设计 chat 决定是否绕过 Graphiti 中转直通 L2-B；当前依靠 preload + Graphiti 中转 | deferred-to-design |
| **永久权威标记** | Obsidian-设定-日常 + Obsidian-设定-Roleplay 永远不可被低 authority 覆盖 / 永不衰减 / 永不 GHOST | ratified |
| **一键删除 / 切换 Roleplay 模式** | RustworkX 一键 `remove_nodes_from(roleplay_subgraph)` 即可；具体接口 Chat 2 给 | deferred-to-design |

### 3.3 GOSLO 主动发现来源

| 维度 | 决策 | status |
|:--|:--|:--|
| **enum 处理** | **未决** — 是新增 ObservationSource enum（如 `GOSLO_AUTONOMOUS`）/ 用 `source_meta.triggered_by` / 独立 filter 三选一由 Chat 2 决定 | tbd |
| **优先级** | 主动发现节点 priority **<** 被用户问出来的节点（同走 IDENTIFY_OBJECT 但触发方不同）| ratified |
| **TTL** | 短 TTL（避免 GOSLO 好奇刷屏）；具体时长 Chat 2 定 | ratified（必要性）/ deferred-to-design（数值）|
| **是否参与 L2-B + 观察者 + 时间轴 + L3** | ✅ 是 — 主动发现节点参与全链路 | ratified |
| **是否阻塞对话** | tbd — "GOSLO 用了这个工具就会说话吗？再看吧" | tbd |

### 3.4 IDENTIFY_OBJECT / GEMINI_ORAL / USER_EXPLICIT / MOCK

| Source | 决策 | status |
|:--|:--|:--|
| **IDENTIFY_OBJECT — 命中节点降级** | `lastSeen` 永久保留；其他状态字段不必那么多；具体 TTL 由具体场景具体设计 | ratified（lastSeen 永久）/ deferred-to-design（其他降级规则）|
| **GEMINI_ORAL — "泛泛之谈" vs "当前场景实体"** | ✅ 需要区分；具体区分规则由 Chat 2 + [`dsg-l2b-node-organization-options §3.2`](../../../skills/dsg-l2b-node-organization-options/SKILL.md) 跨源合并信号定 | ratified（必要性）/ deferred-to-design（规则）|
| **USER_EXPLICIT 拆 USER_VERBAL / USER_UI** | ✅ 拆 — Chat 2 实施 | ratified（必要性）/ deferred-to-design（实施）|
| **MOCK** | 测试桩，不参与 lifecycle 设计 | ratified |

### 3.5 跨 source 状态机

| 维度 | 决策 | status |
|:--|:--|:--|
| **桌面起步** | 所有 source 共享统一状态机（EXPECTED → ACTIVE → PERIPHERAL → GHOST 或类似）| ratified |
| **未来分轴** | 是按 NodeKind 拆 vs 按 source 拆 vs 双轴正交（[`dsg-l2b-node-organization-options §1.4`](../../../skills/dsg-l2b-node-organization-options/SKILL.md) 选项 D）— 留 Chat 2 决定 | provisional-revisit-after-L2-design |
| **GHOST 转换** | 单 source 单维 evidence_score 阈值 vs 多因素综合（[Opus 19 §2.3](../../../../docs/InfoCollections/Opus/19_anomaly_ghost_expectation_vision.md)）— 测试期先**不衰减**，后期好加 | ratified（先不衰减）|
| **novelty 衰减** | 测试期不启用 | ratified（短期）/ deferred-to-design（长期参数）|
| **habituation 累加** | 测试期不启用 | ratified（短期）/ deferred-to-design（长期参数）|

### 3.6 状态变更 observability

| 维度 | 决策 | status |
|:--|:--|:--|
| **状态转换发 EcpEvent 通知 Unity** | ✅ 发 — 为测试覆盖率（Phase 4 wire 不动；新 EcpEventType 走新 ADR）| ratified |
| **写 obs_log** | ✅ 写 — 用既有 [`log_obs_event`](../../../../src/parrot/brain/obs_log.py) | ratified |
| **触发 trigger** | ✅ 触发（如 `ATTENTION_DECAY` → Brain 知道节点不再活跃）| ratified |

> 三条都开是为了**测试覆盖率**；产线开关由 Chat 2 决定。

---

## §4 注意力实现路径（**双开放**）

> **本节修正**：上轮 [opus_dsg_residual_intent.md](opus_dsg_residual_intent.md) §3.2 把"走 RustworkX 机制实现"写成单选；用户 2026-05-06 原话明确"注意力可以是子类 Node 的特殊字段也可以是 RustworkX 机制层"。

| 路径 | 适用场景 | 落地范式 | status |
|:--|:--|:--|:--|
| **字段层**（子类 Node 特殊字段）| 高频读写状态（衰减权重 / 计数器 / track_id 等）| `SemanticNode.attention/novelty/habituation_count` 字段已存在；扩展走 `source_meta` factory | open（不锁单选）|
| **RustworkX 机制层**（Cluster / 子图 / 折叠 / 跃迁通道 / Spreading Activation / PPR）| 拓扑遍历 / 中心性 / 子图同构；潜意识联想；分桶 | 见 [`dsg-rustworkx-master §3`](../../../skills/dsg-rustworkx-master/SKILL.md) 4 范式 + [`dsg-attention-schema-papers §5.4`](../../../skills/dsg-attention-schema-papers/SKILL.md) Spreading Activation | open（不锁单选）|

**实际很可能是混合**（[`dsg-rustworkx-master §1.2`](../../../skills/dsg-rustworkx-master/SKILL.md) "骨架 vs 血肉"范式）：

```
RustworkX 拓扑（Rust 内存）= 骨架，不每帧重建
Node payload（Python 对象）= 血肉，频繁更新 attention/衰减
```

| 维度 | 决策 | status |
|:--|:--|:--|
| **路径选择** | 双开放 — 不预先选单一路径 | ratified |
| **混合配比** | 由 Chat 2 调研 4 新 skill 后裁决；建议参考 §1.2 骨架 vs 血肉范式 | deferred-to-design |
| **触发条件**（升级到子类 Node）| 仍按 [ADR-L1.5-001 §4.1](../adr_l1_5_source_dispatch_extension_space_20260504.md) 三条触发器；当前**未触发**| ratified |
| **L2-B 注意力字段衰减是否启用** | 测试期不启用（与 §3.5 一致）；后期由 Chat 2 决定走字段衰减 vs 机制层衰减 | ratified（短期）/ deferred-to-design（长期）|

---

## §5 工作记忆延迟归档（**新约束**）

> **2026-05-06 用户原话**："工作记忆不会在当场的对话中就通过 Graphiti 存档到 nanobot，快照和 Episode 等会而是先存起来到内存或者硬盘，等对话结束后 且 nanobot 闲时 / 夜间空闲时 才启动存档流程，把一整次次对话和 Ref 信息和数据标注和记录下来的时间轴和数据给 统一经过过滤器 + LLM 存起来到 graphiti。"

### 5.1 三阶段归档流程

```
对话期间:
  L2-B + 内存快照 + Ref 表 + 时间轴标注（运行时；不写 Graphiti）
       ↓
对话结束:
  序列化到硬盘（建议路径 data/conversations/{conv_id}/{snapshot,refs,timeline}.{json,jsonl}）
       ↓
nanobot 闲时 / 夜间空闲时:
  统一经过过滤器（含 MemoryValidity 过滤器，[`module_map_p2 §11.2`](../module_map_p2.md)）
       + LLM
       → 写 Graphiti
```

### 5.2 与现有代码的冲突点（实施前必查）

| 现有代码 | 冲突点 | 处理 |
|:--|:--|:--|
| [`l2b_graph.py:start_episode()`](../../../../src/parrot/dsg/l2b_graph.py) 异步立即 archive 上一个 episode (`loop.create_task(self.archive_episode_to_graphiti(...))`) | 当场写 Graphiti — 与新约束冲突 | Chat 2 实施时**改为**：序列化到硬盘 + 入 nanobot 闲时队列；不直接 archive |
| [`runner.py:commit_observation`](../../../../src/parrot/dsg/ingest/runner.py) 内 `TODO(S4.B): write-back to Graphiti here for CONFIRMED nodes` | TODO 描述错误方向 | Chat 2 改 TODO 描述："**禁止当场写回**；走 §5.1 三阶段流程" |
| `MemoryValidity 过滤器` ([`module_map_p2 §11.2`](../module_map_p2.md)) | PLANNED P3；位于 L2 Graphiti 写入之前 | 与本节 §5.1 是同一管线的两个角度；Chat 2 + P3 chat 协调推进 |

### 5.3 决策表

| 维度 | 决策 | status |
|:--|:--|:--|
| **归档时机** | ✅ 三阶段（对话期间不写 / 对话结束序列化 / nanobot 闲时统一过滤 + LLM）| ratified |
| **序列化格式** | JSON / JSONL（建议）；具体 schema 由 Chat 2 给 | deferred-to-design |
| **硬盘路径约定** | `data/conversations/{conv_id}/...`（建议）| deferred-to-design |
| **nanobot 闲时检测信号** | 待 Chat 2 + nanobot skill 协同设计 | tbd |
| **MemoryValidity 过滤器衔接** | 在归档管线"过滤器 + LLM"段引用既有 P3 设计 | deferred-to-P3（具体规则）/ ratified（位置）|

---

## §6 P3 / A10 独立设计 chat 边界（**defer 清单**）

以下 deferred-to-P3 — Chat 2 不展开，仅在设计稿里**预留位置 + 显式标 P3**：

| 项 | 来源 |
|:--|:--|
| A10 接入时 `register_source_meta_factory("cv_a10", ...)` 装哪些字段 | Q2.4 / [`dsg-l1-5-l2a-conceptgraph-distilled §3.4`](../../../skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md) |
| A10 节点自动 confidence decay（外观漂移问题）| ConceptGraph SKILL §8a Q8 |
| A10 与现有 IDENTIFY_OBJECT 节点合并策略（reid_hash 跨 source ReID）| Q2.4 |
| A10 适配 AR 坐标 + 手机传感器数据 + SAM2/DINOv2 + 软件建图 + VPS | Q2.4 |
| **不可能事件**（电视瞬移）报错不进 L1.5 标不可信 | §1.2 |
| 同类第二实例需用户确认才进 L2-B | §1.2 |
| MemoryValidity 过滤器具体 Ebbinghaus 衰减公式 + 置信度阈值 | [`module_map_p2 §11.2`](../module_map_p2.md) |

---

## §7 已 resolved + 仍 TBD 的 Open Questions

### 7.1 已 resolved（2026-05-06 这一轮）

| # | 问题 | 解 |
|:--|:--|:--|
| **D1** | LineB vs DSG 派发顺序 | LineB 已完成（[`lineb_implementation_completion_20260504.md`](../lineb_implementation_completion_20260504.md)），DSG 直接进 |
| **D2** | graphiti 前的有效期预测模块 | `MemoryValidity 过滤器`（[`module_map_p2 §11.2`](../module_map_p2.md)）；P3 实施；临时方案 conversation_writer / identify_object 内 `importance < 0.3` 硬规则 |
| **D3** | RustworkX 调研 | Migration package 已搬迁；4 新 skill + 6 蒸馏入库；本表 §4 / §1.2 / §2.1 已纳入 |

### 7.2 仍 TBD

| # | 问题 | 处理位置 |
|:--|:--|:--|
| **D4** | GOSLO 主动发现是否阻塞对话 | §3.3；用户原话"再看吧" |
| **D6** | Q3.5 后两小问（PHOTO 短瞬节点 close 时归档？多 Episode 嵌套？）| open_questions §3.5 留白 |
| **D7** | Q4.1-Q4.5 锁面交互核对（ADR-L1.5-001 §4.1 触发 / Phase 4 §8 / cs_parity / Observer-Attention 边界 / 测试基线）| Chat 2 设计稿 sign off **前必填** |
| **D8** | 工作记忆延迟归档与 nanobot 闲时 / MemoryValidity / conversation_writer 的衔接 | §5；Chat 2 + P3 chat 协调 |
| **D9** | 注意力路径字段层 vs RustworkX 机制层混合的具体配比 | §4；Chat 2 调研 4 新 skill 后裁决 |

---

## §8 后续审计触发条件

| 条件 | 动作 |
|:--|:--|
| **Chat 2（L2-B 组织方式 + L1.5 池架构适配）sign off** | 回审本表所有 `provisional-revisit-after-L2-design` 条目；如果 4 新 skill 给出更好解法，新决策 supersede 旧条目（注 `superseded` 状态 + 链接到新决策位置）|
| Chat 2 触发 [ADR-L1.5-001 §4.1](../adr_l1_5_source_dispatch_extension_space_20260504.md) 三条升级条件之一 | 起新 ADR `supersedes: [ADR-L1.5-001]`；同步更新本表 |
| Phase 5+ A10 接入设计 chat 启动 | 回审 §6 defer 清单；逐项进入实施 |
| 真机 spike 验收 #1/#2 ✅ | DSG 模块 Sprint 4 → Sprint 5 转换前回审本表，把 ratified-short-term 项升 ratified |

---

## §9 引用源

### 9.1 ADR & 决策锁

- [ADR-L1.5-001](../adr_l1_5_source_dispatch_extension_space_20260504.md) — Q1/Q2/Q3 + §4.1 升级条件
- [ADR-PROTOCOL-INTERFACE-001](../adr_protocol_upgrade_and_interface_refinement_background_20260504.md)
- [Phase 4 §8 13 决策锁](../sprint4_phase4_entry_20260430.md)
- [Phase 4 完成报告](../sprint4_phase4_completion_and_final_audit_20260430.md)
- [LineB 完成报告](../lineb_implementation_completion_20260504.md) — Sprint 4 Phase 5+ 双管线

### 9.2 DSG cursor skills（4 个新蒸馏 + 2 个相关）

- [dsg-rustworkx-master](../../../skills/dsg-rustworkx-master/SKILL.md) — 总入口路由 + RustworkX 实操 + 仿生 4 范式
- [dsg-l2b-node-organization-options](../../../skills/dsg-l2b-node-organization-options/SKILL.md) — Node/Edge 组织 5 选项 + 子图分层 P1-P4
- [dsg-attention-schema-papers](../../../skills/dsg-attention-schema-papers/SKILL.md) — 13 篇论文索引（GAT/DySAT/AGCN/G-HAM/Schema/Hippocampal Indexing/Spreading Activation 等）
- [dsg-l1-5-l2a-conceptgraph-distilled](../../../skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md) — A10 入口门控 + L2-A 语义抽象
- [graphiti](../../../skills/graphiti/SKILL.md) — Graphiti 客户端
- [py-trees](../../../skills/py-trees/SKILL.md) — 行为树（Scheduler 用）

### 9.3 ~~蒸馏素材池~~ → 已入 dsg-* skill（2026-05-09 物理删除）

> 原 NewZone/ 蒸馏素材池已**全部冗余删除**；蒸馏精华已入 4 个 dsg-* skill。

- ConceptGraph 仓库 → [`.cursor/skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md`](../../../skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md)
- rustworkx-docs / rustworkx-repo → [`.cursor/skills/dsg-rustworkx-master/SKILL.md`](../../../skills/dsg-rustworkx-master/SKILL.md)
- superlocalmemory（SLM 9 层 + TWF 衰减）→ [`.cursor/skills/dsg-l2b-node-organization-options/SKILL.md`](../../../skills/dsg-l2b-node-organization-options/SKILL.md) §1.5 + §6
- HippoRAG / AriGraph → [`.cursor/skills/dsg-l2b-node-organization-options/SKILL.md`](../../../skills/dsg-l2b-node-organization-options/SKILL.md) §6
- RustworkX 图模拟研究案例（§119-§122 仿生 4 范式）→ [`.cursor/skills/dsg-rustworkx-master/SKILL.md`](../../../skills/dsg-rustworkx-master/SKILL.md) §3.5

### 9.4 行为契约 / 既有约束

- [parrot_behavior_rules.md §3.7](../../parrot_behavior_rules.md) — Observer / Attention 边界
- [module_map_p2.md §10 / §11](../module_map_p2.md) — DSG 分层 + 时间轴 + MemoryValidity 过滤器位置

### 9.5 代码真源

- [src/parrot/dsg/l1_5_protocol.py](../../../../src/parrot/dsg/l1_5_protocol.py) — L1.5 合同
- [src/parrot/dsg/l2b_types.py](../../../../src/parrot/dsg/l2b_types.py) — L2-B 类型 + source dispatch
- [src/parrot/dsg/l2b_graph.py](../../../../src/parrot/dsg/l2b_graph.py) — RustworkX 工作记忆图（含将被改的 archive_episode 路径，§5.2）
- [src/parrot/dsg/ingest/](../../../../src/parrot/dsg/ingest/) — 5 filter + IngestRunner + base
- [src/parrot/dsg/triggers/](../../../../src/parrot/dsg/triggers/) — 4 触发器
- [src/parrot/dsg/attention/](../../../../src/parrot/dsg/attention/) — Phase 4 W6-7 attention 模块
- [tests/test_dsg/](../../../../tests/test_dsg/) — 234/234 测试基线（含 ADR-L1.5-001 +11 项）

### 9.6 相关工作区文件

- [workspace_index.md](workspace_index.md) — DSG 工作区入口
- [dsg_current_state_distilled.md](dsg_current_state_distilled.md) — 全景理解快照
- [opus_dsg_residual_intent.md](opus_dsg_residual_intent.md) — Opus 09/11/12/17/18/19 蒸馏
- [source_x_lifecycle_status.md](source_x_lifecycle_status.md) — source × lifecycle 现状
- [open_questions_for_design_chat.md](open_questions_for_design_chat.md) — 开放问题 + 用户已答 Q&A 原文

---

## §10 变更日志

- **2026-05-06**：本表创建。覆盖 Q1.1-Q3.4 第一问的全部决策 + 新冒出的 §4 注意力双开放（修正上轮 opus_residual 偏差）+ §5 工作记忆延迟归档（新约束）+ §1.2 防爆炸门控分层 + §3.2 Obsidian 三分类。所有 `provisional-revisit-after-L2-design` 条目在 Chat 2 sign off 后回审。
- **2026-05-06（Chat 2 实施完成回审）**：所有 11 条 `provisional-revisit-after-L2-design` 条目回审完毕，**9 条升 ratified / 2 条推 P3**（详见 [`dsg_l1_5_implementation_completion_20260506.md §6`](dsg_l1_5_implementation_completion_20260506.md)）：
  - **Ratified**：§1.1 L1.5 角色升级 / §1.1 与 L2-B 关系 / §1.2 入池门规则 / §1.3 入池条件 / §1.4 池上限+主动出池 / §3.1 _SOURCE_PRIORITY 切换开关 / §3.2 roleplay NodeKind / §6.5 子图分层 P1+P4 hybrid（部分）
  - **Deferred-to-P3**：§2.1 后期分图/Cluster / §3.5 跨 source 状态机分轴 / §6.5 P2 时间分层+真折叠
  - **新增 ratified**：GOSLO_AUTONOMOUS source priority=70（介于 IDENTIFY_OBJECT=80 和 CV_A10=60，master § 3.3 落地）
  - **配套**：8 份设计/协议文档 + 1 份完成报告 + 14 新模块 + 118 新测试。Phase 4 § 8 + cs_parity + ADR-L1.5-001 11 项三大守护全护，0 漂移。
