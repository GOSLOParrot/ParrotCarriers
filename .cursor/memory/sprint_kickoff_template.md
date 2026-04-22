---
status: ratified
status_note: "Sprint N 开工前填一份, 本模板本身稳定, 不随 Sprint 改。"
last_reviewed: 2026-04-22
---

# Sprint N 开工清单模板

> 源: `sprint0_preflight.md §2.3`
> 用法: 每个 Sprint 开工前 **拷一份** 到 `.cursor/memory/sprint{N}_kickoff.md`, 逐条打钩。
> 没打完不许动代码。

---

## 0. 基本信息

- **Sprint 编号**:
- **开工日期**:
- **计划收尾日期**:
- **主设计文档**:
- **主验收文档**: `ar_feature_implementation_plan.md §Sprint {N}`

---

## 1. 开工前 (Day 0) 必读清单

> 读完每一条打钩。读了但没看懂必须先问, 不许"读过了"糊过去。

- [ ] `.cursor/memory/active_context.md` 头部 (当前进度坐标)
- [ ] `sprint0_preflight.md` 全文 (六项收口 + 四层时间轴 + 三闸门 + 两态机)
- [ ] `ar_feature_vision.md §1-3.3` (硬事实边界 + tier/mode 两轴)
- [ ] `ar_feature_implementation_plan.md §Sprint {N}` 全部 (含验收用例)
- [ ] 上一个 Sprint 的 `sprint{N-1}_kickoff.md` (如有) 的**问题池** & 遗留
- [ ] 本 Sprint 涉及模块的**现有代码** (至少扫一遍, 哪些在哪)
- [ ] `timeline_api.md` (L0/L1/L2/L3 写入/投影规则)
- [ ] `test_gate_rules.md` (三闸门)

---

## 2. 问题收集 (Day 0 结束前)

> 列出开工前就看到的**疑问**, 用户回答或 agent 查证后再开工。

| # | 疑问 | 归属 (自己查 / 问用户 / 查 Opus 26) | 状态 |
|:--|:-----|:-----|:-----|
| 1 |  |  | open |

---

## 3. 本 Sprint 目标 (单句)

> 一句话写清这个 Sprint 产出什么, **够到 Gate 2** 才能收。

**目标**:

**不做什么** (反向约束, 防止 scope creep):
- 不做 A
- 不做 B

---

## 4. 任务分解 (S{N}.A / .B / ... )

| ID | 任务 | 类型 (code/doc/infra) | 三闸门预估 | ADR 预计 |
|:--|:-----|:-----|:-----|:-----|
| S{N}.A |  |  | G1 自测 + G2 用例 + G3 回归 |  |

---

## 5. 本 Sprint 会 ratified 的文档

> 开工前填: **Sprint 收尾**时这些 tentative 会升 ratified。没列在这的不升。

- [ ] `xxx.md` — 升 ratified 条件: {具体动作}

---

## 6. 风险 & 阻塞

| # | 风险 | 触发条件 | 应对 |
|:--|:-----|:--------|:-----|
| 1 |  |  |  |

---

## 7. 收尾动作 (Sprint 结束时填)

- [ ] 三闸门全过 (Gate 1/2/3 日志链)
- [ ] §5 列出的文档已升 ratified
- [ ] `active_context.md` 头部坐标前推 (用户手动)
- [ ] 回归基线追加到 `test_gate_rules.md §3.2`
- [ ] `sprint0_preflight.md §7.2` 对应 S0.* 打 ✅ (如在 Sprint 0 范围)
- [ ] 本 kickoff 文件底部留一段"问题池总结 + 下 Sprint 输入"
