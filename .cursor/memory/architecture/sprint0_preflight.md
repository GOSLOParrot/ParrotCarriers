---
status: tentative
status_note: "流程约束本身引自成熟实践 (ADR / 三闸门 / Event Sourcing), 不经代码。但 14 项 S0.A-N 是否落得下来, 要完成后才算 ratified。届时把 §7 任务单标 DONE 并整体升 ratified。"
last_reviewed: 2026-04-22
---

# Sprint 0 前置 Checklist — 开工前先收口这 6 件事

> 日期: 2026-04-22
> 起因: 用户在 Sprint 0 开工前提出 6 件担心, 不先解决就开工会踩坑
> 状态: **必须在 Sprint 0 代码任务 (S0.1-S0.7) 之前全部 ✅ 过一遍**
> 口径: 只定**流程约束和工具合约**, 不定任何尚未验证的产品代码细节

---

## 0. TL;DR — 用户的 6 件担心和对应处置

| # | 用户担心 | 本文档处置 | 严格度 |
|:--|:--------|:----------|:------|
| 1 | 时间轴/事件/数据标注怎么统一到 DSG, 我担心综合不起来 | §1 **四层时间轴统一模型** (对齐 2026 前沿 Chronos/REMem/SEEM + Claru 机器人标注) | 需先敲定 |
| 2 | 施工时上下文/架构在 Cursor 里怎么确保不出错 | §2 **Cursor 工作合约** (每次开工开 context / PR 级工作流 / 不写代码只改计划) | 需先敲定 |
| 3 | 联网搜索在 Cursor 开工前怎么确认/补需求 | §3 **开工前调研 checklist** (3 条硬规则) | 轻量 |
| 4 | 验收流程够严谨吗 / Cursor 能写好 AR 代码吗 | §4 **三闸门验收** (Claru 机器人标注借鉴 + Unity/Brain 分跑道) | 需先敲定 |
| 5 | 版本锁都锁好了吗 | §5 **版本锁审计** (现在就 sanity check) | 轻量, 已基本就位 |
| 6 | 项目内规则/约束要定好, 但怎么防提前锁死 | §6 **tentative vs. ratified 两态机** (学 ADR + VIRF tutor-apprentice) | **核心** |

---

## 1. 四层时间轴统一模型 — 先把"怎么记事"敲死

### 1.1 为什么需要这一节

你的担心 100% 合理。现在项目里**四个地方在各自记时间**, 没有统一口径:

1. **Graphiti `add_episode(reference_time=...)`** — 已在用 (`conversation_writer.py`, `identify_object.py::_save_new_object`), 但只写对话和物体
2. **DSG L2-B `SemanticNode`** — 有 `first_seen_at / last_seen_at`, 但没有"事件"概念
3. **Redis Stream** — `shared/constants.py` 有 `STREAM_EVENTS`, 实际只跑了部分消息
4. **Sprint 1 新加的 `obs_log` (VIGIL 式)** — 准备加, 还没加

**不收口就开工 = 四条时间轴, 查的时候永远差一条**。

### 1.2 2026 前沿共识 (调研结果)

| 来源 | 关键洞见 | 搬过来的部分 |
|:-----|:--------|:-----------|
| **Chronos** (arxiv 2603.16862, 2026-03) | **Event Calendar (结构化, 有 datetime 范围) + Turn Calendar (原始对话保留)** 双索引, 互不替代 | GOSLO: Graphiti episode = Turn Calendar, L2-B + PhotoEvent = Event Calendar, 两者并存 |
| **REMem** (arxiv 2602.13530, 2026-02) | **Gist (人读摘要) + Fact (time-scoped triple)** 两种粒度, 链接到 timeline + 情境维度 | PhotoEvent 节点结构按这个设计, 保留原图 URI + 三元组 + 情境 |
| **SEEM** (arxiv 2601.06411, 2026-01) | **Episodic Event Frame** 有精确 provenance pointer, 支持 Reverse Provenance Expansion | 所有 L2-B 节点强制 `provenance_stream_id` 字段, 能反查原始 event |
| **eventure + Chronos Engine** (2026-03 开源游戏 NPC memory) | **Event Sourcing**: 所有状态变化都是 immutable event, EventLog 是 single source of truth, 支持时间旅行 | Redis Stream 做**唯一真实事件日志**, 其他派生物 (Blackboard/BT/L2-B) 都是投影 |
| **Claru 机器人标注 2026** | **三层标注粒度**: Dense timestep / Phase segment / Skill-level, 不要混 | 我们**只做 Phase segment 和 Skill-level**, Dense timestep 留给 A10 P3 |

### 1.3 GOSLO 四层时间轴 (**Sprint 0 敲死, 后面只扩不改**)

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 0 — Raw Event Stream (Redis Stream)                   │
│  真实发生的原始事件, 永不删, Event Sourcing 的 source of truth │
│  key: parrot:event_log                                        │
│  schema: {ts, kind, layer(reflex|intent|task), actor, payload}│
│  写: 所有 Sprint 1+ 代码都走这里 (dispatcher / StateInjector) │
└─────────────────────────────────────────────────────────────┘
         │
         ├──── 投影 ────→ Layer 1 — Blackboard (当前状态快照)
         │                只保留"现在", 不保留历史
         │                py-trees Blackboard, 4 作用域
         │
         ├──── 投影 ────→ Layer 2 — Graphiti Episode (Turn Calendar)
         │                对话 turn 和大事件, reference_time 锚定
         │                已在跑 (conversation_writer)
         │
         └──── 投影 ────→ Layer 3 — DSG L2-B Event Nodes (Event Calendar)
                           结构化事件节点 (PhotoEvent/ObjectNode/EncounterEvent)
                           有 datetime 范围 + 情境维度 + provenance 回指 Layer 0
                           Sprint 4 扩充
```

**四层的职责划分** (红线, 不准越界):

| 层 | 写入条件 | 保留期 | 用来查什么 | **禁止** |
|:---|:--------|:-------|:----------|:--------|
| L0 事件流 | 所有 dispatcher 分发决策 / BB 变化 / RPC ack / 异常 | 永久 (P3 后做归档) | "到底发生过什么" | 禁止直接从 L0 查业务结果 (要经 L2/L3 投影) |
| L1 Blackboard | 只写"当前值", 不写 append | 运行期内存 | "现在是什么状态" | 禁止当时间轴用, 查不到历史 |
| L2 Graphiti Episode | 对话 turn / 长事件总结 (Gist 级) | 永久 | "什么时候说过什么 / 做过什么" | 禁止塞结构化字段 (进 L3) |
| L3 L2-B Event Node | 有明确 schema 的结构化事件 (Fact 级) | 永久 + Salience 淘汰 | "去年买的手办第一次在这个场景被看到" | 禁止不带 provenance 入 L3 |

**关键约定**: L0 是**唯一写端**, L1/L2/L3 都通过订阅 L0 Stream 异步投影 (学 eventure + CQRS)。这样**查任何时间点的状态都可以从 L0 replay**, 没有"某条数据不知道哪里写的"困扰。

### 1.4 Sprint 0 要做什么

| 任务 | 位置 | 产出 |
|:-----|:-----|:-----|
| **S0.A — 锁 L0 Stream schema** | `src/parrot/shared/event_log.py` 新文件 | `EventEnvelope` Pydantic 模型 (ts / kind / layer / actor / payload / provenance_parent) |
| **S0.B — 锁 L3 节点共同基字段** | `src/parrot/dsg/l2b_types.py` 扩 | 所有节点强制 `provenance_stream_id: str = ""` + `time_span: tuple[datetime, datetime | None]` |
| **S0.C — 时间轴 API 约定** (文档) | 本文档 §1 + commit_guidelines 加一节 | "任何新写入必须先进 L0, 再投影到 L1/L2/L3" |

**Sprint 0 不做**: 真的跑起来投影管线 (Sprint 1 做) / PhotoEvent 节点 (Sprint 4 做) / 归档策略 (P3)。

---

## 2. Cursor 工作合约 — 施工时上下文不跑偏

### 2.1 每次开工前的"5 秒检查"

> **用户的真实问题**: Cursor agent 在长 session 里可能忘掉需求、改错文件、或自作主张加功能。

**硬规则** (写进 `.cursor/rules/workspace.mdc`):

| 条目 | 怎么做 | 为什么 |
|:-----|:------|:------|
| 1. 每个 Sprint 开 **新会话** | 不要在一个 session 里跨 Sprint, 新会话第一句话必须是 "读 `active_context.md` 和 `ar_feature_implementation_plan.md` Sprint X 那一节, 告诉我你要做什么, 先别动代码" | 防上下文污染; 让 agent 用自己的话复述一遍需求 |
| 2. 每个任务开头 agent 必须**先说要改哪几个文件**, 等确认再动手 | prompt: "S1.F 要改哪几个文件? 列清单, 别动代码, 等我确认" | 防"悄悄改了 10 个文件"; 避免越界 |
| 3. **不许 agent 改 `active_context.md` 的 "当前状态" 段** | 由用户手动维护 | 这是真相锚点, agent 改了就假真相 |
| 4. 每完成一个 **S1.X 子任务就提 commit**, 不攒大 commit | `commit_guidelines.md` 已有, 强化执行 | 小颗粒好 review, 坏了能回滚 |
| 5. **写代码前先读 3 个文件**: 本模块 / 被调用方 / 被调用方的测试 | prompt 里塞: "先 Read 这 3 个文件, 然后告诉我你要改什么" | 防"重复造轮子" / "API 签名不对" |

### 2.2 Cursor 能写好 AR 项目的代码吗 — 诚实回答

**可以, 但有边界**:

| 类型 | Cursor 擅长度 | 建议 |
|:-----|:------------|:----|
| Python 后端 (Brain/DSG/Scheduler) | ⭐⭐⭐⭐⭐ | 放手让它写, 但要带测试 |
| Unity C# 业务逻辑 (RoomManager/ParrotRpcHandler) | ⭐⭐⭐⭐ | 让它写, 但**必须 Editor Play 实跑验证**, 编译通过不等于能跑 |
| Unity Shader / URP / Rendering | ⭐⭐ | **手工验证**, 别信 agent 说"这样写就行" |
| AR Foundation / XR Hands 新特性 | ⭐⭐⭐ | 让它按 `ar-foundation.mdc` 已知坑规避, 但**真机必验** |
| LiveKit SDK 细节 (Track / DataChannel) | ⭐⭐⭐⭐ | 已有 skill, 按 skill 跑, 有坑 agent 可能凭印象写错 API |
| 设计/架构决策 | ⭐⭐⭐ | Agent 容易过度工程, 要用 §6 tentative 机制压制 |

**不让 Cursor 做的事** (硬红线):
- ❌ 版本锁 / pyproject.toml / manifest.json 的升级 (必须用户手动确认)
- ❌ 部署脚本的"自动修复" (sync-castle.ps1 / docker compose)
- ❌ 修改 `active_context.md` 真相段 (见 §2.1 第 3 条)
- ❌ 删 commit / force push
- ❌ 改 `.env` / secrets

### 2.3 Sprint 0 要做什么

| 任务 | 位置 | 产出 |
|:-----|:-----|:-----|
| **S0.D — 在 `workspace.mdc` 加"Cursor 工作合约"节** | `.cursor/rules/workspace.mdc` | §2.1 5 条 + §2.2 硬红线 |
| **S0.E — Sprint 开工模板** | `.cursor/memory/sprint_kickoff_template.md` | 每个 Sprint 开工的"先读什么 / 不准做什么 / 先产出什么"模板 |

---

## 3. 开工前的联网调研 Checklist — 怎么查缺补漏

### 3.1 三条硬规则

> 你问"联网搜索在 cursor 开工前怎么确认和收集和查缺补漏需求"。就这三条:

**规则 1 — 只在 Sprint 开工当天调研一次, 不反复刷**

每个 Sprint 开工第一件事: agent **主动**跑一轮 `WebSearch` 针对本 Sprint 涉及的 2-3 个关键技术点, 看 2026 年是否有新做法**颠覆**当前设计。如果有 → 加一条 tentative 条目到 §6 queue 里, **但不改当前 Sprint 范围**。

**规则 2 — 查的内容必须"可落到代码"**

| ❌ 不好 | ✅ 好 |
|:-------|:-----|
| "2026 最新 AR 架构" | "Unity 6.2 AR Foundation 的 `ARAnchorManager.TryAddAnchor` 是否仍需要 raycast hit" |
| "GOSLO 应该怎么设计" | "LiveKit DataChannel 单帧 payload 安全上限 2026 年是否仍是 15KB" |
| "游戏如何做时间轴" | "Bevy observer pattern 对应 Python 的什么库 (完成 L0 Stream 订阅时参考)" |

**规则 3 — 每条调研结论落到 ADR**

凡是调研发现"我们设计错了"或"有更好方案" → 写进 `.cursor/memory/architecture/adr/` 目录下新文件 `ADR-0XX-<名字>.md`, 格式: `状态 (proposed/accepted/rejected) / 背景 / 调研证据 / 决策 / 对哪些 Sprint 的影响`。**不合并进 `ar_feature_vision.md`**, 因为 vision 文档是已定稿的架构契约, 修它要走 §6 的 ratify 流程。

### 3.2 已完成的调研 + 本次新加

> **注意**: 本表"状态"列指**调研环节是否收口**, 与**文档 frontmatter 的 status** (tentative / ratified) **不是一回事**。调研可以收口, 但基于调研得出的**代码架构方案**只有代码落地后才升 ratified。见下面"调研收口 vs 架构 ratified"对照。

| 调研主题 | 主源文档 | 调研状态 | 架构 status |
|:--------|:--------|:--------|:-----------|
| AR 相机交互 | `ar_camera_interaction_survey.md` | 调研收口 | ratified (不再改) |
| GOSLO 自知 / 三层意识 | `ar_feature_vision.md` §3.5 | 调研收口 | **tentative** (Sprint 1 S1.C 代码落地后升) |
| DSG 两轴正交 | `ar_feature_vision.md` §3.6 | 调研收口 | **tentative** (Sprint 2 代码落地后升) |
| Reflex/Intent/Task 三级调度 (与意识分发统一) | `ar_feature_vision.md` §3.5 三合一 | 调研收口 | **tentative** (Sprint 1 S1.F/G 代码落地后升) |
| **🆕 时间轴/事件记录/数据标注** | **本文档 §1** | 调研收口 | tentative (S0.A-C 落地后升) |
| AR 真机场景 (ARCore / ARKit / ARWorldMap) | `ar-foundation.mdc` (只写坑) | partial, Sprint 3 前补调研 | — |
| Gemini Flash 多图视觉比对的 token 成本 | 未调研 | **Sprint 4 开工前补** | — |

**规则**: **调研主题只讨论 1 次, 主源只有 1 个**。其他地方提到必须指向主源, 不复述不改写。在主源以外改动 → 视为违反 §6 ratify 流程。

### 3.3 Sprint 0 要做什么

| 任务 | 位置 | 产出 |
|:-----|:-----|:-----|
| **S0.F — 建 ADR 目录和模板** | `.cursor/memory/architecture/adr/README.md` + `adr_template.md` | 模板文件 |
| **S0.G — 把已有的隐式决策补成 ADR** (追溯补) | `adr/ADR-001-py-trees-blackboard.md` `ADR-002-video-tier-dsg-mode-orthogonal.md` `ADR-003-three-layer-consciousness.md` | 3 个 ADR, **既不要重写内容, 只写"状态+索引到 vision 某节"** |

**不做**: 不追溯写所有历史决策的 ADR, 只挑最近 3 个影响面最大的。

---

## 4. 验收流程的严格度 — 三闸门

### 4.1 现在的验收长什么样

每个 Sprint 在 `ar_feature_implementation_plan.md` 有"验收用例"清单 (例: Sprint 1 的 5 条)。这是**单一闸门**, 不够严。

### 4.2 升级成三闸门 (借鉴 Claru 机器人标注 2026 + SVRC 数据质量三段闸)

```
┌─ Gate 1: 单元自测 (agent 写完代码自己跑) ────┐
│  Python: pytest 相关模块 (最小 skeleton)    │
│  C#:     Unity Editor 编译通过              │
│  必要: agent 必须贴出测试输出, 不是"应该能跑"│
└────────────────────────────────────────────┘
         │ 通过
         ▼
┌─ Gate 2: 跑通用例 (用户手动 Play) ──────────┐
│  按验收用例 1-N 条, 逐条勾选                 │
│  失败: 退回 agent 修, 不进 Gate 3           │
│  每条 ≤10 分钟验完, 超时说明用例设计太重    │
└────────────────────────────────────────────┘
         │ 通过
         ▼
┌─ Gate 3: 回归 (不破坏前 Sprint) ────────────┐
│  重跑前一个 Sprint 的验收用例 (抽 1-2 条)    │
│  失败: 说明本 Sprint 改动有回归, 强制修复   │
└────────────────────────────────────────────┘
         │ 通过
         ▼
      Sprint 收, 打 tag v-sN, 进下一 Sprint
```

### 4.3 每类代码的最低验收门槛 (不同类型不同门槛)

| 代码类型 | Gate 1 (单测) | Gate 2 (用例) | Gate 3 (回归) |
|:---------|:------------|:-------------|:-------------|
| Blackboard 扩域 / Scheduler BT | pytest 必须 | 手动 tick 跑日志 | 回归 P2 连通 |
| Unity C# 业务脚本 | 编译 + Editor Play | 真实 Play/Stop/Play 3 次 | 回归 Unity 麦克风+视频 |
| Unity Rendering/Shader | 编译 | Editor 截图对比 | — |
| AR Foundation (真机/模拟) | — | **XR Simulation Editor Play** + **Android/iOS 真机跑** | 回归 Editor Webcam 通路 |
| LiveKit SDK 调用 | 编译 | Brain agent 日志显示订阅 | 回归 MIC+CAM 连通 |
| Graphiti / L2-B 写入 | pytest | Graphiti 查到新节点 | 回归已有记忆节点 |

### 4.4 Sprint 0 要做什么

| 任务 | 位置 | 产出 |
|:-----|:-----|:-----|
| **S0.H — 写三闸门规则** | `.cursor/memory/test_gate_rules.md` 新文件 | §4.2 + §4.3 |
| **S0.I — 每 Sprint 的验收用例补"Gate 归类"** | `ar_feature_implementation_plan.md` 每 Sprint 验收段 | 每条用例标 `[Gate 1/2/3]` |

**不做**: 不写 CI/CD (Sprint 4 后再说) / 不做 perf benchmark (P3)。

---

## 5. 版本锁审计 — 开工前 sanity check

### 5.1 现有版本锁 (从 `active_context.md`)

| 依赖 | pyproject.toml | Castle | 状态 |
|:----|:-------------|:------|:----|
| `livekit-agents[google]` | `>=1.5,<2.0` | 1.5.2 | ✅ |
| `graphiti-core[falkordb,google-genai]` | `>=0.28,<0.29` | 0.28.2 | ✅ |
| `redis` | `>=7.1,<9.0` | 7.4.0 | ✅ |
| `python-dotenv` | `>=1.0,<2.0` | 1.2.2 | ✅ |
| `py-trees` | `>=2.4,<3.0` | 2.4.0 | ✅ |
| `rustworkx` | `>=0.15,<1.0` | 0.17.1 | ✅ |
| LiveKit Unity SDK | commit hash 锁 | 同 | ✅ |

### 5.2 Sprint 1-4 要用的新依赖 — 现在就锁

| 依赖 | 用途 | 建议锁 | 锁的时机 |
|:----|:----|:------|:---------|
| `livekit-agents[images]` (Pillow) | Gemini 看视频需要 (已在 Castle 装) | `>=11,<12` (Pillow) | **Sprint 0** 写进 pyproject.toml (目前漏了) |
| `google-genai` | Gemini tool + 多图比对 | 跟 `livekit-agents[google]` 走 | 继承 |
| `pydantic` | L0 Stream Envelope | `>=2.5,<3.0` | Sprint 0 |
| `AR Foundation` & `XR Simulation` | AR 功能底座与编辑器内测试 | `5.1.5` | Sprint 0 已注入 manifest.json |
| Unity `UIToolkit` (UXML/USS) | 便签 / 启动屏 | Unity 2022.3 自带, 无需锁 | — |
| Unity `XR Hands` | 已有 | 已锁 | — |
| Unity `URP` / 粒子 | Sprite / 动画 | Unity 2022.3 自带 | — |
| Neo4j 驱动 (`neo4j`) | **我们不用, 已换 FalkorDB** | 禁止装 | — |
| `serpapi` / `googlesearch-python` | S4.B5 `web_search` tool (选项 α) | 先不装, Sprint 4 开工再决定 | 延期 |

### 5.3 Sprint 0 要做什么

| 任务 | 位置 | 产出 |
|:-----|:-----|:-----|
| **S0.J — 补 `livekit-agents[images]` 和 `pydantic>=2.5` 到 pyproject.toml** | `pyproject.toml` | 两行 |
| **S0.K — Castle SSH 跑 `pip list` 和本地对比** | 脚本 `infra/audit_deps.ps1` 新建 | 输出 diff, 确认没有漂移 |

---

## 6. 防提前锁定 — tentative vs. ratified 两态机

> **用户原话**: "项目内约束和规则要定好, 但怎么注意不会偏移导致提前锁住和没有写好代码和验证就预先设计 (这点我被坑过)"

这是**整个清单最重要的一节**。

### 6.1 坑的根源

- **规则 (`.cursor/rules/*.mdc`)** 一旦写下, agent 会**严格遵守**, 哪怕规则本身有错
- **设计文档 (vision / plan)** 一旦写下, 后续工作容易"按文档走", 哪怕没跑过代码验证
- **skill (`.cursor/skills/*/SKILL.md`)** 一旦写下, agent 会**按 skill 写代码**, 哪怕 skill 是凭调研写的, 没验证过
- 这就是**提前锁定**: 设计跑得比代码快, 等代码跑起来发现设计错了, 但规则已经把 agent 锁死在错的路上

### 6.2 两态机 (学 ADR 的 `proposed / accepted / deprecated` + VIRF tutor-apprentice)

```
┌────────────────┐     代码跑通 + 验收通过      ┌──────────────┐
│   TENTATIVE    │ ────────────────────────▶ │  RATIFIED    │
│   (试探期)     │                            │  (已批准)     │
│                │ ◀──────────────────────── │              │
│ Agent 可参考   │     发现问题 → demote       │ Agent 必须遵守│
│ 但不强制遵守   │                            │              │
└────────────────┘                            └──────────────┘
```

### 6.3 落地规则

**每个规则/skill/设计文档**开头必须有一个 YAML frontmatter 或顶部标记:

```markdown
---
status: tentative | ratified
ratified_by: [Sprint 名, git commit hash, 日期]
last_reviewed: 2026-04-22
review_trigger: "代码 X 跑通 + 验收用例 Y 通过"
---
```

**Agent 的处理**:

| status | Agent 行为 |
|:-------|:----------|
| `tentative` | 作为**参考**, 可以偏离, 偏离时要在 commit msg 说明 "drift from tentative rule X because Y" |
| `ratified` | 作为**硬约束**, 违反必须 block 并提醒用户 |

**什么时候从 tentative → ratified** (严格):
- 对应代码**真的跑起来了** (Gate 1 + Gate 2 过了)
- 本项目真的从中受益 (不是因为论文这么说)
- 用户**显式确认**"可以 ratify 了"

**什么时候从 ratified → deprecated** (允许改口):
- 发现 ratified 规则和真实代码冲突, 选代码, 把规则 deprecated, 不强行把代码改来迁就规则

### 6.4 应用到当前文件

| 文件 | 当前应该的 status | 理由 |
|:-----|:----------------|:-----|
| `.cursor/rules/workspace.mdc` | **ratified** | 长期基建, 已验证 |
| `.cursor/rules/ar-foundation.mdc` | **ratified** | 只写已知坑, 都来自真实踩坑 |
| `.cursor/rules/livekit-unity-sdk.mdc` | **ratified** | 已踩坑总结 |
| `.cursor/skills/livekit-unity-video-publish/SKILL.md` | **ratified** | 基于 ARVideoPublisher.cs 真实代码写的 |
| `.cursor/memory/architecture/ar_feature_vision.md` | **tentative** (部分) | §3.1-3.4 ratified; §3.5 三层意识 + §3.6 两轴 = **tentative 直到 Sprint 1/2 跑完** |
| `.cursor/memory/architecture/ar_feature_implementation_plan.md` | **tentative** | 计划本身就是 tentative, Sprint 做完才会 ratify 对应段 |
| 本文档 `sprint0_preflight.md` | **tentative → ratified after Sprint 0** | 过完 Sprint 0 才知道这 checklist 对不对 |
| 未来的 `.cursor/rules/scheduler-three-layer.mdc` (Sprint 2 末写) | 写时 **tentative**, Sprint 2 验收过才 ratify | 按 §6 铁规矩 |
| 未来的 `.cursor/rules/soul-constraints.mdc` (Sprint 4 末写) | 同上 | 体感约束必须经过对话实测 |

### 6.5 Sprint 0 要做什么

| 任务 | 位置 | 产出 |
|:-----|:-----|:-----|
| **S0.L — 给现有 7 个文件加 `status:` frontmatter** | 每个 `.mdc` / 架构 `.md` | 按 §6.4 分类打标 |
| **S0.M — 在 `workspace.mdc` 加一节"规则两态机"** | `.cursor/rules/workspace.mdc` | §6.2 + §6.3 |
| **S0.N — `commit_guidelines.md` 补一条**: tentative 规则与代码冲突时选代码, 写 drift 说明 | `.cursor/memory/commit_guidelines.md` | 2 行 |

---

## 7. Sprint 0 最终任务单 (合并 S0.A 到 S0.N)

> 整合本文档的所有 S0.* + 原计划的基建修缮 + L1.5 protocol lock (之前和用户讨论过)。

### 7.1 原计划的 S0 任务 (来自 `ar_feature_implementation_plan.md`)

| # | 任务 | 位置 | 状态 |
|:--|:-----|:-----|:-----|
| S0.1 | requirements.md / config / Docker volumes 整理 | 已大部分就位 | ✅ done |
| S0.2 | commit_guidelines 强化 | 已就位 | ✅ done |
| S0.3 | ARVideoPublisher attach 确认 | 已就位 | ✅ done |
| S0.4 | Castle 4 commit push + docker up | **用户手动**, 不走 agent | ⬜ 用户 |
| S0.5 | FalkorDB 健康检查 + Graphiti 集成测试 | 脚本已有 | ⬜ 用户 |
| S0.6 | commit_guidelines 加一条回归基线 | §9 新增 | ✅ done (2026-04-22) |
| S0.7 | **🆕 L1.5 协议锁定** `src/parrot/dsg/l1_5_protocol.py` | 新文件 | ✅ done (2026-04-22) |

### 7.2 本文档追加的 S0 任务

| # | 任务 | 归属 | 状态 |
|:--|:-----|:----|:-----|
| S0.A | 锁 L0 Stream schema `shared/event_log.py` | §1.4 | ✅ done (b8bb0a9) |
| S0.B | 锁 L3 节点 provenance 字段 | §1.4 | ✅ done (2026-04-22) |
| S0.C | 时间轴 API 约定文档化 `timeline_api.md` | §1.4 | ✅ done (2026-04-22) |
| S0.D | `workspace.mdc` 加 Cursor 工作合约 | §2.3 | ✅ done (2026-04-22) |
| S0.E | Sprint 开工模板 `sprint_kickoff_template.md` | §2.3 | ✅ done (2026-04-22) |
| S0.F | ADR 目录和模板 `architecture/adr/` | §3.3 | ✅ done (2026-04-22) |
| S0.G | 补 3 个追溯 ADR (001/002/003) | §3.3 | ✅ done (2026-04-22) |
| S0.H | 三闸门验收规则 `test_gate_rules.md` | §4.4 | ✅ done (2026-04-22) |
| S0.I | plan 里每条用例标 Gate | §4.4 | ✅ done (2026-04-22) |
| S0.J | pyproject.toml 补 `pydantic` | §5.3 | ✅ done (b8bb0a9) |
| S0.K | Castle 依赖审计脚本 `infra/audit_deps.ps1` | §5.3 | ✅ done (2026-04-22) |
| S0.L | 7 个现有文件打 status tag | §6.5 | ✅ done (2026-04-22) |
| S0.M | workspace.mdc 加两态机 | §6.5 | ✅ done (2026-04-22) |
| S0.N | commit_guidelines 补 drift 说明条款 | §6.5 | ✅ done (2026-04-22) |
| S0.O | AR Foundation 5.1 蒸馏配置 | §5.2 | ✅ done (manifest.json 已锁 5.1.5, 技能 ratified) |
| S0.P | L2-B SemanticNode Pydantic 迁移 | §10.1 | ⏸ deferred → Sprint 4 |

### 7.3 总估时

- **原计划 S0.1-S0.7**: 1-2 天 (原估)
- **新增 S0.A-S0.O** (15 项): 大部分是**文档和配置改动**, 不写业务代码, 约 **1 天**
- **合计**: **2-3 天**, 比原来多 1 天, 但省掉后面 5-10 天的返工

---

## 8. 回答用户的 6 件担心 — 简短收尾

| # | 担心 | 回答 |
|:--|:----|:----|
| 1 | 时间轴记不好 | §1 四层模型已敲死, L0 Stream 是 single source of truth, 剩下都是投影。回放/审计/综合查询都可以 |
| 2 | Cursor 上下文不出错 | §2 5 条工作合约 + 硬红线, 每 Sprint 开新会话 + 读 plan + 先列改动范围再动手 |
| 3 | 联网查缺补漏 | §3 三条硬规则, 调研结论走 ADR, 不偷偷改 vision |
| 4 | 验收严不严 / Cursor 写 AR 行不行 | §4 三闸门 + 每类代码不同门槛; Cursor 在后端/C# 业务强, Shader/真机验证要人工 |
| 5 | 版本锁 | §5 已基本就位, 补 `[images]` `pydantic` 即可 |
| 6 | **防提前锁定** | §6 tentative/ratified 两态机, 给每个文档打 status tag, 没跑通的设计只是 tentative, agent 不盲从 |

---

## 9. 回引

- 四层时间轴 → Sprint 1 的 `obs_log` (S1.E) 和 Sprint 4 PhotoEvent (S4.C) 都在 L0 Stream 之上
- Cursor 工作合约 → Sprint 1 开工第一件事就是按这个跑
- ADR 追溯 → `ar_feature_vision.md` §3.5/§3.6 的设计要各自有一份 ADR 占位
- 三闸门验收 → Sprint 1 验收用例要按 Gate 1/2/3 重新标
- tentative / ratified → Sprint 1 开工前, 本文档和 `ar_feature_vision.md` §3.5/§3.6 都要带 status

---

## 10. 悬挂决策 (Deferred Decisions) — 不在 Sprint 0 做

> 登记"已讨论 + 暂不做"的设计决策, 防止遗忘。每条都带**解锁条件** (什么时候可以重新拾起)。
> 维护方式: 决策被拾起时从本节**下移到对应 Sprint 任务单**, 不直接删。

### 10.1 S0.P — L2-B SemanticNode 迁移 Pydantic v2 (tentative, deferred)

**讨论日期**: 2026-04-22 (S0.A 开工时顺带产生)

**问题**: `src/parrot/dsg/l2b_types.py::SemanticNode` 目前是 dataclass, 和 Graphiti `EntityNode` (BaseModel) 不同种族, archive 时靠 `graphiti_uuid` 字符串手工桥接。随 L2-A (ConceptGraph / SSG 学习, P3) 和 L2-B archive filter (未设计) 推进, 类型一致性可能有价值。

**为什么现在不做**:
1. L2-B 是运行时热路径 (`touch()` / `attention +=` 每 tick 调), Pydantic `validate_assignment` 有开销; 关掉又拿不到 Pydantic 的好处
2. L2-B 已 IMPLEMENTED + 有集成测试, 改字段签名 = 13+ 调用点全回归
3. **关键**: **archive filter + 对话混合层还没设计** (用户 2026-04-22 原话: "存档有一层过滤器和与对话混合，记录数据目前还没设计好")。此时锁 schema = 典型的 §6 提前锁定陷阱
4. Graphiti EntityNode 只有 7 个持久字段, SemanticNode 有 15+ 个运行时字段 (attention/novelty/habituation/_rx_index 等), 硬套一个 BaseModel 会污染持久 schema 或被迫拆两层

**解锁条件** (满足后可迁移):
- (a) L2-B archive filter 设计 ratified (预计 Sprint 4 PhotoEvent 开工时一起做)
- (b) 明确 persistent-facing 字段 vs runtime-only 字段的边界
- (c) 检索端 Obsidian 强化方案落地, 知道 SemanticNode 要不要暴露给检索层

**预计**: Sprint 4 S4.A5 (`SemanticNode` 扩 `reference_image_path`) 是最早的切入点, 可以把"加字段"和"迁 Pydantic"合并一次做。

**临时方案**: S0.A 建 `EventEnvelope` 用 Pydantic v2, 建立**持久/协议层用 Pydantic** 的样例; SemanticNode 保留 dataclass; 桥接转换 (`to_graphiti_entity()`) 等 Sprint 4 写。

### 10.2 (未来条目占位)

按 Sprint 推进逐条追加。
