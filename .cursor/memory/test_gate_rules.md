---
status: tentative
status_note: "S0.H 产出的三闸门规则。Sprint 1 首次按本规则走完一次验收, 无明显漏洞再升 ratified。"
last_reviewed: 2026-04-22
---

# 三闸门验收规则 (Three-Gate Acceptance)

> 源: `sprint0_preflight.md §4`
> 适用: **每一个 Sprint / 每一个 S{N}.{letter} 子任务**
> 核心主张: 单一闸门 (跑一下就过) 不够严, **三闸门逐级**才能防止"编译过就合并"的假通过。

---

## 0. TL;DR

```
Gate 1 (单测)  →  Gate 2 (用例手验)  →  Gate 3 (回归)  →  Sprint 收尾打 tag
```

三闸门**全过**才能收 Sprint。任意一个失败回退到对应闸门修。

---

## 1. Gate 1 — 单元自测 (AI agent 负责)

### 1.1 必须产出

| 代码类型 | Gate 1 产出 |
|:--------|:-----------|
| Python 后端 | `pytest tests/<module>/ -v` **输出截图/粘贴**, 不是 "应该能跑" |
| Unity C# | Unity Editor 编译通过 + 无 `error CS*` |
| Shader / Rendering | 编译通过 + Editor 渲染截图 |
| Infra 脚本 | `--dry-run` 或 `--help` 能跑通 |
| 纯文档改动 | Markdown 渲染 + `ruff check` / `markdownlint` (如配) |

### 1.2 失败处理

- 报错 → agent 自己修, **不允许**直接进 Gate 2
- 没写单测 → Gate 1 直接 FAIL, 不论代码看起来多对

---

## 2. Gate 2 — 跑通用例 (用户手动 Play)

### 2.1 操作流

1. 用户按 `ar_feature_implementation_plan.md` Sprint N 的验收用例列表逐条跑
2. 每条用例 **≤10 分钟验完**, 超时说明用例设计太重 (写小一点)
3. 任一条失败 → 退回 agent, **不许跳过, 不许"下次再说"**
4. 用例都通过再进 Gate 3

### 2.2 每类代码的最低 Gate 2 门槛

| 代码类型 | Gate 2 |
|:--------|:-------|
| Blackboard / Scheduler BT | 手动 tick 跑日志, 肉眼确认状态迁移 |
| Unity C# 业务脚本 | **真实 Play / Stop / Play 3 次** (测 cleanup / rebind), 日志看到预期 RPC |
| Unity Rendering / Shader | Editor 截图对比 |
| AR Foundation (真机/模拟) | **XR Simulation Editor Play** + **Android/iOS 真机跑** (至少一个) |
| LiveKit SDK 调用 | Brain agent 日志显示订阅成功 / Track 发布成功 |
| Graphiti / L2-B 写入 | 查 Graphiti 能看到新节点 (`query_scene` 或直接 FalkorDB 查) |
| L0 Event Stream 写入 (Sprint 1+) | `redis-cli XRANGE parrot.events.log - + COUNT 10` 看到新条目 + schema 对 |

---

## 3. Gate 3 — 回归 (不破坏前 Sprint)

### 3.1 操作

1. 跑前一个 Sprint 的验收用例, **抽 1-2 条** (不用全跑, 快即可)
2. 优先抽"改动面大的 / 依赖本 Sprint 改动的"那几条
3. 失败 → 说明本 Sprint 改动有回归, **强制修复**, 不是"下个 Sprint 再说"

### 3.2 回归基线 (每个 Sprint 收尾时更新)

| 完成 Sprint | 必抽回归用例 |
|:-----------|:------------|
| Sprint 0 收 | 无 (基线) |
| Sprint 1 收 | Brain + sim_unity_client 语音往返 (P2 基线) + Gemini tool remember/query_memory |
| Sprint 2 收 | Sprint 1 的 vision/state 状态机切换 + Blackboard 订阅日志 |
| Sprint 3 收 | Sprint 1 全部 + Sprint 2 的 VideoTier 降档 |
| Sprint 4 收 | Sprint 3 AR 桌面 MVP + Gemini 能看到视频 |

---

## 4. 三闸门与"提前锁定"的关系

**没过 Gate 2 的设计 = 仍是 tentative**, 对应 `.mdc` / skill / 架构文档的 frontmatter 必须是 `status: tentative`。

**Gate 3 过了之后**才允许**把对应 tentative 文档升 ratified**, 见 `sprint0_preflight.md §6.3`。

换句话说: **三闸门通过 = tentative → ratified 的票据**。没有票据不准升。

---

## 5. 常见反模式 (严禁)

| # | 反模式 | 正确做法 |
|:--|:-------|:---------|
| 1 | "我跑过一次, 成功了" | 日志粘过来 + 截图 (Gate 1 产出) |
| 2 | "编译过了就算 Gate 1" | 编译 + 单测 + 执行输出 |
| 3 | "Gate 3 留到下个 Sprint 补" | 不允许, 未回归=未收 Sprint |
| 4 | "验收用例设计太严, 简化一下" | 可以, 但必须**新写**一条用例, 原用例不许删 |
| 5 | "reviewer 看一眼就行" | reviewer 只负责判断 Gate 1-3 是否过, 不代替 |

---

## 6. 关联

- `sprint0_preflight.md §4` — 规则源头
- `ar_feature_implementation_plan.md` — 每 Sprint 的验收用例 (S0.I 标 Gate 号)
- `commit_guidelines.md §5/§X` — 回归基线 + drift 说明 (S0.N)
