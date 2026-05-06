---
status: ratified
category: chat-dispatch-plan
status_note: "Phase 4 后续 chat 派发计划：DSG 升级（ConceptGraph 蒸馏 / L1.5 池设计）+ 协议升级与接口提炼 ADR fork chat + 接口提炼实施 chat + 独立审计 chat + Sprint 4 总结报告 chat。每条记录范围 / 启动 prompt 入口 / 依赖 / 何时启动。"
last_reviewed: 2026-05-04
ai_priority: high
ai_audience: "用户（决定派发顺序）+ 任何后续 chat（看自己处于路径哪一节）"
parent_doc: "sprint4_phase4_completion_and_final_audit_20260430.md"
---

# Phase 4 后续 Chat 派发计划

> **本文用途**：Phase 4 主线（230/230 测试 + Echo 全链路 + Photo 全链路 + 联机 smoke #3/#4/#5 ✅ + 真机 #1/#2 显式 defer 到正式 App）收口后，**所有派出去的独立 chat 路径** 一图收口。
>
> **此 chat 范围已结束**：Sprint 4 主线收口 + 任务 1 / 2 启动包（A/B/C/D + 本 D 文件）。下面的 chat **不在此 chat 实施**。

---

## §0 状态全景

```
[Sprint 4 Phase 4 主 chat]
        │
        ├─ ✅ A — DSG 1.5 A10 + L2-A skill seeker spec
        │       (dsg_skill_seeker_l1_5_a10_l2a_20260504.md)
        │
        ├─ ✅ B — Source 字段 + factory hook + ADR + 11 测试
        │       (adr_l1_5_source_dispatch_extension_space_20260504.md)
        │
        ├─ ✅ C — Fork chat 启动 prompt（任务 2 入场）
        │       (sprint4_phase4_protocol_and_interface_adr_fork_chat_prompt_20260504.md)
        │
        └─ ✅ D — 本派发计划
                ↓
        ┌──────┴──────────┬─────────────────────┐
        ↓                  ↓                     ↓
[Chat 1 ConceptGraph蒸馏] [Chat 2 L1.5池设计]  [Chat 3 协议+接口ADR fork]
   独立 workspace          独立 chat             同仓 fork
   用户派出 (A 入场)         用户做 (任务 1.4)     用户派出 (C 入场)
        ↓                  ↓                     ↓
        └──────────┬──────┘                     ↓
                   ↓                  ┌────────┴────────┐
            (蒸馏 + 池设计完成)         ↓                 ↓
                                  [Chat 4 接口提炼实施] [Chat 5 独立审计]
                                  (派出 — T2-C prompt) (派出)
                                       ↓                 ↓
                                       └────────┬────────┘
                                                ↓
                                       [Chat 6 Sprint 4 总结]
                                       (协议升级报告 + 接口设计报告)
                                                ↓
                                       [Chat 7 P2.5 完成汇报]
                                       (Sprint 0-4 全收口 + 真机 spike 后)
```

---

## §1 Chat 派发清单（按依赖顺序）

### §1.1 任务 1 分支（DSG 升级）

#### Chat 1 — ConceptGraph 仓库蒸馏（任务 1.1）

| 字段 | 值 |
|:--|:--|
| 范围 | 把 ConceptGraph + open-vocab vision stack 蒸馏成 SKILL.md |
| 启动 prompt | `dsg_skill_seeker_l1_5_a10_l2a_20260504.md` §5 prompt 模板 |
| 工作区 | **独立 workspace**（用户派出，非本仓） |
| 依赖 | 无 |
| 输出 | `.cursor/skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md` |
| 何时启动 | 任意时候（与其他 chat 并行） |
| 完成判据 | SKILL.md 落地 + 覆盖蒸馏任务包 §4.1 全部章节 + §1.2 不做事项 0 违反 |

#### Chat 2 — L1.5 预加载 Node 池 + 状态生命周期设计（任务 1.4，**用户自己做**）

| 字段 | 值 |
|:--|:--|
| 范围 | 设计 L1.5 预加载 Node 池 + 状态生命周期（**A10 入口除外** — 那是 Chat 1 蒸馏的输入）+ L2-B 组织方式简单升级（保留复杂仿生设计空间）+ L1.5 ↔ L2 调研后审 + Obsidian / GOSLO 主动发现 / 已有 source 差异化 lifecycle |
| 启动 prompt | [`architecture/dsg/dsg_l1_5_pool_design_chat_launch_prompt_20260506.md`](dsg/dsg_l1_5_pool_design_chat_launch_prompt_20260506.md)（2026-05-06 新建）|
| 工作区 | 同仓 |
| 依赖 | Chat 1 完成（拿蒸馏的 SKILL.md 当输入）+ ADR-L1.5-001（已落）+ **DSG 工作区**（已落，2026-05-04 + 2026-05-06 增补）+ **LineB 完成**（2026-05-04 已落，DSG 不再被它阻塞） |
| **入场必读**（2026-05-06 更新）| 1. `architecture/dsg/workspace_index.md`<br/>2. `architecture/dsg/dsg_decisions_master.md` — 用户已决事项 SSOT，不再讨论 ratified 条目<br/>3. `architecture/dsg/dsg_current_state_distilled.md`（含 §11 防爆炸门控分层 + §12 工作记忆延迟归档）<br/>4. **4 个 DSG skill** — 按 `dsg-rustworkx-master/SKILL.md §0` 路由表决定回读哪个 + `dsg-l2b-node-organization-options` 选项库 + `dsg-attention-schema-papers` 论文索引 + `dsg-l1-5-l2a-conceptgraph-distilled`（A10 占位）<br/>5. 按需 `opus_dsg_residual_intent.md` / `source_x_lifecycle_status.md` / `open_questions_for_design_chat.md` Q4.x 锁面核对<br/>6. 按需 `NewZone/distill_output/` 6 份 Gemini 蒸馏深读 |
| 输出 | 设计 doc（建议路径 `architecture/dsg/dsg_l1_5_pool_and_lifecycle_design_<date>.md`）+ 必要时新 ADR（触发 ADR-L1.5-001 §4.1 升级条件 / 或回审 master `provisional-revisit-after-L2-design` 条目时 supersede）|
| 何时启动 | Chat 1 完成 + DSG 工作区 sign off 后（用户已 sign off 2026-05-06 增补） |
| 完成判据 | 设计 doc + 必要时 ADR 修订 / supersede + 回审 master §8 触发条件 + 开放问题 Q1-Q4 逐条回答 |

---

### §1.2 任务 2 分支（协议升级 + 接口提炼）

#### Chat 3 — 协议升级 + 接口提炼 ADR fork chat（任务 2）

| 字段 | 值 |
|:--|:--|
| 范围 | 协议升级总结 ADR + 接口提炼要求归纳 ADR + 接口提炼实施 chat 启动 prompt |
| 启动 prompt | `sprint4_phase4_protocol_and_interface_adr_fork_chat_prompt_20260504.md` 全文 |
| 工作区 | **同仓 fork**（fork from 本主 chat） |
| 依赖 | 无（基于 Phase 4 完成态 + ADR-L1.5-001） |
| 输出 | 3 个文件：`adr_protocol_upgrade_summary_phase4_<date>.md` + `adr_interface_refinement_requirements_<date>.md` + `interface_refinement_chat_launch_prompt_<date>.md` |
| 何时启动 | 任意时候（与 Chat 1 / 2 并行） |
| 完成判据 | 3 文件落地 + Chat 4 / 5 / 6 启动 prompt 已就绪 |

#### Chat 4 — 接口提炼实施

| 字段 | 值 |
|:--|:--|
| 范围 | 实施 Chat 3 T2-B 的接口设计 + 重构（不限于：模块拆分 / API 公开面定义 / wire schema 演进策略） |
| 启动 prompt | ⭐ `chat4_interface_refinement_launch_prompt_20260507.md`（2026-05-07 落地 — 简单版，不预设计划，启动后先和用户讨论 §3 七问）+ 旧嵌入式指引保留在 `adr_protocol_upgrade_and_interface_refinement_background_20260504.md §7` 作背景 |
| 工作区 | 同仓 |
| 依赖 | Chat 3 完成 + DSG Chat 2 完成（2026-05-06）+ GOSLO 模块化完成（2026-05-06）+ 跨 chat 待办登记表（`cross_chat_pending_registry_20260507.md`） |
| 输出 | 代码改动 + 接口设计 doc + 测试（具体形态由启动后 §3 Q7 与用户讨论决定） |
| 何时启动 | Chat 3 完成 + 用户 sign off ADR 后（**当前已就绪**：408/408 pytest + 三大 chat 收口 + 登记表 + 启动 prompt 全部齐全） |
| 完成判据 | pytest 全绿 + 接口面 doc 已落 + 与 Chat 3 ADR 0 漂移 + 跨 chat 登记表 NEED-P2.5-* 处理 / defer 路径明确 |

#### Chat 5 — 独立审计

| 字段 | 值 |
|:--|:--|
| 范围 | cold-read 接口提炼成果 + 跨语言守护扩展（如 cs_parity 风格的接口面 freeze test） |
| 启动 prompt | Chat 3 在 T2-A 末尾给的"独立审计 chat 启动指引"（占位 — Chat 3 实际写） |
| 工作区 | 同仓 |
| 依赖 | Chat 4 完成 |
| 输出 | 独立审计 doc + 0~N 个 finding（沿 Brain 自审范式 13 项格式） |
| 何时启动 | Chat 4 完成后 |
| 完成判据 | 审计 doc 落地 + 高严重度 finding 全部修复 / reject + 测试基线不破 |

---

### §1.3 收口分支

#### Chat 6 — Sprint 4 总结报告（协议升级报告 + 接口设计报告）

| 字段 | 值 |
|:--|:--|
| 范围 | Sprint 4 完整闭环报告 = **协议升级报告**（基于 T2-A）+ **接口设计报告**（基于 T2-B + Chat 4 实施 + Chat 5 审计） |
| 启动 prompt | Chat 3 在 T2-A 给"总结报告骨架"占位（Chat 6 自己填）|
| 工作区 | 同仓 |
| 依赖 | Chat 4 + Chat 5 完成 |
| 输出 | 2 份独立 doc：`sprint4_protocol_upgrade_report_<date>.md` + `sprint4_interface_design_report_<date>.md` |
| 何时启动 | Chat 5 完成后 |
| 完成判据 | 2 报告落地 + Sprint 4 完整收口 / Sprint 5 入场前置就绪 |

#### Chat 7 — P2.5 完成汇报

| 字段 | 值 |
|:--|:--|
| 范围 | Sprint 0-4 + 真机 spike 全收口汇报 |
| 启动 prompt | （等真机 spike 完成后再写） |
| 工作区 | 同仓 |
| 依赖 | **真机 spike 完成**（首版正式 App 集成测试，包含 perch_to_finger + identify_object 验收 #1/#2，per smoke 完成报告 §8） |
| 输出 | `p2_5_completion_report_<date>.md` |
| 何时启动 | 真机 spike 跑通 Sprint 4 全部 5 验收口径后 |

---

## §2 与已派出 / 已搁置 chat 的边界

| 之前提到过但本计划**不重启** | 状态 |
|:--|:--|
| 联机 smoke chat | ✅ 已完成（`sprint4_phase4_online_smoke_completion_20260504.md`）|
| Unity W8 半边 chat | ✅ 已合并到联机 smoke chat 实施（PhotoController 等） |
| 30s 连接优化 | 推到 Phase 5+，等 TURN server 评估 chat 启动 |
| identify_object L2 完整化 (web_search / 同步 Nanobot) | Phase 5+；不在本计划范围 |
| ChatBot 降级模式 / Cat Maid 协作 | Phase 5+；接口提炼 chat 触及 surface，但具体 ChatBot 实施留 Phase 5+ |

---

## §3 推荐启动顺序（用户决策参考）

按"性价比 / 解锁度"排：

| 步 | 启动 chat | 理由 |
|:--|:--|:--|
| 1 | **Chat 3**（协议+接口 ADR fork）| 0 依赖；产出 Chat 4/5/6 的启动 prompt；不冲突任何并行 chat |
| 1' | **Chat 1**（ConceptGraph 蒸馏）— 与 1 并行 | 0 依赖；独立 workspace；蒸馏可能要几小时（仓库大），早派早完成 |
| 2 | **Chat 2**（L1.5 池设计）— 用户自己做 | 等 Chat 1 完成 |
| 3 | **Chat 4**（接口提炼实施） | 等 Chat 3 完成 + 用户 sign off ADR |
| 4 | **Chat 5**（独立审计） | 等 Chat 4 完成 |
| 5 | **Chat 6**（Sprint 4 总结报告） | 等 Chat 5 完成 |
| 6 | **真机 spike** — 首版正式 App 集成测试（用户主导）| 等 Chat 4 完成 + AR 工作区准备好（白模 → formal 转换）|
| 7 | **Chat 7**（P2.5 完成汇报） | 等真机 spike 全 5 验收 ✅ |

**关键并行点**：Chat 1 + Chat 3 可同时开（独立 workspace + 同仓 fork 互不干扰）。

---

## §4 完成判据（整个 Phase 4 → 5 转换收口）

下列**全部** ✅ 时，Phase 4 → 5 转换正式完成，可进 Sprint 5：

- [ ] Chat 1 + Chat 2 完成 → DSG L1.5 升级有方向
- [ ] Chat 3 完成 → 协议 / 接口 ADR 锁
- [ ] Chat 4 完成 → 接口面落地
- [ ] Chat 5 完成 → 接口审计通过
- [ ] Chat 6 完成 → 2 份 Sprint 4 总结报告
- [ ] 真机 spike 完成 → 验收 #1/#2 ✅
- [ ] Chat 7 完成 → P2.5 汇报

---

## §5 引用

- Phase 4 主收口：`sprint4_phase4_completion_and_final_audit_20260430.md`
- 联机 smoke：`sprint4_phase4_online_smoke_completion_20260504.md`
- 上游 ADR：`adr_l1_5_source_dispatch_extension_space_20260504.md`
- ConceptGraph 蒸馏 spec：`dsg_skill_seeker_l1_5_a10_l2a_20260504.md`
- Fork chat prompt：`sprint4_phase4_protocol_and_interface_adr_fork_chat_prompt_20260504.md`
- Phase 4 §8 决策锁：`sprint4_phase4_entry_20260430.md §8`
