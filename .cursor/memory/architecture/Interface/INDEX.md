---
status: ratified
category: interface-skeleton
status_note: "P2.5 接口分类骨架（2026-05-09）。上一轮 v0 把 12 场景调用栈穷举 → 仓库复印；本目录用核心/业务二分 + 4 字段业务模板 + 失败教训前置 取代。任何接口提炼 / 命名审计 / Web 控制台 / Obsidian / Figma chat 入场必读。"
last_reviewed: 2026-05-09
ai_priority: high
ai_audience: "所有动 src/parrot/** 公开表面或 unity/ArSpike/Assets/Scripts/ParrotApp/** DTO 的 chat"
parent_doc: "../../INDEX.md"
related:
  - "../backend_interface_refinement_20260507.md (Brain Core SSOT)"
  - "../protocol_snapshot_p4.md (协议 SSOT)"
  - "../bus_v4.md (Bus 拓扑)"
  - "../dsg/workspace_index.md (DSG 工作区入口)"
  - "../chat_launches/ (3 份待开 chat launch prompt)"
  - "menu_design_complete_20260507.md (菜单设计 SSOT)"
  - "concept_dictionary_20260507.md (术语)"
  - "legacy_issues_split_20260507.md (P2.5/P3 NEED 登记)"
---

# Interface 工作区索引（核心 / 业务 二分 + 4 字段业务模板）

> **本文用途**：接口提炼的**入口**与**纪律**。任何动 `src/parrot/**` 公开表面或 `unity/ArSpike/Assets/Scripts/ParrotApp/**` DTO 的 chat 入场前必读。
> **不是**：把仓库再罗列一遍的"接口大全"。

---

## §0 上一轮失败教训（必读，决定本目录所有取舍）

2026-05-07 P2.5 接口提炼 v0（[`interface_design_and_how_todo_v0_20260507.md`](interface_design_and_how_todo_v0_20260507.md)）走了"自下而上 12 场景穷举"路线，把每条场景的调用栈逐层抄进文档，最终产物把仓库复印了半份，user 原话："效果非常糟糕"。

**根因**：
- 自下而上从场景出发 → 每条业务都把它路过的所有核心模块 API 抄一遍 → 同一个 API 在 N 份场景表里重复 N 次
- 没有"核心 vs 业务"分层 → 文档里既有"该业务做什么"又有"该模块的稳定 public 表面是什么"，两者纠缠不清
- 把"完成判据"写成"覆盖率"（接口都列上 = 完成），不是"业务能跑通"

**本目录后续严禁**：
- 不在业务接口文档里抄核心接口签名（只写"用了哪些核心接口"）
- 不在核心接口文档里枚举所有调用方（只写"这一层为什么稳定 / 不动"）
- 不把"接口完整性"当目标 → 目标是"该业务跑通 + 核心层不被反复推翻"

**v0 + supplement 状态**：标 superseded_by 本文件，**不删**——12 场景清单本身仍是有用的"业务清单参考"，只是不再当作"接口设计产物"。后续业务接口写作时可拿来对照"我这条业务在 v0 第几场景"。

---

## §1 核心接口（按协议模块；指针式，不抄签名）

> **核心接口** = 模块的稳定 public 表面，约束是"不动这层接口，业务怎么换都不破"。
> **本节只放指针**——签名细节去对应 SSOT 看；新增核心接口必须先在 SSOT 落地，再回填本节加一行指针。
> **补充候选**（如 RustworkX 节点 CRUD / DSG L2-B 注意力查询）必须先读模块职责 + 架构设计 + 对应 skill，再判断"是不是真的稳定到能进核心层"。

### §1.1 Bus（传输 / 通道 / 拓扑）

- 真源：[`../bus_v4.md`](../bus_v4.md) §三层协议 + §拓扑 + §East-West/North-South + [`../protocol_snapshot_p4.md`](../protocol_snapshot_p4.md) §channel/topic + §BB key + §13 决策锁
- Skill：`.cursor/skills/client-sdk-unity/` / `.cursor/skills/livekit-agents/` / `.cursor/skills/parrot-bus-orchestration/`
- 边界：DataChannel ≤ 8KB / RPC Reliable / Redis Stream 长任务 / Blackboard V2 跨模块状态

### §1.2 Brain（云端大脑公开 API）

- ⭐ 真源：[`../backend_interface_refinement_20260507.md`](../backend_interface_refinement_20260507.md) — **已 ratified 的 Brain Core SSOT**，覆盖 Persona / 4-block Menu Registry / Preset Loader / IntentWorkspace / BB watcher registry / L2-B baseline algorithms 全部代码已落公开签名
- 补充：`brain/tools/` 下 10 个 function_tool（Gemini 可调） — 已在 `protocol_snapshot_p4` §tool 段
- Skill：`.cursor/skills/livekit-agents/` (Agent 框架) / `.cursor/skills/py-trees/` (BT 接口对位)

### §1.3 DSG（感知耦合层 / L1.5 / L2-A / L2-B / Ingest / 触发器）

- 真源：[`../dsg/workspace_index.md`](../dsg/workspace_index.md) §核心接口 + 13 份 dsg/dsg_protocol_*_v1 / dsg_decisions_master / dsg_current_state_distilled
- 补充候选（动前必看）：节点 CRUD / 图查询 / 注意力扩散 / 子图激活 → 用 `.cursor/skills/dsg-rustworkx-master/` 决定走 RustworkX 哪条 API + `.cursor/skills/dsg-l2b-node-organization-options/` 看组织选项
- ADR 锁：[`../adr_l1_5_source_dispatch_extension_space_20260504.md`](../adr_l1_5_source_dispatch_extension_space_20260504.md) — SemanticNode.source 字段边界 + Meta dict/factory hook 扩展空间 + chat 路径锁。**任何动 `src/parrot/dsg/**` 的 chat 必读**

### §1.4 Memory（Graphiti 桥 + FalkorDB + 对话归档 + 三阶段工作记忆）

- 真源：[`../dsg/dsg_protocol_archive_v1_20260506.md`](../dsg/dsg_protocol_archive_v1_20260506.md) + Graphiti skill 内的 `add_episode` / `search` / `group_id` 分区
- Skill：`.cursor/skills/graphiti/` — Graphiti API 全量 + 自定义 entity types + MCP server
- 边界：hot 内存（IntentWorkspace）→ cold 硬盘（disk recovery）→ nanobot 闲时归档；三阶段在 `dsg_current_state_distilled §12`

### §1.5 Scheduler（py-trees BT + Blackboard V2 + Reflex/Intent/Task 三层）

- 真源：[`../protocol_snapshot_p4.md`](../protocol_snapshot_p4.md) §BT topic + §BB key + §三层调度面（与 ECP 对齐）+ [`../sprint4_protocol_v2_ecp.md`](../sprint4_protocol_v2_ecp.md) §BT 对齐
- Skill：`.cursor/skills/py-trees/` — Behaviour / Selector / Sequence / Parallel / Blackboard V2 / event-driven tick

### §1.6 Bus 服务化外挂（Nanobot / SVA / LiveKit Agents）

- Skill：`.cursor/skills/nanobot/` / `.cursor/skills/sva-vision-agents/` / `.cursor/skills/livekit-agents/`
- 真源：[`../bus_v4.md`](../bus_v4.md) §九 外挂生态 + [`../module_map_p2.md`](../module_map_p2.md) §九

---

## §2 业务接口模板（4 字段，不写签名）

> 业务接口在**对应业务 chat 内**写，**不写在本目录**；本节只规定**写作纪律**。
> 任何业务 chat 启动时，按字段 A→B→C→D 顺序填表。

### 字段 A — 模块职责回读（必读 ≤ 3 个文档）

写之前必须读：
- 必读 1：本业务主要触及的核心模块的 §1.x 真源
- 必读 2：[`../module_map_p2.md`](../module_map_p2.md) 对应模块的成熟度 + A10 依赖
- 必读 3（条件性）：相关 Skill SKILL.md 头部 / 相关 ADR

填表样式：`A = [doc_path §section, doc_path §section, ...]`（**3 项以内**；不抄正文，只列定位）

### 字段 B — 用现有核心接口能否组合实现？

二选一：
- **yes** → 跳过字段 C，进字段 D 写完成判据；本业务**不补核心**
- **no** → 进字段 C 设计补充

**判据**：业务能否仅通过 §1 列出的指针 SSOT 中**已有**的签名 + 通过现有 channel / topic / BB key 跑通？如果需要新建 channel / topic / BB key / function_tool / RPC method，则 **no**。

### 字段 C — 需要补哪些核心接口（仅在 B = no 时填）

| 子字段 | 写什么 |
|:--|:--|
| 命名 | 候选签名（不必精确，候选即可） |
| 落点模块 | 哪个 §1.x 模块承载（Bus / Brain / DSG / Memory / Scheduler / 外挂） |
| 是否进 protocol_snapshot_p4 | wire 字段必须；纯 Python 内部 API 不必 |
| 是否需要 cs_parity | 有 Unity DTO 镜像必须；纯 Python 内部不必 |

**写完字段 C 不等于动手**——补核心接口必须先开**子 chat**走 protocol upgrade 流程（参考 `../adr_protocol_upgrade_and_interface_refinement_background_20260504.md` §流程），不在业务 chat 内直接动协议。

### 字段 D — 完成判据（业务能跑通，不是覆盖率）

写"什么输入 → 什么可观测"两条：
- **正向**：典型输入下，业务可观测的最小验证信号（例：用户在 Web 控制台点 "查看 DSG 节点 X 详情" → 收到 JSON 含 `id / kind / source / last_sighting_path`）
- **失败**：若依赖的核心接口未补，业务的失败信号是什么（例：404 + log "intent_workspace 未注册 X scope"）

---

## §3 三个待开 chat 的业务接口占位

> 占位仅放 chat 文件名 + 一行 scope；**不在本目录填字段 A-D**——字段 A-D 在 chat 启动时由该 chat 自己填进 [`../chat_launches/`](../chat_launches/) 对应 launch prompt 内。
> 业务接口子目录（`Interface/business/`）**不在准备阶段创建**——避免空架子；第一个 chat 启动且产出第一份业务接口表时再建。

### §3.1 Obsidian 真连接

- Launch prompt：[`../chat_launches/obsidian_realconnect_launch_20260509.md`](../chat_launches/obsidian_realconnect_launch_20260509.md)
- Scope：后端 ↔ Obsidian 三子类（Ref-加强 / 设定-日常 / 设定-Roleplay）真连接 ingest；Web 真连接显式 defer

### §3.2 Web 控制台 read-only 优先

- Launch prompt：[`../chat_launches/web_console_launch_20260509.md`](../chat_launches/web_console_launch_20260509.md)
- Scope：DSG 可视化 + Ref 仓库 + 模块状态 + 菜单/画布管理；read+write 在第二轮

### §3.3 Figma UI 资产入工作区

- Launch prompt：[`../chat_launches/figma_ui_assets_landing_launch_20260509.md`](../chat_launches/figma_ui_assets_landing_launch_20260509.md)
- Scope：Figma 设计稿 → `unity/ArSpike/Assets/UI/`（Codex+Unity MCP 工作区主导）+ Cursor 工作区设计参考目录
- 备注：本条主要是**资产入仓**，不涉及 §2 4 字段业务接口

---

## §4 本目录 8 份文件状态

| 文件 | 状态 | 角色 |
|:--|:--|:--|
| `INDEX.md`（本文） | active | 接口分类骨架（Core/Business 二分 + 4 字段模板） |
| `concept_dictionary_20260507.md` | active / Design | ≈100 项术语 + 路由指引 |
| `legacy_issues_split_20260507.md` | active / Requirements | P2.5 / P3 NEED 二分 + grep 速查 + 修复 chat 派发表 |
| `menu_design_complete_20260507.md` | active / Design | 完整菜单设计 SSOT（4 类块 + 预设 + 海盗换肤） |
| `goslo_app_game_overview_asset_brief_20260507.md` | active / Design | App 总览 + 美术资产 brief |
| `interface_design_and_how_todo_v0_20260507.md` | superseded_by INDEX.md | 12 场景接口栈穷举主表（场景清单仍可参考） |
| `interface_design_supplement_20260507.md` | superseded_by INDEX.md | v0 之外 7 项新发现 |
| (已外迁 → docs/sprint_archive/sprint4/) | — | `app_flow_chat_launch_prompt_v2_20260507.md` + `backend_interface_chat_launch_prompt_v2_20260507.md` |

---

## §5 入场顺序（任何动 src/ 公开表面 / Unity DTO 的 chat）

1. 读本文 §0（教训前置）
2. 按业务方向找 §1.x 对应核心层指针 SSOT，**只读 SSOT 头部 + 章节目录**（不读全文）
3. 按 §2 字段 A 列回读清单（3 项以内）
4. 按 §2 字段 B 判定是否需补核心；若 yes 则字段 C 留空
5. 写字段 D 完成判据
6. 进入业务实施 / chat 内代码实现
7. **如字段 C 非空** → 不在本 chat 动手；fork 子 chat 走 protocol upgrade 流程
