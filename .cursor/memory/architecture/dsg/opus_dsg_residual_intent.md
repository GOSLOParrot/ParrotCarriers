---
status: ratified
category: workspace-snapshot
status_note: "Opus 09/11/12/17/18/19 中仍生效的 DSG 设计意图蒸馏。每条记录原文段落锚点 → 当前是否仍生效（active/superseded/absorbed）→ 对应当前代码或 ADR 位置 → 1-2 句蒸馏要点。Opus 原文 frontmatter 与路径不动。"
last_reviewed: 2026-05-04
ai_priority: medium
ai_audience: "DSG 系列设计 chat — 在做 L1.5 池/lifecycle/L2-B 升级前查看哪些早期设计意图仍可作为参考"
parent_doc: "workspace_index.md"
---

# Opus DSG 系列调研 — 仍生效的设计意图蒸馏

> **定位**：把 Opus 09/11/12/17/18/19 6 篇调研里的 DSG 相关设计意图按"是否仍生效"切片：
> - **active**：设计意图仍是当前正在进行 / 即将进行的方向；Chat 2 设计 L1.5 池 / lifecycle / L2-B 升级时**应**参考
> - **absorbed**：已落入当前代码或更近期 ADR / SKILL；引用新位置即可，**不必**回读 Opus
> - **superseded**：被新决策覆盖（如 ADR-L1.5-001 / Phase 4 §8 锁）；Opus 原文仅作历史
>
> **本文不做**：不重写 Opus、不修改 Opus 原文 frontmatter / 路径、不做新设计。Opus 原文仍归 `docs/InfoCollections/Opus/`，受 [INDEX.md §1.5 历史归档](../../INDEX.md) 约束。

---

## §0 总览表

| Opus | 标题 | 当前状态 | 主要去向 |
|:--|:--|:--|:--|
| 09 | DSG 技术选型（L2-A/L2-B RustworkX，L3 Graphiti）| **absorbed** | `l2b_graph.py`（RustworkX）+ `module_map_p2.md §10` + `bus_v4.md` |
| 11 | L1 视觉设计（区域裁剪 + 帧抽样 + ARCore + SVA）| 部分 **active**，多数 **absorbed** | AR Foundation skill + ConceptGraph SKILL + Phase 5+ A10 路径 |
| 12 | Scene + 时间轴 + SceneProfile | **absorbed** | `scene.md` + `sprint0_preflight.md §1` 时间轴 + DsgMode |
| 17 | DSG 节点 + 触发器设计 | **混合** — L2-A 节点继承 active；L2-B 注意力衰减 active；触发器矩阵 absorbed | 见 §3 |
| 18 | 传感器置信度 + StabilityGate + 节点生命周期审计 | **active**（多因素置信度链路 / 节点 TTL） | 见 §4 |
| 19 | 异常 / 幽灵 / EXPECTED / 多因素证据 | **active**（核心 lifecycle 设计意图 — Chat 2 重点参考） | 见 §5 |

---

## §1 Opus 09 — DSG 技术选型

**原文锚点**：`docs/InfoCollections/Opus/09_dsg_technology_selection.md`

| 设计意图 | 当前状态 | 落地位置 |
|:--|:--|:--|
| L2-A / L2-B 用 RustworkX 而非 Neo4j | **absorbed** | `src/parrot/dsg/l2b_graph.py` 使用 `rustworkx.PyDiGraph` |
| L3 长期记忆用 Graphiti | **absorbed** | `src/parrot/memory/graphiti_client.py` |
| FalkorDB 替代 Neo4j 的理由（Castle 2C8G 内存约束）| **absorbed** | [workspace.mdc §关键约束 #2](../../../rules/workspace.mdc) + [deploy_snapshot_p2_20260412.md](../../deploy_snapshot_p2_20260412.md) |
| L2-A 与 L2-B 平行但独立的双图设计 | **superseded**（部分）| L2-A 仍是 PLANNED；当前只有 L2-B 单图。Phase 5+ 重启 L2-A 时再回看 |

**Chat 2 不需要回读 Opus 09**。

---

## §2 Opus 11 — L1 视觉设计

**原文锚点**：`docs/InfoCollections/Opus/11_L1_vision_design.md`

| 设计意图 | 当前状态 | 落地位置 |
|:--|:--|:--|
| 区域裁剪 + 帧抽样作为 L1 入口节流 | **absorbed** | [SVA skill](../../../skills/sva-vision-agents/SKILL.md) Processor 模式 + Phase 4 lossy `parrot.ecp.tick` |
| ARCore TrackingState 作为门控信号 | **absorbed** | `l1_5_protocol.SensorFrame.ar_tracking_state` + AR Foundation 5.1.5 |
| SVA Processor 模式 | **absorbed** | [SVA skill](../../../skills/sva-vision-agents/SKILL.md) |
| StabilityGate（运动状态门控）| **active** — 命名仍使用，具体阈值实测未定 | 见 [§4](#4-opus-18-传感器置信度--节点生命周期审计) |
| L1 → L2-A track event schema | **superseded** | 由 [ADR-PROTOCOL-INTERFACE-001](../adr_protocol_upgrade_and_interface_refinement_background_20260504.md) + Phase 4 EcpEvent 13 类型替代 |

**Chat 2 参考要点**：StabilityGate 概念在 Phase 5+ A10 接入时仍是入口门控的备选；具体实现不重叠 ConceptGraph SKILL 的 IoU/CLIP 门控（ConceptGraph 是 detection 级别，StabilityGate 是 frame 运动级别）。

---

## §3 Opus 17 — DSG 节点 + 触发器设计

**原文锚点**：`docs/InfoCollections/Opus/17_dsg_node_and_trigger_design.md`

### §3.1 L2-A 节点继承体系（§1.3 原文）

| 设计意图 | 当前状态 | 备注 |
|:--|:--|:--|
| L2-A 节点继承（PhysicalNode / TrackedObjectNode / HandNode / FocusNode 等）| **planned**（P3 起重启）| 当前 L2-A 仍是占位；ConceptGraph SKILL §4 给出了 L2-A 节点描述生成的现代方案，可与本设计意图对照 |
| `class_votes` + `class_confidence` 多帧投票 | **active**（设计意图）| ConceptGraph SKILL §1.3 多帧 vote 是同主题的更现代方案；A10 接入时合并参考 |
| `gesture_confidence` 手势置信度字段 | **superseded**（部分）| Phase 4 perch_to_finger 用了 ECP RPC + Reflex 路径，不通过 L2-A 节点字段 |

### §3.2 L2-B 节点继承体系（§2 原文）

| 设计意图 | 当前状态 | 落地位置 |
|:--|:--|:--|
| `attention_weight` / `novelty_score` / `habituation_count` 三因子模型 | **partial absorbed**（字段已落，逻辑未落）| `l2b_types.py:SemanticNode.attention/novelty/habituation_count` 三字段都存在，但 **novelty 不衰减 / habituation 不累加** — Chat 2 设计空间。**2026-05-06 修正**：实现路径**双开放**（字段层 vs RustworkX 机制层），混合实施由 Chat 2 调研后裁决；详见 [dsg_decisions_master §4](dsg_decisions_master.md) + [dsg_current_state_distilled §5.4](dsg_current_state_distilled.md) |
| `is_notable() = attention > 0.4 or salience in (FOREGROUND, ALERT)` | **absorbed** | `l2b_types.py:SemanticNode.is_notable()` 同名实现 |
| Posner 注意力模型（外源 bottom-up + 内源 top-down + 习惯化）| **active**（设计意图）| Phase 4 W6-7 attention threshold 是 bottom-up 实现的开端；top-down + 习惯化未实现 |

### §3.3 Graphiti 自定义实体类型（§3 原文）

| 设计意图 | 当前状态 | 落地位置 |
|:--|:--|:--|
| Graphiti 自定义实体类型 schema | **absorbed** | `parrot.memory.graphiti_client` 当前用通用 EpisodeType；自定义实体类型未启用 |
| L2-B ↔ Graphiti 数据流（运行时不持久化 attention/novelty）| **absorbed** | `l2b_types.SemanticNode` 注释明确 "Attention/novelty/habituation are runtime-only (not persisted)" |
| 写回时使用自定义类型 | **deferred** | `runner.py` 内 TODO(S4.B) 标记未实施 |

### §3.4 触发器全景矩阵（§4 原文）

| 设计意图 | 当前状态 | 落地位置 |
|:--|:--|:--|
| L1 → L2-A 物理追踪事件（TRACK_STARTED / TRACK_LOST / STABILITY_CHANGED）| **superseded** | 当前由 EcpEvent 13 类型 + RefBinding 替代 |
| L2-A → L2-B 空间事件 | **planned**（P3 起重启）| L2-A 占位；Phase 5+ 重启 |
| L2-B → L3 语义注意力事件（ATTENTION_PEAK / ATTENTION_DECAY 等）| **partial absorbed** | Phase 4 W6-7 attention hint writer 是开端 |
| 4 触发器（Calendar / Message / SSOTEnrichment / SceneContext）| **absorbed** | `dsg/triggers/` 4 个文件已实现 |

### §3.5 注意力参数调优（H 项 + §1.4 §2.2 原文）

> 衰减速率 / 半衰期 / 增益常数 — Opus 17 §0.2 H 项标注 "P2 实测定"

**当前状态**：**active**（仍未实测）。Chat 2 设计 lifecycle 时若**走字段层路径**（[dsg_decisions_master §4](dsg_decisions_master.md) 双开放路径之一），需选定具体参数（半衰期 / 衰减曲线）；Opus 17 §5.3 的 Posner 模型 + 神经科学参考可作为起点。

**2026-05-06 修正**：上轮把 attention 衰减写成"走 RustworkX 机制层而非字段层"是**单选错误**。用户原话"注意力可以是子类 Node 的特殊字段也可以是 RustworkX 机制层"。两条路径都开放：

| 路径 | 工程实现 | Opus 17 / 神经科学锚点 |
|:--|:--|:--|
| **字段层**（保留 Opus 17 三因子） | `SemanticNode.attention/novelty/habituation_count` 字段衰减 | Opus 17 §5.3 Posner / Schneider-Shiffrin |
| **机制层**（走 RustworkX）| Cluster / 子图 / 折叠 / Spreading Activation / PPR | [`dsg-rustworkx-master §3`](../../../skills/dsg-rustworkx-master/SKILL.md) 4 仿生范式 |
| **混合**（推荐基线） | 拓扑骨架走 RustworkX + 高频状态挂 payload | [`dsg-rustworkx-master §1.2`](../../../skills/dsg-rustworkx-master/SKILL.md) 骨架 vs 血肉范式 |

### §3.6 Chat 2 应参考 Opus 17 哪些段落

| Opus 17 段落 | Chat 2 参考用途 |
|:--|:--|
| §2.2 L2-B 节点继承体系 | "AttentionSystem" 三因子的最早设计稿；Chat 2 决定要不要让 novelty 真的衰减时回查 |
| §0.2 H 项 + §5.3 注意力神经科学 | 衰减参数选择的理论起点（不是必须，可选）|
| §4.3 L2-B → L3 ATTENTION_DECAY 事件 | 节点何时从 ACTIVE 退到 BACKGROUND 的事件触发设计意图 |

---

## §4 Opus 18 — 传感器置信度 + 节点生命周期审计

**原文锚点**：`docs/InfoCollections/Opus/18_sensor_confidence_navigation_audit.md`

### §4.1 节点置信度完整链路（§3 原文）— **核心 active 内容**

| 设计意图 | 当前状态 | 备注 |
|:--|:--|:--|
| 节点置信度从传感器到节点的 9 段链路问题分析（光照 / 过曝 / WebRTC 压缩 / 反射 / 假阳性 / 距离失真 等）| **active** | 当前 Detection 只有 `confidence: float [0,1]` 单字段；多因素分解未实现 |
| 假阳性 → 幽灵节点的 TTL 机制（"低 confidence 短时间存活"）| **active** | 当前 `confirmation_status=GHOST` 是 enum 值，无主动转换逻辑 |
| 综合置信度评估模型（§3.3）| **active** | Chat 2 lifecycle 设计的关键参考 |

### §4.2 L1 缓冲功能（§2 原文）

| 设计意图 | 当前状态 | 备注 |
|:--|:--|:--|
| StabilityGate（运动门控，stability_upgrade_delay / downgrade_delay）| **partial absorbed** | `l1_5_protocol.SensorFrame.ar_tracking_state` 字段存在；具体 stability tier 和延迟逻辑未实现 |
| 标签缓冲（多帧投票）| **active** | ConceptGraph SKILL §1.3 多帧 vote 提供更现代方案 |
| 位置缓冲 | **active** | 当前无；P3 起 L2-A 重启时考虑 |
| SceneProfile（室内 / 户外不同阈值）| **superseded**（部分）| 当前由 DsgMode 4 模式替代（DSG_TEXT_ONLY / DSG_GEMINI_VISION / DSG_FULL / DSG_SENTINEL_AUX）|

### §4.3 节点生命周期 vs StabilityGate 适配（§5 原文）

> Opus 18 §5 关注点：节点的 first_seen / last_seen / lost / archived 状态机如何跟 StabilityGate 互动。

**当前状态**：**active**（核心未实现）。当前 `SemanticNode.last_seen_this_session` 只在 `touch()` 时更新；没有"too long unseen → archive" 转换。Chat 2 设计 lifecycle 时这是关键缺失点。

### §4.4 Chat 2 应参考 Opus 18 哪些段落

| Opus 18 段落 | Chat 2 参考用途 |
|:--|:--|
| §3.1 链路全景图 | 多因素 confidence 设计基线（要不要把 `evidence_score` 拆成多因素？）|
| §3.3 综合置信度评估模型 | 公式形式参考；具体加权未定 |
| §5 节点生命周期 ↔ StabilityGate 适配 | 节点 TTL / archive 触发条件设计的最早稿 |

---

## §5 Opus 19 — 异常 / 幽灵 / EXPECTED / 多因素证据

**原文锚点**：`docs/InfoCollections/Opus/19_anomaly_ghost_expectation_vision.md`

> 这是 Chat 2 设计 lifecycle 的**最重要**Opus 参考。

### §5.1 EXPECTED 状态（§2.2 原文）— **核心 active**

| 设计意图 | 当前状态 | 落地位置 |
|:--|:--|:--|
| EXPECTED 状态语义（"我相信你在那里，但我还没亲眼看到"）| **absorbed** | `l2b_types.ConfirmationStatus.EXPECTED` enum 值已存在 |
| 预加载场景时所有物体初始 = EXPECTED | **absorbed** | `l2b_graph.preload_from_graphiti()` 创建节点 confirmation = EXPECTED |
| EXPECTED → ACTIVE 通过 ReID 匹配 | **active**（路径未通）| 当前没有 ReID；`from_observation` 直接根据 obs.confirmation 设置；Chat 2 lifecycle 设计要补这条转换 |
| EXPECTED → OUT_OF_VIEW（30s 未见）| **active**（未实现）| Chat 2 设计点 |
| 每个 EXPECTED 节点的验证倒计时 | **active**（未实现）| Chat 2 设计点 |

### §5.2 多因素证据确认（§2.3 原文）— **核心 active**

| 设计意图 | 当前状态 | 备注 |
|:--|:--|:--|
| 多因素证据加权（位置一致 +0.15 / 形状匹配 / 时间衰减 / 等等）| **active**（未实现）| 当前 `evidence_score` 是单维 float；Chat 2 决定要不要做多因素分解 |
| `REJECTION_THRESHOLD = -0.3` → 否定为幽灵 | **active**（未实现）| Chat 2 lifecycle 设计点 |
| GHOST 状态触发条件 | **active**（未实现）| `ConfirmationStatus.GHOST` 是 enum 值，无主动转换 |

### §5.3 异常处理矩阵（§1.5 原文）

| 设计意图 | 当前状态 | 备注 |
|:--|:--|:--|
| 硬件 / 姿态 / 环境三级异常 | **active**（仅设计，未实现）| Phase 4 已有 connection_health 4 态聚合（与硬件级异常部分重叠）|
| 镜面反射造成 SAM2 追踪镜中物体 → 幽灵 | **noted** | A10 接入后需要参考 |

### §5.4 视觉模型编排（§3 原文）— 与 ConceptGraph SKILL 重叠

| 设计意图 | 当前状态 | 备注 |
|:--|:--|:--|
| SAM2 + DINOv2 + YOLO 编排 | **superseded** | [ConceptGraph SKILL](../../../skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md) §2 提供更现代的蒸馏（含 RAM / Grounded-SAM）|

### §5.5 Chat 2 应参考 Opus 19 哪些段落（**重点**）

| Opus 19 段落 | Chat 2 参考用途 |
|:--|:--|
| §2.1 幽灵节点定义 | "什么是 GHOST 状态" 的语义锚点 |
| §2.2 EXPECTED 状态语义 + 验证倒计时 | EXPECTED → ACTIVE / OUT_OF_VIEW / GHOST 状态机设计 |
| §2.3 多因素证据加权 + REJECTION_THRESHOLD | `evidence_score` 是否要拆多因素 + 拒绝阈值数值 |
| §1.5 异常处理矩阵 | 何时把节点标 GHOST（vs 仅降 confidence）|

---

## §6 总结：Chat 2 应回读的 Opus 段落清单

按重要度排序：

| 排序 | Opus + 段落 | 用途 |
|:--|:--|:--|
| 1（必读）| Opus 19 §2.1-§2.3 | EXPECTED + GHOST + 多因素证据的最早设计稿 |
| 2（推荐）| Opus 18 §3.1-§3.3 + §5 | 多因素 confidence 链路 + 节点生命周期 ↔ StabilityGate |
| 3（推荐）| Opus 17 §2.2 + §4.3 | L2-B 注意力三因子（走字段层时的字段定义参考）+ ATTENTION_DECAY 事件触发 |
| 4（可选 — 字段层路径需读）| Opus 17 §0.2 H + §5.3 | 注意力衰减参数选择的理论起点（**仅当 Chat 2 选字段层或混合路径时需要**）|
| 5（可选）| Opus 18 §2 | L1 缓冲功能（标签 / 位置缓冲）|

**所有 Opus 17/18/19 的具体 schema / API / class 定义**：**仅作历史参考**，不要逐字照抄到设计稿。Phase 4 §8 的合同锁 + ADR-L1.5-001 的 source dispatch 决策**优先**于任何 Opus 早期 schema。

**Chat 2 优先看新蒸馏**：4 个 2026-05-06 落地的 DSG skill（[`dsg-rustworkx-master`](../../../skills/dsg-rustworkx-master/SKILL.md) / [`dsg-l2b-node-organization-options`](../../../skills/dsg-l2b-node-organization-options/SKILL.md) / [`dsg-attention-schema-papers`](../../../skills/dsg-attention-schema-papers/SKILL.md) / [`dsg-l1-5-l2a-conceptgraph-distilled`](../../../skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md)）+ 6 份 Gemini 蒸馏（`NewZone/distill_output/`），其内容可能比 Opus 旧文给出**更现代的解法**；Opus 仅作历史回查。

---

## §7 不可违反的边界（与本工作区其他文件保持一致）

引自 [workspace_index.md §5](workspace_index.md):

1. 本文是**蒸馏与引用**，**不修改 Opus 原文 frontmatter / 路径**
2. Opus 中已被 ADR-L1.5-001 / Phase 4 §8 / ConceptGraph SKILL **覆盖**的部分标 `superseded` 或 `absorbed`
3. Opus 的 `active` 部分仅是**设计意图**，不是落地承诺；Chat 2 设计稿可参考也可不采纳
4. 本工作区 `dsg_current_state_distilled.md` §10.3 引用本文；本文不直接对外，仅作 §10.3 的展开

---

## §8 引用

- Opus INDEX：[../../../../docs/InfoCollections/Opus/INDEX.md](../../../../docs/InfoCollections/Opus/INDEX.md) — 26 篇调研全索引（含 DSG 系列 09/11/12/17/18/19）
- ConceptGraph SKILL：[../../../skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md](../../../skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md) — A10 入口侧的现代蒸馏
- ADR-L1.5-001：[../adr_l1_5_source_dispatch_extension_space_20260504.md](../adr_l1_5_source_dispatch_extension_space_20260504.md) — source dispatch 决策锁
- Phase 4 §8：[../sprint4_phase4_entry_20260430.md](../sprint4_phase4_entry_20260430.md) — 13 决策锁
- 当前理解快照：[dsg_current_state_distilled.md](dsg_current_state_distilled.md)
