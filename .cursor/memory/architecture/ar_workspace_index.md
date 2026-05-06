---
status: tentative
category: active
status_note: "AR 工作区聚合入口。把分散在 INDEX 不同节的 AR / LiveKit / Unity App 相关文档、skill、规则、ArSpike 仓位、调研产物归到一处。新增 AR 相关产物时，先在这里登记一行，再决定是否进 INDEX 主表。"
last_reviewed: 2026-04-29
---

# AR 工作区聚合入口

> 创建：2026-04-29（Sprint4 协议升级 Phase 1 完成 + 路由审计后）
> 用途：AR / LiveKit / Unity App / ArSpike 相关任务的**单一入口**。下次会话只要打算碰 AR 工作区，先读这一份再决定继续读什么。
> 边界：本文不复述具体决策；只做**路由 + 角色 + 入口模式**的聚合。深入内容请按链接进对应文件。

## 1. 仓位与角色边界

| 仓位 | 路径 | 当前角色 (2026-04-29) |
|:--|:--|:--|
| **ParrotDev**（测试床） | `unity/ParrotDev/` | Sprint 1–3 测试床；Sprint4 起**冻结**，仅作真机回归对照。新代码不进。 |
| **ArSpike**（接口工作区） | `unity/ArSpike/` | 正式 AR App **接口工作区 / 白模**。AR 基线探针 + ECP DTO 骨架。Phase 3 起的新代码主场。无美术资产。 |
| **GOSLOParrot**（带资产打包） | 暂未创建 | 未来正式 App 的资产 + 打包仓位。Phase 3/4 跑通后再决定何时奠基。 |

ArSpike 内部脚本治理规则：

- 入口：`unity/ArSpike/README.md` —— ArSpike 双角色说明 + AR Foundation 5.1.5 版本锁
- 迁移台账：`unity/ArSpike/Assets/Scripts/ParrotApp/MIGRATION.md` —— 当前迁移状态、依赖搬迁顺序、不搬迁清单、不允许误读

ParrotDev 与 ArSpike 同时存在期间，ECP 协议代码以 ArSpike 为准；ParrotDev 那份 `EcpDtos.cs` 仅作对照保留，不再同步。

## 2. 架构文档（按角色分组）

### 2.1 当前真源（实现 / 设计前先读）

| 文件 | 角色 |
|:--|:--|
| `architecture/ar_app_flow_ui_design.md` | **App Flow / UI / 功能入口当前真源**。HUD、工具柜、放大镜、注意力框、相机模式、纸条等设计基线 |
| `architecture/ar_feature_vision.md` | AR 互动愿景（自知 / 门控 / 两轴 / §3.5 三合一）。tentative，等 Sprint 1-2 代码落地后逐段升 ratified |
| `architecture/ar_feature_implementation_plan.md` | Sprint 0-4 任务清单 + 依赖图（每 Sprint 完成后该段升 ratified） |

### 2.2 Sprint4 协议三件套 + 审计（Phase 2/3/4 入场必读）

| 文件 | 角色 |
|:--|:--|
| `architecture/sprint4_pre_entry_prompt_and_plan.md` | Sprint4 前置入口：测试束隔离、能力提炼、最高效执行顺序 |
| `architecture/sprint4_protocol_ecp_background_20260429.md` | 协议背景锚点：用户原话、RIT/BT/BT 森林边界、DSG/Graphiti/Obsidian/Ref 边界 |
| `architecture/sprint4_protocol_v2_ecp.md` | Protocol V2 / ECP 正式设计稿：最小合同、状态面、Snapshot/Sighting/RefBinding、Lifecycle/Audio |
| `architecture/sprint4_ecp_minimal_audit_20260429.md` | **Phase 1 审计护栏**：A1-A5 修复 / B1-B5 推迟 + DRIFT NOTE / Phase 2 入场清单 / "不允许误读" |

### 2.2b Phase 4 完成 + Phase 5 转换前置（2026-05-04 新增）

| 文件 | 角色 |
|:--|:--|
| `architecture/sprint4_phase4_completion_and_final_audit_20260430.md` | **Phase 4 完成报告 + 终一致性审计** — 234/234 pytest + Echo/Photo 全链路 + §8 决策锁 13 条 0 漂移。**所有下游 chat 入场必读** |
| `architecture/sprint4_phase4_online_smoke_completion_20260504.md` | **联机 smoke 收口** — smoke #3/#4/#5 ✅；#1/#2 显式 defer 到真机集成测试 |
| `architecture/sprint4_phase4_downstream_chat_dispatch_plan_20260504.md` | **全下游 chat 派发地图** — Step 1-7 顺序 + 各 chat 角色 / 输入 / 输出边界 |
| `architecture/adr_protocol_upgrade_and_interface_refinement_background_20260504.md` | **ADR-PROTOCOL-INTERFACE-001**（fork chat 产出）— Sprint4 协议升级总结 + 接口提炼任务输入。下游接口提炼 chat 必读；不修改 Phase 4 锁定值 |
| `architecture/adr_l1_5_source_dispatch_extension_space_20260504.md` | **ADR-L1.5-SOURCE-DISPATCH-001** — Q1 SemanticNode.source 字段边界 + Q2 Meta dict/factory hook 扩展空间 + Q3 chat 路径锁。**任何动 dsg/ 的 chat 必读** |
| `architecture/sprint4_deferred_issues_and_bugs_20260504.md` | Phase 4 遗留问题 + pre-existing breakage 汇总（独立审计 chat 处理）|
| `architecture/dsg_skill_seeker_l1_5_a10_l2a_20260504.md` | ConceptGraph 蒸馏任务包（派出独立 workspace，Chat 1）|
### 2.3 视频 / 数据流前置调研

| 文件 | 角色 |
|:--|:--|
| `architecture/sprint4_livekit_stability_and_video_strategy.md` | LiveKit Bus 稳定性、视频上限、门控策略前置稿（Phase 3 调研入口之一） |
| `architecture/audit_identify_object_no_screenshot_20260420.md` | identify_object 视频采样审计 → captureSnapshot / SnapshotEvent 改造起点 |
| `docs/sprint4_research/result/INDEX_for_phase3.md` | **Phase 3 决策索引（薄）**（2026-04-29）：18 条已采用 / 8 条 spike / 11 条弃用 + 启动提示词。**Phase 3 实现 chat 起步页**，导向决策不导向原因 |
| `docs/sprint4_research/result/05_lifecycle_and_defensive_design.md` | **Phase 3 前置 lifecycle / 防御性机制汇总（厚）**（2026-04-29）：Phase A 联网广搜 + Phase B 接口验证 + 三段式（采用 / spike / 弃用）+ 候选 BB 键。**已筛选并合入 IMPL_REF**，本文档保留作决策依据回查 |
| `docs/sprint4_research/result/01_WebRTC_Lifecycle_and_Video_Strategy.md` (含 2026-04-29 补遗) | 先前 task1 总策略 + 本轮补遗（SDK 事件不可靠 / SetParameters 不可用 / ARCore 后台 blank / 截帧两条干净路径） |

### 2.4 早期参考（仅作问卷追溯）

| 文件 | 角色 |
|:--|:--|
| `architecture/ar_app_plan.md` | 早期 AR 工程计划 + C1-C12 进度 + 五维问卷追溯。**不再驱动当前 UI**，被 `ar_app_flow_ui_design.md` 取代 |
| `architecture/ar_camera_interaction_survey.md` | AR 摄影互动问卷（已回填，不再改） |
| `architecture/ar_skill_seekers_distillation_report.md` | AR Foundation 5.1 蒸馏报告（一次性产物） |

## 3. 规则（自动加载或按 glob 加载）

| 规则 | 加载条件 | 角色 |
|:--|:--|:--|
| `.cursor/rules/workspace.mdc` | alwaysApply | 全局路由（含本工作区入口） |
| `.cursor/rules/ar-foundation.mdc` | 自动 / AR 相关任务 | AR Foundation 5.1.x 版本锁 + 9 条已知坑 |
| `.cursor/rules/livekit-unity-sdk.mdc` | `unity/**/*.cs` glob | LiveKit Unity SDK 适配规则（含 2026-04-26 真机踩坑） |
| `.cursor/rules/bus-audit-constraints.mdc` | 审计任务 | Bus / 协议审计护栏 |

## 4. Skills（按需显式调用 / glob 自动）

### 4.1 AR Foundation

| Skill | 角色 |
|:--|:--|
| `.cursor/skills/ar-foundation-api/SKILL.md` | AR Foundation 5.1.x 完整 API 参考（Packages.md） |
| `.cursor/skills/ar-foundation-samples/SKILL.md` | 官方 Samples 实现模式（帧抓取、平面、面部、Anchor） |

### 4.2 LiveKit Unity

| Skill | 角色 |
|:--|:--|
| `.cursor/skills/client-sdk-unity/SKILL.md` | LiveKit Unity SDK 能力面（Room / Track / RPC / DataChannel） |
| `.cursor/skills/livekit-unity-video-publish/SKILL.md` + `IMPL_REF.md` | **数据流主题** — 推流 / 多处采样 / 截帧（XRCpuImage / AsyncGPUReadback）/ 黑帧门 / VideoTier 切换路径 / 15 条踩坑表（2026-04-29 Patch 1/2/5/6/8/10 已合入） |
| `.cursor/skills/livekit-unity-lifecycle/SKILL.md` + `IMPL_REF.md` | **lifecycle / 防御性主题** — AppLifecycleState 11 状态 FSM / Graceful shutdown chokepoint / Connectivity watchdog / ConnectionHealthState 聚合 / ARCore 后台 blank / setVideoTier 副作用 / AudioRoutePolicy baseline / 17 个可调参数表（2026-04-29 创建，承载 Patch 3/4/7/9） |
| `.cursor/skills/bus-deploy-livekit-ecs/SKILL.md` | 阿里云 ECS 上 LiveKit Bus 部署与稳定性策略 |

### 4.3 Phase 3 调研后 skill 拆分决策（2026-04-29 已落地）

调研 chat（2026-04-29）产出落地路径：

| 产物 | 落地位置 | 状态 |
|:--|:--|:--|
| 调研厚稿（决策依据） | `docs/sprint4_research/result/05_lifecycle_and_defensive_design.md` | 已生成 |
| 调研薄索引（导向决策） | `docs/sprint4_research/result/INDEX_for_phase3.md` | 已生成 |
| `result/01` 补遗（与 task1 总策略偏差） | `docs/sprint4_research/result/01_WebRTC_Lifecycle_and_Video_Strategy.md` 末尾 | 已合入 |
| Patch 1/2/5/6/8/10（数据流主题） | `.cursor/skills/livekit-unity-video-publish/IMPL_REF.md` | 已合入 |
| Patch 3/4/7/9（lifecycle / 防御性主题） | `.cursor/skills/livekit-unity-lifecycle/IMPL_REF.md` | 已合入（新建） |

**拆分决策（Agent 可读性优先）**：
- 保留 `livekit-unity-video-publish/` 名字不改（避免破坏现有 rule / 路由引用），更新 description 让 Agent 召回时聚焦数据流主题；
- 新建 `livekit-unity-lifecycle/` 独立 skill，单主题 description（lifecycle / 防御性 / 重连 / shutdown / health / 后台 blank / VideoTier 副作用）召回更准；
- 两份 IMPL_REF 顶部互相 link 回，遇到冲突各自负责自己的真源主题。

## 5. ArSpike 工作区文件

| 文件 | 角色 |
|:--|:--|
| `unity/ArSpike/README.md` | ArSpike 双角色 + AR Foundation 5.1.5 版本锁 + xr.management 不钉的理由 |
| `unity/ArSpike/Assets/Scripts/ParrotApp/MIGRATION.md` | 当前迁移状态 + 依赖搬迁顺序 + 不搬迁清单 + 不允许误读 |
| `unity/ArSpike/Assets/Scripts/ParrotApp/RPC/EcpDtos.cs` | Sprint4 ECP-minimal 已迁移 |

## 6. 外部调研产物（非事实源，按需 @ 引用）

| 文件 | 用途 |
|:--|:--|
| `docs/sprint4_research/result/01_WebRTC_Lifecycle_and_Video_Strategy.md` | LiveKit/WebRTC lifecycle + 视频策略调研 |
| `docs/sprint4_research/result/02_LLM_Control_Protocol_and_State_Machine.md` | LLM 控制协议 / 状态机调研 |
| `docs/sprint4_research/result/03_App_Flow_and_UI_Layout_Design.md` | App Flow / UI 调研（已被 `ar_app_flow_ui_design.md` 内化） |
| `docs/sprint4_research/result/04_DSG_Graphiti_Memory_and_Subconscious_Design.md` | DSG / Graphiti / 潜意识设计调研 |
| `docs/test/p2_5/sprint3_effective_lessons_for_sprint4_zh.md` | Sprint3 真机 smoke 有效经验提炼 |

## 7. 入口模式（按你下一步要做什么读哪几份）

### 7.1 实现模式（要写代码 / 修代码）

```
INDEX.md §〇 必读 7 份  →  本文件 §1-2 (确定仓位 + 真源)
                      →  对应 skill (§4)
                      →  对应规则 (§3)
                      →  ArSpike MIGRATION.md (§5) 确认迁移状态
                      →  动手
```

### 7.2 调研模式（要新写一份 skill / 设计稿）

```
本文件 §2.4 早期参考（看历史结论）
+ 本文件 §6 外部调研产物（看现成材料）
+ 本文件 §4 现有 skill（看已蒸馏的能力面）
→ 输出新文档到对应位置（架构 / skill / IMPL_REF）
→ 回填本文件相应小节登记一行
```

### 7.3 审计模式（要给某次落地做对照）

```
sprint4_ecp_minimal_audit_20260429.md (审计模板)
+ 实际代码 + 设计稿 (对照)
→ 输出新审计文件到 architecture/<topic>_audit_<date>.md
→ 在 INDEX §1.1 active 登记 + 本文件 §2.2 登记
```

## 8. 不允许误读

1. **本文不是真源**。它是路由 / 入口聚合。具体决策、设计、踩坑都在被指向的文件里；本文出现"决策"字样属于错误，应回到对应文件查核。
2. **本文与 INDEX.md 的关系**：INDEX.md 是项目唯一真相源（含 Bus / Brain / Scheduler / DSG / Memory 全部模块）；本文只覆盖 AR / LiveKit / Unity App / ArSpike 的子集，不替代 INDEX。AR 任务可以从本文进；非 AR 任务进 INDEX。
3. **新增 AR 相关产物时**，先在本文对应小节登记一行；如该产物影响 §〇 必读级别，再去 INDEX §〇 加。多数情况只需要登记到本文。
4. **路径写错就回退**。本文出现的所有路径必须能直接定位到文件；如果某个文件被移动 / 重命名，先修本文 + INDEX 再改用法，不要静默漂移。

## 9. 变更日志

- 2026-04-29: 创建。聚合 17 份 AR 工作区相关文档 + 4 个 AR/LiveKit skill + 3 条规则 + ArSpike 仓位。来源是路由审计修复（INDEX §1.1 active 登记）。
- 2026-04-29 (晚): Phase 3 调研产物落地登记。新增 `INDEX_for_phase3.md`（薄索引）+ 新建 `livekit-unity-lifecycle/` skill（IMPL_REF 承载 Patch 3/4/7/9 + 17 个可调参数表）+ `livekit-unity-video-publish/IMPL_REF.md` 合入 Patch 1/2/5/6/8/10。skill 拆分决策（不改名 + 新建独立 lifecycle skill）已写入 §4.3。
- 2026-05-04: Phase 4 完成 + Phase 5 转换期。新增 §2.2b，登记 7 份 5/4 新产出：Phase 4 完成报告 + 联机 smoke 收口 + 全下游 chat 派发地图 + ADR-PROTOCOL-INTERFACE-001（fork chat 产出）+ ADR-L1.5-SOURCE-DISPATCH-001（dsg/ 决策锁）+ 遗留问题汇总 + ConceptGraph 蒸馏任务包。INDEX.md §1.1 同步登记。
