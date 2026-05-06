---
status: ratified-code / pending-unity-editor-smoke
category: completion-report
status_note: "GOSLO 模型 + 行为树 + Unity 资产导入 模块化任务（Step 1-4 + 1.5 暗线审计）实施收口。Python+Unity 代码 + 415 pytest 全绿 + 协议文档 + 残余债审计 + AI CLI MVP 全部就绪；Unity Editor 联机 smoke + 第一个真实 MMD demo 留下游执行（无 Editor + 无 user 待选 MMD 资产）。"
last_reviewed: 2026-05-06
authoritative_for: "GOSLO 模型模块化任务完成证据 / 已落地范围 / 跨语言 wire 0 漂移证明 / Phase 4 §8 锁 0 漂移证明 / 已知缺陷与 deferred 工作清单"
prereq_commits: "(本 Chat 改动；落库后填)"
sources:
  - "goslo_model_modularization_launch_prompt_20260506.md (任务启动)"
  - "goslo_model_manifest_protocol_v1.md (Step 1 协议规则)"
  - "goslo_modularization_residual_debt_20260506.md (Step 1.5 暗线审计)"
  - "sprint4_phase4_entry_20260430.md §8 (Phase 4 决策锁)"
  - "lineb_implementation_completion_20260504.md (报告样板)"
related:
  - "ar_workspace_index.md (AR 工作区聚合)"
  - "INDEX.md (全局真相源)"
---

# GOSLO 模型 + 行为树 + Unity 资产导入 模块化 — 完成报告（Step 1-5）

> **本文用途**：GOSLO 模型模块化任务（[`goslo_model_modularization_launch_prompt_20260506.md`](goslo_model_modularization_launch_prompt_20260506.md)）Step 1-4 + 1.5 暗线审计 全部落地后的收口报告。
>
> **基调**：本 Chat 完成"协议层 schema + Unity 端 manifest-driven 三层架构 + Brain tools `model_id` 透传 + AI CLI MVP + 残余模块化债审计"5 件套；**未跑 Unity Editor 联机 smoke**（无 Editor 环境）+ 未做 **MMD 真实资产端到端 demo**（user 自选 MMD `.pmx + .vmd → FBX` 流程）。两项留下游 Chat / user 自验。
>
> **Step 6（Brain `soul.py` LLM 人设参数化）已确认推下游**（user 2026-05-06 sign off：与 p3 菜单画布 4 类块一起做，避免半成品 schema）。

---

## §0 TL;DR

| 维度 | 状态 |
|:--|:--|
| Step 1 — `parrot.shared.model_manifest` Pydantic schema + 协议规则文档 v1 + `EcpCommand.meta` plumbing | ✅ |
| Step 1.5 — 暗线审计（7 类 parrot-isms 残余债 + p2.5/p3 前瞻需求注记） | ✅ |
| Step 2 — Unity ModelDriver 三层架构 + GosloLegacyController shim + Resources baseline | ✅（联机 smoke ⏳） |
| Step 3 — Brain `animate` / `fly_to` 加 `model_id` 参数 + 静态源护栏 × 6 | ✅ |
| Step 4 — AI CLI `asset_to_manifest.py` MVP + 23 测试 | ✅ |
| Step 5 — 完成报告（本文） | ✅ |
| Phase 4 §8 wire schema 0 漂移 | ✅（`EcpCommand.meta` 是既有 frozen 字段；新增 `EcpCommandMetaDto` typed slot 不破 wire） |
| `tests/test_ecp_event/test_cs_parity.py` 4/4 | ✅ |
| `ParrotAnimation` / `ParrotBodyState` / `BehaviorMode` enum 0 增删 | ✅ |
| 既有 Unity 场景兼容（未挂 ModelDriver / ParrotRegistry） | ✅（fallback 链：IParrotController → AnimationDriver → Animator → dev-pulse） |
| 全量 pytest（除 integration env-dep） | **415 passed** ✅ |

---

## §1 落地清单

### §1.1 Python 协议层

| 类型 | 路径 | 行数 | 说明 |
|:--|:--|--:|:--|
| 新建 | `src/parrot/shared/model_manifest.py` | 270 | `Capability` / `CapabilityKind` / `ModelManifest` Pydantic + `RESERVED_PARROT_CAPABILITY_IDS` + `DEFAULT_MODEL_ID` |
| 改动 | `src/parrot/shared/ecp.py` | +20 | `EcpCommand.for_legacy_rpc(meta=...)` + `wrap_legacy_rpc_payload(meta=...)` 透传 kwarg；不动 schema 字段集 |

### §1.2 Brain tools

| 类型 | 路径 | 行数 | 说明 |
|:--|:--|--:|:--|
| 改动 | `src/parrot/brain/tools/animate.py` | +9 | `model_id: str = ""` kwarg + 条件 `meta={"model_id": ...}` 透传 |
| 改动 | `src/parrot/brain/tools/fly_to.py` | +9 | 同上模式 |

### §1.3 Unity 端（ArSpike）

| 类型 | 路径 | 行数 | 说明 |
|:--|:--|--:|:--|
| 新建 | `unity/ArSpike/Assets/Scripts/ParrotApp/Parrot/IParrotController.cs` | 70 | Capability 路由契约接口 |
| 新建 | `Parrot/ModelManifestDto.cs` | 175 | JsonUtility 适配 DTO + Resources 加载器 + 派生属性 |
| 新建 | `Parrot/ParrotRegistry.cs` | 130 | scene-singleton P1 stub（last-registered active；P3 多 actor 占位） |
| 新建 | `Parrot/ModelDriver.cs` | 175 | manifest 加载 + 反射实例化 controller + auto-scale + 注册 |
| 新建 | `Parrot/GosloLegacyController.cs` | 155 | IParrotController 实现，包装 AnimationDriver |
| 改动 | `Parrot/AnimationDriver.cs` | +20 | 加 `ReflexEnabled` 公共 flag + Update() reflex 门控（默认 true 0 漂移） |
| 改动 | `Parrot/ParrotController.cs` | +60 | 加 `FlyTo(target, modelId)` / `PlayAnimation(name, modelId)` 重载 |
| 改动 | `RPC/EcpDtos.cs` | +35 | 加 `EcpCommandMetaDto` + `EcpCommandDto.meta` typed 字段 + `ModelId` 便捷属性 |
| 改动 | `RPC/ParrotRpcHandler.cs` | +6 | 提取 `_ecp.meta.model_id` 透传给 ParrotController 路由重载 |
| 新建 | `Resources/parrot_models/goslo_default.json` | 21 | GOSLO 兼容性基线 manifest（8 reserved capability_id 全声明） |

### §1.4 AI CLI

| 类型 | 路径 | 行数 | 说明 |
|:--|:--|--:|:--|
| 新建 | `src/scripts/asset_to_manifest.py` | 350 | argparse CLI + Pydantic 校验 + default/mmd preset + scaffolding + validate-only + 启发式重命名建议 |

### §1.5 测试

| 类型 | 路径 | case 数 | 说明 |
|:--|:--|--:|:--|
| 新建 | `tests/test_shared/test_model_manifest.py` | 23 | schema / Reflex 派生 / GOSLO sentinel / JSON round-trip |
| 改动 | `tests/test_scheduler/test_ecp.py` | +5 | meta kwarg passthrough / 默认空 / 未知 keys 留存 / Unity DTO field-parity 守 |
| 新建 | `tests/test_brain/test_tools_model_id.py` | 6 | animate/fly_to 静态源护栏（kwarg 存在 / meta 透传 / 空值不发 key）|
| 新建 | `tests/test_scripts/test_asset_to_manifest.py` | 23 | CLI capability spec / preset 层叠 / scaffolding / validate-only / 警告 / 启发式建议 |

### §1.6 文档

| 类型 | 路径 | 说明 |
|:--|:--|:--|
| 新建 | `goslo_model_manifest_protocol_v1.md` | 协议规则 SSOT — schema 字段定义 / 接入约定 / Reflex 激活条件 / MMD 端到端 walkthrough |
| 新建 | `goslo_modularization_residual_debt_20260506.md` | 暗线审计 — 7 类 parrot-isms + p2.5/p3 前瞻需求注记（Chat 4 接口提炼输入） |
| 新建 | `goslo_modularization_completion_20260506.md`（本文） | 完成报告 |
| 改动 | `goslo_model_modularization_launch_prompt_20260506.md §7` | 加协议文档 + 审计文档入口 |
| 改动 | `unity/ArSpike/Assets/Scripts/ParrotApp/MIGRATION.md` | Group 4 表更新 + 新 "GOSLO 模型模块化 Step 2" 子表 |

---

## §2 验收数字

| 维度 | 数字 |
|:--|:--|
| 本 Chat 新增/改动测试 case | **57 个**（23 + 5 + 6 + 23） |
| 全量 pytest（除 `tests/integration`）| **415 passed**（baseline 358 + 本 Chat 57） |
| 既有测试 0 回归 | ✅ |
| `tests/test_ecp_event/test_cs_parity.py` 4/4 | ✅ |
| `tests/test_ecp_event/test_tools_state_header.py` 3/3 | ✅ |
| Linter（Python + C#） | 0 errors |
| 新增 Unity 文件 | 5（C#） + 1（json） |
| 改动 Unity 文件 | 4（C#） + 1（md） |
| 新增 Python 文件 | 2（schema + CLI）+ 4 测试 |
| 改动 Python 文件 | 3（ecp.py / animate.py / fly_to.py）+ 1 测试 |
| 新增文档 | 3（协议 + 审计 + 完成报告） |

### §2.1 Phase 4 §8 wire schema 0 漂移证据

| 锁项 | 状态 | 证据 |
|:--|:--|:--|
| L1-L13 wire schema 顶层字段集 | ✅ 0 改动 | `EcpEvent` / `EcpState` / `EcpAck` / `EcpCommand` 顶层字段集未变；本 Chat 只动 `EcpCommand.meta` 既有 `dict[str, Any]` 字段的 plumbing 入口（`for_legacy_rpc(meta=...)` / `wrap_legacy_rpc_payload(meta=...)`） |
| `EcpEventTypeNames` cs_parity | ✅ 4/4 | `tests/test_ecp_event/test_cs_parity.py` 跑过 |
| `ParrotAnimation` enum 8 项 | ✅ 0 增删 | grep 验证：本 Chat 不动 `parrot_actions.py`；新增 `RESERVED_PARROT_CAPABILITY_IDS = frozenset(a.value for a in ParrotAnimation)` 是派生集合，单测断言其等价 8 项 |
| `ParrotBodyState` / `BehaviorMode` enum | ✅ 0 增删 | 同上 |
| `EcpCommandDto` C# 字段集 | ⚠️ 加 1 字段 | `EcpCommandDto.meta = new EcpCommandMetaDto()` — 这是 typed mirror 既有 Python `EcpCommand.meta` 字段（不是 wire 新增字段；C# 端原本就该有但缺失），加上后通过新 `test_ecp_command_meta_unity_dto_field_parity` 守。**判定**：这是 **wire 形状一致性补全** 而非 wire schema 扩展，符合 §8 锁精神 |

---

## §3 设计决策与哲学校正

### §3.1 协议哲学（设计 chat 2026-05-06 Q-A sign off）

**Brain LLM 词汇表 + Reflex 触发器双重身份**：`ParrotAnimation` enum 8 项不是"模型必须实现集"，是 (a) Brain LLM 的固定词汇表（永不发明新动作），(b) Parrot Reflex 层激活条件（任意 capability_id 落入 reserved 集合即激活呼吸/idle 摇头/tail sway 次级行为）。

**模型完全开放注册能力**：模型作者声明 `capabilities: tuple[Capability, ...]`，capability_id 自由命名；非鸟模型可 0 reserved id → Reflex 关闭 + Brain 仅通过未来 dispatch_task / 自定义 tool 触发。

**Wire 0 改动**：`EcpCommand.meta["model_id"]` 走既有 `dict[str, Any]` 槽 — Phase 4 §8 锁不动 + cs_parity 不动 + 不需新 ADR。

### §3.2 Unity 端 OPTIONAL 组件设计

**未挂 `ModelDriver` / `ParrotRegistry` 的旧场景 0 漂移**：现有 GOSLO Parrot prefab 不需要任何 Unity Editor 操作即可继续工作（fallback 链：`IParrotController` → `AnimationDriver` → `Animator` → dev pulse）。新组件按需挂载，逐步迁移。

**反射实例化 + GetComponent reuse**：`ModelDriver` 优先 `GetComponentInChildren<IParrotController>()`（旧 prefab 手动加好的组件），fallback 到 `Type.GetType(controller_type)` + `AddComponent`（自定义模型 manifest 驱动）。

**ReflexLayer 折叠进 AnimationDriver**：原 design draft §C 列了独立 `ReflexLayer.cs`，但实际 AnimationDriver 现有 `Update()` 已实现 sin/cos 次级行为，独立文件会重复代码。改为 `AnimationDriver.ReflexEnabled` flag 由 `GosloLegacyController.ConfigureFromManifest` 注入。

### §3.3 Step 6（LLM persona 参数化）推下游

详见 [`goslo_modularization_residual_debt_20260506.md §2.1`](goslo_modularization_residual_debt_20260506.md)。

**关键 finding**：`brain/soul.py` 内联硬编码"You are Parrot — a cheerful Minecraft-style parrot companion"，换非鹦鹉模型时 LLM 嗓音不会跟着变。**这是当前最大的高严重度残余债**，但与 p3 菜单画布"模型 / 设定 / 模式 / 场景"4 类块的统一接口设计强耦合。user 决策（2026-05-06）：推到下游 Chat 与 4 类块一起设计，避免半成品 persona schema 造成 p3 菜单画布的接口回头改。

---

## §4 已知缺陷 / Deferred 工作

### §4.1 ❗ 阻塞"非鹦鹉模型自然演出"

**[D-1] LLM 人设硬编码** — `brain/soul.py` `CORE_INSTRUCTIONS` / `COMPANION_INSTRUCTIONS` / `PLAYFUL_INSTRUCTIONS` 全内联鹦鹉味儿。换 Q 版 chibi → Unity 骨骼正确驱动 + LLM 仍说自己是鹦鹉。
- **严重度**：高
- **修法**：抽 persona file 外置 + 加载器 + BB key `global/active_persona_id` + 默认 `goslo_parrot_default`
- **下游**：DSG 协议升级 Chat 标 `NEED-P2.5-A`；与 p3 菜单画布"设定块"统一设计

### §4.2 ⚠️ 功能受限但能跑

**[D-2] `ParrotBodyState` wire 5 项锁** — 非鸟模型上报 `body_state` 只能挑最像的 1 项（粒度损失）。Phase 4 §8 锁内不可改；推 p3 ADR：`controller_body_state: str` 自由字段（Option A）vs `body_state` 升级 string（Option B）。

**[D-3] `fly_to` 动词假设会飞** — 非飞行模型调用 `fly_to` 仍触发 `Fly` capability。修法：tool 暴露层按 manifest `declared_capability_ids` 动态注册到 LLM。
- **下游**：建议作 Step 3.5 增量（Brain `ModelManifestRegistry` 副本 + tool 注册过滤）；本 Chat 不做（user 选"舍"）

### §4.3 ⏳ 未跑 / 未演示

**[D-4] Unity Editor 联机 smoke 未执行** — 本 Chat 无 Unity Editor。手工验收清单：
1. 打开 ArSpike 项目 → 现有 Parrot prefab 加 `ModelDriver` 组件 → Inspector `modelId` 留空（默认 `GOSLO_default`）→ 自动 Awake 时载入 Resources/parrot_models/goslo_default.json
2. 在 Parrot prefab 加 `GosloLegacyController` 组件（`[RequireComponent(typeof(AnimationDriver))]` 会自动确保 AnimationDriver 在场）
3. 跑 Editor Play → 现有 GOSLO 行为应**完全相同**（呼吸 / idle 摇头 / tail sway / fly / dance / perch / sit 全等价）
4. 联机 smoke：通过 Brain RPC 测试 `flyTo` / `animate` 流程，确认 `_ecp.meta.model_id` 在 `ParrotRpcHandler.HandleFlyTo` 日志可见 + `ParrotController.FlyTo(target, modelId)` 路由重载被调用 + `ParrotRegistry.Resolve(modelId)` 返回 `GosloLegacyController`
5. 反向兼容 smoke：从 Parrot prefab **移除** ModelDriver + GosloLegacyController + ParrotRegistry → 跑 Editor Play → 通过 `ParrotController.PlayAnimation("dance")` 老路径直达 AnimationDriver，行为不变

**[D-5] MMD `.pmx + .vmd → FBX` 端到端 demo 未执行** — user Q5 提到自己找 MMD 资产（"二头身 Q 版大头橘福福"）。流程：
1. user 拿 .pmx + .vmd 用 Blender + mmd_tools 转成 .fbx（含 AnimationClip）
2. 拖入 Unity ArSpike → Resources/parrot_models/qfufu_v1/ → Prefab 化
3. 写 `QFufuController.cs : MonoBehaviour, IParrotController`（路由 capability_id → Animator state）
4. 跑 CLI `python src/scripts/asset_to_manifest.py --preset mmd --model-id qfufu_v1 --asset-path parrot_models/qfufu_v1 --controller-type ParrotApp.Parrot.QFufuController --capability idle:pose:Idle --capability wave_hand:animation:Wave --capability dance_q_pose:animation:Dance --capability bow:animation:Bow --out unity/ArSpike/Assets/Resources/parrot_models/qfufu_v1.json`
5. 在 ModelDriver 上把 `modelId="qfufu_v1"` 设给 active prefab → Editor Play → 应能控制 Q 版 chibi 跳舞
6. **预期视觉违和**：LLM 仍以鹦鹉嗓音说话 — 这是 [D-1] 的具象化，符合预期

### §4.4 ❌ 显式不做（已确认推下游）

| 项 | 推到 |
|:--|:--|
| Brain `soul.py` persona 参数化 | DSG 协议升级 Chat / p3 菜单画布 Chat |
| `fly_to` 动词 capability gating | 同上 |
| `ParrotBodyState` wire 解锁 ADR | p3 ADR |
| 多 actor 真路由 + spawn/despawn tool | p3 Chat |
| Controller `.cs` 自动 codegen | 后续 Chat（待证明协议简单到模板化） |
| FBX/glTF 骨骼自动解析 + LLM 别名建议 | AI CLI 后续增强 |
| Unity Editor 资产浏览器 / 预览器 UI | AR 工作区独立 Chat |
| p3 菜单画布（4 类块拖拽 + 预设保存） | DSG 协议升级 Chat 标 NEED-P3-B/C/D/E |

---

## §5 给下游 Chat 的入场素材

### §5.1 DSG 协议升级 Chat — 入场即标 TODO

**入场必读**：本文 §3.3 + §4.1 + [`goslo_modularization_residual_debt_20260506.md §4`](goslo_modularization_residual_debt_20260506.md)

**待标 TODO（user 在该 Chat 处理）**：
- `NEED-P2.5-A`：persona 文件外置 + 加载器 + BB key + 默认 `goslo_parrot_default`
- `NEED-P2.5-B`：Unity menu 暴露 DSG bucket / scene 切换接口
- `NEED-P3-A`：`EcpFrontendState.body_state` 解锁评估（Option A vs B）
- `NEED-P3-B`：4 类块（模型 / 设定 / 模式 / 场景）每类的 ID 命名空间 + 注册表 + 数据格式 + 加载器 + active BB key + 切换事件
- `NEED-P3-C`：预设 = 4 个 active ID 命名快照 JSON schema
- `NEED-P3-D`：Unity menu UI = node-canvas（ComfyUI / n8n 风）
- `NEED-P3-E`：默认菜单 fallback —"列表选择 + 保存预设 + 恢复默认"

### §5.2 Chat 4 接口提炼 — 入场即消费

**入场必读**：本文 §1（已落地接口）+ [`goslo_model_manifest_protocol_v1.md`](goslo_model_manifest_protocol_v1.md)（Step 1-2 接口）+ [`goslo_modularization_residual_debt_20260506.md §4.3`](goslo_modularization_residual_debt_20260506.md)（4 类块结构）

**接口提炼输入**：
- `IParrotController` 接口签名（`ApplyCapability` / `ModelId` / `SupportedCapabilities` / `ParrotReflexEnabled`）— 模型块的 Unity 端契约
- `ModelManifest` Pydantic + `ModelManifestDto` C# — 模型块的数据契约（含坐标系 / 单位 / 缩放 / capability 集合）
- `ParrotRegistry` 接口（`Register` / `Resolve` / `Unregister` / `EnsureInstance`）— 模型块的运行时绑定
- `EcpCommand.meta["model_id"]` wire 槽 — 模型块的命令路由协议
- `RESERVED_PARROT_CAPABILITY_IDS` 集合 — Brain LLM 词汇表 + Reflex 触发条件（设定块 / 模型块的交叉点）
- DSG 已有 `BucketRegistry` + `SceneRegistry.SceneSwitchOutcome` — 场景块的后端能力（详见 [`goslo_modularization_residual_debt_20260506.md §4.1`](goslo_modularization_residual_debt_20260506.md)）

### §5.3 自定义模型作者（人 / AI）— 接入步骤

**入场必读**：[`goslo_model_manifest_protocol_v1.md §4`](goslo_model_manifest_protocol_v1.md)（接入步骤）+ §5（MMD walkthrough）

**最小流程**：
1. 准备 Unity prefab 放到 `Assets/Resources/parrot_models/<model_id>/`
2. 写 `<ModelName>Controller : MonoBehaviour, IParrotController`
3. 跑 `python src/scripts/asset_to_manifest.py --model-id ... --capability ... --out ...` 生成 manifest.json
4. 在场景上挂 `ModelDriver` 组件，Inspector 设 `modelId`
5. Editor Play 验证

---

## §6 交叉引用

| 引用类型 | 路径 |
|:--|:--|
| 任务启动 prompt | [`goslo_model_modularization_launch_prompt_20260506.md`](goslo_model_modularization_launch_prompt_20260506.md) |
| 协议规则文档（Step 1） | [`goslo_model_manifest_protocol_v1.md`](goslo_model_manifest_protocol_v1.md) |
| 暗线审计（Step 1.5） | [`goslo_modularization_residual_debt_20260506.md`](goslo_modularization_residual_debt_20260506.md) |
| 完成报告（本文，Step 5） | `goslo_modularization_completion_20260506.md` |
| Phase 4 §8 决策锁 | [`sprint4_phase4_entry_20260430.md §8`](sprint4_phase4_entry_20260430.md) |
| 报告样板 | [`lineb_implementation_completion_20260504.md`](lineb_implementation_completion_20260504.md) |
| Unity Migration | [`unity/ArSpike/Assets/Scripts/ParrotApp/MIGRATION.md`](../../../unity/ArSpike/Assets/Scripts/ParrotApp/MIGRATION.md) |

---

## §7 变更日志

- **2026-05-06 Step 1-5 + 1.5 全部落地**：
  - Step 1：`parrot.shared.model_manifest` Pydantic schema + 协议规则文档 v1 + `wrap_legacy_rpc_payload(meta=...)` plumbing
  - Step 1.5：暗线审计（7 类 parrot-isms + p2.5/p3 前瞻需求注记）
  - Step 2：Unity 三层架构（IParrotController / ModelDriver / ParrotRegistry / GosloLegacyController）+ AnimationDriver `ReflexEnabled` flag + ParrotController/ParrotRpcHandler `model_id` 路由 + `EcpCommandMetaDto` C# typed slot + `goslo_default.json` baseline
  - Step 3：Brain `animate.py` / `fly_to.py` 加 `model_id: str = ""` kwarg + `meta` 透传
  - Step 4：AI CLI `asset_to_manifest.py` MVP（argparse + Pydantic 校验 + default/mmd preset + 启发式建议）
  - Step 5：本完成报告
  - 415 pytest passed / Phase 4 §8 0 漂移 / cs_parity 4/4 / Unity 旧场景 fallback 链保留 0 漂移
  - Step 6（LLM persona 参数化）确认推下游 Chat（与 p3 菜单画布 4 类块一起做）
  - Unity Editor 联机 smoke + MMD 真实资产 demo 留 user / 下游 Chat 执行
