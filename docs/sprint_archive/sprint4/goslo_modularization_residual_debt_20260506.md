---
status: ratified-audit / advisory
category: modularization-audit
status_note: "GOSLO 模型模块化任务 — 暗线审计（Step 1.5）。覆盖 7 类 parrot-isms 残余债 + 当前 Chat Step 2-5 是否需吸纳的判定 + p2.5 / p3 前瞻性需求注记（菜单画布 / 设定文件 / 多模型 / 预设保存）。本文不动代码；产出供 DSG 协议升级 Chat 标 TODO + Chat 4 接口提炼入场。"
last_reviewed: 2026-05-06
authoritative_for: "GOSLO 模块化的'残余债清单'+'本 Chat 任务范围裁定'+'未来菜单画布等 p2.5/p3 需求注记的来源依据'"
parent_doc: "../INDEX.md"
sources:
  - "goslo_model_modularization_launch_prompt_20260506.md (任务启动 prompt)"
  - "goslo_model_manifest_protocol_v1.md (Step 1 协议规则文档)"
  - "src/parrot/brain/soul.py (LLM persona 真源)"
  - "src/parrot/brain/tools/{set_mode,query_scene,fly_to,animate}.py"
  - "src/parrot/dsg/l1_5/{buckets,scene_snapshot}.py (DSG bucket/scene 切换能力)"
  - "src/parrot/shared/parrot_actions.py (wire-locked enum)"
  - ".cursor/memory/parrot_behavior_rules.md (行为规则文档)"
related:
  - "ar_workspace_index.md (AR 工作区聚合)"
  - "ar_app_flow_ui_design.md (AR App Flow / UI — 菜单需求落点)"
  - "lineb_implementation_completion_20260504.md (报告样板)"
---

# GOSLO 模型模块化 — 残余债审计 + 前瞻性需求注记（Step 1.5）

> **本文用途**：GOSLO 模型模块化任务（[`goslo_model_modularization_launch_prompt_20260506.md`](goslo_model_modularization_launch_prompt_20260506.md)）的"暗线审计"产出。Step 1（Manifest schema + 协议文档）已落地后，user 提的隐藏任务："顺便审查相关模块的模块化状态（即使换成自定义模型也能跑）"。
>
> **基调**：本 Chat 范围只做"自定义模型 + GOSLO 模块化"+"暗线审计"。审计**只 inventory + 标严重度 + 给修法建议**，**不动代码**。残余项中的高严重度项考虑是否纳入本 Chat Step 2-5；其余推到下游 Chat。p2.5 / p3 前瞻性需求（菜单画布 / 设定文件 / 多模型 / 预设保存）由本文记录后，由 user 在 **DSG 协议升级 Chat** 标 TODO 入 App / 核心功能需求；**Chat 4 接口提炼**会以本文为输入。

---

## §0 TL;DR

| 维度 | 结论 |
|:--|:--|
| Step 1 协议层 + ECP 部分 | ✅ **够了**（不需要继续升级 schema / wire；后续 Step 2-5 不会回头改 Step 1 字段集）|
| 暗线审计：parrot-isms 渗透 | ⚠️ **7 类**（高 1 / 中 2 / 低 4），见 §2 |
| 影响"非 parrot 模型也能跑" | 高严重度只有 **`brain/soul.py` LLM 人设**（不修：Q 版 chibi 仍说自己是鹦鹉）|
| 本 Chat Step 2-5 是否需调整 | ❌ Step 2 / 3 / 4 / 5 plan **不动**；高严重度的 LLM persona 建议作为新 Step 6 候选（可选纳入 / 推下游） |
| 前瞻性需求注记（不在本 Chat 实施） | p2.5 设定文件 / p3 多模型 / p3 菜单画布（4 类块拖拽 + 预设） / p3 默认保存恢复 |
| 现有 DSG 能力（user 询问） | ✅ 已有：`BucketRegistry` 一键管理 + `SceneRegistry.SceneSwitchOutcome` 场景切换。**未有**：persona/setting 文件外置 + 4 类块绑定预设 |

---

## §1 范围

### §1.1 本审计要回答什么

1. Step 1 协议层是否够了 → 是否需要继续动 wire / schema → 答案见 §0。
2. 现有代码里**还有什么地方假设"伴侣是只 GOSLO 鹦鹉"**？换成自定义模型时哪些会碎？→ §2。
3. 本 Chat 的 Step 2-5 plan 要不要因审计调整？→ §3。
4. 哪些是本 Chat **不该做**、但需要在下游 Chat 拿到的"前瞻性需求"？→ §4。

### §1.2 本审计**不做**什么

- 不动代码（`tests` 也不动 — 本文是 advisory，写完即冻结）
- 不修改 App / 核心功能需求文档（`requirements.md` / `ar_app_flow_ui_design.md` / `milestone_p2.md`）— 由 user 在 DSG 协议升级 Chat 完成
- 不展开 Chat 4 接口提炼工作（本文只为它准备入场素材）
- 不做 LLM persona 参数化的实施（即使建议做，也是新 Step 6 — 由 user 决定是否纳入本 Chat）

---

## §2 残余债清单 — 7 类 parrot-isms

按"换成非鹦鹉模型时是否会破"的严重度排序。

### §2.1 ⚠️ 高严重度（阻塞"非鹦鹉模型跑通"）

#### #1 `brain/soul.py` — LLM 人设系统提示词

**位置**：`src/parrot/brain/soul.py` `CORE_INSTRUCTIONS` / `COMPANION_INSTRUCTIONS` / `PLAYFUL_INSTRUCTIONS`

**渗透点**：
- "You are Parrot — a cheerful Minecraft-style parrot companion living in augmented reality."
- "Playful, curious, and loyal. You love perching on the user's shoulder."
- "You occasionally squawk or make parrot sounds for emphasis."
- "animate: Play an animation (dance, head_bob, wing_flap, idle, sleep, perch, sit, fly)."
- "Keep responses concise — you're a parrot, not an essay writer."
- COMPANION 段："Respond to affection warmly — you love head scratches and shoulder perching."
- PLAYFUL 段："Use animate frequently — dance, wing_flap, head_bob at every opportunity."

**当前耦合**：人设 prompt 内联在 Python 模块、`get_instructions(mode)` 根据 BehaviorMode 拼接，**与 model_id 无关**。

**换非鹦鹉模型会发生**：Unity 端骨骼正确驱动（Q 版 chibi 跳舞），Brain LLM 仍以"鹦鹉 + 喜欢 perch on shoulder + squawk"语气回应；动作描述（"flying" / "wing flap"）与视觉（人形挥手 / 鞠躬）严重不匹配。

**修法建议**（新 Step 6 候选 / 或下游 Chat）：
1. 把 `CORE_INSTRUCTIONS` / mode 段抽到外部"人设文件"（建议路径 `src/parrot/brain/personas/<persona_id>.md` 或 `.toml`），加载器 `parrot.brain.persona_loader.load(persona_id)`
2. 现有 `CORE_INSTRUCTIONS` 等 = `personas/goslo_parrot_default.md`（行为 0 漂移）
3. ModelManifest **不**直接含 persona — model 与 persona 解耦（user 期望 §4.3 的"模型 / 设定 / 模式 三者各自切换"）
4. Brain Agent 启动时按 BB key `global/active_persona_id` 选 persona file（默认 `goslo_parrot_default`）
5. p3 菜单画布：persona 文件成为"设定块"的具象化载体

**严重度**：⚠️ 高 — 这是"非鹦鹉模型也能跑"语义层面的最大坑。

**纳入本 Chat 与否**：建议**作为新 Step 6**（推荐但非阻塞）。如果不纳入，Step 5 完成报告必须显式声明"已知缺陷：Brain LLM 人设仍硬编码鹦鹉，换模型时 LLM 语气不会跟着变"。

---

### §2.2 ⚠️ 中严重度（功能受限但能跑）

#### #2 `ParrotBodyState` enum + `EcpFrontendState.body_state` wire

**位置**：`src/parrot/shared/parrot_actions.py` `ParrotBodyState` (5 项 wire-locked) + `src/parrot/shared/ecp.py` `EcpFrontendState`

**渗透点**：
- 5 项：`idle / flying / perching / dancing / frozen`
- 受 **Phase 4 §8 wire 锁** 约束（增减需新 ADR + cs_parity 全过）
- Unity 端 `EcpAckJson.Completed` 必须返回这 5 项之一作为 `body_state`

**换非鹦鹉模型会发生**：Q 版 chibi 实际在 walking / waving / sitting_on_chair，但 wire 上必须挑一个 parrot 风味的 5 项（最接近 = `idle` / `dancing`），上报粒度变粗。Brain 不会因此崩；只是"伴侣自我感知"信息丢失精度。

**修法建议**（**不在本 Chat**，需新 ADR）：
- **Option A**（保守）：保留 5 项 wire，加 `EcpFrontendState.controller_body_state: str` 自由字段（model 可填自己的语义；Brain LLM 通过 `attach_state_header` 看 controller_body_state；`body_state` 仍走粗粒度兼容 wire）
- **Option B**（激进）：升级 `body_state` 为自由 string，模型自带语义；旧 5 项变成"标准方言"。需要 ADR + cs_parity 升级。

**纳入本 Chat 与否**：❌ **不纳入**。本 Chat 不动 wire schema 是硬约束。注记到 §4.2 forward-looking。

#### #3 `brain/tools/fly_to.py` — 动词假设会飞

**位置**：`src/parrot/brain/tools/fly_to.py` + `set_mode.py` 把"butler / researcher / playful"模式描述都假设 parrot 上下文。

**渗透点**：
- Tool 名 `fly_to` + LLM 描述 `"Move yourself to a position in the user's AR space"` — 暗示飞行
- `wrap_legacy_rpc_payload` 的 `target={"state": "flying", ...}` 写死 "flying" 值
- 非飞行模型（人形）调用 `fly_to` → Unity 端 GosloLegacyController 会触发 `Fly` capability → 飞行动画播放 → 视觉违和

**修法建议**（**不在本 Chat**）：
- Tool 暴露层做 **capability gating**：Brain Agent 启动时读 active model manifest 的 `declared_capability_ids`，只把 model 实现的动作对应的 tool 注册给 LLM
- 例：active model 不声明 `fly` 能力 → `fly_to` tool 不注册 → LLM 看不到该 tool → 不会调用
- 这需要 `ModelManifest` 在 Brain 端可访问（Step 3 加 `model_id` 参数到 `animate` 时同步落地一个 `ModelManifestRegistry` Brain 副本即可，但本 Chat 设计图没含这部分；建议作 Step 3 增量或下游）

**纳入本 Chat 与否**：⚠️ **建议作为 Step 3 增量**（轻量；Brain 端读 manifest 后给 LLM 暴露 capability 列表 — 5-15 行代码 + 1 个测试）。但 user 可裁定"推下游"，因 Step 3 主任务是 `model_id` 参数化。

---

### §2.3 ⚠️ 低严重度（命名 / 品牌化，不影响跑）

#### #4 `brain/tools/animate.py` 的 `VALID_ANIMATIONS` 强校验

**位置**：`animate.py:15` `VALID_ANIMATIONS = {a.value for a in ParrotAnimation}`

**渗透点**：Tool 拒绝任何非 8 项 enum 值。

**当前耦合 + 是否需要改**：
- Step 1 协议设计已经把 8 项 enum 解释为 **Brain LLM 词汇表**（不是模型必须实现集），所以 Brain 主动调 `animate` 一定走 8 项之一 → enum 校验**仍然合理**
- 自定义动作（`dance_q_pose`）走 `dispatch_task` 或后续新 tool（如 `play_capability`），不走 `animate`
- ✅ **不需要改**

**纳入本 Chat 与否**：❌ 无需。

#### #5 `dsg/triggers/goslo_curiosity_trigger.py` + `dsg/ingest/base.py:GOSLO_AUTONOMOUS`

**渗透点**：命名包含 "GOSLO"；语义 = "伴侣自主好奇心触发"。

**修法建议**：跨模型语义不变（任何伴侣都可以"自主好奇"），改名是品牌化工作。**推下游**。

#### #6 `memory/graphiti_client.py:PARTITIONS.GOSLO`

**渗透点**：Graphiti 记忆分区键 = `"goslo"`。

**修法建议**：语义 = "伴侣自己的记忆 vs 用户的 vs 场景的"，跨模型仍有效。改名涉及**已写入数据迁移**（FalkorDB 中 group_id = "goslo" 的节点），工作量大且无收益。**不改**，作为约定保留。

#### #7 `parrot_behavior_rules.md` 文档 + `ParrotApp.Parrot.*` Unity 命名空间

**渗透点**：
- `parrot_behavior_rules.md` 标题 "GOSLO 鹦鹉行为状态规则"，但实际章节内容（body / head / cognitive 三层 + 调度优先级）**模型无关**
- Unity `ParrotApp.Parrot.*` 命名空间 + `ParrotController` / `ParrotRpcHandler` / `ParrotRegistry` 等类名

**修法建议**：品牌化工作；建议保留（GOSLO 是项目品牌名，不是模型名）。Step 2 新增的 `ParrotRegistry` / `ModelDriver` / `IParrotController` **保持现有命名**（`Parrot` 在这里 = "伴侣门面"，与具体模型解耦）。

---

## §3 本 Chat Step 2-5 plan 评审 — 需要调整吗？

| Step | 原 plan | 审计后判定 |
|:--|:--|:--|
| **Step 2** — Unity ModelDriver 三层 + GOSLO shim | 不变 | ✅ 不调整。AnimationDriver hardcoding 是 Step 2 的目标，正好对应 §2 #2 的 Unity 侧。 |
| **Step 3** — Brain `animate(model_id)` 参数 | 不变（基础）+ 可选增量 | ⚠️ 若纳入 §2 #3 的 capability gating，Step 3 范围 +20%（Brain 端 ModelManifestRegistry stub + tool 动态注册校验）。**建议先做基础 Step 3，capability gating 留 Step 3.5 / 下游**。 |
| **Step 4** — AI CLI MVP + MMD demo | 不变 | ✅ 不调整。 |
| **Step 5** — 完成报告 | 不变 + 必须显式声明已知缺陷 | ⚠️ 报告必须列出"已知缺陷：LLM 人设硬编码鹦鹉"（§2 #1）+ "已知缺陷：fly_to 动词假设会飞"（§2 #3 未做时）。 |
| **Step 6（新候选）** — Brain persona 参数化 | — | ⚠️ **可选**。15-30 分钟工作量：persona file 抽取 + 加载器 + BB key + 默认 `goslo_parrot_default`。是否纳入本 Chat 由 user 决定。 |

### §3.1 user 决策点

请在审计后给出 Step 6 取舍：

- **取**：本 Chat 多花 30 分钟把 LLM persona 也外置 → 真正"换模型也能跑得自然"
- **舍**：Step 5 完成报告显式标记此为"高严重度残余债"，由下游 Chat 完成（节省时间，但 demo 时换 Q 版 chibi 仍是"鹦鹉嗓"）

---

## §4 前瞻性需求注记（**不在本 Chat 实施**）

下列需求**不属于本 Chat 范围**，但本审计为其落定**事实依据 + 建议接口形态**，便于 user 在 DSG 协议升级 Chat 标 TODO 入 App / 核心功能需求 + Chat 4 接口提炼时直接消费。

### §4.1 p2.5 — 设定文件管理（user 提及）

**user 原话**："设定修改有 DSG 部分倒是应该有足够的能力接口了（好像是 bucket 和 L1.5 池的一键管理），而设定文件好像还不能管理。"

**事实核查**：

| 维度 | 现状 |
|:--|:--|
| DSG bucket 管理 | ✅ 已有：`src/parrot/dsg/l1_5/buckets.py` `BucketRegistry` + `BucketOpKind` + `BucketOp` 完整一键操作 API |
| DSG scene 切换 | ✅ 已有：`src/parrot/dsg/l1_5/scene_snapshot.py` `SceneRegistry.SceneSwitchOutcome` + `SceneType` enum + `SceneProfile`；可切换 + 快照保存 |
| 行为模式（BehaviorMode） | ✅ 已有：`set_mode` tool（`companion / butler / researcher / playful / full`）+ BB key `global/behavior_mode` + `mode_watcher` |
| **persona / 设定文件外置** | ❌ **未有**：`brain/soul.py` 全部内联，无加载器，无 BB key，无文件 |
| **L1.5 池一键管理 UI 入口** | ⏳ 后端能力齐全；缺 Unity menu UI 入口 |

**p2.5 建议入需求**（user 在下游 Chat 标 TODO）：

> **NEED-P2.5-A**：persona / 设定文件外置 + 加载器 + BB key（`global/active_persona_id`）+ 默认 `goslo_parrot_default`。建议路径 `src/parrot/brain/personas/`，文件格式 `.md` 或 `.toml`（含 `core_instructions` + 各 mode 段）。覆盖审计 §2 #1。
>
> **NEED-P2.5-B**：Unity menu 暴露 DSG bucket / scene 切换接口（后端齐全；UI 端点 + 协议绑定为新增工作）。

### §4.2 p3 — 多模型协议-状态延伸

**事实**：当前 `ParrotBodyState` wire 锁住 5 项，仅适合鸟类（§2 #2）。

**p3 建议入需求**（**新 ADR**）：

> **NEED-P3-A**：评估给 `EcpFrontendState` 加 `controller_body_state: str` 自由字段（保守 Option A），还是升级 `body_state` 为自由 string（激进 Option B）。Option A 是渐进、向后兼容、不破 cs_parity 的路径，建议先走。

### §4.3 p3 — 菜单画布（block-based composer）

**user 原话**：

> "我希望到时候 模型 / 设定 / 模式 三者可以快速各自切换，预设、和绑定随意组合的那种。"
>
> "你可以自定义和设定不同的设定块和功能块、模式块、场景块等。只要把这些设定块和功能块给在菜单的画布里连接起来（类似于网上的那种工具流），就可以保存好预设模式，下次进房间选预设来启动就行了。"
>
> "当然普通的菜单和保存、恢复默认也应该有。"

**结构概念**（本审计描述，供下游消费）：

```
菜单画布 = 节点图 + 预设保存
节点类型（"块"）：
  ┌─ 模型块（Model）       — model_id，加载 ModelManifest
  ├─ 设定块（Persona/Setting）— persona_id，加载 persona file（§4.1 NEED-P2.5-A）
  ├─ 模式块（Mode）         — BehaviorMode flags
  └─ 场景块（Scene）        — DSG SceneProfile + bucket 集合 + group_id 切片

边（连接）：
  - 模型 ←→ 设定（绑定关系：可任意组合）
  - 设定 ←→ 模式（绑定关系：模式覆盖设定子句）
  - 模型/设定/模式 ←→ 场景（场景内激活的组合）

预设 = 一个节点图快照（JSON）
进房间流程：
  1. 选择预设（或"默认"=GOSLO + parrot_default + companion + main_scene）
  2. ParrotApp 启动时按预设把 active_model_id / active_persona_id /
     active_mode / active_scene 4 个 BB key 全部 set
  3. ModelDriver / persona_loader / mode_watcher / SceneRegistry
     按各自 BB key 加载/切换
```

**p3 建议入需求**：

> **NEED-P3-B**：4 类块（模型 / 设定 / 模式 / 场景）每类需要：① ID 命名空间 + 注册表 ② 文件/数据格式 ③ 加载器 ④ active BB key ⑤ 切换事件
>
> **NEED-P3-C**：预设 = 4 个 active ID 的命名快照；JSON schema TBD；存放路径建议 `data/presets/<preset_id>.json`
>
> **NEED-P3-D**：Unity menu UI = node-canvas（参考 ComfyUI / n8n / Unreal Blueprint 的拖拽连线 UX）；本 Chat 不设计 UI，但 SO（ScriptableObject）层接口约定要预留
>
> **NEED-P3-E**：默认菜单 fallback — 每个块类都有"默认"+ 列表选择 +"保存当前组合为预设"+"恢复默认"；这是非画布用户的兼容路径，不能省

### §4.4 接口提炼准备（Chat 4 输入素材）

本审计为 Chat 4 接口提炼提供以下 inventory：

1. **§2 七类残余债** = "需要参数化 / 解耦的接口点"输入清单
2. **§4.1 现有 DSG 能力 inventory** = "已有接口，需要 menu binding"清单
3. **§4.3 4 类块结构** = "新接口的命名空间设计"输入

Chat 4 不需要重做 inventory；直接以本文为入场即可。

---

## §5 交叉引用

| 引用方 | 引用方式 |
|:--|:--|
| `goslo_model_modularization_launch_prompt_20260506.md §7` | 加 1 行：`本 Chat 暗线审计 → goslo_modularization_residual_debt_20260506.md` |
| `goslo_model_manifest_protocol_v1.md §1 / §7` | 加 1 行：`残余 parrot-isms 清单 → goslo_modularization_residual_debt_20260506.md` |
| `INDEX.md`（user 自管，本 Chat 不改）| 无需操作 |
| App 流程 / 核心功能需求文档（`requirements.md` / `ar_app_flow_ui_design.md` / `milestone_p2.md`）| **不改**。由 user 在 DSG 协议升级 Chat 完成（标 NEED-P2.5-A/B / NEED-P3-A/B/C/D/E TODO）|

---

## §6 变更日志

- **2026-05-06 (Step 1.5 audit)**：本文创建。Step 1（Manifest schema + 协议文档）落地后产出。结论：协议层够了；7 类残余债中只 1 类高严重度（LLM persona）；本 Chat Step 2-5 plan 不调整；user 决策 Step 6（persona 参数化）取舍；p2.5 / p3 前瞻需求注记齐全，等下游 Chat 标 TODO。
