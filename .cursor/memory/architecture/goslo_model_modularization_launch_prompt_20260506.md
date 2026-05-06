---
status: draft / launch-prompt
category: chat-launch-prompt
status_note: "GOSLO 模型 + 行为树 + Unity 资产导入 + AI 一键转换 模块化任务启动提示词。新 chat 启动时 @ 引用本文 + 按 §1 顺序读完入场必读 5 项即可进入设计/实施。"
last_reviewed: 2026-05-06
ai_priority: high
ai_audience: "新启动的 GOSLO 模型化任务 chat（独立于 DSG / AR / Sprint4 主线）"
parent_doc: "../INDEX.md"
related:
  - "../parrot_behavior_rules.md"
  - "../requirements.md"
  - "sprint4_phase4_entry_20260430.md"
  - "ar_workspace_index.md"
---

# GOSLO 模型 + 行为树 + Unity 资产导入 模块化 — 任务启动 Prompt

> **本文用途**：派发到新 chat 的"启动背景与提示词"。新 chat 入场时把本文当 entry SSOT；按 §1 顺序读完入场必读 5 项后即可进入设计 / 实施阶段。
>
> **任务定位**：把当前**绑死 GOSLO.glb 的硬编码鹦鹉模型 / 行为树**重构成**模型/动画无关的协议层** + **资产导入工具**，让用户能下载或自定义 Unity 资产（带动画的角色 / 道具 / Prop）经 AI 一键转换后接入既有协议。

---

## §0 Mission（一段话使命）

把"GOSLO = `unity/.../GOSLO.glb` + `AnimationDriver.cs` 写死骨骼名 + Brain `ParrotAnimation` enum 8 项"的紧耦合现状，重构为：

```
Brain 端：ParrotAnimation enum (Phase 4 § 8 锁) + ModelManifest (新 protocol) + AI 转换工具
   ↓ wire (不变 — Phase 4 § 8 锁住的 EcpEvent / EcpCommand)
Unity 端：ModelDriver (manifest-driven) + ParrotPrefab (任意 glTF/FBX 资产 + 配套 manifest.json)
```

**核心愿景**（用户原话 2026-05-06）：
> 我后面想支持把一些网上找到带动作的 Unity 资产，支持自定义用 AI 一键转换成协议支持的可玩的模型。

---

## §1 入场必读（按顺序读完再进入设计）

### §1.1 既有协议合同 + 锁

1. [`sprint4_phase4_entry_20260430.md §8`](sprint4_phase4_entry_20260430.md) — Phase 4 § 8 13 决策锁
   - 重点：L2-L6（EcpEventType / EcpEventSource / topic 常量 / wire schema 不动）
   - 任何动 wire 的方案都必须先起新 ADR

### §1.2 协议层既有定义

2. `src/parrot/shared/parrot_actions.py` — **ParrotAnimation enum 8 项 + ParrotBodyState 5 项 + BehaviorMode 5 项**（Brain↔Unity wire 契约）
3. `src/parrot/shared/ecp_event.py` — EcpEvent / EcpEventType / EcpEventSource（Phase 4 锁）
4. `src/parrot/shared/bb_schema.py` — Blackboard schema

### §1.3 现状代码（绑死 GOSLO 的部分）

5. **Unity 端**：
   - `unity/ArSpike/Assets/Scripts/ParrotApp/Parrot/AnimationDriver.cs` — **812 行硬编码**
     - 7 个 BodyState enum + 4 个 HeadState enum
     - 骨骼节点名硬编码：`headNodeName="Head"` / `bodyNodeName="Body"` / `leftWingGroupNodeName="left_wing"` / `right_wing` / `left_wing_rotation` / `right_wing_rotation` / `left_leg` / `right_leg` / `tail`
     - 所有动画参数 SerializeField inline（flySpeed / wingFlapAxisMode / danceWingSpreadDegrees 等 30+ 字段）
     - Wire mapper 静态硬编码（`BodyStateToWire`/`HeadStateToWire`）
   - `unity/ArSpike/Assets/Scripts/ParrotApp/Parrot/ParrotController.cs` — RPC 入口（flyTo / animate）
   - `unity/ParrotDev/Assets/Scripts/Parrot/{AnimationDriver,ParrotController}.cs` — 测试床版本（冻结）

### §1.4 Brain 端 Tools

6. `src/parrot/brain/tools/animate.py` — animate tool 强校验 ParrotAnimation enum
7. `src/parrot/brain/tools/fly_to.py` — flyTo RPC

### §1.5 行为树 + 调度器

8. `src/parrot/scheduler/bt_router.py` + `bt_nodes.py` — py-trees BT (Selector + 3 leaf) — 跟模型耦合度低，主要是 dispatch 层

---

## §2 设计范围（in / out scope）

### §2.1 In scope（**本任务必产**）

#### A. ModelManifest 协议（**新增 Pydantic schema，仅 Brain 内部 / 不动 wire**）

```python
# 候选 schema (要求设计稿先锁定)
class BoneMapping(BaseModel):
    """Map a logical bone name to a model-specific Transform path."""
    logical_name: str           # "head" / "body" / "left_wing" / "right_wing" / ...
    transform_path: str          # "Armature/Spine/Head" or "left_wing_rotation"
    base_rotation_offset: tuple[float, float, float] = (0, 0, 0)
    flap_axis_mode: str = "POS_Z"  # POS_Z / NEG_Z / POS_X / NEG_X

class AnimationSpec(BaseModel):
    """One playable animation = name + bone modulations."""
    animation_id: str            # "fly" / "dance" / "idle" / 自定义
    parrot_animation_alias: ParrotAnimation | None = None
    """协议层别名 — 一个 model 自定义动作映射回 ParrotAnimation enum 的哪一项。
    None = 本动画不对应任何 ParrotAnimation；Brain 永远不主动派发它，只能通过
    自定义工具或 GOSLO 显式调用。"""
    bone_keyframes: list[dict] | None = None
    builtin_clip_name: str = ""   # 若 Unity prefab 自带 AnimationClip，引用其名
    duration_seconds: float = 0.0

class ModelManifest(BaseModel):
    """Top-level descriptor for a custom Unity model."""
    manifest_version: int = 1
    model_id: str                # "GOSLO_default" / "owl_v1" / 用户自定义
    asset_path: str              # Unity Resources path or addressable id
    bones: tuple[BoneMapping, ...] = ()
    animations: tuple[AnimationSpec, ...] = ()
    runtime_capabilities: list[str] = []   # "wing_flap" / "head_tilt" / "perch" / "fly"
    preview_image: str = ""
    author_meta: dict[str, str] = {}
```

#### B. Unity 端 ModelDriver（替代 AnimationDriver）

- 新文件 `unity/ArSpike/Assets/Scripts/ParrotApp/Parrot/ModelDriver.cs`
- 启动时载入 `ModelManifest.json`（Resources 或 Addressable）
- 通过 `BoneMapping.transform_path` 动态绑定骨骼，**不再 FindDeep 硬编码字符串**
- Wire 输入（`ApplyBodyStateString` / `ApplyHeadStateString`）保持兼容（Phase 4 § 8 不动）
- 内部把 wire string → `parrot_animation_alias` 反查 → 找到 `AnimationSpec` → 播放
- 旧 `AnimationDriver.cs` 保留 → 做"DEPRECATED stub"：转发给 ModelDriver；**不立即删**（向后兼容 Sprint 0-4 测试床）

#### C. AI 一键转换工具（**新 CLI 脚本**）

- 新文件 `src/scripts/asset_to_manifest.py`
- 输入：用户给的 Unity 资产文件夹（含 .glb/.fbx/.prefab + 可选 .anim）
- 流程：
  1. 解析骨骼树（gltflib / pyassimp / Unity meta scan）
  2. **LLM 调用**（Gemini Flash）建议骨骼语义映射（"Spine_05" → "head"）
  3. 解析 AnimationClip → 建议 `parrot_animation_alias`
  4. 输出 `ModelManifest.json` + Unity prefab 绑定脚本
  5. 用户审阅 + 微调（只动 manifest.json，不动代码）
- 命令行用例：
  ```
  python src/scripts/asset_to_manifest.py \
      --asset path/to/owl_animated.glb \
      --out path/to/manifest.json \
      --suggest-aliases \
      --interactive
  ```

#### D. 行为树侧的轻改动

- `src/parrot/scheduler/bt_router.py` 不动（dispatch 层与模型无关）
- `src/parrot/brain/tools/animate.py` 增加 `model_id: str = ""` 可选参数
  - 默认空 = 当前活跃模型（GOSLO_default）
  - 显式传 = 路由到对应模型（多模型同场景时可指定）
- `EcpEvent` payload 新增可选 `model_id` 字段？
  - **wire 方案 A（preferred）**：用 `payload.meta["model_id"]` — **不动 EcpEvent 顶层 schema，Phase 4 § 8 锁不变**
  - **wire 方案 B**：加顶层 `model_id` 字段 — 需新 ADR + cs_parity 全过

### §2.2 Out of scope（本任务不做）

| 项 | 推到哪 | 原因 |
|:--|:--|:--|
| 自动绑骨（rigging）| 后续设计 chat | 需要 ML 视觉 + 用户交互 |
| 物理 / 碰撞 / IK | P3+ | 单独任务 |
| 多 GOSLO 同房间（multi-instance）| 后续 | 协议先支持 1 个 model_id 切换 |
| ParrotAnimation enum 增删 | **永不**（Phase 4 § 8 L1 锁 — wire 锁）| 自定义动作通过 `parrot_animation_alias` 别名映射 |
| BehaviorMode enum 增删 | **永不**（Phase 4 § 8 锁）| 同上 |
| 完整 Unity Editor UI（资产浏览器 / 预览器）| AR 工作区独立 chat | 这是 UX，本任务管协议 + 工具 |

---

## §3 硬约束（**严禁触动**）

| 锁 | 不能动什么 |
|:--|:--|
| Phase 4 § 8 L1 (NodeKind / EdgeKind enum) | 不动 |
| Phase 4 § 8 L2-L6 (wire schema) | 不动 — 任何 ECP 顶层字段动需新 ADR |
| ParrotAnimation enum 8 项 | 不增不减；自定义动作走 alias 映射 |
| ParrotBodyState enum / BehaviorMode enum | 同上 |
| `tests/test_ecp_event/test_cs_parity.py` 4/4 | 不动 wire = 不破 cs_parity |
| `parrot.shared.ecp_event` / `bb_schema` | 不动 |
| `tests/test_ecp_event/*` 既有测试 | 全护（必要时新增 happy path） |

---

## §4 推荐推进顺序

### Step 1 — Manifest + 测试期 baseline

1. 写 `parrot.shared.model_manifest` Pydantic schema + 单元测试
2. 写 `unity/.../ModelDriver.cs`（可加载 manifest，但行为兼容 AnimationDriver）
3. 抽 GOSLO.glb 当前硬编码 → `Resources/parrot_models/goslo_default.json`
4. 旧 `AnimationDriver.cs` 改为 deprecated shim（转发 ModelDriver）
5. 跑既有 Unity 真机 smoke：动作行为 0 改变（ECP wire 输入相同 → 同样的动画输出）

### Step 2 — AI 转换 CLI

1. 写 `src/scripts/asset_to_manifest.py` minimum viable（手工标注模式）
2. 加 LLM 建议（Gemini Flash）骨骼语义映射
3. 加 AnimationClip 反向 alias 推断
4. 跑测：用一个免费的 Unity 鸟类 / 动物资产端到端转一次

### Step 3 — 行为树轻改

1. `animate` tool 加 `model_id` 可选参数
2. `EcpEvent.payload.meta["model_id"]` wire 方案 A 落地（不动顶层 schema）
3. ModelDriver 多 model 路由（model_id → 找对应 manifest → ApplyBodyState）

### Step 4 — 完成报告

参考 [`lineb_implementation_completion_20260504.md`](lineb_implementation_completion_20260504.md) 风格，重点字段：
- Phase 4 § 8 + cs_parity 0 漂移证据
- 旧 AnimationDriver shim 验证（既有 GOSLO 行为 0 变化）
- AI 转换工具端到端样例（含一个真实 Unity 资产 demo）
- 多 model 路由测试
- 已知 finding（如 LLM alias 误判 / Unity Resources 加载延迟等）

---

## §5 提问纪律

✅ **应该问用户**：
- ParrotAnimation alias 模糊（用户上传的"flap_a / flap_b"两个动作哪个映射 ParrotAnimation.FLY？）
- wire 方案 A vs B 哪个走（meta dict vs 顶层字段）— 用户审完 Phase 4 § 8 影响后定
- 第一个端到端 AI 转换测试用哪个免费资产
- 多 model 同时存在时的优先级（默认 GOSLO，临时切到 owl，对话结束自动恢复 GOSLO？）

❌ **不应该问用户**：
- LLM prompt 微调（自决）
- Unity Resources path 约定（按既有项目惯例自决）
- pyassimp / gltflib 选哪个（自决，桌面 baseline 选最少依赖的）
- AnimationClip 速度 / 缓动参数（参数化 + 桌面 baseline）

---

## §6 启动开局 prompt（**直接发给新 chat 的开场白**）

> **复制下面这段到新 chat 第一条消息**：

```
你是 ParrotCarriers GOSLO 模型 + 行为树 + Unity 资产导入 模块化 chat。

任务定义文件：
@architecture/goslo_model_modularization_launch_prompt_20260506.md

行动顺序：
1. 读完上述文件全文
2. 按其 §1 入场必读 5 项顺序读完（每项一句话总结）
3. 输出 design 草案前先列出关键架构问题（按 §5 提问纪律）
4. 用户 sign off design 草案后再进入实施

硬约束：
- 不动 Phase 4 § 8 13 决策锁（特别是 L1-L6 wire schema 锁）
- 不动 ParrotAnimation / ParrotBodyState / BehaviorMode enum 8/5/5 项
- 不动 cs_parity 4/4 跨语言守护
- 自定义动作通过 alias 映射 ParrotAnimation，永不增删 enum

允许动作：
- 重构 unity/.../AnimationDriver.cs（保留 deprecated shim 不立即删）
- 新增 parrot.shared.model_manifest Pydantic schema
- 新增 src/scripts/asset_to_manifest.py AI 转换 CLI
- 加 EcpEvent.payload.meta["model_id"]（不动顶层 schema 即不动 wire）

完成判据：
- Manifest schema + ModelDriver + AI CLI + 端到端样例 + 完成报告
- Phase 4 § 8 + cs_parity 0 漂移
- 旧 GOSLO 行为 0 变化（shim 兼容性 smoke）
- 至少 1 个真实 Unity 资产端到端转换 demo

开始读 §1 入场必读项 1。
```

---

## §7 引用

- 父 INDEX：[`../INDEX.md`](../INDEX.md)
- Phase 4 锁：[`sprint4_phase4_entry_20260430.md §8`](sprint4_phase4_entry_20260430.md)
- 既有协议：`src/parrot/shared/{parrot_actions,ecp_event,bb_schema}.py`
- 既有 Unity：`unity/ArSpike/Assets/Scripts/ParrotApp/Parrot/{AnimationDriver,ParrotController}.cs`
- Brain Tools：`src/parrot/brain/tools/{animate,fly_to}.py`
- 样板报告：[`lineb_implementation_completion_20260504.md`](lineb_implementation_completion_20260504.md)
- Skill：[`.cursor/skills/ar-foundation-api/SKILL.md`](../../skills/ar-foundation-api/SKILL.md) / [`ar-foundation-samples/SKILL.md`](../../skills/ar-foundation-samples/SKILL.md)（Unity 端 API）

---

## §8 变更日志

- **2026-05-06**：本文创建。基于 DSG Chat 2 完成后用户提出的"网络资产 + AI 一键转换 → 协议支持可玩模型"愿景，写定模块化任务的入场启动 prompt。范围严格限定在"协议层 + 资产导入工具 + Unity 端 manifest-driven 重构"，不动既有 wire / enum。
