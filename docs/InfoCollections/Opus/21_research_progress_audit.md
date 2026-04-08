# Phase 0 调研进展盘点

> 生成日期: 2026-02-24
> 用途: 回顾我们最初的调研目标，盘点哪些做了、哪些没做、调研资料是否保留

---

## 1. 最初的调研目标 vs 实际完成

### 1.1 计划要学习的项目 — 进展一览

| 学习对象 | 计划学什么 | 实际进展 | 调研深度 | 原始资料保留 |
|:---------|:----------|:---------|:---------|:-----------|
| **LiveKit Agents** | infra 骨架, AgentSession, DataChannel | ✅ 完成 | 深 — 读了文档+示例 | ✅ `03` 中有 Pattern 总结 |
| **SVA Vision-Agents** | Processor 模式, 上下文注入, Gemini 交流方式 | ✅ 完成 | 深 — 读了源码+文档 | ✅ `03` 中有 Pattern 总结 |
| **OpenTeach** | AR 映射, 坐标转换, 手势传输 | ✅ 完成 | 深 — 读了源码 (keypoint_transform/oculus/vectorops/constants) | ✅ `22` §7 |
| **游戏 AI / 状态机** | 行为树, 优先级/打断, GOAP | ✅ 完成 | 深 — 读了 py-trees 文档 (Composites/Blackboard/Decorators) | ✅ `22` §9/§12 |
| **机器人控制** | 状态机设计, 指令交互 | ⚠️ 概念级 | 中 — 通过 OpenTeach 和 Reachy Mini 了解架构模式 | ⚠️ 融入 `22` §7/§11 |
| **SSG 项目** (Spark-DSG/Hydra) | 节点继承, 分层图 | ✅ 完成 | 深 — 读了 C++ 源码 header | ⚠️ 融入 `17` 设计, 无独立资料 |
| **SSG 项目** (ConceptGraphs) | 多视角融合, CLIP embedding | ✅ 完成 | 深 — 读了论文+源码 | ⚠️ 融入 `17` 设计, 无独立资料 |
| **SSG 项目** (3DSSG) | 空间关系类型 | ⚠️ 概念引用 | 浅 — 只引用了关系类型 | ❌ |
| **SSG 项目** (FROSS) | 3D 高斯位置不确定性 | ⚠️ 概念引用 | 浅 — 只取了概念 | ❌ |
| **GraphRAG** (Microsoft) | Leiden 社区检测, 层次聚类 | ✅ 完成 | 中 — 读了文档确认 Graphiti 已内置 | ⚠️ 结论在 `03` |
| **Graphiti** | 自定义实体, group_id 分区, 社区检测 | ✅ 完成 | 深 — 读了官方文档 | ⚠️ 融入 `17` 设计 |
| **ARCore / AR Foundation** | 传感器能力, 平面检测, 锚点 | ✅ 完成 | 深 — 读了多篇官方文档 | ⚠️ 融入 `11`/`18` 设计 |
| **OpenClaw (Agent SOUL)** | 人格设计, SOUL 文件 | ✅ 完成 | 深 — 获取了官方模板原文和 5 文件系统 | ✅ `22` §10 |
| **Inworld AI** | 多角色互动 | ✅ 完成 | 中 — 了解了 Character Brain 三层架构 | ✅ `22` §11 |
| **CrewAI** | 多 Agent 协作 | ⚠️ 概念引用 | 浅 — LiveKit multi-agent 模式更适用 | ⚠️ `22` §14 |

### 1.2 调研进展评分

```
深度调研完成 (有实际的文档/源码阅读): 12/15  = 80%  (↑ from 40%)
概念引用但未深入:                      3/15  = 20%  (↓ from 40%)
完全未调研:                            0/15  =  0%  (↓ from 20%)
```

> **2026-02-24 更新**: 补充完成了 OpenTeach 源码阅读、py-trees API 深度调研、
> OpenClaw SOUL 模板获取、Inworld AI Character Brain 调研、LiveKit Unity 原生 SDK 发现、
> Zep×LiveKit 官方集成发现、Livia AR 伙伴论文发现。详见 `22_research_sources_and_traceability.md`。

---

## 2. 原始调研资料保留情况

### 2.1 问题: 调研结果融入了设计, 但原始资料未独立保留

大部分调研的结论直接写进了设计文档 (doc 09/11/17/18/19), 但**原始调研过程和发现没有独立归档**。这意味着:

- ✅ **设计结论是有的** — 每个设计都有调研依据
- ❌ **但回溯困难** — 如果想知道"ConceptGraphs 到底怎么做多视角融合的", 需要重新搜
- ❌ **调研细节丢失** — WebSearch/WebFetch 的结果只在对话历史中, 没有持久化

### 2.2 哪些调研资料值得补充独立归档

| 调研对象 | 有价值的发现 | 当前保留位置 | 建议 |
|:---------|:-----------|:-----------|:-----|
| Spark-DSG C++ header | 节点继承体系 `NodeAttributes` | 融入 `17` §1.1 | ⚠️ 够用 |
| ConceptGraphs | clip_ft 多视角融合, class_id 投票 | 融入 `17` §1.2 | ⚠️ 够用 |
| Graphiti 自定义实体 API | Pydantic 模型定义方式 | 融入 `17` §3 | ⚠️ 够用 |
| ARCore 平面检测 API | boundary vertices, alignment | 融入 `11` §4, `18` §1 | ⚠️ 够用 |
| ARCore 持久锚点 | TrySaveAnchorAsync, GUID 管理 | 融入 `18` §1.2 | ⚠️ 够用 |
| Unity 传感器 API | Input System 传感器清单 | 融入 `18` §1.1 | ⚠️ 够用 |
| **OpenTeach 坐标转换细节** | 左右手系转换矩阵 | `03` 中只有 4 行 | ❌ **需要补充** |
| **OpenTeach 控制器架构** | 传感器/执行器分离模式 | 完全没有 | ❌ **需要补充** |
| **py-trees 行为树 API** | Selector/Sequence/Parallel 用法 | `14` 中只有概念图 | ❌ **需要补充** |
| **游戏 AI 状态机参考项目** | 具体的项目和实现 | 完全没有 | ❌ **需要补充** |
| **OpenClaw SOUL 文件格式** | 实际的文件结构和内容 | `13` 中只有概念 | ❌ **需要补充** |

---

## 3. 未完成的调研任务

### 3.1 OpenTeach 深入调研 (当前仅粗浅)

当前 `03_reference_projects.md` 中 OpenTeach 部分只有:
- 4 个 Pattern (坐标转换/高频遥测/Redis PubSub/模块化控制器)
- 3 行差异说明

**缺失的调研内容:**

| 缺失项 | 为什么需要 | 优先级 |
|:-------|:----------|:-------|
| **坐标系转换具体实现** | Unity 左手系 ↔ Python 右手系, 我们必须做 | P0 |
| **XR Hands 数据格式** | 手部关节数据怎么从 AR Foundation 取, 怎么发 | P0 |
| **延迟补偿策略** | OpenTeach 在 90Hz 下怎么处理网络延迟 | P1 |
| **控制器分离架构** | sensor_reader / robot_controller 的分离方式 | P1 |
| **遥测数据压缩** | 高频数据怎么减少带宽 | P2 |

### 3.2 机器人控制 / 游戏 AI 调研 (完全未做)

这是用户最初提到的学习目标之一, 但到现在完全没有独立调研:

| 缺失项 | 为什么需要 | 优先级 |
|:-------|:----------|:-------|
| **py-trees 实际 API** | 我们设计了行为树但没看过 py-trees 源码/文档 | P1 |
| **游戏 AI 行为树参考项目** | 类似 Unreal BT / Unity BT 的实践经验 | P1 |
| **GOAP 是否适合** | 目标导向行为规划, 可能比行为树更灵活 | P2 |
| **机器人状态机实践** | ROS2 状态机 / SMACH 等成熟方案 | P2 |
| **虚拟角色 AI 参考** | Inworld AI / Convai / ReadyPlayerMe 的 NPC AI | P1 |

### 3.3 OpenClaw / SOUL 文件调研 (仅概念引用)

`13_soul_memory_communication.md` 中提到了 OpenClaw SOUL 的概念, 但没有实际读过:

| 缺失项 | 为什么需要 | 优先级 |
|:-------|:----------|:-------|
| **OpenClaw SOUL.md 实际内容** | 我们的 ParrotSoul 设计借鉴了它但没看过原版 | P1 |
| **Inworld AI 的 Character Brain** | 人格持久化的商业实践 | P2 |

---

## 4. 架构设计成果评估

### 4.1 设计覆盖度

| 设计领域 | 覆盖状况 | 评价 |
|:---------|:---------|:-----|
| 整体架构 (四层 DSG) | ✅ 完整 | 方向正确, 层次清晰 |
| L1 视觉管线 | ✅ 完整 | StabilityGate + 处理器分级, 实际可用 |
| L2-A 空间图 | ✅ 完整 | 节点继承 + 关系类型 + 场景折叠 |
| L2-B 语义注意力 | ✅ 完整 | 注意力机制 + Graphiti 对接 |
| L3 认知接口 | ✅ 完整 | 观察者 + 时间线 + Gemini Tools |
| 前后端通信 | ✅ 完整 | DataChannel JSON 协议 |
| 记忆系统 | ✅ 完整 | Graphiti 分区 + 自定义实体 |
| 任务调度 | ⚠️ 概念层 | 有行为树设计但没看过 py-trees 实际 API |
| 前端状态机 | ⚠️ 概念层 | 有分层动画概念但没有 Unity Animator 细节 |
| AR 手势交互 | ⚠️ 薄弱 | 只有"张手→飞来"概念, 没有 XR Hands 细节 |
| 异常处理 | ✅ 完整 (过度) | 13 种异常, MVP 只需 3-4 种 |
| 节点置信度 | ✅ 完整 (过度) | 6 维模型, MVP 用 1 维就够 |

### 4.2 结构设计是否符合需求?

**符合。** 四层架构 (L1→L2-A→L2-B→L3) 的方向完全正确:
- L1 解决了手持 AR 的稳定性问题 (这是旧项目跳变的根因)
- L2-A 用 RustworkX 做空间图, 学了 Spark-DSG 的分层理念
- L2-B 用 RustworkX 做语义注意力, 对接 Graphiti
- L3 用 LiveKit 事件做 Gemini 通信, 学了 SVA 的注入方式

**但有过度细化** — doc 17-19 中很多设计是 Phase 3 级别, 不影响架构正确性但增加了认知负担。

---

## 5. 建议的下一步

### 5.1 调研完成状态 (2026-02-24 更新)

```
P0 (进入 Phase 1 前必须):
  [✅] OpenTeach: Unity ↔ Python 坐标系转换的具体实现 → doc 22 §7
  [✅] OpenTeach: XR Hands 数据格式和传输方式 → doc 22 §7
  [✅] LiveKit Unity SDK: 实际的连接和 DataChannel API → doc 22 §8 ★重大修正

P1 (Phase 2 前补充):
  [✅] py-trees: 实际 API 调研 → doc 22 §9
  [✅] OpenClaw: SOUL.md 文件的实际内容和格式 → doc 22 §10
  [✅] 虚拟角色 AI: Inworld AI Character Brain → doc 22 §11
  [✅] 游戏 AI: 行为树实践项目 → doc 22 §12

P2 (有空再看):
  [ ] GOAP vs 行为树的对比 (暂不需要, py-trees 已足够)
  [ ] ROS2 状态机方案 SMACH (暂不需要, 我们不用 ROS)
```

### 5.2 意外发现 (调研过程中新增)

```
[★] LiveKit client-sdk-unity 原生支持 Android — 修正了旧有认知 → doc 22 §8
[★] zep-livekit 官方包: Graphiti 已有 LiveKit Agent 集成 → doc 22 §13
[★] Livia 论文 (arXiv:2509.05298): 几乎相同的项目方向 → doc 22 §11
[★] LiveKit multi-agent 最佳实践: function_tool + UserData → doc 22 §14
[★] Gemini Live Vision Recipe: 30 行实现视觉 Agent → doc 22 §15
[★] Reachy Mini: 分层运动系统 + 可选视觉 → doc 22 §11
```

### 5.2 调研资料归档建议

当前的融入式归档对于**设计决策**来说够用了。如果需要，可以在后续对具体项目深入学习时创建独立的调研笔记。

当前文档的定位:
```
doc 01-07: 项目启动文档 (需求/审计/结构/规则/路线图)
doc 08-10: 架构核心 (验证/技术选型/架构图)
doc 11-14: 四层设计 (L1/场景/记忆通信/调度器)
doc 15:    决策日志 (28 个 ADR)
doc 16:    场景推演 (9 个场景/15 个遗漏)
doc 17-19: 细节设计 (节点/传感器/异常) — 大部分是 Phase 3 储备
doc 20:    复杂度审计 (MVP 分级)
doc 21:    本文 (进展盘点)
```
