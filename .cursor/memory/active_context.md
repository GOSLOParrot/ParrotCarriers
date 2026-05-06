# 当前进度与下一步

> ⚠ **2026-05-07 Pivot — 转向 App 实施**：Chat 4"接口提炼"任务 pivot；49 文件产出基本 reorganize 已有 doc，止损改向**直接推进 App 实施 + 代码编写**。接口在实施中自然浮现。
>
> **新 SSOT 双件**（替代接口提炼工作）：
> - 架构图 → [`architecture/module_map_p4_snapshot.md`](architecture/module_map_p4_snapshot.md) — 单一清晰最新模块架构 + 三条主路径 + 模块状态表
> - 协议全集 → [`protocol_snapshot_p4.md`](protocol_snapshot_p4.md) — Sprint 4 收口 + DSG Chat 2 + GOSLO mod 全协议 SSOT（§1-§28，含 13 EcpEventType / 26 BB keys / 8 enum / Phase 4 §8 13 锁等）
>
> **`.cursor/memory/interfaces/`**：保留 4 件高价值（methodology.md / upgrade_roadmap.md / change_impact_table.md / _sync/grep_verification_20260507.md）；其余 44 件已删（详 [`interfaces/README.md`](interfaces/README.md) §2）。
>
> **下一步**：直接进入 App 实施。upgrade_roadmap.md §1（Chat 4 4-A 实施轨 5 项）+ 既有 NEED-* 标签是 backlog；遇到具体接口问题就地修代码 + 同步 protocol_snapshot_p4。
>
> ---
>
> ⚠ **2026-05-04 重大更新**：Sprint 4 Phase 4 **整体收口完成** + 联机 smoke 通过 + Phase 5 入场转换包就绪。下面 §0 是当前权威入场点，旧 4/29 内容（§1+ 起）保留作历史。
>
> **2026-05-04 追加**：DSG 工作区已建立（`architecture/dsg/`），作为 DSG 系列设计 chat（L1.5 池 / lifecycle / L2-B 简单升级 / Phase 5+ A10 接入）的 SSOT 入场点，与 AR 工作区（`ar_workspace_index.md`）对位。Chat 2 启动前先读 `architecture/dsg/workspace_index.md` + `dsg_current_state_distilled.md`。
>
> **🟢 2026-05-06 重大更新**：**DSG Chat 2（L1.5 Pool + Lifecycle + IntentWorkspace + Plan）实施完成** — 8 份设计/协议文档 + 14 新模块 + 5 改动既有 + 118 新测试 → **352/352 pytest 全绿**；Phase 4 § 8 + cs_parity 4/4 + ADR-L1.5-001 11/11 三大守护通过；ADR-L1.5-001 §4.1 三触发器全部未触发（继续 meta+factory hybrid）；master 11 条 `provisional-revisit-after-L2-design` 全部回审完毕。详见 [`architecture/dsg/dsg_l1_5_implementation_completion_20260506.md`](architecture/dsg/dsg_l1_5_implementation_completion_20260506.md)。
>
> **🟢 2026-05-06 重大更新**：**GOSLO 模型 + 行为树模块化任务实施完成** — `parrot.shared.model_manifest` Pydantic + Unity 三层（IParrotController / ModelDriver / ParrotRegistry / GosloLegacyController shim）+ Brain `animate` / `fly_to` 加 `model_id` 透传 + AI CLI `asset_to_manifest.py` MVP + 23/6/23/5 新测试 → **415/415 pytest** + Phase 4 § 8 wire 0 漂移；Step 6（LLM persona 参数化）确认推下游与 p3 菜单画布 4 类块同设计。详见 [`architecture/goslo_modularization_completion_20260506.md`](architecture/goslo_modularization_completion_20260506.md) + [`architecture/goslo_modularization_residual_debt_20260506.md`](architecture/goslo_modularization_residual_debt_20260506.md) + [`architecture/goslo_model_manifest_protocol_v1.md`](architecture/goslo_model_manifest_protocol_v1.md)。
>
> **🟢 2026-05-07 跨 chat 统一标注 pass**：三大 chat（Sprint4 主线 / DSG Chat 2 / GOSLO 模块化）完成后的统一 TODO + NEED 标签登记表落地 → [`architecture/cross_chat_pending_registry_20260507.md`](architecture/cross_chat_pending_registry_20260507.md)。**16 文件 26 处源码标签 + 4 P2.5 NEED + 8 P3 NEED + 6 修复 chat 路径表**；408/408 pytest 全绿（DSG Chat 2 之后 GOSLO mod 之前）/ cs_parity 4/4 守护通过。下游：Chat 4（接口提炼实施，处理 NEED-P2.5-PLAN-INTEGRATION + NANOBOT-HEARTBEAT + ARCHIVE-LLM 等）/ DSG 协议升级 chat（NEED-P2.5-A persona 外置 + NEED-P3-B/C 4 类块 + 预设）/ AR menu chat（NEED-P3-D/E）/ P3 wire ADR chat（NEED-P3-A body_state 解锁 + Plan UI wire）/ P3 仿生升级 chat（fold / spreading / RefHealth）/ A10 接入 chat（multi-scene）。

---

## §0 当前阶段（2026-05-04 — Phase 4 → 5 转换期）

### §0.1 Phase 4 终态（authoritative）

**协议升级 + 4 工具 + 全链路数据流 全部落地**：

- entry §8 决策锁 13 条 0 漂移
- 234/234 pytest（含 ADR-L1.5-001 新增 11 项）
- Echo 全链路接通（Unity SO Echo → Brain handler → FocusBboxThreshold 读 BB）
- Photo 全链路（preview EcpEvent + HTTP 全量上传 + asset_uploaded 回程）
- 联机 smoke #3/#4/#5 ✅；#1/#2 显式 defer 到首版正式 App 真机集成测试
- ECS 部署 sanity（Castle Brain + LiveKit + token_mint:7888 + photo_upload_server:7889 全绿）

### §0.2 Phase 4 → 5 转换期 决策记录（**高优 AI 可读 — 必读**）

本节合并三组关键决策的"**当前选择 + 原因 + 后续升级路线**"，新 chat 看完不必回读旧 doc。

#### Q1 — `SemanticNode.source` 字段在哪一层？

| 维度 | 值 |
|:--|:--|
| **当前选择** | **Python only**（Brain 内部 dsg/l2b_types.py + dsg/ingest/runner.py），**不上 Unity wire** |
| **原因** | A10 入口是 Brain-side CV pipeline 不通过 Unity；EcpEventSource enum 已隐含 unity/brain/nanobot 来源标识；wire 加新字段会动 cs_parity 跨语言守护 → 协议合同变更 |
| **后续升级路线** | 当 Unity 端某新功能必须知道某 Node 的 ingest source 时（目前没有这种需求），考虑 BB key 投影一份 read-only summary；**不要**直接加 EcpEvent 字段 |
| **真源 doc** | `architecture/adr_l1_5_source_dispatch_extension_space_20260504.md` §2.1 |

#### Q2 — 怎么留扩展空间（不锁子类 axis）？

| 维度 | 值 |
|:--|:--|
| **当前选择** | **Meta dict + factory hook 混合** — `SemanticNode.source: str` + `SemanticNode.source_meta: dict[str, Any]` + `SemanticNode.from_observation()` classmethod + `_SOURCE_META_FACTORIES` 注册表（新 source 调 `register_source_meta_factory()`） |
| **原因** | 用户原话"具体的多样化 Node 状态和生命周期设计在 L2-B 完善过程中完成，效果未知"——立刻引入子类会锁错 axis（行为差异 vs 数据 shape 差异 vs 字段差异，未明）|
| **后续升级路线**（按触发条件）| ① 若 ≥3 字段稳定 → meta dict 升 typed Pydantic model ② 若 ≥2 source 行为多态（如 A10 自动 decay confidence vs user 不 decay）→ 升 SemanticNode 子类 ③ 若 isinstance 反复手写 → 升 typed dispatch |
| **真源 doc** | `architecture/adr_l1_5_source_dispatch_extension_space_20260504.md` §2.2 + §4.1 |
| **代码注释锚点** | `src/parrot/dsg/l2b_types.py` 顶部 "Source dispatch (Phase 4 → 5 transition)" 模块级注释 |

#### Q3 — 协议升级 + 接口提炼 ADR 在哪做？

| 维度 | 值 |
|:--|:--|
| **当前选择** | **4 chat 路径**：fork chat 只做 ADR + 要求归纳；接口提炼实施派独立 chat；独立审计派独立 chat；Sprint 4 总结报告派独立 chat |
| **原因** | 用户 5/4 原话"任务 2 是此 chat 的 fork chat 内完成足够多的协议升级和接口提炼的要求归纳和 ADR；然后我们开始 chat 接口提炼和独立审计"——4 阶段路径已锁；fork chat 不做实施避免上游 ADR 与下游设计互相污染 |
| **后续升级路线** | 任何阶段如果发现"ADR 不够 / 实施暴露设计漏洞"，回溯到对应 chat 修订；不允许在下游实施 chat 内擅自改 ADR（必须先回 fork chat 类似 chat 重写 ADR） |
| **真源 doc** | `architecture/adr_l1_5_source_dispatch_extension_space_20260504.md` §2.3 + `architecture/sprint4_phase4_downstream_chat_dispatch_plan_20260504.md` §1 |

### §0.3 Phase 4 → 5 转换期 派出文件清单

| 文件 | 用途 | 派出方向 |
|:--|:--|:--|
| `architecture/sprint4_phase4_completion_and_final_audit_20260430.md` | Phase 4 完成报告 + 终一致性审计 | 所有下游 chat 入场 |
| `architecture/sprint4_phase4_online_smoke_completion_20260504.md` | 联机 smoke 收口 + #1/#2 显式 defer 决策 | 真机 spike chat |
| `architecture/adr_l1_5_source_dispatch_extension_space_20260504.md` | Q1/Q2/Q3 决策锁 + L1.5 source 字段 ADR | 任何动 dsg/ 的 chat 必读 |
| `architecture/dsg_skill_seeker_l1_5_a10_l2a_20260504.md` | ConceptGraph 仓库蒸馏任务包 | 用户派出独立 workspace |
| `architecture/sprint4_phase4_protocol_and_interface_adr_fork_chat_prompt_20260504.md` | 任务 2 fork chat 启动 prompt | 用户 fork chat |
| `architecture/sprint4_phase4_downstream_chat_dispatch_plan_20260504.md` | 全下游 chat 派发地图（**这一份是路径全景**）| 用户决策派发顺序 |

### §0.4 任务 2 fork chat 产出（**fork chat 完成 2026-05-04**）

Fork chat 按用户更新口径（"我们就写一份给 AI 够看的"）合并 T2-A + T2-B 为单 ADR，T2-C 在 ADR §7 内嵌"派发提示"，不出独立 prompt 文件：

- **T2-A 协议升级总结 ADR + T2-B 接口提炼要求归纳 ADR（合并）**：
  `.cursor/memory/architecture/adr_protocol_upgrade_and_interface_refinement_background_20260504.md`
  ADR-PROTOCOL-INTERFACE-001 — 单文档收集 Sprint 4 协议升级"升了什么"+ Phase 4 锁定约束 + 遗留问题 + 接口提炼任务输入（用户 2 个 motivating examples 问题清单 + 现有"准接口文档" inventory + 8 候选分类维度 + 单/双份现状证据 + 5 项隐含需求清单）+ 与 §8 锁定值兼容性证明 + 下游 chat 派发提示。0 修改 Phase 4 锁定值；测试基线 234/234 不动。
- **T2-C 接口提炼 chat 启动 prompt**：
  **不创建独立文件**（fork prompt §0 / §2.2 #7 显式授权）。下游接口提炼 chat 入场清单已落 ADR §7.1（必读 / 该做 / 不该做 三栏）。

### §0.5 推荐启动顺序

参考 `architecture/sprint4_phase4_downstream_chat_dispatch_plan_20260504.md` §3：

```
Step 1（并行）: Chat 3 (协议+接口 ADR fork) + Chat 1 (ConceptGraph 蒸馏，独立 workspace)
Step 2: Chat 2 (用户做 L1.5 池设计) ← 等 Chat 1 完成
Step 3: Chat 4 (接口提炼实施) ← 等 Chat 3 完成 + 用户 sign off
Step 4: Chat 5 (独立审计) ← 等 Chat 4 完成
Step 5: Chat 6 (Sprint 4 总结：协议升级报告 + 接口设计报告) ← 等 Chat 5 完成
Step 6: 真机 spike (首版正式 App 集成测试，验收 #1/#2) ← 等 Chat 4 完成 + AR 工作区 ready
Step 7: Chat 7 (P2.5 完成汇报) ← 等真机 spike 全 5 验收 ✅
```

### §0.6 已完成 / 不重启的事项

| 项 | 状态 |
|:--|:--|
| Phase 4 W0-W8 + Echo + Photo | ✅ 落地 |
| 联机 smoke #3/#4/#5 | ✅ 通过 |
| ECS 部署 sanity | ✅ 通过 |
| Brain 自审 13 项 | ✅ 10 resolved + 3 reject |
| GAP-1 (EcpState ingest) | ✅ 已修（联机 smoke chat 内）|
| Unity W8 半边（PhotoController）| ✅ 已合并（联机 smoke chat 内）|
| W3 Animation Minecraft port | ✅ 已合并 |
| 真机 spike #1/#2 验收 | 🔒 显式 defer 到首版正式 App 集成测试 |

### §0.7 已知 pre-existing breakage（留给独立审计 chat 修）

- `tests/test_ecp_event/test_identify_object.py` 收集时 ImportError（`id_module._match_staged` 路径与 env gate 冲突）— 与 Phase 4 → 5 转换无关；独立审计 chat 修

### §0.8 下面是历史档（仅追溯用）

旧 4/29 内容从下方继续；当前阶段以 §0 为准。

---

> 最后更新: 2026-04-29 晚 (Sprint 4 协议升级 Phase 1 / ECP-minimal 已落地 + 审计回路完成；ArSpike 工作区已奠基 + ECP DTO 迁移；**Phase 3 前置调研已收口**，决策索引 + skill 拆分已落地；**Android 15+ 16KB 对齐补丁已合入** — LiveKit SDK pin → main HEAD `7d868ef` (FFI v0.12.53)，ARCore/ARFoundation/ARKit 5.1.5 → 5.2.2，Editor 2022.3.62f3 不动，C# 代码 0 处需改)
> **当前阶段**: **Sprint 4 协议升级 Phase 1 已完成 + Phase 3 前置调研已收口**
> - Phase 1 = ECP-minimal：Pydantic schema (`src/parrot/shared/ecp.py`) + `_rpc_bridge` mirror + Unity DTO/handler + 19 项 pytest 全绿
> - 审计回路完成（A1-A5 必修已全部修复，B1-B5 推迟 + DRIFT NOTE 已留档）
> - ArSpike 已成为正式 AR App 接口工作区；EcpDtos.cs 已迁入 `unity/ArSpike/Assets/Scripts/ParrotApp/RPC/`
> - **Phase 3 前置调研产物已落地**（2026-04-29 晚）：
>   - 厚稿：`docs/sprint4_research/result/05_lifecycle_and_defensive_design.md`（Phase A/B + 三段式）
>   - 薄索引（Phase 3 实现 chat 起步页）：`docs/sprint4_research/result/INDEX_for_phase3.md`
>   - skill 拆分：保留 `livekit-unity-video-publish/`（数据流主题）+ 新建 `livekit-unity-lifecycle/`（lifecycle / 防御性主题）；两份 IMPL_REF 已合入对应主题的 Patch
>   - `result/01` 末尾已合入 2026-04-29 补遗
> - **下一步**：fork 新 chat 进 Sprint 4 Phase 3 实现（按 `INDEX_for_phase3.md` §1/§2/§3 推进）。启动提示词已写在该索引 §6。
>
> **必读护栏（Phase 2/3/4 启动前）**: `.cursor/memory/architecture/sprint4_ecp_minimal_audit_20260429.md` §"不允许误读" + Phase 2 入场清单
> **AR 工作区聚合入口**: `.cursor/memory/architecture/ar_workspace_index.md`
> **Sprint4 协议三件套**:
> - `.cursor/memory/architecture/sprint4_pre_entry_prompt_and_plan.md` — 前置入口
> - `.cursor/memory/architecture/sprint4_protocol_ecp_background_20260429.md` — 背景锚点（用户原话 + RIT/BT/BT 森林边界）
> - `.cursor/memory/architecture/sprint4_protocol_v2_ecp.md` — 正式设计稿
>
> **Dev.unity 定位说明**: Dev.unity = Editor + 真机 **集成测试场景**，用来验证 Bus/Brain/LiveKit/AR Foundation 各层接缝。不是最终要上线的 AR App 场景；AR App 前端（Launcher.unity + AR 主场景）在 P2.5 测试完成后独立搭建。
> **ArSpike 定位说明**: `unity/ArSpike` = **仅 AR 栈**探针（AR Mobile Template，AF 5.1.5 与 `ParrotDev` 对齐），**不含** LiveKit/Brain；用于打包与真机默认平面/放置 demo，**不替代** Dev.unity 总线验收。详见 `unity/ArSpike/README.md`。
>
> **Sprint 4 前置警告 (2026-04-25)**: Sprint 3 的真机测试脚本、Launcher→Dev 临时流程、Runtime HUD、自检按钮、WebCam fallback、`FindObjectOfType` 自动补绑定、3 秒等待、自诊断日志等，只能作为 **P2.5 测试束 / 事故记录 / 设计输入**。它们**不得**被当作 Sprint 4 AR App 的启动流程、连接流程或产品架构原型。Sprint 4 开始前必须先完成“有效内容提炼 + 测试束隔离 + AR App 启动设计”，再允许从 Sprint 3 代码或技能中借鉴实现片段。
>
> **Sprint 3 完成报告 (ratified)**: `.cursor/memory/architecture/sprint3_completion_report_20260423.md` — 2026-04-26 真机联调确认连接/AR/RPC/视频/语音骨架跑通；剩余转 Sprint4 前置
> **Sprint 3 有效经验提炼**: `docs/test/p2_5/sprint3_effective_lessons_for_sprint4_zh.md` — 真正有效遗留问题、测试束噪声、Sprint4 输入
> **Sprint 4 前置入口**: `.cursor/memory/architecture/sprint4_pre_entry_prompt_and_plan.md` — 新 Chat 启动提示词 + 测试束隔离 + 有效能力提炼 + 最高效执行顺序
> **AR App Flow / UI 设计基线**: `.cursor/memory/architecture/ar_app_flow_ui_design.md` — 启动页、HUD/工具柜、2D 工作区、放大镜、注意力框、功能入口与开放问题
> **Sprint 3 开工提示词**: `.cursor/memory/architecture/sprint3_kickoff_prompt.md`
> **Sprint 2 完成报告 (ratified)**: `.cursor/memory/architecture/sprint2_completion_report_20260423.md`
>
> **最新 commit**: `3254d2b` — gitignore mint secrets + Resources config examples + TokenService fallback path fix
>
> ---
>
> ## 整体计划路径（一张图）
>
> ```
> 现在
>  │
>  ├─ [Sprint 3 测试] Dev.unity 真机验收 AC1-AC11；**补充** ArSpike AC12（仅 AR 基线，见下文）
>  │    目标: 确认 Token Mint / AR 平面 / GOSLO 放置 / 两轴模式 / Brain RPC / 音频轨 / 视频轨 / DataChannel 生命周期全通
>  │    工具: adb logcat + python src/scripts/tail_obs_log.py --stream both
>  │    状态: ✅ smoke 已通过；连接/AR/LiveKit/Gemini 骨架跑通；有效遗留已转 `sprint3_effective_lessons_for_sprint4_zh.md`；ArSpike 独立探针见 AC12
>  │
>  ├─ [Sprint 4 前置隔离] 测试束审计/提炼 + AR App 启动设计
>  │    前提: Sprint 3 真机测试完成或至少拿到足够日志证明多通道生命周期问题
>  │    目标: 把 Sprint3 中“可保留能力/踩坑经验/错误临时设计”分类，禁止把测试脚本当产品启动方案
>  │    输入: 架构与需求 + LiveKit 能力边界 + client-sdk-unity + AR/Foundation/游戏/机器人控制/AR app 启动流程调研
>  │    输出: Sprint4 启动警告、测试束隔离清单、可复用设计输入清单、AR App 启动/连接独立设计草案
>  │
>  ├─ [Sprint 4] 数据流部分继续推进，但必须带入 App 生命周期位置设计
>  │    内容: captureSnapshot + 相机模式补充通道 + identify_object Path1 + 便签 UI + 食指 perching
>  │    前提: Sprint 3 AC1-AC5 通过 + Sprint4 前置隔离完成
>  │    完成标志: P2.5 全部功能验收通过；数据流生命周期能放入未来 App 启动/连接/前后台/权限模型中解释
>  │
>  ├─ [P2.5 收口] 全量功能测试完成 → 写 P2.5 completion report
>  │    标志: Sprint 0-4 全部 ratified，identify_object 三路全通，相机模式完整
>  │
>  ├─ [AR 工作区搭建] 基于已验证的各层接缝，独立构建 AR App 前端
>  │    内容: Launcher.unity 正式场景 + AR 主场景 + UI 完善 + GOSLO.glb 真模型
>  │    参考: ar_app_flow_ui_design.md + ar_camera_interaction_survey.md；ar_app_plan.md 仅作早期问卷追溯
>  │    注意: 不重建后端！只是前端工程，所有 Brain/Bus/DSG 接口复用 Sprint 3-4 已验证的版本
>  │
>  └─ [各模块独立开发] AR 工作区稳定后，按模块边界拆分独立迭代
>       Brain Tools 扩展 → DSG 语义层深化 → Nanobot 任务调度 → Obsidian 双链 → 记忆蒸馏 …
>       （每个模块有独立的 skill/rule 文件，不再需要全局上下文对齐）
> ```
>
> ---
>
> **Sprint 4 核心目标**: captureSnapshot + 相机模式补充通道 + identify_object Path 1 (A10 CV) + 便签 UI + 食指 perching
>
> ### Sprint 4 开始前警告与准入条件 (2026-04-25)
>
> **用户原始意图**: P2.5 / Sprint 3 的真机工作只是为了测试 **数据流生命周期**（LiveKit 房间、音频轨、视频轨、RPC、DataChannel、前后台/断线/重连、Brain 是否在房），并非提前设计正式 AR App 的启动/连接方式。当前 App 启动流程尚未设计，不能因为测试束能跑就反向认定产品启动流程。
>
> **禁止事项**:
> 1. 禁止把 `Dev.unity`、`Launcher.unity -> Dev.unity` 临时跳转、Runtime HUD、自检按钮、IMGUI 面板、`unity_join_token.txt` 桌面路径、WebCam fallback、3 秒自检等待、`FindObjectOfType` 自动补绑定等视为 Sprint 4 / AR App 正式启动流程。
> 2. 禁止继续为了“测试方便”把产品生命周期逻辑塞进测试脚本，尤其禁止让 HUD / SelfTest / Diagnostics 决定连接、权限、发布器初始化顺序。
> 3. 禁止在 `.cursor/skills/livekit-unity-video-publish/SKILL.md` 或 `IMPL_REF.md` 中把当前测试束的临时代码写成 ratified 产品实现；该技能最终只能记录 LiveKit Unity SDK 能力边界、有效接缝、踩坑经验和可复用最小模式。
>
> **Sprint 4 前必须先完成的提炼工作**:
> 1. **理解前提**: 只基于架构/需求、LiveKit 能力边界、`client-sdk-unity`、AR Foundation 约束、已验证 Bus/Brain/DSG 协议来设计；不得从测试脚本反推产品流程。
> 2. **外部启动流程调研**: 在 Sprint 4 app 启动设计前，先调研并记录若干 AR/游戏/机器人控制/游戏 AI/AR 项目启动流程经验（例如 Pokémon GO 式权限与 AR 模式进入、移动游戏主菜单/加载/权限门、机器人控制 App 的连接/安全态/重连、AR 相机会话启动/暂停/恢复）。这些调研只用于筛选 Sprint3 踩坑是否对 App 设计有效，不用于照搬 UI。
> 3. **测试束审计**: 把 Sprint3 真机测试中暴露的问题分为四类：
>    - **可保留能力**: LiveKit 房间连接、Token Mint、音频轨发布、视频轨首帧与发布、RPC 注册/调用、DataChannel telemetry、断线/重连状态清理、日志对表。
>    - **有效踩坑**: 明文 HTTP 被 Unity 禁、Brain 未在房但 LiveKit ON、无视频仍可语音但必须有麦轨和订阅者、视频轨 publish 成功不等于有真实帧、发布器断线后状态污染、`setVideoTier` 未绑定 publisher、重复 RPC 注册。
>    - **错误临时设计**: Launcher/Dev 混合临时流程、测试按钮/HUD 过度介入、自动 fallback 与自动查找掩盖真实依赖、把测试路径写成产品路径。
>    - **应迁入测试留档**: Runtime HUD、自检按钮、DiagnosticsLog、SceneChannelAudit、测试矩阵、adb/logcat 对表、ECS 对表报告；这些只能进入 `Testing/Runtime`、`Testing/Editor` 或 `docs/test/p2_5/`。
> 4. **Sprint3 有效内容独立留档**: 在 Sprint4 设计前新增独立文件（建议 `docs/test/p2_5/sprint3_effective_lessons_for_sprint4_zh.md` 或 `.cursor/memory/architecture/sprint3_effective_lessons_for_sprint4.md`），只记录对 Sprint4 有用的能力、坑、设计约束；不把现有测试脚本作为架构蓝图。
> 5. **技能延后整理**: `.cursor/skills/livekit-unity-video-publish/IMPL_REF.md` 和 `SKILL.md` 的最终提炼不急于现在完成。等 Sprint4 app 启动/连接/视频生命周期设计明确后，再从 Sprint3 独立留档中筛选有效内容写回技能。
>
> **Sprint 4 的重新定义**:
> - Sprint4 仍然以 **数据流部分** 为主：captureSnapshot、相机模式补充通道、identify_object Path1、便签 UI、食指 perching 等。
> - 但 Sprint4 必须同时考虑这些数据流在未来 App 中的位置：权限门、启动门、连接门、AR 会话门、前后台、断线/重连、视频/音频轨启停、Brain 不在房时的降级 UI。
> - Sprint4 不是完整 AR App 深入开发；但它必须输出足够清晰的 App 生命周期设计边界，避免 P2.5 测试束继续污染正式 App。
>
> **Sprint 3 决策收口 (D1-D6)**:
>   D1: set_video_tier hold_seconds=300 (PARROT_OVERRIDE_HOLD_SECONDS 可配置)
>   D2: A10 heartbeat via Redis SETEX parrot:a10_heartbeat + asyncio task (src/parrot/a10/heartbeat.py)
>   D3: Token Mint Bearer secret, Unity 存 Resources/parrot_config.json（gitignored，见 parrot_config.json.example）
>   D4: 新增 TRACK_REBUILDING reason, 映射 PAUSED 跳过 Supervisor 降档计时
>   D5: Gemini 继续看纯摄像头画面, Sprint 4 再接合成帧
>   D6: GOSLO.glb 换上真模型 (Assets/Models/GOSLO.glb 29KB), AnimationDriver 用 Transform.Find() 查节点
>
> 部署快照: `.cursor/memory/deploy_snapshot_p2_20260412.md`
> **P2 里程碑**: `.cursor/memory/milestone_p2.md` (P2 已完成, 历史归档)
> 同步工具: `.cursor/memory/commit_guidelines.md` + `infra/sync-castle.ps1`
>
> **Sprint 3 验收用例 (2026-04-26 smoke 收口状态)**:
>   AC1 ✅ IQOO NEO9 → Launcher 权限弹窗 → 全部允许 → 就绪（smoke）
>   AC2 ✅ 点连接 → Token Mint 成功 → 房间连接 → "连接成功"（smoke）
>   AC3 ✅ AR 场景加载 → Brain onSceneReady → GOSLO 问候语播放（单问候修复后 smoke）
>   AC4 ✅/⚠️ AR Foundation/ARCore 基本链路到 `SessionTracking`；正式 AR App 场景与交互留 Sprint4/AR 工作区独立搭建
>   AC5 ✅ 视频主通道 fresh frames；Gemini 能描述画面；tier ack/升级策略转协议 V2
>   AC6 ⚠️ VIDEO_OFF / mute / DSG PASSIVE 不再作为 Sprint3 连接阻塞；作为 Sprint4 视频生命周期用例保留
>   AC7 ⚠️ 断网/前后台/重连策略转 Sprint4 WebRTC 生命周期设计；Sprint3 仅确认基本连接 smoke
>   AC8 ✅/⚠️ `setScene` / SceneProfile 骨架存在；上下文注入 API 漂移与协议 V2 转 Sprint4
>   AC9 ✅ 真机麦克风轨 baseline 可用；外放回声/蓝牙/输入路由转 Sprint4 音频入口设计
>   AC10 ✅ 真机视频轨具备 fresh frames；黑屏问题根因和修复见 `brain_connected_black_video_20260425.md`
>   AC11 ✅/⚠️ RPC RTT 约 129ms；DataChannel/手势消费侧作为 Sprint4/P2.5 扩展继续对表
>   AC12 ✅ `unity/ArSpike`：AF 5.1.5 + 包/锁与 `ParrotDev` 对齐（无 LiveKit/Brain）；`unity/ArSpike/README.md`。
>   AC12b ✅ Build Settings 将**活动平台**切至 **Android** 后 **Build And Run** 成功，真机可跑模板默认平面/放置 demo（与总线无关的 **AR 栈基线**）。

---

## 版本锁定表 (2026-04-20 已验证)

| 依赖 | pyproject.toml 约束 | Castle 已安装 | 说明 |
|:-----|:--------------------|:-------------|:-----|
| `livekit-agents[google]` | `>=1.5,<2.0` | 1.5.2 | 1.x 主版本内兼容 |
| `graphiti-core[falkordb,google-genai]` | `>=0.28,<0.29` | 0.28.2 | 紧锁 0.28.x，API 已验证 |
| `redis` | `>=7.1,<9.0` | **7.4.0** | **⚠️ 从 5.3.1 升级**，falkordb 1.6.0 要求 >=7.1 |
| `python-dotenv` | `>=1.0,<2.0` | 1.2.2 | — |
| `py-trees` | `>=2.4,<3.0` | 2.4.0 | — |
| `rustworkx` | `>=0.15,<1.0` | 0.17.1 | — |
| LiveKit Unity SDK | `#2a7c57d7bcad2305a75bc75218e8064ccd5d10bf` | 同上 | manifest.json 已锁 commit hash |

**Gemini 模型（.env 可覆盖，无需改代码）：**
```
GEMINI_LIVE_MODEL=gemini-2.5-flash-native-audio-preview-12-2025
GEMINI_LIVE_VOICE=Puck
GEMINI_RERANKER_MODEL=gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
```

---

## 历史阶段留档：Sprint 0 前置 → Sprint 1-3 真机 smoke (已收口, 仅作追溯)

> 以下章节是 Sprint 0–3 的实施留档与决策记录，**不代表当前阶段**。当前阶段以本文头部为准（Sprint 4 协议升级 Phase 1 已落地 / Phase 3 调研待启）。
> 完整 Sprint 报告归档见 `INDEX.md` §1.5 sprint_archive。

### 基础设施状态 (已验证, 无待办)
- Castle Brain Agent: 运行中 (tmux `brain`, worker `AW_Y3QgXUuvtFKD`)
- FalkorDB + Redis + LiveKit: 运行中
- GitHub master: `0d0a2ea`
- Unity 编译: 通过
- 麦克风 / 视频推流: **Unity + Brain + Gemini 三端已验通** (详见 `Test/p2/connectivity_report_p2.md`)

### 历史待办 (Sprint 4 统一处理, 不单独跑)
- ~~Gemini 听到声音~~ → 已验通
- ~~重新生成 token~~ → 已跑过, Token Mint 方案在 Sprint 3
- **[Sprint 4] identify_object 按需发现链路** → `audit_identify_object_no_screenshot_20260420.md` (S4.A-B 统一做)

### P2 实现状态 (2026-04-13)
**已完成 — Graphiti 记忆共享 (P2-Alpha):**
- FalkorDB 替代 Neo4j (Docker 容器, 512MB, 端口 6380)
- Graphiti 客户端单例 + FalkorDB driver + Gemini LLM/Embedder + 4 分区 (goslo/maid/scene/user)
- Brain 记忆工具: `remember` / `query_memory` / `query_scene` / `set_mode`
- 对话自动归档: Brain→goslo 分区, Nanobot→maid 分区

**已完成 — Scheduler 增强 (P2-Beta):**
- BehaviorMode 动态切换: Redis Pub/Sub → mode_watcher → session.update_instructions()
- Context Injector: 记忆注入 + 场景注入 + 主动通知 + 周期轮询

**已完成 — DSG 耦合层 (P2-Gamma):**
- DSG↔Graphiti 接口层 + ExpectationChecker + L1 模拟脚本 + Obsidian SSOT 同步 + Trigger Listener

**已完成 — P2.5 审计修复 + 增强 (Phase 5):**
- TriggerRunner 真正启动 + L2-B 预加载集成到 agent.py
- identify_object ↔ L2-B 双向接入 + 触发事件发射
- Nanobot result_channel 路由协议 + CH_TRIGGER_RESULTS 新通道
- CalendarTrigger 三层提醒 (digest/prep/imminent) + quiet hours + cooldown
- MessageNotificationTrigger (Gmail 重要消息) 新增
- episode_id 防冲突 + 自动归档 + Salience.ALERT + ConfirmationStatus.TENTATIVE
- Agent disconnect 时 TriggerRunner 清理

**待完成 (2026-04-20 核对):**
- [ ] **[P0] git push 4 个未推 commit** → 通过 GitHub Desktop (commit_guidelines §1)
- [ ] **[P0] Castle 拉取 + FalkorDB 首次拉起** → `sync-castle.ps1` 拉代码 + SSH 上 `docker compose up -d`
- [ ] **[P1] Graphiti 线上链路验证** → FalkorDB ping + `remember/query_memory/query_scene` 真实调用
- [ ] **[P1] 创建 Unity AR 项目 (ParrotAR)** 并把 `ARVideoPublisher` 端到端跑通到 Gemini Live
- [ ] **[P1] identify_object 按需发现链路首测** ⚠ 设计未落地 (缺截图+错派Nanobot), 见 `audit_identify_object_no_screenshot_20260420.md`; 需 B1-B2 视频采样基建先就绪
- [ ] **[P2] Google OAuth 真实联调** (CalendarTrigger/MessageTrigger)
- [ ] **[P2] 用户制作 fly/dance/idle 动画 (Minecraft 风格)**
- [ ] **[P2] 像素画小纸条** (lore/ideas.md P3 条目，可能提前到 P2 做 MVP)

> 详见: `.cursor/memory/milestone_p2.md`

### V1 部署基础 (2026-04-12 已验证)
- Castle (ECS) 部署成功: LiveKit Server, Redis, Brain Agent, Nanobot Worker, GOSLO Chat
- GOSLO 双身体上线: Live (Gemini 语音) + Chat (Telegram nanobot)
- Bus V1 全链路验证通过: 语音 + RPC + Nanobot 后台链路
- 信息共享: P2 已通过 Graphiti + FalkorDB 打通记忆互通

### 当前真实状态

**L2 层三条核心链路已真实跑通（有集成测试证明）：**

1. **Path A 挂载**: Brain Agent + Scheduler 通过阶段式 pipeline 挂载到 Bus（L1+L2）
2. **Path B 挂载**: Nanobot Consumer 作为 L2-only Worker 挂载到 Bus
3. **dispatch → consume → result**: Brain dispatch_task → Scheduler 路由 → Redis Stream → Nanobot 消费 → 结果发布

**L1 层 Brain Agent 端到端验证通过（2026-04-11 笔记本模拟）：**

4. **Console 模式**: Bus mount 全流水线 → Gemini Realtime API 连接 → READY
5. **Dev 模式**: Worker 注册 → Agent Dispatch API → Job 分配 → Bus mount 全链路 → Gemini 音频连接 → READY
6. **sim_unity_client**: 连接同一房间 → 收到 Agent 音频 track → RPC handlers 就绪（flyTo/animate）
7. **关键修复**: LiveKit SDK `with_ttl` 改用 `timedelta`；显式 dispatch 需要 `RoomAgentDispatch` 或 API

**Unity 客户端 C# 代码 + Editor 脚本就绪：**

8. **RoomManager**: LiveKit Room 连接 + 远端音频自动播放 + 单例
9. **ParrotRpcHandler**: 注册 flyTo / animate RPC → 转发给 ParrotController
10. **ParrotController**: 方块移动 + 颜色反馈（Phase 1 dev mode）
11. **UnityMainThread**: 线程调度器，LiveKit 回调 → Unity 主线程
12. **DevSceneSetup.cs**: Editor 菜单一键搭建 Dev 场景 (Parrot > Setup Dev Scene)

**Castle 部署配置已创建：**

13. **docker-compose.yml**: Redis 绑定 127.0.0.1
14. **env-castle.template**: Castle 环境变量模板
15. **deploy-castle.sh**: rsync + pip + docker compose + 健康检查

**GitHub 仓库已推送：**

16. **https://github.com/GOSLOParrot/ParrotCarriers** — 2 commits on master
17. **https://github.com/GOSLOParrot/nanobot** — Fork 自 HKUDS/nanobot，`parrot_bus.py` adapter **已完成且已验证**

### 验证矩阵进度

| # | 链路 | 状态 | 验证方式 |
|:--|:-----|:-----|:---------|
| V1 | Brain ↔ Unity (语音) | **✅ 笔记本模拟通过** | sim_unity_client 收到 Agent 音频 track |
| V2 | Brain → Unity (指令) | **RPC 就绪** | sim_unity_client flyTo/animate handlers 注册成功；待真实语音触发 |
| V3 | Brain → Scheduler → Nanobot | **✅ 已验证** | 集成测试 5/5 通过 (含 ParrotBusChannel) |
| V4 | 模块注册与心跳 | **✅ 已验证** | Console + Dev 模式日志确认 register + heartbeat |
| V5 | Nanobot → Bus (结果回写) | **✅ 已验证** | stub + ParrotBusChannel 双路径验证 |
| V6 | ParrotBusChannel 连通 | **✅ 已验证** | test_nanobot_channel.py 2/2 通过 |
| V7 | 猫娘微信 Bot | **✅ 已验证** | QR 登录成功 + gateway 双 channel 并行运行 + Gemini API 200 OK + 微信 sendmessage 200 OK |
| V8 | GOSLO 模式信号 | **已实现** | constants.py HASH_GOSLO_MODE + brain/agent.py mount→live, disconnect→chat |
| V9 | GOSLO Chat bot | **代码就绪** | goslo_config.json + ParrotSoul workspace + start_goslo_chat.py + mode hook；待 TELEGRAM_BOT_TOKEN 配置 |
| V10 | 双 bot 并行 | **部署脚本就绪** | deploy-castle.sh 支持 3 tmux session (brain + maid + goslo-chat)；待 Castle 上验证 |

### 已完成

- [x] 需求清单 v2 + 模块划分 + 目录结构
- [x] Bus 骨架代码（manifest/registry/heartbeat/mounting/processor_hook）
- [x] 审计通过 → ModuleManifest 精简 → mounting 重构
- [x] Brain Agent 入口 + Scheduler 服务 + Nanobot Consumer
- [x] dispatch_task Tool：Brain → Scheduler → Nanobot 完整链路
- [x] 集成测试 2/2 + 单元测试 5/5 + ruff lint 全通过
- [x] Brain Agent 接入 Gemini RealtimeModel（AgentServer + AgentSession）
- [x] ParrotAssistant(Agent) 人格 + function tools (fly_to, animate, dispatch_task)
- [x] RPC 桥接 (`_rpc_bridge.py`): Unity RPC 转发
- [x] docker-compose.dev.yml LiveKit Server + Redis 开发栈
- [x] Console 模式验证: Bus mount → Gemini 连接 → READY ✅
- [x] Dev 模式验证: Worker 注册 → 参与者触发 → 完整入房 → READY ✅
- [x] **Unity C# 客户端**: RoomManager + ParrotRpcHandler + ParrotController + UnityMainThread
- [x] **Token 生成脚本**: `src/scripts/generate_token.py`（已修复 timedelta + agent dispatch）
- [x] **Castle 部署配置**: docker-compose.yml + env-castle.template + deploy-castle.sh
- [x] **项目 README.md + Unity README.md**
- [x] **.gitignore 更新**: ParrotDev + ParrotAR 通配
- [x] **笔记本模拟验证**: sim_unity_client + Brain Agent 端到端 Gemini 语音 ✅
- [x] **DevSceneSetup.cs**: Unity Editor 一键搭建 Dev 场景
- [x] **GOSLO 鹦鹉模型**: Assets/Models/GOSLO.glb (29KB)
- [x] **LiveKit SDK 适配规则**: .cursor/rules/livekit-unity-sdk.mdc
- [x] **GitHub Push**: https://github.com/GOSLOParrot/ParrotCarriers (2 commits)
- [x] **Nanobot ParrotBusChannel**: nanobot/channels/parrot_bus.py — Redis Stream 消费 + agent 回复 → Pub/Sub 结果发布
- [x] **parrot_config.json**: nanobot fork 专用配置 (OpenRouter + Gemini Flash + parrot_bus + weixin channels)
- [x] **start_nanobot_worker.py**: 一键启动真实 nanobot gateway (--stub 可回退到 echo consumer)
- [x] **ParrotBusChannel 连通测试**: test_nanobot_channel.py 2/2 — ParrotBusChannel → 结果发布 + 全链路到 Brain
- [x] **Scheduler 超时检测**: 120s 任务超时 → 通知 Brain
- [x] **NANOBOT_TASK_TYPES 扩展**: +summarize, +remind (对齐 parrot_bus._build_prompt)
- [x] **Brain 结果反馈优化**: timeout/completed/其他状态区分处理
- [x] **Stub consumer 修复**: 增加 result 字段 (解决 result_summary 空白)
- [x] **集成测试修复**: Pub/Sub 按 task_id 过滤 (消除跨测试串扰)
- [x] **全量测试**: 27/27 通过 (22 单元 + 5 集成)
- [x] **猫娘女仆微信 Bot**: parrot_config.json 启用 weixin channel + SOUL.md 人格 + USER.md 用户画像
- [x] **start_nanobot_worker.py 升级**: 支持 --no-weixin 参数，默认启用 weixin + parrot_bus 双 channel
- [x] **P2 多角色协作架构设计**: 副协作模块定位 + 不引入外部协作框架 + 外挂 Obsidian/LobeChat 做主工作区
- [x] **GOSLO 模式信号**: HASH_GOSLO_MODE (Redis Hash) + Brain Agent 连接/断开时写入 active_body=live/chat
- [x] **GOSLO Chat bot 配置**: goslo_config.json (Telegram channel) + ParrotSoul SOUL.md/AGENTS.md + start_goslo_chat.py
- [x] **Protocol Snapshot v1.1**: 新增 Section 10 — 角色工作模式 + 多实例架构 + 信息共享策略 + 决策 D12-D17
- [x] **Scene.md 更新**: GOSLO 双身体(Live+Chat) 拆分为独立角色行项
- [x] **GOSLO 模式感知 pre-hook**: BaseChannel.pre_handle_hook + goslo_mode.py 中间件 (查 Redis → live 转发/chat 正常)
- [x] **start_goslo_chat.py 升级**: in-process gateway 启动 + 自动注入 mode hook (--no-mode-hook 可禁用)
- [x] **deploy-castle.sh 升级**: 双仓库同步 + nanobot pip install + GOSLO workspace setup + 3 tmux session 说明
- [x] **env-castle.template 更新**: 新增 GEMINI_API_KEY + TELEGRAM_BOT_TOKEN + REDIS_URL

### 当前不做 (P2/P2.5 阶段)

- [ ] 不做 DSG 真实视觉管线（需 A10 GPU，P3/P4）
- [ ] 不做 MemoryValidity 衰减层（P3）
- [ ] 不做 Skill Distillation 技能提炼（P3）
- [ ] 不做群聊（Telegram 群 + LobeChat，P3）
- [ ] 不加 VAD/Silero（Gemini 自带 turn detection）
- [x] ~~不做 XR Hands~~ → P2.5 已完成 Unity 端骨架 (XRHandTracker + PerchOnHand)

### 下一步

**当前真实下一步 (2026-04-29，已覆盖 2026-04-25 口径):**

1. **Sprint4 协议 Phase 1 已完成**：ECP-minimal 落地 + 审计回路修复。代码状态：`src/parrot/shared/ecp.py` + `_rpc_bridge` mirror + Unity DTO/handler + 19 项 pytest 全绿。
2. **下一步：Phase 3 前置调研（在新 chat 启动）**：
   - 主题：LiveKit Unity SDK + AR Foundation lifecycle / 重连 / 切屏 / 切设备（蓝牙/扬声器/麦克风）/ 视频质量切换 / 防御性机制
   - 输入：现有 Gemini deepResearch 策略性记录 + `docs/sprint4_research/result/01_*.md` + Sprint3 有效经验 + skill 验证（`client-sdk-unity` / `livekit-unity-video-publish` / `ar-foundation-api` / `ar-foundation-samples`）
   - 流程：先策略广度搜集 → 用户筛选 → 显式调用 skill 验证具体接口 → 产物落到 `livekit-unity-video-publish/IMPL_REF.md` 完善 + 新候选 skill (lifecycle / 防御性设计) + `ar_workspace_index.md` 登记
3. **Phase 3 实现暂缓**：等调研产出后回到现 chat 的 fork（ECP 审计完成那一轮）继续；不在调研 chat 里直接做实现。
4. **后端 Python 接口提炼推迟**：不从 ParrotDev 测试代码"屎里淘金"，等 Phase 3/4 部分跑通后再决定哪些接口值得提炼。
5. **AR 工作区文档路由已修复**：`workspace.mdc` / `INDEX.md` / `active_context.md` / `ar-foundation.mdc` / `livekit-unity-sdk.mdc` 已对齐 Sprint4 现状；新增 `architecture/ar_workspace_index.md` 作为 AR 任务聚合入口。

**当前关键路径 (按顺序, 每步完成再进下一步):**

1. **Sprint4 前置收口**：以 `sprint4_pre_entry_prompt_and_plan.md` 为任务入口，停止继续堆 Sprint3 测试束。
2. **App Flow / UI 基线**：以 `ar_app_flow_ui_design.md` 为当前真源，继续筛选启动页菜单、HUD/工具柜、放大镜、注意力框。
3. **数据流与协议 V2**：设计 `captureSnapshot`、`SnapshotEvent`、`SightingEvent`、`EcpCommand` / `EcpAck`、DSG L2-B 接口。
4. **Sprint4 实现顺序**：先实现能验证协议升级的最小功能，再扩展 2D 工作区、纸条、猫爪、主题皮肤。
5. **历史计划只作追溯**：`ar_app_plan.md`、旧 Sprint 报告、旧问卷不再定义当前 App Flow。

**Sprint 过程中按需补 skill/rule** (不提前):
- Sprint 2 末: `rules/scheduler-three-layer.mdc` — E2/E5 与三层意识收口约束
- Sprint 4 中 (S4.A3 后): `skills/unity-snapshot-service/SKILL.md` — AsyncGPUReadback 坑
- Sprint 4 中 (S4.B2 后): `skills/gemini-visual-match/SKILL.md` — Flash 多图比对约束
- Sprint 4 末: `rules/soul-constraints.mdc` + `rules/consciousness-dispatch.mdc` — 实测后固化

**P2 收尾延期项** (Sprint 之外, 不阻塞):
- GitHub Desktop push 4 个未推 commit → `sync-castle.ps1` → SSH `docker compose up -d`
- SSH 上跑 FalkorDB 健康检查 + Graphiti 集成测试

**P2 剩余 (随顺序推进):**
- [ ] Brain 优雅退出: AgentSession cleanup + 心跳停止 + Bus deregister
- [ ] `Scheduler._connect_livekit` 补完 (P1 遗留 stub，Castle 调试时做)
- [ ] 用户完成 fly/dance/idle/thinking 动画 (Minecraft 风格) → Unity 替换 Cube
- [ ] 像素画小纸条 (lore/ideas.md) MVP: Unity UI Canvas + 2D 像素风 Sprite + RPC 触发

**P2.5 准备:**
- [x] AR App Flow / UI 设计基线: `.cursor/memory/architecture/ar_app_flow_ui_design.md` (启动页+HUD/工具柜+工具入口+开放问题)
- [x] AR App 工程计划追溯: `.cursor/memory/architecture/ar_app_plan.md` (早期硬事实+调研索引+问卷，不再作为当前 UI 真源)
- [x] 视频流采样 skill: `.cursor/skills/livekit-unity-video-publish/SKILL.md` (5段接缝: Unity推流端+Gemini消费端+DSG预留接口+identify_object截帧路径)
- [x] AR Foundation 规则: `.cursor/rules/ar-foundation.mdc` (版本约束+5条已知坑)
- [ ] Cursor 工作区规则: .cursor/rules/ 模块隔离策略（按官方推荐）
- [ ] 新 skill 收集: XR Interaction Toolkit, Unity Sentis (本地推理)
- [ ] 猫娘 cron 任务: Obsidian vault 变更 → Gemini Flash 三元组补充
- [x] Google 生态 MCP 配置就位
  - 架构设计: `.cursor/memory/architecture/gemini_drive_bridge.md`
  - 验证计划: `.cursor/memory/architecture/verification_plan_google.md`
  - ⚠️ **真实 OAuth 联调未做** (Calendar/Gmail Trigger 需要用户账号授权)
- [ ] 三级调度 Priority 子树 (reflex > intent > task)
- [ ] ResourceLockManager 骨架 (body 通道互斥)

**lore/ideas.md 待回流到 requirements:**
- [ ] "发现 vs 未发现的不对称性" → 影响 `ExpectationChecker` 的 MISSING 判定和 `ConfirmationStatus` 状态机

**P3 前瞻:**
- [ ] MemoryValidity (信息有效期 + Ebbinghaus 衰减)
- [ ] Skill Distillation (工作流 → skill 自动提炼)
- [ ] DSG 真实视觉管线 (A10 GPU)
- [ ] Obsidian MCP 双向交互
- [ ] 群聊 (Telegram 群 + LobeChat)
- [ ] XR Hands 手势反射 (C8, C9)
- [ ] Unity ARFoundation 前端升级

### 新增重大讨论项与潜在风险 (2026-04-13)

- 🔶 **多工作区环境配置与双仓代码推送策略**: 当前部署是通过简单的 SSH 脚本强推。用户提出：后续开发在 PC 上的 Cursor 环境进行，但是在 ECS 和 `nanobot` 项目进行部署或者模式配置补充时，可能需要在 ECS 远程环境利用 `Remote SSH` 工作。这种工作模式的割裂可能会带来双仓代码同步、Git 冲突等问题。如何组织推代码（Push 策略）和切换 Agent 的关注点，是后续在进行 ECS 操作时必须先讨论清晰的痛点。未来请通过 `.cursor/rules/workspace.mdc` 定义隔离策略，但本期暂不急着改规则。
- 🔶 **LiveKit 的密钥错位问题**: 在本地进行开发，而服务端部署在云端时，由于 `.env` 与云端部署脚本中的 `livekit.yaml` 可能会错配（如云端 `secret` 与本地长字符串冲突导致 401），以后要保证 ECS 工作环境与本地 `.env` 永远严格对齐。
- 🔶 **网络 VPN 引发的 UDP 大丢包**: 测试证明使用科学上网代理（Clash/Mihomo）连接阿里云 ECS 7880 UDP 端口，会造成 3~5 秒极大延迟与丢包。测试 LiveKit 时必须为该 IP 配置直连（DIRECT）或直接关闭代理。

### 关于 Tool 阻塞（已确认）

- `fly_to` / `animate`: 等待 Unity RPC 响应（<10s），不阻塞 Agent 事件循环
- `dispatch_task`: 火即忘（publish → return），不等 Nanobot 结果

### P1.5 完成项（2026-04-12）

- **Scheduler**: SimpleRouter if-else → py-trees BT (Selector + HandleReflex/DispatchToNanobot/HandleBrainDirect)
- **Blackboard**: 自写空壳删除 → py-trees Blackboard V2 Client + namespace /scheduler/*
- **结果汇总**: Brain 不再直听 CH_NANOBOT_RESULTS → Scheduler 汇总后走 CH_SCHEDULER_TO_BRAIN
- **DataChannel**: TelemetryFrame(pose+timestamp+behavior_state) + TelemetryEvent 定义 + Python 接收回调
- **BehaviorMode**: Flag enum (BASE|COMPANION) + Blackboard 存储 + ParrotSoul 按模式拼接 instructions
- **协议快照**: protocol_snapshot_p1.md — 已验证/候选标注完整
- **共享枚举**: ParrotAnimation(8种) + ParrotBodyState(5种) + BehaviorMode(5种) 统一在 shared/parrot_actions.py
- **新增通道**: CH_SCHEDULER_TO_BRAIN = "parrot.scheduler.to_brain"
- **测试**: 22 passed (9 BT router + 4 parrot_actions + 4 telemetry + 5 bus registry)
- **审计修复 (2026-04-12 补)**: dispatch_task 任务类型与 BT 路由表对齐 + animate 强校验 + 正式链路集成测试 + docstring 更新 + 协议快照口径修正

### P1 审计发现（2026-04-11，P1.5 已修复的标 ✅）

- ✅ Blackboard 类已写但全仓库无调用方 → py-trees Blackboard V2 替换，BT 节点和 BTRouter 都使用
- ✅ Brain 直听 CH_NANOBOT_RESULTS 跳过 Scheduler 汇总 → 改走 CH_SCHEDULER_TO_BRAIN
- ✅ DataChannel 遥测（A6）完全空白 → telemetry.py + telemetry_receiver.py 骨架
- ✅ BehaviorMode 有调研设计但未实现 → Flag enum + Blackboard + ParrotSoul 集成
- 🔶 Scheduler._connect_livekit 仍是空壳（P1.5-B Castle 部署时补）
- 🔶 SimpleRouter 的 reflex_direct 和 brain_direct 无下游执行器（P2 接入 DataChannel/XR Hands）
- ✅ animate tool 已接入 ParrotAnimation enum 强校验（不在枚举内返回错误提示）
- 🔶 15 个 Redis 常量中仍有 10 个无消费代码（候选，P2 按需激活）
- 🔶 **多端 RPC 路由风险**: 当前 `_rpc_bridge.py` 寻找 `unity-*` 客户端的逻辑是找到房间里的“第一个”。如果是 `sim_unity_client` + `Unity Editor` 都在房间内且身份均以 `unity-` 开头，会导致 RPC 随机打给其中一个。P1 是单端 demo 此设计无伤大雅，P2/P3 多端多设备协作时需升级（广播 / 靶向）。

### 已确认事实（防翻案）

- Phase 1 = Bus-first（模块化基础设施，非 demo）
- Nanobot 直接适配（fork + parrot_bus.py），不做"最小部署"过渡
- A10 非前置条件：Phase 1 只为 DSG 留 Processor 挂载接口
- 调度器统一叫 Scheduler；查旧稿时注意历史名称 Dispatcher
- 双仓库架构：ParrotCarriers（主）+ nanobot（fork 已完成：GOSLOParrot/nanobot）
- 2C8G 够用: P2 已用 FalkorDB 替代 Neo4j (D-P2-1)，内存压力解除
- 协议由代码驱动，不在纸上空转，V1 定版可迭代
- GOSLOParrot = 主项目（家族全景）；ParrotCarriers = Bus 基建子项目
- GOSLO = 鹦鹉大小姐 desuwa；Nanobot = 猫娘女仆（Agents Team，默认 3 并发）
- 猫娘女仆微信 Bot = nanobot 内置 weixin channel，纯配置启用，零代码改造
- nanobot 一个实例可同时运行多个 channel（parrot_bus + weixin），共享 AgentLoop，独立 session
- GOSLO Chat bot = 第二个 nanobot 实例（goslo_config.json + goslo-workspace/ + ParrotSoul），P2 已创建配置
- GOSLO 双身体通过 Redis HASH_GOSLO_MODE 协调：Brain 连接时 active_body=live，断开时 =chat
- ParrotCarriers 定位 = 副协作模块 + 信息提供商，不膨胀为 one-for-all 工作区
- 不引入 AutoGen/CrewAI 等外部协作框架——Agent 是多进程独立实例，Redis Bus 已够用
- 群聊 = P3（Telegram 群 + LobeChat），P2 聚焦各角色 1对1 bot 稳定运行
- Graphiti 信息共享策略: group_id 分区隔离 (goslo/maid)，scene/user 分区共享只读
- ModuleManifest = 轻量挂载声明，不是 God Contract
- Brain Agent 使用 `agents.cli.run_app(server)` 作为入口点
- Agent dispatch 需显式调用 `agent_dispatch.create_dispatch()`
- Console 模式可以在无 LiveKit Server 时测试
- Unity 客户端 identity 必须以 "unity" 前缀开头（_rpc_bridge.py 检测）
- LiveKit Unity SDK v1.3.5 通过 UPM git URL 安装
- LiveKit Python SDK `with_ttl()` 需要 `timedelta` 而非 `int`
- `@server.rtc_session(agent_name=...)` 启用显式 dispatch，需通过 API 或 token room_config 触发
- sim_unity_client.py 内置 auto-dispatch 逻辑（检测房间无 agent 时自动调用 dispatch API）
- GitHub 仓库: https://github.com/GOSLOParrot/ParrotCarriers
- FalkorDB 替代 Neo4j (D-P2-1): 2C8G 下必选，~100-500MB vs ~2.7GB
- DSG 是耦合子系统，不是独立模块 (D-P2-2): 通过触发器/预加载/直写和 Graphiti/Brain 紧密耦合
- Gemini 4 条通信通道 (D-P2-3): 语音 / generate_reply / update_instructions / tools 返回值
- Obsidian 是人写 SSOT (D-P2-4): .md + UUID 绑定 Graphiti scene 分区，文件组织随意
- Graphiti 4 分区 (D-P2-5): goslo / maid / scene / user
- P2 里程碑详情: `.cursor/memory/milestone_p2.md`

---

## 关键上下文

- **项目**: `ParrotCarriers` — GOSLOParrot 通信总线子项目
- **GitHub**: `GOSLOParrot/ParrotCarriers` + `GOSLOParrot/nanobot`
- **服务器**: 东京 `ecs.g9i.large`（常驻）+ 东京 `A10`（按需），同 VPC
- **全局索引**: `.cursor/memory/INDEX.md`
- **需求清单**: `.cursor/memory/requirements.md` v2
- **模块划分**: `.cursor/memory/architecture/module_division.md`
- **总线架构**: `.cursor/memory/architecture/bus_v4.md` v4.2
- **审计报告**: `docs/report/2026-04-08_p1_bus_architecture_manifest_trace_report.md`
- **设计护栏**: `.cursor/memory/BigIssue.md`
- **P2 里程碑**: `.cursor/memory/milestone_p2.md` — 记忆共享 + Scheduler 增强 + DSG 耦合层
- **协议快照**: `.cursor/memory/architecture/protocol_snapshot_p1.md`
- **部署快照**: `.cursor/memory/deploy_snapshot_p2_20260412.md`

### 运行命令速查

```bash
# ===== 快速启动（推荐）=====

# 终端 1: 一键启动开发栈 + 生成 token
python src/scripts/run_dev.py

# 终端 1 (继续): 启动 Brain Agent
.venv\Scripts\python.exe -m parrot.brain.agent dev

# 终端 2: 模拟客户端 + 麦克风 + 全栈（Scheduler + Nanobot）
.venv\Scripts\python.exe src/scripts/sim_unity_client.py --mic --full

# ===== 手动分步 =====

# 开发栈
docker compose -f infra/docker-compose.dev.yml up -d   # Redis + LiveKit Server

# Brain Agent
python -m parrot.brain.agent console                    # 终端模式（无需 LiveKit）
python -m parrot.brain.agent dev                        # 开发模式（需 LiveKit）

# 模拟客户端（替代 Unity）
python src/scripts/sim_unity_client.py --mic            # 麦克风语音对话
python src/scripts/sim_unity_client.py --mic --full     # 语音 + Scheduler + Nanobot
python src/scripts/sim_unity_client.py                  # 仅监听（不发语音）

# Scheduler（单独启动，不用 --full 时需要）
python src/scripts/start_scheduler.py

# Nanobot Worker（stub 版，不用 --full 时需要）
python -m parrot.bus.nanobot_consumer

# 猫娘微信 Bot
D:\GOSLOParrot\ParrotCarriers\.venv\Scripts\nanobot.exe channels login weixin -c D:\GOSLOParrot\nanobot\config\parrot_config.json  # 首次扫码
python src/scripts/start_nanobot_worker.py              # 启动 parrot_bus + weixin
python src/scripts/start_nanobot_worker.py --no-weixin  # 只启动 parrot_bus

# Unity Token
python src/scripts/generate_token.py                    # 生成 → 保存到文件 + 复制到剪贴板
python src/scripts/generate_token.py --identity unity-phone  # 手机用

# 测试
pytest tests/test_bus/ -v                               # 单元测试
pytest tests/integration/ -v                            # 集成测试（需 Redis）
pytest tests/integration/test_graphiti_chain.py -v      # Graphiti 链路（需 FalkorDB）

# Castle 同步（日常）—— 详见 commit_guidelines.md §2
.\infra\sync-castle.ps1               # 只拉代码
.\infra\sync-castle.ps1 -Workspace    # 代码 + nanobot persona
.\infra\sync-castle.ps1 -Env          # 代码 + .env
.\infra\sync-castle.ps1 -All          # 全量

# Castle 首次部署或重置（用 Git Bash 跑）
bash infra/deploy-castle.sh 8.216.45.45

# ===== P2 新增 =====

# DSG 桌面模拟
python src/scripts/sim_dsg_desktop.py                   # 全场景模拟
python src/scripts/sim_dsg_desktop.py --scenario new    # 物体出现
python src/scripts/sim_dsg_desktop.py --scenario missing # 物体消失

# Obsidian 同步到 Graphiti
python src/scripts/sync_obsidian_to_graphiti.py --vault /path/to/obsidian/objects

# Graphiti 集成测试
pytest tests/integration/test_graphiti_chain.py -v      # 需要 FalkorDB 运行
```

### 手动验证场景

| 场景 | 你说什么 | 期望结果 |
|:-----|:---------|:---------|
| 语音对话 | "Hello Parrot" | Gemini 用 Parrot 人格语音回复 |
| 跳舞指令 | "Dance for me" | sim client 打印 `RPC animate: dance` |
| 飞行指令 | "Fly to 1 2 3" | sim client 打印 `RPC flyTo: {x:1,y:2,z:3}` |
| 后台任务 | "Search for IPoAC" | Scheduler 路由 → Nanobot 处理 → Gemini 语音反馈结果 |
| 记忆写入 | "记住我喜欢咖啡" | Graphiti goslo 分区写入 → 下次启动能搜到 |
| 记忆查询 | "我之前说过什么" | query_memory 从 Graphiti 搜索 → 返回结果 |
| 场景查询 | "桌上有什么" | query_scene 从 Graphiti scene 分区搜索 |
| 模式切换 | "切换到研究模式" | set_mode → Redis → mode_watcher → instructions 更新 |
| 物体发现 | "这是什么东西？" | identify_object(match) → Graphiti 搜索 → L2-B 更新 → 自然回复 |
| 保存新物体 | "记住这个杯子" | identify_object(save_new) → Graphiti 写入 + L2-B 节点 + SSOT 触发器 |
| 深度搜索 | "帮我查一下这个" | identify_object(deep_search) → Nanobot research → 结果回写 |
| Episode 管理 | "开始新任务：找包裹" | manage_episode(start) → L2-B Episode 创建 |
| 日程提醒 | (自动) | CalendarTrigger → Nanobot → 三层提醒 → Gemini 自然播报 |
